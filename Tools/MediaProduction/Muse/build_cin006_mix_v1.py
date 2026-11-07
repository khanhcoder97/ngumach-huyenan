#!/usr/bin/env python3
"""MEDIA-02 checkpoint 34 (Goi 31 item 4): CIN_006 DRAFT mix v1.

First scene mix for CIN_006 ("Con dau qua pho", 18 s), built with the
exact recipe of the P0 draft mixes v1/v2/v3 (build_p0_mix_v3.py): same
gain targets, same ducking params, same peak guard, same loop-join
method, same runtime stem bytes (ClientGodot/assets/audio/composed/,
OGG music/ambience/stingers).

NEW PROPOSED_CANDIDATE stem assignment (nothing in the CP02 P0 stem
table assigns any stem to CIN_006, and the scene timing manifest lists
only SFX/CINEMA/reveal as a candidate stem -- this assignment is new,
proposed, not locked; adoption is Codex's adapter decision):
  music    MUSIC/thang_long (composed, CP26) 0-18 s, ducked by the VO
  ambience AMBIENCE/thang_long_crowd (composed, CP30) 0-18 s, unducked
  stinger  SFX/CINEMA/reveal (composed, CP26) at 6.0 s = S02 start,
           PROPOSED placement (mirrors the CIN_004 reveal at 6.0 s)
  VO       CIN_006_S03 draft take (CP19) at the 12.5 s window start

Known consequence of the kept overrun (owner decision 2026-11-06:
window kept as-is, Codex decides at PR review): the take is 5.52 s,
so it runs 12.5-18.02 s -- 0.02 s past the scene end. The scene mix
trims to 18.00 s, so the final 0.02 s of the take is cut (inside the
0.3 s scene-edge fade). Recorded in the manifest; the window, the
take and the timing are NOT changed to hide it.

Outputs land in Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1/: one WAV
(48 kHz stereo pcm_s16le) + CIN006_MIX_V1_manifest_v1.json.
Intermediates live in a temp dir. DRAFT_MIX_NOT_FINAL, no ear
audition; measurements are from the real rendered bytes.
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
TOTAL = 18.0
MUSIC_TARGET_LUFS = -30.0
AMB_PRIMARY_LUFS = -36.0
PEAK_CEILING_DBTP = -1.0
DUCK = {"threshold": 0.03, "ratio": 4, "attackMs": 15, "releaseMs": 350}
LOOP_SECONDS = 16.0
XFADE_SECONDS = 1.0

MUSIC_CUE = "MUSIC/thang_long"
AMB_CUE = "AMBIENCE/thang_long_crowd"
STINGER_CUE = "SFX/CINEMA/reveal"
STEM_FILES = {
    MUSIC_CUE: "ClientGodot/assets/audio/composed/music/thang_long.ogg",
    AMB_CUE: "ClientGodot/assets/audio/composed/ambience/thang_long_crowd.ogg",
    STINGER_CUE: "ClientGodot/assets/audio/composed/cinema/reveal.ogg",
}
PROVENANCE = {
    MUSIC_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    AMB_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
    STINGER_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
}
# Pack-table LUFS (CP26 music/stingers, CP30 ambience); re-measured
# this run before mixing and asserted to match within 0.05 LUFS.
PACK_LUFS = {MUSIC_CUE: -21.96, AMB_CUE: -30.59, STINGER_CUE: -24.96}

VO_SRC = "Art_Source/Audio/Muse/VO/CIN006_DRAFT/VO_CIN_006_S03_HAMAC_draft_v1.wav"
VO_AT = 12.5
STINGER_AT = 6.0


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
    out_dir = root / "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="cin006_mix_"))

    # Re-measure the stems actually mixed; gains use these values.
    measured = {}
    for cue, rel in STEM_FILES.items():
        ln = loudnorm(root / rel)
        measured[cue] = float(ln["input_i"])
        if abs(measured[cue] - PACK_LUFS[cue]) > 0.05:
            print(f"STEM LUFS DRIFT {cue}: measured {measured[cue]} "
                  f"vs pack {PACK_LUFS[cue]}", file=sys.stderr)
            sys.exit(1)
        print(f"stem {cue}: re-measured {measured[cue]} LUFS "
              f"(pack {PACK_LUFS[cue]})")

    vo_path = root / VO_SRC
    vo_take = probe(vo_path)
    vo_dur = float(vo_take["format"]["duration"])
    vo_end = VO_AT + vo_dur
    tail_trim = round(max(0.0, vo_end - TOTAL), 3)
    win = (VO_AT, round(min(vo_end, TOTAL), 3))
    vo_bus = place(vo_path, VO_AT, TOTAL, work, "vo", mono_to_stereo=True)

    stem_records = []
    loop_records = []

    # Music bus (ducked by VO)
    gain = MUSIC_TARGET_LUFS - measured[MUSIC_CUE]
    seg = place(root / STEM_FILES[MUSIC_CUE], 0.0, TOTAL, work,
                "music_raw", gain_db=gain, seg_len=TOTAL,
                fade_in=0.5, fade_out=1.5)
    stem_records.append({
        "cue": MUSIC_CUE, "role": "music",
        "source": STEM_FILES[MUSIC_CUE],
        "provenance": PROVENANCE[MUSIC_CUE],
        "segmentSceneSeconds": [0.0, TOTAL],
        "targetLUFS": MUSIC_TARGET_LUFS,
        "packMeasuredLUFS": PACK_LUFS[MUSIC_CUE],
        "remeasuredLUFS": measured[MUSIC_CUE],
        "gainDb": round(gain, 2), "duckedByVo": True,
    })
    music_raw, music_ducked = seg, duck(seg, vo_bus, work, "music_ducked")

    # Ambience bus (unducked, looped with 1 s acrossfade joins)
    gain_a = AMB_PRIMARY_LUFS - measured[AMB_CUE]
    bed, joins = build_bed(root / STEM_FILES[AMB_CUE], TOTAL, gain_a,
                           work, "amb_thang_long_crowd")
    loop_records.append({"cue": AMB_CUE, "joins": loop_qa(bed, joins)})
    amb_bus = place(bed, 0.0, TOTAL, work, "amb_placed")
    stem_records.append({
        "cue": AMB_CUE, "role": "ambience",
        "source": STEM_FILES[AMB_CUE],
        "provenance": PROVENANCE[AMB_CUE],
        "segmentSceneSeconds": [0.0, TOTAL],
        "targetLUFS": AMB_PRIMARY_LUFS,
        "packMeasuredLUFS": PACK_LUFS[AMB_CUE],
        "remeasuredLUFS": measured[AMB_CUE],
        "gainDb": round(gain_a, 2), "duckedByVo": False,
    })

    # Stinger (PROPOSED placement at S02 start)
    st = place(root / STEM_FILES[STINGER_CUE], STINGER_AT, TOTAL, work,
               "stinger")
    stinger_record = {
        "cue": STINGER_CUE, "source": STEM_FILES[STINGER_CUE],
        "provenance": PROVENANCE[STINGER_CUE],
        "atSeconds": STINGER_AT, "gainDb": 0.0,
        "packMeasuredLUFS": PACK_LUFS[STINGER_CUE],
        "remeasuredLUFS": measured[STINGER_CUE],
        "placementStatus": "PROPOSED_PENDING_PICTURE_LOCK",
    }
    stem_records.append({**stinger_record, "role": "stinger"})

    # Ducking evidence (music bus, in-window vs 2 s reference before it)
    ref_start = max(0.0, win[0] - 2.5)
    in_raw = segment_rms_db(music_raw, win[0], min(2.0, win[1] - win[0]))
    in_duck = segment_rms_db(music_ducked, win[0],
                             min(2.0, win[1] - win[0]))
    out_raw = segment_rms_db(music_raw, ref_start, 2.0)
    out_duck = segment_rms_db(music_ducked, ref_start, 2.0)
    duck_evidence = [{
        "bus": "music",
        "windowSeconds": list(win),
        "referenceSeconds": [ref_start, ref_start + 2.0],
        "depthInWindowDb": round(in_duck - in_raw, 2),
        "depthOutsideWindowDb": round(out_duck - out_raw, 2),
    }]

    parts = [vo_bus, music_ducked, amb_bus, st]
    tmp_mix = work / "mix_untrimmed.wav"
    mixdown(parts, TOTAL, tmp_mix)
    ln = loudnorm(tmp_mix)
    tp = float(ln["input_tp"])
    trim = round(tp - PEAK_CEILING_DBTP, 2) if tp > PEAK_CEILING_DBTP else 0.0
    mix_path = out_dir / "CIN_006_mix_draft_v1.wav"
    mixdown(parts, TOTAL, mix_path, trim_db=trim)
    ln = loudnorm(mix_path)
    p = probe(mix_path)
    dur = float(p["format"]["duration"])
    if abs(dur - TOTAL) > 0.05:
        print(f"CIN_006: MIX DURATION {dur} != {TOTAL}", file=sys.stderr)
        sys.exit(1)
    print(f"CIN_006: mix {dur:.3f}s LUFS {ln['input_i']} "
          f"TP {ln['input_tp']} (peak trim {trim:.2f} dB), "
          f"ducking music {duck_evidence[0]['depthInWindowDb']} dB, "
          f"VO tail trimmed {tail_trim} s")

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 34 - CIN_006 draft mix v1 (Goi 31 item 4: minimal runtime pack -- first scene mix for CIN_006, same recipe as P0 v3)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_MIX_NOT_FINAL",
        "mixVersion": "v1_cin006_proposed",
        "mixVerdict": ("DRAFT_MIX_FOR_REVIEW: first scene mix for CIN_006, "
                       "built with the P0 v3 recipe (same gain targets, "
                       "ducking params, peak guard, loop joins). Stem "
                       "assignment is NEW and PROPOSED_CANDIDATE (the "
                       "CP02 stem table assigns nothing to CIN_006; the "
                       "scene timing manifest lists only the reveal "
                       "stinger as a candidate stem). VO take is the "
                       "CP19 draft; the +0.52 s overrun window is kept "
                       "as-is per the owner decision and the take tail "
                       "is trimmed 0.02 s at the scene edge -- recorded, "
                       "not hidden. NOT a mix PASS: no ear audition, "
                       "stem table not locked, stinger placement "
                       "PROPOSED pending picture lock. Adoption is "
                       "Codex's adapter decision."),
        "stemAssignment": {
            "status": "PROPOSED_CANDIDATE_NEW",
            "source": ("No CP02 assignment exists for CIN_006; "
                       "thang_long music + thang_long_crowd ambience "
                       "are the Thang Long setting cues (composed, "
                       "CP26/CP30) and the reveal stinger is the "
                       "scene's only manifest-listed candidate stem "
                       "(CIN_006_timing_v1.json)."),
            "alternateTakeExcluded": ("CIN_006_ALT_T01 is NOT in this "
                                      "mix (DEC-MEDIA-P0 Q3: alternate "
                                      "take keeps its own takeId/version "
                                      "and never replaces canonical)."),
        },
        "gainStaging": {
            "vo": "unity (anchor; take as delivered)",
            "musicTargetLUFS": MUSIC_TARGET_LUFS,
            "ambiencePrimaryTargetLUFS": AMB_PRIMARY_LUFS,
            "stingers": "unity",
            "peakCeilingDBTP": PEAK_CEILING_DBTP,
        },
        "notes": [
            "VO window 12.5-17.5 s is PROPOSED_ANIMATIC_PLACEMENT (only "
            "CIN_001_S05 is DECIDED); all 21 windows are approved for "
            "DRAFT VO per Goi 30 D1.",
            "VO take runs 12.5-18.02 s: 0.02 s past the 18.00 s scene "
            "end. The mix trims to 18.00 s, so the last 0.02 s of the "
            "take is cut inside the 0.3 s scene-edge fade. The window, "
            "the take and the timing are unchanged; Codex decides the "
            "overrun at PR review (owner decision 2026-11-06).",
            "Ducking depth is measured on the ducked bus against its "
            "unducked render (RMS in the first 2 s of the VO window "
            "vs a 2 s reference before the window).",
            "Ambience loop join uses a 1 s acrossfade; loopQA reports "
            "the max sample jump at the join against the bed's own "
            "99.9th-percentile jump.",
            "Stinger placement at 6.0 s (S02 start) is PROPOSED pending "
            "picture lock, mirroring the CIN_004 reveal at 6.0 s.",
        ],
        "scenes": [{
            "sceneId": "CIN_006",
            "seconds": TOTAL,
            "vo": {"take": VO_SRC.split("/")[-1],
                   "windowSeconds": list(win),
                   "takeDurationSeconds": vo_dur,
                   "takeEndSeconds": round(vo_end, 3),
                   "tailTrimmedAtSceneEdgeSeconds": tail_trim,
                   "overrunVsWindowSeconds": round(vo_end - 17.5, 3),
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
        }],
    }
    (out_dir / "CIN006_MIX_V1_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: CIN006_MIX_V1_manifest_v1.json written")


if __name__ == "__main__":
    main()
