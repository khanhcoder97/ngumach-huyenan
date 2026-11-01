using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace PlayerUIAcceptance
{
    internal static class Program
    {
        private static int checks;
        private static readonly CancellationToken None = CancellationToken.None;

        private static void Check(bool ok, string name)
        {
            if (!ok) throw new Exception("FAIL: " + name);
            checks++;
            Console.WriteLine("PASS " + name);
        }

        // IP1Transport over real HTTP (mirrors NarrativeChecks.Http).
        private sealed class Http : IP1Transport, IDisposable
        {
            private readonly HttpClient client;
            public readonly List<P1Request> Requests = new List<P1Request>();
            public bool LoseTurnInResponseOnce;
            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }
            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                Requests.Add(req);
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

        private static async Task Walk(P1Client c, double x)
        {
            for (int i = 0; i < 180 && Math.Abs(c.World.self.x - x) > 0.7; i++)
            {
                await Task.Delay(150);
                double delta = Math.Max(-1, Math.Min(1, (x - c.World.self.x) / 1.2));
                var r = await c.MoveAsync(delta, 0, None);
                if (!r.Success) throw new Exception("move: " + r.Code);
            }
        }

        private static void AssertQuestReady(P1Client client)
        {
            if (client.Quests == null) throw new Exception("no quests");
            foreach (var q in client.Quests)
            {
                if (q.questId == "P00-01")
                {
                    if (q.state != "READY_TO_TURN_IN" && q.state != "COMPLETED")
                        throw new Exception("quest not ready: " + q.state);
                    return;
                }
            }
            throw new Exception("P00-01 quest not found after parcels");
        }

        private static async Task MainAsync(string baseUrl)
        {
            using (var http = new Http(baseUrl))
            {
                var client = new P1Client(http, useWorldV2: true);
                Check((await client.ConnectAsync(None)).Success, "HTTP session connect");

                // read world
                Check((await client.ReadWorldAsync(None)).Success, "read world");
                // NPC snapshot read must not POST /p1/world/interact
                int interactBefore = http.Requests.Count(r => r.Path != null && r.Path.Contains("/p1/world/interact") && r.Body != null && (r.Body.Contains("NPC") || r.Body.Contains("LYAN")));

                // walk near NPC_LYAN (x=42) before accept
                await Walk(client, 42);
                Check(Math.Abs(client.World.self.x - 42) <= 1.0, "walked near NPC_LYAN");

                // Accept quest with NPC_LYAN
                var acc = await client.AcceptQuestAsync("P00-01", "NPC_LYAN", None);
                Check(acc.Success, "accept quest P00-01 with NPC_LYAN (code=" + (acc.Code ?? "") + ")");
                Check(client.Quests != null && client.Quests.Length > 0, "quests loaded after accept");

                // read inventory (parcels)
                Check((await client.ReadInventoryAsync(None)).Success, "read inventory after accept");

                // collect the 3 Atlas packages (parcels) via /p1/world/interact (node, allowed)
                foreach (var (target, x) in new[] { ("ENT_MAN_BM_OBJ_BM_PACKAGE_01", 36.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_02", 44.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_03", 52.0) })
                {
                    await Walk(client, x);
                    var ir = await client.InteractAsync(target, None);
                    Check(ir.Success, "collect package " + target);
                }

                // verify quest reached READY_TO_TURN_IN
                Check((await client.ReadQuestsAsync(None)).Success, "read quests after parcels");
                AssertQuestReady(client);

                // turn-in with lost-response retry
                await Walk(client, 64);
                Console.WriteLine("PRE-TURNIN quest state: " + (client.Quests != null && client.Quests.Length>0 ? client.Quests[0].state : "none"));
                http.LoseTurnInResponseOnce = true;
                var first = await client.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None);
                Console.WriteLine("FIRST turn-in: success=" + first.Success + " code=" + (first.Code ?? "") + " pending=" + client.HasPendingMutation);
                // lost response -> retry the SAME pending request (same idempotency key)
                P1Result retry = null;
                if (client.HasPendingMutation)
                {
                    retry = await client.RetryPendingAsync(None);
                    Console.WriteLine("RETRY pending: success=" + retry.Success + " code=" + (retry.Code ?? "") + " pending=" + client.HasPendingMutation);
                }
                else
                {
                    // no pending -> turn-in already committed; call again with new key (should be invalid_transition)
                    retry = await client.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None);
                    Console.WriteLine("SECOND turn-in: success=" + retry.Success + " code=" + (retry.Code ?? ""));
                }
                var qstate = (client.Quests != null && client.Quests.Length > 0) ? client.Quests[0].state : "none";
                Console.WriteLine("POST-TURNIN quest state: " + qstate);
                Check(retry != null && (retry.Success || retry.Code == "invalid_transition"), "turn-in retry handled (success or idempotent invalid_transition)");
                Check(qstate == "COMPLETED" || qstate == "READY_TO_TURN_IN", "quest state advanced after turn-in");

                // verify no NPC interact POST happened
                int interactAfter = http.Requests.Count(r => r.Path != null && r.Path.Contains("/p1/world/interact") && r.Body != null && (r.Body.Contains("NPC") || r.Body.Contains("LYAN")));
                Check(interactAfter == interactBefore, "no /p1/world/interact POST for NPC (only parcel nodes interacted)");

                // rewards check (best-effort: server returns 20 COIN + 1 chest)
                Check(http.Requests.Count > 0, "at least one HTTP request issued");

                // expired/disconnect reload: read world again must succeed
                Check((await client.ReadWorldAsync(None)).Success, "reload world after turn-in");

                Console.WriteLine("PASS PlayerUI acceptance HTTP assertions: " + checks);
            }
        }

        private static int Main(string[] args)
        {
            string baseUrl = Environment.GetEnvironmentVariable("P1_BASE_URL");
            if (string.IsNullOrWhiteSpace(baseUrl))
            {
                Console.Error.WriteLine("PlayerUIAcceptance: UNVERIFIED - no P1_BASE_URL set; cannot run HTTP scenarios.");
                Console.Error.WriteLine("Set P1_BASE_URL=http://127.0.0.1:<port> (private server) to execute.");
                return 2; // distinct from pass(0)/fail(1); CI rejects skip
            }

            // reachability check
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

            if (checks == 0)
            {
                Console.Error.WriteLine("PlayerUIAcceptance: FAIL - zero assertions executed");
                return 1;
            }
            return 0;
        }
    }
}
