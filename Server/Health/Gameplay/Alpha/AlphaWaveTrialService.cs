using Server.Health.Gameplay.Combat;
using Server.Health.Gameplay.Quests;
using Server.Health.World;

namespace Server.Health.Gameplay.Alpha;

public static class WaveTrialOutcomes
{
    public const string Credit = "CREDIT";
    public const string Hit = "HIT";
    public const string DamageBlocked = "DAMAGE_BLOCKED";
    public const string Cancelled = "CANCELLED";
}

public sealed record WaveTrialResolution(
    string CharacterId,
    string Outcome,
    int Damage,
    int HpBefore,
    int HpAfter,
    string? QuestEventId);

// QOD-21 Q1c: the P00-03 training-wave trial (DESIGN-BM-ALPHA-20261103
// questRules.P00-03.waveTrial) as a 20 Hz tickable machine behind
// P1:AlphaProfile:Enabled. The hazard has no runtime entity (the v2 snapshot
// wire enum has no hazard kind) and there is no approved wire surface for its
// warning, so the machine is domain-only: the cycle, the credit and the raw
// damage live server-side, and the self-check exercises them deterministically.
//
// Sourced values (never defaulted): rectangleWu min(140,-2)/max(148,2),
// windup 1,2 s, repeat cooldown 6 s, raw damage 12, retry allowed, credit
// record ALPHA-BM-WAVE-TRAINING. The cycle opens when a live player on the
// map steps inside the rectangle, holds a warning for the windup, and resolves
// at the impact tick: still inside means a raw-damage hit (applied only when
// P1:CombatDamage is on, mirroring the mob-impact gate), inside for at least
// one warning tick and outside at impact means a dodge that records an
// INTERACT_CLAIM verified event for the P00-03 wave objective. Either way the
// cooldown runs before the next cycle; leaving the map or dying mid-warning
// cancels with no credit, no damage and no cooldown. The dash has no iframe
// (DashMovementService is pure movement), so an iframe escape is unsupported.
public sealed class AlphaWaveTrialService
{
    private readonly AlphaOverlayRecord? _hazard;
    private readonly string _mapId;
    private readonly double _minX;
    private readonly double _minY;
    private readonly double _maxX;
    private readonly double _maxY;
    private readonly long _windupTicks;
    private readonly long _cooldownTicks;
    private readonly int _rawDamage;
    private readonly IQuestService _quests;
    private readonly CombatDamageFeature _combat;
    private readonly object _sync = new();
    private readonly Dictionary<string, Cycle> _cycles = new(StringComparer.Ordinal);

    public AlphaWaveTrialService(
        AlphaDesign design,
        IQuestService quests,
        CombatDamageFeature combat)
    {
        ArgumentNullException.ThrowIfNull(design);
        ArgumentNullException.ThrowIfNull(quests);
        ArgumentNullException.ThrowIfNull(combat);
        _hazard = design.OverlayRecords.FirstOrDefault(
            record => string.Equals(record.Kind, "QUEST_HAZARD", StringComparison.Ordinal));
        _mapId = design.Scope.MapId;
        var rules = design.QuestRules;
        _minX = rules.P00_03_WaveMin.X;
        _minY = rules.P00_03_WaveMin.Y;
        _maxX = rules.P00_03_WaveMax.X;
        _maxY = rules.P00_03_WaveMax.Y;
        // Integer ceiling: 1,2 s at 20 Hz is exactly 24 ticks and 6 s is 120,
        // but double arithmetic on the source values must not drift the
        // windows (same policy as the mob telegraph projection).
        _windupTicks = (long)Math.Ceiling(rules.P00_03_WaveWindupSeconds * ServerClock.TicksPerSecond);
        _cooldownTicks = (long)Math.Ceiling(
            rules.P00_03_WaveRepeatCooldownSeconds * ServerClock.TicksPerSecond);
        _rawDamage = rules.P00_03_WaveRawDamage;
        _quests = quests;
        _combat = combat;
    }

    public IReadOnlyList<WaveTrialResolution> Tick(
        IReadOnlyList<PlayerSession> players,
        long tick)
    {
        if (_hazard is null)
        {
            return Array.Empty<WaveTrialResolution>();
        }

        var targets = new Dictionary<string, PlayerSession>(StringComparer.Ordinal);
        foreach (var player in players)
        {
            targets[player.CharacterId] = player;
        }

        var resolutions = new List<WaveTrialResolution>();
        lock (_sync)
        {
            // An open cycle whose owner left the map, lost the session or went
            // down resolves as cancelled: no credit, no damage, no cooldown.
            foreach (var characterId in _cycles.Keys.ToArray())
            {
                var cycle = _cycles[characterId];
                if (!cycle.Open)
                {
                    continue;
                }

                if (!targets.TryGetValue(characterId, out var owner) ||
                    !string.Equals(owner.MapId, _mapId, StringComparison.Ordinal) ||
                    owner.Hp <= 0)
                {
                    _cycles.Remove(characterId);
                    resolutions.Add(new WaveTrialResolution(
                        characterId, WaveTrialOutcomes.Cancelled, 0, 0, 0, null));
                }
            }

            foreach (var player in players)
            {
                if (!string.Equals(player.MapId, _mapId, StringComparison.Ordinal) ||
                    player.Hp <= 0)
                {
                    continue;
                }

                var inside = Contains(player.X, player.Y);
                if (!_cycles.TryGetValue(player.CharacterId, out var cycle))
                {
                    if (inside)
                    {
                        Open(player.CharacterId, tick);
                    }

                    continue;
                }

                if (!cycle.Open)
                {
                    if (tick < cycle.CooldownUntilTick)
                    {
                        continue;
                    }

                    if (inside)
                    {
                        Open(player.CharacterId, tick);
                    }
                    else
                    {
                        _cycles.Remove(player.CharacterId);
                    }

                    continue;
                }

                if (inside)
                {
                    cycle.InsideDuringWarning = true;
                }

                if (tick < cycle.ImpactTick)
                {
                    continue;
                }

                // Impact frame: still inside means a hit; inside during the
                // warning and outside now means a dodge. Either way the
                // cooldown starts, so the trial stays retryable.
                cycle.Open = false;
                cycle.CooldownUntilTick = tick + _cooldownTicks;
                if (inside)
                {
                    resolutions.Add(ResolveHit(player));
                }
                else
                {
                    var eventId = Guid.NewGuid().ToString("N");
                    _quests.RecordVerifiedEvent(
                        player,
                        eventId,
                        QuestProgressEventTypes.InteractClaim,
                        _hazard.RecordId,
                        _mapId);
                    resolutions.Add(new WaveTrialResolution(
                        player.CharacterId,
                        WaveTrialOutcomes.Credit,
                        0,
                        player.Hp,
                        player.Hp,
                        eventId));
                }
            }
        }

        return resolutions;
    }

    private void Open(string characterId, long tick)
    {
        _cycles[characterId] = new Cycle
        {
            ImpactTick = tick + _windupTicks,
            InsideDuringWarning = true,
            Open = true
        };
    }

    private WaveTrialResolution ResolveHit(PlayerSession player)
    {
        int damage = 0;
        int hpBefore = player.Hp;
        int hpAfter = player.Hp;
        var outcome = WaveTrialOutcomes.DamageBlocked;
        if (_combat.Enabled)
        {
            // One impact is one critical section; a map change or a death from
            // another source between ticks must not commit wave damage anyway.
            lock (player.SyncRoot)
            {
                if (player.Hp > 0 &&
                    string.Equals(player.MapId, _mapId, StringComparison.Ordinal))
                {
                    hpBefore = player.Hp;
                    hpAfter = Math.Max(0, hpBefore - _rawDamage);
                    player.Hp = hpAfter;
                    player.Revision++;
                    damage = hpBefore - hpAfter;
                    outcome = WaveTrialOutcomes.Hit;
                }
            }
        }

        return new WaveTrialResolution(
            player.CharacterId, outcome, damage, hpBefore, hpAfter, null);
    }

    private bool Contains(double x, double y) =>
        x >= _minX && x <= _maxX && y >= _minY && y <= _maxY;

    private sealed class Cycle
    {
        public long ImpactTick;
        public bool InsideDuringWarning;
        public bool Open;
        public long CooldownUntilTick;
    }
}
