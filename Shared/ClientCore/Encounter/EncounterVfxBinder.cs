// OPC-16 O6 — renderer-neutral encounter VFX binding.
// A payload is copied from the authoritative snapshot at the moment a new cast is
// accepted, including the cast id, shape and server-tick deadline. The binder emits
// at most one payload per cast and only marks it committed after the consumer has
// actually started the VFX. Repeated polls/apply calls cannot duplicate an effect.
// Pure C#, no engine dependency. Owner: OpenCode.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Core.Encounter
{
    // O6 — clean-up reasons the host must route into the binder. Cast-local
    // cancellation keeps committed history so the same cast cannot replay;
    // life/encounter/transport changes start a fresh visual scene.
    public enum EncounterVfxLifecycleChange
    {
        CastCanceled,
        CastRejected,
        BossDeath,
        PlayerDeath,
        Logout,
        MapChanged,
        EncounterEnded
    }

    public sealed class EncounterVfxPayload
    {
        public string EncounterId { get; }
        public string CastId { get; }
        public string MoveId { get; }
        public string TargetLock { get; }
        public long BossLifeId { get; }
        public long BossRevision { get; }
        public long ServerTick { get; }
        public long StateEndsAtTick { get; }
        public long TicksRemaining { get; }
        public BossPhase Phase { get; }
        public MoveState State { get; }
        public EncounterShapeState Shape { get; }
        // Captured from the host accessibility setting at bind time. The binder
        // still emits exactly once; the engine chooses the reduced variant.
        public bool ReducedMotion { get; }

        internal EncounterVfxPayload(EncounterSnapshot snapshot, ActiveMove move, bool reducedMotion)
        {
            EncounterId = snapshot.EncounterId;
            CastId = move.CastId;
            MoveId = move.MoveId;
            TargetLock = move.TargetLock;
            BossLifeId = snapshot.BossLifeId;
            BossRevision = snapshot.BossRevision;
            ServerTick = snapshot.ServerTick;
            StateEndsAtTick = move.StateEndsAtTick;
            TicksRemaining = move.TicksRemaining;
            Phase = snapshot.Phase;
            State = move.State;
            ReducedMotion = reducedMotion;
            // EncounterShapeState copies every primitive; no mutable wire DTO escapes.
            Shape = move.Shape == null ? null : new EncounterShapeState(move.Shape);
        }

        public bool IsTelegraph => State == MoveState.Telegraph;
        public bool IsRecovery => State == MoveState.Recovery;

        // Server-owned deadline; callers must not derive this from a local clock.
        public long RemainingTicksAt(long serverTick)
        {
            long remaining = StateEndsAtTick - serverTick;
            return remaining < 0 ? 0 : remaining;
        }

        public bool IsExpiredAt(long serverTick)
        {
            return serverTick >= StateEndsAtTick;
        }
    }

    public sealed class EncounterVfxBinder
    {
        private readonly HashSet<string> _committed = new HashSet<string>(StringComparer.Ordinal);
        private EncounterVfxPayload _pending;

        public EncounterVfxPayload Pending { get { return _pending; } }
        public string PendingCastId { get { return _pending == null ? null : _pending.CastId; } }

        // Accessibility preference copied into each new payload.
        public bool ReducedMotion { get; set; }

        // Binds only an accepted new-cast transition whose snapshot still carries the
        // same cast. A rejected/stale update or a cast mismatch binds nothing.
        public bool TryBind(EncounterUpdate update, EncounterSnapshot snapshot, out EncounterVfxPayload payload)
        {
            payload = null;
            if (update == null || snapshot == null) return false;
            if (!update.Accepted || !update.IsNewCast) return false;
            if (string.IsNullOrEmpty(update.CastId)) return false;
            if (!string.Equals(update.CastId, snapshot.ActiveMove == null ? null : snapshot.ActiveMove.CastId,
                    StringComparison.Ordinal))
                return false;
            return TryBindCore(snapshot, out payload);
        }

        // Snapshot-only convenience for hosts that already track new casts themselves.
        // Still exactly once per cast id; the caller must Commit after starting VFX.
        public bool TryBind(EncounterSnapshot snapshot, out EncounterVfxPayload payload)
        {
            return TryBindCore(snapshot, out payload);
        }

        private bool TryBindCore(EncounterSnapshot snapshot, out EncounterVfxPayload payload)
        {
            payload = null;
            if (snapshot == null || snapshot.ActiveMove == null || snapshot.ActiveMove.Shape == null) return false;
            if (!string.Equals(snapshot.StatusRaw, "OPEN", StringComparison.OrdinalIgnoreCase)) return false;

            var move = snapshot.ActiveMove;
            if (string.IsNullOrEmpty(move.CastId)) return false;
            if (_committed.Contains(move.CastId)) return false;

            // The payload is already past its server deadline: a late poll must not
            // start a telegraph/impact that the players could no longer react to.
            if (move.StateEndsAtTick <= 0 || snapshot.ServerTick >= move.StateEndsAtTick) return false;

            // A payload already handed to the consumer is pending until Commit/Cancel.
            // A different incoming cast supersedes it (the newer server state is
            // authoritative). The superseded cast is still marked seen: a later poll
            // must never replay an effect the consumer may already have started.
            if (_pending != null)
            {
                if (string.Equals(_pending.CastId, move.CastId, StringComparison.Ordinal))
                    return false;
                _committed.Add(_pending.CastId);
                _pending = null;
            }

            payload = new EncounterVfxPayload(snapshot, move, ReducedMotion);
            _pending = payload;
            return true;
        }

        // Idempotent. Returns true only for the transition from pending to committed.
        public bool Commit()
        {
            if (_pending == null) return false;
            bool added = _committed.Add(_pending.CastId);
            _pending = null;
            return added;
        }

        // Drops the pending payload so the caller may retry if VFX start failed.
        // Already committed casts remain committed and can never replay.
        public void CancelPending()
        {
            _pending = null;
        }

        // Cancels only the matching pending cast (e.g. a rejected server cast).
        public bool CancelPending(string castId)
        {
            if (_pending == null || string.IsNullOrEmpty(castId) ||
                !string.Equals(_pending.CastId, castId, StringComparison.Ordinal)) return false;
            _pending = null;
            return true;
        }

        // Called from the host tick/event pump with the authoritative server tick.
        // An effect whose deadline passed before the engine started it is marked
        // seen and dropped, so a later poll cannot replay a late impact.
        public bool ExpirePending(long serverTick)
        {
            if (_pending == null || !_pending.IsExpiredAt(serverTick)) return false;
            _committed.Add(_pending.CastId);
            _pending = null;
            return true;
        }

        public bool IsCommitted(string castId)
        {
            return !string.IsNullOrEmpty(castId) && _committed.Contains(castId);
        }

        // New encounter/life/clear: forget both pending and committed history.
        public void Reset()
        {
            _pending = null;
            _committed.Clear();
        }

        // Lifecycle cleanup. A rejected/cancelled cast only drops that pending
        // payload; death/logout/map/encounter changes clear the whole visual scene.
        public void ClearForLifecycle(EncounterVfxLifecycleChange change)
        {
            if (change == EncounterVfxLifecycleChange.CastCanceled ||
                change == EncounterVfxLifecycleChange.CastRejected)
            {
                _pending = null;
                return;
            }
            _pending = null;
            _committed.Clear();
        }
    }
}
