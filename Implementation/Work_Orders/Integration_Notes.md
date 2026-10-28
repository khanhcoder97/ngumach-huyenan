# Integration notes

Ghi yêu cầu liên-agent theo mẫu:

```md
## YYYY-MM-DD — From <agent> to <agent>
- Context:
- Requested interface or asset:
- Canonical IDs involved:
- Blocking: yes/no
- Proposed acceptance check:
```

## 2026-10-27 — From Qoder to OpenCode

- Context: `POST /p1/combat` (issue #13, QOD-06) exposes the existing authoritative combat service. Only the self-targeting `SK-MK-01` succeeds today; `SK-MK-02`/`SK-MK-03` return `invalid_payload`/`target_not_found` until the server registers world targets.
- Requested interface or asset: P1 `Envelope` with a `CombatInput` payload (`inputSequence`, `skillId`, `aimX`, `aimY`, optional `targetId`, optional `clientTimeUtc`), session ID in `X-Session-ID`. Success returns `200` with a `combat.effect` `CombatEvent` in `result`, plus `sessionId`, `revision` and `X-Correlation-ID`.
- Canonical IDs involved: `SK-MK-01`, `SK-MK-02`, `SK-MK-03`, `CLASS_MINH_KIEM`, `MAP_BEN_MUA`.
- Blocking: no.
- Proposed acceptance check: the client keeps one strictly increasing `inputSequence` for both `/p1/move` and `/p1/combat`; a successful cast advances that counter, and reusing a sequence on either endpoint returns `409 stale_sequence` without consuming the sequence.

## 2026-10-27 — From Qoder to OpenCode

- Context: QOD-07 adds read-only HTTP projections for the quest tracker and inventory panel so the client never invents local state.
- Requested interface or asset: `GET /p1/quests/{sessionId}` returns `result` as an array of `QuestState` (`questId`, `state`, `stepId`, `objectiveCounters`, `revision`); `GET /p1/inventory/{sessionId}` returns `result` as an `InventorySnapshot` (`inventoryRevision`, `items[]`, `currencies[]`). Both need only `X-Correlation-ID`; unknown session returns `404 session_not_found`.
- Canonical IDs involved: `P00-01`, `STEP_P00_01_PACKAGES`, `OBJ_P00_01_PACKAGES`, `MAP_BEN_MUA`.
- Blocking: no.
- Proposed acceptance check: a brand-new session reads `P00-01` as `AVAILABLE` with counter `0` and an inventory with `inventoryRevision: 0` plus empty `items`/`currencies`. Accept/turn-in and item grants have no endpoint yet — do not synthesize them client-side.
