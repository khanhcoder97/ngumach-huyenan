using Server.Health.Contracts;
using Server.Health.Gameplay.Alpha;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// Q-B3 + DEC-DEATH-RETURN-20261105: the server-owned return from a downed state.
//
// The caller may only say "return me" and carries an idempotency key — never a
// destination. Everything the return is made of is server-owned: the anchor comes
// from the approved alpha design (or, without that profile, from the only
// server-owned coordinates the P1 slice has ever had, `P1World:SpawnX/SpawnY`),
// the HP comes from the approved formula, and the cleared state is counted from
// the events actually emitted rather than asserted.
//
// What the decision settles and this file therefore does not choose: the anchor
// [18,0] in MAP_BEN_MUA, HP = max(1, ceil(effectiveMaxHp × 0.5)), MP kept absolute
// and only clamped, three penalties of zero, a 3-second (60-tick) cooldown that
// only a successful apply starts, and a credit key built on the player's own
// death record (PlayerLifeLedger) instead of a minted id. What is still not
// chosen anywhere, because no source defines it: per-map safe anchors other than
// Bến Mưa, and any XP / durability / currency penalty other than zero.
public sealed record DeathReturnOptions
{
    public const string SectionName = "P1:DeathReturn";

    // OFF by default, and the route is not mapped unless P1:AlphaProfile is also
    // on, so a production boot answers 404 rather than 503.
    public bool Enabled { get; set; }

    // DEV FIXTURE for the pre-alpha shape only: returning a downed actor to the
    // map spawn point without restoring anything is still a useful integration
    // test, and zero means "relocate and clear combat state, leave HP alone".
    // Under P1:AlphaProfile it must stay zero — the approved formula owns the
    // returned HP there, and DeathReturnOptionsValidator refuses the pair.
    public int RestoreHpFixture { get; set; }
}

public static class DeathReturnOptionsValidator
{
    public static void Validate(
        DeathReturnOptions options, P1WorldOptions world, bool alphaProfileEnabled)
    {
        if (options.RestoreHpFixture < 0)
        {
            throw new InvalidOperationException(
                "P1:DeathReturn:RestoreHpFixture must be zero or greater " +
                "(zero means the return restores nothing).");
        }

        // DEC-DEATH-RETURN-20261105 gates.alphaWithPositiveRestoreHpFixture: the
        // formula and a fixture cannot both decide the returned HP, and the
        // formula is the approved answer.
        if (alphaProfileEnabled && options.RestoreHpFixture != 0)
        {
            throw new InvalidOperationException(
                $"P1:DeathReturn:RestoreHpFixture {options.RestoreHpFixture} must be 0 while " +
                "P1:AlphaProfile:Enabled=true: DEC-DEATH-RETURN-20261105 fixes the returned HP " +
                "as max(1,ceil(currentEffectiveMaxHp*0.5)), so a fixture value would silently " +
                "override the approved formula.");
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
    public const string Cooldown = "death_return_cooldown";
    public const string KeyConflict = "idempotency_key_conflict";
}

// The whole answer a return gives, sized to the approved response so the handler
// is a mapping rather than a second decision. `InflightCastsCancelled` and
// `ReservedCountersCancelled` are counted from the events the engine actually
// emitted, so a cleared thing is never reported as cleared when it was not.
public sealed record DeathReturnResult(
    bool Applied,
    bool Replayed,
    string? ErrorCode,
    string? SessionId,
    string? CharacterId,
    string? MapId,
    double X,
    double Y,
    int Hp,
    int MaxHp,
    int Mp,
    int MaxMp,
    long Revision,
    long ServerTick,
    int InflightCastsCancelled,
    int ReservedCountersCancelled,
    bool GuardWindowClosed,
    bool MovementTimingReset,
    long? NextReturnAllowedAtTick,
    string? DeathEventId,
    int NewLifeVersion);

public sealed class DeathReturnService
{
    // Superseding a life does not expire its keys; only a proven expiry may release a receipt.
    public const int LedgerCapacity = 256;

    private int _receiptsHeldPastBound;

    // How many times a receipt had to be kept past the bound. Exposed so the growth is an
    // observation with a number attached rather than an invisible leak.
    public int ReceiptsHeldPastBound
    {
        get
        {
            lock (_ledgerSync)
            {
                return _receiptsHeldPastBound;
            }
        }
    }

    private readonly ISessionStore _sessions;
    private readonly MapBoundsCatalog _bounds;
    private readonly P1WorldOptions _world;
    private readonly DeathReturnOptions _options;
    private readonly GuardWindowStore _windows;
    private readonly CombatTickEngine _engine;
    private readonly PlayerLifeLedger _lives;
    private readonly IServerClock _clock;
    private readonly AlphaDeathReturnRules? _alpha;
    private readonly object _ledgerSync = new();
    private readonly Dictionary<string, (string CharacterId, DeathReturnResult Result)> _ledger =
        new(StringComparer.Ordinal);
    private readonly Dictionary<string, long> _cooldownUntilTick = new(StringComparer.Ordinal);

    public DeathReturnService(
        ISessionStore sessions,
        MapBoundsCatalog bounds,
        P1WorldOptions world,
        DeathReturnOptions options,
        GuardWindowStore windows,
        CombatTickEngine engine,
        PlayerLifeLedger lives,
        IServerClock clock,
        AlphaDeathReturnRules? alpha)
    {
        _sessions = sessions;
        _bounds = bounds;
        _world = world;
        _options = options;
        _windows = windows;
        _engine = engine;
        _lives = lives;
        _clock = clock;
        _alpha = alpha;
    }

    public bool Enabled => _options.Enabled;

    // The cooldown window comes from the alpha design and nowhere else: without
    // that profile there is no source for a return cooldown, so the pre-alpha
    // dev-fixture path keeps its original "one credit per idempotency key" rule
    // and never refuses for timing.
    public int CooldownTicks =>
        _alpha is { } rules ? rules.NewDeathReturnCooldownSeconds * ServerClock.TicksPerSecond : 0;

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

        // DEC-DEATH-RETURN-20261105 replay.ordering: the request and its owner are
        // established first, then the receipt lookup, and only after that the
        // state guards (not_downed, cooldown). So a key that already committed
        // always answers with what it committed, whatever the actor looks like now.
        var actor = _sessions.Find(sessionId);
        if (actor is null)
        {
            return Rejected(DeathReturnErrorCodes.UnknownSession);
        }

        if (idempotencyKey is not { Length: 32 } || !P1Validation.IsHex32(idempotencyKey))
        {
            return Rejected(DeathReturnErrorCodes.InvalidKey, actor);
        }

        lock (_ledgerSync)
        {
            // Same key, same character: the recorded answer, applied exactly once.
            // Same key presented by a different character: refused outright rather
            // than letting one client's key move another actor.
            if (_ledger.TryGetValue(idempotencyKey, out var prior))
            {
                // A replay never heals, never moves, never advances the life
                // counter and never restarts the cooldown. It repeats the committed
                // snapshot verbatim - including its serverTick and revision, which
                // is why the decision tells the client to fresh-read the world
                // instead of treating a receipt as current state - and it answers
                // applied=false/replayed=true so no consumer can read the second
                // arrival as a second return.
                return prior.CharacterId == actor.CharacterId
                    ? prior.Result with { Applied = false, Replayed = true }
                    : Rejected(DeathReturnErrorCodes.KeyConflict, actor);
            }

            return _engine.SerializeActor(actor, () =>
            {
                if (!_bounds.TryResolve(actor.MapId, out var bounds) ||
                    (_alpha is { } rules &&
                     !string.Equals(actor.MapId, rules.MapId, StringComparison.Ordinal)))
                {
                    return Rejected(DeathReturnErrorCodes.UnknownMap, actor);
                }

                var result = Apply(actor, bounds);
                if (!result.Applied)
                {
                    return result;
                }

                _ledger[idempotencyKey] = (actor.CharacterId, result);
                if (_ledger.Count > LedgerCapacity)
                {
                    _receiptsHeldPastBound++;
                }

                return result;
            });
        }
    }

    private DeathReturnResult Apply(PlayerSession actor, MapBounds bounds)
    {
        double anchorX;
        double anchorY;
        int hpBefore;
        int hpAfter;
        long revisionAfter;
        long applyTick;
        long? nextAllowedAtTick;
        int newLifeVersion;
        PlayerDeathRecord? death;
        var rules = _alpha;

        lock (actor.SyncRoot)
        {
            if (actor.Hp > 0)
            {
                return Rejected(DeathReturnErrorCodes.NotDowned, actor);
            }

            applyTick = _clock.Tick;
            if (_cooldownUntilTick.TryGetValue(actor.CharacterId, out var blockedUntil) &&
                applyTick < blockedUntil)
            {
                // Refusing does not extend the window and does not run any of the
                // cleanup below, so a retry after the deadline sees the same world
                // the first attempt would have.
                return Rejected(DeathReturnErrorCodes.Cooldown, actor, blockedUntil);
            }

            // The anchor is server-owned in both shapes: the approved alpha
            // anchor, or the only coordinate pair the P1 slice published before
            // that decision existed. Clamped into the actor's own map bounds,
            // never taken from the request.
            anchorX = Math.Clamp(rules?.AnchorX ?? _world.SpawnX, bounds.XMin, bounds.XMax);
            anchorY = Math.Clamp(rules?.AnchorY ?? _world.SpawnY, bounds.YMin, bounds.YMax);
            actor.X = anchorX;
            actor.Y = anchorY;

            death = _lives.LatestDeath(actor.CharacterId);
            hpBefore = actor.Hp;
            if (rules is not null)
            {
                // DEC-DEATH-RETURN-20261105 restoreHp: max(1, ceil(current
                // EffectiveMaxHp × 0.5)). currentEffectiveMaxHp is actor.MaxHp
                // because no source yet adds equipment stats to the aggregate
                // (equipment stays metadata-only), so this is the whole formula,
                // not an approximation of a bigger one.
                hpAfter = Math.Max(1, (int)Math.Ceiling(actor.MaxHp * 0.5));
            }
            else if (_options.RestoreHpFixture > 0)
            {
                hpAfter = Math.Min(actor.MaxHp, _options.RestoreHpFixture);
            }
            else
            {
                hpAfter = hpBefore;
            }

            actor.Hp = hpAfter;
            // restoreMp: keep the current absolute value and clamp it. Nothing
            // restores MP — no source says a return refills it.
            actor.Mp = Math.Clamp(actor.Mp, 0, actor.MaxMp);
            // design.clear "movement held intent" has no queue to drain: /p1/move
            // integrates an elapsed window from LastMoveAtUtc and commits, so the
            // only sourced equivalent is restarting that window here, exactly as
            // the teleport path already does.
            actor.LastMoveAtUtc = _clock.UtcNow;
            actor.Revision++;
            hpAfter = actor.Hp;
            revisionAfter = actor.Revision;
            // The life that ends here is numbered by the same ledger the damage
            // paths write, so a resurrection advances it exactly once and a
            // replay (which never reaches Apply) never does.
            newLifeVersion = _lives.RecordResurrectionCommit(
                actor.CharacterId, hpBefore, hpAfter);
            var cooldownTicks = CooldownTicks;
            nextAllowedAtTick = cooldownTicks > 0 ? applyTick + cooldownTicks : null;
        }

        // A return is a fresh start for the fight: no inherited guard window,
        // no counter that would swing at something the actor can no longer see,
        // no cast still pending on the previous life's coordinates.
        // Aggro needs no ledger of its own — mob targeting is recomputed each
        // tick and skips a downed player, so a mob mid-telegraph drops the
        // pending impact as soon as it has no target.
        var guardWasOpen = _windows.FindAny(actor.CharacterId) is { IsOpen: true };
        _windows.Close(actor.CharacterId, GuardWindowEndReasons.DefenderDown);
        var cancelled = _engine.CancelPendingFor(actor.CharacterId);
        // Each abandoned cast emits CANCEL then END; a reserved counter emits a
        // single CANCEL. Counting the pair apart is what makes these two numbers
        // measurements of the events the client will read, not assertions.
        var endCount = cancelled.Count(cancelledEvent =>
            cancelledEvent.Type == CombatEventTypesV2.End);
        var cancelCount = cancelled.Count(cancelledEvent =>
            cancelledEvent.Type == CombatEventTypesV2.Cancel);

        if (nextAllowedAtTick is { } until)
        {
            foreach (var expiredCharacter in _cooldownUntilTick
                         .Where(entry => entry.Value <= applyTick)
                         .Select(entry => entry.Key).ToArray())
            {
                _cooldownUntilTick.Remove(expiredCharacter);
            }

            _cooldownUntilTick[actor.CharacterId] = until;
        }

        return new DeathReturnResult(
            Applied: true,
            Replayed: false,
            ErrorCode: null,
            SessionId: actor.SessionId,
            CharacterId: actor.CharacterId,
            MapId: actor.MapId,
            X: anchorX,
            Y: anchorY,
            Hp: hpAfter,
            MaxHp: actor.MaxHp,
            Mp: actor.Mp,
            MaxMp: actor.MaxMp,
            Revision: revisionAfter,
            ServerTick: applyTick,
            InflightCastsCancelled: endCount,
            ReservedCountersCancelled: Math.Max(0, cancelCount - endCount),
            GuardWindowClosed: guardWasOpen,
            MovementTimingReset: true,
            NextReturnAllowedAtTick: nextAllowedAtTick,
            DeathEventId: death?.DeathEventId,
            NewLifeVersion: newLifeVersion);
    }

    private DeathReturnResult Rejected(
        string errorCode, PlayerSession? actor = null, long? nextAllowedAtTick = null)
    {
        // The cooldown deadline travels with the refusal it describes, so a
        // client can schedule its retry from the server's tick instead of
        // guessing how long a "retryable" 422 meant.
        nextAllowedAtTick ??= actor is { } known && _cooldownUntilTick.TryGetValue(
            known.CharacterId, out var knownUntil)
            ? knownUntil
            : null;

        return new DeathReturnResult(
            Applied: false,
            Replayed: false,
            ErrorCode: errorCode,
            SessionId: actor?.SessionId,
            CharacterId: actor?.CharacterId,
            MapId: actor?.MapId,
            X: actor?.X ?? 0,
            Y: actor?.Y ?? 0,
            Hp: actor?.Hp ?? 0,
            MaxHp: actor?.MaxHp ?? 0,
            Mp: actor?.Mp ?? 0,
            MaxMp: actor?.MaxMp ?? 0,
            Revision: actor?.Revision ?? 0,
            ServerTick: _clock.Tick,
            InflightCastsCancelled: 0,
            ReservedCountersCancelled: 0,
            GuardWindowClosed: false,
            MovementTimingReset: false,
            NextReturnAllowedAtTick: nextAllowedAtTick,
            DeathEventId: actor is null ? null : _lives.LatestDeath(actor.CharacterId)?.DeathEventId,
            NewLifeVersion: actor is null ? 1 : _lives.LifeVersion(actor.CharacterId));
    }
}
