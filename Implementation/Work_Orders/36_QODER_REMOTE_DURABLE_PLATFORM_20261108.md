# Qoder Remote — QR-01→03: durable state đến restart integration

Owner Qoder Remote, issue #79, PR #98/nhánh qr-01 hiện có. Head5371a46 chưa có source hoặc ACK mới của Remote. Nhận toàn R1–R9; không chuyển client/art hoặc đổi model/auth. Artifact QOD25§7 từ Qoder local là đầu vào thiết kế, không phải Remote đã nhận việc.

## R1 — repository build được trước

Track csproj library/test/harness, dependency versions/lock/license và ignore whitelist đúng path. Library/DTO phụ thuộc một chiều, không tham chiếu ngược executable Health.NET10. Từ clone sạch phải restore/build/test thật, TRX total>0, workflow dùng đúng project. CI server chung không là DB PASS. Giao source đầu sớm, không chỉ report; thiếu tool/network thì ACK lệnh và lỗi cụ thể tại #79.

## R2 — transaction nguyên tử

State + expectedRevision + full receipt(request hash/result) + ledger + outbox trong một DB transaction/CAS. Không mutate domain xong rồi append DB callback và gọi crash-safe. Key namespace/owner/operation/version và canonical serialization rõ; cùng key khác body/owner phải conflict, replay giữ kết quả lịch sử.

Capacity refusal không là success commit. Death-loot retry giữ roll decision. Full life/death/return before-after snapshots theo QOD25§7; global key không được chuyển thành fresh command ở đời sau. Tombstone không là Missing. Chưa có expiry duyệt thì chưa reclaim nghĩa vụ; không giảm30ngày thành256entry hoặc tăng RAM rồi gọi durable.

## R3 — identity/lease/fencing

Character/account/session ownership, reconnect120s theo source, fencing token và stale-owner refusal. Hai process thật cùng DB tranh key/state/lease; worker mất lease không được commit muộn. Clock điều khiển được cho expiry, process boundary cho DB races; không sleep dài để đoán. Auth edge cấp identity, không lấy characterId client làm quyền production.

## R4 — crash, restart, outbox

Kill process trước/giữa transaction, sau commit trước reply; lost response rồi restart và replay. Outbox write/claim/retry/ack/dedupe/cursor/checkpoint durable. Consumer crash sau effect trước ack không tạo reward/activation thứ hai. Poison-job/recovery có policy và bounded work.

Kiểm lifeVersion/deathId qua300character churn, nhiều đời và restart; key return cũ không heal đời mới.10.000 replays phải không tăng item/currency/XP/life, không thay bằng GET hoặc in-memory mock. Báo capacity/retention thật, không tự đặt TTL.

## R5 — provider và migration

Giữ production target theo OnlineSpec, không tự đổi PostgreSQL thành SQLite. SQLite chỉ là profile dev/test đã ghi rõ. Track schema versions/index/uniqueness/serialization và upgrade/rollback compatibility. Crash giữa migration phải recover hoặc fail closed có runbook; không bỏ dữ liệu để boot.

## R6 — backup/restore/fault handling

SQLite dùng backup API hoặc quiesce WAL, không copy DB đang WAL. Production provider có runbook tương ứng. Kiểm integrity thật, corrupt/truncated backup, IO denied/disk full/partial write và duplicate restore. Restore state/receipt/outbox cùng cut; không state mới/ledger cũ. Path/PID cleanup giới hạn đúng workspace, không secret và không return-true placeholder/reflection private handle.

## R7 — domain adapters

Giao DTO/interface/capability version cho inventory/quest/XP/currency/loot/equipment/consume/stat/craft/mail/trade/guild/rank, life/death/return, attempt/activation/reset buckets. Handler chưa có vẫn unsupported. Qoder local review transaction boundary trước khi nối Health; DB await/cancellation/unknown commit không được deadlock actor lock.

## R8 — ops, dependencies và performance

Metrics/audit redaction, retry budget, bounded queues, pool limits, configuration/health/readiness/provider migration status. Benchmark commit latency/contention/replay/outbox có hardware/load/DB size/percentiles; không bỏ fencing/durability để đẹp số. Rate-limit identity/units thuộc API packet, không mượn quota chat. Dependencies/version/license được tracked, không dump credentials vào evidence.

## R9 — tích hợp sau review

Checkpoints: buildable source → atomic basic → two-process/crash/outbox → migration/restore → adapters → ops/package → Codex review và Qoder nối feature gate → public HTTP restart. Default production OFF, không tự sửa Health hoặc merge PR98. Library PASS chưa chứng minh Health durable; restart quest/reward/death/return phải giữ identity/receipts và không double grant.

Push source, commands/TRX/CI/raw process logs và failure matrix ở mỗi checkpoint rồi tiếp phần độc lập. R1 là đường găng, không cần chờ gameplay/cinematic mới tạo project/test module.