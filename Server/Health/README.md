# Ngu Mach Huyen An — Health Server

Minimal ASP.NET Core API (net10.0) exposing the health check, the P1 authoritative movement slice, the QOD-03 combat, quest, inventory and teleport service skeletons, the QOD-13 quest-progress/interact slice, and the QOD-14 turn-in/reward slice.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check; unchanged from the P0 scaffold |
| POST | `/p1/sessions` | Create an in-memory player session on `MAP_BEN_MUA` |
| POST | `/p1/move` | Submit a `MoveIntent` envelope for the session in `X-Session-ID` |
| GET | `/p1/world/{sessionId}` | Read the latest authoritative `WorldSnapshot` |
| POST | `/p1/combat` | Submit a `CombatInput` envelope for the session in `X-Session-ID` |
| GET | `/p1/quests/{sessionId}` | Read the authoritative quest states for the session character |
| GET | `/p1/inventory/{sessionId}` | Read the authoritative `InventorySnapshot` for the session character |
| POST | `/p1/quests/accept` | Accept an `AVAILABLE` quest for the session in `X-Session-ID` (feature-flagged, off by default) |
| POST | `/p1/world/interact` | Claim an `INTERACTABLE` or gather from a `GATHER_NODE` world entity (feature-flagged, off by default) |
| POST | `/p1/quests/turnin` | Turn in a `READY_TO_TURN_IN` quest and receive atomic rewards (feature-flagged, off by default) |

Every response, including errors, carries `X-Correlation-ID`. A safe incoming value (1–64 characters of ASCII letters, digits, `-`, `_`, `.`) is echoed; otherwise a new GUID is generated.

## Run

```bash
dotnet run --project Server/Health/Health.csproj
```

The service listens on `http://localhost:5000` unless `ASPNETCORE_URLS` or launch settings override it.

The server loads `Implementation/Content/map_bounds.json` at startup by walking up from the working directory, content root and application base directory. Override with `Content__MapBoundsPath=/absolute/path/map_bounds.json` if needed. It likewise loads canonical `QuestDefinition` content from `Implementation/Content/Examples/QuestDefinition` (override with `Content__QuestsPath`), canonical combat skills from `Implementation/Content/Examples/SkillDefinition` (override with `Content__SkillsPath`), and the built world record catalog from `Implementation/Content/Runtime/world_records.json` (override with `Content__WorldRecordsPath`). Startup fails if the configured map is unknown, the spawn is outside bounds, the movement configuration is inconsistent, a quest or skill definition is invalid, or a quest objective target has no matching world record/NPC anchor.

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

## Combat

`POST /p1/combat` accepts a P1 `Envelope` whose payload is `CombatInput` and uses the same `X-Session-ID` header. Fields follow `Implementation/Contracts/P1/CombatInput.schema.json`; `inputSequence`, `skillId`, `aimX` and `aimY` are required, `targetId` is required for non-self skills.

```bash
curl -i -X POST http://localhost:5000/p1/combat \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -H "X-Correlation-ID: demo-combat-1" \
  -d '{
    "schemaVersion": 1,
    "requestId": "33333333333333333333333333333333",
    "idempotencyKey": "44444444444444444444444444444444",
    "sentAtUtc": "2026-10-26T07:00:02Z",
    "characterId": "CHR_MINH_KIEM_01",
    "payload": {
      "inputSequence": 3,
      "skillId": "SK-MK-01",
      "aimX": 1,
      "aimY": 0
    }
  }'
```

A successful cast returns `200` with the schema-shaped `combat.effect` event, the session ID and the post-cast `revision`:

```json
{
  "schemaVersion": 1,
  "requestId": "33333333333333333333333333333333",
  "sessionId": "<SESSION_ID>",
  "serverTimeUtc": "2026-10-26T07:00:02Z",
  "revision": 4,
  "result": {
    "eventId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "eventType": "combat.effect",
    "aggregateId": "CHR_MINH_KIEM_01",
    "aggregateRevision": 4,
    "emittedAtUtc": "2026-10-26T07:00:02Z",
    "schemaVersion": 1,
    "payload": {
      "sourceId": "CHR_MINH_KIEM_01",
      "targetId": "CHR_MINH_KIEM_01",
      "skillId": "SK-MK-01",
      "cooldownEndsAtUtc": "2026-10-26T07:00:12Z"
    }
  }
}
```

- `SK-MK-01` is `SELF`, so the caller is its own target and no world entity is needed. `SK-MK-02` without `targetId` returns `400 invalid_payload`; `SK-MK-02/03` with an unregistered target returns `404 target_not_found`. Damage, hit chance and death are intentionally absent until canonical stat/damage data and authoritative world targets exist.
- The server still owns results: `aimX`/`aimY` and `clientTimeUtc` are validated but never trusted for damage or hit resolution.
- **One input sequence per character.** `inputSequence` is shared with `/p1/move`; a combat cast advances `LastInputSequence` exactly like a move, so the client must keep a single strictly increasing counter across both endpoints. Reusing a sequence returns `409 stale_sequence`.
- Rejected casts do not consume the sequence and do not change `revision`, MP or position.

## Snapshot

```bash
curl -i http://localhost:5000/p1/world/<SESSION_ID> \
  -H "X-Correlation-ID: demo-world"
```

The response uses the same envelope as a successful move.

## Quest and inventory reads

Both are read-only projections for client UI. No accept/turn-in or add/remove command is exposed; those stay server-side seams.

```bash
curl -i http://localhost:5000/p1/quests/<SESSION_ID> \
  -H "X-Correlation-ID: demo-quests"

curl -i http://localhost:5000/p1/inventory/<SESSION_ID> \
  -H "X-Correlation-ID: demo-inventory"
```

`/p1/quests/{sessionId}` returns one `QuestState` per canonical `QuestDefinition`, using the state already validated by `QuestState.schema.json`:

```json
{
  "schemaVersion": 1,
  "requestId": "55555555555555555555555555555555",
  "sessionId": "<SESSION_ID>",
  "serverTimeUtc": "2026-10-26T07:00:03Z",
  "result": [
    {
      "questId": "P00-01",
      "state": "AVAILABLE",
      "stepId": "STEP_P00_01_PACKAGES",
      "objectiveCounters": { "OBJ_P00_01_PACKAGES": 0 },
      "revision": 1
    }
  ]
}
```

`/p1/inventory/{sessionId}` returns an `InventorySnapshot`. A session that has not been granted anything yet returns `inventoryRevision: 0` with empty `items` and `currencies`; the server does not seed starting gear.

Unknown session IDs return `404 session_not_found`. Reading quest state creates the row lazily so availability is refreshed; it never changes position, revision or resources of the world snapshot.

## Quest accept (feature-flagged)

`POST /p1/quests/accept` is mapped only when `P1:QuestAccept:Enabled=true`; otherwise the POST handler is not mapped and the request falls through to the `GET /p1/quests/{sessionId}` read route template, which answers `405`. It is **off by default** because the interaction line-of-sight guard has no walkability bundle yet — enabling it logs `DEV STUB: P1:QuestAccept is enabled...` at startup. Contract: `Implementation/Contracts/P1/QuestAcceptRequest.schema.json` + `QuestAcceptResponse.schema.json`; proposal and guard order in `Implementation/Work_Orders/Proposals/QOD-08_QuestAcceptRequest_vi.md`.

```bash
curl -i -X POST http://localhost:5000/p1/quests/accept \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -H "X-Correlation-ID: demo-accept" \
  -d '{
    "schemaVersion": 1,
    "requestId": "55555555555555555555555555555555",
    "idempotencyKey": "99999999999999999999999999999999",
    "sentAtUtc": "2026-10-28T07:00:00Z",
    "characterId": "CHR_MINH_KIEM_01",
    "payload": { "questId": "P00-01", "npcId": "NPC_LYAN" }
  }'
```

Guards run in order: session → quest catalog → `npcId` = canonical `startNpcId` → same map/floor → foot distance ≤ `MaxInteractionDistanceWu` → prerequisites/level → `AVAILABLE`. Success flips the quest to `ACTIVE` exactly once and leaves position, HP/MP and the movement/combat `inputSequence` untouched. `idempotencyKey` is scoped to the character: replaying the same key with the same payload returns the first result; the same key with a different payload returns `409 idempotency_conflict`.

Line of sight is enforced from `MapTopology` bundles (`Implementation/Content/Examples/MapTopology`): a query must share `mapId`+`floorId`, stay inside walkable polygons, and not cross a blocked polygon from the actor foot to the NPC anchor. Only bundles with `reviewState: REVIEWED` are used; the shipped fixture is `SYNTHETIC_TEST_ONLY`, so the current server reports `not_enforced` and the endpoint keeps its DEV STUB warning. Bundle rules are documented in `Implementation/Work_Orders/Proposals/QOD-10_MapTopology_vi.md` and validated by `python Implementation/Tools/validate_topology.py`.

NPC anchors come from `Implementation/Content/Runtime/npc_anchors.json`, generated from the canonical spawn manifest:

```bash
python Implementation/Tools/build_npc_anchors.py
```

## Interact (feature-flagged)

`POST /p1/world/interact` is mapped only when `P1:Interact:Enabled=true`; otherwise the POST handler is not mapped and the request falls through to the `GET /p1/world/{sessionId}` read route template, which answers `405`. It is **off by default** because no reviewed walkability bundle exists yet — enabling it logs `DEV FIXTURE: P1:Interact is enabled...` at startup. Contract: `Implementation/Contracts/P1/InteractRequest.schema.json` + `InteractResponse.schema.json`; proposal and guard order in `Implementation/Work_Orders/Proposals/QOD-13_QuestProgressGathering_vi.md`.

```bash
curl -i -X POST http://localhost:5000/p1/world/interact \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: <SESSION_ID>" \
  -H "X-Correlation-ID: demo-interact" \
  -d '{
    "schemaVersion": 1,
    "requestId": "66666666666666666666666666666666",
    "idempotencyKey": "77777777777777777777777777777777",
    "sentAtUtc": "2026-10-29T07:00:00Z",
    "characterId": "CHR_MINH_KIEM_01",
    "payload": { "targetId": "ENT_MAN_BM_OBJ_BM_PACKAGE_01" }
  }'
```

A successful claim returns `200` with an `InteractResult`: `interactionId` (hex32), `targetId`, `recordId` (the world record the entity resolved to), `kind` (`INTERACTABLE` or `GATHER_NODE`), `outcome` (`collected` or `gathered`), `targetState` (`DEPLETED` for shared interactables, `AVAILABLE` for per-character claims — gather nodes and the P00-01 packages), `claimedAtUtc`, optional `respawnAtUtc`, optional `yield` (`itemId` + `quantity` for gather nodes) and `questUpdates` — the changed `QuestState` rows from the server-owned `RecordVerifiedEvent` call:

```json
{
  "schemaVersion": 1,
  "requestId": "66666666666666666666666666666666",
  "sessionId": "<SESSION_ID>",
  "serverTimeUtc": "2026-10-29T07:00:00Z",
  "result": {
    "interactionId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "targetId": "ENT_MAN_BM_OBJ_BM_PACKAGE_01",
    "recordId": "MAN-BM-OBJ_BM_PACKAGE_01",
    "kind": "INTERACTABLE",
    "outcome": "collected",
    "targetState": "AVAILABLE",
    "claimedAtUtc": "2026-10-29T07:00:00Z",
    "respawnAtUtc": "2026-10-29T07:00:20Z",
    "questUpdates": [
      {
        "questId": "P00-01",
        "state": "ACTIVE",
        "stepId": "STEP_P00_01_PACKAGES",
        "objectiveCounters": { "OBJ_P00_01_PACKAGES": 1 },
        "revision": 3
      }
    ]
  }
}
```

Guards run in order: idempotency replay (`idempotencyKey` scoped to the character; same key + same payload returns the stored result, same key + different payload → `409 idempotency_conflict`) → target exists in the world entity registry → kind is `INTERACTABLE` or `GATHER_NODE` → same map/floor → foot distance ≤ `MaxInteractionDistanceWu` (5) → line of sight (only with a `REVIEWED` topology bundle; otherwise `not_enforced`) → profession gate (`AssumedProfessionLevel` vs the record's `professionLevelRequired`; a DEV-fixture stand-in until character professions exist) → claim (`SHARED` interactables despawn the shared registry entry; `PER_CHARACTER` interactables and gather nodes use a per-character claim window in `GatherClaimStore`) → yield roll and inventory grant for gather nodes → `RecordVerifiedEvent` for quest progress. Rejected claims change no state and grant no items.

The `P00-01` packages (`ENT_MAN_BM_OBJ_BM_PACKAGE_01..03` at x=36/44/52) are the minimal acceptance slice: collecting all three flips the quest to `READY_TO_TURN_IN`. They carry `claimPolicy: PER_CHARACTER` in `world_entities_bm.json` (source: `Production_Rules_Complete_v1_vi.md` §5 — each package counts at most once per character and never removes the world item for other characters), so two characters can collect all three without waiting for a global respawn; the 20 s window is a **labelled DEV fixture**, not canonical balance. World records come from `Implementation/Content/Runtime/world_records.json` (352 records built by `python Implementation/Tools/build_world_records.py`); entity registries are rebuilt by `python Implementation/Tools/build_world_entities.py`, and CI verifies both files have no drift from their sources.

Failure codes: `invalid_payload` (400), `session_not_found` (404), `target_not_found` (404, retryable), `invalid_target` (400), `out_of_range` (422, retryable), `target_not_available` (409), `profession_level_insufficient` (422), `idempotency_conflict` (409).

## Combat internals (QOD-03/QOD-06)

`POST /p1/combat` exposes `ICombatService` for the self-targeting `SK-MK-01` path. The service stays the server-side seam for future `combat.input` work:

- `ICombatSkillCatalog` loads `SK-MK-01..03` from canonical `SkillDefinition` content (class, cooldown, MP cost, targeting type, range, angle, max targets, per-mode coefficients, telegraph and VFX key). No balance values are duplicated in C#.
- `ICombatTargetProvider` is a composite: the world-entity registry resolves alive mobs/bosses by entity instance ID (map/floor/position from canonical placements), plus an in-memory registry used by dev/test. Non-self skills still return `target_not_found` for dead, NPC or unregistered IDs.
- `InMemoryCombatService.Resolve(PlayerSession, CombatCommand)` validates the command, then applies gates in order: skill/class, per-actor `inputSequence`, target existence/map/alive/range, cooldown, and MP cost. Accepted casts decrement MP, advance `LastInputSequence` and `Revision`, and return a schema-shaped `combat.effect` `CombatEvent`. `LastInputSequence` is shared with movement, so clients must keep one monotonic input sequence per actor.
- Client `aimX`/`aimY` and `clientTimeUtc` are validated but not trusted. The canonical damage formula now exists as pure domain (`DamageFormula` + seeded `CombatRng`, QOD-16 phase 1) behind the `P1:CombatDamage` gate, but casts still return no `damage` or `hit`: nothing applies the formula until the QOD-16 proposal is approved.
- `combat.effect` is returned to the caller, not broadcast; transport and persistence arrive with the real-time layer.
- `idempotencyKey` is scoped to the character: replaying an accepted cast with the same key and payload returns the stored outcome before the stale-sequence guard; the same key with a different payload returns `409 idempotency_conflict`.

Internal failure codes: `unknown_skill`, `skill_not_available`, `invalid_target`, `target_not_found`, `target_not_alive`, `out_of_range`, `cooldown_active`, `insufficient_resource`, `unsupported_resource`, plus the shared `invalid_payload` and `stale_sequence`.

## Combat damage domain (QOD-16, phase 1)

The first QOD-16 slice lands the combat subset as internal domain only — no wire change and no damage applied until the proposal `Implementation/Work_Orders/Proposals/QOD-16_WorldProjectionCombatSubset_vi.md` is approved:

- `DamageFormula` implements Production Rules §2 exactly: hit roll `clamp(0.90 + accuracy − dodge, 0.05, 0.98)`, capped crit roll, `raw = (attack + flat) × coefficient × rankMultiplier × (1 + bonus)`, `mitigation = 100/(100 + max(0, armor))`, element `1 − clamp(resist, 0, 0.5 PvE / 0.3 PvP)`, crit ×1.5, DR cap 0.8, final `max(1, floor(...))`. The locked oracle holds: attack 20, coefficient 1.5, armor 10 → 27; crit → 40. `CombatRng` is seeded per `(castId, targetId, hitIndex)` with `combat-rng-v1` for reproducible audits.
- `Implementation/Tools/build_combat_mob_stats.py` deterministically exports `Implementation/Content/Runtime/combat_mob_stats_v1.json` from Art Bible §12 + Production Rules §4 (3 archetypes with the owner-locked `REFERENCE_L5` table, elite ×6/×1.6/×1.8, Mãng Cốt boss `BOSSDATA_BLOCKED` because `phaseGuard`/`interruptible` data does not exist yet). CI rebuilds the bundle and fails on drift.
- `SK-MK-03` range comes from the `combat.skillRangeMigrationWu` migration in `completion_v1.json` (4.4 WU) — the skill example intentionally has no `rangeWu`. Loaded only when the gate is on.
- `GuardPrecisionLoader` reads the owner-locked DEC-022 bundle (`Implementation/Content/DesignBaselines/p1_guard_precision_v1.json`, `DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION`) behind the same gate and validates window `[T, T+8)`, whiff `[T+8, T+28)`, counter-on-next-tick, 120°/4.4 WU cone, DR bucket cap and the 27/8/21/5 + counter 32/49 oracle arithmetic at load. `GuardTimeline` provides the pure window/cone/DR-bucket/deterministic-ordering helpers; `COUNTER_CONFIRMED` is a v2 event semantic (confirmation + one reserved counter, **not** counter damage). The runtime guard/counter state machine lands with QOD-17.

- `CombatEventStore` is the internal reliable event read for v2: typed events (`CAST_START`/`COUNTER_CONFIRMED`/`IMPACT`/`MISS`/`CANCEL`/`END`/`DEATH`), a monotonic per-session cursor starting at 1, a bounded per-session buffer (`P1:CombatEventStream`, DEV budget 512/page 200) and explicit resync instead of silent drops — readers behind the evicted range get `BUFFER_OVERFLOW`, stale cursors from a previous stream lifetime get `CURSOR_TOO_OLD`, both with no events (reconcile from the next snapshot). Appending the same `eventId` is a replay-safe no-op; reconnect cleanup is `RemoveSession`. The v2 read endpoint and combat tick engine land with QOD-17.
- `WorldAoiProjectionService` is the v2 audience filter: internal candidates stay full-map, while each session receives MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE only within the same map instance/floor/phase and AOI **enter 40 WU / leave 48 WU** (8 WU hysteresis), sourced from Online_Persistence_Release_Complete §2. NPCs project as `INVULNERABLE`/`targetable:false`/hp 0, the blocked boss as `BLOCKED` (never `DEAD`, not targetable), mobs with `REFERENCE_L5` hp and `ALIVE`/`DEAD`; claimables expose only a per-caller `availability` (`AVAILABLE`/`COOLDOWN`, per-character claim windows, no quest flags). Reconnect cleanup is `RemoveSession`, which also forgets the hysteresis memory. Phase/instance are labelled DEV placeholders (`OPEN_WORLD`, `#1`); the v2 snapshot endpoint lands with QOD-17.
- `CombatDamageFeature` gates everything: `P1:CombatDamage:Enabled=false` by default, and touching the bundle or migration while disabled throws. Enabling it logs a `DEV STUB` warning and changes nothing on the wire.
- `WorldEntityProjectionService` is the internal entity read-model (entityId, kind, map, floor, x, y, state, revision, lifeId, hp/maxHp): NPCs stay invulnerable with hp 0 (Art Bible §13), bosses stay hp 0 while `BOSSDATA_BLOCKED`, mobs use the `REFERENCE_L5` archetype stats (elite suffix applies the elite multipliers), and `lifeId` bumps on respawn. It is not yet wired into the world snapshot.

## Quest skeleton (QOD-03)

`GET /p1/quests/{sessionId}` exposes the state list read-only. No accept/turn-in command is exposed yet; `IQuestService` remains the server-side seam for those:

- `IQuestCatalog` loads canonical `QuestDefinition` files (currently `P00-01`) from `Implementation/Content/Examples/QuestDefinition`; unknown quest IDs are rejected.
- `InMemoryQuestService` keeps per-character state behind `IQuestStateStore` and supports `GetState`, `GetStates`, `Accept`, `RecordVerifiedEvent`, `TurnIn` and `Fail`.
- Allowed transitions: `LOCKED → AVAILABLE` when all prerequisites are `COMPLETED`, `AVAILABLE → ACTIVE` on accept, `ACTIVE → READY_TO_TURN_IN` when every canonical objective counter reaches its count, `READY_TO_TURN_IN → COMPLETED` on turn-in, and `ACTIVE`/`READY_TO_TURN_IN → FAILED` on failure.
- Objective progress is clamped to the canonical objective count and updates `revision`; invalid transitions return the current snapshot with `invalid_transition`. State rows are created lazily on first query/accept, and prerequisite availability is refreshed lazily on read.
- `RecordVerifiedEvent(actor, eventId, eventType, recordId, mapId)` is the only progress path: server-verified gameplay events (interact/gather claims, talks, kills) advance objective counters. Each event contributes **once**: `COLLECT`/`INTERACT`/`TALK` objectives are keyed by distinct `recordId` (`R:{recordId}`), `KILL` objectives by event (`E:{eventId}`). No event can double-count the same record, and events on another map never contribute. It is an internal seam for server-side events, not raw client input.
- Startup validation rejects quests whose `COLLECT`/`INTERACT` objective targets resolve to no world record on the objective's map, or whose `TALK` targets have no NPC anchor (`QuestCatalogValidator`); dangling IDs fail the boot instead of silently blocking progress.
- Canonical `QuestDefinition` has no step graph, so the initial `stepId` is derived from the first objective (`OBJ_…` → `STEP_…`); `P00-01` yields `STEP_P00_01_PACKAGES`.
- Rewards, XP, currency and items are not granted. Level-band eligibility is not enforced because `PlayerSession` has no level field yet.
- Internal failure codes: `unknown_quest`, `quest_not_found`, `invalid_transition`, plus the shared `invalid_payload`.

## Movement rules

- The server owns position. Client coordinates are never accepted; only a direction from `MoveIntent` is used.
- Direction is normalized, so diagonal input does not grant extra speed.
- Distance is `MoveSpeedWuPerSecond × elapsed server time`, with elapsed clamped to `MaxStepSeconds`. Client timestamps are validated for shape but never trusted for movement.
- The result is clamped to the canonical map bounds. Repeated movement into an edge stops at the edge rather than erroring.
- When a `REVIEWED` topology bundle exists for the map, the whole swept step is validated: the segment (with `ActorFootprintRadiusWu` clearance against blocked geometry) must stay inside walkable polygons and must not cross a blocked polygon. A blocked sweep returns `422 movement_blocked` without consuming the sequence, revision or position. Without a reviewed bundle the query reports `not_enforced` and movement keeps the P1 bounds-only behaviour (dev stub).
- `inputSequence` must strictly increase. A stale or repeated sequence is rejected before any state changes.
- `characterId` in the envelope must match the session.
- `idempotencyKey` is validated but movement is not deduplicated in P1; the monotonic sequence is the replay guard. Economic actions will add idempotency records later.
- `serverTick` is derived from a monotonic process clock at the canonical 20 ticks/second.

## Inventory skeleton

`IInventoryService` owns the authoritative per-character inventory. It is exposed read-only through `GET /p1/inventory/{sessionId}`; `Apply` stays a server-side seam with no HTTP surface. `GetSnapshot` returns a payload shaped like `Implementation/Contracts/P1/InventorySnapshot.schema.json`.

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

## Quest turn-in (feature-flagged)

`POST /p1/quests/turnin` is mapped only when `P1:QuestTurnIn:Enabled=true`; otherwise the POST handler is not mapped and the request falls through to the `GET /p1/quests/{sessionId}` read route template, which answers `405`. It is **off by default** because no walkability bundle is reviewed yet — enabling it logs `DEV STUB: P1:QuestTurnIn is enabled...` at startup. Contract: `Implementation/Contracts/P1/TurnInRequest.schema.json` + `TurnInResponse.schema.json`; proposal in `Implementation/Work_Orders/Proposals/QOD-14_TurnInReward_vi.md`.

```bash
curl -i -X POST http://localhost:5000/p1/quests/turnin \
  -H "Content-Type: application/json" \
  -H "X-Session-ID: 8a7b6c5d4e3f4a2b1c0d9e8f7a6b5c4d" \
  -H "X-Correlation-ID: demo-turnin" \
  -d '{
    "schemaVersion": 1,
    "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "idempotencyKey": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    "sentAtUtc": "2026-10-29T00:05:00Z",
    "characterId": "CHR_MINH_KIEM_01",
    "payload": {"questId":"P00-01","npcId":"NPC_TA_VAN_KHANH"}
  }'
```

```json
{
  "schemaVersion": 1,
  "requestId": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "sessionId": "8a7b6c5d4e3f4a2b1c0d9e8f7a6b5c4d",
  "serverTimeUtc": "2026-10-29T00:05:00Z",
  "result": {
    "questState": {
      "questId": "P00-01",
      "state": "COMPLETED",
      "stepId": "STEP_P00_01_PACKAGES",
      "objectiveCounters": {"OBJ_P00_01_PACKAGES": 3},
      "revision": 7
    },
    "rewards": {
      "currency": [{"currencyId": "COIN", "amount": 20}],
      "items": [{"templateId": "EQ-MK-CHEST-T1-R-COMMON", "stack": 1, "location": "BAG"}],
      "xp": {"xpRule": "LEVEL_BAND_BASE", "applied": false}
    },
    "unlocks": ["P00-02"]
  }
}
```

Service `IQuestTurnInService` orchestrates an atomic transaction under the session lock:

1. **Idempotency** — `(characterId, idempotencyKey)` scoped like accept. Replay returns the first outcome; a different payload under the same key returns `409 idempotency_conflict`.
2. **Validate** — catalog → `npcId == turnInNpcId` → same map/floor → distance ≤ 5 WU → LOS (not enforced without REVIEWED topology) → state `READY_TO_TURN_IN`.
3. **Grant** — `IInventoryService.Apply` with canonical `rewards.currency` and `rewards.itemIds` (stack 1, `BAG`). All-or-nothing; failure aborts with no partial reward.
4. **Flip** — `IQuestService.TurnIn` transitions to `COMPLETED` (+1 revision).
5. **Ledger** — `RewardLedgerStore` records `(characterId, questId)` for reward-once audit.

Rewards use canonical data from the `QuestDefinition.rewards` block. XP is echoed with `applied: false` (no XP system yet). `unlocks` lists quest IDs enabled by the completion; their state refreshes lazily. The ledger is in-memory (lost on restart) and labelled as a dev fixture.

## Configuration (`appsettings.json`)

| Key | Value | Source |
|---|---|---|
| `P1World:DefaultMapId` | `MAP_BEN_MUA` | Canonical P1 map |
| `P1World:SpawnX` / `SpawnY` | `18` / `0` | `MapDefinition/MAP_BEN_MUA.json` spawn point |
| `P1World:MoveSpeedWuPerSecond` | `6.0` | **Provisional** slice value; not yet locked in production data |
| `P1World:MaxStepSeconds` | `0.25` | Rejects long-frame jumps |
| `P1World:MaxStepDistanceWu` | `1.5` | Safety bound; must be ≥ speed × max step |
| `P1World:ActorFootprintRadiusWu` | `0.6` | DEC-016 hero footprint half-width; 0 disables swept clearance |
| `P1World:StartingHp` / `MaxHp` | `100` / `100` | `WorldSnapshot.example.json` |
| `P1World:StartingMp` / `MaxMp` | `50` / `50` | `WorldSnapshot.example.json` |
| `P1World:StartingLevel` | `1` | Session level used by the quest level-band guard |
| `P1:QuestAccept:Enabled` | `false` | Maps `/p1/quests/accept`; dev stub until walkability exists |
| `P1:QuestAccept:MaxInteractionDistanceWu` | `5` | DEC-016 NPC interaction distance |
| `P1:Interact:Enabled` | `false` | Maps `/p1/world/interact`; dev fixture until walkability exists |
| `P1:Interact:MaxInteractionDistanceWu` | `5` | DEC-016 interaction distance for interactables and gather nodes |
| `P1:Interact:AssumedProfessionLevel` | `1` | **DEV FIXTURE** stand-in for the character's gather profession level |
| `P1:QuestTurnIn:Enabled` | `false` | Maps `/p1/quests/turnin`; dev stub until walkability exists |
| `P1:QuestTurnIn:MaxInteractionDistanceWu` | `5` | DEC-016 NPC interaction distance for turn-in |
| `P1:MobBehavior:Enabled` | `false` | Enables the labelled mob-behaviour fixture on the 20 Hz world tick |
| `P1:MobBehavior:AggroRadiusWu` / `LeashRadiusWu` | `6` / `12` | **DEV FIXTURE**, not canonical balance |
| `P1:MobBehavior:AttackRangeWu` / `AttackCooldownSeconds` | `1.2` / `2` | **DEV FIXTURE** |
| `P1:MobBehavior:MoveSpeedWuPerSecond` | `2` | **DEV FIXTURE** |
| `P1:CombatDamage:Enabled` | `false` | Loads the mob-stat, SK-MK-03 range-migration and DEC-022 guard-precision bundles; domain only, no damage applied until the QOD-16 proposal is approved |
| `P1:CombatEventStream:CapacityPerSession` / `MaxPageSize` | `512` / `200` | DEV budget for the v2 event-read buffer per session; overflow reports `BUFFER_OVERFLOW` instead of dropping silently |

Environment overrides use the standard form, e.g. `P1World__MoveSpeedWuPerSecond=8` or `P1__QuestAccept__Enabled=true`.

| Content key | Purpose |
|---|---|
| `Content:MapBoundsPath` | Optional absolute/relative override for `map_bounds.json` |
| `Content:QuestsPath` | Optional absolute/relative override for the `QuestDefinition` directory |
| `Content:SkillsPath` | Optional absolute/relative override for the `SkillDefinition` directory |
| `Content:NpcAnchorsPath` | Optional absolute/relative override for `Implementation/Content/Runtime/npc_anchors.json` |
| `Content:TopologyPath` | Optional absolute/relative override for the `MapTopology` bundle directory |
| `Content:WorldEntitiesPath` | Optional absolute/relative override for `Implementation/Content/Runtime/world_entities_bm.json` |
| `Content:WorldRecordsPath` | Optional absolute/relative override for `Implementation/Content/Runtime/world_records.json` |

## Errors

| Status | Code | Meaning |
|---|---|---|
| 400 | `invalid_payload` | Malformed JSON, schema/pattern violation, wrong character, missing session header |
| 404 | `session_not_found` | Unknown session ID |
| 409 | `stale_sequence` | Sequence already applied; state unchanged |
| 413 | `invalid_payload` | Request body over 8 KB |
| 422 | `invalid_map` | Session map is not in `map_bounds.json` |
| 422 | `movement_too_far` | Defensive guard if a configured step exceeds `MaxStepDistanceWu` |
| 422 | `movement_blocked` | Swept step crosses blocked geometry or leaves walkable area (only with a `REVIEWED` topology bundle) |
| 400 | `unknown_skill`, `skill_not_available`, `invalid_target` | Combat skill or target input the server refuses |
| 404 | `target_not_found` | Combat target is not registered in the authoritative world |
| 409 | `cooldown_active`, `insufficient_resource`, `target_not_alive` | Combat gate rejected the cast; `stale_sequence` also applies |
| 422 | `out_of_range`, `unsupported_resource` | Combat cast outside configured range or using an unsupported resource |
| 404 | `quest_not_found` | Quest accept: `questId` is not in the canonical catalog |
| 422 | `npc_mismatch` | Quest accept: `npcId` is not the quest's canonical `startNpcId` |
| 422 | `out_of_range` | Quest accept: different map/floor, or farther than 5 WU |
| 422 | `prerequisite_not_met` | Quest accept: prerequisites incomplete or level outside the band |
| 409 | `invalid_transition` | Quest accept: state is not `AVAILABLE` |
| 409 | `idempotency_conflict` | Quest accept, combat cast or interact: same `idempotencyKey` with a different payload |
| 400 | `invalid_target` | Interact: target exists but is not an `INTERACTABLE` or `GATHER_NODE` |
| 404 | `target_not_found` | Interact: target ID is not in the world entity registry |
| 409 | `target_not_available` | Interact: target is depleted or on per-character gather cooldown |
| 422 | `out_of_range` | Interact: different map/floor, farther than 5 WU, or line of sight blocked |
| 422 | `profession_level_insufficient` | Interact: gather node requires a higher profession level |

All error envelopes include `code`, `messageKey`, `retryable`, `fieldErrors` and `correlationId`. Inventory and teleport service codes listed above are domain results; they have no HTTP mapping yet.

## Runtime smoke test

The `server-smoke` GitHub Actions workflow builds the server, starts it on `127.0.0.1:5080` with `P1__QuestAccept__Enabled=true`, `P1__Interact__Enabled=true` and `P1__QuestTurnIn__Enabled=true`, and runs `Server/Health/Smoke/smoke_p1.py`. The script uses only the Python standard library and verifies:

- `/health` returns `200` and echoes `X-Correlation-ID`.
- Session creation returns `201`, a `Location` header, the canonical spawn and `revision=1`.
- A valid move advances `x`, returns `revision=2` and keeps `y` unchanged.
- Replaying that sequence returns `409 stale_sequence`; the snapshot position and revision do not change.
- Wrong character, missing session header, unknown session and a 31-character `requestId` return the expected errors.
- A later move with sequence `2` succeeds, proving rejected requests did not consume the sequence.
- The full `P00-01` collect flow: walk to each Atlas package and claim it via `/p1/world/interact`, watching the quest reach `ACTIVE` (counter 1) → `ACTIVE` (counter 2) → `READY_TO_TURN_IN` (counter 3), with idempotent replays, `idempotency_conflict`, depleted retries (`409 target_not_available`) and out-of-range rejection (`422`) covered along the way.
- A second character gathers from `ENT_MAN_BM_NODE_BM_ORE_01`, verifying the `gather` outcome, the yield grant in `/p1/inventory` (correct item, stack and `BAG` location), replay without double-collection, and the per-character cooldown.
- The full `P00-01` turn-in flow: walk to `NPC_TA_VAN_KHANH` at x=64, turn in with `questId=P00-01` and `npcId=NPC_TA_VAN_KHANH`, verify `COMPLETED` quest state, 20 COIN + 1 chest item in inventory, `applied: false` XP, `P00-02` unlock, idempotent replay, and `409 invalid_transition` on a second turn-in attempt with a new key.

Run the same flow locally:

```bash
dotnet build Server/Health/Health.csproj --configuration Release
(cd Server/Health && dotnet bin/Release/net10.0/Health.dll --urls http://127.0.0.1:5080) &
python3 Server/Health/Smoke/smoke_p1.py http://127.0.0.1:5080
```

Stop the background server process afterward. See `Implementation/Reports/QOD-04_verification_report.md` for the verification summary and OpenCode integration conditions.

## Domain service self-check

Quest and inventory HTTP surfaces are read-only, teleport has no endpoint, and combat only reaches the self-targeting `SK-MK-01`, so `server-smoke` also exercises the services in-process before starting the listener:

```bash
dotnet Server/Health/bin/Release/net10.0/Health.dll --self-check
```

The flag boots the DI container and canonical content, then runs 231 assertions covering combat gating (skill/class, sequence, cooldown, MP, target and range), the QOD-16 combat domain (skill coefficients/targeting/telegraph/VFX keys, the versioned `REFERENCE_L5` mob-stat bundle with elite multipliers and the `BOSSDATA_BLOCKED` boss, the SK-MK-03 range migration, the Production Rules §2 damage-formula oracle with seeded RNG, the DEC-022 guard precision bundle (window `[T,T+8)`, whiff `[T+8,T+28)`, inclusive 120°/4.4 WU cone edges, DR bucket cap 0.8, oracle 27/8/21/5, counter 32/49 and deterministic impact ordering), the v2 event store (monotonic cursors, replay-safe append, bounded buffer with `BUFFER_OVERFLOW`/`CURSOR_TOO_OLD` resync, session isolation/lifetime reset, barrier-parallel appends), the AOI audience filter (enter 40/leave 48 WU hysteresis, floor/instance filtering, NPC/blocked-boss policy, per-caller node availability, reconnect reset), and the internal entity read-model: 27 projected entities, NPC invulnerability, elite stats, blocked-boss hp 0, gate-off hp 0 and lifeId/revision bumps on respawn), world-target resolution and floor checks, the full `P00-01` quest flow through `COMPLETED` driven by server-verified events, quest accept guards, idempotency, line-of-sight and swept-walk geometry (clear, wall, large step, hole, corner, floor, non-finite, outside, footprint, not-enforced), the NPC anchor registry, the world record catalog (352 records, `TryResolveTarget` by record ID and by entity ID per map), the Bến Mưa world-entity registry with despawn/respawn under a manual clock, interact claims (collect, depleted, idempotent replay/conflict, out-of-range, LOS-blocked, respawn and distinct-record dedupe), per-character package ownership (`PER_CHARACTER` claims: two characters collect all three packages under a barrier with no global respawn, world state stays `AVAILABLE`, per-character claim window and respawn), objective-scoped progress dedupe (two objectives sharing one record, duplicate events, sequential-step guard, KILL event scope) and gather claims (yield grant, per-character cooldown and respawn, profession gate), barrier-coordinated interact/gather races (same key replays one result, two keys grant once, per-character shards stay independent, shared interactable despawn grants once, claim released by token when the grant fails so a retry grants exactly once), turn-in atomic reward (npc-mismatch, wrong-floor, out-of-range, success + inventory verification, replay same key, same-key-different-npc conflict, invalid-transition after completed, double-reward guard, idempotency, ledger recording, grant/flip/ledger failure injection with full rollback, currency overflow with no partial commit, and barrier-coordinated parallel turn-ins granting exactly once with same-key replays), inventory grants/equips/removals with revision, slot and currency guards, and teleport map/bounds/reason/death-return validation. Each check prints `PASS` or `FAIL` and the process exits non-zero if any check fails; no network listener is opened.

## Manual verification

`dotnet` and Unity are not installed in the current authoring environment. The `server-build` workflow compiles this project on .NET 10, and `server-smoke` runs the runtime checks above plus the domain self-check. Both Python validators pass locally. The table below remains the manual equivalent for a machine with the .NET SDK.

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
| 11 | Combat `inputSequence=3` with `SK-MK-01` | `200`, `combat.effect`, `aggregateRevision=4`, MP 50→38 |
| 12 | Repeat combat `inputSequence=3` | `409 stale_sequence`; MP unchanged |
| 13 | Combat `inputSequence=4` with `SK-MK-01` immediately | `409 cooldown_active`, `retryable: true` |
| 14 | Move with `inputSequence=3` after that cast | `409 stale_sequence` (sequence shared with combat) |
| 15 | Combat `SK-MK-02` without `targetId` | `400 invalid_payload`, field `targetId` |
| 16 | Combat `SK-MK-03` with unknown `targetId` | `404 target_not_found` |
| 17 | `GET /p1/quests/{sessionId}` | `200`, one `P00-01` entry, `state: AVAILABLE`, counters `{"OBJ_P00_01_PACKAGES": 0}` |
| 18 | `GET /p1/inventory/{sessionId}` | `200`, `inventoryRevision: 0`, empty `items` and `currencies` |
| 19 | Walk east to `x >= 37.5`, then accept `P00-01` from `NPC_LYAN` | `200`, `state: ACTIVE`, `revision: 2` |
| 20 | Replay accept with the same `idempotencyKey` and payload | `200`, same state and revision, no second transition |
| 21 | Accept again with a new key | `409 invalid_transition`; state/revision unchanged |
| 22 | Same key with `npcId = NPC_TA_VAN_KHANH` | `409 idempotency_conflict` |
| 23 | Accept `P00-01` from a fresh session at spawn | `422 out_of_range`, `retryable: true` |
| 24 | With the quest `ACTIVE`, walk to `x >= 36` and claim `ENT_MAN_BM_OBJ_BM_PACKAGE_01` via `/p1/world/interact` | `200`, `outcome: collected`, `targetState: AVAILABLE`, counter `1` |
| 25 | Repeat the same claim before respawn | `409 target_not_available` |
| 26 | Gather `ENT_MAN_BM_NODE_BM_ORE_01` within 5 WU | `200`, `outcome: gathered`, `yield` granted in `/p1/inventory` |
| 27 | Any request | Response always has `X-Correlation-ID` |

## Headless E2E scenario (QOD-15)

One command builds the server, starts it and drives the whole gameplay loop:

```bash
bash Server/Health/Smoke/run_e2e_p1.sh default   # production gates OFF: expects blocked output
bash Server/Health/Smoke/run_e2e_p1.sh dev       # dev synthetic scenario: full golden loop
```

- `default` starts the server without the P1 feature flags and asserts the expected blocked output: session/movement/read endpoints work, while `/p1/quests/accept`, `/p1/world/interact` and `/p1/quests/turnin` return `404` because the routes are not mapped.
- `dev` starts the server with `P1__QuestAccept__Enabled`, `P1__Interact__Enabled` and `P1__QuestTurnIn__Enabled` set to `true` and runs the golden loop in one session: create session → valid move → wall-crossing attempt → accept `P00-01` → collect the three Atlas packages (`ACTIVE` → `READY_TO_TURN_IN`) → turn-in at `NPC_TA_VAN_KHANH` (`COMPLETED`, COIN 20 + chest, XP `applied: false`, unlock `P00-02`) → replay same key returns the stored result → a new key returns `409 invalid_transition` → inventory/quest readback shows exactly one reward → two parallel turn-ins with different keys yield exactly one winner → two fresh characters claim the same package concurrently (`concurrent_package_claim=OK`, no respawn wait) → wrong character/unknown session guards.

The Bến Mưa topology fixture is `SYNTHETIC_TEST_ONLY`, so wall enforcement is `not_enforced` on the dev server: the wall-crossing move succeeds and the scenario records `wall_enforcement=not_enforced`. When a `REVIEWED` bundle lands, the same move must return `422 movement_blocked`; the scenario accepts exactly those two outcomes and fails on anything else. The wall/sweep logic itself is verified deterministically by the self-check's reviewed synthetic bundle. `server-e2e` runs both profiles in CI.

## Current limits

- Sessions are in memory and lost on restart; there is no database, authentication or real-time transport.
- `entities` is always empty in snapshots; combat can target alive world mobs/bosses by instance ID, but there is still no damage, death or loot. The QOD-16 phase-1 domain (damage formula, seeded RNG, mob-stat bundle, internal entity projection) exists behind the `P1:CombatDamage` gate but is not applied anywhere yet.
- Mob behaviour (`MobLifecycleService`) exists as a tickable state machine (IDLE/AGGRO/CHASE/ATTACK/RETURN/DEAD) with LOS, leash and attack-cooldown gates, driven by the 20 Hz `WorldTickBackgroundService` when `P1:MobBehavior:Enabled=true` (off by default) — there is no damage or loot yet, and every radius/speed is a labelled DEV fixture. Teleport has no endpoint.
- The Bến Mưa world-entity registry (`world_entities_bm.json`: 27 canonical placements, 22 templates) is loaded with despawn/respawn state; interact uses it for shared `INTERACTABLE` claims and per-character (`claimPolicy: PER_CHARACTER`) package claims, and combat resolves alive mobs/bosses by instance ID. The 352-entry world record catalog (`world_records.json`) maps entities to `recordId`s for interact claims and quest progress.
- Combat casts still have no damage, hit chance, telegraphs, death or loot on the wire: `combat.effect` only records an accepted cast and its cooldown. The canonical damage formula and mob stats exist as gated domain (see the QOD-16 section) awaiting proposal approval.
- Quest state is in memory; accept, interact and turn-in are feature-flagged off by default. Progress advances only from server-verified events (`RecordVerifiedEvent`); `P00-01` reaches `READY_TO_TURN_IN` by collecting the three Atlas packages. `P1:QuestTurnIn:Enabled` gates the turn-in endpoint; rewards use canonical `rewards` data from the QuestDefinition, XP is echoed with `applied: false` (no XP system), and the reward ledger is in-memory only (lost on restart). Turn-in commits grant → quest flip → ledger under the actor lock and re-checks state inside the lock, so parallel turn-ins grant exactly once (one winner, the other `invalid_transition`; same-key contention never double-grants). Line-of-sight runs only for `REVIEWED` topology bundles; the shipped bundle is synthetic, so it is `not_enforced` until Muse delivers the Bến Mưa layout.
- Interact gather yields (item IDs, quantity ranges, respawn seconds, profession levels) are DEV fixtures from the supplement records, not canonical economy data; the profession gate uses a configured `AssumedProfessionLevel` until character progression exists.
- Inventory is read-only over HTTP and starts empty: no item catalog, stack-limit enforcement, durability rules, seeded starting items or mutation endpoint.
- Teleport uses map bounds only; there is no walkability, portal, cooldown or respawn logic.
- Movement speed and starting HP/MP are slice defaults, not locked balance values.
