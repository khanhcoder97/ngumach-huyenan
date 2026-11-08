#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 2: independent validator for the MD2
pack (intros/outros + stems + phase layers) + coverage matrix.

Re-checks from real bytes (never trusts the builder's recorded
numbers): file existence, LFS-pointer rejection, sha256/size,
ffprobe codec/sample-rate/channels/duration, and an independent
ffmpeg loudnorm re-measurement compared against the pack values
(tolerance +/-0.5 LUFS / +/-0.5 dBTP). Plus the two MD2-specific
properties, both re-measured from real bytes:

  * stem exact-sum: lead + padbass + percussion masters summed from
    real bytes must equal the shipped MD1 parent master within
    24-bit quantisation (max abs diff <= 5e-7, about 2 LSB);
  * layer combined level: base master + layer master summed from
    real bytes, loudnorm re-measured against the pack's recorded
    combined values (+/-0.5), combined true peak <= -3 dBTP.

Also verifies the M-D coverage matrix (15/15 slots, MD2 block,
openForMdCp3) and that no cueKey/stem collides with the
checkpoint-26, ambience or MD1 packs.

Usage: python3 Tools/MediaProduction/Muse/check_composed_score_md2_v1.py [--out PATH]
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
        / "MUSIC_SCORE_MD2_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
MD1 = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "MUSIC_SCORE_MD1_pack_v1.json")
CP26 = (ROOT / "Implementation/Content/Audio/Deliveries"
        / "MUSIC_COMPOSED_pack_v1.json")
AMB = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "AMBIENCE_COMPOSED_pack_v1.json")

ERRORS = []
NOTES = []
COUNTS = {}
SUM_THRESHOLD = 5e-7


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
    tmp = Path(f"/tmp/md2_validate_{tag}.wav")
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
        # Digital silence by design (tragedy percussion stem):
        # loudnorm is undefined (-inf); assert the silence instead.
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
    if pack["counts"] != {"intro": 7, "outro": 7, "stems": 21,
                          "layers": 2, "total": 37}:
        err(f"MD2 pack counts drift: {pack['counts']}")
    if pack.get("packId") != "NGM_MUSIC_SCORE_MD2_V1":
        err(f"MD2 packId drift: {pack.get('packId')}")
    COUNTS["md2_cues"] = len(pack["cues"])

    md1 = json.loads(MD1.read_text(encoding="utf-8"))
    md1_by_key = {c["cueKey"]: c for c in md1["cues"]}
    cp26 = json.loads(CP26.read_text(encoding="utf-8"))
    amb = json.loads(AMB.read_text(encoding="utf-8"))
    known_keys = {c["cueKey"] for c in cp26["cues"]} | \
        {c["cueKey"] for c in amb["cues"]} | set(md1_by_key)
    known_stems = set()
    for c in cp26["cues"] + amb["cues"] + md1["cues"]:
        known_stems.add(Path(c["master"]["path"]).stem)

    total_files = 0
    stems_by_parent = {}
    for cue in pack["cues"]:
        key = cue["cueKey"]
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"MD2 {key}: provenance missing/drift")
        if key in known_keys:
            err(f"MD2 {key}: cueKey collides with an earlier pack")
        stem = Path(cue["master"]["path"]).stem
        if stem in known_stems:
            err(f"MD2 {key}: master stem collides with an earlier pack")
        parent = cue.get("parentCueKey")
        cp26_keys = {c["cueKey"] for c in cp26["cues"]}
        if not parent or (parent not in md1_by_key
                         and parent not in cp26_keys):
            err(f"MD2 {key}: parentCueKey {parent} unknown")
        if cue["kind"] == "STEM":
            stems_by_parent.setdefault(parent, []).append(cue)
            if cue.get("loop") is not True:
                err(f"MD2 {key}: stem must loop")
            # Stems only exist for the 7 MD1 parents.
            if abs(cue["master"]["durationSeconds"]
                   - md1_by_key[parent]["master"]["durationSeconds"]) \
                    > 0.02:
                err(f"MD2 {key}: stem duration != parent duration")
            if cue.get("group") not in ("lead", "padbass",
                                         "percussion"):
                err(f"MD2 {key}: unknown stem group "
                    f"{cue.get('group')}")
        elif cue["kind"] in ("INTRO", "OUTRO"):
            if cue.get("loop"):
                err(f"MD2 {key}: intro/outro must not loop")
            bpm = md1_by_key[parent]["composition"]["tempoBpm"]
            want_dur = 480.0 / bpm  # 2 bars
            if abs(cue["master"]["durationSeconds"] - want_dur) > 0.02:
                err(f"MD2 {key}: duration "
                    f"{cue['master']['durationSeconds']} != 2 bars "
                    f"({want_dur:.4f} s at {bpm} bpm)")
            if not (-23.5 <= cue["master"]["integratedLufs"] <= -20.5):
                err(f"MD2 {key}: master LUFS "
                    f"{cue['master']['integratedLufs']} outside "
                    "[-23.5, -20.5]")
            if cue["master"]["truePeakDbtp"] > -6.0:
                err(f"MD2 {key}: master TP "
                    f"{cue['master']['truePeakDbtp']} > -6.0 dBTP")
        elif cue["kind"] == "LAYER":
            if cue.get("loop") is not True:
                err(f"MD2 {key}: layer must loop")
            base = (md1_by_key.get(parent)
                    or [c for c in cp26["cues"]
                        if c["cueKey"] == parent][0])
            if abs(cue["master"]["durationSeconds"]
                   - base["master"]["durationSeconds"]) > 0.02:
                err(f"MD2 {key}: layer duration != parent duration")
            if not (-27.0 <= cue["master"]["integratedLufs"] <= -23.0):
                err(f"MD2 {key}: master LUFS "
                    f"{cue['master']['integratedLufs']} outside "
                    "[-27.0, -23.0]")
            if cue["master"]["truePeakDbtp"] > -5.0:
                err(f"MD2 {key}: master TP "
                    f"{cue['master']['truePeakDbtp']} > -5.0 dBTP")
            comb = cue.get("combinedWithBase", {})
            base_tr = decode_f32(ROOT / base["master"]["path"])
            layer_tr = decode_f32(ROOT / cue["master"]["path"])
            if base_tr.shape != layer_tr.shape:
                err(f"MD2 {key}: layer shape {layer_tr.shape} != "
                    f"base shape {base_tr.shape}")
            else:
                c_lufs, c_tp = measure_track_loudnorm(
                    base_tr + layer_tr, Path(cue["master"]["path"]).stem)
                if abs(c_lufs - comb.get("integratedLufs", 999)) > 0.5:
                    err(f"MD2 {key}: combined LUFS re-measured "
                        f"{c_lufs:.2f} != pack "
                        f"{comb.get('integratedLufs')}")
                if abs(c_tp - comb.get("truePeakDbtp", 999)) > 0.5:
                    err(f"MD2 {key}: combined TP re-measured "
                        f"{c_tp:.2f} != pack {comb.get('truePeakDbtp')}")
                if c_tp > -3.0:
                    err(f"MD2 {key}: combined TP {c_tp:.2f} > "
                        "-3.0 dBTP")
                note(f"MD2 {key}: combined base+layer re-measured "
                     f"{c_lufs:.2f} LUFS / {c_tp:.2f} dBTP")
            if "wrapJumpRaw" not in cue.get("seam", {}):
                err(f"MD2 {key}: seam block missing wrapJumpRaw")
        else:
            err(f"MD2 {key}: unknown kind {cue.get('kind')}")
        check_side(cue["master"], f"MD2 {key}/master", "pcm_s24le")
        check_side(cue["runtime"], f"MD2 {key}/runtime", "vorbis")
        total_files += 2
    COUNTS["md2_files_checked"] = total_files

    # Stem exact-sum: 3 stems per MD1 parent, summed from real bytes.
    for sg in pack.get("stemGroups", []):
        parent = sg["parentCueKey"]
        cues = stems_by_parent.get(parent, [])
        if sorted(c["group"] for c in cues) != ["lead", "padbass",
                                                 "percussion"]:
            err(f"MD2 stem group {parent}: groups "
                f"{sorted(c['group'] for c in cues)} != 3 expected")
            continue
        ref = decode_f32(ROOT / md1_by_key[parent]["master"]["path"])
        total = None
        for c in cues:
            s = decode_f32(ROOT / c["master"]["path"])
            if s.shape != ref.shape:
                err(f"MD2 stem {c['cueKey']}: shape {s.shape} != "
                    f"parent {ref.shape}")
                total = None
                break
            total = s if total is None else total + s
        if total is None:
            continue
        diff = total - ref
        max_diff = float(np.max(np.abs(diff)))
        rms_diff = float(np.sqrt((diff ** 2).mean()))
        if max_diff > SUM_THRESHOLD:
            err(f"MD2 stem-sum {parent}: max abs diff {max_diff:.2e} "
                f"> {SUM_THRESHOLD:.0e}")
        if abs(max_diff - sg.get("maxAbsDiff", -1)) > 1e-9:
            err(f"MD2 stem-sum {parent}: re-measured max diff "
                f"{max_diff:.2e} != pack {sg.get('maxAbsDiff')}")
        note(f"MD2 stem-sum {parent}: max abs diff {max_diff:.2e}, "
             f"rms {rms_diff:.2e} (<= {SUM_THRESHOLD:.0e})")
    COUNTS["stem_groups_checked"] = len(pack.get("stemGroups", []))

    # Tragedy percussion stem must be digital silence by design.
    for cue in pack["cues"]:
        if cue["cueKey"] == "MUSIC/tragedy_stem_percussion":
            sig = decode_f32(ROOT / cue["master"]["path"])
            if float(np.max(np.abs(sig))) != 0.0:
                err("MD2 tragedy percussion stem is not silent")
            else:
                note("MD2 tragedy percussion stem verified silent")

    # Reference reproduction: every MD1 master reproduced bit-exact.
    repro = pack.get("referenceReproduction", [])
    if len(repro) != 7:
        err(f"MD2 referenceReproduction entries {len(repro)} != 7")
    for r in repro:
        if not r.get("match"):
            err(f"MD2 reference {r['cueKey']}: reproduced sha != "
                "MD1 master sha")
        if r.get("reproducedSha256") != r.get("md1MasterSha256"):
            err(f"MD2 reference {r['cueKey']}: sha fields disagree")
        if r.get("md1MasterSha256") != \
                md1_by_key[r["cueKey"]]["master"]["sha256"]:
            err(f"MD2 reference {r['cueKey']}: recorded MD1 sha != "
                "MD1 pack")
    COUNTS["reference_reproductions"] = len(repro)

    # Coverage matrix.
    cov = json.loads(COVERAGE.read_text(encoding="utf-8"))
    if cov.get("coverageId") != "NGM_MUSIC_SCORE_MD_COVERAGE_V1":
        err(f"coverageId drift: {cov.get('coverageId')}")
    if cov["slotsTotal"] != 15 or cov["slotsCoveredComposed"] != 15 \
            or cov["slotsGap"] != 0:
        err(f"coverage totals drift: {cov['slotsTotal']} slots, "
            f"{cov['slotsCoveredComposed']} covered, "
            f"{cov['slotsGap']} gaps")
    md2cov = cov.get("md2", {})
    if md2cov.get("pack") != "MUSIC_SCORE_MD2_pack_v1" or \
            (md2cov.get("intros"), md2cov.get("outros"),
             md2cov.get("stems"), md2cov.get("layers")) != (7, 7, 21, 2):
        err(f"coverage md2 block drift: {md2cov}")
    if not cov.get("openForMdCp3"):
        err("coverage openForMdCp3 is empty")
    if not cov.get("openForMdCp2"):
        err("coverage openForMdCp2 is empty (MD1 validator compat)")
    COUNTS["coverage_slots"] = len(cov["slots"])
    note(f"coverage verified: {cov['slotsCoveredComposed']}/"
         f"{cov['slotsTotal']} slots covered, 0 gaps, md2 7/7/21/2")

    result = {
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 2 (intro/outro + "
                      "stems + phase layers for the 7 MD1 score cues; "
                      "runtime audio manifest total 637 -> 674)",
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
            "Stem-sum is a byte property (max abs diff <= 5e-7, about "
            "2 LSB of 24-bit audio), not a listening judgement.",
            "No ear audition of the MD2 intros/outros/stems/layers or "
            "their loop seams; audition status NOT_AUDITIONED.",
            "Intro/outro segments and stems for the 9 checkpoint-26 "
            "cues remain open for a later checkpoint, if the director "
            "wants them (see coverage openForMdCp3).",
        ],
    }
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
        print(f"wrote {args.out}", flush=True)
    print(f"MD2 validation: {result['verdict']} "
          f"({len(ERRORS)} mismatches, {total_files} files, "
          f"{COUNTS['stem_groups_checked']} stem groups)", flush=True)
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
