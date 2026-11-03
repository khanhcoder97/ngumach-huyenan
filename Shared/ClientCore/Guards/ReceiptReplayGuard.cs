// OPC-15 O-B — Receipt replay evaluator for mutations (turn-in etc.).
// Same payload + same key => replay success with the stored receipt.
// Different payload or different key => conflict (no grant). No optimistic grant.
// Pure C#.

using System;

namespace NguMach.Client.Core.Guards
{
    public sealed class MutationReceipt
    {
        public string Key { get; set; }          // idempotency key
        public string PayloadHash { get; set; }  // hash of the canonical payload
        public string QuestState { get; set; }   // e.g. COMPLETED
        public int CoinGranted { get; set; }
        public int ChestGranted { get; set; }
        public bool Applied { get; set; }        // true once the server committed
    }

    public enum ReplayVerdict { ReplaySuccess, Conflict, NotApplied }

    public static class ReceiptReplayGuard
    {
        public static ReplayVerdict Evaluate(MutationReceipt stored, string incomingKey, string incomingPayloadHash)
        {
            if (stored == null || !stored.Applied) return ReplayVerdict.NotApplied;
            if (!string.Equals(stored.Key, incomingKey, StringComparison.Ordinal)) return ReplayVerdict.Conflict;
            if (!string.Equals(stored.PayloadHash, incomingPayloadHash, StringComparison.Ordinal)) return ReplayVerdict.Conflict;
            return ReplayVerdict.ReplaySuccess;
        }
    }
}
