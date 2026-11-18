using Godot;
using System;
using System.Text.Json;

namespace Ngumach.VisualReboot;

public partial class LinhCungFanPractice : Node2D
{
    public const string SkillName = "Tán Hoa";
    private const string ActionName = "fan";
    internal const float Range = 80;
    internal const float NearDistance = 16;
    private const float CosHalfAngle = .6427876f;
    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private Node2D[] _targets = null!;
    private Func<bool> _lowFx = null!;
    private Godot.Collections.Array<Rid> _excluded = null!;
    private LinhCungPractice.Effect _fan = null!, _fall = null!;
    private Vector2 _caster, _direction;
    private Rect2 _icon;
    private float _angleCorrection;
    private double _time, _fullAt, _fallAt;
    private bool _released;
    internal bool Active { get; private set; }
    internal bool Resolved { get; private set; }
    internal int NormalHits { get; private set; }
    internal int CloseHits { get; private set; }
    internal int Blocked { get; private set; }
    internal bool FanVisible => _fan.Sprite.Visible;
    internal bool LeavesVisible => _fall.Sprite.Visible;
    public event Action<string, bool>? Feedback;
    public (Texture2D Texture, Rect2 Region) Icon => (_fan.Sprite.Texture, _icon);

    internal void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D[] targets,
                            JsonElement effects, Func<bool> lowFx)
    {
        _hero = hero;
        _animator = animator;
        _targets = targets;
        _lowFx = lowFx;
        _excluded = new Godot.Collections.Array<Rid> { hero.GetRid() };
        var fan = effects.GetProperty("fan_open");
        _fullAt = fan.GetProperty("fullAt").GetDouble();
        _fallAt = fan.GetProperty("fallAt").GetDouble();
        _angleCorrection = Mathf.DegToRad(fan.GetProperty("angleCorrectionDegrees").GetSingle());
        var icon = fan.GetProperty("iconRect");
        _icon = new Rect2(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle());
        _fan = new LinhCungPractice.Effect(this, fan, Range, 2);
        _fan.Sprite.Scale *= new Vector2(1, fan.GetProperty("ratioY").GetSingle());
        _fall = new LinhCungPractice.Effect(this, effects.GetProperty("fan_fall"), 25, 2);
        _animator.ActionReleased += Release;
    }

    internal bool TryCast(Vector2 aim)
    {
        if (Active || !_animator.TryCast(ActionName)) return false;
        _direction = aim.LengthSquared() > 1e-4f ? aim.Normalized() :
            Vector2.Up.Rotated(_animator.ActionDirection * Mathf.Pi / 4);
        Active = true;
        _released = Resolved = false;
        NormalHits = CloseHits = Blocked = 0;
        return true;
    }

    private void Release(string action, Vector2 muzzle)
    {
        if (action != ActionName || !Active) return;
        _released = true;
        _time = 0;
        _caster = _hero.GlobalPosition;
        var start = _caster + muzzle + _direction * 2;
        _fan.Sprite.GlobalPosition = start;
        _fan.Sprite.Rotation = _direction.Angle() + _angleCorrection;
        _fan.Sprite.ResetPhysicsInterpolation();
        _fan.Seek(0);
        _fan.Sprite.Visible = true;
        _fall.Sprite.GlobalPosition = start + _direction * 40;
        _fall.Sprite.Rotation = _direction.Angle();
        _fall.Sprite.ResetPhysicsInterpolation();
    }

    internal static float HitScale(Vector2 direction, Vector2 offset)
    {
        float distance = offset.LengthSquared();
        if (distance > Range * Range) return 0;
        if (distance > 0 && direction.Dot(offset) < CosHalfAngle * Mathf.Sqrt(distance)) return 0;
        return distance < NearDistance * NearDistance ? .7f : 1;
    }

    private void Resolve()
    {
        Resolved = true;
        var space = GetWorld2D().DirectSpaceState;
        foreach (var target in _targets)
        {
            var offset = target.GlobalPosition - _caster;
            float scale = HitScale(_direction, offset);
            if (scale == 0) continue;
            var ray = PhysicsRayQueryParameters2D.Create(_caster, target.GlobalPosition, LinhCungPractice.TerrainLayer, _excluded);
            ray.HitFromInside = true;
            if (offset != Vector2.Zero && space.IntersectRay(ray).Count != 0) Blocked++;
            else if (scale < 1) CloseHits++;
            else NormalHits++;
        }

        int hits = NormalHits + CloseHits;
        string message = hits == 0 ? (Blocked > 0 ? "Tán Hoa · bị địa hình chặn" : "Tán Hoa · trượt") :
            NormalHits == 0 ? $"Tán Hoa · {CloseHits} trúng gần (105%)" :
            CloseHits == 0 ? $"Tán Hoa · {NormalHits} trúng (150%)" : $"Tán Hoa · {NormalHits} xa · {CloseHits} gần";
        Feedback?.Invoke(message, hits > 0);
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_released || !Active) return;
        _time += delta;
        if (!Resolved && _time >= _fullAt) Resolve();
        _fan.Sprite.Visible = _time < _fan.Duration;
        if (_fan.Sprite.Visible) _fan.Seek(_time);
        _fall.Sprite.Visible = !_lowFx() && _time >= _fallAt && _time < _fallAt + _fall.Duration;
        if (_fall.Sprite.Visible) _fall.Seek(_time - _fallAt);
        if (_time >= _fallAt + _fall.Duration) Active = false;
    }

    public override void _ExitTree() => _animator.ActionReleased -= Release;
}
