using Godot;
using System;
using System.Linq;
using System.Threading.Tasks;
using NguMach.Client.P1;
namespace Ngumach.VisualReboot;

public partial class VisualPreview
{
    private async void RunTargetTests()
    {
        int checks=0;void Check(bool ok,string label){checks++;if(!ok)throw new InvalidOperationException(label);}
        async Task Frames(int n){for(int i=0;i<n;i++)await ToSignal(GetTree(),SceneTree.SignalName.ProcessFrame);}
        async Task Click(Vector2 point,MouseButton button=MouseButton.Left)
        {GetViewport().PushInput(new InputEventMouseButton{Position=point,Pressed=true,ButtonIndex=button},true);await Frames(1);GetViewport().PushInput(new InputEventMouseButton{Position=point,Pressed=false,ButtonIndex=button},true);}
        P1EntityV2 Mob(string id,double x,double y,string kind="MOB",int hp=60,long life=1)=>new(){entityId=id,kind=kind,x=x,y=y,hp=hp,maxHp=60,targetable=hp>0,healthState=hp>0?"ALIVE":"DEAD",state=hp>0?"IDLE":"DEAD",lifeId=life,revision=1,mapInstanceId="TEST",floorId="OVERWORLD",phase="TEST"};
        var self=new P1Self{characterId="TEST_HERO",classId="CLASS_MINH_KIEM",x=36,y=0,hp=100,maxHp=100,mp=50,maxMp=50};
        NativeOnlineFrame Frame(long revision,P1EntityV2[] entities,P1EventV2[]? events=null,string session="TEST",string? action=null,string? skill=null)=>new(){AcceptedAction=action,AcceptedSkill=skill,SessionId=session,SampleTime=AuthoritativeMotion.Now,
            World=new(){mapId="MAP_BEN_MUA",self=self,revision=revision,entities=entities.Select(e=>new P1Entity{entityId=e.entityId,kind=e.kind,x=e.x,y=e.y,hp=e.hp,maxHp=e.maxHp,state=e.state,healthState=e.healthState,targetable=e.targetable}).ToArray()},
            WorldV2=new(){mapId="MAP_BEN_MUA",mapInstanceId="TEST",floorId="OVERWORLD",phase="TEST",revision=revision,self=self,entities=entities},Events=events??Array.Empty<P1EventV2>()};
        P1EventV2 Event(long cursor,string target="TEST_SPAWN_BM_01_A",long life=1)=>new(){eventId="EV"+cursor,cursor=cursor,mapInstanceId="TEST",floorId="OVERWORLD",actorId="TEST_HERO",castId="CAST"+cursor,type="IMPACT",targetId=target,targetLifeId=life,result=new(){hit=true,hpDamage=12,amount=12}};
        try
        {
            GD.Print("TARGET_TEST_MODE SOURCE_DTO_AND_ENGINE_POINTER_FIXTURE_NO_HTTP_NO_GRANTS");
            _captureStarted=true;
            _liveActors=new NativeActorsView();_hero.GetParent().AddChild(_liveActors);
            _liveActors.TargetChanged+=()=>_hud.ApplyTarget(_liveActors.TargetInfo);
            var a=Mob("TEST_SPAWN_BM_01_A",35,2);var b=Mob("TEST_SPAWN_BM_02_B",40,2);
            var far=Mob("TEST_SPAWN_BM_01_FAR",120,0);var npc=Mob("TEST_NPC_LYAN",36,1,"NPC");
            var unknown=Mob("TEST_SPAWN_BM_04_MIXED",37,1);
            ApplyOnlineFrame(Frame(1,new[]{a,b,far,npc,unknown}));await Frames(4);
            var point=GetViewport().GetCanvasTransform()*(NativeActorsView.RenderPoint(a.x,a.y)+new Vector2(0,-12));
            await Click(point);Check(_liveActors.TargetId==a.entityId,"pointer selects visible living mob");
            Check(_hud.CombatTarget?.Hp==60&&_hud.CombatTarget.Name=="Cá Linh","target HUD binds authoritative name/HP");
            _liveActors.CycleTarget(WorldView());Check(_liveActors.TargetId==b.entityId,"Tab advances rather than reselecting nearest");
            _liveActors.CycleTarget(WorldView());Check(_liveActors.TargetId==a.entityId,"Tab wraps only valid visible hostile art");
            _liveActors.CycleTarget(WorldView(),true);Check(_liveActors.TargetId==b.entityId,"reverse cycle wraps");
            await Click(new Vector2(650,450),MouseButton.Right);Check(_liveActors.TargetId==null,"right pointer clears target");
            await Click(point);await Click(new Vector2(805,40));Check(_liveActors.TargetId==null,"target panel close clears target");
            Check(_hud.BlocksWorldPointer(new Vector2(40,50))&&!_hud.BlocksWorldPointer(new Vector2(650,450)),"HUD blocks world picking while map stays interactive");
            Check(!_liveActors.SelectAt(NativeActorsView.RenderPoint(npc.x,npc.y),WorldView()),"NPC cannot become a combat target");
            _liveActors.TargetId=a.entityId;
            var dead=Mob(a.entityId,a.x,a.y,hp:0);ApplyOnlineFrame(Frame(2,new[]{dead,b,far,npc,unknown}));
            Check(_liveActors.TargetId==null&&_hud.CombatTarget==null,"death clears selection and HUD");
            var next=Mob(a.entityId,a.x,a.y,life:2);ApplyOnlineFrame(Frame(3,new[]{next,b,far}));_liveActors.TargetId=a.entityId;
            next=Mob(a.entityId,a.x,a.y,life:3);ApplyOnlineFrame(Frame(4,new[]{next,b,far}));
            Check(_liveActors.TargetId==null,"same entity respawn does not inherit a previous-life lock");
            _liveActors.TargetId=b.entityId;_liveActors.UpdateFrame(Frame(3,new[]{a}));
            Check(_liveActors.TargetId==b.entityId,"stale snapshot cannot replace current target state");
            var old=_liveActors.VisualPosition(b.entityId);var moved=Mob(b.entityId,42,2);
            _liveActors.UpdateFrame(Frame(5,new[]{next,moved,far}));Check(_liveActors.VisualPosition(b.entityId)==old,"remote sprite does not jump directly to a packet position");
            await Frames(18);Check(_liveActors.VisualPosition(b.entityId).DistanceTo(NativeActorsView.RenderPoint(42,2))<1,"remote interpolation reaches confirmed position");
            ApplyOnlineFrame(Frame(6,new[]{next,moved,far},new[]{Event(1,b.entityId)}));Check(_vfx.FeedbackCount==1,"confirmed same-life impact creates hit feedback");
            ApplyOnlineFrame(Frame(6,new[]{next,moved,far},new[]{Event(1,b.entityId)}));Check(_vfx.FeedbackCount==1,"duplicate event creates no second hit text");
            ApplyOnlineFrame(Frame(7,new[]{next,moved,far},new[]{Event(2,a.entityId,2)}));Check(_vfx.FeedbackCount==1,"previous-life hit cannot flash respawned enemy");
            var wrong=Event(3,b.entityId);wrong.floorId="OTHER";ApplyOnlineFrame(Frame(8,new[]{next,moved,far},new[]{wrong}));Check(_vfx.FeedbackCount==1,"wrong floor event creates no hit feedback");
            _vfx.GuardCue(_hero.Position,"TEST_GUARD");_vfx.Clear();Check(_vfx.FeedbackCount==0,"cancel/context cleanup removes guard and hit feedback");
            for(int i=0;i<40;i++)_vfx.Impact(new(){hit=true,hpDamage=1},_hero.Position);Check(_vfx.FeedbackCount==24,"hit feedback is bounded");_vfx.Clear();
            ApplyOnlineFrame(Frame(9,new[]{far,npc,unknown}));Check(_liveActors.CombatTarget(WorldView())==null,"automatic combat never acquires invisible/offscreen/friendly actors");
            var gate=new CombatEventGate();gate.Bind(Frame(1,new[]{a}));
            Check(gate.Accept(Event(12))&&gate.Accept(Event(11)),"out-of-order events within bounded window remain presentable");
            Check(!gate.Accept(Event(12)),"same cursor and event are deduplicated");
            for(int i=13;i<=1100;i++)gate.Accept(Event(i));
            Check(gate.RetainedCount<=1024&&!gate.Accept(Event(11)),"evicted old events cannot replay after cache pressure");
            var start=Event(4);start.type="CAST_START";start.result=null;
            ApplyOnlineFrame(Frame(10,new[]{a,b},new[]{start},action:"BASIC_ATTACK"));
            var end=Event(5);end.type="END";end.result=null;end.castId=start.castId;
            ApplyOnlineFrame(Frame(11,new[]{a,b},new[]{end}));Check(_hud.CombatHint.Contains("không trúng",StringComparison.Ordinal),"damage cast END without impact has explicit whiff feedback");
            var guard=Event(6);guard.type="CAST_START";guard.result=null;
            ApplyOnlineFrame(Frame(12,new[]{a,b},new[]{guard},action:"CAST",skill:"SK-MK-01"));
            var guardEnd=Event(7);guardEnd.type="END";guardEnd.result=null;guardEnd.castId=guard.castId;
            ApplyOnlineFrame(Frame(13,new[]{a,b},new[]{guardEnd}));Check(!_hud.CombatHint.Contains("không trúng",StringComparison.Ordinal),"guard ending is never misreported as a missed damage cast");
            ApplyOnlineFrame(Frame(1,new[]{a,b},session:"NEW_SESSION"));Check(_liveActors.TargetId==null,"session change clears target identity");
            _hudHidden=true;await Frames(2);await Click(PreviewHud.AttackCenter);
            Check(!_hud.IsPressed(-1),"hidden HUD cannot intercept attack-area world clicks");
            _hudHidden=false;await Frames(2);
            var overlap=Mob(b.entityId,a.x,a.y);ApplyOnlineFrame(Frame(2,new[]{a,overlap},session:"NEW_SESSION"));
            _liveActors.TargetId=a.entityId;await Frames(3);
            Check(_liveActors.GetChildren().SelectMany(n=>n.GetChildren()).OfType<Label>().Count(l=>l.Visible&&l.Text=="Cá Linh")==1,"overlapping mob names keep the selected target readable");
            var label=new Label{Text="KIỂM UI BẰNG FIXTURE · KHÔNG PHẢI COMBAT ONLINE",Position=new Vector2(390,135)};_hud.AddChild(label);
            if(_capture!=null){await ToSignal(RenderingServer.Singleton,RenderingServer.SignalName.FramePostDraw);Check(GetViewport().GetTexture().GetImage().SavePng(_capture)==Error.Ok,"native target fixture capture");}
            GD.Print("TARGET_SELF_TEST PASS assertions="+checks);GetTree().Quit();
        }
        catch(Exception e){GD.PushError("TARGET_SELF_TEST FAIL "+e);GetTree().Quit(1);}
    }
}
