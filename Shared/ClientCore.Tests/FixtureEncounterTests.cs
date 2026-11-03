using System;
using System.IO;
using Newtonsoft.Json;
using NguMach.Client.Core.Encounter;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class FixtureEncounterTests
    {
        private static string FixturePath => Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "Fixtures", "encounter_v1.json");

        private static string LoadFixture()
        {
            // Try a few relative locations.
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
            var snap = JsonConvert.DeserializeObject<EncounterSnapshot>(json);
            Assert.NotNull(snap);
            Assert.Equal("enc-fixture-001", snap.EncounterId);
            Assert.Equal("Telegraph", snap.Phase);
            Assert.Equal(1200, snap.Hp);
            Assert.NotNull(snap.ActiveMove);
            Assert.Equal("cast-fixture-001", snap.ActiveMove.CastId);
            Assert.NotNull(snap.ActiveMove.Shape);
            Assert.True(MoveShapeValidator.IsValid(snap.ActiveMove.Shape, out var reason), reason);
        }

        [Fact]
        public void Fixture_ViewAppliesAndTracksCast()
        {
            var json = LoadFixture();
            var snap = JsonConvert.DeserializeObject<EncounterSnapshot>(json);
            var view = new EncounterView();
            view.Apply(snap);
            Assert.True(view.HasSnapshot);
            Assert.True(view.IsTelegraphActive);
            Assert.Equal("cast-fixture-001", view.LastCastId);
            Assert.False(view.IsNewCast("cast-fixture-001"));
            Assert.True(view.IsNewCast("cast-other"));
        }

        [Fact]
        public void Fixture_ShapeFacing_NormalizedWithinTolerance()
        {
            var json = LoadFixture();
            var snap = JsonConvert.DeserializeObject<EncounterSnapshot>(json);
            var sh = snap.ActiveMove.Shape;
            double len = Math.Sqrt(sh.FacingX * sh.FacingX + sh.FacingY * sh.FacingY);
            Assert.True(len > 0.99 && len < 1.01, "facing not normalized: " + len);
        }
    }
}
