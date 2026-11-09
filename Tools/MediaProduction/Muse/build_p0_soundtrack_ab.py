#!/usr/bin/env python3
"""WO37 M-B CP1 - P0 soundtrack A/B (v1 vs v2 vs v3).

Closes the remainder of WO37 big checkpoint 2 (see M-C CP2 report §8 and
CP54 report "Next": "soundtrack A/B for P0 (v1 vs v2 vs v3)").

Design: the SAME candidate-B picture (M38-A review reel, video stream
copied byte-identical) in all three reels; only the soundtrack differs.
  v1 = ported PackV1 music + ambience + stingers (checkpoint 20)
  v2 = composed music + stingers, ported ambience (checkpoint 29)
  v3 = fully composed music + stingers + ambience (checkpoint 31)
VO takes are identical in all three versions (same CP04 draft VO, same
placements/gains/ducking per the v2/v3 mix verdicts), so the A/B isolates
the music/ambience character: v1-vs-v2 = music+stinger substitution,
v2-vs-v3 = ambience substitution.

All numbers are measured from real bytes (ffprobe / ffmpeg loudnorm /
astats / numpy waveform diff). Nothing is a listening PASS: the pack is
DRAFT / NOT_AUDITIONED; Codex/director picks the winner.

Outputs (all under policy roots):
  Art_Source/Cinematics/P0_Motion/soundtrack_ab/
    P0_soundtrack_v1_72s_640x360_30fps.mp4
    P0_soundtrack_v2_72s_640x360_30fps.mp4
    P0_soundtrack_v3_72s_640x360_30fps.mp4
    P0_SOUNDTRACK_AB_v1.json
  Implementation/Reports/MuseMedia/p0_soundtrack_ab_playlist.txt

Runtime is NOT modified: no file under ClientGodot/ is touched.
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "Art_Source/Cinematics/P0_Motion/soundtrack_ab"
REEL_SRC = ROOT / "Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_review_72s_640x360_30fps.mp4"
REEL_SRC_SHA = "a9ae424cd95de09899dfd8bcff40a1ca572f571f7043d3259e10f14c0110780c"

MIXES = {
    "v1": {
        "label": "ported PackV1 stems (checkpoint 20)",
        "wav": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT/P0_mix_review_72s_draft_v1.wav",
        "sha256": "2a982b5f8e92bebd2f1b2e637f9c3e8cad550c4fbf989566f6c257afc40ded81",
        "cp9": {"lufs": -22.66, "truePeakDbtp": -1.46},
    },
    "v2": {
        "label": "composed music + stingers, ported ambience (checkpoint 29)",
        "wav": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/P0_mix_review_72s_draft_v2.wav",
        "sha256": "4a1bc54e7c7f998b85685de73b2b475d9fad731e5730a506cba28c055ed81ced",
        "cp9": {"lufs": -22.72, "truePeakDbtp": -1.51},
    },
    "v3": {
        "label": "fully composed music + stingers + ambience (checkpoint 31)",
        "wav": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_mix_review_72s_draft_v3.wav",
        "sha256": "09f7cf8ecf302a8b8b73d8d18064e9159c4014b984457a688783d1db938d8b6a",
        "cp9": {"lufs": -22.49, "truePeakDbtp": -1.66},
    },
}

# Reel-local seconds. Reel = CIN_001 [0,36) + CIN_002 [36,54) + CIN_004 [54,72).
SCENES = [
    {"sceneId": "CIN_001", "reelSeconds": [0.0, 36.0]},
    {"sceneId": "CIN_002", "reelSeconds": [36.0, 54.0]},
    {"sceneId": "CIN_004", "reelSeconds": [54.0, 72.0]},
]
# Locked dialogue windows (timing manifests; scene-local -> reel-local).
VO_WINDOWS = [
    {"shotId": "CIN_001_S05", "speaker": "Ly An", "windowSceneSeconds": [24.8, 28.5],
     "windowReelSeconds": [24.8, 28.5], "text": "Đầu kia! Giữ giúp tôi đầu kia!"},
    {"shotId": "CIN_002_S02", "speaker": "Tạ Vân Khanh", "windowSceneSeconds": [7.0, 11.0],
     "windowReelSeconds": [43.0, 47.0], "text": "Trên bờ chỉ nghe nửa tiếng. Phần còn lại ở dưới ấy."},
    {"shotId": "CIN_004_S02", "speaker": "Ly An (off-screen)", "windowSceneSeconds": [7.5, 9.5],
     "windowReelSeconds": [61.5, 63.5], "text": "Nó cứ tránh chỗ nước ấy."},
]
SR = 48000


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"command failed ({r.returncode}): {' '.join(cmd)}\n{r.stderr[-2000:]}")
    return r


def probe(p: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,bit_rate",
             "-show_entries", "format=duration,size",
             "-of", "json", str(p)])
    return json.loads(r.stdout)


def loudnorm(p: Path, start: float | None = None, dur: float | None = None) -> dict:
    cmd = ["ffmpeg", "-hide_banner", "-v", "info"]
    if start is not None:
        cmd += ["-ss", str(start)]
    if dur is not None:
        cmd += ["-t", str(dur)]
    cmd += ["-i", str(p), "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"loudnorm failed for {p}: {r.stderr[-1000:]}")
    m = re.search(r"\{[^}]*\"input_i\"[^}]*\}", r.stderr, re.S)
    if not m:
        raise RuntimeError(f"loudnorm parse failed for {p}:\n{r.stderr[-1500:]}")
    j = json.loads(m.group(0))
    return {"integratedLUFS": round(float(j["input_i"]), 2),
            "truePeakDBTP": round(float(j["input_tp"]), 2)}


def window_stats(p: Path, start: float, dur: float) -> dict:
    """RMS + peak level (dBFS, Overall) of one time window, from real bytes."""
    cmd = ["ffmpeg", "-hide_banner", "-v", "info", "-ss", str(start), "-t", str(dur),
           "-i", str(p), "-vn", "-af", "astats=metadata=1:reset=1", "-f", "null", "-"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"astats failed for {p}: {r.stderr[-1000:]}")
    overall = r.stderr.rsplit("Overall", 1)[-1]
    rms = re.search(r"RMS level dB:\s*(-?[\d.]+)", overall)
    peak = re.search(r"Peak level dB:\s*(-?[\d.]+)", overall)
    if not rms or not peak:
        raise RuntimeError(f"astats parse failed for {p}:\n{r.stderr[-1500:]}")
    return {"rmsDbfs": round(float(rms.group(1)), 2),
            "peakDbfs": round(float(peak.group(1)), 2)}


def video_stream_md5(p: Path) -> str:
    r = run(["ffmpeg", "-v", "error", "-i", str(p), "-map", "0:v", "-c", "copy",
             "-f", "md5", "-"])
    m = re.search(r"MD5=([0-9a-f]{32})", r.stdout)
    if not m:
        raise RuntimeError(f"video md5 failed for {p}: {r.stdout}")
    return m.group(1)


def decode_mono(p: Path) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p),
                        "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {p}: {r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").astype(np.float64)


def diff_stats(a: np.ndarray, b: np.ndarray, start: float, end: float) -> dict:
    i0, i1 = int(start * SR), int(end * SR)
    x, y = a[i0:i1], b[i0:i1]
    d = x - y
    rms_x = float(np.sqrt(np.mean(x ** 2)))
    rms_d = float(np.sqrt(np.mean(d ** 2)))
    corr = float(np.corrcoef(x, y)[0, 1]) if rms_x > 0 and float(np.sqrt(np.mean(y ** 2))) > 0 else 0.0
    return {"diffRmsRatio": round(rms_d / rms_x, 4) if rms_x > 0 else None,
            "correlation": round(corr, 4)}


def git_clean(paths) -> bool:
    r = subprocess.run(["git", "status", "--porcelain", "--"] + [str(x) for x in paths],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() == ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not git_clean(["ClientGodot/"]):
        raise RuntimeError("ClientGodot/ is not clean before build; refusing to touch runtime")

    # --- verify inputs are the exact bytes the manifests record ---
    if sha256(REEL_SRC) != REEL_SRC_SHA:
        raise RuntimeError("candidate reel SHA mismatch; refusing to build from wrong picture")
    for ver, m in MIXES.items():
        if sha256(m["wav"]) != m["sha256"]:
            raise RuntimeError(f"{ver} mix WAV SHA mismatch; refusing to build")

    src_probe = probe(REEL_SRC)
    src_video_md5 = video_stream_md5(REEL_SRC)
    src_loud = loudnorm(REEL_SRC)

    decoded = {ver: decode_mono(m["wav"]) for ver, m in MIXES.items()}
    for ver, sig in decoded.items():
        assert len(sig) == 72 * SR, f"{ver} master is not exactly 72s of audio"

    reels = []
    for ver in ("v1", "v2", "v3"):
        out = OUT_DIR / f"P0_soundtrack_{ver}_72s_640x360_30fps.mp4"
        # No -shortest: it drops the last video frames when muxing a copied
        # video stream against a fresh AAC encode (observed: 2157/2160 frames).
        # The candidate reel's audio runs 72.021333 s (AAC priming) while its
        # video is exactly 72.000 s / 2160 frames; apad fills the 21 ms tail
        # with digital silence so the video stream stays whole and identical.
        run(["ffmpeg", "-y", "-v", "error", "-i", str(REEL_SRC), "-i", str(MIXES[ver]["wav"]),
             "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
             "-af", "apad", "-t", "72.021333", str(out)])
        pr = probe(out)
        vstreams = [s for s in pr["streams"] if s["codec_type"] == "video"]
        astreams = [s for s in pr["streams"] if s["codec_type"] == "audio"]
        assert len(vstreams) == 1 and len(astreams) == 1, f"{ver}: expected 1v+1a, got {pr['streams']}"
        vmd5 = video_stream_md5(out)
        assert vmd5 == src_video_md5, f"{ver}: video stream differs from candidate reel"
        master_loud = loudnorm(MIXES[ver]["wav"])
        reel_loud = loudnorm(out)
        # Cross-check re-measured master loudness against the CP9 ear pack.
        cp9 = MIXES[ver]["cp9"]
        if abs(master_loud["integratedLUFS"] - cp9["lufs"]) > 0.05 or \
           abs(master_loud["truePeakDBTP"] - cp9["truePeakDbtp"]) > 0.05:
            raise RuntimeError(f"{ver}: re-measured master loudness {master_loud} "
                               f"does not match CP9 {cp9}")
        reels.append({
            "version": ver,
            "label": MIXES[ver]["label"],
            "file": f"Art_Source/Cinematics/P0_Motion/soundtrack_ab/{out.name}",
            "bytes": int(pr["format"]["size"]),
            "sha256": sha256(out),
            "durationSeconds": round(float(pr["format"]["duration"]), 3),
            "video": {"codec": vstreams[0]["codec_name"],
                      "width": vstreams[0]["width"], "height": vstreams[0]["height"],
                      "fps": vstreams[0]["r_frame_rate"], "streamMd5": vmd5},
            "audio": {"codec": astreams[0]["codec_name"],
                      "sampleRateHz": int(astreams[0]["sample_rate"]),
                      "channels": int(astreams[0]["channels"]),
                      "bitRateBps": int(astreams[0].get("bit_rate", 0))},
            "masterLoudness": master_loud,
            "reelLoudness": reel_loud,
        })

    # --- per-scene loudness + per-VO-window RMS, measured on the reels ---
    per_scene = []
    for sc in SCENES:
        s0, s1 = sc["reelSeconds"]
        row = {"sceneId": sc["sceneId"], "reelSeconds": sc["reelSeconds"]}
        for ver, reel in zip(("v1", "v2", "v3"), reels):
            row[ver] = loudnorm(ROOT / reel["file"], start=s0, dur=s1 - s0)
        per_scene.append(row)
    vo_windows = []
    for w in VO_WINDOWS:
        w0, w1 = w["windowReelSeconds"]
        row = dict(w)
        for ver, reel in zip(("v1", "v2", "v3"), reels):
            row[ver] = window_stats(ROOT / reel["file"], w0, w1 - w0)
        vo_windows.append(row)

    # --- waveform difference between masters (what the A/B actually changes) ---
    scopes = ([("full72s", 0.0, 72.0)]
              + [(sc["sceneId"], sc["reelSeconds"][0], sc["reelSeconds"][1]) for sc in SCENES]
              + [(w["shotId"], w["windowReelSeconds"][0], w["windowReelSeconds"][1])
                 for w in VO_WINDOWS])
    wave_diff = []
    for pair in (("v1", "v2"), ("v1", "v3"), ("v2", "v3")):
        a, b = decoded[pair[0]], decoded[pair[1]]
        for name, s0, s1 in scopes:
            wave_diff.append({"pair": f"{pair[0]}-vs-{pair[1]}", "scope": name,
                              "seconds": [s0, s1], **diff_stats(a, b, s0, s1)})

    # --- v3 cross-check: my v3 reel audio vs the M38-A candidate reel audio ---
    v3_reel = next(r for r in reels if r["version"] == "v3")
    cross = {"candidateReelLoudness": src_loud, "abV3ReelLoudness": v3_reel["reelLoudness"],
             "integratedLufsDiff": round(v3_reel["reelLoudness"]["integratedLUFS"]
                                         - src_loud["integratedLUFS"], 2),
             "truePeakDiffDb": round(v3_reel["reelLoudness"]["truePeakDBTP"]
                                     - src_loud["truePeakDBTP"], 2),
             "note": "Same v3 WAV master, same AAC 192k/48kHz stereo settings; "
                     "small diff = encoder run variance vs the CP2/M38-A encode."}

    manifest = {
        "manifestId": "NGM_P0_SOUNDTRACK_AB_V1",
        "checkpoint": "WO37 M-B CP1",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_REVIEW_PACKAGE_NOT_FINAL / NOT_AUDITIONED",
        "purpose": ("Remainder of WO37 big checkpoint 2: soundtrack A/B for P0 "
                    "(v1 vs v2 vs v3). Same candidate-B picture in all three reels; "
                    "only the soundtrack differs. Codex/director picks the winner; "
                    "no version is adopted by this checkpoint."),
        "picture": {
            "source": "Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_review_72s_640x360_30fps.mp4",
            "role": "M38-A candidate reel (B pose-animation takes, 12 shots, 640x360 30fps)",
            "sha256": REEL_SRC_SHA,
            "videoStreamMd5": src_video_md5,
            "durationSeconds": round(float(src_probe["format"]["duration"]), 3),
        },
        "substitutionSummary": {
            "v1-vs-v2": "MUSIC/quiet_discovery + MUSIC/boss_mang_cot + SFX/CINEMA/reveal + tension: "
                        "ported PackV1 -> composed (CP26). Ambience unchanged (ported).",
            "v2-vs-v3": "AMBIENCE/rain_light + river_shore + underwater: ported PackV1 -> "
                        "composed (CP30). Music/stingers unchanged from v2.",
            "vo": "Identical in all three versions: same CP04 draft VO takes, same windows, "
                  "same gains/ducking (per v2/v3 mix verdicts).",
        },
        "audioMasters": {ver: {"file": str(m["wav"].relative_to(ROOT)),
                                "sha256": m["sha256"],
                                "cp9Loudness": m["cp9"]} for ver, m in MIXES.items()},
        "reels": reels,
        "comparison": {
            "perSceneLoudness": per_scene,
            "voWindowStats": vo_windows,
            "waveformDiffMasters": wave_diff,
            "v3CrossCheckVsCandidateReel": cross,
        },
        "listeningQuestions": [
            {"version": "v1", "question": "Baseline ported: does the PackV1 music bed sit under the VO without masking it? Rain/river beds: present or washed out?"},
            {"version": "v2", "question": "Composed score: does the composed quiet_discovery / boss_mang_cot change the scene feel vs ported? VO clarity in the three locked windows vs v1?"},
            {"version": "v3", "question": "Fully composed: do the composed ambience beds (rain_light / river_shore / underwater) hold the rain/river/underwater scenes? Any bed that reads thinner or thicker than ported?"},
            {"version": "all", "question": "Ducking: is the VO clearly on top of the bed in all three windows in every version? Stinger hits (reveal/tension): too hot, too soft, or right — and does the composed stinger change the hit vs ported?"},
        ],
        "sourceClosure": {
            "candidateReelSha256": REEL_SRC_SHA,
            "mixMasterSha256": {ver: MIXES[ver]["sha256"] for ver in ("v1", "v2", "v3")},
            "voWindowsSource": ("Implementation/Content/Narrative/Deliveries/CIN_001/CIN_001_timing_v1.json, "
                                "CIN_002/CIN_002_timing_v1.json, CIN_004/CIN_004_timing_v1.json "
                                "(locked windows; CIN_001_S05 DECIDED_DEC_MEDIA_P0)"),
            "substitutionSource": ("Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/P0_MIX_V2_manifest_v1.json + "
                                   "P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json substitutionTable"),
            "encode": ("video stream copied from candidate reel; audio AAC 192k 48kHz stereo "
                       "from the 72s WAV masters; apad + -t 72.021333 so the 2160-frame "
                       "video stays whole (masters are 72.000 s, candidate audio 72.021333 s "
                       "via AAC priming; the 21 ms tail is digital silence)"),
        },
        "runtimeUnchangedProof": {
            "clientGodotClean": git_clean(["ClientGodot/"]),
            "note": "Builder asserts ClientGodot/ clean before building; no file under "
                    "ClientGodot/ is written by this checkpoint.",
        },
        "provenance": {
            "vo": "Draft VO (CP04), fictional voices, no real-person cloning, no unlicensed samples.",
            "musicAmbience": "v1 ported PackV1 (Codex pack); v2/v3 composed originals (CP26/CP30).",
            "statusNote": "COMPOSED_CANDIDATE / DRAFT_NOT_FINAL / NOT_AUDITIONED. "
                          "Loudness/RMS/diff figures are measurements, not a listening PASS.",
        },
    }
    (OUT_DIR / "P0_SOUNDTRACK_AB_v1.json").write_text(
        json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    playlist = OUT_DIR.parent  # not used; playlist lives in Reports
    pl = ROOT / "Implementation/Reports/MuseMedia/p0_soundtrack_ab_playlist.txt"
    lines = ["#EXTM3U",
             "# MEDIA-02 WO37 M-B CP1 — P0 soundtrack A/B (v1 vs v2 vs v3)",
             "# AUDITION STATUS: NOT_AUDITIONED (prepared for a human listener)",
             "# Same candidate-B picture in all three reels; only the soundtrack differs.",
             "# M3U content under a .txt name (.m3u is not a policy extension);",
             "# rename a copy to .m3u to open it directly in a player.",
             "# Paths are relative to Implementation/Reports/MuseMedia/."]
    for ver in ("v1", "v2", "v3"):
        lines.append(f"#EXTINF:72.0,P0 soundtrack {ver} — {MIXES[ver]['label']}")
        lines.append(f"../../../Art_Source/Cinematics/P0_Motion/soundtrack_ab/P0_soundtrack_{ver}_72s_640x360_30fps.mp4")
    pl.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps({"reels": [{r["version"]: r["sha256"][:12], "bytes": r["bytes"],
                                 "dur": r["durationSeconds"],
                                 "reelLufs": r["reelLoudness"]} for r in reels]},
                     indent=1, ensure_ascii=False))
    print("picture video md5 (all three reels):", src_video_md5)
    print("v3 cross-check vs candidate reel:", cross)
    return 0


if __name__ == "__main__":
    sys.exit(main())
