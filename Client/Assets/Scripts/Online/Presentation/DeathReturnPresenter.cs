// OPC-16 O4 — death-return presenter built on authoritative HP, never on a
// client "downed" flag. Cooldown comes from the server tick carried by the
// receipt/error; a replay never moves or heals the actor a second time.
// Owner: OpenCode.

using System;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class DeathReturnViewState
    {
        public int Hp { get; }
        public int MaxHp { get; }
        public bool IsDowned { get; }
        public bool CanRequest { get; }
        public bool HasPendingMutation { get; }
        public long? NextReturnAllowedAtTick { get; }
        public long? ServerTick { get; }
        public P1DeathReturnResultV1 Receipt { get; }
        public bool LastApplied { get; }
        public bool LastReplayed { get; }
        public string ErrorCode { get; }
        public string HintVi { get; }

        public DeathReturnViewState(
            int hp, int maxHp, bool isDowned, bool canRequest, bool hasPendingMutation,
            long? nextReturnAllowedAtTick, long? serverTick, P1DeathReturnResultV1 receipt,
            string errorCode)
        {
            Hp = hp;
            MaxHp = maxHp;
            IsDowned = isDowned;
            CanRequest = canRequest;
            HasPendingMutation = hasPendingMutation;
            NextReturnAllowedAtTick = nextReturnAllowedAtTick;
            ServerTick = serverTick;
            Receipt = receipt;
            LastApplied = receipt != null && receipt.applied;
            LastReplayed = receipt != null && receipt.replayed;
            ErrorCode = errorCode;
            HintVi = BuildHint();
        }

        public bool IsCooldownAt(long tick)
        {
            return NextReturnAllowedAtTick.HasValue && tick < NextReturnAllowedAtTick.Value;
        }

        private string BuildHint()
        {
            if (LastReplayed)
                return "Máy chủ đã xác nhận lần hồi sinh trước; không dịch chuyển lần hai.";
            if (!IsDowned) return "Bạn vẫn còn sống.";
            if (HasPendingMutation) return "Đang chờ máy chủ xác nhận hồi sinh.";
            if (NextReturnAllowedAtTick.HasValue &&
                (ErrorCode == "death_return_cooldown" ||
                 (ServerTick.HasValue && ServerTick.Value < NextReturnAllowedAtTick.Value)))
                return "Chưa thể hồi sinh. Thử lại sau tick " + NextReturnAllowedAtTick.Value + ".";
            if (CanRequest) return "Nhấn Hồi sinh để trở về điểm an toàn.";
            return "Chưa thể hồi sinh.";
        }
    }

    public sealed class DeathReturnPresenter
    {
        private readonly IP1DeathReturnAdapter _adapter;
        private DeathReturnViewState _view;
        private string _lastErrorCode;

        public DeathReturnViewState View => _view;
        public event Action OnChanged;

        public DeathReturnPresenter(IP1DeathReturnAdapter adapter)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            Refresh();
        }

        public DeathReturnViewState Refresh(long? serverTick = null)
        {
            var self = _adapter.Self;
            bool downed = self != null && self.hp <= 0;
            bool cooldown = serverTick.HasValue && _adapter.NextReturnAllowedAtTick.HasValue &&
                            serverTick.Value < _adapter.NextReturnAllowedAtTick.Value;
            bool canRequest = downed && !_adapter.HasPendingMutation &&
                              _adapter.ConnectionState == UIConnectionState.Ready && !cooldown;
            _view = new DeathReturnViewState(
                self != null ? self.hp : 0, self != null ? self.maxHp : 0,
                downed, canRequest, _adapter.HasPendingMutation,
                _adapter.NextReturnAllowedAtTick, serverTick,
                _adapter.LastDeathReturn, _lastErrorCode);
            Notify();
            return _view;
        }

        public async System.Threading.Tasks.Task<DeathReturnViewState> RequestReturnAsync(
            System.Threading.CancellationToken ct)
        {
            if (_view == null) Refresh();
            if (!_view.IsDowned)
            {
                _lastErrorCode = "not_downed";
                return Refresh(_view.ServerTick);
            }
            if (!_view.CanRequest)
            {
                _lastErrorCode = _adapter.HasPendingMutation ? "mutation_outcome_unknown" : "resync_required";
                return Refresh(_view.ServerTick);
            }

            var result = await _adapter.ReturnFromDeathAsync(ct);
            _lastErrorCode = result.Success ? null : result.Code;
            return Refresh(_view.ServerTick);
        }

        public void ClearError()
        {
            _lastErrorCode = null;
            Refresh(_view != null ? _view.ServerTick : null);
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler != null) handler();
        }
    }
}
