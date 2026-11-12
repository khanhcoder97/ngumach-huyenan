using System;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Guards;
using NguMach.Client.Core.Handshake;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

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

        // gói39 O39-D — the sample runs on the REAL Muse delivery metadata
        // (branch muse/media-production-20261104, pin b1472f2) instead of a
        // host-crafted DTO, and prints byte-level provenance so the numbers
        // are traceable. The content root for path policy probes is the
        // fixture directory; deliveries stay root-relative from there.
        private static string FindUp(string relativeUnderShared)
        {
            string dir = AppContext.BaseDirectory;
            for (int i = 0; i < 14; i++)
            {
                string candidate = Path.Combine(dir, "Shared", relativeUnderShared);
                if (Directory.Exists(candidate)) return candidate;
                var parent = Directory.GetParent(dir);
                if (parent == null) break;
                dir = parent.FullName;
            }
            return null;
        }

        private static void PrintMediaProvenance()
        {
            Console.WriteLine("== PLAYBACK_METADATA_v1 (real Muse delivery fixture, pin b1472f2) ==");
            string museDir = FindUp(Path.Combine("ClientCore.Tests", "Fixtures", "MuseMedia"));
            if (museDir == null)
            {
                Console.WriteLine("MuseMedia fixtures not found — skipping real-metadata demo.");
                return;
            }
            var doc = MediaMetadataLoader.LoadDocument(museDir, "PLAYBACK_METADATA_v1.json");
            if (!doc.Success)
            {
                Console.WriteLine("metadata load FAILED: " + doc.Error);
                return;
            }
            Console.WriteLine("document: manifest=" + doc.ManifestId
                + " scenes=" + doc.ScenesTotal
                + " embeddedSoundtrack=" + doc.WithEmbeddedSoundtrack
                + " silent=" + doc.Silent);
            Console.WriteLine("provenance: " + doc.Provenance);
            foreach (var scene in doc.Scenes)
                Console.WriteLine("scene " + scene.SceneId + " " + scene.AudioOwnership
                    + " burnedIntoRuntimeVideo=" + (scene.Subtitle != null && scene.Subtitle.BurnedIntoRuntimeVideo)
                    + " runtimeDeliveries=" + scene.RuntimeDeliveryPaths.Count);
            var scene0 = doc.Scenes.Count > 0 ? doc.Scenes[0] : null;
            if (scene0 != null)
                Console.WriteLine("first-scene provenance: " + (scene0.Provenance ?? "-"));

            foreach (var srtName in new[] { "CIN_000_vi.srt", "CIN_001_vi.srt" })
            {
                string srtPath = Path.Combine(museDir, srtName);
                if (!File.Exists(srtPath)) continue;
                var parsed = MediaSrtParser.Parse(File.ReadAllText(srtPath));
                Console.WriteLine("srt " + srtName + ": cues=" + (parsed.Success ? parsed.Cues.Count : -1)
                    + " success=" + parsed.Success);
            }

            string delivery = scene0 != null && scene0.RuntimeDeliveryPaths.Count > 0
                ? scene0.RuntimeDeliveryPaths[0]
                : "ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps.mp4";
            string accepted = MediaPathPolicy.TryCanonicalize(museDir, delivery);
            string refused = MediaPathPolicy.TryCanonicalize(museDir, "../../private.mp4");
            Console.WriteLine("policy: real delivery canonical in-root=" + (accepted != null)
                + " traversal refused=" + (refused == null));
        }

        private static async Task MainAsync()
        {
            PrintMediaProvenance();
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
