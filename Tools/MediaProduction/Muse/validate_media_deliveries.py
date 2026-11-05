#!/usr/bin/env python3
"""MEDIA-02 checkpoint 09 (M7/V4): cross-validate every delivered pack against
real bytes on disk. This tool does NOT re-measure loudness (checkpoints 02/04/
07/08 already measured it from real bytes); it verifies that the files the
packs describe are still the same bytes: existence, LFS-pointer detection,
size, sha256, and ffprobe codec/sample-rate/channels/duration. Timing JSONs
are cross-checked against their SRT files (UTF-8 strict + NFC + cue text and
window equality), and the P0 animatic + P0 VO drafts are probed.

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
    outputs = json.loads((ROOT / "Art_Source/Cinematics/P0_Animatic/P0_animatic_outputs_v2.json").read_text(encoding="utf-8"))
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_audio_packs()
    check_timing_srt()
    check_runtime_cine_manifest()
    check_animatic_vo()
    result = {
        "checkpoint": "MEDIA-02 checkpoint 14 (Gói 30 fix (a): dialogueCues cross-manifest validation)",
        "base_integration": "f383233",
        "branch": "muse/media-production-20261104",
        "counts": COUNTS,
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak values are NOT re-measured here; they come from checkpoints 02/04/07/08, measured from real bytes.",
            "No ear audition of loop seams or VO takes in this validation.",
            "Campaign dialogue windows remain PROPOSED except CIN_001_S05 (DECIDED); this check verifies SRT==timing consistency, not directorial approval.",
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
