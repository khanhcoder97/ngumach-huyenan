// OPC-16 O6 — encounter VFX binding tests.
// Proves the payload is an immutable copy of the authoritative cast shape/tick
// window and that each cast can start VFX at most once. Owner: OpenCode.

using System;
using System.Collections.Generic;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class EncounterVfxBinderTests
    {
        private const string CastOne = "CAST-ALPHA-00000001";
        private const string CastTwo = "CAST-ALPHA-00000002";

        private static EncounterSnapshot Snapshot(
            string castId = CastOne,
            string state = "TELEGRAPH",
            long serverTick = 2000,
            long endsAtTick = 2018,
            long ticksRemaining = 18)
        {
            return new EncounterSnapshot
            {
                SchemaVersion = 1,
                EncounterId = "ENC-0123456789ABCDEF01234567",
                QuestId = "P00-05",
                BossRecordId = "MAN-BM-SPAWN_BM_05_QUEST",
                BossEntityId = "ENT_BOSS_BM_05",
                BossLifeId = 1,
                BossRevision = 8,
                StatusRaw = "OPEN",
                PhaseRaw = 1,
                BossHp = 1200,
                BossMaxHp = 1200,
                ServerTick = serverTick,
                RegisteredCharacterIds = new List<string> { "CHR_TEST_A" },
                ActiveMove = new ActiveMove
                {
                    MoveId = "D",
                    CastId = castId,
                    StateRaw = state,
                    TicksRemaining = ticksRemaining,
                    StateEndsAtTick = endsAtTick,
                    TargetLock = "CHR_TEST_A",
                    Shape = new MoveShape
                    {
                        KindRaw = "CONE",
                        CenterXWu = 178,
                        CenterYWu = 0,
                        AngleDegrees = 120,
                        RangeWu = 8,
                        FacingX = 1,
                        FacingY = 0
                    }
                },
                MoveCooldownRemainingTicks = new Dictionary<string, long> { { "D", 0 } },
                PhaseGuardRemainingTicks = 0,
                WipeCountdownTicks = null,
                Arena = new EncounterArena
                {
                    Shape = "CIRCLE", CenterXWu = 178, CenterYWu = 0, RadiusWu = 11
                },
                SafePads = new List<SafePad>(),
                PhaseNpc = null,
                TrialNpcVisible = false
            };
        }

        private static EncounterUpdate NewCast(string castId = CastOne)
        {
            return new EncounterUpdate
            {
                Accepted = true,
                IsNewCast = true,
                CastId = castId
            };
        }

        [Fact]
        public void NewCast_BindsAuthoritativeShapeAndTickWindow()
        {
            var binder = new EncounterVfxBinder();
            var snapshot = Snapshot();

            EncounterVfxPayload payload;
            Assert.True(binder.TryBind(NewCast(), snapshot, out payload));
            Assert.NotNull(payload);
            Assert.Equal(CastOne, payload.CastId);
            Assert.Equal("D", payload.MoveId);
            Assert.Equal("ENC-0123456789ABCDEF01234567", payload.EncounterId);
            Assert.Equal(1, payload.BossLifeId);
            Assert.Equal(8, payload.BossRevision);
            Assert.Equal(2000, payload.ServerTick);
            Assert.Equal(2018, payload.StateEndsAtTick);
            Assert.Equal(18, payload.TicksRemaining);
            Assert.Equal(MoveState.Telegraph, payload.State);
            Assert.True(payload.IsTelegraph);
            Assert.Equal(BossPhase.Phase1, payload.Phase);
            Assert.Equal("CHR_TEST_A", payload.TargetLock);
            Assert.Equal(MoveShapeKind.Cone, payload.Shape.Kind);
            Assert.Equal(178, payload.Shape.CenterXWu);
            Assert.Equal(120, payload.Shape.AngleDegrees.Value);
            Assert.Equal(8, payload.Shape.RangeWu.Value);
            Assert.Equal(18, payload.RemainingTicksAt(2000));
            Assert.Equal(0, payload.RemainingTicksAt(2020));
            Assert.Equal(CastOne, binder.PendingCastId);
        }

        [Fact]
        public void Payload_IsCopyOfShape_NotLiveWireObject()
        {
            var binder = new EncounterVfxBinder();
            var snapshot = Snapshot();

            EncounterVfxPayload payload;
            Assert.True(binder.TryBind(snapshot, out payload));

            snapshot.ActiveMove.Shape.CenterXWu = 999;
            snapshot.ActiveMove.Shape.RangeWu = 50;
            snapshot.ActiveMove.CastId = CastTwo;

            Assert.Equal(178, payload.Shape.CenterXWu);
            Assert.Equal(8, payload.Shape.RangeWu.Value);
            Assert.Equal(CastOne, payload.CastId);
        }

        [Fact]
        public void SameCast_CannotBindTwice_UntilCommitted()
        {
            var binder = new EncounterVfxBinder();
            var snapshot = Snapshot();

            EncounterVfxPayload first;
            Assert.True(binder.TryBind(NewCast(), snapshot, out first));

            EncounterVfxPayload second;
            Assert.False(binder.TryBind(NewCast(), snapshot, out second));
            Assert.Null(second);
            Assert.False(binder.IsCommitted(CastOne));

            Assert.True(binder.Commit());
            Assert.False(binder.Commit()); // idempotent
            Assert.True(binder.IsCommitted(CastOne));
            Assert.Null(binder.PendingCastId);

            EncounterVfxPayload third;
            Assert.False(binder.TryBind(NewCast(), snapshot, out third));
            Assert.Null(third);
        }

        [Fact]
        public void NewCastAfterCommit_EmitsExactlyOnce()
        {
            var binder = new EncounterVfxBinder();

            EncounterVfxPayload first;
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out first));
            Assert.True(binder.Commit());

            EncounterVfxPayload second;
            Assert.True(binder.TryBind(NewCast(CastTwo), Snapshot(CastTwo, "RECOVERY", 2040, 2050, 10), out second));
            Assert.Equal(CastTwo, second.CastId);
            Assert.Equal(MoveState.Recovery, second.State);
            Assert.True(second.IsRecovery);
            Assert.Equal(10, second.TicksRemaining);
            Assert.True(binder.Commit());

            EncounterVfxPayload replay;
            Assert.False(binder.TryBind(NewCast(CastTwo), Snapshot(CastTwo, "RECOVERY", 2040, 2050, 10), out replay));
        }

        [Fact]
        public void SupersededPendingCast_NeverReplays()
        {
            var binder = new EncounterVfxBinder();

            EncounterVfxPayload first;
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out first));

            // A newer authoritative cast arrives before the caller committed the first.
            EncounterVfxPayload second;
            Assert.True(binder.TryBind(NewCast(CastTwo), Snapshot(CastTwo), out second));
            Assert.Equal(CastTwo, binder.PendingCastId);

            // The old payload was already handed out; re-observing it must not replay.
            EncounterVfxPayload oldAgain;
            Assert.False(binder.TryBind(Snapshot(), out oldAgain));
        }

        [Fact]
        public void CancelPending_AllowsRetryButCommittedCastStaysClosed()
        {
            var binder = new EncounterVfxBinder();

            EncounterVfxPayload first;
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out first));
            binder.CancelPending();
            Assert.Null(binder.PendingCastId);

            EncounterVfxPayload retry;
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out retry));
            Assert.Equal(CastOne, retry.CastId);
            Assert.True(binder.Commit());

            binder.CancelPending();
            EncounterVfxPayload afterCommit;
            Assert.False(binder.TryBind(NewCast(), Snapshot(), out afterCommit));
        }

        [Fact]
        public void Reset_AllowsNewLifeToBindAgain()
        {
            var binder = new EncounterVfxBinder();
            EncounterVfxPayload first;
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out first));
            Assert.True(binder.Commit());
            Assert.True(binder.IsCommitted(CastOne));

            binder.Reset();
            Assert.False(binder.IsCommitted(CastOne));
            Assert.Null(binder.PendingCastId);
            Assert.True(binder.TryBind(NewCast(), Snapshot(), out first));
        }

        [Fact]
        public void RejectedStaleOrMismatchedUpdate_BindsNothing()
        {
            var binder = new EncounterVfxBinder();
            var snapshot = Snapshot();
            EncounterVfxPayload payload;

            Assert.False(binder.TryBind(null, snapshot, out payload));
            Assert.False(binder.TryBind(NewCast(), null, out payload));

            Assert.False(binder.TryBind(new EncounterUpdate { Accepted = false, IsNewCast = true, CastId = CastOne },
                snapshot, out payload));
            Assert.False(binder.TryBind(new EncounterUpdate { Accepted = true, IsNewCast = false, CastId = CastOne },
                snapshot, out payload));
            Assert.False(binder.TryBind(NewCast(CastTwo), snapshot, out payload));
            Assert.Null(binder.PendingCastId);

            var noMove = Snapshot();
            noMove.ActiveMove = null;
            Assert.False(binder.TryBind(noMove, out payload));

            var noShape = Snapshot();
            noShape.ActiveMove.Shape = null;
            Assert.False(binder.TryBind(noShape, out payload));

            var noCast = Snapshot();
            noCast.ActiveMove.CastId = null;
            Assert.False(binder.TryBind(noCast, out payload));
        }
    }
}
