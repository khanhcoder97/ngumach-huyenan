using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class OutboxTests
{
    [Fact]
    public async Task Claim_IsOrderedAndPreventsSecondClaim()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        for (var index = 0; index < 3; index++)
        {
            await fixture.CommitAsync(fixture.Request($"key-{index}", "char-a", lease.FencingToken, expected: index), $"{{\"gold\":{index}}}");
        }

        var claimed = await fixture.Outbox.ClaimAsync("worker-1", 2);
        Assert.Equal(2, claimed.Count);
        Assert.True(claimed[0].OutboxId < claimed[1].OutboxId);
        Assert.All(claimed, item => Assert.Equal("worker-1", item.ClaimedBy));
        Assert.All(claimed, item => Assert.Equal(1, item.Attempts));

        var other = await fixture.Outbox.ClaimAsync("worker-2", 10);
        Assert.Single(other);
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync());
    }

    [Fact]
    public async Task Ack_RemovesFromPending()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-ack", "char-a", lease.FencingToken), "{\"gold\":1}");

        var item = (await fixture.Outbox.ClaimAsync("worker-1", 1)).Single();
        Assert.True(await fixture.Outbox.AckAsync("worker-1", item.OutboxId));
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync());
        Assert.NotNull((await fixture.Outbox.ReadAllAsync()).Single().AckedAt);
    }

    [Fact]
    public async Task Fail_SchedulesRetryAfterBackoff()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-retry", "char-a", lease.FencingToken), "{\"gold\":1}");

        var item = (await fixture.Outbox.ClaimAsync("worker-1", 1)).Single();
        var now = DateTimeOffset.UtcNow;
        Assert.True(await fixture.Outbox.FailAsync("worker-1", item.OutboxId, "handler-failed", TimeSpan.FromMinutes(1), now));
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync(now));
        Assert.Equal(1, await fixture.Outbox.GetPendingCountAsync(now + TimeSpan.FromSeconds(61)));

        var retried = await fixture.Outbox.ClaimAsync("worker-2", 1, now: now + TimeSpan.FromSeconds(61));
        Assert.Equal(2, retried.Single().Attempts);
    }

    [Fact]
    public async Task ApplyOnce_SecondCall_DoesNotDuplicateEffect()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await using var connection = await fixture.Database.OpenAsync();
        await using (var create = connection.CreateCommand())
        {
            create.CommandText = "CREATE TABLE test_effects (effect TEXT PRIMARY KEY);";
            await create.ExecuteNonQueryAsync();
        }

        var first = await fixture.Outbox.ApplyOnceAsync("consumer-1", "effect-1", async (conn, tx, ct) =>
        {
            await using var command = conn.CreateCommand();
            command.Transaction = tx;
            command.CommandText = "INSERT INTO test_effects (effect) VALUES ('reward');";
            await command.ExecuteNonQueryAsync(ct);
        });
        var second = await fixture.Outbox.ApplyOnceAsync("consumer-1", "effect-1", async (conn, tx, ct) =>
        {
            await using var command = conn.CreateCommand();
            command.Transaction = tx;
            command.CommandText = "INSERT INTO test_effects (effect) VALUES ('reward');";
            await command.ExecuteNonQueryAsync(ct);
        });

        Assert.True(first);
        Assert.False(second);
        Assert.Equal(1, (await fixture.Database.GetTableCountsAsync())["consumer_effects"]);
    }

    [Fact]
    public async Task CrashAfterEffectBeforeAck_RetryDoesNotReapply()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-outbox-crash", "char-a", lease.FencingToken), "{\"gold\":1}");

        var item = (await fixture.Outbox.ClaimAsync("worker-1", 1)).Single();
        await using var connection = await fixture.Database.OpenAsync();
        await using (var create = connection.CreateCommand())
        {
            create.CommandText = "CREATE TABLE reward_effects (effect TEXT PRIMARY KEY);";
            await create.ExecuteNonQueryAsync();
        }

        // The consumer applies the effect (dedupe marker committed) and "crashes" before ack.
        await fixture.Outbox.ApplyOnceAsync("consumer-1", "outbox-" + item.OutboxId, async (conn, tx, ct) =>
        {
            await using var command = conn.CreateCommand();
            command.Transaction = tx;
            command.CommandText = "INSERT INTO reward_effects (effect) VALUES ('granted');";
            await command.ExecuteNonQueryAsync(ct);
        });

        // Claim expires; a second worker retries the same outbox row.
        var retried = await fixture.Outbox.ClaimAsync("worker-2", 1, now: DateTimeOffset.UtcNow + TimeSpan.FromMinutes(2));
        Assert.Single(retried);
        var appliedAgain = await fixture.Outbox.ApplyOnceAsync("consumer-1", "outbox-" + item.OutboxId, async (conn, tx, ct) =>
        {
            await using var command = conn.CreateCommand();
            command.Transaction = tx;
            command.CommandText = "INSERT INTO reward_effects (effect) VALUES ('granted');";
            await command.ExecuteNonQueryAsync(ct);
        }, now: DateTimeOffset.UtcNow + TimeSpan.FromMinutes(2));

        Assert.False(appliedAgain);
        await fixture.Outbox.AckAsync("worker-2", item.OutboxId, DateTimeOffset.UtcNow + TimeSpan.FromMinutes(2));
        Assert.Equal(0, await fixture.Outbox.GetPendingCountAsync(DateTimeOffset.UtcNow + TimeSpan.FromMinutes(3)));
    }

    [Fact]
    public async Task Cursor_PersistsMonotonically()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.Outbox.AdvanceCursorAsync("consumer-1", 5);
        await fixture.Outbox.AdvanceCursorAsync("consumer-1", 3);
        Assert.Equal(5, await fixture.Outbox.GetCursorAsync("consumer-1"));
    }
}
