using System.Text.Json;
using Xunit;

namespace NguMach.Server.Persistence.Tests;

/// <summary>
/// R2/R7: death/return before-after snapshots, global receipt semantics and the guarantee
/// that a replay is history rather than a fresh grant in a later life.
/// </summary>
public sealed class LifeReceiptTests
{
    [Fact]
    public async Task DeathAndReturn_CommitLifeProvenanceAtomically()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");

        var death = await CommitDeathAsync(fixture, lease, "key-death", lifeVersion: 1, expected: 0, revision: 1);
        Assert.Equal(MutationStatus.Committed, death.Status);

        var before = new LifeSnapshot("char-a", 1, DeathRecord(1, 1));
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        var outcome = await fixture.UnitOfWork.ExecuteAsync(
            request,
            _ => PlanDecision.Accept(new MutationPlan("{\"hp\":50}", Array.Empty<LedgerEntry>(), Array.Empty<OutboxMessage>())
            {
                Life = LifeTransition.ForReturn(before, new LifeSnapshot("char-a", 2, before.LatestDeath), ReturnCommit(request, before, revision: 2))
            }));

        Assert.Equal(MutationStatus.Committed, outcome.Status);
        var life = await fixture.Life.ReadLifeAsync("char-a");
        Assert.NotNull(life);
        Assert.Equal(2, life!.LifeVersion);
        Assert.Equal("PDEATH_test_1_1", life.LatestDeath!.DeathEventId);

        var lookup = await fixture.Life.LookupReturnAsync("key-return");
        Assert.Equal(ReturnLookupKind.Committed, lookup.Kind);
        Assert.Equal("char-a", lookup.OwnerCharacterId);
        Assert.Equal(2, lookup.Commit!.After.LifeVersion);
        Assert.True(lookup.Commit.CommittedResult.Applied);
        Assert.Equal(50, lookup.Commit.CommittedResult.Hp);
        Assert.Equal(1000, lookup.Commit.CommittedResult.ServerTick);
        Assert.Equal(1, lookup.Commit.CommittedResult.InflightCastsCancelled);

        var counts = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(1, counts["life_state"]);
        Assert.Equal(1, counts["life_receipts"]);
    }

    [Fact]
    public async Task ReturnReplay_ReturnsHistoricalResultWithoutAdvancingLife()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, request, beforeLife: 1, revision: 2);

        var replay = await fixture.UnitOfWork.ExecuteAsync(
            request,
            _ => throw new Xunit.Sdk.XunitException("return replay must not plan a new transition"));

        Assert.Equal(MutationStatus.Replayed, replay.Status);
        Assert.True(replay.Replayed);
        Assert.Equal(2, replay.Revision);
        Assert.Equal("{\"hp\":50}", replay.ResultJson);
        Assert.Equal(2, (await fixture.Life.ReadLifeAsync("char-a"))!.LifeVersion);
        Assert.Equal(1, (await fixture.Database.GetTableCountsAsync())["life_receipts"]);
    }

    [Fact]
    public async Task ReturnKey_IsGlobal_OtherOwnerConflicts()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a", "char-b");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, request, beforeLife: 1, revision: 2);

        var otherLease = await fixture.AcquireAsync("char-b");
        var conflict = await fixture.UnitOfWork.ExecuteAsync(
            fixture.Request("key-return", "char-b", otherLease.FencingToken, expected: 0),
            _ => throw new Xunit.Sdk.XunitException("foreign owner must not plan"));

        Assert.Equal(MutationStatus.OwnerConflict, conflict.Status);
        Assert.Equal("idempotency-key-owned-by-another-character", conflict.ErrorCode);
        Assert.Null(await fixture.Life.ReadLifeAsync("char-b"));
    }

    [Fact]
    public async Task StaleLifeSnapshot_IsRefusedAndRollsBackTheWholeCommand()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var first = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, first, beforeLife: 1, revision: 2);

        // A second command tries to return again from the already-superseded life 1.
        var stale = fixture.Request("key-return-stale", "char-a", lease.FencingToken, expected: 2);
        var outcome = await fixture.UnitOfWork.ExecuteAsync(
            stale,
            _ => PlanDecision.Accept(new MutationPlan("{\"hp\":999}", Array.Empty<LedgerEntry>(), new[] { new OutboxMessage("bad", "{}") })
            {
                Life = LifeTransition.ForReturn(
                    new LifeSnapshot("char-a", 1, DeathRecord(1, 1)),
                    new LifeSnapshot("char-a", 2, DeathRecord(1, 1)),
                    ReturnCommit(stale, new LifeSnapshot("char-a", 1, DeathRecord(1, 1)), revision: 3))
            }));

        Assert.Equal(MutationStatus.RevisionConflict, outcome.Status);
        Assert.Equal(PersistenceErrorCodes.LifeVersionConflict, outcome.ErrorCode);
        Assert.Null(await fixture.Database.ReadReceiptAsync("key-return-stale"));
        Assert.Equal("{\"hp\":50}", (await fixture.Database.ReadStateAsync("char-a"))!.StateJson);
        Assert.Equal(2, (await fixture.Life.ReadLifeAsync("char-a"))!.LifeVersion);
        Assert.Equal(0, (await fixture.Database.GetTableCountsAsync())["outbox"]);
    }

    [Fact]
    public async Task Tombstone_IsNotMissingAndNotAFreshCommand()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, request, beforeLife: 1, revision: 2);

        // Expiry is not approved, so nothing in the library sets this; the read side still
        // has to treat an explicitly tombstoned receipt as not-Missing.
        await fixture.ExecuteAsync("UPDATE life_receipts SET tombstoned_at = '2026-11-14T00:00:00.0000000+00:00' WHERE idempotency_key = 'key-return';");

        var lookup = await fixture.Life.LookupReturnAsync("key-return");
        Assert.Equal(ReturnLookupKind.Tombstoned, lookup.Kind);
        Assert.Equal("char-a", lookup.OwnerCharacterId);
        Assert.Null(lookup.Commit);
    }

    [Fact]
    public async Task OldReturnKey_InLaterLife_StillReplaysHistoryAndDoesNotHeal()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");

        // Life 1: death and return.
        await CommitDeathAsync(fixture, lease, "key-death-1", 1, 0, 1);
        var life1Return = fixture.Request("key-return-1", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, life1Return, beforeLife: 1, revision: 2);

        // The character is downed again in life 2 and returned into life 3.
        await CommitDeathAsync(fixture, lease, "key-death-2", 2, 2, 3);
        var life2Return = fixture.Request("key-return-2", "char-a", lease.FencingToken, expected: 3);
        await CommitReturnAsync(fixture, life2Return, beforeLife: 2, revision: 4);

        var replay = await fixture.UnitOfWork.ExecuteAsync(
            life1Return,
            _ => throw new Xunit.Sdk.XunitException("old return key must not plan a new transition"));

        Assert.Equal(MutationStatus.Replayed, replay.Status);
        Assert.Equal(2, replay.Revision);
        Assert.Equal(3, (await fixture.Life.ReadLifeAsync("char-a"))!.LifeVersion);
        Assert.Equal(2, (await fixture.Database.GetTableCountsAsync())["life_receipts"]);
    }

    [Fact]
    public async Task ThreeHundredOtherReceipts_DoNotExpireAnOldReturnKey()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, request, beforeLife: 1, revision: 2);

        for (var index = 0; index < 300; index++)
        {
            var character = "char-churn-" + index;
            await fixture.Identity.CreateCharacterAsync(character, "account-1");
            var churnLease = await fixture.AcquireAsync(character);
            await fixture.CommitAsync(fixture.Request("key-churn-" + index, character, churnLease.FencingToken), "{\"life\":1}");
        }

        Assert.Equal(ReturnLookupKind.Committed, (await fixture.Life.LookupReturnAsync("key-return")).Kind);
        var replay = await fixture.UnitOfWork.ExecuteAsync(request, _ => throw new Xunit.Sdk.XunitException("churn must not expire the key"));
        Assert.Equal(MutationStatus.Replayed, replay.Status);
        Assert.Equal(2, (await fixture.Life.ReadLifeAsync("char-a"))!.LifeVersion);
    }

    [Fact]
    public async Task TenThousandReplays_DoNotChangeLifeOrGrantAgain()
    {
        await using var fixture = await TestFixture.CreateAsync("char-a");
        var lease = await fixture.AcquireAsync("char-a");
        await CommitDeathAsync(fixture, lease, "key-death", 1, 0, 1);
        var request = fixture.Request("key-return", "char-a", lease.FencingToken, expected: 1);
        await CommitReturnAsync(fixture, request, beforeLife: 1, revision: 2);
        var before = await fixture.Database.GetTableCountsAsync();

        for (var index = 0; index < 10_000; index++)
        {
            var outcome = await fixture.UnitOfWork.ExecuteAsync(request, _ => throw new Xunit.Sdk.XunitException("replay must not plan"));
            Assert.Equal(MutationStatus.Replayed, outcome.Status);
        }

        var after = await fixture.Database.GetTableCountsAsync();
        Assert.Equal(2, (await fixture.Life.ReadLifeAsync("char-a"))!.LifeVersion);
        Assert.Equal(before["receipts"], after["receipts"]);
        Assert.Equal(before["ledger"], after["ledger"]);
        Assert.Equal(before["outbox"], after["outbox"]);
        Assert.Equal(before["life_receipts"], after["life_receipts"]);
        Assert.NotNull((await fixture.Life.LookupReturnAsync("key-return")).Commit);
    }

    private static async Task<MutationOutcome> CommitDeathAsync(
        TestFixture fixture,
        LeaseGrant lease,
        string key,
        int lifeVersion,
        long expected,
        long revision)
    {
        var before = await fixture.Life.ReadLifeAsync("char-a") ?? new LifeSnapshot("char-a", 1, null);
        var death = DeathRecord(lifeVersion, revision);
        var request = fixture.Request(key, "char-a", lease.FencingToken, expected);
        return await fixture.UnitOfWork.ExecuteAsync(
            request,
            _ => PlanDecision.Accept(new MutationPlan("{\"hp\":0}", Array.Empty<LedgerEntry>(), Array.Empty<OutboxMessage>())
            {
                Life = LifeTransition.ForDeath(before, new LifeSnapshot("char-a", lifeVersion, death), death)
            }));
    }

    private static async Task<MutationOutcome> CommitReturnAsync(
        TestFixture fixture,
        MutationRequest request,
        int beforeLife,
        long revision)
    {
        var before = await fixture.Life.ReadLifeAsync(request.OwnerCharacterId)
                     ?? new LifeSnapshot(request.OwnerCharacterId, beforeLife, null);
        var after = new LifeSnapshot(request.OwnerCharacterId, beforeLife + 1, before.LatestDeath);
        return await fixture.UnitOfWork.ExecuteAsync(
            request,
            _ => PlanDecision.Accept(new MutationPlan("{\"hp\":50}", Array.Empty<LedgerEntry>(), Array.Empty<OutboxMessage>())
            {
                Life = LifeTransition.ForReturn(before, after, ReturnCommit(request, before, revision))
            }));
    }

    private static LifeReturnCommit ReturnCommit(MutationRequest request, LifeSnapshot before, long revision)
    {
        var after = new LifeSnapshot(request.OwnerCharacterId, before.LifeVersion + 1, before.LatestDeath);
        return new LifeReturnCommit(
            request.IdempotencyKey,
            CanonicalJson.HashRequest(request.Operation, request.RequestJson),
            before,
            after,
            new DeathReturnResultSnapshot(
                Applied: true,
                Replayed: false,
                ErrorCode: null,
                SessionId: "session-1",
                CharacterId: request.OwnerCharacterId,
                MapId: "MAP_BEN_MUA",
                X: 18,
                Y: 0,
                Hp: 50,
                MaxHp: 100,
                Mp: 10,
                MaxMp: 20,
                Revision: revision,
                ServerTick: 1000,
                InflightCastsCancelled: 1,
                ReservedCountersCancelled: 0,
                GuardWindowClosed: true,
                MovementTimingReset: true,
                NextReturnAllowedAtTick: 1060,
                DeathEventId: before.LatestDeath?.DeathEventId,
                NewLifeVersion: after.LifeVersion),
            DateTimeOffset.UtcNow);
    }

    private static PlayerDeathSnapshot DeathRecord(int lifeVersion, long revision) =>
        new("char-a", lifeVersion, revision, "PDEATH_test_" + lifeVersion + "_" + revision,
            new DateTimeOffset(2026, 11, 14, 0, 0, 0, TimeSpan.Zero));
}
