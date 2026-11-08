using System;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class EncounterViewTests
    {
        private static EncounterSnapshot Snap(string castId = "cast-1", long life = 1, int phase = 1) =>
            new EncounterSnapshot
            {
                EncounterId = "enc-1", BossLifeId = life, StatusRaw = "OPEN", PhaseRaw = phase,
                ServerTick = 10, BossHp = 1200, BossMaxHp = 1200, BossRevision = 1,
                ActiveMove = new ActiveMove { CastId = castId, StateRaw = "TELEGRAPH", StateEndsAtTick = 20,
                    Shape = new MoveShape { KindRaw = "cone", RangeWu = 5, FacingX = 1, FacingY = 0, AngleDegrees = 60 } }
            };

        [Fact]
        public void Apply_SetsSnapshotAndReturnsNewEncounter()
        {
            var v = new EncounterView();
            var upd = v.Apply(Snap("cast-1"));
            Assert.True(v.HasSnapshot);
            Assert.True(v.IsTelegraphActive);
            Assert.True(upd.IsNewEncounter);
            Assert.True(upd.IsNewCast);
            Assert.Null(v.LastCastId); // not committed yet
            v.CommitCast();
            Assert.Equal("cast-1", v.LastCastId);
        }

        [Fact]
        public void SameCast_IsNotNew_AfterCommit()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1"));
            v.CommitCast();
            var upd = v.Apply(Snap("cast-1"));
            Assert.False(upd.IsNewCast);
        }

        [Fact]
        public void LifeChange_ResetsCastTracking()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1", 1));
            v.CommitCast();
            var upd = v.Apply(Snap("cast-1", 2)); // new life
            Assert.True(upd.IsNewLife);
            Assert.True(upd.IsNewCast);
        }

        [Fact]
        public void Reset_ClearsEverything()
        {
            var v = new EncounterView();
            v.Apply(Snap());
            v.CommitCast();
            v.Reset();
            Assert.False(v.HasSnapshot);
            Assert.Null(v.LastCastId);
        }

        [Fact]
        public void RemainingTicks_ClampsAtZero()
        {
            var v = new EncounterView();
            v.Apply(Snap());
            Assert.Equal(10, v.RemainingTicks(10));
            Assert.Equal(0, v.RemainingTicks(100));
        }

        [Fact]
        public void NullApply_Throws()
        {
            var v = new EncounterView();
            Assert.Throws<ArgumentNullException>(() => v.Apply(null));
        }

        [Fact]
        public void CancelPendingVfx_ClearsPending()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-2"));
            Assert.True(v.PendingCastId == "cast-2");
            v.CancelPendingVfx();
            Assert.Null(v.PendingCastId);
        }

        [Fact]
        public void SameCastPollBeforeCommit_KeepsPending()
        {
            var v = new EncounterView();
            var first = v.Apply(Snap("cast-1"));
            Assert.True(first.IsNewCast);
            var second = v.Apply(Snap("cast-1"));
            Assert.False(second.IsNewCast);
            Assert.Equal("cast-1", v.PendingCastId);
            Assert.Null(v.LastCastId);
            v.CommitCast();
            Assert.Equal("cast-1", v.LastCastId);
        }

        [Fact]
        public void StaleLife_IsRejectedAndDoesNotOverwrite()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-2", 2));
            Assert.True(v.HasSnapshot);
            var update = v.Apply(Snap("cast-1", 1));
            Assert.False(update.Accepted);
            Assert.Contains("stale life", update.RejectReason);
            Assert.Equal(2, v.Snapshot.BossLifeId);
            Assert.Equal("cast-2", v.Snapshot.ActiveMove.CastId);
        }

        [Fact]
        public void StaleRevision_IsRejectedAndDoesNotOverwrite()
        {
            var v = new EncounterView();
            var newer = Snap("cast-2", 1);
            newer.BossRevision = 5;
            v.Apply(newer);
            var older = Snap("cast-1", 1);
            older.BossRevision = 4;
            var update = v.Apply(older);
            Assert.False(update.Accepted);
            Assert.Contains("stale revision", update.RejectReason);
            Assert.Equal(5, v.Snapshot.BossRevision);
        }

        [Fact]
        public void StaleServerTick_IsRejectedAtSameLifeAndRevision()
        {
            var v = new EncounterView();
            var newer = Snap("cast-2", 1);
            newer.ServerTick = 50;
            v.Apply(newer);
            // Same life and revision with a rewound tick must never roll back
            // the countdown the players are already looking at.
            var older = Snap("cast-1", 1);
            older.ServerTick = 40;
            var update = v.Apply(older);
            Assert.False(update.Accepted);
            Assert.Contains("stale server tick", update.RejectReason);
            Assert.Equal(50, v.Snapshot.ServerTick);
            // An equal tick is an idempotent re-poll and stays accepted.
            var sameTick = Snap("cast-1", 1);
            sameTick.ServerTick = 50;
            Assert.True(v.Apply(sameTick).Accepted);
        }

        [Fact]
        public void NewLife_ClearsPendingVfxAndTracksNewCast()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1", 1));
            v.CommitCast();
            var update = v.Apply(Snap("cast-2", 2));
            Assert.True(update.Accepted);
            Assert.True(update.IsNewLife);
            Assert.True(update.IsNewCast);
            Assert.Equal("cast-2", v.PendingCastId);
        }

        [Fact]
        public void TerminalStatus_IsReportedAndClearsPending()
        {
            var v = new EncounterView();
            var snap = Snap("cast-1");
            snap.StatusRaw = "DEFEATED";
            var update = v.Apply(snap);
            Assert.True(update.IsTerminal);
            Assert.False(update.IsNewCast);
            Assert.Null(v.PendingCastId);
            Assert.Equal(EncounterStatus.Defeated, v.Snapshot.Status);
        }

        [Fact]
        public void PhaseChange_IsReported()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1", 1, 1));
            var update = v.Apply(Snap("cast-2", 1, 2));
            Assert.True(update.PhaseChanged);
            Assert.Equal(BossPhase.Phase2, v.Snapshot.Phase);
        }

        [Fact]
        public void RemainingTicks_UsesSnapshotServerTick()
        {
            var v = new EncounterView();
            v.Apply(Snap());
            Assert.Equal(10, v.RemainingTicks());
        }
    }
}
