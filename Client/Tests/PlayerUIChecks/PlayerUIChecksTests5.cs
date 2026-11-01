// OPC-13 Package A — ModalOrchestrator tests: single Escape/Space owner across
// narrative, cinema, player panels and HUD modals. All fixtures SYNTHETIC; they
// probe the pure-C# orchestrator contract, NOT native VisualElement input
// (native remains UNVERIFIED until the Muse VM packet runs).
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 20).

using System;
using System.Collections.Generic;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    public class ModalOrchestratorTests
    {
        private sealed class SpyLayer
        {
            public bool Open;
            public int EscapeCalls;
            public int SpaceCalls;
            public Func<bool> ProbeOverride;
            public Func<bool> Probe() => ProbeOverride ?? (() => Open);
        }

        private static (ModalOrchestrator orchestrator, SpyLayer narrative, SpyLayer cinema, SpyLayer panels, SpyLayer audio, SpyLayer details) Build()
        {
            var narrative = new SpyLayer();
            var cinema = new SpyLayer();
            var panels = new SpyLayer();
            var audio = new SpyLayer();
            var details = new SpyLayer();
            var orchestrator = new ModalOrchestrator();
            // Same visual registration order as P1OnlinePanel.RegisterModalLayers().
            orchestrator.Register(
                narrative.Probe(), () => { if (narrative.Open) narrative.EscapeCalls++; }, false);
            orchestrator.Register(
                cinema.Probe(), () => { if (cinema.Open) cinema.EscapeCalls++; }, true,
                () => { if (cinema.Open) cinema.SpaceCalls++; });
            orchestrator.Register(
                panels.Probe(), () => { if (panels.Open) panels.EscapeCalls++; }, false);
            orchestrator.Register(
                audio.Probe(), () => { if (audio.Open) audio.EscapeCalls++; }, false);
            orchestrator.Register(
                details.Probe(), () => { if (details.Open) details.EscapeCalls++; }, false);
            return (orchestrator, narrative, cinema, panels, audio, details);
        }

        [Fact]
        public void Escape_ClosedEverything_RunsNoFallback()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
            Assert.Equal(0, narrative.EscapeCalls);
            Assert.Equal(0, cinema.EscapeCalls);
            Assert.Equal(0, panels.EscapeCalls);
            Assert.Equal(0, audio.EscapeCalls);
            Assert.Equal(0, details.EscapeCalls);
        }

        [Fact]
        public void Escape_CinemaOverPanel_OnePressSkipsCinemaOnly()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            cinema.Open = true;
            panels.Open = true;

            Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchEscape());
            Assert.Equal(1, cinema.EscapeCalls);
            Assert.Equal(0, panels.EscapeCalls); // panel below must not close from the same press

            cinema.Open = false;
            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            Assert.Equal(1, panels.EscapeCalls);
        }

        [Fact]
        public void Escape_NarrativeAboveCinema_OnePressOneBehavior()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            narrative.Open = true;
            cinema.Open = true;

            Assert.Equal(ModalLayer.Narrative, orchestrator.DispatchEscape());
            Assert.Equal(1, narrative.EscapeCalls);
            Assert.Equal(0, cinema.EscapeCalls); // AG89 finding: previously cinema also skipped on the same press
        }

        [Fact]
        public void Escape_PriorityChain_AudioThenDetails()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            details.Open = true;
            audio.Open = true;
            panels.Open = true;

            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            panels.Open = false;
            Assert.Equal(ModalLayer.AudioPanel, orchestrator.DispatchEscape());
            audio.Open = false;
            Assert.Equal(ModalLayer.HudDetails, orchestrator.DispatchEscape());
            details.Open = false;
            Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
        }

        [Fact]
        public void Space_CinemaSkips_GameplayFallthroughOtherwise()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();

            // No modal → fall through to gameplay attack.
            Assert.Equal(ModalLayer.None, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls);

            // Panel-only open must NOT consume Space (bag/journal scrolling uses other keys).
            panels.Open = true;
            Assert.Equal(ModalLayer.None, orchestrator.DispatchSpace());
            Assert.Equal(0, cinema.SpaceCalls);

            // Cinematic playing → one Space skips cinema.
            cinema.Open = true;
            Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchSpace());
            Assert.Equal(1, cinema.SpaceCalls);
        }

        [Fact]
        public void BrokenProbe_DispatchesPastIt_WithoutThrowing()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            cinema.ProbeOverride = () => throw new InvalidOperationException("broken probe (synthetic)");
            panels.Open = true;
            Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
            Assert.Equal(1, panels.EscapeCalls);
        }

        [Fact]
        public void IsAnyOpen_ReflectsLiveProbes()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            Assert.False(orchestrator.IsAnyOpen);
            audio.Open = true;
            Assert.True(orchestrator.IsAnyOpen);
        }

        [Fact]
        public void Lifecycle_200Cycles_EachPressConsumesExactlyOneLayer()
        {
            var (orchestrator, narrative, cinema, panels, audio, details) = Build();
            for (int cycle = 0; cycle < 200; cycle++)
            {
                // A cinematic starts over an open panel (story flow timing is out of scope here).
                panels.Open = true;
                cinema.Open = true;
                Assert.Equal(ModalLayer.Cinema, orchestrator.DispatchEscape());
                cinema.Open = false;

                Assert.Equal(ModalLayer.PlayerPanel, orchestrator.DispatchEscape());
                panels.Open = false;

                // A one-off HUD details panel above.
                details.Open = true;
                Assert.Equal(ModalLayer.HudDetails, orchestrator.DispatchEscape());
                details.Open = false;

                // Nothing open → falls through, no handler runs.
                Assert.Equal(ModalLayer.None, orchestrator.DispatchEscape());
                Assert.Equal(ModalLayer.None, orchestrator.LastConsumedEscape);
                Assert.True(cinema.EscapeCalls >= cycle);
            }
            Assert.Equal(200, panels.EscapeCalls);
            Assert.Equal(200, cinema.EscapeCalls);
            Assert.Equal(200, details.EscapeCalls);
            Assert.Equal(0, narrative.EscapeCalls);
            Assert.Equal(0, audio.EscapeCalls);
        }

        [Fact]
        public void Register_RequiresSpaceBehavior_WhenConsumingSpace()
        {
            var orchestrator = new ModalOrchestrator();
            Assert.Throws<ArgumentException>(() => orchestrator.Register(() => false, () => { }, consumesSpace: true));
            Assert.Throws<ArgumentNullException>(() => orchestrator.Register(null, () => { }, false));
            Assert.Throws<ArgumentNullException>(() => orchestrator.Register(() => false, null, false));
        }
    }
}
