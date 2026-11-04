// OPC-15 O3 — Renderer-neutral view model derived from an EncounterSnapshot.
// Fix: Apply no longer overwrites LastCastId before the consumer can detect a
// new cast. Instead Apply returns an EncounterUpdate describing the transition,
// and the consumer calls CommitCast() after handling. Life/encounter/session
// change resets pending VFX. Countdown clamps at 0 using serverTick only.
// Pure C#. Owner: OpenCode.

using System;

namespace NguMach.Client.Core.Encounter
{
    public sealed class EncounterUpdate
    {
        public bool IsNewEncounter { get; set; }
        public bool IsNewLife { get; set; }
        public bool IsNewCast { get; set; }
        public bool StateChanged { get; set; }
        public bool PhaseChanged { get; set; }
        public bool IsTerminal { get; set; }
        public string CastId { get; set; }
    }

    public sealed class EncounterView
    {
        public EncounterSnapshot Snapshot { get; private set; }
        public string LastCastId { get; private set; }
        public string PendingCastId { get; private set; }
        public long LastLifeGeneration { get; private set; }
        public BossPhase? LastPhase { get; private set; }
        public MoveState? LastState { get; private set; }
        public EncounterStatus? LastStatus { get; private set; }

        public bool HasSnapshot => Snapshot != null;

        // Apply returns a transition descriptor; LastCastId is NOT advanced until
        // CommitCast() is called by the consumer after handling VFX.
        public EncounterUpdate Apply(EncounterSnapshot snapshot)
        {
            if (snapshot == null) throw new ArgumentNullException(nameof(snapshot));
            var update = new EncounterUpdate();
            if (Snapshot == null)
            {
                update.IsNewEncounter = true;
            }
            else
            {
                if (snapshot.BossLifeId != Snapshot.BossLifeId) update.IsNewLife = true;
                if (snapshot.EncounterId != Snapshot.EncounterId) update.IsNewEncounter = true;
                if (LastPhase.HasValue && LastPhase.Value != snapshot.Phase) update.PhaseChanged = true;
                if (LastState.HasValue && Snapshot.ActiveMove != null && snapshot.ActiveMove != null &&
                    LastState.Value != snapshot.ActiveMove.State) update.StateChanged = true;
            }

            // new cast detection (before advancing)
            string incomingCast = snapshot.ActiveMove != null ? snapshot.ActiveMove.CastId : null;
            if (!string.IsNullOrEmpty(incomingCast) && !string.Equals(incomingCast, LastCastId, StringComparison.Ordinal))
            {
                update.IsNewCast = true;
                PendingCastId = incomingCast;
            }
            else
            {
                PendingCastId = null;
            }
            update.CastId = incomingCast;

            // reset tracking on new life
            if (update.IsNewLife)
            {
                LastCastId = null;
                PendingCastId = incomingCast;
                if (!string.IsNullOrEmpty(incomingCast)) update.IsNewCast = true;
            }

            update.IsTerminal = snapshot.Status == EncounterStatus.Defeated || snapshot.Status == EncounterStatus.Reset;

            Snapshot = snapshot;
            LastLifeGeneration = snapshot.BossLifeId;
            LastPhase = snapshot.Phase;
            LastState = snapshot.ActiveMove != null ? snapshot.ActiveMove.State : (MoveState?)null;
            LastStatus = snapshot.Status;
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
            long r = Snapshot.ActiveMove.StateEndsAtTick - currentServerTick;
            return r < 0 ? 0 : r;
        }

        public bool IsNewCast(string castId)
        {
            if (string.IsNullOrEmpty(castId)) return false;
            return !string.Equals(castId, LastCastId, StringComparison.Ordinal);
        }

        public void Reset()
        {
            Snapshot = null;
            LastCastId = null;
            PendingCastId = null;
            LastLifeGeneration = 0;
            LastPhase = null;
            LastState = null;
            LastStatus = null;
        }
    }
}
