// OPC-13 Package C — HUD safe-area overload policy (pure C#, no Unity dep).
// Decides a controlled scale/hide tiers for the busy player HUD (menu bar +
// pinned-quest tracker) from the viewport and OS safe-area insets: the HUD
// compacts/hides ITSELF inside the safe area instead of spilling over notches,
// punch-holes or stray thumbs. View orientation (top-down world view, curved
// skill arc) is untouched — this never changes logical render/PPU/world zoom.
// _decide is a pure function of (viewport, safe insets, control count) so it is
// fully headless-testable; the MonoBehaviour side applies Scale/DisplayStyle.
// Owner: OpenCode LOCAL — Issue #85 (work order 20, Package C).

using System;

namespace NguMach.Client.Presentation
{
    public enum HudMode { Full, Compact, Hidden }

    public readonly struct HudViewport
    {
        public readonly float WidthPx;
        public readonly float HeightPx;
        /// <summary>OS-guaranteed safe area in pixels from each screen edge.</summary>
        public readonly float SafeLeft;
        public readonly float SafeTop;
        public readonly float SafeRight;
        public readonly float SafeBottom;

        public HudViewport(float widthPx, float heightPx, float safeLeft, float safeTop, float safeRight, float safeBottom)
        {
            WidthPx = Math.Max(0f, widthPx);
            HeightPx = Math.Max(0f, heightPx);
            SafeLeft = Math.Max(0f, safeLeft);
            SafeTop = Math.Max(0f, safeTop);
            SafeRight = Math.Max(0f, safeRight);
            SafeBottom = Math.Max(0f, safeBottom);
        }

        public static readonly HudViewport Desktop1920 = new HudViewport(1920f, 1080f, 0f, 0f, 0f, 0f);
    }

    public readonly struct HudDecision : IEquatable<HudDecision>
    {
        public readonly HudMode Mode;
        /// <summary>Uniform scale for the bar/tracker; 1 in Full mode.</summary>
        public readonly float Scale;
        /// <summary>true when the overload policy hides the pinned-quest tracker box.</summary>
        public readonly bool TrackerHidden;

        public HudDecision(HudMode mode, float scale, bool trackerHidden)
        {
            Mode = mode;
            Scale = scale;
            TrackerHidden = trackerHidden;
        }

        public bool Equals(HudDecision other) => Mode == other.Mode && Scale.Equals(other.Scale) && TrackerHidden == other.TrackerHidden;
        public override bool Equals(object obj) => obj is HudDecision other && Equals(other);
        public override int GetHashCode() => (Mode, Scale, TrackerHidden).GetHashCode();
        public override string ToString() => FormattableString.Invariant($"{Mode}({Scale:0.00}) trackerHidden={TrackerHidden}");
    }

    public static class HudSafeAreaPolicy
    {
        /// <summary>Worst-case width estimate per HUD control button, px (labels + padding).</summary>
        public const float ControlWidthPx = 90f;
        /// <summary>Worst-case width of the menu bar + pinned tracker side by side, px.</summary>
        public const float TrackerWidthPx = 310f;
        /// <summary>Minimum vertical legibility band for the bar, px.</summary>
        public const float BarHeightPx = 90f;
        /// <summary>Extra vertical room needed to keep the tracker readable, px.</summary>
        public const float TrackerHeightPx = 140f;

        private const float MinScale = 0.6f;
        private const float CompactScale = 0.85f;

        /// <summary>
        /// Pure decision: Full (bar + tracker, scale 1) → Compact (tracker hidden,
        /// uniform downscale) → Hidden (viewport too small to be legible at all).
        /// All thresholds apply inside the safe area — insets only shrink usable space.
        /// </summary>
        public static HudDecision Decide(in HudViewport vp, int controlCount)
        {
            float usableW = Math.Max(0f, vp.WidthPx - vp.SafeLeft - vp.SafeRight);
            float usableH = Math.Max(0f, vp.HeightPx - vp.SafeTop - vp.SafeBottom);

            int controls = Math.Max(1, controlCount);
            float barW = controls * ControlWidthPx;
            float fullW = barW + TrackerWidthPx;

            // Legibility floor: nothing meaningfully HUD fits inside the safe area.
            if (usableW < barW * 0.5f || usableH < 72f)
                return new HudDecision(HudMode.Hidden, 1f, trackerHidden: true);

            // Tracker steals width; drop it first, then scale the bar down to fit
            // instead of letting elements cross the safe-area boundary unscaled.
            bool trackerFits = usableW >= fullW && usableH >= TrackerHeightPx;
            if (trackerFits)
                return new HudDecision(HudMode.Full, 1f, trackerHidden: false);

            float scale = Math.Clamp(usableH / BarHeightPx, MinScale, CompactScale);
            return new HudDecision(HudMode.Compact, scale, trackerHidden: true);
        }
    }
}
