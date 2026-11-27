using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

internal static class V2HttpChecks
{
    private static int assertions;
    private static readonly CancellationToken None = CancellationToken.None;
    private static void Check(bool value, string why) { assertions++; if (!value) throw new Exception(why); }
    private sealed class Transport : IP1Transport, IDisposable
    {
        private readonly HttpClient http;
        public readonly List<P1Request> Requests = new List<P1Request>();
        public string LoseResponseOnce;
        public Transport(string origin)
        { http = new HttpClient(new HttpClientHandler { AllowAutoRedirect = false }) { BaseAddress = new Uri(origin), Timeout = TimeSpan.FromSeconds(10) }; }
        public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
        {
            Requests.Add(req);
            using (var message = new HttpRequestMessage(new HttpMethod(req.Method), req.Path))
            {
                if (req.SessionId != null) message.Headers.Add("X-Session-ID", req.SessionId);
                if (req.Body != null) message.Content = new StringContent(req.Body, Encoding.UTF8, "application/json");
                using (var reply = await http.SendAsync(message, ct))
                {
                    string body = await reply.Content.ReadAsStringAsync(ct);
                    if (LoseResponseOnce == req.Path) { LoseResponseOnce = null; return new P1HttpReply { StatusCode = 0 }; }
                    return new P1HttpReply { StatusCode = (int)reply.StatusCode, Body = body };
                }
            }
        }
        public void Dispose() { http.Dispose(); }
    }
    private static async Task Walk(P1Client c, double x)
    {
        // Normal authoritative movement commands, no teleport/position mutation or server test hook.
        for (int i = 0; i < 800 && Math.Abs(c.World.self.x - x) > 0.7; i++)
        {
            await Task.Delay(60);
            var r = await c.MoveAsync(Math.Sign(x - c.World.self.x), 0, None);
            if (!r.Success) throw new Exception("Walk failed: " + r.Code);
        }
        Check(Math.Abs(c.World.self.x - x) <= 0.7, "walk reached interaction point " + x);
    }
    public static async Task Default(string origin)
    {
        using (var t = new Transport(origin))
        {
            var c = new P1Client(t, useWorldV2: true);
            Check(!(await c.ConnectAsync(None)).Success && c.LastError == "feature_unavailable" && c.WorldV2 == null, "default server leaves explicit v2 unavailable");
            var legacy = new P1Client(t); Check((await legacy.ConnectAsync(None)).Success, "v1 still connects on default server");
            Check((await legacy.InteractAsync("ENT_MAN_BM_OBJ_BM_PACKAGE_01", None)).Code == "feature_unavailable" && !legacy.HasPendingMutation, "interact flag OFF is a definite rejection");
            Check((await legacy.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Code == "feature_unavailable" && !legacy.HasPendingMutation, "turn-in flag OFF grants nothing");
        }
        Console.WriteLine("PASS default v2 HTTP assertions: " + assertions);
    }
    public static async Task Dev(string origin, bool tickCombat = false)
    {
        using (var ta = new Transport(origin))
        using (var tb = new Transport(origin))
        {
            var a = new P1Client(ta, useWorldV2: true); var b = new P1Client(tb, useWorldV2: true);
            foreach (var c in new[] { a, b })
            {
                Check((await c.ConnectAsync(None)).Success && c.WorldV2 != null, "DEV connects through v2 snapshot");
                Check(c.WorldV2.audience.aoiEnterWu == 40 && c.WorldV2.audience.aoiLeaveWu == 48, "wire AOI policy is 40/48");
                Check(c.World.entities.Any(e => e.kind == "NPC") && c.World.entities.Where(e => e.kind == "NPC").All(e => e.targetable == false && e.healthState == "INVULNERABLE"), "NPC never a damage target");
                Check((await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None)).Code == "out_of_range", "far accept rejected by real server");
                await Walk(c, 42);
                Check((await c.AcceptQuestAsync("P00-01", "NPC_LYAN", None)).Success, "accept near Ly An");
            }
            Check(a.SessionId != b.SessionId && a.World.self.characterId != b.World.self.characterId, "two clients own separate actors");
            int[] packageX = { 36, 44, 52 };
            for (int i = 0; i < packageX.Length; i++)
            {
                string target = "ENT_MAN_BM_OBJ_BM_PACKAGE_0" + (i + 1);
                foreach (var c in new[] { a, b })
                {
                    await Walk(c, packageX[i]);
                    Check((await c.InteractAsync(target, None)).Success, "each character collects same package independently");
                }
            }
            foreach (var c in new[] { a, b })
            {
                Check((await c.ReadQuestsAsync(None)).Success && c.Quests.Single(q => q.questId == "P00-01").state == "READY_TO_TURN_IN", "three packages reach READY");
                Check(c.Quests.Single(q => q.questId == "P00-01").objectiveCounters.Values.Single() == 3, "three unique objective counts");
                Check((await c.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Code == "out_of_range", "far turn-in cannot grant");
                await Walk(c, 64);
            }
            ta.LoseResponseOnce = "/p1/quests/turnin";
            Check(!(await a.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Success && a.HasPendingMutation, "lose response after actual server commit");
            var request = ta.Requests.Last(r => r.Path == "/p1/quests/turnin");
            Check((await a.RetryPendingAsync(None)).Success && !a.HasPendingMutation, "exact retry recovers committed reward");
            Check(ta.Requests.Where(r => r.Path == request.Path).Last().Body == request.Body, "HTTP retry body and idempotency unchanged");
            Check((await b.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Success, "second actor turns in own quest");
            for (int i = 0; i < 3; i++) Check((await ta.SendAsync(request, None)).StatusCode == 200, "server replay returns original receipt");
            foreach (var c in new[] { a, b })
            {
                Check((await c.ReadInventoryAsync(None)).Success && c.Inventory.currencies.Single(x => x.currencyId == "COIN").amount == 20, "one grant of 20 coins after retries");
                Check(c.Inventory.items.Count(x => x.templateId == "EQ-MK-CHEST-T1-R-COMMON") == 1, "one chest instance per actor");
                Check(c.Quests.Single(q => q.questId == "P00-01").state == "COMPLETED", "quest stays completed");
                Check(c.LastTurnIn != null && !c.LastTurnIn.rewards.xp.applied, "unsupported XP is explicitly unapplied");
            }
            await Walk(a, 82); await a.ReadWorldAsync(None);
            var mob = a.World.entities.FirstOrDefault(e => e.targetable == true && e.kind == "MOB" && Math.Abs(e.x - a.World.self.x) <= 4);
            Check(mob != null, "authoritative hostile visible near first mob group");
            Check((await a.BasicAttackAsync(mob.entityId, 1, 0, None)).Success, "real v2 basic command accepted");
            var command = ta.Requests.Last(r => r.Path == "/p1/v2/combat");
            var acceptedEvents = a.DrainPresentationEvents();
            Check(acceptedEvents.Any(e => e.type == "CAST_START") && acceptedEvents.All(e => e.type == "CAST_START"), "accept-only dependency produces no fabricated impacts");
            Check((await a.ReadEventsAsync(None)).Success && a.EventCursor > 0, "real reliable event cursor read");
            var polled = a.DrainPresentationEvents();
            Check(polled.All(e => e.type != "CAST_START"), "event poll does not duplicate command CAST_START");
            Check((await ta.SendAsync(command, None)).StatusCode == 200, "real combat replay accepted once");
            Check((await a.ReadEventsAsync(None)).Success, "read after combat replay");
            var replayed = a.DrainPresentationEvents();
            Check(replayed.All(e => e.type != "CAST_START"), "combat replay appends no duplicate CAST_START");
            if (tickCombat)
            {
                // A cached POST is still a replay after the original cast left the active scheduler.
                await Task.Delay(600);
                Check((await a.ReadEventsAsync(None)).Success && (await a.ReadWorldAsync(None)).Success, "wait for original END before replay probe");
                var finished = a.DrainPresentationEvents();
                string originalCast = acceptedEvents.First(e => e.type == "CAST_START").castId;
                int hpBeforeReplay = a.World.entities.First(e => e.entityId == mob.entityId).hp;
                Check((await ta.SendAsync(command, None)).StatusCode == 200, "finished cast replay returns cached receipt");
                await Task.Delay(400);
                Check((await a.ReadEventsAsync(None)).Success && (await a.ReadWorldAsync(None)).Success, "read after finished cast replay");
                var lateReplay = a.DrainPresentationEvents();
                Check(!lateReplay.Any(e => e.castId == originalCast) && a.World.entities.First(e => e.entityId == mob.entityId).hp == hpBeforeReplay,
                    "replay after END must not schedule a second effect or damage");
                int mpBeforeMk03 = a.World.self.mp;
                Check((await a.CastAsync("SK-MK-03", mob.entityId, 1, 0, None)).Success, "real MK03 accepted");
                string mk03Cast = a.DrainPresentationEvents().Single(e => e.type == "CAST_START").castId;
                await Task.Delay(550);
                Check((await a.ReadEventsAsync(None)).Success && (await a.ReadWorldAsync(None)).Success, "read actual MK03 tick results");
                var mk03Events = a.DrainPresentationEvents();
                Check(mk03Events.Where(e => e.castId == mk03Cast && (e.type == "IMPACT" || e.type == "MISS"))
                    .Select(e => e.hitIndex).OrderBy(i => i).SequenceEqual(new int?[] { 0, 1, 2 }), "MK03 three distinct hit indices arrive from server ticks");
                Check(a.World.self.mp < mpBeforeMk03, "MK03 resource consumption comes from server snapshot");
                int originalHp = mob.hp; int impacts = polled.Count(e => e.type == "IMPACT") + replayed.Count(e => e.type == "IMPACT");
                impacts += finished.Count(e => e.type == "IMPACT") + mk03Events.Count(e => e.type == "IMPACT");
                int deaths = polled.Count(e => e.type == "DEATH") + replayed.Count(e => e.type == "DEATH") + finished.Count(e => e.type == "DEATH");
                bool dead = false;
                for (int i = 0; i < 30 && !dead; i++)
                {
                    await Task.Delay(350);
                    Check((await a.ReadEventsAsync(None)).Success && (await a.ReadWorldAsync(None)).Success, "tick event and HP readback");
                    var events = a.DrainPresentationEvents(); impacts += events.Count(e => e.type == "IMPACT"); deaths += events.Count(e => e.type == "DEATH");
                    var current = a.World.entities.FirstOrDefault(e => e.entityId == mob.entityId);
                    dead = current == null || current.targetable == false && current.hp == 0;
                    if (dead) break;
                    Check(current.hp <= originalHp, "server target HP never increases during this attempt");
                    var next = await a.BasicAttackAsync(current.entityId, 1, 0, None);
                    Check(next.Success, "repeat basic at authoritative cooldown: " + next.Code);
                    var start = a.DrainPresentationEvents();
                    Check(start.All(e => e.type == "CAST_START"), "each command only presents its accepted start");
                }
                Check(impacts > 0 && deaths == 1 && dead, "real 20Hz impacts and one death reduce a server mob to zero");
                Check(!a.World.entities.Any(e => e.entityId == mob.entityId && e.targetable == true), "dead mob cannot remain targetable");
            }
        }
        Console.WriteLine("PASS DEV v2 two-client HTTP assertions: " + assertions +
            (tickCombat ? " (tick damage/death verified; synthetic nav/in-memory; boss/save not accepted)" : " (accept-only dependency; synthetic nav/in-memory; boss/save not accepted)"));
    }
}
