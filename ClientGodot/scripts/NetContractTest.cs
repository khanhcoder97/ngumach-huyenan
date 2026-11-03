using Godot;
using System;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

/// <summary>
/// Live contract test: this Godot .NET client talks to Qoder's REAL P1
/// server (branch qoder/p1-server-slice, ASP.NET Core, unmodified) using
/// only System.Net.Http + System.Text.Json — the same .NET stack the
/// server and the Unity client both use. Nothing Unity-specific exists
/// anywhere in the contract: envelope, schemas and examples are plain
/// JSON, and Production_Technical_Contracts_vi.md declares the baseline
/// transport-independent (HTTP/JSON + WebSocket).
///
/// Flow checked against the live server on http://127.0.0.1:5000:
///   GET  /health            -> 200, status ok, correlation id echoed
///   POST /p1/sessions       -> 201, spawn (18, 0) on MAP_BEN_MUA
///   POST /p1/move           -> 200, authoritative x increases, revision +1
///   POST /p1/move (replay)  -> 409, error code stale_sequence
///   GET  /p1/world/{id}     -> snapshot matches the move result
/// Run: godot --headless --path . NetTest.tscn -- --nettest (server up).
/// </summary>
public partial class NetContractTest : Node
{
    private const string BaseUrl = "http://127.0.0.1:5000";
    private const string CharacterId = "CHR_MINH_KIEM_01";
    private int _failures;

    public override void _Ready()
    {
        if (OS.GetCmdlineUserArgs().Contains("--nettest"))
            _ = Run();
    }

    private void Check(string name, bool ok, string detail = "")
    {
        GD.Print($"NETTEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _failures++;
    }

    private static string Hex32() => Guid.NewGuid().ToString("N");
    private static string NowUtc() => DateTime.UtcNow.ToString("yyyy-MM-dd'T'HH:mm:ss'Z'");

    private async Task Run()
    {
        // Direct connect, no proxy: on this VM an egress proxy is injected
        // via env vars (http_proxy/ALL_PROXY) and .NET's default handler
        // path ends up refused by it even for 127.0.0.1, while a plain
        // socket connects fine (measured). A game client should reach the
        // game server directly anyway, so the handler pins an explicit
        // IPv4 ConnectCallback — portable, and identical on player PCs.
        var handler = new SocketsHttpHandler
        {
            UseProxy = false,
            ConnectCallback = async (ctx, ct) =>
            {
                var addresses = await System.Net.Dns.GetHostAddressesAsync(ctx.DnsEndPoint.Host, ct);
                System.Net.IPAddress chosen = addresses[0];
                foreach (var a in addresses)
                    if (a.AddressFamily == System.Net.Sockets.AddressFamily.InterNetwork) { chosen = a; break; }
                var socket = new System.Net.Sockets.Socket(chosen.AddressFamily,
                    System.Net.Sockets.SocketType.Stream, System.Net.Sockets.ProtocolType.Tcp);
                await socket.ConnectAsync(new System.Net.IPEndPoint(chosen, ctx.DnsEndPoint.Port), ct);
                return new System.Net.Sockets.NetworkStream(socket, ownsSocket: true);
            }
        };
        using var http = new System.Net.Http.HttpClient(handler)
        { Timeout = TimeSpan.FromSeconds(5) };
        try
        {
            // --- /health with correlation id (TitleBootstrap contract) ---
            string correlation = Hex32();
            var healthReq = new HttpRequestMessage(HttpMethod.Get, $"{BaseUrl}/health");
            healthReq.Headers.Add("X-Correlation-ID", correlation);
            var healthRes = await http.SendAsync(healthReq);
            string healthBody = await healthRes.Content.ReadAsStringAsync();
            using var healthJson = JsonDocument.Parse(healthBody);
            Check("health_200_ok", healthRes.IsSuccessStatusCode &&
                healthJson.RootElement.GetProperty("status").GetString() == "ok",
                $"status={(int)healthRes.StatusCode}");
            Check("health_correlation_echo",
                healthJson.RootElement.GetProperty("correlationId").GetString() == correlation,
                $"sent={correlation[..8]}… got={healthJson.RootElement.GetProperty("correlationId").GetString()?[..8]}…");

            // --- POST /p1/sessions ---
            var sessionBody = JsonSerializer.Serialize(new
            {
                characterId = CharacterId,
                classId = "CLASS_MINH_KIEM"
            });
            var sessionRes = await http.PostAsync($"{BaseUrl}/p1/sessions",
                new StringContent(sessionBody, Encoding.UTF8, "application/json"));
            string sessionText = await sessionRes.Content.ReadAsStringAsync();
            using var sessionJson = JsonDocument.Parse(sessionText);
            var sRoot = sessionJson.RootElement;
            Check("session_201", (int)sessionRes.StatusCode == 201, $"status={(int)sessionRes.StatusCode}");
            string sessionId = sRoot.GetProperty("sessionId").GetString();
            var self0 = sRoot.GetProperty("result").GetProperty("self");
            double spawnX = self0.GetProperty("x").GetDouble();
            double spawnY = self0.GetProperty("y").GetDouble();
            long rev0 = sRoot.GetProperty("revision").GetInt64();
            Check("session_spawn_18_0", spawnX == 18 && spawnY == 0,
                $"spawn=({spawnX},{spawnY}) map={sRoot.GetProperty("result").GetProperty("mapId").GetString()}");

            // --- POST /p1/move (wait so the server step = 6 WU/s * 0.25 s) ---
            await Task.Delay(300);
            string moveBody = BuildMove(seq: 1, moveX: 1, moveY: 0);
            var moveRes = await SendMove(http, sessionId, moveBody);
            string moveText = await moveRes.Content.ReadAsStringAsync();
            using var moveJson = JsonDocument.Parse(moveText);
            var mRoot = moveJson.RootElement;
            Check("move_200", moveRes.IsSuccessStatusCode, $"status={(int)moveRes.StatusCode} body={moveText[..Math.Min(120, moveText.Length)]}");
            double x1 = mRoot.GetProperty("result").GetProperty("self").GetProperty("x").GetDouble();
            long rev1 = mRoot.GetProperty("revision").GetInt64();
            Check("move_authoritative_east", x1 > spawnX && x1 <= spawnX + 1.5, $"x {spawnX} -> {x1}");
            Check("move_revision_increment", rev1 == rev0 + 1, $"rev {rev0} -> {rev1}");

            // --- replay the same sequence -> 409 stale_sequence ---
            var replayRes = await SendMove(http, sessionId, BuildMove(seq: 1, moveX: 1, moveY: 0));
            string replayText = await replayRes.Content.ReadAsStringAsync();
            using var replayJson = JsonDocument.Parse(replayText);
            string errCode = replayJson.RootElement.GetProperty("error").GetProperty("code").GetString();
            Check("replay_409_stale_sequence",
                (int)replayRes.StatusCode == 409 && errCode == "stale_sequence",
                $"status={(int)replayRes.StatusCode} code={errCode}");

            // --- GET /p1/world/{sessionId} matches ---
            var worldRes = await http.GetAsync($"{BaseUrl}/p1/world/{sessionId}");
            string worldText = await worldRes.Content.ReadAsStringAsync();
            using var worldJson = JsonDocument.Parse(worldText);
            var wSelf = worldJson.RootElement.GetProperty("result").GetProperty("self");
            Check("world_snapshot_matches",
                worldRes.IsSuccessStatusCode &&
                Math.Abs(wSelf.GetProperty("x").GetDouble() - x1) < 1e-9 &&
                worldJson.RootElement.GetProperty("result").GetProperty("serverTick").GetInt64() >= 0,
                $"world x={wSelf.GetProperty("x").GetDouble()} tick={worldJson.RootElement.GetProperty("result").GetProperty("serverTick").GetInt64()}");
        }
        catch (Exception ex)
        {
            Check("exception", false, ex.GetType().Name + ": " + ex.Message);
        }

        GD.Print(_failures == 0 ? "NETTEST RESULT: PASS" : $"NETTEST RESULT: FAIL ({_failures})");
        GetTree().Quit(_failures == 0 ? 0 : 1);
    }

    private static string BuildMove(int seq, double moveX, double moveY) =>
        JsonSerializer.Serialize(new
        {
            schemaVersion = 1,
            requestId = Hex32(),
            idempotencyKey = Hex32(),
            sentAtUtc = NowUtc(),
            characterId = CharacterId,
            payload = new
            {
                inputSequence = seq,
                moveX,
                moveY,
                clientTimeUtc = NowUtc()
            }
        });

    private static async Task<HttpResponseMessage> SendMove(System.Net.Http.HttpClient http, string sessionId, string body)
    {
        var req = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/p1/move")
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json")
        };
        req.Headers.Add("X-Session-ID", sessionId);
        return await http.SendAsync(req);
    }
}
