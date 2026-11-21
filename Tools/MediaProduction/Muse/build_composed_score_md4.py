#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 4: more phase layers.

Work Order 37 module M-D, following checkpoint 3 (MD3: intro/outro +
stems + phase layers for the 9 checkpoint-26 cues). The coverage
matrix (MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work
as the second item of openForMdCp4:

  * boss phase 4 -- the final escalation over boss_mang_cot
    (checkpoint-26 cue, 10 bars @ 66 bpm, Dm);
  * swamp intensity -- the pulse the swamp base withholds (MD1 cue,
    16 bars @ 58 bpm, Bm/Em, no drums by design);
  * dungeon intensity -- the drive the dungeon base withholds (MD1
    cue, 12 bars @ 70 bpm, Dm, only a soft bar-line drum by design).

All three are additive loops at the parent cue's tempo/bars
(-25 LUFS target, same as the MD2/MD3 layers): they play over the
base cue, they do not replace it. Combined base+layer
loudness/true-peak is measured from real bytes and recorded per
layer; the validator re-checks it from real bytes.

Layer design -- each layer adds only what its base and the earlier
layers do NOT already do, so stacking stays musical:

  * boss phase 4: phase 2 fills beats 1/2/3 with an 8th-note D1 bass
    pulse and F4 bells every 2 bars; phase 3 fills all four beats
    with a 16th-note D1 bass pulse and F4 bells every bar. Phase 4
    therefore goes double-time (drums on the beats AND the offbeats),
    drives the bass in alternating D1/D2 octaves (8ths), tolls a HIGH
    D6 bell every 2 bars, and doubles the base's own minor-head pluck
    fragment an octave up on bars 2 and 7 (the base states it on
    2/5/7/8; phases 2/3 already cover the other bars, so no free bar
    is left for a new fragment -- octave doubling is the final-phase
    intensification). No pad, no flute.
  * swamp intensity: the base has no drums, a B0 drone, one low bell
    per phrase and a single low pluck figure (bar 6). The layer adds
    soft drums on beats 0 and 2, a quarter-note bass pedal on the
    bar's own root (the base's root progression), an E3 toll every 4
    bars (E is the cue's hanging note), and the base's own (D4, A4)
    pluck figure on bars 3 and 11 (bars where the base has neither
    flute nor pluck). No pad, no flute.
  * dungeon intensity: the base has a soft drum on the bar line only,
    a whole-bar D1 drone, and pluck fragments on bars 1/5/9 (+ a
    variant on bar 7). The layer fills beats 1/2/3 around the bar-line
    drum, adds an 8th-note D1 bass pulse, tolls a cold F4 bell every 2
    bars on the even bars the base leaves free (0/2/6/10; the base's
    bells are D4 bar 4 and F4 bar 8), and states the minor-head pluck
    fragment on bars 3 and 10. No pad, no flute.

Single-engine rule (from checkpoint 2, still kept): the builders
live in build_composed_music.py itself, so this tool loads THAT file
once as cm and uses it for everything. Never load a second copy.

Rules kept from checkpoint 26 / MD1 / MD2 / MD3: no external
samples, no ported bytes, no voices. The 541 ported PackV1 files and
the checkpoint-26/30/MD1/MD2/MD3 packs are untouched and are NOT
counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD4_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md4 block + openForMdCp5; openForMdCp2,
    openForMdCp3 and openForMdCp4 kept so the MD1/MD2/MD3
    validators still pass)
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
            / "MUSIC_SCORE_MD4_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
MD1_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md4"
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
beat_s = cm.beat_s
room = cm.room
tail_wrap = cm.tail_wrap
end_landing = cm.end_landing
write_master_wav = cm.write_master_wav
encode_ogg = cm.encode_ogg
file_entry = cm.file_entry
seam_stats = cm.seam_stats

D4, E4, FS4, A4, B4 = 62, 64, 66, 69, 71
D5, E5, FS5, A5, B5, D6 = 74, 76, 78, 81, 83, 86
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; the full flute tail stays "
              "reserved for the resolve stinger and rift_finale")
RENDERING = ("procedural synthesis (additive pluck/flute/bell/pad/bass "
             "+ noise percussion), authored in "
             "build_composed_score_md4.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the checkpoint-26 / MD1 "
             "arrangements (build_composed_music.py / "
             "build_composed_score_md1.py); no external samples")

# D F A, the minor head the boss and dungeon pieces state in low
# pluck (MD3 FRAG_MINOR, reused here).
FRAG_MINOR = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]
# The same fragment an octave up, for the boss final-phase doubling.
FRAG_MINOR_HI = [(0, D5, 1), (1, 77, 1), (2, A5, 1.5)]
# The swamp base's own low pluck figure (D4, A4), bar 6.
SWAMP_FIG = [(0, D4, 1), (2, A4, 2)]
# The swamp base's bass root progression (piece_swamp, MD1).
SWAMP_ROOTS = [35, 35, 40, 35, 43, 40, 35, 40,
               35, 43, 40, 35, 40, 35, 35, 35]


def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied. Copied from the MD3 builder (same engine,
    same reason: a single pre-multiplied factor differs from the
    sequential multiplications in the last float64 ulp). Returns
    (track, mults, lufs, tp)."""
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
    """The checkpoint-26 loop construction (MD3 copy): room, tail
    wrap 1.5 s, end landing 0.25 s."""
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
def layer_boss_phase4():
    """Additive phase-4 layer over boss_mang_cot (10 bars @ 66 bpm):
    double-time drums (beats AND offbeats), alternating D1/D2 octave
    bass in 8ths, a HIGH D6 bell toll every 2 bars, and the minor-head
    pluck fragment doubled an octave up on bars 2 and 7 (the base's
    own statements; phases 2/3 already cover every other bar). No
    pad, no flute -- those stay in the base cue."""
    bpm, bars = 66, 10
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 1, 2, 3):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.22)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.13)
        for i, bt in enumerate((0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5)):
            note = 26 if i % 2 == 0 else 38
            play(tr, "bass", note, bar * 4 * b + bt * b, 0.8 * b, 0.45)
        if bar % 2 == 0:
            play(tr, "bell", D6, bar * 4 * b, 2 * b, 0.14, pan=0.3)
    for bar in (2, 7):
        melody(tr, "pluck", FRAG_MINOR_HI, bpm, bar, 0.35, pan=-0.15,
               bright=0.6)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "boss_mang_cot_layer_phase4")
    return tr, raw_jump


def layer_swamp_intensity():
    """Additive intensity layer over swamp (16 bars @ 58 bpm): the
    base is drumless by design (Bm/Em pads, B0 drone, one low bell
    per phrase, one low pluck figure at bar 6), so this layer adds
    the pulse the base withholds -- soft drums on beats 0 and 2, a
    quarter-note bass pedal on the bar's own root (the base's root
    progression), an E3 toll every 4 bars (E is the cue's hanging
    note), and the base's own (D4, A4) pluck figure on bars 3 and 11
    (bars where the base has neither flute nor pluck). No flute, no
    pad."""
    bpm, bars = 58, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 2):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.25)
        for bt in (0, 1, 2, 3):
            play(tr, "bass", SWAMP_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        if bar % 4 == 0:
            play(tr, "bell", 52, bar * 4 * b, 3 * b, 0.15, pan=-0.2)
    for bar in (3, 11):
        melody(tr, "pluck", SWAMP_FIG, bpm, bar, 0.4, pan=0.25,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "swamp_layer_intensity")
    return tr, raw_jump


def layer_dungeon_intensity():
    """Additive intensity layer over dungeon (12 bars @ 70 bpm): the
    base has only a soft drum on the bar line, a whole-bar D1 drone
    and pluck fragments on bars 1/5/9 (+ a variant on bar 7), so this
    layer fills beats 1/2/3 around the bar-line drum, adds an
    8th-note D1 bass pulse, tolls a cold F4 bell every 2 bars on the
    even bars the base leaves free (0/2/6/10; the base's bells are D4
    bar 4 and F4 bar 8), and states the minor-head pluck fragment on
    bars 3 and 10. No pad, no flute."""
    bpm, bars = 70, 12
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (1, 2, 3):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.20)
        for bt in (0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5):
            play(tr, "bass", 26, bar * 4 * b + bt * b, 0.8 * b, 0.4)
        if bar % 2 == 0 and bar not in (4, 8):
            play(tr, "bell", 65, bar * 4 * b, 3 * b, 0.15, pan=-0.2)
    for bar in (3, 10):
        melody(tr, "pluck", FRAG_MINOR, bpm, bar, 0.5, pan=-0.15,
               bright=0.4)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "dungeon_layer_intensity")
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
    order = ["MUSIC/boss_mang_cot_layer_phase4",
             "MUSIC/swamp_layer_intensity",
             "MUSIC/dungeon_layer_intensity"]
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": 0, "outro": 0, "stems": 0,
              "layers": len(cues), "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD4_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 4 - phase layers "
                      "(boss phase 4, swamp intensity, dungeon "
                      "intensity; Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: phase layers "
                      "authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md4.py (synthesis engine "
                      "and checkpoint-26 / MD1 arrangements reused "
                      "from build_composed_music.py and "
                      "build_composed_score_md1.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These "
                      f"{counts['total']} files are NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, "
                      "checkpoint-30, MD1, MD2 and MD3 packs, which "
                      "keep their own provenance and are untouched.",
        "counts": counts,
        "cues": cues,
        "notes": [
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Each MD4 layer adds only what its base and the earlier "
            "layers do not already do: boss phase 4 goes double-time "
            "with octave bass and a high D6 bell (phases 2/3 already "
            "fill the beats and the F4 bells); swamp intensity adds "
            "the pulse a drumless base withholds; dungeon intensity "
            "fills beats 1/2/3 around the base's bar-line drum.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD4 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/layers/ and do NOT "
            "replace the ported PackV1 files, their cue bindings, or "
            "the checkpoint-26/30/MD1/MD2/MD3 cues.",
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
          f"{pack['counts']['total']} MD4 cues", flush=True)
    return pack


# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP4, an md4 block records what this checkpoint delivered,
    openForMdCp5 lists what stays open. openForMdCp2, openForMdCp3
    and openForMdCp4 are KEPT so the MD1/MD2/MD3 validators (which
    assert they are non-empty) still pass; slots and transitions are
    untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 4"
    cov["md4"] = {
        "pack": "MUSIC_SCORE_MD4_pack_v1",
        "layers": 3,
        "detail": ("Additive phase layers MUSIC/"
                   "boss_mang_cot_layer_phase4, "
                   "MUSIC/swamp_layer_intensity and "
                   "MUSIC/dungeon_layer_intensity."),
    }
    cov["openForMdCp5"] = [
        "Ear audition of all MD1/MD2/MD3/MD4 cues + loop seams "
        "(NOT_AUDITIONED).",
        "More phase-layer candidates (e.g. hub/rain intensity "
        "layers, boss phase 5).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 4, "
          f"md4 recorded, openForMdCp5 listed", flush=True)
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
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}

    if only is None or "layers" in only:
        boss = cp26_by_key["MUSIC/boss_mang_cot"]
        entry = render_layer(
            "boss_mang_cot_layer_phase4",
            "MUSIC/boss_mang_cot_layer_phase4",
            "Mãng Cốt · Lớp giai đoạn 4", "MUSIC/boss_mang_cot",
            ROOT / boss["master"]["path"],
            boss["master"]["durationSeconds"], 66, 10,
            layer_boss_phase4,
            "Additive phase-4 layer over boss_mang_cot (10 bars @ "
            "66 bpm): double-time drums (beats + offbeats), "
            "alternating D1/D2 octave bass in 8ths, high D6 bell "
            "toll every 2 bars, minor-head pluck fragment doubled "
            "an octave up on bars 2 and 7 (the base's own "
            "statements). Phases 2/3 already fill the beats, the "
            "8th/16th D1 pulse and the F4 bells, so phase 4 adds "
            "the offbeats, the octave bass and the high bell. No "
            "pad, no flute -- those stay in the base cue. -25 LUFS "
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

        swamp = md1_by_key["MUSIC/swamp"]
        entry = render_layer(
            "swamp_layer_intensity", "MUSIC/swamp_layer_intensity",
            "Đầm · Lớp tăng cường", "MUSIC/swamp",
            ROOT / swamp["master"]["path"],
            swamp["master"]["durationSeconds"], 58, 16,
            layer_swamp_intensity,
            "Additive intensity layer over swamp (16 bars @ 58 "
            "bpm): soft drums on beats 0 and 2, quarter-note bass "
            "pedal on the bar's own root (the base's root "
            "progression), E3 toll every 4 bars (E is the cue's "
            "hanging note), and the base's own (D4, A4) pluck "
            "figure on bars 3 and 11. The base is drumless by "
            "design (Bm/Em pads, B0 drone, one low bell per "
            "phrase); this layer adds the pulse the base "
            "withholds. -25 LUFS target; combined base+layer "
            "loudness measured from real bytes.")
        by_key[entry["cueKey"]] = entry
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP; combined "
              f"{entry['combinedWithBase']['integratedLufs']} LUFS / "
              f"{entry['combinedWithBase']['truePeakDbtp']} dBTP",
              flush=True)
        save_pack(by_key)

        dungeon = md1_by_key["MUSIC/dungeon"]
        entry = render_layer(
            "dungeon_layer_intensity", "MUSIC/dungeon_layer_intensity",
            "Hầm · Lớp tăng cường", "MUSIC/dungeon",
            ROOT / dungeon["master"]["path"],
            dungeon["master"]["durationSeconds"], 70, 12,
            layer_dungeon_intensity,
            "Additive intensity layer over dungeon (12 bars @ 70 "
            "bpm): drums on beats 1/2/3 around the base's soft "
            "bar-line drum, 8th-note D1 bass pulse, cold F4 bell "
            "every 2 bars on the even bars the base leaves free "
            "(0/2/6/10; the base's bells are D4 bar 4 and F4 bar "
            "8), and the minor-head pluck fragment on bars 3 and "
            "10. -25 LUFS target; combined base+layer loudness "
            "measured from real bytes.")
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
