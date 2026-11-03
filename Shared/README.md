# Shared/ClientCore — portable C# client core (Godot-ready)

Target framework: `net8.0` (Godot 4.7.2 stable .NET baseline; do not self-upgrade).
No `UnityEngine` / `UnityEditor` / UI Toolkit / `Resources.Load`. Engine-agnostic.

## Projects
- `Shared/ClientCore/ClientCore.csproj` — class library. Reuses the existing portable
  `Client/Assets/Scripts/Online/Core` and `.../Presentation` sources via explicit
  `Compile Include` (provenance kept), plus new portable modules:
  - `Encounter/` — DTO + view model + shape validator (approved snapshot contract)
  - `Guards/` — `StaleResponseGuard`, `ReceiptReplayGuard`
  - `Catalog/` — `IFileProvider` + `CatalogLoader` (no Resources.Load)
  - `Handshake/` — capability/version handshake
- `Shared/ClientCore.Tests/ClientCore.Tests.csproj` — xunit portable tests (40 assertions).
- `Shared/ClientCore.HttpRunner/` — console runner against a private Health server.

## Build / test
```
dotnet build Shared/ClientCore/ClientCore.csproj -c Release
dotnet test  Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release
```
SDK: `D:/Project/NGUMACHHUYENAN-tools/dotnet10/dotnet.exe` with
`DOTNET_ROLL_FORWARD=LatestMajor` on machines carrying only .NET 10.

## HTTP runner (real server required)
```
set P1_BASE_URL=http://127.0.0.1:<port>
dotnet run --project Shared/ClientCore.HttpRunner/ClientCore.HttpRunner.csproj -c Release
```
Missing server => exit 2 (UNVERIFIED), never exit 0.

## Godot consumer (Muse)
Reference `NguMach.Client.Core.dll` from `ClientGodot/`. Example:
```csharp
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.P1;

var client = new P1Client(transport, useWorldV2: true);
var guard = new StaleResponseGuard();
var view  = new EncounterView();
// poll: var snap = await client.ReadEncounterAsync(ct); if (guard.IsApplicable(...)) view.Apply(snap);
```
Do not flip Y in the portable model; Godot side owns render transform.
No scene/runtime Godot edits belong to OpenCode — only this library + adapter contract.
