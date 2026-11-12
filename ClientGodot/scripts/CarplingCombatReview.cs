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
    private Sprite2D? _rootCue;
    private ActorLibraryData.Direction? _rootCueFrames;
    private double Windup => ActorLibraryData.Duration(_actor, "telegraph_01");
    private double Strike => ActorLibraryData.Duration(_actor, "attack_01");
    private double Recover => ActorLibraryData.Duration(_actor, "recovery_01");
    private readonly List<ActorLibrarySprite> _sprites = new();
    private static readonly string[] Actions = { "telegraph_01", "attack_01", "recovery_01", "hurt", "death" };
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
        var bg = new ColorRect { Color = Color.FromHtml("#20243b"), MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(bg);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string edge in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + edge, 24);
        AddChild(margin); var stack = new VBoxContainer(); margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label(_library.Actors[_actor].Name.ToUpperInvariant() + " / KIỂM CHUỖI COMBAT", 24, MoonGlassTheme.Gold));
        var directions = new OptionButton();
        for (int i = 0; i < 8; i++) directions.AddItem(ArtStudioCodec.Directions[i] + (i >= 5 ? " · lật ảnh nguồn" : " · góc vẽ nguồn"));
        directions.Select(_facing); stack.AddChild(directions);
        directions.ItemSelected += i => { _facing = (int)i; foreach (var sprite in _sprites) { sprite.Facing = _facing; sprite.Restart(); } };
        stack.AddChild(MoonGlassTheme.Label("16 ảnh nguồn/động tác · xem theo hướng · nguồn chưa tự duyệt gameplay · ESC: đóng", 13));
        var grid = new GridContainer { Columns = 3, SizeFlagsVertical = SizeFlags.ExpandFill }; stack.AddChild(grid);
        grid.AddThemeConstantOverride("h_separation", 18); grid.AddThemeConstantOverride("v_separation", 16);
        for (int i = 0; i < 6; i++)
        {
            var card = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 225) }; grid.AddChild(card);
            string action = i < 5 ? Actions[i] : "telegraph_01";
            string title = i < 5 ? action + " · " + ActorLibraryData.Duration(_actor, action).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + " s" : $"NỐI BA PHA · {Windup:0.00} / {Strike:0.00} / {Recover:0.00} s";
            card.AddChild(MoonGlassTheme.Label(title, 16, MoonGlassTheme.Blue));
            var stage = new Control { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 170) }; card.AddChild(stage);
            var sprite = new ActorLibrarySprite { Library = _library, ActorId = _actor, Clip = action, Facing = _facing, DisplayHeight = _actor == "MOB_WATERROOT" ? 88 : 120, Loop = i < 3 };
            _sprites.Add(sprite); stage.AddChild(sprite);
            void Place() => sprite.Position = _actor == "MOB_WATERROOT" ? new Vector2(stage.Size.X * .38f, stage.Size.Y * .74f) : stage.Size / 2;
            stage.Resized += Place; Place();
            if (!sprite.Available)
            {
                var missing = MoonGlassTheme.Label("CHƯA CÓ NGUỒN\nKhông thay bằng idle", 12, MoonGlassTheme.Muted);
                missing.Position = new Vector2(0, 75); missing.Size = new Vector2(300, 45); stage.AddChild(missing);
            }
            if (i == 5)
            {
                _sequence = sprite; _phase = MoonGlassTheme.Label("", 13); card.AddChild(_phase);
                if (_actor == "MOB_WATERROOT" && _library.Pages.TryGetValue("sk_mob_waterroot_01_ripple_component", out var cue))
                {
                    _rootCueFrames = cue.Directions[0]; float width = 1;
                    foreach (var frame in _rootCueFrames.Frames) width = Math.Max(width, frame.Region.Size.X);
                    _rootCue = new Sprite2D { Texture = GD.Load<Texture2D>(_rootCueFrames.Frames[0].File), RegionEnabled = true, Centered = false,
                        TextureFilter = TextureFilterEnum.Nearest, Scale = Vector2.One * (160 / width) };
                    stage.AddChild(_rootCue); sprite.ZIndex = 1;
                    stage.Resized += () => _rootCue.Position = sprite.Position; _rootCue.Position = sprite.Position;
                }
            }
            else card.AddChild(MoonGlassTheme.Label(i < 3 ? "Lặp riêng để soi pose; không phải nhịp AI." : "Một lần · giữ khung cuối", 12, MoonGlassTheme.Muted));
        }
        stack.AddChild(MoonGlassTheme.Label(_actor == "MOB_WATERROOT" ? "Rễ Nước: 0,70 s báo; 0,35/0,55 s đánh/hồi là timing review. Vòng chân chỉ báo lấy đà, không phải vùng hit." : "0,45 s báo / 0,50 s hồi theo visual bible. 0,30 s đánh là timing thử, chỉnh được trong Studio; không quy định cửa sổ damage.", 12, MoonGlassTheme.Muted));
        stack.AddChild(MoonGlassTheme.Label("Review hình ảnh; video --fixed-fps 60 là xuất offline, không chứng nhận FPS gameplay. Góc còn thiếu không được thay bằng ảnh SOUTH.", 12, MoonGlassTheme.Muted));
        int capture = Array.IndexOf(args, "--combat-capture");
        if (Array.IndexOf(args, "--combat-self-test") >= 0) { SelfTest(); return; }
        if (capture >= 0 && capture + 1 < args.Length) Capture(args[capture + 1]);
    }
    public override void _Process(double delta)
    {
        if (_sequence == null) return;
        if (!_capture) _clock += delta; double t = _clock % (Windup + Strike + Recover + .75); string clip; double local;
        if (t < Windup) { clip = "telegraph_01"; local = t; }
        else if (t < Windup + Strike) { clip = "attack_01"; local = t - Windup; }
        else if (t < Windup + Strike + Recover) { clip = "recovery_01"; local = t - Windup - Strike; }
        else { clip = "idle"; local = t - Windup - Strike - Recover; }
        _sequence.Clip = clip; _sequence.Paused = true;
        _sequence.ManualFrame = Math.Clamp((int)(local / ActorLibraryData.Duration(_actor, clip) * 16), 0, 15);
        _phase.Text = clip + " · " + (_sequence.ManualFrame + 1) + "/16 · nghỉ sau chuỗi 0,75 s";
        if (_rootCue != null)
        {
            _rootCue.Visible = clip == "telegraph_01";
            var frame = _rootCueFrames!.Frames[_sequence.ManualFrame];
            _rootCue.RegionRect = frame.Region; _rootCue.Offset = -frame.Pivot;
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
            foreach (var sample in new[] { (0d, true, 0), (.69, true, 15), (.70, false, 0), (1.05, false, 0), (1.60, false, 0), (2.36, true, 0) })
            {
                _clock = sample.Item1; _Process(0);
                if (_rootCue.Visible != sample.Item2 || (sample.Item2 && _sequence.ManualFrame != sample.Item3)) throw new Exception("cue phase leaked: " + sample.Item1);
                checks++;
            }
            GD.Print("ROOT_COMBAT_REVIEW_SELF_TEST PASS assertions=" + checks + " PRESENTATION_ONLY_NO_GAMEPLAY_HITBOX"); GetTree().Quit();
        }
        catch (Exception error) { GD.PushError("ROOT_COMBAT_REVIEW_SELF_TEST FAIL " + error); GetTree().Quit(1); }
    }
    private async void Capture(string path)
    {
        _capture = true; _clock = Windup - .02;
        foreach (var sprite in FindChildren("*", "Sprite2D", true, false))
            if (sprite is ActorLibrarySprite actor) { actor.Paused = true; actor.ManualFrame = actor.Clip switch { "attack_01" => 7, "hurt" => 4, _ => 15 }; }
        for (int i = 0; i < 5; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var result = GetViewport().GetTexture().GetImage().SavePng(path);
        GD.Print("CREATURE_COMBAT_CAPTURE " + _actor + " " + result + " STATIC_REVIEW_NOT_GAMEPLAY"); GetTree().Quit(result == Error.Ok ? 0 : 1);
    }
    public override void _ExitTree() => _library?.Dispose();
}
