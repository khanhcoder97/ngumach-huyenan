using Godot;
using System;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Ground targeting, single-use trap state and a patrol for local practice.</summary>
public partial class LinhCungTrapPractice : Node2D
{
    public const string SkillName = "Dây Gai";
    private const float Radius = 2 * TopDownCamera.PixelsPerWorldUnit;
    private const float Range = 6 * TopDownCamera.PixelsPerWorldUnit;
    private const float PatrolSpeed = 32;
    private const double ArmedSeconds = 4, WarningSeconds = .45, SlowDuration = 2.5;
    private static readonly Color ReadyColor = new(.56f, .96f, .66f, .86f);
    private static readonly Color BlockedColor = new(.99f, .43f, .42f, .9f);

    internal enum Stage { Idle, Aiming, Windup, Seed, Growing, Armed, Retracting }
    internal Stage CurrentStage { get; private set; }
    internal int Placed { get; private set; }
    internal int Triggered { get; private set; }
    internal int Expired { get; private set; }
    internal double SlowSeconds { get; private set; }
    internal Vector2 GroundPoint => _trapRoot.GlobalPosition;
    public bool IsAiming => CurrentStage == Stage.Aiming;
    public CharacterBody2D Target { get; private set; } = null!;
    public event Action<string, bool>? Feedback;

    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private BenMuaEnvironment _terrain = null!;
    private Node2D _trapRoot = null!;
    private LinhCungPractice.Effect _patrol = null!, _seed = null!, _growth = null!, _armed = null!, _retract = null!;
    private Line2D _cursor = null!, _boundary = null!;
    private (Texture2D Texture, Rect2 Region) _icon;
    private Vector2 _patrolLeft, _patrolRight, _seedStart, _seedReleaseOffset;
    private Vector2? _requestedPoint, _previewPoint;
    private Action<Vector2> _face = null!;
    private bool _patrolEast = true;
    private double _patrolClock, _stageClock;
    public (Texture2D Texture, Rect2 Region) Icon => _icon;

    public void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D actors,
                          BenMuaEnvironment terrain, JsonElement effects, Action<Vector2> face)
    {
        _hero = hero;
        _animator = animator;
        _terrain = terrain;
        _face = face;
        _patrolLeft = terrain.Spawn + new Vector2(-114, 8);
        _patrolRight = terrain.Spawn + new Vector2(-34, 8);
        Target = new CharacterBody2D
        {
            Name = "WaterrootPatrol", Position = _patrolLeft, CollisionLayer = LinhCungPractice.DummyLayer,
            CollisionMask = LinhCungPractice.TerrainLayer, MotionMode = CharacterBody2D.MotionModeEnum.Floating
        };
        actors.AddChild(Target);
        Target.AddChild(new CollisionShape2D
        {
            Position = LinhCungPractice.TargetOffset, Shape = new CircleShape2D { Radius = 12 }
        });
        _patrol = new LinhCungPractice.Effect(Target, effects.GetProperty("patrol"), 42, 0);
        _patrol.Sprite.Visible = true;
        var label = new Label
        {
            Text = "Rễ Nước tuần tra", Position = new Vector2(-56, -59), Size = new Vector2(112, 20),
            HorizontalAlignment = HorizontalAlignment.Center, MouseFilter = Control.MouseFilterEnum.Ignore, ZIndex = 4
        };
        label.AddThemeFontSizeOverride("font_size", 11);
        label.AddThemeColorOverride("font_outline_color", new Color(.08f, .1f, .07f));
        label.AddThemeConstantOverride("outline_size", 4);
        Target.AddChild(label);

        _trapRoot = new Node2D { Name = "DayGai" };
        actors.AddChild(_trapRoot);
        _boundary = MakeRing(_trapRoot);
        _cursor = MakeRing(this);
        _cursor.ZIndex = 5;
        var seed = effects.GetProperty("trap_seed");
        _seed = new LinhCungPractice.Effect(_trapRoot, seed, Radius * .34f, 1);
        var offset = seed.GetProperty("releaseOffset");
        _seedReleaseOffset = new Vector2(offset[0].GetSingle(), offset[1].GetSingle()) * _seed.Sprite.Scale.X;
        _growth = new LinhCungPractice.Effect(_trapRoot, effects.GetProperty("trap_grow"), Radius * 2, 0);
        var armed = effects.GetProperty("trap_armed");
        _armed = new LinhCungPractice.Effect(_trapRoot, armed, Radius * 2, 0);
        _retract = new LinhCungPractice.Effect(_trapRoot, effects.GetProperty("trap_retract"), Radius * 2, 0);
        var icon = armed.GetProperty("iconRect");
        _icon = (_armed.Sprite.Texture, new Rect2(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle()));
        _animator.ActionReleased += Release;
    }

    private static Line2D MakeRing(Node2D parent)
    {
        var ring = new Line2D
        {
            Closed = true, Width = 1.3f, Visible = false, Antialiased = true, DefaultColor = ReadyColor,
            Points = Enumerable.Range(0, 40).Select(i => Vector2.FromAngle(i * Mathf.Tau / 40) * Radius).ToArray()
        };
        parent.AddChild(ring);
        return ring;
    }

    public void ToggleAim()
    {
        if (CancelAim()) return;
        if (CurrentStage != Stage.Idle || _animator.IsAttacking)
        {
            Feedback?.Invoke("Chờ bẫy hoặc động tác hiện tại kết thúc.", false);
            return;
        }
        SetStage(Stage.Aiming);
        Feedback?.Invoke("Chọn điểm đặt Dây Gai trên mặt đất.", true);
    }

    public bool CancelAim()
    {
        if (!IsAiming) return false;
        _requestedPoint = _previewPoint = null;
        _cursor.Visible = false;
        SetStage(Stage.Idle);
        return true;
    }

    public void SetPreview(Vector2? point) => _previewPoint = point;

    public void RequestPlacement(Vector2 point)
    {
        if (IsAiming && _requestedPoint == null) _requestedPoint = point;
    }

    private bool CanPlace(Vector2 point)
    {
        var from = _hero.GlobalPosition;
        float distance = from.DistanceSquaredTo(point);
        if (distance > Range * Range || !_terrain.IsWalkable(point)) return false;
        if (distance < 1) return true;
        var ray = PhysicsRayQueryParameters2D.Create(from, point, LinhCungPractice.TerrainLayer);
        ray.Exclude = new Godot.Collections.Array<Rid> { _hero.GetRid() };
        return GetWorld2D().DirectSpaceState.IntersectRay(ray).Count == 0;
    }

    private void UpdateAim()
    {
        _cursor.Visible = _previewPoint.HasValue;
        if (_previewPoint is {} preview)
        {
            _cursor.GlobalPosition = preview;
            _cursor.DefaultColor = CanPlace(preview) ? ReadyColor : BlockedColor;
        }
        if (_requestedPoint is not {} requested) return;
        _requestedPoint = null;
        if (!CanPlace(requested))
        {
            Feedback?.Invoke("Điểm đặt bị chắn hoặc ngoài tầm.", false);
            return;
        }
        _face(requested - _hero.GlobalPosition);
        if (!_animator.TryCast("trap"))
        {
            Feedback?.Invoke("Chờ động tác hiện tại kết thúc.", false);
            return;
        }
        _trapRoot.GlobalPosition = requested;
        _trapRoot.ResetPhysicsInterpolation();
        _cursor.Visible = false;
        _previewPoint = null;
        SetStage(Stage.Windup);
        Feedback?.Invoke("Dây Gai · đang đặt hạt", true);
    }

    private void Release(string action, Vector2 hand)
    {
        if (action != "trap" || CurrentStage != Stage.Windup) return;
        _seedStart = _hero.GlobalPosition + hand - GroundPoint - _seedReleaseOffset;
        _seed.Sprite.Position = _seedStart;
        _seed.Sprite.ResetPhysicsInterpolation();
        Show(_seed);
        SetStage(Stage.Seed);
        Placed++;
    }

    public override void _PhysicsProcess(double delta)
    {
        MovePatrol(delta);
        _stageClock += delta;
        switch (CurrentStage)
        {
            case Stage.Aiming:
                UpdateAim();
                break;
            case Stage.Seed:
                _seed.Sprite.Position = _seedStart.Lerp(Vector2.Zero, (float)Math.Min(1, _stageClock / .21));
                _seed.Seek(_stageClock);
                if (_stageClock >= _seed.Duration)
                {
                    _seed.Sprite.Visible = false;
                    Show(_growth);
                    _boundary.DefaultColor = ReadyColor;
                    _boundary.Visible = true;
                    SetStage(Stage.Growing);
                }
                break;
            case Stage.Growing:
                _growth.Seek(_stageClock);
                _boundary.Visible = _stageClock < WarningSeconds;
                if (_stageClock >= _growth.Duration)
                {
                    _growth.Sprite.Visible = false;
                    Show(_armed);
                    _boundary.DefaultColor = new Color(ReadyColor, .38f);
                    _boundary.Visible = true;
                    SetStage(Stage.Armed);
                    Feedback?.Invoke("Dây Gai đang chờ mục tiêu.", true);
                }
                break;
            case Stage.Armed:
                _armed.Seek(_stageClock % _armed.Duration);
                if (_stageClock >= ArmedSeconds - 1e-7)
                    Resolve(false);
                else if (GroundPoint.DistanceSquaredTo(Target.GlobalPosition) <= Radius * Radius)
                    Resolve(true);
                break;
            case Stage.Retracting:
                _retract.Seek(_stageClock);
                _retract.Sprite.Modulate = new Color(Colors.White, (float)Math.Clamp((_retract.Duration - _stageClock) / .1, 0, 1));
                if (_stageClock >= _retract.Duration)
                {
                    _retract.Sprite.Visible = false;
                    SetStage(Stage.Idle);
                }
                break;
        }
    }

    private void MovePatrol(double delta)
    {
        Vector2 destination = _patrolEast ? _patrolRight : _patrolLeft;
        Vector2 travel = destination - Target.Position;
        float speed = PatrolSpeed * (SlowSeconds > 0 ? .6f : 1);
        Target.Velocity = travel.LimitLength(speed * (float)delta) / (float)delta;
        var before = Target.Position;
        Target.MoveAndSlide();
        if (Target.Position.DistanceSquaredTo(before) > 1e-6f)
        {
            _patrolClock = (_patrolClock + delta * speed / PatrolSpeed) % _patrol.Duration;
            _patrol.Seek(_patrolClock, !_patrolEast);
        }
        if (Target.Position.DistanceSquaredTo(destination) < .25f || Target.GetSlideCollisionCount() != 0)
            _patrolEast = !_patrolEast;
        SlowSeconds = Math.Max(0, SlowSeconds - delta);
    }

    private void Resolve(bool hit)
    {
        _armed.Sprite.Visible = _boundary.Visible = false;
        _retract.Sprite.Modulate = Colors.White;
        Show(_retract);
        SetStage(Stage.Retracting);
        if (hit)
        {
            Triggered++;
            SlowSeconds = SlowDuration;
            Feedback?.Invoke("Dây Gai trúng · làm chậm Rễ Nước.", true);
        }
        else
        {
            Expired++;
            Feedback?.Invoke("Dây Gai hết hạn · thu gai.", true);
        }
    }

    private static void Show(LinhCungPractice.Effect effect)
    {
        effect.Seek(0);
        effect.Sprite.Visible = true;
    }

    private void SetStage(Stage stage)
    {
        CurrentStage = stage;
        _stageClock = 0;
    }

    public override void _ExitTree() => _animator.ActionReleased -= Release;
}
