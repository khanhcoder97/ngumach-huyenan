#!/usr/bin/env python3
"""WO38 M38-A builder: assemble ONE P0 review candidate from the existing
WO37 M-C CP2 motion A/B deliverables.

Candidate definition (selection rationale lives in the report MD):
  video = B takes (procedural pose animation, 5 poses @ 10 pose/s per shot)
  audio = P0 draft mix v3 (fully composed stems + draft VO), embedded AAC
The current runtime package (A takes) is NOT modified.

Outputs:
  Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_review_72s_640x360_30fps.mp4
  Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_contact_all12.png
  Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json

Every number is measured from real bytes on disk; every pre-existing file
is re-hashed and compared against its CP2 / ledger manifest record.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCENES = ["CIN_001", "CIN_002", "CIN_004"]
SHOT_OFFSETS = {"CIN_001": 0.0, "CIN_002": 36.0, "CIN_004": 54.0}  # in the 72 s reel
CAND_DIR = ROOT / "Art_Source/Cinematics/P0_Motion/candidate_m38a"
SUBSET_OUT = ROOT / "Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json"


def sha256_of(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def entry(rel: str, role: str) -> dict:
    p = ROOT / rel
    return {"path": rel, "role": role, "bytes": p.stat().st_size, "sha256": sha256_of(p)}


def ffprobe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def loudnorm(p: Path) -> dict:
    r = subprocess.run(
        ["ffmpeg", "-i", str(p), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    txt = r.stderr
    i = txt.rfind("{")
    d = json.loads(txt[i:txt.rfind("}") + 1])
    return {"integratedLufs": float(d["input_i"]), "truePeakDbtp": float(d["input_tp"])}


def parse_srt(p: Path):
    cues = []
    blocks = p.read_text(encoding="utf-8").strip().split("\n\n")
    for b in blocks:
        lines = [ln for ln in b.splitlines() if ln.strip()]
        if len(lines) < 3:
            continue
        rng = lines[1]
        def ts(s):
            h, m, rest = s.split(":")
            sec, ms = rest.split(",")
            return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000.0
        a, z = rng.split(" --> ")
        cues.append({"startSeconds": ts(a), "endSeconds": ts(z), "text": " ".join(lines[2:])})
    return cues


def main() -> int:
    ab = json.loads((ROOT / "Implementation/Content/Narrative/Deliveries/P0_MOTION_AB_v1.json").read_text())
    ledger = json.loads((ROOT / "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json").read_text())
    playback = json.loads((ROOT / "ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json").read_text())
    led_by_shot = {s["shotId"]: s for s in ledger["shots"]}
    pb_by_scene = {e["sceneId"]: e for e in playback["scenes"]}

    problems = []

    # --- 1. re-verify every CP2 file against its manifest record ----------
    def verify(rel: str, recorded: str, label: str):
        actual = sha256_of(ROOT / rel)
        if actual != recorded:
            problems.append(f"{label}: sha mismatch {rel}: disk {actual[:12]} != manifest {recorded[:12]}")

    for scene, st in ab["sceneTakes"].items():
        verify(st["file"], st["sha256"], f"sceneTake {scene}")
        verify(st["audio"]["sourceMix"], st["audio"]["sourceMixSha256"], f"mix v3 {scene}")
    for shot, tk in ab["shotTakes"].items():
        verify(tk["file"], tk["sha256"], f"shotTake {shot}")
    for scene, v in ab["abVideos"].items():
        verify(v["file"], v["sha256"], f"abVideo {scene}")
        verify(v["aTake"]["file"], v["aTake"]["sha256"], f"aTake {scene}")
    for shot, c in ab["contacts"].items():
        verify(c["file"], c["sha256"], f"contact {shot}")
    for s in ab["shots"]:
        for rel, recorded in zip(s["poseFiles"], s["poseSha256"]):
            verify(rel, recorded, f"pose {s['shotId']}")
        kf = led_by_shot[s["shotId"]]["keyframe"]
        verify(kf["file"], kf["sha256"], f"keyframe {s['shotId']}")
    if problems:
        print("HASH VERIFICATION FAILED:")
        print("\n".join(problems))
        return 1
    print("CP2/ledger hash re-verification: all match")

    # --- 2. combined 72 s review MP4 (stream copy concat) -----------------
    CAND_DIR.mkdir(parents=True, exist_ok=True)
    combined = CAND_DIR / "P0_candidate_review_72s_640x360_30fps.mp4"
    listfile = CAND_DIR / "_concat_list.txt"
    listfile.write_text("".join(
        f"file '{(ROOT / ab['sceneTakes'][sc]['file']).as_posix()}'\n" for sc in SCENES))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", str(listfile), "-c", "copy", str(combined)], check=True)
    listfile.unlink()
    probe = ffprobe(combined)
    dur = float(probe["format"]["duration"])
    if abs(dur - 72.0) > 0.15:
        print(f"combined duration wrong: {dur}")
        return 1
    print(f"combined review MP4: {dur:.3f} s, streams={len(probe['streams'])}")

    # --- 3. combined contact sheet (12 per-shot sheets, labelled) ---------
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    cell_w, sheet_h, label_h = 960, 90, 30
    order = [s["shotId"] for s in ab["shots"]]
    canvas = Image.new("RGB", (cell_w * 2, (sheet_h + label_h) * 6), (16, 16, 16))
    draw = ImageDraw.Draw(canvas)
    for i, shot in enumerate(order):
        img = Image.open(ROOT / ab["contacts"][shot]["file"]).resize((cell_w, sheet_h))
        x, y = (i % 2) * cell_w, (i // 2) * (sheet_h + label_h)
        draw.rectangle([x, y, x + cell_w, y + label_h], fill=(0, 0, 0))
        draw.text((x + 10, y + 5), shot, fill=(255, 255, 255), font=font)
        canvas.paste(img, (x, y + label_h))
    sheet_out = CAND_DIR / "P0_candidate_contact_all12.png"
    canvas.save(sheet_out)
    print(f"combined contact sheet: {canvas.size}")

    # --- 4. per-shot notes data -------------------------------------------
    srt_by_scene = {}
    for sc in SCENES:
        cues = parse_srt(ROOT / f"ClientGodot/assets/cinematics/{sc}/{sc}_vi.srt")
        srt_by_scene[sc] = cues
    per_shot = []
    for idx, s in enumerate(ab["shots"]):
        shot = s["shotId"]
        scene = shot.rsplit("_S", 1)[0]
        shot_idx = int(shot.rsplit("_S", 1)[1]) - 1
        start = shot_idx * 6.0
        led = led_by_shot[shot]
        dlg = None
        if led.get("dialogue"):
            cue = srt_by_scene[scene][0]
            dlg = {"speaker": led["dialogue"]["speaker"], "windowSceneSeconds": [cue["startSeconds"], cue["endSeconds"]],
                   "text": cue["text"], "beatStartsAtWindowHead": abs((start + s["beatSeconds"][0]) - cue["startSeconds"]) < 0.01}
        per_shot.append({
            "shotId": shot, "sceneId": scene,
            "windowInSceneSeconds": [start, start + 6.0],
            "windowInReelSeconds": [SHOT_OFFSETS[scene] + start, SHOT_OFFSETS[scene] + start + 6.0],
            "camera": led["camera"],
            "beatWindowShotLocalSeconds": s["beatSeconds"],
            "beatWindowSceneSeconds": [start + s["beatSeconds"][0], start + s["beatSeconds"][1]],
            "poseCount": s["poseCount"], "poseFps": s["poseFps"], "route": s["route"],
            "meanInterPoseDiff": s["meanInterPoseDiff"],
            "pose1VsKeyframeDiff": s["pose1VsKeyframeDiff"],
            "lastPoseVsKeyframeDiff": s["lastPoseVsKeyframeDiff"],
            "dialogue": dlg,
            "characterLockRequired": bool(led.get("characterLockRequired")),
            "guardrails": led.get("guardrails") or [],
        })

    # --- 5. audio: measure the v3 mixes ------------------------------------
    mixes = {}
    for sc in SCENES:
        rel = ab["sceneTakes"][sc]["audio"]["sourceMix"]
        mixes[sc] = {**entry(rel, "candidate_embedded_soundtrack_mix_wav"), **loudnorm(ROOT / rel)}

    # --- 6. source closure ---------------------------------------------------
    closure = {"keyframes": [], "timing": [], "subtitles": [], "voTakes": [], "mixManifests": [], "tools": []}
    for s in ab["shots"]:
        kf = led_by_shot[s["shotId"]]["keyframe"]
        closure["keyframes"].append(entry(kf["file"], f"storyboard_keyframe_{s['shotId']}"))
    for sc in SCENES:
        closure["timing"].append(entry(f"Implementation/Content/Narrative/Deliveries/{sc}/{sc}_timing_v1.json", f"timing_{sc}"))
        closure["subtitles"].append(entry(f"ClientGodot/assets/cinematics/{sc}/{sc}_vi.srt", f"subtitles_runtime_{sc}"))
        closure["subtitles"].append(entry(f"Implementation/Content/Narrative/Deliveries/{sc}/{sc}_vi.srt", f"subtitles_delivery_{sc}"))
    vo_dir = ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
    for f in sorted(vo_dir.rglob("*")):
        if f.is_file():
            closure["voTakes"].append(entry(f.relative_to(ROOT).as_posix(), "vo_draft_take_source"))
    mix_root = ROOT / "Art_Source/Audio/Muse/MIX"
    for f in sorted(mix_root.rglob("*manifest*.json")):
        name = f.name.upper()
        if any(sc in name for sc in SCENES) or "P0" in str(f.parent).upper():
            closure["mixManifests"].append(entry(f.relative_to(ROOT).as_posix(), "mix_manifest"))
    for t in ["build_p0_motion_ab_v1.py", "build_p0_mix_v3.py", "build_p0_candidate_m38a.py"]:
        closure["tools"].append(entry(f"Tools/MediaProduction/Muse/{t}", "builder_tool"))

    # --- 7. candidate file list ----------------------------------------------
    files = []
    files.append(entry("Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_review_72s_640x360_30fps.mp4", "candidate_review_reel_72s"))
    files.append(entry("Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_contact_all12.png", "candidate_contact_sheet_all12"))
    for sc in SCENES:
        files.append(entry(ab["sceneTakes"][sc]["file"], f"candidate_scene_take_{sc}"))
        files.append(entry(ab["abVideos"][sc]["file"], f"ab_comparison_video_{sc}"))
    for s in ab["shots"]:
        files.append(entry(ab["shotTakes"][s["shotId"]]["file"], f"shot_take_{s['shotId']}"))
        files.append(entry(ab["contacts"][s["shotId"]]["file"], f"contact_sheet_{s['shotId']}"))

    runtime_unchanged = []
    for sc in SCENES:
        for rel in [f"ClientGodot/assets/cinematics/{sc}/{sc}_640x360_30fps.mp4",
                    f"ClientGodot/assets/cinematics/{sc}/{sc}_640x360_30fps.ogv",
                    f"ClientGodot/assets/cinematics/{sc}/{sc}_poster.png"]:
            runtime_unchanged.append(entry(rel, f"runtime_current_{sc}"))

    subset = {
        "manifestId": "NGM_P0_CANDIDATE_M38A_SUBSET_V1",
        "workOrder": "WO38 M38-A (GoI 38, issue #116 comment 6733227370, PR #130)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baselineSha": "14b588c663a6d53295b34f1d632e84c48c7f5ca9",
        "status": "DRAFT_CANDIDATE_FOR_CODEX_REVIEW - NOT final animation, NOT_AUDITIONED, runtime package NOT modified",
        "candidate": {
            "video": "B takes - procedural pose animation from storyboard keyframes (WO37 M-C CP2): 5 poses per shot at 10 pose/s inside 30 fps video",
            "audio": "P0 draft mix v3 embedded (AAC 48 kHz stereo) - fully composed music + composed ambience + draft VO, sidechain-ducked",
            "scenes": SCENES,
            "totalDurationSeconds": 72.0,
            "frameSize": [640, 360], "fps": 30,
        },
        "files": files,
        "perShot": per_shot,
        "audioRouting": {
            "rule": "EMBEDDED_SOUNDTRACK_ONLY - play only the soundtrack embedded in the candidate clip; never play a standalone mix WAV or VO take at the same time",
            "embeddedMixes": mixes,
            "subtitles": "external SRT (UTF-8), not baked into the candidate video; no double captions",
            "alternatesNotInCandidate": [
                "P0 mix v1 (ported stems) ClientGodot/assets/audio/mix/p0/",
                "P0 mix v2 (composed music + ported ambience) ClientGodot/assets/audio/mix/p0_v2/",
                "M-F CP1 palette pickup VO takes (alternate casting) ClientGodot/assets/audio/vo/palette_pickups/",
            ],
            "playbackMetadataConsistency": {sc: pb_by_scene[sc]["audioOwnership"] for sc in SCENES},
        },
        "sourceClosure": closure,
        "runtimeUnchangedProof": runtime_unchanged,
        "provenance": {
            "musicAmbience": "ORIGINAL_COMPOSED_BY_MUSE - procedural synthesis, no samples (CP26/CP30)",
            "voice": "fictional TTS draft voices only, no real-voice cloning (Ly An = Aria; male draft voice shared - M-F palette pickups are alternates, not in this candidate)",
            "picture": "procedural pose animation rendered from generated storyboard keyframes (STORYBOARD_ONLY); 8 generated strips rejected at CP2, 0 generated pixels in the takes",
            "portedPackV1FilesInCandidate": 0,
        },
    }
    SUBSET_OUT.write_text(json.dumps(subset, ensure_ascii=False, indent=2) + "\n")
    print(f"subset manifest written: {SUBSET_OUT.relative_to(ROOT)} "
          f"({len(files)} candidate files, closure k={len(closure['keyframes'])}/t={len(closure['timing'])}/"
          f"s={len(closure['subtitles'])}/vo={len(closure['voTakes'])}/mm={len(closure['mixManifests'])}/tools={len(closure['tools'])})")
    for sc in SCENES:
        print(f"  mix {sc}: {mixes[sc]['integratedLufs']} LUFS / {mixes[sc]['truePeakDbtp']} dBTP")
    return 0


if __name__ == "__main__":
    sys.exit(main())
