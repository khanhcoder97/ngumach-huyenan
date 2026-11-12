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
        public P1TurnInResult LastTurnIn { get; private set; }
        public long EventCursor { get; private set; }
        public int EventResyncCount { get; private set; }
        private readonly Queue<P1EventV2> presentationEvents = new Queue<P1EventV2>();
        public P1EventV2[] DrainPresentationEvents()
        { lock (presentationEvents) { var result = presentationEvents.ToArray(); presentationEvents.Clear(); return result; } }
        private void ResetV2()
        {
            WorldV2 = null; LastTurnIn = null; EventCursor = 0; EventResyncCount = 0;
            lock (presentationEvents) presentationEvents.Clear();
        }
        private static bool Timestamp(string value)
        { return DateTimeOffset.TryParse(value, CultureInfo.InvariantCulture, DateTimeStyles.RoundtripKind, out _); }
        private static bool OneOf(string value, params string[] allowed) { return Array.IndexOf(allowed, value) >= 0; }

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
                if (string.IsNullOrWhiteSpace(target) || !target.StartsWith("ENT_", StringComparison.Ordinal)) return Fail("invalid_target");
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
        private static bool MissingRoute<T>(P1HttpReply h, P1Response<T> r)
        { return (h.StatusCode == 404 || h.StatusCode == 405) && r == null; }
        private P1Result RejectPending(string reason)
        { pending = null; State = P1ConnectionState.Ready; return Fail(reason); }
    }
}
