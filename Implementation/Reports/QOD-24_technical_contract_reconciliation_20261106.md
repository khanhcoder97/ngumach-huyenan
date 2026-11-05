# QOD-24 - `Production_Technical_Contracts_vi.md` reconciled against the shipped surface (2026-11-06)

`docs/production/Production_Technical_Contracts_vi.md` is the frozen transport-independent
contract, and until today nothing in this repository read it: no loader, no validator, no
check. `Implementation/Tools/reconcile_technical_contract.py` now does, and CI runs it in
content-validation. Nothing in this change touches a route, a schema, a gate or a
`docs/production/**` file.

## 1. What matches (measured)

| Contract list | Doc says | Shipped | Result |
| --- | --- | --- | --- |
| Request envelope fields (section 1) | `schemaVersion, requestId, idempotencyKey, sentAtUtc, characterId, payload` | 6 of 6 appear in the 31 wire schemas | **0 absent** |
| Response envelope fields (section 1) | `serverTimeUtc, result, error, revision` | 4 of 4 appear | **0 absent** |
| Server event fields (section 4) | `eventId, eventType, aggregateId, aggregateRevision, emittedAtUtc, schemaVersion, payload` | 7 of 7 appear | **7 of 7** |

So the envelope and event shapes in the contract are genuinely implemented - that is the
first time the claim is backed by a measurement instead of by my reading of the DTOs.

## 2. What does not match, named

- **Canonical error codes: 5 of 13 are answered by a shipped wire code**
  (`REVISION_CONFLICT`, `PREREQUISITE_NOT_MET`, `INSUFFICIENT_CURRENCY`,
  `INSUFFICIENT_ITEMS`, `COOLDOWN_ACTIVE`). **8 have no identically named code** in the
  server's 62 lowercase wire constants: `AUTH_EXPIRED`, `CHARACTER_NOT_FOUND`,
  `INVALID_STATE`, `CAP_REACHED`, `ZONE_UNAVAILABLE`, `MATCH_RULES_MISMATCH`,
  `RATE_LIMITED`, `INTERNAL_RETRYABLE`.
  Two of those are naming divergences, not missing behaviour - the server answers
  `invalid_transition` for INVALID_STATE and `session_not_found` / `unknown_session` where
  the contract names CHARACTER_NOT_FOUND. The other six correspond to subsystems that do
  not exist yet (auth edge, character registry as a resource, zone availability, match
  rules, throttling, retryable internal failures), so the honest statement is: the wire
  vocabulary is the server's own, and the contract's canonical list was never reconciled
  to it. Deciding whether to rename or to keep both vocabularies is a contract change and
  is not mine to make.
- **Idempotency retention: the contract says `idempotencyKey + actorId + operation` is
  recorded at least 30 days.** This server keeps five in-memory ledgers, each bounded to
  **256 entries** and lost on restart:
  `Server/Health/Gameplay/Combat/DeathReturn.cs:117`,
  `Server/Health/Gameplay/Combat/PlayerLifeLedger.cs:33`,
  `Server/Health/Gameplay/Inventory/ConsumableCatalog.cs:210`,
  `Server/Health/Gameplay/Inventory/Equipment.cs:87`,
  `Server/Health/Gameplay/Inventory/EquipmentV2.cs:72`.
  30 days is unreachable without persistence, and the 256 bound is the same eviction class
  the PR #106 review filed against `PlayerLifeLedger` (work order 30 item 1): a replay of a
  key that aged out can act twice.
- **Acceptance baseline: "no duplicate item/currency across 10,000 replayed idempotent
  commands" (section 6)** cannot be demonstrated with a 256-entry ledger, so I am not
  claiming it. The number is printed by the tool so the gap stays visible.
- **Rate limiting (section 5):** the contract requires per-account and per-IP limits on
  economy endpoints and channel-specific limits on chat. No server type or middleware
  carries that name; nothing in this repository throttles. `RATE_LIMITED` is therefore
  both unimplemented and un-emittable.

## 3. What I did not do, deliberately

- No error code was added, renamed or mapped, because the message key pattern and the code
  list are wire-visible and the standing rule is packet then approval then schema.
- No ledger capacity was raised as a way to make the 30-day claim "true": durability is
  QODER Remote's `Server/Persistence` scope (R-series), and a second writer is worse than
  an honest gap.
- No `docs/production/**` edit, no topology `reviewState` change, no gate flipped;
  `appsettings.json` untouched.

## 4. Decisions this creates for the owner/Codex

1. Canonical error vocabulary vs the shipped one: rename 62 codes to the 13, or amend the
   contract to the server vocabulary and mark the six subsystem-dependent codes as not yet
   reachable? Either way it is a contract edit, not a server choice.
2. Where idempotency receipts live so "30 days" and "10,000 replays" become measurable,
   and what happens to the five 256-entry bounds meanwhile.
3. Which component owns rate limiting (edge/gateway vs this server), since section 5 puts
   it on the server for economy endpoints.
4. Whether `AUTH_EXPIRED` and `CHARACTER_NOT_FOUND` belong to this slice at all, given
   section 2 places OAuth and platform credentials at the auth edge, outside it.
