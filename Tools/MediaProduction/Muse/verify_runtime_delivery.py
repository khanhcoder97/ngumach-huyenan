#!/usr/bin/env python3
"""MEDIA-02 checkpoint 11 (M8 handover/QA): re-verify the checkpoint-10
runtime delivery still matches its manifests, file by file, from real bytes.

Checks every entry of the two runtime manifests:
  ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json (545 audio files)
  ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json
    (3 animatic files + 20 scenes x timing JSON + SRT)

Per file: existence, LFS-pointer detection, size, sha256; audio files also
get ffprobe codec / sample rate / channels / duration (+-0.02 s) when the
manifest carries those fields. This tool does NOT re-measure loudness
(checkpoints 02/04/07/08 already measured it from real bytes) and does NOT
re-validate the source packs (validate_media_deliveries.py does that).

Usage: python3 verify_runtime_delivery.py [--out <json>]
Exit code 0 = no mismatches; 1 = at least one mismatch (details in JSON).
Only reads the repo tree; writes only the JSON report passed via --out.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "ClientGodot"
ERRORS = []
NOTES = []
COUNTS = {}


def err(msg):
    ERRORS.append(msg)


def note(msg):
    NOTES.append(msg)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path):
    try:
        with open(path, "rb") as f:
            return f.read(40).startswith(b"version https://git-lfs")
    except OSError:
        return False


def probe(path):
    """ffprobe first stream + format duration; returns dict or None."""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", str(path)],
            text=True, timeout=120)
    except Exception as exc:
        err(f"ffprobe failed for {path}: {exc}")
        return None
    data = json.loads(out)
    streams = data.get("streams") or []
    if not streams:
        err(f"ffprobe found no stream in {path}")
        return None
    s = streams[0]
    dur = None
    try:
        dur = float(s.get("duration") or data["format"]["duration"])
    except Exception:
        pass
    return {
        "codec": s.get("codec_name"),
        "sample_rate": int(s["sample_rate"]) if s.get("sample_rate") else None,
        "channels": s.get("channels"),
        "duration": dur,
    }


def check_file(rel_client_path, want_sha, want_size, label, audio_fields=None):
    """rel_client_path is relative to ClientGodot/ (e.g. assets/audio/...)."""
    path = CLIENT / rel_client_path
    if not path.exists():
        err(f"{label}: MISSING {rel_client_path}")
        return
    if is_lfs_pointer(path):
        err(f"{label}: LFS POINTER, not real bytes: {rel_client_path}")
        return
    size = path.stat().st_size
    if want_size is not None and size != want_size:
        err(f"{label}: size {size} != manifest {want_size}: {rel_client_path}")
    digest = sha256_of(path)
    if want_sha is not None and digest != want_sha:
        err(f"{label}: sha256 mismatch: {rel_client_path}")
    if audio_fields:
        p = probe(path)
        if p is None:
            return
        if audio_fields.get("codec") and p["codec"] != audio_fields["codec"]:
            err(f"{label}: codec {p['codec']} != manifest {audio_fields['codec']}: {rel_client_path}")
        if audio_fields.get("sampleRateHz") and p["sample_rate"] != audio_fields["sampleRateHz"]:
            err(f"{label}: sample_rate {p['sample_rate']} != manifest {audio_fields['sampleRateHz']}: {rel_client_path}")
        if audio_fields.get("channels") and p["channels"] != audio_fields["channels"]:
            err(f"{label}: channels {p['channels']} != manifest {audio_fields['channels']}: {rel_client_path}")
        if audio_fields.get("durationSeconds") is not None and p["duration"] is not None:
            if abs(p["duration"] - audio_fields["durationSeconds"]) > 0.02:
                err(f"{label}: duration {p['duration']:.4f} != manifest {audio_fields['durationSeconds']}: {rel_client_path}")


def check_audio_manifest():
    manifest = json.loads((CLIENT / "assets/audio/RUNTIME_AUDIO_manifest_v1.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    total = 0
    for entry in files:
        check_file(entry["runtimePath"], entry["sha256"], entry["sizeBytes"],
                   f"AUDIO {entry.get('cueKey', entry['runtimePath'])}", audio_fields=entry)
        total += 1
    COUNTS["runtime_audio_files_checked"] = total
    COUNTS["runtime_audio_manifest_total"] = manifest["totalFiles"]
    if total != manifest["totalFiles"]:
        err(f"AUDIO manifest totalFiles {manifest['totalFiles']} != entries checked {total}")
    note(f"Audio manifest counts: {manifest['counts']}")


def check_cinematics_manifest():
    manifest = json.loads((CLIENT / "assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json").read_text(encoding="utf-8"))
    anim = 0
    for entry in manifest["animatic"]:
        check_file(entry["runtimePath"], entry["sha256"], entry["sizeBytes"],
                   f"ANIMATIC {entry['runtimePath']}")
        anim += 1
    scenes = 0
    timing = 0
    srt = 0
    for scene in manifest["scenes"]:
        scenes += 1
        check_file(scene["timingFile"], scene["timingSha256"], None,
                   f"TIMING {scene['sceneId']}")
        timing += 1
        check_file(scene["srtFile"], scene["srtSha256"], None,
                   f"SRT {scene['sceneId']}")
        srt += 1
    COUNTS["animatic_files_checked"] = anim
    COUNTS["cinematics_scenes_checked"] = scenes
    COUNTS["timing_files_checked"] = timing
    COUNTS["srt_files_checked"] = srt
    totals = manifest.get("campaignTotals", {})
    if totals.get("scenes") != scenes:
        err(f"CINEMATICS manifest scenes {totals.get('scenes')} != checked {scenes}")
    note(f"Campaign totals in manifest: {totals}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_audio_manifest()
    check_cinematics_manifest()
    result = {
        "checkpoint": "MEDIA-02 checkpoint 11 (M8 handover/QA) - runtime re-verification",
        "base_integration": "cf17178",
        "branch": "muse/media-production-20261104",
        "verifies": "checkpoint 10 runtime delivery (RUNTIME_AUDIO_manifest_v1.json + RUNTIME_CINEMATICS_manifest_v1.json)",
        "counts": COUNTS,
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak values are NOT re-measured here; they come from checkpoints 02/04/07/08, measured from real bytes.",
            "This check verifies runtime copies still match their manifests; it does not verify the source packs (see validate_media_deliveries.py, re-run at checkpoint 11).",
            "NOT a mix PASS and NOT an ear audition; NOT a Godot wiring check (presentation adapter is Codex's work).",
        ],
    }
    print(f"counts: {json.dumps(COUNTS, indent=1)}")
    print(f"mismatches: {len(ERRORS)}")
    for e in ERRORS[:50]:
        print("  MISMATCH: " + e)
    print(f"notes: {len(NOTES)}")
    for n in NOTES[:20]:
        print("  NOTE: " + n)
    print("verdict: " + result["verdict"])
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report written: {args.out}")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
