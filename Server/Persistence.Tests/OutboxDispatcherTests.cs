using Microsoft.Data.Sqlite;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class OutboxDispatcherTests
{
    [Fact]
    public async Task Dispatch_AppliesAcksAndAdvancesCursor()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.ExecuteAsync("CREATE TABLE reward_effects (effect TEXT PRIMARY KEY);");
        var item = await CommitOneAsync(fixture, "key-dispatch");
        var dispatcher = new OutboxDispatcher(fixture.Outbox);

        var report = await dispatcher.DispatchBatchAsync("consumer-1", "worker-1", async (outboxItem, applyOnce, ct) =>
        {
            await applyOnce(async (connection, transaction, token) =>
            {
                await using var command = connection.CreateCommand();
                command.Transaction = transaction;
                command.CommandText = "INSERT INTO reward_effects (effect) VALUES ('granted');";
                await command.ExecuteNonQueryAsync(token);
            });
        });

        Assert.Equal(1, report.Claimed);
        Assert.Equal(1, report.Applied);
        Assert.Equal(0, report.Retried);
        Assert.Equal(0, report.DeadLetteredCount);
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync());
        Assert.Equal(item.OutboxId, await fixture.Outbox.GetCursorAsync("consumer-1"));
    }

    [Fact]
    public async Task Dispatch_HandlerCrashAfterEffect_RetryDoesNotDoubleGrant()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.ExecuteAsync("CREATE TABLE reward_effects (effect TEXT PRIMARY KEY);");
        await CommitOneAsync(fixture, "key-dispatch-crash");
        var dispatcher = new OutboxDispatcher(fixture.Outbox);
        var now = DateTimeOffset.UtcNow;

        var first = await dispatcher.DispatchBatchAsync("consumer-1", "worker-1", async (outboxItem, applyOnce, ct) =>
        {
            await applyOnce(async (connection, transaction, token) =>
            {
                await using var command = connection.CreateCommand();
                command.Transaction = transaction;
                command.CommandText = "INSERT INTO reward_effects (effect) VALUES ('granted');";
                await command.ExecuteNonQueryAsync(token);
            });
            throw new InvalidOperationException("consumer died before ack");
        }, now: now);

        Assert.Equal(1, first.Retried);

        var second = await dispatcher.DispatchBatchAsync("consumer-1", "worker-2", async (outboxItem, applyOnce, ct) =>
        {
            // The effect is already recorded; applyOnce returns false and inserts nothing.
            var applied = await applyOnce(async (connection, transaction, token) =>
            {
                await using var command = connection.CreateCommand();
                command.Transaction = transaction;
                command.CommandText = "INSERT INTO reward_effects (effect) VALUES ('granted');";
                await command.ExecuteNonQueryAsync(token);
            });
            Assert.False(applied);
        }, now: now + TimeSpan.FromMinutes(5));

        Assert.Equal(1, second.Applied);
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync(now + TimeSpan.FromMinutes(6)));
        Assert.Equal(1, await CountAsync(fixture, "reward_effects"));
    }

    [Fact]
    public async Task Dispatch_PoisonMessage_IsDeadLetteredAfterBound()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await CommitOneAsync(fixture, "key-poison");
        var dispatcher = new OutboxDispatcher(fixture.Outbox, TimeSpan.FromSeconds(1));
        var now = DateTimeOffset.UtcNow;
        var deadLettered = 0;

        for (var attempt = 0; attempt < 6 && deadLettered == 0; attempt++)
        {
            var report = await dispatcher.DispatchBatchAsync(
                "consumer-1",
                "worker-" + attempt,
                (_, _, _) => throw new InvalidOperationException("poison"),
                maxAttempts: 3,
                retryBackoff: TimeSpan.FromMilliseconds(1),
                now: now + TimeSpan.FromSeconds(attempt));
            deadLettered = report.DeadLetteredCount;
            Assert.True(report.Claimed <= 1);
        }

        Assert.Equal(1, deadLettered);
        Assert.Equal(1, await fixture.Outbox.GetDeadLetterCountAsync());
        Assert.Single(await fixture.Outbox.ReadDeadLettersAsync());
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync(now + TimeSpan.FromHours(1)));
    }

    [Fact]
    public async Task Dispatch_BatchIsBounded()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.ExecuteAsync("CREATE TABLE reward_effects (effect TEXT PRIMARY KEY);");
        var lease = await fixture.AcquireAsync("char-a");
        for (var index = 0; index < 5; index++)
        {
            await fixture.CommitAsync(fixture.Request("key-batch-" + index, "char-a", lease.FencingToken, expected: index), $"{{\"gold\":{index}}}");
        }

        var dispatcher = new OutboxDispatcher(fixture.Outbox);
        var report = await dispatcher.DispatchBatchAsync("consumer-1", "worker-1", async (outboxItem, applyOnce, ct) =>
        {
            await applyOnce(async (connection, transaction, token) =>
            {
                await using var command = connection.CreateCommand();
                command.Transaction = transaction;
                command.CommandText = "INSERT OR IGNORE INTO reward_effects (effect) VALUES ($effect);";
                command.Parameters.AddWithValue("$effect", outboxItem.OutboxId.ToString(System.Globalization.CultureInfo.InvariantCulture));
                await command.ExecuteNonQueryAsync(token);
            });
        }, batchSize: 2);

        Assert.Equal(2, report.Claimed);
        Assert.Equal(2, report.Applied);
        Assert.Equal(3, await fixture.Outbox.GetPendingCountAsync());
    }

    private static async Task<OutboxItem> CommitOneAsync(TestFixture fixture, string key)
    {
        var lease = await fixture.AcquireAsync("char-a");
        var outcome = await fixture.CommitAsync(fixture.Request(key, "char-a", lease.FencingToken), "{\"gold\":1}");
        Assert.Equal(MutationStatus.Committed, outcome.Status);
        return (await fixture.Outbox.ReadAllAsync()).Single();
    }

    private static async Task<long> CountAsync(TestFixture fixture, string table)
    {
        await using var connection = await fixture.Database.OpenAsync();
        await using var command = connection.CreateCommand();
        command.CommandText = $"SELECT COUNT(*) FROM {table};";
        return (long)(await command.ExecuteScalarAsync() ?? 0L);
    }
}
