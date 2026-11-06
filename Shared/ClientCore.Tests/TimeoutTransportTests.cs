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

        // Ignores CancellationToken entirely: the pre-fix bug.
        private sealed class IgnoringTransport : IP1Transport
        {
            private readonly int _delayMs;
            public IgnoringTransport(int delayMs) { _delayMs = delayMs; }
            public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                await Task.Delay(_delayMs);
                return new P1HttpReply { StatusCode = 200, CorrelationId = "late" };
            }
        }

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
        public async Task IgnoringInner_TimesOutOnDeadlineWithinBudget()
        {
            // Codex harness at 685b888: 40ms timeout still not done after 316ms.
            var inner = new IgnoringTransport(5000);
            var t = new TimeoutTransport(inner, TimeSpan.FromMilliseconds(40));
            var req = new P1Request("POST", "/p1/world/interact", "payload", "s", "key-1");
            var sw = System.Diagnostics.Stopwatch.StartNew();
            var reply = await t.SendAsync(req, CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(2));
            sw.Stop();
            Assert.Equal(0, reply.StatusCode);
            Assert.Equal("key-1", reply.CorrelationId);
            Assert.True(sw.ElapsedMilliseconds < 1000,
                "caller must complete in deadline, took " + sw.ElapsedMilliseconds + "ms");
        }

        [Fact]
        public async Task IgnoringInner_LateCompletionRejectedAndObserved()
        {
            var inner = new IgnoringTransport(150);
            var t = new TimeoutTransport(inner, TimeSpan.FromMilliseconds(30));
            var req = new P1Request("GET", "/x", null, "s", "key-2");
            var reply = await t.SendAsync(req, CancellationToken.None).WaitAsync(TimeSpan.FromSeconds(2));
            Assert.Equal(0, reply.StatusCode);
            Assert.Equal("key-2", reply.CorrelationId);
            // Wait for the abandoned inner task, then assert nothing throws.
            await Task.Delay(250);
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
