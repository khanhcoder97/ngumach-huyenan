# QR-01 R3 — migration/restore fault handling và gói handoff (R5–R9)

Ngày 14/11/2026. Tiếp checkpoint R2 trên cùng nhánh
`qoder-remote/qr-01-r1-buildable-20261114`, PR #132. Không sửa `Server/Health`, client,
contracts, canonical XY, art; production gate OFF; không merge PR #132/#98.

## 1. Phạm vi và trạng thái work order 36

| Mốc | Trạng thái | Bằng chứng |
| --- | --- | --- |
| R1 buildable source | **DONE** (R1) | clean clone 42/42, CI xanh |
| R2 transaction/receipt/ledger/outbox + life/return | **DONE** (R2/R3) | 77 test, life receipt + 10.000 replay |
| R3 identity/lease/fencing hai process | **DONE** | principal ownership + stale-owner subprocess |
| R4 crash/restart/outbox poison | **DONE** | kill trước/sau commit, dead-letter, 300 life churn |
| R5 migration/upgrade | **DONE (dev profile)** | v1→v3, failed migration rollback, future/checksum fail-closed |
| R6 backup/restore/fault | **DONE (IO-denied); disk-full/ACL UNVERIFIED** | locked target giữ nguyên DB, staged restore |
| R7 adapter DTO/interface/version | **DONE (interface checkpoint)** | registry 17 capability; handler unsupported |
| R8 ops/benchmark | **DONE** | readiness/metrics redacted + benchmark JSON |
| R9 Codex review → Health feature gate → HTTP restart | **BLOCKED — chờ review bên ngoài** | handoff guide đã giao; không tự sửa Health/gate |

## 2. Thay đổi checkpoint này

### R5 — migration fail-closed

- `FailedMigration_RollsBackEveryPendingStepAndKeepsV1Data`: tạo DB v1, cố tình có
  `life_state` trước để v3 fail sau khi v2 đã chạy trong cùng transaction. Kết quả: schema
  vẫn 1, account/character v1 còn nguyên, không có cột `dead_at`, không có receipt.
- `Upgrade_FromV1_AppliesV2AndV3AndKeepsExistingData`: upgrade tuần tự, kiểm cả `dead_at`
  và hai bảng life.
- Checksum bị sửa / version tương lai vẫn fail closed (test cũ giữ nguyên).

### R6 — restore không phá bản gốc

- Restore đổi sang **staged swap**: copy backup vào `<target>.restore.tmp`, verify, mới
  chuyển target cũ sang `<target>.restore-old`, publish temp, verify lại, rồi xóa bản cũ.
  Nếu bất kỳ bước swap/verify nào lỗi, target cũ được đưa lại; temp luôn được dọn.
- `Restore_WhenTargetIoIsDenied_KeepsExistingDatabaseIntact`: trên Windows giữ file target
  bằng `FileStream(FileShare.Read)`; trên Linux/macOS share mode chỉ là advisory nên test
  chmod thư mục target thành read-only (giữ lại mode cũ trong `finally`). Restore bị từ chối,
  DB cũ vẫn đọc được state/receipt, không còn `.restore.tmp`/`.restore-old`.
- `Backup_WhenSourceIoIsDenied_PublishesNothing`: trên Windows khóa source
  (`FileShare.None`); trên Linux/macOS chmod file DB thành `None`, sau đó trả mode cũ.
  Backup fail, không tạo file backup/manifest/tmp.
- `Restore_SameBackupTwice_IsRepeatable`: restore hai lần cho cùng hash/counts/state.
- Backup đè file cũ dùng `File.Move(overwrite)` sau khi file mới đã verify, không xóa bản cũ
  trước khi có bản thay thế.
- `BackupRecoveryTests.Restore_ReplacesExistingTargetDataAtomically` kiểm thêm không còn
  file tạm.

### R3 — đọc có kiểm quyền

- `PersistenceDatabase.ReadStateAsync(characterId, principalAccountId)` và
  `ReadReceiptAsync(key, principalAccountId)` join `characters.account_id`; trả `null` cho
  cả "không tồn tại" và "không sở hữu" để không lộ character của account khác.
- Test: account-1 đọc được state/receipt của mình; account-2 nhận `null`; character lạ cũng
  `null`.

### R4 — churn nhiều đời + restart

- `ExpiredLease_NewOwnerCommits_OldOwnerIsRefusedAsStale` bỏ `Task.Delay` cố định: harness
  ghi `--ready-file` sau khi acquire lease, test đọc DB chờ đúng `ExpiresAt` của lease hết
  hạn, rồi process thứ hai takeover/commit, cuối cùng test ghi `--barrier` để process cũ thử
  commit. Kết quả stale fencing là tất định, không phụ thuộc tốc độ khởi động máy.
  Đây là sửa lỗi CI Linux (2 test IO-denied fail vì share mode của Unix chỉ advisory; và
  takeover chạy trước khi lease 200 ms hết hạn nên nhận `LeaseHeld`; xem mục 3).

- `DeathLootReceipt_ReplayKeepsRollAndDoesNotDoubleGrant`: death có loot ledger/outbox; replay
  không roll lại, ledger/outbox/life không đổi.
- `ThreeHundredCharacters_MultipleLivesAndRestart_DoNotReuseOldKeys`: 300 nhân vật, mỗi
  nhân vật một death + một return (life 1→2), sau đó mở lại DB bằng object mới; key return
  của nhân vật gốc vẫn chỉ replay lịch sử, life không tăng; `life_receipts` = 301.

### R7/R9 — handoff

- `docs/production/Qoder_Remote_Persistence_Handoff_vi.md`: mapping call Health → library,
  transaction boundary, error mapping, feature-gate/rollback, giới hạn single-host,
  checklist review và lệnh kiểm chứng.
- Không tạo writer thứ hai; commit life/return vẫn đi qua `MutationPlan.Life` trong unit of
  work. Handler gameplay chưa có trả `unsupported-capability`.

## 3. Bằng chứng chạy thật

Môi trường: Windows 10.0.19045, 4 logical processor, .NET SDK `10.0.404`, runtime `10.0.15`.

```text
dotnet build Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release
  Build succeeded. 0 Warning(s), 0 Error(s)

dotnet test Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release
  Passed! - Failed: 0, Passed: 77, Skipped: 0, Total: 77, Duration: 2 m 3 s
```

TRX: `C:\Users\khanh\AppData\Local\Temp\opencode\qr01-results-r3\qr01-r3.trx`
(không commit TRX; CI upload artifact riêng).

Clean-clone tại `87c61bd4cb1fe1bec3f75ac4776af06e021e222c` (export `git archive`, không
dùng working tree): restore `--locked-mode`, build **0 warning/0 error**, test **77/77
passed** trong 1 m 22 s.

Lịch sử CI Linux:

- Commit `97af4ec3` — QR-01 CI fail 2 test IO-denied vì `FileShare` trên Unix chỉ là
  advisory; 75/77 pass.
- Commit `df9b01fb` — IO-denied đã chuyển sang chmod; IO-denied pass, nhưng stale-fencing fail
  vì takeover chạy trước khi lease 200 ms hết hạn (`LeaseHeld`, exit 10).
- Commit `87c61bd4` — test chờ đúng `ExpiresAt` trong DB trước takeover; **cả hai QR-01 CI
  run đều success**: `43475921557` và `43475909049`, log hiển thị
  `Passed! - Failed: 0, Passed: 77, Total: 77, Duration: 10 s`.
  TRX artifact của run `43475921557`: `total=77, passed=77, failed=0`.

Lưu ý vận hành: trong lúc chạy test lần đầu, ổ C hết chỗ do các bản clean-clone tạm trước đó;
test dừng với `IOException: There is not enough space on the disk` tại `TempWorkspace.Create`.
Đã xóa đúng các thư mục tạm do mình tạo (`ngumach-qr01-tests`, `opencode\qr01-clean*`,
`opencode\qr01-ci-*`, `ngumach-qr01-bench-*`), không xóa ngoài các path đó; chạy lại đạt
77/77. Đây **không** phải test disk-full có kiểm soát, nên disk-full vẫn UNVERIFIED.

## 4. Chưa xác minh / blocked

- **R9 blocked:** cần Codex review gói interface và Qoder local nối adapter sau feature gate;
  sau đó mới chạy restart HTTP thật. Không thể tự review/tự merge hoặc sửa `Server/Health`
  trong checkpoint này.
- Disk-full và ACL-denied: chưa có môi trường cô lập; IO-denied đã test bằng file lock trên
  Windows và chmod trên Unix (CI Linux), không phải disk-full.
- Crash kill đúng điểm migration: mới mô phỏng bằng DDL fail trong transaction.
- Tombstone expiry/reclaim chờ quyết định expiry; không giảm 30 ngày thành capacity.
- PostgreSQL provider, rate-limit quota, auth edge: ngoài module này.
- Benchmark chỉ trên máy dev single-host; xem R2 report.

## 5. Bước tiếp theo sau review

1. Codex/Qoder local trả lời checklist trong handoff guide.
2. Nếu approved: nối Health sau gate OFF, chạy restart HTTP cho quest/reward/death/return.
3. Chỉ khi có acceptance HTTP + review mới đóng R9/GAP-08 phần persistence.

Không merge PR #132, không force-push PR #98, production gate vẫn OFF.
