namespace NguMach.Server.Persistence;

/// <summary>
/// Bounded-work constants for the QR-01 profile. They are deliberately small and static so
/// no caller can turn an outbox loop or retry policy into an unbounded one by accident.
/// </summary>
public static class PersistenceLimits
{
    public const int OutboxDefaultBatch = 10;
    public const int OutboxMaxBatch = 1000;
    public const int OutboxDefaultMaxAttempts = 5;
    public const int OutboxMaxAttempts = 100;
    public const int OutboxMaxBackoffSeconds = 300;
}

/// <summary>
/// Which provider/profile this database is and where the production migration stands.
/// SQLite stays a single-host dev/test profile; PostgreSQL remains the production target.
/// </summary>
public sealed record ProviderMigrationStatus(
    string Provider,
    string Profile,
    string ProductionTarget,
    string Status,
    int SchemaVersion,
    int SupportedSchemaVersion)
{
    public static ProviderMigrationStatus Current(int schemaVersion) =>
        new("sqlite-single-host", "dev-test", "postgresql-online-spec", "not-implemented", schemaVersion, PersistenceMigrations.CurrentVersion);
}

/// <summary>
/// Readiness snapshot for a health/ops endpoint. Contains no payloads, ids, tokens or
/// exception text: only schema/provider state and aggregate counters.
/// </summary>
public sealed record PersistenceReadiness(
    bool Ready,
    bool Degraded,
    string Reason,
    ProviderMigrationStatus Provider,
    bool IntegrityOk,
    bool ForeignKeysOk,
    long PendingOutbox,
    long DeadLetterOutbox,
    DateTimeOffset ObservedAtUtc);

/// <summary>Aggregate metrics with no row contents; safe to log or export as evidence.</summary>
public sealed record PersistenceMetrics(
    ProviderMigrationStatus Provider,
    IReadOnlyDictionary<string, long> TableCounts,
    long PendingOutbox,
    long DeadLetterOutbox,
    long Consumers,
    long AppliedEffects,
    long? OldestPendingOutboxAgeSeconds,
    DateTimeOffset ObservedAtUtc);

/// <summary>
/// Ops read surface for R8. Every call verifies the real database rather than returning a
/// configured "healthy" constant.
/// </summary>
public sealed class PersistenceDiagnostics
{
    private readonly PersistenceDatabase _database;

    public PersistenceDiagnostics(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
    }

    public async Task<PersistenceMetrics> ReadMetricsAsync(
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        var clock = now ?? DateTimeOffset.UtcNow;
        var counts = await _database.GetTableCountsAsync(cancellationToken).ConfigureAwait(false);
        var outbox = new OutboxStore(_database);
        var pending = await outbox.GetPendingCountAsync(clock, cancellationToken).ConfigureAwait(false);
        var dead = await outbox.GetDeadLetterCountAsync(cancellationToken).ConfigureAwait(false);

        long? oldestAge = null;
        await using (var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false))
        await using (var command = connection.CreateCommand())
        {
            command.CommandText = "SELECT MIN(created_at) FROM outbox WHERE acked_at IS NULL AND dead_at IS NULL;";
            var value = await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
            if (value is string oldest)
            {
                var age = clock - PersistenceDatabase.ParseTimestamp(oldest);
                oldestAge = Math.Max(0, (long)age.TotalSeconds);
            }
        }

        return new PersistenceMetrics(
            ProviderMigrationStatus.Current(await _database.GetSchemaVersionAsync(cancellationToken).ConfigureAwait(false)),
            counts,
            pending,
            dead,
            counts["outbox_consumers"],
            counts["consumer_effects"],
            oldestAge,
            clock);
    }

    public async Task<PersistenceReadiness> ReadReadinessAsync(
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        var metrics = await ReadMetricsAsync(now, cancellationToken).ConfigureAwait(false);
        var integrity = await _database.VerifyIntegrityAsync(cancellationToken).ConfigureAwait(false);
        var versionOk = integrity.SchemaVersion == PersistenceMigrations.CurrentVersion;
        var ready = integrity.IntegrityOk && integrity.ForeignKeysOk && versionOk;
        var reason = ready
            ? "ok"
            : !integrity.IntegrityOk ? "integrity-check-failed"
            : !integrity.ForeignKeysOk ? "foreign-key-violation"
            : "schema-version-not-current";
        var degraded = metrics.DeadLetterOutbox > 0;

        return new PersistenceReadiness(
            ready,
            degraded,
            degraded && ready ? "dead-letter-outbox-present" : reason,
            metrics.Provider,
            integrity.IntegrityOk,
            integrity.ForeignKeysOk,
            metrics.PendingOutbox,
            metrics.DeadLetterOutbox,
            metrics.ObservedAtUtc);
    }
}
