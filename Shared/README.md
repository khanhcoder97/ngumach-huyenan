# Shared/ClientCore — portable C# client core (Godot-ready)

Target framework: `net8.0` (Godot 4.7.2 stable .NET baseline; do not self-upgrade).
No `UnityEngine` / `UnityEditor` / UI Toolkit / `Resources.Load`. Engine-agnostic.

Code head: `ce4ce5b83505e55059722b06f4e347292f27144b`; last verified head:
`37704f485b95c7a9c9e40cd3ad97aef75c081631` (PR #109, branch
`opencode/opc-15-godot-client-core-20261103`); encounter validation is bound to
Qoder's published QOD-21 Q2 schema
`Implementation/Contracts/P1/EncounterSnapshotV1.schema.json` (PR #106).

## Projects
- `Shared/ClientCore/ClientCore.csproj` — class library. Reuses the existing portable
  `Client/Assets/Scripts/Online/Core` and `.../Presentation` sources via explicit
  `Compile Include` (provenance kept), plus new portable modules:
  - `Encounter/` — strict DTO + validator + `EncounterView` / immutable `EncounterState`
  - `Composition/` — `ClientSession`, `ClientSessionFactory`, pending-mutation carry
  - `Transport/` — `HttpClientTransport`, `TimeoutTransport`
  - `Dispatch/` — `IMainThreadDispatcher`, `SynchronousDispatcher`
  - `Guards/` — `StaleResponseGuard`, `ReceiptReplayGuard`
  - `Catalog/` — `IFileProvider` + `CatalogLoader` (no Resources.Load)
  - `Handshake/` — capability/version handshake (client-supported vs server-enabled)
- `Shared/ClientCore.Tests/ClientCore.Tests.csproj` — xunit portable tests
  (`135/135` passing locally and in CI).
- `Shared/ClientCore.HttpRunner/` — console acceptance runner against a private
  Health server (`55` real HTTP assertions in CI).

## Build / test
```
dotnet build Shared/ClientCore/ClientCore.csproj -c Release
dotnet build Shared/ClientCore.Sample/ClientCore.Sample.csproj -c Release
dotnet test  Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release
```
SDK: `D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe` with
`DOTNET_ROLL_FORWARD=LatestMajor` on machines carrying only .NET 10.
CI installs both .NET 8 and .NET 10.

## HTTP acceptance runner (real private server required)
```
set "DOTNET=D:\Project\NGUMACHHUYENAN-tools\dotnet10\dotnet.exe"
python Shared/ClientCore.HttpRunner/run_http.py
```
`run_http.py` builds/starts a private loopback Health server, runs the real HTTP
runner, writes raw logs and `TestResults/clientcore-http/assertions.txt`, and exits:
- `0` only when the server responded and the runner reported a positive assertion count;
- `1` on build/runner failure, missing marker, or zero assertions;
- `2` when the server is unavailable (UNVERIFIED, never a pass).

The assertion gate is mandatory: exit code alone is not accepted, and a run with
zero assertions cannot pass. CI uploads the TRX and HTTP artifacts.

## Encounter contract
Wire authority is `Shared/ClientCore.Tests/Fixtures/encounter_snapshot_v1_reference_20261104.json`,
bound to Qoder's published QOD-21 Q2 schema `EncounterSnapshotV1.schema.json`
(PR #106; Qoder owns schema/fixtures/routes). The parser is strict:
unknown/duplicate/missing properties, wrong types, bad enum casing/ID patterns,
non-finite numbers, non-normalized cone facing, out-of-range values, shape/field
mismatches, tick mismatch, multiple owners, missing/unknown cooldown keys, and
out-of-bounds pads/NPC are rejected without throwing. Non-applicable fields are
present as `null`; `activeMove` is `null` when there is no move. Published move
states are `TELEGRAPH|RECOVERY`; `IMPACT` is not a snapshot state.

## Godot consumer (Muse)
Reference `NguMach.Client.Core.dll` from `ClientGodot/`. Use the composition root,
not a hand-built transport:
```csharp
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Handshake;

var session = ClientSessionFactory.CreateHttp("http://127.0.0.1:15085",
    characterId: "CHR_...", requestTimeout: TimeSpan.FromSeconds(10),
    dispatcher: godotDispatcher); // implements IMainThreadDispatcher

session.EncounterUpdated += update => { /* dispatch to main thread, render VFX */ };

var connected = await session.ConnectAsync();
if (!connected.Success) { /* show localized error */ }

var current = await session.ReadCurrentEncounterAsync();
if (current.Outcome == EncounterReadOutcome.Success)
{
    var state = current.State;          // immutable typed projection
    // current.Update: IsNewEncounter/IsNewCast/IsNewLife/PhaseChanged/IsTerminal
    // call session.Encounter.CommitCast() after the cast VFX starts
}
```
Capability is explicit: check `CapabilityHandshake.IsRouteEnabled` (server-enabled)
before enabling encounter UI; `IsRouteSupported` only says the client knows the
route. `IsEncounterUsable` requires the alpha gate and both current/detail routes.
Production profile keeps encounter OFF and advertises no server-enabled routes.

Do not flip Y in the portable model; Godot side owns render transform.
No scene/runtime Godot edits belong to OpenCode — only this library + adapter contract.

## Verification status
Verified in CI run `41803595203` (`godot-client-core`, code head `ce4ce5b`) and
again in run `41803960912` (head `37704f4`):
- build core + sample: PASS
- `135/135` unit tests: PASS (TRX counters `total=135 passed=135 failed=0`)
- private HTTP runner: PASS with `55` assertions.

UNVERIFIED / blocked:
- encounter HTTP routes: 404 `encounter_not_found` until Qoder merges/runs the
  routes with the alpha gate on (the client treats this as typed `NotFound`,
  never fabricates state);
- native Godot import/build/export (Muse-owned);
- full-bag turn-in (no seed/capacity contract);
- inventory v2 12-slot/death-return (no complete upstream route/schema).
