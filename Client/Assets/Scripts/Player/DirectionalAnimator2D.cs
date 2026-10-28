using UnityEngine;

/// <summary>
/// Feeds the 8-direction Animator from <see cref="PlayerController2D"/> and plays
/// one-shot actions on request. Animator contract (built by MinhKiemCharacterSetup):
///   DirIndex (int)  - sheet row: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
///   IsMoving (bool) - true while the player has movement input
///   IsRunning (bool)- true while the run modifier is held
///   ActionId (int)  - -1 = locomotion; 0 Hurt, 1 Death, 2 Dodge, 3 Attack1,
///                     4 Attack2, 5 Attack3, 6 Skill1 (Phản Quang), 7 Skill2 (Tầm Long),
///                     8 Skill3 (Kiếm Trận), 9 Jump, 10 Fall, 11 Land, 12 Interact
/// One-shot actions auto-clear back to locomotion when their clip finishes.
/// Death (1) and Fall (10) hold until ClearAction() is called by gameplay code.
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(PlayerController2D))]
[DisallowMultipleComponent]
public sealed class DirectionalAnimator2D : MonoBehaviour
{
    private static readonly int DirIndexId = Animator.StringToHash("DirIndex");
    private static readonly int IsMovingId = Animator.StringToHash("IsMoving");
    private static readonly int IsRunningId = Animator.StringToHash("IsRunning");
    private static readonly int ActionIdId = Animator.StringToHash("ActionId");

    // Clip durations (seconds) for one-shot actions, indexed by ActionId.
    // -1 = hold until cleared (Death, Fall). Locomotion is -1 in the other sense
    // (no action); index 0..12 below matches the ActionId codes.
    private static readonly float[] OneShotDurations =
    {
        2f / 8f,   // 0 Hurt
        -1f,       // 1 Death (holds)
        4f / 12f,  // 2 Dodge
        5f / 12f,  // 3 Attack1
        5f / 12f,  // 4 Attack2
        5f / 12f,  // 5 Attack3
        6f / 12f,  // 6 Skill1
        6f / 12f,  // 7 Skill2
        6f / 12f,  // 8 Skill3
        4f / 12f,  // 9 Jump
        -1f,       // 10 Fall (loops until cleared)
        4f / 12f,  // 11 Land
        4f / 8f,   // 12 Interact
    };

    private Animator animator;
    private PlayerController2D controller;
    private int currentAction = -1;
    private float actionStartedAt;

    /// <summary>Currently playing ActionId, or -1 when in locomotion.</summary>
    public int CurrentAction => currentAction;

    private void Awake()
    {
        animator = GetComponent<Animator>();
        controller = GetComponent<PlayerController2D>();
    }

    /// <summary>Plays an action by its ActionId code (see class summary).</summary>
    public void PlayAction(int actionId)
    {
        if (actionId < 0 || actionId >= OneShotDurations.Length)
        {
            Debug.LogWarning($"DirectionalAnimator2D: unknown ActionId {actionId}");
            return;
        }
        currentAction = actionId;
        actionStartedAt = Time.time;
        animator.SetInteger(ActionIdId, actionId);
    }

    /// <summary>Returns control to locomotion (Idle/Walk/Run).</summary>
    public void ClearAction()
    {
        currentAction = -1;
        animator.SetInteger(ActionIdId, -1);
    }

    private void Update()
    {
        animator.SetInteger(DirIndexId, DirectionIndex(controller.FacingDirection));
        animator.SetBool(IsMovingId, controller.IsMoving);
        animator.SetBool(IsRunningId, controller.IsRunning);

        if (currentAction >= 0)
        {
            float duration = OneShotDurations[currentAction];
            if (duration > 0f && Time.time - actionStartedAt >= duration)
                ClearAction();
        }
    }

    /// <summary>Maps a facing vector to the walk sheet row index (N=0 clockwise to NW=7).</summary>
    public static int DirectionIndex(Vector2 facing)
    {
        // Sector 0 = East, counting counter-clockwise in 45-degree steps.
        float degrees = Mathf.Atan2(facing.y, facing.x) * Mathf.Rad2Deg;
        int sector = ((Mathf.RoundToInt(degrees / 45f) % 8) + 8) % 8;

        // sector (E,NE,N,NW,W,SW,S,SE) -> row (2,1,0,7,6,5,4,3)
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
