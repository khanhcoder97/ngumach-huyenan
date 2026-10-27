using System.Globalization;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Text.RegularExpressions;

namespace Server.Health.Contracts;

public static class P1Json
{
    public static readonly JsonSerializerOptions Options = new(JsonSerializerDefaults.Web)
    {
        UnmappedMemberHandling = JsonUnmappedMemberHandling.Disallow
    };
}

public static class P1Time
{
    private const string UtcFormat = "yyyy-MM-dd'T'HH:mm:ss'Z'";

    public static string ToUtcString(DateTimeOffset value) =>
        value.ToUniversalTime().ToString(UtcFormat, CultureInfo.InvariantCulture);
}

public static class P1ErrorCodes
{
    public const string InvalidPayload = "invalid_payload";
    public const string SessionNotFound = "session_not_found";
    public const string StaleSequence = "stale_sequence";
    public const string InvalidMap = "invalid_map";
    public const string MovementTooFar = "movement_too_far";
}

public static class P1Validation
{
    private const int CharacterIdMaxLength = 64;

    private static readonly Regex CharacterIdPattern =
        new(@"^CHR_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    private static readonly Regex UtcTimestampPattern =
        new(@"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
            RegexOptions.CultureInvariant);

    private static readonly Regex TargetIdPattern =
        new(@"^[A-Z][A-Z0-9_]*$", RegexOptions.CultureInvariant);

    private static readonly Regex SkillIdPattern =
        new(@"^SK-MK-0[1-3]$", RegexOptions.CultureInvariant);

    private static readonly Regex QuestIdPattern =
        new(@"^[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{2}$", RegexOptions.CultureInvariant);

    private static readonly Regex ObjectiveIdPattern =
        new(@"^OBJ_[A-Z0-9_]+$", RegexOptions.CultureInvariant);

    public static bool IsHex32(string? value)
    {
        if (value is null || value.Length != 32)
        {
            return false;
        }

        foreach (var character in value)
        {
            if (!char.IsAsciiDigit(character) && character is not (>= 'a' and <= 'f'))
            {
                return false;
            }
        }

        return true;
    }

    public static bool IsCharacterId(string? value) =>
        value is not null &&
        value.Length <= CharacterIdMaxLength &&
        CharacterIdPattern.IsMatch(value);

    public static bool IsTargetId(string? value) =>
        value is not null && TargetIdPattern.IsMatch(value);

    public static bool IsSkillId(string? value) =>
        value is not null && SkillIdPattern.IsMatch(value);

    public static bool IsQuestId(string? value) =>
        value is not null && QuestIdPattern.IsMatch(value);

    public static bool IsObjectiveId(string? value) =>
        value is not null && ObjectiveIdPattern.IsMatch(value);

    public static bool TryParseUtc(string? value, out DateTimeOffset parsed)
    {
        parsed = default;
        if (value is null || !UtcTimestampPattern.IsMatch(value))
        {
            return false;
        }

        return DateTimeOffset.TryParseExact(
            value,
            "yyyy-MM-dd'T'HH:mm:ss'Z'",
            CultureInfo.InvariantCulture,
            DateTimeStyles.AssumeUniversal | DateTimeStyles.AdjustToUniversal,
            out parsed);
    }

    public static List<string> ValidateMoveEnvelope(MoveEnvelope? envelope)
    {
        var errors = new List<string>();
        if (envelope is null)
        {
            errors.Add("body");
            return errors;
        }

        if (envelope.SchemaVersion != 1)
        {
            errors.Add("schemaVersion");
        }

        if (!IsHex32(envelope.RequestId))
        {
            errors.Add("requestId");
        }

        if (!IsHex32(envelope.IdempotencyKey))
        {
            errors.Add("idempotencyKey");
        }

        if (!TryParseUtc(envelope.SentAtUtc, out _))
        {
            errors.Add("sentAtUtc");
        }

        if (!IsCharacterId(envelope.CharacterId))
        {
            errors.Add("characterId");
        }

        if (envelope.Payload is null)
        {
            errors.Add("payload");
            return errors;
        }

        if (envelope.Payload.InputSequence is null ||
            envelope.Payload.InputSequence.Value < 1)
        {
            errors.Add("payload.inputSequence");
        }

        if (!IsUnitComponent(envelope.Payload.MoveX))
        {
            errors.Add("payload.moveX");
        }

        if (!IsUnitComponent(envelope.Payload.MoveY))
        {
            errors.Add("payload.moveY");
        }

        if (envelope.Payload.ClientTimeUtc is not null &&
            !TryParseUtc(envelope.Payload.ClientTimeUtc, out _))
        {
            errors.Add("payload.clientTimeUtc");
        }

        return errors;
    }

    private static bool IsUnitComponent(double? value) =>
        value is { } component &&
        double.IsFinite(component) &&
        component >= -1 &&
        component <= 1;
}
