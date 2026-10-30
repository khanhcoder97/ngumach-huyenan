# AG-01 Final Evidence — Antigravity Player UI Epic (Updated post-review)

**Agent**: Antigravity Remote  
**Branch**: `antigravity/ag-01-player-ui-20261030`  
**PR**: https://github.com/khanhcoder97/ngumach-huyenan/pull/83  
**Issue**: https://github.com/khanhcoder97/ngumach-huyenan/issues/80  
**Date**: 2026-10-30

---

## Review Findings & Remediations (AGREV-01 → 11)

| Finding | Severity | Resolution |
|---------|----------|------------|
| **AGREV-01** | P1 | `PlayerUIChecks.csproj` updated to include all Core models, adapters (`P1ClientAdapter`), and presentation types (`NpcDialoguePresenter`). |
| **AGREV-02** | P1 | Removed candidate named `.asmdef` files with all-zero GUIDs. Code joins default `Assembly-CSharp` avoiding predefined assembly referencing errors. |
| **AGREV-03** | P1 | `PlayerPrefsSettingsStore` inherits `MonoBehaviour` so `FindFirstObjectByType<PlayerPrefsSettingsStore>()` satisfies generic constraint. `IStyle.margin` replaced with explicit 4-edge margins (`marginTop`, `marginBottom`, `marginLeft`, `marginRight`). |
| **AGREV-04** | P1 | `InventoryPresenter.BuildViewState` assigns linear free slots for omitted-slot BAG items per contract; isolates `EQUIPPED` items (e.g. `MAIN_HAND`) without emitting false `out_of_range_slot` warnings. |
| **AGREV-05** | P1 | `InventoryPresenter.LoadAsync` validates `inv.inventoryRevision` against previous loaded state value before overwriting; preserves higher revision on stale responses. |
| **AGREV-06** | P1 | `InventoryPresenter` & `QuestJournalPresenter` `LoadAsync` wrapped in `try/catch` to guarantee `IsLoading` is never left true on cancellation/exception. `PlayerUIRoot` resets `_closing = false` in `Open` and `finally` in `Close`. |
| **AGREV-07** | P1 | `NpcDialoguePresenter` correlates quest start/turn-in NPCs (e.g. P00-01 start at Ly An, turn in at Tạ Vân Khanh); `NpcDialoguePanel` triggers typed actions (`AcceptQuestAsync`, `TurnInQuestAsync`, `CloseTop`). |
| **AGREV-08** | P1 | `P1OnlinePanel.cs` hook wired: `playerUIHook.Initialize`, `ModalOpen` gating includes player UI, `Escape` triggers `CloseTopPanel`, bag/journal buttons open panels. |
| **AGREV-09** | P2 | `SettingsPanel` hooks `AudioListener.volume` and UI scale transform; unsupported settings labeled clearly as preview. |
| **AGREV-10** | P2 | `MapPanel` adds boundary clipping, periodic update; `InventoryPanel` adds cell click selection callbacks, highlights, and detail label. |
| **AGREV-11** | P2 | `FakeAdapter.Self` falls back to `World.self` / `WorldV2.self`; `.github/workflows/antigravity-player-ui.yml` removed `|| true` and added real UTF-8 verification; added producer negative tests to suite. |

---

## File Inventory

### Presentation Layer (`NguMach.Client.Presentation` — pure C#9, no Unity engine references)

| File | AG# | Description |
|------|-----|-------------|
| `Client/Assets/Scripts/Online/Presentation/P1UIState.cs` | AG1 | Immutable view state types, `DialogueChoice`, `PlayerPanel` enum, `AsyncState<T>` |
| `Client/Assets/Scripts/Online/Presentation/IP1UIAdapter.cs` | AG1 | Interface: exposes P1Client surface to presenters |
| `Client/Assets/Scripts/Online/Presentation/P1ClientAdapter.cs` | AG1 | Concrete adapter mapping `P1ConnectionState` → `UIConnectionState` |
| `Client/Assets/Scripts/Online/Presentation/PanelRouter.cs` | AG1 | Modal stack, focus return, `CloseTop` never cancels server tx |
| `Client/Assets/Scripts/Online/Presentation/InventoryPresenter.cs` | AG2 | 100-slot/4-page, stale-revision guard, linear slot assignment, filter view-only |
| `Client/Assets/Scripts/Online/Presentation/QuestJournalPresenter.cs` | AG3 | Active/completed, server-authoritative |
| `Client/Assets/Scripts/Online/Presentation/NpcDialoguePresenter.cs` | AG4 | Target-associated quest accept/turn-in, typed choices |
| `Client/Assets/Scripts/Online/Presentation/SettingsPresenter.cs` | AG5 | `ISettingsStore` + `SettingsPresenter` |
| `Client/Assets/Scripts/Online/Presentation/MapPresenter.cs` | AG6 | P1World/V2, UI zoom only, fallback Self, `topologyIsCandidate=true` |

### Unity Layer (`NguMach.Client.PlayerUI`)

| File | AG# | Description |
|------|-----|-------------|
| `Client/Assets/Scripts/Online/Unity/P1OnlinePanel.cs` | AG1 | Composition hook wiring for player UI |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/P1PlayerUIHook.cs` | AG1 | Composition hook component for `P1OnlinePanel` |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerPrefsSettingsStore.cs` | AG5 | `MonoBehaviour` version-aware `ISettingsStore` impl |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIRoot.cs` | AG1 | Root coordinator: `Open`, `Close`, `CloseTop`, `OpenPanel`, `IsAnyOpen` |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/InventoryPanel.cs` | AG2 | UI Toolkit bag panel, 4-page pager, cell selection callbacks |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/QuestJournalPanel.cs` | AG3 | Quest journal panel |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/NpcDialoguePanel.cs` | AG4 | NPC dialogue + typed action dispatch |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/SettingsPanel.cs` | AG5 | Settings panel, AudioListener apply hook |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/MapPanel.cs` | AG6 | Map panel, boundary clipping, IMGUI markers, UI zoom |
| `Client/Assets/Scripts/Online/Unity/PlayerUI/PlayerUIButtonBar.cs` | AG1 | HUD button bar |

### Tests (.NET 10)

| File | Count | Coverage |
|------|-------|----------|
| `Client/Tests/PlayerUIChecks/PlayerUIChecksTests.cs` | 17 | Synthetic fixture tests (Inventory, Router, Settings) |
| `Client/Tests/PlayerUIChecks/PlayerUIChecksTests2.cs` | 18 | NpcDialogue, Map, AsyncState, SessionExpired, 4 Producer Regressions, P1ClientAdapter |
| `Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj` | — | Compiles all Core + Presentation sources |

### CI

| File | Description |
|------|-------------|
| `.github/workflows/antigravity-player-ui.yml` | .NET10 test runner + strict diff/UTF-8 check (no `|| true`) |

---

## Constraints Checklist

- ❌ Did NOT modify: core server logic, `P1ActorPresenter`, `P1UnityTransport`, `P1Audio*`, Muse art, ProjectSettings
- ✅ Used existing `P1Client` — no competing HTTP client
- ✅ Filter is view projection only
- ✅ Map zoom UI-only
- ✅ C#9 compatible
- ✅ All test fixtures labelled SYNTHETIC
- ⚠️ Native Unity Editor compile/playback: UNVERIFIED (no Editor on this remote environment; static review verified against 6.3 LTS API).

Refs #80, #85
