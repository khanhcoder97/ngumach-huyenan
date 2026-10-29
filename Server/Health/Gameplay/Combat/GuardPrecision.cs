using System.Text.Json;

namespace Server.Health.Gameplay.Combat;

// DEC-022 (docs/production/P1_Guard_Precision_20261030_vi.md): versioned
// runtime projection of the owner-locked Phản Quang precision bundle. The
// baseline is DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION and is only read when
// P1:CombatDamage:Enabled=true (OFF by default). These are tuning baseline
// values, not playtest balance; v1 wire stays untouched.
public sealed record GuardPrecisionBundle(
    int SchemaVersion,
    string BundleId,
    string DecisionId,
    string Activation,
    int TickHz,
    GuardWindow Guard,
    GuardWhiffWindow Whiff,
    GuardCounterWindow Counter,
    GuardOrdering Ordering,
    GuardOracle Oracle);

public sealed record GuardWindow(
    int DurationTicks,
    string Interval,
    double AngleDegrees,
    double RangeWu,
    string Origin,
    string Facing,
    string Boundary,
    double DamageReduction,
    int MaxConfirmations,
    int SwordIntentGain,
    int SwordIntentCap);

public sealed record GuardWhiffWindow(
    string Condition,
    int DurationTicks,
    double DamageReduction,
    IReadOnlyList<string> ExcludedOn);

public sealed record GuardCounterWindow(
    int DelayTicks,
    int MaxTargets,
    double RangeWu,
    double AngleDegrees,
    string Target,
    IReadOnlyList<string> Recheck,
    IReadOnlyList<string> Flags,
    bool BossHardControl,
    bool RefundOnMissOrTargetDeath);

public sealed record GuardOrdering(
    IReadOnlyList<string> Impacts,
    string ConfirmationPoint,
    IReadOnlyList<string> ConfirmationUniqueKey,
    IReadOnlyList<string> CounterUniqueKey);

public sealed record GuardOracle(
    long CastStartTick,
    long GuardEndExclusiveTick,
    long WhiffEndExclusiveTick,
    double RawDamage,
    double Armor,
    double OtherDamageReduction,
    int GuardFinalDamage,
    int WhiffFinalDamage,
    int OutsideFinalDamage,
    double GuardAndOtherReductionAtCap,
    int CappedFinalDamage,
    double CounterAttack,
    double CounterPveCoefficient,
    int CounterNonCritFinalDamage,
    int CounterCritFinalDamage);

public static class GuardPrecisionLoader
{
    public const string DesignOnlyActivation = "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION";
    public const string DecisionId = "DEC-022";
    public const string ExpectedBundleId = "DESIGN_P1_GUARD_PRECISION_V1";
    private const string RelativePath =
        "Implementation/Content/DesignBaselines/p1_guard_precision_v1.json";
    private const int MaxSearchDepth = 12;

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true
    };

    public static string DiscoverPath(IConfiguration configuration, string contentRoot)
    {
        var configured = configuration["Content:GuardPrecisionPath"];
        if (!string.IsNullOrWhiteSpace(configured))
        {
            var resolved = Path.IsPathRooted(configured)
                ? configured
                : Path.GetFullPath(Path.Combine(contentRoot, configured));
            if (!File.Exists(resolved))
            {
                throw new FileNotFoundException(
                    $"Content:GuardPrecisionPath points to '{resolved}', which does not exist.");
            }

            return resolved;
        }

        var starts = new[] { contentRoot, Directory.GetCurrentDirectory(), AppContext.BaseDirectory }
            .Where(path => !string.IsNullOrWhiteSpace(path))
            .Distinct(StringComparer.OrdinalIgnoreCase);

        foreach (var start in starts)
        {
            DirectoryInfo? directory = new(Path.GetFullPath(start));
            for (var depth = 0; depth < MaxSearchDepth && directory is not null; depth++)
            {
                var candidate = Path.Combine(directory.FullName, RelativePath);
                if (File.Exists(candidate))
                {
                    return candidate;
                }

                directory = directory.Parent;
            }
        }

        throw new FileNotFoundException(
            $"Could not locate {RelativePath}. Set Content:GuardPrecisionPath or run from the repository.");
    }

    public static GuardPrecisionBundle Load(string path)
    {
        GuardFile? file;
        try
        {
            using var stream = File.OpenRead(path);
            file = JsonSerializer.Deserialize<GuardFile>(stream, JsonOptions);
        }
        catch (JsonException exception)
        {
            throw new InvalidOperationException(
                $"{path}: invalid JSON ({exception.Message})", exception);
        }

        if (file is null)
        {
            throw new InvalidOperationException($"{path}: file is empty.");
        }

        if (file.SchemaVersion != 1 ||
            !string.Equals(file.BundleId, ExpectedBundleId, StringComparison.Ordinal) ||
            !string.Equals(file.DecisionId, DecisionId, StringComparison.Ordinal) ||
            !string.Equals(file.Activation, DesignOnlyActivation, StringComparison.Ordinal))
        {
            throw new InvalidOperationException(
                $"{path}: expected schemaVersion 1, bundleId {ExpectedBundleId}, " +
                $"decisionId {DecisionId} and activation {DesignOnlyActivation}.");
        }

        if (file.TickHz != 20)
        {
            throw new InvalidOperationException($"{path}: tickHz must be 20.");
        }

        var guard = file.Guard;
        if (guard is null ||
            guard.DurationTicks != 8 ||
            !string.Equals(guard.Interval, "START_INCLUSIVE_END_EXCLUSIVE", StringComparison.Ordinal) ||
            !Near(guard.AngleDegrees, 120) ||
            !Near(guard.RangeWu, 4.4) ||
            !string.Equals(guard.Origin, "DEFENDER_CURRENT_FOOT", StringComparison.Ordinal) ||
            !string.Equals(guard.Facing, "CAST_START_SNAPSHOT", StringComparison.Ordinal) ||
            !string.Equals(guard.Boundary, "INCLUSIVE", StringComparison.Ordinal) ||
            !Near(guard.DamageReduction, 0.7) ||
            guard.MaxConfirmations != 1 ||
            guard.SwordIntentGain != 2 ||
            guard.SwordIntentCap != 5)
        {
            throw new InvalidOperationException(
                $"{path}: guard window must match DEC-022 (8 ticks [start,end), " +
                "120 deg, 4.4 WU, 0.70 DR, one confirmation, +2/5 sword intent).");
        }

        var whiff = file.Whiff;
        if (whiff is null ||
            whiff.DurationTicks != 20 ||
            !Near(whiff.DamageReduction, 0.2) ||
            !string.Equals(
                whiff.Condition,
                "NATURAL_EXPIRY_WITH_NO_CONFIRMATION_AND_ALIVE",
                StringComparison.Ordinal) ||
            !SameSet(
                whiff.ExcludedOn,
                ["DEATH", "MAP_CHANGE", "SESSION_END", "HARD_CONTROL", "DODGE_CANCEL"]))
        {
            throw new InvalidOperationException(
                $"{path}: whiff window must match DEC-022 (20 ticks of 0.20 DR, " +
                "natural expiry only, excluded on death/map/session/hard-control/dodge).");
        }

        var counter = file.Counter;
        if (counter is null ||
            counter.DelayTicks != 1 ||
            counter.MaxTargets != 1 ||
            !Near(counter.RangeWu, guard.RangeWu) ||
            !Near(counter.AngleDegrees, guard.AngleDegrees) ||
            !string.Equals(counter.Target, "CONFIRMED_ATTACK_SOURCE", StringComparison.Ordinal) ||
            counter.BossHardControl ||
            counter.RefundOnMissOrTargetDeath ||
            !SameSet(
                counter.Flags,
                ["NO_COUNTER_TRIGGER", "NO_EXTRA_RESOURCE_ON_DAMAGE",
                 "NO_NEW_MP_COST", "NO_NEW_COOLDOWN"]))
        {
            throw new InvalidOperationException(
                $"{path}: counter must match DEC-022 (next tick, one source target, " +
                "4.4 WU/120 deg, no recursion/refund/hard control).");
        }

        var ordering = file.Ordering;
        if (ordering is null ||
            !SameSequence(
                ordering.Impacts,
                ["scheduledTick", "castStartTick", "castIdOrdinal", "hitIndex", "targetIdOrdinal"]) ||
            !SameSequence(ordering.ConfirmationUniqueKey, ["guardCastId"]) ||
            !SameSequence(ordering.CounterUniqueKey, ["guardCastId", "confirmationEventId"]))
        {
            throw new InvalidOperationException(
                $"{path}: impact ordering and confirmation/counter keys must match DEC-022.");
        }

        var oracle = file.Oracle;
        if (oracle is null)
        {
            throw new InvalidOperationException($"{path}: oracle is required.");
        }

        var guardEnd = oracle.CastStartTick + guard.DurationTicks;
        if (oracle.GuardEndExclusiveTick != guardEnd ||
            oracle.WhiffEndExclusiveTick != guardEnd + whiff.DurationTicks)
        {
            throw new InvalidOperationException(
                $"{path}: oracle guard/whiff end ticks disagree with the window durations.");
        }

        var mitigation = DamageFormula.MitigationMultiplier(oracle.Armor);
        var outside = DamageFormula.FinalDamage(oracle.RawDamage, mitigation, 1, 1, 1);
        var guarded = DamageFormula.FinalDamage(
            oracle.RawDamage, mitigation, 1, 1,
            DamageFormula.DamageReductionMultiplier(guard.DamageReduction));
        var whiffed = DamageFormula.FinalDamage(
            oracle.RawDamage, mitigation, 1, 1,
            DamageFormula.DamageReductionMultiplier(whiff.DamageReduction));
        var capped = DamageFormula.FinalDamage(
            oracle.RawDamage, mitigation, 1, 1,
            DamageFormula.DamageReductionMultiplier(GuardTimeline.DamageReductionCap));
        var counterRaw = oracle.CounterAttack * oracle.CounterPveCoefficient;
        var counterDamage = DamageFormula.FinalDamage(counterRaw, mitigation, 1, 1, 1);
        var counterCritDamage = DamageFormula.FinalDamage(
            counterRaw, mitigation, 1, DamageFormula.CritMultiplier, 1);
        if (outside != oracle.OutsideFinalDamage ||
            guarded != oracle.GuardFinalDamage ||
            whiffed != oracle.WhiffFinalDamage ||
            capped != oracle.CappedFinalDamage ||
            !Near(
                oracle.GuardAndOtherReductionAtCap,
                GuardTimeline.CombineReduction(
                    guard.DamageReduction, whiff.DamageReduction)) ||
            counterDamage != oracle.CounterNonCritFinalDamage ||
            counterCritDamage != oracle.CounterCritFinalDamage)
        {
            throw new InvalidOperationException(
                $"{path}: oracle arithmetic does not reproduce DEC-022 " +
                $"(27/8/21/5, counter 32/49); got {outside}/{guarded}/{whiffed}/{capped}, " +
                $"counter {counterDamage}/{counterCritDamage}.");
        }

        return new GuardPrecisionBundle(
            file.SchemaVersion,
            file.BundleId!,
            file.DecisionId!,
            file.Activation!,
            file.TickHz,
            new GuardWindow(
                guard.DurationTicks,
                guard.Interval!,
                guard.AngleDegrees,
                guard.RangeWu,
                guard.Origin!,
                guard.Facing!,
                guard.Boundary!,
                guard.DamageReduction,
                guard.MaxConfirmations,
                guard.SwordIntentGain,
                guard.SwordIntentCap),
            new GuardWhiffWindow(
                whiff.Condition!,
                whiff.DurationTicks,
                whiff.DamageReduction,
                whiff.ExcludedOn ?? []),
            new GuardCounterWindow(
                counter.DelayTicks,
                counter.MaxTargets,
                counter.RangeWu,
                counter.AngleDegrees,
                counter.Target!,
                counter.Recheck ?? [],
                counter.Flags ?? [],
                counter.BossHardControl,
                counter.RefundOnMissOrTargetDeath),
            new GuardOrdering(
                ordering.Impacts!,
                ordering.ConfirmationPoint ?? string.Empty,
                ordering.ConfirmationUniqueKey!,
                ordering.CounterUniqueKey!),
            new GuardOracle(
                oracle.CastStartTick,
                oracle.GuardEndExclusiveTick,
                oracle.WhiffEndExclusiveTick,
                oracle.RawDamage,
                oracle.Armor,
                oracle.OtherDamageReduction,
                oracle.GuardFinalDamage,
                oracle.WhiffFinalDamage,
                oracle.OutsideFinalDamage,
                oracle.GuardAndOtherReductionAtCap,
                oracle.CappedFinalDamage,
                oracle.CounterAttack,
                oracle.CounterPveCoefficient,
                oracle.CounterNonCritFinalDamage,
                oracle.CounterCritFinalDamage));
    }

    private static bool Near(double actual, double expected) =>
        Math.Abs(actual - expected) < 1e-9;

    private static bool SameSet(IReadOnlyList<string>? actual, string[] expected) =>
        actual is not null &&
        actual.Count == expected.Length &&
        actual.OrderBy(value => value, StringComparer.Ordinal)
            .SequenceEqual(expected.OrderBy(value => value, StringComparer.Ordinal), StringComparer.Ordinal);

    private static bool SameSequence(IReadOnlyList<string>? actual, string[] expected) =>
        actual is not null && actual.SequenceEqual(expected, StringComparer.Ordinal);

    private sealed class GuardFile
    {
        public int SchemaVersion { get; init; }
        public string? BundleId { get; init; }
        public string? DecisionId { get; init; }
        public string? Activation { get; init; }
        public string? Owner { get; init; }
        public int TickHz { get; init; }
        public List<string>? Scope { get; init; }
        public GuardFileWindow? Guard { get; init; }
        public WhiffFileWindow? Whiff { get; init; }
        public CounterFileWindow? Counter { get; init; }
        public OrderingFile? Ordering { get; init; }
        public OracleFile? Oracle { get; init; }
    }

    private sealed class GuardFileWindow
    {
        public int DurationTicks { get; init; }
        public string? Interval { get; init; }
        public double AngleDegrees { get; init; }
        public double RangeWu { get; init; }
        public string? Origin { get; init; }
        public string? Facing { get; init; }
        public string? Boundary { get; init; }
        public double DamageReduction { get; init; }
        public int MaxConfirmations { get; init; }
        public int SwordIntentGain { get; init; }
        public int SwordIntentCap { get; init; }
    }

    private sealed class WhiffFileWindow
    {
        public string? Condition { get; init; }
        public int DurationTicks { get; init; }
        public double DamageReduction { get; init; }
        public List<string>? ExcludedOn { get; init; }
    }

    private sealed class CounterFileWindow
    {
        public int DelayTicks { get; init; }
        public int MaxTargets { get; init; }
        public double RangeWu { get; init; }
        public double AngleDegrees { get; init; }
        public string? Target { get; init; }
        public List<string>? Recheck { get; init; }
        public List<string>? Flags { get; init; }
        public bool BossHardControl { get; init; }
        public bool RefundOnMissOrTargetDeath { get; init; }
    }

    private sealed class OrderingFile
    {
        public List<string>? Impacts { get; init; }
        public string? ConfirmationPoint { get; init; }
        public List<string>? ConfirmationUniqueKey { get; init; }
        public List<string>? CounterUniqueKey { get; init; }
    }

    private sealed class OracleFile
    {
        public long CastStartTick { get; init; }
        public long GuardEndExclusiveTick { get; init; }
        public long WhiffEndExclusiveTick { get; init; }
        public double RawDamage { get; init; }
        public double Armor { get; init; }
        public double OtherDamageReduction { get; init; }
        public int GuardFinalDamage { get; init; }
        public int WhiffFinalDamage { get; init; }
        public int OutsideFinalDamage { get; init; }
        public double GuardAndOtherReductionAtCap { get; init; }
        public int CappedFinalDamage { get; init; }
        public double CounterAttack { get; init; }
        public double CounterPveCoefficient { get; init; }
        public int CounterNonCritFinalDamage { get; init; }
        public int CounterCritFinalDamage { get; init; }
    }
}

// Pure DEC-022 timeline/geometry helpers — no state, no RNG. The guard window
// is [castStart, castStart+8) at 20 Hz; whiff is [guardEnd, guardEnd+20);
// the counter resolves on the tick after a confirmed hit.
public static class GuardTimeline
{
    public const double DamageReductionCap = 0.8;
    private const double Epsilon = 1e-9;

    public static long GuardEndExclusiveTick(long castStartTick, int durationTicks) =>
        castStartTick + durationTicks;

    public static bool IsGuardActive(long castStartTick, int durationTicks, long tick) =>
        tick >= castStartTick && tick < castStartTick + durationTicks;

    public static long WhiffStartTick(long castStartTick, int guardDurationTicks) =>
        castStartTick + guardDurationTicks;

    public static long WhiffEndExclusiveTick(
        long castStartTick, int guardDurationTicks, int whiffDurationTicks) =>
        castStartTick + guardDurationTicks + whiffDurationTicks;

    public static bool IsWhiffActive(
        long castStartTick, int guardDurationTicks, int whiffDurationTicks, long tick) =>
        tick >= WhiffStartTick(castStartTick, guardDurationTicks) &&
        tick < WhiffEndExclusiveTick(castStartTick, guardDurationTicks, whiffDurationTicks);

    // DEC-022 §2: guard region attaches to the defender's current foot with
    // the cast-start facing; boundaries are inclusive and a coincident foot
    // pair counts as inside (zero-length vector is never normalized).
    public static bool InFront(
        double originX,
        double originY,
        double facingX,
        double facingY,
        double sourceX,
        double sourceY,
        double rangeWu,
        double angleDegrees)
    {
        if (!double.IsFinite(originX) || !double.IsFinite(originY) ||
            !double.IsFinite(facingX) || !double.IsFinite(facingY) ||
            !double.IsFinite(sourceX) || !double.IsFinite(sourceY) ||
            !double.IsFinite(rangeWu) || rangeWu < 0 ||
            !double.IsFinite(angleDegrees) || angleDegrees is < 0 or > 360)
        {
            return false;
        }

        var deltaX = sourceX - originX;
        var deltaY = sourceY - originY;
        var distanceSquared = (deltaX * deltaX) + (deltaY * deltaY);
        if (distanceSquared > (rangeWu * rangeWu) + Epsilon)
        {
            return false;
        }

        if (distanceSquared <= Epsilon)
        {
            return true;
        }

        var facingLength = Math.Sqrt((facingX * facingX) + (facingY * facingY));
        if (facingLength <= Epsilon)
        {
            return false;
        }

        var distance = Math.Sqrt(distanceSquared);
        var dot = ((deltaX * facingX) + (deltaY * facingY)) / (distance * facingLength);
        var halfAngleRadians = angleDegrees / 2.0 * Math.PI / 180.0;
        return dot >= Math.Cos(halfAngleRadians) - Epsilon;
    }

    // DR modifiers share one additive bucket capped at 0.80 (DEC-022 §4).
    public static double CombineReduction(params double[] reductions)
    {
        var total = 0.0;
        foreach (var reduction in reductions)
        {
            if (double.IsFinite(reduction) && reduction > 0)
            {
                total += reduction;
            }
        }

        return Math.Min(DamageReductionCap, total);
    }

    // DEC-022 §3: (scheduledTick, castStartTick, castId ordinal, hitIndex,
    // targetId ordinal) — deterministic across replays and process restarts.
    public static int CompareImpacts(ImpactOrderKey left, ImpactOrderKey right)
    {
        var comparison = left.ScheduledTick.CompareTo(right.ScheduledTick);
        if (comparison != 0)
        {
            return comparison;
        }

        comparison = left.CastStartTick.CompareTo(right.CastStartTick);
        if (comparison != 0)
        {
            return comparison;
        }

        comparison = string.CompareOrdinal(left.CastId, right.CastId);
        if (comparison != 0)
        {
            return comparison;
        }

        comparison = left.HitIndex.CompareTo(right.HitIndex);
        return comparison != 0
            ? comparison
            : string.CompareOrdinal(left.TargetId, right.TargetId);
    }
}

public readonly record struct ImpactOrderKey(
    long ScheduledTick,
    long CastStartTick,
    string CastId,
    int HitIndex,
    string TargetId);
