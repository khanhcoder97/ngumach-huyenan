# QOD-24 — Đối chiếu Top-Down Gameplay World Spec DEC-016 (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Top_Down_Gameplay_World_Spec_vi.md`
(50 dòng, DEC-016 thay thế side-scroll) dưới góc độ server; đối chiếu §1 không gian/
điều khiển, §2 collision/sweep/floor, §3 map/migration/bundle v2/portal, §4 rangeWu với
map_bounds.json, MapTopology, walk geometry, movement, portal alpha, skill catalog.
Báo cáo-only: không mở route/gate/wire, không đổi tọa độ canonical, **không tuyên bố
topology REVIEWED**, không sửa manifest/bundle.

## 1. Trạng thái runtime đo được

- Map bounds: `Implementation/Content/map_bounds.json` `schemaVersion=1`,
  `knownMapIds` đo **=46**, `defaultBounds {xMin:0,xMax:360,yMin:-12,yMax:72}`,
  `overrides=1`, `MAP_BEN_MUA` có mặt. `boundsRule`: "Atlas floor Y=0; manifest
  water/fishing anchors dùng Y âm tới -3; validator cho phép water margin 12 WU".
- Bundle v2: `MapTopology.cs:73` `SupportedBundleVersion=2`; loader bắt
  `coordinateSystem=="TOP_DOWN_XY"` (`:196`), `layoutVersion>=1` (`:185`),
  `bundleVersion==2` (`:190`), `reviewState` hợp lệ (`:202`), bounds khớp registry
  (`:214–222`), `floorIds` không rỗng/không trùng (`:224–241`), walkable + blocked
  polygon >=3 điểm hữu hạn/không tự cắt/trong bounds (`:243/251/315/321`), placements
  (`:253`), sourceRefs không rỗng (`:256`). `TopologyReviewStates` (`:6–9`) chỉ chấp
  nhận **REVIEWED | SYNTHETIC_TEST_ONLY**.
- Movement: `P1Endpoints.cs:750` `distance = MoveSpeedWuPerSecond * elapsedSeconds`;
  `:771` `geometry.CheckWalkSegment(...)` sweep, `:779` `sweep.IsBlocked` chặn.
  README:368 "Direction is normalized, so diagonal input does not grant extra speed";
  README:369 "Distance = MoveSpeedWuPerSecond × elapsed server time, elapsed clamped
  MaxStepSeconds; client timestamps validated for shape but never trusted".
  `appsettings.json:13` `P1World:MoveSpeedWuPerSecond=6.0`; README:519 "**Provisional**
  slice value; not yet locked in production data".
- Facing: runtime dùng vector liên tục `FacingX/FacingY` (`EncounterMessages.cs:148/151`,
  `GuardRuntime.cs:53/54`); grep `DirIndex` trong Server = 0.
- Portal alpha: `AlphaPortals.cs:23` `MaxInteractionDistanceWu=5` (nguồn 5 WU của
  accept/turn-in/talk); `:17–22` DEC-TUTORIAL-TRANSPORT-20261106 cấm thêm phí/cooldown
  ngoài nguồn; `AlphaPortalRegistry` (`:61–65`) 2 entry canonical
  `TP_BM_THANH_LAC (348,0)→(8,0)`, `TP_TL_BEN_MUA (20,0)→(348,0)`, cố ý không gồm
  `TP_BM_THANG_LONG` (gate C1-06), giữ arrival 8 ≠ return 20.

## 2. Khớp (đo từ nguồn)

- **§3 giữ 46 map ID**: `knownMapIds=46` khớp "Giữ 46 map ID và bounds trong
  map_bounds.json để không hỏng API hiện hành". Bến Mưa có trong registry; bounds là
  giới hạn tổng thể (không chứng minh ô đi được) — đúng §3.
- **§1 server-authoritative + normalize**: khoảng cách = tốc độ server × elapsed server
  time, client timestamp chỉ validate hình dạng không tin (README:369, P1Endpoints:750);
  hướng normalize nên chéo không nhanh hơn (README:368) — khớp §1 "client gửi ý định,
  server trả vị trí thực" và "normalize khi độ dài >1". Tốc độ runtime **không** lấy 3,2
  WU/s demo Muse (dùng 6.0 provisional) — đúng ý §1 cấm demo làm mặc định.
- **§2 sweep + diagonal không xuyên góc**: `CheckWalkSegment` sweep trước cập nhật vị
  trí (P1Endpoints:771); self-check `ServiceSelfCheck.cs:2810–2851` phủ refusal
  `sweep.clear/wall/big_step/hole/corner_touch/floor/nonfinite_radius/footprint_blocked`
  — corner-touch bị chặn (khớp §2 "Diagonal không xuyên góc hai tường", "normalize và
  sweep trước khi cập nhật vị trí").
- **§3 bundle v2 TOP_DOWN_XY**: máy validate v2 có thật và bắt đúng coordinateSystem/
  bounds/floors/polygon/sourceRefs/reviewState (MapTopology.cs đã dẫn). Polygon >=3 đỉnh
  hữu hạn, không tự cắt — khớp §3 "Polygon gồm >=3 đỉnh hữu hạn, không tự cắt".
- **§4 rangeWu migration xong cho MK-01/02**: `Examples/SkillDefinition/SK-MK-01.json:13`
  `rangeWu=4.4`, `SK-MK-02.json:13` `rangeWu=11` — khớp §4 "2,2m=>4,4 WU; 5,5m=>11 WU",
  **không** còn lỗi export 2.2/5.5 gắn rangeWu. `SkillDefinition.schema.json:65` có field
  rangeWu. CONE/DASH tính từ facing XY (FacingX/FacingY + CombatDash).
- **§3 portal canonical + range 5 WU**: registry chỉ 2 portal đã duyệt, không tự thêm
  route Thăng Long; touch distance 5 WU cùng nguồn verb quest — khớp §3 "destination vẫn
  dùng canonical portal table, không tự thêm route" và "khoảng tương tác <=5 WU".

## 3. Khoảng trống (field cụ thể)

1. **Không map production nào REVIEWED** (§3/§5 gate topology). Đo thư mục
   `Implementation/Content/Examples/MapTopology`: **1 bundle**, `reviewState=
   SYNTHETIC_TEST_ONLY`, `bundleVersion=2`. `MapTopology.cs:52` `ReviewedCount` đếm
   bundle IsReviewed — với data hiện tại = 0. Máy v2 chạy nhưng chỉ trên bundle synthetic;
   §5 "mỗi map ký riêng gate topology/collision/placement" chưa map nào ký. **Không tuyên
   bố REVIEWED**; đây là blocker thật (§4 "topology reviewed vẫn là blocker thật").
2. **Bundle v2 thiếu field floorLinks/portals/safeZones/cameraBounds** (§3 liệt kê đủ).
   `MapTopologyBundle` trả về chỉ FloorIds/WalkablePolygons/BlockedPolygons/Placements
   (`MapTopology.cs:262–275`); grep `FloorLink|Portal|SafeZone|CameraBounds` trong
   MapTopology.cs = 0; bundle example chỉ có `floorIds`. Các field floorLinks (cầu hai
   đầu), portals, safeZones, cameraBounds là spec-only chưa model hóa trong topology
   runtime. §2 "P1 chỉ dùng OVERWORLD, không cầu chồng đường" vì thế vẫn đúng hiện trạng.
3. **reviewState vocabulary khác migration label** (§3). Runtime chỉ nhận
   REVIEWED | SYNTHETIC_TEST_ONLY (`TopologyReviewStates:6–9`); nhãn
   `TOPDOWN_REVIEW_REQUIRED` của §3 là trạng thái **hồ sơ migration đi kèm**, không phải
   reviewState runtime (không có state UNREVIEWED/REQUIRED được chấp nhận). Cần phân biệt
   khi import migration, không ép nhãn migration vào reviewState.
4. **DirIndex 8 hướng không phải field server** (§1). grep DirIndex=0; facing runtime là
   vector liên tục FacingX/FacingY. Quantize 8 hướng (N=0..NW=7) là presentation sprite
   sheet DEC-015 phía client, không phải contract server đo được. §1 "facing quantize 8
   hướng, giữ hướng cũ khi đứng yên" chưa phải ràng buộc server.
5. **Tốc độ chưa version-lock** (§1). `MoveSpeedWuPerSecond=6.0` là provisional
   (README:519), chưa khóa trong production data version hóa. §1 yêu cầu "tốc độ runtime
   lấy cấu hình server đang version hóa" — giá trị hiện tại là slice tạm, cần owner chốt
   nguồn (không tự đổi số).
6. **Arrival 2s chống retrigger chưa là rule alpha** (§3). grep không thấy hằng số
   cooldown arrival 2s trong Gameplay; `AlphaPortals.cs:17–22` ghi rõ DEC-TUTORIAL-TRANSPORT
   cấm thêm cooldown/phí ngoài nguồn, portal alpha chỉ ship touch-distance 5 WU. "Arrival
   có 2s chống retrigger cổng; không ban bất tử combat" là proposal chờ owner quyết trong
   lane portal WO31 Q3 (topology authority + class-confirm), không tự thêm.
7. **Kiếm Trận range blocked** (§4). §4 "Kiếm Trận chưa có range chính xác nên damage
   rollout giữ blocked tới khi config chốt" — nối task 106/108 (30 skill/gear stats) đang
   chờ nguồn numeric version hóa; endpoint hiện chứng minh gating, không chứng minh
   combat hoàn thiện (đúng disclaimer §4/§5).

## 4. Câu hỏi owner (chưa tự quyết, chưa mở wire)

1. **Topology gate**: lộ trình ký REVIEWED từng map (ai review, thứ tự Bến Mưa trước
   theo §5), hay giữ SYNTHETIC_TEST_ONLY đến khi Muse bàn giao blockout? Không tự nâng
   reviewState.
2. **Bundle v2 field mở rộng**: floorLinks/portals/safeZones/cameraBounds có đưa vào
   MapTopologyBundle + schema khi mở cầu chồng đường/safe-zone, hay giữ P1
   OVERWORLD-only? Cần duyệt schema trước khi thêm field wire.
3. **Tốc độ + DirIndex**: chốt MoveSpeedWuPerSecond production từ nguồn nào; DirIndex
   8 hướng là client-only hay cần server field? Không tự đổi 6.0.
4. **Portal arrival 2s**: có approved rule chống retrigger 2s (ngoài nguồn hiện tại)
   không, hay giữ touch-distance 5 WU như alpha đang ship? Thuộc WO31 Q3 portal lane.

Không gate/wire/merge, không đổi tọa độ, không tuyên bố topology REVIEWED. Mọi số đo từ
map_bounds.json/MapTopology.cs/runtime/JSON skill tại head này; không gõ số sưu tập.