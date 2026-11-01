// AG5 / OPC-13 C — MapPresenter: builds MapViewState from P1Client world snapshot.
// Map zoom AND pan are UI-only, never modify the world camera (DEC-019 constraint).
// Topology marked "candidate" until reviewed — never edits 349 coordinates.
// Pan offset is relative to the player (map follows the player) and is clamped so
// the visible world window never leaves the canonical map bounds (map_bounds.json).
// Camera rectangle / waypoint rendering is NOT implemented: no authority contract
// exists yet — the panel shows an UNSUPPORTED notice instead of inventing coordinates.
// Owner: Antigravity Remote — Issue #80, #85; Package C OPC-13 — Issue #85.

using System;
using System.Collections.Generic;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class MapPresenter
    {
        private readonly IP1UIAdapter _adapter;
        private MapViewState _state;
        private float _zoomLevel = 1f;
        // OPC-13 C: view-center offset from the player, in world units (UI-only pan).
        private double _panX, _panY;

        public MapViewState State => _state;
        public event Action OnChanged;

        public MapPresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        /// <summary>Rebuild map state from current world snapshot. Call after world refresh.</summary>
        public void Refresh()
        {
            // World v2 first, then v1 — self/markers/mapId must come from the SAME
            // generation, never a mixed v1-self/v2-markers snapshot.
            if (_adapter.WorldV2 != null)
            {
                var w2 = _adapter.WorldV2;
                var self2 = w2.self;
                if (self2 == null) { _panX = _panY = 0; _state = null; NotifyChanged(); return; }
                var bounds2 = MapBounds.ForMap(w2.mapId);
                if (_state != null && (_state.MapId != w2.mapId
                    || bounds2.XMin != _state.Bounds?.XMin || bounds2.XMax != _state.Bounds?.XMax
                    || bounds2.YMin != _state.Bounds?.YMin || bounds2.YMax != _state.Bounds?.YMax))
                {
                    _panX = _panY = 0; // OPC-14 M0: map switch (incl. mapId change / same-bounds) → drop stale pan
                }
                ClampPan(self2.x, self2.y, bounds2);
                _state = new MapViewState(w2.mapId, self2.x, self2.y, BuildMarkersV2(w2),
                    _zoomLevel, topologyIsCandidate: true, bounds2,
                    self2.x + _panX, self2.y + _panY);
                NotifyChanged();
                return;
            }

            if (_adapter.World != null)
            {
                var w = _adapter.World;
                var self1 = w.self;
                if (self1 == null) { _panX = _panY = 0; _state = null; NotifyChanged(); return; }
                var bounds1 = MapBounds.ForMap(w.mapId);
                if (_state != null && (_state.MapId != w.mapId
                    || bounds1.XMin != _state.Bounds?.XMin || bounds1.XMax != _state.Bounds?.XMax
                    || bounds1.YMin != _state.Bounds?.YMin || bounds1.YMax != _state.Bounds?.YMax))
                {
                    _panX = _panY = 0;
                }
                ClampPan(self1.x, self1.y, bounds1);
                _state = new MapViewState(w.mapId, self1.x, self1.y, BuildMarkersV1(w),
                    _zoomLevel, topologyIsCandidate: true, bounds1,
                    self1.x + _panX, self1.y + _panY);
                NotifyChanged();
                return;
            }

            _panX = _panY = 0;
            _state = null;
            NotifyChanged();
        }

        public void SetZoom(float zoom)
        {
            _zoomLevel = Math.Max(0.25f, Math.Min(4f, zoom));
            if (_state != null)
            {
                ClampPan(_state.PlayerX, _state.PlayerY, _state.Bounds);
                _state = new MapViewState(_state.MapId, _state.PlayerX, _state.PlayerY, _state.Markers,
                    _zoomLevel, _state.TopologyIsCandidate, _state.Bounds,
                    _state.PlayerX + _panX, _state.PlayerY + _panY);
            }
            NotifyChanged();
        }

        /// <summary>
        /// OPC-13 C: pan by a world-unit delta (UI gesture translation). The offset is
        /// accumulated then clamped so the visible world window stays inside the
        /// canonical map bounds at the current zoom. Pure local view state — no wire.
        /// </summary>
        public void PanBy(double dWorldX, double dWorldY)
        {
            _panX += dWorldX;
            _panY += dWorldY;
            RebuildPreservingPan();
            NotifyChanged();
        }

        /// <summary>OPC-13 C: re-center the view on the player (drops the pan offset).</summary>
        public void CenterOnPlayer()
        {
            _panX = _panY = 0;
            RebuildPreservingPan();
            NotifyChanged();
        }

        private void RebuildPreservingPan()
        {
            if (_state == null) return;
            ClampPan(_state.PlayerX, _state.PlayerY, _state.Bounds);
            _state = new MapViewState(
                _state.MapId, _state.PlayerX, _state.PlayerY, _state.Markers,
                _zoomLevel, _state.TopologyIsCandidate, _state.Bounds,
                _state.PlayerX + _panX, _state.PlayerY + _panY);
        }

        /// <summary>
        /// Clamps (panX,panY) so the visible window stays inside the map bounds per axis.
        /// The UI projection uses one uniform scale (canvas is square, based on bounds
        /// width), but each axis can exceed the map when the whole map fits the canvas —
        /// then the view locks to that axis's center (edge-less panning is meaningless
        /// when the entire map is already visible).
        /// </summary>
        private void ClampPan(double playerX, double playerY, MapBounds bounds)
        {
            if (bounds == null) { _panX = _panY = 0; return; }
            double halfX = Math.Min(bounds.Width / (_zoomLevel * 2), bounds.Width * 0.5);
            double halfY = Math.Min(bounds.Width / (_zoomLevel * 2), bounds.Height * 0.5); // same square-canvas visible extent as X (280x280 projection)
            double midX = (bounds.XMin + bounds.XMax) * 0.5;
            double midY = (bounds.YMin + bounds.YMax) * 0.5;

            // Travel shrinks to zero once the window covers the whole axis.
            double travelX = Math.Max(0, bounds.Width * 0.5 - halfX);
            double travelY = Math.Max(0, bounds.Height * 0.5 - halfY);
            double cx = playerX + _panX;
            double cy = playerY + _panY;
            cx = midX + Math.Max(-travelX, Math.Min(travelX, cx - midX));
            cy = midY + Math.Max(-travelY, Math.Min(travelY, cy - midY));
            _panX = cx - playerX;
            _panY = cy - playerY;
        }

        private static IReadOnlyList<MapMarker> BuildMarkersV1(P1World w)
        {
            var markers = new List<MapMarker>();
            markers.Add(new MapMarker(w.self.characterId, "PLAYER", w.self.x, w.self.y, "Bạn"));
            foreach (var e in w.entities ?? Array.Empty<P1Entity>())
            {
                if (e == null || string.IsNullOrEmpty(e.entityId)) continue;
                string label = ResolveMarkerLabel(e.entityId, e.kind);
                markers.Add(new MapMarker(e.entityId, e.kind ?? "UNKNOWN", e.x, e.y, label));
            }
            return markers;
        }

        private static IReadOnlyList<MapMarker> BuildMarkersV2(P1WorldV2 w)
        {
            var markers = new List<MapMarker>();
            markers.Add(new MapMarker(w.self.characterId, "PLAYER", w.self.x, w.self.y, "Bạn"));
            foreach (var e in w.entities ?? Array.Empty<P1EntityV2>())
            {
                if (e == null || string.IsNullOrEmpty(e.entityId)) continue;
                string label = ResolveMarkerLabel(e.entityId, e.kind);
                markers.Add(new MapMarker(e.entityId, e.kind ?? "UNKNOWN", e.x, e.y, label));
            }
            return markers;
        }

        private static string ResolveMarkerLabel(string entityId, string kind)
        {
            var npc = NpcContextMapping.Resolve(entityId);
            if (npc != null && !npc.DisplayName.Contains("UNRESOLVED"))
            {
                return npc.DisplayName;
            }
            return null;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
