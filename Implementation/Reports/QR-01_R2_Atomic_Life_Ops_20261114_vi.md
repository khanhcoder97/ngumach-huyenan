# QR-01 R2 — atomic life/return, poison outbox, ownership và ops/benchmark

Ngày 14/11/2026. Tiếp checkpoint R1 trên cùng nhánh
`qoder-remote/qr-01-r1-buildable-20261114`, PR #132. Người nhận vai trò Qoder Remote:
OpenCode. Không chạm `Server/Health`, client, contracts, canonical XY hoặc art; không bật
feature gate; production target vẫn là PostgreSQL OnlineSpec.

## 1. Phạm vi checkpoint

Checkpoint này gom phần độc lập của R2, R3, R4, R6, R7 (DTO/interface) và R8 (ops/benchmark)
chưa có ở R1. Không tuyên bố R9 hay tích hợp Health.

| Yêu cầu | Trạng thái |
| --- | --- |
| State + revision + receipt + ledger + outbox một transaction | Đã có từ R1, giữ nguyên |
| Life/death/return before/after snapshots, full result, global key | **MỚI — IMPLEMENTED + TESTED** |
| Death giữ life version; return tăng đúng một lần; stale life bị từ chối | **MỚI — TESTED** |
| Tombstone không bị coi là Missing hoặc lệnh mới | **MỚI — TESTED (read-side)** |
| Principal account phải sở hữu character ở command và lease | **MỚI — TESTED** |
| Outbox poison: retry budget + dead-letter bền vững | **MỚI — TESTED** |
| Hai process: lease hết hạn, takeover, writer cũ bị stale | **MỚI — TESTED bằng subprocess thật** |
| 10.000 replay không tăng life/item/currency/receipt | **MỚI — TESTED** |
| 300 receipt khác không làm mất key return cũ | **MỚI — TESTED** |
| Migration v1→v3, checksum/future version fail closed | **MỚI — TESTED** |
| Readiness/metrics có redaction | **MỚI — IMPLEMENTED + TESTED** |
| Benchmark commit/replay/outbox/contention có cấu hình | **MỚI — MEASURED** |
| Disk-full / IO-denied / ACL-denied | **UNVERIFIED** — không có môi trường cô lập |
| PostgreSQL provider | **NOT IMPLEMENTED** — giữ mục tiêu production |
| Nối Health/gameplay, bật gate | **KHÔNG LÀM** — chờ Codex review |

## 2. Thay đổi chính

- `Server/Persistence/Migrations.cs` — schema v3: `life_state`, `life_receipts`; giữ
  `outbox.dead_at` của v2. Upgrade từ v1 chạy tuần tự v2→v3, dữ liệu cũ còn nguyên.
- `Server/Persistence/LifeReceipts.cs` — DTO theo QOD-25 §7 (`PlayerDeathSnapshot`,
  `LifeSnapshot`, `DeathReturnResultSnapshot`, `LifeReturnCommit`, `LifeTransition`,
  `ReturnLookupKind`, `ReturnLookup`), interface đọc `ILifeReceiptAdapter` và store
  `LifeReceiptStore`. Không tham chiếu executable Health.
- `Server/Persistence/Contracts.cs` — `MutationPlan.Life` để life transition đi cùng
  transaction/cas/fencing của unit of work.
- `Server/Persistence/DurableUnitOfWork.cs` — ghi life transition trước commit; stale life
  trả `RevisionConflict` + `life-version-conflict` và rollback toàn bộ command.
- `Server/Persistence/OutboxDispatcher.cs` — batch bounded, retry backoff có trần,
  dead-letter sau attempt budget; chỉ ghi loại lỗi, không ghi payload.
- `Server/Persistence/OutboxStore.cs` — `DeadLetterAsync`, `GetDeadLetterCountAsync`,
  `ReadDeadLettersAsync`, loại dead-letter khỏi claim/ack/retry.
- `Server/Persistence/IdentityStore.cs`, `LeaseStore.cs`, `DurableUnitOfWork.cs` — kiểm
  `PrincipalAccountId` khớp account sở hữu character.
- `Server/Persistence/Diagnostics.cs` — `PersistenceLimits`, `ProviderMigrationStatus`,
  `PersistenceReadiness`, `PersistenceMetrics`, `PersistenceDiagnostics`; output chỉ có
  count/version/tuổi outbox, không có payload/id/token.
- `Server/Persistence/Domain/DomainAdapters.cs` — capability registry + version cho
  inventory/quest/XP/currency/loot/equipment/consume/stat/craft/mail/trade/guild/rank,
  life/death/return, attempt/activation/reset; handler chưa có trả
  `unsupported-capability`.
- `Server/Persistence.Harness/Program.cs` — thêm `hold-lease-then-commit` (hai process
  stale-owner) và `benchmark` (commit/replay/outbox/contention, xuất JSON).
- Tests mới: `LifeReceiptTests`, `OutboxDispatcherTests`, `DiagnosticsTests`,
  `DomainAdapterTests`; bổ sung principal ownership, v1→v3 migration, stale-owner
  subprocess, backup thiếu/hỏng, restore đè target.

## 3. Bằng chứng chạy thật (TESTED)

Môi trường: Windows 10.0.19045, 4 logical processor, .NET SDK `10.0.404`, runtime
`10.0.15`, `Microsoft.Data.Sqlite 10.0.0`, `SQLitePCLRaw.lib.e_sqlite3 2.1.13`.

```text
dotnet build Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release
  Build succeeded. 0 Warning(s), 0 Error(s)

dotnet test Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release
  Passed! - Failed: 0, Passed: 70, Skipped: 0, Total: 70, Duration: 1 m 8 s
```

70 test dùng file SQLite thật trong thư mục temp riêng cho từng test. Cleanup chỉ xóa đúng
thư mục con do test tạo; không quét `%TEMP%`.

Clean-clone từ `git archive HEAD` (source `dc039b0aa07bb522edc2ee7e00520e118f44a676`):

```text
dotnet restore ... --locked-mode
  Restored 3/3 projects
dotnet build ... -c Release --no-restore
  Build succeeded. 0 Warning(s), 0 Error(s)
dotnet test ... -c Release --no-build --logger "trx;LogFileName=clean-r2.trx"
  Passed! - Failed: 0, Passed: 70, Skipped: 0, Total: 70, Duration: 1 m 8 s
```

TRX: `clean-r2.trx` trong thư mục kết quả của bản clean-clone.

Nhóm bằng chứng quan trọng:

- `DeathAndReturn_CommitLifeProvenanceAtomically` — life 1 chết, return lên life 2; lưu
  before/after + toàn bộ `DeathReturnResultSnapshot` (HP/MP/map/tick/cleanup/death id).
- `ReturnReplay_ReturnsHistoricalResultWithoutAdvancingLife` — replay trả đúng result cũ,
  life vẫn 2, không thêm receipt.
- `ReturnKey_IsGlobal_OtherOwnerConflicts` — owner khác dùng cùng key bị `OwnerConflict`.
- `StaleLifeSnapshot_IsRefusedAndRollsBackTheWholeCommand` — state/receipt/outbox/life đều
  không đổi khi life version lệch.
- `Tombstone_IsNotMissingAndNotAFreshCommand` — tombstone trả `Tombstoned`, không `Missing`.
- `OldReturnKey_InLaterLife_StillReplaysHistoryAndDoesNotHeal` — key đời 1 khi đang ở đời 3
  chỉ replay lịch sử.
- `ThreeHundredOtherReceipts_DoNotExpireAnOldReturnKey` — 300 receipt khác không làm mất key.
- `TenThousandReplays_DoNotChangeLifeOrGrantAgain` — 10.000 replay, counts không đổi.
- `ExpiredLease_NewOwnerCommits_OldOwnerIsRefusedAsStale` — process cũ giữ fencing 1 quá
  TTL 200 ms; process mới takeover fencing 2 commit trước; process cũ bị
  `StaleFencingToken`, receipt cũ không tồn tại.
- `DeadLetterOutbox_IsDegradedButDatabaseStillReady` — poison outbox bị dead-letter, DB vẫn
  `Ready`, `Degraded=true` với lý do `dead-letter-outbox-present`.
- `Metrics_ContainCountsButNoPayloadsOrIdentifiers` — JSON metrics/readiness không chứa
  token, character id, key hay payload.

## 4. Benchmark đo được (MEASURED)

Lệnh (DB tạm, xóa sau khi đo):

```text
benchmark --db <temp>/bench.sqlite --character bench-hero \
  --iterations 200 --replays 2000 --concurrency 4 --contention-iterations 50
```

Kết quả JSON thật:

```json
{"mode":"benchmark","hardware":{"os":"Microsoft Windows 10.0.19045","architecture":"X64","processorCount":4,"dotnet":"10.0.15"},"database":{"schemaVersion":3,"sizeBytes":368640,"walBytes":0,"busyTimeoutMs":10000},"config":{"iterations":200,"replays":2000,"concurrency":4,"contentionIterations":50},"commit":{"count":200,"p50Ms":9.586,"p95Ms":12.946,"p99Ms":15.145,"maxMs":85.597,"totalMs":1995.38},"replay":{"count":2000,"p50Ms":5.022,"p95Ms":10.687,"p99Ms":15.388,"maxMs":29.783,"totalMs":11606.26},"outbox":{"applied":200,"totalMs":7159.85},"contention":{"count":200,"p50Ms":37.706,"p95Ms":136.844,"p99Ms":165.522,"maxMs":255.36,"totalMs":10749.8},"contentionErrors":0,"errors":0}
```

Đọc đúng phạm vi: đây là benchmark một máy dev, DB 360 KiB, 4 process/task tranh nhau trên
cùng file; không phải capacity production, không phải PostgreSQL. Fencing, `synchronous=FULL`
và receipt path không bị tắt để có số đẹp. Latency tăng dưới contention là chi phí SQLite
single-writer thật, không phải lỗi mất dữ liệu (`contentionErrors=0`).

## 5. Chưa xác minh / giới hạn (UNVERIFIED)

- Disk-full, IO-denied, ACL-denied và partial-write: chưa có môi trường cô lập; không tuyên bố.
- Crash giữa migration: mới có transaction + checksum + fail-closed, chưa có test kill đúng
  điểm migration; runbook production chưa viết.
- Tombstone/expiry: library chỉ đọc tombstone, **không tự tạo** vì chưa có expiry được duyệt.
  Chưa reclaim receipt cũ; đúng yêu cầu "tombstone không phải Missing".
- Rate-limit quota, auth edge và PostgreSQL provider thuộc packet/owner khác.
- Health chưa gọi library; library PASS không chứng minh Health durable.
- Benchmark chưa chạy trên PostgreSQL hoặc nhiều máy; số trên chỉ là dev profile.

## 6. Bước tiếp theo trên cùng nhánh

1. Fault injection có kiểm soát cho IO-denied/disk-full (Windows ACL trong thư mục test
   riêng) và migration crash, ghi rõ nếu môi trường không cho phép.
2. Gói interface/DI cho Codex + Qoder local review transaction boundary của adapter.
3. Chỉ sau review mới nối Health sau feature gate OFF; chạy restart HTTP và chứng minh
   quest/reward/death/return không double grant.

Không merge PR #132, không force-push PR #98, không bật production gate.

## 7. Exact SHA

- Source checkpoint R2: `dc039b0aa07bb522edc2ee7e00520e118f44a676`
  (`feat(qr-01): atomic life/return receipts, poison outbox and ops surface [R2]`).
- Nhánh: `qoder-remote/qr-01-r1-buildable-20261114`, PR #132 (Refs #79, #98).
- Commit report này là commit kế tiếp trên cùng nhánh; CI GitHub chạy lại đúng project test.

