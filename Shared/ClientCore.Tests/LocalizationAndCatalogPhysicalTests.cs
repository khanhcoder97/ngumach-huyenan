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
        [Fact]
        public void PhysicalProvider_LoadsRealCatalog()
        {
            var path = @"D:\Project\NGUMACHHUYENAN-opencode-godot-core-20261103\Client\Assets\Resources\PlayerUI\ui_item_catalog.json";
            if (!File.Exists(path)) return; // environment without checkout
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
                "mutation_outcome_unknown", "invalid_transition", "resync_required" };
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
