using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Dispatch;
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
            public readonly List<P1Request> Requests = new List<P1Request>();
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                lock (Requests) Requests.Add(request);
                return Handler(request, ct);
            }
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
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
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
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
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
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
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

        // ── Work30: public-API repro fixes ──────────────────────────────────

        [Fact]
        public async Task ReturnFromDeath_DisposeDuringRequest_DoesNotMutateState()
        {
            // Transport returns a death-return receipt only after the release gate,
            // simulating a non-cancelling transport whose reply arrives late.
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/actor/death-return")
                    {
                        started.TrySetResult(true);
                        return DelayBeyondCancellation(release.Task, () => new P1HttpReply
                        {
                            StatusCode = 200,
                            CorrelationId = r.CorrelationId,
                            Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                                   "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                                   "\"applied\":true,\"replayed\":false,\"mapId\":\"MAP_BEN_MUA\"," +
                                   "\"xWu\":18.0,\"yWu\":0.0,\"hp\":50,\"maxHp\":100," +
                                   "\"mp\":50,\"maxMp\":50,\"serverTick\":1840,\"revision\":12," +
                                   "\"cleared\":{\"inflightCasts\":1,\"reservedCounters\":0," +
                                   "\"guardWindowClosed\":false,\"movementWindowReset\":true}," +
                                   "\"penalties\":{\"xp\":0,\"currency\":0,\"durability\":0}," +
                                   "\"nextReturnAllowedAtTick\":1900}}"
                        });
                    }
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                Assert.Null(s.Client.LastDeathReturn);

                var death = s.ReturnFromDeathAsync(CancellationToken.None);
                await started.Task.WaitAsync(TimeSpan.FromSeconds(5));

                // Dispose while the death-return request is in flight.
                s.Dispose();
                release.TrySetResult(true);

                var result = await death.WaitAsync(TimeSpan.FromSeconds(5));
                // Late reply is rejected as stale: no receipt/HP/world-read mutation.
                Assert.False(result.Success, "stale death-return must not succeed");
                Assert.Null(s.Client.LastDeathReturn);
                Assert.Null(s.Client.NextReturnAllowedAtTick);
            }
        }

        [Fact]
        public async Task DispatcherCallback_AfterDispose_DoesNotCallOldConsumer()
        {
            var encounterJson = FindFixture();
            var firstRead = false;
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/encounters/current")
                    {
                        if (!firstRead)
                        {
                            firstRead = true;
                            return Task.FromResult(EncounterReply(r, encounterJson));
                        }
                        return DelayBeyondCancellation(release.Task, () => EncounterReply(r, encounterJson));
                    }
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            var s = new ClientSession(t);
            int events = 0;
            Action<EncounterUpdate> handler = _ => Interlocked.Increment(ref events);
            s.EncounterUpdated += handler;
            Assert.True((await s.ConnectAsync()).Success);
            Assert.True((await s.ReadCurrentEncounterAsync()).Success);
            events = 0; // do not count the first read's callback

            // Queue another read so its callback is pending, then dispose.
            var read = s.ReadCurrentEncounterAsync();
            await Task.Delay(50); // let the delayed handler enter WaitAsync
            s.Dispose();
            release.TrySetResult(true);

            var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
            // The callback queued before Dispose must not invoke the old consumer.
            Assert.Equal(0, Volatile.Read(ref events));
        }

        [Fact]
        public async Task Relogin_QueuedDispatcherCallback_DoesNotCallOldConsumer()
        {
            var encounterJson = FindFixture();
            var sessionIndex = 0;
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r,
                            Interlocked.Increment(ref sessionIndex) == 1 ? SessionOne : SessionTwo));
                    if (r.Path == "/p1/encounters/current")
                    {
                        started.TrySetResult(true);
                        return DelayBeyondCancellation(release.Task, () => EncounterReply(r, encounterJson));
                    }
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            var s = new ClientSession(t);
            int events = 0;
            Action<EncounterUpdate> handler = _ => Interlocked.Increment(ref events);
            s.EncounterUpdated += handler;
            Assert.True((await s.ConnectAsync()).Success);

            // Queue a read on session 1, then relogin (bumps epoch) before the reply.
            var read = s.ReadCurrentEncounterAsync();
            await started.Task.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.True((await s.ReloginAsync()).Success);
            release.TrySetResult(true);

            var result = await read.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.Equal(EncounterReadOutcome.Stale, result.Outcome);
            // The callback queued before relogin must not invoke the old consumer
            // under the old epoch.
            Assert.Equal(0, Volatile.Read(ref events));
        }

        // ── Work30 round2: deterministic queued-ordering tests ────────────────

        private sealed class SingleThreadSyncContext : SynchronizationContext
        {
            private readonly Queue<Tuple<SendOrPostCallback, object>> _queue =
                new Queue<Tuple<SendOrPostCallback, object>>();
            public override void Post(SendOrPostCallback d, object state)
                => _queue.Enqueue(Tuple.Create(d, state));
            public override void Send(SendOrPostCallback d, object state) => d(state);
            public int QueuedCount => _queue.Count;
            public bool RunOne()
            {
                if (_queue.TryDequeue(out var item)) { item.Item1(item.Item2); return true; }
                return false;
            }
            public void RunAll()
            {
                while (RunOne()) { }
            }
        }

        // Queued dispatcher: Post() enqueues instead of running inline, so tests
        // can deterministically drain callbacks before/after Dispose/relogin.
        private sealed class QueuedDispatcher : IMainThreadDispatcher
        {
            public bool IsMainThread => true;
            private readonly Queue<Action> _queue = new Queue<Action>();
            public void Post(Action action) => _queue.Enqueue(action ?? throw new ArgumentNullException(nameof(action)));
            public Task InvokeAsync(Func<Task> action)
            {
                _queue.Enqueue(async () => { if (action != null) await action(); });
                return Task.CompletedTask;
            }
            public int QueuedCount => _queue.Count;
            public void RunAll()
            {
                while (_queue.TryDequeue(out var action)) action();
            }
        }

        [Fact]
        public async Task ReturnFromDeath_QueuedSuccessBeforeDispose_DoesNotMutateState()
        {
            // HTTP reply is successfully received (transport completes) but the
            // continuation after the await is queued on a single-threaded UI
            // context. Dispose runs before the queued continuation drains, so
            // ct.ThrowIfCancellationRequested() inside Core must throw and the
            // pending mutation must be preserved.
            var replyTcs = new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                        return Task.FromResult(SessionReply(r, SessionOne));
                    if (r.Path == "/p1/actor/death-return")
                        return replyTcs.Task;
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                Assert.Null(s.Client.LastDeathReturn);

                var death = s.ReturnFromDeathAsync(CancellationToken.None);
                Assert.False(death.IsCompleted); // reply has not arrived yet

                // Dispose runs before the reply is delivered.
                s.Dispose();

                // Reply arrives after dispose: transport completes, then
                // ct.ThrowIfCancellationRequested() inside Core must throw.
                replyTcs.SetResult(new P1HttpReply
                {
                    StatusCode = 200,
                    CorrelationId = Guid.NewGuid().ToString("N"),
                    Body = "{\"schemaVersion\":1,\"requestId\":\"" + Guid.NewGuid().ToString("N") +
                           "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                           "\"applied\":true,\"replayed\":false,\"mapId\":\"MAP_BEN_MUA\"," +
                           "\"xWu\":18.0,\"yWu\":0.0,\"hp\":50,\"maxHp\":100," +
                           "\"mp\":50,\"maxMp\":50,\"serverTick\":1840,\"revision\":12," +
                           "\"cleared\":{\"inflightCasts\":1,\"reservedCounters\":0," +
                           "\"guardWindowClosed\":false,\"movementWindowReset\":true}," +
                           "\"penalties\":{\"xp\":0,\"currency\":0,\"durability\":0}," +
                           "\"nextReturnAllowedAtTick\":1900}}"
                });

                var result = await death.WaitAsync(TimeSpan.FromSeconds(5));
                Assert.False(result.Success, "stale death-return must not succeed");
                Assert.Null(s.Client.LastDeathReturn);
                Assert.Null(s.Client.NextReturnAllowedAtTick);
                // Pending mutation preserved for same-key retry.
                Assert.NotNull(s.Client.CapturePendingMutation());
            }
        }

        [Fact]
        public async Task ReturnFromDeath_OldReplyAcrossRelogin_PreservesPending()
        {
            // Session 1 sends death-return; reply is delayed. Relogin to session 2.
            // Session 2 retries with the same key. The old reply from session 1
            // arrives after relogin and must not mutate session 2.
            int sessionCounter = 0;
            var release1 = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var started1 = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                    {
                        var id = Interlocked.Increment(ref sessionCounter);
                        return Task.FromResult(SessionReply(r, id == 1 ? SessionOne : SessionTwo));
                    }
                    if (r.Path == "/p1/actor/death-return")
                    {
                        if (!started1.Task.IsCompleted)
                        {
                            // First death-return (session 1): delay its reply.
                            started1.TrySetResult(true);
                            return DelayBeyondCancellation(release1.Task, () => new P1HttpReply
                            {
                                StatusCode = 200,
                                CorrelationId = r.CorrelationId,
                                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                                       "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                                       "\"applied\":true,\"replayed\":false,\"mapId\":\"MAP_BEN_MUA\"," +
                                       "\"xWu\":18.0,\"yWu\":0.0,\"hp\":50,\"maxHp\":100," +
                                       "\"mp\":50,\"maxMp\":50,\"serverTick\":1840,\"revision\":12," +
                                       "\"cleared\":{\"inflightCasts\":1,\"reservedCounters\":0," +
                                       "\"guardWindowClosed\":false,\"movementWindowReset\":true}," +
                                       "\"penalties\":{\"xp\":0,\"currency\":0,\"durability\":0}," +
                                       "\"nextReturnAllowedAtTick\":1900}}"
                            });
                        }
                        // Second death-return (session 2 retry): immediate reply.
                        return Task.FromResult(new P1HttpReply
                        {
                            StatusCode = 200,
                            CorrelationId = r.CorrelationId,
                            Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                                   "\",\"sessionId\":\"" + SessionTwo + "\",\"result\":{" +
                                   "\"applied\":true,\"replayed\":false,\"mapId\":\"MAP_BEN_MUA\"," +
                                   "\"xWu\":18.0,\"yWu\":0.0,\"hp\":50,\"maxHp\":100," +
                                   "\"mp\":50,\"maxMp\":50,\"serverTick\":1841,\"revision\":13," +
                                   "\"cleared\":{\"inflightCasts\":0,\"reservedCounters\":0," +
                                   "\"guardWindowClosed\":true,\"movementWindowReset\":true}," +
                                   "\"penalties\":{\"xp\":0,\"currency\":0,\"durability\":0}," +
                                   "\"nextReturnAllowedAtTick\":1901}}"
                        });
                    }
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            using (var s = new ClientSession(t))
            {
                Assert.True((await s.ConnectAsync()).Success);
                Assert.Equal(SessionOne, s.Client.SessionId);

                // Session 1: death-return sent, reply delayed.
                var death1 = s.ReturnFromDeathAsync(CancellationToken.None);
                await started1.Task.WaitAsync(TimeSpan.FromSeconds(5));

                // Relogin to session 2 (replaces Client, bumps generation).
                Assert.True((await s.ReloginAsync()).Success);
                Assert.Equal(SessionTwo, s.Client.SessionId);

                // Session 2: same-key retry. The pending mutation from session 1 is
                // carried over; RetryPending resubmits with the same body/key.
                var retry = await s.Adapter.RetryPendingAsync(CancellationToken.None);
                Assert.True(retry.Success, retry.Code);

                // Release the old session-1 reply. It must not mutate session 2.
                release1.TrySetResult(true);
                var result = await death1.WaitAsync(TimeSpan.FromSeconds(5));
                // Old reply rejected: stale epoch, not applied.
                Assert.False(result.Success);
                // Session 2's own retry succeeded and set LastDeathReturn.
                Assert.NotNull(s.Client.LastDeathReturn);
                Assert.Equal(13, s.Client.LastDeathReturn.revision);
                // Pending cleared after successful retry.
                Assert.Null(s.Client.CapturePendingMutation());
            }
        }

        [Fact]
        public async Task DispatcherCallback_AfterFailedRelogin_DoesNotCallOldConsumer()
        {
            // Callback queued on the dispatcher before a FAILED relogin must not
            // invoke the old consumer: Client reference changes even though
            // SessionGeneration does not (ConnectAsync failed).
            var encounterJson = FindFixture();
            int sessionIndex = 0;
            var release = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var started = new TaskCompletionSource<bool>(TaskCreationOptions.RunContinuationsAsynchronously);
            var dispatcher = new QueuedDispatcher();
            var t = new DelegateTransport
            {
                Handler = (r, ct) =>
                {
                    if (r.Path == "/p1/sessions")
                    {
                        // First call: success (session 1). Second call (relogin): failure.
                        if (Interlocked.Increment(ref sessionIndex) == 1)
                            return Task.FromResult(SessionReply(r, SessionOne));
                        return Task.FromResult(new P1HttpReply
                        {
                            StatusCode = 500,
                            CorrelationId = r.CorrelationId,
                            Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                                   "\",\"error\":{\"code\":\"internal_error\",\"retryable\":false}}"
                        });
                    }
                    if (r.Path == "/p1/encounters/current")
                    {
                        started.TrySetResult(true);
                        return Task.FromResult(EncounterReply(r, encounterJson));
                    }
                    if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                        return Task.FromResult(SessionReply(r, r.SessionId ?? SessionTwo));
                    return Task.FromResult(NetworkFailure(r));
                }
            };
            var s = new ClientSession(t, dispatcher: dispatcher);
            int events = 0;
            Action<EncounterUpdate> handler = _ => Interlocked.Increment(ref events);
            s.EncounterUpdated += handler;
            Assert.True((await s.ConnectAsync()).Success);

            // Queue an encounter read on session 1; reply comes back immediately
            // and its callback is enqueued on the dispatcher (not yet drained).
            var read = s.ReadCurrentEncounterAsync();
            await started.Task.WaitAsync(TimeSpan.FromSeconds(5));
            Assert.True(read.IsCompleted);
            Assert.Equal(1, dispatcher.QueuedCount);

            // Relogin FAILS: session endpoint returns 500 on the second call.
            // ReloginAsync replaces Client before ConnectAsync, so Client reference
            // changes but SessionGeneration does not.
            var relogin = await s.ReloginAsync(CancellationToken.None);
            Assert.False(relogin.Success);

            // Drain the dispatcher: the queued callback must not invoke the old
            // consumer because Client != capturedClient.
            dispatcher.RunAll();
            Assert.Equal(0, Volatile.Read(ref events));
            Assert.True((await read).Success);
        }

        // ── Gói 31: TALK / portal / MAP-VIEWED transport tests ──────────────

        [Fact]
        public async Task TalkAsync_SendsEmptyIntentAndAppliesResult()
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
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"applied\":true,\"appliedFlags\":[\"FLAG_TALK_01\"]," +
                               "\"questId\":\"P00-01\",\"stepId\":\"STEP_P00_01_TALK\",\"revision\":2}" +
                               "}"
                    });
                return Task.FromResult(NetworkFailure(r));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);

            Assert.True(result.Success, result.Code);
            var sent = transport.Requests[transport.Requests.Count - 1];
            var body = P1Wire.Decode<P1Envelope<P1QuestTalkIntent>>(sent.Body);
            Assert.Equal("NPC_LYAN", body.payload.npcId);
            Assert.Equal("NODE_GREETING_01", body.payload.nodeId);
            Assert.True(P1Wire.Hex32(body.requestId));
            Assert.True(P1Wire.Hex32(body.idempotencyKey));
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task TalkAsync_FeatureUnavailableWhenRouteMissing()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("feature_unavailable", result.Code);
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task TalkAsync_PendingPreservedForRetry()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/quests/talk")
                    return Task.FromResult(new P1HttpReply { StatusCode = 0, CorrelationId = r.CorrelationId });
                return Task.FromResult(NetworkFailure(r));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var first = await client.TalkAsync("NPC_LYAN", "NODE_GREETING_01", CancellationToken.None);
            Assert.False(first.Success);
            Assert.Equal("mutation_outcome_unknown", first.Code);
            Assert.True(client.HasPendingMutation);

            var sent = transport.Requests[transport.Requests.Count - 1];
            var firstBody = P1Wire.Decode<P1Envelope<P1QuestTalkIntent>>(sent.Body);

            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/quests/talk")
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"applied\":true,\"appliedFlags\":[],\"questId\":\"P00-01\"," +
                               "\"stepId\":\"STEP_P00_01_TALK\",\"revision\":2}}"
                    });
                return Task.FromResult(NetworkFailure(r));
            };

            var retry = await client.RetryPendingAsync(CancellationToken.None);
            Assert.True(retry.Success, retry.Code);
            var retrySent = transport.Requests[transport.Requests.Count - 1];
            var retryBody = P1Wire.Decode<P1Envelope<P1QuestTalkIntent>>(retrySent.Body);
            Assert.Equal(firstBody.requestId, retryBody.requestId);
            Assert.Equal(firstBody.idempotencyKey, retryBody.idempotencyKey);
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task PortalAsync_SendsPortalIdAndAppliesResult()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/world/portal")
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"portalId\":\"TP_BM_THANH_LAC\",\"destinationMapId\":\"MAP_THANH_LAC\"," +
                               "\"destinationXWu\":8.0,\"destinationYWu\":0.0,\"serverTick\":100,\"revision\":1}" +
                               "}"
                    });
                return Task.FromResult(NetworkFailure(r));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.PortalAsync("TP_BM_THANH_LAC", CancellationToken.None);

            Assert.True(result.Success, result.Code);
            var sent = transport.Requests[transport.Requests.Count - 1];
            var body = P1Wire.Decode<P1Envelope<P1WorldPortalIntent>>(sent.Body);
            Assert.Equal("TP_BM_THANH_LAC", body.payload.portalId);
            Assert.True(P1Wire.Hex32(body.requestId));
            Assert.True(P1Wire.Hex32(body.idempotencyKey));
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task PortalAsync_FeatureUnavailableWhenRouteMissing()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.PortalAsync("TP_BM_THANH_LAC", CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("feature_unavailable", result.Code);
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task MapViewedAsync_SendsQuestIdAndAppliesResult()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                if (r.Path == "/p1/quests/map-viewed")
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + SessionOne + "\",\"result\":{" +
                               "\"questId\":\"P00-01\",\"acknowledged\":true,\"serverTick\":101,\"revision\":1}" +
                               "}"
                    });
                return Task.FromResult(NetworkFailure(r));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.MapViewedAsync("P00-01", CancellationToken.None);

            Assert.True(result.Success, result.Code);
            var sent = transport.Requests[transport.Requests.Count - 1];
            var body = P1Wire.Decode<P1Envelope<P1QuestMapViewedIntent>>(sent.Body);
            Assert.Equal("P00-01", body.payload.questId);
            Assert.True(P1Wire.Hex32(body.requestId));
            Assert.True(P1Wire.Hex32(body.idempotencyKey));
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task MapViewedAsync_FeatureUnavailableWhenRouteMissing()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r, SessionOne));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.MapViewedAsync("P00-01", CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("feature_unavailable", result.Code);
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task TalkPortalMapViewed_InvalidInputRejected()
        {
            var transport = new DelegateTransport();
            transport.Handler = (r, ct) => Task.FromResult(SessionReply(r, SessionOne));
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            Assert.Equal("invalid_input", (await client.TalkAsync(null, "NODE", CancellationToken.None)).Code);
            Assert.Equal("invalid_input", (await client.TalkAsync("NPC", null, CancellationToken.None)).Code);
            Assert.Equal("invalid_input", (await client.PortalAsync(null, CancellationToken.None)).Code);
            Assert.Equal("invalid_input", (await client.MapViewedAsync(null, CancellationToken.None)).Code);
            Assert.Equal("invalid_input", (await client.MapViewedAsync("", CancellationToken.None)).Code);
            Assert.False(client.HasPendingMutation);
        }
    }
}
