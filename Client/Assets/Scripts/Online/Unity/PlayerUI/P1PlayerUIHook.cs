// AG1 — P1OnlinePanel composition hook: opens/closes PlayerUIRoot panel set.
// This is a MINIMAL hook — only adds panel open/close to the existing HUD.
// Does NOT rewrite HUD, combat, polling, audio, or input pump.
// Review by Codex before connecting to engine.
// Owner: Antigravity Remote — Issue #80, #85.

using NguMach.Client.Presentation;
using UnityEngine;
using UnityEngine.UIElements;

namespace NguMach.Client.P1
{
    /// <summary>
    /// Composition hook component placed alongside <see cref="P1OnlinePanel"/>.
    /// Manages the <see cref="PlayerUIRoot"/> lifecycle; wired via inspector references.
    /// P1OnlinePanel calls <see cref="OpenPlayerUI"/> / <see cref="ClosePlayerUI"/>.
    /// </summary>
    [DisallowMultipleComponent]
    public sealed class P1PlayerUIHook : MonoBehaviour
    {
        [SerializeField] private PlayerUIRoot playerUIRoot;
        [SerializeField] private UIDocument playerUIDocument;

        private IP1UIAdapter _adapter;

        /// <summary>
        /// Call from P1OnlinePanel.Open after P1Client is ready.
        /// Idempotent (OPC-13 A): calling again with the same adapter/document keeps the live composition;
        /// a rebind closes the previous composition first so no stale view/pin/session survives.
        /// </summary>
        public void Initialize(IP1UIAdapter adapter, UIDocument injectedDoc = null)
        {
            if (adapter == null) return;
            var doc = injectedDoc ?? playerUIDocument;

            if (playerUIRoot == null)
            {
                playerUIRoot = GetComponentInChildren<PlayerUIRoot>();
                if (playerUIRoot == null)
                {
                    playerUIRoot = PlayerUIFactory.Create(gameObject, doc);
                }
            }

            if (ReferenceEquals(_adapter, adapter) && playerUIRoot != null && playerUIRoot.IsInitialized(doc))
            {
                return; // Same session; nothing to rebind.
            }

            if (_adapter != null)
            {
                playerUIRoot.Close(); // Drop previous view/pin/state before rebinding (OPC-13 A lifecycle).
            }
            _adapter = adapter;

            playerUIRoot.HandleEscapeInput = false; // Single Escape owner: P1OnlinePanel dispatches Escape
            playerUIRoot.Initialize(_adapter, doc);
        }

        /// <summary>Open a specific player panel (inventory, map, character, etc.).</summary>
        public void OpenPanel(PlayerPanel panel)
        {
            if (playerUIRoot == null || _adapter == null) return;
            playerUIRoot.OpenPanel(panel);
        }

        public void OpenWithNpc(string targetId)
        {
            if (playerUIRoot == null || _adapter == null || string.IsNullOrEmpty(targetId)) return;
            playerUIRoot.OpenWithNpc(targetId);
        }

        /// <summary>Close all player panels.</summary>
        public void CloseAllPanels()
        {
            if (playerUIRoot == null) return;
            playerUIRoot.CloseAll();
        }

        /// <summary>Close topmost player panel.</summary>
        public void CloseTopPanel()
        {
            if (playerUIRoot == null) return;
            playerUIRoot.CloseTop();
        }

        /// <summary>Dispose and release full UI lifetime on parent close / session tear down (AGR2-05).</summary>
        public void Dispose()
        {
            if (playerUIRoot != null)
            {
                playerUIRoot.Close();
            }
            _adapter = null;
        }

        /// <summary>True if any player panel is open (used by P1OnlinePanel.ModalOpen).</summary>
        public bool IsAnyPanelOpen => playerUIRoot != null && playerUIRoot.IsAnyOpen;

        /// <summary>True if any router panel is open and NO cinematic is running (modal orchestrator probe, OPC-13).</summary>
        public bool HasAnyPanelOpen => playerUIRoot != null && playerUIRoot.HasAnyPanelOpen;

        /// <summary>True while the cinematic overlay is playing (modal orchestrator probe, OPC-13).</summary>
        public bool CinemaPlaying => playerUIRoot != null && playerUIRoot.CinemaPlaying;

        /// <summary>Skip the running cinematic without touching panels (modal orchestrator handler, OPC-13).</summary>
        public void SkipCinema()
        {
            if (playerUIRoot != null) playerUIRoot.SkipCinema();
        }

        private void OnDestroy() => Dispose();
    }
}
