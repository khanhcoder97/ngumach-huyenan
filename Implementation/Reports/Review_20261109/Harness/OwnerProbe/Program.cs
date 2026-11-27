using Newtonsoft.Json.Linq;
using NguMach.Client.P1;
using NguMach.Client.Core.Composition;

var clientRoot = Environment.GetEnvironmentVariable("CLIENT_SOURCE_ROOT") ?? throw new Exception("Set CLIENT_SOURCE_ROOT to pinned OpenCode checkout");
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

sealed class Transport(Func<P1Request, CancellationToken, Task<P1HttpReply>> handler) : IP1Transport
{
    public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation) => handler(request, cancellation);
}
