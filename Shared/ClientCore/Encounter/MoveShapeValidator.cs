// OPC-15 O-C — Shape validation for encounter telegraphs (renderer-neutral).
// Cone: angleDegrees in (0,360], range > 0, facing finite & not both zero.
// Circle: radius > 0.
// Annulus: 0 <= innerRadius < outerRadius.
// No engine dep.

using System;

namespace NguMach.Client.Core.Encounter
{
    public static class MoveShapeValidator
    {
        public static bool IsValid(MoveShape s, out string reason)
        {
            reason = null;
            if (s == null) { reason = "null shape"; return false; }
            switch (s.Kind)
            {
                case MoveShapeKind.Cone:
                    if (!s.AngleDegrees.HasValue || s.AngleDegrees.Value <= 0 || s.AngleDegrees.Value > 360)
                    { reason = "cone angleDegrees must be in (0,360]"; return false; }
                    if (!s.Range.HasValue || s.Range.Value <= 0) { reason = "cone range must be > 0"; return false; }
                    if (!IsFinite(s.FacingX) || !IsFinite(s.FacingY)) { reason = "facing must be finite"; return false; }
                    if (s.FacingX == 0 && s.FacingY == 0) { reason = "facing must not be zero vector"; return false; }
                    return true;
                case MoveShapeKind.Circle:
                    if (!s.Radius.HasValue || s.Radius.Value <= 0) { reason = "circle radius must be > 0"; return false; }
                    return true;
                case MoveShapeKind.Annulus:
                    if (!s.InnerRadius.HasValue || !s.OuterRadius.HasValue) { reason = "annulus radii required"; return false; }
                    if (s.InnerRadius.Value < 0) { reason = "innerRadius must be >= 0"; return false; }
                    if (s.InnerRadius.Value >= s.OuterRadius.Value) { reason = "innerRadius must be < outerRadius"; return false; }
                    return true;
                default:
                    reason = "unknown shape"; return false;
            }
        }

        private static bool IsFinite(double v) { return !double.IsNaN(v) && !double.IsInfinity(v); }
    }
}
