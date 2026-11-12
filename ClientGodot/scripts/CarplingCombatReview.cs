using Godot;
using System;
using System.Collections.Generic;

namespace Ngumach.VisualReboot;

/// <summary>Native source-art review; no encounter, damage, inventory or server state.</summary>
public partial class CarplingCombatReview : Control
{
    private ActorLibraryData _library = null!;
    private ActorLibrarySprite _sequence = null!;
    private Label _phase = null!;
    private double _clock;
    private bool _capture;
    private int _facing = 4;
    private string _actor = "MOB_CARPLING";
    private int _variant = 1;
    private string TellClip => $"telegraph_{_variant:00}";
    private string AttackClip => $"attack_{_variant:00}";
    private string RecoverClip => $"recovery_{_variant:00}";
    private Sprite2D? _rootCue;
    private ActorLibraryData.Direction? _rootCueFrames;
    private double Windup => ActorLibraryData.Duration(_actor, TellClip);
    private double Strike => ActorLibraryData.Duration(_actor, AttackClip);
    private double Recover => ActorLibraryData.Duration(_actor, RecoverClip);
    private readonly List<ActorLibrarySprite> _sprites = new();
    private readonly List<Action> _placements = new();
    private string[] Actions => _variant == 2 ? new[] { TellClip, AttackClip, RecoverClip } : new[] { TellClip, AttackClip, RecoverClip, "hurt", "death" };
    public override void _Ready()
    {
        Engine.MaxFps = 60; Theme = MoonGlassTheme.Create();
        _library = new ActorLibraryData(reviewMode: true);
        var args = OS.GetCmdlineUserArgs(); int direction = Array.IndexOf(args, "--combat-direction");
        int actorArg = Array.IndexOf(args, "--combat-actor");
        if (actorArg >= 0 && actorArg + 1 < args.Length)
        {
            _actor = args[actorArg + 1];
            if (_actor != "MOB_CARPLING" && _actor != "MOB_WATERROOT") { GD.PushError("Unsupported combat review actor"); GetTree().Quit(1); return; }
        }
        if (direction >= 0 && direction + 1 < args.Length)
        { int requested = Array.IndexOf(ArtStudioCodec.Directions, args[direction + 1]); if (requested >= 0 && requested < 8) _facing = requested; }
        int variant = Array.IndexOf(args, "--combat-variant");
        if (variant >= 0)
        {
            if (variant + 1 >= args.Length || !int.TryParse(args[variant + 1], out _variant) || _variant < 1 || _variant > 2 || (_variant == 2 && _actor != "MOB_WATERROOT"))
            { GD.PushError("Unsupported combat review variant"); GetTree().Quit(1); return; }
        }
        var bg = new ColorRect { Color = Color.FromHtml("#20243b"), MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(bg);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string edge in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + edge, 24);
        AddChild(margin); var stack = new VBoxContainer(); margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label(_library.Actors[_actor].Name.ToUpperInvariant() + " / KIỂM CHUỖI COMBAT", 24, MoonGlassTheme.Gold));
        var directions = new OptionButton();
        for (int i = 0; i < 8; i++) directions.AddItem(ArtStudioCodec.Directions[i] + (i >= 5 ? " · lật ảnh nguồn" : " · góc vẽ nguồn"));
        directions.Select(_facing); stack.AddChild(directions);
        directions.ItemSelected += i => { _facing = (int)i; foreach (var sprite in _sprites) { sprite.Facing = _facing; sprite.Restart(); } foreach (var place in _placements) place(); };
        stack.AddChild(MoonGlassTheme.Label("16 ảnh nguồn/động tác · xem theo hướng · nguồn chưa tự duyệt gameplay · ESC: đóng", 13));
        var grid = new GridContainer { Columns = _variant == 2 ? 2 : 3, SizeFlagsVertical = SizeFlags.ExpandFill }; stack.AddChild(grid);
        grid.AddThemeConstantOverride("h_separation", 18); grid.AddThemeConstantOverride("v_separation", 16);
        int standalone = Actions.Length;
        for (int i = 0; i <= standalone; i++)
        {
            var card = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 225) }; grid.AddChild(card);
            string action = i < standalone ? Actions[i] : TellClip;
            string title = i < standalone ? action + " · " + ActorLibraryData.Duration(_actor, action).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + " s" : $"NỐI BA PHA · {Windup:0.00} / {Strike:0.00} / {Recover:0.00} s";
            card.AddChild(MoonGlassTheme.Label(title, 16, MoonGlassTheme.Blue));
            var stage = new Control { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 170) }; card.AddChild(stage);
            var sprite = new ActorLibrarySprite { Library = _library, ActorId = _actor, Clip = action, Facing = _facing, DisplayHeight = _actor == "MOB_WATERROOT" ? 88 : 120, Loop = i < 3 };
            _sprites.Add(sprite); stage.AddChild(sprite);
            void Place() => sprite.Position = _actor == "MOB_WATERROOT" ? new Vector2(stage.Size.X * (_variant == 2 ? (_facing is 5 or 6 or 7 ? .65f : .35f) : .38f), stage.Size.Y * (_variant == 2 ? (_facing is 3 or 4 or 5 ? .44f : .74f) : .74f)) : stage.Size / 2;
            stage.Resized += Place; _placements.Add(Place); Place();
            if (!sprite.Available)
            {
                var missing = MoonGlassTheme.Label("CHƯA CÓ NGUỒN\nKhông thay bằng idle", 12, MoonGlassTheme.Muted);
                missing.Position = new Vector2(0, 75); missing.Size = new Vector2(300, 45); stage.AddChild(missing);
            }
            if (i == standalone)
            {
                _sequence = sprite; _phase = MoonGlassTheme.Label("", 13); card.AddChild(_phase);
                string cueId = _variant == 2 ? "sk_mob_waterroot_02_line_component" : "sk_mob_waterroot_01_ripple_component";
                if (_actor == "MOB_WATERROOT" && _library.Pages.TryGetValue(cueId, out var cue))
                {
                    _rootCueFrames = cue.Directions[0]; float width = 1;
                    foreach (var frame in _rootCueFrames.Frames) width = Math.Max(width, frame.Region.Size.X);
                    _rootCue = new Sprite2D { Texture = GD.Load<Texture2D>(_rootCueFrames.Frames[0].File), RegionEnabled = true, Centered = false,
                        TextureFilter = TextureFilterEnum.Nearest, Scale = Vector2.One * ((_variant == 2 ? 80 : 160) / width) };
                    stage.AddChild(_rootCue); sprite.ZIndex = 1;
                    stage.Resized += () => _rootCue.Position = sprite.Position; _rootCue.Position = sprite.Position;
                }
            }
            else card.AddChild(MoonGlassTheme.Label(i < 3 ? "Lặp riêng để soi pose; không phải nhịp AI." : "Một lần · giữ khung cuối", 12, MoonGlassTheme.Muted));
        }
        stack.AddChild(MoonGlassTheme.Label(_actor == "MOB_WATERROOT" ? (_variant == 2 ? "Chồi Đất: 0,70 s báo; 0,40/0,60 s đánh/hồi là timing review. Đường báo minh họa, không định tỷ lệ 4 m/hitbox." : "Rễ Nước: 0,70 s báo; 0,35/0,55 s đánh/hồi là timing review. Vòng chân chỉ báo lấy đà, không phải vùng hit.") : "0,45 s báo / 0,50 s hồi theo visual bible. 0,30 s đánh là timing thử, chỉnh được trong Studio; không quy định cửa sổ damage.", 12, MoonGlassTheme.Muted));
        stack.AddChild(MoonGlassTheme.Label("Review hình ảnh; video --fixed-fps 60 là xuất offline, không chứng nhận FPS gameplay. Góc còn thiếu không được thay bằng ảnh SOUTH.", 12, MoonGlassTheme.Muted));
        int capture = Array.IndexOf(args, "--combat-capture");
        if (Array.IndexOf(args, "--combat-self-test") >= 0) { SelfTest(); return; }
        if (capture >= 0 && capture + 1 < args.Length) Capture(args[capture + 1]);
    }
    public override void _Process(double delta)
    {
        if (_sequence == null) return;
        if (!_capture) _clock += delta; double t = _clock % (Windup + Strike + Recover + .75); string clip; double local;
        if (t < Windup) { clip = TellClip; local = t; }
        else if (t < Windup + Strike) { clip = AttackClip; local = t - Windup; }
        else if (t < Windup + Strike + Recover) { clip = RecoverClip; local = t - Windup - Strike; }
        else { clip = "idle"; local = t - Windup - Strike - Recover; }
        _sequence.Clip = clip; _sequence.Paused = true;
        _sequence.ManualFrame = Math.Clamp((int)(local / ActorLibraryData.Duration(_actor, clip) * 16), 0, 15);
        _phase.Text = clip + " · " + (_sequence.ManualFrame + 1) + "/16 · nghỉ sau chuỗi 0,75 s";
        if (_rootCue != null)
        {
            _rootCue.Visible = clip == TellClip;
            var frame = _rootCueFrames!.Frames[_sequence.ManualFrame];
            _rootCue.RegionRect = frame.Region; _rootCue.Offset = -frame.Pivot;
            if (_variant == 2)
            {
                float angle = Mathf.DegToRad(-90 + _facing * 45);
                _rootCue.Rotation = angle;
                _rootCue.Position = _sequence.Position + Vector2.FromAngle(angle) * 80;
            }
        }
    }
    public override void _UnhandledKeyInput(InputEvent ev)
    { if (ev is InputEventKey key && key.Pressed && key.Keycode == Key.Escape) GetTree().Quit(); }
    private void SelfTest()
    {
        try
        {
            if (_actor != "MOB_WATERROOT" || _rootCue == null || _rootCueFrames!.Frames.Length != 16) throw new Exception("root cue missing");
            _capture = true; int checks = 0;
            foreach (var sample in new[] { (0d, true, 0, TellClip), (Windup - .01, true, 15, TellClip), (Windup, false, 0, AttackClip), (Windup + Strike, false, 0, RecoverClip), (Windup + Strike + Recover, false, 0, "idle"), (Windup + Strike + Recover + .76, true, 0, TellClip) })
            {
                _clock = sample.Item1; _Process(0);
                if (_rootCue.Visible != sample.Item2 || (sample.Item2 && _sequence.ManualFrame != sample.Item3)) throw new Exception("cue phase leaked: " + sample.Item1);
                checks++;
                _sequence._Process(0);
                if (_sequence.Clip != sample.Item4 || !_library.Resolve(_actor, sample.Item4, _facing, out var direction)) throw new Exception("sequence used wrong phase");
                var expected = direction!.Frames[_sequence.ManualFrame];
                if (_sequence.DisplayedFrame != _sequence.ManualFrame || _sequence.RegionRect != expected.Region || _sequence.Texture?.ResourcePath != expected.File || Math.Abs(_sequence.Scale.Y - 88 / direction.Height) > .0001) throw new Exception("sequence render/source registration mismatch");
                checks++;
            }
            if (_variant == 2)
            {
                for (int facing = 0; facing < 8; facing++)
                {
                    _facing = facing; _clock = .3; _Process(0);
                    float expected = Mathf.DegToRad(-90 + facing * 45);
                    if (Math.Abs(_rootCue.Rotation - expected) > .0001 || _rootCue.Position.DistanceTo(_sequence.Position + Vector2.FromAngle(expected) * 80) > .001) throw new Exception("line cue heading/anchor drift");
                    checks++;
                }
            }
            GD.Print("ROOT_COMBAT_REVIEW_SELF_TEST PASS variant=" + _variant + " assertions=" + checks + " PRESENTATION_ONLY_NO_GAMEPLAY_HITBOX"); GetTree().Quit();
        }
        catch (Exception error) { GD.PushError("ROOT_COMBAT_REVIEW_SELF_TEST FAIL " + error); GetTree().Quit(1); }
    }
    private async void Capture(string path)
    {
        _capture = true; _clock = Windup - .02;
        foreach (var sprite in FindChildren("*", "Sprite2D", true, false))
            if (sprite is ActorLibrarySprite actor) { actor.Paused = true; actor.ManualFrame = actor.Clip == AttackClip ? 7 : actor.Clip == "hurt" ? 4 : 15; }
        for (int i = 0; i < 5; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        GD.Print($"COMBAT_CAPTURE_POSE clip={_sequence.Clip} manual={_sequence.ManualFrame} displayed={_sequence.DisplayedFrame} region={_sequence.RegionRect} scale={_sequence.Scale} texture={_sequence.Texture?.ResourcePath}");
        var result = GetViewport().GetTexture().GetImage().SavePng(path);
        GD.Print("CREATURE_COMBAT_CAPTURE " + _actor + " " + result + " STATIC_REVIEW_NOT_GAMEPLAY"); GetTree().Quit(result == Error.Ok ? 0 : 1);
    }
    public override void _ExitTree() => _library?.Dispose();
}
