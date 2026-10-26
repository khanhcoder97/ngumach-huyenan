# OpenCode Work Order — P1-01 Authoritative Movement Slice

**Owner:** OpenCode

## Goal
Implement a small, runnable authoritative server slice for player session creation and movement. It must form the first playable-network foundation for *Ngũ Mạch: Huyền Ấn* without changing the pixel-art pipeline or runtime presentation.

## Boundaries

You own server gameplay code and contract integration for this work order.

Do not modify:
- `Client/Assets/Art/` or `Client/Assets/UI/Art/`
- Pixel-art renderer/import configuration and editor tooling
- `docs/production/`
- Existing `Client/Assets/Scripts/Bootstrap/TitleBootstrap.cs`
- Existing health endpoint semantics: `GET /health` must continue to return 200 and the `X-Correlation-ID` response header.

Use existing content and contracts as the source of truth:
- `Implementation/Content/map_bounds.json`
- `Implementation/Contracts/P1/MoveIntent.schema.json`
- `Implementation/Contracts/P1/WorldSnapshot.schema.json`
- `Implementation/Contracts/P1/Envelope.schema.json`

## Deliverables

1. Under `Server/Health/`, add a small in-memory world/session service. Keep `Program.cs` as the API composition root; place models/services in separate, clearly named files.
2. Add `POST /p1/sessions`.
   - Generates a server session ID.
   - Creates a player in `MAP_BEN_MUA` at a valid configured spawn or documented safe default within canonical map bounds.
   - Returns a response compatible with the P1 envelope conventions.
3. Add `POST /p1/move`.
   - Accepts the existing `MoveIntent` field shape.
   - Validates session, sequence number, map ID, and target coordinates.
   - Uses authoritative server coordinates only; reject stale/out-of-order movement.
   - Clamps valid movement to the selected map bounds and rejects implausible movement distances.
   - Returns an envelope containing the updated `WorldSnapshot` representation and a useful machine-readable error code for rejected requests.
4. Add `GET /p1/world/{sessionId}`.
   - Returns the latest authoritative snapshot for that session.
5. Preserve the current correlation-ID middleware on every response, including errors.
6. Add no external database, package, authentication system, or real-time transport for this slice.
7. Add `Server/Health/README.md` sections with launch commands and three curl examples for health, create session, and move.
8. Add a focused test project only if it can use built-in .NET test facilities without adding unavailable dependencies. Otherwise provide a compact manual verification table in the README.

## Acceptance checks

- `dotnet run --project Server/Health/Health.csproj` starts the service.
- `/health` still behaves as documented.
- A newly created session can move inside `MAP_BEN_MUA`.
- A request with a stale sequence number is rejected without changing its stored position.
- Out-of-bounds target coordinate is handled predictably and documented.
- The response always includes `X-Correlation-ID`.
- No change to art assets, art import pipeline, production documents, or title screen bootstrap.

## Completion report

Report modified files, endpoints and request/response examples, plus any assumption needed because the local machine does not currently have the .NET SDK installed for a real build.
