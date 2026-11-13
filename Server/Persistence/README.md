# QR-01 Server Persistence (Qoder Remote)

SQLite persistence library for the QR-01 epic (issue #79): durable state, fenced
transactions, idempotent receipts, ledger, outbox and crash/backup recovery.

**Status:** R1 checkpoint (buildable library + tests + harness) and R2 checkpoint
(atomic life/return provenance, poison outbox, principal ownership, readiness/metrics and a
measured benchmark). This is a single-host development/test profile. The production target
stays the OnlineSpec PostgreSQL provider; nothing here replaces it.

**Not in scope / not claimed:** no Health endpoint integration, no feature flag turned on,
no production readiness, no MMORPG exactly-once guarantee, no disk-full/ACL proof.

## Projects

| Path | Purpose |
| --- | --- |
| `Server/Persistence/Server.Persistence.csproj` | Library: migrations, identity, leases, unit of work, outbox, backup/recovery |
| `Server/Persistence.Tests/Server.Persistence.Tests.csproj` | xUnit tests against real SQLite files, includes subprocess crash tests |
| `Server/Persistence.Harness/Server.Persistence.Harness.csproj` | Small CLI used by tests to crash a process at transaction boundaries and to contend for leases |

## Commands

```bash
dotnet restore Server/Persistence.Tests/Server.Persistence.Tests.csproj --locked-mode
dotnet build Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release --no-restore
dotnet test Server/Persistence.Tests/Server.Persistence.Tests.csproj -c Release \
  --logger "trx;LogFileName=qr01.trx" --collect:"XPlat Code Coverage"
```

The CI workflow is `.github/workflows/qr-01-ci.yml` and runs exactly these projects.

Benchmark (writes JSON to stdout; use a throwaway DB path):

```bash
dotnet Server/Persistence.Harness/bin/Release/net10.0/NguMach.Server.Persistence.Harness.dll \
  benchmark --db <temp>/bench.sqlite --character bench-hero \
  --iterations 200 --replays 2000 --concurrency 4 --contention-iterations 50
```

## Design guarantees

- **Atomic unit of work** — state, expected revision, receipt (request hash + committed
  result), ledger and outbox are written in one `BEGIN IMMEDIATE` transaction. A domain
  planner computes the transition inside that transaction and must be pure.
- **Global idempotency key** — replay with the same key and payload returns the stored
  result (`Replayed`), with no new ledger/outbox rows. A different payload or owner is a
  conflict, never a fresh grant. Keys are not scoped to a character or life version.
- **Fencing** — leases carry a monotonically increasing fencing token. The owner may renew
  inside the lease TTL; after expiry a 120 s reconnect grace keeps the same token for the
  same owner; a takeover increments it and stale tokens are refused at commit.
- **Capacity/rejection is not success** — a planner may return `Reject` or
  `CapacityExceeded`; nothing is written and no receipt is stored.
- **Outbox** — claim ordered by id, claim expiry, retry/backoff, ack, per-consumer cursor.
  `ApplyOnceAsync` records the dedupe marker in the same SQL transaction as the effect, so
  a crash after the effect but before the ack cannot grant twice. `OutboxDispatcher` keeps
  one batch bounded (default 10, hard cap 1000) and moves poison messages to a durable
  dead-letter state after a bounded attempt budget instead of retrying forever.
- **Life/death/return** — a `LifeTransition` is written inside the same fenced transaction as
  state/revision/receipt/ledger/outbox. Death keeps the life version; a return advances it
  exactly once. The full before/after snapshots and the whole committed return result are
  stored under a global idempotency key, so a replay in a later life is history, never a
  fresh heal. A stale life snapshot is refused and rolls the whole command back. There is no
  second writer and no unapproved expiry: tombstones are readable but never produced by
  the library.
- **Backup/restore** — SQLite online backup API only (never a raw copy of a live WAL
  database), integrity/schema/count verification, SHA-256 manifest, corrupt/truncated and
  digest-mismatch refusal. Restore copies into a sibling temp file, verifies it, swaps the
  target, and restores the previous target if the swap or post-verification fails; a locked
  target is refused rather than overwritten.
- **Migrations** — versioned scripts recorded with SHA-256 checksums; tampering and
  newer-than-supported schema versions fail closed.
- **Ops surface** — `PersistenceDiagnostics` returns real readiness (integrity, foreign keys,
  schema version) and aggregate metrics (counts, pending/dead outbox, oldest pending age).
  It exposes no payload, id or token. `PersistenceLimits` documents the bounded queue/retry
  values; SQLite connections are non-pooled short-lived connections with a finite busy
  timeout.

## Schema (v3)

`accounts`, `characters`, `player_state`, `receipts`, `ledger`, `outbox` (plus `dead_at`),
`leases`, `outbox_consumers`, `consumer_effects`, `life_state`, `life_receipts`,
`schema_migrations`.

Timestamps are round-trip UTC strings; content hashes use canonical JSON (sorted object
keys) with SHA-256. v1→v2 adds outbox dead-lettering; v2→v3 adds life provenance and return
receipts. Both upgrades are exercised from a synthetic v1 database.

## Evidence (this checkpoint)

| Item | State |
| --- | --- |
| Library + test + harness projects tracked | IMPLEMENTED |
| Clean-clone restore/build/test | TESTED (see PR/issue evidence) |
| Atomic state/receipt/ledger/outbox | IMPLEMENTED + TESTED |
| Replay/conflict/owner/stale revision | IMPLEMENTED + TESTED |
| Principal account ownership at command/lease boundary | IMPLEMENTED + TESTED |
| Lease/fencing/reconnect grace | IMPLEMENTED + TESTED in-process and across processes (lease contention, expired owner vs takeover) |
| Crash before/after commit, lost response | IMPLEMENTED + TESTED with subprocess kill |
| Outbox claim/retry/ack/dedupe/cursor | IMPLEMENTED + TESTED |
| Outbox dispatcher: bounded batch, retry budget, poison dead-letter | IMPLEMENTED + TESTED |
| Life/death/return before/after + full result receipt | IMPLEMENTED + TESTED (library-owned DTO; Health not wired) |
| Ownership-gated state/receipt reads | IMPLEMENTED + TESTED |
| Health integration guide / feature-gate review pack | `docs/production/Qoder_Remote_Persistence_Handoff_vi.md` (review input, not integration) |
| 10.000 replays and 300-character churn | TESTED (no life/receipt/ledger/outbox growth) |
| Migration checksum/future version, v1→v3 upgrade, integrity | IMPLEMENTED + TESTED |
| Backup/restore/corrupt/truncated/digest | IMPLEMENTED + TESTED |
| Restore staged/replace, locked target preserved, repeat restore | IMPLEMENTED + TESTED |
| IO-denied via real file lock on Windows / chmod on Unix (backup and restore) | TESTED in CI Linux and locally; ACL/disk-full still UNVERIFIED |
| Readiness/metrics with redacted output | IMPLEMENTED + TESTED |
| Benchmark commit/replay/outbox/contention | MEASURED on this machine (see R2 report) |
| Disk-full / IO-denied / ACL-denied recovery | IO-denied TESTED with a locked file; disk-full and ACL UNVERIFIED |
| PostgreSQL provider | NOT IMPLEMENTED (production target unchanged) |
| Health/gameplay adapter integration | NOT IMPLEMENTED (waits for Codex review; library passing is not Health durability) |
| Domain capability adapters for gameplay owners | DTO/interface/version registry IMPLEMENTED; handlers unsupported by design |

## Dependencies

| Package | Version | License |
| --- | --- | --- |
| Microsoft.Data.Sqlite | 10.0.0 | MIT |
| SQLitePCLRaw.lib.e_sqlite3 | 2.1.13 (pinned past GHSA-2m69-gcr7-jv3q) | Apache-2.0 |
| SQLite | bundled with SQLitePCLRaw | Public domain |
| xunit / xunit.runner.visualstudio | 2.9.3 / 2.8.2 | Apache-2.0 |
| Microsoft.NET.Test.Sdk | 17.14.1 | MIT |
| coverlet.collector | 6.0.4 | MIT |

`packages.lock.json` files are committed for all three projects; CI restores with
`--locked-mode`.
