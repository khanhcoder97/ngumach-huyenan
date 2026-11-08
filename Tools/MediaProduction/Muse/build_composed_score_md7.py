#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 7: more phase layers.

Work Order 37 module M-D, following checkpoint 6 (MD6: ben_mua,
lam_trieu, sa_hoa intensity). The coverage matrix
(MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work as
the second item of openForMdCp7 -- the last five intensity layers
for the checkpoint-26 cues:

  * thang_long intensity -- the city pulse the street arrangement
    withholds (checkpoint-26 cue, 16 bars @ 92 bpm, D major);
  * tran_son intensity -- the gate pulse the bell-led stately
    form withholds (checkpoint-26 cue, 15 bars @ 90 bpm, D major);
  * bach_uyen intensity -- the deep current the underwater city
    withholds (checkpoint-26 cue, 15 bars @ 62 bpm, B minor,
    whole mix low-passed at 850 Hz like the parent);
  * rift_finale intensity -- the resolve pulse the five-stream
    finale withholds (checkpoint-26 cue, 16 bars @ 100 bpm,
    D major);
  * quiet_discovery intensity -- the depth the exploration
    silence withholds (checkpoint-26 cue, 16 bars @ 60 bpm,
    D major).

All five are additive loops at the parent cue's tempo/bars
(-25 LUFS target, same as the MD2/MD3/MD4/MD5/MD6 layers): they
play over the base cue, they do not replace it. Combined
base+layer loudness/true-peak is measured from real bytes and
recorded per layer; the validator re-checks it from real bytes.
After this checkpoint every checkpoint-26 music cue carries an
intensity layer (ben_mua, thang_long, quiet_discovery, lam_trieu,
sa_hoa, tran_son, bach_uyen, rift_finale); the only score cue
still without one is MD1's Thanh Lac.

Layer design -- each layer adds only what its base and the earlier
layers do NOT already do, so stacking stays musical:

  * thang_long intensity: the base is a busy street arrangement
    -- pads on every bar, a bell of the chord tonic on every bar
    line, bass on ALL FOUR beats, pluck arpeggios on every bar,
    flute at bars 0/8, a low-pluck tail answer at bar 10, a flute
    restatement at bar 14, and shaker on every offbeat. No drums
    at all. The layer adds the one thing the street withholds --
    a soft drum on the bar line and on beat 2 (the two-beat city
    pulse) -- plus a low pluck echo of the motif head on bars 4
    and 12 (bars where the base has no melody; the arpeggio is
    texture, not melody). No bells (the base tolls every bar),
    no shaker (the base already owns the full offbeat grid),
    no bass fill (the bass already plays all four beats), no pad,
    no flute.
  * tran_son intensity: the base is a bell-led stately form --
    pads on every bar, bass on beat 0 only, the bell states the
    motif at bars 0/9, a low flute answers at bar 5, a drum marks
    every bar line, and the final bar leaves a soft hanging E5
    under the gate bell. No shaker, no pluck. The layer adds the
    gate pulse -- a soft drum on beat 2 (the base drum is bar
    line only, so the two-beat pulse is now complete), a bass
    fill on beats 1 and 3 on the bar's own root, shaker on the
    offbeats, and a low pluck echo of the motif head on bars 3
    and 11 (bars where the base has no melody). No bells (the
    bell is the voice).
  * bach_uyen intensity: the base is the theme underwater -- pads
    on every bar, bass on beats 0/2 only, the motif an octave
    down in flute at bars 1/9, slow bell marks (D4 at bar 5, A4
    at bar 12), sparse drops, whole mix low-passed at 850 Hz.
    No drums, no shaker, no pluck. The layer adds the deep
    current the city withholds -- a soft drum on the bar line,
    a bass fill on beats 1 and 3 on the bar's own root, shaker
    on the offbeats (muffled by the same 850 Hz low-pass, so it
    reads as soft underwater ticks), a low pluck echo of the
    motif head on bars 6 and 13 (bars where the base has no
    melody), and a D5 bell toll on bar 14 (the tonic bell on the
    final bar; the base has no bell there). No flute (the base
    flute stays the voice), no drops (the base already drops),
    no pad. The whole layer is low-passed at 850 Hz like its
    parent, BEFORE the gain stage, so the -25 LUFS target is
    measured on the filtered layer.
  * rift_finale intensity: the base passes the motif across five
    registers -- pads on every bar, bass on beats 0/2, low pluck
    at bar 0, mid pluck at bar 3, flute at bar 6, bell at bar 9,
    full question in flute + bell at bar 11, the withheld tail
    in flute at bar 14, and the set's only full D-major close
    (D6 + D5 bells, one drum) at bar 15. No shaker. The layer
    adds the resolve pulse -- a soft drum on the bar lines of
    bars 0-14 (bar 15 already has the closing drum, so it is
    left alone), a bass fill on beats 1 and 3 on the bar's own
    root, shaker on the offbeats, and a low pluck echo of the
    motif head on bars 5 and 13 (bars where the base has no
    melody). No bells (the base bells at 9/11/15 are the close),
    no flute (the streams are the voice).
  * quiet_discovery intensity: the base is exploration silence
    -- sparse chords (D bars 0-1, G bars 10-11, D bars 14-15),
    solo flute fragments at bars 0/8, single bells at bars
    4/6/12, a low pluck at bar 13, water drops and far-water
    noise. No bass, no drums, no shaker, no pad. The layer adds
    the depth the silence withholds -- a gentle bass on beats 0
    and 2 (D bars 0-9, G bars 10-13, D bars 14-15), shaker on
    the offbeats ONLY in the second half (bars 8-15; the
    discovery deepens), and a low pluck echo of the motif head
    on bars 2 and 10 (bars where the base has no melody). NO
    drums, deliberately: a bar-line drum would fight the cue's
    identity -- the pulse here is the bass and the late shaker,
    not a drum. No bells (the base bells are the voice), no pad
    (the chords stay sparse by design).

Single-engine rule (from checkpoint 2, still kept): the builders
live in build_composed_music.py itself, so this tool loads THAT file
once as cm and uses it for everything. Never load a second copy.

Rules kept from checkpoint 26 / MD1 / MD2 / MD3 / MD4 / MD5 / MD6:
no external samples, no ported bytes, no voices. The 541 ported
PackV1 files and the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5/MD6 packs
are untouched and are NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD7_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md7 block + openForMdCp8; openForMdCp2,
    openForMdCp3, openForMdCp4, openForMdCp5, openForMdCp6 and
    openForMdCp7 kept so the MD1/MD2/MD3/MD4/MD5/MD6 validators
    still pass)
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
            / "MUSIC_SCORE_MD7_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md7"
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
add = cm.add
drum = cm.drum
shaker = cm.shaker
beat_s = cm.beat_s
room = cm.room
tail_wrap = cm.tail_wrap
end_landing = cm.end_landing
write_master_wav = cm.write_master_wav
encode_ogg = cm.encode_ogg
file_entry = cm.file_entry
seam_stats = cm.seam_stats
MOTIF_HEAD = cm.MOTIF_HEAD

D4, E4, FS4, A4, B4 = 62, 64, 66, 69, 71
D5, E5, FS5, A5, B5, D6 = 74, 76, 78, 81, 83, 86
G5 = 79
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; the full flute tail stays "
              "reserved for the resolve stinger and rift_finale")
RENDERING = ("procedural synthesis (additive pluck/flute/bell/pad/bass "
             "+ noise percussion), authored in "
             "build_composed_score_md7.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the checkpoint-26 "
             "arrangements (build_composed_music.py); no external "
             "samples")

# The motif head an octave down, for the low-pluck echoes.
MOTIF_HEAD_LOW = [(be, m - 12, ln) for be, m, ln in MOTIF_HEAD]
# The thang_long base's bass root progression (piece_thang_long,
# CP26). Not used by the thang_long layer (its bass already plays
# all four beats); recorded so the progression stays checkable.
THANG_LONG_ROOTS = [38, 43, 38, 33, 35, 43, 38, 33,
                    38, 43, 35, 33, 38, 43, 33, 38]
# The tran_son base's bass root progression (piece_tran_son, CP26).
TRAN_SON_ROOTS = [38, 43, 38, 35, 38, 43, 33, 38,
                  43, 35, 38, 33, 38, 43, 38]
# The bach_uyen base's bass root progression (piece_bach_uyen, CP26).
BACH_UYEN_ROOTS = [35, 35, 40, 35, 43, 35, 40, 38,
                   35, 43, 40, 35, 38, 40, 35]
# The rift_finale base's bass root progression (piece_finale, CP26).
RIFT_FINALE_ROOTS = [38, 43, 35, 33, 38, 43, 35, 33,
                     38, 43, 35, 40, 33, 38, 38, 38]
# The quiet_discovery chord roots (piece_quiet, CP26): D bars 0-9,
# G bars 10-13, D bars 14-15. The base has no bass at all; the
# layer is the first bass the cue ever carries.
QUIET_DISCOVERY_ROOTS = [38] * 10 + [43] * 4 + [38] * 2


def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied. Copied from the MD3/MD4/MD5/MD6 builders
    (same engine, same reason: a single pre-multiplied factor
    differs from the sequential multiplications in the last
    float64 ulp). Returns (track, mults, lufs, tp)."""
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
    """The checkpoint-26 loop construction (MD3/MD4/MD5/MD6 copy):
    room, tail wrap 1.5 s, end landing 0.25 s. lp_hz low-passes
    first when the parent cue is itself low-passed (bach_uyen at
    850 Hz; the other four MD7 parents are not low-passed)."""
    if lp_hz:
        for ch in range(2):
            track[:, ch] = cm.lowpass(track[:, ch], lp_hz)
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


# --------------------------------------------------------- phase layers
def layer_thang_long_intensity():
    """Additive intensity layer over thang_long (16 bars @ 92 bpm):
    the base is a busy street arrangement -- pads on every bar, a
    bell of the chord tonic on every bar line, bass on ALL FOUR
    beats, pluck arpeggios on every bar, flute at bars 0/8, a
    low-pluck tail answer at bar 10, a flute restatement at bar
    14, and shaker on every offbeat. No drums at all. This layer
    adds the one thing the street withholds -- a soft drum on the
    bar line and on beat 2 (the two-beat city pulse) -- plus a low
    pluck echo of the motif head on bars 4 and 12 (bars where the
    base has no melody; the arpeggio is texture, not melody). No
    bells (the base tolls every bar), no shaker (the base already
    owns the full offbeat grid), no bass fill (the bass already
    plays all four beats), no pad, no flute."""
    bpm, bars = 92, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        add(tr, drum(), bar * 4 * b + 2 * b, 0.0, 0.12)
    for bar in (4, 12):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "thang_long_layer_intensity")
    return tr, raw_jump


def layer_tran_son_intensity():
    """Additive intensity layer over tran_son (15 bars @ 90 bpm):
    the base is a bell-led stately form -- pads on every bar, bass
    on beat 0 only, the bell states the motif at bars 0/9, a low
    flute answers at bar 5, a drum marks every bar line, and the
    final bar leaves a soft hanging E5 under the gate bell. No
    shaker, no pluck. This layer adds the gate pulse -- a soft
    drum on beat 2 (the base drum is bar line only, so the
    two-beat pulse is now complete), a bass fill on beats 1 and 3
    on the bar's own root, shaker on the offbeats, and a low pluck
    echo of the motif head on bars 3 and 11 (bars where the base
    has no melody). No bells (the bell is the voice)."""
    bpm, bars = 90, 15
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b + 2 * b, 0.0, 0.15)
        for bt in (1, 3):
            play(tr, "bass", TRAN_SON_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.04)
    for bar in (3, 11):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "tran_son_layer_intensity")
    return tr, raw_jump


def layer_bach_uyen_intensity():
    """Additive intensity layer over bach_uyen (15 bars @ 62 bpm):
    the base is the theme underwater -- pads on every bar, bass on
    beats 0/2 only, the motif an octave down in flute at bars 1/9,
    slow bell marks (D4 at bar 5, A4 at bar 12), sparse drops,
    whole mix low-passed at 850 Hz. No drums, no shaker, no pluck.
    This layer adds the deep current the city withholds -- a soft
    drum on the bar line, a bass fill on beats 1 and 3 on the
    bar's own root, shaker on the offbeats (muffled by the same
    850 Hz low-pass, so it reads as soft underwater ticks), a low
    pluck echo of the motif head on bars 6 and 13 (bars where the
    base has no melody), and a D5 bell toll on bar 14 (the tonic
    bell on the final bar; the base has no bell there). No flute
    (the base flute stays the voice), no drops (the base already
    drops), no pad. The whole layer is low-passed at 850 Hz like
    its parent, BEFORE the gain stage, so the -25 LUFS target is
    measured on the filtered layer."""
    bpm, bars = 62, 15
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        for bt in (1, 3):
            play(tr, "bass", BACH_UYEN_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.04)
        if bar == 14:
            play(tr, "bell", D5, bar * 4 * b, 3 * b, 0.12, pan=0.2)
    for bar in (6, 13):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, 850.0)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "bach_uyen_layer_intensity")
    return tr, raw_jump


def layer_rift_finale_intensity():
    """Additive intensity layer over rift_finale (16 bars @ 100 bpm):
    the base passes the motif across five registers -- pads on
    every bar, bass on beats 0/2, low pluck at bar 0, mid pluck at
    bar 3, flute at bar 6, bell at bar 9, full question in flute +
    bell at bar 11, the withheld tail in flute at bar 14, and the
    set's only full D-major close (D6 + D5 bells, one drum) at bar
    15. No shaker. This layer adds the resolve pulse -- a soft
    drum on the bar lines of bars 0-14 (bar 15 already has the
    closing drum, so it is left alone), a bass fill on beats 1 and
    3 on the bar's own root, shaker on the offbeats, and a low
    pluck echo of the motif head on bars 5 and 13 (bars where the
    base has no melody). No bells (the base bells at 9/11/15 are
    the close), no flute (the streams are the voice)."""
    bpm, bars = 100, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        if bar < 15:
            add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        for bt in (1, 3):
            play(tr, "bass", RIFT_FINALE_ROOTS[bar],
                 bar * 4 * b + bt * b, 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.04)
    for bar in (5, 13):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "rift_finale_layer_intensity")
    return tr, raw_jump


def layer_quiet_discovery_intensity():
    """Additive intensity layer over quiet_discovery (16 bars @ 60
    bpm): the base is exploration silence -- sparse chords (D bars
    0-1, G bars 10-11, D bars 14-15), solo flute fragments at bars
    0/8, single bells at bars 4/6/12, a low pluck at bar 13,
    water drops and far-water noise. No bass, no drums, no shaker,
    no pad. This layer adds the depth the silence withholds -- a
    gentle bass on beats 0 and 2 (D bars 0-9, G bars 10-13, D bars
    14-15), shaker on the offbeats ONLY in the second half (bars
    8-15; the discovery deepens), and a low pluck echo of the
    motif head on bars 2 and 10 (bars where the base has no
    melody). NO drums, deliberately: a bar-line drum would fight
    the cue's identity -- the pulse here is the bass and the late
    shaker, not a drum. No bells (the base bells are the voice),
    no pad (the chords stay sparse by design)."""
    bpm, bars = 60, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 2):
            play(tr, "bass", QUIET_DISCOVERY_ROOTS[bar],
                 bar * 4 * b + bt * b, 1.6 * b, 0.35)
        if bar >= 8:
            for bt in (0.5, 1.5, 2.5, 3.5):
                add(tr, shaker(0.08), bar * 4 * b + bt * b,
                    -0.4 if bar % 2 else 0.4, 0.035)
    for bar in (2, 10):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "quiet_discovery_layer_intensity")
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


def save_pack(by_key):
    order = ["MUSIC/thang_long_layer_intensity",
             "MUSIC/tran_son_layer_intensity",
             "MUSIC/bach_uyen_layer_intensity",
             "MUSIC/rift_finale_layer_intensity",
             "MUSIC/quiet_discovery_layer_intensity"]
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": 0, "outro": 0, "stems": 0,
              "layers": len(cues), "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD7_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 7 - phase layers "
                      "(thang_long intensity, tran_son intensity, "
                      "bach_uyen intensity, rift_finale intensity, "
                      "quiet_discovery intensity; Work Order 37 "
                      "module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: phase layers "
                      "authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md7.py (synthesis engine "
                      "and checkpoint-26 arrangements reused from "
                      "build_composed_music.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These "
                      f"{counts['total']} files are NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, "
                      "checkpoint-30, MD1, MD2, MD3, MD4, MD5 and "
                      "MD6 packs, which keep their own provenance "
                      "and are untouched.",
        "counts": counts,
        "cues": cues,
        "notes": [
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Each MD7 layer adds only what its base and the earlier "
            "layers do not already do: thang_long intensity adds "
            "the two-beat city drum pulse the busy street "
            "arrangement withholds (no drums at all in the base) "
            "plus a low pluck echo on melody-free bars; tran_son "
            "intensity completes the two-beat drum pulse, fills "
            "the bass on beats 1/3 and adds the offbeat shaker the "
            "bell-led form withholds; bach_uyen intensity adds "
            "the deep current (bar-line drum, bass fill, offbeat "
            "shaker, motif echo, final-bar D5 bell), low-passed "
            "at 850 Hz like its parent; rift_finale intensity "
            "adds the resolve pulse (drums on bars 0-14, bass "
            "fill, offbeat shaker, motif echo) and leaves bar 15 "
            "alone, where the base already lands its only full "
            "close; quiet_discovery intensity adds the depth the "
            "silence withholds (first bass the cue ever carries, "
            "late shaker in the second half, motif echo) and "
            "deliberately carries NO drums, so the pulse never "
            "fights the cue's identity.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD7 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/layers/ and do NOT "
            "replace the ported PackV1 files, their cue bindings, or "
            "the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5/MD6 cues.",
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
          f"{pack['counts']['total']} MD7 cues", flush=True)
    return pack


# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP7, an md7 block records what this checkpoint delivered,
    openForMdCp8 lists what stays open. openForMdCp2, openForMdCp3,
    openForMdCp4, openForMdCp5, openForMdCp6 and openForMdCp7 are
    KEPT so the MD1/MD2/MD3/MD4/MD5/MD6 validators (which assert
    they are non-empty) still pass; slots and transitions are
    untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 7"
    cov["md7"] = {
        "pack": "MUSIC_SCORE_MD7_pack_v1",
        "layers": 5,
        "detail": ("Additive phase layers MUSIC/"
                   "thang_long_layer_intensity, MUSIC/"
                   "tran_son_layer_intensity, MUSIC/"
                   "bach_uyen_layer_intensity, MUSIC/"
                   "rift_finale_layer_intensity and MUSIC/"
                   "quiet_discovery_layer_intensity."),
    }
    cov["openForMdCp8"] = [
        "Ear audition of all MD1/MD2/MD3/MD4/MD5/MD6/MD7 cues + "
        "loop seams (NOT_AUDITIONED).",
        "More phase-layer candidates (e.g. Thanh Lac intensity "
        "layer -- the only score cue still without one).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 7, "
          f"md7 recorded, openForMdCp8 listed", flush=True)
    return cov


def _render_one(by_key, cp26_by_key, stem, cue_key, name_vi, parent_key,
                bpm, bars, layer_fn, structure):
    parent = cp26_by_key[parent_key]
    entry = render_layer(
        stem, cue_key, name_vi, parent_key,
        ROOT / parent["master"]["path"],
        parent["master"]["durationSeconds"], bpm, bars,
        layer_fn, structure)
    by_key[entry["cueKey"]] = entry
    print(f"OK {entry['cueKey']}: "
          f"{entry['master']['durationSeconds']} s master "
          f"{entry['master']['integratedLufs']} LUFS / "
          f"{entry['master']['truePeakDbtp']} dBTP; combined "
          f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
          f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
          flush=True)
    save_pack(by_key)
    return entry


# ---------------------------------------------------------------- main
def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))

    cp26_pack = json.loads(CP26_PACK.read_text(encoding="utf-8"))
    cp26_by_key = {c["cueKey"]: c for c in cp26_pack["cues"]}

    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}

    if only is None or "layers" in only:
        _render_one(
            by_key, cp26_by_key,
            "thang_long_layer_intensity",
            "MUSIC/thang_long_layer_intensity",
            "Thăng Long · Lớp tăng cường", "MUSIC/thang_long",
            92, 16, layer_thang_long_intensity,
            "Additive intensity layer over thang_long (16 bars @ 92 "
            "bpm): soft drum on the bar line and on beat 2 (the "
            "two-beat city pulse; the base has no drums at all) and "
            "a low pluck echo of the motif head on bars 4 and 12 "
            "(bars where the base has no melody; the arpeggio is "
            "texture, not melody). The base has pads on every bar, "
            "a bell of the chord tonic on every bar line, bass on "
            "all four beats, pluck arpeggios on every bar and "
            "shaker on every offbeat; this layer adds the pulse the "
            "street arrangement withholds. No bells, no shaker, no "
            "bass fill, no pad, no flute. -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        _render_one(
            by_key, cp26_by_key,
            "tran_son_layer_intensity",
            "MUSIC/tran_son_layer_intensity",
            "Trấn Sơn · Lớp tăng cường", "MUSIC/tran_son",
            90, 15, layer_tran_son_intensity,
            "Additive intensity layer over tran_son (15 bars @ 90 "
            "bpm): soft drum on beat 2 (the base drum is bar line "
            "only, so the two-beat pulse is now complete), bass "
            "fill on beats 1 and 3 on the bar's own root, shaker on "
            "the offbeats, and a low pluck echo of the motif head "
            "on bars 3 and 11 (bars where the base has no melody). "
            "The base has pads on every bar, bass on beat 0 only, "
            "the bell stating the motif at bars 0/9 and a low flute "
            "answer at bar 5; this layer adds the gate pulse. No "
            "bells (the bell is the voice). -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        _render_one(
            by_key, cp26_by_key,
            "bach_uyen_layer_intensity",
            "MUSIC/bach_uyen_layer_intensity",
            "Bạch Uyên · Lớp tăng cường", "MUSIC/bach_uyen",
            62, 15, layer_bach_uyen_intensity,
            "Additive intensity layer over bach_uyen (15 bars @ 62 "
            "bpm): soft drum on the bar line, bass fill on beats 1 "
            "and 3 on the bar's own root, shaker on the offbeats "
            "(muffled by the same 850 Hz low-pass as the parent, so "
            "it reads as soft underwater ticks), a low pluck echo "
            "of the motif head on bars 6 and 13 (bars where the "
            "base has no melody), and a D5 bell toll on bar 14 "
            "(the tonic bell on the final bar; the base has no bell "
            "there). The base has pads on every bar, bass on beats "
            "0/2 only, the motif an octave down in flute at bars "
            "1/9 and slow bell marks at bars 5/12; this layer adds "
            "the deep current the city withholds. Whole layer "
            "low-passed at 850 Hz like its parent, BEFORE the gain "
            "stage. No flute, no drops, no pad. -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        _render_one(
            by_key, cp26_by_key,
            "rift_finale_layer_intensity",
            "MUSIC/rift_finale_layer_intensity",
            "Ngũ Mạch · Lớp tăng cường", "MUSIC/rift_finale",
            100, 16, layer_rift_finale_intensity,
            "Additive intensity layer over rift_finale (16 bars @ "
            "100 bpm): soft drum on the bar lines of bars 0-14 "
            "(bar 15 already has the closing drum, so it is left "
            "alone), bass fill on beats 1 and 3 on the bar's own "
            "root, shaker on the offbeats, and a low pluck echo of "
            "the motif head on bars 5 and 13 (bars where the base "
            "has no melody). The base passes the motif across five "
            "registers and lands the set's only full D-major close "
            "at bar 15; this layer adds the resolve pulse. No "
            "bells, no flute. -25 LUFS target; combined base+layer "
            "loudness measured from real bytes.")
        _render_one(
            by_key, cp26_by_key,
            "quiet_discovery_layer_intensity",
            "MUSIC/quiet_discovery_layer_intensity",
            "Khoảng lặng khám phá · Lớp tăng cường",
            "MUSIC/quiet_discovery",
            60, 16, layer_quiet_discovery_intensity,
            "Additive intensity layer over quiet_discovery (16 bars "
            "@ 60 bpm): gentle bass on beats 0 and 2 (the first "
            "bass the cue ever carries; D bars 0-9, G bars 10-13, D "
            "bars 14-15), shaker on the offbeats ONLY in the second "
            "half (bars 8-15; the discovery deepens), and a low "
            "pluck echo of the motif head on bars 2 and 10 (bars "
            "where the base has no melody). The base is exploration "
            "silence -- sparse chords, solo flute fragments, single "
            "bells; this layer adds the depth the silence "
            "withholds. NO drums, deliberately: a bar-line drum "
            "would fight the cue's identity. No bells, no pad. "
            "-25 LUFS target; combined base+layer loudness "
            "measured from real bytes.")

    save_pack(by_key)
    update_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
