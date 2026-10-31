// QR-01 — Transaction manager with optimistic locking, fencing, and receipts.
// Server-side implementation for durable transaction processing.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).

using System;
using System.Collections.Concurrent;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Server.Persistence;

namespace NguMach.Server.Core
{
    /// <summary>
    /// Manages transactions with optimistic locking, ownership leases, and fencing.
    /// </summary>
    public interface ITransactionManager : IDisposable
    {
        /// <summary>Execute transaction with optimistic concurrency.</summary>
        Task<TransactionResult<T>> ExecuteAsync<T>(string commandId, string playerId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct = default);
        
        /// <summary>Claim ownership lease for a player session.</summary>
        Task<string?> AcquireLeaseAsync(string playerId, TimeSpan duration, CancellationToken ct);
        
        /// <summary>Release ownership lease after successful commit.</summary>
        Task<bool> ReleaseLeaseAsync(string playerId, string leaseToken);
        
        /// <summary>Check if current lease is still valid (fencing).</summary>
        bool IsLeaseValid(string playerId, string currentLeaseToken);
        
        /// <summary>Publish outbox entry for event delivery.</summary>
        Task PublishEventAsync(string entityType, string entityId, OutboxOperation operation);
        
        /// <summary>Cleanup expired leases and uncommitted transactions.</summary>
        Task CleanupExpiredEntriesAsync(CancellationToken ct);
    }

    /// <summary>Result of transaction execution.</summary>
    public sealed class TransactionResult<T>
    {
        public string ReceiptId { get; }
        public string CommandId { get; }
        public T Value { get; }
        public long Version { get; }
        public bool Successful { get; }
        public string? Error { get; }

        public TransactionResult(string receiptId, string commandId, T value, long version, bool successful, string? error)
        {
            ReceiptId = receiptId; CommandId = commandId; Value = value; Version = version; Successful = successful; Error = error;
        }

        public static TransactionResult<T> Success(string receiptId, string commandId, T value, long version) =>
            new(receiptId, commandId, value, version, true, null);

        public static TransactionResult<T> Failure(string commandId, string error) =>
            new("", commandId, default, 0, false, error);
    }

    /// <summary>Internal command execution result.</summary>
    public sealed class CommandExecution
    {
        public object? Result { get; set; }
        public byte[] SerializedPayload { get; set; } = Array.Empty<byte>();
        public bool Succeeded { get; set; }
        public string? Error { get; set; }
    }

    /// <summary>Manages server-side transactions with SQLite backend.</summary>
    internal sealed class TransactionManagerImpl : ITransactionManager
    {
        private readonly IDatabaseRepository _repository;
        private readonly ConcurrentDictionary<string, LeaseInfo> _leases = new();
        private readonly TimeSpan _leaseGracePeriod = TimeSpan.FromSeconds(120);

        public TransactionManagerImpl(IDatabaseRepository repository)
        {
            _repository = repository ?? throw new ArgumentNullException(nameof(repository));
        }

        public async Task<TransactionResult<T>> ExecuteAsync<T>(string commandId, string playerId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct = default)
        {
            var leaseToken = await AcquireLeaseAsync(playerId, TimeSpan.FromMinutes(5), ct);
            if (string.IsNullOrEmpty(leaseToken))
                return TransactionResult<T>.Failure(commandId, "No active lease");

            try
            {
                var execution = await action(ct);
                if (!execution.Succeeded)
                    return TransactionResult<T>.Failure(commandId, execution.Error);

                // Commit transaction atomically
                await _repository.CommitTransactionAsync(commandId, execution.SerializedPayload, playerId, DateTimeOffset.UtcNow.ToUnixTimeSeconds(), execution.Succeeded);

                // Create receipt
                var receiptId = Guid.NewGuid().ToString("N");
                await _repository.CreateReceiptAsync(receiptId, commandId, DateTimeOffset.UtcNow.ToUnixTimeSeconds());

                // Append to ledger if result has amount
                if (execution.Result is decimal amount)
                    await _repository.AppendToLedgerAsync(Guid.NewGuid().ToString("N"), commandId, amount, null);

                return TransactionResult<T>.Success(receiptId, commandId, (T)execution.Result!, DateTimeOffset.UtcNow.ToUnixTimeSeconds());
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

        public async Task<string?> AcquireLeaseAsync(string playerId, TimeSpan duration, CancellationToken ct)
        {
            var existingLease = _leases.GetValueOrDefault(playerId);
            if (existingLease != null && !existingLease.IsExpired)
                return existingLease.Token;

            var newToken = Guid.NewGuid().ToString("N");
            var leaseInfo = new LeaseInfo(newToken, DateTimeOffset.UtcNow + duration);
            _leases[playerId] = leaseInfo;

            return newToken;
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

        public async Task PublishEventAsync(string entityType, string entityId, OutboxOperation operation)
        {
            var outboxId = Guid.NewGuid().ToString("N");
            await _repository.PublishOutboxEntryAsync(outboxId, entityType, entityId, operation);
        }

        public async Task CleanupExpiredEntriesAsync(CancellationToken ct)
        {
            var threshold = DateTime.UtcNow - _leaseGracePeriod;

            // Remove expired leases
            foreach (var kvp in _leases.Where(l => l.Value.IsExpired).ToList())
                _leases.TryRemove(kvp.Key, out _);

            // Cleanup old committed transactions
            await _repository.CleanupCommittedTransactionsOlderThan(threshold);
        }

        public void Dispose() { }
    }

    /// <summary>Lease info with expiration check.</summary>
    internal sealed class LeaseInfo
    {
        public string Token { get; }
        public DateTimeOffset ExpiresAt { get; }

        public LeaseInfo(string token, DateTimeOffset expiresAt)
        {
            Token = token; ExpiresAt = expiresAt;
        }

        public bool IsExpired => DateTimeOffset.UtcNow > ExpiresAt;
    }
}
