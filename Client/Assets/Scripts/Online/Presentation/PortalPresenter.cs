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
        public string DestinationMapId { get; }
        public double DestinationXWu { get; }
        public double DestinationYWu { get; }
        public long ServerTick { get; }
        public long Revision { get; }
        public bool HasReceipt { get; }
        public bool RequiresWorldRefresh { get; }
        public bool CanRequest { get; }
        public bool HasPendingMutation { get; }
        public string ErrorCode { get; }
        public string CorrelationId { get; }
        public string HintVi { get; }

        internal PortalViewState(
            string portalId, string destinationMapId, double destinationXWu, double destinationYWu,
            long serverTick, long revision, bool requiresWorldRefresh,
            bool canRequest, bool hasPendingMutation, string errorCode, string correlationId, string hintVi)
        {
            PortalId = portalId;
            DestinationMapId = destinationMapId;
            DestinationXWu = destinationXWu;
            DestinationYWu = destinationYWu;
            ServerTick = serverTick;
            Revision = revision;
            HasReceipt = !string.IsNullOrEmpty(portalId) && !string.IsNullOrEmpty(destinationMapId);
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
                receipt != null ? receipt.destinationMapId : null,
                receipt != null ? receipt.destinationXWu : 0,
                receipt != null ? receipt.destinationYWu : 0,
                receipt != null ? receipt.serverTick : 0,
                receipt != null ? receipt.revision : 0,
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
            if (requiresRefresh)
                return "Máy chủ đã nhận cổng. Đang chờ bản đồ mới; không tự dịch chuyển.";
            return "Đích do máy chủ chọn: " + receipt.destinationMapId + ".";
        }

        private static string HintFor(string code)
        {
            if (code == "invalid_input") return "Cần chọn cổng cụ thể.";
            if (code == "pending_mutation") return "Đang chờ máy chủ xác nhận thao tác trước.";
            if (code == "resync_required") return "Cần đồng bộ lại với máy chủ trước khi chuyển cảnh.";
            if (code == "feature_unavailable") return "Cổng chuyển cảnh chưa được bật trên máy chủ.";
            if (code == "invalid_transition") return "Cổng này chưa mở cho nhân vật hiện tại.";
            if (code == "portal_not_found") return "Không tìm thấy cổng này.";
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
