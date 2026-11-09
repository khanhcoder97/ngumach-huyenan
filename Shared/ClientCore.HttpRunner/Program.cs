using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Handshake;
using NguMach.Client.Core.Tutorial;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace ClientCoreHttpRunner
{
    internal static class Program
    {
        private const string ChestTemplate = "EQ-MK-CHEST-T1-R-COMMON";
        private const string CharacterA = "CHR_WO26_ALPHA_A";
        private const string CharacterB = "CHR_WO26_ALPHA_B";
        private const string TalkNpc = "NPC_LYAN";
        private const string TalkOfferNode = "DLG_P00_01_OFFER";
        private const string TalkClueNode = "DLG_P00_01_CLUE";
        private const string PortalBenMua = "TP_BM_THANH_LAC";
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
            public string LastEquipBody;
            public string LastTalkBody;
            // Portal receipts are captured the same way as turn-in/talk so the
            // runner can replay the exact body (same idempotency key) and can
            // compare the raw wire shape against PortalResponse.schema.json even
            // when the strict typed parser rejects that shape.
            public string LastPortalBody;
            public int LastPortalStatus;
            public string LastPortalResponse;
            public bool LoseTurnInResponseOnce;
            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }
            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                if (req.Path == "/p1/quests/turnin" && req.Body != null) LastTurnInBody = req.Body;
                if (req.Path == "/p1/inventory/v2/equip" && req.Body != null) LastEquipBody = req.Body;
                if (req.Path == "/p1/quests/talk" && req.Body != null) LastTalkBody = req.Body;
                if (req.Path == "/p1/world/portal" && req.Body != null) LastPortalBody = req.Body;
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
                        if (req.Path == "/p1/world/portal")
                        {
                            LastPortalStatus = (int)reply.StatusCode;
                            LastPortalResponse = body;
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

        private static async Task WalkTo(P1Client c, double x, int maxSteps = 240)
        {
            for (int i = 0; i < maxSteps && Math.Abs(c.World.self.x - x) > 0.75; i++)
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

        // P1_ALPHA_MODE is set by run_http.py for the paired server. An unknown
        // value must fail the run instead of silently measuring the wrong gate set.
        private static bool AlphaMode()
        {
            var mode = Environment.GetEnvironmentVariable("P1_ALPHA_MODE");
            if (string.IsNullOrWhiteSpace(mode) || mode == "gates-off") return false;
            if (mode == "private-alpha") return true;
            throw new Exception("unknown P1_ALPHA_MODE: " + mode);
        }

        private static DeploymentProfile ProfileFor(bool alpha)
        {
            return alpha
                ? DeploymentProfile.PrivateAlpha(
                    encounterEnabled: true, inventoryV2Enabled: true, deathReturnEnabled: true,
                    questTalkEnabled: true, portalEnabled: true)
                : DeploymentProfile.PrivateAlpha(encounterEnabled: false);
        }

        private static bool Contains(string[] values, string value)
        {
            if (values == null) return false;
            for (int i = 0; i < values.Length; i++)
                if (string.Equals(values[i], value, StringComparison.Ordinal)) return true;
            return false;
        }

        // The same routes the alpha server would expose must be genuinely absent
        // when the paired server runs with every private-alpha gate OFF. A client
        // that passed because it never called them would prove nothing.
        private static async Task CheckGatesOffNegatives(P1Client c)
        {
            var inv = await c.ReadInventoryV2Async(CancellationToken.None);
            Check(!inv.Success && inv.Code == "feature_unavailable", "gates-off inventory v2 absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off inventory v2 cleans pending");

            var talk = await c.TalkAsync(TalkNpc, TalkOfferNode, CancellationToken.None);
            Check(!talk.Success && talk.Code == "feature_unavailable", "gates-off talk absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off talk cleans pending");

            var portal = await c.PortalAsync(PortalBenMua, CancellationToken.None);
            Check(!portal.Success && portal.Code == "feature_unavailable", "gates-off portal absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off portal cleans pending");

            var death = await c.ReturnFromDeathAsync(CancellationToken.None);
            Check(!death.Success && death.Code == "feature_unavailable", "gates-off death-return absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off death-return cleans pending");

            var equip = await c.EquipV2Async("ITM_" + new string('A', 28), 1, CancellationToken.None);
            Check(!equip.Success && equip.Code == "feature_unavailable", "gates-off equip absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off equip cleans pending");

            var unequip = await c.UnequipV2Async("CHEST", 1, CancellationToken.None);
            Check(!unequip.Success && unequip.Code == "feature_unavailable", "gates-off unequip absent");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "gates-off unequip cleans pending");
        }

        // Twelve-slot inventory plus equip/replay/unequip against the real route.
        // The replay reuses the captured body so the same idempotency key is sent.
        private static async Task CheckAlphaInventory(P1Client c, Http http, string baseUrl)
        {
            Check((await c.ReadInventoryV2Async(CancellationToken.None)).Success, "alpha inventory v2 read");
            Check(c.InventoryV2 != null && c.InventoryV2.slots.Length == 12, "alpha inventory v2 twelve slots");
            Check(c.InventoryV2 != null && c.InventoryV2.bagSlots == 100, "alpha inventory v2 bagSlots 100");
            Check(c.InventoryV2 != null && c.InventoryV2.slotSpec == "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT", "alpha inventory v2 slotSpec");
            Check(c.InventoryV2 != null && c.InventoryV2.bag != null, "alpha inventory v2 bag present");
            var chest = c.InventoryV2 == null ? null :
                c.InventoryV2.bag.FirstOrDefault(i => i != null && i.templateId == ChestTemplate);
            Check(chest != null, "alpha chest in bag");

            long before = c.InventoryV2.inventoryRevision;
            var equip = await c.EquipV2Async(chest.instanceId, before, CancellationToken.None);
            Check(equip.Success && !c.HasPendingMutation, "alpha equip chest accepted: " + (equip.Code ?? "ok"));
            Check(c.InventoryV2.inventoryRevision > before, "alpha equip advances revision");
            var chestSlot = c.InventoryV2.slots.First(s => s.slotId == "CHEST");
            Check(chestSlot.item != null && chestSlot.item.instanceId == chest.instanceId, "alpha chest in CHEST slot");
            Check(!string.IsNullOrWhiteSpace(http.LastEquipBody), "alpha captured equip body");

            long equippedRevision = c.InventoryV2.inventoryRevision;
            var replay = await RawPost(baseUrl, "/p1/inventory/v2/equip", http.LastEquipBody, c.SessionId);
            var replayBody = await replay.Content.ReadAsStringAsync();
            Check((int)replay.StatusCode == 200, "alpha equip replay accepted");
            // Equip replay is snapshot-shaped: same ledger entry, same revision and
            // the same equipped instance, not a second move.
            Check(replayBody.Contains("\"inventoryRevision\":" + equippedRevision, StringComparison.Ordinal) &&
                  replayBody.Contains(chest.instanceId, StringComparison.Ordinal),
                "alpha equip replay same snapshot");
            Check((await c.ReadInventoryV2Async(CancellationToken.None)).Success, "alpha inventory after replay");
            Check(c.InventoryV2.inventoryRevision == equippedRevision, "alpha equip replay no state change");
            Check(c.InventoryV2.slots.First(s => s.slotId == "CHEST").item != null, "alpha chest still equipped");

            var stale = await c.EquipV2Async(chest.instanceId, 1, CancellationToken.None);
            Check(!stale.Success && stale.Code == "revision_conflict", "alpha stale revision refused");
            Check(stale.Retryable && Contains(stale.FieldErrors, "payload.expectedRevision"),
                "alpha stale revision retryable field");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready, "alpha stale revision cleans pending");

            long unequipRevision = c.InventoryV2.inventoryRevision;
            var unequip = await c.UnequipV2Async("CHEST", unequipRevision, CancellationToken.None);
            Check(unequip.Success && !c.HasPendingMutation, "alpha unequip chest accepted: " + (unequip.Code ?? "ok"));
            Check(c.InventoryV2.inventoryRevision > unequipRevision, "alpha unequip advances revision");
            Check(c.InventoryV2.slots.First(s => s.slotId == "CHEST").item == null, "alpha CHEST slot empty");
            Check(c.InventoryV2.bag.Any(i => i != null && i.instanceId == chest.instanceId && i.location == "BAG"),
                "alpha chest back in bag");
        }

        // TALK positive on B before P00-01 is accepted (the OFFER node is
        // QUEST_AVAILABLE), plus the three refusal shapes the wire defines.
        private static async Task CheckAlphaTalk(P1Client c, Http http, string baseUrl)
        {
            var far = await c.TalkAsync(TalkNpc, TalkOfferNode, CancellationToken.None);
            Check(!far.Success && far.Code == "out_of_range", "alpha talk far refused");
            Check(far.Retryable && !Contains(far.FieldErrors, "revealGate"), "alpha talk far retryable");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready && c.LastTalk == null,
                "alpha talk far cleans pending");

            await WalkTo(c, 42);

            var wrong = await c.TalkAsync("NPC_TA_VAN_KHANH", TalkOfferNode, CancellationToken.None);
            Check(!wrong.Success && wrong.Code == "npc_mismatch", "alpha talk wrong speaker refused");
            Check(!wrong.Retryable && Contains(wrong.FieldErrors, "payload.npcId"), "alpha talk wrong speaker field");
            Check(!c.HasPendingMutation && c.LastTalk == null, "alpha talk wrong speaker cleans pending");

            var closed = await c.TalkAsync(TalkNpc, TalkClueNode, CancellationToken.None);
            Check(!closed.Success && closed.Code == "invalid_transition", "alpha talk closed reveal refused");
            Check(closed.Retryable && Contains(closed.FieldErrors, "revealGate"), "alpha talk reveal gate field");
            Check(!c.HasPendingMutation && c.LastTalk == null, "alpha talk reveal gate cleans pending");

            var ok = await c.TalkAsync(TalkNpc, TalkOfferNode, CancellationToken.None);
            Check(ok.Success, "alpha talk offer accepted: " + (ok.Code ?? "ok"));
            Check(c.LastTalk != null && c.LastTalk.questId == "P00-01" && c.LastTalk.npcId == TalkNpc &&
                  c.LastTalk.nodeId == TalkOfferNode, "alpha talk receipt identity");
            Check(c.LastTalk != null && !c.LastTalk.credited && c.LastTalk.objectiveId == null &&
                  c.LastTalk.eventId == null, "alpha talk narrative node credits nothing");
            Check(c.State == P1ConnectionState.NeedsResync, "alpha talk requires fresh read");
            Check((await c.ReadWorldAsync(CancellationToken.None)).Success && c.State == P1ConnectionState.Ready,
                "alpha talk fresh world read");

            Check(!string.IsNullOrWhiteSpace(http.LastTalkBody), "alpha captured talk body");
            var replay = await RawPost(baseUrl, "/p1/quests/talk", http.LastTalkBody, c.SessionId);
            var replayBody = await replay.Content.ReadAsStringAsync();
            Check((int)replay.StatusCode == 200, "alpha talk replay accepted");
            Check(replayBody.Contains("\"replayed\":true", StringComparison.Ordinal), "alpha talk replay receipt");
        }

        // Portal refusals from the pinned server: out_of_range at distance and
        // portal_locked without the chapter grant. The positive transition is
        // claimed later in CheckAlphaFullTutorial, after P00-05 grants the
        // chapter flag; it is not claimed here pre-completion.
        private static async Task CheckAlphaPortal(P1Client c)
        {
            var far = await c.PortalAsync(PortalBenMua, CancellationToken.None);
            Check(!far.Success && far.Code == "out_of_range", "alpha portal far refused");
            Check(far.Retryable && !Contains(far.FieldErrors, "chapterPermission"), "alpha portal far retryable");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready && c.LastPortal == null,
                "alpha portal far cleans pending");

            // TP_BM_THANH_LAC stands at x=348; the map is 360 WU wide and this
            // walk stays inside the same map and floor.
            await WalkTo(c, 348, 900);

            var locked = await c.PortalAsync(PortalBenMua, CancellationToken.None);
            Check(!locked.Success && locked.Code == "portal_locked", "alpha portal locked refused");
            Check(locked.Retryable && Contains(locked.FieldErrors, "chapterPermission"),
                "alpha portal locked chapter field");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready && c.LastPortal == null,
                "alpha portal locked cleans pending");
        }

        private static async Task CheckAlphaDeathAlive(P1Client c)
        {
            var r = await c.ReturnFromDeathAsync(CancellationToken.None);
            Check(!r.Success && r.Code == "not_downed", "alpha death-return alive refused");
            Check(!c.HasPendingMutation && c.State == P1ConnectionState.Ready,
                "alpha death-return refusal cleans pending");
        }

        private static async Task<HttpResponseMessage> RawGet(string baseUrl, string path, string sessionId)
        {
            using (var http = new HttpClient())
            {
                var msg = new HttpRequestMessage(HttpMethod.Get, baseUrl.TrimEnd('/') + path);
                msg.Headers.Add("X-Session-ID", sessionId);
                msg.Headers.Add("X-Correlation-ID", Guid.NewGuid().ToString("N"));
                return await http.SendAsync(msg);
            }
        }

        private static string Envelope(string characterId, string payloadJson)
        {
            string requestId = Guid.NewGuid().ToString("N");
            string idempotencyKey = Guid.NewGuid().ToString("N");
            string sentAtUtc = DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture);
            return "{\"schemaVersion\":1,\"requestId\":\"" + requestId +
                   "\",\"idempotencyKey\":\"" + idempotencyKey +
                   "\",\"sentAtUtc\":\"" + sentAtUtc +
                   "\",\"characterId\":\"" + characterId +
                   "\",\"payload\":" + payloadJson + "}";
        }

        private static string TalkEnvelope(string characterId, string npcId, string nodeId)
        {
            return Envelope(characterId, "{\"npcId\":\"" + npcId + "\",\"nodeId\":\"" + nodeId + "\"}");
        }

        private static string PortalEnvelope(string characterId, string portalId)
        {
            return Envelope(characterId, "{\"portalId\":\"" + portalId + "\"}");
        }

        private static long JsonLong(string body, string key)
        {
            if (body == null) return long.MinValue;
            string pattern = "\"" + key + "\":";
            int i = body.IndexOf(pattern, StringComparison.Ordinal);
            if (i < 0) return long.MinValue;
            i += pattern.Length;
            int j = i;
            if (j < body.Length && (body[j] == '-' || body[j] == '+')) j++;
            while (j < body.Length && char.IsDigit(body[j])) j++;
            long value;
            if (j <= i || !long.TryParse(body.Substring(i, j - i), NumberStyles.Integer, CultureInfo.InvariantCulture, out value))
                return long.MinValue;
            return value;
        }

        private static double JsonDouble(string body, string key)
        {
            if (body == null) return double.NaN;
            string pattern = "\"" + key + "\":";
            int i = body.IndexOf(pattern, StringComparison.Ordinal);
            if (i < 0) return double.NaN;
            i += pattern.Length;
            int j = i;
            if (j < body.Length && (body[j] == '-' || body[j] == '+')) j++;
            while (j < body.Length && (char.IsDigit(body[j]) || body[j] == '.' || body[j] == 'e' || body[j] == 'E' || body[j] == '-' || body[j] == '+')) j++;
            double value;
            if (j <= i || !double.TryParse(body.Substring(i, j - i), NumberStyles.Float, CultureInfo.InvariantCulture, out value))
                return double.NaN;
            return value;
        }

        private static P1Quest FindQuest(P1Client c, string questId)
        {
            if (c.Quests == null) return null;
            return c.Quests.FirstOrDefault(q => q != null && q.questId == questId);
        }

        private static int QuestCounter(P1Client c, string questId, string objectiveId)
        {
            var q = FindQuest(c, questId);
            if (q == null || q.objectiveCounters == null) return -1;
            int value;
            return q.objectiveCounters.TryGetValue(objectiveId, out value) ? value : -1;
        }

        private static string QuestState(P1Client c, string questId)
        {
            var q = FindQuest(c, questId);
            return q == null ? null : q.state;
        }

        private static long QuestRevision(P1Client c, string questId)
        {
            var q = FindQuest(c, questId);
            return q == null ? -1 : q.revision;
        }

        private static long Coin(P1Client c)
        {
            if (c.Inventory == null || c.Inventory.currencies == null) return -1;
            return c.Inventory.currencies.Where(x => x != null && x.currencyId == "COIN").Sum(x => x.amount);
        }

        private static async Task RefreshQuests(P1Client c, string tag)
        {
            Check((await c.ReadQuestsAsync(CancellationToken.None)).Success, tag);
        }

        private static async Task AdvanceTicks(P1Client c, int wantTicks)
        {
            if (!(await c.ReadWorldAsync(CancellationToken.None)).Success)
                throw new Exception("advance ticks initial world read failed");
            long start = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
            for (int i = 0; i < 4000; i++)
            {
                long now = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
                if (now - start >= wantTicks) return;
                await Task.Delay(25);
                await c.ReadWorldAsync(CancellationToken.None);
            }
            throw new Exception("advance ticks gave up after " + wantTicks + " ticks");
        }

        // Walk the 1.5-WU grid axis-major until the target is inside `within` WU
        // in a straight line (euclidean). Steps are never asserted per step;
        // without a failures list the caller gets one check for the whole walk.
        private static async Task Approach(P1Client c, double targetX, double targetY,
            double within = 3.0, int maxSteps = 800, List<string> failures = null)
        {
            if (!(await c.ReadWorldAsync(CancellationToken.None)).Success)
                throw new Exception("approach initial world read failed");
            var stepFailures = new List<string>();
            double x = c.World.self.x, y = c.World.self.y;
            for (int i = 0; i < maxSteps; i++)
            {
                double dx = targetX - x, dy = targetY - y;
                if (Math.Sqrt(dx * dx + dy * dy) <= within) break;
                P1Result r;
                if (Math.Abs(dx) >= Math.Abs(dy))
                    r = await c.MoveAsync(dx > 0 ? 1 : -1, 0, CancellationToken.None);
                else
                    r = await c.MoveAsync(0, dy > 0 ? 1 : -1, CancellationToken.None);
                if (!r.Success) stepFailures.Add((r.Code ?? "?") + "@" + i);
                x = c.World.self.x; y = c.World.self.y;
                await Task.Delay(80);
            }
            double dist = Math.Sqrt((targetX - x) * (targetX - x) + (targetY - y) * (targetY - y));
            if (failures == null)
            {
                Check(stepFailures.Count == 0, "approach " + targetX + "," + targetY + " no failing moves: " + string.Join(";", stepFailures));
                Check(dist <= within, "approach " + targetX + "," + targetY + " within " + within + " (stopped " + dist.ToString("F2") + " away)");
            }
            else
            {
                failures.AddRange(stepFailures);
                if (dist > within) failures.Add("stop " + dist.ToString("F2") + ">" + within);
            }
        }

        private static async Task AccompanyTo(P1Client c, double limitX, int maxSteps = 60)
        {
            // Pace east while the escort walks at its sourced 3 WU/s. The pause
            // is what lets the domain move the NPC between steps.
            if (!(await c.ReadWorldAsync(CancellationToken.None)).Success)
                throw new Exception("accompany initial world read failed");
            for (int i = 0; i < maxSteps && c.World.self.x < limitX; i++)
            {
                await Task.Delay(500);
                var r = await c.MoveAsync(1, 0, CancellationToken.None);
                if (!r.Success) throw new Exception("accompany move: " + (r.Code ?? "?"));
            }
        }

        private static async Task<bool> WaitQuestCounter(P1Client c, string questId, string objectiveId, int want, int maxTicks)
        {
            if (!(await c.ReadWorldAsync(CancellationToken.None)).Success) return false;
            long start = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
            for (int i = 0; i < 2000; i++)
            {
                await c.ReadQuestsAsync(CancellationToken.None);
                if (QuestCounter(c, questId, objectiveId) >= want) return true;
                long now = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
                if (now - start >= maxTicks) return false;
                await Task.Delay(50);
                await c.ReadWorldAsync(CancellationToken.None);
            }
            return false;
        }

        private static async Task<bool> WaitWaveAlive(P1Client c, IEnumerable<string> members, int maxTicks)
        {
            // Aliveness is healthState ALIVE plus targetable — the same fields
            // the cast path resolves against. `state != DEAD` alone would let
            // a BLOCKED wave look activated.
            if (!(await c.ReadWorldAsync(CancellationToken.None)).Success) return false;
            long start = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
            for (int i = 0; i < 4000; i++)
            {
                var entities = c.WorldV2 != null ? c.WorldV2.entities : null;
                bool allAlive = entities != null;
                if (allAlive)
                    foreach (var id in members)
                    {
                        var e = Array.Find(entities, t => t.entityId == id);
                        if (e == null || e.healthState != "ALIVE" || !e.targetable) { allAlive = false; break; }
                    }
                if (allAlive) return true;
                long now = c.WorldV2 != null ? c.WorldV2.serverTick : c.World.serverTick;
                if (now - start >= maxTicks) return false;
                await Task.Delay(50);
                await c.ReadWorldAsync(CancellationToken.None);
            }
            return false;
        }

        private sealed class KillOutcome
        {
            public bool Died;
            public int Accepted;
            public Dictionary<string, int> Refused = new Dictionary<string, int>();
            public string Reason;
            public int ActorHp, TargetHp;
        }

        private static async Task<KillOutcome> KillEntity(P1Client c, string entityId)
        {
            var outcome = new KillOutcome();
            int? hpSeen = null;
            int hardCap = 0, stall = 0, casts = 0;
            while (true)
            {
                await c.ReadWorldAsync(CancellationToken.None);
                var entities = c.WorldV2 != null ? c.WorldV2.entities : null;
                P1EntityV2 target = entities != null ? Array.Find(entities, t => t.entityId == entityId) : null;
                outcome.ActorHp = c.World.self.hp;
                if (target == null || c.World.self.hp <= 0)
                {
                    outcome.Reason = c.World.self.hp <= 0 ? "actor-down" : "target-row-left-the-audience";
                    return outcome;
                }
                if (target.state == "DEAD" || target.healthState == "DEAD")
                { outcome.Died = true; outcome.Reason = "witnessed-dead"; outcome.TargetHp = target.hp; return outcome; }
                outcome.TargetHp = target.hp;
                bool noProgress;
                if (hpSeen == null) { hardCap = target.maxHp + 200; noProgress = false; }
                else noProgress = target.hp >= hpSeen.Value;
                hpSeen = target.hp;
                double gapX = target.x - c.World.self.x, gapY = target.y - c.World.self.y;
                double distance = Math.Sqrt(gapX * gapX + gapY * gapY);
                if (distance > 2.5)
                {
                    // Close in on the longer axis first: walking past the target
                    // is as useless as missing it (facing cone).
                    var move = Math.Abs(gapX) >= Math.Abs(gapY)
                        ? await c.MoveAsync(gapX >= 0 ? 1 : -1, 0, CancellationToken.None)
                        : await c.MoveAsync(0, gapY >= 0 ? 1 : -1, CancellationToken.None);
                    if (!move.Success) { string code = move.Code ?? "?"; outcome.Refused[code] = outcome.Refused.TryGetValue(code, out var n) ? n + 1 : 1; }
                    await Task.Delay(100);
                    continue;
                }
                double aimX = distance > 0 ? gapX / distance : 1.0;
                double aimY = distance > 0 ? gapY / distance : 0.0;
                var hit = await c.BasicAttackAsync(entityId, aimX, aimY, CancellationToken.None);
                if (hit.Success) outcome.Accepted++;
                else { string code = hit.Code ?? "?"; outcome.Refused[code] = outcome.Refused.TryGetValue(code, out var n2) ? n2 + 1 : 1; }
                casts++;
                stall = noProgress ? stall + 1 : 0;
                if (stall > 60 || casts > hardCap)
                {
                    outcome.Reason = stall > 60 ? "cast-ceiling-no-hp-movement" : "cast-ceiling-hard-cap";
                    return outcome;
                }
                await Task.Delay(120);
            }
        }

        private static async Task EnsureAlive(P1Client c, string label)
        {
            await c.ReadWorldAsync(CancellationToken.None);
            if (c.World.self.hp > 0) return;
            var r = await c.ReturnFromDeathAsync(CancellationToken.None);
            if (!r.Success)
                Console.WriteLine("WARN " + label + ": death-return after death did not apply (code " + (r.Code ?? "?") + ")");
            else
                await c.ReadWorldAsync(CancellationToken.None);
        }

        private static async Task KillWatched(P1Client c, (string Id, double X, double Y)[] pool, int wanted, string label)
        {
            int deaths = 0, attempts = 0;
            var refused = new Dictionary<string, int>();
            var walkFailures = new List<string>();
            while (deaths < wanted && attempts < wanted * 4)
            {
                foreach (var member in pool)
                {
                    if (deaths >= wanted) break;
                    attempts++;
                    await c.ReadWorldAsync(CancellationToken.None);
                    var entities = c.WorldV2 != null ? c.WorldV2.entities : null;
                    var row = entities != null ? Array.Find(entities, t => t.entityId == member.Id) : null;
                    // A row that is present and DEAD is a witnessed death. An
                    // ABSENT row stays uncounted: group respawn makes absence
                    // ambiguous, so only presence plus DEAD credits.
                    if (row != null && (row.state == "DEAD" || row.healthState == "DEAD")) { deaths++; continue; }
                    await Approach(c, member.X, member.Y, 3.0, 800, walkFailures);
                    var outcome = await KillEntity(c, member.Id);
                    foreach (var kv in outcome.Refused)
                        refused[kv.Key] = refused.TryGetValue(kv.Key, out var n) ? n + kv.Value : kv.Value;
                    if (outcome.Died) deaths++;
                }
            }
            Check(deaths >= wanted && walkFailures.Count == 0,
                label + ": witnessed " + deaths + " of " + wanted + " deaths (attempts " + attempts +
                ", refusals " + refused.Count + " kinds, walks " + walkFailures.Count + ")");
        }

        private static async Task CheckTalkRefusalRaw(string baseUrl, string characterId, string sessionId,
            string npcId, string nodeId, int wantStatus, string wantCode, string wantField, string label)
        {
            var reply = await RawPost(baseUrl, "/p1/quests/talk", TalkEnvelope(characterId, npcId, nodeId), sessionId);
            var body = await reply.Content.ReadAsStringAsync();
            // Server DTOs omit Result when null (WhenWritingNull), so "no
            // result" is the absence of a result object, not a `"result":null`.
            Check((int)reply.StatusCode == wantStatus &&
                  body.Contains("\"" + wantCode + "\"", StringComparison.Ordinal) &&
                  body.Contains(wantField, StringComparison.Ordinal) &&
                  !body.Contains("\"result\":{", StringComparison.Ordinal),
                "FT talk " + label + " expected " + wantStatus + " " + wantCode + " naming " + wantField + " with no result");
        }

        // Checkpoint 2: the full alpha tutorial played through the typed client
        // (plus raw envelopes where the wire shape itself is the assertion).
        // Entry state is the end of the checkpoint-1 flow: A has P00-01
        // COMPLETED and P00-02 ACTIVE, standing at the portal anchor after the
        // refusal probes. Legs mirror the e2e alpha-p00 journey positions and
        // counters; timings are server ticks, never stopwatches.
        private static async Task CheckAlphaFullTutorial(P1Client a, Http httpA, string baseUrl, P1Client b)
        {
            string character = a.World.self.characterId;
            string sessionId = a.SessionId;
            const double turnInX = 64.0;

            await RefreshQuests(a, "FT entry quests read");
            Check(QuestState(a, "P00-01") == "COMPLETED" && QuestCounter(a, "P00-01", "OBJ_P00_01_PACKAGES") == 3, "FT entry P00-01 completed");
            Check(QuestState(a, "P00-02") == "ACTIVE", "FT entry P00-02 active");

            // ── C1-01 refusal: the level-11 slice stays LOCKED ──
            // The refusal's wire shape (retryable/fieldErrors) is asserted raw
            // because the typed AcceptQuest legacy path only surfaces the code.
            await Approach(a, 42.0, 0.0);
            long c1RevisionBefore = QuestRevision(a, "C1-01");
            var c1Reply = await RawPost(baseUrl, "/p1/quests/accept",
                Envelope(character, "{\"questId\":\"C1-01\",\"npcId\":\"NPC_LYAN\"}"), sessionId);
            var c1Body = await c1Reply.Content.ReadAsStringAsync();
            // The refusal carries the authoritative quest state (LOCKED), not
            // a null result: QuestAcceptError includes outcome.State.
            Check((int)c1Reply.StatusCode == 422 &&
                  c1Body.Contains("\"prerequisite_not_met\"", StringComparison.Ordinal) &&
                  c1Body.Contains("\"retryable\":false", StringComparison.Ordinal) &&
                  c1Body.Contains("\"fieldErrors\":", StringComparison.Ordinal) &&
                  c1Body.Contains("\"level\"", StringComparison.Ordinal) &&
                  c1Body.Contains("\"questId\":\"C1-01\"", StringComparison.Ordinal) &&
                  c1Body.Contains("\"state\":\"LOCKED\"", StringComparison.Ordinal), "FT C1 refusal field");
            Check(!a.HasPendingMutation, "FT C1 refusal cleans pending");
            await RefreshQuests(a, "FT C1 quests read after refusal");
            Check(QuestState(a, "C1-01") == "LOCKED" && QuestRevision(a, "C1-01") == c1RevisionBefore, "FT C1 locked unchanged");

            // ── P00-02: ripples, CARPLING loot, turn-in ──
            var ripples = new[] { ("ALPHA_OBJ_BM_RIPPLE_01", 70.0, 3.0), ("ALPHA_OBJ_BM_RIPPLE_02", 86.0, -3.0), ("ALPHA_OBJ_BM_RIPPLE_03", 104.0, 3.0) };
            for (int i = 0; i < ripples.Length; i++)
            {
                await Approach(a, ripples[i].Item2, ripples[i].Item3);
                var act = await a.InteractAsync(ripples[i].Item1, CancellationToken.None);
                Check(act.Success, "FT ripple " + ripples[i].Item1 + ": " + (act.Code ?? "ok"));
                await RefreshQuests(a, "FT ripple " + ripples[i].Item1 + " quests");
                Check(QuestCounter(a, "P00-02", "OBJ_P00_02_RIPPLES") == i + 1, "FT ripple counter " + (i + 1));
            }
            Check((await a.ReadInventoryAsync(CancellationToken.None)).Success, "FT loot inv before");
            long coinBefore = Coin(a), revBefore = a.Inventory != null ? a.Inventory.inventoryRevision : -1;
            var carpling = new[] { ("ENT_MAN_BM_SPAWN_BM_01", 84.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_01_M2", 84.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_01_M3", 84.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_02", 116.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_02_M2", 116.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_02_M3", 116.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_02_M4", 116.0, 0.0) };
            await KillWatched(a, carpling, 4, "FT P00-02 CARPLING");
            Check((await a.ReadInventoryAsync(CancellationToken.None)).Success, "FT loot inv after");
            long coinDelta = Coin(a) - coinBefore;
            long revDelta = (a.Inventory != null ? a.Inventory.inventoryRevision : -1) - revBefore;
            Check(coinDelta >= 20 && coinDelta <= 40 && revDelta == 4, "FT CARPLING loot paid (coin +" + coinDelta + ", rev +" + revDelta + ")");
            await RefreshQuests(a, "FT carpling quests");
            Check(QuestCounter(a, "P00-02", "OBJ_P00_02_CARPLING") >= 4, "FT CARPLING counter");
            await Approach(a, turnInX, 0.0);
            var turn2 = await a.TurnInQuestAsync("P00-02", "NPC_TA_VAN_KHANH", CancellationToken.None);
            Check(turn2.Success && a.LastTurnIn != null && a.LastTurnIn.unlocks != null && a.LastTurnIn.unlocks.Length == 1 && a.LastTurnIn.unlocks[0] == "P00-03" &&
                  a.LastTurnIn.questState.state == "COMPLETED" && a.LastTurnIn.rewards.xp.applied, "FT turn-in P00-02 unlocks P00-03");

            // ── P00-03: villagers, WATERROOT, wave-trial dodge, turn-in ──
            await Approach(a, 42.0, 0.0);
            var acc3 = await a.AcceptQuestAsync("P00-03", "NPC_LYAN", CancellationToken.None);
            Check(acc3.Success, "FT accept P00-03: " + (acc3.Code ?? "ok"));
            var villagers = new[] { ("ALPHA_OBJ_BM_VILLAGER_01", 138.0, 3.0), ("ALPHA_OBJ_BM_VILLAGER_02", 146.0, 3.0) };
            for (int i = 0; i < villagers.Length; i++)
            {
                await Approach(a, villagers[i].Item2, villagers[i].Item3);
                var act = await a.InteractAsync(villagers[i].Item1, CancellationToken.None);
                Check(act.Success, "FT villager " + villagers[i].Item1 + ": " + (act.Code ?? "ok"));
                await RefreshQuests(a, "FT villager quests " + villagers[i].Item1);
                Check(QuestCounter(a, "P00-03", "OBJ_P00_03_VILLAGERS") == i + 1, "FT villager counter " + (i + 1));
            }
            var waterroot = new[] { ("ENT_MAN_BM_SPAWN_BM_03", 143.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_03_M2", 143.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_03_M3", 143.0, 0.0), ("ENT_MAN_BM_SPAWN_BM_04_M2", 160.0, 0.0) };
            await KillWatched(a, waterroot, 3, "FT P00-03 WATERROOT");
            // Training-wave dodge: dip inside the sourced rect (140,-2)-(148,2),
            // step out, then wait the hazard's own windup (24 ticks) on the
            // server clock. Only standing outside at the impact frame credits.
            var dodgeFailures = new List<string>();
            for (int attempt = 0; attempt < 6 && QuestCounter(a, "P00-03", "OBJ_P00_03_WAVE_TRIAL") < 1; attempt++)
            {
                await Approach(a, 142.0, 0.0, 1.0, 800, dodgeFailures);
                await Approach(a, 134.0, 0.0, 1.0, 800, dodgeFailures);
                await AdvanceTicks(a, 24);
                await RefreshQuests(a, "FT wave trial probe");
            }
            bool waveCredited = await WaitQuestCounter(a, "P00-03", "OBJ_P00_03_WAVE_TRIAL", 1, 400);
            Check(waveCredited && dodgeFailures.Count == 0, "FT wave trial dodge credited");
            await Approach(a, 42.0, 0.0);
            var turn3 = await a.TurnInQuestAsync("P00-03", "NPC_LYAN", CancellationToken.None);
            Check(turn3.Success && a.LastTurnIn != null && a.LastTurnIn.questState.state == "COMPLETED", "FT turn-in P00-03 to LYAN");

            // ── TALK refusals over the raw wire (3 shapes) ──
            // Standing at LYAN's anchor, so the requests reach the reveal gate
            // instead of the distance guard.
            await CheckTalkRefusalRaw(baseUrl, character, sessionId, "NPC_LYAN", "DLG_C1_01_OFFER", 409, "invalid_transition", "revealGate", "reveal gate");
            await CheckTalkRefusalRaw(baseUrl, character, sessionId, "NPC_TA_VAN_KHANH", "DLG_C1_01_OFFER", 422, "npc_mismatch", "payload.npcId", "wrong speaker");
            await CheckTalkRefusalRaw(baseUrl, character, sessionId, "NPC_LYAN", "DLG_SELFCHECK_NOT_IN_BUNDLE", 404, "narrative_unknown_node", "payload.nodeId", "unpublished node");
            await RefreshQuests(a, "FT talk refusal quests");
            Check(QuestCounter(a, "P00-05", "OBJ_P00_05_CLASS_CONFIRM") == 0 && QuestState(a, "C1-01") != "AVAILABLE", "FT refused talk changed nothing");

            // ── P00-04: escort waves A/B, NPC read model, AOI leave/return ──
            await Approach(a, turnInX, 0.0);
            var acc4 = await a.AcceptQuestAsync("P00-04", "NPC_TA_VAN_KHANH", CancellationToken.None);
            Check(acc4.Success, "FT accept P00-04: " + (acc4.Code ?? "ok"));
            await Approach(a, 42.0, 0.0);
            var waveA = new[] { ("ENT_MAN_BM_WAVE_BM_ESCORT_A", 80.0, 0.0), ("ENT_MAN_BM_WAVE_BM_ESCORT_A_M2", 80.0, 0.0), ("ENT_MAN_BM_WAVE_BM_ESCORT_A_M3", 80.0, 0.0) };
            var waveB = new[] { ("ENT_MAN_BM_WAVE_BM_ESCORT_B", 120.0, 0.0), ("ENT_MAN_BM_WAVE_BM_ESCORT_B_M2", 120.0, 0.0), ("ENT_MAN_BM_WAVE_BM_ESCORT_B_M3", 120.0, 0.0) };
            await AccompanyTo(a, 82.0);
            Check(await WaitWaveAlive(a, waveA.Select(w => w.Item1), 1200), "FT wave A activated");
            Func<double?> escortedNpcX = () =>
            {
                if (a.WorldV2 == null) return null;
                var row = a.WorldV2.entities.FirstOrDefault(e => e != null && e.kind == "NPC" && e.entityId.Contains("LYAN"));
                return row == null ? (double?)null : row.x;
            };
            Check(escortedNpcX() != null, "FT escorted NPC in audience");
            double npcBefore = escortedNpcX().Value;
            await EnsureAlive(a, "FT P00-04 wave A");
            await KillWatched(a, waveA, 3, "FT P00-04 wave A");
            await AdvanceTicks(a, 160);
            Check(escortedNpcX() != null && escortedNpcX().Value > npcBefore, "FT escorted NPC moved in read model");
            // AOI: walk 60 WU north; the escort row must leave the audience,
            // then re-enter on the road (not at the canonical anchor 42).
            var aoiFailures = new List<string>();
            double npcBeforeAoi = escortedNpcX().Value;
            await EnsureAlive(a, "FT P00-04 AOI");
            await Approach(a, npcBeforeAoi, 0.0, 2.0, 800, aoiFailures);
            await Approach(a, npcBeforeAoi, 60.0, 1.0, 800, aoiFailures);
            Check(aoiFailures.Count == 0, "FT AOI walk away had no failing moves");
            Check(escortedNpcX() == null, "FT escort row left audience 60 WU away");
            double escortedX = npcBeforeAoi;
            await Approach(a, escortedX, 0.0, 2.0, 800, aoiFailures);
            Check(aoiFailures.Count == 0, "FT AOI walk back had no failing moves");
            Check(escortedNpcX() != null && escortedNpcX().Value > 42.0 && escortedNpcX().Value <= 120.0, "FT escort row returned to the road");
            await AccompanyTo(a, 122.0);
            Check(await WaitWaveAlive(a, waveB.Select(w => w.Item1), 1500), "FT wave B activated");
            await EnsureAlive(a, "FT P00-04 wave B");
            await KillWatched(a, waveB, 3, "FT P00-04 wave B");
            await RefreshQuests(a, "FT escort quests");
            Console.WriteLine("FT escort diagnostic: state=" + (QuestState(a, "P00-04") ?? "<null>") +
                              " waveA=" + QuestCounter(a, "P00-04", "OBJ_P00_04_WAVE_A") +
                              " waveB=" + QuestCounter(a, "P00-04", "OBJ_P00_04_WAVE_B") +
                              " actor=" + a.World.self.x.ToString("F1") + "," + a.World.self.y.ToString("F1") +
                              " hp=" + a.World.self.hp);
            bool escortCounters = await WaitQuestCounter(a, "P00-04", "OBJ_P00_04_WAVE_A", 3, 200) &&
                                  await WaitQuestCounter(a, "P00-04", "OBJ_P00_04_WAVE_B", 3, 200);
            Check(escortCounters, "FT escort wave counters");
            await Approach(a, turnInX, 0.0);
            var turn4 = await a.TurnInQuestAsync("P00-04", "NPC_TA_VAN_KHANH", CancellationToken.None);
            Check(turn4.Success && a.LastTurnIn != null && a.LastTurnIn.unlocks != null && a.LastTurnIn.unlocks.Length == 1 && a.LastTurnIn.unlocks[0] == "P00-05", "FT turn-in P00-04 unlocks P00-05");

            // ── P00-05: CLUE talk, portal-far, replay/conflict, boss, fragment ──
            await Approach(a, turnInX, 0.0);
            var acc5 = await a.AcceptQuestAsync("P00-05", "NPC_TA_VAN_KHANH", CancellationToken.None);
            Check(acc5.Success, "FT accept P00-05: " + (acc5.Code ?? "ok"));
            string clueEnvelope = TalkEnvelope(character, "NPC_TA_VAN_KHANH", "DLG_P00_05_CLUE");
            var clueReply = await RawPost(baseUrl, "/p1/quests/talk", clueEnvelope, sessionId);
            var clueBody = await clueReply.Content.ReadAsStringAsync();
            Check((int)clueReply.StatusCode == 200 &&
                  clueBody.Contains("\"questId\":\"P00-05\"", StringComparison.Ordinal) &&
                  clueBody.Contains("\"nodeId\":\"DLG_P00_05_CLUE\"", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"xp\":", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"rewards\":", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"currency\":", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"unlocks\":", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"chapterUnlock\":", StringComparison.Ordinal) &&
                  !clueBody.Contains("\"destination\":", StringComparison.Ordinal),
                "FT CLUE talk grant-free receipt");
            // Portal-far over the raw wire: distance guard, nobody moves.
            await a.ReadWorldAsync(CancellationToken.None);
            double farX = a.World.self.x, farY = a.World.self.y;
            var farReply = await RawPost(baseUrl, "/p1/world/portal", PortalEnvelope(character, PortalBenMua), sessionId);
            var farBody = await farReply.Content.ReadAsStringAsync();
            Check((int)farReply.StatusCode == 422 && farBody.Contains("\"out_of_range\"", StringComparison.Ordinal) &&
                  !farBody.Contains("\"result\":{", StringComparison.Ordinal), "FT portal far refused");
            await a.ReadWorldAsync(CancellationToken.None);
            Check(a.World.self.x == farX && a.World.self.y == farY, "FT refused portal moved nobody");
            // TALK replay away from the NPC: same envelope must return the
            // stored receipt; same key with a changed body must conflict.
            await Approach(a, 178.0, 0.0);
            long talkRevBefore = QuestRevision(a, "P00-05");
            int talkCntBefore = QuestCounter(a, "P00-05", "OBJ_P00_05_CLASS_CONFIRM");
            var replayReply = await RawPost(baseUrl, "/p1/quests/talk", clueEnvelope, sessionId);
            var replayBody = await replayReply.Content.ReadAsStringAsync();
            Check((int)replayReply.StatusCode == 200 && replayBody.Contains("\"replayed\":true", StringComparison.Ordinal) &&
                  JsonLong(replayBody, "revision") == JsonLong(clueBody, "revision"), "FT talk replay stored receipt");
            var conflictReply = await RawPost(baseUrl, "/p1/quests/talk", clueEnvelope.Replace("DLG_P00_05_CLUE", "DLG_P00_05_OFFER"), sessionId);
            var conflictBody = await conflictReply.Content.ReadAsStringAsync();
            Check((int)conflictReply.StatusCode == 409 && conflictBody.Contains("\"idempotency_conflict\"", StringComparison.Ordinal) &&
                  conflictBody.Contains("idempotencyKey", StringComparison.Ordinal), "FT talk changed-body conflict");
            await RefreshQuests(a, "FT talk replay quests");
            Check(QuestRevision(a, "P00-05") == talkRevBefore &&
                  QuestCounter(a, "P00-05", "OBJ_P00_05_CLASS_CONFIRM") == talkCntBefore, "FT talk replay changed nothing");
            // Boss registration ring (178,0) r 11.
            var bossId = "ENT_MAN_BM_SPAWN_BM_05_QUEST";
            await a.ReadWorldAsync(CancellationToken.None);
            var bossRow = a.WorldV2 != null ? Array.Find(a.WorldV2.entities, t => t.entityId == bossId) : null;
            Check(bossRow != null && bossRow.targetable && bossRow.healthState == "ALIVE", "FT quest boss owner-targetable");
            await EnsureAlive(a, "FT P00-05 boss");
            var boss = await KillEntity(a, bossId);
            Check(boss.Accepted > 20 && boss.Died, "FT quest boss killed (" + boss.Accepted + " casts, " + boss.Reason + ")");
            await a.ReadWorldAsync(CancellationToken.None);
            var deadRow = a.WorldV2 != null ? Array.Find(a.WorldV2.entities, t => t.entityId == bossId) : null;
            Check(deadRow != null && !deadRow.targetable && deadRow.healthState == "DEAD", "FT boss stays dead");
            await RefreshQuests(a, "FT boss quests");
            Check(QuestCounter(a, "P00-05", "OBJ_P00_05_BOSS") == 1, "FT BOSS counter");
            var frag = await a.InteractAsync("ALPHA_OBJ_BM_FRAGMENT", CancellationToken.None);
            Check(frag.Success, "FT fragment interact: " + (frag.Code ?? "ok"));
            await RefreshQuests(a, "FT fragment quests");
            Check(QuestCounter(a, "P00-05", "OBJ_P00_05_FRAGMENT") == 1, "FT FRAGMENT counter");
            // Premature turn-in: CLASS_CONFIRM is still missing.
            var early = await a.TurnInQuestAsync("P00-05", "NPC_TA_VAN_KHANH", CancellationToken.None);
            await RefreshQuests(a, "FT premature turn-in quests");
            Check(!early.Success && QuestCounter(a, "P00-05", "OBJ_P00_05_CLASS_CONFIRM") == 0 &&
                  QuestState(a, "P00-05") == "ACTIVE", "FT P00-05 turn-in stopped early");
            Check(QuestState(a, "C1-01") == "LOCKED", "FT C1 still locked before finale");

            // ── Finale: class-confirm typed talk, turn-in, portal-positive ──
            await Approach(a, 188.0, 0.0);
            var confirm = await a.TalkAsync("NPC_CLASS_TRIAL", "DLG_P00_05_CLASS_CONFIRM", CancellationToken.None);
            Check(confirm.Success, "FT CLASS_CONFIRM talk: " + (confirm.Code ?? "ok"));
            Check(a.LastTalk != null && a.LastTalk.questId == "P00-05" && a.LastTalk.npcId == "NPC_CLASS_TRIAL" &&
                  a.LastTalk.nodeId == "DLG_P00_05_CLASS_CONFIRM" && a.LastTalk.credited &&
                  a.LastTalk.eventId != null && a.LastTalk.eventId.StartsWith("PQTALK_", StringComparison.Ordinal),
                "FT CLASS_CONFIRM typed receipt");
            Check((await a.ReadWorldAsync(CancellationToken.None)).Success && a.State == P1ConnectionState.Ready, "FT talk fresh world read");
            await RefreshQuests(a, "FT class-confirm quests");
            Check(QuestCounter(a, "P00-05", "OBJ_P00_05_CLASS_CONFIRM") == 1 &&
                  QuestState(a, "P00-05") == "READY_TO_TURN_IN", "FT class confirm credited");
            await Approach(a, turnInX, 0.0);
            var turn5 = await a.TurnInQuestAsync("P00-05", "NPC_TA_VAN_KHANH", CancellationToken.None);
            Check(turn5.Success && a.LastTurnIn != null && a.LastTurnIn.questState.state == "COMPLETED", "FT turn-in P00-05");
            await RefreshQuests(a, "FT finale quests");
            Check(QuestState(a, "P00-05") == "COMPLETED" && QuestState(a, "C1-01") == "LOCKED", "FT chapter unlocked, C1 still level-locked");

            // Portal-positive. The typed call goes first so its raw wire shape
            // is captured; the strict parser must never fabricate a success.
            await Approach(a, 348.0, 0.0);
            var portal = await a.PortalAsync(PortalBenMua, CancellationToken.None);
            string portalResponse = httpA.LastPortalResponse ?? "";
            Check(httpA.LastPortalStatus == 200 && !string.IsNullOrWhiteSpace(httpA.LastPortalBody), "FT portal transported");
            Check(portalResponse.Contains(PortalBenMua, StringComparison.Ordinal) &&
                  portalResponse.Contains("\"applied\":true", StringComparison.Ordinal) &&
                  portalResponse.Contains("\"replayed\":false", StringComparison.Ordinal) &&
                  portalResponse.Contains("P1PORTAL_", StringComparison.Ordinal), "FT portal raw receipt behavioral");
            bool contractShape = portalResponse.Contains("\"mapId\"", StringComparison.Ordinal);
            if (contractShape)
            {
                Check(portal.Success && a.LastPortal != null && a.LastPortal.mapId == "MAP_THANH_LAC" &&
                      Math.Abs(a.LastPortal.xWu - 8.0) < 0.5 && Math.Abs(a.LastPortal.yWu) < 0.5, "FT portal typed destination");
            }
            else
            {
                // The pinned server emits destinationMapId/... instead of the
                // contract's mapId/xWu/yWu, so the strict typed parser
                // correctly refuses to fabricate LastPortal. The behavioral
                // receipt above already proved the transition applied; the
                // contract shape stays UNVERIFIED and is reported, not hidden.
                Console.WriteLine("UNVERIFIED portal-positive contract shape: wire has no mapId/xWu/yWu; typed LastPortal null");
                Check(!portal.Success && a.LastPortal == null, "FT portal typed strict (no fabricated receipt)");
                Check(portalResponse.Contains("\"destinationMapId\":\"MAP_THANH_LAC\"", StringComparison.Ordinal) &&
                      Math.Abs(JsonDouble(portalResponse, "destinationXWu") - 8.0) < 0.5, "FT portal wire destination matches registry");
            }
            Check((await a.ReadWorldAsync(CancellationToken.None)).Success, "FT portal world read");
            Check(a.World.mapId == "MAP_THANH_LAC" && Math.Abs(a.World.self.x - 8.0) < 0.5 && Math.Abs(a.World.self.y) < 0.5, "FT portal arrival MAP_THANH_LAC (8,0)");
            var portalReplay = await RawPost(baseUrl, "/p1/world/portal", httpA.LastPortalBody, sessionId);
            var portalReplayBody = await portalReplay.Content.ReadAsStringAsync();
            Check((int)portalReplay.StatusCode == 200 && portalReplayBody.Contains("\"replayed\":true", StringComparison.Ordinal) &&
                  JsonLong(portalReplayBody, "revision") == JsonLong(portalResponse, "revision"), "FT portal replay stored receipt");
            // Fresh key from the wrong map: distance guard, nobody moves.
            await a.ReadWorldAsync(CancellationToken.None);
            double afterX = a.World.self.x, afterY = a.World.self.y;
            var freshReply = await RawPost(baseUrl, "/p1/world/portal", PortalEnvelope(character, PortalBenMua), sessionId);
            var freshBody = await freshReply.Content.ReadAsStringAsync();
            Check((int)freshReply.StatusCode == 422 && freshBody.Contains("\"out_of_range\"", StringComparison.Ordinal) &&
                  !freshBody.Contains("\"result\":{", StringComparison.Ordinal), "FT fresh-key portal refused");
            await a.ReadWorldAsync(CancellationToken.None);
            Check(a.World.self.x == afterX && a.World.self.y == afterY, "FT fresh-key portal moved nobody");
            await RefreshQuests(a, "FT final quests");
            Check(new[] { "P00-01", "P00-02", "P00-03", "P00-04", "P00-05" }.All(q => QuestState(a, q) == "COMPLETED") &&
                  QuestState(a, "C1-01") == "LOCKED", "FT all tutorial completed, C1 locked");
            // Per-character isolation: B never saw A's progress.
            if (b != null)
            {
                Check((await b.ReadQuestsAsync(CancellationToken.None)).Success, "FT B isolation quests read");
                Check(QuestCounter(b, "P00-02", "OBJ_P00_02_RIPPLES") == 0 &&
                      QuestCounter(b, "P00-02", "OBJ_P00_02_CARPLING") == 0, "FT B inherited none of A's P00-02");
                Check(QuestState(b, "P00-02") == "AVAILABLE" && QuestState(b, "P00-05") == "LOCKED", "FT B isolation states");
            }
        }

        // Routes pinned server does not map yet. 404/405 is recorded as
        // UNVERIFIED (never silently passed); any other answer fails the run.
        private static async Task CheckRouteProbes(P1Client c, string baseUrl)
        {
            string character = c.World.self.characterId;
            var consume = await RawPost(baseUrl, "/p1/inventory/consume", Envelope(character, "{}"), c.SessionId);
            var consumeBody = await consume.Content.ReadAsStringAsync();
            if ((int)consume.StatusCode == 404 || (int)consume.StatusCode == 405)
                Console.WriteLine("UNVERIFIED inventory consume: route unmapped (" + (int)consume.StatusCode + ")");
            else
                Check(false, "FT consume route should be unmapped, got " + (int)consume.StatusCode + ": " + consumeBody);

            // Raw probe (not the typed lane): the portal-positive leg above
            // can legitimately leave a pending uncertain mutation, which
            // blocks the typed MapViewed lane by design.
            var mappedReply = await RawPost(baseUrl, "/p1/quests/map-viewed",
                Envelope(character, "{\"questId\":\"P00-01\"}"), c.SessionId);
            if ((int)mappedReply.StatusCode == 404 || (int)mappedReply.StatusCode == 405)
                Console.WriteLine("UNVERIFIED quest map-viewed: route unmapped (" + (int)mappedReply.StatusCode + ")");
            else if ((int)mappedReply.StatusCode == 200)
                Console.WriteLine("UNVERIFIED quest map-viewed: interim acknowledged only, not frozen (QOD-28)");
            else
                Check(false, "FT map-viewed unexpected status " + (int)mappedReply.StatusCode);

            var escort = await RawGet(baseUrl, "/p1/quests/escort/current", c.SessionId);
            if ((int)escort.StatusCode == 404 || (int)escort.StatusCode == 405)
                Console.WriteLine("UNVERIFIED quest escort current: route unmapped (" + (int)escort.StatusCode + ")");
            else
                Check(false, "FT escort route should be unmapped, got " + (int)escort.StatusCode);
        }

        private static async Task CheckEncounter(ClientSession session)
        {
            var encounter = await session.ReadCurrentEncounterAsync();
            if (encounter.Outcome == EncounterReadOutcome.NotFound)
                Console.WriteLine("UNVERIFIED encounter HTTP: route absent/encounter not found (404 " + encounter.ErrorCode + ")");
            else if (encounter.Success)
                Check(true, "encounter current typed read");
            else
                throw new Exception("encounter read failed: " + encounter.Outcome + " " + encounter.ErrorCode);
        }

        private static async Task MainAsync(string baseUrl)
        {
            bool alpha = AlphaMode();
            using (var httpA = new Http(baseUrl))
            using (var httpB = new Http(baseUrl))
            using (var expB = new ExpiringTransport(httpB))
            using (var sessionA = new ClientSession(httpA, ownsTransport: true, useWorldV2: true,
                       requestTimeout: TimeSpan.FromSeconds(15), characterId: CharacterA,
                       profile: ProfileFor(alpha)))
            using (var sessionB = new ClientSession(expB, ownsTransport: true, useWorldV2: true,
                       requestTimeout: TimeSpan.FromSeconds(15), characterId: CharacterB,
                       profile: ProfileFor(alpha)))
            {
                // ---------- A: normal flow + lost response + fresh inventory ----------
                Check((await sessionA.ConnectAsync()).Success, "A connect");
                Check(sessionA.Adapter.ConnectionState == UIConnectionState.Ready, "A ready");
                Check(sessionA.Client.World.self.characterId == CharacterA, "A identity");

                // O5: the host profile describes this local deployment explicitly;
                // core routes are available, and MAP_VIEWED stays held until its
                // wire schema is approved (QOD-28).
                Check(sessionA.Availability.CanCall("quests"), "A availability quests");
                Check(sessionA.Availability.CanCall("world-v2"), "A availability world-v2");
                Check(!sessionA.Availability.CanCall("map-viewed"), "A availability map-viewed held");
                if (alpha)
                {
                    Check(sessionA.Availability.CanCall("encounter"), "A availability encounter");
                    Check(sessionA.Availability.CanCall("inventory-v2"), "A availability inventory-v2");
                    Check(sessionA.Availability.CanCall("death-return"), "A availability death-return");
                    Check(sessionA.Availability.CanCall("quest-talk"), "A availability quest-talk");
                    Check(sessionA.Availability.CanCall("portal"), "A availability portal");
                }
                else
                {
                    Check(sessionA.Availability.Get("encounter").State == ServiceAvailabilityState.Disabled,
                        "A availability encounter disabled");
                    Check(!sessionA.Availability.CanCall("inventory-v2"), "A availability inventory-v2 off");
                    Check(!sessionA.Availability.CanCall("death-return"), "A availability death-return off");
                    Check(!sessionA.Availability.CanCall("quest-talk"), "A availability quest-talk off");
                    Check(!sessionA.Availability.CanCall("portal"), "A availability portal off");
                    await CheckGatesOffNegatives(sessionA.Client);
                }

                // ---------- A: opening tutorial chain, server-authoritative only ----------
                Check((await sessionA.Client.ReadQuestsAsync(CancellationToken.None)).Success, "A tutorial quests read");
                var tutorial = TutorialProgress.FromServer(sessionA.Client.Quests);
                if (alpha)
                {
                    // The alpha overlay legitimately adds C1-01 to the catalog; the
                    // projection must still report the whole tutorial chain cleanly.
                    Check(tutorial.MissingQuestIds.Count == 0 && tutorial.Diagnostics.Count == 0,
                        "A tutorial chain authoritative in alpha catalog");
                    Check(tutorial.UnexpectedQuestIds.Count == 1 && tutorial.UnexpectedQuestIds[0] == "C1-01",
                        "A alpha catalog adds only C1-01");
                    // Gói 32 checkpoint: the level-11 C1 slice must stay LOCKED for
                    // this level-1 character; the alpha overlay only adds the record,
                    // it must not open the chapter quest.
                    var c1 = sessionA.Client.Quests.Where(q => q != null && q.questId == "C1-01").ToList();
                    Check(c1.Count == 1 && c1[0].state == "LOCKED", "A C1-01 low-level locked");
                }
                else
                {
                    Check(tutorial.IsAuthoritative, "A tutorial chain authoritative");
                }
                Check(tutorial.Steps.Count == 5 && tutorial.Steps[0].QuestId == "P00-01" &&
                      tutorial.Steps[4].QuestId == "P00-05", "A tutorial chain P00-01..05");
                Check(tutorial.Steps[0].IsAvailable && tutorial.Steps[0].StepId == "STEP_P00_01_PACKAGES",
                    "A P00-01 available packages step");
                Check(tutorial.Steps[0].Counter("OBJ_P00_01_PACKAGES") == 0, "A P00-01 counter starts at 0");
                Check(tutorial.Steps.Skip(1).All(s => s.IsLocked), "A P00-02..05 locked by source");
                Check(tutorial.NextActionable != null && tutorial.NextActionable.QuestId == "P00-01",
                    "A next actionable P00-01");
                Check(tutorial.FirstIncomplete != null && tutorial.FirstIncomplete.QuestId == "P00-01",
                    "A first incomplete P00-01");

                // The blocked quest must reject for its named activation fields, not
                // pretend a prerequisite was met and not leave a pending mutation.
                // In alpha the overlay unblocks P00-02, so this spawn-distance probe
                // is refused by range; the prerequisite itself is proven after turn-in.
                var blocked = await sessionA.Client.AcceptQuestAsync("P00-02", "NPC_TA_VAN_KHANH", CancellationToken.None);
                if (alpha)
                    Check(!blocked.Success && blocked.Code == "out_of_range", "A P00-02 far refusal");
                else
                    Check(!blocked.Success && blocked.Code == "prerequisite_not_met", "A P00-02 blocked by activation");
                Check(!sessionA.Client.HasPendingMutation, "A blocked accept clears pending");

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

                Check((await sessionA.Client.ReadQuestsAsync(CancellationToken.None)).Success, "A tutorial quests after turn-in");
                var tutorialAfter = TutorialProgress.FromServer(sessionA.Client.Quests);
                Check(tutorialAfter.Steps[0].IsCompleted, "A P00-01 completed");
                Check(tutorialAfter.Steps[0].Counter("OBJ_P00_01_PACKAGES") == 3, "A P00-01 counter 3");
                Check(tutorialAfter.FirstIncomplete != null && tutorialAfter.FirstIncomplete.QuestId == "P00-02",
                    "A first incomplete P00-02");
                Check(sessionA.Client.LastTurnIn != null && sessionA.Client.LastTurnIn.unlocks != null &&
                      sessionA.Client.LastTurnIn.unlocks.Contains("P00-02"), "A server unlock claim P00-02");
                if (alpha)
                {
                    // The alpha overlay makes the server-owned unlock observable: the
                    // fresh read must show P00-02 AVAILABLE, and accepting it is a real
                    // server transition rather than a client-side guess.
                    Check(tutorialAfter.Steps[1].IsAvailable, "A P00-02 available after server unlock");
                    Check(tutorialAfter.Steps.Skip(2).All(s => s.IsLocked), "A P00-03..05 still locked");
                    Check(tutorialAfter.NextActionable != null && tutorialAfter.NextActionable.QuestId == "P00-02",
                        "A next actionable P00-02 in alpha");
                    var acceptedAfterUnlock = await sessionA.Client.AcceptQuestAsync("P00-02", "NPC_TA_VAN_KHANH", CancellationToken.None);
                    Check(acceptedAfterUnlock.Success && !sessionA.Client.HasPendingMutation,
                        "A P00-02 accepted after server unlock: " + (acceptedAfterUnlock.Code ?? "ok"));
                    Check(sessionA.Client.Quests.Any(q => q != null && q.questId == "P00-02" && q.state == "ACTIVE"),
                        "A P00-02 active from server");
                }
                else
                {
                    Check(tutorialAfter.Steps.Skip(1).All(s => s.IsLocked), "A P00-02..05 still locked");
                    Check(tutorialAfter.NextActionable == null, "A no client-side unlock");
                    var blockedAfterUnlock = await sessionA.Client.AcceptQuestAsync("P00-02", "NPC_TA_VAN_KHANH", CancellationToken.None);
                    Check(!blockedAfterUnlock.Success && blockedAfterUnlock.Code == "prerequisite_not_met",
                        "A P00-02 still not activatable");
                    Check(!sessionA.Client.HasPendingMutation, "A blocked P00-02 clears pending");
                }

                var repeat = await dialogueA.TurnInQuestAsync("P00-01", "NPC_TA_VAN_KHANH", CancellationToken.None);
                Check(repeat.IsError && repeat.ErrorCode == "invalid_transition", "A repeat rejected");
                // Fresh read after reject, specifically not the cached inventory above.
                Check((await sessionA.Client.ReadInventoryAsync(CancellationToken.None)).Success, "A inv read after reject");
                Check(sessionA.Client.Inventory.currencies.Where(c => c.currencyId == "COIN").Sum(c => c.amount) == 20, "A no double grant");
                Check(sessionA.Client.Inventory.items.Count(i => i != null && i.templateId == ChestTemplate) == 1, "A no double chest");

                if (alpha)
                {
                    await CheckAlphaInventory(sessionA.Client, httpA, baseUrl);
                    await CheckAlphaDeathAlive(sessionA.Client);
                    await CheckAlphaPortal(sessionA.Client);
                }
                await CheckEncounter(sessionA);

                // ---------- B: isolation + cross-session replay ----------
                Check((await sessionB.ConnectAsync()).Success, "B connect");
                Check(sessionB.Client.World.self.characterId == CharacterB, "B identity");
                Check(sessionB.Client.World.self.characterId != sessionA.Client.World.self.characterId, "A/B different characters");
                Check((await sessionB.Client.ReadQuestsAsync(CancellationToken.None)).Success, "B read quests");
                Check(sessionB.Client.Quests.All(q => q == null || q.questId != "P00-01" || q.state != "COMPLETED"), "B quest not completed by A");

                // ---------- B: tutorial chain, two-owner isolation ----------
                Check((await sessionB.Client.ReadQuestsAsync(CancellationToken.None)).Success, "B tutorial quests read");
                var tutorialB = TutorialProgress.FromServer(sessionB.Client.Quests);
                if (alpha)
                {
                    Check(tutorialB.MissingQuestIds.Count == 0 && tutorialB.Diagnostics.Count == 0,
                        "B tutorial chain authoritative in alpha catalog");
                }
                else
                {
                    Check(tutorialB.IsAuthoritative, "B tutorial chain authoritative");
                }
                Check(tutorialB.Steps.Count == 5 && tutorialB.Steps[0].QuestId == "P00-01",
                    "B tutorial chain P00-01..05");
                Check(tutorialB.Steps[0].IsAvailable, "B P00-01 available");
                Check(tutorialB.Steps.Skip(1).All(s => s.IsLocked), "B P00-02..05 locked by source");
                Check(tutorialB.NextActionable != null && tutorialB.NextActionable.QuestId == "P00-01",
                    "B next actionable P00-01");
                // B cannot activate P00-02 even though A's turn-in unlocked it on server.
                // Gates-off names the activation block; alpha refuses the spawn-distance
                // probe by range before prerequisites. Both are definite refusals.
                var bBlocked = await sessionB.Client.AcceptQuestAsync("P00-02", "NPC_TA_VAN_KHANH", CancellationToken.None);
                if (alpha)
                    Check(!bBlocked.Success && bBlocked.Code == "out_of_range", "B P00-02 far refusal");
                else
                    Check(!bBlocked.Success && bBlocked.Code == "prerequisite_not_met", "B P00-02 blocked by activation");
                Check(!sessionB.Client.HasPendingMutation, "B blocked accept clears pending");
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

                // ---------- B: TALK checkpoint while P00-01 is still AVAILABLE ----------
                if (alpha) await CheckAlphaTalk(sessionB.Client, httpB, baseUrl);

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

                if (alpha)
                {
                    await CheckAlphaFullTutorial(sessionA.Client, httpA, baseUrl, sessionB.Client);
                    await CheckRouteProbes(sessionA.Client, baseUrl);
                }

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
