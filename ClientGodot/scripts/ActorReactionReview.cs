using Godot;
using System;
using System.Collections.Generic;
using System.Globalization;

namespace Ngumach.VisualReboot;

/// <summary>Authored source transition review only; never emits combat or respawn events.</summary>
public partial class ActorReactionReview : Control
{
    private const string Actor = "CLASS_MINH_KIEM";
    private static readonly string[] Clips = { "skill_04", "hurt", "dodge", "death" };
    private static readonly double[] Durations = { .8, .3, .48, 1.2 };
    private const double DeathHold = .4, Cycle = 3.18;
    private ActorLibraryData _library = null!;
    private readonly List<ActorLibrarySprite> _sprites = new();
    private readonly List<CanvasItem> _markers = new();
    private Label _readout = null!;
    private double _clock, _speed = 1;
    private bool _paused;
    private readonly record struct Sample(int Index, string Clip, double Local, bool Hold);

    private static Sample At(double clock)
    {
        double local = Math.Max(0, clock) % Cycle;
        if (Cycle - local < 1e-9) local = 0;
        for (int phase = 0; phase < Clips.Length; phase++)
        {
            if (local + 1e-9 < Durations[phase]) return new(phase, Clips[phase], Math.Max(0, local), false);
            local -= Durations[phase];
        }
        return new(3, "death", Durations[3] + Math.Max(0, local), true);
    }

    public override void _Ready()
    {
        Engine.MaxFps = 60; ProcessPriority = -1; Theme = MoonGlassTheme.Create();
        _library = new ActorLibraryData(reviewMode: true);
        var background = new ColorRect { Color = Color.FromHtml("#1d2639"), MouseFilter = MouseFilterEnum.Ignore };
        background.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(background);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string edge in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + edge, 20);
        AddChild(margin); var stack = new VBoxContainer(); margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label("MINH KIẾM / KIỂM NỐI PHẢN ỨNG TÁM HƯỚNG", 22, MoonGlassTheme.Gold));
        stack.AddChild(MoonGlassTheme.Label("Thiết Y 0,80 → bị đánh 0,30 → né 0,48 → ngã 1,20 → giữ nằm 0,40 s", 14));
        var controls = new HBoxContainer(); stack.AddChild(controls);
        var pause = new Button { Text = "Tạm dừng" }; controls.AddChild(pause);
        pause.Pressed += () => { _paused = !_paused; pause.Text = _paused ? "Phát tiếp" : "Tạm dừng"; };
        var restart = new Button { Text = "Phát từ đầu" }; controls.AddChild(restart); restart.Pressed += () => { _clock = 0; Apply(); };
        var speed = new SpinBox { MinValue = .1, MaxValue = 2, Step = .1, Value = 1, Prefix = "Tốc độ × ", CustomMinimumSize = new Vector2(155, 0) };
        controls.AddChild(speed); speed.ValueChanged += value => _speed = value;
        var markers = new Button { Text = "Ẩn mốc chân", ToggleMode = true }; controls.AddChild(markers);
        markers.Toggled += hidden => { foreach (var marker in _markers) marker.Visible = !hidden; markers.Text = hidden ? "Hiện mốc chân" : "Ẩn mốc chân"; };
        _readout = MoonGlassTheme.Label("", 14, MoonGlassTheme.Blue); controls.AddChild(_readout);
        var grid = new GridContainer { Columns = 4, SizeFlagsVertical = SizeFlags.ExpandFill }; stack.AddChild(grid);
        grid.AddThemeConstantOverride("h_separation", 12); grid.AddThemeConstantOverride("v_separation", 10);
        for (int facing = 0; facing < 8; facing++)
        {
            var card = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(220, 220) }; grid.AddChild(card);
            var stage = new Control { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(220, 175) }; card.AddChild(stage);
            var sprite = new ActorLibrarySprite { Library = _library, ActorId = Actor, Facing = facing, Clip = Clips[0], DisplayHeight = 110, Paused = true, Loop = false, ZIndex = 1 };
            stage.AddChild(sprite); _sprites.Add(sprite);
            var floor = new ColorRect { Color = Color.FromHtml("#40586b"), Size = new Vector2(160, 1), MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(floor);
            var root = new ColorRect { Color = MoonGlassTheme.Gold, Size = new Vector2(9, 1), ZIndex = 2, MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(root);
            var stem = new ColorRect { Color = MoonGlassTheme.Gold, Size = new Vector2(1, 9), ZIndex = 2, MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(stem);
            _markers.AddRange(new CanvasItem[] { floor, root, stem });
            Action place = () => { sprite.Position = new Vector2(stage.Size.X / 2, stage.Size.Y - 28); floor.Position = sprite.Position - new Vector2(80, 0); root.Position = sprite.Position - new Vector2(4, 0); stem.Position = sprite.Position - new Vector2(0, 4); };
            stage.Resized += () => place(); place();
            card.AddChild(MoonGlassTheme.Label(ArtStudioCodec.Directions[facing] + (facing >= 5 ? " · lật ảnh" : " · góc nguồn"), 14, MoonGlassTheme.Muted));
        }
        stack.AddChild(MoonGlassTheme.Label("Chấm vàng = root cố định; soi chân, tỉ lệ, tay và kiếm lúc nối clip. Nguồn chưa thay renderer gameplay.", 13, MoonGlassTheme.Muted));
        stack.AddChild(MoonGlassTheme.Label("Chu kỳ lặp là công cụ review, không phải hồi sinh hoặc i-frame. Movie Maker 60 bước/s là xuất offline, không đo FPS gameplay. ESC: đóng.", 12, MoonGlassTheme.Muted));
        Apply();
        if (Array.IndexOf(OS.GetCmdlineUserArgs(), "--reaction-self-test") >= 0) SelfTest();
    }

    private void Apply()
    {
        var sample = At(_clock);
        foreach (var sprite in _sprites)
        {
            bool changed = sprite.Clip != sample.Clip;
            if (changed) { sprite.Clip = sample.Clip; sprite.Restart(); }
            if (!_library.Resolve(Actor, sample.Clip, sprite.Facing, out var direction)) throw new InvalidOperationException("Missing reaction source: " + sample.Clip);
            int frame = ActorLibraryData.FrameAt(Actor, sample.Clip, direction!, sample.Local, false);
            if (changed || sprite.ManualFrame != frame) sprite.Seek(frame);
            sprite._Process(0);
        }
        _readout.Text = sample.Clip + (sample.Hold ? " · giữ nằm" : " · khung " + (_sprites[0].DisplayedFrame + 1) + "/16") + " · " + (_clock % Cycle).ToString("0.00", CultureInfo.InvariantCulture) + " s";
    }

    public override void _Process(double delta) { if (!_paused) _clock += delta * _speed; Apply(); }
    public override void _UnhandledKeyInput(InputEvent @event) { if (@event.IsActionPressed("ui_cancel")) GetTree().Quit(); }
    public override void _ExitTree() => _library?.Dispose();

    private void SelfTest()
    {
        int checks = 0;
        try
        {
            void Check(bool value, string reason) { if (!value) throw new Exception(reason); checks++; }
            Check(Math.Abs(Durations[0] + Durations[1] + Durations[2] + Durations[3] + DeathHold - Cycle) < 1e-9, "cycle duration");
            foreach (var probe in new[] { (0d, "skill_04", 0), (.8, "hurt", 0), (1.1, "dodge", 0), (1.58, "death", 0), (2.78, "death", 15), (3.179, "death", 15), (3.18, "skill_04", 0) })
            {
                _clock = probe.Item1; Apply();
                foreach (var sprite in _sprites) Check(sprite.Clip == probe.Item2 && sprite.DisplayedFrame == probe.Item3, "phase boundary or held death restarted");
            }
            Check(At(2.78).Hold && At(3.179).Hold && !At(Cycle).Hold, "hold/cycle boundary");
            foreach (var sprite in _sprites)
            {
                var visited = new Dictionary<string, HashSet<int>>(); foreach (string clip in Clips) visited.Add(clip, new());
                for (int tick = 0; tick < Math.Ceiling(Cycle * 60); tick++)
                {
                    var phase = At(tick / 60d);
                    Check(_library.Resolve(Actor, phase.Clip, sprite.Facing, out var d), "missing angle");
                    Check(Math.Abs(ActorLibraryData.Duration(Actor, phase.Clip, d!) - Durations[phase.Index]) < 1e-6, "source/sequence duration mismatch");
                    visited[phase.Clip].Add(ActorLibraryData.FrameAt(Actor, phase.Clip, d!, phase.Local, false));
                }
                foreach (var frames in visited.Values) Check(frames.Count == 16, "60-step chain skipped a source pose");
            }
            GD.Print("ACTOR_REACTION_SELF_TEST PASS assertions=" + checks + " visual transitions only; no combat/respawn authority"); GetTree().Quit();
        }
        catch (Exception error) { GD.PushError("ACTOR_REACTION_SELF_TEST FAIL " + error); GetTree().Quit(1); }
    }
}
