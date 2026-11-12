using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

internal static class Program
{
    private static int checks;
    private static readonly CancellationToken None = CancellationToken.None;
    private static void Check(bool ok, string name) { if (!ok) throw new Exception(name); checks++; Console.WriteLine("PASS " + name); }
    private static P1NarrativeCatalog Catalog(string path) => new P1NarrativeCatalog(P1Wire.Decode<P1NarrativeBundle>(File.ReadAllText(path)));
    private static P1Quest Quest(string state, long revision = 1) => new P1Quest { questId="P00-01", state=state,
        revision=revision,stepId="STEP_P00_01_PACKAGES",objectiveCounters=new Dictionary<string,int>{{"OBJ_P00_01_PACKAGES",state=="AVAILABLE"?0:3}} };
    private sealed class Fake : IP1Transport
    {
        public string State="AVAILABLE"; public bool LoseAccept; public TaskCompletionSource<bool> Hold;
        public readonly List<P1Request> Requests=new List<P1Request>();
        public string Entity="ENT_MAN_BM_NPC_LYAN"; public string Kind="NPC";
        public double ActorX=42, NpcX=42;
        private object World() => new P1World {mapId="MAP_BEN_MUA",revision=1,serverTick=1,
            self=new P1Self {characterId="CHR_TEST",classId="CLASS_MINH_KIEM",x=ActorX,y=0,hp=100,maxHp=100,mp=100,maxMp=100,swordIntent=0},
            entities=new[]{new P1Entity {entityId=Entity,kind=Kind,x=NpcX,y=0,state="IDLE"}}};
        private P1HttpReply Reply(P1Request req, object result, int status=200) => new P1HttpReply {StatusCode=status,
            CorrelationId=req.CorrelationId,Body=P1Wire.Encode(new {schemaVersion=1,requestId=req.CorrelationId,
                sessionId="11111111111111111111111111111111",revision=1,result=result})};
        public async Task<P1HttpReply> SendAsync(P1Request req, CancellationToken ct)
        {
            Requests.Add(req);
            if(Hold!=null && req.Path.StartsWith("/p1/world/")) await Hold.Task;
            if(req.Path=="/p1/sessions")return Reply(req,World(),201);
            if(req.Path.StartsWith("/p1/world/"))return Reply(req,World());
            if(req.Path.StartsWith("/p1/quests/accept"))
            { State="ACTIVE";if(LoseAccept){LoseAccept=false;return new P1HttpReply {StatusCode=0};} return Reply(req,Quest(State,2)); }
            if(req.Path.StartsWith("/p1/quests/turnin"))
            { State="COMPLETED";return Reply(req,new {questState=Quest(State,3),rewards=new {currency=new object[0],items=new object[0],xp=new {xpRule="LEVEL_BAND_BASE",applied=false}},unlocks=new string[0]}); }
            if(req.Path.StartsWith("/p1/quests/"))return Reply(req,new[]{Quest(State,State=="AVAILABLE"?1:2)});
            if(req.Path.StartsWith("/p1/inventory/"))return Reply(req,new P1Inventory {inventoryRevision=1,items=new P1Item[0],currencies=new P1Currency[0]});
            throw new Exception("Unexpected command: "+req.Path);
        }
    }
    private static async Task Unit(string resource)
    {
        var cat=Catalog(resource);
        var bundle=P1Wire.Decode<P1NarrativeBundle>(File.ReadAllText(resource));
        Check(bundle.entries.Select(e=>e.questId).Distinct().Count()==76 && bundle.entries.Length==229,"v3 resource covers all canonical quests and unique nodes");
        Check(!bundle.entries.Where(e=>e.questId.StartsWith("P00-")).SelectMany(e=>e.pages).Any(t=>t.Contains("Cơ Vô Tướng")||t.Contains("ba mươi năm")),"opening pages preserve later identity and timeline reveals");
        var choice=bundle.entries.Single(e=>e.nodeId=="DLG_C3_05_CHOICE");
        Check(!cat.For(choice.speakerId,"MAP_SA_HOA",new[]{new P1Quest {questId="C3-05",state="ACTIVE"}}).Any(e=>e.nodeId==choice.nodeId),"publication choice withheld until verified post-boss checkpoint exists");
        Check(cat.For("NPC_LYAN","MAP_BEN_MUA",new[]{Quest("LOCKED")}).Length==0,"locked quest has no prose");
        Check(cat.For("NPC_LYAN","MAP_THANH_LAC",new[]{Quest("AVAILABLE")}).Length==0,"correct NPC on wrong map cannot reveal opening");
        Check(cat.Npc("NPC_LYAN","MAP_BEN_MUA")==null,"template ID is not fabricated entity identity");
        var t=new Fake();var client=new P1Client(t);await client.ConnectAsync(None);
        using(var flow=new P1NarrativeFlow(client,cat))
        {
            Check(await flow.OpenAsync(t.Entity,None),"open from concrete client snapshots");
            Check(flow.Page.Contains("giữ giúp tôi"),"opening uses authored pages");
            Check(!flow.CanCommand,"accept waits for last instruction page or explicit skip");
            int sent=t.Requests.Count;flow.Reply(0);flow.Next();flow.Previous();
            Check(t.Requests.Count==sent && t.State=="AVAILABLE","reply/page navigation has no command or quest credit");
            flow.SkipToAction();Check(flow.CanCommand,"explicit skip preserves task/action access");
            t.LoseAccept=true;Check(!(await flow.SubmitAsync(None)).Success && flow.CanRetry,"lost accept stays uncertain and offers original retry");
            var first=t.Requests.Last(r=>r.Path=="/p1/quests/accept");
            Check((await flow.RetryAsync(None)).Success && !flow.IsOpen,"confirmed accept returns to gameplay");
            Check(t.Requests.Last(r=>r.Path==first.Path).Body==first.Body,"narrative retry keeps exact original idempotency body");
            t.State="READY_TO_TURN_IN";t.Entity="ENT_MAN_BM_NPC_TA_VAN_KHANH";t.NpcX=t.ActorX=64;
            Check(await flow.OpenAsync(t.Entity,None),"ready state opens Tạ scene");
            Check(!flow.Page.Contains("Huyền Ấn"),"opening turn-in does not reveal seal name");
            flow.SkipToAction();Check((await flow.SubmitAsync(None)).Success && flow.IsOpen,"after-commit scene follows real validated receipt");
            Check(flow.Page.Contains("ghi xong") && !flow.CanCommand,"committed page cannot grant a second reward");
            flow.Reply(0);Check(flow.ReplyText==null,"old pre-commit replies cannot appear over committed scene");
            sent=t.Requests.Count;flow.SkipToAction();flow.Close();Check(t.Requests.Count==sent,"skip/close after commit emits no mutation");
            t.State="AVAILABLE";await client.ReadQuestsAsync(None); // New client below avoids downgrading revisions.
        }
        t=new Fake {ActorX=0};client=new P1Client(t);await client.ConnectAsync(None);
        using(var flow=new P1NarrativeFlow(client,cat))Check(!await flow.OpenAsync(t.Entity,None),"far-away NPC refused");
        t=new Fake {Kind="MOB"};client=new P1Client(t);await client.ConnectAsync(None);
        using(var flow=new P1NarrativeFlow(client,cat))Check(!await flow.OpenAsync(t.Entity,None),"visible hostile cannot impersonate NPC");
        t=new Fake();client=new P1Client(t);await client.ConnectAsync(None);
        using(var flow=new P1NarrativeFlow(client,cat))
        {
            t.Hold=new TaskCompletionSource<bool>();var work=flow.OpenAsync(t.Entity,None);flow.Close();t.Hold.SetResult(true);
            Check(!await work && !flow.IsOpen && flow.Entry==null,"late snapshot after close cannot resurrect prose");
        }
        Check(!t.Requests.Any(r=>r.Path=="/p1/world/interact"),"NPC reading never posts to parcel-only interact endpoint");
        Console.WriteLine("PASS narrative assertions: "+checks);
    }
    private sealed class Http : IP1Transport, IDisposable
    {
        public static string LastWorldDiagnostic;
        public bool LoseTurnInResponseOnce = true;
        private readonly HttpClient client;
        public readonly List<P1Request> Requests=new List<P1Request>();
        public Http(string url) {client=new HttpClient {BaseAddress=new Uri(url)};}
        public async Task<P1HttpReply> SendAsync(P1Request req,CancellationToken ct)
        {
            Requests.Add(req);using(var msg=new HttpRequestMessage(new HttpMethod(req.Method),req.Path))
            {if(req.SessionId!=null)msg.Headers.Add("X-Session-ID",req.SessionId);msg.Headers.Add("X-Correlation-ID",req.CorrelationId);
             if(req.Body!=null)msg.Content=new StringContent(req.Body,Encoding.UTF8,"application/json");
             using(var reply=await client.SendAsync(msg,ct))
             { var body=await reply.Content.ReadAsStringAsync();
               if(req.Path.StartsWith("/p1/v2/world/"))
               {var decoded=P1Wire.Decode<P1Response<P1WorldV2>>(body);LastWorldDiagnostic=P1Wire.Encode(decoded?.result?.entities);}
               if(req.Path=="/p1/quests/turnin" && reply.IsSuccessStatusCode && LoseTurnInResponseOnce)
               {LoseTurnInResponseOnce=false;return new P1HttpReply {StatusCode=0,CorrelationId=req.CorrelationId};}
               return new P1HttpReply {StatusCode=(int)reply.StatusCode,Body=body,CorrelationId=req.CorrelationId};}}
        }
        public void Dispose()=>client.Dispose();
    }
    private static async Task Walk(P1Client c,double x)
    {
        for(int i=0;i<180 && Math.Abs(c.World.self.x-x)>.7;i++)
        {await Task.Delay(150);var delta=Math.Max(-1,Math.Min(1,(x-c.World.self.x)/1.2));var r=await c.MoveAsync(delta,0,None);if(!r.Success)throw new Exception("move: "+r.Code+" entities="+Http.LastWorldDiagnostic);}
        Check(Math.Abs(c.World.self.x-x)<=.7,"HTTP walk near "+x);
    }
    private static async Task HttpRun(string resource,string url)
    {
        using(var http=new Http(url))
        {
            var c=new P1Client(http,useWorldV2:true);Check((await c.ConnectAsync(None)).Success,"HTTP session");
            using(var flow=new P1NarrativeFlow(c,Catalog(resource)))
            {
                Check(!await flow.OpenAsync("ENT_MAN_BM_NPC_LYAN",None),"HTTP remote conversation refused");
                await Walk(c,42);Check(await flow.OpenAsync("ENT_MAN_BM_NPC_LYAN",None),"HTTP authored opening at actual NPC");
                flow.Reply(0);flow.SkipToAction();Check((await flow.SubmitAsync(None)).Success,"HTTP narrative accept");
                foreach(double x in new[]{36d,44d,52d})
                {
                    await Walk(c,x);
                    var parcel=c.World.entities.Where(e=>e.kind=="INTERACTABLE" && e.state=="AVAILABLE").OrderBy(e=>Math.Abs(e.x-x)).First();
                    Check((await c.InteractAsync(parcel.entityId,None)).Success,"HTTP collect existing parcel");
                }
                await Walk(c,64);Check(await flow.OpenAsync("ENT_MAN_BM_NPC_TA_VAN_KHANH",None),"HTTP READY scene");
                flow.SkipToAction();Check(!(await flow.SubmitAsync(None)).Success && flow.CanRetry,"HTTP lost turn-in response stays uncertain");
                Check(!flow.Page.Contains("ghi xong"),"HTTP missing receipt cannot show after-commit prose");
                var sent=http.Requests.Last(r=>r.Path=="/p1/quests/turnin");
                Check((await flow.RetryAsync(None)).Success,"HTTP retry turn-in through narrative");
                Check(http.Requests.Last(r=>r.Path==sent.Path).Body==sent.Body,"HTTP turn-in retry preserves exact request body");
                Check(flow.IsOpen && flow.Page.Contains("ghi xong") && c.LastTurnIn!=null,"HTTP receipt opens after-commit scene");
                Check(c.Inventory!=null && c.Inventory.items.Length>0,"HTTP inventory from real readback");
                Check(c.Inventory.currencies.Single(i=>i.currencyId=="COIN").amount==20 &&
                    c.Inventory.items.Length==1 && c.Inventory.items[0].templateId=="EQ-MK-CHEST-T1-R-COMMON" && c.Inventory.items[0].stack==1,
                    "HTTP lost receipt/replay grants exactly source 20 coin and one chest item");
                long inventoryRevision=c.Inventory.inventoryRevision;
                var grants=http.Requests.Count(r=>r.Path=="/p1/quests/turnin");flow.SkipToAction();flow.Close();
                Check(http.Requests.Count(r=>r.Path=="/p1/quests/turnin")==grants,"HTTP skip/close does not repeat reward");
                Check((await c.ReadInventoryAsync(None)).Success && c.Inventory.inventoryRevision==inventoryRevision &&
                    c.Inventory.currencies.Single(i=>i.currencyId=="COIN").amount==20,"HTTP after-close readback keeps one grant");
                Check(!http.Requests.Any(r=>r.Path=="/p1/world/interact" && r.Body.Contains("NPC_")),"HTTP NPC route never misuses node interact");
            }
        }
        Console.WriteLine("PASS narrative HTTP assertions: "+checks);
    }
    public static async Task<int> Main(string[] args)
    {try {if(args.Length==3 && args[1]=="--http")await HttpRun(args[0],args[2]);else await Unit(args[0]);return 0;}catch(Exception e){Console.Error.WriteLine(e);return 1;}}
}
