namespace Server.Health.Gameplay.Quests;

public static class QuestTypes
{
    public const string Main = "MAIN";
    public const string Side = "SIDE";
    public const string Daily = "DAILY";
    public const string Weekly = "WEEKLY";
    public const string Class = "CLASS";
    public const string Guild = "GUILD";
    public const string Event = "EVENT";

    private static readonly HashSet<string> Known = new(StringComparer.Ordinal)
    {
        Main, Side, Daily, Weekly, Class, Guild, Event
    };

    public static bool IsKnown(string? value) => value is not null && Known.Contains(value);
}

public static class QuestObjectiveTypes
{
    public const string Collect = "COLLECT";
    public const string Kill = "KILL";
    public const string Interact = "INTERACT";
    public const string Escort = "ESCORT";
    public const string Boss = "BOSS";
    public const string Talk = "TALK";

    private static readonly HashSet<string> Known = new(StringComparer.Ordinal)
    {
        Collect, Kill, Interact, Escort, Boss, Talk
    };

    public static bool IsKnown(string? value) => value is not null && Known.Contains(value);
}

public sealed record QuestRewardCurrency(string CurrencyId, long Amount);

public sealed record QuestRewards(
    IReadOnlyList<QuestRewardCurrency> Currency,
    IReadOnlyList<string> ItemIds,
    string XpRule);

// A quest whose source does not define every field the runtime needs is loaded
// as BLOCKED rather than defaulted: it keeps its place in the graph (other
// quests may require or unlock it) but can never activate, and each gap is
// named with the field and the document that has to supply it.
public static class QuestActivations
{
    public const string Active = "ACTIVE";
    public const string Blocked = "BLOCKED";

    public static bool IsKnown(string? value) =>
        value is Active or Blocked;
}

public sealed record QuestBlockedStep(
    string DesignStep,
    string MissingField,
    string Source);

public sealed record QuestDefinition(
    string QuestId,
    string QuestType,
    string StartNpcId,
    int MinLevel,
    int MaxLevel,
    IReadOnlyList<string> PrerequisiteQuestIds,
    IReadOnlyList<QuestObjectiveDefinition> Objectives,
    string InitialStepId,
    string? TurnInNpcId,
    QuestRewards Rewards,
    IReadOnlyList<string> Unlocks,
    string Activation = QuestActivations.Active,
    IReadOnlyList<QuestBlockedStep>? BlockedSteps = null)
{
    public IReadOnlyList<QuestBlockedStep> Blocked =>
        BlockedSteps ?? Array.Empty<QuestBlockedStep>();

    public bool IsBlocked => string.Equals(Activation, QuestActivations.Blocked, StringComparison.Ordinal);
}

public sealed record QuestObjectiveDefinition(
    string ObjectiveId,
    string Type,
    IReadOnlyList<string> TargetIds,
    int Count,
    string MapId);

public static class QuestStepIds
{
    public static string FromObjectiveId(string objectiveId) =>
        string.Concat("STEP_", objectiveId[4..]);
}
