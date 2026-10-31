// AG1 — Immutable view state types for player UI panels.
// Pure C#9, no Unity dependencies. All state is server-authoritative; no local guesses.
// Owner: Antigravity Remote — do not modify without updating Issue #80.

using System;
using System.Collections.Generic;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    // ── Connection / session ─────────────────────────────────────────────────

    public enum UIConnectionState
    {
        Disconnected,
        Connecting,
        Ready,
        NeedsResync,
        UncertainMutation,  // pending command, outcome unknown — block new input
        Expired,
        Error
    }

    // ── Panel identifiers ────────────────────────────────────────────────────

    public enum PlayerPanel { None, Inventory, Character, QuestJournal, NpcDialogue, Settings, Map }

    // ── Generic async state wrapper ──────────────────────────────────────────

    public enum LoadPhase { Idle, Loading, Loaded, Error, Stale }

    public sealed class AsyncState<T>
    {
        public static readonly AsyncState<T> Idle = new AsyncState<T>(LoadPhase.Idle, default, null);
        public LoadPhase Phase { get; }
        public T Value { get; }
        public string ErrorCode { get; }
        public string CorrelationId { get; }

        public AsyncState(LoadPhase phase, T value, string errorCode, string correlationId = null)
        { Phase = phase; Value = value; ErrorCode = errorCode; CorrelationId = correlationId; }

        public bool IsLoading => Phase == LoadPhase.Loading;
        public bool IsLoaded  => Phase == LoadPhase.Loaded;
        public bool IsError   => Phase == LoadPhase.Error;
        public bool IsStale   => Phase == LoadPhase.Stale;

        public AsyncState<T> WithLoading() => new AsyncState<T>(LoadPhase.Loading, Value, null);
        public AsyncState<T> WithValue(T value) => new AsyncState<T>(LoadPhase.Loaded, value, null);
        public AsyncState<T> WithError(string code, string corr = null) => new AsyncState<T>(LoadPhase.Error, Value, code, corr);
        public AsyncState<T> WithStale() => new AsyncState<T>(LoadPhase.Stale, Value, null);
    }

    // ── Inventory view state ─────────────────────────────────────────────────

    /// <summary>
    /// Slot index = page * 25 + row * 5 + col  (4 pages × 5×5 = 100 slots, DEC-023).
    /// Slots are sparse; missing slot = empty. Do NOT infer stats from icon/name.
    /// </summary>
    public sealed class InventoryViewState
    {
        public const int PagesCount = 4;
        public const int SlotsPerPage = 25;
        public const int TotalSlots = PagesCount * SlotsPerPage; // 100

        public long InventoryRevision { get; }
        /// <summary>Key = 0..99 (slot index). Only populated slots present.</summary>
        public IReadOnlyDictionary<int, ItemSlotView> Slots { get; }
        public IReadOnlyList<CurrencyView> Currencies { get; }
        public int ActivePage { get; }           // 0-3
        public string SelectedInstanceId { get; } // null = none
        public string FilterText { get; }
        public string[] DiagnosticWarnings { get; } // duplicate-slot, bad-ref, out-of-range

        public InventoryViewState(
            long revision,
            IReadOnlyDictionary<int, ItemSlotView> slots,
            IReadOnlyList<CurrencyView> currencies,
            int activePage = 0,
            string selectedInstanceId = null,
            string filterText = null,
            string[] diagnosticWarnings = null)
        {
            InventoryRevision = revision;
            Slots = slots ?? new Dictionary<int, ItemSlotView>();
            Currencies = currencies ?? Array.Empty<CurrencyView>();
            ActivePage = Math.Max(0, Math.Min(PagesCount - 1, activePage));
            SelectedInstanceId = selectedInstanceId;
            FilterText = filterText;
            DiagnosticWarnings = diagnosticWarnings ?? Array.Empty<string>();
        }

        public InventoryViewState WithPage(int page) =>
            new InventoryViewState(InventoryRevision, Slots, Currencies, page, SelectedInstanceId, FilterText, DiagnosticWarnings);

        public InventoryViewState WithSelection(string instanceId) =>
            new InventoryViewState(InventoryRevision, Slots, Currencies, ActivePage, instanceId, FilterText, DiagnosticWarnings);

        public InventoryViewState WithFilter(string text) =>
            new InventoryViewState(InventoryRevision, Slots, Currencies, ActivePage, SelectedInstanceId, text, DiagnosticWarnings);

        /// <summary>Slots visible on current page (indices page*25 .. page*25+24).</summary>
        public IEnumerable<(int localIndex, ItemSlotView item)> PageSlots()
        {
            int start = ActivePage * SlotsPerPage;
            for (int i = 0; i < SlotsPerPage; i++)
            {
                int globalIdx = start + i;
                Slots.TryGetValue(globalIdx, out var slot);
                if (slot != null && !string.IsNullOrEmpty(FilterText))
                {
                    bool match = (slot.DisplayName != null && slot.DisplayName.IndexOf(FilterText, StringComparison.OrdinalIgnoreCase) >= 0)
                              || (slot.TemplateId != null && slot.TemplateId.IndexOf(FilterText, StringComparison.OrdinalIgnoreCase) >= 0);
                    if (!match)
                    {
                        yield return (i, null);
                        continue;
                    }
                }
                yield return (i, slot); // slot may be null = empty
            }
        }
    }

    public sealed class ItemSlotView
    {
        public string InstanceId { get; }
        public string TemplateId { get; }
        public int Stack { get; }
        public string Location { get; }  // "BAG" | "EQUIPPED" | "BANK"
        public int Durability { get; }
        public int Version { get; }
        // Rarity/display fields come from catalog lookup, not guessed from name/icon.
        // If catalog unavailable, DisplayName = TemplateId (UNRESOLVED).
        public string DisplayName { get; }
        public string RarityKey { get; }  // null if catalog unavailable

        public ItemSlotView(P1Item item, string displayName = null, string rarityKey = null)
        {
            if (item == null) throw new ArgumentNullException(nameof(item));
            InstanceId = item.instanceId;
            TemplateId = item.templateId;
            Stack = item.stack;
            Location = item.location;
            Durability = item.durability;
            Version = item.version;
            DisplayName = displayName ?? item.templateId + " (UNRESOLVED)";
            RarityKey = rarityKey;
        }
    }

    public sealed class CurrencyView
    {
        public string CurrencyId { get; }
        public long Amount { get; }
        public CurrencyView(P1Currency c) { CurrencyId = c.currencyId; Amount = c.amount; }
    }

    // ── Quest journal view state ─────────────────────────────────────────────

    public sealed class QuestJournalViewState
    {
        public IReadOnlyList<QuestEntryView> Active { get; }
        public IReadOnlyList<QuestEntryView> Completed { get; }
        public string SelectedQuestId { get; }
        public string PinnedQuestId { get; }
        public QuestEntryView PinnedQuest => Active != null ? Active.Find(q => q.QuestId == PinnedQuestId) : null;
        public bool HasPinnedTracker => !string.IsNullOrEmpty(PinnedQuestId);

        public QuestJournalViewState(
            IReadOnlyList<QuestEntryView> active,
            IReadOnlyList<QuestEntryView> completed,
            string selectedQuestId = null,
            bool hasPinnedTracker = false,
            string pinnedQuestId = null)
        {
            Active = active ?? Array.Empty<QuestEntryView>();
            Completed = completed ?? Array.Empty<QuestEntryView>();
            SelectedQuestId = selectedQuestId;
            PinnedQuestId = pinnedQuestId ?? (hasPinnedTracker ? (selectedQuestId ?? "P00-01") : null);
        }

        public QuestJournalViewState WithSelection(string questId) =>
            new QuestJournalViewState(Active, Completed, questId, HasPinnedTracker, PinnedQuestId);

        public QuestJournalViewState WithPinned(bool pinned) =>
            new QuestJournalViewState(Active, Completed, SelectedQuestId, pinned, pinned ? (PinnedQuestId ?? SelectedQuestId ?? "P00-01") : null);

        public QuestJournalViewState WithPinnedQuest(string pinnedQuestId) =>
            new QuestJournalViewState(Active, Completed, SelectedQuestId, !string.IsNullOrEmpty(pinnedQuestId), pinnedQuestId);
    }

    public sealed class QuestEntryView
    {
        public string QuestId { get; }
        public string State { get; }    // "AVAILABLE" | "ACTIVE" | "READY_TO_TURN_IN" | "COMPLETED"
        public string StepId { get; }
        public long Revision { get; }
        public IReadOnlyDictionary<string, int> Counters { get; }
        public string Title { get; }
        public string ObjectiveDescription { get; }
        public string DisplayName => Title;
        public string ObjectiveDesc => ObjectiveDescription;

        public QuestEntryView(P1Quest q, string title = null, string objectiveDesc = null)
        {
            if (q == null) throw new ArgumentNullException(nameof(q));
            QuestId = q.questId;
            State = q.state;
            StepId = q.stepId;
            Revision = q.revision;
            Counters = q.objectiveCounters ?? new Dictionary<string, int>();
            Title = title ?? q.questId + " (UNRESOLVED)";
            ObjectiveDescription = objectiveDesc ?? q.stepId ?? "";
        }

        public bool IsReadyToTurnIn => State == "READY_TO_TURN_IN";
        public bool IsCompleted => State == "COMPLETED";
    }

    // ── NPC dialogue view state ──────────────────────────────────────────────

    public sealed class NpcDialogueViewState
    {
        public string NpcId { get; }
        public string RecordId { get; }
        public string Kind { get; }
        public string GreetingText { get; }
        public IReadOnlyList<DialogueChoice> Choices { get; }
        public string UnavailableReason { get; }  // null = available
        public string CorrelationId { get; }
        public string InteractionTargetEntityId { get; }
        public string NpcTemplateId => NpcId;
        public string SourceRecordId => RecordId;

        public NpcDialogueViewState(
            string npcId, string recordId, string kind,
            string greetingText,
            IReadOnlyList<DialogueChoice> choices,
            string unavailableReason = null,
            string correlationId = null,
            string interactionTargetEntityId = null)
        {
            NpcId = npcId; RecordId = recordId; Kind = kind;
            GreetingText = greetingText;
            Choices = choices ?? Array.Empty<DialogueChoice>();
            UnavailableReason = unavailableReason;
            CorrelationId = correlationId;
            InteractionTargetEntityId = interactionTargetEntityId ?? npcId;
        }

        public bool IsAvailable => UnavailableReason == null;
    }

    public enum DialogueActionType { Interact, AcceptQuest, TurnInQuest, Close }

    public sealed class DialogueChoice
    {
        public int Index { get; }
        public string Label { get; }
        public bool Enabled { get; }
        public string DisabledReason { get; }
        public DialogueActionType ActionType { get; }
        public string QuestId { get; }
        public string NpcId { get; }

        public DialogueChoice(
            int index,
            string label,
            bool enabled = true,
            string disabledReason = null,
            DialogueActionType actionType = DialogueActionType.Interact,
            string questId = null,
            string npcId = null)
        {
            Index = index;
            Label = label;
            Enabled = enabled;
            DisabledReason = disabledReason;
            ActionType = actionType;
            QuestId = questId;
            NpcId = npcId;
        }
    }

    // ── Settings view state ──────────────────────────────────────────────────

    public sealed class SettingsViewState
    {
        public float UiScale { get; }       // 0.5 – 2.0
        public float MasterVolume { get; }  // 0.0 – 1.0
        public float TextSize { get; }      // 0.75 – 1.5
        public bool ReducedMotion { get; }
        public bool ReducedFlash { get; }
        public bool ShowInputHints { get; }

        public SettingsViewState(
            float uiScale = 1f, float masterVolume = 1f, float textSize = 1f,
            bool reducedMotion = false, bool reducedFlash = false, bool showInputHints = true)
        {
            UiScale = Math.Max(0.5f, Math.Min(2f, uiScale));
            MasterVolume = Math.Max(0f, Math.Min(1f, masterVolume));
            TextSize = Math.Max(0.75f, Math.Min(1.5f, textSize));
            ReducedMotion = reducedMotion;
            ReducedFlash = reducedFlash;
            ShowInputHints = showInputHints;
        }

        public static readonly SettingsViewState Default = new SettingsViewState();
    }

    // ── Map view state & bounds ──────────────────────────────────────────────

    public sealed class MapBounds
    {
        public double XMin { get; }
        public double XMax { get; }
        public double YMin { get; }
        public double YMax { get; }
        public double Width => XMax - XMin;
        public double Height => YMax - YMin;

        public MapBounds(double xMin, double xMax, double yMin, double yMax)
        {
            XMin = xMin; XMax = xMax; YMin = yMin; YMax = yMax;
        }

        public static readonly MapBounds Default = new MapBounds(0, 360, -12, 72);
        public static readonly MapBounds ThangLong = new MapBounds(0, 900, -12, 96);

        public static MapBounds ForMap(string mapId)
        {
            if (string.Equals(mapId, "MAP_THANG_LONG", StringComparison.OrdinalIgnoreCase))
                return ThangLong;
            return Default;
        }
    }

    public sealed class MapViewState
    {
        public string MapId { get; }
        public double PlayerX { get; }
        public double PlayerY { get; }
        public IReadOnlyList<MapMarker> Markers { get; }
        public float ZoomLevel { get; }       // UI zoom, independent of world camera
        public bool TopologyIsCandidate { get; } // true = not yet reviewed, show warning
        public MapBounds Bounds { get; }

        public MapViewState(
            string mapId, double playerX, double playerY,
            IReadOnlyList<MapMarker> markers,
            float zoomLevel = 1f,
            bool topologyIsCandidate = false,
            MapBounds bounds = null)
        {
            MapId = mapId;
            PlayerX = playerX; PlayerY = playerY;
            Markers = markers ?? Array.Empty<MapMarker>();
            ZoomLevel = Math.Max(0.25f, Math.Min(4f, zoomLevel));
            TopologyIsCandidate = topologyIsCandidate;
            Bounds = bounds ?? MapBounds.ForMap(mapId);
        }
    }

    public sealed class MapMarker
    {
        public string EntityId { get; }
        public string Id => EntityId;
        public string Kind { get; }   // "NPC" | "QUEST" | "SPAWN" | "PLAYER"
        public double X { get; }
        public double Y { get; }
        public string Label { get; }
        public MapMarker(string entityId, string kind, double x, double y, string label = null)
        { EntityId = entityId; Kind = kind; X = x; Y = y; Label = label; }
    }
}
