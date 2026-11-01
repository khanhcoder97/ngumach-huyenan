// OPC-14 M4 — Unity EditMode tests: input focus / modal priority.
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.P1;

namespace NguMach.Client.P1.Tests
{
    public class PlayerUIInputFocusTests
    {
        [Test]
        public void ModalOrchestrator_SpaceBlockedByTopmostOpenLayer()
        {
            var modal = new ModalOrchestration();
            int cinemaSkips = 0;
            modal.Register(() => true, () => { }, false);                       // narrative top
            modal.Register(() => true, () => { }, true, () => cinemaSkips++);   // cinema
            Assert.AreEqual(ModalLayer.Narrative, modal.DispatchSpace());
            Assert.AreEqual(0, cinemaSkips);
        }
    }
}
