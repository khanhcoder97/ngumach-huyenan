// OPC-15 O-B / Gói 29 lifecycle fix — Timeout/cancellation-aware transport wrapper.
// A transport that ignores CancellationToken must not keep the caller past the
// deadline: the caller completes on time, the late completion is rejected and
// observed (no unobserved exception), and the request identity is preserved so
// upstream adapters can keep the uncertain mutation key/payload.
//
// Pure C#. Owner: OpenCode.

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
        private readonly Func<TimeSpan, CancellationTokenSource, Task> _deadline;

        public TimeoutTransport(IP1Transport inner, TimeSpan timeout)
            : this(inner, timeout, static (delay, cts) =>
            {
                // Deadline task and inner cancellation share one token so a late
                // inner completion can never outlive the caller-visible timeout.
                cts.CancelAfter(delay);
                return Task.Delay(Timeout.InfiniteTimeSpan, cts.Token);
            })
        {
        }

        // Test seam: tests supply an already-completed (or otherwise controlled)
        // deadline task so timeout behaviour is proven without wall-clock sleeps.
        internal TimeoutTransport(
            IP1Transport inner,
            TimeSpan timeout,
            Func<TimeSpan, CancellationTokenSource, Task> deadline)
        {
            _inner = inner ?? throw new ArgumentNullException(nameof(inner));
            if (timeout <= TimeSpan.Zero) throw new ArgumentOutOfRangeException(nameof(timeout));
            _timeout = timeout;
            _deadline = deadline ?? throw new ArgumentNullException(nameof(deadline));
        }

        public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
        {
            if (request == null) throw new ArgumentNullException(nameof(request));
            var correlationId = request.CorrelationId;

            using (var cts = CancellationTokenSource.CreateLinkedTokenSource(ct))
            {
                var innerTask = _inner.SendAsync(request, cts.Token);
                var timeoutTask = _deadline(_timeout, cts);
                var completed = await Task.WhenAny(innerTask, timeoutTask).ConfigureAwait(false);

                if (completed == innerTask)
                {
                    // Normal path: propagate result or caller cancellation.
                    try
                    {
                        return await innerTask.ConfigureAwait(false);
                    }
                    catch (OperationCanceledException) when (ct.IsCancellationRequested)
                    {
                        throw;
                    }
                    catch (OperationCanceledException)
                    {
                        // Cancellation came from the timeout itself but the inner
                        // still completed first; treat as timeout, not success.
                        return TimeoutReply(correlationId);
                    }
                }

                // Deadline reached while inner is still running (or its token
                // was ignored): observe-and-abandon so its late completion or
                // fault can never overwrite the caller result.
                _ = ObserveLate(innerTask);
                if (ct.IsCancellationRequested)
                    throw new OperationCanceledException(ct);
                return TimeoutReply(correlationId);
            }
        }

        private static P1HttpReply TimeoutReply(string correlationId)
        {
            return new P1HttpReply { StatusCode = 0, CorrelationId = correlationId, Body = null };
        }

        // Runs to completion without throwing; folds any late fault/reply into
        // nothing so GC does not report an unobserved task exception and the
        // caller-facing result stays the timeout reply.
        private static async Task ObserveLate(Task<P1HttpReply> innerTask)
        {
            try { await innerTask.ConfigureAwait(false); }
            catch (Exception) { /* late result rejected by Task.WhenAny */ }
        }
    }
}
