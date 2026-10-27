# Ngu Mach Huyen An — Health Server

Minimal ASP.NET Core API (net10.0) exposing the health check, the P1 authoritative movement slice, and the QOD-03 combat, quest, inventory and teleport service skeletons.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check; unchanged from the P0 scaffold |
| POST | `/p1/sessions` | Create an in-memory player session on `MAP_BEN_MUA` |
| POST | `/p1/move` | Submit a `MoveIntent` envelope for the session in `X-Session-ID` |
| GET | `/p1/world/{sessionId}` | Read the latest authoritative `WorldSnapshot` |

Every response, including errors, carries `X-Correlation-ID`. A safe incoming value (1–64 characters of ASCII letters, digits, `-`, `_`, `.`) is echoed; otherwise a new GUID is generated.

## Run

```bash
dotnet run --project Server/Health/Health.csproj
```

The service listens on `http://localhost:5000` unless `ASPNETCORE_URLS` or launch settings override it.

The server loads `Implementation/Content/map_bounds.json` at startup by walking up from the working directory, content root and application base directory. Override with `Content__MapBoundsPath=/absolute/path/map_bounds.json` if needed. It likewise loads canonical `QuestDefinition` content from `Implementation/Content/Examples/QuestDefinition` (override with `Content__QuestsPath`) and canonical combat skills from `Implementation/Content/Examples/SkillDefinition` (override with `Content__SkillsPath`). Startup fails if the configured map is unknown, the spawn is outside bounds, the movement configuration is inconsistent, or a quest or skill definition is invalid.

```bash
dotnet build Server/Health/Health.csproj
```

## Session

```bash
curl -i -X POST http://localhost:5000/p1/sessions \
  -H "Content-Type: application/json" \
  -H "X-Correlation-ID: demo-session" \
  -d '{"characterId":"CHR_MINH_KIEM_01"}'
```

The body is optional. `characterId` defaults to a generated `CHR_<8 hex>` value; `classId` defaults to `CLASS_MINH_KIEM` and no other class is accepted in P1.

```json
{
  "schemaVersion": 1,
  "requestId": "0f2b6c3d4e5f4a6b8c9d0e1f2a3b4c5d",
  "serverTimeUtc": "2026-10-26T07:00:00Z",
  "sessionId": "8a7b6c5d4e3f4a2b1c0d9e8f7a6b5c4d",
  "revision": 1,
  "result": {
    "mapId": "MAP_BEN_MUA",
    "serverTick": 42,
    "revision": 1,
    "serverTimeUtc": "2026-10-26T07:00:00Z",
    "self": {
      "characterId": "CHR_MINH_KIEM_01",
      "classId": "CLASS_MINH_KIEM",
      "x": 18,
      "y": 0,
      "hp": 100,
      "maxHp": 100,
      "mp": 50,
      "maxMp": 50,
      "swordIntent": 0
    },
    "entities": []
  }
}
```

`201 Created` includes `Location: /p1/world/{sessionId}`.

## Move

The request body is a P1 `Envelope` whose payload is `MoveIntent`; the session ID travels in the `X-Session-ID` header.

```bash
curl -i -X POST http://localhost:5000/p1/move \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -H "X-Correlation-ID: demo-move-1" \
  -d '{
    "schemaVersion": 1,
    "requestId": "11111111111111111111111111111111",
    "idempotencyKey": "22222222222222222222222222222222",
    "sentAtUtc": "2026-10-26T07:00:00Z",
    "characterId": "CHR_MINH_KIEM_01",
    "payload": { "inputSequence": 1, "moveX": 1, "moveY": 0 }
  }'
```

A successful move returns `200` with the updated snapshot and an incremented `revision`.

Replaying the same `inputSequence` returns `409` with `stale_sequence` and does not change position:

```json
{
  "schemaVersion": 1,
  "requestId": "11111111111111111111111111111111",
  "serverTimeUtc": "2026-10-26T07:00:01Z",
  "revision": 2,
  "error": {
    "code": "stale_sequence",
    "messageKey": "P1.ERROR.STALE_SEQUENCE",
    "retryable": false,
    "fieldErrors": ["payload.inputSequence"],
    "correlationId": "demo-move-1"
  }
}
```

## Snapshot

```bash
curl -i http://localhost:5000/p1/world/<SESSION_ID> \
  -H "X-Correlation-ID: demo-world"
```

The response uses the same envelope as a successful move.

## Combat skeleton (QOD-03)

No combat endpoint is exposed yet. The registered `ICombatService` is the server-side seam for the future `combat.input` command:

- `ICombatSkillCatalog` loads `SK-MK-01..03` from canonical `SkillDefinition` content (class, cooldown, MP cost, targeting type, range, max targets). No balance values are duplicated in C#.
- `ICombatTargetProvider` is an in-memory target registry. It starts empty, so non-self skills return `target_not_found` until the world layer registers mobs or players.
- `InMemoryCombatService.Resolve(PlayerSession, CombatCommand)` validates the command, then applies gates in order: skill/class, per-actor `inputSequence`, target existence/map/alive/range, cooldown, and MP cost. Accepted casts decrement MP, advance `LastInputSequence` and `Revision`, and return a schema-shaped `combat.effect` `CombatEvent`. `LastInputSequence` is shared with movement, so clients must keep one monotonic input sequence per actor.
- Client `aimX`/`aimY` and `clientTimeUtc` are validated but not trusted. Damage and hit resolution are intentionally not implemented because no canonical damage formula or character stats exist yet; the returned event carries no `damage` or `hit`.
- `combat.effect` is returned to the caller, not broadcast; transport and persistence arrive with the real-time layer.

Internal failure codes: `unknown_skill`, `skill_not_available`, `invalid_target`, `target_not_found`, `target_not_alive`, `out_of_range`, `cooldown_active`, `insufficient_resource`, `unsupported_resource`, plus the shared `invalid_payload` and `stale_sequence`.

## Quest skeleton (QOD-03)

No quest endpoint is exposed yet. The registered `IQuestService` is the server-side seam for future accept/progress/turn-in commands:

- `IQuestCatalog` loads canonical `QuestDefinition` files (currently `P00-01`) from `Implementation/Content/Examples/QuestDefinition`; unknown quest IDs are rejected.
- `InMemoryQuestService` keeps per-character state behind `IQuestStateStore` and supports `GetState`, `GetStates`, `Accept`, `RecordObjective`, `TurnIn` and `Fail`.
- Allowed transitions: `LOCKED → AVAILABLE` when all prerequisites are `COMPLETED`, `AVAILABLE → ACTIVE` on accept, `ACTIVE → READY_TO_TURN_IN` when every canonical objective counter reaches its count, `READY_TO_TURN_IN → COMPLETED` on turn-in, and `ACTIVE`/`READY_TO_TURN_IN → FAILED` on failure.
- Objective progress is clamped to the canonical objective count and updates `revision`; invalid transitions return the current snapshot with `invalid_transition`. State rows are created lazily on first query/accept, and prerequisite availability is refreshed lazily on read.
- `RecordObjective` is an internal seam for server-side gameplay events (kill, collect, interact), not raw client input; a future endpoint must derive the amount from authoritative events.
- Canonical `QuestDefinition` has no step graph, so the initial `stepId` is derived from the first objective (`OBJ_…` → `STEP_…`); `P00-01` yields `STEP_P00_01_PACKAGES`.
- Rewards, XP, currency and items are not granted. Level-band eligibility is not enforced because `PlayerSession` has no level field yet.
- Internal failure codes: `unknown_quest`, `quest_not_found`, `invalid_transition`, `unknown_objective`, `invalid_amount`, plus the shared `invalid_payload`.

## Movement rules

- The server owns position. Client coordinates are never accepted; only a direction from `MoveIntent` is used.
- Direction is normalized, so diagonal input does not grant extra speed.
- Distance is `MoveSpeedWuPerSecond × elapsed server time`, with elapsed clamped to `MaxStepSeconds`. Client timestamps are validated for shape but never trusted for movement.
- The result is clamped to the canonical map bounds. Repeated movement into an edge stops at the edge rather than erroring.
- `inputSequence` must strictly increase. A stale or repeated sequence is rejected before any state changes.
- `characterId` in the envelope must match the session.
- `idempotencyKey` is validated but movement is not deduplicated in P1; the monotonic sequence is the replay guard. Economic actions will add idempotency records later.
- `serverTick` is derived from a monotonic process clock at the canonical 20 ticks/second.

## Inventory skeleton

`IInventoryService` owns the authoritative per-character inventory. It is registered in DI but is not exposed over HTTP yet. `GetSnapshot` returns a payload shaped like `Implementation/Contracts/P1/InventorySnapshot.schema.json`.

`Apply(session, InventoryMutation)` is a single all-or-nothing transaction:

- Validation runs before any state changes. Character, template, instance, location, slot and currency identifiers follow the P1 patterns.
- `expectedRevision` is optional. If present and stale, the call returns `revision_conflict` with `retryable = true` and the current snapshot. Otherwise the inventory revision increments exactly once.
- Grants always create a new `ITM_<32 uppercase hex>` instance because the item catalog and its stack limits are not loaded yet; there is no automatic stack merging.
- Removals address `instanceId`. An unknown instance returns `item_not_found`, over-removal returns `insufficient_items`, and the item version increments whenever its stack changes.
- `EQUIPPED` slots must be unique. A taken slot returns `slot_occupied`.
- Currency deltas are aggregated; a negative resulting balance returns `insufficient_currency`, and zero balances are omitted from snapshots.
- Durability is caller-supplied and is not yet validated against item content.

State is in memory and there is no seed inventory; a new character starts with no items and no currency.

## Teleport skeleton

`ITeleportService.Teleport(session, TeleportCommand)` is the authoritative teleport path. It is registered in DI but is not exposed over HTTP yet. The command is shaped like `Implementation/Contracts/P1/TeleportRequest.schema.json`.

- `mapId` must match `^MAP_[A-Z0-9_]+$` and exist in `map_bounds.json`; an unknown map returns `invalid_map`.
- Coordinates must be finite and inside that map's bounds. Teleport does not clamp; outside bounds returns `out_of_bounds`.
- `reason` must be one of `QUEST`, `DEATH_RETURN`, `CITY_RETURN`, `ADMIN`. `DEATH_RETURN` requires `hp <= 0`; every other reason requires `hp > 0`, otherwise `invalid_condition`.
- On success the session map, position and revision are updated under the session lock, and `LastMoveAtUtc` is reset so elapsed time before the teleport cannot be spent as movement.
- Teleport does not revive, heal or reset the movement sequence; respawn and death behavior stay in separate services.

## Configuration (`appsettings.json`)

| Key | Value | Source |
|---|---|---|
| `P1World:DefaultMapId` | `MAP_BEN_MUA` | Canonical P1 map |
| `P1World:SpawnX` / `SpawnY` | `18` / `0` | `MapDefinition/MAP_BEN_MUA.json` spawn point |
| `P1World:MoveSpeedWuPerSecond` | `6.0` | **Provisional** slice value; not yet locked in production data |
| `P1World:MaxStepSeconds` | `0.25` | Rejects long-frame jumps |
| `P1World:MaxStepDistanceWu` | `1.5` | Safety bound; must be ≥ speed × max step |
| `P1World:StartingHp` / `MaxHp` | `100` / `100` | `WorldSnapshot.example.json` |
| `P1World:StartingMp` / `MaxMp` | `50` / `50` | `WorldSnapshot.example.json` |

Environment overrides use the standard form, e.g. `P1World__MoveSpeedWuPerSecond=8`.

| Content key | Purpose |
|---|---|
| `Content:MapBoundsPath` | Optional absolute/relative override for `map_bounds.json` |
| `Content:QuestsPath` | Optional absolute/relative override for the `QuestDefinition` directory |
| `Content:SkillsPath` | Optional absolute/relative override for the `SkillDefinition` directory |

## Errors

| Status | Code | Meaning |
|---|---|---|
| 400 | `invalid_payload` | Malformed JSON, schema/pattern violation, wrong character, missing session header |
| 404 | `session_not_found` | Unknown session ID |
| 409 | `stale_sequence` | Sequence already applied; state unchanged |
| 413 | `invalid_payload` | Request body over 8 KB |
| 422 | `invalid_map` | Session map is not in `map_bounds.json` |
| 422 | `movement_too_far` | Defensive guard if a configured step exceeds `MaxStepDistanceWu` |

All error envelopes include `code`, `messageKey`, `retryable`, `fieldErrors` and `correlationId`. The inventory and teleport service error codes listed above are domain results; they have no HTTP mapping yet.

## Runtime smoke test

The `server-smoke` GitHub Actions workflow builds the server, starts it on `127.0.0.1:5080`, and runs `Server/Health/Smoke/smoke_p1.py`. The script uses only the Python standard library and verifies:

- `/health` returns `200` and echoes `X-Correlation-ID`.
- Session creation returns `201`, a `Location` header, the canonical spawn and `revision=1`.
- A valid move advances `x`, returns `revision=2` and keeps `y` unchanged.
- Replaying that sequence returns `409 stale_sequence`; the snapshot position and revision do not change.
- Wrong character, missing session header, unknown session and a 31-character `requestId` return the expected errors.
- A later move with sequence `2` succeeds, proving rejected requests did not consume the sequence.

Run the same flow locally:

```bash
dotnet build Server/Health/Health.csproj --configuration Release
(cd Server/Health && dotnet bin/Release/net10.0/Health.dll --urls http://127.0.0.1:5080) &
python3 Server/Health/Smoke/smoke_p1.py http://127.0.0.1:5080
```

Stop the background server process afterward. See `Implementation/Reports/QOD-04_verification_report.md` for the verification summary and OpenCode integration conditions.

## Manual verification

`dotnet` and Unity are not installed in the current authoring environment. The `server-build` workflow compiles this project on .NET 10, and `server-smoke` runs the runtime checks above. Both Python validators pass locally. The table below remains the manual equivalent for a machine with the .NET SDK.

| # | Step | Expected |
|---|---|---|
| 1 | `dotnet run --project Server/Health/Health.csproj` | Starts; logs `Loaded map bounds for 46 maps`, `Loaded 3 combat skills` and `Loaded quest definitions: 1.` |
| 2 | `GET /health` | `200`, `status: ok`, echoed `X-Correlation-ID` |
| 3 | Create session with `CHR_MINH_KIEM_01` | `201`, `Location` header, `MAP_BEN_MUA`, `x=18`, `y=0`, `revision=1` |
| 4 | Move `inputSequence=1`, `moveX=1` | `200`, `x>18`, `revision=2` |
| 5 | Repeat `inputSequence=1` | `409 stale_sequence`; snapshot position unchanged |
| 6 | Move with a different `characterId` | `400 invalid_payload` |
| 7 | Move without `X-Session-ID` | `400 invalid_payload` |
| 8 | Move with an unknown session ID | `404 session_not_found` |
| 9 | Send sequences 1..20 with `moveX=-1`, ~300 ms apart | `x` decreases and stops at `0` |
| 10 | Move with a 31-character `requestId` | `400 invalid_payload` |
| 11 | Any request | Response always has `X-Correlation-ID` |

## Current limits

- Sessions are in memory and lost on restart; there is no database, authentication or real-time transport.
- `entities` is always empty; the combat target registry starts empty and the combat, quest, inventory and teleport services are not exposed over HTTP.
- Combat is a service skeleton with no endpoint: damage, hit chance, telegraphs, death and loot are not implemented, and `combat.effect` only records an accepted cast and its cooldown.
- Quest state is in memory, has no endpoint, and only one canonical `QuestDefinition` (`P00-01`) is loaded. Rewards, level-band eligibility and multi-step graphs are not implemented.
- Inventory has no item catalog, stack-limit enforcement, durability rules or seeded starting items.
- Teleport uses map bounds only; there is no walkability, portal, cooldown or respawn logic.
- Movement speed and starting HP/MP are slice defaults, not locked balance values.
