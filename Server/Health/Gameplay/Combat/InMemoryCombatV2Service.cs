using System.Collections.Concurrent;
using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// QOD-16 phase 2, owner decision Q3: the v2 command endpoint only accepts and
// schedules a cast. It returns the castId, cost/cooldown state and the events
// that already occurred (CAST_START); future impacts resolve on the real tick
// engine (QOD-17) and are read through the event cursor, never batched into
// the accepted response. v1 stays untouched.
public sealed class P1CombatV2Options
{
    public const string SectionName = "P1:CombatV2";

    public bool Enabled { get; set; }
}

public static class CombatV2Actions
{
    public const string BasicAttack = "BASIC_ATTACK";
    public const string Skill = "SKILL";

    public static bool IsKnown(string? value) => value is BasicAttack or Skill;
}

public sealed record CombatV2Intent(
    string ActionKind,
    string? SkillId,
    string? TargetId,
    int InputSequence,
    double AimX,
    double AimY,
    string? ClientTimeUtc);

public sealed record CombatV2Result(
    string CastId,
    string ActionKind,
    string? SkillId,
    int Mp,
    int MpCost,
    string CooldownEndUtc,
    int NextInputSequence,
    IReadOnlyList<CombatEventV2> Events);

public sealed record CombatV2Outcome(CombatV2Result? Result, CombatFailure? Failure)
{
    public bool Accepted => Failure is null;

    public static CombatV2Outcome Success(CombatV2Result result) => new(result, null);

    public static CombatV2Outcome Rejected(
        string code, bool retryable, params string[] fieldErrors) =>
        new(null, new CombatFailure(code, retryable, fieldErrors));
}

public sealed class InMemoryCombatV2Service
{
    // Production Rules §2 basic attack: recovery 0.25 s. The P1 subset only
    // supports Minh Kiếm actions until other classes ship content/runtime.
    public const double BasicAttackCooldownSeconds = 0.25;
    public const string SupportedClassId = "CLASS_MINH_KIEM";

    private readonly ICombatSkillCatalog _skills;
    private readonly CombatEventStore _events;
    private readonly ServerClock _clock;
    private readonly ConcurrentDictionary<(string CharacterId, string Key), IdempotencyEntry>
        _idempotency = new();
    private readonly ConcurrentDictionary<(string CharacterId, string ActionKey), DateTimeOffset>
        _cooldowns = new();

    public InMemoryCombatV2Service(
        ICombatSkillCatalog skills,
        CombatEventStore events,
        ServerClock clock)
    {
        _skills = skills;
        _events = events;
        _clock = clock;
    }

    public CombatV2Outcome Resolve(
        PlayerSession actor, string sessionId, CombatV2Intent intent, string? idempotencyKey)
    {
        ArgumentNullException.ThrowIfNull(actor);
        ArgumentNullException.ThrowIfNull(intent);

        var requestHash = idempotencyKey is null ? null : Hash(intent);
        var entryKey = (actor.CharacterId, idempotencyKey ?? string.Empty);
        if (requestHash is not null && _idempotency.TryGetValue(entryKey, out var prior))
        {
            if (!string.Equals(prior.RequestHash, requestHash, StringComparison.Ordinal))
            {
                return CombatV2Outcome.Rejected(
                    CombatErrorCodes.IdempotencyConflict, retryable: false, "idempotencyKey");
            }

            return prior.Outcome;
        }

        var fieldErrors = Validate(intent);
        if (fieldErrors.Count > 0)
        {
            return CombatV2Outcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, fieldErrors: [.. fieldErrors]);
        }

        var isBasic = string.Equals(
            intent.ActionKind, CombatV2Actions.BasicAttack, StringComparison.Ordinal);
        CombatSkillDefinition? skill = null;
        if (!isBasic)
        {
            if (!_skills.TryGet(intent.SkillId!, out var resolved))
            {
                return CombatV2Outcome.Rejected(
                    CombatErrorCodes.UnknownSkill, retryable: false, "skillId");
            }

            skill = resolved;
        }
        else if (!string.Equals(actor.ClassId, SupportedClassId, StringComparison.Ordinal))
        {
            return CombatV2Outcome.Rejected(
                CombatErrorCodes.SkillNotAvailable, retryable: false, "actionKind");
        }

        if (skill is not null &&
            !string.Equals(skill.ClassId, actor.ClassId, StringComparison.Ordinal))
        {
            return CombatV2Outcome.Rejected(
                CombatErrorCodes.SkillNotAvailable, retryable: false, "skillId");
        }

        lock (actor.SyncRoot)
        {
            if (intent.InputSequence <= actor.LastInputSequence)
            {
                return CombatV2Outcome.Rejected(
                    P1ErrorCodes.StaleSequence, retryable: false, "inputSequence");
            }

            var now = _clock.UtcNow;
            var actionKey = isBasic ? CombatV2Actions.BasicAttack : skill!.SkillId;
            if (_cooldowns.TryGetValue((actor.CharacterId, actionKey), out var cooldownEndsAt) &&
                now < cooldownEndsAt)
            {
                return CombatV2Outcome.Rejected(
                    CombatErrorCodes.CooldownActive, retryable: true, actionKey);
            }

            var mpCost = skill?.ResourceCost ?? 0;
            if (mpCost > 0)
            {
                if (!string.Equals(skill!.Resource, "MP", StringComparison.OrdinalIgnoreCase))
                {
                    return CombatV2Outcome.Rejected(
                        CombatErrorCodes.UnsupportedResource, retryable: false, "skillId");
                }

                if (actor.Mp < mpCost)
                {
                    return CombatV2Outcome.Rejected(
                        CombatErrorCodes.InsufficientResource, retryable: false, "skillId");
                }
            }

            actor.Mp -= mpCost;
            var cooldownEnd = now.AddSeconds(
                isBasic ? BasicAttackCooldownSeconds : skill!.CooldownSeconds);
            _cooldowns[(actor.CharacterId, actionKey)] = cooldownEnd;
            actor.LastInputSequence = intent.InputSequence;
            actor.Revision++;

            var castId = Guid.NewGuid().ToString("N");
            var castStart = _events.Append(
                sessionId,
                new CombatEventV2(
                    Guid.NewGuid().ToString("N"),
                    CombatEventTypesV2.CastStart,
                    castId,
                    actor.CharacterId,
                    null,
                    null,
                    null,
                    actor.MapId + WorldAudience.MapInstanceSuffix,
                    actor.FloorId,
                    actor.Revision,
                    null,
                    _clock.Tick,
                    now,
                    null));

            var result = new CombatV2Result(
                castId,
                intent.ActionKind,
                skill?.SkillId,
                actor.Mp,
                mpCost,
                P1Time.ToUtcString(cooldownEnd),
                actor.LastInputSequence,
                [castStart]);

            var outcome = CombatV2Outcome.Success(result);
            if (requestHash is not null)
            {
                _idempotency[entryKey] = new IdempotencyEntry(requestHash, outcome);
            }

            return outcome;
        }
    }

    private static List<string> Validate(CombatV2Intent intent)
    {
        var errors = new List<string>();
        if (!CombatV2Actions.IsKnown(intent.ActionKind))
        {
            errors.Add("payload.actionKind");
        }

        if (intent.InputSequence < 1)
        {
            errors.Add("payload.inputSequence");
        }

        if (!double.IsFinite(intent.AimX) || intent.AimX is < -1 or > 1)
        {
            errors.Add("payload.aimX");
        }

        if (!double.IsFinite(intent.AimY) || intent.AimY is < -1 or > 1)
        {
            errors.Add("payload.aimY");
        }

        if (string.Equals(intent.ActionKind, CombatV2Actions.Skill, StringComparison.Ordinal) &&
            !P1Validation.IsSkillId(intent.SkillId))
        {
            errors.Add("payload.skillId");
        }

        if (string.Equals(intent.ActionKind, CombatV2Actions.BasicAttack, StringComparison.Ordinal) &&
            intent.SkillId is not null)
        {
            errors.Add("payload.skillId");
        }

        if (intent.TargetId is not null && !P1Validation.IsEntityId(intent.TargetId))
        {
            errors.Add("payload.targetId");
        }

        return errors;
    }

    private static string Hash(CombatV2Intent intent)
    {
        var payload = string.Join(
            '|',
            intent.ActionKind,
            intent.SkillId ?? string.Empty,
            intent.TargetId ?? string.Empty,
            intent.InputSequence,
            intent.AimX.ToString("R", CultureInfo.InvariantCulture),
            intent.AimY.ToString("R", CultureInfo.InvariantCulture),
            intent.ClientTimeUtc ?? string.Empty);
        return Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(payload)));
    }

    private sealed record IdempotencyEntry(string RequestHash, CombatV2Outcome Outcome);
}
