using System.Collections.Concurrent;

namespace Server.Health.World;

public interface ISessionStore
{
    PlayerSession? Find(string sessionId);

    PlayerSession Add(PlayerSession session);
}

public sealed class InMemorySessionStore : ISessionStore
{
    private readonly ConcurrentDictionary<string, PlayerSession> _sessions =
        new(StringComparer.Ordinal);

    public PlayerSession? Find(string sessionId) =>
        _sessions.TryGetValue(sessionId, out var session) ? session : null;

    public PlayerSession Add(PlayerSession session)
    {
        if (!_sessions.TryAdd(session.SessionId, session))
        {
            throw new InvalidOperationException(
                $"Session '{session.SessionId}' already exists.");
        }

        return session;
    }
}
