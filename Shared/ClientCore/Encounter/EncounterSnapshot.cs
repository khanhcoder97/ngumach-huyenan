// OPC-15 O-C — Renderer-neutral encounter DTOs for the approved alpha snapshot contract.
// Pure C# (no Unity/Godot). Mirrors EncounterSnapshotV1 (additionalProperties:false).
// Owner: OpenCode (portable core). Muse binds these to Godot scenes; Qoder owns the route.
// Refs: Encounter_Snapshot_Review_Decisions_20261103_vi.md

using System;
using Newtonsoft.Json;

namespace NguMach.Client.Core.Encounter
{
    public enum EncounterPhase
    {
        Idle = 0,
        Telegraph = 1,
        Active = 2,
        Phase2 = 3,
        Phase3 = 4,
        Defeated = 5,
        Wiped = 6,
    }

    public enum MoveShapeKind
    {
        Cone = 0,
        Circle = 1,
        Annulus = 2,
    }

    public sealed class MoveShape
    {
        [JsonProperty("type")] public string Type { get; set; } = "cone";
        // Cone
        [JsonProperty("angleDegrees")] public double? AngleDegrees { get; set; }
        [JsonProperty("range")] public double? Range { get; set; }
        // Circle
        [JsonProperty("radius")] public double? Radius { get; set; }
        // Annulus
        [JsonProperty("innerRadius")] public double? InnerRadius { get; set; }
        [JsonProperty("outerRadius")] public double? OuterRadius { get; set; }
        // Facing (locked at telegraph; finite, normalized within tolerance)
        [JsonProperty("facingX")] public double FacingX { get; set; }
        [JsonProperty("facingY")] public double FacingY { get; set; }

        public MoveShapeKind Kind
        {
            get
            {
                if (string.Equals(Type, "circle", StringComparison.OrdinalIgnoreCase)) return MoveShapeKind.Circle;
                if (string.Equals(Type, "annulus", StringComparison.OrdinalIgnoreCase)) return MoveShapeKind.Annulus;
                return MoveShapeKind.Cone;
            }
        }
    }

    public sealed class ActiveMove
    {
        [JsonProperty("moveId")] public string MoveId { get; set; }
        [JsonProperty("castId")] public string CastId { get; set; }
        [JsonProperty("stateEndsAtTick")] public long StateEndsAtTick { get; set; }
        [JsonProperty("shape")] public MoveShape Shape { get; set; }
    }

    public sealed class EncounterSnapshot
    {
        [JsonProperty("schemaVersion")] public int SchemaVersion { get; set; } = 1;
        [JsonProperty("encounterId")] public string EncounterId { get; set; }
        [JsonProperty("bossLifeId")] public string BossLifeId { get; set; }
        [JsonProperty("generation")] public long Generation { get; set; }
        [JsonProperty("ownerCharacterId")] public string OwnerCharacterId { get; set; }
        [JsonProperty("questAttemptId")] public string QuestAttemptId { get; set; }
        [JsonProperty("phase")] public string Phase { get; set; }
        [JsonProperty("serverTick")] public long ServerTick { get; set; }
        [JsonProperty("hp")] public int Hp { get; set; }
        [JsonProperty("maxHp")] public int MaxHp { get; set; }
        [JsonProperty("revision")] public long Revision { get; set; }
        [JsonProperty("activeMove")] public ActiveMove ActiveMove { get; set; }
        [JsonProperty("deadlineTick")] public long? DeadlineTick { get; set; }
        [JsonProperty("ticksRemaining")] public long? TicksRemaining { get; set; }
        [JsonProperty("lifeScope")] public string LifeScope { get; set; } // owner | attempt

        public EncounterPhase PhaseEnum
        {
            get
            {
                if (string.IsNullOrEmpty(Phase)) return EncounterPhase.Idle;
                EncounterPhase p;
                return Enum.TryParse(Phase, true, out p) ? p : EncounterPhase.Idle;
            }
        }
    }
}
