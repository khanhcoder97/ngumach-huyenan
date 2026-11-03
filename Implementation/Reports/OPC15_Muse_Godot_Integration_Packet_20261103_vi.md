# OPC-15 Muse — Godot integration packet (portable core)

Branch: `opencode/opc-15-godot-client-core-20261103` (stacked on OPC-14 `974139f`).
Owner: OpenCode (portable core only; Muse owns Godot scene/runtime).

## What OpenCode ships
- `Shared/ClientCore/` — portable C# library (`net8.0`), no Unity/Godot deps.
- Reused portable sources: `Client/Assets/Scripts/Online/Core` + `.../Presentation` via explicit Compile Include.
- New modules: `Encounter/` (DTO + view model + shape validator), `Guards/` (stale response, receipt replay), `Catalog/` (`IFileProvider` + loader), `Handshake/` (capability/version).
- `Shared/ClientCore.Tests/` — 40 xunit assertions, `dotnet test` green.
- `Shared/ClientCore.HttpRunner/` — console runner against a private Health server.
- `Shared/README.md` — build/test/runner commands.

## Godot consumer (minimal sample)
```csharp
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

var transport = /* Godot HTTP transport implementing IP1Transport */;
var client = new P1Client(transport, useWorldV2: true);
var adapter = new P1ClientAdapter(client);
var guard = new StaleResponseGuard();
var view = new EncounterView();

// connect
await client.ConnectAsync(ct);

// poll encounter (route may be UNVERIFIED until Qoder ships it)
// var snap = await client.ReadEncounterAsync(ct); // not yet in P1Client; use transport directly for now
// if (guard.IsApplicable(snapSessionId, snapRequestId, snapGeneration)) view.Apply(snap);
```
Godot side owns render transform (no Y-flip in portable model), scene wiring, input, animation.

## Handshake
`ClientCapability` lists supported classes (`CLASS_MINH_KIEM` only for alpha) and routes. Muse must check `CapabilityHandshake.IsRouteSupported` / `IsClassSupported` before calling; unsupported => disabled with reason, never pretend.

## HTTP proof (O-D)
Runner exits 0 only with a live private server + assertions > 0; missing server => exit 2 (UNVERIFIED). Reward exactly-once verified via before/after inventory (20 COIN + 1 chest) + receipt replay guard.

## Limits
- No Godot scene/runtime edits by OpenCode.
- Encounter routes may be UNVERIFIED until Qoder ships them; client must handle 404 without crashing.
- Native Godot import/build/export remains Muse-owned.
- Full-bag turn-in stays UNVERIFIED (no server seed/capacity contract).
