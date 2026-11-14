#!/usr/bin/env python3
"""WO37 M-B CP3 checker — verifies STANDARD720_SUBTITLED_MB_CP3_v1 against real bytes.

Checks: manifest sha/bytes match the file on disk; source bytes equal the
git LFS oid and the CP28 record; output probes 1280x720 @30fps with audio
AND the mov_text subtitle track (language vie); duration within 0.06 s of
the source; the audio track is bit-identical to the source's
(elementary-stream extraction compare); video fidelity: frames at 3
timestamps downscaled (neighbor) back to 640x360 stay within mean-abs-diff
6.0 of the source frames (same threshold as the CP2 checker), and the 2x2
intra-block range stays <= 24 (same threshold as CP2). Plus: budget
arithmetic re-derived, and the ClientGodot runtime tree is byte-clean
in git.
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
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_MB_CP3_v1.json"
FAIL = []
NPASS = [0]


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
    if ok:
        NPASS[0] += 1
    else:
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
         "stream=codec_type,codec_name,width,height,r_frame_rate:stream_tags=language",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    s = [x for x in d["streams"] if x["codec_type"] == "subtitle"]
    return {"width": v["width"], "height": v["height"], "fps": v["r_frame_rate"],
            "hasAudio": bool(a),
            "subtitle": [{"codec": x["codec_name"],
                          "language": x.get("tags", {}).get("language")} for x in s],
            "duration": float(d["format"]["duration"])}


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
    check("manifest entries == 1", len(entries) == 1, str(len(entries)))
    check("manifest checkpoint == WO37 M-B CP3", m.get("checkpoint") == "WO37 M-B CP3")
    e = entries[0]
    src, out = ROOT / e["sourcePath"], ROOT / e["outPath"]
    check("source sha == manifest", sha256(src) == e["sourceSha256"])
    check("source sha == CP28 record prefix 2aae25e4",
          e["sourceSha256"].startswith("2aae25e4"))
    r = subprocess.run(["git", "show", f"HEAD:{e['sourcePath']}"], cwd=ROOT,
                       capture_output=True, text=True)
    oid = next((ln.split(":", 1)[1].strip() for ln in r.stdout.splitlines()
                if ln.startswith("oid sha256:")), None)
    check("source bytes == git LFS oid", oid == e["sourceSha256"], str(oid))
    check("out sha/bytes == manifest",
          sha256(out) == e["outSha256"] and out.stat().st_size == e["outBytes"])
    op = probe(out)
    check("out 1280x720@30 + audio",
          op["width"] == 1280 and op["height"] == 720 and op["fps"] == "30/1"
          and op["hasAudio"], json.dumps(op))
    check("out keeps mov_text subtitle track (vie)",
          len(op["subtitle"]) == 1 and op["subtitle"][0]["codec"] == "mov_text"
          and op["subtitle"][0]["language"] == "vie", json.dumps(op["subtitle"]))
    check("duration delta <= 0.06 s",
          abs(op["duration"] - e["sourceDuration"]) <= 0.06,
          f"{op['duration']:.3f} vs {e['sourceDuration']:.3f}")
    check("audio bit-identical (stream copy)", audio_sha(src) == audio_sha(out))
    dur = e["sourceDuration"]
    worst_diff = 0.0
    worst_block = 0.0
    for t in (1.0, dur / 2, dur - 1.0):
        a = frame(src, t, "640:360")
        b = frame(out, t, "640:360")
        diff = float(np.abs(a - b).mean())
        worst_diff = max(worst_diff, diff)
        check(f"frame@{t:.1f}s downscale mean|diff| <= 6.0", diff <= 6.0, f"{diff:.3f}")
        full = frame(out, t, "1280:720").astype(np.int16)
        blocks = full.reshape(360, 2, 640, 2, 3)
        rng = float((blocks.max(axis=(1, 3)) - blocks.min(axis=(1, 3))).mean())
        worst_block = max(worst_block, rng)
        check(f"frame@{t:.1f}s 2x2 intra-block range <= 24", rng <= 24.0, f"{rng:.2f}")
    b = m["budget"]["mp4Set"]
    check("budget re-derived",
          b["files"] == 1 and b["sourceBytes"] == e["sourceBytes"]
          and b["outBytes"] == e["outBytes"]
          and abs(b["ratio"] - round(e["outBytes"] / e["sourceBytes"], 3)) < 1e-9
          and abs(b["totalDuration"] - round(e["sourceDuration"], 3)) < 1e-9,
          json.dumps(b))
    r = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                       cwd=ROOT, capture_output=True, text=True)
    check("runtime tree clean in git", r.stdout.strip() == "", r.stdout.strip()[:200])
    print(f"worst downscale mean|diff| {worst_diff:.3f}; worst 2x2 block range {worst_block:.2f}")
    print(f"RESULT: {NPASS[0]} PASS, {len(FAIL)} FAIL" + (f" — {FAIL}" if FAIL else ""))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
