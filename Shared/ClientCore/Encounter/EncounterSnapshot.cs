// OPC-15 O1 — Renderer-neutral encounter DTOs matching the approved alpha contract.
// Numeric boss phase 1/2/3, encounter status OPEN/DEFEATED/RESET, move state
// TELEGRAPH/IMPACT/RECOVERY, bossHp/bossMaxHp/bossRevision, shape.kind/center/rangeWu/...
// Strict: no silent mapping of unknown shapes/phases; unknown properties rejected.
// Pure C# (no Unity/Godot). Owner: OpenCode (portable core).
// Refs: Encounter_Snapshot_Review_Decisions_20261103_vi.md, work order 25 O1.

using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace NguMach.Client.Core.Encounter
{
    public enum EncounterStatus
    {
        Open,
        Defeated,
        Reset,
    }

    public enum BossPhase
    {
        Phase1 = 1,
        Phase2 = 2,
        Phase3 = 3,
    }

    public enum MoveState
    {
        Telegraph,
        Impact,
        Recovery,
    }

    public enum MoveShapeKind
    {
        Cone,
        Circle,
        Annulus,
    }

    public sealed class Point2
    {
        [JsonProperty("x")] public double X { get; set; }
        [JsonProperty("y")] public double Y { get; set; }
    }

    public sealed class MoveShape
    {
        [JsonProperty("kind")] public string KindRaw { get; set; }
        [JsonProperty("center")] public Point2 Center { get; set; }
        [JsonProperty("rangeWu")] public double RangeWu { get; set; }
        [JsonProperty("radiusWu")] public double? RadiusWu { get; set; }
        [JsonProperty("innerRadiusWu")] public double? InnerRadiusWu { get; set; }
        [JsonProperty("outerRadiusWu")] public double? OuterRadiusWu { get; set; }
        [JsonProperty("angleDegrees")] public double? AngleDegrees { get; set; }
        [JsonProperty("facingX")] public double FacingX { get; set; }
        [JsonProperty("facingY")] public double FacingY { get; set; }

        [JsonIgnore] public MoveShapeKind Kind
        {
            get
            {
                if (string.Equals(KindRaw, "circle", StringComparison.OrdinalIgnoreCase)) return MoveShapeKind.Circle;
                if (string.Equals(KindRaw, "annulus", StringComparison.OrdinalIgnoreCase)) return MoveShapeKind.Annulus;
                return MoveShapeKind.Cone;
            }
        }
    }

    public sealed class ActiveMove
    {
        [JsonProperty("moveId")] public string MoveId { get; set; }
        [JsonProperty("castId")] public string CastId { get; set; }
        [JsonProperty("state")] public string StateRaw { get; set; }
        [JsonProperty("stateEndsAtTick")] public long StateEndsAtTick { get; set; }
        [JsonProperty("shape")] public MoveShape Shape { get; set; }

        [JsonIgnore] public MoveState State
        {
            get
            {
                MoveState s;
                return Enum.TryParse(StateRaw, true, out s) ? s : MoveState.Telegraph;
            }
        }
    }

    public sealed class EncounterRegistration
    {
        [JsonProperty("registeredCharacterIds")] public List<string> RegisteredCharacterIds { get; set; }
        [JsonProperty("ownerCharacterId")] public string OwnerCharacterId { get; set; }
    }

    public sealed class EncounterArena
    {
        [JsonProperty("minX")] public double MinX { get; set; }
        [JsonProperty("maxX")] public double MaxX { get; set; }
        [JsonProperty("minY")] public double MinY { get; set; }
        [JsonProperty("maxY")] public double MaxY { get; set; }
    }

    public sealed class SafePad
    {
        [JsonProperty("id")] public string Id { get; set; }
        [JsonProperty("x")] public double X { get; set; }
        [JsonProperty("y")] public double Y { get; set; }
        [JsonProperty("radiusWu")] public double RadiusWu { get; set; }
    }

    public sealed class EncounterSnapshot
    {
        [JsonProperty("schemaVersion")] public int SchemaVersion { get; set; } = 1;
        [JsonProperty("encounterId")] public string EncounterId { get; set; }
        [JsonProperty("bossLifeId")] public long BossLifeId { get; set; }
        [JsonProperty("status")] public string StatusRaw { get; set; }
        [JsonProperty("phase")] public int PhaseRaw { get; set; }
        [JsonProperty("serverTick")] public long ServerTick { get; set; }
        [JsonProperty("bossHp")] public int BossHp { get; set; }
        [JsonProperty("bossMaxHp")] public int BossMaxHp { get; set; }
        [JsonProperty("bossRevision")] public long BossRevision { get; set; }
        [JsonProperty("activeMove")] public ActiveMove ActiveMove { get; set; }
        [JsonProperty("deadlineTick")] public long? DeadlineTick { get; set; }
        [JsonProperty("ticksRemaining")] public long? TicksRemaining { get; set; }
        [JsonProperty("registration")] public EncounterRegistration Registration { get; set; }
        [JsonProperty("arena")] public EncounterArena Arena { get; set; }
        [JsonProperty("safePads")] public List<SafePad> SafePads { get; set; }
        [JsonProperty("npcId")] public string NpcId { get; set; }
        [JsonProperty("cooldowns")] public Dictionary<string, long> Cooldowns { get; set; }

        [JsonExtensionData] public Dictionary<string, object> Extra { get; set; }

        [JsonIgnore] public EncounterStatus Status
        {
            get
            {
                EncounterStatus s;
                return Enum.TryParse(StatusRaw, true, out s) ? s : EncounterStatus.Open;
            }
        }
        [JsonIgnore] public BossPhase Phase
        {
            get { return (BossPhase)Math.Max(1, Math.Min(3, PhaseRaw)); }
        }
    }
}
