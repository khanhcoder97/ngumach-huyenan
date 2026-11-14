#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 8: one more phase layer.

Work Order 37 module M-D, following checkpoint 7 (MD7: thang_long,
tran_son, bach_uyen, rift_finale, quiet_discovery intensity). The
coverage matrix (MUSIC_SCORE_MD_COVERAGE_v1.json) lists this
checkpoint's work as the second item of openForMdCp8 -- the last
intensity layer for a score cue:

  * thanh_lac intensity -- the market pulse the busiest street
    arrangement withholds (MD1 cue, 16 bars @ 96 bpm, D major).

After this checkpoint EVERY composed score cue carries an intensity
layer: all 9 checkpoint-26 music cues (ben_mua, thang_long,
boss_mang_cot, quiet_discovery, lam_trieu, sa_hoa, tran_son,
bach_uyen, rift_finale) and all 7 MD1 cues (hub_lac_chau,
thanh_lac, rain_veil, swamp, dungeon, arena, tragedy) -- through
their MD2/MD3/MD4/MD5/MD6/MD7 layers and this one. No further
intensity layer is pending for a score cue; what stays open is ear
audition (NOT_AUDITIONED) and any further phase layer the director
asks for (e.g. boss phase 6).

The layer is an additive loop at the parent cue's tempo/bars
(-25 LUFS target, same as the MD2/MD3/MD4/MD5/MD6/MD7 layers):
it plays over the base cue, it does not replace it. Combined
base+layer loudness/true-peak is measured from real bytes and
recorded; the validator re-checks it from real bytes.

Layer design -- the layer adds only what its base and the earlier
layers do NOT already do, so stacking stays musical:

  * thanh_lac intensity: the base is the busiest street form --
    pads on every bar, a bell of the chord tonic on every bar
    line, bass on ALL FOUR beats, pluck arpeggios on every bar
    plus a second off-beat pluck voice an octave down, flute
    motif at bars 0/8, a low-pluck tail at bar 12, and shaker on
    every offbeat. No drums at all. The layer adds the one thing
    the market withholds -- a soft drum on the bar line and on
    beat 2 (the two-beat market pulse) -- plus a low pluck echo
    of the motif head on bars 4 and 13 (bars where the base has
    no melody; the arpeggio is texture, not melody). No bells
    (the base tolls every bar), no shaker (the base already owns
    the full offbeat grid), no bass fill (the bass already plays
    all four beats), no pad, no flute.

Single-engine rule (from checkpoint 2, still kept): the builders
live in build_composed_music.py itself, so this tool loads THAT file
once as cm and uses it for everything. Never load a second copy.

Rules kept from checkpoint 26 / MD1 / MD2 / MD3 / MD4 / MD5 / MD6 /
MD7: no external samples, no ported bytes, no voices. The 541
ported PackV1 files and the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5/
MD6/MD7 packs are untouched and are NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/layers/<stem>.wav
    (masters, 48k/24b)
  ClientGodot/assets/audio/composed/layers/*.ogg
    (runtime, Vorbis q5)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD8_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json
    (updated in place: md8 block + openForMdCp9; openForMdCp2,
    openForMdCp3, openForMdCp4, openForMdCp5, openForMdCp6,
    openForMdCp7 and openForMdCp8 kept so the
    MD1/MD2/MD3/MD4/MD5/MD6/MD7 validators still pass)
"""
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
            / "MUSIC_SCORE_MD8_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
MD1_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
TMP = Path.home() / "workspace" / "tmp" / "composed_score_md8"
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
             "build_composed_score_md8.py on the checkpoint-26 engine "
             "(build_composed_music.py) and the MD1 arrangement "
             "(build_composed_score_md1.py); no external "
             "samples")

# The motif head an octave down, for the low-pluck echoes.
MOTIF_HEAD_LOW = [(be, m - 12, ln) for be, m, ln in MOTIF_HEAD]
# The thanh_lac base's bass root progression (piece_thanh_lac,
# MD1). Not used by the thanh_lac layer (its bass already plays
# all four beats); recorded so the progression stays checkable.
THANH_LAC_ROOTS = [38, 43, 38, 33, 35, 43, 38, 33,
                   38, 43, 35, 33, 38, 43, 33, 38]


def stage_like_gain_stage(track, target_lufs, tp_ceiling, tag):
    """cm.gain_stage's exact operations (same loop, same sequential
    in-place multiplications), but also returns the list of
    multipliers applied. Copied from the MD3/MD4/MD5/MD6/MD7
    builders (same engine, same reason: a single pre-multiplied
    factor differs from the sequential multiplications in the last
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
    """The checkpoint-26 loop construction (MD3/MD4/MD5/MD6/MD7
    copy): room, tail wrap 1.5 s, end landing 0.25 s. lp_hz
    low-passes first when the parent cue is itself low-passed;
    thanh_lac is not low-passed."""
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


# --------------------------------------------------------- phase layer
def layer_thanh_lac_intensity():
    """Additive intensity layer over thanh_lac (16 bars @ 96 bpm):
    the base is the busiest street form -- pads on every bar, a
    bell of the chord tonic on every bar line, bass on ALL FOUR
    beats, pluck arpeggios on every bar plus a second off-beat
    pluck voice an octave down, flute motif at bars 0/8, a
    low-pluck tail at bar 12, and shaker on every offbeat. No
    drums at all. This layer adds the one thing the market
    withholds -- a soft drum on the bar line and on beat 2 (the
    two-beat market pulse) -- plus a low pluck echo of the motif
    head on bars 4 and 13 (bars where the base has no melody; the
    arpeggio is texture, not melody). No bells (the base tolls
    every bar), no shaker (the base already owns the full offbeat
    grid), no bass fill (the bass already plays all four beats),
    no pad, no flute."""
    bpm, bars = 96, 16
    tr = new_track(bars * 240.0 / bpm)
    b = beat_s(bpm)
    for bar in range(bars):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        add(tr, drum(), bar * 4 * b + 2 * b, 0.0, 0.12)
    for bar in (4, 13):
        melody(tr, "pluck", MOTIF_HEAD_LOW, bpm, bar, 0.5, pan=0.2,
               bright=0.5)
    tr, raw_jump = loop_process(tr, None)
    tr, _mults, lufs, tp = stage_like_gain_stage(
        tr, -25.0, -5.0, "thanh_lac_layer_intensity")
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
    order = ["MUSIC/thanh_lac_layer_intensity"]
    cues = [by_key[k] for k in order if k in by_key]
    counts = {"intro": 0, "outro": 0, "stems": 0,
              "layers": len(cues), "total": len(cues)}
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD8_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 8 - phase layer "
                      "(thanh_lac intensity; Work Order 37 "
                      "module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: phase layer "
                      "authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md8.py (synthesis engine "
                      "reused from build_composed_music.py, MD1 "
                      "arrangement from build_composed_score_md1.py) "
                      "and rendered by procedural synthesis. No "
                      "external samples, no ported bytes. This "
                      f"{counts['total']} file is NEW audio, "
                      "counted separately from the 541 ported PackV1 "
                      "files and from the checkpoint-26, "
                      "checkpoint-30, MD1, MD2, MD3, MD4, MD5, MD6 "
                      "and MD7 packs, which keep their own provenance "
                      "and are untouched.",
        "counts": counts,
        "cues": cues,
        "notes": [
            "Phase layers are ADDITIVE loops at the parent cue's "
            "tempo/bars (-25 LUFS target): they play over the base "
            "cue, they do not replace it. Combined base+layer "
            "loudness/true-peak is measured from real bytes and "
            "recorded per layer.",
            "The MD8 layer adds only what its base and the earlier "
            "layers do not already do: thanh_lac intensity adds "
            "the two-beat market drum pulse the busiest street "
            "arrangement withholds (no drums at all in the base) "
            "plus a low pluck echo on melody-free bars. After MD8 "
            "every composed score cue carries an intensity layer; "
            "no further intensity layer is pending for a score cue.",
            "Adoption is a presentation-adapter decision (Codex): "
            "the MD8 file is delivered in parallel under "
            "ClientGodot/assets/audio/composed/layers/ and does NOT "
            "replace the ported PackV1 files, their cue bindings, or "
            "the checkpoint-26/30/MD1/MD2/MD3/MD4/MD5/MD6/MD7 cues.",
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
          f"{pack['counts']['total']} MD8 cue", flush=True)
    return pack


# ------------------------------------------------------------ coverage
def update_coverage():
    """Update the M-D coverage matrix in place: checkpoint label moves
    to MD CP8, an md8 block records what this checkpoint delivered,
    openForMdCp9 lists what stays open. openForMdCp2, openForMdCp3,
    openForMdCp4, openForMdCp5, openForMdCp6, openForMdCp7 and
    openForMdCp8 are KEPT so the
    MD1/MD2/MD3/MD4/MD5/MD6/MD7 validators (which assert they are
    non-empty) still pass; slots and transitions are untouched."""
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    cov["checkpoint"] = "MEDIA-02 WO37 M-D checkpoint 8"
    cov["md8"] = {
        "pack": "MUSIC_SCORE_MD8_pack_v1",
        "layers": 1,
        "detail": ("Additive phase layer MUSIC/"
                   "thanh_lac_layer_intensity -- the last score cue "
                   "without an intensity layer; after MD8 every "
                   "composed score cue carries one."),
    }
    cov["openForMdCp9"] = [
        "Ear audition of all MD1/MD2/MD3/MD4/MD5/MD6/MD7/MD8 cues + "
        "loop seams (NOT_AUDITIONED).",
        "More phase-layer candidates if the director asks for them "
        "(e.g. boss phase 6 or a second intensity layer for a cue "
        "the director wants louder) -- no intensity layer is pending "
        "for a score cue after MD8.",
    ]
    COVERAGE.write_text(json.dumps(cov, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: checkpoint 8, "
          f"md8 recorded, openForMdCp9 listed", flush=True)
    return cov


def _render_one(by_key, md1_by_key, stem, cue_key, name_vi, parent_key,
                bpm, bars, layer_fn, structure):
    parent = md1_by_key[parent_key]
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

    md1_pack = json.loads(MD1_PACK.read_text(encoding="utf-8"))
    md1_by_key = {c["cueKey"]: c for c in md1_pack["cues"]}

    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}

    if only is None or "layers" in only:
        _render_one(
            by_key, md1_by_key,
            "thanh_lac_layer_intensity",
            "MUSIC/thanh_lac_layer_intensity",
            "Thanh Lạc · Lớp tăng cường", "MUSIC/thanh_lac",
            96, 16, layer_thanh_lac_intensity,
            "Additive intensity layer over thanh_lac (16 bars @ 96 "
            "bpm): soft drum on the bar line and on beat 2 (the "
            "two-beat market pulse; the base has no drums at all) "
            "and a low pluck echo of the motif head on bars 4 and "
            "13 (bars where the base has no melody; the arpeggio "
            "is texture, not melody). The base has pads on every "
            "bar, a bell of the chord tonic on every bar line, "
            "bass on all four beats, pluck arpeggios on every bar "
            "plus a second off-beat pluck voice an octave down, "
            "flute motif at bars 0/8, a low-pluck tail at bar 12 "
            "and shaker on every offbeat; this layer adds the "
            "pulse the market arrangement withholds. No bells, no "
            "shaker, no bass fill, no pad, no flute. -25 LUFS "
            "target; combined base+layer loudness measured from "
            "real bytes.")

    save_pack(by_key)
    update_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
