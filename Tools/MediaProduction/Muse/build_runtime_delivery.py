#!/usr/bin/env python3
"""MEDIA-02 checkpoint 10 (M6 runtime delivery).

Copy verified media deliverables into the Godot runtime asset tree with
byte-level verification, and write runtime manifests that Codex's
presentation adapter can consume (data only -- no Godot code, which Muse
is forbidden to write).

Sources (all already measured from real bytes in checkpoints 01-09):
  - Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json
    (22 cues: runtime OGG under Client/Assets/Audio/PackV1/)
  - Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json
    (173 cues x 3 variants: runtime WAV under Client/Assets/Audio/PackV1/)
  - Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json
    (3 P0 VO draft takes + 72 s VO timeline WAV)
  - Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json
    (17 campaign VO draft takes + 378 s VO timeline WAV, checkpoint 17)
  - Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json
    (CIN_006 canonical take + alternate take + 18 s VO timeline WAV,
    checkpoint 19)
  - Art_Source/Audio/Muse/MIX/P0_DRAFT/P0_MIX_manifest_v1.json
    (3 P0 scene draft mixes + 72 s review mix WAV, checkpoint 20)
  - Art_Source/Cinematics/Campaign/CIN_005/
    (3 storyboard keyframes 640x360 + scene export manifest with the
    18 s animated take MP4/OGV/poster, checkpoint 21)
  - Art_Source/Cinematics/Campaign/CIN_006/
    (3 storyboard keyframes 640x360 + scene export manifest with the
    18 s animated take MP4/OGV/poster, checkpoint 22)
  - Art_Source/Cinematics/Campaign/CIN_009/
    (3 storyboard keyframes 640x360 + scene export manifest with the
    18 s animated take MP4/OGV/poster, checkpoint 23)
  - Art_Source/Cinematics/Campaign/CIN_020/
    (3 storyboard keyframes 640x360 + scene export manifest with the
    18 s animated take MP4/OGV/poster, checkpoint 24)
  - Art_Source/Cinematics/Campaign/CIN_003, CIN_007, CIN_008, CIN_010,
    CIN_011, CIN_012, CIN_013, CIN_014, CIN_015, CIN_016, CIN_017,
    CIN_018, CIN_019/
    (3 storyboard keyframes 640x360 each + scene export manifests with
    the 18 s animated takes MP4/OGV/poster, checkpoint 25 batch --
    all 20 campaign scenes now carry video)
  - Implementation/Content/Narrative/Deliveries/{P0,CAMPAIGN}_timing_manifest_v1.json
    + CIN_006/CIN_006_timing_manifest_v1.json (20 scenes timing JSON + SRT)

Destinations (policy-allowed media roots):
  - ClientGodot/assets/audio/<relpath under PackV1/>   (541 files)
  - ClientGodot/assets/audio/vo/p0/                     (4 files)
  - ClientGodot/assets/audio/vo/campaign/               (18 files)
  - ClientGodot/assets/audio/vo/cin006/                 (3 files)
  - ClientGodot/assets/audio/mix/p0/                    (4 files)
  - ClientGodot/assets/cinematics/timing/               (40 files)
  - ClientGodot/assets/cinematics/P0_animatic_*         (already there
    since checkpoint 03, revised in checkpoint 13; verified here, not re-copied)

Verification per file (any failure aborts with non-zero exit):
  - source is real bytes, never a git-LFS pointer
  - copied sha256 == pack/manifest-recorded sha256
  - copied size == recorded size_bytes
  - ffprobe duration == recorded duration_s (tolerance 0.02 s)

Outputs:
  - ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json
  - ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # repo root
AUDIO_DEST = ROOT / "ClientGodot" / "assets" / "audio"
CINE_DEST = ROOT / "ClientGodot" / "assets" / "cinematics"
PACK_PREFIX = "Client/Assets/Audio/PackV1/"
VO_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "VO" / "P0_DRAFT"
CAMPAIGN_VO_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "VO" / "CAMPAIGN_DRAFT"
CIN006_VO_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "VO" / "CIN006_DRAFT"
P0_MIX_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "P0_DRAFT"
P0_MIX_V2_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "P0_DRAFT_V2"
P0_MIX_V3_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "P0_DRAFT_V3"
CIN006_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN006_DRAFT_V1"
CIN003_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN003_DRAFT_V1"
CIN005_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN005_DRAFT_V1"
CIN007_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN007_DRAFT_V1"
CIN008_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN008_DRAFT_V1"
CIN009_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN009_DRAFT_V1"
CIN010_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN010_DRAFT_V1"
CIN011_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN011_DRAFT_V1"
CIN012_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN012_DRAFT_V1"
CIN013_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN013_DRAFT_V1"
CIN014_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN014_DRAFT_V1"
CIN015_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN015_DRAFT_V1"
CIN016_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN016_DRAFT_V1"
CIN017_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN017_DRAFT_V1"
CIN018_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN018_DRAFT_V1"
CIN019_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN019_DRAFT_V1"
CIN020_MIX_V1_SRC = ROOT / "Art_Source" / "Audio" / "Muse" / "MIX" / "CIN020_DRAFT_V1"
DUR_TOL_S = 0.02

# P0 animatic files delivered in checkpoint 03, revised in checkpoint 13
# (4 panels) and checkpoint 16 (CIN_002_S02 keyframe; report SHAs).
ANIMATIC_EXPECTED = {
    "P0_animatic_640x360_30fps.mp4":
        "570c78ff0f3a03409ef0b292d5f505f15719476e64cb1e30f49047112091dcf4",
    "P0_animatic_640x360_30fps.ogv":
        "06acf54e73eeba5358d5e738984f63c48484a3bfacf75cc5a63fcaa407c68f50",
    "P0_animatic_poster.png":
        "ea9d42287274d46c5b8c1cedb70c00a4d795f61d757484233fbbfd019ba9bce8",
}

failures = []


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path: Path) -> bool:
    with open(path, "rb") as f:
        return f.read(200).startswith(b"version https://git-lfs.github.com")


def ffprobe_duration_s(path: Path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def ffprobe_first_stream_duration_s(path: Path):
    """Duration of the first stream (the video stream for film
    files) -- the quantity verify_runtime_delivery measures. For
    the checkpoint 27 prologue this differs from the format
    duration by 0.1 s (xfade frame rounding; see the film
    builder)."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    data = json.loads(out.stdout)
    return float(data["streams"][0].get("duration")
                 or data["format"]["duration"])


SRT_TIME_RE = re.compile(
    r"^\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d$")


def count_srt_cues(text: str):
    """Count SRT cue blocks; None when the file is unparseable.

    A cue block is an index line followed by a timestamp line. This is the
    same strict shape validate_media_deliveries.parse_srt enforces, counted
    here so the builder never trusts a manifest's cue list alone.
    """
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip())
              if b.strip()]
    if not blocks:
        return None
    count = 0
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3 or not lines[0].strip().isdigit():
            return None
        if not SRT_TIME_RE.match(lines[1].strip()):
            return None
        count += 1
    return count


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL: " + msg)


def copy_verified_audio(src_rel, dest_rel, expect_sha, expect_size,
                        expect_dur, label):
    src = ROOT / src_rel
    dest = AUDIO_DEST / dest_rel
    check(src.exists(), f"{label}: source missing {src_rel}")
    if not src.exists():
        return None
    check(not is_lfs_pointer(src), f"{label}: source is LFS pointer {src_rel}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    got_sha = sha256(dest)
    got_size = dest.stat().st_size
    check(got_sha == expect_sha,
          f"{label}: sha mismatch {got_sha} != {expect_sha}")
    check(got_size == expect_size,
          f"{label}: size mismatch {got_size} != {expect_size}")
    try:
        got_dur = ffprobe_duration_s(dest)
    except Exception as e:  # noqa: BLE001
        failures.append(f"{label}: ffprobe failed: {e}")
        return None
    check(abs(got_dur - expect_dur) <= DUR_TOL_S,
          f"{label}: duration mismatch {got_dur} != {expect_dur}")
    return {"runtimePath": "assets/audio/" + dest_rel,
            "sourcePath": src_rel, "sha256": got_sha,
            "sizeBytes": got_size, "durationSeconds": round(got_dur, 4)}


def main():
    audio_entries = []
    counts = {"music_ambience": 0, "sfx_ui_variants": 0, "vo": 0,
              "mix": 0, "composed": 0}

    # --- 1. Music + ambience runtime OGGs (checkpoint 07) ---
    ma = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                     / "MUSIC_AMBIENCE_pack_v1.json").read_text(encoding="utf-8"))
    for cue in ma["cues"]:
        rt = cue["runtime"]
        rel = rt["path"][len(PACK_PREFIX):]
        entry = copy_verified_audio(
            rt["path"], rel, rt["sha256"], rt["size_bytes"],
            rt["duration_s"], cue["cueKey"])
        if entry is None:
            continue
        entry.update({"cueKey": cue["cueKey"], "category": "music"
                      if "/music/" in rt["path"] else "ambience",
                      "bus": cue["bus"], "loop": cue["loop"],
                      "gain": cue["gain"], "codec": rt["codec"],
                      "sampleRateHz": rt["sample_rate_hz"],
                      "channels": rt["channels"],
                      "integratedLufs": rt.get("integrated_lufs"),
                      "truePeakDbtp": rt.get("true_peak_dbtp"),
                      "assetState": "RENDERED_CANDIDATE",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["music_ambience"] += 1

    # --- 2. SFX + UI runtime WAVs (checkpoint 08) ---
    sfx = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                      / "SFX_UI_pack_v1.json").read_text(encoding="utf-8"))
    for cue in sfx["cues"]:
        for var in cue["variants"]:
            rt = var["runtime"]
            rel = rt["path"][len(PACK_PREFIX):]
            label = f"{cue['cueKey']} {var['variantId']}"
            entry = copy_verified_audio(
                rt["path"], rel, rt["sha256"], rt["size_bytes"],
                rt["duration_s"], label)
            if entry is None:
                continue
            entry.update({"cueKey": cue["cueKey"],
                          "variantId": var["variantId"],
                          "category": cue["category"],
                          "bus": cue["bus"], "loop": cue["loop"],
                          "gain": cue["gain"], "codec": rt["codec"],
                          "sampleRateHz": rt["sample_rate_hz"],
                          "channels": rt["channels"],
                          "integratedLufs": rt.get("integrated_lufs"),
                          "truePeakDbtp": rt.get("true_peak_dbtp"),
                          "assetState": "RENDERED_CANDIDATE",
                          "wireStatus":
                              "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
            audio_entries.append(entry)
            counts["sfx_ui_variants"] += 1

    # --- 3. P0 VO drafts (checkpoint 04) ---
    vo = json.loads((VO_SRC / "P0_VO_manifest_v1.json").read_text(
        encoding="utf-8"))
    for take in vo["takes"]:
        src_rel = f"Art_Source/Audio/Muse/VO/P0_DRAFT/{take['wav']}"
        dest_rel = f"vo/p0/{take['wav']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, take["wavSha256"],
            take["format"]["bytes"], take["durationSeconds"],
            f"VO {take['key']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"VO/{take['key']}",
                      "category": "vo", "speaker": take["speaker"],
                      "shotId": take["shotId"],
                      "windowSceneSeconds": take["windowSceneSeconds"],
                      "windowStatus": take["status"],
                      "codec": take["format"]["codec"],
                      "sampleRateHz": take["format"]["sampleRateHz"],
                      "channels": take["format"]["channels"],
                      "integratedLufs": float(
                          take["loudness"]["integratedLUFS"]),
                      "truePeakDbtp": float(
                          take["loudness"]["truePeakDBTP"]),
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1
    tl = vo["timeline"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/VO/P0_DRAFT/{tl['file']}",
        f"vo/p0/{tl['file']}", tl["sha256"],
        (VO_SRC / tl["file"]).stat().st_size,
        tl.get("durationSeconds", 72.0), "VO timeline")
    if entry is not None:
        entry.update({"cueKey": "VO/P0_TIMELINE", "category": "vo",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 1,
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1

    # --- 3b. Campaign VO drafts (checkpoint 17) ---
    cvo = json.loads((CAMPAIGN_VO_SRC / "CAMPAIGN_VO_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    for take in cvo["takes"]:
        src_rel = f"Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/{take['wav']}"
        dest_rel = f"vo/campaign/{take['wav']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, take["wavSha256"],
            take["format"]["bytes"], take["durationSeconds"],
            f"VO {take['key']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"VO/{take['key']}",
                      "category": "vo", "speaker": take["speaker"],
                      "shotId": take["shotId"],
                      "windowSceneSeconds": take["windowSceneSeconds"],
                      "windowStatus": take["status"],
                      "fit": take["fit"],
                      "slackSeconds": take["slackSeconds"],
                      "codec": take["format"]["codec"],
                      "sampleRateHz": take["format"]["sampleRateHz"],
                      "channels": take["format"]["channels"],
                      "integratedLufs": float(
                          take["loudness"]["integratedLUFS"]),
                      "truePeakDbtp": float(
                          take["loudness"]["truePeakDBTP"]),
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1
    ctl = cvo["timeline"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/{ctl['file']}",
        f"vo/campaign/{ctl['file']}", ctl["sha256"],
        (CAMPAIGN_VO_SRC / ctl["file"]).stat().st_size,
        ctl.get("durationSeconds", 378.0), "VO campaign timeline")
    if entry is not None:
        entry.update({"cueKey": "VO/CAMPAIGN_TIMELINE", "category": "vo",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 1,
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1

    # --- 3c. CIN_006 VO drafts (checkpoint 19) ---
    c6vo = json.loads((CIN006_VO_SRC / "CIN006_VO_manifest_v1.json")
                      .read_text(encoding="utf-8"))
    for take in c6vo["takes"]:
        src_rel = f"Art_Source/Audio/Muse/VO/CIN006_DRAFT/{take['wav']}"
        dest_rel = f"vo/cin006/{take['wav']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, take["wavSha256"],
            take["format"]["bytes"], take["durationSeconds"],
            f"VO {take['key']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"VO/{take['key']}",
                      "category": "vo", "speaker": take["speaker"],
                      "shotId": take["shotId"],
                      "takeKind": take["takeKind"],
                      "windowSceneSeconds": take["windowSceneSeconds"],
                      "windowStatus": take["status"],
                      "fit": take["fit"],
                      "slackSeconds": take["slackSeconds"],
                      "codec": take["format"]["codec"],
                      "sampleRateHz": take["format"]["sampleRateHz"],
                      "channels": take["format"]["channels"],
                      "integratedLufs": float(
                          take["loudness"]["integratedLUFS"]),
                      "truePeakDbtp": float(
                          take["loudness"]["truePeakDBTP"]),
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        if take.get("takeId"):
            entry.update({"takeId": take["takeId"],
                          "version": take["version"]})
        audio_entries.append(entry)
        counts["vo"] += 1
    c6tl = c6vo["timeline"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/VO/CIN006_DRAFT/{c6tl['file']}",
        f"vo/cin006/{c6tl['file']}", c6tl["sha256"],
        (CIN006_VO_SRC / c6tl["file"]).stat().st_size,
        c6tl.get("durationSeconds", 18.0), "VO CIN_006 timeline")
    if entry is not None:
        entry.update({"cueKey": "VO/CIN006_TIMELINE", "category": "vo",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 1,
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1

    # --- 3d. P0 draft mixes (checkpoint 20) ---
    pmix = json.loads((P0_MIX_SRC / "P0_MIX_manifest_v1.json")
                      .read_text(encoding="utf-8"))
    for scene in pmix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/P0_DRAFT/{mx['file']}"
        dest_rel = f"mix/p0/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"P0 mix {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1
    rmx = pmix["reviewMix"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/MIX/P0_DRAFT/{rmx['file']}",
        f"mix/p0/{rmx['file']}", rmx["sha256"],
        (P0_MIX_SRC / rmx["file"]).stat().st_size,
        rmx.get("durationSeconds", 72.0), "P0 mix review 72 s")
    if entry is not None:
        entry.update({"cueKey": "MIX/P0_REVIEW_72S", "category": "mix",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 2,
                      "integratedLufs": float(rmx["integratedLUFS"]),
                      "truePeakDbtp": float(rmx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3g. P0 draft mixes v2 from composed stems (checkpoint 29) ---
    # Same three scenes + 72 s review, re-mixed from the checkpoint-26
    # composed music/stingers (ported ambience + CP04 VO unchanged).
    # Delivered in parallel under mix/p0_v2/; the v1 mixes in mix/p0/
    # are byte-identical to before. Adoption is Codex's decision.
    pmix2 = json.loads((P0_MIX_V2_SRC / "P0_MIX_V2_manifest_v1.json")
                       .read_text(encoding="utf-8"))
    for scene in pmix2["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/{mx['file']}"
        dest_rel = f"mix/p0_v2/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"P0 mix v2 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V2/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v2_composed_stems",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1
    rmx2 = pmix2["reviewMix"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/{rmx2['file']}",
        f"mix/p0_v2/{rmx2['file']}", rmx2["sha256"],
        (P0_MIX_V2_SRC / rmx2["file"]).stat().st_size,
        rmx2.get("durationSeconds", 72.0), "P0 mix v2 review 72 s")
    if entry is not None:
        entry.update({"cueKey": "MIX/V2/P0_REVIEW_72S", "category": "mix",
                      "mixVersion": "v2_composed_stems",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 2,
                      "integratedLufs": float(rmx2["integratedLUFS"]),
                      "truePeakDbtp": float(rmx2["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3i. P0 draft mixes v3 from fully composed stems (checkpoint 31) ---
    # Same three scenes + 72 s review, re-mixed from the checkpoint-26
    # composed music/stingers PLUS the checkpoint-30 composed ambience
    # (no ported stem remains in the P0 mixes). Delivered in parallel
    # under mix/p0_v3/; the v1 mixes in mix/p0/ and v2 mixes in
    # mix/p0_v2/ are byte-identical to before. Adoption is Codex's
    # decision.
    pmix3 = json.loads((P0_MIX_V3_SRC / "P0_MIX_V3_manifest_v1.json")
                       .read_text(encoding="utf-8"))
    for scene in pmix3["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/{mx['file']}"
        dest_rel = f"mix/p0_v3/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"P0 mix v3 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V3/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v3_fully_composed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1
    rmx3 = pmix3["reviewMix"]
    entry = copy_verified_audio(
        f"Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/{rmx3['file']}",
        f"mix/p0_v3/{rmx3['file']}", rmx3["sha256"],
        (P0_MIX_V3_SRC / rmx3["file"]).stat().st_size,
        rmx3.get("durationSeconds", 72.0), "P0 mix v3 review 72 s")
    if entry is not None:
        entry.update({"cueKey": "MIX/V3/P0_REVIEW_72S", "category": "mix",
                      "mixVersion": "v3_fully_composed",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 2,
                      "integratedLufs": float(rmx3["integratedLUFS"]),
                      "truePeakDbtp": float(rmx3["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3j. CIN_006 draft mix v1 (checkpoint 34, Goi 31 item 4) ---
    # First scene mix for CIN_006 (same recipe as P0 v3; stem
    # assignment PROPOSED_CANDIDATE, see CIN006_MIX_V1_manifest_v1.json).
    # Delivered under mix/cin006_v1/; the P0 v1/v2/v3 mixes are
    # byte-identical to before. Adoption is Codex's decision.
    cin006_mix = json.loads((CIN006_MIX_V1_SRC
                             / "CIN006_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin006_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin006_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_006 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin006_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k. CIN_003 draft mix v1 (checkpoint 37) ---
    # Second scene mix after CIN_006 v1 (same recipe as P0 v3; stem
    # assignment PROPOSED_CANDIDATE, see CIN003_MIX_V1_manifest_v1.json).
    # Delivered under mix/cin003_v1/; the P0 v1/v2/v3 and CIN_006 v1
    # mixes are byte-identical to before. Adoption is Codex's decision.
    cin003_mix = json.loads((CIN003_MIX_V1_SRC
                             / "CIN003_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin003_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin003_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_003 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin003_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k2. CIN_005 draft mix v1 (checkpoint 38) ---
    # Third scene mix after CIN_006 v1 and CIN_003 v1 (same recipe as
    # P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN005_MIX_V1_manifest_v1.json). The CP17 draft VO take
    # overruns its 12.5-17.5 s window by 0.160 s and the overrun is
    # KEPT per the owner verdict (Goi 30 D1); no tail trim at the
    # 18.00 s scene edge. Delivered under mix/cin005_v1/; the P0
    # v1/v2/v3, CIN_006 v1 and CIN_003 v1 mixes are byte-identical
    # to before. Adoption is Codex's decision.
    cin005_mix = json.loads((CIN005_MIX_V1_SRC
                             / "CIN005_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin005_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin005_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_005 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin005_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k3. CIN_007 draft mix v1 (checkpoint 39) ---
    # Fourth scene mix after CIN_006 v1, CIN_003 v1 and CIN_005 v1
    # (same recipe as P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN007_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (3.912 s, ends 16.412 s): no
    # overrun, no tail trim at the 18.00 s scene edge. Ducking
    # evidence is measured over the full VO window because
    # quiet_discovery is sparse by design (the first 2 s of the
    # window are near-silence). Delivered under mix/cin007_v1/; the
    # P0 v1/v2/v3, CIN_006 v1, CIN_003 v1 and CIN_005 v1 mixes are
    # byte-identical to before. Adoption is Codex's decision.
    cin007_mix = json.loads((CIN007_MIX_V1_SRC
                             / "CIN007_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin007_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin007_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_007 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin007_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k4. CIN_008 draft mix v1 (checkpoint 40) ---
    # Fifth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1 and
    # CIN_007 v1 (same recipe as P0 v3; stem assignment
    # PROPOSED_CANDIDATE, see CIN008_MIX_V1_manifest_v1.json). The
    # CP17 draft VO take FITS inside its 12.5-17.5 s window (3.552 s,
    # ends 16.052 s): no overrun, no tail trim at the 18.00 s scene
    # edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability). Delivered under
    # mix/cin008_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1 and CIN_007 v1 mixes are byte-identical to before.
    # Adoption is Codex's decision.
    cin008_mix = json.loads((CIN008_MIX_V1_SRC
                             / "CIN008_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin008_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin008_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_008 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin008_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k5. CIN_009 draft mix v1 (checkpoint 41) ---
    # Sixth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1 and CIN_008 v1 (same recipe as P0 v3; stem assignment
    # PROPOSED_CANDIDATE, see CIN009_MIX_V1_manifest_v1.json). The
    # CP17 draft VO take FITS inside its 12.5-17.5 s window (4.080 s,
    # ends 16.580 s): no overrun, no tail trim at the 18.00 s scene
    # edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability). The mix is hotter
    # than CIN_008 (-17.84 LUFS) because the CP17 VO take itself is
    # hot (-17.23 LUFS); VO is kept at unity per the recipe, not
    # normalized. Delivered under mix/cin009_v1/; the P0 v1/v2/v3,
    # CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1 and CIN_008 v1
    # mixes are byte-identical to before. Adoption is Codex's decision.
    cin009_mix = json.loads((CIN009_MIX_V1_SRC
                             / "CIN009_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin009_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin009_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_009 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin009_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k6. CIN_010 draft mix v1 (checkpoint 42) ---
    # Seventh scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1 and CIN_009 v1 (same recipe as P0 v3;
    # stem assignment PROPOSED_CANDIDATE, see
    # CIN010_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (2.808 s, ends 15.308 s, 2.192 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability). The mix measures
    # -24.60 LUFS because the CP17 VO take itself is quiet (-22.01
    # LUFS); VO is kept at unity per the recipe, not normalized.
    # Delivered under mix/cin010_v1/; the P0 v1/v2/v3, CIN_006 v1,
    # CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1 and CIN_009 v1
    # mixes are byte-identical to before. Adoption is Codex's decision.
    cin010_mix = json.loads((CIN010_MIX_V1_SRC
                             / "CIN010_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin010_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin010_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_010 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin010_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k7. CIN_011 draft mix v1 (checkpoint 45) ---
    # Eighth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1 and CIN_010 v1 (same recipe
    # as P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN011_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.2-17.8 s window (5.592 s, ends 17.792 s, 0.008 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability). The mix measures
    # -20.34 LUFS because the CP17 VO take itself is quiet (-21.50
    # LUFS); VO is kept at unity per the recipe, not normalized.
    # Delivered under mix/cin011_v1/; the P0 v1/v2/v3, CIN_006 v1,
    # CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1 and
    # CIN_010 v1 mixes are byte-identical to before. Adoption is
    # Codex's decision.
    cin011_mix = json.loads((CIN011_MIX_V1_SRC
                             / "CIN011_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin011_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin011_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_011 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin011_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k8. CIN_012 draft mix v1 (checkpoint 46) ---
    # Ninth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1 and CIN_011 v1
    # (same recipe as P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN012_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (4.320 s, ends 16.820 s, 0.680 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability). The mix measures
    # -25.60 LUFS because the CP17 VO take itself is quiet (-25.38
    # LUFS); VO is kept at unity per the recipe, not normalized.
    # Delivered under mix/cin012_v1/; the P0 v1/v2/v3, CIN_006 v1,
    # CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1,
    # CIN_010 v1 and CIN_011 v1 mixes are byte-identical to before.
    # Adoption is Codex's decision.
    cin012_mix = json.loads((CIN012_MIX_V1_SRC
                             / "CIN012_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin012_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin012_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_012 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin012_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k9. CIN_013 draft mix v1 (checkpoint 47) ---
    # Tenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1 and
    # CIN_012 v1 (same recipe as P0 v3; stem assignment
    # PROPOSED_CANDIDATE, see CIN013_MIX_V1_manifest_v1.json). The
    # CP17 draft VO take FITS inside its 12.5-17.5 s window (2.472 s,
    # ends 14.972 s, 2.528 s before the window end): no overrun, no
    # tail trim at the 18.00 s scene edge. Ducking evidence is
    # measured over the full VO window (CP39 method, retained for
    # comparability). The mix measures -25.87 LUFS; the CP17 VO take
    # itself is quiet (-22.51 LUFS); VO is kept at unity per the
    # recipe, not normalized. Staging question, not a mix defect:
    # the timing manifest marks the S03 dialogue onscreen: true for
    # the refugee leader, but the S03 keyframe and the runtime clip
    # at 15 s show only Ly An at the open gate; the leader is on
    # screen in S02. Delivered under mix/cin013_v1/; the P0 v1/v2/v3,
    # CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1,
    # CIN_009 v1, CIN_010 v1, CIN_011 v1 and CIN_012 v1 mixes are
    # byte-identical to before. Adoption is Codex's decision.
    cin013_mix = json.loads((CIN013_MIX_V1_SRC
                             / "CIN013_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin013_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin013_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_013 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin013_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k10. CIN_014 draft mix v1 (checkpoint 48) ---
    # Eleventh scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1 and CIN_013 v1 (same recipe as P0 v3; stem assignment
    # PROPOSED_CANDIDATE, see CIN014_MIX_V1_manifest_v1.json). The
    # CP17 draft VO take FITS inside its 12.5-17.5 s window (3.072 s,
    # ends 15.572 s, 1.928 s before the window end): no overrun, no
    # tail trim at the 18.00 s scene edge. Ducking evidence is
    # measured over the full VO window (CP39 method, retained for
    # comparability): -8.84 dB. The mix measures -24.42 LUFS; the
    # CP17 VO take itself is -22.05 LUFS; VO is kept at unity per
    # the recipe, not normalized. Staging: the timing manifest marks
    # the S03 dialogue onscreen: true for Tong Banh and the keyframe
    # places a blue-robed figure at the open gate, but the recorded
    # keyframe defects note he is not visually identifiable in S03
    # (his armour differs across S01/S02 and neither S03 figure
    # matches it) -- a final-picture/character-lock matter, not a
    # mix defect; the mix does not move the VO. Delivered under
    # mix/cin014_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1 and CIN_013 v1 mixes are byte-identical
    # to before. Adoption is Codex's decision.
    cin014_mix = json.loads((CIN014_MIX_V1_SRC
                             / "CIN014_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin014_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin014_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_014 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin014_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k11. CIN_015 draft mix v1 (checkpoint 49) ---
    # Twelfth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1 and CIN_014 v1 (same recipe as P0 v3;
    # stem assignment PROPOSED_CANDIDATE, see
    # CIN015_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (2.880 s, ends 15.380 s, 2.120 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability): -6.87 dB. The mix
    # measures -25.30 LUFS; the CP17 VO take itself is -23.27 LUFS;
    # VO is kept at unity per the recipe, not normalized. Staging:
    # the timing manifest marks the S03 dialogue onscreen: true for
    # the Diver Lead and the keyframe places a small diver figure
    # with a conical hat at the bottom centre of the top-down
    # corridor, but the figure is tiny and seen from above/behind so
    # the speaker is not identifiable by face or gear from the
    # picture alone (S02 shows only a bare diver hand, S01 no figure
    # at all) -- a final-picture/character-lock matter, not a mix
    # defect; the mix does not move the VO. Delivered under
    # mix/cin015_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1, CIN_013 v1 and CIN_014 v1 mixes are
    # byte-identical to before. Adoption is Codex's decision.
    cin015_mix = json.loads((CIN015_MIX_V1_SRC
                             / "CIN015_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin015_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin015_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_015 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin015_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k12. CIN_016 draft mix v1 (checkpoint 50) ---
    # Thirteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1, CIN_014 v1 and CIN_015 v1 (same recipe
    # as P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN016_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (2.472 s, ends 14.972 s, 2.528 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability): 0.0 dB -- NOT a
    # missing compressor: MUSIC/quiet_discovery is digitally silent
    # from 12 s to 15 s (RMS -120 dB floor), so the 12.5-14.972 s VO
    # window falls entirely inside the cue's near-silence gap between
    # fragments; the sidechain compressor (same params) has no signal
    # to cut there. The mix measures -25.07 LUFS; the CP17 VO take
    # itself is -21.92 LUFS; VO is kept at unity per the recipe, not
    # normalized. Staging: unlike CIN_015, the speaker IS identifiable
    # here -- the S03 keyframe shows Ha Mac clearly (face in profile,
    # green headband, green robe, brush in hand, writing in the book)
    # asking the blue-robed elder across the desk; whether the hooded
    # figure seen from behind in S02 is Ha Mac arriving is a
    # continuity question for final picture (woven basket-hat vs
    # rectangular backpack) -- a final-picture/character-lock matter,
    # not a mix defect; the mix does not move the VO. Delivered under
    # mix/cin016_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1 and CIN_015 v1
    # mixes are byte-identical to before. Adoption is Codex's decision.
    cin016_mix = json.loads((CIN016_MIX_V1_SRC
                             / "CIN016_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin016_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin016_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_016 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin016_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k13. CIN_017 draft mix v1 (checkpoint 51) ---
    # Fourteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1 and CIN_016 v1
    # (same recipe as P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN017_MIX_V1_manifest_v1.json). The CP17 draft VO take FITS
    # inside its 12.5-17.5 s window (3.168 s, ends 15.668 s, 1.832 s
    # before the window end): no overrun, no tail trim at the 18.00 s
    # scene edge. Ducking evidence is measured over the full VO window
    # (CP39 method, retained for comparability): -4.85 dB -- a real
    # cut, as expected: MUSIC/bach_uyen was NOT silent inside
    # CIN_015's window either (measured cut -6.87 dB there). The mix
    # measures -24.63 LUFS; the CP17 VO take itself is -22.33 LUFS;
    # VO is kept at unity per the recipe, not normalized. Staging:
    # like CIN_015, the speaker is NOT identifiable here -- and this
    # time the timing manifest says so itself: the S03 dialogue
    # onscreen is null for the Diver Lead (NPC_DIVER_LEAD), and the
    # S03 keyframe shows only the misty river gorge with no diver
    # figure anywhere in the frame (S01 the serpent with no human
    # figure, S02 only the serpent and the crystal) -- the line is
    # delivered off-screen, like Ly An's voice in CIN_004 (DEC-MEDIA-
    # P0 Q2); a final-picture/character-lock matter, not a mix defect;
    # the mix does not move the VO. Stem reuse stated plainly: the
    # bach_uyen + underwater pairing is the same as CIN_015 (the
    # drowned city) because the two scenes share one water chapter
    # and the cue set has a single water form; boss_mang_cot was
    # passed over because it is boss material for the WRONG boss
    # (Mang Cot, not the Tide Serpent). Delivered under
    # mix/cin017_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1 and
    # CIN_016 v1 mixes are byte-identical to before. Adoption is
    # Codex's decision.
    cin017_mix = json.loads((CIN017_MIX_V1_SRC
                             / "CIN017_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin017_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin017_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_017 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin017_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k14. CIN_018 draft mix v1 (checkpoint 52) ---
    # Fifteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1
    # and CIN_017 v1 (same recipe as P0 v3; stem assignment
    # PROPOSED_CANDIDATE, see CIN018_MIX_V1_manifest_v1.json).
    # CIN_018 is the ONLY campaign scene with TWO dialogue windows:
    # the S02 take (Co Vo Tuong) FITS inside its 6.5-11.5 s window
    # (2.880 s, ends 9.380 s, 2.120 s before the window end) and the
    # S03 take (player) OVERRUNS its 12.5-17.5 s window by 0.280 s
    # (5.280 s, ends 17.780 s, 0.220 s before the 18.00 s scene
    # end) -- the overrun is KEPT per the owner verdict on the
    # three campaign overruns, not trimmed, not sped up; no tail
    # trim at the scene edge for either take. Both takes duck the
    # music bus through ONE combined VO bus (ducking -6.05 dB over
    # the S02 window and -7.44 dB over the S03 window, CP39
    # full-window method per window -- real cuts, as expected:
    # MUSIC/sa_hoa was NOT silent inside CIN_010's window either
    # (measured cut -7.94 dB there)). The mix measures -21.51
    # LUFS; the CP17 VO takes themselves are -23.77 LUFS (S02)
    # and -22.54 LUFS (S03); VO is kept at unity per the recipe,
    # not normalized. The reveal stinger is placed at 0.0 s (S01
    # start), NOT the recipe's 6.0 s: the cue is 3.000 s long, so
    # at 6.0 s it would sit under 2.5 s of the S02 line -- the
    # scene's key refusal line, spoken on screen. Staging: the
    # S02 speaker IS identifiable (onscreen: true, face visible at
    # his desk); the S03 line is delivered off-screen (onscreen:
    # null, like Ly An's voice in CIN_004, DEC-MEDIA-P0 Q2) -- the
    # masked figure in the S03 keyframe is NOT identified as the
    # speaker, and the keyframe defects record its full-face
    # porcelain mask (not the specified cracked half mask) and
    # torso-spanning copper machinery; S02 is a medium shot
    # instead of the detail close view and his hair differs from
    # S01's; S01's petition renders as a modern wax-sealed
    # envelope. Final-picture/character-lock matters, not mix
    # defects; the mix does not move the VO. The S03 take is
    # VOICE_PLACEHOLDER_ONLY (VOICE_GUIDE assigns the player no
    # spoken voice or gender). Stem reuse stated plainly: the
    # sa_hoa + desert_wind pairing is the same as CIN_010 (the
    # ash-gold caravan rest) because the two scenes share the
    # Sa Hoa / desert setting and the cue set has a single desert
    # form; bach_uyen was passed over because it is the
    # underwater form -- the opposite of this drought scene
    # (water present there, water withheld here). Delivered under
    # mix/cin018_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1,
    # CIN_016 v1 and CIN_017 v1 mixes are byte-identical to
    # before. Adoption is Codex's decision.
    cin018_mix = json.loads((CIN018_MIX_V1_SRC
                             / "CIN018_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin018_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin018_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_018 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin018_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k15. CIN_019 draft mix v1 (checkpoint 53) ---
    # Sixteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1,
    # CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1,
    # CIN_017 v1 and CIN_018 v1 (same recipe as P0 v3; stem
    # assignment PROPOSED_CANDIDATE, see
    # CIN019_MIX_V1_manifest_v1.json). The CP17 VO take (Ly An)
    # FITS inside its 12.5-17.5 s window (2.880 s, ends 15.380 s,
    # 2.120 s before the window end); no overrun, no tail trim.
    # Ducking -4.29 dB over the full VO window (CP39 method -- a
    # real cut: rift_finale carries real signal inside the
    # window, segment RMS -22.1 dBFS measured this run). The mix
    # measures -27.09 LUFS / -8.62 dBTP -- the quietest scene mix
    # so far -- because the CP17 take itself is one of the
    # quietest (-25.52 LUFS); VO is kept at unity per the recipe,
    # not normalized. rift_finale is the composed set's only
    # full close (the leitmotif's answering tail, withheld in
    # every other cue except the resolve stinger) and this is
    # its FIRST scene-mix use, for the campaign's resolution
    # scene; river_shore is a third scene-mix use (CIN_003,
    # CIN_008) for the rebuilt river village the line lands in.
    # Staging: the timing records the S03 dialogue onscreen:
    # true for Ly An and the keyframe manifest lists her among
    # the scene's on-screen characters, but the S03 frame is a
    # wide dawn view of the whole village under reconstruction
    # and no individual figure is identifiable as Ly An at this
    # scale; faces and costumes are storyboard placeholders
    # (NPC_LYAN has no approved cinematic character lock).
    # Final-picture/character-lock matter, not a mix defect;
    # the mix does not move the VO. Delivered under
    # mix/cin019_v1/; the P0 v1/v2/v3, CIN_006 v1, CIN_003 v1,
    # CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1,
    # CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1,
    # CIN_016 v1, CIN_017 v1 and CIN_018 v1 mixes are
    # byte-identical to before. Adoption is Codex's decision.
    cin019_mix = json.loads((CIN019_MIX_V1_SRC
                             / "CIN019_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin019_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin019_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_019 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin019_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3k16. CIN_020 draft mix v1 (checkpoint 54) ---
    # Seventeenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005
    # v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011
    # v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016
    # v1, CIN_017 v1, CIN_018 v1 and CIN_019 v1 (same recipe as
    # P0 v3; stem assignment PROPOSED_CANDIDATE, see
    # CIN020_MIX_V1_manifest_v1.json). The CP17 VO take (the
    # letter recipient) FITS inside its 12.5-17.5 s window
    # (3.000 s, ends 15.500 s, 2.000 s before the window end);
    # no overrun, no tail trim. Ducking -5.25 dB over the full
    # VO window (CP39 method -- a real cut: ben_mua carries real
    # signal inside the window, segment RMS -20.5 dBFS measured
    # this run). The mix measures -23.41 LUFS / -5.22 dBTP; the
    # CP17 take measures -19.59 LUFS; VO is kept at unity per
    # the recipe, not normalized. ben_mua is the rain-quay
    # leitmotif of the opening where the sealed letter changed
    # hands, back for the closing scene where the letter is
    # answered at the same river (third scene-mix use after
    # CIN_003 and CIN_014); river_shore is a fourth scene-mix
    # use (CIN_003, CIN_008, CIN_019). rift_finale was passed
    # over: the set's only full close, spent at CIN_019's
    # resolution -- this scene is the quiet morning after.
    # Casting: the recipient's voice is a placeholder role
    # voice (CP17 VOICE_LETTER_RECIPIENT; identity/gender
    # undecided) and the draft take uses the same fictional
    # system voice as Ly An's drafts -- a draft-casting
    # collision for the WO37 M-F palette work, not a mix
    # decision. Staging: the timing records the S03 dialogue
    # onscreen: null; the S03 keyframe shows the villager
    # seated at frame left seen from behind (top-down), so the
    # speaker is present but his face is not visible; the CP24
    # keyframe manifest records his appearance drifting between
    # all three shots (the scene's pack character list is
    # empty; no named lock exists for him).
    # Final-picture/casting matters, not mix defects; the mix
    # does not move the VO. Delivered under mix/cin020_v1/; the
    # P0 v1/v2/v3, CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007
    # v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1,
    # CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016
    # v1, CIN_017 v1, CIN_018 v1 and CIN_019 v1 mixes are
    # byte-identical to before. With this mix, every one of
    # the 21 entries carries an embedded soundtrack (0 silent)
    # and WO37 M-B big checkpoint 1 is complete. Adoption is
    # Codex's decision.
    cin020_mix = json.loads((CIN020_MIX_V1_SRC
                             / "CIN020_MIX_V1_manifest_v1.json")
                            .read_text(encoding="utf-8"))
    for scene in cin020_mix["scenes"]:
        mx = scene["mix"]
        src_rel = f"Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V1/{mx['file']}"
        dest_rel = f"mix/cin020_v1/{mx['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, mx["sha256"], mx["format"]["bytes"],
            mx["durationSeconds"], f"CIN_020 mix v1 {scene['sceneId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"MIX/V1/{scene['sceneId']}",
                      "category": "mix", "sceneId": scene["sceneId"],
                      "mixVersion": "v1_cin020_proposed",
                      "codec": mx["format"]["codec"],
                      "sampleRateHz": mx["format"]["sampleRateHz"],
                      "channels": mx["format"]["channels"],
                      "integratedLufs": float(mx["integratedLUFS"]),
                      "truePeakDbtp": float(mx["truePeakDBTP"]),
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    # --- 3e. Composed music + cinema stingers (checkpoint 26) ---
    # The composer (build_composed_music.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/; this
    # section verifies them in place against the delivery pack and
    # registers them in the runtime audio manifest. The ported PackV1
    # entries above are untouched; composed cues are parallel
    # candidates whose adoption is Codex's adapter decision.
    composed = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_COMPOSED_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": ("composed_music" if cue["kind"] == "MUSIC"
                         else "composed_sfx"),
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3h. Composed ambience (checkpoint 30) ---
    # The composer (build_composed_ambience.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/ambience/;
    # this section verifies them in place against the delivery pack
    # and registers them in the runtime audio manifest. The ported
    # PackV1 entries above are untouched; composed cues are parallel
    # candidates whose adoption is Codex's adapter decision.
    composed_amb = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "AMBIENCE_COMPOSED_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_amb["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed ambience {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": "composed_ambience",
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3k. WO37 M-D checkpoint 1 score batch (MD1 pack) ---
    # The composer (build_composed_score_md1.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/music/ and
    # .../composed/transitions/; this section verifies them in place
    # against the delivery pack and registers them in the runtime
    # audio manifest. Same contract as 3e/3h: the ported PackV1
    # entries and the checkpoint-26/30 composed packs are untouched;
    # MD1 cues are parallel candidates whose adoption is Codex's
    # adapter decision.
    composed_md1 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_SCORE_MD1_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_md1["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed MD1 {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": ("composed_music" if cue["kind"] == "MUSIC"
                         else "composed_transition"),
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3l. WO37 M-D checkpoint 2 intro/outro + stems + layers ---
    # The composer (build_composed_score_md2.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/intros/,
    # .../outros/, .../stems/ and .../layers/; this section verifies
    # them in place against the delivery pack and registers them in
    # the runtime audio manifest. Same contract as 3k: the ported
    # PackV1 entries and the checkpoint-26/30/MD1 packs are untouched;
    # MD2 files are parallel candidates whose adoption is Codex's
    # adapter decision. Stems sum to their MD1 parent master within
    # 24-bit quantisation (the MD2 validator re-checks that from
    # real bytes); layers are additive loops over their base cue.
    composed_md2 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_SCORE_MD2_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_md2["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed MD2 {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": {"INTRO": "composed_intro",
                         "OUTRO": "composed_outro",
                         "STEM": "composed_stem",
                         "LAYER": "composed_layer"}[cue["kind"]],
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3m. WO37 M-D checkpoint 3 intro/outro + stems + layers ---
    # The composer (build_composed_score_md3.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/intros/,
    # .../outros/, .../stems/ and .../layers/; this section verifies
    # them in place against the delivery pack and registers them in
    # the runtime audio manifest. Same contract as 3k/3l: the ported
    # PackV1 entries and the checkpoint-26/30/MD1/MD2 packs are
    # untouched; MD3 files are parallel candidates whose adoption is
    # Codex's adapter decision. Stems sum to their checkpoint-26
    # parent master within 24-bit quantisation (the MD3 validator
    # re-checks that from real bytes); layers are additive loops over
    # their base cue. The checkpoint-26 parents were built in several
    # separate renders, so each cue's reproducing RNG history is
    # recorded in the MD3 pack (see build_composed_score_md3.py).
    composed_md3 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_SCORE_MD3_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_md3["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed MD3 {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": {"INTRO": "composed_intro",
                         "OUTRO": "composed_outro",
                         "STEM": "composed_stem",
                         "LAYER": "composed_layer"}[cue["kind"]],
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3n. WO37 M-D checkpoint 4 phase layers ---
    # The composer (build_composed_score_md4.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/layers/;
    # this section verifies them in place against the delivery pack
    # and registers them in the runtime audio manifest. Same contract
    # as 3k/3l/3m: the ported PackV1 entries and the
    # checkpoint-26/30/MD1/MD2/MD3 packs are untouched; MD4 files are
    # parallel candidates whose adoption is Codex's adapter decision.
    # Layers are additive loops over their base cue (combined
    # base+layer loudness measured from real bytes; the MD4 validator
    # re-checks that from real bytes).
    composed_md4 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_SCORE_MD4_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_md4["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed MD4 {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": {"INTRO": "composed_intro",
                         "OUTRO": "composed_outro",
                         "STEM": "composed_stem",
                         "LAYER": "composed_layer"}[cue["kind"]],
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3o. WO37 M-D checkpoint 5 phase layers ---
    # The composer (build_composed_score_md5.py) already rendered the
    # runtime OGGs into ClientGodot/assets/audio/composed/layers/;
    # this section verifies them in place against the delivery pack
    # and registers them in the runtime audio manifest. Same contract
    # as 3k/3l/3m/3n: the ported PackV1 entries and the
    # checkpoint-26/30/MD1/MD2/MD3/MD4 packs are untouched; MD5 files are
    # parallel candidates whose adoption is Codex's adapter decision.
    # Layers are additive loops over their base cue (combined
    # base+layer loudness measured from real bytes; the MD5 validator
    # re-checks that from real bytes).
    composed_md5 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_SCORE_MD5_pack_v1.json").read_text(encoding="utf-8"))
    for cue in composed_md5["cues"]:
        rt = cue["runtime"]
        dest_rel = rt["path"].split("assets/audio/", 1)[1]
        dest = AUDIO_DEST / dest_rel
        label = f"composed MD5 {cue['cueKey']}"
        check(dest.exists(), f"{label}: runtime file missing {rt['path']}")
        if not dest.exists():
            continue
        check(not is_lfs_pointer(dest),
              f"{label}: runtime file is an LFS pointer")
        got_sha = sha256(dest)
        got_size = dest.stat().st_size
        check(got_sha == rt["sha256"],
              f"{label}: sha mismatch {got_sha} != {rt['sha256']}")
        check(got_size == rt["sizeBytes"],
              f"{label}: size mismatch {got_size} != {rt['sizeBytes']}")
        got_dur = ffprobe_duration_s(dest)
        check(abs(got_dur - rt["durationSeconds"]) <= DUR_TOL_S,
              f"{label}: duration mismatch {got_dur} != "
              f"{rt['durationSeconds']}")
        entry = {"runtimePath": "assets/audio/" + dest_rel,
                 "sourcePath": cue["master"]["path"],
                 "sha256": got_sha, "sizeBytes": got_size,
                 "durationSeconds": round(got_dur, 4)}
        entry.update({
            "cueKey": cue["cueKey"],
            "category": {"INTRO": "composed_intro",
                         "OUTRO": "composed_outro",
                         "STEM": "composed_stem",
                         "LAYER": "composed_layer"}[cue["kind"]],
            "codec": rt["codec"],
            "sampleRateHz": rt["sampleRateHz"],
            "channels": rt["channels"],
            "integratedLufs": rt["integratedLufs"],
            "truePeakDbtp": rt["truePeakDbtp"],
            "assetState": "COMPOSED_CANDIDATE",
            "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER",
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE"})
        audio_entries.append(entry)
        counts["composed"] += 1

    # --- 3f. Prologue CIN_000 narration VO + film mix (checkpoint 27) ---
    # The prologue is a standalone pre-game film (owner-ordered,
    # script approved in main chat 2026-11-06), NOT part of the
    # 20-scene campaign. Its 5 narration takes and its embedded film
    # mix register here; the film itself registers in the
    # cinematics manifest under a separate "prologue" key (section
    # 6b), never inside the campaign totals.
    provo = json.loads((ROOT / "Art_Source/Audio/Muse/VO"
                        / "PROLOGUE_VO_manifest_v1.json").read_text(
                            encoding="utf-8"))
    for take in provo["segments"]:
        src_rel = f"Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT/{take['file']}"
        dest_rel = f"vo/prologue/{take['file']}"
        entry = copy_verified_audio(
            src_rel, dest_rel, take["sha256"],
            (ROOT / src_rel).stat().st_size, take["durationSeconds"],
            f"prologue VO {take['takeId']}")
        if entry is None:
            continue
        entry.update({"cueKey": f"VO/{take['takeId']}",
                      "category": "vo", "sceneId": "CIN_000",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 1,
                      "integratedLufs": take["integratedLufs"],
                      "truePeakDbtp": take["truePeakDbtp"],
                      "assetState": "DRAFT_NOT_FINAL_VO",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["vo"] += 1
    pmix27 = json.loads((ROOT / "Art_Source/Audio/Muse/MIX"
                         / "PROLOGUE_DRAFT/PROLOGUE_mix_manifest_v1.json"
                         ).read_text(encoding="utf-8"))
    entry = copy_verified_audio(
        "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav",
        "mix/prologue/PROLOGUE_mix_v1.wav", pmix27["sha256"],
        pmix27["sizeBytes"], pmix27["durationSeconds"],
        "prologue film mix")
    if entry is not None:
        entry.update({"cueKey": "MIX/CIN_000_PROLOGUE",
                      "category": "mix", "sceneId": "CIN_000",
                      "codec": "pcm_s16le", "sampleRateHz": 48000,
                      "channels": 2,
                      "integratedLufs": pmix27["integratedLufs"],
                      "truePeakDbtp": pmix27["truePeakDbtp"],
                      "assetState": "DRAFT_MIX_NOT_FINAL",
                      "wireStatus": "RUNTIME_DELIVERED_REQUIRES_CODEX_ADAPTER"})
        audio_entries.append(entry)
        counts["mix"] += 1

    audio_manifest = {
        "manifestId": "NGM_RUNTIME_AUDIO_V1",
        "checkpoint": ("MEDIA-02 WO37 M-D checkpoint 5 - M6 runtime "
                       "delivery revised: MD5 phase layers added (3 "
                       "layers, total 725 -> 728); MD4 phase layers "
                       "(checkpoint 4: 3 layers, total 722 -> 725); "
                       "MD3 intro/outro + "
                       "stems + phase layers (checkpoint 3: 9 intros "
                       "+ 9 outros + 27 stems + 3 layers, total "
                       "674 -> 722); MD2 "
                       "intro/outro + stems + phase layers "
                       "(checkpoint 2: 7 intros + 7 outros + 21 "
                       "stems + 2 layers, total 637 -> 674) and MD1 "
                       "score batch (checkpoint 1: 7 missing core "
                       "cues + 3 transition bridges, total 627 -> "
                       "637) unchanged; label also catches up "
                       "CIN_019 mix v1 (checkpoint 53) and CIN_020 "
                       "mix v1 (checkpoint 54) added since the "
                       "checkpoint-52 label; status phrasing corrected "
                       "(all 21 dialogue windows approved for DRAFT VO "
                       "production per the Goi 30 D1 decision, PR #120; "
                       "only CIN_001_S05 is DECIDED); P0 draft mixes v3 "
                       "(checkpoint 31), CIN_006 mix v1 (checkpoint 34), "
                       "CIN_003 mix v1 (checkpoint 37), CIN_005 mix v1 "
                       "(checkpoint 38), CIN_007 mix v1 (checkpoint 39), "
                       "CIN_008 mix v1 (checkpoint 40), CIN_009 mix v1 "
                       "(checkpoint 41), CIN_010 mix v1 (checkpoint 42), "
                       "CIN_011 mix v1 (checkpoint 45), "
                       "CIN_012 mix v1 (checkpoint 46), "
                       "CIN_013 mix v1 (checkpoint 47), "
                       "CIN_014 mix v1 (checkpoint 48), "
                       "CIN_015 mix v1 (checkpoint 49), "
                       "CIN_016 mix v1 (checkpoint 50), "
                       "CIN_017 mix v1 (checkpoint 51), "
                       "CIN_018 mix v1 (checkpoint 52), "
                       "prologue "
                       "(checkpoint 27/28), composed music "
                       "(checkpoint 26) and composed ambience "
                       "(checkpoint 30) unchanged"),
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "counts": counts,
        "totalFiles": len(audio_entries),
        "notes": [
            "Every file copied from real bytes and verified: sha256 + size + "
            "ffprobe duration against the checkpoint 04/07/08 pack records. "
            "LFS pointers fail the copy.",
            "All cues remain RENDERED_CANDIDATE / DRAFT_NOT_FINAL_VO. Files "
            "are delivered into the runtime tree; wiring them into Godot "
            "scenes/code is Codex's presentation adapter work (Muse writes "
            "no .gd/.tscn/.cs).",
            "Per-cue loudness only, NOT a mix PASS; no combined mix, no "
            "ducking was measured here.",
            "CIN_001_S05 is the only DECIDED dialogue window (24.8-28.5 s, "
            "version B); all 21 dialogue windows are approved for DRAFT "
            "VO production per the Goi 30 D1 decision (PR #120, "
            "media_draft_timing_decisions_20261105.json). The other 20 "
            "windows remain PROPOSED_ANIMATIC_PLACEMENT; final picture, "
            "mix and autoplay are NOT approved.",
            "Campaign VO (checkpoint 17): 17 draft takes, 15 FITS / 2 "
            "OVERRUN at natural speed (CIN_005_S03 -0.16 s, CIN_018_S03 "
            "-0.28 s; D1 forbids voice speed-up to fit, so the overruns "
            "stand as director findings). All 17 campaign windows are "
            "PROPOSED_ANIMATIC_PLACEMENT. PLAYER take is a timing-only "
            "placeholder voice; CIN_020 uses placeholder role voice "
            "VOICE_LETTER_RECIPIENT.",
            "CIN_006 VO (checkpoint 19): canonical take CIN_006_S03 "
            "(window 12.5-17.5 s PROPOSED, D1 draft only) + alternate "
            "take CIN_006_ALT_T01 v1-alt kept separate per DEC-MEDIA-P0 "
            "Q3 (no window assigned, not in the SRT, not on the scene "
            "timeline, does not replace canonical). With this delivery "
            "all 21 D1-approved dialogue windows have a draft VO take.",
            "P0 draft mixes (checkpoint 20): DRAFT_MIX_NOT_FINAL, "
            "built from the CP02 PROPOSED_CANDIDATE stem table and "
            "CP04 draft VO with formula gain staging and sidechain "
            "ducking; NOT a mix PASS (no ear audition, stem table "
            "not locked, stinger placements PROPOSED pending "
            "picture lock). The 72 s review mix is review/gallery "
            "only, NOT an auto-run opening.",
            "P0 draft mixes v2 (checkpoint 29): same three scenes + "
            "72 s review, re-mixed from the checkpoint-26 composed "
            "music + cinema stingers (ported ambience and CP04 VO "
            "unchanged; same placements, gain targets, ducking and "
            "peak guard as v1). Delivered in parallel under "
            "mix/p0_v2/; v1 mixes in mix/p0/ are untouched. "
            "Adoption is Codex's presentation-adapter decision. "
            "DRAFT_MIX_NOT_FINAL, no ear audition.",
            "P0 draft mixes v3 (checkpoint 31): same three scenes + "
            "72 s review, re-mixed from FULLY COMPOSED stems -- "
            "checkpoint-26 music/stingers plus checkpoint-30 "
            "composed ambience (no ported stem remains in the P0 "
            "mixes; same placements, gain targets, ducking and "
            "peak guard as v2). Delivered in parallel under "
            "mix/p0_v3/; v1 and v2 mixes are untouched. Adoption "
            "is Codex's presentation-adapter decision. "
            "DRAFT_MIX_NOT_FINAL, no ear audition.",
            "Composed music + stingers (checkpoint 26, Goi 30 item "
            "7): 13 ORIGINAL cues composed by Muse (9 music + 4 "
            "SFX/CINEMA stingers), provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/ from MUSIC_COMPOSED_pack_v1.json. "
            "They do NOT replace the ported PackV1 files (541 files, "
            "checkpoints 07/08) or their bindings; adoption is "
            "Codex's presentation-adapter decision. Loudness is "
            "measured from real bytes; no ear audition.",
            "Composed ambience (checkpoint 30): 13 ORIGINAL cues "
            "composed by Muse (all AMBIENCE/* cues), provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/ambience/ from "
            "AMBIENCE_COMPOSED_pack_v1.json. Filtered-noise beds + "
            "sparse deterministic events; crowd beds are filtered "
            "noise only (no voices, no words). They do NOT replace "
            "the ported PackV1 files or their bindings; adoption is "
            "Codex's presentation-adapter decision. Loudness targets "
            "are the ported cues' checkpoint-07 measured LUFS; "
            "measured from real bytes; no ear audition.",
            "WO37 M-D checkpoint 3 intro/outro + stems + phase layers "
            "(MD3): 48 ORIGINAL files composed by Muse -- 2-bar "
            "intro/outro for each of the 9 checkpoint-26 cues, lead / "
            "pad-bass / percussion stems per checkpoint-26 cue (the "
            "three stems sum to the shipped checkpoint-26 master "
            "within 24-bit quantisation, re-checked from real bytes "
            "by the MD3 validator), and additive phase layers "
            "MUSIC/boss_mang_cot_layer_phase3, "
            "MUSIC/tragedy_layer_intensity and MUSIC/arena_layer_low "
            "(combined base+layer loudness measured from real bytes) "
            "-- provenance ORIGINAL_COMPOSED_BY_MUSE, delivered in "
            "parallel under assets/audio/composed/intros/, "
            ".../outros/, .../stems/ and .../layers/ from "
            "MUSIC_SCORE_MD3_pack_v1.json; coverage matrix "
            "MUSIC_SCORE_MD_COVERAGE_v1.json records the MD3 delivery "
            "and lists openForMdCp4, including the recovered per-cue "
            "RNG histories (the checkpoint-26 masters were built in "
            "several separate renders, in pairs per --only run). They "
            "do NOT replace the ported PackV1 files, their bindings, "
            "or the checkpoint-26/30/MD1/MD2 cues; adoption is Codex's "
            "presentation-adapter decision. No ear audition.",
            "WO37 M-D checkpoint 4 phase layers (MD4): 3 ORIGINAL "
            "files composed by Muse -- additive phase layers "
            "MUSIC/boss_mang_cot_layer_phase4, "
            "MUSIC/swamp_layer_intensity and "
            "MUSIC/dungeon_layer_intensity (combined base+layer "
            "loudness measured from real bytes) -- provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/layers/ from "
            "MUSIC_SCORE_MD4_pack_v1.json; coverage matrix "
            "MUSIC_SCORE_MD_COVERAGE_v1.json records the MD4 delivery "
            "and lists openForMdCp5. They do NOT replace the ported "
            "PackV1 files, their bindings, or the "
            "checkpoint-26/30/MD1/MD2/MD3 cues; adoption is Codex's "
            "presentation-adapter decision. No ear audition.",
            "WO37 M-D checkpoint 5 phase layers (MD5): 3 ORIGINAL "
            "files composed by Muse -- additive phase layers "
            "MUSIC/boss_mang_cot_layer_phase5, "
            "MUSIC/hub_layer_intensity and "
            "MUSIC/rain_layer_intensity (combined base+layer "
            "loudness measured from real bytes) -- provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/layers/ from "
            "MUSIC_SCORE_MD5_pack_v1.json; coverage matrix "
            "MUSIC_SCORE_MD_COVERAGE_v1.json records the MD5 delivery "
            "and lists openForMdCp6. Boss phase 5 completes the "
            "16th-note drum grid with 16th-note octave bass, a D6 "
            "bell every bar and the minor head in flute (the first "
            "flute in any boss layer -- the base has no flute at "
            "all); hub intensity adds the festival pulse a drumless "
            "home base withholds; rain intensity adds the weight of "
            "heavier rain inside the base's own 1200 Hz veil. They "
            "do NOT replace the ported PackV1 files, their bindings, "
            "or the checkpoint-26/30/MD1/MD2/MD3/MD4 cues; adoption "
            "is Codex's presentation-adapter decision. No ear "
            "audition.",
            "WO37 M-D checkpoint 2 intro/outro + stems + phase layers "
            "(MD2): 37 ORIGINAL files composed by Muse -- 2-bar "
            "intro/outro for each of the 7 MD1 cues, lead / pad-bass "
            "/ percussion stems per MD1 cue (the three stems sum to "
            "the shipped MD1 master within 24-bit quantisation, "
            "re-checked from real bytes by the MD2 validator), and "
            "additive phase layers MUSIC/arena_layer_high and "
            "MUSIC/boss_mang_cot_layer_phase2 (combined base+layer "
            "loudness measured from real bytes) -- provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/intros/, .../outros/, .../stems/ "
            "and .../layers/ from MUSIC_SCORE_MD2_pack_v1.json; "
            "coverage matrix MUSIC_SCORE_MD_COVERAGE_v1.json records "
            "the MD2 delivery and lists openForMdCp3. They do NOT "
            "replace the ported PackV1 files, their bindings, or the "
            "checkpoint-26/30/MD1 cues; adoption is Codex's "
            "presentation-adapter decision. No ear audition.",
            "WO37 M-D checkpoint 1 score batch (MD1): 10 ORIGINAL "
            "cues composed by Muse (7 missing core score cues -- hub, "
            "Thanh Lac, rain, swamp, dungeon, arena, tragedy -- + 3 "
            "transition bridges), provenance "
            "ORIGINAL_COMPOSED_BY_MUSE, delivered in parallel under "
            "assets/audio/composed/music/ and "
            "assets/audio/composed/transitions/ from "
            "MUSIC_SCORE_MD1_pack_v1.json; coverage matrix "
            "MUSIC_SCORE_MD_COVERAGE_v1.json now shows 15/15 M-D "
            "slots covered, 0 gaps. They do NOT replace the ported "
            "PackV1 files, their bindings, or the checkpoint-26/30 "
            "composed packs; adoption is Codex's presentation-adapter "
            "decision. Loudness measured from real bytes (music "
            "-22 LUFS target, transitions -25 LUFS); no ear audition. "
            "Intro/outro segments, stems and phase-layer candidates "
            "remain open for M-D checkpoint 2.",
            "Prologue CIN_000 (checkpoint 27): 5 narration draft "
            "takes (fictional TTS narrator, DRAFT casting) + the "
            "film's draft mix (narration + checkpoint 26 composed "
            "Ben Mua theme + ported rain/river ambience, sidechain "
            "ducked; the mix is also embedded in the film files). "
            "The final line of the film reuses the checkpoint 04 "
            "CIN_001_S05 take and is NOT re-registered here (it is "
            "already counted with the P0 VO). DRAFT states only; no "
            "ear audition.",
        ],
        "files": audio_entries,
    }
    (AUDIO_DEST / "RUNTIME_AUDIO_manifest_v1.json").write_text(
        json.dumps(audio_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # --- 4. Cinematics: verify P0 animatic already in runtime (cp03, revised cp13) ---
    cine_files = []
    for name, expect_sha in ANIMATIC_EXPECTED.items():
        p = CINE_DEST / name
        check(p.exists(), f"animatic missing in runtime: {name}")
        if not p.exists():
            continue
        check(not is_lfs_pointer(p), f"animatic is LFS pointer: {name}")
        got = sha256(p)
        check(got == expect_sha, f"animatic sha mismatch: {name}")
        cine_files.append({"runtimePath": f"assets/cinematics/{name}",
                           "sha256": got, "sizeBytes": p.stat().st_size,
                           "status": "VERIFIED_CHECKPOINT_13"})

    # --- 5. Timing JSON + SRT for all 20 scenes (cp01/05/06) ---
    scenes = {}
    p0m = json.loads((ROOT / "Implementation/Content/Narrative/Deliveries"
                      / "P0_timing_manifest_v1.json").read_text(
                          encoding="utf-8"))
    for s in p0m["scenes"]:
        scenes[s["sceneId"]] = s
    camp = json.loads((ROOT / "Implementation/Content/Narrative/Deliveries"
                       / "CAMPAIGN_timing_manifest_v1.json").read_text(
                           encoding="utf-8"))
    for s in camp["scenes"]:
        scenes[s["sceneId"]] = s
    c6 = json.loads((ROOT / "Implementation/Content/Narrative/Deliveries"
                     / "CIN_006/CIN_006_timing_manifest_v1.json").read_text(
                         encoding="utf-8"))
    scenes[c6["scene"]["sceneId"]] = c6["scene"]
    check(len(scenes) == 20, f"expected 20 scenes, got {len(scenes)}")

    timing_dir = CINE_DEST / "timing"
    timing_dir.mkdir(parents=True, exist_ok=True)
    scene_entries = []
    for scene_id in sorted(scenes):
        s = scenes[scene_id]
        timing_src = ROOT / s["timingFile"]
        srt_src = ROOT / s["srtFile"]
        check(timing_src.exists(), f"{scene_id}: timing missing")
        check(srt_src.exists(), f"{scene_id}: srt missing")
        if not (timing_src.exists() and srt_src.exists()):
            continue
        check(not is_lfs_pointer(timing_src),
              f"{scene_id}: timing is LFS pointer")
        check(not is_lfs_pointer(srt_src), f"{scene_id}: srt is LFS pointer")
        timing_dest = timing_dir / timing_src.name
        srt_dest = timing_dir / srt_src.name
        shutil.copyfile(timing_src, timing_dest)
        shutil.copyfile(srt_src, srt_dest)
        srt_sha = sha256(srt_dest)
        check(srt_sha == s["srtSha256"],
              f"{scene_id}: srt sha mismatch {srt_sha} != {s['srtSha256']}")
        timing = json.loads(timing_dest.read_text(encoding="utf-8"))
        # Gói 30 item 1 / PR119 review finding 1: dialogueCues must come
        # from parsed timing dialogue + SRT, NOT from len(s.get("cues")).
        # The three source manifests have different shapes: P0 and CIN_006
        # scenes carry no "cues" key at all, so the old expression wrote 0
        # for CIN_001/002/004/006 even though each SRT has one cue. Any
        # disagreement between the three layers aborts the delivery.
        timing_dialogues = sum(
            1 for sh in timing.get("shots", [])
            if isinstance(sh.get("dialogue"), dict))
        srt_cues = count_srt_cues(srt_dest.read_text(encoding="utf-8"))
        check(srt_cues is not None,
              f"{scene_id}: unparseable SRT {srt_src.name}")
        if srt_cues is not None:
            check(timing_dialogues == srt_cues,
                  f"{scene_id}: timing dialogues {timing_dialogues} "
                  f"!= SRT cues {srt_cues}")
        if "cues" in s:
            check(len(s["cues"]) == timing_dialogues,
                  f"{scene_id}: source manifest cues {len(s['cues'])} "
                  f"!= timing dialogues {timing_dialogues}")
        scene_entries.append({
            "sceneId": scene_id,
            "durationSeconds": s.get("durationSeconds",
                                     timing.get("durationSeconds")),
            "shots": s.get("shots", len(timing.get("shots", []))),
            "timingFile": f"assets/cinematics/timing/{timing_src.name}",
            "timingSha256": sha256(timing_dest),
            "srtFile": f"assets/cinematics/timing/{srt_src.name}",
            "srtSha256": srt_sha,
            "srtStatus": s.get("srtStatus", "DRAFT"),
            "dialogueWindowStatus": s.get("dialogueWindowStatus"),
            "dialogueCues": timing_dialogues,
        })
    total_dialogue_cues = sum(e["dialogueCues"] for e in scene_entries)

    # --- 6. Per-scene clips (checkpoint 18, Goi 30 item 6; CIN_005
    # animated take added in checkpoint 21, CIN_006 in checkpoint 22,
    # CIN_009 in checkpoint 23, CIN_020 in checkpoint 24, and the
    # remaining 13 campaign scenes in the checkpoint 25 batch,
    # Goi 30 item 7) ---
    # Each scene folder holds its own MP4/OGV/poster/SRT/timing + export
    # manifest; all 20 scenes now carry video.
    # Verified here against the export manifests, not trusted blindly.
    scene_clip_entries = []
    for scene_id in ("CIN_001", "CIN_002", "CIN_004", "CIN_006", "CIN_005",
                     "CIN_009", "CIN_020",
                     "CIN_003", "CIN_007", "CIN_008", "CIN_010", "CIN_011",
                     "CIN_012", "CIN_013", "CIN_014", "CIN_015", "CIN_016",
                     "CIN_017", "CIN_018", "CIN_019"):
        exp_path = CINE_DEST / scene_id / "scene_export_manifest_v1.json"
        check(exp_path.exists(),
              f"scene clip manifest missing: {scene_id}")
        if not exp_path.exists():
            continue
        exp = json.loads(exp_path.read_text(encoding="utf-8"))
        check(exp.get("sceneId") == scene_id,
              f"scene clip manifest sceneId mismatch: {scene_id}")
        for key, f in exp.get("files", {}).items():
            p = ROOT / "ClientGodot" / f["path"]
            check(p.exists(), f"scene clip missing: {f['path']}")
            if not p.exists():
                continue
            check(not is_lfs_pointer(p),
                  f"scene clip is LFS pointer: {f['path']}")
            check(sha256(p) == f["sha256"],
                  f"scene clip sha mismatch: {f['path']}")
            check(p.stat().st_size == f["sizeBytes"],
                  f"scene clip size mismatch: {f['path']}")
            if key in ("mp4", "ogv"):
                try:
                    got_dur = ffprobe_duration_s(p)
                except Exception as e:  # noqa: BLE001
                    failures.append(f"scene clip {scene_id}/{key}: "
                                    f"ffprobe failed: {e}")
                    continue
                check(abs(got_dur - f["durationSeconds"]) <= DUR_TOL_S,
                      f"scene clip {scene_id}/{key}: duration {got_dur} "
                      f"!= manifest {f['durationSeconds']}")
        # Checkpoint 34 (Goi 31 item 4): a clip that declares an
        # embedded audio track must carry an audio stream in BOTH
        # the runtime OGV and the review MP4 (mirrors the 6b
        # prologue check). Clips without the flag stay silent.
        if exp.get("hasAudioTrack") is True:
            for key in ("mp4", "ogv"):
                f = exp["files"][key]
                p = ROOT / "ClientGodot" / f["path"]
                pr = json.loads(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_streams",
                     "-of", "json", str(p)],
                    capture_output=True, text=True).stdout)
                kinds = [s["codec_type"] for s in pr["streams"]]
                check("audio" in kinds,
                      f"scene clip {scene_id}/{key} declares audio "
                      f"but has no audio stream")
                if "audio" in kinds:
                    a = next(s for s in pr["streams"]
                             if s["codec_type"] == "audio")
                    check(a["codec_name"] == f["audio"]["codec"],
                          f"scene clip {scene_id}/{key} audio codec "
                          f"{a['codec_name']} != {f['audio']['codec']}")
        scene_clip_entries.append({
            "sceneId": scene_id,
            "durationSeconds": exp["durationSeconds"],
            "videoStatus": exp["videoStatus"],
            "reelOffsetSeconds": exp.get("reelOffsetSeconds"),
            "dialogueCues": exp["dialogueCues"],
            "files": exp["files"],
        })
    check(len(scene_clip_entries) == 20,
          f"expected 20 per-scene clip exports, got "
          f"{len(scene_clip_entries)}")

    # --- 6b. Prologue film CIN_000 (checkpoint 27) ---
    # Standalone pre-game film; verified in place against its own
    # scene export manifest and registered under a separate
    # "prologue" key -- never inside sceneClips / campaignTotals.
    pro_exp_path = (CINE_DEST / "CIN_000"
                    / "scene_export_manifest_v1.json")
    check(pro_exp_path.exists(), "prologue export manifest missing")
    prologue_entry = None
    if pro_exp_path.exists():
        pexp = json.loads(pro_exp_path.read_text(encoding="utf-8"))
        check(pexp.get("sceneId") == "CIN_000",
              "prologue export manifest sceneId mismatch")
        check(pexp.get("hasAudioTrack") is True,
              "prologue export must declare an embedded audio track")
        for key in ("mp4", "ogv", "poster"):
            f = pexp[key]
            p = ROOT / f["path"]
            check(p.exists(), f"prologue file missing: {f['path']}")
            if not p.exists():
                continue
            check(not is_lfs_pointer(p),
                  f"prologue file is LFS pointer: {f['path']}")
            check(sha256(p) == f["sha256"],
                  f"prologue sha mismatch: {f['path']}")
            check(p.stat().st_size == f["sizeBytes"],
                  f"prologue size mismatch: {f['path']}")
            if key in ("mp4", "ogv"):
                got_dur = ffprobe_first_stream_duration_s(p)
                check(abs(got_dur - f["durationSeconds"]) <=
                      DUR_TOL_S,
                      f"prologue {key} duration {got_dur} != "
                      f"{f['durationSeconds']}")
                pr = json.loads(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_streams",
                     "-of", "json", str(p)],
                    capture_output=True, text=True).stdout)
                kinds = [s["codec_type"] for s in pr["streams"]]
                check("audio" in kinds,
                      f"prologue {key} has NO audio stream")
        for key, sha_key in (("timingFile", "timingSha256"),
                             ("srtFile", "srtSha256")):
            p = CINE_DEST / "CIN_000" / pexp[key]
            check(p.exists(), f"prologue {key} missing in runtime")
            if p.exists():
                check(sha256(p) == pexp[sha_key],
                      f"prologue {key} sha mismatch")
        # --- 6c. Prologue subtitled variant (checkpoint 28) ---
        # Owner-requested viewing variant of the same film: burned-in
        # + embedded readable Vietnamese subtitles, narration at
        # +5 dB presentation gain. Verified in place against the
        # export manifest and registered alongside the canonical
        # files; canonical MP4/OGV/SRT are unchanged.
        pro_sub = None
        if "mp4SubVi" in pexp:
            f = pexp["mp4SubVi"]
            p = ROOT / f["path"]
            check(p.exists(),
                  f"prologue sub-vi file missing: {f['path']}")
            if p.exists():
                check(not is_lfs_pointer(p),
                      f"prologue sub-vi file is LFS pointer: "
                      f"{f['path']}")
                check(sha256(p) == f["sha256"],
                      f"prologue sub-vi sha mismatch: {f['path']}")
                check(p.stat().st_size == f["sizeBytes"],
                      f"prologue sub-vi size mismatch: {f['path']}")
                got_dur = ffprobe_first_stream_duration_s(p)
                check(abs(got_dur - f["durationSeconds"]) <=
                      DUR_TOL_S,
                      f"prologue sub-vi duration {got_dur} != "
                      f"{f['durationSeconds']}")
                pr = json.loads(subprocess.run(
                    ["ffprobe", "-v", "error", "-show_streams",
                     "-of", "json", str(p)],
                    capture_output=True, text=True).stdout)
                kinds = [s["codec_type"] for s in pr["streams"]]
                check(kinds == ["video", "audio", "subtitle"],
                      f"prologue sub-vi streams {kinds} != "
                      f"[video, audio, subtitle]")
            rs = pexp["readableSrt"]
            rp = ROOT / rs["path"]
            check(rp.exists(), "prologue readable SRT missing")
            if rp.exists():
                check(sha256(rp) == rs["sha256"],
                      "prologue readable SRT sha mismatch")
                check(rp.stat().st_size == rs["sizeBytes"],
                      "prologue readable SRT size mismatch")
            pro_sub = {
                "mp4SubVi": f,
                "readableSrtFile": "assets/cinematics/CIN_000/"
                                   "CIN_000_vi_readable.srt",
                "readableSrtSha256": rs["sha256"],
            }
        prologue_entry = {
            "sceneId": "CIN_000",
            "title": pexp["title"],
            "durationSeconds": pexp["durationSeconds"],
            "videoStatus": pexp["videoStatus"],
            "hasAudioTrack": True,
            "mp4": pexp["mp4"], "ogv": pexp["ogv"],
            "poster": pexp["poster"],
            "timingFile": "assets/cinematics/CIN_000/"
                          "CIN_000_timing_v1.json",
            "timingSha256": pexp["timingSha256"],
            "srtFile": "assets/cinematics/CIN_000/CIN_000_vi.srt",
            "srtSha256": pexp["srtSha256"],
            **(pro_sub or {}),
        }

    cine_manifest = {
        "manifestId": "NGM_RUNTIME_CINEMATICS_V1",
        "checkpoint": "MEDIA-02 checkpoint 51 - Goi 31 item 4 extended (prologue + CIN_001/002/004/006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 + CIN_012 + CIN_013 + CIN_014 + CIN_015 + CIN_016 + CIN_017: P0 mixes v3, CIN_006 mix v1, CIN_003 mix v1, CIN_005 mix v1, CIN_007 mix v1, CIN_008 mix v1, CIN_009 mix v1, CIN_010 mix v1, CIN_011 mix v1, CIN_012 mix v1, CIN_013 mix v1, CIN_014 mix v1, CIN_015 mix v1, CIN_016 mix v1 and CIN_017 mix v1 embedded in the runtime OGV + review MP4; poster + SRT + timing per scene; baked-subtitle variant stays review-only); checkpoint 32 shot fixes + status phrasing (all 21 dialogue windows approved for DRAFT VO per Goi 30 D1, PR #120; only CIN_001_S05 DECIDED) otherwise unchanged; prologue CIN_000 subtitled viewing variant registered under the 'prologue' key (mp4SubVi: burned-in + embedded readable Vietnamese subtitles, narration +5 dB presentation gain; canonical film files unchanged); checkpoint 27 prologue registration otherwise unchanged (standalone pre-game film with embedded mixed audio; NOT part of the 20-scene campaign totals); campaign video batch (checkpoint 25) + P0 animatic v3 + audio/timing otherwise unchanged",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "campaignTotals": {"scenes": 20, "shots": 63, "seconds": 378,
                           "dialogueCues": total_dialogue_cues},
        "notes": [
            "P0 animatic v3 (MP4 review + OGV runtime + poster) verified "
            "against checkpoint 16 SHAs (outputs v3 manifest); 5 panels "
            "revised in total (4 in checkpoint 13: CIN_001_S03, CIN_001_S06, "
            "CIN_004_S01, CIN_004_S03; 1 in checkpoint 16: CIN_002_S02), "
            "7 panels byte-identical to v1; poster unchanged (CIN_001_S01). "
            "Separate 16:9 keyframes per shot in "
            "Art_Source/Cinematics/P0_Animatic/keyframes_16x9/ "
            "(P0_keyframes_16x9_manifest_v1.json).",
            "Timing JSON + SRT per scene copied from Narrative/Deliveries "
            "with sha256 verification against the checkpoint 01/05/06 "
            "manifests. SRT is UTF-8/NFC, DRAFT.",
            "dialogueCues is derived from parsed timing JSON "
            "shots[].dialogue, cross-checked against the parsed SRT cue "
            "count and, where present, the source manifest 'cues' list "
            "(Gói 30 item 1 / PR119 review finding 1). P0 + CIN_006 source "
            "manifests carry no 'cues' key; their counts come from "
            "timing/SRT. Any disagreement aborts this build.",
            "CIN_001_S05 (24.8-28.5 s, version B) is the only DECIDED "
            "dialogue window; the other 20 windows remain "
            "PROPOSED_ANIMATIC_PLACEMENT, but all 21 windows are "
            "approved for DRAFT VO production per the Goi 30 D1 "
            "decision (PR #120, "
            "media_draft_timing_decisions_20261105.json). Final picture, "
            "mix and autoplay are NOT approved. (Status phrasing "
            "corrected in checkpoint 32, Goi 31 item 1.)",
            "No final picture: animatic is storyboard level (revision v3 "
            "fixes all 5 recorded panel defects, not final picture); "
            "character keyframes still await lock for locked shots.",
            "Per-scene clips (checkpoint 18, Goi 30 item 6): CIN_001 "
            "(36 s), CIN_002 (18 s) and CIN_004 (18 s) each exported as "
            "its own MP4 + OGV + poster + SRT + timing + hash manifest "
            "under assets/cinematics/<SCENE>/. The 72 s reel stays "
            "review/gallery only, NOT auto-run as opening.",
            "CIN_005 animated take (checkpoint 21, Goi 30 item 7): first "
            "campaign video with real motion -- 18 s / 3 shots, slow Ken "
            "Burns camera moves on 3 storyboard keyframes "
            "(Art_Source/Cinematics/Campaign/CIN_005/keyframes_16x9/, "
            "CIN005_keyframes_manifest_v1.json). Animatic-level motion, "
            "NOT a final pose-animated take; no audio track in the clip "
            "(VO/music/ambience added separately in editing); no baked "
            "subtitles. Known defect: S02 roof palette drifts from S01.",
            "CIN_006 animated take (checkpoint 22, Goi 30 item 7): the "
            "scene leaves PENDING_PANELS_NO_STORYBOARD with 3 storyboard "
            "keyframes (Art_Source/Cinematics/Campaign/CIN_006/"
            "keyframes_16x9/, CIN006_keyframes_manifest_v1.json) + 18 s "
            "Ken Burns clip. NPC_HA_MAC / NPC_SAM_CHU_QUY have NO "
            "approved character lock: faces/costumes are storyboard "
            "placeholders, cinematic-only staging per DEC-MEDIA-P0 Q4. "
            "Known defects: S02's composition defect (oversized blurred "
            "glove + pale face-like shape at frame right) was FIXED in "
            "checkpoint 32 (Goi 31 item 2, retry 3: whole-table view, "
            "small glove, fiber trapped inside the paper); cross-shot "
            "lighting drift remains, recorded per shot for the "
            "final-picture revision pass.",
            "CIN_009 animated take (checkpoint 23, Goi 30 item 7): first "
            "Chapter 2 campaign scene with video -- 18 s / 3 shots, slow "
            "Ken Burns camera moves on 3 storyboard keyframes "
            "(Art_Source/Cinematics/Campaign/CIN_009/keyframes_16x9/, "
            "CIN009_keyframes_manifest_v1.json). Pack character list is "
            "empty, so no character lock is involved; the S02 workers "
            "are unnamed generation-invented figures. Animatic-level "
            "motion, NOT a final pose-animated take; no audio track in "
            "the clip (VO/music/ambience added separately in editing); "
            "no baked subtitles. Known defects: S01's invented white "
            "hooded figure was REMOVED in checkpoint 32 (Goi 31 item 2) "
            "and the spring now reads as a bright daylight payoff; S03 "
            "is not strictly top-down and adds a shrine not in the "
            "prompt (unchanged).",
            "CIN_020 animated take (checkpoint 24, Goi 30 item 7): the "
            "closing campaign scene -- 18 s / 3 shots, slow Ken Burns "
            "camera moves on 3 storyboard keyframes "
            "(Art_Source/Cinematics/Campaign/CIN_020/keyframes_16x9/, "
            "CIN020_keyframes_manifest_v1.json). Pack character list is "
            "empty, so no character lock is involved; the villager is "
            "an unnamed figure. Animatic-level motion, NOT a final "
            "pose-animated take; no audio track in the clip; no baked "
            "subtitles. Known defects: the same villager wears three "
            "different outfits/headgear across the shots (continuity "
            "drift) and S02 is an interior medium shot instead of a "
            "detail close view. Also fixed in this checkpoint: the "
            "CIN_009 keyframe manifest carried CIN_006's title "
            "('Con dau qua pho') since checkpoint 23 -- corrected to "
            "'Tieng rung duoc dap' in the manifest and its builder.",
            "Campaign video batch (checkpoint 25, Goi 30 item 7): the "
            "remaining 13 campaign scenes (CIN_003, CIN_007, CIN_008, "
            "CIN_010, CIN_011, CIN_012, CIN_013, CIN_014, CIN_015, "
            "CIN_016, CIN_017, CIN_018, CIN_019) each gained an 18 s "
            "animated take -- slow Ken Burns camera moves on 3 "
            "storyboard keyframes per scene, generated in parallel "
            "staging runs from the pack shot prompts verbatim "
            "(Art_Source/Cinematics/Campaign/<scene>/keyframes_16x9/ + "
            "per-scene keyframe manifests; builder "
            "build_campaign_batch_video.py). All 20 scenes now carry "
            "video. Every batch scene has named characters on screen "
            "with NO approved cinematic character lock, so all batch "
            "faces/costumes are storyboard placeholders and final "
            "picture per shot stays blocked on the lock; animatic-level "
            "motion, NOT final pose-animated takes; no audio track in "
            "the clips; no baked subtitles. Headline recorded defects "
            "(full per-shot records in the keyframe manifests): "
            "CIN_012_S03 carries a baked-in game choice UI bar with "
            "legible English buttons (hard clean-frame violation); "
            "CIN_017_S02 misses its subject entirely (no crystal core, "
            "no serpent; invented robed man); CIN_015_S02 is a dry "
            "above-water courtyard instead of the drowned ruin, with "
            "an invented mascot figure (the same white hooded "
            "mascot-like intrusion also appears in CIN_012_S01); "
            "CIN_011 invents a design-consistent teal-robed woman in "
            "S01 and S03 who is in no prompt; CIN_010's environment "
            "collapses after S01 (desert -> bamboo grove -> scrub) and "
            "its Sam is a slim young man, not the stocky middle-aged "
            "merchant of the brief; CIN_008_S03's bandage reads on the "
            "character's right forearm while canon places it on the "
            "LEFT; CIN_018 has two dialogue cues and its S03 VO draft "
            "still overruns its window by +0.280 s (owner decision "
            "2026-11-06: window kept as-is, Codex decides at PR "
            "review). All headline defects listed in this note were "
            "FIXED in checkpoint 32 (Goi 31 item 2): 14 revised "
            "keyframes across 8 scenes (CIN_006, CIN_008, CIN_009, "
            "CIN_010, CIN_011, CIN_012, CIN_015, CIN_017), "
            "re-exported video, before/after contact sheets; the "
            "revised keyframe manifests carry the new known-defect "
            "state per shot.",
            "Prologue film CIN_000 (checkpoint 27): a standalone "
            "87.367 s pre-game lore film (owner-ordered; narration "
            "script approved in main chat 2026-11-06), registered "
            "under the separate 'prologue' key -- it is NOT one of "
            "the 20 campaign scenes and is not counted in "
            "campaignTotals. Unlike the campaign clips it CARRIES "
            "its mixed soundtrack (narration + composed theme + "
            "ambience) embedded in the MP4/OGV. Picture: 11 "
            "painterly cinematic panels + a code-rendered title "
            "card (poster = the title card). Canon guardrails: no "
            "avatar origin/face/bloodline, no naming of Co Vo "
            "Tuong / the hop mach mechanism / Ta Van Khanh's "
            "responsibility (reveal table), the traveler is an "
            "unnamed back-view silhouette, and the film ends on "
            "the checkpoint 04 CIN_001_S05 line (reused take) so "
            "it hands off into CIN_001. Recorded defects include "
            "the S01/S03 mechanism design drift and S11's "
            "ambiguous arrival direction (full per-shot records in "
            "CIN000_keyframes_manifest_v1.json). Wiring the "
            "prologue into the post-character-creation flow is "
            "Codex's presentation-adapter work.",
            "Shot-content fixes (checkpoint 32, Goi 31 item 2): the "
            "three Codex-review errors are fixed without waiting for "
            "the character lock -- CIN_012_S03's baked-in English "
            "choice UI bar is removed (frame clean for the game's own "
            "choice overlay), CIN_017_S02 now shows the white-blue "
            "crystal core supported by three stone pressure channels "
            "with the tide serpent coiled around it (no machine, no "
            "robed man), CIN_015_S02 is now a fully submerged drowned "
            "ruin (dining bowl, guide rope, bare diver hand; no "
            "mascot, no clay pot) -- plus unprompted mascot/character "
            "cleanup (CIN_012_S01, CIN_015_S01, CIN_017_S03, "
            "CIN_011_S01/S03, CIN_009_S01, CIN_006_S02), bandage on "
            "the LEFT forearm (CIN_008_S03) and environment continuity "
            "(CIN_010_S02/S03 back to the ash-gold desert caravan rest "
            "of S01; CIN_015_S03 reads underwater). 14 revised "
            "keyframes across 8 scenes, each with a before/after "
            "contact sheet next to the keyframes; the 8 scene videos "
            "were re-exported with the same motion model per shot. "
            "Motion is still animatic-level Ken Burns on storyboard "
            "stills, NOT final pose animation; final picture per shot "
            "stays blocked on the character lock.",
        ],
        "animatic": cine_files,
        "sceneClips": scene_clip_entries,
        "prologue": prologue_entry,
        "scenes": scene_entries,
    }
    (CINE_DEST / "RUNTIME_CINEMATICS_manifest_v1.json").write_text(
        json.dumps(cine_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"audio copied: music/ambience={counts['music_ambience']} "
          f"sfx/ui variants={counts['sfx_ui_variants']} vo={counts['vo']} "
          f"mix={counts['mix']} composed={counts['composed']} "
          f"total={len(audio_entries)}")
    print(f"cinematics: animatic verified={len(cine_files)} "
          f"sceneClips={len(scene_clip_entries)} "
          f"scenes={len(scene_entries)} "
          f"(timing+srt files={len(scene_entries) * 2})")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print(" - " + f)
        return 1
    print("M6 runtime delivery: ALL VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
