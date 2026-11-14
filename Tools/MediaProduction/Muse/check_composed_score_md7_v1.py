#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 7: independent validator for the MD7
pack (phase layers: thang_long intensity, tran_son intensity,
bach_uyen intensity, rift_finale intensity, quiet_discovery
intensity) + coverage matrix.

Re-checks from real bytes (never trusts the builder's recorded
numbers): file existence, LFS-pointer rejection, sha256/size,
ffprobe codec/sample-rate/channels/duration, and an independent
ffmpeg loudnorm re-measurement compared against the pack values
(tolerance +/-0.5 LUFS / +/-0.5 dBTP). Plus the MD7-specific
property, re-measured from real bytes:

  * layer combined level: base master + layer master summed from
    real bytes, loudnorm re-measured against the pack's recorded
    combined values (+/-0.5), combined true peak <= -3 dBTP.

Also verifies the M-D coverage matrix (15/15 slots, MD7 block,
openForMdCp8) and that no cueKey/stem collides with the
checkpoint-26, ambience, MD1, MD2, MD3, MD4, MD5 or MD6 packs.

Usage: python3 Tools/MediaProduction/Muse/check_composed_score_md7_v1.py [--out PATH]
Exit 0 on PASS, 1 on any mismatch.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
        / "MUSIC_SCORE_MD7_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
MD1 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD1_pack_v1.json")
MD2 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD2_pack_v1.json")
MD3 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD3_pack_v1.json")
MD4 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD4_pack_v1.json")
MD5 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD5_pack_v1.json")
MD6 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD6_pack_v1.json")
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


def decode_f32(path: Path):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def measure_track_loudnorm(track, tag):
    tmp = Path.home() / "workspace" / "tmp" / f"md7_validate_{tag}.wav"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    raw = np.ascontiguousarray(track, dtype="<f4").tobytes()
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le",
                        "-ar", "48000", "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s16le", str(tmp)],
                       input=raw, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-1000:])
    return measure_loudnorm(tmp)


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
    if entry["integratedLufs"] is None:
        if lufs != float("-inf"):
            err(f"{label}: expected digital silence, re-measured "
                f"{lufs:.2f} LUFS")
        else:
            note(f"{label}: digital silence re-verified")
        return
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
    if pack["counts"] != {"intro": 0, "outro": 0, "stems": 0,
                          "layers": 5, "total": 5}:
        err(f"MD7 pack counts drift: {pack['counts']}")
    if pack.get("packId") != "NGM_MUSIC_SCORE_MD7_V1":
        err(f"MD7 packId drift: {pack.get('packId')}")
    COUNTS["md7_cues"] = len(pack["cues"])

    md1 = json.loads(MD1.read_text(encoding="utf-8"))
    md1_by_key = {c["cueKey"]: c for c in md1["cues"]}
    md2 = json.loads(MD2.read_text(encoding="utf-8"))
    md3 = json.loads(MD3.read_text(encoding="utf-8"))
    md4 = json.loads(MD4.read_text(encoding="utf-8"))
    md5 = json.loads(MD5.read_text(encoding="utf-8"))
    md6 = json.loads(MD6.read_text(encoding="utf-8"))
    cp26 = json.loads(CP26.read_text(encoding="utf-8"))
    cp26_by_key = {c["cueKey"]: c for c in cp26["cues"]}
    amb = json.loads(AMB.read_text(encoding="utf-8"))
    known_keys = ({c["cueKey"] for c in cp26["cues"]}
                  | {c["cueKey"] for c in amb["cues"]}
                  | set(md1_by_key)
                  | {c["cueKey"] for c in md2["cues"]}
                  | {c["cueKey"] for c in md3["cues"]}
                  | {c["cueKey"] for c in md4["cues"]}
                  | {c["cueKey"] for c in md5["cues"]}
                  | {c["cueKey"] for c in md6["cues"]})
    known_stems = set()
    for c in (cp26["cues"] + amb["cues"] + md1["cues"] + md2["cues"]
              + md3["cues"] + md4["cues"] + md5["cues"] + md6["cues"]):
        known_stems.add(Path(c["master"]["path"]).stem)

    total_files = 0
    for cue in pack["cues"]:
        key = cue["cueKey"]
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"MD7 {key}: provenance missing/drift")
        if key in known_keys:
            err(f"MD7 {key}: cueKey collides with an earlier pack")
        stem = Path(cue["master"]["path"]).stem
        if stem in known_stems:
            err(f"MD7 {key}: master stem collides with an earlier pack")
        parent = cue.get("parentCueKey")
        base = cp26_by_key.get(parent) or md1_by_key.get(parent)
        if base is None:
            err(f"MD7 {key}: parentCueKey {parent} unknown")
            continue
        if cue["kind"] != "LAYER":
            err(f"MD7 {key}: unknown kind {cue.get('kind')} "
                "(MD7 is layers only)")
            continue
        if cue.get("loop") is not True:
            err(f"MD7 {key}: layer must loop")
        if abs(cue["master"]["durationSeconds"]
               - base["master"]["durationSeconds"]) > 0.02:
            err(f"MD7 {key}: layer duration != parent duration")
        if not (-27.0 <= cue["master"]["integratedLufs"] <= -23.0):
            err(f"MD7 {key}: master LUFS "
                f"{cue['master']['integratedLufs']} outside "
                "[-27.0, -23.0]")
        if cue["master"]["truePeakDbtp"] > -5.0:
            err(f"MD7 {key}: master TP "
                f"{cue['master']['truePeakDbtp']} > -5.0 dBTP")
        comb = cue.get("combinedWithBase", {})
        base_tr = decode_f32(ROOT / base["master"]["path"])
        layer_tr = decode_f32(ROOT / cue["master"]["path"])
        if base_tr.shape != layer_tr.shape:
            err(f"MD7 {key}: layer shape {layer_tr.shape} != "
                f"base shape {base_tr.shape}")
        else:
            c_lufs, c_tp = measure_track_loudnorm(
                base_tr + layer_tr, Path(cue["master"]["path"]).stem)
            if abs(c_lufs - comb.get("integratedLufs", 999)) > 0.5:
                err(f"MD7 {key}: combined LUFS re-measured "
                    f"{c_lufs:.2f} != pack "
                    f"{comb.get('integratedLufs')}")
            if abs(c_tp - comb.get("truePeakDbtp", 999)) > 0.5:
                err(f"MD7 {key}: combined TP re-measured "
                    f"{c_tp:.2f} != pack {comb.get('truePeakDbtp')}")
            if c_tp > -3.0:
                err(f"MD7 {key}: combined TP {c_tp:.2f} > "
                    "-3.0 dBTP")
            note(f"MD7 {key}: combined base+layer re-measured "
                 f"{c_lufs:.2f} LUFS / {c_tp:.2f} dBTP")
        if "wrapJumpRaw" not in cue.get("seam", {}):
            err(f"MD7 {key}: seam block missing wrapJumpRaw")
        check_side(cue["master"], f"MD7 {key}/master", "pcm_s24le")
        check_side(cue["runtime"], f"MD7 {key}/runtime", "vorbis")
        total_files += 2
    COUNTS["md7_files_checked"] = total_files

    # Coverage matrix.
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    if cov.get("coverageId") != "NGM_MUSIC_SCORE_MD_COVERAGE_V1":
        err(f"coverageId drift: {cov.get('coverageId')}")
    if cov["slotsTotal"] != 15 or cov["slotsCoveredComposed"] != 15 \
            or cov["slotsGap"] != 0:
        err(f"coverage totals drift: {cov['slotsTotal']} slots, "
            f"{cov['slotsCoveredComposed']} covered, "
            f"{cov['slotsGap']} gaps")
    md7cov = cov.get("md7", {})
    if md7cov.get("pack") != "MUSIC_SCORE_MD7_pack_v1" or \
            md7cov.get("layers") != 5:
        err(f"coverage md7 block drift: {md7cov}")
    if not cov.get("openForMdCp8"):
        err("coverage openForMdCp8 is empty")
    if not cov.get("openForMdCp7"):
        err("coverage openForMdCp7 is empty (MD6 validator compat)")
    if not cov.get("openForMdCp6"):
        err("coverage openForMdCp6 is empty (MD5 validator compat)")
    if not cov.get("openForMdCp5"):
        err("coverage openForMdCp5 is empty (MD4 validator compat)")
    if not cov.get("openForMdCp4"):
        err("coverage openForMdCp4 is empty (MD3 validator compat)")
    if not cov.get("openForMdCp3"):
        err("coverage openForMdCp3 is empty (MD2 validator compat)")
    if not cov.get("openForMdCp2"):
        err("coverage openForMdCp2 is empty (MD1 validator compat)")
    COUNTS["coverage_slots"] = len(cov["slots"])
    note(f"coverage verified: {cov['slotsCoveredComposed']}/"
         f"{cov['slotsTotal']} slots covered, 0 gaps, md7 5 layers")

    result = {
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 7 (phase layers: "
                      "thang_long intensity, tran_son intensity, "
                      "bach_uyen intensity, rift_finale intensity, "
                      "quiet_discovery intensity; runtime audio manifest "
                      "total 731 -> 736)",
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
            "No ear audition of the MD7 layers or their loop seams; "
            "audition status NOT_AUDITIONED.",
        ],
    }
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"wrote {args.out}", flush=True)
    print(f"MD7 validation: {result['verdict']} "
          f"({len(ERRORS)} mismatches, {total_files} files)", flush=True)
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
