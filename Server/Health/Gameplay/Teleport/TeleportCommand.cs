namespace Server.Health.Gameplay.Teleport;

public static class TeleportReasons
{
    public const string Quest = "QUEST";
    public const string DeathReturn = "DEATH_RETURN";
    public const string CityReturn = "CITY_RETURN";
    public const string Admin = "ADMIN";

    public static bool IsValid(string? value) =>
        string.Equals(value, Quest, StringComparison.Ordinal) ||
        string.Equals(value, DeathReturn, StringComparison.Ordinal) ||
        string.Equals(value, CityReturn, StringComparison.Ordinal) ||
        string.Equals(value, Admin, StringComparison.Ordinal);
}

public sealed record TeleportCommand(
    string? MapId,
    double XWu,
    double YWu,
    string? Reason);
