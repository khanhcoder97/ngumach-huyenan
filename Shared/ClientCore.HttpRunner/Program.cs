using System;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using NguMach.Client.Core.Guards;

namespace ClientCoreHttpRunner
{
    internal static class Program
    {
        private const string ChestTemplate = "EQ-MK-CHEST-T1-R-COMMON";
        private static int checks;

        private static void Check(bool ok, string name)
        {
            if (!ok) throw new Exception("FAIL: " + name);
            checks++;
            Console.WriteLine("PASS " + name);
        }

        private sealed class Http : IP1Transport, IDisposable
        {
            private readonly HttpClient client;
            public bool LoseTurnInResponseOnce;
            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }
            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                using (var msg = new HttpRequestMessage(new HttpMethod(req.Method), req.Path))
                {
                    if (req.SessionId != null) msg.Headers.Add("X-Session-ID", req.SessionId);
                    msg.Headers.Add("X-Correlation-ID", req.CorrelationId);
                    if (req.Body != null) msg.Content = new StringContent(req.Body, Encoding.UTF8, "application/json");
                    using (var reply = await client.SendAsync(msg, ct))
                    {
                        var body = await reply.Content.ReadAsStringAsync();
                        if (req.Path == "/p1/quests/turnin" && reply.IsSuccessStatusCode && LoseTurnInResponseOnce)
                        {
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
                var r = await c.MoveAsync(dx, 0, CancellationToken.None);
                if (!r.Success) throw new Exception("move: " + (r.Code ?? "?"));
            }
            if (Math.Abs(c.World.self.x - x) > 1.0) throw new Exception("walk failed");
        }

        private static async Task MainAsync(string baseUrl)
        {
            using (var http = new Http(baseUrl))
            {
                var client = new P1Client(http, useWorldV2: true);
                var adapter = new P1ClientAdapter(client);
                var dialogue = new NpcDialoguePresenter(adapter);
                var journal = new QuestJournalPresenter(adapter);

                Check((await client.ConnectAsync(CancellationToken.None)).Success, "connect");
                Check(adapter.ConnectionState == UIConnectionState.Ready, "ready");

                // stale guard demo
                var guard = new StaleResponseGuard();
                guard.BeginSession(client.SessionId, 1);
                Check(guard.IsApplicable(client.SessionId, null, 1), "stale guard accepts current session");

                await WalkTo(client, 42);
                Check((await dialogue.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None)).IsLoaded, "accept");
                foreach (var (t, x) in new[] { ("ENT_MAN_BM_OBJ_BM_PACKAGE_01", 36.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_02", 44.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_03", 52.0) })
                {
                    await WalkTo(client, x);
                    Check((await dialogue.InteractAsync(t, CancellationToken.None)).IsLoaded, "parcel " + t);
                }
                Check((await client.ReadQuestsAsync(CancellationToken.None)).Success, "read quests");
                await WalkTo(client, 64);
                Check((await client.ReadInventoryAsync(CancellationToken.None)).Success, "inv pre");
                Check(client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 0, "pre coin 0");

                http.LoseTurnInResponseOnce = true;
                var first = await dialogue.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(first.IsError && first.ErrorCode == "mutation_outcome_unknown", "lost response");
                Check(adapter.HasPendingMutation, "pending");

                var retry = await adapter.RetryPendingAsync(CancellationToken.None);
                Check(retry.Success && !adapter.HasPendingMutation, "retry success");
                Check(client.LastTurnIn != null && client.LastTurnIn.questState.state == "COMPLETED", "completed");
                Check((await client.ReadInventoryAsync(CancellationToken.None)).Success, "inv post");
                Check(client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "20 coin");
                Check(client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "1 chest");

                // receipt replay guard demo
                var receipt = new MutationReceipt { Key = "k", PayloadHash = "h", Applied = true, CoinGranted = 20, ChestGranted = 1 };
                Check(ReceiptReplayGuard.Evaluate(receipt, "k", "h") == ReplayVerdict.ReplaySuccess, "replay same");
                Check(ReceiptReplayGuard.Evaluate(receipt, "k", "h2") == ReplayVerdict.Conflict, "replay conflict");

                var repeat = await dialogue.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(repeat.IsError && repeat.ErrorCode == "invalid_transition", "repeat rejected");
                Check(client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "no double grant");

                Console.WriteLine("PASS ClientCore HTTP assertions: " + checks);
            }
        }

        private static int Main(string[] args)
        {
            string baseUrl = Environment.GetEnvironmentVariable("P1_BASE_URL");
            if (string.IsNullOrWhiteSpace(baseUrl))
            {
                Console.Error.WriteLine("ClientCoreHttpRunner: UNVERIFIED - no P1_BASE_URL");
                return 2;
            }
            try { using (var c = new HttpClient { Timeout = TimeSpan.FromSeconds(3) }) { var r = c.GetAsync(baseUrl.TrimEnd('/') + "/health").GetAwaiter().GetResult(); if (!r.IsSuccessStatusCode) throw new Exception(); } }
            catch (Exception e) { Console.Error.WriteLine("UNVERIFIED - server unreachable: " + e.Message); return 2; }
            try { MainAsync(baseUrl).GetAwaiter().GetResult(); }
            catch (Exception e) { Console.Error.WriteLine("FAIL: " + e.Message); return 1; }
            if (checks < 10) { Console.Error.WriteLine("FAIL - only " + checks + " assertions"); return 1; }
            return 0;
        }
    }
}
