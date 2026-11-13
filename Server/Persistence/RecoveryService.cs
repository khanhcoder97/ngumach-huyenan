namespace NguMach.Server.Persistence;

/// <summary>
/// Post-crash inspection and recovery entry point. It never invents committed data: SQLite
/// rolls back an interrupted transaction, this service checkpoints the WAL, verifies the
/// file and reports pending outbox work so the caller can resume publication.
/// </summary>
public sealed class RecoveryService
{
    private readonly PersistenceDatabase _database;
    private readonly OutboxStore _outbox;

    public RecoveryService(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
        _outbox = new OutboxStore(database);
    }

    public async Task<RecoveryReport> RecoverAsync(DateTimeOffset? now = null, CancellationToken cancellationToken = default)
    {
        var clock = now ?? DateTimeOffset.UtcNow;
        var integrity = await _database.VerifyIntegrityAsync(cancellationToken).ConfigureAwait(false);
        var checkpoint = await _database.CheckpointWalAsync(cancellationToken).ConfigureAwait(false);
        var counts = await _database.GetTableCountsAsync(cancellationToken).ConfigureAwait(false);
        var pendingOutbox = await _outbox.GetPendingCountAsync(clock, cancellationToken).ConfigureAwait(false);
        var version = await _database.GetSchemaVersionAsync(cancellationToken).ConfigureAwait(false);

        return new RecoveryReport(integrity.IsHealthy, checkpoint.Succeeded, version, pendingOutbox, counts, integrity, checkpoint);
    }
}

public sealed record RecoveryReport(
    bool Healthy,
    bool WalCheckpointSucceeded,
    int SchemaVersion,
    long PendingOutbox,
    IReadOnlyDictionary<string, long> TableCounts,
    IntegrityReport Integrity,
    WalCheckpointReport Checkpoint);
