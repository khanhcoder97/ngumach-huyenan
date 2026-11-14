#!/usr/bin/env python3
"""M-G CP10 independent validator — fresh-checkout verification of the
WO37 M-B CP5 content delta (commit 257c985, 7 files) at head 8f7120a.

Independent of check_prologue_subtitled_v2_v1.py: own SRT parser, own
ffprobe reads, own manifest arithmetic, own git-scope reads. The CP5
checker re-run (55/55) is consumed only as a reproducibility artifact
(section E): its output JSON must equal the committed one detail by
detail. Run against a FRESH clone (GIT_LFS_SKIP_SMUDGE=1 + pure-network
`git lfs pull -I` of the delta + checker reference paths).

Usage: python3 check_fresh_delta_mg_cp10_v1.py <fresh-clone-root> <out-json>
"""
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# git-lfs lives in the workspace tools-bin; git needs it on PATH for any
# command that touches LFS-filtered paths (status/show/diff).
os.environ["PATH"] = (str(Path.home() / "workspace/tools-bin") + os.pathsep
                      + os.environ.get("PATH", ""))

ROOT = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]).resolve()

HEAD = "8f7120a34d92bee816ce163e6ea6213a1a916e24"
CONTENT = "257c98538c91a9d42c208300ab9a8e0e51a5fc90"
BASE = "443d3e4"  # M-G CP9 verified head
DELTA = [
    "Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json",
    "Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4",
    "Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/CIN_000_1280x720_30fps_sub_vi_v2.mp4",
    "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt",
    "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_V2_MB_CP5_v1.json",
    "Tools/MediaProduction/Muse/build_prologue_subtitled_v2.py",
    "Tools/MediaProduction/Muse/check_prologue_subtitled_v2_v1.py",
]
POLICY_ROOTS = [
    "Art_Source/Cinematics/", "Art_Source/Audio/Muse/",
    "ClientGodot/assets/cinematics/", "ClientGodot/assets/audio/",
    "Implementation/Content/Narrative/Deliveries/",
    "Implementation/Content/Audio/Deliveries/",
    "Implementation/Reports/MuseMedia/", "Tools/MediaProduction/Muse/",
]
MP4_640 = "Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4"
MP4_720 = "Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/CIN_000_1280x720_30fps_sub_vi_v2.mp4"
SRT = "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt"
CP5_MANIFEST = "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_V2_MB_CP5_v1.json"
FILM_MANIFEST = "Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json"
EXPECT = {
    MP4_640: ("f8d6ac322c9123113eedb080a0c464ce2d2e297ee9921b092b59317b2f8ca0be", 11927191),
    MP4_720: ("472c116718f294663b2f9aac700e20fda72ed96db8a4229942fdc12ed234e760", 32342539),
    SRT: ("b4495c2506295535df3a0c6508ccfee28d3a61c3236f66942b22a8515185b0d0", 2526),
}

CHECKS = {"total": 0, "passed": 0}
FAIL = []
DETAILS = {}


def check(name, ok, detail=""):
    CHECKS["total"] += 1
    if ok:
        CHECKS["passed"] += 1
    else:
        FAIL.append(name)
    if detail != "":
        DETAILS[name] = detail


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout.strip()


def ffprobe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_streams",
                          "-show_format", "-of", "json", str(p)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def parse_srt(text):
    cues = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 2 or "-->" not in lines[1]:
            continue
        m = re.match(r"(\d+):(\d+):([\d,]+) --> (\d+):(\d+):([\d,]+)", lines[1])
        if not m:
            continue

        def t(h, mi, s):
            return int(h) * 3600 + int(mi) * 60 + float(s.replace(",", "."))
        cues.append({"start": t(*m.group(1, 2, 3)), "end": t(*m.group(4, 5, 6)),
                     "text": " ".join(lines[2:]).strip()})
    return cues


def main():
    # --- A. delta scope (git) ---
    check("fresh HEAD == 8f7120a", git("rev-parse", "HEAD") == HEAD,
          git("rev-parse", "HEAD")[:7])
    check("fresh tree clean", git("status", "--porcelain") == "")
    got = git("show", "--name-only", "--format=", CONTENT).splitlines()
    check("content commit delta == exactly the 7 expected paths",
          sorted(got) == sorted(DELTA), f"{len(got)} paths")
    check("all 7 delta paths under policy roots",
          all(any(p.startswith(r) for r in POLICY_ROOTS) for p in DELTA))
    check("no delta path under ClientGodot/ (runtime)",
          not any(p.startswith("ClientGodot/") for p in DELTA))
    rng = git("diff", "--name-only", f"{BASE}..HEAD").splitlines()
    check("range 443d3e4..8f7120a has no ClientGodot/ path",
          not any(p.startswith("ClientGodot/") for p in rng),
          f"{len(rng)} paths in range")

    # --- B. LFS real bytes + manifest arithmetic ---
    for rel, (sha, size) in EXPECT.items():
        p = ROOT / rel
        check(f"{Path(rel).name} sha/size == CP5 record",
              sha256_of(p) == sha and p.stat().st_size == size,
              f"{sha256_of(p)[:16]} / {p.stat().st_size}")
    check("both MP4s are real bytes, not 133 B pointers",
          (ROOT / MP4_640).stat().st_size > 1_000_000
          and (ROOT / MP4_720).stat().st_size > 1_000_000)
    fman = json.loads((ROOT / FILM_MANIFEST).read_text(encoding="utf-8"))
    sv2 = fman.get("subtitledVariantV2", {})
    check("film manifest subtitledVariantV2 sha == 640 disk",
          sv2.get("sha256") == sha256_of(ROOT / MP4_640),
          (sv2.get("sha256") or "")[:16])
    check("film manifest subtitledVariantV2 readable SRT sha == disk",
          sv2.get("readableSrtSha256") == sha256_of(ROOT / SRT))
    cp5 = json.loads((ROOT / CP5_MANIFEST).read_text(encoding="utf-8"))
    e640, e720 = cp5["entries"]
    check("CP5 manifest 640 entry sha/size == disk",
          e640["sha256"] == sha256_of(ROOT / MP4_640)
          and e640["sizeBytes"] == (ROOT / MP4_640).stat().st_size)
    check("CP5 manifest 720 entry sha/size == disk",
          e720["outSha256"] == sha256_of(ROOT / MP4_720)
          and e720["outBytes"] == (ROOT / MP4_720).stat().st_size)
    check("CP5 manifest budget arithmetic",
          cp5["budget"]["mp4Set"]["totalBytes"]
          == e640["sizeBytes"] + e720["outBytes"],
          str(cp5["budget"]["mp4Set"]["totalBytes"]))
    check("CP5 manifest runtimeTreeModified == false",
          cp5.get("runtimeTreeModified") is False)

    # --- C. ffprobe streams ---
    for rel, w, h in ((MP4_640, 640, 360), (MP4_720, 1280, 720)):
        probe = ffprobe(ROOT / rel)
        kinds = [s["codec_type"] for s in probe["streams"]]
        v = next(s for s in probe["streams"] if s["codec_type"] == "video")
        a = next(s for s in probe["streams"] if s["codec_type"] == "audio")
        dur = float(probe["format"]["duration"])
        check(f"{Path(rel).name} streams [video, audio, subtitle]",
              kinds == ["video", "audio", "subtitle"], str(kinds))
        check(f"{Path(rel).name} video h264 {w}x{h}@30",
              v["codec_name"] == "h264" and v["width"] == w
              and v["height"] == h and v.get("r_frame_rate") == "30/1")
        check(f"{Path(rel).name} audio AAC stereo 48k",
              a["codec_name"] == "aac" and a["channels"] == 2
              and a["sample_rate"] == "48000")
        check(f"{Path(rel).name} duration 87.2667 +-0.01",
              abs(dur - 87.2667) <= 0.01, f"{dur:.4f}")
    d640 = float(ffprobe(ROOT / MP4_640)["format"]["duration"])
    d720 = float(ffprobe(ROOT / MP4_720)["format"]["duration"])
    check("640 and 720 durations equal within 0.01 s",
          abs(d640 - d720) <= 0.01, f"{d640:.4f} vs {d720:.4f}")

    # --- D. SRT, own parser ---
    raw = (ROOT / SRT).read_text(encoding="utf-8")
    check("SRT has no CR", "\r" not in raw)
    cues = parse_srt(raw)
    check("readable v2 SRT has 26 chunks", len(cues) == 26, str(len(cues)))
    check("cues monotonic, non-overlapping",
          all(cues[i]["end"] <= cues[i + 1]["start"]
              for i in range(len(cues) - 1)))
    mind = min(c["end"] - c["start"] for c in cues)
    check("min chunk duration >= 1.0 s", mind >= 1.0, f"{mind:.3f} s")
    canon = parse_srt((ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi.srt")
                      .read_text(encoding="utf-8"))

    def norm(s):
        return re.sub(r"\s+", " ", s).strip()
    check("readable v2 text == canonical text (normalized)",
          norm(" ".join(c["text"] for c in cues))
          == norm(" ".join(c["text"] for c in canon)))
    check("first chunk starts at 1.400 s (SEG01 window)",
          abs(cues[0]["start"] - 1.4) <= 0.001, f"{cues[0]['start']:.3f}")
    # Chunks 1-24 are the 5 narration segments; chunks 25-26 carry the
    # Ly An final line (starts 80.907 s). The SEG05 narration end is the
    # 24th chunk, not the last chunk.
    check("24th chunk ends at 77.839 s (SEG05 palette end)",
          abs(cues[23]["end"] - 77.839) <= 0.001, f"{cues[23]['end']:.3f}")
    check("25th chunk starts at 80.907 s (Ly An final line)",
          abs(cues[24]["start"] - 80.907) <= 0.001, f"{cues[24]['start']:.3f}")
    check("last chunk ends at 83.475 s (final line end)",
          abs(cues[-1]["end"] - 83.475) <= 0.001, f"{cues[-1]['end']:.3f}")

    # --- E. checker re-run reproducibility ---
    rerun = json.loads((ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP5_VALIDATION_20261113.json")
                       .read_text(encoding="utf-8"))
    # The file on disk in the fresh clone is the re-run output (the checker
    # overwrote it); the committed original comes from git HEAD.
    saved_raw = subprocess.run(
        ["git", "show",
         "HEAD:Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP5_VALIDATION_20261113.json"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout
    saved = json.loads(saved_raw)
    check("CP5 checker re-run in fresh clone: 55/55 PASS",
          rerun["checks"] == {"total": 55, "passed": 55}
          and rerun.get("status") == "PASS" and not rerun.get("failures"),
          str(rerun["checks"]))
    saved = json.loads(saved_raw)
    check("re-run details == committed details (all keys)",
          rerun.get("details") == saved.get("details"))
    check("re-run files block == committed files block",
          rerun.get("files") == saved.get("files"))
    check("re-run presentation gain == committed 0.9 dB",
          rerun.get("presentationGainDb") == saved.get("presentationGainDb") == 0.9,
          str(rerun.get("presentationGainDb")))

    # --- F. runtime untouched ---
    st = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                        cwd=ROOT, capture_output=True, text=True).stdout.strip()
    check("runtime tree untouched (git status ClientGodot/ clean)", st == "")
    exp = json.loads((ROOT / "ClientGodot/assets/cinematics/CIN_000/scene_export_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    check("v1 export manifest mp4SubVi sha unchanged (50ec6a98)",
          exp["mp4SubVi"]["sha256"].startswith("50ec6a98"))

    result = {
        "checkpoint": "WO37 M-G CP10",
        "validator": "check_fresh_delta_mg_cp10_v1.py",
        "fresh_clone": "mg_cp10_fresh",
        "fresh_head": HEAD,
        "verified_delta": "WO37 M-B CP5 content 257c985 (7 files)",
        "checks": CHECKS,
        "failures": FAIL,
        "details": DETAILS,
        "status": "PASS" if not FAIL else "FAIL",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    print(f"\n{CHECKS['passed']}/{CHECKS['total']} PASS"
          + (f" — FAILURES: {FAIL}" if FAIL else ""))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
