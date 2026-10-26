# HỢP ĐỒNG KỸ THUẬT PRODUCTION
## API, schema, transaction, event và vận hành nền

Đây là contract baseline độc lập transport; implementation có thể dùng HTTP/JSON cho command/query và WebSocket cho state/event. Tất cả thời gian là UTC ISO-8601 trong payload; timezone chỉ dùng cho lịch/reward UI. Mọi gameplay mutation được server xác thực.

## 1. Envelope và quy ước

```json
{
  "schemaVersion": 1,
  "requestId": "uuid",
  "idempotencyKey": "uuid-per-logical-action",
  "sentAtUtc": "2026-10-23T00:00:00Z",
  "characterId": "CHR_...",
  "payload": {}
}
```

Response thêm `serverTimeUtc`, `result`, `error`, `revision`. Client gửi `requestId` mới cho mỗi transport retry nhưng giữ `idempotencyKey` cho cùng một hành động kinh tế/quest/reward. Server ghi `idempotencyKey + actorId + operation` ít nhất 30 ngày hoặc lâu hơn nếu ledger retention yêu cầu. Không tin client clock, stat, inventory count, cooldown hoặc reward outcome.

Error envelope: `{code, messageKey, retryable, fieldErrors[], correlationId}`. Canonical errors: `AUTH_EXPIRED`, `CHARACTER_NOT_FOUND`, `REVISION_CONFLICT`, `INVALID_STATE`, `PREREQUISITE_NOT_MET`, `INSUFFICIENT_CURRENCY`, `INSUFFICIENT_ITEMS`, `CAP_REACHED`, `COOLDOWN_ACTIVE`, `ZONE_UNAVAILABLE`, `MATCH_RULES_MISMATCH`, `RATE_LIMITED`, `INTERNAL_RETRYABLE`. User text luôn lấy localization key; log ghi code/correlation ID, không ghi token/credential.

## 2. Service boundaries và command/query

| Domain | Command/query contract | Idempotency / transaction |
|---|---|---|
| Account | `POST /v1/session`, `POST /v1/session/refresh`, `DELETE /v1/session`; OAuth/platform credential chỉ ở auth edge | refresh token rotate; revoke session có audit |
| Character | `GET /v1/characters`, `POST /v1/characters`, `PATCH /v1/characters/{id}/appearance` | character create/name reservation unique transaction; appearance revision check |
| World | `POST /v1/world/enter`, `POST /v1/world/transition`, WS `world.snapshot`, `world.delta`, `world.command_result` | save checkpoint before route transition; transition command dedupe |
| Combat | WS `combat.input`; server emits `combat.hit`, `combat.effect`, `combat.cooldown`, `combat.death` | command sequence monotonic per actor; no client-computed damage |
| Quest | `GET /v1/quests`, `POST /v1/quests/{id}/accept`, `/interact`, `/turn-in` | event-ID dedupe; reward and quest completion in same transaction |
| Inventory | `GET /v1/inventory`, `POST /v1/equipment/{slot}`, `/salvage`, `/repair` | optimistic inventory revision; item move and currency ledger atomic |
| Forge | `POST /v1/forge/preview`, `POST /v1/forge/commit` | preview is nonbinding; commit revalidates costs/recipe; deterministic server seed recorded |
| Trade/market | `POST /v1/trade/{session}/offer`, `/confirm`; `POST /v1/market/list`, `/buy`, `/cancel` | escrow; two-phase confirm; seller debit/buyer credit/item transfer atomic |
| Social | `POST /v1/party`, `/guild`, `/chat/message`, `/block`; `GET /v1/guild/{id}` | role check on server; chat rate/moderation before broadcast |
| Activity | `POST /v1/activity/queue`, `/ready`, `/leave`; event scheduler publishes `activity.state` | queue ticket unique; match result/reward ledger exactly once |
| Data | signed content bundle manifest with `bundleVersion`, hashes, minClientVersion | client content is read-only and never authoritative |

HTTP statuses: 200/201 success, 400 malformed, 401/403 auth/permission, 404 unknown, 409 state/revision conflict, 422 rule/cap validation, 429 throttle, 5xx retryable only when response says so. State-changing command returns authoritative post-commit revision.

## 3. Canonical persistence entities

| Entity | Required fields / constraints |
|---|---|
| Account | `account_id`, `status`, `created_at`, `region_id`, `privacy_flags`, `schema_version`; external identity stored separately |
| Character | `character_id`, `account_id`, `class_id`, `level`, `xp`, `map_id`, `x/y`, `quest_revision`, `inventory_revision`, `created_at`; account max 4 per DEC config |
| ItemInstance | `instance_id`, `template_id`, `owner_id`, `stack`, `bind_state`, `durability`, `upgrade`, `affixes[]`, `location`, `version`; unique instance, stack bounds from template |
| QuestState | `character_id`, `quest_id`, `state`, `step_id`, `objective_counters`, `flags`, `revision`, `updated_at` |
| CurrencyLedger | `entry_id`, `owner_id`, `currency_id`, signed `delta`, `reason_code`, `source_id`, `idempotency_key`, `created_at`; append-only |
| RewardLedger | `reward_id`, `recipient_id`, `activity_id`, `source_event_id`, `table_version`, `roll_seed_hash`, `items[]`, `currency[]`, `committed_at`; unique recipient+source event |
| ActivityMatch | `match_id`, `mode_id`, `ruleset_hash`, `roster`, `state`, `phase`, `score`, `started_at`, `ended_at`, `result_revision` |
| Guild | `guild_id`, `name_normalized`, `leader_id`, `member_count`, `level`, `treasury_revision`, `created_at` |
| Schedule | `event_id`, `region_id`, `timezone`, `local_rule`, `start_utc`, `end_utc`, `config_version`, `eligibility`, `reward_cap` |

All persisted IDs are immutable machine-safe IDs. Display names and localized text are keys. Numeric config declares unit and inclusive/exclusive boundaries. Every table has migration version, backup policy and rollback compatibility.

## 4. Event contracts and consistency

Server events have `{eventId, eventType, aggregateId, aggregateRevision, emittedAtUtc, schemaVersion, payload}`. Consumers store eventId for dedupe; out-of-order revision is buffered or causes snapshot fetch. World movement may be eventually consistent; currency/item/quest completion must be transactionally consistent. A reconnect sends `lastSeenRevision` and gets snapshot plus replay window; if replay expired, server sends full authoritative snapshot.

Reward flow: eligibility check → lock ledger key → compute server-side result → persist item/currency/quest state atomically → publish event from transactional outbox → acknowledge client. If publish fails, outbox retries; never rerun random roll on retry.

## 5. Security, rate limits, observability

- Access token short-lived and scoped; refresh token rotated, revocable and stored hashed. Secrets remain server-side.
- Validate request size/schema, owner access, rate limit, replay window, numeric bounds, map bounds and allowed state transition.
- Economy endpoints use per-account and per-IP limits; chat uses channel-specific rate limit; interaction distance checked server-side.
- Audit admin mutation, trade, market, currency adjustment, account deletion and moderation action with actor, reason and correlation ID.
- Metrics: command p50/p95/p99, tick duration, WS reconnect, queue wait, reward commit failures, currency/item deltas, outbox lag, shard occupancy, crash rate. Gameplay analytics use pseudonymous IDs and minimal events.

## 6. Non-functional acceptance baseline

Vertical slice target: 20 authoritative simulation ticks/s; world command ack p95 ≤150ms within same region at ≤100ms RTT; reconnect ≤120s according to DEC-004; no duplicate item/currency across 10,000 replayed idempotent commands. Prototype capacity benchmark uses 100 concurrent simulated clients per zone; production capacity/CCU and region topology remain owner approvals. Instance design must scale horizontally and isolate noisy activity shards. Backup/restore targets for launch are provisional RPO ≤15 minutes and RTO ≤4 hours; operations owner must replace with funded target before release.

## 7. Content data import contract

CSV headers are schema-versioned; UTF-8; comma delimiter; quote RFC 4180; decimals use dot; booleans `true/false`; IDs unique within declared namespace. Import pipeline performs foreign-key checks, enum checks, map-bound checks, graph cycle/entry validation, percentage sum validation, reward cap validation, missing localization, unused asset refs and semantic diff. Content bundle is immutable once released; balance change creates new `bundleVersion` and rollback target.
