// OPC-15 O1 (WO26) — Shape validation for encounter telegraphs (renderer-neutral).
// Cone requires angle/range/normalized facing; circle requires radius; annulus requires
// 0 <= innerRadius < outerRadius. Only cone carries a facing vector; circle/annulus do
// not derive facing from the owner's current position.
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
            if (string.IsNullOrWhiteSpace(s.KindRaw)) { reason = "missing shape kind"; return false; }

            string kind = s.KindRaw.ToUpperInvariant();
            if (kind != "CONE" && kind != "CIRCLE" && kind != "ANNULUS")
            {
                reason = "unknown kind: " + s.KindRaw;
                return false;
            }

            if (!IsFinite(s.CenterXWu) || !IsFinite(s.CenterYWu))
            {
                reason = "center must be finite";
                return false;
            }

            switch (kind)
            {
                case "CONE":
                    if (!s.RangeWu.HasValue || !IsFinite(s.RangeWu.Value) || s.RangeWu.Value <= 0)
                    {
                        reason = "cone rangeWu must be > 0";
                        return false;
                    }
                    if (!s.AngleDegrees.HasValue || !IsFinite(s.AngleDegrees.Value) ||
                        s.AngleDegrees.Value <= 0 || s.AngleDegrees.Value > 360)
                    {
                        reason = "cone angleDegrees must be in (0,360]";
                        return false;
                    }
                    if (!s.FacingX.HasValue || !s.FacingY.HasValue ||
                        !IsFinite(s.FacingX.Value) || !IsFinite(s.FacingY.Value))
                    {
                        reason = "cone facing must be finite";
                        return false;
                    }
                    double length = Math.Sqrt(s.FacingX.Value * s.FacingX.Value + s.FacingY.Value * s.FacingY.Value);
                    if (Math.Abs(length - 1.0) > 0.001)
                    {
                        reason = "cone facing must be normalized";
                        return false;
                    }
                    if (s.RadiusWu.HasValue || s.InnerRadiusWu.HasValue || s.OuterRadiusWu.HasValue)
                    {
                        reason = "cone must not carry radius/annulus fields";
                        return false;
                    }
                    return true;

                case "CIRCLE":
                    if (!s.RadiusWu.HasValue || !IsFinite(s.RadiusWu.Value) || s.RadiusWu.Value <= 0)
                    {
                        reason = "circle radiusWu must be > 0";
                        return false;
                    }
                    if (s.AngleDegrees.HasValue || s.RangeWu.HasValue)
                    {
                        reason = "circle must not carry cone angle/range";
                        return false;
                    }
                    if (s.InnerRadiusWu.HasValue || s.OuterRadiusWu.HasValue)
                    {
                        reason = "circle must not carry annulus radii";
                        return false;
                    }
                    if (s.FacingX.HasValue || s.FacingY.HasValue)
                    {
                        reason = "circle must not carry facing";
                        return false;
                    }
                    return true;

                case "ANNULUS":
                    if (!s.InnerRadiusWu.HasValue || !s.OuterRadiusWu.HasValue)
                    {
                        reason = "annulus radii required";
                        return false;
                    }
                    if (!IsFinite(s.InnerRadiusWu.Value) || !IsFinite(s.OuterRadiusWu.Value))
                    {
                        reason = "annulus radii must be finite";
                        return false;
                    }
                    if (s.InnerRadiusWu.Value < 0)
                    {
                        reason = "innerRadiusWu must be >= 0";
                        return false;
                    }
                    if (s.InnerRadiusWu.Value >= s.OuterRadiusWu.Value)
                    {
                        reason = "innerRadiusWu must be < outerRadiusWu";
                        return false;
                    }
                    if (s.AngleDegrees.HasValue || s.RangeWu.HasValue || s.RadiusWu.HasValue)
                    {
                        reason = "annulus must not carry cone/circle fields";
                        return false;
                    }
                    if (s.FacingX.HasValue || s.FacingY.HasValue)
                    {
                        reason = "annulus must not carry facing";
                        return false;
                    }
                    return true;
            }

            reason = "unhandled kind";
            return false;
        }

        private static bool IsFinite(double value)
        {
            return !double.IsNaN(value) && !double.IsInfinity(value);
        }
    }
}
