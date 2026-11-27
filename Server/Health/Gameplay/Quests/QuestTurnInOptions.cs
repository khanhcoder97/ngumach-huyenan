namespace Server.Health.Gameplay.Quests;

public sealed class QuestTurnInOptions
{
    public const string SectionName = "P1:QuestTurnIn";

    public bool Enabled { get; set; }

    public double MaxInteractionDistanceWu { get; set; } = 5;
}

public static class QuestTurnInOptionsValidator
{
    public static void Validate(QuestTurnInOptions options)
    {
        if (!double.IsFinite(options.MaxInteractionDistanceWu) ||
            options.MaxInteractionDistanceWu <= 0)
        {
            throw new InvalidOperationException(
                "P1:QuestTurnIn:MaxInteractionDistanceWu must be greater than zero.");
        }
    }
}