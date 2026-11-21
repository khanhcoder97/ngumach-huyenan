#!/usr/bin/env python3
"""WO38 M38-A independent checker for P0_CANDIDATE_M38A_SUBSET_v1.json.

Re-hashes every file the subset manifest lists (candidate files, source
closure, runtime-unchanged proof), ffprobes the candidate videos,
re-parses the SRT windows against the per-shot notes, and asserts the
runtime cinematic/audio trees carry no tracked modifications.
Writes a validation JSON (--out) and exits non-zero on any mismatch.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SUBSET = ROOT / "Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    subset = json.loads(SUBSET.read_text())
    checks = []
    failures = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        if not ok:
            failures.append(f"{name}: {detail}")

    # 1. hashes: candidate files + closure + runtime proof
    all_entries = list(subset["files"])
    for group in subset["sourceClosure"].values():
        all_entries += group
    all_entries += subset["runtimeUnchangedProof"]
    bad = []
    for e in all_entries:
        p = ROOT / e["path"]
        if not p.exists() or p.stat().st_size != e["bytes"] or sha256_of(p) != e["sha256"]:
            bad.append(e["path"])
    check("hashes_all_subset_entries", not bad, f"{len(all_entries)} entries, bad={bad}")

    # 2. candidate video facts
    by_role = {e["role"]: e for e in subset["files"]}
    expect = {"candidate_scene_take_CIN_001": 36.0, "candidate_scene_take_CIN_002": 18.0,
              "candidate_scene_take_CIN_004": 18.0, "candidate_review_reel_72s": 72.0}
    for role, want in expect.items():
        pr = ffprobe(ROOT / by_role[role]["path"])
        dur = float(pr["format"]["duration"])
        vs = [s for s in pr["streams"] if s["codec_type"] == "video"]
        aus = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        ok = (abs(dur - want) <= 0.15 and len(vs) == 1 and len(aus) == 1
              and vs[0]["width"] == 640 and vs[0]["height"] == 360
              and vs[0]["r_frame_rate"] == "30/1" and vs[0]["codec_name"] == "h264"
              and aus[0]["codec_name"] == "aac")
        check(f"ffprobe_{role}", ok, f"dur={dur:.3f} streams={len(pr['streams'])}")
    for sc in ["CIN_001", "CIN_002", "CIN_004"]:
        pr = ffprobe(ROOT / by_role[f"ab_comparison_video_{sc}"]["path"])
        vs = [s for s in pr["streams"] if s["codec_type"] == "video"][0]
        check(f"ffprobe_ab_{sc}", vs["width"] == 640 and vs["height"] == 720,
              f"{vs['width']}x{vs['height']}")

    # 3. contact sheet geometry
    from PIL import Image
    sheet = Image.open(ROOT / by_role["candidate_contact_sheet_all12"]["path"])
    check("contact_sheet_size", sheet.size == (1920, 720), f"{sheet.size}")

    # 4. SRT windows vs per-shot dialogue notes
    def parse_srt(p: Path):
        cues = []
        for b in p.read_text(encoding="utf-8").strip().split("\n\n"):
            lines = [ln for ln in b.splitlines() if ln.strip()]
            if len(lines) < 3:
                continue
            def ts(s):
                h, m, rest = s.split(":")
                sec, ms = rest.split(",")
                return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0
            a, z = lines[1].split(" --> ")
            cues.append((ts(a), ts(z), " ".join(lines[2:])))
        return cues
    srt_bad = []
    for shot in subset["perShot"]:
        if shot["dialogue"]:
            cues = parse_srt(ROOT / f"ClientGodot/assets/cinematics/{shot['sceneId']}/{shot['sceneId']}_vi.srt")
            w = shot["dialogue"]["windowSceneSeconds"]
            if not cues or abs(cues[0][0] - w[0]) > 0.01 or abs(cues[0][1] - w[1]) > 0.01 \
                    or cues[0][2] != shot["dialogue"]["text"]:
                srt_bad.append(shot["shotId"])
            if shot["dialogue"]["beatStartsAtWindowHead"] is not True:
                srt_bad.append(shot["shotId"] + ":beat")
    check("srt_windows_match_notes", not srt_bad, f"bad={srt_bad}")

    # 5. runtime trees unmodified (tracked files)
    r = subprocess.run(["git", "status", "--porcelain", "--",
                        "ClientGodot/assets/cinematics", "ClientGodot/assets/audio"],
                       capture_output=True, text=True, cwd=ROOT)
    mods = [ln for ln in r.stdout.splitlines() if ln.strip()]
    check("runtime_trees_unmodified", not mods, f"{len(mods)} changed lines")

    result = {"validator": "check_p0_candidate_m38a_v1", "subset": SUBSET.name,
              "checks": checks, "pass": not failures, "failures": failures}
    out = ROOT / args.out if not Path(args.out).is_absolute() else Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"checks: {sum(1 for c in checks if c['pass'])}/{len(checks)} PASS; failures={failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
