// OPC-15 O5 (WO26) — Immutable, renderer-neutral view state for Godot consumers.
// Every collection is copied; no DTO or list exposed by reference can be mutated by UI.
// Pure C#. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;

namespace NguMach.Client.Core.Encounter
{
    public sealed class EncounterShapeState
    {
        public MoveShapeKind Kind { get; }
        public double CenterXWu { get; }
        public double CenterYWu { get; }
        public double? AngleDegrees { get; }
        public double? RangeWu { get; }
        public double? RadiusWu { get; }
        public double? InnerRadiusWu { get; }
        public double? OuterRadiusWu { get; }
        public double? FacingX { get; }
        public double? FacingY { get; }

        internal EncounterShapeState(MoveShape shape)
        {
            Kind = shape.Kind;
            CenterXWu = shape.CenterXWu;
            CenterYWu = shape.CenterYWu;
            AngleDegrees = shape.AngleDegrees;
            RangeWu = shape.RangeWu;
            RadiusWu = shape.RadiusWu;
            InnerRadiusWu = shape.InnerRadiusWu;
            OuterRadiusWu = shape.OuterRadiusWu;
            FacingX = shape.FacingX;
            FacingY = shape.FacingY;
        }
    }

    public sealed class EncounterMoveState
    {
        public string MoveId { get; }
        public string CastId { get; }
        public MoveState State { get; }
        public long TicksRemaining { get; }
        public long StateEndsAtTick { get; }
        public EncounterShapeState Shape { get; }
        public string TargetLock { get; }

        internal EncounterMoveState(ActiveMove move)
        {
            MoveId = move.MoveId;
            CastId = move.CastId;
            State = move.State;
            TicksRemaining = move.TicksRemaining;
            StateEndsAtTick = move.StateEndsAtTick;
            Shape = move.Shape == null ? null : new EncounterShapeState(move.Shape);
            TargetLock = move.TargetLock;
        }
    }

    public sealed class EncounterArenaState
    {
        public string Shape { get; }
        public double CenterXWu { get; }
        public double CenterYWu { get; }
        public double RadiusWu { get; }

        internal EncounterArenaState(EncounterArena arena)
        {
            Shape = arena.Shape;
            CenterXWu = arena.CenterXWu;
            CenterYWu = arena.CenterYWu;
            RadiusWu = arena.RadiusWu;
        }
    }

    public sealed class EncounterSafePadState
    {
        public double CenterXWu { get; }
        public double CenterYWu { get; }
        public double RadiusWu { get; }
        public bool Applies { get; }

        internal EncounterSafePadState(SafePad pad)
        {
            CenterXWu = pad.CenterXWu;
            CenterYWu = pad.CenterYWu;
            RadiusWu = pad.RadiusWu;
            Applies = pad.Applies;
        }
    }

    public sealed class EncounterPhaseNpcState
    {
        public string NpcId { get; }
        public double XWu { get; }
        public double YWu { get; }
        public bool Active { get; }

        internal EncounterPhaseNpcState(PhaseNpc npc)
        {
            NpcId = npc.NpcId;
            XWu = npc.XWu;
            YWu = npc.YWu;
            Active = npc.Active;
        }
    }

    public sealed class EncounterState
    {
        public int SchemaVersion { get; }
        public string EncounterId { get; }
        public string QuestId { get; }
        public string BossRecordId { get; }
        public string BossEntityId { get; }
        public long BossLifeId { get; }
        public long BossRevision { get; }
        public EncounterStatus Status { get; }
        public BossPhase Phase { get; }
        public int BossHp { get; }
        public int BossMaxHp { get; }
        public long ServerTick { get; }
        public IReadOnlyList<string> RegisteredCharacterIds { get; }
        public EncounterMoveState ActiveMove { get; }
        public IReadOnlyDictionary<string, long> MoveCooldownRemainingTicks { get; }
        public long PhaseGuardRemainingTicks { get; }
        public long? WipeCountdownTicks { get; }
        public EncounterArenaState Arena { get; }
        public IReadOnlyList<EncounterSafePadState> SafePads { get; }
        public EncounterPhaseNpcState PhaseNpc { get; }
        public bool TrialNpcVisible { get; }

        internal EncounterState(EncounterSnapshot snapshot)
        {
            SchemaVersion = snapshot.SchemaVersion;
            EncounterId = snapshot.EncounterId;
            QuestId = snapshot.QuestId;
            BossRecordId = snapshot.BossRecordId;
            BossEntityId = snapshot.BossEntityId;
            BossLifeId = snapshot.BossLifeId;
            BossRevision = snapshot.BossRevision;
            Status = snapshot.Status;
            Phase = snapshot.Phase;
            BossHp = snapshot.BossHp;
            BossMaxHp = snapshot.BossMaxHp;
            ServerTick = snapshot.ServerTick;
            RegisteredCharacterIds = new ReadOnlyCollection<string>(
                snapshot.RegisteredCharacterIds == null ? new List<string>() : new List<string>(snapshot.RegisteredCharacterIds));
            ActiveMove = snapshot.ActiveMove == null ? null : new EncounterMoveState(snapshot.ActiveMove);
            var cooldowns = new Dictionary<string, long>(StringComparer.Ordinal);
            if (snapshot.MoveCooldownRemainingTicks != null)
                foreach (var pair in snapshot.MoveCooldownRemainingTicks) cooldowns[pair.Key] = pair.Value;
            MoveCooldownRemainingTicks = new ReadOnlyDictionary<string, long>(cooldowns);
            PhaseGuardRemainingTicks = snapshot.PhaseGuardRemainingTicks;
            WipeCountdownTicks = snapshot.WipeCountdownTicks;
            Arena = snapshot.Arena == null ? null : new EncounterArenaState(snapshot.Arena);
            var pads = new List<EncounterSafePadState>();
            if (snapshot.SafePads != null)
                foreach (var pad in snapshot.SafePads) if (pad != null) pads.Add(new EncounterSafePadState(pad));
            SafePads = new ReadOnlyCollection<EncounterSafePadState>(pads);
            PhaseNpc = snapshot.PhaseNpc == null ? null : new EncounterPhaseNpcState(snapshot.PhaseNpc);
            TrialNpcVisible = snapshot.TrialNpcVisible;
        }
    }
}
