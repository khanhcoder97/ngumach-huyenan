using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

// Fail-fast validation that the quest graph and its objective targets resolve
// against the content the server owns. Targets are checked by type: a KILL or
// BOSS step must point at a real spawn/boss record, an INTERACT/COLLECT step at
// a real record, a TALK step at an NPC anchor. A blocked quest keeps its place
// in the graph but must say, for every gap, which field is missing and which
// document has to fill it.
public static class QuestCatalogValidator
{
    public static void Validate(
        IQuestCatalog quests,
        WorldRecordCatalog records,
        NpcAnchorCatalog npcAnchors)
    {
        var byId = new Dictionary<string, QuestDefinition>(StringComparer.Ordinal);
        foreach (var questId in quests.QuestIds)
        {
            if (quests.TryGet(questId, out var definition))
            {
                byId[questId] = definition;
            }
        }

        foreach (var definition in byId.Values)
        {
            ValidateObjectives(definition, records, npcAnchors);
            ValidateBlockedSteps(definition);
        }

        ValidateGraph(byId);
    }

    private static void ValidateObjectives(
        QuestDefinition definition,
        WorldRecordCatalog records,
        NpcAnchorCatalog npcAnchors)
    {
        foreach (var objective in definition.Objectives)
        {
            switch (objective.Type)
            {
                case QuestObjectiveTypes.Collect:
                case QuestObjectiveTypes.Interact:
                case QuestObjectiveTypes.Kill:
                case QuestObjectiveTypes.Boss:
                case QuestObjectiveTypes.Escort:
                    ValidateRecordTargets(definition.QuestId, objective, records);
                    break;
                case QuestObjectiveTypes.Talk:
                    ValidateNpcTargets(definition.QuestId, objective, npcAnchors);
                    break;
            }
        }
    }

    private static void ValidateBlockedSteps(QuestDefinition definition)
    {
        if (definition.IsBlocked)
        {
            if (definition.Blocked.Count == 0)
            {
                throw new InvalidOperationException(
                    $"Quest '{definition.QuestId}' is blocked but names no blocked step.");
            }

            if (definition.TurnInNpcId is null &&
                !definition.Blocked.Any(step =>
                    string.Equals(step.MissingField, "turnInNpcId", StringComparison.Ordinal)))
            {
                throw new InvalidOperationException(
                    $"Quest '{definition.QuestId}' has no turn-in NPC and does not " +
                    "name that gap as a blocked step.");
            }
        }
        else if (definition.Blocked.Count > 0)
        {
            throw new InvalidOperationException(
                $"Quest '{definition.QuestId}' is active but carries blocked steps.");
        }
    }

    private static void ValidateGraph(IReadOnlyDictionary<string, QuestDefinition> byId)
    {
        foreach (var definition in byId.Values)
        {
            foreach (var prerequisiteId in definition.PrerequisiteQuestIds)
            {
                if (!byId.TryGetValue(prerequisiteId, out var prerequisite))
                {
                    throw new InvalidOperationException(
                        $"Quest '{definition.QuestId}' requires '{prerequisiteId}', " +
                        "which is not in the catalog.");
                }

                if (!prerequisite.Unlocks.Contains(definition.QuestId, StringComparer.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"Quest '{definition.QuestId}' requires '{prerequisiteId}' but " +
                        $"'{prerequisiteId}' does not unlock it.");
                }
            }

            foreach (var unlockedId in definition.Unlocks)
            {
                if (!byId.TryGetValue(unlockedId, out var unlocked))
                {
                    throw new InvalidOperationException(
                        $"Quest '{definition.QuestId}' unlocks '{unlockedId}', " +
                        "which is not in the catalog.");
                }

                if (!unlocked.PrerequisiteQuestIds.Contains(definition.QuestId, StringComparer.Ordinal))
                {
                    throw new InvalidOperationException(
                        $"Quest '{definition.QuestId}' unlocks '{unlockedId}' but " +
                        $"'{unlockedId}' does not require it.");
                }
            }
        }

        // Depth-first walk over prerequisites: a cycle here means a quest can
        // never open, and the error names the ring rather than the first quest.
        var resolved = new HashSet<string>(StringComparer.Ordinal);
        var path = new List<string>();
        foreach (var questId in byId.Keys)
        {
            Visit(questId, byId, resolved, path);
        }
    }

    private static void Visit(
        string questId,
        IReadOnlyDictionary<string, QuestDefinition> byId,
        HashSet<string> resolved,
        List<string> path)
    {
        if (resolved.Contains(questId))
        {
            return;
        }

        var ringAt = path.IndexOf(questId);
        if (ringAt >= 0)
        {
            var ring = string.Join(" -> ", path.Skip(ringAt).Append(questId));
            throw new InvalidOperationException($"Quest prerequisites form a cycle: {ring}.");
        }

        path.Add(questId);
        foreach (var prerequisiteId in byId[questId].PrerequisiteQuestIds)
        {
            Visit(prerequisiteId, byId, resolved, path);
        }

        path.RemoveAt(path.Count - 1);
        resolved.Add(questId);
    }

    private static void ValidateRecordTargets(
        string questId,
        QuestObjectiveDefinition objective,
        WorldRecordCatalog records)
    {
        foreach (var targetId in objective.TargetIds)
        {
            if (!records.TryResolveTarget(targetId, objective.MapId, out _))
            {
                throw new InvalidOperationException(
                    $"Quest '{questId}' objective '{objective.ObjectiveId}' target " +
                    $"'{targetId}' has no world record on map '{objective.MapId}'.");
            }
        }
    }

    private static void ValidateNpcTargets(
        string questId,
        QuestObjectiveDefinition objective,
        NpcAnchorCatalog npcAnchors)
    {
        foreach (var targetId in objective.TargetIds)
        {
            if (!npcAnchors.HasAnchorFor(targetId))
            {
                throw new InvalidOperationException(
                    $"Quest '{questId}' objective '{objective.ObjectiveId}' target " +
                    $"'{targetId}' has no NPC anchor.");
            }
        }
    }
}
