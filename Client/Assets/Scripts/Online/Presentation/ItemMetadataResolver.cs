// ItemMetadataResolver — Pure C# catalog metadata resolver for player items.
// Rules:
//   - Read-only presentation metadata sourced from Item_Master_Catalog_vi.csv.
//   - Never crashes on unknown template; returns valid fallback without raw "UNRESOLVED" text.
//   - Client does not forge or calculate custom combat stats.
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

            // Canonical common variants
            Reg("EQ-MK-CHEST-T1-R-COMMON", "Thường Áo Mưa Khởi Minh Kiếm", "Trang bị / giáp", "EQUIP_CHEST", "CLASS_MINH_KIEM", "Thường", 1, "Thường Áo Mưa Khởi, cấp 1");
            Reg("EQ-MK-WEAPON-T1-R-COMMON", "Thường Kiếm Mưa Khởi Minh Kiếm", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_MINH_KIEM", "Thường", 1, "Thường Kiếm Mưa Khởi, cấp 1");
            Reg("EQ-AD-WEAPON-T1-R-COMMON", "Thường Đao Mưa Khởi Ảnh Đao", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_ANH_DAO", "Thường", 1, "Thường Đao Mưa Khởi, cấp 1");
            Reg("EQ-HB-WEAPON-T1-R-COMMON", "Thường Bút Mưa Khởi Huyền Bút", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_HUYEN_BUT", "Thường", 1, "Thường Bút Mưa Khởi, cấp 1");
            Reg("EQ-TC-WEAPON-T1-R-COMMON", "Thường Chùy Mưa Khởi Thạch Chùy", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_THACH_CHUY", "Thường", 1, "Thường Chùy Mưa Khởi, cấp 1");
            Reg("EQ-LC-WEAPON-T1-R-COMMON", "Thường Cung Mưa Khởi Linh Cung", "Trang bị / vũ khí", "EQUIP_WEAPON", "CLASS_LINH_CUNG", "Thường", 1, "Thường Cung Mưa Khởi, cấp 1");

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

            // Prefix lookup fallback
            foreach (var kvp in Catalog)
            {
                if (templateId.StartsWith(kvp.Key, StringComparison.OrdinalIgnoreCase))
                    return new ItemMetadata(templateId, kvp.Value.DisplayName, kvp.Value.Category, kvp.Value.Slot, kvp.Value.ClassId, kvp.Value.Rarity, kvp.Value.RequiredLevel, kvp.Value.Description);
            }

            // Clean fallback without UNRESOLVED
            return new ItemMetadata(templateId, templateId, "Vật phẩm", null, null, "Thường", 1, "Chưa có mô tả chi tiết");
        }
    }
}
