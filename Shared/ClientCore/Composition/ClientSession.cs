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

    public sealed class ClientSession : IDisposable, IAsyncDisposable
    {
        // Default bound for awaitable cleanup. Dispose()/DisposeAsync() never
        // block the UI thread; DisposeAsync() additionally waits at most this
        // long for an in-flight read to unwind before it returns.
        public static readonly TimeSpan DefaultDisposeTimeout = TimeSpan.FromSeconds(2);

        private readonly IP1Transport _rawTransport;
        private readonly IP1Transport _transport;
        private readonly bool _ownsTransport;
        private readonly string _characterId;
        // O38-A: when the session is created without an explicit characterId,
        // the server assigns one at connect. The authoritative owner is always
        // the connected world's self.characterId (captured in ConnectAsync
        // success), never null after a successful connect.
        private string _authoritativeCharacterId;
        private readonly IMainThreadDispatcher _dispatcher;
        private readonly SemaphoreSlim _encounterLane = new SemaphoreSlim(1, 1);
        private readonly object _disposeGate = new object();
        private CancellationTokenSource _cts;
        private PendingMutationSnapshot _pendingCarry;
        private volatile bool _disposed;
        private bool _encounterLaneDisposed;

        public P1Client Client { get; private set; }
        // Stable for the whole session lifetime: presenters keep one reference
        // and always reach the current epoch (a relogin swaps Client, not Adapter).
        public P1ClientAdapter Adapter { get; }
        public StaleResponseGuard Guard { get; private set; }
        public EncounterView Encounter { get; }
        // Host-supplied deployment facts. Production-off is the default; no route is
        // ever advertised just because the client knows how to call it.
        public ClientCapability Capability { get; }
        public ServiceAvailability Availability { get; }
        public long SessionGeneration { get; private set; }
        // Upper bound DisposeAsync() may spend waiting for an in-flight read.
        public TimeSpan DisposeTimeout { get; }
        public IMainThreadDispatcher Dispatcher => _dispatcher;
        // After Dispose the token source is released: reads observe cancellation
        // through the captured token they already hold, and a fresh property read
        // degrades to CancellationToken.None instead of throwing.
        public CancellationToken Token { get { var cts = _cts; return cts != null ? cts.Token : CancellationToken.None; } }
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
            DeploymentProfile profile = null,
            TimeSpan? disposeTimeout = null)
        {
            _rawTransport = transport ?? throw new ArgumentNullException(nameof(transport));
            _ownsTransport = ownsTransport;
            _characterId = string.IsNullOrWhiteSpace(characterId) ? null : characterId;
            _dispatcher = dispatcher ?? new SynchronousDispatcher();
            _transport = new TimeoutTransport(_rawTransport, requestTimeout ?? TimeSpan.FromSeconds(30));
            DisposeTimeout = disposeTimeout ?? DefaultDisposeTimeout;
            Client = new P1Client(_transport, useWorldV2: useWorldV2, characterId: _characterId);
            // One adapter for the session's lifetime, bound to the live client
            // through a provider so a relogin is invisible to presenters and a
            // disposed session degrades to a typed "disposed" failure instead of
            // touching a dead transport or the previous epoch's state.
            Adapter = new P1ClientAdapter(() => _disposed ? null : Client);
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
                    _authoritativeCharacterId = Client.World != null && Client.World.self != null
                        ? Client.World.self.characterId
                        : null;
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
            _authoritativeCharacterId = null;

            var previous = Client;
            Client = new P1Client(_transport, useWorldV2: previous.UseWorldV2, characterId: _characterId);
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

            // captureoldclient + epoch before await: guard happens inside Core
            // before any receipt/cooldown/world mutation.
            var client = Client;
            string expectedSessionId = client.SessionId;
            long expectedGeneration = SessionGeneration;

            using (var linked = CreateLinkedToken(ct))
            {
                P1Result result;
                try
                {
                    result = await client.ReturnFromDeathAsync(linked.Token, expectedSessionId);
                }
                catch (OperationCanceledException)
                {
                    // Dispose/caller cancelled the token mid-request. Surface as stale,
                    // not a throw; pending key is preserved inside P1Client.
                    return P1Result.Fail("stale_session");
                }

                // Facade-level confirmation: dispose/relogin between Core return and
                // here must not let a stale result through.
                if (!IsCurrentEpoch(expectedSessionId, expectedGeneration))
                    return P1Result.Fail("stale_session");

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

            // Owner identity: the snapshot must carry exactly this session's own
            // character as its registered owner, so two sessions can never read
            // each other's encounter. The expected owner is the explicit
            // constructor id when given, otherwise the server-assigned character
            // captured from session/world at connect. A session that never
            // captured one keeps the shape-only validation.
            string expectedOwner = !string.IsNullOrEmpty(_characterId) ? _characterId : _authoritativeCharacterId;
            if (!string.IsNullOrEmpty(expectedOwner) &&
                (snapshot.RegisteredCharacterIds == null || snapshot.RegisteredCharacterIds.Count == 0 ||
                 !string.Equals(snapshot.RegisteredCharacterIds[0], expectedOwner, StringComparison.Ordinal)))
                return EncounterReadResult.Fail(EncounterReadOutcome.Error, "invalid_snapshot: owner mismatch", reply.StatusCode);

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
            // captureoldclient: a failed relogin replaces Client without bumping
            // generation, so compare the reference too.
            var capturedClient = Client;
            long generation = SessionGeneration;
            _dispatcher.Post(() =>
            {
                Action<EncounterUpdate> live;
                lock (_disposeGate)
                {
                    if (_disposed || SessionGeneration != generation || Client != capturedClient) return;
                    // Re-check the subscription when the callback actually runs:
                    // an unsubscribe (or a new subscriber) between Post and drain
                    // must change who receives this update.
                    live = StillSubscribed(handler, EncounterUpdated);
                    if (live == null) return;
                }
                try { live(update); }
                catch (Exception) { /* a consumer callback must not corrupt the client lane */ }
            });
        }

        // Returns the subset of the captured handlers that is still subscribed, or
        // null when none is. Handlers added after Post() never receive it.
        private static Action<EncounterUpdate> StillSubscribed(
            Action<EncounterUpdate> captured, Action<EncounterUpdate> current)
        {
            if (captured == null || current == null) return null;
            var live = current.GetInvocationList();
            Action<EncounterUpdate> result = null;
            foreach (var entry in captured.GetInvocationList())
            {
                foreach (var candidate in live)
                {
                    if (ReferenceEquals(candidate, entry))
                    {
                        result += (Action<EncounterUpdate>)entry;
                        break;
                    }
                }
            }
            return result;
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
            var cts = _cts;
            if (cts == null) throw new ObjectDisposedException(nameof(ClientSession));
            return CancellationTokenSource.CreateLinkedTokenSource(caller, cts.Token);
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

        public void Cancel() { var cts = _cts; if (cts == null) return; try { cts.Cancel(); } catch (Exception) { } }

        // Claims the one-shot right to run cleanup. The first caller wins and
        // performs its own cleanup (sync non-blocking, or async bounded); any
        // later Dispose/DisposeAsync is a no-op so cleanup can never run twice.
        private bool TryBeginDispose()
        {
            lock (_disposeGate)
            {
                if (_disposed) return false;
                _disposed = true;
            }
            EncounterUpdated = null;
            var cts = _cts;
            _cts = null;
            if (cts != null)
            {
                try { cts.Cancel(); } catch (Exception) { }
                cts.Dispose();
            }
            Guard.EndSession();
            return true;
        }

        private void DisposeOwnedTransport()
        {
            if (!_ownsTransport) return;
            var disposable = _rawTransport as IDisposable;
            if (disposable != null) disposable.Dispose();
        }

        // Non-blocking shutdown: never spin-wait on the UI thread. Cancel the
        // token source so cancellation-aware reads exit, mark the lane disposed
        // so in-flight reads skip Release() in their finally blocks, and take
        // the lane only if no read holds it. A non-cancelling transport may
        // keep a read in-flight past Dispose; that read exits on its own and
        // its late reply is rejected by the epoch check in ReadEncounterCoreAsync.
        public void Dispose()
        {
            if (!TryBeginDispose()) return;
            lock (_disposeGate) { _encounterLaneDisposed = true; }
            try
            {
                if (_encounterLane.Wait(0)) _encounterLane.Release();
            }
            catch (ObjectDisposedException) { }
            DisposeOwnedTransport();
        }

        // Awaitable, bounded cleanup for hosts that need to know when the session
        // is really torn down. It never blocks the caller's thread: the wait is
        // async and capped by DisposeTimeout, so a transport that ignores
        // cancellation can delay cleanup but can never hang it.
        public async ValueTask DisposeAsync()
        {
            if (!TryBeginDispose()) return;
            bool acquired = false;
            try
            {
                acquired = await _encounterLane.WaitAsync(DisposeTimeout).ConfigureAwait(false);
            }
            catch (ObjectDisposedException) { }
            catch (OperationCanceledException) { }
            lock (_disposeGate) { _encounterLaneDisposed = true; }
            if (acquired)
            {
                try { _encounterLane.Release(); }
                catch (ObjectDisposedException) { }
                catch (SemaphoreFullException) { }
            }
            DisposeOwnedTransport();
        }
    }
}
