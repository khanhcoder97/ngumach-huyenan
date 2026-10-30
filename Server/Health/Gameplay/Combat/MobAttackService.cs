using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// QOD-17 mob -> player damage. A mob ATTACK transition is the impact frame of a
// telegraph, so damage lands only when the target is still up, on the same map
// and floor, and still inside the attack range at impact — that re-check is what
// makes the telegraph a real dodge window (Art Bible §12). Damage follows the
// Production_Rules §2 order of operations with the mob's basic move multiplier
// (the "Đòn thường" column of Art Bible §12, which is the first attack exported
// per archetype) against the labelled completion_v1 player baseline.
//
// Mob accuracy and crit are not exported anywhere in the canonical tables, so a
// mob impact never rolls: it connects unless the player is out of range. Mob
// move *selection* (basic vs heavy) has no canonical rule either, so every mob
// uses its basic move — both gaps are filed as cases in the QOD-16 proposal.
public sealed record MobAttackResolution(
    string EntityId,
    string TargetCharacterId,
    string? AttackId,
    int Damage,
    int HpBefore,
    int HpAfter,
    bool Applied,
    string BlockedReason);

public static class MobAttackBlockedReasons
{
    public const string None = "NONE";
    public const string GateOff = "COMBAT_DAMAGE_GATE_OFF";
    public const string UnknownTemplate = "MOB_TEMPLATE_UNKNOWN";
    public const string EntityMissing = "MOB_ENTITY_NOT_FOUND";
    public const string MobNotAlive = "MOB_NOT_ALIVE";
    public const string TargetMissing = "TARGET_SESSION_NOT_FOUND";
    public const string TargetDown = "TARGET_ALREADY_DOWN";
    public const string TargetLeftField = "TARGET_NOT_ON_FIELD";
    public const string OutOfRangeAtImpact = "TARGET_OUT_OF_RANGE_AT_IMPACT";
}

public sealed class MobAttackService
{
    private readonly WorldEntityRegistry _entities;
    private readonly CombatDamageFeature _combat;
    private readonly MobBehaviorOptions _options;

    public MobAttackService(
        WorldEntityRegistry entities,
        CombatDamageFeature combat,
        MobBehaviorOptions options)
    {
        _entities = entities;
        _combat = combat;
        _options = options;
    }

    // Resolves every impact frame emitted by one mob AI tick. Blocked impacts
    // still return a resolution so the self-check and the logs can tell "no
    // damage because the gate is off" apart from "no damage because the player
    // outran the telegraph".
    public IReadOnlyList<MobAttackResolution> ApplyImpacts(
        IReadOnlyList<MobLifecycleEvent> lifecycleEvents,
        IReadOnlyList<PlayerSession> players)
    {
        var impacts = lifecycleEvents
            .Where(lifecycle =>
                string.Equals(lifecycle.ToState, MobBehaviorStates.Attack, StringComparison.Ordinal))
            .ToArray();
        if (impacts.Length == 0)
        {
            return Array.Empty<MobAttackResolution>();
        }

        var targets = new Dictionary<string, PlayerSession>(StringComparer.Ordinal);
        foreach (var player in players)
        {
            targets[player.CharacterId] = player;
        }

        var resolutions = new List<MobAttackResolution>(impacts.Length);
        foreach (var impact in impacts)
        {
            if (impact.TargetCharacterId is not { } targetCharacterId)
            {
                continue;
            }

            targets.TryGetValue(targetCharacterId, out var target);
            resolutions.Add(ResolveImpact(
                impact.EntityId, targetCharacterId, target));
        }

        return resolutions;
    }

    private MobAttackResolution ResolveImpact(
        string entityId,
        string targetCharacterId,
        PlayerSession? target)
    {
        if (!_combat.Enabled)
        {
            return Blocked(entityId, targetCharacterId, MobAttackBlockedReasons.GateOff);
        }

        if (!_entities.TryGet(entityId, out var entity))
        {
            return Blocked(entityId, targetCharacterId, MobAttackBlockedReasons.EntityMissing);
        }

        if (!string.Equals(entity.State, WorldEntityStates.Alive, StringComparison.Ordinal))
        {
            return Blocked(entityId, targetCharacterId, MobAttackBlockedReasons.MobNotAlive);
        }

        if (target is null)
        {
            return Blocked(entityId, targetCharacterId, MobAttackBlockedReasons.TargetMissing);
        }

        if (ResolveAttack(entity) is not { } attack)
        {
            return Blocked(entityId, targetCharacterId, MobAttackBlockedReasons.UnknownTemplate);
        }

        // Rules §2 step 4: mitigation is the player's armor; no element, crit or
        // damage-reduction bucket applies to a mob swing (none are exported).
        var raw = DamageFormula.RawDamage(
            attack.Stats.Attack, 0, attack.Move.AttackMultiplier, 1, 0);
        var damage = (int)DamageFormula.FinalDamage(
            raw, DamageFormula.MitigationMultiplier(CombatActorBaseline.Armor), 1, 1, 1);

        int hpBefore;
        int hpAfter;
        lock (target.SyncRoot)
        {
            if (target.Hp <= 0)
            {
                return Blocked(
                    entityId, targetCharacterId, MobAttackBlockedReasons.TargetDown);
            }

            if (!string.Equals(target.MapId, entity.MapId, StringComparison.Ordinal) ||
                !string.Equals(target.FloorId, entity.FloorId, StringComparison.Ordinal))
            {
                return Blocked(
                    entityId, targetCharacterId, MobAttackBlockedReasons.TargetLeftField);
            }

            if (Distance(entity.X, entity.Y, target.X, target.Y) > _options.AttackRangeWu)
            {
                return Blocked(
                    entityId, targetCharacterId, MobAttackBlockedReasons.OutOfRangeAtImpact);
            }

            hpBefore = target.Hp;
            hpAfter = Math.Max(0, hpBefore - damage);
            target.Hp = hpAfter;
            // HP is part of the session aggregate, so the revision the client
            // reconciles against has to move with it (design resolution §3).
            target.Revision++;
        }

        return new MobAttackResolution(
            entityId,
            targetCharacterId,
            attack.Move.AttackId,
            damage,
            hpBefore,
            hpAfter,
            Applied: true,
            MobAttackBlockedReasons.None);
    }

    private MobAttack? ResolveAttack(WorldEntityInstance entity)
    {
        var templateId = entity.TemplateIds.FirstOrDefault();
        if (templateId is null)
        {
            return null;
        }

        var bundle = _combat.MobStats;
        var isElite = templateId.EndsWith("_ELITE", StringComparison.Ordinal);
        var archetypeId = isElite ? templateId[..^"_ELITE".Length] : templateId;
        var archetype = bundle.Archetypes.FirstOrDefault(stats =>
            string.Equals(stats.MobId, archetypeId, StringComparison.Ordinal));
        if (archetype is null || archetype.Attacks.Count == 0)
        {
            return null;
        }

        var stats = CombatMobStatLoader.EffectiveAt(
            bundle, archetypeId, CombatActorBaseline.MobReferenceLevel);
        if (isElite)
        {
            stats = new MobEffectiveStats(
                checked((int)Math.Round(stats.Hp * bundle.Elite.Hp)),
                stats.Attack * bundle.Elite.Attack,
                stats.Defense * bundle.Elite.Defense);
        }

        return new MobAttack(archetype.Attacks[0], stats);
    }

    private static MobAttackResolution Blocked(
        string entityId, string targetCharacterId, string reason) =>
        new(entityId, targetCharacterId, AttackId: null, Damage: 0,
            HpBefore: 0, HpAfter: 0, Applied: false, reason);

    private static double Distance(double ax, double ay, double bx, double by) =>
        Math.Sqrt(((bx - ax) * (bx - ax)) + ((by - ay) * (by - ay)));

    private sealed record MobAttack(MobAttackMove Move, MobEffectiveStats Stats);
}
