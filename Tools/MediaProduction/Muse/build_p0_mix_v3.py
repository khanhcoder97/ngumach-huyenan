#!/usr/bin/env python3
"""MEDIA-02 checkpoint 31: P0 DRAFT mix v3 -- same three scenes, re-mixed
from FULLY COMPOSED stems: the checkpoint-26 composed music + cinema
stingers (as in v2) PLUS the checkpoint-30 composed ambience
(ORIGINAL_COMPOSED_BY_MUSE), replacing the last ported stems in the
P0 mixes. Same roles, placements, gain formula, ducking and peak guard
as v1/v2; only the ambience stem bytes change vs v2.

Substitution table vs v2 (ambience only; music/stingers identical):
  AMBIENCE/rain_light    ported (-27.48 LUFS) -> composed rain_light
      runtime OGG, re-measured 2026-11-06 at -27.80 LUFS, 16.0 s
  AMBIENCE/river_shore   ported (-29.53 LUFS) -> composed river_shore
      runtime OGG, re-measured 2026-11-06 at -29.69 LUFS, 16.0 s
  AMBIENCE/underwater    ported (-33.02 LUFS) -> composed underwater
      runtime OGG, re-measured 2026-11-06 at -33.11 LUFS, 16.0 s
  (Re-measurements this run match the checkpoint-30 pack table to
  0.01 LUFS.) VO takes are the same checkpoint-04 drafts as v1/v2.

The v1 and v2 mixes are NOT replaced: v3 is delivered in parallel
under MIX/P0_DRAFT_V3/ and runtime mix/p0_v3/ so Codex can choose at
review which stem set the presentation adapter uses. Same DRAFT status
as v1/v2: DRAFT_MIX_NOT_FINAL, no ear audition, stinger placements
PROPOSED.

This tool mixes, per P0 scene, the checkpoint-04 VO take with the
checkpoint-02 PROPOSED_CANDIDATE stem-per-shot table, using the runtime
stem bytes exactly as delivered (ClientGodot/assets/audio/composed/,
OGG music, ambience and cinema stingers -- every P0 stem is now
composed, no ported stem remains):

  CIN_001 (36 s): composed rain_light 0-6 s + composed river_shore
    throughout; quiet_discovery 6-30 s, sidechain-ducked by the VO;
    VO at the DECIDED window 24.8 s; reveal stinger at 30.0 s
    (S06 start, PROPOSED placement, pending picture lock).
  CIN_002 (18 s): composed underwater 0-6 s + composed river_shore
    throughout, the river bed sidechain-ducked by the VO (per the
    CP02 table); tension stinger at 6.0 s (S02 start, PROPOSED);
    VO at 7.0 s.
  CIN_004 (18 s): boss_mang_cot 0-12 s, sidechain-ducked by the
    off-screen VO; composed river_shore throughout; reveal stinger
    at 6.0 s (S02 start, PROPOSED, "distorted-current beat" has no
    timecode in any source); VO at 7.5 s.

Draft gain staging (targets are integrated-LUFS goals; the applied
gain is target minus the measured value of the stem actually mixed --
CP26 re-measurements for the composed music/stingers, CP30 pack
measurements (re-measured this run, matching to 0.01 LUFS) for the
composed ambience -- recorded per stem in the manifest):
  VO at unity (anchor, takes as delivered, no normalization);
  music beds to -30 LUFS; ambience beds to -36 LUFS (a secondary
  ambience layered under another bed goes to -38 LUFS); stingers at
  unity. Ducking: ffmpeg sidechaincompress, threshold 0.03, ratio 4,
  attack 15 ms, release 350 ms, key = the scene VO bus. (First render
  with threshold 0.015 / ratio 6 ducked the CIN_001 music by -18.8 dB
  under its hot -16 LUFS VO take -- near-mute, not a usable draft
  balance -- so the curve was softened; depths are re-measured and
  recorded per scene in the manifest.) Ambience loops
  are extended with 1 s acrossfade joins; the manifest carries a loop
  QA number per join (max sample jump at the join vs the bed's own
  99.9th-percentile sample jump). A peak guard trims the whole scene
  mix only if its true peak would exceed -1.0 dBTP (trim recorded).

This is a DRAFT MIX FOR REVIEW, not a mix PASS: the stem table is
PROPOSED_CANDIDATE (not locked), stinger placements are PROPOSED
pending picture lock, VO takes are DRAFT_NOT_FINAL_VO, gains are
formula targets (segment loudness varies inside a stem), and there
has been no ear audition. Measurements reported are from the real
rendered bytes: per-scene integrated LUFS / true peak (loudnorm) and
the ducking depth inside vs outside the VO window, measured on the
ducked bus against its unducked render.

Outputs land in Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/: one WAV per
scene (48 kHz stereo pcm_s16le), the concatenated 72 s review mix,
and P0_MIX_V3_manifest_v1.json. Intermediates live in a temp dir.
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
VO_TAKES = {  # sceneId -> (wav in P0_DRAFT, window start s)
    "CIN_001": ("VO_CIN001_S05_LYAN_draft_v1.wav", 24.8),
    "CIN_002": ("VO_CIN002_S02_TAVANKHANH_draft_v1.wav", 7.0),
    "CIN_004": ("VO_CIN004_S02_LYAN_OFFSCREEN_draft_v1.wav", 7.5),
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
    vo_dir = root / "Art_Source/Audio/Muse/VO/P0_DRAFT"
    out_dir = root / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3"
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
        mix_path = out_dir / f"{scene_id}_mix_draft_v3.wav"
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

    # 72 s review mix: CIN_001 + CIN_002 + CIN_004 concatenated.
    review = out_dir / "P0_mix_review_72s_draft_v3.wav"
    inputs = []
    for sid in ("CIN_001", "CIN_002", "CIN_004"):
        inputs += ["-i", str(scene_mix_paths[sid])]
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         "-filter_complex", "[0:a][1:a][2:a]concat=n=3:v=0:a=1[a]",
         "-map", "[a]", "-ar", str(SR), "-ac", "2", str(review)])
    ln = loudnorm(review)
    p = probe(review)
    rdur = float(p["format"]["duration"])
    if abs(rdur - 72.0) > 0.05:
        print(f"REVIEW DURATION {rdur} != 72.0", file=sys.stderr)
        sys.exit(1)
    print(f"review 72 s: {rdur:.3f}s LUFS {ln['input_i']} TP {ln['input_tp']}")

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 31 - P0 draft mix v3 from fully composed stems (checkpoint-30 composed ambience; Goi 30 item 7 follow-up, part 2)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_MIX_NOT_FINAL",
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
        "mixVersion": "v3_fully_composed",
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
        "reviewMix": {
            "file": review.name,
            "sha256": sha256(review),
            "durationSeconds": round(rdur, 4),
            "integratedLUFS": ln["input_i"],
            "truePeakDBTP": ln["input_tp"],
            "sceneOrder": ["CIN_001", "CIN_002", "CIN_004"],
            "note": ("Concatenation of the three scene mixes in reel "
                     "order; the 72 s reel remains review/gallery "
                     "only, NOT an auto-run opening (Goi 30 item 6)."),
        },
    }
    (out_dir / "P0_MIX_V3_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: P0_MIX_V3_manifest_v1.json written")


if __name__ == "__main__":
    main()
