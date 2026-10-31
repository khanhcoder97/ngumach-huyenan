// PlayerUIRoot — MonoBehaviour gốc điều phối toàn bộ panel PlayerUI.
// Inject IP1UIAdapter, dùng PanelRouter để routing, giữ CancellationTokenSource lifecycle.
// Owner: Antigravity Remote — Issue #80, #85.

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
        [SerializeField] private CharacterPanel characterPanel;
        [SerializeField] private QuestJournalPanel questJournalPanel;
        [SerializeField] private NpcDialoguePanel npcDialoguePanel;
        [SerializeField] private SettingsPanel settingsPanel;
        [SerializeField] private MapPanel mapPanel;
        [SerializeField] private PlayerUIButtonBar buttonBar;
        [SerializeField] private CinemaOverlay cinemaOverlay;

        // ── Runtime state ────────────────────────────────────────────────────
        private IP1UIAdapter _adapter;
        private UIDocument _doc;
        private PanelRouter _router;
        private CancellationTokenSource _life;
        private bool _closing;

        // ── Public API ───────────────────────────────────────────────────────

        public bool IsAnyOpen => (_router != null && _router.IsAnyOpen) || (cinemaOverlay != null && cinemaOverlay.Presenter != null && cinemaOverlay.Presenter.State != null && cinemaOverlay.Presenter.State.IsPlaying);
        public PanelRouter Router => _router;
        public bool HandleEscapeInput { get; set; } = false; // AGR2-03: Single Escape owner

        /// <summary>Called from P1PlayerUIHook after adapter is ready. Finds UIDocument in scene if not provided.</summary>
        public void Initialize(IP1UIAdapter adapter, UIDocument doc = null)
        {
            if (doc == null) doc = GetComponent<UIDocument>() ?? GetComponentInParent<UIDocument>();
            if (doc == null) { Debug.LogError("[PlayerUIRoot] No UIDocument found on host or parent."); return; }
            Open(adapter, doc);
        }

        public void SetPanelReferences(
            InventoryPanel inv,
            CharacterPanel character,
            QuestJournalPanel quest,
            NpcDialoguePanel npc,
            SettingsPanel settings,
            MapPanel map,
            PlayerUIButtonBar bar,
            CinemaOverlay cinema)
        {
            inventoryPanel = inv;
            characterPanel = character;
            questJournalPanel = quest;
            npcDialoguePanel = npc;
            settingsPanel = settings;
            mapPanel = map;
            buttonBar = bar;
            cinemaOverlay = cinema;
        }

        /// <summary>Close all panels (alias for hook compatibility).</summary>
        public void CloseAll()
        {
            _router?.CloseAll();
            HideAllPanels();
        }

        /// <summary>Close topmost open modal panel or skip cinema overlay.</summary>
        public void CloseTop()
        {
            if (cinemaOverlay != null && cinemaOverlay.Presenter != null && cinemaOverlay.Presenter.State != null && cinemaOverlay.Presenter.State.IsPlaying)
            {
                cinemaOverlay.Presenter.Skip();
                return;
            }
            _router?.CloseTop();
        }

        /// <summary>Open the PlayerUI. Call once per session.</summary>
        public void Open(IP1UIAdapter adapter, UIDocument doc)
        {
            if (_adapter != null) { Debug.LogError("[PlayerUIRoot] Open called twice; call Close first."); return; }
            _closing = false;
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            _doc = doc ?? throw new ArgumentNullException(nameof(doc));
            _life = new CancellationTokenSource();
            _router = new PanelRouter();
            _router.OnPanelChanged += HandlePanelChanged;

            var store = GetComponent<ISettingsStore>() ?? GetComponentInParent<ISettingsStore>();

            // Pass references and injected document to child panels.
            if (inventoryPanel != null) inventoryPanel.Initialize(_adapter, _router, _life.Token, _doc);
            if (characterPanel != null) characterPanel.Initialize(_adapter, _router, _life.Token, _doc);
            if (questJournalPanel != null)
            {
                questJournalPanel.Initialize(_adapter, _router, _life.Token, _doc);
                if (questJournalPanel.Presenter != null && buttonBar != null)
                {
                    questJournalPanel.Presenter.OnChanged += () =>
                    {
                        var pinned = questJournalPanel.Presenter.State.Value?.PinnedQuest;
                        buttonBar.SetPinnedQuest(pinned?.Title, pinned?.ObjectiveDesc);
                    };
                }
            }
            if (npcDialoguePanel != null) npcDialoguePanel.Initialize(_adapter, _router, _life.Token, null, _doc);
            if (settingsPanel != null) settingsPanel.Initialize(_adapter, _router, _life.Token, store, _doc);
            if (mapPanel != null) mapPanel.Initialize(_adapter, _router, _life.Token, _doc);
            if (buttonBar != null) buttonBar.Initialize(_adapter, this, _doc);
            if (cinemaOverlay != null) cinemaOverlay.Initialize(_doc);

            // All panels start hidden.
            HideAllPanels();
        }

        /// <summary>Close and release all panels.</summary>
        public void Close()
        {
            if (_closing) return;
            _closing = true;
            try
            {
                _life?.Cancel();
                _life?.Dispose();
                _life = null;
                if (_router != null)
                {
                    _router.OnPanelChanged -= HandlePanelChanged;
                    _router.CloseAll();
                    _router = null;
                }
                HideAllPanels();

                inventoryPanel?.Teardown();
                characterPanel?.Teardown();
                questJournalPanel?.Teardown();
                npcDialoguePanel?.Teardown();
                settingsPanel?.Teardown();
                mapPanel?.Teardown();
                buttonBar?.Teardown();
                cinemaOverlay?.Teardown();

                _adapter = null;
                _doc = null;
            }
            finally
            {
                _closing = false;
            }
        }

        public void PlayCinema(string sceneId) => cinemaOverlay?.PlayScene(sceneId);

        public void OpenWithNpc(string targetId)
        {
            if (_adapter == null || _closing || string.IsNullOrEmpty(targetId)) return;
            OpenPanel(PlayerPanel.NpcDialogue);
            if (npcDialoguePanel != null)
            {
                _ = npcDialoguePanel.OpenWithNpcAsync(targetId);
            }
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
                case PlayerPanel.Character:     if (characterPanel != null) characterPanel.Show(); break;
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
            if (characterPanel != null) characterPanel.Hide();
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

            // Single Escape Owner: handled here only if standalone (not Hook-driven)
            if (HandleEscapeInput && Input.GetKeyDown(KeyCode.Escape))
            {
                if (_router != null && _router.IsAnyOpen)
                {
                    _router.CloseTop();
                }
            }

            // Keyboard Shortcuts
            if (Input.GetKeyDown(KeyCode.C))
            {
                TogglePanel(PlayerPanel.Character);
            }
            else if (Input.GetKeyDown(KeyCode.B) || Input.GetKeyDown(KeyCode.I))
            {
                TogglePanel(PlayerPanel.Inventory);
            }
            else if (Input.GetKeyDown(KeyCode.J))
            {
                TogglePanel(PlayerPanel.QuestJournal);
            }
            else if (Input.GetKeyDown(KeyCode.M))
            {
                TogglePanel(PlayerPanel.Map);
            }

            if (buttonBar != null) buttonBar.RefreshVisibility(cs);
        }

        private void TogglePanel(PlayerPanel panel)
        {
            if (_router == null) return;
            if (_router.Current == panel)
                _router.CloseTop();
            else
                OpenPanel(panel);
        }

        private void OnDestroy() => Close();
    }
}
