# OpenCode PR109 independent review — 2026-11-05

Pinned source: `c3c8a12eacb3c7f91e9985afd843b34781af39c5`.
Previous head: `685b888ae1ac42a314569602e1a4370a783f250c`.
Review worktree: `D:/Project/NGUMACHHUYENAN-opc16-review-20261105`, branch `codex/review-opc16-20261105`.
No source edits, merge, or GitHub posts were performed. This is not native engine acceptance.

## Blocking composition findings

1. **Lifetime cancellation does not cover the new death-return facade.** `Shared/ClientCore/Composition/ClientSession.cs:155–158` forwards the caller token directly to `Client.ReturnFromDeathAsync`, unlike Connect/Encounter which link `_cts`. Start death-return, then Dispose before the server reply: the transport token remains uncanceled; completing the reply mutates the disposed client's LastDeathReturn and fresh world, and starts a new world read. Observed: `innerTokenCanceled=False success=True hp=50 receiptApplied=True postDisposeWorldReads=1`. A session-owned facade must link lifetime and reject publications after its captured epoch expires; do not drop the retained uncertain mutation identity.

2. **Queued callbacks survive disposal/relogin.** `ClientSession.cs:331–338` captures the event delegate before `_dispatcher.Post` and the queued closure has no current-epoch/disposed check. Accept an encounter read through a queued dispatcher, Dispose before draining it, then drain: observed `deliveredAfterDispose=1`. Setting `EncounterUpdated=null` does not invalidate the already captured delegate. Guard the closure at execution time with the captured session/generation and subscription/lifetime validity.

3. **Dispose blocks the UI context for two seconds.** `ClientSession.cs:398–410` loops with `Thread.Sleep(1)` until the lane releases. The encounter continuation captured the UI SynchronizationContext, so that continuation cannot run while Dispose blocks that thread. Observed `UI_DISPOSE elapsedMs=2022 readOutcome=Stale`; original SemaphoreSlim.Release exception is prevented, but replaced by a visible shutdown/logout freeze. Mark stopped, cancel, and let the active read perform deferred final cleanup (or use an awaited async shutdown); do not synchronously wait on its own UI continuation.

## Verified repairs and current test result

- TimeoutTransport no longer waits forever on an asynchronous inner transport ignoring CT. With a never-completing task and 40ms deadline, final harness run returned status0/correlation preserved in122ms on this loaded laptop. Initial run90ms; another overloaded run1485ms. This demonstrates bounded abandonment, not realtime40ms scheduling accuracy.
- Canonical `ALPHA_OBJ_BM_RIPPLE_01`: one actual transport send. Unpublished `ALPHA_OBJ_BM_RIPPLE_99`: invalid_target with zero sends. Bounded request allowlist is implemented.
- Fake valid WorldV2 containing all six exact IDs as INTERACTABLE/INVULNERABLE/AVAILABLE: actual ConnectAsync+ReadWorldV2 succeeds, count6, all IDs preserved.
- **221/221 unit tests passed**, 0failed/0skipped. TRX `results/opc16_review_full_sparse.trx`.
- First sparse attempt failed1/221 because the catalog fixture path was excluded from sparse checkout. Adding `Client/Assets/Resources/PlayerUI` fixed it; that initial missing-checkout failure is not a product defect.
- Initial core build had1CS1998 warning at P1ClientV2.cs:409 (ApplyInventoryV2 async without await); no build errors.

Commands:

```powershell
$env:DOTNET_ROOT='D:\Project\NGUMACHHUYENAN-tools\dotnet8'
$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
# CWD review worktree
& "$env:DOTNET_ROOT\dotnet.exe" test Shared/ClientCore.Tests/ClientCore.Tests.csproj -c Release -m:1 --no-restore --logger 'trx;LogFileName=opc16_review_full_sparse.trx' --results-directory D:\Project\NGUMACHHUYENAN-tools\review-opc16-20261105\results
# CWD this report's directory
& "$env:DOTNET_ROOT\dotnet.exe" run --project Review.csproj -c Release -m:1
```

`Program.cs` is an independent public-API harness; `repro-output.txt` is the last actual output. ThreadPool minimum8 in this harness reduces timing noise only; the UI Dispose repro installs a single-thread queued SynchronizationContext. The fake transports do not modify any server state.

## Alpha world closure

`P1ClientV2.cs:82–107` does not apply the ENT request regex to world entity IDs, only nonempty/uniqueness and closed kind/state/health constraints. This logic is unchanged since685b888, so the current native bridge can already read ALPHA IDs. Its old InteractAsync request validation was the blocker.

Qoder pinned `cb4f475` `Server/Health/Gameplay/Alpha/AlphaOverlayMerger.cs:91–110` projects design RESCUE_INTERACTABLE to wire INTERACTABLE and keeps exact ALPHA IDs; QUEST_HAZARD creates no runtime entity. `WorldSnapshotV2.schema.json` entityId pattern already accepts `^(?:ENT|ALPHA)_[A-Z0-9_]+$`. No wire kind expansion is needed.

## Safe selective consumption

Do not merge/adopt ClientSession wholesale while these three composition bugs remain. A narrower bridge integration can consume the additive Core APIs separately after review:

- The entire delta from integrationf383233 to c3c8a12 in `Client/Assets/Scripts/Online/Core` is only **four files**: P1Client.cs, P1ClientV2.cs, P1Models.cs, P1ModelsV2.cs (384insertions/13deletions). No new external package or Shared composition dependency is required.
- Existing calls `new P1Client(transport,useWorldV2:true)` remain source compatible; optional `characterId` is a new fourth argument. P1SessionRequest gets that optional field. Other changes preserve pending expiry/relogin state and parse schemaVersion1 error envelopes for v2 routes.
- Public APIs: `ReadInventoryV2Async(ct)`, `EquipV2Async(instanceId,expectedRevision,ct)`, `UnequipV2Async(slotId,expectedRevision,ct)`, `ReturnFromDeathAsync(ct)`. Public projections: InventoryV2, LastDeathReturn, NextReturnAllowedAtTick.
- v2slot order is fixed HAT/CHEST/LEGS/WEAPON/GLOVES/BOOTS/NECK/RING_L/RING_R/PENDANT/CLOAK/SEAL, bag100; v1 stays separate.
- Keep NativeOnlineSession's serial worker, its own linked Run.Token and epoch-guarded main-thread publication. Pass Run.Token to all new APIs. Do not use the faulty ClientSession death facade or queued event dispatch. Run nativeP00-01 regressions after selecting these four files, and real HTTP inventory/death acceptance against the reviewed Qoder server before advertising those features.

The new HTTP runner still only validates P00-01 and explicitly reports P00-02..05 locked against its baseline; its green run is not full tutorial/death/inventory HTTP acceptance.
