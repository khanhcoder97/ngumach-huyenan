using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Consumer side of the outbox. A handler must perform its durable effect through the
/// supplied <c>applyOnce</c> callback so the dedupe marker and the effect share one SQL
/// transaction. Failures are retried with bounded backoff and poison messages are moved to
/// a durable dead-letter state after <c>maxAttempts</c>; one batch never loops unbounded.
/// </summary>
public sealed class OutboxDispatcher
{
    private readonly OutboxStore _outbox;
    private readonly TimeSpan _maxBackoff;

    public OutboxDispatcher(OutboxStore outbox, TimeSpan? maxBackoff = null)
    {
        _outbox = outbox ?? throw new ArgumentNullException(nameof(outbox));
        var configured = maxBackoff ?? TimeSpan.FromMinutes(5);
        _maxBackoff = configured <= TimeSpan.Zero
            ? throw new ArgumentOutOfRangeException(nameof(maxBackoff))
            : configured > TimeSpan.FromSeconds(PersistenceLimits.OutboxMaxBackoffSeconds)
                ? TimeSpan.FromSeconds(PersistenceLimits.OutboxMaxBackoffSeconds)
                : configured;
    }

    public async Task<DispatchReport> DispatchBatchAsync(
        string consumer,
        string workerId,
        OutboxHandler handler,
        int batchSize = PersistenceLimits.OutboxDefaultBatch,
        int maxAttempts = PersistenceLimits.OutboxDefaultMaxAttempts,
        TimeSpan? retryBackoff = null,
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(consumer);
        ArgumentException.ThrowIfNullOrWhiteSpace(workerId);
        ArgumentNullException.ThrowIfNull(handler);
        if (batchSize is <= 0 or > PersistenceLimits.OutboxMaxBatch)
        {
            throw new ArgumentOutOfRangeException(nameof(batchSize), $"Batch size must be between 1 and {PersistenceLimits.OutboxMaxBatch}.");
        }

        if (maxAttempts is < 1 or > PersistenceLimits.OutboxMaxAttempts)
        {
            throw new ArgumentOutOfRangeException(nameof(maxAttempts));
        }

        var clock = now ?? DateTimeOffset.UtcNow;
        var backoff = retryBackoff ?? TimeSpan.FromSeconds(5);
        if (backoff <= TimeSpan.Zero)
        {
            throw new ArgumentOutOfRangeException(nameof(retryBackoff));
        }

        if (backoff > _maxBackoff)
        {
            backoff = _maxBackoff;
        }

        var claimed = await _outbox.ClaimAsync(workerId, batchSize, now: clock, cancellationToken: cancellationToken).ConfigureAwait(false);
        var report = new DispatchReport(claimed.Count);

        foreach (var item in claimed)
        {
            if (item.Attempts >= maxAttempts)
            {
                await _outbox.DeadLetterAsync(workerId, item.OutboxId, "max-attempts-exceeded", clock, cancellationToken).ConfigureAwait(false);
                report = report.WithDeadLetter("max-attempts-exceeded");
                continue;
            }

            try
            {
                await handler(
                    item,
                    effect => _outbox.ApplyOnceAsync(consumer, consumer + ":effect:" + item.OutboxId, effect, clock, cancellationToken),
                    cancellationToken).ConfigureAwait(false);

                await _outbox.AckAsync(workerId, item.OutboxId, clock, cancellationToken).ConfigureAwait(false);
                await _outbox.AdvanceCursorAsync(consumer, item.OutboxId, clock, cancellationToken).ConfigureAwait(false);
                report = report.WithApplied();
            }
            catch (OperationCanceledException)
            {
                throw;
            }
            catch (Exception exception)
            {
                // Record only the type, never payload or exception data, to keep audit clean.
                var error = "handler-failed:" + exception.GetType().Name;
                if (item.Attempts >= maxAttempts)
                {
                    await _outbox.DeadLetterAsync(workerId, item.OutboxId, error, clock, cancellationToken).ConfigureAwait(false);
                    report = report.WithDeadLetter(error);
                }
                else
                {
                    var delay = TimeSpan.FromTicks(Math.Min(_maxBackoff.Ticks, backoff.Ticks * item.Attempts));
                    await _outbox.FailAsync(workerId, item.OutboxId, error, delay, clock, cancellationToken).ConfigureAwait(false);
                    report = report.WithRetry(error);
                }
            }
        }

        return report;
    }
}

public delegate Task OutboxHandler(
    OutboxItem item,
    Func<Func<SqliteConnection, SqliteTransaction, CancellationToken, Task>, Task<bool>> applyOnce,
    CancellationToken cancellationToken);

public sealed record DispatchReport(
    int Claimed,
    int Applied,
    int Retried,
    int DeadLetteredCount,
    IReadOnlyList<string> Errors)
{
    public DispatchReport(int claimed) : this(claimed, 0, 0, 0, Array.Empty<string>())
    {
    }

    public DispatchReport WithApplied() => this with { Applied = Applied + 1 };

    public DispatchReport WithRetry(string error) => this with { Retried = Retried + 1, Errors = Errors.Append(error).ToArray() };

    public DispatchReport WithDeadLetter(string error) => this with { DeadLetteredCount = DeadLetteredCount + 1, Errors = Errors.Append(error).ToArray() };
}
