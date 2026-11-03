// OPC-14 M1 — Accessibility policy (pure C#, no Unity dep).
// Consumers (cinema transitions, loading pulse, highlights, hotkey labels, tooltips)
// read these decisions instead of ad-hoc booleans. World VFX/camera shake are out of
// scope and stay explicitly UNSUPPORTED (never advertise "reduce all effects").
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 21, OPC-14 M1).
//
// Settings are local preferences only — never character save / offline progression.

using System;

namespace NguMach.Client.Presentation
{
    public static class AccessibilityPolicy
    {
        /// <summary>Whether UI motion (transitions, loading pulse) should animate.</summary>
        public static bool MotionEnabled(bool reducedMotion) => !reducedMotion;

        /// <summary>Whether flash/highlight effects should play.</summary>
        public static bool FlashEnabled(bool reducedFlash) => !reducedFlash;

        /// <summary>Whether hotkey labels should be shown.</summary>
        public static bool HotkeyLabelsVisible(bool showInputHints) => showInputHints;

        /// <summary>
        /// Effective text scale clamped to a readable, non-clipping range.
        /// Native-wide relayout of explicit-size labels is a Muse-VM item; this policy
        /// only guarantees the root scale stays inside the supported band.
        /// </summary>
        public static float TextScale(float textSize) => Math.Max(0.75f, Math.Min(1.5f, textSize));

        /// <summary>
        /// Whether a UI element of the given rendered height fits inside a container
        /// of the given height at the current text scale (no clipping).
        /// </summary>
        public static bool FitsVertically(float elementHeightPx, float containerHeightPx, float textSize)
        {
            if (containerHeightPx <= 0f) return false;
            float scale = TextScale(textSize);
            return elementHeightPx * scale <= containerHeightPx + 0.5f;
        }

        /// <summary>
        /// Whether horizontal content fits without clipping (for tooltips/labels).
        /// </summary>
        public static bool FitsHorizontally(float contentWidthPx, float containerWidthPx, float textSize)
        {
            if (containerWidthPx <= 0f) return false;
            float scale = TextScale(textSize);
            return contentWidthPx * scale <= containerWidthPx + 0.5f;
        }
    }
}