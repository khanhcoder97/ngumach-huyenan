// PlayerUIChecksTests4 — Integrated UI & Lifecycle Tests for Work Order 17:
//   - Section A: 200 open/close/rebind cycles, late cancellation, NPC switch generation
//   - Section B: Concrete P1Client + P1ClientAdapter + scripted transport journey (P00-01)
//   - Section C: Inventory diagnostic warnings & data retention, canonical map bounds, pinned quest
//   - Section D: Single Escape/modal priority & settings bootstrap
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace PlayerUIChecks
{
    // ── Scripted IP1Transport implementation for Concrete Journey ─────────────

    public sealed class ScriptedP1Transport : IP1Transport
    {
        private readonly Dictionary<string, Func<P1Request, P1HttpReply>> _routes =
            new Dictionary<string, Func<P1Request, P1HttpReply>>(StringComparer.OrdinalIgnoreCase);

        public List<P1Request> DispatchedRequests { get; } = new List<P1Request>();

        public static P1HttpReply MakeReply(int statusCode, string body, string correlationId) =>
            new P1HttpReply { StatusCode = statusCode, Body = body, CorrelationId = correlationId };

        public void MapRoute(string method, string pathPrefix, Func<P1Request, P1HttpReply> handler)
        {
            _routes[method + " " + pathPrefix] = handler;
        }

        public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation)
        {
            DispatchedRequests.Add(request);
            foreach (var kv in _routes)
            {
                var parts = kv.Key.Split(' ');
                if (string.Equals(request.Method, parts[0], StringComparison.OrdinalIgnoreCase) &&
                    request.Path.StartsWith(parts[1], StringComparison.OrdinalIgnoreCase))
                {
                    return Task.FromResult(kv.Value(request));
                }
            }
            return Task.FromResult(MakeReply(404, "{\"error\":{\"code\":\"not_found\"}}", request.CorrelationId));
        }
    }

    // ── Work Order 17 Section B: Concrete P1ClientAdapter Journey ─────────────

    public class ConcreteAdapterJourneyTests
    {
        private const string SessionHex = "0123456789abcdef0123456789abcdef";

        [Fact]
        public async Task Journey_FullP0001_ThroughConcreteClientAndAdapter()
        {
            var transport = new ScriptedP1Transport();
            int questRevision = 1;
            string questState = "AVAILABLE";
            int packageCount = 0;
            int inventoryRevision = 1;
            var inventoryItems = new List<string>();

            // 1. Session route
            transport.MapRoute("POST", "/p1/sessions", req =>
            {
                string body = "{\"sessionId\":\"" + SessionHex + "\",\"result\":{" +
                    "\"mapId\":\"MAP_BEN_MUA\",\"revision\":1,\"serverTick\":100," +
                    "\"self\":{\"characterId\":\"CHAR_MINH_KIEM\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":10.0,\"y\":20.0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50}," +
                    "\"entities\":[" +
                        "{\"entityId\":\"ENT_MAN_BM_NPC_LYAN\",\"kind\":\"NPC\",\"x\":15.0,\"y\":25.0}," +
                        "{\"entityId\":\"ENT_MAN_BM_NPC_TA_VAN_KHANH\",\"kind\":\"NPC\",\"x\":50.0,\"y\":50.0}" +
                    "]}}";
                return ScriptedP1Transport.MakeReply(201, body, req.CorrelationId);
            });

            // 2. World route
            transport.MapRoute("GET", "/p1/world/" + SessionHex, req =>
            {
                string body = "{\"sessionId\":\"" + SessionHex + "\",\"result\":{" +
                    "\"mapId\":\"MAP_BEN_MUA\",\"revision\":1,\"serverTick\":105," +
                    "\"self\":{\"characterId\":\"CHAR_MINH_KIEM\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":10.0,\"y\":20.0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50}," +
                    "\"entities\":[" +
                        "{\"entityId\":\"ENT_MAN_BM_NPC_LYAN\",\"kind\":\"NPC\",\"x\":15.0,\"y\":25.0}," +
                        "{\"entityId\":\"ENT_MAN_BM_NPC_TA_VAN_KHANH\",\"kind\":\"NPC\",\"x\":50.0,\"y\":50.0}" +
                    "]}}";
                return ScriptedP1Transport.MakeReply(200, body, req.CorrelationId);
            });

            // 3. Quests read route
            transport.MapRoute("GET", "/p1/quests/" + SessionHex, req =>
            {
                string body = "{\"result\":[{" +
                    "\"questId\":\"P00-01\",\"state\":\"" + questState + "\",\"stepId\":\"STEP_BEN_MUA\"," +
                    "\"revision\":" + questRevision + "," +
                    "\"objectiveCounters\":{\"OBJ_P00_01_PACKAGES\":" + packageCount + "}}]}";
                return ScriptedP1Transport.MakeReply(200, body, req.CorrelationId);
            });

            // 4. Interact route
            transport.MapRoute("POST", "/p1/interact", req =>
            {
                return ScriptedP1Transport.MakeReply(200, "{\"result\":{\"ok\":true}}", req.CorrelationId);
            });

            // 5. Accept quest route
            transport.MapRoute("POST", "/p1/quests/" + SessionHex + "/accept", req =>
            {
                questState = "ACTIVE";
                questRevision++;
                return ScriptedP1Transport.MakeReply(200, "{\"result\":{\"receiptId\":\"RCPT_ACC_01\",\"questId\":\"P00-01\"}}", req.CorrelationId);
            });

            // 6. Turn in quest route
            transport.MapRoute("POST", "/p1/quests/" + SessionHex + "/turn-in", req =>
            {
                questState = "COMPLETED";
                questRevision++;
                inventoryRevision++;
                inventoryItems.Add("EQ-MK-WEAPON-T1-R-COMMON");
                return ScriptedP1Transport.MakeReply(200, "{\"result\":{\"receiptId\":\"RCPT_TURNIN_01\",\"questId\":\"P00-01\"}}", req.CorrelationId);
            });

            // 7. Inventory read route
            transport.MapRoute("GET", "/p1/inventory/" + SessionHex, req =>
            {
                string itemsJson = "";
                for (int i = 0; i < inventoryItems.Count; i++)
                {
                    if (i > 0) itemsJson += ",";
                    itemsJson += "{\"instanceId\":\"INST_" + i + "\",\"templateId\":\"" + inventoryItems[i] + "\",\"location\":\"BAG\",\"slot\":\"" + i + "\",\"stack\":1}";
                }
                string body = "{\"result\":{\"inventoryRevision\":" + inventoryRevision + ",\"items\":[" + itemsJson + "],\"currencies\":[{\"currencyId\":\"CUR_GOLD\",\"amount\":100}]}}";
                return ScriptedP1Transport.MakeReply(200, body, req.CorrelationId);
            });

            // Start concrete client & adapter
            var client = new P1Client(transport);
            var connectResult = await client.ConnectAsync(CancellationToken.None);
            Assert.True(connectResult.Success);
            Assert.Equal(P1ConnectionState.Ready, client.State);

            var adapter = new P1ClientAdapter(client);
            Assert.Equal(UIConnectionState.Ready, adapter.ConnectionState);

            // Presenters wired to concrete adapter
            var dialoguePresenter = new NpcDialoguePresenter(adapter);
            var journalPresenter = new QuestJournalPresenter(adapter);
            var inventoryPresenter = new InventoryPresenter(adapter);

            // Step 1: Initial Quests Read
            await journalPresenter.LoadAsync(CancellationToken.None);
            Assert.Empty(journalPresenter.State.Value.Active);

            // Step 2: Interact with Ly An using world Entity ID
            var dialogueState = await dialoguePresenter.InteractAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);
            Assert.True(dialogueState.IsLoaded);
            Assert.Equal("NPC_LYAN", dialogueState.Value.NpcTemplateId);
            Assert.Equal("ENT_MAN_BM_NPC_LYAN", dialogueState.Value.InteractionTargetEntityId);
            Assert.Contains(dialogueState.Value.Choices, c => c.ActionType == DialogueActionType.AcceptQuest && c.QuestId == "P00-01");

            // Step 3: Accept Quest via Dialogue
            var acceptResult = await dialoguePresenter.AcceptQuestAsync("P00-01", "ENT_MAN_BM_NPC_LYAN", CancellationToken.None);
            Assert.True(acceptResult.IsLoaded);

            // Step 4: Refresh Journal -> P00-01 is Active with 0/3 packages
            await journalPresenter.LoadAsync(CancellationToken.None);
            Assert.Single(journalPresenter.State.Value.Active);
            Assert.Equal("P00-01", journalPresenter.State.Value.Active[0].QuestId);
            Assert.Equal("Thu thập gói hàng Bến Mưa (0/3).", journalPresenter.State.Value.Active[0].ObjectiveDesc);

            // Step 5: Progress packages to 3/3
            packageCount = 3;
            questState = "READY_TO_TURN_IN";
            questRevision++;
            await journalPresenter.LoadAsync(CancellationToken.None);
            Assert.Equal("Báo cáo với Tạ Vân Khanh tại Bến Mưa.", journalPresenter.State.Value.Active[0].ObjectiveDesc);
            Assert.True(journalPresenter.State.Value.Active[0].IsReadyToTurnIn);

            // Step 6: Interact with Ta Van Khanh
            var turnInDialogue = await dialoguePresenter.InteractAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.True(turnInDialogue.IsLoaded);
            Assert.Equal("NPC_TA_VAN_KHANH", turnInDialogue.Value.NpcTemplateId);
            Assert.Contains(turnInDialogue.Value.Choices, c => c.ActionType == DialogueActionType.TurnInQuest && c.QuestId == "P00-01");

            // Step 7: Turn in Quest
            var turnInResult = await dialoguePresenter.TurnInQuestAsync("P00-01", "ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            Assert.True(turnInResult.IsLoaded);

            // Step 8: Read inventory -> Reward item received
            await inventoryPresenter.LoadAsync(CancellationToken.None);
            Assert.True(inventoryPresenter.State.IsLoaded);
            Assert.NotNull(inventoryPresenter.State.Value.GetSlot(0));
            Assert.Equal("EQ-MK-WEAPON-T1-R-COMMON", inventoryPresenter.State.Value.GetSlot(0).TemplateId);
            Assert.Equal("Thường Kiếm Mưa Khởi Minh Kiếm", inventoryPresenter.State.Value.GetSlot(0).DisplayName);

            // Step 9: Read journal -> Quest is Completed
            await journalPresenter.LoadAsync(CancellationToken.None);
            Assert.Empty(journalPresenter.State.Value.Active);
            Assert.Single(journalPresenter.State.Value.Completed);
            Assert.Equal("P00-01", journalPresenter.State.Value.Completed[0].QuestId);
        }
    }

    // ── Work Order 17 Section A: Lifecycle & 200 Cycles Tests ─────────────────

    public class LifecycleAndRobustnessTests
    {
        private sealed class FakeLifetimeAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; } = false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self => new P1Self { characterId = "CHAR_1", classId = "CLASS_MINH_KIEM", x = 10, y = 20, hp = 100, maxHp = 100, mp = 50, maxMp = 50 };
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory { get; set; } = new P1Inventory { inventoryRevision = 1, items = Array.Empty<P1Item>() };
            public P1Quest[] Quests { get; set; } = Array.Empty<P1Quest>();

            public TaskCompletionSource<P1Result> NextRead;

            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => NextRead != null ? NextRead.Task : Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => NextRead != null ? NextRead.Task : Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string targetId, CancellationToken ct) => NextRead != null ? NextRead.Task : Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }

        [Fact]
        public async Task Lifecycle_200OpenCloseRebindCycles_MaintainsConsistency()
        {
            var adapter = new FakeLifetimeAdapter();
            var router = new PanelRouter();
            var invPresenter = new InventoryPresenter(adapter);
            var questPresenter = new QuestJournalPresenter(adapter);

            for (int cycle = 0; cycle < 200; cycle++)
            {
                // Open modal
                router.Open(PlayerPanel.Inventory, UIConnectionState.Ready);
                Assert.Equal(PlayerPanel.Inventory, router.Current);

                // Load inventory
                using (var cts = new CancellationTokenSource())
                {
                    await invPresenter.LoadAsync(cts.Token);
                    Assert.True(invPresenter.State.IsLoaded);
                }

                // Switch modal
                router.Open(PlayerPanel.QuestJournal, UIConnectionState.Ready);
                Assert.Equal(PlayerPanel.QuestJournal, router.Current);

                using (var cts = new CancellationTokenSource())
                {
                    await questPresenter.LoadAsync(cts.Token);
                    Assert.True(questPresenter.State.IsLoaded);
                }

                // Close all
                router.CloseAll();
                Assert.Equal(PlayerPanel.None, router.Current);
                Assert.False(router.IsAnyOpen);
            }
        }

        [Fact]
        public async Task Lifecycle_NpcSwitch_AToB_DropsOldNpcGeneration()
        {
            var adapter = new FakeLifetimeAdapter();
            var tcsA = new TaskCompletionSource<P1Result>(TaskCreationOptions.RunContinuationsAsynchronously);
            var presenter = new NpcDialoguePresenter(adapter);

            // Start interacting with NPC A (delayed)
            adapter.NextRead = tcsA;
            var taskA = presenter.InteractAsync("ENT_MAN_BM_NPC_LYAN", CancellationToken.None);
            Assert.True(presenter.State.IsLoading);

            // Switch to NPC B immediately (immediate complete)
            adapter.NextRead = null;
            var taskB = presenter.InteractAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH", CancellationToken.None);
            await taskB;

            Assert.True(presenter.State.IsLoaded);
            Assert.Equal("NPC_TA_VAN_KHANH", presenter.State.Value.NpcTemplateId);

            // Now complete task A late
            tcsA.SetResult(P1Result.Ok());
            await taskA;

            // Generation token must have preserved B, dropping late completion from A
            Assert.Equal("NPC_TA_VAN_KHANH", presenter.State.Value.NpcTemplateId);
        }

        [Fact]
        public void Lifecycle_DisconnectAndExpiry_ResetsRouter()
        {
            var router = new PanelRouter();
            router.Open(PlayerPanel.Character, UIConnectionState.Ready);
            Assert.True(router.IsAnyOpen);

            // Disconnected connection rejects or closes open panels
            router.Open(PlayerPanel.Inventory, UIConnectionState.Disconnected);
            Assert.False(router.IsAnyOpen);
            Assert.Equal(PlayerPanel.None, router.Current);

            // Reconnect
            router.Open(PlayerPanel.Map, UIConnectionState.Ready);
            Assert.Equal(PlayerPanel.Map, router.Current);

            // Expired closes panels
            router.Open(PlayerPanel.Settings, UIConnectionState.Expired);
            Assert.False(router.IsAnyOpen);
        }
    }

    // ── Work Order 17 Section C: Diagnostics, Map Bounds & Pinned Quest ───────

    public class InventoryDiagnosticsAndMapBoundsTests
    {
        [Fact]
        public async Task Inventory_DuplicateAndOutOfRangeSlots_EmitWarningsAndRetainItems()
        {
            var adapter = new FakeLifetimeAdapter
            {
                Inventory = new P1Inventory
                {
                    inventoryRevision = 1,
                    items = new[]
                    {
                        // Normal slot 0
                        new P1Item { instanceId = "ITEM_0", templateId = "EQ-MK-WEAPON-T1-R-COMMON", location = "BAG", slot = "0", stack = 1 },
                        // Duplicate slot 0 (must produce warning and be relocated to free slot)
                        new P1Item { instanceId = "ITEM_DUP", templateId = "EQ-MK-WEAPON-T1-R-REFINED", location = "BAG", slot = "0", stack = 1 },
                        // Out of range slot 999 (must produce warning and be relocated to free slot)
                        new P1Item { instanceId = "ITEM_OOR", templateId = "EQ-MK-WEAPON-T1-R-SPIRIT", location = "BAG", slot = "999", stack = 1 },
                    }
                }
            };

            var presenter = new InventoryPresenter(adapter);
            await presenter.LoadAsync(CancellationToken.None);

            var state = presenter.State.Value;
            Assert.NotNull(state.DiagnosticWarnings);
            Assert.Contains(state.DiagnosticWarnings, w => w.StartsWith("duplicate_slot_index:0:ITEM_DUP"));
            Assert.Contains(state.DiagnosticWarnings, w => w.StartsWith("out_of_range_slot:999:ITEM_OOR"));

            // Crucial: 0 data loss! All 3 items must be present across slots
            Assert.NotNull(state.GetSlot(0));
            Assert.Equal("ITEM_0", state.GetSlot(0).InstanceId);

            // The duplicate and out-of-range items were safely re-allocated to free slots (e.g. slots 1 and 2)
            bool foundDup = false;
            bool foundOor = false;
            for (int i = 1; i < InventoryViewState.TotalSlots; i++)
            {
                var slot = state.GetSlot(i);
                if (slot != null)
                {
                    if (slot.InstanceId == "ITEM_DUP") foundDup = true;
                    if (slot.InstanceId == "ITEM_OOR") foundOor = true;
                }
            }
            Assert.True(foundDup, "Duplicate slot item was retained in a free slot");
            Assert.True(foundOor, "Out of range item was retained in a free slot");
        }

        [Fact]
        public void MapBounds_CanonicalBounds_ResolvedFromMapId()
        {
            var defaultBounds = MapBounds.ForMap("MAP_BEN_MUA");
            Assert.Equal(0, defaultBounds.XMin);
            Assert.Equal(360, defaultBounds.XMax);
            Assert.Equal(-12, defaultBounds.YMin);
            Assert.Equal(72, defaultBounds.YMax);
            Assert.Equal(360, defaultBounds.Width);
            Assert.Equal(84, defaultBounds.Height);

            var thangLongBounds = MapBounds.ForMap("MAP_THANG_LONG");
            Assert.Equal(0, thangLongBounds.XMin);
            Assert.Equal(900, thangLongBounds.XMax);
            Assert.Equal(-12, thangLongBounds.YMin);
            Assert.Equal(96, thangLongBounds.YMax);
            Assert.Equal(900, thangLongBounds.Width);
            Assert.Equal(108, thangLongBounds.Height);
        }

        [Fact]
        public void QuestJournal_PinnedQuest_ExposesTitleAndObjective()
        {
            var q = new P1Quest
            {
                questId = "P00-01",
                state = "ACTIVE",
                stepId = "STEP_BEN_MUA",
                revision = 1,
                objectiveCounters = new Dictionary<string, int> { ["OBJ_P00_01_PACKAGES"] = 1 }
            };

            var view = new QuestEntryView(q, "Khởi Đầu Tại Bến Mưa", "Thu thập gói hàng Bến Mưa (1/3).");
            var journalState = new QuestJournalViewState(
                new[] { view },
                Array.Empty<QuestEntryView>(),
                selectedQuestId: null,
                hasPinnedTracker: true,
                pinnedQuestId: "P00-01");

            Assert.Equal("P00-01", journalState.PinnedQuestId);
            Assert.NotNull(journalState.PinnedQuest);
            Assert.Equal("Khởi Đầu Tại Bến Mưa", journalState.PinnedQuest.Title);
            Assert.Equal("Thu thập gói hàng Bến Mưa (1/3).", journalState.PinnedQuest.ObjectiveDesc);
        }

        private sealed class FakeLifetimeAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; } = false;
            public string LastErrorCode => null;
            public string LastCorrelationId => null;
            public P1Self Self => new P1Self { characterId = "CHAR_1", classId = "CLASS_MINH_KIEM", x = 10, y = 20, hp = 100, maxHp = 100, mp = 50, maxMp = 50 };
            public P1World World => null;
            public P1WorldV2 WorldV2 => null;
            public P1Inventory Inventory { get; set; } = new P1Inventory { inventoryRevision = 1, items = Array.Empty<P1Item>() };
            public P1Quest[] Quests { get; set; } = Array.Empty<P1Quest>();

            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> AcceptQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> TurnInQuestAsync(string q, string n, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> InteractAsync(string targetId, CancellationToken ct) => Task.FromResult(P1Result.Ok());
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) => Task.FromResult(P1Result.Ok());
        }
    }
}
