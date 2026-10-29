using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using Newtonsoft.Json.Linq;

internal static class Program
{
    private const string Session = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
    private static readonly CancellationToken None = CancellationToken.None;
    private static int assertions;
    private static void Check(bool ok, string message)
    { assertions++; if (!ok) throw new Exception(message); }
    private static P1World World(long revision = 1, double x = 18, int mp = 50)
    {
        return new P1World { mapId = "MAP_BEN_MUA", revision = revision, serverTick = revision * 2,
            serverTimeUtc = "2026-10-29T00:00:00Z", entities = new P1Entity[0], self = new P1Self {
                characterId = "CHR_CLIENT_CHECK", classId = "CLASS_MINH_KIEM", x = x, y = 0,
                hp = 100, maxHp = 100, mp = mp, maxMp = 50, swordIntent = 0 } };
    }
    private static P1Quest Quest(long rev = 1, string state = "AVAILABLE")
    { return new P1Quest { questId = "P00-01", state = state, stepId = "STEP_P00_01_PACKAGES", revision = rev,
        objectiveCounters = new Dictionary<string, int> { { "OBJ_P00_01_PACKAGES", 0 } } }; }
    private static P1HttpReply Reply<T>(T result, int status = 200, string error = null, string session = Session)
    { return new P1HttpReply { StatusCode = status, CorrelationId = "trace-test", Body = P1Wire.Encode(new P1Response<T> {
        schemaVersion = 1, requestId = Session, sessionId = session, serverTimeUtc = "2026-10-29T00:00:00Z", result = result,
        error = error == null ? null : new P1Error { code = error, fieldErrors = new string[0], correlationId = "trace-test" } }) }; }
    private static P1HttpReply CastReply()
    { return Reply(new P1CombatEvent { schemaVersion = 1, eventId = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", eventType = "combat.effect",
        aggregateId = "CHR_CLIENT_CHECK", aggregateRevision = 2, payload = new P1CombatPayload { sourceId = "CHR_CLIENT_CHECK",
            targetId = "CHR_CLIENT_CHECK", skillId = "SK-MK-01", cooldownEndsAtUtc = "2026-10-29T00:00:10Z" } }); }
    private sealed class Script : IP1Transport
    {
        public readonly List<P1Request> Requests = new List<P1Request>();
        public readonly Queue<Func<P1Request, CancellationToken, Task<P1HttpReply>>> Steps =
            new Queue<Func<P1Request, CancellationToken, Task<P1HttpReply>>>();
        public void Add(P1HttpReply reply) { Steps.Enqueue((r, c) => Task.FromResult(reply)); }
        public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
        { Requests.Add(request); if (Steps.Count == 0) throw new Exception("Unexpected request " + request.Path); return Steps.Dequeue()(request, ct); }
    }
    private static async Task<P1Client> Connected(Script t)
    { t.Add(Reply(World(), 201)); var c = new P1Client(t); Check((await c.ConnectAsync(None)).Success, "create session"); return c; }

    private static async Task RunCases()
    {
        {
            var previous = System.Globalization.CultureInfo.CurrentCulture;
            try
            {
                System.Globalization.CultureInfo.CurrentCulture = System.Globalization.CultureInfo.GetCultureInfo("th-TH");
                var t = new Script(); t.Add(Reply(World(), 201));
                var c = new P1Client(t, () => new DateTimeOffset(2026, 10, 29, 0, 0, 0, TimeSpan.Zero));
                await c.ConnectAsync(None);
                t.Steps.Enqueue((r, ct) => {
                    Check(P1Wire.Decode<P1Envelope<P1Move>>(r.Body).sentAtUtc == "2026-10-29T00:00:00Z", "wire UTC must not use the device's Thai calendar");
                    return Task.FromResult(Reply(World(2, 19)));
                });
                Check((await c.MoveAsync(1, 0, None)).Success, "non-Gregorian device locale supported");
            }
            finally { System.Globalization.CultureInfo.CurrentCulture = previous; }
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Steps.Enqueue((r, ct) => {
                var env = P1Wire.Decode<P1Envelope<P1Move>>(r.Body);
                Check(env.payload.inputSequence == 1 && Math.Abs(env.payload.moveX - 1 / Math.Sqrt(2)) < 1e-9, "normalize diagonal");
                Check(P1Wire.Hex32(env.requestId) && P1Wire.Hex32(env.idempotencyKey) && r.SessionId == Session, "envelope and session");
                return Task.FromResult(Reply(World(2, 19)));
            });
            Check((await c.MoveAsync(1, 1, None)).Success && c.World.self.x == 19, "only authoritative position");
            var count = t.Requests.Count;
            Check(!(await c.MoveAsync(double.NaN, 0, None)).Success && t.Requests.Count == count, "NaN never sent");
            Check(!(await c.MoveAsync(2, 0, None)).Success, "axis out of range");
            t.Add(Reply<P1World>(null, 422, "movement_too_far"));
            Check(!(await c.MoveAsync(1, 0, None)).Success && c.World.self.x == 19 && c.State == P1ConnectionState.Ready, "reject doesn't change pose");
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Add(new P1HttpReply { StatusCode = 0 });
            await c.MoveAsync(1, 0, None);
            Check(c.State == P1ConnectionState.NeedsResync, "lost move needs readback");
            int n = t.Requests.Count;
            Check(!(await c.MoveAsync(1, 0, None)).Success && t.Requests.Count == n, "no move queue after timeout");
            t.Add(Reply(World(2, 19))); await c.ReadWorldAsync(None);
            t.Add(Reply(World(3, 20))); await c.MoveAsync(1, 0, None);
            Check(P1Wire.Decode<P1Envelope<P1Move>>(t.Requests.Last().Body).payload.inputSequence == 2, "lost move not replayed");
            t.Add(Reply(World(1, 18))); await c.ReadWorldAsync(None);
            Check(c.World.revision == 3 && c.World.self.x == 20, "stale snapshot ignored");
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Add(new P1HttpReply { StatusCode = 0 }); await c.CastAsync("SK-MK-01", null, 1, 0, None);
            Check(c.HasPendingMutation && c.State == P1ConnectionState.UncertainMutation && c.World.self.mp == 50, "cast loss: no fake MP commit");
            var sent = t.Requests.Last(); int n = t.Requests.Count;
            Check(!(await c.CastAsync("SK-MK-01", null, 1, 0, None)).Success && t.Requests.Count == n, "ambiguous cast blocks new cast");
            t.Add(Reply(World(2, 18, 38))); await c.ReadWorldAsync(None);
            Check(c.HasPendingMutation && c.State == P1ConnectionState.UncertainMutation, "readback alone doesn't discard pending");
            t.Add(CastReply()); t.Add(Reply(World(2, 18, 38)));
            Check((await c.RetryPendingAsync(None)).Success && !c.HasPendingMutation, "same cast retry resolves");
            var retries = t.Requests.Where(r => r.Path == "/p1/combat").ToArray();
            Check(retries.Length == 2 && retries[1].Body == sent.Body && retries[1].CorrelationId == sent.CorrelationId, "exact immutable retry");
            Check(c.World.self.mp == 38 && c.LastCombatEvent.payload.damage == null, "MP from snapshot, no invented damage");
            Check(!(await c.CastAsync("SK-MK-06", null, 1, 0, None)).Success, "unsupported skill doesn't submit");
            Check(!(await c.CastAsync("SK-MK-02", null, 1, 0, None)).Success, "target required");
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Add(new P1HttpReply { StatusCode = 404, Body = "" });
            Check((await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None)).Code == "feature_unavailable" && c.Quests.Length == 0 && !c.HasPendingMutation, "flag off not accepted");
            t.Add(new P1HttpReply { StatusCode = 405, Body = "" });
            Check((await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None)).Code == "feature_unavailable" && !c.HasPendingMutation && c.State == P1ConnectionState.Ready, "GET route overlap405 is definite rejection");
            t.Add(Reply(Quest(2, "ACTIVE"), 409, "invalid_transition"));
            Check(!(await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None)).Success && c.Quests[0].state == "ACTIVE", "error binds authoritative quest state");
            t.Add(Reply(new[] { Quest(1) })); await c.ReadQuestsAsync(None);
            Check(c.Quests[0].revision == 2 && c.Quests[0].objectiveCounters["OBJ_P00_01_PACKAGES"] == 0, "quest revision/dictionary preserved");
            t.Add(new P1HttpReply { StatusCode = 503, Body = "upstream unavailable" });
            await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None);
            var original = t.Requests.Last();
            t.Add(Reply(Quest(3, "ACTIVE"))); await c.RetryPendingAsync(None);
            Check(t.Requests.Last().Body == original.Body && c.Quests[0].revision == 3, "quest retry uses original key/body");
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Add(Reply(new P1Inventory { inventoryRevision = 5, items = new P1Item[0], currencies = new[] { new P1Currency { currencyId = "COIN", amount = 20 } } }));
            await c.ReadInventoryAsync(None);
            t.Add(Reply(new P1Inventory { inventoryRevision = 1, items = new P1Item[0], currencies = new P1Currency[0] }));
            await c.ReadInventoryAsync(None);
            Check(c.Inventory.inventoryRevision == 5 && c.Inventory.currencies[0].amount == 20, "stale inventory cannot remove money");
            t.Add(Reply(new P1Inventory { inventoryRevision = 6, items = new P1Item[0], currencies = new[] { new P1Currency { amount = -1 } } }));
            Check(!(await c.ReadInventoryAsync(None)).Success && c.Inventory.inventoryRevision == 5, "invalid inventory rejected");
            t.Add(Reply<P1World>(null, 404, "session_not_found", null));
            await c.ReadWorldAsync(None);
            Check(c.State == P1ConnectionState.Expired && c.SessionId == null && c.World == null && c.Inventory == null, "expiry clears all snapshots");
        }
        {
            var t = new Script(); var c = await Connected(t);
            t.Add(new P1HttpReply { StatusCode = 200, Body = "{}" });
            Check(!(await c.ReadWorldAsync(None)).Success && c.World.self.x == 18 && c.State == P1ConnectionState.NeedsResync, "malformed success cannot zero state");
            var obj = JObject.Parse(Reply(World()).Body); ((JObject)obj["result"]["self"]).Remove("hp");
            t.Add(new P1HttpReply { StatusCode = 200, Body = obj.ToString() });
            Check(!(await c.ReadWorldAsync(None)).Success, "required HP not silently defaulted");
            t.Add(Reply(World())); await c.ReadWorldAsync(None);
            t.Add(Reply(World(2), session: "cccccccccccccccccccccccccccccccc"));
            Check(!(await c.ReadWorldAsync(None)).Success && c.World.revision == 1, "other session snapshot rejected");
        }
        {
            var t = new Script(); var c = await Connected(t);
            var cancel = new CancellationTokenSource();
            t.Steps.Enqueue((r, ct) => { cancel.Cancel(); return Task.FromCanceled<P1HttpReply>(ct); });
            try { await c.CastAsync("SK-MK-01", null, 1, 0, cancel.Token); throw new Exception("Expected cancellation"); }
            catch (OperationCanceledException) { }
            Check(c.HasPendingMutation && c.State == P1ConnectionState.UncertainMutation, "cancel after send keeps outcome uncertain");
            t.Add(CastReply()); t.Add(Reply(World(2, 18, 38)));
            Check((await c.RetryPendingAsync(None)).Success, "new token can retry retained request");
        }
        {
            var t = new Script(); var c = await Connected(t);
            var waiting = new TaskCompletionSource<P1HttpReply>();
            t.Steps.Enqueue((r, ct) => waiting.Task);
            t.Add(Reply(World(3, 20)));
            var first = c.MoveAsync(1, 0, None); var second = c.MoveAsync(1, 0, None);
            Check(t.Requests.Count == 2, "single request in flight");
            waiting.SetResult(Reply(World(2, 19))); await first; await second;
            Check(c.World.revision == 3 && P1Wire.Decode<P1Envelope<P1Move>>(t.Requests.Last().Body).payload.inputSequence == 2, "serialized shared sequence");
        }
        Console.WriteLine("PASS P1 core assertions: " + assertions);
    }

    private sealed class HttpTransport : IP1Transport, IDisposable
    {
        private readonly HttpClient http;
        public HttpTransport(string url)
        { http = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false }) { BaseAddress = new Uri(url), Timeout = TimeSpan.FromSeconds(5) }; }
        public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
        {
            using (var msg = new HttpRequestMessage(new HttpMethod(request.Method), request.Path))
            {
                msg.Headers.Add("X-Correlation-ID", request.CorrelationId);
                if (request.SessionId != null) msg.Headers.Add("X-Session-ID", request.SessionId);
                if (request.Body != null) msg.Content = new StringContent(request.Body, Encoding.UTF8, "application/json");
                using (var r = await http.SendAsync(msg, ct))
                    return new P1HttpReply { StatusCode = (int)r.StatusCode, Body = await r.Content.ReadAsStringAsync(ct),
                        CorrelationId = r.Headers.TryGetValues("X-Correlation-ID", out var ids) ? ids.First() : null };
            }
        }
        public void Dispose() { http.Dispose(); }
    }
    private static async Task HttpChecks(string url)
    {
        using (var http = new HttpTransport(url))
        {
            var c = new P1Client(http);
            Check((await c.ConnectAsync(None)).Success && c.World.mapId == "MAP_BEN_MUA", "HTTP create session");
            double before = c.World.self.x;
            await Task.Delay(180);
            Check((await c.MoveAsync(1, 0, None)).Success && c.World.self.x > before, "HTTP authoritative move");
            Check((await c.ReadQuestsAsync(None)).Success && c.Quests.Any(q => q.questId == "P00-01"), "HTTP quest read");
            Check((await c.ReadInventoryAsync(None)).Success && c.Inventory.items.Length == 0, "HTTP inventory read");
            var result = await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None);
            Check(!result.Success && result.Code == "feature_unavailable", "HTTP default quest feature off: " + result.Code);
            int mp = c.World.self.mp;
            Check((await c.CastAsync("SK-MK-01", null, 1, 0, None)).Success && c.World.self.mp == mp - 12, "HTTP cast then authoritative MP readback");
            Check(c.LastCombatEvent.eventType == "combat.effect" && c.LastCombatEvent.payload.damage == null, "HTTP no fabricated damage");
        }
        Console.WriteLine("PASS P1 client HTTP assertions: " + assertions);
    }
    public static async Task<int> Main(string[] args)
    {
        try { if (args.Length == 2 && args[0] == "--http") await HttpChecks(args[1]); else await RunCases(); return 0; }
        catch (Exception e) { Console.Error.WriteLine(e); return 1; }
    }
}
