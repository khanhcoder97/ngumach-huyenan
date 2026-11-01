// QR-01 — Adapter connecting QODER Remote persistence to existing P1Client infrastructure.
// Provides seamless integration between new transactional layer and current gameplay code.
// Owner: QODER Remote Persistence — Issue #79 (Work Order 11).

using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Extensions.Configuration;
using NguMach.Client.Presentation;
using NguMach.Server.Atomic;
using NguMach.Server.Core;
using NguMach.Server.Persistence;
using NguMach.Server.Recovery;

namespace NguMach.Integration
{
    /// <summary>
    /// Exposes persistent transaction functionality through existing client interfaces.
    /// </summary>
    public interface IP1ClientPersistence : IP1UIAdapter
    {
        /// <summary>P1Client with persistent backend.</summary>
        Task<PersistentActionResult> ExecutePersistentAsync(string commandId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct);
        
        /// <summary>Recover session state after disconnection.</summary>
        Task<RecoveryStatus> RecoverSessionAsync(CancellationToken ct);
        
        /// <summary>Create checkpoint for save/load support.</summary>
        Task<string> CreateCheckpointAsync(CancellationToken ct);
        
        /// <summary>Restore from saved checkpoint.</summary>
        Task<bool> RestoreFromCheckpointAsync(string checkpointId, CancellationToken ct);
    }

    /// <summary>Action execution result with persistence context.</summary>
    public sealed class PersistentActionResult
    {
        public bool Succeeded { get; }
        public string? ReceiptId { get; }
        public string? Error { get; }
        public bool WasRecovered { get; }
        public CheckpointInfo? LastCheckpoint { get; }

        public PersistentActionResult(bool succeeded, string? receiptId, string? error, bool wasRecovered, CheckpointInfo? lastCheckpoint)
        {
            Succeeded = succeeded; ReceiptId = receiptId; Error = error; WasRecovered = wasRecovered; LastCheckpoint = lastCheckpoint;
        }

        public static PersistentActionResult Success(string receiptId, CheckpointInfo? checkpoint = null) =>
            new(true, receiptId, null, false, checkpoint);

        public static PersistentActionResult Failure(string error, CheckpointInfo? checkpoint = null) =>
            new(false, null, error, false, checkpoint);
    }

    /// <summary>Checkpoint metadata.</summary>
    public sealed class CheckpointInfo
    {
        public string Id { get; set; } = "";
        public DateTime CreatedAt { get; set; }
        public string PlayerId { get; set; } = "";
        public long CommittedRevision { get; set; }
        public int UncommittedTransactions { get; set; }
    }

    /// <summary>Recovery status after reconnect.</summary>
    public sealed class RecoveryStatus
    {
        public bool HasPendingRecovery { get; }
        public int UncommittedCount { get; }
        public string? LastCommittedTransactionId { get; }
        public Exception? Error { get; }
        public bool Success => HasPendingRecovery || Error == null;
    }

    /// <summary>Integrates P1Client with Server Persistence layer.</summary>
    internal sealed class P1ClientPersistenceAdapter : IP1ClientPersistence
    {
        private readonly P1Client _client;
        private readonly IDatabaseRepository _db;
        private readonly ITransactionManager _txMgr;
        private readonly IAtomicMutationCoordinator _coord;
        private readonly ICrashRecoveryManager _recovery;
        private readonly IFeatureGate _featureGate;
        private readonly Dictionary<string, CheckpointInfo> _checkpoints = new();
        private volatile bool _isRecovering;

        public UIConnectionState ConnectionState => _client.State.ToUIState();
        public bool HasPendingMutation => _client.HasPendingMutation;
        public string LastErrorCode => _client.LastError;
        public string LastCorrelationId => _client.LastCorrelationId;
        public P1Self Self => _client.World?.self ?? _client.WorldV2?.self;
        public P1World World => _client.UseWorldV2 ? null : _client.World;
        public P1WorldV2 WorldV2 => _client.UseWorldV2 ? _client.WorldV2 : null;
        public P1Quest[] Quests => _client.Quests;
        public P1Inventory Inventory => _client.Inventory;

        public P1ClientPersistenceAdapter(P1Client client, IConfiguration? config = null)
        {
            _client = client ?? throw new ArgumentNullException(nameof(client));

            // Initialize persistence components
            var dbPath = GetDatabasePath(config);
            var db = new SqliteDatabaseRepository(dbPath);
            var txMgr = new TransactionManagerImpl(db);
            var coord = new AtomicMutationCoordinatorImpl(db, txMgr);
            var recovery = new CrasRecoveryManagerImpl(db, dbPath);
            var featureGate = FeatureGateExtensions.CreateDefaultFeatureGate();

            _db = db;
            _txMgr = txMgr;
            _coord = coord;
            _recovery = recovery;
            _featureGate = featureGate;
        }

        public async Task<PersistentActionResult> ExecutePersistentAsync(string commandId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct)
        {
            if (!_featureGate.IsEnabled)
                return await ExecuteWithoutPersistence(commandId, action, ct);

            try
            {
                var result = await _coord.ExecuteMutationAsync(
                    commandId, 
                    Self?.playerId ?? "unknown", 
                    1, 
                    null!, // Would serialize payload here
                    ct);

                if (!result.Succeeded)
                    return PersistentActionResult.Failure(result.Error!);

                var lastCkpt = GetCurrentCheckpointInfo();
                return PersistentActionResult.Success(result.ReceiptId!, lastCkpt);
            }
            catch (Exception ex)
            {
                return PersistentActionResult.Failure(ex.Message, GetCurrentCheckpointInfo());
            }
        }

        public async Task<RecoveryStatus> RecoverSessionAsync(CancellationToken ct)
        {
            if (_isRecovering)
                return new RecoveryStatus { HasPendingRecovery = false };

            _isRecovering = true;
            try
            {
                var recoveryResult = await _recovery.RecoverAfterCrashAsync(ct);

                if (!recoveryResult.Success)
                    return new RecoveryStatus { Error = new Exception(recoveryResult.Error), HasPendingRecovery = false };

                var uncommitted = await _db.GetUncommittedTransactionsAsync(Self?.playerId ?? "");
                return new RecoveryStatus
                {
                    HasPendingRecovery = uncommitted.Count > 0,
                    UncommittedCount = uncommitted.Count,
                    LastCommittedTransactionId = recoveryResult.LastCommittedTransactionId
                };
            }
            finally
            {
                _isRecovering = false;
            }
        }

        public async Task<string> CreateCheckpointAsync(CancellationToken ct)
        {
            var id = Guid.NewGuid().ToString("N");
            var info = new CheckpointInfo
            {
                Id = id,
                CreatedAt = DateTime.UtcNow,
                PlayerId = Self?.playerId ?? "",
                CommittedRevision = DateTimeOffset.UtcNow.ToUnixTimeSeconds()
            };

            info.UncommittedTransactions = (await _db.GetUncommittedTransactionsAsync(info.PlayerId)).Count;
            
            _checkpoints[id] = info;

            await _recovery.CheckpointWALAsync();
            await _recovery.CreateBackupAsync(Path.Combine(GetCheckpointPath(), $"{id}.sqlite"), ct);

            return id;
        }

        public async Task<bool> RestoreFromCheckpointAsync(string checkpointId, CancellationToken ct)
        {
            if (!_checkpoints.TryGetValue(checkpointId, out var info))
                return false;

            var backupPath = Path.Combine(GetCheckpointPath(), $"{checkpointId}.sqlite");
            if (!System.IO.File.Exists(backupPath))
                return false;

            var restoreResult = await _recovery.RestoreFromBackupAsync(backupPath, ct);
            return restoreResult.Success;
        }

        private CheckpointInfo? GetCurrentCheckpointInfo()
        {
            var checkpoints = _checkpoints.Values.OrderBy(c => c.CreatedAt).ToList();
            return checkpoints.Count > 0 ? checkpoints[^1] : null;
        }

        private async Task<PersistentActionResult> ExecuteWithoutPersistence(string commandId, Func<CancellationToken, Task<CommandExecution>> action, CancellationToken ct)
        {
            // Fallback to direct client execution without persistence
            var result = await action(ct);
            return result.Succeeded 
                ? PersistentActionResult.Success(null) 
                : PersistentActionResult.Failure(result.Error ?? "Unknown failure");
        }

        private string GetDatabasePath(IConfiguration? config)
        {
            var envVar = Environment.GetEnvironmentVariable("QODER_DB_PATH");
            if (!string.IsNullOrEmpty(envVar) && !string.IsNullOrEmpty(config?.GetValue<string>("qoderm_remote_db_path")))
                envVar = config["qoderm_remote_db_path"];

            return envVar ?? Path.Combine(System.IO.Path.GetTempPath(), "ngumach_persistence.sqlite");
        }

        private string GetCheckpointPath() => Path.Combine(System.IO.Path.GetTempPath(), "ngumach_checkpoints");

        // Delegate remaining IP1UIAdapter methods to underlying client
        public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => _client.ReadQuestsAsync(ct);
        public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => _client.ReadInventoryAsync(ct);
        public Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct) => _client.AcceptQuestAsync(questId, npcId, ct);
        public Task<P1Result> InteractAsync(string targetId, CancellationToken ct) => _client.InteractAsync(targetId, ct);
        public Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct) => _client.TurnInQuestAsync(questId, npcId, ct);
        public Task<P1Result> RetryPendingAsync(CancellationToken ct) => _client.RetryPendingAsync(ct);
    }

    // Helper extension methods
    internal static class StateExtensions
    {
        public static UIConnectionState ToUIState(this P1ConnectionState state)
        {
            return state switch
            {
                P1ConnectionState.Disconnected => UIConnectionState.Disconnected,
                P1ConnectionState.Connecting => UIConnectionState.Connecting,
                P1ConnectionState.Ready => UIConnectionState.Ready,
                P1ConnectionState.NeedsResync => UIConnectionState.NeedsResync,
                P1ConnectionState.UncertainMutation => UIConnectionState.UncertainMutation,
                P1ConnectionState.Expired => UIConnectionState.Expired,
                _ => UIConnectionState.Error
            };
        }
    }
}
