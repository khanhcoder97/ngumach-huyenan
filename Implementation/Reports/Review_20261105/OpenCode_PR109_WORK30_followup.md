# PR109 work30 delta review

Pinned head **060b8764fed0d2c2b5d2d33d3880b834c1637143**, verified still current. Base for this delta: c3c8a12. No source edits or GitHub actions performed. Only independent harness files outside the review checkout were extended.

## Improvements actually verified

Original three simple repros now pass: UI-context Dispose returns0ms (previous2022ms); cancellation while death HTTP is still pending leaves HP0/no receipt/no follow-up read; queued EncounterUpdated after Dispose is suppressed. Timeout and six bounded alpha IDs remain functional. No full224-unit rerun was needed; those are the author's reported counts, not this review's independent count.

## Remaining blockers — deterministic public API repros

**P1: stale death reply is applied before facade checks it.**

- `Shared/ClientCore/Composition/ClientSession.cs:184` awaits `Client.ReturnFromDeathAsync` before checking the epoch.
- `Client/Assets/Scripts/Online/Core/P1ClientV2.cs:319–323` clears the pending identity, writes receipt/cooldown, and starts ReadWorld without cancellation/epoch validation after receiving the successful transport result.
- Repro installs a queued UI SynchronizationContext. Complete the HTTP reply, wait until the successful result has been queued for the Core continuation, then Dispose before pumping that queue. TimeoutTransport already returned the successful result; canceling its token cannot retract that queued continuation.
- Actual result: `stale_session`, but HP changed0→50, pending key was cleared, one world read started **after** Dispose, and receipt was transiently visible. Thus the new comment claiming no state apply/world read is false. Restoring two fields after the fact cannot undo HP/world mutation or restore unresolved request identity.

**P1: rollback corrupts the new epoch.**

- `ClientSession.cs:198–199` writes through the mutable current `Client` property instead of the captured old client.
- Repro queues old death Core continuation as above; Relogin creates a new client and carries the original pending key; same-key retry on that new client succeeds and produces cooldown2900. Pump old continuation. Old facade then restores its pre-request null values into the **new** client.
- Actual result: new epoch cooldown **2900→null**, old Core still changed HP and sent another world read. The facade result is stale_session but the new epoch has already been corrupted.

**P2: queued encounter event survives failed relogin.**

- `ClientSession.cs:389` checks disposed, generation and nonnull subscription, but not captured session/current Guard validity.
- After a successful encounter read queues a dispatcher callback, force Relogin to fail. Generation remains1, current session becomesnull and Guard has ended. Drain queued callback: it still invokes the old consumer once.
- Actual: `loginSuccess=False oldGeneration=1 currentGeneration=1 activeSession=NONE deliveredAfterEpochEnded=1`.

## Required correction

Guard cancellation and captured session/epoch **before Core writes receipt/cooldown/pending/world state and before any follow-up read**. A request that may have committed remotely must keep the exact original key/body for reconciliation. Capture the client identity for the operation; never apply-then-restore snapshots and never write old saved fields into `Client` after Relogin. Return LastDeathReturn/NextReturnAllowedAtTick setters to private unless a separately justified API needs otherwise. At dispatcher execution, validate the captured session against the active Guard/epoch, including failed relogin, not just the generation counter.

## Reproduce

Harness/source: `D:/Project/NGUMACHHUYENAN-tools/review-opc16-20261105/Program.cs` + `Review.csproj`.

```powershell
$env:DOTNET_ROOT='D:\Project\NGUMACHHUYENAN-tools\dotnet8'
$env:PATH=$env:DOTNET_ROOT+';'+$env:PATH
# CWD D:\Project\NGUMACHHUYENAN-tools\review-opc16-20261105
& "$env:DOTNET_ROOT\dotnet.exe" run --project Review.csproj -c Release -m:1
```

Raw results are preserved in **repro-work30-output.txt**. The old c3c8a12 results remain in repro-output.txt. Relevant harness methods: DeathResponseAlreadyQueued(false), DeathResponseAlreadyQueued(true), QueuedEventAfterFailedRelogin(). These use public facade/Core methods and controlled task/UI queues, no reflection or server fixtures. The new unit tests only cancel before the HTTP reply finishes; they do not cover this queued-success-before-Dispose/relogin ordering, so reported224PASS does not close these failures.

## Consumption and stacking

Do not import ClientSession or merge PR109 yet. Root's serial NativeOnlineSession and captured Run.Token/main-thread epoch publication remain the safer host. The four-file Core subset at **c3c8a12** is the same typed inventory/death/alpha API logic as060b876 except the new internal setters; it needs no composition/facade dependencies. A future selective Core import should retain private receipt setters and add the before-apply guard. PR109 targets `opencode/opc-14-ui-runtime-hardening-20261101` (PR103), not the gameplay integration branch; merging the whole stack would also include unreviewed PR103 UI work. It is not an isolated portable-only fast-forward into current integration.
