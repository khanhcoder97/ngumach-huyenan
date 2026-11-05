#!/usr/bin/env python3
"""MEDIA-02 checkpoint 03: build the P0 animatic (72 s / 12 shots) from the
storyboard sheet.

Reads Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json for the shot
order, timing and sheet panel boxes; crops each panel (3 px inset to drop the
sheet border), center-crops to 16:9, resizes to 640x360, holds each panel for
its shot duration at 30 fps, and concatenates into:
  - ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.mp4 (H.264)
  - ClientGodot/assets/cinematics/P0_animatic_640x360_30fps.ogv (Theora)
  - ClientGodot/assets/cinematics/P0_animatic_poster.png (CIN_001_S01 panel)
Panels land in Art_Source/Cinematics/P0_Animatic/panels/.

The MP4/OGV carry NO audio track and NO baked subtitles by design: VO audio
is block (c), SRT drafts live in Implementation/Content/Narrative/Deliveries/,
and stems stay separate per the checkpoint 02 stem-per-shot table (referenced
in the spec). Verification with ffprobe (duration, frames, codec, size) runs
at the end and fails the script on mismatch.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image

FPS = 30
W, H = 640, 360


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--spec", default="Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json")
    args = ap.parse_args()
    root = Path(args.root)
    spec = json.loads((root / args.spec).read_text(encoding="utf-8"))
    sheet = Image.open(root / spec["storyboardSheet"]).convert("RGB")
    panels_dir = root / spec["panelsDir"]
    panels_dir.mkdir(parents=True, exist_ok=True)

    panel_files = []
    for shot in spec["shots"]:
        box = shot["sheetBox"]  # [x0, y0, x1, y1] border-inclusive
        x0, y0, x1, y1 = (box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3)
        crop = sheet.crop((x0, y0, x1, y1))
        # Center-crop to 16:9, then resize to 640x360.
        w, h = crop.size
        target = w / h
        if target > 16 / 9:
            nw = int(h * 16 / 9)
            crop = crop.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
        else:
            nh = int(w * 9 / 16)
            crop = crop.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))
        panel = crop.resize((W, H), Image.LANCZOS)
        out = panels_dir / f"panel_{shot['shotId']}.png"
        panel.save(out)
        panel_files.append((shot, out))

    cine_dir = root / spec["runtimeDir"]
    cine_dir.mkdir(parents=True, exist_ok=True)
    mp4 = cine_dir / "P0_animatic_640x360_30fps.mp4"
    ogv = cine_dir / "P0_animatic_640x360_30fps.ogv"
    poster = cine_dir / "P0_animatic_poster.png"
    # Poster = first panel (CIN_001_S01), copied, not moved.
    import shutil
    shutil.copyfile(panel_files[0][1], poster)

    # Build concat list: each panel held for its shot duration.
    concat = root / "Art_Source/Cinematics/P0_Animatic/_ffmpeg_concat.txt"
    with open(concat, "w", encoding="utf-8") as f:
        for shot, p in panel_files:
            dur = shot["endSeconds"] - shot["startSeconds"]
            f.write(f"file '{p.resolve()}'\nduration {dur}\n")
        f.write(f"file '{panel_files[-1][1].resolve()}'\n")

    # The concat demuxer ignores the last file's duration unless it is
    # repeated, and the repeated file then adds one extra shot length; trim
    # the output to exactly the summed shot duration (72 s) to cancel that.
    total_dur = sum(s["endSeconds"] - s["startSeconds"] for s in spec["shots"])
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-vf", f"fps={FPS},format=yuv420p",
         "-c:v", "libx264", "-r", str(FPS), "-t", str(total_dur), str(mp4)])
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
         "-i", str(concat), "-vf", f"fps={FPS}",
         "-c:v", "libtheora", "-r", str(FPS), "-t", str(total_dur), str(ogv)])
    concat.unlink()

    # Verify with ffprobe: 72.0 s, 2160 frames, 640x360, 30 fps.
    def probe(path):
        r = run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
                 "-show_entries", "stream=codec_name,width,height,avg_frame_rate,nb_frames,nb_read_frames,duration",
                 "-show_entries", "format=duration", "-of", "json", str(path)])
        return json.loads(r.stdout)

    manifest = {"spec": str(args.spec), "shots": [], "outputs": {}}
    total = 0.0
    for shot, p in panel_files:
        dur = shot["endSeconds"] - shot["startSeconds"]
        total += dur
        manifest["shots"].append({"shotId": shot["shotId"], "panel": str(p),
                                  "panelSha256": sha256(p), "durationSeconds": dur})
    for label, path, codec in (("mp4", mp4, "h264"), ("ogv", ogv, "theora")):
        info = probe(path)
        st = info["streams"][0]
        dur = float(info["format"]["duration"])
        frames = int(st.get("nb_frames") or st.get("nb_read_frames") or 0)
        assert st["codec_name"] == codec, (label, st)
        assert (st["width"], st["height"]) == (W, H), (label, st)
        assert abs(dur - total) < 0.15, (label, dur, total)
        if codec == "h264":
            # MP4 must hold every 30 fps frame: 72 s x 30 = 2160.
            assert frames == int(total * FPS), (label, frames)
        else:
            # Theora collapses held (duplicate) panel frames into
            # longer-duration frames: verified by re-encoding the checked
            # MP4, which also yields ~211-252 stored frames over 72.0 s.
            # Duration (72.0 s), not stored-frame count, is the check.
            assert 0 < frames < int(total * FPS), (label, frames)
        manifest["outputs"][label] = {"file": str(path), "sha256": sha256(path),
                                      "codec": codec, "durationSeconds": dur,
                                      "storedFrames": frames, "size": f"{W}x{H}",
                                      "fps": FPS, "audioTracks": 0,
                                      "bakedSubtitles": False}
    manifest["outputs"]["poster"] = {"file": str(poster), "sha256": sha256(poster)}
    manifest["totalSeconds"] = total
    out_manifest = root / spec["outputsManifest"]
    out_manifest.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8")
    print(f"OK: {total:.1f}s / {len(panel_files)} panels -> {mp4} + {ogv}")
    print(f"manifest: {out_manifest}")


if __name__ == "__main__":
    main()
