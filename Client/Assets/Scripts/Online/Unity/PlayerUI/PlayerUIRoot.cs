// PlayerUIRoot — MonoBehaviour gốc điều phối toàn bộ panel PlayerUI.
// Inject IP1UIAdapter, dùng PanelRouter để routing, giữ CancellationTokenSource lifecycle.
// Owner: Antigravity Remote — Issue #80, #85.

using System;
using System.Collections.Generic;
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
        private UIDocument _configuredDocument;
        private PanelRouter _router;
        private CancellationTokenSource _life;
        private bool _closing;
        private SettingsConsumerBinder _settingsBinder;
        private UiItemResolverSession _itemResolver;
        private VisualElement _focusBeforeOpen;

        private const string FocusScopeGlobal = "global";

        // ── Public API ───────────────────────────────────────────────────────

        public bool IsAnyOpen => (_router != null && _router.IsAnyOpen) || (cinemaOverlay != null && cinemaOverlay.Presenter != null && cinemaOverlay.Presenter.State != null && cinemaOverlay.Presenter.State.IsPlaying);

        /// <summary>True when any panel/modal of the router is open but no cinematic is playing (OPC-13 modal probe).</summary>
        public bool HasAnyPanelOpen => _router != null && _router.IsAnyOpen;

        /// <summary>True while the cinematic overlay is playing (single-owner probe).</summary>
        public bool CinemaPlaying => cinemaOverlay != null && cinemaOverlay.Presenter != null && cinemaOverlay.Presenter.State != null &&
            (cinemaOverlay.Presenter.State.Phase == CinemaPlaybackPhase.Playing || cinemaOverlay.Presenter.State.Phase == CinemaPlaybackPhase.Fallback);

        public PanelRouter Router => _router;
        public bool HandleEscapeInput { get; set; } = false; // AGR2-03: Single Escape owner

        public void BindDocument(UIDocument doc)
        {
            if (doc == null) throw new ArgumentNullException(nameof(doc));
            if (_adapter != null && _doc != doc)
                throw new InvalidOperationException("Close PlayerUI before changing its document.");
            _configuredDocument = doc;
        }

        /// <summary>True when a composition is live on the given document (idempotent rebind support, OPC-13 A).</summary>
        public bool IsInitialized(UIDocument doc)
        {
            return _adapter != null && ReferenceEquals(_doc, doc);
        }

        /// <summary>Uses the injected composition document, or a document on this host/parent.</summary>
        public void Initialize(IP1UIAdapter adapter, UIDocument doc = null)
        {
            if (doc == null) doc = _configuredDocument;
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

        // ── OPC-13 B2 — live quest snapshot wiring ─────────────────────────────

        private string _lastQuestsSignature;

        /// <summary>Sessions start with no known signature; a new Open/rebind re-arms the tracker.</summary>
        private static string QuestsSignature(IP1UIAdapter adapter)
        {
            var qs = adapter?.Quests;
            if (qs == null) return null;
            var sb = new System.Text.StringBuilder();
            for (int i = 0; i < qs.Length; i++)
            {
                var q = qs[i];
                if (q == null) continue;
                sb.Append(q.questId).Append('|').Append(q.state).Append('|').Append(q.revision).Append(';');
            }
            return sb.ToString();
        }

        /// <summary>
        /// OPC-13 B2: the HUD quest tracker lives off the session quest snapshot. When the
        /// server-reported quests change (state or revision), the journal view and the pinned
        /// tracker refresh locally — no wire call, no reopening the journal panel. Pin state
        /// survives refreshes; if the pinned quest completes, the tracker hides itself.
        /// </summary>
        private void RefreshTrackerFromSnapshot()
        {
            if (questJournalPanel?.Presenter == null) return;
            var signature = QuestsSignature(_adapter);
            if (string.Equals(signature, _lastQuestsSignature, StringComparison.Ordinal)) return;
            _lastQuestsSignature = signature;
            questJournalPanel.Presenter.RefreshFromSnapshot();
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
            _lastQuestsSignature = null; // B2: re-arm the tracker wiring for the new session
            _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));
            _doc = doc ?? throw new ArgumentNullException(nameof(doc));
            _life = new CancellationTokenSource();
            _router = new PanelRouter();
            _router.OnPanelChanged += HandlePanelChanged;

            var store = GetComponent<ISettingsStore>() ?? GetComponentInParent<ISettingsStore>();

            // OPC-14 O1/B: load the generated catalog before any panel builds its presenter,
            // then inject the per-session/document resolver into bag + character.
            UiCatalog catalog = null;
            try
            {
                var ta = Resources.Load<TextAsset>("PlayerUI/ui_item_catalog");
                if (ta != null && UiCatalogLoader.TryLoad(ta.text, out var cat, out var err))
                {
                    catalog = cat;
                    UiItemResolver.SetCatalog(cat);
                }
                else if (ta == null)
                    Debug.LogWarning("[PlayerUIRoot] ui_item_catalog not found in Resources/PlayerUI; resolver stays on embedded fallback.");
                else
                    Debug.LogWarning("[PlayerUIRoot] ui_item_catalog load failed: " + err);
            }
            catch (Exception e) { Debug.LogWarning("[PlayerUIRoot] catalog load error: " + e.Message); }
            _itemResolver = new UiItemResolverSession(catalog);

            // Pass references and injected document to child panels.
            if (inventoryPanel != null) inventoryPanel.Initialize(_adapter, _router, _life.Token, _doc, _itemResolver);
            if (characterPanel != null) characterPanel.Initialize(_adapter, _router, _life.Token, _doc, _itemResolver);
            if (questJournalPanel != null)
            {
                questJournalPanel.Initialize(_adapter, _router, _life.Token, _doc);
                if (questJournalPanel.Presenter != null && buttonBar != null)
                {
                    questJournalPanel.Presenter.OnChanged += UpdatePinnedQuest;
                }
            }
            if (npcDialoguePanel != null) npcDialoguePanel.Initialize(_adapter, _router, _life.Token, null, _doc);
            if (settingsPanel != null) settingsPanel.Initialize(_adapter, _router, _life.Token, store, _doc);
            if (mapPanel != null) mapPanel.Initialize(_adapter, _router, _life.Token, _doc);
            if (buttonBar != null) buttonBar.Initialize(_adapter, this, _doc);
            UpdatePinnedQuest();
            if (cinemaOverlay != null) cinemaOverlay.Initialize(_doc);

            // OPC-14 O1: bind settings to actual owned UI consumers (one binder per doc/session).
            if (settingsPanel != null && settingsPanel.Presenter != null)
            {
                _settingsBinder = new SettingsConsumerBinder(settingsPanel.Presenter);
                if (settingsPanel is IUiAccessibilityConsumer sc) _settingsBinder.Register(sc);
                if (cinemaOverlay is IUiAccessibilityConsumer cc) _settingsBinder.Register(cc);
                if (buttonBar is IUiAccessibilityConsumer bc) _settingsBinder.Register(bc);
                if (mapPanel is IUiAccessibilityConsumer mc) _settingsBinder.Register(mc);
                if (inventoryPanel is IUiAccessibilityConsumer ic) _settingsBinder.Register(ic);
                if (characterPanel is IUiAccessibilityConsumer chc) _settingsBinder.Register(chc);
            }

            // OPC-14 O1: Tab/Shift+Tab trap on the real focus controller of the top modal.
            _doc.rootVisualElement.RegisterCallback<KeyDownEvent>(OnRootKeyDown, TrickleDown.TrickleDown);

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

                if (questJournalPanel != null && questJournalPanel.Presenter != null)
                    questJournalPanel.Presenter.OnChanged -= UpdatePinnedQuest;
                if (_doc != null)
                    _doc.rootVisualElement.UnregisterCallback<KeyDownEvent>(OnRootKeyDown, TrickleDown.TrickleDown);
                _focusBeforeOpen = null;
                _settingsBinder?.Dispose();
                _settingsBinder = null;
                _itemResolver = null;
                UiItemResolver.SetCatalog(null);
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

        /// <summary>Skip the running cinematic — invoked by the modal orchestrator only (OPC-13).</summary>
        public void SkipCinema() => cinemaOverlay?.HandleSkip();

        private void UpdatePinnedQuest()
        {
            var pinned = questJournalPanel?.Presenter?.State.Value?.PinnedQuest;
            buttonBar?.SetPinnedQuest(pinned?.Title, pinned?.ObjectiveDesc);
        }

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

        /// <summary>Native visible-tree probe used by EditMode tests (route + display).</summary>
        public bool IsPanelVisible(PlayerPanel panel)
        {
            switch (panel)
            {
                case PlayerPanel.Inventory: return inventoryPanel != null && inventoryPanel.IsVisible;
                case PlayerPanel.Character: return characterPanel != null && characterPanel.IsVisible;
                case PlayerPanel.QuestJournal: return questJournalPanel != null && questJournalPanel.IsVisible;
                case PlayerPanel.NpcDialogue: return npcDialoguePanel != null && npcDialoguePanel.IsVisible;
                case PlayerPanel.Settings: return settingsPanel != null && settingsPanel.IsVisible;
                case PlayerPanel.Map: return mapPanel != null && mapPanel.IsVisible;
                default: return false;
            }
        }

        private VisualElement ActiveModalRoot()
        {
            if (_router != null)
            {
                switch (_router.Current)
                {
                    case PlayerPanel.Inventory: return inventoryPanel?.FocusRoot;
                    case PlayerPanel.Character: return characterPanel?.FocusRoot;
                    case PlayerPanel.QuestJournal: return questJournalPanel?.FocusRoot;
                    case PlayerPanel.NpcDialogue: return npcDialoguePanel?.FocusRoot;
                    case PlayerPanel.Settings: return settingsPanel?.FocusRoot;
                    case PlayerPanel.Map: return mapPanel?.FocusRoot;
                }
            }
            if (CinemaPlaying) return cinemaOverlay?.FocusRoot;
            return null;
        }

        private string ActiveFocusScope()
        {
            if (_router != null && _router.Current != PlayerPanel.None) return _router.Current.ToString();
            return CinemaPlaying ? "Cinema" : FocusScopeGlobal;
        }

        private static string ElementId(VisualElement element)
        {
            if (element == null) return null;
            if (!string.IsNullOrEmpty(element.name)) return element.name;
            var parts = new List<string>();
            var cur = element;
            while (cur != null && cur.parent != null)
            {
                parts.Add(cur.parent.IndexOf(cur).ToString());
                cur = cur.parent;
            }
            parts.Reverse();
            return "path:" + string.Join("/", parts);
        }

        private static void CollectFocusables(VisualElement root, string scope, List<FocusElement> into)
        {
            if (root == null) return;
            foreach (var child in root.Children())
            {
                if (child == null) continue;
                if (child.focusable)
                {
                    bool editor = child is TextField || child is Slider || child is SliderInt ||
                                  child is IntegerField || child is FloatField || child is LongField;
                    into.Add(new FocusElement(ElementId(child), scope, into.Count, editor));
                }
                CollectFocusables(child, scope, into);
            }
        }

        private static bool IsDescendant(VisualElement root, VisualElement element)
        {
            var cur = element;
            while (cur != null) { if (cur == root) return true; cur = cur.parent; }
            return false;
        }

        private static void FocusById(VisualElement root, string id)
        {
            if (root == null || string.IsNullOrEmpty(id)) return;
            if (ElementId(root) == id) { root.Focus(); return; }
            foreach (var child in root.Children())
            {
                if (child == null) continue;
                if (ElementId(child) == id) { child.Focus(); return; }
                FocusById(child, id);
            }
        }

        /// <summary>
        /// OPC-14 O1: real Tab / Shift+Tab trap on the top modal's own focusController.
        /// Tab never escapes the open modal into cinema/gameplay; Shift+Tab wraps.
        /// TextField/Slider children are still focusable and are marked as editors, while
        /// Space gating stays in P1OnlinePanel's RefreshInputSurface.
        /// </summary>
        private void OnRootKeyDown(KeyDownEvent evt)
        {
            if (evt == null || evt.keyCode != KeyCode.Tab) return;
            var root = ActiveModalRoot();
            if (root == null) return; // no modal open: gameplay owns Tab

            string scope = ActiveFocusScope();
            var elements = new List<FocusElement>();
            CollectFocusables(root, scope, elements);
            if (elements.Count == 0) return;

            var focusController = _doc?.rootVisualElement?.panel?.focusController;
            var focused = focusController?.focusedElement as VisualElement;
            string currentId = focused != null && IsDescendant(root, focused) ? ElementId(focused) : null;

            string next = evt.shiftKey
                ? FocusNavigationPolicy.Previous(currentId, elements, scope)
                : FocusNavigationPolicy.Next(currentId, elements, scope);
            if (next == null) return;

            FocusById(root, next);
            evt.StopPropagation();   // never also reach cinema/gameplay Tab handlers
            evt.PreventDefault();
        }

        private void HandlePanelChanged(PlayerPanel prev, PlayerPanel next)
        {
            var focusController = _doc?.rootVisualElement?.panel?.focusController;
            if (prev == PlayerPanel.None && next != PlayerPanel.None)
                _focusBeforeOpen = focusController?.focusedElement as VisualElement;

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

            // OPC-14 O1: restore focus to where it was before the modal opened.
            if (next == PlayerPanel.None && _focusBeforeOpen != null)
            {
                if (_focusBeforeOpen.panel != null) _focusBeforeOpen.Focus();
                _focusBeforeOpen = null;
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
            RefreshTrackerFromSnapshot();
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
