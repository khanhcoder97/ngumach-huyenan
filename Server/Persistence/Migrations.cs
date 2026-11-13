namespace NguMach.Server.Persistence;

/// <summary>
/// Versioned schema migrations. Every applied migration is recorded with the SHA-256
/// of its SQL text; a changed script or a newer-than-known version fails closed instead
/// of silently booting on an incompatible database.
/// </summary>
public static class PersistenceMigrations
{
    public const int CurrentVersion = 1;

    public static IReadOnlyList<MigrationScript> All { get; } = new[]
    {
        new MigrationScript(1, "qr01-core", """
            CREATE TABLE accounts (
                account_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            );

            CREATE TABLE characters (
                character_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL REFERENCES accounts(account_id),
                created_at TEXT NOT NULL
            );

            CREATE TABLE player_state (
                character_id TEXT PRIMARY KEY REFERENCES characters(character_id),
                revision INTEGER NOT NULL CHECK (revision >= 1),
                state_json TEXT NOT NULL,
                state_hash TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE receipts (
                idempotency_key TEXT PRIMARY KEY,
                owner_character_id TEXT NOT NULL REFERENCES characters(character_id),
                operation TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                result_json TEXT NOT NULL,
                result_hash TEXT NOT NULL,
                revision INTEGER NOT NULL,
                committed_at TEXT NOT NULL
            );
            CREATE INDEX ix_receipts_owner ON receipts(owner_character_id);

            CREATE TABLE ledger (
                entry_id TEXT PRIMARY KEY,
                idempotency_key TEXT NOT NULL REFERENCES receipts(idempotency_key),
                character_id TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE INDEX ix_ledger_key ON ledger(idempotency_key);

            CREATE TABLE outbox (
                outbox_id INTEGER PRIMARY KEY AUTOINCREMENT,
                idempotency_key TEXT NOT NULL,
                topic TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                available_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                claimed_by TEXT,
                claim_expires_at TEXT,
                acked_at TEXT,
                last_error TEXT
            );
            CREATE INDEX ix_outbox_pending ON outbox(acked_at, available_at, outbox_id);

            CREATE TABLE leases (
                character_id TEXT PRIMARY KEY REFERENCES characters(character_id),
                owner_token TEXT NOT NULL,
                fencing_token INTEGER NOT NULL CHECK (fencing_token >= 1),
                acquired_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE TABLE outbox_consumers (
                consumer TEXT PRIMARY KEY,
                cursor_outbox_id INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE consumer_effects (
                effect_id TEXT PRIMARY KEY,
                consumer TEXT NOT NULL,
                applied_at TEXT NOT NULL
            );
            """)
    };

    internal static string Checksum(MigrationScript script) => CanonicalJson.Hash(script.Sql);
}

public sealed record MigrationScript(int Version, string Name, string Sql);
