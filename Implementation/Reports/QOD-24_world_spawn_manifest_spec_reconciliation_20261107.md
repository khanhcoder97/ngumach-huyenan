# QOD-24 — Đối chiếu World Spawn / Gathering Manifest (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `World_Spawn_Gathering_Manifest_Spec_vi.md`
(129 dòng) dưới góc độ server; đối chiếu §1 phân loại, §3 design_state, §4 composition,
§6 respawn, §7 node/tool/yield, §8 item-ref với manifest CSV 349 hàng, build script và
runtime world/interact. Báo cáo-only: không mở route/gate/wire, không sửa manifest,
không đổi tọa độ canonical, không thêm anchor.

## 1. Trạng thái runtime đo được

- Runtime nạp world record từ JSON build `Implementation/Content/Runtime/world_records.json`
  (không đọc thẳng CSV production). `WorldRecords.cs:14–25` `WorldRecord` giữ
  RecordId/MapId/RecordType/**DesignState**/EntityIds/X/Y/RespawnSeconds/RespawnPolicy/
  Condition/Gather. `WorldRecords.cs:280–281` `IsKnownRecordType` chấp nhận đúng 5 loại
  `NPC|MOB_GROUP|BOSS|GATHER_NODE|INTERACTABLE` — khớp vocabulary §1.
- `DesignState` là **string opaque**: `WorldRecords.cs:18` field, `:262` `source.DesignState
  ?? string.Empty`, `:294` init. Nhánh duy nhất tiêu thụ DesignState trong runtime là tiền
  tố alpha: `AlphaOverlayMerger.cs:16` `OverlayDesignStatePrefix="ALPHA_OVERLAY:"`, `:47`
  gán `{prefix}{decisionId}`; `ServiceSelfCheck.cs:5970` kiểm `record.DesignState ==
  $"ALPHA_OVERLAY:{alphaDesign.DecisionId}"`. **9 giá trị vocabulary §3** (ATLAS_ANCHOR/
  SPAWN/QUEST_WAVE/QUEST_ACTOR/BOSS/EVENT_POOL, ACTIVITY_BOSS/PLACEMENT, NEW_PROPOSED)
  **không được branch** trong gameplay — chúng là provenance metadata, không điều khiển
  spawn/respawn/loot. grep `ATLAS_|ACTIVITY_|NEW_PROPOSED` trong Server/Health/Gameplay = 0.
- Gather: `WorldRecords.cs:6–12` `WorldGatherRecord(Profession, ItemId, YieldMin, YieldMax,
  ProfessionLevelRequired, ToolId)` — 6 field. `InMemoryInteractionService.cs:196`
  `quantity = _rolls.Roll(record.Gather.YieldMin, record.Gather.YieldMax)` (roll đều
  min..max), `:223` `InteractYield`. Gate nghề `:179` `ProfessionLevelRequired >
  _options.AssumedProfessionLevel` → `InteractionOutcome.cs:12`
  `profession_level_insufficient`. `InteractionOptions.cs:11–12` ghi rõ **DEV FIXTURE**:
  "P1 has no profession progression yet, so gather gates compare against this assumed
  level instead of a per-character profession state" (README:530 `AssumedProfessionLevel=1`,
  Program.cs:630 startup log).

## 2. Khớp (đo từ nguồn, không gõ số)

- **§1 phân loại khớp tuyệt đối**: CSV đo `total_rows=349`; record_type
  `NPC=104, MOB_GROUP=163, BOSS=29, INTERACTABLE=18, GATHER_NODE=35` (tổng 349). Đúng
  từng con số §1 công bố (104/163/29/35/18). `distinct_map_id=46` khớp §1/§2 "46 map ID".
- **§7 node khớp**: `gather_nodes=35`, phân bố đúng 5 node × 7 map
  (`MAP_BEN_MUA/LAM_TRIEU/SA_HOA/TRAN_SON/BACH_UYEN/VUC_NGHICH_MACH/DAI_NGU_MACH` mỗi map 5).
  Profession→tool đo từ CSV: `MINING→TOOL-PICK-01 (16)`, `HERBALISM→TOOL-SICKLE-01 (14)`,
  `LOGGING→TOOL-HATCHET-01 (5)` — khớp §7 mapping 3 nghề/3 tool.
- **§8 item-ref resolve**: gather_item_id và tool_id của 35 node đối chiếu
  `Item_Master_Catalog_vi.csv` (cột `item_id`): `gather_items_unresolved=[]`,
  `tools_unresolved=[]`. Không ID mồ côi — khớp §8 "đã kiểm tra có mặt trong Item Master".
- **§4 composition==quantity**: 304 hàng dùng grammar nhân `ID×N` (NPC 104, MOB_GROUP 163,
  BOSS 29, INTERACTABLE 8); đo `multiplier_composition_quantity_mismatches=0`. Tổng thành
  phần bằng quantity trên mọi hàng nhóm — khớp §4. (45 hàng còn lại composition là prose
  mô tả anchor/socket, không dùng grammar nhân, không áp dụng check này.)
- **§6 respawn data-driven**: `InMemoryInteractionService.cs:155/165/218` respawn theo
  `entity.RespawnSeconds` riêng từng node, claim per-character (`_claims.TryClaim`
  CharacterId+EntityId). Khớp §6 "respawn_seconds là hồi node riêng sau thu hoạch" và
  §7 "node hiển thị theo shard/người chơi tránh tranh chấp last-hit". NPC respawn=0 bền vững.

## 3. Khoảng trống / mâu thuẫn (field cụ thể)

1. **§3 design_state prose STALE so với CSV** (mâu thuẫn nội bộ spec, không phải lỗi CSV).
   Spec §3 viết: "Trong bản này có **176** hàng `ATLAS_*`, **27** hàng `ACTIVITY_*` và
   **130** hàng `NEW_PROPOSED`" — tổng **333**, trong khi §1 và CSV đều là **349** (hụt 16).
   Đo CSV thực tế: `ATLAS_*=182` (ANCHOR 89 / SPAWN 26 / QUEST_WAVE 31 / QUEST_ACTOR 4 /
   BOSS 7 / EVENT_POOL 25), `ACTIVITY_*=38` (BOSS 7 / PLACEMENT 31), `NEW_PROPOSED=129`
   (tổng 349). Lệch so prose: ATLAS **+6**, ACTIVITY **+11**, NEW_PROPOSED **−1**. CSV nhất
   quán nội bộ (tổng đúng 349, mọi hàng có design_state hợp lệ); **prose §3 là bản cũ chưa
   cập nhật**. Vì runtime coi DesignState là opaque (§1.2), lệch này không gây lỗi runtime,
   nhưng là tài liệu bàn giao sai số — cần owner sửa prose, không sửa CSV.
2. **quality_tier + yield_spec bị drop ở build** (§7 tier bonus không model hóa). CSV có
   `quality_tier` (I=16 / II=13 / III=6) và `yield_spec` (35/35 non-empty, chứa xác suất
   +15%/+25% thưởng +1). `build_world_records.py:123–136` chỉ đọc
   yield_min/yield_max/profession_level_required/gather_profession/tool_id — **không đọc
   quality_tier/yield_spec**; JSON gather chỉ 6 field (đo: `{profession,itemId,yieldMin,
   yieldMax,professionLevelRequired,toolId}`). Runtime `Roll(YieldMin,YieldMax)` là roll
   đều, **không áp xác suất bonus tier** (§7 "Tier II 15% +1, Tier III 25% +1"). grep
   `QualityTier|YieldSpec|TierBonus|BonusChance` trong Server = 0. Sản lượng bonus là
   proposal chưa thực thi.
3. **ToolId carried nhưng không enforce lúc gather**. `WorldGatherRecord.ToolId` nạp
   (`WorldRecords.cs:255/311`, JSON `toolId`) nhưng `InMemoryInteractionService` đoạn
   gather (172–224) **không tham chiếu `record.Gather.ToolId`** — chỉ gate profession level
   rồi roll yield. grep `ToolId` trong Gameplay chỉ còn `LifeSimCatalog.cs:34` (record
   fishing/farm khác). §7 "yêu cầu tool bắt buộc" chưa phải điều kiện interact; tool là
   data chờ enforcement (lane life-sim/profession, chưa mở).
4. **Gather base time 1,2s + interrupt-on-hit không phải hằng số runtime**. §7 "thời gian
   cơ sở 1,2 giây; bị đánh ngắt" — gather runtime là **claim tức thời** (không channel/
   duration; grep `GatherSeconds|GatherDuration|ChannelSeconds` = 0). Các hit `1.2` trong
   Server là combat: `MobLifecycle.cs:33 AttackRangeWu=1.2`, AlphaBoss windup coeff 1.2 —
   không phải gather timer. Kênh thu thập 1,2s/ngắt-khi-bị-đánh là presentation/proposal.
5. **Profession level là DEV FIXTURE, không progression per-character**. §7
   `profession_level_required` gate so với `AssumedProfessionLevel=1` cố định
   (InteractionOptions.cs:11–12), không phải trạng thái nghề của nhân vật. Đúng nhãn
   "proposal có thể cân bằng bằng config" (§7/§10) nhưng chưa phải hệ nghề thật.
6. **Composition token scheduler không phải entity ID** (không phải orphan, đã ghi chú).
   `MAN-TA30-TOWER_F30_BOSS_SOCKET` (INTERACTABLE, ACTIVITY_PLACEMENT) có
   `entity_id=OBJ_TOWER_BOSS_ALTAR` nhưng `composition=BOSS_WEEKLY_ROTATION×1`;
   `composition_ids_not_in_entity_id` đo = 1 hàng này. `notes` ghi rõ "BOSS_WEEKLY_ROTATION
   is not a runtime entity or art asset", `condition` nói scheduler chọn source_boss_id
   trong `Weekly_Boss_Rotation_Data_vi.csv`. Đây là token scheduler có chủ ý, không phải
   ID mồ côi; check §9 "entity_id resolve" không flag, nhưng cross-check composition↔
   entity_id ngây thơ sẽ báo lệch — cần giữ ghi chú khi import.

## 4. Câu hỏi owner (chưa tự quyết, chưa mở wire)

1. **Sửa prose §3** về 182/38/129 (tổng 349) cho khớp CSV, hay giữ 176/27/130 như snapshot
   lịch sử và thêm change note? CSV không cần đổi; đây là lỗi tài liệu bàn giao.
2. **quality_tier/yield_spec**: có đưa vào build + runtime (xác suất bonus tier) trong P1
   hay giữ là proposal cân bằng sau? Nếu đưa, cần schema gather mở rộng + roll có trọng số
   (không đổi wire hiện tại nếu chưa duyệt).
3. **Tool enforcement + gather channel 1,2s/interrupt**: thuộc lane profession/life-sim
   nào, có mở interact gate theo ToolId equipped và kênh thu thập ngắt-khi-bị-đánh không?
4. **AssumedProfessionLevel**: khi nào thay bằng profession state per-character (nguồn
   progression nào), hay giữ DEV FIXTURE đến khi có hệ nghề?

Không gate/wire/merge. Mọi số trong báo cáo đo từ CSV/JSON/build script/runtime tại head
này; không gõ số sưu tập, không suy đoán tọa độ.