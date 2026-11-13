using Godot;
using System;
using System.Collections.Generic;
using System.Globalization;
using System.Linq;

namespace Ngumach.VisualReboot;

/// <summary>Native source transition inspection, with unapproved angles visibly labelled.</summary>
public partial class ActorLocomotionReview : Control
{
    private string Actor = "CLASS_ANH_DAO";
    private string[] Clips = { "idle", "walk", "idle", "basic_attack", "idle" };
    private double[] _durations = Array.Empty<double>();
    private double Cycle => _durations.Sum();
    private ActorLibraryData _library = null!;
    private readonly List<ActorLibrarySprite> _sprites = new();
    private readonly List<CanvasItem> _markers = new();
    private Label _readout = null!;
    private double _clock, _speed = 1;
    private bool _paused, _extended;
    private readonly record struct Sample(int Phase, string Clip, double Local);

    private Sample At(double clock)
    {
        double local = Math.Max(0, clock) % Cycle;
        if (Cycle - local < 1e-9) local = 0;
        for (int i = 0; i < Clips.Length; i++)
        {
            if (local + 1e-9 < _durations[i]) return new(i, Clips[i], Math.Max(0, local));
            local -= _durations[i];
        }
        return new(0, Clips[0], 0);
    }

    public override void _Ready()
    {
        Engine.MaxFps = 60; ProcessPriority = -1; Theme = MoonGlassTheme.Create();
        var args = OS.GetCmdlineUserArgs(); int actorArgument = Array.IndexOf(args, "--actor");
        if (actorArgument >= 0)
        {
            if (actorArgument + 1 >= args.Length) throw new ArgumentException("Missing mobility actor");
            Actor = args[actorArgument + 1];
        }
        if (Actor is not ("CLASS_ANH_DAO" or "CLASS_MINH_KIEM")) throw new ArgumentException("Unsupported mobility actor");
        _extended = Array.IndexOf(OS.GetCmdlineUserArgs(), "--mobility-review") >= 0;
        if (_extended) Clips = new[] { "idle", "walk", "run", "idle", "basic_attack", "basic_attack_02", "basic_attack_03", "idle", "interact", "idle" };
        _durations = Clips.Select(c => ActorLibraryData.Duration(Actor, c)).ToArray();
        _library = new ActorLibraryData(reviewMode: true);
        string actorName = _library.Actors[Actor].Name;
        var background = new ColorRect { Color = Color.FromHtml("#1d2639"), MouseFilter = MouseFilterEnum.Ignore };
        background.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(background);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string side in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + side, 20);
        AddChild(margin); var stack = new VBoxContainer(); margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label(actorName + (_extended ? " / CHẠY – COMBO BA NHÁT – TƯƠNG TÁC" : " / KIỂM NỐI ĐỨNG – ĐI – CHÉM THƯỜNG"), 22, MoonGlassTheme.Gold));
        stack.AddChild(MoonGlassTheme.Label(_extended ? "Đứng → đi → chạy → đứng → 3 nhát combo → đứng → tương tác → đứng · 8,84 s · mỗi clip 16 pose nguồn." : "Đứng 1,0 → đi 0,8 → đứng 1,0 → chém nhát 1 0,6 → đứng 1,0 s. Mỗi clip 16 pose nguồn.", 14));
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
            var card = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(220, 210) }; grid.AddChild(card);
            var stage = new Control { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(220, 160) }; card.AddChild(stage);
            var sprite = new ActorLibrarySprite { Library = _library, ActorId = Actor, Facing = facing, Clip = "idle", DisplayHeight = 100, Paused = true, Loop = false, ZIndex = 1 };
            stage.AddChild(sprite); _sprites.Add(sprite);
            var floor = new ColorRect { Color = Color.FromHtml("#40586b"), Size = new Vector2(160, 1), MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(floor);
            var root = new ColorRect { Color = MoonGlassTheme.Gold, Size = new Vector2(9, 1), ZIndex = 2, MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(root);
            var stem = new ColorRect { Color = MoonGlassTheme.Gold, Size = new Vector2(1, 9), ZIndex = 2, MouseFilter = MouseFilterEnum.Ignore }; stage.AddChild(stem);
            _markers.AddRange(new CanvasItem[] { floor, root, stem });
            Action place = () => { sprite.Position = new Vector2(stage.Size.X / 2, stage.Size.Y - 28); floor.Position = sprite.Position - new Vector2(80, 0); root.Position = sprite.Position - new Vector2(4, 0); stem.Position = sprite.Position - new Vector2(0, 4); };
            stage.Resized += () => place(); place();
            string label = ArtStudioCodec.Directions[facing] + (facing >= 5 ? " · lật ảnh" : " · góc nguồn");
            var sources = Clips.Distinct().Select(clip => SourcePage(clip, facing)).ToArray();
            bool held = sources.Any(p => p.VisualState == "HOLD"), pending = sources.Any(p => !p.Approved);
            if (held) label += " · HOLD"; else if (pending) label += " · CHỜ DUYỆT";
            card.AddChild(MoonGlassTheme.Label(label, 13, pending ? MoonGlassTheme.Gold : MoonGlassTheme.Muted));
        }
        stack.AddChild(MoonGlassTheme.Label(_extended ? "Mốc vàng = root ảnh, không phải mặt phẳng vật lý. Soi chân bay, tỉ lệ, tay/đao, combo và tương tác." : "Mốc vàng cố định: soi chân, kích thước đầu, tay/đao và đường nối clip; chém thường chỉ là nhát 1 của combo.", 13, MoonGlassTheme.Muted));
        stack.AddChild(MoonGlassTheme.Label("Review cho phép xem HOLD; không cấp quyền gameplay. Xuất offline 60 bước/s không đo FPS gameplay. ESC: đóng.", 12, MoonGlassTheme.Muted));
        if (Actor == "CLASS_MINH_KIEM")
        {
            bool usesUnarmedBase = new[] { "idle", "walk", "basic_attack" }.Any(clip => Enumerable.Range(0, 5).Any(facing => SourcePage(clip, facing).Status == "EXISTING_NATIVE_MOTION16"));
            stack.AddChild(MoonGlassTheme.Label(usesUnarmedBase
                ? "Còn clip nền cũ không cầm kiếm: cần sửa chuyển thế; chưa nghiệm thu class."
                : "Đang kiểm nguồn nền có kiếm mới; HOLD/chờ duyệt vẫn bị chặn ở chế độ chỉ dùng nguồn đã duyệt.", 12, MoonGlassTheme.Gold));
        }
        Apply();
        if (Array.IndexOf(OS.GetCmdlineUserArgs(), "--locomotion-self-test") >= 0) SelfTest();
    }

    private ActorLibraryData.Page SourcePage(string clip, int facing)
    {
        string source = facing >= 5 ? new[] { "SE", "E", "NE" }[facing - 5] : ArtStudioCodec.Directions[facing];
        string common = Actor.ToLowerInvariant() + "_" + clip;
        string id = common + "_" + source.ToLowerInvariant();
        if (_library.Pages.TryGetValue(id, out var page)) return page;
        // The three inherited Minh Kiem Motion16 pages contain all directions.
        return _library.Pages.TryGetValue(common, out page) ? page : throw new InvalidOperationException("Missing authored source: " + id);
    }

    private void Apply()
    {
        var sample = At(_clock);
        foreach (var sprite in _sprites)
        {
            if (sprite.Clip != sample.Clip) { sprite.Clip = sample.Clip; sprite.Restart(); }
            if (!_library.Resolve(Actor, sample.Clip, sprite.Facing, out var direction)) throw new InvalidOperationException("Missing locomotion angle");
            sprite.Seek(ActorLibraryData.FrameAt(Actor, sample.Clip, direction!, sample.Local, false)); sprite._Process(0);
        }
        _readout.Text = sample.Clip + " · " + (_sprites[0].DisplayedFrame + 1) + "/16 · " + (_clock % Cycle).ToString("0.00", CultureInfo.InvariantCulture) + " s";
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
            Check(Math.Abs(Cycle - (_extended ? 8.84 : 4.4)) < 1e-9, "sequence duration");
            double boundary = 0;
            for (int i = 0; i < Clips.Length; i++)
            {
                _clock = boundary; Apply(); Check(At(boundary).Phase == i, "phase boundary");
                foreach (var sprite in _sprites) Check(sprite.Clip == Clips[i] && sprite.DisplayedFrame == 0, "phase starts at source0");
                boundary += _durations[i];
            }
            Check(At(Cycle).Phase == 0 && At(Cycle).Local == 0, "sequence wraps");
            foreach (var sprite in _sprites)
            {
                var visited = Clips.Distinct().ToDictionary(c => c, _ => new HashSet<int>());
                for (int tick = 0; tick < (int)Math.Ceiling(Cycle * 60); tick++)
                {
                    var sample = At(tick / 60d);
                    Check(_library.Resolve(Actor, sample.Clip, sprite.Facing, out var direction), "missing source direction");
                    Check(Math.Abs(ActorLibraryData.Duration(Actor, sample.Clip, direction!) - _durations[sample.Phase]) < 1e-6, "source duration mismatch");
                    visited[sample.Clip].Add(ActorLibraryData.FrameAt(Actor, sample.Clip, direction!, sample.Local, false));
                }
                foreach (var frames in visited.Values) Check(frames.Count == 16, "60-step sequence skipped a source pose");
            }
            using var approved = new ActorLibraryData();
            IEnumerable<string> policyClips = _extended ? _library.Actors[Actor].Clips : Clips.Distinct();
            if (_extended) Check(_library.Actors[Actor].Clips.Length == 16, "canonical sixteen-action class scope");
            foreach (string clip in policyClips) foreach (int facing in Enumerable.Range(0, 8))
            {
                var source = SourcePage(clip, facing);
                Check(_library.Resolve(Actor, clip, facing, out var direction), "missing canonical source or permitted mirror");
                Check(direction!.Frames.Length == 16, "canonical action source count");
                Check(approved.Resolve(Actor, clip, facing, out _) == source.Approved, "source/mirror approval gate mismatch");
            }
            GD.Print("ACTOR_LOCOMOTION_SELF_TEST PASS actor=" + Actor + " profile=" + (_extended ? "MOBILITY" : "BASE") + " assertions=" + checks + " source timing/transition only; approval gates follow current source records"); GetTree().Quit();
        }
        catch (Exception error) { GD.PushError("ACTOR_LOCOMOTION_SELF_TEST FAIL " + error); GetTree().Quit(1); }
    }
}
