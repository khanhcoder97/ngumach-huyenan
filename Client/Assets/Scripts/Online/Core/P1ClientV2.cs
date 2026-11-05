using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;

namespace NguMach.Client.P1
{
    public sealed partial class P1Client
    {
        public P1WorldV2 WorldV2 { get; private set; }
        public P1InventorySnapshotV2 InventoryV2 { get; private set; }
        public P1DeathReturnResultV1 LastDeathReturn { get; private set; }
        public long? NextReturnAllowedAtTick { get; private set; }
        public P1TurnInResult LastTurnIn { get; private set; }
        public long EventCursor { get; private set; }
        public int EventResyncCount { get; private set; }
        private readonly Queue<P1EventV2> presentationEvents = new Queue<P1EventV2>();
        public P1EventV2[] DrainPresentationEvents()
        { lock (presentationEvents) { var result = presentationEvents.ToArray(); presentationEvents.Clear(); return result; } }
        private void ResetV2()
        {
            WorldV2 = null; InventoryV2 = null; LastDeathReturn = null; NextReturnAllowedAtTick = null;
            LastTurnIn = null; EventCursor = 0; EventResyncCount = 0;
            lock (presentationEvents) presentationEvents.Clear();
        }
        private static bool Timestamp(string value)
        { return DateTimeOffset.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out _); }
        private static bool OneOf(string value, params string[] allowed) { return Array.IndexOf(allowed, value) >= 0; }

        // DEC-ALPHA-INTERACT-IDS-20261105: the six published alpha interact
        // targets kept beside the canonical ENT_ rule. The retired
        // ALPHA_NPC_RESCUE* names are NOT canonical and are rejected.
        private static readonly string[] AlphaInteractIds =
        {
            "ALPHA_OBJ_BM_FRAGMENT",
            "ALPHA_OBJ_BM_RIPPLE_01",
            "ALPHA_OBJ_BM_RIPPLE_02",
            "ALPHA_OBJ_BM_RIPPLE_03",
            "ALPHA_OBJ_BM_VILLAGER_01",
            "ALPHA_OBJ_BM_VILLAGER_02"
        };

        internal static bool IsValidInteractTarget(string target)
        {
            if (string.IsNullOrWhiteSpace(target)) return false;
            // "ENT_" alone is not an entity id; require a non-empty suffix.
            if (target.Length > 4 && target.StartsWith("ENT_", StringComparison.Ordinal)) return true;
            return Array.IndexOf(AlphaInteractIds, target) >= 0;
        }

        private async Task<P1Result> ReadWorldV2(CancellationToken ct)
        {
            var reply = await Send(Get("/p1/v2/world/" + SessionId), ct);
            var r = Parse<P1WorldV2>(reply, 2);
            if (IsExpired(r)) return Expire();
            if (!Good(reply, r) || r.sessionId != SessionId || !ValidWorldV2(r.result))
            {
                State = pending != null ? P1ConnectionState.UncertainMutation : P1ConnectionState.NeedsResync;
                return Fail((reply.StatusCode == 404 || reply.StatusCode == 405) && r == null ? "feature_unavailable" : Error(reply, r), reply.CorrelationId);
            }
            var w = r.result;
            if (WorldV2 == null || w.revision > WorldV2.revision || w.revision == WorldV2.revision && w.serverTick >= WorldV2.serverTick)
            {
                // A snapshot is the only source of displayed HP and position. Event amounts are never subtracted locally.
                if (WorldV2 != null && (w.mapInstanceId != WorldV2.mapInstanceId || w.floorId != WorldV2.floorId))
                    lock (presentationEvents) presentationEvents.Clear();
                WorldV2 = w;
                var entities = new P1Entity[w.entities.Length];
                for (int i = 0; i < entities.Length; i++)
                {
                    var e = w.entities[i];
                    entities[i] = new P1Entity { entityId = e.entityId, kind = e.kind, state = e.state, x = e.x, y = e.y,
                        hp = e.hp, maxHp = e.maxHp, targetable = e.targetable, healthState = e.healthState, availability = e.availability };
                }
                World = new P1World { mapId = w.mapId, revision = w.revision, serverTick = w.serverTick,
                    serverTimeUtc = w.serverTimeUtc, self = w.self, entities = entities };
            }
            if (pending != null) { State = P1ConnectionState.UncertainMutation; return P1Result.Ok(); }
            return Ready();
        }
        private bool ValidWorldV2(P1WorldV2 w)
        {
            if (w == null || w.schemaVersion != 2 || w.audience == null || w.entities == null || w.self == null ||
                w.self.characterId != World.self.characterId || string.IsNullOrWhiteSpace(w.mapInstanceId) ||
                string.IsNullOrWhiteSpace(w.floorId) || string.IsNullOrWhiteSpace(w.phase) || !Timestamp(w.serverTimeUtc) ||
                !P1Wire.Finite(w.audience.aoiEnterWu) || !P1Wire.Finite(w.audience.aoiLeaveWu) ||
                w.audience.aoiEnterWu <= 0 || w.audience.aoiLeaveWu < w.audience.aoiEnterWu) return false;
            if (!P1Wire.Valid(new P1World { mapId = w.mapId, revision = w.revision, serverTick = w.serverTick,
                self = w.self, entities = new P1Entity[0] })) return false;
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var e in w.entities)
            {
                if (e == null || string.IsNullOrWhiteSpace(e.entityId) || !ids.Add(e.entityId) ||
                    e.mapInstanceId != w.mapInstanceId || e.floorId != w.floorId || e.phase != w.phase ||
                    !P1Wire.Finite(e.x) || !P1Wire.Finite(e.y) || e.revision < 0 || e.lifeId < 0 || e.maxHp < 0 || e.hp < 0 || e.hp > e.maxHp ||
                    !OneOf(e.kind, "MOB", "BOSS", "NPC", "GATHER_NODE", "INTERACTABLE") ||
                    !OneOf(e.state, "IDLE", "AGGRO", "CHASE", "ATTACK", "RETURN", "DEAD", "ACTIVE", "AVAILABLE", "DEPLETED") ||
                    !OneOf(e.healthState, "ALIVE", "DEAD", "INVULNERABLE", "BLOCKED") ||
                    e.availability != null && !OneOf(e.availability, "AVAILABLE", "COOLDOWN")) return false;
                bool hostile = e.kind == "MOB" || e.kind == "BOSS";
                if (e.targetable && (!hostile || e.healthState != "ALIVE" || e.hp == 0)) return false;
                if (!hostile && e.healthState != "INVULNERABLE") return false;
                if (e.healthState == "DEAD" && (e.hp != 0 || e.targetable)) return false;
            }
            return true;
        }
        public Task<P1Result> BasicAttackAsync(string target, double aimX, double aimY, CancellationToken ct)
        { return UseWorldV2 ? CombatV2Async("BASIC_ATTACK", null, target, aimX, aimY, ct) : Task.FromResult(Fail("feature_unavailable")); }
        private async Task<P1Result> CombatV2Async(string kind, string skill, string target, double aimX, double aimY, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null || WorldV2 == null) return Fail("resync_required");
                if (kind == "SKILL" && !OneOf(skill, "SK-MK-01", "SK-MK-02", "SK-MK-03")) return Fail("unsupported_skill");
                if (!P1Wire.Finite(aimX) || !P1Wire.Finite(aimY) || Math.Abs(aimX) > 1 || Math.Abs(aimY) > 1) return Fail("invalid_input");
                if (target != null)
                {
                    P1EntityV2 entity = Array.Find(WorldV2.entities, e => e.entityId == target);
                    if (entity == null || !entity.targetable) return Fail("invalid_target");
                }
                if ((kind == "BASIC_ATTACK" || skill != "SK-MK-01") && string.IsNullOrWhiteSpace(target)) return Fail("target_required");
                pending = Command("/p1/v2/combat", new P1CastV2 { actionKind = kind, skillId = skill, targetId = target,
                    inputSequence = NextSequence(), aimX = aimX, aimY = aimY,
                    clientTimeUtc = utcNow().UtcDateTime.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture) }, 2);
                pendingKind = PendingKind.CombatV2;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }
        private async Task<P1Result> ApplyCombatV2(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1CastResultV2>(reply, 2);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r)) return RejectPending(Error(reply, r));
            var sent = P1Wire.Decode<P1Envelope<P1CastV2>>(pending.Body).payload; var result = r.result;
            if (r.sessionId != SessionId || r.requestId != pending.CorrelationId || result == null || !P1Wire.Hex32(result.castId) || result.actionKind != sent.actionKind ||
                result.skillId != sent.skillId || result.mp < 0 || result.mpCost < 0 ||
                !Timestamp(result.cooldownEndUtc) || result.acceptedInputSequence != sent.inputSequence || result.events == null || result.events.Length == 0 ||
                !ValidEvents(result.events, -1)) return Uncertain(reply.CorrelationId);
            foreach (var e in result.events) if (e.castId != result.castId || e.actorId != World.self.characterId) return Uncertain(reply.CorrelationId);
            cooldowns[sent.actionKind == "BASIC_ATTACK" ? "BASIC_ATTACK" : sent.skillId] = result.cooldownEndUtc;
            sequence = Math.Max(sequence, result.acceptedInputSequence);
            foreach (var e in result.events) Present(e);
            pending = null; State = P1ConnectionState.NeedsResync;
            return await ReadWorld(ct);
        }
        public async Task<P1Result> ReadEventsAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (!UseWorldV2 || SessionId == null || WorldV2 == null) return Fail("feature_unavailable");
                var reply = await Send(Get("/p1/v2/events/" + SessionId + "?cursor=" + EventCursor.ToString(CultureInfo.InvariantCulture) + "&max=100"), ct);
                var r = Parse<P1EventPageV2>(reply, 2);
                if (IsExpired(r)) return Expire();
                if (!Good(reply, r) || r.sessionId != SessionId || r.result == null) return Fail(Error(reply, r), reply.CorrelationId);
                var page = r.result;
                if (page.schemaVersion != 2 || page.sessionId != SessionId || page.nextCursor < 0 || page.events == null) return Fail("invalid_response");
                if (page.resyncRequired)
                {
                    if (page.events.Length != 0 || !OneOf(page.resyncReason, "CURSOR_TOO_OLD", "BUFFER_OVERFLOW")) return Fail("invalid_response");
                    var sync = await ReadWorld(ct); if (!sync.Success) return sync;
                    // Reconcile silently. Never replay expired hit/audio animations after a gap.
                    EventCursor = page.nextCursor; EventResyncCount++;
                    lock (presentationEvents) presentationEvents.Clear();
                    seenEvents.Clear(); seenEventOrder.Clear();
                    return P1Result.Ok();
                }
                if (page.resyncReason != null || page.nextCursor < EventCursor || !ValidEvents(page.events, EventCursor) ||
                    page.events.Length > 100 || (page.events.Length > 0 && page.nextCursor != page.events[page.events.Length - 1].cursor)) return Fail("invalid_response");
                foreach (var e in page.events) Present(e);
                EventCursor = page.nextCursor;
                return P1Result.Ok();
            }
            finally { lane.Release(); }
        }
        private static bool ValidEvents(P1EventV2[] events, long after)
        {
            long cursor = after; var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var e in events)
            {
                if (e == null || !P1Wire.Hex32(e.eventId) || !P1Wire.Hex32(e.castId) || !ids.Add(e.eventId) || e.cursor <= cursor || e.cursor < 1 ||
                    string.IsNullOrWhiteSpace(e.actorId) || string.IsNullOrWhiteSpace(e.mapInstanceId) || string.IsNullOrWhiteSpace(e.floorId) ||
                    e.sourceRevision < 0 || e.serverTick < 0 || e.targetRevision < 0 || e.targetLifeId < 0 || e.hitIndex < 0 || !Timestamp(e.emittedAtUtc) ||
                    !OneOf(e.type, "CAST_START", "COUNTER_CONFIRMED", "IMPACT", "MISS", "CANCEL", "END", "DEATH")) return false;
                var hit = e.result;
                if (hit != null && (hit.amount < 0 || hit.absorbed < 0 || hit.hpDamage < 0 ||
                    (long)hit.absorbed + hit.hpDamage > hit.amount || (!hit.hit || hit.immune) && hit.amount != 0)) return false;
                if (e.type == "IMPACT" && (hit == null || string.IsNullOrWhiteSpace(e.targetId) || !e.targetLifeId.HasValue || !e.hitIndex.HasValue || !e.targetRevision.HasValue)) return false;
                cursor = e.cursor;
            }
            return true;
        }
        private void Present(P1EventV2 e)
        {
            if (e.cursor <= EventCursor || !seenEvents.Add(e.eventId)) return;
            seenEventOrder.Enqueue(e.eventId);
            if (seenEventOrder.Count > 512) seenEvents.Remove(seenEventOrder.Dequeue());
            if (WorldV2 == null || e.mapInstanceId != WorldV2.mapInstanceId || e.floorId != WorldV2.floorId) return;
            lock (presentationEvents) { if (presentationEvents.Count >= 256) presentationEvents.Dequeue(); presentationEvents.Enqueue(e); }
        }
        public async Task<P1Result> InteractAsync(string target, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (!IsValidInteractTarget(target)) return Fail("invalid_target");
                pending = Command("/p1/world/interact", new P1Interact { targetId = target }); pendingKind = PendingKind.Interact;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }
        private async Task<P1Result> ApplyInteraction(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1InteractResult>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r)) return RejectPending(Error(reply, r));
            var result = r.result;
            if (r.sessionId != SessionId || r.requestId != pending.CorrelationId || result == null || !P1Wire.Hex32(result.interactionId) ||
                result.targetId != P1Wire.Decode<P1Envelope<P1Interact>>(pending.Body).payload.targetId ||
                string.IsNullOrWhiteSpace(result.recordId) || !OneOf(result.kind, "INTERACTABLE", "GATHER_NODE") ||
                !OneOf(result.outcome, "collected", "gathered") || !OneOf(result.targetState, "AVAILABLE", "DEPLETED") ||
                !Timestamp(result.claimedAtUtc) || result.questUpdates == null) return Uncertain(reply.CorrelationId);
            foreach (var q in result.questUpdates) if (!ValidQuest(q)) return Uncertain(reply.CorrelationId);
            foreach (var q in result.questUpdates) ApplyQuest(q);
            pending = null; State = P1ConnectionState.NeedsResync;
            return await ReadWorld(ct);
        }
        public async Task<P1Result> TurnInQuestAsync(string quest, string npc, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (string.IsNullOrWhiteSpace(quest) || string.IsNullOrWhiteSpace(npc)) return Fail("invalid_input");
                pending = Command("/p1/quests/turnin", new P1QuestAccept { questId = quest, npcId = npc }); pendingKind = PendingKind.TurnIn;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }
        private async Task<P1Result> ApplyTurnIn(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1TurnInResult>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r)) return RejectPending(Error(reply, r));
            var receipt = r.result;
            if (r.sessionId != SessionId || r.requestId != pending.CorrelationId || receipt == null || !ValidQuest(receipt.questState) || receipt.questState.state != "COMPLETED" ||
                receipt.questState.questId != P1Wire.Decode<P1Envelope<P1QuestAccept>>(pending.Body).payload.questId ||
                receipt.rewards == null || receipt.rewards.currency == null || receipt.rewards.items == null || receipt.rewards.xp == null ||
                string.IsNullOrWhiteSpace(receipt.rewards.xp.xpRule) || receipt.unlocks == null) return Uncertain(reply.CorrelationId);
            foreach (var c in receipt.rewards.currency) if (c == null || string.IsNullOrWhiteSpace(c.currencyId) || c.amount < 0) return Uncertain(reply.CorrelationId);
            foreach (var item in receipt.rewards.items) if (item == null || string.IsNullOrWhiteSpace(item.templateId) || item.stack < 1 ||
                !OneOf(item.location, "BAG", "EQUIPPED", "BANK")) return Uncertain(reply.CorrelationId);
            ApplyQuest(receipt.questState); LastTurnIn = receipt;
            pending = null; State = P1ConnectionState.NeedsResync;
            // A grant receipt is not an inventory snapshot; never synthesize item instances or add its money locally.
            var sync = await ReadWorld(ct);
            if (!sync.Success) return SessionId == null ? sync : Fail("reward_refresh_pending", sync.CorrelationId);
            sync = await ReadInventoryUnlocked(ct);
            return !sync.Success && SessionId != null ? Fail("reward_refresh_pending", sync.CorrelationId) : sync;
        }
        private async Task<P1Result> ReadInventoryUnlocked(CancellationToken ct)
        {
            var reply = await Send(Get("/p1/inventory/" + SessionId), ct); var r = Parse<P1Inventory>(reply);
            if (IsExpired(r)) return Expire();
            if (!Good(reply, r) || r.sessionId != SessionId || !ValidInventory(r.result))
            { State = pending != null ? P1ConnectionState.UncertainMutation : P1ConnectionState.NeedsResync; return Fail(Error(reply, r), reply.CorrelationId); }
            if (Inventory == null || r.result.inventoryRevision >= Inventory.inventoryRevision) Inventory = r.result;
            return pending != null ? P1Result.Ok() : Ready();
        }
        // ── Death-return (DEC-DEATH-RETURN-20261105, frozen schema at 4b59b08) ──
        public async Task<P1Result> ReturnFromDeathAsync(CancellationToken ct, string expectedSessionId = null)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                pending = Command("/p1/actor/death-return", new P1DeathReturnIntent());
                pendingKind = PendingKind.DeathReturn;
                return await SubmitPending(ct, expectedSessionId);
            }
            finally { lane.Release(); }
        }

        // ── Quest talk (TALK, gate P1:QuestTalk:Enabled + AlphaProfile) ──
        public async Task<P1Result> TalkAsync(string npcId, string nodeId, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (string.IsNullOrWhiteSpace(npcId) || string.IsNullOrWhiteSpace(nodeId)) return Fail("invalid_input");
                pending = Command("/p1/quests/talk", new P1QuestTalkIntent { npcId = npcId, nodeId = nodeId });
                pendingKind = PendingKind.Talk;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }

        // ── World portal (gate P1:Portal:Enabled + AlphaProfile) ──
        public async Task<P1Result> PortalAsync(string portalId, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (string.IsNullOrWhiteSpace(portalId)) return Fail("invalid_input");
                pending = Command("/p1/world/portal", new P1WorldPortalIntent { portalId = portalId });
                pendingKind = PendingKind.Portal;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }

        // ── Quest map-viewed (gate private-alpha) ──
        public async Task<P1Result> MapViewedAsync(string questId, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (string.IsNullOrWhiteSpace(questId)) return Fail("invalid_input");
                pending = Command("/p1/quests/map-viewed", new P1QuestMapViewedIntent { questId = questId });
                pendingKind = PendingKind.MapViewed;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }

        private async Task<P1Result> ApplyDeathReturn(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1DeathReturnResultV1>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            // The two-gate mapping normally makes this a 404; the schema still
            // names 503 death_return_disabled so a consumer never sees a mystery.
            if (r != null && r.error != null && r.error.code == "death_return_disabled")
                return RejectPending("death_return_disabled");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (r == null || r.requestId != pending.CorrelationId) return Uncertain(reply.CorrelationId);

            if (!Good(reply, r))
            {
                if (r.error != null && r.error.nextReturnAllowedAtTick.HasValue)
                    NextReturnAllowedAtTick = r.error.nextReturnAllowedAtTick;
                return RejectPending(Error(reply, r));
            }

            var result = r.result;
            if (r.sessionId != SessionId || !ValidDeathReturn(result)) return Uncertain(reply.CorrelationId);

            // The receipt is authoritative for what the server committed; a
            // replay repeats historical HP/anchor, so never apply it as current
            // world state. Fresh-read the actor/world instead.
            pending = null;
            LastDeathReturn = result;
            NextReturnAllowedAtTick = result.nextReturnAllowedAtTick;
            State = P1ConnectionState.NeedsResync;
            var sync = await ReadWorld(ct);
            if (sync.Success) return P1Result.Ok();
            return SessionId == null ? sync : Fail("death_return_refresh_pending", sync.CorrelationId);
        }

        private static bool ValidDeathReturn(P1DeathReturnResultV1 r)
        {
            if (r == null || (r.applied == r.replayed) || string.IsNullOrEmpty(r.mapId) ||
                r.mapId.Length <= 4 || !r.mapId.StartsWith("MAP_", StringComparison.Ordinal) ||
                !ValidUpperToken(r.mapId.Substring(4), false) ||
                !P1Wire.Finite(r.xWu) || !P1Wire.Finite(r.yWu) ||
                r.maxHp < 1 || r.hp < 1 || r.hp > r.maxHp ||
                r.maxMp < 0 || r.mp < 0 || r.mp > r.maxMp ||
                r.serverTick < 0 || r.revision < 0 || r.nextReturnAllowedAtTick < 0) return false;
            if (r.cleared == null || r.cleared.inflightCasts < 0 || r.cleared.reservedCounters < 0) return false;
            if (r.penalties == null || r.penalties.xp != 0 || r.penalties.currency != 0 || r.penalties.durability != 0)
                return false;
            return true;
        }

        private static bool MissingRoute<T>(P1HttpReply h, P1Response<T> r)
        { return (h.StatusCode == 404 || h.StatusCode == 405) && r == null; }
        private P1Result RejectPending(string reason)
        { pending = null; State = P1ConnectionState.Ready; return Fail(reason); }

        private async Task<P1Result> ApplyTalk(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1QuestTalkResult>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r) || r.sessionId != SessionId || r.requestId != pending.CorrelationId ||
                r.result == null || string.IsNullOrWhiteSpace(r.result.questId)) return Uncertain(reply.CorrelationId);
            pending = null; State = P1ConnectionState.NeedsResync;
            return P1Result.Ok();
        }

        private async Task<P1Result> ApplyPortal(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1WorldPortalResult>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r) || r.sessionId != SessionId || r.requestId != pending.CorrelationId ||
                r.result == null || string.IsNullOrWhiteSpace(r.result.portalId)) return Uncertain(reply.CorrelationId);
            pending = null; State = P1ConnectionState.NeedsResync;
            return P1Result.Ok();
        }

        private async Task<P1Result> ApplyMapViewed(P1HttpReply reply, CancellationToken ct)
        {
            var r = Parse<P1QuestMapViewedResult>(reply);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (!Good(reply, r) || r.sessionId != SessionId || r.requestId != pending.CorrelationId ||
                r.result == null || string.IsNullOrWhiteSpace(r.result.questId)) return Uncertain(reply.CorrelationId);
            pending = null; State = P1ConnectionState.NeedsResync;
            return P1Result.Ok();
        }

        // ── Inventory v2 (Qoder 77bc3a6: twelve closed slots beside frozen v1) ──
        private static readonly string[] InventoryV2SlotOrder =
        {
            "HAT", "CHEST", "LEGS", "WEAPON", "GLOVES", "BOOTS",
            "NECK", "RING_L", "RING_R", "PENDANT", "CLOAK", "SEAL"
        };
        private const string InventoryV2SlotSpec = "V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT";

        public async Task<P1Result> ReadInventoryV2Async(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (SessionId == null) return Fail("not_connected");
                var reply = await Send(Get("/p1/inventory/v2/" + SessionId), ct);
                var r = Parse<P1InventorySnapshotV2>(reply, 2);
                if (IsExpired(r)) return Expire();
                if (MissingRoute(reply, r)) return Fail("feature_unavailable");
                if (!Good(reply, r) || r.sessionId != SessionId || !ValidInventoryV2(r.result))
                {
                    State = pending != null ? P1ConnectionState.UncertainMutation : P1ConnectionState.NeedsResync;
                    return Fail(Error(reply, r), reply.CorrelationId);
                }
                if (InventoryV2 == null || r.result.inventoryRevision >= InventoryV2.inventoryRevision)
                    InventoryV2 = r.result;
                LastError = null;
                return P1Result.Ok();
            }
            finally { lane.Release(); }
        }

        public async Task<P1Result> EquipV2Async(string itemInstanceId, long expectedRevision, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (!ValidInstanceIdV2(itemInstanceId) || expectedRevision < 1) return Fail("invalid_input");
                pending = Command("/p1/inventory/v2/equip",
                    new P1EquipV2 { itemInstanceId = itemInstanceId, expectedRevision = expectedRevision }, 2);
                pendingKind = PendingKind.InventoryV2;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }

        public async Task<P1Result> UnequipV2Async(string slotId, long expectedRevision, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (Array.IndexOf(InventoryV2SlotOrder, slotId) < 0 || expectedRevision < 1) return Fail("invalid_input");
                pending = Command("/p1/inventory/v2/unequip",
                    new P1UnequipV2 { slotId = slotId, expectedRevision = expectedRevision }, 2);
                pendingKind = PendingKind.InventoryV2;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }

        private async Task<P1Result> ApplyInventoryV2(P1HttpReply reply)
        {
            var r = Parse<P1InventorySnapshotV2>(reply, 2);
            if (IsExpired(r)) return Expire();
            if (MissingRoute(reply, r)) return RejectPending("feature_unavailable");
            if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
            if (r == null || r.requestId != pending.CorrelationId) return Uncertain(reply.CorrelationId);
            if (r.result != null && !ValidInventoryV2(r.result)) return Uncertain(reply.CorrelationId);

            if (!Good(reply, r))
            {
                // A rejection may carry the current authoritative snapshot
                // (revision_conflict / slot_occupied). Adopt it but never retry
                // silently: the definite error reaches the UI.
                if (r.result != null && (InventoryV2 == null || r.result.inventoryRevision >= InventoryV2.inventoryRevision))
                    InventoryV2 = r.result;
                return RejectPending(Error(reply, r));
            }

            long expected;
            if (pending.Path.EndsWith("/equip", StringComparison.Ordinal))
                expected = P1Wire.Decode<P1Envelope<P1EquipV2>>(pending.Body).payload.expectedRevision;
            else
                expected = P1Wire.Decode<P1Envelope<P1UnequipV2>>(pending.Body).payload.expectedRevision;

            if (r.sessionId != SessionId || r.result == null ||
                r.result.inventoryRevision <= expected) return Uncertain(reply.CorrelationId);
            InventoryV2 = r.result;
            pending = null;
            LastError = null;
            return Ready();
        }

        private static bool ValidInventoryV2(P1InventorySnapshotV2 inv)
        {
            if (inv == null || inv.schemaVersion != 2 || inv.slotSpec != InventoryV2SlotSpec ||
                inv.inventoryRevision < 0 || inv.bagSlots != 100 || inv.slots == null || inv.slots.Length != 12 ||
                inv.bag == null || inv.unsupported == null || inv.currencies == null) return false;

            var ids = new HashSet<string>(StringComparer.Ordinal);
            for (int i = 0; i < InventoryV2SlotOrder.Length; i++)
            {
                var slot = inv.slots[i];
                if (slot == null || slot.slotId != InventoryV2SlotOrder[i]) return false;
                if (slot.item == null) continue;
                if (!ValidItemV2(slot.item) || slot.item.location != "EQUIPPED" || slot.item.slotId != slot.slotId) return false;
                if (!ids.Add(slot.item.instanceId)) return false;
            }
            foreach (var item in inv.bag)
            {
                if (!ValidItemV2(item) || !ids.Add(item.instanceId)) return false;
            }
            foreach (var unsupported in inv.unsupported)
            {
                if (unsupported == null || !ValidInstanceIdV2(unsupported.instanceId) ||
                    !ValidTemplateIdV2(unsupported.templateId) || unsupported.reason != "UNMAPPED_SLOT" ||
                    (unsupported.sourceSlot != null && unsupported.sourceSlot.Length == 0) ||
                    !ids.Add(unsupported.instanceId)) return false;
            }
            var currencies = new HashSet<string>(StringComparer.Ordinal);
            foreach (var currency in inv.currencies)
                if (currency == null || currency.amount < 0 || !ValidUpperToken(currency.currencyId, false) ||
                    !currencies.Add(currency.currencyId)) return false;
            return true;
        }

        private static bool ValidItemV2(P1ItemV2 item)
        {
            return item != null && ValidInstanceIdV2(item.instanceId) && ValidTemplateIdV2(item.templateId) &&
                   item.stack >= 1 && OneOf(item.location, "BAG", "EQUIPPED", "BANK") &&
                   (item.slotId == null || Array.IndexOf(InventoryV2SlotOrder, item.slotId) >= 0) &&
                   item.durability >= 0 && item.version >= 1;
        }

        private static bool ValidInstanceIdV2(string value)
        {
            return value != null && value.Length > 4 && value.StartsWith("ITM_", StringComparison.Ordinal) &&
                   ValidUpperToken(value, false);
        }

        // ^[A-Z0-9_]+(?:-[A-Z0-9_]+)*$ — v2 templateId accepts underscores (catalog correction).
        private static bool ValidTemplateIdV2(string value)
        {
            if (string.IsNullOrEmpty(value)) return false;
            foreach (var part in value.Split('-'))
                if (!ValidUpperToken(part, false)) return false;
            return true;
        }

        private static bool ValidUpperToken(string value, bool allowHyphen)
        {
            if (string.IsNullOrEmpty(value)) return false;
            foreach (char c in value)
            {
                bool ok = (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c == '_' || (allowHyphen && c == '-');
                if (!ok) return false;
            }
            return true;
        }
    }
}
