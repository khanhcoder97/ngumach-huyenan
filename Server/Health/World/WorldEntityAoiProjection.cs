using System.Collections.Concurrent;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;

namespace Server.Health.World;

// QOD-16 phase 2 audience policy (owner decision Q6): the v2 snapshot exposes
// MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE after an AOI filter — enter 40 WU,
// leave at 48 WU (8 WU hysteresis) from Online_Persistence_Release_Complete
// §2 — within the same map instance/floor/phase. The internal projection sees
// all 27 candidates; a client only receives its visible subset. Phase and
// instance are labelled DEV placeholders until encounter phases (QOD-19) and
// multi-instance maps exist.
public static class WorldAudience
{
    public const double AoiEnterWu = 40;
    public const double AoiLeaveWu = 48;
    public const string MapInstanceSuffix = "#1";
    public const string Phase = "OPEN_WORLD";
}

public static class WorldHealthStates
{
    public const string Alive = "ALIVE";
    public const string Dead = "DEAD";
    public const string Invulnerable = "INVULNERABLE";
    public const string Blocked = "BLOCKED";
}

public static class WorldAvailability
{
    public const string Available = "AVAILABLE";
    public const string Cooldown = "COOLDOWN";
}

public sealed record ProjectedEntityV2(
    string EntityId,
    string Kind,
    string MapInstanceId,
    string FloorId,
    string Phase,
    double X,
    double Y,
    string State,
    string HealthState,
    bool Targetable,
    string? Availability,
    int Hp,
    int MaxHp,
    long Revision,
    long LifeId);

public sealed class WorldAoiProjectionService
{
    private const string EliteSuffix = "_ELITE";

    private readonly WorldEntityRegistry _entities;
    private readonly MobLifecycleService _mobs;
    private readonly CombatDamageFeature _combat;
    private readonly GatherClaimStore _claims;
    private readonly ConcurrentDictionary<string, SessionVisibility> _visibility =
        new(StringComparer.Ordinal);

    public WorldAoiProjectionService(
        WorldEntityRegistry entities,
        MobLifecycleService mobs,
        CombatDamageFeature combat,
        GatherClaimStore claims)
    {
        _entities = entities;
        _mobs = mobs;
        _combat = combat;
        _claims = claims;
    }

    public int SessionCount => _visibility.Count;

    // Returns the entities visible to this viewer and updates the remembered
    // visibility set used for the 48 WU leave radius on the next read.
    public IReadOnlyList<ProjectedEntityV2> Project(PlayerSession viewer)
    {
        ArgumentNullException.ThrowIfNull(viewer);
        var session = _visibility.GetOrAdd(
            viewer.CharacterId, _ => new SessionVisibility());

        var projected = new List<ProjectedEntityV2>();
        lock (session.SyncRoot)
        {
            var nextVisible = new HashSet<string>(StringComparer.Ordinal);
            var mapInstanceId = viewer.MapId + WorldAudience.MapInstanceSuffix;
            foreach (var entity in _entities.All)
            {
                if (!string.Equals(entity.MapId, viewer.MapId, StringComparison.Ordinal) ||
                    !string.Equals(entity.FloorId, viewer.FloorId, StringComparison.Ordinal))
                {
                    continue;
                }

                var limit = session.Visible.Contains(entity.EntityId)
                    ? WorldAudience.AoiLeaveWu
                    : WorldAudience.AoiEnterWu;
                if (Distance(entity.X, entity.Y, viewer.X, viewer.Y) > limit)
                {
                    continue;
                }

                nextVisible.Add(entity.EntityId);
                projected.Add(Map(entity, viewer, mapInstanceId));
            }

            session.Visible.Clear();
            session.Visible.UnionWith(nextVisible);
        }

        return projected;
    }

    // Reconnect/cleanup: forgetting the session also forgets its hysteresis
    // memory, so a fresh lifetime re-enters at the 40 WU radius.
    public bool RemoveSession(string characterId) =>
        _visibility.TryRemove(characterId, out _);

    private ProjectedEntityV2 Map(
        WorldEntityInstance entity, PlayerSession viewer, string mapInstanceId)
    {
        var isMob = string.Equals(entity.Kind, WorldEntityKinds.Mob, StringComparison.Ordinal);
        var isBoss = string.Equals(entity.Kind, WorldEntityKinds.Boss, StringComparison.Ordinal);
        var isNpc = string.Equals(entity.Kind, WorldEntityKinds.Npc, StringComparison.Ordinal);
        var isClaimable = string.Equals(
                entity.Kind, WorldEntityKinds.GatherNode, StringComparison.Ordinal) ||
            string.Equals(entity.Kind, WorldEntityKinds.Interactable, StringComparison.Ordinal);

        var state = isMob || isBoss
            ? _mobs.GetState(entity.EntityId)
            : entity.State;

        string healthState;
        var targetable = false;
        var hp = 0;
        var maxHp = 0;
        string? availability = null;
        if (isMob)
        {
            var stats = ResolveMobStats(entity);
            var dead = string.Equals(entity.State, WorldEntityStates.Dead, StringComparison.Ordinal) ||
                       string.Equals(state, MobBehaviorStates.Dead, StringComparison.Ordinal);
            healthState = dead ? WorldHealthStates.Dead : WorldHealthStates.Alive;
            targetable = !dead;
            hp = dead ? 0 : stats?.Hp ?? 0;
            maxHp = stats?.Hp ?? 0;
        }
        else if (isBoss)
        {
            // Mãng Cốt stays BOSSDATA_BLOCKED until the QOD-19 encounter data
            // exists; a blocked boss is not shown as dead and is not targetable.
            healthState = WorldHealthStates.Blocked;
            targetable = false;
        }
        else if (isNpc)
        {
            healthState = WorldHealthStates.Invulnerable;
        }
        else if (isClaimable)
        {
            healthState = WorldHealthStates.Invulnerable;
            availability = ResolveAvailability(entity, viewer);
        }
        else
        {
            healthState = WorldHealthStates.Invulnerable;
        }

        return new ProjectedEntityV2(
            entity.EntityId,
            entity.Kind,
            mapInstanceId,
            entity.FloorId,
            WorldAudience.Phase,
            entity.X,
            entity.Y,
            state,
            healthState,
            targetable,
            availability,
            hp,
            maxHp,
            entity.Revision,
            entity.LifeId);
    }

    private string ResolveAvailability(WorldEntityInstance entity, PlayerSession viewer)
    {
        if (string.Equals(
                entity.ClaimPolicy, WorldEntityClaimPolicies.PerCharacter, StringComparison.Ordinal))
        {
            return _claims.IsAvailable(
                    viewer.CharacterId, entity.EntityId, entity.RespawnSeconds)
                ? WorldAvailability.Available
                : WorldAvailability.Cooldown;
        }

        return string.Equals(entity.State, WorldEntityStates.Available, StringComparison.Ordinal)
            ? WorldAvailability.Available
            : WorldAvailability.Cooldown;
    }

    private MobEffectiveStats? ResolveMobStats(WorldEntityInstance entity)
    {
        if (!_combat.Enabled)
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

    private static double Distance(double ax, double ay, double bx, double by) =>
        Math.Sqrt(((bx - ax) * (bx - ax)) + ((by - ay) * (by - ay)));

    private sealed class SessionVisibility
    {
        public object SyncRoot { get; } = new();
        public HashSet<string> Visible { get; } = new(StringComparer.Ordinal);
    }
}
