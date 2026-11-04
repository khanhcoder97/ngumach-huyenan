// OPC-15 O1 (WO26) — Renderer-neutral encounter DTO matching the approved reference payload.
// Field names/types exactly as in encounter_snapshot_v1_reference_20261104.json.
// Pure C#. Owner: OpenCode (portable core).
// Refs: Encounter_Snapshot_Review_Decisions_20261103_vi.md, WO25/WO26.

using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace NguMach.Client.Core.Encounter
{
    public enum EncounterStatus { Open, Defeated, Reset }
    public enum BossPhase { Phase1 = 1, Phase2 = 2, Phase3 = 3 }
    public enum MoveState { Telegraph, Impact, Recovery }
    public enum MoveShapeKind { Cone, Circle, Annulus }

    public sealed class MoveShape
    {
        [JsonProperty("kind")] public string KindRaw { get; set; }
        [JsonProperty("centerXWu")] public double CenterXWu { get; set; }
        [JsonProperty("centerYWu")] public double CenterYWu { get; set; }
        [JsonProperty("angleDegrees")] public double? AngleDegrees { get; set; }
        [JsonProperty("rangeWu")] public double RangeWu { get; set; }
        [JsonProperty("radiusWu")] public double? RadiusWu { get; set; }
        [JsonProperty("innerRadiusWu")] public double? InnerRadiusWu { get; set; }
        [JsonProperty("outerRadiusWu")] public double? OuterRadiusWu { get; set; }
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
        [JsonProperty("ticksRemaining")] public long TicksRemaining { get; set; }
        [JsonProperty("stateEndsAtTick")] public long StateEndsAtTick { get; set; }
        [JsonProperty("shape")] public MoveShape Shape { get; set; }
        [JsonProperty("targetLock")] public string TargetLock { get; set; }

        [JsonIgnore] public MoveState State
        {
            get { MoveState s; return Enum.TryParse(StateRaw, true, out s) ? s : MoveState.Telegraph; }
        }
    }

    public sealed class EncounterArena
    {
        [JsonProperty("shape")] public string Shape { get; set; }
        [JsonProperty("centerXWu")] public double CenterXWu { get; set; }
        [JsonProperty("centerYWu")] public double CenterYWu { get; set; }
        [JsonProperty("radiusWu")] public double RadiusWu { get; set; }
    }

    public sealed class SafePad
    {
        [JsonProperty("centerXWu")] public double CenterXWu { get; set; }
        [JsonProperty("centerYWu")] public double CenterYWu { get; set; }
        [JsonProperty("radiusWu")] public double RadiusWu { get; set; }
        [JsonProperty("applies")] public bool Applies { get; set; }
    }

    public sealed class PhaseNpc
    {
        [JsonProperty("npcId")] public string NpcId { get; set; }
        [JsonProperty("xWu")] public double XWu { get; set; }
        [JsonProperty("yWu")] public double YWu { get; set; }
        [JsonProperty("active")] public bool Active { get; set; }
    }

    public sealed class EncounterSnapshot
    {
        [JsonProperty("schemaVersion")] public int SchemaVersion { get; set; } = 1;
        [JsonProperty("encounterId")] public string EncounterId { get; set; }
        [JsonProperty("questId")] public string QuestId { get; set; }
        [JsonProperty("bossRecordId")] public string BossRecordId { get; set; }
        [JsonProperty("bossEntityId")] public string BossEntityId { get; set; }
        [JsonProperty("bossLifeId")] public long BossLifeId { get; set; }
        [JsonProperty("bossRevision")] public long BossRevision { get; set; }
        [JsonProperty("status")] public string StatusRaw { get; set; }
        [JsonProperty("phase")] public int PhaseRaw { get; set; }
        [JsonProperty("bossHp")] public int BossHp { get; set; }
        [JsonProperty("bossMaxHp")] public int BossMaxHp { get; set; }
        [JsonProperty("serverTick")] public long ServerTick { get; set; }
        [JsonProperty("registeredCharacterIds")] public List<string> RegisteredCharacterIds { get; set; }
        [JsonProperty("activeMove")] public ActiveMove ActiveMove { get; set; }
        [JsonProperty("moveCooldownRemainingTicks")] public Dictionary<string, long> MoveCooldownRemainingTicks { get; set; }
        [JsonProperty("phaseGuardRemainingTicks")] public long PhaseGuardRemainingTicks { get; set; }
        [JsonProperty("wipeCountdownTicks")] public long? WipeCountdownTicks { get; set; }
        [JsonProperty("arena")] public EncounterArena Arena { get; set; }
        [JsonProperty("safePads")] public List<SafePad> SafePads { get; set; }
        [JsonProperty("phaseNpc")] public PhaseNpc PhaseNpc { get; set; }
        [JsonProperty("trialNpcVisible")] public bool TrialNpcVisible { get; set; }

        [JsonExtensionData] public Dictionary<string, object> Extra { get; set; }

        [JsonIgnore] public EncounterStatus Status
        {
            get { EncounterStatus s; return Enum.TryParse(StatusRaw, true, out s) ? s : EncounterStatus.Open; }
        }
        [JsonIgnore] public BossPhase Phase
        {
            get { return (BossPhase)Math.Max(1, Math.Min(3, PhaseRaw)); }
        }
    }
}
