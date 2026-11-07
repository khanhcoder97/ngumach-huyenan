# QOD-24 — Đối chiếu Quest / Narrative production spec với runtime (work order 29 Q5/Q7)

Ngày: 2026-11-07. Phạm vi: đọc trọn lần đầu `Quest_and_Narrative_Production_Spec_vi.md`
(202 dòng) dưới góc độ server; đối chiếu §1 quy ước triển khai, §2 36 quest chính, §3 40
quest phụ, §5 acceptance/failure với quest runtime, `Quest_Dialogue_Production_Data_vi.csv`,
`narrative_nodes_v1.json`, `npc_anchors.json` và manifest spawn. Báo cáo-only: không mở
route/gate/wire, không sửa nguồn, không đổi vocabulary wire đã đóng băng.

## 1. Trạng thái runtime đo được

- Quest runtime **có thật**: `QuestDefinition.cs` khai báo `QuestTypes` 7 loại
  (MAIN/SIDE/DAILY/WEEKLY/CLASS/GUILD/EVENT), `QuestObjectiveTypes` **6 loại**
  (COLLECT/KILL/INTERACT/ESCORT/BOSS/TALK, dòng 21–36), `QuestActivations` ACTIVE/BLOCKED;
  `QuestCatalogValidator.cs` fail-fast, validate target theo type (switch 6 case, dòng 43–55);
  `NarrativeNodes.cs` graph node + `PartyPolicies.SoloOnly`; `QuestTalk.cs`; escort/boss alpha.
- `narrative_nodes_v1.json` (runtime load): **229 node, 76 quest**, node_type OFFER 76 /
  CLUE 76 / TURN_IN 76 / CHOICE 1 (node choice mang 2 option).
- `Quest_Dialogue_Production_Data_vi.csv` (nguồn): **230 row, 76 quest_id distinct**
  (36 main-pattern P00/C1–C6 + 40 SQ, 0 other); node_type OFFER 76 / CLUE 76 / TURN_IN 76 /
  CHOICE 2.

## 2. Phần khớp (đo từ nguồn, không gõ số tay)

- **76 quest = 36 chính + 40 phụ** khớp spec §2 (36) + §3 (40): CSV distinct quest_id = 76,
  runtime JSON distinct questId = 76; phân rã 36 main-pattern + 40 SQ + 0 other.
- **Build dialogue graph trung thực**: 230 CSV row → 229 distinct node; `in_csv_not_json` =
  rỗng. 2 row CHOICE là 2 option (PUBLISH/COUNCIL) của **một** node `DLG_C3_05_CHOICE`
  (C3-05 Lò Trời), gộp thành `choices[]` với flag `C3_05_PUBLISHED`/`C3_05_COUNCIL_ONLY` —
  khớp spec C3-05 "công bố nhật ký hoặc giao hội đồng; lựa chọn đổi Trust/thoại, không đổi loot".
- **5 class master đã đăng ký anchor**: `npc_anchors.json` có NPC_MASTER_MINH_KIEM/ANH_DAO/
  HUYEN_BUT/THACH_CHUY/LINH_CUNG, mỗi vị 2 placement (MAN-TL Thanh Lạc + MAN-VM Đài Ngũ Mạch);
  tổng 104 anchor / 83 npcId distinct.
- **Escort P00-04 checkpoint x=80/x=120** đã cài (`AlphaEscortService.cs`: waypoint
  (42,0)→(80,0)→(120,0), followRange 12 wu, wipe khôi phục checkpoint) — khớp spec P00-04
  và §5 "escort reset tại checkpoint". (Làn alpha đã báo ở WO31 Q4 / QOD-19/21.)
- **Respawn data-driven**: `RespawnSeconds`/`GroupRespawnSeconds` nguồn từ manifest mỗi entity
  (`WorldEntities.cs:72/81`, `MobSpawnGroupService.cs`), không phải hằng số cứng.
- **Idempotent reward/accept/cast/interact**: ledger `idempotencyKey` theo character
  (README:505/406), replay trả kết quả đầu, khác payload → `409 idempotency_conflict` — khớp
  §5 "transaction idempotent / unique transaction id" ở mức replay-guard.

## 3. Khoảng trống (field cụ thể, đo được)

1. **Step-kind vocabulary lệch**: spec §1 liệt kê 8 loại step (TALK/INTERACT/KILL/COLLECT/
   ESCORT/**DEFEND**/**BOSS_PHASE**/**INSTANCE_CLEAR**); runtime `QuestObjectiveTypes` chỉ 6.
   `DEFEND` grep hit = chuỗi combat DEFENDER_DOWN/DEFENDER_CURRENT_FOOT (`GuardRuntime.cs:24`,
   `GuardPrecision.cs:169`, `CombatTickEngine.cs:516`), **không** phải objective type;
   `BOSS_PHASE` hit = character id `CHR_SELFCHECK_BOSS_PHASE` (`ServiceSelfCheck.cs:8717+`);
   `INSTANCE_CLEAR` grep = 0. Spec BOSS ánh xạ runtime Boss; DEFEND/BOSS_PHASE/INSTANCE_CLEAR
   không có case trong `QuestCatalogValidator` → quest author bằng các step này không validate được.
2. **Token NPC_MASTER không được thay**: spec §1 gọi token `NPC_MASTER_[CLASS]` (**0 occurrence**
   trong CSV/runtime); CSV + `narrative_nodes_v1.json` ship `NPC_MASTER_BY_PLAYER_CLASS`
   (**6 node**: C1-02 + C6-03, mỗi quest OFFER/CLUE/TURN_IN). Không có compiler thay thế
   (Quests dir grep MASTER/Replace/Substitut/[CLASS]/classId = 0). Placeholder **không** phải
   npc_anchor (chỉ xuất hiện trong narrative JSON + CSV); 5 master cụ thể tồn tại nhưng không gì ánh xạ
   placeholder → master theo lớp người chơi. C1-02/C6-03 TALK không bind được NPC theo lớp
   (liên quan task #134 TALK blocked).
3. **Party share §5 "chia tiến độ trong 35m"**: `PartyPolicies.SoloOnly`
   (`NarrativeNodes.cs:46–51`) ghi rõ "P1 has no party runtime ... instead of implying shared
   credit". Không share radius 35m, không party progress.
4. **Quest pouch §5**: grep pouch/QuestItem/quest_pouch = 0 trong Server. Reward/item quest đi
   vào BAG thường (README P00-01 turn-in "1 chest item in inventory"); không pouch riêng, không
   khóa bán/phân giải cho quest item.
5. **Respawn prose "20s" lệch timer authored**: §5 nói "quái quest respawn 20s"; manifest
   `respawn_seconds` cho quest mob = **18/20/24/30/0 theo zone** (MOB_CARPLING 18/20/30/0,
   MOB_WATERROOT 24/30; chỉ 1 row CARPLING = 20). Runtime tôn trọng giá trị nguồn (đúng);
   prose §5 "20s" là khái quát không khớp timer authored. "Icon riêng" là client UI, không field server.
6. **Raid reconnect §5 "trước boss death+60s, tham gia ≥30% được clear"**: không logic
   participation/reconnect (Participation grep chỉ = prose pet `CompanionCatalog.cs:89`).
   Không raid-clear-credit rule.
7. **Durable transaction + reset bucket**: ledger idempotency in-memory, bounded 256, mất khi
   restart (README:751/406) — chưa phải transaction bền cho one-time reward (làn persistence #79,
   không second writer). 76 quest shipped đều main+side; `QuestTypes` khai báo DAILY/WEEKLY/
   GUILD/EVENT/CLASS nhưng không record riêng, không reset bucket server-side đo được.

## 4. Câu hỏi owner (chưa tự quyết, chưa mở wire)

1. **Step kind**: thêm objective type DEFEND/BOSS_PHASE/INSTANCE_CLEAR (schema + validator +
   handler) hay ánh xạ về 6 loại hiện có (BOSS_PHASE→Boss, DEFEND→Escort/Kill wave,
   INSTANCE_CLEAR→Boss/Interact)? Quest spec nào dùng chúng và mapping duyệt là gì?
2. **NPC_MASTER**: duyệt compiler thay `NPC_MASTER_BY_PLAYER_CLASS` → anchor master theo lớp,
   và đổi token về `NPC_MASTER_[CLASS]` của spec hay sửa spec theo placeholder đã ship?
   Placement nào (TL hay VM) cho C1-02 vs C6-03? (Liên quan #134.)
3. **Party/raid/pouch**: P1 SoloOnly là chủ đích — party-share-35m / raid-reconnect-30% thuộc
   làn sau hay spec §5 nên đánh dấu post-P1? Quest pouch + khóa bán/phân giải quest item:
   sub-domain inventory mới hay flag trên BAG item?
4. **Respawn + durable**: sửa prose §5 "20s" thành "respawn_seconds nguồn theo entity
   (18/20/24/30/0)"? Transaction reward bền + daily/weekly reset bucket thuộc persistence #79 —
   xác nhận làn, không second writer.

## 5. Nguồn đối chiếu

- `docs/production/Quest_and_Narrative_Production_Spec_vi.md` (§1–§5, biên tập v2).
- `docs/production/Quest_Dialogue_Production_Data_vi.csv` (230 row).
- `docs/production/World_Spawn_Gathering_Manifest_vi.csv` (respawn_seconds quest mob).
- `Implementation/Content/Runtime/narrative_nodes_v1.json` (229 node),
  `Implementation/Content/Runtime/npc_anchors.json` (104 anchor / 83 npcId).
- `Server/Health/Gameplay/Quests/QuestDefinition.cs`, `QuestCatalogValidator.cs`,
  `NarrativeNodes.cs`; `Server/Health/Gameplay/Alpha/AlphaEscortService.cs`;
  `Server/Health/World/WorldEntities.cs`, `MobSpawnGroupService.cs`; `Server/Health/README.md`.