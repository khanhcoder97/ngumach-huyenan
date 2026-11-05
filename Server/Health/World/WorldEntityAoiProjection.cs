using System.Collections.Concurrent;
using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Interactions;

namespace Server.Health.World;

// QOD-16 phase 2 audience policy (owner decision Q6): the v2 snapshot exposes
// MOB/BOSS/NPC/GATHER_NODE/INTERACTABLE after an AOI filter — enter 40 WU,
// leave at 48 WU (8 WU hysteresis) from Online_Persistence_Release_Complete
// §2 — within the same map instance/floor/phase. The internal read model sees every
// candidate the registry holds; a client receives only the visible subset. The instance
// label is always mapId + "#1" and the phase is the constant OPEN_WORLD, so nothing in
// this filter is encounter-aware - the Mãng Cốt fight scopes by its own quest-attempt
// instance rather than through these two constants.
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
    private readonly MobCombatStateStore _states;
    private readonly ICombatBossBridge? _bosses;
    private readonly INpcEscortPositionSource? _npcPositions;
    private readonly ConcurrentDictionary<string, SessionVisibility> _visibility =
        new(StringComparer.Ordinal);

    public WorldAoiProjectionService(
        WorldEntityRegistry entities,
        MobLifecycleService mobs,
        CombatDamageFeature combat,
        GatherClaimStore claims,
        MobCombatStateStore states,
        ICombatBossBridge? bosses = null,
        INpcEscortPositionSource? npcPositions = null)
    {
        _entities = entities;
        _mobs = mobs;
        _combat = combat;
        _claims = claims;
        _states = states;
        _bosses = bosses;
        _npcPositions = npcPositions;
    }

    // The position an audience member is shown for an NPC: the escort domain's live
    // position when this viewer is the one escorting that actor, otherwise the canonical
    // anchor. Both the AOI distance test and the projected coordinates go through here, so
    // a walking NPC cannot be visible at its anchor while being reported somewhere else.
    private (double X, double Y) EscortPosition(WorldEntityInstance entity, PlayerSession viewer)
    {
        if (_npcPositions is { } positions &&
            positions.TryGetEscortPosition(
                viewer.CharacterId, out var escortedEntityId, out var x, out var y) &&
            string.Equals(entity.EntityId, escortedEntityId, StringComparison.Ordinal))
        {
            return (x, y);
        }

        return (entity.X, entity.Y);
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
                var (positionX, positionY) = EscortPosition(entity, viewer);
                if (Distance(positionX, positionY, viewer.X, viewer.Y) > limit)
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

        // The alpha boss encounter is owner-scoped, so only the registered owner
        // has an audience view of it; everyone else keeps the blocked policy.
        BossEncounterAudience? bossAudience = null;
        if (isBoss && _bosses is not null &&
            _bosses.TryGetAudience(viewer.CharacterId, entity, out var audience))
        {
            bossAudience = audience;
        }

        var state = isMob || isBoss
            ? _mobs.GetState(entity.EntityId)
            : entity.State;
        if (bossAudience?.Defeated == true)
        {
            state = MobBehaviorStates.Dead;
        }

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
            var knownMaxHp = stats?.Hp ?? 0;
            // A mob the audience cannot resolve stats for is not "alive at 0 HP":
            // ResolveHit skips any target whose max HP is unknown, so a cast
            // accepted at it produces no event at all. Report BLOCKED and not
            // targetable, the same policy the boss branch uses, instead of
            // advertising a target the engine will silently not resolve. The
            // behaviour state (IDLE/CHASE/TELEGRAPH …) still travels untouched —
            // it is real, it is only the health numbers that are unavailable.
            healthState = dead
                ? WorldHealthStates.Dead
                : knownMaxHp > 0 ? WorldHealthStates.Alive : WorldHealthStates.Blocked;
            targetable = !dead && knownMaxHp > 0;
            var lifeState = _states.TryGet(entity.EntityId, entity.LifeId);
            hp = dead || knownMaxHp <= 0 ? 0 : lifeState?.Hp ?? knownMaxHp;
            maxHp = knownMaxHp;
        }
        else if (isBoss)
        {
            // A boss with no encounter for this viewer stays BOSSDATA_BLOCKED:
            // it is not shown as dead and is not targetable. The owner of a live
            // encounter gets the same view the cast path will accept, so the
            // audience never advertises a target the engine would refuse.
            healthState = WorldHealthStates.Blocked;
            if (bossAudience is { } owned)
            {
                healthState = owned.Defeated
                    ? WorldHealthStates.Dead
                    : WorldHealthStates.Alive;
                targetable = owned.Targetable;
                hp = owned.Hp;
                maxHp = owned.MaxHp;
            }
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
            EscortPosition(entity, viewer).X,
            EscortPosition(entity, viewer).Y,
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
