# Packet QOD-21 Q3 — bundle navigation/placement 2D, version + hash, và bảng source→target — **CHỜ DUYỆT — không đổi tọa độ, không bật `REVIEWED`, chưa có code**

Gửi owner (#87, #41) + Codex (review) + Antigravity #85 / Muse #1 (client).
Lệnh gốc: work order QOD-21 mục 3 — *"Export bounds/floor/axis/PPU/nav version/hash/footbox/portal/trigger cùng path và round-trip test. Giữ 349 placement/canonical quest refs cho tới migration được review. Art staging A2 chưa phải server map. Giao một packet chuyển sang map 2D có source→target cụ thể cho NPC/quái/node/quest/return/portal/arena và toàn đường đi; không x-only projection, không tự dời tọa độ hoặc gắn REVIEWED. Trong lúc Codex review packet, tiếp Q4–Q8."* Owner nhắc lại lúc 23:35:35Z (#87).

Packet này **không** sửa file content nào, **không** đổi schema nào, **không** đụng `approvedXY` của record nào, và **không** đánh dấu bundle nào `REVIEWED`. Toàn bộ số liệu dưới đây đã đếm lại từ checkout này ở head `cdac238`, không lấy từ ghi nhớ.

## 1. Hiện trạng đã đếm (mỗi dòng kiểm lại được bằng lệnh kèm theo)

| cái gì | số liệu | nguồn | cách kiểm |
|---|---|---|---|
| Hàng manifest canonical | **349** = NPC 104 + MOB_GROUP 163 + BOSS 29 + GATHER_NODE 35 + INTERACTABLE 18 | `docs/production/World_Spawn_Gathering_Manifest_vi.csv`, spec ở `World_Spawn_Gathering_Manifest_Spec_vi.md:19` | `len(DictReader(csv))` |
| `world_records.json` | **352** = 349 + 3 supplement atlas (`MAN-BM-OBJ_BM_PACKAGE_01..03`) | `Implementation/Content/Runtime/world_records.json` | `records` length |
| **Record nằm trên lane `y=0`** | **343/352**; 9 record có `yWu` khác 0 (`-3, 3, 5, 7, 8`) | cùng file | đếm `yWu != 0` |
| `world_entities_bm.json` | **44** entity instance, **0/44 có `yWu != 0`** — toàn bộ map `MAP_BEN_MUA` chỉ một lane | `Implementation/Content/Runtime/world_entities_bm.json` | đếm |
| `npc_anchors.json` | **104** anchor, tất cả `floorId=OVERWORLD`, **tất cả `yWu=0`**, `xWu` 18→876 | `Implementation/Content/Runtime/npc_anchors.json` | đếm |
| Registry migration đã có sẵn | **349** record, `reviewState=TOPDOWN_REVIEW_REQUIRED` **349/349**, **`approvedXY` khác null: 0**, kèm `sourceSha256` | `Implementation/Reports/TopDown_Placement_Migration_20261028.json` | đếm |
| Bundle topology | **1** bundle, `reviewState=SYNTHETIC_TEST_ONLY`, `layoutVersion 1`, `bundleVersion 2`, `coordinateSystem=TOP_DOWN_XY`, walkable 1 polygon (4 đỉnh), blocked 3 polygon (4 đỉnh each), placements 1. **Không có bundle `REVIEWED` nào** | `Implementation/Content/Examples/MapTopology/SYNTHETIC_TEST_ROOM_MAP_BEN_MUA.json`, `Implementation/Reports/QOD-10_topology_validation.md` §3 |
| Map đã biết | **46** `knownMapIds`; `defaultBounds` `x 0..360 / y -12..72`; override duy nhất `MAP_THANG_LONG` `0..900 / -12..96`. `MAP_THANH_LAC` **có** bounds (qua `defaultBounds`, không override) | `Implementation/Content/map_bounds.json:3-63` |
| Overlay alpha (7 record) | `RIPPLE_01 (70,3)`, `RIPPLE_02 (86,-3)`, `RIPPLE_03 (104,3)`, `VILLAGER_01 (138,3)`, `VILLAGER_02 (146,3)`, `ALPHA_WAVE_BM_TRAINING (144,0)`, `FRAGMENT (178,0)` | `Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json` `newOverlayRecords` |
| Arena boss | `centerWu [178,0]`, `arenaShape CIRCLE`, `radiusWu 11`, safePad `[168,0]`/`[188,0]` r `0.75` | cùng file, `boss` |
| Hazard P00-03 | `rectangleWu {minX 140, maxX 148, minY -2, maxY 2}` | cùng file, `questRules["P00-03"].waveTrial` |
| Escort P00-04 | `waypointsWu [[42,0],[80,0],[120,0]]`, `checkpointXs [80,120]` | cùng file, `questRules["P00-04"]` |
| Death-return anchor | `mapId MAP_BEN_MUA`, `safeAnchorWu [18,0]` | cùng file, `deathReturn` (đã duyệt `DEC-DEATH-RETURN-20261105`) |
| PPU | `20 px/WU; 1 WU = 0,5 m` — **là quy chuẩn render/art**, không phải field server | `docs/production/Pixel_Art_Production_Standard_vi.md:20`, `Top_Down_Gameplay_World_Spec_vi.md:7-8` |
| Footprint | hero `capsule ngang 1,2×0,6 WU, offset (0;0,3)`; server chỉ có **một scalar** `P1World:ActorFootprintRadiusWu=0.6` | `Top_Down_Gameplay_World_Spec_vi.md:16`; `Server/Health/appsettings.json:21` |
| Portal / trigger record | **Không tồn tại ở dạng record có tọa độ trong JSON nào.** Chỉ có prose `TP_LT_THANH_LAC=(350,0)` / `TP_DNM_VUC=(350,0)` trong atlas, và chuỗi điều kiện `"Tắt khi P00-05 boss trigger"` trong `condition` | `Map_Production_Atlas_vi.md:144,232`; `world_entities_bm.json:546,566,586` |
| Path tuần tra | Manifest **có** cột `patrol_path`, `patrol_radius_wu`; **không** runtime JSON nào và **không** loader nào đọc chúng | `World_Spawn_Gathering_Manifest_vi.csv` header; §9 |

**Bằng chứng mạnh nhất cho "không x-only projection":** overlay alpha đã dùng `y=±3` cho ripple/villager trong khi **0/44** entity runtime và **343/352** record nằm `y=0`. Nghĩa là thiết kế đã cần 2D; chỉ riêng dữ kiện này đủ để nói lane `y=0` là giả định tạm, không phải hiện thực bản đồ.

## 2. Server đang đọc gì / không đọc gì (để biết chỗ nào còn trống)

Đang parse: `MapBoundsLoader` (`schemaVersion`, `defaultBounds`, `overrides`, `knownMapIds`) → `MapBounds(XMin,XMax,YMin,YMax)`; `MapTopology.cs` (`LayoutVersion`, `BundleVersion==2`, `CoordinateSystem=="TOP_DOWN_XY"`, `ReviewState ∈ {REVIEWED, SYNTHETIC_TEST_ONLY}`, `Bounds`, `FloorIds`, `WalkablePolygons/BlockedPolygons` với `points[{xWu,yWu}]`, `Placements[{recordId,npcId,floorId,xWu,yWu}]`, `SourceRefs`); `WorldRecords.cs`; `WorldEntities.cs`; `NpcAnchors.cs`; `WorldGeometry.cs` (point-in-polygon + segment LOS, từ chối `nonfinite/floor/outside_walkable/blocked_polygon`).

Không có **bất kỳ** representation nào phía server cho: `PPU`/render origin, **footbox per-entity** (chỉ có một bán kính toàn cục), `navVersion`/lưới nav, **portal record**, **trigger volume**, **path/patrol route**, **content hash**, và `floorLinks`/`safeZones`/`cameraBounds` (schema topology hiện `additionalProperties:false` nên **không chứa nổi** các trường mà `Top_Down_Gameplay_World_Spec_vi.md:28` yêu cầu cho bundle v2).

## 3. Bundle `nav_ben_mua_v1.json` đề xuất (export + round-trip, không đổi tọa độ)

Nguyên tắc: bundle mới **chỉ đóng gói dữ kiện đã có**; mỗi field phải trỏ được về một nguồn, nếu không thì nằm trong §5 (thiếu nguồn) chứ không được bịa.

```jsonc
{
  "schemaVersion": 1,
  "navVersion": 1,                       // tăng khi layout đổi, KHÔNG bao giờ tái chế
  "mapId": "MAP_BEN_MUA",
  "coordinateSystem": "TOP_DOWN_XY",     // +X Đông, +Y Bắc; Z chỉ render (Top_Down_..._Spec:7)
  "floorIds": ["OVERWORLD"],
  "bounds": { "xMin": 0, "xMax": 360, "yMin": -12, "yMax": 72 },  // map_bounds defaultBounds
  "cellSizeWu": null,                    // SEE §5: không nguồn
  "units": { "wuToMetres": 0.5 },        // có nguồn; PPU thì KHÔNG (xem §5)
  "sources": [
    { "path": "docs/production/World_Spawn_Gathering_Manifest_vi.csv", "sha256": "<64 hex>" },
    { "path": "Implementation/Content/map_bounds.json", "sha256": "<64 hex>" },
    { "path": "Implementation/Content/Runtime/world_entities_bm.json", "sha256": "<64 hex>" }
  ],
  "contentSha256": "<sha256 của canonical JSON, đã sort key, không white-space>",
  "placements": [                        // bản sao y hệt, KHÔNG phải quyết định mới
    { "recordId": "MAN-BM-NPC_LYAN", "kind": "NPC", "mapId": "MAP_BEN_MUA",
      "floorId": "OVERWORLD", "xWu": 42.0, "yWu": 0.0,
      "reviewState": "TOPDOWN_REVIEW_REQUIRED", "approvedXY": null }
  ],
  "volumes": [],                         // rỗng cho tới khi §5 được trả lời
  "portals": [],                         // rỗng — xem `QOD-21_Portal_Contract_Packet`
  "paths": []                            // rỗng, dù manifest có patrol_path: xem §5
}
```

Quy ước version/hash (điểm này owner hay chốt, nên tôi nêu rõ thuật toán thay vì để suy đoán):
1. `sources[].sha256` = digest **nguyên văn byte** của file nguồn (như `TopDown_Placement_Migration_20261028.json` đang làm với `sourceSha256`).
2. `contentSha256` = `sha256(` canonical JSON của bundle **không chứa** `contentSha256`: key sort theo ordinal, không khoảng trắng, số không zero-pad) → dựng lại nhiều lần phải ra cùng một digest, đó là điều round-trip test kiểm.
3. `navVersion` là số nguyên do người biên tập tăng; **không** suy từ hash. Lý do: một layout đổi nội dung nhưng cùng hash (ví dụ tráo thứ tự không đổi hình học) không được phép làm client tưởng là không đổi.
4. Bundle giữ `reviewState` **kế thừa từ registry** (`TOPDOWN_REVIEW_REQUIRED`), và server từ chối bundle tự xưng `REVIEWED` mà registry chưa có `approvedXY`.

Round-trip test (thứ CI sẽ chạy, `Implementation/Tools/`):
- `build_nav_bundle.py` → `validate_nav_bundle.py` → `--self-check` của server nạp lại bundle và so **từng** placement với `world_records.json`/`npc_anchors.json` (sai biệt duy nhất cho phép: `null`).
- Build hai lần liên tiếp phải ra byte-identical (chống timestamp đồng hồ lọt vào bundle).
- Đổi một ký tự trong manifest CSV nguồn → test phải FAIL (chứng minh hash thật, không phải chữ trang trí).
- Số học kiểm tra: `len(placements) == 352`, `count(xWu/yWu != registry) == 0`, `count(approvedXY != null) == 0`.

## 4. Bảng source→target mà migration sẽ phải đi qua (không làm gì trong bảng này hôm nay)

| class | hiện ở đâu (đếm được) | đích cần có | thiếu gì để dời |
|---|---|---|---|
| NPC anchor | `npc_anchors.json` 104, tất cả `y=0`, x tới 876 | toạ độ 2D thật per map, có `approvedXY` | **toàn bộ**: không có nguồn toạ độ 2D nào được duyệt |
| Mob spawn / group | `world_entities_bm.json` 25 MOB trên 7 group BM (`SPAWN_BM_01..07`) + `WAVE_BM_ESCORT_A/B`, tất cả `y=0` | vị trí bầy đàn theo vùng thật (đường đi, không phải lane) | như trên + quy tắc vùng spawn (chưa có) |
| Gather node | 5 node BM (21..132, `y=0`), 35 record toàn cục | như trên | như trên |
| Interactable | `OBJ_BM_PACKAGE_01..03` (36/44/52), `FISHING_LINH` (132) | như trên; **lưu ý**: 3 package là DEV FIXTURE do `build_world_records.py` thêm, không phải canonical | cần owner xác nhận package có phải canonical không |
| Boss arena | `centerWu [178,0]`, `radiusWu 11`, safePads `[168,0]`/`[188,0]` r 0.75 — **đã duyệt** | giữ nguyên; arena là hình tròn nên đã 2D một phần | không dời gì cho tới khi bounds map đổi |
| Hazard/trial | `rectangleWu (140,-2)-(148,2)` — **đã duyệt**, đã có `y` khác 0 | thành trigger volume record | schema hiện không chứa được (xem §2) |
| Escort path | `waypointsWu [[42,0],[80,0],[120,0]]` — ba điểm thẳng hàng `y=0` | đường đi thật có `y` đổi | không có nguồn; `patrol_path` manifest chưa từng được đọc |
| Death-return anchor | `[18,0]` `MAP_BEN_MUA` — **đã duyệt** `DEC-DEATH-RETURN-20261105` | giữ nguyên; migration nào đổi `[18,0]` phải là một quyết định mới, không phải hệ quả im lặng | — |
| Portal | **không có record nào**; `MAP_THANH_LAC` đã có bounds qua `defaultBounds`, có 24 record + 17 NPC anchor, nhưng **không** có điểm đến | packet riêng đã gửi: `QOD-21_Portal_Contract_Packet_20261104_vi.md` | tọa độ hai đầu, cặp map, điều kiện |
| Path/cảnh giới | cột `patrol_path`/`patrol_radius_wu` trong manifest, không consumer | `paths[]` trong bundle | **không nguồn dạng máy đọc** |

## 5. THIẾU NGUỒN — tôi không tự chọn số

Mỗi mục là một câu hỏi, kèm lựa chọn tôi sẽ làm nếu owner im lặng (mặc định luôn là "không làm gì / để null"):

1. **PPU phía server.** Mọi phát biểu `20 px/WU` đều là chuẩn render/art (`Pixel_Art_Production_Standard:20`, DEC-014). Tôi **không** đưa `pixelsPerUnit` vào bundle server, trừ khi owner nói ngược lại. Câu hỏi: bundle server có được phép chứa field render không, hay PPU chỉ sống ở client config?
2. **Footbox per-entity.** Từ khoá "footbox" không tồn tại trong repo. Có footprint hero `1,2×0,6 WU` (docs) và một scalar server `ActorFootprintRadiusWu=0.6`. Câu hỏi: footbox là (a) một cặp `w,h` per template, (b) bán kính scalar như hiện tại, hay (c) capsule như docs? Chọn sai là đổi collision của 44 entity.
3. **Lưới nav / `cellSizeWu`.** Không có nguồn. `thang_long_layout_v2.json` có `chunkSizeWu [64,64]`, `chunkGrid [32,24]`, `logicalResolution [640,360]` nhưng file đó tự ghi `activation: DESIGN_ONLY_REQUIRES_MIGRATION` và chỉ cho `MAP_THANG_LONG`. Tôi để `cellSizeWu: null`. Câu hỏi: có duyệt một kích thước ô không, và ô đó dùng cho LOS hay chỉ cho pathfinding client?
4. **`navVersion` do ai tăng.** Mặc định: tôi thêm tham số `--nav-version` bắt buộc trong build tool, không tự động hoá, để mỗi lần đổi layout là một lần người quyết định.
5. **Portal record có được nằm trong topology bundle không?** `MapTopology.schema.json` đang `additionalProperties:false`, nên thêm `portals/floorLinks/safeZones/cameraBounds` là **đổi schema đã đóng băng** — cần quyết định riêng (bundleVersion 3?), không ăn theo packet này.
6. **Trigger volume.** Chuỗi `"Tắt khi P00-05 boss trigger"` là ghi chú, không phải hình học. Câu hỏi: nó có trở thành `volumes[]` không, và ai quyết hình (center/radius hay rect)?
7. **Patrol path.** Manifest có cột nhưng không loader nào đọc. Nếu đưa vào bundle thì phải định nghĩa dạng: danh sách waypoints, radius, và **hành vi** (server authoritative hay client-only). Không có nguồn cho cả ba.
8. **349 hay 352 là "placement canonical".** Registry migration ghi 349; runtime có 352 vì `build_world_records.py` cộng 3 package DEV FIXTURE. Nếu round-trip test so với 352 thì nó sẽ **khoá** 3 record do tool tự thêm. Câu hỏi: 3 package đó nên thành record duyệt chính thức, hay thành overlay-only như alpha? Mặc định của tôi: không đổi gì, chỉ ghi rõ `origin: TOOL_SUPPLEMENT_DEV_FIXTURE` trong bundle.
9. **Thứ tự review.** Tôi đề xuất: (i) owner/Codex duyệt packet này; (ii) tôi build bundle + validator + round-trip test **với tất cả `approvedXY` vẫn null** và enforcement **vẫn OFF**; (iii) migration tọa độ thật là một quyết định riêng, từng map một, có `approvedXY` tường minh.

## 6. Việc làm được ngay sau khi duyệt, không đụng toạ độ, không wire change

1. `Implementation/Tools/build_nav_bundle.py` (deterministic, đọc `sources` và xuất `contentSha256`).
2. `Implementation/Tools/validate_nav_bundle.py` (schema + hash + bounds + "không được đổi toạ độ so với registry" + "không được có approvedXY nếu chưa REVIEWED").
3. `Implementation/Content/Schemas/NavBundle.schema.json` (schema mới, không sửa schema cũ).
4. Nạp bundle trong `--self-check` và round-trip test; job CI `nav-bundle`.
5. Server **chưa** dùng bundle này cho hình học: `WorldGeometry` vẫn chỉ enforcement khi có bundle topology `REVIEWED` (không có cái nào), nên adding bundle không đổi hành vi runtime — đây là điểm tôi muốn owner xác nhận, vì nó là lý do bước này an toàn.

Không có mục nào trong §6 bật flag production nào, và không mục nào sửa `docs/production/**`, topology `reviewState`, hay toạ độ canonical.

## 7. Một giới hạn của chính packet này

Packet này mô tả **khung** bundle và migration; nó không thể cung cấp toạ độ 2D, vì không nguồn nào trong repo có toạ độ đó (§5.1–.5.4, §4). Nếu owner cần "map 2D chạy được" chứ không phải "khung để review map 2D", thì phần thiếu nằm ở art/design (A2 staging chưa phải server map — đúng như lệnh gốc nói), không phải ở code server, và tôi cần một nguồn toạ độ được duyệt trước khi viết bất kỳ số nào vào bundle.
