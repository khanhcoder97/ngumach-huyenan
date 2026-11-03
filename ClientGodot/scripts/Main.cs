using Godot;
using System;
using System.Linq;

/// <summary>
/// Prototype main scene. Ports two Unity pieces:
///  - PixelArtCameraBootstrap: 640x360 / 20 PPU / pixel snapping. In Godot
///    this is project settings (canvas_items stretch + nearest filter) plus
///    a Camera2D child of the player — no per-camera component needed.
///  - TitleBootstrap health poll: GET http://127.0.0.1:5000/health every
///    10 s, 3 s timeout, status label. UnityWebRequest coroutine becomes
///    an HttpRequest node + Timer.
/// Also hosts the headless self-test (run with: godot --headless -- --selftest).
/// </summary>
public partial class Main : Node2D
{
    private const string HealthUrl = "http://127.0.0.1:5000/health";

    private PlayerController2D _player;
    private DirectionalAnimator2D _animator;
    private Label _statusLabel;
    private HttpRequest _http;
    private bool _selfTest;

    public override void _Ready()
    {
        _player = GetNode<PlayerController2D>("Player");
        _animator = GetNode<DirectionalAnimator2D>("Player/DirectionalAnimator2D");
        _statusLabel = GetNode<Label>("HUD/StatusLabel");
        _http = GetNode<HttpRequest>("HealthRequest");
        _http.Timeout = 3;
        _http.RequestCompleted += OnHealthCompleted;

        _selfTest = OS.GetCmdlineUserArgs().Contains("--selftest");
        if (_selfTest)
        {
            _ = RunSelfTest();
        }
        else if (OS.GetCmdlineUserArgs().Contains("--screenshot"))
        {
            _ = RunScreenshot();
        }
        else
        {
            PollHealth();
            var timer = new Timer { WaitTime = 10, Autostart = true };
            timer.Timeout += PollHealth;
            AddChild(timer);
        }
    }

    private void PollHealth()
    {
        if (_http.GetHttpClientStatus() == HttpClient.Status.Disconnected)
            _http.Request(HealthUrl, new[] { $"X-Correlation-ID: {Guid.NewGuid():N}" });
    }

    private void OnHealthCompleted(long result, long code, string[] headers, byte[] body)
    {
        bool online = result == (long)HttpRequest.Result.Success && code >= 200 && code < 300;
        _statusLabel.Text = online ? "Máy chủ: Trực tuyến" : "Máy chủ: Ngoại tuyến";
    }

    private async System.Threading.Tasks.Task RunScreenshot()
    {
        // Walk SE briefly so the capture shows a mid-stride frame on the map.
        _player.SetMoveInput(new Vector2(1, 1), running: false);
        await WaitPhysicsFrames(30);
        _player.SetMoveInput(Vector2.Zero, running: false);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_prototype.png");
        image.SavePng(path);
        GD.Print($"SCREENSHOT SAVED: {path} size={image.GetSize()}");
        GetTree().Quit(0);
    }

    // ---------------- Headless self-test ----------------

    private int _failures;

    private void Check(string name, bool ok, string detail = "")
    {
        GD.Print($"SELFTEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _failures++;
    }

    private async System.Threading.Tasks.Task WaitPhysicsFrames(int n)
    {
        for (int i = 0; i < n; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private async System.Threading.Tasks.Task RunSelfTest()
    {
        await WaitPhysicsFrames(10); // let _Ready of children + first frames run

        // 1. Animation library built from sheets: 16 actions x 8 dirs = 128.
        Check("anim_count_128", _animator.SpriteFramesAnimationCount == 128,
            $"count={_animator.SpriteFramesAnimationCount}");

        // 2. Direction mapping: all 8 facings land on the Unity sheet rows.
        (Vector2, int)[] cases =
        {
            (Vector2.Up, 0), (new Vector2(1, -1), 1), (Vector2.Right, 2), (new Vector2(1, 1), 3),
            (Vector2.Down, 4), (new Vector2(-1, 1), 5), (Vector2.Left, 6), (new Vector2(-1, -1), 7),
        };
        bool mapOk = cases.All(c => DirectionalAnimator2D.DirectionIndex(c.Item1.Normalized()) == c.Item2);
        Check("direction_index_8way", mapOk);

        // 3. Walk SE for ~1 s at 64 px/s: moves (+45,+45) diag, plays walk_SE.
        Vector2 start = _player.GlobalPosition;
        _player.SetMoveInput(new Vector2(1, 1), running: false);
        await WaitPhysicsFrames(60);
        _player.SetMoveInput(Vector2.Zero, running: false);
        Vector2 moved = _player.GlobalPosition - start;
        Check("walk_se_moves", moved.X > 35 && moved.Y > 35, $"moved={moved}");
        Check("walk_se_anim", _animator.CurrentAnimation == "walk_SE", _animator.CurrentAnimation);
        await WaitPhysicsFrames(20);

        // 4. Idle keeps facing: idle_SE.
        Check("idle_keeps_facing_se", _animator.CurrentAnimation == "idle_SE", _animator.CurrentAnimation);

        // 5. Run N for ~0.5 s at 102.4 px/s: moves up ~51 px, plays run_N (real
        // run clips since the full library port; was walk_N at 1.6x speed).
        start = _player.GlobalPosition;
        _player.SetMoveInput(Vector2.Up, running: true);
        await WaitPhysicsFrames(30);
        bool running = _player.IsRunning;
        string animDuring = _animator.CurrentAnimation;
        _player.SetMoveInput(Vector2.Zero, running: false);
        moved = _player.GlobalPosition - start;
        Check("run_n_moves_fast", moved.Y < -40 && Math.Abs(moved.X) < 2, $"moved={moved}");
        Check("run_flag_and_anim", running && animDuring == "run_N", $"running={running} anim={animDuring}");

        GD.Print(_failures == 0 ? "SELFTEST RESULT: PASS" : $"SELFTEST RESULT: FAIL ({_failures})");
        GetTree().Quit(_failures == 0 ? 0 : 1);
    }
}
