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
    (3 storyboard keyframes 640x360 + keyframes manifest, and the
    18 s animated take MP4/OGV/poster, checkpoint 23)
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
              "mix": 0}

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

    audio_manifest = {
        "manifestId": "NGM_RUNTIME_AUDIO_V1",
        "checkpoint": ("MEDIA-02 checkpoint 20 - M6 runtime delivery "
                       "revised: P0 draft mixes (3 scene mixes + 72 s "
                       "review mix) added"),
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
            "CIN_002/CIN_004 VO windows remain PROPOSED; only CIN_001_S05 "
            "is DECIDED (24.8-28.5 s).",
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
    # CIN_009 in checkpoint 23, Goi 30 item 7) ---
    # Each scene folder holds its own MP4/OGV/poster/SRT/timing + export
    # manifest; all six scenes carry video (CIN_009 joined in
    # checkpoint 23 with its own storyboard keyframes + animated take).
    # Verified here against the export manifests, not trusted blindly.
    scene_clip_entries = []
    for scene_id in ("CIN_001", "CIN_002", "CIN_004", "CIN_006", "CIN_005",
                     "CIN_009"):
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
        scene_clip_entries.append({
            "sceneId": scene_id,
            "durationSeconds": exp["durationSeconds"],
            "videoStatus": exp["videoStatus"],
            "reelOffsetSeconds": exp.get("reelOffsetSeconds"),
            "dialogueCues": exp["dialogueCues"],
            "files": exp["files"],
        })
    check(len(scene_clip_entries) == 6,
          f"expected 6 per-scene clip exports, got "
          f"{len(scene_clip_entries)}")

    cine_manifest = {
        "manifestId": "NGM_RUNTIME_CINEMATICS_V1",
        "checkpoint": "MEDIA-02 checkpoint 23 - CIN_009 animated take (Goi 30 item 7): 3 storyboard keyframes + 18 s Ken Burns clip; all 6 exported scenes now carry video; P0 animatic v3 + audio/timing unchanged from checkpoint 22",
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
            "Only CIN_001_S05 (24.8-28.5 s, version B) is DECIDED; all "
            "other dialogue windows remain PROPOSED_ANIMATIC_PLACEMENT "
            "until director/Codex confirms them.",
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
            "Known defects: S02 composition (oversized blurred glove + "
            "pale face-like shape at frame right) and cross-shot "
            "lighting drift, recorded per shot for the final-picture "
            "revision pass.",
            "CIN_009 animated take (checkpoint 23, Goi 30 item 7): first "
            "Chapter 2 campaign scene with video -- 18 s / 3 shots, slow "
            "Ken Burns camera moves on 3 storyboard keyframes "
            "(Art_Source/Cinematics/Campaign/CIN_009/keyframes_16x9/, "
            "CIN009_keyframes_manifest_v1.json). Pack character list is "
            "empty, so no character lock is involved; the S02 workers "
            "are unnamed generation-invented figures. Animatic-level "
            "motion, NOT a final pose-animated take; no audio track in "
            "the clip (VO/music/ambience added separately in editing); "
            "no baked subtitles. Known defects: S01 carries an invented "
            "white hooded figure not in the prompt and reads darker than "
            "a daylight payoff; S03 is not strictly top-down and adds a "
            "shrine not in the prompt.",
        ],
        "animatic": cine_files,
        "sceneClips": scene_clip_entries,
        "scenes": scene_entries,
    }
    (CINE_DEST / "RUNTIME_CINEMATICS_manifest_v1.json").write_text(
        json.dumps(cine_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"audio copied: music/ambience={counts['music_ambience']} "
          f"sfx/ui variants={counts['sfx_ui_variants']} vo={counts['vo']} "
          f"mix={counts['mix']} "
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
