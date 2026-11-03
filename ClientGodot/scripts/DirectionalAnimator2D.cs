using Godot;

/// <summary>
/// Godot .NET port of the Unity DirectionalAnimator2D + MinhKiemCharacterSetup
/// (full-anim branch, PR #22). Unity builds 128 clips (16 actions x 8 dirs)
/// in the editor from a table; here the SpriteFrames library is built in
/// code at startup from the SAME table — values copied 1-1:
///
///   action    frames fps loop  ActionId
///   idle         4    6  yes     - (locomotion)
///   walk         6    8  yes     -
///   run          6   12  yes     -
///   hurt         2    8  no      0
///   death        4    8  no      1  (holds until ClearAction)
///   dodge        4   12  no      2
///   attack1      5   12  no      3
///   attack2      5   12  no      4
///   attack3      5   12  no      5
///   skill1       6   12  no      6
///   skill2       6   12  no      7
///   skill3       6   12  no      8
///   jump         4   12  no      9
///   fall         4    8  YES    10  (loops AND holds until ClearAction)
///   land         4   12  no     11
///   interact     4    8  no     12
///
/// Multi-class: [Export] ClassId selects the sheet folder
/// (assets/chars/<classId>/) and the action table. Minh Kiem has the
/// full 16-action table; the other four classes currently ship the
/// 5-action base set (idle/walk/attack1/hurt/death — same frame counts
/// and fps as Minh Kiem's matching actions, 40 clips each). PlayAction
/// for an action a class does not have is warned + ignored. Classes
/// without a run sheet fall back to walk at 1.6x speed when running.
/// Sheets: rows 0..7 = N, NE, E, SE, S, SW, W, NW; cell 48x64, pivot
/// bottom-center (sprite offset (0,-32), origin = feet). Animation names
/// keep this prototype's lowercase convention ("attack1_SE"); the Unity
/// clip names differ only in casing ("Attack1_SE").
/// PlayAction/ClearAction mirror the Unity API: one-shots auto-clear when
/// the clip finishes; Death and Fall hold until gameplay code clears them.
/// Facing is locked to the direction at trigger time, as in Unity.
/// Y-flip gotcha: Unity's DirectionIndex uses Atan2(y,x) with Y up; Godot
/// Y is down, so Y is negated before the identical sector mapping.
/// </summary>
public partial class DirectionalAnimator2D : Node
{
    private static readonly string[] RowNames = { "N", "NE", "E", "SE", "S", "SW", "W", "NW" };

    /// <summary>Asset folder under res://assets/chars/ + action table key.</summary>
    [Export] public string ClassId = "minh_kiem";

    private sealed record ActionDef(string Name, int Frames, float Fps, bool Loop, int ActionId);
    private static readonly ActionDef[] Actions =
    {
        new("idle",     4,  6f, true,  -1),
        new("walk",     6,  8f, true,  -1),
        new("run",      6, 12f, true,  -1),
        new("hurt",     2,  8f, false,  0),
        new("death",    4,  8f, false,  1),
        new("dodge",    4, 12f, false,  2),
        new("attack1",  5, 12f, false,  3),
        new("attack2",  5, 12f, false,  4),
        new("attack3",  5, 12f, false,  5),
        new("skill1",   6, 12f, false,  6),
        new("skill2",   6, 12f, false,  7),
        new("skill3",   6, 12f, false,  8),
        new("jump",     4, 12f, false,  9),
        new("fall",     4,  8f, true,  10),
        new("land",     4, 12f, false, 11),
        new("interact", 4,  8f, false, 12),
    };

    /// <summary>Base set shipped by Anh Dao / Huyen But / Thach Chuy /
    /// Linh Cung (v2 sheets): the same actions Minh Kiem has, minus the
    /// extended set. ActionIds stay the global ones (hurt 0, death 1,
    /// attack1 3) so gameplay code is class-agnostic.</summary>
    private static readonly ActionDef[] BaseActions =
    {
        new("idle",    4, 6f, true,  -1),
        new("walk",    6, 8f, true,  -1),
        new("hurt",    2, 8f, false,  0),
        new("death",   4, 8f, false,  1),
        new("attack1", 5, 12f, false, 3),
    };

    private ActionDef[] Table => ClassId == "minh_kiem" ? Actions : BaseActions;
    private bool _hasRun;

    private AnimatedSprite2D _sprite;
    private PlayerController2D _controller;
    private string _currentAnim = "";
    private int _currentActionId = -1;
    private int _actionRow;

    public string CurrentAnimation => _currentAnim;
    /// <summary>Currently playing ActionId, or -1 when in locomotion (Unity parity).</summary>
    public int CurrentActionId => _currentActionId;
    public int SpriteFramesAnimationCount => _sprite?.SpriteFrames?.GetAnimationNames().Length ?? 0;
    public SpriteFrames Library => _sprite?.SpriteFrames;

    public override void _Ready()
    {
        _controller = GetParent<PlayerController2D>();
        _sprite = GetNode<AnimatedSprite2D>("../AnimatedSprite2D"); // sibling under Player
        _sprite.SpriteFrames = BuildFrames();
        _sprite.Offset = new Vector2(0, -32); // pivot bottom-center
        _sprite.AnimationFinished += OnAnimationFinished;
        PlayLocomotion(4); // idle S
    }

    /// <summary>Switches the character class at runtime: rebuilds the
    /// SpriteFrames library from that class's sheets/table and returns
    /// to locomotion. Used by the online client's class-select flow.</summary>
    public void SetClass(string classId)
    {
        ClassId = classId;
        _currentActionId = -1;
        _currentAnim = "";
        _sprite.SpriteFrames = BuildFrames();
        PlayLocomotion(DirectionIndex(_controller.FacingDirection));
    }

    /// <summary>Plays an action by its ActionId code (0..12). Unknown ids
    /// are ignored with a warning, as in Unity.</summary>
    public void PlayAction(int actionId)
    {
        var def = System.Array.Find(Table, a => a.ActionId == actionId);
        if (def == null)
        {
            GD.PushWarning($"DirectionalAnimator2D: ActionId {actionId} not available for class {ClassId}");
            return;
        }
        _currentActionId = actionId;
        _actionRow = DirectionIndex(_controller.FacingDirection);
        string name = $"{def.Name}_{RowNames[_actionRow]}";
        _currentAnim = name;
        _sprite.Play(name);
        _sprite.Frame = 0;
        _sprite.FrameProgress = 0;
    }

    /// <summary>Returns control to locomotion (Unity parity).</summary>
    public void ClearAction()
    {
        if (_currentActionId == -1) return;
        _currentActionId = -1;
        _currentAnim = ""; // force locomotion refresh next _Process
    }

    private void OnAnimationFinished()
    {
        // One-shots auto-clear; Death (1) holds on its last frame and
        // Fall (10) loops, so neither reaches here as a "finished" hold.
        if (_currentActionId != -1 && _currentActionId != 1)
            ClearAction();
    }

    public override void _Process(double delta)
    {
        if (_currentActionId != -1) return; // an action owns the sprite
        PlayLocomotion(DirectionIndex(_controller.FacingDirection));
    }

    private void PlayLocomotion(int row)
    {
        string action;
        float scale = 1f;
        if (_controller.IsMoving && _controller.IsRunning)
        {
            if (_hasRun) action = "run";
            else { action = "walk"; scale = 1.6f; } // no run sheet: walk faster
        }
        else if (_controller.IsMoving) action = "walk";
        else action = "idle";
        string name = $"{action}_{RowNames[row]}";
        if (name == _currentAnim && Mathf.Abs(_sprite.SpeedScale - scale) < 0.01f) return;
        _currentAnim = name;
        _sprite.SpeedScale = scale;
        _sprite.Play(name);
    }

    private SpriteFrames BuildFrames()
    {
        var frames = new SpriteFrames();
        frames.RemoveAnimation("default");
        _hasRun = System.Array.Exists(Table, a => a.Name == "run");
        foreach (var def in Table)
        {
            var sheet = GD.Load<Texture2D>($"res://assets/chars/{ClassId}/{def.Name}.png");
            AddSheet(frames, def, sheet);
        }
        return frames;
    }

    private static void AddSheet(SpriteFrames frames, ActionDef def, Texture2D sheet)
    {
        const int cellW = 48, cellH = 64, rows = 8;
        for (int row = 0; row < rows; row++)
        {
            string name = $"{def.Name}_{RowNames[row]}";
            frames.AddAnimation(name);
            frames.SetAnimationSpeed(name, def.Fps);
            frames.SetAnimationLoop(name, def.Loop);
            for (int f = 0; f < def.Frames; f++)
            {
                var atlas = new AtlasTexture
                {
                    Atlas = sheet,
                    Region = new Rect2(f * cellW, row * cellH, cellW, cellH),
                    FilterClip = true
                };
                frames.AddFrame(name, atlas);
            }
        }
    }

    /// <summary>Identical mapping to the Unity version, with Y negated for Godot axes.</summary>
    public static int DirectionIndex(Vector2 facing)
    {
        float degrees = Mathf.Atan2(-facing.Y, facing.X) * 180f / Mathf.Pi;
        int sector = ((Mathf.RoundToInt(degrees / 45f) % 8) + 8) % 8;
        switch (sector)
        {
            case 0: return 2; // E
            case 1: return 1; // NE
            case 2: return 0; // N
            case 3: return 7; // NW
            case 4: return 6; // W
            case 5: return 5; // SW
            case 6: return 4; // S
            default: return 3; // SE
        }
    }
}
