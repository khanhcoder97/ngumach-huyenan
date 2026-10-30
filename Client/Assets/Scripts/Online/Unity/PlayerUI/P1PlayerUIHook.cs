// AG1 — P1OnlinePanel composition hook: opens/closes PlayerUIRoot panel set.
// This is a MINIMAL hook — only adds panel open/close to the existing HUD.
// Does NOT rewrite HUD, combat, polling, audio, or input pump.
// Review by Codex before connecting to engine.
// Owner: Antigravity Remote — Issue #80.

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

        /// <summary>Call from P1OnlinePanel.Open after P1Client is ready.</summary>
        public void Initialize(IP1UIAdapter adapter)
        {
            _adapter = adapter;
            if (playerUIRoot == null)
            {
                Debug.LogError("[P1PlayerUIHook] PlayerUIRoot not assigned. Assign via Inspector.");
                return;
            }
            playerUIRoot.Initialize(_adapter);
        }

        /// <summary>Open a specific player panel (inventory, map, etc.).</summary>
        public void OpenPanel(PlayerPanel panel)
        {
            if (playerUIRoot == null || _adapter == null) return;
            playerUIRoot.OpenPanel(panel);
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

        /// <summary>True if any player panel is open (used by P1OnlinePanel.ModalOpen).</summary>
        public bool IsAnyPanelOpen => playerUIRoot != null && playerUIRoot.IsAnyOpen;

        private void OnDestroy() => playerUIRoot?.CloseAll();
    }
}
