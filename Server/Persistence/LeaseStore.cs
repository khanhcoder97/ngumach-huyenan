using System.Data;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Durable character lease with a monotonically increasing fencing token. A stale owner
/// (one whose token has been superseded) cannot commit through <see cref="DurableUnitOfWork"/>.
/// </summary>
public sealed class LeaseStore
{
    private readonly PersistenceDatabase _database;
    private readonly PersistenceOptions _options;

    public LeaseStore(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
        _options = database.Options;
    }

    public async Task<LeaseResult> AcquireAsync(
        string characterId,
        string ownerToken,
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default,
        string? principalAccountId = null)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(ownerToken);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);

        if (!await IdentityStore.CharacterExistsAsync(connection, transaction, characterId, cancellationToken).ConfigureAwait(false))
        {
            return LeaseResult.Failed(MutationStatus.OwnershipDenied, PersistenceErrorCodes.CharacterNotFound);
        }

        if (principalAccountId is not null)
        {
            var account = await IdentityStore.AccountForCharacterAsync(connection, transaction, characterId, cancellationToken).ConfigureAwait(false);
            if (!string.Equals(account, principalAccountId, StringComparison.Ordinal))
            {
                return LeaseResult.Failed(MutationStatus.OwnershipDenied, "account-does-not-own-character");
            }
        }

        var existing = await ReadLeaseAsync(connection, transaction, characterId, cancellationToken).ConfigureAwait(false);
        if (existing is null)
        {
            var created = new LeaseGrant(characterId, ownerToken, 1, clock, clock + _options.LeaseTtl);
            await UpsertLeaseAsync(connection, transaction, created, cancellationToken).ConfigureAwait(false);
            await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
            return LeaseResult.Acquired(created, false);
        }

        var expired = existing.ExpiresAt <= clock;
        if (!expired)
        {
            if (string.Equals(existing.OwnerToken, ownerToken, StringComparison.Ordinal))
            {
                var renewed = existing with { ExpiresAt = clock + _options.LeaseTtl };
                await UpsertLeaseAsync(connection, transaction, renewed, cancellationToken).ConfigureAwait(false);
                await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
                return LeaseResult.Acquired(renewed, true);
            }

            return LeaseResult.Failed(MutationStatus.LeaseHeld, "lease-held", existing);
        }

        // The lease has expired. Inside the reconnect grace window the same owner token
        // resumes with the same fencing token so already-issued tokens stay valid.
        var withinGrace = clock <= existing.ExpiresAt + _options.ReconnectGrace;
        if (withinGrace && string.Equals(existing.OwnerToken, ownerToken, StringComparison.Ordinal))
        {
            var resumed = existing with { ExpiresAt = clock + _options.LeaseTtl };
            await UpsertLeaseAsync(connection, transaction, resumed, cancellationToken).ConfigureAwait(false);
            await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
            return LeaseResult.Acquired(resumed, true);
        }

        // Takeover: a new owner (or the old owner after the grace window) receives a
        // higher fencing token, invalidating every in-flight stale writer.
        var taken = new LeaseGrant(characterId, ownerToken, existing.FencingToken + 1, clock, clock + _options.LeaseTtl);
        await UpsertLeaseAsync(connection, transaction, taken, cancellationToken).ConfigureAwait(false);
        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
        return LeaseResult.Acquired(taken, false);
    }

    public async Task<LeaseResult> RenewAsync(
        string characterId,
        string ownerToken,
        long fencingToken,
        DateTimeOffset? now = null,
        CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(ownerToken);
        var clock = now ?? DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);
        var existing = await ReadLeaseAsync(connection, transaction, characterId, cancellationToken).ConfigureAwait(false);
        if (existing is null)
        {
            return LeaseResult.Failed(MutationStatus.LeaseMissing, "lease-missing");
        }

        if (!string.Equals(existing.OwnerToken, ownerToken, StringComparison.Ordinal) || existing.FencingToken != fencingToken)
        {
            return LeaseResult.Failed(MutationStatus.StaleFencingToken, "stale-fencing-token", existing);
        }

        if (existing.ExpiresAt <= clock)
        {
            return LeaseResult.Failed(MutationStatus.LeaseExpired, "lease-expired", existing);
        }

        var renewed = existing with { ExpiresAt = clock + _options.LeaseTtl };
        await UpsertLeaseAsync(connection, transaction, renewed, cancellationToken).ConfigureAwait(false);
        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
        return LeaseResult.Acquired(renewed, true);
    }

    public async Task<bool> ReleaseAsync(string characterId, string ownerToken, long fencingToken, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(ownerToken);

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "DELETE FROM leases WHERE character_id = $character AND owner_token = $owner AND fencing_token = $fencing;";
        command.Parameters.AddWithValue("$character", characterId);
        command.Parameters.AddWithValue("$owner", ownerToken);
        command.Parameters.AddWithValue("$fencing", fencingToken);
        return await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false) > 0;
    }

    public async Task<LeaseGrant?> ReadAsync(string characterId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        return await ReadLeaseAsync(connection, null, characterId, cancellationToken).ConfigureAwait(false);
    }

    internal static async Task<LeaseGrant?> ReadLeaseAsync(SqliteConnection connection, SqliteTransaction? transaction, string characterId, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "SELECT owner_token, fencing_token, acquired_at, expires_at FROM leases WHERE character_id = $character;";
        command.Parameters.AddWithValue("$character", characterId);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return null;
        }

        return new LeaseGrant(
            characterId,
            reader.GetString(0),
            reader.GetInt64(1),
            PersistenceDatabase.ParseTimestamp(reader.GetString(2)),
            PersistenceDatabase.ParseTimestamp(reader.GetString(3)));
    }

    private static async Task UpsertLeaseAsync(SqliteConnection connection, SqliteTransaction transaction, LeaseGrant lease, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            INSERT INTO leases (character_id, owner_token, fencing_token, acquired_at, expires_at)
            VALUES ($character, $owner, $fencing, $acquired, $expires)
            ON CONFLICT(character_id) DO UPDATE SET
                owner_token = excluded.owner_token,
                fencing_token = excluded.fencing_token,
                acquired_at = excluded.acquired_at,
                expires_at = excluded.expires_at;
            """;
        command.Parameters.AddWithValue("$character", lease.CharacterId);
        command.Parameters.AddWithValue("$owner", lease.OwnerToken);
        command.Parameters.AddWithValue("$fencing", lease.FencingToken);
        command.Parameters.AddWithValue("$acquired", PersistenceDatabase.Timestamp(lease.AcquiredAt));
        command.Parameters.AddWithValue("$expires", PersistenceDatabase.Timestamp(lease.ExpiresAt));
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }
}

public sealed record LeaseGrant(string CharacterId, string OwnerToken, long FencingToken, DateTimeOffset AcquiredAt, DateTimeOffset ExpiresAt);

public sealed record LeaseResult(bool Succeeded, MutationStatus Status, string? ErrorCode, LeaseGrant? Lease)
{
    public static LeaseResult Acquired(LeaseGrant lease, bool renewed) =>
        new(true, renewed ? MutationStatus.LeaseRenewed : MutationStatus.LeaseAcquired, null, lease);

    public static LeaseResult Failed(MutationStatus status, string errorCode, LeaseGrant? current = null) =>
        new(false, status, errorCode, current);
}
