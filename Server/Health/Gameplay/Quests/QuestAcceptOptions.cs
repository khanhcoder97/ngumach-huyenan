namespace Server.Health.Gameplay.Quests;

public sealed class QuestAcceptOptions
{
    public const string SectionName = "P1:QuestAccept";

    public bool Enabled { get; set; }

    public double MaxInteractionDistanceWu { get; set; } = 5;
}

public static class QuestAcceptOptionsValidator
{
    public static void Validate(QuestAcceptOptions options)
    {
        if (!double.IsFinite(options.MaxInteractionDistanceWu) ||
            options.MaxInteractionDistanceWu <= 0)
        {
            throw new InvalidOperationException(
                "P1:QuestAccept:MaxInteractionDistanceWu must be greater than zero.");
        }
    }
}
