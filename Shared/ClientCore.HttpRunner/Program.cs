using System;
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
            public bool LoseTurnInResponseOnce;
            public Http(string url) { client = new HttpClient { BaseAddress = new Uri(url) }; }
            public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
            {
                if (req.Path == "/p1/quests/turnin" && req.Body != null) LastTurnInBody = req.Body;
                if (req.Path == "/p1/inventory/v2/equip" && req.Body != null) LastEquipBody = req.Body;
                if (req.Path == "/p1/quests/talk" && req.Body != null) LastTalkBody = req.Body;
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
        // portal_locked without the chapter grant. A positive transition is not
        // claimed here because P00-05 cannot be completed at this pin.
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
