// OPC-17 O-B — session lifecycle tests driven by controllable seams
// (injected dispatcher, injected transport, injected dispose bound). No test
// here asserts on elapsed time or relies on a guessed sleep.
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.P1;
using NguMach.Client.Presentation;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class SessionLifecycleTests
    {
        private const string SessionOne = "11111111111111111111111111111111";
        private const string SessionTwo = "22222222222222222222222222222222";

        private static string WorldJson =>
            "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"char_test\"," +
            "\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50," +
            "\"swordIntent\":0},\"entities\":[]}";

        private sealed class DelegateTransport : IP1Transport
        {
            public Func<P1Request, CancellationToken, Task<P1HttpReply>> Handler;
            public readonly List<P1Request> Requests = new List<P1Request>();
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                lock (Requests) Requests.Add(request);
                return Handler(request, ct);
            }
            public int CountPath(string path)
            {
                lock (Requests)
                {
                    int n = 0;
                    foreach (var r in Requests) if (r.Path == path) n++;
                    return n;
                }
            }
        }

        // Post() enqueues instead of running inline so a test can change the
        // subscription set between "queued" and "run".
        private sealed class QueuedDispatcher : IMainThreadDispatcher
        {
            private readonly Queue<Action> _queue = new Queue<Action>();
            public bool IsMainThread => true;
            public void Post(Action action) => _queue.Enqueue(action ?? throw new ArgumentNullException(nameof(action)));
            public Task InvokeAsync(Func<Task> action)
            {
                _queue.Enqueue(async () => { if (action != null) await action(); });
                return Task.CompletedTask;
            }
            public int QueuedCount { get { lock (_queue) return _queue.Count; } }
            public void RunAll()
            {
                while (true)
                {
                    Action action;
                    lock (_queue)
                    {
                        if (_queue.Count == 0) return;
                        action = _queue.Dequeue();
                    }
                    action();
                }
            }
        }

        // Single-threaded "UI" context: continuations are queued and only run
        // when the owner pumps them, exactly like a game loop.
        private sealed class SingleThreadSyncContext : SynchronizationContext
        {
            private readonly Queue<Tuple<SendOrPostCallback, object>> _queue =
                new Queue<Tuple<SendOrPostCallback, object>>();
            public override void Post(SendOrPostCallback d, object state)
            {
                lock (_queue) _queue.Enqueue(Tuple.Create(d, state));
            }
            public override void Send(SendOrPostCallback d, object state) => d(state);
            public int QueuedCount { get { lock (_queue) return _queue.Count; } }
            public void RunAll()
            {
                while (true)
                {
                    Tuple<SendOrPostCallback, object> item;
                    lock (_queue)
                    {
                        if (_queue.Count == 0) return;
                        item = _queue.Dequeue();
                    }
                    item.Item1(item.Item2);
                }
            }
            // Waits for a *state* (something queued), never for a duration.
            public bool WaitForQueued()
            {
                var deadline = DateTime.UtcNow + TimeSpan.FromSeconds(10);
                while (QueuedCount == 0)
                {
                    if (DateTime.UtcNow > deadline) return false;
                    Thread.Yield();
                }
                return true;
            }
        }

        private static string FindFixture()
        {
            var relative = System.IO.Path.Combine("Shared", "ClientCore.Tests", "Fixtures",
                "encounter_snapshot_v1_reference_20261104.json");
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            for (int depth = 0; dir != null && depth < 12; depth++, dir = dir.Parent)
            {
                var candidate = System.IO.Path.Combine(dir.FullName, relative);
                if (System.IO.File.Exists(candidate)) return System.IO.File.ReadAllText(candidate);
            }
            throw new System.IO.FileNotFoundException("encounter reference fixture not found");
        }

        private static P1HttpReply SessionReply(P1Request r, string sessionId)
        {
            return new P1HttpReply
            {
                StatusCode = 201,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + sessionId + "\",\"result\":" + WorldJson + "}"
            };
        }

        private static P1HttpReply EncounterReply(P1Request r, string encounterJson)
        {
            return new P1HttpReply
            {
                StatusCode = 200,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + r.SessionId + "\",\"result\":" + encounterJson + "}"
            };
        }

        // ── queued success + single-thread context ───────────────────────────

        [Fact]
        public async Task SingleThreadContext_ReplyQueuedThenDispose_NeverApplies()
        {
            var encounterJson = FindFixture();
            var replyGate = new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current") return replyGate.Task;
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionOne));
                    return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
                }
            };

            var ctx = new SingleThreadSyncContext();
            var original = SynchronizationContext.Current;
            var s = new ClientSession(t, dispatcher: new QueuedDispatcher());
            int events = 0;
            s.EncounterUpdated += _ => Interlocked.Increment(ref events);
            try
            {
                Assert.True((await s.ConnectAsync()).Success);

                // Start the read while the single-thread context is current, so
                // its post-transport continuation is queued instead of running.
                SynchronizationContext.SetSynchronizationContext(ctx);
                var read = s.ReadCurrentEncounterAsync();
                SynchronizationContext.SetSynchronizationContext(original);

                Assert.False(read.IsCompleted, "reply has not been delivered yet");

                // The transport answers successfully; the continuation is now
                // sitting on the UI queue and nothing has been applied yet.
                replyGate.SetResult(EncounterReply(
                    new P1Request("GET", "/p1/encounters/current", null, SessionOne, Guid.NewGuid().ToString("N")),
                    encounterJson));
                Assert.True(ctx.WaitForQueued(), "read continuation must be queued on the UI context");
                Assert.False(read.IsCompleted);

                // Dispose wins the race for the queued success.
                s.Dispose();
                ctx.RunAll();

                var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
                Assert.False(s.Encounter.HasSnapshot);
                Assert.Equal(0, Volatile.Read(ref events));
            }
            finally
            {
                SynchronizationContext.SetSynchronizationContext(original);
                s.Dispose();
            }
        }

        // ── subscription changed between queue and run ───────────────────────

        [Fact]
        public async Task SubscriptionRemovedBetweenQueueAndRun_DoesNotInvoke()
        {
            var encounterJson = FindFixture();
            var dispatcher = new QueuedDispatcher();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current") return Task.FromResult(EncounterReply(r, encounterJson));
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionOne));
                    return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
                }
            };
            var s = new ClientSession(t, dispatcher: dispatcher);
            int first = 0, second = 0;
            Action<EncounterUpdate> a = _ => Interlocked.Increment(ref first);
            Action<EncounterUpdate> b = _ => Interlocked.Increment(ref second);
            try
            {
                s.EncounterUpdated += a;
                s.EncounterUpdated += b;
                Assert.True((await s.ConnectAsync()).Success);

                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(result.Success, result.ErrorCode);
                Assert.Equal(1, dispatcher.QueuedCount);

                // Both were subscribed when the update was queued; one leaves
                // before the queue is drained.
                s.EncounterUpdated -= b;
                dispatcher.RunAll();

                Assert.Equal(1, Volatile.Read(ref first));
                Assert.Equal(0, Volatile.Read(ref second));
            }
            finally { s.Dispose(); }
        }

        [Fact]
        public async Task SubscriptionReplacedBetweenQueueAndRun_InvokesOnlyLiveHandlers()
        {
            var encounterJson = FindFixture();
            var dispatcher = new QueuedDispatcher();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current") return Task.FromResult(EncounterReply(r, encounterJson));
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionOne));
                    return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
                }
            };
            var s = new ClientSession(t, dispatcher: dispatcher);
            int oldCount = 0, newCount = 0;
            Action<EncounterUpdate> oldHandler = _ => Interlocked.Increment(ref oldCount);
            Action<EncounterUpdate> newHandler = _ => Interlocked.Increment(ref newCount);
            try
            {
                s.EncounterUpdated += oldHandler;
                Assert.True((await s.ConnectAsync()).Success);

                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(result.Success, result.ErrorCode);
                Assert.Equal(1, dispatcher.QueuedCount);

                // Swap the subscriber while the update waits on the queue: the
                // handler that was live at Post() time must not run, and the one
                // that arrived afterwards must not receive a stale event either.
                s.EncounterUpdated -= oldHandler;
                s.EncounterUpdated += newHandler;
                dispatcher.RunAll();

                Assert.Equal(0, Volatile.Read(ref oldCount));
                Assert.Equal(0, Volatile.Read(ref newCount));
            }
            finally { s.Dispose(); }
        }

        // ── cancel after commit ──────────────────────────────────────────────

        [Fact]
        public async Task CancelAfterCommit_KeepsReceiptAndNeverResends()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/quests/talk")
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + Guid.NewGuid().ToString("N") +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"questId\":\"P00-01\",\"objectiveId\":null," +
                               "\"npcId\":\"NPC_LYAN\",\"nodeId\":\"NODE_GREETING_01\"," +
                               "\"credited\":true,\"replayed\":false,\"appliedFlag\":null," +
                               "\"eventId\":\"PQTALK_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\"," +
                               "\"revision\":2}}"
                    });
                return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var caller = new CancellationTokenSource();
            var committed = await client.TalkAsync("NPC_LYAN", "NODE_GREETING_01", caller.Token);
            Assert.True(committed.Success, committed.Code);
            Assert.NotNull(client.LastTalk);
            Assert.False(client.HasPendingMutation);
            Assert.Equal(1, transport.CountPath("/p1/quests/talk"));

            // The caller cancels only after the receipt landed. A committed
            // receipt is never revoked and no follow-up send may happen.
            caller.Cancel();

            Assert.NotNull(client.LastTalk);
            Assert.Equal("P00-01", client.LastTalk.questId);
            Assert.False(client.HasPendingMutation);
            // A confirmed receipt needs a fresh read; it never leaves the client
            // in an unknown-outcome state just because the caller cancelled.
            Assert.Equal(P1ConnectionState.NeedsResync, client.State);

            var retry = await client.RetryPendingAsync(CancellationToken.None);
            Assert.Equal("no_pending_mutation", retry.Code);
            Assert.Equal(1, transport.CountPath("/p1/quests/talk"));
            Assert.NotNull(client.LastTalk);
        }

        // ── duplicate concurrent calls ───────────────────────────────────────

        [Fact]
        public async Task DuplicateConcurrentRetry_SendsExactlyOneRequest()
        {
            bool failFirst = true;
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/quests/accept")
                {
                    if (failFirst)
                    {
                        failFirst = false;
                        return Task.FromResult(new P1HttpReply { StatusCode = 0, CorrelationId = r.CorrelationId });
                    }
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"questId\":\"P00-01\",\"state\":\"ACTIVE\",\"stepId\":\"STEP_01\"," +
                               "\"objectiveCounters\":{},\"revision\":1}}"
                    });
                }
                return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var first = await client.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None);
            Assert.Equal("mutation_outcome_unknown", first.Code);
            Assert.True(client.HasPendingMutation);
            Assert.Equal(1, transport.CountPath("/p1/quests/accept"));

            // Two callers hit retry at the same time: the lane must let exactly
            // one of them resubmit, the other reports that there is nothing left.
            var a = client.RetryPendingAsync(CancellationToken.None);
            var b = client.RetryPendingAsync(CancellationToken.None);
            var results = await Task.WhenAll(a, b).WaitAsync(TimeSpan.FromSeconds(5));

            int ok = 0, none = 0;
            foreach (var r in results)
            {
                if (r.Success) ok++;
                else if (r.Code == "no_pending_mutation") none++;
            }
            Assert.Equal(1, ok);
            Assert.Equal(1, none);
            Assert.Equal(2, transport.CountPath("/p1/quests/accept"));
            Assert.False(client.HasPendingMutation);
        }

        // ── dispose: idempotent and bounded ──────────────────────────────────

        [Fact]
        public async Task ConcurrentDisposeAndDisposeAsync_NeverThrowsAndIsIdempotent()
        {
            var t = new DelegateTransport
            {
                Handler = (r, ct) => Task.FromResult(r.Path == "/p1/sessions"
                    ? SessionReply(r, SessionOne)
                    : new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId })
            };
            var s = new ClientSession(t);
            Assert.True((await s.ConnectAsync()).Success);

            var callers = new List<Task>();
            for (int i = 0; i < 8; i++)
            {
                int index = i;
                callers.Add(Task.Run(() =>
                {
                    if (index % 2 == 0) s.Dispose();
                    else s.DisposeAsync().AsTask().GetAwaiter().GetResult();
                }));
            }
            await Task.WhenAll(callers).WaitAsync(TimeSpan.FromSeconds(10));

            Assert.True(s.Token == CancellationToken.None, "token source must be released exactly once");
            await Assert.ThrowsAsync<ObjectDisposedException>(() => s.ReadCurrentEncounterAsync());
            // Cleanup ran once: a later dispose is a no-op, not a second teardown.
            s.Dispose();
            await s.DisposeAsync();
        }

        [Fact]
        public async Task DisposeAsync_BoundsCleanupWhenTransportIgnoresCancellation()
        {
            var encounterJson = FindFixture();
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current")
                    {
                        started.TrySetResult(true);
                        // Deliberately ignores cancellation, like a stuck socket.
                        return release.Task.ContinueWith(
                            _ => EncounterReply(r, encounterJson),
                            CancellationToken.None, TaskContinuationOptions.ExecuteSynchronously,
                            TaskScheduler.Default);
                    }
                    return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
                }
            };
            // Seam: the bound is injected, not guessed by the test.
            var s = new ClientSession(t, disposeTimeout: TimeSpan.FromMilliseconds(20));
            try
            {
                Assert.True((await s.ConnectAsync()).Success);
                var read = s.ReadCurrentEncounterAsync();
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));

                // The read still holds the lane and the transport never answers:
                // cleanup must still return instead of hanging the caller.
                await s.DisposeAsync().AsTask().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(s.Token == CancellationToken.None);

                release.TrySetResult(true);
                var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
                Assert.False(s.Encounter.HasSnapshot);
            }
            finally
            {
                release.TrySetResult(true);
                s.Dispose();
            }
        }

        // ── adapter lifetime guard ───────────────────────────────────────────

        [Fact]
        public async Task Adapter_IsStableAndFollowsCurrentEpochAcrossRelogin()
        {
            int sessions = 0;
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions")
                {
                    int index = Interlocked.Increment(ref sessions);
                    return Task.FromResult(SessionReply(r, index == 1 ? SessionOne : SessionTwo));
                }
                if (r.Path == "/p1/quests/talk")
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + Guid.NewGuid().ToString("N") +
                               "\",\"sessionId\":\"" + r.SessionId + "\",\"result\":{" +
                               "\"questId\":\"P00-01\",\"objectiveId\":null," +
                               "\"npcId\":\"NPC_LYAN\",\"nodeId\":\"NODE_GREETING_01\"," +
                               "\"credited\":true,\"replayed\":false,\"appliedFlag\":null," +
                               "\"eventId\":\"PQTALK_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef\"," +
                               "\"revision\":2}}"
                    });
                return Task.FromResult(new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
            };
            var s = new ClientSession(transport);
            try
            {
                Assert.True((await s.ConnectAsync()).Success);
                var held = s.Adapter;
                Assert.Same(held, s.Adapter);
                Assert.Equal(UIConnectionState.Ready, held.ConnectionState);

                var first = await held.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);
                Assert.True(first.Success, first.Code);
                Assert.Equal(SessionOne, transport.Requests[transport.Requests.Count - 1].SessionId);
                Assert.NotNull(held.LastTalk);

                // A relogin swaps Client but not Adapter: the presenter-held
                // reference now reaches the new epoch instead of the dead one.
                Assert.True((await s.ReloginAsync()).Success);
                Assert.Same(held, s.Adapter);
                Assert.Null(s.Client.LastTalk);
                Assert.Null(held.LastTalk); // the previous epoch's receipt is gone

                var second = await held.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);
                Assert.True(second.Success, second.Code);
                Assert.Equal(SessionTwo, transport.Requests[transport.Requests.Count - 1].SessionId);
            }
            finally { s.Dispose(); }
        }

        [Fact]
        public async Task Adapter_AfterDispose_FailsTypedAndTouchesNoTransport()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) => Task.FromResult(r.Path == "/p1/sessions"
                ? SessionReply(r, SessionOne)
                : new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId });
            var s = new ClientSession(transport);
            Assert.True((await s.ConnectAsync()).Success);
            var adapter = s.Adapter;
            int before = transport.CountPath("/p1/quests/talk");

            s.Dispose();

            // A presenter that outlives the session degrades to a typed failure
            // and an empty projection: no throw, no transport call, no state
            // read from the disposed epoch.
            Assert.Equal(UIConnectionState.Disconnected, adapter.ConnectionState);
            Assert.False(adapter.HasPendingMutation);
            Assert.Null(adapter.Self);
            Assert.Null(adapter.World);
            Assert.Null(adapter.WorldV2);
            Assert.Null(adapter.Inventory);
            Assert.Null(adapter.LastTalk);
            Assert.Null(adapter.LastPortal);
            Assert.Null(adapter.LastMapViewed);
            Assert.Null(adapter.LastDeathReturn);
            Assert.Empty(adapter.Quests);
            Assert.Empty(adapter.CooldownEndsAtUtc);

            var talk = await adapter.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);
            Assert.False(talk.Success);
            Assert.Equal("disposed", talk.Code);
            var retry = await adapter.RetryPendingAsync(CancellationToken.None);
            Assert.Equal("disposed", retry.Code);
            var world = await adapter.ReadWorldAsync(CancellationToken.None);
            Assert.Equal("disposed", world.Code);
            Assert.Equal(before, transport.CountPath("/p1/quests/talk"));
        }
    }
}
