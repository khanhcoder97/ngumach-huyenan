#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 6: more phase layers.

Work Order 37 module M-D, following checkpoint 5 (MD5: boss phase 5,
hub intensity, rain intensity). The coverage matrix
(MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work as
the second item of openForMdCp6:

  * ben_mua intensity -- the pulse the pier theme withholds
    (checkpoint-26 cue, 17 bars @ 72 bpm, D major);
  * lam_trieu intensity -- the forest pulse the leaf-tick base
    leaves half-empty (checkpoint-26 cue, 20 bars @ 90 bpm,
    G major pentatonic);
  * sa_hoa intensity -- the weight the dry furnace cue withholds
    (checkpoint-26 cue, 20 bars @ 110 bpm, A minor pentatonic).

All three are additive loops at the parent cue's tempo/bars
(-25 LUFS target, same as the MD2/MD3/MD4/MD5 layers): they play
over the base cue, they do not replace it. Combined base+layer
loudness/true-peak is measured from real bytes and recorded per
layer; the validator re-checks it from real bytes.

Layer design -- each layer adds only what its base and the earlier
layers do NOT already do, so stacking stays musical:

  * ben_mua intensity: the base is the theme itself -- pads on
    every bar, bass on beats 0/2 only, flute states the question
    phrase at bars 0/4/10, pluck echoes at bars 2/6/12, a flute
    fragment at bar 14, and the final bar leaves the hanging E5
    over the tonic pad with a single D5 bell; water drops fall
    sparsely. No drums, no shaker, no bell before the final bar.
    The layer adds the pulse the pier theme withholds -- a soft
    drum on the bar line, a bass fill on beats 1 and 3 on the
    bar's own root, shaker on the offbeats (rain patter on the
    pier), a low pluck echo of the motif head on bars 8 and 15
    (bars where the base has no melody), and an E5 bell toll on
    bars 5 and 11 (E is the cue's hanging note). No flute (the
    base flute stays the voice), no drops (the base already drops),
    no pad.
  * lam_trieu intensity: the base transposes the motif to G major
    pentatonic -- pads on every bar, bass on beats 0/2 only, flute
    at bars 0/14, a low pluck echo at bar 4, an ornamented flute
    restatement at bar 8, and leaf-tick shaker on the EVEN bars
    only (beats 1.5/3.5), with sparse drops. No drums, no bells.
    The layer adds the forest pulse -- a soft drum on the bar
    line, a bass fill on beats 1 and 3 on the bar's own root,
    shaker on the ODD bars at 1.5/3.5 (completing the leaf-tick
    grid the base leaves half-empty), a low pluck echo of the
    motif head transposed to G on bars 6 and 12 (bars where the
    base has no melody), and a G5 bell toll on bars 10 and 18
    (the tonic bell; the base has no bells at all). No flute
    (the base flute stays the voice).
  * sa_hoa intensity: the base maps the motif to A minor
    pentatonic -- pads on even bars only, bass on beats 0/1.5/3,
    dry bright plucks at bars 0/6 (offset +0.5)/12, a soft drum
    on beat 2 of every bar and shaker on beat 3.5 of every bar.
    No bells, no flute. The layer adds the weight the dry
    furnace cue withholds -- a soft drum on the bar line (the
    base drum is beat 2 only, so the two-beat pulse is now
    complete), a bass fill on beats 1 and 2 on the bar's own
    root (beat 2 doubles the drum beat, beat 1 fills the gap),
    shaker on 0.5/1.5/2.5 (completing the offbeat grid the base
    leaves at 3.5 only), a low pluck echo of the A-minor motif
    head on bars 9 and 16 (bars where the base has no melody),
    and an A5 bell toll on bars 4 and 14 (the tonic bell; the
    base has no bells at all). No flute (pluck is the voice),
    no pad (the pads stay sparse by design).

Single-engine rule (from checkpoint 2, still kept): the builders
live in build_composed_music.py itself, so this tool loads THAT file
once as cm and uses it for everything. Never load a second copy.

Rules kept from checkpoint 26 / MD1 / MD2 / MD3 / MD4 / MD5: no
external samples, no ported bytes, no voices. The 541 ported PackV1
files and the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5 packs are
untouched and are NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD6_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md6 block + openForMdCp7; openForMdCp2,
    openForMdCp3, openForMdCp4, openForMdCp5 and openForMdCp6 kept
    so the MD1/MD2/MD3/MD4/MD5 validators still pass)
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
            / "MUSIC_SCORE_MD6_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md6"
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
             "build_composed_score_md6.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the checkpoint-26 "
             "arrangements (build_composed_music.py); no external "
             "samples")

# The motif head an octave down, for the ben_mua low-pluck echoes.
MOTIF_HEAD_LOW = [(be, m - 12, ln) for be, m, ln in MOTIF_HEAD]
# The motif head transposed to G (+5) and an octave down, for the
# lam_trieu low-pluck echoes (G major pentatonic).
LAM_TRIEU_HEAD_LOW = [(be, m + 5 - 12, ln) for be, m, ln in MOTIF_HEAD]
# The motif head mapped to A minor pentatonic and an octave down,
# for the sa_hoa low-pluck echoes (D->A, F#->D, A->E, B->G).
SA_HOA_HEAD_LOW = [(0, 57, 1), (1, 62, 1), (2, 64, 1.5), (3.5, 67, 0.5)]
# The ben_mua base's bass root progression (piece_ben_mua, CP26).
BEN_MUA_ROOTS = [38, 38, 43, 38, 35, 43, 38, 33,
                 38, 38, 43, 35, 40, 33, 38, 38, 38]
# The lam_trieu base's bass root progression (piece_lam_trieu, CP26).
LAM_TRIEU_ROOTS = [31, 36, 31, 38, 28, 36, 31, 38,
                   31, 36, 28, 38, 31, 36, 38, 31,
                   28, 36, 38, 31]
# The sa_hoa base's bass root progression (piece_sa_hoa, CP26).
SA_HOA_ROOTS = [33, 33, 41, 33, 36, 33, 41, 36,
                33, 33, 43, 33, 41, 36, 33, 33,
                41, 43, 33, 33]


def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied. Copied from the MD3/MD4/MD5 builders (same
    engine, same reason: a single pre-multiplied factor differs
    from the sequential multiplications in the last float64 ulp).
    Returns (track, mults, lufs, tp)."""
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
    """The checkpoint-26 loop construction (MD3/MD4/MD5 copy): room,
    tail wrap 1.5 s, end landing 0.25 s. lp_hz low-passes first when
    the parent cue is itself low-passed (none of the MD6 parents
    are)."""
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
def layer_ben_mua_intensity():
    """Additive intensity layer over ben_mua (17 bars @ 72 bpm): the
    base is the theme itself -- pads on every bar, bass on beats 0/2
    only, flute at bars 0/4/10, pluck echoes at bars 2/6/12, a flute
    fragment at bar 14, and the final bar leaves the hanging E5 over
    the tonic pad with a single D5 bell; sparse water drops. No
    drums, no shaker, no bell before the final bar. This layer adds
    the pulse the pier theme withholds -- a soft drum on the bar
    line, a bass fill on beats 1 and 3 on the bar's own root, shaker
    on the offbeats (rain patter on the pier), a low pluck echo of
    the motif head on bars 8 and 15 (bars where the base has no
    melody), and an E5 bell toll on bars 5 and 11 (E is the cue's
    hanging note). No flute (the base flute stays the voice), no
    drops (the base already drops), no pad."""
    bpm, bars = 72, 17
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        for bt in (1, 3):
            play(tr, "bass", BEN_MUA_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.04)
        if bar in (5, 11):
            play(tr, "bell", E5, bar * 4 * b, 3 * b, 0.12, pan=0.2)
    for bar in (8, 15):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "ben_mua_layer_intensity")
    return tr, raw_jump


def layer_lam_trieu_intensity():
    """Additive intensity layer over lam_trieu (20 bars @ 90 bpm):
    the base transposes the motif to G major pentatonic -- pads on
    every bar, bass on beats 0/2 only, flute at bars 0/14, a low
    pluck echo at bar 4, an ornamented flute restatement at bar 8,
    and leaf-tick shaker on the EVEN bars only (beats 1.5/3.5),
    with sparse drops. No drums, no bells. This layer adds the
    forest pulse -- a soft drum on the bar line, a bass fill on
    beats 1 and 3 on the bar's own root, shaker on the ODD bars at
    1.5/3.5 (completing the leaf-tick grid the base leaves
    half-empty), a low pluck echo of the motif head transposed to
    G on bars 6 and 12 (bars where the base has no melody), and a
    G5 bell toll on bars 10 and 18 (the tonic bell; the base has
    no bells at all). No flute (the base flute stays the voice)."""
    bpm, bars = 90, 20
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        for bt in (1, 3):
            play(tr, "bass", LAM_TRIEU_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.35)
        if bar % 2 == 1:
            for bt in (1.5, 3.5):
                add(tr, shaker(0.07), bar * 4 * b + bt * b, 0.45,
                    0.045)
        if bar in (10, 18):
            play(tr, "bell", G5, bar * 4 * b, 3 * b, 0.12, pan=-0.2)
    for bar in (6, 12):
        melody(tr, "pluck", LAM_TRIEU_HEAD_LOW, bpm, bar, 0.5,
               pan=0.25, bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "lam_trieu_layer_intensity")
    return tr, raw_jump


def layer_sa_hoa_intensity():
    """Additive intensity layer over sa_hoa (20 bars @ 110 bpm):
    the base maps the motif to A minor pentatonic -- pads on even
    bars only, bass on beats 0/1.5/3, dry bright plucks at bars 0/6
    (offset +0.5)/12, a soft drum on beat 2 of every bar and shaker
    on beat 3.5 of every bar. No bells, no flute. This layer adds
    the weight the dry furnace cue withholds -- a soft drum on the
    bar line (the base drum is beat 2 only, so the two-beat pulse
    is now complete), a bass fill on beats 1 and 2 on the bar's own
    root (beat 2 doubles the drum beat, beat 1 fills the gap),
    shaker on 0.5/1.5/2.5 (completing the offbeat grid the base
    leaves at 3.5 only), a low pluck echo of the A-minor motif head
    on bars 9 and 16 (bars where the base has no melody), and an A5
    bell toll on bars 4 and 14 (the tonic bell; the base has no
    bells at all). No flute (pluck is the voice), no pad (the pads
    stay sparse by design)."""
    bpm, bars = 110, 20
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        for bt in (1, 2):
            play(tr, "bass", SA_HOA_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5):
            add(tr, shaker(0.06), bar * 4 * b + bt * b,
                -0.3 if bar % 2 else 0.3, 0.05)
        if bar in (4, 14):
            play(tr, "bell", A5, bar * 4 * b, 3 * b, 0.12, pan=0.2)
    for bar in (9, 16):
        melody(tr, "pluck", SA_HOA_HEAD_LOW, bpm, bar, 0.5, pan=-0.2,
               bright=1.4)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "sa_hoa_layer_intensity")
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
    order = ["MUSIC/ben_mua_layer_intensity",
             "MUSIC/lam_trieu_layer_intensity",
             "MUSIC/sa_hoa_layer_intensity"]
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": 0, "outro": 0, "stems": 0,
              "layers": len(cues), "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD6_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 6 - phase layers "
                      "(ben_mua intensity, lam_trieu intensity, "
                      "sa_hoa intensity; Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: phase layers "
                      "authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md6.py (synthesis engine "
                      "and checkpoint-26 arrangements reused from "
                      "build_composed_music.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These "
                      f"{counts['total']} files are NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, "
                      "checkpoint-30, MD1, MD2, MD3, MD4 and MD5 "
                      "packs, which keep their own provenance and "
                      "are untouched.",
        "counts": counts,
        "cues": cues,
        "notes": [
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Each MD6 layer adds only what its base and the earlier "
            "layers do not already do: ben_mua intensity adds the "
            "pulse the pier theme withholds (bar-line drum, bass "
            "fill, offbeat shaker, motif echo on melody-free bars, "
            "E5 bell on the hanging note); lam_trieu intensity "
            "completes the leaf-tick shaker grid the base leaves "
            "half-empty and adds the tonic G5 bell the base never "
            "tolls; sa_hoa intensity completes the two-beat drum "
            "pulse and the offbeat shaker grid and adds the tonic "
            "A5 bell the base never tolls.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD6 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/layers/ and do NOT "
            "replace the ported PackV1 files, their cue bindings, or "
            "the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5 cues.",
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
          f"{pack['counts']['total']} MD6 cues", flush=True)
    return pack


# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP6, an md6 block records what this checkpoint delivered,
    openForMdCp7 lists what stays open. openForMdCp2, openForMdCp3,
    openForMdCp4, openForMdCp5 and openForMdCp6 are KEPT so the
    MD1/MD2/MD3/MD4/MD5 validators (which assert they are non-empty)
    still pass; slots and transitions are untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 6"
    cov["md6"] = {
        "pack": "MUSIC_SCORE_MD6_pack_v1",
        "layers": 3,
        "detail": ("Additive phase layers MUSIC/"
                   "ben_mua_layer_intensity, "
                   "MUSIC/lam_trieu_layer_intensity and "
                   "MUSIC/sa_hoa_layer_intensity."),
    }
    cov["openForMdCp7"] = [
        "Ear audition of all MD1/MD2/MD3/MD4/MD5/MD6 cues + loop "
        "seams (NOT_AUDITIONED).",
        "More phase-layer candidates (e.g. Thang Long / Tran Son / "
        "Bach Uyen / rift finale / quiet discovery intensity "
        "layers).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 6, "
          f"md6 recorded, openForMdCp7 listed", flush=True)
    return cov


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
        ben = cp26_by_key["MUSIC/ben_mua"]
        entry = render_layer(
            "ben_mua_layer_intensity",
            "MUSIC/ben_mua_layer_intensity",
            "Bến Mưa · Lớp tăng cường", "MUSIC/ben_mua",
            ROOT / ben["master"]["path"],
            ben["master"]["durationSeconds"], 72, 17,
            layer_ben_mua_intensity,
            "Additive intensity layer over ben_mua (17 bars @ 72 "
            "bpm): soft drum on the bar line, bass fill on beats 1 "
            "and 3 on the bar's own root, shaker on the offbeats "
            "(rain patter), low pluck echo of the motif head on bars "
            "8 and 15 (bars where the base has no melody), and an E5 "
            "bell toll on bars 5 and 11 (E is the cue's hanging "
            "note). The base has no drums, no shaker, a bass line on "
            "beats 0 and 2 only, and a single D5 bell on the final "
            "bar; this layer adds the pulse the pier theme "
            "withholds. No flute, no drops, no pad. -25 LUFS "
            "target; combined base+layer loudness measured from "
            "real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key)

        lam = cp26_by_key["MUSIC/lam_trieu"]
        entry = render_layer(
            "lam_trieu_layer_intensity",
            "MUSIC/lam_trieu_layer_intensity",
            "Lâm Triều · Lớp tăng cường", "MUSIC/lam_trieu",
            ROOT / lam["master"]["path"],
            lam["master"]["durationSeconds"], 90, 20,
            layer_lam_trieu_intensity,
            "Additive intensity layer over lam_trieu (20 bars @ 90 "
            "bpm): soft drum on the bar line, bass fill on beats 1 "
            "and 3 on the bar's own root, shaker on the ODD bars at "
            "1.5/3.5 (completing the leaf-tick grid the base leaves "
            "on even bars only), low pluck echo of the motif head "
            "transposed to G on bars 6 and 12 (bars where the base "
            "has no melody), and a G5 bell toll on bars 10 and 18 "
            "(the tonic bell; the base has no bells at all). The "
            "base has no drums, a bass line on beats 0 and 2 only, "
            "and leaf-tick shaker on even bars only; this layer "
            "adds the forest pulse. No flute. -25 LUFS target; "
            "combined base+layer loudness measured from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key)

        sa = cp26_by_key["MUSIC/sa_hoa"]
        entry = render_layer(
            "sa_hoa_layer_intensity",
            "MUSIC/sa_hoa_layer_intensity",
            "Sa Hỏa · Lớp tăng cường", "MUSIC/sa_hoa",
            ROOT / sa["master"]["path"],
            sa["master"]["durationSeconds"], 110, 20,
            layer_sa_hoa_intensity,
            "Additive intensity layer over sa_hoa (20 bars @ 110 "
            "bpm): soft drum on the bar line (the base drum is beat "
            "2 only, so the two-beat pulse is now complete), bass "
            "fill on beats 1 and 2 on the bar's own root, shaker on "
            "0.5/1.5/2.5 (completing the offbeat grid the base "
            "leaves at 3.5 only), low pluck echo of the A-minor "
            "motif head on bars 9 and 16 (bars where the base has "
            "no melody), and an A5 bell toll on bars 4 and 14 (the "
            "tonic bell; the base has no bells at all). The base "
            "has pads on even bars only, a bass line on beats "
            "0/1.5/3, and dry bright plucks; this layer adds the "
            "weight the dry furnace cue withholds. No flute, no pad. "
            "-25 LUFS target; combined base+layer loudness measured "
            "from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key)

    save_pack(by_key)
    update_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
