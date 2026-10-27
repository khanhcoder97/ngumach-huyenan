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

public sealed record QuestDefinition(
    string QuestId,
    string QuestType,
    int MinLevel,
    int MaxLevel,
    IReadOnlyList<string> PrerequisiteQuestIds,
    IReadOnlyList<QuestObjectiveDefinition> Objectives,
    string InitialStepId);

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
