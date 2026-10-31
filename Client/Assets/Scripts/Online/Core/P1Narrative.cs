using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace NguMach.Client.P1
{
    [Serializable] public sealed class P1NarrativeBundle
    {
        public int schemaVersion;
        public string locale, sourceDigest;
        public P1NarrativeEntry[] entries;
        public P1NarrativeNpc[] npcs;
    }
    [Serializable] public sealed class P1NarrativeNpc
    { public string entityId, npcId, mapId, displayName; }
    [Serializable] public sealed class P1NarrativeReply
    { public string label, text; }
    [Serializable] public sealed class P1NarrativeEntry
    {
        public string nodeId, questId, title, speakerId, questState, command, requiredCheckpoint;
        public string[] allowedMapIds, pages, committedPages;
        public P1NarrativeReply[] replies;
    }

    // Read-only localization/presentation catalog. No executable Ink, flags, rewards or commands from prose.
    public sealed class P1NarrativeCatalog
    {
        private readonly P1NarrativeBundle data;
        public string SourceDigest { get { return data.sourceDigest; } }
        public P1NarrativeCatalog(P1NarrativeBundle bundle)
        {
            if (bundle == null || bundle.schemaVersion != 1 || bundle.locale != "vi" ||
                bundle.entries == null || bundle.npcs == null || string.IsNullOrWhiteSpace(bundle.sourceDigest))
                throw new ArgumentException("Invalid narrative bundle");
            var ids = new HashSet<string>(StringComparer.Ordinal);
            foreach (var e in bundle.entries)
            {
                if (e == null || !ids.Add(e.nodeId ?? "") || string.IsNullOrWhiteSpace(e.nodeId) ||
                    string.IsNullOrWhiteSpace(e.questId) || string.IsNullOrWhiteSpace(e.speakerId) ||
                    e.allowedMapIds == null || e.allowedMapIds.Length == 0 || e.pages == null || e.pages.Length == 0 ||
                    Array.Exists(e.pages, string.IsNullOrWhiteSpace) ||
                    !StateKnown(e.questState) || !CommandKnown(e.command) ||
                    (e.command == "ACCEPT" && e.questState != "AVAILABLE") ||
                    (e.command == "TURN_IN" && e.questState != "READY_TO_TURN_IN"))
                    throw new ArgumentException("Invalid narrative entry: " + e?.nodeId);
            }
            ids.Clear();
            foreach (var n in bundle.npcs)
                if (n == null || !ids.Add(n.entityId ?? "") || string.IsNullOrWhiteSpace(n.entityId) ||
                    string.IsNullOrWhiteSpace(n.npcId) || string.IsNullOrWhiteSpace(n.mapId))
                    throw new ArgumentException("Invalid NPC binding");
            data = bundle;
        }
        private static bool StateKnown(string s) => s == "AVAILABLE" || s == "ACTIVE" || s == "READY_TO_TURN_IN";
        private static bool CommandKnown(string s) => s == "NONE" || s == "ACCEPT" || s == "TURN_IN";
        public P1NarrativeNpc Npc(string entityId, string mapId) =>
            Array.Find(data.npcs, n => n.entityId == entityId && n.mapId == mapId);
        public P1NarrativeEntry[] For(string npcId, string mapId, P1Quest[] quests)
        {
            var result = new List<P1NarrativeEntry>();
            foreach (var e in data.entries)
            {
                // No reviewed checkpoint feed exists yet for post-boss publication choices.
                if (!string.IsNullOrEmpty(e.requiredCheckpoint)) continue;
                var q = Array.Find(quests ?? Array.Empty<P1Quest>(), item => item != null && item.questId == e.questId);
                if (q != null && q.state == e.questState && e.speakerId == npcId &&
                    Array.IndexOf(e.allowedMapIds, mapId) >= 0) result.Add(e);
            }
            return result.ToArray();
        }
    }

    // A conversation reads server snapshots; only explicit buttons call the existing reviewed P1 commands.
    // The closed interact contract handles parcels/nodes, NOT NPC conversations: never POST an NPC to it.
    public sealed class P1NarrativeFlow : IDisposable
    {
        private readonly P1Client client;
        private readonly P1NarrativeCatalog catalog;
        private int generation, busy;
        private string session, entityId, mapId, expectedState, pendingCommand;
        private string mapInstance, floor;
        private P1NarrativeEntry[] options = Array.Empty<P1NarrativeEntry>();
        private bool committed;
        public bool IsOpen { get; private set; }
        public bool IsCommitted { get { return committed; } }
        public bool IsBusy { get { return busy != 0; } }
        public P1NarrativeEntry Entry { get; private set; }
        public P1NarrativeNpc Npc { get; private set; }
        public int PageIndex { get; private set; }
        public string Error { get; private set; }
        public string CorrelationId { get; private set; }
        public string ReplyText { get; private set; }
        public IReadOnlyList<P1NarrativeEntry> Options { get { return options; } }
        public string Page { get { return Entry == null ? "" : Pages[PageIndex]; } }
        private string[] Pages { get { return committed ? Entry.committedPages : Entry.pages; } }
        public int PageCount { get { return Entry == null ? 0 : Pages.Length; } }
        public bool CanCommand { get { return IsOpen && !IsBusy && Entry != null && !committed &&
            PageIndex == PageCount - 1 && Entry.command != "NONE" && ValidContext() &&
            client.State == P1ConnectionState.Ready && !client.HasPendingMutation; } }
        public bool CanRetry { get { return IsOpen && !IsBusy && pendingCommand != null && client.HasPendingMutation && session == client.SessionId; } }
        public event Action Changed;
        public P1NarrativeFlow(P1Client source, P1NarrativeCatalog text)
        { client = source ?? throw new ArgumentNullException(nameof(source)); catalog = text ?? throw new ArgumentNullException(nameof(text)); }

        public async Task<bool> OpenAsync(string target, CancellationToken ct)
        {
            Close();
            if (Interlocked.CompareExchange(ref busy, 1, 0) != 0) return false;
            int mine = generation;
            session = client.SessionId; entityId = target;
            try
            {
                if (session == null || client.HasPendingMutation || client.State != P1ConnectionState.Ready) return false;
                var r = await client.ReadWorldAsync(ct);
                if (!Current(mine, ct) || !r.Success) return false;
                mapId = client.World?.mapId;
                mapInstance = client.WorldV2?.mapInstanceId; floor = client.WorldV2?.floorId;
                Npc = catalog.Npc(target, mapId);
                if (!VisibleNpc()) return false;
                r = await client.ReadQuestsAsync(ct);
                if (!Current(mine, ct) || !r.Success || !VisibleNpc()) return false;
                options = catalog.For(Npc.npcId, mapId, client.Quests);
                if (options.Length == 0) return false;
                IsOpen = true;
                Select(0);
                return true;
            }
            finally
            {
                Interlocked.Exchange(ref busy, 0);
                if (mine == generation) { if (!IsOpen) ClearView(); Changed?.Invoke(); }
            }
        }
        private bool Current(int mine, CancellationToken ct) => mine == generation && !ct.IsCancellationRequested && session == client.SessionId;
        private bool VisibleNpc()
        {
            var w = client.World;
            if (Npc == null || w == null || w.self == null || w.self.hp <= 0 || w.mapId != mapId || w.entities == null) return false;
            if (mapInstance != null && (client.WorldV2?.mapInstanceId != mapInstance || client.WorldV2?.floorId != floor)) return false;
            var npc = Array.Find(w.entities, e => e != null && e.entityId == entityId && e.kind == "NPC");
            // 5WU is the P1 quest interaction radius. Server accept/turn-in rechecks authoritative proximity.
            return npc != null && npc.state != "DEAD" && (npc.availability == null || npc.availability == "AVAILABLE") &&
                P1Wire.Finite(npc.x) && P1Wire.Finite(npc.y) &&
                Math.Pow(w.self.x - npc.x, 2) + Math.Pow(w.self.y - npc.y, 2) <= 25.000000001;
        }
        private bool ValidContext()
        {
            if (session != client.SessionId || !VisibleNpc() || Entry == null) return false;
            var q = Array.Find(client.Quests, item => item != null && item.questId == Entry.questId);
            return q != null && q.state == expectedState;
        }
        public void RefreshValidity()
        {
            if (!IsOpen) return;
            if (client.State == P1ConnectionState.Expired || client.State == P1ConnectionState.Disconnected || session != client.SessionId) { Close(); return; }
            if (!IsBusy && !ValidContext()) Close();
        }
        public void Select(int index)
        {
            if (!IsOpen || index < 0 || index >= options.Length || pendingCommand != null || (IsBusy && Entry != null)) return;
            Entry = options[index]; expectedState = Entry.questState; PageIndex = 0; committed = false; ReplyText = Error = CorrelationId = null;
            Changed?.Invoke();
        }
        public void Next() { if (IsOpen && !IsBusy && PageIndex + 1 < PageCount) { PageIndex++; ReplyText = null; Changed?.Invoke(); } }
        public void Previous() { if (IsOpen && !IsBusy && PageIndex > 0) { PageIndex--; ReplyText = null; Changed?.Invoke(); } }
        public void SkipToAction() { if (IsOpen && !IsBusy && Entry != null) { PageIndex = PageCount - 1; ReplyText = null; Changed?.Invoke(); } }
        public void Reply(int index)
        {
            if (!IsOpen || IsBusy || committed || Entry?.replies == null || index < 0 || index >= Entry.replies.Length) return;
            ReplyText = Entry.replies[index].text; Changed?.Invoke(); // local tone only, never a quest event
        }
        public async Task<P1Result> SubmitAsync(CancellationToken ct)
        {
            if (!CanCommand || Interlocked.CompareExchange(ref busy, 1, 0) != 0) return P1Result.Fail("narrative_not_available");
            int mine = generation; pendingCommand = Entry.command;
            return await Execute(mine, ct, false);
        }
        public async Task<P1Result> RetryAsync(CancellationToken ct)
        {
            if (!CanRetry || Interlocked.CompareExchange(ref busy, 1, 0) != 0) return P1Result.Fail("no_pending_mutation");
            return await Execute(generation, ct, true);
        }
        private async Task<P1Result> Execute(int mine, CancellationToken ct, bool retry)
        {
            var entry = Entry; string command = pendingCommand; Changed?.Invoke();
            try
            {
                var result = retry ? await client.RetryPendingAsync(ct) : command == "ACCEPT"
                    ? await client.AcceptQuestAsync(entry.questId, Npc.npcId, ct)
                    : await client.TurnInQuestAsync(entry.questId, Npc.npcId, ct);
                if (!Current(mine, ct)) { if (mine == generation) Close(); return result; }
                Error = result.Success ? null : result.Code; CorrelationId = result.CorrelationId;
                if (!client.HasPendingMutation) pendingCommand = null;
                var q = Array.Find(client.Quests, item => item.questId == entry.questId);
                // A local page, old receipt, or READY status never means a committed reward.
                if (result.Success && command == "TURN_IN" && q?.state == "COMPLETED" &&
                    client.LastTurnIn?.questState?.questId == entry.questId &&
                    entry.committedPages != null && entry.committedPages.Length > 0)
                { committed = true; expectedState = "COMPLETED"; PageIndex = 0; ReplyText = null; }
                else if (result.Success) Close();
                return result;
            }
            finally { Interlocked.Exchange(ref busy, 0); if (mine == generation) Changed?.Invoke(); }
        }
        public void Close() { Interlocked.Increment(ref generation); IsOpen = false; ClearView(); Changed?.Invoke(); }
        private void ClearView() { Entry = null; Npc = null; options = Array.Empty<P1NarrativeEntry>(); PageIndex = 0; committed = false; ReplyText = null; pendingCommand = null; }
        public void Dispose() { Close(); Changed = null; }
    }
}
