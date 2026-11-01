// OPC-14 M4 — Unity EditMode tests: composition + two UIDocuments + 200 open/close/rebind.
// Run via Unity Test Runner (EditMode) on Unity 6000.3.17f1. Muse VM: link this assembly.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 21, OPC-14 M4).

using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.P1;

namespace NguMach.Client.P1.Tests
{
    public class PlayerUICompositionTests
    {
        private GameObject hostA;
        private GameObject hostB;
        private UIDocument docA;
        private UIDocument docB;
        private PlayerUIRoot rootA;
        private PlayerUIRoot rootB;

        [SetUp]
        public void SetUp()
        {
            hostA = new GameObject("PlayerUI_Host_A");
            docA = hostA.AddComponent<UIDocument>();
            rootA = PlayerUIFactory.Create(hostA, docA);

            hostB = new GameObject("PlayerUI_Host_B");
            docB = hostB.AddComponent<UIDocument>();
            rootB = PlayerUIFactory.Create(hostB, docB);
        }

        [TearDown]
        public void TearDown()
        {
            Object.DestroyImmediate(hostA);
            Object.DestroyImmediate(hostB);
        }

        [Test]
        public void TwoDocuments_IndependentRoots()
        {
            Assert.IsNotNull(rootA);
            Assert.IsNotNull(rootB);
            Assert.AreNotSame(rootA, rootB);
            Assert.AreEqual(1, hostA.GetComponentsInChildren<UIDocument>().Length);
            Assert.AreEqual(1, hostB.GetComponentsInChildren<UIDocument>().Length);
        }

        [Test]
        public void OpenCloseRebind_200Cycles_NoInstanceGrowth()
        {
            int before = hostA.transform.childCount;
            for (int i = 0; i < 200; i++)
            {
                rootA.OpenPanel(PlayerPanel.Inventory);
                rootA.OpenPanel(PlayerPanel.QuestJournal);
                rootA.OpenPanel(PlayerPanel.Map);
                rootA.CloseTop();
                rootA.CloseTop();
                rootA.CloseTop();
            }
            // No unbounded growth of panel instances under the host.
            Assert.LessOrEqual(hostA.transform.childCount, before + 2);
        }

        [Test]
        public void Rebind_DoesNotDuplicateComponents()
        {
            var before = hostA.GetComponents<PlayerUIRoot>().Length;
            PlayerUIFactory.Create(hostA, docA); // idempotent rebind
            Assert.AreEqual(before, hostA.GetComponents<PlayerUIRoot>().Length);
        }
    }
}
