using System.Data;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Owns connections, pragmas and schema migrations for one SQLite database file.
/// All writes use short-lived connections so two OS processes can share the file and
/// SQLite's WAL/transaction guarantees remain the source of truth.
/// </summary>
public sealed class PersistenceDatabase
{
    public PersistenceDatabase(PersistenceOptions options)
    {
        ArgumentNullException.ThrowIfNull(options);
        options.Validate();
        Options = options;
        ConnectionString = new SqliteConnectionStringBuilder
        {
            DataSource = options.DatabasePath,
            Mode = SqliteOpenMode.ReadWriteCreate,
            Cache = SqliteCacheMode.Private,
            Pooling = false,
            DefaultTimeout = (int)Math.Ceiling(options.BusyTimeout.TotalSeconds)
        }.ToString();
    }

    public PersistenceOptions Options { get; }

    public string ConnectionString { get; }

    public string DatabasePath => Options.DatabasePath;

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        await ExecuteAsync(connection, null, "PRAGMA journal_mode=WAL;", cancellationToken).ConfigureAwait(false);
        await ExecuteAsync(connection, null, "PRAGMA synchronous=FULL;", cancellationToken).ConfigureAwait(false);
        await MigrateAsync(connection, cancellationToken).ConfigureAwait(false);
    }

    public async Task<int> GetSchemaVersionAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        return await GetSchemaVersionAsync(connection, null, cancellationToken).ConfigureAwait(false);
    }

    /// <summary>
    /// Applies missing migrations inside one transaction and verifies that every already
    /// applied migration still has the expected checksum.
    /// </summary>
    public async Task<int> MigrateAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        await ExecuteAsync(connection, null, "PRAGMA journal_mode=WAL;", cancellationToken).ConfigureAwait(false);
        await MigrateAsync(connection, cancellationToken).ConfigureAwait(false);
        return await GetSchemaVersionAsync(connection, null, cancellationToken).ConfigureAwait(false);
    }

    public async Task<StateRecord?> ReadStateAsync(string characterId, CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        return await ReadStateAsync(connection, null, characterId, cancellationToken).ConfigureAwait(false);
    }

    public async Task<ReceiptRecord?> ReadReceiptAsync(string idempotencyKey, CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = """
            SELECT idempotency_key, owner_character_id, operation, request_hash, result_json, result_hash, revision, committed_at
            FROM receipts WHERE idempotency_key = $key;
            """;
        command.Parameters.AddWithValue("$key", idempotencyKey);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return null;
        }

        return new ReceiptRecord(
            reader.GetString(0),
            reader.GetString(1),
            reader.GetString(2),
            reader.GetString(3),
            reader.GetString(4),
            reader.GetString(5),
            reader.GetInt64(6),
            reader.GetString(7));
    }

    /// <summary>Runs PRAGMA integrity_check and foreign_key_check and returns a report.</summary>
    public async Task<IntegrityReport> VerifyIntegrityAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);

        var integrity = await ScalarAsync<string>(connection, null, "PRAGMA integrity_check;", cancellationToken).ConfigureAwait(false);
        var foreignKeyErrors = new List<string>();
        await using (var command = connection.CreateCommand())
        {
            command.CommandText = "PRAGMA foreign_key_check;";
            await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
            while (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
            {
                foreignKeyErrors.Add(reader.GetString(0));
            }
        }

        var version = await GetSchemaVersionAsync(connection, null, cancellationToken).ConfigureAwait(false);
        return new IntegrityReport(string.Equals(integrity, "ok", StringComparison.OrdinalIgnoreCase), foreignKeyErrors.Count == 0, version, integrity ?? "unknown", foreignKeyErrors);
    }

    /// <summary>Forces a WAL checkpoint. Returns the checkpoint result from SQLite.</summary>
    public async Task<WalCheckpointReport> CheckpointWalAsync(CancellationToken cancellationToken = default)
    {
        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "PRAGMA wal_checkpoint(TRUNCATE);";
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        long busy = -1, log = -1, checkpointed = -1;
        if (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            busy = reader.GetInt64(0);
            log = reader.GetInt64(1);
            checkpointed = reader.GetInt64(2);
        }

        return new WalCheckpointReport(busy == 0, busy, log, checkpointed);
    }

    public async Task<Dictionary<string, long>> GetTableCountsAsync(CancellationToken cancellationToken = default)
    {
        var tables = new[]
        {
            "accounts", "characters", "player_state", "receipts", "ledger", "outbox", "leases", "outbox_consumers", "consumer_effects", "schema_migrations"
        };

        await using var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        var counts = new Dictionary<string, long>(StringComparer.Ordinal);
        foreach (var table in tables)
        {
            var value = await ScalarAsync<long>(connection, null, $"SELECT COUNT(*) FROM {table};", cancellationToken).ConfigureAwait(false);
            counts[table] = value;
        }

        return counts;
    }

    public async Task<SqliteConnection> OpenAsync(CancellationToken cancellationToken = default)
    {
        var connection = new SqliteConnection(ConnectionString);
        await connection.OpenAsync(cancellationToken).ConfigureAwait(false);
        await ExecuteAsync(connection, null, $"PRAGMA busy_timeout={Options.BusyTimeout.TotalMilliseconds:0};", cancellationToken).ConfigureAwait(false);
        await ExecuteAsync(connection, null, "PRAGMA foreign_keys=ON;", cancellationToken).ConfigureAwait(false);
        return connection;
    }

    internal async Task<SqliteConnection> OpenInitializedAsync(CancellationToken cancellationToken)
    {
        var connection = await OpenAsync(cancellationToken).ConfigureAwait(false);
        var version = await GetSchemaVersionAsync(connection, null, cancellationToken).ConfigureAwait(false);
        if (version != PersistenceMigrations.CurrentVersion)
        {
            await connection.DisposeAsync().ConfigureAwait(false);
            throw new PersistenceException(PersistenceErrorCodes.MigrationFailed, $"Database schema version {version} is not usable; expected {PersistenceMigrations.CurrentVersion}. Run initialization/migrations first.");
        }

        return connection;
    }

    private static async Task MigrateAsync(SqliteConnection connection, CancellationToken cancellationToken)
    {
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);
        await ExecuteAsync(connection, transaction, "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, name TEXT NOT NULL, checksum TEXT NOT NULL, applied_at TEXT NOT NULL);", cancellationToken).ConfigureAwait(false);

        var applied = new Dictionary<int, (string Name, string Checksum)>();
        await using (var command = connection.CreateCommand())
        {
            command.Transaction = transaction;
            command.CommandText = "SELECT version, name, checksum FROM schema_migrations ORDER BY version;";
            await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
            while (await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
            {
                applied[reader.GetInt32(0)] = (reader.GetString(1), reader.GetString(2));
            }
        }

        var maxApplied = applied.Count == 0 ? 0 : applied.Keys.Max();
        if (maxApplied > PersistenceMigrations.CurrentVersion)
        {
            throw new PersistenceException(
                PersistenceErrorCodes.MigrationFutureVersion,
                $"Database schema version {maxApplied} is newer than supported version {PersistenceMigrations.CurrentVersion}; refusing to start.");
        }

        foreach (var migration in PersistenceMigrations.All)
        {
            var expectedChecksum = PersistenceMigrations.Checksum(migration);
            if (applied.TryGetValue(migration.Version, out var record))
            {
                if (!string.Equals(record.Checksum, expectedChecksum, StringComparison.Ordinal))
                {
                    throw new PersistenceException(
                        PersistenceErrorCodes.MigrationChecksumMismatch,
                        $"Migration {migration.Version} ({record.Name}) checksum {record.Checksum} does not match the expected {expectedChecksum}.");
                }

                continue;
            }

            await ExecuteAsync(connection, transaction, migration.Sql, cancellationToken).ConfigureAwait(false);
            await using var insert = connection.CreateCommand();
            insert.Transaction = transaction;
            insert.CommandText = "INSERT INTO schema_migrations (version, name, checksum, applied_at) VALUES ($version, $name, $checksum, $applied);";
            insert.Parameters.AddWithValue("$version", migration.Version);
            insert.Parameters.AddWithValue("$name", migration.Name);
            insert.Parameters.AddWithValue("$checksum", expectedChecksum);
            insert.Parameters.AddWithValue("$applied", Timestamp(DateTimeOffset.UtcNow));
            await insert.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
        }

        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
    }

    private static async Task<int> GetSchemaVersionAsync(SqliteConnection connection, SqliteTransaction? transaction, CancellationToken cancellationToken)
    {
        var exists = await ScalarAsync<long>(connection, transaction, "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='schema_migrations';", cancellationToken).ConfigureAwait(false);
        if (exists == 0)
        {
            return 0;
        }

        return (int)await ScalarAsync<long>(connection, transaction, "SELECT COALESCE(MAX(version), 0) FROM schema_migrations;", cancellationToken).ConfigureAwait(false);
    }

    internal static async Task<StateRecord?> ReadStateAsync(SqliteConnection connection, SqliteTransaction? transaction, string characterId, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "SELECT revision, state_json, state_hash FROM player_state WHERE character_id = $character;";
        command.Parameters.AddWithValue("$character", characterId);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return null;
        }

        return new StateRecord(reader.GetInt64(0), reader.GetString(1), reader.GetString(2));
    }

    internal static async Task ExecuteAsync(SqliteConnection connection, SqliteTransaction? transaction, string sql, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = sql;
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    internal static async Task<T> ScalarAsync<T>(SqliteConnection connection, SqliteTransaction? transaction, string sql, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = sql;
        var value = await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
        if (value is null || value is DBNull)
        {
            return default!;
        }

        return (T)Convert.ChangeType(value, typeof(T), System.Globalization.CultureInfo.InvariantCulture);
    }

    internal static string Timestamp(DateTimeOffset value) => value.ToUniversalTime().ToString("O");

    internal static DateTimeOffset ParseTimestamp(string value) => DateTimeOffset.Parse(value, System.Globalization.CultureInfo.InvariantCulture, System.Globalization.DateTimeStyles.RoundtripKind);
}

public sealed record StateRecord(long Revision, string StateJson, string StateHash);

public sealed record ReceiptRecord(
    string IdempotencyKey,
    string OwnerCharacterId,
    string Operation,
    string RequestHash,
    string ResultJson,
    string ResultHash,
    long Revision,
    string CommittedAt);

public sealed record IntegrityReport(bool IntegrityOk, bool ForeignKeysOk, int SchemaVersion, string IntegrityMessage, IReadOnlyList<string> ForeignKeyViolations)
{
    public bool IsHealthy => IntegrityOk && ForeignKeysOk;
}

public sealed record WalCheckpointReport(bool Succeeded, long Busy, long LogFrames, long CheckpointedFrames);
