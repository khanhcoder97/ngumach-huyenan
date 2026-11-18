using Godot;
using System;
using System.Text.Json;

namespace Ngumach.VisualReboot;

public partial class LinhCungRetreatPractice : Node2D
{
    public const string SkillName = "Phi Diệp";
    private const string ActionName = "retreat";
    internal const float RetreatDistance = 5 * TopDownCamera.PixelsPerWorldUnit;
    private const float ArrowRange = 8 * TopDownCamera.PixelsPerWorldUnit;

    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private Node2D[] _targets = null!;
    private Godot.Collections.Array<Rid> _excluded = null!;
    private LinhCungPractice.Effect _arrow = null!;
    private readonly LinhCungPractice.Effect[] _heels = new LinhCungPractice.Effect[2];
    private readonly double[] _heelTime = new double[2];
    private Rect2 _icon, _heelIcon;
    private Vector2 _aim, _tip, _rayOrigin;
    private double _startAt, _endAt, _elapsed, _flight;
    private bool _ownsMotion;
    internal bool Active => _ownsMotion || ArrowVisible || _heels[0].Sprite.Visible || _heels[1].Sprite.Visible;
    internal bool ArrowVisible => _arrow.Sprite.Visible;
    internal int MarksShown { get; private set; }
    internal int Releases { get; private set; }
    internal int Hits { get; private set; }
    internal bool BlockedRetreat { get; private set; }
    internal float DistanceMoved { get; private set; }
    internal Vector2 ShotDirection { get; private set; }
    public event Action<string, bool>? Feedback;
    public (Texture2D Texture, Rect2 Region) Icon => (_arrow.Sprite.Texture, _icon);
    public (Texture2D Texture, Rect2 Region) HeelIcon => (_heels[0].Sprite.Texture, _heelIcon);

    internal void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D[] targets, JsonElement effects)
    {
        _hero = hero;
        _animator = animator;
        _targets = targets;
        _excluded = new Godot.Collections.Array<Rid> { hero.GetRid() };
        var arrow = effects.GetProperty("retreat_arrow");
        var heel = effects.GetProperty("retreat_heel");
        _icon = ReadIcon(arrow.GetProperty("iconRect"));
        _heelIcon = ReadIcon(heel.GetProperty("iconRect"));
        _startAt = heel.GetProperty("retreatStartsAt").GetDouble();
        _endAt = heel.GetProperty("retreatEndsAt").GetDouble();
        _arrow = new LinhCungPractice.Effect(this, arrow, 23, 3);
        for (int i = 0; i < _heels.Length; i++) _heels[i] = new LinhCungPractice.Effect(this, heel, 12, 0);
        _animator.ActionReleased += Release;
    }

    private static Rect2 ReadIcon(JsonElement icon) =>
        new(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle());

    internal bool TryCast(Vector2 aim)
    {
        if (Active || !_animator.TryCast(ActionName, physicsDriven: true)) return false;
        _aim = aim.LengthSquared() > 1e-4f ? aim.Normalized() : Vector2.Up.Rotated(_animator.ActionDirection * Mathf.Pi / 4);
        _elapsed = 0;
        _ownsMotion = true;
        MarksShown = Releases = Hits = 0;
        BlockedRetreat = false;
        DistanceMoved = 0;
        ShotDirection = Vector2.Zero;
        return true;
    }

    internal bool StepHero(double delta)
    {
        if (!_ownsMotion) return false;
        double previous = _elapsed;
        _elapsed += delta;
        _hero.Velocity = Vector2.Zero;
        if (MarksShown == 0 && _elapsed >= _startAt) Stamp(0);
        float distance = RetreatDistance * (Progress(_elapsed) - Progress(previous));
        if (!BlockedRetreat && distance > 0)
        {
            Vector2 before = _hero.GlobalPosition;
            BlockedRetreat = _hero.MoveAndCollide(-_aim * distance) != null;
            DistanceMoved += before.DistanceTo(_hero.GlobalPosition);
        }
        _animator.AdvancePhysicsAction(delta);
        _ownsMotion = _animator.CurrentAction == ActionName;
        return true;
    }

    private float Progress(double elapsed)
    {
        float t = (float)Math.Clamp((elapsed - _startAt) / (_endAt - _startAt), 0, 1);
        return t * t * (3 - 2 * t);
    }

    private void Stamp(int index)
    {
        var effect = _heels[index];
        _heelTime[index] = 0;
        effect.Sprite.GlobalPosition = _hero.GlobalPosition + _aim.Orthogonal() * (index == 0 ? -3 : 3);
        effect.Sprite.Rotation = _aim.Angle();
        effect.Sprite.ResetPhysicsInterpolation();
        effect.Seek(0);
        effect.Sprite.Visible = true;
        MarksShown++;
    }

    private void Release(string action, Vector2 muzzle)
    {
        if (action != ActionName || !_ownsMotion || Releases > 0) return;
        Stamp(1);
        _rayOrigin = _hero.GlobalPosition + new Vector2(0, muzzle.Y);
        _tip = _hero.GlobalPosition + muzzle + _aim * 2;
        _flight = 0;
        ShotDirection = _aim;
        _arrow.Sprite.GlobalPosition = _tip;
        _arrow.Sprite.Rotation = _aim.Angle();
        _arrow.Sprite.ResetPhysicsInterpolation();
        _arrow.Seek(0);
        _arrow.Sprite.Visible = true;
        Releases++;
    }

    public override void _PhysicsProcess(double delta)
    {
        for (int i = 0; i < _heels.Length; i++)
        {
            var effect = _heels[i];
            if (!effect.Sprite.Visible) continue;
            _heelTime[i] += delta;
            effect.Sprite.Visible = _heelTime[i] < effect.Duration;
            if (effect.Sprite.Visible) effect.Seek(_heelTime[i]);
        }
        if (ArrowVisible) StepArrow(delta);
    }

    private void StepArrow(double delta)
    {
        double travelTime = Math.Min(delta, _arrow.Duration - _flight);
        var next = _tip + ShotDirection * (float)(ArrowRange * travelTime / _arrow.Duration);
        var query = PhysicsRayQueryParameters2D.Create(_rayOrigin, next,
            LinhCungPractice.TerrainLayer | LinhCungPractice.DummyLayer, _excluded);
        query.HitFromInside = true;
        var hit = GetWorld2D().DirectSpaceState.IntersectRay(query);
        if (hit.Count != 0)
        {
            var collider = hit["collider"].AsGodotObject();
            bool target = Array.Exists(_targets, item => item == collider);
            if (target) Hits++;
            FinishArrow(target ? "Phi Diệp · trúng (80%)" : "Phi Diệp · tên bị chặn", target);
            return;
        }
        _rayOrigin = _tip = next;
        _arrow.Sprite.GlobalPosition = next;
        _flight += travelTime;
        if (_flight >= _arrow.Duration) FinishArrow("Phi Diệp · tên trượt", false);
        else _arrow.Seek(_flight);
    }

    private void FinishArrow(string text, bool hit)
    {
        _arrow.Sprite.Visible = false;
        Feedback?.Invoke(text, hit);
    }

    public override void _ExitTree() => _animator.ActionReleased -= Release;
}
