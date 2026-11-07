using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Transport;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class TimeoutTransportTests
    {
        private static int _lateExceptions;

        static TimeoutTransportTests()
        {
            TaskScheduler.UnobservedTaskException += (s, e) =>
            {
                System.Threading.Interlocked.Increment(ref _lateExceptions);
                e.SetObserved();
            };
        }

        private sealed class SlowTransport : IP1Transport
        {
            private readonly int _delayMs;
            public SlowTransport(int delayMs) { _delayMs = delayMs; }
            public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                await Task.Delay(_delayMs, ct);
                return new P1HttpReply { StatusCode = 200, CorrelationId = request.CorrelationId };
            }
        }

        // Ignores CancellationToken entirely (the pre-fix bug) and completes only
        // when the test releases it, so the deadline path never depends on a sleep.
        private sealed class GatedTransport : IP1Transport
        {
            private readonly TaskCompletionSource<P1HttpReply> _gate =
                new TaskCompletionSource<P1HttpReply>(TaskCreationOptions.RunContinuationsAsynchronously);

            public Task<P1HttpReply> Sent => _gate.Task;

            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct) => _gate.Task;

            public void Complete(P1HttpReply reply) => _gate.TrySetResult(reply);
        }

        // A deadline that is already reached: the wrapper must time out without
        // consulting the wall clock, which keeps this test deterministic under CI load.
        private static Task ImmediateDeadline(TimeSpan timeout, CancellationTokenSource cts)
            => Task.CompletedTask;

        [Fact]
        public async Task FastInner_ReturnsNormally()
        {
            var inner = new SlowTransport(10);
            var t = new TimeoutTransport(inner, TimeSpan.FromSeconds(2));
            var req = new P1Request("GET", "/x", null, "s", "c");
            var reply = await t.SendAsync(req, CancellationToken.None);
            Assert.Equal(200, reply.StatusCode);
        }

        [Fact]
        public async Task SlowInner_TimesOut()
        {
            var inner = new SlowTransport(5000);
            var t = new TimeoutTransport(inner, TimeSpan.FromMilliseconds(50));
            var req = new P1Request("GET", "/x", null, "s", "c");
            var reply = await t.SendAsync(req, CancellationToken.None);
            Assert.Equal(0, reply.StatusCode);
        }

        [Fact]
        public async Task CallerCancellation_Propagates()
        {
            var inner = new SlowTransport(5000);
            var t = new TimeoutTransport(inner, TimeSpan.FromSeconds(10));
            var cts = new CancellationTokenSource();
            cts.Cancel();
            var req = new P1Request("GET", "/x", null, "s", "c");
            await Assert.ThrowsAnyAsync<OperationCanceledException>(async () =>
                await t.SendAsync(req, cts.Token));
        }

        [Fact]
        public async Task IgnoringInner_TimesOutOnControlledDeadline()
        {
            // The inner transport never completes on its own. A controlled,
            // already-reached deadline proves the wrapper returns without waiting
            // for it, so CI scheduling cannot turn this into a budget race.
            var inner = new GatedTransport();
            var t = new TimeoutTransport(inner, TimeSpan.FromMilliseconds(40), ImmediateDeadline);
            var req = new P1Request("POST", "/p1/world/interact", "payload", "s", "key-1");
            var reply = await t.SendAsync(req, CancellationToken.None);
            Assert.Equal(0, reply.StatusCode);
            Assert.Equal("key-1", reply.CorrelationId);
            Assert.False(inner.Sent.IsCompleted, "a timed-out call must not wait for the inner");
            inner.Complete(new P1HttpReply { StatusCode = 200, CorrelationId = "late" });
        }

        [Fact]
        public async Task IgnoringInner_LateCompletionRejectedAndObserved()
        {
            var inner = new GatedTransport();
            var t = new TimeoutTransport(inner, TimeSpan.FromMilliseconds(30), ImmediateDeadline);
            var req = new P1Request("GET", "/x", null, "s", "key-2");
            var reply = await t.SendAsync(req, CancellationToken.None);
            Assert.Equal(0, reply.StatusCode);
            Assert.Equal("key-2", reply.CorrelationId);
            // Release the abandoned inner task; ObserveLate consumes it, so the
            // late success cannot overwrite the timeout reply or go unobserved.
            inner.Complete(new P1HttpReply { StatusCode = 200, CorrelationId = "late" });
            await inner.Sent;
            await Task.Yield();
            Assert.Equal(0, reply.StatusCode);
            var exceptions = System.Threading.Volatile.Read(ref _lateExceptions);
            Assert.Equal(0, exceptions);
        }

        [Fact]
        public void ZeroTimeout_Throws()
        {
            Assert.Throws<ArgumentOutOfRangeException>(() =>
                new TimeoutTransport(new SlowTransport(1), TimeSpan.Zero));
        }

        [Fact]
        public void NullInner_Throws()
        {
            Assert.Throws<ArgumentNullException>(() =>
                new TimeoutTransport(null, TimeSpan.FromSeconds(1)));
        }
    }
}
