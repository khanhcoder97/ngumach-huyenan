#!/usr/bin/env python3
"""WO37 M-C checkpoint 3c: Ken Burns hold slice for CIN_020_S03 (1 shot).

Closes the remainder named in M-C checkpoint 3b: the 26th priority-3
shot, CIN_020_S03, is a ledger KEN_BURNS_HOLD shot (M-C CP5 reclassified
it from ACTION in the continuity ledger without rebuilding the file) but
still has only a CP3a pose take file. The hold slice is an exact 6 s cut
of the runtime A video, re-encoded exactly like the CP3a/CP3b holds
(libx264 crf 18, 640x360, 30 fps, silent). Character lock does not block
a hold slice (it blocks final pose animation only).

The scene B take is MIXED: S01/S02 keep their CP3a pose takes (SHA-verified
against the P2 manifest before concatenation), S03 uses the new hold slice;
the AB video labels B accordingly (POSE + HOLD). The CP3a pose take file
for S03 is retained on disk but no longer used by the scene B take. The
CP3a manifest (CAMPAIGN_MOTION_P2_v1.json) is NOT edited: its CIN_020
B take / AB / contact entries are superseded by the P2C manifest.

Reads Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_SPEC_v1.json
and builds:

  Art_Source/Cinematics/Campaign_Motion/takes/CIN_020_S03_hold_640x360_30fps.mp4 (1)
  Art_Source/Cinematics/Campaign_Motion/takes/CIN_020_pose_640x360_30fps.mp4 (rebuilt B take, draft v1 mix audio)
  Art_Source/Cinematics/Campaign_Motion/ab/CIN_020_ab_kenburns_vs_pose_640x720_30fps.mp4 (rebuilt)
  Art_Source/Cinematics/Campaign_Motion/contact/CIN_020_S03_contact.png (rebuilt; keyframe + 5 slice frames)
  Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_v1.json (manifest)

The runtime files are NOT replaced; this is a review pack.
Status DRAFT_KEN_BURNS_HOLD.

Every measurement is recomputed from bytes on disk; the builder FAILS on:
  - keyframe file SHA != motion ledger
  - mix / runtime A SHA != spec (which the validator cross-checks against
    the scene export manifests)
  - pose take S01/S02 SHA != spec (which the validator cross-checks
    against the P2 manifest)
  - hold slice frames != 180, duration != 6.0 s
  - hold slice vs runtime A at 1.0/3.0/5.0 s: mean abs channel diff >= 5
  - hold slice frozen: first-vs-last sampled frame diff == 0
  - mix duration != scene duration, A/B size != 640x720
"""
import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

W, H = 640, 360
FPS = 30
FRAMES_PER_SHOT = 180
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SAMPLE_SECONDS = [0.0, 1.5, 3.0, 4.5, 5.9]


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


def existing_ok(path: Path, frames: int, duration: float, need_audio: bool = False) -> bool:
    """Resume guard: an output file is reusable only if it exists and probes
    exactly as the builder would have produced it (size / frames / duration
    / audio). A file killed mid-encode fails the probe and is rebuilt."""
    if not path.exists() or path.stat().st_size == 0:
        return False
    try:
        info = probe(path)
    except Exception:
        return False
    vs = [x for x in info["streams"] if x["codec_type"] == "video"]
    if not vs or vs[0]["width"] != W or vs[0]["height"] != (720 if frames == 540 and need_audio and "ab" in path.name else H):
        return False
    if int(vs[0]["nb_frames"]) != frames:
        return False
    if abs(float(info["format"]["duration"]) - duration) > 0.05:
        return False
    if need_audio and not [x for x in info["streams"] if x["codec_type"] == "audio"]:
        return False
    return True


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    d = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return round(sum(ImageStat.Stat(d).mean) / 3.0, 3)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def extract_frame(video: Path, seconds: float, out: Path):
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(seconds),
         "-i", str(video), "-frames:v", "1", str(out)])


def build_hold_slice(root: Path, spec: dict, scene_id: str, shot: dict):
    """Ken Burns hold slice: exact 6 s cut from the runtime A video
    (frame-accurate seek, re-encoded like the CP3a/CP3b holds)."""
    sid = shot["shotId"]
    start = shot["startSeconds"]
    mix = spec["mixes"][scene_id]
    a_path = root / mix["runtimeMp4"]
    assert sha256(a_path) == mix["runtimeMp4Sha256"], f"{scene_id}: runtime A SHA mismatch"
    out = root / "Art_Source/Cinematics/Campaign_Motion/takes" / f"{sid}_hold_640x360_30fps.mp4"
    if existing_ok(out, FRAMES_PER_SHOT, 6.0):
        print(f"{sid}: hold slice reused (already on disk, probe OK)")
    else:
        run(["ffmpeg", "-y", "-v", "error",
             "-ss", str(start), "-i", str(a_path), "-t", "6",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-r", "30",
             "-an", str(out)])
    info = probe(out)
    vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
    assert vs["width"] == W and vs["height"] == H, f"{sid}: hold slice size"
    assert int(vs["nb_frames"]) == FRAMES_PER_SHOT, f"{sid}: hold slice frames {vs['nb_frames']}"
    assert abs(float(info["format"]["duration"]) - 6.0) < 0.05, f"{sid}: hold slice duration"
    # Fidelity: hold slice vs runtime A at the same scene time (1/3/5 s).
    # Drift: first vs last sampled frame must differ (Ken Burns move, not frozen).
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        diffs = {}
        for t in (1.0, 3.0, 5.0):
            extract_frame(out, t, td / f"h{t}.png")
            extract_frame(a_path, start + t, td / f"a{t}.png")
            d = mean_abs_diff(Image.open(td / f"h{t}.png").convert("RGB"),
                              Image.open(td / f"a{t}.png").convert("RGB"))
            assert d < 5, f"{sid}: hold slice differs from runtime A by {d} at {t}s"
            diffs[f"{t}s"] = d
        extract_frame(out, 0.0, td / "first.png")
        extract_frame(out, 5.9, td / "last.png")
        drift = mean_abs_diff(Image.open(td / "first.png").convert("RGB"),
                              Image.open(td / "last.png").convert("RGB"))
        assert drift > 0, f"{sid}: hold slice frozen (first==last frame)"
        samples = []
        for t in SAMPLE_SECONDS:
            extract_frame(out, t, td / f"s{t}.png")
            samples.append(Image.open(td / f"s{t}.png").convert("RGB"))
    return {"file": str(out.relative_to(root)), "sha256": sha256(out),
            "sizeBytes": out.stat().st_size, "frames": FRAMES_PER_SHOT,
            "durationSeconds": 6.0, "kind": "KEN_BURNS_HOLD",
            "sourceRuntime": mix["runtimeMp4"],
            "sourceRuntimeSha256": mix["runtimeMp4Sha256"],
            "sourceStartSeconds": start,
            "sourceEndSeconds": start + 6.0,
            "vsRuntimeMeanAbsDiff": diffs,
            "kenBurnsDriftFirstLast": drift}, samples


def build_scene_take(root: Path, spec: dict, scene_id: str,
                     scene_shots_all):
    """Full-scene B take, MIXED segments in ledger shot order: S01/S02 keep
    their CP3a pose takes (SHA-verified), S03 uses the new hold slice; then
    mux the draft v1 mix. The old B take file is stale by design (its S03
    segment was the CP3a pose take), so this always rebuilds."""
    mix = spec["mixes"][scene_id]
    mix_path = root / mix["file"]
    assert sha256(mix_path) == mix["sha256"], f"{scene_id}: mix SHA mismatch"
    minfo = probe(mix_path)
    mdur = float(minfo["format"]["duration"])
    scene_dur = sum(6.0 for _ in scene_shots_all)
    assert abs(mdur - scene_dur) < 0.05, f"{scene_id}: mix {mdur}s != scene {scene_dur}s"
    takes_dir = root / "Art_Source/Cinematics/Campaign_Motion/takes"
    segments = []
    kinds = []
    for (sid, _s) in scene_shots_all:
        if sid in spec["poseTakes"]:
            seg = takes_dir / (sid + "_pose_640x360_30fps.mp4")
            assert sha256(seg) == spec["poseTakes"][sid]["sha256"], f"{sid}: pose take SHA mismatch"
            assert sha256(root / spec["poseTakes"][sid]["file"]) == spec["poseTakes"][sid]["sha256"]
            segments.append(seg)
            kinds.append("POSE_ANIMATION")
        else:
            segments.append(takes_dir / (sid + "_hold_640x360_30fps.mp4"))
            kinds.append("KEN_BURNS_HOLD")
    with tempfile.TemporaryDirectory() as td:
        concat = Path(td) / "concat.txt"
        concat.write_text("".join(f"file '{seg}'\n" for seg in segments), encoding="utf-8")
        vonly = Path(td) / "video_only.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-c", "copy", str(vonly)])
        out = takes_dir / f"{scene_id}_pose_640x360_30fps.mp4"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(vonly), "-i", str(mix_path),
             "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)])
    info = probe(out)
    assert abs(float(info["format"]["duration"]) - scene_dur) < 0.05, f"{scene_id}: B take duration"
    vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
    assert int(vs["nb_frames"]) == int(scene_dur * FPS), f"{scene_id}: B take frames {vs['nb_frames']}"
    audio = [x for x in info["streams"] if x["codec_type"] == "audio"][0]
    return {"file": str(out.relative_to(root)), "sha256": sha256(out),
            "sizeBytes": out.stat().st_size, "durationSeconds": scene_dur,
            "audio": {"codec": audio["codec_name"],
                      "sampleRateHz": int(audio["sample_rate"]),
                      "channels": int(audio["channels"]),
                      "sourceMix": mix["file"], "sourceMixSha256": mix["sha256"]},
            "segments": [{"shotId": sid, "kind": kind}
                         for (sid, _s), kind in zip(scene_shots_all, kinds)]}


def build_ab(root: Path, spec: dict, scene_id: str, scene_take: dict):
    """Vertical stack: A (runtime Ken Burns) over B (mixed pose + hold take),
    labelled. The B label is honest for this pack: S01/S02 are pose animation,
    S03 is a Ken Burns hold re-cut. The old AB file is stale by design (its
    B half came from the old B take), so this always rebuilds."""
    mix = spec["mixes"][scene_id]
    a_path = root / mix["runtimeMp4"]
    assert sha256(a_path) == mix["runtimeMp4Sha256"], f"{scene_id}: runtime A SHA mismatch"
    b_path = root / scene_take["file"]
    out = root / "Art_Source/Cinematics/Campaign_Motion/ab" / f"{scene_id}_ab_kenburns_vs_pose_640x720_30fps.mp4"
    fc = ("[0:v]drawtext=fontfile={f}:text='A - KEN BURNS (hien tai)':fontsize=20:"
          "fontcolor=white:box=1:boxcolor=black@0.5:boxborderw=6:x=10:y=10[v0];"
          "[1:v]drawtext=fontfile={f}:text='B - POSE + HOLD (S03 cat tu runtime A)':fontsize=20:"
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


def build_contacts(root: Path, spec: dict, samples: dict):
    """Contact sheet per hold shot: keyframe + 5 sampled frames of the hold
    slice (0.0 / 1.5 / 3.0 / 4.5 / 5.9 s), 320x180 tiles, 1920x180."""
    out_dir = root / "Art_Source/Cinematics/Campaign_Motion/contact"
    out_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for s in spec["shots"]:
        sid = s["shotId"]
        kf = Image.open(root / s["keyframe"]["file"]).convert("RGB").resize((320, 180), Image.NEAREST)
        tiles = [kf] + [im.resize((320, 180), Image.NEAREST) for im in samples[sid]]
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
    args = ap.parse_args()
    root = Path(args.root).resolve()
    spec = load_json(root / "Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_SPEC_v1.json")
    ledger = load_json(root / "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json")
    # full shot order per scene from the ledger (S01/S02 pose + S03 hold)
    scene_shots_all = {}
    for s in ledger["shots"]:
        if s["sceneId"] in spec["mixes"]:
            scene_shots_all.setdefault(s["sceneId"], []).append((s["shotId"], s["startSeconds"]))
    for sc in scene_shots_all:
        scene_shots_all[sc].sort(key=lambda x: x[1])
    # keyframe SHAs must match the ledger before anything is cut
    kf_sha = {s["shotId"]: s["keyframe"]["sha256"] for s in ledger["shots"]}
    for s in spec["shots"]:
        assert s["keyframe"]["sha256"] == kf_sha[s["shotId"]], f"{s['shotId']}: keyframe SHA != ledger"
        assert sha256(root / s["keyframe"]["file"]) == kf_sha[s["shotId"]], f"{s['shotId']}: keyframe file SHA != ledger"

    (root / "Art_Source/Cinematics/Campaign_Motion/takes").mkdir(parents=True, exist_ok=True)
    (root / "Art_Source/Cinematics/Campaign_Motion/ab").mkdir(parents=True, exist_ok=True)

    hold_slices, samples, records = {}, {}, []
    for s in spec["shots"]:
        sid = s["shotId"]
        rec, sam = build_hold_slice(root, spec, s["sceneId"], s)
        hold_slices[sid] = rec
        samples[sid] = sam
        records.append({
            "shotId": sid, "sceneId": s["sceneId"], "route": "ken_burns_hold",
            "startSeconds": s["startSeconds"],
            "keyframe": s["keyframe"],
            "holdSlice": rec["file"], "holdSliceSha256": rec["sha256"],
            "vsRuntimeMeanAbsDiff": rec["vsRuntimeMeanAbsDiff"],
            "kenBurnsDriftFirstLast": rec["kenBurnsDriftFirstLast"],
            **({"dialogueStagingNote": s["dialogueStagingNote"]} if "dialogueStagingNote" in s else {}),
        })
        print(f"{sid}: hold ok, vs-runtime {rec['vsRuntimeMeanAbsDiff']}, drift {rec['kenBurnsDriftFirstLast']}")

    scene_takes, abs_ = {}, {}
    for scene_id in sorted(spec["mixes"]):
        scene_takes[scene_id] = build_scene_take(
            root, spec, scene_id, scene_shots_all[scene_id])
        abs_[scene_id] = build_ab(root, spec, scene_id, scene_takes[scene_id])
        print(f"{scene_id}: B take + AB ok, {abs_[scene_id]['sha256'][:12]}")

    contacts = build_contacts(root, spec, samples)

    manifest = {
        "manifestId": "NGM_CAMPAIGN_MOTION_P2C_V1",
        "checkpoint": "WO37 M-C checkpoint 3c - campaign motion, Ken Burns hold for CIN_020_S03 (1 shot)",
        "decisionId": spec["decisionId"],
        "workOrder": "WO37 M-C",
        "branch": spec["branch"],
        "baseSha": spec["baseSha"],
        "status": spec["rules"]["status"],
        "sources": spec["sources"],
        "rules": spec["rules"],
        "shots": records,
        "holdSlices": hold_slices,
        "sceneTakes": scene_takes,
        "abVideos": abs_,
        "contacts": contacts,
        "supersedes": {
            "manifest": "Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2_v1.json",
            "entries": {
                "sceneTakes": {"CIN_020": "7ae22522831bc8f70fdc3bda8184576f43cbc3da9d156dbc0714d8020e6106aa"},
                "abVideos": {"CIN_020": "686a63020b2f9714bc0e583358466366bb16076f8358a1d7185919ea57550ccb"},
                "contacts": {"CIN_020_S03": "59a3f34dafd9b3a84ae0396abd055d01dc66e12ba15ebb6dd807b236a3c741ba"},
            },
            "note": "The CP3a manifest file itself is NOT edited (history intact). Its CIN_020 B take / AB / contact entries record the CP3a build, in which S03 was the pose take; this manifest is the current record for those three files.",
        },
        "retainedPoseTake": {
            "file": "Art_Source/Cinematics/Campaign_Motion/takes/CIN_020_S03_pose_640x360_30fps.mp4",
            "sha256": "eaff4cc90baa5cc014ddbb0106520b5c1cc3ccc6e5666cdedc5ec643aaa5b78e",
            "note": "CP3a pose take file retained on disk (archive of the CP3a build); no longer used by the scene B take. Its pose frames are a degenerate ping-pong (pose_01 = keyframe, pose_04 = pose_02, pose_05 = pose_01) — one reason M-C CP5 reclassified the shot to KEN_BURNS_HOLD.",
        },
        "totals": {
            "shots": 1, "holdSlices": 1, "scenes": 1,
            "sceneShotSlots": 3, "holdSegments": 1, "poseSegments": 2,
            "sceneDurations": {sc: 18.0 for sc in sorted(spec["mixes"])},
            "note": "After this pack, all 26 ledger Ken Burns hold shots have a hold slice file "
                    "(19 CP3a + 6 CP3b + 1 CP3c: CIN_020_S03). All 20 campaign scenes have a scene B take; "
                    "CIN_020 is the only scene whose B take mixes pose and hold segments.",
        },
    }
    out = root / "Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_v1.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("manifest ->", out)
    print("CAMPAIGN MOTION P2C BUILD OK: 1 hold slice, 1 scene B take, 1 AB video, 1 contact")
    return 0


if __name__ == "__main__":
    sys.exit(main())
