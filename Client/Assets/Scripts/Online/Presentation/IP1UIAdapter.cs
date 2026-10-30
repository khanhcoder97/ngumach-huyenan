// AG1 — Adapter interface: wraps P1Client read-only surface for UI.
// UI code only calls this interface; never touches P1Client directly.
// Implementations must NOT create competing HTTP clients or gameplay state.
// Owner: Antigravity Remote — Issue #80.

using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    /// <summary>
    /// Read-only projection of P1Client state for UI consumption.
    /// Mutations go through command methods; results are server-authoritative.
    /// </summary>
    public interface IP1UIAdapter
    {
        // ── State ──────────────────────────────────────────────────────────
        UIConnectionState ConnectionState { get; }
        bool HasPendingMutation { get; }
        string LastErrorCode { get; }
        string LastCorrelationId { get; }

        // ── World / self ───────────────────────────────────────────────────
        P1Self Self { get; }          // null when not connected
        P1World World { get; }        // v1; null when not connected or v2 active
        P1WorldV2 WorldV2 { get; }    // v2; null when v1 or not connected

        // ── Reads (do not mutate) ──────────────────────────────────────────
        P1Quest[] Quests { get; }
        P1Inventory Inventory { get; }

        // ── Commands ───────────────────────────────────────────────────────
        /// <summary>Read server quests into Quests property.</summary>
        Task<P1Result> ReadQuestsAsync(CancellationToken ct);

        /// <summary>Read server inventory into Inventory property.</summary>
        Task<P1Result> ReadInventoryAsync(CancellationToken ct);

        /// <summary>Accept a quest from an NPC. Idempotent via core.</summary>
        Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct);

        /// <summary>Interact with an entity (NPC, gather node, etc.).</summary>
        Task<P1Result> InteractAsync(string targetId, CancellationToken ct);

        /// <summary>Turn in a ready quest to an NPC.</summary>
        Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct);

        /// <summary>Retry the pending uncertain command without sending a new one.</summary>
        Task<P1Result> RetryPendingAsync(CancellationToken ct);
    }
}
