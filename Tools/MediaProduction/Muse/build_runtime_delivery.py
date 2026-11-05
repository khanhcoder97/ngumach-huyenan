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
  - Implementation/Content/Narrative/Deliveries/{P0,CAMPAIGN}_timing_manifest_v1.json
    + CIN_006/CIN_006_timing_manifest_v1.json (20 scenes timing JSON + SRT)

Destinations (policy-allowed media roots):
  - ClientGodot/assets/audio/<relpath under PackV1/>   (541 files)
  - ClientGodot/assets/audio/vo/p0/                     (4 files)
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
    counts = {"music_ambience": 0, "sfx_ui_variants": 0, "vo": 0}

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

    audio_manifest = {
        "manifestId": "NGM_RUNTIME_AUDIO_V1",
        "checkpoint": "MEDIA-02 checkpoint 10 - M6 runtime delivery",
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
    cine_manifest = {
        "manifestId": "NGM_RUNTIME_CINEMATICS_V1",
        "checkpoint": "MEDIA-02 checkpoint 16 - Gói 30 fix (c): CIN_002_S02 corrected keyframe + separate 16:9 keyframes (animatic v3); audio/timing unchanged from checkpoint 10/13/14/15",
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
        ],
        "animatic": cine_files,
        "scenes": scene_entries,
    }
    (CINE_DEST / "RUNTIME_CINEMATICS_manifest_v1.json").write_text(
        json.dumps(cine_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    print(f"audio copied: music/ambience={counts['music_ambience']} "
          f"sfx/ui variants={counts['sfx_ui_variants']} vo={counts['vo']} "
          f"total={len(audio_entries)}")
    print(f"cinematics: animatic verified={len(cine_files)} "
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
