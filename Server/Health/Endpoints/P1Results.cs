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

    public static IResult InteractSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        InteractResult result) =>
        Results.Json(new P1InteractResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = result
        });

    public static IResult InteractError(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors,
        bool retryable) =>
        Results.Json(
            new P1InteractResponse
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
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

    public static IResult EquipmentSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        InventorySnapshot snapshot) =>
        Results.Json(new P1EquipmentResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = snapshot
        });

    public static IResult EquipmentError(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors,
        bool retryable,
        InventorySnapshot? snapshot = null) =>
        Results.Json(
            new P1EquipmentResponse
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
                Result = snapshot,
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

    // The v2 inventory answers carry schemaVersion 2 and the twelve-slot snapshot as
    // `result`, so a client never has to infer which vocabulary it is being served.
    // The death-return envelope carries one member the shared P1 error does not:
    // the tick a cooldown refusal may be retried at. It is declared on this
    // route's own error type so no other route's frozen error shape changes.
    public static IResult DeathReturn(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        DeathReturnResultV1? result = null,
        string? code = null,
        IReadOnlyList<string>? fieldErrors = null,
        bool retryable = false,
        long? nextReturnAllowedAtTick = null) =>
        Results.Json(
            new P1DeathReturnResponse
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
                Result = result,
                Error = code is null
                    ? null
                    : new DeathReturnErrorV1
                    {
                        Code = code,
                        MessageKey = $"P1.ERROR.{code.ToUpperInvariant()}",
                        Retryable = retryable,
                        FieldErrors = fieldErrors ?? Array.Empty<string>(),
                        CorrelationId = context.TraceIdentifier,
                        NextReturnAllowedAtTick = nextReturnAllowedAtTick
                    }
            },
            P1Json.Options,
            statusCode: statusCode);

    public static IResult InventoryV2(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        InventorySnapshotV2? result = null,
        string? code = null,
        IReadOnlyList<string>? fieldErrors = null,
        bool retryable = false) =>
        Results.Json(
            new P1InventoryV2Response
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
                Result = result,
                Error = code is null
                    ? null
                    : new P1Error
                    {
                        Code = code,
                        MessageKey = $"P1.ERROR.{code.ToUpperInvariant()}",
                        Retryable = retryable,
                        FieldErrors = fieldErrors ?? Array.Empty<string>(),
                        CorrelationId = context.TraceIdentifier
                    }
            },
            P1Json.Options,
            statusCode: statusCode);

    public static IResult TalkSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        Server.Health.Gameplay.Quests.TalkResult result) =>
        Results.Json(new P1TalkResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = result
        });

    public static IResult TalkError(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string? sessionId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors,
        bool retryable) =>
        Results.Json(new P1TalkResponse
        {
            RequestId = requestId,
            SessionId = string.IsNullOrEmpty(sessionId) ? null : sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Error = new P1Error
            {
                Code = code,
                MessageKey = $"P1.ERROR.{code.ToUpperInvariant()}",
                Retryable = retryable,
                FieldErrors = fieldErrors ?? Array.Empty<string>(),
                CorrelationId = context.TraceIdentifier
            }
        }, statusCode: statusCode);

    public static IResult TurnInSuccess(
        string requestId,
        string sessionId,
        ServerClock clock,
        TurnInResult result) =>
        Results.Json(new P1TurnInResponse
        {
            RequestId = requestId,
            SessionId = sessionId,
            ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
            Result = result
        });

    public static IResult TurnInError(
        HttpContext context,
        ServerClock clock,
        string requestId,
        string sessionId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors,
        bool retryable) =>
        Results.Json(
            new P1TurnInResponse
            {
                RequestId = requestId,
                SessionId = sessionId,
                ServerTimeUtc = P1Time.ToUtcString(clock.UtcNow),
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
}
