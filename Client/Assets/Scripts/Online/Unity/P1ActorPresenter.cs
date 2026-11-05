using System.Collections.Generic;
using UnityEngine;

namespace NguMach.Client.P1
{
    // Isolated presentation adapter: never edits Muse's Animator, clips, prefab or builder.
    public sealed class P1ActorPresenter : MonoBehaviour
    {
        private PlayerController2D localController;
        private DirectionalAnimator2D localAnimator;
        private Rigidbody2D body;
        private Animator animator;
        private bool controllerEnabled, animatorEnabled;
        private Vector2 oldPosition;
        private Vector3 oldTransform;
        private RigidbodyType2D oldBodyType;
        private bool moved;
        private bool bound;
        private Vector2 facing = Vector2.down;
        private readonly HashSet<int> parameters = new HashSet<int>();
        public Vector2 Facing { get { return facing; } }

        public void Bind()
        {
            oldTransform = transform.position;
            bound = true;
            localController = GetComponent<PlayerController2D>();
            localAnimator = GetComponent<DirectionalAnimator2D>();
            body = GetComponent<Rigidbody2D>();
            animator = GetComponent<Animator>();
            if (localController != null) { controllerEnabled = localController.enabled; localController.enabled = false; }
            if (localAnimator != null) { animatorEnabled = localAnimator.enabled; localAnimator.enabled = false; }
            if (body != null) { oldPosition = body.position; oldBodyType = body.bodyType; body.linearVelocity = Vector2.zero; body.bodyType = RigidbodyType2D.Kinematic; }
            if (animator != null) foreach (var p in animator.parameters) parameters.Add(p.nameHash);
        }
        public void Apply(P1World world)
        {
            var pos = new Vector2((float)world.self.x, (float)world.self.y);
            Vector2 previous = body != null ? body.position : (Vector2)transform.position;
            var delta = pos - previous;
            moved = delta.sqrMagnitude > 0.0001f;
            if (moved) facing = delta.normalized;
            if (body != null) body.position = pos;
            transform.position = new Vector3(pos.x, pos.y, oldTransform.z);
            if (animator != null)
            {
                if (parameters.Contains(Animator.StringToHash("DirIndex"))) animator.SetInteger("DirIndex", DirectionalAnimator2D.DirectionIndex(facing));
                if (parameters.Contains(Animator.StringToHash("IsMoving"))) animator.SetBool("IsMoving", moved);
            }
        }
        public void SetIdle()
        {
            if (animator != null && parameters.Contains(Animator.StringToHash("IsMoving"))) animator.SetBool("IsMoving", false);
        }
        public void Release()
        {
            if (!bound) return;
            bound = false;
            if (body != null) { body.linearVelocity = Vector2.zero; body.bodyType = oldBodyType; body.position = oldPosition; }
            transform.position = oldTransform;
            if (localController != null) localController.enabled = controllerEnabled;
            if (localAnimator != null) localAnimator.enabled = animatorEnabled;
        }
        private void OnDestroy() { Release(); }
    }
}
