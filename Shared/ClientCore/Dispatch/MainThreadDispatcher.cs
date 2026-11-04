// OPC-15 O5 — Main-thread dispatcher abstraction so portable core can request
// UI-thread execution without referencing an engine. Pure C#. Owner: OpenCode.

using System;
using System.Threading.Tasks;

namespace NguMach.Client.Core.Dispatch
{
    public interface IMainThreadDispatcher
    {
        bool IsMainThread { get; }
        void Post(Action action);
        Task InvokeAsync(Func<Task> action);
    }

    // Default synchronous dispatcher (for tests/headless). Godot supplies a real one.
    public sealed class SynchronousDispatcher : IMainThreadDispatcher
    {
        public bool IsMainThread => true;
        public void Post(Action action) { if (action != null) action(); }
        public async Task InvokeAsync(Func<Task> action) { if (action != null) await action(); }
    }
}
