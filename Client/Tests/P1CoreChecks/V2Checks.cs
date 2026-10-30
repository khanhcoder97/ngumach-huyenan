using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using NguMach.Client.P1;

internal static class V2Checks
{
    private const string Session = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", EventId = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", CastId = "cccccccccccccccccccccccccccccccc";
    private const string Now = "2026-10-30T00:00:00Z", Char = "CHR_CLIENT_V2", Mob = "ENT_MOB_1", Node = "ENT_PACKAGE_1";
    private static int assertions;
    private static readonly CancellationToken None = CancellationToken.None;
    private static void Check(bool value, string why) { assertions++; if (!value) throw new Exception(why); }
    private sealed class Script : IP1Transport
    {
        public readonly List<P1Request> Requests = new List<P1Request>();
        public readonly Queue<P1HttpReply> Replies = new Queue<P1HttpReply>();
        public bool KeepReplyRequestIdOnce;
        public Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
        {
            Requests.Add(req); if (Replies.Count == 0) throw new Exception("Unexpected " + req.Path);
            var reply = Replies.Dequeue();
            if (!KeepReplyRequestIdOnce && req.Method == "POST" && req.Path != "/p1/sessions" && !string.IsNullOrWhiteSpace(reply.Body))
            {
                var obj = JObject.Parse(reply.Body); obj["requestId"] = req.CorrelationId; reply.Body = obj.ToString();
            }
            KeepReplyRequestIdOnce = false;
            return Task.FromResult(reply);
        }
    }
    private static P1HttpReply Reply(object result, int version = 2, int status = 200, string error = null)
    { return new P1HttpReply { StatusCode = status, Body = P1Wire.Encode(new P1Response<object> { schemaVersion = version,
        requestId = Session, sessionId = Session, serverTimeUtc = Now, result = result, error = error == null ? null : new P1Error { code = error } }) }; }
    private static P1Self Self(int mp = 50)
    { return new P1Self { characterId = Char, classId = "CLASS_MINH_KIEM", hp = 100, maxHp = 100, mp = mp, maxMp = 50, x = 18, y = 0 }; }
    private static P1World Legacy(int mp = 50)
    { return new P1World { mapId = "MAP_BEN_MUA", revision = 1, serverTick = 1, serverTimeUtc = Now, self = Self(mp), entities = new P1Entity[0] }; }
    private static P1EntityV2 Entity(string id, string kind, bool targetable, int hp)
    { return new P1EntityV2 { entityId = id, kind = kind, targetable = targetable, hp = hp, maxHp = hp, x = 19, y = 0,
        healthState = targetable ? "ALIVE" : "INVULNERABLE", state = "IDLE", mapInstanceId = "MAP_BEN_MUA#1", floorId = "OVERWORLD", phase = "OPEN_WORLD", lifeId = 1, revision = 1 }; }
    private static P1WorldV2 World(long revision = 1, int hp = 192, int mp = 50)
    { return new P1WorldV2 { schemaVersion = 2, mapId = "MAP_BEN_MUA", mapInstanceId = "MAP_BEN_MUA#1", floorId = "OVERWORLD", phase = "OPEN_WORLD",
        serverTimeUtc = Now, serverTick = revision, revision = revision, self = Self(mp), audience = new P1Audience { aoiEnterWu = 40, aoiLeaveWu = 48 },
        entities = new[] { Entity(Mob, "MOB", true, hp), Entity("ENT_NPC_1", "NPC", false, 0), Entity(Node, "INTERACTABLE", false, 0) } }; }
    private static async Task<P1Client> Connect(Script t)
    { t.Replies.Enqueue(Reply(Legacy(), 1, 201)); t.Replies.Enqueue(Reply(World())); var c = new P1Client(t, useWorldV2: true);
        Check((await c.ConnectAsync(None)).Success, "v2 connects via v1 session then v2 snapshot"); return c; }
    private static P1EventV2 Event(long cursor = 1, string type = "CAST_START")
    { return new P1EventV2 { eventId = cursor == 1 ? EventId : cursor.ToString("x32"), castId = CastId, actorId = Char, cursor = cursor,
        type = type, sourceRevision = 2, serverTick = 2, emittedAtUtc = Now, mapInstanceId = "MAP_BEN_MUA#1", floorId = "OVERWORLD" }; }
    private static P1CastResultV2 Cast(string kind = "BASIC_ATTACK", int next = 1)
    { return new P1CastResultV2 { castId = CastId, actionKind = kind, skillId = kind == "SKILL" ? "SK-MK-01" : null,
        mp = 50, mpCost = 0, cooldownEndUtc = Now, acceptedInputSequence = next, events = new[] { Event() } }; }
    private static P1EventPageV2 Page(params P1EventV2[] events)
    { return new P1EventPageV2 { schemaVersion = 2, sessionId = Session, nextCursor = events.Length == 0 ? 0 : events.Last().cursor, events = events }; }
    private static P1Quest Quest(string state = "READY_TO_TURN_IN", long revision = 3)
    { return new P1Quest { questId = "P00-01", state = state, stepId = "STEP_P00_01_PACKAGES", revision = revision,
        objectiveCounters = new Dictionary<string, int> { { "OBJ_P00_01_PACKAGES", 3 } } }; }
    private static P1Inventory Inventory(int coins = 20)
    { return new P1Inventory { inventoryRevision = 2, items = new P1Item[0], currencies = new[] { new P1Currency { currencyId = "COIN", amount = coins } } }; }
    private static P1TurnInResult Receipt()
    { return new P1TurnInResult { questState = Quest("COMPLETED", 4), unlocks = new[] { "P00-02" }, rewards = new P1RewardReceipt {
        currency = new[] { new P1Currency { currencyId = "COIN", amount = 20 } }, items = new P1RewardItem[0], xp = new P1RewardXp { xpRule = "LEVEL_BAND_BASE", applied = false } } }; }

    public static async Task Run()
    {
        {
            var t = new Script(); var c = await Connect(t);
            Check(c.World.entities.Length == 3 && c.World.entities[1].hp == 0 && c.World.entities[1].healthState == "INVULNERABLE", "NPC hp0 is invulnerable, not dead");
            int n = t.Requests.Count;
            Check(!(await c.BasicAttackAsync("ENT_NPC_1", 1, 0, None)).Success && t.Requests.Count == n, "NPC never sent as attack target");
            Check(!(await c.BasicAttackAsync(Node, 1, 0, None)).Success && t.Requests.Count == n, "package never sent as attack target");
            Check(!(await c.BasicAttackAsync(Mob, double.NaN, 0, None)).Success && t.Requests.Count == n, "v2 NaN rejected before send");
            var broken = JObject.Parse(Reply(World(2)).Body); ((JObject)broken["result"]["entities"][0]).Remove("targetable");
            t.Replies.Enqueue(new P1HttpReply { StatusCode = 200, Body = broken.ToString() });
            Check(!(await c.ReadWorldAsync(None)).Success && c.World.revision == 1, "missing required v2 fields never default silently");
            var wrongFloor = World(2); wrongFloor.entities[0].floorId = "OTHER"; t.Replies.Enqueue(Reply(wrongFloor));
            Check(!(await c.ReadWorldAsync(None)).Success && c.WorldV2.floorId == "OVERWORLD", "cross-floor data rejected atomically");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(Reply(Legacy(), 1)); t.Replies.Enqueue(Reply(World(2)));
            Check((await c.MoveAsync(1, 0, None)).Success, "v1 move followed by v2 authoritative refresh");
            t.Replies.Enqueue(Reply(Cast(next: 2))); t.Replies.Enqueue(Reply(World(3)));
            Check((await c.BasicAttackAsync(Mob, 1, 0, None)).Success, "basic accepted through explicit v2 route");
            var req = t.Requests.First(r => r.Path == "/p1/v2/combat"); var env = P1Wire.Decode<P1Envelope<P1CastV2>>(req.Body);
            Check(env.schemaVersion == 2 && env.payload.inputSequence == 2 && env.payload.actionKind == "BASIC_ATTACK" && env.payload.skillId == null, "move/basic share one sequence and correct wire");
            var shown = c.DrainPresentationEvents(); Check(shown.Length == 1 && shown[0].type == "CAST_START", "accept renders start only, not a fabricated hit");
            var impact = Event(2, "IMPACT"); impact.targetId = Mob; impact.targetLifeId = 1; impact.targetRevision = 2; impact.hitIndex = 0;
            impact.result = new P1ImpactResultV2 { hit = true, amount = 27, hpDamage = 27 };
            t.Replies.Enqueue(Reply(Page(Event(), impact)));
            Check((await c.ReadEventsAsync(None)).Success && c.EventCursor == 2, "reliable events advance cursor");
            Check(c.DrainPresentationEvents().Single().type == "IMPACT", "command plus event replay presents cast start once");
            Check(c.World.entities[0].hp == 192, "impact amount is never subtracted from snapshot HP locally");
            t.Replies.Enqueue(Reply(World(4, hp: 165))); await c.ReadWorldAsync(None);
            Check(c.World.entities[0].hp == 165, "next world snapshot supplies actual HP");
            var bad = Event(3, "IMPACT"); bad.result = new P1ImpactResultV2 { hit = true, amount = -1 };
            t.Replies.Enqueue(Reply(Page(Event(3), bad)));
            Check(!(await c.ReadEventsAsync(None)).Success && c.EventCursor == 2 && c.DrainPresentationEvents().Length == 0, "invalid page has no partial event effects");
            t.Replies.Enqueue(Reply(new P1EventPageV2 { schemaVersion = 2, sessionId = Session, nextCursor = 5, resyncRequired = true,
                resyncReason = "BUFFER_OVERFLOW", events = new P1EventV2[0] })); t.Replies.Enqueue(Reply(World(5, 150)));
            Check((await c.ReadEventsAsync(None)).Success && c.EventCursor == 5 && c.EventResyncCount == 1 && c.DrainPresentationEvents().Length == 0, "overflow reconciles snapshot silently");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(new P1HttpReply { StatusCode = 0 }); await c.CastAsync("SK-MK-01", null, 0, -1, None);
            var original = t.Requests.Last();
            Check(c.HasPendingMutation && c.World.self.mp == 50 && c.DrainPresentationEvents().Length == 0, "lost v2 cast retains intent without MP/VFX fabrication");
            t.Replies.Enqueue(Reply(World(2, mp: 38))); await c.ReadWorldAsync(None);
            Check(c.HasPendingMutation && c.State == P1ConnectionState.UncertainMutation, "v2 snapshot cannot cancel pending mutation");
            var accepted = Cast("SKILL"); accepted.mp = 38; accepted.mpCost = 12;
            t.Replies.Enqueue(Reply(accepted)); t.Replies.Enqueue(Reply(World(3, mp: 38)));
            Check((await c.RetryPendingAsync(None)).Success && !c.HasPendingMutation, "v2 retry resolves exact cast");
            Check(t.Requests.Where(r => r.Path == "/p1/v2/combat").Last().Body == original.Body, "v2 retry preserves IDs, body and sequence");
            Check(c.World.self.mp == 38 && c.DrainPresentationEvents().Length == 1, "confirmed cost from snapshot, single start event");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(new P1HttpReply { StatusCode = 0 }); await c.InteractAsync(Node, None); var original = t.Requests.Last();
            t.Replies.Enqueue(Reply(new P1InteractResult { interactionId = EventId, targetId = Node, recordId = "MAN-PACKAGE-1", kind = "INTERACTABLE",
                outcome = "collected", targetState = "DEPLETED", claimedAtUtc = Now, questUpdates = new[] { Quest() } }, 1));
            t.Replies.Enqueue(Reply(World(2)));
            Check((await c.RetryPendingAsync(None)).Success && c.Quests.Single().state == "READY_TO_TURN_IN", "interaction progress only from server receipt");
            Check(t.Requests.Where(r => r.Path == "/p1/world/interact").Last().Body == original.Body && c.Inventory == null, "interaction retry immutable; no invented inventory");
            t.Replies.Enqueue(Reply(null, 1, 422, "inventory_full"));
            Check(!(await c.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Success && c.Quests.Single().state == "READY_TO_TURN_IN" && !c.HasPendingMutation, "full bag rejection keeps quest READY and no grant");
            t.Replies.Enqueue(new P1HttpReply { StatusCode = 0 }); await c.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None); var turn = t.Requests.Last();
            t.Replies.Enqueue(Reply(Receipt(), 1)); t.Replies.Enqueue(Reply(World(3))); t.Replies.Enqueue(Reply(Inventory(), 1));
            Check((await c.RetryPendingAsync(None)).Success && c.Quests.Single().state == "COMPLETED", "turn-in committed before inventory readback");
            Check(t.Requests.Where(r => r.Path == "/p1/quests/turnin").Last().Body == turn.Body, "turn-in retry retains idempotency key");
            Check(c.Inventory.currencies.Single().amount == 20 && !c.LastTurnIn.rewards.xp.applied, "money comes from inventory snapshot; unapplied XP not claimed");
            Check(c.Inventory.items.Length == 0 && c.DrainAudioNotices().Length == 0, "receipt does not fabricate item instance or acceptance sound");
        }
        {
            var t = new Script(); var c = await Connect(t);
            var wrong = Receipt(); wrong.questState.questId = "P00-02"; t.Replies.Enqueue(Reply(wrong, 1));
            Check(!(await c.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Success && c.HasPendingMutation && c.Quests.Length == 0, "wrong quest success cannot apply or discard pending");
        }
        {
            var t = new Script(); var c = await Connect(t); t.KeepReplyRequestIdOnce = true;
            t.Replies.Enqueue(Reply(Cast()));
            Check(!(await c.BasicAttackAsync(Mob, 1, 0, None)).Success && c.HasPendingMutation && c.DrainPresentationEvents().Length == 0,
                "wrong request receipt cannot resolve a different pending command");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(Reply(Legacy(), 1)); t.Replies.Enqueue(new P1HttpReply { StatusCode = 0 });
            Check(!(await c.MoveAsync(1, 0, None)).Success && c.World.entities.Length == 3 && c.WorldV2.revision == 1,
                "failed v2 refresh after move preserves full last v2 scene rather than replacing it with empty v1 entities");
        }
        {
            var t = new Script(); var c = await Connect(t); var missingStart = Cast(); missingStart.events = new P1EventV2[0]; t.Replies.Enqueue(Reply(missingStart));
            Check(!(await c.BasicAttackAsync(Mob, 1, 0, None)).Success && c.HasPendingMutation, "empty event success violates the v2 command contract");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(Reply(new P1EventPageV2 { schemaVersion = 2, sessionId = Session, nextCursor = 7, resyncRequired = true,
                resyncReason = "BUFFER_OVERFLOW", events = new P1EventV2[0] })); t.Replies.Enqueue(new P1HttpReply { StatusCode = 0 });
            Check(!(await c.ReadEventsAsync(None)).Success && c.EventCursor == 0, "failed snapshot reconciliation cannot advance past missing events");
        }
        {
            var t = new Script(); var c = await Connect(t);
            t.Replies.Enqueue(Reply(Receipt(), 1)); t.Replies.Enqueue(Reply(World(2))); t.Replies.Enqueue(new P1HttpReply { StatusCode = 503, Body = "Unavailable" });
            Check(!(await c.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", None)).Success && !c.HasPendingMutation &&
                c.Quests.Single().state == "COMPLETED" && c.Inventory == null && c.State == P1ConnectionState.NeedsResync,
                "committed turn-in with failed inventory refresh never fabricates money or retries a new grant");
            Check(c.LastError == "reward_refresh_pending", "UI distinguishes a committed reward from an uncommitted failure");
        }
        {
            var t = new Script(); t.Replies.Enqueue(Reply(Legacy(), 1, 201)); t.Replies.Enqueue(new P1HttpReply { StatusCode = 404, Body = "" });
            var c = new P1Client(t, useWorldV2: true);
            Check(!(await c.ConnectAsync(None)).Success && c.WorldV2 == null && c.State == P1ConnectionState.NeedsResync, "flag-off v2 never silently falls back to fake world");
        }
        Console.WriteLine("PASS P1 v2/interaction/reward assertions: " + assertions);
    }
}
