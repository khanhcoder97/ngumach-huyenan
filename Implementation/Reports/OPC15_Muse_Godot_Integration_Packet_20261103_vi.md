# OPC-15 Muse — Godot integration packet (portable core)

Branch: `opencode/opc-15-godot-client-core-20261103` (stacked on OPC-14 `974139f`).
Code head: `ce4ce5b83505e55059722b06f4e347292f27144b` (PR #109).
Owner: OpenCode (portable core only; Muse owns Godot scene/runtime).

## Trạng thái đã xác minh
- `godot-client-core` CI run `41803595203`: **PASS** cả hai job.
- `Shared/ClientCore.Tests`: **135/135** test PASS (TRX `total=135 passed=135 failed=0`).
- HTTP runner với private Health server thật: **55 assertions**, marker
  `PASS ClientCore HTTP assertions: 55`; CI gate đọc `assertions.txt` và fail nếu 0/thiếu.
- Build core, sample và HTTP runner: 0 warning/0 error ở phần ClientCore.

## OpenCode bàn giao gì
- `Shared/ClientCore/` — thư viện C# portable (`net8.0`), không phụ thuộc Unity/Godot.
- Source tái sử dụng: `Client/Assets/Scripts/Online/Core` + `.../Presentation`
  qua `Compile Include` tường minh.
- Module mới:
  - `Encounter/` — DTO strict, validator, `EncounterView`, `EncounterState` immutable.
  - `Composition/` — `ClientSession`, `ClientSessionFactory`, `PendingMutationCarry`.
  - `Transport/` — `HttpClientTransport`, `TimeoutTransport`.
  - `Dispatch/` — `IMainThreadDispatcher`, `SynchronousDispatcher`.
  - `Guards/`, `Catalog/`, `Handshake/` như trước, nay tách client-supported/server-enabled.
- `Shared/ClientCore.Tests/` — 135 test, gồm negative fixture, strict enum/ID/cooldown,
  stale read/mutation, relogin epoch, pending carry, timeout/cancellation, capability split.
- `Shared/ClientCore.HttpRunner/` — runner HTTP thật + wrapper `run_http.py` có assertion gate.
- `Shared/README.md` — build/test/runner/API/verification.

## Godot consumer (mẫu tối thiểu)
```csharp
using System;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Handshake;

var session = ClientSessionFactory.CreateHttp(
    "http://127.0.0.1:15085",
    characterId: "CHR_...",
    requestTimeout: TimeSpan.FromSeconds(10),
    dispatcher: godotDispatcher); // Muse cài IMainThreadDispatcher

session.EncounterUpdated += update =>
{
    // update.IsNewEncounter / IsNewCast / IsNewLife / PhaseChanged / IsTerminal
    // session.Encounter.State là EncounterState immutable để render.
    // Gọi session.Encounter.CommitCast() sau khi bắt đầu VFX cast.
};

var connect = await session.ConnectAsync();
if (!connect.Success) { /* hiển thị lỗi localized */ }

var current = await session.ReadCurrentEncounterAsync();
switch (current.Outcome)
{
    case EncounterReadOutcome.Success:
        // current.State: typed immutable view
        break;
    case EncounterReadOutcome.NotFound:
        // 404 encounter_not_found: không có encounter/route chưa mở; không tạo state giả
        break;
    case EncounterReadOutcome.SessionExpired:
        // gọi session.ReloginAsync(); pending mutation giữ nguyên key
        break;
}
```
Godot side sở hữu render transform (không Y-flip trong portable model), scene wiring,
input, animation, VFX. OpenCode không sửa scene/runtime Godot.

## Capability và alpha gate
`ClientCapability` tách:
- `IsRouteSupported`: client biết route (không có nghĩa server đã bật).
- `IsRouteEnabled`: server/deployment profile bật route.
- `IsEncounterUsable`: alpha boss gate ON **và** cả current/detail được server bật.

`DeploymentProfile.ProductionOff()` giữ encounter OFF, không advertise route.
Muse phải check `CapabilityHandshake.IsRouteEnabled` / `IsEncounterUsable` trước khi
bật UI encounter; không tự tạo endpoint hoặc tự bật alpha.

## Hợp đồng encounter
Authority thiết kế: `encounter_snapshot_v1_reference_20261104.json`, bind với schema
QOD-21 Q2 đã publish: `Implementation/Contracts/P1/EncounterSnapshotV1.schema.json`
(PR #106, chưa merge main).
Parser strict: unknown/duplicate/missing property, sai type, sai enum casing/ID pattern,
NaN/Infinity, facing không chuẩn hóa, phase/HP ngoài range, shape mang field không áp dụng,
`ticksRemaining != stateEndsAtTick - serverTick`, nhiều owner, thiếu/thừa key cooldown,
pad/NPC ngoài arena đều bị từ chối, không throw và không silent-map. `shape.kind` là
`CONE` / `CIRCLE` / `ANNULUS`; `status` là `OPEN` / `DEFEATED` / `RESET`; phase numeric
`1..3`; move state trên wire chỉ `TELEGRAPH` / `RECOVERY` (schema QOD-21 Q2 không serialize
`IMPACT`). `bossRevision >= 1`; `moveId` A/B/C; `targetLock` thuộc ba giá trị đã publish.

## Phụ thuộc Qoder
- Qoder sở hữu schema/fixtures/routes encounter thật (`/p1/encounters/current`,
  `/p1/encounters/{id}`). Schema + example đã publish ở PR #106; route chỉ map khi
  `P1:AlphaProfile:Enabled`, production vẫn OFF. Hiện route trả 404
  `encounter_not_found`; runner ghi **UNVERIFIED**, client trả `NotFound` typed và
  không dựng snapshot giả.
- Khi Qoder publish route/schema, chạy lại `python Shared/ClientCore.HttpRunner/run_http.py`
  và cập nhật packet/PR bằng exact SHA + assertion count mới.

## UNVERIFIED / blocker
- Native Godot import/build/export và playmode: Muse-owned, chưa có evidence.
- Encounter HTTP thật: chờ Qoder publish route/schema/fixtures.
- Full-bag turn-in: chưa có seed/capacity contract.
- Inventory v2 12-slot/death-return: chưa có upstream route/schema đầy đủ.
- Production gates vẫn OFF; không merge PR #109 khi chưa có nghiệm thu native và route thật.

## Bằng chứng
- PR #109: https://github.com/khanhcoder97/ngumach-huyenan/pull/109
- CI: run `41803595203`, workflow `godot-client-core`, 2/2 job PASS.
- Unit evidence: TRX counters `total=135 passed=135 failed=0`.
- Assertion marker CI: `PASS ClientCore HTTP assertions: 55`
  và bước gate in `HTTP assertions: 55`.
