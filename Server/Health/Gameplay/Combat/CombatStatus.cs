using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// Q-B: a reconnecting or resyncing client has to answer "am I still guarding, is
// the whiff buff up, what is on cooldown, where did my dash land" without
// replaying events that already left the bounded buffer. This is the authoritative
// read model for that question.
//
// It is deliberately not wired to HTTP yet: WorldSnapshotV2.self is a frozen
// required-field object and CombatEventV2 has no status type, and both the v1 and
// v2 contracts forbid quietly added fields (P1_Design_Resolution §3.2). The
// proposal section in Implementation/Work_Orders/Proposals carries the exact
// schema, example and capability shape for review before any wire change.
public sealed record CombatCooldown(string ActionKey, DateTimeOffset EndsAtUtc, bool Active);

public sealed record CombatStatusSnapshot(
    string CharacterId,
    long ServerTick,
    long ActorRevision,
    int Hp,
    int MaxHp,
    int Mp,
    int MaxMp,
    int SwordIntent,
    string GuardPhase,
    string? GuardCastId,
    long? GuardEndExclusiveTick,
    long? WhiffEndExclusiveTick,
    bool CounterReserved,
    long? CounterTick,
    string? CounterOutcome,
    string? CounterSourceEntityId,
    IReadOnlyList<CombatCooldown> Cooldowns,
    DashResolution? LastDash);

public sealed class CombatStatusProjection
{
    private readonly GuardWindowStore _windows;
    private readonly InMemoryCombatV2Service _commands;
    private readonly DashMovementService _dashes;

    public CombatStatusProjection(
        GuardWindowStore windows,
        InMemoryCombatV2Service commands,
        DashMovementService dashes)
    {
        _windows = windows;
        _commands = commands;
        _dashes = dashes;
    }

    public CombatStatusSnapshot Project(PlayerSession actor, long tick, DateTimeOffset nowUtc)
    {
        ArgumentNullException.ThrowIfNull(actor);

        string phase;
        string? guardCastId;
        long? guardEnd;
        long? whiffEnd;
        bool counterReserved;
        long? counterTick;
        string? counterOutcome;
        string? counterSource;
        var withCooldowns = new List<CombatCooldown>();

        lock (actor.SyncRoot)
        {
            var window = _windows.Find(actor.CharacterId);
            if (window is null)
            {
                phase = GuardPhases.None;
            }
            else if (tick < window.GuardEndExclusiveTick)
            {
                phase = GuardPhases.Guard;
            }
            else if (tick < window.WhiffEndExclusiveTick && window.WhiffGranted)
            {
                phase = GuardPhases.Whiff;
            }
            else
            {
                phase = GuardPhases.Expired;
            }

            guardCastId = window?.GuardCastId;
            guardEnd = window?.GuardEndExclusiveTick;
            whiffEnd = window?.WhiffEndExclusiveTick;
            counterReserved = window is { CounterResolved: false };
            counterTick = window is { CounterResolved: false } ? window.CounterTick : null;
            counterOutcome = window?.CounterOutcome;
            counterSource = window?.CounterSourceEntityId;

            // Only report a cooldown the server would still reject on; the
            // action key is the skill id, or BASIC_ATTACK for the basic swing.
            foreach (var actionKey in _commands.TrackedActions(actor.CharacterId))
            {
                if (!_commands.TryGetCooldown(actor.CharacterId, actionKey, out var endsAt))
                {
                    continue;
                }

                var active = nowUtc < endsAt;
                if (active)
                {
                    withCooldowns.Add(new CombatCooldown(actionKey, endsAt, active));
                }
            }
        }

        var lastDash = _dashes.Ledger.All()
            .Where(resolution => string.Equals(
                resolution.CharacterId, actor.CharacterId, StringComparison.Ordinal))
            .OrderByDescending(resolution => resolution.AppliedTick)
            .ThenByDescending(resolution => resolution.ActorRevision)
            .FirstOrDefault();

        return new CombatStatusSnapshot(
            actor.CharacterId,
            tick,
            actor.Revision,
            actor.Hp,
            actor.MaxHp,
            actor.Mp,
            actor.MaxMp,
            actor.SwordIntent,
            phase,
            guardCastId,
            guardEnd,
            whiffEnd,
            counterReserved,
            counterTick,
            counterOutcome,
            counterSource,
            withCooldowns,
            lastDash);
    }
}
