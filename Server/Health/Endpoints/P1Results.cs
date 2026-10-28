using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Endpoints;

internal static class P1Results
{
    public static IResult Success(
        string requestId,
        string sessionId,
        WorldSnapshot snapshot,
        int statusCode = StatusCodes.Status200OK)
    {
        var response = new P1Response
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = snapshot.ServerTimeUtc,
            Revision = snapshot.Revision,
            Result = snapshot
        };

        return Results.Json(response, statusCode: statusCode);
    }

    public static IResult CombatSuccess(
        string requestId,
        string sessionId,
        CombatEvent combatEvent) =>
        Results.Json(new P1CombatResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = combatEvent.EmittedAtUtc,
            Revision = combatEvent.AggregateRevision,
            Result = combatEvent
        });

    public static IResult QuestsSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        IReadOnlyList<QuestState> states) =>
        Results.Json(new P1QuestListResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = states
        });

    public static IResult InventorySuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        InventorySnapshot snapshot) =>
        Results.Json(new P1InventoryResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = snapshot
        });

    public static IResult QuestAcceptSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        QuestState state) =>
        Results.Json(new P1QuestAcceptResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = state
        });

    public static IResult QuestAcceptError(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors,
        bool retryable,
        QuestState? state) =>
        Results.Json(
            new P1QuestAcceptResponse
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
                Result = state,
                Error = new P1Error
                {
                    Code = code,
                    MessageKey = $"P1.ERROR.{code.ToUpperInvariant()}",
                    Retryable = retryable,
                    FieldErrors = fieldErrors ?? Array.Empty<string>(),
                    CorrelationId = context.TraceIdentifier
                }
            },
            statusCode: statusCode);

    public static IResult Error(
        HttpContext context,
        ServerClock clock,
        string requestId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors = null,
        long? revision = null,
        bool retryable = false)
    {
        var response = new P1Response
        {
            RequestId = requestId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Revision = revision,
            Error = new P1Error
            {
                Code = code,
                MessageKey = $"P1.ERROR.{code.ToUpperInvariant()}",
                Retryable = retryable,
                FieldErrors = fieldErrors ?? Array.Empty<string>(),
                CorrelationId = context.TraceIdentifier
            }
        };

        return Results.Json(response, statusCode: statusCode);
    }
}
