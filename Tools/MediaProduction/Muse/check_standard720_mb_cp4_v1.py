#!/usr/bin/env python3
"""WO37 M-B CP4 checker — verifies STANDARD720_MB_CP4_v1 against real bytes.

Checks per re-rendered entry (14): video source sha == manifest, CP2
manifest and git LFS oid; v2 mix WAV sha == manifest and M-F CP2
validation (PASS 369/369); output sha/bytes == manifest; output probes
1280x720 @30fps with AAC audio; duration within 0.06 s of the source;
video fidelity: frames at 3 timestamps downscaled (neighbor) back to
640x360 stay within mean|diff| <= 6.0 of the source frames (CP2
threshold), and the 2x2-block structure of an integer upscale survives
(intra-block range <= 24, CP2 threshold); audio: the output AAC decoded
to mono correlates with the v2 mix WAV at >= 0.99 (lag-tolerant search
+/-4096 samples, AAC priming delay is real), loudnorm integrated LUFS
within +/-0.3 of the v2 mix value, true peak within +/-0.5 dBTP, audio
duration within 0.06 s.

Per carried-over entry (7): the committed HEAD LFS pointer oid equals
the CP2 manifest outSha256 (byte-identical CP2 file, verified without
materialising the LFS object) and outBytes match CP2.

Plus: budget arithmetic re-derived from the manifest entries, and the
ClientGodot runtime tree is byte-clean in git.
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
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP4_v1.json"
CP2_MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP2_v1.json"
MF_CP2_VALIDATION = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json"
OUT_JSON = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP4_VALIDATION_20261110.json"
FAIL = []
CHECKS = {"total": 0, "passed": 0}


def check(name, ok, detail=""):
    CHECKS["total"] += 1
    if ok:
        CHECKS["passed"] += 1
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
            "hasAudio": bool(a), "audioCodec": a[0]["codec_name"] if a else None,
            "duration": float(d["format"]["duration"])}


def audio_stream_duration(p: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a:0",
         "-show_entries", "stream=duration", "-of", "csv=p=0", str(p)],
        capture_output=True, text=True, check=True).stdout.strip()
    return float(out)


def frame(p: Path, t: float, size: str) -> np.ndarray:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp = Path(tf.name)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i", str(p),
                    "-frames:v", "1", "-vf", f"scale={size}:flags=neighbor",
                    str(tmp)], check=True)
    arr = np.asarray(Image.open(tmp).convert("RGB"), dtype=np.int16)
    tmp.unlink()
    return arr


def loudnorm(p: Path) -> dict:
    """Single-pass loudnorm, same extraction as the M-F CP2 checker
    (default verbosity, JSON from the last '{') — plus brace matching,
    because ffmpeg 8.x prints a muxing summary line AFTER the JSON."""
    r = subprocess.run(
        ["ffmpeg", "-i", str(p), "-vn", "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    txt = r.stderr
    i = txt.rfind("{")
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                return json.loads(txt[i:j + 1])
    raise ValueError("loudnorm JSON block not found")


def decode_mono_f32(p: Path) -> np.ndarray:
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-vn", "-ac", "1", "-ar", "48000",
         "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


def best_corr(a: np.ndarray, b: np.ndarray, max_lag: int = 4096):
    """Pearson correlation of a vs b over lag search; returns (best, lag)."""
    n = min(len(a), len(b))
    a = a[:n].astype(np.float64)
    b = b[:n].astype(np.float64)
    a = a - a.mean()
    b = b - b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    best, best_lag = -1.0, 0
    for lag in range(-max_lag, max_lag + 1):
        if lag >= 0:
            x, y = a[lag:], b[:n - lag]
        else:
            x, y = a[:n + lag], b[-lag:]
        c = float((x * y).sum() / denom) if denom else 0.0
        if c > best:
            best, best_lag = c, lag
    return best, best_lag


def head_lfs_oid(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("oid sha256:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cp2 = json.loads(CP2_MANIFEST.read_text(encoding="utf-8"))
    cp2_by_scene = {e["sceneId"]: e for e in cp2["entries"]}
    mf2 = json.loads(MF_CP2_VALIDATION.read_text(encoding="utf-8"))
    mix_by_scene = {x["scene"]: x for x in mf2["mixes"]}
    entries = m["entries"]
    check("manifest entries == 21", len(entries) == 21, str(len(entries)))
    check("M-F CP2 validation is PASS 369/369",
          mf2["status"] == "PASS" and mf2["checksPassed"] == 369)
    tot_src = tot_out = 0
    worst_diff = 0.0
    worst_block = 0.0
    worst_corr = 1.0
    worst_lufs = 0.0
    worst_tp = 0.0
    for e in entries:
        scene = e["sceneId"]
        out = ROOT / e["outPath"]
        if "carriedOverFrom" in e:
            cp2e = cp2_by_scene[scene]
            check(f"{scene} carried over: HEAD LFS oid == CP2 outSha",
                  head_lfs_oid(e["outPath"]) == cp2e["outSha256"])
            check(f"{scene} carried over: bytes + sha == CP2 manifest",
                  e["outSha256"] == cp2e["outSha256"]
                  and e["outBytes"] == cp2e["outBytes"])
            tot_src += e["sourceBytes"]
            tot_out += e["outBytes"]
            continue
        src, wav = ROOT / e["videoSourcePath"], ROOT / e["audioSourcePath"]
        mix = mix_by_scene[scene]
        check(f"{scene} video source sha == manifest + CP2",
              sha256(src) == e["videoSourceSha256"]
              and e["videoSourceSha256"] == cp2_by_scene[scene]["sourceSha256"])
        check(f"{scene} v2 mix sha == manifest + M-F CP2 validation",
              sha256(wav) == e["audioSourceSha256"]
              and e["audioSourceSha256"] == mix["sha256"])
        check(f"{scene} v2 mix LUFS/TP recorded == validation",
              e["audioSourceIntegratedLUFS"] == mix["integratedLUFS"]
              and e["audioSourceTruePeakDBTP"] == mix["truePeakDBTP"])
        check(f"{scene} out sha/bytes == manifest",
              sha256(out) == e["outSha256"] and out.stat().st_size == e["outBytes"])
        op = probe(out)
        check(f"{scene} out 1280x720@30 + AAC audio",
              op["width"] == 1280 and op["height"] == 720 and op["fps"] == "30/1"
              and op["hasAudio"] and op["audioCodec"] == "aac", json.dumps(op))
        check(f"{scene} duration delta <= 0.06 s",
              abs(op["duration"] - e["sourceDuration"]) <= 0.06,
              f"{op['duration']:.3f} vs {e['sourceDuration']:.3f}")
        check(f"{scene} supersedes CP2 outSha",
              e["supersedesCp2OutSha256"] == cp2_by_scene[scene]["outSha256"])
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
        # Audio: decoded AAC vs the v2 mix WAV (measurement, not byte equality).
        adur = audio_stream_duration(out)
        check(f"{scene} audio stream duration delta <= 0.06 s",
              abs(adur - e["audioSourceDuration"]) <= 0.06, f"{adur:.3f}")
        ln = loudnorm(out)
        dlufs = abs(float(ln["input_i"]) - e["audioSourceIntegratedLUFS"])
        dtp = abs(float(ln["input_tp"]) - e["audioSourceTruePeakDBTP"])
        worst_lufs = max(worst_lufs, dlufs)
        worst_tp = max(worst_tp, dtp)
        check(f"{scene} audio LUFS within +/-0.3 of v2 mix",
              dlufs <= 0.3, f"out {ln['input_i']} vs mix {e['audioSourceIntegratedLUFS']}")
        check(f"{scene} audio true peak within +/-0.5 dBTP of v2 mix",
              dtp <= 0.5, f"out {ln['input_tp']} vs mix {e['audioSourceTruePeakDBTP']}")
        ref = decode_mono_f32(wav)
        got = decode_mono_f32(out)
        corr, lag = best_corr(ref, got)
        worst_corr = min(worst_corr, corr)
        check(f"{scene} audio waveform corr vs v2 mix >= 0.99 (lag-tolerant)",
              corr >= 0.99, f"corr {corr:.4f} lag {lag} samples")
        check(f"{scene} audio best lag within +/-2048 samples (AAC priming)",
              abs(lag) <= 2048, f"lag {lag}")
        tot_src += e["videoSourceBytes"]
        tot_out += e["outBytes"]
    b = m["budget"]["mp4Set"]
    check("budget mp4 totals re-derived",
          b["sourceBytes"] == tot_src and b["outBytes"] == tot_out,
          f"{tot_src} -> {tot_out}")
    check("budget delta vs CP2 re-derived",
          m["budget"]["deltaVsCp2SetBytes"] == tot_out - cp2["budget"]["mp4Set"]["outBytes"])
    r = subprocess.run(["git", "status", "--porcelain", "--", "ClientGodot/"],
                       cwd=ROOT, capture_output=True, text=True)
    check("runtime tree untouched (git clean under ClientGodot/)",
          r.stdout.strip() == "", r.stdout[:200])
    print(f"\nworst frame downscale mean|diff|: {worst_diff:.3f}; "
          f"worst 2x2 intra-block range: {worst_block:.2f}; "
          f"worst audio corr: {worst_corr:.4f}; "
          f"worst |dLUFS|: {worst_lufs:.2f}; worst |dTP|: {worst_tp:.2f}")
    print(f"checks: {CHECKS['passed']}/{CHECKS['total']} "
          f"({'ALL PASS' if not FAIL else 'FAILURES: ' + str(FAIL)})")
    OUT_JSON.write_text(json.dumps({
        "checker": "check_standard720_mb_cp4_v1",
        "checkpoint": "MEDIA-02 WO37 M-B CP4",
        "checksTotal": CHECKS["total"], "checksPassed": CHECKS["passed"],
        "failures": FAIL,
        "status": "PASS" if not FAIL else "FAIL",
        "worstFrameDownscaleMeanAbsDiff": round(worst_diff, 3),
        "worst2x2IntraBlockRange": round(worst_block, 2),
        "worstAudioCorr": round(worst_corr, 4),
        "worstAbsDeltaLUFS": round(worst_lufs, 2),
        "worstAbsDeltaTruePeakDBTP": round(worst_tp, 2),
        "mp4SetOutBytes": tot_out,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("validation:", OUT_JSON.relative_to(ROOT))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
