namespace Server.Health.Gameplay.Interactions;

public sealed class InteractionOptions
{
    public const string SectionName = "P1:Interact";

    public bool Enabled { get; set; }

    public double MaxInteractionDistanceWu { get; set; } = 5;

    // DEV FIXTURE: P1 has no profession progression yet, so gather gates compare
    // against this assumed level instead of a per-character profession state.
    public int AssumedProfessionLevel { get; set; } = 1;
}

public static class InteractionOptionsValidator
{
    public static void Validate(InteractionOptions options)
    {
        if (!double.IsFinite(options.MaxInteractionDistanceWu) ||
            options.MaxInteractionDistanceWu <= 0)
        {
            throw new InvalidOperationException(
                "P1:Interact:MaxInteractionDistanceWu must be greater than zero.");
        }

        if (options.AssumedProfessionLevel < 1)
        {
            throw new InvalidOperationException(
                "P1:Interact:AssumedProfessionLevel must be at least 1.");
        }
    }
}
