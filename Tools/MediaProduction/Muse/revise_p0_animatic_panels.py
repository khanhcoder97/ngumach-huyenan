#!/usr/bin/env python3
"""MEDIA-02 checkpoint 13: revise the 4 defective P0 animatic panels (D4).

Reads the v1 storyboard sheet + spec, pastes 4 corrected 16:9 panels
(generated + visually verified this checkpoint) into the exact crop regions
that build_p0_animatic.py extracts (same inset + center-crop 16:9 math, so
the rebuilt panel equals the corrected image), and writes:
  - Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v2.png
  - Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v2.json
The other 8 panels are untouched (sheet re-save is lossless PNG, so their
rebuilt SHAs stay identical to v1). The 13th study panel is untouched.

Usage:
  python3 revise_p0_animatic_panels.py --panel-dir /tmp/panel_v2 \\
      --root . [--spec-v1 Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json]
Panel files in --panel-dir must be named panel_<SHOTID>_v2.png.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

FIXES = {
    "CIN_001_S03": ("Bell drawn solid under the pier in v1; v2 removes the solid "
                    "bell entirely — only its reflection ripples on the water, "
                    "one ripple interrupting the reflected shape (per pack)."),
    "CIN_001_S06": ("Figure read as the warden (topknot, dark robe) in v1; v2 draws "
                    "Ly An per the questkit reference (brown low ponytail, teal-blue "
                    "rain cloak with gold trim, cream tunic, brown messenger satchel)."),
    "CIN_004_S01": ("Broken-horn detail unreadable in v1; v2 shows exactly one "
                    "broken horn — one horn snapped to a short jagged stump, the "
                    "other whole and curved (canon: 1 broken horn)."),
    "CIN_004_S03": ("Framing angled in v1; v2 is a strict top-down orthographic "
                    "arena frame — serpent withdrawing into the northern pool, "
                    "southern arrival area clear, wooden landing at the south edge."),
}


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
    ap.add_argument("--panel-dir", required=True)
    ap.add_argument("--root", default=".")
    ap.add_argument("--spec-v1",
                    default="Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json")
    args = ap.parse_args()
    root = Path(args.root)
    panel_dir = Path(args.panel_dir)
    spec = json.loads((root / args.spec_v1).read_text(encoding="utf-8"))
    sheet = Image.open(root / spec["storyboardSheet"]).convert("RGB")
    assert sheet.size == (1920, 1280), sheet.size

    fixed = []
    for shot in spec["shots"]:
        sid = shot["shotId"]
        if sid not in FIXES:
            continue
        src = Image.open(panel_dir / f"panel_{sid}_v2.png").convert("RGB")
        box = shot["sheetBox"]
        # Fill the whole box with the corrected panel (covers slivers the
        # tool's center-crop discards), then paste the exact crop region.
        sheet.paste(src.resize((box[2] - box[0], box[3] - box[1]), Image.LANCZOS),
                    (box[0], box[1]))
        (rx0, ry0, rx1, ry1), (rw, rh) = crop_region(box)
        sheet.paste(src.resize((rw, rh), Image.LANCZOS), (rx0, ry0))
        fixed.append(sid)
        print(f"{sid}: box {box} crop-region {(rx0, ry0, rx1, ry1)} {rw}x{rh}")
    assert fixed == sorted(FIXES), fixed

    sheet_v2 = root / "Art_Source/Cinematics/P0_Animatic/P0_storyboard_sheet_v2.png"
    sheet.save(sheet_v2)
    sheet_sha = sha256(sheet_v2)
    print(f"sheet v2: {sheet_v2} sha256={sheet_sha}")
    old_sheet_sha = spec["storyboardSheetSha256"]

    # --- spec v2 ---
    spec["checkpoint"] = ("MEDIA-02 checkpoint 13 - P0 animatic revision v2 "
                          "(D4 panel fixes)")
    spec["baseSha"] = "f38323386b079f861c6472d2bd139e1ed9762c3c"
    spec["branchBaseNote"] = ("Media branch merge-base remains cf17178 (no rebase); "
                              "baseSha here is the integration HEAD this revision "
                              "was validated against (PR #119 base).")
    spec["storyboardSheet"] = ("Art_Source/Cinematics/P0_Animatic/"
                               "P0_storyboard_sheet_v2.png")
    spec["storyboardSheetSha256"] = sheet_sha
    spec["outputsManifest"] = ("Art_Source/Cinematics/P0_Animatic/"
                               "P0_animatic_outputs_v2.json")
    spec["storyboardSheetNote"] = (
        "Sheet v2 (1920x1280): v1 pixels except the 4 revised panels "
        "(CIN_001_S03, CIN_001_S06, CIN_004_S01, CIN_004_S03), pasted into "
        "the exact crop regions build_p0_animatic.py extracts. The other 8 "
        "timeline panels and the 13th study panel (row 4, column 2, coiled "
        "serpent, box [506, 959, 947, 1251]) are byte-identical to v1.")
    spec["revision"] = {
        "fromSheetSha256": old_sheet_sha,
        "fromSpec": "P0_animatic_spec_v1.json",
        "fixedShots": sorted(FIXES),
        "method": ("Corrected panels generated as 16:9 edits of the v1 panels, "
                   "viewed directly, then pasted into the sheet at the exact "
                   "crop regions; rebuilt with build_p0_animatic.py --spec v2."),
        "reference": ("Ly An per ben_mua_questkit_v1.png (integration f383233, "
                      "content sha256 cff1157896050a93947d3573424f1af1547265604e3d0e97599c053b91ba5f32, "
                      "read-only; NOT copied into the media branch)."),
    }
    spec["sources"]["characterReference"]["branch"] = (
        "codex/story-gameplay-integration-20261031 (PR #118 merged, HEAD "
        "f383233; READ-ONLY reference; NOT merged into the media branch, "
        "NOT edited)")
    spec["sources"]["characterReference"]["fetchedHead"] = (
        "a75b53840c0b2fb4bbfa5a84c5bfa80914bffe9b (questkit source commit; "
        "file now in integration f383233 with identical content sha256)")
    spec["statusNote"] = (spec["statusNote"] +
                          " Revision v2 (checkpoint 13) fixes the 4 recorded "
                          "panel defects (D4); timing, SRT, stems and VO are "
                          "unchanged. Still a storyboard animatic, not final "
                          "picture; final takes still go to Codex review.")
    for shot in spec["shots"]:
        sid = shot["shotId"]
        if sid in FIXES:
            shot.pop("panelDefect", None)
            shot["panelFix"] = FIXES[sid]
            shot["panelFixVerified"] = "viewed directly 2026-11-05 (checkpoint 13)"
    spec_v2 = root / "Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v2.json"
    spec_v2.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8")
    print(f"spec v2: {spec_v2}")


if __name__ == "__main__":
    main()
