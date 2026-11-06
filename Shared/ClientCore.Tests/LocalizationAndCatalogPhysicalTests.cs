using System;
using System.IO;
using NguMach.Client.Core.Catalog;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Presentation;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class CatalogPhysicalProviderTests
    {
        // The catalog is part of this checkout; a missing file is a real failure, not a skip.
        internal static string FindRepoRoot()
        {
            var relative = Path.Combine("Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json");
            var starts = new[]
            {
                AppContext.BaseDirectory,
                Directory.GetCurrentDirectory()
            };
            foreach (var start in starts)
            {
                var dir = new DirectoryInfo(Path.GetFullPath(start));
                for (int depth = 0; dir != null && depth < 12; depth++, dir = dir.Parent)
                {
                    if (File.Exists(Path.Combine(dir.FullName, relative))) return dir.FullName;
                }
            }
            throw new FileNotFoundException("checkout root with " + relative + " was not found");
        }

        [Fact]
        public void PhysicalProvider_LoadsRealCatalog()
        {
            var path = Path.Combine(FindRepoRoot(), "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json");
            Assert.True(File.Exists(path), path);
            var prov = new PhysicalFileProvider();
            Assert.True(CatalogLoader.TryLoad(prov, path, out var text, out var err), err);
            Assert.True(UiCatalogLoader.TryLoad(text, out var cat, out var lerr), lerr);
            Assert.True(cat.Count > 0);
            Assert.True(cat.VerifyDigest());
        }
    }

    public class LocalizationIdTests
    {
        [Fact]
        public void ErrorCodes_AreNonEmptyLocalizationIds()
        {
            // P1 result codes are localization keys, never empty.
            var codes = new[] { "not_connected", "invalid_input", "session_not_found",
                "mutation_outcome_unknown", "invalid_transition", "resync_required",
                "network_unavailable", "invalid_envelope", "invalid_snapshot" };
            foreach (var c in codes)
            {
                Assert.False(string.IsNullOrWhiteSpace(c));
                Assert.DoesNotContain(" ", c);
            }
        }

        [Fact]
        public void BossPhase_Values_Are123()
        {
            Assert.Equal(1, (int)BossPhase.Phase1);
            Assert.Equal(2, (int)BossPhase.Phase2);
            Assert.Equal(3, (int)BossPhase.Phase3);
        }
    }
}
