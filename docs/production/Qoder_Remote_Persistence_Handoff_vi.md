# Qoder Remote — QR-01 persistence handoff cho Health (R7–R9)

Ngày 14/11/2026. Tài liệu này là **gói interface/DI để Codex và Qoder local review**, không
phải tích hợp đã chạy. Library đã pass test trên file SQLite thật, nhưng **chưa nối
`Server/Health`** và **chưa chứng minh Health durable**. Production gate vẫn OFF.

- Module: `Server/Persistence`, `Server/Persistence.Tests`, `Server/Persistence.Harness`
- Nhánh: `qoder-remote/qr-01-r1-buildable-20261114`, PR #132
- Issue: #79 (Refs #98)
- Provider dev/test: SQLite single-host. Production target: PostgreSQL OnlineSpec, chưa làm.

## 1. Ranh giới trách nhiệm

| Việc | Owner |
| --- | --- |
| Account/character mapping bền vững, lease/fencing, transaction, receipt, ledger, outbox, backup | Library QR-01 |
| Quyết định gameplay (damage, loot roll, quest transition, return formula) | Health/Qoder local |
| Auth edge cấp `principalAccountId` | Auth packet (chưa có trong Health P1) |
| Rate-limit quota, expiry/tombstone policy | Chủ dự án + API packet |
| Bật feature gate, HTTP restart acceptance | Sau Codex review |

Library **không** tham chiếu `Health.exe`; DTO life/death/return nằm trong
`Server/Persistence/LifeReceipts.cs` và chỉ chuyển field, không mint id.

## 2. Điểm gọi từ Health (đề xuất)

Giữ nguyên thứ tự: xác thực principal → acquire lease → đọc state → planner thuần → commit.

```csharp
var db = new PersistenceDatabase(new PersistenceOptions
{
    DatabasePath = config.DatabasePath,          // ngoài repo, không commit DB
    LeaseTtl = TimeSpan.FromSeconds(60),
    ReconnectGrace = TimeSpan.FromSeconds(120),
    OutboxClaimTtl = TimeSpan.FromSeconds(30),
    BusyTimeout = TimeSpan.FromSeconds(10)
});
await db.InitializeAsync();                       // migration fail-closed

var leases = new LeaseStore(db);
var lease = await leases.AcquireAsync(characterId, ownerToken, principalAccountId: accountId);
// lease.Succeeded == false => map LeaseHeld/LeaseMissing/LeaseExpired/OwnershipDenied

var uow = new DurableUnitOfWork(db);
var outcome = await uow.ExecuteAsync(
    new MutationRequest(
        idempotencyKey,
        characterId,
        operation,
        requestJson,
        expectedRevision,
        lease.Lease!.FencingToken,
        principalAccountId: accountId),
    context => planner.Plan(context));            // pure, no I/O, no await inside
```

`MutationPlan` có thể mang `LifeTransition`:

```csharp
var death = new PlayerDeathSnapshot(characterId, lifeVersion, deathRevision, deathEventId, atUtc);
var transition = LifeTransition.ForDeath(before, new LifeSnapshot(characterId, lifeVersion, death), death);

var returnCommit = new LifeReturnCommit(key, requestHash, before, after, fullResult, committedUtc);
var transition = LifeTransition.ForReturn(before, after, returnCommit);
```

Chỉ một trong hai đường: **hoặc** planner trả plan có `Life`, **hoặc** gọi một writer khác.
Không mutate actor rồi mới gọi library; như vậy không còn crash-safe.

Đọc có kiểm quyền:

```csharp
var state = await db.ReadStateAsync(characterId, principalAccountId);
var receipt = await db.ReadReceiptAsync(idempotencyKey, principalAccountId);
// null cho cả "không tồn tại" và "không sở hữu" — không lộ character của account khác
```

Life/return read:

```csharp
var life = await new LifeReceiptStore(db).ReadLifeAsync(characterId);
var lookup = await new LifeReceiptStore(db).LookupReturnAsync(idempotencyKey);
// Missing / Committed / Tombstoned. Tombstone không phải Missing.
```

Outbox:

```csharp
var dispatcher = new OutboxDispatcher(new OutboxStore(db));
var report = await dispatcher.DispatchBatchAsync(
    consumer, workerId,
    async (item, applyOnce, ct) =>
    {
        await applyOnce(async (connection, transaction, token) =>
        {
            // ghi hiệu ứng gameplay trong CÙNG transaction với dedupe marker
        });
    },
    batchSize: 10, maxAttempts: 5);
```

`applyOnce` trả `false` nghĩa là hiệu ứng đã được áp trước đó; không grant lần hai.
Delivery là **at-least-once**, consumer phải dedupe theo `consumer_effects`.

Readiness/metrics cho endpoint nội bộ:

```csharp
var readiness = await new PersistenceDiagnostics(db).ReadReadinessAsync();
var metrics = await new PersistenceDiagnostics(db).ReadMetricsAsync();
// chỉ count/version/age; không payload, id, characterId, token
```

## 3. Transaction boundary và lỗi

- Planner chạy **bên trong** transaction `BEGIN IMMEDIATE`, sau CAS revision, lease/fencing
  và ownership. Planner phải thuần: không `await`, không đọc DB khác, không gọi network.
- State + receipt + ledger + outbox + life transition commit cùng nhau. Planner trả
  `Reject`/`CapacityExceeded` thì không ghi gì.
- Replay cùng key + cùng operation/payload/owner trả đúng result lịch sử; khác payload →
  `RequestConflict`; khác owner → `OwnerConflict`. Không dùng TTL receipt để grant lại.
- Stale life version → `RevisionConflict` + `life-version-conflict`, rollback toàn bộ.
- Cancellation sau khi transaction đã commit là **unknown commit**: client retry cùng key;
  không được đổi key hoặc coi là thất bại để grant lại.
- Không giữ actor lock trong lúc `await` DB; làm giảm nguy cơ deadlock với tick loop.

Mapping gợi ý:

| `MutationStatus` / `ErrorCode` | Ý nghĩa HTTP |
| --- | --- |
| `Committed` | 200 |
| `Replayed` | 200 + `replayed=true` (fresh-read state) |
| `RevisionConflict` | 409 `revision_conflict` |
| `OwnerConflict` / `RequestConflict` | 409 `idempotency_key_conflict` |
| `OwnershipDenied` | 403/404 theo auth edge, không lộ character tồn tại |
| `LeaseHeld` / `LeaseExpired` / `StaleFencingToken` | 409/423, client re-auth/acquire lại |
| `LeaseMissing` | 409 (command không có lease) |
| `CapacityExceeded` | 422, không phải success |
| `Failed` | 500 với correlation id, không trả payload nội bộ |

## 4. Feature gate và rollback

- Gate mặc định **OFF**; không map route mới, không đổi wire v2, không sửa Health trong
  checkpoint này.
- Bật gate chỉ sau Codex review + test restart HTTP thật. Library pass không thay thế
  acceptance của Health.
- Rollback: tắt gate trước, giữ DB file; không auto-downgrade schema. Nếu buộc quay về
  in-memory, coi dữ liệu DB là nguồn export một chiều và ghi rõ mất state phát sinh sau mốc.
- Migration lỗi/không tương thích: fail closed, giữ nguyên DB cũ; dùng backup đã verify để
  restore, không xóa DB để boot.

## 5. Giới hạn đã biết

- Single-host SQLite, một writer tại một thời điểm; không phải capacity production.
- Benchmark dev: commit p50 ~9.6 ms, p99 ~15.1 ms; contention 4 task p99 ~165 ms trên máy
  4 CPU (xem `Implementation/Reports/QR-01_R2_Atomic_Life_Ops_20261114_vi.md`).
- Tombstone/expiry chưa được duyệt: library chỉ đọc tombstone, không reclaim receipt cũ.
- Chưa có disk-full/ACL proof; IO-denied được test bằng file lock thật.
- PostgreSQL provider, rate-limit quota, auth edge: ngoài checkpoint.

## 6. Checklist review cho Codex/Qoder local

1. Planner có thực sự thuần và không giữ actor lock qua `await`?
2. `LifeTransition` có được tạo từ **trước** khi mutate actor, với full before/after và
   `DeathReturnResult` đầy đủ field?
3. Caller có dùng đúng `principalAccountId` từ auth edge (không lấy `characterId` client làm
   quyền) và map `OwnershipDenied` không lộ tồn tại?
4. Outbox handler có ghi hiệu ứng qua `applyOnce` trong cùng transaction, và chịu được
   replay/consumer crash?
5. Gate OFF, không đổi wire/contracts/client, migration/backup runbook đã đọc?
6. Chấp nhận các giới hạn single-host/at-least-once/tombstone chưa có expiry?

## 7. Lệnh kiểm chứng

```bash
dotnet restore Server/Persistence.Tests/Server.Persistence.Tests.csproj --locked-mode
dotnet build Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release --no-restore
dotnet test  Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release \
  --logger "trx;LogFileName=qr01.trx"
```

CI: `.github/workflows/qr-01-ci.yml`. Không cần Unity, service cloud hay DB production.
