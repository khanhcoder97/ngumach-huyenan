// OPC-15 O3/O5 (WO26) — Renderer-neutral view model derived from an EncounterSnapshot.
// Apply() reports transitions without advancing LastCastId; the consumer calls
// CommitCast() only after the new-cast VFX has actually been started. This prevents
// a poll between Apply and Commit from losing the new cast. Stale life/revision
// snapshots are rejected and never overwrite newer state. All countdown timing uses
// serverTick + stateEndsAtTick, never the local clock or animation callbacks.
// State is an immutable projection safe to hand to the Godot main thread.
// Pure C#. Owner: OpenCode.

using System;

namespace NguMach.Client.Core.Encounter
{
    public sealed class EncounterUpdate
    {
        public bool Accepted { get; set; }
        public string RejectReason { get; set; }
        public bool IsNewEncounter { get; set; }
        public bool IsNewLife { get; set; }
        public bool IsNewCast { get; set; }
        public bool StateChanged { get; set; }
        public bool PhaseChanged { get; set; }
        public bool IsTerminal { get; set; }
        public bool IsCleared { get; set; }
        public string CastId { get; set; }
    }

    public sealed class EncounterView
    {
        public EncounterSnapshot Snapshot { get; private set; }
        public EncounterState State { get; private set; }
        public string LastCastId { get; private set; }
        public string PendingCastId { get; private set; }
        public long LastLifeGeneration { get; private set; }
        public BossPhase? LastPhase { get; private set; }
        public MoveState? LastState { get; private set; }
        public EncounterStatus? LastStatus { get; private set; }

        public bool HasSnapshot => Snapshot != null;

        // Returns false for a stale life/revision snapshot. The view is left untouched.
        public bool TryApply(EncounterSnapshot snapshot, out EncounterUpdate update)
        {
            if (snapshot == null) throw new ArgumentNullException(nameof(snapshot));
            update = new EncounterUpdate { Accepted = false };

            string reject = null;
            if (Snapshot != null && string.Equals(snapshot.EncounterId, Snapshot.EncounterId, StringComparison.Ordinal))
            {
                if (snapshot.BossLifeId < Snapshot.BossLifeId)
                    reject = "stale life: " + snapshot.BossLifeId + " < " + Snapshot.BossLifeId;
                else if (snapshot.BossLifeId == Snapshot.BossLifeId && snapshot.BossRevision < Snapshot.BossRevision)
                    reject = "stale revision: " + snapshot.BossRevision + " < " + Snapshot.BossRevision;
            }
            if (reject != null)
            {
                update.RejectReason = reject;
                return false;
            }

            update.Accepted = true;

            var oldSnapshot = Snapshot;
            bool newEncounter = oldSnapshot == null ||
                !string.Equals(snapshot.EncounterId, oldSnapshot.EncounterId, StringComparison.Ordinal);
            bool newLife = oldSnapshot != null && snapshot.BossLifeId != oldSnapshot.BossLifeId;
            update.IsNewEncounter = newEncounter;
            update.IsNewLife = newLife;

            if (newEncounter || newLife)
            {
                // A new encounter/life has no committed cast from the previous generation.
                LastCastId = null;
                PendingCastId = null;
                LastState = null;
                LastPhase = null;
                LastStatus = null;
            }

            var oldMove = oldSnapshot == null ? null : oldSnapshot.ActiveMove;
            var newMove = snapshot.ActiveMove;
            var oldState = oldMove == null ? (MoveState?)null : oldMove.State;
            var newState = newMove == null ? (MoveState?)null : newMove.State;
            update.StateChanged = !Nullable.Equals(oldState, newState);
            if (oldSnapshot == null && newState.HasValue) update.StateChanged = true;

            update.PhaseChanged = !LastPhase.HasValue || LastPhase.Value != snapshot.Phase;

            string incomingCast = newMove == null ? null : newMove.CastId;
            if (newEncounter || newLife)
            {
                if (!string.IsNullOrEmpty(incomingCast))
                {
                    update.IsNewCast = true;
                    PendingCastId = incomingCast;
                }
            }
            else if (!string.IsNullOrEmpty(incomingCast))
            {
                if (string.Equals(incomingCast, PendingCastId, StringComparison.Ordinal))
                {
                    // Same cast polled again before the consumer committed it: keep pending.
                    update.IsNewCast = false;
                }
                else if (!string.Equals(incomingCast, LastCastId, StringComparison.Ordinal))
                {
                    update.IsNewCast = true;
                    PendingCastId = incomingCast;
                }
                else
                {
                    PendingCastId = null;
                }
            }
            else
            {
                // No active move: nothing may remain pending.
                PendingCastId = null;
            }
            update.CastId = incomingCast;

            update.IsTerminal = snapshot.Status == EncounterStatus.Defeated || snapshot.Status == EncounterStatus.Reset;
            if (update.IsTerminal)
            {
                PendingCastId = null;
                update.IsNewCast = false;
            }

            Snapshot = snapshot;
            State = new EncounterState(snapshot);
            LastLifeGeneration = snapshot.BossLifeId;
            LastPhase = snapshot.Phase;
            LastState = newState;
            LastStatus = snapshot.Status;
            return true;
        }

        public EncounterUpdate Apply(EncounterSnapshot snapshot)
        {
            EncounterUpdate update;
            TryApply(snapshot, out update);
            return update;
        }

        // Consumer calls after handling VFX for the pending cast.
        public void CommitCast()
        {
            if (!string.IsNullOrEmpty(PendingCastId))
            {
                LastCastId = PendingCastId;
                PendingCastId = null;
            }
        }

        public void CancelPendingVfx()
        {
            PendingCastId = null;
        }

        public bool IsTelegraphActive
        {
            get { return Snapshot != null && Snapshot.ActiveMove != null && Snapshot.ActiveMove.State == MoveState.Telegraph; }
        }

        public bool IsImpactActive
        {
            get { return Snapshot != null && Snapshot.ActiveMove != null && Snapshot.ActiveMove.State == MoveState.Impact; }
        }

        public long RemainingTicks(long currentServerTick)
        {
            if (Snapshot == null || Snapshot.ActiveMove == null) return 0;
            long remaining = Snapshot.ActiveMove.StateEndsAtTick - currentServerTick;
            return remaining < 0 ? 0 : remaining;
        }

        // Uses the snapshot's own server tick; never DateTime/engine time.
        public long RemainingTicks()
        {
            return Snapshot == null ? 0 : RemainingTicks(Snapshot.ServerTick);
        }

        public bool IsNewCast(string castId)
        {
            if (string.IsNullOrEmpty(castId)) return false;
            return !string.Equals(castId, LastCastId, StringComparison.Ordinal);
        }

        public void Reset()
        {
            Snapshot = null;
            State = null;
            LastCastId = null;
            PendingCastId = null;
            LastLifeGeneration = 0;
            LastPhase = null;
            LastState = null;
            LastStatus = null;
        }
    }
}
