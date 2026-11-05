// OPC-16 O1 — typed inventory v2 contract tests against Qoder 77bc3a6.
// Twelve closed slots, unsupported[] and underscore templateIds beside the
// frozen v1 five-slot route. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class InventoryV2Tests
    {
        private const string Session = "11111111111111111111111111111111";
        private const string Character = "CHR_TEST";
        private static readonly string[] SlotOrder =
        {
            "HAT", "CHEST", "LEGS", "WEAPON", "GLOVES", "BOOTS",
            "NECK", "RING_L", "RING_R", "PENDANT", "CLOAK", "SEAL"
        };

        private static string WorldJson =>
            "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1,\"revision\":0,\"self\":{\"characterId\":\"" + Character +
            "\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":100,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";

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
                       "\",\"sessionId\":\"" + Session + "\",\"result\":" + WorldJson + "}"
            };
        }

        private static P1HttpReply Envelope(P1Request r, int status, string resultJson)
        {
            return new P1HttpReply
            {
                StatusCode = status,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":2,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + Session + "\",\"serverTimeUtc\":\"2026-11-05T09:00:00Z\",\"result\":" +
                       resultJson + "}"
            };
        }

        private static P1HttpReply Error(P1Request r, int status, string code, string resultJson = null)
        {
            return new P1HttpReply
            {
                StatusCode = status,
                CorrelationId = r.CorrelationId,
                Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                       "\",\"sessionId\":\"" + Session + "\",\"error\":{\"code\":\"" + code +
                       "\",\"messageKey\":\"P1.ERROR." + code.ToUpperInvariant() +
                       "\",\"retryable\":true,\"fieldErrors\":[],\"correlationId\":\"" + r.CorrelationId +
                       "\"}" + (resultJson == null ? "" : ",\"result\":" + resultJson) + "}"
            };
        }

        private static string Item(string instanceId, string templateId, string location, string slotId,
            int stack = 1, int durability = 0, int version = 1)
        {
            return "{\"instanceId\":\"" + instanceId + "\",\"templateId\":\"" + templateId +
                   "\",\"stack\":" + stack + ",\"location\":\"" + location + "\",\"slotId\":" +
                   (slotId == null ? "null" : "\"" + slotId + "\"") + ",\"durability\":" + durability +
                   ",\"version\":" + version + "}";
        }

        private static string Snapshot(long revision, string hatInstance = null, bool withUnsupported = true,
            string bagTemplate = "POT-HP-01")
        {
            var slots = new StringBuilder();
            for (int i = 0; i < SlotOrder.Length; i++)
            {
                if (i > 0) slots.Append(',');
                slots.Append("{\"slotId\":\"").Append(SlotOrder[i]).Append("\",\"item\":");
                if (SlotOrder[i] == "HAT" && hatInstance != null)
                    slots.Append(Item(hatInstance, "EQ_MK_HAT_T1_R_COMMON", "EQUIPPED", "HAT"));
                else
                    slots.Append("null");
                slots.Append('}');
            }
            var unsupported = withUnsupported
                ? "[{\"instanceId\":\"ITM_TEST_UNMAPPED\",\"templateId\":\"EQ_OLD_SLOT_T1\",\"sourceSlot\":\"MAIN_HAND\",\"reason\":\"UNMAPPED_SLOT\"}]"
                : "[]";
            return "{\"schemaVersion\":2,\"slotSpec\":\"V2_SIDE_BY_SIDE_KEEP_V1_FIVE_SLOT_CONTRACT\"," +
                   "\"inventoryRevision\":" + revision + ",\"bagSlots\":100,\"slots\":[" + slots + "]," +
                   "\"bag\":[" + Item("ITM_TEST_POTION", bagTemplate, "BAG", null, 5) + "]," +
                   "\"unsupported\":" + unsupported + ",\"currencies\":[{\"currencyId\":\"COIN\",\"amount\":80}]}";
        }

        private static ScriptedTransport Connected(out P1Client client, string snapshotJson)
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/v2/" + Session)
                    return Task.FromResult(Envelope(r, 200, snapshotJson));
                if (r.Path == "/p1/inventory/v2/equip" || r.Path == "/p1/inventory/v2/unequip")
                    return Task.FromResult(Envelope(r, 200, snapshotJson));
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            client = new P1Client(transport);
            Assert.True(client.ConnectAsync(CancellationToken.None).GetAwaiter().GetResult().Success);
            return transport;
        }

        [Fact]
        public async Task ReadV2_AcceptsTwelveSlotsUnderscoreTemplateAndUnsupported()
        {
            var transport = Connected(out var client, Snapshot(4, "ITM_TEST_HAT"));
            var result = await client.ReadInventoryV2Async(CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.NotNull(client.InventoryV2);
            Assert.Equal(4, client.InventoryV2.inventoryRevision);
            Assert.Equal(12, client.InventoryV2.slots.Length);
            Assert.Equal("HAT", client.InventoryV2.slots[0].slotId);
            Assert.Equal("EQ_MK_HAT_T1_R_COMMON", client.InventoryV2.slots[0].item.templateId);
            Assert.Equal("ITM_TEST_POTION", client.InventoryV2.bag[0].instanceId);
            Assert.Single(client.InventoryV2.unsupported);
            Assert.Equal("UNMAPPED_SLOT", client.InventoryV2.unsupported[0].reason);
            Assert.Equal(80, client.InventoryV2.currencies[0].amount);
            Assert.Null(client.Inventory); // v1 snapshot untouched
            Assert.Equal("/p1/inventory/v2/" + Session, transport.Requests[1].Path);
        }

        [Fact]
        public async Task EquipV2_SendsSchema2WithoutClientSlotAndAppliesSnapshot()
        {
            var transport = new ScriptedTransport();
            bool equipped = false;
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/v2/" + Session)
                    return Task.FromResult(Envelope(r, 200, Snapshot(4)));
                if (r.Path == "/p1/inventory/v2/equip")
                {
                    equipped = true;
                    return Task.FromResult(Envelope(r, 200, Snapshot(5, "ITM_TEST_HAT")));
                }
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);
            Assert.True((await client.ReadInventoryV2Async(CancellationToken.None)).Success);

            var result = await client.EquipV2Async("ITM_TEST_HAT", 4, CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.True(equipped);
            Assert.Equal(5, client.InventoryV2.inventoryRevision);
            Assert.Equal("ITM_TEST_HAT", client.InventoryV2.slots[0].item.instanceId);
            var sent = transport.Requests[transport.Requests.Count - 1];
            var body = P1Wire.Decode<P1Envelope<P1EquipV2>>(sent.Body);
            Assert.Equal(2, body.schemaVersion);
            Assert.True(P1Wire.Hex32(body.requestId));
            Assert.True(P1Wire.Hex32(body.idempotencyKey));
            Assert.Equal("ITM_TEST_HAT", body.payload.itemInstanceId);
            Assert.Equal(4, body.payload.expectedRevision);
            Assert.DoesNotContain("slotId", sent.Body);
        }

        [Fact]
        public async Task UnequipV2_SendsSlotAndRevision()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/v2/" + Session)
                    return Task.FromResult(Envelope(r, 200, Snapshot(5, "ITM_TEST_HAT")));
                if (r.Path == "/p1/inventory/v2/unequip")
                    return Task.FromResult(Envelope(r, 200, Snapshot(6)));
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);
            Assert.True((await client.ReadInventoryV2Async(CancellationToken.None)).Success);

            var result = await client.UnequipV2Async("HAT", 5, CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.Equal(6, client.InventoryV2.inventoryRevision);
            Assert.Null(client.InventoryV2.slots[0].item);
            var sent = transport.Requests[transport.Requests.Count - 1];
            var body = P1Wire.Decode<P1Envelope<P1UnequipV2>>(sent.Body);
            Assert.Equal(2, body.schemaVersion);
            Assert.Equal("HAT", body.payload.slotId);
            Assert.Equal(5, body.payload.expectedRevision);
        }

        [Fact]
        public async Task RevisionConflict_AppliesAuthoritativeSnapshotAndClearsPending()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/v2/" + Session)
                    return Task.FromResult(Envelope(r, 200, Snapshot(4)));
                if (r.Path == "/p1/inventory/v2/equip")
                    return Task.FromResult(Error(r, 409, "revision_conflict", Snapshot(7, "ITM_TEST_HAT")));
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);
            Assert.True((await client.ReadInventoryV2Async(CancellationToken.None)).Success);

            var result = await client.EquipV2Async("ITM_TEST_HAT", 4, CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("revision_conflict", result.Code);
            Assert.False(client.HasPendingMutation);
            Assert.Equal(P1ConnectionState.Ready, client.State);
            Assert.Equal(7, client.InventoryV2.inventoryRevision);
            Assert.Equal("ITM_TEST_HAT", client.InventoryV2.slots[0].item.instanceId);
        }

        [Fact]
        public async Task AmbiguousEquip_RetryKeepsSameRequestAndIdempotencyKey()
        {
            var transport = new ScriptedTransport();
            bool fail = true;
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/v2/" + Session)
                    return Task.FromResult(Envelope(r, 200, Snapshot(4)));
                if (r.Path == "/p1/inventory/v2/equip")
                {
                    if (fail) return Task.FromResult(new P1HttpReply { StatusCode = 0, CorrelationId = r.CorrelationId });
                    return Task.FromResult(Envelope(r, 200, Snapshot(5, "ITM_TEST_HAT")));
                }
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);
            Assert.True((await client.ReadInventoryV2Async(CancellationToken.None)).Success);

            var first = await client.EquipV2Async("ITM_TEST_HAT", 4, CancellationToken.None);
            Assert.False(first.Success);
            Assert.Equal("mutation_outcome_unknown", first.Code);
            Assert.True(client.HasPendingMutation);

            var firstSent = transport.Requests[transport.Requests.Count - 1];
            var firstBody = P1Wire.Decode<P1Envelope<P1EquipV2>>(firstSent.Body);
            fail = false;
            var retry = await client.RetryPendingAsync(CancellationToken.None);

            Assert.True(retry.Success, retry.Code);
            var retrySent = transport.Requests[transport.Requests.Count - 1];
            var retryBody = P1Wire.Decode<P1Envelope<P1EquipV2>>(retrySent.Body);
            Assert.Equal(firstSent.Path, retrySent.Path);
            Assert.Equal(firstSent.CorrelationId, retrySent.CorrelationId);
            Assert.Equal(firstBody.requestId, retryBody.requestId);
            Assert.Equal(firstBody.idempotencyKey, retryBody.idempotencyKey);
            Assert.False(client.HasPendingMutation);
            Assert.Equal(5, client.InventoryV2.inventoryRevision);
        }

        [Theory]
        [InlineData("eleven_slots")]
        [InlineData("duplicate_slot")]
        [InlineData("bad_template")]
        [InlineData("thirteen_slots")]
        public async Task InvalidSnapshot_IsRejectedWithoutState(string mutation)
        {
            var snapshot = Snapshot(4);
            if (mutation == "eleven_slots") snapshot = snapshot.Replace(",{\"slotId\":\"SEAL\",\"item\":null}", "");
            if (mutation == "duplicate_slot") snapshot = snapshot.Replace("\"RING_R\"", "\"RING_L\"");
            if (mutation == "bad_template") snapshot = snapshot.Replace("POT-HP-01", "pot hp 01");
            if (mutation == "thirteen_slots") snapshot = snapshot.Replace(
                "{\"slotId\":\"SEAL\",\"item\":null}",
                "{\"slotId\":\"SEAL\",\"item\":null},{\"slotId\":\"EXTRA\",\"item\":null}");
            var transport = Connected(out var client, snapshot);

            var result = await client.ReadInventoryV2Async(CancellationToken.None);

            Assert.False(result.Success);
            Assert.Equal("invalid_response", result.Code);
            Assert.Null(client.InventoryV2);
            Assert.Equal(2, transport.Requests.Count); // session POST + v2 read
        }

        [Fact]
        public async Task FeatureDisabled404_IsUiReadableAndDoesNotLeavePending()
        {
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                return Task.FromResult(new P1HttpReply { StatusCode = 404, CorrelationId = r.CorrelationId, Body = "" });
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var read = await client.ReadInventoryV2Async(CancellationToken.None);
            var equip = await client.EquipV2Async("ITM_TEST_HAT", 1, CancellationToken.None);

            Assert.False(read.Success);
            Assert.Equal("feature_unavailable", read.Code);
            Assert.False(equip.Success);
            Assert.Equal("feature_unavailable", equip.Code);
            Assert.False(client.HasPendingMutation);
            Assert.Null(client.InventoryV2);
        }

        [Theory]
        [InlineData("ITM_TEST_HAT", 1, true)]
        [InlineData("ITM_", 1, false)]
        [InlineData("itm_test_hat", 1, false)]
        [InlineData("ITM_TEST_HAT", 0, false)]
        public async Task EquipV2_InputValidation(string instanceId, long revision, bool accepted)
        {
            var transport = Connected(out var client, Snapshot(4));
            var result = await client.EquipV2Async(instanceId, revision, CancellationToken.None);
            Assert.Equal(accepted, result.Success);
            if (!accepted) Assert.Equal("invalid_input", result.Code);
        }

        [Fact]
        public async Task V1InventoryRouteAndModel_Unchanged()
        {
            var v1 = "{\"inventoryRevision\":3,\"items\":[{\"instanceId\":\"ITM_V1\",\"templateId\":\"POT-HP-01\"," +
                     "\"location\":\"BAG\",\"slot\":null,\"stack\":1,\"durability\":0,\"version\":1}]," +
                     "\"currencies\":[{\"currencyId\":\"COIN\",\"amount\":1}]}";
            var transport = new ScriptedTransport();
            transport.Handler = (r, ct) =>
            {
                if (r.Path == "/p1/sessions") return Task.FromResult(SessionReply(r));
                if (r.Path == "/p1/inventory/" + Session)
                    return Task.FromResult(new P1HttpReply
                    {
                        StatusCode = 200,
                        CorrelationId = r.CorrelationId,
                        Body = "{\"schemaVersion\":1,\"requestId\":\"" + r.CorrelationId +
                               "\",\"sessionId\":\"" + Session + "\",\"result\":" + v1 + "}"
                    });
                return Task.FromResult(Error(r, 404, "not_found"));
            };
            var client = new P1Client(transport);
            Assert.True((await client.ConnectAsync(CancellationToken.None)).Success);

            var result = await client.ReadInventoryAsync(CancellationToken.None);

            Assert.True(result.Success, result.Code);
            Assert.Equal(3, client.Inventory.inventoryRevision);
            Assert.Null(client.InventoryV2);
            Assert.Equal("/p1/inventory/" + Session, transport.Requests[1].Path);
        }
    }
}
