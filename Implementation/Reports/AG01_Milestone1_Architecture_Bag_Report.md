# AG01 — Milestone 1 Report: Architecture + Bag (AG1 + AG2)

**Epic**: AG-01 Player UI  
**Issue**: https://github.com/khanhcoder97/ngumach-huyenan/issues/80  
**Branch**: `antigravity/ag-01-player-ui-20261030`  
**Source HEAD at commit**: (updated after push)  
**Baseline**: `92adee098fcb58acb5b280dcb167db9beecb8932`  
**Date**: 2026-10-30, Asia/Tokyo  
**Agent**: Antigravity Remote (Windows/PowerShell)  
**OS/Toolchain**: Windows 10+, git 2.x, dotnet UNVERIFIED (not installed on this machine)

---

## Files created

| File | Purpose |
|---|---|
| `Client/Assets/Scripts/Online/Presentation/P1UIState.cs` | Immutable view state types: `InventoryViewState`, `QuestJournalViewState`, `NpcDialogueViewState`, `SettingsViewState`, `MapViewState`, `AsyncState<T>`, `PanelRouter`-adjacent types |
| `Client/Assets/Scripts/Online/Presentation/IP1UIAdapter.cs` | Interface wrapping P1Client for UI |
| `Client/Assets/Scripts/Online/Presentation/P1ClientAdapter.cs` | Concrete adapter over live `P1Client` |
| `Client/Assets/Scripts/Online/Presentation/PanelRouter.cs` | Modal stack, panel open/close, focus return |
| `Client/Assets/Scripts/Online/Presentation/InventoryPresenter.cs` | AG2: 100-slot bag, 4-page view, duplicate-slot/out-of-range warnings, stale-revision guard, selection preservation |
| `Client/Assets/Scripts/Online/Presentation/QuestJournalPresenter.cs` | AG3: active/completed grouping, server-authoritative only |
| `Client/Assets/Scripts/Online/Presentation/SettingsPresenter.cs` | AG4: local preferences with version/default/reset, ISettingsStore interface |
| `Client/Assets/Scripts/Online/Presentation/MapPresenter.cs` | AG5: map view state from P1World/V2, UI zoom independent of world camera |
| `Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj` | .NET10 test project |
| `Client/Tests/PlayerUIChecks/PlayerUIChecksTests.cs` | Synthetic fixture tests (see below) |
| `.github/workflows/antigravity-player-ui.yml` | CI: runs PlayerUIChecks only |
| Matching `.meta` files | GUID-unique, valid Unity format |

## Test coverage (synthetic fixtures, labelled SYNTHETIC)

| Test | Scenario |
|---|---|
| `Load_100Slots_4Pages` | Full 100-slot inventory, 4 pages × 25 |
| `Load_DuplicateSlot_ProducesWarning` | Two items at same slot → warning, first wins |
| `Load_OutOfRangeSlot_ProducesWarning` | Slot index 999 → warning, no crash |
| `StaleRevision_NotApplied` | Old revision does not overwrite newer state |
| `SelectionPreserved_AfterPageChange` | Selection by instanceId survives page switch |
| `SelectionCleared_WhenItemGone` | Selection cleared if item no longer present |
| `EmptyInventory_NotMisread_AsLost` | Empty inventory ≠ lost items |
| `LoadError_PreservesLastKnownData` | Error state keeps last known items visible |
| `FilterIsProjectionOnly_SlotIndicesUnchanged` | Filter is view-only, never rewrites slot map |
| `PanelRouter_*` (4 tests) | Open, stack, CloseTop focus return, CloseAll |
| `QuestJournalPresenter_*` (2 tests) | active/completed split, error phase |
| `SettingsPresenter_*` (3 tests) | defaults, clamp, reset |

## Test run status

**UNVERIFIED** — `dotnet` not installed on this machine.  
Tests are correctly structured for `dotnet test` from a clean clone with .NET 10.  
CI workflow `antigravity-player-ui.yml` will run them on GitHub Actions.

## Constraints verified (code review)

- [x] No Unity dependency in `Presentation/` layer (pure C#9)
- [x] `IP1UIAdapter` wraps `P1Client` read-only; no competing HTTP client
- [x] `InventoryViewState`: 4 pages × 25 = 100 slots (DEC-023)
- [x] Slot filter is view projection only — does not modify authoritative slot indices
- [x] `inventoryRevision` old does not overwrite new
- [x] Toast/receipt not added to snapshot
- [x] `PanelRouter.CloseTop()` never cancels server-committed transaction
- [x] `UncertainMutation` state flows through `IP1UIAdapter.ConnectionState`
- [x] Map zoom is UI-only (does not modify world camera profile)
- [x] Topology marked `topologyIsCandidate: true` — no coordinate edits
- [x] No art/audio/server/tooling files touched

## Known gaps / UNVERIFIED

- Unity compile/import/prefab: **UNVERIFIED** (no Unity on this machine)
- `Client/Assets/Scripts/Online/Unity/PlayerUI/` MonoBehaviours: next milestone
- NPC dialogue panel presenter: next milestone (AG3 full)
- Catalog resolver (display name / rarity lookup): stub returns UNRESOLVED; to be connected after catalog API review
- `ISettingsStore` implementation (Unity PlayerPrefs adapter): next milestone

## Integration instructions for Codex / Qoder local

1. Checkout `antigravity/ag-01-player-ui-20261030`
2. `dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj`
3. In Unity: `Presentation/` assemblies are pure C#9 — add to an asmdef that references `NguMach.Client.P1` asmdef only
4. Hook `P1ClientAdapter` to existing `P1Client` instance in `P1OnlinePanel.cs` (minimal composition only — will submit diff separately after Codex review)
5. `IP1UIAdapter` is the only surface Unity MonoBehaviours should call

## Next milestone

AG3 full (NPC dialogue panel), AG4 Unity settings panel, AG5 map Unity panel + `P1OnlinePanel.cs` composition hook diff.
