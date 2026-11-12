#!/usr/bin/env python3
"""Checker for the SCENE-CLIPS export-manifest reconciliation (2026-11-13).

The 8 pre-existing validate_media_deliveries mismatches (CIN_005/009/017/020:
"timing sha mismatch" + "runtime manifest files != export manifest files")
came from WO37 M-C CP5's timing edits: M-G CP7 (9cd5808) synced the three
timing FILE mirrors but the four scene_export_manifest_v1.json records were
never updated — they still carried the pre-CP5 timing sha256/sizeBytes while
the runtime manifest (regenerated) already matched the real files.

This checker asserts, from real bytes:
1. For all 20 campaign scenes, the export manifest's files dict equals the
   runtime cinematics manifest's sceneClips files dict.
2. For all 20 scenes, the recorded timing sha256/sizeBytes equal the real
   runtime timing file AND the Narrative/Deliveries source timing file.
3. For the 4 reconciled scenes, the manifest differs from the base commit
   (be9ccb8) ONLY in files.timing.sha256 / files.timing.sizeBytes.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = "be9ccb8af8fea2ae5632952cc2b94ad4148d40fa"
FIXED = ("CIN_005", "CIN_009", "CIN_017", "CIN_020")
SCENES = ("CIN_001", "CIN_002", "CIN_003", "CIN_004", "CIN_005", "CIN_006",
          "CIN_007", "CIN_008", "CIN_009", "CIN_010", "CIN_011", "CIN_012",
          "CIN_013", "CIN_014", "CIN_015", "CIN_016", "CIN_017", "CIN_018",
          "CIN_019", "CIN_020")

checks = 0
fails = []


def check(ok, label):
    global checks
    checks += 1
    if not ok:
        fails.append(label)


def sha256_of(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    cine = ROOT / "ClientGodot/assets/cinematics"
    runtime = json.loads(
        (cine / "RUNTIME_CINEMATICS_manifest_v1.json").read_text("utf-8"))
    rc = {c["sceneId"]: c for c in runtime["sceneClips"]}
    for s in SCENES:
        exp = json.loads(
            (cine / s / "scene_export_manifest_v1.json").read_text("utf-8"))
        check(exp["files"] == rc[s]["files"], f"{s}: export files == runtime files")
        t = exp["files"]["timing"]
        real = ROOT / "ClientGodot" / t["path"]
        src = (ROOT / "Implementation/Content/Narrative/Deliveries" / s
               / f"{s}_timing_v1.json")
        check(sha256_of(real) == t["sha256"], f"{s}: timing sha == real file")
        check(real.stat().st_size == t["sizeBytes"], f"{s}: timing size == real file")
        check(sha256_of(src) == t["sha256"], f"{s}: timing sha == Deliveries source")
    for s in FIXED:
        rel = f"ClientGodot/assets/cinematics/{s}/scene_export_manifest_v1.json"
        old = json.loads(subprocess.run(
            ["git", "show", f"{BASE}:{rel}"], cwd=ROOT,
            capture_output=True, check=True).stdout)
        new = json.loads((ROOT / rel).read_text("utf-8"))
        old_t = old["files"].pop("timing")
        new_t = new["files"].pop("timing")
        check(old == new, f"{s}: nothing outside files.timing changed")
        check(old_t["path"] == new_t["path"], f"{s}: timing path unchanged")
        check(old_t["sha256"] != new_t["sha256"], f"{s}: timing sha actually updated")
    print(f"checks: {checks}, fails: {len(fails)}")
    for f in fails:
        print("FAIL:", f)
    print("verdict:", "PASS" if not fails else "FAIL")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
