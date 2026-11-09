// OPC-17 checkpoint 5 (O-G) — media bridge read model (pure C#).
// Validates Muse PLAYBACK_METADATA-shaped input, projects subtitle cues
// and playback position, and records seen/skipped/rewatched. All of it
// is presentation-only: nothing here grants quest progress, rewards or
// turn-ins. Codex owns the player/widgets. Owner: OpenCode.

using System;
using System.Collections.Generic;

namespace NguMach.Client.Presentation
{
    public sealed class MediaSubtitleCue
    {
        public double StartSeconds { get; }
        public double EndSeconds { get; }
        public string Text { get; }

        public MediaSubtitleCue(double startSeconds, double endSeconds, string text)
        {
            if (startSeconds < 0) throw new ArgumentException("cue start is negative");
            StartSeconds = startSeconds;
            EndSeconds = Math.Max(startSeconds, endSeconds);
            Text = text ?? "";
        }
    }

    public sealed class MediaMetadata
    {
        public string SceneId { get; }
        /// <summary>Source paths inside the approved content root only.</summary>
        public IReadOnlyList<string> AllowedPaths { get; }
        public bool EmbeddedSoundtrackOnly { get; }
        public IReadOnlyList<MediaSubtitleCue> SubtitleCues { get; }

        public MediaMetadata(string sceneId, string[] allowedPaths, bool embeddedSoundtrackOnly,
            IReadOnlyList<MediaSubtitleCue> subtitleCues)
        {
            if (string.IsNullOrWhiteSpace(sceneId)) throw new ArgumentException("scene id required");
            SceneId = sceneId;
            AllowedPaths = allowedPaths != null && allowedPaths.Length > 0
                ? Array.AsReadOnly((string[])allowedPaths.Clone())
                : Array.Empty<string>();
            EmbeddedSoundtrackOnly = embeddedSoundtrackOnly;
            if (subtitleCues != null)
            {
                var cues = new MediaSubtitleCue[subtitleCues.Count];
                for (int i = 0; i < subtitleCues.Count; i++)
                    cues[i] = subtitleCues[i];
                SubtitleCues = Array.AsReadOnly(cues);
            }
            else
            {
                SubtitleCues = Array.Empty<MediaSubtitleCue>();
            }
        }
    }

    public enum MediaPlaybackPhase { Idle, Playing, Paused, Ended, Fallback }

    public sealed class MediaPlaybackViewState
    {
        public string SceneId { get; }
        public MediaPlaybackPhase Phase { get; }
        public double ElapsedSeconds { get; }
        public double DurationSeconds { get; }
        public string CurrentSubtitle { get; }
        public bool HasSeen { get; }
        public bool WasSkipped { get; }
        public int RewatchCount { get; }
        public bool ReducedMotion { get; }
        /// <summary>Reason the bridge is in fallback instead of Playing.</summary>
        public string FallbackReason { get; }

        public MediaPlaybackViewState(string sceneId, MediaPlaybackPhase phase,
            double elapsedSeconds, double durationSeconds, string currentSubtitle,
            bool hasSeen, bool wasSkipped, int rewatchCount, bool reducedMotion, string fallbackReason)
        {
            SceneId = sceneId;
            Phase = phase;
            ElapsedSeconds = elapsedSeconds;
            DurationSeconds = durationSeconds;
            CurrentSubtitle = currentSubtitle ?? "";
            HasSeen = hasSeen;
            WasSkipped = wasSkipped;
            RewatchCount = rewatchCount;
            ReducedMotion = reducedMotion;
            FallbackReason = fallbackReason;
        }

        public double ProgressNormalized =>
            DurationSeconds > 0 ? Math.Min(1, Math.Max(0, ElapsedSeconds / DurationSeconds)) : 1;
    }

    public sealed class MediaPlaybackPresenter
    {
        private MediaMetadata _meta;
        private MediaPlaybackPhase _phase = MediaPlaybackPhase.Idle;
        private double _elapsed;
        private double _duration;
        private bool _hasSeen;
        private bool _wasSkipped;
        private int _rewatchCount;
        private bool _reducedMotion;
        private string _fallbackReason;

        public MediaPlaybackViewState View { get; private set; }
        public event Action OnChanged;

        public MediaPlaybackPresenter(bool reducedMotion = false)
        {
            _reducedMotion = reducedMotion;
            Publish();
        }

        public bool Load(MediaMetadata meta, double durationSeconds, bool codecSupported = true, string requestedPath = null)
        {
            if (meta == null) throw new ArgumentNullException(nameof(meta));
            if (durationSeconds <= 0) throw new ArgumentException("duration must be positive");
            _meta = meta;
            _duration = durationSeconds;
            _elapsed = 0;
            _hasSeen = false;
            _wasSkipped = false;
            _rewatchCount = 0;
            string fallback = Validate(meta, codecSupported, requestedPath);
            _fallbackReason = fallback;
            _phase = fallback != null ? MediaPlaybackPhase.Fallback : MediaPlaybackPhase.Playing;
            Publish();
            return fallback == null;
        }

        public static string Validate(MediaMetadata meta, bool codecSupported, string requestedPath)
        {
            if (meta == null) return "missing_metadata";
            if (!codecSupported) return "unsupported_codec";
            if (meta.EmbeddedSoundtrackOnly && requestedPath != null &&
                (requestedPath.IndexOf("vo_", StringComparison.OrdinalIgnoreCase) >= 0 ||
                 requestedPath.IndexOf("standalone", StringComparison.OrdinalIgnoreCase) >= 0))
                return "embedded_soundtrack_only";
            if (requestedPath != null)
            {
                bool allowed = false;
                for (int i = 0; i < meta.AllowedPaths.Count; i++)
                    allowed |= string.Equals(meta.AllowedPaths[i], requestedPath, StringComparison.Ordinal);
                if (!allowed) return "path_not_allowed";
            }            return null;
        }

        public double Seek(double seconds)
        {
            if (_meta == null || _phase == MediaPlaybackPhase.Idle || _phase == MediaPlaybackPhase.Fallback) return _elapsed;
            _elapsed = Math.Max(0, Math.Min(_duration, seconds));
            Publish();
            return _elapsed;
        }

        public void Pause() { if (_phase == MediaPlaybackPhase.Playing) { _phase = MediaPlaybackPhase.Paused; Publish(); } }
        public void Resume() { if (_phase == MediaPlaybackPhase.Paused) { _phase = MediaPlaybackPhase.Playing; Publish(); } }

        // Ending (natural, skipped or rewound) is presentation bookkeeping
        // only; it never advances quest/chapter state.
        public void End(bool skipped)
        {
            if (_phase == MediaPlaybackPhase.Playing || _phase == MediaPlaybackPhase.Paused ||
                (_phase == MediaPlaybackPhase.Fallback && _meta != null))
            {
                _hasSeen = true;
                _wasSkipped = skipped;
                _elapsed = skipped ? _elapsed : _duration;
                _phase = MediaPlaybackPhase.Ended;
                Publish();
            }
        }

        public void Rewatch()
        {
            if (_meta == null) return;
            _rewatchCount++;
            _wasSkipped = false;
            _elapsed = 0;
            _phase = _fallbackReason != null ? MediaPlaybackPhase.Fallback : MediaPlaybackPhase.Playing;
            Publish();
        }

        public void SetReducedMotion(bool reducedMotion)
        {
            _reducedMotion = reducedMotion;
            Publish();
        }

        public MediaPlaybackViewState Publish()
        {
            string cue = _meta != null ? CueAt(_meta, _elapsed) : "";
            View = new MediaPlaybackViewState(
                _meta != null ? _meta.SceneId : null, _phase, _elapsed, _duration, cue,
                _hasSeen, _wasSkipped, _rewatchCount, _reducedMotion, _fallbackReason);
            var handler = OnChanged;
            if (handler != null)
            {
                try { handler(); }
                catch (Exception) { /* consumer callback must not corrupt the presenter */ }
            }
            return View;
        }

        private static string CueAt(MediaMetadata meta, double elapsed)
        {
            for (int i = 0; i < meta.SubtitleCues.Count; i++)
            {
                var cue = meta.SubtitleCues[i];
                if (elapsed >= cue.StartSeconds && elapsed < cue.EndSeconds) return cue.Text;
            }
            return "";
        }
    }
}
