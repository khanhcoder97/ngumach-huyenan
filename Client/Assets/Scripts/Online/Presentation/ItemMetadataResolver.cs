// ItemMetadataResolver — Pure C# catalog metadata resolver for player items.
// Rules:
//   - Read-only presentation metadata sourced from Item_Master_Catalog_vi.csv and Item_Rarity_Variant_Catalog_vi.csv.
//   - Never crashes on unknown template; returns valid fallback without raw "UNRESOLVED" text.
//   - Unknown templates never inherit known slots or class IDs.
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    public sealed class ItemMetadata
    {
        public string TemplateId { get; }
        public string DisplayName { get; }
        public string Category { get; }
        public string Slot { get; }
        public string ClassId { get; }
        public string Rarity { get; }
        public int RequiredLevel { get; }
        public string Description { get; }
        public string SourceRef { get; }

        public ItemMetadata(
            string templateId,
            string displayName,
            string category,
            string slot,
            string classId,
            string rarity,
            int requiredLevel,
            string description,
            string sourceRef = "docs/production/Item_Master_Catalog_vi.csv v1.0")
        {
            TemplateId = templateId ?? "";
            DisplayName = displayName ?? templateId;
            Category = category ?? "Vật phẩm";
            Slot = slot;
            ClassId = classId;
            Rarity = rarity ?? "Thường";
            RequiredLevel = requiredLevel;
            Description = description ?? "";
            SourceRef = sourceRef;
        }
    }

    public static class ItemMetadataResolver
    {
        private static readonly Dictionary<string, ItemMetadata> Catalog =
            new Dictionary<string, ItemMetadata>(StringComparer.OrdinalIgnoreCase);

        private static readonly Dictionary<string, (string prefix, string rarity)> RaritySuffixes =
            new Dictionary<string, (string, string)>(StringComparer.OrdinalIgnoreCase)
            {
                ["COMMON"]  = ("Thường ", "Thường"),
                ["REFINED"] = ("Tinh ", "Tinh"),
                ["SPIRIT"]  = ("Linh ", "Linh"),
                ["ARCANE"]  = ("Huyền ", "Huyền"),
                ["RELIC"]   = ("Cổ Vật ", "Cổ Vật")
            };

        static ItemMetadataResolver()
        {
            // Minh Kiếm T1 Set & Equipment
            Reg("EQ-MK-HAT-T1", "Nón Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_HAT", "CLASS_MINH_KIEM", "Thường", 1, "Mảnh set giáp Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-CHEST-T1", "Áo Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_CHEST", "CLASS_MINH_KIEM", "Thường", 1, "Mảnh set giáp Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-LEGS-T1", "Quần Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_LEGS", "CLASS_MINH_KIEM", "Thường", 1, "Mảnh set giáp Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-WEAPON-T1", "Kiếm Mưa Khởi Minh Kiếm", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_MINH_KIEM", "Thường", 1, "Kiếm khởi đầu phái Minh Kiếm");
            Reg("EQ-MK-GLOVES-T1", "Găng Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_GLOVES", "CLASS_MINH_KIEM", "Thường", 1, "Mảnh set giáp Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-BOOTS-T1", "Giày Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_BOOTS", "CLASS_MINH_KIEM", "Thường", 1, "Mảnh set giáp Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-NECK-T1", "Dây chuyền Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_NECK", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-RING_L-T1", "Nhẫn trái Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_RING_L", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-RING_R-T1", "Nhẫn phải Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_RING_R", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-PENDANT-T1", "Ngọc bội Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_PENDANT", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-CLOAK-T1", "Phi phong Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_CLOAK", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");
            Reg("EQ-MK-SEAL-T1", "Ấn hộ mệnh Mưa Khởi Minh Kiếm", "Trang bị / phụ kiện", "EQUIP_SEAL", "CLASS_MINH_KIEM", "Thường", 1, "Phụ kiện Mưa Khởi Minh Kiếm");

            // Weapons for other classes
            Reg("EQ-AD-WEAPON-T1", "Đao Mưa Khởi Ảnh Đao", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_ANH_DAO", "Thường", 1, "Đao khởi đầu phái Ảnh Đao");
            Reg("EQ-HB-WEAPON-T1", "Bút Mưa Khởi Huyền Bút", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_HUYEN_BUT", "Thường", 1, "Bút khởi đầu phái Huyền Bút");
            Reg("EQ-TC-WEAPON-T1", "Chùy Mưa Khởi Thạch Chùy", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_THACH_CHUY", "Thường", 1, "Chùy khởi đầu phái Thạch Chùy");
            Reg("EQ-LC-WEAPON-T1", "Cung Mưa Khởi Linh Cung", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_LINH_CUNG", "Thường", 1, "Cung khởi đầu phái Linh Cung");

            // Consumables & Materials
            Reg("POT-HP-01", "Dược Bến Mưa", "Dược phẩm", null, null, "Thường", 1, "Hồi 25% HP, hồi chiêu chia sẻ 8s");
            Reg("GEM-KIM-01", "Ngọc Kim", "Ngọc", null, null, "Thường", 1, "+1% chính xác, 1 socket");
            Reg("MAT-CORE-01", "Lõi Mạch", "Nguyên liệu", null, null, "Tinh", 1, "Vật liệu nâng cấp, khóa giao dịch");
            Reg("MAT-RELIC-01", "Cổ Linh Phách", "Nguyên liệu", null, null, "Cổ Vật", 61, "Nguyên liệu tuần cho Ấn Hộ Mệnh T5");
            Reg("MAT-GUARD-01", "Phù Bảo Hộ", "Phù chú", null, null, "Linh", 1, "Chất xúc tác +11..+15, khóa nhân vật");
            Reg("MAT-LOCK-01", "Phù Khóa", "Phù chú", null, null, "Thường", 1, "Bảo vệ khỏi phân giải, tiêu hao");

            // Quest package objectives
            Reg("OBJ_BM_PACKAGE_01", "Gói Hàng Bến Mưa 1", "Nhiệm vụ", null, null, "Thường", 1, "Gói hàng thất lạc tại Bến Mưa");
            Reg("OBJ_BM_PACKAGE_02", "Gói Hàng Bến Mưa 2", "Nhiệm vụ", null, null, "Thường", 1, "Gói hàng thất lạc tại Bến Mưa");
            Reg("OBJ_BM_PACKAGE_03", "Gói Hàng Bến Mưa 3", "Nhiệm vụ", null, null, "Thường", 1, "Gói hàng thất lạc tại Bến Mưa");
        }

        private static void Reg(string templateId, string name, string category, string slot, string classId, string rarity, int level, string desc)
        {
            Catalog[templateId] = new ItemMetadata(templateId, name, category, slot, classId, rarity, level, desc);
        }

        public static ItemMetadata Resolve(string templateId)
        {
            if (string.IsNullOrEmpty(templateId))
                return new ItemMetadata("", "Không tên", "Vật phẩm", null, null, "Thường", 1, "");

            if (Catalog.TryGetValue(templateId, out var meta))
                return meta;

            // Rarity variant lookup: <base-id>-R-<RARITY>
            int rIdx = templateId.LastIndexOf("-R-", StringComparison.OrdinalIgnoreCase);
            if (rIdx > 0)
            {
                string baseId = templateId.Substring(0, rIdx);
                string suffix = templateId.Substring(rIdx + 3);

                if (RaritySuffixes.TryGetValue(suffix, out var rInfo) && Catalog.TryGetValue(baseId, out var baseMeta))
                {
                    return new ItemMetadata(
                        templateId,
                        rInfo.prefix + baseMeta.DisplayName,
                        baseMeta.Category,
                        baseMeta.Slot,
                        baseMeta.ClassId,
                        rInfo.rarity,
                        baseMeta.RequiredLevel,
                        baseMeta.Description,
                        "docs/production/Item_Rarity_Variant_Catalog_vi.csv v1.0");
                }
            }

            // Clean fallback without UNRESOLVED (null slot and classId for unknown templates)
            return new ItemMetadata(templateId, templateId, "Vật phẩm", null, null, "Thường", 1, "Chưa có mô tả chi tiết");
        }
    }
}
