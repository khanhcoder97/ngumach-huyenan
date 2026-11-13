using System.Data;
using System.Globalization;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// QR-01 atomic unit of work. State, expected revision, receipt (request hash + committed
/// result), ledger and outbox are written in one SQLite IMMEDIATE transaction. A replay
/// returns the exact stored result; a different payload or foreign owner is a conflict.
/// </summary>
public sealed class DurableUnitOfWork
{
    private readonly PersistenceDatabase _database;

    public DurableUnitOfWork(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
    }

    public async Task<MutationOutcome> ExecuteAsync(
        MutationRequest request,
        Func<MutationContext, PlanDecision> planner,
        CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(request);
        ArgumentNullException.ThrowIfNull(planner);
        Validate(request);

        var requestHash = CanonicalJson.HashRequest(request.Operation, request.RequestJson);
        var committedAt = DateTimeOffset.UtcNow;

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);

        var receipt = await ReadReceiptAsync(connection, transaction, request.IdempotencyKey, cancellationToken).ConfigureAwait(false);
        if (receipt is not null)
        {
            if (!string.Equals(receipt.OwnerCharacterId, request.OwnerCharacterId, StringComparison.Ordinal))
            {
                return MutationOutcome.Rejected(MutationStatus.OwnerConflict, "idempotency-key-owned-by-another-character");
            }

            if (!string.Equals(receipt.RequestHash, requestHash, StringComparison.Ordinal))
            {
                return MutationOutcome.Rejected(MutationStatus.RequestConflict, "idempotency-key-reused-with-different-payload");
            }

            return new MutationOutcome(MutationStatus.Replayed, null, receipt.Revision, receipt.ResultJson, true, 0, 0);
        }

        if (!await IdentityStore.CharacterExistsAsync(connection, transaction, request.OwnerCharacterId, cancellationToken).ConfigureAwait(false))
        {
            return MutationOutcome.Rejected(MutationStatus.OwnershipDenied, PersistenceErrorCodes.CharacterNotFound);
        }

        var lease = await LeaseStore.ReadLeaseAsync(connection, transaction, request.OwnerCharacterId, cancellationToken).ConfigureAwait(false);
        if (lease is null)
        {
            return MutationOutcome.Rejected(MutationStatus.LeaseMissing, "lease-missing");
        }

        // The owner token is authenticated out of band; the fencing token is the commit guard.
        if (lease.FencingToken != request.FencingToken)
        {
            return MutationOutcome.Rejected(MutationStatus.StaleFencingToken, "stale-fencing-token");
        }

        if (lease.ExpiresAt <= committedAt)
        {
            return MutationOutcome.Rejected(MutationStatus.LeaseExpired, "lease-expired");
        }

        var state = await PersistenceDatabase.ReadStateAsync(connection, transaction, request.OwnerCharacterId, cancellationToken).ConfigureAwait(false);
        var currentRevision = state?.Revision ?? 0;
        if (currentRevision != request.ExpectedRevision)
        {
            return MutationOutcome.Rejected(MutationStatus.RevisionConflict, $"expected-revision-{request.ExpectedRevision}-but-found-{currentRevision}");
        }

        var context = new MutationContext(
            request.IdempotencyKey,
            request.OwnerCharacterId,
            request.Operation,
            request.RequestJson,
            request.ExpectedRevision,
            currentRevision,
            state?.StateJson);

        PlanDecision decision;
        try
        {
            decision = planner(context);
        }
        catch (Exception exception) when (exception is not OperationCanceledException)
        {
            return MutationOutcome.Rejected(MutationStatus.Failed, exception.Message);
        }

        if (!decision.IsAccepted)
        {
            return MutationOutcome.Rejected(decision.Status, decision.ErrorCode);
        }

        var plan = decision.Plan!;
        if (string.IsNullOrWhiteSpace(plan.NextStateJson))
        {
            return MutationOutcome.Rejected(MutationStatus.Failed, "planner-returned-empty-state");
        }

        var normalizedResult = CanonicalJson.Normalize(plan.NextStateJson);
        var resultHash = CanonicalJson.Hash(normalizedResult);
        var stateHash = resultHash;
        var nextRevision = currentRevision + 1;
        var timestamp = PersistenceDatabase.Timestamp(committedAt);

        await UpsertStateAsync(connection, transaction, request.OwnerCharacterId, nextRevision, normalizedResult, stateHash, timestamp, cancellationToken).ConfigureAwait(false);
        await InsertReceiptAsync(connection, transaction, request, requestHash, normalizedResult, resultHash, nextRevision, timestamp, cancellationToken).ConfigureAwait(false);

        for (var index = 0; index < plan.Ledger.Count; index++)
        {
            var entry = plan.Ledger[index] ?? throw new ArgumentException("Ledger entries must not be null.", nameof(planner));
            ArgumentException.ThrowIfNullOrWhiteSpace(entry.EntryType);
            var entryId = CanonicalJson.Hash(request.IdempotencyKey + "|ledger|" + index.ToString(CultureInfo.InvariantCulture));
            await InsertLedgerAsync(connection, transaction, entryId, request.IdempotencyKey, request.OwnerCharacterId, entry, timestamp, cancellationToken).ConfigureAwait(false);
        }

        for (var index = 0; index < plan.Outbox.Count; index++)
        {
            var message = plan.Outbox[index] ?? throw new ArgumentException("Outbox messages must not be null.", nameof(planner));
            ArgumentException.ThrowIfNullOrWhiteSpace(message.Topic);
            await InsertOutboxAsync(connection, transaction, request.IdempotencyKey, message, timestamp, cancellationToken).ConfigureAwait(false);
        }

        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);

        return new MutationOutcome(MutationStatus.Committed, null, nextRevision, normalizedResult, false, plan.Ledger.Count, plan.Outbox.Count);
    }

    private static void Validate(MutationRequest request)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(request.IdempotencyKey);
        ArgumentException.ThrowIfNullOrWhiteSpace(request.OwnerCharacterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(request.Operation);
        ArgumentNullException.ThrowIfNull(request.RequestJson);
        if (request.ExpectedRevision < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(request.ExpectedRevision), "ExpectedRevision must not be negative.");
        }

        if (request.FencingToken < 1)
        {
            throw new ArgumentOutOfRangeException(nameof(request.FencingToken), "FencingToken must be positive; acquire a lease first.");
        }
    }

    private static async Task<ReceiptRecord?> ReadReceiptAsync(SqliteConnection connection, SqliteTransaction transaction, string key, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            SELECT idempotency_key, owner_character_id, operation, request_hash, result_json, result_hash, revision, committed_at
            FROM receipts WHERE idempotency_key = $key;
            """;
        command.Parameters.AddWithValue("$key", key);
        await using var reader = await command.ExecuteReaderAsync(cancellationToken).ConfigureAwait(false);
        if (!await reader.ReadAsync(cancellationToken).ConfigureAwait(false))
        {
            return null;
        }

        return new ReceiptRecord(
            reader.GetString(0), reader.GetString(1), reader.GetString(2), reader.GetString(3),
            reader.GetString(4), reader.GetString(5), reader.GetInt64(6), reader.GetString(7));
    }

    private static async Task UpsertStateAsync(SqliteConnection connection, SqliteTransaction transaction, string characterId, long revision, string stateJson, string stateHash, string timestamp, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            INSERT INTO player_state (character_id, revision, state_json, state_hash, updated_at)
            VALUES ($character, $revision, $state, $hash, $updated)
            ON CONFLICT(character_id) DO UPDATE SET
                revision = excluded.revision,
                state_json = excluded.state_json,
                state_hash = excluded.state_hash,
                updated_at = excluded.updated_at;
            """;
        command.Parameters.AddWithValue("$character", characterId);
        command.Parameters.AddWithValue("$revision", revision);
        command.Parameters.AddWithValue("$state", stateJson);
        command.Parameters.AddWithValue("$hash", stateHash);
        command.Parameters.AddWithValue("$updated", timestamp);
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    private static async Task InsertLedgerAsync(SqliteConnection connection, SqliteTransaction transaction, string entryId, string key, string characterId, LedgerEntry entry, string timestamp, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "INSERT INTO ledger (entry_id, idempotency_key, character_id, entry_type, payload_json, created_at) VALUES ($id, $key, $character, $type, $payload, $created);";
        command.Parameters.AddWithValue("$id", entryId);
        command.Parameters.AddWithValue("$key", key);
        command.Parameters.AddWithValue("$character", characterId);
        command.Parameters.AddWithValue("$type", entry.EntryType);
        command.Parameters.AddWithValue("$payload", CanonicalJson.Normalize(entry.PayloadJson));
        command.Parameters.AddWithValue("$created", timestamp);
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    private static async Task InsertOutboxAsync(SqliteConnection connection, SqliteTransaction transaction, string key, OutboxMessage message, string timestamp, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "INSERT INTO outbox (idempotency_key, topic, payload_json, created_at, available_at) VALUES ($key, $topic, $payload, $created, $created);";
        command.Parameters.AddWithValue("$key", key);
        command.Parameters.AddWithValue("$topic", message.Topic);
        command.Parameters.AddWithValue("$payload", CanonicalJson.Normalize(message.PayloadJson));
        command.Parameters.AddWithValue("$created", timestamp);
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    private static async Task InsertReceiptAsync(SqliteConnection connection, SqliteTransaction transaction, MutationRequest request, string requestHash, string resultJson, string resultHash, long revision, string timestamp, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = """
            INSERT INTO receipts (idempotency_key, owner_character_id, operation, request_hash, result_json, result_hash, revision, committed_at)
            VALUES ($key, $owner, $operation, $requestHash, $result, $resultHash, $revision, $committed);
            """;
        command.Parameters.AddWithValue("$key", request.IdempotencyKey);
        command.Parameters.AddWithValue("$owner", request.OwnerCharacterId);
        command.Parameters.AddWithValue("$operation", request.Operation);
        command.Parameters.AddWithValue("$requestHash", requestHash);
        command.Parameters.AddWithValue("$result", resultJson);
        command.Parameters.AddWithValue("$resultHash", resultHash);
        command.Parameters.AddWithValue("$revision", revision);
        command.Parameters.AddWithValue("$committed", timestamp);
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }
}
