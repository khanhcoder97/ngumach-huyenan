using Godot;
using System;
using System.Linq;
using System.Threading.Tasks;

/// <summary>
/// Online scene: the full Bến Mưa tilemap (visual/collision reference) +
/// a player whose position is OWNED BY THE REAL P1 SERVER. The client
/// sends MoveIntent at 5 Hz while a direction is held (world axes: Y up,
/// so Godot input Y is negated) and renders the player by tracking the
/// authoritative snapshot position — no local movement simulation.
///
/// Collision: Qoder's P1 slice validates movement against map BOUNDS
/// only (clamp X 0..360, Y -12..72) — it has no tile collision yet. Per
/// the owner's order, this client therefore CLAMPS ITS OWN INTENTS
/// against the tiledata blocked layer (the same data the offline
/// FullMapTest proves): before an intent is sent, the maximal server
/// step (1.5 WU) is predicted with the player's feet box; if the full
/// direction would enter a blocked cell, the client tries axis-separated
/// slides (X-only, then Y-only), and if all are blocked it sends nothing.
/// Be clear about what this is: a client-side gate for honest play and
/// feel — a modified client could still walk on water, because the
/// server does not check. The real fix belongs server-side; the blocked
/// layer is ready for Qoder to consume, and this client will not need
/// changes when that lands (it already only trusts snapshots).
///
/// Modes:
///   (none)        : interactive, WASD/arrows against the live server.
///   --onlinetest  : scripted run vs the live server (spawn placement,
///                   east walk distance = server integration, north walk
///                   proves the Y-flip, render tracks snapshot, revision
///                   bookkeeping, zero rejected intents).
///   --onlineshot  : connect, walk E then N, save screenshot_online.png.
/// Server must be running at http://127.0.0.1:5000 (see server-test/).
/// </summary>
public partial class OnlineMain : Node2D
{
    private const string BaseUrl = "http://127.0.0.1:5000";
    private const double IntentIntervalMs = 200;

    private PlayerController2D _player;
    private Label _label;
    private Hud _hud;
    private DirectionalAnimator2D _animator;
    private ClassSelect _classSelect;
    /// <summary>Asset class id chosen on the select screen (or by a test).</summary>
    public string SelectedClass { get; private set; }
    /// <summary>Character id the current server client was built with.</summary>
    public string ClientCharacterId { get; private set; }
    private int _comboStep;
    private ulong _lastAttackMs;
    private bool _attackKeyWasDown;
    private BenMuaTilemapBuilder _builder;
    private GameServerClient _client;
    private bool _connected;
    private Vector2 _serverTargetPx;
    private Vector2 _input = Vector2.Zero;
    private bool _testMode;
    private double _lastSendMs = -1000;
    private Task _sendChain = Task.CompletedTask;
    private int _accepted;
    private int _rejected;
    private string _lastError = "";
    private double _lastRttMs;
    private int _clamped;
    private int _serverPosViolations;

    public override void _Ready()
    {
        _player = GetNode<PlayerController2D>("Player");
        _label = GetNode<Label>("HUD/StatusLabel");
        _hud = GetNodeOrNull<Hud>("GameHud");
        _animator = GetNode<DirectionalAnimator2D>("Player/DirectionalAnimator2D");
        if (_hud != null)
        {
            _hud.AttackPressed += OnAttackPressed;
            _hud.SkillActivated += OnSkillActivated;
        }
        _builder = GetNode<BenMuaTilemapBuilder>("TilemapBuilder");
        _classSelect = GetNode<ClassSelect>("ClassSelect");
        _classSelect.ClassChosen += id => _ = StartGame(id);
        _player.ExternalControl = true;
        var args = OS.GetCmdlineUserArgs();
        if (args.Contains("--onlinetest")) { _testMode = true; _ = RunOnlineTest(); }
        else if (args.Contains("--onlineshot")) { _testMode = true; _ = RunOnlineShot(); }
        else if (args.Contains("--selecttest")) { _testMode = true; _ = RunSelectTest(); }
        else if (args.Contains("--selectshot")) { _testMode = true; _ = RunSelectShot(); }
        else _classSelect.ShowMenu(); // interactive: pick a class first
    }

    /// <summary>Applies a class choice end-to-end: animator library,
    /// HUD portrait, then the server session for that class.</summary>
    private async System.Threading.Tasks.Task StartGame(string assetClassId)
    {
        SelectedClass = assetClassId;
        _classSelect.HideMenu();
        _animator.SetClass(assetClassId);
        _hud?.SetPortraitClass(assetClassId);
        await ConnectAsync(assetClassId);
    }

    // ---------------- combat input (client-side presentation only) -----
    // The P1 server has no combat yet: these trigger the character's
    // action clips locally (attack combo Attack1->2->3 within 1.2 s
    // windows; HUD skill buttons 1-3 play Skill1-3; buttons 4-6 have no
    // Minh Kiem skill clips — only their HUD cooldown runs).
    private void OnAttackPressed()
    {
        ulong now = Time.GetTicksMsec();
        if (now - _lastAttackMs > 1200) _comboStep = 0;
        _animator?.PlayAction(3 + _comboStep);
        _comboStep = (_comboStep + 1) % 3;
        _lastAttackMs = now;
    }

    private void OnSkillActivated(int index)
    {
        if (index < 3) _animator?.PlayAction(6 + index);
    }

    /// <summary>World WU (Y up, map Y range -12..72) -> Godot pixels.</summary>
    private static Vector2 WorldToPixel(double x, double y) =>
        new((float)(x * 20.0), (float)((36.0 - y) * 20.0));

    // ---------------- client-side tile clamp (blocked layer) -----------

    /// <summary>
    /// Would the player's feet box (24x12 px at (0,-6), the same box the
    /// offline controller collides with) overlap any blocked cell if the
    /// player stood at this world position? Out-of-grid counts as blocked.
    /// </summary>
    private bool FeetBoxBlocked(Vector2 worldPos)
    {
        Vector2 px = WorldToPixel(worldPos.X, worldPos.Y);
        float cx = px.X, cy = px.Y - 6f;
        int c0 = Mathf.FloorToInt((cx - 12f) / 16f), c1 = Mathf.FloorToInt((cx + 11.9f) / 16f);
        int r0 = Mathf.FloorToInt((cy - 6f) / 16f), r1 = Mathf.FloorToInt((cy + 5.9f) / 16f);
        for (int r = r0; r <= r1; r++)
            for (int c = c0; c <= c1; c++)
                if (c < 0 || r < 0 || c >= _builder.Cols || r >= _builder.Rows || _builder.IsBlockedCell(c, r))
                    return true;
        return false;
    }

    /// <summary>
    /// Gate one intent direction (world axes) from a known server
    /// position. The server's step is at most 1.5 WU (6 WU/s x 0.25 s
    /// clamp), so predicting the FULL 1.5 WU step is conservative: if
    /// that fits, whatever smaller step the server actually takes fits
    /// too. Tries full direction, then X-only, then Y-only (wall slide).
    /// Returns Vector2.Zero when every candidate would enter blocked
    /// cells — the caller then sends nothing.
    /// </summary>
    private Vector2 ClampDirection(Vector2 fromWorld, Vector2 dirWorld)
    {
        if (dirWorld.LengthSquared() < 0.001f) return Vector2.Zero;
        var full = dirWorld.Normalized();
        var candidates = new[]
        {
            full,
            new Vector2(full.X, 0),
            new Vector2(0, full.Y)
        };
        Vector2 seen = new(float.NaN, float.NaN);
        foreach (var cand in candidates)
        {
            if (cand.LengthSquared() < 0.001f || cand == seen) continue;
            seen = cand;
            var mid = fromWorld + cand * 0.75f;
            var end = fromWorld + cand * 1.5f;
            if (!FeetBoxBlocked(mid) && !FeetBoxBlocked(end))
                return cand;
        }
        return Vector2.Zero;
    }

    /// <summary>Count snapshots whose CENTER cell is blocked (must stay 0
    /// while the clamp is on; checked in the online test).</summary>
    private void NoteSnapshot(GameServerClient.Snapshot s)
    {
        int c = Mathf.FloorToInt((float)(s.X / 0.8));
        int r = Mathf.FloorToInt((float)((36.0 - s.Y) / 0.8));
        if (c < 0 || r < 0 || c >= _builder.Cols || r >= _builder.Rows || _builder.IsBlockedCell(c, r))
        {
            _serverPosViolations++;
            GD.Print($"ONLINE WARN: snapshot inside blocked cell ({s.X:0.00},{s.Y:0.00}) cell=({c},{r})");
        }
    }

    private async Task<bool> ConnectAsync(string assetClassId)
    {
        var info = ClassSelect.Find(assetClassId);
        try
        {
            ClientCharacterId = info.CharacterId;
            _client = new GameServerClient(BaseUrl, info.CharacterId);
            if (!await _client.CheckHealthAsync())
            {
                _label.Text = "Online: server /health không đạt (correlation/status)";
                return false;
            }
            var snap = await _client.CreateSessionAsync(info.ServerClassId);
            NoteSnapshot(snap);
            _hud?.SetVitals(snap.Hp, snap.MaxHp, snap.Mp, snap.MaxMp);
            _hud?.SetMinimapCenter(snap.X, snap.Y);
            _serverTargetPx = WorldToPixel(snap.X, snap.Y);
            _player.GlobalPosition = _serverTargetPx; // spawn exactly where the server put us
            _connected = true;
            GD.Print($"ONLINE connected: class={info.ServerClassId} session={_client.SessionId} spawn=({snap.X},{snap.Y}) rev={snap.Revision}");
            return true;
        }
        catch (Exception ex)
        {
            // The P1 server slice is Minh-Kiem-only for now: say so
            // plainly instead of dumping a raw 400 at the player.
            _label.Text = ex.Message.Contains("classId")
                ? $"Server P1 hiện chỉ mở Minh Kiếm — {info.DisplayName} chưa được server hỗ trợ"
                : $"Online: kết nối thất bại — {ex.GetType().Name}: {ex.Message}";
            GD.PrintErr($"ONLINE connect failed: {ex.Message}");
            return false;
        }
    }

    public override void _Process(double delta)
    {
        if (!_connected) return;

        _input = _testMode ? _input : ReadKeyboard();
        if (!_testMode)
        {
            bool atk = Input.IsKeyPressed(Key.Space) || Input.IsKeyPressed(Key.J);
            if (atk && !_attackKeyWasDown) OnAttackPressed();
            _attackKeyWasDown = atk;
        }
        if (!_testMode && _input == Vector2.Zero && _hud != null)
            _input = _hud.JoystickVector; // HUD joystick as fallback input
        if (_input.LengthSquared() > 0.01f) _hud?.NoteMovement();
        _player.SetExternalInput(_input);

        double now = Time.GetTicksMsec();
        if (_input.LengthSquared() > 0.01f && now - _lastSendMs >= IntentIntervalMs)
        {
            _lastSendMs = now;
            double rawX = _input.X, rawY = -_input.Y; // Godot Y down -> world Y up
            _sendChain = _sendChain.ContinueWith(async _ =>
            {
                // Clamp INSIDE the chain, at execution time: the server
                // only moves on accepted intents, so LastSnapshot is the
                // exact position the next step starts from.
                var from = _client.LastSnapshot;
                var dir = ClampDirection(new Vector2((float)from.X, (float)from.Y),
                                         new Vector2((float)rawX, (float)rawY));
                if (dir == Vector2.Zero)
                {
                    _clamped++; // fully blocked: send nothing, burn no sequence
                    return;
                }
                if (dir != new Vector2((float)rawX, (float)rawY).Normalized() && rawX * rawX + rawY * rawY > 0.01)
                    _clamped++; // slid along an axis instead of the full direction
                var outcome = await _client.MoveAsync(dir.X, dir.Y);
                _lastRttMs = outcome.RoundTripMs;
                if (outcome.Ok)
                {
                    _accepted++;
                    NoteSnapshot(outcome.Snapshot);
                    _serverTargetPx = WorldToPixel(outcome.Snapshot.X, outcome.Snapshot.Y);
                }
                else
                {
                    _rejected++;
                    _lastError = $"{outcome.StatusCode}:{outcome.ErrorCode}";
                }
            }).Unwrap();
        }

        // Render tracking: glide to the authoritative position; snap when far.
        var pos = _player.GlobalPosition;
        float dist = pos.DistanceTo(_serverTargetPx);
        _player.GlobalPosition = dist > 40f
            ? _serverTargetPx
            : pos.MoveToward(_serverTargetPx, (float)(300.0 * delta));

        var s = _client.LastSnapshot;
        if (s != null)
        {
            _hud?.SetVitals(s.Hp, s.MaxHp, s.Mp, s.MaxMp);
            _hud?.SetMinimapCenter(s.X, s.Y);
            _label.Text = $"ONLINE · session {_client.SessionId?[..8]}… · server ({s.X:0.00}, {s.Y:0.00}) WU" +
                          $" · rev {s.Revision} · tick {s.ServerTick} · rtt {_lastRttMs:0} ms" +
                          $" · intents ok {_accepted} / rejected {_rejected} · clamp {_clamped}";
        }
    }

    private static Vector2 ReadKeyboard()
    {
        Vector2 raw = Vector2.Zero;
        if (Input.IsPhysicalKeyPressed(Key.Left) || Input.IsPhysicalKeyPressed(Key.A)) raw.X -= 1;
        if (Input.IsPhysicalKeyPressed(Key.Right) || Input.IsPhysicalKeyPressed(Key.D)) raw.X += 1;
        if (Input.IsPhysicalKeyPressed(Key.Up) || Input.IsPhysicalKeyPressed(Key.W)) raw.Y -= 1;
        if (Input.IsPhysicalKeyPressed(Key.Down) || Input.IsPhysicalKeyPressed(Key.S)) raw.Y += 1;
        return raw.LengthSquared() > 1f ? raw.Normalized() : raw;
    }

    // ---------------- automated online test ----------------
    private int _failures;
    private void Check(string name, bool ok, string detail = "")
    {
        GD.Print($"ONLINETEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _failures++;
    }

    private async Task WaitUntil(Func<bool> cond, int timeoutMs, string what)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        while (!cond() && sw.ElapsedMilliseconds < timeoutMs)
            await Task.Delay(50);
        if (!cond()) GD.Print($"ONLINETEST wait timeout: {what}");
    }

    private async Task RunOnlineTest()
    {
        // Class sweep vs the real server. Qoder's P1 slice currently
        // hard-codes CLASS_MINH_KIEM (P1Endpoints.DefaultClassId): MK
        // must be ACCEPTED (session + echoed class + spawn (18,0)); the
        // other four must be CLEANLY REJECTED (400, fieldErrors classId)
        // — not a crash, not a timeout. If the server opens more
        // classes later, the rejected-side checks fail loudly here,
        // which is the signal to widen them.
        foreach (var info in ClassSelect.Classes)
        {
            bool expectOpen = info.ServerClassId == "CLASS_MINH_KIEM";
            try
            {
                using var probe = new GameServerClient(BaseUrl, info.CharacterId);
                bool health = await probe.CheckHealthAsync();
                var snap0 = health ? await probe.CreateSessionAsync(info.ServerClassId) : null;
                Check($"session_class_{info.Id}",
                    expectOpen && snap0 != null && snap0.ClassId == info.ServerClassId && snap0.X == 18 && snap0.Y == 0,
                    snap0 == null ? "no session" : $"class={snap0.ClassId} spawn=({snap0.X},{snap0.Y})");
            }
            catch (InvalidOperationException ex) when (!expectOpen
                && ex.Message.Contains("400") && ex.Message.Contains("classId"))
            {
                Check($"session_class_{info.Id}_rejected_clean", true, "400 classId (server P1 scope)");
            }
            catch (Exception ex)
            {
                Check($"session_class_{info.Id}", false, ex.GetType().Name);
            }
        }

        await StartGame("minh_kiem");
        Check("connected", _connected);
        if (!_connected) { FinishTest(); return; }
        var spawn = _client.LastSnapshot;
        Check("spawn_server_18_0", spawn.X == 18 && spawn.Y == 0, $"({spawn.X},{spawn.Y})");
        await Task.Delay(150);
        float spawnErr = _player.GlobalPosition.DistanceTo(WorldToPixel(18, 0));
        Check("spawn_render_at_360_720", spawnErr < 2f, $"render={_player.GlobalPosition} err={spawnErr:0.0}px");

        // Walk EAST 1.4 s of intents. The server integrates REAL elapsed
        // time at 6 WU/s between accepted intents (per-step clamp 1.5 WU),
        // including the connect->first-intent gap (~0.25 s here), so the
        // honest expectation is ~6*(1.4+0.25) = ~9.9 WU, not 6*1.4.
        // First run measured dx=9.60 with a [6.0, 9.6] assert — the bound
        // was miscalibrated, the movement was right; bounds now [6, 10.5].
        _input = Vector2.Right;
        await Task.Delay(1400);
        _input = Vector2.Zero;
        await WaitUntil(() => _sendChain.IsCompleted, 3000, "east chain drain");
        await Task.Delay(500); // render settle
        var afterE = _client.LastSnapshot;
        double dx = afterE.X - 18;
        Check("east_distance_server", dx >= 6.0 && dx <= 10.5, $"dx={dx:0.00} WU accepted={_accepted}");
        float trackErrE = _player.GlobalPosition.DistanceTo(WorldToPixel(afterE.X, afterE.Y));
        Check("render_tracks_snapshot_east", trackErrE < 10f, $"err={trackErrE:0.0}px");

        // Walk NORTH 0.9 s: Godot input (0,-1) must become world +Y.
        double yBefore = afterE.Y;
        int acceptedBefore = _accepted;
        _input = Vector2.Up;
        await Task.Delay(900);
        _input = Vector2.Zero;
        await WaitUntil(() => _sendChain.IsCompleted, 3000, "north chain drain");
        await Task.Delay(500);
        var afterN = _client.LastSnapshot;
        double dy = afterN.Y - yBefore;
        Check("north_distance_server_y_up", dy >= 3.5 && dy <= 6.6, $"dy={dy:0.00} WU (Y-flip correct)");
        Check("phase_north_progress", _accepted > acceptedBefore, $"accepted={_accepted}");

        // CLAMP phase 1 — walk SOUTH into the water south of the hub.
        // Tiledata: this column is open until row 50 (world Y = -4.0);
        // without the client clamp the server would happily walk the
        // player to the map bound Y=-12. With the clamp (feet box, max
        // step predicted), he must stop with Y in (-4.0, -2.5), the
        // clamp counter must have fired, and no snapshot may ever land
        // inside a blocked cell.
        _input = Vector2.Down; // Godot down = world -Y (south)
        await Task.Delay(2600);
        _input = Vector2.Zero;
        await WaitUntil(() => _sendChain.IsCompleted, 3000, "south chain drain");
        await Task.Delay(400);
        var afterS = _client.LastSnapshot;
        Check("clamp_stops_at_water_edge", afterS.Y > -4.05 && afterS.Y < -2.2,
            $"final y={afterS.Y:0.00} (water edge -4.0; unclamped server bound -12)");
        Check("clamp_counter_fired", _clamped > 0, $"clamped={_clamped}");

        // CLAMP phase 2 — push SOUTH-EAST against the shore: full diagonal
        // is blocked, X-only slide must carry him east along the edge.
        double sx = afterS.X, sy = afterS.Y;
        _input = new Vector2(1, 1).Normalized(); // Godot SE = world SE
        await Task.Delay(1400);
        _input = Vector2.Zero;
        await WaitUntil(() => _sendChain.IsCompleted, 3000, "slide chain drain");
        await Task.Delay(400);
        var afterSE = _client.LastSnapshot;
        Check("clamp_wall_slide_east", afterSE.X - sx >= 3.0 && Math.Abs(afterSE.Y - sy) <= 0.9,
            $"dx={afterSE.X - sx:0.00} dy={afterSE.Y - sy:0.00}");
        Check("no_snapshot_in_blocked_cell", _serverPosViolations == 0,
            $"violations={_serverPosViolations}");
        Check("no_rejected_intents", _rejected == 0,
            $"accepted={_accepted} rejected={_rejected} err={_lastError}");
        Check("revision_equals_accepted", afterSE.Revision == 1 + _accepted,
            $"rev={afterSE.Revision} accepted={_accepted}");

        FinishTest();
    }

    private void FinishTest()
    {
        GD.Print(_failures == 0 ? "ONLINETEST RESULT: PASS" : $"ONLINETEST RESULT: FAIL ({_failures})");
        GetTree().Quit(_failures == 0 ? 0 : 1);
    }

    private async Task RunOnlineShot()
    {
        string shotClass = "minh_kiem";
        foreach (var a in OS.GetCmdlineUserArgs())
            if (a.StartsWith("--shotclass=")) shotClass = a["--shotclass=".Length..];
        await StartGame(shotClass);
        if (!_connected) { GetTree().Quit(1); return; }
        _input = Vector2.Right;
        await Task.Delay(900);
        _input = Vector2.Down; // south, into the water — the clamp must stop him at the shore
        await Task.Delay(2400);
        _input = Vector2.Zero;
        await WaitUntil(() => _sendChain.IsCompleted, 3000, "shot chain drain");
        await Task.Delay(600);
        // Mirror HUD mockup r2 for the screenshot: skill 2 at 50% (3 s of
        // 6 s left) and skill 5 at 25% (3 s of 12 s left).
        if (_hud != null)
        {
            _hud.StartCooldown(4);
            _hud.AdvanceTime(6.0);
            _hud.StartCooldown(1);
            _hud.AdvanceTime(3.0);
        }
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_online.png");
        image.SavePng(path);
        var s = _client.LastSnapshot;
        GD.Print($"ONLINESHOT SAVED: {path} server=({s.X:0.00},{s.Y:0.00}) rev={s.Revision}");
        GetTree().Quit(0);
    }

    // ---------------- class-select test (offline) ----------------
    // The full session-per-class proof lives in RunOnlineTest (needs the
    // server). This offline suite proves the menu flow itself under the
    // WO24 M-B rule: server-unsupported classes are DISABLED with a
    // reason (preview kept) and choosing one is refused at the menu —
    // only Minh Kiếm can be picked, and picking it applies animator
    // library + HUD portrait + character id, then attempts the connect
    // for THAT class (fails gracefully here — no server in this suite).
    private int _selFailures;
    private void SelCheck(string name, bool ok, string detail = "")
    {
        GD.Print($"SELECTTEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _selFailures++;
    }

    private async Task RunSelectTest()
    {
        _classSelect.ShowMenu(); // what interactive mode does in _Ready
        for (int i = 0; i < 5; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        SelCheck("menu_shown_first", _classSelect.Visible);
        SelCheck("no_class_yet", SelectedClass == null);

        // WO24 M-B: exactly one card enabled (Minh Kiếm); the other four
        // are disabled because the alpha server does not support them.
        bool cardStates = true;
        foreach (var info in ClassSelect.Classes)
            cardStates &= _classSelect.IsCardDisabled(info.Id)
                          == (info.ServerClassId != "CLASS_MINH_KIEM");
        SelCheck("cards_disabled_except_minh_kiem", cardStates);

        // Choosing a disabled class is refused at the menu: nothing is
        // emitted, the menu stays open, the reason is shown.
        _classSelect.Choose("linh_cung");
        for (int i = 0; i < 3; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        SelCheck("refused_menu_stays_open", _classSelect.Visible);
        SelCheck("refused_no_selection", SelectedClass == null && _classSelect.SelectedClass == null);
        SelCheck("refused_reason_shown", _classSelect.RefusalMessage.Contains("Minh Kiếm"),
            _classSelect.RefusalMessage);
        SelCheck("refused_animator_untouched", _animator.ClassId == "minh_kiem", _animator.ClassId);

        // The key path refuses the same way (key 4 = Thạch Chùy).
        _classSelect.SimulateKeyIndex(3);
        SelCheck("refused_key_path", _classSelect.Visible
            && _classSelect.RefusalMessage.Contains("THẠCH CHÙY"), _classSelect.RefusalMessage);

        // Minh Kiếm — the one supported class — goes through end-to-end.
        _classSelect.Choose("minh_kiem");
        await Task.Delay(400); // StartGame applies sync, connect attempt fails fast (no server)
        for (int i = 0; i < 3; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

        SelCheck("menu_hidden_after_choose", !_classSelect.Visible);
        SelCheck("selected_minh_kiem", SelectedClass == "minh_kiem", SelectedClass ?? "null");
        SelCheck("animator_minh_kiem_128", _animator.ClassId == "minh_kiem"
            && _animator.SpriteFramesAnimationCount == 128,
            $"{_animator.ClassId}/{_animator.SpriteFramesAnimationCount}");
        SelCheck("hud_portrait_minh_kiem", _hud != null && _hud.CurrentPortraitClass == "minh_kiem",
            _hud?.CurrentPortraitClass ?? "nohud");
        SelCheck("character_id_for_class", ClientCharacterId == "CHR_MINH_KIEM_01",
            ClientCharacterId ?? "null");
        SelCheck("not_connected_without_server", !_connected);

        GD.Print(_selFailures == 0 ? "SELECTTEST RESULT: PASS" : $"SELECTTEST RESULT: FAIL ({_selFailures})");
        GetTree().Quit(_selFailures == 0 ? 0 : 1);
    }

    private async Task RunSelectShot()
    {
        _classSelect.ShowMenu();
        for (int i = 0; i < 5; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_select.png");
        image.SavePng(path);
        GD.Print($"SELECTSHOT SAVED: {path}");
        // Second capture: press key 5 (Linh Cung) — the card is disabled
        // in the alpha, so the menu stays open and the refusal reason
        // appears on the notice line.
        _classSelect.SimulateKeyIndex(4);
        await Task.Delay(300);
        for (int i = 0; i < 3; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image2 = GetViewport().GetTexture().GetImage();
        string path2 = ProjectSettings.GlobalizePath("res://screenshot_select_refusal.png");
        image2.SavePng(path2);
        GD.Print($"SELECTSHOT2 SAVED: {path2}");
        GetTree().Quit(0);
    }
}
