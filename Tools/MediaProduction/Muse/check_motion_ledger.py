#!/usr/bin/env python3
"""Validate MOTION_LEDGER_v1.json against the real sources.

Re-reads every timing manifest, keyframe manifest and scene export
manifest, re-hashes all 63 keyframe PNGs from disk, re-derives the
per-shot motion class / priority / lock requirement with the builder's
rules, and deep-compares the result with the ledger JSON. Any drift --
a stale ledger, a changed keyframe, a new defect, a re-worded framing
-- is a mismatch and fails the run. Exit 0 only on PASS.

Writes Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_MOTION_LEDGER_VALIDATION_20261108.json.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(".")
LEDGER = (ROOT / "Implementation/Content/Narrative/Deliveries"
          / "MOTION_LEDGER_v1.json")
OUT = (ROOT / "Implementation/Reports/MuseMedia"
       / "MEDIA02_WO37_MC_MOTION_LEDGER_VALIDATION_20261108.json")

spec = importlib.util.spec_from_file_location(
    "motion_ledger",
    ROOT / "Tools/MediaProduction/Muse/build_motion_ledger_v1.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MISMATCHES = []


def err(msg: str) -> None:
    MISMATCHES.append(msg)
    print("MISMATCH:", msg, file=sys.stderr)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    ledger = load_json(LEDGER)
    rows = {r["shotId"]: r for r in ledger["shots"]}
    if len(rows) != 63:
        err(f"ledger has {len(rows)} shots, expected 63")

    # Re-read keyframes (same sources as the builder).
    keyframes = {}
    p0 = load_json(ROOT / "Art_Source/Cinematics/P0_Animatic"
                   / "P0_keyframes_16x9_manifest_v1.json")
    for s in p0["shots"]:
        keyframes[s["shotId"]] = {
            "file": s["file"], "sha256": s["sha256"],
            "framing": s.get("framingNote", ""), "defects": [],
            "status": s.get("finalPictureStatus", "STORYBOARD_ONLY")}
    camp_dir = ROOT / "Art_Source/Cinematics/Campaign"
    for mpath in sorted(camp_dir.glob("*/CIN*_keyframes_manifest_v1.json")):
        m = load_json(mpath)
        for k in m["keyframes"]:
            keyframes[k["shotId"]] = {
                "file": "Art_Source/Cinematics/Campaign/%s/%s" % (
                    m["sceneId"], k["file"]),
                "sha256": k["sha256"],
                "framing": k.get("framing", ""),
                "defects": ([k["knownDefects"]] if isinstance(
                    k.get("knownDefects"), str) else
                    list(k.get("knownDefects") or [])),
                "status": m.get("status", "STORYBOARD")}
    if len(keyframes) != 63:
        err(f"keyframes re-read: {len(keyframes)} != 63")

    runtime = load_json(ROOT / "ClientGodot/assets/cinematics"
                        / "RUNTIME_CINEMATICS_manifest_v1.json")
    totals = runtime["campaignTotals"]
    if (totals["scenes"], totals["shots"], totals["seconds"],
            totals["dialogueCues"]) != (20, 63, 378, 21):
        err(f"campaign totals changed: {totals}")

    checked = 0
    dialogue_shots = 0
    for n in range(1, 21):
        scene_id = f"CIN_{n:03d}"
        timing = load_json(ROOT / "Implementation/Content/Narrative"
                           / "Deliveries" / scene_id
                           / f"{scene_id}_timing_v1.json")
        export = load_json(ROOT / "ClientGodot/assets/cinematics"
                           / scene_id / "scene_export_manifest_v1.json")
        motion = export.get("motionModel", {})
        frame_check = export.get("frameCheck", {})
        for shot in timing["shots"]:
            shot_id = shot["shotId"]
            checked += 1
            row = rows.get(shot_id)
            if row is None:
                err(f"{shot_id}: missing from ledger")
                continue
            kf = keyframes[shot_id]
            disk_sha = sha256(ROOT / kf["file"])
            if disk_sha != kf["sha256"]:
                err(f"{shot_id}: keyframe disk SHA {disk_sha[:8]} != "
                    f"manifest {kf['sha256'][:8]}")
            if row["keyframe"]["sha256"] != kf["sha256"]:
                err(f"{shot_id}: ledger keyframe SHA != manifest")
            if row["keyframe"]["file"] != kf["file"]:
                err(f"{shot_id}: ledger keyframe file != manifest")
            if shot_id in mod.CP32_FIXED:
                if not disk_sha.startswith(mod.CP32_FIXED[shot_id][1]):
                    err(f"{shot_id}: CP32 fix lost (current "
                        f"{disk_sha[:8]} != {mod.CP32_FIXED[shot_id][1]})")
            if mod.MASCOT.search(kf["framing"]):
                err(f"{shot_id}: mascot in current framing")
            text = (kf["framing"] + " " + " ".join(kf["defects"])).strip()
            if row["keyframeDefects"] != kf["defects"]:
                err(f"{shot_id}: ledger keyframeDefects != manifest")
            if row["camera"] != shot.get("camera"):
                err(f"{shot_id}: ledger camera != timing")
            if (row["startSeconds"], row["endSeconds"]) != (
                    shot["startSeconds"], shot["endSeconds"]):
                err(f"{shot_id}: ledger shot bounds != timing")
            dlg = shot.get("dialogue")
            if dlg:
                dialogue_shots += 1
            # Re-derive the classification with the builder's rules.
            speaker_raw = dlg.get("speaker") if dlg else None
            speaker = (mod.SPEAKER_ALIASES.get(speaker_raw, speaker_raw)
                       if speaker_raw else None)
            onscreen = dlg.get("onscreen") if dlg else None
            names = mod.find_names(text, scene_id)
            negated = set()
            for char_id, evs in names.items():
                for ev in evs:
                    if mod.NOT_IDENTIFIABLE.search(ev):
                        negated.add(char_id)
            speaker_fail = False
            speaker_in_frame = False
            if dlg and onscreen is True and speaker and speaker != "PLAYER":
                role_words = mod.SPEAKER_ROLE_WORDS.get(speaker, [])
                patterns = dict(mod.LEXICON).get(speaker, [])
                for c in mod.clauses(text):
                    low = c.lower()
                    import re as _re
                    mentions = (any(_re.search(p, c, _re.I) for p in patterns)
                                or any(w in low for w in role_words))
                    if mentions:
                        speaker_in_frame = True
                        if mod.NOT_IDENTIFIABLE.search(c):
                            speaker_fail = True
                if not speaker_in_frame:
                    speaker_fail = True
            visible = sorted(
                {c for c in names if c not in negated} |
                ({speaker} if speaker and speaker != "PLAYER"
                 and onscreen is True and not speaker_fail else set()))
            required = sorted(set(names) |
                              ({speaker} if speaker and speaker != "PLAYER"
                               and onscreen is True else set()))
            lock_required = bool(required)
            is_p0 = scene_id in mod.P0_SCENES
            if is_p0:
                motion_class, priority = "ACTION_ANIMATION", 1
            elif lock_required or speaker_fail:
                motion_class, priority = "KEN_BURNS_HOLD", 3
            else:
                motion_class, priority = "ACTION_ANIMATION", 2
            for field, want in (
                    ("motionClass", motion_class),
                    ("priority", priority),
                    ("characterLockRequired", lock_required),
                    ("speakerIdentifiabilityDefect", bool(speaker_fail)),
                    ("speakerNotInFrame", bool(
                        dlg and onscreen is True and speaker
                        and speaker != "PLAYER" and not speaker_in_frame)),
                    ("namedCharactersVisible", visible),
                    ("namedCharactersRequired", required),
                    ("genericPersonMention", bool(
                        mod.GENERIC_PERSON.search(text)))):
                if row[field] != want:
                    err(f"{shot_id}: ledger {field} {row[field]!r} != "
                        f"re-derived {want!r}")
            fc = frame_check.get(shot_id, {})
            if row["currentMotion"]["shotMove"] != motion.get(
                    "shots", {}).get(shot_id):
                err(f"{shot_id}: ledger shotMove != export manifest")
            if row["currentMotion"]["motionMeanAbsChannelDiff"] != fc.get(
                    "motionMeanAbsChannelDiff"):
                err(f"{shot_id}: ledger motion diff != frameCheck")

    if dialogue_shots != 21:
        err(f"dialogue shots re-derived {dialogue_shots} != 21")
    if checked != 63:
        err(f"shots re-checked {checked} != 63")

    # Ledger-level totals and execution order.
    by_class, by_priority = {}, {}
    for r in ledger["shots"]:
        by_class[r["motionClass"]] = by_class.get(r["motionClass"], 0) + 1
        by_priority[r["priority"]] = by_priority.get(r["priority"], 0) + 1
    if ledger["totals"]["byMotionClass"] != by_class:
        err(f"totals byMotionClass {ledger['totals']['byMotionClass']} "
            f"!= {by_class}")
    if ledger["totals"]["byPriority"] != {str(k): v for k, v in
                                           sorted(by_priority.items())}:
        err("totals byPriority mismatch")
    if ledger["totals"]["characterLockRequired"] != sum(
            1 for r in ledger["shots"] if r["characterLockRequired"]):
        err("totals characterLockRequired mismatch")
    if ledger["totals"]["speakerIdentifiabilityDefects"] != sum(
            1 for r in ledger["shots"] if r["speakerIdentifiabilityDefect"]):
        err("totals speakerIdentifiabilityDefects mismatch")
    order = [r["shotId"] for r in sorted(
        ledger["shots"],
        key=lambda r: (r["priority"], r["sceneId"], r["shotId"]))]
    if ledger["executionOrder"] != order:
        err("executionOrder != priority/scene/shot sort")
    p0_order = [s for s in order if s.split("_")[1] in ("001", "002", "004")]
    if ledger["milestones"]["M-C checkpoint 2 (P0 motion/AB)"] != p0_order:
        err("M-C checkpoint 2 milestone list mismatch")
    if (len(ledger["milestones"]["M-C checkpoint 2 (P0 motion/AB)"]) +
            len(ledger["milestones"]["M-C checkpoint 3 (campaign motion)"])
            != 63):
        err("milestone lists do not cover 63 shots")

    verdict = "PASS" if not MISMATCHES else "FAIL"
    result = {
        "validator": "check_motion_ledger.py",
        "ledger": "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json",
        "verdict": verdict,
        "mismatches": MISMATCHES,
        "checked": {
            "shots": checked,
            "dialogueShots": dialogue_shots,
            "keyframesShaVerifiedOnDisk": 63,
            "cp32FixedShotsVerified": len(mod.CP32_FIXED),
            "campaignTotals": totals,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"{verdict}: {len(MISMATCHES)} mismatches; "
          f"{checked} shots re-checked, {dialogue_shots} dialogue shots")
    sys.exit(0 if verdict == "PASS" else 1)


if __name__ == "__main__":
    main()
