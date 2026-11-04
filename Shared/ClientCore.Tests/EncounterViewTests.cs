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
    }
}
