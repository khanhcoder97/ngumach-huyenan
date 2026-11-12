using NguMach.Client.P1;
using Newtonsoft.Json.Linq;

const string Sid = "11111111111111111111111111111111";
const string World = "{\"mapId\":\"MAP_BEN_MUA\",\"serverTick\":1840,\"revision\":12,\"self\":{\"characterId\":\"CHR_TEST\",\"classId\":\"CLASS_MINH_KIEM\",\"x\":18,\"y\":0,\"hp\":50,\"maxHp\":100,\"mp\":50,\"maxMp\":50,\"swordIntent\":0},\"entities\":[]}";
const string Qoder = "D:/Project/NGUMACHHUYENAN-review-qod-20261108/Implementation/Contracts/P1/Examples/";
var actualUrl = Environment.GetEnvironmentVariable("PROBE_URL");
foreach (var operation in new[] { "talk", "portal" })
{
    foreach (bool refusal in new[] { false, true })
    {
        var t = new Transport((r, ct) =>
        {
            JObject envelope;
            int status;
            if (r.Path == "/p1/sessions")
            {
                envelope = new JObject { ["result"] = JObject.Parse(World) };
                status = 201;
            }
            else if (refusal)
            {
                envelope = new JObject { ["error"] = new JObject {
                    ["code"] = "out_of_range", ["messageKey"] = "P1.ERROR.OUT_OF_RANGE",
                    ["retryable"] = false, ["fieldErrors"] = new JArray("npcId"), ["correlationId"] = r.CorrelationId } };
                status = 422;
            }
            else
            {
                envelope = JObject.Parse(File.ReadAllText(Qoder + (operation == "talk" ? "TalkResponse.example.json" : "PortalResponse.example.json")));
                status = 200;
            }
            envelope["schemaVersion"] = 1;
            envelope["sessionId"] = Sid;
            envelope["requestId"] = r.CorrelationId;
            envelope["serverTimeUtc"] = "2026-11-08T00:00:00Z";
            return Task.FromResult(new P1HttpReply { StatusCode = status, CorrelationId = r.CorrelationId, Body = envelope.ToString() });
        });
        var client = new P1Client(actualUrl == null ? t : new ActualHttp(actualUrl));
        var connected = await client.ConnectAsync(CancellationToken.None);
        if (!connected.Success) throw new Exception("Probe connect failed: " + connected.Code);
        var answer = operation == "talk"
            ? await client.TalkAsync("NPC_TA_VAN_KHANH", "DLG_P00_05_CLUE", CancellationToken.None)
            : await client.PortalAsync("TP_BM_THANH_LAC", CancellationToken.None);
        Console.WriteLine($"{operation} input={(actualUrl != null ? "PAIRED_HEAD_HTTP" : refusal ? "DETERMINISTIC_422_OUT_OF_RANGE" : "CANONICAL_QODER_SUCCESS_EXAMPLE")} success={answer.Success} code={answer.Code} state={client.State} pending={client.HasPendingMutation}");
        if (actualUrl != null) break;
    }
}

sealed class Transport(Func<P1Request, CancellationToken, Task<P1HttpReply>> handler) : IP1Transport
{
    public Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation) => handler(request, cancellation);
}

sealed class ActualHttp(string baseUrl) : IP1Transport
{
    private readonly HttpClient http = new() { BaseAddress = new Uri(baseUrl) };
    public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken cancellation)
    {
        using var message = new HttpRequestMessage(new HttpMethod(request.Method), request.Path);
        message.Headers.Add("X-Correlation-ID", request.CorrelationId);
        if (request.SessionId != null) message.Headers.Add("X-Session-ID", request.SessionId);
        if (request.Body != null) message.Content = new StringContent(request.Body, System.Text.Encoding.UTF8, "application/json");
        using var response = await http.SendAsync(message, cancellation);
        var body = await response.Content.ReadAsStringAsync(cancellation);
        if (request.Path != "/p1/sessions") Console.WriteLine($"HTTP {request.Path} status={(int)response.StatusCode} body={body}");
        return new P1HttpReply { StatusCode = (int)response.StatusCode, CorrelationId = request.CorrelationId, Body = body };
    }
}
