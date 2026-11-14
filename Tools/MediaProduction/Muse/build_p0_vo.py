#!/usr/bin/env python3
"""MEDIA-02 checkpoint 04: build the P0 VO drafts (3 lines) from TTS MP3s.

Regenerate the raw MP3s first (fictional system voices only, no real-voice
cloning, no unlicensed samples) with /opt/hatch/bin/tts:

  tts speak --voice avocado_v2:MAI_01 --language vi \\
      --output CIN001_S05.mp3 --text-stdin   # "Dau kia! Giu giup toi dau kia!"
  tts speak --voice avocado_v2:MAI_03 --language vi \\
      --output CIN002_S02.mp3 --text-stdin   # "Tren bo chi nghe nua tieng. ..."
  tts speak --voice avocado_v2:MAI_01 --language vi \\
      --output CIN004_S02.mp3 --text-stdin   # "No cu tranh cho nuoc ay."

(Vietnamese text is passed verbatim via stdin; the comments above are ASCII
placeholders only, never synthesis input.)

This tool then converts each MP3 to WAV 48 kHz mono, measures duration with
ffprobe and loudness/true peak with ffmpeg loudnorm, checks every take fits
its dialogue window (fails on overrun -- a draft that does not fit its window
is not a deliverable), and assembles a 72 s VO-only timeline WAV placing each
take at its scene-offset window start (CIN_001 offset 0 s, CIN_002 offset
36 s, CIN_004 offset 54 s). The timeline is a DRAFT assembly, not a mix:
no music/ambience stems are mixed in, and no loudness normalization is
applied to the takes. Outputs land in Art_Source/Audio/Muse/VO/P0_DRAFT/.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

TAKES = [
    {
        "key": "CIN001_S05",
        "shotId": "CIN_001_S05",
        "speaker": "NPC_LYAN",
        "voice": "avocado_v2:MAI_01",
        "voiceLabel": "Aria (fictional system voice)",
        "mp3": "CIN001_S05.mp3",
        "wav": "VO_CIN001_S05_LYAN_draft_v1.wav",
        "text": "Đầu kia! Giữ giúp tôi đầu kia!",
        "windowSceneSeconds": [24.8, 28.5],
        "sceneOffsetSeconds": 0.0,
        "status": "DECIDED_DEC_MEDIA_P0",
    },
    {
        "key": "CIN002_S02",
        "shotId": "CIN_002_S02",
        "speaker": "NPC_TA_VAN_KHANH",
        "voice": "avocado_v2:MAI_03",
        "voiceLabel": "Helio (fictional system voice)",
        "mp3": "CIN002_S02.mp3",
        "wav": "VO_CIN002_S02_TAVANKHANH_draft_v1.wav",
        "text": "Trên bờ chỉ nghe nửa tiếng. Phần còn lại ở dưới ấy.",
        "windowSceneSeconds": [7.0, 11.0],
        "sceneOffsetSeconds": 36.0,
        "status": "PROPOSED_ANIMATIC_PLACEMENT",
    },
    {
        "key": "CIN004_S02",
        "shotId": "CIN_004_S02",
        "speaker": "NPC_LYAN",
        "voice": "avocado_v2:MAI_01",
        "voiceLabel": "Aria (fictional system voice)",
        "mp3": "CIN004_S02.mp3",
        "wav": "VO_CIN004_S02_LYAN_OFFSCREEN_draft_v1.wav",
        "text": "Nó cứ tránh chỗ nước ấy.",
        "windowSceneSeconds": [7.5, 9.5],
        "sceneOffsetSeconds": 54.0,
        "status": "PROPOSED_ANIMATIC_PLACEMENT; OFFSCREEN_DECIDED_DEC_MEDIA_P0",
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stdout, r.stderr, file=sys.stderr)
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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--mp3-dir", required=True)
    ap.add_argument("--out-dir",
                    default="Art_Source/Audio/Muse/VO/P0_DRAFT")
    args = ap.parse_args()
    root = Path(args.root)
    mp3_dir = Path(args.mp3_dir)
    out = root / args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    results = []
    for take in TAKES:
        src = mp3_dir / take["mp3"]
        if not src.exists():
            print(f"MISSING MP3: {src}", file=sys.stderr)
            sys.exit(1)
        raw = out / take["mp3"].replace(".mp3", "_tts_raw.mp3")
        raw.write_bytes(src.read_bytes())
        wav = out / take["wav"]
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
             "-ar", "48000", "-ac", "1", str(wav)])
        p = probe(wav)
        duration = float(p["format"]["duration"])
        window = take["windowSceneSeconds"][1] - take["windowSceneSeconds"][0]
        slack = window - duration
        ln = loudnorm(wav)
        fit = "FITS" if slack >= 0 else "OVERRUN"
        print(f"{take['shotId']}: {duration:.4f}s in {window:.1f}s window "
              f"(slack {slack:+.4f}s) {fit} "
              f"LUFS {ln['input_i']} TP {ln['input_tp']}")
        if slack < 0:
            print(f"OVERRUN: {take['shotId']} exceeds its window; "
                  "not a deliverable.", file=sys.stderr)
            sys.exit(1)
        results.append({
            **take,
            "wav": take["wav"],
            "wavSha256": sha256(wav),
            "rawMp3": raw.name,
            "rawMp3Sha256": sha256(raw),
            "durationSeconds": round(duration, 4),
            "windowSeconds": window,
            "slackSeconds": round(slack, 4),
            "fit": fit,
            "timelineStartSeconds": round(
                take["sceneOffsetSeconds"] + take["windowSceneSeconds"][0], 1),
            "loudness": {
                "integratedLUFS": ln["input_i"],
                "truePeakDBTP": ln["input_tp"],
                "loudnessRangeLU": ln["input_lra"],
                "thresholdLUFS": ln["input_thresh"],
            },
            "format": {
                "codec": p["streams"][0]["codec_name"],
                "sampleRateHz": int(p["streams"][0]["sample_rate"]),
                "channels": int(p["streams"][0]["channels"]),
                "bytes": int(p["format"]["size"]),
            },
        })

    # 72 s VO-only timeline: each take delayed to its absolute window start.
    timeline = out / "P0_VO_timeline_draft_v1.wav"
    inputs, filters = [], []
    for i, take in enumerate(results):
        inputs += ["-i", str(out / take["wav"])]
        ms = int(round(take["timelineStartSeconds"] * 1000))
        filters.append(f"[{i}:a]adelay={ms}:all=1[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(results))) +
                   f"amix=inputs={len(results)}:normalize=0,"
                   "apad=whole_dur=72,atrim=0:72[aout]")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
         ";".join(filters), "-map", "[aout]", "-ar", "48000", "-ac", "1",
         str(timeline)])
    tp = probe(timeline)
    tl_duration = float(tp["format"]["duration"])
    print(f"timeline: {tl_duration:.4f}s")
    if abs(tl_duration - 72.0) > 0.05:
        print("TIMELINE DURATION MISMATCH", file=sys.stderr)
        sys.exit(1)

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 04 - P0 VO drafts (3 lines)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL_VO",
        "notes": [
            "Fictional system voices only; no real-voice cloning, "
            "no unlicensed samples.",
            "CIN_002/CIN_004 placements remain PROPOSED; only CIN_001_S05 "
            "text+window are DECIDED.",
            "Per-take loudness only, NOT a mix PASS; stems stay separate.",
            "Timeline is VO-only draft assembly; no music/ambience mixed in.",
        ],
        "takes": results,
        "timeline": {
            "file": timeline.name,
            "sha256": sha256(timeline),
            "durationSeconds": round(tl_duration, 4),
            "format": {"codec": tp["streams"][0]["codec_name"],
                       "sampleRateHz": int(tp["streams"][0]["sample_rate"]),
                       "channels": int(tp["streams"][0]["channels"])},
        },
    }
    (out / "P0_VO_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: manifest written")


if __name__ == "__main__":
    main()
