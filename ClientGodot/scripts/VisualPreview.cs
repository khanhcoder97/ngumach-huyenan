using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Offline art staging, NOT the online quest/loot client.
/// New independent source sprites only; no concept-image map or Muse graphics.</summary>
public partial class VisualPreview : Node2D
{
    public const int Columns = 160, Rows = 120, CellPixels = 16;
    private readonly List<Rect2> _blocked = new();
    private CharacterBody2D _hero = null!;
    private Sprite2D _body = null!;
    private TopDownCamera _camera = null!;
    private PreviewHud _hud = null!;
    private Texture2D _heroTexture = null!;
    private JsonDocument _manifest = null!;
    private int _direction = 4;
    private int _frames;
    private bool _selfTest;
    private string? _capture;
    private bool _captureStarted;
    private bool _cleanCapture;

    public override void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        _selfTest = args.Contains("--camera-self-test");
        _cleanCapture = args.Contains("--clean-capture");
        for (int i = 0; i < args.Length - 1; i++)
            if (args[i] == "--capture") _capture = args[i + 1];
        TextureFilter = TextureFilterEnum.Nearest;
        _manifest = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/reboot/manifest.json"));
        BuildTerrain();
        var actors = new Node2D { Name = "DepthSorted", YSortEnabled = true };
        AddChild(actors);
        BuildProps(actors);
        _heroTexture = GD.Load<Texture2D>("res://assets/reboot/hero_idle_body.png");
        _hero = new CharacterBody2D { Name = "Hero", Position = new Vector2(1280, 896),
            CollisionLayer = 1, CollisionMask = 1, MotionMode = CharacterBody2D.MotionModeEnum.Floating };
        actors.AddChild(_hero);
        _hero.AddChild(new CollisionShape2D { Shape = new CircleShape2D { Radius = 5 } });
        _body = new Sprite2D { Texture = _heroTexture, RegionEnabled = true, Centered = false };
        _hero.AddChild(_body);
        ApplyDirection();
        // Only the staging map has these footprints. No canonical nav data is changed.
        AddBlock(new Rect2(0, 71 * CellPixels, Columns * CellPixels, (Rows - 71) * CellPixels));
        AddBlock(new Rect2(-20, -20, 20, Rows * CellPixels + 40));
        AddBlock(new Rect2(Columns * CellPixels, -20, 20, Rows * CellPixels + 40));
        AddBlock(new Rect2(0, -20, Columns * CellPixels, 20));
        _camera = new TopDownCamera { Name = "WorldCamera" };
        AddChild(_camera);
        _camera.Configure(new Vector2(Columns * CellPixels, Rows * CellPixels));
        if (args.Contains("--compact")) _camera.SetCompact(true);
        _camera.Follow(_hero.Position);
        var canvas = new CanvasLayer { Layer = 10, Name = "HudLayer" };
        AddChild(canvas);
        _hud = new PreviewHud { Name = "Hud", Visible = !_cleanCapture };
        canvas.AddChild(_hud);
        if (_selfTest) RunCameraTests();
    }

    private void BuildTerrain()
    {
        var source = new TileSetAtlasSource {
            Texture = GD.Load<Texture2D>("res://assets/reboot/terrain.png"),
            TextureRegionSize = new Vector2I(256, 256)
        };
        for (int y = 0; y < 4; y++) for (int x = 0; x < 6; x++) source.CreateTile(new Vector2I(x, y));
        var tiles = new TileSet { TileSize = new Vector2I(256, 256) };
        tiles.AddSource(source, 0);
        var ground = new TileMapLayer { Name = "GroundTiles", TileSet = tiles,
            Scale = Vector2.One * (CellPixels / 256f) };
        AddChild(ground);
        for (int y = 0; y < Rows; y++)
        for (int x = 0; x < Columns; x++)
        {
            int tile;
            if (y > 70) tile = 6 + ((x * 13 + y * 7) % 9 == 0 ? 2 : 1);
            else if (y == 70) tile = 12; // land north, water south, verified from actual pixels
            else if ((y >= 52 && y <= 56) || (x >= 77 && x <= 82)) tile = 4;
            else if ((x >= 35 && x <= 38) || (x >= 120 && x <= 123) || (y >= 25 && y <= 27)) tile = 3;
            else tile = ((x * 17 + y * 31) % 11 < 2) ? 1 : 0;
            ground.SetCell(new Vector2I(x, y), 0, new Vector2I(tile % 6, tile / 6));
        }
    }

    private void BuildProps(Node2D actors)
    {
        var tex = GD.Load<Texture2D>("res://assets/reboot/props.png");
        void Prop(int slot, Vector2 position, float size, bool solid)
        {
            var bounds = new Rect2((slot % 3) * 512, (slot / 3) * 512, 512, 512);
            var sprite = new Sprite2D { Texture = new AtlasTexture { Atlas = tex, Region = bounds },
                Position = position, Centered = false, Offset = new Vector2(-256, -456),
                Scale = Vector2.One * (size / 512) };
            actors.AddChild(sprite);
            if (solid) AddBlock(new Rect2(position.X - size * .34f, position.Y - size * .70f, size * .68f, size * .68f));
        }
        for (int districtY = 0; districtY < 2; districtY++)
        for (int districtX = 0; districtX < 6; districtX++)
        {
            float x = 240 + districtX * 360;
            float y = districtY == 0 ? 720 : 1050;
            if (Mathf.Abs(x - 1280) < 170) x += 100;
            Prop((districtX + districtY) % 3 == 0 ? 3 : 2, new Vector2(x, y), 208, true);
            Prop(4, new Vector2(x + 125, y + 20), 96, true);
        }
        for (int i = 0; i < 28; i++)
        {
            float x = 100 + (i * 313 % 2300);
            float y = 180 + (i * 197 % 760);
            if (x > 1180 && x < 1380 || y > 800 && y < 930 || _blocked.Any(r => r.Grow(60).HasPoint(new Vector2(x,y)))) continue;
            Prop(i % 2, new Vector2(x, y), i % 2 == 0 ? 152 : 128, false);
        }
        Prop(5, new Vector2(1160, 1240), 192, false);
        Prop(5, new Vector2(1720, 1240), 192, false);
    }

    private void AddBlock(Rect2 rect)
    {
        _blocked.Add(rect);
        var body = new StaticBody2D { Position = rect.GetCenter(), CollisionLayer = 1 };
        body.AddChild(new CollisionShape2D { Shape = new RectangleShape2D { Size = rect.Size } });
        AddChild(body);
    }

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if (@event is not InputEventKey key || !key.Pressed || key.Echo) return;
        if (key.Keycode == Key.F2) _camera.SetCompact(!_camera.Compact);
        if (key.Keycode == Key.H) _hud.Visible = !_hud.Visible;
        if (key.Keycode == Key.Escape) GetTree().Quit();
    }

    public override void _Notification(int what)
    {
        // No injected movement state is kept across focus loss.
        if (what == NotificationApplicationFocusOut && _hero != null) _hero.Velocity = Vector2.Zero;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_hero == null || _selfTest) return;
        var move = new Vector2(
            (Input.IsPhysicalKeyPressed(Key.D) || Input.IsPhysicalKeyPressed(Key.Right) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.A) || Input.IsPhysicalKeyPressed(Key.Left) ? 1 : 0),
            (Input.IsPhysicalKeyPressed(Key.S) || Input.IsPhysicalKeyPressed(Key.Down) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.W) || Input.IsPhysicalKeyPressed(Key.Up) ? 1 : 0));
        if (move != Vector2.Zero)
        {
            move = move.Normalized();
            _direction = ((int)Mathf.Round((Mathf.Atan2(move.X, -move.Y) + Mathf.Tau) / (Mathf.Pi / 4))) % 8;
            ApplyDirection();
        }
        _hero.Velocity = move * 80; // 4 WU/s for staging only, not a server movement rule
        _hero.MoveAndSlide();
        _camera.Follow(_hero.Position);
        _hud.Coordinates = _hero.Position / TopDownCamera.PixelsPerWorldUnit;
        _hud.Compact = _camera.Compact;
        _hud.QueueRedraw();
    }

    private void ApplyDirection()
    {
        var frame = _manifest.RootElement.GetProperty("heroFrames")[_direction];
        var rect = frame.GetProperty("rect").EnumerateArray().Select(v => v.GetInt32()).ToArray();
        var pivot = frame.GetProperty("pivot").EnumerateArray().Select(v => v.GetSingle()).ToArray();
        _body.RegionRect = new Rect2(rect[0], rect[1], rect[2], rect[3]);
        _body.Offset = -new Vector2(pivot[0], pivot[1]);
        _body.Scale = Vector2.One * (48f / 372f);
    }

    public override void _Process(double delta)
    {
        _frames++;
        if (_capture != null && _frames >= 20 && !_captureStarted)
        {
            _captureStarted = true;
            CaptureAndQuit();
        }
    }

    private async void CaptureAndQuit()
    {
        await ToSignal(RenderingServer.Singleton, RenderingServer.SignalName.FramePostDraw);
        var error = GetViewport().GetTexture().GetImage().SavePng(_capture!);
        GD.Print("CAPTURE " + error + " " + _capture);
        GetTree().Quit(error == Error.Ok ? 0 : 1);
    }

    private void RunCameraTests()
    {
        int assertions = 0;
        void Check(bool ok, string name) { assertions++; if (!ok) throw new InvalidOperationException(name); }
        try
        {
            Check(_camera.VisibleWorldSize == new Vector2(64, 36), "default is 64x36 WU");
            Check(_camera.Zoom == Vector2.One, "1280x720 at 20 PPU");
            Check(_camera.Rotation == 0 && !_camera.PositionSmoothingEnabled, "orthographic pixel camera");
            Check(_camera.Constrain(Vector2.Zero) == new Vector2(640, 360), "northwest edge clamp");
            Check(_camera.Constrain(new Vector2(99999,99999)) == new Vector2(1920,1560), "southeast edge clamp");
            _camera.SetCompact(true);
            Check(_camera.VisibleWorldSize == new Vector2(48,27), "optional compact");
            _camera.SetCompact(false);
            Check(_hud.GetParent() is CanvasLayer, "HUD outside camera transform");
            var slots = PreviewHud.SkillCenters();
            foreach (var p in slots) Check(p.X-23 >= 16 && p.X+23 <= 1264 && p.Y-23 >= 16 && p.Y+23 <= 704, "skill arc safe area");
            for(int i=0;i<slots.Length;i++) for(int j=i+1;j<slots.Length;j++) Check(slots[i].DistanceTo(slots[j]) > 46, "skill slots do not overlap");
            Check(_blocked.Any(r => r.HasPoint(new Vector2(100,1500))), "water blocked");
            Check(!_blocked.Any(r => r.HasPoint(_hero.Position)), "spawn walkable");
            Check(_manifest.RootElement.GetProperty("heroFrames").GetArrayLength() == 8, "8 explicit regions");
            foreach (var frame in _manifest.RootElement.GetProperty("heroFrames").EnumerateArray())
            {
                var r = frame.GetProperty("rect").EnumerateArray().Select(v => v.GetInt32()).ToArray();
                Check(r[0] >= 0 && r[1] >= 0 && r[0]+r[2] <= _heroTexture.GetWidth()
                    && r[1]+r[3] <= _heroTexture.GetHeight(), "atlas bounds " + frame.GetProperty("direction").GetString());
            }
            _camera.Configure(new Vector2(100,100));
            Check(_camera.Constrain(new Vector2(999,999)) == new Vector2(50,50), "small map centers without zoom");
            _camera.Configure(new Vector2(Columns * CellPixels, Rows * CellPixels));
            _camera.Follow(_hero.Position);
            GD.Print("CAMERA_SELF_TEST PASS assertions=" + assertions);
            if (_capture == null) GetTree().Quit();
        }
        catch (Exception ex) { GD.PushError("CAMERA_SELF_TEST FAIL " + ex); GetTree().Quit(1); }
    }

    public override void _ExitTree() => _manifest?.Dispose();
}
