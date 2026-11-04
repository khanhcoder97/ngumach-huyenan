using Godot;

/// <summary>
/// Class-select screen for the online client: five cards (one per
/// playable class), click or keys 1-5. This class also owns the single
/// class table the whole client uses — asset id (sheet folder), display
/// name, and the server contract ids (CLASS_* / CHR_*_01 from the
/// production spec). Portraits on the cards are the head crop of each
/// class's own idle sheet (S frame), so what you pick is what you play.
/// Text uses the engine default font, like the HUD (the game's
/// Vietnamese pixel font does not exist yet).
///
/// Work Order 24 M-B + OPC-15 packet: a class the server does not
/// support yet is shown as a DISABLED card (portrait preview kept) with
/// the reason on the card and on the notice line — it is never chosen
/// and never sent to the server as another class. The gate below
/// mirrors OPC-15's ClientCapability list (alpha: CLASS_MINH_KIEM
/// only); when Shared/ClientCore merges into this branch it binds to
/// ClientCapability.IsClassSupported directly. The server stays the
/// source of truth (it rejects other classes with a clean 400).
/// </summary>
public partial class ClassSelect : CanvasLayer
{
    [Signal] public delegate void ClassChosenEventHandler(string classId);

    public sealed record ClassInfo(string Id, string DisplayName, string Sub,
                                   string ServerClassId, string CharacterId);
    public static readonly ClassInfo[] Classes =
    {
        new("minh_kiem",  "MINH KIẾM",  "Kiếm · Cận chiến",  "CLASS_MINH_KIEM",  "CHR_MINH_KIEM_01"),
        new("anh_dao",    "ẢNH ĐAO",    "Đao · Sát thủ",           "CLASS_ANH_DAO",    "CHR_ANH_DAO_01"),
        new("huyen_but",  "HUYỀN BÚT",  "Bút pháp · Hỗ trợ",       "CLASS_HUYEN_BUT",  "CHR_HUYEN_BUT_01"),
        new("thach_chuy", "THẠCH CHÙY", "Chùy · Đỡ đòn",           "CLASS_THACH_CHUY", "CHR_THACH_CHUY_01"),
        new("linh_cung",  "LINH CUNG",  "Cung · Tầm xa",           "CLASS_LINH_CUNG",  "CHR_LINH_CUNG_01"),
    };

    public static ClassInfo Find(string id) =>
        System.Array.Find(Classes, c => c.Id == id) ?? Classes[0];

    // --- alpha capability gate (mirror of OPC-15 ClientCapability) ---
    private static readonly string[] AlphaSupportedServerClasses = { "CLASS_MINH_KIEM" };
    public static bool IsServerSupported(ClassInfo info) =>
        System.Array.IndexOf(AlphaSupportedServerClasses, info.ServerClassId) >= 0;
    public const string UnsupportedReason = "Server alpha hiện chỉ mở Minh Kiếm";

    private readonly System.Collections.Generic.Dictionary<string, Button> _cards = new();
    private Label _notice;
    /// <summary>Last refusal text shown for a disabled class ("" if none).</summary>
    public string RefusalMessage { get; private set; } = "";
    /// <summary>True when the class's card is disabled (server-unsupported).</summary>
    public bool IsCardDisabled(string classId) =>
        _cards.TryGetValue(classId, out var b) && b.Disabled;

    public string SelectedClass { get; private set; }

    public override void _Ready()
    {
        Layer = 20;
        Visible = false;
        var dim = new ColorRect
        {
            Position = Vector2.Zero,
            Size = new Vector2(640, 360),
            Color = new Color(0.02f, 0.03f, 0.05f, 0.86f)
        };
        AddChild(dim);
        AddLabel("CHỌN NHÂN VẬT", 0, 46, 640, 16, new Color(0.96f, 0.82f, 0.35f), HorizontalAlignment.Center);
        AddLabel("Ngũ Mạch — Huyền Ấn", 0, 68, 640, 9, new Color(0.75f, 0.78f, 0.85f), HorizontalAlignment.Center);

        for (int i = 0; i < Classes.Length; i++)
            AddCard(i, Classes[i]);

        _notice = new Label
        {
            Text = "",
            Position = new Vector2(0, 296),
            Size = new Vector2(640, 14),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        _notice.AddThemeFontSizeOverride("font_size", 10);
        _notice.AddThemeColorOverride("font_color", new Color(0.98f, 0.62f, 0.5f));
        AddChild(_notice);

        AddLabel("Bấm vào thẻ hoặc nhấn phím 1–5 để chọn", 0, 322, 640, 9,
                 new Color(0.65f, 0.68f, 0.75f), HorizontalAlignment.Center);
    }

    private void AddLabel(string text, float x, float y, float w, int fontSize, Color color,
                          HorizontalAlignment align)
    {
        var l = new Label
        {
            Text = text,
            Position = new Vector2(x, y),
            Size = new Vector2(w, fontSize + 6),
            HorizontalAlignment = align,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        l.AddThemeFontSizeOverride("font_size", fontSize);
        l.AddThemeColorOverride("font_color", color);
        AddChild(l);
    }

    private void AddCard(int i, ClassInfo info)
    {
        bool supported = IsServerSupported(info);
        var btn = new Button
        {
            Position = new Vector2(20 + i * 122, 100),
            Size = new Vector2(112, 180),
            Text = "",
            Disabled = !supported
        };
        _cards[info.Id] = btn;
        var normal = new StyleBoxFlat
        {
            BgColor = new Color(0.05f, 0.07f, 0.10f, 0.97f),
            BorderColor = new Color(0.55f, 0.45f, 0.2f),
            BorderWidthLeft = 1, BorderWidthRight = 1, BorderWidthTop = 1, BorderWidthBottom = 1,
            CornerRadiusTopLeft = 4, CornerRadiusTopRight = 4,
            CornerRadiusBottomLeft = 4, CornerRadiusBottomRight = 4
        };
        var hover = (StyleBoxFlat)normal.Duplicate();
        hover.BorderColor = new Color(0.96f, 0.82f, 0.35f);
        hover.BgColor = new Color(0.08f, 0.11f, 0.16f, 0.97f);
        btn.AddThemeStyleboxOverride("normal", normal);
        btn.AddThemeStyleboxOverride("hover", hover);
        btn.AddThemeStyleboxOverride("pressed", hover);
        btn.AddThemeStyleboxOverride("focus", new StyleBoxEmpty());
        if (!supported)
        {
            var disabledBox = (StyleBoxFlat)normal.Duplicate();
            disabledBox.BgColor = new Color(0.04f, 0.05f, 0.07f, 0.97f);
            disabledBox.BorderColor = new Color(0.3f, 0.3f, 0.34f);
            btn.AddThemeStyleboxOverride("disabled", disabledBox);
        }
        string id = info.Id;
        btn.Pressed += () => Choose(id);
        AddChild(btn);

        // Head crop from the class's own idle sheet (S row, frame 0).
        var sheet = GD.Load<Texture2D>($"res://assets/chars/{info.Id}/idle.png");
        var head = new AtlasTexture { Atlas = sheet, Region = new Rect2(8, 256, 32, 32), FilterClip = true };
        var portrait = new TextureRect
        {
            Texture = head,
            ExpandMode = TextureRect.ExpandModeEnum.IgnoreSize,
            StretchMode = TextureRect.StretchModeEnum.KeepAspectCentered,
            TextureFilter = CanvasItem.TextureFilterEnum.Nearest,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        if (!supported)
            portrait.Modulate = new Color(0.45f, 0.45f, 0.5f); // preview kept, clearly dimmed
        btn.AddChild(portrait);
        portrait.Position = new Vector2(24, 14);
        portrait.Size = new Vector2(64, 64);

        var name = new Label
        {
            Text = info.DisplayName,
            Position = new Vector2(0, 88),
            Size = new Vector2(112, 16),
            HorizontalAlignment = HorizontalAlignment.Center,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        name.AddThemeFontSizeOverride("font_size", 11);
        name.AddThemeColorOverride("font_color", supported ? Colors.White : new Color(0.55f, 0.56f, 0.6f));
        btn.AddChild(name);

        var sub = new Label
        {
            Text = info.Sub,
            Position = new Vector2(2, 108),
            Size = new Vector2(108, 26),
            HorizontalAlignment = HorizontalAlignment.Center,
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        sub.AddThemeFontSizeOverride("font_size", 8);
        sub.AddThemeColorOverride("font_color", supported ? new Color(0.8f, 0.75f, 0.55f) : new Color(0.5f, 0.48f, 0.4f));
        btn.AddChild(sub);

        if (!supported)
        {
            var reason = new Label
            {
                Text = "Chưa mở ở bản alpha",
                Position = new Vector2(2, 148),
                Size = new Vector2(108, 12),
                HorizontalAlignment = HorizontalAlignment.Center,
                MouseFilter = Control.MouseFilterEnum.Ignore
            };
            reason.AddThemeFontSizeOverride("font_size", 8);
            reason.AddThemeColorOverride("font_color", new Color(0.98f, 0.62f, 0.5f));
            btn.AddChild(reason);
        }

        var key = new Label
        {
            Text = (i + 1).ToString(),
            Position = new Vector2(6, 4),
            Size = new Vector2(12, 12),
            MouseFilter = Control.MouseFilterEnum.Ignore
        };
        key.AddThemeFontSizeOverride("font_size", 9);
        key.AddThemeColorOverride("font_color", new Color(0.96f, 0.82f, 0.35f));
        btn.AddChild(key);
    }

    public void ShowMenu() => Visible = true;
    public void HideMenu() => Visible = false;

    /// <summary>Pick a class (same path as clicking its card). A
    /// server-unsupported class is REFUSED here as a second line of
    /// defence (its card is already disabled): the menu stays open and
    /// the reason is shown — nothing is emitted, nothing is sent.</summary>
    public void Choose(string classId)
    {
        var info = Find(classId);
        if (!IsServerSupported(info)) { ShowRefusal(info); return; }
        SelectedClass = classId;
        Visible = false;
        EmitSignal(SignalName.ClassChosen, classId);
    }

    private void ShowRefusal(ClassInfo info)
    {
        RefusalMessage = $"{info.DisplayName} — {UnsupportedReason}";
        if (_notice != null) _notice.Text = RefusalMessage;
    }

    /// <summary>Same path as pressing keys 1-5 (also used by tests/shots).</summary>
    public void SimulateKeyIndex(int idx)
    {
        if (!Visible || idx < 0 || idx >= Classes.Length) return;
        var info = Classes[idx];
        if (IsServerSupported(info)) Choose(info.Id);
        else ShowRefusal(info);
    }

    public override void _UnhandledInput(InputEvent e)
    {
        if (!Visible) return;
        if (e is InputEventKey k && k.Pressed && !k.Echo)
        {
            int idx = k.Keycode switch
            {
                Key.Key1 => 0, Key.Key2 => 1, Key.Key3 => 2, Key.Key4 => 3, Key.Key5 => 4,
                _ => -1
            };
            if (idx >= 0) SimulateKeyIndex(idx);
        }
    }
}
