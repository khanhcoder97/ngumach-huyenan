using Godot;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;

namespace Ngumach.VisualReboot;

/// <summary>Authored art staging and a server-authoritative local P00-01 slice.
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
    private SkillVfxPlayer _vfx=null!;
    private NativeOnlineSession? _online;
    private NativeActorsView? _liveActors;
    private NativeDialoguePanel? _dialog;
    private NativeOnlineFrame? _onlineFrame;
    private Vector2 _facing=Vector2.Down;
    private readonly AuthoritativeMotion _motion=new();
    private double _movingGrace;
    private int _previewCast;
    private bool _onlineTest,_onlineUiTest,_visualTest,_vfxReview,_questArtReview,_reviewStarted,_scenarioCapture;
    private string _lastSession="";
    private readonly HashSet<string> _impactIds=new();
    private bool _uiGallery;

    private int _frames;
    private bool _selfTest;
    private string? _capture;
    private bool _captureStarted;
    private bool _cleanCapture,_hudHidden;
    private bool _focused=true, _awaitMovementRelease;

    public override void _Ready()
    {
        Engine.MaxFps=60;
        if(DisplayServer.GetName()!="headless")
        {
            float refresh=DisplayServer.ScreenGetRefreshRate();
            DisplayServer.WindowSetVsyncMode(DisplayServer.VSyncMode.Enabled);
            // At60Hz let vblank be the single frame limiter; a second sleep cap adds jitter on older Windows drivers.
            if(refresh>=59&&refresh<=61)Engine.MaxFps=0;
        }
        var args = OS.GetCmdlineUserArgs();
        _selfTest = args.Contains("--camera-self-test");
        _onlineTest=args.Contains("--online-self-test");
        _onlineUiTest=args.Contains("--online-ui-self-test");
        _visualTest=args.Contains("--visual-self-test");
        _vfxReview=args.Contains("--vfx-review");
        _questArtReview=args.Contains("--quest-art-review");
        _uiGallery=args.Contains("--ui-gallery");
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
        _body = new HeroAnimator { Name="HeroBody" };
        _hero.AddChild(_body);
        ApplyDirection();
        _vfx=new SkillVfxPlayer{ZIndex=20};AddChild(_vfx);
        _camera = new TopDownCamera { Name = "WorldCamera",ProcessCallback=Camera2D.Camera2DProcessCallback.Physics };
        AddChild(_camera);
        _camera.Configure(new Vector2(Columns * CellPixels, Rows * CellPixels));
        if (args.Contains("--compact")) _camera.SetCompact(true);
        _camera.Follow(_hero.Position);
        var canvas = new CanvasLayer { Layer = 10, Name = "HudLayer" };
        AddChild(canvas);
        _hud = new PreviewHud { Name = "Hud", Visible = !_cleanCapture };
        canvas.AddChild(_hud);
        _hud.SkillPressed+=UseSkill;
        _hud.AttackPressed+=Attack;
        _hud.InventoryPressed+=OpenInventory;
        _hud.InteractPressed+=InteractNearest;
        _hud.JournalPressed+=OpenJournal;
        _hud.RetryPressed+=()=>_online?.Command("RETRY");
        _hud.MenuPressed+=OpenMenu;
        _dialog=new NativeDialoguePanel();AddChild(_dialog);
        _dialog.CommandRequested+=(kind,target,quest)=>_online?.Command(kind,target,quest);
        _dialog.Closed+=()=>_online?.SetMove(Vector2.Zero);
        _dialog.DisplaySettingsChanged+=(low,compact)=>{_vfx.LowFx=low;_hud.LowFx=low;_camera.SetCompact(compact);};
        if(!args.Any(a=>a.Contains("test",StringComparison.Ordinal))&&_capture==null&&!args.Contains("--performance-profile"))_dialog.ApplySavedPreferences();
        var url=OS.GetEnvironment("P1_BASE_URL");
        if((_onlineTest||_onlineUiTest)&&(!Uri.TryCreate(url,UriKind.Absolute,out var testUri)||!testUri.IsLoopback))
        {GD.PushError("Online acceptance requires the launcher's private loopback server.");GetTree().Quit(2);return;}
        if(!string.IsNullOrWhiteSpace(url)&&!_selfTest&&!_visualTest&&!_vfxReview&&!_questArtReview&&!args.Contains("--quest-ui-self-test")&&!args.Contains("--motion-self-test")&&!args.Contains("--motion-art-review"))
        {
            _hero.CollisionLayer=1;_hero.CollisionMask=1;
            var bounds=new Rect2(NativeActorsView.RenderOrigin+new Vector2(0,-1440),new Vector2(7200,1680));
            _camera.ConfigureBounds(bounds);_environment.ExtendOnlineBackdrop(bounds);
            _liveActors=new NativeActorsView();actors.AddChild(_liveActors);
            _online=new NativeOnlineSession();AddChild(_online);
            _online.FrameReady+=ApplyOnlineFrame;
            _online.ScenarioPassed+=count=>
            {
                GD.Print("GODOT_FIRST_QUEST_COMPLETE assertions="+count);
                _dialog?.ShowInventory(_online!.Frame);
                if(_capture!=null){_scenarioCapture=true;_frames=0;}
                else GetTree().Quit();
            };
            _online.ScenarioFailed+=error=>{GD.PushError(error);if(_onlineTest||_onlineUiTest)GetTree().Quit(1);else _hud.StatusText=error;};
            _online.Start(url,_onlineTest);
            if(_onlineUiTest)
            {
                var test=new NativeGameplayUiTest();AddChild(test);
                test.Configure(_online,_dialog,InteractNearest,OpenInventory,count=>
                {
                    GD.Print("GODOT_UI_FIRST_QUEST_COMPLETE assertions="+count);
                    if(_uiGallery)CaptureUiGallery();
                    else if(_capture!=null){_scenarioCapture=true;_frames=0;}
                    else GetTree().Quit();
                },error=>{GD.PushError(error);GetTree().Quit(1);});
            }
        }
        else if(_onlineTest||_onlineUiTest){GD.PushError("P1_BASE_URL is required for online test.");GetTree().Quit(2);return;}
        if(args.Contains("--quest-ui-self-test"))QuestPresentationSelfTest.Run(this);
        if(args.Contains("--motion-self-test"))RunMotionTests();
        if(args.Contains("--motion-art-review")){_captureStarted=true;RunMotionArtReview();}
        int screen=Array.IndexOf(args,"--ui-screen");
        if(screen>=0&&screen+1<args.Length)OpenMenu(args[screen+1]);
        int profile=Array.IndexOf(args,"--performance-profile");
        if(profile>=0&&profile+1<args.Length)AddChild(new FrameProfile{OutputPath=args[profile+1],Walk=args.Contains("--profile-walk")});
        if(_visualTest) RunVisualTests();
        if (_selfTest) RunCameraTests();
        else if(args.Contains("--scene-self-test")) RunSceneTests();
    }

    public override void _UnhandledKeyInput(InputEvent @event)
    {
        if(@event is not InputEventKey key||!key.Pressed||key.Echo)return;
        if(key.Keycode==Key.Escape)
        {
            if(_dialog?.IsOpen==true){_dialog.HidePanel();return;}
            GetTree().Quit();return;
        }
        if(key.Keycode==Key.I){OpenInventory();return;}
        if(key.Keycode==Key.J){OpenJournal();return;}
        if(key.Keycode==Key.C){OpenMenu("Character");return;}
        if(key.Keycode==Key.K){OpenMenu("Skills");return;}
        if(key.Keycode==Key.M){OpenMenu("WorldMap");return;}
        if(key.Keycode==Key.F10){OpenMenu("Settings");return;}
        if(_dialog?.IsOpen==true)return;
        int slot=(int)key.Keycode-(int)Key.Key1;
        if(slot>=0&&slot<6){UseSkill(slot);return;}
        if(key.Keycode==Key.Space)Attack();
        if(key.Keycode==Key.E)InteractNearest();
        if(key.Keycode==Key.R)_online?.Command("RETRY");
        if(key.Keycode==Key.Tab&&_onlineFrame?.World!=null)
        {
            var entity=_liveActors?.NearestTargetable(new Vector2((float)_onlineFrame.World.self.x,(float)_onlineFrame.World.self.y));
            if(_liveActors!=null)_liveActors.TargetId=entity?.entityId;
        }
        if(key.Keycode==Key.F2)_camera.SetCompact(!_camera.Compact);
        if(key.Keycode==Key.F6){_vfx.LowFx=!_vfx.LowFx;_hud.LowFx=_vfx.LowFx;}
        if(key.Keycode==Key.H)_hudHidden=!_hudHidden;
    }

    public override void _Notification(int what)
    {
        // No injected movement state is kept across focus loss.
        if (what == NotificationApplicationFocusOut){_focused=false;if(_hero!=null)_hero.Velocity=Vector2.Zero;_online?.SetMove(Vector2.Zero);}
        if (what == NotificationApplicationFocusIn){_focused=true;_awaitMovementRelease=true;}
    }

    public override void _PhysicsProcess(double delta)
    {
        if (_hero == null || _selfTest || _visualTest) return;
        var move = new Vector2(
            (Input.IsPhysicalKeyPressed(Key.D) || Input.IsPhysicalKeyPressed(Key.Right) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.A) || Input.IsPhysicalKeyPressed(Key.Left) ? 1 : 0),
            (Input.IsPhysicalKeyPressed(Key.S) || Input.IsPhysicalKeyPressed(Key.Down) ? 1 : 0) -
            (Input.IsPhysicalKeyPressed(Key.W) || Input.IsPhysicalKeyPressed(Key.Up) ? 1 : 0));
        if(!_focused||_dialog?.IsOpen==true) move=Vector2.Zero;
        if(_awaitMovementRelease){if(move==Vector2.Zero)_awaitMovementRelease=false;move=Vector2.Zero;}
        if (move != Vector2.Zero)
        {
            move = move.Normalized();
            _facing=move;
            _direction = ((int)Mathf.Round((Mathf.Atan2(move.X, -move.Y) + Mathf.Tau) / (Mathf.Pi / 4))) % 8;
            ApplyDirection();
        }
        if(_online!=null)
        {
            if(!_onlineUiTest)_online.SetMove(new Vector2(move.X,-move.Y));
            var target=_motion.Sample(AuthoritativeMotion.Now,_hero.Position);
            var displacement=target-_hero.Position;
            _hero.Velocity=Vector2.Zero;
            var previousPosition=_hero.Position;
            if(displacement.LengthSquared()>.0001f)_hero.MoveAndCollide(displacement);
            _movingGrace=_hero.Position.DistanceSquaredTo(previousPosition)>.0025f?.12:Math.Max(0,_movingGrace-delta);
        }
        else
        {
            _hero.Velocity=move*64;
            _hero.MoveAndSlide();
        }
        if(_body is HeroAnimator animator)animator.SetMoving(_online!=null?_movingGrace>0:_hero.Velocity.LengthSquared()>1);

        _environment.UpdateOcclusion(_hero.Position,_liveActors?.OcclusionFocus);
        _camera.Follow(_hero.Position);
        _hud.Coordinates = _online!=null?NativeActorsView.WorldPoint(_hero.Position):_hero.Position/TopDownCamera.PixelsPerWorldUnit;
        _hud.Facing=_facing;
        _hud.Compact = _camera.Compact;

    }

    private void ApplyDirection()
    {
        if(_body is HeroAnimator animator){animator.SetFacing(_direction);return;}
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
        _hud.Visible=!_cleanCapture&&!_hudHidden&&_dialog?.IsOpen!=true;
        if((_vfxReview||_questArtReview)&&!_reviewStarted&&_frames>3)
        {_reviewStarted=true;if(_questArtReview)ShowQuestArtReview();else ShowVfxReview();}
        if (_capture != null && _frames >= 20 && !_captureStarted && (_online==null||_scenarioCapture))
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
    private async void CaptureUiGallery()
    {
        _captureStarted=true;
        try
        {
            string directory=System.IO.Path.GetDirectoryName(_capture!)!;
            async System.Threading.Tasks.Task Capture(string name)
            {
                for(int i=0;i<4;i++)await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);
                await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);
                var result=GetViewport().GetTexture().GetImage().SavePng(System.IO.Path.Combine(directory,name));
                if(result!=Error.Ok)throw new InvalidOperationException("Gallery capture: "+result);
            }
            _dialog!.HidePanel();await Capture("moonglass_hud.png");
            foreach(var section in NativeDialoguePanel.Sections)
            {_dialog.ShowMenu(section.Id,_online!.Frame);await Capture("moonglass_"+section.Id.ToLowerInvariant()+".png");_dialog.AuditWorkspaceBounds();}
            _dialog.ShowInventory(_online!.Frame);await Capture(System.IO.Path.GetFileName(_capture!));
            GD.Print("MOONGLASS_GALLERY PASS sections="+NativeDialoguePanel.Sections.Length);GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("MOONGLASS_GALLERY FAIL "+ex);GetTree().Quit(1);}
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
        // Observe completed physics ticks, including buffered synthetic input on headless catch-up frames.
        {for(int i=0;i<count;i++){await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);}}
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


    private void ApplyOnlineFrame(NativeOnlineFrame frame)
    {
        _onlineFrame=frame;_hud.ApplyOnline(frame);_liveActors?.UpdateFrame(frame);_dialog?.ApplyFrame(frame);
        if(frame.World==null)return;
        if(_lastSession!=""&&_lastSession!=frame.SessionId){_vfx.Clear();_impactIds.Clear();}
        var point=NativeActorsView.RenderPoint(frame.World.self.x,frame.World.self.y);
        bool first=_lastSession==""||_lastSession!=frame.SessionId;
        var delta=point-_hero.Position;
        if(delta.LengthSquared()>.25f)
        {
            _facing=delta.Normalized();_movingGrace=.18;
            _direction=((int)Mathf.Round((Mathf.Atan2(_facing.X,-_facing.Y)+Mathf.Tau)/(Mathf.Pi/4)))%8;
            ApplyDirection();
        }
        _motion.Push(point,frame.SampleTime>0?frame.SampleTime:AuthoritativeMotion.Now,first);
        if(first||point.DistanceTo(_hero.Position)>240){_hero.Position=point;_hero.ResetPhysicsInterpolation();_camera.ResetPhysicsInterpolation();}
        _lastSession=frame.SessionId;
        if(frame.World.self.hp<=0){_vfx.Clear();_movingGrace=0;}
        if(frame.AcceptedAction is "CAST" or "BASIC_ATTACK")
        {
            if(_body is HeroAnimator animator){if(frame.AcceptedAction=="CAST")animator.Cast();else animator.Attack();}
            if(frame.AcceptedAction=="CAST"&&frame.AcceptedSkill!=null)
            {
                int index=Array.IndexOf(new[]{"SK-MK-01","SK-MK-02","SK-MK-03"},frame.AcceptedSkill);
                // A successful guard cast is not a successful counter. Its release
                // arc must wait for COUNTER_CONFIRMED, including a result-less event.
                var cast=frame.Events.LastOrDefault(e=>e.type=="CAST_START"&&e.actorId==frame.World.self.characterId);
                if(cast!=null){if(index>0)_vfx.Play(index,_hero.Position,_facing,cast.castId);else if(index==0)_vfx.GuardCue(_hero.Position,cast.castId);}
            }
        }
        foreach(var ev in frame.Events)
        {
            if(!_impactIds.Add(ev.eventId))continue;
            if(_impactIds.Count>512)_impactIds.Clear();
            if(ev.actorId==frame.World.self.characterId)
            {
                if(ev.type=="COUNTER_CONFIRMED")_vfx.Play(0,_hero.Position,_facing,ev.castId);
                if(ev.type=="CANCEL")_vfx.Clear();
            }
            if(ev.result==null)continue;
            var target=frame.World.entities.FirstOrDefault(e=>e.entityId==ev.targetId);
            if(target==null)continue;
            var text=new Label{Text=ev.result.hit?ev.result.hpDamage.ToString():"Trượt",
                Position=NativeActorsView.RenderPoint(target.x,target.y)+new Vector2(-12,-55)};
            text.AddThemeFontSizeOverride("font_size",18);
            text.AddThemeColorOverride("font_outline_color",Colors.Black);text.AddThemeConstantOverride("outline_size",3);
            AddChild(text);text.ZIndex=25;
            var tween=CreateTween();tween.SetParallel();
            tween.TweenProperty(text,"position:y",text.Position.Y-24,.7);
            tween.TweenProperty(text,"modulate:a",0,.7);
            tween.Chain().TweenCallback(Callable.From(()=>text.QueueFree()));
        }
    }

    private void InteractNearest()
    {
        if(_dialog?.IsOpen==true||_onlineFrame?.World==null||_online==null)return;
        var self=_onlineFrame.World.self;
        var entity=_liveActors?.NearestInteractable(new Vector2((float)self.x,(float)self.y));
        if(entity==null){_hud.StatusText="Hãy tới gần người hoặc đồ vật cần tương tác.";return;}
        if(entity.kind=="NPC")
        {
            string npc=entity.entityId.StartsWith("ENT_MAN_BM_")?entity.entityId["ENT_MAN_BM_".Length..]:entity.entityId;
            _dialog?.ShowNpc(npc,_onlineFrame);_online.SetMove(Vector2.Zero);
        }
        else _online.Command("INTERACT",entity.entityId);
    }
    private void OpenInventory()
    {
        if(_dialog==null)return;
        if(_dialog.IsOpen){_dialog.HidePanel();return;}
        _online?.SetMove(Vector2.Zero);_online?.Command("REFRESH");_dialog.ShowInventory(_onlineFrame??new NativeOnlineFrame());
    }
    private void OpenJournal()
    {
        if(_dialog==null)return;
        if(_dialog.IsOpen){_dialog.HidePanel();return;}
        _online?.SetMove(Vector2.Zero);_online?.Command("REFRESH");_dialog.ShowJournal(_onlineFrame??new NativeOnlineFrame());
    }
    private void OpenMenu(string section)
    {
        if(_dialog==null)return;
        _online?.SetMove(Vector2.Zero);_dialog.ShowMenu(section,_onlineFrame??new NativeOnlineFrame());
    }
    private bool BeginCombat(int slot)
    {
        if(_dialog?.IsOpen==true)return false;
        _hud.PressAction(slot);
        if(_online!=null&&_onlineFrame?.ConnectionState!=NguMach.Client.P1.P1ConnectionState.Ready)
        {_hud.ShowAction(slot,_onlineFrame?.ConnectionState==NguMach.Client.P1.P1ConnectionState.UncertainMutation?"Chưa rõ kết quả. Nhấn R để thử lại.":"Đang đồng bộ; hãy chờ một chút.");return false;}
        if(_online!=null&&_hud.Cooldown(slot)>0)
        {_hud.ShowAction(slot,"Đang hồi · "+Math.Ceiling(_hud.Cooldown(slot))+" giây");return false;}
        return true;
    }
    private void Attack()
    {
        if(!BeginCombat(-1))return;
        if(_body is HeroAnimator swing)swing.Attack();
        if(_online!=null)
        {
            if(_onlineFrame?.World==null)return;
            var self=_onlineFrame.World.self;
            var target=_liveActors?.TargetId;
            if(target==null)target=_liveActors?.NearestTargetable(new Vector2((float)self.x,(float)self.y))?.entityId;
            if(target==null){_hud.ShowAction(-1,"Chưa có mục tiêu có thể tấn công.");return;}
            _online.Command("BASIC_ATTACK",target,aimX:_facing.X,aimY:-_facing.Y);
        }
        else _hud.ShowAction(-1,"Tấn công · xem thử",true);
    }
    private void UseSkill(int index)
    {
        if(!BeginCombat(index))return;
        _hud.LastSkill=SkillVfxPlayer.Names[index];
        if(_online!=null)
        {
            if(index>=3){_hud.ShowAction(index,"Kỹ năng này chưa được mở.");return;}
            if(_onlineFrame?.World==null)return;
            var self=_onlineFrame.World.self;
            var target=index==0?null:_liveActors?.TargetId??_liveActors?.NearestTargetable(new Vector2((float)self.x,(float)self.y))?.entityId;
            if(index>0&&target==null){_hud.ShowAction(index,"Cần chọn mục tiêu còn sống.");return;}
            if(_body is HeroAnimator castActor)castActor.Cast();
            _online.Command("CAST",target??"",skillId:"SK-MK-0"+(index+1),aimX:_facing.X,aimY:-_facing.Y);
        }
        else
        {
            if(_body is HeroAnimator animator)animator.Cast();
            _hud.ShowAction(index,SkillVfxPlayer.Names[index]+" · xem thử",true);
            _vfx.Play(index,_hero.Position,_facing,"PREVIEW_"+(++_previewCast));
        }
    }
    private void ShowVfxReview()
    {
        _hud.Visible=false;
        _vfx.ReviewFreeze=true;
        for(int i=0;i<6;i++)
        {
            var foot=_hero.Position+new Vector2(-390+(i%3)*350,-120+(i/3)*260);
            _vfx.Play(i,foot,Vector2.Right,"REVIEW_"+i);
            var label=new Label{Text=SkillVfxPlayer.Names[i],Position=foot+new Vector2(-90,-75),ZIndex=21};
            label.AddThemeFontSizeOverride("font_size",17);label.AddThemeColorOverride("font_outline_color",Colors.Black);
            label.AddThemeConstantOverride("outline_size",3);AddChild(label);
        }
        _hud.StatusText="Gallery VFX: khung chính để kiểm hình. Chế độ chơi phát đầy đủ timeline.";
    }
    private void ShowQuestArtReview()
    {
        _hud.Visible=false;_hero.Visible=false;
        var a=_hero.Position+new Vector2(-530,-250);var z=_hero.Position+new Vector2(530,230);
        AddChild(new Polygon2D{Polygon=new[]{a,new Vector2(z.X,a.Y),z,new Vector2(a.X,z.Y)},Color=new Color(.025f,.05f,.045f,.97f),ZIndex=20});
        var heading=new Label{Text="Bến Mưa · kiểm hình asset, không phải vị trí spawn",Position=a+new Vector2(20,12),ZIndex=22};
        heading.AddThemeFontSizeOverride("font_size",18);heading.AddThemeColorOverride("font_color",Color.FromHtml("#e7c783"));AddChild(heading);
        using var manifest=JsonDocument.Parse(FileAccess.GetFileAsString("res://assets/combat_v1/manifest.json"));
        var texture=GD.Load<Texture2D>("res://assets/combat_v1/ben_mua_quest_markers.png");
        string[] keys={"RIPPLE_0","RIPPLE_1","RIPPLE_2","RIPPLE_3","VILLAGER_01_WAIT","VILLAGER_01_STAND","VILLAGER_02_WAIT","VILLAGER_02_STAND"};
        for(int i=0;i<8;i++)
        {
            var data=manifest.RootElement.GetProperty("questMarkers").GetProperty(keys[i]);
            var r=data.GetProperty("rect");var p=data.GetProperty("pivot");var b=data.GetProperty("contentBounds");
            var foot=_hero.Position+new Vector2(-390+(i%4)*260,i<4?-140:160);
            float scale=i<4?70/(b[2].GetSingle()-b[0].GetSingle()):72/(b[3].GetSingle()-b[1].GetSingle());
            var sprite=new Sprite2D{Texture=new AtlasTexture{Atlas=texture,Region=new Rect2(r[0].GetSingle(),r[1].GetSingle(),r[2].GetSingle(),r[3].GetSingle()),FilterClip=true},
                Centered=false,Position=foot,Offset=-new Vector2(p[0].GetSingle(),p[1].GetSingle()),Scale=Vector2.One*scale,ZIndex=21,TextureFilter=TextureFilterEnum.Nearest};
            AddChild(sprite);
            var label=new Label{Text=i<4?"Gợn nước · "+(i+1):i<6?"Người dân · "+(i-3):"Người dân · "+(i-5),
                Position=foot+new Vector2(-60,i<4?40:15),ZIndex=22};
            label.AddThemeFontSizeOverride("font_size",16);label.AddThemeColorOverride("font_outline_color",Colors.Black);label.AddThemeConstantOverride("outline_size",3);AddChild(label);
        }
    }
    private async void RunVisualTests()
    {
        int assertions=0;
        void Check(bool ok,string text){assertions++;if(!ok)throw new InvalidOperationException(text);}
        async System.Threading.Tasks.Task Frames(int n)
        {for(int i=0;i<n;i++)await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);}
        try
        {
            var actor=(HeroAnimator)_body;actor.SetMoving(true);
            for(int i=0;i<8;i++){actor.SetFacing(i);await Frames(9);Check(actor.RegionRect.Size.X>0,"whole-body direction "+i);}
            actor.Attack();await Frames(2);Check(actor.IsAttacking,"attack starts");
            await Frames(40);Check(!actor.IsAttacking,"attack recovers");
            _vfx.Clear();
            Check(_vfx.Play(0,_hero.Position,Vector2.Right,"TEST_CAST"),"new cast starts");
            Check(!_vfx.Play(0,_hero.Position,Vector2.Right,"TEST_CAST"),"same cast is not replayed");
            for(int i=0;i<30;i++)_vfx.Play(i%6,_hero.Position,Vector2.Right,"POOL_"+i);
            Check(_vfx.ActiveCount==24,"full VFX budget");
            _vfx.LowFx=true;_vfx.Play(0,_hero.Position,Vector2.Right,"LOWFX");
            Check(_vfx.ActiveCount<=8,"low VFX budget");
            _vfx.Clear();Check(_vfx.ActiveCount==0,"lifetime cancel clears all");
            GD.Print("VISUAL_SELF_TEST PASS assertions="+assertions);GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("VISUAL_SELF_TEST FAIL "+ex);GetTree().Quit(1);}
    }

    public override void _ExitTree() => _manifest?.Dispose();
}
