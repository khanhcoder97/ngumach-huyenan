namespace Server.Health.Gameplay.Combat;

// Q-F part 1: the Mãng Cốt encounter as a deterministic state machine.
//
// Sourced invariants (Production_Rules_Complete_v1_vi.md §4 and the QOD-19
// proposal): three phases, thresholds 60% / 30%, damage resolves before the
// phase check, only one phase per impact, at most one boss move resolving at a
// time, priority C → B → A, no loot/unlock on a wipe. Everything numeric that
// the sources do not carry is deliberately absent: there is no HP/ATK/armor,
// no move damage/telegraph/shape and no arena polygon here. Even the phase
// guard duration is injected by the caller, so production has to pass a
// reviewed value and tests pass a labelled fixture.
//
// This type is domain-only: nothing registers it in DI and no route exposes it.
// P00-05 stays BLOCKED until the boss stats, moves and arena exist.
public enum BossEncounterPhase
{
    Idle = 0,
    One = 1,
    Two = 2,
    Three = 3
}

public enum BossEncounterStatus
{
    Idle,
    Active,
    PhaseGuard,
    Defeated
}

public sealed record BossMoveDefinition(string MoveId, int CooldownTicks);

public sealed record BossEncounterRules(int PhaseGuardTicks)
{
    // Production_Rules §4: phase 2 at 60%, phase 3 at 30%.
    public const int Phase2Percent = 60;
    public const int Phase3Percent = 30;

    // Fixed by the same source: when several moves are ready, C wins, then B,
    // then A. No random tie-break.
    public static readonly IReadOnlyList<string> Priority = new[] { "C", "B", "A" };
}

public sealed record BossMoveToken(long Episode, string MoveId);

public static class BossEncounterErrorCodes
{
    public const string AlreadyEngaged = "already_engaged";
    public const string NotEngaged = "not_engaged";
    public const string LifeAlreadyDefeated = "life_already_defeated";
    public const string MoveInFlight = "move_in_flight";
    public const string NoMoveReady = "no_move_ready";
    public const string PhaseGuard = "phase_guard";
    public const string StaleMove = "stale_move";
}

public sealed record BossEngageOutcome(bool Engaged, string? BlockedReason);

public sealed record BossMoveOutcome(BossMoveToken? Token, string? BlockedReason)
{
    public bool Started => Token is not null;
}

public sealed record BossImpactOutcome(
    bool Accepted,
    string? BlockedReason,
    BossEncounterPhase Phase,
    bool PhaseChanged,
    bool Defeated,
    int? PhaseGuardUntilTick)
{
    public static BossImpactOutcome Rejected(
        string code, BossEncounterPhase phase, BossEncounterStatus status) =>
        new(false, code, phase, false, status == BossEncounterStatus.Defeated, null);
}

public sealed class BossEncounter
{
    private readonly BossEncounterRules _rules;
    private readonly IReadOnlyDictionary<string, BossMoveDefinition> _moves;
    private readonly Dictionary<string, int> _cooldownUntilTick = new(StringComparer.Ordinal);

    private long _episode;
    private long _lifeId;
    private long? _defeatedLifeId;
    private BossEncounterPhase _phase = BossEncounterPhase.Idle;
    private BossEncounterStatus _status = BossEncounterStatus.Idle;
    private string? _activeMove;
    private int _phaseGuardUntilTick;

    public BossEncounter(BossEncounterRules rules, IReadOnlyList<BossMoveDefinition> moves)
    {
        ArgumentNullException.ThrowIfNull(rules);
        ArgumentNullException.ThrowIfNull(moves);

        if (rules.PhaseGuardTicks < 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(rules), "PhaseGuardTicks must be zero or greater.");
        }

        if (moves.Count != 3 ||
            !BossEncounterRules.Priority.All(priority =>
                moves.Count(move => string.Equals(move.MoveId, priority, StringComparison.Ordinal)) == 1))
        {
            throw new ArgumentException(
                "The encounter requires exactly one definition for each of A, B and C.",
                nameof(moves));
        }

        foreach (var move in moves)
        {
            if (move.CooldownTicks < 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(moves), $"Move '{move.MoveId}' cooldown must be zero or greater.");
            }
        }

        _rules = rules;
        _moves = moves.ToDictionary(move => move.MoveId, StringComparer.Ordinal);
    }

    public BossEncounterPhase Phase => _phase;

    public BossEncounterStatus Status => _status;

    public long Episode => _episode;

    public long? DefeatedLifeId => _defeatedLifeId;

    // Snapshot read model: how many ticks until this move can be chosen again,
    // and how long the phase guard still blocks any move. Both are pure reads of
    // state the machine already owns, so a snapshot never invents a countdown.
    public int CooldownRemainingTicks(string moveId, int tick)
    {
        if (!_moves.TryGetValue(moveId, out var move))
        {
            throw new ArgumentException($"Unknown move '{moveId}'.", nameof(moveId));
        }

        var cooldownUntil = _cooldownUntilTick.GetValueOrDefault(move.MoveId);
        return Math.Max(0, cooldownUntil - tick);
    }

    public int PhaseGuardRemainingTicks(int tick) =>
        _status == BossEncounterStatus.PhaseGuard
            ? Math.Max(0, _phaseGuardUntilTick - tick)
            : 0;

    public BossEngageOutcome Engage(long lifeId, int tick)
    {
        if (_status is BossEncounterStatus.Active or BossEncounterStatus.PhaseGuard)
        {
            return new BossEngageOutcome(false, BossEncounterErrorCodes.AlreadyEngaged);
        }

        if (_defeatedLifeId == lifeId)
        {
            return new BossEngageOutcome(false, BossEncounterErrorCodes.LifeAlreadyDefeated);
        }

        _lifeId = lifeId;
        _episode++;
        _phase = BossEncounterPhase.One;
        _status = BossEncounterStatus.Active;
        _activeMove = null;
        _phaseGuardUntilTick = 0;
        _cooldownUntilTick.Clear();
        return new BossEngageOutcome(true, null);
    }

    public BossMoveOutcome TryBeginMove(int tick)
    {
        if (_status == BossEncounterStatus.PhaseGuard)
        {
            if (tick < _phaseGuardUntilTick)
            {
                return new BossMoveOutcome(null, BossEncounterErrorCodes.PhaseGuard);
            }

            _status = BossEncounterStatus.Active;
        }

        if (_status != BossEncounterStatus.Active)
        {
            return new BossMoveOutcome(null, BossEncounterErrorCodes.NotEngaged);
        }

        if (_activeMove is not null)
        {
            return new BossMoveOutcome(null, BossEncounterErrorCodes.MoveInFlight);
        }

        foreach (var moveId in BossEncounterRules.Priority)
        {
            var cooldownUntil = _cooldownUntilTick.GetValueOrDefault(moveId);
            if (tick < cooldownUntil)
            {
                continue;
            }

            var move = _moves[moveId];
            _activeMove = moveId;
            _cooldownUntilTick[moveId] = checked(tick + move.CooldownTicks);
            return new BossMoveOutcome(new BossMoveToken(_episode, moveId), null);
        }

        return new BossMoveOutcome(null, BossEncounterErrorCodes.NoMoveReady);
    }

    public BossImpactOutcome ResolveImpact(
        BossMoveToken token, long hp, long maxHp, int tick)
    {
        ArgumentNullException.ThrowIfNull(token);
        if (maxHp <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(maxHp), "maxHp must be positive.");
        }

        if (_status == BossEncounterStatus.PhaseGuard)
        {
            return BossImpactOutcome.Rejected(
                BossEncounterErrorCodes.PhaseGuard, _phase, _status);
        }

        if (_status != BossEncounterStatus.Active)
        {
            return BossImpactOutcome.Rejected(
                BossEncounterErrorCodes.NotEngaged, _phase, _status);
        }

        if (token.Episode != _episode ||
            !string.Equals(token.MoveId, _activeMove, StringComparison.Ordinal))
        {
            return BossImpactOutcome.Rejected(
                BossEncounterErrorCodes.StaleMove, _phase, _status);
        }

        _activeMove = null;

        if (hp <= 0)
        {
            _status = BossEncounterStatus.Defeated;
            _defeatedLifeId = _lifeId;
            return new BossImpactOutcome(
                true, null, _phase, PhaseChanged: false, Defeated: true,
                PhaseGuardUntilTick: null);
        }

        // Damage first, phase second (DEC-022 ordering), and never more than
        // one phase per impact even when a single hit crosses both thresholds.
        var target = PhaseFor(hp, maxHp);
        if (target <= _phase)
        {
            return new BossImpactOutcome(
                true, null, _phase, PhaseChanged: false, Defeated: false,
                PhaseGuardUntilTick: null);
        }

        _phase = (BossEncounterPhase)((int)_phase + 1);
        if (_rules.PhaseGuardTicks == 0)
        {
            return new BossImpactOutcome(
                true, null, _phase, PhaseChanged: true, Defeated: false,
                PhaseGuardUntilTick: null);
        }

        _status = BossEncounterStatus.PhaseGuard;
        _phaseGuardUntilTick = checked(tick + _rules.PhaseGuardTicks);
        return new BossImpactOutcome(
            true, null, _phase, PhaseChanged: true, Defeated: false,
            PhaseGuardUntilTick: _phaseGuardUntilTick);
    }

    // Wipe or leave-ring reset: no loot, no unlock, no lifeId bump here — the
    // caller owns that policy. Bumping the episode makes every token issued
    // before the reset unable to resolve, so a late impact cannot damage or
    // reward the reset encounter.
    public void Reset()
    {
        _episode++;
        _phase = BossEncounterPhase.Idle;
        _status = BossEncounterStatus.Idle;
        _activeMove = null;
        _phaseGuardUntilTick = 0;
        _cooldownUntilTick.Clear();
    }

    private static BossEncounterPhase PhaseFor(long hp, long maxHp)
    {
        var current = Math.Max(0, Math.Min(hp, maxHp));
        if (current * 100 <= maxHp * BossEncounterRules.Phase3Percent)
        {
            return BossEncounterPhase.Three;
        }

        if (current * 100 <= maxHp * BossEncounterRules.Phase2Percent)
        {
            return BossEncounterPhase.Two;
        }

        return BossEncounterPhase.One;
    }
}
