using System.Collections.Concurrent;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// DEC-022 runtime (docs/production/P1_Guard_Precision_20261030_vi.md). One
// guard window per character, opened when SK-MK-01 is accepted and resolved on
// the authoritative 20 Hz tick: guard [T,T+8) at 0.70 DR inside the front
// region, one confirmation and +2 Kiếm Ý per guardCastId, a counter reserved
// against the confirming source that resolves on the next tick, and a whiff
// buff of 0.20 DR for [T+8,T+28) only when the window expired naturally with no
// confirmation while the defender was alive.
public static class GuardPhases
{
    public const string None = "NONE";
    public const string Guard = "GUARD";
    public const string Whiff = "WHIFF";
    public const string Expired = "EXPIRED";
}

public static class GuardWindowEndReasons
{
    public const string None = "NONE";
    public const string DefenderDown = "DEFENDER_DOWN";
    public const string MapOrFloorChange = "MAP_OR_FLOOR_CHANGE";
}

// The incoming-damage policy the defender gets for one impact.
public sealed record GuardIncoming(
    string Phase,
    double DamageReduction,
    bool FrontHit,
    bool CounterEligible);

public sealed record GuardConfirmation(
    string GuardCastId,
    string ConfirmationEventId,
    string CounterSourceEntityId,
    long CounterSourceLifeId,
    long CounterTick,
    int SwordIntentAfter);

public sealed class GuardWindowState
{
    public required PlayerSession Defender { get; init; }
    public required string SessionId { get; init; }
    public required string GuardCastId { get; init; }
    public required long CastStartTick { get; init; }
    public required double FacingX { get; init; }
    public required double FacingY { get; init; }
    public required double AttackSnapshot { get; init; }
    public required double CounterCoefficient { get; init; }
    public required string MapId { get; init; }
    public required string FloorId { get; init; }

    public int GuardDurationTicks { get; init; }
    public int WhiffDurationTicks { get; init; }

    public long GuardEndExclusiveTick => CastStartTick + GuardDurationTicks;

    public long WhiffEndExclusiveTick => GuardEndExclusiveTick + WhiffDurationTicks;

    public int ConfirmationCount { get; set; }
    public string? ConfirmationEventId { get; set; }
    public string? CounterSourceEntityId { get; set; }
    public long? CounterSourceLifeId { get; set; }
    public long? CounterTick { get; set; }
    public bool CounterResolved { get; set; }
    public string? CounterOutcome { get; set; }
    public bool WhiffGranted { get; set; }
    public string EndReason { get; set; } = GuardWindowEndReasons.None;

    public bool IsOpen => EndReason == GuardWindowEndReasons.None;
}

// One window per character; a new cast refreshes it (DEC-022 stacking
// SAME_SKILL_REFRESH_NO_ADD) instead of adding a second reduction source.
public sealed class GuardWindowStore
{
    private readonly ConcurrentDictionary<string, GuardWindowState> _windows =
        new(StringComparer.Ordinal);

    public int Count => _windows.Count;

    public GuardWindowState? Find(string characterId) =>
        _windows.TryGetValue(characterId, out var window) && window.IsOpen
            ? window
            : null;

    // A reserved counter always gets resolved on its tick — even when the
    // window has since closed (defender down, map change) — so the client sees
    // one CANCEL instead of a silently dropped outcome.
    public IReadOnlyList<GuardWindowState> PendingCounters(long tick)
    {
        var pending = new List<GuardWindowState>();
        foreach (var window in _windows.Values)
        {
            if (!window.CounterResolved && window.CounterTick == tick &&
                window.CounterSourceEntityId is not null)
            {
                pending.Add(window);
            }
        }

        return pending;
    }

    public GuardWindowState Open(GuardWindowState window)
    {
        _windows[window.Defender.CharacterId] = window;
        return window;
    }

    // Death or a map change closes the window: it stops paying reduction,
    // never grants the whiff reward, and leaves a reserved counter to be
    // cancelled exactly once on its own tick. DEC-022 §3 zeroes the resource
    // only on death; a map change keeps what the character already earned.
    public void Close(string characterId, string reason)
    {
        if (!_windows.TryGetValue(characterId, out var window))
        {
            return;
        }

        lock (window.Defender.SyncRoot)
        {
            window.EndReason = reason;
            window.WhiffGranted = false;
            if (reason == GuardWindowEndReasons.DefenderDown)
            {
                window.Defender.SwordIntent = 0;
            }
        }
    }
}

// Incoming-damage side of DEC-022: how much of a mob swing the guard eats, and
// whether that swing is the direct-melee front hit that reserves a counter.
public sealed class GuardDefenseService
{
    private readonly GuardWindowStore _windows;
    private readonly CombatDamageFeature _combat;
    private readonly CombatEventStore _events;

    public GuardDefenseService(
        GuardWindowStore windows,
        CombatDamageFeature combat,
        CombatEventStore events)
    {
        _windows = windows;
        _combat = combat;
        _events = events;
    }

    public GuardIncoming EvaluateIncoming(
        string? characterId, long tick, double sourceX, double sourceY)
    {
        if (characterId is null || !_combat.Enabled ||
            _windows.Find(characterId) is not { } window)
        {
            return NoGuard;
        }

        var guard = _combat.GuardPrecision.Guard;
        var defender = window.Defender;
        lock (defender.SyncRoot)
        {
            CloseOnEnvironmentChange(window, defender);
            if (!window.IsOpen)
            {
                return NoGuard;
            }

            if (tick < window.GuardEndExclusiveTick)
            {
                var front = GuardTimeline.InFront(
                    defender.X, defender.Y,
                    window.FacingX, window.FacingY,
                    sourceX, sourceY,
                    guard.RangeWu, guard.AngleDegrees);

                // Only direct damage from the front region gets the 70%; a hit
                // from behind is plain damage and never confirms (DEC-022 §2).
                return front
                    ? new GuardIncoming(GuardPhases.Guard, guard.DamageReduction, FrontHit: true, true)
                    : new GuardIncoming(GuardPhases.Guard, 0, FrontHit: false, CounterEligible: false);
            }

            if (tick >= window.WhiffEndExclusiveTick)
            {
                return new GuardIncoming(GuardPhases.Expired, 0, FrontHit: false, CounterEligible: false);
            }

            if (!TryGrantWhiff(window, defender))
            {
                return NoGuard;
            }

            // The whiff buff sits in the normal DR bucket and applies to all
            // incoming damage; it never confirms a counter.
            return new GuardIncoming(
                GuardPhases.Whiff,
                _combat.GuardPrecision.Whiff.DamageReduction,
                FrontHit: false,
                CounterEligible: false);
        }
    }

    // DEC-022 §3: the root damage resolves first, then survival decides. A lethal
    // hit means death cleanup, zero resource, no confirmation and no counter.
    public GuardConfirmation? CommitConfirmation(
        string? characterId,
        WorldEntityInstance source,
        long tick,
        DateTimeOffset atUtc,
        bool defenderSurvived)
    {
        if (characterId is null || !_combat.Enabled ||
            _windows.Find(characterId) is not { } window)
        {
            return null;
        }

        var guard = _combat.GuardPrecision.Guard;
        var defender = window.Defender;
        lock (defender.SyncRoot)
        {
            CloseOnEnvironmentChange(window, defender);
            if (!window.IsOpen)
            {
                return null;
            }

            if (!defenderSurvived)
            {
                window.EndReason = GuardWindowEndReasons.DefenderDown;
                defender.SwordIntent = 0;
                return null;
            }

            if (tick >= window.GuardEndExclusiveTick ||
                window.ConfirmationCount >= guard.MaxConfirmations)
            {
                // Later hits inside the window keep the 70% but never pay again
                // (one confirmation, one +2, one counter per guardCastId).
                return null;
            }

            if (!GuardTimeline.InFront(
                    defender.X, defender.Y,
                    window.FacingX, window.FacingY,
                    source.X, source.Y,
                    guard.RangeWu, guard.AngleDegrees))
            {
                return null;
            }

            window.ConfirmationCount++;
            window.CounterSourceEntityId = source.EntityId;
            window.CounterSourceLifeId = source.LifeId;
            window.CounterTick = tick + _combat.GuardPrecision.Counter.DelayTicks;
            defender.SwordIntent = Math.Min(
                guard.SwordIntentCap, defender.SwordIntent + guard.SwordIntentGain);

            var confirmation = _events.Append(
                window.SessionId,
                new CombatEventV2(
                    Guid.NewGuid().ToString("N"),
                    CombatEventTypesV2.CounterConfirmed,
                    window.GuardCastId,
                    defender.CharacterId,
                    source.EntityId,
                    source.LifeId,
                    null,
                    defender.MapId + WorldAudience.MapInstanceSuffix,
                    defender.FloorId,
                    defender.Revision,
                    null,
                    tick,
                    atUtc,
                    Result: null));

            window.ConfirmationEventId = confirmation.EventId;
            return new GuardConfirmation(
                window.GuardCastId,
                confirmation.EventId,
                source.EntityId,
                source.LifeId,
                window.CounterTick ?? tick,
                defender.SwordIntent);
        }
    }

    private static bool TryGrantWhiff(GuardWindowState window, PlayerSession defender)
    {
        if (window.ConfirmationCount > 0)
        {
            // A successful guard has no whiff buff at all.
            return false;
        }

        if (defender.Hp <= 0)
        {
            window.EndReason = GuardWindowEndReasons.DefenderDown;
            defender.SwordIntent = 0;
            return false;
        }

        window.WhiffGranted = true;
        return true;
    }

    private static void CloseOnEnvironmentChange(GuardWindowState window, PlayerSession defender)
    {
        if (!window.IsOpen)
        {
            return;
        }

        if (!string.Equals(defender.MapId, window.MapId, StringComparison.Ordinal) ||
            !string.Equals(defender.FloorId, window.FloorId, StringComparison.Ordinal))
        {
            window.EndReason = GuardWindowEndReasons.MapOrFloorChange;
            window.WhiffGranted = false;
        }
    }

    private static GuardIncoming NoGuard =>
        new(GuardPhases.None, 0, FrontHit: false, CounterEligible: false);
}
