// OPC-16 O3 — read-only projection of the opening tutorial chain P00-01..05.
// The server's QuestState is the only source of state, step, counters and revision.
// This class never unlocks a quest, advances a step or invents a counter: a
// server-confirmed turn-in unlock list is not the same as an activatable quest.
// Pure C#, no engine dependency. Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using NguMach.Client.P1;

namespace NguMach.Client.Core.Tutorial
{
    public sealed class TutorialStep
    {
        public string QuestId { get; }
        public bool IsPresent { get; }
        public string State { get; }
        public string StepId { get; }
        public long Revision { get; }
        public IReadOnlyDictionary<string, int> ObjectiveCounters { get; }
        public string StatusVi { get; }

        internal TutorialStep(string questId, P1Quest quest, bool present)
        {
            QuestId = questId;
            IsPresent = present && quest != null;
            if (!IsPresent)
            {
                State = null;
                StepId = null;
                Revision = 0;
                ObjectiveCounters = new ReadOnlyDictionary<string, int>(
                    new Dictionary<string, int>(StringComparer.Ordinal));
                StatusVi = "Chưa có trong snapshot máy chủ.";
                return;
            }

            State = quest.state;
            StepId = quest.stepId;
            Revision = quest.revision;
            var counters = new Dictionary<string, int>(StringComparer.Ordinal);
            if (quest.objectiveCounters != null)
                foreach (var pair in quest.objectiveCounters) counters[pair.Key] = pair.Value;
            ObjectiveCounters = new ReadOnlyDictionary<string, int>(counters);
            StatusVi = StateVi(quest.state);
        }

        public bool IsLocked => IsPresent && State == "LOCKED";
        public bool IsAvailable => IsPresent && State == "AVAILABLE";
        public bool IsActive => IsPresent && State == "ACTIVE";
        public bool IsReadyToTurnIn => IsPresent && State == "READY_TO_TURN_IN";
        public bool IsCompleted => IsPresent && State == "COMPLETED";
        public bool IsFailed => IsPresent && State == "FAILED";

        public int Counter(string objectiveId)
        {
            if (objectiveId == null) return 0;
            int value;
            return ObjectiveCounters.TryGetValue(objectiveId, out value) ? value : 0;
        }

        private static string StateVi(string state)
        {
            switch (state)
            {
                case "LOCKED": return "Chưa mở";
                case "AVAILABLE": return "Có thể nhận";
                case "ACTIVE": return "Đang thực hiện";
                case "READY_TO_TURN_IN": return "Có thể trả nhiệm vụ";
                case "COMPLETED": return "Đã hoàn thành";
                case "FAILED": return "Thất bại";
                default: return "Không xác định";
            }
        }
    }

    public sealed class TutorialProgress
    {
        // The opening chain is fixed by the reviewed content; order is presentation,
        // not an unlock rule. Only the server decides which quest is AVAILABLE.
        public static readonly string[] Chain =
        {
            "P00-01", "P00-02", "P00-03", "P00-04", "P00-05"
        };

        public IReadOnlyList<TutorialStep> Steps { get; }
        public IReadOnlyList<string> MissingQuestIds { get; }
        public IReadOnlyList<string> UnexpectedQuestIds { get; }
        public IReadOnlyList<string> Diagnostics { get; }
        public TutorialStep NextActionable { get; }
        public TutorialStep FirstIncomplete { get; }
        public bool IsChainComplete { get; }
        public bool IsAuthoritative { get; }

        private readonly Dictionary<string, TutorialStep> byId;

        private TutorialProgress(
            IReadOnlyList<TutorialStep> steps,
            IReadOnlyList<string> missing,
            IReadOnlyList<string> unexpected,
            IReadOnlyList<string> diagnostics)
        {
            Steps = steps;
            MissingQuestIds = missing;
            UnexpectedQuestIds = unexpected;
            Diagnostics = diagnostics;
            byId = new Dictionary<string, TutorialStep>(StringComparer.Ordinal);
            for (int i = 0; i < steps.Count; i++) byId[steps[i].QuestId] = steps[i];

            NextActionable = null;
            FirstIncomplete = null;
            bool complete = true;
            for (int i = 0; i < steps.Count; i++)
            {
                var step = steps[i];
                if (NextActionable == null && step.IsAvailable) NextActionable = step;
                if (FirstIncomplete == null && !step.IsCompleted) FirstIncomplete = step;
                if (!step.IsCompleted) complete = false;
            }
            IsChainComplete = complete;
            IsAuthoritative = missing.Count == 0 && unexpected.Count == 0 && diagnostics.Count == 0;
        }

        public TutorialStep Find(string questId)
        {
            if (questId == null) return null;
            TutorialStep step;
            return byId.TryGetValue(questId, out step) ? step : null;
        }

        // A tutorial command is legal only on the exact authoritative state. Being
        // "next" or "unlocked in a receipt" is not a client-side permission.
        public bool CanAccept(string questId)
        {
            var step = Find(questId);
            return step != null && step.IsAvailable;
        }

        public bool CanTurnIn(string questId)
        {
            var step = Find(questId);
            return step != null && step.IsReadyToTurnIn;
        }

        public static TutorialProgress FromServer(IReadOnlyList<P1Quest> quests)
        {
            var diagnostics = new List<string>();
            var unexpected = new List<string>();
            var found = new Dictionary<string, P1Quest>(StringComparer.Ordinal);

            if (quests != null)
            {
                for (int i = 0; i < quests.Count; i++)
                {
                    var quest = quests[i];
                    if (quest == null)
                    {
                        diagnostics.Add("null_entry");
                        continue;
                    }
                    if (string.IsNullOrEmpty(quest.questId))
                    {
                        diagnostics.Add("missing_quest_id");
                        continue;
                    }
                    if (Array.IndexOf(Chain, quest.questId) < 0)
                    {
                        if (unexpected.IndexOf(quest.questId) < 0) unexpected.Add(quest.questId);
                        continue;
                    }
                    if (!KnownState(quest.state)) diagnostics.Add("invalid_state:" + quest.questId);
                    if (string.IsNullOrEmpty(quest.stepId) ||
                        !quest.stepId.StartsWith("STEP_", StringComparison.Ordinal))
                        diagnostics.Add("invalid_step:" + quest.questId);
                    if (quest.revision < 0) diagnostics.Add("negative_revision:" + quest.questId);
                    if (quest.objectiveCounters == null)
                    {
                        diagnostics.Add("missing_counters:" + quest.questId);
                    }
                    else
                    {
                        foreach (var pair in quest.objectiveCounters)
                        {
                            if (string.IsNullOrEmpty(pair.Key)) diagnostics.Add("empty_counter_key:" + quest.questId);
                            if (pair.Value < 0) diagnostics.Add("negative_counter:" + pair.Key);
                        }
                    }

                    P1Quest previous;
                    if (found.TryGetValue(quest.questId, out previous))
                    {
                        diagnostics.Add("duplicate:" + quest.questId);
                        // Keep the newer revision so a reconnect cannot regress the view,
                        // but still expose the duplicate instead of hiding it.
                        if (quest.revision >= previous.revision) found[quest.questId] = quest;
                    }
                    else
                    {
                        found[quest.questId] = quest;
                    }
                }
            }

            var steps = new List<TutorialStep>(Chain.Length);
            var missing = new List<string>();
            for (int i = 0; i < Chain.Length; i++)
            {
                P1Quest quest;
                if (found.TryGetValue(Chain[i], out quest))
                {
                    steps.Add(new TutorialStep(Chain[i], quest, true));
                }
                else
                {
                    missing.Add(Chain[i]);
                    steps.Add(new TutorialStep(Chain[i], null, false));
                }
            }

            return new TutorialProgress(
                new ReadOnlyCollection<TutorialStep>(steps),
                new ReadOnlyCollection<string>(missing),
                new ReadOnlyCollection<string>(unexpected),
                new ReadOnlyCollection<string>(diagnostics));
        }

        private static bool KnownState(string state)
        {
            return state == "LOCKED" || state == "AVAILABLE" || state == "ACTIVE" ||
                   state == "READY_TO_TURN_IN" || state == "COMPLETED" || state == "FAILED";
        }
    }
}
