# QODER Remote - Health Module Integration Specification

**Issue**: #79  
**Component**: `Server.Health` → `Server.Persistence` interface contract  
**Version**: 1.0.0-alpha  
**Date**: 2026-11-01  

---

## Overview

This document specifies the interface contract between `Health` subsystem and `Server.Persistence` module for durable transaction management.

The Health module needs to persist player state changes (inventory, quests, combat state) through the persistence layer while maintaining transactional integrity.

---

## API Interface Definition

```csharp
namespace NguMach.Server.Health
{
    /// <summary>
    /// Interface for Health subsystem to interact with Server Persistence layer.
    /// Provides transactional persistence for all Health-related mutations.
    /// </summary>
    public interface IHealthPersistenceAPI : IDisposable
    {
        // ── Transaction Management ───────────────────────────────────────
        
        /// <summary>
        /// Submit a mutation command to the transaction queue with optimistic locking.
        /// Returns receipt ID on success, null if conflict detected.
        /// </summary>
        Task<TransactionReceipt?> SubmitMutationAsync(
            string playerId, 
            string commandId, 
            byte[] mutationPayload, 
            long expectedRevision,
            CancellationToken ct);

        /// <summary>
        /// Retry a pending uncertain mutation after connection reestablishment.
        /// </summary>
        Task<bool> RetryPendingMutationAsync(string playerId, string commandId, CancellationToken ct);

        // ── State Retrieval ─────────────────────────────────────────────
        
        /// <summary>Get latest committed transaction for a specific entity type.</summary>
        Task<StoredTransaction?> GetEntityTransaction(string playerId, string entityType, string entityId);

        /// <summary>Get inventory revision current as of this point in time.</summary>
        Task<long> GetCurrentInventoryRevision(string playerId);

        /// <summary>Get quest journal revision.</summary>
        Task<long> GetQuestJournalRevision(string playerId);

        /// <summary>Get pending/uncertain mutations awaiting acknowledgment.</summary>
        Task<IReadOnlyList<PendingMutation>> GetPendingMutations(string playerId);

        // ── Receipt Querying ────────────────────────────────────────────
        
        /// <summary>Get receipt for successful transaction by command ID.</summary>
        Task<TransactionReceipt?> GetReceiptByCommandId(string commandId);

        /// <summary>Get receipts within time window for audit purposes.</summary>
        Task<IReadOnlyList<TransactionReceipt>> GetReceiptsInRange(DateTime start, DateTime end);

        // ── Mutation Effects ────────────────────────────────────────────
        
        /// <summary>Record ledger entry for financial transactions.</summary>
        Task RecordLedgerEntry(string commandId, decimal amount, string currencyId, string metadata);

        /// <summary>Publish outbox event for eventual consistency consumers.</summary>
        Task PublishMutationEvent(string commandId, EventType eventType, Dictionary<string, object> data);

        // ── Checkpoint Management ───────────────────────────────────────
        
        /// <summary>Force checkpoint at current point in time.</summary>
        Task<string> CreateCheckpointAsync(string reason);

        /// <summary>Restore state from specified checkpoint.</summary>
        Task<RestoreResult> RestoreFromCheckpointAsync(string checkpointId);
    }

    /// <summary>Holds pending mutation details waiting for server acknowledgment.</summary>
    public sealed class PendingMutation
    {
        public string CommandId { get; set; } = "";
        public byte[] Payload { get; set; } = Array.Empty<byte>();
        public DateTime QueuedAt { get; set; }
        public int RetryCount { get; set; }
    }

    /// <summary>Describes event types for mutation publication.</summary>
    public enum EventType { MutationCreated, MutationAcknowledged, MutationRejected, SessionEnded }
}
```

---

## Implementation Requirements

### 1. **Optimistic Locking Semantics**

All mutation submissions MUST implement version checking:

```csharp
// Example implementation flow:
public async Task<TransactionReceipt?> SubmitMutationAsync(...)
{
    // Step 1: Validate client-provided revision matches server state
    var currentRev = await _repository.GetCurrentRevision(playerId, entityType);
    if (currentRev != expectedRevision)
        return null; // Conflict - client is stale

    // Step 2: Execute transaction atomically
    using var tx = await _db.BeginTransactionAsync();
    
    // Insert lease first for ownership tracking
    await _repository.InsertLease(commandId, playerId, leaseToken, expiresAt);
    
    // Then insert transaction data
    await _repository.CommitTransaction(cmdId, payload, playerId, currentRev + 1, true);
    
    // Finally generate receipt with new version
    var receipt = await _repository.CreateReceipt(cmdId, currentRev + 1);
    
    await tx.CommitAsync();
    
    return receipt;
}
```

### 2. **Ownership Validation**

Each transaction MUST include lease token validation:

```sql
-- Verify player still owns this session at commit time
SELECT COUNT(*) FROM leases 
WHERE command_id = @CommandId 
  AND player_id = @PlayerId 
  AND lease_token = @LeaseToken
  AND expires_at > CURRENT_TIMESTAMP;
```

If count == 0, reject transaction with "Stale lease" error.

### 3. **Outbox Delivery Guarantee**

All mutations MUST publish to outbox table before acknowledging success:

```sql
INSERT INTO outbox (outbox_id, entity_type, entity_id, operation, created_at)
VALUES (@OutboxId, 'Mutation', @CommandId, 0, CURRENT_TIMESTAMP);

-- Ensure subscriber processes this entry eventually
```

Delivery semantics: At-least-once via polling unprocessed entries every X seconds.

---

## Usage Examples

### From Health Controller

```csharp
public class HealthController : MonoBehaviour
{
    [Inject] private IHealthPersistenceAPI _persistence { get; set; }
    
    private async void OnItemCollect(ItemCollectionData data)
    {
        var mutation = SerializeInventoryUpdate(data);
        
        var receipt = await _persistence.SubmitMutationAsync(
            playerId: LocalPlayerId,
            commandId: Guid.NewGuid().ToString("N"),
            mutationPayload: mutation,
            expectedRevision: InventoryRevision,
            CancellationToken.None);
        
        if (receipt != null)
        {
            InventoryRevision = receipt.Version; // Update local cache
            ShowSuccessFeedback();
        }
        else
        {
            // Client stale - force refresh from server
            ForceRefreshFromServer();
        }
    }
}
```

### From Recovery Manager

```csharp
public class CrashRecoveryService : MonoBehaviour
{
    [Inject] private IHealthPersistenceAPI _persistence { get; set; }
    
    private async Task RecoverUncommittedState()
    {
        var pending = await _persistence.GetPendingMutations(LocalPlayerId);
        
        foreach (var pm in pending)
        {
            // Re-execute mutation with fresh state
            var result = await _persistence.SubmitMutationAsync(
                LocalPlayerId,
                pm.CommandId,
                pm.Payload,
                /* use latest server revision */
                await _persistence.GetCurrentInventoryRevision(LocalPlayerId),
                CancellationToken.None);
            
            if (result == null)
            {
                Debug.Log($"Mutation {pm.CommandId} failed retry, marking completed");
                await MarkTransactionCompleted(pm.CommandId);
            }
        }
    }
}
```

---

## Error Handling

### Standardized Response Codes

| Scenario | HTTP Status | Receipt Result |
|----------|-------------|----------------|
| Optimistic lock failure | 409 Conflict | `null` |
| Stale lease/token expired | 403 Forbidden | Error message |
| Invalid signature/format | 400 Bad Request | Error code |
| Rate limit exceeded | 429 Too Many Requests | Retry-After header |
| Database write error | 500 Internal Server | Rollback automatic |

---

## Performance Considerations

### Expected Latency Bounds

| Operation | p99 Latency Target | Notes |
|-----------|-------------------|-------|
| Single mutation submit | <50ms | I/O bound |
| Receipt query | <5ms | Indexed lookup |
| Pending mutations list | <10ms | Paginated results |
| Restore from checkpoint | <2s | Depends on backup size |

### Scaling Strategy

For production deployment (PostgreSQL target):
- Shard by `player_id` for horizontal scaling
- Implement read replicas for heavy query patterns
- Use connection pooling (min 10, max 100 per shard)
- Cache recent revisions in Redis (TTL 60s)

---

## Security Considerations

### Input Validation

Never trust client-provided revisions:
```csharp
// ALWAYS validate on server side
if (expectedRevision <= lastKnownRevision)
    throw new OptimisticLockException($"Client revision {expectedRevision} behind server {lastKnownRevision}");
```

### Authorization

Check player owns entity before accepting mutation:
```sql
SELECT EXISTS(SELECT 1 FROM characters WHERE id = @PlayerId AND active = true);
-- If false, reject mutation immediately
```

---

## Migration Path

### Phase 1: SQLite Prototype (Current)
- Single-host storage with WAL mode
- All features available but not distributed
- Feature gate OFF until validated

### Phase 2: PostgreSQL Production
- Replace `SqliteDatabaseRepository` with `PostgresDatabaseRepository`
- Maintain same interface contract (swap-in compatible)
- Enable sharding and replication

### Phase 3: Cloud Managed Service
- Connect to RDS/Cloud SQL managed instance
- Enable automated failover
- Implement multi-region read replica pattern

Interface remains unchanged throughout migration.

---

## Testing Strategy

### Unit Tests

```csharp
[Fact]
public async Task SubmitMutationAsync_OptimisticLock_FailsOnConflict()
{
    // Setup two concurrent players modifying same entity
    await db.UpdateEntity("item-123", rev: 1);
    var receipt1 = await api.SubmitMutationAsync(..., expectedRevision: 1); // Succeeds
    
    var receipt2 = await api.SubmitMutationAsync(..., expectedRevision: 1); // Should fail
    
    receipt1.Should().NotBeNull();
    receipt2.Should().BeNull();
}
```

### Integration Tests (Harness)

Test actual database operations with real transactions and concurrent access via subprocess spawning.

See `Server.Harness/FenceIdentityTests.cs` for examples.

---

## Related Documentation

- Issue #79: https://github.com/khanhcoder97/ngumach-huyenan/issues/79
- PR #98: https://github.com/khanhcoder97/ngumach-huyenan/pull/98
- Server.Persistence README.md: Integration guide
- Work Order 11 requirements: Scope definition

---

**Document Owner**: QODER Remote Development Team  
**Last Updated**: 2026-11-01  
**Status**: Draft - Awaiting Review by Health module owners
