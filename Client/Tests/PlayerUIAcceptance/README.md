# PlayerUIAcceptance (OPC-14 M3)

HTTP acceptance harness for the player UI against a real P1 server.

Status: **UNVERIFIED** — no P1 server is available in this sparse worktree. The
harness compiles (smoke) but scenarios are documented, not executed. Native/HTTP
results must not be claimed until run against a server from the same integration
checkout/commit.

## Scenarios (P00-01)
1. NPC snapshot reads do not POST `/p1/world/interact` (network profiler / transport log).
2. Accept with the correct NPC template id → 3 parcels → ready → turn-in; server
   receipts: 20 COIN + one chest, exactly one grant (no double grant on retry).
3. Journal/tracker update live; pin does not issue a wire command.
4. Faults: lost turn-in response after commit → retry same pending request → no
   double grant; delayed snapshot after close/rebind/NPC switch → no stale view;
   expired/disconnected → disable + recover snapshot without local grant.
5. Full-bag case depends on a server seed API; if unavailable, stays UNVERIFIED
   (do not invent an endpoint).

## Run
```
set P1_BASE_URL=http://127.0.0.1:<port>
dotnet run --project Client/Tests/PlayerUIAcceptance/PlayerUIAcceptance.csproj -c Release
```
The server must be started from the same integration checkout; do not mutate
global DB or open a public service. Stop only processes created by the harness.

## Honesty
- HTTP scenarios are NOT counted as TESTED_HTTP until executed with a real server.
- Producer/narrative tests are untouched; this harness adds, not replaces.
