using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Options;
using Server.Health.Contracts;
using Server.Health.World;

namespace Server.Health.Endpoints;

public static class P1Endpoints
{
    private const int MaxBodyBytes = 8 * 1024;
    private const string DefaultClassId = "CLASS_MINH_KIEM";

    public static IEndpointRouteBuilder MapP1Endpoints(this IEndpointRouteBuilder app)
    {
        app.MapPost("/p1/sessions", CreateSessionAsync);
        app.MapPost("/p1/move", MoveAsync);
        app.MapGet("/p1/world/{sessionId}", GetWorld);
        return app;
    }

    private static async Task<IResult> CreateSessionAsync(
        HttpContext context,
        ISessionStore sessions,
        MapBoundsCatalog maps,
        ServerClock clock,
        IOptions<P1WorldOptions> optionsAccessor,
        ILoggerFactory loggerFactory)
    {
        var options = optionsAccessor.Value;
        var requestId = NewRequestId();
        SessionCreateRequest? request = null;

        var (body, tooLarge) = await ReadBodyAsync(context);
        if (tooLarge)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status413PayloadTooLarge,
                P1ErrorCodes.InvalidPayload, ["body"]);
        }

        if (!string.IsNullOrWhiteSpace(body))
        {
            if (!context.Request.HasJsonContentType())
            {
                return P1Results.Error(
                    context, clock, requestId, StatusCodes.Status400BadRequest,
                    P1ErrorCodes.InvalidPayload, ["body"]);
            }

            try
            {
                request = JsonSerializer.Deserialize<SessionCreateRequest>(body, P1Json.Options);
            }
            catch (JsonException)
            {
                return P1Results.Error(
                    context, clock, requestId, StatusCodes.Status400BadRequest,
                    P1ErrorCodes.InvalidPayload, ["body"]);
            }
        }

        var fieldErrors = new List<string>();
        var characterId = request?.CharacterId;
        if (characterId is null)
        {
            characterId = $"CHR_{Guid.NewGuid():N}"[..12].ToUpperInvariant();
        }
        else if (!P1Validation.IsCharacterId(characterId))
        {
            fieldErrors.Add("characterId");
        }

        var classId = request?.ClassId ?? DefaultClassId;
        if (!string.Equals(classId, DefaultClassId, StringComparison.Ordinal))
        {
            fieldErrors.Add("classId");
        }

        if (fieldErrors.Count > 0)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, fieldErrors);
        }

        if (!maps.TryResolve(options.DefaultMapId, out _))
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status422UnprocessableEntity,
                P1ErrorCodes.InvalidMap, ["mapId"]);
        }

        string sessionId;
        do
        {
            sessionId = NewRequestId();
        }
        while (sessions.Find(sessionId) is not null);

        var now = clock.UtcNow;
        var session = new PlayerSession(
            sessionId,
            characterId!,
            classId,
            options.DefaultMapId,
            options.SpawnX,
            options.SpawnY,
            options.StartingHp,
            options.StartingMaxHp,
            options.StartingMp,
            options.StartingMaxMp,
            now);

        sessions.Add(session);
        var snapshot = WorldSnapshotFactory.Create(session, clock);

        loggerFactory.CreateLogger("P1.Sessions").LogInformation(
            "Session {SessionId} created for {CharacterId} on {MapId} at ({X},{Y})",
            session.SessionId,
            session.CharacterId,
            session.MapId,
            session.X,
            session.Y);

        context.Response.Headers["Location"] = $"/p1/world/{session.SessionId}";
        return P1Results.Success(
            requestId, session.SessionId, snapshot, StatusCodes.Status201Created);
    }

    private static async Task<IResult> MoveAsync(
        HttpContext context,
        ISessionStore sessions,
        MapBoundsCatalog maps,
        ServerClock clock,
        IOptions<P1WorldOptions> optionsAccessor,
        ILoggerFactory loggerFactory)
    {
        var options = optionsAccessor.Value;
        var requestId = NewRequestId();

        var (body, tooLarge) = await ReadBodyAsync(context);
        if (tooLarge)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status413PayloadTooLarge,
                P1ErrorCodes.InvalidPayload, ["body"]);
        }

        if (string.IsNullOrWhiteSpace(body) || !context.Request.HasJsonContentType())
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, ["body"]);
        }

        MoveEnvelope? envelope;
        try
        {
            envelope = JsonSerializer.Deserialize<MoveEnvelope>(body, P1Json.Options);
        }
        catch (JsonException)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, ["body"]);
        }

        if (envelope?.RequestId is { } incomingRequestId &&
            P1Validation.IsHex32(incomingRequestId))
        {
            requestId = incomingRequestId;
        }

        var fieldErrors = P1Validation.ValidateMoveEnvelope(envelope);
        if (fieldErrors.Count > 0)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, fieldErrors);
        }

        var sessionId = context.Request.Headers["X-Session-ID"].ToString().Trim();
        if (sessionId.Length == 0)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, ["X-Session-ID"]);
        }

        var session = sessions.Find(sessionId);
        if (session is null)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status404NotFound,
                P1ErrorCodes.SessionNotFound, ["X-Session-ID"]);
        }

        if (!string.Equals(envelope!.CharacterId, session.CharacterId, StringComparison.Ordinal))
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status400BadRequest,
                P1ErrorCodes.InvalidPayload, ["characterId"], session.Revision);
        }

        var payload = envelope.Payload!;
        var now = clock.UtcNow;
        WorldSnapshot snapshot;
        double finalX;
        double finalY;
        var logger = loggerFactory.CreateLogger("P1.Move");

        lock (session.SyncRoot)
        {
            if (!maps.TryResolve(session.MapId, out var bounds))
            {
                return P1Results.Error(
                    context, clock, requestId, StatusCodes.Status422UnprocessableEntity,
                    P1ErrorCodes.InvalidMap, ["mapId"], session.Revision);
            }

            var sequence = payload.InputSequence.GetValueOrDefault();
            if (sequence <= session.LastInputSequence)
            {
                return P1Results.Error(
                    context, clock, requestId, StatusCodes.Status409Conflict,
                    P1ErrorCodes.StaleSequence, ["payload.inputSequence"], session.Revision);
            }

            var elapsedSeconds = Math.Clamp(
                (now - session.LastMoveAtUtc).TotalSeconds, 0, options.MaxStepSeconds);
            var distance = options.MoveSpeedWuPerSecond * elapsedSeconds;
            if (distance > options.MaxStepDistanceWu + 1e-9)
            {
                return P1Results.Error(
                    context, clock, requestId, StatusCodes.Status422UnprocessableEntity,
                    P1ErrorCodes.MovementTooFar, ["payload"], session.Revision);
            }

            var moveX = payload.MoveX.GetValueOrDefault();
            var moveY = payload.MoveY.GetValueOrDefault();
            var magnitude = Math.Sqrt((moveX * moveX) + (moveY * moveY));
            if (magnitude > 0)
            {
                session.X = Math.Clamp(
                    session.X + (distance * (moveX / magnitude)), bounds.XMin, bounds.XMax);
                session.Y = Math.Clamp(
                    session.Y + (distance * (moveY / magnitude)), bounds.YMin, bounds.YMax);
            }

            session.LastInputSequence = sequence;
            session.LastMoveAtUtc = now;
            session.Revision++;
            finalX = session.X;
            finalY = session.Y;
            snapshot = WorldSnapshotFactory.Create(session, clock);
        }

        logger.LogDebug(
            "Accepted move {Sequence} for {SessionId} to ({X},{Y})",
            payload.InputSequence, session.SessionId, finalX, finalY);

        return P1Results.Success(requestId, session.SessionId, snapshot);
    }

    private static IResult GetWorld(
        HttpContext context,
        string sessionId,
        ISessionStore sessions,
        ServerClock clock)
    {
        var requestId = NewRequestId();
        var session = sessions.Find(sessionId.Trim());
        if (session is null)
        {
            return P1Results.Error(
                context, clock, requestId, StatusCodes.Status404NotFound,
                P1ErrorCodes.SessionNotFound, ["sessionId"]);
        }

        WorldSnapshot snapshot;
        lock (session.SyncRoot)
        {
            snapshot = WorldSnapshotFactory.Create(session, clock);
        }

        return P1Results.Success(requestId, session.SessionId, snapshot);
    }

    private static string NewRequestId() => Guid.NewGuid().ToString("N");

    private static async Task<(string? Body, bool TooLarge)> ReadBodyAsync(HttpContext context)
    {
        var buffer = new char[MaxBodyBytes + 1];
        var total = 0;

        using var reader = new StreamReader(
            context.Request.Body, Encoding.UTF8, detectEncodingFromByteOrderMarks: false,
            bufferSize: 1024, leaveOpen: true);

        while (total < buffer.Length)
        {
            var read = await reader.ReadAsync(
                buffer.AsMemory(total, buffer.Length - total), context.RequestAborted);
            if (read == 0)
            {
                break;
            }

            total += read;
        }

        return total > MaxBodyBytes
            ? (null, true)
            : (new string(buffer, 0, total), false);
    }
}
