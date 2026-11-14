#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 9 — independent validator for the
ear-audition pack. Re-checks from the real bytes: every item file exists
and its sha256 matches the pack; every playlist line resolves to an
existing file and covers exactly its section's files; header counts
match; every P0 priority item carries a flag and a listening question.
Writes MEDIA02_WO37_MD_CP9_VALIDATION_20261109.json next to the pack.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
PACK = REPORTS / "EAR_AUDITION_PACK_v1.json"
OUT = REPORTS / "MEDIA02_WO37_MD_CP9_VALIDATION_20261109.json"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def playlist_files(name):
    files = []
    for line in (REPORTS / name).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # entries are ../../../<repo-relative path> from the reports folder
        rel = line[len("../../../"):] if line.startswith("../../../") else line
        files.append(rel)
    return files


def main():
    pack = json.loads(PACK.read_text(encoding="utf-8"))
    mismatches = []
    checked_files = 0
    by_id = {}
    for sec, items in pack["sections"].items():
        if pack["counts"].get(sec) != len(items):
            mismatches.append(f"count mismatch in {sec}: header {pack['counts'].get(sec)} vs {len(items)}")
        for it in items:
            by_id[it["id"]] = it
            p = ROOT / it["file"]
            if not p.exists():
                mismatches.append(f"{it['id']}: missing file {it['file']}")
                continue
            checked_files += 1
            if sha256_of(p) != it["sha256"]:
                mismatches.append(f"{it['id']}: sha256 mismatch {it['file']}")
            if not it.get("question"):
                mismatches.append(f"{it['id']}: empty listening question")
            if it["priority"] == "P0" and not it.get("flags"):
                mismatches.append(f"{it['id']}: P0 without flag")
    if pack["totalItems"] != sum(pack["counts"].values()):
        mismatches.append("totalItems mismatch")
    for q in pack["priorityQueue"]:
        if q["id"] not in by_id:
            mismatches.append(f"priorityQueue references unknown id {q['id']}")

    expect = {
        "ear_audition_01_score_playlist.txt":
            [it["file"] for s in ("scoreMasters", "stingers", "transitions") for it in pack["sections"][s]],
        "ear_audition_02_intro_outro_playlist.txt":
            [it["file"] for it in pack["sections"]["introOutro"]],
        "ear_audition_04_stems_playlist.txt":
            [it["file"] for it in pack["sections"]["stems"]],
        "ear_audition_05_ambience_playlist.txt":
            [it["file"] for it in pack["sections"]["ambience"]],
        "ear_audition_06_mixes_playlist.txt":
            [it["file"] for it in pack["sections"]["mixes"]],
        "ear_audition_07_vo_playlist.txt":
            [it["file"] for it in pack["sections"]["vo"]],
    }
    for name, want in expect.items():
        got = playlist_files(name)
        if got != want:
            mismatches.append(f"playlist {name}: {len(got)} entries vs expected {len(want)} (order/set differs)")
        for rel in got:
            if not (ROOT / rel).exists():
                mismatches.append(f"playlist {name}: unresolved {rel}")
    lay = playlist_files("ear_audition_03_layers_playlist.txt")
    layer_files = [it["file"] for it in pack["sections"]["layers"]]
    for f in layer_files:
        if f not in lay:
            mismatches.append(f"layers playlist missing {f}")
    for rel in lay:
        if not (ROOT / rel).exists():
            mismatches.append(f"layers playlist: unresolved {rel}")

    result = {
        "validator": "check_ear_audition_pack_cp9_v1",
        "pack": "EAR_AUDITION_PACK_v1.json",
        "status": "PASS" if not mismatches else "FAIL",
        "mismatches": mismatches,
        "itemsChecked": len(by_id),
        "filesHashed": checked_files,
        "counts": pack["counts"],
        "priorityItems": len(pack["priorityQueue"]),
        "auditionStatus": pack["status"],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    return 0 if not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
