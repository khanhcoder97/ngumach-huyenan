// OPC-17 gói39 O39-B — media bridge read model (pure C#).
// Validates a scene built by the strict PLAYBACK_METADATA_v1 parser
// (MediaPlaybackMetadata.cs), projects subtitle cues and playback position,
// and records seen/skipped/rewatched. All of it is presentation-only:
// nothing here grants quest progress, rewards or turn-ins.
//
// Validation is canonical, not string-allowlist based: the requested path
// must canonicalize inside the content root AND belong to the scene's typed
// runtime delivery set. Under EMBEDDED_SOUNDTRACK_ONLY ownership only the
// video's own soundtrack plays — the external copy of the same mix
// (sourceMixWav) and the standalone alternates are named by the manifest and
// rejected by type, never by substring. Burned-subtitle review variants are
// excluded from runtime and never combine with the SRT overlay (no double
// captions). Codex owns the player/widgets. Owner: OpenCode.

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
        private readonly string _contentRoot;
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

        /// <summary>contentRoot is the canonical content root of this
        /// deployment; every requested path is canonicalized inside it.</summary>
        public MediaPlaybackPresenter(string contentRoot, bool reducedMotion = false)
        {
            _contentRoot = MediaPathPolicy.CanonicalizeRoot(contentRoot)
                ?? throw new ArgumentException("content root must be a valid absolute directory path", nameof(contentRoot));
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
            string fallback = Validate(meta, codecSupported, requestedPath, _contentRoot);
            _fallbackReason = fallback;
            _phase = fallback != null ? MediaPlaybackPhase.Fallback : MediaPlaybackPhase.Playing;
            Publish();
            return fallback == null;
        }

        /// <summary>Boundary validation for one playback request. Returns null
        /// when the request may play, otherwise a machine reason:
        /// missing_metadata, missing_content_root, unsupported_codec,
        /// missing_delivery_path, path_outside_content_root,
        /// burned_subtitle_review_not_runtime, embedded_soundtrack_only,
        /// path_not_allowed.</summary>
        public static string Validate(MediaMetadata meta, bool codecSupported, string requestedPath, string contentRoot)
        {
            if (meta == null) return "missing_metadata";
            if (string.IsNullOrWhiteSpace(contentRoot)) return "missing_content_root";
            if (!codecSupported) return "unsupported_codec";
            string effective = requestedPath ?? DefaultVideoPath(meta);
            if (effective == null) return "missing_delivery_path";

            // The requested path must canonicalize inside the content root.
            // Traversal, absolute paths and URI schemes die here even when a
            // caller "allowlists" them.
            if (MediaPathPolicy.TryCanonicalize(contentRoot, effective) == null)
                return "path_outside_content_root";

            // Burned-subtitle review variants are REVIEW_ONLY_NOT_RUNTIME.
            // They never play and never combine with the SRT overlay.
            var review = meta.Subtitle != null ? meta.Subtitle.ReviewOnly : null;
            if (review != null && (PathMatches(contentRoot, effective, review.Mp4SubVi) ||
                                   PathMatches(contentRoot, effective, review.ReadableSrt)))
                return "burned_subtitle_review_not_runtime";

            // The external copy of the embedded mix and the standalone
            // alternates are named by the manifest: under embedded ownership
            // they are alternates OF the soundtrack, never a second layer.
            if (MatchesExternalMix(meta, contentRoot, effective)) return "embedded_soundtrack_only";

            // Only the scene's own typed runtime delivery set may play.
            if (!PathMatchesAny(contentRoot, effective, meta.RuntimeDeliveryPaths))
                return "path_not_allowed";

            // Embedded ownership: the video (its own soundtrack) is the only
            // playable asset. The SRT file is an overlay, not a playable.
            if (meta.HasEmbeddedSoundtrack &&
                string.Equals(meta.AudioOwnership, "EMBEDDED_SOUNDTRACK_ONLY", StringComparison.Ordinal) &&
                !IsVideoPath(meta, contentRoot, effective))
                return "embedded_soundtrack_only";

            return null;
        }

        private static string DefaultVideoPath(MediaMetadata meta)
        {
            if (meta.VideoMp4 != null && !string.IsNullOrEmpty(meta.VideoMp4.Path)) return meta.VideoMp4.Path;
            if (meta.VideoOgv != null && !string.IsNullOrEmpty(meta.VideoOgv.Path)) return meta.VideoOgv.Path;
            return null;
        }

        private static bool IsVideoPath(MediaMetadata meta, string contentRoot, string requested)
        {
            return PathMatches(contentRoot, requested, meta.VideoOgv != null ? meta.VideoOgv.Path : null) ||
                   PathMatches(contentRoot, requested, meta.VideoMp4 != null ? meta.VideoMp4.Path : null);
        }

        private static bool MatchesExternalMix(MediaMetadata meta, string contentRoot, string requested)
        {
            if (PathMatches(contentRoot, requested, meta.EmbeddedMixSourceWavPath)) return true;
            for (int i = 0; i < meta.ExternalMixAlternates.Count; i++)
            {
                var alt = meta.ExternalMixAlternates[i];
                if (PathMatches(contentRoot, requested, alt.WavPath) ||
                    PathMatches(contentRoot, requested, alt.RuntimeCopyPath)) return true;
            }
            return false;
        }

        private static bool PathMatchesAny(string contentRoot, string requested, IReadOnlyList<string> candidates)
        {
            if (candidates == null) return false;
            for (int i = 0; i < candidates.Count; i++)
                if (PathMatches(contentRoot, requested, candidates[i])) return true;
            return false;
        }

        private static bool PathMatches(string contentRoot, string requested, string candidate)
        {
            if (string.IsNullOrEmpty(candidate)) return false;
            var a = MediaPathPolicy.TryCanonicalize(contentRoot, requested);
            var b = MediaPathPolicy.TryCanonicalize(contentRoot, candidate);
            return a != null && b != null && string.Equals(a, b, StringComparison.OrdinalIgnoreCase);
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
            string cue = _meta != null && OverlayAllowed(_meta) ? CueAt(_meta, _elapsed) : "";
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

        /// <summary>SRT overlay is served only on top of a clean runtime video:
        /// a burned subtitle track would double the captions.</summary>
        private static bool OverlayAllowed(MediaMetadata meta)
        {
            return meta.Subtitle == null || !meta.Subtitle.BurnedIntoRuntimeVideo;
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
