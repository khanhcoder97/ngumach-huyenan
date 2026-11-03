// OPC-14 O3 — Unity EditMode tests: input focus / modal priority.
// Uses the real ModalOrchestrator (Presentation namespace), never a stale duplicate type.
// Native focus/Tab behavior itself is UNVERIFIED_NATIVE until run on Unity 6000.3.17f1.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 23, OPC-14 O3).

using NUnit.Framework;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1.Tests
{
    public class PlayerUIInputFocusTests
    {
        [Test]
        public void ModalOrchestrator_SpaceBlockedByTopmostOpenLayer()
        {
            var modal = new ModalOrchestrator();
            int cinemaSkips = 0;
            modal.Register(() => true, () => { }, false);                       // narrative top (non-consuming)
            modal.Register(() => true, () => { }, true, () => cinemaSkips++);   // cinema below
            Assert.AreEqual(ModalLayer.Narrative, modal.DispatchSpace());
            Assert.AreEqual(0, cinemaSkips);
        }

        [Test]
        public void ModalOrchestrator_NoOpenLayer_FallsThroughToGameplay()
        {
            var modal = new ModalOrchestrator();
            modal.Register(() => false, () => { }, true, () => { });
            Assert.AreEqual(ModalLayer.None, modal.DispatchSpace());
            Assert.AreEqual(ModalLayer.None, modal.DispatchEscape());
        }

        [Test]
        public void ModalOrchestrator_EscapeConsumesOnlyTopmostOpenLayer()
        {
            var modal = new ModalOrchestrator();
            int top = 0, below = 0;
            modal.Register(() => true, () => top++, false);
            modal.Register(() => true, () => below++, false);
            Assert.AreEqual(ModalLayer.Narrative, modal.DispatchEscape());
            Assert.AreEqual(1, top);
            Assert.AreEqual(0, below);
        }
    }
}
