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
    private BenMuaEnvironment _environment = null!;
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
    private bool _focused=true, _awaitMovementRelease;

    public override void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        _selfTest = args.Contains("--camera-self-test");
        _cleanCapture = args.Contains("--clean-capture");
        for (int i = 0; i < args.Length - 1; i++)
            if (args[i] == "--capture") _capture = args[i + 1];
        TextureFilter = TextureFilterEnum.Nearest;
        _manifest = JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/reboot/manifest.json"));
        var actors = new Node2D { Name = "DepthSorted", YSortEnabled = true };
        AddChild(actors);
        _environment=new BenMuaEnvironment();
        AddChild(_environment);
        _environment.Build(actors);
        _heroTexture = GD.Load<Texture2D>("res://assets/reboot/hero_idle_body.png");
        _hero = new CharacterBody2D { Name = "Hero", Position = _environment.Spawn,
            CollisionLayer = 1, CollisionMask = 1, MotionMode = CharacterBody2D.MotionModeEnum.Floating };
        actors.AddChild(_hero);
        _hero.AddChild(new CollisionShape2D { Shape = new CircleShape2D { Radius = 5 } });
        _body = new Sprite2D { Texture = _heroTexture, RegionEnabled = true, Centered = false };
        _hero.AddChild(_body);
        ApplyDirection();
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
        else if(args.Contains("--scene-self-test")) RunSceneTests();
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
        if (what == NotificationApplicationFocusOut){_focused=false;if(_hero!=null)_hero.Velocity=Vector2.Zero;}
        if (what == NotificationApplicationFocusIn){_focused=true;_awaitMovementRelease=true;}
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_hero == null || _selfTest) return;
        var move = new Vector2(
            (Input.IsPhysicalKeyPressed(Key.D) || Input.IsPhysicalKeyPressed(Key.Right) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.A) || Input.IsPhysicalKeyPressed(Key.Left) ? 1 : 0),
            (Input.IsPhysicalKeyPressed(Key.S) || Input.IsPhysicalKeyPressed(Key.Down) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.W) || Input.IsPhysicalKeyPressed(Key.Up) ? 1 : 0));
        if(!_focused) move=Vector2.Zero;
        if(_awaitMovementRelease){if(move==Vector2.Zero)_awaitMovementRelease=false;move=Vector2.Zero;}
        if (move != Vector2.Zero)
        {
            move = move.Normalized();
            _direction = ((int)Mathf.Round((Mathf.Atan2(move.X, -move.Y) + Mathf.Tau) / (Mathf.Pi / 4))) % 8;
            ApplyDirection();
        }
        _hero.Velocity = move * 80; // 4 WU/s for staging only, not a server movement rule
        _hero.MoveAndSlide();
        _environment.UpdateOcclusion(_hero.Position);
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
        _body.Scale = Vector2.One * (36f / 372f);
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
            Check(!_environment.IsWalkable(_environment.World(new Vector2(360,586))), "curved river blocked");
            Check(_environment.IsWalkable(_hero.Position), "spawn walkable");
            Check(_environment.IsWalkable(_environment.World(new Vector2(660,580))), "pier is walkable over water");
            Check(_environment.AuthoredPlacementCount == 113, "authored placement registry");
            Check(_environment.ShoreDetailCount > 100, "shore decoration coverage");
            var reachable=_environment.Reachable(_hero.Position);
            foreach(var target in new[]{new Vector2(648,72),new Vector2(980,327),new Vector2(170,360),new Vector2(660,580),new Vector2(458,335)})
            {
                var wp=_environment.World(target);
                var grid=new Vector2I(Mathf.RoundToInt(wp.X/16),Mathf.RoundToInt(wp.Y/16));
                Check(reachable.Contains(grid), "route from spawn to "+target);
            }
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


    private async void RunSceneTests()
    {
        int assertions=0;
        void Check(bool ok,string message){assertions++;if(!ok)throw new InvalidOperationException(message);}
        void KeyState(Key key,bool pressed)=>Input.ParseInputEvent(new InputEventKey{Keycode=key,PhysicalKeycode=key,Pressed=pressed});
        async System.Threading.Tasks.Task Frames(int count)
        {for(int i=0;i<count;i++)await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);}
        var original=_hero.Position;
        try
        {
            await Frames(3);
            var before=_hero.Position;
            KeyState(Key.D,true);await Frames(24);KeyState(Key.D,false);await Frames(3);
            Check(_hero.Position.X-before.X>20,"real input moves hero on physics frames");
            Check(Mathf.Abs(_hero.Position.Y-before.Y)<.2f,"east movement stays on axis");
            var stopped=_hero.Position;await Frames(5);
            Check(stopped.DistanceTo(_hero.Position)<.1f,"key release stops movement");
            KeyState(Key.D,true);await Frames(4);
            _Notification((int)NotificationApplicationFocusOut);var unfocused=_hero.Position;await Frames(6);
            Check(unfocused.DistanceTo(_hero.Position)<.1f,"focus loss blocks held input");
            _Notification((int)NotificationApplicationFocusIn);await Frames(6);
            Check(unfocused.DistanceTo(_hero.Position)<.1f,"focus regain requires release");
            KeyState(Key.D,false);await Frames(2);
            KeyState(Key.D,true);await Frames(6);KeyState(Key.D,false);await Frames(2);
            Check(_hero.Position.X>unfocused.X+4,"fresh press works after focus recovery");
            _hero.Position=_environment.World(new Vector2(660,575));await Frames(2);
            KeyState(Key.S,true);await Frames(60);KeyState(Key.S,false);await Frames(2);
            var pierLocal=_hero.Position-_environment.DistrictOrigin;
            Check(pierLocal.Y>590&&pierLocal.Y<604,"physics stops at pier end, not in river: "+pierLocal);
            _hero.Position=_environment.World(new Vector2(337,270));await Frames(2);
            var willow=_hero.GetParent().GetNode<Sprite2D>("ART_BM_TREE_10");
            Check(willow.Modulate.A<.6f,"canopy fades when hiding hero");
            _hero.Position=original;await Frames(2);
            Check(willow.Modulate.A>.99f,"canopy restores after player leaves");
            GD.Print("SCENE_SELF_TEST PASS assertions="+assertions);
            GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("SCENE_SELF_TEST FAIL "+ex);GetTree().Quit(1);}
        finally{KeyState(Key.D,false);KeyState(Key.S,false);}
    }

    public override void _ExitTree() => _manifest?.Dispose();
}
