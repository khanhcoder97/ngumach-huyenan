#!/usr/bin/env python3
"""Independent validator for MEDIA-02 WO37 M-D CP10 (ear-audition pack v2 delta).

Re-measures all 58 delta items from real bytes on disk (own probe code,
not the builder's), and checks:
  - sha256 / size / duration / codec / sample rate / LUFS / TP match the pack
  - playlists 08 and 09 list exactly their section's files, in order, with
    matching item ids
  - the 18 SFX items are covered by the two already-delivered SFX audition
    playlists (read-only check; those files are NOT modified here)
  - every supersedes / variantOf id exists in EAR_AUDITION_PACK_v1.json
    (v1 bytes are never re-hashed: only the v1 JSON is read)
  - counts / totals / unique ids / priorities
  - no ClientGodot/ path is touched by this checkpoint (git status)

Usage: python3 Tools/MediaProduction/Muse/check_ear_audition_pack_cp10_v1.py
Output: Implementation/Reports/MuseMedia/MEDIA02_WO37_MD_CP10_VALIDATION_20261112.json
Exit 0 only when checksPassed == checksTotal and failures is empty.
"""
import hashlib
import json
import math
import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
PACK = REPORTS / "EAR_AUDITION_PACK_v2_DELTA.json"
TOL = 0.05

CHECKS = {"total": 0, "passed": 0, "failures": []}


def check(ok: bool, label: str):
    CHECKS["total"] += 1
    if ok:
        CHECKS["passed"] += 1
    else:
        CHECKS["failures"].append(label)


def pooled_rms_dbfs(p: Path) -> float:
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p),
         "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
        capture_output=True, check=True).stdout
    n = len(raw) // 4
    xs = struct.unpack(f"<{n}f", raw)
    rms = math.sqrt(sum(x * x for x in xs) / n)
    return round(20 * math.log10(rms), 2)


def probe(p: Path) -> dict:
    if p.read_bytes()[:40].startswith(b"version https://git-lfs"):
        raise SystemExit(f"LFS pointer, not real bytes: {p}")
    data = p.read_bytes()
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,sample_rate,channels",
         "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    stream = j["streams"][0]
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    loud = json.loads("{" + err.split("{", 1)[1].rsplit("}", 1)[0] + "}")
    lufs = None if loud["input_i"] == "-inf" else float(loud["input_i"])
    return {
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": round(float(j["format"]["duration"]), 4),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": lufs,
        "true_peak_dbtp": float(loud["input_tp"]),
        "rms_dbfs": pooled_rms_dbfs(p) if lufs is None else None,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> None:
    pack = json.loads(PACK.read_text())
    v1 = json.loads((REPORTS / "EAR_AUDITION_PACK_v1.json").read_text())
    v1_ids = {it["id"] for sec in v1["sections"].values() for it in sec}

    check(pack["packId"] == "NGM_EAR_AUDITION_PACK_V2_DELTA", "packId")
    check(pack["totalItems"] == 58, "totalItems == 58")
    check(pack["v1TotalItems"] == 196, "v1TotalItems == 196")
    check(pack["combinedTotalItems"] == 254, "combinedTotalItems == 254")
    check(pack["counts"] == {"mixesV2": 14, "ambienceVariants": 26, "sfxDrafts": 18},
          "counts == 14/26/18")

    all_items = []
    for sec_name, items in pack["sections"].items():
        check(len(items) == pack["counts"][sec_name], f"section {sec_name} length")
        for it in items:
            all_items.append((sec_name, it))
    ids = [it["id"] for _, it in all_items]
    check(len(set(ids)) == len(ids) == 58, "58 unique item ids")
    check(all(it["priority"] in ("P0", "P1", "P2") for _, it in all_items),
          "priorities in P0/P1/P2")
    check(all(it.get("question") for _, it in all_items), "every item has a question")
    check(all(it.get("source") for _, it in all_items), "every item has a source")

    total_dur = 0.0
    for sec_name, it in all_items:
        p = ROOT / it["file"]
        check(p.is_file(), f"{it['id']}: file exists")
        if not p.is_file():
            continue
        m = probe(p)
        check(m["sha256"] == it["sha256"], f"{it['id']}: sha256")
        check(m["size_bytes"] == it["sizeBytes"], f"{it['id']}: size")
        check(abs(m["duration_s"] - it["durationSeconds"]) <= 0.005,
              f"{it['id']}: duration")
        check(m["codec"] == it["codec"], f"{it['id']}: codec")
        check(m["sample_rate_hz"] == 48000, f"{it['id']}: 48kHz")
        if it["lufs"] is None:
            check(m["integrated_lufs"] is None, f"{it['id']}: LUFS undefined as recorded")
            check(m["rms_dbfs"] is not None and it.get("rmsDbfs") is not None
                  and abs(m["rms_dbfs"] - it["rmsDbfs"]) <= TOL,
                  f"{it['id']}: pooled RMS")
        else:
            check(m["integrated_lufs"] is not None
                  and abs(m["integrated_lufs"] - it["lufs"]) <= TOL, f"{it['id']}: LUFS")
        check(abs(m["true_peak_dbtp"] - it["truePeakDbtp"]) <= TOL, f"{it['id']}: TP")
        if it.get("supersedes"):
            check(it["supersedes"] in v1_ids, f"{it['id']}: supersedes in v1 pack")
        if it.get("variantOf"):
            check(it["variantOf"] in v1_ids, f"{it['id']}: variantOf in v1 pack")
        total_dur += it["durationSeconds"]
    check(abs(total_dur - pack["totalDurationSeconds"]) < 0.01, "total duration sum")

    # ---- playlists 08 / 09: exact file set, in order, ids match ----
    def playlist_ok(fname, items):
        lines = (REPORTS / fname).read_text(encoding="utf-8").splitlines()
        paths = [ln for ln in lines if ln.startswith("../../../")]
        extinf = [ln for ln in lines if ln.startswith("#EXTINF")]
        check(len(paths) == len(items), f"{fname}: path count")
        check(len(extinf) == len(items), f"{fname}: EXTINF count")
        for ln, it in zip(paths, items):
            check(ln == f"../../../{it['file']}", f"{fname}: path {it['id']}")
        for ln, it in zip(extinf, items):
            check(ln.startswith(f"#EXTINF:-1,{it['id']} "), f"{fname}: EXTINF {it['id']}")

    playlist_ok("ear_audition_08_v2mixes_playlist.txt", pack["sections"]["mixesV2"])
    playlist_ok("ear_audition_09_ambience_variants_playlist.txt",
                pack["sections"]["ambienceVariants"])

    # ---- SFX items covered by the already-delivered SFX playlists (read-only) ----
    sfx_covered = set()
    for rel in ("Implementation/Content/Audio/Deliveries/"
                "SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt",
                "Implementation/Content/Audio/Deliveries/"
                "SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt"):
        txt = (ROOT / rel).read_text(encoding="utf-8")
        for ln in txt.splitlines():
            ln = ln.strip()
            if ln.startswith("../") or ln.startswith("Art_Source/"):
                # playlists sit 4 levels deep; strip leading ../ to repo-relative
                sfx_covered.add(re.sub(r"^(?:\.\./)+", "", ln))
    for it in pack["sections"]["sfxDrafts"]:
        check(it["file"] in sfx_covered, f"{it['id']}: covered by delivered SFX playlist")

    # ---- priority queue + core-pass update reference real items ----
    pq_ids = {q["id"] for q in pack["priorityQueue"]}
    check(pq_ids == {"MIX2-001", "MIX2-002", "MIX2-003", "MIX2-013"},
          "priorityQueue == 4 P0 items")
    for row in pack["corePassUpdate"]:
        check(row["v1Id"] in v1_ids, f"corePassUpdate v1Id {row['v1Id']} exists")
        if row["v2Id"]:
            check(row["v2Id"] in ids, f"corePassUpdate v2Id {row['v2Id']} exists")

    # ---- runtime untouched by this checkpoint ----
    status = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                            capture_output=True, text=True, check=True).stdout
    dirty_runtime = [ln for ln in status.splitlines() if "ClientGodot/" in ln]
    check(not dirty_runtime, "no ClientGodot/ paths dirty")

    out = {
        "checker": "check_ear_audition_pack_cp10_v1",
        "checkpoint": "MEDIA-02 WO37 M-D CP10",
        "checksTotal": CHECKS["total"],
        "checksPassed": CHECKS["passed"],
        "failures": CHECKS["failures"],
        "status": "PASS" if CHECKS["passed"] == CHECKS["total"] else "FAIL",
        "runtimeClientGodotDirty": bool(dirty_runtime),
        "counts": {"items": 58, "mixesV2": 14, "ambienceVariants": 26, "sfxDrafts": 18},
        "totalDurationSeconds": pack["totalDurationSeconds"],
        "notes": [
            "All 58 items re-measured from real bytes (own probe code); v1 pack bytes NOT re-hashed (Gói 38 delta discipline).",
            "SFX drafts and M39-B A/B renders keep their already-delivered playlists; referenced, not duplicated.",
        ],
    }
    (REPORTS / "MEDIA02_WO37_MD_CP10_VALIDATION_20261112.json").write_text(
        json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{out['status']}: {out['checksPassed']}/{out['checksTotal']} checks")
    if out["failures"]:
        for f in out["failures"]:
            print(f"  FAIL: {f}")
    sys.exit(0 if out["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
