using System;
using System.IO;
using NguMach.Client.P1;
using Newtonsoft.Json.Linq;

internal static class AudioChecks
{
    private static int checks;
    private static void Check(bool value, string message) { checks++; if (!value) throw new Exception("Audio: " + message); }
    private static void Reject(Action action, string message)
    { bool failed = false; try { action(); } catch (ArgumentException) { failed = true; } Check(failed, message); }
    private static P1AudioSignal Signal(P1AudioCatalog c, string key, string id, bool confirmed = true, int hit = -1)
    {
        var cue = Array.Find(c.cues, x => x.cueKey == key);
        return new P1AudioSignal { scope = "scope-A", eventId = id, cueKey = key,
            semantic = cue.triggerSemantic, confirmed = confirmed, hitIndex = hit, x = 0, y = 0 };
    }
    private static P1AudioPolicy Policy(P1AudioCatalog c)
    { var p = new P1AudioPolicy(c, new P1AudioSettings()); p.SetScope("scope-A"); return p; }
    public static void Run()
    {
        string json = File.ReadAllText("Client/Assets/AudioManifests/game_audio_v1.json");
        var catalog = P1AudioCatalog.Parse(json);
        Check(catalog.cues.Length == 195, "parse all delivered cues");
        var altered = JObject.Parse(json); altered["cues"][0]["clips"][0]["path"] = "Client/Assets/Audio/PackV1/../secret.wav";
        Reject(() => P1AudioCatalog.Parse(altered.ToString()), "reject traversal");
        altered = JObject.Parse(json); altered["cues"][0]["gain"] = double.NaN;
        Reject(() => P1AudioCatalog.Parse(altered.ToString()), "reject non-finite catalog gain");
        altered = JObject.Parse(json); altered["voiceCaps"]["skill"] = 0;
        Reject(() => P1AudioCatalog.Parse(altered.ToString()), "reject zero group budget");
        altered = JObject.Parse(json); altered["cues"][1]["clips"][0]["path"] = altered["cues"][0]["clips"][0]["path"].DeepClone();
        Reject(() => P1AudioCatalog.Parse(altered.ToString()), "reject aliased clip ownership");
        {
            var p = Policy(catalog);
            var guard = Signal(catalog, "SFX/SKILL/metal_parry", "guard"); guard.semantic = "CAST_ACCEPTED";
            Check(p.Admit(guard, 0).reason == "semantic_not_confirmed", "cast acceptance is not counter");
            guard.semantic = "COUNTER_CONFIRMED"; guard.confirmed = false;
            Check(!p.Admit(guard, 0).Accepted, "animation/local input cannot confirm counter");
            guard.confirmed = true; guard.audienceAllowed = false;
            Check(!p.Admit(guard, 0).Accepted, "audience denied before audio");
            guard.audienceAllowed = true; guard.x = null;
            Check(p.Admit(guard, 0).reason == "position_required", "world sound requires XY");
            guard.x = 0;
            var first = p.Admit(guard, 0); Check(first.Accepted, "verified counter admitted");
            Check(p.Admit(guard, 0.1).reason == "duplicate", "same event never plays twice");
            var pickup = Signal(catalog, "SFX/UI/item_pickup_common", "pickup", false);
            Check(!p.Admit(pickup, 0.2).Accepted, "UI-labelled committed item still requires confirmation");
        }
        {
            var p = Policy(catalog); var first = p.Admit(Signal(catalog, "SFX/UI/focus", "1", false), 0);
            Check(first.Accepted, "local focus cue accepted");
            Check(p.Admit(Signal(catalog, "SFX/UI/focus", "2", false), 0.01).reason == "min_gap", "focus spam throttled");
            var next = p.Admit(Signal(catalog, "SFX/UI/focus", "3", false), 0.09);
            Check(next.Accepted && next.voice.variant != first.voice.variant, "next variant never immediate repeat");
            p.Settings.muted = true; var mute = Signal(catalog, "SFX/QUEST/accepted", "muted");
            Check(p.Admit(mute, 1).reason == "muted", "mute suppresses new voice");
            p.Settings.muted = false;
            Check(p.Admit(mute, 2).reason == "duplicate", "unmute does not replay suppressed history");
            double previous = p.Settings.ui; p.Settings.muted = true; p.Settings.muted = false;
            Check(p.Settings.ui == previous, "mute preserves saved bus gain");
            p.Settings.SetGain("Master", -8); Check(p.Settings.master == 0, "clamp low gain");
            p.Settings.SetGain("Master", 7); Check(p.Settings.master == 1, "clamp high gain");
            Reject(() => p.Settings.SetGain("Music", double.PositiveInfinity), "infinite settings fail");
            Check(P1AudioSettings.FromJson("{\"master\":null}").master == 0.7, "corrupt preference falls back");
        }
        {
            var c = P1AudioCatalog.Parse(json); c.voiceCaps["skill"] = 2; var p = Policy(c);
            var a = p.Admit(Signal(c, "SFX/SKILL/metal_parry", "a"), 0);
            var b = p.Admit(Signal(c, "SFX/SKILL/metal_parry", "b"), 0.1);
            Check(p.ActiveCount == 2, "per-cue cap reached");
            var third = p.Admit(Signal(c, "SFX/SKILL/metal_parry", "c"), 0.2);
            Check(third.Accepted && third.stopped.Contains(a.voice.id) && !third.stopped.Contains(b.voice.id) && p.ActiveCount == 2, "equal priority steals oldest cue voice");
            var warn = p.Admit(Signal(c, "SFX/BOSS/mang_cot_sweep_warning", "warn"), 0.21);
            Check(warn.Accepted && warn.stopped.Contains(b.voice.id), "boss warning steals lower priority");
            var warn2 = p.Admit(Signal(c, "SFX/BOSS/mang_cot_emerge_warning", "warn2"), 0.22);
            Check(warn2.Accepted && warn2.stopped.Contains(third.voice.id), "budget contains two priority warnings");
            Check(p.Admit(Signal(c, "SFX/SKILL/metal_parry", "low"), 0.3).reason == "voice_budget", "low priority cannot steal warning");
        }
        {
            var p = Policy(catalog);
            // Resolve the canonical key from the source metadata instead of guessing a name.
            var c = Array.Find(catalog.cues, x => x.variationSelector == "CONFIRMED_HIT_INDEX_LIGHT_MEDIUM_HEAVY");
            var hit = Signal(catalog, c.cueKey, "combo");
            Check(p.Admit(hit, 0).reason == "hit_index_required", "multi-hit requires explicit index");
            for (int i = 0; i < 3; i++)
            { hit.hitIndex = i; var d = p.Admit(hit, i * 0.1); Check(d.Accepted && d.voice.variant == i, "one component per confirmed hit " + i); }
            Check(p.Admit(hit, 0.4).reason == "duplicate", "same hit index deduped");
        }
        {
            var p = Policy(catalog); var music = p.Admit(Signal(catalog, "MUSIC/thang_long", "region"), 0);
            Check(music.Accepted, "explicit music state starts loop");
            double normal = p.Volume(music.voice, 0);
            var warning = p.Admit(Signal(catalog, "SFX/BOSS/mang_cot_sweep_warning", "w"), 1);
            Check(warning.Accepted && Math.Abs(p.Volume(music.voice, 1.04) / normal - 0.75) < 0.001, "duck attack envelope");
            Check(Math.Abs(p.Volume(music.voice, 1.1) / normal - 0.5) < 0.001, "warning halves music only");
            Check(Math.Abs(p.Volume(music.voice, warning.voice.endsAt + 0.6) - normal) < 0.001, "duck releases after hold");
            p.Settings.muted = true;
            Check(p.Volume(warning.voice, 1.1) == 0 && p.Volume(music.voice, 1.1) == 0, "warning never bypasses mute");
            var stop = p.SetScope("scope-B"); Check(stop.Contains(music.voice.id) && p.ActiveCount == 0, "map scope change stops loops");
            Check(!p.Admit(Signal(catalog, "MUSIC/thang_long", "old"), 3).Accepted, "old-scope event cannot restart music");
        }
        {
            var p = Policy(catalog); var d = p.Admit(Signal(catalog, "SFX/SKILL/metal_parry", "xy"), 0);
            Check(p.Volume(d.voice, 0, 100, 100) == 0, "far sound attenuated to zero");
            Check(p.Pan(d.voice, -10) > 0 && p.Pan(d.voice, 10) < 0, "pan follows X in XY plane");
            Check(p.Volume(d.voice, 0, double.NaN, 0) == 0, "invalid listener cannot produce NaN volume");
            Check(p.Advance(2).Contains(d.voice.id) && p.ActiveCount == 0, "ended one-shot frees voice budget");
        }
        Console.WriteLine("PASS audio policy assertions: " + checks);
    }
}
