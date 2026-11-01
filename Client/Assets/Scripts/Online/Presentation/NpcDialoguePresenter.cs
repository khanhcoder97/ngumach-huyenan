// AG3 — NpcDialoguePresenter: wraps InteractAsync/TurnInQuestAsync for dialogue panel.
// No Unity dependency. Builds NpcDialogueViewState from interaction results.
// Rules:
//   - Retry uncertain goes back to same pending command, never re-sends a different one.
//   - Choosing an option never writes story flags or rewards locally.
//   - UnavailableReason shown with correlationId when applicable.
//   - Invalidate presentation generation on Clear/interact to drop late completions (AGR2-02).
//   - Canonical NPC ID used for quest wire commands; entity ID preserved for interact (AGR2-01).
// Owner: Antigravity Remote — Issue #80, #85.

using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Presentation
{
    public sealed class NpcDialoguePresenter
    {
        private readonly IP1UIAdapter _adapter;
        private AsyncState<NpcDialogueViewState> _state = AsyncState<NpcDialogueViewState>.Idle;
        private int _generation;

        public AsyncState<NpcDialogueViewState> State => _state;
        public event Action OnChanged;

        public NpcDialoguePresenter(IP1UIAdapter adapter)
            => _adapter = adapter ?? throw new ArgumentNullException(nameof(adapter));

        /// <summary>Interact with a gather node/parcel target (closed interact contract; NPC is NOT allowed here).</summary>
        public async Task<AsyncState<NpcDialogueViewState>> InteractAsync(string targetId, CancellationToken ct)
        {
            if (string.IsNullOrEmpty(targetId)) throw new ArgumentException("targetId required", nameof(targetId));
            var context = NpcContextMapping.Resolve(targetId);
            if (context?.TemplateId != null)
                throw new InvalidOperationException("NPC conversations must not POST /p1/world/interact; use OpenSnapshotAsync and the narrative provider (OPC-13 B).");
            return await InteractNodeAsync(targetId, ct);
        }

        /// <summary>
        /// OPC-13 B: open NPC dialogue from the world/quest snapshot ONLY (read-only).
        /// Never POSTs the NPC to the closed /p1/world/interact contract; accept/turn-in keep
        /// their canonical commands. Generation token drops late results on NPC switch/Clear.
        /// </summary>
        public async Task<AsyncState<NpcDialogueViewState>> OpenSnapshotAsync(string targetId, CancellationToken ct)
        {
            if (string.IsNullOrEmpty(targetId)) throw new ArgumentException("targetId required", nameof(targetId));

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            // Snapshot-only composition; no adapter call is issued for the conversation itself.
            await Task.Yield();
            if (curGen != _generation) return _state;

            var context = NpcContextMapping.Resolve(targetId);
            _state = ComposeSnapshotView(targetId, context);
            NotifyChanged();
            return _state;
        }

        private AsyncState<NpcDialogueViewState> ComposeSnapshotView(string targetId, NpcContextInfo context)
        {
            if (context == null || context.TemplateId == null)
            {
                // Unknown/unsupported NPC: exact state, never a forged identity or dialogue.
                var unknown = new NpcDialogueViewState(
                    npcId: targetId,
                    recordId: null,
                    kind: null,
                    greetingText: null,
                    choices: Array.Empty<DialogueChoice>(),
                    unavailableReason: "UNRESOLVED — NPC chưa có trong catalog narrative (không đọc được thoại).",
                    correlationId: null,
                    interactionTargetEntityId: targetId);
                return _state.WithValue(unknown);
            }

            string canonicalNpcId = context.TemplateId;
            var choices = BuildChoicesFromQuestState(canonicalNpcId);

            // Presence snapshot from the world (if available): marks row when the entity is not on the map.
            string unavailableReason = null;
            bool presentOnMap = true;
            try
            {
                if (_adapter.WorldV2 != null)
                {
                    var entities = _adapter.WorldV2.entities;
                    presentOnMap = entities != null && Array.Exists(entities, e => e != null && string.Equals(e.entityId, context.EntityId, StringComparison.Ordinal));
                }
                else if (_adapter.World != null)
                {
                    var world = _adapter.World.entities;
                    presentOnMap = world != null && Array.Exists(world, e => e != null && string.Equals(e.entityId, context.EntityId, StringComparison.Ordinal));
                }
            }
            catch (Exception) { presentOnMap = true; } // Malformed world must not break a read-only dialogue.

            if (!presentOnMap)
            {
                unavailableReason = "NPC không còn trên bản đồ hiện tại (snapshot có thể đã đổi phiên/địa điểm reload).";
                for (int i = 0; i < choices.Count; i++)
                {
                    var c = choices[i];
                    if (c.Enabled && c.ActionType != DialogueActionType.Close)
                    {
                        // Server-authoritative stance: never offer actionable wire commands
                        // (accept/turn-in) against an entity absent from the world snapshot.
                        choices[i] = new DialogueChoice(
                            c.Index, c.Label, enabled: false, disabledReason: unavailableReason,
                            actionType: c.ActionType, questId: c.QuestId, npcId: c.NpcId);
                    }
                }
            }

            var view = new NpcDialogueViewState(
                npcId: canonicalNpcId,
                recordId: context.RecordId,
                kind: "NPC",
                greetingText: context.DisplayName,
                choices: choices,
                unavailableReason: unavailableReason,
                correlationId: null,
                interactionTargetEntityId: context.EntityId);
            return _state.WithValue(view);
        }

        /// <summary>Gather node/parcel interaction via the closed interact contract (OPC-13 B carve-out).</summary>
        private async Task<AsyncState<NpcDialogueViewState>> InteractNodeAsync(string targetId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var result = await _adapter.InteractAsync(targetId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var context = NpcContextMapping.Resolve(targetId);
                string canonicalNpcId = context.TemplateId;
                var choices = BuildChoicesFromQuestState(canonicalNpcId);

                var view = new NpcDialogueViewState(
                    npcId: canonicalNpcId,
                    recordId: context.RecordId,
                    kind: "NPC",
                    greetingText: context.DisplayName,
                    choices: choices,
                    unavailableReason: null,
                    correlationId: null,
                    interactionTargetEntityId: context.EntityId);

                if (curGen != _generation) return _state;
                _state = _state.WithValue(view);
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        /// <summary>Accept quest via dialogue.</summary>
        public async Task<AsyncState<NpcDialogueViewState>> AcceptQuestAsync(string questId, string npcId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var context = NpcContextMapping.Resolve(npcId);
                string canonicalNpcId = context.TemplateId;

                var result = await _adapter.AcceptQuestAsync(questId, canonicalNpcId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(canonicalNpcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    canonicalNpcId,
                    current?.RecordId ?? context.RecordId,
                    current?.Kind ?? "NPC",
                    current?.GreetingText ?? context.DisplayName,
                    choices,
                    interactionTargetEntityId: current?.InteractionTargetEntityId ?? context.EntityId));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        /// <summary>Turn in quest via dialogue.</summary>
        public async Task<AsyncState<NpcDialogueViewState>> TurnInQuestAsync(string questId, string npcId, CancellationToken ct)
        {
            if (_adapter.HasPendingMutation)
            {
                _state = _state.WithError("pending_mutation");
                NotifyChanged();
                return _state;
            }

            int curGen = Interlocked.Increment(ref _generation);
            _state = _state.WithLoading();
            NotifyChanged();

            try
            {
                var context = NpcContextMapping.Resolve(npcId);
                string canonicalNpcId = context.TemplateId;

                var result = await _adapter.TurnInQuestAsync(questId, canonicalNpcId, ct);
                if (curGen != _generation) return _state;

                if (!result.Success)
                {
                    _state = _state.WithError(result.Code, result.CorrelationId);
                    NotifyChanged();
                    return _state;
                }

                var choices = BuildChoicesFromQuestState(canonicalNpcId);
                var current = _state.Value;
                _state = _state.WithValue(new NpcDialogueViewState(
                    canonicalNpcId,
                    current?.RecordId ?? context.RecordId,
                    current?.Kind ?? "NPC",
                    current?.GreetingText ?? context.DisplayName,
                    choices,
                    interactionTargetEntityId: current?.InteractionTargetEntityId ?? context.EntityId));
                NotifyChanged();
                return _state;
            }
            catch (OperationCanceledException)
            {
                if (curGen != _generation) return _state;
                _state = _state.Value != null ? _state.WithValue(_state.Value) : AsyncState<NpcDialogueViewState>.Idle;
                NotifyChanged();
                throw;
            }
            catch (Exception ex)
            {
                if (curGen != _generation) return _state;
                _state = _state.WithError(ex.Message);
                NotifyChanged();
                throw;
            }
        }

        public void Clear()
        {
            Interlocked.Increment(ref _generation);
            _state = AsyncState<NpcDialogueViewState>.Idle;
            NotifyChanged();
        }

        private List<DialogueChoice> BuildChoicesFromQuestState(string npcTemplateId)
        {
            var choices = new List<DialogueChoice>();
            var quests = _adapter.Quests ?? Array.Empty<P1Quest>();
            int idx = 0;

            foreach (var q in quests)
            {
                if (q == null) continue;

                if (QuestNpcCatalog.IsQuestStartNpc(q.questId, npcTemplateId) && q.state == "AVAILABLE")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nhận nhiệm vụ] " + q.questId,
                        enabled: true,
                        actionType: DialogueActionType.AcceptQuest,
                        questId: q.questId,
                        npcId: npcTemplateId));
                }
                else if (QuestNpcCatalog.IsQuestTurnInNpc(q.questId, npcTemplateId) && q.state == "READY_TO_TURN_IN")
                {
                    choices.Add(new DialogueChoice(
                        idx++,
                        "[Nộp nhiệm vụ] " + q.questId,
                        enabled: true,
                        actionType: DialogueActionType.TurnInQuest,
                        questId: q.questId,
                        npcId: npcTemplateId));
                }
                else if (QuestNpcCatalog.IsQuestStartNpc(q.questId, npcTemplateId) || QuestNpcCatalog.IsQuestTurnInNpc(q.questId, npcTemplateId))
                {
                    if (q.state == "ACTIVE")
                    {
                        choices.Add(new DialogueChoice(
                            idx++,
                            "[Đang làm] " + q.questId,
                            enabled: false,
                            disabledReason: "Chưa hoàn thành mục tiêu",
                            actionType: DialogueActionType.Interact,
                            questId: q.questId,
                            npcId: npcTemplateId));
                    }
                }
            }

            choices.Add(new DialogueChoice(idx, "Tạm biệt", enabled: true, actionType: DialogueActionType.Close, npcId: npcTemplateId));
            return choices;
        }

        private void NotifyChanged() => OnChanged?.Invoke();
    }
}
