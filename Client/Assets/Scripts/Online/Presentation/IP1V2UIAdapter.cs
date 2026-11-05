// OPC-16 O4 — v2 adapter surfaces used by the portable presenters.
// Kept separate from IP1UIAdapter so existing v1 fake adapters stay source-compatible.
// Owner: OpenCode.

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
        Task<P1Result> TalkAsync(string npcId, string nodeId, CancellationToken ct);
        Task<P1Result> PortalAsync(string portalId, CancellationToken ct);
        Task<P1Result> MapViewedAsync(string questId, CancellationToken ct);
    }
}
