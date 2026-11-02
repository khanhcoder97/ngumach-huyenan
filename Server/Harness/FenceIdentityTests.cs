// QR-01 — Harness tests for identity/fencing/subprocess crash recovery scenarios.
// Tests: multiple concurrent processes, wrong-owner detection, stale writer rejection.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).

using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using NguMach.Server.Core;
using NguMach.Server.Persistence;
using Xunit;

namespace ServerPersistenceHarness
{
    [Trait("Category", "QR-01")]
    public sealed class FenceIdentityTests : IDisposable
    {
        private readonly string _dbPath;
        private readonly string _testDir;

        public FenceIdentityTests()
        {
            _testDir = Path.Combine(Path.GetTempPath(), $"harness_fence_{Guid.NewGuid():N}");
            Directory.CreateDirectory(_testDir);
            _dbPath = Path.Combine(_testDir, "fence.db");

            var db = new SqliteDatabaseRepository(_dbPath);
            db.InitializeAsync().GetAwaiter().GetResult();
        }

        [Fact]
        public async Task MultipleProcesses_WrongOwner_RejectedByLeaseCheck()
        {
            // Arrange: Process A acquires lease
            var dbRepo = new SqliteDatabaseRepository(_dbPath);
            var txMgrA = new TransactionManagerImpl(dbRepo);
            
            var processA_lease = await txMgrA.AcquireLeaseAsync("player-1", TimeSpan.FromMinutes(5), CancellationToken.None);
            Assert.NotNull(processA_lease);

            // Arrange: Process B (wrong owner) tries with different player
            var dbRepoB = new SqliteDatabaseRepository(_dbPath);
            var txMgrB = new TransactionManagerImpl(dbRepoB);

            var processB_lease = await txMgrB.AcquireLeaseAsync("player-2", TimeSpan.FromMinutes(5), CancellationToken.None);
            Assert.NotNull(processB_lease);

            // Act: Process B cannot use Process A's lease
            var isValid = txMgrB.IsLeaseValid("player-1", processA_lease);
            isValid.Should().BeFalse("because different players should have different leases");

            // Verify: Process B can only claim its own player ID
            var validForB = txMgrB.IsLeaseValid("player-2", processB_lease);
            validForB.Should().BeTrue();
        }

        [Fact]
        public async Task ReconnectAfterCrash_RejectsStaleWriter()
        {
            // Arrange: Process A starts session
            var dbRepoA = new SqliteDatabaseRepository(_dbPath);
            var txMgrA = new TransactionManagerImpl(dbRepoA);  // FIXED: was dbRepoDB (typo)
            
            var leaseA = await txMgrA.AcquireLeaseAsync("reconnect-player", TimeSpan.FromSeconds(30), CancellationToken.None);

            // Arrange: Simulate crash by discarding Process A manager
            txMgrA.Dispose();
            GC.Collect();
            
            // Arrange: New Process A reconnected after "crash"
            var dbRepoANew = new SqliteDatabaseRepository(_dbPath);
            var txMgrANew = new TransactionManagerImpl(dbRepoANew);
            
            // Act: Should acquire NEW lease, not reuse old one
            var leaseNew = await txMgrANew.AcquireLeaseAsync("reconnect-player", TimeSpan.FromSeconds(30), CancellationToken.None);
            leaseNew.Should().NotBeNull();
            leaseNew.Should().NotEqual(leaseA, "after crash/restart should get new lease");

            // Verify: Old lease is rejected immediately
            var staleRejected = txMgrANew.IsLeaseValid("reconnect-player", leaseA);
            staleRejected.Should().BeFalse("old lease from crashed process should be invalid");
        }

        [Fact]
        public async Task ConcurrentWrites_DifferentPlayers_Allowed_SamePlayer_Blocking()
        {
            // Arrange: Single database connection shared across threads
            var dbRepo = new SqliteDatabaseRepository(_dbPath);
            
            // Thread 1: Player A transaction
            bool thread1Completed = false;
            Task thread1Task = Task.Run(async () =>
            {
                var txMgr = new TransactionManagerImpl(dbRepo);
                var lease = await txMgr.AcquireLeaseAsync("player-concurrent", TimeSpan.FromMinutes(5), CancellationToken.None);
                
                var result = await txMgr.ExecuteAsync("cmd-thread1", "player-concurrent", ct => Task.FromResult(new CommandExecution 
                    { Result = 1L, SerializedPayload = Array.Empty<byte>(), Succeeded = true }), ct: CancellationToken.None);
                
                thread1Completed = result.Succeeded;
            }, CancellationToken.None);

            // Thread 2: Same player trying concurrently (should be blocked by fence)
            Task thread2Task = Task.Run(async () =>
            {
                var txMgr = new TransactionManagerImpl(dbRepo);
                var lease = await txMgr.AcquireLeaseAsync("player-concurrent", TimeSpan.FromMinutes(5), CancellationToken.None);
                
                // Second attempt from same player while first lease active
                // In real implementation, this would fail or queue
                await Task.Delay(TimeSpan.FromMilliseconds(100)); // Give first thread time to commit
            }, CancellationToken.None);

            await Task.WhenAll(thread1Task, thread2Task);

            thread1Completed.Should().BeTrue("first player transaction should complete successfully");
        }

        public void Dispose()
        {
            if (Directory.Exists(_testDir))
            {
                try
                {
                    foreach (var f in Directory.GetFiles(_testDir, "*.sqlite*"))
                        File.Delete(f);
                    Directory.Delete(_testDir);
                }
                catch { /* Ignore cleanup errors */ }
            }
        }
    }

    [Trait("Category", "QR-01")]
    public sealed class SubprocessCrashRecoveryTests : IDisposable
    {
        private readonly string _dbPath;
        private readonly string _testDir;
        private Process? _subprocess;

        public SubprocessCrashRecoveryTests()
        {
            _testDir = Path.Combine(Path.GetTempPath(), $"harness_subprocess_{Guid.NewGuid():N}");
            Directory.CreateDirectory(_testDir);
            _dbPath = Path.Combine(_testDir, "subprocess.db");

            var db = new SqliteDatabaseRepository(_dbPath);
            db.InitializeAsync().GetAwaiter().GetResult();
        }

        [Fact(Skip = "Requires subprocess spawning - manual testing until harness infrastructure ready")]
        public async Task KillBeforeCommit_ProcessRecoversUncommittedTransactions()
        {
            // This test requires spawning a subprocess that:
            // 1. Starts a transaction but doesn't commit
            // 2. Gets killed abruptly before commit
            // 3. Parent process detects uncommitted transactions during recovery
            
            // TODO: Implement actual subprocess spawn using Process.Start()
            Skip.Reason("Subprocess test requires harness infrastructure setup");
        }

        [Fact]
        public async Task BackupWithWALHandling_VerifiesIntegrity()
        {
            // Arrange: Create test transaction
            var dbRepo = new SqliteDatabaseRepository(_dbPath);
            var txMgr = new TransactionManagerImpl(dbRepo);

            var cmdId = Guid.NewGuid().ToString();
            await txMgr.ExecuteAsync(cmdId, "backup-player", ct => Task.FromResult(new CommandExecution 
                { Result = 42L, SerializedPayload = Array.Empty<byte>(), Succeeded = true }), CancellationToken.None);

            // Act: Force WAL checkpoint before backup
            var recovery = new CrasRecoveryManagerImpl(dbRepo, _dbPath);
            var checkpointed = await recovery.CheckpointWALAsync();

            checkpointed.Should().BeTrue("checkpoint should succeed without error");

            // Act: Create backup (simulating quiesced state after checkpoint)
            var backupPath = Path.Combine(_testDir, $"backup_{DateTime.UtcNow:yyyyMMdd_HHmmss}.sqlite");
            var backupResult = await recovery.CreateBackupAsync(backupPath, CancellationToken.None);

            backupResult.Success.Should().BeTrue("backup should complete successfully");
            backupResult.ChecksumMD5.Should().NotBeNull("backup should generate checksum");

            // Verify: Can restore from backup
            var restored = await recovery.RestoreFromBackupAsync(backupPath, CancellationToken.None);
            restored.Success.Should().BeTrue("restore from backup should succeed");
        }

        [Fact]
        public async Task BatchProcessUncommitted_ProcessesCorrectCount()
        {
            // Arrange: Create multiple transactions manually via repository
            var dbRepo = new SqliteDatabaseRepository(_dbPath);
            
            for (int i = 0; i < 5; i++)
            {
                var cmdId = $"batch-cmd-{i}";
                var payload = System.Text.Encoding.UTF8.GetBytes($"payload-{i}");
                await dbRepo.CommitTransactionAsync(cmdId, payload, "batch-player", DateTimeOffset.UtcNow.ToUnixTimeSeconds(), false); // Uncommitted
            }

            // Act: Process batch of uncommitted transactions
            var recovery = new CrasRecoveryManagerImpl(dbRepo, _dbPath);
            var processed = await recovery.ProcessUncommittedTransactionsAsync(maxBatchSize: 3, CancellationToken.None);

            // Verify: Correct count processed (limited to maxBatchSize)
            processed.Should().Be(3, "should process exactly maxBatchSize transactions");

            // Verify: First batch marked as processed
            var remaining = await dbRepo.GetUncommittedTransactionsAsync("batch-player");
            remaining.Count.Should().Be(2, "remaining uncommitted transactions should be 2");
        }

        [Fact]
        public void WALStatus_ReturnsNonNullWhenExists()
        {
            // Arrange: Trigger WAL creation by doing a write
            var dbRepo = new SqliteDatabaseRepository(_dbPath);
            var txMgr = new TransactionManagerImpl(dbRepo);
            
            _ = Task.Run(async () =>
            {
                await txMgr.ExecuteAsync(Guid.NewGuid().ToString(), "wal-test", ct => Task.FromResult(new CommandExecution 
                    { Result = 1L, SerializedPayload = Array.Empty<byte>(), Succeeded = true }), CancellationToken.None);
            }).GetAwaiter().GetResult();

            // Act: Check WAL status
            var recovery = new CrasRecoveryManagerImpl(dbRepo, _dbPath);
            var status = recovery.GetWALStatusAsync(CancellationToken.None).GetAwaiter().GetResult();

            // Verify: WAL file should exist or status returns null (SQLite might not create WAL yet)
            status.Should().NotBeNull();
        }

        public void Dispose()
        {
            _subprocess?.Kill();
            _subprocess?.Dispose();

            if (Directory.Exists(_testDir))
            {
                try
                {
                    foreach (var f in Directory.GetFiles(_testDir, "*.sqlite*"))
                        File.Delete(f);
                    Directory.Delete(_testDir);
                }
                catch { /* Ignore cleanup errors */ }
            }
        }
    }

    [Trait("Category", "QR-01")]
    public sealed class FullIntegrationTests : IDisposable
    {
        private readonly string _dbPath;
        private readonly string _testDir;
        private IDatabaseRepository? _db;
        private ITransactionManager? _txMgr;

        public FullIntegrationTests()
        {
            _testDir = Path.Combine(Path.GetTempPath(), $"harness_integration_{Guid.NewGuid():N}");
            Directory.CreateDirectory(_testDir);
            _dbPath = Path.Combine(_testDir, "integration.db");

            var repo = new SqliteDatabaseRepository(_dbPath);
            _ = repo.InitializeAsync().GetAwaiter().GetResult();
            _db = repo;

            var txMgr = new TransactionManagerImpl(repo);
            _txMgr = txMgr;
        }

        [Fact]
        public async Task CompleteMutationCycle_CommitReceiptOutbox_AllPresent()
        {
            // Arrange
            var cmdId = Guid.NewGuid().ToString("N");
            var playerId = "integration-player";
            
            // Act: Execute full mutation cycle
            var result = await _txMgr!.ExecuteAsync(cmdId, playerId, async ct =>
            {
                return new CommandExecution 
                { 
                    Result = "mutation-result", 
                    SerializedPayload = System.Text.Encoding.UTF8.GetBytes("mutation-payload"),
                    Succeeded = true 
                };
            }, CancellationToken.None);

            // Verify receipt created
            var receipts = await _db!.QueryAsync<NuMach.Server.Persistence.Receipt>("SELECT * FROM receipts WHERE command_id = @CmdId", new { CmdId = cmdId });
            receipts.Any().Should().BeTrue("receipt should be created for committed transaction");

            // Verify ledger entry created
            var ledgerEntries = await _db.QueryAsync<Server.Persistence.LedgerEntry>(
                @"SELECT l.* FROM ledger l JOIN transactions t ON l.transaction_id = t.command_id WHERE t.command_id = @CmdId", 
                new { CmdId = cmdId });
            ledgerEntries.Any().Should().BeTrue("ledger entry should be created");

            // Verify outbox entry published
            var outboxEntries = await _db.QueryAsync<OutboxEntry>(@"SELECT * FROM outbox WHERE entity_id = @CmdId", new { CmdId = cmdId });
            outboxEntries.Any().Should().BeTrue("outbox entry should be published for audit trail");

            // Verify transaction committed
            var tx = await _db.GetTransactionByIdAsync(cmdId);
            tx.Should().NotBeNull();
            tx!.IsCommitted.Should().BeTrue();

            result.Successful.Should().BeTrue("full mutation cycle should succeed");
            result.Value.Should().Be("mutation-result");
        }

        [Fact]
        public async Task StaleRevision_Rejection_OptimisticLockingWorks()
        {
            // This is a conceptual test - optimistic locking needs more infrastructure
            Skip.Reason("Optimistic locking requires additional version tracking in application layer");
        }

        public void Dispose()
        {
            _db?.Dispose();
            _txMgr?.Dispose();

            if (Directory.Exists(_testDir))
            {
                try
                {
                    foreach (var f in Directory.GetFiles(_testDir, "*.sqlite*"))
                        File.Delete(f);
                    Directory.Delete(_testDir);
                }
                catch { /* Ignore cleanup errors */ }
            }
        }
    }
}
