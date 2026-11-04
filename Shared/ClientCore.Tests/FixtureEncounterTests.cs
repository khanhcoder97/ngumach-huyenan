using System;
using System.IO;
using Newtonsoft.Json;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class FixtureEncounterTests
    {
        private static string LoadReference()
        {
            var candidates = new[]
            {
                Path.Combine("Fixtures", "encounter_snapshot_v1_reference_20261104.json"),
                Path.Combine("..", "..", "..", "Fixtures", "encounter_snapshot_v1_reference_20261104.json"),
                @"D:\Project\NGUMACHHUYENAN-opencode-godot-core-20261103\Shared\ClientCore.Tests\Fixtures\encounter_snapshot_v1_reference_20261104.json",
            };
            foreach (var c in candidates) if (File.Exists(c)) return File.ReadAllText(c);
            throw new FileNotFoundException("reference fixture not found");
        }

        [Fact]
        public void Reference_ParsesStrictly()
        {
            var json = LoadReference();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out var err), err);
            Assert.NotNull(snap);
            Assert.Equal("ENC-0123456789ABCDEF01234567", snap.EncounterId);
            Assert.Equal("P00-05", snap.QuestId);
            Assert.Equal("MAN-BM-SPAWN_BM_05_QUEST", snap.BossRecordId);
            Assert.Equal(1L, snap.BossLifeId);
            Assert.Equal(8L, snap.BossRevision);
            Assert.Equal(EncounterStatus.Open, snap.Status);
            Assert.Equal(BossPhase.Phase1, snap.Phase);
            Assert.Equal(1200, snap.BossHp);
            Assert.Equal(1200, snap.BossMaxHp);
            Assert.Equal(2000L, snap.ServerTick);
            Assert.NotNull(snap.RegisteredCharacterIds);
            Assert.Single(snap.RegisteredCharacterIds);
            Assert.NotNull(snap.ActiveMove);
            Assert.Equal("CAST-ALPHA-00000001", snap.ActiveMove.CastId);
            Assert.Equal(MoveState.Telegraph, snap.ActiveMove.State);
            Assert.Equal(18, snap.ActiveMove.TicksRemaining);
            Assert.Equal(2018L, snap.ActiveMove.StateEndsAtTick);
            Assert.Equal(MoveShapeKind.Cone, snap.ActiveMove.Shape.Kind);
            Assert.Equal(178.0, snap.ActiveMove.Shape.CenterXWu);
            Assert.Equal(0.0, snap.ActiveMove.Shape.CenterYWu);
            Assert.Equal(120.0, snap.ActiveMove.Shape.AngleDegrees);
            Assert.Equal(8.0, snap.ActiveMove.Shape.RangeWu);
            Assert.Equal(1.0, snap.ActiveMove.Shape.FacingX);
            Assert.Equal(0.0, snap.ActiveMove.Shape.FacingY);
            Assert.NotNull(snap.MoveCooldownRemainingTicks);
            Assert.Equal(3, snap.MoveCooldownRemainingTicks.Count);
            Assert.NotNull(snap.Arena);
            Assert.Equal("CIRCLE", snap.Arena.Shape);
            Assert.Equal(11.0, snap.Arena.RadiusWu);
            Assert.NotNull(snap.SafePads);
            Assert.Equal(2, snap.SafePads.Count);
            Assert.NotNull(snap.PhaseNpc);
            Assert.Equal("NPC_TA_VAN_KHANH", snap.PhaseNpc.NpcId);
            Assert.False(snap.TrialNpcVisible);
        }

        [Fact]
        public void Reference_ViewAppliesAndTracksCast()
        {
            var json = LoadReference();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out _));
            var view = new EncounterView();
            var upd = view.Apply(snap);
            Assert.True(view.HasSnapshot);
            Assert.True(view.IsTelegraphActive);
            Assert.True(upd.IsNewEncounter);
            Assert.True(upd.IsNewCast);
            Assert.Null(view.LastCastId);
            view.CommitCast();
            Assert.Equal("CAST-ALPHA-00000001", view.LastCastId);
            var upd2 = view.Apply(snap);
            Assert.False(upd2.IsNewCast);
        }

        [Fact]
        public void Reference_Strict_RejectsUnknownProperty()
        {
            var json = LoadReference().Replace("\"phaseNpc\"", "\"phaseNpcX\"");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out var err));
            Assert.False(string.IsNullOrEmpty(err));
        }

        [Fact]
        public void Reference_Strict_RejectsInvalidPhase()
        {
            var json = LoadReference().Replace("\"phase\": 1", "\"phase\": 9");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out _));
        }

        [Fact]
        public void Reference_Strict_RejectsNaN()
        {
            var json = LoadReference().Replace("0.8660254", "NaN");
            // NaN not present in reference; inject into facingX
            json = LoadReference().Replace("\"facingX\": 1.0", "\"facingX\": NaN");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out _));
        }

        [Fact]
        public void Reference_Strict_RejectsNonNormalizedFacing()
        {
            var json = LoadReference().Replace("\"facingX\": 1.0", "\"facingX\": 2.0");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out _));
        }
    }
}
