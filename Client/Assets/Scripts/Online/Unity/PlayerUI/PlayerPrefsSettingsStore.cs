// AG4 — ISettingsStore implementation using Unity PlayerPrefs.
// Version-aware: if stored version < current, resets to default to avoid stale schema.
// Owner: Antigravity Remote — Issue #80.

using UnityEngine;

namespace NguMach.Client.Presentation
{
    /// <summary>
    /// Persists <see cref="SettingsViewState"/> via Unity PlayerPrefs.
    /// Schema version bump resets to default rather than loading corrupt keys.
    /// Inherits from MonoBehaviour so it can be placed in scene and found via FindFirstObjectByType.
    /// </summary>
    public class PlayerPrefsSettingsStore : MonoBehaviour, ISettingsStore
    {
        private const string KeyVersion       = "ag_settings_version";
        private const string KeyUiScale       = "ag_ui_scale";
        private const string KeyVolume        = "ag_master_volume";
        private const string KeyTextSize      = "ag_text_size";
        private const string KeyReducedMotion = "ag_reduced_motion";
        private const string KeyReducedFlash  = "ag_reduced_flash";
        private const string KeyInputHints    = "ag_input_hints";
        private const int    CurrentVersion   = 1;

        public SettingsViewState Load()
        {
            int stored = PlayerPrefs.GetInt(KeyVersion, 0);
            if (stored != CurrentVersion) return null; // schema changed → use defaults
            return new SettingsViewState(
                uiScale:       PlayerPrefs.GetFloat(KeyUiScale,       1f),
                masterVolume:  PlayerPrefs.GetFloat(KeyVolume,        1f),
                textSize:      PlayerPrefs.GetFloat(KeyTextSize,      1f),
                reducedMotion: PlayerPrefs.GetInt(KeyReducedMotion, 0) == 1,
                reducedFlash:  PlayerPrefs.GetInt(KeyReducedFlash,  0) == 1,
                showInputHints:PlayerPrefs.GetInt(KeyInputHints,    1) == 1);
        }

        public void Save(SettingsViewState s)
        {
            if (s == null) return;
            PlayerPrefs.SetInt(KeyVersion,        CurrentVersion);
            PlayerPrefs.SetFloat(KeyUiScale,      s.UiScale);
            PlayerPrefs.SetFloat(KeyVolume,       s.MasterVolume);
            PlayerPrefs.SetFloat(KeyTextSize,     s.TextSize);
            PlayerPrefs.SetInt(KeyReducedMotion,  s.ReducedMotion  ? 1 : 0);
            PlayerPrefs.SetInt(KeyReducedFlash,   s.ReducedFlash   ? 1 : 0);
            PlayerPrefs.SetInt(KeyInputHints,     s.ShowInputHints ? 1 : 0);
            PlayerPrefs.Save();
        }
    }
}
