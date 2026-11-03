// OPC-14 M1 — HUD overflow policy (pure C#, no Unity dep).
// When the viewport cannot fit all menu buttons at the minimum touch target,
// collapse the overflow ones into a single "..." menu instead of hiding all access.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 21, OPC-14 M1).

using System;

namespace NguMach.Client.Presentation
{
    public readonly struct HudOverflowDecision
    {
        public readonly int VisibleCount;   // buttons shown inline
        public readonly bool HasOverflow;    // true when at least one button collapsed
        public HudOverflowDecision(int visibleCount, bool hasOverflow)
        {
            VisibleCount = Math.Max(0, visibleCount);
            HasOverflow = hasOverflow;
        }
    }

    public static class HudOverflowPolicy
    {
        public const float MinTouchTargetPx = 44f;
        public const float ButtonGapPx = 4f;
        public const float OverflowButtonWidthPx = 52f;

        /// <summary>
        /// Decide how many of <paramref name="buttonCount"/> buttons fit inline given
        /// <paramref name="usableWidthPx"/>. At least the overflow button is kept when
        /// nothing else fits, so menu/settings access is never fully lost.
        /// </summary>
        public static HudOverflowDecision Decide(int buttonCount, float usableWidthPx)
        {
            if (buttonCount <= 0) return new HudOverflowDecision(0, false);
            if (usableWidthPx <= 0f) return new HudOverflowDecision(0, true);

            int n = buttonCount;
            // Try to fit all; if not, drop one at a time keeping room for overflow button.
            while (n > 0)
            {
                float width = n * (MinTouchTargetPx + ButtonGapPx) + (n < buttonCount ? OverflowButtonWidthPx + ButtonGapPx : 0f);
                if (width <= usableWidthPx) return new HudOverflowDecision(n, n < buttonCount);
                n--;
            }
            // Nothing fits except the overflow button itself.
            return new HudOverflowDecision(0, true);
        }
    }
}