// AG5 — MapPresenter: builds MapViewState from P1Client world snapshot.
// Map zoom is UI-only, never modifies world camera (DEC-019 constraint).
// Topology marked "candidate" until reviewed — never edits 349 coordinates.
// Owner: Antigravity Remote — Issue #80.

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

        public MapViewState State => _state;
        public event Action OnChanged;

        public MapPresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        /// <summary>Rebuild map state from current world snapshot. Call after world refresh.</summary>
        public void Refresh()
        {
            var self = _adapter.Self;
            if (self == null) { _state = null; NotifyChanged(); return; }

            string mapId;
            IReadOnlyList<MapMarker> markers;

            if (_adapter.WorldV2 != null)
            {
                var w2 = _adapter.WorldV2;
                mapId = w2.mapId;
                markers = BuildMarkersV2(w2);
            }
            else if (_adapter.World != null)
            {
                var w = _adapter.World;
                mapId = w.mapId;
                markers = BuildMarkersV1(w);
            }
            else
            {
                _state = null; NotifyChanged(); return;
            }

            _state = new MapViewState(mapId, self.x, self.y, markers, _zoomLevel, topologyIsCandidate: true);
            NotifyChanged();
        }

        public void SetZoom(float zoom)
        {
            _zoomLevel = Math.Max(0.25f, Math.Min(4f, zoom));
            if (_state != null)
                _state = new MapViewState(_state.MapId, _state.PlayerX, _state.PlayerY, _state.Markers, _zoomLevel, _state.TopologyIsCandidate);
            NotifyChanged();
        }

        private static IReadOnlyList<MapMarker> BuildMarkersV1(P1World w)
        {
            var markers = new List<MapMarker>();
            markers.Add(new MapMarker(w.self.characterId, "PLAYER", w.self.x, w.self.y, "You"));
            foreach (var e in w.entities ?? Array.Empty<P1Entity>())
            {
                if (e == null || string.IsNullOrEmpty(e.entityId)) continue;
                markers.Add(new MapMarker(e.entityId, e.kind ?? "UNKNOWN", e.x, e.y));
            }
            return markers;
        }

        private static IReadOnlyList<MapMarker> BuildMarkersV2(P1WorldV2 w)
        {
            var markers = new List<MapMarker>();
            markers.Add(new MapMarker(w.self.characterId, "PLAYER", w.self.x, w.self.y, "You"));
            foreach (var e in w.entities ?? Array.Empty<P1EntityV2>())
            {
                if (e == null || string.IsNullOrEmpty(e.entityId)) continue;
                markers.Add(new MapMarker(e.entityId, e.kind ?? "UNKNOWN", e.x, e.y));
            }
            return markers;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
