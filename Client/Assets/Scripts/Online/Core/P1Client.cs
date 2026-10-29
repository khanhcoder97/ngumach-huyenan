using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;

namespace NguMach.Client.P1
{
    public interface IP1Transport
    {
        Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation);
    }

    // One lane for commands and reads. No prediction, fake grants or local cooldown commits.
    public sealed class P1Client
    {
        private readonly IP1Transport transport;
        private readonly SemaphoreSlim lane = new SemaphoreSlim(1, 1);
        private readonly Func<DateTimeOffset> utcNow;
        private int sequence;
        private P1Request pending;
        private bool pendingCombat;
        private readonly HashSet<string> seenEvents = new HashSet<string>(StringComparer.Ordinal);
        private readonly Queue<string> seenEventOrder = new Queue<string>();
        private readonly Dictionary<string, string> cooldowns = new Dictionary<string, string>();

        public P1ConnectionState State { get; private set; } = P1ConnectionState.Disconnected;
        public string SessionId { get; private set; }
        public P1World World { get; private set; }
        public P1Quest[] Quests { get; private set; } = new P1Quest[0];
        public P1Inventory Inventory { get; private set; }
        public P1CombatEvent LastCombatEvent { get; private set; }
        public string LastError { get; private set; }
        public string LastCorrelationId { get; private set; }
        public bool HasPendingMutation { get { return pending != null; } }
        public IReadOnlyDictionary<string, string> CooldownEndsAtUtc { get { return cooldowns; } }
        public P1Client(IP1Transport transport, Func<DateTimeOffset> clock = null)
        { this.transport = transport ?? throw new ArgumentNullException(nameof(transport)); utcNow = clock ?? (() => DateTimeOffset.UtcNow); }

        public async Task<P1Result> ConnectAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                // An explicit new session never silently discards an ambiguous grant/cast.
                if (pending != null) return Fail("pending_mutation");
                State = P1ConnectionState.Connecting;
                var request = new P1Request("POST", "/p1/sessions", P1Wire.Encode(new P1SessionRequest()), null, Id());
                var reply = await Send(request, ct);
                var response = Parse<P1World>(reply);
                if (response == null || reply.StatusCode != 201 || response.error != null ||
                    !P1Wire.Hex32(response.sessionId) || !P1Wire.Valid(response.result))
                {
                    ClearSession(P1ConnectionState.Disconnected);
                    return Fail(response != null && response.error != null ? response.error.code : "connect_failed", reply.CorrelationId);
                }
                SessionId = response.sessionId; World = response.result;
                sequence = 0; pending = null; Quests = new P1Quest[0]; Inventory = null;
                LastCombatEvent = null; seenEvents.Clear(); seenEventOrder.Clear();
                cooldowns.Clear();
                return Ready();
            }
            finally { lane.Release(); }
        }

        public async Task<P1Result> ReadWorldAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try { return await ReadWorld(ct); }
            finally { lane.Release(); }
        }
        private async Task<P1Result> ReadWorld(CancellationToken ct)
        {
            if (SessionId == null) return Fail("not_connected");
            var reply = await Send(Get("/p1/world/" + SessionId), ct);
            var r = Parse<P1World>(reply);
            if (IsExpired(r)) return Expire();
            if (!Good(reply, r) || r.sessionId != SessionId || !P1Wire.Valid(r.result, World.self.characterId))
            {
                State = pending != null ? P1ConnectionState.UncertainMutation : P1ConnectionState.NeedsResync;
                return Fail(Error(reply, r), reply.CorrelationId);
            }
            // Actor revision first; server tick breaks ties without rolling world state back.
            if (r.result.revision > World.revision ||
                (r.result.revision == World.revision && r.result.serverTick >= World.serverTick)) World = r.result;
            if (pending != null) { State = P1ConnectionState.UncertainMutation; return P1Result.Ok(); }
            return Ready();
        }

        public async Task<P1Result> ReadQuestsAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (SessionId == null) return Fail("not_connected");
                var reply = await Send(Get("/p1/quests/" + SessionId), ct);
                var r = Parse<P1Quest[]>(reply);
                if (IsExpired(r)) return Expire();
                if (!Good(reply, r) || r.sessionId != SessionId || r.result == null) return Fail(Error(reply, r), reply.CorrelationId);
                foreach (var q in r.result) if (!ValidQuest(q)) return Fail("invalid_response");
                foreach (var q in r.result) ApplyQuest(q);
                LastError = null; return P1Result.Ok();
            }
            finally { lane.Release(); }
        }
        public async Task<P1Result> ReadInventoryAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (SessionId == null) return Fail("not_connected");
                var reply = await Send(Get("/p1/inventory/" + SessionId), ct);
                var r = Parse<P1Inventory>(reply);
                if (IsExpired(r)) return Expire();
                if (!Good(reply, r) || r.sessionId != SessionId || !ValidInventory(r.result)) return Fail(Error(reply, r), reply.CorrelationId);
                if (Inventory == null || r.result.inventoryRevision >= Inventory.inventoryRevision) Inventory = r.result;
                LastError = null; return P1Result.Ok();
            }
            finally { lane.Release(); }
        }

        public async Task<P1Result> MoveAsync(double x, double y, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready) return Fail("resync_required");
                if (!P1Wire.Finite(x) || !P1Wire.Finite(y) || Math.Abs(x) > 1 || Math.Abs(y) > 1) return Fail("invalid_input");
                double length = Math.Sqrt(x * x + y * y);
                if (length > 1) { x /= length; y /= length; }
                var req = Command("/p1/move", new P1Move { inputSequence = NextSequence(), moveX = x, moveY = y });
                State = P1ConnectionState.NeedsResync;
                var reply = await Send(req, ct);
                var r = Parse<P1World>(reply);
                if (IsExpired(r)) return Expire();
                if (!Good(reply, r))
                {
                    State = Ambiguous(reply, r) ? P1ConnectionState.NeedsResync : P1ConnectionState.Ready;
                    return Fail(Error(reply, r), reply.CorrelationId);
                }
                if (r.sessionId != SessionId || !P1Wire.Valid(r.result, World.self.characterId))
                { State = P1ConnectionState.NeedsResync; return Fail("invalid_response"); }
                if (r.result.revision >= World.revision) World = r.result;
                return Ready();
            }
            finally { lane.Release(); }
        }

        public async Task<P1Result> AcceptQuestAsync(string quest, string npc, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (string.IsNullOrWhiteSpace(quest) || string.IsNullOrWhiteSpace(npc)) return Fail("invalid_input");
                pending = Command("/p1/quests/accept", new P1QuestAccept { questId = quest, npcId = npc });
                pendingCombat = false;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }
        public async Task<P1Result> CastAsync(string skill, string target, double aimX, double aimY, CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try
            {
                if (State != P1ConnectionState.Ready || pending != null) return Fail("resync_required");
                if (skill != "SK-MK-01" && skill != "SK-MK-02" && skill != "SK-MK-03") return Fail("unsupported_skill");
                if (!P1Wire.Finite(aimX) || !P1Wire.Finite(aimY) || Math.Abs(aimX) > 1 || Math.Abs(aimY) > 1) return Fail("invalid_input");
                if (skill != "SK-MK-01" && string.IsNullOrWhiteSpace(target)) return Fail("target_required");
                pending = Command("/p1/combat", new P1Cast { inputSequence = NextSequence(), skillId = skill,
                    targetId = target, aimX = aimX, aimY = aimY });
                pendingCombat = true;
                return await SubmitPending(ct);
            }
            finally { lane.Release(); }
        }
        public async Task<P1Result> RetryPendingAsync(CancellationToken ct)
        {
            await lane.WaitAsync(ct);
            try { return pending == null ? Fail("no_pending_mutation") : await SubmitPending(ct); }
            finally { lane.Release(); }
        }

        private async Task<P1Result> SubmitPending(CancellationToken ct)
        {
            // Cancellation after send is also ambiguous; never leave new input enabled.
            State = P1ConnectionState.UncertainMutation;
            var reply = await Send(pending, ct);
            if (pendingCombat)
            {
                var r = Parse<P1CombatEvent>(reply);
                if (IsExpired(r)) return Expire();
                if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
                if (!Good(reply, r)) { pending = null; State = P1ConnectionState.Ready; return Fail(Error(reply, r), reply.CorrelationId); }
                if (r.sessionId != SessionId || r.result == null || !P1Wire.Hex32(r.result.eventId) || r.result.payload == null ||
                    r.result.schemaVersion != 1 || r.result.payload.sourceId != World.self.characterId ||
                    r.result.payload.skillId != P1Wire.Decode<P1Envelope<P1Cast>>(pending.Body).payload.skillId)
                    return Uncertain(reply.CorrelationId);
                if (seenEvents.Add(r.result.eventId))
                {
                    LastCombatEvent = r.result; seenEventOrder.Enqueue(r.result.eventId);
                    if (!string.IsNullOrEmpty(r.result.payload.skillId) && !string.IsNullOrEmpty(r.result.payload.cooldownEndsAtUtc))
                        cooldowns[r.result.payload.skillId] = r.result.payload.cooldownEndsAtUtc;
                    if (seenEventOrder.Count > 512) seenEvents.Remove(seenEventOrder.Dequeue());
                }
                pending = null;
                // MP/HP and pose come from a new world snapshot, not from an assumed cost.
                State = P1ConnectionState.NeedsResync;
                return await ReadWorld(ct);
            }
            else
            {
                var r = Parse<P1Quest>(reply);
                if (IsExpired(r)) return Expire();
                // A flag-off POST can be 405 because GET /quests/{sessionId} matches "accept".
                // Both missing-route variants are definite rejections, not an ambiguous commit.
                if ((reply.StatusCode == 404 || reply.StatusCode == 405) && r == null)
                { pending = null; State = P1ConnectionState.Ready; return Fail("feature_unavailable"); }
                if (Ambiguous(reply, r)) return Uncertain(reply.CorrelationId);
                if ((r.sessionId != null && r.sessionId != SessionId) || (r.result != null && r.sessionId != SessionId)) return Uncertain(reply.CorrelationId);
                if (r.result != null && r.result.questId != P1Wire.Decode<P1Envelope<P1QuestAccept>>(pending.Body).payload.questId) return Uncertain(reply.CorrelationId);
                if (r.result != null && ValidQuest(r.result)) ApplyQuest(r.result); // Reject can carry authoritative current state.
                if (Good(reply, r) && !ValidQuest(r.result)) return Uncertain(reply.CorrelationId);
                pending = null; State = P1ConnectionState.Ready;
                return Good(reply, r) ? Ready() : Fail(Error(reply, r), reply.CorrelationId);
            }
        }
        private P1Request Command<T>(string path, T payload)
        {
            var id = Id();
            var body = new P1Envelope<T> { requestId = id, idempotencyKey = Id(),
                sentAtUtc = utcNow().UtcDateTime.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'", CultureInfo.InvariantCulture), characterId = World.self.characterId, payload = payload };
            return new P1Request("POST", path, P1Wire.Encode(body), SessionId, id);
        }
        private P1Request Get(string path) { return new P1Request("GET", path, null, SessionId, Id()); }
        private int NextSequence() { return checked(++sequence); }
        private static string Id() { return Guid.NewGuid().ToString("N"); }
        private async Task<P1HttpReply> Send(P1Request request, CancellationToken ct)
        {
            try { return await transport.SendAsync(request, ct) ?? new P1HttpReply { StatusCode = 0 }; }
            catch (OperationCanceledException) { ct.ThrowIfCancellationRequested(); return new P1HttpReply { StatusCode = 0, CorrelationId = request.CorrelationId }; }
            catch (Exception e) when (e is System.IO.IOException || e is System.Net.Http.HttpRequestException)
            { return new P1HttpReply { StatusCode = 0, CorrelationId = request.CorrelationId }; }
        }
        private static P1Response<T> Parse<T>(P1HttpReply reply)
        {
            try
            {
                var r = P1Wire.Decode<P1Response<T>>(reply.Body);
                return r != null && r.schemaVersion == 1 && P1Wire.Hex32(r.requestId) ? r : null;
            }
            catch (Newtonsoft.Json.JsonException) { return null; }
        }
        private static bool Good<T>(P1HttpReply h, P1Response<T> r) { return h.StatusCode >= 200 && h.StatusCode < 300 && r != null && r.error == null; }
        private static bool Ambiguous<T>(P1HttpReply h, P1Response<T> r) { return h.StatusCode == 0 || h.StatusCode >= 500 || r == null; }
        private static string Error<T>(P1HttpReply h, P1Response<T> r)
        { return r != null && r.error != null ? r.error.code : h.StatusCode == 0 ? "network_unavailable" : "invalid_response"; }
        private static bool IsExpired<T>(P1Response<T> r) { return r != null && r.error != null && r.error.code == "session_not_found"; }
        private static bool ValidQuest(P1Quest q)
        {
            if (q == null || string.IsNullOrEmpty(q.questId) || string.IsNullOrEmpty(q.stepId) || q.objectiveCounters == null || q.revision < 0) return false;
            if (q.state != "LOCKED" && q.state != "AVAILABLE" && q.state != "ACTIVE" && q.state != "READY_TO_TURN_IN" && q.state != "COMPLETED" && q.state != "FAILED") return false;
            foreach (int n in q.objectiveCounters.Values) if (n < 0) return false;
            return true;
        }
        private static bool ValidInventory(P1Inventory inv)
        {
            if (inv == null || inv.inventoryRevision < 0 || inv.items == null || inv.currencies == null) return false;
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var item in inv.items)
                if (item == null || item.stack < 1 || string.IsNullOrEmpty(item.instanceId) || string.IsNullOrEmpty(item.templateId) ||
                    !ids.Add(item.instanceId) || item.durability < 0 || item.version < 0 ||
                    (item.location != "BAG" && item.location != "EQUIPPED" && item.location != "BANK")) return false;
            ids.Clear();
            foreach (var currency in inv.currencies)
                if (currency == null || currency.amount < 0 || string.IsNullOrEmpty(currency.currencyId) || !ids.Add(currency.currencyId)) return false;
            return true;
        }
        private void ApplyQuest(P1Quest q)
        {
            for (int i = 0; i < Quests.Length; i++) if (Quests[i].questId == q.questId)
            { if (q.revision >= Quests[i].revision) Quests[i] = q; return; }
            var list = new List<P1Quest>(Quests); list.Add(q); Quests = list.ToArray();
        }
        private P1Result Ready() { State = P1ConnectionState.Ready; LastError = null; return P1Result.Ok(); }
        private P1Result Uncertain(string correlation)
        { State = P1ConnectionState.UncertainMutation; return Fail("mutation_outcome_unknown", correlation); }
        private P1Result Fail(string error, string correlation = null)
        { LastError = error; LastCorrelationId = correlation; return P1Result.Fail(error, correlation); }
        private void ClearSession(P1ConnectionState state)
        { SessionId = null; World = null; Quests = new P1Quest[0]; Inventory = null; pending = null; LastCombatEvent = null; cooldowns.Clear(); State = state; }
        private P1Result Expire() { ClearSession(P1ConnectionState.Expired); return Fail("session_not_found"); }
    }
}
