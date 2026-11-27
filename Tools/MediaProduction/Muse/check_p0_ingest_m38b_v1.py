#!/usr/bin/env python3
"""WO38 M38-B checker: verify P0_INGEST_M38B_SUBSET_v1.json against real bytes.

Checks: manifest/file hashes+sizes; stream shape of candidate and runtime
files (exactly 1 video + 1 audio, codecs, 640x360@30, 48 kHz stereo);
durations; SRT encoding + locked windows; runtime tree unchanged vs the
M38-A runtime-proof hashes; candidate OGV loudness vs the mix v3 WAV masters;
a frame spot-check proving the OGV carries the B picture (close to the B MP4,
clearly different from the A runtime frame inside a pose beat); policy facts
(audio-path rule present, NOT_AUDITIONED status, new files only in Art_Source).
"""
import hashlib
import io
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/P0_INGEST_M38B_SUBSET_v1.json"
M38A_SUBSET = ROOT / "Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json"

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudnorm_i(p: Path) -> float:
    import re
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-vn", "-af",
         "loudnorm=I=-23:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r'"input_i"\s*:\s*"([-\d.]+)"', r.stderr)
    return float(m.group(1))


def frame(p: Path, t: float) -> np.ndarray:
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(p), "-frames:v", "1",
         "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True, check=True)
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGB"), dtype=np.int16)


def main() -> int:
    man = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("manifest fileCount", man["fileCount"] == len(man["files"]),
          f"{man['fileCount']} entries")

    bad = []
    for e in man["files"]:
        p = ROOT / e["path"]
        if not p.exists() or p.stat().st_size != e["sizeBytes"] or sha256(p) != e["sha256"]:
            bad.append(e["path"])
    check("all file hashes+sizes", not bad, "; ".join(bad))

    dur_expect = {"CIN_001": 36.0, "CIN_002": 18.0, "CIN_004": 18.0}
    for s in man["scenes"]:
        sid = s["sceneId"]
        for label, e, vc, ac in (
            ("candidate MP4", s["candidateVideo"]["mp4"], "h264", "aac"),
            ("candidate OGV", s["candidateVideo"]["ogv"], "theora", "vorbis"),
            ("runtime MP4", s["runtimeCurrent"]["mp4"], "h264", "aac"),
            ("runtime OGV", s["runtimeCurrent"]["ogv"], "theora", "vorbis"),
        ):
            d = probe(ROOT / e["path"])
            st = d["streams"]
            v = [x for x in st if x["codec_type"] == "video"]
            a = [x for x in st if x["codec_type"] == "audio"]
            ok = (len(st) == 2 and len(v) == 1 and len(a) == 1
                  and v[0]["codec_name"] == vc and a[0]["codec_name"] == ac
                  and v[0]["width"] == 640 and v[0]["height"] == 360
                  and v[0]["r_frame_rate"] == "30/1"
                  and int(a[0]["sample_rate"]) == 48000 and a[0]["channels"] == 2
                  and abs(float(d["format"]["duration"]) - dur_expect[sid]) <= 0.15)
            check(f"{sid} {label} stream shape", ok,
                  f"dur={d['format']['duration']}")
        raw = (ROOT / s["runtimeCurrent"]["srt"]["path"]).read_bytes()
        text = raw.decode("utf-8")
        enc_ok = (not raw.startswith(b"\xef\xbb\xbf") and b"\r\n" not in raw
                  and unicodedata.is_normalized("NFC", text))
        win = s["dialogue"]["windowSeconds"]
        import re
        m = re.search(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)", text)
        secs = lambda g: int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000.0
        parsed = [secs(m.groups()[:4]), secs(m.groups()[4:8])]
        check(f"{sid} SRT encoding+window", enc_ok and parsed == win and text.count("-->") == 1,
              f"window={parsed}")
        d_lufs = abs(loudnorm_i(ROOT / s["candidateVideo"]["ogv"]["path"])
                     - loudnorm_i(ROOT / s["embeddedSoundtrack"]["sourceMixWav"]["path"]))
        check(f"{sid} OGV loudness vs WAV master", d_lufs <= 0.6, f"delta={d_lufs:.2f} LUFS")

    m38a = json.loads(M38A_SUBSET.read_text(encoding="utf-8"))
    proof = {e["path"]: e["sha256"] for e in m38a["runtimeUnchangedProof"]}
    drift = []
    for s in man["scenes"]:
        for k in ("mp4", "ogv", "poster"):
            e = s["runtimeCurrent"][k]
            if proof.get(e["path"]) != e["sha256"]:
                drift.append(e["path"])
    check("runtime tree unchanged vs M38-A proof", not drift, "; ".join(drift))

    f_ogv = frame(ROOT / "Art_Source/Cinematics/P0_Motion/candidate_m38a/CIN_001_candidateB_640x360_30fps.ogv", 27.0)
    f_b = frame(ROOT / "Art_Source/Cinematics/P0_Motion/takes/CIN_001_pose_640x360_30fps.mp4", 27.0)
    f_a = frame(ROOT / "ClientGodot/assets/cinematics/CIN_001/CIN_001_640x360_30fps.mp4", 27.0)
    d_b = float(np.abs(f_ogv - f_b).mean())
    d_a = float(np.abs(f_ogv - f_a).mean())
    check("OGV frame ~= B MP4 frame @27s (S05 beat)", d_b <= 12.0, f"meanAbsDiff={d_b:.2f}")
    check("OGV frame != A runtime frame @27s", d_a >= 3.0, f"meanAbsDiff={d_a:.2f}")

    rule = man["audioPathRule"]["rule"]
    check("exactly-one-audio-path rule present",
          "EXACTLY ONE" in rule and "EMBEDDED_SOUNDTRACK_ONLY" in rule)
    check("honest status (NOT_AUDITIONED, no self-PASS)",
          "NOT_AUDITIONED" in man["status"] and "NOT_AUDITIONED" in man["auditionStatus"])
    new_files = [e["path"] for e in man["files"] if "NEW in M38-B" in e["role"]]
    check("new files only under Art_Source",
          len(new_files) == 3 and all(p.startswith("Art_Source/") for p in new_files),
          "; ".join(new_files))
    gs = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                        capture_output=True, text=True, cwd=ROOT).stdout.strip()
    check("git: no runtime modifications", gs == "", gs[:120])

    failed = [r for r in results if not r["pass"]]
    print(f"\n{len(results) - len(failed)}/{len(results)} PASS")
    if "--out" in sys.argv:
        outp = Path(sys.argv[sys.argv.index("--out") + 1])
        outp.write_text(json.dumps(
            {"validator": "check_p0_ingest_m38b_v1", "manifest": str(MANIFEST.relative_to(ROOT)),
             "total": len(results), "passed": len(results) - len(failed),
             "failed": len(failed), "results": results}, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
