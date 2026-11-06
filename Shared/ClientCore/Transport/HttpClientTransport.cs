// OPC-15 O5 — Real HttpClient transport for portable core (no Unity).
// Pure C#. Owner: OpenCode.

using System;
using System.Net.Http;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using NguMach.Client.P1;

namespace NguMach.Client.Core.Transport
{
    public sealed class HttpClientTransport : IP1Transport, IDisposable
    {
        private readonly HttpClient _client;
        private readonly string _baseUrl;
        private bool _disposed;

        public HttpClientTransport(string baseUrl, HttpClient client = null)
        {
            if (string.IsNullOrWhiteSpace(baseUrl)) throw new ArgumentNullException(nameof(baseUrl));
            _baseUrl = baseUrl.TrimEnd('/');
            _client = client ?? new HttpClient();
        }

        public async Task<P1HttpReply> SendAsync(P1Request request, CancellationToken ct)
        {
            if (_disposed) throw new ObjectDisposedException(nameof(HttpClientTransport));
            using (var msg = new HttpRequestMessage(new HttpMethod(request.Method), _baseUrl + request.Path))
            {
                if (request.SessionId != null) msg.Headers.TryAddWithoutValidation("X-Session-ID", request.SessionId);
                if (request.CorrelationId != null) msg.Headers.TryAddWithoutValidation("X-Correlation-ID", request.CorrelationId);
                if (request.Body != null) msg.Content = new StringContent(request.Body, Encoding.UTF8, "application/json");
                using (var reply = await _client.SendAsync(msg, ct))
                {
                    var body = await reply.Content.ReadAsStringAsync();
                    return new P1HttpReply { StatusCode = (int)reply.StatusCode, Body = body, CorrelationId = request.CorrelationId };
                }
            }
        }

        public void Dispose()
        {
            if (_disposed) return;
            _disposed = true;
            _client.Dispose();
        }
    }
}
