using System.Collections.Concurrent;
using System.Diagnostics;
using Newtonsoft.Json.Linq;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.Core.Transport;
using NguMach.Client.P1;

class Program
{
    const string Sid="11111111111111111111111111111111";
    static string World(int hp)=>"{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1840,\"revision\":12,\"self\":{\"characterId\":\"CHR_TEST\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":"+hp+",\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";
    static P1HttpReply Reply(P1Request r,string result,int status=200)=>new(){StatusCode=status,CorrelationId=r.CorrelationId,Body="{\"schemaVersion\":1,\"requestId\":\""+r.CorrelationId+"\",\"sessionId\":\""+Sid+"\",\"result\":"+result+"}"};
    sealed class Transport : IP1Transport
    {
        public Func<P1Request,CancellationToken,Task<P1HttpReply>> Handler;
        public Task<P1HttpReply> SendAsync(P1Request r,CancellationToken ct)=>Handler(r,ct);
    }
    sealed class QueuedContext : SynchronizationContext
    {
        readonly ConcurrentQueue<(SendOrPostCallback,object)> q=new();
        public int Pending=>q.Count;
        public override void Post(SendOrPostCallback cb,object state)=>q.Enqueue((cb,state));
        public void Drain(){while(q.TryDequeue(out var item))item.Item1(item.Item2);}
    }
    sealed class QueuedDispatcher : IMainThreadDispatcher
    {
        readonly Queue<Action> q=new();
        public bool IsMainThread=>true;
        public Task InvokeAsync(Func<Task> action)=>action();
        public void Post(Action action)=>q.Enqueue(action);
        public void Drain(){while(q.TryDequeue(out var action))action();}
    }
    static async Task Main()
    {
        ThreadPool.GetMinThreads(out var workers,out var io);
        ThreadPool.SetMinThreads(Math.Max(workers,8),Math.Max(io,8));
        var gate=new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);
        var timed=new TimeoutTransport(new Transport{Handler=(r,ct)=>gate.Task},TimeSpan.FromMilliseconds(40));
        var sw=Stopwatch.StartNew();
        var timeout=await timed.SendAsync(new P1Request("GET","/x",null,"s","key"),CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(2));
        Console.WriteLine($"IGNORING_CT_TIMEOUT elapsedMs={sw.ElapsedMilliseconds} status={timeout.StatusCode} key={timeout.CorrelationId}");
        gate.SetResult(new P1HttpReply{StatusCode=200});
        UiDispose();
        await DeathAfterDispose();
        await QueuedEventAfterDispose();
        await AlphaActualSend();
        await AlphaWorldRead();
        DeathResponseAlreadyQueued(false);
        DeathResponseAlreadyQueued(true);
        await QueuedEventAfterFailedRelogin();
    }
    static void UiDispose()
    {
        var old=SynchronizationContext.Current;
        var context=new QueuedContext();SynchronizationContext.SetSynchronizationContext(context);
        try
        {
            var gate=new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t=new Transport{Handler=(r,ct)=>r.Path=="/p1/sessions"?Task.FromResult(Reply(r,World(0),201)):gate.Task};
            var s=new ClientSession(t);
            if(!s.ConnectAsync().GetAwaiter().GetResult().Success)throw new Exception("connect");
            var read=s.ReadCurrentEncounterAsync();
            var sw=Stopwatch.StartNew();s.Dispose();sw.Stop();
            var deadline=Stopwatch.StartNew();while(!read.IsCompleted&&deadline.ElapsedMilliseconds<1000){context.Drain();Thread.Sleep(1);}
            var result=read.GetAwaiter().GetResult();
            Console.WriteLine($"UI_DISPOSE elapsedMs={sw.ElapsedMilliseconds} readOutcome={result.Outcome}");
            gate.SetResult(new P1HttpReply{StatusCode=200});
        }
        finally{SynchronizationContext.SetSynchronizationContext(old);}
    }
    static async Task DeathAfterDispose()
    {
        var gate=new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
        CancellationToken received=default;int afterReads=0;
        var t=new Transport{Handler=async(r,ct)=>
        {
            if(r.Path=="/p1/sessions")return Reply(r,World(0),201);
            if(r.Path=="/p1/actor/death-return")
            {
                received=ct;await gate.Task;
                var fixture=JObject.Parse(File.ReadAllText("D:/Project/NGUMACHHUYENAN-handoff-opc-20261106/Shared/ClientCore.Tests/Fixtures/death_return_response_v1_reference_20261105.json"));
                return Reply(r,fixture["result"].ToString());
            }
            Interlocked.Increment(ref afterReads);return Reply(r,World(50));
        }};
        var s=new ClientSession(t);
        await s.ConnectAsync();
        var task=s.ReturnFromDeathAsync();
        s.Dispose();
        bool tokenCanceled=received.IsCancellationRequested;
        gate.SetResult(true);
        var result=await task.WaitAsync(TimeSpan.FromSeconds(2));
        Console.WriteLine($"DEATH_AFTER_DISPOSE innerTokenCanceled={tokenCanceled} success={result.Success} hp={s.Client.World.self.hp} receiptApplied={s.Client.LastDeathReturn?.applied} postDisposeWorldReads={afterReads}");
    }
    static async Task QueuedEventAfterDispose()
    {
        var fixture=File.ReadAllText("D:/Project/NGUMACHHUYENAN-handoff-opc-20261106/Shared/ClientCore.Tests/Fixtures/encounter_snapshot_v1_reference_20261104.json");
        var d=new QueuedDispatcher();
        var t=new Transport{Handler=(r,ct)=>Task.FromResult(Reply(r,r.Path=="/p1/sessions"?World(0):fixture,r.Path=="/p1/sessions"?201:200))};
        var s=new ClientSession(t,dispatcher:d);await s.ConnectAsync();
        int events=0;s.EncounterUpdated+=_=>events++;
        var result=await s.ReadCurrentEncounterAsync();
        s.Dispose();d.Drain();
        Console.WriteLine($"QUEUED_EVENT_AFTER_DISPOSE accepted={result.Success} deliveredAfterDispose={events}");
    }
    static async Task AlphaActualSend()
    {
        int sends=0;
        var t=new Transport{Handler=(r,ct)=>
        {
            if(r.Path=="/p1/sessions")return Task.FromResult(Reply(r,World(0),201));
            sends++;
            return Task.FromResult(new P1HttpReply{StatusCode=404,CorrelationId=r.CorrelationId,Body=""});
        }};
        var c=new P1Client(t);await c.ConnectAsync(CancellationToken.None);
        var result=await c.InteractAsync("ALPHA_OBJ_BM_RIPPLE_01",CancellationToken.None);
        Console.WriteLine($"ALPHA_CANONICAL actualHttpSends={sends} result={result.Code}");
        var c2=new P1Client(t);await c2.ConnectAsync(CancellationToken.None);
        int before=sends;var bad=await c2.InteractAsync("ALPHA_OBJ_BM_RIPPLE_99",CancellationToken.None);
        Console.WriteLine($"ALPHA_UNLISTED actualHttpSends={sends-before} result={bad.Code}");
    }
    static async Task AlphaWorldRead()
    {
        var ids=new[]{"ALPHA_OBJ_BM_FRAGMENT","ALPHA_OBJ_BM_RIPPLE_01","ALPHA_OBJ_BM_RIPPLE_02","ALPHA_OBJ_BM_RIPPLE_03","ALPHA_OBJ_BM_VILLAGER_01","ALPHA_OBJ_BM_VILLAGER_02"};
        var entities=new JArray(ids.Select(id=>new JObject{
            ["entityId"]=id,["kind"]="INTERACTABLE",["state"]="AVAILABLE",["mapInstanceId"]="MAP_BEN_MUA#1",
            ["floorId"]="OVERWORLD",["phase"]="PUBLIC",["healthState"]="INVULNERABLE",["targetable"]=false,
            ["x"]=18,["y"]=0,["hp"]=0,["maxHp"]=0,["revision"]=1,["lifeId"]=1,["availability"]="AVAILABLE"
        }));
        var world=new JObject{["schemaVersion"]=2,["mapId"]="MAP_BEN_MUA",["mapInstanceId"]="MAP_BEN_MUA#1",
            ["floorId"]="OVERWORLD",["phase"]="PUBLIC",["serverTimeUtc"]="2026-11-05T09:00:01Z",["serverTick"]=1840,["revision"]=12,
            ["audience"]=new JObject{["aoiEnterWu"]=64,["aoiLeaveWu"]=72},["self"]=JObject.Parse(World(0))["self"],["entities"]=entities};
        var t=new Transport{Handler=(r,ct)=>
        {
            if(r.Path=="/p1/sessions")return Task.FromResult(Reply(r,World(0),201));
            var reply=Reply(r,world.ToString());var env=JObject.Parse(reply.Body);env["schemaVersion"]=2;reply.Body=env.ToString();
            return Task.FromResult(reply);
        }};
        var client=new P1Client(t,useWorldV2:true);var result=await client.ConnectAsync(CancellationToken.None);
        Console.WriteLine($"ALPHA_WORLD_6 success={result.Success} code={result.Code} count={client.WorldV2?.entities.Length} idsPreserved={client.WorldV2?.entities.Select(e=>e.entityId).SequenceEqual(ids)}");
    }
    static void DeathResponseAlreadyQueued(bool relogin)
    {
        var previous=SynchronizationContext.Current;var ui=new QueuedContext();SynchronizationContext.SetSynchronizationContext(ui);
        try
        {
            ClientSession session=null;int deathCalls=0,afterStopWorldReads=0;bool stopped=false,transientReceipt=false;
            P1Request original=null;var replyGate=new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);
            var fixture=JObject.Parse(File.ReadAllText("D:/Project/NGUMACHHUYENAN-handoff-opc-20261106/Shared/ClientCore.Tests/Fixtures/death_return_response_v1_reference_20261105.json"));
            var t=new Transport{Handler=(r,ct)=>
            {
                if(r.Path=="/p1/sessions")return Task.FromResult(Reply(r,World(0),201));
                if(r.Path=="/p1/actor/death-return")
                {
                    if(++deathCalls==1){original=r;return replyGate.Task;}
                    var current=(JObject)fixture["result"].DeepClone();current["nextReturnAllowedAtTick"]=2900;
                    return Task.FromResult(Reply(r,current.ToString()));
                }
                if(stopped){afterStopWorldReads++;transientReceipt|=session.Client.LastDeathReturn!=null;}
                return Task.FromResult(Reply(r,World(50)));
            }};
            session=new ClientSession(t);session.ConnectAsync().GetAwaiter().GetResult();
            var oldClient=session.Client;
            var pending=session.ReturnFromDeathAsync();
            replyGate.SetResult(Reply(original,fixture["result"].ToString()));
            // Hold the UI event loop until the successful transport result is queued
            // for Core continuation. Cancellation after this point cannot remove it.
            var wait=Stopwatch.StartNew();while(ui.Pending==0&&wait.ElapsedMilliseconds<2000)Thread.Sleep(1);
            if(ui.Pending==0)throw new Exception("no queued Core continuation");
            long? beforeTick=null;
            if(relogin)
            {
                session.ReloginAsync().GetAwaiter().GetResult();
                var retry=session.Client.RetryPendingAsync(CancellationToken.None).GetAwaiter().GetResult();
                if(!retry.Success)throw new Exception("new epoch retry: "+retry.Code);
                beforeTick=session.Client.NextReturnAllowedAtTick;
            }
            else session.Dispose();
            stopped=true;
            wait.Restart();while(!pending.IsCompleted&&wait.ElapsedMilliseconds<2000){ui.Drain();Thread.Sleep(1);}
            var result=pending.GetAwaiter().GetResult();
            Console.WriteLine($"QUEUED_DEATH_{(relogin?"RELOGIN":"DISPOSE")} result={result.Code} oldHp={oldClient.World.self.hp} currentHp={session.Client.World.self.hp} pendingRetained={oldClient.HasPendingMutation} lateWorldReads={afterStopWorldReads} transientReceiptObserved={transientReceipt} newEpochTickBefore={beforeTick} currentTickAfter={session.Client.NextReturnAllowedAtTick}");
            session.Dispose();
        }
        finally{SynchronizationContext.SetSynchronizationContext(previous);}
    }
    static async Task QueuedEventAfterFailedRelogin()
    {
        var fixture=File.ReadAllText("D:/Project/NGUMACHHUYENAN-handoff-opc-20261106/Shared/ClientCore.Tests/Fixtures/encounter_snapshot_v1_reference_20261104.json");
        bool failLogin=false;var d=new QueuedDispatcher();
        var t=new Transport{Handler=(r,ct)=>Task.FromResult(r.Path=="/p1/sessions"?
            failLogin?new P1HttpReply{StatusCode=500,CorrelationId=r.CorrelationId,Body=""}:Reply(r,World(0),201):Reply(r,fixture))};
        var s=new ClientSession(t,dispatcher:d);await s.ConnectAsync();
        int events=0;s.EncounterUpdated+=_=>events++;
        await s.ReadCurrentEncounterAsync();
        var oldGeneration=s.SessionGeneration;failLogin=true;var login=await s.ReloginAsync();
        d.Drain();
        Console.WriteLine($"QUEUED_EVENT_FAILED_RELOGIN loginSuccess={login.Success} oldGeneration={oldGeneration} currentGeneration={s.SessionGeneration} activeSession={s.Client.SessionId??"NONE"} deliveredAfterEpochEnded={events}");
        s.Dispose();
    }
}
