#!/usr/bin/env python3
"""Independent validator for MEDIA-02 WO39 M39-B CP1 (level-matched A/B
voice-palette review pack).

Re-derives everything from disk + the M-F CP1 source pack; never trusts
the builder's manifest. Checks:
  1. all 40 source WAVs re-hash to the M-F CP1 pack values;
  2. all 40 renders re-hash to the M39-B manifest values;
  3. re-measured pre LUFS/TP match the manifest within 0.10;
  4. gain arithmetic: post LUFS == pre LUFS + applied gain (+/-0.35 LU);
  5. post LUFS within 0.30 LU of the pair target; A/B spread <= 0.35 LU;
  6. pair-target rule: target == min(-23.00, loudest TP-safe level) (+/-0.05),
     and ceilingLimited flag agrees with the rule;
  7. post true peak <= -1.00 dBTP on every render;
  8. duration unchanged vs source (+/-0.002 s); format pcm_s16le/48k/mono;
  9. render bytes differ from source bytes (gain actually applied);
 10. manifest counts/paths consistent; playlist lists all 40 renders
     exactly once, repo-root-relative, resolving to real files;
 11. no render path leaves Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1/.

Writes Implementation/Reports/MuseMedia/MEDIA02_WO39_M39B_CP1_VO_REVIEW_VALIDATION_20261112.json
and exits non-zero on any failure.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json"
MANIFEST = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_REVIEW_M39B_v1.json"
PLAYLIST = ROOT / "Implementation/Reports/MuseMedia/vo_palette_review_m39b_playlist.txt"
OUT = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO39_M39B_CP1_VO_REVIEW_VALIDATION_20261112.json"

TARGET_LUFS = -23.00
TP_CEILING = -1.00


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n{r.stderr[-1500:]}")
    return r


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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


def measure(path: Path) -> dict:
    p = probe(path)
    s = p["streams"][0]
    ln = loudnorm(path)
    return {"duration": round(float(p["format"]["duration"]), 3),
            "lufs": round(float(ln["input_i"]), 2),
            "tp": round(float(ln["input_tp"]), 2),
            "codec": s["codec_name"], "rate": int(s["sample_rate"]),
            "ch": int(s["channels"]), "bytes": int(p["format"]["size"])}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    global ROOT, PACK, MANIFEST, PLAYLIST, OUT
    ROOT = Path(args.root).resolve()
    PACK = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json"
    MANIFEST = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_REVIEW_M39B_v1.json"
    PLAYLIST = ROOT / "Implementation/Reports/MuseMedia/vo_palette_review_m39b_playlist.txt"
    OUT = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO39_M39B_CP1_VO_REVIEW_VALIDATION_20261112.json"

    checks, failures = [], []

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        if not ok:
            failures.append(f"{name}: {detail}")

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    pack_by_key = {t["takeKey"]: t for t in pack["takes"]}

    check("manifest.checkpoint", man.get("checkpoint") == "MEDIA-02 WO39 M39-B CP1",
          str(man.get("checkpoint")))
    check("manifest.counts.pairs", man["counts"]["pairs"] == 20, str(man["counts"]))
    check("manifest.counts.renders", man["counts"]["renders"] == 40, str(man["counts"]))
    check("manifest.review_only", man.get("reviewOnly") is True, str(man.get("reviewOnly")))
    check("manifest.status", man.get("status") == "DRAFT_NOT_FINAL", str(man.get("status")))

    listed = []
    for pr in man["pairs"]:
        key = pr["takeKey"]
        src = pack_by_key.get(key)
        check(f"{key}.in_source_pack", src is not None)
        if src is None:
            continue
        check(f"{key}.role_voice_match",
              pr["role"] == src["role"] and pr["voice"] == src["voice"] and pr["text"] == src["text"],
              f"{pr['role']}/{pr['voice']}")
        # expected pair target from re-measured sources
        sides_src = []
        for side, label in (("A", "canonical"), ("B", "palette")):
            s = next(x for x in pr["sides"] if x["side"] == side)
            if label == "canonical":
                spath = ROOT / src["canonicalTake"]["dir"] / src["canonicalTake"]["file"]
                exp_sha = src["canonicalTake"]["sha256"]
            else:
                spath = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1" / src["paletteTake"]["wav"]
                exp_sha = src["paletteTake"]["wavSha256"]
            check(f"{key}.{side}.source_sha", sha256(spath) == exp_sha,
                  f"{spath.name}")
            sm = measure(spath)
            check(f"{key}.{side}.pre_lufs_match_manifest",
                  abs(sm["lufs"] - s["preIntegratedLufs"]) <= 0.10,
                  f"re-measured {sm['lufs']} vs manifest {s['preIntegratedLufs']}")
            check(f"{key}.{side}.pre_tp_match_manifest",
                  abs(sm["tp"] - s["preTruePeakDbtp"]) <= 0.10,
                  f"re-measured {sm['tp']} vs manifest {s['preTruePeakDbtp']}")
            sides_src.append((side, s, spath, sm))
            rpath = ROOT / s["renderFile"]
            check(f"{key}.{side}.render_exists", rpath.exists(), s["renderFile"])
            if not rpath.exists():
                continue
            check(f"{key}.{side}.render_sha", sha256(rpath) == s["renderSha256"])
            check(f"{key}.{side}.render_bytes", rpath.stat().st_size == s["renderBytes"],
                  f"{rpath.stat().st_size} vs {s['renderBytes']}")
            check(f"{key}.{side}.render_differs_from_source",
                  sha256(rpath) != sha256(spath), "identical bytes")
            check(f"{key}.{side}.render_under_review_root",
                  s["renderFile"].startswith(
                      "Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1/"),
                  s["renderFile"])
            rm = measure(rpath)
            check(f"{key}.{side}.post_lufs_match_manifest",
                  abs(rm["lufs"] - s["postIntegratedLufs"]) <= 0.10,
                  f"re-measured {rm['lufs']} vs manifest {s['postIntegratedLufs']}")
            check(f"{key}.{side}.post_tp_match_manifest",
                  abs(rm["tp"] - s["postTruePeakDbtp"]) <= 0.10,
                  f"re-measured {rm['tp']} vs manifest {s['postTruePeakDbtp']}")
            check(f"{key}.{side}.post_lufs_near_target",
                  abs(rm["lufs"] - pr["pairTargetLufs"]) <= 0.30,
                  f"{rm['lufs']} vs target {pr['pairTargetLufs']}")
            check(f"{key}.{side}.post_tp_ceiling",
                  rm["tp"] <= TP_CEILING + 0.01, f"TP {rm['tp']}")
            check(f"{key}.{side}.duration_unchanged",
                  abs(rm["duration"] - sm["duration"]) <= 0.002,
                  f"{sm['duration']} -> {rm['duration']}")
            check(f"{key}.{side}.format",
                  (rm["codec"], rm["rate"], rm["ch"]) == ("pcm_s16le", 48000, 1),
                  f"{rm['codec']}/{rm['rate']}/{rm['ch']}")
            check(f"{key}.{side}.gain_arithmetic",
                  abs((sm["lufs"] + s["appliedGainDb"]) - rm["lufs"]) <= 0.35,
                  f"{sm['lufs']} + {s['appliedGainDb']} = {sm['lufs'] + s['appliedGainDb']:.2f} "
                  f"vs measured {rm['lufs']}")
            listed.append(s["renderFile"])
        # pair-level rules from re-measured sources
        achievable = [sm["lufs"] + (TP_CEILING - sm["tp"]) for _, _, _, sm in sides_src]
        expected_target = round(min(TARGET_LUFS, min(achievable)), 2)
        check(f"{key}.pair_target_rule",
              abs(pr["pairTargetLufs"] - expected_target) <= 0.05,
              f"manifest {pr['pairTargetLufs']} vs rule {expected_target}")
        check(f"{key}.ceiling_flag",
              pr["ceilingLimited"] == (expected_target < TARGET_LUFS - 0.005),
              f"flag {pr['ceilingLimited']} vs expected {expected_target < TARGET_LUFS - 0.005}")
        posts = [next(x for x in pr["sides"] if x["side"] == sd)["postIntegratedLufs"]
                 for sd in ("A", "B")]
        check(f"{key}.ab_spread",
              abs(posts[0] - posts[1]) <= 0.35, f"A {posts[0]} vs B {posts[1]}")

    plines = PLAYLIST.read_text(encoding="utf-8").splitlines()
    ppaths = [ln for ln in plines if ln and not ln.startswith("#")]
    check("playlist.count", len(ppaths) == 40, f"{len(ppaths)} paths")
    check("playlist.unique", len(set(ppaths)) == 40, f"{len(set(ppaths))} unique")
    check("playlist.matches_manifest", sorted(ppaths) == sorted(listed),
          "playlist set != manifest render set")
    for ln in ppaths:
        p = ROOT / ln
        check(f"playlist.exists:{ln}", p.exists() and p.is_file())
        check(f"playlist.relative:{ln}", not Path(ln).is_absolute())

    result = {"checkpoint": "MEDIA-02 WO39 M39-B CP1",
              "validator": "check_vo_palette_review_m39b_cp1_v1.py",
              "verdict": "PASS" if not failures else "FAIL",
              "checksTotal": len(checks),
              "checksPassed": sum(1 for c in checks if c["pass"]),
              "failures": failures,
              "checks": checks}
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"validator: {result['checksPassed']}/{result['checksTotal']} PASS "
          f"-> {result['verdict']}")
    for f in failures:
        print(f"  FAIL: {f}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
