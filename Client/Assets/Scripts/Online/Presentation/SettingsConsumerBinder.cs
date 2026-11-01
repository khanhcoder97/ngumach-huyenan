// OPC-14 A — Settings consumer binding (pure C#, no Unity dep).
// Binds SettingsPresenter.OnChanged to owned UI consumers so reduced motion/flash/
// input hints and text scale actually affect UI owned by OpenCode (not just prefs).
// World camera/VFX are out of scope and stay explicitly UNSUPPORTED.
// Owner: OpenCode LOCAL — Issue #85, #80 (work order 22, OPC-14 A).

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    /// <summary>Consumer of accessibility settings owned by OpenCode UI.</summary>
    public interface IUiAccessibilityConsumer
    {
        void ApplyAccessibility(SettingsViewState settings);
    }

    /// <summary>
    /// Subscribes to a SettingsPresenter and forwards changes to registered consumers.
    /// Rebind swaps the presenter without losing the consumer set.
    /// </summary>
    public sealed class SettingsConsumerBinder : IDisposable
    {
        private SettingsPresenter _presenter;
        private readonly List<IUiAccessibilityConsumer> _consumers = new List<IUiAccessibilityConsumer>();

        public SettingsConsumerBinder(SettingsPresenter presenter)
        {
            _presenter = presenter ?? throw new ArgumentNullException(nameof(presenter));
            _presenter.OnChanged += Notify;
            Notify();
        }

        public int ConsumerCount => _consumers.Count;

        public void Register(IUiAccessibilityConsumer consumer)
        {
            if (consumer == null) throw new ArgumentNullException(nameof(consumer));
            if (_consumers.Contains(consumer)) return;
            _consumers.Add(consumer);
            Notify(); // initial apply on register
        }

        public void Unregister(IUiAccessibilityConsumer consumer)
        {
            if (consumer == null) return;
            _consumers.Remove(consumer);
        }

        public void Rebind(SettingsPresenter newPresenter)
        {
            if (newPresenter == null) throw new ArgumentNullException(nameof(newPresenter));
            if (_presenter != null) _presenter.OnChanged -= Notify;
            _presenter = newPresenter;
            _presenter.OnChanged += Notify;
            Notify();
        }

        private void Notify()
        {
            if (_presenter == null || _presenter.Current == null) return;
            var s = _presenter.Current;
            // Snapshot to allow unregister during notify.
            var snapshot = _consumers.ToArray();
            foreach (var c in snapshot)
            {
                try { c.ApplyAccessibility(s); }
                catch (Exception) { /* a broken consumer must not break the settings pump */ }
            }
        }

        public void Dispose()
        {
            if (_presenter != null) _presenter.OnChanged -= Notify;
            _consumers.Clear();
            _presenter = null;
        }
    }
}
