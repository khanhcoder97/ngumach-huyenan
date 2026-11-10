#!/usr/bin/env python3
"""WO37 M-B CP2 checker — verifies STANDARD720_MB_CP2_v1 against real bytes.

Checks per entry: manifest sha/bytes match the file on disk; source bytes
equal the git LFS oid (the delivered master); output probes 1280x720 @30fps
with an audio stream; duration within 0.06 s of the source; the audio track
is bit-identical to the source's (elementary-stream extraction compare);
video fidelity: frames at 3 timestamps downscaled (neighbor) back to
640x360 stay within a small mean-abs-diff of the source frames, and the
2x2-block structure of an integer upscale survives (mean intra-block range
reported). Plus: budget arithmetic re-derived from the manifest entries,
sample OGV probes, and the ClientGodot runtime tree is byte-clean in git.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP2_v1.json"
FAIL = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if not ok:
        FAIL.append(name)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    return {"width": v["width"], "height": v["height"], "fps": v["r_frame_rate"],
            "hasAudio": bool(a), "duration": float(d["format"]["duration"])}


def frame(p: Path, t: float, size: str) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp = Path(tf.name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(p),
                    "-frames:v", "1", "-vf", f"scale={size}:flags=neighbor",
                    str(tmp)], check=True)
    arr = np.asarray(Image.open(tmp).convert("RGB"), dtype=np.int16)
    tmp.unlink()
    return arr


def audio_sha(p: Path) -> str:
    with tempfile.NamedTemporaryFile(suffix=".aac", delete=False) as tf:
        tmp = Path(tf.name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(p),
                    "-map", "0:a", "-c:a", "copy", "-f", "adts", str(tmp)], check=True)
    s = sha256(tmp)
    tmp.unlink()
    return s


def main() -> int:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = m["entries"]
    check("manifest entries == 21", len(entries) == 21, str(len(entries)))
    tot_src = tot_out = 0
    worst_diff = 0.0
    worst_block = 0.0
    for e in entries:
        scene = e["sceneId"]
        src, out = ROOT / e["sourcePath"], ROOT / e["outPath"]
        check(f"{scene} source sha == manifest", sha256(src) == e["sourceSha256"])
        check(f"{scene} out sha/bytes == manifest",
              sha256(out) == e["outSha256"] and out.stat().st_size == e["outBytes"])
        op = probe(out)
        check(f"{scene} out 1280x720@30 + audio",
              op["width"] == 1280 and op["height"] == 720 and op["fps"] == "30/1"
              and op["hasAudio"], json.dumps(op))
        check(f"{scene} duration delta <= 0.06 s",
              abs(op["duration"] - e["sourceDuration"]) <= 0.06,
              f"{op['duration']:.3f} vs {e['sourceDuration']:.3f}")
        check(f"{scene} audio bit-identical (stream copy)",
              audio_sha(src) == audio_sha(out))
        dur = e["sourceDuration"]
        for t in (1.0, dur / 2, dur - 1.0):
            a = frame(src, t, "640:360")
            b = frame(out, t, "640:360")
            diff = float(np.abs(a - b).mean())
            worst_diff = max(worst_diff, diff)
            check(f"{scene} frame@{t:.1f}s downscale mean|diff| <= 6.0",
                  diff <= 6.0, f"{diff:.3f}")
            full = frame(out, t, "1280:720").astype(np.int16)
            blocks = full.reshape(360, 2, 640, 2, 3)
            rng = float((blocks.max(axis=(1, 3)) - blocks.min(axis=(1, 3))).mean())
            worst_block = max(worst_block, rng)
            check(f"{scene} frame@{t:.1f}s 2x2 intra-block range <= 24",
                  rng <= 24.0, f"{rng:.2f}")
        if "ogvSample" in e:
            g = ROOT / e["ogvSample"]["outPath"]
            gp = probe(g)
            check(f"{scene} OGV sample sha/bytes + 1280x720 + audio",
                  sha256(g) == e["ogvSample"]["outSha256"]
                  and g.stat().st_size == e["ogvSample"]["outBytes"]
                  and gp["width"] == 1280 and gp["height"] == 720 and gp["hasAudio"])
        tot_src += e["sourceBytes"]
        tot_out += e["outBytes"]
    b = m["budget"]["mp4Set"]
    check("budget mp4 totals re-derived",
          b["sourceBytes"] == tot_src and b["outBytes"] == tot_out,
          f"{tot_src} -> {tot_out}")
    r = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                       cwd=ROOT, capture_output=True, text=True)
    check("runtime tree untouched (git clean under ClientGodot/)",
          r.stdout.strip() == "", r.stdout[:200])
    print(f"\nworst frame downscale mean|diff|: {worst_diff:.3f}; "
          f"worst 2x2 intra-block range: {worst_block:.2f}")
    print(f"{'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)}")
    Path("/tmp/mb_cp2_check_summary.txt").write_text(
        f"failures={len(FAIL)} worst_diff={worst_diff:.3f} worst_block={worst_block:.2f}\n")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
