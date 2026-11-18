using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

public partial class LinhCungRainPractice : Node2D, IPracticeGroundAim
{
    public const string SkillName = "Bách Tiễn Quy Tông";
    public int Slot => 5;
    internal const float Radius = 6 * TopDownCamera.PixelsPerWorldUnit;
    private const float Range = 12 * TopDownCamera.PixelsPerWorldUnit;
    private const int WaveCount = 4;
    private const int TargetLimit = 8;
    private const double WaveSpacing = .20;
    private static readonly Vector2[] Pattern =
    {
        new(-.36f,-.27f), new(.31f,.21f), new(.19f,-.41f),
        new(-.62f,.21f), new(.52f,.43f), new(.60f,-.27f)
    };

    private sealed record Drop(Vector2 Site, float Altitude, LinhCungPractice.Effect Arrow, LinhCungPractice.Effect? Flecks);
    private readonly Drop[][] _waves = new Drop[WaveCount][];
    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private Node2D[] _targets = null!;
    private BenMuaEnvironment _terrain = null!;
    private Action<Vector2> _face = null!;
    private Func<bool> _lowFx = null!;
    private Line2D _cursor = null!, _activeBoundary = null!;
    private Node2D _zone = null!, _boostGlints = null!;
    private LinhCungPractice.Effect _ring = null!;
    private Rect2 _icon;
    private Vector2? _preview, _request;
    private double _clock, _warningTime, _contactOffset, _finishTime;
    public bool IsAiming { get; private set; }
    internal bool Active { get; private set; }
    internal bool WarningVisible => _ring.Sprite.Visible;
    internal bool BoostVisible => _boostGlints.Visible;
    internal bool Empowered { get; private set; }
    internal int WoodMarks { get; set; }
    internal int WavesApplied { get; private set; }
    internal int Hits { get; private set; }
    internal int VisibleArrows => _waves.Sum(wave => wave.Count(drop => drop.Arrow.Sprite.Visible));
    internal int FactorPerWave => Empowered ? 90 : 75;
    internal Vector2 Center => _zone.GlobalPosition;
    public event Action<string, bool>? Feedback;
    public (Texture2D Texture, Rect2 Region) Icon => (_ring.Sprite.Texture, _icon);

    internal void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D[] targets,
                            BenMuaEnvironment terrain, JsonElement effects, Action<Vector2> face, Func<bool> lowFx)
    {
        _hero = hero;
        _animator = animator;
        _targets = targets;
        _terrain = terrain;
        _face = face;
        _lowFx = lowFx;
        _zone = new Node2D { Name = "ArrowRainZone" };
        AddChild(_zone);
        var ring = effects.GetProperty("rain_ring");
        var arrow = effects.GetProperty("rain_arrow");
        var flecks = effects.GetProperty("rain_impact");
        _ring = new LinhCungPractice.Effect(_zone, ring, Radius * 2, 0);
        _ring.Sprite.Scale *= new Vector2(1, ring.GetProperty("ratioY").GetSingle());
        _warningTime = _ring.Duration;
        _contactOffset = arrow.GetProperty("contactAt").GetDouble();
        _finishTime = _warningTime + (WaveCount - 1) * WaveSpacing + _contactOffset + flecks.GetProperty("duration").GetDouble();
        var icon = ring.GetProperty("iconRect");
        _icon = new Rect2(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle());
        _cursor = MakeCircle(this);
        _activeBoundary = MakeCircle(_zone);
        _activeBoundary.DefaultColor = new Color(.77f, .68f, .30f, .7f);
        _boostGlints = new Node2D { Visible = false, ZIndex = 1 };
        _zone.AddChild(_boostGlints);
        for (int i = 0; i < 3; i++)
        {
            var normal = Vector2.FromAngle(Mathf.Tau * i / 3 - Mathf.Pi / 2);
            _boostGlints.AddChild(new Line2D
            {
                Points = new[] { normal * 27, normal * 36 },
                Width = 2.7f, DefaultColor = new Color(1, .88f, .53f), Antialiased = true
            });
        }
        for (int wave = 0; wave < WaveCount; wave++)
        {
            _waves[wave] = new Drop[Pattern.Length];
            for (int i = 0; i < Pattern.Length; i++)
            {
                var arrowArt = new LinhCungPractice.Effect(_zone, arrow, 24, 3);
                var debris = i < 2 ? new LinhCungPractice.Effect(_zone, flecks, 17, 2) : null;
                _waves[wave][i] = new Drop(Pattern[i].Rotated(.79f * wave) * Radius,
                                           38 + (i % 3) * 7, arrowArt, debris);
            }
        }
    }

    private static Line2D MakeCircle(Node2D parent)
    {
        var circle = new Line2D
        {
            Visible = false, Closed = true, Width = 1.6f, Antialiased = true, ZIndex = 1,
            Points = Enumerable.Range(0, 64).Select(i => Vector2.FromAngle(i * Mathf.Tau / 64) * Radius).ToArray()
        };
        parent.AddChild(circle);
        return circle;
    }

    public void ToggleAim()
    {
        if (CancelAim()) return;
        if (Active || _animator.IsAttacking)
        {
            Feedback?.Invoke("Chờ tuyệt kỹ hoặc động tác kết thúc.", false);
            return;
        }
        IsAiming = true;
        Feedback?.Invoke("Chọn tâm mưa tên trên mặt đất.", true);
    }

    public bool CancelAim()
    {
        if (!IsAiming) return false;
        IsAiming = false;
        _preview = _request = null;
        _cursor.Visible = false;
        return true;
    }

    public void SetPreview(Vector2? point) => _preview = point;
    public void RequestPlacement(Vector2 point)
    {
        if (IsAiming && _request == null) _request = point;
    }

    private bool CanPlace(Vector2 point) => LinhCungPractice.CanAimAtGround(_hero, _terrain, point, Range);

    private void Aim()
    {
        _cursor.Visible = _preview.HasValue;
        if (_preview is {} preview)
        {
            _cursor.GlobalPosition = preview;
            _cursor.DefaultColor = CanPlace(preview) ? Color.FromHtml("#b9ce8c") : Color.FromHtml("#dc8c89");
        }
        if (_request is not {} target) return;
        _request = null;
        if (!CanPlace(target))
        {
            Feedback?.Invoke("Tâm mưa tên bị chắn hoặc ngoài tầm.", false);
            return;
        }
        _face(target - _hero.GlobalPosition);
        if (!_animator.TryCast("rain"))
        {
            Feedback?.Invoke("Chờ động tác hiện tại kết thúc.", false);
            return;
        }
        CancelAim();
        _zone.GlobalPosition = target;
        _zone.ResetPhysicsInterpolation();
        _clock = 0;
        WavesApplied = Hits = 0;
        Empowered = WoodMarks >= 3;
        if (Empowered) WoodMarks -= 3;
        Active = _ring.Sprite.Visible = _activeBoundary.Visible = true;
        _boostGlints.Visible = Empowered;
        _ring.Seek(0);
        Feedback?.Invoke("Bách Tiễn · báo vùng 1,2 giây", true);
    }

    internal static IEnumerable<Node2D> TargetsInZone(IEnumerable<Node2D> targets, Vector2 center) =>
        targets.Where(target => center.DistanceSquaredTo(target.GlobalPosition) <= Radius * Radius)
               .OrderBy(target => center.DistanceSquaredTo(target.GlobalPosition)).Take(TargetLimit);

    public override void _PhysicsProcess(double delta)
    {
        if (IsAiming) Aim();
        else if (Active) Play(delta);
    }

    private void Play(double delta)
    {
        _clock += delta;
        _ring.Sprite.Visible = _clock < _warningTime - 1e-7;
        _boostGlints.Visible = Empowered && _ring.Sprite.Visible;
        if (_ring.Sprite.Visible)
        {
            _ring.Seek(_clock);
            return;
        }

        while (WavesApplied < WaveCount && _clock + 1e-7 >= _warningTime + WavesApplied * WaveSpacing + _contactOffset)
        {
            WavesApplied++;
            int hit = TargetsInZone(_targets, Center).Count();
            Hits += hit;
            Feedback?.Invoke($"Mưa tên · đợt {WavesApplied}/4 · {hit} trúng ({FactorPerWave}%)", hit > 0);
        }
        bool finished = _clock >= _finishTime - 1e-7;
        bool lowFx = _lowFx();
        for (int wave = 0; wave < WaveCount; wave++)
            DrawWave(_waves[wave], finished ? -1 : _clock - _warningTime - wave * WaveSpacing, lowFx);
        if (finished) Active = _activeBoundary.Visible = false;
    }

    private void DrawWave(Drop[] drops, double age, bool lowFx)
    {
        for (int i = 0; i < drops.Length; i++)
        {
            Drop drop = drops[i];
            bool shown = age >= 0 && age < drop.Arrow.Duration && (i < 3 || !lowFx);
            drop.Arrow.Sprite.Visible = shown;
            if (shown)
            {
                float lift = (float)(1 - Math.Min(1, age / _contactOffset));
                drop.Arrow.Sprite.Position = drop.Site + Vector2.Up * (drop.Altitude * lift);
                drop.Arrow.Seek(age);
            }
            if (drop.Flecks is not {} flecks) continue;
            double afterContact = age - _contactOffset;
            flecks.Sprite.Visible = !lowFx && afterContact >= 0 && afterContact < flecks.Duration;
            if (flecks.Sprite.Visible)
            {
                flecks.Sprite.Position = drop.Site;
                flecks.Seek(afterContact);
            }
        }
    }
}
