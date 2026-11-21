#!/usr/bin/env python3
"""WO37 M-C checkpoint 2: P0 motion/AB pack v1 (12 P0 shots).

Reads Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_SPEC_v1.json
and builds, for every P0 shot, a pose-animation take at 10 pose fps
(5 poses, each held 3 output frames at 30 fps = 0.5 s action beat;
keyframe hold before the beat, last pose held after; 6 s per shot):

  Art_Source/Cinematics/P0_Motion/pose_frames/<SHOT>/pose_01..05.png
  Art_Source/Cinematics/P0_Motion/takes/<SHOT>_pose_640x360_30fps.mp4 (silent)
  Art_Source/Cinematics/P0_Motion/takes/<SCENE>_pose_640x360_30fps.mp4 (v3 mix audio)
  Art_Source/Cinematics/P0_Motion/ab/<SCENE>_ab_kenburns_vs_pose_640x720_30fps.mp4
  Art_Source/Cinematics/P0_Motion/contact/<SHOT>_contact.png
  Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json (manifest)

Pose routes (per spec):
  - procedural: pose frames rendered by code from the storyboard keyframe
    (deterministic rain / ripple / drip / drops / bob / sway / advance /
    pull / mask-sweep / splash / debris layers). No generated pixels.
    (The generated-strip route was tried and abandoned: every generated
    strip is a panorama with the subject repeated, not 8 separate frames;
    see the spec's rejectedStrips list.)

A/B: A = existing runtime Ken Burns take (video stream, v3 mix audio);
B = pose-animation scene take (same v3 mix audio). The runtime files are
NOT replaced; this is a review pack. Status DRAFT_POSE_ANIMATION:
storyboard-level motion draft, final picture still waits on character lock.

Usage:
  python3 build_p0_motion_ab_v1.py [--root .] [--debug-boxes]
--debug-boxes only renders the procedural-box overlay sheet to /tmp and exits.
Every measurement is recomputed from bytes on disk; the builder FAILS on:
  - pose count != 5, take frames != 180, scene duration mismatch
  - inter-pose mean abs channel diff outside (0.15, 30) procedural /
    (5, 100) generated (frozen / duplicate / garbage); generated panels are
    full redraws, so their background boil is measured separately
    (redrawBoilBackgroundDiff) and flagged as defect D-MC-01, not failed
  - pose1 vs keyframe diff >= 10 (procedural) / >= 100 (generated)
  - mix duration != scene duration, A/B size != 640x720
"""
import argparse
import hashlib
import json
import random
import subprocess
import sys
import tempfile
from collections import deque
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

W, H = 640, 360
FPS = 30
FRAMES_PER_SHOT = 180
POSES = 5
FRAMES_PER_POSE = 3
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)
    return r


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    st = ImageStat.Stat(d)
    return round(sum(st.mean) / 3.0, 3)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- layers
def apply_rain(img: Image.Image, k: int, count: int, seed: int, dy: int) -> Image.Image:
    rng = random.Random(seed)
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for _ in range(count):
        x = rng.randint(0, W - 1)
        y0 = rng.randint(0, H - 1)
        ln = rng.randint(10, 16)
        y = (y0 + k * dy) % H
        dr.line([(x, y), (x - 2, y + ln)], fill=(205, 215, 230, 110), width=1)
    return Image.alpha_composite(base, ov).convert("RGB")


def apply_ripples(img: Image.Image, k: int, centers, growth: int) -> Image.Image:
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for (cx, cy, r0) in centers:
        r = r0 + k * growth
        dr.ellipse([cx - r, cy - r * 0.35, cx + r, cy + r * 0.35],
                   outline=(190, 205, 225, 150), width=2)
        r2 = max(2, int(r * 0.55))
        dr.ellipse([cx - r2, cy - r2 * 0.35, cx + r2, cy + r2 * 0.35],
                   outline=(190, 205, 225, 80), width=1)
    return Image.alpha_composite(base, ov).convert("RGB")


def apply_drip(img: Image.Image, k: int, x: int, y0: int, growth: int) -> Image.Image:
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    ln = 10 + k * growth
    dr.line([(x, y0), (x, y0 + ln)], fill=(200, 215, 230, 170), width=2)
    dr.ellipse([x - 2 - k, y0 + ln - 2 - k, x + 2 + k, y0 + ln + 2 + k],
               fill=(200, 215, 230, 170))
    return Image.alpha_composite(base, ov).convert("RGB")


def apply_drops(img: Image.Image, k: int, centers, r0: float, growth: float) -> Image.Image:
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for (cx, cy) in centers:
        r = r0 + k * growth
        dr.ellipse([cx - r, cy - r * 0.7, cx + r, cy + r * 0.7],
                   fill=(205, 220, 235, 200), outline=(120, 140, 160, 200))
    return Image.alpha_composite(base, ov).convert("RGB")


def shift_box(img: Image.Image, box, dx: int, dy: int) -> Image.Image:
    """Translate a box's content by (dx, dy); fill the exposed strip by
    replicating the nearest edge row/column of the moved content."""
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    out = img.copy()
    content = img.crop((x0, y0, x1, y1))
    out.paste(content, (x0 + dx, y0 + dy))
    if dy > 0:  # exposed strip at top: replicate first content row
        strip = content.crop((0, 0, w, 1)).resize((w, dy), Image.NEAREST)
        out.paste(strip, (x0, y0))
    elif dy < 0:
        strip = content.crop((0, h - 1, w, h)).resize((w, -dy), Image.NEAREST)
        out.paste(strip, (x0, y1 + dy))
    if dx > 0:  # exposed strip at left: replicate first content column
        strip = content.crop((0, 0, 1, h)).resize((dx, h), Image.NEAREST)
        out.paste(strip, (x0, y0))
    elif dx < 0:
        strip = content.crop((w - 1, 0, w, h)).resize((-dx, h), Image.NEAREST)
        out.paste(strip, (x0 + w + dx, y0))
    return out


def _color_dist(c1, c2) -> float:
    return ((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2 + (c1[2] - c2[2]) ** 2) ** 0.5


def build_advance_mask(kf: Image.Image, seed, region):
    """Flood-fill the serpent mask from a seed pixel: pixels within color
    distance 48 of the sampled spine palette, inside region, 4-connected."""
    px = kf.load()
    sx, sy = seed
    pts = [(sx, sy), (sx, sy - 50), (sx, sy + 50), (sx, sy - 90), (sx, sy + 90),
           (sx - 20, sy), (sx + 20, sy), (sx - 5, sy - 30), (sx + 5, sy + 70)]
    palette = [px[x, y] for (x, y) in pts]
    x0, y0, x1, y1 = region

    def is_serpent(x, y):
        if not (x0 <= x < x1 and y0 <= y < y1):
            return False
        c = px[x, y]
        return min(_color_dist(c, p) for p in palette) < 48

    mask = set()
    dq = deque([(sx, sy)])
    seen = {(sx, sy)}
    while dq:
        x, y = dq.popleft()
        if not is_serpent(x, y):
            continue
        mask.add((x, y))
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                dq.append((nx, ny))
    return mask


def apply_advance(img: Image.Image, k: int, mask, dy: int, fill_below: int) -> Image.Image:
    out = img.copy()
    px_src = img.load()
    px_out = out.load()
    moved = set()
    for (x, y) in mask:
        ny = y - dy
        if 0 <= ny < H:
            px_out[x, ny] = px_src[x, y]
            moved.add((x, ny))
    # Vacated pixels: mask pixels not covered by the moved serpent.
    for (x, y) in mask:
        if (x, y) not in moved:
            fy = min(y + fill_below, H - 1)
            px_out[x, y] = px_src[x, fy]
    return out


def build_color_mask(kf: Image.Image, seed_points, region, threshold: float = 48):
    """Flood-fill a mask from seed_points[0]: pixels within `threshold` of
    the sampled palette, inside region, 4-connected. Used for maskSweep."""
    seed_points = [tuple(p) for p in seed_points]
    px = kf.load()
    palette = [px[x, y] for (x, y) in seed_points]
    x0, y0, x1, y1 = region

    def is_member(x, y):
        if not (x0 <= x < x1 and y0 <= y < y1):
            return False
        c = px[x, y]
        return min(_color_dist(c, p) for p in palette) < threshold

    mask = set()
    dq = deque([seed_points[0]])
    seen = {seed_points[0]}
    while dq:
        x, y = dq.popleft()
        if not is_member(x, y):
            continue
        mask.add((x, y))
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if (nx, ny) not in seen:
                seen.add((nx, ny))
                dq.append((nx, ny))
    return mask


def apply_mask_translate(img: Image.Image, mask, dx: int, dy: int) -> Image.Image:
    """Translate a masked subject by (dx, dy); vacated pixels are filled by
    scanning from the trailing edge toward the nearest non-mask pixel."""
    out = img.copy()
    px_src = img.load()
    px_out = out.load()
    moved = set()
    for (x, y) in mask:
        nx, ny = x + dx, y + dy
        if 0 <= nx < W and 0 <= ny < H:
            px_out[nx, ny] = px_src[x, y]
            moved.add((nx, ny))
    if dx != 0:
        step = (-1, 0) if dx > 0 else (1, 0)
    else:
        step = (0, -1) if dy > 0 else (0, 1)
    for (x, y) in mask:
        if (x, y) in moved:
            continue
        found = None
        for d in range(1, 25):
            cx, cy = x + step[0] * d, y + step[1] * d
            if not (0 <= cx < W and 0 <= cy < H):
                break
            if (cx, cy) not in mask:
                found = (cx, cy)
                break
        if found is not None:
            px_out[x, y] = px_src[found[0], found[1]]
        else:
            px_out[x, y] = px_src[x, min(y + 16, H - 1)]
    return out


def apply_splash(img: Image.Image, k: int, centers, seed: int) -> Image.Image:
    """White radial splash streaks around centers; length grows with k."""
    rng = random.Random(seed)
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    import math
    for (cx, cy) in centers:
        for _ in range(6):
            ang = rng.uniform(0, 6.283)
            ln = 6 + k * 4 + rng.randint(0, 4)
            x1 = cx + int(8 * math.cos(ang))
            y1 = cy + int(8 * math.sin(ang) * 0.5)
            x2 = cx + int((8 + ln) * math.cos(ang))
            y2 = cy + int((8 + ln) * math.sin(ang) * 0.5)
            dr.line([(x1, y1), (x2, y2)], fill=(220, 230, 240, 170), width=2)
    return Image.alpha_composite(base, ov).convert("RGB")


def apply_debris(img: Image.Image, k: int, starts) -> Image.Image:
    """Small tan debris rects flying outward: [x, y, w, h, vx, vy] per piece."""
    base = img.convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    for (x0, y0, w, h, vx, vy) in starts:
        x, y = x0 + k * vx, y0 + k * vy
        dr.rectangle([x, y, x + w, y + h], fill=(176, 157, 132, 255))
    return Image.alpha_composite(base, ov).convert("RGB")


def render_procedural_pose(kf: Image.Image, layers, k: int, mask_cache: dict) -> Image.Image:
    img = kf
    for layer in layers:
        t = layer["type"]
        if t == "rain":
            img = apply_rain(img, k, layer["count"], layer["seed"], layer["dyPerPose"])
        elif t == "ripples":
            img = apply_ripples(img, k, layer["centers"], layer["growth"])
        elif t == "drip":
            img = apply_drip(img, k, layer["x"], layer["y0"], layer["growth"])
        elif t == "drops":
            img = apply_drops(img, k, layer["centers"], layer["r0"], layer["growth"])
        elif t == "bob":
            img = shift_box(img, layer["box"], 0, layer["dy"][k])
        elif t == "sway":
            img = shift_box(img, layer["box"], 0, layer["dy"][k])
        elif t == "swayX":
            for box in layer["boxes"]:
                img = shift_box(img, box, layer["dx"][k], 0)
        elif t == "pull":
            img = shift_box(img, layer["parcelBox"], layer["parcelDx"][k], 0)
            img = shift_box(img, layer["armBox"], layer["armDx"][k], 0)
        elif t == "advance":
            key = "advance"
            if key not in mask_cache:
                mask_cache[key] = build_advance_mask(
                    kf, layer["seed"], layer["region"])
            img = apply_advance(img, k, mask_cache[key], layer["dy"][k],
                                layer["fillBelow"])
        elif t == "maskSweep":
            key = "sweep"
            if key not in mask_cache:
                mask_cache[key] = build_color_mask(
                    kf, layer["seedPoints"], layer["region"])
                mask_cache["sweepPixels"] = len(mask_cache[key])
            img = apply_mask_translate(img, mask_cache[key],
                                       layer["dx"][k], layer["dy"][k])
        elif t == "splash":
            img = apply_splash(img, k, layer["centers"], layer["seed"])
        elif t == "debris":
            img = apply_debris(img, k, layer["starts"])
        else:
            raise ValueError(f"unknown layer type {t!r}")
    return img


# ---------------------------------------------------------------- strips
def cut_strip_cells(strip_path: Path, panels):
    """Cut the requested panels (0-indexed) from a strip into 640x360 poses.
    Returns (poses, transform, cell_size)."""
    strip = Image.open(strip_path).convert("RGB")
    sw, sh = strip.size
    cw = sw // 8
    poses = []
    for p in panels:
        cell = strip.crop((p * cw, 0, (p + 1) * cw, sh))
        ar = cell.size[0] / cell.size[1]
        target = 16 / 9
        if abs(ar - target) / target < 0.01:
            pose = cell.resize((W, H), Image.NEAREST)
            transform = "resize-direct-nearest"
        elif ar > target:  # too wide: center-crop height
            nh = int(cell.size[0] / target)
            top = (cell.size[1] - nh) // 2
            pose = cell.crop((0, top, cell.size[0], top + nh)).resize((W, H), Image.NEAREST)
            transform = f"center-crop-height-{nh}"
        else:  # too narrow: fit height, edge-replicate pad sides
            nh = H
            nw = int(cell.size[0] * nh / cell.size[1])
            scaled = cell.resize((nw, nh), Image.NEAREST)
            pose = Image.new("RGB", (W, H))
            pad = (W - nw) // 2
            left = scaled.crop((0, 0, 1, H)).resize((pad, H), Image.NEAREST)
            right = scaled.crop((nw - 1, 0, nw, H)).resize((W - nw - pad, H), Image.NEAREST)
            pose.paste(left, (0, 0))
            pose.paste(scaled, (pad, 0))
            pose.paste(right, (pad + nw, 0))
            transform = f"fit-height-pad-{pad}-{W - nw - pad}"
        poses.append(pose)
    return poses, transform, (cw, sh)

# ---------------------------------------------------------------- build
def debug_boxes(root: Path, spec: dict) -> None:
    """Render one overlay sheet: every procedural box on its keyframe."""
    tiles = []
    for s in spec["shots"]:
        if s["route"] != "procedural":
            continue
        kf = Image.open(root / s["keyframe"]["file"]).convert("RGB")
        dr = ImageDraw.Draw(kf)
        for layer in s["layers"]:
            boxes = []
            if layer["type"] in ("bob", "sway"):
                boxes = [layer["box"]]
            elif layer["type"] == "swayX":
                boxes = layer["boxes"]
            elif layer["type"] == "pull":
                boxes = [layer["parcelBox"], layer["armBox"]]
            elif "box" in layer:
                boxes = [layer["box"]]
            for b in boxes:
                dr.rectangle(b, outline=(255, 0, 0), width=3)
        tiles.append((s["shotId"], kf))
    sheet = Image.new("RGB", (W, len(tiles) * (H // 2 + 20)), (255, 255, 255))
    dr = ImageDraw.Draw(sheet)
    for i, (sid, tile) in enumerate(tiles):
        small = tile.resize((W // 2, H // 2), Image.NEAREST)
        y = i * (H // 2 + 20)
        sheet.paste(small, (0, y + 20))
        dr.text((4, y + 2), sid, fill=(0, 0, 0))
    out = Path("/tmp/p0_motion_boxes.png")
    sheet.save(out)
    print("debug boxes ->", out, sheet.size)


def prepare_poses(root: Path, spec: dict):
    """Render/cut all pose frames. Returns per-shot pose records."""
    poses_dir = root / "Art_Source/Cinematics/P0_Motion/pose_frames"
    records = {}
    for s in spec["shots"]:
        sid = s["shotId"]
        kf = Image.open(root / s["keyframe"]["file"]).convert("RGB")
        assert kf.size == (W, H), f"{sid}: keyframe size {kf.size}"
        out_dir = poses_dir / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        if s["route"] == "generated_strip":
            st = s["strip"]
            strip_path = root / st["file"]
            assert sha256(strip_path) == st["stripPngSha256"], f"{sid}: strip SHA mismatch"
            poses, transform, cell = cut_strip_cells(strip_path, st["panels"])
            extra = {"stripFile": st["file"], "stripAttempt": st["attempt"],
                     "stripPanels": st["panels"], "stripCellSize": list(cell),
                     "stripTransform": transform,
                     "stripSha256": st["stripPngSha256"]}
        else:
            mask_cache = {}
            poses = [render_procedural_pose(kf, s["layers"], k, mask_cache)
                     for k in range(POSES)]
            extra = {"maskPixels": (len(mask_cache["advance"]) if "advance" in mask_cache
                                     else (mask_cache.get("sweepPixels") if "sweep" in mask_cache else None))}
        assert len(poses) == POSES, f"{sid}: pose count {len(poses)}"
        files, hashes = [], []
        for i, pose in enumerate(poses, 1):
            fp = out_dir / f"pose_{i:02d}.png"
            pose.save(fp)
            files.append(str(fp.relative_to(root)))
            hashes.append(sha256(fp))
        diffs = [mean_abs_diff(poses[i], poses[i + 1]) for i in range(POSES - 1)]
        p1_diff = mean_abs_diff(poses[0], kf)
        last_diff = mean_abs_diff(poses[-1], kf)
        if s["route"] == "generated_strip":
            # Generated panels are full redraws: the same composition re-drawn
            # per panel, so inter-pose diffs are ~50 (background rain/water
            # texture moves with the redraw). The audit therefore checks
            # distinctness + a loose sanity cap, NOT tight continuity; the
            # composition continuity was verified by viewing the strip.
            # redrawBoil: background-only (top strip) diff pose1->pose2,
            # quantifying the redraw flicker (defect D-MC-01).
            for d in diffs:
                assert 5 < d < 100, f"{sid}: inter-pose diff {d} out of (5, 100)"
            assert p1_diff < 100, f"{sid}: pose1 vs keyframe diff {p1_diff} >= 100"
            extra["redrawBoilBackgroundDiff"] = mean_abs_diff(
                poses[0].crop((0, 0, W, 60)), poses[1].crop((0, 0, W, 60)))
            extra["redrawBoilNote"] = (
                "D-MC-01: generated panels are full redraws; background rain/water "
                "texture changes per panel (background-only diff ~38), so the beat "
                "has visible background boil and a texture pop at beat start. "
                "Figure composition is stable (verified by viewing the strip).")
        else:
            for d in diffs:
                assert 0.15 < d < 30, f"{sid}: inter-pose diff {d} out of (0.15, 30)"
            limit = 10
            assert p1_diff < limit, f"{sid}: pose1 vs keyframe diff {p1_diff} >= {limit}"
        records[sid] = {
            "shotId": sid, "route": s["route"], "beatSeconds": s["beatSeconds"],
            "poseCount": POSES, "poseFps": spec["rules"]["poseFps"],
            "poseFiles": files, "poseSha256": hashes,
            "interPoseMeanAbsDiff": diffs,
            "meanInterPoseDiff": round(sum(diffs) / len(diffs), 3),
            "pose1VsKeyframeDiff": p1_diff,
            "lastPoseVsKeyframeDiff": last_diff,
            **extra,
        }
        print(f"{sid}: poses ok, inter-pose diffs {diffs}, "
              f"pose1-vs-kf {p1_diff}, last-vs-kf {last_diff}")
    return records


def build_shot_take(root: Path, spec: dict, sid: str, kf_path: Path, pose_paths):
    """180-frame take: keyframe hold, 5 poses x 3 frames, last pose hold."""
    s = next(x for x in spec["shots"] if x["shotId"] == sid)
    beat_start = int(round(s["beatSeconds"][0] * FPS))
    kf = Image.open(kf_path).convert("RGB")
    poses = [Image.open(root / p).convert("RGB") for p in pose_paths]
    last = poses[-1]
    frames = []
    for f in range(FRAMES_PER_SHOT):
        if f < beat_start:
            frames.append(kf)
        elif f < beat_start + POSES * FRAMES_PER_POSE:
            frames.append(poses[(f - beat_start) // FRAMES_PER_POSE])
        else:
            frames.append(last)
    out = root / "Art_Source/Cinematics/P0_Motion/takes" / f"{sid}_pose_640x360_30fps.mp4"
    with tempfile.TemporaryDirectory() as td:
        for i, fr in enumerate(frames):
            fr.save(Path(td) / f"f{i:03d}.png")
        run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
             "-i", str(Path(td) / "f%03d.png"),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
             "-movflags", "+faststart", str(out)])
    info = probe(out)
    vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
    assert vs["width"] == W and vs["height"] == H, f"{sid}: take size"
    assert int(vs["nb_frames"]) == FRAMES_PER_SHOT, f"{sid}: take frames {vs['nb_frames']}"
    assert abs(float(info["format"]["duration"]) - 6.0) < 0.05, f"{sid}: take duration"
    return {"file": str(out.relative_to(root)), "sha256": sha256(out),
            "sizeBytes": out.stat().st_size, "frames": FRAMES_PER_SHOT,
            "durationSeconds": 6.0, "beatStartFrame": beat_start}


def build_scene_take(root: Path, spec: dict, scene_id: str, shot_takes: dict):
    """Concatenate the scene's shot takes (video-only), then mux the v3 mix."""
    scene_shots = [s for s in spec["shots"] if s["sceneId"] == scene_id]
    mix = spec["mixes"][scene_id]
    mix_path = root / mix["file"]
    assert sha256(mix_path) == mix["sha256"], f"{scene_id}: mix SHA mismatch"
    minfo = probe(mix_path)
    mdur = float(minfo["format"]["duration"])
    scene_dur = sum(s["shotDurationSeconds"] for s in scene_shots)
    assert abs(mdur - scene_dur) < 0.05, f"{scene_id}: mix {mdur}s != scene {scene_dur}s"
    takes_dir = root / "Art_Source/Cinematics/P0_Motion/takes"
    with tempfile.TemporaryDirectory() as td:
        concat = Path(td) / "concat.txt"
        concat.write_text("".join(
            f"file '{takes_dir / (s['shotId'] + '_pose_640x360_30fps.mp4')}'\n"
            for s in scene_shots), encoding="utf-8")
        vonly = Path(td) / "video_only.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", str(vonly)])
        out = takes_dir / f"{scene_id}_pose_640x360_30fps.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(vonly), "-i", str(mix_path),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    info = probe(out)
    assert abs(float(info["format"]["duration"]) - scene_dur) < 0.05, f"{scene_id}: B take duration"
    audio = [x for x in info["streams"] if x["codec_type"] == "audio"][0]
    return {"file": str(out.relative_to(root)), "sha256": sha256(out),
            "sizeBytes": out.stat().st_size, "durationSeconds": scene_dur,
            "audio": {"codec": audio["codec_name"],
                      "sampleRateHz": int(audio["sample_rate"]),
                      "channels": int(audio["channels"]),
                      "sourceMix": mix["file"], "sourceMixSha256": mix["sha256"]}}


def build_ab(root: Path, spec: dict, scene_id: str, scene_take: dict):
    """Vertical stack: A (runtime Ken Burns) over B (pose take), labelled."""
    mix = spec["mixes"][scene_id]
    a_path = root / mix["runtimeMp4"]
    assert sha256(a_path) == mix["runtimeMp4Sha256"], f"{scene_id}: runtime A SHA mismatch"
    b_path = root / scene_take["file"]
    out = root / "Art_Source/Cinematics/P0_Motion/ab" / f"{scene_id}_ab_kenburns_vs_pose_640x720_30fps.mp4"
    fc = ("[0:v]drawtext=fontfile={f}:text='A - KEN BURNS (hien tai)':fontsize=20:"
          "fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6:x=10:y=10[v0];"
          "[1:v]drawtext=fontfile={f}:text='B - POSE ANIMATION (moi, 10 pose/s)':fontsize=20:"
          "fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6:x=10:y=10[v1];"
          "[v0][v1]vstack=inputs=2[vout]").format(f=FONT)
    run(["ffmpeg", "-y", "-v", "error",
         "-i", str(a_path), "-i", str(b_path), "-i", str(root / mix["file"]),
         "-filter_complex", fc, "-map", "[vout]", "-map", "2:a",
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    info = probe(out)
    vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
    assert vs["width"] == W and vs["height"] == 720, f"{scene_id}: AB size"
    return {"file": str(out.relative_to(root)), "sha256": sha256(out),
            "sizeBytes": out.stat().st_size,
            "durationSeconds": float(info["format"]["duration"]),
            "aTake": {"file": mix["runtimeMp4"], "sha256": mix["runtimeMp4Sha256"]},
            "bTake": {"file": scene_take["file"], "sha256": scene_take["sha256"]}}


def build_contacts(root: Path, spec: dict, records: dict):
    out_dir = root / "Art_Source/Cinematics/P0_Motion/contact"
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for s in spec["shots"]:
        sid = s["shotId"]
        kf = Image.open(root / s["keyframe"]["file"]).convert("RGB").resize((320, 180), Image.NEAREST)
        tiles = [kf] + [Image.open(root / p).convert("RGB").resize((320, 180), Image.NEAREST)
                       for p in records[sid]["poseFiles"]]
        sheet = Image.new("RGB", (320 * 6, 180), (255, 255, 255))
        for i, t in enumerate(tiles):
            sheet.paste(t, (i * 320, 0))
        fp = out_dir / f"{sid}_contact.png"
        sheet.save(fp)
        files[sid] = {"file": str(fp.relative_to(root)), "sha256": sha256(fp)}
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--debug-boxes", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    spec = load_json(root / "Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_SPEC_v1.json")
    assert spec["rules"]["poseCount"] == POSES

    if args.debug_boxes:
        debug_boxes(root, spec)
        return 0

    records = prepare_poses(root, spec)

    shot_takes = {}
    for s in spec["shots"]:
        sid = s["shotId"]
        shot_takes[sid] = build_shot_take(
            root, spec, sid, root / s["keyframe"]["file"], records[sid]["poseFiles"])
        print(f"{sid}: take ok, {shot_takes[sid]['sha256'][:12]}")

    scene_takes, abs_ = {}, {}
    for scene_id in ("CIN_001", "CIN_002", "CIN_004"):
        scene_takes[scene_id] = build_scene_take(root, spec, scene_id, shot_takes)
        abs_[scene_id] = build_ab(root, spec, scene_id, scene_takes[scene_id])
        print(f"{scene_id}: B take + AB ok, {abs_[scene_id]['sha256'][:12]}")

    contacts = build_contacts(root, spec, records)

    manifest = {
        "manifestId": "NGM_P0_MOTION_AB_V1",
        "checkpoint": "WO37 M-C checkpoint 2 - P0 motion/AB (12 shots)",
        "decisionId": spec["decisionId"],
        "workOrder": "WO37 M-C",
        "branch": spec["branch"],
        "baseSha": spec["baseSha"],
        "status": spec["rules"]["status"],
        "sources": spec["sources"],
        "rules": spec["rules"],
        "rejectedStrips": spec.get("rejectedStrips", []),
        "shots": [records[s["shotId"]] for s in spec["shots"]],
        "shotTakes": {sid: shot_takes[sid] for sid in shot_takes},
        "sceneTakes": scene_takes,
        "abVideos": abs_,
        "contacts": contacts,
        "totals": {
            "shots": 12, "posesPerShot": POSES,
            "poseFps": spec["rules"]["poseFps"],
            "generatedShots": sum(1 for s in spec["shots"] if s["route"] == "generated_strip"),
            "proceduralShots": sum(1 for s in spec["shots"] if s["route"] == "procedural"),
            "sceneDurations": {"CIN_001": 36.0, "CIN_002": 18.0, "CIN_004": 18.0},
        },
    }
    out = root / "Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("manifest ->", out)
    print("P0 MOTION/AB BUILD OK: 12 shots, 60 poses, 3 scene B takes, 3 AB videos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
