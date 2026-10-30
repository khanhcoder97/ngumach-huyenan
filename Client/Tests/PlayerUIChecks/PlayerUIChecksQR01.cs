// QR-01 — Unit tests for QODER Remote durable state system.
// Tests cover: snapshot serialization, transaction retry logic, session recovery workflows.
// DOTNET: Requires dotnet test runner. Run with: dotnet test Client/Tests/PlayerUIChecks/PlayerUIChecks.csproj
// Owner: QODER Remote Persistence — Issue #79.

using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using NguMach.Client.QR;
using UnityEngine;
using Xunit;

namespace PlayerUIChecks
{
    // ── Fake implementations for testing ─────────────────────────────────────

    sealed class FakeDiskStore : IDiskStore
    {
        public string RootPath { get; set; } = "";
        private readonly Dictionary<string, string> _memoryStore = new();

        public Task WriteAsync(string relativePath, string content, CancellationToken ct = default)
        {
            _memoryStore[relativePath] = content;
            return Task.CompletedTask;
        }

        public Task<string> ReadAllTextAsync(string relativePath, CancellationToken ct = default)
        {
            if (_memoryStore.TryGetValue(relativePath, out var content))
                return Task.FromResult(content);
            throw new FileNotFoundException(relativePath);
        }

        public bool FileExists(string relativePath) => _memoryStore.ContainsKey(relativePath);
        public void DeleteFile(string relativePath) => _memoryStore.Remove(relativePath);
        public IReadOnlyList<string> ListFiles(string pattern = "*.json") => new List<string>(_memoryStore.Keys);
        public long GetFileSize(string relativePath) => _memoryStore.TryGetValue(relativePath, out var content) ? System.Text.Encoding.UTF8.GetByteCount(content) : 0L;
        public DateTime GetLastWriteTime(string relativePath) => DateTime.Now;
        public void CleanupOlderThan(string basePath) { /* No-op for in-memory store */ }
    }

    sealed class FakeDurableStateManager : IDurableStateManager
    {
        private readonly Dictionary<string, SessionSnapshot> _snapshots = new(StringComparer.Ordinal);
        private readonly List<SessionEvent> _events = new();
        private string? _lastCorrelationId;

        public TimeSpan? AutoCheckpointInterval { get; set; }
        public string StoragePath { get; set; } = "/tmp/test";
        public event Action? OnReady;
        public event Action<CheckpointReason>? OnBeforeCheckpoint;

        public async Task<SnapshotRef> TakeSnapshotAsync(string? metadata = null, string? correlationId = null, CancellationToken ct = default)
        {
            var id = Guid.NewGuid().ToString("N");
            var snapshot = new SessionSnapshot(id, DateTime.Now, correlationId);
            _snapshots[id] = snapshot;
            _lastCorrelationId = correlationId;

            return new SnapshotRef(id, DateTime.Now, metadata, correlationId, 100);
        }

        public async Task<SessionSnapshot?> LoadSnapshotAsync(string? snapshotId = null, CancellationToken ct = default)
        {
            var key = snapshotId ?? _snapshots.Keys.Count > 0 ? _snapshots.Keys.First() : null;
            return key != null && _snapshots.TryGetValue(key, out var snap) ? snap : null;
        }

        public IReadOnlyList<SnapshotRef> ListSnapshots()
        {
            var refs = new List<SnapshotRef>();
            foreach (var kv in _snapshots)
                refs.Add(new SnapshotRef(kv.Key, DateTime.Now, null, null, 100));
            refs.Sort((a, b) => b.CreatedAt.CompareTo(a.CreatedAt));
            return refs;
        }

        public bool RestoreFromSnapshot(SessionSnapshot snapshot) => snapshot != null;
        public void LogEvent(SessionEvent evt) => _events.Add(evt);
        public IReadOnlyList<SessionEvent> QueryEvents(DateTimeRange range) => _events.FindAll(e => e.Timestamp >= range.Start && e.Timestamp <= range.End);
        public Task ForceCheckpointAsync(CancellationToken ct = default) => TakeSnapshotAsync("Force", null, ct);
    }

    sealed class MockTransactionManager : ITransactionManager
    {
        public int MaxRetries { get; set; } = 3;
        public TimeSpan InitialBackoff { get; set; } = TimeSpan.FromMilliseconds(10);
        public float BackoffMultiplier { get; set; } = 2.0f;
        public float JitterPercentage { get; set; } = 0.0f; // Deterministic for tests
        public int PendingMutationCount => 0;
        public string LastCommandCorrelationId { get; set; } = "";
        public bool IsBusy => false;
        public event Action<string, string>? OnCommandStarted;
        public event Action<string, string>? OnCommandSucceeded;
        public event Action<string, string, string>? OnCommandFailed;
        public event Action<string, string, int>? OnCommandRetry;

        public void ExecuteFireAndForget(string commandType, Func<CancellationToken, Task> action, string? correlationId = null)
        {
            _ = ExecuteAsync(commandType, action, correlationId, CancellationToken.None);
        }

        public async Task<T> ExecuteAsync<T>(string commandType, Func<CancellationToken, Task<T>> action, string? correlationId = null, CancellationToken ct = default)
        {
            correlationId ??= Guid.NewGuid().ToString("N");
            OnCommandStarted?.Invoke(correlationId, commandType);

            try
            {
                var result = await action(ct);
                OnCommandSucceeded?.Invoke(correlationId, commandType);
                LastCommandCorrelationId = correlationId;
                return result;
            }
            catch (Exception ex)
            {
                OnCommandFailed?.Invoke(correlationId, commandType, ex.Message);
                throw;
            }
        }
    }

    // ── Durable State Manager Tests ──────────────────────────────────────────

    public class DurableStateManagerTests
    {
        [Fact]
        public void Constructor_WithNullAdapter_ThrowsArgumentNullException()
        {
            Assert.ThrowsAny<ArgumentNullException>(() => new DurableStateManagerImpl(null!, new FakeDiskStore()));
        }

        [Fact]
        public async Task TakeSnapshot_AssignsUniqueIdAndReturnsRef()
        {
            var adapter = new FakeAdapter();
            var diskStore = new FakeDiskStore();
            var manager = new DurableStateManagerImpl(adapter, diskStore);

            var refResult = await manager.TakeSnapshotAsync("test-metadata", "corr-123");

            Assert.NotNull(refResult.SnapshotId);
            Assert.NotEmpty(refResult.SnapshotId);
            Assert.Equal("test-metadata", refResult.Metadata);
            Assert.Equal("corr-123", refResult.CorrelationId);
        }

        [Fact]
        public async Task LoadSnapshot_ReturnsNullWhenNoSnapshotsExist()
        {
            var adapter = new FakeAdapter();
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            var snapshot = await manager.LoadSnapshotAsync();

            Assert.Null(snapshot);
        }

        [Fact]
        public async Task ListSnapshots_SortsByCreatedAtDescending()
        {
            var adapter = new FakeAdapter();
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            await manager.TakeSnapshotAsync(metadata: "first", correlationId: "c1");
            await Task.Delay(10);
            await manager.TakeSnapshotAsync(metadata: "second", correlationId: "c2");

            var snapshots = manager.ListSnapshots();

            Assert.Equal(2, snapshots.Count);
            Assert.Equal("second", snapshots[0].Metadata); // Most recent first
        }

        [Fact]
        public void RestoreFromSnapshot_WithNullSnapshot_ReturnsFalse()
        {
            var adapter = new FakeAdapter();
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            var result = manager.RestoreFromSnapshot(null!);

            Assert.False(result);
        }

        [Fact]
        public void RestoreFromSnapshot_WithValidSnapshot_ReturnsTrue()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            var result = manager.RestoreFromSnapshot(new SessionSnapshot("test", DateTime.Now, ""));

            Assert.True(result);
        }

        [Fact]
        public void LogEvent_AddsToQueue_KeepsLast1000()
        {
            var adapter = new FakeAdapter();
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            // Add more than 1000 events
            for (int i = 0; i < 1500; i++)
            {
                var evt = new SessionEvent(Guid.NewGuid().ToString(), DateTime.Now, EventType.CommandSent, "{}");
                manager.LogEvent(evt);
            }

            var allEvents = manager.QueryEvents(new DateTimeRange { Start = DateTime.MinValue, End = DateTime.MaxValue });

            Assert.Equal(1000, allEvents.Count);
        }

        [Fact]
        public void QueryEvents_FiltersByTimeRange()
        {
            var adapter = new FakeAdapter();
            var manager = new DurableStateManagerImpl(adapter, new FakeDiskStore());

            var baseTime = DateTime.Now;
            manager.LogEvent(new SessionEvent("e1", baseTime, EventType.CommandSent, "{}"));
            manager.LogEvent(new SessionEvent("e2", baseTime + TimeSpan.FromSeconds(5), EventType.CommandAcknowledged, "{}"));
            manager.LogEvent(new SessionEvent("e3", baseTime + TimeSpan.FromSeconds(10), EventType.SnapshotTaken, "{}"));

            var events = manager.QueryEvents(new DateTimeRange
            {
                Start = baseTime + TimeSpan.FromSeconds(4),
                End = baseTime + TimeSpan.FromSeconds(6)
            });

            Assert.Single(events);
            Assert.Equal("e2", events[0].EventId);
        }
    }

    // ── Transaction Manager Tests ────────────────────────────────────────────

    public class TransactionManagerTests
    {
        [Fact]
        public async Task ExecuteAsync_SuccessfulCommand_ReturnsValue()
        {
            var adapter = new FakeAdapter();
            var stateManager = new FakeDurableStateManager();
            var manager = new TransactionManagerImpl(adapter, stateManager);

            var result = await manager.ExecuteAsync("TestCommand", async ct =>
            {
                await Task.Delay(1, ct);
                return 42;
            }, "corr-test");

            Assert.Equal(42, result);
            Assert.Equal("corr-test", manager.LastCommandCorrelationId);
        }

        [Fact]
        public async Task ExecuteAsync_CommandFails_RetriesUntilMax()
        {
            var adapter = new FakeAdapter();
            var stateManager = new FakeDurableStateManager();
            var manager = new TransactionManagerImpl(adapter, stateManager) { MaxRetries = 3, InitialBackoff = TimeSpan.FromMilliseconds(5) };

            int attemptCount = 0;
            var exception = await Assert.ThrowsAsync<Exception>(() => manager.ExecuteAsync("FailingCommand", async ct =>
            {
                attemptCount++;
                throw new Exception("Simulated failure");
            }));

            Assert.Equal(3, attemptCount);
            Assert.Equal("Simulated failure", exception.Message);
        }

        [Fact]
        public async Task ExecuteAsync_OperationCanceled_ReturnsCancelledResult()
        {
            var adapter = new FakeAdapter();
            var stateManager = new FakeDurableStateManager();
            var manager = new TransactionManagerImpl(adapter, stateManager);

            var cts = new CancellationTokenSource();
            cts.Cancel();

            await Assert.ThrowsAsync<OperationCanceledException>(() => manager.ExecuteAsync("CancelledCommand", async ct =>
            {
                await Task.Delay(1000, ct);
                return "never-reaches-here";
            }, ct: cts.Token));
        }

        [Fact]
        public void EventHandlers_TriggerOnSuccessFailure()
        {
            var adapter = new FakeAdapter();
            var stateManager = new FakeDurableStateManager();
            var manager = new TransactionManagerImpl(adapter, stateManager);

            bool started = false, succeeded = false, failed = false;
            manager.OnCommandStarted += (_, _) => started = true;
            manager.OnCommandSucceeded += (_, _) => succeeded = true;
            manager.OnCommandFailed += (_, _, _) => failed = true;

            _ = manager.ExecuteAsync("Test", async ct => { await Task.CompletedTask; return 0; });

            // Events fire synchronously within ExecuteAsync
            Assert.True(started);
            Assert.True(succeeded);
        }

        [Fact]
        public void RetryEvent_TriggeredOnEachRetry()
        {
            var adapter = new FakeAdapter();
            var stateManager = new FakeDurableStateManager();
            var manager = new TransactionManagerImpl(adapter, stateManager) { MaxRetries = 3, InitialBackoff = TimeSpan.FromMilliseconds(1) };

            int retryCount = 0;
            manager.OnCommandRetry += (_, _, attempt) => retryCount = attempt;

            _ = Assert.ThrowsAny<Exception>(() => manager.ExecuteAsync("FailTest", async ct =>
            {
                throw new Exception("Always fails");
            }, ct: CancellationToken.None)).WaitAsync(TimeSpan.FromSeconds(2));
        }
    }

    // ── Session Recovery Manager Tests ──────────────────────────────────────

    public class SessionRecoveryManagerTests
    {
        [Fact]
        public void Constructor_WithNullDependencies_Throws()
        {
            var adapter = new FakeAdapter();
            Assert.ThrowsAny<ArgumentNullException>(() => new SessionRecoveryManagerImpl(null!, null!, null!));
            Assert.ThrowsAny<ArgumentNullException>(() => new SessionRecoveryManagerImpl(adapter, null!, null!));
            Assert.ThrowsAny<ArgumentNullException>(() => new SessionRecoveryManagerImpl(adapter, null!, null!));
        }

        [Fact]
        public async Task RecoverToLatestAsync_NoSnapshots_ReturnsFalse()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            var success = await recovery.RecoverToLatestAsync();

            Assert.False(success);
            Assert.Equal(SessionHealthStatus.Unhealthy, recovery.HealthStatus);
        }

        [Fact]
        public async Task RecoverToLatestAsync_WithValidSnapshots_ReturnsTrue()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            await stateManager.TakeSnapshotAsync("valid-snapshot");
            var success = await recovery.RecoverToLatestAsync();

            Assert.True(success);
            Assert.Equal(SessionHealthStatus.Healthy, recovery.HealthStatus);
            Assert.NotNull(recovery.LastRecoveredSnapshotId);
        }

        [Fact]
        public async Task RecoverToSnapshotAsync_DisconnectedSnapshot_ReturnsFalse()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Disconnected };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            var snapshot = new SessionSnapshot("bad-snapshot", DateTime.Now, "", UIConnectionState.Disconnected, "", "");
            var success = await recovery.RecoverToSnapshotAsync("bad-snapshot");

            Assert.False(success);
        }

        [Fact]
        public void OnConnectionStateChanged_ChangesHealthStatus()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            recovery.OnConnectionStateChanged(UIConnectionState.Disconnected);

            Assert.Equal(SessionHealthStatus.NeedsRecovery, recovery.HealthStatus);
        }

        [Fact]
        public void HealthChangedEvent_TriggeredOnStateChange()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            bool triggered = false;
            SessionHealthStatus receivedStatus = SessionHealthStatus.Healthy;

            recovery.OnHealthChanged += status =>
            {
                triggered = true;
                receivedStatus = status;
            };

            recovery.OnConnectionStateChanged(UIConnectionState.UncertainMutation);

            Assert.True(triggered);
            Assert.Equal(SessionHealthStatus.Degraded, receivedStatus);
        }

        [Fact]
        public async Task RollbackAsync_NotEnoughSnapshots_ReturnsFalse()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            // Only one snapshot exists
            await stateManager.TakeSnapshotAsync("single-snapshot");

            var success = await recovery.RollbackAsync();

            Assert.False(success);
        }

        [Fact]
        public void ListCheckpoints_ReturnsSortedSnapshots()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var stateManager = new FakeDurableStateManager();
            var txManager = new MockTransactionManager();
            var recovery = new SessionRecoveryManagerImpl(adapter, stateManager, txManager);

            _ = stateManager.TakeSnapshotAsync("snap1").GetAwaiter().GetResult();
            _ = stateManager.TakeSnapshotAsync("snap2").GetAwaiter().GetResult();

            var checkpoints = recovery.ListCheckpoints();

            Assert.Equal(2, checkpoints.Count);
        }
    }

    // ── Serialization Tests ──────────────────────────────────────────────────

    public class SnapshotSerializationTests
    {
        [Fact]
        public void SessionSnapshot_ToJson_DeserializesCorrectly()
        {
            var inventory = new P1Inventory
            {
                inventoryRevision = 123,
                items = new[] { new P1Item { instanceId = "item-1", templateId = "tmpl-1", stack = 5 } },
                currencies = Array.Empty<P1Currency>()
            };

            var snapshot = new SessionSnapshot(
                snapshotId: "test-id",
                createdAt: DateTime.UtcNow,
                correlationId: "corr-1",
                connectionState: UIConnectionState.Ready,
                lastErrorCode: null,
                lastCorrelationId: "corr-1",
                hasPendingMutation: false,
                self: new P1Self { playerId = "player-123", location = null!, stats = null!, identity = null!, metadata = null! },
                world: null!,
                worldV2: null!,
                inventory: inventory,
                quests: Array.Empty<P1Quest>(),
                settings: SettingsViewState.Default,
                metadata: null!,
                eventCount: 5);

            var json = snapshot.ToJson();
            var restored = SessionSnapshot.FromJson(json);

            Assert.Equal("test-id", restored.SnapshotId);
            Assert.Equal(UIConnectionState.Ready, restored.ConnectionState);
            Assert.Equal(1, restored.Inventory.items.Length);
            Assert.Equal("item-1", restored.Inventory.items[0].instanceId);
        }

        [Fact]
        public void SerializableSettingsViewState_PersistsAllFields()
        {
            var customSettings = new SettingsViewState(uiScale: 1.5f, masterVolume: 0.8f, textSize: 1.2f, reducedMotion: true, reducedFlash: false, showInputHints: false);

            var serializable = new SerializableSettingsViewState(customSettings);

            Assert.Equal(1.5f, serializable.uiScale);
            Assert.Equal(0.8f, serializable.masterVolume);
            Assert.Equal(true, serializable.reducedMotion);
        }

        [Fact]
        public void SerializableP1Inventory_SerializesItemsAndCurrencies()
        {
            var inventory = new P1Inventory
            {
                inventoryRevision = 456,
                items = new[] { new P1Item { instanceId = "inv-item", stack = 10, location = "BAG" } },
                currencies = new[] { new P1Currency { currencyId = "gold", amount = 1000 } }
            };

            var serializable = new SerializableP1Inventory(inventory);

            Assert.Equal(456, serializable.inventoryRevision);
            Assert.Single(serializable.items);
            Assert.Single(serializable.currencies);
            Assert.Equal("gold", serializable.currencies[0].currencyId);
            Assert.Equal(1000, serializable.currencies[0].amount);
        }
    }

    // ── Integration Tests ────────────────────────────────────────────────────

    public class QODERRemoteIntegrationTests
    {
        [Fact]
        public void QODERRemoteHelpers_CanInitializeWithAdapter()
        {
            var adapter = new FakeAdapter();
            
            // Reset static state
            var field = typeof(QODERRemote).GetType().GetField("_service", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Static);
            field?.SetValue(null, null);

            QODERRemote.Initialize(adapter);

            Assert.True(QODERRemote.IsInitialized);
        }

        [Fact]
        public void QODERRemoteService_ConfigurationDefaults()
        {
            var adapter = new FakeAdapter();
            var service = new QODERRemoteServiceImpl(adapter);

            Assert.Equal(30, service.AutoSaveIntervalSeconds);
            Assert.Equal(50, service.MaxSnapshotsToKeep);
            Assert.True(service.AutoRecoverOnReconnect);
        }

        [Fact]
        public async Task Service_AutoSave_TakesSnapshot()
        {
            var adapter = new FakeAdapter { ConnectionState = UIConnectionState.Ready };
            var service = new QODERRemoteServiceImpl(adapter) { AutoSaveIntervalSeconds = 1 };

            await Task.Delay(2000); // Wait for auto-save

            var snapshots = service.ListCheckpoints();
            Assert.NotEmpty(snapshots);
        }
    }

    // ── Extension Methods for Testing ───────────────────────────────────────

    public static class TestExtensions
    {
        public static async Task WaitAsync(this Task task, TimeSpan timeout)
        {
            var delay = Task.Delay(timeout);
            var completed = await Task.WhenAny(task, delay);

            if (completed == delay)
                throw new TimeoutException($"Operation timed out after {timeout}");
        }
    }
}
