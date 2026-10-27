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

    public static IResult Error(
        HttpContext context,
        ServerClock clock,
        string requestId,
        int statusCode,
        string code,
        IReadOnlyList<string>? fieldErrors = null,
        long? revision = null)
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
                Retryable = false,
                FieldErrors = fieldErrors ?? Array.Empty<string>(),
                CorrelationId = context.TraceIdentifier
            }
        };

        return Results.Json(response, statusCode: statusCode);
    }
}
