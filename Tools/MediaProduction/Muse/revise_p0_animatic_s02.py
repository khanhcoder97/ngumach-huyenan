#!/usr/bin/env python3
"""MEDIA-02 checkpoint 16 (Gói 30 fix (c)): revise the CIN_002_S02 panel.

Reads the v2 storyboard sheet + spec, pastes the corrected 16:9 keyframe
(built by build_p0_keyframes.py) into the exact crop region that
build_p0_animatic.py extracts (same inset + center-crop 16:9 math, so the
rebuilt panel is the corrected image resampled through the sheet), and writes:
  - Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v3.png
  - Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v3.json
The other 11 panels are untouched (sheet re-save is lossless PNG, so their
rebuilt SHAs stay identical to v2). The 13th study panel is untouched.

Usage:
  python3 revise_p0_animatic_s02.py --keyframe-dir \\
      Art_Source/Cinematics/P0_Animatic/keyframes_16x9 --root . \\
      [--spec-v2 Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v2.json]
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

FIX_SHOT = "CIN_002_S02"
FIX_NOTE = ("v1/v2 panel showed the BANDAGED hand touching the water and the "
            "head crown clipped by the center-crop. v3 keyframe (checkpoint "
            "16, independently generated 16:9): the BARE good hand is lowered "
            "toward the water and STOPS above it (visible gap, no touch, no "
            "contact ripples); the BANDAGED forearm rests back on the pier; "
            "the whole head and face are in frame with headroom; broken "
            "sword hilt on his back. Per review finding 3 + owner issue "
            "#116 comment 6657227288.")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def crop_region(box):
    """Replicate build_p0_animatic.py: inset 3 px, center-crop 16:9.
    Returns absolute (x0, y0, x1, y1) of the region the tool extracts."""
    x0, y0, x1, y1 = box[0] + 3, box[1] + 3, box[2] - 3, box[3] - 3
    w, h = x1 - x0, y1 - y0
    if w / h > 16 / 9:
        nw = int(h * 16 / 9)
        ox = (w - nw) // 2
        return (x0 + ox, y0, x0 + ox + nw, y1), (nw, h)
    nh = int(w * 9 / 16)
    oy = (h - nh) // 2
    return (x0, y0 + oy, x1, y0 + oy + nh), (w, nh)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--keyframe-dir", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--spec-v2",
                    default="Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v2.json")
    args = ap.parse_args()
    root = Path(args.root)
    keyframe_dir = Path(args.keyframe_dir)
    spec = json.loads((root / args.spec_v2).read_text(encoding="utf-8"))
    sheet = Image.open(root / spec["storyboardSheet"]).convert("RGB")
    assert sheet.size == (1920, 1280), sheet.size

    shot = next(s for s in spec["shots"] if s["shotId"] == FIX_SHOT)
    src = Image.open(keyframe_dir / f"keyframe_{FIX_SHOT}.png").convert("RGB")
    assert src.size == (640, 360), src.size
    box = shot["sheetBox"]
    # Fill the whole box with the corrected keyframe (covers slivers the
    # tool's center-crop discards), then paste the exact crop region.
    sheet.paste(src.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS),
                (box[0], box[1]))
    (rx0, ry0, rx1, ry1), (rw, rh) = crop_region(box)
    sheet.paste(src.resize((rw, rh), Image.LANCZOS), (rx0, ry0))
    print(f"{FIX_SHOT}: box {box} crop-region {(rx0, ry0, rx1, ry1)} {rw}x{rh}")

    sheet_v3 = root / "Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v3.png"
    sheet.save(sheet_v3)
    sheet_sha = sha256(sheet_v3)
    print(f"sheet v3: {sheet_v3} sha256={sheet_sha}")
    old_sheet_sha = spec["storyboardSheetSha256"]

    # --- spec v3 ---
    spec["checkpoint"] = ("MEDIA-02 checkpoint 16 - P0 animatic revision v3 "
                          "(Gói 30 fix (c): CIN_002_S02 corrected keyframe + "
                          "separate 16:9 keyframes)")
    spec["baseSha"] = "f0859d05c2102f0ddd03c16adeb29ce785396e73"
    spec["branchBaseNote"] = ("Media branch merge-base remains cf17178 (no rebase); "
                              "baseSha here is the integration HEAD this revision "
                              "was validated against (PR #121 merged, f0859d0).")
    spec["storyboardSheet"] = ("Art_Source/Cinematics/P0_Animatic/"
                               "P0_storyboard_sheet_v3.png")
    spec["storyboardSheetSha256"] = sheet_sha
    spec["outputsManifest"] = ("Art_Source/Cinematics/P0_Animatic/"
                               "P0_animatic_outputs_v3.json")
    spec["keyframesDir"] = "Art_Source/Cinematics/P0_Animatic/keyframes_16x9"
    spec["keyframesManifest"] = ("Art_Source/Cinematics/P0_Animatic/"
                                 "P0_keyframes_16x9_manifest_v1.json")
    spec["storyboardSheetNote"] = (
        "Sheet v3 (1920x1280): v2 pixels except the CIN_002_S02 panel, "
        "replaced by the corrected checkpoint-16 keyframe pasted into the "
        "exact crop region build_p0_animatic.py extracts. The other 11 "
        "timeline panels and the 13th study panel (row 4, column 2, coiled "
        "serpent, box [506, 959, 947, 1251]) are byte-identical to v2.")
    spec["revision"] = {
        "fromSheetSha256": old_sheet_sha,
        "fromSpec": "P0_animatic_spec_v2.json",
        "fixedShots": [FIX_SHOT],
        "method": ("Corrected keyframe generated as an independent 16:9 image, "
                   "viewed directly (full frame + hand zoom), then pasted into "
                   "the sheet at the exact crop region; rebuilt with "
                   "build_p0_animatic.py --spec v3. Separate 16:9 keyframes "
                   "for all 12 shots built by build_p0_keyframes.py."),
        "reference": ("Ta Van Khanh per ben_mua_questkit_v1.png (integration "
                      "f0859d0, content sha256 "
                      "cff1157896050a93947d3573424f1af1547265604e3d0e97599c053b91ba5f32, "
                      "read-only; NOT copied into the media branch). "
                      "Bandaged arm is his RIGHT forearm; the good hand is "
                      "the bare LEFT hand."),
    }
    spec["statusNote"] = (spec["statusNote"] +
                          " Revision v3 (checkpoint 16) fixes the 5th panel "
                          "defect (CIN_002_S02, review finding 3) and adds "
                          "separate 16:9 keyframes per shot. Timing, SRT, "
                          "stems and VO are unchanged. Still a storyboard "
                          "animatic, not final picture; final takes still go "
                          "to Codex review.")
    shot.pop("panelDefect", None)
    shot["panelFix"] = FIX_NOTE
    shot["panelFixVerified"] = "viewed directly 2026-11-05 (checkpoint 16: full frame + hand zoom)"
    spec_v3 = root / "Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v3.json"
    spec_v3.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print(f"spec v3: {spec_v3}")


if __name__ == "__main__":
    main()
