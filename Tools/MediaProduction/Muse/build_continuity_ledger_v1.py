#!/usr/bin/env python3
"""MEDIA-02 WO37 M-C CP4 — Continuity ledger v1 (63 campaign shots).

Builds Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v1.json
from real files on disk. No new picture, no new audio, no character decision:
this ledger cross-checks what already exists for continuity across shots.

Rules (K1-K6), all derived from sources, never from a stale summary:
  K1 Timing tiling: per scene, shots from the timing manifest tile
     contiguously (end[n] == start[n+1] +/-0.001), first shot starts at
     0.0, last shot ends at the scene duration; ledger timing must equal
     timing-manifest timing per shot; scene duration must agree across
     timing manifest / scene export manifest / mix manifest; campaign
     totals must be 20 scenes / 63 shots / 378 s / 21 dialogue cues.
  K2 SRT/dialogue: the runtime-manifest SRT (sha-verified) must decode
     UTF-8, be NFC + LF-only, have cue count == export-manifest
     dialogueCues, non-overlapping ordered cues; every dialogue shot
     must have exactly one cue, window inside the shot, text (NFC) ==
     ledger dialogue text; scenes without dialogue have 0 cues.
  K3 Character continuity: per scene, per named character (visible or
     required), the shot sequence is listed; BLINK = visible, absent
     >=1 shot, visible again in the same scene; REQUIRED_NOT_VISIBLE =
     required but not visible in a shot; dialogue speaker not visible
     in its own shot is a FLAG unless the ledger already records it as
     speakerNotInFrame / speaker-identifiability defect (staging note).
  K4 Guardrail continuity: each R5 guardrail key is traced across its
     scene: every other shot where the same subject (named character,
     or whole-scene for environment-level keys) appears should carry
     the same guardrail assertion; unasserted shots are NOTE findings
     (documentation coverage, not a picture verdict).
  K5 Audio coverage per shot: from the current mix manifest per scene
     (P0 scenes -> P0_MIX_V3, others -> CINxxx_DRAFT_V1), stems with
     segmentSceneSeconds cover overlapping shots, stingers cover the
     shot containing atSeconds, VO covers overlapping shots. Flags:
     DRY_SHOT (no music/ambience/stinger/vo), SEGMENT_BOUNDARY_MID_SHOT
     (a music/ambience segment starts/ends strictly inside a shot),
     STINGER_AT_SHOT_BOUNDARY. Ambience loop-seam wrapJumpMeasured is
     attached from the pronunciation seam table (composed preferred).
  K6 Mix cross-check: mix scene seconds == scene duration; mix VO
     window vs ledger/SRT window is recorded (a take ending before the
     locked window end is a NOTE; the mix manifest already documents
     overrunVsWindowSeconds).

Output: CONTINUITY_LEDGER_v1.json next to MOTION_LEDGER_v1.json.
Checker: check_continuity_ledger_v1.py (independent re-derivation).
"""
import hashlib
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"
RUNTIME = ROOT / "ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json"
PRON = ROOT / "Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json"
OUT = ROOT / "Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v1.json"

TOL = 0.001
SCENES = ["CIN_%03d" % i for i in range(1, 21)]
P0 = {"CIN_001", "CIN_002", "CIN_004"}
GUARDRAIL_SUBJECT = {
    "BROKEN_HORN": "BOSS_MANG_COT",
    "LEFT_BANDAGE": "NPC_TA_VAN_KHANH",
    "SUBJECT_CORE_SERPENT": "BOSS_TIDE_SERPENT",
    # NO_ENGLISH_UI and UNDERWATER_NOT_DRY are scene/environment level.
}


def sha256_file(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def parse_srt(path):
    """Return (cues, checks). cues: [{index, start, end, text}]."""
    raw = Path(path).read_bytes()
    checks = {
        "bytes": len(raw),
        "utf8Ok": True,
        "hasCR": b"\r" in raw,
        "endsWithLF": raw.endswith(b"\n"),
    }
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        checks["utf8Ok"] = False
        return [], checks
    checks["nfcOk"] = unicodedata.is_normalized("NFC", text)
    cues = []
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = re.match(
            r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})",
            lines[1].strip(),
        )
        if not m:
            continue
        def ts(g):
            return int(g[0]) * 3600 + int(g[1]) * 60 + int(g[2]) + int(g[3]) / 1000.0
        cues.append({
            "index": int(lines[0].strip()),
            "start": ts(m.groups()[:4]),
            "end": ts(m.groups()[4:]),
            "text": "\n".join(lines[2:]).strip(),
        })
    return cues, checks


def mix_manifest_for(scene_id):
    if scene_id in P0:
        return ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json"
    return ROOT / ("Art_Source/Audio/Muse/MIX/%s_DRAFT_V1/%s_MIX_V1_manifest_v1.json"
                   % (scene_id.replace("_", ""), scene_id.replace("_", "")))


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    runtime = json.loads(RUNTIME.read_text(encoding="utf-8"))
    pron = json.loads(PRON.read_text(encoding="utf-8"))
    shots = ledger["shots"]
    by_shot = {s["shotId"]: s for s in shots}
    by_scene = {}
    for s in shots:
        by_scene.setdefault(s["sceneId"], []).append(s)
    for v in by_scene.values():
        v.sort(key=lambda s: s["startSeconds"])

    seam = {}
    for row in pron["seamTable"]:
        key = (row["cueKey"], row["version"])
        seam[key] = row

    findings = []
    def add(sev, cat, shot_ids, evidence, sources):
        findings.append({
            "id": "F%03d" % (len(findings) + 1),
            "severity": sev, "category": cat,
            "shots": shot_ids, "evidence": evidence, "sources": sources,
        })

    scene_rows = []
    shot_rows = []
    total_duration = 0.0
    total_shots = 0
    total_cues = 0

    for scene_id in SCENES:
        timing_path = ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % scene_id)
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        export_path = ROOT / ("ClientGodot/assets/cinematics/%s/scene_export_manifest_v1.json" % scene_id)
        export = json.loads(export_path.read_text(encoding="utf-8"))
        rt_scene = next(s for s in runtime["scenes"] if s["sceneId"] == scene_id)
        srt_path = ROOT / ("ClientGodot/assets/cinematics/timing/%s_vi.srt" % scene_id)
        srt_raw = srt_path.read_bytes()
        srt_sha_ok = hashlib.sha256(srt_raw).hexdigest() == rt_scene["srtSha256"]
        timing_sha_ok = sha256_file(timing_path) == rt_scene["timingSha256"]
        cues, srt_checks = parse_srt(srt_path)
        mix_path = mix_manifest_for(scene_id)
        mix = json.loads(mix_path.read_text(encoding="utf-8"))
        mix_scene = next(s for s in mix["scenes"] if s["sceneId"] == scene_id)
        scene_shots = by_scene[scene_id]
        dur = timing["durationSeconds"]

        # ---- K1: tiling from the timing manifest ----
        tiling_ok = True
        tiling_notes = []
        tshots = timing["shots"]
        if abs(tshots[0]["startSeconds"] - 0.0) > TOL:
            tiling_ok = False
            tiling_notes.append("first shot starts at %s, not 0.0" % tshots[0]["startSeconds"])
        for a, b in zip(tshots, tshots[1:]):
            if abs(a["endSeconds"] - b["startSeconds"]) > TOL:
                tiling_ok = False
                tiling_notes.append("%s ends %s but %s starts %s"
                                    % (a["shotId"], a["endSeconds"], b["shotId"], b["startSeconds"]))
        if abs(tshots[-1]["endSeconds"] - dur) > TOL:
            tiling_ok = False
            tiling_notes.append("last shot ends %s, scene duration %s" % (tshots[-1]["endSeconds"], dur))
        ledger_timing_ok = True
        for ts in tshots:
            ls = by_shot[ts["shotId"]]
            if abs(ls["startSeconds"] - ts["startSeconds"]) > TOL or abs(ls["endSeconds"] - ts["endSeconds"]) > TOL:
                ledger_timing_ok = False
        if len(tshots) != len(scene_shots):
            tiling_ok = False
            tiling_notes.append("timing manifest has %d shots, ledger has %d" % (len(tshots), len(scene_shots)))
        dur_agree = (abs(export["durationSeconds"] - dur) <= TOL
                     and abs(mix_scene["seconds"] - dur) <= TOL
                     and rt_scene["durationSeconds"] == dur)
        if not dur_agree:
            add("FLAG", "K1_DURATION_MISMATCH", [s["shotId"] for s in scene_shots],
                "scene duration disagrees: timing %s / export %s / mix %s / runtime %s"
                % (dur, export["durationSeconds"], mix_scene["seconds"], rt_scene["durationSeconds"]),
                [str(timing_path), str(export_path), str(mix_path)])
        if not tiling_ok:
            add("FLAG", "K1_TILING", [s["shotId"] for s in scene_shots],
                "; ".join(tiling_notes), [str(timing_path)])
        if not ledger_timing_ok:
            add("FLAG", "K1_LEDGER_TIMING", [s["shotId"] for s in scene_shots],
                "motion ledger shot timing differs from timing manifest", [str(timing_path)])

        # ---- K2: SRT / dialogue ----
        srt_ok = (srt_sha_ok and srt_checks["utf8Ok"] and not srt_checks["hasCR"]
                  and srt_checks["nfcOk"] and len(cues) == export["dialogueCues"])
        if not srt_sha_ok:
            add("FLAG", "K2_SRT_SHA", [s["shotId"] for s in scene_shots],
                "SRT sha256 differs from runtime manifest", [str(srt_path)])
        if not srt_checks["utf8Ok"] or srt_checks["hasCR"] or not srt_checks["nfcOk"]:
            add("FLAG", "K2_SRT_ENCODING", [s["shotId"] for s in scene_shots],
                "utf8Ok=%s hasCR=%s nfcOk=%s" % (srt_checks["utf8Ok"], srt_checks["hasCR"], srt_checks["nfcOk"]),
                [str(srt_path)])
        if len(cues) != export["dialogueCues"]:
            add("FLAG", "K2_SRT_CUE_COUNT", [s["shotId"] for s in scene_shots],
                "SRT has %d cues, export manifest says %d" % (len(cues), export["dialogueCues"]),
                [str(srt_path)])
        ordered = all(cues[i]["end"] <= cues[i + 1]["start"] + TOL for i in range(len(cues) - 1))
        if not ordered:
            add("FLAG", "K2_SRT_OVERLAP", [s["shotId"] for s in scene_shots],
                "SRT cues overlap or are out of order in scene", [str(srt_path)])
        dlg_shots = [s for s in scene_shots if s["dialogue"]]
        cue_by_shot = {}
        for s in dlg_shots:
            w = s["dialogue"]["windowSeconds"]
            match = [c for c in cues
                     if abs(c["start"] - w[0]) <= TOL and abs(c["end"] - w[1]) <= TOL]
            if len(match) != 1:
                add("FLAG", "K2_DIALOGUE_CUE", [s["shotId"]],
                    "dialogue window %s matches %d SRT cues (expected 1)" % (w, len(match)),
                    [str(srt_path)])
                continue
            cue = match[0]
            cue_by_shot[s["shotId"]] = cue
            if cue["start"] < s["startSeconds"] - TOL or cue["end"] > s["endSeconds"] + TOL:
                add("FLAG", "K2_WINDOW_OUTSIDE_SHOT", [s["shotId"]],
                    "cue %s-%s outside shot %s-%s"
                    % (cue["start"], cue["end"], s["startSeconds"], s["endSeconds"]),
                    [str(srt_path)])
            if unicodedata.normalize("NFC", cue["text"]) != unicodedata.normalize("NFC", s["dialogue"]["text"]):
                add("FLAG", "K2_SRT_TEXT", [s["shotId"]],
                    "SRT text differs from ledger dialogue text", [str(srt_path)])
        if not dlg_shots and cues:
            add("FLAG", "K2_UNEXPECTED_CUES", [s["shotId"] for s in scene_shots],
                "scene has %d SRT cues but no dialogue shot in ledger" % len(cues), [str(srt_path)])

        # ---- K5: audio coverage per shot (mix manifest) ----
        # VO entries: mix manifests carry either a `voices` list (one entry
        # per dialogue shot, with shotId — e.g. CIN_018) or a single `vo`.
        vo_entries = mix_scene.get("voices")
        if not vo_entries:
            single = mix_scene.get("vo") or {}
            vo_entries = [single] if single else []
        vo_by_shot = {}
        for ve in vo_entries:
            sid = ve.get("shotId")
            if not sid:
                dlg = [s for s in scene_shots if s["dialogue"]]
                if len(dlg) == 1:
                    sid = dlg[0]["shotId"]
            if sid:
                vo_by_shot[sid] = ve
        vo_windows = [ve.get("windowSeconds") for ve in vo_entries if ve.get("windowSeconds")]
        stems = mix_scene.get("stems", [])
        for s in scene_shots:
            a, b = s["startSeconds"], s["endSeconds"]
            roles = []
            covering = []
            for st in stems:
                seg = st.get("segmentSceneSeconds")
                if seg and seg[1] - a > TOL and b - seg[0] > TOL:
                    roles.append(st["role"])
                    covering.append({"cue": st["cue"], "role": st["role"],
                                     "segmentSceneSeconds": seg})
                    if st["role"] in ("music", "ambience"):
                        if a + TOL < seg[0] < b - TOL or a + TOL < seg[1] < b - TOL:
                            add("NOTE", "K5_SEGMENT_BOUNDARY_MID_SHOT", [s["shotId"]],
                                "%s %s starts/ends inside shot (%s-%s within %s-%s)"
                                % (st["role"], st["cue"], seg[0], seg[1], a, b),
                                [str(mix_path)])
                at = st.get("atSeconds")
                if at is not None:
                    # A stinger belongs to the shot that STARTS at its
                    # placement second (reveal at 6.0 s opens S02); only
                    # if no shot starts there does it fall in the
                    # containing shot. One finding per stinger, not two.
                    starts_here = abs(at - a) <= TOL
                    contains = a - TOL <= at <= b + TOL and not starts_here
                    shot_starts = [x["startSeconds"] for x in scene_shots]
                    if starts_here or (contains and not any(abs(at - ss) <= TOL for ss in shot_starts)):
                        roles.append(st["role"])
                        covering.append({"cue": st["cue"], "role": st["role"], "atSeconds": at})
                        bounds = [x["startSeconds"] for x in scene_shots] + [scene_shots[-1]["endSeconds"]]
                        if any(abs(at - bd) <= TOL for bd in bounds):
                            add("NOTE", "K5_STINGER_AT_SHOT_BOUNDARY", [s["shotId"]],
                                "%s placed at %.3f s, exactly on a shot boundary (opens this shot)"
                                % (st["cue"], at),
                                [str(mix_path)])
            for vw in vo_windows:
                if vw[1] - a > TOL and b - vw[0] > TOL:
                    roles.append("vo")
            roles = sorted(set(roles))
            if not roles:
                add("FLAG", "K5_DRY_SHOT", [s["shotId"]],
                    "no music/ambience/stinger/vo stem covers this shot in the current mix",
                    [str(mix_path)])
            amb_seams = []
            for c in covering:
                if c["role"] == "ambience":
                    row = seam.get((c["cue"], "composed")) or seam.get((c["cue"], "ported"))
                    if row:
                        amb_seams.append({"cue": c["cue"],
                                          "version": row["version"],
                                          "wrapJumpMeasured": row["wrapJumpMeasured"],
                                          "flagEarCheck": row["flagEarCheck"]})
                        if row["wrapJumpMeasured"] > 0.005:
                            add("NOTE", "K5_AMBIENCE_SEAM_HIGH", [s["shotId"]],
                                "%s (%s) loop wrap jump %.6f > 0.005; ear-check flag=%s"
                                % (c["cue"], row["version"], row["wrapJumpMeasured"], row["flagEarCheck"]),
                                ["Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json"])
            shot_rows.append({
                "shotId": s["shotId"], "sceneId": scene_id,
                "startSeconds": a, "endSeconds": b,
                "audioRoles": roles,
                "stemsCovering": covering,
                "ambienceLoopSeams": amb_seams,
                "dialogueShot": bool(s["dialogue"]),
                "voWindowInMix": (vo_by_shot[s["shotId"]].get("windowSeconds")
                                  if s["shotId"] in vo_by_shot else None),
            })
        # K6: mix VO take extent vs locked/SRT window, matched by shotId.
        # Mix `windowSeconds` is the take's actual placement [start, takeEnd]
        # (takeEndSeconds when present); the locked window end is
        # `windowEndSeconds` when present, else the ledger/SRT window end.
        for s in dlg_shots:
            ve = vo_by_shot.get(s["shotId"])
            w = s["dialogue"]["windowSeconds"]
            if not ve:
                add("FLAG", "K6_MIX_VO_MISSING", [s["shotId"]],
                    "dialogue shot but no VO entry for this shotId in the mix manifest",
                    [str(mix_path)])
                continue
            vw = ve.get("windowSeconds")
            if not vw:
                add("FLAG", "K6_MIX_VO_MISSING", [s["shotId"]],
                    "VO entry for this shot has no windowSeconds", [str(mix_path)])
                continue
            take_end = ve.get("takeEndSeconds", vw[1])
            locked_end = ve.get("windowEndSeconds", w[1])
            if abs(vw[0] - w[0]) > TOL or abs(locked_end - w[1]) > TOL:
                add("FLAG", "K6_MIX_VO_WINDOW_MISMATCH", [s["shotId"]],
                    "mix VO window %s (locked end %s) vs locked/SRT window %s"
                    % (vw, locked_end, w), [str(mix_path)])
            delta = take_end - w[1]
            if abs(delta) > TOL:
                verb = "overruns the locked window end by %.3f s" % delta if delta > 0 \
                    else "ends %.3f s before the locked window end" % (-delta)
                add("NOTE", "K6_VO_TAKE_EXTENT", [s["shotId"]],
                    "take %s ends at %.3f s; locked window ends %.3f s — %s "
                    "(mix manifest records overrunVsWindowSeconds=%s)"
                    % (ve.get("take", "?"), take_end, w[1], verb,
                       ve.get("overrunVsWindowSeconds", "n/a")),
                    [str(mix_path)])

        total_duration += dur
        total_shots += len(scene_shots)
        total_cues += export["dialogueCues"]
        scene_rows.append({
            "sceneId": scene_id,
            "durationSeconds": dur,
            "shots": len(scene_shots),
            "dialogueCues": export["dialogueCues"],
            "timingShaMatchesRuntimeManifest": timing_sha_ok,
            "srtShaMatchesRuntimeManifest": srt_sha_ok,
            "srtChecks": srt_checks,
            "tilingOk": tiling_ok,
            "ledgerTimingMatchesTimingManifest": ledger_timing_ok,
            "durationsAgreeAcrossSources": dur_agree,
            "srtCueCountMatchesExport": len(cues) == export["dialogueCues"],
            "srtCuesOrderedNonOverlapping": ordered,
            "mixManifest": str(mix_path.relative_to(ROOT)),
            "mixSeconds": mix_scene["seconds"],
        })

    # ---- K3: character continuity (per scene, cross-shot) ----
    char_rows = []
    for scene_id in SCENES:
        scene_shots = by_scene[scene_id]
        chars = set()
        for s in scene_shots:
            chars.update(s["namedCharactersVisible"])
            chars.update(s["namedCharactersRequired"])
        for ch in sorted(chars):
            vis_idx = [i for i, s in enumerate(scene_shots) if ch in s["namedCharactersVisible"]]
            req_idx = [i for i, s in enumerate(scene_shots) if ch in s["namedCharactersRequired"]]
            blinks = []
            for j in range(len(vis_idx) - 1):
                gap = vis_idx[j + 1] - vis_idx[j]
                if gap > 1:
                    blinks.append({"fromShot": scene_shots[vis_idx[j]]["shotId"],
                                   "toShot": scene_shots[vis_idx[j + 1]]["shotId"],
                                   "absentShots": [scene_shots[k]["shotId"]
                                                   for k in range(vis_idx[j] + 1, vis_idx[j + 1])]})
                    add("NOTE", "K3_CHARACTER_BLINK", [scene_shots[vis_idx[j]]["shotId"],
                                                        scene_shots[vis_idx[j + 1]]["shotId"]],
                        "%s visible in %s, absent %d shot(s), visible again in %s (same scene; "
                        "cut explains it unless the storyboard says otherwise)"
                        % (ch, scene_shots[vis_idx[j]]["shotId"], gap - 1, scene_shots[vis_idx[j + 1]]["shotId"]),
                        ["Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            req_not_vis = [scene_shots[i]["shotId"] for i in req_idx if i not in vis_idx]
            for sid in req_not_vis:
                add("NOTE", "K3_REQUIRED_NOT_VISIBLE", [sid],
                    "%s required but not visible in this shot (ledger records the staging reason)"
                    % ch, ["Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            char_rows.append({
                "character": ch, "sceneId": scene_id,
                "visibleShotIds": [scene_shots[i]["shotId"] for i in vis_idx],
                "requiredShotIds": [scene_shots[i]["shotId"] for i in req_idx],
                "blinks": blinks,
                "requiredNotVisibleShotIds": req_not_vis,
            })
    # dialogue speaker visibility
    for s in shots:
        if not s["dialogue"]:
            continue
        sp = s["dialogue"]["speaker"]
        onscreen = s["dialogue"].get("onscreen")
        if sp is None:
            add("FLAG", "K3_SPEAKER_NO_ID", [s["shotId"]],
                "dialogue speaker has no canonical ID in the timing manifest or the "
                "ledger (speakerDisplay=%r); the take exists as a placeholder role "
                "voice, but no speaker ID is recorded for final-picture/VO continuity"
                % s["dialogue"].get("speakerDisplay"),
                ["ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % s["sceneId"],
                 "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            continue
        if sp == "PLAYER":
            continue
        if sp not in s["namedCharactersVisible"]:
            if onscreen is False:
                add("NOTE", "K3_SPEAKER_OFFSCREEN_DECIDED", [s["shotId"]],
                    "speaker %s not visible in its dialogue shot; onscreen=false in the "
                    "timing manifest and the ledger (designed voice off-screen)"
                    % sp,
                    ["ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % s["sceneId"],
                     "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            elif s["speakerNotInFrame"] or s["speakerIdentifiabilityDefect"]:
                add("NOTE", "K3_SPEAKER_OFFSCREEN_STAGING", [s["shotId"]],
                    "speaker %s not visible in its dialogue shot; ledger records it as "
                    "speakerNotInFrame=%s / identifiability defect=%s (staging note, not a mix defect)"
                    % (sp, s["speakerNotInFrame"], s["speakerIdentifiabilityDefect"]),
                    ["Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            else:
                add("FLAG", "K3_SPEAKER_NOT_VISIBLE", [s["shotId"]],
                    "speaker %s not visible in its dialogue shot; onscreen=null in the "
                    "timing manifest and the ledger, and the ledger records no off-screen "
                    "staging note — director decision needed: mark off-screen or fix the picture"
                    % sp,
                    ["ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % s["sceneId"],
                     "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])

    # ---- K4: guardrail continuity ----
    guard_rows = []
    for s in shots:
        for g in s["guardrails"]:
            key = g.split(":", 1)[0].strip()
            subject = GUARDRAIL_SUBJECT.get(key)
            scene_shots = by_scene[s["sceneId"]]
            if subject:
                appearances = [x["shotId"] for x in scene_shots
                               if subject in x["namedCharactersVisible"] or subject in x["namedCharactersRequired"]]
            else:
                appearances = [x["shotId"] for x in scene_shots]
            asserted = [x["shotId"] for x in scene_shots
                        if any(gr.split(":", 1)[0].strip() == key for gr in x["guardrails"])]
            unasserted = [sid for sid in appearances if sid not in asserted]
            if unasserted:
                add("NOTE", "K4_GUARDRAIL_NOT_ASSERTED_ELSEWHERE", [s["shotId"]] + unasserted,
                    "%s asserted on %s only, but subject appears in %d shot(s) of %s; "
                    "other shots do not re-assert it in the ledger (documentation coverage, "
                    "not a picture verdict — the keyframe may still show it)"
                    % (key, s["shotId"], len(appearances), s["sceneId"]),
                    ["Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"])
            guard_rows.append({
                "guardrailKey": key, "originShot": s["shotId"], "sceneId": s["sceneId"],
                "subject": subject or "SCENE_LEVEL",
                "subjectAppearances": appearances,
                "assertedOnShotIds": asserted,
                "unassertedShotIds": unasserted,
            })

    totals = {
        "scenes": len(SCENES),
        "shots": total_shots,
        "durationSeconds": total_duration,
        "dialogueCues": total_cues,
        "dialogueShots": len([s for s in shots if s["dialogue"]]),
        "findings": len(findings),
        "findingsBySeverity": {
            sev: len([f for f in findings if f["severity"] == sev])
            for sev in ("FLAG", "NOTE")},
        "dryShots": len([f for f in findings if f["category"] == "K5_DRY_SHOT"]),
        "characterBlinks": len([f for f in findings if f["category"] == "K3_CHARACTER_BLINK"]),
    }
    ledger_out = {
        "ledgerId": "NGM_CONTINUITY_LEDGER_V1",
        "checkpoint": "MEDIA-02 WO37 M-C CP4 — continuity ledger v1 (63 campaign shots)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrder": "WO37 M-C (continuity), continuing Gói 38 item 4",
        "branch": "muse/media-production-20261104",
        "baseSha": "9ac73dc",
        "headSha": "4c53683",
        "status": "DRAFT",
        "sources": {
            "motionLedger": "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json",
            "motionLedgerSha256": sha256_file(LEDGER),
            "runtimeManifest": "ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json",
            "runtimeManifestSha256": sha256_file(RUNTIME),
            "pronunciationTable": "Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json",
            "pronunciationTableSha256": sha256_file(PRON),
            "timingManifests": "ClientGodot/assets/cinematics/timing/CIN_XXX_timing_v1.json (20 files)",
            "sceneExportManifests": "ClientGodot/assets/cinematics/CIN_XXX/scene_export_manifest_v1.json (20 files)",
            "srtFiles": "ClientGodot/assets/cinematics/timing/CIN_XXX_vi.srt (20 files)",
            "mixManifests": "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3 (P0 scenes) + Art_Source/Audio/Muse/MIX/CINxxx_DRAFT_V1 (17 scenes)",
        },
        "rules": [
            "K1 timing tiling from timing manifests; ledger timing must match; durations must agree across timing/export/mix/runtime; totals 20/63/378/21.",
            "K2 SRT (runtime-manifest sha) must be UTF-8/NFC/LF-only, cue count == export dialogueCues, ordered non-overlapping; one cue per dialogue shot, window inside shot, text == ledger dialogue text.",
            "K3 per scene per named character: visible-shot sequence, BLINK = visible/absent/visible again in one scene; REQUIRED_NOT_VISIBLE; speaker not visible in own dialogue shot is NOTE when onscreen=false (designed off-screen) or the ledger records off-screen staging, otherwise FLAG (no off-screen decision recorded); speaker with no canonical ID is FLAG.",
            "K4 each R5 guardrail key traced across its scene: every shot where the same subject appears should re-assert it; unasserted shots are NOTE (documentation coverage).",
            "K5 per-shot audio coverage from the current mix manifest; DRY_SHOT is FLAG; segment boundary mid-shot and stinger on a shot boundary are NOTE (a stinger belongs to the shot starting at its placement second); ambience loop-seam wrapJump attached from pronunciation seam table.",
            "K6 mix VO take extent vs locked/SRT window, matched by shotId (mix `voices` list, else single `vo`); take end is takeEndSeconds when present, else windowSeconds[1]; a take ending before the locked end is NOTE, an overrun is NOTE with the recorded overrunVsWindowSeconds; a window mismatch is FLAG.",
        ],
        "totals": totals,
        "scenes": scene_rows,
        "shots": shot_rows,
        "characterContinuity": char_rows,
        "guardrailContinuity": guard_rows,
        "findings": findings,
    }
    OUT.write_text(json.dumps(ledger_out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("scenes:", len(scene_rows), "shots:", len(shot_rows))
    print("totals:", totals)
    print("findings:", len(findings))
    for f in findings:
        print(" ", f["id"], f["severity"], f["category"], f["shots"], "|", f["evidence"][:160])


if __name__ == "__main__":
    main()
