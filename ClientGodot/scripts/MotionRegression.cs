using Godot;
using System;
using System.Threading.Tasks;
namespace Ngumach.VisualReboot;
public partial class VisualPreview
{
    /// <summary>Offline engine-physics and presentation fixtures; no authoritative grant/combat simulation.</summary>
    private async void RunMotionTests()
    {
        int checks=0;void Check(bool ok,string name){checks++;if(!ok)throw new InvalidOperationException(name);}
        void KeyState(Key key,bool down)=>Input.ParseInputEvent(new InputEventKey{Keycode=key,PhysicalKeycode=key,Pressed=down});
        async Task Frames(int n){for(int i=0;i<n;i++){await ToSignal(GetTree(),SceneTree.SignalName.PhysicsFrame);await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);}}
        try
        {
            GD.Print("MOTION_REGRESSION_MODE OFFLINE_PHYSICS_AND_POINTER_EVENT_INJECTION");
            var actor=(HeroAnimator)_body;
            foreach(var action in new[]{"idle","walk","attack","cast"})
            for(int d=0;d<8;d++)for(int f=0;f<16;f++)
            {actor.ReviewPose(action,d,f);Check(actor.DisplayedFrame==f&&actor.Texture!=null&&actor.RegionRect.Size.X>0,action+" direction"+d+" pose"+f);}
            actor.ClearReview();Check(actor.AnimationFrameCount==16,"renderer uses16authored poses");
            var motion=new AuthoritativeMotion();motion.Push(Vector2.Zero,0);motion.Push(new Vector2(10,0),.1);
            Check(motion.Sample(.15,Vector2.Zero).DistanceTo(new Vector2(5,0))<.001,"snapshot interpolation is continuous");
            Check(motion.Sample(10,Vector2.Zero)==new Vector2(10,0),"network stall never extrapolates into unconfirmed terrain");
            motion.Push(new Vector2(500,100),11);Check(motion.Sample(11,Vector2.Zero)==new Vector2(500,100),"large authoritative teleport resets interpolation");
            var restart=new AuthoritativeMotion();restart.Push(Vector2.Zero,0);restart.Push(new Vector2(6.4f,0),5);
            Check(restart.Sample(5,Vector2.Zero).Length()<.001,"idle restart holds last confirmed position without jump");
            Check(restart.Sample(5.05,Vector2.Zero).DistanceTo(new Vector2(3.2f,0))<.001,"idle restart smoothly consumes the confirmed step");
            await Frames(3);_focused=true;_awaitMovementRelease=false;
            _hero.Position=_environment.World(new Vector2(640,360));await Frames(3);var start=_hero.Position;
            KeyState(Key.D,true);ulong tickStart=Engine.GetPhysicsFrames();await Frames(60);KeyState(Key.D,false);
            double seconds=(Engine.GetPhysicsFrames()-tickStart)/(double)Engine.PhysicsTicksPerSecond;
            float distance=_hero.Position.X-start.X;double rate=distance/seconds;Check(Math.Abs(rate-64)<3,"offline speed is64pixels/second over actual physics ticks: "+rate);await Frames(3);
            var stop=_hero.Position;await Frames(4);Check(stop.DistanceTo(_hero.Position)<.1,"release stops movement");
            _hero.Position=_environment.World(new Vector2(458,350));await Frames(3);
            KeyState(Key.W,true);await Frames(90);KeyState(Key.W,false);await Frames(3);
            Check(_hero.Position.Y-_environment.DistrictOrigin.Y>=319,"actual physics blocks the central hall foundation");
            _hero.Position=_environment.World(new Vector2(700,470));await Frames(3);
            KeyState(Key.S,true);await Frames(100);KeyState(Key.S,false);await Frames(3);
            Check(_hero.Position.Y-_environment.DistrictOrigin.Y<530&&_environment.IsWalkable(_hero.Position),"actual physics blocks river outside the dock");
            _hero.Position=_environment.World(new Vector2(660,480));await Frames(3);
            KeyState(Key.S,true);await Frames(150);KeyState(Key.S,false);await Frames(3);
            float dockY=_hero.Position.Y-_environment.DistrictOrigin.Y;
            Check(dockY>580&&dockY<604,"actual physics walks deck and stops at dock end: "+dockY);
            var dock=_hero.GetParent().GetNode<Sprite2D>("ART_BM_MAIN_DOCK_A");Check(dock.ZIndex<_hero.ZIndex,"deck renders beneath character");
            _vfx.Clear();int clicks=0;_hud.SkillPressed+=_=>clicks++;
            for(int slot=0;slot<6;slot++)
            {
                GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=true,Position=PreviewHud.SkillCenters()[slot]},true);await Frames(1);
                GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=false,Position=PreviewHud.SkillCenters()[slot]},true);
                Check(_hud.IsPressed(slot),"skill pointer press is visible: "+slot);
                Check(PreviewHud.HitSkill(PreviewHud.SkillCenters()[slot]+new Vector2(17,25))==slot,"skill hotkey badge is part of hit area: "+slot);
            }
            Check(clicks==6&&_vfx.ActiveCount>0,"all six offline skill hit regions route through production handlers");
            GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=true,Position=PreviewHud.AttackCenter},true);await Frames(1);
            GetViewport().PushInput(new InputEventMouseButton{ButtonIndex=MouseButton.Left,Pressed=false,Position=PreviewHud.AttackCenter},true);
            Check(_hud.IsPressed(-1),"attack pointer press is visible");
            GD.Print("MOTION_REGRESSION PASS assertions="+checks);GetTree().Quit();
        }
        catch(Exception ex){GD.PushError("MOTION_REGRESSION FAIL "+ex);GetTree().Quit(1);}
        finally{KeyState(Key.D,false);KeyState(Key.W,false);KeyState(Key.S,false);}
    }
}
