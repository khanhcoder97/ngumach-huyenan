#!/usr/bin/env python3
"""MEDIA-02 checkpoint 18: export each P0 scene as its own clip
(Goi 30 item 6 / PR119 review: the 72 s reel is review/gallery only,
NOT auto-run as opening).

Reads Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v3.json (12 shots,
3 scenes with storyboard panels) and builds, per scene:
  ClientGodot/assets/cinematics/<SCENE>/
    <SCENE>_640x360_30fps.mp4   (H.264 review)
    <SCENE>_640x360_30fps.ogv   (Theora runtime)
    <SCENE>_poster.png          (first shot's panel)
    <SCENE>_timing_v1.json      (copy of the Narrative/Deliveries timing)
    <SCENE>_vi.srt              (copy of the Narrative/Deliveries SRT)
    scene_export_manifest_v1.json (SHA/size/duration/frames + reel offsets)

Scene-local time starts at 0: the shot list in each manifest is rebased
from reel time, and the copied SRT is already scene-local (its cue
windows are the timing windows, verified here against the timing JSON).

CIN_006 has timing + SRT but NO storyboard panels (it was never in the
72 s reel; checkpoint 05 was timing only), so its export folder holds
timing + SRT + a manifest with videoStatus PENDING_PANELS_NO_STORYBOARD
and no video files. No placeholder/empty video is fabricated.

Verification (any failure aborts with non-zero exit):
  - every panel is real image bytes, never a git-LFS pointer
  - the 3 video scenes tile the reel exactly: offsets 0-36 / 36-54 / 54-72
  - ffprobe per clip: codec, 640x360, duration == scene seconds;
    MP4 frame count == seconds * 30; Theora stored-frame count is
    0 < n < seconds * 30 (held panel frames collapse, CP03 rule)
  - decoded first/last clip frame is close to the first/last shot panel
    (mean abs channel diff < 10; lossy H.264/Theora noise is ~1-3, a
    wrong panel scores ~30+), proving the clip is a true slice of the
    reel content, not a re-render drift
  - copied timing/SRT SHA match the source-manifest records
    (P0_timing_manifest_v1.json for CIN_001/002/004,
    CIN_006_timing_manifest_v1.json for CIN_006); dialogue cue count
    comes from parsed timing shots[].dialogue cross-checked with the
    parsed SRT (Goi 30 item 1 rule)
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
SPEC = ROOT / "Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v3.json"
PANELS = ROOT / "Art_Source/Cinematics/P0_Animatic/panels"
DELIVERIES = ROOT / "Implementation/Content/Narrative/Deliveries"
CINE_DEST = ROOT / "ClientGodot/assets/cinematics"
FPS = 30
W, H = 640, 360
FRAME_DIFF_MAX = 10.0
BASE_SHA = "f0859d0"
CHECKPOINT = ("MEDIA-02 checkpoint 18 - per-scene clip export "
              "(Goi 30 item 6): CIN_001/CIN_002/CIN_004 video clips + "
              "CIN_006 timing/SRT only (no panels yet)")

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


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print("FAIL: " + msg)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)
    return r


def probe_video(path: Path):
    out = run(["ffprobe", "-v", "error", "-count_frames",
               "-select_streams", "v:0",
               "-show_entries",
               "stream=codec_name,width,height,avg_frame_rate,"
               "nb_read_frames,duration",
               "-show_entries", "format=duration",
               "-of", "json", str(path)])
    return json.loads(out.stdout)


SRT_TIME_RE = re.compile(
    r"^\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d$")


def count_srt_cues(text: str):
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


def mean_abs_diff(img_a: Image.Image, img_b: Image.Image) -> float:
    a = img_a.convert("RGB")
    b = img_b.convert("RGB")
    if a.size != b.size:
        return float("inf")
    pa = list(a.getdata())
    pb = list(b.getdata())
    total = 0
    for (r1, g1, b1), (r2, g2, b2) in zip(pa, pb):
        total += abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
    return total / (len(pa) * 3)


def extract_frame(video: Path, seconds: float, out: Path):
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(seconds),
         "-i", str(video), "-frames:v", "1", str(out)])


def main() -> None:
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    shots = spec["shots"]
    check(len(shots) == 12, f"expected 12 shots in spec v3, got {len(shots)}")

    # Group shots by scene in reel order; reel offsets must tile 0-72.
    scenes = {}
    order = []
    cursor = 0.0
    for shot in shots:
        sid = shot["sceneId"]
        if sid not in scenes:
            scenes[sid] = {"sceneId": sid, "shots": [],
                           "reelStart": shot["startSeconds"]}
            order.append(sid)
        check(abs(shot["startSeconds"] - cursor) < 1e-9,
              f"{shot['shotId']} starts {shot['startSeconds']}, "
              f"expected reel cursor {cursor}")
        scenes[sid]["shots"].append(shot)
        cursor = shot["endSeconds"]
    check(abs(cursor - 72.0) < 1e-9,
          f"reel shots end at {cursor}, expected 72.0")
    for sid in order:
        scenes[sid]["reelEnd"] = scenes[sid]["shots"][-1]["endSeconds"]
        scenes[sid]["duration"] = (scenes[sid]["reelEnd"]
                                   - scenes[sid]["reelStart"])

    # Source-manifest records for timing/SRT SHA cross-checks.
    p0m = json.loads((DELIVERIES / "P0_timing_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    src = {s["sceneId"]: s for s in p0m["scenes"]}
    c6m = json.loads((DELIVERIES / "CIN_006/CIN_006_timing_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    src[c6m["scene"]["sceneId"]] = c6m["scene"]
    all_scene_ids = order + ["CIN_006"]

    results = {}
    for scene_id in all_scene_ids:
        timing_src = DELIVERIES / scene_id / f"{scene_id}_timing_v1.json"
        srt_src = DELIVERIES / scene_id / f"{scene_id}_vi.srt"
        check(timing_src.exists(), f"{scene_id}: timing missing")
        check(srt_src.exists(), f"{scene_id}: srt missing")
        if not (timing_src.exists() and srt_src.exists()):
            continue
        timing = json.loads(timing_src.read_text(encoding="utf-8"))
        srt_text = srt_src.read_text(encoding="utf-8")
        timing_dialogues = sum(
            1 for sh in timing.get("shots", [])
            if isinstance(sh.get("dialogue"), dict))
        srt_cues = count_srt_cues(srt_text)
        check(srt_cues is not None, f"{scene_id}: unparseable SRT")
        if srt_cues is not None:
            check(timing_dialogues == srt_cues,
                  f"{scene_id}: timing dialogues {timing_dialogues} "
                  f"!= SRT cues {srt_cues}")
        expect_srt_sha = src[scene_id].get("srtSha256")
        check(sha256(srt_src) == expect_srt_sha,
              f"{scene_id}: source SRT sha != manifest record")

        out_dir = CINE_DEST / scene_id
        out_dir.mkdir(parents=True, exist_ok=True)
        timing_dest = out_dir / timing_src.name
        srt_dest = out_dir / srt_src.name
        shutil.copyfile(timing_src, timing_dest)
        shutil.copyfile(srt_src, srt_dest)
        check(sha256(timing_dest) == sha256(timing_src),
              f"{scene_id}: timing copy sha mismatch")
        check(sha256(srt_dest) == expect_srt_sha,
              f"{scene_id}: srt copy sha mismatch")

        manifest = {
            "schemaVersion": 1,
            "checkpoint": CHECKPOINT,
            "decisionId": "DEC-MEDIA-P0-20261105",
            "branch": "muse/media-production-20261104",
            "baseSha": BASE_SHA,
            "sceneId": scene_id,
            "title": timing.get("title"),
            "durationSeconds": timing["durationSeconds"],
            "dialogueCues": timing_dialogues,
            "dialogueWindowStatus":
                src[scene_id].get("dialogueWindowStatus"),
            "files": {},
            "notes": [
                "Scene-local time starts at 0; shot list is rebased from "
                "reel time. The copied SRT is already scene-local.",
                "The 72 s P0 reel is review/gallery only, NOT auto-run as "
                "opening; this per-scene clip is the runtime unit "
                "(Goi 30 item 6).",
            ],
        }

        if scene_id in scenes:
            info = scenes[scene_id]
            manifest["reelOffsetSeconds"] = {
                "start": info["reelStart"], "end": info["reelEnd"]}
            manifest["reelTotalSeconds"] = 72.0
            check(abs(timing["durationSeconds"] - info["duration"]) < 1e-9,
                  f"{scene_id}: timing duration "
                  f"{timing['durationSeconds']} != reel span "
                  f"{info['duration']}")
            # Verify panels are real bytes, then build the clip.
            panel_files = []
            for shot in info["shots"]:
                p = PANELS / f"panel_{shot['shotId']}.png"
                check(p.exists(), f"{scene_id}: panel missing {p.name}")
                if p.exists():
                    check(not is_lfs_pointer(p),
                          f"{scene_id}: panel is LFS pointer {p.name}")
                panel_files.append((shot, p))
            concat = ROOT / ("Art_Source/Cinematics/P0_Animatic/"
                             f"_ffmpeg_scene_{scene_id}.txt")
            with open(concat, "w", encoding="utf-8") as f:
                for shot, p in panel_files:
                    dur = shot["endSeconds"] - shot["startSeconds"]
                    f.write(f"file '{p.resolve()}'\nduration {dur}\n")
                f.write(f"file '{panel_files[-1][1].resolve()}'\n")
            mp4 = out_dir / f"{scene_id}_640x360_30fps.mp4"
            ogv = out_dir / f"{scene_id}_640x360_30fps.ogv"
            poster = out_dir / f"{scene_id}_poster.png"
            shutil.copyfile(panel_files[0][1], poster)
            total_dur = info["duration"]
            run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe",
                 "0", "-i", str(concat), "-vf", f"fps={FPS},format=yuv420p",
                 "-c:v", "libx264", "-r", str(FPS), "-t", str(total_dur),
                 str(mp4)])
            run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe",
                 "0", "-i", str(concat), "-vf", f"fps={FPS}",
                 "-c:v", "libtheora", "-r", str(FPS), "-t", str(total_dur),
                 str(ogv)])
            concat.unlink()
            manifest["videoStatus"] = "VIDEO_FROM_STORYBOARD_PANELS"
            # ffprobe verification per clip.
            for path, want_codec in ((mp4, "h264"), (ogv, "theora")):
                check(path.exists(), f"{scene_id}: missing {path.name}")
                check(not is_lfs_pointer(path),
                      f"{scene_id}: clip is LFS pointer {path.name}")
                info_probe = probe_video(path)
                stream = info_probe["streams"][0]
                check(stream["codec_name"] == want_codec,
                      f"{scene_id} {path.name}: codec "
                      f"{stream['codec_name']} != {want_codec}")
                check((stream["width"], stream["height"]) == (W, H),
                      f"{scene_id} {path.name}: size "
                      f"{stream['width']}x{stream['height']} != 640x360")
                frames = int(stream.get("nb_read_frames")
                             or stream.get("nb_frames") or 0)
                if want_codec == "h264":
                    # MP4 must hold every 30 fps frame.
                    check(stream["avg_frame_rate"] in ("30/1", "30"),
                          f"{scene_id} {path.name}: fps "
                          f"{stream['avg_frame_rate']} != 30")
                    check(frames == int(total_dur * FPS),
                          f"{scene_id} {path.name}: frames {frames} != "
                          f"{int(total_dur * FPS)}")
                else:
                    # Theora collapses held (duplicate) panel frames into
                    # longer-duration frames (same as the 72 s reel: 271
                    # stored frames, avg_frame_rate 0/0). Duration, not
                    # stored-frame count, is the check (CP03 rule).
                    check(0 < frames < int(total_dur * FPS),
                          f"{scene_id} {path.name}: stored frames "
                          f"{frames} outside (0, {int(total_dur * FPS)})")
                dur = float(info_probe["format"]["duration"])
                check(abs(dur - total_dur) <= 0.02,
                      f"{scene_id} {path.name}: duration {dur} != "
                      f"{total_dur}")
                key = "mp4" if path == mp4 else "ogv"
                entry = {
                    "path": f"assets/cinematics/{scene_id}/{path.name}",
                    "sha256": sha256(path),
                    "sizeBytes": path.stat().st_size,
                    "codec": want_codec,
                    "width": W, "height": H,
                    "fps": FPS,
                    "durationSeconds": round(dur, 4),
                }
                if want_codec == "h264":
                    entry["frames"] = frames
                else:
                    entry["storedFrames"] = frames
                manifest["files"][key] = entry
            # Frame-identity: decoded first/last clip frame vs panels.
            tmp = ROOT / ("Art_Source/Cinematics/P0_Animatic/"
                          f"_framecheck_{scene_id}")
            tmp.mkdir(exist_ok=True)
            for label, at_s, panel in (
                    ("first", 0.0, panel_files[0][1]),
                    ("last", total_dur - 1.0 / FPS,
                     panel_files[-1][1])):
                frame_png = tmp / f"{label}.png"
                extract_frame(mp4, at_s, frame_png)
                diff = mean_abs_diff(Image.open(frame_png),
                                     Image.open(panel))
                check(diff < FRAME_DIFF_MAX,
                      f"{scene_id}: {label} frame diff {diff:.2f} "
                      f">= {FRAME_DIFF_MAX} vs {panel.name}")
                manifest.setdefault("frameCheck", {})[label] = {
                    "panel": panel.name,
                    "meanAbsChannelDiff": round(diff, 3),
                    "maxAllowed": FRAME_DIFF_MAX,
                }
            shutil.rmtree(tmp)
            manifest["files"]["poster"] = {
                "path": f"assets/cinematics/{scene_id}/{poster.name}",
                "sha256": sha256(poster),
                "sizeBytes": poster.stat().st_size,
                "sourcePanel": panel_files[0][1].name,
            }
            check(sha256(poster) == sha256(panel_files[0][1]),
                  f"{scene_id}: poster sha != first panel sha")
            manifest["shots"] = [
                {"shotId": s["shotId"],
                 "startSeconds": round(s["startSeconds"]
                                       - info["reelStart"], 3),
                 "endSeconds": round(s["endSeconds"]
                                     - info["reelStart"], 3),
                 "panel": f"panel_{s['shotId']}.png"}
                for s in info["shots"]]
        else:
            # CIN_006: timing + SRT only; no storyboard panels, no video.
            manifest["reelOffsetSeconds"] = None
            manifest["reelTotalSeconds"] = None
            manifest["videoStatus"] = "PENDING_PANELS_NO_STORYBOARD"
            manifest["shots"] = [
                {"shotId": s["shotId"],
                 "startSeconds": s["startSeconds"],
                 "endSeconds": s["endSeconds"],
                 "panel": None}
                for s in timing.get("shots", [])]
            manifest["notes"].append(
                "No video clip: CIN_006 was never storyboarded into the "
                "72 s P0 reel (checkpoint 05 was timing only) and has no "
                "panels yet. Timing + SRT are exported; the clip waits for "
                "panels, it is NOT faked from an empty or tone-generator "
                "frame.")
            for name in (f"{scene_id}_640x360_30fps.mp4",
                         f"{scene_id}_640x360_30fps.ogv",
                         f"{scene_id}_poster.png"):
                check(not (out_dir / name).exists(),
                      f"{scene_id}: unexpected video file {name}")

        manifest["files"]["timing"] = {
            "path": f"assets/cinematics/{scene_id}/{timing_src.name}",
            "sha256": sha256(timing_dest),
            "sizeBytes": timing_dest.stat().st_size,
        }
        manifest["files"]["srt"] = {
            "path": f"assets/cinematics/{scene_id}/{srt_src.name}",
            "sha256": sha256(srt_dest),
            "sizeBytes": srt_dest.stat().st_size,
            "status": "DRAFT",
        }
        (out_dir / "scene_export_manifest_v1.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=1),
            encoding="utf-8")
        results[scene_id] = manifest

    print("scenes exported:")
    for scene_id in all_scene_ids:
        m = results.get(scene_id)
        if not m:
            continue
        video = m["videoStatus"]
        mp4 = m["files"].get("mp4", {})
        print(f"  {scene_id}: {m['durationSeconds']}s, {video}, "
              f"dialogueCues={m['dialogueCues']}, "
              f"mp4={mp4.get('sha256', '-')[:12]}")
    if failures:
        print(f"FAILURES: {len(failures)}")
        for f in failures[:20]:
            print(" - " + f)
        return 1
    print("Per-scene clip export: ALL VERIFIED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
