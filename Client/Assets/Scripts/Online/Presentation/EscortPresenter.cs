// OPC-17 checkpoint 3 — escort read model (O-D). Projects the escorted NPC
// the authoritative world audience row already carries (P00-04 owner NPC
// LYAN on the Ben Mua road). The server owns the escort machine, waypoints
// and waves; this presenter never infers a path or fabricates positions.
// Read-only: an absent audience row means "not served", never "dead".
// Pure C#. Owner: OpenCode.

using System;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class EscortViewState
    {
        public string EntityId { get; }
        public string DisplayName { get; }
        public string Kind { get; }
        public bool InAudience { get; }
        public double X { get; }
        public double Y { get; }
        public double DistanceToSelfWu { get; }
        public long ServerTick { get; }
        public string MapId { get; }
        public bool IsOnRoad { get; }
        public string HintVi { get; }

        internal EscortViewState(
            string entityId, string displayName, string kind, bool inAudience,
            double x, double y, double distanceToSelfWu, long serverTick, string mapId, string hintVi)
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
            // The sourced P00-04 road runs anchor (42,0) to checkpoint (120,0).
            IsOnRoad = inAudience && x > 42.0 && x <= 120.0;
            HintVi = hintVi;
        }
    }

    public sealed class EscortPresenter
    {
        public const string EscortedNpcToken = "LYAN";
        public const string Unavailable = "not_in_audience";

        private readonly IP1UIAdapter _adapter;
        private EscortViewState _view;

        public EscortViewState View { get { return _view; } }
        public event Action OnChanged;

        public EscortPresenter(IP1UIAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        public EscortViewState Refresh()
        {
            var worldV2 = _adapter.WorldV2;
            var worldV1 = _adapter.World;
            var self = _adapter.Self ?? (worldV1 != null ? worldV1.self : null);

            P1EntityV2 rowV2 = null;
            if (worldV2 != null && worldV2.entities != null)
            {
                for (int i = 0; i < worldV2.entities.Length; i++)
                {
                    var e = worldV2.entities[i];
                    if (e != null && e.kind == "NPC" &&
                        e.entityId != null && e.entityId.Contains(EscortedNpcToken))
                    {
                        rowV2 = e;
                        break;
                    }
                }
            }

            P1Entity rowV1 = null;
            if (rowV2 == null && worldV1 != null && worldV1.entities != null)
            {
                for (int i = 0; i < worldV1.entities.Length; i++)
                {
                    var e = worldV1.entities[i];
                    if (e != null && e.kind == "NPC" &&
                        e.entityId != null && e.entityId.Contains(EscortedNpcToken))
                    {
                        rowV1 = e;
                        break;
                    }
                }
            }

            string mapId = worldV2 != null ? worldV2.mapId : (worldV1 != null ? worldV1.mapId : null);
            long tick = worldV2 != null ? worldV2.serverTick : (worldV1 != null ? worldV1.serverTick : 0);

            if (rowV2 != null)
            {
                double dist = self != null
                    ? Math.Sqrt((rowV2.x - self.x) * (rowV2.x - self.x) + (rowV2.y - self.y) * (rowV2.y - self.y))
                    : double.NaN;
                _view = new EscortViewState(
                    rowV2.entityId, string.IsNullOrEmpty(rowV2.entityId) ? rowV2.entityId : rowV2.entityId,
                    rowV2.kind, true, rowV2.x, rowV2.y, dist, tick, mapId,
                    "Đang hộ tống. Vị trí từ máy chủ, không tự tính đường đi.");
            }
            else if (rowV1 != null)
            {
                double dist = self != null
                    ? Math.Sqrt((rowV1.x - self.x) * (rowV1.x - self.x) + (rowV1.y - self.y) * (rowV1.y - self.y))
                    : double.NaN;
                _view = new EscortViewState(
                    rowV1.entityId, rowV1.entityId, rowV1.kind, true,
                    rowV1.x, rowV1.y, dist, tick, mapId,
                    "Đang hộ tống. Vị trí từ máy chủ, không tự tính đường đi.");
            }
            else
            {
                _view = new EscortViewState(
                    null, null, null, false, double.NaN, double.NaN, double.NaN, tick, mapId,
                    "NPC hộ tống chưa trong vùng nghe của máy chủ (ngoài bán kính).");
            }
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
