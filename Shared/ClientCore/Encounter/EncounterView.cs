// OPC-15 O-C — Renderer-neutral view model derived from an EncounterSnapshot.
// No animation playback, no damage decision, no engine calls. Tracks the last
// observed castId so a poll that returns the same cast does not replay VFX.
// Owner: OpenCode (portable core).

using System;

namespace NguMach.Client.Core.Encounter
{
    public sealed class EncounterView
    {
        public EncounterSnapshot Snapshot { get; private set; }
        public string LastCastId { get; private set; }
        public long LastLifeGeneration { get; private set; }

        public bool HasSnapshot => Snapshot != null;

        public void Apply(EncounterSnapshot snapshot)
        {
            if (snapshot == null) throw new ArgumentNullException(nameof(snapshot));
            // Life/generation change cancels pending VFX: reset tracking.
            if (Snapshot == null || snapshot.Generation != Snapshot.Generation ||
                snapshot.BossLifeId != Snapshot.BossLifeId)
            {
                LastCastId = null;
            }
            Snapshot = snapshot;
            if (snapshot.ActiveMove != null && !string.IsNullOrEmpty(snapshot.ActiveMove.CastId))
                LastCastId = snapshot.ActiveMove.CastId;
            LastLifeGeneration = snapshot.Generation;
        }

        public bool IsTelegraphActive
        {
            get
            {
                if (Snapshot == null || Snapshot.ActiveMove == null) return false;
                return Snapshot.PhaseEnum == EncounterPhase.Telegraph;
            }
        }

        public bool IsImpactActive
        {
            get
            {
                if (Snapshot == null || Snapshot.ActiveMove == null) return false;
                return Snapshot.PhaseEnum == EncounterPhase.Active;
            }
        }

        public long RemainingTicks(long currentServerTick)
        {
            if (Snapshot == null || !Snapshot.DeadlineTick.HasValue) return 0;
            long r = Snapshot.DeadlineTick.Value - currentServerTick;
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
            LastLifeGeneration = 0;
        }
    }
}
