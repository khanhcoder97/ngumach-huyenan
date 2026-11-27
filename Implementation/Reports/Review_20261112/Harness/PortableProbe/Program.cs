using Newtonsoft.Json.Linq;
using NguMach.Client.P1;
using NguMach.Client.Core.Composition;
using NguMach.Client.Presentation;

var clientRoot = Environment.GetEnvironmentVariable("CLIENT_SOURCE_ROOT") ?? throw new Exception("Set CLIENT_SOURCE_ROOT");
const string Sid = "11111111111111111111111111111111";
const string World = "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1840,\"revision\":12,\"self\":{\"characterId\":\"CHR_TEST\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":50,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";
var fixture = JObject.Parse(File.ReadAllText(Path.Combine(clientRoot, "Shared/ClientCore.Tests/Fixtures/encounter_snapshot_v1_reference_20261104.json")));
var snapshot = (JObject)(fixture["result"] ?? fixture);
snapshot["registeredCharacterIds"] = new JArray("CHR_FOREIGN");

foreach (bool explicitIdentity in new[] { false, true })
{
    var transport = new Transport((request, ct) =>
    {
        var result = request.Path == "/p1/sessions" ? JObject.Parse(World) : snapshot.DeepClone();
        var body = new JObject { ["schemaVersion"] = 1, ["requestId"] = request.CorrelationId,
            ["sessionId"] = Sid, ["serverTimeUtc"] = "2026-11-09T00:00:00Z", ["result"] = result };
        return Task.FromResult(new P1HttpReply { StatusCode = request.Path == "/p1/sessions" ? 201 : 200,
            CorrelationId = request.CorrelationId, Body = body.ToString() });
    });
    using var session = new ClientSession(transport, characterId: explicitIdentity ? "CHR_TEST" : null);
    var connected = await session.ConnectAsync();
    if (!connected.Success) throw new Exception("Probe connect failed: " + connected.Code);
    int deliveries = 0;
    session.EncounterUpdated += _ => deliveries++;
    var answer = await session.ReadCurrentEncounterAsync();
    Console.WriteLine($"explicitRequestedIdentity={explicitIdentity} actualActor={session.Client.World.self.characterId} suppliedOwner=CHR_FOREIGN accepted={answer.Success} outcome={answer.Outcome} deliveries={deliveries}");
}

var media = new MediaPlaybackPresenter();
var outside = new MediaMetadata("CIN_TEST", new[] { "../../private.mp4" }, false, null);
Console.WriteLine($"media traversalInAllowedList accepted={media.Load(outside, 10, true, "../../private.mp4")} phase={media.View.Phase}");
var audio = new MediaMetadata("CIN_TEST", new[] { "ClientGodot/assets/audio/mix/p0_v3/CIN_001_mix_draft_v3.wav" }, true, null);
Console.WriteLine($"media externalMixUnderEmbeddedPolicy accepted={media.Load(audio, 10, true, audio.AllowedPaths[0])} phase={media.View.Phase}");
var adapter = new FakeUiAdapter {
    Self = new P1Self { x = 82, y = 0 },
    WorldV2 = new P1WorldV2 { mapId = "MAP_THANH_LAC", serverTick = 500, entities = Array.Empty<P1EntityV2>() },
    World = new P1World { mapId = "MAP_BEN_MUA", serverTick = 10, entities = new[] { new P1Entity { entityId = "ENT_NPC_LYAN_STATIC", kind = "NPC", x = 90, y = 0 } } }
};
var escort = new EscortPresenter(adapter).Refresh();
Console.WriteLine($"escort v2AbsentButV1OldNpc inAudience={escort.InAudience} entity={escort.EntityId} map={escort.MapId} tick={escort.ServerTick} x={escort.X} onRoad={escort.IsOnRoad}");

sealed class Transport(Func<P1Request, CancellationToken, Task<P1HttpReply>> handler) : IP1Transport
{
    public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation) => handler(request, cancellation);
}

        sealed class FakeUiAdapter : IP1UIAdapter
        {
            public UIConnectionState ConnectionState { get; set; } = UIConnectionState.Ready;
            public bool HasPendingMutation { get; set; }
            public string LastErrorCode { get; set; }
            public string LastCorrelationId { get; set; }
            public P1Self Self { get; set; }
            public P1World World { get; set; }
            public P1WorldV2 WorldV2 { get; set; }
            public P1Quest[] Quests { get; set; } = new P1Quest[0];
            public P1Inventory Inventory { get; set; }
            public Task<P1Result> ReadQuestsAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> ReadInventoryAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> ReadWorldAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> AcceptQuestAsync(string questId, string npcId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> InteractAsync(string targetId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> TurnInQuestAsync(string questId, string npcId, CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
            public Task<P1Result> RetryPendingAsync(CancellationToken ct) { return Task.FromResult(P1Result.Ok()); }
        }
