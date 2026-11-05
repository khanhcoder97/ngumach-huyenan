// OPC-15 O2/O5 (WO26) — Portable composition/facade owning session epoch, transport,
// adapter, typed encounter reads, subscriptions and cancellation lifecycle.
// Epoch is monotonic across relogin. Every response is checked against the captured
// session+generation before it can touch current state. Ambiguous mutations keep their
// request id/idempotency key across relogin. Pure C#. Owner: OpenCode.

using System;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.Core.Handshake;
using NguMach.Client.Core.Transport;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace NguMach.Client.Core.Composition
{
    public enum EncounterReadOutcome
    {
        Success,
        NotFound,
        SessionExpired,
        Stale,
        Error,
        NotConnected
    }

    public sealed class EncounterReadResult
    {
        public EncounterReadOutcome Outcome { get; internal set; }
        public bool Success => Outcome == EncounterReadOutcome.Success;
        public EncounterState State { get; internal set; }
        public EncounterUpdate Update { get; internal set; }
        public string ErrorCode { get; internal set; }
        public int StatusCode { get; internal set; }

        internal static EncounterReadResult Fail(EncounterReadOutcome outcome, string code, int status = 0)
        {
            return new EncounterReadResult { Outcome = outcome, ErrorCode = code, StatusCode = status };
        }
    }

    public sealed class ClientSession : IDisposable
    {
        private readonly IP1Transport _rawTransport;
        private readonly IP1Transport _transport;
        private readonly bool _ownsTransport;
        private readonly string _characterId;
        private readonly IMainThreadDispatcher _dispatcher;
        private readonly SemaphoreSlim _encounterLane = new SemaphoreSlim(1, 1);
        private readonly object _disposeGate = new object();
        private CancellationTokenSource _cts;
        private PendingMutationSnapshot _pendingCarry;
        private bool _disposed;
        private bool _encounterLaneDisposed;

        public P1Client Client { get; private set; }
        public P1ClientAdapter Adapter { get; private set; }
        public StaleResponseGuard Guard { get; private set; }
        public EncounterView Encounter { get; }
        // Host-supplied deployment facts. Production-off is the default; no route is
        // ever advertised just because the client knows how to call it.
        public ClientCapability Capability { get; }
        public ServiceAvailability Availability { get; }
        public long SessionGeneration { get; private set; }
        public IMainThreadDispatcher Dispatcher => _dispatcher;
        public CancellationToken Token { get { return _cts != null ? _cts.Token : CancellationToken.None; } }
        public bool HasPendingMutation => Client.HasPendingMutation || _pendingCarry != null;

        // Raised on the injected main-thread dispatcher after a typed encounter read
        // was accepted by the view. Unsubscribe (or dispose the session) to release it.
        public event Action<EncounterUpdate> EncounterUpdated;

        public ClientSession(
            IP1Transport transport,
            bool ownsTransport = false,
            bool useWorldV2 = false,
            TimeSpan? requestTimeout = null,
            IMainThreadDispatcher dispatcher = null,
            string characterId = null,
            DeploymentProfile profile = null)
        {
            _rawTransport = transport ?? throw new ArgumentNullException(nameof(transport));
            _ownsTransport = ownsTransport;
            _characterId = string.IsNullOrWhiteSpace(characterId) ? null : characterId;
            _dispatcher = dispatcher ?? new SynchronousDispatcher();
            _transport = new TimeoutTransport(_rawTransport, requestTimeout ?? TimeSpan.FromSeconds(30));
            Client = new P1Client(_transport, useWorldV2: useWorldV2, characterId: _characterId);
            Adapter = new P1ClientAdapter(Client);
            Guard = new StaleResponseGuard();
            Encounter = new EncounterView();
            Capability = ClientCapability.FromProfile(profile ?? DeploymentProfile.ProductionOff());
            Availability = ServiceAvailabilityPolicy.Evaluate(Capability);
            _cts = new CancellationTokenSource();
        }

        public async Task<P1Result> ConnectAsync(CancellationToken ct = default)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            using (var linked = CreateLinkedToken(ct))
            {
                Guard.EndSession();
                var result = await Client.ConnectAsync(linked.Token);
                if (result.Success)
                {
                    SessionGeneration++;
                    Guard.BeginSession(Client.SessionId, SessionGeneration);
                    Encounter.Reset();
                    RestorePendingCarry();
                }
                return result;
            }
        }

        // Re-login: new client/epoch; old in-flight responses can never touch it.
        // An ambiguous mutation is carried across with the same request/key.
        public async Task<P1Result> ReloginAsync(CancellationToken ct = default)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            var captured = Client.CapturePendingMutation();
            if (captured != null) _pendingCarry = captured;

            try { _cts.Cancel(); } catch (Exception) { }
            _cts.Dispose();
            _cts = new CancellationTokenSource();
            Guard.EndSession();
            Encounter.Reset();

            var previous = Client;
            Client = new P1Client(_transport, useWorldV2: previous.UseWorldV2, characterId: _characterId);
            Adapter = new P1ClientAdapter(Client);
            return await ConnectAsync(ct);
        }

        // Applies state only if the response still belongs to the active session/epoch.
        public bool TryApply(string responseSessionId, string responseRequestId, long responseGeneration, Action apply)
        {
            if (apply == null) return false;
            if (!Guard.IsApplicable(responseSessionId, responseRequestId, responseGeneration)) return false;
            apply();
            return true;
        }

        public Task<EncounterReadResult> ReadCurrentEncounterAsync(CancellationToken ct = default)
        {
            return ReadEncounterCoreAsync("/p1/encounters/current", true, ct);
        }

        // Death-return intent goes through the same P1Client lane so the
        // idempotency key survives relogin/replay and no second grant can occur.
        // The response is gated by the captured session+epoch: a dispose or
        // relogin between send and receive makes the late reply stale, so it
        // never mutates receipt/HP or starts a fresh world read. The unresolved
        // operation keeps its request id/idempotency key for a same-key retry.
        public Task<P1Result> ReturnFromDeathAsync(CancellationToken ct = default)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            return ReturnFromDeathCoreAsync(ct);
        }

        private async Task<P1Result> ReturnFromDeathCoreAsync(CancellationToken ct)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            if (Client.SessionId == null)
                return P1Result.Fail("not_connected");

            string sessionId = Client.SessionId;
            long generation = SessionGeneration;

            // Capture death-return state before the request so a stale late reply
            // (non-cancelling transport) cannot leave mutated receipt/HP behind.
            var beforeLastDeathReturn = Client.LastDeathReturn;
            var beforeNextReturnAllowedAtTick = Client.NextReturnAllowedAtTick;

            using (var linked = CreateLinkedToken(ct))
            {
                P1Result result;
                try
                {
                    result = await Client.ReturnFromDeathAsync(linked.Token);
                }
                catch (OperationCanceledException)
                {
                    // Dispose cancelled the token mid-request. Surface as stale,
                    // not a throw; pending key is preserved inside P1Client.
                    return P1Result.Fail("stale_session");
                }

                // A dispose/relogin between send and receive makes this response
                // stale: never apply a late receipt, HP, or world read. Restore
                // death-return state to its pre-request values.
                if (!IsCurrentEpoch(sessionId, generation))
                {
                    Client.LastDeathReturn = beforeLastDeathReturn;
                    Client.NextReturnAllowedAtTick = beforeNextReturnAllowedAtTick;
                    return P1Result.Fail("stale_session");
                }

                return result;
            }
        }

        public Task<EncounterReadResult> ReadEncounterAsync(string encounterId, CancellationToken ct = default)
        {
            if (string.IsNullOrWhiteSpace(encounterId))
                return Task.FromResult(EncounterReadResult.Fail(EncounterReadOutcome.Error, "invalid_input"));
            return ReadEncounterCoreAsync("/p1/encounters/" + Uri.EscapeDataString(encounterId), false, ct);
        }

        private async Task<EncounterReadResult> ReadEncounterCoreAsync(string path, bool isCurrent, CancellationToken ct)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            if (Client.SessionId == null)
                return EncounterReadResult.Fail(EncounterReadOutcome.NotConnected, "not_connected");

            string sessionId = Client.SessionId;
            long generation = SessionGeneration;
            string requestId = Guid.NewGuid().ToString("N");
            var request = new P1Request("GET", path, null, sessionId, requestId);

            using (var linked = CreateLinkedToken(ct))
            {
                try
                {
                    await _encounterLane.WaitAsync(linked.Token);
                }
                catch (OperationCanceledException)
                {
                    return CanceledOrStale(sessionId, generation, "canceled_wait");
                }
                catch (ObjectDisposedException)
                {
                    // Dispose won the race for the lane after the entry check.
                    return EncounterReadResult.Fail(EncounterReadOutcome.Stale, "stale_session");
                }

                try
                {
                    P1HttpReply reply;
                    try
                    {
                        reply = await _transport.SendAsync(request, linked.Token);
                    }
                    catch (OperationCanceledException)
                    {
                        return CanceledOrStale(sessionId, generation, "canceled");
                    }
                    catch (Exception e)
                    {
                        return EncounterReadResult.Fail(EncounterReadOutcome.Error, "network_unavailable: " + e.Message);
                    }

                    // A relogin/expiry between send and receive makes this response stale.
                    if (!IsCurrentEpoch(sessionId, generation))
                        return EncounterReadResult.Fail(EncounterReadOutcome.Stale, "stale_session");

                    return ApplyEncounterReply(reply, sessionId, generation, isCurrent);
                }
                finally
                {
                    // Dispose() waits for this release before disposing the lane;
                    // the gate guarantees Release() can never race Dispose().
                    lock (_disposeGate)
                    {
                        if (!_encounterLaneDisposed)
                        {
                            try { _encounterLane.Release(); }
                            catch (ObjectDisposedException) { }
                            catch (SemaphoreFullException) { }
                        }
                    }
                }
            }
        }

        private EncounterReadResult ApplyEncounterReply(P1HttpReply reply, string sessionId, long generation, bool isCurrent)
        {
            string errorCode = null;
            JObject root = null;
            if (!string.IsNullOrWhiteSpace(reply.Body) && reply.Body.Length <= 1024 * 1024)
            {
                try { root = JObject.Parse(reply.Body); }
                catch (JsonException) { root = null; }
            }
            if (root != null)
            {
                var error = root["error"] as JObject;
                if (error != null) errorCode = ReadString(error, "code");
            }

            if (reply.StatusCode == 404)
            {
                if (!IsCurrentEpoch(sessionId, generation))
                    return EncounterReadResult.Fail(EncounterReadOutcome.Stale, "stale_session");

                if (string.Equals(errorCode, "session_not_found", StringComparison.Ordinal))
                {
                    // Typed routes bypass the P1Client lane; keep the client state honest
                    // so the caller sees Expired/Uncertain and can relogin. The old
                    // encounter is no longer authoritative in this session.
                    Client.MarkSessionExpired();
                    bool had = Encounter.HasSnapshot;
                    Encounter.Reset();
                    if (had) DispatchEncounterUpdate(new EncounterUpdate { Accepted = true, IsCleared = true, IsTerminal = true });
                    return EncounterReadResult.Fail(EncounterReadOutcome.SessionExpired, "session_not_found", 404);
                }

                // Missing route when alpha is OFF is also 404. Treat as "no encounter";
                // do not claim the server-enabled encounter feature is usable.
                if (isCurrent)
                {
                    bool had = Encounter.HasSnapshot;
                    Encounter.Reset();
                    if (had) DispatchEncounterUpdate(new EncounterUpdate { Accepted = true, IsCleared = true, IsTerminal = true });
                }
                return EncounterReadResult.Fail(EncounterReadOutcome.NotFound, errorCode ?? "encounter_not_found", 404);
            }

            if (reply.StatusCode == 0)
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "network_unavailable", 0);
            if (reply.StatusCode < 200 || reply.StatusCode >= 300)
            {
                return EncounterReadResult.Fail(
                    EncounterReadOutcome.Error,
                    errorCode ?? ("http_" + reply.StatusCode),
                    reply.StatusCode);
            }

            if (root == null)
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "invalid_envelope", reply.StatusCode);

            int schemaVersion;
            string responseRequestId = ReadString(root, "requestId");
            string responseSessionId = ReadString(root, "sessionId");
            try { schemaVersion = root["schemaVersion"] == null ? 0 : root["schemaVersion"].Value<int>(); }
            catch (Exception) { schemaVersion = 0; }

            // GET envelopes carry a server-generated request id (the P1 contract only
            // requires a 32-hex id); only POST mutation envelopes echo the client id.
            if (schemaVersion != 1 ||
                !P1Wire.Hex32(responseRequestId) ||
                !string.Equals(responseSessionId, sessionId, StringComparison.Ordinal))
            {
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "invalid_envelope", reply.StatusCode);
            }

            var result = root["result"] as JObject;
            if (result == null)
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "missing_result", reply.StatusCode);

            EncounterSnapshot snapshot;
            string parseError;
            if (!EncounterSnapshotValidator.TryParse(result.ToString(Formatting.None), out snapshot, out parseError))
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "invalid_snapshot: " + parseError, reply.StatusCode);

            if (!IsCurrentEpoch(sessionId, generation))
                return EncounterReadResult.Fail(EncounterReadOutcome.Stale, "stale_session");

            EncounterUpdate update;
            if (!Encounter.TryApply(snapshot, out update))
                return EncounterReadResult.Fail(EncounterReadOutcome.Stale, update.RejectReason, reply.StatusCode);

            DispatchEncounterUpdate(update);
            return new EncounterReadResult
            {
                Outcome = EncounterReadOutcome.Success,
                State = Encounter.State,
                Update = update,
                StatusCode = reply.StatusCode
            };
        }

        private void DispatchEncounterUpdate(EncounterUpdate update)
        {
            var handler = EncounterUpdated;
            if (handler == null) return;
            long generation = SessionGeneration;
            _dispatcher.Post(() =>
            {
                lock (_disposeGate)
                {
                    // A callback queued before Dispose or relogin must not invoke
                    // the old consumer: check disposed state, epoch, and whether the
                    // subscription still exists at execution time.
                    if (_disposed || SessionGeneration != generation || EncounterUpdated == null) return;
                }
                try { handler(update); }
                catch (Exception) { /* a consumer callback must not corrupt the client lane */ }
            });
        }

        private bool IsCurrentEpoch(string sessionId, long generation)
        {
            return !_disposed &&
                   SessionGeneration == generation &&
                   Guard.Active != null &&
                   Guard.Active.Generation == generation &&
                   string.Equals(Guard.Active.SessionId, sessionId, StringComparison.Ordinal) &&
                   string.Equals(Client.SessionId, sessionId, StringComparison.Ordinal);
        }

        private void RestorePendingCarry()
        {
            if (_pendingCarry == null || Client.SessionId == null) return;
            Client.RestorePendingMutation(_pendingCarry);
            _pendingCarry = null;
        }

        private CancellationTokenSource CreateLinkedToken(CancellationToken caller)
        {
            if (_cts == null) throw new ObjectDisposedException(nameof(ClientSession));
            return CancellationTokenSource.CreateLinkedTokenSource(caller, _cts.Token);
        }

        private EncounterReadResult CanceledOrStale(string sessionId, long generation, string code)
        {
            // A dispose or relogin cancels the in-flight token. That is a stale
            // response, not a network error: the caller must not surface it as
            // actionable failure, and no state/event may be applied afterwards.
            if (_disposed || !IsCurrentEpoch(sessionId, generation))
                return EncounterReadResult.Fail(EncounterReadOutcome.Stale, "stale_session");
            return EncounterReadResult.Fail(EncounterReadOutcome.Error, code);
        }

        private static string ReadString(JObject obj, string name)
        {
            var token = obj[name];
            if (token == null || token.Type != JTokenType.String) return null;
            return token.Value<string>();
        }

        public void Cancel() { try { _cts.Cancel(); } catch (Exception) { } }

        public void Dispose()
        {
            bool already;
            lock (_disposeGate)
            {
                already = _disposed;
                _disposed = true;
            }
            if (already) return;
            EncounterUpdated = null;
            try { _cts.Cancel(); } catch (Exception) { }
            _cts.Dispose();
            Guard.EndSession();

            // Non-blocking shutdown: never spin-wait on the UI thread. Cancel the
            // token source so cancellation-aware reads exit, mark the lane disposed
            // so in-flight reads skip Release() in their finally blocks, and take
            // the lane only if no read holds it. A non-cancelling transport may
            // keep a read in-flight past Dispose; that read exits on its own and
            // its late reply is rejected by the epoch check in ReadEncounterCoreAsync.
            lock (_disposeGate) { _encounterLaneDisposed = true; }
            try
            {
                if (_encounterLane.Wait(0)) _encounterLane.Release();
            }
            catch (ObjectDisposedException) { }
            if (_ownsTransport)
            {
                var disposable = _rawTransport as IDisposable;
                if (disposable != null) disposable.Dispose();
            }
        }
    }
}
