using System;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using UnityEngine.Networking;

namespace NguMach.Client.P1
{
    public sealed class P1UnityTransport : IP1Transport
    {
        private readonly Uri origin;
        private readonly int timeout;
        public P1UnityTransport(string baseUrl, int timeoutSeconds = 5)
        {
            if (!Uri.TryCreate(baseUrl.TrimEnd('/') + "/", UriKind.Absolute, out origin) ||
                (origin.Scheme != "http" && origin.Scheme != "https") || !string.IsNullOrEmpty(origin.UserInfo) ||
                !string.IsNullOrEmpty(origin.Query) || !string.IsNullOrEmpty(origin.Fragment) || origin.AbsolutePath != "/")
                throw new ArgumentException("P1 base URL must be an HTTP(S) origin, without credentials/path/query.");
            timeout = Math.Max(1, Math.Min(30, timeoutSeconds));
        }
        public async Task<P1HttpReply> SendAsync(P1Request input, CancellationToken ct)
        {
            ct.ThrowIfCancellationRequested();
            using (var req = new UnityWebRequest(new Uri(origin, input.Path).AbsoluteUri, input.Method))
            {
                req.timeout = timeout;
                req.redirectLimit = 0; // Do not forward session headers to a redirect target.
                req.downloadHandler = new DownloadHandlerBuffer();
                if (input.Body != null)
                {
                    req.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(input.Body));
                    req.SetRequestHeader("Content-Type", "application/json");
                }
                req.SetRequestHeader("X-Correlation-ID", input.CorrelationId);
                if (input.SessionId != null) req.SetRequestHeader("X-Session-ID", input.SessionId);
                var op = req.SendWebRequest();
                var done = new TaskCompletionSource<bool>();
                op.completed += _ => done.TrySetResult(true);
                if (op.isDone) done.TrySetResult(true);
                // Unity calls are made on Unity's main synchronization context.
                while (!done.Task.IsCompleted)
                {
                    if (ct.IsCancellationRequested) { req.Abort(); ct.ThrowIfCancellationRequested(); }
                    if (req.downloadedBytes > 1024 * 1024) { req.Abort(); return new P1HttpReply { StatusCode = 0 }; }
                    await Task.Yield();
                }
                ct.ThrowIfCancellationRequested();
                return new P1HttpReply
                {
                    StatusCode = req.result == UnityWebRequest.Result.ConnectionError ? 0 : (int)req.responseCode,
                    Body = req.downloadHandler.text,
                    CorrelationId = req.GetResponseHeader("X-Correlation-ID") ?? input.CorrelationId
                };
            }
        }
    }
}
