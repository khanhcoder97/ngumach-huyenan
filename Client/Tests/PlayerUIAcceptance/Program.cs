// OPC-14 O2 — Real-HTTP acceptance for the PlayerUI presenters.
// Drives the ACTUAL NpcDialoguePresenter / QuestJournalPresenter through
// P1ClientAdapter + P1Client over a private Health server (no stubs, no
// fake grants). Every success claim comes from a server receipt, never from
// a local guess: a lost turn-in response stays pending, the retry reuses the
// same body/idempotency key, the quest must reach COMPLETED, and the reread
// inventory must hold exactly 20 COIN + exactly 1 chest.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 23, OPC-14 O2).
// Exit codes: 0 = pass, 1 = FAIL/zero assertions, 2 = UNVERIFIED (no server).

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace PlayerUIAcceptance
{
    internal static class Program
    {
        private const string ChestTemplate = "EQ-MK-CHEST-T1-R-COMMON";
        private const int MinimumAssertions = 40;

        private static readonly CancellationToken None = CancellationToken.None;
        private static int checks;

        private static void Check(bool ok, string name)
        {
            if (!ok) throw new Exception("FAIL: " + name);
            checks++;
            Console.WriteLine("PASS " + name);
        }

        // ── Real HTTP transport (one lane, records every request) ────────────
        private sealed class Http : IP1Transport, IDisposable
        {
            private readonly HttpClient client;
            public readonly List<P1Request> Requests = new List<P1Request>();

            // Simulate the first turn-in reply being lost after the server committed.
            public bool LoseTurnInResponseOnce;
            // Point the next read at a bogus session path so the client sees session_not_found.
            public bool CorruptSessionPathOnce;

            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }

            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                Requests.Add(req);
                string path = req.Path;
                if (CorruptSessionPathOnce && req.Method == "GET" && path != null && path.LastIndexOf('/') > 0)
                {
                    CorruptSessionPathOnce = false;
                    path = path.Substring(0, path.LastIndexOf('/') + 1) + new string('f', 32);
                }

                using (var msg = new HttpRequestMessage(new HttpMethod(req.Method), path))
                {
                    if (req.SessionId != null) msg.Headers.Add("X-Session-ID", req.SessionId);
                    msg.Headers.Add("X-Correlation-ID", req.CorrelationId);
                    if (req.Body != null) msg.Content = new StringContent(req.Body, Encoding.UTF8, "application/json");
                    using (var reply = await client.SendAsync(msg, ct))
                    {
                        var body = await reply.Content.ReadAsStringAsync();
                        if (req.Path == "/p1/quests/turnin" && reply.IsSuccessStatusCode && LoseTurnInResponseOnce)
                        {
                            // Server committed the grant; the client never sees the receipt.
                            LoseTurnInResponseOnce = false;
                            return new P1HttpReply { StatusCode = 0, CorrelationId = req.CorrelationId };
                        }
                        return new P1HttpReply { StatusCode = (int)reply.StatusCode, Body = body, CorrelationId = req.CorrelationId };
                    }
                }
            }

            public void Dispose() => client.Dispose();
        }

        private static async Task WalkTo(P1Client c, double x)
        {
            for (int i = 0; i < 240 && Math.Abs(c.World.self.x - x) > 0.75; i++)
            {
                await Task.Delay(100);
                double dx = Math.Max(-1, Math.Min(1, (x - c.World.self.x) / 1.2));
                var r = await c.MoveAsync(dx, 0, None);
                if (!r.Success) throw new Exception("move: " + (r.Code ?? "?")); // never silently stall
            }
            if (Math.Abs(c.World.self.x - x) > 1.0) throw new Exception("walk failed to reach x=" + x);
        }

        private static P1Quest FindQuest(P1Client client, string questId)
        {
            return client.Quests?.FirstOrDefault(q => q != null && q.questId == questId);
        }

        private static long CoinAmount(P1Inventory inv)
        {
            if (inv?.currencies == null) return 0;
            return inv.currencies.Where(c => c != null && c.currencyId == "COIN").Sum(c => c.amount);
        }

        private static int ChestCount(P1Inventory inv)
        {
            if (inv?.items == null) return 0;
            return inv.items.Count(i => i != null && i.templateId == ChestTemplate);
        }

        private static int NpcInteractPosts(Http http)
        {
            return http.Requests.Count(r =>
                r.Path != null && r.Path.Contains("/p1/world/interact") && r.Body != null &&
                (r.Body.Contains("ENT_MAN_BM_NPC") || r.Body.Contains("NPC_LYAN") || r.Body.Contains("NPC_TA_VAN_KHANH")));
        }

        private static int PostCount(Http http) =>
            http.Requests.Count(r => string.Equals(r.Method, "POST", StringComparison.Ordinal));

        private static async Task MainAsync(string baseUrl)
        {
            using (var http = new Http(baseUrl))
            {
                var client = new P1Client(http, useWorldV2: true);
                var adapter = new P1ClientAdapter(client);
                var dialogue = new NpcDialoguePresenter(adapter);
                var journal = new QuestJournalPresenter(adapter);

                // ── Session ─────────────────────────────────────────────────
                var connected = await client.ConnectAsync(None);
                Check(connected.Success, "HTTP session connect");
                Check(adapter.ConnectionState == UIConnectionState.Ready, "adapter reports Ready after connect");
                Check(client.World?.self != null, "world snapshot has self");

                // ── Dialogue snapshot is read-only (no NPC interact POST) ───
                int npcPosts = NpcInteractPosts(http);
                var snap = await dialogue.OpenSnapshotAsync("NPC_LYAN", None);
                Check(snap.IsLoaded && snap.Value != null, "NPC dialogue snapshot loaded");
                Check(snap.Value.NpcId == "NPC_LYAN", "snapshot uses canonical NPC id");
                Check(snap.Value.GreetingText == "Lý An", "snapshot carries the catalog display name");
                Check(snap.Value.InteractionTargetEntityId == "ENT_MAN_BM_NPC_LYAN", "snapshot keeps the world entity id");
                Check(NpcInteractPosts(http) == npcPosts, "opening an NPC snapshot never POSTs /p1/world/interact");

                // ── Quest journal + local pin/selection (no wire) ───────────
                Check((await client.ReadQuestsAsync(None)).Success, "initial quest read");
                Check(FindQuest(client, "P00-01")?.state == "AVAILABLE", "P00-01 starts AVAILABLE");
                var journalState = await journal.LoadAsync(None);
                Check(journalState.IsLoaded && journalState.Value != null, "quest journal loaded");
                Check(!journalState.Value.Completed.Any(q => q.QuestId == "P00-01"), "journal does not fake P00-01 as completed");
                int wireBeforePin = http.Requests.Count;
                journal.TogglePin("P00-01");
                Check(journal.State.Value.PinnedQuestId == "P00-01", "journal pin applied locally");
                journal.SetSelection("P00-01");
                Check(journal.State.Value.SelectedQuestId == "P00-01", "journal selection applied locally");
                journal.RefreshFromSnapshot();
                Check(journal.State.Value.PinnedQuestId == "P00-01", "refresh preserves the local pin");
                Check(http.Requests.Count == wireBeforePin, "pin/selection/refresh issue no wire request");

                // ── Accept via the real dialogue presenter ──────────────────
                await WalkTo(client, 42);
                var accepted = await dialogue.AcceptQuestAsync("P00-01", "NPC_LYAN", None);
                Check(accepted.IsLoaded && !accepted.IsError, "dialogue accept succeeded");
                Check(FindQuest(client, "P00-01")?.state == "ACTIVE", "server reports P00-01 ACTIVE after accept");
                Check((await client.ReadInventoryAsync(None)).Success, "inventory read after accept");

                // ── Collect the three parcels through the real presenter ────
                foreach (var (target, x) in new[]
                {
                    ("ENT_MAN_BM_OBJ_BM_PACKAGE_01", 36.0),
                    ("ENT_MAN_BM_OBJ_BM_PACKAGE_02", 44.0),
                    ("ENT_MAN_BM_OBJ_BM_PACKAGE_03", 52.0),
                })
                {
                    await WalkTo(client, x);
                    var node = await dialogue.InteractAsync(target, None);
                    Check(node.IsLoaded && !node.IsError, "parcel collected: " + target);
                }

                // ── READY is not completion ─────────────────────────────────
                Check((await client.ReadQuestsAsync(None)).Success, "quest read after parcels");
                var ready = FindQuest(client, "P00-01");
                Check(ready != null && ready.state == "READY_TO_TURN_IN", "P00-01 is READY_TO_TURN_IN (not COMPLETED)");
                var readyJournal = await journal.LoadAsync(None);
                Check(readyJournal.Value.Active.Any(q => q.QuestId == "P00-01"), "journal still shows P00-01 as active");
                // ── Turn-in with a lost first response ──────────────────────
                await WalkTo(client, 64);
                var turnInSnap = await dialogue.OpenSnapshotAsync("NPC_TA_VAN_KHANH", None);
                Check(turnInSnap.IsLoaded && turnInSnap.Value.NpcId == "NPC_TA_VAN_KHANH", "turn-in NPC snapshot loaded");
                Check(NpcInteractPosts(http) == npcPosts, "turn-in NPC snapshot issues no interact POST");

                Check((await client.ReadInventoryAsync(None)).Success, "inventory read before turn-in");
                Check(CoinAmount(client.Inventory) == 0, "pre-turn-in COIN is 0");
                Check(ChestCount(client.Inventory) == 0, "pre-turn-in chest count is 0");

                http.LoseTurnInResponseOnce = true;
                var first = await dialogue.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None);
                Check(first.IsError, "lost turn-in response surfaces as an error (no local success)");
                Check(first.ErrorCode == "mutation_outcome_unknown", "lost turn-in code is mutation_outcome_unknown");
                Check(adapter.HasPendingMutation, "lost turn-in keeps the mutation pending");
                Check(adapter.ConnectionState == UIConnectionState.UncertainMutation, "adapter reports UncertainMutation while pending");

                var turnIns = http.Requests.Where(r => r.Path == "/p1/quests/turnin").ToList();
                Check(turnIns.Count == 1, "exactly one turn-in request before retry");
                var firstRequest = turnIns[0];

                // ── Retry the SAME pending command (same body/key) ──────────
                var retry = await adapter.RetryPendingAsync(None);
                Check(retry.Success, "RetryPendingAsync succeeded");
                Check(!adapter.HasPendingMutation, "retry cleared the pending mutation");
                Check(adapter.ConnectionState == UIConnectionState.Ready, "adapter returns to Ready after retry");

                turnIns = http.Requests.Where(r => r.Path == "/p1/quests/turnin").ToList();
                Check(turnIns.Count == 2, "exactly two turn-in requests after retry");
                Check(turnIns[1].Body == firstRequest.Body, "retry reuses the exact same request body");
                Check(turnIns[1].CorrelationId == firstRequest.CorrelationId, "retry reuses the same idempotency/correlation key");

                // ── Receipt is the proof, not a READY state ─────────────────
                Check(client.LastTurnIn != null, "turn-in receipt captured");
                Check(client.LastTurnIn.questState.state == "COMPLETED", "receipt quest state is COMPLETED");
                Check(FindQuest(client, "P00-01")?.state == "COMPLETED", "client quest state is COMPLETED");
                var receiptCoin = client.LastTurnIn.rewards.currency
                    .Where(c => c != null && c.currencyId == "COIN").Sum(c => c.amount);
                Check(receiptCoin == 20, "receipt grants exactly 20 COIN");
                Check(client.LastTurnIn.rewards.items.Count(i => i != null && i.templateId == ChestTemplate) == 1,
                    "receipt grants exactly one chest");
                Check(client.LastTurnIn.unlocks != null && client.LastTurnIn.unlocks.Contains("P00-02"),
                    "receipt unlocks P00-02");

                // ── Reread inventory after the retry ───────────────────────
                Check((await client.ReadInventoryAsync(None)).Success, "inventory read after retry");
                Check(CoinAmount(client.Inventory) == 20, "inventory holds exactly 20 COIN after retry");
                Check(ChestCount(client.Inventory) == 1, "inventory holds exactly one chest after retry");
                Check(client.Inventory.items.Count(i => i != null) == 1, "inventory has no synthetic duplicate items");
                var chest = client.Inventory.items.First(i => i != null && i.templateId == ChestTemplate);
                Check(chest.location == "BAG", "chest landed in BAG");

                var completedJournal = await journal.LoadAsync(None);
                Check(completedJournal.Value.Completed.Any(q => q.QuestId == "P00-01"),
                    "journal moved P00-01 into Completed");
                Check(!completedJournal.Value.Active.Any(q => q.QuestId == "P00-01"),
                    "journal no longer lists P00-01 as active");

                // ── A NEW key must be rejected and must not double-grant ───
                var repeat = await dialogue.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None);
                Check(repeat.IsError, "repeat turn-in with a new key is rejected");
                Check(repeat.ErrorCode == "invalid_transition", "repeat turn-in code is invalid_transition, not a receipt");
                Check((await client.ReadInventoryAsync(None)).Success, "inventory read after repeat rejection");
                Check(CoinAmount(client.Inventory) == 20, "repeat turn-in did not double-grant COIN");
                Check(ChestCount(client.Inventory) == 1, "repeat turn-in did not double-grant the chest");

                // ── Delayed reread + rebind share the server truth ─────────
                await Task.Delay(250);
                Check((await client.ReadInventoryAsync(None)).Success, "delayed inventory reread succeeded");
                Check(CoinAmount(client.Inventory) == 20 && ChestCount(client.Inventory) == 1,
                    "delayed reread is stable (20 COIN / 1 chest)");
                var rebound = new QuestJournalPresenter(adapter);
                var reboundState = await rebound.LoadAsync(None);
                Check(reboundState.Value.Completed.Any(q => q.QuestId == "P00-01"),
                    "rebound journal reads the completed quest from the server");
                Check(NpcInteractPosts(http) == npcPosts, "rebind issues no NPC interact POST");

                // ── NPC switch / clear drops stale dialogue ────────────────
                var switchA = await dialogue.OpenSnapshotAsync("NPC_TA_VAN_KHANH", None);
                Check(switchA.Value.NpcId == "NPC_TA_VAN_KHANH", "NPC switch targets the new canonical id");
                var switchB = await dialogue.OpenSnapshotAsync("NPC_LYAN", None);
                Check(switchB.Value.NpcId == "NPC_LYAN", "NPC switch back targets the original id");
                dialogue.Clear();
                Check(dialogue.State.Phase == LoadPhase.Idle, "dialogue Clear returns to Idle");

                // ── Session expiry over real HTTP (404 session_not_found) ──
                using (var expiryHttp = new Http(baseUrl))
                {
                    var expiryClient = new P1Client(expiryHttp, useWorldV2: false);
                    var expiryAdapter = new P1ClientAdapter(expiryClient);
                    Check((await expiryClient.ConnectAsync(None)).Success, "expiry probe session connected");
                    expiryHttp.CorruptSessionPathOnce = true;
                    var expiredRead = await expiryClient.ReadWorldAsync(None);
                    Check(!expiredRead.Success, "bogus session read fails");
                    Check(expiryClient.State == P1ConnectionState.Expired, "client moves to Expired on session_not_found");
                    Check(expiryAdapter.ConnectionState == UIConnectionState.Expired, "adapter maps Expired");
                    Check(expiryClient.SessionId == null, "expiry clears the session id");
                    Check(!(await expiryClient.ReadWorldAsync(None)).Success, "read after expiry requires a new session");
                }

                // No NPC ever went through the closed interact contract.
                Check(NpcInteractPosts(http) == npcPosts, "no NPC interact POST happened for the whole run");

                // Full bag has no server seed/capacity contract yet; keep it explicit.
                Console.WriteLine("UNVERIFIED fullbag: server has no seed/capacity contract for a full-bag turn-in.");

                // Artifact summary (CI uploads the console log).
                Console.WriteLine("REQUESTS " + http.Requests.Count + " POSTS " + PostCount(http) +
                                  " TURNINS " + http.Requests.Count(r => r.Path == "/p1/quests/turnin"));
                Console.WriteLine("PASS PlayerUI acceptance HTTP assertions: " + checks);
            }
        }

        private static int Main(string[] args)
        {
            string baseUrl = Environment.GetEnvironmentVariable("P1_BASE_URL");
            if (string.IsNullOrWhiteSpace(baseUrl))
            {
                Console.Error.WriteLine("PlayerUIAcceptance: UNVERIFIED - no P1_BASE_URL set; cannot run HTTP scenarios.");
                Console.Error.WriteLine("Run Client/Tests/PlayerUIAcceptance/run_acceptance.py to start the private server.");
                return 2; // distinct from pass(0)/fail(1); CI rejects skip
            }

            try
            {
                using (var c = new HttpClient { Timeout = TimeSpan.FromSeconds(3) })
                {
                    var r = c.GetAsync(baseUrl.TrimEnd('/') + "/health").GetAwaiter().GetResult();
                    if (!r.IsSuccessStatusCode) throw new Exception("health not ok: " + (int)r.StatusCode);
                }
            }
            catch (Exception e)
            {
                Console.Error.WriteLine("PlayerUIAcceptance: UNVERIFIED - server unreachable: " + e.Message);
                return 2;
            }

            try
            {
                MainAsync(baseUrl).GetAwaiter().GetResult();
            }
            catch (Exception e)
            {
                Console.Error.WriteLine("PlayerUIAcceptance FAIL: " + e.Message);
                return 1;
            }

            if (checks < MinimumAssertions)
            {
                Console.Error.WriteLine("PlayerUIAcceptance: FAIL - only " + checks + " assertions (< " + MinimumAssertions + ")");
                return 1;
            }
            return 0;
        }
    }
}
