// OPC-16 O4 — system message read model. UI notices are local presentation only:
// they never grant progress, never hide a server rejection and never claim a
// feature is enabled. Codes are localized to Vietnamese; unknown codes keep the
// raw server code so a bug is visible during alpha.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public enum SystemMessageSeverity { Info, Warning, Error, Critical }

    public sealed class SystemMessageView
    {
        public long Sequence { get; }
        public SystemMessageSeverity Severity { get; }
        public string Code { get; }
        public string TextVi { get; }
        public string CorrelationId { get; }
        public bool IsBlocking { get; }

        internal SystemMessageView(
            long sequence, SystemMessageSeverity severity, string code, string textVi,
            string correlationId, bool isBlocking)
        {
            Sequence = sequence;
            Severity = severity;
            Code = code;
            TextVi = textVi;
            CorrelationId = correlationId;
            IsBlocking = isBlocking;
        }
    }

    public sealed class SystemMessagePresenter
    {
        private readonly List<SystemMessageView> _messages = new List<SystemMessageView>();
        private readonly int _capacity;
        private ReadOnlyCollection<SystemMessageView> _snapshot;
        private long _sequence;
        private int _blockingCount;

        public IReadOnlyList<SystemMessageView> Messages
        {
            get
            {
                if (_snapshot == null) _snapshot = new ReadOnlyCollection<SystemMessageView>(_messages.ToArray());
                return _snapshot;
            }
        }

        public SystemMessageView Last { get { return _messages.Count == 0 ? null : _messages[0]; } }
        public bool HasBlocking { get { return _blockingCount > 0; } }
        public int Capacity { get { return _capacity; } }
        public event Action OnChanged;

        public SystemMessagePresenter(int capacity = 64)
        {
            _capacity = capacity < 1 ? 1 : capacity;
        }

        public SystemMessageView Push(
            SystemMessageSeverity severity, string code, string textVi = null, string correlationId = null)
        {
            string normalizedCode = string.IsNullOrEmpty(code) ? "unknown" : code;
            string text = string.IsNullOrEmpty(textVi) ? Localize(normalizedCode) : textVi;

            // The UI pump may report the same last error each frame; do not stack
            // identical notices. A later distinct event still adds a new entry.
            for (int i = 0; i < _messages.Count; i++)
            {
                var existing = _messages[i];
                if (existing.Severity == severity &&
                    string.Equals(existing.Code, normalizedCode, StringComparison.Ordinal) &&
                    string.Equals(existing.CorrelationId, correlationId, StringComparison.Ordinal) &&
                    string.Equals(existing.TextVi, text, StringComparison.Ordinal))
                    return existing;
            }

            bool blocking = severity == SystemMessageSeverity.Critical;
            var message = new SystemMessageView(++_sequence, severity, normalizedCode, text, correlationId, blocking);
            _messages.Insert(0, message);
            if (blocking) _blockingCount++;
            while (_messages.Count > _capacity)
            {
                var removed = _messages[_messages.Count - 1];
                if (removed.IsBlocking) _blockingCount--;
                _messages.RemoveAt(_messages.Count - 1);
            }
            _snapshot = null;
            Notify();
            return message;
        }

        public SystemMessageView PushResult(P1Result result, string actionVi = null)
        {
            if (result == null)
                return Push(SystemMessageSeverity.Error, "unknown_result",
                    string.IsNullOrEmpty(actionVi) ? Localize("unknown_result") : "Không thể " + actionVi + ". " + Localize("unknown_result"));
            if (result.Success)
                return Push(SystemMessageSeverity.Info, "ok",
                    string.IsNullOrEmpty(actionVi) ? "Thao tác đã được máy chủ xác nhận." :
                    actionVi + " đã được máy chủ xác nhận.");

            var severity = IsCritical(result.Code) ? SystemMessageSeverity.Critical : SystemMessageSeverity.Error;
            string prefix = string.IsNullOrEmpty(actionVi) ? "" : "Không thể " + actionVi + ". ";
            return Push(severity, result.Code, prefix + Localize(result.Code), result.CorrelationId);
        }

        public bool Dismiss(long sequence)
        {
            for (int i = 0; i < _messages.Count; i++)
            {
                if (_messages[i].Sequence != sequence) continue;
                if (_messages[i].IsBlocking) _blockingCount--;
                _messages.RemoveAt(i);
                _snapshot = null;
                Notify();
                return true;
            }
            return false;
        }

        public void Clear()
        {
            if (_messages.Count == 0 && _blockingCount == 0) return;
            _messages.Clear();
            _blockingCount = 0;
            _snapshot = null;
            Notify();
        }

        public static bool IsCritical(string code)
        {
            return code == "session_expired" || code == "session_not_found" ||
                   code == "not_connected" || code == "auth_failed" || code == "schema_mismatch";
        }

        public static string Localize(string code)
        {
            if (string.IsNullOrEmpty(code)) return "Máy chủ không trả mã lỗi.";
            switch (code)
            {
                case "ok": return "Thao tác đã được máy chủ xác nhận.";
                case "feature_unavailable": return "Tính năng này chưa được bật trên máy chủ.";
                case "resync_required": return "Cần đồng bộ lại với máy chủ trước khi tiếp tục.";
                case "pending_mutation": return "Đang chờ máy chủ xác nhận thao tác trước.";
                case "mutation_outcome_unknown": return "Chưa rõ kết quả thao tác; cần thử lại đúng thao tác cũ.";
                case "session_expired": return "Phiên đã hết hạn. Vui lòng đăng nhập lại.";
                case "session_not_found": return "Máy chủ không tìm thấy phiên hiện tại. Vui lòng đăng nhập lại.";
                case "not_connected": return "Chưa kết nối tới máy chủ.";
                case "auth_failed": return "Xác thực phiên thất bại. Vui lòng đăng nhập lại.";
                case "schema_mismatch": return "Máy chủ và client lệch phiên bản hợp đồng.";
                case "revision_conflict": return "Dữ liệu đã thay đổi; đang hiển thị bản mới nhất từ máy chủ.";
                case "invalid_target": return "Mục tiêu không còn hợp lệ.";
                case "target_required": return "Cần chọn mục tiêu.";
                case "target_lost": return "Mục tiêu đã rời khỏi trạng thái có thể tấn công.";
                case "unsupported_skill": return "Kỹ năng này chưa được hỗ trợ.";
                case "invalid_input": return "Dữ liệu gửi không hợp lệ.";
                case "invalid_transition": return "Trạng thái hiện tại chưa cho phép thao tác này.";
                case "death_return_cooldown": return "Chưa thể hồi sinh, còn trong thời gian chờ.";
                case "death_return_disabled": return "Hồi sinh chưa được bật trên máy chủ.";
                case "quest_not_found": return "Không tìm thấy nhiệm vụ.";
                case "portal_not_found": return "Không tìm thấy cổng chuyển cảnh.";
                case "empty_response": return "Máy chủ trả về dữ liệu trống.";
                case "not_loaded": return "Dữ liệu chưa được tải.";
                case "not_equippable": return "Vật phẩm không thể trang bị.";
                case "wrong_location": return "Vật phẩm không ở đúng vị trí.";
                case "unknown_result": return "Máy chủ không trả kết quả.";
                default: return "Máy chủ báo: " + code + ".";
            }
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler != null) handler();
        }
    }
}
