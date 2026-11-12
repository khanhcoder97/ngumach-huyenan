using Godot;
using System;
using System.Diagnostics;
using System.Linq;
using System.Threading.Tasks;
using NguMach.Client.P1;
namespace Ngumach.VisualReboot;

/// <summary>Real ordinary loopback session, public movement and production pointer handlers.
/// No private grant, fixture spawn, teleport, forced RNG or client-authored damage.</summary>
public partial class NativeCombatAcceptance : Node
{
    private NativeOnlineSession _session=null!;
    private NativeActorsView _actors=null!;
    private PreviewHud _hud=null!;
    private SkillVfxPlayer _vfx=null!;
    private string _capture="";
    private int _checks,_impacts;
    private P1EventV2? _lastImpact;
    private readonly Stopwatch _clock=Stopwatch.StartNew();
    public void Configure(NativeOnlineSession session,NativeActorsView actors,PreviewHud hud,SkillVfxPlayer vfx,string capture)
    {_session=session;_actors=actors;_hud=hud;_vfx=vfx;_capture=capture;_session.FrameReady+=Observe;Run();}
    private void Observe(NativeOnlineFrame frame)
    {foreach(var e in frame.Events.Where(e=>e.actorId==frame.World?.self.characterId)){GD.Print("COMBAT_EVENT "+e.type+" target="+e.targetId+" hpDamage="+e.result?.hpDamage);if(e.type=="END")_impacts++;if(e.result!=null)_lastImpact=e;}}
    private void Check(bool okay,string label){_checks++;if(!okay)throw new InvalidOperationException(label);GD.Print("COMBAT_CHECK "+label);}
    private async Task Frames(int n){for(int i=0;i<n;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);}
    private async Task Wait(Func<bool> predicate,double seconds)
    {
        double start=_clock.Elapsed.TotalSeconds;
        while(!predicate())
        {if(_clock.Elapsed.TotalSeconds-start>seconds||_clock.Elapsed.TotalSeconds>90)throw new TimeoutException("combat acceptance timed out: "+_hud.CombatHint);await Frames(1);}
    }
    private async Task Click(Vector2 point,MouseButton button=MouseButton.Left)
    {GetViewport().PushInput(new InputEventMouseButton{Position=point,Pressed=true,ButtonIndex=button},true);await Frames(1);GetViewport().PushInput(new InputEventMouseButton{Position=point,Pressed=false,ButtonIndex=button},true);await Frames(1);}
    private async Task Capture(string name)
    {await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);Check(GetViewport().GetTexture().GetImage().SavePng(System.IO.Path.Combine(System.IO.Path.GetDirectoryName(_capture)!,name))==Error.Ok,"native capture "+name);}
    private async Task Walk(Vector2 destination)
    {
        await Wait(()=>
        {
            var self=_session.Frame.World!.self;var delta=destination-new Vector2((float)self.x,(float)self.y);
            if(delta.Length()<.22){_session.SetMove(Vector2.Zero);return true;}
            _session.SetMove(delta.Normalized());return false;
        },20);
        _session.SetMove(Vector2.Zero);await Frames(2);
    }
    private async void Run()
    {
        try
        {
            GD.Print("NATIVE_COMBAT_MODE REAL_HTTP_AND_VIEWPORT_POINTER_NOT_HARDWARE_MOUSE");
            await Wait(()=>_session.Frame.ConnectionState==P1ConnectionState.Ready&&_session.Frame.WorldV2!=null&&_session.Frame.Inventory!=null,20);
            Check(Math.Abs(_session.Frame.World!.self.x-18)<.01,"ordinary authoritative spawn remains x18");
            // Authored terrain route, .85WU clearance; movement still accepted/rejected by server.
            foreach(var waypoint in new[]{new Vector2(18,1),new(31,1),new(31,1.5f),new(34.5f,1.5f),new(34.5f,2),new(45.5f,2),new(45.5f,2.5f),new(68,2.5f),new(68,3),new(84,3)})await Walk(waypoint);
            Check(Math.Abs(_session.Frame.World!.self.x-84)<.3&&Math.Abs(_session.Frame.World.self.y-3)<.3,"walked from village to real fish spawn along dry bank");
            await Frames(10);
            var entity=_session.Frame.World.entities.First(e=>e.entityId=="ENT_MAN_BM_SPAWN_BM_01");
            Check(entity.targetable==true&&entity.healthState=="ALIVE"&&entity.hp>0,"real enemy is living and targetable");
            var point=GetViewport().GetCanvasTransform()*(_actors.VisualPosition(entity.entityId)+new Vector2(0,-12));
            await Click(point);Check(_actors.TargetId!=null,"pointer selects a rendered real enemy");
            string target=_actors.TargetId!;
            Check(_hud.CombatTarget?.EntityId==target&&_hud.CombatTarget.Hp==entity.hp,"target HUD reads server HP");
            bool profiled=false;AddChild(new FrameProfile{OutputPath=System.IO.Path.Combine(System.IO.Path.GetDirectoryName(_capture)!,"performance_combat.json"),Completed=()=>profiled=true});
            await Wait(()=>profiled,20);Check(_actors.TargetId==target,"target remains stable during real online frame profile");
            GetViewport().PushInput(new InputEventKey{Keycode=Key.Tab,PhysicalKeycode=Key.Tab,Pressed=true},true);await Frames(1);
            GetViewport().PushInput(new InputEventKey{Keycode=Key.Tab,PhysicalKeycode=Key.Tab,Pressed=false},true);
            Check(_actors.TargetId!=target&&_actors.TargetId!=null,"native Tab changes real group member");
            // Basic cone picks nearest entity, not an exact targetId when spawn members overlap.
            // Re-pick the deterministic first rendered member before checking its actual HP.
            await Click(point);target=_actors.TargetId!;
            Check(target==entity.entityId,"re-pick nearest member for authoritative cone target semantics");
            int before=_session.Frame.World.entities.First(e=>e.entityId==target).hp;
            for(int attempt=0;attempt<5;attempt++)
            {
                await Wait(()=>_hud.Cooldown(-1)<=0,8);int eventsBefore=_impacts;
                _lastImpact=null;GD.Print("COMBAT_AIM from="+_session.Frame.World!.self.x+","+_session.Frame.World.self.y+" to="+entity.x+","+entity.y);
                await Click(PreviewHud.AttackCenter);await Wait(()=>_session.Frame.CooldownEnds.ContainsKey("BASIC_ATTACK"),8);
                await Wait(()=>_impacts>eventsBefore,8);
                if(_lastImpact?.targetId==target&&_lastImpact.result.hpDamage>0)break;
            }
            Check(_session.Frame.CooldownEnds.ContainsKey("BASIC_ATTACK"),"attack button receives authoritative acceptance");
            Check(_vfx.FeedbackCount>0,"real impact reaches life-scoped VFX feedback");
            await Wait(()=>_session.Frame.World!.entities.First(e=>e.entityId==target).hp<before,8);
            Check(_hud.CombatTarget?.Hp<before,"confirmed attack HP change reaches target panel");
            await Capture("native_combat_hit.png");
            await Click(PreviewHud.SkillCenters()[2]);
            await Wait(()=>_session.Frame.CooldownEnds.ContainsKey("SK-MK-03"),8);
            Check(_session.Frame.World!.self.mp<50,"targeted skill consumes real MP");
            Check(_hud.Cooldown(2)>0,"targeted skill cooldown displayed from receipt");
            string end=_session.Frame.CooldownEnds["SK-MK-03"];int mp=_session.Frame.World.self.mp;
            await Click(PreviewHud.SkillCenters()[2]);Check(_hud.CombatHint.Contains("Đang hồi",StringComparison.Ordinal),"fresh second pointer cast reports cooldown");
            await Frames(4);Check(_session.Frame.World!.self.mp==mp&&_session.Frame.CooldownEnds["SK-MK-03"]==end,"rejected repeated input consumes nothing extra");
            await Capture(System.IO.Path.GetFileName(_capture));
            await Click(new Vector2(650,470),MouseButton.Right);Check(_actors.TargetId==null&&_hud.CombatTarget==null,"native right-click clears real target and HUD");
            Check(_session.Frame.Inventory!.currencies.All(c=>c.amount==0)&&_session.Frame.Inventory.items.Length==0,"combat test grants no local loot or quest reward");
            GD.Print("NATIVE_COMBAT_PASS assertions="+_checks);GetTree().Quit();
        }
        catch(Exception e){try{await Capture("native_combat_failure.png");}catch{}GD.PushError("NATIVE_COMBAT_FAIL "+e);GetTree().Quit(1);}
        finally{_session.SetMove(Vector2.Zero);}
    }
    public override void _ExitTree(){if(_session!=null)_session.FrameReady-=Observe;}
}
