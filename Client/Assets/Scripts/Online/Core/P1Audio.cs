using System;
using System.Collections.Generic;
using Newtonsoft.Json;

namespace NguMach.Client.P1
{
    [Serializable] public sealed class P1AudioCatalog
    {
        public int schemaVersion;
        public string packId;
        public Dictionary<string, int> voiceCaps;
        public P1AudioDucking warningDucking;
        public P1AudioCue[] cues;
        public static P1AudioCatalog Parse(string json)
        {
            var c = JsonConvert.DeserializeObject<P1AudioCatalog>(json);
            if (c == null || c.schemaVersion != 1 || c.packId != "NGM_ORIGINAL_AUDIO_V1" || c.cues == null || c.voiceCaps == null || c.warningDucking == null)
                throw new ArgumentException("Invalid audio catalog");
            var keys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var paths = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var duck = c.warningDucking;
            if (!Finite(duck.musicAmbienceGainMultiplier) || duck.musicAmbienceGainMultiplier < 0 || duck.musicAmbienceGainMultiplier > 1 ||
                duck.attackMs < 1 || duck.attackMs > 1000 || duck.holdMs < 0 || duck.holdMs > 10000 || duck.releaseMs < 1 || duck.releaseMs > 10000)
                throw new ArgumentException("Invalid warning ducking");
            foreach (var cap in c.voiceCaps) if (cap.Value < 1 || cap.Value > 64) throw new ArgumentException("Invalid voice cap");
            foreach (var cue in c.cues)
            {
                if (cue == null || string.IsNullOrEmpty(cue.cueKey) || !keys.Add(cue.cueKey) ||
                    !SafeKey(cue.cueKey) || !c.voiceCaps.ContainsKey(cue.voiceGroup ?? "") ||
                    !P1AudioSettings.ValidBus(cue.bus) || cue.bus == "Master" || !Finite(cue.gain) || cue.gain < 0 || cue.gain > 1 ||
                    cue.priority < 0 || cue.priority > 100 || cue.maxInstances < 1 || cue.maxInstances > c.voiceCaps[cue.voiceGroup] ||
                    cue.minGapMs < 0 || cue.minGapMs > 60000 || string.IsNullOrEmpty(cue.triggerSemantic) ||
                    !Finite(cue.minDistanceWu) || !Finite(cue.maxDistanceWu) || cue.minDistanceWu < 0 || cue.maxDistanceWu < cue.minDistanceWu ||
                    cue.clips == null || cue.clips.Length < 1 || cue.clips.Length > 16)
                    throw new ArgumentException("Invalid audio cue");
                foreach (var clip in cue.clips)
                    if (clip == null || !SafePath(clip.path) || !paths.Add(clip.path) || !Finite(clip.durationSeconds) || clip.durationSeconds <= 0 || clip.durationSeconds > 90)
                        throw new ArgumentException("Invalid audio clip");
            }
            return c;
        }
        internal static bool Finite(double n) { return !double.IsNaN(n) && !double.IsInfinity(n); }
        private static bool SafeKey(string key)
        {
            if (!(key.StartsWith("SFX/", StringComparison.Ordinal) || key.StartsWith("MUSIC/", StringComparison.Ordinal) || key.StartsWith("AMBIENCE/", StringComparison.Ordinal))) return false;
            foreach (char ch in key) if (!(ch >= 'a' && ch <= 'z') && !(ch >= 'A' && ch <= 'Z') && !(ch >= '0' && ch <= '9') && ch != '_' && ch != '/') return false;
            return !key.EndsWith("/", StringComparison.Ordinal) && !key.Contains("//");
        }
        private static bool SafePath(string path)
        { return path != null && path.StartsWith("Client/Assets/Audio/PackV1/", StringComparison.Ordinal) &&
            !path.Contains("..") && !path.Contains("\\") && !path.Contains(":") &&
            (path.EndsWith(".wav", StringComparison.Ordinal) || path.EndsWith(".ogg", StringComparison.Ordinal)); }
    }
    [Serializable] public sealed class P1AudioDucking
    { public double musicAmbienceGainMultiplier; public int attackMs, holdMs, releaseMs; }
    [Serializable] public sealed class P1AudioCue
    {
        public string cueKey, bus, voiceGroup, triggerSemantic, variationSelector;
        public int priority, maxInstances, minGapMs;
        public double gain, minDistanceWu, maxDistanceWu;
        public bool loop;
        public P1AudioClipInfo[] clips;
        public bool Spatial { get { return bus == "SFX" && maxDistanceWu > 0; } }
    }
    [Serializable] public sealed class P1AudioClipInfo { public string path; public double durationSeconds; }

    [Serializable] public sealed class P1AudioSettings
    {
        public double master = 0.7, music = 0.65, ambience = 0.6, sfx = 0.8, ui = 0.7;
        public bool muted;
        public static bool ValidBus(string bus) { return bus == "Master" || bus == "Music" || bus == "Ambience" || bus == "SFX" || bus == "UI"; }
        public void SetGain(string bus, double value)
        {
            if (!ValidBus(bus) || !P1AudioCatalog.Finite(value)) throw new ArgumentException("Invalid mixer gain");
            value = Math.Max(0, Math.Min(1, value));
            switch (bus) { case "Master": master = value; break; case "Music": music = value; break;
                case "Ambience": ambience = value; break; case "SFX": sfx = value; break; case "UI": ui = value; break; }
        }
        public double GetGain(string bus)
        { switch (bus) { case "Master": return master; case "Music": return music; case "Ambience": return ambience; case "SFX": return sfx; case "UI": return ui; default: return 0; } }
        public static P1AudioSettings FromJson(string json)
        {
            try
            {
                var saved = JsonConvert.DeserializeObject<P1AudioSettings>(json);
                if (saved == null) return new P1AudioSettings();
                foreach (var bus in new[] { "Master", "Music", "Ambience", "SFX", "UI" }) saved.SetGain(bus, saved.GetGain(bus));
                return saved;
            }
            catch (Exception e) when (e is JsonException || e is ArgumentException) { return new P1AudioSettings(); }
        }
    }
    public sealed class P1AudioSignal
    {
        public string scope, eventId, cueKey, semantic;
        public int hitIndex = -1;
        public bool confirmed, audienceAllowed = true;
        public double? x, y;
    }
    public sealed class P1AudioVoice
    {
        public long id;
        public P1AudioCue cue;
        public int variant;
        public double startedAt, endsAt;
        public double? x, y;
    }
    public sealed class P1AudioDecision
    {
        public string reason;
        public P1AudioVoice voice;
        public readonly List<long> stopped = new List<long>();
        public bool Accepted { get { return voice != null; } }
    }

    // Presentation policy only. Confirmation/audience comes from a trusted adapter,
    // never from an unvalidated network body or an animation marker.
    public sealed class P1AudioPolicy
    {
        private readonly Dictionary<string, P1AudioCue> cues = new Dictionary<string, P1AudioCue>(StringComparer.Ordinal);
        private readonly Dictionary<string, int> caps;
        private readonly P1AudioDucking ducking;
        private readonly Dictionary<long, P1AudioVoice> voices = new Dictionary<long, P1AudioVoice>();
        private readonly Dictionary<string, double> lastStarts = new Dictionary<string, double>();
        private readonly Dictionary<string, int> nextVariant = new Dictionary<string, int>();
        private readonly HashSet<Tuple<string, string, string, int>> seen = new HashSet<Tuple<string, string, string, int>>();
        private readonly Queue<Tuple<string, string, string, int>> seenOrder = new Queue<Tuple<string, string, string, int>>();
        private string scope;
        private long nextId;
        private double duckStart = double.NegativeInfinity, duckEnd = double.NegativeInfinity, duckFrom = 1;
        public P1AudioSettings Settings { get; private set; }
        public int ActiveCount { get { return voices.Count; } }
        public P1AudioPolicy(P1AudioCatalog catalog, P1AudioSettings settings)
        { caps = catalog.voiceCaps; ducking = catalog.warningDucking; Settings = settings ?? throw new ArgumentNullException(nameof(settings)); foreach (var c in catalog.cues) cues.Add(c.cueKey, c); }
        public P1AudioCue Find(string key) { P1AudioCue c; return key != null && cues.TryGetValue(key, out c) ? c : null; }
        public List<long> SetScope(string value)
        {
            if (scope == value) return new List<long>();
            var stop = new List<long>(voices.Keys); voices.Clear(); scope = value;
            seen.Clear(); seenOrder.Clear(); lastStarts.Clear(); nextVariant.Clear();
            duckStart = duckEnd = double.NegativeInfinity; duckFrom = 1; return stop;
        }
        public List<long> Advance(double now)
        {
            var stop = new List<long>();
            foreach (var pair in voices) if (!pair.Value.cue.loop && pair.Value.endsAt <= now) stop.Add(pair.Key);
            foreach (long id in stop) voices.Remove(id);
            return stop;
        }
        public void Release(long id) { voices.Remove(id); }
        public P1AudioDecision Admit(P1AudioSignal s, double now)
        {
            var result = new P1AudioDecision();
            result.stopped.AddRange(Advance(now));
            var c = s == null ? null : Find(s.cueKey);
            if (!P1AudioCatalog.Finite(now) || c == null || string.IsNullOrEmpty(scope) || s.scope != scope || string.IsNullOrEmpty(s.eventId) || !s.audienceAllowed)
            { result.reason = "scope_or_audience"; return result; }
            bool localUi = c.cueKey == "SFX/UI/focus" || c.cueKey == "SFX/UI/confirm" || c.cueKey == "SFX/UI/error" || c.cueKey == "SFX/UI/panel_open" || c.cueKey == "SFX/UI/panel_close";
            if (s.semantic != c.triggerSemantic || (!s.confirmed && !localUi)) { result.reason = "semantic_not_confirmed"; return result; }
            if (c.Spatial && (!s.x.HasValue || !s.y.HasValue || !P1AudioCatalog.Finite(s.x.Value) || !P1AudioCatalog.Finite(s.y.Value)))
            { result.reason = "position_required"; return result; }
            if (c.variationSelector == "CONFIRMED_HIT_INDEX_LIGHT_MEDIUM_HEAVY" && (s.hitIndex < 0 || s.hitIndex >= c.clips.Length))
            { result.reason = "hit_index_required"; return result; }
            var key = Tuple.Create(s.scope, s.eventId, s.cueKey, s.hitIndex);
            if (!seen.Add(key)) { result.reason = "duplicate"; return result; }
            seenOrder.Enqueue(key); if (seenOrder.Count > 8192) seen.Remove(seenOrder.Dequeue());
            // Consumed while muted: historical one-shots never wake up on unmute.
            if (Settings.muted || Settings.master <= 0 || Settings.GetGain(c.bus) <= 0) { result.reason = "muted"; return result; }
            double previous;
            if (lastStarts.TryGetValue(c.cueKey, out previous) && (now - previous) * 1000 < c.minGapMs) { result.reason = "min_gap"; return result; }
            int cueCount = 0, groupCount = 0;
            foreach (var v in voices.Values) { if (v.cue.cueKey == c.cueKey) cueCount++; if (v.cue.voiceGroup == c.voiceGroup) groupCount++; }
            bool cueFull = cueCount >= c.maxInstances, groupFull = groupCount >= caps[c.voiceGroup];
            if (cueFull || groupFull)
            {
                P1AudioVoice victim = null;
                foreach (var v in voices.Values)
                {
                    if (v.cue.voiceGroup != c.voiceGroup || (cueFull && v.cue.cueKey != c.cueKey)) continue;
                    if (victim == null || v.cue.priority < victim.cue.priority || (v.cue.priority == victim.cue.priority && v.id < victim.id)) victim = v;
                }
                if (victim == null || victim.cue.priority > c.priority) { result.reason = "voice_budget"; return result; }
                voices.Remove(victim.id); result.stopped.Add(victim.id);
            }
            int variant;
            if (c.variationSelector == "CONFIRMED_HIT_INDEX_LIGHT_MEDIUM_HEAVY") variant = s.hitIndex;
            else { nextVariant.TryGetValue(c.cueKey, out variant); nextVariant[c.cueKey] = (variant + 1) % c.clips.Length; }
            var voice = new P1AudioVoice { id = ++nextId, cue = c, variant = variant, startedAt = now,
                endsAt = c.loop ? double.PositiveInfinity : now + c.clips[variant].durationSeconds, x = s.x, y = s.y };
            voices.Add(voice.id, voice); lastStarts[c.cueKey] = now;
            if (c.voiceGroup == "skill" && c.priority == 100)
            { duckFrom = Duck(now); duckStart = now; duckEnd = Math.Max(duckEnd, now + c.clips[variant].durationSeconds + ducking.holdMs / 1000.0); }
            result.voice = voice; result.reason = "accepted"; return result;
        }
        public double Volume(P1AudioVoice v, double now, double listenerX = 0, double listenerY = 0)
        {
            if (Settings.muted || !P1AudioCatalog.Finite(now) || !P1AudioCatalog.Finite(listenerX) || !P1AudioCatalog.Finite(listenerY)) return 0;
            double spatial = 1;
            if (v.cue.Spatial)
            {
                double dx = v.x.Value - listenerX, dy = v.y.Value - listenerY, distance = Math.Sqrt(dx * dx + dy * dy);
                if (distance >= v.cue.maxDistanceWu) spatial = 0;
                else if (distance > v.cue.minDistanceWu) spatial = 1 - (distance - v.cue.minDistanceWu) / Math.Max(0.001, v.cue.maxDistanceWu - v.cue.minDistanceWu);
            }
            double duck = v.cue.bus == "Music" || v.cue.bus == "Ambience" ? Duck(now) : 1;
            return Settings.master * Settings.GetGain(v.cue.bus) * v.cue.gain * spatial * duck;
        }
        public double Pan(P1AudioVoice v, double listenerX)
        { return !v.cue.Spatial || !P1AudioCatalog.Finite(listenerX) ? 0 : Math.Max(-1, Math.Min(1, (v.x.Value - listenerX) / Math.Max(1, v.cue.maxDistanceWu))); }
        private double Duck(double now)
        {
            if (double.IsNegativeInfinity(duckStart)) return 1;
            double target = ducking.musicAmbienceGainMultiplier, attack = ducking.attackMs / 1000.0;
            if (now < duckStart + attack) return duckFrom + (target - duckFrom) * Math.Max(0, (now - duckStart) / attack);
            if (now <= duckEnd) return target;
            return target + (1 - target) * Math.Min(1, (now - duckEnd) / (ducking.releaseMs / 1000.0));
        }
    }
}
