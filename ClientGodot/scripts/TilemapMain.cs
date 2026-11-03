using Godot;
using System;
using System.Linq;

/// <summary>
/// Tilemap test scene root: Bến Mưa strip 000_064 as real TileMapLayers
/// (built by BenMuaTilemapBuilder from converted tiledata) + the same
/// player as the first prototype. Modes:
///   --tilemtest : automated checks (counts, water block, footprint block,
///                 open walk) — run headless.
///   --tilemshot : walk briefly near the dock plaza and save a screenshot.
/// </summary>
public partial class TilemapMain : Node2D
{
    private PlayerController2D _player;
    private BenMuaTilemapBuilder _builder;

    public override void _Ready()
    {
        _player = GetNode<PlayerController2D>("Player");
        _builder = GetNode<BenMuaTilemapBuilder>("TilemapBuilder");

        if (OS.GetCmdlineUserArgs().Contains("--tilemtest"))
            _ = RunTests();
        else if (OS.GetCmdlineUserArgs().Contains("--tilemshot"))
            _ = RunShot();
    }

    private int _failures;
    private void Check(string name, bool ok, string detail = "")
    {
        GD.Print($"TILEMTEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _failures++;
    }

    private async System.Threading.Tasks.Task WaitPhysicsFrames(int n)
    {
        for (int i = 0; i < n; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private static Vector2 CellCenter(int c, int r) => new((c + 0.5f) * 16f, (r + 0.5f) * 16f);

    private async System.Threading.Tasks.Task Teleport(int c, int r)
    {
        _player.SetMoveInput(Vector2.Zero, false);
        _player.GlobalPosition = CellCenter(c, r);
        _player.Velocity = Vector2.Zero;
        await WaitPhysicsFrames(3);
    }

    private async System.Threading.Tasks.Task RunTests()
    {
        await WaitPhysicsFrames(5);

        // 1. Counts straight from the converted tiledata.
        Check("grid_80x60", _builder.Cols == 80 && _builder.Rows == 60, $"{_builder.Cols}x{_builder.Rows}");
        Check("unique_tiles_16", _builder.UniqueTiles == 16, $"={_builder.UniqueTiles}");
        Check("layer_ground_3160", _builder.LayerCounts["GroundLayer"] == 3160, $"={_builder.LayerCounts["GroundLayer"]}");
        Check("layer_water_800", _builder.LayerCounts["WaterLayer"] == 800, $"={_builder.LayerCounts["WaterLayer"]}");
        Check("layer_path_840", _builder.LayerCounts["PathLayer"] == 840, $"={_builder.LayerCounts["PathLayer"]}");
        Check("blocked_1008", _builder.BlockedCount == 1008, $"={_builder.BlockedCount}");
        int usedVisual = _builder.GroundLayer.GetUsedCells().Count;
        Check("tilemap_cells_match", usedVisual == 3160, $"ground used={usedVisual}");

        // 2. Data sanity for the two collision cases below.
        Check("data_water_blocked", _builder.IsBlockedCell(30, 50) && !_builder.IsBlockedCell(30, 49));
        Check("data_footprint_grass_blocked", _builder.IsBlockedCell(64, 30) && !_builder.IsBlockedCell(61, 30),
            "cell (64,30) is a grass tile but blocked=1 in tiledata");

        // 3. Water blocks: from dock edge (30,48) walk south 1.5 s.
        //    Unobstructed would be +96 px; the water line is at y=800.
        await Teleport(30, 48);
        float y0 = _player.GlobalPosition.Y;
        _player.SetMoveInput(Vector2.Down, false);
        await WaitPhysicsFrames(90);
        _player.SetMoveInput(Vector2.Zero, false);
        float y1 = _player.GlobalPosition.Y;
        Check("water_stops_player", y1 > y0 + 15 && y1 < 802, $"y {y0} -> {y1} (water edge 800)");

        // 4. Footprint blocks: from (61,30) walk east 1.5 s toward the
        //    grass-looking but blocked cell (64,30); wall at x=1024,
        //    player half-width 12 -> stop near x=1012.
        await Teleport(61, 30);
        float x0 = _player.GlobalPosition.X;
        _player.SetMoveInput(Vector2.Right, false);
        await WaitPhysicsFrames(90);
        _player.SetMoveInput(Vector2.Zero, false);
        float x1 = _player.GlobalPosition.X;
        Check("footprint_stops_player", x1 > x0 + 20 && x1 < 1015, $"x {x0} -> {x1} (wall 1024)");

        // 5. Open grass walks freely: (22,25) east 1 s = ~64 px.
        await Teleport(22, 25);
        x0 = _player.GlobalPosition.X;
        _player.SetMoveInput(Vector2.Right, false);
        await WaitPhysicsFrames(60);
        _player.SetMoveInput(Vector2.Zero, false);
        x1 = _player.GlobalPosition.X;
        Check("open_walk_free", Math.Abs((x1 - x0) - 64f) < 4, $"moved {x1 - x0:0.0} px");

        GD.Print(_failures == 0 ? "TILEMTEST RESULT: PASS" : $"TILEMTEST RESULT: FAIL ({_failures})");
        GetTree().Quit(_failures == 0 ? 0 : 1);
    }

    private async System.Threading.Tasks.Task RunShot()
    {
        await Teleport(21, 41); // path/plaza west of spawn anchor 18-24 WU
        _player.SetMoveInput(new Vector2(1, 1), false);
        await WaitPhysicsFrames(24);
        _player.SetMoveInput(Vector2.Zero, false);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_tilemap.png");
        image.SavePng(path);
        GD.Print($"TILEMSHOT SAVED: {path} size={image.GetSize()}");
        GetTree().Quit(0);
    }
}
