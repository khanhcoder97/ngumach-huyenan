// OPC-16 O4 — combat HUD read model: self vitals, target and skill cooldowns.
// The presenter only projects authoritative world/self state. Cooldown deadlines
// are the server-issued UTC strings; the presenter never starts or shortens a
// local cooldown, and never claims a hit before the server response.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Globalization;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class CombatTargetView
    {
        public string EntityId { get; }
        public string DisplayName { get; }
        public string Kind { get; }
        public string HealthState { get; }
        public string Availability { get; }
        public double X { get; }
        public double Y { get; }
        public int Hp { get; }
        public int MaxHp { get; }
        public bool Targetable { get; }
        public bool IsAlive { get; }
        public bool CanAttack { get; }
        public string HintVi { get; }

        internal CombatTargetView(
            string entityId, string displayName, string kind, string healthState, string availability,
            double x, double y, int hp, int maxHp, bool targetable, bool isAlive, bool canAttack, string hintVi)
        {
            EntityId = entityId;
            DisplayName = string.IsNullOrEmpty(displayName) ? entityId : displayName;
            Kind = kind;
            HealthState = healthState;
            Availability = availability;
            X = x;
            Y = y;
            Hp = hp;
            MaxHp = maxHp;
            Targetable = targetable;
            IsAlive = isAlive;
            CanAttack = canAttack;
            HintVi = hintVi;
        }

        public bool HasHealthBar { get { return MaxHp > 0; } }

        public double HealthRatio
        {
            get
            {
                if (MaxHp <= 0) return 0;
                double ratio = (double)Hp / MaxHp;
                return ratio < 0 ? 0 : (ratio > 1 ? 1 : ratio);
            }
        }
    }

    public sealed class SkillCooldownView
    {
        public string SkillId { get; }
        public string DisplayNameVi { get; }
        public bool Supported { get; }
        public bool CooldownKnown { get; }
        public string CooldownEndsAtUtc { get; }
        public bool IsOnCooldown { get; }
        public long? RemainingSeconds { get; }
        public string HintVi { get; }

        internal SkillCooldownView(
            string skillId, string displayNameVi, bool supported, bool cooldownKnown,
            string cooldownEndsAtUtc, bool isOnCooldown, long? remainingSeconds, string hintVi)
        {
            SkillId = skillId;
            DisplayNameVi = displayNameVi;
            Supported = supported;
            CooldownKnown = cooldownKnown;
            CooldownEndsAtUtc = cooldownEndsAtUtc;
            IsOnCooldown = isOnCooldown;
            RemainingSeconds = remainingSeconds;
            HintVi = hintVi;
        }
    }

    public sealed class CombatHudViewState
    {
        public UIConnectionState ConnectionState { get; }
        public string MapId { get; }
        public long ServerTick { get; }
        public long Revision { get; }
        public int Hp { get; }
        public int MaxHp { get; }
        public int Mp { get; }
        public int MaxMp { get; }
        public int SwordIntent { get; }
        public string SelectedTargetId { get; }
        public CombatTargetView Target { get; }
        public IReadOnlyList<SkillCooldownView> Skills { get; }
        public bool CanBasicAttack { get; }
        public bool HasPendingMutation { get; }
        public string ErrorCode { get; }
        public string HintVi { get; }

        internal CombatHudViewState(
            UIConnectionState connectionState, string mapId, long serverTick, long revision,
            int hp, int maxHp, int mp, int maxMp, int swordIntent,
            string selectedTargetId, CombatTargetView target, IReadOnlyList<SkillCooldownView> skills,
            bool canBasicAttack, bool hasPendingMutation, string errorCode, string hintVi)
        {
            ConnectionState = connectionState;
            MapId = mapId;
            ServerTick = serverTick;
            Revision = revision;
            Hp = hp;
            MaxHp = maxHp;
            Mp = mp;
            MaxMp = maxMp;
            SwordIntent = swordIntent;
            SelectedTargetId = selectedTargetId;
            Target = target;
            Skills = skills ?? Array.Empty<SkillCooldownView>();
            CanBasicAttack = canBasicAttack;
            HasPendingMutation = hasPendingMutation;
            ErrorCode = errorCode;
            HintVi = hintVi;
        }

        public bool IsReady { get { return ConnectionState == UIConnectionState.Ready && !HasPendingMutation; } }

        public SkillCooldownView GetSkill(string skillId)
        {
            if (string.IsNullOrEmpty(skillId)) return null;
            for (int i = 0; i < Skills.Count; i++)
                if (string.Equals(Skills[i].SkillId, skillId, StringComparison.Ordinal)) return Skills[i];
            return null;
        }
    }

    public sealed class CombatHudPresenter
    {
        // Cooldown key canonicalization: the server reports basic-attack cooldown
        // under action key "BASIC_ATTACK" (CombatV2Actions.BasicAttack) while the
        // v2 wire carries skillId=null for a basic swing. The client therefore
        // stores/reads the basic-attack deadline under "BASIC_ATTACK" (not skillId)
        // in P1ClientV2.ApplyCombatV2, and this presenter reads the same key.
        // Skills use their own skillId as the cooldown key on both sides.
        public const string BasicAttackId = "BASIC_ATTACK";
        public const string SkillOne = "SK-MK-01";
        public const string SkillTwo = "SK-MK-02";
        public const string SkillThree = "SK-MK-03";

        private static readonly string[] SupportedSkillIds = { SkillOne, SkillTwo, SkillThree };
        private static readonly string[] SkillOrder = { BasicAttackId, SkillOne, SkillTwo, SkillThree };

        private readonly IP1CombatHudAdapter _adapter;
        private readonly Func<DateTimeOffset> _utcNow;
        private string _selectedTargetId;
        private string _lastErrorCode;
        private CombatHudViewState _view;

        public CombatHudViewState View { get { return _view; } }
        public string SelectedTargetId { get { return _selectedTargetId; } }
        public string LastErrorCode { get { return _lastErrorCode; } }
        public event Action OnChanged;

        public CombatHudPresenter(IP1CombatHudAdapter adapter, Func<DateTimeOffset> utcNow = null)
        {
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            _utcNow = utcNow ?? (() => DateTimeOffset.UtcNow);
            Refresh();
        }

        public CombatHudViewState Refresh()
        {
            var worldV2 = _adapter.WorldV2;
            var worldV1 = _adapter.World;
            var self = worldV2 != null && worldV2.self != null
                ? worldV2.self
                : (_adapter.Self ?? (worldV1 != null ? worldV1.self : null));

            CombatTargetView target = null;
            if (!string.IsNullOrEmpty(_selectedTargetId))
            {
                target = ResolveTarget(_selectedTargetId);
                if (target == null || !target.CanAttack)
                {
                    _selectedTargetId = null;
                    target = null;
                    if (_lastErrorCode == null) _lastErrorCode = "target_lost";
                }
            }

            var skills = BuildSkills(worldV2 != null ? worldV2.serverTimeUtc : (worldV1 != null ? worldV1.serverTimeUtc : null));
            bool canBasicAttack = _adapter.UseWorldV2 && target != null && target.CanAttack &&
                                  _adapter.ConnectionState == UIConnectionState.Ready &&
                                  !_adapter.HasPendingMutation;

            _view = new CombatHudViewState(
                _adapter.ConnectionState,
                worldV2 != null ? worldV2.mapId : (worldV1 != null ? worldV1.mapId : null),
                worldV2 != null ? worldV2.serverTick : (worldV1 != null ? worldV1.serverTick : 0),
                worldV2 != null ? worldV2.revision : (worldV1 != null ? worldV1.revision : 0),
                self != null ? self.hp : 0,
                self != null ? self.maxHp : 0,
                self != null ? self.mp : 0,
                self != null ? self.maxMp : 0,
                self != null ? self.swordIntent : 0,
                _selectedTargetId, target, skills, canBasicAttack, _adapter.HasPendingMutation,
                _lastErrorCode, BuildHint(target));
            Notify();
            return _view;
        }

        // Passing null clears the selection. Invalid/dead targets are never kept as
        // an actionable target; the UI sees the explicit error instead.
        public CombatHudViewState SelectTarget(string entityId)
        {
            if (string.IsNullOrEmpty(entityId))
            {
                _selectedTargetId = null;
                _lastErrorCode = null;
                return Refresh();
            }
            var target = ResolveTarget(entityId);
            if (target == null || !target.CanAttack)
            {
                _selectedTargetId = null;
                _lastErrorCode = "invalid_target";
                return Refresh();
            }
            _selectedTargetId = entityId;
            _lastErrorCode = null;
            return Refresh();
        }

        public async Task<CombatHudViewState> BasicAttackAsync(double aimX, double aimY, CancellationToken ct)
        {
            if (!_adapter.UseWorldV2)
            {
                _lastErrorCode = "feature_unavailable";
                return Refresh();
            }
            var gate = CommandGate();
            if (gate != null)
            {
                _lastErrorCode = gate;
                return Refresh();
            }
            var target = ResolveTarget(_selectedTargetId);
            if (target == null || !target.CanAttack)
            {
                _lastErrorCode = string.IsNullOrEmpty(_selectedTargetId) ? "target_required" : "invalid_target";
                return Refresh();
            }
            if (!ValidAim(aimX, aimY))
            {
                _lastErrorCode = "invalid_input";
                return Refresh();
            }

            var result = await _adapter.BasicAttackAsync(target.EntityId, aimX, aimY, ct);
            _lastErrorCode = result.Success ? null : result.Code;
            return Refresh();
        }

        public async Task<CombatHudViewState> CastAsync(
            string skillId, double aimX, double aimY, CancellationToken ct)
        {
            if (Array.IndexOf(SupportedSkillIds, skillId) < 0)
            {
                _lastErrorCode = "unsupported_skill";
                return Refresh();
            }
            var gate = CommandGate();
            if (gate != null)
            {
                _lastErrorCode = gate;
                return Refresh();
            }
            if (!ValidAim(aimX, aimY))
            {
                _lastErrorCode = "invalid_input";
                return Refresh();
            }

            CombatTargetView target = null;
            if (skillId != SkillOne)
            {
                target = ResolveTarget(_selectedTargetId);
                if (target == null || !target.CanAttack)
                {
                    _lastErrorCode = string.IsNullOrEmpty(_selectedTargetId) ? "target_required" : "invalid_target";
                    return Refresh();
                }
            }

            var result = await _adapter.CastAsync(
                skillId, target == null ? null : target.EntityId, aimX, aimY, ct);
            _lastErrorCode = result.Success ? null : result.Code;
            return Refresh();
        }

        public void ClearError()
        {
            _lastErrorCode = null;
            Refresh();
        }

        private string CommandGate()
        {
            if (_adapter.HasPendingMutation) return "pending_mutation";
            if (_adapter.ConnectionState != UIConnectionState.Ready) return "resync_required";
            return null;
        }

        private static bool ValidAim(double aimX, double aimY)
        {
            return P1Wire.Finite(aimX) && P1Wire.Finite(aimY) &&
                   Math.Abs(aimX) <= 1 && Math.Abs(aimY) <= 1;
        }

        private CombatTargetView ResolveTarget(string entityId)
        {
            if (string.IsNullOrEmpty(entityId)) return null;
            var worldV2 = _adapter.WorldV2;
            if (worldV2 != null && worldV2.entities != null)
            {
                for (int i = 0; i < worldV2.entities.Length; i++)
                {
                    var entity = worldV2.entities[i];
                    if (entity == null || !string.Equals(entity.entityId, entityId, StringComparison.Ordinal)) continue;
                    bool alive = entity.healthState == "ALIVE" && entity.hp > 0;
                    bool hostile = entity.kind == "MOB" || entity.kind == "BOSS";
                    bool canAttack = entity.targetable && alive && hostile;
                    return new CombatTargetView(
                        entity.entityId, DisplayName(entity.entityId), entity.kind, entity.healthState,
                        entity.availability, entity.x, entity.y, entity.hp, entity.maxHp,
                        entity.targetable, alive, canAttack, TargetHint(alive, canAttack));
                }
            }

            var worldV1 = _adapter.World;
            if (worldV1 != null && worldV1.entities != null)
            {
                for (int i = 0; i < worldV1.entities.Length; i++)
                {
                    var entity = worldV1.entities[i];
                    if (entity == null || !string.Equals(entity.entityId, entityId, StringComparison.Ordinal)) continue;
                    bool targetable = entity.targetable == true;
                    bool alive = (entity.healthState == null || entity.healthState == "ALIVE") && entity.hp > 0;
                    bool hostile = entity.kind == "MOB" || entity.kind == "BOSS";
                    bool canAttack = targetable && alive && hostile;
                    return new CombatTargetView(
                        entity.entityId, DisplayName(entity.entityId), entity.kind, entity.healthState,
                        entity.availability, entity.x, entity.y, entity.hp, entity.maxHp,
                        targetable, alive, canAttack, TargetHint(alive, canAttack));
                }
            }
            return null;
        }

        private IReadOnlyList<SkillCooldownView> BuildSkills(string serverTimeUtc)
        {
            // The server clock is preferred when the snapshot carries it; otherwise the
            // injected UTC clock only formats the server-issued deadline. No local
            // cooldown is ever created from a cast attempt.
            var now = _utcNow();
            if (!string.IsNullOrEmpty(serverTimeUtc))
            {
                DateTimeOffset parsedServer;
                if (DateTimeOffset.TryParse(serverTimeUtc, CultureInfo.InvariantCulture,
                        DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out parsedServer))
                    now = parsedServer;
            }

            var result = new List<SkillCooldownView>(SkillOrder.Length);
            var cooldowns = _adapter.CooldownEndsAtUtc;
            for (int i = 0; i < SkillOrder.Length; i++)
            {
                string skillId = SkillOrder[i];
                string deadline = null;
                if (cooldowns != null) cooldowns.TryGetValue(skillId, out deadline);
                result.Add(BuildSkill(skillId, deadline, now));
            }
            return result;
        }

        private static SkillCooldownView BuildSkill(string skillId, string deadline, DateTimeOffset now)
        {
            string displayVi;
            bool supported;
            if (skillId == BasicAttackId) { displayVi = "Đánh thường"; supported = true; }
            else if (skillId == SkillOne) { displayVi = "Kỹ năng 1"; supported = true; }
            else if (skillId == SkillTwo) { displayVi = "Kỹ năng 2"; supported = true; }
            else { displayVi = "Kỹ năng 3"; supported = true; }

            if (string.IsNullOrEmpty(deadline))
                return new SkillCooldownView(skillId, displayVi, supported, true, null, false, null,
                    "Sẵn sàng theo trạng thái máy chủ.");

            DateTimeOffset endsAt;
            if (!DateTimeOffset.TryParse(deadline, CultureInfo.InvariantCulture,
                    DateTimeStyles.AdjustToUniversal | DateTimeStyles.AssumeUniversal, out endsAt))
                return new SkillCooldownView(skillId, displayVi, supported, false, deadline, false, null,
                    "Máy chủ gửi mốc hồi chiêu không hợp lệ; chờ xác nhận mới.");

            var remaining = endsAt - now;
            if (remaining <= TimeSpan.Zero)
                return new SkillCooldownView(skillId, displayVi, supported, true, deadline, false, 0,
                    "Hồi chiêu đã kết thúc theo máy chủ.");

            long seconds = (long)Math.Ceiling(remaining.TotalSeconds);
            return new SkillCooldownView(skillId, displayVi, supported, true, deadline, true, seconds,
                "Còn " + seconds.ToString(CultureInfo.InvariantCulture) + " giây hồi chiêu.");
        }

        private string BuildHint(CombatTargetView target)
        {
            if (!string.IsNullOrEmpty(_lastErrorCode)) return HintFor(_lastErrorCode);
            if (_adapter.HasPendingMutation) return "Đang chờ máy chủ xác nhận thao tác.";
            if (_adapter.ConnectionState != UIConnectionState.Ready)
                return "Cần đồng bộ lại với máy chủ trước khi chiến đấu.";
            if (target != null) return "Đã chọn " + target.DisplayName + ". " + target.HintVi;
            return "Chưa chọn mục tiêu.";
        }

        private static string HintFor(string code)
        {
            if (code == "target_required") return "Cần chọn mục tiêu trước.";
            if (code == "invalid_target") return "Mục tiêu không còn hợp lệ.";
            if (code == "target_lost") return "Mục tiêu đã rời khỏi trạng thái có thể tấn công.";
            if (code == "unsupported_skill") return "Kỹ năng này chưa được hỗ trợ.";
            if (code == "feature_unavailable") return "Chiến đấu v2 chưa được bật trên máy chủ.";
            if (code == "pending_mutation") return "Đang chờ máy chủ xác nhận thao tác trước.";
            if (code == "resync_required") return "Cần đồng bộ lại với máy chủ.";
            if (code == "invalid_input") return "Hướng tấn công không hợp lệ.";
            return "Máy chủ báo: " + code + ".";
        }

        private static string TargetHint(bool alive, bool canAttack)
        {
            if (!alive) return "Mục tiêu đã chết.";
            if (!canAttack) return "Mục tiêu không thể tấn công.";
            return "Có thể tấn công.";
        }

        private static string DisplayName(string entityId)
        {
            var npc = NpcContextMapping.Resolve(entityId);
            if (npc != null && !string.IsNullOrEmpty(npc.DisplayName) &&
                npc.DisplayName.IndexOf("UNRESOLVED", StringComparison.Ordinal) < 0)
                return npc.DisplayName;
            return entityId;
        }

        private void Notify()
        {
            var handler = OnChanged;
            if (handler != null) handler();
        }
    }
}
