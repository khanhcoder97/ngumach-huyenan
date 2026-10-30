# Qoder local — QOD-18/19: hoàn thiện vòng chơi Bến Mưa

Issue epic mới: https://github.com/khanhcoder97/ngumach-huyenan/issues/87 . Milestone dùng `Refs #87` và cập nhật queue #41; chưa đóng epic khi chỉ sửa combat hoặc chạy hết P00-01.

Giao2026-10-30 theo yêu cầu chủ dự án kiểm tra tiến độ rồi giao tiếp. Nhận cả **Q-A→G**, triển khai liên tục qua nhiều milestone PR; không dừng sau ACK, proposal, một fix hoặc một PR. Issue điều phối gameplay vẫn #41, epic mới có link ở comment giao việc. Đọc report `Qoder_Progress_Review_20261030.md/.json` và hai negative evidence liên quan.

## Baseline và phạm vi

Latest reviewed Qoder #84: `4d959dd0473435c3bf7feea2877e1d5076d186d5`, base #78 `ed4898be621bd5e4e8603c0e5560ba239ef4d9b4`→#77→#75 và stack cũ. CI6/6,301self-check/440smoke có thật nhưng hai regression ngoài suite vẫn FAIL. Fix #76 `514c3f20c077175c7752706d845d11d78d464eda` chưa là ancestor; không tự coi đã hợp nhất.

Nhánh được cấp cho gói sau fixes: `qoder/qod-18-ben-mua-completion-20261030`, từ reviewed #84 cộng report/work order. Sửa correctness của #84 trên đúng nhánh/PR hiện tại trước, checkpoint rồi đưa fixes sang nhánh QOD18; không reset/clean/stash checkout root hoặc xóa hai ảnh untracked. PR tiếp theo target #84 nếu dependency chưa merge; ghi exact base/dependencies, retarget sau review có kiểm chứng. Không auto-merge whole stack.

Giữ quyền Qoder gameplay: `Server/Health/**`, contracts/schema/examples/runtime exporter/data có provenance, tests/workflow server và proposal/handoff thuộc gói. Không sửa client core/UI (Codex/Antigravity), Muse art/map/VFX/video, OpenCode `ContentPipeline`/asset tool/BuildCandidates, hoặc `Server/Persistence*` của QODER Remote. `Tools/ProducerReview/**` thuộc Codex, không sửa report/runner lịch sử để xóa finding. Lấy design quyết định mới từ main bằng fetch/read, không switch main mù giữa stack.

Nguồn bắt buộc: work order08/09, DEC016..023, Rules Complete, P1 Design Resolution, Runtime State and Catalog Precision, Guard Precision, Quest and Narrative Production Spec/edited dialogue, boss/encounter spec và manifest. Không dùng browser-demo stats/save làm production data. 349XY giữ original cùng TOPDOWN_REVIEW_REQUIRED, không tự REVIEWED để vượt gate.

## Q-A — correctness và tích hợp fix đã bàn giao

Đóng QREV01–05 bằng implementation+tests:

- Cached command replay sau END phải trả receipt cũ, không gọi lại scheduler, refresh guard, cấp +2, thêm END/hit/death/kill. Tích hợp #76 bảo toàn guard mới, hoặc giải pháp tương đương có full regressions. Không merge/cherry-pick mù làm mất code #84.
- Reserve key/hash/validation/cost/CD/sequence/revision/receipt dưới ownership nguyên tử; same/different payload concurrent phải đúng replay/conflict. Không chỉ dùng ConcurrentDictionary check trước lock. HP0 reject fresh cast; source chết/map/floor đổi trước hit phải CANCEL/END một lần, không damage/credit.
- Counter deadline: bắt case tick101→103 với counter due102. Bounded catch-up/overdue resolve hoặc cancel có lý do đúng một lần, không bỏ event hoặc resolve nhiều lần; pin ordering player hit/mob hit/counter/death và timestamps. Server tick phải được sample/advance nhất quán trong một iteration; test repeated tick và long stall, không sleep đoán race.
- Basic/MK03 impact recheck LOS/range/alive/life/instance/invulnerability theo contract, counter giữ no-retarget/no-refund. REVIEWED geometry fixture cho wall test, không sửa production review state.
- Guard DR→HP→survival→confirm/resource/revision/event dùng cùng impact/window ownership hoặc token để tránh fresh guard/move interleave làm DR của castA nhưng confirm castB. Barrier tests và source/frame/life provenance. Death/cancel không được thưởng whiff.

Một milestone correctness đủ lớn trên #84, exactSHA/lệnh/output và negative probes không còn FAIL ở head mới; report baseline vẫn giữ lịch sử. Chờ review thì tiếp data/proposals/tests phần độc lập dưới đây.

## Q-B — combat recovery và trải nghiệm sống/chết

Hoàn thiện MK02 swept movement không damage theo nguồn đã có, collision/stop reason/cancel/death/cost/retry; không gọi cast accepted là dash. Mob telegraph metadata/read projection phải có enough timing/target/shape để client đọc đòn khi có contract. Guard active/whiff/CD/resource và reconnect/resync snapshot cần versioned proposal/examples/capability thay vì dựa vào event đã trôi khỏi buffer. V1 và v2 strict hiện tại không bị thêm field lạ âm thầm; chờ approval phần wire thì làm read model/tests riêng, không chặn Q-C.

Death/respawn-return command: server kiểm dead state, safe anchor/map/floor/transition, cost/penalty theo nguồn, idempotency/lease; không chạy tự heal khi chỉ reconnect/equip. Thiếu anchor/penalty field thì ghi proposal cụ thể, làm DEV fixture có nhãn và gateOFF. Từ chối revive tại tọa độ client tự chọn; không reset quest/receipt/CD tùy tiện. Dọn cast/guard/counter/aggro/session refs khi chuyển map/death/logout đúng policy, có cancellation events và bounded cleanup.

Nối MobBehavior+CombatDamage trong **test profile riêng** và HTTP scenario conditional waits: đọc TELEGRAPH→ra khỏi vùng→miss, đứng lại→damage, bật guard→confirm/counter, source/defender chết→cancel. Không bật MobBehavior trong smoke cũ rồi sửa expected vô tội vạ; giữ default gatesOFF và fixture tách biệt.

## Q-C — đủ objective graph P00-01..05 và phần khám phá

Runtime records từ source đúng: prerequisite, steps, talk/interact/explore/collect/kill/escort/defend theo quest thật, target record IDs/map/floor/count/checkpoints/share/event keys, text refs, rewards và class-teacher mapping. Không gán mọi loại objective vào từng quest; dùng đúng loại được viết trong nguồn. OpenCode nhận candidate compiler; Qoder viết loader/adapter/validator runtime, không compiler cạnh tranh ghi BuildCandidates.

Đầu tiên làm P00-01..03; tiếp04..05 và điểm boss/fragment/class confirm. Tương tác narrative cần server-owned flags, reveal gates và event→objective mapping; đọc lore/khám phá/gặp NPC phải thực sự tiến mục tiêu khi source quy định, không chỉ đánh quái. Chọn class giữ class đã tạo; unsupported class/NPC trả rõ, không free respec. Text/230dialogues không tự thành objective graph. Missing numeric/ref là blocked activation có field/source, không default0.

Các test: duplicate/out-of-order progress, một event có thể đóng góp các objective hợp lệ riêng, sequential step guard, party policy chưa có giữ solo label, package per-character, node cooldown/count, wrong NPC/map/floor, quest prerequisites/cycle/dangling refs. Boss chưa active thì P00-05 giữ blocked ở đúng step, không unlock portal trước.

## Q-D — XP, level và stat/loadout không phát thưởng hai lần

Reward transaction gồm quest+inventory+currency+XP/level+ledger/idempotency tương ứng, fail rollback nguyên khối. XP snapshot/scale nguồn, level cap/multi-level/overflow/insufficient capacity/retry/concurrent đều có tests. Cập nhật receipt `xp.applied` chỉ true sau commit thực; client còn đọc field cũ phải được review compatibility. Không sửa response shape không version.

Load stat/profile/item numeric từ source có provenance/version/units/rounding; DEC023 alias armor/weapon_power/primary không cộng đôi. Khi maxHP/MP đổi do level/equip/respec: giữ current tuyệt đối rồi clamp, không tự heal/revive; migration refill là ngoại lệ một lần có version. Chuyển baseline fixture phải migration có notes, không silent đổi save. Missing fields cân bằng ghi ID/field/source và proposal tách biệt, không sao chép HP640/potion100/weapon26 từ browser demo.

## Q-E — loot/equipment dùng được, giữ tính nhất quán dữ liệu

PR #77 mới dry-run: giữ nguyên source eligibility/RNG/ledger audit, thêm grant orchestration có idempotency transaction và source life/group-generation semantics sau review. Killed/death/replay không roll/grant lại; RETURN/wipe/cancel không phát loot. Coin bands/gear roll vector chưa resolve thì grant candidate tương ứng OFF, không bịa giá trị. Inventory instance/stack/100slot, fullbag policy theo source, currency overflow và grant conflicts có tests.

Nối equipment read model và equip/unequip/use endpoints **chỉ cho cơ chế đã có dữ liệu**, với schema/example/version/proposal, owner/capacity/combat restrictions và expected revision/idempotency; báo Antigravity #85 contract packet. Không thêm cả market/mail/trade/guild/crafting trong gói này. Hành vi chưa có source phải unsupported rõ, không mutate mock state rồi gọi gameplay.

## Q-F — Mãng Cốt, kết thúc tuyến mở đầu và portal

Encounter proposal đủ arena/safe-pad/phaseGuard/interruptibility/attack selection/stats/loot/attempt/reset, giữ nguồn Rules §4 (3đòn, ưu tiênC→B→A, ngưỡng60%/30%, không overlap). Liệt kê field chưa chốt bằng case; không mượn boss khác/đánh tráo phase minion hoặc fixture numeric thành production approved.

State machine+deterministic fixture tests tiếp tục trong lúc chờ review. Khi config được duyệt, nối telegraph/impact/phase/cancel/wipe/reset, contribution/kill-ledger, fragment interaction→class confirmation→unlock portal đúng sequence. Party scale không giảm HP để exploit khi người rời; production party chưa có giữ unsupported/solo. Boss death/retry/late event không duplicate reward; wipe không loot; session recover/resync không hồi boss thành attempt mới hoặc unlock sớm.

## Q-G — E2E nhiều người, handoff và ranh giới persistence

Một command từ clone sạch chạy default gatesOFF và DEV labels, cùng 2client/scenario P00-01→05/boss/equip/portal khi phần đó thực executable; phần blocked phải fail/skip có lý do và feature matrix, không PASS cảcampaign sau mỗi P00-01. Có đối kháng package/node/kill/reward, delayed/lost/duplicate/out-of-order, death/dash/guard/map/floor/cursoroverflow và fullbag. Domain fake clock/barrier cho timing, HTTP conditional waits có timeout; không retry dài để che policy sai. Xuất examples/event meanings/timing cho Codex/Antigravity/Muse kèm exactSHA, source content version và logs.

**QODER Remote #79 giữ DB implementation** `Server/Persistence*`, schema/repos/migrations/identity ownership/leases/outbox/crash/restore. Remote chưa ACK thì nhắc issue và tiếp gameplay/data/tests trong phạm vi local, không viết DB thứ hai. Qoder local chỉ review interface/adapter request và nối Health sau module review; durable gatesOFF trước đó. SQLite prototype không tự thay PostgreSQL target/production deployment trong Online spec. Không gọi in-memory restart là persistence/relogin thành công.

Milestones: A correctness; B combat recovery; C quests+discovery; D/E XP/stat/reward/equipment; F encounter; G actual E2E+handoff. PR theo checkpoint đủ review, ghi dependency và tiếp module độc lập khi chờ; không tự merge, bật production flags hoặc tuyên bố game hoàn chỉnh. ACK issue ngay với branch/HEAD và mốc bắt đầu, cập nhật sau mỗi handoff thực.
