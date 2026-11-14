#!/usr/bin/env python3
"""MEDIA-02 checkpoint 32 (Goi 31 item 2): revise campaign keyframes with
content errors and re-export the affected scenes.

Codex review (issue #116 comment 6670983075, Work Order 31) found three
shot errors that need no character lock, plus unprompted mascot/character
cleanup, bandage side and environment continuity:

  CIN_012_S03  baked-in English choice UI bar ("WAIT IN SILENCE" /
               "OFFER THE PAPERS") -- frame must stay clean for the
               game's own choice overlay.
  CIN_017_S02  crystal core / serpent missing -- rendered as a bamboo
               pipe machine with glowing orbs + invented robed man.
  CIN_015_S02  dry above-water courtyard + pale mascot instead of the
               drowned ruin (dining bowl, guide rope, bare diver hand).
  CIN_012_S01  white hooded mascot intrusion + dark-blue dusk palette
               instead of the stepped orange heat palette.
  CIN_015_S01  unscripted lantern figure standing dry on a ruin wall
               + overly dense bubble columns.
  CIN_015_S03  weak underwater read (dry interior, slate-purple).
  CIN_017_S03  invented armed figure at frame left (shot is only the
               receding silhouette) + dotted glint rows on the water.
  CIN_008_S03  bandage reads on the RIGHT forearm; canon is LEFT.
  CIN_011_S01/S03  unnamed teal-robed woman in no prompt.
  CIN_010_S02/S03  environment continuity collapse (desert -> bamboo
               grove -> rocky scrub); Sam reads as a slim young man,
               not the stocky middle-aged merchant.
  CIN_006_S02  oversized blurred gloved hand + pale face-like shape
               intruding from frame right; resin as splash, not fiber.
  CIN_009_S01  invented small white hooded figure; darker/bluer than
               a daylight payoff.

Revised keyframes were generated in parallel staging runs from the pack
shot prompts verbatim PLUS an explicit repair suffix (the verbatim
prompt alone under-specifies the shot and is what let the generator
invent the UI/mascot/machine). Staging WebPs live in
~/workspace/goals/ng-m-ch-continuous-development/hidden_files/
cin<NNN>_keyframes_staging/ with handover notes; the revised staging
records are supplied as JSON (default path below).

This script re-exports ONLY the 8 affected scenes (CIN_006, CIN_008,
CIN_009, CIN_010, CIN_011, CIN_012, CIN_015, CIN_017) with the SAME
motion model per shot as the original take (labels read back from the
old scene export manifest, so a zoom-out S03 stays a zoom-out). The
other 12 campaign scenes are untouched. Unchanged shots are
re-downscaled from their original staging and must reproduce byte-identical
keyframes (determinism guard); revised shots get new SHAs. Before/after
contact sheets (old keyframe left, revised right) are written per revised
shot next to the keyframes.

Motion is still animatic-level Ken Burns on storyboard stills -- NOT a
final pose-animated take (pack pose cadence 8-12 fps needs approved
character reference + pose animation). The clips carry NO audio track
and NO baked subtitles.

Pack: Implementation/Content/Narrative/Cinema_Production_Pack_v1.json
sha256 09e8685f42bcbd4f559c36c220a2d86bce96121749d46445f436aac758b93148.
Base: integration abcf254 (PR #123 merged).
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_campaign_batch_video as batch  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STAGING_ROOT = Path("/home/hatch/workspace/goals/"
                    "ng-m-ch-continuous-development/hidden_files")
DELIVERIES = ROOT / "Implementation/Content/Narrative/Deliveries"
PACK = ROOT / "Implementation/Content/Narrative/Cinema_Production_Pack_v1.json"
CAMP_MANIFEST = DELIVERIES / "CAMPAIGN_timing_manifest_v1.json"
REVISED_DEFAULT = (STAGING_ROOT / "cp32_revised_staging.json")
PACK_SHA = "09e8685f42bcbd4f559c36c220a2d86bce96121749d46445f436aac758b93148"
BASE_SHA = "abcf254"
BRANCH = "muse/media-production-20261104"
DECISION = "DEC-MEDIA-P0-20261105"
FPS = 30
W, H = 640, 360
DUR = 18.0
CHECKPOINT = ("MEDIA-02 checkpoint 32 - {sid} revised take "
              "(Goi 31 item 2): shot-content fixes + re-export "
              "(Ken Burns animatic motion on 3 storyboard keyframes, "
              "18 s / 3 shots)")

REVISION_NOTES = {
    "CIN_006": ("Checkpoint 32 (Goi 31 item 2) revises S02: the oversized "
                "blurred gloved hand and pale face-like intrusion from "
                "frame right are removed; the green resin now reads as a "
                "fiber trapped inside the rough paper. S01/S03 unchanged "
                "from checkpoint 22."),
    "CIN_008": ("Checkpoint 32 (Goi 31 item 2) revises S03: the bandage "
                "now wraps the LEFT forearm (outer side, away from the "
                "pool); the bandaged hand holds nothing. S01/S02 "
                "unchanged from checkpoint 25."),
    "CIN_009": ("Checkpoint 32 (Goi 31 item 2) revises S01: the invented "
                "white hooded figure is removed; the spring reads as a "
                "bright daylight payoff. S02/S03 unchanged from "
                "checkpoint 23."),
    "CIN_010": ("Checkpoint 32 (Goi 31 item 2) revises S02/S03: "
                "environment continuity restored to the ash-gold desert "
                "caravan rest of S01; Sam Chu Quy is now a stocky "
                "middle-aged merchant; the communal vessel is the lidded "
                "barrel and the flask is clay. S01 unchanged from "
                "checkpoint 25."),
    "CIN_011": ("Checkpoint 32 (Goi 31 item 2) revises S01/S03: the "
                "unnamed teal-robed woman is removed; S01's relief is "
                "three joined copper fragments; S03 is a detail close "
                "view of the copper relief with Ha Mac alone. S02 "
                "unchanged from checkpoint 25."),
    "CIN_012": ("Checkpoint 32 (Goi 31 item 2) revises S01/S03: S03's "
                "baked-in English choice UI bar is removed -- the frame "
                "is clean for the game's own choice overlay; S01's white "
                "hooded mascot is removed and the stepped orange heat "
                "palette is restored. S02 unchanged from checkpoint 25."),
    "CIN_015": ("Checkpoint 32 (Goi 31 item 2) revises S01/S02/S03: S02 "
                "is now a fully submerged drowned ruin (dining bowl tied "
                "to a stone table, guide rope, bare diver hand, no "
                "mascot, no clay pot); S01 has no unscripted figure and "
                "restrained bubbles; S03 reads underwater with deep teal "
                "tint and bubbles."),
    "CIN_017": ("Checkpoint 32 (Goi 31 item 2) revises S02/S03: S02 now "
                "shows the white-blue crystal core supported by three "
                "stone pressure channels with the tide serpent coiled "
                "around it (no machine, no robed man); S03 is only the "
                "receding serpent silhouette (no armed figure, no dotted "
                "glints). S01 unchanged from checkpoint 25."),
}

# Per-scene staging dir slug + characters + status note. Batch scenes
# reuse build_campaign_batch_video.SCENES for title/dialogue/extra notes
# context; CIN_006/CIN_009 keep their own builders' status notes.
SCENE_META = {
    "CIN_006": {
        "slug": "cin006",
        "characters": ["NPC_HA_MAC", "NPC_SAM_CHU_QUY"],
        "statusNote": (
            "Storyboard-level keyframes generated from the pack shot "
            "prompts verbatim; NOT final picture. CIN_006 names "
            "NPC_HA_MAC and NPC_SAM_CHU_QUY but no approved character "
            "lock exists for either, so their faces and costumes here "
            "are placeholders; per DEC-MEDIA-P0 Q4 they are "
            "cinematic-only staging and these frames create no "
            "persistent design canon."),
    },
    "CIN_008": {
        "slug": "cin008",
        "characters": ["NPC_TA_VAN_KHANH"],
        "statusNote": None,  # generic batch note (filled from old manifest)
    },
    "CIN_009": {
        "slug": "cin009",
        "characters": [],
        "statusNote": (
            "Storyboard-level keyframes generated from the pack shot "
            "prompts verbatim; NOT final picture. CIN_009 has an empty "
            "pack character list, so no named character lock blocks "
            "these pictures; the three workers in S02 are unnamed "
            "generation-invented figures, not canon designs."),
    },
    "CIN_010": {
        "slug": "cin010",
        "characters": ["NPC_SAM_CHU_QUY"],
        "statusNote": None,
    },
    "CIN_011": {
        "slug": "cin011",
        "characters": ["NPC_HA_MAC"],
        "statusNote": None,
    },
    "CIN_012": {
        "slug": "cin012",
        "characters": ["NPC_HA_MAC"],
        "statusNote": None,
    },
    "CIN_015": {
        "slug": "cin015",
        "characters": ["NPC_DIVER_LEAD"],
        "statusNote": None,
    },
    "CIN_017": {
        "slug": "cin017",
        "characters": ["BOSS_TIDE_SERPENT"],
        "statusNote": None,
    },
}

BATCH_BY_ID = {s["sceneId"]: s for s in batch.SCENES}
GENERIC_STATUS = (
    "Storyboard-level keyframes generated from the pack shot prompts "
    "verbatim; NOT final picture. The scene's on-screen characters "
    "({chars}) have no approved cinematic character lock, so faces and "
    "costumes are storyboard placeholders under DEC-MEDIA-P0-20261105; "
    "final picture per shot stays blocked on the character lock.")


def motion_for_label(idx, label):
    """(kind, zoompan expr, identity_s, identity_frame, motion_s, mid_s).

    Preserves each shot's ORIGINAL motion kind (from the old export
    manifest): a zoom-out S03 stays a zoom-out; push-ins keep the
    batch factors (S02 1.10, others 1.08).
    """
    if label.startswith("zoom-out"):
        return ("zoom-out centered",
                "zoompan=z='1.08-0.08*on/179':x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':d=180:s=640x360:fps=30",
                17.9667, 539, 12.0, 15.0)
    if idx == 0:
        return (label,
                "zoompan=z='1+0.08*on/179':x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':d=180:s=640x360:fps=30",
                0.0, None, 5.9, 3.0)
    if idx == 1:
        return (label,
                "zoompan=z='1+0.10*on/179':x='iw/2-(iw/zoom/2)':"
                "y='ih/2-(ih/zoom/2)':d=180:s=640x360:fps=30",
                6.0, None, 11.9, 9.0)
    return (label,
            "zoompan=z='1+0.08*on/179':x='iw/2-(iw/zoom/2)':"
            "y='ih/2-(ih/zoom/2)':d=180:s=640x360:fps=30",
            12.0, None, 17.9, 15.0)


def dialogue_note_from(old_notes):
    for n in old_notes or []:
        if ("dialogue window" in n or "VO draft" in n
                or "dialogueCues" in n):
            return n
    return ""


def build_scene(sid, revised, camp, pack_sha, tmp):
    from PIL import Image
    meta = SCENE_META[sid]
    failures = []

    def check(cond, msg):
        if not cond:
            failures.append(msg)

    checkpoint = CHECKPOINT.format(sid=sid)
    staging = STAGING_ROOT / f"{meta['slug']}_keyframes_staging"
    key_dir = ROOT / "Art_Source/Cinematics/Campaign" / sid / "keyframes_16x9"
    cine_dest = ROOT / "ClientGodot/assets/cinematics" / sid
    old_kf_manifest_path = (key_dir.parent
                            / f"{sid.replace('_', '')}"
                              "_keyframes_manifest_v1.json")
    old_exp_path = cine_dest / "scene_export_manifest_v1.json"
    check(old_kf_manifest_path.exists(), f"{sid}: old keyframe manifest missing")
    check(old_exp_path.exists(), f"{sid}: old export manifest missing")
    if failures:
        raise RuntimeError("; ".join(failures))
    old_kf = json.loads(old_kf_manifest_path.read_text(encoding="utf-8"))
    old_exp = json.loads(old_exp_path.read_text(encoding="utf-8"))
    old_entries = {e["shotId"]: e for e in old_kf["keyframes"]}
    old_motion = old_exp.get("motionModel", {}).get("shots", {})
    title = old_kf["title"]
    camp_by_id = {s["sceneId"]: s for s in camp["scenes"]}
    if sid in camp_by_id:
        camp_rec = camp_by_id[sid]
    elif sid == "CIN_006":
        # CIN_006 (like the other P0/P1 scenes) is not in the campaign
        # timing manifest; its record lives in its own timing manifest.
        camp_rec = json.loads(
            (DELIVERIES / sid / f"{sid}_timing_manifest_v1.json")
            .read_text(encoding="utf-8"))["scene"]
    else:
        raise RuntimeError(f"{sid}: no campaign record found")
    revised_ids = sorted(s for s in revised if s.startswith(sid + "_"))
    check(bool(revised_ids), f"{sid}: no revised shots in REVISED json")

    # --- 1. Staging verification + keyframes (old keyframes saved aside
    # for before/after contact sheets before any overwrite).
    before_dir = tmp / f"{sid}_before"
    before_dir.mkdir(parents=True, exist_ok=True)
    keyframes = {}
    new_entries = []
    for shot_id in sorted(old_entries):
        entry = old_entries[shot_id]
        if shot_id in revised:
            src_data = revised[shot_id]
            is_revised = True
        else:
            src_data = {
                "file": entry["sourceStagingFile"],
                "sha256": entry["sourceStagingSha256"],
                "snapshotId": entry["sourceSnapshotId"],
                "framing": entry["framing"],
                "defects": entry["knownDefects"],
            }
            is_revised = False
        src = staging / src_data["file"]
        check(src.exists(), f"{shot_id}: staging file missing")
        if not src.exists():
            continue
        check(not batch.is_lfs_pointer(src), f"{shot_id}: staging is LFS pointer")
        check(batch.sha256(src) == src_data["sha256"],
              f"{shot_id}: staging sha mismatch")
        im = Image.open(src).convert("RGB")
        check(im.size == (2048, 1152),
              f"{shot_id}: staging size {im.size} != 2048x1152")
        kf = key_dir / f"keyframe_{shot_id}.png"
        if kf.exists():
            shutil.copyfile(kf, before_dir / kf.name)
        im.resize((W, H), Image.LANCZOS).save(kf)
        check(kf.exists() and not batch.is_lfs_pointer(kf),
              f"{shot_id}: keyframe not real bytes")
        check(Image.open(kf).size == (W, H),
              f"{shot_id}: keyframe size != 640x360")
        if not is_revised:
            check(batch.sha256(kf) == entry["sha256"],
                  f"{shot_id}: unchanged shot keyframe NOT byte-identical "
                  f"to the checkpoint-25/22/23 downscale (staging drift?)")
        keyframes[shot_id] = kf
        new_entries.append({
            "shotId": shot_id,
            "camera": entry["camera"],
            "file": f"keyframes_16x9/keyframe_{shot_id}.png",
            "width": W, "height": H,
            "sha256": batch.sha256(kf),
            "sourceStagingFile": src_data["file"],
            "sourceStagingSha256": src_data["sha256"],
            "sourceSnapshotId": src_data["snapshotId"],
            "framing": src_data["framing"],
            "knownDefects": src_data["defects"],
        })

    status_note = meta["statusNote"] or GENERIC_STATUS.format(
        chars=", ".join(meta["characters"]))
    status_note += (f" Checkpoint 32 (Goi 31 item 2) revises "
                    f"{', '.join(revised_ids)}; all other shots unchanged.")
    kf_manifest = {
        "manifestId": old_kf["manifestId"],
        "checkpoint": checkpoint,
        "decisionId": DECISION,
        "branch": BRANCH,
        "baseSha": BASE_SHA,
        "sceneId": sid,
        "title": title,
        "packSha256": pack_sha,
        "status": "STORYBOARD",
        "statusNote": status_note,
        "keyframes": new_entries,
        "notes": [
            "3 separate 16:9 keyframes, one per shot, 640x360 each.",
            REVISION_NOTES[sid],
        ],
    }
    old_kf_manifest_path.write_text(
        json.dumps(kf_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    # --- before/after contact sheets (old left, revised right).
    contact_shas = {}
    for shot_id in revised_ids:
        before_png = before_dir / f"keyframe_{shot_id}.png"
        after_png = keyframes[shot_id]
        sheet = Image.new("RGB", (W * 2, H), (0, 0, 0))
        sheet.paste(Image.open(before_png).convert("RGB"), (0, 0))
        sheet.paste(Image.open(after_png).convert("RGB"), (W, 0))
        out = key_dir / f"before_after_{shot_id}_cp32.png"
        sheet.save(out)
        contact_shas[shot_id] = {
            "file": f"keyframes_16x9/before_after_{shot_id}_cp32.png",
            "sha256": batch.sha256(out),
            "sizeBytes": out.stat().st_size,
        }

    # --- 2. Timing + SRT copies, cross-checked (same as batch builder).
    timing_src = DELIVERIES / sid / f"{sid}_timing_v1.json"
    srt_src = DELIVERIES / sid / f"{sid}_vi.srt"
    check(timing_src.exists(), f"{sid}: timing missing")
    check(srt_src.exists(), f"{sid}: srt missing")
    timing = json.loads(timing_src.read_text(encoding="utf-8"))
    srt_text = srt_src.read_text(encoding="utf-8")
    check(timing.get("title") == title,
          f"{sid}: title {timing.get('title')!r} != registry {title!r}")
    timing_dialogues = sum(
        1 for sh in timing.get("shots", [])
        if isinstance(sh.get("dialogue"), dict))
    srt_cues = batch.count_srt_cues(srt_text)
    check(srt_cues is not None, f"{sid}: unparseable SRT")
    if srt_cues is not None:
        check(timing_dialogues == srt_cues,
              f"{sid}: timing dialogues {timing_dialogues} != SRT cues "
              f"{srt_cues}")
    check(batch.sha256(srt_src) == camp_rec["srtSha256"],
          f"{sid}: source SRT sha != campaign manifest record")
    check(timing["durationSeconds"] == DUR,
          f"{sid}: timing duration {timing['durationSeconds']} != 18")
    timing_dest = cine_dest / timing_src.name
    srt_dest = cine_dest / srt_src.name
    shutil.copyfile(timing_src, timing_dest)
    shutil.copyfile(srt_src, srt_dest)
    check(batch.sha256(timing_dest) == batch.sha256(timing_src),
          f"{sid}: timing copy sha mismatch")
    check(batch.sha256(srt_dest) == camp_rec["srtSha256"],
          f"{sid}: srt copy sha mismatch")

    # --- 3. Animated clip render (one filter_complex, 3 zoompan shots).
    from PIL import Image as _Image  # noqa: F401  (kept explicit)
    motions = {}
    inputs, filt = [], []
    shot_ids = [e["shotId"] for e in new_entries]
    for i, shot_id in enumerate(shot_ids):
        label = old_motion.get(shot_id, "push-in centered")
        kind, zp, id_s, id_f, mo_s, mid_s = motion_for_label(i, label)
        motions[shot_id] = {
            "kind": kind, "zoompan": zp, "identity": id_s,
            "identityFrame": id_f, "motion": mo_s, "mid": mid_s}
        up = tmp / f"{sid}_{shot_id}_1280.png"
        Image.open(keyframes[shot_id]).resize(
            (1280, 720), Image.LANCZOS).save(up)
        inputs += ["-i", str(up)]
        filt.append(f"[{i}:v]{zp}[v{i}]")
    filt.append("[v0][v1][v2]concat=n=3:v=1:a=0,format=yuv420p[vout]")
    mp4 = cine_dest / f"{sid}_640x360_30fps.mp4"
    ogv = cine_dest / f"{sid}_640x360_30fps.ogv"
    poster = cine_dest / f"{sid}_poster.png"
    shutil.copyfile(keyframes[shot_ids[0]], poster)
    batch.run(["ffmpeg", "-y", "-v", "error"] + inputs +
              ["-filter_complex", ";".join(filt), "-map", "[vout]",
               "-c:v", "libx264", "-r", str(FPS), "-t", str(DUR), str(mp4)])
    batch.run(["ffmpeg", "-y", "-v", "error"] + inputs +
              ["-filter_complex", ";".join(filt), "-map", "[vout]",
               "-c:v", "libtheora", "-r", str(FPS), "-t", str(DUR), str(ogv)])

    # --- 4. ffprobe verification.
    manifest_files = {}
    for path, want_codec in ((mp4, "h264"), (ogv, "theora")):
        check(path.exists(), f"{sid}: missing {path.name}")
        check(not batch.is_lfs_pointer(path),
              f"{sid}: clip is LFS pointer {path.name}")
        info = batch.probe_video(path)
        stream = info["streams"][0]
        check(stream["codec_name"] == want_codec,
              f"{sid} {path.name}: codec {stream['codec_name']}")
        check((stream["width"], stream["height"]) == (W, H),
              f"{sid} {path.name}: size mismatch")
        frames = int(stream.get("nb_read_frames")
                     or stream.get("nb_frames") or 0)
        if want_codec == "h264":
            check(stream["avg_frame_rate"] in ("30/1", "30"),
                  f"{sid} {path.name}: fps {stream['avg_frame_rate']}")
            check(frames == int(DUR * FPS),
                  f"{sid} {path.name}: frames {frames} != 540")
        else:
            check(0 < frames < int(DUR * FPS),
                  f"{sid} {path.name}: stored frames {frames} outside "
                  f"(0, 540)")
        dur = float(info["format"]["duration"])
        check(abs(dur - DUR) <= 0.02,
              f"{sid} {path.name}: duration {dur} != {DUR}")
        entry = {
            "path": f"assets/cinematics/{sid}/{path.name}",
            "sha256": batch.sha256(path),
            "sizeBytes": path.stat().st_size,
            "codec": want_codec,
            "width": W, "height": H,
            "fps": FPS,
            "durationSeconds": round(dur, 4),
        }
        entry["frames" if want_codec == "h264" else "storedFrames"] = frames
        manifest_files["mp4" if want_codec == "h264" else "ogv"] = entry

    # --- 5. Frame identity + motion proof on the MP4.
    frame_check = {}
    for shot_id in shot_ids:
        fc = motions[shot_id]
        kf_img = Image.open(keyframes[shot_id])
        per = {}
        for label, at_s in (("identity", fc["identity"]),
                            ("motion", fc["motion"]),
                            ("mid", fc["mid"])):
            fp = tmp / f"{sid}_{shot_id}_{label}.png"
            if label == "identity" and fc["identityFrame"] is not None:
                batch.extract_frame_n(mp4, fc["identityFrame"], fp)
            else:
                batch.extract_frame(mp4, at_s, fp)
            per[label] = batch.mean_abs_diff(Image.open(fp), kf_img)
        check(per["identity"] < batch.FRAME_DIFF_MAX,
              f"{shot_id}: identity diff {per['identity']:.2f} >= 10")
        check(per["motion"] > batch.MOTION_DIFF_MIN,
              f"{shot_id}: motion diff {per['motion']:.2f} <= 1.5")
        cont = batch.mean_abs_diff(
            Image.open(tmp / f"{sid}_{shot_id}_mid.png"),
            Image.open(tmp / f"{sid}_{shot_id}_motion.png"))
        check(cont > batch.CONTINUOUS_DIFF_MIN,
              f"{shot_id}: mid vs end diff {cont:.2f} <= 0.5")
        frame_check[shot_id] = {
            "identitySeconds": fc["identity"],
            "identityMeanAbsChannelDiff": round(per["identity"], 3),
            "identityMaxAllowed": batch.FRAME_DIFF_MAX,
            "motionSeconds": fc["motion"],
            "motionMeanAbsChannelDiff": round(per["motion"], 3),
            "motionMinRequired": batch.MOTION_DIFF_MIN,
            "continuousMotionMeanAbsChannelDiff": round(cont, 3),
            "continuousMinRequired": batch.CONTINUOUS_DIFF_MIN,
        }
    check(batch.sha256(poster) == batch.sha256(keyframes[shot_ids[0]]),
          f"{sid}: poster sha != S01 keyframe sha")
    manifest_files["poster"] = {
        "path": f"assets/cinematics/{sid}/{poster.name}",
        "sha256": batch.sha256(poster),
        "sizeBytes": poster.stat().st_size,
        "sourceKeyframe": f"keyframe_{shot_ids[0]}.png",
    }
    manifest_files["timing"] = {
        "path": f"assets/cinematics/{sid}/{timing_src.name}",
        "sha256": batch.sha256(timing_dest),
        "sizeBytes": timing_dest.stat().st_size,
    }
    manifest_files["srt"] = {
        "path": f"assets/cinematics/{sid}/{srt_src.name}",
        "sha256": batch.sha256(srt_dest),
        "sizeBytes": srt_dest.stat().st_size,
        "status": "DRAFT",
    }

    dialogue_note = dialogue_note_from(old_exp.get("notes"))
    export_manifest = {
        "schemaVersion": 1,
        "checkpoint": checkpoint,
        "decisionId": DECISION,
        "branch": BRANCH,
        "baseSha": BASE_SHA,
        "sceneId": sid,
        "title": timing.get("title"),
        "durationSeconds": DUR,
        "dialogueCues": timing_dialogues,
        "dialogueWindowStatus": camp_rec.get("dialogueWindowStatus"),
        "videoStatus": "VIDEO_ANIMATED_TAKE_KEN_BURNS",
        "motionModel": {
            "kind": "ANIMATIC_MOTION_KEN_BURNS",
            "method": ("ffmpeg zoompan on 1280x720 upscales of the "
                       "640x360 storyboard keyframes; no optical flow, "
                       "no morphing"),
            "shots": {s: motions[s]["kind"] for s in shot_ids},
        },
        "reelOffsetSeconds": None,
        "reelTotalSeconds": None,
        "files": manifest_files,
        "frameCheck": frame_check,
        "shots": [
            {"shotId": s["shotId"],
             "startSeconds": s["startSeconds"],
             "endSeconds": s["endSeconds"],
             "camera": s["camera"],
             "keyframe": f"keyframe_{s['shotId']}.png",
             "motion": motions[s["shotId"]]["kind"]}
            for s in timing.get("shots", [])
        ],
        "notes": [
            ("Campaign revised take (Goi 31 item 2, checkpoint 32): "
             "shot-content fixes, real camera motion, not a panel hold. "
             "Motion is animatic-level Ken Burns; NOT a final "
             "pose-animated take (pack pose cadence 8-12 fps needs "
             "approved character reference + pose animation)."),
            "No audio track in the clip: VO/music/ambience are added "
            "separately in editing per the pack dialoguePolicy. No "
            "baked subtitles.",
            f"{sid} is NOT part of the 72 s P0 reel; it has no reel "
            "offset. The reel stays review/gallery only, NOT auto-run "
            "as opening.",
            dialogue_note,
            REVISION_NOTES[sid],
        ],
    }
    old_exp_path.write_text(
        json.dumps(export_manifest, ensure_ascii=False, indent=1),
        encoding="utf-8")

    if failures:
        raise RuntimeError("; ".join(failures[:6])
                           + (f" (+{len(failures) - 6} more)"
                              if len(failures) > 6 else ""))
    return {
        "sceneId": sid,
        "revisedShots": revised_ids,
        "mp4Sha256": manifest_files["mp4"]["sha256"],
        "ogvSha256": manifest_files["ogv"]["sha256"],
        "ogvStoredFrames": manifest_files["ogv"]["storedFrames"],
        "posterSha256": manifest_files["poster"]["sha256"],
        "identity": [frame_check[s]["identityMeanAbsChannelDiff"]
                     for s in shot_ids],
        "motion": [frame_check[s]["motionMeanAbsChannelDiff"]
                   for s in shot_ids],
        "dialogueCues": timing_dialogues,
        "beforeAfter": contact_shas,
        "newKeyframeShas": {e["shotId"]: e["sha256"][:8]
                            for e in new_entries if e["shotId"] in revised},
    }


def main() -> int:
    revised_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REVISED_DEFAULT
    only = sys.argv[2:] or None
    if not revised_path.exists():
        print(f"FAIL: revised staging json missing: {revised_path}")
        return 1
    revised = json.loads(revised_path.read_text(encoding="utf-8"))
    camp = json.loads(CAMP_MANIFEST.read_text(encoding="utf-8"))
    pack_sha = batch.sha256(PACK)
    if pack_sha != PACK_SHA:
        print(f"FAIL: pack sha {pack_sha} != recorded {PACK_SHA}")
        return 1
    # Integration base must be the recorded one.
    try:
        head = subprocess.run(
            ["git", "rev-parse", "--short",
             "origin/codex/story-gameplay-integration-20261031"],
            capture_output=True, text=True, cwd=str(ROOT),
            check=True).stdout.strip()
        if head != BASE_SHA:
            print(f"FAIL: integration head {head} != recorded base "
                  f"{BASE_SHA}; update BASE_SHA / re-baseline first")
            return 1
    except subprocess.CalledProcessError as e:
        print(f"FAIL: cannot resolve integration head: {e}")
        return 1
    tmp = Path(tempfile.mkdtemp(prefix="campaign_revise_cp32_"))
    results, failures = [], []
    try:
        for sid in SCENE_META:
            if only and sid not in only:
                continue
            try:
                r = build_scene(sid, revised, camp, pack_sha, tmp)
                results.append(r)
                print(f"OK {r['sceneId']}: revised {r['revisedShots']} "
                      f"mp4 {r['mp4Sha256'][:8]} ogv {r['ogvSha256'][:8]} "
                      f"({r['ogvStoredFrames']} stored) "
                      f"poster {r['posterSha256'][:8]} "
                      f"identity {r['identity']} motion {r['motion']}")
            except Exception as e:  # noqa: BLE001 - report all scenes
                failures.append((sid, str(e)))
                print(f"FAIL {sid}: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\nbuilt {len(results)}/{len(results) + len(failures)} scenes")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
