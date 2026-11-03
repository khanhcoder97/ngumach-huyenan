// OPC-14 O3 — Unity EditMode tests: real adapter + document composition, route/visible
// tree assertions before the 200-cycle soak, and two-document independence.
// Run via Unity Test Runner (EditMode) on Unity 6000.3.17f1. Muse VM: link this assembly.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 23, OPC-14 O3).

using System;
using System.Threading;
using System.Threading.Tasks;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1.Tests
{
    public class PlayerUICompositionTests
    {
        private const string SessionId = "0123456789abcdef0123456789abcdef";

        private GameObject hostA;
        private GameObject hostB;
        private UIDocument docA;
        private UIDocument docB;
        private PlayerUIRoot rootA;
        private PlayerUIRoot rootB;
        private P1ClientAdapter adapterA;
        private P1ClientAdapter adapterB;

        [SetUp]
        public void SetUp()
        {
            hostA = new GameObject("PlayerUI_Host_A");
            docA = hostA.AddComponent<UIDocument>();
            rootA = PlayerUIFactory.Create(hostA, docA);
            adapterA = ConnectAdapter();

            hostB = new GameObject("PlayerUI_Host_B");
            docB = hostB.AddComponent<UIDocument>();
            rootB = PlayerUIFactory.Create(hostB, docB);
            adapterB = ConnectAdapter();
        }

        [TearDown]
        public void TearDown()
        {
            if (rootA != null) rootA.Close();
            if (rootB != null) rootB.Close();
            if (hostA != null) UnityEngine.Object.DestroyImmediate(hostA);
            if (hostB != null) UnityEngine.Object.DestroyImmediate(hostB);
        }

        private static P1ClientAdapter ConnectAdapter()
        {
            var client = new P1Client(new StubTransport(), useWorldV2: false);
            var result = client.ConnectAsync(CancellationToken.None).GetAwaiter().GetResult();
            Assert.IsTrue(result.Success, "stub connect failed: " + result.Code);
            Assert.AreEqual(UIConnectionState.Ready, new P1ClientAdapter(client).ConnectionState);
            return new P1ClientAdapter(client);
        }

        [Test]
        public void TwoDocuments_IndependentRootsAndVisibleTrees()
        {
            rootA.Initialize(adapterA, docA);
            rootB.Initialize(adapterB, docB);
            Assert.IsTrue(rootA.IsInitialized(docA));
            Assert.IsTrue(rootB.IsInitialized(docB));
            Assert.AreNotSame(rootA, rootB);

            rootA.OpenPanel(PlayerPanel.Inventory);
            Assert.AreEqual(PlayerPanel.Inventory, rootA.Router.Current);
            Assert.IsTrue(rootA.IsPanelVisible(PlayerPanel.Inventory));
            Assert.AreEqual(PlayerPanel.None, rootB.Router.Current);
            Assert.IsFalse(rootB.IsPanelVisible(PlayerPanel.Inventory));

            rootA.CloseTop();
            Assert.AreEqual(PlayerPanel.None, rootA.Router.Current);
            Assert.IsFalse(rootA.IsPanelVisible(PlayerPanel.Inventory));
            Assert.AreEqual(PlayerPanel.None, rootB.Router.Current);
        }

        [Test]
        public void RouteAndVisibleTree_AreCorrectBeforeSoak()
        {
            rootA.Initialize(adapterA, docA);
            var panels = new[]
            {
                PlayerPanel.Inventory, PlayerPanel.Character, PlayerPanel.QuestJournal,
                PlayerPanel.Settings, PlayerPanel.Map
            };
            foreach (var panel in panels)
            {
                rootA.OpenPanel(panel);
                Assert.AreEqual(panel, rootA.Router.Current, "route " + panel);
                Assert.IsTrue(rootA.IsPanelVisible(panel), "visible tree " + panel);
                rootA.CloseTop();
                Assert.AreEqual(PlayerPanel.None, rootA.Router.Current, "closed " + panel);
                Assert.IsFalse(rootA.IsPanelVisible(panel), "hidden tree " + panel);
            }
        }

        [Test]
        public void OpenClose_200Cycles_NoRouteOrVisibilityLeak()
        {
            rootA.Initialize(adapterA, docA);
            for (int i = 0; i < 200; i++)
            {
                rootA.OpenPanel(PlayerPanel.Inventory);
                Assert.AreEqual(PlayerPanel.Inventory, rootA.Router.Current);
                Assert.IsTrue(rootA.IsPanelVisible(PlayerPanel.Inventory));

                rootA.OpenPanel(PlayerPanel.QuestJournal);
                Assert.AreEqual(PlayerPanel.QuestJournal, rootA.Router.Current);
                Assert.IsTrue(rootA.IsPanelVisible(PlayerPanel.QuestJournal));
                Assert.IsFalse(rootA.IsPanelVisible(PlayerPanel.Inventory));

                rootA.OpenPanel(PlayerPanel.Map);
                rootA.CloseTop();
                rootA.CloseTop();
                Assert.AreEqual(PlayerPanel.None, rootA.Router.Current, "cycle " + i);
                Assert.IsFalse(rootA.IsPanelVisible(PlayerPanel.QuestJournal), "cycle " + i);
            }
        }

        [Test]
        public void Rebind_DoesNotDuplicateComponents()
        {
            rootA.Initialize(adapterA, docA);
            var before = hostA.GetComponents<PlayerUIRoot>().Length;
            PlayerUIFactory.Create(hostA, docA); // idempotent rebind, same document
            Assert.AreEqual(before, hostA.GetComponents<PlayerUIRoot>().Length);
        }

        // Minimal real wire: P1Client + P1ClientAdapter with a deterministic transport.
        private sealed class StubTransport : IP1Transport
        {
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                string body;
                int status = 200;
                if (request.Path == "/p1/sessions")
                {
                    status = 201;
                    body = Response(request, WorldResult());
                }
                else if (request.Path.StartsWith("/p1/inventory/", StringComparison.Ordinal))
                {
                    body = Response(request, "{\"inventoryRevision\":0,\"items\":[],\"currencies\":[]}");
                }
                else if (request.Path.StartsWith("/p1/quests/", StringComparison.Ordinal))
                {
                    body = Response(request, "[]");
                }
                else if (request.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                {
                    body = Response(request, WorldResult());
                }
                else
                {
                    status = 404;
                    body = "";
                }
                return Task.FromResult(new P1HttpReply
                {
                    StatusCode = status,
                    Body = body,
                    CorrelationId = request.CorrelationId
                });
            }

            private static string Response(P1Request request, string resultJson)
                => "{\"schemaVersion\":1,\"requestId\":\"" + request.CorrelationId +
                   "\",\"sessionId\":\"" + SessionId + "\",\"result\":" + resultJson + "}";

            private static string WorldResult()
                => "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{" +
                   "\"characterId\":\"char_test\",\"classId\":\"CLASS_MINH_KIEM\"," +
                   "\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0}," +
                   "\"entities\":[]}";
        }
    }
}
