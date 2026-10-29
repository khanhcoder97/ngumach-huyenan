using Server.Health.World;

namespace Server.Health.Gameplay.Quests;

// Fail-fast validation that quest objective targets resolve against the world
// content the server owns. KILL/ESCORT/BOSS are only format-checked by the
// loader because their verified-event sources do not exist yet (QOD-13 scope).
public static class QuestCatalogValidator
{
    public static void Validate(
        IQuestCatalog quests,
        WorldRecordCatalog records,
        NpcAnchorCatalog npcAnchors)
    {
        foreach (var questId in quests.QuestIds)
        {
            if (!quests.TryGet(questId, out var definition))
            {
                continue;
            }

            foreach (var objective in definition.Objectives)
            {
                switch (objective.Type)
                {
                    case QuestObjectiveTypes.Collect:
                    case QuestObjectiveTypes.Interact:
                        ValidateRecordTargets(questId, objective, records);
                        break;
                    case QuestObjectiveTypes.Talk:
                        ValidateNpcTargets(questId, objective, npcAnchors);
                        break;
                }
            }
        }
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
