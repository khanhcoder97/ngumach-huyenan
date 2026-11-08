#!/usr/bin/env python3
"""MEDIA-02 checkpoint 09 (M7/V4): cross-validate every delivered pack against
real bytes on disk. This tool does NOT re-measure loudness (checkpoints 02/04/
07/08 already measured it from real bytes); it verifies that the files the
packs describe are still the same bytes: existence, LFS-pointer detection,
size, sha256, and ffprobe codec/sample-rate/channels/duration. Timing JSONs
are cross-checked against their SRT files (UTF-8 strict + NFC + cue text and
window equality), and the P0 animatic + P0/campaign VO drafts are probed.

Usage: python3 validate_media_deliveries.py [--out <json>]
Exit code 0 = no mismatches; 1 = at least one mismatch (details in JSON).
Only reads the repo tree; writes only the JSON report passed via --out.
"""
import argparse
import hashlib
import json
import math
import re
import struct
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ERRORS = []
NOTES = []
COUNTS = {}


def err(msg):
    ERRORS.append(msg)


def note(msg):
    NOTES.append(msg)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path):
    try:
        with open(path, "rb") as f:
            return f.read(40).startswith(b"version https://git-lfs")
    except OSError:
        return False


def probe(path):
    """ffprobe first stream + format duration; returns dict or None."""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", str(path)],
            text=True, timeout=120)
    except Exception as exc:
        err(f"ffprobe failed for {path}: {exc}")
        return None
    data = json.loads(out)
    streams = data.get("streams") or []
    if not streams:
        err(f"ffprobe found no stream in {path}")
        return None
    s = streams[0]
    dur = None
    try:
        dur = float(s.get("duration") or data["format"]["duration"])
    except Exception:
        pass
    return {
        "codec": s.get("codec_name"),
        "sample_rate": int(s["sample_rate"]) if s.get("sample_rate") else None,
        "channels": s.get("channels"),
        "width": s.get("width"),
        "height": s.get("height"),
        "avg_frame_rate": s.get("avg_frame_rate"),
        "duration": dur,
    }


def check_audio_file(entry, label):
    """Validate one pack entry dict with path/sha256/size_bytes/duration_s."""
    path = ROOT / entry["path"]
    if not path.exists():
        err(f"{label}: MISSING {entry['path']}")
        return
    if is_lfs_pointer(path):
        err(f"{label}: LFS POINTER, not real bytes: {entry['path']}")
        return
    size = path.stat().st_size
    if "size_bytes" in entry and size != entry["size_bytes"]:
        err(f"{label}: size {size} != pack {entry['size_bytes']}: {entry['path']}")
    digest = sha256_of(path)
    if digest != entry["sha256"]:
        err(f"{label}: sha256 mismatch: {entry['path']}")
    p = probe(path)
    if p is None:
        return
    if p["codec"] != entry["codec"]:
        err(f"{label}: codec {p['codec']} != pack {entry['codec']}: {entry['path']}")
    if p["sample_rate"] != entry["sample_rate_hz"]:
        err(f"{label}: sample_rate {p['sample_rate']} != pack {entry['sample_rate_hz']}: {entry['path']}")
    if p["channels"] != entry["channels"]:
        err(f"{label}: channels {p['channels']} != pack {entry['channels']}: {entry['path']}")
    if p["duration"] is not None and abs(p["duration"] - entry["duration_s"]) > 0.02:
        err(f"{label}: duration {p['duration']:.4f} != pack {entry['duration_s']}: {entry['path']}")


def check_audio_packs():
    total = 0
    music = json.loads((ROOT / "Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json").read_text(encoding="utf-8"))
    for cue in music["cues"]:
        for side in ("runtime", "master"):
            check_audio_file(cue[side], f"MUSIC_AMBIENCE {cue['cueKey']}/{side}")
            total += 1
    sfx = json.loads((ROOT / "Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json").read_text(encoding="utf-8"))
    for cue in sfx["cues"]:
        for variant in cue["variants"]:
            for side in ("runtime", "master"):
                check_audio_file(variant[side], f"SFX_UI {cue['cueKey']}/{variant['variantId']}/{side}")
                total += 1
    stems = json.loads((ROOT / "Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_02_P0_STEMS_20261105.json").read_text(encoding="utf-8"))
    stem_keys = set()
    for stem in stems["stems"]:
        check_audio_file(stem, f"P0_STEM {stem['cue']}")
        stem_keys.add(stem["cue"])
        total += 1
    COUNTS["audio_files_checked"] = total
    COUNTS["audio_music_ambience_cues"] = len(music["cues"])
    COUNTS["audio_sfx_ui_cues"] = len(sfx["cues"])
    COUNTS["p0_stem_pool_files"] = len(stems["stems"])
    note(f"P0 stem pool cues validated as files: {sorted(stem_keys)}")


def check_composed_pack():
    """Checkpoint 26: the ORIGINAL composed pack (Goi 30 item 7).
    Entries use camelCase in the delivery manifest; reshape them to
    the check_audio_file contract. Provenance must stay explicit:
    composed cues are new audio, ported PackV1 files are not."""
    pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                       / "MUSIC_COMPOSED_pack_v1.json").read_text(
                           encoding="utf-8"))
    if pack["counts"] != {"music": 9, "cinemaStingers": 4, "total": 13}:
        err(f"COMPOSED pack counts drift: {pack['counts']}")
    total = 0
    for cue in pack["cues"]:
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"COMPOSED {cue['cueKey']}: provenance missing/drift")
        for side_name in ("master", "runtime"):
            side = cue[side_name]
            entry = {"path": side["path"], "sha256": side["sha256"],
                     "size_bytes": side["sizeBytes"],
                     "codec": side["codec"],
                     "sample_rate_hz": side["sampleRateHz"],
                     "channels": side["channels"],
                     "duration_s": side["durationSeconds"]}
            check_audio_file(entry, f"COMPOSED {cue['cueKey']}/"
                             f"{side_name}")
            total += 1
        if cue["kind"] == "MUSIC" and not cue.get("loop"):
            err(f"COMPOSED {cue['cueKey']}: music cue must loop")
    COUNTS["audio_composed_cues"] = len(pack["cues"])
    COUNTS["audio_files_checked"] += total
    note(f"composed pack validated: {len(pack['cues'])} cues "
         f"(9 music + 4 cinema stingers), {total} files")


def check_composed_ambience_pack():
    """Checkpoint 30: the ORIGINAL composed ambience pack (all 13
    AMBIENCE/* cues). Same contract as check_composed_pack: provenance
    must stay explicit, every cue loops, both sides byte-checked."""
    pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                       / "AMBIENCE_COMPOSED_pack_v1.json").read_text(
                           encoding="utf-8"))
    if pack["counts"] != {"ambience": 13, "total": 13}:
        err(f"COMPOSED AMBIENCE pack counts drift: {pack['counts']}")
    total = 0
    for cue in pack["cues"]:
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"COMPOSED AMBIENCE {cue['cueKey']}: provenance "
                f"missing/drift")
        if cue.get("kind") != "AMBIENCE":
            err(f"COMPOSED AMBIENCE {cue['cueKey']}: kind drift "
                f"{cue.get('kind')}")
        for side_name in ("master", "runtime"):
            side = cue[side_name]
            entry = {"path": side["path"], "sha256": side["sha256"],
                     "size_bytes": side["sizeBytes"],
                     "codec": side["codec"],
                     "sample_rate_hz": side["sampleRateHz"],
                     "channels": side["channels"],
                     "duration_s": side["durationSeconds"]}
            check_audio_file(entry, f"COMPOSED AMBIENCE {cue['cueKey']}/"
                             f"{side_name}")
            total += 1
        if not cue.get("loop"):
            err(f"COMPOSED AMBIENCE {cue['cueKey']}: ambience cue must "
                f"loop")
        if abs(cue["master"]["durationSeconds"] - 16.0) > 0.05:
            err(f"COMPOSED AMBIENCE {cue['cueKey']}: duration "
                f"{cue['master']['durationSeconds']} != 16.0 s")
    COUNTS["audio_composed_ambience_cues"] = len(pack["cues"])
    COUNTS["audio_files_checked"] += total
    note(f"composed ambience pack validated: {len(pack['cues'])} cues, "
         f"{total} files")


def check_composed_score_md1_pack():
    """WO37 M-D checkpoint 1: the MD1 score pack (7 missing core cues
    + 3 transition bridges). Same contract as check_composed_pack:
    provenance must stay explicit, every cue byte-checked on both
    sides, music cues loop, transitions are 6.0 s one-shots. The
    coverage matrix must show all 15 M-D slots covered."""
    pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                       / "MUSIC_SCORE_MD1_pack_v1.json").read_text(
                           encoding="utf-8"))
    if pack["counts"] != {"music": 7, "transitions": 3, "total": 10}:
        err(f"COMPOSED MD1 pack counts drift: {pack['counts']}")
    total = 0
    for cue in pack["cues"]:
        if cue.get("provenance") != "ORIGINAL_COMPOSED_BY_MUSE":
            err(f"COMPOSED MD1 {cue['cueKey']}: provenance missing/drift")
        for side_name in ("master", "runtime"):
            side = cue[side_name]
            entry = {"path": side["path"], "sha256": side["sha256"],
                     "size_bytes": side["sizeBytes"],
                     "codec": side["codec"],
                     "sample_rate_hz": side["sampleRateHz"],
                     "channels": side["channels"],
                     "duration_s": side["durationSeconds"]}
            check_audio_file(entry, f"COMPOSED MD1 {cue['cueKey']}/"
                             f"{side_name}")
            total += 1
        if cue["kind"] == "MUSIC" and not cue.get("loop"):
            err(f"COMPOSED MD1 {cue['cueKey']}: music cue must loop")
        if cue["kind"] == "TRANSITION":
            if cue.get("loop"):
                err(f"COMPOSED MD1 {cue['cueKey']}: transition must "
                    "not loop")
            if abs(cue["master"]["durationSeconds"] - 6.0) > 0.02:
                err(f"COMPOSED MD1 {cue['cueKey']}: transition "
                    f"duration {cue['master']['durationSeconds']} "
                    "!= 6.0 s")
    cov = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                      / "MUSIC_SCORE_MD_COVERAGE_v1.json").read_text(
                          encoding="utf-8"))
    if cov["slotsTotal"] != 15 or cov["slotsCoveredComposed"] != 15 \
            or cov["slotsGap"] != 0:
        err(f"COMPOSED MD1 coverage drift: {cov['slotsTotal']} slots, "
            f"{cov['slotsCoveredComposed']} covered, "
            f"{cov['slotsGap']} gaps")
    for slot in cov["slots"]:
        if slot["status"] != "COVERED_COMPOSED":
            err(f"COMPOSED MD1 coverage slot {slot['slot']}: status "
                f"{slot['status']}")
    COUNTS["audio_composed_score_md1_cues"] = len(pack["cues"])
    COUNTS["audio_files_checked"] += total
    note(f"composed MD1 score pack validated: {len(pack['cues'])} cues "
         f"(7 music + 3 transitions), {total} files; M-D coverage "
         f"15/15 slots, 0 gaps")


def parse_srt(text):
    cues = []
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text.strip()) if b.strip()]
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            return None
        m = re.match(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)$", lines[1].strip())
        if not m:
            return None
        g = [int(x) for x in m.groups()]
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        cues.append({"start": start, "end": end, "text": "\n".join(lines[2:]).strip()})
    return cues


def check_timing_srt():
    scenes = 0
    dialogues = 0
    srt_cues = 0
    base = ROOT / "Implementation/Content/Narrative/Deliveries"
    for scene_dir in sorted(base.glob("CIN_*")):
        if scene_dir.name == "CIN_000":
            # Checkpoint 27: the prologue is a standalone film with
            # narration-driven variable shot lengths and crossfade
            # overlaps; it does not follow the campaign pack's
            # uniform 6 s shot contract. check_prologue() verifies
            # it against its own contract.
            continue
        timing_path = scene_dir / f"{scene_dir.name}_timing_v1.json"
        if not timing_path.exists():
            err(f"TIMING: missing {timing_path.relative_to(ROOT)}")
            continue
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        scenes += 1
        shots = timing["shots"]
        cursor = 0.0
        expected = []
        for shot in shots:
            if abs(shot["startSeconds"] - cursor) > 1e-9:
                err(f"TIMING {scene_dir.name}: shot {shot['shotId']} starts {shot['startSeconds']}, expected {cursor}")
            if abs((shot["endSeconds"] - shot["startSeconds"]) - 6.0) > 1e-9:
                err(f"TIMING {scene_dir.name}: shot {shot['shotId']} is not 6s")
            cursor = shot["endSeconds"]
            dlg = shot.get("dialogue")
            if dlg:
                expected.append(dlg)
                if not (shot["startSeconds"] - 1e-9 <= dlg["windowSeconds"][0] and dlg["windowSeconds"][1] <= shot["endSeconds"] + 1e-9):
                    err(f"TIMING {scene_dir.name}: dialogue window {dlg['windowSeconds']} outside shot {shot['shotId']}")
        if abs(cursor - timing["durationSeconds"]) > 1e-9:
            err(f"TIMING {scene_dir.name}: shots end {cursor}, durationSeconds {timing['durationSeconds']}")
        srt_path = scene_dir / f"{scene_dir.name}_vi.srt"
        if not srt_path.exists():
            if expected:
                err(f"SRT {scene_dir.name}: missing SRT but timing has {len(expected)} dialogue(s)")
            else:
                note(f"SRT {scene_dir.name}: no SRT file and no dialogue in timing")
            continue
        raw = srt_path.read_bytes()
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            err(f"SRT {scene_dir.name}: not strict UTF-8: {exc}")
            continue
        if unicodedata.normalize("NFC", text) != text:
            err(f"SRT {scene_dir.name}: not NFC-normalized")
        cues = parse_srt(text)
        if cues is None:
            err(f"SRT {scene_dir.name}: unparseable SRT")
            continue
        dialogues += len(expected)
        srt_cues += len(cues)
        if len(cues) != len(expected):
            err(f"SRT {scene_dir.name}: {len(cues)} cues != {len(expected)} dialogues in timing")
            continue
        for cue, dlg in zip(cues, expected):
            if abs(cue["start"] - dlg["windowSeconds"][0]) > 0.001 or abs(cue["end"] - dlg["windowSeconds"][1]) > 0.001:
                err(f"SRT {scene_dir.name}: cue window {cue['start']}-{cue['end']} != timing {dlg['windowSeconds']}")
            if cue["text"] != dlg["text"]:
                err(f"SRT {scene_dir.name}: cue text differs from timing dialogue text")
    COUNTS["timing_scenes_checked"] = scenes
    COUNTS["timing_dialogues"] = dialogues
    COUNTS["srt_cues"] = srt_cues


def check_runtime_cine_manifest():
    """Cross-manifest equality for dialogue cues (Gói 30 item 1 / PR119
    review finding 1): the runtime cinematics manifest's dialogueCues
    must equal, per scene, the timing JSON's shots[].dialogue count, the
    parsed SRT cue count, and the source manifest's "cues" length where
    that key exists. P0 + CIN_006 source manifests carry no "cues" key;
    their counts come from timing/SRT only."""
    runtime = json.loads((ROOT / "ClientGodot/assets/cinematics"
                          / "RUNTIME_CINEMATICS_manifest_v1.json")
                         .read_text(encoding="utf-8"))
    base = ROOT / "Implementation/Content/Narrative/Deliveries"
    source_cues = {}
    for name in ("P0_timing_manifest_v1.json",
                 "CAMPAIGN_timing_manifest_v1.json"):
        manifest = json.loads((base / name).read_text(encoding="utf-8"))
        for s in manifest["scenes"]:
            if "cues" in s:
                source_cues[s["sceneId"]] = len(s["cues"])
    c6 = json.loads((base / "CIN_006/CIN_006_timing_manifest_v1.json")
                    .read_text(encoding="utf-8"))
    if "cues" in c6["scene"]:
        source_cues[c6["scene"]["sceneId"]] = len(c6["scene"]["cues"])
    scenes = 0
    total = 0
    for entry in runtime["scenes"]:
        sid = entry["sceneId"]
        scenes += 1
        timing = json.loads((base / sid / f"{sid}_timing_v1.json")
                            .read_text(encoding="utf-8"))
        timing_dialogues = sum(
            1 for sh in timing.get("shots", [])
            if isinstance(sh.get("dialogue"), dict))
        srt_path = base / sid / f"{sid}_vi.srt"
        cues = parse_srt(srt_path.read_text(encoding="utf-8"))
        if cues is None:
            err(f"RUNTIME-CUES {sid}: unparseable source SRT")
            continue
        srt_cues = len(cues)
        got = entry.get("dialogueCues")
        if got != timing_dialogues:
            err(f"RUNTIME-CUES {sid}: runtime dialogueCues {got} "
                f"!= timing dialogues {timing_dialogues}")
        if got != srt_cues:
            err(f"RUNTIME-CUES {sid}: runtime dialogueCues {got} "
                f"!= SRT cues {srt_cues}")
        if sid in source_cues and source_cues[sid] != timing_dialogues:
            err(f"RUNTIME-CUES {sid}: source manifest cues "
                f"{source_cues[sid]} != timing dialogues "
                f"{timing_dialogues}")
        total += timing_dialogues
    totals = runtime.get("campaignTotals", {})
    if totals.get("dialogueCues") != total:
        err(f"RUNTIME-CUES: campaignTotals.dialogueCues "
            f"{totals.get('dialogueCues')} != derived total {total}")
    COUNTS["runtime_cine_scenes_checked"] = scenes
    COUNTS["runtime_dialogue_cues_total"] = total
    note(f"Runtime cinematics dialogue cues cross-checked: {scenes} "
         f"scenes, {total} cues (timing == SRT == runtime manifest)")


def png_dims(path):
    with open(path, "rb") as f:
        head = f.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    w, h = struct.unpack(">II", head[16:24])
    return (w, h)


def check_animatic_vo():
    cine = ROOT / "ClientGodot/assets/cinematics"
    for name, codec_want in (("P0_animatic_640x360_30fps.mp4", "h264"),
                             ("P0_animatic_640x360_30fps.ogv", "theora")):
        path = cine / name
        if not path.exists():
            err(f"ANIMATIC: missing {path.relative_to(ROOT)}")
            continue
        p = probe(path)
        if p is None:
            continue
        if p["codec"] != codec_want:
            err(f"ANIMATIC {name}: codec {p['codec']} != {codec_want}")
        if (p["width"], p["height"]) != (640, 360):
            err(f"ANIMATIC {name}: size {p['width']}x{p['height']} != 640x360")
        if p["duration"] is None or abs(p["duration"] - 72.0) > 0.5:
            err(f"ANIMATIC {name}: duration {p['duration']} != 72.0")
        if p["avg_frame_rate"] not in ("30/1", "30"):
            note(f"ANIMATIC {name}: avg_frame_rate {p['avg_frame_rate']} (expected 30/1)")
    poster = cine / "P0_animatic_poster.png"
    if poster.exists():
        dims = png_dims(poster)
        if dims != (640, 360):
            err(f"ANIMATIC poster dims {dims} != (640, 360)")
    else:
        err("ANIMATIC: missing poster in ClientGodot/assets/cinematics")
    outputs = json.loads((ROOT / "Art_Source/Cinematics/P0_Animatic/P0_animatic_outputs_v3.json").read_text(encoding="utf-8"))
    panels_ok = 0
    for shot in outputs["shots"]:
        panel = ROOT / shot["panel"]
        if not panel.exists():
            err(f"ANIMATIC panel missing: {shot['panel']}")
            continue
        if sha256_of(panel) != shot["panelSha256"]:
            err(f"ANIMATIC panel sha mismatch: {shot['panel']}")
        if png_dims(panel) != (640, 360):
            err(f"ANIMATIC panel dims != 640x360: {shot['panel']}")
        panels_ok += 1
    COUNTS["animatic_panels_checked"] = panels_ok
    COUNTS["animatic_panels_listed"] = len(outputs["shots"])

    vo_dir = ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
    manifest = json.loads((vo_dir / "P0_VO_manifest_v1.json").read_text(encoding="utf-8"))
    for take in manifest["takes"]:
        wav = vo_dir / take["wav"]
        if not wav.exists():
            err(f"VO {take['key']}: missing {take['wav']}")
            continue
        if sha256_of(wav) != take["wavSha256"]:
            err(f"VO {take['key']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - take["durationSeconds"]) > 0.02:
            err(f"VO {take['key']}: duration {p['duration']} != manifest {take['durationSeconds']}")
        if take["durationSeconds"] > take["windowSeconds"] + 1e-9:
            err(f"VO {take['key']}: take longer than its window")
    timeline = vo_dir / "P0_VO_timeline_draft_v1.wav"
    if timeline.exists():
        p = probe(timeline)
        if p and abs(p["duration"] - 72.0) > 0.1:
            err(f"VO timeline duration {p['duration']} != 72.0")
    else:
        err("VO: missing P0_VO_timeline_draft_v1.wav")
    COUNTS["vo_takes_checked"] = len(manifest["takes"])


def check_keyframes():
    """Checkpoint 16: separate 16:9 keyframes, one per P0 shot.

    Verifies the keyframes manifest: 12 entries, each file exists,
    is 640x360, is real image bytes (not an LFS pointer), and matches
    the recorded SHA. Cross-checks the keyframe list against the
    animatic outputs manifest (same 12 shot IDs).
    """
    manifest_path = (ROOT / "Art_Source/Cinematics/P0_Animatic"
                     / "P0_keyframes_16x9_manifest_v1.json")
    if not manifest_path.exists():
        err("KEYFRAMES: missing P0_keyframes_16x9_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs = json.loads((ROOT / "Art_Source/Cinematics/P0_Animatic"
                          / "P0_animatic_outputs_v3.json").read_text(encoding="utf-8"))
    output_ids = {s["shotId"] for s in outputs["shots"]}
    checked = 0
    for entry in manifest["shots"]:
        sid = entry["shotId"]
        if sid not in output_ids:
            err(f"KEYFRAMES {sid}: not in animatic outputs manifest")
            continue
        kf = ROOT / entry["file"]
        if not kf.exists():
            err(f"KEYFRAMES {sid}: missing {entry['file']}")
            continue
        if is_lfs_pointer(kf):
            err(f"KEYFRAMES {sid}: file is an LFS pointer, not image bytes")
            continue
        if png_dims(kf) != (640, 360):
            err(f"KEYFRAMES {sid}: dims {png_dims(kf)} != 640x360")
        if sha256_of(kf) != entry["sha256"]:
            err(f"KEYFRAMES {sid}: sha mismatch")
        if entry.get("source") not in ("generated-16x9-checkpoint-16",
                                        "panel-16x9-checkpoint-13",
                                        "panel-sheet-crop-v1"):
            err(f"KEYFRAMES {sid}: unknown source {entry.get('source')!r}")
        checked += 1
    if checked != 12:
        err(f"KEYFRAMES: {checked}/12 keyframes checked")
    if {s["shotId"] for s in manifest["shots"]} != output_ids:
        err("KEYFRAMES: keyframe shot set != animatic shot set")
    COUNTS["keyframes_checked"] = checked
    note(f"Keyframes 16:9 checked: {checked}/12 (S02 generated checkpoint 16; "
         f"4 checkpoint-13 panels; 7 v1 sheet crops re-verified for framing)")


def check_cin005_keyframes():
    """Checkpoint 21: CIN_005 storyboard keyframes (3, one per shot).

    Verifies the keyframe manifest: 3 entries, each file exists under
    Art_Source/Cinematics/Campaign/CIN_005/, is 640x360, is real image
    bytes (not an LFS pointer), and matches the recorded SHA. Provenance
    is tied back to the staged generation: the staging WebP must still
    exist at its recorded path with the recorded SHA, and each entry
    must carry framing + known-defects notes. Shot IDs are cross-checked
    against the CIN_005 timing JSON.
    """
    manifest_path = (ROOT / "Art_Source/Cinematics/Campaign/CIN_005"
                     / "CIN005_keyframes_manifest_v1.json")
    if not manifest_path.exists():
        err("CIN005-KEYFRAMES: missing CIN005_keyframes_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    timing = json.loads((ROOT / "Implementation/Content/Narrative"
                         / "Deliveries/CIN_005/CIN_005_timing_v1.json")
                        .read_text(encoding="utf-8"))
    timing_ids = {s["shotId"] for s in timing.get("shots", [])}
    staging_root = Path("/home/hatch/workspace/goals"
                        "/ng-m-ch-continuous-development/hidden_files"
                        "/cin005_keyframes_staging")
    checked = 0
    for entry in manifest.get("keyframes", []):
        sid = entry["shotId"]
        if sid not in timing_ids:
            err(f"CIN005-KEYFRAMES {sid}: not in CIN_005 timing shots")
            continue
        kf = ROOT / "Art_Source/Cinematics/Campaign/CIN_005" / entry["file"]
        if not kf.exists():
            err(f"CIN005-KEYFRAMES {sid}: missing {entry['file']}")
            continue
        if is_lfs_pointer(kf):
            err(f"CIN005-KEYFRAMES {sid}: file is an LFS pointer")
            continue
        if png_dims(kf) != (640, 360):
            err(f"CIN005-KEYFRAMES {sid}: dims {png_dims(kf)} != 640x360")
        if sha256_of(kf) != entry["sha256"]:
            err(f"CIN005-KEYFRAMES {sid}: sha mismatch")
        staged = staging_root / entry["sourceStagingFile"]
        if not staged.exists():
            err(f"CIN005-KEYFRAMES {sid}: staging source missing "
                f"{entry['sourceStagingFile']}")
        elif sha256_of(staged) != entry["sourceStagingSha256"]:
            err(f"CIN005-KEYFRAMES {sid}: staging source sha mismatch")
        if not entry.get("framing"):
            err(f"CIN005-KEYFRAMES {sid}: no framing note")
        if not entry.get("knownDefects"):
            err(f"CIN005-KEYFRAMES {sid}: no known-defects note")
        checked += 1
    if checked != 3:
        err(f"CIN005-KEYFRAMES: {checked}/3 keyframes checked")
    if {e["shotId"] for e in manifest.get("keyframes", [])} != timing_ids:
        err("CIN005-KEYFRAMES: keyframe shot set != timing shot set")
    if manifest.get("status") != "STORYBOARD":
        err(f"CIN005-KEYFRAMES: status {manifest.get('status')!r} "
            f"!= STORYBOARD")
    COUNTS["cin005_keyframes_checked"] = checked
    note(f"CIN_005 keyframes checked: {checked}/3 (storyboard level, "
         f"staging SHA-verified)")


WINDOW_FIT_OVERRUNS = []


def check_campaign_vo():
    """Checkpoint 17: campaign VO drafts (17 takes + 378 s timeline).

    Byte-level checks are strict (existence, SHA, duration, 48 kHz mono
    pcm_s16le, take text char-exact in the scene SRT). Window fit is
    reported as a finding, NOT a byte mismatch: D1 forbids speeding the
    voice up to fit, so an OVERRUN take is delivered unchanged and its
    window/line decision belongs to the director. Overruns are listed in
    WINDOW_FIT_OVERRUNS and in the result's windowFit section.
    """
    vo_dir = ROOT / "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT"
    manifest_path = vo_dir / "CAMPAIGN_VO_manifest_v1.json"
    if not manifest_path.exists():
        err("CAMPAIGN VO: missing CAMPAIGN_VO_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    takes = manifest.get("takes", [])
    if len(takes) != 17:
        err(f"CAMPAIGN VO: {len(takes)}/17 takes in manifest")
    checked = 0
    fits = 0
    for take in takes:
        wav = vo_dir / take["wav"]
        if not wav.exists():
            err(f"CAMPAIGN VO {take['key']}: missing {take['wav']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CAMPAIGN VO {take['key']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != take["wavSha256"]:
            err(f"CAMPAIGN VO {take['key']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - take["durationSeconds"]) > 0.02:
            err(f"CAMPAIGN VO {take['key']}: duration {p['duration']} "
                f"!= manifest {take['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 1):
                err(f"CAMPAIGN VO {take['key']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/1")
        # Text char-exact in the scene SRT (independent re-check).
        srt_path = (ROOT / "Implementation/Content/Narrative/Deliveries"
                    / take["sceneId"] / f"{take['sceneId']}_vi.srt")
        srt = unicodedata.normalize(
            "NFC", srt_path.read_text(encoding="utf-8"))
        if unicodedata.normalize("NFC", take["text"]) not in srt:
            err(f"CAMPAIGN VO {take['key']}: text not in scene SRT")
        if take["fit"] == "FITS":
            fits += 1
        else:
            WINDOW_FIT_OVERRUNS.append(
                {"shotId": take["shotId"],
                 "slackSeconds": take["slackSeconds"]})
        checked += 1
    timeline = vo_dir / "CAMPAIGN_VO_timeline_draft_v1.wav"
    if timeline.exists():
        if is_lfs_pointer(timeline):
            err("CAMPAIGN VO: timeline is an LFS pointer")
        p = probe(timeline)
        if p and abs(p["duration"] - 378.0) > 0.1:
            err(f"CAMPAIGN VO timeline duration {p['duration']} != 378.0")
    else:
        err("CAMPAIGN VO: missing CAMPAIGN_VO_timeline_draft_v1.wav")
    COUNTS["vo_campaign_takes_checked"] = checked
    COUNTS["vo_campaign_fits"] = fits
    COUNTS["vo_campaign_overruns"] = len(WINDOW_FIT_OVERRUNS)
    note(f"Campaign VO checked: {checked}/17 takes, {fits} FITS, "
         f"{len(WINDOW_FIT_OVERRUNS)} OVERRUN "
         f"({[o['shotId'] for o in WINDOW_FIT_OVERRUNS] or 'none'}); "
         f"overruns are director findings (D1: no voice speed-up to fit), "
         f"not byte mismatches")


def check_cin006_keyframes():
    """Checkpoint 22: CIN_006 storyboard keyframes (3, one per shot).

    Verifies the keyframe manifest: 3 entries, each file exists under
    Art_Source/Cinematics/Campaign/CIN_006/, is 640x360, is real image
    bytes (not an LFS pointer), and matches the recorded SHA. Provenance
    is tied back to the staged generation: the staging WebP must still
    exist at its recorded path with the recorded SHA, and each entry
    must carry framing + known-defects notes. Shot IDs are cross-checked
    against the CIN_006 timing JSON.
    """
    manifest_path = (ROOT / "Art_Source/Cinematics/Campaign/CIN_006"
                     / "CIN006_keyframes_manifest_v1.json")
    if not manifest_path.exists():
        err("CIN006-KEYFRAMES: missing CIN006_keyframes_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    timing = json.loads((ROOT / "Implementation/Content/Narrative"
                         / "Deliveries/CIN_006/CIN_006_timing_v1.json")
                        .read_text(encoding="utf-8"))
    timing_ids = {s["shotId"] for s in timing.get("shots", [])}
    staging_root = Path("/home/hatch/workspace/goals"
                        "/ng-m-ch-continuous-development/hidden_files"
                        "/cin006_keyframes_staging")
    checked = 0
    for entry in manifest.get("keyframes", []):
        sid = entry["shotId"]
        if sid not in timing_ids:
            err(f"CIN006-KEYFRAMES {sid}: not in CIN_006 timing shots")
            continue
        kf = ROOT / "Art_Source/Cinematics/Campaign/CIN_006" / entry["file"]
        if not kf.exists():
            err(f"CIN006-KEYFRAMES {sid}: missing {entry['file']}")
            continue
        if is_lfs_pointer(kf):
            err(f"CIN006-KEYFRAMES {sid}: file is an LFS pointer")
            continue
        if png_dims(kf) != (640, 360):
            err(f"CIN006-KEYFRAMES {sid}: dims {png_dims(kf)} != 640x360")
        if sha256_of(kf) != entry["sha256"]:
            err(f"CIN006-KEYFRAMES {sid}: sha mismatch")
        staged = staging_root / entry["sourceStagingFile"]
        if not staged.exists():
            err(f"CIN006-KEYFRAMES {sid}: staging source missing "
                f"{entry['sourceStagingFile']}")
        elif sha256_of(staged) != entry["sourceStagingSha256"]:
            err(f"CIN006-KEYFRAMES {sid}: staging source sha mismatch")
        if not entry.get("framing"):
            err(f"CIN006-KEYFRAMES {sid}: no framing note")
        if not entry.get("knownDefects"):
            err(f"CIN006-KEYFRAMES {sid}: no known-defects note")
        checked += 1
    if checked != 3:
        err(f"CIN006-KEYFRAMES: {checked}/3 keyframes checked")
    if {e["shotId"] for e in manifest.get("keyframes", [])} != timing_ids:
        err("CIN006-KEYFRAMES: keyframe shot set != timing shot set")
    if manifest.get("status") != "STORYBOARD":
        err(f"CIN006-KEYFRAMES: status {manifest.get('status')!r} "
            f"!= STORYBOARD")
    COUNTS["cin006_keyframes_checked"] = checked
    note(f"CIN_006 keyframes checked: {checked}/3 (storyboard level, "
         f"staging SHA-verified)")


def check_cin009_keyframes():
    """Checkpoint 23: CIN_009 storyboard keyframes (3, one per shot).

    Verifies the keyframe manifest: 3 entries, each file exists under
    Art_Source/Cinematics/Campaign/CIN_009/, is 640x360, is real image
    bytes (not an LFS pointer), and matches the recorded SHA. Provenance
    is tied back to the staged generation: the staging WebP must still
    exist at its recorded path with the recorded SHA, and each entry
    must carry framing + known-defects notes. Shot IDs are cross-checked
    against the CIN_009 timing JSON. CIN_009 has an empty pack
    character list, so no character lock is involved; the S02 workers
    are unnamed generation-invented figures.
    """
    manifest_path = (ROOT / "Art_Source/Cinematics/Campaign/CIN_009"
                     / "CIN009_keyframes_manifest_v1.json")
    if not manifest_path.exists():
        err("CIN009-KEYFRAMES: missing CIN009_keyframes_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    timing = json.loads((ROOT / "Implementation/Content/Narrative"
                         / "Deliveries/CIN_009/CIN_009_timing_v1.json")
                        .read_text(encoding="utf-8"))
    timing_ids = {s["shotId"] for s in timing.get("shots", [])}
    staging_root = Path("/home/hatch/workspace/goals"
                        "/ng-m-ch-continuous-development/hidden_files"
                        "/cin009_keyframes_staging")
    checked = 0
    for entry in manifest.get("keyframes", []):
        sid = entry["shotId"]
        if sid not in timing_ids:
            err(f"CIN009-KEYFRAMES {sid}: not in CIN_009 timing shots")
            continue
        kf = ROOT / "Art_Source/Cinematics/Campaign/CIN_009" / entry["file"]
        if not kf.exists():
            err(f"CIN009-KEYFRAMES {sid}: missing {entry['file']}")
            continue
        if is_lfs_pointer(kf):
            err(f"CIN009-KEYFRAMES {sid}: file is an LFS pointer")
            continue
        if png_dims(kf) != (640, 360):
            err(f"CIN009-KEYFRAMES {sid}: dims {png_dims(kf)} != 640x360")
        if sha256_of(kf) != entry["sha256"]:
            err(f"CIN009-KEYFRAMES {sid}: sha mismatch")
        staged = staging_root / entry["sourceStagingFile"]
        if not staged.exists():
            err(f"CIN009-KEYFRAMES {sid}: staging source missing "
                f"{entry['sourceStagingFile']}")
        elif sha256_of(staged) != entry["sourceStagingSha256"]:
            err(f"CIN009-KEYFRAMES {sid}: staging source sha mismatch")
        if not entry.get("framing"):
            err(f"CIN009-KEYFRAMES {sid}: no framing note")
        if not entry.get("knownDefects"):
            err(f"CIN009-KEYFRAMES {sid}: no known-defects note")
        checked += 1
    if checked != 3:
        err(f"CIN009-KEYFRAMES: {checked}/3 keyframes checked")
    if {e["shotId"] for e in manifest.get("keyframes", [])} != timing_ids:
        err("CIN009-KEYFRAMES: keyframe shot set != timing shot set")
    if manifest.get("status") != "STORYBOARD":
        err(f"CIN009-KEYFRAMES: status {manifest.get('status')!r} "
            f"!= STORYBOARD")
    COUNTS["cin009_keyframes_checked"] = checked
    note(f"CIN_009 keyframes checked: {checked}/3 (storyboard level, "
         f"staging SHA-verified)")


def check_cin006_vo():
    """Checkpoint 19: CIN_006 VO drafts (canonical + alternate take).

    Closes the 21st D1-approved dialogue window (checkpoints 04 + 17
    covered the other 20). Byte checks are strict (existence, not an
    LFS pointer, SHA, duration, 48 kHz mono pcm_s16le). The canonical
    text must be char-exact in the scene SRT; the alternate take text
    must NOT be in the SRT and must carry no window (DEC-MEDIA-P0 Q3:
    own takeId/version, never merged with canonical). Canonical window
    fit is a finding, not a byte mismatch (D1: no speed-up to fit).
    """
    vo_dir = ROOT / "Art_Source/Audio/Muse/VO/CIN006_DRAFT"
    manifest_path = vo_dir / "CIN006_VO_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN006 VO: missing CIN006_VO_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    takes = manifest.get("takes", [])
    if len(takes) != 2:
        err(f"CIN006 VO: {len(takes)}/2 takes in manifest")
    srt_path = (ROOT / "Implementation/Content/Narrative/Deliveries"
                / "CIN_006" / "CIN_006_vi.srt")
    srt = unicodedata.normalize(
        "NFC", srt_path.read_text(encoding="utf-8"))
    checked = 0
    canon_fit = None
    for take in takes:
        wav = vo_dir / take["wav"]
        if not wav.exists():
            err(f"CIN006 VO {take['key']}: missing {take['wav']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN006 VO {take['key']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != take["wavSha256"]:
            err(f"CIN006 VO {take['key']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - take["durationSeconds"]) > 0.02:
            err(f"CIN006 VO {take['key']}: duration {p['duration']} "
                f"!= manifest {take['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 1):
                err(f"CIN006 VO {take['key']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/1")
        text_nfc = unicodedata.normalize("NFC", take["text"])
        if take["takeKind"] == "CANONICAL":
            if text_nfc not in srt:
                err(f"CIN006 VO {take['key']}: canonical text not in SRT")
            canon_fit = take["fit"]
            if take["fit"] != "FITS":
                WINDOW_FIT_OVERRUNS.append(
                    {"shotId": take["shotId"],
                     "slackSeconds": take["slackSeconds"]})
        else:
            if text_nfc in srt:
                err(f"CIN006 VO {take['key']}: alt text leaked into SRT")
            if take.get("windowSceneSeconds") is not None:
                err(f"CIN006 VO {take['key']}: alt take has a window")
            if take.get("takeId") != "CIN_006_ALT_T01":
                err(f"CIN006 VO {take['key']}: bad takeId "
                    f"{take.get('takeId')}")
        checked += 1
    timeline = vo_dir / "CIN006_VO_timeline_draft_v1.wav"
    if timeline.exists():
        if is_lfs_pointer(timeline):
            err("CIN006 VO: timeline is an LFS pointer")
        p = probe(timeline)
        want = manifest.get("timeline", {}).get("durationSeconds")
        if p and want and abs(p["duration"] - want) > 0.1:
            err(f"CIN006 VO timeline duration {p['duration']} "
                f"!= manifest {want}")
    else:
        err("CIN006 VO: missing CIN006_VO_timeline_draft_v1.wav")
    COUNTS["vo_cin006_takes_checked"] = checked
    COUNTS["vo_cin006_canonical_fit"] = canon_fit
    note(f"CIN_006 VO checked: {checked}/2 takes (canonical fit "
         f"{canon_fit}); 21/21 dialogue windows now have draft VO")


def check_p0_mix():
    """Checkpoint 20: P0 draft mixes (3 scenes + 72 s review mix).

    Byte checks are strict (existence, not an LFS pointer, SHA,
    duration, 48 kHz stereo pcm_s16le). The manifest's mix evidence
    is sanity-checked as data: every scene with a ducked bus must
    show a negative in-window ducking depth and zero depth outside
    the window (sidechain keyed by VO only), and every ambience
    loop join must carry a loop-QA ratio. The mix itself is a
    DRAFT (see the manifest mixVerdict); nothing here is a mix PASS.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT"
    manifest_path = mix_dir / "P0_MIX_manifest_v1.json"
    if not manifest_path.exists():
        err("P0 MIX: missing P0_MIX_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenes = manifest.get("scenes", [])
    if len(scenes) != 3:
        err(f"P0 MIX: {len(scenes)}/3 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"P0 MIX {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"P0 MIX {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"P0 MIX {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"P0 MIX {scene['sceneId']}: duration {p['duration']} "
                f"!= manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"P0 MIX {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"P0 MIX {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"P0 MIX {scene['sceneId']}: ducking depth in "
                    f"window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"P0 MIX {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"P0 MIX {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        checked += 1
    rmx = manifest.get("reviewMix", {})
    review = mix_dir / rmx.get("file", "")
    if not review.exists():
        err("P0 MIX: missing review mix wav")
    else:
        if is_lfs_pointer(review):
            err("P0 MIX: review mix is an LFS pointer")
        if sha256_of(review) != rmx["sha256"]:
            err("P0 MIX: review mix sha mismatch")
        p = probe(review)
        if p and abs(p["duration"] - 72.0) > 0.05:
            err(f"P0 MIX review duration {p['duration']} != 72.0")
        checked += 1
    COUNTS["p0_mix_files_checked"] = checked
    note(f"P0 draft mixes checked: {checked}/4 files (3 scenes + "
         f"72 s review); DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_p0_mix_v2():
    """Checkpoint 29: P0 draft mixes v2 from composed stems.

    Mirrors check_p0_mix() for MIX/P0_DRAFT_V2/ + P0_MIX_V2_manifest_
    v1.json, plus v2-specific assertions: the manifest must declare
    mixVersion v2_composed_stems, every music/stinger stem must carry
    ORIGINAL_COMPOSED_BY_MUSE provenance and every ambience stem the
    ported PackV1 provenance, and the v1 mix directory must be
    untouched (its SHAs are NOT re-checked here -- v1 was verified at
    checkpoint 20 and its files are byte-identical by the delivery
    builder's copy-verify; the runtime verifier checks both sets).
    The mix itself is a DRAFT (see the manifest mixVerdict); nothing
    here is a mix PASS.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2"
    manifest_path = mix_dir / "P0_MIX_V2_manifest_v1.json"
    if not manifest_path.exists():
        err("P0 MIX V2: missing P0_MIX_V2_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v2_composed_stems":
        err(f"P0 MIX V2: mixVersion "
            f"{manifest.get('mixVersion')} != v2_composed_stems")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 3:
        err(f"P0 MIX V2: {len(scenes)}/3 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"P0 MIX V2 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"P0 MIX V2 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"P0 MIX V2 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"P0 MIX V2 {scene['sceneId']}: duration {p['duration']} "
                f"!= manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"P0 MIX V2 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"P0 MIX V2 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if st["role"] in ("music", "stinger"):
                if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                    err(f"P0 MIX V2 {scene['sceneId']}: {st['role']} stem "
                        f"{st['cue']} provenance is not composed: {prov}")
            elif st["role"] == "ambience":
                if "PORTED_CODEX_PACKV1" not in prov:
                    err(f"P0 MIX V2 {scene['sceneId']}: ambience stem "
                        f"{st['cue']} provenance is not ported: {prov}")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"P0 MIX V2 {scene['sceneId']}: ducking depth in "
                    f"window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"P0 MIX V2 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"P0 MIX V2 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        checked += 1
    rmx = manifest.get("reviewMix", {})
    review = mix_dir / rmx.get("file", "")
    if not review.exists():
        err("P0 MIX V2: missing review mix wav")
    else:
        if is_lfs_pointer(review):
            err("P0 MIX V2: review mix is an LFS pointer")
        if sha256_of(review) != rmx["sha256"]:
            err("P0 MIX V2: review mix sha mismatch")
        p = probe(review)
        if p and abs(p["duration"] - 72.0) > 0.05:
            err(f"P0 MIX V2 review duration {p['duration']} != 72.0")
        checked += 1
    COUNTS["p0_mix_v2_files_checked"] = checked
    note(f"P0 draft mixes v2 checked: {checked}/4 files (3 scenes + "
         f"72 s review, composed stems); DRAFT_MIX_NOT_FINAL, not a "
         f"mix PASS")



def check_p0_mix_v3():
    """Checkpoint 31: P0 draft mixes v3 from fully composed stems.

    Mirrors check_p0_mix_v2() for MIX/P0_DRAFT_V3/ + P0_MIX_V3_
    manifest_v1.json, plus the v3-specific assertion: EVERY stem
    (music, stinger AND ambience) must carry ORIGINAL_COMPOSED_BY_
    MUSE provenance -- no ported stem remains in the P0 mixes.
    The mix itself is a DRAFT (see the manifest mixVerdict); nothing
    here is a mix PASS.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3"
    manifest_path = mix_dir / "P0_MIX_V3_manifest_v1.json"
    if not manifest_path.exists():
        err("P0 MIX V3: missing P0_MIX_V3_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v3_fully_composed":
        err(f"P0 MIX V3: mixVersion "
            f"{manifest.get('mixVersion')} != v3_fully_composed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 3:
        err(f"P0 MIX V3: {len(scenes)}/3 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"P0 MIX V3 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"P0 MIX V3 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"P0 MIX V3 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"P0 MIX V3 {scene['sceneId']}: duration {p['duration']} "
                f"!= manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"P0 MIX V3 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"P0 MIX V3 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"P0 MIX V3 {scene['sceneId']}: {st['role']} stem "
                    f"{st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"P0 MIX V3 {scene['sceneId']}: {st['role']} stem "
                    f"{st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"P0 MIX V3 {scene['sceneId']}: ducking depth in "
                    f"window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"P0 MIX V3 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"P0 MIX V3 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        checked += 1
    rmx = manifest.get("reviewMix", {})
    review = mix_dir / rmx.get("file", "")
    if not review.exists():
        err("P0 MIX V3: missing review mix wav")
    else:
        if is_lfs_pointer(review):
            err("P0 MIX V3: review mix is an LFS pointer")
        if sha256_of(review) != rmx["sha256"]:
            err("P0 MIX V3: review mix sha mismatch")
        p = probe(review)
        if p and abs(p["duration"] - 72.0) > 0.05:
            err(f"P0 MIX V3 review duration {p['duration']} != 72.0")
        checked += 1
    COUNTS["p0_mix_v3_files_checked"] = checked
    note(f"P0 draft mixes v3 checked: {checked}/4 files (3 scenes + "
         f"72 s review, fully composed stems); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin006_mix():
    """Checkpoint 34 (Goi 31 item 4): CIN_006 draft mix v1.

    Mirrors check_p0_mix_v3() for MIX/CIN006_DRAFT_V1/ +
    CIN006_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE; the
    +0.52 s VO overrun is kept (window unchanged, 0.02 s tail trim
    at the scene edge, recorded in the manifest).
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1"
    manifest_path = mix_dir / "CIN006_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN006 MIX V1: missing CIN006_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin006_proposed":
        err(f"CIN006 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin006_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN006 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN006 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN006 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN006 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN006 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN006 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN006 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN006 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN006 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN006 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN006 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN006 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.02:
            err(f"CIN006 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.02")
        if vo.get("overrunVsWindowSeconds", 0) != 0.52:
            err(f"CIN006 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != 0.52")
        checked += 1
    COUNTS["cin006_mix_v1_files_checked"] = checked
    note(f"CIN_006 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin003_mix():
    """Checkpoint 37: CIN_003 draft mix v1.

    Mirrors check_cin006_mix() for MIX/CIN003_DRAFT_V1/ +
    CIN003_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_006, the CP17 draft VO take FITS inside its window (ends
    16.532 s, 0.968 s before the 17.5 s window end): recorded
    overrun is -0.968 and the tail trim at the scene edge is 0.0.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1"
    manifest_path = mix_dir / "CIN003_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN003 MIX V1: missing CIN003_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin003_proposed":
        err(f"CIN003 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin003_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN003 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN003 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN003 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN003 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN003 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN003 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN003 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN003 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN003 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN003 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN003 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN003 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN003 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -0.968:
            err(f"CIN003 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -0.968")
        checked += 1
    COUNTS["cin003_mix_v1_files_checked"] = checked
    note(f"CIN_003 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO fits "
         f"inside its window); DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin005_mix():
    """Checkpoint 38: CIN_005 draft mix v1.

    Mirrors check_cin003_mix() for MIX/CIN005_DRAFT_V1/ +
    CIN005_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_006, the CP17 draft VO take OVERRUNS its window by 0.160 s
    (5.160 s, 12.5-17.660 s) and the overrun is KEPT per the owner
    verdict (Goi 30 D1); the tail trim at the scene edge is 0.0.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1"
    manifest_path = mix_dir / "CIN005_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN005 MIX V1: missing CIN005_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin005_proposed":
        err(f"CIN005 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin005_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN005 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN005 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN005 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN005 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN005 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN005 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN005 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN005 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN005 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN005 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN005 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN005 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN005 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != 0.16:
            err(f"CIN005 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != 0.16")
        checked += 1
    COUNTS["cin005_mix_v1_files_checked"] = checked
    note(f"CIN_005 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO overrun "
         f"+0.160 s KEPT per owner verdict); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin007_mix():
    """Checkpoint 39: CIN_007 draft mix v1.

    Mirrors check_cin005_mix() for MIX/CIN007_DRAFT_V1/ +
    CIN007_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_005/CIN_006, the CP17 draft VO take FITS its window
    (3.912 s, 12.5-16.412 s): the recorded overrun is -1.088 and
    the tail trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window because quiet_discovery is
    sparse by design (the first 2 s of the window are near-silence
    at -91 dB mean, so a 2 s slice would show no measurable cut).
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1"
    manifest_path = mix_dir / "CIN007_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN007 MIX V1: missing CIN007_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin007_proposed":
        err(f"CIN007 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin007_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN007 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN007 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN007 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN007 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN007 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN007 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN007 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN007 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN007 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN007 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN007 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN007 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN007 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -1.088:
            err(f"CIN007 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -1.088")
        checked += 1
    COUNTS["cin007_mix_v1_files_checked"] = checked
    note(f"CIN_007 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window, ends 16.412 s); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin008_mix():
    """Checkpoint 40: CIN_008 draft mix v1.

    Mirrors check_cin005_mix() for MIX/CIN008_DRAFT_V1/ +
    CIN008_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_005/CIN_006, the CP17 draft VO take FITS its window
    (3.552 s, 12.5-16.052 s): the recorded overrun is -1.448 and
    the tail trim at the scene edge is 0.0. Ducking evidence is measured over the full VO window (the CP39 full-window method is retained so the depth is comparable across the CIN_003/CIN_005/CIN_007/CIN_008 mixes).
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1"
    manifest_path = mix_dir / "CIN008_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN008 MIX V1: missing CIN008_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin008_proposed":
        err(f"CIN008 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin008_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN008 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN008 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN008 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN008 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN008 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN008 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN008 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN008 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN008 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN008 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN008 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN008 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN008 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -1.448:
            err(f"CIN008 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -1.448")
        checked += 1
    COUNTS["cin008_mix_v1_files_checked"] = checked
    note(f"CIN_008 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window, ends 16.052 s); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin009_mix():
    """Checkpoint 41: CIN_009 draft mix v1.

    Mirrors check_cin009_mix() for MIX/CIN009_DRAFT_V1/ +
    CIN009_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_005/CIN_006, the CP17 draft VO take FITS its window
    (4.080 s, 12.5-16.580 s): the recorded overrun is -0.92 and
    the tail trim at the scene edge is 0.0. Ducking evidence is measured over the full VO window (the CP39 full-window method is retained so the depth is comparable across the CIN_003/CIN_005/CIN_007/CIN_009/CIN_009 mixes). The mix is hotter than CIN_009 (-17.84 LUFS) because the CP17 VO take itself is hot (-17.23 LUFS); VO is kept at unity per the recipe, not normalized.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1"
    manifest_path = mix_dir / "CIN009_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN009 MIX V1: missing CIN009_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin009_proposed":
        err(f"CIN009 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin009_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN009 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN009 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN009 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN009 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN009 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN009 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN009 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN009 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN009 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN009 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN009 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN009 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN009 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -0.92:
            err(f"CIN009 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -0.92")
        checked += 1
    COUNTS["cin009_mix_v1_files_checked"] = checked
    note(f"CIN_009 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window, ends 16.580 s); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin010_mix():
    """Checkpoint 42: CIN_010 draft mix v1.

    Mirrors check_cin009_mix() for MIX/CIN010_DRAFT_V1/ +
    CIN010_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_005/CIN_006, the CP17 draft VO take FITS its window
    (2.808 s, 12.5-15.308 s): the recorded overrun is -2.192 and
    the tail trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010 mixes). The mix
    measures -24.60 LUFS because the CP17 VO take itself is quiet
    (-22.01 LUFS); VO is kept at unity per the recipe, not normalized.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1"
    manifest_path = mix_dir / "CIN010_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN010 MIX V1: missing CIN010_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin010_proposed":
        err(f"CIN010 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin010_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN010 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN010 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN010 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN010 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN010 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN010 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN010 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN010 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN010 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN010 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN010 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN010 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN010 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.192:
            err(f"CIN010 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.192")
        checked += 1
    COUNTS["cin010_mix_v1_files_checked"] = checked
    note(f"CIN_010 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window, ends 15.308 s); DRAFT_MIX_NOT_FINAL, "
         f"not a mix PASS")


def check_cin011_mix():
    """Checkpoint 45: CIN_011 draft mix v1.

    Mirrors check_cin010_mix() for MIX/CIN011_DRAFT_V1/ +
    CIN011_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Unlike
    CIN_005/CIN_006, the CP17 draft VO take FITS its window -- by
    0.008 s (5.592 s, 12.2-17.792 s): the recorded overrun is -0.008
    and the tail trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011 mixes).
    The mix measures -20.34 LUFS because the CP17 VO take itself is
    quiet (-21.50 LUFS); VO is kept at unity per the recipe, not
    normalized.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V1"
    manifest_path = mix_dir / "CIN011_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN011 MIX V1: missing CIN011_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin011_proposed":
        err(f"CIN011 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin011_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN011 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN011 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN011 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN011 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN011 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN011 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN011 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN011 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN011 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN011 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN011 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN011 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN011 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -0.008:
            err(f"CIN011 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -0.008")
        checked += 1
    COUNTS["cin011_mix_v1_files_checked"] = checked
    note(f"CIN_011 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 0.008 s, ends 17.792 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin012_mix():
    """Checkpoint 46: CIN_012 draft mix v1.

    Mirrors check_cin011_mix() for MIX/CIN012_DRAFT_V1/ +
    CIN012_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011, the CP17 draft VO take
    FITS its window -- by 0.680 s (4.320 s, 12.5-16.820 s): the
    recorded overrun is -0.68 and the tail trim at the scene edge
    is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012 mixes).
    The mix measures -25.60 LUFS because the CP17 VO take itself is
    quiet (-25.38 LUFS); VO is kept at unity per the recipe, not
    normalized.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V1"
    manifest_path = mix_dir / "CIN012_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN012 MIX V1: missing CIN012_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin012_proposed":
        err(f"CIN012 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin012_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN012 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN012 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN012 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN012 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN012 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN012 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN012 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN012 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN012 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN012 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN012 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN012 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN012 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -0.68:
            err(f"CIN012 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -0.68")
        checked += 1
    COUNTS["cin012_mix_v1_files_checked"] = checked
    note(f"CIN_012 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 0.680 s, ends 16.820 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin013_mix():
    """Checkpoint 47: CIN_013 draft mix v1.

    Mirrors check_cin012_mix() for MIX/CIN013_DRAFT_V1/ +
    CIN013_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012, the CP17 draft VO take
    FITS its window -- by 2.528 s (2.472 s, 12.5-14.972 s): the
    recorded overrun is -2.528 and the tail trim at the scene edge
    is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013 mixes).
    The mix measures -25.87 LUFS because the CP17 VO take itself is
    quiet (-22.51 LUFS); VO is kept at unity per the recipe, not
    normalized.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V1"
    manifest_path = mix_dir / "CIN013_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN013 MIX V1: missing CIN013_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin013_proposed":
        err(f"CIN013 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin013_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN013 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN013 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN013 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN013 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN013 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN013 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN013 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN013 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN013 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN013 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN013 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN013 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN013 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.528:
            err(f"CIN013 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.528")
        checked += 1
    COUNTS["cin013_mix_v1_files_checked"] = checked
    note(f"CIN_013 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 2.528 s, ends 14.972 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin014_mix():
    """Checkpoint 48: CIN_014 draft mix v1.

    Mirrors check_cin013_mix() for MIX/CIN014_DRAFT_V1/ +
    CIN014_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013, the
    CP17 draft VO take FITS its window -- by 1.928 s (3.072 s,
    12.5-15.572 s): the recorded overrun is -1.928 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014 mixes).
    The mix measures -24.42 LUFS because the CP17 VO take itself is
    quiet (-22.05 LUFS); VO is kept at unity per the recipe, not
    normalized. Ducking depth -8.84 dB is deeper than CIN_013's
    -5.19 dB: same compressor params, ben_mua is louder inside the
    window than lam_trieu was -- measured evidence, not a retune.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V1"
    manifest_path = mix_dir / "CIN014_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN014 MIX V1: missing CIN014_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin014_proposed":
        err(f"CIN014 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin014_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN014 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN014 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN014 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN014 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN014 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN014 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN014 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN014 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN014 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN014 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN014 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN014 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN014 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -1.928:
            err(f"CIN014 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -1.928")
        checked += 1
    COUNTS["cin014_mix_v1_files_checked"] = checked
    note(f"CIN_014 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 1.928 s, ends 15.572 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")

def check_cin015_mix():
    """Checkpoint 49: CIN_015 draft mix v1.

    Mirrors check_cin013_mix() for MIX/CIN015_DRAFT_V1/ +
    CIN015_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014, the
    CP17 draft VO take FITS its window -- by 2.120 s (2.880 s,
    12.5-15.380 s): the recorded overrun is -2.120 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015 mixes).
    The mix measures -25.30 LUFS because the CP17 VO take itself is
    quiet (-23.27 LUFS); VO is kept at unity per the recipe, not
    normalized. Ducking depth -6.87 dB is shallower than CIN_014's
    -8.84 dB: same compressor params, bach_uyen is quieter inside the
    window than ben_mua was -- measured evidence, not a retune.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V1"
    manifest_path = mix_dir / "CIN015_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN015 MIX V1: missing CIN015_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin015_proposed":
        err(f"CIN015 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin015_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN015 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN015 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN015 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN015 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN015 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN015 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN015 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN015 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN015 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN015 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN015 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN015 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN015 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.120:
            err(f"CIN015 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.120")
        checked += 1
    COUNTS["cin015_mix_v1_files_checked"] = checked
    note(f"CIN_015 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 2.120 s, ends 15.380 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def _segment_rms_db(path, start, dur):
    """RMS (dBFS) of one audio segment, decoded to s16le mono 48 kHz.

    Returns -120.0 for digital silence. Used only by
    check_cin016_mix() to prove the 0.0 dB ducking depth is a silence
    gap in the music bed, not a missing compressor.
    """
    try:
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-ss", f"{start:.3f}",
             "-t", f"{dur:.3f}", "-i", str(path),
             "-ac", "1", "-ar", "48000", "-f", "s16le", "-"],
            timeout=120)
    except Exception as exc:
        err(f"segment RMS decode failed for {path}: {exc}")
        return None
    n = len(raw) // 2
    if n == 0:
        return -120.0
    samples = struct.unpack(f"<{n}h", raw[:n * 2])
    mean_sq = sum(s * s for s in samples) / float(n) / (32768.0 ** 2)
    if mean_sq <= 0:
        return -120.0
    return 20.0 * math.log10(math.sqrt(mean_sq))


def check_cin016_mix():
    """Checkpoint 50: CIN_016 draft mix v1.

    Mirrors check_cin015_mix() for MIX/CIN016_DRAFT_V1/ +
    CIN016_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, and loop
    joins must carry QA ratios. The mix itself is a DRAFT (see the
    manifest mixVerdict); nothing here is a mix PASS. The stem
    assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015, the
    CP17 draft VO take FITS its window -- by 2.528 s (2.472 s,
    12.5-14.972 s): the recorded overrun is -2.528 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016 mixes).
    The mix measures -25.07 LUFS because the CP17 VO take itself is
    quiet (-21.92 LUFS); VO is kept at unity per the recipe, not
    normalized.

    Ducking is the one deliberate difference from check_cin015_mix():
    the recorded depth is 0.0 dB, NOT a negative cut. That is the
    honest measurement, and this check proves why instead of
    accepting it on trust: MUSIC/quiet_discovery is digitally silent
    from 12 s to 15 s, so the short 12.5-14.972 s VO window falls
    entirely inside the cue's near-silence gap between fragments and
    the sidechain compressor (same params as every scene mix) has no
    signal to cut. The check therefore asserts the recorded depth is
    exactly 0.0 AND independently re-measures the music stem's RMS
    over the same window from real bytes, requiring silence
    (<= -110 dBFS). If the bed were NOT silent, 0.0 dB would be a
    real ducking failure and this check would fail. The two earlier
    quiet_discovery mixes (CIN_007 -9.43 dB, CIN_011 -10.79 dB) show
    a real cut because their longer windows extended past 15 s into
    the next fragment. No recipe change, no stem change, no gain
    change was made to manufacture a number.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V1"
    manifest_path = mix_dir / "CIN016_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN016 MIX V1: missing CIN016_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin016_proposed":
        err(f"CIN016 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin016_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN016 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN016 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN016 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN016 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN016 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN016 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN016 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN016 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN016 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        music_src = None
        for st in scene["stems"]:
            if st.get("role") == "music":
                music_src = st.get("source")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] != 0.0:
                err(f"CIN016 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} != 0.0 on "
                    f"{ev['bus']} bus (manifest must record the "
                    f"silence-gap 0.0 dB, see docstring)")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN016 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
            # Prove the 0.0 dB: the music bed itself must be silent
            # over the measured window; otherwise the compressor
            # failed and 0.0 dB is a defect, not a gap.
            if music_src:
                win = ev["windowSeconds"]
                rms = _segment_rms_db(ROOT / music_src, win[0],
                                      win[1] - win[0])
                if rms is not None and rms > -110.0:
                    err(f"CIN016 MIX V1 {scene['sceneId']}: music bed "
                        f"RMS {rms:.2f} dB in the VO window is not "
                        f"silent, so ducking 0.0 dB is a failure")
                elif rms is not None:
                    note(f"CIN_016 music bed RMS in VO window: "
                         f"{rms:.2f} dBFS (silence gap confirmed)")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN016 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN016 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.528:
            err(f"CIN016 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.528")
        checked += 1
    COUNTS["cin016_mix_v1_files_checked"] = checked
    note(f"CIN_016 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 2.528 s, ends 14.972 s; ducking 0.0 dB "
         f"is the measured silence gap of quiet_discovery 12-15 s, "
         f"verified from the real stem bytes); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin017_mix():
    """Checkpoint 51: CIN_017 draft mix v1.

    Mirrors check_cin017_mix() for MIX/CIN017_DRAFT_V1/ +
    CIN017_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016, the
    CP17 draft VO take FITS its window -- by 1.832 s (3.168 s,
    12.5-15.668 s): the recorded overrun is -1.832 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017 mixes).
    The mix measures -24.63 LUFS because the CP17 VO take itself is
    quiet (-22.33 LUFS); VO is kept at unity per the recipe, not
    normalized. Ducking depth -4.85 dB is shallower than CIN_015's
    -6.87 dB: same compressor params, bach_uyen is quieter inside
    this window than it was in CIN_015's -- measured evidence, not a
    retune. The bach_uyen + underwater pairing is the same as CIN_015
    (the drowned city), stated plainly: the two scenes share one
    water chapter and the cue set has a single water form.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V1"
    manifest_path = mix_dir / "CIN017_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN017 MIX V1: missing CIN017_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin017_proposed":
        err(f"CIN017 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin017_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN017 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN017 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN017 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN017 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN017 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN017 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN017 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN017 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN017 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN017 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN017 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN017 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN017 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -1.832:
            err(f"CIN017 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -1.832")
        checked += 1
    COUNTS["cin017_mix_v1_files_checked"] = checked
    note(f"CIN_015 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 1.832 s, ends 15.668 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_cin018_mix():
    """Checkpoint 52: CIN_018 draft mix v1.

    Mirrors check_cin017_mix() for MIX/CIN018_DRAFT_V1/ +
    CIN018_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE.
    CIN_018 is the ONLY campaign scene with TWO dialogue windows,
    so this checker also verifies the manifest's "voices" list:
    the S02 take FITS its 6.5-11.5 s window by 2.120 s (2.880 s,
    6.5-9.380 s) and the S03 take OVERRUNS its 12.5-17.5 s window
    by 0.280 s (5.280 s, 12.5-17.780 s) -- the overrun is KEPT
    per the owner verdict on the three campaign overruns, and the
    tail trim at the scene edge is 0.0 for both takes. Ducking
    evidence is measured over EACH full VO window (the CP39
    full-window method per window): both depths must be real cuts
    (< 0), as sa_hoa was not silent in CIN_010's window either
    (measured cut -7.94 dB there). The reveal stinger is placed
    at 0.0 s (S01 start), NOT the recipe's 6.0 s, so it does not
    sit under the S02 dialogue -- the checker asserts the
    recorded placement. The mix measures -21.51 LUFS because it
    carries two VO takes (the CP17 takes themselves are -23.77
    and -22.54 LUFS); VO is kept at unity per the recipe, not
    normalized. The sa_hoa + desert_wind pairing is the same as
    CIN_010 (the ash-gold caravan rest), stated plainly: the two
    scenes share the Sa Hoa / desert setting and the cue set has
    a single desert form.
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1"
    manifest_path = mix_dir / "CIN018_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN018 MIX V1: missing CIN018_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin018_proposed":
        err(f"CIN018 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin018_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN018 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN018 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN018 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN018 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN018 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN018 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN018 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN018 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN018 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        ev = scene["ducking"]["evidence"]
        if len(ev) != 2:
            err(f"CIN018 MIX V1 {scene['sceneId']}: ducking evidence "
                f"has {len(ev)} entries, want 2 (one per VO window)")
        for e in ev:
            if e["depthInWindowDb"] >= 0:
                err(f"CIN018 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {e['depthInWindowDb']} >= 0 on "
                    f"{e['bus']} bus ({e.get('shotId')})")
            if e["depthOutsideWindowDb"] != 0:
                err(f"CIN018 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {e['depthOutsideWindowDb']} "
                    f"!= 0 on {e['bus']} bus ({e.get('shotId')})")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN018 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN018 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != 0.28:
            err(f"CIN018 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != 0.28")
        voices = scene.get("voices", [])
        if len(voices) != 2:
            err(f"CIN018 MIX V1 {scene['sceneId']}: voices list has "
                f"{len(voices)} entries, want 2")
        else:
            want = {"CIN_018_S02": (-2.12, [6.5, 9.38]),
                    "CIN_018_S03": (0.28, [12.5, 17.78])}
            for v in voices:
                w = want.get(v.get("shotId"))
                if w is None:
                    err(f"CIN018 MIX V1 {scene['sceneId']}: unexpected "
                        f"voice shot {v.get('shotId')}")
                    continue
                if v.get("overrunVsWindowSeconds") != w[0]:
                    err(f"CIN018 MIX V1 {scene['sceneId']}: voice "
                        f"{v.get('shotId')} overrun "
                        f"{v.get('overrunVsWindowSeconds')} != {w[0]}")
                if v.get("windowSeconds") != w[1]:
                    err(f"CIN018 MIX V1 {scene['sceneId']}: voice "
                        f"{v.get('shotId')} window "
                        f"{v.get('windowSeconds')} != {w[1]}")
                if v.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
                    err(f"CIN018 MIX V1 {scene['sceneId']}: voice "
                        f"{v.get('shotId')} tail trim "
                        f"{v.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        stinger = scene.get("stinger", {})
        if stinger.get("atSeconds") != 0.0:
            err(f"CIN018 MIX V1 {scene['sceneId']}: stinger at "
                f"{stinger.get('atSeconds')} != 0.0 (recipe deviation: "
                f"6.0 s would sit under the S02 dialogue)")
        checked += 1
    COUNTS["cin018_mix_v1_files_checked"] = checked
    note(f"CIN_018 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, two VO takes: "
         f"S02 fits its window by 2.120 s, S03 overrun +0.280 s KEPT "
         f"per owner verdict; stinger at 0.0 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")




def check_cin019_mix():
    """Checkpoint 53: CIN_019 draft mix v1.

    Mirrors check_cin017_mix() for MIX/CIN019_DRAFT_V1/ +
    CIN019_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017, the
    CP17 draft VO take FITS its window -- by 2.120 s (2.880 s,
    12.5-15.380 s): the recorded overrun is -2.12 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019 mixes).
    The mix measures -27.09 LUFS -- the quietest scene mix so far --
    because the CP17 VO take itself is one of the quietest
    (-25.52 LUFS); VO is kept at unity per the recipe, not
    normalized. Ducking depth -4.29 dB is a real cut: rift_finale
    carries real signal inside this window (segment RMS
    -22.1 dBFS measured from the stem bytes this run), same
    compressor params -- measured evidence, not a retune.
    rift_finale is the composed set's only full close and this is
    its first scene-mix use; river_shore is a third scene-mix use
    (CIN_003/CIN_008).
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1"
    manifest_path = mix_dir / "CIN019_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN019 MIX V1: missing CIN019_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin019_proposed":
        err(f"CIN019 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin019_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN019 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN019 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN019 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN019 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN019 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN019 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN019 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN019 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN019 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN019 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN019 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN019 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN019 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.12:
            err(f"CIN019 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.12")
        checked += 1
    COUNTS["cin019_mix_v1_files_checked"] = checked
    note(f"CIN_019 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 2.120 s, ends 15.380 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")



def check_cin020_mix():
    """Checkpoint 54: CIN_020 draft mix v1.

    Mirrors check_cin017_mix() for MIX/CIN020_DRAFT_V1/ +
    CIN020_MIX_V1_manifest_v1.json (single scene, no review mix):
    every stem must carry ORIGINAL_COMPOSED_BY_MUSE provenance, the
    mix WAV must match the manifest sha/duration/format, ducking
    evidence must show a real in-window cut with no out-of-window
    change, and loop joins must carry QA ratios. The mix itself is
    a DRAFT (see the manifest mixVerdict); nothing here is a mix
    PASS. The stem assignment is NEW and PROPOSED_CANDIDATE. Like
    CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_019, the
    CP17 draft VO take FITS its window -- by 2.000 s (3.000 s,
    12.5-15.500 s): the recorded overrun is -2.0 and the tail
    trim at the scene edge is 0.0. Ducking evidence is
    measured over the full VO window (the CP39 full-window method is
    retained so the depth is comparable across the
    CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019/CIN_020 mixes).
    The mix measures -23.41 LUFS; the CP17 VO take itself
    measures -19.59 LUFS. VO is kept at unity per the recipe, not
    normalized. Ducking depth -5.25 dB is a real cut: ben_mua
    carries real signal inside this window (segment RMS
    -20.5 dBFS measured from the stem bytes this run), same
    compressor params -- measured evidence, not a retune.
    ben_mua is a third scene-mix use (CIN_003/CIN_014);
    river_shore is a fourth (CIN_003/CIN_008/CIN_019). The
    recipient's draft voice is a placeholder role voice sharing
    Ly An's draft voice (CP17) -- an M-F palette item, not a mix
    decision. With this mix, every one of the 21 entries carries
    an embedded soundtrack (WO37 M-B big checkpoint 1 complete).
    """
    mix_dir = ROOT / "Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V1"
    manifest_path = mix_dir / "CIN020_MIX_V1_manifest_v1.json"
    if not manifest_path.exists():
        err("CIN020 MIX V1: missing CIN020_MIX_V1_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("mixVersion") != "v1_cin020_proposed":
        err(f"CIN020 MIX V1: mixVersion "
            f"{manifest.get('mixVersion')} != v1_cin020_proposed")
    scenes = manifest.get("scenes", [])
    if len(scenes) != 1:
        err(f"CIN020 MIX V1: {len(scenes)}/1 scenes in manifest")
    checked = 0
    for scene in scenes:
        mx = scene["mix"]
        wav = mix_dir / mx["file"]
        if not wav.exists():
            err(f"CIN020 MIX V1 {scene['sceneId']}: missing {mx['file']}")
            continue
        if is_lfs_pointer(wav):
            err(f"CIN020 MIX V1 {scene['sceneId']}: wav is an LFS pointer")
            continue
        if sha256_of(wav) != mx["sha256"]:
            err(f"CIN020 MIX V1 {scene['sceneId']}: wav sha mismatch")
        p = probe(wav)
        if p and abs(p["duration"] - mx["durationSeconds"]) > 0.02:
            err(f"CIN020 MIX V1 {scene['sceneId']}: duration "
                f"{p['duration']} != manifest {mx['durationSeconds']}")
        if p:
            if (p.get("codec") != "pcm_s16le"
                    or p.get("sample_rate") != 48000
                    or p.get("channels") != 2):
                err(f"CIN020 MIX V1 {scene['sceneId']}: format "
                    f"{p.get('codec')}/{p.get('sample_rate')}/"
                    f"{p.get('channels')} != pcm_s16le/48000/2")
        if abs(mx["durationSeconds"] - scene["seconds"]) > 0.05:
            err(f"CIN020 MIX V1 {scene['sceneId']}: mix duration "
                f"{mx['durationSeconds']} != scene {scene['seconds']}")
        for st in scene["stems"]:
            prov = st.get("provenance", "")
            if "ORIGINAL_COMPOSED_BY_MUSE" not in prov:
                err(f"CIN020 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} provenance is not composed: {prov}")
            if "PORTED_CODEX_PACKV1" in prov:
                err(f"CIN020 MIX V1 {scene['sceneId']}: {st['role']} "
                    f"stem {st['cue']} still uses a ported stem")
        for ev in scene["ducking"]["evidence"]:
            if ev["depthInWindowDb"] >= 0:
                err(f"CIN020 MIX V1 {scene['sceneId']}: ducking depth "
                    f"in window {ev['depthInWindowDb']} >= 0 on "
                    f"{ev['bus']} bus")
            if ev["depthOutsideWindowDb"] != 0:
                err(f"CIN020 MIX V1 {scene['sceneId']}: ducking depth "
                    f"outside window {ev['depthOutsideWindowDb']} "
                    f"!= 0 on {ev['bus']} bus")
        for lq in scene["loopQA"]:
            for join in lq["joins"]:
                if join.get("ratioToP999") is None:
                    err(f"CIN020 MIX V1 {scene['sceneId']}: loop join "
                        f"{lq['cue']} @{join['atSeconds']} has no "
                        f"QA ratio")
        vo = scene.get("vo", {})
        if vo.get("tailTrimmedAtSceneEdgeSeconds", 0) != 0.0:
            err(f"CIN020 MIX V1 {scene['sceneId']}: recorded VO tail "
                f"trim {vo.get('tailTrimmedAtSceneEdgeSeconds')} != 0.0")
        if vo.get("overrunVsWindowSeconds", 0) != -2.0:
            err(f"CIN020 MIX V1 {scene['sceneId']}: recorded VO "
                f"overrun {vo.get('overrunVsWindowSeconds')} != -2.0")
        checked += 1
    COUNTS["cin020_mix_v1_files_checked"] = checked
    note(f"CIN_020 draft mix v1 checked: {checked}/1 file (18 s, "
         f"fully composed stems, PROPOSED assignment, VO take fits "
         f"inside its window by 2.000 s, ends 15.500 s); "
         f"DRAFT_MIX_NOT_FINAL, not a mix PASS")


def check_playback_metadata():
    """Checkpoint 43 (Codex WO32 item 4): playback metadata for embedded mixes.

    Verifies ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json against
    the Goi 31 runtime pack + the cinematics manifest and against real bytes:
    21 scene entries (12 with embedded soundtracks incl. the prologue, 9
    silent), builder verdict PASS with no mismatches, embedded/silent sets
    exactly matching pack-vs-clips, per-scene mixVersion equal to the pack's
    embeddedMixVersion, source mix WAV sha256 equal to the recorded value,
    silent scenes carrying NO_EMBEDDED_SOUNDTRACK with no mix attached, and
    the audio-ownership policy block complete. The byte-level loudness/SHA
    evidence was measured by build_playback_metadata_v1.py at build time;
    this check verifies structure + cross-manifest consistency and file
    hashes; it does not re-measure loudness and is not an ear audition.
    """
    path = ROOT / "ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json"
    if not path.exists():
        err("playback metadata: missing PLAYBACK_METADATA_v1.json")
        return
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("manifestId") != "NGM_PLAYBACK_METADATA_V1":
        err(f"playback metadata: manifestId {d.get('manifestId')} "
            f"!= NGM_PLAYBACK_METADATA_V1")
    ver = d.get("verification", {})
    if ver.get("verdict") != "PASS" or ver.get("mismatches"):
        err(f"playback metadata: builder verdict {ver.get('verdict')} "
            f"mismatches {ver.get('mismatches')}")
    pack = json.loads(
        (ROOT / "ClientGodot/assets/cinematics/RUNTIME_PACK_GOI31_v1.json")
        .read_text(encoding="utf-8"))
    clips = json.loads(
        (ROOT / "ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json")
        .read_text(encoding="utf-8"))
    pack_versions = {s["sceneId"]: s["embeddedMixVersion"]
                     for s in pack["scenes"]}
    clip_ids = {s["sceneId"] for s in clips["sceneClips"]} | {"CIN_000"}
    entries = {s["sceneId"]: s for s in d.get("scenes", [])}
    if set(entries) != clip_ids:
        err(f"playback metadata: scene set {sorted(entries)} "
            f"!= cinematics set {sorted(clip_ids)}")
    embedded = {sid for sid, s in entries.items()
                if s.get("hasEmbeddedSoundtrack")}
    silent = {sid for sid, s in entries.items()
              if not s.get("hasEmbeddedSoundtrack")}
    if embedded != set(pack_versions):
        err(f"playback metadata: embedded set {sorted(embedded)} "
            f"!= pack set {sorted(pack_versions)}")
    for sid in sorted(embedded):
        mix = entries[sid].get("embeddedMix") or {}
        if mix.get("mixVersion") != pack_versions[sid]:
            err(f"playback metadata {sid}: mixVersion "
                f"{mix.get('mixVersion')} != pack {pack_versions[sid]}")
        wav = mix.get("sourceMixWav")
        if not wav:
            err(f"playback metadata {sid}: no sourceMixWav recorded")
            continue
        p = ROOT / wav
        if not p.exists():
            err(f"playback metadata {sid}: sourceMixWav missing {wav}")
        elif mix.get("sourceMixSha256") and sha256_of(p) != mix["sourceMixSha256"]:
            err(f"playback metadata {sid}: sourceMixWav sha mismatch {wav}")
        if entries[sid].get("audioOwnership") != "EMBEDDED_SOUNDTRACK_ONLY":
            err(f"playback metadata {sid}: audioOwnership "
                f"{entries[sid].get('audioOwnership')} "
                f"!= EMBEDDED_SOUNDTRACK_ONLY")
    for sid in sorted(silent):
        if entries[sid].get("embeddedMix") is not None:
            err(f"playback metadata {sid}: silent scene carries an embeddedMix")
        if entries[sid].get("audioOwnership") != "NO_EMBEDDED_SOUNDTRACK":
            err(f"playback metadata {sid}: audioOwnership "
                f"{entries[sid].get('audioOwnership')} "
                f"!= NO_EMBEDDED_SOUNDTRACK")
    policy = d.get("audioOwnershipPolicy", {})
    for key in ("embeddedScenes", "standaloneMixFiles", "voTakes",
                "subtitles", "questSemantics"):
        if key not in policy:
            err(f"playback metadata: policy missing key {key}")
    if d.get("reviewReel", {}).get("hasEmbeddedSoundtrack"):
        err("playback metadata: review reel unexpectedly carries a soundtrack")
    COUNTS["playback_metadata_scenes"] = len(entries)
    COUNTS["playback_metadata_embedded"] = len(embedded)
    COUNTS["playback_metadata_silent"] = len(silent)
    note(f"playback metadata checked: {len(entries)} scenes "
         f"({len(embedded)} embedded, {len(silent)} silent); "
         f"WO32 item 4; not an ear audition")


def _silence_head_tail(path, duration):
    """Head/tail silence via silencedetect at -60 dBFS (min 0.05 s)."""
    try:
        out = subprocess.run(
            ["ffmpeg", "-i", str(path), "-af",
             "silencedetect=noise=-60dB:d=0.05", "-f", "null", "-"],
            capture_output=True, text=True, timeout=120)
    except Exception as exc:
        err(f"silencedetect failed for {path}: {exc}")
        return None, None
    starts, ends = [], []
    for line in out.stderr.splitlines():
        m = re.search(r"silence_start: ([0-9.]+)", line)
        if m:
            starts.append(float(m.group(1)))
        m = re.search(r"silence_end: ([0-9.]+)", line)
        if m:
            ends.append(float(m.group(1)))
    head = tail = 0.0
    for s, e in zip(starts, ends):
        if s <= 0.01:
            head = round(e, 3)
        if e >= duration - 0.01:
            tail = round(duration - s, 3)
    if len(starts) > len(ends) and starts[-1] <= 0.01:
        head = round(duration, 3)
    return head, tail


def _wrap_jump(path):
    """CP07/CP33 seam method: mono 48 kHz f32; wrap = |last - first|."""
    import array
    try:
        raw = subprocess.check_output(
            ["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1",
             "-ar", "48000", "-f", "f32le", "-"], timeout=120)
    except Exception as exc:
        err(f"seam decode failed for {path}: {exc}")
        return None
    a = array.array("f")
    a.frombytes(raw)
    if len(a) < 9600:
        err(f"seam decode too short for {path}")
        return None
    return round(abs(a[-1] - a[0]), 6)


def _find_vo_wav(filename):
    for sub in ("P0_DRAFT", "CAMPAIGN_DRAFT", "CIN006_DRAFT", "PROLOGUE_DRAFT"):
        p = ROOT / "Art_Source/Audio/Muse/VO" / sub / filename
        if p.exists():
            return p
    if filename.startswith("VO_CIN000_SEG"):
        p = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT" / filename
        if p.exists():
            return p
    return None


def check_pronunciation_table():
    """Checkpoint 44 (Codex WO32 item 3): pronunciation/proper-name table
    + gap/head-tail/ducking/seam cues + fallback playback.

    Verifies Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json
    against real bytes and real sources: 16 names (4 spoken in current
    audio, 1 DECIDED spelling), 22 playback cue rows (16 embedded mixes +
    6 P0 v1/v2 alternates), 23 seam rows, 21 fallback rows. Head/tail
    silence is re-measured here by silencedetect and wrap jumps are
    re-measured by f32 decode; ducking depths and loop joins are checked
    against the mix manifests; fallback files are checked for existence
    (mix WAV sha256 vs manifest for embedded scenes). Loudness is NOT
    re-measured (WO32 item 3 rule) and nothing here is an ear audition:
    auditionStatus must stay NOT_AUDITIONED.
    """
    path = ROOT / ("Implementation/Content/Audio/Deliveries"
                   "/PRONUNCIATION_TABLE_v1.json")
    if not path.exists():
        err("pronunciation table: missing PRONUNCIATION_TABLE_v1.json")
        return
    d = json.loads(path.read_text(encoding="utf-8"))
    if d.get("manifestId") != "NGM_PRONUNCIATION_TABLE_V1":
        err(f"pronunciation table: manifestId {d.get('manifestId')} "
            f"!= NGM_PRONUNCIATION_TABLE_V1")
    if d.get("auditionStatus") != "NOT_AUDITIONED":
        err(f"pronunciation table: auditionStatus {d.get('auditionStatus')} "
            f"!= NOT_AUDITIONED")
    counts = d.get("counts", {})
    if counts.get("names") != 16:
        err(f"pronunciation table: names {counts.get('names')} != 16")
    if counts.get("namesSpokenInAudio") != 4:
        err(f"pronunciation table: spoken {counts.get('namesSpokenInAudio')} != 4")
    if counts.get("playbackCueRows") != 27:
        err(f"pronunciation table: cue rows {counts.get('playbackCueRows')} != 27")
    if counts.get("seamRows") != 23:
        err(f"pronunciation table: seam rows {counts.get('seamRows')} != 23")
    if counts.get("fallbackScenes") != 21:
        err(f"pronunciation table: fallback scenes {counts.get('fallbackScenes')} != 21")
    # --- names
    names = d.get("names", [])
    spoken = {n["name"] for n in names if n.get("spokenInAudio")}
    if spoken != {"Lạc Châu", "Huyền Ấn", "Bến Mưa", "Sa Hỏa"}:
        err(f"pronunciation table: spoken set {sorted(spoken)} "
            f"!= expected 4 names")
    decided = [n["name"] for n in names if n.get("status") == "DECIDED"]
    if decided != ["Tạ Vân Khanh"]:
        err(f"pronunciation table: DECIDED names {decided} "
            f"!= ['Tạ Vân Khanh']")
    srt = (ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000"
           / "CIN_000_vi.srt").read_text(encoding="utf-8")
    vo_texts = []
    for mp in ("Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json",
               "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
               "Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json"):
        man = json.loads((ROOT / mp).read_text(encoding="utf-8"))
        vo_texts += [t["text"] for t in man["takes"]]
    for nm in ("Lạc Châu", "Huyền Ấn", "Bến Mưa"):
        if nm not in srt:
            err(f"pronunciation table: {nm} claimed spoken in prologue but absent from SRT")
    if "Sa Hỏa" not in " ".join(vo_texts):
        err("pronunciation table: Sa Hỏa claimed spoken in dialogue but absent from take texts")
    all_audio_text = srt + " " + " ".join(vo_texts)
    for n in names:
        if not unicodedata.is_normalized("NFC", n["name"]):
            err(f"pronunciation table: name not NFC: {n['name']}")
        if n["name"] not in ("Lạc Châu", "Huyền Ấn", "Bến Mưa", "Sa Hỏa"):
            if n["name"] in all_audio_text:
                err(f"pronunciation table: {n['name']} unexpectedly spoken in audio")
        for t in n.get("takes", []):
            if not _find_vo_wav(t["wav"]):
                err(f"pronunciation table: take wav missing for {n['name']}: {t['wav']}")
    docs = {"Tạ Vân Khanh": 0, "Tạ Văn Khánh": 0}
    for p in (ROOT / "docs/production").rglob("*.md"):
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for k in docs:
            docs[k] += t.count(k)
    if docs["Tạ Vân Khanh"] < 10:
        err(f"pronunciation table: Tạ Vân Khanh docs count {docs['Tạ Vân Khanh']} < 10")
    if docs["Tạ Văn Khánh"] != 0:
        err(f"pronunciation table: wrong spelling Tạ Văn Khánh in docs: {docs['Tạ Văn Khánh']}")
    # --- playback cues
    for row in d.get("playbackCues", []):
        src = ROOT / row["sourceMix"]
        rt = ROOT / row["runtimeMix"]
        if not src.exists():
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: source mix missing")
            continue
        if not rt.exists():
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: runtime mix missing")
            continue
        pr = probe(src)
        if pr and pr.get("duration") is not None:
            if abs(pr["duration"] - row["durationSeconds"]) > 0.02:
                err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: duration {pr['duration']} != {row['durationSeconds']}")
        head, tail = _silence_head_tail(src, row["durationSeconds"])
        if head is not None and abs(head - row["headSilenceSeconds"]) > 0.05:
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: head silence {head} != {row['headSilenceSeconds']}")
        if tail is not None and abs(tail - row["tailSilenceSeconds"]) > 0.05:
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: tail silence {tail} != {row['tailSilenceSeconds']}")
        mans = list(src.parent.glob("*manifest*.json"))
        if not mans:
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: no mix manifest beside source mix")
            continue
        man = json.loads(mans[0].read_text(encoding="utf-8"))
        entry = None
        if "scenes" in man:
            for s in man["scenes"]:
                if s["sceneId"] == row["sceneId"]:
                    entry = s
        elif row["sceneId"] == "CIN_000":
            entry = man
        if entry is None:
            err(f"pronunciation table cue {row['sceneId']}: scene missing from mix manifest")
            continue
        mix_info = entry.get("mix", {})
        if mix_info.get("sha256") and sha256_of(src) != mix_info["sha256"]:
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: source mix sha mismatch")
        if mix_info.get("sha256") and sha256_of(rt) != mix_info["sha256"]:
            err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: runtime mix sha mismatch")
        dk = entry.get("ducking")
        if isinstance(dk, dict) and dk.get("evidence"):
            ev = dk["evidence"][0]
            tev = (row.get("duckingEvidence_manifest") or [{}])[0]
            if tev.get("depthInWindowDb") != ev.get("depthInWindowDb"):
                err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: ducking {tev.get('depthInWindowDb')} != manifest {ev.get('depthInWindowDb')}")
        elif isinstance(dk, str):
            if not row.get("duckingNote_manifest"):
                err(f"pronunciation table cue {row['sceneId']}: prologue ducking note missing")
        if row["sceneId"] != "CIN_000":
            man_joins = {}
            for lj in entry.get("loopQA", []):
                man_joins[lj["cue"]] = sorted(j["atSeconds"] for j in lj["joins"])
            tab_joins = {}
            for lj in row.get("loopJoins", []):
                tab_joins[lj["cue"]] = sorted(j["atSeconds"] for j in lj["joins"])
            if man_joins != tab_joins:
                err(f"pronunciation table cue {row['sceneId']} {row['mixVersion']}: loop joins {tab_joins} != manifest {man_joins}")
    # --- seam table
    for r in d.get("seamTable", []):
        p = ROOT / r["measuredFrom"]
        if not p.exists():
            err(f"pronunciation table seam {r['cueKey']}: bed missing {r['measuredFrom']}")
            continue
        w = _wrap_jump(p)
        if w is not None and abs(w - r["wrapJumpMeasured"]) > 0.002:
            err(f"pronunciation table seam {r['cueKey']} {r['version']}: wrap {w} != {r['wrapJumpMeasured']}")
        if r.get("flagEarCheck") != bool(r["wrapJumpMeasured"] > 0.015):
            err(f"pronunciation table seam {r['cueKey']}: flagEarCheck mismatch")
    # --- fallback table
    pb = json.loads((ROOT / "ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json").read_text(encoding="utf-8"))
    pb_scenes = {s["sceneId"]: s for s in pb["scenes"]}
    for f in d.get("fallbackTable", []):
        sid = f["sceneId"]
        for key in ("ogv", "mp4"):
            if not (ROOT / f[key]).exists():
                err(f"pronunciation table fallback {sid}: {key} missing {f[key]}")
        srt_p = f["fallbackSrtOnly"].get("srt")
        if not srt_p or not (ROOT / srt_p).exists():
            err(f"pronunciation table fallback {sid}: SRT missing {srt_p}")
        if f["hasEmbeddedSoundtrack"]:
            fw = f.get("fallbackMixWav") or {}
            if not fw.get("path") or not (ROOT / fw["path"]).exists():
                err(f"pronunciation table fallback {sid}: fallback mix missing {fw.get('path')}")
            if (pb_scenes.get(sid, {}).get("embeddedMix") or {}).get("mixVersion") != fw.get("mixVersion"):
                err(f"pronunciation table fallback {sid}: mixVersion {fw.get('mixVersion')} != playback metadata")
            f2 = f.get("fallbackStemsAndVo") or {}
            for st in f2.get("stems", []):
                if st.get("source") and not (ROOT / st["source"]).exists():
                    err(f"pronunciation table fallback {sid}: stem missing {st['source']}")
            for w in f2.get("voTakes", []):
                if not _find_vo_wav(w):
                    err(f"pronunciation table fallback {sid}: VO take missing {w}")
        else:
            if f.get("fallbackMixWav") is not None or f.get("fallbackStemsAndVo") is not None or f.get("fallbackVoAndSrt") is not None:
                err(f"pronunciation table fallback {sid}: silent scene carries an audio fallback")
    COUNTS["pronunciation_names"] = len(names)
    COUNTS["pronunciation_names_spoken"] = len(spoken)
    COUNTS["pronunciation_cue_rows"] = len(d.get("playbackCues", []))
    COUNTS["pronunciation_seam_rows"] = len(d.get("seamTable", []))
    COUNTS["pronunciation_seam_flagged"] = sum(1 for r in d.get("seamTable", []) if r.get("flagEarCheck"))
    COUNTS["pronunciation_fallback_scenes"] = len(d.get("fallbackTable", []))
    COUNTS["pronunciation_fallback_files"] = counts.get("fallbackFilesVerified", 0)
    note("Pronunciation table (checkpoint 44, Codex WO32 item 3; re-run "
         "at checkpoint 52 for the CIN_018 draft mix v1): 16 names "
         "(4 spoken in current audio, 1 DECIDED spelling), 25 playback cue "
         "rows, 22 seam rows (1 flagged for ear check), 21 fallback rows; "
         "NOT_AUDITIONED; loudness not re-measured.")


def check_ab_shortlist():
    """Checkpoint 33 (Goi 31 item 3): A/B review shortlist.

    Verifies the shortlist JSON + 6 M3U playlists against real bytes:
    every playlist entry resolves to an existing runtime file whose sha256
    matches the RUNTIME_AUDIO manifest and the sha recorded in the JSON;
    durations re-probed by ffprobe match the JSON; the canonical VO
    playlist holds exactly the 21 D1-approved windows and the CIN006
    alternate take is kept in its own playlist only (DEC-MEDIA-P0 Q3).
    Audition status must stay NOT_AUDITIONED: this check verifies bytes,
    never listening.
    """
    reports = ROOT / "Implementation/Reports/MuseMedia"
    json_path = reports / "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json"
    if not json_path.exists():
        err("AB shortlist: missing MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json")
        return
    s = json.loads(json_path.read_text(encoding="utf-8"))
    if s.get("auditionStatus") != "NOT_AUDITIONED":
        err(f"AB shortlist: auditionStatus {s.get('auditionStatus')} "
            "!= NOT_AUDITIONED")
    runtime_manifest = json.loads(
        (ROOT / "ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json")
        .read_text(encoding="utf-8"))
    manifest_sha = {"ClientGodot/" + f["runtimePath"]: f["sha256"]
                    for f in runtime_manifest["files"]}

    def check_file(rel, label):
        p = ROOT / rel
        if not p.exists():
            err(f"AB shortlist {label}: MISSING {rel}")
            return None
        if is_lfs_pointer(p):
            err(f"AB shortlist {label}: LFS POINTER, not real bytes: {rel}")
            return None
        digest = sha256_of(p)
        if rel in manifest_sha and digest != manifest_sha[rel]:
            err(f"AB shortlist {label}: sha mismatch vs runtime manifest: {rel}")
        return digest

    # --- mixes A/B table: 4 rows, re-probe durations, sha vs JSON
    ab = s.get("mixesAB", [])
    if len(ab) != 4:
        err(f"AB shortlist: mixesAB has {len(ab)} rows != 4")
    mix_checked = 0
    for row in ab:
        for version in ("v1", "v2", "v3"):
            cell = row[version]
            # locate the runtime file from the mix manifests via the JSON's
            # recorded sha: find it in the mixes section is not stored, so
            # resolve through the versioned mix dirs by filename.
            fname = cell["file"]
            for d in ("mix/p0", "mix/p0_v2", "mix/p0_v3"):
                cand = f"ClientGodot/assets/audio/{d}/{fname}"
                if (ROOT / cand).exists():
                    rel = cand
                    break
            else:
                err(f"AB shortlist mix {row['scene']} {version}: "
                    f"file not found: {fname}")
                continue
            digest = check_file(rel, f"mix {row['scene']} {version}")
            if digest is None:
                continue
            p = probe(ROOT / rel)
            if p and p["duration"] is not None and abs(
                    p["duration"] - cell["duration_s"]) > 0.02:
                err(f"AB shortlist mix {row['scene']} {version}: duration "
                    f"{p['duration']} != JSON {cell['duration_s']}")
            mix_checked += 1
        # delta arithmetic
        if abs((row["v2"]["integrated_lufs"] - row["v1"]["integrated_lufs"])
               - row["delta_v2_minus_v1_lufs"]) > 0.011:
            err(f"AB shortlist {row['scene']}: delta v2-v1 arithmetic mismatch")
        if abs((row["v3"]["integrated_lufs"] - row["v1"]["integrated_lufs"])
               - row["delta_v3_minus_v1_lufs"]) > 0.011:
            err(f"AB shortlist {row['scene']}: delta v3-v1 arithmetic mismatch")
    COUNTS["ab_shortlist_mix_cells_checked"] = mix_checked

    # --- music / stingers / ambience rows: sha + duration vs JSON
    def check_rows(rows, label):
        n = 0
        for r in rows:
            digest = check_file(r["runtimePath"], label + " " + r["cueKey"])
            if digest is None:
                continue
            if digest != r["sha256"]:
                err(f"AB shortlist {label} {r['cueKey']}: sha != JSON sha256")
            p = probe(ROOT / r["runtimePath"])
            if p and p["duration"] is not None and abs(
                    p["duration"] - r["duration_s"]) > 0.02:
                err(f"AB shortlist {label} {r['cueKey']}: duration "
                    f"{p['duration']} != JSON {r['duration_s']}")
            n += 1
        return n
    COUNTS["ab_shortlist_music_checked"] = check_rows(
        s.get("music", []), "music") + check_rows(s.get("stingers", []), "stinger")
    COUNTS["ab_shortlist_ambience_checked"] = check_rows(
        s.get("ambienceComposed", []), "ambience composed") + check_rows(
        s.get("ambiencePorted", []), "ambience ported") + check_rows(
        s.get("musicPorted", []), "music ported")
    if len(s.get("music", [])) != 9:
        err(f"AB shortlist: music cues {len(s.get('music', []))} != 9")
    if len(s.get("stingers", [])) != 4:
        err(f"AB shortlist: stingers {len(s.get('stingers', []))} != 4")
    if len(s.get("ambienceComposed", [])) != 13:
        err(f"AB shortlist: composed ambience "
            f"{len(s.get('ambienceComposed', []))} != 13")
    if len(s.get("ambiencePorted", [])) != 13:
        err(f"AB shortlist: ported ambience "
            f"{len(s.get('ambiencePorted', []))} != 13")
    if len(s.get("musicPorted", [])) != 9:
        err(f"AB shortlist: ported music "
            f"{len(s.get('musicPorted', []))} != 9")

    # --- seam table: 44 loop cues; flags only above threshold
    seam = s.get("seamTable", [])
    if len(seam) != 44:
        err(f"AB shortlist: seam table has {len(seam)} entries != 44")
    for e in seam:
        w = e.get("wrap_jump_measured")
        if w is None:
            err(f"AB shortlist seam {e['cueKey']}/{e['version']}: no measurement")
            continue
        if e.get("flag_ear_check") != (w > 0.015):
            err(f"AB shortlist seam {e['cueKey']}/{e['version']}: flag "
                f"{e.get('flag_ear_check')} inconsistent with wrap {w}")

    # --- VO: 21 canonical + 1 alternate kept separate
    vo = s.get("voCanonical", [])
    alt = s.get("voAlternate", [])
    if len(vo) != 21:
        err(f"AB shortlist: canonical VO takes {len(vo)} != 21")
    if len(alt) != 1 or alt[0].get("key") != "CIN006_ALT_T01":
        err("AB shortlist: alternate VO must be exactly CIN006_ALT_T01")
    vo_checked = 0
    for r in vo + alt:
        digest = check_file(r["runtimePath"], "VO " + r["key"])
        if digest is None:
            continue
        if digest != r["sha256"]:
            err(f"AB shortlist VO {r['key']}: sha != JSON sha256")
        p = probe(ROOT / r["runtimePath"])
        if p and p["duration"] is not None and abs(
                p["duration"] - r["takeDuration_s"]) > 0.05:
            err(f"AB shortlist VO {r['key']}: duration {p['duration']} "
                f"!= JSON {r['takeDuration_s']}")
        if r.get("canonical") and r.get("fit") == "OVERRUN":
            if r["shotId"] not in s.get("voCounts", {}).get("overruns", []):
                err(f"AB shortlist VO {r['key']}: OVERRUN not in voCounts")
        vo_checked += 1
    COUNTS["ab_shortlist_vo_checked"] = vo_checked
    if sorted(s.get("voCounts", {}).get("overruns", [])) != [
            "CIN_005_S03", "CIN_006_S03", "CIN_018_S03"]:
        err(f"AB shortlist: overrun list "
            f"{s.get('voCounts', {}).get('overruns')} != known 3 overruns")

    # --- defects: every entry has the fields a listener needs
    defects = s.get("defects", [])
    if len(defects) < 10:
        err(f"AB shortlist: defects {len(defects)} < 10")
    for d in defects:
        for field in ("id", "area", "evidence", "listenAt", "question", "status"):
            if not d.get(field):
                err(f"AB shortlist defect {d.get('id')}: missing {field}")

    # --- playlists: every entry resolves inside the runtime audio tree
    playlists = s.get("playlists", {})
    if len(playlists) != 6:
        err(f"AB shortlist: playlists {len(playlists)} != 6")
    alt_path = None
    for fname, meta in playlists.items():
        m3u = reports / fname
        if not m3u.exists():
            err(f"AB shortlist: missing playlist {fname}")
            continue
        entries = []
        lines = m3u.read_text(encoding="utf-8").splitlines()
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            entries.append(line)
        if len(entries) != meta["entries"]:
            err(f"AB shortlist playlist {fname}: {len(entries)} entries "
                f"!= JSON {meta['entries']}")
        for rel_m3u in entries:
            target = (reports / rel_m3u).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                err(f"AB shortlist playlist {fname}: entry escapes repo: "
                    f"{rel_m3u}")
                continue
            if not target.exists():
                err(f"AB shortlist playlist {fname}: missing file: {rel_m3u}")
                continue
            if is_lfs_pointer(target):
                err(f"AB shortlist playlist {fname}: LFS pointer: {rel_m3u}")
        if fname == "ab_shortlist_vo_alt_playlist.txt":
            alt_path = entries
    canonical_vo = reports / "ab_shortlist_vo_playlist.txt"
    if canonical_vo.exists() and alt_path:
        canon_text = canonical_vo.read_text(encoding="utf-8")
        for rel_m3u in alt_path:
            if rel_m3u.split("/")[-1] in canon_text:
                err("AB shortlist: alternate take present in canonical VO "
                    "playlist (Q3 violation)")
    canon_entries = []
    if canonical_vo.exists():
        canon_entries = [ln.strip() for ln in
                         canonical_vo.read_text(encoding="utf-8").splitlines()
                         if ln.strip() and not ln.strip().startswith("#")]
    if len(canon_entries) != 21:
        err(f"AB shortlist: canonical VO playlist has {len(canon_entries)} "
            "entries != 21")
    COUNTS["ab_shortlist_playlist_entries_checked"] = sum(
        m["entries"] for m in playlists.values())
    note("A/B review shortlist checked: 12 mix cells, 13 music/stinger, "
         "35 music/ambience rows (13 composed ambience + 13 ported ambience "
         "+ 9 ported music), 22 VO takes, 44 seam rows, 6 playlists "
         f"({COUNTS['ab_shortlist_playlist_entries_checked']} entries); "
         "audition status NOT_AUDITIONED, no listening PASS claimed")


def check_scene_clips():
    """Checkpoint 18 (Goi 30 item 6): per-scene clip exports.

    For CIN_001/002/004: export manifest exists; MP4/OGV exist as real
    bytes, SHA/size match the manifest, ffprobe duration/codec/dims
    match (H.264 frames == seconds*30; Theora stored frames collapse,
    CP03 rule); poster is 640x360 and SHA-matches the first panel;
    timing/SRT in the scene folder SHA-match the source files in
    Narrative/Deliveries; shot list is scene-local (starts 0, sums to
    duration); reel offsets tile the 72 s reel exactly (0-36/36-54/54-72).
    CIN_006 carried no video until checkpoint 22 (storyboard panels +
    animated take); it is now checked like the other video scenes. The
    runtime cinematics manifest's
    sceneClips must equal the export manifests, file for file.
    """
    cine = ROOT / "ClientGodot/assets/cinematics"
    base = ROOT / "Implementation/Content/Narrative/Deliveries"
    checked = 0
    video_scenes = 0
    reel_end = 0.0
    runtime = json.loads((cine / "RUNTIME_CINEMATICS_manifest_v1.json")
                         .read_text(encoding="utf-8"))
    runtime_clips = {c["sceneId"]: c
                     for c in runtime.get("sceneClips", [])}
    if len(runtime_clips) != 20:
        err(f"SCENE-CLIPS: runtime manifest has {len(runtime_clips)} "
            f"sceneClips, expected 20")
    for scene_id in ("CIN_001", "CIN_002", "CIN_004", "CIN_006", "CIN_005",
                     "CIN_009", "CIN_020",
                     "CIN_003", "CIN_007", "CIN_008", "CIN_010", "CIN_011",
                     "CIN_012", "CIN_013", "CIN_014", "CIN_015", "CIN_016",
                     "CIN_017", "CIN_018", "CIN_019"):
        exp_path = cine / scene_id / "scene_export_manifest_v1.json"
        if not exp_path.exists():
            err(f"SCENE-CLIPS {scene_id}: missing export manifest")
            continue
        exp = json.loads(exp_path.read_text(encoding="utf-8"))
        if exp.get("sceneId") != scene_id:
            err(f"SCENE-CLIPS {scene_id}: manifest sceneId mismatch")
        timing_src = base / scene_id / f"{scene_id}_timing_v1.json"
        srt_src = base / scene_id / f"{scene_id}_vi.srt"
        for key in ("timing", "srt"):
            f = exp["files"].get(key)
            if not f:
                err(f"SCENE-CLIPS {scene_id}: manifest has no {key}")
                continue
            p = ROOT / "ClientGodot" / f["path"]
            if not p.exists():
                err(f"SCENE-CLIPS {scene_id}: missing {f['path']}")
                continue
            if is_lfs_pointer(p):
                err(f"SCENE-CLIPS {scene_id}: {key} is an LFS pointer")
                continue
            if sha256_of(p) != f["sha256"]:
                err(f"SCENE-CLIPS {scene_id}: {key} sha mismatch")
            src = timing_src if key == "timing" else srt_src
            if sha256_of(p) != sha256_of(src):
                err(f"SCENE-CLIPS {scene_id}: {key} != source file")
        # Shot list: scene-local, contiguous, sums to duration.
        cursor = 0.0
        for shot in exp.get("shots", []):
            if abs(shot["startSeconds"] - cursor) > 1e-9:
                err(f"SCENE-CLIPS {scene_id}: shot {shot['shotId']} "
                    f"starts {shot['startSeconds']}, expected {cursor}")
            cursor = shot["endSeconds"]
        if abs(cursor - exp["durationSeconds"]) > 1e-9:
            err(f"SCENE-CLIPS {scene_id}: shots end {cursor}, "
                f"duration {exp['durationSeconds']}")
        if exp["videoStatus"] in ("VIDEO_FROM_STORYBOARD_PANELS",
                                  "VIDEO_ANIMATED_TAKE_KEN_BURNS"):
            video_scenes += 1
            if exp["videoStatus"] == "VIDEO_FROM_STORYBOARD_PANELS":
                off = exp.get("reelOffsetSeconds") or {}
                off_start = off.get("start")
                if off_start is None or abs(off_start - reel_end) > 1e-9:
                    err(f"SCENE-CLIPS {scene_id}: reel offset starts "
                        f"{off_start}, expected {reel_end}")
                reel_end = off.get("end", reel_end)
            else:
                # Campaign animated take: not part of the 72 s P0 reel.
                if exp.get("reelOffsetSeconds") is not None:
                    err(f"SCENE-CLIPS {scene_id}: reel offset set despite "
                        f"no reel segment")
            for key, want_codec in (("mp4", "h264"), ("ogv", "theora")):
                f = exp["files"].get(key)
                if not f:
                    err(f"SCENE-CLIPS {scene_id}: manifest has no {key}")
                    continue
                p = ROOT / "ClientGodot" / f["path"]
                if not p.exists():
                    err(f"SCENE-CLIPS {scene_id}: missing {f['path']}")
                    continue
                if is_lfs_pointer(p):
                    err(f"SCENE-CLIPS {scene_id}: {key} is LFS pointer")
                    continue
                if sha256_of(p) != f["sha256"]:
                    err(f"SCENE-CLIPS {scene_id}: {key} sha mismatch")
                if p.stat().st_size != f["sizeBytes"]:
                    err(f"SCENE-CLIPS {scene_id}: {key} size mismatch")
                pr = probe(p)
                if pr is None:
                    continue
                if pr["codec"] != want_codec:
                    err(f"SCENE-CLIPS {scene_id}: {key} codec "
                        f"{pr['codec']} != {want_codec}")
                if (pr["width"], pr["height"]) != (640, 360):
                    err(f"SCENE-CLIPS {scene_id}: {key} size "
                        f"{pr['width']}x{pr['height']} != 640x360")
                if pr["duration"] is None or abs(
                        pr["duration"] - exp["durationSeconds"]) > 0.02:
                    err(f"SCENE-CLIPS {scene_id}: {key} duration "
                        f"{pr['duration']} != {exp['durationSeconds']}")
            poster = exp["files"].get("poster")
            if not poster:
                err(f"SCENE-CLIPS {scene_id}: manifest has no poster")
            else:
                p = ROOT / "ClientGodot" / poster["path"]
                if not p.exists():
                    err(f"SCENE-CLIPS {scene_id}: missing poster")
                elif is_lfs_pointer(p):
                    err(f"SCENE-CLIPS {scene_id}: poster is LFS pointer")
                elif sha256_of(p) != poster["sha256"]:
                    err(f"SCENE-CLIPS {scene_id}: poster sha mismatch")
                elif png_dims(p) != (640, 360):
                    err(f"SCENE-CLIPS {scene_id}: poster dims "
                        f"{png_dims(p)} != 640x360")
                else:
                    if exp["videoStatus"] == "VIDEO_ANIMATED_TAKE_KEN_BURNS":
                        first_panel = (ROOT / "Art_Source/Cinematics"
                                       / f"Campaign/{scene_id}/keyframes_16x9"
                                       / f"keyframe_{exp['shots'][0]['shotId']}.png")
                    else:
                        first_panel = (ROOT / "Art_Source/Cinematics"
                                       / "P0_Animatic/panels"
                                       / f"panel_{exp['shots'][0]['shotId']}.png")
                    if sha256_of(p) != sha256_of(first_panel):
                        err(f"SCENE-CLIPS {scene_id}: poster != first "
                            f"shot keyframe/panel")
        elif exp["videoStatus"] == "PENDING_PANELS_NO_STORYBOARD":
            for key in ("mp4", "ogv", "poster"):
                if key in exp["files"]:
                    err(f"SCENE-CLIPS {scene_id}: {key} present despite "
                        f"PENDING_PANELS_NO_STORYBOARD")
                p = cine / scene_id / f"{scene_id}_640x360_30fps.{key}" \
                    if key != "poster" else cine / scene_id \
                    / f"{scene_id}_poster.png"
                if p.exists():
                    err(f"SCENE-CLIPS {scene_id}: unexpected file {p.name}")
            if exp.get("reelOffsetSeconds") is not None:
                err(f"SCENE-CLIPS {scene_id}: reel offset set despite "
                    f"no reel segment")
        else:
            err(f"SCENE-CLIPS {scene_id}: unknown videoStatus "
                f"{exp['videoStatus']!r}")
        # Runtime manifest must mirror this export manifest.
        rc = runtime_clips.get(scene_id)
        if rc is None:
            err(f"SCENE-CLIPS {scene_id}: missing from runtime manifest")
        elif rc.get("files") != exp["files"]:
            err(f"SCENE-CLIPS {scene_id}: runtime manifest files != "
                f"export manifest files")
        elif rc.get("videoStatus") != exp["videoStatus"]:
            err(f"SCENE-CLIPS {scene_id}: runtime videoStatus != export")
        checked += 1
    if abs(reel_end - 72.0) > 1e-9:
        err(f"SCENE-CLIPS: video scenes tile reel to {reel_end}, "
            f"expected 72.0")
    COUNTS["scene_clips_checked"] = checked
    COUNTS["scene_clips_with_video"] = video_scenes
    note(f"Per-scene clips checked: {checked}/20 ({video_scenes} with "
         f"video: P0 x3 panel-hold + 17 campaign animated takes); "
         f"reel tiled 0-72 exactly")


def check_cin020_keyframes():
    """Checkpoint 24: CIN_020 storyboard keyframes (3, one per shot).

    Verifies the keyframe manifest: 3 entries, each file exists under
    Art_Source/Cinematics/Campaign/CIN_020/, is 640x360, is real image
    bytes (not an LFS pointer), and matches the recorded SHA. Provenance
    is tied back to the staged generation: the staging WebP must still
    exist at its recorded path with the recorded SHA, and each entry
    must carry framing + known-defects notes. Shot IDs are cross-checked
    against the CIN_020 timing JSON. CIN_020 has an empty pack
    character list, so no character lock is involved; the S02 workers
    are unnamed generation-invented figures.
    """
    manifest_path = (ROOT / "Art_Source/Cinematics/Campaign/CIN_020"
                     / "CIN020_keyframes_manifest_v1.json")
    if not manifest_path.exists():
        err("CIN020-KEYFRAMES: missing CIN020_keyframes_manifest_v1.json")
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    timing = json.loads((ROOT / "Implementation/Content/Narrative"
                         / "Deliveries/CIN_020/CIN_020_timing_v1.json")
                        .read_text(encoding="utf-8"))
    timing_ids = {s["shotId"] for s in timing.get("shots", [])}
    staging_root = Path("/home/hatch/workspace/goals"
                        "/ng-m-ch-continuous-development/hidden_files"
                        "/cin020_keyframes_staging")
    checked = 0
    for entry in manifest.get("keyframes", []):
        sid = entry["shotId"]
        if sid not in timing_ids:
            err(f"CIN020-KEYFRAMES {sid}: not in CIN_020 timing shots")
            continue
        kf = ROOT / "Art_Source/Cinematics/Campaign/CIN_020" / entry["file"]
        if not kf.exists():
            err(f"CIN020-KEYFRAMES {sid}: missing {entry['file']}")
            continue
        if is_lfs_pointer(kf):
            err(f"CIN020-KEYFRAMES {sid}: file is an LFS pointer")
            continue
        if png_dims(kf) != (640, 360):
            err(f"CIN020-KEYFRAMES {sid}: dims {png_dims(kf)} != 640x360")
        if sha256_of(kf) != entry["sha256"]:
            err(f"CIN020-KEYFRAMES {sid}: sha mismatch")
        staged = staging_root / entry["sourceStagingFile"]
        if not staged.exists():
            err(f"CIN020-KEYFRAMES {sid}: staging source missing "
                f"{entry['sourceStagingFile']}")
        elif sha256_of(staged) != entry["sourceStagingSha256"]:
            err(f"CIN020-KEYFRAMES {sid}: staging source sha mismatch")
        if not entry.get("framing"):
            err(f"CIN020-KEYFRAMES {sid}: no framing note")
        if not entry.get("knownDefects"):
            err(f"CIN020-KEYFRAMES {sid}: no known-defects note")
        checked += 1
    if checked != 3:
        err(f"CIN020-KEYFRAMES: {checked}/3 keyframes checked")
    if {e["shotId"] for e in manifest.get("keyframes", [])} != timing_ids:
        err("CIN020-KEYFRAMES: keyframe shot set != timing shot set")
    if manifest.get("status") != "STORYBOARD":
        err(f"CIN020-KEYFRAMES: status {manifest.get('status')!r} "
            f"!= STORYBOARD")
    COUNTS["cin020_keyframes_checked"] = checked
    note(f"CIN_020 keyframes checked: {checked}/3 (storyboard level, "
         f"staging SHA-verified)")


BATCH_SCENES = ("CIN_003", "CIN_007", "CIN_008", "CIN_010", "CIN_011",
                "CIN_012", "CIN_013", "CIN_014", "CIN_015", "CIN_016",
                "CIN_017", "CIN_018", "CIN_019")


def check_campaign_keyframes_batch():
    """Checkpoint 25: storyboard keyframes for the 13 batch scenes.

    Same verification shape as the per-scene checkers of checkpoints
    21-24, generalized: each scene's keyframe manifest must carry 3
    entries whose files exist under Art_Source/Cinematics/Campaign/
    <scene>/, are 640x360 real image bytes matching the recorded SHA,
    whose staging WebP still exists at its recorded path with the
    recorded SHA, and which carry framing + known-defects notes. Shot
    IDs are cross-checked against the scene timing JSON.

    This checker also closes the gap recorded at checkpoint 24 (the
    CIN_009 manifest carried CIN_006's title undetected since
    checkpoint 23): the keyframe manifest TITLE is cross-checked
    against the timing JSON title for every campaign scene that has a
    keyframe manifest -- the 13 batch scenes plus CIN_005/CIN_006/
    CIN_009/CIN_020.
    """
    staging_base = Path("/home/hatch/workspace/goals"
                        "/ng-m-ch-continuous-development/hidden_files")
    checked = 0
    for scene_id in BATCH_SCENES:
        tag = scene_id.replace("_", "") + "-KEYFRAMES"
        scene_dir = ROOT / "Art_Source/Cinematics/Campaign" / scene_id
        manifest_path = (scene_dir
                         / f"{scene_id.replace('_', '')}"
                           "_keyframes_manifest_v1.json")
        if not manifest_path.exists():
            err(f"{tag}: missing keyframe manifest")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        timing = json.loads((ROOT / "Implementation/Content/Narrative"
                             / f"Deliveries/{scene_id}"
                               f"/{scene_id}_timing_v1.json")
                            .read_text(encoding="utf-8"))
        if manifest.get("title") != timing.get("title"):
            err(f"{tag}: manifest title {manifest.get('title')!r} != "
                f"timing title {timing.get('title')!r}")
        if manifest.get("status") != "STORYBOARD":
            err(f"{tag}: status {manifest.get('status')!r} != STORYBOARD")
        timing_ids = {s["shotId"] for s in timing.get("shots", [])}
        staging_root = (staging_base
                        / f"{scene_id.replace('_', '').lower()}"
                          "_keyframes_staging")
        scene_checked = 0
        for entry in manifest.get("keyframes", []):
            sid = entry["shotId"]
            if sid not in timing_ids:
                err(f"{tag} {sid}: not in {scene_id} timing shots")
                continue
            kf = scene_dir / entry["file"]
            if not kf.exists():
                err(f"{tag} {sid}: missing {entry['file']}")
                continue
            if is_lfs_pointer(kf):
                err(f"{tag} {sid}: file is an LFS pointer")
                continue
            if png_dims(kf) != (640, 360):
                err(f"{tag} {sid}: dims {png_dims(kf)} != 640x360")
            if sha256_of(kf) != entry["sha256"]:
                err(f"{tag} {sid}: sha mismatch")
            staged = staging_root / entry["sourceStagingFile"]
            if not staged.exists():
                err(f"{tag} {sid}: staging source missing "
                    f"{entry['sourceStagingFile']}")
            elif sha256_of(staged) != entry["sourceStagingSha256"]:
                err(f"{tag} {sid}: staging source sha mismatch")
            if not entry.get("framing"):
                err(f"{tag} {sid}: no framing note")
            if not entry.get("knownDefects"):
                err(f"{tag} {sid}: no known-defects note")
            scene_checked += 1
        if scene_checked != 3:
            err(f"{tag}: {scene_checked}/3 keyframes checked")
        if {e["shotId"] for e in manifest.get("keyframes", [])} \
                != timing_ids:
            err(f"{tag}: keyframe shot set != timing shot set")
        checked += scene_checked
    # Title cross-check for the earlier campaign keyframe scenes
    # (their per-scene checkers predate the checkpoint-24 gap finding).
    for scene_id in ("CIN_005", "CIN_006", "CIN_009", "CIN_020"):
        tag = scene_id.replace("_", "") + "-KEYFRAMES"
        manifest_path = (ROOT / "Art_Source/Cinematics/Campaign" / scene_id
                         / f"{scene_id.replace('_', '')}"
                           "_keyframes_manifest_v1.json")
        if not manifest_path.exists():
            err(f"{tag}: missing keyframe manifest (title cross-check)")
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        timing = json.loads((ROOT / "Implementation/Content/Narrative"
                             / f"Deliveries/{scene_id}"
                               f"/{scene_id}_timing_v1.json")
                            .read_text(encoding="utf-8"))
        if manifest.get("title") != timing.get("title"):
            err(f"{tag}: manifest title {manifest.get('title')!r} != "
                f"timing title {timing.get('title')!r}")
    COUNTS["campaign_batch_keyframes_checked"] = checked
    note(f"Campaign batch keyframes checked: {checked}/39 across 13 "
         f"scenes (storyboard level, staging SHA-verified); keyframe "
         f"manifest titles cross-checked vs timing for all 17 campaign "
         f"keyframe scenes")


def check_prologue():
    """Checkpoint 27: standalone prologue film CIN_000 (owner-ordered,
    script approved 2026-11-06). Verifies the timing/SRT pair, the
    narration VO manifest (+ the reused CP04 final line), the
    keyframe manifest against the staging WebPs, the film + mix
    manifests, and the runtime delivery (film files WITH an embedded
    audio stream + the runtime manifests' prologue registrations).
    Checkpoint 28 extends it to the subtitled viewing variant
    (mp4SubVi + readable SRT, owner-requested).
    The prologue is NOT part of the 20-scene campaign totals."""
    import subprocess as sp
    checked = 0
    staging = (Path.home() / "workspace/goals/ng-m-ch-continuous-"
               "development/hidden_files/prologue_keyframes_staging")
    # --- timing + SRT ---
    tpath = (ROOT / "Implementation/Content/Narrative/Deliveries"
             / "CIN_000/CIN_000_timing_v1.json")
    spath = (ROOT / "Implementation/Content/Narrative/Deliveries"
             / "CIN_000/CIN_000_vi.srt")
    timing = json.loads(tpath.read_text(encoding="utf-8"))
    if timing.get("sceneId") != "CIN_000":
        err("PROLOGUE: timing sceneId != CIN_000")
    shots = timing.get("shots", [])
    if len(shots) != 12:
        err(f"PROLOGUE: timing shots {len(shots)} != 12")
    if shots and abs(shots[-1]["endSeconds"]
                     - timing["durationSeconds"]) > 0.01:
        err("PROLOGUE: last shot end != durationSeconds")
    cues = parse_srt(spath.read_text(encoding="utf-8"))
    if cues is None:
        err("PROLOGUE: unparseable SRT")
        cues = []
    if len(cues) != 6:
        err(f"PROLOGUE: SRT cues {len(cues)} != 6")
    flat = []
    for sh in shots:
        for d in sh.get("dialogue", []):
            flat.append(d)
    if len(flat) != len(cues):
        err(f"PROLOGUE: timing dialogues {len(flat)} != SRT cues "
            f"{len(cues)}")
    for d, c in zip(flat, cues):
        if d["text"] != c["text"]:
            err(f"PROLOGUE: dialogue text drift vs SRT: {d['text'][:30]}")
        if abs(d["startSeconds"] - c["start"]) > 0.01 or \
                abs(d["endSeconds"] - c["end"]) > 0.01:
            err(f"PROLOGUE: dialogue window drift vs SRT: "
                f"{d.get('takeId')}")
    checked += 2
    # --- VO manifest + reused final line ---
    vman = json.loads((ROOT / "Art_Source/Audio/Muse/VO"
                       / "PROLOGUE_VO_manifest_v1.json").read_text(
                           encoding="utf-8"))
    if len(vman.get("segments", [])) != 5:
        err("PROLOGUE: VO segments != 5")
    for seg in vman.get("segments", []):
        src = (ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
               / seg["file"])
        rt = (ROOT / "ClientGodot/assets/audio/vo/prologue"
              / seg["file"])
        for p, lbl in ((src, "source"), (rt, "runtime")):
            if not p.exists():
                err(f"PROLOGUE VO {seg['takeId']}: missing {lbl}")
                continue
            if sha256_of(p) != seg["sha256"]:
                err(f"PROLOGUE VO {seg['takeId']}: sha drift ({lbl})")
            pr = probe(p)
            if pr and abs(pr["duration"]
                          - seg["durationSeconds"]) > 0.02:
                err(f"PROLOGUE VO {seg['takeId']}: duration drift")
            checked += 1
    lyan = (ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
            / "VO_CIN001_S05_LYAN_draft_v1.wav")
    if sha256_of(lyan) != vman["finalLine"]["sha256"]:
        err("PROLOGUE: final-line reuse sha != CP04 take on disk")
    checked += 1
    # --- keyframes vs staging ---
    kman = json.loads((ROOT / "Art_Source/Cinematics/Prologue"
                       / "CIN000_keyframes_manifest_v1.json").read_text(
                           encoding="utf-8"))
    if len(kman.get("frames", [])) != 12:
        err("PROLOGUE: keyframe frames != 12")
    for fr in kman.get("frames", []):
        png = ROOT / fr["keyframePng"]
        if not png.exists():
            err(f"PROLOGUE KF {fr['shotId']}: png missing")
            continue
        if sha256_of(png) != fr["keyframeSha256"]:
            err(f"PROLOGUE KF {fr['shotId']}: png sha drift")
        if png_dims(png) != (640, 360):
            err(f"PROLOGUE KF {fr['shotId']}: dims != 640x360")
        checked += 1
        st = fr.get("staging", {})
        if st.get("file"):
            sf = staging / st["file"]
            if not sf.exists():
                err(f"PROLOGUE KF {fr['shotId']}: staging missing")
            elif sha256_of(sf) != st["sha256"]:
                err(f"PROLOGUE KF {fr['shotId']}: staging sha drift")
            else:
                checked += 1
    # --- mix + film manifests ---
    mman = json.loads((ROOT / "Art_Source/Audio/Muse/MIX"
                       / "PROLOGUE_DRAFT/PROLOGUE_mix_manifest_v1.json"
                       ).read_text(encoding="utf-8"))
    mix = (ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
           / "PROLOGUE_mix_v1.wav")
    if sha256_of(mix) != mman["sha256"]:
        err("PROLOGUE: mix sha drift")
    pr = probe(mix)
    if pr and abs(pr["duration"] - mman["durationSeconds"]) > 0.02:
        err("PROLOGUE: mix duration drift")
    checked += 1
    fman = json.loads((ROOT / "Art_Source/Cinematics/Prologue"
                       / "CIN000_film_manifest_v1.json").read_text(
                           encoding="utf-8"))
    if fman.get("mixSha256") != mman["sha256"]:
        err("PROLOGUE: film manifest mix sha != mix manifest")
    if fman.get("timingSha256") != sha256_of(tpath):
        err("PROLOGUE: film manifest timing sha drift")
    if fman.get("srtSha256") != sha256_of(spath):
        err("PROLOGUE: film manifest srt sha drift")
    # --- runtime film files ---
    exp = json.loads((ROOT / "ClientGodot/assets/cinematics/CIN_000"
                      / "scene_export_manifest_v1.json").read_text(
                          encoding="utf-8"))
    if exp.get("videoStatus") != "VIDEO_PROLOGUE_FILM_WITH_MIXED_AUDIO":
        err("PROLOGUE: unexpected videoStatus")
    if exp.get("hasAudioTrack") is not True:
        err("PROLOGUE: export manifest hasAudioTrack != true")
    for key in ("mp4", "ogv"):
        f = exp[key]
        p = ROOT / f["path"]
        if not p.exists():
            err(f"PROLOGUE {key}: missing {f['path']}")
            continue
        if sha256_of(p) != f["sha256"]:
            err(f"PROLOGUE {key}: sha drift")
        out = sp.run(["ffprobe", "-v", "error", "-show_format",
                      "-show_streams", "-of", "json", str(p)],
                     capture_output=True, text=True).stdout
        pr2 = json.loads(out)
        kinds = [s["codec_type"] for s in pr2["streams"]]
        if "audio" not in kinds or "video" not in kinds:
            err(f"PROLOGUE {key}: streams {kinds} (audio required)")
        dur = float(pr2["streams"][0].get("duration")
                    or pr2["format"]["duration"])
        if abs(dur - f["durationSeconds"]) > 0.05:
            err(f"PROLOGUE {key}: duration drift {dur}")
        checked += 1
    # --- subtitled viewing variant (checkpoint 28) ---
    sub = exp.get("mp4SubVi")
    if not sub:
        err("PROLOGUE: export manifest lacks mp4SubVi (cp28)")
    else:
        p = ROOT / sub["path"]
        if not p.exists():
            err(f"PROLOGUE mp4SubVi: missing {sub['path']}")
        else:
            if sha256_of(p) != sub["sha256"]:
                err("PROLOGUE mp4SubVi: sha drift")
            out = sp.run(["ffprobe", "-v", "error", "-show_streams",
                          "-of", "json", str(p)],
                         capture_output=True, text=True).stdout
            prs = json.loads(out)
            kinds = [s["codec_type"] for s in prs["streams"]]
            if kinds != ["video", "audio", "subtitle"]:
                err(f"PROLOGUE mp4SubVi: streams {kinds}")
            dur = float(prs["streams"][0]["duration"])
            if abs(dur - sub["durationSeconds"]) > 0.05:
                err(f"PROLOGUE mp4SubVi: duration drift {dur}")
            checked += 1
            rs = exp.get("readableSrt", {})
            rp = ROOT / rs.get("path", "")
            if not rp.exists():
                err("PROLOGUE: readable SRT missing in runtime")
            else:
                if sha256_of(rp) != rs.get("sha256"):
                    err("PROLOGUE: readable SRT sha drift")
                rcues = parse_srt(rp.read_text(encoding="utf-8"))
                if len(rcues) != rs.get("cues"):
                    err(f"PROLOGUE: readable cues {len(rcues)} "
                        f"!= manifest {rs.get('cues')}")
                import re as _re

                def _norm(s):
                    return _re.sub(r"\s+", " ", s).strip()
                if _norm(" ".join(c["text"] for c in rcues)) != \
                        _norm(" ".join(c["text"] for c in cues)):
                    err("PROLOGUE: readable SRT text != canonical "
                        "SRT text (whitespace-normalized)")
                prev = 0.0
                for c in rcues:
                    if c["start"] < prev - 0.001 or \
                            c["end"] <= c["start"]:
                        err("PROLOGUE: readable cues not monotonic")
                        break
                    prev = c["end"]
                if rcues and rcues[-1]["end"] > \
                        timing["durationSeconds"] + 0.05:
                    err("PROLOGUE: readable cues past film end")
                emb = parse_srt(sp.run(
                    ["ffmpeg", "-v", "error", "-i", str(p), "-map",
                     "0:s:0", "-f", "srt", "-"],
                    capture_output=True, text=True).stdout)
                if len(emb) != len(rcues) or \
                        _norm(" ".join(c["text"] for c in emb)) != \
                        _norm(" ".join(c["text"] for c in rcues)):
                    err("PROLOGUE: embedded subtitle track != "
                        "readable SRT")
                checked += 2
    poster = ROOT / exp["poster"]["path"]
    title_png = (ROOT / "Art_Source/Cinematics/Prologue"
                 / "keyframes_16x9/keyframe_CIN_000_S12.png")
    if sha256_of(poster) != exp["poster"]["sha256"] or \
            sha256_of(poster) != sha256_of(title_png):
        err("PROLOGUE: poster != title-card keyframe")
    checked += 1
    for f in ("CIN_000_timing_v1.json", "CIN_000_vi.srt"):
        src = ROOT / "Implementation/Content/Narrative/Deliveries" \
            / "CIN_000" / f
        rt = ROOT / "ClientGodot/assets/cinematics/CIN_000" / f
        if sha256_of(rt) != sha256_of(src):
            err(f"PROLOGUE: runtime {f} != Deliveries source")
        checked += 1
    # --- runtime manifest registrations ---
    cm = json.loads((ROOT / "ClientGodot/assets/cinematics"
                     / "RUNTIME_CINEMATICS_manifest_v1.json").read_text(
                         encoding="utf-8"))
    pro = cm.get("prologue")
    if not pro:
        err("PROLOGUE: runtime cinematics manifest lacks 'prologue'")
    elif pro.get("mp4", {}).get("sha256") != exp["mp4"]["sha256"]:
        err("PROLOGUE: runtime manifest prologue sha != export")
    if pro and exp.get("mp4SubVi") and \
            pro.get("mp4SubVi", {}).get("sha256") != \
            exp["mp4SubVi"]["sha256"]:
        err("PROLOGUE: runtime manifest mp4SubVi sha != export")
    if cm.get("campaignTotals", {}).get("scenes") != 20:
        err("PROLOGUE: campaign totals changed (must stay 20)")
    am = json.loads((ROOT / "ClientGodot/assets/audio"
                     / "RUNTIME_AUDIO_manifest_v1.json").read_text(
                         encoding="utf-8"))
    vo_n = sum(1 for e in am["files"]
               if e.get("runtimePath", "").startswith(
                   "assets/audio/vo/prologue/"))
    mix_n = sum(1 for e in am["files"]
                if e.get("cueKey") == "MIX/CIN_000_PROLOGUE")
    if vo_n != 5 or mix_n != 1:
        err(f"PROLOGUE: runtime audio registrations vo={vo_n} "
            f"mix={mix_n} (want 5/1)")
    # WO37 M-D checkpoint 1: 627 + 10 MD1 score cues = 637.
    if am.get("totalFiles") != 637:
        err(f"PROLOGUE: runtime audio total {am.get('totalFiles')}"
            f" != 637")
    COUNTS["prologue_files_checked"] = checked
    COUNTS["audio_files_checked"] = \
        COUNTS.get("audio_files_checked", 0) + 6
    note("Prologue CIN_000 (checkpoint 27): standalone pre-game film, "
         "87.367 s, narration derived from measured VO durations; "
         "final line reuses the CP04 take; campaign totals unchanged.")
    note("Prologue subtitled variant (checkpoint 28): mp4SubVi with "
         "burned-in + embedded readable Vietnamese subtitles "
         "(26 chunks split from the canonical 6 cues, text identical) "
         "and the checkpoint 27 narration at +5 dB presentation "
         "gain; canonical MP4/OGV/SRT unchanged.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_audio_packs()
    check_composed_pack()
    check_composed_ambience_pack()
    check_composed_score_md1_pack()
    check_timing_srt()
    check_runtime_cine_manifest()
    check_animatic_vo()
    check_keyframes()
    check_cin005_keyframes()
    check_cin006_keyframes()
    check_cin009_keyframes()
    check_cin020_keyframes()
    check_campaign_keyframes_batch()
    check_campaign_vo()
    check_cin006_vo()
    check_p0_mix()
    check_p0_mix_v2()
    check_p0_mix_v3()
    check_cin006_mix()
    check_cin003_mix()
    check_cin005_mix()
    check_cin007_mix()
    check_cin008_mix()
    check_cin009_mix()
    check_cin010_mix()
    check_cin011_mix()
    check_cin012_mix()
    check_cin013_mix()
    check_cin014_mix()
    check_cin015_mix()
    check_cin016_mix()
    check_cin017_mix()
    check_cin018_mix()
    check_cin019_mix()
    check_cin020_mix()
    check_playback_metadata()
    check_pronunciation_table()
    check_ab_shortlist()
    check_scene_clips()
    check_prologue()
    result = {
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 1 (whole-game score batch 1: 7 missing core cues + 3 transition bridges; 15/15 M-D slots covered, 0 gaps; runtime audio manifest total 627 -> 637; composed score now 16 music cues + 4 stingers + 3 transitions across the checkpoint-26 and MD1 packs) following MEDIA-02 checkpoint 54 (CIN_020 draft mix v1: seventeenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1, CIN_017 v1, CIN_018 v1 and CIN_019 v1, same P0 v3 recipe; ben_mua music + river_shore ambience + reveal stinger at 6.0 s + CP17 draft VO take (fits its 12.5-17.5 s window by 2.000 s); embedded in CIN_020 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run for the new embedded mix: 21 embedded soundtracks, 0 silent, 27 playback cue rows, 23 seam rows, 21 fallback rows, 176 fallback files; runtime audio manifest total 626 -> 627, mix 29 -> 30; every entry now carries an embedded soundtrack, WO37 M-B big checkpoint 1 complete; integration baseline 6f79853, PR #119 MERGEABLE/CLEAN per Codex comment 6716052477 / WO37 MEDIA-03-05)",
        "base_integration": "6f79853",
        "branch": "muse/media-production-20261104",
        "counts": COUNTS,
        "windowFit": {"fits": COUNTS.get("vo_campaign_fits", 0),
                      "overruns": WINDOW_FIT_OVERRUNS},
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak values are NOT re-measured here; they come from checkpoints 02/04/07/08/17/19/20/26/29/30/31, measured from real bytes.",
            "No ear audition of loop seams or VO takes in this validation.",
            "Campaign dialogue windows remain PROPOSED_ANIMATIC_PLACEMENT except CIN_001_S05 (DECIDED); all 21 windows are approved for DRAFT VO production per the Goi 30 D1 decision (PR #120). This check verifies SRT==timing consistency, not directorial approval.",
            "Campaign VO window overruns (if any) are director findings, not byte mismatches; see windowFit.",
            "CIN_006 keyframes are STORYBOARD level: NPC_HA_MAC / NPC_SAM_CHU_QUY have no approved character lock, so faces/costumes are placeholders; S02's composition defect (oversized blurred glove + pale face-like shape) was FIXED in checkpoint 32 (Goi 31 item 2, retry 3: whole-table view, small glove, fiber trapped inside the paper) -- the old defect text is superseded by the revised keyframe manifest.",
            "CIN_006 alternate take CIN_006_ALT_T01 has no dialogue window by design (DEC-MEDIA-P0 Q3); its absence from the SRT and from the scene timeline is verified, not an omission.",
            "P0 mixes (v1 checkpoint 20, v2 checkpoint 29 and v3 checkpoint 31) are DRAFT_MIX_NOT_FINAL: this check verifies bytes, durations and the recorded ducking/loop evidence, not the audible balance; no ear audition has been done. v2 re-mixes the same scenes from the checkpoint-26 composed music/stingers (ported ambience + CP04 VO unchanged); v3 re-mixes them from fully composed stems (checkpoint-26 music/stingers + checkpoint-30 ambience, no ported stem remains). All three versions are delivered in parallel; adoption is Codex's decision.",
            "CIN_005 clip motion is animatic-level Ken Burns on still keyframes, not a final pose-animated take; S02 roof palette drifts from S01 (blue-grey vs red), recorded as a known defect for art-direction lock.",
            "CIN_009 keyframes are STORYBOARD level: the pack character list is empty, so no character lock is involved; the S02 workers are unnamed generation-invented figures, and S01's invented white hooded figure was REMOVED in checkpoint 32 (Goi 31 item 2) -- the old defect text is superseded by the revised keyframe manifest.",
            "CIN_020 keyframes are STORYBOARD level: the unnamed villager's appearance drifts across the three shots (three outfits/headgear) and S02 is an interior medium shot instead of a detail close view; both recorded for the final-picture revision pass.",
            "CIN_009 clip motion is animatic-level Ken Burns on still keyframes, not a final pose-animated take; S03 is not strictly top-down and adds a shrine not in the prompt.",
            "Checkpoint 25 batch keyframes are STORYBOARD level: every batch scene has named characters on screen with no approved cinematic character lock, so all faces/costumes are placeholders and final picture per shot stays blocked on the lock. Headline defects recorded at checkpoint 25 -- CIN_012_S03's baked-in choice UI bar with legible English buttons, CIN_017_S02's missing subject (no core, no serpent), CIN_015_S02's dry-courtyard setting failure with an invented mascot figure, and CIN_011's invented teal-robed woman in S01/S03 -- were FIXED in checkpoint 32 (Goi 31 item 2, 14 revised keyframes across 8 scenes, re-exported video, before/after contact sheets); the revised keyframe manifests carry the new known-defect state per shot.",
            "All campaign clip motion (checkpoints 21-25) is animatic-level Ken Burns on still keyframes, not final pose-animated takes.",
            "Composed pack (checkpoint 26, Goi 30 item 7): 13 ORIGINAL cues composed by Muse (9 music + 4 SFX/CINEMA stingers) from one leitmotif system; loudness measured from real bytes by the composer (music -22.0 LUFS target, stingers -25.0), this check re-verifies bytes/SHA/duration only. Loop seams are recorded per cue in the delivery manifest: wrapJump after a disclosed 0.25 s end-landing loop construction, wrapJumpRaw before it; no ear audition. The 541 ported PackV1 files keep their own provenance and are NOT counted as new audio; composed cues are parallel candidates whose adoption is Codex's presentation-adapter decision.",
            "Composed ambience pack (checkpoint 30): 13 ORIGINAL cues composed by Muse (all AMBIENCE/* cues, 16.0 s each) from filtered-noise beds with slow gust/swell envelopes and sparse deterministic events; loudness targets are the ported cues' checkpoint-07 measured LUFS, this check re-verifies bytes/SHA/duration only. Loop seams are recorded per cue in the delivery manifest with the same disclosed 0.25 s end-landing construction; no ear audition. Crowd beds are filtered noise only (no voices, no words). The 541 ported PackV1 files keep their own provenance and are NOT counted as new audio; composed cues are parallel candidates whose adoption is Codex's presentation-adapter decision.",
            "Composed MD1 score pack (WO37 M-D checkpoint 1): 10 ORIGINAL cues composed by Muse (7 missing core score cues -- hub, Thanh Lac, rain, swamp, dungeon, arena, tragedy -- + 3 transition bridges of 6.0 s) from the same leitmotif system as checkpoint 26; loudness measured from real bytes by the composer (music -22.0 LUFS target, transitions -25.0), this check re-verifies bytes/SHA/duration only, and the dedicated MD1 validator (check_composed_score_md1_v1.py) re-measures loudness from real bytes within +/-0.5. Loop seams are recorded per cue in the delivery manifest: wrapJump after a disclosed 0.25 s end-landing loop construction, wrapJumpRaw before it; no ear audition. The M-D coverage matrix (MUSIC_SCORE_MD_COVERAGE_v1.json) shows 15/15 slots covered, 0 gaps. The 541 ported PackV1 files keep their own provenance and are NOT counted as new audio; MD1 cues are parallel candidates whose adoption is Codex's presentation-adapter decision. Intro/outro segments, stems and phase-layer candidates remain open for M-D checkpoint 2.",
            "A/B review shortlist (checkpoint 33, Goi 31 item 3): 12 P0 mix cells, 9 composed music + 4 stingers, 13 composed + 13 ported ambience, 21 canonical VO takes + 1 alternate, 44 seam rows, 6 M3U playlists (72 entries). This check verifies bytes/SHA/duration and playlist resolution only; loudness/true-peak/seam numbers in the shortlist JSON were measured from real bytes by build_ab_shortlist_goi31.py at build time and are NOT re-measured here. Audition status is NOT_AUDITIONED: no human listening has happened, and the defect table (D-01..D-12) is open for the listener/director. The alternate take CIN_006_ALT_T01 is verified to live in its own playlist only. D-12 resolved by owner decision 2026-11-07: the canonical spelling is 'Tạ Vân Khanh'. The 'Tạ Văn Khánh' label came from the shortlist tool's SPEAKER_DISPLAY fallback (the P0 VO manifest stores the speaker id only; no manifest carried the wrong spelling) and was corrected at checkpoint 36.",
            "Prologue CIN_000 (checkpoint 27): a standalone pre-game film, NOT a campaign scene; its narration is DRAFT TTS (narrator casting is a director decision), its mix is DRAFT_MIX_NOT_FINAL, and no ear audition has been done. Identity checks inside the film builder use crop-compensated diffs (full-res < 20, 160x90 structure < 8) because the render path resamples twice; a brute-force fit on S01 confirmed the designed zooms (1.015/1.035/1.055) at zero offset with a 4.2-6.5 structure floor. Headline picture defects: S01/S03 mechanism design drift and S11's ambiguous arrival direction, recorded per shot in CIN000_keyframes_manifest_v1.json.",
            "CIN_006 draft mix v1 (checkpoint 34, Goi 31 item 4): first scene mix for CIN_006, built with the P0 v3 recipe (music thang_long + ambience thang_long_crowd + reveal stinger at 6.0 s + CP19 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_006 and the scene timing manifest lists only the reveal stinger as a candidate stem. The +0.52 s VO overrun window is kept as-is per the owner decision; the take tail is trimmed 0.02 s at the 18.00 s scene edge (recorded, not hidden). The alternate take CIN_006_ALT_T01 is NOT in the mix or the pack (DEC-MEDIA-P0 Q3). The minimal runtime pack embeds v3 mixes in the P0 scene OGV/MP4 and the CIN_006 v1 mix in CIN_006's OGV/MP4 (video streams copied bit-for-bit, verified by stored-frame counts); the prologue film is verified unchanged. Runtime playback is clean OGV + sidecar SRT overlay; the baked-subtitle MP4 is review-only. No ear audition has been done (NOT_AUDITIONED).",
            "CIN_003 draft mix v1 (checkpoint 37): second scene mix after CIN_006 v1, same P0 v3 recipe (music ben_mua + ambience river_shore + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_003 and the scene timing manifest lists only the reveal stinger as a candidate stem. Unlike CIN_006, the CP17 draft VO take FITS inside its 12.5-17.5 s window (4.032 s, ends 16.532 s): no overrun, no tail trim. The v1 mix is embedded in CIN_003's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_005 draft mix v1 (checkpoint 38): third scene mix after CIN_006 v1 and CIN_003 v1, same P0 v3 recipe (music thang_long + ambience thang_long_crowd + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_005 and the scene timing manifest lists only the reveal stinger as a candidate stem; thang_long/thang_long_crowd are the Thanh Lac city cues for this late-morning courtyard scene (pack shot prompts S01/S02: merchants, tea stall, five faction flags in one breeze). Like CIN_006, the CP17 draft VO take OVERRUNS its 12.5-17.5 s window by 0.160 s (5.160 s, ends 17.660 s) and the overrun is KEPT per the owner verdict (Goi 30 D1); no tail trim at the 18.00 s scene edge. The v1 mix is embedded in CIN_005's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_007 draft mix v1 (checkpoint 39): fourth scene mix after CIN_006 v1, CIN_003 v1 and CIN_005 v1, same P0 v3 recipe (music quiet_discovery + ambience wind_canopy + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_007 and the scene timing manifest lists only the reveal stinger as a candidate stem; quiet_discovery/wind_canopy are the forest cues for this ancient rain-green forest scene (pack shot prompts S01/S02: trickle over bark, carved grooves brightening, leaf shadow). Unlike CIN_005/CIN_006, the CP17 draft VO take FITS inside its 12.5-17.5 s window (3.912 s, ends 16.412 s): no overrun, no tail trim. Ducking evidence is measured over the full VO window because quiet_discovery is sparse by design (the first 2 s of the window are near-silence at -91 dB mean). The mix measures -18.05 LUFS / -1.43 dBTP, louder than the CIN_003/CIN_005 mixes because the CP17 take itself is louder (mean -17.9 dB, max -1.4 dB); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_007's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_008 draft mix v1 (checkpoint 40): fifth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1 and CIN_007 v1, same P0 v3 recipe (music tran_son + ambience river_shore + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_008 and the scene timing manifest lists only the reveal stinger as a candidate stem; tran_son is the composed set's bell-led gate form, matching the scene's central gate image (S02: tall wooden double gate nearly shut, lantern-lit), and river_shore is the water-edge bed for the bamboo forest pool (S03). Unlike CIN_005/CIN_006, the CP17 draft VO take FITS inside its 12.5-17.5 s window (3.552 s, ends 16.052 s): no overrun, no tail trim. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -24.58 LUFS / -1.61 dBTP, quieter than the CIN_007 mix because the CP17 take itself is quieter (-23.10 LUFS per checkpoint 17); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_008's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_009 draft mix v1 (checkpoint 41): sixth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1 and CIN_008 v1, same P0 v3 recipe (music lam_trieu + ambience waterfall + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_009 and the scene timing manifest lists only the reveal stinger as a candidate stem; lam_trieu is the composed set's G-major transposition with ornamented flute, carrying the forest's answering voice of the scene title 'Tieng rung duoc dap', and waterfall is the water bed for the stream running through all three shots. Unlike CIN_005/CIN_006, the CP17 draft VO take FITS inside its 12.5-17.5 s window (4.080 s, ends 16.580 s): no overrun, no tail trim. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -17.84 LUFS / -2.91 dBTP, hotter than the CIN_008 mix because the CP17 take itself is hotter (-17.23 LUFS per checkpoint 17); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_009's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_010 draft mix v1 (checkpoint 42): seventh scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1 and CIN_009 v1, same P0 v3 recipe (music sa_hoa + ambience desert_wind + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_010 and the scene timing manifest lists only the reveal stinger as a candidate stem; sa_hoa is the composed set's desert form ('Sa Hoa -- Lo va cat', kiln and sand: A minor pentatonic, dry bright plucks, 110 BPM), matching the scene's ash-gold caravan rest and last-water-flask image, and desert_wind is the desert wind bed for the dunes running through all three shots. Unlike CIN_005/CIN_006, the CP17 draft VO take FITS inside its 12.5-17.5 s window (2.808 s, ends 15.308 s): no overrun, no tail trim. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -24.60 LUFS / -4.86 dBTP, quieter than the CIN_009 mix because the CP17 take itself is quieter (-22.01 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_010's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_011 draft mix v1 (checkpoint 45): eighth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1 and CIN_010 v1, same P0 v3 recipe (music quiet_discovery + ambience wind_canopy + reveal stinger at 6.0 s + CP17 draft VO at 12.2 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_011 and the scene timing manifest lists only the reveal stinger as a candidate stem; quiet_discovery is the composed set's exploration silence ('Khoang lang kham pha': solo flute fragments, single bells, long near-silences, water drops, 60 BPM), matching the scene's quiet carving workshop and moral reflection (S01 workbench with carved tablets, S02 two men in an open bamboo shelter, S03 Ha Mac leaning over a carved landscape panel), and wind_canopy is the wind-through-canopy bed for the open shelter and the greenery behind S02. Unlike CIN_005/CIN_006, the CP17 draft VO take FITS inside its 12.2-17.8 s window (5.592 s, ends 17.792 s) by 0.008 s: no overrun, no tail trim. The window was widened from the uniform 12.5-17.5 s for rate (87 chars at 15.54 chars/s). Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -20.34 LUFS / -3.30 dBTP; the CP17 take itself is quiet (-21.50 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_011's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 12 embedded soundtracks, 9 silent CIN_012-020, 18 playback cue rows, 19 seam rows (1 flagged), 21 fallback rows, 130 files verified. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_012 draft mix v1 (checkpoint 46): ninth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1 and CIN_011 v1, same P0 v3 recipe (music tran_son + ambience forge + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_012 and the scene timing manifest lists only the reveal stinger as a candidate stem; tran_son is the composed set's bell-led stately form ('Tran Son — Nguoi qua cua', 90 BPM), matching the scene's lantern-lit hall and moral decision (S01 stone furnace, S02 archive desk, S03 Ha Mac behind the long wooden table), and forge is the fire bed for the stone furnace and smithing tools of S01. sa_hoa was passed over: it was just used for CIN_010 and its 110 BPM drive suits that desert scene better than this quiet moral line. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011, the CP17 draft VO take FITS inside its 12.5-17.5 s window (4.320 s, ends 16.820 s) by 0.680 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (71 chars at 14.20 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -25.60 LUFS / -5.13 dBTP; the CP17 take itself is quiet (-25.38 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_012's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 13 embedded soundtracks, 8 silent CIN_013-020, 19 playback cue rows, 20 seam rows (1 flagged), 21 fallback rows, 135 files verified. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_013 draft mix v1 (checkpoint 47): tenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1 and CIN_012 v1, same P0 v3 recipe (music lam_trieu + ambience mountain_wind + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_013 and the scene timing manifest lists only the reveal stinger as a candidate stem; lam_trieu is the composed set's G-major transposition with ornamented flute, matching the scene's village road, rice paddies and waiting line (S01 stone gatehouse, S02 the refugee leader with his map, S03 Ly An at the open gate), and mountain_wind is the wind bed for the mountain gate and open pass (first embedded use). tran_son was passed over: the bell-led gate form, but just used for CIN_012, the immediately preceding scene. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012, the CP17 draft VO take FITS inside its 12.5-17.5 s window (2.472 s, ends 14.972 s) by 2.528 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (37 chars at 7.40 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability). The mix measures -25.87 LUFS / -5.17 dBTP; the CP17 take itself is quiet (-22.51 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_013's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 14 embedded soundtracks, 7 silent CIN_014-020, 20 playback cue rows, 21 seam rows (1 flagged), 21 fallback rows, 140 files verified. Staging question, not a mix defect: the timing manifest marks the S03 dialogue onscreen: true for the refugee leader, but the S03 keyframe and the runtime clip at 15 s show only Ly An at the open gate; the leader is on screen in S02. The line plays over Ly An waiting at the gate; voice-over vs staging mismatch is a director/Codex call. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_014 draft mix v1 (checkpoint 48): eleventh scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1 and CIN_013 v1, same P0 v3 recipe (music ben_mua + ambience wind_canopy + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_014 and the scene timing manifest lists only the reveal stinger as a candidate stem; ben_mua is the campaign's own leitmotif statement ('Ben Mua', the rain quay): D major pentatonic question phrase hanging on scale degree 2, tail withheld -- the unresolved hanging phrase for a commander who stamps an order he knows is false (S01 kneeling among discarded armour, S02 the seal set down in detail, S03 Tong Banh at the open village gate), and wind_canopy is the wind-through-canopy bed for the bamboo framing all three shots. lam_trieu was passed over: just used for CIN_013, the immediately preceding scene; tran_son was passed over: the bell-led gate form, already used for CIN_008 and CIN_012. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013, the CP17 draft VO take FITS inside its 12.5-17.5 s window (3.072 s, ends 15.572 s) by 1.928 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (35 chars at 7.00 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): -8.84 dB, deeper than CIN_013's -5.19 dB because ben_mua is louder inside the window than lam_trieu was -- same compressor params, measured evidence, not a retune. The mix measures -24.42 LUFS / -1.95 dBTP; the CP17 take itself is quiet (-22.05 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_014's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 15 embedded soundtracks, 6 silent CIN_015-020, 21 playback cue rows, 21 seam rows (1 flagged), 21 fallback rows, 145 files verified. Staging: the timing manifest marks the S03 dialogue onscreen: true for Tong Banh and the keyframe places a blue-robed figure at the open gate, but the recorded keyframe defects note he is not visually identifiable in S03 (his armour differs across S01/S02 and neither S03 figure matches it) -- a final-picture/character-lock matter, not a mix defect; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_015 draft mix v1 (checkpoint 49): twelfth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1 and CIN_014 v1, same P0 v3 recipe (music bach_uyen + ambience underwater + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_015 and the scene timing manifest lists only the reveal stinger as a candidate stem; bach_uyen is the composed set's underwater low-passed form (850 Hz), the setting-exact cue for a drowned city (S01 wide view of the submerged ruined town, S02 the dining bowl tied to the stone table with the guide rope and a bare diver hand, S03 top-down underwater corridor with a small diver figure in a conical hat), and underwater is the composed underwater bed for the submerged city framing all three shots; both are first scene-mix uses (P0 v3 review reel only before). ben_mua was passed over: just used for CIN_014, the immediately preceding scene. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014, the CP17 draft VO take FITS inside its 12.5-17.5 s window (2.880 s, ends 15.380 s) by 2.120 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s; it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): -6.87 dB, shallower than CIN_014's -8.84 dB because bach_uyen is quieter inside the window than ben_mua was -- same compressor params, measured evidence, not a retune. The mix measures -25.30 LUFS / -3.89 dBTP; the CP17 take itself is quiet (-23.27 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_015's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 16 embedded soundtracks, 5 silent CIN_016-020, 22 playback cue rows, 22 seam rows (1 flagged), 21 fallback rows, 150 files verified. Staging: the timing manifest marks the S03 dialogue onscreen: true for the Diver Lead and the keyframe places a small diver figure with a conical hat at the bottom centre of the top-down corridor, but the figure is tiny and seen from above/behind, so the speaker is not identifiable by face or gear from the picture alone (S02 shows only a bare diver hand, S01 no figure at all) -- a final-picture/character-lock matter, not a mix defect; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_016 draft mix v1 (checkpoint 50): thirteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1 and CIN_015 v1, same P0 v3 recipe (music quiet_discovery + ambience wind_canopy + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_016 and the scene timing manifest lists only the reveal stinger as a candidate stem; quiet_discovery is the composed set's exploration silence ('Khoang lang kham pha': solo flute fragments, single bells, long near-silences, water drops, 60 BPM), the setting-exact cue for a quiet indoor conversation about writing someone else's story down (S01 detail of the old manuscript under the hanging lamp, S02 the blue-robed man at the desk with a hooded figure seen from behind, S03 Ha Mac writing in his book as he asks the elder across the desk), and wind_canopy is the wind-through-canopy bed for the greenery outside the S03 window and the bamboo walls; both are third scene-mix uses (CIN_007, CIN_011, CIN_014 for wind_canopy). Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015, the CP17 draft VO take FITS inside its 12.5-17.5 s window (2.472 s, ends 14.972 s) by 2.528 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (42 chars at 8.40 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): 0.0 dB -- NOT a missing compressor: MUSIC/quiet_discovery is digitally silent from 12 s to 15 s (RMS -120 dB floor), so the 12.5-14.972 s window falls entirely inside the cue's near-silence gap between fragments; the earlier quiet_discovery mixes show a real cut (CIN_007 -9.43 dB, CIN_011 -10.79 dB) because their longer windows extended past 15 s; the validator re-measures the music stem RMS in the window from real bytes and requires silence (<= -110 dBFS), so a 0.0 dB depth on a non-silent bed would fail. Same compressor params, measured evidence, not a retune. The mix measures -25.07 LUFS / -4.36 dBTP; the CP17 take itself is quiet (-21.92 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_016's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts and by video-stream MD5 vs the pre-mux files). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 17 embedded soundtracks, 4 silent CIN_017-020, 23 playback cue rows, 22 seam rows (1 flagged), 21 fallback rows, 155 files verified. Staging: unlike CIN_015, the speaker IS identifiable here -- the S03 keyframe shows Ha Mac clearly (face in profile, green headband, green robe, brush in hand, writing in the book) asking the blue-robed elder across the desk; whether the hooded figure seen from behind in S02 is Ha Mac arriving is a continuity question for final picture (woven basket-hat on his back in S03 vs rectangular backpack in S02) -- a final-picture/character-lock matter, not a mix defect; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "Playback metadata (checkpoint 43, Codex WO32 item 4): PLAYBACK_METADATA_v1.json records, for every runtime cinematic, whether a soundtrack is embedded, which mix (version + source WAV + sha256 + stems + VO take/window) and which subtitle source, plus the audio-ownership rules the presentation adapter must honour (embedded soundtrack only; standalone mix files and VO takes are alternates/components, never simultaneous layers; runtime subtitles are overlay SRT, burned variants review-only; rewatch/skip/seen/fallback grant no quest). All byte-level evidence (stream layout, embedded loudness vs source mix and pack record, file sha256, SRT cue counts) was measured by build_playback_metadata_v1.py at build time with a 0.40 LUFS tolerance; this check verifies structure, cross-manifest consistency and source-mix hashes. The metadata is a delivery FOR Codex's adapter; Muse does not wire playback. All mixes remain DRAFT_MIX_NOT_FINAL and NOT_AUDITIONED; final audible approval is pending per WO32.",
            "CIN_017 draft mix v1 (checkpoint 51): fourteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1 and CIN_016 v1, same P0 v3 recipe (music bach_uyen + ambience underwater + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_017 and the scene timing manifest lists only the reveal stinger as a candidate stem; bach_uyen is the composed set's underwater low-passed form (850 Hz), the setting-exact cue for a tide-serpent scene built around water and a crystal core (S01 wide view of the flooded ruined temple courtyard at night, the teal tide serpent coiled around the crystal core in the water; S02 detail of the serpent coiled around the glowing crystal on the stone pillar, bubbles rising; S03 misty river gorge with fishing gear on the bank and the serpent-shaped dark current winding down the river), and underwater is the composed underwater bed for the water framing all three shots; both are second scene-mix uses -- the same pairing as CIN_015 (the drowned city), stated plainly because the two scenes share one water chapter and the cue set has a single water form; boss_mang_cot was passed over because it is boss material for the WRONG boss (Mang Cot, not the Tide Serpent), and this beat is a quiet line, not a boss fight. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016, the CP17 draft VO take FITS inside its 12.5-17.5 s window (3.168 s, ends 15.668 s) by 1.832 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (44 chars at 8.80 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): -4.85 dB, shallower than CIN_015's -6.87 dB because bach_uyen is quieter inside this window than it was in CIN_015's -- same compressor params, measured evidence, not a retune. The mix measures -24.63 LUFS / -2.44 dBTP; the CP17 take itself is quiet (-22.33 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_017's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 18 embedded soundtracks, 3 silent CIN_018-020, 24 playback cue rows, 22 seam rows (1 flagged), 21 fallback rows, 160 files verified. Staging: like CIN_015, the speaker is NOT identifiable here -- and this time the timing manifest says so itself: the S03 dialogue onscreen is null for the Diver Lead, and the S03 keyframe shows only the misty river gorge with no diver figure anywhere in the frame (S01 the serpent with no human figure, S02 only the serpent and the crystal) -- the line is delivered off-screen, like Ly An's voice in CIN_004 (DEC-MEDIA-P0 Q2); a final-picture/character-lock matter, not a mix defect; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_018 draft mix v1 (checkpoint 52): fifteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1 and CIN_017 v1, same P0 v3 recipe (music sa_hoa + ambience desert_wind + reveal stinger at 0.0 s + TWO CP17 draft VO takes). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_018 and the scene timing manifest lists only the reveal stinger as a candidate stem; sa_hoa is the composed set's desert form ('Sa Hoa -- Lo va cat': kiln and sand, A minor pentatonic, dry bright plucks, 110 BPM), the setting-exact cue for a drought scene built around the lack of water (S01 cracked drought field, a man pouring the last water from a gourd, a sealed petition and a measuring post; S02 Co Vo Tuong at his desk; S03 the masked hooded figure beside the copper water-machine at night), and desert_wind is the desert wind bed for the dry field and the night bamboo of all three shots; both are second scene-mix uses -- the same pairing as CIN_010 (the ash-gold caravan rest), stated plainly because the two scenes share the Sa Hoa / desert setting and the cue set has a single desert form; bach_uyen was passed over because it is the underwater form -- the opposite of this scene (water present there, water withheld here). CIN_018 is the ONLY campaign scene with TWO dialogue windows: the S02 take (Co Vo Tuong) FITS inside its 6.5-11.5 s window (2.880 s, ends 9.380 s) by 2.120 s and the S03 take (player) OVERRUNS its 12.5-17.5 s window by 0.280 s (5.280 s, ends 17.780 s) with the overrun KEPT per the owner verdict on the three campaign overruns, not trimmed, not sped up; no tail trim at the scene edge for either take. Both takes duck the music bus through ONE combined VO bus (ducking -6.05 dB over the S02 window and -7.44 dB over the S03 window, CP39 full-window method per window -- real cuts, as sa_hoa was not silent in CIN_010's window either, measured cut -7.94 dB there). The reveal stinger is placed at 0.0 s (S01 start), NOT the recipe's 6.0 s: the cue is 3.000 s long, so at 6.0 s it would sit under 2.5 s of the S02 line -- the scene's key refusal line, spoken on screen. The mix measures -21.51 LUFS / -2.51 dBTP; the CP17 VO takes themselves are -23.77 LUFS (S02) and -22.54 LUFS (S03), re-verified from real bytes this run; VO stays at unity per the recipe, no gain change was made. The S03 take is VOICE_PLACEHOLDER_ONLY (VOICE_GUIDE assigns the player no spoken voice or gender). The v1 mix is embedded in CIN_018's runtime OGV + review MP4 (video streams copied bit-for-bit, verified by stored-frame counts and by video-stream MD5 vs the pre-mux files). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 19 embedded soundtracks, 2 silent CIN_019-020, 25 playback cue rows, 22 seam rows (1 flagged), 21 fallback rows, 166 files verified. Staging: the S02 speaker IS identifiable (onscreen: true, face visible at his desk); the S03 line is delivered off-screen (onscreen: null, like Ly An's voice in CIN_004) -- the masked figure in the S03 keyframe is NOT identified as the speaker, and the keyframe defects record its full-face porcelain mask (not the specified cracked half mask) and torso-spanning copper machinery; S02 is a medium shot instead of the detail close view and his hair differs from S01's; S01's petition renders as a modern wax-sealed envelope. Final-picture/character-lock matters, not mix defects; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_019 draft mix v1 (checkpoint 53): sixteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1, CIN_017 v1 and CIN_018 v1, same P0 v3 recipe (music rift_finale + ambience river_shore + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_019 and the scene timing manifest lists only the reveal stinger as a candidate stem; rift_finale is the composed set's only full close (the Ben Mua leitmotif's answering tail F#-E-D, withheld in every other cue except the resolve stinger), the setting-exact cue for the campaign's resolution scene (S01 wide three-quarter view of a mountaintop stone platform at dusk, five elemental pillars around an empty central space; S02 medium interior of a machinery hall, two wardens at the levers; S03 wide dawn view of a riverside village under reconstruction, water cascading through a stepped stone-repaired channel, workers carrying logs and baskets), and river_shore is the composed water-edge bed for the rebuilt river village the spoken line lands in; rift_finale is a first scene-mix use, river_shore a third (CIN_003/CIN_008); mountain_wind was passed over because it beds only S01's mountaintop. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017, the CP17 draft VO take FITS inside its 12.5-17.5 s window (2.880 s, ends 15.380 s) by 2.120 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (39 chars at 7.80 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): -4.29 dB, a real cut -- rift_finale carries real signal inside this window (segment RMS -22.1 dBFS measured from the stem bytes this run); same compressor params, measured evidence, not a retune. The mix measures -27.09 LUFS / -8.62 dBTP -- the quietest scene mix so far; the CP17 take itself is one of the quietest (-25.52 LUFS per checkpoint 17, re-verified from real bytes this run); VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_019's runtime OGV + review MP4 (video streams copied bit-for-bit). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 20 embedded soundtracks, 1 silent CIN_020, 26 playback cue rows, 23 seam rows (1 flagged), 21 fallback rows, 171 files verified. Staging: the timing records the S03 dialogue onscreen: true for Ly An (NPC_LYAN) and the keyframe manifest lists her among the scene's on-screen characters, but the S03 frame is a wide dawn view of the whole village under reconstruction and no individual figure is identifiable as Ly An at this scale; the scene's faces and costumes are storyboard placeholders (NPC_LYAN has no approved cinematic character lock) -- a final-picture/character-lock matter, not a mix defect; the mix does not move the VO. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "CIN_020 draft mix v1 (checkpoint 54): seventeenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1, CIN_017 v1, CIN_018 v1 and CIN_019 v1, same P0 v3 recipe (music ben_mua + ambience river_shore + reveal stinger at 6.0 s + CP17 draft VO at 12.5 s). The stem assignment is NEW and PROPOSED_CANDIDATE -- the CP02 stem table assigns nothing to CIN_020 and the scene timing manifest lists only the reveal stinger as a candidate stem; ben_mua is the composed set's rain-quay leitmotif, the theme of the opening quay where the sealed letter changed hands, the setting-exact cue for the closing scene where the letter is answered at the same river (S01 medium shot, the villager at the repaired plank table on the river dock reading the opened letter; S02 interior, the villager at a wooden desk by an open window writing the reply, the river beyond; S03 top-down view of the table with the folded reply, the villager seated at frame left seen from behind), and river_shore is the composed water-edge bed for the dock and the river beyond the window; ben_mua is a third scene-mix use (CIN_003/CIN_014), river_shore a fourth (CIN_003/CIN_008/CIN_019); rift_finale was passed over because its full close was spent at CIN_019's resolution -- this scene is the quiet morning after. Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_019, the CP17 draft VO take FITS inside its 12.5-17.5 s window (3.000 s, ends 15.500 s) by 2.000 s: no overrun, no tail trim. The window is the uniform 12.5-17.5 s (39 chars at 7.80 chars/s); it was NOT widened. Ducking evidence is measured over the full VO window (the CP39 method, retained for comparability): -5.25 dB, a real cut -- ben_mua carries real signal inside this window (segment RMS -20.5 dBFS measured from the stem bytes this run); same compressor params, measured evidence, not a retune. The mix measures -23.41 LUFS / -5.22 dBTP; the CP17 take itself measures -19.59 LUFS per checkpoint 17, re-verified from real bytes this run; VO stays at unity per the recipe, no gain change was made. The v1 mix is embedded in CIN_020's runtime OGV + review MP4 (video streams copied bit-for-bit). The playback metadata (checkpoint 43 builder) and pronunciation table (checkpoint 44 builder) were re-run for the new embedded mix: 21 embedded soundtracks, 0 silent, 27 playback cue rows, 23 seam rows (1 flagged), 21 fallback rows, 176 files verified. Casting: the recipient's voice is a placeholder role voice (CP17 VOICE_LETTER_RECIPIENT; identity/gender undecided) and the draft take uses the same fictional system voice as Ly An's drafts -- a draft-casting collision for the WO37 M-F palette work to resolve. Staging: the timing records the S03 dialogue onscreen: null; the S03 keyframe shows the villager seated at frame left seen from behind in the top-down frame, so the speaker is present but his face is not visible, and the CP24 keyframe manifest records his appearance drifting between all three shots (S01 headband and brown vest; S02 conical hat and blue tunic; S03 green top and dark headwrap) -- the scene's pack character list is empty, so no named character lock exists for him -- final-picture/casting matters, not mix defects; the mix does not move the VO. With this mix, every one of the 21 entries carries an embedded soundtrack and Work Order 37 M-B big checkpoint 1 is complete. DRAFT_MIX_NOT_FINAL, no ear audition (NOT_AUDITIONED); adoption is Codex's adapter decision.",
            "Pronunciation table (checkpoint 44, Codex WO32 item 3; re-run at checkpoint 54 for the CIN_020 draft mix v1): PRONUNCIATION_TABLE_v1.json records 16 proper names with syllable + tone + approximate Northern Vietnamese IPA guidance (only 4 are actually spoken in current audio: Lạc Châu, Huyền Ấn, Bến Mưa in the prologue narration and Sa Hỏa in CIN_018_S03; the 10 speaker/role names are never spoken in their own lines, so the listener checks voice fit, not name pronunciation), 27 playback cue rows (21 embedded mixes + 6 P0 v1/v2 alternates) with head/tail silence re-measured by silencedetect, VO take lead/tail silence, window slack and manifest ducking/loop-join evidence, 23 seam rows with wrap jumps re-measured from the runtime OGG beds (1 flagged: MUSIC/sa_hoa composed, 0.016015; no new seam row this checkpoint -- MUSIC/ben_mua + AMBIENCE/river_shore were already measured at CIN_003), and a 21-scene fallback chain (embedded -> standalone mix -> stems+VO -> VO+SRT -> SRT only; no scene is silent any more (CIN_020 embedded at checkpoint 54); the chain's silent tail survives only as the terminal fallback if an embedded file is missing or corrupt at runtime). CIN_018's cue row carries both dialogue takes (S02 FITS, S03 overrun +0.280 s kept per owner verdict) and its fallback re-assembly lists both VO takes. Loudness is NOT re-measured in this checkpoint (WO32 item 3 rule); mix loudness figures are cited from their mix manifests only. NOT_AUDITIONED.",
            "Prologue subtitled variant (checkpoint 28, owner request): a VIEWING variant only -- the canonical MP4/OGV keep the checkpoint 27 mix at its measured level (-20.81 LUFS) and the canonical SRT keeps its 6 cues. The variant's +5 dB is a flat presentation gain (no dynamics change, measured -15.83 LUFS / -4.09 dBTP on the variant file), and its readable SRT is a presentation split whose concatenated text is verified identical to the canonical SRT. Burned-in subtitle font is DejaVu Sans (the project has no locked Vietnamese display font, same placeholder status as the title card). No OGV subtitled variant: in-engine subtitle display is the presentation adapter's concern (Codex).",
        ],
    }
    print(f"counts: {json.dumps(COUNTS, indent=1)}")
    print(f"mismatches: {len(ERRORS)}")
    for e in ERRORS[:50]:
        print("  MISMATCH: " + e)
    print(f"notes: {len(NOTES)}")
    for n in NOTES[:20]:
        print("  NOTE: " + n)
    print("verdict: " + result["verdict"])
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report written: {args.out}")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
