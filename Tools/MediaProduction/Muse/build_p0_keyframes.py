#!/usr/bin/env python3
"""MEDIA-02 checkpoint 16 (Gói 30 fix (c)): build the separate 16:9
keyframe set for the 12 P0 shots.

Reads the shot order from P0_animatic_spec_v2.json and writes:
  - Art_Source/Cinematics/P0_Animatic/keyframes_16x9/keyframe_<SHOT>.png
    (12 files, each exactly 640x360, 16:9)
  - Art_Source/Cinematics/P0_Animatic/P0_keyframes_16x9_manifest_v1.json

Provenance is recorded per shot, honestly:
  - CIN_002_S02: independently generated 16:9 keyframe (checkpoint 16),
    corrected per review finding 3 + owner comment 6657227288 (good hand
    stops before the water; bandaged arm back on the pier; full head/face
    in frame). Source is the generated file passed with --generated.
  - The 4 checkpoint-13 shots: independently generated 16:9 panels, pasted
    into sheet v2; the keyframe is that panel at 640x360.
  - The other 7 shots: the v1 sheet-crop panels (center-crop 16:9 from the
    storyboard sheet), framing re-verified on the checkpoint-16 contact
    sheet (subject/head in frame). They are carried forward as the separate
    16:9 keyframe for that shot at STORYBOARD level; they are NOT claimed
    to be independently generated final frames. Final-picture frames for
    those shots remain future work (campaign animated takes).

The animatic panel for a shot is derived from the storyboard sheet by
build_p0_animatic.py (sheet box -> center-crop -> 640x360 resample), so a
rebuilt panel SHA may differ from the keyframe SHA by resampling; the
keyframe manifest records keyframe SHAs only, and the outputs manifest
records panel SHAs. Both are checked by validate_media_deliveries.py.

Usage:
  python3 build_p0_keyframes.py --generated /tmp/.../panel_CIN_002_S02_v3.png \\
      --root . [--framing-verified "..."]
"""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

from PIL import Image

W, H = 640, 360

# Per-shot framing notes (from the spec content + the checkpoint-16
# contact-sheet viewing). Sources are set in code, not guessed.
FRAMING = {
    "CIN_001_S01": "Wide rainy pier with lanterns and baskets; no person; full pier and water in frame.",
    "CIN_001_S02": "Sealed parcel on the pier edge over water; parcel whole, rope and post in frame.",
    "CIN_001_S03": "Bell reflection only on the water under the pier (checkpoint 13 fix); no solid bell; ripple interrupts the reflection.",
    "CIN_001_S04": "Sealed letter close-up on the pier boards; whole letter and wax seal in frame.",
    "CIN_001_S05": "Ly An crouching with the parcel at the pier edge; full figure in frame (DECIDED dialogue window 24.8-28.5 s).",
    "CIN_001_S06": "Ly An standing on the pier (checkpoint 13 fix, per questkit); full figure in frame.",
    "CIN_002_S01": "Ripples drifting toward the submerged stone channel; no person; full channel in frame.",
    "CIN_002_S02": "Ta Van Khanh leaning on the pier: BARE good hand lowered toward the water and STOPPING above it (visible gap, no touch, no contact ripples); BANDAGED forearm resting back on the pier; whole head and face in frame with headroom; broken sword hilt on his back.",
    "CIN_002_S03": "Strict top-down reed bank and stone channel; hairline crack readable; no person.",
    "CIN_004_S01": "Boss Mang Cot head rising: exactly ONE broken horn (short jagged stump) and one whole curved horn (checkpoint 13 fix, canon: 1 broken horn).",
    "CIN_004_S02": "Serpent coiling in the whirlpool; whole head and body arc in frame.",
    "CIN_004_S03": "Strict top-down arena (checkpoint 13 fix); serpent withdrawing north, southern arrival clear, wooden landing at the south edge.",
}

CP13_SHOTS = {"CIN_001_S03", "CIN_001_S06", "CIN_004_S01", "CIN_004_S03"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generated", required=True,
                    help="Generated corrected CIN_002_S02 keyframe (16:9 image).")
    ap.add_argument("--root", default=".")
    ap.add_argument("--framing-verified", default="",
                    help="Human verification note for the framing check.")
    args = ap.parse_args()
    root = Path(args.root)
    anim = root / "Art_Source/Cinematics/P0_Animatic"
    spec = json.loads((anim / "P0_animatic_spec_v2.json").read_text(encoding="utf-8"))
    generated = Path(args.generated)
    gen_sha = sha256(generated)

    out_dir = anim / "keyframes_16x9"
    out_dir.mkdir(parents=True, exist_ok=True)

    shots = []
    for shot in spec["shots"]:
        sid = shot["shotId"]
        out = out_dir / f"keyframe_{sid}.png"
        if sid == "CIN_002_S02":
            im = Image.open(generated).convert("RGB").resize((W, H), Image.LANCZOS)
            im.save(out)
            source = "generated-16x9-checkpoint-16"
            source_detail = ("Independently generated 16:9 keyframe (checkpoint 16), "
                             "corrected per review finding 3 + owner comment "
                             "6657227288; generated source sha256 " + gen_sha + ".")
        else:
            panel = anim / "panels" / f"panel_{sid}.png"
            assert panel.exists(), f"missing panel {panel}"
            im = Image.open(panel).convert("RGB")
            assert im.size == (W, H), (sid, im.size)
            shutil.copyfile(panel, out)
            if sid in CP13_SHOTS:
                source = "panel-16x9-checkpoint-13"
                source_detail = ("Independently generated 16:9 panel (checkpoint 13, "
                                 "D4 fix), pasted into storyboard sheet v2.")
            else:
                source = "panel-sheet-crop-v1"
                source_detail = ("v1 sheet-crop panel (center-crop 16:9 from storyboard "
                                 "sheet v1); framing re-verified on the checkpoint-16 "
                                 "contact sheet. STORYBOARD level only — NOT an "
                                 "independently generated final frame.")
        shots.append({
            "shotId": sid,
            "sceneId": shot["sceneId"],
            "file": f"Art_Source/Cinematics/P0_Animatic/keyframes_16x9/keyframe_{sid}.png",
            "sha256": sha256(out),
            "size": f"{W}x{H}",
            "aspectRatio": "16:9",
            "source": source,
            "sourceDetail": source_detail,
            "framingNote": FRAMING[sid],
            "finalPictureStatus": "STORYBOARD_ONLY",
        })
        print(f"{sid}: {source} sha256={shots[-1]['sha256'][:12]}...")

    manifest = {
        "manifestId": "NGM_P0_KEYFRAMES_16X9_V1",
        "checkpoint": ("MEDIA-02 checkpoint 16 (Gói 30 fix (c): CIN_002_S02 corrected "
                       "keyframe + separate 16:9 keyframes per shot)"),
        "decisionRefs": [
            "DEC-MEDIA-P0-20261105 (CIN_001_S05 version B, 24.8-28.5 s; CIN_004 Ly An off-screen)",
            "Review Muse_PR119.md finding 3 (CIN_002_S02: good hand stops before water; no center-crop clipping)",
            "Owner issue #116 comment 6657227288 (fix the 5th panel; keep full head/face in the 16:9 frame)",
            "Review Muse_PR119_67f_followup.md (4 CP13 panels accepted at storyboard level; S02 unchanged until this checkpoint)",
        ],
        "baseIntegration": "f0859d0",
        "branch": "muse/media-production-20261104",
        "generatedSourceSha256": gen_sha,
        "framingVerified": args.framing_verified or "NOT_YET_VIEWED",
        "notes": [
            "12 separate 16:9 keyframes, one per P0 shot, 640x360 each.",
            "Only CIN_002_S02 is a newly generated picture in this checkpoint; the other 11 keyframes are the v2 panels (4 independently generated in checkpoint 13, 7 v1 sheet crops re-verified for framing).",
            "The animatic panel for a shot is derived from the storyboard sheet (sheet box -> center-crop -> 640x360), so a rebuilt panel SHA may differ from the keyframe SHA by resampling; panel SHAs live in P0_animatic_outputs_v3.json.",
            "Still STORYBOARD_ONLY: final animated takes and final-picture approval remain with Codex review.",
        ],
        "shots": shots,
    }
    mpath = anim / "P0_keyframes_16x9_manifest_v1.json"
    mpath.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8")
    print(f"OK: {len(shots)} keyframes -> {out_dir}")
    print(f"manifest: {mpath}")


if __name__ == "__main__":
    main()
