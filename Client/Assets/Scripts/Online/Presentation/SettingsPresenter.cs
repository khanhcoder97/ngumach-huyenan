// AG4 — SettingsPresenter: manages local preferences (version/default/reset).
// Settings are local preference only — NOT character save or offline MMO progression.
// Hooks that are unsupported show "unsupported" state — never fake success.
// Owner: Antigravity Remote — Issue #80.

using System;

namespace NguMach.Client.Presentation
{
    public sealed class SettingsPresenter
    {
        private SettingsViewState _current;
        private readonly ISettingsStore _store;

        public SettingsViewState Current => _current;
        public event Action OnChanged;

        public SettingsPresenter(ISettingsStore store)
        {
            _store = store ?? throw new ArgumentNullException(nameof(store));
            _current = _store.Load() ?? SettingsViewState.Default;
        }

        public void SetUiScale(float v) { _current = new SettingsViewState(v, _current.MasterVolume, _current.TextSize, _current.ReducedMotion, _current.ReducedFlash, _current.ShowInputHints); Save(); }
        public void SetMasterVolume(float v) { _current = new SettingsViewState(_current.UiScale, v, _current.TextSize, _current.ReducedMotion, _current.ReducedFlash, _current.ShowInputHints); Save(); }
        public void SetTextSize(float v) { _current = new SettingsViewState(_current.UiScale, _current.MasterVolume, v, _current.ReducedMotion, _current.ReducedFlash, _current.ShowInputHints); Save(); }
        public void SetReducedMotion(bool v) { _current = new SettingsViewState(_current.UiScale, _current.MasterVolume, _current.TextSize, v, _current.ReducedFlash, _current.ShowInputHints); Save(); }
        public void SetReducedFlash(bool v) { _current = new SettingsViewState(_current.UiScale, _current.MasterVolume, _current.TextSize, _current.ReducedMotion, v, _current.ShowInputHints); Save(); }
        public void SetInputHints(bool v) { _current = new SettingsViewState(_current.UiScale, _current.MasterVolume, _current.TextSize, _current.ReducedMotion, _current.ReducedFlash, v); Save(); }

        public void Reset() { _current = SettingsViewState.Default; Save(); }

        private void Save() { _store.Save(_current); OnChanged?.Invoke(); }
    }

    /// <summary>Persistence back-end for settings (version-aware). Unity PlayerPrefs or JSON file.</summary>
    public interface ISettingsStore
    {
        SettingsViewState Load();
        void Save(SettingsViewState settings);
    }
}
