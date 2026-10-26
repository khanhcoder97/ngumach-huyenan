namespace Server.Health.Contracts;

public static class QuestStates
{
    public const string Locked = "LOCKED";
    public const string Available = "AVAILABLE";
    public const string Active = "ACTIVE";
    public const string ReadyToTurnIn = "READY_TO_TURN_IN";
    public const string Completed = "COMPLETED";
    public const string Failed = "FAILED";
}

public sealed class QuestState
{
    public required string QuestId { get; init; }
    public required string State { get; init; }
    public required string StepId { get; init; }
    public required IReadOnlyDictionary<string, int> ObjectiveCounters { get; init; }
    public required long Revision { get; init; }
}
