#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 5: more phase layers.

Work Order 37 module M-D, following checkpoint 4 (MD4: boss phase 4,
swamp intensity, dungeon intensity). The coverage matrix
(MUSIC_SCORE_MD_COVERAGE_v1.json) lists this checkpoint's work as
the second item of openForMdCp5:

  * boss phase 5 -- the final escalation over boss_mang_cot
    (checkpoint-26 cue, 10 bars @ 66 bpm, Dm);
  * hub intensity -- the pulse the hub base withholds (MD1 cue,
    16 bars @ 80 bpm, D major, no drums by design);
  * rain intensity -- the weight the rain base withholds (MD1 cue,
    16 bars @ 66 bpm, D major, no drums by design, low-passed at
    1200 Hz so the rain ambience can sit on top).

All three are additive loops at the parent cue's tempo/bars
(-25 LUFS target, same as the MD2/MD3/MD4 layers): they play over
the base cue, they do not replace it. Combined base+layer
loudness/true-peak is measured from real bytes and recorded per
layer; the validator re-checks it from real bytes.

Layer design -- each layer adds only what its base and the earlier
layers do NOT already do, so stacking stays musical:

  * boss phase 5: the base heartbeat is beats 0/1.5; phase 2 fills
    beats 1/2/3; phase 3 fills all four beats; phase 4 fills beats
    AND offbeats. Phase 5 therefore completes the 16th-note drum
    grid (low ticks on the "e"/"a" subdivisions), drives the bass
    in 16ths alternating D1/D2 (phases 2/3 drive 8th-note D1,
    phase 4 drives 8th-note D1/D2), tolls the HIGH D6 bell every
    bar (phase 4 tolls it every 2 bars), and states the minor-head
    fragment in FLUTE at bars 0 and 8 -- the boss theme lifted to
    a scream register. The flute is a deliberate break of the
    "no flute" layer convention: the boss base has no flute at
    all, and no earlier layer uses it, so the voice is new, not
    a duplication. Bar 0 doubles phase 3's pluck fragment in the
    new voice; bar 8 answers the base's own foreign FS5 bell and
    variant fragment. No pad.
  * hub intensity: the base has no drums, a bass line on beats 0
    and 2 only, bells on every bar line, and flute statements at
    bars 0/8/14 with a low pluck answer at bar 4 and the tail at
    bars 10-11. The layer adds the festival pulse the home base
    withholds -- soft drums on beats 0 and 2, a bass fill on
    beats 1 and 3 on the bar's own root, shaker on the offbeats,
    and a low pluck echo of the motif head on bars 2 and 12
    (bars where the base has no melody). No bells (the base
    already tolls every bar), no flute (the base flute at 0/8/14
    stays the voice).
  * rain intensity: the base has no drums, a bass line on beat 0
    only, sparse flute fragments (head bar 0, second half bar 8),
    bells at bars 4/12, and a low-pass veil at 1200 Hz. The layer
    adds the weight of heavier rain -- a soft drum on the bar line,
    a bass fill on beat 2 on the bar's own root, shaker on the
    offbeats (rain patter), a low pluck echo of the motif head on
    bars 2 and 10, and an E5 bell toll on bars 6 and 14 (E is the
    cue's hanging note). The layer is low-passed at the same
    1200 Hz as the base so it sits inside the same veil. No flute
    (the base flute stays the voice).

Single-engine rule (from checkpoint 2, still kept): the builders
live in build_composed_music.py itself, so this tool loads THAT file
once as cm and uses it for everything. Never load a second copy.

Rules kept from checkpoint 26 / MD1 / MD2 / MD3 / MD4: no external
samples, no ported bytes, no voices. The 541 ported PackV1 files and
the checkpoint-26/30/MD1/MD2/MD3/MD4 packs are untouched and are NOT
counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD5_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md5 block + openForMdCp6; openForMdCp2,
    openForMdCp3, openForMdCp4 and openForMdCp5 kept so the
    MD1/MD2/MD3/MD4 validators still pass)
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
            / "MUSIC_SCORE_MD5_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
MD1_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md5"
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
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; the full flute tail stays "
              "reserved for the resolve stinger and rift_finale")
RENDERING = ("procedural synthesis (additive pluck/flute/bell/pad/bass "
             "+ noise percussion), authored in "
             "build_composed_score_md5.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the checkpoint-26 / MD1 "
             "arrangements (build_composed_music.py / "
             "build_composed_score_md1.py); no external samples")

# D F A, the minor head the boss and dungeon pieces state in low
# pluck (MD3 FRAG_MINOR, reused here).
FRAG_MINOR = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]
# The same fragment an octave up, for the boss final-phase flute.
FRAG_MINOR_HI = [(0, D5, 1), (1, 77, 1), (2, A5, 1.5)]
# The motif head an octave down, for the hub/rain low-pluck echoes.
MOTIF_HEAD_LOW = [(be, m - 12, ln) for be, m, ln in MOTIF_HEAD]
# The hub base's bass root progression (piece_hub, MD1).
HUB_ROOTS = [38, 43, 38, 35, 40, 43, 38, 33,
             38, 43, 38, 35, 40, 33, 38, 38]
# The rain base's bass root progression (piece_rain, MD1).
RAIN_ROOTS = [38, 38, 35, 38, 43, 38, 35, 43,
              38, 38, 35, 40, 43, 33, 38, 38]


def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied. Copied from the MD3/MD4 builders (same
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
    """The checkpoint-26 loop construction (MD3/MD4 copy): room, tail
    wrap 1.5 s, end landing 0.25 s. lp_hz low-passes first when the
    parent cue is itself low-passed (rain: 1200 Hz)."""
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
def layer_boss_phase5():
    """Additive phase-5 layer over boss_mang_cot (10 bars @ 66 bpm):
    the final escalation. 16th-note drum ticks on the "e"/"a"
    subdivisions (the grid phases 2/3/4 leave free), 16th-note bass
    alternating D1/D2 (phases 2/3 drive 8th-note D1, phase 4 drives
    8th-note D1/D2), a HIGH D6 bell toll every bar (phase 4 tolls it
    every 2 bars), and the minor-head fragment in FLUTE on bars 0
    and 8 (the boss theme lifted to a scream register -- the first
    flute in any boss layer; the base has no flute at all, so the
    voice is new. Bar 0 doubles phase 3's pluck fragment in the new
    voice; bar 8 answers the base's own foreign FS5 bell and variant
    fragment). No pad."""
    bpm, bars = 66, 10
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0.25, 0.75, 1.25, 1.75, 2.25, 2.75, 3.25, 3.75):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.07)
        for i, bt in enumerate((0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 1.75,
                                2, 2.25, 2.5, 2.75, 3, 3.25, 3.5, 3.75)):
            note = 26 if i % 2 == 0 else 38
            play(tr, "bass", note, bar * 4 * b + bt * b, 0.45 * b, 0.45)
        play(tr, "bell", D6, bar * 4 * b, 2 * b, 0.14, pan=0.3)
    for bar in (0, 8):
        melody(tr, "flute", FRAG_MINOR_HI, bpm, bar, 0.5, pan=0.2)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "boss_mang_cot_layer_phase5")
    return tr, raw_jump


def layer_hub_intensity():
    """Additive intensity layer over hub_lac_chau (16 bars @ 80 bpm):
    the base has no drums, a bass line on beats 0 and 2 only, bells
    on every bar line, and flute at bars 0/8/14 with a low pluck
    answer at bar 4 and the tail at bars 10-11. This layer adds the
    festival pulse the home base withholds -- soft drums on beats 0
    and 2, a bass fill on beats 1 and 3 on the bar's own root, shaker
    on the offbeats, and a low pluck echo of the motif head on bars
    2 and 12 (bars where the base has no melody). No bells (the base
    already tolls every bar), no flute (the base flute stays the
    voice)."""
    bpm, bars = 80, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        for bt in (0, 2):
            add(tr, drum(), bar * 4 * b + bt * b, 0.0, 0.25)
        for bt in (1, 3):
            play(tr, "bass", HUB_ROOTS[bar], bar * 4 * b + bt * b,
                 1.6 * b, 0.4)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.05)
    for bar in (2, 12):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "hub_layer_intensity")
    return tr, raw_jump


def layer_rain_intensity():
    """Additive intensity layer over rain_veil (16 bars @ 66 bpm):
    the base has no drums, a bass line on beat 0 only, sparse flute
    fragments (head bar 0, second half bar 8), bells at bars 4/12,
    and a low-pass veil at 1200 Hz. This layer adds the weight of
    heavier rain -- a soft drum on the bar line, a bass fill on beat
    2 on the bar's own root, shaker on the offbeats (rain patter), a
    low pluck echo of the motif head on bars 2 and 10, and an E5
    bell toll on bars 6 and 14 (E is the cue's hanging note). The
    layer is low-passed at the same 1200 Hz as the base so it sits
    inside the same veil. No flute (the base flute stays the
    voice)."""
    bpm, bars = 66, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        play(tr, "bass", RAIN_ROOTS[bar], bar * 4 * b + 2 * b,
             1.6 * b, 0.35)
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.04)
        if bar in (6, 14):
            play(tr, "bell", E5, bar * 4 * b, 3 * b, 0.12, pan=0.2)
    for bar in (2, 10):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.35, pan=-0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, 1200.0)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "rain_layer_intensity")
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
    order = ["MUSIC/boss_mang_cot_layer_phase5",
             "MUSIC/hub_layer_intensity",
             "MUSIC/rain_layer_intensity"]
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": 0, "outro": 0, "stems": 0,
              "layers": len(cues), "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD5_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 5 - phase layers "
                      "(boss phase 5, hub intensity, rain intensity; "
                      "Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: phase layers "
                      "authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md5.py (synthesis engine "
                      "and checkpoint-26 / MD1 arrangements reused "
                      "from build_composed_music.py and "
                      "build_composed_score_md1.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These "
                      f"{counts['total']} files are NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, "
                      "checkpoint-30, MD1, MD2, MD3 and MD4 packs, "
                      "which keep their own provenance and are "
                      "untouched.",
        "counts": counts,
        "cues": cues,
        "notes": [
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "Each MD5 layer adds only what its base and the earlier "
            "layers do not already do: boss phase 5 completes the "
            "16th-note drum grid with 16th-note octave bass, a D6 "
            "bell every bar and the minor head in flute (the first "
            "flute in any boss layer -- the base has no flute at "
            "all); hub intensity adds the festival pulse a drumless "
            "home base withholds; rain intensity adds the weight of "
            "heavier rain inside the base's own 1200 Hz veil.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD5 files are delivered in parallel under "
            "ClientGodot/assets/audio/composed/layers/ and do NOT "
            "replace the ported PackV1 files, their cue bindings, or "
            "the checkpoint-26/30/MD1/MD2/MD3/MD4 cues.",
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
          f"{pack['counts']['total']} MD5 cues", flush=True)
    return pack


# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP5, an md5 block records what this checkpoint delivered,
    openForMdCp6 lists what stays open. openForMdCp2, openForMdCp3,
    openForMdCp4 and openForMdCp5 are KEPT so the MD1/MD2/MD3/MD4
    validators (which assert they are non-empty) still pass; slots
    and transitions are untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 5"
    cov["md5"] = {
        "pack": "MUSIC_SCORE_MD5_pack_v1",
        "layers": 3,
        "detail": ("Additive phase layers MUSIC/"
                   "boss_mang_cot_layer_phase5, "
                   "MUSIC/hub_layer_intensity and "
                   "MUSIC/rain_layer_intensity."),
    }
    cov["openForMdCp6"] = [
        "Ear audition of all MD1/MD2/MD3/MD4/MD5 cues + loop seams "
        "(NOT_AUDITIONED).",
        "More phase-layer candidates (e.g. Ben Mua / Sa Hoa / Lam "
        "Trieu intensity layers).",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 5, "
          f"md5 recorded, openForMdCp6 listed", flush=True)
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
            "boss_mang_cot_layer_phase5",
            "MUSIC/boss_mang_cot_layer_phase5",
            "Mãng Cốt · Lớp giai đoạn 5", "MUSIC/boss_mang_cot",
            ROOT / boss["master"]["path"],
            boss["master"]["durationSeconds"], 66, 10,
            layer_boss_phase5,
            "Additive phase-5 layer over boss_mang_cot (10 bars @ "
            "66 bpm): 16th-note drum ticks on the 'e'/'a' "
            "subdivisions (the grid phases 2/3/4 leave free), "
            "16th-note bass alternating D1/D2 (phases 2/3 drive "
            "8th-note D1, phase 4 drives 8th-note D1/D2), high D6 "
            "bell toll every bar (phase 4 tolls it every 2 bars), "
            "and the minor-head fragment in FLUTE on bars 0 and 8 "
            "(the boss theme lifted to a scream register -- the "
            "first flute in any boss layer; the base has no flute "
            "at all, so the voice is new. Bar 0 doubles phase 3's "
            "pluck fragment in the new voice; bar 8 answers the "
            "base's own foreign FS5 bell and variant fragment). No "
            "pad. -25 LUFS target; combined base+layer loudness "
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

        hub = md1_by_key["MUSIC/hub_lac_chau"]
        entry = render_layer(
            "hub_layer_intensity", "MUSIC/hub_layer_intensity",
            "Lạc Châu · Lớp tăng cường", "MUSIC/hub_lac_chau",
            ROOT / hub["master"]["path"],
            hub["master"]["durationSeconds"], 80, 16,
            layer_hub_intensity,
            "Additive intensity layer over hub_lac_chau (16 bars @ "
            "80 bpm): soft drums on beats 0 and 2, bass fill on "
            "beats 1 and 3 on the bar's own root, shaker on the "
            "offbeats, and a low pluck echo of the motif head on "
            "bars 2 and 12 (bars where the base has no melody). The "
            "base has no drums, a bass line on beats 0 and 2 only, "
            "bells on every bar line, and flute at bars 0/8/14; "
            "this layer adds the festival pulse the home base "
            "withholds. No bells, no flute. -25 LUFS target; "
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

        rain = md1_by_key["MUSIC/rain_veil"]
        entry = render_layer(
            "rain_layer_intensity", "MUSIC/rain_layer_intensity",
            "Mưa · Lớp tăng cường", "MUSIC/rain_veil",
            ROOT / rain["master"]["path"],
            rain["master"]["durationSeconds"], 66, 16,
            layer_rain_intensity,
            "Additive intensity layer over rain_veil (16 bars @ 66 "
            "bpm): soft drum on the bar line, bass fill on beat 2 "
            "on the bar's own root, shaker on the offbeats (rain "
            "patter), low pluck echo of the motif head on bars 2 "
            "and 10, and an E5 bell toll on bars 6 and 14 (E is the "
            "cue's hanging note). The base has no drums, a bass "
            "line on beat 0 only, sparse flute fragments and bells "
            "at bars 4/12, and a low-pass veil at 1200 Hz; the "
            "layer is low-passed at the same 1200 Hz so it sits "
            "inside the same veil. No flute. -25 LUFS target; "
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

    save_pack(by_key)
    update_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
