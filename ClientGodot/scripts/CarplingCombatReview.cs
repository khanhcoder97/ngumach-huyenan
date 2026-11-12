using Godot;
using System;

namespace Ngumach.VisualReboot;

/// <summary>Native source-art review; no encounter, damage, inventory or server state.</summary>
public partial class CarplingCombatReview : Control
{
    private ActorLibraryData _library = null!;
    private ActorLibrarySprite _sequence = null!;
    private Label _phase = null!;
    private double _clock;
    private bool _capture;
    private static readonly string[] Actions = { "telegraph_01", "attack_01", "recovery_01", "hurt", "death" };
    public override void _Ready()
    {
        Engine.MaxFps = 60; Theme = MoonGlassTheme.Create();
        _library = new ActorLibraryData(reviewMode: true);
        var bg = new ColorRect { Color = Color.FromHtml("#20243b"), MouseFilter = MouseFilterEnum.Ignore };
        bg.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect); AddChild(bg);
        var margin = new MarginContainer(); margin.SetAnchorsAndOffsetsPreset(LayoutPreset.FullRect);
        foreach (string edge in new[] { "left", "right", "top", "bottom" }) margin.AddThemeConstantOverride("margin_" + edge, 24);
        AddChild(margin); var stack = new VBoxContainer(); margin.AddChild(stack);
        stack.AddChild(MoonGlassTheme.Label("CÁ LINH / KIỂM CHUỖI COMBAT", 24, MoonGlassTheme.Gold));
        stack.AddChild(MoonGlassTheme.Label("SOUTH · 16 ảnh nguồn/động tác · candidate chưa duyệt gameplay · ESC: đóng", 14));
        var grid = new GridContainer { Columns = 3, SizeFlagsVertical = SizeFlags.ExpandFill }; stack.AddChild(grid);
        grid.AddThemeConstantOverride("h_separation", 18); grid.AddThemeConstantOverride("v_separation", 16);
        for (int i = 0; i < 6; i++)
        {
            var card = new VBoxContainer { SizeFlagsHorizontal = SizeFlags.ExpandFill, SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 250) }; grid.AddChild(card);
            string action = i < 5 ? Actions[i] : "telegraph_01";
            string title = i < 5 ? action + " · " + ActorLibraryData.Duration("MOB_CARPLING", action).ToString("0.00", System.Globalization.CultureInfo.InvariantCulture) + " s" : "NỐI BA PHA · 0,45 / 0,30 / 0,50 s";
            card.AddChild(MoonGlassTheme.Label(title, 16, MoonGlassTheme.Blue));
            var stage = new Control { SizeFlagsVertical = SizeFlags.ExpandFill, CustomMinimumSize = new Vector2(300, 200) }; card.AddChild(stage);
            var sprite = new ActorLibrarySprite { Library = _library, ActorId = "MOB_CARPLING", Clip = action, Facing = 4, DisplayHeight = 140, Loop = i < 3 };
            stage.AddChild(sprite); stage.Resized += () => sprite.Position = new Vector2(stage.Size.X / 2, stage.Size.Y / 2 + 65);
            sprite.Position = new Vector2(150, 165);
            if (i == 5) { _sequence = sprite; _phase = MoonGlassTheme.Label("", 13); card.AddChild(_phase); }
            else card.AddChild(MoonGlassTheme.Label(i < 3 ? "Lặp riêng để soi pose; không phải nhịp AI." : "Một lần · giữ khung cuối", 12, MoonGlassTheme.Muted));
        }
        stack.AddChild(MoonGlassTheme.Label("0,45 s báo / 0,50 s hồi theo visual bible. 0,30 s đánh là timing thử, chỉnh được trong Studio; không quy định cửa sổ damage.", 12, MoonGlassTheme.Muted));
        stack.AddChild(MoonGlassTheme.Label("Review hình ảnh; video --fixed-fps 60 là xuất offline, không chứng nhận FPS gameplay. Góc còn thiếu không được thay bằng ảnh SOUTH.", 12, MoonGlassTheme.Muted));
        var args = OS.GetCmdlineUserArgs(); int capture = Array.IndexOf(args, "--combat-capture");
        if (capture >= 0 && capture + 1 < args.Length) Capture(args[capture + 1]);
    }
    public override void _Process(double delta)
    {
        if (_sequence == null) return;
        if (!_capture) _clock += delta; double t = _clock % 2; string clip; double local;
        if (t < .45) { clip = "telegraph_01"; local = t; }
        else if (t < .75) { clip = "attack_01"; local = t - .45; }
        else if (t < 1.25) { clip = "recovery_01"; local = t - .75; }
        else { clip = "idle"; local = t - 1.25; }
        _sequence.Clip = clip; _sequence.Paused = true;
        _sequence.ManualFrame = Math.Clamp((int)(local / ActorLibraryData.Duration("MOB_CARPLING", clip) * 16), 0, 15);
        _phase.Text = clip + " · " + (_sequence.ManualFrame + 1) + "/16 · nghỉ sau chuỗi 0,75 s";
    }
    public override void _UnhandledKeyInput(InputEvent ev)
    { if (ev is InputEventKey key && key.Pressed && key.Keycode == Key.Escape) GetTree().Quit(); }
    private async void Capture(string path)
    {
        _capture = true; _clock = .43;
        foreach (var sprite in FindChildren("*", "Sprite2D", true, false))
            if (sprite is ActorLibrarySprite actor) { actor.Paused = true; actor.ManualFrame = actor.Clip switch { "attack_01" => 7, "hurt" => 4, _ => 15 }; }
        for (int i = 0; i < 5; i++) await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var result = GetViewport().GetTexture().GetImage().SavePng(path);
        GD.Print("CARPLING_COMBAT_CAPTURE " + result + " STATIC_REVIEW_NOT_GAMEPLAY"); GetTree().Quit(result == Error.Ok ? 0 : 1);
    }
    public override void _ExitTree() => _library?.Dispose();
}
