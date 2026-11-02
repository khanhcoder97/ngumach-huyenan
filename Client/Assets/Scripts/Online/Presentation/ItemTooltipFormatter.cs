// OPC-13 Package B — Bag/character tooltip metadata formatter (pure C#).
// Composes the player-facing tooltip line set from ItemMetadataResolver's
// catalog-backed metadata — no placeholder copy, no second catalog source.
// Unknown templates fall back cleanly (no raw "UNRESOLVED" text ever leaks).
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 20).

using System;
using System.Text;

namespace NguMach.Client.Presentation
{
    public static class ItemTooltipFormatter
    {
        /// <summary>
        /// Full detail tooltip for a bag/equipped slot: catalog display name, rarity,
        /// category, required level, stack/durability and the catalog description,
        /// ending with the catalog source reference for provenance.
        /// </summary>
        public static string Format(ItemSlotView item, ItemMetadata meta)
        {
            if (item == null) throw new ArgumentNullException(nameof(item));
            var m = meta ?? new ItemMetadata(
                item.TemplateId, item.DisplayName, category: null, slot: null, classId: null,
                rarity: null, requiredLevel: 1, description: null);

            var sb = new StringBuilder();
            sb.Append("Tên: ").AppendLine(m.DisplayName);
            sb.Append("Phẩm chất: ").AppendLine(m.Rarity);
            sb.Append("Loại: ").AppendLine(m.Category);
            sb.Append("Cấp yêu cầu: ").AppendLine(m.RequiredLevel.ToString());
            if (item.Stack > 1) sb.Append("Số lượng: ×").AppendLine(item.Stack.ToString());
            sb.Append("Độ bền: ").Append(item.Durability).AppendLine("/100");
            sb.Append("Phiên bản: v").AppendLine(item.Version.ToString());

            // OPC-14 O1: render the catalog's extended fields (never invented) so templates
            // outside the embedded subset get the same detail level as the subset.
            AppendIf(sb, "Công vũ khí", m.WeaponPower);
            AppendIf(sb, "Giáp", m.Armor);
            AppendStat(sb, "Chỉ số chính", m.PrimaryStat, m.PrimaryValue);
            AppendStat(sb, "Chỉ số phụ", m.SecondaryStat, m.SecondaryValue);
            if (!string.IsNullOrEmpty(m.SetName) || !string.IsNullOrEmpty(m.SetId))
                sb.Append("Bộ: ").AppendLine(string.IsNullOrEmpty(m.SetName) ? m.SetId : m.SetName);
            AppendIf(sb, "Hiệu ứng bộ 2", m.SetBonus2);
            AppendIf(sb, "Hiệu ứng bộ 4", m.SetBonus4);
            AppendIf(sb, "Hiệu ứng ẩn", m.HiddenEffect);
            AppendIf(sb, "Khóa", m.Binding);
            AppendIf(sb, "Giao dịch", m.Tradeable);
            AppendIf(sb, "Nguồn rơi", m.SourceMap);
            AppendIf(sb, "Quy tắc nguồn", m.SourceRule);

            if (!string.IsNullOrEmpty(m.Description)) sb.AppendLine(m.Description);
            sb.Append("Nguồn: ").Append(m.SourceRef);
            return sb.ToString();
        }

        private static void AppendIf(StringBuilder sb, string label, string value)
        {
            if (!string.IsNullOrEmpty(value)) sb.Append(label).Append(": ").AppendLine(value);
        }

        private static void AppendStat(StringBuilder sb, string label, string stat, string value)
        {
            if (string.IsNullOrEmpty(stat)) return;
            sb.Append(label).Append(": ").Append(stat);
            if (!string.IsNullOrEmpty(value)) sb.Append(' ').Append(value);
            sb.AppendLine();
        }

        /// <summary>
        /// Slot button two-line label for the bag: catalog display name (rarity-aware)
        /// with a stack suffix when stacked. Unknown templates keep their raw template
        /// id as display name — never a forged in-game name.
        /// </summary>
        public static string SlotLabel(ItemSlotView item, ItemMetadata meta)
        {
            if (item == null) return "";
            var name = meta != null ? meta.DisplayName : item.TemplateId;
            return item.Stack > 1 ? name + " ×" + item.Stack : name;
        }
    }
}
