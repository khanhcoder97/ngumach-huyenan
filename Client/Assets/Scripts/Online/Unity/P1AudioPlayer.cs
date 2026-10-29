using System;
using System.Collections.Generic;
using Newtonsoft.Json;
using UnityEngine;

namespace NguMach.Client.P1
{
    public sealed class P1AudioPlayer : MonoBehaviour
    {
        private const string PreferenceKey = "ngumach.audio.settings.v1";
        private readonly Dictionary<long, Playback> playing = new Dictionary<long, Playback>();
        private readonly Dictionary<string, P1AudioCueAsset> cache = new Dictionary<string, P1AudioCueAsset>();
        private P1AudioPolicy policy;
        private AudioListener ownedListener;
        private string scope, session, map;
        private double listenerX, listenerY;
        public P1AudioSettings Settings { get; private set; } = new P1AudioSettings();
        public bool Ready { get { return policy != null; } }
        public int ActiveVoices { get { return playing.Count; } }
        private sealed class Playback { public P1AudioVoice voice; public AudioSource source; }
        private double Now { get { return Time.realtimeSinceStartupAsDouble; } }

        public void Initialize()
        {
            Settings = P1AudioSettings.FromJson(PlayerPrefs.GetString(PreferenceKey, "{}"));
            var text = Resources.Load<TextAsset>("P1Audio/catalog");
            if (text == null) { Debug.LogWarning("P1 audio catalog not generated. Use Ngu Mach/Audio/Build Runtime Catalog in Editor."); return; }
            try { policy = new P1AudioPolicy(P1AudioCatalog.Parse(text.text), Settings); }
            catch (Exception e) when (e is JsonException || e is ArgumentException)
            { Debug.LogError("P1 audio catalog rejected: " + e.Message); }
            if (Ready && FindFirstObjectByType<AudioListener>() == null && Camera.main != null)
                ownedListener = Camera.main.gameObject.AddComponent<AudioListener>();
        }
        public void ObserveWorld(string sessionId, P1World world)
        {
            var nextMap = world == null ? null : world.mapId;
            if (session != sessionId || map != nextMap)
            {
                session = sessionId; map = nextMap;
                // This namespace is local UI presentation. It is NOT a server mapInstanceId.
                scope = sessionId == null || nextMap == null ? null : Guid.NewGuid().ToString("N");
                if (policy != null) Stop(policy.SetScope(scope));
                cache.Clear();
            }
            if (world != null) { listenerX = world.self.x; listenerY = world.self.y; }
        }
        public void LocalUi(string cueKey)
        {
            var cue = policy == null ? null : policy.Find(cueKey);
            if (cue == null) return;
            Play(new P1AudioSignal { scope = scope, eventId = Guid.NewGuid().ToString("N"), cueKey = cueKey, semantic = cue.triggerSemantic });
        }
        public void ConfirmedNotice(P1AudioNotice notice)
        {
            if (notice == null) return;
            // Only currently supported command-result semantic; no generic combat event.
            if (notice.cueKey != "SFX/QUEST/accepted" || notice.semantic != "QUEST_ACCEPT_COMMITTED") return;
            Play(new P1AudioSignal { scope = scope, eventId = notice.eventId, cueKey = notice.cueKey, semantic = notice.semantic, confirmed = true });
        }
        private void Play(P1AudioSignal signal)
        {
            if (policy == null) return;
            var decision = policy.Admit(signal, Now); Stop(decision.stopped);
            if (!decision.Accepted) return;
            var voice = decision.voice;
            var asset = LoadCue(voice.cue.cueKey);
            if (asset == null || asset.clips == null || asset.clips.Length != voice.cue.clips.Length || asset.clips[voice.variant] == null)
            { policy.Release(voice.id); Debug.LogWarning("P1 audio resource missing: " + voice.cue.cueKey); return; }
            var child = new GameObject("P1AudioVoice"); child.transform.SetParent(transform, false);
            var source = child.AddComponent<AudioSource>(); source.playOnAwake = false;
            source.clip = asset.clips[voice.variant]; source.loop = voice.cue.loop;
            source.spatialBlend = 0; source.dopplerLevel = 0;
            source.volume = (float)policy.Volume(voice, Now, listenerX, listenerY);
            source.panStereo = (float)policy.Pan(voice, listenerX);
            source.Play(); voice.startedAt = Now;
            voice.endsAt = voice.cue.loop ? double.PositiveInfinity : Now + source.clip.length;
            playing.Add(voice.id, new Playback { voice = voice, source = source });
        }
        private P1AudioCueAsset LoadCue(string key)
        {
            P1AudioCueAsset asset;
            if (cache.TryGetValue(key, out asset)) return asset;
            // Limit retained cue handles; Unity memory still needs engine profiling.
            if (cache.Count >= 48)
            {
                string unused = null;
                foreach (var candidate in cache.Keys)
                {
                    bool active = false;
                    foreach (var voice in playing.Values) if (voice.voice.cue.cueKey == candidate) { active = true; break; }
                    if (!active) { unused = candidate; break; }
                }
                if (unused == null) return null;
                cache.Remove(unused);
            }
            asset = Resources.Load<P1AudioCueAsset>("P1Audio/Cues/" + key.ToLowerInvariant());
            if (asset == null || asset.cueKey != key) return null;
            cache.Add(key, asset); return asset;
        }
        private void Update()
        {
            if (policy == null) return;
            Stop(policy.Advance(Now));
            foreach (var pair in playing)
            {
                pair.Value.source.volume = (float)policy.Volume(pair.Value.voice, Now, listenerX, listenerY);
                pair.Value.source.panStereo = (float)policy.Pan(pair.Value.voice, listenerX);
            }
        }
        private void Stop(IEnumerable<long> ids)
        {
            foreach (long id in ids)
            {
                Playback p;
                if (!playing.TryGetValue(id, out p)) continue;
                p.source.Stop(); p.source.clip = null; Destroy(p.source.gameObject); playing.Remove(id);
            }
        }
        public void SaveSettings()
        { PlayerPrefs.SetString(PreferenceKey, JsonConvert.SerializeObject(Settings)); PlayerPrefs.Save(); }
        private void OnDisable()
        {
            SaveSettings();
            Stop(new List<long>(playing.Keys));
            if (policy != null) policy.SetScope(null);
            cache.Clear();
            if (ownedListener != null) Destroy(ownedListener);
        }
    }
}
