# QR-01 R1 — bàn giao checkpoint build/test được (Qoder Remote)

Ngày 14/11/2026. Người nhận vai trò: OpenCode thay Qoder Remote tại issue #79.
Nhánh mới tách từ `origin/main`, không sửa nhánh Qoder local/Codex/Antigravity và không
force-push PR #98.

> Checkpoint tiếp theo: `QR-01_R2_Atomic_Life_Ops_20261114_vi.md` (life/return receipt,
> poison outbox, ownership, readiness/benchmark). Các mục "chưa làm" dưới đây là trạng thái
> tại R1, không phải trạng thái hiện hành.

## 1. Trạng thái Qoder Remote trước khi bàn giao

- PR #98 giữ nguyên head `5371a4675fbd8fc4b41b4748f2b1732ef2d81824`; không có commit mới
  sau 03/11/2026.
- Trong tree của head đó **không có** `csproj` cho library/test/harness được track.
  Các file `.csproj` nhìn thấy trên máy là file local bị `.gitignore` (`*.csproj`) che,
  không nằm trong commit.
- Workflow `qr-01-ci.yml` trỏ tới project không tồn tại, dùng `needs: deploy-preview`
  không tồn tại, và job summary đọc `job.status` của chính nó.
- Báo cáo cũ tuyên bố "24/24 test", "production-ready" nhưng không có TRX/CI tương ứng.
- Kết luận: Qoder Remote dừng ở trạng thái chờ bàn giao R1; các tuyên bố hoàn tất trước đó
  không có bằng chứng.

## 2. Phạm vi checkpoint này

Làm lại R1 bằng một module độc lập, build được từ clone sạch:

| Project | Nội dung |
| --- | --- |
| `Server/Persistence` | Library net10.0: migrations, identity, lease/fencing, unit of work, outbox, backup/recovery |
| `Server/Persistence.Tests` | 42 test xUnit trên file SQLite thật, gồm crash subprocess |
| `Server/Persistence.Harness` | CLI nhỏ để test kill trước/sau commit và tranh lease giữa hai process |

Không chạm `Server/Health`, client, contracts, canonical XY, art. Không bật feature gate.
Không tuyên bố Health đã durable.

## 3. Những gì đã làm (IMPLEMENTED)

- Schema v1 có version/checksum; migration idempotent; checksum bị sửa hoặc version tương
  lai thì fail closed.
- Unit of work một transaction `BEGIN IMMEDIATE`: state + expected revision + receipt
  (request hash + result hash + result) + ledger + outbox.
- Idempotency key toàn cục: replay cùng key/payload trả đúng kết quả lịch sử; khác payload
  hoặc khác owner là conflict; không tạo grant mới.
- Planner thuần chạy trong transaction; `Reject`/`CapacityExceeded` không ghi gì.
- Lease DB với fencing token tăng dần, reconnect grace 120 giây, stale token bị từ chối
  khi commit.
- Outbox claim theo thứ tự id, claim TTL, retry/backoff, ack, cursor theo consumer;
  `ApplyOnce` ghi dedupe cùng transaction với hiệu ứng.
- Backup dùng SQLite backup API, verify integrity/schema/count, manifest SHA-256; restore
  verify lại; từ chối backup hỏng/truncated/digest sai.
- Recovery kiểm WAL checkpoint, integrity, foreign key và pending outbox thật.
- CI riêng `.github/workflows/qr-01-ci.yml` restore `--locked-mode`, build, test, upload
  TRX, cleanup thư mục temp có giới hạn (không wildcard biến rỗng).

## 4. Bằng chứng chạy thật (TESTED)

Môi trường: Windows, .NET SDK `10.0.404`, SQLite bundled qua `Microsoft.Data.Sqlite 10.0.0`.

```text
dotnet restore Server/Persistence.Tests/Server.Persistence.Tests.csproj
dotnet build Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release
dotnet test  Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release \
  --logger "trx;LogFileName=qr01.trx"
```

Kết quả:

```text
Passed! - Failed: 0, Passed: 42, Skipped: 0, Total: 42, Duration: 15 s
```

Các nhóm test: migration/checksum (6), unit of work/replay/conflict/lease fencing (10),
lease (8), outbox (6), backup/recovery (7), subprocess crash/lost-response/hai process/churn
300 nhân vật (5).

Test dùng file DB thật trong thư mục temp duy nhất cho từng test; cleanup chỉ xóa đúng
thư mục con do test tạo, không quét `%TEMP%`.

## 5. Chưa xác minh / chưa làm (UNVERIFIED / NOT IMPLEMENTED)

- Disk-full, IO-denied/ACL-denied: chưa có môi trường cô lập để chứng minh; chưa tuyên bố.
- Benchmark latency/contention/percentile có cấu hình: chưa chạy.
- PostgreSQL provider: giữ nguyên mục tiêu production, chưa triển khai trong checkpoint này.
- Adapter inventory/quest/XP/life/death/return và nối Health: R7, chờ Codex review module.
- QOD-25 §7 DTO: mới là input thiết kế, chưa đưa vào library (tránh phụ thuộc ngược
  executable Health).

## 6. Bước tiếp theo

R2–R6 đã có phần lõi trong checkpoint này (transaction/receipt/outbox/fencing/crash/backup).
Các phần còn thiếu sẽ làm tiếp trên cùng nhánh: migration nâng cấp/thử rollback, fault
injection có kiểm soát, benchmark, adapter DTO và gói interface gửi Codex/Qoder local sau
review.

## 7. Exact SHA và clean-clone

- Source checkpoint: `e3cc38b9fbda3d16426a56c2fd53c35709a8a4b4`
  (`feat(qr-01): deliver buildable persistence library, tests and harness [R1]`).
- Nhánh: `qoder-remote/qr-01-r1-buildable-20261114`, tách từ `origin/main`.
- Clean-clone: `git archive --format=zip HEAD` → thư mục trống, sau đó:

```text
dotnet restore Server/Persistence.Tests/Server.Persistence.Tests.csproj --locked-mode
  Restored 3/3 projects
dotnet build ... -c Release --no-restore
  Build succeeded. 0 Warning(s), 0 Error(s)
dotnet test  ... -c Release --no-build --logger "trx;LogFileName=clean.trx"
  Passed! - Failed: 0, Passed: 42, Skipped: 0, Total: 42, Duration: 17 s
```

- Toolchain: .NET SDK `10.0.404`, Windows, `Microsoft.Data.Sqlite 10.0.0` +
  `SQLitePCLRaw.lib.e_sqlite3 2.1.13` (ghim để tránh GHSA-2m69-gcr7-jv3q).
- TRX: `clean.trx` sinh trong thư mục kết quả của bản clean-clone; CI sẽ upload artifact
  `qr01-persistence-results` khi workflow chạy trên GitHub.

