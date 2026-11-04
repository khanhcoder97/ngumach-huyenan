// OPC-15 O2 (WO26) — Preserve an ambiguous mutation across relogin.
// The request body (requestId + idempotencyKey) never changes; only the session
// header is rebound after a fresh connect. Pure C#. Owner: OpenCode.

using System;

namespace NguMach.Client.P1
{
    public sealed class PendingMutationSnapshot
    {
        public P1Request Request { get; }
        public bool Combat { get; }
        public int Kind { get; }

        internal PendingMutationSnapshot(P1Request request, bool combat, int kind)
        {
            Request = request ?? throw new ArgumentNullException(nameof(request));
            Combat = combat;
            Kind = kind;
        }

        internal PendingMutationSnapshot Rebind(string sessionId)
        {
            return new PendingMutationSnapshot(Request.WithSession(sessionId), Combat, Kind);
        }
    }

    public sealed partial class P1Client
    {
        public PendingMutationSnapshot CapturePendingMutation()
        {
            if (pending == null) return null;
            return new PendingMutationSnapshot(pending, pendingCombat, (int)pendingKind);
        }

        public void RestorePendingMutation(PendingMutationSnapshot snapshot)
        {
            if (snapshot == null) return;
            if (string.IsNullOrEmpty(SessionId))
                throw new InvalidOperationException("Cannot restore a pending mutation without a session.");
            pending = snapshot.Request.WithSession(SessionId);
            pendingCombat = snapshot.Combat;
            pendingKind = (PendingKind)snapshot.Kind;
            State = P1ConnectionState.UncertainMutation;
        }
    }
}
