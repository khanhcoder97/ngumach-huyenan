using System;
using System.Net;
using System.Net.Http;
using System.Net.Sockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

/// <summary>
/// Minimal client for Qoder's P1 server contract (branch
/// qoder/p1-server-slice), written against the JSON schemas in
/// Implementation/Contracts/P1. Plain System.Net.Http + System.Text.Json —
/// the same stack the server uses; nothing engine-specific.
///
/// Endpoints:
///   GET  /health                  -> {status, service, correlationId}
///   POST /p1/sessions             -> 201 + envelope{result: WorldSnapshot}
///   POST /p1/move                 -> envelope{result: WorldSnapshot} (header X-Session-ID)
///   GET  /p1/world/{sessionId}    -> envelope{result: WorldSnapshot}
/// Errors arrive as envelope{error:{code, messageKey, retryable,
/// fieldErrors[], correlationId}} with HTTP 400/404/409/422.
///
/// Direct-connect handler: on Muse's VM the injected egress-proxy env
/// breaks .NET's default connect path even for 127.0.0.1 (measured in
/// Bổ sung 3 of the evaluation); a game client should connect directly
/// anyway, so the handler pins an explicit ConnectCallback + UseProxy=false.
/// </summary>
public sealed class GameServerClient : IDisposable
{
    public sealed record Snapshot(
        string MapId, long ServerTick, long Revision,
        string CharacterId, string ClassId,
        double X, double Y, int Hp, int MaxHp, int Mp, int MaxMp);

    public sealed record MoveOutcome(bool Ok, int StatusCode, string ErrorCode, Snapshot Snapshot, double RoundTripMs);

    private readonly HttpClient _http;
    private readonly string _characterId;
    private int _sequence;

    public string BaseUrl { get; }
    public string SessionId { get; private set; }
    public Snapshot LastSnapshot { get; private set; }

    public GameServerClient(string baseUrl, string characterId)
    {
        BaseUrl = baseUrl;
        _characterId = characterId;
        var handler = new SocketsHttpHandler
        {
            UseProxy = false,
            ConnectCallback = async (ctx, ct) =>
            {
                var addresses = await Dns.GetHostAddressesAsync(ctx.DnsEndPoint.Host, ct);
                IPAddress chosen = addresses[0];
                foreach (var a in addresses)
                    if (a.AddressFamily == AddressFamily.InterNetwork) { chosen = a; break; }
                var socket = new Socket(chosen.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
                await socket.ConnectAsync(new IPEndPoint(chosen, ctx.DnsEndPoint.Port), ct);
                return new NetworkStream(socket, ownsSocket: true);
            }
        };
        _http = new HttpClient(handler) { Timeout = TimeSpan.FromSeconds(5) };
    }

    private static string Hex32() => Guid.NewGuid().ToString("N");
    private static string NowUtc() => DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'");

    public async Task<bool> CheckHealthAsync()
    {
        string correlation = Hex32();
        using var req = new HttpRequestMessage(HttpMethod.Get, $"{BaseUrl}/health");
        req.Headers.Add("X-Correlation-ID", correlation);
        using var res = await _http.SendAsync(req);
        if (!res.IsSuccessStatusCode) return false;
        using var doc = JsonDocument.Parse(await res.Content.ReadAsStringAsync());
        return doc.RootElement.GetProperty("status").GetString() == "ok"
            && doc.RootElement.GetProperty("correlationId").GetString() == correlation;
    }

    public async Task<Snapshot> CreateSessionAsync(string classId)
    {
        string body = JsonSerializer.Serialize(new { characterId = _characterId, classId });
        using var res = await _http.PostAsync($"{BaseUrl}/p1/sessions",
            new StringContent(body, Encoding.UTF8, "application/json"));
        string text = await res.Content.ReadAsStringAsync();
        if ((int)res.StatusCode != 201)
            throw new InvalidOperationException($"CreateSession failed: {(int)res.StatusCode} {text}");
        using var doc = JsonDocument.Parse(text);
        SessionId = doc.RootElement.GetProperty("sessionId").GetString();
        LastSnapshot = ParseSnapshot(doc.RootElement.GetProperty("result"));
        return LastSnapshot;
    }

    /// <summary>
    /// Send one move intent. moveX/moveY are in WORLD axes (Y up):
    /// callers convert from Godot input by negating Y.
    /// </summary>
    public async Task<MoveOutcome> MoveAsync(double moveX, double moveY)
    {
        int seq = Interlocked.Increment(ref _sequence);
        string body = JsonSerializer.Serialize(new
        {
            schemaVersion = 1,
            requestId = Hex32(),
            idempotencyKey = Hex32(),
            sentAtUtc = NowUtc(),
            characterId = _characterId,
            payload = new
            {
                inputSequence = seq,
                moveX,
                moveY,
                clientTimeUtc = NowUtc()
            }
        });
        using var req = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/p1/move")
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json")
        };
        req.Headers.Add("X-Session-ID", SessionId);
        var sw = System.Diagnostics.Stopwatch.StartNew();
        using var res = await _http.SendAsync(req);
        sw.Stop();
        string text = await res.Content.ReadAsStringAsync();
        using var doc = JsonDocument.Parse(text);
        if (res.IsSuccessStatusCode)
        {
            LastSnapshot = ParseSnapshot(doc.RootElement.GetProperty("result"));
            return new MoveOutcome(true, (int)res.StatusCode, null, LastSnapshot, sw.Elapsed.TotalMilliseconds);
        }
        string code = doc.RootElement.TryGetProperty("error", out var err)
            ? err.GetProperty("code").GetString() : "unknown";
        return new MoveOutcome(false, (int)res.StatusCode, code, null, sw.Elapsed.TotalMilliseconds);
    }

    public async Task<Snapshot> GetWorldAsync()
    {
        using var res = await _http.GetAsync($"{BaseUrl}/p1/world/{SessionId}");
        string text = await res.Content.ReadAsStringAsync();
        if (!res.IsSuccessStatusCode)
            throw new InvalidOperationException($"GetWorld failed: {(int)res.StatusCode} {text}");
        using var doc = JsonDocument.Parse(text);
        LastSnapshot = ParseSnapshot(doc.RootElement.GetProperty("result"));
        return LastSnapshot;
    }

    private static Snapshot ParseSnapshot(JsonElement result)
    {
        var self = result.GetProperty("self");
        return new Snapshot(
            result.GetProperty("mapId").GetString(),
            result.GetProperty("serverTick").GetInt64(),
            result.GetProperty("revision").GetInt64(),
            self.GetProperty("characterId").GetString(),
            self.GetProperty("classId").GetString(),
            self.GetProperty("x").GetDouble(),
            self.GetProperty("y").GetDouble(),
            self.GetProperty("hp").GetInt32(),
            self.GetProperty("maxHp").GetInt32(),
            self.GetProperty("mp").GetInt32(),
            self.GetProperty("maxMp").GetInt32());
    }

    public void Dispose() => _http.Dispose();
}
