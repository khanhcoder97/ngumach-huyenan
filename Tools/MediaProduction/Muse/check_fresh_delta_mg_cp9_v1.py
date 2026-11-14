#!/usr/bin/env python3
"""MEDIA-02 WO37 M-G CP9 — fresh-checkout verification of the
M-B CP4 + PROLOGUE V1 FIX binary delta (head be9ccb8).

Run INSIDE a fresh clone of muse/media-production-20261104 at
be9ccb8 after a pure-network selective LFS pull of the delta
paths (see the CP9 report for the exact pull list) plus a
`git lfs fetch` of the two superseded objects (broken mix
f026ed3e..., old MP4 88049317...) from ref 7f461da, so the
before/after controls exist in the local LFS object store.

Independent measurements from real bytes (conventions copied
from check_standard720_mb_cp4_v1.py and
check_prologue_v1_fix_v1.py — sha256, ffprobe, single-pass
loudnorm with brace matching, normalized cross-correlation):
  * fresh HEAD == be9ccb8, tree clean;
  * delta 7f461da..be9ccb8 is exactly the 40 known files
    (CP4 content 17 + CP4 report 2 + fix content 19 + fix
    report 2), every binary file real bytes (not a pointer)
    with sha/size matching its manifest;
  * the 21 Standard720 MP4s: sha/bytes == CP4 manifest,
    probe 1280x720@30 + AAC;
  * the fixed prologue mix: installed byte-identically at all
    three paths, loudnorm == manifest, every narration take
    present at lag 0 (corr >= 0.90) and absent from the broken
    control (<= 0.10);
  * runtime CIN_000 film + derivatives carry the fixed mix;
  * the CP4 re-run result (run separately in this clone) is
    270/271 with the single expected failure being the
    CIN_000 video-source sha — explained here, not hidden:
    the prologue fix re-muxed the runtime MP4 (audio only),
    so its file sha differs from the CP4 manifest while its
    VIDEO STREAM is bit-identical (stream-hash proof below);
  * runtime audio total stays 783; LFS census fresh vs the
    CP8 baseline; cumulative scope count re-derived
    (cf17178..be9ccb8 == 2375, cf17178..962b6df == 2373 —
    the fix report's 2368 was the pre-rebase count).

Reads the CP4 re-run JSON from the evidence copy at
MG_CP9_CP4_RERUN_JSON (env) or the default scratch path; the
validator does NOT read the committed validation JSON as
evidence of its own run. Exit 0 = PASS.
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
HEAD_SHA = "be9ccb8af8fea2ae5632952cc2b94ad4148d40fa"
BASE_7F = "7f461da15e8071bccde548ff998093c429f10541"
MERGE_BASE = "cf171786baebb10c3f17d3060d47429faf3e4026"
FIXED_SHA = ("4f8224e108fd86ecec4deb8b950344ed7c526ef4bd6bd66a79"
             "b58c9a71122e63")
BROKEN_SHA = ("f026ed3e10499b42ea4fcc39ada9a1b42e0b5b749d16"
              "ab77208afd54016ffb54")
OLD_MP4_SHA = ("8804931743e31d21c46c269f86b3deb65800668e3ec9c3e"
               "7c38d6a73057c2806")
SR = 48000
OUT_JSON = ROOT / ("Implementation/Reports/MuseMedia/"
                   "MEDIA02_WO37_MG_CP9_VALIDATION_20261113.json")
CHECKS = {"total": 0, "passed": 0}
FAIL = []
NOTES = {}


def check(name, ok, detail=""):
    CHECKS["total"] += 1
    if ok:
        CHECKS["passed"] += 1
    print(("PASS " if ok else "FAIL ") + name
          + (f" — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


def run(*args, cwd=None):
    return subprocess.run(args, cwd=cwd or ROOT, capture_output=True,
                          text=True)


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_pointer(p):
    with open(p, "rb") as f:
        return f.read(132).startswith(b"version https://git-lfs")


def probe(p):
    out = run("ffprobe", "-v", "error", "-show_format",
              "-show_streams", "-of", "json", str(p)).stdout
    return json.loads(out)


def loudnorm(p):
    r = run("ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
            "-af", "loudnorm=print_format=json", "-f", "null", "-")
    txt = r.stderr
    i = txt.rfind("{")
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                d = json.loads(txt[i:j + 1])
                return float(d["input_i"]), float(d["input_tp"])
    raise ValueError("loudnorm JSON block not found")


def decode_mono(path):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
         "-ar", str(SR), "-f", "f32le", "-"],
        capture_output=True).stdout
    return np.frombuffer(out, dtype=np.float32).astype(np.float64)


def corr_at(mix, take, lag):
    if lag < 0:
        take, mix = mix[:len(take) + lag], take[-lag:]
    seg = mix[lag:lag + len(take)]
    n = min(len(seg), len(take))
    a, b = seg[:n] - seg[:n].mean(), take[:n] - take[:n].mean()
    d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
    return float(a @ b / d) if d > 0 else 0.0


def best_corr(mix, take, start_s, win_s=0.25):
    exp = int(round(start_s * SR))
    best = (0.0, 0.0)
    for lag in range(exp - int(win_s * SR),
                     exp + int(win_s * SR), 240):
        if lag < 0 or lag + len(take) > len(mix):
            continue
        c = corr_at(mix, take, lag)
        if abs(c) > abs(best[0]):
            best = (c, lag / SR - start_s)
    c0, l0 = best
    base = exp + int(round(l0 * SR))
    for lag in range(base - 240, base + 240):
        if lag < 0 or lag + len(take) > len(mix):
            continue
        c = corr_at(mix, take, lag)
        if abs(c) > abs(best[0]):
            best = (c, lag / SR - start_s)
    return best


def align_corr(a, b, win_s=0.2):
    best = 0.0
    for off in range(-int(win_s * SR), int(win_s * SR), 480):
        if off >= 0:
            x, y = a[off:], b[:len(a) - off]
        else:
            x, y = a[:off], b[-off:]
        n = min(len(x), len(y))
        x, y = x[:n] - x[:n].mean(), y[:n] - y[:n].mean()
        d = np.sqrt((x ** 2).sum() * (y ** 2).sum())
        if d > 0:
            best = max(best, abs(float(x @ y / d)))
    return best


def stream_hash(p, spec):
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-map", spec,
         "-c", "copy", "-f", "hash", "-hash", "sha256", "-"],
        capture_output=True, text=True).stdout.strip()
    return out.split("=")[-1]


def lfs_object(oid):
    common = run("git", "rev-parse", "--git-common-dir").stdout.strip()
    p = ROOT / common / "lfs/objects" / oid[:2] / oid[2:4] / oid
    assert p.exists(), p
    assert sha256_of(p) == oid
    return p


def main() -> int:
    # ---- 1. fresh clone identity
    head = run("git", "rev-parse", "HEAD").stdout.strip()
    check("fresh HEAD == be9ccb8", head == HEAD_SHA, head[:12])
    st = run("git", "status", "--porcelain").stdout.strip()
    # Ignore this run's own artefacts: the validator copy and
    # the validation JSON it writes into the fresh clone.
    st_lines = [ln for ln in st.splitlines()
                if "check_fresh_delta_mg_cp9_v1.py" not in ln
                and "MEDIA02_WO37_MG_CP9_VALIDATION_20261113.json"
                not in ln]
    check("fresh tree clean (except this validator copy)",
          st_lines == [], "\n".join(st_lines)[:200])
    check("merge-base cf17178 is ancestor of HEAD",
          run("git", "merge-base", "--is-ancestor",
              MERGE_BASE, "HEAD").returncode == 0)

    # ---- 2. delta file list
    delta = run("git", "diff", "--name-only",
                f"{BASE_7F}..{HEAD_SHA}").stdout.split()
    check("delta 7f461da..be9ccb8 == 40 files", len(delta) == 40,
          str(len(delta)))
    NOTES["delta_files"] = len(delta)
    cp4_block = run("git", "diff", "--name-only",
                    "7f461da..21bc9ef386bec6cbd823a9dff564df03ee3534d4"
                    ).stdout.split()
    fix_block = run("git", "diff", "--name-only",
                    "41bfbaede1a5ec9365a39351564efac8fa5538a7"
                    "..962b6df05163a51d3f405e5dbec708f2894d1a2d"
                    ).stdout.split()
    check("CP4 content block == 17 paths", len(cp4_block) == 17,
          str(len(cp4_block)))
    check("fix content block == 19 paths", len(fix_block) == 19,
          str(len(fix_block)))
    cum_head = len(run("git", "diff", "--name-only",
                       f"{MERGE_BASE}..{HEAD_SHA}").stdout.split())
    cum_content = len(run(
        "git", "diff", "--name-only",
        f"{MERGE_BASE}..962b6df05163a51d3f405e5dbec708f2894d1a2d"
        ).stdout.split())
    check("cumulative cf17178..be9ccb8 == 2375", cum_head == 2375,
          str(cum_head))
    check("cumulative cf17178..962b6df == 2373", cum_content == 2373,
          str(cum_content))
    NOTES["cumulative_head"] = cum_head
    NOTES["cumulative_content_962b6df"] = cum_content

    # ---- 3. CP4 Standard720 set: sha/size/probe vs manifest
    cp4 = json.loads((ROOT / "Implementation/Content/Narrative"
                      "/Deliveries/STANDARD720_MB_CP4_v1.json"
                      ).read_text(encoding="utf-8"))
    cp2 = json.loads((ROOT / "Implementation/Content/Narrative"
                      "/Deliveries/STANDARD720_MB_CP2_v1.json"
                      ).read_text(encoding="utf-8"))
    cp2_by_scene = {e["sceneId"]: e for e in cp2["entries"]}
    check("CP4 manifest entries == 21", len(cp4["entries"]) == 21)
    tot_out = 0
    for e in cp4["entries"]:
        scene = e["sceneId"]
        out = ROOT / e["outPath"]
        check(f"{scene} 720p real bytes (not LFS pointer)",
              out.exists() and not is_pointer(out)
              and out.stat().st_size == e["outBytes"],
              f"{out.stat().st_size} B")
        check(f"{scene} 720p sha == CP4 manifest",
              sha256_of(out) == e["outSha256"])
        pr = probe(out)
        v = next(s for s in pr["streams"]
                 if s["codec_type"] == "video")
        a = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        check(f"{scene} 720p probe 1280x720@30 + AAC",
              v["width"] == 1280 and v["height"] == 720
              and v["r_frame_rate"] == "30/1"
              and a and a[0]["codec_name"] == "aac")
        check(f"{scene} 720p duration == manifest",
              abs(float(pr["format"]["duration"])
                  - e["outDuration"]) <= 0.06,
              f"{pr['format']['duration']} vs {e['outDuration']}")
        tot_out += e["outBytes"]
    check("CP4 set total bytes == 148002469", tot_out == 148002469,
          str(tot_out))
    NOTES["cp4_set_bytes"] = tot_out

    # ---- 4. fixed prologue mix
    sys.path.insert(0, str(ROOT / "Tools/MediaProduction/Muse"))
    from build_prologue_mix_v2 import (  # noqa: E402
        LYAN_WAV, VO_MANIFEST, build_timeline)
    fix_dir = ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED"
    fix_wav = fix_dir / "PROLOGUE_mix_v1_fixed.wav"
    fix_man = json.loads((fix_dir / "PROLOGUE_MIX_V1_FIXED_manifest_v1.json"
                          ).read_text(encoding="utf-8"))
    as_mix = (ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
              / "PROLOGUE_mix_v1.wav")
    rt_mix = (ROOT / "ClientGodot/assets/audio/mix/prologue"
              / "PROLOGUE_mix_v1.wav")
    check("fixed mix sha == its manifest",
          sha256_of(fix_wav) == fix_man["sha256"] == FIXED_SHA)
    check("Art_Source canonical mix == fixed render",
          sha256_of(as_mix) == FIXED_SHA)
    check("runtime mix copy == fixed render",
          sha256_of(rt_mix) == FIXED_SHA)
    check("fixed mix files are real bytes",
          not is_pointer(fix_wav) and not is_pointer(as_mix)
          and not is_pointer(rt_mix))
    lufs, tp = loudnorm(fix_wav)
    check("fixed mix loudnorm == manifest (-22.37/-3.11)",
          abs(lufs - fix_man["integratedLufs"]) <= 0.05
          and abs(tp - fix_man["truePeakDbtp"]) <= 0.05,
          f"{lufs:.2f} LUFS / {tp:.2f} dBTP")
    NOTES["fixed_mix_lufs"] = round(lufs, 2)
    NOTES["fixed_mix_tp"] = round(tp, 2)

    # ---- 5. narration takes: present in fixed, absent in broken
    vo = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    _, cues, _, _, lyan_start = build_timeline(vo)
    fixed = decode_mono(fix_wav)
    broken = decode_mono(lfs_object(BROKEN_SHA))
    take_dir = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
    worst_fixed = 1.0
    worst_broken = 0.0
    for i, s in enumerate(vo["segments"]):
        take = decode_mono(take_dir / s["file"])
        c, lag = best_corr(fixed, take, cues[i]["start"])
        worst_fixed = min(worst_fixed, c)
        check(f"SEG0{i + 1} take present in fixed mix",
              c >= 0.90 and abs(lag) <= 0.05,
              f"corr {c:+.3f} lag {lag:+.3f}s")
        cb, _ = best_corr(broken, take, cues[i]["start"])
        worst_broken = max(worst_broken, abs(cb))
        check(f"SEG0{i + 1} take absent in broken mix (control)",
              abs(cb) <= 0.10, f"corr {cb:+.3f}")
    lyan = decode_mono(LYAN_WAV)
    c, lag = best_corr(fixed, lyan, lyan_start)
    worst_fixed = min(worst_fixed, c)
    check("Ly An final line present in fixed mix",
          c >= 0.90 and abs(lag) <= 0.05,
          f"corr {c:+.3f} lag {lag:+.3f}s")
    cb, _ = best_corr(broken, lyan, lyan_start)
    worst_broken = max(worst_broken, abs(cb))
    check("Ly An final line absent in broken mix (control)",
          abs(cb) <= 0.10, f"corr {cb:+.3f}")
    NOTES["worst_fixed_corr"] = round(worst_fixed, 3)
    NOTES["worst_broken_corr"] = round(worst_broken, 3)

    # ---- 6. runtime CIN_000 film + derivatives carry the fixed mix
    cine = ROOT / "ClientGodot/assets/cinematics/CIN_000"
    exp = json.loads((cine / "scene_export_manifest_v1.json"
                      ).read_text(encoding="utf-8"))
    mp4 = cine / "CIN_000_640x360_30fps.mp4"
    ogv = cine / "CIN_000_640x360_30fps.ogv"
    sub = cine / "CIN_000_640x360_30fps_sub_vi.mp4"
    s720 = (ROOT / "Art_Source/Cinematics/Standard720/CIN_000_subtitled"
            / "CIN_000_1280x720_30fps_sub_vi.mp4")
    for label, path, entry in (("MP4", mp4, exp["mp4"]),
                               ("OGV", ogv, exp["ogv"])):
        check(f"{label} sha/size == export manifest",
              sha256_of(path) == entry["sha256"]
              and path.stat().st_size == entry["sizeBytes"])
        emb = decode_mono(path)
        check(f"{label} embedded audio is the fixed mix",
              align_corr(emb, fixed) >= 0.90,
              f"corr {align_corr(emb, fixed):.3f}")
    check("subtitled sha == export manifest",
          sha256_of(sub) == exp["mp4SubVi"]["sha256"])
    check("subtitled embedded audio is the fixed mix",
          align_corr(decode_mono(sub), fixed) >= 0.90)
    man720 = json.loads((ROOT / "Implementation/Content/Narrative"
                         "/Deliveries"
                         "/STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json"
                         ).read_text(encoding="utf-8"))
    e720 = man720["entries"][0]
    check("720p subtitled sha/source == FIX720 manifest",
          sha256_of(s720) == e720["outSha256"]
          and e720["sourceSha256"] == sha256_of(sub))
    check("720p subtitled audio bit-copied from variant",
          stream_hash(s720, "0:a:0") == stream_hash(sub, "0:a:0"))

    # ---- 7. the expected CP4-checker CIN_000 failure, explained
    old_mp4 = lfs_object(OLD_MP4_SHA)
    check("CIN_000 video stream bit-identical to pre-fix MP4",
          stream_hash(mp4, "0:v:0")
          == stream_hash(old_mp4, "0:v:0"))
    check("current runtime MP4 sha != CP4 manifest (expected: "
          "prologue fix re-muxed audio only)",
          sha256_of(mp4) != cp2_by_scene["CIN_000"]["sourceSha256"]
          and sha256_of(mp4) == exp["mp4"]["sha256"],
          sha256_of(mp4)[:12])

    # ---- 8. runtime audio total + LFS census
    ra = json.loads((ROOT / "ClientGodot/assets/audio"
                     "/RUNTIME_AUDIO_manifest_v1.json"
                     ).read_text(encoding="utf-8"))
    audio_files = run("git", "ls-files",
                      "ClientGodot/assets/audio").stdout.split()
    check("runtime audio manifest total == 783",
          ra["totalFiles"] == 783, str(ra["totalFiles"]))
    check("runtime audio files on disk == 784 (783 + manifest)",
          len(audio_files) == 784, str(len(audio_files)))
    lfs_lines = run("git", "lfs", "ls-files").stdout.splitlines()
    # `git lfs ls-files` prints "<oid> * <path>" (or "- " when
    # the file is not yet downloaded); the OID is field 0.
    oids = {ln.split()[0] for ln in lfs_lines if ln.split()}
    check("LFS census recorded",
          len(lfs_lines) > 2800 and len(oids) > 2100,
          f"{len(lfs_lines)} tracked / {len(oids)} OIDs")
    NOTES["lfs_tracked"] = len(lfs_lines)
    NOTES["lfs_oids"] = len(oids)

    # ---- 9. CP4 checker re-run result (evidence copy)
    rerun_path = os.environ.get(
        "MG_CP9_CP4_RERUN_JSON",
        "/home/hatch/workspace/projects/media02-scratch"
        "/mg_cp9_cp4_rerun.json")
    rerun = json.loads(Path(rerun_path).read_text(encoding="utf-8"))
    check("CP4 checker re-run == 270/271 (1 expected failure)",
          rerun["checksTotal"] == 271
          and rerun["checksPassed"] == 270,
          f"{rerun['checksPassed']}/{rerun['checksTotal']}")
    check("CP4 re-run sole failure is the CIN_000 source sha",
          rerun["failures"]
          == ["CIN_000 video source sha == manifest + CP2"],
          str(rerun["failures"]))
    NOTES["cp4_rerun"] = (f"{rerun['checksPassed']}/"
                          f"{rerun['checksTotal']}")

    OUT_JSON.write_text(json.dumps({
        "checker": "check_fresh_delta_mg_cp9_v1",
        "checkpoint": "MEDIA-02 WO37 M-G CP9",
        "base": BASE_7F,
        "head": HEAD_SHA,
        "checksTotal": CHECKS["total"],
        "checksPassed": CHECKS["passed"],
        "failures": FAIL,
        "status": "PASS" if not FAIL else "FAIL",
        "notes": NOTES,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{CHECKS['passed']}/{CHECKS['total']} PASS, "
          f"{len(FAIL)} FAIL")
    print("validation:", OUT_JSON.relative_to(ROOT))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
