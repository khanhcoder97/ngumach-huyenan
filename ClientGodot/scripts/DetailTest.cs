using Godot;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;

/// <summary>
/// Checks for the detail presentation layers (round-13 composite split by
/// the blocked grid — see tools/build_detail_layers.py):
///   * both overlays load at full-map size, z-order under(5) &lt; player(10)
///     &lt; over(15);
///   * the generator's sample contract holds in the actual textures:
///     under samples are opaque in under + transparent in over, and vice
///     versa (no pixel lives in both layers, under samples sit on
///     walkable cells, over samples on blocked cells);
///   * the player can be placed at the manifest's occlusion spot.
/// --detailshot saves a screenshot at that spot: the blocked prop must
/// visibly cover the player's head (over layer at work).
/// </summary>
public partial class DetailTest : Node2D
{
    private int _pass, _fail;

    public override void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        if (args.Contains("--detailtest")) _ = Run(false);
        else if (args.Contains("--detailshot")) _ = Run(true);
    }

    private async Task Run(bool shot)
    {
        var builder = GetNode<BenMuaTilemapBuilder>("TilemapBuilder");
        var player = GetNode<CharacterBody2D>("Player");
        for (int i = 0; i < 5; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

        string json = FileAccess.GetFileAsString("res://assets/tilemap/full_map/detail_layers.json");
        using var doc = JsonDocument.Parse(json);
        var man = doc.RootElement;

        if (!shot)
        {
            Check("layers_active", builder.DetailLayersActive);
            var under = builder.DetailUnderSprite;
            var over = builder.DetailOverSprite;
            Check("sizes_7200x960",
                under.Texture.GetSize() == new Vector2(7200, 960) &&
                over.Texture.GetSize() == new Vector2(7200, 960));
            Check("z_order", under.ZIndex == 5 && player.ZIndex == 10 && over.ZIndex == 15,
                $"under={under.ZIndex} player={player.ZIndex} over={over.ZIndex}");

            var underImg = under.Texture.GetImage();
            var overImg = over.Texture.GetImage();
            foreach (var s in man.GetProperty("under_samples").EnumerateArray())
            {
                int x = s[0].GetInt32(), y = s[1].GetInt32();
                Check($"under_sample_opaque({x},{y})",
                    underImg.GetPixel(x, y).A > 0.9f && overImg.GetPixel(x, y).A < 0.1f);
                int c = x / 16, r = y / 16;
                Check($"under_sample_walkable({c},{r})", !builder.IsBlockedCell(c, r));
            }
            foreach (var s in man.GetProperty("over_samples").EnumerateArray())
            {
                int x = s[0].GetInt32(), y = s[1].GetInt32();
                Check($"over_sample_opaque({x},{y})",
                    overImg.GetPixel(x, y).A > 0.9f && underImg.GetPixel(x, y).A < 0.1f);
                int c = x / 16, r = y / 16;
                Check($"over_sample_blocked({c},{r})", builder.IsBlockedCell(c, r));
            }
            long up = man.GetProperty("under_px").GetInt64();
            long op = man.GetProperty("over_px").GetInt64();
            Check("coverage_sane", up > 1_000_000 && op > 100_000, $"under={up} over={op}");
        }

        var spot = man.GetProperty("shot_spot").GetProperty("player_px");
        player.GlobalPosition = new Vector2(spot[0].GetInt32(), spot[1].GetInt32());
        for (int i = 0; i < 3; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

        if (shot)
        {
            var image = GetViewport().GetTexture().GetImage();
            string path = ProjectSettings.GlobalizePath("res://screenshot_detail.png");
            image.SavePng(path);
            GD.Print($"DETAILSHOT SAVED: {path} player={player.GlobalPosition}");
            GetTree().Quit(0);
            return;
        }
        Check("player_at_spot", player.GlobalPosition == new Vector2(spot[0].GetInt32(), spot[1].GetInt32()),
            player.GlobalPosition.ToString());
        GD.Print($"DETAILTEST: {_pass} passed, {_fail} failed");
        GD.Print(_fail == 0 ? "DETAILTEST RESULT: PASS" : "DETAILTEST RESULT: FAIL");
        GetTree().Quit(_fail == 0 ? 0 : 1);
    }

    private void Check(string name, bool ok, object detail = null)
    {
        if (ok) { _pass++; GD.Print($"  PASS {name}"); }
        else { _fail++; GD.Print($"  FAIL {name} :: {detail}"); }
    }
}
