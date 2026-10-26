# ĐẶC TẢ LÒ RÈN VÀ CHẾ TÁC — OVERLAY + LOGIC
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Phạm vi và nguyên tắc dữ liệu

Đây là đặc tả giao diện và luật tương tác cho NPC_LÒ_RÈN/NPC_BLACKSMITH, NPC_REPAIRER và bàn chế tác. Một overlay thống nhất có các chế độ: **Cường hóa, Chế tác, Khảm ngọc, Tinh luyện, Sửa chữa, Phân giải**. Chế độ mặc định là Chế tác nếu mở từ bản vẽ/recipe; mở từ trang bị đang chọn thì vào Cường hóa.

Các item/recipe hiện có là nguồn chuẩn trong `Item_Master_Catalog_vi.csv`, `Item_Rarity_Variant_Catalog_vi.csv`, `Item_Catalog_and_Set_Bible_vi.md` và Content Bible. Lò rèn không được tự tạo tên, giá, tỉ lệ, output hoặc nguồn nguyên liệu. Công thức/cường hóa có các giá trị đã khóa dưới đây; recipe khác phải có `recipeId`, input, output, điều kiện, fee và source rõ trước khi bật nút Rèn.

Quy tắc nền của game được giữ nguyên: 12 slot nhân vật; 5 phẩm chất **Thường, Tinh, Linh, Huyền, Cổ Vật**; level 1–100; +0…+15; 3 ngọc cùng cấp ghép thành cấp kế tiếp; tháo ngọc luôn trả viên; craft item equipment bị khóa theo lớp nếu item yêu cầu; vật phẩm khóa/quest không thể tiêu nhầm. Đây là đề xuất mới cho Ngũ Mạch, không phải bảng dữ liệu server trích từ KPAH.

### 2. Bố cục tổng và responsive

Overlay mở trên viewport phủ slate tối phẳng, không blur. Frame/icon/font pixel art theo `Pixel_Art_Production_Standard_vi.md`; point sampling và scale nguyên. Desktop dùng dialog centered 60/40: **trái 60%** là mode/tabs/filter/catalog; **phải 40%** là item inspector, preview kết quả và footer thao tác. Modal tối đa rộng 1180 CSS px, cao 86vh; nội dung từng cột cuộn độc lập, header/title và CTA giữ cố định.

| Thiết bị | Bố cục |
|---|---|
| PC 1920×1080 | 1160×760px tối đa; cột trái 696px, phải 464px; lề safe area 32px |
| PC cửa sổ nhỏ | 94vw × 92vh; cột trái/phải tối thiểu 1.25fr/1fr; dưới 900px chuyển một cột |
| Mobile ngang 1280×720–2400×1080 | 96vw × 94vh; header/tab cố định; hai tab nội dung `Danh sách` và `Xem/Rèn`; nút xác nhận sticky đáy |
| Tay cầm | cùng bố cục màn hình; focus ring vàng; trái/phải đổi mode/list/inspector; A xác nhận, B quay lại |

Khung Slate Ink-900 opacity 96%, vân gỗ gụ rất mờ, viền đồng 1.5px, góc 12px, shadow 0 12px 40px. Gold dùng cho focus/CTA; hoa văn góc không nằm dưới text. Control tối thiểu 48×48dp mobile, 40×40px PC. Rarity dùng đúng hình dạng/icon từ Item Bible: Thường vòng xám, Tinh tam giác lục, Linh thoi lam, Huyền hai vạch tím, Cổ Vật ấn vàng; không dùng bộ trắng/xanh/tím/vàng generic.

### 3. Header và điều hướng chế độ

Header trái hiển thị `LÒ RÈN` cùng map/NPC; phải có nút X, phím Esc/Back và trạng thái đồng bộ. Nếu avatar đang combat hoặc service không sẵn sàng, header hiện lý do và nút thao tác bị khóa.

Thanh mode: `Cường hóa | Chế tác | Khảm ngọc | Tinh luyện | Sửa chữa | Phân giải`. Tab mode khác với lọc danh mục item. Danh mục Chế tác gồm:

1. **Vũ khí** — chỉ hiện bản vẽ vũ khí đã mở; hiện catalog hiện tại chưa có blueprint vũ khí, nên tab báo `Chưa có bản vẽ chế tác vũ khí` và có nút xem nguồn item.
2. **Giáp & phụ kiện** — áo, nón, quần, găng, giày, dây chuyền, nhẫn, ngọc bội, phi phong, ấn hộ mệnh theo 12 slot.
3. **Ngọc & nguyên liệu** — recipe ghép ngọc, thuốc, sửa chữa, vật liệu Cổ Vật và công thức phụ trợ.
4. **Thú & mỹ phẩm** — thức ăn thú/cosmetic có recipe; không tạo stat cho mỹ phẩm. Game không có hệ cánh bay; không gắn nhãn “phi hành” cho thú cưỡi.

### 4. Cột trái — catalog và recipe tiles

Phía trên danh sách có search theo tên/ID, bộ lọc `Đã học`, `Có thể chế tác`, `Đủ nguyên liệu`, `Thiếu`, phẩm chất, cấp yêu cầu, lớp và slot. Nút sort: tên, tier, phẩm chất, gần đủ nguyên liệu, mới mở. Kết quả giữ lựa chọn khi chuyển sang inspector.

Grid desktop 3 cột, mobile 2 cột ở landscape rộng hoặc 1 cột ở viewport hẹp; item card vuông 110–144 CSS px PC/100–120dp mobile. Mỗi card có icon pixel-art (32–64px source, integer scale), rarity shape/frame, bitmap-font name, subline tier/lớp/slot, trạng thái recipe và hành động phụ:

- `Xem`: chỉ chọn card, không tiêu hao gì.
- `Nguồn`: mở drawer nguồn lấy recipe/nguyên liệu.
- `Rèn`: chọn card và đưa focus sang inspector; chưa gửi giao dịch.
- `Đã học`, `Chưa học`, `Thiếu nguyên liệu` là badge trạng thái, không thay thế tooltip lý do.

Recipe chưa học vẫn hiện mờ nếu lọc `Tất cả`, kèm nguồn mở và điều kiện. Item không có blueprint không được hiện nút Rèn; có thể mở trang item để xem nguồn loot/quest/market. Item Cổ Vật/quest không nằm trong grid craft nếu recipe không được định nghĩa rõ.

### 5. Cột phải — inspector và preview kết quả

Inspector giữ panel item được chọn. Header có icon 96px PC/80dp mobile, tên, itemId nhỏ khi bật chế độ data QA, phẩm chất, tier/level, slot, lớp, binding và trạng thái set. Frame icon dùng pixel palette accent theo rarity; Cổ Vật có thể có một sprite shimmer ngắn theo event, không shader glow và không chạy liên tục.

**Hai cột stat comparison:** `Hiện tại → Sau thao tác` với từng stat có giá trị, dấu +/− và nguồn. Khi craft đồ mới, cột hiện tại là slot tương ứng đang mặc, cột kết quả là item chế tác. Hiện set count trước/sau; nếu đổi món làm mất bonus 2/4 mảnh, cảnh báo dưới preview. Tooltip stat ghi cap, bucket PvE/PvP và dòng ẩn nếu đã giám định.

#### Điều kiện có thể thao tác

Requirement strip có state:
- Xanh/check: đủ cấp, lớp phù hợp, recipe đã học, nghề và map đã mở.
- Amber: thiếu vật liệu hoặc phí; giải thích số còn thiếu.
- Đỏ/khóa: level/lớp sai, durability/state không hợp lệ, item đang trade/equip/lock, đang combat hoặc recipe bị khóa theo quest.
- `Cảnh giới` không tự suy từ level; chỉ hiện nếu recipe/progression service trả realm requirement.

Requirement kiểm tra item và nhân vật riêng: `Cấp nhân vật`, `Môn phái`, `Cấp nghề Chế tác`, `Recipe unlock`, `Item level/tier`, `Slot`, `Binding/Trade state`, `Trạng thái khu vực`. Nút không khả dụng luôn có tooltip lý do.

### 6. Material checklist và nguồn nguyên liệu

Mỗi dòng hiển thị icon + tên + `đang có / cần`, stack binding và toggle chọn nguồn:

- `Túi nhân vật` bật mặc định.
- `Kho cá nhân` chỉ đọc/tiêu khi người chơi bật rõ; số trong kho bang không được đưa vào quote.
- Quest item, item đang niêm yết, đang giao dịch, đang mặc hoặc đã bảo vệ không được tính như vật liệu khả dụng.
- Khi đủ hiện check xanh và số màu sáng; thiếu hiện dấu X đỏ kèm `Thiếu 3`; không chỉ đổi màu chữ.
- Thay đổi túi/kho đẩy delta realtime. Nếu lượng vật liệu tụt dưới requirement, quote hết hạn và nút rèn disable trước khi gửi request.

Nút `Lấy ở đâu?` mở panel có map, node/quái/boss/quest/hoạt động/recipe, cấp vùng, thời gian mở và trạng thái người chơi. Market chỉ xuất hiện nếu material tradeable; link dẫn tới tìm kiếm item, không tự mua. Không có raffle/quay thưởng trong nguồn vật liệu; guild reward là nhiệm vụ/đổi token tuần. Source map ID khớp Map Atlas.

### 7. Luật cường hóa +0…+15

Chọn item từ slot mặc hoặc túi. Item hỏng ở 0 durability vẫn có thể rèn nếu rule server cho phép; item đang trade, escrow, locked, quest-bound, unique conflict hoặc người chơi đang combat thì không. Panel hiển thị cấp hiện tại, cấp đích, stat trước/sau và xác suất trước nút xác nhận.

**Tăng stat:** +1…+5 mỗi cấp +2% base weapon power/armor; +6…+10 mỗi cấp +1,5%; +11…+15 mỗi cấp +1%; tổng +27,5% tại +15. Không tăng set bonus, hidden effect, affix, gem value hoặc cosmetic.

Stat cuối = `round_half_up(baseStat × (1 + enhancementPercent))`; tính từ base đã áp rarity, không cộng dồn số nguyên đã làm tròn từng cấp. Cost của lần thử là cost theo cấp đích `n` = `ceil_to_10(tierBaseCost × 1.35^(n−1))`.

**Tỷ lệ thành công:** +1…+5: 100%; +6: 80%; +7: 70%; +8: 60%; +9: 50%; +10: 40%; +11: 35%; +12: 30%; +13: 25%; +14: 20%; +15: 15%. Thất bại không phá đồ, không giảm cấp; giữ nguyên stat và item instance. Kết quả thành công/fail do server trả.

**Đồng tại cấp +1 theo tier T1→T7:** 100 / 500 / 1.500 / 4.000 / 8.000 / 15.000 / 25.000. Cấp đích n dùng `ceil_to_10(baseCost × 1.35^(n−1))`; UI hiển thị số đã làm tròn đúng như server trước khi xác nhận.

| Tier | Vật liệu rèn chính |
|---|---|
| T1 | MAT-ORE-01 — Quặng Thô |
| T2 | MAT-ORE-02 — Quặng Kim Thanh Lạc |
| T3 | MAT-ORE-03 — Thạch Mạch Rừng |
| T4 | MAT-ORE-04 — Quặng Xỉ Hỏa |
| T5 | MAT-ORE-05 — Đá Trấn Sơn |
| T6 | MAT-SCALE-01 — Vảy Uyên |
| T7 | MAT-CORE-01 — Lõi Mạch |

Vật liệu mỗi lượt: +1…+5 cần 1 catalyst tier tương ứng; +6…+10 cần 2; +11…+15 cần 3 cộng **1 MAT-GUARD-01 Phù Bảo Hộ**. Mỗi lần thử +11…+15 tiêu 1 Phù Bảo Hộ kể cả thất bại. Tooltip nêu rõ đây là catalyst bắt buộc; fail vẫn không phá/giảm cấp.

**Confirm cường hóa:** trước lần đầu có thể bật `Xác nhận từng lượt`; từ +6 trở lên luôn hiện xác suất và vật liệu, từ +11 luôn confirm riêng. Auto-cường hóa chỉ nhận mục tiêu dừng +N, dừng khi đạt, fail, thiếu phí/vật liệu, item đổi, mất mạng, cảnh báo xác suất chưa đọc hoặc người chơi chạm Hủy. Không auto chạy khi chọn item Cổ Vật nếu không giữ xác nhận.

### 8. Luật chế tác và danh mục recipe launch

Crafting mặc định deterministic; không roll chất lượng ngầm. Recipe cấp output quality cụ thể hoặc cho chọn trong danh sách option, preview hiển thị đúng itemId, stats, class, level, binding và giá trị nguyên liệu. Tạo equipment 1 lần/giao dịch; batch tối đa 10 chỉ cho vật phẩm tiêu hao/recipe stackable. Hiện coin fee 0 nếu recipe không đặt phí; không tự suy giá từ rarity.

| Recipe ID | Điều kiện | Đầu vào | Đầu ra |
|---|---|---|---|
| RCP-POTION-01 | Chế tác bậc 1 | 3 MAT-HERB-01 + 1 MAT-WATER-01 | 2 POT-HP-01 Dược Bến Mưa |
| RCP-GEM-02 | Cấp nhân vật 1+, gem cùng mạch/cấp L1–L4 | 3 ngọc cùng mạch/cấp + 5 MAT-ORE-01 | 1 ngọc cùng mạch cấp kế tiếp; chắc chắn, trần L5 |
| RCP-ARMOR-10 | Cấp 10+, chọn lớp phù hợp | 8 MAT-ORE-01 + 4 MAT-WOOD-01 + 1 MAT-SOUL-01 | 1 áo T1; chọn lớp và chất lượng Thường/Tinh trước khi rèn |
| RCP-REPAIR-01 | Chế tác bậc 1 | 2 MAT-ORE-01 + 1 MAT-WOOD-01 | 1 KIT-REPAIR-01 Bộ Vá Giáp (sửa 25 durability) |
| RCP-SOUL-01 | Cấp 61+, bậc nghề 5; quota tuần còn | 5 MAT-SOUL-02 + 1 MAT-CORE-01 | 1 MAT-RELIC-01 Cổ Linh Phách; tối đa 3 lần/tuần |
| RCP-FOOD-ATK | Chế tác bậc phù hợp | 3 MAT-HERB-03 + 1 MAT-ASH-01 | 1 FOOD-ATK-01 Bánh Mạch Hỏa |
| RCP-FOOD-DEF | Chế tác bậc phù hợp | 2 MAT-HERB-02 + 1 MAT-ORE-05 | 1 FOOD-DEF-01 Canh Rễ Đá |
| RCP-PET-FEED | Cấp 20+, thú đã mở | 1 MAT-SEED-01 + 1 MAT-FISH-01 | 1 PET-FEED-01 Hạt Linh Thú |
| RCP-CLOAK-31 | Cấp 31+, nghề Chế tác bậc 3 | 5 MAT-WOOD-02 + 3 MAT-LEATHER-01 + 1 MAT-SOUL-01 | 1 Phi Phong Rễ Nhớ T3 Thường, chọn lớp |
| RCP-SEAL-61 | Cấp 61+, nghề Chế tác bậc 5, lớp hợp lệ | 6 MAT-ORE-05 + 3 MAT-CLOTH-01 + 2 MAT-RELIC-01 + 1 MAT-CORE-01 | 1 Ấn Hộ Mệnh T5 Tinh theo lớp |

Nếu recipe có `coinCost`/`professionLevel` khác bảng baseline, data version mới phải cập nhật cả catalog và spec. Nếu recipe chưa đủ input/output/quality/level, nó vẫn hiện `Chưa khả dụng` trong QA catalog và không gọi API craft.

### 9. Khảm ngọc, tinh luyện, sửa chữa, phân giải

**Khảm ngọc:** inspector hiển thị socket capacity hiện tại và các ô trống. Chỉ lắp viên tương thích; xác nhận trước khi bind viên vào item. Lắp miễn phí tại hub; tháo ngọc trả lại viên 100%, không giảm stat hay phẩm chất. Không tự mở socket không tồn tại trong item instance. Ghép dùng `RCP-GEM-02`: 3 viên cùng mạch/cùng cấp (L1–L4) + 5 MAT-ORE-01 → 1 viên cấp kế tiếp, chắc chắn; L5 là trần và không có nút ghép tiếp.

**Tinh luyện (đúc lại affix):** chỉ gear Tinh trở lên có affix ngẫu nhiên. Người chơi chọn đúng một dòng phụ để đúc lại; dòng khác, phẩm chất, socket, set, dòng ẩn, cường hóa và durability giữ nguyên. Stat mới lấy từ pool hợp slot/tier trong Item Bible, không trùng stat khác trên món; trị số được roll trong range và server trả kết quả. Preview cho thấy toàn bộ pool có thể ra, min–max, tỷ lệ đồng đều giữa các lựa chọn hợp lệ và chi phí, nhưng không giả lập trước kết quả. Mỗi lượt tốn 1 MAT-SEAL-01, 1 catalyst đúng tier (bảng T1–T7 ở mục 7) và phí Đồng theo tier: 500 / 2.500 / 7.500 / 20.000 / 40.000 / 75.000 / 125.000. Gear Thường không có affix nên mode này disable. Hidden effect/set bonus không thể đúc lại.

**Sửa chữa:** có thể sửa tại NPC hoặc dùng KIT-REPAIR-01 ngoài combat. Kit cộng 25 durability, không vượt 100; panel hiển thị durability trước/sau. Tại NPC, phí = `ceil_to_10(tierBaseCost × (100 − durability hiện tại) / 100)`, trong đó `tierBaseCost` là bảng cường hóa +1 T1–T7; phí tối thiểu 10 Đồng nếu durability dưới 100. Ở durability 0 item giảm 10% tổng chỉ số đến khi sửa; ngoài mốc 0 không có phạt. Sửa không đổi phẩm chất/affix/socket/set.

**Phân giải:** hiện vật liệu đầu ra cố định theo item trước xác nhận. Gear không quest-bound hoặc event-protected trả 1 catalyst đúng tier + 1 MAT-SEAL-01; output thừa hưởng binding của gear. Catalyst: T1–T5 dùng MAT-ORE-01…05 tương ứng, T6 MAT-SCALE-01, T7 MAT-CORE-01. Item khác chỉ phân giải được nếu có `salvageTableId`; thiếu bảng thì nút khóa và không tự ước lượng. Bỏ qua item đang mặc, locked, quest, market escrow hoặc protected. MAT-LOCK-01 Phù Khóa là dấu bảo vệ chống phân giải, tiêu hao một lần khi áp dụng; chỉ bỏ dấu qua thao tác xác nhận riêng. Gear Huyền/Cổ Vật cần xác nhận nhập tên hoặc giữ nút 0,8s; bulk salvage không nhận Huyền/Cổ Vật.

### 10. Nguồn vật liệu và quyền dùng kho

Recipe inspector tra `source_map`, `source_rule`, quest unlock, loot table, node/zone và tradeability. Ví dụ material vùng: quặng/wood/herb từ node; MAT-SOUL-01/02 từ tinh anh/boss theo vùng; MAT-SEAL-01 từ nhiệm vụ/node để đúc affix; MAT-RELIC-01 từ RCP-SOUL-01 theo tuần; MAT-GUARD-01 từ weekly challenge/guild exchange/elite cache; MAT-LOCK-01 từ NPC_BLACKSMITH/quest.

Kho cá nhân có opt-in riêng trước khi ingredient count tăng. Kho bang, thư, listing chợ, item đang trao đổi và vật phẩm quest không bao giờ tự bị tiêu. Nếu recipe cần item khóa nhân vật thì panel nêu rõ; nếu người chơi chọn item tradeable, hiện icon binding khi output.

### 11. Giao dịch server và lỗi

Luồng craft/upgrade:
1. Client chọn item/recipe; inspector lấy snapshot inventory revision và server quote.
2. Preflight trả `eligible`, `missingMaterials[]`, `currencyCost`, `successRate`, `outputPreview`, `expiresAt`.
3. Người chơi xác nhận; client gửi `requestId`, `recipeId/operation`, `itemInstanceId`, `inventoryRevision`, `selectedMaterials[]`, `selectedOutput`.
4. Server lock item/material; validate số lượng, binding, cooldown, quota, level/profession, zone, combat state và quote expiry.
5. Transaction atomic tiêu nguyên liệu/phí và ghi output/kết quả; idempotency theo requestId. Client chỉ phát animation thành công sau ACK.
6. Push inventory delta sang túi, kho, forge inspector và party loot state; đóng/giữ modal theo lựa chọn.

Lỗi: `QuoteExpired` → tải lại counts/fee; `MaterialChanged` → cập nhật dòng thiếu; `Ineligible` → nêu lý do; `AlreadyProcessed` → hiển thị kết quả cũ; `NetworkUnknown` → giữ pending request và tra kết quả theo ID, không gửi giao dịch mới; `InventoryFull` → chặn trước craft hoặc chuyển output vào mailbox chỉ khi item policy cho phép. Không tự tiêu phí lần hai.

### 12. Mẫu dữ liệu inspector

```json
{
  "operation": "upgrade",
  "itemInstanceId": "inst-8842",
  "itemId": "EQ-MK-WEAPON-T5",
  "rarity": "Thường",
  "currentEnhancement": 10,
  "targetEnhancement": 11,
  "successRate": 0.35,
  "failureRule": "keep_item_and_level",
  "currencyCost": 160860,
  "materials": [
    {"itemId":"MAT-ORE-05","required":3,"inventory":4,"bank":2,"consumeFromBank":false},
    {"itemId":"MAT-GUARD-01","required":1,"inventory":1,"bank":0,"consumeFromBank":false}
  ],
  "preview": {"weaponPowerBefore":560,"weaponPowerAfterSuccess":664,"setBonusChanged":false},
  "inventoryRevision": 192,
  "quoteExpiresAt": "server timestamp"
}
```

Mẫu số liệu chỉ minh họa cấu trúc; giá/tỉ lệ/output thực lấy từ server config versioned. UI tự format localization và không tính lại damage/upgrade từ text.

### 13. Hiệu ứng, accessibility và performance

- Thành công: vòng sáng đồng 0,4s quanh item, âm búa kim loại nhẹ, toast item/cấp; thất bại +6..+15: tiếng nảy trầm, thông báo rõ `Không thành công — trang bị không đổi`.
- Không dùng màn trắng, lửa che item, camera shake mạnh hoặc âm thanh bắt buộc; LowFX tắt hạt phụ nhưng giữ kết quả, tỷ lệ và warning.
- Chữ 15–18px desktop, 14–16sp mobile; số vật liệu tabular; colorblind state có icon/check/X và pattern.
- Panel material source có thể đọc qua screen reader; focus không nhảy khi realtime count cập nhật.
- Không chạy animation lặp vô hạn; danh sách 60fps scroll, icon atlas cache, material updates theo event.

### 14. Checklist bàn giao

- Mockup 1920×1080, 1366×768, 1280×720 landscape, inspector đủ/thiếu vật liệu, cấp không đủ, recipe chưa học, quote hết hạn, success/fail.
- Card rarity dùng đúng 5 phẩm chất của Item Bible; test bộ 2/4 mảnh đổi bonus trong preview.
- Rèn T1–T7 hiển thị đúng catalyst, Đồng, tỷ lệ và cost rounding; +11 luôn yêu cầu MAT-GUARD-01.
- Tất cả recipe ID trong bảng resolve thành output/itemId; input không trùng hoặc thiếu; batch chỉ hiện với recipe stackable.
- Server transaction atomic/idempotent; mất kết nối sau commit không mất item và không tiêu hai lần.
- Có keyboard, touch, controller, safe area, LowFX, text scale, xác nhận item quý và trạng thái server offline.

### 15. Tài liệu liên quan

- Catalog/balance/cường hóa/set: `Item_Catalog_and_Set_Bible_vi.md`.
- Item schema/túi/giao dịch/craft: `Character_Equipment_Inventory_Spec_vi.md`.
- NPC/map/source materials: `Map_Production_Atlas_vi.md`, `Art_Entity_Weather_UI_Visual_Bible_vi.md`.
- UI tổng thể: `UI_UX_Spec_vi.md`; lò rèn mở từ `NPC_BLACKSMITH` và `NPC_FORGE_MASTER` theo map.
