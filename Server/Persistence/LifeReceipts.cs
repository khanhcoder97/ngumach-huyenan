using System.Data;
using System.Text.Json;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Source-shaped death identity. The event id is derived by the gameplay owner from
/// (character, lifeVersion, deathRevision); this library records it and never mints one.
/// Mirrors QOD-25 §7 without depending on the Health executable.
/// </summary>
public sealed record PlayerDeathSnapshot(
    string CharacterId,
    int LifeVersion,
    long DeathRevision,
    string DeathEventId,
    DateTimeOffset AtUtc);

/// <summary>Life provenance for one character. <c>LatestDeath</c> may belong to an earlier life.</summary>
public sealed record LifeSnapshot(string CharacterId, int LifeVersion, PlayerDeathSnapshot? LatestDeath);

/// <summary>Full committed return answer; every source field is preserved for verbatim replay.</summary>
public sealed record DeathReturnResultSnapshot(
    bool Applied,
    bool Replayed,
    string? ErrorCode,
    string? SessionId,
    string? CharacterId,
    string? MapId,
    double X,
    double Y,
    int Hp,
    int MaxHp,
    int Mp,
    int MaxMp,
    long Revision,
    long ServerTick,
    int InflightCastsCancelled,
    int ReservedCountersCancelled,
    bool GuardWindowClosed,
    bool MovementTimingReset,
    long? NextReturnAllowedAtTick,
    string? DeathEventId,
    int NewLifeVersion);

/// <summary>
/// Before/after snapshots written in the same transaction as state, revision, receipts,
/// ledger and outbox. <c>CommittedUtc</c> is the commit time, never a replay time.
/// </summary>
public sealed record LifeReturnCommit(
    string IdempotencyKey,
    string RequestHash,
    LifeSnapshot Before,
    LifeSnapshot After,
    DeathReturnResultSnapshot CommittedResult,
    DateTimeOffset CommittedUtc);

/// <summary>
/// One life transition committed with a unit of work. A death keeps the life version and
/// records the death identity; a return advances it exactly once. A transition is never
/// applied on replay.
/// </summary>
public sealed record LifeTransition(
    LifeSnapshot Before,
    LifeSnapshot After,
    PlayerDeathSnapshot? Death,
    LifeReturnCommit? Return)
{
    public static LifeTransition ForDeath(LifeSnapshot before, LifeSnapshot after, PlayerDeathSnapshot death) =>
        new(before, after, death, null);

    public static LifeTransition ForReturn(LifeSnapshot before, LifeSnapshot after, LifeReturnCommit commit) =>
        new(before, after, null, commit);
}

public enum ReturnLookupKind
{
    /// <summary>No receipt exists and no obligation was recorded.</summary>
    Missing,

    /// <summary>A committed return receipt exists; replay it verbatim.</summary>
    Committed,

    /// <summary>A receipt was explicitly invalidated. Never treated as Missing or a fresh command.</summary>
    Tombstoned
}

public sealed record ReturnLookup(
    ReturnLookupKind Kind,
    string? OwnerCharacterId,
    string? RequestHash,
    LifeReturnCommit? Commit)
{
    public static ReturnLookup Missing { get; } = new(ReturnLookupKind.Missing, null, null, null);

    public static ReturnLookup Tombstoned(string ownerCharacterId, string requestHash) =>
        new(ReturnLookupKind.Tombstoned, ownerCharacterId, requestHash, null);
}

/// <summary>
/// Read side of the life/death/return adapter (R7). Commits go through
/// <see cref="DurableUnitOfWork"/> with <see cref="MutationPlan.Life"/> so state,
/// revision, receipt and life provenance share one fenced transaction; there is no
/// second writer and no way to record a return after the actor was already mutated.
/// </summary>
public interface ILifeReceiptAdapter
{
    ValueTask<LifeSnapshot?> ReadLifeAsync(string characterId, CancellationToken cancellationToken = default);

    ValueTask<ReturnLookup> LookupReturnAsync(string idempotencyKey, CancellationToken cancellationToken = default);
}

/// <summary>Durable life provenance and return receipts over the QR-01 SQLite profile.</summary>
public sealed class LifeReceiptStore : ILifeReceiptAdapter
{
    private readonly PersistenceDatabase _database;

    public LifeReceiptStore(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
    }

    public async ValueTask<LifeSnapshot?> ReadLifeAsync(string characterId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        return await ReadLifeAsync(connection, null, characterId, cancellationToken).ConfigureAwait(false);
    }

    public async ValueTask<ReturnLookup> LookupReturnAsync(string idempotencyKey, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(idempotencyKey);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        return await LookupReturnAsync(connection, null, idempotencyKey, cancellationToken).ConfigureAwait(false);
    }

    internal static async Task<LifeSnapshot?> ReadLifeAsync(
        SqliteConnection connection,
        SqliteTransaction? transaction,
        string characterId,
        CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "SELECT life_version, latest_death_json FROM life_state WHERE character_id = $character;";
        command.Parameters.AddWithValue("$character", characterId);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return null;
        }

        var lifeVersion = reader.GetInt32(0);
        var death = reader.IsDBNull(1)
            ? null
            : JsonSerializer.Deserialize<PlayerDeathSnapshot>(reader.GetString(1))
              ?? throw new PersistenceException(PersistenceErrorCodes.DatabaseCorrupt, "Stored death record is not readable.");
        return new LifeSnapshot(characterId, lifeVersion, death);
    }

    internal static async Task<ReturnLookup> LookupReturnAsync(
        SqliteConnection connection,
        SqliteTransaction? transaction,
        string idempotencyKey,
        CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            SELECT owner_character_id, request_hash, before_json, after_json, result_json,
                   committed_life_version, committed_at, tombstoned_at
            FROM life_receipts WHERE idempotency_key = $key;
            """;
        command.Parameters.AddWithValue("$key", idempotencyKey);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return ReturnLookup.Missing;
        }

        var owner = reader.GetString(0);
        var requestHash = reader.GetString(1);
        if (!reader.IsDBNull(7))
        {
            return ReturnLookup.Tombstoned(owner, requestHash);
        }

        var before = Deserialize<LifeSnapshot>(reader.GetString(2));
        var after = Deserialize<LifeSnapshot>(reader.GetString(3));
        var result = Deserialize<DeathReturnResultSnapshot>(reader.GetString(4));
        var committedLifeVersion = reader.GetInt32(5);
        var committedAt = PersistenceDatabase.ParseTimestamp(reader.GetString(6));
        if (after.LifeVersion != committedLifeVersion || result.NewLifeVersion != committedLifeVersion)
        {
            throw new PersistenceException(
                PersistenceErrorCodes.DatabaseCorrupt,
                $"Life receipt '{idempotencyKey}' has inconsistent life provenance.");
        }

        return new ReturnLookup(
            ReturnLookupKind.Committed,
            owner,
            requestHash,
            new LifeReturnCommit(idempotencyKey, requestHash, before, after, result, committedAt));
    }

    /// <summary>
    /// Writes the life transition inside the caller's transaction. The stored life version
    /// is the CAS value: a transition built on a stale snapshot is refused, never merged.
    /// </summary>
    internal static async Task WriteTransitionAsync(
        SqliteConnection connection,
        SqliteTransaction transaction,
        MutationRequest request,
        LifeTransition transition,
        string requestHash,
        string timestamp,
        CancellationToken cancellationToken)
    {
        ArgumentNullException.ThrowIfNull(transition);
        var before = transition.Before ?? throw new ArgumentException("Life transition requires a before snapshot.", nameof(transition));
        var after = transition.After ?? throw new ArgumentException("Life transition requires an after snapshot.", nameof(transition));

        if (!string.Equals(before.CharacterId, request.OwnerCharacterId, StringComparison.Ordinal) ||
            !string.Equals(after.CharacterId, request.OwnerCharacterId, StringComparison.Ordinal))
        {
            throw new ArgumentException("Life transition must belong to the request owner.", nameof(transition));
        }

        if (before.LifeVersion < 1 || after.LifeVersion < before.LifeVersion)
        {
            throw new ArgumentException("Life version must not move backwards.", nameof(transition));
        }

        if (transition.Death is null && transition.Return is null)
        {
            throw new ArgumentException("A life transition must record a death or a return.", nameof(transition));
        }

        if (transition.Death is { } death)
        {
            if (!string.Equals(death.CharacterId, request.OwnerCharacterId, StringComparison.Ordinal) ||
                death.LifeVersion != after.LifeVersion ||
                after.LifeVersion != before.LifeVersion ||
                !Equals(after.LatestDeath, death))
            {
                throw new ArgumentException("Death transition must keep the life version and record its own death identity.", nameof(transition));
            }
        }

        if (transition.Return is { } commit)
        {
            if (!string.Equals(commit.IdempotencyKey, request.IdempotencyKey, StringComparison.Ordinal) ||
                !string.Equals(commit.RequestHash, requestHash, StringComparison.Ordinal))
            {
                throw new ArgumentException("Return commit key/hash must match the unit-of-work request.", nameof(transition));
            }

            if (!commit.CommittedResult.Applied || commit.CommittedResult.Replayed ||
                !string.Equals(commit.CommittedResult.CharacterId, request.OwnerCharacterId, StringComparison.Ordinal) ||
                after.LifeVersion != before.LifeVersion + 1 ||
                commit.CommittedResult.NewLifeVersion != after.LifeVersion ||
                !Equals(commit.Before, before) || !Equals(commit.After, after))
            {
                throw new ArgumentException("Return commit must advance the life exactly once and carry its own snapshots.", nameof(transition));
            }
        }

        var current = await ReadLifeAsync(connection, transaction, request.OwnerCharacterId, cancellationToken).ConfigureAwait(false);
        var currentVersion = current?.LifeVersion ?? 1;
        if (currentVersion != before.LifeVersion)
        {
            throw new PersistenceException(
                PersistenceErrorCodes.LifeVersionConflict,
                $"Life version conflict: expected {before.LifeVersion} but found {currentVersion}.");
        }

        if (current is not null && !Equals(current, before))
        {
            throw new PersistenceException(
                PersistenceErrorCodes.LifeVersionConflict,
                $"Life snapshot conflict for character '{request.OwnerCharacterId}'.");
        }

        var afterJson = JsonSerializer.Serialize(after);
        var afterHash = CanonicalJson.HashJson(afterJson);
        var deathJson = after.LatestDeath is null ? null : JsonSerializer.Serialize(after.LatestDeath);
        var deathHash = deathJson is null ? null : CanonicalJson.HashJson(deathJson);

        await using (var upsert = connection.CreateCommand())
        {
            upsert.Transaction = transaction;
            upsert.CommandText = """
                INSERT INTO life_state (character_id, life_version, latest_death_json, latest_death_hash, updated_at)
                VALUES ($character, $version, $death, $deathHash, $updated)
                ON CONFLICT(character_id) DO UPDATE SET
                    life_version = excluded.life_version,
                    latest_death_json = excluded.latest_death_json,
                    latest_death_hash = excluded.latest_death_hash,
                    updated_at = excluded.updated_at;
                """;
            upsert.Parameters.AddWithValue("$character", request.OwnerCharacterId);
            upsert.Parameters.AddWithValue("$version", after.LifeVersion);
            upsert.Parameters.AddWithValue("$death", (object?)deathJson ?? DBNull.Value);
            upsert.Parameters.AddWithValue("$deathHash", (object?)deathHash ?? DBNull.Value);
            upsert.Parameters.AddWithValue("$updated", timestamp);
            await upsert.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
        }

        if (transition.Return is { } returnCommit)
        {
            var beforeJson = JsonSerializer.Serialize(before);
            var resultJson = JsonSerializer.Serialize(returnCommit.CommittedResult);
            await using var insert = connection.CreateCommand();
            insert.Transaction = transaction;
            insert.CommandText = """
                INSERT INTO life_receipts (
                    idempotency_key, owner_character_id, request_hash, committed_life_version,
                    before_json, before_hash, after_json, after_hash, result_json, result_hash, committed_at)
                VALUES (
                    $key, $owner, $requestHash, $lifeVersion,
                    $before, $beforeHash, $after, $afterHash, $result, $resultHash, $committed);
                """;
            insert.Parameters.AddWithValue("$key", request.IdempotencyKey);
            insert.Parameters.AddWithValue("$owner", request.OwnerCharacterId);
            insert.Parameters.AddWithValue("$requestHash", requestHash);
            insert.Parameters.AddWithValue("$lifeVersion", after.LifeVersion);
            insert.Parameters.AddWithValue("$before", beforeJson);
            insert.Parameters.AddWithValue("$beforeHash", CanonicalJson.HashJson(beforeJson));
            insert.Parameters.AddWithValue("$after", afterJson);
            insert.Parameters.AddWithValue("$afterHash", afterHash);
            insert.Parameters.AddWithValue("$result", resultJson);
            insert.Parameters.AddWithValue("$resultHash", CanonicalJson.HashJson(resultJson));
            insert.Parameters.AddWithValue("$committed", PersistenceDatabase.Timestamp(returnCommit.CommittedUtc));
            await insert.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
        }
    }

    private static T Deserialize<T>(string json) =>
        JsonSerializer.Deserialize<T>(json)
        ?? throw new PersistenceException(PersistenceErrorCodes.DatabaseCorrupt, $"Stored {typeof(T).Name} is not readable.");
}
