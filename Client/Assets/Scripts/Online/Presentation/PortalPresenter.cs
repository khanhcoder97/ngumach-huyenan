// OPC-16 O4 — portal read model. The server owns the destination; the presenter
// shows the receipt and flags that a fresh world read is required. It never
// moves the actor locally and never treats a missing route as a success.
// Owner: OpenCode.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class PortalViewState
    {
        public string PortalId { get; }
        public string MapId { get; }
        public double XWu { get; }
        public double YWu { get; }
        public long Revision { get; }
        public string EventId { get; }
        public bool Applied { get; }
        public bool Replayed { get; }
        public int InflightCastsCancelled { get; }
        public int ReservedCountersCancelled { get; }
        public bool GuardWindowClosed { get; }
        public bool HasReceipt { get; }
        public bool RequiresWorldRefresh { get; }
        public bool CanRequest { get; }
        public bool HasPendingMutation { get; }
        public string ErrorCode { get; }
        public string CorrelationId { get; }
        public string HintVi { get; }

        internal PortalViewState(
            string portalId, string mapId, double xWu, double yWu,
            long revision, string eventId, bool applied, bool replayed,
            int inflightCastsCancelled, int reservedCountersCancelled, bool guardWindowClosed,
            bool requiresWorldRefresh, bool canRequest, bool hasPendingMutation,
            string errorCode, string correlationId, string hintVi)
        {
            PortalId = portalId;
            MapId = mapId;
            XWu = xWu;
            YWu = yWu;
            Revision = revision;
            EventId = eventId;
            Applied = applied;
            Replayed = replayed;
            InflightCastsCancelled = inflightCastsCancelled;
            ReservedCountersCancelled = reservedCountersCancelled;
            GuardWindowClosed = guardWindowClosed;
            HasReceipt = !string.IsNullOrEmpty(portalId) && !string.IsNullOrEmpty(mapId);
            RequiresWorldRefresh = requiresWorldRefresh;
            CanRequest = canRequest;
            HasPendingMutation = hasPendingMutation;
            ErrorCode = errorCode;
            CorrelationId = correlationId;
            HintVi = hintVi;
        }
    }

    public sealed class PortalPresenter
    {
        private readonly IP1TalkAdapter _adapter;
        private PortalViewState _view;
        private string _lastErrorCode;
        private string _lastCorrelationId;

        public PortalViewState View { get { return _view; } }
        public event Action OnChanged;

        public PortalPresenter(IP1TalkAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        public PortalViewState Refresh()
        {
            var receipt = _adapter.LastPortal;
            bool canRequest = _adapter.ConnectionState == UIConnectionState.Ready && !_adapter.HasPendingMutation;
            bool requiresRefresh = receipt != null && _adapter.ConnectionState != UIConnectionState.Ready;
            _view = new PortalViewState(
                receipt != null ? receipt.portalId : null,
                receipt != null ? receipt.mapId : null,
                receipt != null ? receipt.xWu : 0,
                receipt != null ? receipt.yWu : 0,
                receipt != null ? receipt.revision : 0,
                receipt != null ? receipt.eventId : null,
                receipt != null && receipt.applied,
                receipt != null && receipt.replayed,
                receipt != null ? receipt.inflightCastsCancelled : 0,
                receipt != null ? receipt.reservedCountersCancelled : 0,
                receipt != null && receipt.guardWindowClosed,
                requiresRefresh, canRequest, _adapter.HasPendingMutation,
                _lastErrorCode, _lastCorrelationId, BuildHint(receipt, canRequest, requiresRefresh));
            Notify();
            return _view;
        }

        public async Task<PortalViewState> RequestAsync(string portalId, CancellationToken ct)
        {
            if (string.IsNullOrWhiteSpace(portalId)) return Fail("invalid_input");
            if (_adapter.HasPendingMutation) return Fail("pending_mutation");
            if (_adapter.ConnectionState != UIConnectionState.Ready) return Fail("resync_required");

            var result = await _adapter.PortalAsync(portalId, ct);
            _lastErrorCode = result.Success ? null : result.Code;
            _lastCorrelationId = result.Success ? null : result.CorrelationId;
            return Refresh();
        }

        public void ClearError()
        {
            _lastErrorCode = null;
            _lastCorrelationId = null;
            Refresh();
        }

        private PortalViewState Fail(string code)
        {
            _lastErrorCode = code;
            _lastCorrelationId = null;
            return Refresh();
        }

        private string BuildHint(P1WorldPortalResult receipt, bool canRequest, bool requiresRefresh)
        {
            if (!string.IsNullOrEmpty(_lastErrorCode)) return HintFor(_lastErrorCode);
            if (receipt == null) return canRequest ? "Chọn cổng để yêu cầu máy chủ chuyển cảnh." :
                "Cần đồng bộ lại với máy chủ.";
            if (receipt.replayed)
                return "Máy chủ trả lại biên nhận cũ: đích giữ nguyên, không kéo nhân vật về.";
            if (requiresRefresh)
                return "Máy chủ đã nhận cổng. Đang chờ bản đồ mới; không tự dịch chuyển.";
            return "Đích do máy chủ chọn: " + receipt.mapId + ".";
        }

        private static string HintFor(string code)
        {
            if (code == "invalid_input") return "Cần chọn cổng cụ thể.";
            if (code == "invalid_payload") return "Yêu cầu chuyển cảnh không đúng hợp đồng máy chủ.";
            if (code == "pending_mutation") return "Đang chờ máy chủ xác nhận thao tác trước.";
            if (code == "resync_required") return "Cần đồng bộ lại với máy chủ trước khi chuyển cảnh.";
            if (code == "feature_unavailable") return "Cổng chuyển cảnh chưa được bật trên máy chủ.";
            if (code == "portal_locked") return "Cổng này còn khóa: chưa hoàn tất nhập môn P00-05.";
            if (code == "portal_not_found") return "Không tìm thấy cổng này.";
            if (code == "out_of_range") return "Cần đứng gần cổng hơn để chuyển cảnh.";
            if (code == "actor_not_alive") return "Nhân vật đang gục; không thể chuyển cảnh.";
            if (code == "invalid_map") return "Bản đồ đích không hợp lệ trên máy chủ.";
            if (code == "out_of_bounds") return "Điểm đến nằm ngoài giới hạn bản đồ.";
            if (code == "invalid_condition") return "Điều kiện chuyển cảnh chưa thỏa.";
            if (code == "idempotency_conflict") return "Khóa thao tác đã dùng cho lệnh khác.";
            if (code == "session_not_found") return "Phiên đã hết hạn. Vui lòng đăng nhập lại.";
            return "Máy chủ báo: " + code + ".";
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler != null) handler();
        }
    }
}
