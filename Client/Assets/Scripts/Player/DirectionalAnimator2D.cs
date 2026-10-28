using UnityEngine;

/// <summary>
/// Feeds the 8-direction walk Animator from <see cref="PlayerController2D"/>.
/// Animator contract (built by MinhKiemCharacterSetup):
///   DirIndex (int)  - sheet row: 0=N, 1=NE, 2=E, 3=SE, 4=S, 5=SW, 6=W, 7=NW
///   IsMoving (bool) - true while the player has movement input
/// When idle the last walk state is kept (idle clips arrive with the next art batch).
/// </summary>
[RequireComponent(typeof(Animator))]
[RequireComponent(typeof(PlayerController2D))]
[DisallowMultipleComponent]
public sealed class DirectionalAnimator2D : MonoBehaviour
{
    private static readonly int DirIndexId = Animator.StringToHash("DirIndex");
    private static readonly int IsMovingId = Animator.StringToHash("IsMoving");

    private Animator animator;
    private PlayerController2D controller;

    private void Awake()
    {
        animator = GetComponent<Animator>();
        controller = GetComponent<PlayerController2D>();
    }

    private void Update()
    {
        animator.SetInteger(DirIndexId, DirectionIndex(controller.FacingDirection));
        animator.SetBool(IsMovingId, controller.IsMoving);
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
