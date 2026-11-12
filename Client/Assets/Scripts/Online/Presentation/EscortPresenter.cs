// OPC-17 gói39 O39-A — escort read model with provenance gating (pure C#).
// One authoritative snapshot/epoch: WorldV2 when present; WorldV1 only as a
// legacy single-snapshot source when no v2 exists at all. Rows from one
// epoch are never mixed with the map/tick of another one.
//
// Escort ownership status (on-road, owner, life, attempt, instance, floor,
// sample tick, quest/lifecycle state) is bound ONLY from an approved
// escort/current packet supplied by the host once that route ships. Without
// such a packet this presenter serves nothing: it never infers "escorted"
// ownership from an entity-id substring, an NPC-kind match or a road-range
// coordinate check — a generic/static NPC is not an escorted owner NPC.
//
// Read-only: absent provenance means "not served", never "dead". The server
// owns the escort machine and waypoints; this presenter never fabricates a
// path or a position. Owner: OpenCode.

using System;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    /// <summary>Approved escort/current packet. Supplied by the host once the
    /// escort/current route is approved and mapped; never synthesized here.</summary>
    public sealed class EscortPacket
    {
        public string OwnerCharacterId { get; }
        public string ActorEntityId { get; }
        public string LifeState { get; }
        public long AttemptId { get; }
        public string InstanceId { get; }
        public string FloorId { get; }
        public long SampleTick { get; }
        public string MapId { get; }
        /// <summary>Authoritative on-road flag carried by the packet; the
        /// presenter never infers it from coordinates.</summary>
        public bool OnRoad { get; }
        public string QuestId { get; }
        public string QuestStatus { get; }

        public EscortPacket(string ownerCharacterId, string actorEntityId, string lifeState,
            long attemptId, string instanceId, string floorId, long sampleTick, string mapId,
            bool onRoad, string questId, string questStatus)
        {
            OwnerCharacterId = ownerCharacterId;
            ActorEntityId = actorEntityId;
            LifeState = lifeState;
            AttemptId = attemptId;
            InstanceId = instanceId;
            FloorId = floorId;
            SampleTick = sampleTick;
            MapId = mapId;
            OnRoad = onRoad;
            QuestId = questId;
            QuestStatus = questStatus;
        }
    }

    public enum EscortProvenance
    {
        /// <summary>No world snapshot at all.</summary>
        NoSnapshot,
        /// <summary>Authoritative snapshot exists, but nothing is served:
        /// no approved escort packet is bound yet.</summary>
        NotServed,
        /// <summary>A packet was supplied but rejected by an epoch/owner/map/
        /// instance/floor guard; it never rewrites the view.</summary>
        PacketRejected,
        /// <summary>Approved packet bound to the audience row of the same
        /// authoritative epoch; ownership fields served as given.</summary>
        PacketBound
    }

    public sealed class EscortViewState
    {
        public string EntityId { get; }
        public string DisplayName { get; }
        public string Kind { get; }
        public bool InAudience { get; }
        public double X { get; }
        public double Y { get; }
        public double DistanceToSelfWu { get; }
        /// <summary>Server tick of the SAME authoritative snapshot that produced
        /// the row; never mixed across epochs.</summary>
        public long ServerTick { get; }
        public string MapId { get; }
        /// <summary>True only when a bound approved packet carries the on-road
        /// flag; never inferred from a coordinate range.</summary>
        public bool IsOnRoad { get; }
        public string HintVi { get; }
        /// <summary>Machine-readable provenance for host binding.</summary>
        public EscortProvenance Provenance { get; }
        /// <summary>"worldv2", "worldv1_legacy" or null (no snapshot).</summary>
        public string SourceSnapshot { get; }
        /// <summary>Machine reason when NotServed/PacketRejected; null when served.</summary>
        public string NotServedReason { get; }
        // Bound from the approved escort packet only; null while unbound.
        public string OwnerCharacterId { get; }
        public string ActorEntityId { get; }
        public string LifeState { get; }
        public long? AttemptId { get; }
        public string InstanceId { get; }
        public string FloorId { get; }
        public long? SampleTick { get; }
        public string QuestId { get; }
        public string QuestStatus { get; }

        internal EscortViewState(
            string entityId, string displayName, string kind, bool inAudience,
            double x, double y, double distanceToSelfWu, long serverTick, string mapId,
            bool isOnRoad, string hintVi, EscortProvenance provenance, string sourceSnapshot,
            string notServedReason, string ownerCharacterId, string actorEntityId,
            string lifeState, long? attemptId, string instanceId, string floorId,
            long? sampleTick, string questId, string questStatus)
        {
            EntityId = entityId;
            DisplayName = displayName;
            Kind = kind;
            InAudience = inAudience;
            X = x;
            Y = y;
            DistanceToSelfWu = distanceToSelfWu;
            ServerTick = serverTick;
            MapId = mapId;
            IsOnRoad = isOnRoad;
            HintVi = hintVi;
            Provenance = provenance;
            SourceSnapshot = sourceSnapshot;
            NotServedReason = notServedReason;
            OwnerCharacterId = ownerCharacterId;
            ActorEntityId = actorEntityId;
            LifeState = lifeState;
            AttemptId = attemptId;
            InstanceId = instanceId;
            FloorId = floorId;
            SampleTick = sampleTick;
            QuestId = questId;
            QuestStatus = questStatus;
        }
    }

    public sealed class EscortPresenter
    {
        public const string Unavailable = "not_in_audience";
        public const string SourceWorldV2 = "worldv2";
        public const string SourceWorldV1Legacy = "worldv1_legacy";

        private readonly IP1UIAdapter _adapter;
        private EscortPacket _packet;
        private EscortViewState _view;

        public EscortViewState View { get { return _view; } }
        public event Action OnChanged;

        public EscortPresenter(IP1UIAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        /// <summary>Bind (or clear with null) the approved escort packet. The
        /// host may only call this once the escort/current route is approved;
        /// the presenter guards every field against the authoritative epoch.</summary>
        public void BindEscortPacket(EscortPacket packet)
        {
            _packet = packet;
            Refresh();
        }

        public EscortViewState Refresh()
        {
            var worldV2 = _adapter.WorldV2;
            var worldV1 = _adapter.World;

            // One authoritative epoch. WorldV2, when present, is the live
            // epoch and WorldV1 is ignored entirely — even when v2 has no
            // escorted row. WorldV1 is used only when no v2 snapshot exists,
            // and then every field comes from that single v1 epoch.
            string source = worldV2 != null ? SourceWorldV2
                : worldV1 != null ? SourceWorldV1Legacy
                : null;
            string mapId = worldV2 != null ? worldV2.mapId : (worldV1 != null ? worldV1.mapId : null);
            long tick = worldV2 != null ? worldV2.serverTick : (worldV1 != null ? worldV1.serverTick : 0);
            var self = worldV2 != null && worldV2.self != null ? worldV2.self
                : worldV1 != null && worldV1.self != null ? worldV1.self
                : _adapter.Self;

            if (source == null)
            {
                _view = new EscortViewState(
                    null, null, null, false, double.NaN, double.NaN, double.NaN, 0, null, false,
                    "Chưa có snapshot thế giới authoritative.",
                    EscortProvenance.NoSnapshot, null, "no_snapshot",
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }

            var packet = _packet;
            if (packet == null)
            {
                // No approved escort packet: escort ownership is unsupported/
                // not served. A generic or static NPC in the audience is never
                // promoted to an escorted owner NPC by substring or coordinates.
                _view = new EscortViewState(
                    null, null, null, false, double.NaN, double.NaN, double.NaN, tick, mapId, false,
                    "Hộ tống chưa được phục vụ: chưa có packet escort đã duyệt; không suy đoán từ toạ độ.",
                    EscortProvenance.NotServed, source, "escort_packet_not_bound",
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }

            // Epoch/identity guards. Every rejection keeps the previous
            // semantics: not served, no partial binding, no coordinate guesses.
            // Escort/current is a v2 route: a legacy v1-only epoch never binds.
            string reject = null;
            if (string.IsNullOrEmpty(packet.OwnerCharacterId) || string.IsNullOrEmpty(packet.ActorEntityId))
                reject = "packet_missing_identity";
            else if (source != SourceWorldV2)
                reject = "packet_requires_worldv2";
            else if (packet.MapId == null || !string.Equals(packet.MapId, mapId, StringComparison.Ordinal))
                reject = "packet_map_mismatch";
            else if (packet.SampleTick != tick)
                reject = "packet_stale_sample";
            else if (self == null || !string.Equals(packet.OwnerCharacterId, self.characterId, StringComparison.Ordinal))
                reject = "packet_owner_mismatch";

            if (reject != null)
            {
                _view = new EscortViewState(
                    null, null, null, false, double.NaN, double.NaN, double.NaN, tick, mapId, false,
                    "Packet hộ tống bị từ chối bởi guard provenance; không serve.",
                    EscortProvenance.PacketRejected, source, reject,
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }

            // Locate the packet actor inside the SAME authoritative snapshot.
            double? rowX = null, rowY = null;
            string rowInstance = null, rowFloor = null;
            if (worldV2 != null && worldV2.entities != null)
            {
                for (int i = 0; i < worldV2.entities.Length; i++)
                {
                    var e = worldV2.entities[i];
                    if (e == null || e.kind != "NPC" || e.entityId == null) continue;
                    if (!string.Equals(e.entityId, packet.ActorEntityId, StringComparison.Ordinal)) continue;
                    rowX = e.x; rowY = e.y; rowInstance = e.mapInstanceId; rowFloor = e.floorId;
                    break;
                }
            }

            if (rowX == null)
            {
                // Absent/late audience row: the packet alone never fabricates a
                // position or an on-road claim.
                _view = new EscortViewState(
                    packet.ActorEntityId, packet.ActorEntityId, "NPC", false, double.NaN, double.NaN,
                    double.NaN, tick, mapId, false,
                    "Actor hộ tống chưa trong vùng nghe của snapshot authoritative (absent/late).",
                    EscortProvenance.PacketRejected, source, "packet_actor_absent_in_audience",
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }

            if (packet.InstanceId == null || !string.Equals(packet.InstanceId, rowInstance, StringComparison.Ordinal))
            {
                _view = new EscortViewState(
                    packet.ActorEntityId, packet.ActorEntityId, "NPC", false, double.NaN, double.NaN,
                    double.NaN, tick, mapId, false,
                    "Packet hộ tống khác map-instance với audience row; không serve.",
                    EscortProvenance.PacketRejected, source, "packet_instance_mismatch",
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }
            if (packet.FloorId == null || !string.Equals(packet.FloorId, rowFloor, StringComparison.Ordinal))
            {
                _view = new EscortViewState(
                    packet.ActorEntityId, packet.ActorEntityId, "NPC", false, double.NaN, double.NaN,
                    double.NaN, tick, mapId, false,
                    "Packet hộ tống khác floor với audience row; không serve.",
                    EscortProvenance.PacketRejected, source, "packet_floor_mismatch",
                    null, null, null, null, null, null, null, null, null);
                Notify();
                return _view;
            }

            double dist = self != null
                ? Math.Sqrt((rowX.Value - self.x) * (rowX.Value - self.x) + (rowY.Value - self.y) * (rowY.Value - self.y))
                : double.NaN;
            _view = new EscortViewState(
                packet.ActorEntityId, packet.ActorEntityId, "NPC", true, rowX.Value, rowY.Value, dist,
                tick, mapId, packet.OnRoad,
                "Đang hộ tống theo packet đã duyệt. Vị trí từ máy chủ, không tự tính đường đi.",
                EscortProvenance.PacketBound, source, null,
                packet.OwnerCharacterId, packet.ActorEntityId, packet.LifeState, packet.AttemptId,
                packet.InstanceId, packet.FloorId, packet.SampleTick, packet.QuestId, packet.QuestStatus);
            Notify();
            return _view;
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler == null) return;
            try { handler(); }
            catch (Exception) { /* consumer callback must not corrupt the presenter */ }
        }
    }
}
