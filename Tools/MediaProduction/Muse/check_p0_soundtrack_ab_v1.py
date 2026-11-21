#!/usr/bin/env python3
"""Independent checker for WO37 M-B CP1 - P0 soundtrack A/B (v1 vs v2 vs v3).

Re-derives everything from disk: re-hashes sources and reels, re-probes
streams, re-measures loudness (full reel + all per-scene segments + one
VO window per reel), re-computes the video-stream MD5, and verifies the
playlist resolves and the runtime tree is untouched.

Writes Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP1_VALIDATION_20261109.json
and exits 0 only when every check passes.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Art_Source/Cinematics/P0_Motion/soundtrack_ab/P0_SOUNDTRACK_AB_v1.json"
OUT = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP1_VALIDATION_20261109.json"
PLAYLIST = ROOT / "Implementation/Reports/MuseMedia/p0_soundtrack_ab_playlist.txt"

LUFS_TOL = 0.10
TP_TOL = 0.20
RMS_TOL = 0.30
DUR_TOL = 0.05

checks = []


def check(name, ok, detail):
    checks.append({"check": name, "pass": bool(ok), "detail": str(detail)})
    print(("PASS " if ok else "FAIL ") + name + " — " + str(detail))
    return bool(ok)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stderr[-1500:]}")
    return r


def probe(p: Path) -> dict:
    return json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                           "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,bit_rate",
                           "-show_entries", "format=duration,size",
                           "-of", "json", str(p)]).stdout)


def loudnorm(p: Path, start=None, dur=None) -> dict:
    cmd = ["ffmpeg", "-hide_banner", "-v", "info"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", str(p), "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    m = re.search(r"\{[^}]*\"input_i\"[^}]*\}", r.stderr, re.S)
    if r.returncode != 0 or not m:
        raise RuntimeError(f"loudnorm failed for {p}: {r.stderr[-1000:]}")
    j = json.loads(m.group(0))
    return {"integratedLUFS": round(float(j["input_i"]), 2),
            "truePeakDBTP": round(float(j["input_tp"]), 2)}


def window_stats(p: Path, start: float, dur: float) -> dict:
    cmd = ["ffmpeg", "-hide_banner", "-v", "info", "-ss", str(start), "-t", str(dur),
           "-i", str(p), "-vn", "-af", "astats=metadata=1:reset=1", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    overall = r.stderr.rsplit("Overall", 1)[-1]
    rms = re.search(r"RMS level dB:\s*(-?[\d.]+)", overall)
    peak = re.search(r"Peak level dB:\s*(-?[\d.]+)", overall)
    if r.returncode != 0 or not rms or not peak:
        raise RuntimeError(f"astats failed for {p}: {r.stderr[-1000:]}")
    return {"rmsDbfs": round(float(rms.group(1)), 2),
            "peakDbfs": round(float(peak.group(1)), 2)}


def video_md5(p: Path) -> str:
    r = run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:v", "-c", "copy", "-f", "md5", "-"])
    m = re.search(r"MD5=([0-9a-f]{32})", r.stdout)
    if not m:
        raise RuntimeError(f"video md5 failed for {p}")
    return m.group(1)


def close(a, b, tol):
    return abs(a - b) <= tol


def main() -> int:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    bad = []

    # --- 1. sources: candidate reel + 3 mix masters ---
    pic = man["picture"]
    src_ok = sha256(ROOT / pic["source"]) == pic["sha256"]
    bad += [] if src_ok else ["candidate reel sha"]
    check("source_candidate_reel_sha", src_ok, pic["sha256"][:12])
    for ver, want in man["sourceClosure"]["mixMasterSha256"].items():
        got = sha256(ROOT / man["audioMasters"][ver]["file"])
        ok = got == want
        bad += [] if ok else [f"{ver} master sha"]
        check(f"source_mix_master_sha_{ver}", ok, want[:12])

    # --- 2. reels: hash, probe, video md5, full loudness ---
    by_ver = {r["version"]: r for r in man["reels"]}
    for ver in ("v1", "v2", "v3"):
        r = by_ver[ver]
        p = ROOT / r["file"]
        ok = p.exists() and sha256(p) == r["sha256"]
        bad += [] if ok else [f"{ver} reel sha"]
        check(f"reel_sha_{ver}", ok, r["sha256"][:12])
        pr = probe(p)
        vs = [s for s in pr["streams"] if s["codec_type"] == "video"]
        au = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        shape_ok = (len(vs) == 1 and len(au) == 1 and vs[0]["width"] == 640
                    and vs[0]["height"] == 360 and vs[0]["r_frame_rate"] == "30/1"
                    and au[0]["codec_name"] == "aac" and int(au[0]["sample_rate"]) == 48000
                    and int(au[0]["channels"]) == 2
                    and close(float(pr["format"]["duration"]), r["durationSeconds"], DUR_TOL))
        bad += [] if shape_ok else [f"{ver} stream shape"]
        check(f"reel_shape_{ver}", shape_ok,
              f"{vs[0]['width']}x{vs[0]['height']}@{vs[0]['r_frame_rate']} "
              f"{au[0]['codec_name']} {au[0]['sample_rate']}Hz "
              f"dur={float(pr['format']['duration']):.3f}")
        md5 = video_md5(p)
        ok = md5 == pic["videoStreamMd5"]
        bad += [] if ok else [f"{ver} video md5"]
        check(f"reel_video_md5_{ver}", ok, md5[:12])
        loud = loudnorm(p)
        ok = (close(loud["integratedLUFS"], r["reelLoudness"]["integratedLUFS"], LUFS_TOL)
              and close(loud["truePeakDBTP"], r["reelLoudness"]["truePeakDBTP"], TP_TOL))
        bad += [] if ok else [f"{ver} reel loudness"]
        check(f"reel_loudness_{ver}", ok, loud)

    # --- 3. per-scene loudness (all 9 segments) ---
    scene_rows = {row["sceneId"]: row for row in man["comparison"]["perSceneLoudness"]}
    for sc in ("CIN_001", "CIN_002", "CIN_004"):
        row = scene_rows[sc]
        s0, s1 = row["reelSeconds"]
        for ver in ("v1", "v2", "v3"):
            want = row[ver]
            got = loudnorm(ROOT / by_ver[ver]["file"], start=s0, dur=s1 - s0)
            ok = (close(got["integratedLUFS"], want["integratedLUFS"], LUFS_TOL)
                  and close(got["truePeakDBTP"], want["truePeakDBTP"], TP_TOL))
            bad += [] if ok else [f"{sc} {ver} scene loudness"]
            check(f"scene_loudness_{sc}_{ver}", ok, got)

    # --- 4. one VO window RMS per reel (CIN_001_S05, the DECIDED window) ---
    w = next(x for x in man["comparison"]["voWindowStats"] if x["shotId"] == "CIN_001_S05")
    w0, w1 = w["windowReelSeconds"]
    for ver in ("v1", "v2", "v3"):
        want = w[ver]
        got = window_stats(ROOT / by_ver[ver]["file"], w0, w1 - w0)
        ok = (close(got["rmsDbfs"], want["rmsDbfs"], RMS_TOL)
              and close(got["peakDbfs"], want["peakDbfs"], RMS_TOL))
        bad += [] if ok else [f"{ver} VO window RMS"]
        check(f"vo_window_rms_{ver}", ok, got)

    # --- 5. v3 cross-check vs candidate reel ---
    cross = man["comparison"]["v3CrossCheckVsCandidateReel"]
    cand_loud = loudnorm(ROOT / pic["source"])
    ok = (close(cand_loud["integratedLUFS"], cross["candidateReelLoudness"]["integratedLUFS"], LUFS_TOL)
          and close(cand_loud["truePeakDBTP"], cross["candidateReelLoudness"]["truePeakDBTP"], TP_TOL))
    bad += [] if ok else ["candidate reel loudness"]
    check("crosscheck_candidate_reel_loudness", ok, cand_loud)

    # --- 6. manifest consistency: wave-diff rows ---
    wd = man["comparison"]["waveformDiffMasters"]
    pairs = {d["pair"] for d in wd}
    scopes = {d["scope"] for d in wd}
    ok = len(wd) == 21 and pairs == {"v1-vs-v2", "v1-vs-v3", "v2-vs-v3"} and len(scopes) == 7
    bad += [] if ok else ["wave-diff table"]
    check("wave_diff_table_shape", ok, f"{len(wd)} rows, {len(pairs)} pairs, {len(scopes)} scopes")

    # --- 7. playlist resolves ---
    pl_ok = PLAYLIST.exists()
    entries = []
    if pl_ok:
        for line in PLAYLIST.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                entries.append(line)
        pl_ok = len(entries) == 3 and all((ROOT / "Implementation/Reports/MuseMedia" / e).exists()
                                          for e in entries)
    bad += [] if pl_ok else ["playlist"]
    check("playlist_resolves", pl_ok, f"{len(entries)} entries")

    # --- 8. runtime untouched ---
    r = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                       capture_output=True, text=True, cwd=ROOT)
    ok = r.stdout.strip() == ""
    bad += [] if ok else ["ClientGodot dirty"]
    check("runtime_trees_unmodified", ok, "0 changed lines" if ok else r.stdout.strip()[:200])

    result = {"validator": "check_p0_soundtrack_ab_v1",
              "manifest": "P0_SOUNDTRACK_AB_v1.json",
              "checks": checks,
              "pass": len(bad) == 0,
              "failures": bad}
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{sum(c['pass'] for c in checks)}/{len(checks)} checks passed")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
