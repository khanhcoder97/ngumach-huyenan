using System;
using System.IO;
using Newtonsoft.Json;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class FixtureEncounterTests
    {
        private static string LoadFixture()
        {
            var candidates = new[]
            {
                Path.Combine("Fixtures", "encounter_v1.json"),
                Path.Combine("..", "..", "..", "Fixtures", "encounter_v1.json"),
                @"D:\Project\NGUMACHHUYENAN-opencode-godot-core-20261103\Shared\ClientCore.Tests\Fixtures\encounter_v1.json",
            };
            foreach (var c in candidates) if (File.Exists(c)) return File.ReadAllText(c);
            throw new FileNotFoundException("encounter_v1.json fixture not found");
        }

        [Fact]
        public void Fixture_ParsesAndValidates()
        {
            var json = LoadFixture();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out var err), err);
            Assert.NotNull(snap);
            Assert.Equal("enc-fixture-001", snap.EncounterId);
            Assert.Equal(EncounterStatus.Open, snap.Status);
            Assert.Equal(BossPhase.Phase1, snap.Phase);
            Assert.Equal(1200, snap.BossHp);
            Assert.Equal(1200, snap.BossMaxHp);
            Assert.NotNull(snap.ActiveMove);
            Assert.Equal("cast-fixture-001", snap.ActiveMove.CastId);
            Assert.Equal(MoveState.Telegraph, snap.ActiveMove.State);
            Assert.NotNull(snap.ActiveMove.Shape);
            Assert.True(MoveShapeValidator.IsValid(snap.ActiveMove.Shape, out var reason), reason);
            Assert.Equal(MoveShapeKind.Cone, snap.ActiveMove.Shape.Kind);
        }

        [Fact]
        public void Fixture_ViewAppliesAndTracksCast()
        {
            var json = LoadFixture();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out _));
            var view = new EncounterView();
            var upd = view.Apply(snap);
            Assert.True(view.HasSnapshot);
            Assert.True(view.IsTelegraphActive);
            Assert.True(upd.IsNewEncounter);
            Assert.True(upd.IsNewCast);
            // LastCastId is NOT advanced until the consumer commits after handling VFX.
            Assert.Null(view.LastCastId);
            view.CommitCast();
            Assert.Equal("cast-fixture-001", view.LastCastId);
            // same cast again is not new
            var upd2 = view.Apply(snap);
            Assert.False(upd2.IsNewCast);
        }

        [Fact]
        public void Fixture_ShapeFacing_NormalizedWithinTolerance()
        {
            var json = LoadFixture();
            Assert.True(EncounterSnapshotValidator.TryParse(json, out var snap, out _));
            var sh = snap.ActiveMove.Shape;
            double len = Math.Sqrt(sh.FacingX * sh.FacingX + sh.FacingY * sh.FacingY);
            Assert.True(len > 0.99 && len < 1.01, "facing not normalized: " + len);
        }

        [Fact]
        public void Fixture_Strict_RejectsUnknownProperty()
        {
            var json = LoadFixture().Replace("\"npcId\"", "\"npcIdX\"");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out var err));
            Assert.False(string.IsNullOrEmpty(err));
        }

        [Fact]
        public void Fixture_Strict_RejectsInvalidPhase()
        {
            var json = LoadFixture().Replace("\"phase\": 1", "\"phase\": 9");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out _));
        }

        [Fact]
        public void Fixture_Strict_RejectsNaN()
        {
            var json = LoadFixture().Replace("0.8660254", "NaN");
            Assert.False(EncounterSnapshotValidator.TryParse(json, out _, out _));
        }
    }
}
