// OPC-16 O4 — TALK read model. The receipt only proves what the server credited
// (objective/flag/event id, quest revision); it never grants XP, turn-in,
// chapter unlock or a map transition. After TALK the client must fresh-read the
// world. Owner: OpenCode.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class TalkViewState
    {
        public string NpcId { get; }
        public string NodeId { get; }
        public string QuestId { get; }
        public string ObjectiveId { get; }
        public string AppliedFlag { get; }
        public string EventId { get; }
        public long Revision { get; }
        public bool Credited { get; }
        public bool Replayed { get; }
        public bool HasReceipt { get; }
        public bool CanTalk { get; }
        public bool HasPendingMutation { get; }
        public string ErrorCode { get; }
        public string CorrelationId { get; }
        public string HintVi { get; }

        internal TalkViewState(
            string npcId, string nodeId, string questId, string objectiveId,
            string appliedFlag, string eventId, long revision, bool credited, bool replayed,
            bool canTalk, bool hasPendingMutation,
            string errorCode, string correlationId, string hintVi)
        {
            NpcId = npcId;
            NodeId = nodeId;
            QuestId = questId;
            ObjectiveId = objectiveId;
            AppliedFlag = appliedFlag;
            EventId = eventId;
            Revision = revision;
            Credited = credited;
            Replayed = replayed;
            HasReceipt = !string.IsNullOrEmpty(questId) && !string.IsNullOrEmpty(nodeId);
            CanTalk = canTalk;
            HasPendingMutation = hasPendingMutation;
            ErrorCode = errorCode;
            CorrelationId = correlationId;
            HintVi = hintVi;
        }
    }

    public sealed class TalkPresenter
    {
        private readonly IP1TalkAdapter _adapter;
        private TalkViewState _view;
        private string _lastNpcId;
        private string _lastNodeId;
        private string _lastErrorCode;
        private string _lastCorrelationId;

        public TalkViewState View { get { return _view; } }
        public event Action OnChanged;

        public TalkPresenter(IP1TalkAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        public TalkViewState Refresh()
        {
            var receipt = _adapter.LastTalk;
            bool canTalk = _adapter.ConnectionState == UIConnectionState.Ready && !_adapter.HasPendingMutation;
            _view = new TalkViewState(
                receipt != null ? receipt.npcId : _lastNpcId,
                receipt != null ? receipt.nodeId : _lastNodeId,
                receipt != null ? receipt.questId : null,
                receipt != null ? receipt.objectiveId : null,
                receipt != null ? receipt.appliedFlag : null,
                receipt != null ? receipt.eventId : null,
                receipt != null ? receipt.revision : 0,
                receipt != null && receipt.credited,
                receipt != null && receipt.replayed,
                canTalk,
                _adapter.HasPendingMutation,
                _lastErrorCode,
                _lastCorrelationId,
                BuildHint(receipt, canTalk));
            Notify();
            return _view;
        }

        public async Task<TalkViewState> TalkAsync(string npcId, string nodeId, CancellationToken ct)
        {
            if (string.IsNullOrWhiteSpace(npcId) || string.IsNullOrWhiteSpace(nodeId))
                return Fail("invalid_input");
            if (_adapter.HasPendingMutation) return Fail("pending_mutation");
            if (_adapter.ConnectionState != UIConnectionState.Ready) return Fail("resync_required");

            _lastNpcId = npcId;
            _lastNodeId = nodeId;
            var result = await _adapter.TalkAsync(npcId, nodeId, ct);
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

        private TalkViewState Fail(string code)
        {
            _lastErrorCode = code;
            _lastCorrelationId = null;
            return Refresh();
        }

        private string BuildHint(P1QuestTalkResult receipt, bool canTalk)
        {
            if (!string.IsNullOrEmpty(_lastErrorCode)) return HintFor(_lastErrorCode);
            if (receipt == null) return canTalk ? "Chọn lời thoại với NPC." : "Cần đồng bộ lại với máy chủ.";
            if (receipt.replayed) return "Máy chủ cho biết lời thoại này đã được ghi nhận trước đó.";
            if (!receipt.credited) return "Máy chủ đã trả lời nhưng không cấp tiến độ cho lời thoại này.";
            if (_adapter.ConnectionState != UIConnectionState.Ready)
                return "Máy chủ đã ghi nhận lời thoại. Cần đọc lại thế giới trước khi tiếp tục.";
            return "Máy chủ đã ghi nhận lời thoại; không tự cấp thưởng hay mở chương.";
        }

        private static string HintFor(string code)
        {
            if (code == "invalid_input") return "Cần chọn NPC và đoạn thoại cụ thể.";
            if (code == "invalid_payload") return "Yêu cầu lời thoại không đúng hợp đồng máy chủ.";
            if (code == "pending_mutation") return "Đang chờ máy chủ xác nhận thao tác trước.";
            if (code == "resync_required") return "Cần đồng bộ lại với máy chủ trước khi nói chuyện.";
            if (code == "feature_unavailable") return "Lời thoại nhiệm vụ chưa được bật trên máy chủ.";
            if (code == "invalid_transition") return "Đoạn thoại chưa mở cho nhiệm vụ hiện tại.";
            if (code == "quest_not_found") return "Không tìm thấy nhiệm vụ của lời thoại này.";
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
