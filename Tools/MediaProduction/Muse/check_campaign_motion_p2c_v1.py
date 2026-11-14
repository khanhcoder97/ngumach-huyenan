#!/usr/bin/env python3
"""WO37 M-C checkpoint 3c: independent validator for the Ken Burns hold pack
for CIN_020_S03.

Re-reads the spec, the manifest, the timing file, the motion ledger, the
CP3a manifest and the scene export manifest from disk, and re-derives every
claim in Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_v1.json:
  - counts: 1 shot, 1 hold slice, 1 scene, 1 B take, 1 AB video, 1 contact
  - file hashes: hold slice, scene take, AB video, contact
  - source SHAs: keyframe vs motion ledger, mix / runtime A vs scene export
    manifest, pose takes S01/S02 vs spec and vs the CP3a manifest
  - history intact: the CP3a manifest still records the old CIN_020 B take /
    AB / contact SHAs, and the CP3a pose take file for S03 is still on disk
    with its CP3a SHA (retained, not deleted, not edited)
  - hold slice: 180 frames / 6.0 s, frames at 1.0/3.0/5.0 s match the runtime
    A video at the same scene time (< 5, re-derived to 0.001); first-vs-last
    sampled frame differs (Ken Burns drift, not frozen)
  - scene take: 540 frames / 18.0 s with AAC 48 kHz stereo from the v1 mix;
    segments [POSE_ANIMATION, POSE_ANIMATION, KEN_BURNS_HOLD] in ledger shot
    order; segment-boundary frames match the corresponding segment start
    frames (< 5)
  - AB video: 640x720 / 540 frames / 18.0 s; halves match the A and B takes
    below the label band (< 5) at 9.0 s (pose window) and 15.0 s (hold
    window); A half vs B half differs only by re-encode noise (< 5) at
    15.0 s — the fidelity proof for the hold re-cut (the pose windows are
    genuinely different pictures, so they are not part of that proof)
  - contact: keyframe + 5 re-extracted slice frames, pixels re-derived
  - dialogue staging: S03 window [12.5, 17.5], onscreen=true, speaker
    LETTER_RECIPIENT, staging note recorded in the manifest (no beat is
    rendered for a hold shot)

Writes Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP3C_VALIDATION_20261112.json
and exits non-zero on any mismatch.
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

W, H = 640, 360
ROOT = Path(__file__).resolve().parents[3]
SAMPLE_SECONDS = [0.0, 1.5, 3.0, 4.5, 5.9]


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

    spec = load("Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_SPEC_v1.json")
    man = load("Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_v1.json")
    ledger = load("Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json")
    p2 = load("Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2_v1.json")

    # --- counts / totals
    if len(man["shots"]) != 1 or len(man["holdSlices"]) != 1:
        err(f"shots/holdSlices {len(man['shots'])}/{len(man['holdSlices'])} != 1/1")
    else:
        ok()
    if len(man["sceneTakes"]) != 1 or len(man["abVideos"]) != 1 or len(man["contacts"]) != 1:
        err(f"sceneTakes/abVideos/contacts {len(man['sceneTakes'])}/{len(man['abVideos'])}/{len(man['contacts'])} != 1/1/1")
    else:
        ok()
    tot = man["totals"]
    if (tot["shots"], tot["holdSlices"], tot["scenes"], tot["sceneShotSlots"],
            tot["holdSegments"], tot["poseSegments"]) != (1, 1, 1, 3, 1, 2):
        err(f"totals mismatch: {tot}")
    else:
        ok()
    if tot["sceneDurations"] != {sc: 18.0 for sc in sorted(spec["mixes"])}:
        err(f"sceneDurations mismatch: {tot['sceneDurations']}")
    else:
        ok()
    if "CIN_020_S03" not in tot["note"] or "26" not in tot["note"]:
        err("totals note does not record the 26/26 hold-slice completion")
    else:
        ok()
    if man["status"] != spec["rules"]["status"]:
        err("status mismatch")
    else:
        ok()
    if man["manifestId"] != "NGM_CAMPAIGN_MOTION_P2C_V1":
        err(f"manifestId {man['manifestId']}")
    else:
        ok()

    # --- history intact: CP3a manifest untouched, CP3a pose take retained
    sup = man["supersedes"]
    if p2["sceneTakes"]["CIN_020"]["sha256"] != sup["entries"]["sceneTakes"]["CIN_020"]:
        err("P2 manifest CIN_020 B take SHA changed (history must stay intact)")
    else:
        ok()
    if p2["abVideos"]["CIN_020"]["sha256"] != sup["entries"]["abVideos"]["CIN_020"]:
        err("P2 manifest CIN_020 AB SHA changed (history must stay intact)")
    else:
        ok()
    if p2["contacts"]["CIN_020_S03"]["sha256"] != sup["entries"]["contacts"]["CIN_020_S03"]:
        err("P2 manifest CIN_020_S03 contact SHA changed (history must stay intact)")
    else:
        ok()
    ret = man["retainedPoseTake"]
    if sha256(ROOT / ret["file"]) != ret["sha256"]:
        err("retained CP3a pose take file SHA mismatch (must stay on disk untouched)")
    else:
        ok()
    if p2["shotTakes"]["CIN_020_S03"]["sha256"] != ret["sha256"]:
        err("retained pose take SHA != P2 manifest shotTakes entry")
    else:
        ok()

    # --- source SHAs: keyframe vs motion ledger, mixes vs scene manifests
    kf_sha = {s["shotId"]: s["keyframe"]["sha256"] for s in ledger["shots"]}
    for s in spec["shots"]:
        if s["keyframe"]["sha256"] != kf_sha.get(s["shotId"]):
            err(f"{s['shotId']}: keyframe SHA != motion ledger")
        else:
            ok()
        if sha256(ROOT / s["keyframe"]["file"]) != kf_sha[s["shotId"]]:
            err(f"{s['shotId']}: keyframe file SHA != ledger")
        else:
            ok()
        # ledger agrees this shot is a lock-required Ken Burns hold, priority 3
        ls = next(x for x in ledger["shots"] if x["shotId"] == s["shotId"])
        if not (ls.get("characterLockRequired") and ls.get("motionClass") == "KEN_BURNS_HOLD"
                and ls.get("priority") == 3):
            err(f"{s['shotId']}: ledger does not say lock-required KEN_BURNS_HOLD p3")
        else:
            ok()
    for sc in sorted(spec["mixes"]):
        em = load(f"ClientGodot/assets/cinematics/{sc}/scene_export_manifest_v1.json")
        if spec["mixes"][sc]["sha256"] != em["files"]["mp4"]["audio"]["sourceMixSha256"]:
            err(f"{sc}: mix SHA != scene export manifest")
        else:
            ok()
        if spec["mixes"][sc]["runtimeMp4Sha256"] != em["files"]["mp4"]["sha256"]:
            err(f"{sc}: runtime A SHA != scene export manifest")
        else:
            ok()
    # pose takes S01/S02: spec SHA == disk SHA == P2 manifest SHA
    for sid, pt in spec["poseTakes"].items():
        if sha256(ROOT / pt["file"]) != pt["sha256"]:
            err(f"{sid}: pose take file SHA != spec")
        else:
            ok()
        if p2["shotTakes"][sid]["sha256"] != pt["sha256"]:
            err(f"{sid}: pose take SHA != P2 manifest shotTakes entry")
        else:
            ok()

    # --- dialogue staging: S03 window [12.5, 17.5], onscreen, LETTER_RECIPIENT
    for sc in sorted(spec["mixes"]):
        t = load(f"Implementation/Content/Narrative/Deliveries/{sc}/{sc}_timing_v1.json")
        s03 = next(x for x in t["shots"] if x["shotId"] == f"{sc}_S03")
        if not s03.get("dialogue") or s03["dialogue"]["windowSeconds"] != [12.5, 17.5]:
            err(f"{sc}_S03: dialogue window != [12.5, 17.5]")
        else:
            ok()
        if s03["dialogue"].get("speaker") != "LETTER_RECIPIENT" or not s03["dialogue"].get("onscreen"):
            err(f"{sc}_S03: dialogue speaker/onscreen != LETTER_RECIPIENT/true")
        else:
            ok()
        rec = next(x for x in man["shots"] if x["shotId"] == f"{sc}_S03")
        if "dialogueStagingNote" not in rec:
            err(f"{sc}_S03: manifest has no dialogue staging note")
        else:
            ok()

    # --- per-shot: hold slice probe + SHA + fidelity + drift + contact pixels
    for s in spec["shots"]:
        sid = s["shotId"]
        rec = next(x for x in man["shots"] if x["shotId"] == sid)
        hs = man["holdSlices"][sid]
        if sha256(ROOT / hs["file"]) != hs["sha256"]:
            err(f"{sid}: hold slice SHA mismatch")
        else:
            ok()
        if hs["sha256"] != rec["holdSliceSha256"]:
            err(f"{sid}: manifest record SHA != hold slice SHA")
        else:
            ok()
        info = probe(ROOT / hs["file"])
        vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
        if (vs["width"], vs["height"]) != (640, 360) or int(vs["nb_frames"]) != 180:
            err(f"{sid}: hold slice video {vs['width']}x{vs['height']} frames {vs['nb_frames']}")
        else:
            ok()
        if abs(float(info["format"]["duration"]) - 6.0) > 0.05:
            err(f"{sid}: hold slice duration {info['format']['duration']}")
        else:
            ok()
        if [x for x in info["streams"] if x["codec_type"] == "audio"]:
            err(f"{sid}: hold slice must be silent")
        else:
            ok()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            diffs = {}
            for t in (1.0, 3.0, 5.0):
                extract_frame(ROOT / hs["file"], t, td / f"h{t}.png")
                extract_frame(ROOT / hs["sourceRuntime"], hs["sourceStartSeconds"] + t, td / f"a{t}.png")
                diffs[f"{t}s"] = mean_abs_diff(
                    Image.open(td / f"h{t}.png").convert("RGB"),
                    Image.open(td / f"a{t}.png").convert("RGB"))
            if diffs != rec["vsRuntimeMeanAbsDiff"]:
                err(f"{sid}: vs-runtime diffs {diffs} != manifest {rec['vsRuntimeMeanAbsDiff']}")
            else:
                ok()
            if any(d >= 5 for d in diffs.values()):
                err(f"{sid}: vs-runtime diff >= 5: {diffs}")
            else:
                ok()
            extract_frame(ROOT / hs["file"], 0.0, td / "first.png")
            extract_frame(ROOT / hs["file"], 5.9, td / "last.png")
            drift = mean_abs_diff(Image.open(td / "first.png").convert("RGB"),
                                  Image.open(td / "last.png").convert("RGB"))
            if drift != rec["kenBurnsDriftFirstLast"]:
                err(f"{sid}: drift {drift} != manifest {rec['kenBurnsDriftFirstLast']}")
            else:
                ok()
            if drift <= 0:
                err(f"{sid}: hold slice frozen (drift 0)")
            else:
                ok()
            # contact sheet pixels re-derived
            c = man["contacts"][sid]
            if sha256(ROOT / c["file"]) != c["sha256"]:
                err(f"{sid}: contact SHA mismatch")
            else:
                ok()
            kf = Image.open(ROOT / s["keyframe"]["file"]).convert("RGB").resize((320, 180), Image.NEAREST)
            tiles = [kf]
            for t in SAMPLE_SECONDS:
                extract_frame(ROOT / hs["file"], t, td / f"s{t}.png")
                tiles.append(Image.open(td / f"s{t}.png").convert("RGB").resize((320, 180), Image.NEAREST))
            sheet = Image.new("RGB", (320 * 6, 180), (255, 255, 255))
            for i, tile in enumerate(tiles):
                sheet.paste(tile, (i * 320, 0))
            disk = Image.open(ROOT / c["file"]).convert("RGB")
            if hashlib.sha256(disk.tobytes()).hexdigest() != hashlib.sha256(sheet.tobytes()).hexdigest():
                err(f"{sid}: contact pixels != re-derived sheet")
            else:
                ok()

    # --- scene take + AB (mixed pose + hold)
    for sc in sorted(spec["mixes"]):
        st = man["sceneTakes"][sc]
        if sha256(ROOT / st["file"]) != st["sha256"]:
            err(f"{sc}: scene take SHA mismatch")
        else:
            ok()
        info = probe(ROOT / st["file"])
        if abs(float(info["format"]["duration"]) - 18.0) > 0.05:
            err(f"{sc}: scene take duration {info['format']['duration']} != 18.0")
        else:
            ok()
        vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
        if int(vs["nb_frames"]) != 540:
            err(f"{sc}: scene take frames {vs['nb_frames']} != 540")
        else:
            ok()
        au = [x for x in info["streams"] if x["codec_type"] == "audio"]
        if not au or au[0]["codec_name"] != "aac" or int(au[0]["sample_rate"]) != 48000:
            err(f"{sc}: scene take audio not AAC 48kHz")
        else:
            ok()
        expect = [{"shotId": "CIN_020_S01", "kind": "POSE_ANIMATION"},
                  {"shotId": "CIN_020_S02", "kind": "POSE_ANIMATION"},
                  {"shotId": "CIN_020_S03", "kind": "KEN_BURNS_HOLD"}]
        if st["segments"] != expect:
            err(f"{sc}: scene take segments {st['segments']} != {expect}")
        else:
            ok()
        # segment boundaries: B take frame at 0.0/6.0/12.0 s matches the
        # corresponding segment start frame (< 5)
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            for boundary, seg_file in ((0.0, spec["poseTakes"]["CIN_020_S01"]["file"]),
                                       (6.0, spec["poseTakes"]["CIN_020_S02"]["file"]),
                                       (12.0, man["holdSlices"]["CIN_020_S03"]["file"])):
                extract_frame(ROOT / st["file"], boundary, td / "b.png")
                extract_frame(ROOT / seg_file, 0.0, td / "s.png")
                d = mean_abs_diff(Image.open(td / "b.png").convert("RGB"),
                                  Image.open(td / "s.png").convert("RGB"))
                if d >= 5:
                    err(f"{sc}: B take at {boundary}s differs from segment start by {d}")
                else:
                    ok()
        ab = man["abVideos"][sc]
        if sha256(ROOT / ab["file"]) != ab["sha256"]:
            err(f"{sc}: AB SHA mismatch")
        else:
            ok()
        info = probe(ROOT / ab["file"])
        vs = [x for x in info["streams"] if x["codec_type"] == "video"][0]
        if (vs["width"], vs["height"]) != (640, 720) or int(vs["nb_frames"]) != 540:
            err(f"{sc}: AB size/frames {vs['width']}x{vs['height']}/{vs['nb_frames']}")
        else:
            ok()
        if abs(float(info["format"]["duration"]) - 18.0) > 0.05:
            err(f"{sc}: AB duration != 18.0")
        else:
            ok()
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            for mid in (9.0, 15.0):
                extract_frame(ROOT / ab["file"], mid, td / "ab.png")
                extract_frame(ROOT / spec["mixes"][sc]["runtimeMp4"], mid, td / "a.png")
                extract_frame(ROOT / st["file"], mid, td / "b.png")
                ab_im = Image.open(td / "ab.png").convert("RGB")
                a_im = Image.open(td / "a.png").convert("RGB")
                b_im = Image.open(td / "b.png").convert("RGB")
                d_top = mean_abs_diff(ab_im.crop((0, 40, 640, 360)),
                                      a_im.crop((0, 40, 640, 360)))
                d_bot = mean_abs_diff(ab_im.crop((0, 400, 640, 720)),
                                      b_im.crop((0, 40, 640, 360)))
                if d_top > 5 or d_bot > 5:
                    err(f"{sc}: AB halves differ from A/B takes at {mid}s (top {d_top}, bottom {d_bot})")
                else:
                    ok()
                print(f"{sc}: AB at {mid}s halves vs takes top {d_top} bottom {d_bot}")
            # fidelity proof, hold window only: A half vs B half at 15.0 s
            extract_frame(ROOT / ab["file"], 15.0, td / "ab15.png")
            ab_im = Image.open(td / "ab15.png").convert("RGB")
            d_ab = mean_abs_diff(ab_im.crop((0, 40, 640, 360)),
                                 ab_im.crop((0, 400, 640, 720)))
            if d_ab >= 5:
                err(f"{sc}: A half vs B half at 15.0s differ by {d_ab} (not a faithful hold re-cut)")
            else:
                ok()
            print(f"{sc}: AB A-vs-B at 15.0s {d_ab}")

    result = {
        "validator": "check_campaign_motion_p2c_v1.py",
        "manifest": "Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_v1.json",
        "spec": "Implementation/Content/Narrative/Deliveries/CAMPAIGN_MOTION_P2C_SPEC_v1.json",
        "checks": checked, "mismatches": errors,
        "status": "PASS" if not errors else "FAIL",
    }
    out = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP3C_VALIDATION_20261112.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"VALIDATION {result['status']}: {checked} checks, {len(errors)} mismatches -> {out}")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
