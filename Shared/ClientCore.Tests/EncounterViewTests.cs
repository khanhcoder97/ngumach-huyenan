using System;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class EncounterViewTests
    {
        private static EncounterSnapshot Snap(string castId = "cast-1", long gen = 1, string life = "life-1") =>
            new EncounterSnapshot
            {
                EncounterId = "enc-1", BossLifeId = life, Generation = gen,
                Phase = "Telegraph", ServerTick = 10, Hp = 1200, MaxHp = 1200,
                Revision = 1, ActiveMove = new ActiveMove { CastId = castId, StateEndsAtTick = 20,
                    Shape = new MoveShape { Type = "cone", FacingX = 1, FacingY = 0, AngleDegrees = 60 } },
                DeadlineTick = 20
            };

        [Fact]
        public void Apply_SetsSnapshotAndTracksCast()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1"));
            Assert.True(v.HasSnapshot);
            Assert.True(v.IsTelegraphActive);
            Assert.Equal("cast-1", v.LastCastId);
        }

        [Fact]
        public void SameCast_IsNotNew()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1"));
            Assert.False(v.IsNewCast("cast-1"));
            Assert.True(v.IsNewCast("cast-2"));
        }

        [Fact]
        public void LifeChange_ResetsCastTracking()
        {
            var v = new EncounterView();
            v.Apply(Snap("cast-1", 1, "life-1"));
            v.Apply(Snap("cast-1", 2, "life-2")); // new life/generation
            // cast id same string but new life => tracking reset then re-set; still recorded
            Assert.Equal("cast-1", v.LastCastId);
            Assert.Equal(2, v.LastLifeGeneration);
        }

        [Fact]
        public void Reset_ClearsEverything()
        {
            var v = new EncounterView();
            v.Apply(Snap());
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
    }
}
