// PlayerUIRoot — MonoBehaviour gốc điều phối toàn bộ panel PlayerUI.
// Inject IP1UIAdapter, dùng PanelRouter để routing, giữ CancellationTokenSource lifecycle.
// Owner: Antigravity Remote — Issue #80.

using System;
using System.Threading;
using UnityEngine;
using UnityEngine.UIElements;
using NguMach.Client.Presentation;

namespace NguMach.Client.P1
{
    [DisallowMultipleComponent]
    public sealed class PlayerUIRoot : MonoBehaviour
    {
        // ── Inspector ────────────────────────────────────────────────────────
        [SerializeField] private InventoryPanel inventoryPanel;
        [SerializeField] private QuestJournalPanel questJournalPanel;
        [SerializeField] private NpcDialoguePanel npcDialoguePanel;
        [SerializeField] private SettingsPanel settingsPanel;
        [SerializeField] private MapPanel mapPanel;
        [SerializeField] private PlayerUIButtonBar buttonBar;

        // ── Runtime state ────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private UIDocument _doc;
        private PanelRouter _router;
        private CancellationTokenSource _life;
        private bool _closing;

        // ── Public API ───────────────────────────────────────────────────────

        public bool IsAnyOpen => _router != null && _router.IsAnyOpen;

        /// <summary>Called from P1PlayerUIHook after adapter is ready. Finds UIDocument in scene.</summary>
        public void Initialize(IP1UIAdapter adapter)
        {
            var doc = FindFirstObjectByType<UIDocument>();
            if (doc == null) { Debug.LogError("[PlayerUIRoot] No UIDocument found in scene."); return; }
            Open(adapter, doc);
        }

        /// <summary>Close all panels (alias for hook compatibility).</summary>
        public void CloseAll()
        {
            _router?.CloseAll();
            HideAllPanels();
        }

        /// <summary>Open the PlayerUI. Call once per session.</summary>
        public void Open(IP1UIAdapter adapter, UIDocument doc)
        {
            if (_adapter != null) { Debug.LogError("[PlayerUIRoot] Open called twice; call Close first."); return; }
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            _doc = doc ?? throw new ArgumentNullException(nameof(doc));
            _life = new CancellationTokenSource();
            _router = new PanelRouter();
            _router.OnPanelChanged += HandlePanelChanged;

            // Pass references to child panels.
            if (inventoryPanel != null) inventoryPanel.Initialize(_adapter, _router, _life.Token);
            if (questJournalPanel != null) questJournalPanel.Initialize(_adapter, _router, _life.Token);
            if (npcDialoguePanel != null) npcDialoguePanel.Initialize(_adapter, _router, _life.Token);
            if (settingsPanel != null) settingsPanel.Initialize(_adapter, _router, _life.Token);
            if (mapPanel != null) mapPanel.Initialize(_adapter, _router, _life.Token);
            if (buttonBar != null) buttonBar.Initialize(_adapter, this);

            // All panels start hidden.
            HideAllPanels();
        }

        /// <summary>Close and release all panels.</summary>
        public void Close()
        {
            if (_closing) return;
            _closing = true;
            _life?.Cancel();
            _life?.Dispose();
            _life = null;
            if (_router != null) { _router.OnPanelChanged -= HandlePanelChanged; _router.CloseAll(); _router = null; }
            HideAllPanels();
            _adapter = null;
            _doc = null;
        }

        public void OpenPanel(PlayerPanel panel)
        {
            if (_adapter == null || _closing) return;
            var cs = _adapter.ConnectionState;
            if (cs == UIConnectionState.Expired || cs == UIConnectionState.Disconnected)
            { Close(); return; }
            _router?.Open(panel, cs);
        }

        // ── Panel routing ────────────────────────────────────────────────────

        private void HandlePanelChanged(PlayerPanel prev, PlayerPanel next)
        {
            HideAllPanels();
            switch (next)
            {
                case PlayerPanel.Inventory:     if (inventoryPanel != null) inventoryPanel.Show(); break;
                case PlayerPanel.QuestJournal:  if (questJournalPanel != null) questJournalPanel.Show(); break;
                case PlayerPanel.NpcDialogue:   if (npcDialoguePanel != null) npcDialoguePanel.Show(); break;
                case PlayerPanel.Settings:      if (settingsPanel != null) settingsPanel.Show(); break;
                case PlayerPanel.Map:           if (mapPanel != null) mapPanel.Show(); break;
                case PlayerPanel.None:          break;
            }
        }

        private void HideAllPanels()
        {
            if (inventoryPanel != null) inventoryPanel.Hide();
            if (questJournalPanel != null) questJournalPanel.Hide();
            if (npcDialoguePanel != null) npcDialoguePanel.Hide();
            if (settingsPanel != null) settingsPanel.Hide();
            if (mapPanel != null) mapPanel.Hide();
        }

        // ── Unity lifecycle ──────────────────────────────────────────────────

        private void Update()
        {
            if (_adapter == null || _closing) return;
            var cs = _adapter.ConnectionState;
            if (cs == UIConnectionState.Expired || cs == UIConnectionState.Disconnected)
            { Close(); return; }
            if (buttonBar != null) buttonBar.RefreshVisibility(cs);
        }

        private void OnDestroy() => Close();
    }
}
