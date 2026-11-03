using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Guards;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class PortableTransportTests
    {
        private sealed class StubTransport : IP1Transport
        {
            private readonly Func<P1Request, P1HttpReply> _handler;
            public StubTransport(Func<P1Request, P1HttpReply> handler) { _handler = handler; }
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
                => Task.FromResult(_handler(request));
        }

        private static string WorldJson => "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"char_test\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";

        private static P1HttpReply Ok(P1Request r, string resultJson) => new P1HttpReply
        {
            StatusCode = 200,
            Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId + "\",\"sessionId\":\"" + r.SessionId + "\",\"result\":" + resultJson + "}",
            CorrelationId = r.CorrelationId
        };

        private static StubTransport SuccessTransport(string sessionId = "0123456789abcdef0123456789abcdef")
        {
            var sid = sessionId;
            return new StubTransport(r =>
            {
                if (r.Path == "/p1/sessions") return new P1HttpReply { StatusCode = 201, Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId + "\",\"sessionId\":\"" + sid + "\",\"result\":" + WorldJson + "}", CorrelationId = r.CorrelationId };
                if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal)) return Ok(r, WorldJson);
                if (r.Path.StartsWith("/p1/quests/", StringComparison.Ordinal)) return Ok(r, "[]");
                if (r.Path.StartsWith("/p1/inventory/", StringComparison.Ordinal)) return Ok(r, "{\"inventoryRevision\":0,\"items\":[],\"currencies\":[]}");
                return new P1HttpReply { StatusCode = 404, Body = "", CorrelationId = r.CorrelationId };
            });
        }

        [Fact]
        public async Task TwoSessions_AreIndependent()
        {
            var c1 = new P1Client(SuccessTransport("0123456789abcdef0123456789abcdef"), useWorldV2: false);
            var c2 = new P1Client(SuccessTransport("fedcba9876543210fedcba9876543210"), useWorldV2: false);
            Assert.True((await c1.ConnectAsync(CancellationToken.None)).Success);
            Assert.True((await c2.ConnectAsync(CancellationToken.None)).Success);
            Assert.NotEqual(c1.SessionId, c2.SessionId);
            Assert.Equal("0123456789abcdef0123456789abcdef", c1.SessionId);
            Assert.Equal("fedcba9876543210fedcba9876543210", c2.SessionId);
            Assert.True((await c1.ReadWorldAsync(CancellationToken.None)).Success);
            Assert.True((await c2.ReadWorldAsync(CancellationToken.None)).Success);
        }

        [Fact]
        public async Task FailedRequest_DoesNotCorruptState()
        {
            var transport = new StubTransport(r =>
            {
                if (r.Path == "/p1/sessions") return new P1HttpReply { StatusCode = 500, Body = "", CorrelationId = r.CorrelationId };
                return new P1HttpReply { StatusCode = 404, Body = "", CorrelationId = r.CorrelationId };
            });
            var client = new P1Client(transport, useWorldV2: false);
            var res = await client.ConnectAsync(CancellationToken.None);
            Assert.False(res.Success);
            Assert.True(string.IsNullOrEmpty(client.SessionId));
        }

        [Fact]
        public async Task Relogin_NewClient_NewSession()
        {
            var c1 = new P1Client(SuccessTransport("0123456789abcdef0123456789abcdef"), useWorldV2: false);
            Assert.True((await c1.ConnectAsync(CancellationToken.None)).Success);
            var oldSession = c1.SessionId;
            // "logout" = drop reference; relogin = new client
            var c2 = new P1Client(SuccessTransport("fedcba9876543210fedcba9876543210"), useWorldV2: false);
            Assert.True((await c2.ConnectAsync(CancellationToken.None)).Success);
            Assert.NotEqual(oldSession, c2.SessionId);
        }

        [Fact]
        public void StaleAsync_OldSessionResponseRejected()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-new", 2);
            // simulate an in-flight response from the previous session arriving late
            Assert.False(g.IsApplicable("sess-old", null, 1));
            // current session still applicable
            Assert.True(g.IsApplicable("sess-new", null, 2));
        }

        [Fact]
        public void StaleAsync_OldRequestRejected()
        {
            var g = new StaleResponseGuard();
            g.BeginSession("sess-1", 1);
            g.BeginRequest("req-new");
            Assert.False(g.IsApplicable("sess-1", "req-old", 1));
            Assert.True(g.IsApplicable("sess-1", "req-new", 1));
        }
    }
}
