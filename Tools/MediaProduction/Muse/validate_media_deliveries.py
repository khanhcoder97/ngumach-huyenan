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
    if len(runtime_clips) != 5:
        err(f"SCENE-CLIPS: runtime manifest has {len(runtime_clips)} "
            f"sceneClips, expected 5")
    for scene_id in ("CIN_001", "CIN_002", "CIN_004", "CIN_006", "CIN_005"):
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
    note(f"Per-scene clips checked: {checked}/5 ({video_scenes} with "
         f"video: P0 x3 panel-hold + CIN_005/CIN_006 animated "
         f"takes); reel tiled 0-72 exactly")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_audio_packs()
    check_timing_srt()
    check_runtime_cine_manifest()
    check_animatic_vo()
    check_keyframes()
    check_cin005_keyframes()
    check_cin006_keyframes()
    check_campaign_vo()
    check_cin006_vo()
    check_p0_mix()
    check_scene_clips()
    result = {
        "checkpoint": "MEDIA-02 checkpoint 22 (CIN_006 animated take: 3 storyboard keyframes + 18 s Ken Burns clip, MP4 + OGV + poster + timing/SRT; CIN_006 leaves PENDING_PANELS_NO_STORYBOARD; runtime delivery revised)",
        "base_integration": "f0859d0",
        "branch": "muse/media-production-20261104",
        "counts": COUNTS,
        "windowFit": {"fits": COUNTS.get("vo_campaign_fits", 0),
                      "overruns": WINDOW_FIT_OVERRUNS},
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak values are NOT re-measured here; they come from checkpoints 02/04/07/08/17/19/20, measured from real bytes.",
            "No ear audition of loop seams or VO takes in this validation.",
            "Campaign dialogue windows remain PROPOSED except CIN_001_S05 (DECIDED); this check verifies SRT==timing consistency, not directorial approval.",
            "Campaign VO window overruns (if any) are director findings, not byte mismatches; see windowFit.",
            "CIN_006 keyframes are STORYBOARD level: NPC_HA_MAC / NPC_SAM_CHU_QUY have no approved character lock, so faces/costumes are placeholders; S02 carries a recorded composition defect for the final-picture revision pass.",
            "CIN_006 alternate take CIN_006_ALT_T01 has no dialogue window by design (DEC-MEDIA-P0 Q3); its absence from the SRT and from the scene timeline is verified, not an omission.",
            "P0 mixes are DRAFT_MIX_NOT_FINAL: this check verifies bytes, durations and the recorded ducking/loop evidence, not the audible balance; no ear audition has been done.",
            "CIN_005 clip motion is animatic-level Ken Burns on still keyframes, not a final pose-animated take; S02 roof palette drifts from S01 (blue-grey vs red), recorded as a known defect for art-direction lock.",
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
