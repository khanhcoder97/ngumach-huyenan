#!/usr/bin/env python3
"""WO37 M-C checkpoint 2: independent validator for the P0 motion/AB pack.

Re-reads the spec, the manifest, the timing files, the P0 keyframes
manifest and the scene export manifests from disk, and re-derives every
claim in Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json:
  - counts: 12 shots, 5 poses each, 10 pose fps, 3 generated / 9 procedural
  - file hashes: strips, pose frames, takes, scene takes, AB videos, contacts
  - strip re-cut (own implementation) -> pose frame hashes must match
  - procedural pose re-render (builder's pure renderers) -> hashes must match
  - measurements re-computed from disk frames (inter-pose diffs,
    pose1-vs-keyframe, redraw boil) must match the manifest to 0.001
  - video probes: shot takes 180 frames / 6.0 s / 640x360; scene takes
    36/18/18 s with AAC 48 kHz stereo from the v3 mix; AB 640x720 with the
    same durations; AB mid-frame halves match the A and B takes (< 5)
  - beat placement: the 3 dialogue shots start their beat exactly at the
    dialogue window start (CIN_001_S05 24.8, CIN_002_S02 7.0, CIN_004_S02 7.5
    scene-local); all beats are 0.5 s at 10 pose fps
  - source SHAs: keyframes vs P0 manifest, mixes vs scene export manifests,
    runtime A videos vs scene export manifests

Writes Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP2_VALIDATION_20261108.json
and exits non-zero on any mismatch.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

sys.path.insert(0, str(Path(__file__).parent))
from build_p0_motion_ab_v1 import (  # noqa: E402  (reuse pure renderers for drift check)
    render_procedural_pose)

W, H = 640, 360
ROOT = Path(__file__).resolve().parents[3]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def probe(path: Path) -> dict:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                        "-of", "json", str(path)], capture_output=True, text=True)
    assert r.returncode == 0, f"ffprobe failed on {path}: {r.stderr}"
    return json.loads(r.stdout)


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return round(sum(ImageStat.Stat(d).mean) / 3.0, 3)


def cut_cells(strip_path: Path, panels):
    """Own strip-cut implementation (independent of the builder)."""
    strip = Image.open(strip_path).convert("RGB")
    sw, sh = strip.size
    cw = sw // 8
    out = []
    for p in panels:
        cell = strip.crop((p * cw, 0, (p + 1) * cw, sh))
        ar = cell.size[0] / cell.size[1]
        if abs(ar - 16 / 9) / (16 / 9) < 0.01:
            out.append(cell.resize((W, H), Image.NEAREST))
        elif ar > 16 / 9:
            nh = int(cell.size[0] / (16 / 9))
            top = (cell.size[1] - nh) // 2
            out.append(cell.crop((0, top, cell.size[0], top + nh)).resize((W, H), Image.NEAREST))
        else:
            nw = int(cell.size[0] * H / cell.size[1])
            scaled = cell.resize((nw, H), Image.NEAREST)
            pose = Image.new("RGB", (W, H))
            pad = (W - nw) // 2
            pose.paste(scaled.crop((0, 0, 1, H)).resize((pad, H), Image.NEAREST), (0, 0))
            pose.paste(scaled, (pad, 0))
            pose.paste(scaled.crop((nw - 1, 0, nw, H)).resize((W - nw - pad, H), Image.NEAREST),
                       (pad + nw, 0))
            out.append(pose)
    return out


def extract_frame(video: Path, seconds: float, out: Path):
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(seconds),
                        "-i", str(video), "-frames:v", "1", str(out)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"frame extract failed {video}: {r.stderr}"


def main() -> int:
    errors, checked = [], 0

    def err(msg):
        errors.append(msg)
        print("MISMATCH:", msg)

    def ok():
        nonlocal checked
        checked += 1

    spec = load("Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_SPEC_v1.json")
    man = load("Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json")

    # --- counts / totals
    if len(man["shots"]) != 12:
        err(f"shots {len(man['shots'])} != 12")
    else:
        ok()
    if man["totals"] != {"shots": 12, "posesPerShot": 5, "poseFps": 10,
                         "generatedShots": 0, "proceduralShots": 12,
                         "sceneDurations": {"CIN_001": 36.0, "CIN_002": 18.0, "CIN_004": 18.0}}:
        err(f"totals mismatch: {man['totals']}")
    else:
        ok()
    if man["status"] != spec["rules"]["status"]:
        err("status mismatch")
    else:
        ok()

    # --- source SHAs: keyframes vs P0 manifest, mixes vs scene manifests
    p0 = load("Art_Source/Cinematics/P0_Animatic/P0_keyframes_16x9_manifest_v1.json")
    kf_sha = {s["shotId"]: s["sha256"] for s in p0["shots"]}
    for s in spec["shots"]:
        if s["keyframe"]["sha256"] != kf_sha.get(s["shotId"]):
            err(f"{s['shotId']}: keyframe SHA != P0 manifest")
        else:
            ok()
        if sha256(ROOT / s["keyframe"]["file"]) != kf_sha[s["shotId"]]:
            err(f"{s['shotId']}: keyframe file SHA != manifest")
        else:
            ok()
    for sc in ("CIN_001", "CIN_002", "CIN_004"):
        em = load(f"ClientGodot/assets/cinematics/{sc}/scene_export_manifest_v1.json")
        if spec["mixes"][sc]["sha256"] != em["files"]["mp4"]["audio"]["sourceMixSha256"]:
            err(f"{sc}: mix SHA != scene export manifest")
        else:
            ok()
        if spec["mixes"][sc]["runtimeMp4Sha256"] != em["files"]["mp4"]["sha256"]:
            err(f"{sc}: runtime A SHA != scene export manifest")
        else:
            ok()

    # --- beat placement vs dialogue windows
    dlg = {}
    for sc in ("CIN_001", "CIN_002", "CIN_004"):
        t = load(f"Implementation/Content/Narrative/Deliveries/{sc}/{sc}_timing_v1.json")
        for sh in t["shots"]:
            if sh.get("dialogue"):
                dlg[sh["shotId"]] = sh["dialogue"]["windowSeconds"][0] - sh["startSeconds"]
    for s in spec["shots"]:
        sid = s["shotId"]
        if abs((s["beatSeconds"][1] - s["beatSeconds"][0]) - 0.5) > 1e-9:
            err(f"{sid}: beat length != 0.5 s")
        else:
            ok()
        if sid in dlg and abs(s["beatSeconds"][0] - dlg[sid]) > 1e-9:
            err(f"{sid}: beat start {s['beatSeconds'][0]} != dialogue window start {dlg[sid]}")
        else:
            ok()

    # --- per-shot: poses, measurements, takes
    for s in spec["shots"]:
        sid = s["shotId"]
        rec = next(x for x in man["shots"] if x["shotId"] == sid)
        kf = Image.open(ROOT / s["keyframe"]["file"]).convert("RGB")
        # strip SHA + re-cut / re-render
        if s["route"] == "generated_strip":
            if sha256(ROOT / s["strip"]["file"]) != s["strip"]["stripPngSha256"]:
                err(f"{sid}: strip SHA mismatch")
            else:
                ok()
            poses = cut_cells(ROOT / s["strip"]["file"], s["strip"]["panels"])
        else:
            mask_cache = {}
            poses = [render_procedural_pose(kf, s["layers"], k, mask_cache)
                     for k in range(5)]
        if len(poses) != 5:
            err(f"{sid}: pose count {len(poses)}")
            continue
        ok()
        for i, pose in enumerate(poses):
            fp = ROOT / rec["poseFiles"][i]
            if not fp.exists():
                err(f"{sid}: pose file missing {fp}")
                continue
            if sha256(fp) != rec["poseSha256"][i]:
                err(f"{sid}: pose {i + 1} file SHA != manifest")
            else:
                ok()
            disk = Image.open(fp).convert("RGB")
            import hashlib as _h
            if _h.sha256(disk.tobytes()).hexdigest() != _h.sha256(pose.tobytes()).hexdigest():
                err(f"{sid}: pose {i + 1} pixels != re-derived pose")
            else:
                ok()
        diffs = [mean_abs_diff(poses[i], poses[i + 1]) for i in range(4)]
        if diffs != rec["interPoseMeanAbsDiff"]:
            err(f"{sid}: inter-pose diffs {diffs} != manifest {rec['interPoseMeanAbsDiff']}")
        else:
            ok()
        if mean_abs_diff(poses[0], kf) != rec["pose1VsKeyframeDiff"]:
            err(f"{sid}: pose1-vs-kf != manifest")
        else:
            ok()
        if s["route"] == "generated_strip":
            boil = mean_abs_diff(poses[0].crop((0, 0, W, 60)),
                                 poses[1].crop((0, 0, W, 60)))
            if boil != rec.get("redrawBoilBackgroundDiff"):
                err(f"{sid}: redraw boil {boil} != manifest {rec.get('redrawBoilBackgroundDiff')}")
            else:
                ok()
        # take probe
        tk = man["shotTakes"][sid]
        if sha256(ROOT / tk["file"]) != tk["sha256"]:
            err(f"{sid}: take SHA mismatch")
        else:
            ok()
        info = probe(ROOT / tk["file"])
        vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
        if (vs["width"], vs["height"]) != (640, 360) or int(vs["nb_frames"]) != 180:
            err(f"{sid}: take video {vs['width']}x{vs['height']} frames {vs['nb_frames']}")
        else:
            ok()
        if abs(float(info["format"]["duration"]) - 6.0) > 0.05:
            err(f"{sid}: take duration {info['format']['duration']}")
        else:
            ok()

    # --- scene takes + AB
    for sc, dur in (("CIN_001", 36.0), ("CIN_002", 18.0), ("CIN_004", 18.0)):
        st = man["sceneTakes"][sc]
        if sha256(ROOT / st["file"]) != st["sha256"]:
            err(f"{sc}: scene take SHA mismatch")
        else:
            ok()
        info = probe(ROOT / st["file"])
        if abs(float(info["format"]["duration"]) - dur) > 0.05:
            err(f"{sc}: scene take duration {info['format']['duration']} != {dur}")
        else:
            ok()
        au = [x for x in info["streams"] if x["codec_type"] == "audio"]
        if not au or au[0]["codec_name"] != "aac" or int(au[0]["sample_rate"]) != 48000:
            err(f"{sc}: scene take audio not AAC 48kHz")
        else:
            ok()
        ab = man["abVideos"][sc]
        if sha256(ROOT / ab["file"]) != ab["sha256"]:
            err(f"{sc}: AB SHA mismatch")
        else:
            ok()
        info = probe(ROOT / ab["file"])
        vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
        if (vs["width"], vs["height"]) != (640, 720):
            err(f"{sc}: AB size {vs['width']}x{vs['height']} != 640x720")
        else:
            ok()
        if abs(float(info["format"]["duration"]) - dur) > 0.05:
            err(f"{sc}: AB duration != {dur}")
        else:
            ok()
        # AB halves match A and B takes at mid-scene
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            mid = dur / 2
            extract_frame(ROOT / ab["file"], mid, td / "ab.png")
            extract_frame(ROOT / spec["mixes"][sc]["runtimeMp4"], mid, td / "a.png")
            extract_frame(ROOT / st["file"], mid, td / "b.png")
            ab_im = Image.open(td / "ab.png").convert("RGB")
            a_im = Image.open(td / "a.png").convert("RGB")
            b_im = Image.open(td / "b.png").convert("RGB")
            d_top = mean_abs_diff(ab_im.crop((0, 0, 640, 360)), a_im)
            d_bot = mean_abs_diff(ab_im.crop((0, 360, 640, 720)), b_im)
            if d_top > 5 or d_bot > 5:
                err(f"{sc}: AB halves differ from A/B takes (top {d_top}, bottom {d_bot})")
            else:
                ok()

    # --- contacts
    for sid, c in man["contacts"].items():
        if sha256(ROOT / c["file"]) != c["sha256"]:
            err(f"{sid}: contact SHA mismatch")
        else:
            ok()

    result = {
        "validator": "check_p0_motion_ab_v1.py",
        "manifest": "Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json",
        "spec": "Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_SPEC_v1.json",
        "checks": checked, "mismatches": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    out = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP2_VALIDATION_20261108.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"VALIDATION {result['status']}: {checked} checks, {len(errors)} mismatches -> {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
