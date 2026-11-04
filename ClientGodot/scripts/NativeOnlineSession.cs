#nullable enable
using Godot;
using System;
using System.Collections.Concurrent;
using System.Diagnostics;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Transport;
using NguMach.Client.P1;
using NetHttpClient = System.Net.Http.HttpClient;

namespace Ngumach.VisualReboot;

/// <summary>Codex-owned Godot host for the existing portable P1 client.
/// One worker owns all client reads/mutations. Only detached frames enter the
/// Godot main thread. This host does not own authoritative gameplay or map data.</summary>
public partial class NativeOnlineSession : Node
{
    private const string Quest = "P00-01";
    private const string Chest = "EQ-MK-CHEST-T1-R-COMMON";
    private readonly object _inputLock = new();
    private Vector2 _movement;
    private Run? _run;
    private long _epoch;
    private int _exited;

    public event Action<NativeOnlineFrame>? FrameReady;
    public event Action<int>? ScenarioPassed;
    public event Action<string>? ScenarioFailed;
    public NativeOnlineFrame Frame { get; private set; } = new();

    private sealed record Intent(string Kind,string Target,string QuestId,string Skill,double AimX,double AimY);

    private sealed class Run
    {
        public readonly long Epoch;
        public readonly string BaseUrl;
        public readonly bool Scenario;
        public readonly CancellationTokenSource Lifetime = new();
        public readonly CancellationToken Token;
        public readonly HttpClientTransport RawHttp;
        public readonly P1Client Client;
        public readonly DropTurnInReply? Drop;
        public readonly ConcurrentQueue<Intent> Commands = new();
        public readonly Stopwatch Clock = Stopwatch.StartNew();
        public Task? Pump;
        public string Message = "Đang kết nối máy chủ...";
        public int Assertions;
        public bool Complete;
        public volatile bool Finished, MutationInFlight, PendingForHost;
        public string? HostNotice;
        public volatile bool QueueOverflow;
        private int _networkDisposed;

        public Run(long epoch,string url,bool scenario)
        {
            Epoch=epoch;BaseUrl=url.TrimEnd('/');Scenario=scenario;Token=Lifetime.Token;
            RawHttp=new HttpClientTransport(url,new NetHttpClient{Timeout=TimeSpan.FromSeconds(8)});
            if(scenario) Drop=new DropTurnInReply(RawHttp);
            Client=new P1Client((IP1Transport?)Drop??RawHttp,useWorldV2:true);
        }

        public void RequestStop()
        {
            try{Lifetime.Cancel();}catch(ObjectDisposedException){}
            // Safe for an active HttpClient send; the worker owns the final CTS cleanup.
            RawHttp.Dispose();
        }

        public void DisposeNetwork()
        {
            if(Interlocked.Exchange(ref _networkDisposed,1)!=0)return;
            RawHttp.Dispose();
            Lifetime.Dispose();
        }
    }

    // Test seam: the actual server commits a successful turn-in before its reply is lost.
    // Request bytes are observed, never changed. Only scenario mode installs this wrapper.
    private sealed class DropTurnInReply : IP1Transport
    {
        private readonly IP1Transport _inner;
        private bool _drop=true;
        public readonly System.Collections.Generic.List<string> Bodies = new();
        public bool Dropped { get; private set; }
        public DropTurnInReply(IP1Transport inner)=>_inner=inner;

        public async Task<P1HttpReply> SendAsync(P1Request request,CancellationToken ct)
        {
            bool turnIn=request.Path=="/p1/quests/turnin";
            if(turnIn) Bodies.Add(request.Body);
            var reply=await _inner.SendAsync(request,ct).ConfigureAwait(false);
            if(turnIn&&_drop&&reply.StatusCode>=200&&reply.StatusCode<300)
            {
                var body=P1Wire.Decode<P1Response<P1TurnInResult>>(reply.Body);
                if(body.error==null&&body.result?.questState?.state=="COMPLETED")
                {
                    _drop=false;Dropped=true;
                    return new P1HttpReply{StatusCode=0,CorrelationId=request.CorrelationId};
                }
            }
            return reply;
        }
    }

    /// <summary>Call from the Godot main thread after adding this node to the tree.
    /// Re-start invalidates all queued publications from the previous lifetime.</summary>
    public void Start(string baseUrl,bool scenario=false)
    {
        if(!Uri.TryCreate(baseUrl,UriKind.Absolute,out var uri)||
            (uri.Scheme!=Uri.UriSchemeHttp&&uri.Scheme!=Uri.UriSchemeHttps))
            throw new ArgumentException("An absolute HTTP(S) server URL is required.",nameof(baseUrl));
        if(scenario&&!uri.IsLoopback)
            throw new ArgumentException("The mutation/retry test requires a loopback server.",nameof(baseUrl));
        Run run;
        lock(_inputLock)
        {
            var previous=Volatile.Read(ref _run);
            // Starting another connection must never silently abandon an ambiguous grant.
            if(previous!=null&&(previous.PendingForHost||previous.MutationInFlight||
                (previous.Scenario&&!previous.Finished)))
            {
                Interlocked.Exchange(ref previous.HostNotice,"Còn thao tác chưa rõ kết quả; hãy dùng RETRY trước khi mở phiên mới.");
                return;
            }
            Volatile.Write(ref _exited,0);
            Interlocked.Increment(ref _epoch);
            previous?.RequestStop();
            _movement=Vector2.Zero;
            run=new Run(Interlocked.Read(ref _epoch),baseUrl,scenario);
            Volatile.Write(ref _run,run);
        }
        run.Pump=Task.Run(()=>PumpAsync(run));
    }

    /// <summary>Canonical server axes, not canvas axes: positive Y is up.
    /// A direction only; no position/teleport is sent. Modal/focus owners must send zero.</summary>
    public void SetMove(Vector2 canonicalDirection)
    {
        if(!float.IsFinite(canonicalDirection.X)||!float.IsFinite(canonicalDirection.Y))
            canonicalDirection=Vector2.Zero;
        if(canonicalDirection.LengthSquared()>1)canonicalDirection=canonicalDirection.Normalized();
        lock(_inputLock)_movement=canonicalDirection;
    }

    public void Command(string kind,string targetId="",string questId="",string skillId="",double aimX=1,double aimY=0)
    {
        var run=Volatile.Read(ref _run);
        if(run==null||run.Scenario||run.Token.IsCancellationRequested)return;
        if(run.Commands.Count>=32){run.QueueOverflow=true;return;}
        run.Commands.Enqueue(new Intent((kind??"").Trim().ToUpperInvariant(),targetId,questId,skillId,aimX,aimY));
    }

    private async Task PumpAsync(Run run)
    {
        try
        {
            Publish(run);
            var connect=await run.Client.ConnectAsync(run.Token).ConfigureAwait(false);
            Require(connect,"Kết nối");
            await RefreshAsync(run,true).ConfigureAwait(false);
            run.Message="Đã kết nối máy chủ.";
            Publish(run);
            if(run.Scenario)
            {
                await RunScenarioAsync(run).ConfigureAwait(false);
                return;
            }
            long nextWorld=run.Clock.ElapsedMilliseconds+300,nextEvents=run.Clock.ElapsedMilliseconds+300;
            while(!run.Token.IsCancellationRequested)
            {
                var hostNotice=Interlocked.Exchange(ref run.HostNotice,null);
                if(hostNotice!=null){run.Message=hostNotice;Publish(run);}
                if(run.QueueOverflow)
                {
                    run.QueueOverflow=false;
                    run.Message="Hàng đợi thao tác đã đầy; chờ thao tác trước hoàn tất.";
                    Publish(run);
                }
                if(run.Commands.TryDequeue(out var intent))
                {
                    await ExecuteAsync(run,intent).ConfigureAwait(false);
                    nextWorld=run.Clock.ElapsedMilliseconds+300;
                    continue;
                }
                Vector2 move;
                lock(_inputLock)move=_movement;
                if(move!=Vector2.Zero&&run.Client.State==P1ConnectionState.Ready&&!run.Client.HasPendingMutation)
                {
                    var result=await run.Client.MoveAsync(move.X,move.Y,run.Token).ConfigureAwait(false);
                    if(!result.Success)run.Message=Failure("Di chuyển",result);
                    Publish(run);
                    nextWorld=run.Clock.ElapsedMilliseconds+300;
                }
                else if(run.Clock.ElapsedMilliseconds>=nextWorld)
                {
                    var result=await run.Client.ReadWorldAsync(run.Token).ConfigureAwait(false);
                    if(!result.Success)run.Message=Failure("Đồng bộ thế giới",result);
                    Publish(run);
                    nextWorld=run.Clock.ElapsedMilliseconds+300;
                }
                if(run.Client.WorldV2!=null&&run.Clock.ElapsedMilliseconds>=nextEvents)
                {
                    var events=await run.Client.ReadEventsAsync(run.Token).ConfigureAwait(false);
                    if(!events.Success)run.Message=Failure("Đồng bộ sự kiện",events);
                    Publish(run);
                    nextEvents=run.Clock.ElapsedMilliseconds+300;
                }
                await Task.Delay(100,run.Token).ConfigureAwait(false);
            }
        }
        catch(OperationCanceledException) when(run.Token.IsCancellationRequested){}
        catch(Exception ex)
        {
            if(!run.Token.IsCancellationRequested)
            {
                run.Message=ex.Message;
                Publish(run,failed:run.Scenario?ex.Message:null);
            }
        }
        finally{run.Finished=true;run.DisposeNetwork();}
    }

    private async Task ExecuteAsync(Run run,Intent intent)
    {
        var c=run.Client;
        lock(_inputLock)
        {
            if(!ReferenceEquals(Volatile.Read(ref _run),run)||run.Token.IsCancellationRequested)return;
            run.MutationInFlight=intent.Kind!="REFRESH";
        }
        try
        {
        P1Result result;
        switch(intent.Kind)
        {
            case "ACCEPT": result=await c.AcceptQuestAsync(intent.QuestId,intent.Target,run.Token).ConfigureAwait(false);break;
            case "INTERACT": result=await c.InteractAsync(intent.Target,run.Token).ConfigureAwait(false);break;
            case "TURNIN": result=await c.TurnInQuestAsync(intent.QuestId,intent.Target,run.Token).ConfigureAwait(false);break;
            case "RETRY": result=await c.RetryPendingAsync(run.Token).ConfigureAwait(false);break;
            case "BASIC_ATTACK":result=await c.BasicAttackAsync(intent.Target,intent.AimX,intent.AimY,run.Token).ConfigureAwait(false);break;
            case "CAST":result=await c.CastAsync(intent.Skill,intent.Target,intent.AimX,intent.AimY,run.Token).ConfigureAwait(false);break;
            case "REFRESH":
                if(await RefreshAsync(run,false).ConfigureAwait(false))run.Message="Đã đồng bộ thế giới, nhiệm vụ và túi đồ.";
                Publish(run);return;
            default:
                run.Message="Thao tác chưa được hỗ trợ: "+intent.Kind;
                Publish(run);return;
        }
        run.Message=result.Success?"Máy chủ đã xác nhận: "+intent.Kind:Failure(intent.Kind,result);
        // Only this publication carries an action edge. Polls never re-emit it.
        Publish(run,result.Success?intent.Kind:null,result.Success&&intent.Kind=="CAST"?intent.Skill:null);
        await RefreshAsync(run,false).ConfigureAwait(false);
        Publish(run);
        }
        finally{run.PendingForHost=c.HasPendingMutation;run.MutationInFlight=false;}
    }

    private async Task<bool> RefreshAsync(Run run,bool required)
    {
        var c=run.Client;
        bool okay=true;
        foreach(var item in new (string Name,Func<Task<P1Result>> Read)[]
        {
            ("thế giới",()=>c.ReadWorldAsync(run.Token)),
            ("nhiệm vụ",()=>c.ReadQuestsAsync(run.Token)),
            ("túi đồ",()=>c.ReadInventoryAsync(run.Token))
        })
        {
            var result=await item.Read().ConfigureAwait(false);
            if(required)Require(result,item.Name);
            else if(!result.Success){okay=false;run.Message=Failure(item.Name,result);}
        }
        if(c.WorldV2!=null)
        {
            var events=await c.ReadEventsAsync(run.Token).ConfigureAwait(false);
            if(required)Require(events,"sự kiện");
            else if(!events.Success){okay=false;run.Message=Failure("sự kiện",events);}
        }
        return okay;
    }

    private void Publish(Run run,string? action=null,string? skill=null,string? failed=null,bool passed=false)
    {
        // All reads/clones run on the sole client worker, never concurrently with a mutation.
        run.PendingForHost=run.Client.HasPendingMutation;
        var frame=new NativeOnlineFrame
        {
            SessionId=run.Client.SessionId??"",
            ConnectionState=run.Client.State,
            Message=run.Message,
            World=Clone(run.Client.World),
            WorldV2=Clone(run.Client.WorldV2),
            Quests=Clone(run.Client.Quests)??Array.Empty<P1Quest>(),
            Inventory=Clone(run.Client.Inventory),
            Events=Clone(run.Client.DrainPresentationEvents())??Array.Empty<P1EventV2>(),
            AcceptedAction=action,AcceptedSkill=skill,
            ScenarioComplete=run.Complete,Assertions=run.Assertions
        };
        Callable.From(()=>
        {
            if(!GodotObject.IsInstanceValid(this)||Volatile.Read(ref _exited)!=0||
                Interlocked.Read(ref _epoch)!=run.Epoch||!ReferenceEquals(Volatile.Read(ref _run),run)||
                run.Token.IsCancellationRequested||!IsInsideTree())return;
            Frame=frame;
            try{FrameReady?.Invoke(frame);}
            catch(Exception ex)
            {
                GD.PushError("Native online frame consumer failed: "+ex);
                if(run.Scenario)ScenarioFailed?.Invoke("Native frame consumer: "+ex.Message);
                return;
            }
            if(failed!=null)
            {
                GD.PushError("NATIVE_P00_01_FAIL "+failed);
                ScenarioFailed?.Invoke(failed);
            }
            if(passed)
            {
                GD.Print("NATIVE_P00_01_PASS assertions="+frame.Assertions);
                ScenarioPassed?.Invoke(frame.Assertions);
            }
        }).CallDeferred();
    }

    private static T? Clone<T>(T? value) where T:class =>
        value==null?null:P1Wire.Decode<T>(P1Wire.Encode(value));

    private static string Failure(string operation,P1Result result)=>
        operation+": "+(result.Code??"network_unavailable")+
        (string.IsNullOrEmpty(result.CorrelationId)?"":" ["+result.CorrelationId+"]");

    private static void Require(P1Result result,string operation)
    {
        if(!result.Success)throw new InvalidOperationException(Failure(operation,result));
    }

    private static long Coins(P1Inventory? inventory)=>
        inventory?.currencies?.Where(c=>c.currencyId=="COIN").Sum(c=>c.amount)??0;
    private static int Chests(P1Inventory? inventory)=>
        inventory?.items?.Where(i=>i.templateId==Chest).Sum(i=>i.stack)??0;

    private void Check(Run run,bool condition,string message)
    {
        run.Assertions++;
        if(!condition)throw new InvalidOperationException("Scenario assertion: "+message);
    }

    private async Task WalkToAsync(Run run,double targetX)
    {
        long deadline=run.Clock.ElapsedMilliseconds+45000;
        run.Message="Đi tới mốc "+targetX.ToString("0.#",System.Globalization.CultureInfo.InvariantCulture);
        while(Math.Abs(run.Client.World.self.x-targetX)>.75)
        {
            run.Token.ThrowIfCancellationRequested();
            if(run.Clock.ElapsedMilliseconds>deadline)throw new TimeoutException("Không đi được tới mốc "+targetX);
            await Task.Delay(100,run.Token).ConfigureAwait(false);
            double dx=Math.Clamp((targetX-run.Client.World.self.x)/1.2,-1,1);
            Require(await run.Client.MoveAsync(dx,0,run.Token).ConfigureAwait(false),"Đi tới mốc "+targetX);
            Publish(run);
        }
        Check(run,Math.Abs(run.Client.World.self.x-targetX)<=.75,"đã tới mốc "+targetX);
    }

    private async Task RunScenarioAsync(Run run)
    {
        var a=run.Client;
        Check(run,a.State==P1ConnectionState.Ready&&a.WorldV2!=null,"A connected using v2 world");
        using var bHttp=new HttpClientTransport(run.BaseUrl,new NetHttpClient{Timeout=TimeSpan.FromSeconds(8)});
        var b=new P1Client(bHttp,useWorldV2:true);
        Require(await b.ConnectAsync(run.Token).ConfigureAwait(false),"Kết nối phiên B");
        Require(await b.ReadQuestsAsync(run.Token).ConfigureAwait(false),"Nhiệm vụ phiên B");
        Require(await b.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Túi đồ phiên B");
        Check(run,b.SessionId!=a.SessionId&&b.World.self.characterId!=a.World.self.characterId,"different sessions and characters");
        var bCoins=Coins(b.Inventory);var bChests=Chests(b.Inventory);
        double bx=b.World.self.x,by=b.World.self.y;

        await WalkToAsync(run,42).ConfigureAwait(false);
        Require(await a.AcceptQuestAsync(Quest,"NPC_LYAN",run.Token).ConfigureAwait(false),"Nhận P00-01");
        Require(await a.ReadQuestsAsync(run.Token).ConfigureAwait(false),"Đọc nhiệm vụ đã nhận");
        Check(run,a.Quests.Any(q=>q.questId==Quest&&q.state=="ACTIVE"),"quest ACTIVE");
        run.Message="Đã nhận P00-01 từ Ly An.";Publish(run,"ACCEPT");

        foreach(var parcel in new[]{("ENT_MAN_BM_OBJ_BM_PACKAGE_01",36d),("ENT_MAN_BM_OBJ_BM_PACKAGE_02",44d),("ENT_MAN_BM_OBJ_BM_PACKAGE_03",52d)})
        {
            await WalkToAsync(run,parcel.Item2).ConfigureAwait(false);
            Require(await a.InteractAsync(parcel.Item1,run.Token).ConfigureAwait(false),"Nhặt kiện "+parcel.Item1);
            run.Message="Máy chủ xác nhận đã nhặt kiện hàng.";Publish(run,"INTERACT");
        }
        Require(await a.ReadQuestsAsync(run.Token).ConfigureAwait(false),"Đọc tiến độ kiện hàng");
        var quest=a.Quests.Single(q=>q.questId==Quest);
        Check(run,quest.objectiveCounters.TryGetValue("OBJ_P00_01_PACKAGES",out var collected)&&collected==3,"three parcels credited");
        await WalkToAsync(run,64).ConfigureAwait(false);
        Require(await a.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Túi đồ trước trả nhiệm vụ");
        long beforeCoins=Coins(a.Inventory);int beforeChests=Chests(a.Inventory);

        var lost=await a.TurnInQuestAsync(Quest,"NPC_TA_VAN_KHANH",run.Token).ConfigureAwait(false);
        Check(run,!lost.Success&&lost.Code=="mutation_outcome_unknown","lost committed response is uncertain");
        Check(run,a.HasPendingMutation&&a.State==P1ConnectionState.UncertainMutation,"pending key retained");
        Check(run,run.Drop!.Dropped&&run.Drop.Bodies.Count==1,"actual successful server reply dropped once");
        run.Message="Đã mất phản hồi trả nhiệm vụ; thử lại đúng khóa cũ.";Publish(run);
        await Task.Delay(150,run.Token).ConfigureAwait(false);
        Require(await a.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Kiểm kho sau phản hồi bị mất");
        Check(run,Coins(a.Inventory)==beforeCoins+20,"server already committed 20 coins");
        Check(run,Chests(a.Inventory)==beforeChests+1,"server already committed one chest");
        Require(await a.RetryPendingAsync(run.Token).ConfigureAwait(false),"Thử lại khóa trả nhiệm vụ");
        Check(run,!a.HasPendingMutation,"retry resolved pending mutation");
        Check(run,run.Drop.Bodies.Count==2&&run.Drop.Bodies[0]==run.Drop.Bodies[1],"retry body/request/key identical");
        Require(await a.ReadQuestsAsync(run.Token).ConfigureAwait(false),"Nhiệm vụ sau retry");
        Require(await a.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Túi đồ sau retry");
        Check(run,a.Quests.Any(q=>q.questId==Quest&&q.state=="COMPLETED"),"quest COMPLETED");
        Check(run,Coins(a.Inventory)==beforeCoins+20,"exactly-once coins after retry");
        Check(run,Chests(a.Inventory)==beforeChests+1,"exactly-once chest after retry");

        var repeat=await a.TurnInQuestAsync(Quest,"NPC_TA_VAN_KHANH",run.Token).ConfigureAwait(false);
        Check(run,!repeat.Success&&repeat.Code=="invalid_transition","fresh duplicate turn-in rejected");
        Require(await a.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Túi đồ sau trả lặp");
        Check(run,Coins(a.Inventory)==beforeCoins+20&&Chests(a.Inventory)==beforeChests+1,"no second reward");

        Require(await b.ReadWorldAsync(run.Token).ConfigureAwait(false),"Thế giới phiên B");
        Require(await b.ReadQuestsAsync(run.Token).ConfigureAwait(false),"Nhiệm vụ phiên B sau A");
        Require(await b.ReadInventoryAsync(run.Token).ConfigureAwait(false),"Túi đồ phiên B sau A");
        Check(run,Coins(b.Inventory)==bCoins&&Chests(b.Inventory)==bChests,"B inventory isolated");
        Check(run,!b.Quests.Any(q=>q.questId==Quest&&q.state=="COMPLETED"),"B quest not completed by A");
        Check(run,b.Quests.Where(q=>q.questId==Quest).All(q=>q.objectiveCounters.Values.All(v=>v==0)),"B counters unchanged");
        Check(run,b.World.self.x==bx&&b.World.self.y==by,"B position unchanged");

        await RefreshAsync(run,true).ConfigureAwait(false);
        run.Complete=true;
        run.Message="Hoàn tất P00-01: nhận nhiệm vụ, nhặt 3 kiện, trả thưởng đúng một lần.";
        Publish(run,passed:true);
    }

    public override void _ExitTree()
    {
        Volatile.Write(ref _exited,1);
        Interlocked.Increment(ref _epoch);
        lock(_inputLock)_movement=Vector2.Zero;
        Volatile.Read(ref _run)?.RequestStop();
        FrameReady=null;ScenarioPassed=null;ScenarioFailed=null;
    }
}
