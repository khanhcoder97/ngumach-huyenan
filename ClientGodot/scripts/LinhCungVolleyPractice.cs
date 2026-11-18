using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

public partial class LinhCungVolleyPractice : Node2D
{
    public const string SkillName = "Liên Châu";
    private const string ActionName = "volley";
    private const float Range = 150;
    private const int TargetHitLimit = 3;
    private static readonly int[] SpreadDegrees = { 0, -6, 6, -3, 3 };

    private sealed class Flight
    {
        public required LinhCungPractice.Effect Art { get; init; }
        public Vector2 RayOrigin, Tip, Velocity;
        public double Elapsed;
    }

    private readonly Dictionary<ulong, int> _hitCounts = new();
    private CharacterBody2D _hero = null!;
    private HeroAnimator _animator = null!;
    private Node2D[] _targets = null!;
    private Flight[] _flights = null!;
    private LinhCungPractice.Effect[] _nocks = null!;
    private Godot.Collections.Array<Rid> _excluded = null!;
    private Rect2 _icon;
    private Vector2 _aim, _firstMuzzle, _facing;
    private bool _active;
    private double _castTime;
    internal int Released { get; private set; }
    internal int Hits { get; private set; }
    internal int Capped { get; private set; }
    internal int Blocked { get; private set; }
    internal int Expired { get; private set; }
    internal int InFlight => _flights.Count(flight => flight.Art.Sprite.Visible);
    internal int NocksVisible => _nocks.Count(nock => nock.Sprite.Visible);
    internal bool Active => _active;
    public event Action<string, bool>? Feedback;
    public (Texture2D Texture, Rect2 Region) Icon => (_flights[0].Art.Sprite.Texture, _icon);

    internal void Configure(CharacterBody2D hero, HeroAnimator animator, Node2D[] targets, JsonElement effects)
    {
        _hero = hero;
        _animator = animator;
        _targets = targets;
        _excluded = new Godot.Collections.Array<Rid> { hero.GetRid() };
        var arrow = effects.GetProperty("volley_arrow");
        var nock = effects.GetProperty("volley_nock");
        var icon = arrow.GetProperty("iconRect");
        _icon = new Rect2(icon[0].GetSingle(), icon[1].GetSingle(), icon[2].GetSingle(), icon[3].GetSingle());
        _flights = new Flight[SpreadDegrees.Length];
        _nocks = new LinhCungPractice.Effect[SpreadDegrees.Length];
        for (int i = 0; i < _flights.Length; i++)
        {
            _flights[i] = new Flight { Art = new LinhCungPractice.Effect(this, arrow, 21, 3) };
            _nocks[i] = new LinhCungPractice.Effect(this, nock, 4, 4);
        }
        _animator.ActionReleased += Release;
    }

    internal bool TryCast(Vector2 aim, Vector2? targetPoint)
    {
        if (_active || !_animator.TryCast(ActionName)) return false;
        _facing = Vector2.Up.Rotated(_animator.ActionDirection * Mathf.Pi / 4);
        _firstMuzzle = _animator.FirstReleaseOffset(ActionName);
        var direction = targetPoint is { } target ? target - (_hero.GlobalPosition + _firstMuzzle) : aim;
        _aim = direction.LengthSquared() > 1e-4f ? direction.Normalized() : _facing;
        _active = true;
        _castTime = 0;
        Released = Hits = Capped = Blocked = Expired = 0;
        _hitCounts.Clear();
        return true;
    }

    private void Release(string action, Vector2 muzzle)
    {
        if (action != ActionName || !_active || Released >= _flights.Length) return;
        var flight = _flights[Released];
        var direction = _aim.Rotated(Mathf.DegToRad(SpreadDegrees[Released]));
        _nocks[Released].Sprite.Visible = false;
        flight.Elapsed = 0;
        flight.RayOrigin = _hero.GlobalPosition + new Vector2(0, muzzle.Y);
        flight.Tip = _hero.GlobalPosition + muzzle + direction * 2;
        flight.Velocity = direction * (Range / (float)flight.Art.Duration);
        flight.Art.Sprite.GlobalPosition = flight.Tip;
        flight.Art.Sprite.Rotation = direction.Angle();
        flight.Art.Sprite.ResetPhysicsInterpolation();
        flight.Art.Seek(0);
        flight.Art.Sprite.Visible = true;
        Released++;
    }

    public override void _Process(double delta)
    {
        if (!_active) return;
        _castTime += delta;
        if (_castTime < .07 || Released == _nocks.Length) return;
        var across = _facing.Orthogonal();
        var origin = _hero.GlobalPosition + _firstMuzzle - _facing * 4;
        for (int i = Released; i < _nocks.Length; i++)
        {
            var nock = _nocks[i];
            nock.Sprite.GlobalPosition = origin + across * ((i - 2) * 4);
            if (!nock.Sprite.Visible) nock.Sprite.ResetPhysicsInterpolation();
            nock.Sprite.Visible = true;
            nock.Seek(_castTime - .07);
        }
    }

    public override void _PhysicsProcess(double delta)
    {
        if (!_active) return;
        var space = GetWorld2D().DirectSpaceState;
        foreach (var flight in _flights)
        {
            if (!flight.Art.Sprite.Visible) continue;
            double step = Math.Min(delta, flight.Art.Duration - flight.Elapsed);
            var next = flight.Tip + flight.Velocity * (float)step;
            var query = PhysicsRayQueryParameters2D.Create(flight.RayOrigin, next,
                LinhCungPractice.TerrainLayer | LinhCungPractice.DummyLayer, _excluded);
            query.HitFromInside = true;
            var hit = space.IntersectRay(query);
            if (hit.Count > 0)
            {
                flight.Art.Sprite.Visible = false;
                if (hit["collider"].AsGodotObject() is Node2D target && _targets.Contains(target))
                {
                    ulong id = target.GetInstanceId();
                    int count = _hitCounts.GetValueOrDefault(id);
                    if (count >= TargetHitLimit) Capped++;
                    else
                    {
                        _hitCounts[id] = count + 1;
                        Hits++;
                    }
                }
                else Blocked++;
                continue;
            }
            flight.RayOrigin = flight.Tip = next;
            flight.Elapsed += step;
            flight.Art.Sprite.GlobalPosition = next;
            if (flight.Elapsed >= flight.Art.Duration)
            {
                flight.Art.Sprite.Visible = false;
                Expired++;
            }
            else flight.Art.Seek(flight.Elapsed);
        }
        if (Released != _flights.Length || InFlight > 0) return;
        _active = false;
        string detail = $"Liên Châu · {Hits}/5 trúng";
        if (Capped > 0) detail += Blocked > 0 ? $" · {Capped} dư" : $" · {Capped} vượt giới hạn";
        if (Blocked > 0) detail += $" · {Blocked} bị chặn";
        Feedback?.Invoke(detail, Hits > 0);
    }

    public override void _ExitTree() => _animator.ActionReleased -= Release;
}
