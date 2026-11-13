using Xunit;

namespace NguMach.Server.Persistence.Tests;

public sealed class UnitOfWorkTests
{
    [Fact]
    public async Task Commit_WritesStateReceiptLedgerAndOutboxAtomically()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var outcome = await fixture.CommitAsync(
            fixture.Request("key-1", "char-a", lease.FencingToken),
            "{\"gold\":10}",
            ("currency", "{\"gold\":10}"));

        Assert.Equal(MutationStatus.Committed, outcome.Status);
        Assert.Equal(1, outcome.Revision);
        Assert.Equal(1, outcome.LedgerEntries);
        Assert.Equal(1, outcome.OutboxMessages);

        var state = await fixture.Database.ReadStateAsync("char-a");
        Assert.Equal(1, state!.Revision);
        Assert.Equal("{\"gold\":10}", state.StateJson);

        var receipt = await fixture.Database.ReadReceiptAsync("key-1");
        Assert.NotNull(receipt);
        Assert.Equal(64, receipt!.RequestHash.Length);
        Assert.Equal(state.StateHash, receipt.ResultHash);

        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["ledger"]);
        Assert.Equal(1, counts["outbox"]);
    }

    [Fact]
    public async Task Replay_SameKeySamePayload_ReturnsHistoricalResultWithoutDuplicates()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var request = fixture.Request("key-replay", "char-a", lease.FencingToken);
        var first = await fixture.CommitAsync(request, "{\"gold\":10}", ("currency", "{\"gold\":10}"));

        // New database instance simulates a reconnect/restart: the stored result is read back.
        var reopened = new PersistenceDatabase(PersistenceOptions.ForFile(fixture.Workspace.DatabasePath));
        var second = await new DurableUnitOfWork(reopened).ExecuteAsync(request, _ => throw new Xunit.Sdk.XunitException("planner must not run for a replay"));

        Assert.Equal(MutationStatus.Replayed, second.Status);
        Assert.True(second.Replayed);
        Assert.Equal(first.ResultJson, second.ResultJson);
        Assert.Equal(first.Revision, second.Revision);

        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["ledger"]);
        Assert.Equal(1, counts["outbox"]);
    }

    [Fact]
    public async Task SameKeyDifferentPayload_IsConflictAndWritesNothing()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-conflict", "char-a", lease.FencingToken, body: "{\"amount\":1}"), "{\"gold\":1}");

        var outcome = await fixture.CommitAsync(
            fixture.Request("key-conflict", "char-a", lease.FencingToken, body: "{\"amount\":2}"),
            "{\"gold\":2}");

        Assert.Equal(MutationStatus.RequestConflict, outcome.Status);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["outbox"]);
        Assert.Equal("{\"gold\":1}", (await fixture.Database.ReadStateAsync("char-a"))!.StateJson);
    }

    [Fact]
    public async Task SameKeyForeignOwner_IsOwnerConflict()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a", "char-b");
        var leaseA = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-owner", "char-a", leaseA.FencingToken), "{\"gold\":1}");

        var leaseB = await fixture.AcquireAsync("char-b");
        var outcome = await fixture.CommitAsync(fixture.Request("key-owner", "char-b", leaseB.FencingToken), "{\"gold\":9}");

        Assert.Equal(MutationStatus.OwnerConflict, outcome.Status);
    }

    [Fact]
    public async Task StaleRevision_RollsBackStateLedgerAndOutbox()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-v1", "char-a", lease.FencingToken, expected: 0), "{\"gold\":1}", ("currency", "{\"gold\":1}"));

        var outcome = await fixture.CommitAsync(
            fixture.Request("key-stale", "char-a", lease.FencingToken, expected: 0),
            "{\"gold\":2}",
            ("currency", "{\"gold\":1}"));

        Assert.Equal(MutationStatus.RevisionConflict, outcome.Status);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["receipts"]);
        Assert.Equal(1, counts["ledger"]);
        Assert.Equal(1, counts["outbox"]);
        Assert.Equal("{\"gold\":1}", (await fixture.Database.ReadStateAsync("char-a"))!.StateJson);
    }

    [Fact]
    public async Task MissingLease_IsRefused()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var outcome = await fixture.CommitAsync(fixture.Request("key-no-lease", "char-a", fencing: 1), "{\"gold\":1}");
        Assert.Equal(MutationStatus.LeaseMissing, outcome.Status);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(0, counts["receipts"]);
        Assert.Equal(0, counts["ledger"]);
        Assert.Equal(0, counts["outbox"]);
    }

    [Fact]
    public async Task StaleFencingToken_IsRefused()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var start = DateTimeOffset.UtcNow;
        var first = await fixture.AcquireAsync("char-a", now: start);
        Assert.Equal(1, first.FencingToken);

        // Let the lease expire and the grace window pass, then a new owner takes over.
        var takeoverAt = start + fixture.Database.Options.LeaseTtl + fixture.Database.Options.ReconnectGrace + TimeSpan.FromSeconds(1);
        var second = await fixture.Leases.AcquireAsync("char-a", "char-a", takeoverAt);
        Assert.True(second.Succeeded);
        Assert.Equal(2, second.Lease!.FencingToken);

        var stale = await fixture.CommitAsync(fixture.Request("key-stale-fence", "char-a", first.FencingToken), "{\"gold\":1}");
        Assert.Equal(MutationStatus.StaleFencingToken, stale.Status);

        var current = await fixture.CommitAsync(fixture.Request("key-current-fence", "char-a", second.Lease.FencingToken), "{\"gold\":2}");
        Assert.Equal(MutationStatus.Committed, current.Status);
    }

    [Fact]
    public async Task RejectionAndCapacityRefusal_WriteNothing()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var request = fixture.Request("key-reject", "char-a", lease.FencingToken);

        var rejected = await fixture.UnitOfWork.ExecuteAsync(request, _ => PlanDecision.Reject("domain-rejected"));
        var capacity = await fixture.UnitOfWork.ExecuteAsync(request, _ => PlanDecision.CapacityExceeded("inventory-full"));

        Assert.Equal(MutationStatus.Rejected, rejected.Status);
        Assert.Equal(MutationStatus.CapacityExceeded, capacity.Status);
        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(0, counts["receipts"]);
        Assert.Equal(0, counts["ledger"]);
        Assert.Equal(0, counts["outbox"]);
        Assert.Null(await fixture.Database.ReadStateAsync("char-a"));
    }

    [Fact]
    public async Task UnknownCharacter_IsOwnershipDenied()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var outcome = await fixture.CommitAsync(fixture.Request("key-unknown", "char-ghost", fencing: 1), "{\"gold\":1}");
        Assert.Equal(MutationStatus.OwnershipDenied, outcome.Status);
    }

    [Fact]
    public async Task PlannerFailure_RollsBack()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var outcome = await fixture.UnitOfWork.ExecuteAsync(
            fixture.Request("key-planner-error", "char-a", lease.FencingToken),
            _ => throw new InvalidOperationException("boom"));

        Assert.Equal(MutationStatus.Failed, outcome.Status);
        Assert.Equal(0, (await fixture.Database.GetTableCountsAsync())["receipts"]);
    }

    [Fact]
    public async Task PrincipalAccount_MustOwnCharacter()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        var request = fixture.Request("key-principal", "char-a", lease.FencingToken) with { PrincipalAccountId = "account-1" };
        var committed = await fixture.CommitAsync(request, "{\"gold\":1}");
        Assert.Equal(MutationStatus.Committed, committed.Status);

        var otherLease = await fixture.AcquireAsync("char-a");
        var foreign = fixture.Request("key-principal-foreign", "char-a", otherLease.FencingToken) with { PrincipalAccountId = "account-other" };
        var denied = await fixture.CommitAsync(foreign, "{\"gold\":2}");
        Assert.Equal(MutationStatus.OwnershipDenied, denied.Status);
        Assert.Equal("account-does-not-own-character", denied.ErrorCode);
    }

    [Fact]
    public async Task OwnershipGatedReads_HideForeignCharacterAndReceipt()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        await fixture.Identity.CreateAccountAsync("account-2");
        await fixture.Identity.CreateCharacterAsync("char-b", "account-2");
        var lease = await fixture.AcquireAsync("char-a");
        await fixture.CommitAsync(fixture.Request("key-read", "char-a", lease.FencingToken), "{\"gold\":1}");

        Assert.NotNull(await fixture.Database.ReadStateAsync("char-a", "account-1"));
        Assert.Null(await fixture.Database.ReadStateAsync("char-a", "account-2"));
        Assert.NotNull(await fixture.Database.ReadReceiptAsync("key-read", "account-1"));
        Assert.Null(await fixture.Database.ReadReceiptAsync("key-read", "account-2"));
        Assert.Null(await fixture.Database.ReadStateAsync("char-missing", "account-1"));
    }
}
