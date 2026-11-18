using Godot;
using System;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>The local Bến Mưa archery practice. Contact comes from the
/// terrain/dummy ray cast. The scene has no access to online combat state.</summary>
public partial class LinhCungPractice : Node2D
{
    public const string AssetRoot = "res://assets/linh_cung_practice/";
    public const string SkillName = "Khóa Mạch";
    internal const uint TerrainLayer = 1;
    internal const uint DummyLayer = 2;
    private const float Range = 150;
    internal static readonly Vector2 TargetOffset = new(0, -16);

    internal sealed class Effect
    {
        public Sprite2D Sprite { get; }
        public double Duration { get; }
        private readonly (Rect2 Region, Vector2 Pivot)[] _frames;
        private int _shown = -1;

        public Effect(Node2D parent, JsonElement data, float size, int depth)
        {
            Duration = data.GetProperty("duration").GetDouble();
            var source = data.GetProperty("frames");
            string file = source[0].GetProperty("file").GetString()!;
            string path = file.StartsWith("res://", StringComparison.Ordinal) ? file : AssetRoot + file;
            var texture = GD.Load<Texture2D>(path) ?? throw new InvalidOperationException("Missing practice texture: " + path);
            _frames = source.EnumerateArray().Select(frame =>
            {
                var r = frame.GetProperty("rect");
                var p = frame.GetProperty("pivot");
                return (new Rect2(r[0].GetSingle(), r[1].GetSingle(), r[2].GetSingle(), r[3].GetSingle()),
                        new Vector2(p[0].GetSingle(), p[1].GetSingle()));
            }).ToArray();
            if (_frames.Length != 16) throw new InvalidOperationException("Practice effects require sixteen poses.");
            Sprite = new Sprite2D
            {
                RegionEnabled = true, Centered = false, Visible = false, ZIndex = depth,
                Texture = texture, TextureFilter = TextureFilterEnum.Nearest,
                Scale = Vector2.One * (size / data.GetProperty("sourceHeight").GetSingle())
            };
            parent.AddChild(Sprite);
            Seek(0);
        }

        public void Seek(double seconds, bool flip=false)
        {
            int phase = Math.Clamp((int)(seconds / Duration * _frames.Length), 0, _frames.Length - 1);
            if (phase == _shown && Sprite.FlipH == flip) return;
            _shown = phase;
            Sprite.FlipH = flip;
            Sprite.RegionRect = _frames[phase].Region;
            var pivot = _frames[phase].Pivot;
            if (flip) pivot.X = Sprite.RegionRect.Size.X - pivot.X;
            Sprite.Offset = -pivot;
        }
    }

    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private Effect _dummyArt = null!, _arrow = null!, _tail = null!, _mark = null!;
    private StaticBody2D _dummy = null!;
    private Node2D? _selectedTarget, _markedTarget;
    private Line2D _ring = null!;
    private Vector2 _aim, _velocity, _cursor;
    private Rect2 _icon;
    private Vector2? _castTarget;
    private double _flightTime, _dummyTime, _tailTime, _markTime;
    public bool Selected => _selectedTarget != null;
    public bool IsCasting => _animator.CurrentAction is "cast" or "trap" or "volley" or "fan";
    public LinhCungTrapPractice Trap { get; private set; } = null!;
    public LinhCungVolleyPractice Volley { get; private set; } = null!;
    public LinhCungFanPractice Fan { get; private set; } = null!;
    public bool LowFx { get; set; }
    public event Action<string, bool>? Feedback;
    internal bool ArrowVisible => _arrow.Sprite.Visible;
    internal bool MarkVisible => _mark.Sprite.Visible;
    internal int Releases { get; private set; }
    internal int Hits { get; private set; }
    internal int Misses { get; private set; }
    internal Vector2 TargetPoint => _dummy.GlobalPosition + TargetOffset;

    public void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D actors, Vector2 target,
                          BenMuaEnvironment environment, Action<Vector2> face)
    {
        _hero = hero;
        _animator = animator;
        using var manifest = JsonDocument.Parse(FileAccess.GetFileAsString(AssetRoot + "manifest.json"));
        var effects = manifest.RootElement.GetProperty("effects");
        _dummy = new StaticBody2D
        {
            Name = "Rễ Nước tập luyện", Position = target, CollisionLayer = DummyLayer, CollisionMask = 0
        };
        actors.AddChild(_dummy);
        _dummy.AddChild(new CollisionShape2D { Position = TargetOffset, Shape = new CircleShape2D { Radius = 12 } });
        _ring = new Line2D
        {
            Width = 1.4f, DefaultColor = Color.FromHtml("#e7c783"), Closed = true, Visible = true,
            Points = Enumerable.Range(0, 24).Select(i => Vector2.FromAngle(i * Mathf.Tau / 24) * new Vector2(21, 9)).ToArray()
        };
        AddChild(_ring);
        _selectedTarget = _dummy;
        _ring.GlobalPosition = _dummy.GlobalPosition;
        _dummyArt = new Effect(_dummy, effects.GetProperty("dummy"), 42, 0);
        _dummyArt.Sprite.Visible = true;
        var arrow = effects.GetProperty("arrow");
        var icon = arrow.GetProperty("iconRect");
        _icon = new Rect2(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle());
        _arrow = new Effect(this, arrow, 22, 2);
        _tail = new Effect(this, effects.GetProperty("tail"), 24, 3);
        _mark = new Effect(this, effects.GetProperty("mark"), 34, 2);
        Trap = new LinhCungTrapPractice();
        AddChild(Trap);
        Trap.Configure(hero, animator, actors, environment, effects, face);
        Volley = new LinhCungVolleyPractice();
        AddChild(Volley);
        var targets = new Node2D[] { _dummy, Trap.Target };
        Volley.Configure(hero, animator, targets, effects);
        Fan = new LinhCungFanPractice();
        AddChild(Fan);
        Fan.Configure(hero, animator, targets, effects, () => LowFx);
        _animator.ActionReleased += Release;
    }

    public (Texture2D Texture, Rect2 Region) Icon => (_arrow.Sprite.Texture, _icon);

    public Vector2 Aim(Vector2 fallback)
    {
        if (_selectedTarget == null) return fallback;
        var direction = _selectedTarget.GlobalPosition - _hero.GlobalPosition;
        return direction.LengthSquared() > 1 ? direction.Normalized() : fallback;
    }

    public bool SelectAt(Vector2 world)
    {
        var patrol = Trap.Target;
        Node2D target = TargetPoint.DistanceSquaredTo(world) <=
            (patrol.GlobalPosition + TargetOffset).DistanceSquaredTo(world) ? _dummy : patrol;
        if ((target.GlobalPosition + TargetOffset).DistanceSquaredTo(world) > 24 * 24) return false;
        _selectedTarget = target;
        _ring.GlobalPosition = target.GlobalPosition;
        _ring.Visible = true;
        Feedback?.Invoke(target == _dummy ? "Đã chọn bia Khóa Mạch" : "Đã chọn Rễ Nước tuần tra", true);
        return true;
    }

    public void ClearTarget() { _selectedTarget = null; _ring.Visible = false; }
    public bool TryVolley(Vector2 aim) => Volley.TryCast(aim, _selectedTarget?.GlobalPosition + TargetOffset);

    public bool TryCast(Vector2 aim)
    {
        if (_arrow.Sprite.Visible || !_animator.TryCast()) return false;
        _aim = aim.Normalized();
        _castTarget = _selectedTarget?.GlobalPosition + TargetOffset;
        return true;
    }

    private void Release(string action, Vector2 muzzle)
    {
        if (action != "cast") return;
        _cursor = _hero.GlobalPosition + muzzle;
        Vector2 direction = _aim;
        if (_castTarget is {} target && target.DistanceSquaredTo(_cursor) > 1)
            direction = (target - _cursor).Normalized();
        _velocity = direction * (float)(Range / _arrow.Duration);
        _flightTime = 0;
        _arrow.Sprite.GlobalPosition = _cursor;
        _arrow.Sprite.Rotation = direction.Angle();
        _arrow.Sprite.ResetPhysicsInterpolation();
        _arrow.Sprite.Visible = true;
        _arrow.Seek(0);
        Releases++;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_arrow.Sprite.Visible) return;
        double travelTime = Math.Min(delta, _arrow.Duration - _flightTime);
        var next = _cursor + _velocity * (float)travelTime;
        var query = PhysicsRayQueryParameters2D.Create(_cursor, next, TerrainLayer | DummyLayer);
        query.Exclude = new Godot.Collections.Array<Rid> { _hero.GetRid() };
        query.HitFromInside = true;
        var hit = GetWorld2D().DirectSpaceState.IntersectRay(query);
        if (hit.Count != 0)
        {
            _arrow.Sprite.Visible = false;
            var collider = hit["collider"].AsGodotObject();
            if (collider == _dummy || collider == Trap.Target)
                OnContact(hit["position"].AsVector2(), (Node2D)collider!);
            else
                OnMiss("Địa hình đã chặn mũi tên");
            return;
        }
        _cursor = next;
        _arrow.Sprite.GlobalPosition = _cursor;
        _flightTime += travelTime;
        _arrow.Seek(_flightTime);
        if (_flightTime >= _arrow.Duration) OnMiss("Mũi tên không chạm mục tiêu");
    }

    private void OnContact(Vector2 contact, Node2D target)
    {
        Hits++;
        _tail.Sprite.GlobalPosition = contact;
        _tail.Sprite.Rotation = _arrow.Sprite.Rotation;
        _tail.Sprite.ResetPhysicsInterpolation();
        _tail.Sprite.Visible = !LowFx;
        _tail.Seek(0);
        _tailTime = 0;
        _markedTarget = target;
        _mark.Sprite.GlobalPosition = target.GlobalPosition + TargetOffset;
        _mark.Sprite.ResetPhysicsInterpolation();
        _mark.Sprite.Visible = true;
        _mark.Seek(0);
        _markTime = 0;
        Feedback?.Invoke("Khóa Mạch đã chạm mục tiêu", true);
    }

    private void OnMiss(string reason)
    {
        _arrow.Sprite.Visible = false;
        Misses++;
        Feedback?.Invoke(reason, false);
    }

    public override void _Process(double delta)
    {
        _dummyTime = (_dummyTime + delta) % _dummyArt.Duration;
        _dummyArt.Seek(_dummyTime);
        if (_selectedTarget != null) _ring.GlobalPosition = _selectedTarget.GlobalPosition;
        if (_mark.Sprite.Visible && _markedTarget != null)
            _mark.Sprite.GlobalPosition = _markedTarget.GlobalPosition + TargetOffset;
        Advance(_tail, ref _tailTime, delta);
        Advance(_mark, ref _markTime, delta);
    }

    private static void Advance(Effect effect, ref double time, double delta)
    {
        if (!effect.Sprite.Visible) return;
        time += delta;
        effect.Sprite.Visible = time < effect.Duration;
        if (effect.Sprite.Visible) effect.Seek(time);
    }

    public override void _ExitTree() => _animator.ActionReleased -= Release;
}
