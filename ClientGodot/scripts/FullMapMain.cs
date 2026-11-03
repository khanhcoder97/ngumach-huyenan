using Godot;
using System;
using System.Linq;

/// <summary>
/// Full-map scene: all 6 Bến Mưa strips merged into one tilemap
/// (450x60 cells = 360x48 WU) by tools/convert_full_map.py, loaded by the
/// same BenMuaTilemapBuilder with different DataPath/AtlasPath exports.
/// Modes:
///   --fulltest : counts vs BM audit (27,000 / water 4,960 / blocked 5,375),
///                walk across all 5 seams on path rows, river collision in
///                strip 192-256, east-gate passage (348 WU) stays open,
///                boss-arena floor (178 WU) walks freely.
///   --fullshot : screenshot standing in the boss arena.
/// </summary>
public partial class FullMapMain : Node2D
{
    private PlayerController2D _player;
    private BenMuaTilemapBuilder _builder;

    public override void _Ready()
    {
        _player = GetNode<PlayerController2D>("Player");
        _builder = GetNode<BenMuaTilemapBuilder>("TilemapBuilder");
        if (OS.GetCmdlineUserArgs().Contains("--fulltest"))
            _ = RunTests();
        else if (OS.GetCmdlineUserArgs().Contains("--fullshot"))
            _ = RunShot();
    }

    private int _failures;
    private void Check(string name, bool ok, string detail = "")
    {
        GD.Print($"FULLTEST {(ok ? "PASS" : "FAIL")}: {name} {detail}");
        if (!ok) _failures++;
    }

    private async System.Threading.Tasks.Task WaitPhysicsFrames(int n)
    {
        for (int i = 0; i < n; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.PhysicsFrame);
    }

    private static Vector2 CellCenter(int c, int r) => new((c + 0.5f) * 16f, (r + 0.5f) * 16f);
    private static int CellColOf(Vector2 p) => (int)(p.X / 16f);

    private async System.Threading.Tasks.Task Teleport(int c, int r)
    {
        _player.SetMoveInput(Vector2.Zero, false);
        _player.GlobalPosition = CellCenter(c, r);
        _player.Velocity = Vector2.Zero;
        await WaitPhysicsFrames(3);
    }

    private async System.Threading.Tasks.Task<float> WalkEast(int fromC, int r, int frames)
    {
        await Teleport(fromC, r);
        float x0 = _player.GlobalPosition.X;
        _player.SetMoveInput(Vector2.Right, false);
        await WaitPhysicsFrames(frames);
        _player.SetMoveInput(Vector2.Zero, false);
        return _player.GlobalPosition.X - x0;
    }

    private async System.Threading.Tasks.Task RunTests()
    {
        await WaitPhysicsFrames(5);

        Check("grid_450x60", _builder.Cols == 450 && _builder.Rows == 60, $"{_builder.Cols}x{_builder.Rows}");
        Check("unique_tiles_47", _builder.UniqueTiles == 47, $"={_builder.UniqueTiles}");
        Check("layer_ground_16879", _builder.LayerCounts["GroundLayer"] == 16879, $"={_builder.LayerCounts["GroundLayer"]}");
        Check("layer_water_4960", _builder.LayerCounts["WaterLayer"] == 4960, $"={_builder.LayerCounts["WaterLayer"]}");
        Check("layer_path_5161", _builder.LayerCounts["PathLayer"] == 5161, $"={_builder.LayerCounts["PathLayer"]}");
        Check("blocked_5375", _builder.BlockedCount == 5375, $"={_builder.BlockedCount}");

        // Walk across every seam on a path row: 2 s east = 128 px from
        // 4 cells west of the seam; an invisible seam wall would show up
        // as a short move or a stop before the far side.
        (int seamCol, int row)[] seams = { (80, 41), (160, 40), (240, 41), (320, 41), (400, 42) };
        foreach (var (seamCol, row) in seams)
        {
            float moved = await WalkEast(seamCol - 4, row, 120);
            int endCol = CellColOf(_player.GlobalPosition);
            Check($"seam_{seamCol * 8 / 10}wu_cross", moved > 120 && endCol > seamCol + 2,
                $"moved={moved:0.0}px endCol={endCol} seamCol={seamCol} row={row}");
        }

        // River collision in strip 192-256: walkable (253..256,10),
        // water blocked from col 257 (wall x=4112, stop near 4100).
        await WalkEast(253, 10, 90);
        float x = _player.GlobalPosition.X;
        Check("river_192_256_blocks", x > 4090 && x < 4102, $"stop x={x:0.0} (wall 4112)");

        // East gate passage at 348 WU (col 435) must stay open on row 41.
        float gateMoved = await WalkEast(430, 41, 120);
        Check("east_gate_open", gateMoved > 120 && CellColOf(_player.GlobalPosition) > 436,
            $"moved={gateMoved:0.0}px endCol={CellColOf(_player.GlobalPosition)}");

        // Boss arena floor at 178 WU (col ~222) walks freely south 1 s.
        await Teleport(222, 33);
        float y0 = _player.GlobalPosition.Y;
        _player.SetMoveInput(Vector2.Down, false);
        await WaitPhysicsFrames(60);
        _player.SetMoveInput(Vector2.Zero, false);
        float movedY = _player.GlobalPosition.Y - y0;
        Check("arena_floor_open", Math.Abs(movedY - 64f) < 4, $"moved {movedY:0.0} px");

        GD.Print(_failures == 0 ? "FULLTEST RESULT: PASS" : $"FULLTEST RESULT: FAIL ({_failures})");
        GetTree().Quit(_failures == 0 ? 0 : 1);
    }

    private async System.Threading.Tasks.Task RunShot()
    {
        await Teleport(219, 32); // NW edge of the boss arena (ring centre 178 WU)
        _player.SetMoveInput(new Vector2(1, 1), false);
        await WaitPhysicsFrames(24);
        _player.SetMoveInput(Vector2.Zero, false);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_fullmap.png");
        image.SavePng(path);
        GD.Print($"FULLSHOT SAVED: {path} size={image.GetSize()}");
        GetTree().Quit(0);
    }
}
