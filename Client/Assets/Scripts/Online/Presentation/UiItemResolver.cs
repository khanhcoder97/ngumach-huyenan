// OPC-14 B — Catalog-backed item metadata resolver (pure C#, no Unity dep).
// Uses UiCatalogLoader's typed catalog as the single source of truth when loaded;
// falls back to the embedded subset only when no catalog is loaded (backward compat).
// Unknown templates never inherit known slots/class IDs; missing fields stay empty
// (no fake 0 / no UNRESOLVED leak). Base/variant (-R-) resolution supported.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 22, OPC-14 B).

using System;

namespace NguMach.Client.Presentation
{
    public static class UiItemResolver
    {
        private static UiCatalog _catalog;

        /// <summary>Set the loaded catalog (from UiCatalogLoader). Pass null to clear.</summary>
        public static void SetCatalog(UiCatalog catalog) { _catalog = catalog; }

        public static UiCatalog CurrentCatalog => _catalog;

        public static ItemMetadata Resolve(string templateId)
            => ResolveWith(_catalog, templateId);

        /// <summary>
        /// OPC-14 O1: explicit catalog resolution so a session/document can own its own
        /// catalog instead of the process-wide ambient one. Null catalog falls back to the
        /// embedded subset only (never a second live catalog).
        /// </summary>
        public static ItemMetadata ResolveWith(UiCatalog catalog, string templateId)
        {
            if (string.IsNullOrEmpty(templateId))
                return new ItemMetadata("", "Không tên", "Vật phẩm", null, null, null, "Thường", null, 1, "");

            // 1. Loaded catalog path (preferred when present).
            if (catalog != null)
            {
                var entry = catalog.Find(templateId);
                if (entry == null)
                {
                    // Variant lookup: <base-id>-R-<RARITY>
                    int rIdx = templateId.LastIndexOf("-R-", StringComparison.OrdinalIgnoreCase);
                    if (rIdx > 0)
                    {
                        string baseId = templateId.Substring(0, rIdx);
                        string suffix = templateId.Substring(rIdx + 3);
                        var baseEntry = catalog.Find(baseId);
                        if (baseEntry != null)
                        {
                            string rarity = SuffixToRarity(suffix);
                            string prefix = SuffixToPrefix(suffix);
                            return FromEntry(templateId, baseEntry, rarityOverride: rarity, namePrefix: prefix);
                        }
                    }
                    // Unknown template: clean fallback, no fake fields, no slot/class inheritance.
                    return new ItemMetadata(templateId, templateId, "Vật phẩm", null, null, null, "Thường", null, 0, "Chưa có mô tả chi tiết",
                        "ui_item_catalog.json (unknown template)");
                }
                return FromEntry(templateId, entry, null, null);
            }

            // 2. Fallback: embedded subset (backward compat when no catalog loaded).
            return ItemMetadataResolver.Resolve(templateId);
        }

        private static ItemMetadata FromEntry(string templateId, UiCatalogEntry e, string rarityOverride, string namePrefix)
        {
            string rarity = !string.IsNullOrEmpty(rarityOverride) ? rarityOverride : (e.RarityPool ?? "Thường");
            // rarity_pool may be "Thường|Tinh|..." (base template) — take first if multi.
            if (rarity != null && rarity.Contains("|"))
            {
                var parts = rarity.Split(new[] { '|' }, StringSplitOptions.RemoveEmptyEntries);
                if (parts.Length > 0) rarity = parts[0].Trim();
            }
            string name = e.DisplayName ?? templateId;
            if (!string.IsNullOrEmpty(namePrefix)) name = namePrefix + name;
            int level = e.RequiredLevel;
            string sourceRef = (e.Source != null)
                ? (e.Source.File + " row " + e.Source.Row)
                : "ui_item_catalog.json";
            return new ItemMetadata(
                templateId,
                name,
                e.Category,
                e.Slot,
                e.ClassId,
                e.Element,
                rarity,
                e.RarityPool,
                level,
                e.Description,
                sourceRef,
                e.WeaponPower, e.Armor, e.PrimaryStat, e.PrimaryValue,
                e.SecondaryStat, e.SecondaryValue, e.AffixRule, e.SocketRule,
                e.SetId, e.SetName, e.SetBonus2, e.SetBonus4,
                e.HiddenEffectId, e.HiddenEffectUnlock, e.HiddenEffect,
                e.StackLimit, e.Durability, e.Binding, e.Tradeable,
                e.SourceMap, e.SourceRule);
        }

        private static string SuffixToRarity(string suffix)
        {
            if (string.IsNullOrEmpty(suffix)) return null;
            switch (suffix.ToUpperInvariant())
            {
                case "COMMON": return "Thường";
                case "REFINED": return "Tinh";
                case "SPIRIT": return "Linh";
                case "ARCANE": return "Huyền";
                case "RELIC": return "Cổ Vật";
            }
            return suffix;
        }

        private static string SuffixToPrefix(string suffix)
        {
            if (string.IsNullOrEmpty(suffix)) return null;
            switch (suffix.ToUpperInvariant())
            {
                case "COMMON": return "Thường ";
                case "REFINED": return "Tinh ";
                case "SPIRIT": return "Linh ";
                case "ARCANE": return "Huyền ";
                case "RELIC": return "Cổ Vật ";
            }
            return "";
        }
    }

    /// <summary>
    /// OPC-14 O1: per-session/document resolver. Panels built for one UIDocument/session
    /// resolve against exactly the catalog loaded for that session (no process-wide bleed
    /// when two documents or a rebind are alive).
    /// </summary>
    public sealed class UiItemResolverSession
    {
        private readonly UiCatalog _catalog;
        public UiItemResolverSession(UiCatalog catalog) { _catalog = catalog; }
        public UiCatalog Catalog => _catalog;
        public ItemMetadata Resolve(string templateId) => UiItemResolver.ResolveWith(_catalog, templateId);
    }
}
