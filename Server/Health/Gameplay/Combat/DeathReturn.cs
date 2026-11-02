using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// Q-B3: server-owned return from a downed state for the P1 slice.
//
// There is deliberately no HTTP surface yet: a request/response pair for this is
// a wire change, and the fields the rule depends on are not in canonical content
// (see the DeathReturn section of the QOD-18 proposal). The work order says to
// record the missing sources, ship a labelled DEV fixture behind an OFF gate, and
// refuse client-chosen coordinates — which is exactly what this does: the caller
// may only say "return me" and carries an idempotency key, never a destination.
//
// Proven here: only a downed actor on a map with known bounds is returned, exactly
// once per idempotency key, only to the server's own anchor, with the guard
// window closed, the in-flight casts cancelled and the reserved counter cancelled
// — all as events the client already polls. Not chosen here, because no source
// exists: per-map safe anchors, any XP / durability / currency penalty, and
// whether returning restores HP at all.
public sealed record DeathReturnOptions
{
    public const string SectionName = "P1:DeathReturn";

    // DEV FIXTURE, OFF by default. Returning a downed actor to the map spawn
    // point reuses the only server-owned coordinates the P1 slice actually has.
    public bool Enabled { get; set; }

    // DEV FIXTURE: Production_Rules §3 carries no restore-on-return value, so
    // nothing is restored unless an operator configures the existing starting HP.
    // Zero means the return relocates and clears combat state but leaves HP alone.
    public int RestoreHpFixture { get; set; }
}

public static class DeathReturnOptionsValidator
{
    public static void Validate(DeathReturnOptions options, P1WorldOptions world)
    {
        if (options.RestoreHpFixture < 0)
        {
            throw new InvalidOperationException(
                "P1:DeathReturn:RestoreHpFixture must be zero or greater " +
                "(zero means the return restores nothing).");
        }

        if (options.RestoreHpFixture > world.StartingMaxHp)
        {
            throw new InvalidOperationException(
                $"P1:DeathReturn:RestoreHpFixture {options.RestoreHpFixture} exceeds " +
                $"P1World:StartingMaxHp {world.StartingMaxHp}; no source allows a return " +
                "to put an actor above its starting HP yet.");
        }
    }
}

public static class DeathReturnErrorCodes
{
    public const string Disabled = "death_return_disabled";
    public const string UnknownSession = "unknown_session";
    public const string InvalidKey = "invalid_idempotency_key";
    public const string UnknownMap = "unknown_map";
    public const string NotDowned = "not_downed";
    public const string KeyConflict = "idempotency_key_conflict";
}

public sealed record DeathReturnResult(
    bool Applied,
    bool Replayed,
    string? ErrorCode,
    string? SessionId,
    string? CharacterId,
    double X,
    double Y,
    int Hp,
    long Revision,
    int CancelledEventCount);

public sealed class DeathReturnService
{
    // Bounded so a long-lived process cannot grow the ledger with session count;
    // a key older than the window is a fresh request, which is acceptable because
    // the return itself is idempotent on actor state (an already-returned actor is
    // no longer downed and gets NotDowned rather than a second move).
    public const int LedgerCapacity = 256;

    private readonly ISessionStore _sessions;
    private readonly MapBoundsCatalog _bounds;
    private readonly P1WorldOptions _world;
    private readonly DeathReturnOptions _options;
    private readonly GuardWindowStore _windows;
    private readonly CombatTickEngine _engine;
    private readonly object _ledgerSync = new();
    private readonly Dictionary<string, (string CharacterId, DeathReturnResult Result)> _ledger =
        new(StringComparer.Ordinal);
    private readonly Queue<string> _ledgerOrder = new();

    public DeathReturnService(
        ISessionStore sessions,
        MapBoundsCatalog bounds,
        P1WorldOptions world,
        DeathReturnOptions options,
        GuardWindowStore windows,
        CombatTickEngine engine)
    {
        _sessions = sessions;
        _bounds = bounds;
        _world = world;
        _options = options;
        _windows = windows;
        _engine = engine;
    }

    public bool Enabled => _options.Enabled;

    public int LedgerCount
    {
        get
        {
            lock (_ledgerSync)
            {
                return _ledger.Count;
            }
        }
    }

    public DeathReturnResult ReturnToAnchor(string sessionId, string? idempotencyKey)
    {
        if (!_options.Enabled)
        {
            return Rejected(DeathReturnErrorCodes.Disabled);
        }

        var actor = _sessions.Find(sessionId);
        if (actor is null)
        {
            return Rejected(DeathReturnErrorCodes.UnknownSession);
        }

        if (idempotencyKey is not { Length: 32 } || !P1Validation.IsHex32(idempotencyKey))
        {
            return Rejected(DeathReturnErrorCodes.InvalidKey, actor);
        }

        if (!_bounds.TryResolve(actor.MapId, out var bounds))
        {
            return Rejected(DeathReturnErrorCodes.UnknownMap, actor);
        }

        lock (_ledgerSync)
        {
            // Same key, same character: the recorded answer, applied exactly once.
            // Same key presented by a different character: refused outright rather
            // than letting one client's key move another actor.
            if (_ledger.TryGetValue(idempotencyKey, out var prior))
            {
                return prior.CharacterId == actor.CharacterId
                    ? prior.Result with { Replayed = true }
                    : Rejected(DeathReturnErrorCodes.KeyConflict, actor);
            }

            var result = Apply(actor, bounds);
            if (!result.Applied)
            {
                // A refusal changed nothing, so the same key stays valid for the
                // retry once the actor is actually downed.
                return result;
            }

            _ledger[idempotencyKey] = (actor.CharacterId, result);
            _ledgerOrder.Enqueue(idempotencyKey);
            while (_ledgerOrder.Count > LedgerCapacity && _ledgerOrder.TryDequeue(out var oldest))
            {
                _ledger.Remove(oldest!);
            }

            return result;
        }
    }

    private DeathReturnResult Apply(PlayerSession actor, MapBounds bounds)
    {
        double anchorX;
        double anchorY;
        int hpAfter;
        long revisionAfter;

        // Only the actor's own state is written under the actor lock. The
        // cleanup below reaches into the tick engine, and the tick loop takes the
        // engine lock before the actor lock, so holding both here would invert
        // that order.
        lock (actor.SyncRoot)
        {
            if (actor.Hp > 0)
            {
                return Rejected(DeathReturnErrorCodes.NotDowned, actor);
            }

            // The anchor is server-owned: the only coordinate pair the P1 slice
            // publishes as a spawn point, clamped into the actor's own map bounds.
            anchorX = Math.Clamp(_world.SpawnX, bounds.XMin, bounds.XMax);
            anchorY = Math.Clamp(_world.SpawnY, bounds.YMin, bounds.YMax);
            actor.X = anchorX;
            actor.Y = anchorY;
            if (_options.RestoreHpFixture > 0)
            {
                actor.Hp = Math.Min(actor.MaxHp, _options.RestoreHpFixture);
            }

            actor.Revision++;
            hpAfter = actor.Hp;
            revisionAfter = actor.Revision;
        }

        // A return is a fresh start for the fight: no inherited guard window,
        // no counter that would swing at something the actor can no longer see,
        // no cast still pending on the previous life's coordinates.
        // Aggro needs no ledger of its own — mob targeting is recomputed each
        // tick and skips a downed player, so a mob mid-telegraph drops the
        // pending impact as soon as it has no target.
        _windows.Close(actor.CharacterId, GuardWindowEndReasons.DefenderDown);
        var cancelled = _engine.CancelPendingFor(actor.CharacterId);

        return new DeathReturnResult(
            Applied: true,
            Replayed: false,
            ErrorCode: null,
            SessionId: actor.SessionId,
            CharacterId: actor.CharacterId,
            X: anchorX,
            Y: anchorY,
            Hp: hpAfter,
            Revision: revisionAfter,
            CancelledEventCount: cancelled.Count);
    }

    private static DeathReturnResult Rejected(string errorCode, PlayerSession? actor = null) =>
        new(
            Applied: false,
            Replayed: false,
            ErrorCode: errorCode,
            SessionId: actor?.SessionId,
            CharacterId: actor?.CharacterId,
            X: actor?.X ?? 0,
            Y: actor?.Y ?? 0,
            Hp: actor?.Hp ?? 0,
            Revision: actor?.Revision ?? 0,
            CancelledEventCount: 0);
}
