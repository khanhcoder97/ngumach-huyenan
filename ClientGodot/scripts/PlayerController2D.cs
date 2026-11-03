using Godot;
using System;

/// <summary>
/// Godot .NET port of the Unity PlayerController2D (52 lines in Unity).
/// Top-down 8-direction movement. Differences from the Unity version:
///  - CharacterBody2D + Velocity/MoveAndSlide replaces Rigidbody2D.velocity.
///  - Godot 2D units are pixels, so the locked 20 PPU becomes a plain
///    scale factor: moveSpeed 3.2 WU/s = 64 px/s, run x1.6 (full-anim branch).
///  - Godot's Y axis points DOWN (Unity: up). Facing/input use Godot axes;
///    the row mapping in DirectionalAnimator2D compensates for the flip.
/// Input can be injected with SetMoveInput() so headless self-tests can
/// drive the player without a keyboard — the Unity version has no such seam.
/// </summary>
public partial class PlayerController2D : CharacterBody2D
{
    public const float PixelsPerUnit = 20f;
    [Export] public float MoveSpeedWU = 3.2f;
    [Export] public float RunMultiplier = 1.6f;

    private Vector2 _moveInput;
    private bool _runInput;
    private bool _inputInjected;
    private Vector2 _injectedInput;
    private bool _injectedRun;

    /// <summary>Current 8-way facing; defaults to South (front), as in Unity.</summary>
    public Vector2 FacingDirection { get; private set; } = Vector2.Down;
    public bool IsMoving => _moveInput.LengthSquared() > 0.0001f;
    public bool IsRunning => IsMoving && _runInput;

    public void SetMoveInput(Vector2 input, bool running)
    {
        _inputInjected = true;
        _injectedInput = input;
        _injectedRun = running;
    }

    public void ClearInjectedInput() => _inputInjected = false;

    // --- Server-authoritative mode -------------------------------------
    // Online play: the server owns the position (see OnlineMain). When
    // ExternalControl is on, this controller stops simulating movement
    // locally — it only tracks facing/moving state for the animator,
    // driven via SetExternalInput(); OnlineMain moves the body toward
    // the authoritative snapshot position. Default off; local play and
    // the self-tests are unaffected.
    public bool ExternalControl { get; set; }
    private Vector2 _externalInput;

    public void SetExternalInput(Vector2 input)
    {
        _externalInput = input.LengthSquared() > 1f ? input.Normalized() : input;
    }

    public override void _PhysicsProcess(double delta)
    {
        if (ExternalControl)
        {
            _moveInput = _externalInput;
            _runInput = false;
            if (IsMoving)
                FacingDirection = SnapTo8(_moveInput);
            Velocity = Vector2.Zero;
            return; // position is set externally from server snapshots
        }

        if (_inputInjected)
        {
            _moveInput = _injectedInput;
            _runInput = _injectedRun;
        }
        else
        {
            // Arrow keys / WASD via physical keycodes; Shift = run.
            Vector2 raw = Vector2.Zero;
            if (Input.IsPhysicalKeyPressed(Key.Left) || Input.IsPhysicalKeyPressed(Key.A)) raw.X -= 1;
            if (Input.IsPhysicalKeyPressed(Key.Right) || Input.IsPhysicalKeyPressed(Key.D)) raw.X += 1;
            if (Input.IsPhysicalKeyPressed(Key.Up) || Input.IsPhysicalKeyPressed(Key.W)) raw.Y -= 1;
            if (Input.IsPhysicalKeyPressed(Key.Down) || Input.IsPhysicalKeyPressed(Key.S)) raw.Y += 1;
            _moveInput = raw;
            _runInput = Input.IsPhysicalKeyPressed(Key.Shift);
        }

        if (_moveInput.LengthSquared() > 1f)
            _moveInput = _moveInput.Normalized();

        if (IsMoving)
            FacingDirection = SnapTo8(_moveInput);

        float speed = MoveSpeedWU * PixelsPerUnit * (IsRunning ? RunMultiplier : 1f);
        Velocity = _moveInput * speed;
        MoveAndSlide();
    }

    private static Vector2 SnapTo8(Vector2 v)
    {
        float angle = Mathf.Atan2(v.Y, v.X);
        int sector = Mathf.RoundToInt(angle / (Mathf.Pi / 4f));
        float snapped = sector * (Mathf.Pi / 4f);
        return new Vector2(Mathf.Cos(snapped), Mathf.Sin(snapped));
    }
}
