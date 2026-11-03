using Godot;

/// <summary>
/// TEMPORARY placeholder NPC built from the owner-supplied
/// "Fantasy Party Sprites" draft pack (~/workspace/user/fantasy-party-sprites/).
/// Owner decision 2026-11-01: use the pack ONLY as placeholder NPCs in this
/// prototype — it is single-direction (front), 6 frames per action, AI-generated
/// draft art with no license file, and it does NOT meet the locked Ngũ Mạch
/// standard (8 directions, class weapons, sharp pixel art). Never promote
/// these sprites to production assets; replace them with the real Bến Mưa
/// NPC set before any production use.
///
/// Sheet layout (per the pack README): 6 columns x 4 rows of 64x64 cells;
/// rows are idle, walk, run, attack. The node's origin is the feet point.
/// </summary>
public partial class PlaceholderNpc : Node2D
{
    [Export] public string SheetPath { get; set; } = "";
    [Export] public string DisplayName { get; set; } = "NPC";
    [Export] public string StartAnim { get; set; } = "idle";
    [Export] public bool Flip { get; set; } = false;

    private static readonly string[] RowAnims = { "idle", "walk", "run", "attack" };

    public override void _Ready()
    {
        var texture = GD.Load<Texture2D>(SheetPath);
        if (texture == null)
        {
            GD.PushWarning($"PlaceholderNpc {DisplayName}: cannot load {SheetPath}");
            return;
        }

        var frames = new SpriteFrames();
        frames.RemoveAnimation("default");
        for (int row = 0; row < 4; row++)
        {
            string anim = RowAnims[row];
            frames.AddAnimation(anim);
            frames.SetAnimationLoop(anim, true);
            frames.SetAnimationSpeed(anim, anim == "idle" ? 5.0 : 7.0);
            for (int col = 0; col < 6; col++)
            {
                var atlas = new AtlasTexture
                {
                    Atlas = texture,
                    Region = new Rect2(col * 64, row * 64, 64, 64),
                };
                frames.AddFrame(anim, atlas);
            }
        }

        var sprite = new AnimatedSprite2D
        {
            SpriteFrames = frames,
            TextureFilter = TextureFilterEnum.Nearest,
            Offset = new Vector2(0, -32),
            FlipH = Flip,
            ZIndex = 10,
        };
        AddChild(sprite);
        sprite.Play(StartAnim);

        var label = new Label
        {
            Text = $"{DisplayName} (placeholder)",
            Position = new Vector2(-70, -86),
            Size = new Vector2(140, 12),
            HorizontalAlignment = HorizontalAlignment.Center,
            ZIndex = 11,
        };
        label.AddThemeFontSizeOverride("font_size", 9);
        label.AddThemeColorOverride("font_color", new Color(1, 1, 1, 0.85f));
        label.AddThemeColorOverride("font_shadow_color", new Color(0, 0, 0, 0.8f));
        label.AddThemeConstantOverride("shadow_offset_x", 1);
        label.AddThemeConstantOverride("shadow_offset_y", 1);
        AddChild(label);
    }
}
