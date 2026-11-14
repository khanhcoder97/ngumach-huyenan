#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 3: intro/outro + stems + phase layers
for the checkpoint-26 score cues.

Work Order 37 module M-D, following checkpoint 2 (MD2: intro/outro +
stems + phase layers for the 7 MD1 cues). The coverage matrix
(MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work as
openForMdCp3:

  * per-cue intro/outro segments for the 9 checkpoint-26 cues (2 bars
    each, one-shot, -22 LUFS like the music);
  * stems (lead / pad-bass / percussion groups) per checkpoint-26 cue
    (all 9 -- each cue's reproducing RNG history was recovered by
    search, see the stem section below);
  * more phase-layer candidates (boss phase 3, tragedy intensity
    layer, arena low layer -- additive loops that play over the base
    cue).

Stems are the checkpoint's exactness claim. The checkpoint-26 engine
(room / tail_wrap / end_landing / lowpass) is entirely linear, and
every random draw in it comes from one module-global RNG seeded 26 at
import. So a stem render can be made bit-identical, event by event, to
the checkpoint-26 master render -- PROVIDED the render starts from
the same RNG state the shipped master was rendered from. The shipped
masters were built in several separate renders in 2026-11-05, so a
single sequential re-render does NOT reproduce every master: each
cue's reproducing RNG history was recovered by search (see the
checkpoint report) and is recorded in REPRO_PRIOR below. The gain is
recovered the same way: gain_stage's multipliers are tried first
(bit-exact where they reproduce the shipped master); otherwise the
gain is fitted by least squares against the shipped master (the
pre-gain track is bit-identical to the original's -- the residual
after the fit sits exactly at the 24-bit quantisation floor,
1.19e-07 -- so the fitted gain is the original gain to ~1e-9).

For each stem cue the builder:

  * resets the RNG to seed 26, renders the cue's prior pieces (the
    RNG history that reproduces it), and saves the RNG state;
  * re-renders the cue from that state (no routing) and recovers its
    gain -- the reference must reproduce the shipped master to
    <= 2.5e-7 after the gain (or bit-exact) before any stem is
    written;
  * re-renders the cue's three stems with the RNG state restored
    before each stem render, with the primitives routed: every synth
    call still runs (so RNG consumption is identical), but its signal
    is mixed into the active stem track only when the voice belongs
    to that stem's group, else into a throwaway track;
  * applies the SAME gain to every stem (the same multipliers, in
    the same order, as the reference).

Consequence: lead + padbass + percussion sum to the shipped
checkpoint-26 master within 24-bit quantisation (measured per cue,
max abs diff <= 5e-7, about 2 LSB). The validator re-checks this from
real bytes. No cue is re-composed here: intros/outros/layers are new
segments, stems are a regrouping of the checkpoint-26 arrangements.

Three cues first looked unrecoverable (boss_mang_cot, lam_trieu,
tran_son): their shipped masters do not reproduce from a fresh RNG,
from any prefix of the piece order, from the stingers, or from
self-repeat. A second search over single-prior states found them all:
boss_mang_cot reproduces after thang_long, lam_trieu after
quiet_discovery, tran_son after sa_hoa (each to the 24-bit floor,
1.19e-07). The original session was built in pairs -- the author
rendered two cues per run with --only, in piece order within each
pair: (ben_mua, rift_finale), (thang_long, boss_mang_cot),
(quiet_discovery, lam_trieu), (sa_hoa, tran_son), (bach_uyen alone).
The deterministic skeleton of every cue matches the current
arrangement; only the RNG history differed. All 9 cues therefore
have stems in this checkpoint.

Single-engine rule (a real bug caught in checkpoint 2): the MD1
builders live in build_composed_score_md1.py, which loads
build_composed_music.py itself -- so MD2 had to use md1.cm as THE
engine and never load a second copy. Here the builders live in
build_composed_music.py itself, so this tool loads THAT file once as
cm and uses it for everything. Never load a second copy of the engine
in this tool; a second copy splits the RNG and leaves the
melody/bass_line/drops internals unpatched, so every stem would
silently contain the full mix.

Rules kept from checkpoint 26 / MD1 / MD2: the full flute tail
(F#-E-D) stays reserved for the resolve stinger and rift_finale --
outros close on the tonic pad + bell instead, except rift_finale
itself, whose outro may play the full tail (the set's only full
close), and thang_long, whose outro uses the low pluck tail (the
thang_long precedent: the cue itself answers with the tail in low
pluck at bars 10-11). No external samples, no ported bytes, no
voices. The 541 ported PackV1 files and the checkpoint-26/30/MD1/MD2
packs are untouched and are NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/intros/<stem>_intro.wav
  Art_Source/Audio/Muse/COMPOSED/outros/<stem>_outro.wav
  Art_Source/Audio/Muse/COMPOSED/stems/<stem>_stem_<group>.wav
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/intros|outros|stems|layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD3_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md3 block + openForMdCp4; openForMdCp2 and
    openForMdCp3 kept so the MD1/MD2 validators still pass)
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
            / "MUSIC_SCORE_MD3_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
MD1_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md3"
TMP.mkdir(parents=True, exist_ok=True)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# THE engine instance: the checkpoint-26 builders live in
# build_composed_music.py itself. Load it once here and use it for
# everything -- never load a second copy (see the module docstring).
cm = _load("build_composed_music",
            TOOLS_DIR / "build_composed_music.py")

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
             "build_composed_score_md3.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the checkpoint-26 "
             "arrangements (build_composed_music.py); no external "
             "samples")
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; the full flute tail stays "
              "reserved for the resolve stinger and rift_finale")
STEM_SUM_NOTE = ("lead + padbass + percussion sum to the shipped "
                 "checkpoint-26 master within 24-bit quantisation "
                 "(max abs diff <= 5e-7, about 2 LSB); re-checked "
                 "from real bytes by check_composed_score_md3_v1.py")
SUM_THRESHOLD = 5e-7

GROUPS = ("lead", "padbass", "percussion")
GROUP_OF_VOICE = {"flute": "lead", "pluck": "lead", "bell": "lead",
                  "bass": "padbass"}
VOICE_FN = {"pluck": cm.pluck, "flute": cm.flute, "bell": cm.bell,
            "bass": cm.bass_note}

# Reproducing RNG history per stem cue, recovered by search against
# the shipped checkpoint-26 masters (least-squares gain fit; a match
# is a residual at the 24-bit quantisation floor, 1.19e-07):
#   ben_mua, thang_long, quiet_discovery, sa_hoa, bach_uyen: fresh
#     RNG (no prior render);
#   rift_finale: after ben_mua; boss_mang_cot: after thang_long;
#   lam_trieu: after quiet_discovery; tran_son: after sa_hoa.
# The original session was built in pairs (two cues per --only run,
# in piece order within each pair).
REPRO_PRIOR = {
    "ben_mua": [],
    "thang_long": [],
    "boss_mang_cot": ["thang_long"],
    "quiet_discovery": [],
    "lam_trieu": ["quiet_discovery"],
    "sa_hoa": [],
    "tran_son": ["sa_hoa"],
    "bach_uyen": [],
    "rift_finale": ["ben_mua"],
}
STEM_CUES = tuple(REPRO_PRIOR.keys())


# ------------------------------------------------------- stem routing
# The piece builders write into one track through cm primitives.
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
    cm.chord = chord_routed


def _remove_routing():
    cm.play = play
    cm.add = add
    cm.chord = chord


# ------------------------------------------------------------ helpers
def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied, so stems can apply the identical gain
    sequence. This matters: a single pre-multiplied factor differs
    from the sequential multiplications in the last float64 ulp, and
    that is enough to flip 24-bit LSBs and break bit-exact reference
    reproduction (the checkpoint-26 masters were gain-staged by
    gain_stage itself, so only the identical operation sequence
    reproduces them). Returns (track, mults, lufs, tp)."""
    tmpf = TMP / f"{tag}_measure.wav"
    mults = []
    cur = track
    for attempt in range(3):
        cm.write_f32_wav(cur, tmpf)
        lufs, tp = cm.measure_loudnorm(tmpf)
        gain = min(target_lufs - lufs, tp_ceiling - tp)
        if abs(gain) < 0.15 or attempt == 2:
            return cur, mults, lufs, tp
        mult = 10.0 ** (gain / 20.0)
        mults.append(mult)
        cur = cur * mult
    return cur, mults, lufs, tp


def loop_process(track, lp_hz):
    """The checkpoint-26 loop construction, applied per stem so every
    stem is loopable on its own and the stems sum to the looped
    master."""
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
    for spec in cm.PIECES:
        stem = spec[0]
        order.append(f"MUSIC/{stem}_intro")
        order.append(f"MUSIC/{stem}_outro")
        if stem in STEM_CUES:
            for g in GROUPS:
                order.append(f"MUSIC/{stem}_stem_{g}")
    order.append("MUSIC/boss_mang_cot_layer_phase3")
    order.append("MUSIC/tragedy_layer_intensity")
    order.append("MUSIC/arena_layer_low")
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": sum(1 for c in cues if c["kind"] == "INTRO"),
              "outro": sum(1 for c in cues if c["kind"] == "OUTRO"),
              "stems": sum(1 for c in cues if c["kind"] == "STEM"),
              "layers": sum(1 for c in cues if c["kind"] == "LAYER"),
              "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD3_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 3 - intro/outro "
                      "+ stems + phase layers for the 9 checkpoint-26 "
                      "score cues (Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: intros, outros, "
                      "stems and phase layers authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md3.py (synthesis engine "
                      "and checkpoint-26 arrangements reused from "
                      "build_composed_music.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These "
                      f"{counts['total']} files are NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, checkpoint-30, "
                      "MD1 and MD2 packs, which keep their own "
                      "provenance and are untouched.",
        "counts": counts,
        "cues": cues,
        "stemGroups": stem_groups,
        "referenceReproduction": ref_repro,
        "notes": [
            "Stems regroup the checkpoint-26 arrangements: "
            + STEM_SUM_NOTE,
            "Intros/outros are 2-bar one-shots at the parent cue's "
            "tempo (-22 LUFS target, same as the music); an intro "
            "ends on a handoff bell at the loop's first downbeat, an "
            "outro closes on the tonic pad + bell with a 0.5 s fade. "
            "The full flute tail stays reserved for the resolve "
            "stinger and rift_finale: only the rift_finale outro "
            "plays it (the set's only full close); the thang_long "
            "outro uses the low pluck tail, the thang_long precedent "
            "(the cue itself answers with the tail in low pluck at "
            "bars 10-11); the boss outro uses the minor-head pluck "
            "fragment and the sa_hoa outro its A-minor mapped head.",
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD3 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ and do NOT replace "
            "the ported PackV1 files, their cue bindings, or the "
            "checkpoint-26/30/MD1/MD2 cues.",
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
          f"{pack['counts']['total']} MD3 cues", flush=True)
    return pack

# ------------------------------------------------- reference + stems
def render_pregain(spec):
    """Render one cue's loop-processed track WITHOUT gain staging.
    Used both to advance the RNG through a prior piece and to render
    a reference whose gain is recovered afterwards."""
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    seconds = bars * 240.0 / bpm
    tr = new_track(seconds)
    builder(tr, bpm)
    tr, raw_jump = loop_process(tr, lp_hz)
    return tr, raw_jump


def fit_gain(track, master_path):
    """Least-squares scalar gain mapping the pre-gain track to the
    shipped master, plus the max abs residual after the fit. When the
    pre-gain track is bit-identical to the original's, the residual
    sits at the 24-bit quantisation floor (1.19e-07)."""
    ship = decode_f32(master_path)
    assert ship.shape == track.shape, (master_path, track.shape,
                                       ship.shape)
    g = float((track * ship).sum() / (track * track).sum())
    diff = float(np.max(np.abs(track * g - ship)))
    return g, diff


def render_reference(spec, want_sha, master_path):
    """Re-render one stem cue from its recovered RNG history and
    recover its gain. Returns (track, gain_mults, lufs, tp,
    start_state, repro_record).

    Gain recovery, in order: (1) gain_stage's multipliers, applied
    exactly as gain_stage applies them -- if the resulting master is
    bit-exact (same sha256), those multipliers are the cue's gain;
    (2) otherwise the least-squares fitted gain against the shipped
    master -- the pre-gain track is bit-identical to the original's,
    so the fitted gain is the original gain to ~1e-9 and the residual
    is the 24-bit quantisation floor. A reference that reproduces
    neither way (residual > 2.5e-7) raises: no stems are rendered
    from a diverged reference."""
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    cm.RNG = np.random.default_rng(26)
    by_stem = {s[0]: s for s in cm.PIECES}
    for prior in REPRO_PRIOR[stem]:
        render_pregain(by_stem[prior])
    start_state = copy.deepcopy(cm.RNG.bit_generator.state)
    pre, raw_jump = render_pregain(spec)
    staged, mults, lufs, tp = stage_like_gain_stage(
        pre, -22.0, -7.0, stem)
    tmp = TMP / f"ref_{stem}.wav"
    write_master_wav(staged, tmp)
    got_sha = hashlib.sha256(tmp.read_bytes()).hexdigest()
    if got_sha == want_sha:
        tmp.unlink(missing_ok=True)
        repro = {
            "cueKey": cue_key,
            "cp26MasterSha256": want_sha,
            "reproducedSha256": got_sha,
            "match": True,
            "maxAbsDiff": 0.0,
            "fittedGain": None,
            "gainMethod": "gain_stage",
            "priorRenders": list(REPRO_PRIOR[stem]),
            "method": "re-rendered from the recovered RNG history "
                      "(prior renders listed) with the checkpoint-26 "
                      "pipeline; gain_stage's multipliers reproduce "
                      "the shipped master bit-exact",
        }
        return staged, mults, lufs, tp, start_state, repro
    g, diff = fit_gain(pre, master_path)
    if diff > 2.5e-7:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(
            f"reference {stem} does not reproduce the shipped "
            f"checkpoint-26 master (residual {diff:.2e} after fitted "
            "gain); refusing to render stems from a diverged "
            "reference")
    fitted = pre * g
    write_master_wav(fitted, tmp)
    got_sha2 = hashlib.sha256(tmp.read_bytes()).hexdigest()
    flufs, ftp = cm.measure_loudnorm(tmp)
    tmp.unlink(missing_ok=True)
    repro = {
        "cueKey": cue_key,
        "cp26MasterSha256": want_sha,
        "reproducedSha256": got_sha2,
        "match": got_sha2 == want_sha,
        "maxAbsDiff": diff,
        "fittedGain": g,
        "gainMethod": "least_squares_fit",
        "priorRenders": list(REPRO_PRIOR[stem]),
        "method": "re-rendered from the recovered RNG history "
                  "(prior renders listed) with the checkpoint-26 "
                  "pipeline; gain_stage's multipliers do NOT "
                  "reproduce the shipped master (the shipped master "
                  "was gain-staged slightly differently, ~0.01 dB), "
                  "so the gain was fitted by least squares against "
                  "the shipped master -- the pre-gain track is "
                  "bit-identical to the original's (residual at the "
                  "24-bit quantisation floor)",
    }
    return fitted, [g], flufs, ftp, start_state, repro


def render_stems(spec, start_state, gain_mults):
    """Render the 3 stems of one checkpoint-26 cue with the RNG state
    restored to the cue's reference-render start, so every event's
    synthesis is bit-identical to the reference. Returns {group:
    track} at the reference gain (loop-processed, the same gain
    multipliers applied in the same order as the reference)."""
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
            for m in gain_mults:
                track = track * m
            out[group] = track
            raw_jumps[group] = rj
        return out, raw_jumps
    finally:
        _ACTIVE["group"] = None
        _ACTIVE["track"] = None
        _ACTIVE["dummy"] = None
        _remove_routing()


def check_stem_sum(cp26_master_path, stem_paths):
    """Sum the 3 stem masters (real bytes) and compare with the
    shipped checkpoint-26 master. Returns (max_abs_diff, rms_diff)."""
    ref = decode_f32(cp26_master_path)
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
# Outros are 2 bars: tonic pad, motif head (or the cue's own tail
# rule, see motif_events), bass root, tonic bell at bar 1, 0.5 s end
# fade. No full flute tail anywhere except the rift_finale outro.
INTRO_OUTRO = {
    # stem: (first, tonic, root, motif_voice, motif_shift, extras)
    "ben_mua": ("D", "D", 38, "flute", 0, ("drops",)),
    "thang_long": ("D", "D", 38, "flute", 0, ("bells",)),
    "boss_mang_cot": ("Dm", "Dm", 26, "pluck", 0,
                      ("drone_d1", "cold_bell")),
    "quiet_discovery": ("D", "D", 38, "flute", 0, ("drops",)),
    "lam_trieu": ("G", "G", 31, "flute", 5, ("shaker",)),
    "sa_hoa": ("Dm", "Dm", 33, "pluck", 0, ("drums",)),
    "tran_son": ("D", "D", 38, "bell", 0, ("drums",)),
    "bach_uyen": ("Bm", "Bm", 35, "flute", -12, ("drops",)),
    "rift_finale": ("D", "D", 38, "flute", 0, ()),
}
# D F A, the minor head the boss piece states in low pluck.
FRAG_MINOR = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]
# The motif head mapped to A minor pentatonic (A C D E G), the way
# the sa_hoa piece maps it by scale-degree index.
SA_HEAD = [(0, 69, 1), (1, 74, 1), (2, 76, 1.5), (3.5, 79, 0.5)]


def motif_events(stem, kind):
    """(events, voice, bright) for a cue's intro/outro motif. bright
    is None when the voice takes no bright kwarg (flute/bell)."""
    first, tonic, root, voice, shift, extras = INTRO_OUTRO[stem]
    if stem == "boss_mang_cot":
        return FRAG_MINOR, "pluck", 0.4
    if stem == "sa_hoa":
        return SA_HEAD, "pluck", 1.4
    if kind == "outro" and stem == "rift_finale":
        # The withheld tail, at last: the set's only full close.
        return MOTIF_TAIL, "flute", None
    if kind == "outro" and stem == "thang_long":
        # Low pluck tail: the thang_long precedent (the cue itself
        # answers with the tail in low pluck at bars 10-11).
        return MOTIF_TAIL, "pluck", None
    head = [(be, m + shift, ln) for be, m, ln in MOTIF_HEAD]
    return head, voice, (0.4 if voice == "pluck" else None)


def _melody_motif(tr, stem, kind, bpm, vel, pan=0.0):
    events, voice, bright = motif_events(stem, kind)
    if bright is None:
        melody(tr, voice, events, bpm, 0, vel, pan=pan)
    else:
        melody(tr, voice, events, bpm, 0, vel, pan=pan, bright=bright)


def build_intro(spec):
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz,
     structure) = spec
    first, tonic, root, voice, shift, extras = INTRO_OUTRO[stem]
    seconds = 8 * beat_s(bpm)  # 2 bars
    tr = new_track(seconds)
    b = beat_s(bpm)
    chord(tr, CH[first], 0.0, 7 * b, 0.30)
    play(tr, "bell", CH[first][0] + 24, 0.0, 2 * b, 0.16)
    _melody_motif(tr, stem, "intro", bpm, 0.7)
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
    if "shaker" in extras:
        for bt in (1.5, 3.5, 5.5, 7.5):
            add(tr, shaker(0.07), bt * b, 0.45, 0.045)
    if "bells" in extras:
        play(tr, "bell", CH[first][0] + 24, 4 * b, 2 * b, 0.18,
             pan=-0.3)
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
    _melody_motif(tr, stem, "outro", bpm, 0.55)
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
    if "shaker" in extras:
        add(tr, shaker(0.07), 5.5 * b, 0.45, 0.045)
    if "bells" in extras:
        play(tr, "bell", CH[tonic][0] + 24, 0.0, 2 * b, 0.18,
             pan=0.3)
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
                   "tonic pad + motif head + bass root + tonic bell "
                   "at bar 1; 0.5 s end fade")
                + (f"; low-pass {lp_hz} Hz like the parent cue"
                   if lp_hz else "")
                + ("; outro plays the full flute tail (the set's "
                   "only full close)"
                   if kind == "outro" and stem == "rift_finale" else "")
                + ("; outro uses the low pluck tail (thang_long "
                   "precedent)"
                   if kind == "outro" and stem == "thang_long" else "")
                + ("; minor-head pluck fragment (boss motif)"
                   if stem == "boss_mang_cot" else "")
                + ("; A-minor mapped motif head"
                   if stem == "sa_hoa" else "")),
            "rendering": RENDERING,
        },
        "master": m_entry, "runtime": r_entry,
    }

# --------------------------------------------------------- phase layers
def layer_boss_phase3():
    """Additive phase-3 layer over boss_mang_cot (10 bars @ 66 bpm):
    drums on all four beats (the base heartbeat is beats 0/1.5, the
    phase-2 layer fills 1/2/3), sixteenth-note D1 bass pulse, cold F4
    bell marks every bar, and the minor-head pluck fragment on the
    bars neither the base (2, 5, 7, 8) nor phase 2 (1, 4, 6, 9) uses
    (0, 3). No pad, no flute -- those stay in the base cue."""
    bpm, bars = 66, 10
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 1, 2, 3):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.24)
        for bt in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
            play(tr, "bass", 26, bar * 4 * b + bt * b, 0.8 * b, 0.45)
        play(tr, "bell", 65, bar * 4 * b, 3 * b, 0.15, pan=-0.2)
    for bar in (0, 3):
        melody(tr, "pluck", FRAG_MINOR, bpm, bar, 0.5, pan=0.15,
               bright=0.4)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "boss_mang_cot_layer_phase3")
    return tr, raw_jump


def layer_tragedy_intensity():
    """Additive intensity layer over tragedy (12 bars @ 56 bpm): the
    base is sparse by design (Dm pads, solo flute fragments, single
    bells, one low pluck figure, no drums), so this layer adds the
    pulse the base withholds -- low drums on beats 0 and 2, a D2
    quarter-note bass pedal, a D4 bell toll every 2 bars, and the low
    pluck figure (D-A) on bars 2, 6, 10, where the base has no pluck
    (its only pluck figure is at bar 9). No flute, no pad."""
    bpm, bars = 56, 12
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 2):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.25)
        for bt in (0, 1, 2, 3):
            play(tr, "bass", 38, bar * 4 * b + bt * b, 1.6 * b, 0.4)
        if bar % 2 == 0:
            play(tr, "bell", 62, bar * 4 * b, 3 * b, 0.16, pan=0.2)
    for bar in (2, 6, 10):
        melody(tr, "pluck", [(0, D4, 1), (2, A4, 2)], bpm, bar, 0.45,
               pan=0.25, bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "tragedy_layer_intensity")
    return tr, raw_jump


def layer_arena_low():
    """Additive low-intensity layer over arena (16 bars @ 120 bpm):
    the base is already dense (drums every beat plus an offbeat hit,
    shaker, pluck ostinato, bar-line bells), so this layer is the
    sparse bed the adapter fades to for low-intensity moments -- drum
    on beat 0 only, a whole-note bass root per bar (the base's own
    root progression), a D6 bell every 4 bars. No ostinato, no
    shaker."""
    bpm, bars = 120, 16
    roots = [38, 38, 33, 38, 35, 38, 33, 38,
             38, 38, 33, 35, 43, 33, 38, 38]
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.22)
        play(tr, "bass", roots[bar], bar * 4 * b, 3.4 * b, 0.45)
        if bar % 4 == 0:
            play(tr, "bell", D6, bar * 4 * b, 2 * b, 0.15, pan=0.3)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "arena_layer_low")
    return tr, raw_jump


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
    to MD CP3, an md3 block records what this checkpoint delivered,
    openForMdCp4 lists what stays open. openForMdCp2 and openForMdCp3
    are KEPT so the MD1/MD2 validators (which assert they are
    non-empty) still pass; slots and transitions are untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 3"
    cov["md3"] = {
        "pack": "MUSIC_SCORE_MD3_pack_v1",
        "intros": 9,
        "outros": 9,
        "stems": 27,
        "layers": 3,
        "detail": ("2-bar intro/outro for each of the 9 "
                   "checkpoint-26 cues; lead / pad-bass / percussion "
                   "stems per checkpoint-26 cue, summing to the "
                   "shipped checkpoint-26 master within 24-bit "
                   "quantisation; additive phase layers "
                   "MUSIC/boss_mang_cot_layer_phase3, "
                   "MUSIC/tragedy_layer_intensity and "
                   "MUSIC/arena_layer_low."),
        "reproHistories": {
            "ben_mua": [], "thang_long": [],
            "boss_mang_cot": ["thang_long"],
            "quiet_discovery": [],
            "lam_trieu": ["quiet_discovery"],
            "sa_hoa": [], "tran_son": ["sa_hoa"],
            "bach_uyen": [], "rift_finale": ["ben_mua"],
            "note": ("The shipped checkpoint-26 masters were built "
                     "in several separate renders (pairs per --only "
                     "run, in piece order within each pair), so a "
                     "single sequential re-render does not reproduce "
                     "them; each cue's reproducing RNG history is "
                     "listed here and recorded per cue in the MD3 "
                     "pack's referenceReproduction block."),
        },
    }
    cov["openForMdCp4"] = [
        "Ear audition of all MD1/MD2/MD3 cues + loop seams "
        "(NOT_AUDITIONED).",
        "More phase-layer candidates (e.g. boss phase 4, "
        "swamp/dungeon intensity layers).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 3, "
          f"md3 recorded, openForMdCp4 listed", flush=True)
    return cov


# ---------------------------------------------------------------- main
def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))
    cp26_pack = json.loads(CP26_PACK.read_text(encoding="utf-8"))
    cp26_by_key = {c["cueKey"]: c for c in cp26_pack["cues"]}
    md1_pack = json.loads(MD1_PACK.read_text(encoding="utf-8"))
    md1_by_key = {c["cueKey"]: c for c in md1_pack["cues"]}

    by_key = {}
    stem_groups = []
    ref_repro = []
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}
        stem_groups = existing.get("stemGroups", [])
        ref_repro = existing.get("referenceReproduction", [])

    # --- 1. Reference re-renders (recovered RNG history) + stems ---
    if only is None or "stems" in only or "reference" in only:
        for spec in cm.PIECES:
            stem = spec[0]
            if stem not in STEM_CUES:
                continue
            ref_tr, gain_mults, lufs, tp, start_state, repro = \
                render_reference(
                    spec,
                    cp26_by_key[f"MUSIC/{stem}"]["master"]["sha256"],
                    ROOT / cp26_by_key[f"MUSIC/{stem}"]["master"]
                    ["path"])
            print(f"reference {stem}: "
                  f"{'sha MATCHES' if repro['match'] else 'reproduced '
                   'to ' + format(repro['maxAbsDiff'], '.2e')} "
                  f"checkpoint-26 master ({lufs:.2f} LUFS / "
                  f"{tp:.2f} dBTP; gain via {repro['gainMethod']})",
                  flush=True)
            ref_repro = [r for r in ref_repro
                         if r["cueKey"] != f"MUSIC/{stem}"]
            ref_repro.append(repro)
            if only is not None and "stems" not in only:
                continue
            stems, raw_jumps = render_stems(spec, start_state,
                                            gain_mults)
            stem_paths = []
            for group in GROUPS:
                m_entry, r_entry = write_pair(
                    stems[group], f"{stem}_stem_{group}", "stems",
                    "stem")
                stem_paths.append(MASTER_DIR / "stems"
                                  / f"{stem}_stem_{group}.wav")
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
                            f"{group} stem of {stem} (checkpoint-26 "
                            "arrangement, regrouped): "
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
                by_key[entry["cueKey"]] = entry
                print(f"OK {entry['cueKey']}: "
                      f"{m_entry['durationSeconds']} s master "
                      f"{m_entry['integratedLufs']} LUFS / "
                      f"{m_entry['truePeakDbtp']} dBTP", flush=True)
            max_diff, rms_diff = check_stem_sum(
                ROOT / cp26_by_key[f"MUSIC/{stem}"]["master"]["path"],
                stem_paths)
            assert max_diff <= SUM_THRESHOLD, (stem, max_diff)
            stem_groups = [g for g in stem_groups
                           if g["parentCueKey"] != f"MUSIC/{stem}"]
            stem_groups.append({
                "parentCueKey": f"MUSIC/{stem}",
                "method": "lead + padbass + percussion masters summed "
                          "from real bytes vs the shipped checkpoint-26 "
                          "master",
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
        for spec in cm.PIECES:
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
        boss = cp26_by_key["MUSIC/boss_mang_cot"]
        entry = render_layer(
            "boss_mang_cot_layer_phase3",
            "MUSIC/boss_mang_cot_layer_phase3",
            "Mãng Cốt · Lớp giai đoạn 3", "MUSIC/boss_mang_cot",
            ROOT / boss["master"]["path"],
            boss["master"]["durationSeconds"], 66, 10,
            layer_boss_phase3,
            "Additive phase-3 layer over boss_mang_cot (10 bars @ "
            "66 bpm): drums on all four beats, sixteenth-note D1 "
            "bass pulse, cold F4 bell marks every bar, minor-head "
            "pluck fragments on bars 0 and 3 (the bars neither the "
            "base nor phase 2 uses). No pad, no flute -- those stay "
            "in the base cue. -25 LUFS target; combined base+layer "
            "loudness measured from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key, stem_groups, ref_repro)

        tragedy = md1_by_key["MUSIC/tragedy"]
        entry = render_layer(
            "tragedy_layer_intensity", "MUSIC/tragedy_layer_intensity",
            "Bi kịch · Lớp tăng cường", "MUSIC/tragedy",
            ROOT / tragedy["master"]["path"],
            tragedy["master"]["durationSeconds"], 56, 12,
            layer_tragedy_intensity,
            "Additive intensity layer over tragedy (12 bars @ 56 "
            "bpm): low drums on beats 0 and 2, D2 quarter-note bass "
            "pedal, D4 bell toll every 2 bars, low pluck figure on "
            "bars 2/6/10. The base is sparse by design (no drums); "
            "this layer adds the pulse the base withholds. -25 LUFS "
            "target; combined base+layer loudness measured from real "
            "bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key, stem_groups, ref_repro)

        arena = md1_by_key["MUSIC/arena"]
        entry = render_layer(
            "arena_layer_low", "MUSIC/arena_layer_low",
            "Đấu trường · Lớp trầm", "MUSIC/arena",
            ROOT / arena["master"]["path"],
            arena["master"]["durationSeconds"], 120, 16,
            layer_arena_low,
            "Additive low-intensity layer over arena (16 bars @ 120 "
            "bpm): drum on beat 0 only, whole-note bass root per bar "
            "(the base's own root progression), D6 bell every 4 "
            "bars. The base is already dense; this is the sparse bed "
            "the adapter fades to for low-intensity moments. -25 "
            "LUFS target; combined base+layer loudness measured from "
            "real bytes.")
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
