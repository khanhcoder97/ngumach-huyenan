using System;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace ClientCoreHttpRunner
{
    internal static class Program
    {
        private const string ChestTemplate = "EQ-MK-CHEST-T1-R-COMMON";
        private const string CharacterA = "CHR_WO26_ALPHA_A";
        private const string CharacterB = "CHR_WO26_ALPHA_B";
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
            public string LastTurnInBody;
            public bool LoseTurnInResponseOnce;
            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }
            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                if (req.Path == "/p1/quests/turnin" && req.Body != null) LastTurnInBody = req.Body;
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

        // Simulates a server-side session expiry without restarting the server: the next
        // matching request carries an unknown X-Session-ID. The server genuinely returns
        // session_not_found; this is not a client-side shortcut.
        private sealed class ExpiringTransport : IP1Transport, IDisposable
        {
            private readonly Http inner;
            public bool ExpireTurnInOnce;
            public bool ExpireWorldOnce;
            public ExpiringTransport(Http inner) { this.inner = inner; }
            public Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                if (req.Path == "/p1/quests/turnin" && ExpireTurnInOnce)
                {
                    ExpireTurnInOnce = false;
                    req = req.WithSession("ffffffffffffffffffffffffffffffff");
                }
                else if (req.Path.Contains("/world/", StringComparison.Ordinal) && ExpireWorldOnce)
                {
                    ExpireWorldOnce = false;
                    int slash = req.Path.LastIndexOf('/');
                    string bogusPath = req.Path.Substring(0, slash + 1) + "ffffffffffffffffffffffffffffffff";
                    Console.WriteLine("EXPIRING world request: " + req.Path);
                    req = new P1Request(req.Method, bogusPath, req.Body, req.SessionId, req.CorrelationId);
                }
                return inner.SendAsync(req, ct);
            }
            public void Dispose() => inner.Dispose();
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

        private static async Task PrepareP00_01(P1Client c, NpcDialoguePresenter dialogue, string tag)
        {
            await WalkTo(c, 42);
            Check((await dialogue.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None)).IsLoaded, tag + " accept");
            foreach (var (t, x) in new[] { ("ENT_MAN_BM_OBJ_BM_PACKAGE_01", 36.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_02", 44.0), ("ENT_MAN_BM_OBJ_BM_PACKAGE_03", 52.0) })
            {
                await WalkTo(c, x);
                Check((await dialogue.InteractAsync(t, CancellationToken.None)).IsLoaded, tag + " parcel " + t);
            }
            Check((await c.ReadQuestsAsync(CancellationToken.None)).Success, tag + " read quests");
            await WalkTo(c, 64);
            Check((await c.ReadInventoryAsync(CancellationToken.None)).Success, tag + " inv before turnin");
        }

        private static async Task<HttpResponseMessage> RawPost(string baseUrl, string path, string body, string sessionId)
        {
            using (var http = new HttpClient())
            {
                var msg = new HttpRequestMessage(HttpMethod.Post, baseUrl.TrimEnd('/') + path)
                {
                    Content = new StringContent(body, Encoding.UTF8, "application/json")
                };
                msg.Headers.Add("X-Session-ID", sessionId);
                msg.Headers.Add("X-Correlation-ID", Guid.NewGuid().ToString("N"));
                return await http.SendAsync(msg);
            }
        }

        private static async Task MainAsync(string baseUrl)
        {
            using (var httpA = new Http(baseUrl))
            using (var expB = new ExpiringTransport(new Http(baseUrl)))
            using (var sessionA = new ClientSession(httpA, ownsTransport: true, useWorldV2: true,
                       requestTimeout: TimeSpan.FromSeconds(15), characterId: CharacterA))
            using (var sessionB = new ClientSession(expB, ownsTransport: true, useWorldV2: true,
                       requestTimeout: TimeSpan.FromSeconds(15), characterId: CharacterB))
            {
                // ---------- A: normal flow + lost response + fresh inventory ----------
                Check((await sessionA.ConnectAsync()).Success, "A connect");
                Check(sessionA.Adapter.ConnectionState == UIConnectionState.Ready, "A ready");
                Check(sessionA.Client.World.self.characterId == CharacterA, "A identity");

                var dialogueA = new NpcDialoguePresenter(sessionA.Adapter);
                Check((await sessionA.Client.ReadInventoryAsync(CancellationToken.None)).Success, "A inv pre");
                Check(sessionA.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 0, "A pre coin 0");

                await PrepareP00_01(sessionA.Client, dialogueA, "A");
                httpA.LoseTurnInResponseOnce = true;
                var first = await dialogueA.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(first.IsError && first.ErrorCode == "mutation_outcome_unknown", "A lost response");
                Check(sessionA.Adapter.HasPendingMutation, "A pending");
                Check(!string.IsNullOrWhiteSpace(httpA.LastTurnInBody), "A captured mutation body");

                var retry = await sessionA.Adapter.RetryPendingAsync(CancellationToken.None);
                Check(retry.Success && !sessionA.Adapter.HasPendingMutation, "A retry same key success");
                Check((await sessionA.Client.ReadInventoryAsync(CancellationToken.None)).Success, "A inv post");
                Check(sessionA.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "A 20 coin");
                Check(sessionA.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "A 1 chest");

                var repeat = await dialogueA.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(repeat.IsError && repeat.ErrorCode == "invalid_transition", "A repeat rejected");
                // Fresh read after reject, specifically not the cached inventory above.
                Check((await sessionA.Client.ReadInventoryAsync(CancellationToken.None)).Success, "A inv read after reject");
                Check(sessionA.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "A no double grant");
                Check(sessionA.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "A no double chest");

                var encounter = await sessionA.ReadCurrentEncounterAsync();
                if (encounter.Outcome == EncounterReadOutcome.NotFound)
                    Console.WriteLine("UNVERIFIED encounter HTTP: route absent/alpha OFF (404 " + encounter.ErrorCode + ")");
                else if (encounter.Success)
                    Check(true, "encounter current typed read");
                else
                    throw new Exception("encounter read failed: " + encounter.Outcome + " " + encounter.ErrorCode);

                // ---------- B: isolation + cross-session replay ----------
                Check((await sessionB.ConnectAsync()).Success, "B connect");
                Check(sessionB.Client.World.self.characterId == CharacterB, "B identity");
                Check(sessionB.Client.World.self.characterId != sessionA.Client.World.self.characterId, "A/B different characters");
                Check((await sessionB.Client.ReadQuestsAsync(CancellationToken.None)).Success, "B read quests");
                Check(sessionB.Client.Quests.All(q => q == null || q.questId != "P00-01" || q.state != "COMPLETED"), "B quest not completed by A");
                Check((await sessionB.Client.ReadInventoryAsync(CancellationToken.None)).Success, "B inv pre");
                Check(sessionB.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 0, "B pre coin 0");

                var replay = await RawPost(baseUrl, "/p1/quests/turnin", httpA.LastTurnInBody, sessionB.Client.SessionId);
                Check((int)replay.StatusCode >= 400, "cross-session replay rejected");
                var replayBody = await replay.Content.ReadAsStringAsync();
                Check(replayBody.Contains("characterId", StringComparison.Ordinal) || replayBody.Contains("invalid_payload", StringComparison.Ordinal),
                    "cross-session replay error is structured");
                Check((await sessionB.Client.ReadInventoryAsync(CancellationToken.None)).Success, "B inv after cross-session replay");
                Check(sessionB.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 0, "B no coin from A replay");
                Check(sessionB.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 0, "B no chest from A replay");

                // ---------- B: expiry while mutation pending, relogin, retry same key ----------
                var dialogueB = new NpcDialoguePresenter(sessionB.Adapter);
                await PrepareP00_01(sessionB.Client, dialogueB, "B");
                expB.ExpireTurnInOnce = true;
                var expired = await dialogueB.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(expired.IsError && (expired.ErrorCode == "mutation_outcome_unknown" || expired.ErrorCode == "session_not_found"),
                    "B expiry on mutation rejected");
                Check(sessionB.Adapter.HasPendingMutation, "B pending survives expiry");
                var oldGeneration = sessionB.SessionGeneration;
                var reloginB = await sessionB.ReloginAsync();
                Check(reloginB.Success && sessionB.SessionGeneration > oldGeneration, "B relogin monotonic epoch");
                Check(sessionB.Client.HasPendingMutation, "B pending carried across relogin");
                // A fresh session respawns at the default point; walk back into turn-in range
                // without discarding or re-keying the pending mutation.
                await WalkTo(sessionB.Client, 64);
                var retryB = await sessionB.Adapter.RetryPendingAsync(CancellationToken.None);
                if (!retryB.Success)
                    Console.WriteLine("B retry diagnostic: code=" + (retryB.Code ?? "<null>") +
                                      " state=" + sessionB.Client.State + " last=" + (sessionB.Client.LastError ?? "<null>") +
                                      " pending=" + sessionB.Client.HasPendingMutation);
                Check(retryB.Success && !sessionB.Adapter.HasPendingMutation, "B retry same key after relogin");
                Check((await sessionB.Client.ReadInventoryAsync(CancellationToken.None)).Success, "B inv post");
                Check(sessionB.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "B 20 coin once");
                Check(sessionB.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "B 1 chest once");

                // ---------- B: read expiry then relogin recovers ----------
                expB.ExpireWorldOnce = true;
                var expiredRead = await sessionB.Client.ReadWorldAsync(CancellationToken.None);
                if (expiredRead.Success || sessionB.Client.State != P1ConnectionState.Expired)
                    Console.WriteLine("B read expiry diagnostic: success=" + expiredRead.Success +
                                      " code=" + (expiredRead.Code ?? "<null>") + " state=" + sessionB.Client.State);
                Check(!expiredRead.Success && sessionB.Client.State == P1ConnectionState.Expired, "B read expiry observed");
                var oldReadGeneration = sessionB.SessionGeneration;
                var reloginRead = await sessionB.ReloginAsync();
                Check(reloginRead.Success && sessionB.SessionGeneration > oldReadGeneration, "B read relogin");
                Check((await sessionB.Client.ReadWorldAsync(CancellationToken.None)).Success, "B world after relogin");

                // ---------- A: repeat replay after successful receipt is still no-op ----------
                var replayA = await RawPost(baseUrl, "/p1/quests/turnin", httpA.LastTurnInBody, sessionA.Client.SessionId);
                Check((int)replayA.StatusCode >= 400, "replay after commit rejected");
                Check((await sessionA.Client.ReadInventoryAsync(CancellationToken.None)).Success, "A inv after replay");
                Check(sessionA.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "A replay no double grant");
                Check(sessionA.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "A replay no double chest");

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
            try
            {
                using (var c = new HttpClient { Timeout = TimeSpan.FromSeconds(10) })
                {
                    var r = c.GetAsync(baseUrl.TrimEnd('/') + "/health").GetAwaiter().GetResult();
                    if (!r.IsSuccessStatusCode) throw new Exception();
                    var body = r.Content.ReadAsStringAsync().GetAwaiter().GetResult();
                    if (!body.Contains("ngu-mach-huyen-an-server", StringComparison.Ordinal))
                        throw new Exception("unexpected health identity");
                }
            }
            catch (Exception e)
            {
                Console.Error.WriteLine("UNVERIFIED - server unreachable/wrong identity: " + e.Message);
                return 2;
            }
            try { MainAsync(baseUrl).GetAwaiter().GetResult(); }
            catch (Exception e) { Console.Error.WriteLine("FAIL: " + e.Message); return 1; }
            if (checks < 25) { Console.Error.WriteLine("FAIL - only " + checks + " assertions"); return 1; }
            return 0;
        }
    }
}
