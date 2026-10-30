# Qoder — gói tiếp theo: chiến đấu và chuỗi Bến Mưa

Ngày giao: **2026-10-30, Asia/Tokyo**. Issue chủ vẫn là #41. Tiếp nối work order 07; nhận cả gói QOD-16 pha2 → QOD-20, chia milestone/PR và tiếp tục phần độc lập khi chờ review. Không coi một proposal, exporter hoặc số test xanh là đã có vòng chơi hoàn chỉnh.

## 1. Điểm xuất phát đã kiểm

| PR | Head đã ghi nhận | Trạng thái |
|---|---|---|
| #53 | 37ee7ff9860c5d999add9064cb80fd7c85ad80fb | Có bản sửa claim/idempotency, chờ Codex review lại; chưa merge |
| #54 | c5f43e42f958b1d5bffc75f9f58c9b2de2196db3 | Có bản sửa transaction/replay/floor, chờ review lại; base #53 |
| #57 | 8f4a6685063c26991d85beb35627d860b5bf2e20 | E2E hai profile đã bàn giao; base #54, chưa merge |
| #60 | a513869b56a162bb6f583fcfb5f3501b7d3cbddb | Đã kiểm 6/6 CI success; **pha1 domain/internal projection**, chưa nối damage/snapshot; base #57 |

Qoder giữ checkout/stack đang làm, bảo toàn `temp_rgba.png`, `test.png` và mọi WIP chưa rõ chủ; không clean/reset/stash hộ người khác. Checkout root hiện chưa có work order 07/08 thì đọc bằng GitHub hoặc `git show origin/main:<path>` sau fetch. Không pull/switch main mù vào giữa stack. Chỉ Codex review/merge; CI success không thay review correctness.

## 2. Quyết định owner cho sáu câu hỏi QOD-16

Các quyết định dưới cho phép triển khai phần prototype được mô tả, không tự mở production gate hoặc duyệt toàn bộ PR #60.

### Q1 — level của mob

Cho dùng **REFERENCE_L5 trong profile DEV rõ nhãn** để đóng vòng kiểm thử ba archetype hiện có. Bảng tham chiếu cấp5 trong P1_Design_Resolution không phải level thật của mọi spawn. `character_level_min/max` là band người chơi, không phải spawn level. Không activate 46map hoặc gán cấp5 toàn bộ quái.

Exporter giữ sourceRef/version/activation. Nếu HP sau multiplier không nguyên, ghi unresolved quantization hoặc proposal cụ thể trước rollout ngoài fixture; ATK/DEF giữ thập phân, floor một lần ở Final damage. Không gọi profile ghép fixture HP100/MP50 với công thức tham chiếu là cân bằng đã duyệt. Migration actor stats/HP/MP là mốc riêng.

### Q2 — đánh thường

**Có đánh thường** trong subset Minh Kiếm, theo Production_Rules §2: mỗi nhát100% attack, range4WU/quạt90°/cap1, windup0,15s/hit0,10s/recovery0,25s, timeout combo1,5s sau recovery; ceil thời lượng theo20Hz.

Một lệnh là một nhát; ba nhát là chuỗi combo, không cấp ba hit cho một lần bấm. Recovery/sequence/target/hit do server kiểm. Phân biệt BASIC_ATTACK với active skill trong DTO mới, không tạo SK-MK-07 giả hoặc mở pattern skill v1 để nhét đánh thường. Các class khác vẫn unsupported tới khi có content/runtime của chúng.

### Q3 — transport và thời điểm damage

Chọn **typed combat events có version**, snapshot dùng reconciliation. Không dùng chênh HP trong polling hoặc `combat.effect` làm bằng chứng hit/counter/death; không chèn `hits[]` vào response v1 additionalProperties=false.

Pha này HTTP prototype: giữ v1 nguyên vẹn; triển khai v2 opt-in qua namespace endpoint riêng, đề xuất chuẩn `/p1/v2/world/{sessionId}`, `/p1/v2/combat` và endpoint đọc event có cursor theo session/audience. V2 schema/example/validation phải đi cùng nhau; trường hợp basic attack có action kind riêng. Session/auth P1 hiện có không vì thêm đường v2 mà trở thành auth production. Codex sẽ viết adapter client, không bắt Muse/OpenCode sửa wire thay.

Response command trả accepted/castId/cost-CD state và các event **đã xảy ra**. Impact tương lai chạy ở tick thực: không trả sẵn cả ba hit MK03 ngay lúc accepted. Event polling có cursor monotonic, khoảng trống/overflow báo resync rõ, bounded buffer theo budget nguồn; không drop rồi giả như không thiếu. Replay command trả cùng kết quả, không tạo cast/event/death mới. Có examples START/IMPACT/MISS/CANCEL/END/death với correlation castId/eventId/hitIndex, mapInstanceId/floorId, lifeId, targetId và revision xác định aggregate.

Đây là phê duyệt hướng v2 tách biệt và reliable event read; cập nhật proposal cụ thể trước khi code wire. Không đợi thêm lựa chọn transport từ chủ, tiếp tục domain/test/schema/fixtures trong cùng gói.

### Q4 — loot và EXP

Nguồn đã có: `Loot_Recipe_Reward_Production_Data_vi.csv` có LOOT_ENTRY, MATERIAL_POOL/SELECT_ONE, `group_chance_bps=1200`, weight và quantity. Roll12% là **một lần cho group**, sau thành công chọn một entry theo weight; không roll12% độc lập cho từng vật liệu. Pool riêng của placement cần đối chiếu table và khai precedence/provenance; không mở rộng pool từ tên quái. RNG server-owned có version, receipt/roll result giữ ổn định qua retry; seed do client chọn không quyết định loot.

Số Đồng theo band vẫn chưa có giá trị executable được chốt trong các nguồn đã kiểm. Giữ actual mob-loot grant OFF tới khi reward bundle đầy đủ được review; làm exporter/RNG/eligibility/ledger tests và proposal phần thiếu ngay. Không tự lấy tỷ lệ12% làm số Đồng hoặc báo hoàn tất loot khi mới dry-run. Kill progress có thể chạy độc lập, không giả đã trao loot.

EXP **đã có nguồn**, không tiếp tục ghi toàn bộ XP chưa được thiết kế: Production_Rules §1 và `level_progression_v1.json`. XP-to-next=ceil(100+50L+25L²); thường25%, boss chương55%, phụ12% tại cấp nhận, floor và snapshot khi accept; số tuyệt đối có sẵn ưu tiên. Oracle cấp1: ngưỡng175, quest thường43, boss chương96, phụ21; mob cấp5 cho20 trước các modifier. Elite/quest-boss/world-raid dùng đúng rule riêng, tránh cộng chồng. Triển khai XP cần transaction với reward/level/ledger và migration riêng; chỉ báo `applied=true` khi đã commit thật.

### Q5 — Phản Quang

**Cập nhật owner DEC-022:** precision đã được chốt tại `docs/production/P1_Guard_Precision_20261030_vi.md` và `Implementation/Content/DesignBaselines/p1_guard_precision_v1.json`. Dùng quyết định mới để triển khai versioned guard/counter/status cùng ma trận tests; không cần hỏi lại hướng/thời lượng DR. Đoạn dưới ghi blocker ở thời điểm giao ban đầu, không còn là yêu cầu phải chờ proposal thiết kế trước khi làm domain.

Tách proposal con với case/hit ordering cho guard0,4s, hướng, một counter/cửa, +2KiếmÝ, source chết cùng tick và câu giảm sát thương hụt20% còn thiếu hướng/thời lượng. Không tự điền DR/duration. Phần counter/DR chưa được duyệt phải ghi unsupported; cast accepted hiện có không chứng minh phòng thủ đã có tác dụng. Basic/MK03/mob pipeline và quest tests tiếp tục độc lập. Chỉ emit COUNTER_CONFIRMED sau khi mechanics được duyệt và code thật.

### Q6 — entity và visibility

Snapshot v2 gồm MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE **sau filter audience**. Nguồn Online_Persistence_Release_Complete §2 đã quy định PvE AOI radius40WU, hysteresis8WU. Kiểm cùng instance/map/floor/phase trước AOI; không wire nguyên27entity toàn map như một policy production. Internal projection có27candidate không đồng nghĩa mọi client nhận27visible.

NPC invulnerable và node/interactable không thành target damage hoặc death từ HP0. Boss blocked có targetability/health state rõ, không hiển thị như boss đã chết. Availability/cooldown node theo người gọi, không lộ quest flags/inventory hoặc claim riêng của người khác. V1 không bị thêm field/enum lạ. Full-map fixture chỉ để test có nhãn và không dùng làm bypass AOI cho bản chơi.

## 3. Hai sửa correctness phải làm trước khi mở rộng chuỗi

**P00-01 availability:** Production_Rules §5 ghi mỗi package tính tối đa1/character và không trừ world item cho người khác. Generic shared INTERACTABLE có thể giữ shared rule khi nguồn yêu cầu, nhưng ba package P00-01 phải có policy per-character/quest rõ trong data. Không dùng global Despawn khiến người thứ hai phải đợi respawn của người trước. Sửa ở phạm vi PR liên quan và propagate stack an toàn; E2E hai người nhặt đủ3kiện cùng lúc không phải sleep chờ người đầu. Không biến retry60lần thành cách che sai ownership.

**Progress dedupe:** dùng scope actor/quest/objective/event-or-record phù hợp, không dùng một key record chung làm objective đầu nuốt tiến triển của objective khác. Test hai objective hợp lệ cùng liên quan một record, duplicate event và sequential-step guard; không tự mở tất cả step chỉ vì một event có cùng tên.

Aggro threat trong Rules §4 là chính sách chọn target, chưa tự xác định quyền nhận thưởng. Với prototype solo/không party ở mốc này, owner cho policy DEV: nguồn gây HPDamage kết liễu hợp lệ nhận kill credit, khóa theo entityLifeId/deathEventId; replay không cộng lần hai. Đây là quyết định prototype mới, không là loot/party policy final. Party share/reward production phải proposal theo participation và radius70WU cùng tầng trong Rules §7; không đồng nhất nó với AOI40WU hoặc highest threat. Không phát loot trước eligibility/ledger được duyệt.

## 4. Các milestone thực thi — nhận cả gói

### QOD-16 pha2 — contracts, projection và event read

Đưa quyết định ở §2 vào proposal/schema/examples rồi nối read model v2 và event channel. Có mapInstance/floor/phase/AOI/lifeId/revision semantics; validate version, response shape, cursor gap/resync, old v1 compatibility. Reconcile state không tự phát lại audio/VFX. Test node riêng, NPC không targetable, boss blocked, AOI enter40/leave48, floor/instance khác và phase chưa mở. Không đổi topology thành REVIEWED.

### QOD-17 — combat thực sự chạy theo tick

Accepted → start/windup → hit window/impacts → recover/end/cancel. Basic và MK03 có damage thật theo supported subset; MK02 sweep di chuyển không damage; MK01 giữ giới hạn ở Q5. Snapshot origin/facing khi cast; impact recheck target/range/LOS/alive/invulnerability. MP/CD/sequence một lần, không tính damage từ animation frame hoặc chạy toàn combo ngay khi nhận HTTP.

Mob ordinary có telegraph/attack/recovery, HP/death/life/respawn; clear-group respawn theo manifest, RETURN không phát death/loot. Hai actor tấn công đồng thời chỉ một death event/life, credit theo policy DEV đã nêu; không double-KILL. Hit/miss/immune/shield/crit values tách rõ, không cộng base crit hai lần nếu profile đã có0,0525. Oracle27/40 giữ đúng. RNG deterministic replay và audit, không dùng RNG âm thanh.

Spawn runtime phải mở đủ thành phần và số lượng từng nhóm theo manifest, có member ID ổn định, group ID và generation/life riêng. Projection 27 candidate của pha1 là fixture kiểm thử, chưa chứng minh đã sinh đủ mọi cá thể của tất cả nhóm. Kiểm một nhóm hỗn hợp, quái chết một phần rồi clear nhóm, và respawn đồng bộ đúng policy; không thay quantity của manifest bằng một entity đại diện nếu entity đó còn được target như một cá thể.

### QOD-18 — quest graph, inventory và XP đầu game

Compiler/export/runtime records P00-01..05 từ Quest Spec, manifest và narrative đã biên tập. Có TALK/INTERACT/explore/KILL/COLLECT/ESCORT/DEFEND theo từng objective/checkpoint thật. Đầu tiên chạy P00-01..03; tiếp hộ tống P00-04 và để P00-05 chờ boss QOD-19 nếu chưa đủ. Không báo quest chơi được từ một unlock ID chưa có definition.

Mỗi graph step có guard/event/map/floor/range/share/checkpoint, mapping text_key cũ; skip/replay/hết video không cấp progress/reward. Không sửa CSV logic hoặc230copy để hợp thức hóa code. Thầy macro chỉ resolve cho class đã hỗ trợ, unsupported class trả rõ; không invent NPC/target/cấp quái từ sprite.

Reward transaction gồm quest/inventory/currency/XP/level/ledger/idempotency tương ứng, fail không commit một phần. Snapshot XP khi accept, overflow/level100/multi-level/retry được kiểm. Stat migration versioned/refill một lần theo source, không silent đổi save/HP/MP; policy level-up HP chưa đủ nguồn thì proposal cụ thể. Inventory capacity/stack/equip dùng nguồn item, phần thiếu ghi blocker/candidate, không suy Attack từ tên kiếm. Phối hợp candidate compiler riêng của OpenCode, không ghi đè module của họ.

### QOD-19 — Mãng Cốt và kết thúc mở đầu

Hoàn thiện proposal dữ liệu encounter có phaseGuard/interruptible, reset/attempt, arena/safe-pad geometry và all numeric required. Rules §4 đã có3đòn, ưu tiênC→B→A, thresholds60%/30%, không overlap; dùng đúng nguồn và nêu từng field cần owner chốt. Không điền hồ sơ boss khác vào chỗ trống hoặc bật export mặc định cho blocked boss.

Trong lúc chờ field review làm state machine/tests với fixture gắn nhãn, không dừng gói. Sau duyệt nối telegraph/impact/phase/cancel/reset, wipe/reset không sinh loot; Mãng Cốt P00-05 → tương tác mảnh ấn → xác nhận class đã chọn → unlock chỉ khi tất cả guard đạt. Party scale không giảm HP để exploit khi người rời. Không gọi P00-05 hoàn tất khi boss vẫn invulnerable/unsupported.

### QOD-20 — E2E, client handoff và cổng persistence

Một command từ clone mới chạy default gate-OFF và dev-labelled scenario. Có vòng P00-01..05 theo subset đã chạy, nguồn numeric/content/protocol pin version, expected blocked output cho phần chưa supported. Thêm nhiều actor cạnh tranh package/node/kill, wrong floor/instance, retry/out-of-order/cancel/death/respawn, đầy túi/fail reward, reconnect cleanup và cursor overflow. Không dùng sleep dài để che race; fake clock/domain barrier cho timing, HTTP wait theo điều kiện có timeout.

Giao Codex example command/ack/event/snapshot, matrix implemented/fixture/blocked, lifecycle → VFX/audio, exact SHA/log/CI và lệnh replay. Có kịch bản nhiều client với quy mô/thời gian/giới hạn được ghi, không gọi là benchmark MMO production.

In-memory vẫn mất sau restart. Sau correctness của luồng trên, mở **proposal persistence PostgreSQL** theo Online spec: transaction inventory/quest/currency/XP/reward/idempotency/outbox, migrations và fault/restart test plan. Có thể dựng repository interfaces/fixtures độc lập; chưa triển khai DB live/auth/payment/market/PvP, không thay PostgreSQL bằng SQLite như thể production đã chốt. Không yêu cầu PC chủ repo cài Unity hoặc hạ tầng nặng để Qoder làm code/tests; dùng CI headless.

## 5. Nhịp bàn giao và ownership

Qoder sửa Server/contracts/runtime exporters/tests/workflows server và proposal/report tương ứng. Codex giữ client #51, audio adapter, design decisions và review/merge. Muse giữ art/map/VFX/cinema/Unity proof; OpenCode giữ asset pipeline và candidate compiler ở đường riêng. Lấy thoại230dòng mới từ main, không dùng baseline cũ làm dialogue nguồn.

Ngay khi nhận: comment #41 xác nhận cả gói, branch/checkpoint, stack dependencies và mốc bắt đầu. Mỗi PR có feature matrix, sources, commands/output, exact SHA, phần tiếp theo. Chờ review thì làm phần độc lập của mốc sau; không tự merge hoặc báo game hoàn chỉnh vì test green. Nếu thật sự hết phần độc lập, báo từng blocker bằng case/field/source cụ thể, không yêu cầu chủ giao lại cả gói.
