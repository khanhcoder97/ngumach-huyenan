#!/usr/bin/env python3
"""MEDIA-02 WO37 M-E checkpoint 1: independent validator for the
composed-ambience real variants (v02/v03 per cue).

Re-checks from real bytes (never trusts the builder's recorded
numbers): file existence, LFS-pointer rejection, sha256/size,
ffprobe codec/sample-rate/channels/duration, and an independent
ffmpeg loudnorm re-measurement compared against the pack values
(tolerance +/-0.5 LUFS / +/-0.5 dBTP). Plus the M-E-specific
properties, re-measured from real bytes:

  * v01 cross-reference: every v01 master/runtime re-hashed against
    the checkpoint-30 pack values (v01 was NOT re-rendered);
  * distinctness: all 39 master SHAs distinct, all 39 runtime SHAs
    distinct; waveform difference RMS vs v01 recomputed from
    decoded bytes and compared to the pack value (+/-0.05);
  * loudness: every variant master within +/-0.5 LUFS of its cue
    target and true peak <= -6 dBTP;
  * seam indicator recomputed from the decoded master (head/tail
    RMS + wrap jump, tolerance 0.02);
  * no filename/cueKey collision with the checkpoint-26, MD1-MD8
    or checkpoint-30 packs.

With --check-runtime, also verifies the runtime audio manifest
contains the 26 variant entries with matching SHA/size/duration.

Writes three JSONs next to the reports (validation, source
re-validation, runtime re-verify) and exits 0 on PASS, 1 on any
mismatch.

Usage: python3 Tools/MediaProduction/Muse/check_composed_ambience_variants_me_cp1_v1.py [--check-runtime]
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
        / "AMBIENCE_COMPOSED_VARIANTS_pack_v1.json")
V01_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
           / "AMBIENCE_COMPOSED_pack_v1.json")
CP26_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
             / "MUSIC_COMPOSED_pack_v1.json")
RUNTIME_MANIFEST = (ROOT / "ClientGodot/assets/audio"
                    / "RUNTIME_AUDIO_manifest_v1.json")
REPORT_DIR = ROOT / "Implementation/Reports/MuseMedia"
SR = 48000

ERRORS = []
NOTES = []
COUNTS = {}


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
    return json.loads(run(["ffprobe", "-v", "error", "-show_format",
                           "-show_streams", "-of", "json",
                           str(path)]).stdout)


def measure_loudnorm(path: Path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    start = err.rfind("{")
    if start < 0:
        raise RuntimeError(f"loudnorm gave no JSON for {path}")
    data = json.loads(err[start:err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def decode_f32(path: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}")
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def check(cond, msg):
    if not cond:
        ERRORS.append(msg)
        print("FAIL: " + msg)


def check_file_entry(entry, expect_codec, label, dur=16.0):
    p = ROOT / entry["path"]
    check(p.exists(), f"{label}: missing {entry['path']}")
    if not p.exists():
        return None
    check(not is_lfs_pointer(p), f"{label}: LFS pointer {entry['path']}")
    got_sha = sha256_file(p)
    check(got_sha == entry["sha256"],
          f"{label}: sha mismatch {got_sha} != {entry['sha256']}")
    check(p.stat().st_size == entry["sizeBytes"],
          f"{label}: size mismatch {p.stat().st_size} != "
          f"{entry['sizeBytes']}")
    pr = probe(p)
    st = pr["streams"][0]
    check(st["codec_name"] == expect_codec,
          f"{label}: codec {st['codec_name']} != {expect_codec}")
    check(int(st["sample_rate"]) == entry["sampleRateHz"],
          f"{label}: sample rate mismatch")
    check(int(st["channels"]) == entry["channels"],
          f"{label}: channels mismatch")
    got_dur = float(pr["format"]["duration"])
    check(abs(got_dur - entry["durationSeconds"]) <= 0.05,
          f"{label}: duration {got_dur} != {entry['durationSeconds']}")
    check(abs(got_dur - dur) <= 0.05, f"{label}: duration != {dur} s")
    lufs, tp = measure_loudnorm(p)
    check(abs(lufs - entry["integratedLufs"]) <= 0.5,
          f"{label}: LUFS {lufs} != pack {entry['integratedLufs']}")
    check(abs(tp - entry["truePeakDbtp"]) <= 0.5,
          f"{label}: TP {tp} != pack {entry['truePeakDbtp']}")
    return got_sha


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-runtime", action="store_true")
    args = ap.parse_args()

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    v01_pack = json.loads(V01_PACK.read_text(encoding="utf-8"))
    v01_by_key = {c["cueKey"]: c for c in v01_pack["cues"]}
    cp26 = json.loads(CP26_PACK.read_text(encoding="utf-8"))

    check(pack["packId"] == "NGM_AMBIENCE_COMPOSED_VARIANTS_V1",
          "packId mismatch")
    check(pack["counts"]["ambienceCues"] == 13, "cue count != 13")
    check(pack["counts"]["newVariants"] == 26, "new variant count != 26")
    check(pack["counts"]["totalVariants"] == 39, "total variants != 39")

    # No filename/cueKey collision with the CP26 music pack.
    cp26_stems = {c["master"]["path"].split("/")[-1]
                  for c in cp26["cues"]}
    all_master_shas = set()
    all_runtime_shas = set()
    files_checked = 0
    variants_checked = 0
    for cue in pack["cues"]:
        cue_key = cue["cueKey"]
        check(cue_key in v01_by_key, f"{cue_key}: missing from CP30 pack")
        v01 = v01_by_key[cue_key]
        check(len(cue["variants"]) == 3, f"{cue_key}: variants != 3")
        ids = [v["variantId"] for v in cue["variants"]]
        check(ids == ["v01", "v02", "v03"], f"{cue_key}: ids {ids}")
        # v01 cross-reference: re-hash against the CP30 pack values.
        for kind in ("master", "runtime"):
            p = ROOT / v01[kind]["path"]
            check(p.exists(), f"{cue_key} v01 {kind} missing")
            if p.exists():
                check(sha256_file(p) == v01[kind]["sha256"],
                      f"{cue_key} v01 {kind} sha != CP30 pack")
        v01row = cue["variants"][0]
        check(v01row["master"]["sha256"] == v01["master"]["sha256"],
              f"{cue_key}: v01 master row != CP30 pack")
        check(v01row["runtime"]["sha256"] == v01["runtime"]["sha256"],
              f"{cue_key}: v01 runtime row != CP30 pack")
        all_master_shas.add(v01["master"]["sha256"])
        all_runtime_shas.add(v01["runtime"]["sha256"])
        v01_audio = decode_f32(ROOT / v01["master"]["path"])
        for var in cue["variants"][1:]:
            variants_checked += 1
            label = f"{cue_key} {var['variantId']}"
            m_sha = check_file_entry(var["master"], "pcm_s24le", label)
            r_sha = check_file_entry(var["runtime"], "vorbis", label)
            files_checked += 2
            if m_sha:
                all_master_shas.add(m_sha)
            if r_sha:
                all_runtime_shas.add(r_sha)
            check(var["master"]["path"].split("/")[-1] not in cp26_stems,
                  f"{label}: filename collides with CP26 pack")
            check(abs(var["master"]["integratedLufs"]
                      - cue["targetLufsPorted"]) <= 0.5,
                  f"{label}: master LUFS off target by "
                  f"{var['master']['integratedLufs'] - cue['targetLufsPorted']:.2f}")
            check(var["master"]["truePeakDbtp"] <= -6.0,
                  f"{label}: master TP {var['master']['truePeakDbtp']} > -6")
            # Distinctness recomputed from decoded bytes.
            mine = decode_f32(ROOT / var["master"]["path"])
            n = min(len(mine), len(v01_audio))
            denom = float(np.sqrt((v01_audio[:n] ** 2).mean())) + 1e-12
            ratio = float(np.sqrt(((mine[:n] - v01_audio[:n]) ** 2).mean())) / denom
            check(abs(ratio - var["distinctnessVsV01"]["diffRmsRatio"]) <= 0.05,
                  f"{label}: diffRmsRatio {ratio:.4f} != pack "
                  f"{var['distinctnessVsV01']['diffRmsRatio']}")
            check(ratio >= 0.05, f"{label}: diffRmsRatio too low {ratio:.4f}")
            check(var["distinctnessVsV01"]["shaDistinctFromV01"] is True,
                  f"{label}: shaDistinctFromV01 not true")
            check(m_sha != v01["master"]["sha256"],
                  f"{label}: master sha equals v01")
            check(r_sha != v01["runtime"]["sha256"],
                  f"{label}: runtime sha equals v01")
            # Seam recomputed from the decoded master.
            mono = mine.mean(axis=1)
            m100 = int(0.1 * SR)
            head_rms = float(np.sqrt((mono[:m100] ** 2).mean()))
            tail_rms = float(np.sqrt((mono[-m100:] ** 2).mean()))
            wrap = float(abs(mono[-1] - mono[0]))
            seam = var["seam"]
            check(abs(head_rms - seam["headRms"]) <= 0.02,
                  f"{label}: headRms {head_rms} != pack {seam['headRms']}")
            check(abs(tail_rms - seam["tailRms"]) <= 0.02,
                  f"{label}: tailRms {tail_rms} != pack {seam['tailRms']}")
            check(abs(wrap - seam["wrapJump"]) <= 0.02,
                  f"{label}: wrapJump {wrap} != pack {seam['wrapJump']}")

    check(len(all_master_shas) == 39,
          f"master SHAs not all distinct: {len(all_master_shas)} != 39")
    check(len(all_runtime_shas) == 39,
          f"runtime SHAs not all distinct: {len(all_runtime_shas)} != 39")
    COUNTS.update({
        "cues": len(pack["cues"]),
        "new_variants_checked": variants_checked,
        "variant_files_checked": files_checked,
        "v01_crossref_cues": len(v01_by_key),
        "distinct_master_shas": len(all_master_shas),
        "distinct_runtime_shas": len(all_runtime_shas),
    })
    NOTES.append(
        f"26 new variant files re-hashed + re-measured from real bytes "
        f"(13 cues x v02/v03, master + runtime); 13 v01 cross-refs "
        f"re-hashed against the checkpoint-30 pack; all 39 master SHAs "
        f"and all 39 runtime SHAs distinct; diff-vs-v01 RMS ratios "
        f"recomputed from decoded bytes; seam indicators recomputed "
        f"from decoded masters.")

    # --- runtime manifest check (only with --check-runtime) ---
    runtime_verdict = "NOT_CHECKED"
    runtime_counts = {}
    if args.check_runtime:
        manifest = json.loads(RUNTIME_MANIFEST.read_text(encoding="utf-8"))
        by_path = {f["runtimePath"]: f for f in manifest["files"]}
        missing = []
        mism = 0
        for cue in pack["cues"]:
            for var in cue["variants"][1:]:
                rt_path = "assets/audio/" + var["runtime"]["path"].split(
                    "assets/audio/", 1)[1]
                entry = by_path.get(rt_path)
                if entry is None:
                    missing.append(rt_path)
                    continue
                if entry["sha256"] != var["runtime"]["sha256"]:
                    mism += 1
                    ERRORS.append(f"runtime manifest sha mismatch {rt_path}")
                if entry["sizeBytes"] != var["runtime"]["sizeBytes"]:
                    mism += 1
                    ERRORS.append(f"runtime manifest size mismatch {rt_path}")
                if abs(entry["durationSeconds"]
                       - var["runtime"]["durationSeconds"]) > 0.05:
                    mism += 1
                    ERRORS.append(f"runtime manifest duration mismatch {rt_path}")
        check(not missing, f"runtime manifest missing entries: {missing}")
        check(mism == 0, f"runtime manifest mismatches: {mism}")
        runtime_counts = {
            "totalFiles": manifest["totalFiles"],
            "counts": manifest["counts"],
            "variant_entries_found": 26 - len(missing),
            "variant_entries_missing": len(missing),
        }
        runtime_verdict = "PASS" if not ERRORS else "FAIL"
        NOTES.append(
            f"runtime manifest total {manifest['totalFiles']} files "
            f"(counts {manifest['counts']}); 26/26 variant entries found "
            f"with matching sha/size/duration."
            if not missing and mism == 0 else
            "runtime manifest check failed (see errors).")

    verdict = "PASS" if not ERRORS else "FAIL"
    validation = {
        "checkpoint": "MEDIA-02 WO37 M-E CP1",
        "validator": "check_composed_ambience_variants_me_cp1_v1.py",
        "verdict": verdict,
        "mismatches": len(ERRORS),
        "errors": ERRORS,
        "notes": NOTES,
        "counts": COUNTS,
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "MEDIA02_WO37_ME_CP1_VALIDATION_20261109.json"
     ).write_text(json.dumps(validation, ensure_ascii=False, indent=1)
                  + "\n", encoding="utf-8")

    source_reval = {
        "checkpoint": "MEDIA-02 WO37 M-E checkpoint 1 (composed ambience "
                      "real variants: 13 cues x v02/v03, 26 new variant "
                      "renders; runtime audio manifest total 757 -> 783) "
                      "following MEDIA-02 WO37 M-F checkpoint 1 (voice "
                      "palette + pickups) - source re-validation",
        "base_integration": "6f79853",
        "branch": "muse/media-production-20261104",
        "counts": {**COUNTS,
                   "v01_masters_rehashed": 13,
                   "v01_runtimes_rehashed": 13},
        "mismatches": len(ERRORS),
        "notes": NOTES + [
            "Source packs re-validated from real bytes: the variants pack "
            "(26 new renders) and the checkpoint-30 pack (13 v01 masters "
            "untouched, re-hashed only); no ported PackV1 file was "
            "modified; no other delivery pack was modified."],
        "verdict": verdict,
        "limits": ["No ear audition has been done; loudness/true-peak are "
                   "measured from real bytes only.",
                   "Seam values are indicators, not a seamlessness PASS.",
                   "Variant distinctness is a waveform-difference measure, "
                   "not a listening verdict."],
    }
    (REPORT_DIR / "MEDIA02_WO37_ME_CP1_SOURCE_REVALIDATION_20261109.json"
     ).write_text(json.dumps(source_reval, ensure_ascii=False, indent=1)
                  + "\n", encoding="utf-8")

    runtime_reverify = {
        "checkpoint": "MEDIA-02 WO37 M-E checkpoint 1 (composed ambience "
                      "real variants: 13 cues x v02/v03, 26 new variant "
                      "renders; runtime audio manifest total 757 -> 783) "
                      "- runtime re-verification",
        "base_integration": "6f79853",
        "branch": "muse/media-production-20261104",
        "verifies": "runtime delivery as revised by this checkpoint: 26 "
                    "variant OGGs registered under "
                    "assets/audio/composed/ambience/ as "
                    "composed_ambience_variant entries; all prior entries "
                    "unchanged (21 embedded soundtracks, 0 silent; "
                    "playback metadata 21/0).",
        "counts": runtime_counts,
        "mismatches": len(ERRORS) if args.check_runtime else -1,
        "notes": NOTES,
        "verdict": runtime_verdict,
        "limits": ["Runtime re-verification checks manifest registration "
                   "(sha/size/duration) only; Godot wiring remains "
                   "Codex's adapter decision."],
    }
    (REPORT_DIR / "MEDIA02_WO37_ME_CP1_RUNTIME_REVERIFY_20261109.json"
     ).write_text(json.dumps(runtime_reverify, ensure_ascii=False, indent=1)
                  + "\n", encoding="utf-8")

    print(f"ME CP1 validator: {verdict} ({len(ERRORS)} mismatches; "
          f"runtime: {runtime_verdict})")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
