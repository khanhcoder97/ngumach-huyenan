# QR-01 Server Persistence (Qoder Remote)

SQLite persistence library for the QR-01 epic (issue #79): durable state, fenced
transactions, idempotent receipts, ledger, outbox and crash/backup recovery.

**Status:** R1 checkpoint delivered (buildable library + tests + harness). This is a
single-host development/test profile. The production target stays the OnlineSpec
PostgreSQL provider; nothing here replaces it.

**Not in scope / not claimed:** no Health endpoint integration, no feature flag turned on,
no production readiness, no MMORPG exactly-once guarantee.

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
  a crash after the effect but before the ack cannot grant twice.
- **Backup/restore** — SQLite online backup API only (never a raw copy of a live WAL
  database), integrity/schema/count verification, SHA-256 manifest, corrupt/truncated and
  digest-mismatch refusal.
- **Migrations** — versioned scripts recorded with SHA-256 checksums; tampering and
  newer-than-supported schema versions fail closed.

## Schema (v1)

`accounts`, `characters`, `player_state`, `receipts`, `ledger`, `outbox`, `leases`,
`outbox_consumers`, `consumer_effects`, `schema_migrations`.

Timestamps are round-trip UTC strings; content hashes use canonical JSON (sorted object
keys) with SHA-256.

## Evidence (this checkpoint)

| Item | State |
| --- | --- |
| Library + test + harness projects tracked | IMPLEMENTED |
| Clean-clone restore/build/test | TESTED (see PR/issue evidence) |
| Atomic state/receipt/ledger/outbox | IMPLEMENTED + TESTED |
| Replay/conflict/owner/stale revision | IMPLEMENTED + TESTED |
| Lease/fencing/reconnect grace | IMPLEMENTED + TESTED in-process and across processes (lease contention) |
| Crash before/after commit, lost response | IMPLEMENTED + TESTED with subprocess kill |
| Outbox claim/retry/ack/dedupe/cursor | IMPLEMENTED + TESTED |
| Migration checksum/future version, integrity | IMPLEMENTED + TESTED |
| Backup/restore/corrupt/truncated/digest | IMPLEMENTED + TESTED |
| Disk-full / IO-denied / ACL-denied recovery | UNVERIFIED (no isolated environment in this checkpoint) |
| PostgreSQL provider | NOT IMPLEMENTED (production target unchanged) |
| Health/gameplay adapter integration | NOT IMPLEMENTED (waits for Codex review; library passing is not Health durability) |
| Life/death/return domain adapter (QOD-25 §7) | NOT IMPLEMENTED (R7; DTO design input only) |

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
