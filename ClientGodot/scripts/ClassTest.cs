using Godot;
using System.Linq;
using System.Threading.Tasks;

/// <summary>
/// Checks for the four non-Minh-Kiem class libraries (Anh Dao, Huyen But,
/// Thach Chuy, Linh Cung — v2 sheets, base set idle/walk/attack1/hurt/
/// death = 40 clips each, same frame counts/fps as Minh Kiem's matching
/// actions). Per class: library size, frame counts, attack1 auto-clear,
/// missing-action PlayAction ignored (attack2 does not exist for them),
/// death hold + ClearAction, and the run fallback (walk at 1.6x speed —
/// these classes have no run sheet yet).
/// --classshot saves the lineup (idle, then all attacking SE).
/// </summary>
public partial class ClassTest : Node2D
{
    private static readonly string[] Classes = { "anh_dao", "huyen_but", "thach_chuy", "linh_cung" };
    private int _pass, _fail;

    public override void _Ready()
    {
        var args = OS.GetCmdlineUserArgs();
        if (args.Contains("--classtest")) _ = RunTest();
        else if (args.Contains("--classshot")) _ = RunShot();
    }

    private async Task Frames(int n)
    {
        for (int i = 0; i < n; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
    }

    private (DirectionalAnimator2D anim, PlayerController2D ctrl, AnimatedSprite2D sprite) Rig(string cls)
    {
        var body = GetNode<CharacterBody2D>(cls);
        return (body.GetNode<DirectionalAnimator2D>("DirectionalAnimator2D"),
                body.GetNode<PlayerController2D>("."),
                body.GetNode<AnimatedSprite2D>("AnimatedSprite2D"));
    }

    private async Task RunTest()
    {
        await Frames(5);
        foreach (var cls in Classes)
        {
            var (anim, ctrl, sprite) = Rig(cls);
            var lib = anim.Library;
            Check($"{cls}_library_40", anim.SpriteFramesAnimationCount == 40,
                anim.SpriteFramesAnimationCount.ToString());
            Check($"{cls}_frames", lib.GetFrameCount("idle_S") == 4 && lib.GetFrameCount("walk_SE") == 6
                && lib.GetFrameCount("attack1_N") == 5 && lib.GetFrameCount("hurt_S") == 2
                && lib.GetFrameCount("death_NE") == 4);
            Check($"{cls}_fps", Mathf.Abs(lib.GetAnimationSpeed("walk_S") - 8f) < 0.01f
                && Mathf.Abs(lib.GetAnimationSpeed("attack1_S") - 12f) < 0.01f);

            anim.PlayAction(3);
            Check($"{cls}_attack1_plays", anim.CurrentActionId == 3 && anim.CurrentAnimation == "attack1_S",
                anim.CurrentAnimation);
            await Task.Delay(900);
            await Frames(3);
            Check($"{cls}_attack1_autoclears", anim.CurrentActionId == -1 && anim.CurrentAnimation == "idle_S",
                $"id={anim.CurrentActionId} anim={anim.CurrentAnimation}");

            anim.PlayAction(4); // attack2: not in this class's set
            await Frames(2);
            Check($"{cls}_missing_action_ignored", anim.CurrentActionId == -1,
                anim.CurrentActionId.ToString());

            anim.PlayAction(1);
            await Task.Delay(900);
            await Frames(3);
            Check($"{cls}_death_holds", anim.CurrentActionId == 1 && anim.CurrentAnimation == "death_S",
                anim.CurrentAnimation);
            anim.ClearAction();
            await Frames(3);
            Check($"{cls}_death_clears", anim.CurrentActionId == -1 && anim.CurrentAnimation == "idle_S",
                anim.CurrentAnimation);

            ctrl.SetMoveInput(Vector2.Right, running: true);
            await Frames(10);
            Check($"{cls}_run_fallback_walkE_1.6x",
                anim.CurrentAnimation == "walk_E" && Mathf.Abs(sprite.SpeedScale - 1.6f) < 0.05f,
                $"{anim.CurrentAnimation} x{sprite.SpeedScale:0.0}");
            ctrl.SetMoveInput(Vector2.Zero, running: false);
            await Frames(5);
            Check($"{cls}_back_to_idle", anim.CurrentAnimation == "idle_E" && Mathf.Abs(sprite.SpeedScale - 1f) < 0.05f,
                anim.CurrentAnimation);
        }
        GD.Print($"CLASSTEST: {_pass} passed, {_fail} failed");
        GD.Print(_fail == 0 ? "CLASSTEST RESULT: PASS" : "CLASSTEST RESULT: FAIL");
        GetTree().Quit(_fail == 0 ? 0 : 1);
    }

    private async Task RunShot()
    {
        await Frames(5);
        foreach (var cls in Classes)
        {
            var (_, ctrl, _) = Rig(cls);
            ctrl.SetMoveInput(new Vector2(1, 1), running: false);
        }
        await Frames(6);
        foreach (var cls in Classes)
        {
            var (_, ctrl, _) = Rig(cls);
            ctrl.SetMoveInput(Vector2.Zero, running: false);
        }
        await Frames(3);
        SaveShot("res://screenshot_classes_idle.png");
        foreach (var cls in Classes) Rig(cls).anim.PlayAction(3);
        await Task.Delay(170);
        await Frames(2);
        SaveShot("res://screenshot_classes.png");
        GD.Print("CLASSSHOT SAVED");
        GetTree().Quit(0);
    }

    private void SaveShot(string resPath)
    {
        var image = GetViewport().GetTexture().GetImage();
        image.SavePng(ProjectSettings.GlobalizePath(resPath));
    }

    private void Check(string name, bool ok, object detail = null)
    {
        if (ok) { _pass++; GD.Print($"  PASS {name}"); }
        else { _fail++; GD.Print($"  FAIL {name} :: {detail}"); }
    }
}
