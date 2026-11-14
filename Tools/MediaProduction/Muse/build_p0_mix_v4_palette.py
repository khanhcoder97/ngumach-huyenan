#!/usr/bin/env python3
"""MEDIA-02 WO37 M-F CP2: P0 DRAFT mix v4 -- CIN_002 palette re-mix ONLY.

Clone of build_p0_mix_v3.py (MEDIA-02 checkpoint 31) restricted to
the one P0 scene whose VO changes under the palette decision:
  (a) CIN_002's VO take source is the M-F CP1 palette pickup
      VO_CIN002_S02_TAVANKHANH_palette_v1.wav -- Ta Van Khanh voiced by Polished Coin (fictional system voice)
      (avocado_v2:conor), replacing the checkpoint-04 draft take
      voiced by avocado_v2:MAI_03 (the shared draft voice of every
      male speaker);
  (b) CIN_001 and CIN_004 are NOT rebuilt: both are Ly An lines
      (on-screen S05 and off-screen S02), Ly An keeps her Aria
      voice and has no pickup, so their v3 mixes stand unchanged;
  (c) outputs land in Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/
      (CIN_002_mix_draft_v4.wav + P0_MIX_V4_manifest_v1.json) and
      no 72 s review reel is built (it would mix v3 and v4 scenes);
  (d) manifest prose records the palette decision: the project
      owner delegated the voice choice to Muse (main chat
      2026-11-12 18:30 JST) and Muse's decision is to apply the
      M-F CP1 palette (side B of the WO39 M39-B CP1 level-matched
      A/B review) to every role with a distinct pickup.
The mixing code is byte-for-byte the v3 code for CIN_002: same
fully composed stems, same gain targets, same sidechain ducking
(threshold 0.03, ratio 4, attack 15 ms, release 350 ms), same peak
guard (-1.0 dBTP); VO at unity.

The palette take measures 3.312 s:
placed at the 7.0 s window start it runs to 10.312 s and FITS the
7.0-11.0 s window with 0.688 s of slack.

DRAFT_NOT_FINAL, NOT_AUDITIONED. The v4 mix lives in Art_Source
only: the runtime still embeds the v3-based runtime mixes and the
runtime audio count is unchanged (783); adoption is Codex's
decision at review.
"""
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 48000
MUSIC_TARGET_LUFS = -30.0
AMB_PRIMARY_LUFS = -36.0
AMB_SECONDARY_LUFS = -38.0
PEAK_CEILING_DBTP = -1.0
DUCK = {"threshold": 0.03, "ratio": 4, "attackMs": 15, "releaseMs": 350}

# Measured integrated LUFS on the RUNTIME bytes actually mixed.
# Music + stingers: composed runtime OGGs, re-measured 2026-11-06 with
# ffmpeg loudnorm (match the checkpoint-26 pack table to 0.01 LUFS).
# Ambience: composed runtime OGGs, checkpoint-30 pack values,
# re-measured this run (match the pack table to 0.01 LUFS).
MEASURED_LUFS = {
    "MUSIC/quiet_discovery": -21.72,
    "MUSIC/boss_mang_cot": -21.98,
    "AMBIENCE/rain_light": -27.80,
    "AMBIENCE/river_shore": -29.69,
    "AMBIENCE/underwater": -33.11,
    "SFX/CINEMA/reveal": -24.96,
    "SFX/CINEMA/tension": -24.93,
}
PROVENANCE = {
    "MUSIC/quiet_discovery": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    "MUSIC/boss_mang_cot": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    "SFX/CINEMA/reveal": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    "SFX/CINEMA/tension": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    "AMBIENCE/rain_light": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
    "AMBIENCE/river_shore": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
    "AMBIENCE/underwater": "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
}
STEM_FILES = {
    "MUSIC/quiet_discovery": "ClientGodot/assets/audio/composed/music/quiet_discovery.ogg",
    "MUSIC/boss_mang_cot": "ClientGodot/assets/audio/composed/music/boss_mang_cot.ogg",
    "AMBIENCE/rain_light": "ClientGodot/assets/audio/composed/ambience/rain_light.ogg",
    "AMBIENCE/river_shore": "ClientGodot/assets/audio/composed/ambience/river_shore.ogg",
    "AMBIENCE/underwater": "ClientGodot/assets/audio/composed/ambience/underwater.ogg",
    "SFX/CINEMA/reveal": "ClientGodot/assets/audio/composed/cinema/reveal.ogg",
    "SFX/CINEMA/tension": "ClientGodot/assets/audio/composed/cinema/tension.ogg",
}
VO_TAKES = {  # M-F CP2: ONLY CIN_002 is rebuilt, from its palette
    # pickup in PALETTE_PICKUPS_v1 (see vo_dir below). CIN_001 /
    # CIN_004 are Ly An lines and are not part of this build.
    "CIN_002": ("VO_CIN002_S02_TAVANKHANH_palette_v1.wav", 7.0),
}
SCENES = {
    "CIN_001": {
        "seconds": 36.0,
        "music": {"cue": "MUSIC/quiet_discovery", "at": 6.0, "len": 24.0,
                  "fadeIn": 1.0, "fadeOut": 1.5, "ducked": True},
        "ambience": [
            {"cue": "AMBIENCE/river_shore", "at": 0.0, "len": 36.0,
             "target": AMB_PRIMARY_LUFS, "ducked": False},
            {"cue": "AMBIENCE/rain_light", "at": 0.0, "len": 6.0,
             "target": AMB_SECONDARY_LUFS, "ducked": False,
             "fadeOut": 1.0},
        ],
        "stinger": {"cue": "SFX/CINEMA/reveal", "at": 30.0},
    },
    "CIN_002": {
        "seconds": 18.0,
        "music": None,
        "ambience": [
            {"cue": "AMBIENCE/river_shore", "at": 0.0, "len": 18.0,
             "target": AMB_PRIMARY_LUFS, "ducked": True},
            {"cue": "AMBIENCE/underwater", "at": 0.0, "len": 6.0,
             "target": AMB_SECONDARY_LUFS, "ducked": False,
             "fadeOut": 1.0},
        ],
        "stinger": {"cue": "SFX/CINEMA/tension", "at": 6.0},
    },
    "CIN_004": {
        "seconds": 18.0,
        "music": {"cue": "MUSIC/boss_mang_cot", "at": 0.0, "len": 12.0,
                  "fadeIn": 0.5, "fadeOut": 1.5, "ducked": True},
        "ambience": [
            {"cue": "AMBIENCE/river_shore", "at": 0.0, "len": 18.0,
             "target": AMB_PRIMARY_LUFS, "ducked": False},
        ],
        "stinger": {"cue": "SFX/CINEMA/reveal", "at": 6.0},
    },
}
# M-F CP2: build ONLY CIN_002 (the only P0 scene whose
# VO changes). CIN_001/CIN_004 keep their v3 mixes.
SCENES = {"CIN_002": SCENES["CIN_002"]}
LOOP_SECONDS = 16.0
XFADE_SECONDS = 1.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)
    return r


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error",
             "-show_entries", "stream=codec_name,sample_rate,channels",
             "-show_entries", "format=duration,size",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def loudnorm(path: Path) -> dict:
    r = run(["ffmpeg", "-i", str(path), "-vn", "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    tail = r.stderr.strip().splitlines()
    start = next(i for i, line in enumerate(tail) if line.strip() == "{")
    end = next(i for i, line in enumerate(tail) if line.strip() == "}")
    return json.loads("\n".join(tail[start:end + 1]))


def segment_rms_db(path: Path, start: float, dur: float) -> float:
    """RMS level (dBFS) of a WAV segment, computed from the samples.

    (This ffmpeg build's astats does not print a usable summary, so
    the measurement is done directly on the decoded samples.)
    """
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        w.setpos(int(start * sr))
        frames = w.readframes(int(dur * sr))
    x = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
    if x.size == 0:
        print(f"EMPTY SEGMENT {path} @{start}", file=sys.stderr)
        sys.exit(1)
    rms = float(np.sqrt(np.mean(x * x)))
    return 20.0 * math.log10(rms) if rms > 0 else -120.0


def fmt_t(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".") if "." in f"{x:.3f}" else str(x)


def build_bed(src: Path, length: float, gain_db: float, work: Path,
              name: str, fade_out: float = 0.0):
    """Loop a 16 s ambience stem to `length` with 1 s crossfade joins.

    Returns (wav_path, joins) where joins lists the crossfade centre
    times used for loop QA.
    """
    out = work / f"{name}.wav"
    step = LOOP_SECONDS - XFADE_SECONDS
    n = 1
    while LOOP_SECONDS + (n - 1) * step < length:
        n += 1
    joins = [LOOP_SECONDS - XFADE_SECONDS / 2 + i * step
             for i in range(n - 1)]
    if n == 1:
        filt = (f"[0:a]atrim=0:{fmt_t(length)},"
                f"volume={gain_db:.2f}dB")
        if fade_out:
            filt += f",afade=t=out:st={fmt_t(length - fade_out)}:d={fmt_t(fade_out)}"
        filt += "[a]"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
             "-filter_complex", filt, "-map", "[a]",
             "-ar", str(SR), "-ac", "2", str(out)])
    else:
        inputs = []
        for _ in range(n):
            inputs += ["-i", str(src)]
        # Chain: s0 = input0; s_i = acrossfade(s_{i-1}, input_i)
        chain = []
        prev = "[0:a]"
        for i in range(1, n):
            lbl = f"[s{i}]"
            chain.append(f"{prev}[{i}:a]acrossfade=d={int(XFADE_SECONDS)}{lbl}")
            prev = lbl
        filt = ";".join(chain) + (
            f";{prev}atrim=0:{fmt_t(length)},volume={gain_db:.2f}dB")
        if fade_out:
            filt += f",afade=t=out:st={fmt_t(length - fade_out)}:d={fmt_t(fade_out)}"
        filt += "[a]"
        run(["ffmpeg", "-y", "-v", "error", *inputs,
             "-filter_complex", filt, "-map", "[a]",
             "-ar", str(SR), "-ac", "2", str(out)])
    return out, joins


def loop_qa(wav_path: Path, joins) -> list:
    """Max sample jump near each join vs the bed's own p99.9 jump."""
    with wave.open(str(wav_path), "rb") as w:
        frames = w.readframes(w.getnframes())
        ch = w.getnchannels()
    x = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
    x = x.reshape(-1, ch).mean(axis=1)
    d = np.abs(np.diff(x))
    p999 = float(np.percentile(d, 99.9)) if len(d) else 0.0
    results = []
    for t in joins:
        c = int(t * SR)
        lo = max(0, c - int(0.05 * SR))
        hi = min(len(d), c + int(0.05 * SR))
        jump = float(d[lo:hi].max()) if hi > lo else 0.0
        results.append({
            "atSeconds": round(t, 3),
            "maxJump": round(jump, 5),
            "bedP999Jump": round(p999, 5),
            "ratioToP999": (round(jump / p999, 3) if p999 > 0 else None),
        })
    return results


def place(src: Path, at: float, total: float, work: Path, name: str,
          gain_db: float = 0.0, seg_len: float = None,
          fade_in: float = 0.0, fade_out: float = 0.0,
          mono_to_stereo: bool = False) -> Path:
    """Trim/gain/fade a stem and place it on a silent scene-length bed."""
    out = work / f"{name}.wav"
    filt = "[0:a]"
    if seg_len is not None:
        filt += f"atrim=0:{fmt_t(seg_len)},"
    filt += "aresample=48000"
    if mono_to_stereo:
        filt += ",pan=stereo|c0=c0|c1=c0"
    else:
        filt += ",aformat=channel_layouts=stereo"
    if gain_db:
        filt += f",volume={gain_db:.2f}dB"
    if fade_in:
        filt += f",afade=t=in:st=0:d={fmt_t(fade_in)}"
    if fade_out and seg_len is not None:
        filt += f",afade=t=out:st={fmt_t(seg_len - fade_out)}:d={fmt_t(fade_out)}"
    ms = int(round(at * 1000))
    filt += (f",adelay={ms}:all=1,apad=whole_dur={fmt_t(total)},"
             f"atrim=0:{fmt_t(total)}[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out)])
    return out


def duck(bus: Path, key: Path, work: Path, name: str) -> Path:
    out = work / f"{name}.wav"
    filt = (f"[0:a][1:a]sidechaincompress="
            f"threshold={DUCK['threshold']}:ratio={DUCK['ratio']}:"
            f"attack={DUCK['attackMs']}:release={DUCK['releaseMs']}[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(bus), "-i", str(key),
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out)])
    return out


def mixdown(parts: list, total: float, out_path: Path,
            trim_db: float = 0.0) -> None:
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    filt = ("".join(f"[{i}:a]" for i in range(len(parts)))
            + f"amix=inputs={len(parts)}:normalize=0:dropout_transition=0")
    if trim_db:
        filt += f",volume={-trim_db:.2f}dB"
    filt += (f",afade=t=in:st=0:d=0.3,"
             f"afade=t=out:st={fmt_t(total - 0.3)}:d=0.3,"
             f"atrim=0:{fmt_t(total)}[a]")
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out_path)])


def main() -> None:
    root = Path(".")
    vo_dir = root / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"
    out_dir = root / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V4"
    out_dir.mkdir(parents=True, exist_ok=True)
    work_root = Path(tempfile.mkdtemp(prefix="p0_mix_"))
    manifest_scenes = []
    scene_mix_paths = {}

    for scene_id, spec in SCENES.items():
        total = spec["seconds"]
        work = work_root / scene_id
        work.mkdir()
        vo_wav, vo_at = VO_TAKES[scene_id]
        vo_bus = place(vo_dir / vo_wav, vo_at, total, work, "vo",
                       mono_to_stereo=True)
        vo_take = probe(vo_dir / vo_wav)
        vo_dur = float(vo_take["format"]["duration"])
        win = (vo_at, round(vo_at + vo_dur, 3))

        buses = {"vo": vo_bus}
        stem_records = []
        loop_records = []

        # Music bus
        music_duck = None
        if spec["music"]:
            m = spec["music"]
            gain = m.get("target", MUSIC_TARGET_LUFS) - MEASURED_LUFS[m["cue"]]
            seg = place(root / STEM_FILES[m["cue"]], m["at"], total, work,
                        "music_raw", gain_db=gain, seg_len=m["len"],
                        fade_in=m["fadeIn"], fade_out=m["fadeOut"])
            stem_records.append({
                "cue": m["cue"], "role": "music", "source": STEM_FILES[m["cue"]],
                "provenance": PROVENANCE[m["cue"]],
                "segmentSceneSeconds": [m["at"], m["at"] + m["len"]],
                "targetLUFS": MUSIC_TARGET_LUFS,
                "cp02MeasuredLUFS": MEASURED_LUFS[m["cue"]],
                "gainDb": round(gain, 2), "duckedByVo": m["ducked"],
            })
            if m["ducked"]:
                ducked = duck(seg, vo_bus, work, "music_ducked")
                music_duck = (seg, ducked)
                buses["music"] = ducked
            else:
                buses["music"] = seg

        # Ambience buses: beds are built at their scene offset via place-like
        # handling: build the bed for its own length, then delay it.
        amb_duck = None
        amb_parts = []
        for a in spec["ambience"]:
            gain = a["target"] - MEASURED_LUFS[a["cue"]]
            bed, joins = build_bed(root / STEM_FILES[a["cue"]], a["len"],
                                   gain, work,
                                   f"amb_{a['cue'].split('/')[1]}",
                                   fade_out=a.get("fadeOut", 0.0))
            loop_records.append({"cue": a["cue"], "joins": loop_qa(bed, joins)})
            placed = place(bed, a["at"], total, work,
                           f"amb_{a['cue'].split('/')[1]}_placed")
            stem_records.append({
                "cue": a["cue"], "role": "ambience",
                "source": STEM_FILES[a["cue"]],
                "provenance": PROVENANCE[a["cue"]],
                "segmentSceneSeconds": [a["at"], a["at"] + a["len"]],
                "targetLUFS": a["target"],
                "cp02MeasuredLUFS": MEASURED_LUFS[a["cue"]],
                "gainDb": round(gain, 2), "duckedByVo": a["ducked"],
            })
            if a["ducked"]:
                amb_duck = (placed, None)  # duck after summing ambience
            amb_parts.append((a, placed))
        if len(amb_parts) == 1:
            amb_bus = amb_parts[0][1]
        else:
            amb_bus = work / "amb_bus.wav"
            mixdown([p for _, p in amb_parts], total, amb_bus)
            # mixdown adds scene-edge fades; acceptable on a sub-bus for a
            # draft, and it is re-faded in the final mix. Recorded in notes.
        if amb_duck is not None:
            ducked = duck(amb_bus, vo_bus, work, "amb_ducked")
            amb_duck = (amb_bus, ducked)
            amb_bus = ducked
        buses["ambience"] = amb_bus

        # Stinger
        stinger_record = None
        if spec["stinger"]:
            s = spec["stinger"]
            st = place(root / STEM_FILES[s["cue"]], s["at"], total, work,
                       "stinger", mono_to_stereo=False)  # v2/v3: composed
            # stingers are stereo OGGs; the v1 ported stingers were mono
            # WAVs and needed the pan. Do not collapse the stereo image.
            buses["stinger"] = st
            stinger_record = {
                "cue": s["cue"], "source": STEM_FILES[s["cue"]],
                "provenance": PROVENANCE[s["cue"]],
                "atSeconds": s["at"], "gainDb": 0.0,
                "cp02MeasuredLUFS": MEASURED_LUFS[s["cue"]],
                "placementStatus": "PROPOSED_PENDING_PICTURE_LOCK",
            }
            stem_records.append({**stinger_record, "role": "stinger"})

        # Ducking evidence: RMS of ducked vs unducked bus, in-window vs
        # a 2 s reference right before the window.
        duck_evidence = []
        for label, pair in (("music", music_duck), ("ambience", amb_duck)):
            if not pair:
                continue
            raw_bus, ducked_bus = pair
            ref_start = max(0.0, win[0] - 2.5)
            in_raw = segment_rms_db(raw_bus, win[0], min(2.0, win[1] - win[0]))
            in_duck = segment_rms_db(ducked_bus, win[0],
                                     min(2.0, win[1] - win[0]))
            out_raw = segment_rms_db(raw_bus, ref_start, 2.0)
            out_duck = segment_rms_db(ducked_bus, ref_start, 2.0)
            duck_evidence.append({
                "bus": label,
                "windowSeconds": list(win),
                "referenceSeconds": [ref_start, ref_start + 2.0],
                "depthInWindowDb": round(in_duck - in_raw, 2),
                "depthOutsideWindowDb": round(out_duck - out_raw, 2),
            })

        # Final scene mix with peak guard.
        parts = [buses[k] for k in ("vo", "music", "ambience", "stinger")
                 if k in buses]
        tmp_mix = work / "mix_untrimmed.wav"
        mixdown(parts, total, tmp_mix)
        ln = loudnorm(tmp_mix)
        tp = float(ln["input_tp"])
        trim = round(tp - PEAK_CEILING_DBTP, 2) if tp > PEAK_CEILING_DBTP else 0.0
        mix_path = out_dir / f"{scene_id}_mix_draft_v4.wav"
        mixdown(parts, total, mix_path, trim_db=trim)
        ln = loudnorm(mix_path)
        p = probe(mix_path)
        dur = float(p["format"]["duration"])
        if abs(dur - total) > 0.05:
            print(f"{scene_id}: MIX DURATION {dur} != {total}",
                  file=sys.stderr)
            sys.exit(1)
        print(f"{scene_id}: mix {dur:.3f}s LUFS {ln['input_i']} "
              f"TP {ln['input_tp']} (peak trim {trim:.2f} dB), "
              f"ducking: {[(e['bus'], e['depthInWindowDb']) for e in duck_evidence]}")
        scene_mix_paths[scene_id] = mix_path
        manifest_scenes.append({
            "sceneId": scene_id,
            "seconds": total,
            "vo": {"take": vo_wav, "windowSeconds": list(win),
                   "gainDb": 0.0},
            "stems": stem_records,
            "ducking": {"params": DUCK, "evidence": duck_evidence},
            "stinger": stinger_record,
            "loopQA": loop_records,
            "mix": {
                "file": mix_path.name,
                "sha256": sha256(mix_path),
                "durationSeconds": round(dur, 4),
                "integratedLUFS": ln["input_i"],
                "truePeakDBTP": ln["input_tp"],
                "loudnessRangeLU": ln["input_lra"],
                "peakTrimDb": trim,
                "format": {"codec": p["streams"][0]["codec_name"],
                           "sampleRateHz": int(p["streams"][0]["sample_rate"]),
                           "channels": int(p["streams"][0]["channels"]),
                           "bytes": int(p["format"]["size"])},
            },
        })

    # M-F CP2: no 72 s review reel is built -- only CIN_002
    # changes; CIN_001/CIN_004 keep their v3 mixes.

    manifest = {
        "checkpoint": "MEDIA-02 WO37 M-F CP2 - P0 draft mix v4: CIN_002 palette re-mix only (Ta Van Khanh pickup); CIN_001/CIN_004 not rebuilt, their v3 mixes stand",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL",
        "mixVerdict": ("DRAFT_MIX_FOR_REVIEW: P0 re-mixed from FULLY "
                       "COMPOSED stems -- checkpoint-26 composed music + "
                       "cinema stingers and checkpoint-30 composed "
                       "ambience (same CP02 PROPOSED_CANDIDATE stem "
                       "table, same CP04 draft VO, same placements/"
                       "gains/ducking as the checkpoint-20 v1 and "
                       "checkpoint-29 v2 mixes). Delivered IN PARALLEL "
                       "to v1 and v2; adoption is Codex's adapter "
                       "decision. NOT a mix PASS: no ear audition, stem "
                       "table not locked, stinger placements PROPOSED "
                       "pending picture lock."),
        "mixVersion": "v4_palette_cin002",
        "supersedes": None,
        "v1MixUntouched": ("The checkpoint-20 v1 mixes "
                           "(Art_Source/Audio/Muse/MIX/P0_DRAFT/ and "
                           "ClientGodot/assets/audio/mix/p0/) and the "
                           "checkpoint-29 v2 mixes (MIX/P0_DRAFT_V2/ and "
                           "mix/p0_v2/) are byte-identical to before; "
                           "v3 adds mix/p0_v3/."),
        "substitutionTable": {
            "MUSIC/quiet_discovery": {
                "v2": "composed quiet_discovery.ogg (-21.72 LUFS, CP26)",
                "v3": "UNCHANGED from v2"},
            "MUSIC/boss_mang_cot": {
                "v2": "composed boss_mang_cot.ogg (-21.98 LUFS, CP26)",
                "v3": "UNCHANGED from v2"},
            "SFX/CINEMA/reveal": {
                "v2": "composed reveal.ogg (-24.96 LUFS, CP26, stereo)",
                "v3": "UNCHANGED from v2"},
            "SFX/CINEMA/tension": {
                "v2": "composed tension.ogg (-24.93 LUFS, CP26, stereo)",
                "v3": "UNCHANGED from v2"},
            "AMBIENCE/rain_light": {
                "v2": "ported PackV1 rain_light.ogg (-27.48 LUFS)",
                "v3": "composed rain_light.ogg (-27.80 LUFS, CP30)"},
            "AMBIENCE/river_shore": {
                "v2": "ported PackV1 river_shore.ogg (-29.53 LUFS)",
                "v3": "composed river_shore.ogg (-29.69 LUFS, CP30)"},
            "AMBIENCE/underwater": {
                "v2": "ported PackV1 underwater.ogg (-33.02 LUFS)",
                "v3": "composed underwater.ogg (-33.11 LUFS, CP30)"},
        },
        "stemTableSource": ("Implementation/Reports/MuseMedia/"
                            "MEDIA02_CHECKPOINT_02_P0_STEMS_20261105.json "
                            "(per-shot table, PROPOSED_CANDIDATE)"),
        "stemBytes": ("Runtime stem copies in ClientGodot/assets/audio/ "
                      "(the delivered runtime bytes), not the FLAC "
                      "masters."),
        "gainStaging": {
            "vo": "unity (anchor; takes as delivered)",
            "musicTargetLUFS": MUSIC_TARGET_LUFS,
            "ambiencePrimaryTargetLUFS": AMB_PRIMARY_LUFS,
            "ambienceSecondaryTargetLUFS": AMB_SECONDARY_LUFS,
            "stingers": "unity",
            "peakCeilingDBTP": PEAK_CEILING_DBTP,
        },
        "notes": [
            "Gains are formula targets from CP02 integrated-LUFS "
            "measurements; loudness inside a stem segment varies, so "
            "the realised balance is a draft balance, verified only by "
            "the whole-scene measurements in this manifest.",
            "Ducking depth is measured on the ducked bus against its "
            "unducked render (RMS in the first 2 s of the VO window "
            "vs a 2 s reference before the window).",
            "Ambience loop joins use 1 s acrossfades; loopQA reports "
            "the max sample jump at each join against the bed's own "
            "99.9th-percentile jump (ratio near or below ~2 reads as "
            "no click; an ear check is still outstanding).",
            "When a scene has two ambience beds they are summed on a "
            "sub-bus that carries the standard 0.3 s scene-edge fades "
            "before the final mix; inaudible at bed levels, recorded "
            "here for honesty.",
            "ben_mua and rain_heavy stay unassigned in P0, as in CP02; "
            "resolve/transition stingers are inter-scene and unused.",
            "v3 changes ONLY the ambience stem bytes (composed "
            "instead of ported); music, stingers, VO takes, placements, "
            "gain targets, ducking params and peak guard are identical "
            "to v2, so any loudness/balance delta between v2 and v3 is "
            "attributable to the ambience swap alone.",
            "Composed stingers are stereo OGGs: placed without the "
            "mono-to-stereo pan the v1 ported mono WAV stingers needed.",
            "Composed ambience beds are the checkpoint-30 masters "
            "(16.0 s, 0.25 s end-landing loop construction); the P0 "
            "mixer still extends them with its own 1 s acrossfade "
            "joins, as for the ported beds in v1/v2 -- loop QA in this "
            "manifest is measured on the mixer output, not the cue "
            "seam.",
            "VO windows: CIN_001 DECIDED 24.8-28.5 s; CIN_002 and "
            "CIN_004 PROPOSED (D1 draft approval only).",
        ],
        "scenes": manifest_scenes,
    }
    (out_dir / "P0_MIX_V4_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: P0_MIX_V4_manifest_v1.json written")


# ---------------------------------------------------------------------
# MEDIA-02 WO37 M-F CP2 palette record. The mixing code above is the
# v1 code, unchanged; main() still writes the v1-schema manifest and
# augment_manifest() then records the palette decision, the recomputed
# window fit of the pickup take(s) and the review status on it.
# ---------------------------------------------------------------------
DECISION_REF = {
    "decision": ("Apply the M-F CP1 voice palette (side B of the "
                 "WO39 M39-B CP1 level-matched A/B review) to every "
                 "role that has a distinct pickup take"),
    "delegatedBy": ("Project owner delegated the voice choice to "
                    "Muse (main chat, 2026-11-12 18:30 JST)"),
    "chosenBy": ("Muse (decision recorded in the dev queue, "
                 "2026-11-12 ~18:32 JST)"),
    "checkpoint": "MEDIA-02 WO37 M-F CP2",
    "paletteSourceManifest": ("Implementation/Content/Audio/Deliveries/"
                              "VO_PALETTE_PICKUPS_pack_v1.json"),
    "reason": ("Fixes the draft casting defect: every male speaker "
               "shared one draft voice (avocado_v2:MAI_03) and the "
               "CIN_020 letter recipient shared Ly An's draft voice "
               "(avocado_v2:MAI_01)"),
    "adoption": ("Draft v2 mixes live in Art_Source only; the runtime "
                 "still embeds the v1 mixes (runtime audio count "
                 "unchanged at 783) until Codex adopts v2 at review. "
                 "Final casting remains Codex's review decision."),
}
MANIFEST_REL = "Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/P0_MIX_V4_manifest_v1.json"
TIMING_REL = "Implementation/Content/Narrative/Deliveries/CIN_002/CIN_002_timing_v1.json"
PALETTE_TAKES = [{'takeKey': 'CIN002_S02', 'shotId': 'CIN_002_S02'}]
V2_MIX_VERDICT = "DRAFT_MIX_FOR_REVIEW (CIN_002 mix v4, MEDIA-02 WO37 M-F CP2 palette re-mix): built with the exact P0 v3 recipe (fully composed stems, same gain targets, ducking params, peak guard, loop joins); the ONLY change vs v3 is the VO take -- Ta Van Khanh is now the M-F CP1 palette pickup (VO_CIN002_S02_TAVANKHANH_palette_v1.wav; Polished Coin (fictional system voice), avocado_v2:conor) instead of the draft take voiced by avocado_v2:MAI_03. The palette take FITS its window (7.0-10.312 s inside 7.0-11.0 s, slack 0.688 s), measured from the real pickup bytes. CIN_001 / CIN_004 were NOT rebuilt: their lines are Ly An's and v3 stands. NOT a mix PASS: no ear audition; adoption is Codex's adapter decision. The runtime still embeds the v3 mix (candidate B picture + v3 audio)."
V2_MANIFEST_OVERRIDES = {'supersedes': 'For CIN_002 only: supersedes the v3 CIN_002 mix as the current palette candidate. The CIN_001 and CIN_004 v3 mixes are NOT superseded -- they are not rebuilt here because Ly An has no palette pickup.', 'v1MixUntouched': 'The checkpoint-20 v1 mixes, the checkpoint-29 v2 mixes and the checkpoint-31 v3 mixes (Art_Source and runtime copies) are byte-identical to before; v4 adds MIX/P0_DRAFT_V4/ with the CIN_002 palette re-mix only. The runtime is NOT modified by M-F CP2.'}


def _mf_cp2_probe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FFPROBE FAILED {path}", file=sys.stderr)
        sys.exit(1)
    return float(json.loads(r.stdout)["format"]["duration"])


def augment_manifest() -> None:
    root = Path(".")
    mpath = root / MANIFEST_REL
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    timing = json.loads((root / TIMING_REL).read_text(encoding="utf-8"))
    pickups = json.loads(
        (root / "Implementation/Content/Audio/Deliveries/"
         "VO_PALETTE_PICKUPS_pack_v1.json").read_text(encoding="utf-8"))
    by_key = {t["takeKey"]: t for t in pickups["takes"]}
    shots = {s["shotId"]: s for s in timing["shots"]}
    changes = []
    for spec in PALETTE_TAKES:
        take = by_key[spec["takeKey"]]
        win = shots[spec["shotId"]]["dialogue"]["windowSeconds"]
        rel = ("Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/"
               + take["paletteTake"]["wav"])
        dur = _mf_cp2_probe_dur(root / rel)
        start = float(win[0])
        end = start + dur
        entry = {
            "takeKey": spec["takeKey"],
            "shotId": spec["shotId"],
            "role": take["role"],
            "speakerDisplay": take.get("speakerDisplay"),
            "previousVoice": take["previousVoice"],
            "paletteVoice": take["voice"],
            "paletteVoiceLabel": take.get("voiceLabel"),
            "paletteTakeFile": rel,
            "paletteTakeSha256": sha256(root / rel),
            "paletteTakeDurationSeconds": round(dur, 3),
            "windowSeconds": [win[0], win[1]],
            "takeStartSeconds": start,
            "takeEndSeconds": round(end, 3),
            "slackSeconds": round(float(win[1]) - end, 3),
            "fit": "FITS" if end <= float(win[1]) + 0.005 else "OVERRUN",
            "voGainDb": 0.0,
        }
        if spec.get("voiceStatus"):
            entry["voiceStatus"] = spec["voiceStatus"]
        changes.append(entry)
    manifest["decisionRef"] = DECISION_REF
    manifest["auditionStatus"] = "NOT_AUDITIONED"
    manifest["mixVerdict"] = V2_MIX_VERDICT
    for key, value in V2_MANIFEST_OVERRIDES.items():
        manifest[key] = value
    manifest["paletteRemix"] = {
        "checkpoint": "MEDIA-02 WO37 M-F CP2",
        "palette": "M-F CP1 (side B)",
        "changes": changes,
        "unchanged": ("Stems, stem gains, ducking, peak guard, "
                      "placements and scene-edge fades run the exact "
                      "v1 code; only the VO take source(s) changed."),
    }
    if isinstance(manifest.get("notes"), list):
        manifest["notes"] = [
            "M-F CP2 palette re-mix: the VO take(s) listed under "
            "paletteRemix.changes replace the v1 draft take(s). Any "
            "v1 note below describing the canonical take's duration "
            "or overrun describes the v1 mix only and does not apply "
            "to v2."
        ] + manifest["notes"]
    mpath.write_text(json.dumps(manifest, ensure_ascii=False,
                                indent=2) + "\n", encoding="utf-8")
    print(f"OK: {mpath.name} augmented with the M-F CP2 palette record")


if __name__ == "__main__":
    main()
    augment_manifest()
