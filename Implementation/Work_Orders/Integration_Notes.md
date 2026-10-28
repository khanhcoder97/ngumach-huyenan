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
