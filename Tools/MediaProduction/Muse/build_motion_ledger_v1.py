#!/usr/bin/env python3
"""MEDIA-02 WO37 M-C: motion / final-picture ledger v1 for the 63 campaign shots.

Codex direction (issue #116 comment 6716052477, 2026-11-08 11:14 JST,
Work Order 37): "Motion/final-picture theo 63 shot, uu tien P0 va
shot du reference; character lock chi chan shot lien quan. Ken Burns
khong goi pose animation final; giu clean frame / canon / props /
left-bandage, khong mascot ngoai brief." The four M-C checkpoints in
WO37 run: remaining mixes + metadata -> P0 motion/AB -> campaign
motion/score/SFX/VO -> full exports/stems/provenance/QA/device pack.
This ledger is the work plan for the motion half of M-C: it sorts all
63 campaign shots (CIN_001-CIN_020; the 12 prologue CIN_000 shots are
a separate standalone film and are NOT in the 63) into an execution
order, from real files only -- timing manifests, keyframe manifests
(P0 + campaign), scene export manifests (current Ken Burns motion +
frameCheck), and the CP32 shot-fix record. No new picture is rendered
here; nothing is decided about character design.

Rules (all deterministic, re-derived by check_motion_ledger.py):
  R1  P0 shots (CIN_001/002/004, 12 shots) are ACTION_ANIMATION
      priority 1 -- Codex direction: P0 first.
  R2  A shot is character-lock-blocked for final picture when its
      final picture must show a named character recognisably:
      the dialogue speaker when dialogue.onscreen is true, or a
      named character named in the keyframe framing / knownDefects
      (including a defect-negated mention such as "Ly An is not
      individually identifiable" -- the storyboard failing to show
      her does not remove the requirement; it IS the defect).
      PLAYER is never lock-relevant: VOICE_GUIDE assigns the player
      no spoken voice/gender and the take is VOICE_PLACEHOLDER_ONLY.
  R3  Non-P0 shots with no lock requirement and no speaker-
      identifiability defect are ACTION_ANIMATION priority 2
      (ref-sufficient: the motion subject is environment / props /
      crowd / water, so the motion pass can be built from the
      storyboard reference without waiting for the character lock).
  R4  Non-P0 lock-blocked shots, and shots whose dialogue speaker
      is not identifiable in the storyboard keyframe, stay
      KEN_BURNS_HOLD priority 3 -- Ken Burns animatic until the
      character lock exists (or the final-picture revision fixes
      the identifiability defect). Ken Burns is NEVER called final
      pose animation.
  R5  Guardrails carried per shot where they apply (grounded):
      - CIN_004_S01: exactly ONE broken horn + one whole curved
        horn (P0 keyframe manifest, checkpoint 13 fix, canon).
      - CIN_008_S03: bandage on the LEFT forearm (CP32 fix).
      - CIN_012_S03: no English UI (CP32 fix).
      - CIN_017_S02: crystal core + tide serpent are the subject
        (CP32 fix).
      - CIN_015_S02: underwater, not a dry yard (CP32 fix).
      - All 14 CP32 shots: mascot / UI / wrong-subject cleanup
        verified (current keyframe SHA must equal the CP32 new SHA).
      - No mascots anywhere: no current framing text may mention
        a mascot (asserted).
  R6  Generic person mentions ("a young warden", "workers", ...)
      are recorded as genericPersonMention for audit only; they do
      not change the class, because no named character is the
      motion subject. The motion pass must still confirm this on
      the picture before animating.

Outputs: Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json
(one row per shot, with the evidence text behind every decision).
Every keyframe SHA is re-hashed from the PNG bytes on disk and
asserted against the keyframe manifest; every clip SHA / stored-frame
count is copied from the scene export manifest (measured at CP25/CP32
and re-verified by the runtime re-verify at CP52, PASS).
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(".")
OUT = (ROOT / "Implementation/Content/Narrative/Deliveries"
       / "MOTION_LEDGER_v1.json")
P0_SCENES = {"CIN_001", "CIN_002", "CIN_004"}
BASE_SHA = "6f79853"  # integration head (PR #128 merged); re-pinned CP47

# Named characters. Framing texts are English prose; Vietnamese forms
# are included where a manifest could carry them. PLAYER is excluded
# on purpose (R2): no design to lock, take is placeholder-only.
LEXICON = [
    ("NPC_LYAN", [r"\bly an\b"]),
    ("NPC_TA_VAN_KHANH", [r"\bt[ạa]\s*v[ăa]n\s*kh[áa]nh\b"]),
    ("NPC_HA_MAC", [r"\bh[ạa]\s*m[ặa]c\b"]),
    ("NPC_SAM_CHU_QUY", [r"\bs[ầa]m\b"]),
    ("NPC_CO_VO_TUONG", [r"\bc[ơo]\s*v[ôo]\s*t[ướu][ớo]ng\b"]),
    ("NPC_TONG_BANH", [r"\bt[ốo]ng\s*b[àa]nh\b"]),
    ("BOSS_MANG_COT", [r"\bm[ãa]ng\s*c[ốo]t\b"]),
    ("BOSS_TIDE_SERPENT", [r"\btide serpent\b"]),
    ("NPC_DIVER_LEAD", [r"\bdiver lead\b", r"\bdive lead\b",
                         r"\bdiver leader\b"]),
    ("NPC_REFUGEE_LEAD", [r"\brefugee leader\b"]),
]
# "serpent" alone is the boss only in CIN_004; elsewhere it is the
# tide serpent (CIN_017) or a motif. Resolved per scene, not globally.
SERPENT_SCENE = {"CIN_004": "BOSS_MANG_COT", "CIN_017": "BOSS_TIDE_SERPENT"}
GENERIC_PERSON = re.compile(
    r"\b(man|woman|figure|warden|worker|villager|elder|child|person"
    r"|people|guard|fisherman|merchant|courier|attendant)\b", re.I)
NOT_IDENTIFIABLE = re.compile(
    r"not (individually |clearly )?identifiable|not distinguishable"
    r"|not recognis|unidentifiable|cannot be identified|very small"
    r"|too small|seen only from behind|only from behind", re.I)
MASCOT = re.compile(r"\bmascot\b", re.I)

# Timing-manifest speaker IDs are not all lexicon IDs: the CIN_013
# speaker is recorded as NPC_REFUGEE_LEADER. Normalise to the
# canonical lexicon ID before matching.
SPEAKER_ALIASES = {"NPC_REFUGEE_LEADER": "NPC_REFUGEE_LEAD"}
# Role words that count as the speaker being pictured in the frame
# when the name itself is not written (CIN_018_S02 calls Co Vo Tuong
# "the engineer"; CIN_015_S03 calls the Diver Lead "a diver").
SPEAKER_ROLE_WORDS = {
    "NPC_LYAN": ["ly an"],
    "NPC_TA_VAN_KHANH": ["ta van khanh"],
    "NPC_HA_MAC": ["ha mac"],
    "NPC_SAM_CHU_QUY": ["sam"],
    "NPC_CO_VO_TUONG": ["co vo tuong", "engineer"],
    "NPC_TONG_BANH": ["tong banh"],
    "BOSS_MANG_COT": ["mang cot", "boss", "serpent"],
    "BOSS_TIDE_SERPENT": ["tide serpent", "serpent"],
    "NPC_DIVER_LEAD": ["diver lead", "diver"],
    "NPC_REFUGEE_LEAD": ["refugee leader", "leader"],
}

# CP32 (Goi 31 item 2, 2026-11-06): 14 shots re-generated; the current
# keyframe SHA must equal the NEW sha below. Source: the CP32 report
# (Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_32_SHOT_FIXES_20261106.md).
CP32_FIXED = {
    "CIN_012_S03": ("39ba784c", "84837005", "English UI bar removed; clean frame"),
    "CIN_017_S02": ("6e747e26", "710c1941", "Crystal core + tide serpent are the subject"),
    "CIN_015_S02": ("fc4e92eb", "11847adf", "Underwater, not a dry yard"),
    "CIN_012_S01": ("8c2efbd4", "489eb56b", "Mascot removed; 2 workers at the stone kiln"),
    "CIN_015_S01": ("6dd170f8", "6b067bab", "No figure standing dry on the ruin wall"),
    "CIN_015_S03": ("eb8af0fd", "e7db810d", "Clearly underwater (teal tint + bubbles)"),
    "CIN_017_S03": ("decd8051", "fe4a603b", "Armed figure removed; serpent shadow only"),
    "CIN_008_S03": ("ac807d2e", "e41232c9", "Bandage on the LEFT forearm"),
    "CIN_011_S01": ("81d4d3c0", "5762cd16", "Seated woman removed; bronze relief only"),
    "CIN_011_S03": ("316a9435", "6f167581", "Ha Mac alone, detail close-up"),
    "CIN_010_S02": ("318ffd4e", "b89f2848", "Ash-gold desert matches S01; Sam middle-aged"),
    "CIN_010_S03": ("856aa420", "d998bf59", "Ash-gold desert matches S01; Sam middle-aged"),
    "CIN_006_S02": ("0f8c4f10", "ef1a9a09", "Desk with seal marks; small gloved hand in frame"),
    "CIN_009_S01": ("d38c7ad8", "5d64d3e2", "Hooded figure removed; daylight stream"),
}
GUARDRAILS = {
    "CIN_004_S01": ["BROKEN_HORN: exactly one broken horn (short jagged stump) + one whole curved horn (canon, checkpoint 13 fix)"],
    "CIN_008_S03": ["LEFT_BANDAGE: bandage on the LEFT forearm (CP32 fix); right hand unbandaged and open"],
    "CIN_012_S03": ["NO_ENGLISH_UI: no readable English UI text in frame (CP32 fix)"],
    "CIN_017_S02": ["SUBJECT_CORE_SERPENT: crystal core + tide serpent are the subject (CP32 fix)"],
    "CIN_015_S02": ["UNDERWATER_NOT_DRY: fully underwater teal; no dry yard (CP32 fix)"],
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sentences(text: str) -> list:
    return [s.strip() for s in re.split(r"(?<=[.;])\s+", text or "") if s.strip()]


def clauses(text: str) -> list:
    """Split text into clauses (sentence, then comma/semicolon/dash/
    'while' boundaries). A failure phrase only negates a name when
    both sit in the SAME clause: in CIN_016_S02 one sentence holds
    both 'Ha Mac sits at the table' and 'the survivor ... seen only
    from behind' -- the 'seen only from behind' belongs to the
    survivor, not to Ha Mac. Commas inside parentheses do NOT split:
    CIN_019_S03 reads 'Ly An (the S03 dialogue speaker, marked
    onscreen in the timing) is not individually identifiable ...' --
    the parenthetical comma must not separate the name from its
    failure phrase."""
    out = []
    for s in sentences(text):
        # Paren-aware split on , ; -- -- and the word 'while'.
        parts, buf, depth = [], [], 0
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "(":
                depth += 1
                buf.append(ch)
            elif ch == ")":
                depth = max(0, depth - 1)
                buf.append(ch)
            elif depth == 0 and ch in ",;—–":
                parts.append("".join(buf))
                buf = []
            elif depth == 0 and s[i:i + 5] == "while" and (
                    i == 0 or not s[i - 1].isalnum()) and (
                    i + 5 >= len(s) or not s[i + 5].isalnum()):
                parts.append("".join(buf))
                buf = []
                i += 5
                continue
            else:
                buf.append(ch)
            i += 1
        parts.append("".join(buf))
        out.extend(p.strip() for p in parts if p.strip())
    return out


def find_names(text: str, scene_id: str) -> dict:
    """Return {characterId: [evidence clauses]} for names in text."""
    found = {}
    for char_id, patterns in LEXICON:
        for pat in patterns:
            for m in re.finditer(pat, text or "", re.I):
                for c in clauses(text or ""):
                    if m.group(0).lower() in c.lower():
                        found.setdefault(char_id, []).append(c)
                        break
    if scene_id in SERPENT_SCENE:
        for m in re.finditer(r"\bserpent\b", text or "", re.I):
            for c in clauses(text or ""):
                if "serpent" in c.lower():
                    found.setdefault(SERPENT_SCENE[scene_id], []).append(c)
                    break
    return found


def main() -> None:
    # --- keyframes: P0 manifest (12) + campaign manifests (51) ---
    keyframes = {}
    p0 = load_json(ROOT / "Art_Source/Cinematics/P0_Animatic"
                   / "P0_keyframes_16x9_manifest_v1.json")
    for s in p0["shots"]:
        keyframes[s["shotId"]] = {
            "file": s["file"], "sha256": s["sha256"],
            "framing": s.get("framingNote", ""),
            "defects": [], "status": s.get("finalPictureStatus", "STORYBOARD_ONLY"),
        }
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
                "status": m.get("status", "STORYBOARD"),
            }
    if len(keyframes) != 63:
        print(f"KEYFRAME COUNT {len(keyframes)} != 63", file=sys.stderr)
        sys.exit(1)

    runtime = load_json(ROOT / "ClientGodot/assets/cinematics"
                        / "RUNTIME_CINEMATICS_manifest_v1.json")
    totals = runtime["campaignTotals"]
    assert (totals["scenes"], totals["shots"], totals["seconds"],
            totals["dialogueCues"]) == (20, 63, 378, 21), totals

    rows = []
    dialogue_shots = 0
    for n in range(1, 21):
        scene_id = f"CIN_{n:03d}"
        timing = load_json(ROOT / "Implementation/Content/Narrative"
                           / "Deliveries" / scene_id
                           / f"{scene_id}_timing_v1.json")
        export = load_json(ROOT / "ClientGodot/assets/cinematics"
                           / scene_id / "scene_export_manifest_v1.json")
        motion = export.get("motionModel", {})
        motion_shots = motion.get("shots", {})
        frame_check = export.get("frameCheck", {})
        for shot in timing["shots"]:
            shot_id = shot["shotId"]
            kf = keyframes[shot_id]
            # Keyframe bytes on disk must match the manifest SHA.
            disk_sha = sha256(ROOT / kf["file"])
            if disk_sha != kf["sha256"]:
                print(f"KEYFRAME SHA MISMATCH {shot_id}: disk "
                      f"{disk_sha[:8]} != manifest {kf['sha256'][:8]}",
                      file=sys.stderr)
                sys.exit(1)
            if shot_id in CP32_FIXED:
                old, new, _note = CP32_FIXED[shot_id]
                if not disk_sha.startswith(new):
                    print(f"CP32 FIX LOST {shot_id}: current "
                          f"{disk_sha[:8]} != CP32 new {new}",
                          file=sys.stderr)
                    sys.exit(1)
            text = (kf["framing"] + " " +
                    " ".join(kf["defects"])).strip()
            # R5: the FRAMING (current picture) must not contain a
            # mascot. A defect note may legitimately record the
            # absence ("No person, no hooded figure, no mascot") --
            # that is positive evidence, not a violation.
            if MASCOT.search(kf["framing"]):
                print(f"MASCOT IN FRAMING {shot_id}: "
                      f"{kf['framing'][:120]}", file=sys.stderr)
                sys.exit(1)

            dlg = shot.get("dialogue")
            if dlg:
                dialogue_shots += 1
            speaker_raw = dlg.get("speaker") if dlg else None
            speaker = (SPEAKER_ALIASES.get(speaker_raw, speaker_raw)
                       if speaker_raw else None)
            onscreen = dlg.get("onscreen") if dlg else None
            names = find_names(text, scene_id)
            # A defect-negated mention still requires the character
            # in final picture (R2); it is not visible in storyboard.
            negated = set()
            for char_id, evs in names.items():
                for ev in evs:
                    if NOT_IDENTIFIABLE.search(ev):
                        negated.add(char_id)
            # Speaker identifiability: (a) a defect sentence about
            # the speaker's figure failing to identify them, or
            # (b) the speaker not pictured at all although the
            # timing marks them onscreen (CIN_013_S03: timing says
            # the Refugee Leader speaks onscreen, the keyframe
            # shows only Ly An -- CP47 staging question).
            speaker_fail = False
            speaker_in_frame = False
            if dlg and onscreen is True and speaker and speaker != "PLAYER":
                role_words = SPEAKER_ROLE_WORDS.get(speaker, [])
                patterns = dict(LEXICON).get(speaker, [])
                for c in clauses(text):
                    low = c.lower()
                    mentions = (any(re.search(p, c, re.I) for p in patterns)
                                or any(w in low for w in role_words))
                    if mentions:
                        speaker_in_frame = True
                        if NOT_IDENTIFIABLE.search(c):
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
            speaker_identifiable = None
            if dlg:
                speaker_identifiable = bool(
                    onscreen is True and not speaker_fail)
            ident_defect = bool(speaker_fail)
            speaker_not_in_frame = bool(
                dlg and onscreen is True and speaker
                and speaker != "PLAYER" and not speaker_in_frame)
            lock_required = bool(required)
            is_p0 = scene_id in P0_SCENES
            if is_p0:
                motion_class, priority = "ACTION_ANIMATION", 1
                reason = "P0: Codex direction, P0 motion first"
            elif lock_required or ident_defect:
                motion_class, priority = "KEN_BURNS_HOLD", 3
                reason = ("Character lock required for final picture"
                          if lock_required else
                          "Dialogue speaker not identifiable in storyboard")
                if lock_required and ident_defect:
                    reason += " + speaker not identifiable in storyboard"
            else:
                motion_class, priority = "ACTION_ANIMATION", 2
                reason = ("Ref-sufficient: motion subject is environment / "
                          "props / crowd / water, no named character to lock")
            fc = frame_check.get(shot_id, {})
            rows.append({
                "shotId": shot_id,
                "sceneId": scene_id,
                "sceneTitle": timing.get("title"),
                "camera": shot.get("camera"),
                "startSeconds": shot["startSeconds"],
                "endSeconds": shot["endSeconds"],
                "keyframe": {
                    "file": kf["file"],
                    "sha256": kf["sha256"],
                    "sha256VerifiedOnDisk": True,
                    "status": kf["status"],
                },
                "keyframeDefects": kf["defects"],
                "currentMotion": {
                    "model": motion.get("kind", "ANIMATIC_MOTION_KEN_BURNS"),
                    "shotMove": motion_shots.get(shot_id),
                    "videoStatus": export.get("videoStatus"),
                    "motionMeanAbsChannelDiff": fc.get(
                        "motionMeanAbsChannelDiff"),
                    "identityMeanAbsChannelDiff": fc.get(
                        "identityMeanAbsChannelDiff"),
                },
                "dialogue": ({
                    "speaker": speaker_raw,
                    "speakerCanonical": speaker,
                    "speakerDisplay": dlg.get("speakerDisplay"),
                    "onscreen": onscreen,
                    "windowSeconds": dlg.get("windowSeconds"),
                    "text": dlg.get("text"),
                } if dlg else None),
                "speakerIdentifiableInStoryboard": speaker_identifiable,
                "speakerIdentifiabilityDefect": ident_defect,
                "speakerNotInFrame": speaker_not_in_frame,
                "namedCharactersVisible": visible,
                "namedCharactersRequired": required,
                "characterLockRequired": lock_required,
                "genericPersonMention": bool(GENERIC_PERSON.search(text)),
                "mascotFreeConfirmed": bool(
                    re.search(r"no mascot", " ".join(kf["defects"]), re.I)),
                "motionClass": motion_class,
                "priority": priority,
                "reason": reason,
                "guardrails": GUARDRAILS.get(shot_id, []),
                "cp32Fixed": ({"oldShaPrefix": CP32_FIXED[shot_id][0],
                               "newShaPrefix": CP32_FIXED[shot_id][1],
                               "fix": CP32_FIXED[shot_id][2]}
                              if shot_id in CP32_FIXED else None),
            })
    if dialogue_shots != 21:
        print(f"DIALOGUE SHOTS {dialogue_shots} != 21", file=sys.stderr)
        sys.exit(1)

    by_class = {}
    by_priority = {}
    for r in rows:
        by_class[r["motionClass"]] = by_class.get(r["motionClass"], 0) + 1
        by_priority[r["priority"]] = by_priority.get(r["priority"], 0) + 1
    order = [r["shotId"] for r in sorted(
        rows, key=lambda r: (r["priority"], r["sceneId"], r["shotId"]))]
    ledger = {
        "ledgerId": "NGM_MOTION_LEDGER_V1",
        "checkpoint": ("MEDIA-02 WO37 M-C: motion / final-picture ledger v1 "
                       "(63 campaign shots; P0 motion first, then "
                       "ref-sufficient shots, then character-lock-blocked shots)"),
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrder": "WO37 (issue #116 comment 6716052477, 2026-11-08 11:14 JST)",
        "branch": "muse/media-production-20261104",
        "baseSha": BASE_SHA,
        "status": "PLAN_NOT_FINAL_PICTURE",
        "scopeNote": ("Covers the 63 campaign shots only (CIN_001-CIN_020). "
                      "The 12 prologue CIN_000 shots are a separate standalone "
                      "film and are not in this ledger. All 63 keyframes are "
                      "STORYBOARD level; no final picture exists for any shot. "
                      "Ken Burns is the current animatic motion, never final "
                      "pose animation. Action animation is 8-12 pose fps per "
                      "WO37 M-C."),
        "sources": {
            "timingManifests": ("Implementation/Content/Narrative/Deliveries/"
                                "CIN_XXX/CIN_XXX_timing_v1.json (20 files)"),
            "keyframeManifests": ("Art_Source/Cinematics/P0_Animatic/"
                                  "P0_keyframes_16x9_manifest_v1.json (12 shots) + "
                                  "Art_Source/Cinematics/Campaign/*/CIN*_keyframes_manifest_v1.json "
                                  "(17 files, 51 shots)"),
            "exportManifests": ("ClientGodot/assets/cinematics/CIN_XXX/"
                                "scene_export_manifest_v1.json (20 files)"),
            "campaignTotals": ("ClientGodot/assets/cinematics/"
                               "RUNTIME_CINEMATICS_manifest_v1.json: "
                               "20 scenes / 63 shots / 378 s / 21 dialogue cues"),
            "shotFixes": ("Implementation/Reports/MuseMedia/"
                          "MEDIA02_CHECKPOINT_32_SHOT_FIXES_20261106.md "
                          "(14 shots, old->new keyframe SHA)"),
        },
        "rules": [
            "R1 P0 shots (CIN_001/002/004, 12 shots): ACTION_ANIMATION priority 1.",
            "R2 Character lock required when final picture must show a named character recognisably: dialogue speaker with onscreen true, or a named character named in the keyframe framing/knownDefects (a defect-negated mention still requires the character). PLAYER is never lock-relevant (VOICE_PLACEHOLDER_ONLY).",
            "R3 Non-P0 shots with no lock requirement and no speaker-identifiability defect: ACTION_ANIMATION priority 2 (ref-sufficient).",
            "R4 Non-P0 lock-blocked shots, and shots whose dialogue speaker is not identifiable in the storyboard keyframe (defect says so, or the speaker is not pictured at all although timing marks them onscreen): KEN_BURNS_HOLD priority 3 until the character lock / final-picture revision exists.",
            "R5 Guardrails: broken horn (CIN_004_S01, 1 broken + 1 whole, canon); LEFT bandage (CIN_008_S03); no English UI (CIN_012_S03); crystal core + tide serpent subject (CIN_017_S02); underwater not dry yard (CIN_015_S02); no mascots anywhere (asserted: no current framing text mentions a mascot).",
            "R6 Generic person mentions are recorded for audit only and do not change the class; the motion pass must confirm on the picture that no named character is the motion subject.",
        ],
        "totals": {
            "shots": len(rows),
            "dialogueShots": dialogue_shots,
            "byMotionClass": by_class,
            "byPriority": {str(k): v for k, v in sorted(by_priority.items())},
            "characterLockRequired": sum(1 for r in rows if r["characterLockRequired"]),
            "speakerIdentifiabilityDefects": sum(
                1 for r in rows if r["speakerIdentifiabilityDefect"]),
            "speakerNotInFrame": sum(
                1 for r in rows if r["speakerNotInFrame"]),
            "cp32FixedShots": len(CP32_FIXED),
            "keyframesShaVerifiedOnDisk": sum(
                1 for r in rows if r["keyframe"]["sha256VerifiedOnDisk"]),
        },
        "guardrailsGlobal": [
            "Keep the LEFT bandage (CIN_008_S03); keep the broken horn (CIN_004_S01: exactly one broken + one whole); keep props as staged in each keyframe.",
            "No mascots anywhere (CP32 removed them from 14 shots; this ledger asserts no current framing text mentions one -- a defect note recording 'no mascot' is positive absence evidence, not a violation).",
            "No English UI in CIN_012 (CP32 fix); no wrong subject in CIN_017 (CP32 fix); no dry yard in CIN_015 (CP32 fix).",
            "Ken Burns is animatic motion only -- never call it final pose animation; final picture per shot stays blocked on the character lock where required.",
        ],
        "executionOrder": order,
        "milestones": {
            "M-C checkpoint 2 (P0 motion/AB)": [s for s in order
                                                if s.split("_")[1] in
                                                ("001", "002", "004")],
            "M-C checkpoint 3 (campaign motion)": [s for s in order
                                                   if s.split("_")[1] not in
                                                   ("001", "002", "004")],
        },
        "shots": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    print(f"OK: {OUT} ({len(rows)} shots; "
          f"ACTION_ANIMATION={by_class.get('ACTION_ANIMATION', 0)}, "
          f"KEN_BURNS_HOLD={by_class.get('KEN_BURNS_HOLD', 0)}; "
          f"lock-required={ledger['totals']['characterLockRequired']}; "
          f"ident-defects={ledger['totals']['speakerIdentifiabilityDefects']})")


if __name__ == "__main__":
    main()
