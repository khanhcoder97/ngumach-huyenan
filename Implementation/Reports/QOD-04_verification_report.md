# QOD-04 — Verification and handoff report

- **Owner:** Qoder (server / contracts / tools)
- **Date:** 2026-10-27
- **Branch:** `qoder/qod-04-runtime-smoke`
- **PR:** [#10](https://github.com/khanhcoder97/ngumach-huyenan/pull/10), stacked on `qoder/p1-server-slice` (PR #6)
- **Status:** runtime smoke test green; PRs #6–#10 await owner review/merge.

## Verification results

| Check | Command / workflow | Result |
|---|---|---|
| Content validation | `python Implementation/Tools/validate_content.py` | PASS — 7 schemas, 9 examples |
| Contract validation | `python Implementation/Tools/validate_contracts.py` | PASS — 8 schemas, 8 examples |
| Compile | `server-build` workflow (`dotnet build … --configuration Release` on .NET 10) | PASS |
| Runtime HTTP slice | `server-smoke` workflow + `Server/Health/Smoke/smoke_p1.py` | PASS — 44 checks |
| Smoke script syntax | `python -m py_compile Server/Health/Smoke/smoke_p1.py` | PASS |

Runtime evidence: [server-smoke run 40409654618](https://github.com/khanhcoder97/ngumach-huyenan/actions/runs/40409654618/job/121876662653) — `PASS: 44 smoke checks against http://127.0.0.1:5080`, server healthy after 2s.

Local authoring machine has no .NET SDK or Unity. All runtime verification therefore runs in GitHub Actions on .NET 10; the manual table in `Server/Health/README.md` remains the local equivalent.

## What the smoke test covers

- `/health` returns `200`, `status: ok`, and echoes a safe `X-Correlation-ID`.
- `POST /p1/sessions` returns `201`, `Location: /p1/world/{sessionId}`, `MAP_BEN_MUA`, spawn `(18, 0)`, `revision=1`.
- A valid move returns `200`, advances `x`, keeps `y`, and increments `revision` to `2`.
- Replaying `inputSequence=1` returns `409 stale_sequence`; a following snapshot keeps the same position and revision.
- A wrong `characterId` returns `400 invalid_payload` with `characterId` in `fieldErrors`.
- A missing `X-Session-ID` returns `400 invalid_payload` with `X-Session-ID` in `fieldErrors`.
- An unknown session returns `404 session_not_found`.
- A 31-character `requestId` returns `400 invalid_payload` with `requestId` in `fieldErrors`.
- A later move with `inputSequence=2` succeeds (`revision=3`), proving rejected requests did not consume the sequence.
- Every checked response carries the expected `X-Correlation-ID`.

## OpenCode integration conditions

### Base and headers

- Base URL in CI: `http://127.0.0.1:5080`. Local default is `http://localhost:5000` unless overridden.
- Send `Content-Type: application/json` on `POST`.
- Send a safe `X-Correlation-ID` (1–64 ASCII letters, digits, `-`, `_`, `.`); the server echoes it or generates one.
- Send `X-Session-ID` on `POST /p1/move`; it is not part of the JSON envelope.
- Do not invent client positions. Movement accepts only direction components; the server owns position.

### Endpoints

| Method | Path | Contract |
|---|---|---|
| GET | `/health` | Liveness; unchanged |
| POST | `/p1/sessions` | Optional `{ "characterId", "classId" }`; default class `CLASS_MINH_KIEM` |
| POST | `/p1/move` | P1 `Envelope` + `MoveIntent` payload |
| GET | `/p1/world/{sessionId}` | Latest authoritative `WorldSnapshot` |

`POST /p1/move` requires `schemaVersion=1`, 32-character lowercase hex `requestId` and `idempotencyKey`, UTC `sentAtUtc` in `YYYY-MM-DDTHH:MM:SSZ`, `characterId` matching the session, and a payload with a strictly increasing `inputSequence` plus `moveX`/`moveY` in `[-1, 1]`.

Success responses add `schemaVersion`, `requestId`, `sessionId`, `serverTimeUtc`, `revision`, and `result`. Errors use `error.code`, `error.messageKey`, `error.retryable`, `error.fieldErrors`, and `error.correlationId`, with the same HTTP status for the same failure across calls.

### Error contract

| Status | Code | Client behavior |
|---|---|---|
| 400 | `invalid_payload` | Fix the request; do not retry unchanged |
| 404 | `session_not_found` | Create a new session |
| 409 | `stale_sequence` | Drop the input; do not resend the same sequence |
| 413 | `invalid_payload` | Body exceeded 8 KB |
| 422 | `invalid_map` | Server configuration/content issue |
| 422 | `movement_too_far` | Defensive server guard; do not increase client step size |

### Session and content assumptions

- Sessions and gameplay state are in memory; a server restart invalidates every session ID.
- Canonical map is `MAP_BEN_MUA`; spawn is `(18, 0)`; bounds come from `Implementation/Content/map_bounds.json`.
- `entities` is always empty in P1; the client should not expect mobs or other players yet.
- Movement speed and starting HP/MP are provisional slice values, not locked balance data.
- QOD-03 combat, quest, inventory and teleport skeletons are delivered in sibling PRs #7–#9 and are registered without endpoints; the client must not call or assume them yet.
- `Implementation/HANDOFF_OPENCODE_P1.md` still mentions `MAP_LANG_MOI`; its owner must update it. The server intentionally rejects that map.

### Running the smoke test locally

```bash
dotnet build Server/Health/Health.csproj --configuration Release
(cd Server/Health && dotnet bin/Release/net10.0/Health.dll --urls http://127.0.0.1:5080) &
python3 Server/Health/Smoke/smoke_p1.py http://127.0.0.1:5080
```

Expected final line: `PASS: 44 smoke checks against http://127.0.0.1:5080`. Stop the server process afterward.

## Files changed in QOD-04

- `.github/workflows/server-smoke.yml` — build, start, poll, smoke, stop, upload log.
- `Server/Health/Smoke/smoke_p1.py` — standard-library runtime checks.
- `Server/Health/README.md` — runtime smoke instructions and updated verification notes.

No production code, contracts, content or dependencies changed.

## Remaining work

1. Owner review and merge of PRs #6–#10 in order (#6 first; #7–#10 are stacked on it).
2. After #6 merges, retarget #7–#10 to `main` and re-run checks.
3. Expand runtime tests when endpoints for combat/quest/inventory/teleport exist.
4. Replace in-memory persistence and add authentication/transport only after P1 acceptance.
