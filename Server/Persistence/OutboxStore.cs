using System.Data;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Durable outbox with claim/retry/ack and a per-consumer cursor. Applying an effect is
/// recorded in the same SQL transaction as the effect itself through
/// <see cref="ApplyOnceAsync"/>, so a crash after the effect but before the ack cannot
/// apply the reward twice.
/// </summary>
public sealed class OutboxStore
{
    private readonly PersistenceDatabase _database;
    private readonly PersistenceOptions _options;

    public OutboxStore(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
        _options = database.Options;
    }

    public async Task<IReadOnlyList<OutboxItem>> ClaimAsync(
        string workerId,
        int limit,
        TimeSpan? claimTtl = null,
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(workerId);
        if (limit <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(limit));
        }

        var clock = now ?? DateTimeOffset.UtcNow;
        var ttl = claimTtl ?? _options.OutboxClaimTtl;
        var claimed = new List<OutboxItem>(limit);

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);

        var ids = new List<long>();
        await using (var select = connection.CreateCommand())
        {
            select.Transaction = transaction;
            select.CommandText = """
                SELECT outbox_id FROM outbox
                WHERE acked_at IS NULL
                  AND dead_at IS NULL
                  AND available_at <= $now
                  AND (claimed_by IS NULL OR claim_expires_at IS NULL OR claim_expires_at <= $now)
                ORDER BY outbox_id
                LIMIT $limit;
                """;
            select.Parameters.AddWithValue("$now", PersistenceDatabase.Timestamp(clock));
            select.Parameters.AddWithValue("$limit", limit);
            await using var reader = await select.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
            while (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
            {
                ids.Add(reader.GetInt64(0));
            }
        }

        foreach (var id in ids)
        {
            await using var update = connection.CreateCommand();
            update.Transaction = transaction;
            update.CommandText = """
                UPDATE outbox
                SET claimed_by = $worker, claim_expires_at = $expires, attempts = attempts + 1
                WHERE outbox_id = $id AND acked_at IS NULL;
                """;
            update.Parameters.AddWithValue("$worker", workerId);
            update.Parameters.AddWithValue("$expires", PersistenceDatabase.Timestamp(clock + ttl));
            update.Parameters.AddWithValue("$id", id);
            await update.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);

            var item = await ReadItemAsync(connection, transaction, id, cancellationToken).ConfigureAwait(false);
            if (item is not null)
            {
                claimed.Add(item);
            }
        }

        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
        return claimed;
    }

    public async Task<bool> AckAsync(string workerId, long outboxId, DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(workerId);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            UPDATE outbox SET acked_at = $acked, claimed_by = NULL, claim_expires_at = NULL
            WHERE outbox_id = $id AND claimed_by = $worker AND acked_at IS NULL AND dead_at IS NULL;
            """;
        command.Parameters.AddWithValue("$acked", PersistenceDatabase.Timestamp(clock));
        command.Parameters.AddWithValue("$id", outboxId);
        command.Parameters.AddWithValue("$worker", workerId);
        return await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false) > 0;
    }

    public async Task<bool> FailAsync(string workerId, long outboxId, string error, TimeSpan backoff, DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(workerId);
        if (backoff < TimeSpan.Zero)
        {
            throw new ArgumentOutOfRangeException(nameof(backoff));
        }

        var clock = now ?? DateTimeOffset.UtcNow;
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            UPDATE outbox
            SET claimed_by = NULL, claim_expires_at = NULL, available_at = $available, last_error = $error
            WHERE outbox_id = $id AND claimed_by = $worker AND acked_at IS NULL AND dead_at IS NULL;
            """;
        command.Parameters.AddWithValue("$available", PersistenceDatabase.Timestamp(clock + backoff));
        command.Parameters.AddWithValue("$error", error);
        command.Parameters.AddWithValue("$id", outboxId);
        command.Parameters.AddWithValue("$worker", workerId);
        return await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false) > 0;
    }

    /// <summary>
    /// Applies an effect at most once per consumer. The dedupe marker and the caller's SQL
    /// work commit in one transaction; the caller must not perform external I/O inside.
    /// Returns true when the effect was applied by this call, false on a duplicate.
    /// </summary>
    public async Task<bool> ApplyOnceAsync(
        string consumer,
        string effectId,
        Func<SqliteConnection, SqliteTransaction, CancellationToken, Task> apply,
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(consumer);
        ArgumentException.ThrowIfNullOrWhiteSpace(effectId);
        ArgumentNullException.ThrowIfNull(apply);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);

        await using (var check = connection.CreateCommand())
        {
            check.Transaction = transaction;
            check.CommandText = "SELECT COUNT(*) FROM consumer_effects WHERE effect_id = $id;";
            check.Parameters.AddWithValue("$id", effectId);
            var exists = (long)(await check.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false) ?? 0L);
            if (exists > 0)
            {
                return false;
            }
        }

        await apply(connection, transaction, cancellationToken).ConfigureAwait(false);

        await using (var insert = connection.CreateCommand())
        {
            insert.Transaction = transaction;
            insert.CommandText = "INSERT INTO consumer_effects (effect_id, consumer, applied_at) VALUES ($id, $consumer, $applied);";
            insert.Parameters.AddWithValue("$id", effectId);
            insert.Parameters.AddWithValue("$consumer", consumer);
            insert.Parameters.AddWithValue("$applied", PersistenceDatabase.Timestamp(clock));
            await insert.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
        }

        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
        return true;
    }

    public async Task<long> GetCursorAsync(string consumer, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(consumer);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT cursor_outbox_id FROM outbox_consumers WHERE consumer = $consumer;";
        command.Parameters.AddWithValue("$consumer", consumer);
        var value = await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
        return value is null or DBNull ? 0 : Convert.ToInt64(value);
    }

    public async Task AdvanceCursorAsync(string consumer, long outboxId, DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(consumer);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            INSERT INTO outbox_consumers (consumer, cursor_outbox_id, updated_at)
            VALUES ($consumer, $cursor, $updated)
            ON CONFLICT(consumer) DO UPDATE SET
                cursor_outbox_id = MAX(outbox_consumers.cursor_outbox_id, excluded.cursor_outbox_id),
                updated_at = excluded.updated_at;
            """;
        command.Parameters.AddWithValue("$consumer", consumer);
        command.Parameters.AddWithValue("$cursor", outboxId);
        command.Parameters.AddWithValue("$updated", PersistenceDatabase.Timestamp(clock));
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task<long> GetPendingCountAsync(DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        var clock = now ?? DateTimeOffset.UtcNow;
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM outbox WHERE acked_at IS NULL AND dead_at IS NULL AND available_at <= $now AND (claimed_by IS NULL OR claim_expires_at <= $now);";
        command.Parameters.AddWithValue("$now", PersistenceDatabase.Timestamp(clock));
        return Convert.ToInt64(await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false) ?? 0L);
    }

    /// <summary>Marks a poison message as dead-lettered; it stops being claimable.</summary>
    public async Task<bool> DeadLetterAsync(string workerId, long outboxId, string error, DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(workerId);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            UPDATE outbox
            SET dead_at = $dead, claimed_by = NULL, claim_expires_at = NULL, last_error = $error
            WHERE outbox_id = $id AND acked_at IS NULL AND dead_at IS NULL;
            """;
        command.Parameters.AddWithValue("$dead", PersistenceDatabase.Timestamp(clock));
        command.Parameters.AddWithValue("$error", error);
        command.Parameters.AddWithValue("$id", outboxId);
        return await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false) > 0;
    }

    public async Task<long> GetDeadLetterCountAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT COUNT(*) FROM outbox WHERE dead_at IS NOT NULL AND acked_at IS NULL;";
        return Convert.ToInt64(await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false) ?? 0L);
    }

    public async Task<IReadOnlyList<OutboxItem>> ReadDeadLettersAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT outbox_id, idempotency_key, topic, payload_json, created_at, available_at, attempts, claimed_by, claim_expires_at, acked_at, last_error, dead_at FROM outbox WHERE dead_at IS NOT NULL ORDER BY outbox_id;";
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        var items = new List<OutboxItem>();
        while (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            items.Add(ReadItem(reader));
        }

        return items;
    }

    public async Task<IReadOnlyList<OutboxItem>> ReadAllAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT outbox_id, idempotency_key, topic, payload_json, created_at, available_at, attempts, claimed_by, claim_expires_at, acked_at, last_error, dead_at FROM outbox ORDER BY outbox_id;";
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        var items = new List<OutboxItem>();
        while (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            items.Add(ReadItem(reader));
        }

        return items;
    }

    private static async Task<OutboxItem?> ReadItemAsync(SqliteConnection connection, SqliteTransaction transaction, long id, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "SELECT outbox_id, idempotency_key, topic, payload_json, created_at, available_at, attempts, claimed_by, claim_expires_at, acked_at, last_error, dead_at FROM outbox WHERE outbox_id = $id;";
        command.Parameters.AddWithValue("$id", id);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        return await reader.ReadAsync(cancellationToken).ConfigureAwait(false) ? ReadItem(reader) : null;
    }

    private static OutboxItem ReadItem(SqliteDataReader reader) => new(
        reader.GetInt64(0),
        reader.GetString(1),
        reader.GetString(2),
        reader.GetString(3),
        PersistenceDatabase.ParseTimestamp(reader.GetString(4)),
        PersistenceDatabase.ParseTimestamp(reader.GetString(5)),
        reader.GetInt32(6),
        reader.IsDBNull(7) ? null : reader.GetString(7),
        reader.IsDBNull(8) ? null : PersistenceDatabase.ParseTimestamp(reader.GetString(8)),
        reader.IsDBNull(9) ? null : PersistenceDatabase.ParseTimestamp(reader.GetString(9)),
        reader.IsDBNull(10) ? null : reader.GetString(10),
        reader.IsDBNull(11) ? null : PersistenceDatabase.ParseTimestamp(reader.GetString(11)));
}

public sealed record OutboxItem(
    long OutboxId,
    string IdempotencyKey,
    string Topic,
    string PayloadJson,
    DateTimeOffset CreatedAt,
    DateTimeOffset AvailableAt,
    int Attempts,
    string? ClaimedBy,
    DateTimeOffset? ClaimExpiresAt,
    DateTimeOffset? AckedAt,
    string? LastError,
    DateTimeOffset? DeadAt);
