#!/usr/bin/env python3
"""Prologue v1 plumbing fix -- independent checker.

Verifies the delivered fix from real bytes only:
  * the fixed mix carries every CP27 narration take and the
    final Ly An line at its CP27 timeline position (normalized
    cross-correlation >= 0.90 at lag ~0), while the SAME takes
    against the BROKEN mix bytes (read from the git LFS object
    store, sha f026ed3e...) stay <= 0.10 -- the before / after
    contrast on one method;
  * the fixed render is installed byte-identically at the
    Art_Source canonical path and the runtime copy, and every
    registration (mix manifest, film manifest, scene export
    manifest, RUNTIME_AUDIO / RUNTIME_CINEMATICS manifests,
    PLAYBACK_METADATA, the CP3-successor 720p manifest) matches
    the files on disk;
  * the runtime MP4's video stream is bit-identical to the
    pre-fix MP4 (stream hash), its embedded audio is the fixed
    mix (correlation + loudness), and the OGV / subtitled /
    720p-subtitled derivatives carry the same audio;
  * canonical SRT, readable SRT, timing and poster are
    untouched.
Exit 0 = PASS.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_prologue_mix_v2 import (  # noqa: E402
    LYAN_WAV, ROOT, VO_MANIFEST, build_timeline)

FIX_DIR = ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED"
FIX_WAV = FIX_DIR / "PROLOGUE_mix_v1_fixed.wav"
FIX_MANIFEST = FIX_DIR / "PROLOGUE_MIX_V1_FIXED_manifest_v1.json"
AS_MIX = (ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
          / "PROLOGUE_mix_v1.wav")
AS_MIX_MANIFEST = AS_MIX.parent / "PROLOGUE_mix_manifest_v1.json"
RT_MIX = (ROOT / "ClientGodot/assets/audio/mix/prologue"
          / "PROLOGUE_mix_v1.wav")
CINE = ROOT / "ClientGodot/assets/cinematics/CIN_000"
MP4 = CINE / "CIN_000_640x360_30fps.mp4"
OGV = CINE / "CIN_000_640x360_30fps.ogv"
SUB_MP4 = CINE / "CIN_000_640x360_30fps_sub_vi.mp4"
READABLE_SRT = CINE / "CIN_000_vi_readable.srt"
CANON_SRT = CINE / "CIN_000_vi.srt"
POSTER = CINE / "CIN_000_poster.png"
EXPORT_MANIFEST = CINE / "scene_export_manifest_v1.json"
FILM_MANIFEST = (ROOT / "Art_Source/Cinematics/Prologue"
                 / "CIN000_film_manifest_v1.json")
RT_AUDIO = (ROOT / "ClientGodot/assets/audio"
            / "RUNTIME_AUDIO_manifest_v1.json")
RT_CINE = (ROOT / "ClientGodot/assets/cinematics"
           / "RUNTIME_CINEMATICS_manifest_v1.json")
PLAYBACK = (ROOT / "ClientGodot/assets/cinematics"
            / "PLAYBACK_METADATA_v1.json")
S720_MP4 = (ROOT / "Art_Source/Cinematics/Standard720"
            / "CIN_000_subtitled/CIN_000_1280x720_30fps_sub_vi.mp4")
FIX720 = (ROOT / "Implementation/Content/Narrative/Deliveries"
          / "STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json")
BROKEN_SHA = ("f026ed3e10499b42ea4fcc39ada9a1b42e0b5b749d16"
              "ab77208afd54016ffb54")
OLD_MP4_SHA = ("8804931743e31d21c46c269f86b3deb65800668e3ec9c3e"
               "7c38d6a73057c2806")
SR = 48000

CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def probe(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_format",
                          "-show_streams", "-of", "json", str(p)],
                         capture_output=True, text=True).stdout
    return json.loads(out)


def loudnorm_audio(p):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"\{\s*\"input_i\".*?\}", out.stderr, re.S)
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_tp"])


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
    """Max |corr| between two full-length audios over small
    offsets (codec priming)."""
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
    common = subprocess.run(["git", "rev-parse", "--git-common-dir"],
                            cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    p = (ROOT / common / "lfs/objects" / oid[:2] / oid[2:4] / oid)
    assert p.exists(), p
    assert sha256_of(p) == oid
    return p


def parse_srt(text):
    cues = []
    for block in re.split(r"\r?\n\r?\n", text.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*"
                     r"(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        cues.append({
            "start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
            "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0,
            "text": " ".join(lines[2:]).strip()})
    return cues


def main() -> int:
    fixman = load(FIX_MANIFEST)
    fixed_sha = fixman["sha256"]
    check("fixed mix sha == its manifest",
          sha256_of(FIX_WAV) == fixed_sha)
    check("Art_Source canonical mix == fixed render",
          sha256_of(AS_MIX) == fixed_sha)
    check("runtime mix copy == fixed render",
          sha256_of(RT_MIX) == fixed_sha)
    mman = load(AS_MIX_MANIFEST)
    check("mix manifest sha == fixed render",
          mman["sha256"] == fixed_sha)
    check("mix manifest records superseded broken sha",
          mman.get("plumbingFix", {}).get("supersededSha256")
          == BROKEN_SHA)
    check("mix manifest loudness == fixed manifest",
          mman["integratedLufs"] == fixman["integratedLufs"]
          and mman["truePeakDbtp"] == fixman["truePeakDbtp"])

    # ---- correlations: the heart of the fix
    vo = load(VO_MANIFEST)
    _, cues, total, _, lyan_start = build_timeline(vo)
    fixed = decode_mono(FIX_WAV)
    broken = decode_mono(lfs_object(BROKEN_SHA))
    take_dir = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
    for i, s in enumerate(vo["segments"]):
        take = decode_mono(take_dir / s["file"])
        c, lag = best_corr(fixed, take, cues[i]["start"])
        check(f"SEG0{i + 1} take present in fixed mix",
              c >= 0.90 and abs(lag) <= 0.05,
              f"corr {c:+.3f} lag {lag:+.3f}s")
        cb, _ = best_corr(broken, take, cues[i]["start"])
        check(f"SEG0{i + 1} take absent in broken mix (control)",
              abs(cb) <= 0.10, f"corr {cb:+.3f}")
    lyan = decode_mono(LYAN_WAV)
    c, lag = best_corr(fixed, lyan, lyan_start)
    check("Ly An final line present in fixed mix",
          c >= 0.90 and abs(lag) <= 0.05,
          f"corr {c:+.3f} lag {lag:+.3f}s")
    cb, _ = best_corr(broken, lyan, lyan_start)
    check("Ly An final line absent in broken mix (control)",
          abs(cb) <= 0.10, f"corr {cb:+.3f}")
    lufs, tp = loudnorm_audio(FIX_WAV)
    check("fixed mix loudnorm == manifest",
          abs(lufs - fixman["integratedLufs"]) <= 0.05
          and abs(tp - fixman["truePeakDbtp"]) <= 0.05,
          f"{lufs:.2f} LUFS / {tp:.2f} dBTP")
    dur = float(probe(FIX_WAV)["format"]["duration"])
    check("fixed mix duration == 87.367 s",
          abs(dur - 87.3667) <= 0.05, f"{dur:.3f}")

    # ---- runtime film
    exp = load(EXPORT_MANIFEST)
    fman = load(FILM_MANIFEST)
    old_mp4 = lfs_object(OLD_MP4_SHA)
    check("MP4 video stream bit-identical to pre-fix",
          stream_hash(MP4, "0:v:0") == stream_hash(old_mp4, "0:v:0"))
    for label, path, entry in (("MP4", MP4, exp["mp4"]),
                               ("OGV", OGV, exp["ogv"])):
        pr = probe(path)
        kinds = [(s["codec_type"], s["codec_name"])
                 for s in pr["streams"]]
        check(f"{label} streams video+audio",
              [k[0] for k in kinds] == ["video", "audio"],
              str(kinds))
        check(f"{label} sha/size == export manifest",
              sha256_of(path) == entry["sha256"]
              and path.stat().st_size == entry["sizeBytes"])
        emb = decode_mono(path)
        ac = align_corr(emb, fixed)
        check(f"{label} embedded audio is the fixed mix",
              ac >= 0.90, f"corr {ac:.3f}")
        el, et = loudnorm_audio(path)
        check(f"{label} embedded loudness ~= fixed mix",
              abs(el - lufs) <= 0.35, f"{el:.2f} LUFS")
    check("film manifest mixSha == fixed render",
          fman["mixSha256"] == fixed_sha)
    check("film manifest exports == export manifest",
          fman["exports"]["mp4"] == exp["mp4"]
          and fman["exports"]["ogv"] == exp["ogv"])

    # ---- subtitled variant
    sub_pr = probe(SUB_MP4)
    kinds = [s["codec_type"] for s in sub_pr["streams"]]
    check("subtitled streams [video, audio, subtitle]",
          kinds == ["video", "audio", "subtitle"], str(kinds))
    check("subtitled sha == export manifest",
          sha256_of(SUB_MP4) == exp["mp4SubVi"]["sha256"])
    emb_srt = parse_srt(subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(SUB_MP4), "-map",
         "0:s:0", "-f", "srt", "-"], capture_output=True,
        text=True).stdout)
    readable = parse_srt(READABLE_SRT.read_text(encoding="utf-8"))
    ok = len(emb_srt) == len(readable) == 26 and all(
        a["text"] == b["text"]
        and abs(a["start"] - b["start"]) <= 0.05
        and abs(a["end"] - b["end"]) <= 0.05
        for a, b in zip(emb_srt, readable))
    check("embedded mov_text == readable SRT (26 chunks)", ok)
    sl, stp = loudnorm_audio(SUB_MP4)
    check("subtitled loudness == fixed + 2.0 dB, TP <= -0.9",
          abs(sl - (lufs + 2.0)) <= 0.6 and stp <= -0.9,
          f"{sl:.2f} LUFS / {stp:.2f} dBTP")
    check("subtitled audio record == measured",
          abs(exp["mp4SubVi"]["audio"]["loudnessLufs"] - sl) <= 0.05
          and exp["mp4SubVi"]["audio"]["presentationGainDb"] == 2.0)
    emb_sub = decode_mono(SUB_MP4)
    check("subtitled embedded audio is the fixed mix",
          align_corr(emb_sub, fixed) >= 0.90,
          f"corr {align_corr(emb_sub, fixed):.3f}")

    # ---- 720p subtitled
    pr720 = probe(S720_MP4)
    v720 = next(s for s in pr720["streams"]
                if s["codec_type"] == "video")
    check("720p subtitled is 1280x720 with subtitle stream",
          (v720["width"], v720["height"]) == (1280, 720)
          and any(s["codec_type"] == "subtitle"
                  for s in pr720["streams"]))
    check("720p audio stream bit-copied from variant",
          stream_hash(S720_MP4, "0:a:0")
          == stream_hash(SUB_MP4, "0:a:0"))
    man720 = load(FIX720)
    e720 = man720["entries"][0]
    check("720p sha/source == FIX720 manifest",
          sha256_of(S720_MP4) == e720["outSha256"]
          and e720["sourceSha256"] == sha256_of(SUB_MP4))

    # ---- runtime registrations
    ra = load(RT_AUDIO)
    hits = [e for e in ra["files"] if e.get("runtimePath")
            == "assets/audio/mix/prologue/PROLOGUE_mix_v1.wav"]
    check("runtime audio manifest: 783 entries, mix entry fixed",
          ra["totalFiles"] == 783 and len(hits) == 1
          and hits[0]["sha256"] == fixed_sha
          and hits[0]["sizeBytes"] == RT_MIX.stat().st_size)
    rc = load(RT_CINE)
    check("runtime cine manifest prologue == export manifest",
          rc["prologue"]["mp4"] == exp["mp4"]
          and rc["prologue"]["ogv"] == exp["ogv"]
          and rc["prologue"]["mp4SubVi"] == exp["mp4SubVi"])
    check("campaign totals unchanged",
          rc["campaignTotals"] == {"scenes": 20, "shots": 63,
                                   "seconds": 378,
                                   "dialogueCues": 21})
    pm = load(PLAYBACK)
    e0 = next(s for s in pm["scenes"] if s["sceneId"] == "CIN_000")
    em = e0["embeddedMix"]
    check("playback metadata: source mix == fixed render",
          em["sourceMixSha256"] == fixed_sha
          and em["sourceMixMeasuredLUFS"] == fixman["integratedLufs"]
          and em["sourceMixMeasuredTruePeakDBTP"]
          == fixman["truePeakDbtp"])
    ml, _ = loudnorm_audio(MP4)
    check("playback metadata: MP4 embedded loudness == measured",
          abs(e0["video"]["mp4"]["embeddedLoudnessLUFS"] - ml)
          <= 0.15, f"{ml:.2f}")
    ol, _ = loudnorm_audio(OGV)
    check("playback metadata: OGV embedded loudness == measured",
          abs(e0["video"]["ogv"]["embeddedLoudnessLUFS"] - ol)
          <= 0.15, f"{ol:.2f}")

    # ---- untouched neighbours
    check("canonical SRT untouched",
          sha256_of(CANON_SRT) == exp["srtSha256"])
    check("readable SRT untouched",
          sha256_of(READABLE_SRT) == exp["readableSrt"]["sha256"])
    check("poster untouched",
          sha256_of(POSTER) == exp["poster"]["sha256"])
    check("timing untouched",
          sha256_of(CINE / "CIN_000_timing_v1.json")
          == exp["timingSha256"])

    fails = [c for c in CHECKS if not c[1]]
    print(f"\n{len(CHECKS) - len(fails)}/{len(CHECKS)} PASS, "
          f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
