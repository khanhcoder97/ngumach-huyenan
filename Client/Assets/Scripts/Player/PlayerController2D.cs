using UnityEngine;

/// <summary>
/// Top-down 8-direction player movement for the prototype character.
/// Reads the legacy Input Manager axes and drives a Rigidbody2D; facing is
/// snapped to 8 directions so the directional animator can pick a sheet row.
/// World units: 1 WU = 20 px (locked pixel standard).
/// </summary>
[RequireComponent(typeof(Rigidbody2D))]
[DisallowMultipleComponent]
public sealed class PlayerController2D : MonoBehaviour
{
    [SerializeField] private float moveSpeed = 3.2f;

    private Rigidbody2D body;
    private Vector2 moveInput;

    /// <summary>Current 8-way facing; defaults to South (front) like the sheet's idle pose.</summary>
    public Vector2 FacingDirection { get; private set; } = Vector2.down;

    public bool IsMoving => moveInput.sqrMagnitude > 0.0001f;

    private void Awake()
    {
        body = GetComponent<Rigidbody2D>();
        body.gravityScale = 0f;
        body.freezeRotation = true;
    }

    private void Update()
    {
        moveInput = new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical"));
        if (moveInput.sqrMagnitude > 1f)
            moveInput.Normalize();

        if (IsMoving)
            FacingDirection = SnapTo8(moveInput);
    }

    private void FixedUpdate()
    {
        body.velocity = moveInput * moveSpeed;
    }

    private static Vector2 SnapTo8(Vector2 v)
    {
        float angle = Mathf.Atan2(v.y, v.x);
        int sector = Mathf.RoundToInt(angle / (Mathf.PI / 4f));
        float snapped = sector * (Mathf.PI / 4f);
        return new Vector2(Mathf.Cos(snapped), Mathf.Sin(snapped));
    }
}
