# QOD-24 — Đối chiếu lò rèn / chế tác (work order 29 Q5, phần chưa đọc)

Ngày: 2026-11-07. Phạm vi: đọc lần đầu `Forge_Crafting_Overlay_Spec_vi.md` và các row
`RECIPE` của `Loot_Recipe_Reward_Production_Data_vi.csv` dưới góc độ server; không mở
route, không đổi wire/gate/schema đóng băng, không sửa `docs/production/**`.

## 1. Trạng thái runtime đo được

- `Server/Health/Gameplay/Combat/LootRecipe.cs` chỉ nạp nhóm `LOOT_ENTRY` (57 sources /
  184 entries). Không có craft service, không có route craft/quote/preflight.
- Trước delta này, `Implementation/Tools/build_loot_recipe.py` lọc `LOOT_ENTRY` và
  **bỏ silently 7 row RECIPE** (CSV dòng 174–180); khối `unsupported` của bundle chỉ
  ghi `mobCoinBand` và `bossLoot`. Không file nào trong `Implementation/` hay
  `Server/` nhắc `RCP_CRAFT*`/`RCP-FOOD*`/`RCP-ARMOR*` trước báo cáo này.
- Delta data-only: builder đọc cả row RECIPE, không export vào sources, nhưng ghi
  `unsupported.craftRecipes = {status: PRESENT_IN_SOURCE_NOT_EXPORTED, reason:
  NO_CRAFT_SERVICE; FORGE_SPEC_BASELINE_CONFLICT_UNRESOLVED, count, entryIds[]}` —
  count/ids suy từ CSV, không gõ tay. Loader không đọc `unsupported` nên hành vi
  runtime không đổi. `bossLoot: BOSSDATA_BLOCKED_UNTIL_QOD_19` giữ nguyên chuỗi cũ
  dù encounter QOD-19 đã ship; đây là nhãn cũ, không phải blocker hiện tại (blocker
  thật là coin band + review) — ghi nhận, không sửa semantic trong lượt này.

## 2. Mâu thuẫn spec §8 ↔ CSV RECIPE (chưa nguồn nào được quyền ghi đè nguồn nào)

`Forge_Crafting_Overlay_Spec_vi.md:107–118` khóa bảng baseline 10 recipe;
CSV dòng 174–180 có 7 row RECIPE. Hai bộ không join được bằng id:

| Cặp | Spec §8 | CSV RECIPE |
| --- | --- | --- |
| FOOD-ATK | `RCP-FOOD-ATK` (dòng 114): 3 MAT-HERB-03 + 1 MAT-ASH-01 → **1** FOOD-ATK-01; điều kiện "Chế tác bậc phù hợp"; không phí | `RCP_CRAFT_FOOD_ATK` (dòng 179): 2 MAT-FISH-01 + 1 MAT-HERB-01 → **2** FOOD-ATK-01; `level >= 5; recipe unlock; atomic revalidation`; COIN 150; craft 4s; success 10000 |
| FOOD-DEF | `RCP-FOOD-DEF` (dòng 115): 2 MAT-HERB-02 + 1 MAT-ORE-05 → **1** FOOD-DEF-01; cùng điều kiện nghề | `RCP_CRAFT_FOOD_DEF` (dòng 180): 1 MAT-FISH-01 + 2 MAT-HERB-01 → **2** FOOD-DEF-01; level >= 5; COIN 150; 4s |
| Giáp/vũ khí T1 | `RCP-ARMOR-10` (dòng 111): 8 MAT-ORE-01 + 4 MAT-WOOD-01 + 1 **MAT-SOUL-01** → 1 **áo** T1, chọn lớp + chất lượng Thường/Tinh; cấp 10+; không phí | 5 row `RCP_CRAFT_{MK,AD,HB,TC,LC}_WEAPON_T1` (dòng 174–178): 8–10 ORE/WOOD + 4 LEATHER/WATER/HERB + 1 **MAT-SEAL-01** → **EQ-*-WEAPON-T1**; level >= 10; COIN 150; 4s |

Spec chỉ có mà CSV không có (8): `RCP-POTION-01`, `RCP-GEM-02`, `RCP-ARMOR-10`,
`RCP-REPAIR-01`, `RCP-SOUL-01`, `RCP-PET-FEED`, `RCP-CLOAK-31`, `RCP-SEAL-61`.
CSV chỉ có mà spec không có (5): năm recipe vũ khí theo lớp. Hai row food tồn tại ở
cả hai nhưng khác id/input/output-quantity nên là **cặp mâu thuẫn**, không phải match.

Chính spec §8 dòng 120 yêu cầu: recipe có `coinCost`/`professionLevel` khác baseline
thì "data version mới phải cập nhật cả catalog và spec" — hiện hai bên lệch nhau ở
phí (150 vs không phí), điều kiện (level nhân vật vs bậc nghề), input và số lượng.
§8 dòng 105 cũng chốt "Hiện coin fee 0 nếu recipe không đặt phí; không tự suy giá từ
rarity" — server không được tự chọn bên nào khi chưa có quyết định.

## 3. Cross-check với Item_Master_Catalog (đo bằng script, không ước lượng)

Cả 7 recipe: mọi input và output đều resolve trong `Item_Master_Catalog_vi.csv`
(0 missing). Ba lệch provenance/level đáng ghi:

- `FOOD-ATK-01`: item `required_level=10`, `source_map=MAP_SA_HOA`, `source_rule=
  MAP_SA_HOA|craft`; recipe mở qua `SQ-BM-05` (Bến Mưa) với `level >= 5`.
  `FOOD-DEF-01`: `required_level=10`, `source_map=MAP_LAM_TRIEU`; cùng recipe
  SQ-BM-05 level >= 5. Quest `SQ-BM-05` (Quest_Dialogue CSV dòng 124–126) nói rõ
  "mở công thức thức ăn" — tức chủ ý thiết kế là mở công thức sớm ở Bến Mưa,
  nhưng item gốc lại gắn map sau này và level dùng 10. Cần owner chốt: craft sớm
  được nhưng chưa dùng được, hay sai source_map/level?
- Năm vũ khí T1: item `required_level=1` nhưng recipe đòi `level >= 10` — không
  nhất thiết mâu thuẫn (điều kiện craft khác điều kiện trang bị), ghi nhận để
  owner xác nhận chủ ý.
- MAT-SEAL-01 (CSV) vs MAT-SOUL-01 (spec) cho cùng vai trò vật liệu thứ ba của
  đồ T1: hai item khác nhau trong catalog, không phải alias.

## 4. Phần spec chưa có bất kỳ runtime nào (không chỉ recipe)

§7 cường hóa +0…+15 (stat %, cost `ceil_to_10(base×1.35^(n−1))`, success 100→15%,
MAT-GUARD-01 từ +11), §9 khảm ngọc/tinh luyện/sửa chữa/phân giải, §11 luồng
quote/preflight/atomic transaction — không service, không route, không schema wire.
"Cấp nghề Chế tác" (profession level) không có bảng dữ liệu production nào;
không được suy từ level nhân vật (spec §5 dòng 61 cấm suy Cảnh giới từ level).
Tất cả đều đủ nguồn để packet nhưng chưa được duyệt implement; báo cáo này không mở gate.

## 5. Câu hỏi owner (trả lời trước khi viết schema/handler)

1. Nguồn chuẩn cho craft recipe là CSV RECIPE hay spec §8 baseline? Với hai row
   food: chọn id nào, input nào, output 1 hay 2, phí 0 hay 150, điều kiện level 5
   hay bậc nghề? Với đồ T1: áo chọn lớp/chất lượng (spec) hay vũ khí theo lớp (CSV)?
2. Tám recipe spec-only có được đưa vào CSV không, hay năm recipe CSV-only phải
   vào spec? Ai sở hữu bảng profession level?
3. FOOD-ATK/DEF: giữ unlock sớm qua SQ-BM-05 với item level 10/source map sau,
   hay sửa điều kiện/item source?
4. Có duyệt packet craft service (quote → preflight → atomic commit theo §11)
   không, và wire/schema mới phải qua cổng duyệt riêng như mọi route khác?

## 6. Kiểm chứng lượt này

```bash
python Implementation/Tools/build_loot_recipe.py   # 57 sources/184 entries; 7 RECIPE named
python Implementation/Tools/build_loot_recipe.py   # lặp lại: git diff --exit-code sạch
dotnet build Server/Health/Health.csproj -c Release --no-restore --nologo
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check
python Implementation/Tools/validate_contracts.py
```

Kết quả và CI đúng commit được công bố trên #87/#41/PR106. Delta chỉ gồm builder +
bundle tái sinh + báo cáo này; không đổi hành vi loader, không đổi gate, không merge.