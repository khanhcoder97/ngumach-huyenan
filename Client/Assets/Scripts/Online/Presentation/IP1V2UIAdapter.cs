// OPC-16 O4 — v2 adapter surfaces used by the portable presenters.
// Kept separate from IP1UIAdapter so existing v1 fake adapters stay source-compatible.
// Owner: OpenCode.

using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public interface IP1InventoryV2Adapter
    {
        P1InventorySnapshotV2 InventoryV2 { get; }
        bool HasPendingMutation { get; }
        string LastErrorCode { get; }
        Task<P1Result> ReadInventoryV2Async(CancellationToken ct);
        Task<P1Result> EquipV2Async(string itemInstanceId, long expectedRevision, CancellationToken ct);
        Task<P1Result> UnequipV2Async(string slotId, long expectedRevision, CancellationToken ct);
    }

    public interface IP1DeathReturnAdapter
    {
        UIConnectionState ConnectionState { get; }
        bool HasPendingMutation { get; }
        P1Self Self { get; }
        P1DeathReturnResultV1 LastDeathReturn { get; }
        long? NextReturnAllowedAtTick { get; }
        Task<P1Result> ReturnFromDeathAsync(CancellationToken ct);
    }

    public interface IP1TalkAdapter
    {
        UIConnectionState ConnectionState { get; }
        bool HasPendingMutation { get; }
        string LastErrorCode { get; }
        P1QuestTalkResult LastTalk { get; }
        P1WorldPortalResult LastPortal { get; }
        P1QuestMapViewedResult LastMapViewed { get; }
        Task<P1Result> TalkAsync(string npcId, string nodeId, CancellationToken ct);
        Task<P1Result> PortalAsync(string portalId, CancellationToken ct);
        Task<P1Result> MapViewedAsync(string questId, CancellationToken ct);
    }

    // OPC-16 O4 — combat HUD read surface. Kept separate from IP1UIAdapter so
    // existing fake adapters keep compiling. Cooldowns are the server-issued
    // UTC deadlines; the presenter never commits a local cooldown.
    public interface IP1CombatHudAdapter
    {
        UIConnectionState ConnectionState { get; }
        P1Self Self { get; }
        P1World World { get; }
        P1WorldV2 WorldV2 { get; }
        bool UseWorldV2 { get; }
        IReadOnlyDictionary<string, string> CooldownEndsAtUtc { get; }
        bool HasPendingMutation { get; }
        string LastErrorCode { get; }
        Task<P1Result> BasicAttackAsync(string targetId, double aimX, double aimY, CancellationToken ct);
        Task<P1Result> CastAsync(string skillId, string targetId, double aimX, double aimY, CancellationToken ct);
    }
}
