// OPC-17 gói39 O39-B — typed Muse PLAYBACK_METADATA_v1 bridge (pure C#).
// Parses the manifest Muse actually ships (branch muse/media-production-
// 20261104, pin b1472f2: 21 scenes, every one EMBEDDED_SOUNDTRACK_ONLY,
// OVERLAY_SRT with burnedIntoRuntimeVideo=false) plus real SRT files and
// canonical root-relative paths. The parser never widens the schema: a
// wrong manifest id, a missing required field or a stale counts block is
// an error, not a default. Path containment is canonical: traversal
// ("../.."), absolute paths and URI schemes outside the content root are
// rejected before anything is served. Ownership decisions are typed from
// the manifest (embedded soundtrack vs external mix alternates vs
// burned-subtitle review variants) — never from substrings like "vo_".
// Owner: OpenCode.

using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;
using Newtonsoft.Json.Linq;

namespace NguMach.Client.Presentation
{
    /// <summary>One video delivery of a scene (ogv or mp4) with its measured
    /// stream facts, exactly as the manifest records them.</summary>
    public sealed class MediaVideoDelivery
    {
        /// <summary>Root-relative path exactly as written in the manifest.</summary>
        public string Path { get; }
        public double DurationSecondsMeasured { get; }
        public string AudioCodec { get; }
        public int SampleRateHz { get; }
        public int Channels { get; }
        public int SubtitleStreamsEmbedded { get; }

        internal MediaVideoDelivery(string path, double durationSecondsMeasured,
            string audioCodec, int sampleRateHz, int channels, int subtitleStreamsEmbedded)
        {
            Path = path;
            DurationSecondsMeasured = durationSecondsMeasured;
            AudioCodec = audioCodec;
            SampleRateHz = sampleRateHz;
            Channels = channels;
            SubtitleStreamsEmbedded = subtitleStreamsEmbedded;
        }
    }

    /// <summary>Burned-subtitle review variant: REVIEW_ONLY_NOT_RUNTIME. It is
    /// never a runtime delivery and never plays with an SRT overlay on top.</summary>
    public sealed class MediaReviewOnlyVariant
    {
        public string Mp4SubVi { get; }
        public string ReadableSrt { get; }
        public string Status { get; }

        internal MediaReviewOnlyVariant(string mp4SubVi, string readableSrt, string status)
        {
            Mp4SubVi = mp4SubVi;
            ReadableSrt = readableSrt;
            Status = status;
        }
    }

    public sealed class MediaSubtitleInfo
    {
        public string Mode { get; }
        public bool BurnedIntoRuntimeVideo { get; }
        public string SrtPath { get; }
        public int CuesMeasured { get; }
        public MediaReviewOnlyVariant ReviewOnly { get; }

        internal MediaSubtitleInfo(string mode, bool burnedIntoRuntimeVideo, string srtPath,
            int cuesMeasured, MediaReviewOnlyVariant reviewOnly)
        {
            Mode = mode;
            BurnedIntoRuntimeVideo = burnedIntoRuntimeVideo;
            SrtPath = srtPath;
            CuesMeasured = cuesMeasured;
            ReviewOnly = reviewOnly;
        }
    }

    /// <summary>An external standalone mix that is the SAME mix as the embedded
    /// soundtrack delivered as a separate file (review / alternate routing).
    /// It is an alternate OF the embedded soundtrack, never a layer on top.</summary>
    public sealed class MediaExternalMixAlternate
    {
        public string MixVersion { get; }
        public string WavPath { get; }
        public string RuntimeCopyPath { get; }

        internal MediaExternalMixAlternate(string mixVersion, string wavPath, string runtimeCopyPath)
        {
            MixVersion = mixVersion;
            WavPath = wavPath;
            RuntimeCopyPath = runtimeCopyPath;
        }
    }

    /// <summary>Scene-level read model built by the strict parser from a real
    /// PLAYBACK_METADATA_v1 manifest. Hosts never craft this by hand.</summary>
    public sealed class MediaMetadata
    {
        public string SceneId { get; }
        public string Kind { get; }
        public double DurationSeconds { get; }
        public bool HasEmbeddedSoundtrack { get; }
        /// <summary>Raw manifest ownership value, e.g. "EMBEDDED_SOUNDTRACK_ONLY".</summary>
        public string AudioOwnership { get; }
        public string AudioOwnershipNote { get; }
        public MediaVideoDelivery VideoOgv { get; }
        public MediaVideoDelivery VideoMp4 { get; }
        public MediaSubtitleInfo Subtitle { get; }
        /// <summary>External copy of the embedded mix (sourceMixWav) — the same
        /// audio delivered as a file, never an extra layer under embedded policy.</summary>
        public string EmbeddedMixSourceWavPath { get; }
        public string EmbeddedMixSourceSha256 { get; }
        public IReadOnlyList<MediaExternalMixAlternate> ExternalMixAlternates { get; }
        /// <summary>Root-relative paths this scene actually serves at runtime:
        /// both video deliveries plus the SRT overlay file.</summary>
        public IReadOnlyList<string> RuntimeDeliveryPaths { get; }
        /// <summary>Attached after the SRT overlay is loaded; empty until then.
        /// Empty cues mean no subtitle text is served, never a silent grant.</summary>
        public IReadOnlyList<MediaSubtitleCue> SubtitleCues { get; private set; }
        /// <summary>Byte-level provenance of the manifest the scene came from,
        /// e.g. "sha256:... manifest=<relative path>".</summary>
        public string Provenance { get; private set; }

        internal MediaMetadata(string sceneId, string kind, double durationSeconds,
            bool hasEmbeddedSoundtrack, string audioOwnership, string audioOwnershipNote,
            MediaVideoDelivery videoOgv, MediaVideoDelivery videoMp4, MediaSubtitleInfo subtitle,
            string embeddedMixSourceWavPath, string embeddedMixSourceSha256,
            IReadOnlyList<MediaExternalMixAlternate> externalMixAlternates)
        {
            SceneId = sceneId;
            Kind = kind;
            DurationSeconds = durationSeconds;
            HasEmbeddedSoundtrack = hasEmbeddedSoundtrack;
            AudioOwnership = audioOwnership;
            AudioOwnershipNote = audioOwnershipNote;
            VideoOgv = videoOgv;
            VideoMp4 = videoMp4;
            Subtitle = subtitle;
            EmbeddedMixSourceWavPath = embeddedMixSourceWavPath;
            EmbeddedMixSourceSha256 = embeddedMixSourceSha256;
            ExternalMixAlternates = externalMixAlternates ?? (IReadOnlyList<MediaExternalMixAlternate>)new MediaExternalMixAlternate[0];

            var delivery = new List<string>(3);
            if (VideoOgv != null && !string.IsNullOrEmpty(VideoOgv.Path)) delivery.Add(VideoOgv.Path);
            if (VideoMp4 != null && !string.IsNullOrEmpty(VideoMp4.Path)) delivery.Add(VideoMp4.Path);
            if (Subtitle != null && !string.IsNullOrEmpty(Subtitle.SrtPath)) delivery.Add(Subtitle.SrtPath);
            RuntimeDeliveryPaths = delivery;

            SubtitleCues = Array.Empty<MediaSubtitleCue>();
        }

        /// <summary>Attaches subtitle cues loaded for this scene. Presentation
        /// data only: cues never grant gameplay state. The loader attaches
        /// after its canonical-path containment check; a host that loaded cues
        /// another way attaches here.</summary>
        public void AttachCues(IReadOnlyList<MediaSubtitleCue> cues)
        {
            SubtitleCues = cues ?? (IReadOnlyList<MediaSubtitleCue>)Array.Empty<MediaSubtitleCue>();
        }

        internal void AttachProvenance(string provenance)
        {
            if (!string.IsNullOrEmpty(provenance)) Provenance = provenance;
        }
    }

    public sealed class MediaMetadataParseResult
    {
        public bool Success { get; }
        public string Error { get; }
        public string ManifestId { get; }
        public int ScenesTotal { get; }
        public int WithEmbeddedSoundtrack { get; }
        public int Silent { get; }
        public IReadOnlyList<MediaMetadata> Scenes { get; }

        internal MediaMetadataParseResult(string error) { Success = false; Error = error; Scenes = Array.Empty<MediaMetadata>(); }
        internal MediaMetadataParseResult(string manifestId, int scenesTotal,
            int withEmbeddedSoundtrack, int silent, IReadOnlyList<MediaMetadata> scenes)
        {
            Success = true;
            ManifestId = manifestId;
            ScenesTotal = scenesTotal;
            WithEmbeddedSoundtrack = withEmbeddedSoundtrack;
            Silent = silent;
            Scenes = scenes;
        }
    }

    public sealed class MediaSrtParseResult
    {
        public bool Success { get; }
        public string Error { get; }
        public IReadOnlyList<MediaSubtitleCue> Cues { get; }

        internal MediaSrtParseResult(string error) { Success = false; Error = error; Cues = Array.Empty<MediaSubtitleCue>(); }
        internal MediaSrtParseResult(IReadOnlyList<MediaSubtitleCue> cues) { Success = true; Cues = cues; }
    }

    public sealed class MediaDocumentLoadResult
    {
        public bool Success { get; }
        public string Error { get; }
        public string DocumentPath { get; }
        public string Provenance { get; }
        public string ManifestId { get; }
        public int ScenesTotal { get; }
        public int WithEmbeddedSoundtrack { get; }
        public int Silent { get; }
        public IReadOnlyList<MediaMetadata> Scenes { get; }

        internal MediaDocumentLoadResult(string error) { Success = false; Error = error; Scenes = Array.Empty<MediaMetadata>(); }
        internal MediaDocumentLoadResult(string documentPath, string provenance,
            string manifestId, int scenesTotal, int withEmbeddedSoundtrack, int silent,
            IReadOnlyList<MediaMetadata> scenes)
        {
            Success = true;
            DocumentPath = documentPath;
            Provenance = provenance;
            ManifestId = manifestId;
            ScenesTotal = scenesTotal;
            WithEmbeddedSoundtrack = withEmbeddedSoundtrack;
            Silent = silent;
            Scenes = scenes;
        }
    }

    public sealed class MediaSrtLoadResult
    {
        public bool Success { get; }
        public string Error { get; }
        public string SrtPath { get; }
        public IReadOnlyList<MediaSubtitleCue> Cues { get; }

        internal MediaSrtLoadResult(string error) { Success = false; Error = error; Cues = Array.Empty<MediaSubtitleCue>(); }
        internal MediaSrtLoadResult(string srtPath, IReadOnlyList<MediaSubtitleCue> cues)
        { Success = true; SrtPath = srtPath; Cues = cues; }
    }

    /// <summary>Canonical path containment under one content root. Pure path
    /// logic, no filesystem access: canonicalize then require the result to
    /// stay inside the canonical root.</summary>
    public static class MediaPathPolicy
    {
        private static readonly Regex UriScheme = new Regex(
            "^[A-Za-z][A-Za-z0-9+.\\-]*://", RegexOptions.CultureInvariant);

        /// <summary>Canonical absolute form of the content root, or null.</summary>
        public static string CanonicalizeRoot(string root)
        {
            if (string.IsNullOrWhiteSpace(root)) return null;
            if (UriScheme.IsMatch(root)) return null;
            string full;
            try { full = Path.GetFullPath(root); }
            catch (Exception) { return null; }
            return full;
        }

        /// <summary>Canonical absolute path of a root-relative path, or null
        /// when the path is empty, carries a URI scheme/drive/ADS colon, is
        /// absolute, escapes the root (traversal) or cannot be canonicalized.
        /// Two platform traps are closed BEFORE any OS-specific semantics
        /// apply: a ':' is never legitimate in a root-relative delivery path
        /// (URI scheme, Windows drive letter, NTFS alternate stream — and on
        /// Unix it is a legal filename character, so "C:\Windows\evil.mp4"
        /// would otherwise slip containment as an ordinary in-root name),
        /// and separators are unified to '/' first so rooted, traversal and
        /// containment checks see one shape whether the caller passed
        /// manifest-style forward slashes or Path.Combine output. The
        /// canonical root itself is exempt (CanonicalizeRoot): it is a real
        /// filesystem path and ':'/'\' are its Windows shape.</summary>
        public static string TryCanonicalize(string contentRoot, string relativePath)
        {
            if (string.IsNullOrWhiteSpace(contentRoot) || string.IsNullOrWhiteSpace(relativePath)) return null;
            if (relativePath.IndexOf(':', StringComparison.Ordinal) >= 0) return null;
            string unified = relativePath.Replace('\\', '/');
            if (Path.IsPathRooted(unified)) return null;
            string rootFull;
            string full;
            try
            {
                rootFull = Path.GetFullPath(contentRoot);
                full = Path.GetFullPath(Path.Combine(rootFull, unified));
            }
            catch (Exception) { return null; }
            string prefix = rootFull.TrimEnd(Path.DirectorySeparatorChar, Path.AltDirectorySeparatorChar)
                + Path.DirectorySeparatorChar;
            if (!full.StartsWith(prefix, StringComparison.OrdinalIgnoreCase)) return null;
            return full;
        }
    }

    /// <summary>Strict PLAYBACK_METADATA_v1 parser: Muse manifest bytes in,
    /// typed scenes out, no schema widening and no invented defaults.</summary>
    public static class MediaPlaybackMetadataParser
    {
        public const string RequiredManifestId = "NGM_PLAYBACK_METADATA_V1";

        public static MediaMetadataParseResult Parse(string json)
        {
            if (string.IsNullOrWhiteSpace(json)) return new MediaMetadataParseResult("invalid_json");
            JObject obj;
            try
            {
                var token = JToken.Parse(json);
                obj = token as JObject;
            }
            catch (Exception) { return new MediaMetadataParseResult("invalid_json"); }
            if (obj == null) return new MediaMetadataParseResult("invalid_json");

            string manifestId = Str(obj, "manifestId");
            if (manifestId != RequiredManifestId) return new MediaMetadataParseResult("unsupported_manifest");

            if (!(obj["scenes"] is JArray scenesToken) || scenesToken.Count == 0)
                return new MediaMetadataParseResult("missing_scenes");

            var scenes = new List<MediaMetadata>(scenesToken.Count);
            int embedded = 0, silent = 0;
            foreach (var token in scenesToken)
            {
                var scene = token as JObject;
                if (scene == null) return new MediaMetadataParseResult("invalid_scene");
                string sceneId = ReqStr(scene, "sceneId");
                if (sceneId == null) return new MediaMetadataParseResult("scene_missing_sceneId");

                string kind = ReqStr(scene, "kind");
                if (kind == null) return Fail(sceneId, "kind");
                double? duration = ReqNumber(scene, "durationSeconds");
                if (duration == null || duration.Value <= 0) return Fail(sceneId, "durationSeconds");
                bool? hasEmbedded = ReqBool(scene, "hasEmbeddedSoundtrack");
                if (hasEmbedded == null) return Fail(sceneId, "hasEmbeddedSoundtrack");
                string ownership = ReqStr(scene, "audioOwnership");
                if (ownership == null) return Fail(sceneId, "audioOwnership");
                string ownershipNote = Str(scene, "audioOwnershipNote");

                if (!(scene["video"] is JObject video)) return Fail(sceneId, "video");
                if (!(video["ogv"] is JObject ogv)) return Fail(sceneId, "video_ogv");
                if (!(video["mp4"] is JObject mp4)) return Fail(sceneId, "video_mp4");
                var videoOgv = ReqVideo(sceneId, "video_ogv", ogv);
                if (videoOgv == null) return Fail(sceneId, "video_ogv");
                var videoMp4 = ReqVideo(sceneId, "video_mp4", mp4);
                if (videoMp4 == null) return Fail(sceneId, "video_mp4");

                if (!(scene["subtitle"] is JObject subtitle)) return Fail(sceneId, "subtitle");
                string mode = ReqStr(subtitle, "mode");
                if (mode == null) return Fail(sceneId, "subtitle_mode");
                bool? burned = ReqBool(subtitle, "burnedIntoRuntimeVideo");
                if (burned == null) return Fail(sceneId, "subtitle_burnedIntoRuntimeVideo");
                string srtPath = ReqStr(subtitle, "srtPath");
                if (srtPath == null) return Fail(sceneId, "subtitle_srtPath");
                int? cuesMeasured = ReqInt(subtitle, "cuesMeasured");
                if (cuesMeasured == null || cuesMeasured.Value < 0) return Fail(sceneId, "subtitle_cuesMeasured");
                MediaReviewOnlyVariant review = null;
                if (subtitle["reviewOnlyBakedVariant"] is JObject reviewToken)
                {
                    string mp4SubVi = ReqStr(reviewToken, "mp4SubVi");
                    if (mp4SubVi == null) return Fail(sceneId, "reviewOnly_mp4SubVi");
                    string readableSrt = ReqStr(reviewToken, "readableSrt");
                    if (readableSrt == null) return Fail(sceneId, "reviewOnly_readableSrt");
                    string status = ReqStr(reviewToken, "status");
                    if (status == null) return Fail(sceneId, "reviewOnly_status");
                    review = new MediaReviewOnlyVariant(mp4SubVi, readableSrt, status);
                }
                var subtitleInfo = new MediaSubtitleInfo(mode, burned.Value, srtPath, cuesMeasured.Value, review);

                string sourceMixWav = null, sourceMixSha = null;
                var alternates = new List<MediaExternalMixAlternate>();
                if (scene["embeddedMix"] is JObject embeddedMix)
                {
                    sourceMixWav = Str(embeddedMix, "sourceMixWav");
                    sourceMixSha = Str(embeddedMix, "sourceMixSha256");
                    if (embeddedMix["alternateStandaloneMixesNotEmbedded"] is JArray altToken)
                    {
                        foreach (var alt in altToken)
                        {
                            var altObj = alt as JObject;
                            if (altObj == null) return Fail(sceneId, "alternate_mix_invalid");
                            string mixVersion = ReqStr(altObj, "mixVersion");
                            if (mixVersion == null) return Fail(sceneId, "alternate_mix_version");
                            string wav = ReqStr(altObj, "wav");
                            if (wav == null) return Fail(sceneId, "alternate_mix_wav");
                            string runtimeCopy = ReqStr(altObj, "runtimeCopy");
                            if (runtimeCopy == null) return Fail(sceneId, "alternate_mix_runtimeCopy");
                            alternates.Add(new MediaExternalMixAlternate(mixVersion, wav, runtimeCopy));
                        }
                    }
                }

                scenes.Add(new MediaMetadata(sceneId, kind, duration.Value, hasEmbedded.Value,
                    ownership, ownershipNote, videoOgv, videoMp4, subtitleInfo,
                    sourceMixWav, sourceMixSha, alternates));
                if (hasEmbedded.Value) embedded++; else silent++;
            }

            if (obj["counts"] is JObject counts)
            {
                int? total = ReqInt(counts, "scenesTotal");
                if (total != null && total.Value != scenes.Count) return new MediaMetadataParseResult("counts_mismatch_scenesTotal");
                int? withEmbedded = ReqInt(counts, "withEmbeddedSoundtrack");
                if (withEmbedded != null && withEmbedded.Value != embedded) return new MediaMetadataParseResult("counts_mismatch_withEmbeddedSoundtrack");
                int? silentCount = ReqInt(counts, "silent");
                if (silentCount != null && silentCount.Value != silent) return new MediaMetadataParseResult("counts_mismatch_silent");
            }

            return new MediaMetadataParseResult(manifestId, scenes.Count, embedded, silent, scenes);
        }

        private static MediaMetadataParseResult Fail(string sceneId, string field)
        {
            return new MediaMetadataParseResult("scene_" + sceneId + "_missing_" + field);
        }

        private static MediaVideoDelivery ReqVideo(string sceneId, string prefix, JObject container)
        {
            string path = ReqStr(container, "path");
            if (path == null) return null;
            double? measured = ReqNumber(container, "durationSecondsMeasured");
            if (measured == null) return null;
            if (!(container["audioStream"] is JObject audio)) return null;
            string codec = ReqStr(audio, "codec");
            if (codec == null) return null;
            int? rate = ReqInt(audio, "sampleRateHz");
            if (rate == null) return null;
            int? channels = ReqInt(audio, "channels");
            if (channels == null) return null;
            int? subtitleStreams = ReqInt(container, "subtitleStreamsEmbedded");
            if (subtitleStreams == null) return null;
            return new MediaVideoDelivery(path, measured.Value, codec, rate.Value, channels.Value, subtitleStreams.Value);
        }

        private static string Str(JObject obj, string field)
        {
            var t = obj[field];
            if (t == null || t.Type == JTokenType.Null) return null;
            return t.Value<string>();
        }

        private static string ReqStr(JObject obj, string field)
        {
            var t = obj[field];
            if (t == null || t.Type == JTokenType.Null) return null;
            var value = t.Value<string>();
            return string.IsNullOrEmpty(value) ? null : value;
        }

        private static double? ReqNumber(JObject obj, string field)
        {
            var t = obj[field];
            if (t == null || t.Type != JTokenType.Float && t.Type != JTokenType.Integer) return null;
            return t.Value<double>();
        }

        private static int? ReqInt(JObject obj, string field)
        {
            var t = obj[field];
            if (t == null || t.Type != JTokenType.Integer) return null;
            return t.Value<int>();
        }

        private static bool? ReqBool(JObject obj, string field)
        {
            var t = obj[field];
            if (t == null || t.Type != JTokenType.Boolean) return null;
            return t.Value<bool>();
        }
    }

    /// <summary>Real SRT files in, typed cues out. Rejects missing indices,
    /// malformed timestamps, negative or reversed ranges and non-monotonic
    /// cue order — no widening, no guessed timings.</summary>
    public static class MediaSrtParser
    {
        private static readonly Regex Timestamp = new Regex(
            @"^(\d{2}):(\d{2}):(\d{2})([,.])(\d{1,3})$", RegexOptions.CultureInvariant);

        public static MediaSrtParseResult Parse(string srtText)
        {
            if (srtText == null) return new MediaSrtParseResult("missing_text");
            var text = srtText.Replace("\u00a0", " ");
            if (text.Length > 0 && text[0] == '\ufeff') text = text.Substring(1);
            text = text.Replace("\r\n", "\n").Replace('\r', '\n');
            var blocks = text.Split(new[] { "\n\n" }, StringSplitOptions.None);
            var cues = new List<MediaSubtitleCue>();
            double previousStart = -1;
            for (int b = 0; b < blocks.Length; b++)
            {
                var block = blocks[b];
                if (string.IsNullOrWhiteSpace(block)) continue;
                var lines = block.Split('\n');
                // Index line (may be absent only if the block is empty — a
                // block with no lines was already skipped above).
                if (lines.Length < 2) return new MediaSrtParseResult("srt_block_too_short");
                string indexLine = lines[0].Trim();
                if (indexLine.Length == 0 || !int.TryParse(indexLine, out int index) || index <= 0)
                    return new MediaSrtParseResult("srt_missing_index");

                string stampLine = lines[1].Trim();
                var parts = stampLine.Split(new[] { "-->" }, StringSplitOptions.None);
                if (parts.Length != 2) return new MediaSrtParseResult("srt_bad_timestamp_line");
                double? start = TryParseTimestamp(parts[0].Trim());
                double? end = TryParseTimestamp(parts[1].Trim());
                if (start == null || end == null) return new MediaSrtParseResult("srt_bad_timestamp");
                if (start.Value < 0 || end.Value < start.Value) return new MediaSrtParseResult("srt_bad_range");
                if (previousStart >= 0 && start.Value < previousStart) return new MediaSrtParseResult("srt_not_monotonic");
                previousStart = start.Value;

                var body = new StringBuilder();
                for (int i = 2; i < lines.Length; i++)
                {
                    if (body.Length > 0) body.Append('\n');
                    body.Append(lines[i]);
                }
                cues.Add(new MediaSubtitleCue(start.Value, end.Value, body.ToString()));
            }
            return new MediaSrtParseResult(cues);
        }

        private static double? TryParseTimestamp(string stamp)
        {
            var m = Timestamp.Match(stamp);
            if (!m.Success) return null;
            int hours = int.Parse(m.Groups[1].Value, System.Globalization.CultureInfo.InvariantCulture);
            int minutes = int.Parse(m.Groups[2].Value, System.Globalization.CultureInfo.InvariantCulture);
            int seconds = int.Parse(m.Groups[3].Value, System.Globalization.CultureInfo.InvariantCulture);
            int millis = int.Parse(m.Groups[5].Value, System.Globalization.CultureInfo.InvariantCulture);
            if (minutes >= 60 || seconds >= 60 || millis > 999 && m.Groups[5].Value.Length == 3) return null;
            millis = millis * (int)Math.Pow(10, 3 - m.Groups[5].Value.Length);
            if (hours < 0 || minutes < 0 || seconds < 0 || millis < 0) return null;
            return hours * 3600.0 + minutes * 60.0 + seconds + millis / 1000.0;
        }
    }

    /// <summary>Filesystem loader: canonicalize under the content root, read
    /// the real bytes, hash them for provenance, then run the strict parsers.
    /// Nothing is served from outside the canonical root.</summary>
    public static class MediaMetadataLoader
    {
        public static MediaDocumentLoadResult LoadDocument(string contentRoot, string relativeMetadataPath)
        {
            var canonical = MediaPathPolicy.TryCanonicalize(contentRoot, relativeMetadataPath);
            if (canonical == null) return new MediaDocumentLoadResult("metadata_path_outside_content_root");
            if (!File.Exists(canonical)) return new MediaDocumentLoadResult("metadata_file_missing");
            byte[] bytes;
            try { bytes = File.ReadAllBytes(canonical); }
            catch (Exception) { return new MediaDocumentLoadResult("metadata_file_unreadable"); }
            string json = Encoding.UTF8.GetString(bytes);
            var parsed = MediaPlaybackMetadataParser.Parse(json);
            if (!parsed.Success) return new MediaDocumentLoadResult(parsed.Error);
            string provenance = "sha256:" + Sha256Hex(bytes) + " manifest=" + relativeMetadataPath;
            foreach (var scene in parsed.Scenes) scene.AttachProvenance(provenance);
            return new MediaDocumentLoadResult(relativeMetadataPath, provenance,
                parsed.ManifestId, parsed.ScenesTotal, parsed.WithEmbeddedSoundtrack,
                parsed.Silent, parsed.Scenes);
        }

        /// <summary>Loads the scene's SRT overlay from the manifest path under
        /// the content root (canonical containment enforced), then attaches the
        /// cues to the scene. No cue is attached when anything fails.</summary>
        public static MediaSrtLoadResult LoadSrtCues(string contentRoot, MediaMetadata scene)
        {
            if (scene == null || scene.Subtitle == null || string.IsNullOrEmpty(scene.Subtitle.SrtPath))
                return new MediaSrtLoadResult("scene_has_no_srt_path");
            var canonical = MediaPathPolicy.TryCanonicalize(contentRoot, scene.Subtitle.SrtPath);
            if (canonical == null) return new MediaSrtLoadResult("srt_path_outside_content_root");
            if (!File.Exists(canonical)) return new MediaSrtLoadResult("srt_file_missing");
            string text;
            try { text = File.ReadAllText(canonical, Encoding.UTF8); }
            catch (Exception) { return new MediaSrtLoadResult("srt_file_unreadable"); }
            var parsed = MediaSrtParser.Parse(text);
            if (!parsed.Success) return new MediaSrtLoadResult(parsed.Error);
            scene.AttachCues(parsed.Cues);
            return new MediaSrtLoadResult(scene.Subtitle.SrtPath, parsed.Cues);
        }

        public static string Sha256Hex(byte[] bytes)
        {
            using (var sha = SHA256.Create())
            {
                var hash = sha.ComputeHash(bytes);
                var sb = new StringBuilder(hash.Length * 2);
                foreach (var b in hash) sb.Append(b.ToString("x2"));
                return sb.ToString();
            }
        }
    }
}
