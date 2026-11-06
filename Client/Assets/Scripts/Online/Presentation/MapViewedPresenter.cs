// OPC-16 O4 — MAP_VIEWED read model. The acknowledgement is only a server
// receipt for the quest map view; it does not unlock a quest, grant progress or
// teleport the actor. A missing/disabled route is surfaced as unsupported.
// Owner: OpenCode.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class MapViewedViewState
    {
        public string QuestId { get; }
        public bool Acknowledged { get; }
        public long ServerTick { get; }
        public long Revision { get; }
        public bool HasReceipt { get; }
        public bool CanAcknowledge { get; }
        public bool HasPendingMutation { get; }
        public string ErrorCode { get; }
        public string CorrelationId { get; }
        public string HintVi { get; }

        internal MapViewedViewState(
            string questId, bool acknowledged, long serverTick, long revision,
            bool canAcknowledge, bool hasPendingMutation,
            string errorCode, string correlationId, string hintVi)
        {
            QuestId = questId;
            Acknowledged = acknowledged;
            ServerTick = serverTick;
            Revision = revision;
            HasReceipt = !string.IsNullOrEmpty(questId);
            CanAcknowledge = canAcknowledge;
            HasPendingMutation = hasPendingMutation;
            ErrorCode = errorCode;
            CorrelationId = correlationId;
            HintVi = hintVi;
        }
    }

    public sealed class MapViewedPresenter
    {
        private readonly IP1TalkAdapter _adapter;
        private MapViewedViewState _view;
        private string _lastErrorCode;
        private string _lastCorrelationId;

        public MapViewedViewState View { get { return _view; } }
        public event Action OnChanged;

        public MapViewedPresenter(IP1TalkAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        public MapViewedViewState Refresh()
        {
            var receipt = _adapter.LastMapViewed;
            bool canAcknowledge = _adapter.ConnectionState == UIConnectionState.Ready &&
                                  !_adapter.HasPendingMutation;
            _view = new MapViewedViewState(
                receipt != null ? receipt.questId : null,
                receipt != null && receipt.acknowledged,
                receipt != null ? receipt.serverTick : 0,
                receipt != null ? receipt.revision : 0,
                canAcknowledge, _adapter.HasPendingMutation,
                _lastErrorCode, _lastCorrelationId, BuildHint(receipt, canAcknowledge));
            Notify();
            return _view;
        }

        public async Task<MapViewedViewState> AcknowledgeAsync(string questId, CancellationToken ct)
        {
            if (string.IsNullOrWhiteSpace(questId)) return Fail("invalid_input");
            if (_adapter.HasPendingMutation) return Fail("pending_mutation");
            if (_adapter.ConnectionState != UIConnectionState.Ready) return Fail("resync_required");

            var result = await _adapter.MapViewedAsync(questId, ct);
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

        private MapViewedViewState Fail(string code)
        {
            _lastErrorCode = code;
            _lastCorrelationId = null;
            return Refresh();
        }

        private string BuildHint(P1QuestMapViewedResult receipt, bool canAcknowledge)
        {
            if (!string.IsNullOrEmpty(_lastErrorCode)) return HintFor(_lastErrorCode);
            if (receipt == null) return canAcknowledge ? "Mở bản đồ nhiệm vụ để ghi nhận." :
                "Cần đồng bộ lại với máy chủ.";
            if (!receipt.acknowledged) return "Máy chủ không xác nhận lần xem bản đồ này.";
            return "Máy chủ đã ghi nhận bạn xem bản đồ nhiệm vụ " + receipt.questId + ".";
        }

        private static string HintFor(string code)
        {
            if (code == "invalid_input") return "Cần chọn nhiệm vụ cụ thể.";
            if (code == "pending_mutation") return "Đang chờ máy chủ xác nhận thao tác trước.";
            if (code == "resync_required") return "Cần đồng bộ lại với máy chủ trước khi ghi nhận.";
            if (code == "feature_unavailable") return "Đánh dấu bản đồ chưa được bật trên máy chủ.";
            if (code == "quest_not_found") return "Không tìm thấy nhiệm vụ này.";
            if (code == "invalid_transition") return "Nhiệm vụ chưa cho phép ghi nhận bản đồ.";
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
