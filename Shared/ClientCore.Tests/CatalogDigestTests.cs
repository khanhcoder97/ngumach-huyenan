using NguMach.Client.Presentation;
using System;
using System.IO;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class CatalogDigestTests
    {
        private static string CatalogPath => Path.Combine(
            AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "..", "..",
            "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json");

        private static string LoadText()
        {
            var candidates = new[]
            {
                Path.Combine("..", "..", "..", "..", "..", "Client", "Assets", "Resources", "PlayerUI", "ui_item_catalog.json"),
                @"D:\Project\NGUMACHHUYENAN-opencode-godot-core-20261103\Client\Assets\Resources\PlayerUI\ui_item_catalog.json",
            };
            foreach (var c in candidates) if (File.Exists(c)) return File.ReadAllText(c);
            throw new FileNotFoundException("catalog not found");
        }

        [Fact]
        public void Catalog_LoadsAndVerifiesDigest()
        {
            var text = LoadText();
            Assert.True(UiCatalogLoader.TryLoad(text, out var cat, out var err), err);
            Assert.NotNull(cat);
            Assert.True(cat.Count > 0);
            Assert.True(cat.VerifyDigest());
        }

        [Fact]
        public void Catalog_TamperedEntry_Fails()
        {
            var text = LoadText();
            Assert.True(UiCatalogLoader.TryLoad(text, out var cat, out _));
            var first = cat.Entries[0];
            int at = text.IndexOf("\"item_id\": \"" + first.ItemId + "\"", StringComparison.Ordinal);
            Assert.True(at >= 0);
            int dn = text.IndexOf("\"display_name\": \"", at, StringComparison.Ordinal);
            Assert.True(dn >= 0);
            int start = dn + "\"display_name\": \"".Length;
            int end = text.IndexOf('"', start);
            var tampered = text.Substring(0, start) + "TAMPERED" + text.Substring(end);
            Assert.False(UiCatalogLoader.TryLoad(tampered, out _, out var err));
            Assert.Contains("digest", err);
        }
    }
}
