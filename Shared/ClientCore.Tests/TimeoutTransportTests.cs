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
