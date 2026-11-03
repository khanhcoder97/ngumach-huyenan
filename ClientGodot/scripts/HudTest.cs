using Godot;
using System.Linq;

/// <summary>
/// Automated checks for the board-06 HUD (run: HudTest.tscn -- --hudtest).
/// Covers the functional contract: vitals fractions, cooldown timing per
/// the round-2 spec, joystick vector math + active fade-in, minimap
/// window clamping. Button presses are covered by construction (Godot
/// TextureButton) + the visual online screenshot.
/// </summary>
public partial class HudTest : Node2D
{
    private int _pass, _fail;

    public override async void _Ready()
    {
        if (!OS.GetCmdlineUserArgs().Contains("--hudtest")) return;
        var hud = GetNode<Hud>("GameHud");
        await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);

        // --- vitals fractions ---
        hud.SetVitals(37, 100, 20, 50);
        Check("hp frac 0.37", Mathf.Abs((float)hud.HpFrac - 0.37f) < 0.001f, hud.HpFrac.ToString("0.00"));
        Check("mp frac 0.40", Mathf.Abs((float)hud.MpFrac - 0.40f) < 0.001f, hud.MpFrac.ToString("0.00"));

        // --- cooldown: skill 3 total 8 s ---
        Check("cd start ok", hud.StartCooldown(2));
        Check("cd restart refused while running", !hud.StartCooldown(2));
        hud.AdvanceTime(4.0);
        Check("cd half after 4s", Mathf.Abs((float)hud.CooldownRemaining(2) - 4f) < 0.6f,
            hud.CooldownRemaining(2).ToString("0.0"));
        Check("cd frac 0.5", Mathf.Abs((float)hud.CooldownFrac(2) - 0.5f) < 0.08f,
            hud.CooldownFrac(2).ToString("0.00"));
        hud.AdvanceTime(10.0);
        Check("cd finished", hud.CooldownRemaining(2) == 0);

        // --- joystick vector math (local coords, centre 39,39, radius 30) ---
        hud.SimulateJoystickDrag(new Vector2(39 + 30, 39));
        Check("joy east = (1,0)", hud.JoystickVector.DistanceTo(Vector2.Right) < 0.05f,
            hud.JoystickVector.ToString());
        hud.SimulateJoystickDrag(new Vector2(39, 39 + 15));
        Check("joy south half", hud.JoystickVector.DistanceTo(new Vector2(0, 0.5f)) < 0.05f,
            hud.JoystickVector.ToString());
        // Active texture fades in while dragging (~300 ms).
        for (int i = 0; i < 40 && hud.JoystickActiveAlpha < 0.9; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
        Check("joy active alpha > 0.9", hud.JoystickActiveAlpha > 0.9,
            hud.JoystickActiveAlpha.ToString("0.00"));
        hud.SimulateJoystickRelease();
        Check("joy released = zero", hud.JoystickVector == Vector2.Zero);

        // --- minimap window clamping ---
        hud.SetMinimapCenter(18, 0);
        var r1 = hud.MinimapRegion;
        Check("minimap spawn origin (0,0)", r1.Position == Vector2.Zero, r1.ToString());
        Check("minimap window 1120x960", r1.Size == new Vector2(1120, 960), r1.Size.ToString());
        hud.SetMinimapCenter(180, 12);
        var r2 = hud.MinimapRegion;
        Check("minimap mid origin x 3040", Mathf.Abs(r2.Position.X - 3040) < 0.5f, r2.ToString());
        hud.SetMinimapCenter(359, -11);
        var r3 = hud.MinimapRegion;
        Check("minimap far corner clamped", Mathf.Abs(r3.Position.X - (7200 - 1120)) < 0.5f && r3.Position.Y == 0,
            r3.ToString());

        GD.Print($"HUDTEST: {_pass} passed, {_fail} failed");
        GD.Print(_fail == 0 ? "HUDTEST RESULT: PASS" : "HUDTEST RESULT: FAIL");
        GetTree().Quit();
    }

    private void Check(string name, bool ok, object detail = null)
    {
        if (ok) { _pass++; GD.Print($"  PASS {name}"); }
        else { _fail++; GD.Print($"  FAIL {name} :: {detail}"); }
    }
}
