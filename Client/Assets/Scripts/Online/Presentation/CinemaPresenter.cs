// CinemaPresenter — Presentation controller for Muse cinematic sequence.
// Rules:
//   - Cinema does not pause the shared world (DEC-019).
//   - Skipping/replaying never grants rewards locally.
//   - Sourced from Cinema_Production_Pack_v1.json.
// Owner: Antigravity Remote — Issue #85.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    public sealed class CinemaPresenter
    {
        private CinemaViewState _state;
        public CinemaViewState State => _state;
        public event Action OnChanged;

        private static readonly Dictionary<string, (string title, string questId, float duration, string[] subtitles)> Scenes =
            new Dictionary<string, (string, string, float, string[])>(StringComparer.OrdinalIgnoreCase)
            {
                ["CIN_001"] = (
                    "Nước không soi bóng",
                    "P00-01",
                    36f,
                    new[]
                    {
                        "Bến Mưa lúc rạng đông... sương mờ che khuất mặt sông.",
                        "Một phong thư lạ lạc giữa bến trúc.",
                        "Dưới đáy nước, có bóng chuông đồng ẩn hiện.",
                        "Năm vết khắc trên sáp niêm phong... Huyền Ấn vẫn còn nguyên vẹn."
                    }
                )
            };

        public CinemaPresenter()
        {
            _state = new CinemaViewState(null, null, null, 0f, 0f, null, CinemaPlaybackPhase.Idle);
        }

        public void Play(string sceneId)
        {
            if (string.IsNullOrEmpty(sceneId)) return;

            if (Scenes.TryGetValue(sceneId, out var s))
            {
                _state = new CinemaViewState(
                    sceneId,
                    s.title,
                    s.questId,
                    s.duration,
                    0f,
                    s.subtitles.Length > 0 ? s.subtitles[0] : "",
                    CinemaPlaybackPhase.Playing);
            }
            else
            {
                _state = new CinemaViewState(
                    sceneId,
                    sceneId,
                    null,
                    10f,
                    0f,
                    "Phân cảnh mẫu (chưa có video Muse)",
                    CinemaPlaybackPhase.Fallback);
            }
            OnChanged?.Invoke();
        }

        public void Update(float deltaSeconds)
        {
            if (_state == null || (_state.Phase != CinemaPlaybackPhase.Playing && _state.Phase != CinemaPlaybackPhase.Fallback))
                return;

            float newElapsed = _state.ElapsedSeconds + deltaSeconds;
            if (newElapsed >= _state.DurationSeconds)
            {
                EndPlayback();
                return;
            }

            string subtitle = _state.CurrentSubtitle;
            if (Scenes.TryGetValue(_state.SceneId, out var s) && s.subtitles.Length > 0)
            {
                int subIndex = (int)((newElapsed / _state.DurationSeconds) * s.subtitles.Length);
                subIndex = Math.Max(0, Math.Min(s.subtitles.Length - 1, subIndex));
                subtitle = s.subtitles[subIndex];
            }

            _state = new CinemaViewState(
                _state.SceneId,
                _state.Title,
                _state.QuestId,
                _state.DurationSeconds,
                newElapsed,
                subtitle,
                _state.Phase,
                _state.CanSkip,
                _state.IsPreviewHarness,
                _state.FallbackNote);
            OnChanged?.Invoke();
        }

        public void Skip()
        {
            EndPlayback();
        }

        private void EndPlayback()
        {
            _state = new CinemaViewState(
                _state?.SceneId,
                _state?.Title,
                _state?.QuestId,
                _state?.DurationSeconds ?? 0f,
                _state?.DurationSeconds ?? 0f,
                "",
                CinemaPlaybackPhase.Ended,
                canSkip: false,
                _state?.IsPreviewHarness ?? true,
                _state?.FallbackNote);
            OnChanged?.Invoke();
        }

        public void Close()
        {
            _state = new CinemaViewState(null, null, null, 0f, 0f, null, CinemaPlaybackPhase.Idle);
            OnChanged?.Invoke();
        }
    }
}
