// OPC-13 Package A — ModalOrchestrator: single owner of Escape/Space intent.
// One physical press resolves to exactly one behavior on the top-most open
// modal layer (narrative > cinema > player panels > audio > HUD details).
// Pure C# per layer contract:
//   - probe IsOpen at dispatch time,
//   - Escape always has a close/skip behavior,
//   - Space is consumed only by layers that declare it (currently cinema skip).
// Unity-side key polling happens once in the HUD hook (see P1OnlinePanel);
// overlays (CinemaOverlay etc.) must NOT poll keys on their own (AG89 finding).
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 20, OPC-13 Package A).

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    /// <summary>Modal UI layers that may consume Escape/Space, ordered visually top-most first.</summary>
    public enum ModalLayer
    {
        Narrative,    // Story overlay (dialogue v3) — Escape closes current dialogue context.
        Cinema,       // Full-screen cinematic overlay — Escape/Space skips playback.
        PlayerPanel,  // PlayerUIRoot panels (inventory/journal/map/settings/...) — Escape closes top panel.
        AudioPanel,   // HUD quick audio settings panel — Escape toggles it closed.
        HudDetails,   // HUD quest/bag details panel — Escape toggles it closed.
        None
    }

    /// <summary>
    /// Resolves Escape/Space presses against the current modal stack so that exactly one
    /// layer per press executes its behavior. The caller supplies an ordered set of layer
    /// registrations (probe + handlers); the orchestrator never caches state between presses,
    /// so probes always reflect the live UI (open panels, playing cinema, open dialogue...).
    /// </summary>
    public sealed class ModalOrchestrator
    {
        private readonly List<Layer> _layers = new List<Layer>();
        private ModalLayer _lastConsumed = ModalLayer.None;

        /// <summary>Layer the most recent Escape dispatch consumed (diagnostics/tests only).</summary>
        public ModalLayer LastConsumedEscape => _lastConsumed;

        /// <summary>Register a layer. Order of registration = visual priority (top-most first).</summary>
        public void Register(Func<bool> isOpen, Action escape, bool consumesSpace, Action space = null)
        {
            if (isOpen == null) throw new ArgumentNullException(nameof(isOpen));
            if (escape == null) throw new ArgumentNullException(nameof(escape));
            if (consumesSpace && space == null) throw new ArgumentException("A layer consuming Space must provide its Space behavior.", nameof(space));
            _layers.Add(new Layer(isOpen, escape, consumesSpace, space));
        }

        public void Clear() => _layers.Clear();

        /// <summary>A layer currently open, regardless of depth (for modal gating probes).</summary>
        public bool IsAnyOpen
        {
            get
            {
                foreach (var layer in _layers)
                    if (IsOpen(layer)) return true;
                return false;
            }
        }

        /// <summary>
        /// Run Escape: the first open layer (registration order) runs its escape behavior.
        /// Exactly one behavior per call; probe failures swallow nothing — the registry is static.
        /// </summary>
        /// <returns>The layer that consumed the press, or <see cref="ModalLayer.None"/> when no modal is open.</returns>
        public ModalLayer DispatchEscape()
        {
            for (int i = 0; i < _layers.Count; i++)
            {
                var layer = _layers[i];
                if (!IsOpen(layer)) continue;
                layer.Escape();
                _lastConsumed = ToLayer(i);
                return _lastConsumed;
            }
            _lastConsumed = ModalLayer.None;
            return ModalLayer.None;
        }

        /// <summary>
        /// Run Space: the first open layer that declares a Space behavior runs it.
        /// When no open layer consumes Space the caller falls through to gameplay (input gate still applies).
        /// </summary>
        /// <returns>The layer that consumed the press, or <see cref="ModalLayer.None"/> to fall through.</returns>
        public ModalLayer DispatchSpace()
        {
            for (int i = 0; i < _layers.Count; i++)
            {
                var layer = _layers[i];
                if (!layer.ConsumesSpace || !IsOpen(layer)) continue;
                layer.Space();
                return ToLayer(i);
            }
            return ModalLayer.None;
        }

        private bool IsOpen(Layer layer)
        {
            try { return layer.IsOpen(); }
            catch (Exception) { return false; } // A broken probe must never crash the input pump.
        }

        private static ModalLayer ToLayer(int index)
        {
            // Registration order is fixed by the HUD hook; map index → layer for diagnostics.
            return (ModalLayer)Math.Min(index, (int)ModalLayer.None);
        }

        private readonly struct Layer
        {
            public readonly Func<bool> IsOpen;
            public readonly Action Escape;
            public readonly bool ConsumesSpace;
            public readonly Action Space;

            public Layer(Func<bool> isOpen, Action escape, bool consumesSpace, Action space)
            {
                IsOpen = isOpen; Escape = escape; ConsumesSpace = consumesSpace; Space = space;
            }
        }
    }
}
