// OPC-15 O2 — Portable composition/facade owning session epoch, transport, adapter,
// subscriptions and cancellation lifecycle. Replaces helper-only demos with a real
// client flow. Pure C#. Owner: OpenCode.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Guards;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace NguMach.Client.Core.Composition
{
    public sealed class ClientSession : IDisposable
    {
        private readonly IP1Transport _transport;
        private readonly bool _ownsTransport;
        private CancellationTokenSource _cts;
        private bool _disposed;

        public P1Client Client { get; private set; }
        public P1ClientAdapter Adapter { get; private set; }
        public StaleResponseGuard Guard { get; private set; }
        public long SessionGeneration { get; private set; }
        public CancellationToken Token { get { return _cts != null ? _cts.Token : CancellationToken.None; } }

        public ClientSession(IP1Transport transport, bool ownsTransport = false, bool useWorldV2 = false)
        {
            _transport = transport ?? throw new ArgumentNullException(nameof(transport));
            _ownsTransport = ownsTransport;
            Client = new P1Client(_transport, useWorldV2: useWorldV2);
            Adapter = new P1ClientAdapter(Client);
            Guard = new StaleResponseGuard();
            _cts = new CancellationTokenSource();
        }

        public async Task<P1Result> ConnectAsync(CancellationToken ct = default)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(ClientSession));
            // end previous session epoch
            Guard.EndSession();
            var res = await Client.ConnectAsync(ct == default ? _cts.Token : ct);
            if (res.Success)
            {
                SessionGeneration++;
                Guard.BeginSession(Client.SessionId, SessionGeneration);
            }
            return res;
        }

        // Re-login: new epoch, old in-flight responses rejected by guard.
        public async Task<P1Result> ReloginAsync(CancellationToken ct = default)
        {
            Guard.EndSession();
            // reset client by creating a fresh one on the same transport
            Client = new P1Client(_transport, useWorldV2: Client.UseWorldV2);
            Adapter = new P1ClientAdapter(Client);
            SessionGeneration = 0;
            return await ConnectAsync(ct);
        }

        public void Cancel() { try { _cts.Cancel(); } catch { } }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            try { _cts.Cancel(); } catch { }
            _cts.Dispose();
            Guard.EndSession();
            if (_ownsTransport)
            {
                var d = _transport as IDisposable;
                if (d != null) d.Dispose();
            }
        }
    }
}
