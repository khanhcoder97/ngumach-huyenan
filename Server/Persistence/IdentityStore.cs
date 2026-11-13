using System.Data;
using Microsoft.Data.Sqlite;

namespace NguMach.Server.Persistence;

/// <summary>
/// Minimal account/character identity store. The authentication edge is responsible for
/// proving which account owns a request; this store only records the durable mapping and
/// lets the unit of work reject unknown or unowned characters.
/// </summary>
public sealed class IdentityStore
{
    private readonly PersistenceDatabase _database;

    public IdentityStore(PersistenceDatabase database)
    {
        _database = database ?? throw new ArgumentNullException(nameof(database));
    }

    public async Task CreateAccountAsync(string accountId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(accountId);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "INSERT OR IGNORE INTO accounts (account_id, created_at) VALUES ($account, $created);";
        command.Parameters.AddWithValue("$account", accountId);
        command.Parameters.AddWithValue("$created", PersistenceDatabase.Timestamp(DateTimeOffset.UtcNow));
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task CreateCharacterAsync(string characterId, string accountId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        ArgumentException.ThrowIfNullOrWhiteSpace(accountId);

        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var transaction = connection.BeginTransaction(IsolationLevel.Serializable, deferred: false);
        if (!await ExistsAsync(connection, transaction, "accounts", "account_id", accountId, cancellationToken).ConfigureAwait(false))
        {
            throw new PersistenceException(PersistenceErrorCodes.AccountNotFound, $"Account '{accountId}' does not exist.");
        }

        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "INSERT OR IGNORE INTO characters (character_id, account_id, created_at) VALUES ($character, $account, $created);";
        command.Parameters.AddWithValue("$character", characterId);
        command.Parameters.AddWithValue("$account", accountId);
        command.Parameters.AddWithValue("$created", PersistenceDatabase.Timestamp(DateTimeOffset.UtcNow));
        await command.ExecuteNonQueryAsync(cancellationToken).ConfigureAwait(false);
        await transaction.CommitAsync(cancellationToken).ConfigureAwait(false);
    }

    public async Task<string?> GetAccountForCharacterAsync(string characterId, CancellationToken cancellationToken = default)
    {
        ArgumentException.ThrowIfNullOrWhiteSpace(characterId);
        await using var connection = await _database.OpenInitializedAsync(cancellationToken).ConfigureAwait(false);
        await using var command = connection.CreateCommand();
        command.CommandText = "SELECT account_id FROM characters WHERE character_id = $character;";
        command.Parameters.AddWithValue("$character", characterId);
        var value = await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
        return value is null or DBNull ? null : (string)value;
    }

    internal static async Task<bool> CharacterExistsAsync(SqliteConnection connection, SqliteTransaction transaction, string characterId, CancellationToken cancellationToken)
    {
        return await ExistsAsync(connection, transaction, "characters", "character_id", characterId, cancellationToken).ConfigureAwait(false);
    }

    internal static async Task<string?> AccountForCharacterAsync(SqliteConnection connection, SqliteTransaction? transaction, string characterId, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = "SELECT account_id FROM characters WHERE character_id = $character;";
        command.Parameters.AddWithValue("$character", characterId);
        var value = await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false);
        return value is null or DBNull ? null : (string)value;
    }

    private static async Task<bool> ExistsAsync(SqliteConnection connection, SqliteTransaction transaction, string table, string column, string value, CancellationToken cancellationToken)
    {
        await using var command = connection.CreateCommand();
        command.Transaction = transaction;
        command.CommandText = $"SELECT COUNT(*) FROM {table} WHERE {column} = $value;";
        command.Parameters.AddWithValue("$value", value);
        var count = (long)(await command.ExecuteScalarAsync(cancellationToken).ConfigureAwait(false) ?? 0L);
        return count > 0;
    }
}
