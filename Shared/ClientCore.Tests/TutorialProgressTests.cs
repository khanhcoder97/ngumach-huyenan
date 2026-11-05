// OPC-16 O3 — tutorial chain read model tests over authoritative QuestState.
// Proves missing/duplicate/unexpected data is visible and never silently
// becomes an unlock or a fake step. Owner: OpenCode.

using System;
using System.Collections.Generic;
using NguMach.Client.Core.Tutorial;
using NguMach.Client.P1;
using Xunit;

namespace NguMach.Client.Core.Tests
{
    public class TutorialProgressTests
    {
        private static P1Quest Quest(string id, string state, string step, long revision = 1,
            params (string key, int value)[] counters)
        {
            var map = new Dictionary<string, int>(StringComparer.Ordinal);
            foreach (var pair in counters) map[pair.key] = pair.value;
            return new P1Quest
            {
                questId = id,
                state = state,
                stepId = step,
                revision = revision,
                objectiveCounters = map
            };
        }

        private static P1Quest[] OpeningChain()
        {
            return new[]
            {
                Quest("P00-01", "AVAILABLE", "STEP_P00_01_PACKAGES", 1, ("OBJ_P00_01_PACKAGES", 0)),
                Quest("P00-02", "LOCKED", "STEP_P00_02_CARPLING", 1, ("OBJ_P00_02_CARPLING", 0)),
                Quest("P00-03", "LOCKED", "STEP_P00_03_CLUE", 1),
                Quest("P00-04", "LOCKED", "STEP_P00_04_RESCUE", 1),
                Quest("P00-05", "LOCKED", "STEP_P00_05_BOSS", 1)
            };
        }

        [Fact]
        public void AuthoritativeChain_ProjectsStatesAndCountersInOrder()
        {
            var progress = TutorialProgress.FromServer(OpeningChain());

            Assert.True(progress.IsAuthoritative);
            Assert.Equal(5, progress.Steps.Count);
            Assert.Equal("P00-01", progress.Steps[0].QuestId);
            Assert.Equal("P00-05", progress.Steps[4].QuestId);
            Assert.True(progress.Steps[0].IsAvailable);
            Assert.Equal("Có thể nhận", progress.Steps[0].StatusVi);
            Assert.Equal(0, progress.Steps[0].Counter("OBJ_P00_01_PACKAGES"));
            Assert.Equal("Chưa mở", progress.Steps[1].StatusVi);
            Assert.Equal("P00-01", progress.NextActionable.QuestId);
            Assert.Equal("P00-01", progress.FirstIncomplete.QuestId);
            Assert.False(progress.IsChainComplete);
            Assert.True(progress.CanAccept("P00-01"));
            Assert.False(progress.CanAccept("P00-02"));
            Assert.False(progress.CanTurnIn("P00-01"));
        }

        [Fact]
        public void CompletedFirstQuest_DoesNotUnlockBlockedSecondQuest()
        {
            var chain = OpeningChain();
            chain[0].state = "COMPLETED";
            chain[0].stepId = "STEP_P00_01_DONE";
            chain[0].revision = 4;
            chain[0].objectiveCounters["OBJ_P00_01_PACKAGES"] = 3;

            var progress = TutorialProgress.FromServer(chain);

            Assert.True(progress.Steps[0].IsCompleted);
            Assert.Equal(3, progress.Steps[0].Counter("OBJ_P00_01_PACKAGES"));
            Assert.True(progress.Steps[1].IsLocked);
            Assert.Null(progress.NextActionable); // no client-side unlock
            Assert.Equal("P00-02", progress.FirstIncomplete.QuestId);
            Assert.False(progress.IsChainComplete);
            Assert.False(progress.CanAccept("P00-02"));
        }

        [Fact]
        public void MissingQuest_IsReportedAndNeverInvented()
        {
            var chain = new List<P1Quest>(OpeningChain());
            chain.RemoveAt(2); // P00-03

            var progress = TutorialProgress.FromServer(chain);

            Assert.False(progress.IsAuthoritative);
            Assert.Contains("P00-03", progress.MissingQuestIds);
            Assert.False(progress.Steps[2].IsPresent);
            Assert.Null(progress.Steps[2].State);
            Assert.Equal("Chưa có trong snapshot máy chủ.", progress.Steps[2].StatusVi);
            Assert.False(progress.IsChainComplete);
        }

        [Fact]
        public void MalformedAndUnexpectedEntries_AreDiagnosedNotHidden()
        {
            var chain = new List<P1Quest>(OpeningChain());
            chain.Add(Quest("P00-02", "LOCKED", "STEP_P00_02_CARPLING", 7, ("OBJ_P00_02_CARPLING", 0)));
            chain.Add(Quest("P00-06", "LOCKED", "STEP_P00_06_UNKNOWN"));
            chain[3].state = "OPEN";
            chain[3].stepId = "NOT_A_STEP";
            chain[3].revision = -1;
            chain[3].objectiveCounters["OBJ_P00_04_RESCUE"] = -2;
            chain[4].objectiveCounters = null;

            var progress = TutorialProgress.FromServer(chain);

            Assert.False(progress.IsAuthoritative);
            Assert.Contains("P00-06", progress.UnexpectedQuestIds);
            Assert.Contains("duplicate:P00-02", progress.Diagnostics);
            Assert.Contains("invalid_state:P00-04", progress.Diagnostics);
            Assert.Contains("invalid_step:P00-04", progress.Diagnostics);
            Assert.Contains("negative_revision:P00-04", progress.Diagnostics);
            Assert.Contains("negative_counter:OBJ_P00_04_RESCUE", progress.Diagnostics);
            Assert.Contains("missing_counters:P00-05", progress.Diagnostics);
            Assert.Equal(7, progress.Steps[1].Revision); // newer duplicate retained
        }

        [Fact]
        public void Commands_RequireExactAuthoritativeState()
        {
            var chain = OpeningChain();
            chain[1].state = "READY_TO_TURN_IN";
            chain[1].objectiveCounters["OBJ_P00_02_CARPLING"] = 4;

            var progress = TutorialProgress.FromServer(chain);

            Assert.True(progress.CanTurnIn("P00-02"));
            Assert.False(progress.CanAccept("P00-02"));
            Assert.False(progress.CanAccept("p00-01"));
            Assert.False(progress.CanAccept("P00-99"));
            Assert.False(progress.CanTurnIn(null));
            Assert.Equal(4, progress.Steps[1].Counter("OBJ_P00_02_CARPLING"));
        }

        [Fact]
        public void NullSnapshot_KeepsChainShapeWithoutInventingState()
        {
            var progress = TutorialProgress.FromServer(null);

            Assert.Equal(5, progress.Steps.Count);
            Assert.Equal(5, progress.MissingQuestIds.Count);
            Assert.False(progress.IsAuthoritative);
            Assert.Null(progress.NextActionable);
            AssertNullStep(progress.Steps);
        }

        private static void AssertNullStep(IReadOnlyList<TutorialStep> steps)
        {
            for (int i = 0; i < steps.Count; i++)
            {
                Assert.False(steps[i].IsPresent);
                Assert.Null(steps[i].State);
                Assert.False(steps[i].IsLocked);
                Assert.False(steps[i].IsAvailable);
            }
        }
    }
}
