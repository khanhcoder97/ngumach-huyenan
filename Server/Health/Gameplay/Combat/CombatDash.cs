using System.Collections.Concurrent;
using Server.Health.World;

namespace Server.Health.Gameplay.Combat;

// SK-MK-02 Tầm Long (Art Brief P1 §"Kỹ năng": prep 0,15s, dash 0,20s, recovery
// 0,24s; Content Bible: 5,5 m, "dừng tại tường", không xuyên vật cản; 1 WU =
// 0,5 m per DEC-016, so the canonical rangeWu 11 is that 5,5 m).
//
// The dash moves the actor and never damages: Production_Rules §2 damage needs a
// hit shape, and the design resolution §4 says a dash's attack/collision volume
// needs its own field that no canonical content ships yet, so the 150% number in
// the Content Bible row stays unapplied (filed as a case rather than guessed).
//
// P1 has no reviewed dash volume either, so the sweep reuses the movement
// footprint radius (P1World:ActorFootprintRadiusWu) with the same convention as
// POST /p1/move. The walkability answer only exists for REVIEWED topology: on the
// shipped synthetic bundle the sweep is NotEnforced and the dash runs its full
// distance, which is reported as Complete, never as proof that walls work.
public static class DashStopReasons
{
    public const string Complete = "COMPLETE";
    public const string BlockedByGeometry = "BLOCKED_BY_GEOMETRY";
    public const string ZeroDistance = "ZERO_DISTANCE";
}

public sealed record DashResolution(
    string CastId,
    string CharacterId,
    long AppliedTick,
    double RequestedWu,
    double AchievedWu,
    double X,
    double Y,
    string StopReason,
    long ActorRevision);

// Bounded audit of dash resolutions so a caller can ask "where did that cast
// actually put the actor and why did it stop" without any wire field. Oldest
// entries drop first; nothing here is exposed over HTTP yet (see the QOD-18
// proposal section for the contract request).
public sealed class DashLedger
{
    public const int Capacity = 512;

    private readonly ConcurrentDictionary<string, DashResolution> _byCastId =
        new(StringComparer.Ordinal);
    private readonly ConcurrentQueue<string> _order = new();
    private readonly object _sync = new();

    public int Count => _byCastId.Count;

    public DashResolution Record(DashResolution resolution)
    {
        lock (_sync)
        {
            if (_byCastId.TryAdd(resolution.CastId, resolution))
            {
                _order.Enqueue(resolution.CastId);
            }

            while (_order.Count > Capacity && _order.TryDequeue(out var oldest))
            {
                _byCastId.TryRemove(oldest, out _);
            }
        }

        return resolution;
    }

    public DashResolution? Find(string castId) =>
        _byCastId.TryGetValue(castId, out var resolution) ? resolution : null;
}

public sealed class DashMovementService
{
    // Coarse march then binary refinement: a deterministic farthest-safe point
    // without depending on the geometry service exposing a hit fraction.
    private const double ProbeWu = 0.25;
    private const int RefinementSteps = 12;

    private readonly IWorldGeometryService _geometry;
    private readonly P1WorldOptions _options;
    private readonly MapBoundsCatalog _bounds;
    private readonly DashLedger _ledger = new();

    public DashMovementService(
        IWorldGeometryService geometry,
        P1WorldOptions options,
        MapBoundsCatalog bounds)
    {
        _geometry = geometry;
        _options = options;
        _bounds = bounds;
    }

    public DashLedger Ledger => _ledger;

    // Moves the actor from its current foot at the dash tick along the facing
    // snapshotted when the cast was accepted, never past a blocker or the map
    // edge. Cost, cooldown and sequence were already committed at accept and are
    // not refunded when the sweep stops short (P1_Design_Resolution §3).
    public DashResolution Apply(
        PlayerSession actor,
        string castId,
        double facingX,
        double facingY,
        double requestedWu,
        long tick)
    {
        ArgumentNullException.ThrowIfNull(actor);

        var mapId = actor.MapId;
        var floorId = actor.FloorId;
        var hasBounds = _bounds.TryResolve(mapId, out var bounds);
        var length = Math.Sqrt((facingX * facingX) + (facingY * facingY));
        var unitX = length <= 1e-9 ? 1.0 : facingX / length;
        var unitY = length <= 1e-9 ? 0.0 : facingY / length;

        lock (actor.SyncRoot)
        {
            var startX = actor.X;
            var startY = actor.Y;
            var limit = double.IsFinite(requestedWu) && requestedWu > 0 ? requestedWu : 0;
            var travelled = 0.0;

            while (travelled + ProbeWu <= limit)
            {
                var next = travelled + ProbeWu;
                if (Blocked(mapId, floorId, startX, startY, unitX, unitY, next))
                {
                    break;
                }

                travelled = next;
            }

            if (travelled < limit && !Blocked(mapId, floorId, startX, startY, unitX, unitY, limit))
            {
                travelled = limit;
            }
            else if (travelled < limit)
            {
                var lo = travelled;
                var hi = Math.Min(limit, travelled + ProbeWu);
                for (var step = 0; step < RefinementSteps; step++)
                {
                    var mid = (lo + hi) / 2.0;
                    if (Blocked(mapId, floorId, startX, startY, unitX, unitY, mid))
                    {
                        hi = mid;
                    }
                    else
                    {
                        lo = mid;
                    }
                }

                travelled = lo;
            }

            var rawX = startX + (unitX * travelled);
            var rawY = startY + (unitY * travelled);
            var targetX = hasBounds ? Math.Clamp(rawX, bounds.XMin, bounds.XMax) : rawX;
            var targetY = hasBounds ? Math.Clamp(rawY, bounds.YMin, bounds.YMax) : rawY;
            var achieved = Math.Sqrt(
                ((targetX - startX) * (targetX - startX)) +
                ((targetY - startY) * (targetY - startY)));

            var reason = achieved <= 1e-9
                ? DashStopReasons.ZeroDistance
                : achieved + 1e-6 >= limit
                    ? DashStopReasons.Complete
                    : DashStopReasons.BlockedByGeometry;

            if (achieved > 1e-9)
            {
                actor.X = targetX;
                actor.Y = targetY;
                actor.Revision++;
            }

            return _ledger.Record(new DashResolution(
                castId,
                actor.CharacterId,
                tick,
                limit,
                Math.Round(achieved, 6),
                targetX,
                targetY,
                reason,
                actor.Revision));
        }
    }

    private bool Blocked(
        string mapId,
        string floorId,
        double startX,
        double startY,
        double unitX,
        double unitY,
        double travelled)
    {
        var probeX = startX + (unitX * travelled);
        var probeY = startY + (unitY * travelled);
        return _geometry.CheckWalkSegment(
            mapId, floorId, startX, startY, probeX, probeY, _options.ActorFootprintRadiusWu).IsBlocked;
    }
}
