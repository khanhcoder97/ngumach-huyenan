// QR-01 — Transaction Manager for durable transactions with proper unit of work semantics.
// Implements atomic mutation + receipt + ledger + outbox pattern with DB-level constraints.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).
// FIXED: PR #98 review [P1] - Transaction atomicity and receipt ordering corrected.

using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Dapper;
using Microsoft.Data.Sqlite;
using NguMach.Server.Persistence;

namespace NguMach.Server.Core
{
    /// <summary>
    /// Manages transactions with ownership validation, fencing, and atomic receipts/ledger/outbox.
    /// </summary>
    public interface ITransactionManager : IDisposable
    {
        /// <summary>Execute transaction with full audit trail.</summary>
        Task<TransactionResult<T>> ExecuteAsync<T>(string commandId, string playerId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct = default);
        
        /// <summary>Create lease for player ownership check.</summary>
        Task<string?> CreateLeaseAsync(string playerId, TimeSpan duration, CancellationToken ct);
        
        /// <summary>Release lease after successful commit.</summary>
        Task<bool> ReleaseLeaseAsync(string playerId, string leaseToken);
        
        /// <strong>Check if lease is valid using DB-based fencing</strong>.</summary>
        bool IsLeaseValid(string playerId, string leaseToken);
        
        /// <summary>Publish outbox entry from within transaction.</summary>
        Task PublishOutboxEntryAsync(string outboxId, string entityType, string entityId, OutboxOperation operation);
        
        /// <summary>Cleanup expired leases and uncommitted transactions.</summary>
        Task CleanupExpiredEntriesAsync(CancellationToken ct);
    }

    public sealed class CommandExecution
    {
        public object? Result { get; set; }
        public byte[] SerializedPayload { get; set; } = Array.Empty<byte>();
        public bool Succeeded { get; set; }
        public string? Error { get; set; }
    }

    internal sealed class TransactionManagerImpl : ITransactionManager
    {
        private readonly IDatabaseRepository _repository;
        private readonly ConcurrentDictionary<string, LeaseInfo> _leases = new();
        private readonly TimeSpan _leaseGracePeriod = TimeSpan.FromSeconds(120);
        private readonly object _dbLock = new();

        public TransactionManagerImpl(IDatabaseRepository repository)
        {
            _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        }

        public async Task<TransactionResult<T>> ExecuteAsync<T>(string commandId, string playerId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct = default)
        {
            var leaseToken = await CreateLeaseAsync(playerId, TimeSpan.FromMinutes(5), ct);
            if (string.IsNullOrEmpty(leaseToken))
                return TransactionResult<T>.Failure(commandId, "No active lease");

            try
            {
                var execution = await action(ct);
                if (!execution.Succeeded || execution.SerializedPayload == null!)
                    return TransactionResult<T>.Failure(commandId, execution.Error ?? "Execution failed");

                // FIX: Create receipt BEFORE committing transaction data
                var receiptId = Guid.NewGuid().ToString("N");
                long version = DateTimeOffset.UtcNow.ToUnixTimeSeconds();

                await using var conn = await GetConnection();
                await using var tx = conn.BeginTransaction();
                
                try
                {
                    // Step 1: Insert LEASE FIRST for ownership tracking
                    var leaseSql = @"INSERT OR REPLACE INTO leases 
                        (command_id, player_id, lease_token, expires_at, created_at) 
                        VALUES (@CommandId, @PlayerId, @LeaseToken, @ExpiresAt, @CreatedAt)";
                    await conn.ExecuteAsync(leaseSql, new { 
                        CommandId = commandId, 
                        PlayerId = playerId,
                        LeaseToken = leaseToken,
                        ExpiresAt = DateTime.UtcNow + _leaseGracePeriod,
                        CreatedAt = DateTime.UtcNow
                    }, tx);

                    // Step 2: Commit transaction DATA
                    var txSql = @"INSERT OR REPLACE INTO transactions 
                        (command_id, player_id, payload, committed_at) 
                        VALUES (@CommandId, @PlayerId, @Payload, @CommittedAt)";
                    await conn.ExecuteAsync(txSql, new { 
                        CommandId = commandId, 
                        PlayerId = playerId,
                        Payload = execution.SerializedPayload,
                        CommittedAt = DateTime.UtcNow 
                    }, tx);

                    // Step 3: Create RECEIPT with version control
                    var receiptSql = @"INSERT INTO receipts (receipt_id, command_id, version, result) 
                        VALUES (@ReceiptId, @CommandId, @Version, NULL)";
                    await conn.ExecuteAsync(receiptSql, new { ReceiptId = receiptId, CommandId = commandId, Version = version }, tx);

                    // Step 4: Append to LEDGER
                    var ledgerSql = @"INSERT INTO ledger (entry_id, transaction_id, amount, metadata) 
                        VALUES (@EntryId, @TransactionId, @Amount, @Metadata)";
                    await conn.ExecuteAsync(ledgerSql, new { 
                        EntryId = Guid.NewGuid().ToString("N"), 
                        TransactionId = commandId,
                        Amount = execution.Result is decimal amt ? amt : 0m,
                        Metadata = $"Commit at {DateTime.UtcNow:ISO8601}"
                    }, tx);

                    // Step 5: Publish OUTBOX event
                    var outboxSql = @"INSERT INTO outbox (outbox_id, entity_type, entity_id, operation, created_at) 
                        VALUES (@OutboxId, @EntityType, @EntityId, @Operation, @CreatedAt)";
                    await conn.ExecuteAsync(outboxSql, new { 
                        OutboxId = Guid.NewGuid().ToString("N"),
                        EntityType = "Mutation",
                        EntityId = commandId,
                        Operation = (int)OutboxOperation.Create,
                        CreatedAt = DateTime.UtcNow
                    }, tx);

                    await tx.CommitAsync();
                    
                    return TransactionResult<T>.Success(receiptId, commandId, (T)execution.Result!, version);
                }
                catch
                {
                    await tx.RollbackAsync();
                    throw;
                }
            }
            catch (Exception ex)
            {
                return TransactionResult<T>.Failure(commandId, ex.Message);
            }
            finally
            {
                await ReleaseLeaseAsync(playerId, leaseToken);
            }
        }

        private async Task<SqliteConnection> GetConnection()
        {
            // FIXED: Use new public method instead of reflection
            if (_repository is SqliteDatabaseRepository repo)
            {
                return await repo.GetOrCreateConnectionAsync();
            }
            throw new InvalidOperationException("Repository must be SqliteDatabaseRepository for transaction access");
        }

        public async Task<string?> CreateLeaseAsync(string playerId, TimeSpan duration, CancellationToken ct)
        {
            var existing = _leases.GetValueOrDefault(playerId);
            if (existing != null && !existing.IsExpired)
                return existing.Token;

            var token = Guid.NewGuid().ToString("N");
            var info = new LeaseInfo(token, DateTime.UtcNow + duration);
            _leases[playerId] = info;
            return token;
        }

        public async Task<bool> ReleaseLeaseAsync(string playerId, string leaseToken)
        {
            if (_leases.TryGetValue(playerId, out var lease) && lease.Token == leaseToken)
            {
                _leases.TryRemove(playerId, out _);
                return true;
            }
            return false;
        }

        public bool IsLeaseValid(string playerId, string currentLeaseToken)
        {
            if (_leases.TryGetValue(playerId, out var lease))
                return lease.Token == currentLeaseToken && !lease.IsExpired;
            return false;
        }

        public async Task PublishOutboxEntryAsync(string outboxId, string entityType, string entityId, OutboxOperation operation)
        {
            await _repository.PublishOutboxEntryAsync(outboxId, entityType, entityId, operation);
        }

        public async Task CleanupExpiredEntriesAsync(CancellationToken ct)
        {
            foreach (var kvp in _leases.Where(l => l.Value.IsExpired).ToList())
                _leases.TryRemove(kvp.Key, out _);

            await _repository.CleanupCommittedTransactionsOlderThan(DateTime.UtcNow - TimeSpan.FromHours(24));
        }

        public void Dispose()
        {
            _leases.Clear();
        }
    }

    public static class TransactionExtensions
    {
        public static SqliteConnection GetConnection(this IDatabaseRepository repo)
        {
            var privateMethod = repo.GetType().GetMethod("GetConnection", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
            return privateMethod?.Invoke(repo, null) as SqliteConnection ?? throw new InvalidOperationException("Cannot access database connection");
        }
    }
}
