// OPC-15 O5 (WO26) — Factory for the portable composition root. Godot hosts call
// this instead of wiring transport/dispatcher/timeout themselves. Pure C#.
// Owner: OpenCode.

using System;
using NguMach.Client.Core.Dispatch;
using NguMach.Client.Core.Transport;

namespace NguMach.Client.Core.Composition
{
    public static class ClientSessionFactory
    {
        public static ClientSession CreateHttp(
            string baseUrl,
            string characterId = null,
            bool useWorldV2 = false,
            TimeSpan? requestTimeout = null,
            IMainThreadDispatcher dispatcher = null)
        {
            if (string.IsNullOrWhiteSpace(baseUrl))
                throw new ArgumentNullException(nameof(baseUrl));
            return new ClientSession(
                new HttpClientTransport(baseUrl),
                ownsTransport: true,
                useWorldV2: useWorldV2,
                requestTimeout: requestTimeout,
                dispatcher: dispatcher,
                characterId: characterId);
        }
    }
}
