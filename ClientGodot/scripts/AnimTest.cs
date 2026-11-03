using Godot;
using System.Linq;
using System.Threading.Tasks;

/// <summary>
/// Automated checks for the full 128-clip Minh Kiem library (16 actions x
/// 8 directions, table copied 1-1 from the Unity setup on PR #22):
/// library size, per-action frame counts / fps / loop flags, PlayAction
/// semantics (one-shot auto-clear, Death/Fall hold, ClearAction, unknown
/// id ignored), and real run clips in locomotion.
/// Modes: --animtest (assertions), --animshot (attack screenshot).
/// </summary>
public partial class AnimTest : Node2D
{
    private int _pass, _fail;
    private DirectionalAnimator2D _anim;
    private PlayerController2D _player;
    private AnimatedSprite2D _sprite;

    public override void _Ready()
    {
        _anim = GetNode<DirectionalAnimator2D>("Player/DirectionalAnimator2D");
        _player = GetNode<PlayerController2D>("Player");
        _sprite = GetNode<AnimatedSprite2D>("Player/AnimatedSprite2D");
        var args = OS.GetCmdlineUserArgs();
        if (args.Contains("--animtest")) _ = RunTest();
        else if (args.Contains("--animshot")) _ = RunShot();
    }

    private async Task Frames(int n)
    {
        for (int i = 0; i < n; i++)
            await ToSignal(GetTree(), SceneTree.SignalName.ProcessFrame);
    }

    private async Task RunTest()
    {
        await Frames(5);
        var lib = _anim.Library;

        Check("library_128", _anim.SpriteFramesAnimationCount == 128,
            _anim.SpriteFramesAnimationCount.ToString());
        Check("frames_walk_SE_6", lib.GetFrameCount("walk_SE") == 6);
        Check("frames_run_E_6", lib.GetFrameCount("run_E") == 6);
        Check("frames_attack1_N_5", lib.GetFrameCount("attack1_N") == 5);
        Check("frames_hurt_S_2", lib.GetFrameCount("hurt_S") == 2);
        Check("frames_skill3_NW_6", lib.GetFrameCount("skill3_NW") == 6);
        Check("frames_death_NE_4", lib.GetFrameCount("death_NE") == 4);
        Check("frames_interact_W_4", lib.GetFrameCount("interact_W") == 4);
        Check("fps_idle_6", Mathf.Abs(lib.GetAnimationSpeed("idle_S") - 6f) < 0.01f);
        Check("fps_walk_8", Mathf.Abs(lib.GetAnimationSpeed("walk_S") - 8f) < 0.01f);
        Check("fps_run_12", Mathf.Abs(lib.GetAnimationSpeed("run_S") - 12f) < 0.01f);
        Check("fps_attack2_12", Mathf.Abs(lib.GetAnimationSpeed("attack2_S") - 12f) < 0.01f);
        Check("loop_walk", lib.GetAnimationLoop("walk_S"));
        Check("loop_fall", lib.GetAnimationLoop("fall_S"));
        Check("noloop_attack1", !lib.GetAnimationLoop("attack1_S"));
        Check("noloop_death", !lib.GetAnimationLoop("death_S"));

        Check("starts_idle_S", _anim.CurrentAnimation == "idle_S", _anim.CurrentAnimation);

        // One-shot: Attack1 (id 3, 5f @12 = 0.42 s) auto-clears.
        _anim.PlayAction(3);
        Check("attack1_plays", _anim.CurrentActionId == 3 && _anim.CurrentAnimation == "attack1_S",
            _anim.CurrentAnimation);
        await Task.Delay(900);
        await Frames(3);
        Check("attack1_autoclears", _anim.CurrentActionId == -1 && _anim.CurrentAnimation == "idle_S",
            $"id={_anim.CurrentActionId} anim={_anim.CurrentAnimation}");

        // Death (id 1) holds after finishing until ClearAction.
        _anim.PlayAction(1);
        await Task.Delay(900);
        await Frames(3);
        Check("death_holds", _anim.CurrentActionId == 1 && _anim.CurrentAnimation == "death_S",
            $"id={_anim.CurrentActionId} anim={_anim.CurrentAnimation}");
        _anim.ClearAction();
        await Frames(3);
        Check("death_clears", _anim.CurrentActionId == -1 && _anim.CurrentAnimation == "idle_S",
            _anim.CurrentAnimation);

        // Fall (id 10) loops and holds.
        _anim.PlayAction(10);
        await Task.Delay(700);
        await Frames(3);
        Check("fall_holds", _anim.CurrentActionId == 10 && _anim.CurrentAnimation == "fall_S",
            $"id={_anim.CurrentActionId} anim={_anim.CurrentAnimation}");
        _anim.ClearAction();
        await Frames(3);

        // Unknown id: ignored, still locomotion.
        _anim.PlayAction(99);
        await Frames(2);
        Check("unknown_id_ignored", _anim.CurrentActionId == -1, _anim.CurrentActionId.ToString());

        // Real run clips in locomotion.
        _player.SetMoveInput(Vector2.Right, running: true);
        await Frames(10);
        Check("run_E_anim", _anim.CurrentAnimation == "run_E", _anim.CurrentAnimation);
        _player.SetMoveInput(Vector2.Zero, running: false);
        await Frames(5);
        Check("back_to_idle_E", _anim.CurrentAnimation == "idle_E", _anim.CurrentAnimation);

        GD.Print($"ANIMTEST: {_pass} passed, {_fail} failed");
        GD.Print(_fail == 0 ? "ANIMTEST RESULT: PASS" : "ANIMTEST RESULT: FAIL");
        GetTree().Quit(_fail == 0 ? 0 : 1);
    }

    private async Task RunShot()
    {
        await Frames(5);
        // Face SE, then swing Attack1; capture mid-swing (~frame 2).
        _player.SetMoveInput(new Vector2(1, 1), running: false);
        await Frames(6);
        _player.SetMoveInput(Vector2.Zero, running: false);
        await Frames(3);
        _anim.PlayAction(3);
        await Task.Delay(170);
        await Frames(2);
        var image = GetViewport().GetTexture().GetImage();
        string path = ProjectSettings.GlobalizePath("res://screenshot_attack.png");
        image.SavePng(path);
        GD.Print($"ANIMSHOT SAVED: {path} anim={_anim.CurrentAnimation} frame={_sprite.Frame}");
        GetTree().Quit(0);
    }

    private void Check(string name, bool ok, object detail = null)
    {
        if (ok) { _pass++; GD.Print($"  PASS {name}"); }
        else { _fail++; GD.Print($"  FAIL {name} :: {detail}"); }
    }
}
