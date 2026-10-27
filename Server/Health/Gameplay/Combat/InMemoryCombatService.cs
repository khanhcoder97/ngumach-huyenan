using System.Collections.Concurrent;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

public sealed class InMemoryCombatService : ICombatService
{
    private readonly ICombatSkillCatalog _skills;
    private readonly ICombatTargetProvider _targets;
    private readonly ServerClock _clock;
    private readonly ConcurrentDictionary<string, DateTimeOffset> _cooldowns =
        new(StringComparer.Ordinal);

    public InMemoryCombatService(
        ICombatSkillCatalog skills,
        ICombatTargetProvider targets,
        ServerClock clock)
    {
        _skills = skills;
        _targets = targets;
        _clock = clock;
    }

    public CombatOutcome Resolve(PlayerSession actor, CombatCommand command)
    {
        ArgumentNullException.ThrowIfNull(actor);
        ArgumentNullException.ThrowIfNull(command);

        var fieldErrors = Validate(command);
        if (fieldErrors.Count > 0)
        {
            return CombatOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, fieldErrors: [.. fieldErrors]);
        }

        lock (actor.SyncRoot)
        {
            if (!_skills.TryGet(command.SkillId!, out var skill))
            {
                return CombatOutcome.Rejected(
                    CombatErrorCodes.UnknownSkill, retryable: false, "skillId");
            }

            if (!string.Equals(skill.ClassId, actor.ClassId, StringComparison.Ordinal))
            {
                return CombatOutcome.Rejected(
                    CombatErrorCodes.SkillNotAvailable, retryable: false, "skillId");
            }

            var sequence = command.InputSequence.GetValueOrDefault();
            if (sequence <= actor.LastInputSequence)
            {
                return CombatOutcome.Rejected(
                    P1ErrorCodes.StaleSequence, retryable: false, "inputSequence");
            }

            if (!TryResolveTarget(actor, skill, command.TargetId, out var target, out var targetFailure))
            {
                return targetFailure!;
            }

            if (skill.RangeWu is { } range &&
                !string.Equals(skill.TargetingType, CombatTargetingTypes.Self, StringComparison.Ordinal))
            {
                var deltaX = target!.X - actor.X;
                var deltaY = target.Y - actor.Y;
                if (Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY)) > range + 1e-9)
                {
                    return CombatOutcome.Rejected(
                        CombatErrorCodes.OutOfRange, retryable: true, "targetId");
                }
            }

            var now = _clock.UtcNow;
            var cooldownKey = CooldownKey(actor.CharacterId, skill.SkillId);
            if (_cooldowns.TryGetValue(cooldownKey, out var cooldownEndsAt) && now < cooldownEndsAt)
            {
                return CombatOutcome.Rejected(
                    CombatErrorCodes.CooldownActive, retryable: true, "skillId");
            }

            if (skill.ResourceCost > 0)
            {
                if (!string.Equals(skill.Resource, "MP", StringComparison.OrdinalIgnoreCase))
                {
                    return CombatOutcome.Rejected(
                        CombatErrorCodes.UnsupportedResource, retryable: false, "skillId");
                }

                if (actor.Mp < skill.ResourceCost)
                {
                    return CombatOutcome.Rejected(
                        CombatErrorCodes.InsufficientResource, retryable: false, "skillId");
                }
            }

            if (skill.ResourceCost > 0)
            {
                actor.Mp -= skill.ResourceCost;
            }

            var cooldownEnd = now.AddSeconds(skill.CooldownSeconds);
            _cooldowns[cooldownKey] = cooldownEnd;
            actor.LastInputSequence = sequence;
            actor.Revision++;

            var combatEvent = new CombatEvent
            {
                EventId = Guid.NewGuid().ToString("N"),
                EventType = CombatEventTypes.Effect,
                AggregateId = actor.CharacterId,
                AggregateRevision = actor.Revision,
                EmittedAtUtc = P1Time.ToUtcString(now),
                Payload = new CombatEventPayload
                {
                    SourceId = actor.CharacterId,
                    TargetId = target!.EntityId,
                    SkillId = skill.SkillId,
                    CooldownEndsAtUtc = P1Time.ToUtcString(cooldownEnd)
                }
            };

            return CombatOutcome.Success(combatEvent);
        }
    }

    private bool TryResolveTarget(
        PlayerSession actor,
        CombatSkillDefinition skill,
        string? targetId,
        out CombatTarget? target,
        out CombatOutcome? failure)
    {
        if (string.Equals(skill.TargetingType, CombatTargetingTypes.Self, StringComparison.Ordinal))
        {
            target = new CombatTarget(actor.CharacterId, actor.MapId, actor.X, actor.Y, actor.Hp);
            failure = null;
            return true;
        }

        target = null;
        if (targetId is null)
        {
            failure = CombatOutcome.Rejected(
                P1ErrorCodes.InvalidPayload, retryable: false, "targetId");
            return false;
        }

        if (string.Equals(targetId, actor.CharacterId, StringComparison.Ordinal))
        {
            failure = CombatOutcome.Rejected(
                CombatErrorCodes.InvalidTarget, retryable: false, "targetId");
            return false;
        }

        if (!_targets.TryResolve(targetId, out target) || target is null)
        {
            failure = CombatOutcome.Rejected(
                CombatErrorCodes.TargetNotFound, retryable: true, "targetId");
            return false;
        }

        if (!string.Equals(target.MapId, actor.MapId, StringComparison.Ordinal))
        {
            target = null;
            failure = CombatOutcome.Rejected(
                CombatErrorCodes.TargetNotFound, retryable: true, "targetId");
            return false;
        }

        if (!target.IsAlive)
        {
            failure = CombatOutcome.Rejected(
                CombatErrorCodes.TargetNotAlive, retryable: false, "targetId");
            return false;
        }

        failure = null;
        return true;
    }

    private static List<string> Validate(CombatCommand command)
    {
        var errors = new List<string>();

        if (command.InputSequence is null || command.InputSequence < 1)
        {
            errors.Add("inputSequence");
        }

        if (!P1Validation.IsSkillId(command.SkillId))
        {
            errors.Add("skillId");
        }

        if (command.TargetId is not null && !P1Validation.IsTargetId(command.TargetId))
        {
            errors.Add("targetId");
        }

        if (!IsAimComponent(command.AimX))
        {
            errors.Add("aimX");
        }

        if (!IsAimComponent(command.AimY))
        {
            errors.Add("aimY");
        }

        if (command.ClientTimeUtc is not null &&
            !P1Validation.TryParseUtc(command.ClientTimeUtc, out _))
        {
            errors.Add("clientTimeUtc");
        }

        return errors;
    }

    private static bool IsAimComponent(double? value) =>
        value is { } component &&
        double.IsFinite(component) &&
        component >= -1 &&
        component <= 1;

    private static string CooldownKey(string characterId, string skillId) =>
        string.Concat(characterId, "|", skillId);
}
