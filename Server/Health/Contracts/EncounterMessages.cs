using System.Text.Json.Serialization;

namespace Server.Health.Contracts;

// QOD-21 Q2 wire, approved in docs/production/Encounter_Snapshot_Review_Decisions_20261103_vi.md
// and shaped by Implementation/Content/DesignBaselines/encounter_snapshot_v1_reference_20261104.json.
// A snapshot is one atomic copy of a single encounter generation: HP, phase, life,
// revision, active move and its deadline all come from the same lock/tick, and the
// read model adds nothing the domain does not already hold. No CombatEventV2 type is
// added (boss.eventProtocol), and nothing here is a client-authoritative value.
public sealed class EncounterSnapshotV1
{
    public int SchemaVersion { get; init; } = 1;

    // Opaque id the server issues for (characterId, questAttemptId); it survives a
    // wipe, and a finished or abandoned attempt is never re-used.
    public required string EncounterId { get; init; }

    public required string QuestId { get; init; }

    // The quest-instance boss record only; the world-event record at the same
    // coordinate is a different entity and is never reported here.
    public required string BossRecordId { get; init; }
    public required string BossEntityId { get; init; }

    // Bumped per fresh attempt; a retry is a new life, never a replayed one.
    public required long BossLifeId { get; init; }

    // Moves when snapshot state changes, so a poller can tell two identical-looking
    // frames apart without reading its own clock.
    public required long BossRevision { get; init; }

    public required string Status { get; init; }

    public required int Phase { get; init; }
    public required int BossHp { get; init; }
    public required int BossMaxHp { get; init; }

    // Authoritative tick the snapshot was taken on; every *Ticks field is measured
    // against it, never against a client clock or an animation callback.
    public required long ServerTick { get; init; }

    // Exactly one entry: no late join and no party reader until a roster authority
    // exists, and a reconnect of the same verified character keeps its registration.
    public required IReadOnlyList<string> RegisteredCharacterIds { get; init; }

    // Null while no move is in flight (between moves, during the phase guard, or
    // once the fight is over).
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public EncounterActiveMoveV1? ActiveMove { get; init; }

    // Remaining ticks before each move can be chosen again, keyed by move id.
    public required EncounterMoveCooldownsV1 MoveCooldownRemainingTicks { get; init; }

    public required int PhaseGuardRemainingTicks { get; init; }

    // Ticks left on the sourced wipe countdown, null while a live target exists.
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public int? WipeCountdownTicks { get; init; }

    public required EncounterArenaV1 Arena { get; init; }

    public required IReadOnlyList<EncounterSafePadV1> SafePads { get; init; }

    public required EncounterPhaseNpcV1 PhaseNpc { get; init; }

    // True only after the boss is down AND the fragment is claimed, while the quest
    // has not been turned in — the sourced fix for the circular dependency.
    public required bool TrialNpcVisible { get; init; }
}

public static class EncounterSnapshotStatuses
{
    public const string Open = "OPEN";
    public const string Reset = "RESET";
    public const string Defeated = "DEFEATED";
}

public static class EncounterMoveStates
{
    public const string Telegraph = "TELEGRAPH";
    public const string Recovery = "RECOVERY";
}

public static class EncounterShapeKinds
{
    public const string Cone = "CONE";
    public const string Circle = "CIRCLE";
    public const string Annulus = "ANNULUS";
}

public static class EncounterTargetLocks
{
    public const string TelegraphStartFacing = "TELEGRAPH_START_FACING";
    public const string TelegraphStartTargetPosition = "TELEGRAPH_START_TARGET_POSITION";
    public const string BossPosition = "BOSS_POSITION";
}

public sealed class EncounterActiveMoveV1
{
    public required string MoveId { get; init; }

    // Stable for the whole cast of one move so a poller never restarts the VFX;
    // combined with bossLifeId it identifies a unique attempt at the swing.
    public required string CastId { get; init; }

    public required string State { get; init; }

    // Kept only because it agrees with StateEndsAtTick and ServerTick; a validator
    // rejects the pair when they disagree.
    public required int TicksRemaining { get; init; }

    public required long StateEndsAtTick { get; init; }

    public required EncounterMoveShapeV1 Shape { get; init; }

    public required string TargetLock { get; init; }
}

// One shape object carries every kind; the fields a kind does not use are null by
// rule (declared once here and enforced by the schema and the contract validator),
// never filled with an arbitrary number.
public sealed class EncounterMoveShapeV1
{
    public required string Kind { get; init; }
    public required double CenterXWu { get; init; }
    public required double CenterYWu { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? AngleDegrees { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? RangeWu { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? RadiusWu { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? InnerRadiusWu { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? OuterRadiusWu { get; init; }

    // Cone facing only: locked at the telegraph, finite and normalized. A consumer
    // must not derive a direction from the owner's current position, and AngleDegrees
    // is the opening width, never a substitute for this vector.
    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? FacingX { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.Never)]
    public double? FacingY { get; init; }
}

public sealed class EncounterMoveCooldownsV1
{
    public required int A { get; init; }
    public required int B { get; init; }
    public required int C { get; init; }
}

public sealed class EncounterArenaV1
{
    public required string Shape { get; init; }
    public required double CenterXWu { get; init; }
    public required double CenterYWu { get; init; }
    public required double RadiusWu { get; init; }
}

public sealed class EncounterSafePadV1
{
    public required double CenterXWu { get; init; }
    public required double CenterYWu { get; init; }
    public required double RadiusWu { get; init; }

    // The source marks the pads phase-3 only and explicitly grants no
    // invulnerability, so this only says whether the pad applies right now.
    public required bool Applies { get; init; }
}

public sealed class EncounterPhaseNpcV1
{
    public required string NpcId { get; init; }
    public required double XWu { get; init; }
    public required double YWu { get; init; }

    // The override moves the same actor, never a second copy of them.
    public required bool Active { get; init; }
}

public sealed class P1EncounterResponse
{
    public int SchemaVersion { get; init; } = 1;
    public required string RequestId { get; init; }
    public required string SessionId { get; init; }
    public required string ServerTimeUtc { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public EncounterSnapshotV1? Result { get; init; }

    [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
    public P1Error? Error { get; init; }
}

public static class EncounterErrorCodes
{
    // A different owner's session, an unknown id, and no live encounter all answer
    // the same way so nothing about another player's attempt is disclosed.
    public const string EncounterNotFound = "encounter_not_found";
}
