# ADOPTION — `NguMach.Client.Core` (portable client core)

Audience: the host integrator (Codex) wiring this library into the Godot/Unity
client. Owner: OpenCode. Scope: `Shared/ClientCore` + the portable sources it
packs; no scene, widget, asset, or server file is covered by this packet.

## 1. What you are adopting

- Package: `NguMach.Client.Core` `0.2.0-alpha.1` (`net8.0`, Godot 4.7.2 .NET
  baseline — do not self-upgrade the TFM).
- Composition root: `NguMach.Client.Core.Composition.ClientSessionFactory` /
  `ClientSession`. Never hand-build `HttpClientTransport` + guards in a host.
- Wire DTOs and validators live in namespace `NguMach.Client.P1` (files under
  `Client/Assets/Scripts/Online/Core`, packed into the library via explicit
  `Compile Include` — provenance, not a copy). Presenters/adapters live in
  `NguMach.Client.Presentation`.

## 2. Source and dependency closure

Everything the package ships is in this checkout:

| Area | Path | Namespace |
| --- | --- | --- |
| Portable core (packed) | `Shared/ClientCore/**` | `NguMach.Client.Core.*` |
| Wire core (packed) | `Client/Assets/Scripts/Online/Core/**` | `NguMach.Client.P1` |
| Presenters (packed) | `Client/Assets/Scripts/Online/Presentation/**` | `NguMach.Client.Presentation` |
| Tests | `Shared/ClientCore.Tests/**` | — |
| Sample consumer | `Shared/ClientCore.Sample/**` | — |
| HTTP acceptance runner | `Shared/ClientCore.HttpRunner/**` | — |

- Sole package dependency: `Newtonsoft.Json` 13.0.1 (see
  `Shared/ClientCore/THIRD-PARTY-NOTICES.md`).
- No `UnityEngine`, `UnityEditor`, UI Toolkit, `Resources.Load`, or Godot type
  appears anywhere in the package. Engine bindings (scene nodes, VFX, input)
  are host-owned.
- CI asserts every `.cs` on disk under `Online/Core` + `Online/Presentation`
  is covered by a `Compile Include` glob (G4.3), so a file you see on disk is
  in the package or the build fails.

## 3. Namespace collision checklist

- This checkout contains **no** `NativeOnlineSession` type. If the host tree
  defines one, that is a host-side type: do not rename ours to avoid it, and do
  not make `ClientSession` derive from it. Resolve by qualifying
  (`NguMach.Client.Core.Composition.ClientSession`) at the wiring site, or by
  moving the host type to the host namespace. Re-check at integration time —
  this note reflects the worktree at the OPC-17 checkpoint SHA.
- Two wire namespaces coexist on purpose: `NguMach.Client.P1` (transport DTOs,
  `P1Client`, `P1Wire`) and `NguMach.Client.Core.*` (composition/encounter/
  guards). Do not merge them; hosts use both.

## 4. Contract pin (schema manifest)

- `Shared/ClientCore.Tests/Fixtures/qoder-contract-pins.json` pins SHA-256 for
  every P1 schema + example at Qoder server checkout
  `6814126e2def8a1c4270a1016f0ab85404cba46e` (70 files).
- `Shared/ClientCore.Tests/Fixtures/qoder-contracts-6814126/` vendors the
  pinned bytes for files the client checkout does not carry yet (`vendored`)
  or carries with different bytes (`drift` + recorded `inTreeSha256`). Drift is
  recorded, never silently overwritten — `Implementation/Contracts/P1` stays
  Qoder-owned.
- Tests: `ContractConformanceTests` verifies both trees against the manifest,
  parses the pinned examples through the real typed models (receipt identity,
  credited/replayed, nullability, finite/range, ID patterns), and rejects
  mutated bytes. The HTTP runner takes `--contract-pin` to verify the server
  checkout's bytes before building anything.
- Regenerate the manifest only from a pinned server checkout; never edit hashes
  by hand to make a mismatch pass.

## 5. Method / reentrancy / thread semantics

- `ClientSession` is `IDisposable` **and** `IAsyncDisposable`:
  - `Dispose()` never blocks the caller (fire-and-forget cleanup, preserved
    behavior).
  - `DisposeAsync()` awaits cleanup bounded by `DisposeTimeout`
    (`DefaultDisposeTimeout` = 2 s, ctor-overridable).
  - Disposal is first-wins idempotent; concurrent `Dispose`/`DisposeAsync`
    never throw.
- `Adapter` (`P1ClientAdapter`) is **stable for the session lifetime**: a
  relogin swaps `Client`, not `Adapter`. Presenters may hold one reference
  forever; after dispose, every command returns a typed `disposed` failure and
  no transport call is made.
- `Token` never throws after dispose — it degrades to `CancellationToken.None`.
- `EncounterUpdated` subscribers are re-checked when the queued callback *runs*:
  unsubscribing between queue and run means the handler does not fire; a
  handler added later does not receive older events.
- Reads are serialized on an internal lane; responses are validated against the
  captured session + generation before touching state. Ambiguous mutations keep
  their request id/idempotency key across relogin (`PendingMutationCarry`).
- Dispatcher: all host callbacks arrive on the injected `IMainThreadDispatcher`
  (default `SynchronousDispatcher` — replace it with the engine's main-thread
  pump in a real host).

## 6. Migration / version notes

- Version: `0.2.0-alpha.1` (prerelease). Public API may still move within the
  alpha line; pin the exact version, do not float.
- Known interim shapes (do not "fix" them downstream):
  - `MAP_VIEWED` keeps interim `acknowledged/serverTick` and is **not frozen**.
  - `ReceiptReplayGuard` awaits a durable store (QOD-25 §7).
  - `ApplyTalk` success leaves state `NeedsResync`, not `Ready` — resync is
    expected, not an error.
  - Server mints `requestId`; the client does not fabricate one.
- Routes that stay UNVERIFIED (typed failure, never fabricated state): encounter
  (404 `encounter_not_found`), TALK outside P00-01, portal without chapter
  grant, death downed path, full-bag turn-in.

## 7. License

First-party license: **UNSPECIFIED** — the repository carries no `LICENSE`
file and the package deliberately declares no SPDX identifier
(`Shared/ClientCore/README.md`). Do not add MIT/Apache headers on our behalf;
third-party terms are listed only in `THIRD-PARTY-NOTICES.md`. Clarify the
first-party license with the repo owner before any redistribution.

## 8. Verification entry points

```
dotnet build Shared/ClientCore/ClientCore.csproj -c Release      # 0 warning
dotnet test  Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release
python Shared/ClientCore.HttpRunner/run_http.py                  # real server
python Shared/ClientCore.HttpRunner/run_negative_controls.py \
    --server-root <pinned-server-checkout>                       # must refuse
```
