using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Original source pixels only; fitted bounds include every pose/FX phase.</summary>
public sealed class SkillAssemblySourceBounds
{
    private readonly Dictionary<ActorLibraryData.Frame, Rect2> _bounds = new();
    public SkillAssemblySourceBounds(ActorLibraryData library)
    {
        using var json = JsonDocument.Parse(FileAccess.GetFileAsString(ActorLibraryData.Root + "pages.json"));
        foreach (var p in json.RootElement.GetProperty("pages").EnumerateArray())
        {
            var page = library.Pages[p.GetProperty("id").GetString()!]; int di = 0;
            foreach (var d in p.GetProperty("directions").EnumerateArray())
            {
                int fi = 0;
                foreach (var f in d.GetProperty("frames").EnumerateArray())
                {
                    var b = f.GetProperty("bounds");
                    _bounds[page.Directions[di].Frames[fi++]] = new Rect2(b[0].GetSingle(), b[1].GetSingle(), b[2].GetSingle() - b[0].GetSingle(), b[3].GetSingle() - b[1].GetSingle());
                }
                di++;
            }
        }
    }
    public Rect2 Visible(ActorLibraryData.Frame frame, bool flip)
    {
        Rect2 r = _bounds[frame]; Vector2 pivot = frame.Pivot;
        if (flip) { r.Position = new Vector2(frame.Region.Size.X - r.End.X, r.Position.Y); pivot.X = frame.Region.Size.X - pivot.X; }
        return new Rect2(r.Position - pivot, r.Size);
    }
    public static Rect2 Transform(Rect2 r, float scale, float angle, Vector2 origin)
    {
        var transform = new Transform2D(angle, Vector2.One * scale, 0, origin);
        var points = new[] { r.Position, r.Position + new Vector2(r.Size.X, 0), r.End, r.Position + new Vector2(0, r.Size.Y) }.Select(p => transform * p).ToArray();
        Vector2 low = points.Aggregate((a,b) => a.Min(b)), high = points.Aggregate((a,b) => a.Max(b)); return new Rect2(low, high-low);
    }
}

public partial class SkillAssemblyPane : Control
{
    private ActorLibraryData _library = null!;
    private SkillAssemblySourceBounds _bounds = null!;
    private SkillAssemblyProfile _profile = null!;
    private SkillAssemblyVariant _variant = null!;
    private ActorLibrarySprite _body = null!;
    private readonly List<(SkillAssemblyTrack Track, int Instance, Sprite2D Sprite)> _effects = new();
    private int _facing, _resource;
    private bool _lowFx;
    private double _clock;
    private float _scale = .6f;
    private Vector2 _origin;
    public bool Guides { get; set; } = true;
    public Rect2 WorldBounds { get; private set; }
    public int VisibleEffects => _effects.Count(e => e.Sprite.Visible);
    public int BodyFrame => _body.DisplayedFrame;
    public float BodyDisplayHeight => _body.DisplayHeight;
    public override void _Ready() { ClipContents = true; MouseFilter = MouseFilterEnum.Ignore; }

    public void Bind(ActorLibraryData library, SkillAssemblySourceBounds bounds, SkillAssemblyProfile profile, SkillAssemblyVariant variant, int facing, int resource, bool lowFx)
    {
        _library = library; _bounds = bounds; _profile = profile; _variant = variant; _facing = facing; _resource = resource; _lowFx = lowFx;
        if (_body == null) { _body = new ActorLibrarySprite { Library = library, Paused = true, Loop = false, ZIndex = 1 }; AddChild(_body); }
        _body.ActorId = profile.ActorId; _body.Facing = facing; _body.Restart();
        foreach (var e in _effects) { e.Sprite.Visible = false; e.Sprite.QueueFree(); } _effects.Clear();
        foreach (var t in variant.Tracks)
        for (int i = 0; i < (t.ResourceInstances ? resource : 1); i++)
        {
            var sprite = new Sprite2D { RegionEnabled = true, Centered = false, TextureFilter = TextureFilterEnum.Nearest, ZIndex = t.Z, Visible = false };
            AddChild(sprite); _effects.Add((t, i, sprite));
        }
        WorldBounds = Measure(); QueueRedraw();
    }
    private (Vector2 Extra, float Angle) Instance(SkillAssemblyTrack t, int instance)
    {
        float angle = (t.Rotation == "FACING" ? SkillAssemblySampler.Facings[_facing].Angle() : 0) + Mathf.DegToRad(t.Angle);
        if (!t.ResourceInstances) return (Vector2.Zero, angle);
        float petalAngle = instance * Mathf.Tau / Math.Max(1, _resource);
        return (Vector2.FromAngle(petalAngle) * t.ResourceRadius, angle + petalAngle);
    }
    private Rect2 Measure()
    {
        bool first = true; Rect2 result = default;
        void Include(Rect2 r) { result = first ? r : result.Merge(r); first = false; }
        var clips = new[] { _profile.BodyClip, "idle", _variant.OverrideClip }.Where(c => c != "").Distinct();
        foreach (string clip in clips)
        {
            if (!_library.Resolve(_profile.ActorId, clip, _facing, out var direction)) throw new InvalidOperationException("Thiếu góc body: " + clip);
            foreach (var frame in direction!.Frames)
            foreach (float travel in new[] { 0f, _variant.DashDistance })
                Include(SkillAssemblySourceBounds.Transform(_bounds.Visible(frame, direction.Flip), 140 / direction.Height, 0, SkillAssemblySampler.Facings[_facing] * travel));
        }
        foreach (var e in _effects)
        {
            if (_lowFx && e.Track.LowFxOptional) continue;
            var source = _library.Pages[e.Track.ComponentId].Directions[0]; var instance = Instance(e.Track, e.Instance);
            foreach (var frame in source.Frames)
            foreach (double time in new[] { e.Track.Start, e.Track.Start + e.Track.Duration })
                Include(SkillAssemblySourceBounds.Transform(_bounds.Visible(frame, false), e.Track.Size / source.Height, instance.Angle,
                    SkillAssemblySampler.Anchor(e.Track, _profile, _variant, _facing, time) + instance.Extra));
        }
        if (_variant.Tracks.Any(t => t.Anchor is "TARGET" or "TARGET_HP"))
        {
            Vector2 target = SkillAssemblySampler.Facings[_facing] * _profile.TargetDistance;
            Include(new Rect2(target + new Vector2(-23, -110), new Vector2(46, 120)));
        }
        return result.Grow(12);
    }
    public float SuggestedScale => Math.Min(.72f, Math.Min(Math.Max(1, Size.X-12)/WorldBounds.Size.X, Math.Max(1, Size.Y-12)/WorldBounds.Size.Y));
    public void Fit(float commonScale)
    {
        _scale = commonScale; _origin = Size / 2 - WorldBounds.GetCenter() * _scale;
        _body.DisplayHeight = 140 * _scale; _body.Restart(); RenderAt(_clock);
    }
    public void RenderAt(double clock)
    {
        if (_profile == null) return; _clock = clock;
        var body = SkillAssemblySampler.Body(_profile, _variant, clock);
        if (!_library.Resolve(_profile.ActorId, body.Clip, _facing, out var d)) throw new InvalidOperationException("Góc body không khả dụng.");
        _body.Clip = body.Clip; _body.ManualFrame = ActorLibraryData.FrameAt(_profile.ActorId, body.Clip, d!, body.Local, body.Clip == "idle");
        _body.Position = _origin + SkillAssemblySampler.Facings[_facing] * SkillAssemblySampler.Travel(_variant, clock) * _scale; _body._Process(0);
        foreach (var e in _effects)
        {
            var source = _library.Pages[e.Track.ComponentId].Directions[0]; int frame = SkillAssemblySampler.ComponentFrame(e.Track, source, clock);
            e.Sprite.Visible = frame >= 0 && !(_lowFx && e.Track.LowFxOptional);
            if (!e.Sprite.Visible) continue;
            var f = source.Frames[frame]; var instance = Instance(e.Track, e.Instance);
            e.Sprite.ZIndex = SkillAssemblySampler.Depth(e.Track, _facing);
            e.Sprite.Texture = _library.Texture(f.File); e.Sprite.RegionRect = f.Region; e.Sprite.Offset = -f.Pivot;
            e.Sprite.Scale = Vector2.One * _scale * e.Track.Size / source.Height; e.Sprite.Rotation = instance.Angle;
            e.Sprite.Position = _origin + (SkillAssemblySampler.Anchor(e.Track, _profile, _variant, _facing, clock) + instance.Extra) * _scale;
        }
        QueueRedraw();
    }
    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), Color.FromHtml("#25334a"));
        if (_profile == null || !Guides) return;
        Vector2 root = _origin + SkillAssemblySampler.Facings[_facing] * SkillAssemblySampler.Travel(_variant, _clock) * _scale;
        DrawLine(root-Vector2.Right*4, root+Vector2.Right*4, MoonGlassTheme.Gold, 1); DrawLine(root-Vector2.Down*4, root+Vector2.Down*4, MoonGlassTheme.Gold, 1);
        if (_variant.Tracks.Any(t => t.Anchor is "TARGET" or "TARGET_HP"))
        {
            Vector2 target = _origin + SkillAssemblySampler.Facings[_facing] * _profile.TargetDistance * _scale;
            DrawCircle(target, 5, MoonGlassTheme.Blue, false, 1);
            DrawRect(new Rect2(target + new Vector2(-20,-96)*_scale, new Vector2(40,3)*_scale), MoonGlassTheme.Hp);
        }
    }
}
