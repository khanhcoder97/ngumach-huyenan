# QODER Remote — QR-01: lưu trữ bền vững và khôi phục phiên

Issue nhận việc và bàn giao: https://github.com/khanhcoder97/ngumach-huyenan/issues/79 . PR milestone dùng `Refs #79`; epic chỉ đóng sau khi toàn bộ phạm vi đã nghiệm thu.

Nhận cả QR1→QR6, triển khai code/test thực và bàn giao GitHub. Branch `qoder-remote/qr-01-durable-state-20261030`, baseline main `8298c61058e5016f8a0fe86d3dd4a9b815596a49`. Đây là agent/máy khác với Qoder local đang làm #41/PR #75/#77/#78. Đọc work order09 trước.

## 1. Đích và ranh giới

Đóng phần nền tảng durable state của GAP-08: restart/relogin không mất/nhân inventory, currency, quest, receipt và event; identity/character ownership kiểm ở boundary. Qoder local nhận adapter vào gameplay sau review. Gói này phải có thư viện hoạt động và test qua DB thật, không chỉ schema, interfaces hoặc tài liệu.

Được tạo `Server/Persistence/**`, `Server/Persistence.Tests/**`, `Server/Persistence.Harness/**`; `Implementation/Work_Orders/Proposals/QR01_*`; `Implementation/Reports/QR01_*`; `docs/production/Qoder_Remote_Persistence_Handoff_vi.md`; workflow riêng `.github/workflows/qoder-remote-persistence.yml`. .NET10 theo repo. Pin dependency bằng project/lock file trong module; ghi license/version. SQLite qua provider .NET phù hợp cho single-host alpha, không hứa chịu MMO nhiều shard hoặc production CCU. Interface không khóa khả năng backend khác.

Không sửa `Server/Health/**`, các project/solution/CI của Qoder local, `Implementation/Contracts/P1/**`, canonical CSV/349XY, client, OpenCode compiler/tooling hoặc art. Có thể đọc code main và các branch Qoder để đề xuất adapter. Không cherry-pick toàn stack #53..78 hoặc fix #76 vào library; code baseline độc lập tránh trộn dependency chưa review.

Đọc `Online_Persistence_Release_Complete_vi.md`, `Production_Rules_Complete_v1_vi.md`, DEC-004/005/023, `Runtime_State_and_Catalog_Precision_vi.md`, audit20261030 và work order08. `Server/Health/World/ISessionStore.cs` hiện in-memory; `PlayerSession`, quest/inventory/reward stores là nguồn cấu trúc hiện có, không tự nhận đã durable.

## QR1 — schema, migration và repository hoạt động

Định nghĩa schema version và provenance: account/character ownership; character state/map/floor/position/current-max resources/class; inventory instances/slot/stack/version; currencies integer có overflow checks; quest state/objective/checkpoint; command receipts/reward ledger; session leases; outbox. Những thành phần progression chưa có source phải optional/unsupported rõ, không điền0 thành production balance. Không tạo ID canonical mới.

Migration có version/checksum và transaction, chạy lại idempotent; schema mới hơn runtime phải fail rõ, không auto downgrade/drop DB. Trước destructive migration cần export/backup plan và synthetic migration tests. Repository thực dùng DB trên file trong temp dir; không chỉ SQLite in-memory. Có constraints cho owner/slot/unique grant và optimistic revision; không chỉ trông vào mutex trong process.

## QR2 — unit of work và reward/command receipt nguyên tử

Một command hợp lệ commit cùng transaction: expected revision → mutation inventory/currency/quest → reward ledger → idempotency receipt → outbox. Same key+same normalized full payload trả đúng kết quả đã lưu sau restart; same key+khác operation/actor/NPC/target/payload phải conflict theo scope documented, không gộp nhầm người/quest/life. Receipt có schema/result/hash version; canonicalization không bỏ field có ý nghĩa. Không ghi token/raw credential vào payload/log.

Unique constraints/DB isolation phải chống hai process, không chỉ `ConcurrentDictionary` hoặc check-then-write. Failure injection test-only tại từng boundary: mọi state commit cùng nhau hoặc rollback cùng nhau. Full bag/overflow/revision conflict không grant một phần, quest còn READY, không xóa receipt của request khác. Mất response sau commit rồi retry bằng session mới cùng character không cấp thưởng lại. Ledger giữ quyền phát thưởng một lần riêng với session/transport retry cache; không dùng TTL receipt để cho phép reward lại.

Implement transaction coordinator tổng quát và harness application command với fixture rõ nhãn; không copy hoặc viết một quest/combat engine thay Qoder local. Liệt kê chính xác adapter calls mà Health cần thay sau review. Một test DB library không chứng minh endpoint Health đã persistent.

## QR3 — identity boundary và recovery lease

Tách verified account principal khỏi client-supplied characterId. Repository/command context kiểm ownership trước mọi read/write; test account A không đọc/sửa/attach character B. SessionId là handle, không mặc định là proof tài khoản. Định nghĩa abstraction cho identity provider; không tự nối OAuth/email/payment hoặc invent account production login.

Harness có thể dùng identity issuer giả TEST_ONLY qua DI, không public endpoint, không tự bật DEV auth trên production. Nếu cần resume secret/session credential cho prototype: random đủ mạnh, DB chỉ giữ digest, expiry/revocation/rotation và redacted logs; không hardcode khóa/token. Ghi threat/limit rõ và không gọi test issuer là production auth.

DEC-004 reconnect grace120giây; server UTC/clock injectable; lease có owner/fencing token/version để instance cũ không tiếp tục ghi sau takeover. Reconnect trong grace lấy cùng character durable state/cursor mapping phù hợp, không tạo bản clone nhân vật. Hết grace/revoke cần re-auth qua boundary đã định, không tự heal/max refill/reset item. Restore current HP/MP theo DEC023, giữ death state. Cross-map/floor state commit nhất quán; topology/portal authority vẫn thuộc Qoder local.

## QR4 — transactional outbox và event recovery

Outbox record có durable eventId/aggregateId/revision/order/source command và trạng thái delivery; được viết trong transaction QR2. Publisher retry có acknowledgement và crash recovery. Document delivery at-least-once và consumer dedupe; không hứa exactly-once delivery vì dùng outbox. Duplicate publish không tạo thêm receipt/reward.

Ordering theo aggregate, concurrent publishers có claim/lease/fencing hoặc transaction phù hợp. Test crash trước/sau publish/ack, expired claim, không bỏ event hoặc đảo revision. Không persist vô hạn v2 session cursor như replay log khi chưa có retention/epoch design; đề xuất reset/resync snapshot cho cursor cũ qua adapter. Không sửa wire v2 contracts âm thầm.

## QR5 — backup/restore, diagnostics và chạy từ clone sạch

CLI/harness localhost-only tạo DB synthetic, migration, seed fixture, apply mutation, restart/read, retry receipt, export sanitized evidence và backup/restore verify. Dùng SQLite backup API hoặc checkpoint/quiesce có kiểm chứng; không copy live DB bỏ WAL. Restore phải kiểm schema/version/integrity, row counts/digests/receipts/owner, có lỗi rõ và giữ bản gốc.

Không commit DB/WAL/SHM/backups thật, access token hoặc dữ liệu tài khoản cá nhân. Log có correlation/command hash/latency/error code, không secret. Có cấu hình đường dẫn DB, bounded busy timeout/retry, không vô hạn retry conflict; process hai writer test được. Script không xóa/migrate database bên ngoài temp dir nếu không có đường dẫn rõ và lệnh tương ứng. Không deploy public service hoặc mua hosting.

## QR6 — ma trận nghiệm thu và integration handoff

Tests phải chạy actual .NET library/provider và file DB, gồm:

1. Clean DB→migration→seed→read, migration rerun; checksum/schema mismatch và unsupported upgrade bị chặn không mất dữ liệu.
2. Concurrent same/different idempotency key, same/different payload/actor; dùng barrier hoặc subprocess phối hợp, không sleep đoán race. Hai process cùng grant một reward chỉ một durable ledger/mutation.
3. Full bag100slot, overflow, wrong owner, stale revision, dead actor restore và HP clamp; không grant một phần hoặc auto refill.
4. Kill harness process tại checkpoint test-only trước commit và sau commit trước response; restart đọc không half-write, retry không double grant. Rollback exception đơn thuần không thay crash test.
5. Session rotation/grace expiry/revoke/fencing old writer, outbox replay/order/ack crash; reconnect không mở character khác.
6. Backup/restore qua DB thật, including WAL-safe flow; compare state/ledger/outbox. Không khẳng định restore hoàn tất khi chỉ file exists.

CI chạy project độc lập, không đòi Unity hoặc service/cloud trả phí; giữ temp DB trong runner và cleanup chỉ trong thư mục test xác định. Ghi `dotnet restore/build/test` hoặc self-check commands/output thực tế, provider/runtime versions và evidence SHA. Thiếu khả năng chạy multi-process/crash phải báo UNVERIFIED, không đánh pass từ source regex.

Giao tối thiểu ba milestone PR: schema/repos+migrations; transactions/identity/session; outbox/recovery/restore+CI. PR đầu base main, PR sau có thể stacked rõ dependency. Kèm integration guide gọi từ Health: nơi hydrate/save/lease/transaction/error mapping, migration from in-memory chỉ fixture (không có save người thật để tự chuyển), feature flag mặc định OFF tới khi Qoder local/Codex review, rollback plan và các giới hạn single-host. Bàn giao issue #41 adapter request sau từng interface checkpoint; tiếp tục tests/module độc lập khi chờ phản hồi. Không tự merge hoặc gọi GAP-08 toàn game đã đóng trước integration/end-to-end evidence.
