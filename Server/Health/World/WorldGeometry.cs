namespace Server.Health.World;

public static class GeometryMath
{
    private const double Epsilon = 1e-9;

    public static double Cross(double ax, double ay, double bx, double by) =>
        (ax * by) - (ay * bx);

    public static double Orientation(
        double ax, double ay, double bx, double by, double cx, double cy) =>
        Cross(bx - ax, by - ay, cx - ax, cy - ay);

    public static bool OnSegment(
        double ax, double ay, double bx, double by, double px, double py)
    {
        if (Math.Abs(Orientation(ax, ay, bx, by, px, py)) > Epsilon)
        {
            return false;
        }

        return px >= Math.Min(ax, bx) - Epsilon &&
               px <= Math.Max(ax, bx) + Epsilon &&
               py >= Math.Min(ay, by) - Epsilon &&
               py <= Math.Max(ay, by) + Epsilon;
    }

    public static bool SegmentsIntersect(
        double a1x, double a1y, double a2x, double a2y,
        double b1x, double b1y, double b2x, double b2y)
    {
        var d1 = Orientation(b1x, b1y, b2x, b2y, a1x, a1y);
        var d2 = Orientation(b1x, b1y, b2x, b2y, a2x, a2y);
        var d3 = Orientation(a1x, a1y, a2x, a2y, b1x, b1y);
        var d4 = Orientation(a1x, a1y, a2x, a2y, b2x, b2y);

        if (((d1 > Epsilon && d2 < -Epsilon) || (d1 < -Epsilon && d2 > Epsilon)) &&
            ((d3 > Epsilon && d4 < -Epsilon) || (d3 < -Epsilon && d4 > Epsilon)))
        {
            return true;
        }

        return (Math.Abs(d1) <= Epsilon && OnSegment(b1x, b1y, b2x, b2y, a1x, a1y)) ||
               (Math.Abs(d2) <= Epsilon && OnSegment(b1x, b1y, b2x, b2y, a2x, a2y)) ||
               (Math.Abs(d3) <= Epsilon && OnSegment(a1x, a1y, a2x, a2y, b1x, b1y)) ||
               (Math.Abs(d4) <= Epsilon && OnSegment(a1x, a1y, a2x, a2y, b2x, b2y));
    }

    public static bool PolygonSelfIntersects(IReadOnlyList<TopologyPoint> points)
    {
        var count = points.Count;
        for (var i = 0; i < count; i++)
        {
            var a1 = points[i];
            var a2 = points[(i + 1) % count];
            for (var j = i + 2; j < count; j++)
            {
                if (i == 0 && j == count - 1)
                {
                    continue;
                }

                var b1 = points[j];
                var b2 = points[(j + 1) % count];
                if (SegmentsIntersect(
                        a1.X, a1.Y, a2.X, a2.Y, b1.X, b1.Y, b2.X, b2.Y))
                {
                    return true;
                }
            }
        }

        return false;
    }

    public static bool PointInPolygon(
        IReadOnlyList<TopologyPoint> points, double x, double y)
    {
        var count = points.Count;
        for (var i = 0; i < count; i++)
        {
            var a = points[i];
            var b = points[(i + 1) % count];
            if (OnSegment(a.X, a.Y, b.X, b.Y, x, y))
            {
                return true;
            }
        }

        var inside = false;
        for (var i = 0; i < count; i++)
        {
            var a = points[i];
            var b = points[(i + 1) % count];
            if ((a.Y > y) == (b.Y > y))
            {
                continue;
            }

            var intersectionX = a.X + ((y - a.Y) * (b.X - a.X) / (b.Y - a.Y));
            if (x < intersectionX)
            {
                inside = !inside;
            }
        }

        return inside;
    }

    public static bool SegmentIntersectsPolygon(
        IReadOnlyList<TopologyPoint> points,
        double ax, double ay, double bx, double by)    {
        var count = points.Count;
        for (var i = 0; i < count; i++)
        {
            var a = points[i];
            var b = points[(i + 1) % count];
            if (SegmentsIntersect(ax, ay, bx, by, a.X, a.Y, b.X, b.Y))
            {
                return true;
            }
        }

        return false;
    }

    public static double DistancePointToSegment(
        double px, double py, double ax, double ay, double bx, double by)
    {
        var dx = bx - ax;
        var dy = by - ay;
        var lengthSquared = (dx * dx) + (dy * dy);
        if (lengthSquared <= Epsilon)
        {
            return Math.Sqrt(((px - ax) * (px - ax)) + ((py - ay) * (py - ay)));
        }

        var t = Math.Clamp(
            (((px - ax) * dx) + ((py - ay) * dy)) / lengthSquared, 0, 1);
        var cx = ax + (dx * t);
        var cy = ay + (dy * t);
        return Math.Sqrt(((px - cx) * (px - cx)) + ((py - cy) * (py - cy)));
    }

    public static IReadOnlyList<double> SegmentBoundaryParameters(
        IReadOnlyList<TopologyPoint> points,
        double ax, double ay, double bx, double by)
    {
        var parameters = new List<double>();
        var dx = bx - ax;
        var dy = by - ay;
        var count = points.Count;
        for (var i = 0; i < count; i++)
        {
            var c = points[i];
            var d = points[(i + 1) % count];
            var ex = d.X - c.X;
            var ey = d.Y - c.Y;
            var denominator = Cross(dx, dy, ex, ey);

            if (Math.Abs(denominator) <= Epsilon)
            {
                if (Math.Abs(Cross(c.X - ax, c.Y - ay, dx, dy)) > Epsilon)
                {
                    continue;
                }

                var lengthSquared = (dx * dx) + (dy * dy);
                if (lengthSquared <= Epsilon)
                {
                    continue;
                }

                foreach (var point in new[] { c, d })
                {
                    var t = (((point.X - ax) * dx) + ((point.Y - ay) * dy)) / lengthSquared;
                    if (t > Epsilon && t < 1 - Epsilon)
                    {
                        parameters.Add(t);
                    }
                }

                continue;
            }

            var tSegment = Cross(c.X - ax, c.Y - ay, ex, ey) / denominator;
            var uEdge = Cross(c.X - ax, c.Y - ay, dx, dy) / denominator;
            if (tSegment > Epsilon && tSegment < 1 - Epsilon &&
                uEdge >= -Epsilon && uEdge <= 1 + Epsilon)
            {
                parameters.Add(tSegment);
            }
        }

        return parameters;
    }
}

public enum LineOfSightStatus
{
    Allowed,
    Blocked,
    NotEnforced
}

public sealed record LineOfSightResult(LineOfSightStatus Status, string? Reason)
{
    public bool IsBlocked => Status == LineOfSightStatus.Blocked;
}

public interface IWorldGeometryService
{
    LineOfSightResult CheckLineOfSight(
        string mapId,
        string floorId,
        double fromX,
        double fromY,
        double toX,
        double toY);

    LineOfSightResult CheckWalkSegment(
        string mapId,
        string floorId,
        double fromX,
        double fromY,
        double toX,
        double toY,
        double footprintRadiusWu);
}

public sealed class WorldGeometryService : IWorldGeometryService
{
    private readonly WorldGeometryCatalog _catalog;

    public WorldGeometryService(WorldGeometryCatalog catalog)
    {
        _catalog = catalog;
    }

    public LineOfSightResult CheckLineOfSight(
        string mapId,
        string floorId,
        double fromX,
        double fromY,
        double toX,
        double toY)
    {
        if (!double.IsFinite(fromX) || !double.IsFinite(fromY) ||
            !double.IsFinite(toX) || !double.IsFinite(toY))
        {
            return new LineOfSightResult(LineOfSightStatus.Blocked, "nonfinite");
        }

        if (!_catalog.TryGet(mapId, out var bundle) || !bundle.IsReviewed)
        {
            return new LineOfSightResult(LineOfSightStatus.NotEnforced, "no_reviewed_topology");
        }

        if (!bundle.FloorIds.Contains(floorId, StringComparer.Ordinal))
        {
            return new LineOfSightResult(LineOfSightStatus.Blocked, "floor");
        }

        if (!IsWalkable(bundle, floorId, fromX, fromY) ||
            !IsWalkable(bundle, floorId, toX, toY))
        {
            return new LineOfSightResult(LineOfSightStatus.Blocked, "outside_walkable");
        }

        foreach (var polygon in bundle.BlockedPolygons)
        {
            if (!string.Equals(polygon.FloorId, floorId, StringComparison.Ordinal))
            {
                continue;
            }

            if (GeometryMath.SegmentIntersectsPolygon(
                    polygon.Points, fromX, fromY, toX, toY))
            {
                return new LineOfSightResult(LineOfSightStatus.Blocked, "blocked_polygon");
            }
        }

        var parameters = new List<double> { 0, 1 };
        foreach (var polygon in bundle.WalkablePolygons)
        {
            if (!string.Equals(polygon.FloorId, floorId, StringComparison.Ordinal))
            {
                continue;
            }

            parameters.AddRange(GeometryMath.SegmentBoundaryParameters(
                polygon.Points, fromX, fromY, toX, toY));
        }

        parameters.Sort();
        for (var index = 1; index < parameters.Count; index++)
        {
            var start = parameters[index - 1];
            var end = parameters[index];
            if (end - start <= 1e-6)
            {
                continue;
            }

            var mid = (start + end) / 2;
            var x = fromX + ((toX - fromX) * mid);
            var y = fromY + ((toY - fromY) * mid);
            if (!IsWalkable(bundle, floorId, x, y))
            {
                return new LineOfSightResult(LineOfSightStatus.Blocked, "gap");
            }
        }

        return new LineOfSightResult(LineOfSightStatus.Allowed, null);
    }

    public LineOfSightResult CheckWalkSegment(
        string mapId,
        string floorId,
        double fromX,
        double fromY,
        double toX,
        double toY,
        double footprintRadiusWu)
    {
        if (!double.IsFinite(footprintRadiusWu) || footprintRadiusWu < 0)
        {
            return new LineOfSightResult(LineOfSightStatus.Blocked, "nonfinite_radius");
        }

        var line = CheckLineOfSight(mapId, floorId, fromX, fromY, toX, toY);
        if (line.Status != LineOfSightStatus.Allowed)
        {
            return line;
        }

        if (footprintRadiusWu <= 0)
        {
            return line;
        }

        if (!_catalog.TryGet(mapId, out var bundle))
        {
            return line;
        }

        var deltaX = toX - fromX;
        var deltaY = toY - fromY;
        var length = Math.Sqrt((deltaX * deltaX) + (deltaY * deltaY));
        var steps = Math.Max(1, (int)Math.Ceiling(length / 0.25));
        for (var step = 0; step <= steps; step++)
        {
            var t = (double)step / steps;
            var x = fromX + (deltaX * t);
            var y = fromY + (deltaY * t);
            foreach (var polygon in bundle.BlockedPolygons)
            {
                if (!string.Equals(polygon.FloorId, floorId, StringComparison.Ordinal))
                {
                    continue;
                }

                for (var index = 0; index < polygon.Points.Count; index++)
                {
                    var a = polygon.Points[index];
                    var b = polygon.Points[(index + 1) % polygon.Points.Count];
                    var distance = GeometryMath.DistancePointToSegment(
                        x, y, a.X, a.Y, b.X, b.Y);
                    if (distance < footprintRadiusWu - 1e-9)
                    {
                        return new LineOfSightResult(
                            LineOfSightStatus.Blocked, "footprint");
                    }
                }
            }
        }

        return line;
    }

    private static bool IsWalkable(
        MapTopologyBundle bundle, string floorId, double x, double y)    {
        var inWalkable = false;
        foreach (var polygon in bundle.WalkablePolygons)
        {
            if (string.Equals(polygon.FloorId, floorId, StringComparison.Ordinal) &&
                GeometryMath.PointInPolygon(polygon.Points, x, y))
            {
                inWalkable = true;
                break;
            }
        }

        if (!inWalkable)
        {
            return false;
        }

        foreach (var polygon in bundle.BlockedPolygons)
        {
            if (string.Equals(polygon.FloorId, floorId, StringComparison.Ordinal) &&
                GeometryMath.PointInPolygon(polygon.Points, x, y))
            {
                return false;
            }
        }

        return true;
    }
}
