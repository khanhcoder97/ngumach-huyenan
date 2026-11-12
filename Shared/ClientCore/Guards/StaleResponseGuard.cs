// OPC-15 O-B — Stale response / session guard for portable transport.
// A response is applicable only if its session id and request id match the
// currently active session/request. Old-session in-flight responses must never
// overwrite a new login. Pure C#, no engine dep.

using System;

namespace NguMach.Client.Core.Guards
{
    public sealed class SessionToken
    {
        public string SessionId { get; }
        public long Generation { get; }
        public SessionToken(string sessionId, long generation)
        {
            SessionId = sessionId ?? "";
            Generation = generation;
        }
    }

    public sealed class StaleResponseGuard
    {
        private SessionToken _active;
        private string _activeRequestId;

        public SessionToken Active => _active;

        public void BeginSession(string sessionId, long generation)
        {
            _active = new SessionToken(sessionId, generation);
            _activeRequestId = null;
        }

        public void EndSession()
        {
            _active = null;
            _activeRequestId = null;
        }

        public void BeginRequest(string requestId)
        {
            _activeRequestId = requestId;
        }

        // Returns true when the response may be applied to current state.
        public bool IsApplicable(string responseSessionId, string responseRequestId, long responseGeneration)
        {
            if (_active == null) return false;
            if (!string.Equals(responseSessionId, _active.SessionId, StringComparison.Ordinal)) return false;
            if (responseGeneration != 0 && responseGeneration != _active.Generation) return false;
            if (!string.IsNullOrEmpty(_activeRequestId) &&
                !string.IsNullOrEmpty(responseRequestId) &&
                !string.Equals(responseRequestId, _activeRequestId, StringComparison.Ordinal))
                return false;
            return true;
        }

        // Revision guard: a snapshot with an older revision must not overwrite a newer one.
        public static bool IsNewerRevision(long incomingRevision, long currentRevision)
        {
            return incomingRevision > currentRevision;
        }
    }
}
