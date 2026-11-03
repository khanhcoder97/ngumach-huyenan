// OPC-15 O-B — Timeout/cancellation-aware transport wrapper for portable core.
// Wraps any IP1Transport with a per-request timeout and cancellation propagation.
// Pure C# (no engine dep). Ensures an in-flight request cannot hang forever and
// that cancellation flows through to the inner transport.

using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Core.Transport
{
    public sealed class TimeoutTransport : IP1Transport
    {
        private readonly IP1Transport _inner;
        private readonly TimeSpan _timeout;

        public TimeoutTransport(IP1Transport inner, TimeSpan timeout)
        {
            _inner = inner ?? throw new ArgumentNullException(nameof(inner));
            if (timeout <= TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(timeout));
            _timeout = timeout;
        }

        public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
        {
            using (var cts = CancellationTokenSource.CreateLinkedTokenSource(ct))
            {
                cts.CancelAfter(_timeout);
                try
                {
                    return await _inner.SendAsync(request, cts.Token);
                }
                catch (OperationCanceledException)
                {
                    if (ct.IsCancellationRequested)
                        throw; // caller cancelled
                    // timeout
                    return new P1HttpReply { StatusCode = 0, CorrelationId = request.CorrelationId, Body = null };
                }
            }
        }
    }
}
