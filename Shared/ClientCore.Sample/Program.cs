using System;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.Core.Handshake;
using NguMach.Client.P1;

namespace ClientCoreSample
{
    internal static class Program
    {
        private sealed class StubTransport : IP1Transport
        {
            public Task<P1HttpReply> SendAsync(P1Request r, CancellationToken ct)
            {
                if (r.Path == "/p1/sessions")
                    return Task.FromResult(new P1HttpReply { StatusCode = 201, Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId + "\",\"sessionId\":\"0123456789abcdef0123456789abcdef\",\"result\":{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"char_test\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}}", CorrelationId = r.CorrelationId });
                if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                    return Task.FromResult(new P1HttpReply { StatusCode = 200, Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId + "\",\"sessionId\":\"" + r.SessionId + "\",\"result\":{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":2,\"revision\":1,\"self\":{\"characterId\":\"char_test\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}}", CorrelationId = r.CorrelationId });
                return Task.FromResult(new P1HttpReply { StatusCode = 404, Body = "", CorrelationId = r.CorrelationId });
            }
        }

        private static async Task MainAsync()
        {
            using (var session = new ClientSession(new StubTransport(), ownsTransport: false, useWorldV2: false))
            {
                var res = await session.ConnectAsync();
                Console.WriteLine("connect: " + res.Success + " session=" + session.Client.SessionId);
                var guard = session.Guard;
                guard.BeginRequest("r1");
                Console.WriteLine("guard applicable: " + guard.IsApplicable(session.Client.SessionId, "r1", session.SessionGeneration));

                var view = new EncounterView();
                Console.WriteLine("encounter view created, hasSnapshot=" + view.HasSnapshot);

                var cap = new ClientCapability();
                Console.WriteLine("class supported: " + CapabilityHandshake.IsClassSupported(cap, "CLASS_MINH_KIEM"));
                Console.WriteLine("route supported: " + CapabilityHandshake.IsRouteSupported(cap, "/p1/encounters/current"));

                await session.Client.ReadWorldAsync(CancellationToken.None);
                Console.WriteLine("world tick: " + session.Client.World.serverTick);
            }
            Console.WriteLine("sample OK");
        }

        private static void Main() => MainAsync().GetAwaiter().GetResult();
    }
}
