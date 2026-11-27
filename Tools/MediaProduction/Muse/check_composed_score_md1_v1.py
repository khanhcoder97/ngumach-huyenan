#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 1: independent validator for the MD1
score pack + coverage matrix.

Re-checks from real bytes (never trusts the builder's recorded
numbers): file existence, LFS-pointer rejection, sha256/size,
ffprobe codec/sample-rate/channels/duration, and an independent
ffmpeg loudnorm re-measurement compared against the pack values
(tolerance +/-0.5 LUFS / +/-0.5 dBTP). Also verifies the M-D coverage
matrix: all 15 WO37 slots COVERED_COMPOSED, every slot cue exists in
the checkpoint-26 pack or this MD1 pack, no cueKey/stem collision
with the checkpoint-26 or ambience packs, transitions are 6.0 s
one-shots.

Usage: python3 Tools/MediaProduction/Muse/check_composed_score_md1_v1.py [--out PATH]
Exit 0 on PASS, 1 on any mismatch.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
        / "MUSIC_SCORE_MD1_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
CP26 = (ROOT / "Implementation/Content/Audio/Deliveries"
        / "MUSIC_COMPOSED_pack_v1.json")
AMB = (ROOT / "Implementation/Content/Audio/Deliveries"
        / "AMBIENCE_COMPOSED_pack_v1.json")

ERRORS = []
NOTES = []
COUNTS = {}


def err(msg):
    ERRORS.append(msg)
    print(f"MISMATCH: {msg}", flush=True)


def note(msg):
    NOTES.append(msg)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def is_lfs_pointer(p: Path) -> bool:
    try:
        head = p.read_bytes()[:200]
    except OSError:
        return False
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n"
                           f"{r.stderr[-1000:]}")
    return r


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def measure_loudnorm(path: Path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err_txt = r.stderr
    start = err_txt.rfind("{")
    if start < 0:
        raise RuntimeError(f"loudnorm gave no JSON for {path}")
    data = json.loads(err_txt[start:err_txt.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def check_side(entry: dict, label: str, want_codec: str):
    p = ROOT / entry["path"]
    if not p.exists():
        err(f"{label}: missing file {entry['path']}")
        return
    if is_lfs_pointer(p):
        err(f"{label}: file is an LFS pointer {entry['path']}")
        return
    got_sha = sha256_file(p)
    if got_sha != entry["sha256"]:
        err(f"{label}: sha mismatch {got_sha} != {entry['sha256']}")
    got_size = p.stat().st_size
    if got_size != entry["sizeBytes"]:
        err(f"{label}: size mismatch {got_size} != "
            f"{entry['sizeBytes']}")
    pr = probe(p)
    stream = pr["streams"][0]
    if stream["codec_name"] != want_codec:
        err(f"{label}: codec {stream['codec_name']} != {want_codec}")
    if int(stream["sample_rate"]) != entry["sampleRateHz"]:
        err(f"{label}: sample_rate {stream['sample_rate']} != "
            f"{entry['sampleRateHz']}")
    if int(stream["channels"]) != entry["channels"]:
        err(f"{label}: channels {stream['channels']} != "
            f"{entry['channels']}")
    dur = float(pr["format"]["duration"])
    if abs(dur - entry["durationSeconds"]) > 0.02:
        err(f"{label}: duration {dur} != {entry['durationSeconds']}")
    lufs, tp = measure_loudnorm(p)
    if abs(lufs - entry["integratedLufs"]) > 0.5:
        err(f"{label}: loudness re-measured {lufs:.2f} LUFS != pack "
            f"{entry['integratedLufs']}")
    if abs(tp - entry["truePeakDbtp"]) > 0.5:
        err(f"{label}: true peak re-measured {tp:.2f} dBTP != pack "
            f"{entry['truePeakDbtp']}")
    note(f"{label}: sha/size/codec/duration/loudness re-verified "
         f"({lufs:.2f} LUFS / {tp:.2f} dBTP)")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    if pack["counts"] != {"music": 7, "transitions": 3, "total": 10}:
        err(f"MD1 pack counts drift: {pack['counts']}")
    if pack.get("packId") != "NGM_MUSIC_SCORE_MD1_V1":
        err(f"MD1 packId drift: {pack.get('packId')}")
    COUNTS["md1_cues"] = len(pack["cues"])

    cp26 = json.loads(CP26.read_text(encoding="utf-8"))
    amb = json.loads(AMB.read_text(encoding="utf-8"))
    known_keys = {c["cueKey"] for c in cp26["cues"]} | \
        {c["cueKey"] for c in amb["cues"]}
    known_stems = set()
    for c in cp26["cues"] + amb["cues"]:
        known_stems.add(Path(c["master"]["path"]).stem)

    total_files = 0
    for cue in pack["cues"]:
        key = cue["cueKey"]
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"MD1 {key}: provenance missing/drift")
        if key in known_keys:
            err(f"MD1 {key}: cueKey collides with an earlier pack")
        stem = Path(cue["master"]["path"]).stem
        if stem in known_stems:
            err(f"MD1 {key}: master stem collides with an earlier pack")
        if cue["kind"] == "MUSIC":
            if not cue.get("loop"):
                err(f"MD1 {key}: music cue must loop")
            if cue["master"]["codec"] != "pcm_s24le":
                err(f"MD1 {key}: master codec "
                    f"{cue['master']['codec']} != pcm_s24le")
            if not (-23.5 <= cue["master"]["integratedLufs"] <= -20.5):
                err(f"MD1 {key}: master LUFS "
                    f"{cue['master']['integratedLufs']} outside "
                    "[-23.5, -20.5]")
            if cue["master"]["truePeakDbtp"] > -6.0:
                err(f"MD1 {key}: master TP "
                    f"{cue['master']['truePeakDbtp']} > -6.0 dBTP")
            if "wrapJumpRaw" not in cue.get("seam", {}):
                err(f"MD1 {key}: seam block missing wrapJumpRaw")
        elif cue["kind"] == "TRANSITION":
            if cue.get("loop"):
                err(f"MD1 {key}: transition must not loop")
            if abs(cue["master"]["durationSeconds"] - 6.0) > 0.02:
                err(f"MD1 {key}: transition duration "
                    f"{cue['master']['durationSeconds']} != 6.0 s")
            if not (-27.0 <= cue["master"]["integratedLufs"] <= -23.0):
                err(f"MD1 {key}: master LUFS "
                    f"{cue['master']['integratedLufs']} outside "
                    "[-27.0, -23.0]")
            if cue["master"]["truePeakDbtp"] > -5.0:
                err(f"MD1 {key}: master TP "
                    f"{cue['master']['truePeakDbtp']} > -5.0 dBTP")
        else:
            err(f"MD1 {key}: unknown kind {cue.get('kind')}")
        check_side(cue["master"], f"MD1 {key}/master", "pcm_s24le")
        check_side(cue["runtime"], f"MD1 {key}/runtime", "vorbis")
        total_files += 2
    COUNTS["md1_files_checked"] = total_files

    # Coverage matrix.
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    if cov.get("coverageId") != "NGM_MUSIC_SCORE_MD_COVERAGE_V1":
        err(f"coverageId drift: {cov.get('coverageId')}")
    if cov["slotsTotal"] != 15 or cov["slotsCoveredComposed"] != 15 \
            or cov["slotsGap"] != 0:
        err(f"coverage totals drift: {cov['slotsTotal']} slots, "
            f"{cov['slotsCoveredComposed']} covered, "
            f"{cov['slotsGap']} gaps")
    pack_keys = {c["cueKey"] for c in pack["cues"]}
    cp26_keys = {c["cueKey"] for c in cp26["cues"]}
    for slot in cov["slots"]:
        if slot["status"] != "COVERED_COMPOSED":
            err(f"coverage slot {slot['slot']}: status "
                f"{slot['status']} != COVERED_COMPOSED")
        cue = slot["composedCueKey"]
        if cue not in pack_keys and cue not in cp26_keys:
            err(f"coverage slot {slot['slot']}: cue {cue} exists in "
                "neither the MD1 pack nor the checkpoint-26 pack")
        if slot["composedPack"] not in (
                "MUSIC_SCORE_MD1_pack_v1", "MUSIC_COMPOSED_pack_v1"):
            err(f"coverage slot {slot['slot']}: pack "
                f"{slot['composedPack']} unknown")
    md1_trans = sorted(c["cueKey"] for c in pack["cues"]
                       if c["kind"] == "TRANSITION")
    if cov.get("transitions") != md1_trans:
        err(f"coverage transitions {cov.get('transitions')} != pack "
            f"{md1_trans}")
    if not cov.get("openForMdCp2"):
        err("coverage openForMdCp2 is empty")
    COUNTS["coverage_slots"] = len(cov["slots"])
    note(f"coverage verified: {cov['slotsCoveredComposed']}/"
         f"{cov['slotsTotal']} slots covered, 0 gaps, "
         f"{len(md1_trans)} transitions")

    result = {
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 1 (whole-game score "
                      "batch 1: 7 missing core cues + 3 transition "
                      "bridges; 15/15 M-D slots covered, 0 gaps; "
                      "runtime audio manifest total 627 -> 637)",
        "base_integration": "6f79853",
        "branch": "muse/media-production-20261104",
        "counts": COUNTS,
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak are re-measured here from real bytes "
            "(ffmpeg loudnorm) and compared to the pack within +/-0.5; "
            "they are not a mix PASS.",
            "Loop seams are recorded indicators (wrapJump after the "
            "disclosed 0.25 s end-landing loop construction, "
            "wrapJumpRaw before it), not a seamlessness PASS.",
            "No ear audition of the 10 MD1 cues or their loop seams; "
            "audition status NOT_AUDITIONED.",
            "Intro/outro segments, stems and phase-layer candidates "
            "remain open for M-D checkpoint 2 (see coverage "
            "openForMdCp2).",
        ],
    }
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"wrote {args.out}", flush=True)
    print(f"MD1 validation: {result['verdict']} "
          f"({len(ERRORS)} mismatches, {total_files} files, "
          f"{COUNTS['coverage_slots']} coverage slots)", flush=True)
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
