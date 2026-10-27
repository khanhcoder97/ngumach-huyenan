# Ngu Mach Huyen An — Health Server

Minimal ASP.NET Core API (net10.0) exposing the health check and the P1 authoritative movement slice.

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

The server loads `Implementation/Content/map_bounds.json` at startup by walking up from the working directory, content root and application base directory. Override with `Content__MapBoundsPath=/absolute/path/map_bounds.json` if needed. Startup fails if the configured map is unknown, the spawn is outside bounds, or the movement configuration is inconsistent.

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

## Movement rules

- The server owns position. Client coordinates are never accepted; only a direction from `MoveIntent` is used.
- Direction is normalized, so diagonal input does not grant extra speed.
- Distance is `MoveSpeedWuPerSecond × elapsed server time`, with elapsed clamped to `MaxStepSeconds`. Client timestamps are validated for shape but never trusted for movement.
- The result is clamped to the canonical map bounds. Repeated movement into an edge stops at the edge rather than erroring.
- `inputSequence` must strictly increase. A stale or repeated sequence is rejected before any state changes.
- `characterId` in the envelope must match the session.
- `idempotencyKey` is validated but movement is not deduplicated in P1; the monotonic sequence is the replay guard. Economic actions will add idempotency records later.
- `serverTick` is derived from a monotonic process clock at the canonical 20 ticks/second.

## Configuration (`appsettings.json`)

| Key | Value | Source |
|---|---|---|
| `P1World:DefaultMapId` | `MAP_BEN_MUA` | Canonical P1 map (replaces the stale `MAP_LANG_MOI` reference in the work order) |
| `P1World:SpawnX` / `SpawnY` | `18` / `0` | `MapDefinition/MAP_BEN_MUA.json` spawn point |
| `P1World:MoveSpeedWuPerSecond` | `6.0` | **Provisional** slice value; not yet locked in production data |
| `P1World:MaxStepSeconds` | `0.25` | Rejects long-frame jumps |
| `P1World:MaxStepDistanceWu` | `1.5` | Safety bound; must be ≥ speed × max step |
| `P1World:StartingHp` / `MaxHp` | `100` / `100` | `WorldSnapshot.example.json` |
| `P1World:StartingMp` / `MaxMp` | `50` / `50` | `WorldSnapshot.example.json` |

Environment overrides use the standard form, e.g. `P1World__MoveSpeedWuPerSecond=8`.

## Errors

| Status | Code | Meaning |
|---|---|---|
| 400 | `invalid_payload` | Malformed JSON, schema/pattern violation, wrong character, missing session header |
| 404 | `session_not_found` | Unknown session ID |
| 409 | `stale_sequence` | Sequence already applied; state unchanged |
| 413 | `invalid_payload` | Request body over 8 KB |
| 422 | `invalid_map` | Session map is not in `map_bounds.json` |
| 422 | `movement_too_far` | Defensive guard if a configured step exceeds `MaxStepDistanceWu` |

All error envelopes include `code`, `messageKey`, `retryable`, `fieldErrors` and `correlationId`.

## Manual verification

`dotnet` and Unity are not installed in the current authoring environment. The `server-build` GitHub Actions workflow compiles this project on .NET 10 and passes; the runtime table below still needs to be run on a machine with the .NET SDK. Both Python validators pass locally.

| # | Step | Expected |
|---|---|---|
| 1 | `dotnet run --project Server/Health/Health.csproj` | Starts; logs `Loaded map bounds for 46 maps` |
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
- `entities` is always empty; mobs, combat, quest, inventory and teleport services are the next QOD-03 increment and are not exposed here.
- Movement speed and starting HP/MP are slice defaults, not locked balance values.
