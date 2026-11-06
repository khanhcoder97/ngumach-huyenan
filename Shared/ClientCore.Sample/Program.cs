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
                return Task.FromResult(new P1HttpReply { StatusCode = 404, Body = "{\"schemaVersion\":1,\"requestId\":\"0123456789abcdef0123456789abcdef\",\"error\":{\"code\":\"encounter_not_found\"}}", CorrelationId = r.CorrelationId });
            }
        }

        private static async Task MainAsync()
        {
            string baseUrl = Environment.GetEnvironmentVariable("P1_BASE_URL");
            ClientSession session;
            if (!string.IsNullOrWhiteSpace(baseUrl))
            {
                Console.WriteLine("using ClientSessionFactory/HttpClientTransport -> " + baseUrl);
                session = ClientSessionFactory.CreateHttp(baseUrl, characterId: "char_test");
            }
            else
            {
                Console.WriteLine("using StubTransport (no P1_BASE_URL)");
                session = new ClientSession(new StubTransport(), useWorldV2: false, characterId: "char_test");
            }

            // Capability is deployment/source-versioned. Client support is not the same
            // as server enablement; encounter is not usable while the alpha gate is OFF.
            var profile = DeploymentProfile.ProductionOff();
            var cap = ClientCapability.FromProfile(profile);
            Console.WriteLine("capability client=" + cap.ClientCoreVersion + " profile=" + cap.DeploymentProfileId +
                              " encounter-usable=" + cap.IsEncounterUsable);

            using (session)
            {
                var vfx = new EncounterVfxBinder { ReducedMotion = true };
                session.EncounterUpdated += update =>
                {
                    if (update.IsCleared || update.IsNewLife || update.IsNewEncounter)
                        vfx.ClearForLifecycle(EncounterVfxLifecycleChange.EncounterEnded);
                    if (update.IsCleared)
                    {
                        Console.WriteLine("encounter cleared");
                    }
                    else if (update.IsNewCast)
                    {
                        var snapshot = session.Encounter.Snapshot;
                        if (snapshot != null && vfx.ExpirePending(snapshot.ServerTick))
                            Console.WriteLine("vfx late impact dropped before start");

                        EncounterVfxPayload payload;
                        if (snapshot != null && vfx.TryBind(update, snapshot, out payload))
                        {
                            // Start the engine VFX here; commit only after it started.
                            // A deadline that passed before start drops the payload.
                            if (vfx.ExpirePending(snapshot.ServerTick))
                            {
                                Console.WriteLine("vfx late impact dropped");
                            }
                            else
                            {
                                Console.WriteLine("vfx bind: cast=" + payload.CastId +
                                                  " shape=" + payload.Shape.Kind +
                                                  " ticks=" + payload.TicksRemaining +
                                                  " endsAt=" + payload.StateEndsAtTick +
                                                  " reducedMotion=" + payload.ReducedMotion);
                                session.Encounter.CommitCast();
                                vfx.Commit();
                            }
                        }
                    }
                };

                var availability = ServiceAvailabilityPolicy.Evaluate(cap);
                Console.WriteLine("shop service: " + availability.Get("shop").State + " / " +
                                  availability.Get("shop").ReasonCode);
                Console.WriteLine("unsupported services: " + availability.UnsupportedServiceIds.Count);

                var res = await session.ConnectAsync();
                Console.WriteLine("connect: " + res.Success + " session=" + session.Client.SessionId);
                var guard = session.Guard;
                guard.BeginRequest("r1");
                Console.WriteLine("guard applicable: " + guard.IsApplicable(session.Client.SessionId, "r1", session.SessionGeneration));

                // Typed current/detail encounter API: 404 is a typed NotFound result,
                // never an exception or a fabricated snapshot.
                var current = await session.ReadCurrentEncounterAsync();
                Console.WriteLine("encounter current: " + current.Outcome + " " + current.ErrorCode);
                if (current.Success)
                {
                    Console.WriteLine("boss life=" + current.State.BossLifeId + " revision=" + current.State.BossRevision);
                    // The EncounterUpdated handler binds and commits any new-cast VFX.
                }

                var detail = await session.ReadEncounterAsync("ENC-0123456789ABCDEF01234567");
                Console.WriteLine("encounter detail: " + detail.Outcome + " " + detail.ErrorCode);

                var capAlpha = ClientCapability.FromProfile(DeploymentProfile.PrivateAlpha(true));
                Console.WriteLine("alpha profile encounter usable: " + capAlpha.IsEncounterUsable);
                Console.WriteLine("class supported: " + CapabilityHandshake.IsClassSupported(cap, "CLASS_MINH_KIEM"));

                await session.Client.ReadWorldAsync(CancellationToken.None);
                Console.WriteLine("world tick: " + session.Client.World.serverTick);
            }
            Console.WriteLine("sample OK");
        }

        private static void Main() => MainAsync().GetAwaiter().GetResult();
    }
}
