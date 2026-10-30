// CinemaViewState — Immutable view state for cinematic sequence overlay.
// Rules:
//   - Cinema does not pause the shared world (DEC-019).
//   - Skipping/replaying never grants duplicate or offline rewards.
//   - Preview harness explicitly labeled when Muse media contract is pending.
// Owner: Antigravity Remote — Issue #85.

using System;

namespace NguMach.Client.Presentation
{
    public enum CinemaPlaybackPhase
    {
        Idle,
        Loading,
        Playing,
        Ended,
        Fallback
    }

    public sealed class CinemaViewState
    {
        public string SceneId { get; }
        public string Title { get; }
        public string QuestId { get; }
        public float DurationSeconds { get; }
        public float ElapsedSeconds { get; }
        public string CurrentSubtitle { get; }
        public CinemaPlaybackPhase Phase { get; }
        public bool CanSkip { get; }
        public bool IsPreviewHarness { get; }
        public string FallbackNote { get; }

        public CinemaViewState(
            string sceneId,
            string title,
            string questId,
            float durationSeconds,
            float elapsedSeconds,
            string currentSubtitle,
            CinemaPlaybackPhase phase,
            bool canSkip = true,
            bool isPreviewHarness = true,
            string fallbackNote = "(Preview Harness — Video Muse runtime contract not yet integrated)")
        {
            SceneId = sceneId;
            Title = title;
            QuestId = questId;
            DurationSeconds = durationSeconds;
            ElapsedSeconds = elapsedSeconds;
            CurrentSubtitle = currentSubtitle;
            Phase = phase;
            CanSkip = canSkip;
            IsPreviewHarness = isPreviewHarness;
            FallbackNote = fallbackNote;
        }

        public float ProgressNormalized => DurationSeconds > 0f ? Math.Min(1f, Math.Max(0f, ElapsedSeconds / DurationSeconds)) : 1f;
        public bool IsPlaying => Phase == CinemaPlaybackPhase.Playing;
        public bool IsEnded => Phase == CinemaPlaybackPhase.Ended;
    }
}
