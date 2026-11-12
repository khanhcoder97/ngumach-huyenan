// OPC-16 O1 — death-return typed parser and replay semantics.
// Frozen at Qoder 4b59b08: DeathReturnRequest/Response.schema.json and
// DEC-DEATH-RETURN-20261105. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class DeathReturnTests
    {
        private const string Session = "11111111111111111111111111111111";
        private const string Character = "CHR_TEST";

        private static string WorldJson(int hp = 50) =>
            "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1840,\"revision\":12,\"self\":{\"characterId\":\"" + Character +
            "\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":" + hp + ",\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";

        private sealed class ScriptedTransport : IP1Transport
        {
            public Func<P1Request, CancellationToken, Task<P1HttpReply>> Handler;
            public readonly List<P1Request> Requests = new List<P1Request>();
            public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
            {
                lock (Requests) Requests.Add(request);
                return Handler(request, ct);
            }
        }

        private static P1HttpReply SessionReply(P1Request r)
        {
            return new P1HttpReply
            {
                StatusCode = 201,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + Session + "\",\"result\":" + WorldJson(0) + "}"
            };
        }

        private static string ResultJson(bool applied, bool replayed, int hp = 50, long? nextTick = 1900,
            string mapId = "MAP_BEN_MUA", int xpPenalty = 0)
        {
            return "{\"applied\":" + (applied ? "true" : "false") +
                   ",\"replayed\":" + (replayed ? "true" : "false") +
                   ",\"mapId\":\"" + mapId + "\",\"xWu\":18.0,\"yWu\":0.0,\"hp\":" + hp +
                   ",\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"serverTick\":1840,\"revision\":12," +
                   "\"cleared\":{\"inflightCasts\":1,\"reservedCounters\":0,\"guardWindowClosed\":false,\"movementWindowReset\":true}," +
                   "\"penalties\":{\"xp\":" + xpPenalty + ",\"currency\":0,\"durability\":0}," +
                   "\"nextReturnAllowedAtTick\":" + (nextTick.HasValue ? nextTick.Value.ToString() : "null") + "}";
        }

        private static P1HttpReply Envelope(P1Request r, int status, string resultJson)
        {
            return new P1HttpReply
            {
                StatusCode = status,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + Session + "\",\"serverTimeUtc\":\"2026-11-05T09:00:01Z\",\"result\":" +
                       resultJson + "}"
            };
        }

        private static P1HttpReply Error(P1Request r, int status, string code, bool retryable, long? tick = null)
        {
            return new P1HttpReply
            {
                StatusCode = status,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + Session + "\",\"error\":{\"code\":\"" + code +
                       "\",\"messageKey\":\"P1.ERROR." + code.ToUpperInvariant() + "\",\"retryable\":" +
                       (retryable ? "true" : "false") + ",\"fieldErrors\":[],\"correlationId\":\"" +
                       r.CorrelationId + "\"" + (tick.HasValue ? ",\"nextReturnAllowedAtTick\":" + tick.Value : "") +
                       "}}"
            };
        }

        private static ScriptedTransport Transport(Func<P1Request, P1HttpReply> choose, out P1Client client)
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + Session + "\",\"result\":" + WorldJson() + "}"
                    });
                if (r.Path == "/p1/actor/death-return") return Task.FromResult(choose(r));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            client = new P1Client(transport);
            Assert.True(client.ConnectAsync(CancellationToken.None).GetAwaiter().GetResult().Success);
            return transport;
        }

        [Fact]
        public async Task Commit_SendsEmptyIntentAndFreshReadsWorld()
        {
            var transport = Transport(r => Envelope(r, 200, ResultJson(true, false)), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.True(result.Success, result.Code);
            var sent = transport.Requests[1];
            Assert.Equal("POST", sent.Method);
            Assert.Equal("/p1/actor/death-return", sent.Path);
            Assert.Contains("\"payload\":{}", sent.Body);
            Assert.DoesNotContain("xWu", sent.Body);
            Assert.DoesNotContain("yWu", sent.Body);
            Assert.DoesNotContain("mapId", sent.Body);
            var envelope = P1Wire.Decode<P1Envelope<P1DeathReturnIntent>>(sent.Body);
            Assert.Equal(1, envelope.schemaVersion);
            Assert.True(P1Wire.Hex32(envelope.idempotencyKey));
            Assert.True(P1Wire.Hex32(envelope.requestId));
            Assert.NotNull(client.LastDeathReturn);
            Assert.True(client.LastDeathReturn.applied);
            Assert.False(client.LastDeathReturn.replayed);
            Assert.Equal("MAP_BEN_MUA", client.LastDeathReturn.mapId);
            Assert.Equal(18.0, client.LastDeathReturn.xWu);
            Assert.Equal(50, client.LastDeathReturn.hp);
            Assert.Equal(1900, client.NextReturnAllowedAtTick);
            Assert.Equal(P1ConnectionState.Ready, client.State);
            Assert.Equal(3, transport.Requests.Count); // session, return, fresh world read
            Assert.StartsWith("/p1/world/", transport.Requests[2].Path);
        }

        [Fact]
        public async Task CommittedReplay_ReturnsSameSnapshotWithAppliedFalse()
        {
            var transport = Transport(r => Envelope(r, 200, ResultJson(false, true)), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.NotNull(client.LastDeathReturn);
            Assert.False(client.LastDeathReturn.applied);
            Assert.True(client.LastDeathReturn.replayed);
            Assert.Equal(12, client.LastDeathReturn.revision);
            Assert.Equal(1900, client.NextReturnAllowedAtTick);
            Assert.Equal(3, transport.Requests.Count);
            Assert.Equal(P1ConnectionState.Ready, client.State);
        }

        [Fact]
        public async Task Cooldown_CarriesServerDeadlineAndIsRetryable()
        {
            var transport = Transport(r => Error(r, 422, "death_return_cooldown", true, 1960), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("death_return_cooldown", result.Code);
            Assert.Equal(1960, client.NextReturnAllowedAtTick);
            Assert.False(client.HasPendingMutation);
            Assert.Equal(P1ConnectionState.Ready, client.State);
            Assert.Equal(2, transport.Requests.Count);
        }

        [Theory]
        [InlineData("not_downed", 409)]
        [InlineData("unknown_map", 409)]
        [InlineData("idempotency_conflict", 409)]
        [InlineData("invalid_payload", 400)]
        public async Task DefiniteRejections_ClearPendingAndReachUi(string code, int status)
        {
            Transport(r => Error(r, status, code, false), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal(code, result.Code);
            Assert.False(client.HasPendingMutation);
            Assert.Null(client.LastDeathReturn);
        }

        [Fact]
        public async Task RouteAbsent_IsFeatureUnavailableNotAmbiguous()
        {
            Transport(r => new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" }, out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("feature_unavailable", result.Code);
            Assert.False(client.HasPendingMutation);
        }

        [Fact]
        public async Task Disabled503_IsDefiniteNotAmbiguous()
        {
            Transport(r => Error(r, 503, "death_return_disabled", false), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("death_return_disabled", result.Code);
            Assert.False(client.HasPendingMutation);
            Assert.Equal(P1ConnectionState.Ready, client.State);
        }

        [Fact]
        public async Task AmbiguousSubmit_RetryKeepsSameRequestAndKey()
        {
            bool fail = true;
            var transport = Transport(r =>
            {
                if (fail) return new P1HttpReply { StatusCode = 0, CorrelationId = r.CorrelationId };
                return Envelope(r, 200, ResultJson(true, false));
            }, out var client);

            var first = await client.ReturnFromDeathAsync(CancellationToken.None);
            Assert.False(first.Success);
            Assert.Equal("mutation_outcome_unknown", first.Code);
            Assert.True(client.HasPendingMutation);
            var sent = transport.Requests[1];
            var firstBody = P1Wire.Decode<P1Envelope<P1DeathReturnIntent>>(sent.Body);

            fail = false;
            var retry = await client.RetryPendingAsync(CancellationToken.None);

            Assert.True(retry.Success, retry.Code);
            var retrySent = transport.Requests[2];
            var retryBody = P1Wire.Decode<P1Envelope<P1DeathReturnIntent>>(retrySent.Body);
            Assert.Equal(sent.CorrelationId, retrySent.CorrelationId);
            Assert.Equal(firstBody.requestId, retryBody.requestId);
            Assert.Equal(firstBody.idempotencyKey, retryBody.idempotencyKey);
            Assert.False(client.HasPendingMutation);
        }

        [Theory]
        [InlineData("hp_zero")]
        [InlineData("both_flags")]
        [InlineData("penalty")]
        [InlineData("bad_map")]
        [InlineData("negative_tick")]
        public async Task InvalidAuthoritativeSnapshot_IsNotAppliedAndKeepsPending(string mutation)
        {
            string json = ResultJson(true, false);
            if (mutation == "hp_zero") json = ResultJson(true, false, hp: 0);
            if (mutation == "both_flags") json = ResultJson(true, true);
            if (mutation == "penalty") json = ResultJson(true, false, xpPenalty: 1);
            if (mutation == "bad_map") json = ResultJson(true, false, mapId: "map_ben_mua");
            if (mutation == "negative_tick") json = ResultJson(true, false, nextTick: -1);
            var transport = Transport(r => Envelope(r, 200, json), out var client);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("mutation_outcome_unknown", result.Code);
            Assert.Null(client.LastDeathReturn);
            Assert.True(client.HasPendingMutation);
            Assert.Equal(2, transport.Requests.Count); // no world read on an invalid receipt
        }

        [Fact]
        public async Task ReferenceFixture_ParsesThroughClient()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + Session + "\",\"result\":" + WorldJson() + "}"
                    });
                if (r.Path == "/p1/actor/death-return")
                {
                    var root = JObject.Parse(File.ReadAllText(FindFixture()));
                    root["requestId"] = r.CorrelationId;
                    root["sessionId"] = Session;
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = root.ToString(Newtonsoft.Json.Formatting.None)
                    });
                }
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.Equal(1840, client.LastDeathReturn.serverTick);
            Assert.Equal(1900, client.NextReturnAllowedAtTick);
            Assert.Equal(1, client.LastDeathReturn.cleared.inflightCasts);
        }

        [Fact]
        public async Task InvalidFixture_IsRejected()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/actor/death-return")
                {
                    var root = JObject.Parse(File.ReadAllText(FindInvalidFixture()));
                    root["requestId"] = r.CorrelationId;
                    root["sessionId"] = Session;
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = root.ToString(Newtonsoft.Json.Formatting.None)
                    });
                }
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("mutation_outcome_unknown", result.Code);
            Assert.Null(client.LastDeathReturn);
        }

        [Fact]
        public async Task AmbiguousSubmit_RetryFailsAgain_KeepsPending()
        {
            int failCount = 0;
            var transport = Transport(r =>
            {
                failCount++;
                if (failCount <= 2) return new P1HttpReply { StatusCode = 0, CorrelationId = r.CorrelationId };
                return Envelope(r, 200, ResultJson(true, false));
            }, out var client);

            var first = await client.ReturnFromDeathAsync(CancellationToken.None);
            Assert.False(first.Success);
            Assert.True(client.HasPendingMutation);

            var second = await client.RetryPendingAsync(CancellationToken.None);
            Assert.False(second.Success);
            Assert.True(client.HasPendingMutation);

            var third = await client.RetryPendingAsync(CancellationToken.None);
            Assert.True(third.Success, third.Code);
            Assert.False(client.HasPendingMutation);
            Assert.NotNull(client.LastDeathReturn);
            Assert.True(client.LastDeathReturn.applied);
        }

        [Fact]
        public async Task Commit_WorldReadFailure_ReturnsRefreshPending()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/actor/death-return")
                    return Task.FromResult(Envelope(r, 200, ResultJson(true, false)));
                if (r.Path.StartsWith("/p1/world/", StringComparison.Ordinal))
                    return Task.FromResult(Error(r, 500, "internal_error", false));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.ReturnFromDeathAsync(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("death_return_refresh_pending", result.Code);
            Assert.NotNull(client.LastDeathReturn);
            Assert.True(client.LastDeathReturn.applied);
        }

        private static string FindFixture()
        {
            return FindFixtureFile("death_return_response_v1_reference_20261105.json");
        }

        private static string FindInvalidFixture()
        {
            return FindFixtureFile("death_return_response_v1_invalid_20261105.json");
        }

        private static string FindFixtureFile(string name)
        {
            var relative = Path.Combine("Shared", "ClientCore.Tests", "Fixtures", name);
            var dir = new DirectoryInfo(AppContext.BaseDirectory);
            for (int depth = 0; dir != null && depth < 12; depth++, dir = dir.Parent)
            {
                var candidate = Path.Combine(dir.FullName, relative);
                if (File.Exists(candidate)) return candidate;
            }
            throw new FileNotFoundException("fixture not found: " + name);
        }
    }
}
