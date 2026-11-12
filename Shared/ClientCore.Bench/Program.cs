// gói39 O39-D — standalone measurement executable for the portable client
// core. Fixed workload, warm-up first, distributions reported, environment
// and SDK facts printed with the numbers so a result is never quoted
// without its context.
//
// This is MEASUREMENT ONLY. Nothing here sets a production budget, marks
// the core as capacity-tested, or claims any low-device performance
// (work order O39-D). Numbers describe one machine, one run, fixed
// workloads — they are input to a budget decision, not the decision.
//
// Workloads (fixed sizes, tunable constants are the point of measurement,
// not the tuning):
//   1. parse:      encounter snapshot (real reference fixture), Muse
//                  PLAYBACK_METADATA_v1 manifest (real bytes), SRT cues
//   2. event gate: EncounterView fresh apply + commit cycle, then
//                  duplicate re-apply (the cast must not re-deliver)
//   3. lane/poll:  ClientSession encounter lane under a fixed-cadence
//                  burst poll with a synthetic transport delay; reports
//                  per-read latency distribution, peak in-flight backlog
//                  and allocations per read
//   4. provenance: sha256 + size of every fixture used, printed so the
//                  numbers are traceable to real Muse/reference bytes
//
// Exit codes: 0 measurement complete; 2 fixture missing (UNVERIFIED);
// 1 regression (a parse the suite guarantees now fails, events lost, or a
// typed read failed where the fixture proves it must succeed).

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Runtime;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.Core.Composition;
using NguMach.Client.Core.Encounter;
using NguMach.Client.Core.Handshake;
using NguMach.Client.P1;
using NguMach.Client.Presentation;

namespace ClientCoreBench
{
    internal static class Program
    {
        // Fixed workload sizes. These are the measurement, not a budget.
        private const int WarmupParse = 200;
        private const int IterParse = 2000;
        private const int WarmupMedia = 20;
        private const int IterMedia = 200;
        private const int WarmupSrt = 200;
        private const int IterSrt = 2000;
        private const int EventCycles = 500;
        private const int EventDuplicates = 1000;
        private const int PollWarmupRounds = 3;
        private const int PollRounds = 100;
        private const int PollBurst = 4;
        private const int PollDelayMs = 2;

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

        private static string Sha256Hex(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }

        private static void PrintDistribution(string label, List<double> valuesMs)
        {
            if (valuesMs.Count == 0)
            {
                Console.WriteLine(label + ": no samples");
                return;
            }
            var sorted = valuesMs.OrderBy(v => v).ToList();
            int Idx(double q)
            {
                int i = (int)Math.Ceiling(q * sorted.Count) - 1;
                return i < 0 ? 0 : i;
            }
            double mean = sorted.Average();
            Console.WriteLine(label
                + " n=" + sorted.Count
                + " p50=" + sorted[Idx(0.50)].ToString("F4")
                + " p90=" + sorted[Idx(0.90)].ToString("F4")
                + " p99=" + sorted[Idx(0.99)].ToString("F4")
                + " max=" + sorted[sorted.Count - 1].ToString("F4")
                + " mean=" + mean.ToString("F4"));
        }

        private static double MsSince(long startTimestamp)
        {
            return (Stopwatch.GetTimestamp() - startTimestamp) * 1000.0 / Stopwatch.Frequency;
        }

        // Synthetic fast transport: deterministic envelopes around the real
        // reference fixture bytes. The only variable is the injected delay,
        // which exists to let a fixed-cadence burst build a real backlog at
        // the session's encounter lane.
        private sealed class BenchTransport : IP1Transport
        {
            public const string SessionId = "0123456789abcdef0123456789abcdef";
            private readonly string _snapshotJson;
            private readonly int _delayMs;
            private int _counter;

            public BenchTransport(string snapshotJson, int delayMs)
            {
                _snapshotJson = snapshotJson;
                _delayMs = delayMs;
            }

            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                return SendAsyncCore(request, ct);
            }

            private async Task<P1HttpReply> SendAsyncCore(P1Request request, CancellationToken ct)
            {
                if (request.Method == "POST" && request.Path == "/p1/sessions")
                {
                    string body = "{\"schemaVersion\":1,\"requestId\":\"" + request.CorrelationId +
                        "\",\"sessionId\":\"" + SessionId +
                        "\",\"result\":{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"CHR_BENCHOWNER01\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}}";
                    return new P1HttpReply { StatusCode = 201, Body = body, CorrelationId = request.CorrelationId };
                }
                if (request.Method == "GET" && request.Path == "/p1/encounters/current")
                {
                    await Task.Delay(_delayMs, ct).ConfigureAwait(false);
                    int n = Interlocked.Increment(ref _counter);
                    string body = RewriteSnapshot(n);
                    return new P1HttpReply
                    {
                        StatusCode = 200,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + Guid.NewGuid().ToString("N") +
                               "\",\"sessionId\":\"" + SessionId +
                               "\",\"serverTimeUtc\":\"2026-11-13T00:00:00Z\",\"result\":" + body + "}",
                        CorrelationId = request.CorrelationId
                    };
                }
                return new P1HttpReply
                {
                    StatusCode = 404,
                    Body = "{\"schemaVersion\":1,\"requestId\":\"" + Guid.NewGuid().ToString("N") +
                           "\",\"error\":{\"code\":\"not_found\"}}",
                    CorrelationId = request.CorrelationId
                };
            }

            private string RewriteSnapshot(int n)
            {
                string json = _snapshotJson;
                // The bench session is the owner of this synthetic encounter,
                // exactly as a real server registers the acting session's
                // character; the fixture's registered owner is rewritten to
                // match (the parse benches above run the untouched bytes),
                // and revision/castId advance per read so the typed lane has
                // something new to accept.
                json = json.Replace("\"CHR_0123456789ABCDEF0123456789ABCDEF\"", "\"CHR_BENCHOWNER01\"");
                json = Regex.Replace(json, "\"bossRevision\":\\s*8", "\"bossRevision\": " + (8 + n));
                json = Regex.Replace(json, "\"castId\":\\s*\"CAST-ALPHA-00000001\"",
                    "\"castId\": \"CAST-BENCH" + n.ToString("D8") + "\"");
                return json;
            }
        }

        private static int Main()
        {
            try
            {
                return MainAsync().GetAwaiter().GetResult();
            }
            catch (Exception ex)
            {
                Console.WriteLine("FATAL: " + ex);
                return 1;
            }
        }

        private static async Task<int> MainAsync()
        {
            string fixtures = FindUp(Path.Combine("ClientCore.Tests", "Fixtures"));
            if (fixtures == null)
            {
                Console.WriteLine("UNVERIFIED: fixtures directory not found (expected Shared/ClientCore.Tests/Fixtures).");
                return 2;
            }
            string encounterFixture = Path.Combine(fixtures, "encounter_snapshot_v1_reference_20261104.json");
            string museDir = Path.Combine(fixtures, "MuseMedia");
            string metadataFixture = Path.Combine(museDir, "PLAYBACK_METADATA_v1.json");
            string srtFixture = Path.Combine(museDir, "CIN_000_vi.srt");
            foreach (var path in new[] { encounterFixture, metadataFixture, srtFixture })
            {
                if (!File.Exists(path))
                {
                    Console.WriteLine("UNVERIFIED: missing fixture " + path);
                    return 2;
                }
            }

            byte[] encounterBytes = File.ReadAllBytes(encounterFixture);
            byte[] metadataBytes = File.ReadAllBytes(metadataFixture);
            byte[] srtBytes = File.ReadAllBytes(srtFixture);
            string encounterJson = Encoding.UTF8.GetString(encounterBytes);
            string metadataJson = Encoding.UTF8.GetString(metadataBytes);
            string srtText = Encoding.UTF8.GetString(srtBytes);

            // ---- environment / SDK ----
            var cap = ClientCapability.FromProfile(DeploymentProfile.ProductionOff());
            Console.WriteLine("== environment ==");
            Console.WriteLine("utc: " + DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'"));
            Console.WriteLine("framework: " + RuntimeInformation.FrameworkDescription);
            Console.WriteLine("os: " + RuntimeInformation.OSDescription + " (" + RuntimeInformation.OSArchitecture + ")");
            Console.WriteLine("process: " + RuntimeInformation.ProcessArchitecture + " cores=" + Environment.ProcessorCount);
            Console.WriteLine("gc: serverGC=" + GCSettings.IsServerGC + " latency=" + GCSettings.LatencyMode);
            Console.WriteLine("clientcore: " + cap.ClientCoreVersion + " profile=" + cap.DeploymentProfileId + " encounterUsable=" + cap.IsEncounterUsable);
            Console.WriteLine();

            // ---- provenance ----
            Console.WriteLine("== fixture provenance ==");
            Console.WriteLine("encounter sha256=" + Sha256Hex(encounterBytes) + " bytes=" + encounterBytes.Length + " (reference_20261104)");
            Console.WriteLine("metadata  sha256=" + Sha256Hex(metadataBytes) + " bytes=" + metadataBytes.Length + " (muse pin b1472f2)");
            Console.WriteLine("srt       sha256=" + Sha256Hex(srtBytes) + " bytes=" + srtBytes.Length + " (muse pin b1472f2)");
            Console.WriteLine();

            // ---- parse: encounter snapshot (real fixture bytes) ----
            Warmup(WarmupParse, () =>
            {
                string error; EncounterSnapshot s;
                EncounterSnapshotValidator.TryParse(encounterJson, out s, out error);
            });
            var encounterLatency = new List<double>(IterParse);
            long encounterAllocBefore = GC.GetTotalAllocatedBytes(false);
            for (int i = 0; i < IterParse; i++)
            {
                long t = Stopwatch.GetTimestamp();
                string error; EncounterSnapshot s;
                bool ok = EncounterSnapshotValidator.TryParse(encounterJson, out s, out error);
                encounterLatency.Add(MsSince(t));
                if (!ok) { Console.WriteLine("REGRESSION: encounter fixture no longer parses: " + error); return 1; }
            }
            long encounterAllocAfter = GC.GetTotalAllocatedBytes(false);
            Console.WriteLine("== encounter snapshot parse (real reference fixture) ==");
            PrintDistribution("encounter-parse", encounterLatency);
            Console.WriteLine("encounter-parse alloc/op=" + ((encounterAllocAfter - encounterAllocBefore) / IterParse) + " B");
            Console.WriteLine();

            // ---- parse: Muse PLAYBACK_METADATA_v1 (real manifest bytes) ----
            Warmup(WarmupMedia, () => { MediaPlaybackMetadataParser.Parse(metadataJson); });
            var mediaLatency = new List<double>(IterMedia);
            long mediaAllocBefore = GC.GetTotalAllocatedBytes(false);
            for (int i = 0; i < IterMedia; i++)
            {
                long t = Stopwatch.GetTimestamp();
                var result = MediaPlaybackMetadataParser.Parse(metadataJson);
                mediaLatency.Add(MsSince(t));
                if (!result.Success) { Console.WriteLine("REGRESSION: muse manifest no longer parses: " + result.Error); return 1; }
            }
            long mediaAllocAfter = GC.GetTotalAllocatedBytes(false);
            Console.WriteLine("== muse metadata parse (real PLAYBACK_METADATA_v1, pin b1472f2) ==");
            PrintDistribution("media-parse", mediaLatency);
            Console.WriteLine("media-parse alloc/op=" + ((mediaAllocAfter - mediaAllocBefore) / IterMedia) + " B");
            Console.WriteLine();

            // ---- parse: SRT cues (real fixture bytes) ----
            Warmup(WarmupSrt, () => { MediaSrtParser.Parse(srtText); });
            var srtLatency = new List<double>(IterSrt);
            long srtAllocBefore = GC.GetTotalAllocatedBytes(false);
            int srtCueCount = 0;
            for (int i = 0; i < IterSrt; i++)
            {
                long t = Stopwatch.GetTimestamp();
                var result = MediaSrtParser.Parse(srtText);
                srtLatency.Add(MsSince(t));
                if (!result.Success) { Console.WriteLine("REGRESSION: real SRT no longer parses: " + result.Error); return 1; }
                srtCueCount = result.Cues.Count;
            }
            long srtAllocAfter = GC.GetTotalAllocatedBytes(false);
            Console.WriteLine("== srt cue parse (real CIN_000_vi.srt, cues=" + srtCueCount + ") ==");
            PrintDistribution("srt-parse", srtLatency);
            Console.WriteLine("srt-parse alloc/op=" + ((srtAllocAfter - srtAllocBefore) / IterSrt) + " B");
            Console.WriteLine();

            // ---- event gate: fresh apply + commit, then duplicate re-apply ----
            var eventSnapshots = new List<EncounterSnapshot>(EventCycles);
            for (int i = 0; i < EventCycles; i++)
            {
                string json = Regex.Replace(encounterJson, "\"bossRevision\":\\s*8", "\"bossRevision\": " + (1000 + i));
                json = Regex.Replace(json, "\"castId\":\\s*\"CAST-ALPHA-00000001\"",
                    "\"castId\": \"CAST-VIEW" + i.ToString("D8") + "\"");
                string error; EncounterSnapshot s;
                if (!EncounterSnapshotValidator.TryParse(json, out s, out error))
                {
                    Console.WriteLine("REGRESSION: synthesized snapshot no longer parses: " + error);
                    return 1;
                }
                eventSnapshots.Add(s);
            }
            var view = new EncounterView();
            int delivered = 0, newCasts = 0;
            var cycleLatency = new List<double>(EventCycles);
            long eventAllocBefore = GC.GetTotalAllocatedBytes(false);
            for (int i = 0; i < EventCycles; i++)
            {
                long t = Stopwatch.GetTimestamp();
                EncounterUpdate update;
                bool accepted = view.TryApply(eventSnapshots[i], out update);
                if (accepted && update.IsNewCast) { newCasts++; view.CommitCast(); }
                delivered++;
                cycleLatency.Add(MsSince(t));
            }
            long eventAllocAfter = GC.GetTotalAllocatedBytes(false);
            if (newCasts != EventCycles)
            {
                Console.WriteLine("REGRESSION: expected " + EventCycles + " new casts, got " + newCasts + " (event loss)");
                return 1;
            }
            Console.WriteLine("== encounter event gate (apply+commit, real fixture cast shapes) ==");
            PrintDistribution("apply+commit", cycleLatency);
            Console.WriteLine("apply+commit alloc/op=" + ((eventAllocAfter - eventAllocBefore) / EventCycles) + " B");
            Console.WriteLine("new-cast delivered=" + newCasts + " (every synthesized cast delivered exactly once)");
            // Duplicate re-apply: the same cast must NOT re-deliver.
            long dupAllocBefore = GC.GetTotalAllocatedBytes(false);
            int dupNewCasts = 0;
            for (int i = 0; i < EventDuplicates; i++)
            {
                EncounterUpdate update;
                view.TryApply(eventSnapshots[EventCycles - 1], out update);
                if (update.Accepted && update.IsNewCast) dupNewCasts++;
            }
            long dupAllocAfter = GC.GetTotalAllocatedBytes(false);
            Console.WriteLine("duplicate re-apply x" + EventDuplicates + ": new-cast re-deliveries=" + dupNewCasts
                + " alloc/op=" + ((dupAllocAfter - dupAllocBefore) / EventDuplicates) + " B (must be 0 re-deliveries)");
            if (dupNewCasts != 0) { Console.WriteLine("REGRESSION: duplicate cast re-delivered"); return 1; }
            Console.WriteLine();

            // ---- lane/poll: session encounter lane under a fixed-cadence burst ----
            var pollTransport = new BenchTransport(encounterJson, PollDelayMs);
            using (var session = new ClientSession(pollTransport, ownsTransport: true, useWorldV2: false,
                       characterId: "CHR_BENCHOWNER01", requestTimeout: TimeSpan.FromSeconds(10)))
            {
                var connected = await session.ConnectAsync();
                if (!connected.Success)
                {
                    Console.WriteLine("REGRESSION: connect failed under bench transport: " + connected.Code);
                    return 1;
                }
                int updates = 0, newCastEvents = 0;
                session.EncounterUpdated += update =>
                {
                    Interlocked.Increment(ref updates);
                    if (update.IsNewCast) Interlocked.Increment(ref newCastEvents);
                };
                for (int round = 0; round < PollWarmupRounds; round++)
                    await RunPollRound(session);
                updates = 0; newCastEvents = 0;
                var readLatency = new List<double>(PollRounds * PollBurst);
                int inflight = 0, peakInflight = 0;
                long laneAllocBefore = GC.GetTotalAllocatedBytes(false);
                for (int round = 0; round < PollRounds; round++)
                {
                    var tasks = new Task<EncounterReadResult>[PollBurst];
                    var starts = new long[PollBurst];
                    for (int i = 0; i < PollBurst; i++)
                    {
                        starts[i] = Stopwatch.GetTimestamp();
                        tasks[i] = WrappedRead(session,
                            () => Interlocked.Increment(ref inflight),
                            value => { int snapshot; do { snapshot = Volatile.Read(ref peakInflight); } while (value > snapshot && Interlocked.CompareExchange(ref peakInflight, value, snapshot) != snapshot); },
                            () => Interlocked.Decrement(ref inflight));
                    }
                    for (int i = 0; i < PollBurst; i++)
                    {
                        var result = await tasks[i].ConfigureAwait(false);
                        readLatency.Add(MsSince(starts[i]));
                        if (!result.Success)
                        {
                            Console.WriteLine("REGRESSION: encounter read failed: " + result.Outcome + " " + result.ErrorCode);
                            return 1;
                        }
                    }
                }
                long laneAllocAfter = GC.GetTotalAllocatedBytes(false);
                Console.WriteLine("== encounter lane/poll (burst=" + PollBurst + " delayMs=" + PollDelayMs + " rounds=" + PollRounds + ") ==");
                PrintDistribution("read end-to-end", readLatency);
                int peak = Volatile.Read(ref peakInflight);
                Console.WriteLine("peak in-flight (backlog)=" + peak + " reads of " + PollRounds * PollBurst + " total; transport-delay queue depth observed at the lane");
                Console.WriteLine("lane alloc/read=" + ((laneAllocAfter - laneAllocBefore) / (PollRounds * PollBurst)) + " B");
                Console.WriteLine("updates delivered=" + updates + " new-cast events=" + newCastEvents);
                Console.WriteLine();
            }

            Console.WriteLine("== guardrails ==");
            Console.WriteLine("MEASUREMENT-ONLY: no production budget is set, no caps-test is claimed, and no low-device performance conclusion is drawn from this run (work order O39-D).");
            Console.WriteLine("byte provenance is printed above; fixtures are the real Muse delivery (pin b1472f2) and the real encounter reference (20261104).");
            Console.WriteLine("RESULT: measurement complete");
            return 0;
        }

        private static void Warmup(int iterations, Action action)
        {
            for (int i = 0; i < iterations; i++) action();
        }

        private static async Task<EncounterReadResult> WrappedRead(
            ClientSession session,
            Func<int> increment,
            Action<int> peakCallback,
            Action decrement)
        {
            peakCallback(increment());
            try
            {
                return await session.ReadCurrentEncounterAsync().ConfigureAwait(false);
            }
            finally
            {
                decrement();
            }
        }

        private static Task RunPollRound(ClientSession session)
        {
            var reads = new Task[PollBurst];
            for (int i = 0; i < PollBurst; i++) reads[i] = session.ReadCurrentEncounterAsync();
            return Task.WhenAll(reads);
        }
    }
}
