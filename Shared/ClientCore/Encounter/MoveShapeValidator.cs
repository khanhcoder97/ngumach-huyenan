// OPC-15 O1 — Shape validation for encounter telegraphs (renderer-neutral).
// Uses the approved field names: kind/rangeWu/radiusWu/innerRadiusWu/outerRadiusWu/
// angleDegrees/facingX/facingY/center. Strict: no silent mapping of unknown kinds.
// Pure C#. Owner: OpenCode.

using System;

namespace NguMach.Client.Core.Encounter
{
    public static class MoveShapeValidator
    {
        public static bool IsValid(MoveShape s, out string reason)
        {
            reason = null;
            if (s == null) { reason = "null shape"; return false; }
            // kind must be explicitly one of the three (KindRaw stored)
            var kind = s.KindRaw;
            if (string.IsNullOrEmpty(kind)) kind = "cone";
            if (kind != "cone" && kind != "circle" && kind != "annulus") { reason = "unknown kind: " + kind; return false; }

            if (!IsFinite(s.FacingX) || !IsFinite(s.FacingY)) { reason = "facing must be finite"; return false; }
            if (s.FacingX == 0 && s.FacingY == 0) { reason = "facing must not be zero vector"; return false; }
            double len = Math.Sqrt(s.FacingX * s.FacingX + s.FacingY * s.FacingY);
            if (len < 0.99 || len > 1.01) { reason = "facing not normalized: " + len; return false; }

            switch (kind)
            {
                case "cone":
                    if (s.RangeWu <= 0) { reason = "cone rangeWu must be > 0"; return false; }
                    if (s.AngleDegrees.HasValue && (s.AngleDegrees.Value <= 0 || s.AngleDegrees.Value > 360))
                    { reason = "cone angleDegrees must be in (0,360]"; return false; }
                    return true;
                case "circle":
                    if (!s.RadiusWu.HasValue || s.RadiusWu.Value <= 0) { reason = "circle radiusWu must be > 0"; return false; }
                    return true;
                case "annulus":
                    if (!s.InnerRadiusWu.HasValue || !s.OuterRadiusWu.HasValue) { reason = "annulus radii required"; return false; }
                    if (s.InnerRadiusWu.Value < 0) { reason = "innerRadiusWu must be >= 0"; return false; }
                    if (s.InnerRadiusWu.Value >= s.OuterRadiusWu.Value) { reason = "innerRadiusWu must be < outerRadiusWu"; return false; }
                    return true;
            }
            reason = "unhandled kind"; return false;
        }

        private static bool IsFinite(double v) { return !double.IsNaN(v) && !double.IsInfinity(v); }
    }
}
