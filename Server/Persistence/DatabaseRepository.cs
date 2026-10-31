// QR-01 — Database repository for durable transactions with SQLite provider.
// Server-side implementation with schema migrations and transaction support.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).

using System;
using System.Threading.Tasks;
using Microsoft.Data.Sqlite;
using Dapper;

namespace NguMach.Server.Persistence
{
    /// <summary>
    /// Defines the contract for database operations with migration support.
    /// </summary>
    public interface IDatabaseRepository : IDisposable
    {
        Task InitializeAsync();
        Task MigrateUpAsync(int targetVersion);
        Task<int> GetCurrentSchemaVersion();
        Task CommitTransactionAsync(string commandId, byte[] payload, string playerId, long version, bool successful);
        Task<StoredTransaction?> GetTransactionByIdAsync(string commandId);
        Task<IReadOnlyList<StoredTransaction>> GetUncommittedTransactionsAsync(string playerId);
        Task<TransactionReceipt?> CreateReceiptAsync(string receiptId, string commandId, long version);
        Task AppendToLedgerAsync(string entryId, string transactionId, decimal amount, string metadata);
        Task PublishOutboxEntryAsync(string outboxId, string entityType, string entityId, OutboxOperation operation);
        Task MarkOutboxProcessedAsync(string outboxId);
        Task<IReadOnlyList<OutboxEntry>> GetUnprocessedOutboxEntriesAsync();
        Task CleanupCommittedTransactionsOlderThan(DateTime threshold);
    }

    /// <summary>Represents a stored transaction from the database.</summary>
    public sealed class StoredTransaction
    {
        public string CommandId { get; set; } = "";
        public byte[] Payload { get; set; } = Array.Empty<byte>();
        public string PlayerId { get; set; } = "";
        public DateTime CreatedAt { get; set; }
        public DateTime? CommittedAt { get; set; }
        public string? LeaseToken { get; set; }
        public bool IsCommitted => CommittedAt.HasValue;
    }

    /// <summary>Database receipt after successful commit.</summary>
    public sealed class TransactionReceipt
    {
        public string ReceiptId { get; }
        public string CommandId { get; }
        public long Version { get; }
        public DateTime Timestamp { get; }
        public string? Result { get; }
        public bool Successful { get; }

        public TransactionReceipt(string receiptId, string commandId, long version, DateTime timestamp, string? result, bool successful)
        {
            ReceiptId = receiptId; CommandId = commandId; Version = version; Timestamp = timestamp; Result = result; Successful = successful;
        }
    }

    /// <summary>Operations supported by outbox pattern.</summary>
    public enum OutboxOperation { Create, Update, Delete, SoftDelete }

    /// <summary>Outbox entry for event publication.</summary>
    public sealed class OutboxEntry
    {
        public string OutboxId { get; set; } = "";
        public string EntityType { get; set; } = "";
        public string EntityId { get; set; } = "";
        public OutboxOperation Operation { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? ProcessedAt { get; set; }
        public bool IsProcessed => ProcessedAt.HasValue;
    }

    // ── Implementation ───────────────────────────────────────────────────

    internal sealed class SqliteDatabaseRepository : IDatabaseRepository
    {
        private readonly string _connectionString;
        private readonly object _lock = new object();
        private SqliteConnection? _connection;

        private const int CurrentSchemaVersion = 1;
        private static readonly string[] MigrationScripts =
        {
            @"-- Schema v1: Transactions + Receipts + Ledger + Outbox
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY);
INSERT INTO schema_version VALUES (1);

CREATE TABLE IF NOT EXISTS transactions (
    command_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    payload BLOB NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    committed_at DATETIME,
    lease_token TEXT,
    CHECK (command_id IS NOT NULL AND player_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS receipts (
    receipt_id TEXT PRIMARY KEY,
    command_id TEXT UNIQUE NOT NULL,
    version INTEGER NOT NULL,
    result TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    CHECK (receipt_id IS NOT NULL AND command_id IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS ledger (
    entry_id TEXT PRIMARY KEY,
    transaction_id TEXT NOT NULL,
    amount REAL NOT NULL,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(command_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS outbox (
    outbox_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME,
    CHECK (operation >= 0 AND operation <= 3)
);

CREATE INDEX idx_transactions_player ON transactions(player_id);
CREATE INDEX idx_receipts_command ON receipts(command_id);
CREATE INDEX idx_ledger_transaction ON ledger(transaction_id);
CREATE INDEX idx_outbox_unprocessed ON outbox(processed_at) WHERE processed_at IS NULL;"
        };

        public SqliteDatabaseRepository(string dbPath)
        {
            _connectionString = $"Data Source={dbPath};Journal Mode=WAL;Cache Size=-64000;";
        }

        public async Task InitializeAsync()
        {
            await using var conn = CreateConnection();
            await conn.OpenAsync();

            foreach (var script in MigrationScripts)
                await conn.ExecuteNonQueryAsync(script);
        }

        public void Dispose()
        {
            _connection?.Close();
            _connection?.Dispose();
        }

        private SqliteConnection CreateConnection()
        {
            if (_connection == null || _connection.State != System.Data.ConnectionState.Open)
                _connection = new SqliteConnection(_connectionString);
            return _connection;
        }

        public async Task<int> GetCurrentSchemaVersion()
        {
            var sql = "SELECT COALESCE(MAX(version), 0) FROM schema_version";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            var result = await conn.ExecuteScalarAsync<int>(sql);
            return result ?? 0;
        }

        public async Task MigrateUpAsync(int targetVersion)
        {
            if (targetVersion > CurrentSchemaVersion)
                throw new ArgumentException($"Cannot migrate to version {targetVersion}, max is {CurrentSchemaVersion}");

            var current = await GetCurrentSchemaVersion();
            if (current == 0)
            {
                await using var conn = CreateConnection();
                await conn.OpenAsync();
                await using var tx = conn.BeginTransaction();
                try
                {
                    foreach (var script in MigrationScripts)
                        await conn.ExecuteAsync(script);
                    await tx.CommitAsync();
                }
                catch
                {
                    await tx.RollbackAsync();
                    throw;
                }
            }
        }

        public async Task CommitTransactionAsync(string commandId, byte[] payload, string playerId, long version, bool successful)
        {
            var receiptId = Guid.NewGuid().ToString("N");
            await CreateReceiptAsync(receiptId, commandId, version);

            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await using var tx = conn.BeginTransaction();
            try
            {
                var insertSql = @"INSERT OR REPLACE INTO transactions 
                    (command_id, player_id, payload, committed_at) 
                    VALUES (@CommandId, @PlayerId, @Payload, @CommittedAt)";
                await conn.ExecuteAsync(insertSql, 
                    new { CommandId = commandId, PlayerId = playerId, Payload = payload, CommittedAt = DateTime.UtcNow }, tx);
                
                await tx.CommitAsync();
            }
            catch
            {
                await tx.RollbackAsync();
                throw;
            }
        }

        public async Task<StoredTransaction?> GetTransactionByIdAsync(string commandId)
        {
            var sql = "SELECT command_id, player_id, payload, created_at, committed_at, lease_token FROM transactions WHERE command_id = @CommandId";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            var row = await conn.QueryFirstOrDefaultAsync<StoredTransaction>(sql, new { CommandId });
            return row;
        }

        public async Task<IReadOnlyList<StoredTransaction>> GetUncommittedTransactionsAsync(string playerId)
        {
            var sql = "SELECT * FROM transactions WHERE player_id = @PlayerId AND committed_at IS NULL";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            return await conn.QueryAsync<StoredTransaction>(sql, new { PlayerId = playerId });
        }

        public async Task<TransactionReceipt?> CreateReceiptAsync(string receiptId, string commandId, long version)
        {
            var sql = @"INSERT INTO receipts (receipt_id, command_id, version, result) VALUES (@ReceiptId, @CommandId, @Version, NULL)";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await conn.ExecuteAsync(sql, new { ReceiptId = receiptId, CommandId = commandId, Version = version });
            
            return new TransactionReceipt(receiptId, commandId, version, DateTime.UtcNow, null, true);
        }

        public async Task AppendToLedgerAsync(string entryId, string transactionId, decimal amount, string metadata)
        {
            var sql = @"INSERT INTO ledger (entry_id, transaction_id, amount, metadata) VALUES (@EntryId, @TransactionId, @Amount, @Metadata)";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await conn.ExecuteAsync(sql, new { EntryId = entryId, TransactionId = transactionId, Amount = amount, Metadata = metadata });
        }

        public async Task PublishOutboxEntryAsync(string outboxId, string entityType, string entityId, OutboxOperation operation)
        {
            var sql = @"INSERT INTO outbox (outbox_id, entity_type, entity_id, operation) VALUES (@OutboxId, @EntityType, @EntityId, @Operation)";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await conn.ExecuteAsync(sql, new { OutboxId = outboxId, EntityType = entityType, EntityId = entityId, Operation = (int)operation });
        }

        public async Task MarkOutboxProcessedAsync(string outboxId)
        {
            var sql = "UPDATE outbox SET processed_at = CURRENT_TIMESTAMP WHERE outbox_id = @OutboxId";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await conn.ExecuteAsync(sql, new { OutboxId = outboxId });
        }

        public async Task<IReadOnlyList<OutboxEntry>> GetUnprocessedOutboxEntriesAsync()
        {
            var sql = "SELECT * FROM outbox WHERE processed_at IS NULL ORDER BY created_at ASC";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            return await conn.QueryAsync<OutboxEntry>(sql);
        }

        public async Task CleanupCommittedTransactionsOlderThan(DateTime threshold)
        {
            var sql = @"DELETE FROM transactions 
                WHERE committed_at < @Threshold 
                AND EXISTS (SELECT 1 FROM receipts WHERE receipts.command_id = transactions.command_id)";
            await using var conn = CreateConnection();
            await conn.OpenAsync();
            await conn.ExecuteAsync(sql, new { Threshold = threshold.ToString("ISO8601") });
        }
    }
}
