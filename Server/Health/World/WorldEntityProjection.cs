using Server.Health.Gameplay.Combat;

namespace Server.Health.World;

// Internal read-model projection for QOD-16 (phase 1). Maps registry
// instances to a flat entity record with revision/floor/lifeId and, for
// mobs, HP from the gated combat stat bundle. NPCs stay invulnerable with
// hp 0 (Art Bible §13); bosses stay BOSSDATA_BLOCKED with hp 0 until their
// numeric data is complete. This shape is not wired to the HTTP snapshot
// until the QOD-16 proposal is approved.
public sealed record ProjectedEntity(
    string EntityId,
    string Kind,
    string MapId,
    string FloorId,
    double X,
    double Y,
    string State,
    long Revision,
    long LifeId,
    int Hp,
    int MaxHp);

public sealed class WorldEntityProjectionService
{
    private const string EliteSuffix = "_ELITE";

    private readonly WorldEntityRegistry _entities;
    private readonly MobLifecycleService _mobs;
    private readonly CombatDamageFeature _combat;

    public WorldEntityProjectionService(
        WorldEntityRegistry entities,
        MobLifecycleService mobs,
        CombatDamageFeature combat)
    {
        _entities = entities;
        _mobs = mobs;
        _combat = combat;
    }

    public IReadOnlyList<ProjectedEntity> Project()
    {
        var result = new List<ProjectedEntity>(_entities.Count);
        foreach (var entity in _entities.All)
        {
            var stats = ResolveStats(entity);
            var state = string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal) ||
                        string.Equals(entity.Kind, WorldEntityKinds.Boss, StringComparison.Ordinal)
                ? _mobs.GetState(entity.EntityId)
                : entity.State;
            result.Add(new ProjectedEntity(
                entity.EntityId,
                entity.Kind,
                entity.MapId,
                entity.FloorId,
                entity.X,
                entity.Y,
                state,
                entity.Revision,
                entity.LifeId,
                stats?.Hp ?? 0,
                stats?.Hp ?? 0));
        }

        return result;
    }

    private MobEffectiveStats? ResolveStats(WorldEntityInstance entity)
    {
        if (!_combat.Enabled)
        {
            return null;
        }

        if (!string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal))
        {
            return null;
        }

        var templateId = entity.TemplateIds.FirstOrDefault();
        if (templateId is null)
        {
            return null;
        }

        var bundle = _combat.MobStats;
        var archetype = bundle.Archetypes.FirstOrDefault(stats =>
            string.Equals(stats.MobId, templateId, StringComparison.Ordinal));
        var elite = false;
        if (archetype is null &&
            templateId.EndsWith(EliteSuffix, StringComparison.Ordinal))
        {
            archetype = bundle.Archetypes.FirstOrDefault(stats =>
                string.Equals(
                    stats.MobId,
                    templateId[..^EliteSuffix.Length],
                    StringComparison.Ordinal));
            elite = archetype is not null;
        }

        if (archetype is null)
        {
            return null;
        }

        var level5 = archetype.ReferenceLevel5;
        return elite
            ? new MobEffectiveStats(
                checked((int)Math.Round(level5.Hp * bundle.Elite.Hp)),
                level5.Attack * bundle.Elite.Attack,
                level5.Defense * bundle.Elite.Defense)
            : level5;
    }
}
