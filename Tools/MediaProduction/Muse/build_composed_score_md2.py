#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 2: intro/outro + stems + phase layers
for the MD1 score cues.

Work Order 37 module M-D, following checkpoint 1 (MD1: 7 missing core
cues + 3 transition bridges, 15/15 slots covered). The coverage matrix
(MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work as
openForMdCp2:

  * per-cue intro/outro segments for the 7 MD1 cues (2 bars each,
    one-shot, -22 LUFS like the music);
  * stems (lead / pad-bass / percussion groups) per MD1 cue;
  * phase-layer candidates (arena high-intensity layer, boss phase-2
    layer -- additive loops that play over the base cue).

Stems are the checkpoint's exactness claim. The checkpoint-26 engine
(room / tail_wrap / end_landing / lowpass) is entirely linear, and
every random draw in it comes from one module-global RNG seeded 26 at
import. So a stem render can be made bit-identical, event by event, to
the MD1 master render:

  * the 7 MD1 reference mixes are re-rendered first, in MD1 order,
    from a fresh import (RNG state untouched between cues) -- the
    probe showed the hub master reproduces bit-exact (same sha256);
  * the RNG state at the start of each cue's reference render is
    saved, and restored before each of that cue's three stem renders;
  * the piece builders are re-run with routed primitives: every
    synth call still runs (so RNG consumption is identical), but its
    signal is mixed into the active stem track only when the voice
    belongs to that stem's group, else into a throwaway track;
  * the same loop processing (lowpass for rain, room, tail wrap, end
    landing) and the SAME gain factor as the reference mix are applied
    to every stem.

Consequence: lead + padbass + percussion sum to the shipped MD1
master within 24-bit quantisation (measured per cue, max abs diff
<= 5e-7, about 2 LSB). The validator re-checks this from real bytes.
No cue is re-composed here: intros/outros/layers are new segments,
stems are a regrouping of the MD1 arrangements.

Single-engine rule (a real bug caught in this checkpoint): MD1
loads build_composed_music.py itself, so the builders, their RNG,
and the melody/bass_line/drops internals all live in md1.cm. This
tool must use md1.cm as THE engine and never load a second copy --
a second copy splits the RNG and leaves the internals unpatched, so
every stem silently contains the full mix.

Rules kept from MD1 / checkpoint 26: the full flute tail
(F#-E-D) stays reserved for the resolve stinger and rift_finale --
outros close on the tonic pad + bell instead (hub / Thanh Lac may
use the low pluck tail, the thang_long precedent they already
follow in the loop). No external samples, no ported bytes, no
voices. The 541 ported PackV1 files and the checkpoint-26/30/MD1
packs are untouched and are NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/intros/<stem>_intro.wav
  Art_Source/Audio/Muse/COMPOSED/outros/<stem>_outro.wav
  Art_Source/Audio/Muse/COMPOSED/stems/<stem>_stem_<group>.wav
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/intros|outros|stems|layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD2_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md2 block + openForMdCp3; openForMdCp2 kept
    so the MD1 validator still passes)
"""
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
SR = 48000
MASTER_DIR = ROOT / "Art_Source/Audio/Muse/COMPOSED"
RUNTIME_DIR = ROOT / "ClientGodot/assets/audio/composed"
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD2_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
MD1_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
TMP = Path("/tmp/composed_score_md2")
TMP.mkdir(parents=True, exist_ok=True)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


md1 = _load("build_composed_score_md1",
             TOOLS_DIR / "build_composed_score_md1.py")
# THE engine instance: md1 loads build_composed_music.py itself, and
# its builders (and their RNG) live in that instance. Loading a
# second copy of the engine here would silently split the RNG and the
# melody/bass_line/drops internals (they resolve play/add in the
# engine's own namespace) -- the stems would then each contain the
# full mix. Never load build_composed_music.py separately in this
# tool; everything engine comes from md1.cm.
cm = md1.cm

# Engine primitives (the engine lives in checkpoint 26).
new_track = cm.new_track
play = cm.play
melody = cm.melody
chord = cm.chord
bass_line = cm.bass_line
drops = cm.drops
add = cm.add
drum = cm.drum
shaker = cm.shaker
noise_sw = cm.noise_sw
beat_s = cm.beat_s
lowpass = cm.lowpass
room = cm.room
tail_wrap = cm.tail_wrap
end_landing = cm.end_landing
write_master_wav = cm.write_master_wav
encode_ogg = cm.encode_ogg
file_entry = cm.file_entry
seam_stats = cm.seam_stats

D4, E4, FS4, A4, B4 = 62, 64, 66, 69, 71
D5, E5, FS5, A5, B5, D6 = 74, 76, 78, 81, 83, 86
MOTIF_Q = cm.MOTIF_Q
MOTIF_TAIL = cm.MOTIF_TAIL
MOTIF_HEAD = cm.MOTIF_HEAD
CH = cm.CH

RENDERING = ("procedural synthesis (additive pluck/flute/bell/pad/bass "
             "+ noise percussion), authored in "
             "build_composed_score_md2.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the MD1 arrangements "
             "(build_composed_score_md1.py); no external samples")
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; the full flute tail stays "
              "reserved for the resolve stinger and rift_finale")
STEM_SUM_NOTE = ("lead + padbass + percussion sum to the shipped MD1 "
                 "master within 24-bit quantisation (max abs diff "
                 "<= 5e-7, about 2 LSB); re-checked from real bytes "
                 "by check_composed_score_md2_v1.py")
SUM_THRESHOLD = 5e-7

GROUPS = ("lead", "padbass", "percussion")
GROUP_OF_VOICE = {"flute": "lead", "pluck": "lead", "bell": "lead",
                  "bass": "padbass"}
VOICE_FN = {"pluck": cm.pluck, "flute": cm.flute, "bell": cm.bell,
            "bass": cm.bass_note}


# ------------------------------------------------------- stem routing
# The piece builders write into one track through cm/md1 primitives.
# For stems, the primitives are swapped for routed versions that run
# the exact same synthesis (identical RNG consumption) but mix each
# signal into the active stem track only when it belongs to that
# stem's group; otherwise it goes to a throwaway track of the same
# length. chord -> padbass; drops / drum / shaker / noise_sw -> perc.
_ACTIVE = {"group": None, "track": None, "dummy": None}
_ADD_ORIG = cm.add


def _dest_for(group):
    if _ACTIVE["group"] == group:
        return _ACTIVE["track"]
    return _ACTIVE["dummy"]


def play_routed(track, voice, midi, at_s, dur_s, vel=0.8, pan=0.0,
                **kw):
    fn = VOICE_FN[voice]
    sig = fn(cm.note_freq(midi), dur_s, vel, **kw)
    _ADD_ORIG(_dest_for(GROUP_OF_VOICE[voice]), sig, at_s, pan, 1.0)


def chord_routed(track, midis, at_s, dur_s, vel=0.5, pan=0.0):
    sig = cm.pad_chord([cm.note_freq(m) for m in midis], dur_s, vel)
    _ADD_ORIG(_dest_for("padbass"), sig, at_s, pan, 1.0)


def add_routed(track, sig, at_s, pan=0.0, gain=1.0):
    _ADD_ORIG(_dest_for("percussion"), sig, at_s, pan, gain)


def _install_routing():
    cm.play = play_routed
    cm.add = add_routed
    md1.play = play_routed
    md1.chord = chord_routed
    md1.add = add_routed


def _remove_routing():
    cm.play = play
    cm.add = add
    md1.play = play
    md1.chord = chord
    md1.add = add


# ------------------------------------------------------------ helpers
def stage_factor(track, target_lufs, tp_ceiling, tag):
    """Mirror of cm.gain_stage, but also returns the scalar factor so
    the same gain can be applied to every stem of the cue."""
    tmpf = TMP / f"{tag}_measure.wav"
    factor = 1.0
    cur = track
    for attempt in range(3):
        cm.write_f32_wav(cur, tmpf)
        lufs, tp = cm.measure_loudnorm(tmpf)
        gain = min(target_lufs - lufs, tp_ceiling - tp)
        if abs(gain) < 0.15 or attempt == 2:
            return factor, lufs, tp
        mult = 10.0 ** (gain / 20.0)
        factor *= mult
        cur = cur * mult
    return factor, lufs, tp


def loop_process(track, lp_hz):
    """The MD1 loop construction, applied per stem so every stem is
    loopable on its own and the stems sum to the looped master."""
    if lp_hz:
        for ch in range(2):
            track[:, ch] = lowpass(track[:, ch], lp_hz)
    track = room(track, 0.16)
    track = tail_wrap(track, 1.5)
    track, raw_jump = end_landing(track, 0.25)
    return track, raw_jump


def decode_f32(path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def write_pair(track, stem, subdir, kind_label):
    """Write a master WAV + runtime OGG, return (master_entry,
    runtime_entry) via the engine's file_entry (real-byte probe +
    loudnorm)."""
    master = MASTER_DIR / subdir / f"{stem}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    write_master_wav(track, master)
    runtime = RUNTIME_DIR / subdir / f"{stem}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    encode_ogg(master, runtime)
    m_entry = file_entry(master, f"Art_Source/Audio/Muse/COMPOSED/"
                         f"{subdir}/{stem}.wav", "pcm_s24le")
    r_entry = file_entry(runtime, f"ClientGodot/assets/audio/composed/"
                         f"{subdir}/{stem}.ogg", "vorbis")
    return m_entry, r_entry


def save_pack(by_key, stem_groups, ref_repro):
    order = []
    for spec in md1.PIECES:
        stem = spec[0]
        order.append(f"MUSIC/{stem}_intro")
        order.append(f"MUSIC/{stem}_outro")
        for g in GROUPS:
            order.append(f"MUSIC/{stem}_stem_{g}")
    order.append("MUSIC/arena_layer_high")
    order.append("MUSIC/boss_mang_cot_layer_phase2")
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": sum(1 for c in cues if c["kind"] == "INTRO"),
              "outro": sum(1 for c in cues if c["kind"] == "OUTRO"),
              "stems": sum(1 for c in cues if c["kind"] == "STEM"),
              "layers": sum(1 for c in cues if c["kind"] == "LAYER"),
              "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD2_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 2 - intro/outro "
                      "+ stems + phase layers for the 7 MD1 score "
                      "cues (Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: intros, outros, "
                      "stems and phase layers authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md2.py (synthesis engine "
                      "reused from checkpoint 26 "
                      "build_composed_music.py; MD1 arrangements "
                      "reused from build_composed_score_md1.py) and "
                      "rendered by procedural synthesis. No external "
                      "samples, no ported bytes. These 37 files are "
                      "NEW audio, counted separately from the 541 "
                      "ported PackV1 files and from the checkpoint-26, "
                      "checkpoint-30 and MD1 packs, which keep their "
                      "own provenance and are untouched.",
        "counts": counts,
        "cues": cues,
        "stemGroups": stem_groups,
        "referenceReproduction": ref_repro,
        "notes": [
            "Stems regroup the MD1 arrangements: " + STEM_SUM_NOTE,
            "Intros/outros are 2-bar one-shots at the parent cue's "
            "tempo (-22 LUFS target, same as the music); an intro "
            "ends on a handoff bell at the loop's first downbeat, an "
            "outro closes on the tonic pad + bell with a 0.5 s fade. "
            "The full flute tail stays reserved for the resolve "
            "stinger and rift_finale; hub / Thanh Lac outros use "
            "the low pluck tail, the thang_long precedent.",
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD2 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ and do NOT replace "
            "the ported PackV1 files, their cue bindings, or the "
            "checkpoint-26/30/MD1 cues.",
            "No ear audition has been done; loudness/true-peak are "
            "measured from real bytes. Loop seams are recorded per "
            "looping cue in the delivery manifest: wrapJump after a "
            "disclosed 0.25 s end-landing loop construction, "
            "wrapJumpRaw before it.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['total']} MD2 cues", flush=True)
    return pack

# ------------------------------------------------- reference + stems
def render_reference(spec):
    """Re-render one MD1 cue exactly as MD1 did (fresh-import RNG
    state, pieces in order, no routing). Returns (track, factor,
    lufs, tp, start_state). The caller writes the track to /tmp and
    compares its sha256 with the shipped MD1 master."""
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    seconds = bars * 240.0 / bpm
    start_state = copy.deepcopy(cm.RNG.bit_generator.state)
    tr = new_track(seconds)
    builder(tr, bpm)
    tr, raw_jump = loop_process(tr, lp_hz)
    factor, lufs, tp = stage_factor(tr, -22.0, -7.0, stem)
    tr = tr * factor
    return tr, factor, lufs, tp, start_state, raw_jump


def render_stems(spec, start_state, factor):
    """Render the 3 stems of one MD1 cue with the RNG state restored
    to the cue's reference-render start, so every event's synthesis
    is bit-identical to the reference. Returns {group: track} at the
    reference gain (loop-processed, gain factor applied)."""
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    seconds = bars * 240.0 / bpm
    _install_routing()
    try:
        out = {}
        raw_jumps = {}
        for group in GROUPS:
            cm.RNG.bit_generator.state = copy.deepcopy(start_state)
            track = new_track(seconds)
            dummy = new_track(seconds)
            _ACTIVE["group"] = group
            _ACTIVE["track"] = track
            _ACTIVE["dummy"] = dummy
            builder(track, bpm)
            track, rj = loop_process(track, lp_hz)
            out[group] = track * factor
            raw_jumps[group] = rj
        return out, raw_jumps
    finally:
        _ACTIVE["group"] = None
        _ACTIVE["track"] = None
        _ACTIVE["dummy"] = None
        _remove_routing()


def check_stem_sum(md1_master_path, stem_paths):
    """Sum the 3 stem masters (real bytes) and compare with the
    shipped MD1 master. Returns (max_abs_diff, rms_diff)."""
    ref = decode_f32(md1_master_path)
    total = None
    for p in stem_paths:
        s = decode_f32(p)
        assert s.shape == ref.shape, (p, s.shape, ref.shape)
        total = s if total is None else total + s
    diff = total - ref
    return float(np.max(np.abs(diff))), float(np.sqrt((diff ** 2).mean()))


# ------------------------------------------------------- intro/outro
# Per-cue intro/outro config: (first chord, tonic chord, bass root,
# motif voice, motif octave shift, extras). Intros are 2 bars: pad of
# the first chord (7 beats, releases before the cut), bell, motif
# head, bass root, handoff bell at 7.5 beats, 0.15 s end fade.
# Outros are 2 bars: tonic pad, motif head (or the low pluck tail
# where the thang_long precedent allows it), bass root, tonic bell at
# bar 1, 0.5 s end fade. No full flute tail anywhere.
INTRO_OUTRO = {
    # stem: (first, tonic, root, motif_voice, motif_shift, extras)
    "hub_lac_chau": ("D", "D", 38, "flute", 0, ()),
    "thanh_lac": ("D", "D", 38, "flute", 0, ()),
    "rain_veil": ("D", "D", 38, "flute", 0, ("drops",)),
    "swamp": ("Bm", "D", 35, "flute", -12, ("drone_b0",)),
    "dungeon": ("Dm", "Dm", 26, "pluck", 0, ("drone_d1", "cold_bell")),
    "arena": ("D", "D", 38, "pluck", 0, ("drums",)),
    "tragedy": ("Dm", "Dm", 38, "flute", 0, ()),
}
FRAG_MINOR = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]


def build_intro(spec):
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    first, tonic, root, voice, shift, extras = INTRO_OUTRO[stem]
    seconds = 8 * beat_s(bpm)  # 2 bars
    tr = new_track(seconds)
    b = beat_s(bpm)
    chord(tr, CH[first], 0.0, 7 * b, 0.30)
    play(tr, "bell", CH[first][0] + 24, 0.0, 2 * b, 0.16)
    head = [(be, m + shift, ln) for be, m, ln in MOTIF_HEAD]
    if voice == "pluck":
        melody(tr, voice, head, bpm, 0, 0.7, bright=0.4)
    else:
        melody(tr, voice, head, bpm, 0, 0.7)
    play(tr, "bass", root, 0.0, 3.4 * b, 0.5)
    if "drone_b0" in extras:
        play(tr, "bass", 23, 0.0, 4 * b, 0.5)
    if "drone_d1" in extras:
        play(tr, "bass", 26, 0.0, 4 * b, 0.5)
    if "cold_bell" in extras:
        play(tr, "bell", 65, 2 * b, 3 * b, 0.14, pan=-0.2)
    if "drums" in extras:
        for bt in (0, 2, 4, 6):
            add(tr, drum(), bt * b, 0.0, 0.25)
    if "drops" in extras:
        drops(tr, [1.5 * b, 4.5 * b], 0.09)
    play(tr, "bell", CH[first][0] + 24, 7.5 * b, 0.5 * b, 0.12)
    if lp_hz:
        for ch in range(2):
            tr[:, ch] = lowpass(tr[:, ch], lp_hz)
    tr = room(tr, 0.12)
    fade = int(0.15 * SR)
    tr[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    return tr


def build_outro(spec):
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    first, tonic, root, voice, shift, extras = INTRO_OUTRO[stem]
    seconds = 8 * beat_s(bpm)  # 2 bars
    tr = new_track(seconds)
    b = beat_s(bpm)
    chord(tr, CH[tonic], 0.0, 8 * b, 0.30)
    if stem in ("hub_lac_chau", "thanh_lac"):
        # Low pluck tail: the thang_long precedent these cues follow.
        melody(tr, "pluck", MOTIF_TAIL, bpm, 0, 0.5, pan=-0.2)
    elif stem == "dungeon":
        melody(tr, "pluck", FRAG_MINOR, bpm, 0, 0.55, pan=-0.15,
               bright=0.4)
    else:
        head = [(be, m + shift, ln) for be, m, ln in MOTIF_HEAD]
        melody(tr, voice, head, bpm, 0, 0.55)
    play(tr, "bass", root, 0.0, 3.4 * b, 0.5)
    if "drone_d1" in extras:
        play(tr, "bass", 26, 0.0, 4 * b, 0.5)
    play(tr, "bell", CH[tonic][0] + 24, 4 * b, 3 * b, 0.18)
    if "cold_bell" in extras:
        play(tr, "bell", 65, 4 * b, 3 * b, 0.12, pan=-0.2)
    if "drums" in extras:
        add(tr, drum(), 4 * b, 0.0, 0.30)
        play(tr, "bell", D6, 4 * b, 2 * b, 0.18)
    if "drops" in extras:
        drops(tr, [5.5 * b], 0.07)
    if lp_hz:
        for ch in range(2):
            tr[:, ch] = lowpass(tr[:, ch], lp_hz)
    tr = room(tr, 0.12)
    fade = int(0.5 * SR)
    tr[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    return tr


def render_one_shot(spec, kind, builder_fn):
    """Render an intro/outro: reset RNG for determinism, compose,
    gain-stage to the music target (-22 LUFS / TP <= -7), write both
    sides. Returns the pack entry."""
    (stem, cue_key, name_vi, bpm, bars, _b, lp_hz,
     structure) = spec
    cm.RNG = np.random.default_rng(26)
    tr = builder_fn(spec)
    tr, _, _ = cm.gain_stage(tr, -22.0, -7.0, f"{stem}_{kind}")
    m_entry, r_entry = write_pair(tr, f"{stem}_{kind}",
                                  f"{kind}s", kind)
    seconds = 8 * beat_s(bpm)
    assert abs(m_entry["durationSeconds"] - seconds) < 0.05, stem
    assert -23.5 <= m_entry["integratedLufs"] <= -20.5, (stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -6.0, (stem, m_entry)
    return {
        "cueKey": f"MUSIC/{stem}_{kind}",
        "nameVi": f"{name_vi} · "
                  f"{'Mở đầu' if kind == 'intro' else 'Kết thúc'}",
        "kind": kind.upper(), "loop": False,
        "parentCueKey": f"MUSIC/{stem}",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "tempoBpm": bpm, "bars": 2, "mode": "see structure",
            "motif": MOTIF_NOTE,
            "structure": (
                f"{'Intro' if kind == 'intro' else 'Outro'} (2 bars) "
                f"for {stem}: "
                + ("pad of the first chord (7 beats, releases before "
                   "the cut) + bell + motif head + bass root + "
                   "handoff bell at 7.5 beats; 0.15 s end fade"
                   if kind == "intro" else
                   "tonic pad + motif head (low pluck tail for hub / "
                   "Thanh Lac, thang_long precedent) + bass root + "
                   "tonic bell at bar 1; 0.5 s end fade")
                + (f"; low-pass {lp_hz} Hz like the parent cue"
                   if lp_hz else "")),
            "rendering": RENDERING,
        },
        "master": m_entry, "runtime": r_entry,
    }


# --------------------------------------------------------- phase layers
def layer_arena_high():
    """Additive high-intensity layer over the arena base (16 bars @
    120 bpm): eighth-note shaker + bass ostinato + drums filling
    beats 1 and 3 + bell accents every 2 bars. The base already has
    drums on beats 0/2, quarter shakers and the pluck ostinato, so
    this layer only adds density the adapter can fade in."""
    bpm, bars = 120, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    roots = [38, 38, 33, 38, 35, 38, 33, 38,
             38, 38, 33, 35, 43, 33, 38, 38]
    for bar in range(bars):
        for bt in (1, 3):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.22)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.06), bar * 4 * b + bt * b,
                0.3 if bt in (0.5, 2.5) else -0.3, 0.05)
        for bt in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
            play(tr, "bass", roots[bar], bar * 4 * b + bt * b,
                 0.8 * b, 0.5)
        if bar % 2 == 0:
            play(tr, "bell", D6, bar * 4 * b, 2 * b, 0.15,
                 pan=0.3 if bar % 4 == 0 else -0.3)
    tr, raw_jump = loop_process(tr, None)
    factor, lufs, tp = stage_factor(tr, -25.0, -5.0,
                                    "arena_layer_high")
    return tr * factor, raw_jump


def layer_boss_phase2():
    """Additive phase-2 layer over boss_mang_cot (10 bars @ 66 bpm):
    drums filling beats 1/2/3 around the base heartbeat pulse,
    eighth-note D1 bass pulse, cold F4 bell marks every 2 bars, and
    the minor-head pluck fragment on bars the base does not use
    (1, 4, 6, 9 vs the base's 2, 5, 7, 8). No pad, no flute -- those
    stay in the base cue."""
    bpm, bars = 66, 10
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (1, 2, 3):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.22)
        for bt in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
            play(tr, "bass", 26, bar * 4 * b + bt * b, 0.8 * b, 0.45)
        if bar % 2 == 0:
            play(tr, "bell", 65, bar * 4 * b, 3 * b, 0.15, pan=-0.2)
    for bar in (1, 4, 6, 9):
        melody(tr, "pluck", FRAG_MINOR, bpm, bar, 0.5, pan=0.15,
               bright=0.4)
    tr, raw_jump = loop_process(tr, None)
    factor, lufs, tp = stage_factor(tr, -25.0, -5.0,
                                    "boss_mang_cot_layer_phase2")
    return tr * factor, raw_jump


def combined_loudness(base_wav, layer_wav):
    """Mix base + layer masters (real bytes) and measure the combined
    loudnorm. Returns (lufs, tp)."""
    base = decode_f32(base_wav)
    layer = decode_f32(layer_wav)
    assert base.shape == layer.shape
    tmp = TMP / "combined_measure.wav"
    cm.write_f32_wav(base + layer, tmp)
    return cm.measure_loudnorm(tmp)


def render_layer(stem, cue_key, name_vi, parent_key, parent_wav,
                 parent_seconds, bpm, bars, layer_fn, structure):
    cm.RNG = np.random.default_rng(26)
    tr, raw_jump = layer_fn()
    m_entry, r_entry = write_pair(tr, stem, "layers", "layer")
    assert abs(m_entry["durationSeconds"] - parent_seconds) < 0.05, stem
    assert -27.0 <= m_entry["integratedLufs"] <= -23.0, (stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -5.0, (stem, m_entry)
    c_lufs, c_tp = combined_loudness(parent_wav,
                                     MASTER_DIR / "layers" / f"{stem}.wav")
    assert c_tp <= -3.0, (stem, c_lufs, c_tp)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "LAYER",
        "loop": True, "parentCueKey": parent_key,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "tempoBpm": bpm, "bars": bars, "mode": "see structure",
            "motif": MOTIF_NOTE, "structure": structure,
            "rendering": RENDERING,
        },
        "master": m_entry, "runtime": r_entry,
        "seam": {**seam_stats(tr), "wrapJumpRaw": raw_jump,
                 "landingNote": "wrapJump is measured after a 0.25 s "
                                "end-landing blend to the first sample "
                                "(loop crossfade construction); "
                                "wrapJumpRaw is the step before it"},
        "combinedWithBase": {
            "baseCueKey": parent_key,
            "method": "base master + layer master summed from real "
                      "bytes, ffmpeg loudnorm",
            "integratedLufs": round(c_lufs, 2),
            "truePeakDbtp": round(c_tp, 2),
        },
    }

# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP2, an md2 block records what this checkpoint delivered,
    openForMdCp3 lists what stays open. openForMdCp2 is KEPT so the
    MD1 validator (which asserts it is non-empty) still passes;
    slots and transitions are untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 2"
    cov["md2"] = {
        "pack": "MUSIC_SCORE_MD2_pack_v1",
        "intros": 7,
        "outros": 7,
        "stems": 21,
        "layers": 2,
        "detail": ("2-bar intro/outro for each of the 7 MD1 cues; "
                   "lead / pad-bass / percussion stems per MD1 cue, "
                   "summing to the shipped MD1 master within 24-bit "
                   "quantisation; additive phase layers "
                   "MUSIC/arena_layer_high and "
                   "MUSIC/boss_mang_cot_layer_phase2."),
    }
    cov["openForMdCp3"] = [
        "Per-cue intro/outro segments and stems for the 9 "
        "checkpoint-26 cues (if the director wants them).",
        "More phase-layer candidates (e.g. boss phase 3, tragedy "
        "intensity layer, arena low layer).",
        "Ear audition of all MD1/MD2 cues + loop seams "
        "(NOT_AUDITIONED).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 2, "
          f"md2 recorded, openForMdCp3 listed", flush=True)
    return cov


# ---------------------------------------------------------------- main
def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))
    md1_pack = json.loads(MD1_PACK.read_text(encoding="utf-8"))
    md1_by_key = {c["cueKey"]: c for c in md1_pack["cues"]}
    md1_music = [c for c in md1_pack["cues"] if c["kind"] == "MUSIC"]

    by_key = {}
    stem_groups = []
    ref_repro = []
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}
        stem_groups = existing.get("stemGroups", [])
        ref_repro = existing.get("referenceReproduction", [])

    # --- 1. Reference re-renders (MD1 order, fresh RNG) + stems ---
    if only is None or "stems" in only or "reference" in only:
        saved_states = {}
        for spec in md1.PIECES:
            stem = spec[0]
            ref_tr, factor, lufs, tp, start_state, _rj = \
                render_reference(spec)
            saved_states[stem] = (start_state, factor)
            tmp = TMP / f"ref_{stem}.wav"
            write_master_wav(ref_tr, tmp)
            got_sha = hashlib.sha256(tmp.read_bytes()).hexdigest()
            want_sha = md1_by_key[f"MUSIC/{stem}"]["master"]["sha256"]
            match = got_sha == want_sha
            print(f"reference {stem}: sha "
                  f"{'MATCHES' if match else 'DIFFERS FROM'} MD1 "
                  f"master ({lufs:.2f} LUFS / {tp:.2f} dBTP)",
                  flush=True)
            ref_repro = [r for r in ref_repro
                         if r["cueKey"] != f"MUSIC/{stem}"]
            ref_repro.append({
                "cueKey": f"MUSIC/{stem}",
                "md1MasterSha256": want_sha,
                "reproducedSha256": got_sha,
                "match": match,
                "method": "re-rendered from a fresh import with the "
                          "MD1 pipeline (same builders, same order); "
                          "the RNG state at the start of this render "
                          "is the state the stems restore",
            })
            if only is not None and "stems" not in only:
                continue
            stems, raw_jumps = render_stems(spec, start_state, factor)
            stem_paths = []
            for group in GROUPS:
                m_entry, r_entry = write_pair(
                    stems[group], f"{stem}_stem_{group}", "stems",
                    "stem")
                stem_paths.append(MASTER_DIR / "stems"
                                  / f"{stem}_stem_{group}.wav")
                silent = False
                if group == "percussion" and stem == "tragedy":
                    # Tragedy has no percussion elements by design;
                    # its percussion stem must be digital silence.
                    # ffmpeg loudnorm of silence is -inf, which is
                    # not valid JSON, so loudness is recorded null
                    # with an explicit note (the validator asserts
                    # the silence from real bytes instead).
                    sig = decode_f32(MASTER_DIR / "stems"
                                     / f"{stem}_stem_{group}.wav")
                    assert float(np.max(np.abs(sig))) == 0.0, stem
                    silent = True
                    m_entry["integratedLufs"] = None
                    m_entry["truePeakDbtp"] = None
                    r_entry["integratedLufs"] = None
                    r_entry["truePeakDbtp"] = None
                entry = {
                    "cueKey": f"MUSIC/{stem}_stem_{group}",
                    "nameVi": (f"{spec[2]} · Stem "
                               f"{'giai điệu' if group == 'lead' else 'nền/trầm' if group == 'padbass' else 'bộ gõ'}"),
                    "kind": "STEM", "loop": True,
                    "parentCueKey": f"MUSIC/{stem}",
                    "stemGroup": stem, "group": group,
                    "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
                    "composition": {
                        "tempoBpm": spec[3], "bars": spec[4],
                        "mode": "see structure",
                        "motif": MOTIF_NOTE,
                        "structure": (
                            f"{group} stem of {stem} (MD1 arrangement, "
                            "regrouped): "
                            + {"lead": "flute + pluck melody + bells",
                               "padbass": "pad chords + bass line + "
                                          "drones",
                               "percussion": "drums + shaker + drops + "
                                             "noise wash"}[group]
                            + "; loop-processed like the master so "
                              "the stem is loopable on its own"),
                        "rendering": RENDERING,
                    },
                    "master": m_entry, "runtime": r_entry,
                    "seam": {**seam_stats(stems[group]),
                             "wrapJumpRaw": raw_jumps[group],
                             "landingNote": "wrapJump is measured "
                                            "after a 0.25 s end-landing "
                                            "blend to the first sample "
                                            "(loop crossfade "
                                            "construction); wrapJumpRaw "
                                            "is the step before it"},
                }
                if silent:
                    entry["silence"] = True
                    entry["silenceNote"] = (
                        "Digital silence by design: tragedy has no "
                        "percussion elements; loudnorm is undefined "
                        "(-inf), recorded as null.")
                by_key[entry["cueKey"]] = entry
                print(f"OK {entry['cueKey']}: "
                      f"{m_entry['durationSeconds']} s master "
                      f"{m_entry['integratedLufs']} LUFS / "
                      f"{m_entry['truePeakDbtp']} dBTP", flush=True)
            max_diff, rms_diff = check_stem_sum(
                ROOT / md1_by_key[f"MUSIC/{stem}"]["master"]["path"],
                stem_paths)
            assert max_diff <= SUM_THRESHOLD, (stem, max_diff)
            stem_groups = [g for g in stem_groups
                           if g["parentCueKey"] != f"MUSIC/{stem}"]
            stem_groups.append({
                "parentCueKey": f"MUSIC/{stem}",
                "method": "lead + padbass + percussion masters summed "
                          "from real bytes vs the shipped MD1 master",
                "maxAbsDiff": max_diff,
                "rmsDiff": rms_diff,
                "threshold": SUM_THRESHOLD,
                "note": STEM_SUM_NOTE,
            })
            print(f"stem-sum {stem}: max abs diff {max_diff:.2e} "
                  f"(<= {SUM_THRESHOLD:.0e}), rms {rms_diff:.2e}",
                  flush=True)
            save_pack(by_key, stem_groups, ref_repro)

    # --- 2. Intros / outros ---
    if only is None or "intros" in only or "outros" in only:
        for spec in md1.PIECES:
            if only is None or "intros" in only:
                entry = render_one_shot(spec, "intro", build_intro)
                by_key[entry["cueKey"]] = entry
                print(f"OK {entry['cueKey']}: "
                      f"{entry['master']['durationSeconds']} s master "
                      f"{entry['master']['integratedLufs']} LUFS / "
                      f"{entry['master']['truePeakDbtp']} dBTP",
                      flush=True)
                save_pack(by_key, stem_groups, ref_repro)
            if only is None or "outros" in only:
                entry = render_one_shot(spec, "outro", build_outro)
                by_key[entry["cueKey"]] = entry
                print(f"OK {entry['cueKey']}: "
                      f"{entry['master']['durationSeconds']} s master "
                      f"{entry['master']['integratedLufs']} LUFS / "
                      f"{entry['master']['truePeakDbtp']} dBTP",
                      flush=True)
                save_pack(by_key, stem_groups, ref_repro)

    # --- 3. Phase layers ---
    if only is None or "layers" in only:
        arena = md1_by_key["MUSIC/arena"]
        entry = render_layer(
            "arena_layer_high", "MUSIC/arena_layer_high",
            "Đấu trường · Lớp cao trào", "MUSIC/arena",
            ROOT / arena["master"]["path"],
            arena["master"]["durationSeconds"], 120, 16,
            layer_arena_high,
            "Additive high-intensity layer over the arena base "
            "(16 bars @ 120 bpm): eighth-note shaker + bass "
            "ostinato + drums filling beats 1 and 3 + bell accents "
            "every 2 bars. The base keeps drums on beats 0/2, "
            "quarter shakers and the pluck ostinato; this layer only "
            "adds density the adapter can fade in. -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key, stem_groups, ref_repro)

        cp26 = json.loads((ROOT / "Implementation/Content/Audio"
                           / "Deliveries/MUSIC_COMPOSED_pack_v1.json")
                          .read_text(encoding="utf-8"))
        boss = [c for c in cp26["cues"]
                if c["cueKey"] == "MUSIC/boss_mang_cot"][0]
        entry = render_layer(
            "boss_mang_cot_layer_phase2",
            "MUSIC/boss_mang_cot_layer_phase2",
            "Mãng Cốt · Lớp giai đoạn 2", "MUSIC/boss_mang_cot",
            ROOT / boss["master"]["path"],
            boss["master"]["durationSeconds"], 66, 10,
            layer_boss_phase2,
            "Additive phase-2 layer over boss_mang_cot (10 bars @ "
            "66 bpm): drums filling beats 1/2/3 around the base "
            "heartbeat pulse, eighth-note D1 bass pulse, cold F4 "
            "bell marks every 2 bars, minor-head pluck fragments on "
            "bars 1/4/6/9 (the base uses 2/5/7/8). No pad, no flute "
            "-- those stay in the base cue. -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key, stem_groups, ref_repro)

    save_pack(by_key, stem_groups, ref_repro)
    update_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
