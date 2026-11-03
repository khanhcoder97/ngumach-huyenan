using Godot;
using System;

/// <summary>
/// HUD board-06 (PR #38) rebuilt as real Godot Controls, using the cut
/// components in assets/hud/ at the exact LAYOUT.md coordinates (640x360).
/// Everything is functional, not a mockup image:
///  - HP/MP fills follow SetVitals() — OnlineMain feeds them from the
///    server snapshot (self.hp/maxHp, mp/maxMp).
///  - Skill cooldowns run the round-2 spec: dark wedge (8,12,22,165)
///    covering the REMAINING fraction of the inner disc (r = 0.693 R),
///    starting at 12 o'clock and opening clockwise; center label shows
///    seconds left (1 decimal, half-up). Sample totals 4/6/8/10/12/15 s
///    (real numbers come from Qoder's skill data later).
///  - The joystick is a working input device (mouse + touch drag) AND
///    follows the polish spec: 55% alpha while moving, fading to 22%
///    over ~300 ms after ~2 s idle (the two component textures carry the
///    baked alphas; the active one is cross-faded over the idle one).
///  - The minimap is real: a 56x48 WU window of the Bến Mưa detail map
///    follows the player, with a position marker.
/// Godot quirk found while building this: a TextureRect whose texture is
/// assigned while ExpandMode is KeepSize snaps its rect to the TEXTURE
/// size (735x717 etc.) when it enters the tree, discarding the Size set
/// in the initializer. Every TextureRect below therefore gets its size
/// re-asserted after AddChild.
/// Known remaining defect (from LAYOUT.md, unchanged): all text uses the
/// engine default font — the game's Vietnamese pixel font does not exist
/// yet. Quest lines are the board's sample content.
/// </summary>
public partial class Hud : CanvasLayer
{
    /// <summary>The big attack button was pressed (OnlineMain maps this
    /// to the attack combo).</summary>
    [Signal] public delegate void AttackPressedEventHandler();
    /// <summary>A skill button was pressed (0-based). Its cooldown has
    /// already started client-side when this fires.</summary>
    [Signal] public delegate void SkillActivatedEventHandler(int index);

    private const string A = "res://assets/hud/";

    // Skill button centres from LAYOUT.md (attack centre 582,283).
    private static readonly Vector2[] SkillCenters =
    {
        new(540, 318), new(520, 272), new(528, 228),
        new(556, 192), new(594, 180), new(622, 206)
    };
    private static readonly double[] SkillTotals = { 4, 6, 8, 10, 12, 15 };

    private ColorRect _hpFill, _mpFill, _expFill;
    private TextureRect _portraitRect;
    public string CurrentPortraitClass { get; private set; } = "minh_kiem";
    private readonly double[] _cooldownLeft = new double[6];
    private readonly TextureProgressBar[] _sweeps = new TextureProgressBar[6];
    private readonly Label[] _cdLabels = new Label[6];

    private TextureRect _joyActiveRect;
    private Control _joyArea;
    private bool _joyDragging;
    private double _joyAlpha; // 0 = idle texture only, 1 = active fully over
    private ulong _lastMoveMs;
    public Vector2 JoystickVector { get; private set; } = Vector2.Zero;

    private AtlasTexture _minimapAtlas;
    private ColorRect _minimapMarker;
    private const float MapPxW = 7200f, MapPxH = 960f;

    public double HpFrac { get; private set; } = 1;
    public double MpFrac { get; private set; } = 1;
    public int AttackPresses { get; private set; }
    public int BagPresses { get; private set; }
    public readonly int[] SkillPresses = new int[6];
    public double JoystickActiveAlpha => _joyAlpha;
    public Rect2 MinimapRegion => _minimapAtlas?.Region ?? new Rect2();
    public double CooldownRemaining(int i) => _cooldownLeft[i];
    public double CooldownFrac(int i) => SkillTotals[i] > 0 ? _cooldownLeft[i] / SkillTotals[i] : 0;

    public override void _Ready()
    {
        Layer = 10;
        BuildTopLeft();
        BuildQuest();
        BuildJoystick();
        BuildMinimap();
        BuildButtons();
        BuildExp();
        SetVitals(100, 100, 50, 50);
        SetExp(0.35);
        SetMinimapCenter(18, 0);
    }

    // ---------------- construction helpers ----------------
    private static Texture2D Tex(string name) => GD.Load<Texture2D>(A + name);

    private TextureRect Img(string name, float x, float y, float w, float h)
    {
        var t = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        t.Texture = Tex(name);
        t.Position = new Vector2(x, y);
        AddChild(t);
        t.Size = new Vector2(w, h); // re-assert AFTER tree entry (see note above)
        return t;
    }

    private Label Text(string str, float x, float y, float w, int fontSize, Color color,
                       HorizontalAlignment align = HorizontalAlignment.Left)
    {
        var l = new Label
        {
            Text = str,
            Position = new Vector2(x, y),
            Size = new Vector2(w, fontSize + 4),
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        l.AddThemeFontSizeOverride("font_size", fontSize);
        l.AddThemeColorOverride("font_color", color);
        l.HorizontalAlignment = align;
        AddChild(l);
        return l;
    }

    private ColorRect Box(float x, float y, float w, float h, Color color)
    {
        var r = new ColorRect
        {
            Position = new Vector2(x, y),
            Size = new Vector2(w, h),
            Color = color,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        AddChild(r);
        return r;
    }

    // ---------------- top-left cluster ----------------
    private void BuildTopLeft()
    {
        _portraitRect = Img("portraits/portrait_minh_kiem.png", 8, 4, 56, 56);
        // HP bar: frame 130x11 at (70,14); fill inside (73,16) 124x7.
        // The frame textures are OPAQUE (dark slate interior), so the
        // fill must be drawn ON TOP of the frame's inner band — same
        // compositing order as the PIL mockup.
        Img("hp_bar_frame.png", 70, 14, 130, 11);
        _hpFill = Box(73, 16, 124, 7, new Color(0.78f, 0.13f, 0.15f));
        Img("mp_bar_frame.png", 70, 28, 130, 11);
        _mpFill = Box(73, 30, 124, 7, new Color(0.13f, 0.32f, 0.85f));
        Text("HP", 56, 13, 14, 8, Colors.White);
        Text("MP", 56, 27, 14, 8, Colors.White);
        Img("pips.png", 70, 45, 50, 10);
    }

    /// <summary>Swap the portrait ring to another class's face
    /// (assets/hud/portraits/portrait_<classId>.png, round-2 recipe).</summary>
    public void SetPortraitClass(string classId)
    {
        CurrentPortraitClass = classId;
        _portraitRect.Texture = Tex($"portraits/portrait_{classId}.png");
    }

    public void SetVitals(int hp, int maxHp, int mp, int maxMp)
    {
        HpFrac = maxHp > 0 ? Mathf.Clamp((double)hp / maxHp, 0, 1) : 0;
        MpFrac = maxMp > 0 ? Mathf.Clamp((double)mp / maxMp, 0, 1) : 0;
        _hpFill.Size = new Vector2((float)(124 * HpFrac), 7);
        _mpFill.Size = new Vector2((float)(124 * MpFrac), 7);
    }

    // ---------------- quest panel ----------------
    private void BuildQuest()
    {
        Img("quest_panel.png", 6, 64, 116, 58);
        Text("QUEST", 12, 66, 60, 9, new Color(0.96f, 0.82f, 0.35f));
        string[] lines = { "Diệt Cá Linh x3", "Hai Rễ Nước x2", "Gặp Hạ Mạc" };
        for (int i = 0; i < 3; i++)
        {
            float y = 82 + i * 12;
            var cb = new Panel
            {
                Position = new Vector2(12, y + 1),
                Size = new Vector2(7, 7),
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            var style = new StyleBoxFlat
            {
                BorderWidthLeft = 1, BorderWidthRight = 1, BorderWidthTop = 1, BorderWidthBottom = 1,
                BorderColor = new Color(0.9f, 0.85f, 0.6f),
                BgColor = i == 0 ? new Color(0.95f, 0.55f, 0.15f) : new Color(0, 0, 0, 0)
            };
            cb.AddThemeStyleboxOverride("panel", style);
            AddChild(cb);
            Text(lines[i], 23, y, 96, 8, new Color(0.93f, 0.91f, 0.86f));
        }
    }

    // ---------------- joystick ----------------
    private void BuildJoystick()
    {
        _joyArea = new Control
        {
            Position = new Vector2(15, 251),
            Size = new Vector2(78, 78),
            MouseFilter = Control.MouseFilterEnum.Stop
        };
        AddChild(_joyArea);
        var idle = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        idle.Texture = Tex("joystick_idle.png");
        _joyArea.AddChild(idle);
        idle.Size = new Vector2(78, 78);
        _joyActiveRect = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore,
            Modulate = new Color(1, 1, 1, 0)
        };
        _joyActiveRect.Texture = Tex("joystick_active.png");
        _joyArea.AddChild(_joyActiveRect);
        _joyActiveRect.Size = new Vector2(78, 78);
        _joyArea.GuiInput += OnJoystickInput;
    }

    private void OnJoystickInput(InputEvent e)
    {
        switch (e)
        {
            case InputEventMouseButton b when b.ButtonIndex == MouseButton.Left:
                if (b.Pressed) { _joyDragging = true; UpdateDrag(b.Position); }
                else EndDrag();
                break;
            case InputEventMouseMotion m when _joyDragging:
                UpdateDrag(m.Position);
                break;
            case InputEventScreenTouch t:
                if (t.Pressed) { _joyDragging = true; UpdateDrag(t.Position); }
                else EndDrag();
                break;
            case InputEventScreenDrag d when _joyDragging:
                UpdateDrag(d.Position);
                break;
        }
    }

    private void UpdateDrag(Vector2 localPos)
    {
        Vector2 offset = localPos - new Vector2(39, 39);
        float len = Mathf.Min(offset.Length(), 30f);
        Vector2 dir = offset.Length() > 0.01f ? offset.Normalized() : Vector2.Zero;
        JoystickVector = len / 30f < 0.15f ? Vector2.Zero : dir * (len / 30f);
        _joyActiveRect.Position = dir * Mathf.Min(len, 6f);
        if (JoystickVector != Vector2.Zero) _lastMoveMs = Time.GetTicksMsec();
    }

    private void EndDrag()
    {
        _joyDragging = false;
        JoystickVector = Vector2.Zero;
        _joyActiveRect.Position = Vector2.Zero;
    }

    // Test seams + OnlineMain hook: dragging is simulated through the
    // same code path as real input.
    public void SimulateJoystickDrag(Vector2 localPos)
    {
        _joyDragging = true;
        UpdateDrag(localPos);
    }
    public void SimulateJoystickRelease() => EndDrag();

    /// <summary>Call while the player moves by any input (polish spec:
    /// joystick shows the active state while moving).</summary>
    public void NoteMovement() => _lastMoveMs = Time.GetTicksMsec();

    // ---------------- minimap ----------------
    private void BuildMinimap()
    {
        // "BẾN MƯA" sign tab above the frame.
        Box(564, 4, 52, 12, new Color(0.05f, 0.06f, 0.10f, 0.92f));
        Text("BẾN MƯA", 564, 5, 52, 8, new Color(0.96f, 0.82f, 0.35f), HorizontalAlignment.Center);

        _minimapAtlas = new AtlasTexture { Atlas = GD.Load<Texture2D>("res://assets/ben_mua_full_map.png") };
        var inner = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        inner.Texture = _minimapAtlas;
        inner.Position = new Vector2(550, 15);
        AddChild(inner);
        inner.Size = new Vector2(80, 68);
        _minimapMarker = Box(589, 48, 3, 3, new Color(1f, 0.25f, 0.2f));
        Img("minimap_frame.png", 546, 10, 88, 78);

        // BAG button under the minimap.
        var bag = new TextureButton
        {
            Position = new Vector2(596, 104),
            Size = new Vector2(34, 34),
            TextureNormal = Tex("bag_button.png"),
            IgnoreTextureSize = true,
            StretchMode = TextureButton.StretchModeEnum.Scale
        };
        bag.Pressed += () => BagPresses++;
        AddChild(bag);
        var pouch = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        pouch.Texture = Tex("icon_pouch.png");
        pouch.Position = new Vector2(602, 110);
        AddChild(pouch);
        pouch.Size = new Vector2(22, 22);
        Text("BAG", 596, 139, 34, 8, new Color(0.93f, 0.91f, 0.86f), HorizontalAlignment.Center);
    }

    /// <summary>Center the 56x48 WU minimap window on a world position
    /// (clamped to the map) and place the player marker.</summary>
    public void SetMinimapCenter(double worldX, double worldY)
    {
        float cx = (float)(worldX * 20.0), cy = (float)((36.0 - worldY) * 20.0);
        float rw = 56 * 20f, rh = 48 * 20f; // 1120 x 960 px
        float ox = Mathf.Clamp(cx - rw / 2, 0, MapPxW - rw);
        float oy = Mathf.Clamp(cy - rh / 2, 0, MapPxH - rh);
        _minimapAtlas.Region = new Rect2(ox, oy, rw, rh);
        float mx = 550 + (cx - ox) / rw * 80f - 1.5f;
        float my = 15 + (cy - oy) / rh * 68f - 1.5f;
        _minimapMarker.Position = new Vector2(mx, my);
    }

    // ---------------- attack + skills ----------------
    private void BuildButtons()
    {
        var attack = new TextureButton
        {
            Position = new Vector2(582 - 31, 283 - 31),
            Size = new Vector2(62, 62),
            TextureNormal = Tex("attack_button.png"),
            IgnoreTextureSize = true,
            StretchMode = TextureButton.StretchModeEnum.Scale,
            PivotOffset = new Vector2(31, 31)
        };
        attack.Pressed += () =>
        {
            AttackPresses++;
            EmitSignal(SignalName.AttackPressed);
            var tw = CreateTween();
            attack.Scale = new Vector2(0.92f, 0.92f);
            tw.TweenProperty(attack, "scale", Vector2.One, 0.12);
        };
        AddChild(attack);
        var sword = new TextureRect
        {
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.Scale,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        sword.Texture = Tex("icon_sword.png");
        sword.Position = new Vector2(582 - 20, 283 - 20);
        AddChild(sword);
        sword.Size = new Vector2(40, 40);

        var disc = MakeCooldownDisc();
        for (int i = 0; i < 6; i++)
        {
            int idx = i;
            var c = SkillCenters[i];
            var btn = new TextureButton
            {
                Position = c - new Vector2(16.5f, 16.5f),
                Size = new Vector2(33, 33),
                TextureNormal = Tex("skill_button.png"),
                IgnoreTextureSize = true,
                StretchMode = TextureButton.StretchModeEnum.Scale
            };
            btn.Pressed += () =>
            {
                SkillPresses[idx]++;
                StartCooldown(idx);
                EmitSignal(SignalName.SkillActivated, idx);
            };
            AddChild(btn);
            var icon = new TextureRect
            {
                ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
                StretchMode = TextureRect.StretchModeEnum.Scale,
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            icon.Texture = Tex($"skill_icon_{i + 1}.png");
            icon.Position = c - new Vector2(10.5f, 10.5f);
            AddChild(icon);
            icon.Size = new Vector2(21, 21);

            var sweep = new TextureProgressBar
            {
                Position = c - new Vector2(16.5f, 16.5f),
                Size = new Vector2(33, 33),
                MinValue = 0,
                MaxValue = 1000,
                Value = 0,
                TextureProgress = disc,
                FillMode = (int)TextureProgressBar.FillModeEnum.Clockwise,
                RadialInitialAngle = 0,
                RadialFillDegrees = 360,
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            AddChild(sweep);
            _sweeps[i] = sweep;

            _cdLabels[i] = Text("", c.X - 16, c.Y - 7, 32, 11, Colors.White, HorizontalAlignment.Center);

            // Number badge at (-13,-13) from the button centre.
            var badge = new Panel
            {
                Position = c + new Vector2(-19, -19),
                Size = new Vector2(12, 12),
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            var bs = new StyleBoxFlat
            {
                BgColor = new Color(0.07f, 0.09f, 0.14f, 0.95f),
                BorderWidthLeft = 1, BorderWidthRight = 1, BorderWidthTop = 1, BorderWidthBottom = 1,
                BorderColor = new Color(0.85f, 0.7f, 0.3f),
                CornerRadiusTopLeft = 6, CornerRadiusTopRight = 6,
                CornerRadiusBottomLeft = 6, CornerRadiusBottomRight = 6
            };
            badge.AddThemeStyleboxOverride("panel", bs);
            AddChild(badge);
            var num = new Label
            {
                Text = (i + 1).ToString(),
                Position = c + new Vector2(-19, -19),
                Size = new Vector2(12, 12),
                HorizontalAlignment = HorizontalAlignment.Center,
                VerticalAlignment = VerticalAlignment.Center,
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            num.AddThemeFontSizeOverride("font_size", 8);
            num.AddThemeColorOverride("font_color", Colors.White);
            AddChild(num);
        }
    }

    private static ImageTexture MakeCooldownDisc()
    {
        var img = Image.CreateEmpty(33, 33, false, Image.Format.Rgba8);
        var dark = new Color(8f / 255, 12f / 255, 22f / 255, 165f / 255);
        for (int y = 0; y < 33; y++)
            for (int x = 0; x < 33; x++)
            {
                float d = Mathf.Sqrt((x - 16) * (x - 16) + (y - 16) * (y - 16));
                if (d <= 11.5f) img.SetPixel(x, y, dark);
            }
        return ImageTexture.CreateFromImage(img);
    }

    public bool StartCooldown(int i)
    {
        if (_cooldownLeft[i] > 0) return false;
        _cooldownLeft[i] = SkillTotals[i];
        RefreshCooldown(i);
        return true;
    }

    private void RefreshCooldown(int i)
    {
        double frac = CooldownFrac(i);
        _sweeps[i].Value = frac * 1000.0;
        _cdLabels[i].Text = _cooldownLeft[i] > 0 ? FormatSeconds(_cooldownLeft[i]) : "";
    }

    private static string FormatSeconds(double s)
    {
        double r = Math.Round(s, 1, MidpointRounding.AwayFromZero);
        return r == Math.Floor(r) ? ((int)r).ToString()
            : r.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture);
    }

    /// <summary>Advance cooldown timers; called from _Process and used
    /// directly by tests for deterministic checks.</summary>
    public void AdvanceTime(double dt)
    {
        for (int i = 0; i < 6; i++)
        {
            if (_cooldownLeft[i] <= 0) continue;
            _cooldownLeft[i] = Math.Max(0, _cooldownLeft[i] - dt);
            RefreshCooldown(i);
        }
    }

    // ---------------- EXP ----------------
    private void BuildExp()
    {
        Text("EXP", 3, 347, 20, 8, new Color(0.96f, 0.82f, 0.35f));
        Img("exp_bar.png", 24, 349, 612, 8);
        _expFill = Box(28, 351, 0, 4, new Color(0.98f, 0.8f, 0.3f, 0.9f));
    }

    public void SetExp(double frac)
    {
        frac = Mathf.Clamp(frac, 0, 1);
        _expFill.Size = new Vector2((float)(604 * frac), 4);
    }

    // ---------------- per-frame ----------------
    public override void _Process(double delta)
    {
        AdvanceTime(delta);
        // Joystick fade: active while dragging or within 2 s of movement,
        // cross-fade over ~300 ms (polish spec).
        bool active = _joyDragging || Time.GetTicksMsec() - _lastMoveMs < 2000;
        double target = active ? 1 : 0;
        _joyAlpha = Mathf.MoveToward((float)_joyAlpha, (float)target, (float)(delta / 0.3));
        if (_joyActiveRect != null)
            _joyActiveRect.Modulate = new Color(1, 1, 1, (float)_joyAlpha);
    }
}
