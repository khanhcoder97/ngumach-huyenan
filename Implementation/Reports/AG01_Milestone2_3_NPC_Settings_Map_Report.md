# AG01 — Milestone 2+3 Report: NPC Dialogue, Settings, Map Integration + Handoff

**Epic**: AG-01 Player UI  
**Issue**: https://github.com/khanhcoder97/ngumach-huyenan/issues/80  
**Branch**: `antigravity/ag-01-player-ui-20261030`  
**Commit Milestone 2**: `31f621f`  
**Date**: 2026-10-30, Asia/Tokyo

---

## Files tạo trong Milestone 2+3

| File | Milestone | Mô tả |
|---|---|---|
| `Presentation/NpcDialoguePresenter.cs` | 2 | AG3: InteractAsync, AcceptQuestAsync, TurnInQuestAsync |
| `Unity/PlayerUI/PlayerPrefsSettingsStore.cs` | 2 | AG4: ISettingsStore → Unity PlayerPrefs, version-aware |
| `Unity/PlayerUI/P1PlayerUIHook.cs` | 2 | AG1: Composition hook nối P1OnlinePanel |
| `Presentation/NguMach.Client.Presentation.asmdef` | 2 | Assembly definition, noEngineReferences |
| `Unity/PlayerUI/NguMach.Client.PlayerUI.asmdef` | 2 | Assembly definition, Unity ref |
| `Tests/PlayerUIChecks/PlayerUIChecksTests2.cs` | 2 | +12 synthetic tests |
| `docs/production/Antigravity_Player_UI_Handoff_vi.md` | 3 | Handoff doc đầy đủ |
| `Unity/PlayerUI/PlayerUIRoot.cs` | 2 | (subagent) Root MonoBehaviour |
| `Unity/PlayerUI/InventoryPanel.cs` | 2 | (subagent) Unity UI panel |
| `Unity/PlayerUI/QuestJournalPanel.cs` | 2 | (subagent) Unity UI panel |
| `Unity/PlayerUI/NpcDialoguePanel.cs` | 2 | (subagent) Unity UI panel |
| `Unity/PlayerUI/SettingsPanel.cs` | 2 | (subagent) Unity UI panel |
| `Unity/PlayerUI/MapPanel.cs` | 2 | (subagent) Unity UI panel |
| `Unity/PlayerUI/PlayerUIButtonBar.cs` | 2 | (subagent) HUD button bar |

## Test coverage tổng cộng (29+ tests)

Milestone 1: 17 tests — InventoryPresenter, PanelRouter, QuestJournal, Settings  
Milestone 2: 12 tests — NpcDialogue, Map, AsyncState, SessionExpired scenarios

## Constraints verified

- [x] NpcDialoguePresenter không ghi story flag hoặc reward local
- [x] Retry uncertain trở lại cùng pending command
- [x] PlayerPrefsSettingsStore: schema version bump → reset to default
- [x] P1PlayerUIHook: minimal diff, không rewrite P1OnlinePanel
- [x] asmdef tách `noEngineReferences` cho Presentation layer
- [x] Map topology: `topologyIsCandidate = true` — không sửa 349 tọa độ

## UNVERIFIED

- Unity compile/import: UNVERIFIED  
- UIDocument UXML layout: cần tạo trong Unity Editor  
- Device test keyboard/touch: UNVERIFIED  
- Catalog display name resolver: UNRESOLVED placeholder

## Integration steps cho Codex

Xem `docs/production/Antigravity_Player_UI_Handoff_vi.md` để biết:
1. Wire `P1PlayerUIHook` vào `P1OnlinePanel`
2. Cách tạo asmdef references
3. Gán HUD buttons
4. Feature matrix live/preview/unsupported/UNVERIFIED
