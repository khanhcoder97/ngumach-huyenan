using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class CompositionTests
    {
        private const string SessionOne = "11111111111111111111111111111111";
        private const string SessionTwo = "22222222222222222222222222222222";
        private const string EncounterId = "ENC-0123456789ABCDEF01234567";

        private static string WorldJson => "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"char_test\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";

        private sealed class DelegateTransport : IP1Transport
        {
            public Func<P1Request, CancellationToken, Task<P1HttpReply>> Handler;
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
                => Handler(request, ct);
        }

        private static string FindFixture()
        {
            var relative = Path.Combine("Shared", "ClientCore.Tests", "Fixtures",
                "encounter_snapshot_v1_reference_20261104.json");
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            for (int depth = 0; dir != null && depth < 12; depth++, dir = dir.Parent)
            {
                var candidate = Path.Combine(dir.FullName, relative);
                if (File.Exists(candidate)) return File.ReadAllText(candidate);
            }
            throw new FileNotFoundException("encounter reference fixture not found");
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

        private static P1HttpReply ErrorReply(P1Request r, int status, string code)
        {
            return new P1HttpReply
            {
                StatusCode = status,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"error\":{\"code\":\"" + code + "\",\"retryable\":false}}"
            };
        }

        private static P1HttpReply QuestReply(P1Request r, string questId)
        {
            return new P1HttpReply
            {
                StatusCode = 200,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + r.SessionId + "\",\"result\":{\"questId\":\"" + questId +
                       "\",\"state\":\"ACTIVE\",\"stepId\":\"STEP_01\",\"objectiveCounters\":{},\"revision\":1}}"
            };
        }

        private static P1HttpReply NetworkFailure(P1Request r)
        {
            return new P1HttpReply { StatusCode = 500, CorrelationId = r.CorrelationId, Body = "" };
        }

        private static async Task<P1HttpReply> DelayBeyondCancellation(
            Task gate, Func<P1HttpReply> makeReply)
        {
            await gate.ConfigureAwait(false);
            return makeReply();
        }

        [Fact]
        public async Task Epoch_MonotonicAcrossRelogin()
        {
            var sessionIndex = 0;
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r, Interlocked.Increment(ref sessionIndex) == 1 ? SessionOne : SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var g1 = s.SessionGeneration;
                Assert.Equal(SessionOne, s.Client.SessionId);
                Assert.True((await s.ReloginAsync()).Success);
                Assert.True(s.SessionGeneration > g1, "epoch must increase on relogin");
                Assert.Equal(SessionTwo, s.Client.SessionId);
                Assert.Equal(s.SessionGeneration, s.Guard.Active.Generation);
            }
        }

        [Fact]
        public async Task TryApply_RejectsOldSessionAndRequest()
        {
            var t = new DelegateTransport
            {
                Handler = (r, ct) => Task.FromResult(
                    r.Path == "/p1/sessions" ? SessionReply(r, SessionOne) : NetworkFailure(r))
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var oldSession = s.Client.SessionId;
                var oldGen = s.SessionGeneration;
                Assert.True((await s.ReloginAsync()).Success);
                bool applied = false;
                Assert.False(s.TryApply(oldSession, null, oldGen, () => applied = true));
                Assert.False(applied);

                Assert.True(s.TryApply(s.Client.SessionId, null, s.SessionGeneration, () => applied = true));
                Assert.True(applied);

                s.Guard.BeginRequest("right");
                applied = false;
                Assert.False(s.TryApply(s.Client.SessionId, "wrong", s.SessionGeneration, () => applied = true));
                Assert.False(applied);
            }
        }

        [Fact]
        public void Factory_CreatesHttpSessionAndRejectsMissingUrl()
        {
            Assert.Throws<ArgumentNullException>(() => ClientSessionFactory.CreateHttp(" "));
            using (var s = ClientSessionFactory.CreateHttp("http://127.0.0.1:1", characterId: "CHR_TEST"))
            {
                Assert.NotNull(s.Client);
                Assert.NotNull(s.Adapter);
                Assert.NotNull(s.Guard);
                Assert.False(s.HasPendingMutation);
            }
        }

        [Fact]
        public void Cancel_DisposesCts()
        {
            var t = new DelegateTransport { Handler = (r, ct) => Task.FromResult(NetworkFailure(r)) };
            var s = new ClientSession(t);
            s.Cancel();
            Assert.True(s.Token.IsCancellationRequested);
            s.Dispose();
        }

        [Fact]
        public async Task EncounterRead_SuccessDispatchesImmutableState()
        {
            var encounterJson = FindFixture();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current") return Task.FromResult(EncounterReply(r, encounterJson));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                EncounterUpdate seen = null;
                int events = 0;
                s.EncounterUpdated += u => { events++; seen = u; };
                Assert.True((await s.ConnectAsync()).Success);

                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(result.Success, result.ErrorCode);
                Assert.Equal(EncounterReadOutcome.Success, result.Outcome);
                Assert.NotNull(result.State);
                Assert.Equal(EncounterId, result.State.EncounterId);
                Assert.Equal("P00-05", result.State.QuestId);
                Assert.Equal(2, result.State.SafePads.Count);
                Assert.True(result.State.MoveCooldownRemainingTicks.ContainsKey("A"));
                Assert.True(result.Update.IsNewCast);
                Assert.Equal(1, events);
                Assert.NotNull(seen);
                Assert.True(seen.IsNewCast);
                Assert.True(s.Encounter.HasSnapshot);
                Assert.Equal(MoveState.Telegraph, s.Encounter.State.ActiveMove.State);

                // Immutable projection: the list/dictionary exposed to Godot is not the DTO.
                var pads = result.State.SafePads as IList<EncounterSafePadState>;
                if (pads != null)
                    Assert.Throws<NotSupportedException>(() => pads.Add(pads[0]));
                var cooldowns = result.State.MoveCooldownRemainingTicks as IDictionary<string, long>;
                if (cooldowns != null)
                    Assert.Throws<NotSupportedException>(() => cooldowns["X"] = 1);

                s.Encounter.CommitCast();
                Assert.Equal("CAST-ALPHA-00000001", s.Encounter.LastCastId);

                var detail = await s.ReadEncounterAsync(EncounterId).WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Error, detail.Outcome); // stub has no detail route
            }
        }

        [Fact]
        public async Task EncounterRead_NotFoundIsTypedAndDoesNotFabricateState()
        {
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    return Task.FromResult(ErrorReply(r, 404, "encounter_not_found"));
                }
            };
            using (var s = new ClientSession(t))
            {
                int events = 0;
                s.EncounterUpdated += _ => events++;
                Assert.True((await s.ConnectAsync()).Success);
                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.NotFound, result.Outcome);
                Assert.Null(result.State);
                Assert.False(s.Encounter.HasSnapshot);
                Assert.Equal(0, events);
                Assert.Equal(404, result.StatusCode);
            }
        }

        [Fact]
        public async Task EncounterRead_SessionNotFoundExpiresClientAndReloginRecovers()
        {
            var encounterJson = FindFixture();
            bool expired = false;
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (!expired)
                    {
                        expired = true;
                        return Task.FromResult(ErrorReply(r, 404, "session_not_found"));
                    }
                    return Task.FromResult(EncounterReply(r, encounterJson));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.SessionExpired, result.Outcome);
                Assert.Equal(P1ConnectionState.Expired, s.Client.State);
                Assert.Null(s.Client.SessionId);

                var relogin = await s.ReloginAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(relogin.Success, relogin.Code);
                Assert.Equal(P1ConnectionState.Ready, s.Client.State);
                var recovered = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(recovered.Success, recovered.ErrorCode);
                Assert.Equal(EncounterId, recovered.State.EncounterId);
            }
        }

        [Fact]
        public async Task EncounterRead_InvalidEnvelopeOrSnapshotIsRejected()
        {
            var encounterJson = FindFixture();
            var mode = "bad-envelope";
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (mode == "bad-envelope")
                        return Task.FromResult(new P1HttpReply
                        {
                            StatusCode = 200,
                            CorrelationId = r.CorrelationId,
                            Body = "{\"schemaVersion\":1,\"requestId\":\"not-hex\",\"sessionId\":\"" + r.SessionId + "\",\"result\":{}}"
                        });
                    var broken = encounterJson.Replace("\"bossHp\": 1200,", "");
                    return Task.FromResult(EncounterReply(r, broken));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var badEnvelope = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Error, badEnvelope.Outcome);
                Assert.Equal("invalid_envelope", badEnvelope.ErrorCode);

                mode = "bad-snapshot";
                var badSnapshot = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Error, badSnapshot.Outcome);
                Assert.Contains("invalid_snapshot", badSnapshot.ErrorCode);
                Assert.False(s.Encounter.HasSnapshot);
            }
        }

        [Fact]
        public async Task EncounterRead_EmptyIdIsRejectedWithoutTransportCall()
        {
            var t = new DelegateTransport
            {
                Handler = (r, ct) => Task.FromResult(SessionReply(r, SessionOne))
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var result = await s.ReadEncounterAsync(" ");
                Assert.Equal(EncounterReadOutcome.Error, result.Outcome);
                Assert.Equal("invalid_input", result.ErrorCode);
            }
        }

        [Fact]
        public async Task DelayedEncounterRead_AfterReloginIsStaleAndNotDispatched()
        {
            var encounterJson = FindFixture();
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            int sessions = 0;
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r, Interlocked.Increment(ref sessions) == 1 ? SessionOne : SessionTwo));
                    if (r.Path == "/p1/encounters/current")
                    {
                        var request = r;
                        started.TrySetResult(true);
                        // Deliberately ignores cancellation: a real transport may complete late.
                        return DelayBeyondCancellation(release.Task, () => EncounterReply(request, encounterJson));
                    }
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                int events = 0;
                s.EncounterUpdated += _ => events++;
                Assert.True((await s.ConnectAsync()).Success);
                var oldGeneration = s.SessionGeneration;

                var oldRead = s.ReadCurrentEncounterAsync();
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));

                var relogin = await s.ReloginAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(relogin.Success, relogin.Code);
                Assert.True(s.SessionGeneration > oldGeneration);

                release.TrySetResult(true);
                var result = await oldRead.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
                Assert.False(s.Encounter.HasSnapshot);
                Assert.Equal(0, events);
            }
        }

        [Fact]
        public async Task DelayedMutation_AfterReloginKeepsSameRequestAndKey()
        {
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            int sessions = 0;
            bool acceptSucceeds = false;
            var mutationIds = new List<string>();
            var mutationBodies = new List<string>();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r, Interlocked.Increment(ref sessions) == 1 ? SessionOne : SessionTwo));
                    if (r.Path == "/p1/quests/accept")
                    {
                        lock (mutationIds)
                        {
                            mutationIds.Add(r.CorrelationId);
                            mutationBodies.Add(r.Body);
                        }
                        if (acceptSucceeds) return Task.FromResult(QuestReply(r, "P00-01"));
                        var request = r;
                        started.TrySetResult(true);
                        return DelayBeyondCancellation(release.Task, () => NetworkFailure(request));
                    }
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);

                var oldMutation = s.Client.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None);
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));

                var before = s.Client.CapturePendingMutation();
                Assert.NotNull(before);
                var key = before.Request.CorrelationId;
                var body = before.Request.Body;

                var relogin = await s.ReloginAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(relogin.Success, relogin.Code);
                Assert.True(s.HasPendingMutation);
                var carried = s.Client.CapturePendingMutation();
                Assert.NotNull(carried);
                Assert.Equal(key, carried.Request.CorrelationId);
                Assert.Equal(body, carried.Request.Body);
                Assert.NotEqual(SessionOne, s.Client.SessionId);

                release.TrySetResult(true);
                var oldResult = await oldMutation.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.False(oldResult.Success);
                Assert.Equal("mutation_outcome_unknown", oldResult.Code);

                // The late completion of the old client must not clear the new client's carry.
                var stillCarried = s.Client.CapturePendingMutation();
                Assert.NotNull(stillCarried);
                Assert.Equal(key, stillCarried.Request.CorrelationId);

                acceptSucceeds = true;
                var retry = await s.Adapter.RetryPendingAsync(CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(retry.Success, retry.Code);
                Assert.False(s.HasPendingMutation);
                Assert.Equal(2, mutationIds.Count);
                Assert.Equal(key, mutationIds[0]);
                Assert.Equal(key, mutationIds[1]);
                Assert.Equal(mutationBodies[0], mutationBodies[1]);
            }
        }

        [Fact]
        public async Task PendingCarry_SurvivesFailedReloginAndRestoresAfterward()
        {
            bool sessionFails = false;
            bool acceptSucceeds = false;
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(sessionFails ? NetworkFailure(r) : SessionReply(r, SessionOne));
                    if (r.Path == "/p1/quests/accept")
                        return Task.FromResult(acceptSucceeds ? QuestReply(r, "P00-01") : NetworkFailure(r));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var first = await s.Client.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None);
                Assert.Equal("mutation_outcome_unknown", first.Code);
                var key = s.Client.CapturePendingMutation().Request.CorrelationId;
                var body = s.Client.CapturePendingMutation().Request.Body;
                var generation = s.SessionGeneration;

                sessionFails = true;
                var failed = await s.ReloginAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.False(failed.Success);
                Assert.Equal(generation, s.SessionGeneration);
                Assert.True(s.HasPendingMutation);
                Assert.False(s.Client.HasPendingMutation);

                sessionFails = false;
                var recovered = await s.ReloginAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(recovered.Success, recovered.Code);
                Assert.True(s.SessionGeneration > generation);
                Assert.True(s.Client.HasPendingMutation);
                var carried = s.Client.CapturePendingMutation();
                Assert.Equal(key, carried.Request.CorrelationId);
                Assert.Equal(body, carried.Request.Body);

                acceptSucceeds = true;
                var retry = await s.Adapter.RetryPendingAsync(CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(retry.Success, retry.Code);
                Assert.False(s.HasPendingMutation);
            }
        }

        [Fact]
        public async Task CallerCancellation_KeepsPendingMutationAndSameKey()
        {
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            bool acceptSucceeds = false;
            var ids = new List<string>();
            var t = new DelegateTransport
            {
                Handler = async (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return SessionReply(r, SessionOne);
                    if (r.Path == "/p1/quests/accept")
                    {
                        lock (ids) ids.Add(r.CorrelationId);
                        if (acceptSucceeds) return QuestReply(r, "P00-01");
                        started.TrySetResult(true);
                        await Task.Delay(Timeout.Infinite, ct);
                    }
                    return NetworkFailure(r);
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var cts = new CancellationTokenSource();
                var task = s.Client.AcceptQuestAsync("P00-01", "NPC_LYAN", cts.Token);
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));
                var key = s.Client.CapturePendingMutation().Request.CorrelationId;
                cts.Cancel();
                await Assert.ThrowsAnyAsync<OperationCanceledException>(() => task.WaitAsync(TimeSpan.FromSeconds(5)));
                Assert.True(s.Client.HasPendingMutation);
                Assert.Equal(key, s.Client.CapturePendingMutation().Request.CorrelationId);

                acceptSucceeds = true;
                var retry = await s.Adapter.RetryPendingAsync(CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(retry.Success, retry.Code);
                Assert.Equal(2, ids.Count);
                Assert.All(ids, id => Assert.Equal(key, id));
            }
        }

        [Fact]
        public async Task LifecycleCancellation_ReadReturnsCanceledAndNeverApplies()
        {
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = async (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return SessionReply(r, SessionOne);
                    if (r.Path == "/p1/encounters/current")
                    {
                        started.TrySetResult(true);
                        await Task.Delay(Timeout.Infinite, ct);
                    }
                    return NetworkFailure(r);
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var read = s.ReadCurrentEncounterAsync();
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));
                s.Cancel();
                var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Error, result.Outcome);
                Assert.Equal("canceled", result.ErrorCode);
                Assert.False(s.Encounter.HasSnapshot);
            }
        }

        [Fact]
        public async Task RequestTimeout_MutationKeepsPendingAndRetriesSameKey()
        {
            bool acceptSucceeds = false;
            var ids = new List<string>();
            var t = new DelegateTransport
            {
                Handler = async (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return SessionReply(r, SessionOne);
                    if (r.Path == "/p1/quests/accept")
                    {
                        lock (ids) ids.Add(r.CorrelationId);
                        if (acceptSucceeds) return QuestReply(r, "P00-01");
                        await Task.Delay(Timeout.Infinite, ct);
                    }
                    return NetworkFailure(r);
                }
            };
            using (var s = new ClientSession(t, requestTimeout: TimeSpan.FromMilliseconds(100)))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var timedOut = await s.Client.AcceptQuestAsync("P00-01", "NPC_LYAN", CancellationToken.None)
                    .WaitAsync(TimeSpan.FromSeconds(5));
                Assert.False(timedOut.Success);
                Assert.Equal("mutation_outcome_unknown", timedOut.Code);
                Assert.True(s.Client.HasPendingMutation);
                var key = s.Client.CapturePendingMutation().Request.CorrelationId;

                acceptSucceeds = true;
                var retry = await s.Adapter.RetryPendingAsync(CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(5));
                Assert.True(retry.Success, retry.Code);
                Assert.Equal(2, ids.Count);
                Assert.All(ids, id => Assert.Equal(key, id));
            }
        }

        [Fact]
        public async Task RequestTimeout_ReadReturnsNetworkErrorAndNeverApplies()
        {
            var t = new DelegateTransport
            {
                Handler = async (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return SessionReply(r, SessionOne);
                    if (r.Path == "/p1/encounters/current")
                        await Task.Delay(Timeout.Infinite, ct);
                    return NetworkFailure(r);
                }
            };
            using (var s = new ClientSession(t, requestTimeout: TimeSpan.FromMilliseconds(100)))
            {
                Assert.True((await s.ConnectAsync()).Success);
                var result = await s.ReadCurrentEncounterAsync().WaitAsync(TimeSpan.FromSeconds(5));
                Assert.Equal(EncounterReadOutcome.Error, result.Outcome);
                Assert.Equal("network_unavailable", result.ErrorCode);
                Assert.False(s.Encounter.HasSnapshot);
            }
        }

        [Fact]
        public async Task Dispose_UnsubscribesAndRejectsFurtherReads()
        {
            var encounterJson = FindFixture();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current") return Task.FromResult(EncounterReply(r, encounterJson));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            var s = new ClientSession(t);
            var token = s.Token;
            try
            {
                int events = 0;
                Action<EncounterUpdate> handler = _ => events++;
                s.EncounterUpdated += handler;
                s.EncounterUpdated -= handler;
                Assert.True((await s.ConnectAsync()).Success);
                Assert.True((await s.ReadCurrentEncounterAsync()).Success);
                Assert.Equal(0, events);
            }
            finally
            {
                s.Dispose();
            }
            Assert.True(token.IsCancellationRequested);
            await Assert.ThrowsAsync<ObjectDisposedException>(() => s.ReadCurrentEncounterAsync());
        }

        [Fact]
        public async Task DisposeDuringRead_NoThrowNoEventNoState()
        {
            // Codex harness at 685b888: Dispose during encounter read threw
            // ObjectDisposedException at SemaphoreSlim.Release.
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
                        var request = r;
                        started.TrySetResult(true);
                        return DelayBeyondCancellation(release.Task, () => EncounterReply(request, encounterJson));
                    }
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            var s = new ClientSession(t);
            int events = 0;
            s.EncounterUpdated += _ => Interlocked.Increment(ref events);
            Assert.True((await s.ConnectAsync()).Success);

            var read = s.ReadCurrentEncounterAsync();
            await started.Task.WaitAsync(TimeSpan.FromSeconds(5));

            // Dispose while read is in flight — must never throw, even when the
            // late reply arrives and the read's finally runs.
            s.Dispose();
            release.TrySetResult(true);

            var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.Equal(0, Volatile.Read(ref events));
            Assert.False(s.Encounter.HasSnapshot);
            Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
        }

        private static bool IsAlphaId(string target)
        {
            var method = typeof(P1Client).GetMethod("IsValidInteractTarget",
                System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);
            if (method == null) throw new InvalidOperationException("IsValidInteractTarget missing");
            return (bool)method.Invoke(null, new object[] { target });
        }

        [Theory]
        [InlineData("ALPHA_OBJ_BM_FRAGMENT")]
        [InlineData("ALPHA_OBJ_BM_RIPPLE_01")]
        [InlineData("ALPHA_OBJ_BM_RIPPLE_02")]
        [InlineData("ALPHA_OBJ_BM_RIPPLE_03")]
        [InlineData("ALPHA_OBJ_BM_VILLAGER_01")]
        [InlineData("ALPHA_OBJ_BM_VILLAGER_02")]
        [InlineData("ENT_MAN_BM_OBJ_BM_PACKAGE_01")]
        public void AlphaInteractIds_Accepted(string target)
        {
            Assert.True(IsAlphaId(target));
        }

        [Theory]
        [InlineData("ALPHA_NPC_RESCUE_01")]
        [InlineData("ALPHA_NPC_RESCUE")]
        [InlineData("ALPHA_OBJ_BM_RIPPLE_04")]
        [InlineData("ALPHA_IDENTITY_HACK")]
        [InlineData("ENT_")]
        [InlineData("")]
        [InlineData("   ")]
        [InlineData("npc_lyan")]
        public void AlphaInteractIds_Rejected(string target)
        {
            Assert.False(IsAlphaId(target));
        }
    }
}
