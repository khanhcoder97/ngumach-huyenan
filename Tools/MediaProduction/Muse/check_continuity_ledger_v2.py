#!/usr/bin/env python3
"""MEDIA-02 WO37 M-C CP5 — Independent checker for CONTINUITY_LEDGER_v2.json.

Same independent re-derivation as the v1 checker, plus three new
cross-check sections (2b–2d) added for the CP5 source fix: timing-manifest
mirrors byte-identical, motion-ledger dialogue == timing-manifest dialogue
(speaker / canonical ID with the NPC_REFUGEE_LEADER alias / onscreen /
window / text), and aggregate timing-manifest cues == per-scene timing
dialogue. Does NOT import the builder.

Re-derives every check from the original sources (motion ledger, timing
manifests, scene export manifests, SRT files, mix manifests, pronunciation
seam table, runtime manifest) with its own parsing code, then compares
field-by-field against the ledger. Does NOT import the builder.

Usage: python3 check_continuity_ledger_v1.py
Exit 0 when every re-derived value matches the ledger; exit 1 otherwise.
Writes MEDIA02_WO37_MC_CONTINUITY_LEDGER_VALIDATION_20261109.json next to
the ledger report (same directory as this tool's output argument handling
is fixed: the JSON goes to Implementation/Reports/MuseMedia/).
"""
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LEDGER = ROOT / "Implementation/Content/Narrative/Deliveries/MOTION_LEDGER_v1.json"
CONT = ROOT / "Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v2.json"
RUNTIME = ROOT / "ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json"
PRON = ROOT / "Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json"
OUT = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MC_CP5_CONTINUITY_LEDGER_VALIDATION_20261109.json"

TOL = 0.001
SCENES = ["CIN_%03d" % i for i in range(1, 21)]
P0 = {"CIN_001", "CIN_002", "CIN_004"}
GUARDRAIL_SUBJECT = {
    "BROKEN_HORN": "BOSS_MANG_COT",
    "LEFT_BANDAGE": "NPC_TA_VAN_KHANH",
    "SUBJECT_CORE_SERPENT": "BOSS_TIDE_SERPENT",
}

results = []


def check(name, ok, detail=""):
    results.append({"check": name, "pass": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + (" — " + detail if detail else ""))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def srt_cues(path):
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8")
    assert b"\r" not in raw and unicodedata.is_normalized("NFC", text)
    cues = []
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.strip().split("\n")
        m = re.match(r"(\d\d):(\d\d):(\d\d),(\d{3}) --> (\d\d):(\d\d):(\d\d),(\d{3})", lines[1].strip())
        def ts(a, b, c, d):
            return int(a) * 3600 + int(b) * 60 + int(c) + int(d) / 1000.0
        cues.append((ts(*m.groups()[:4]), ts(*m.groups()[4:]), "\n".join(lines[2:]).strip()))
    return cues


def mix_path(scene_id):
    if scene_id in P0:
        return ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json"
    code = scene_id.replace("_", "")
    return ROOT / ("Art_Source/Audio/Muse/MIX/%s_DRAFT_V1/%s_MIX_V1_manifest_v1.json" % (code, code))


def main():
    cont = json.loads(CONT.read_text(encoding="utf-8"))
    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    rt = json.loads(RUNTIME.read_text(encoding="utf-8"))
    pron = json.loads(PRON.read_text(encoding="utf-8"))
    shots = led["shots"]
    by_shot = {s["shotId"]: s for s in shots}
    by_scene = {}
    for s in shots:
        by_scene.setdefault(s["sceneId"], []).append(s)
    for v in by_scene.values():
        v.sort(key=lambda s: s["startSeconds"])
    seam = {(r["cueKey"], r["version"]): r for r in pron["seamTable"]}

    # 1. totals
    check("totals.scenes", cont["totals"]["scenes"] == 20, str(cont["totals"]["scenes"]))
    check("totals.shots", cont["totals"]["shots"] == 63, str(cont["totals"]["shots"]))
    check("totals.duration", abs(cont["totals"]["durationSeconds"] - 378.0) <= TOL,
          str(cont["totals"]["durationSeconds"]))
    check("totals.cues", cont["totals"]["dialogueCues"] == 21, str(cont["totals"]["dialogueCues"]))
    check("totals.findings_count", cont["totals"]["findings"] == len(cont["findings"]),
          "%d vs %d" % (cont["totals"]["findings"], len(cont["findings"])))
    n_flag = len([f for f in cont["findings"] if f["severity"] == "FLAG"])
    n_note = len([f for f in cont["findings"] if f["severity"] == "NOTE"])
    check("totals.severity_counts",
          cont["totals"]["findingsBySeverity"] == {"FLAG": n_flag, "NOTE": n_note},
          "FLAG=%d NOTE=%d" % (n_flag, n_note))

    # 2. source SHAs recorded in the ledger
    check("sources.motionLedgerSha", cont["sources"]["motionLedgerSha256"] == sha(LEDGER))
    check("sources.runtimeManifestSha", cont["sources"]["runtimeManifestSha256"] == sha(RUNTIME))
    check("sources.pronunciationSha", cont["sources"]["pronunciationTableSha256"] == sha(PRON))

    # 2b. CP5: timing-manifest mirrors byte-identical (Deliveries vs runtime)
    for scene_id in SCENES:
        a = ROOT / ("Implementation/Content/Narrative/Deliveries/%s/%s_timing_v1.json" % (scene_id, scene_id))
        b = ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % scene_id)
        check("mirror.%s.timing" % scene_id, a.read_bytes() == b.read_bytes())

    # 2c. CP5: motion-ledger dialogue == timing-manifest dialogue (both mirrors
    # agree by 2b, so compare against the runtime copy). Speaker canonical
    # follows the motion builder's alias map (NPC_REFUGEE_LEADER -> LEAD).
    SPEAKER_ALIASES = {"NPC_REFUGEE_LEADER": "NPC_REFUGEE_LEAD"}
    for s in shots:
        if not s["dialogue"]:
            continue
        timing = json.loads((ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % s["sceneId"])).read_text(encoding="utf-8"))
        td = next(t for t in timing["shots"] if t["shotId"] == s["shotId"])["dialogue"]
        md = s["dialogue"]
        ok = (md["speaker"] == td["speaker"]
              and md["speakerCanonical"] == SPEAKER_ALIASES.get(td["speaker"], td["speaker"])
              and md.get("speakerDisplay") == td.get("speakerDisplay")
              and md.get("onscreen") == td.get("onscreen")
              and md["windowSeconds"] == td["windowSeconds"]
              and md["text"] == td["text"])
        check("dialogue.%s.matchesTiming" % s["shotId"], ok,
              "speaker=%s onscreen=%s" % (md["speaker"], md.get("onscreen")))

    # 2d. CP5: the four CP4 FLAG shots carry their closure record in timing.
    _flag_shots = {
        "CIN_005_S03": {"speaker": "NPC_LYAN", "onscreen": False},
        "CIN_009_S03": {"speaker": "NPC_LYAN", "onscreen": False},
        "CIN_017_S03": {"speaker": "NPC_DIVER_LEAD", "onscreen": False},
        "CIN_020_S03": {"speaker": "LETTER_RECIPIENT", "onscreen": True},
    }
    for sid, want in _flag_shots.items():
        scene_id = sid.rsplit("_", 1)[0]
        timing = json.loads((ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % scene_id)).read_text(encoding="utf-8"))
        td = next(t for t in timing["shots"] if t["shotId"] == sid)["dialogue"]
        note = td.get("stagingNote") or ""
        ok = (td["speaker"] == want["speaker"] and td.get("onscreen") is want["onscreen"]
              and note.startswith("M-C CP5:") and len(note) > 80)
        if sid == "CIN_020_S03":
            ok = ok and td.get("speakerStatus") == "PLACEHOLDER"
        check("flagClosure.%s" % sid, ok,
              "speaker=%s onscreen=%s note=%d chars" % (td["speaker"], td.get("onscreen"), len(note)))

    # 2e. CP5: aggregate timing manifests' cues == per-scene timing dialogue.
    for agg in ("Implementation/Content/Narrative/Deliveries/CAMPAIGN_timing_manifest_v1.json",
                "Implementation/Content/Narrative/Deliveries/P0_timing_manifest_v1.json"):
        ad = json.loads((ROOT / agg).read_text(encoding="utf-8"))
        for sc in ad["scenes"]:
            timing = json.loads((ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % sc["sceneId"])).read_text(encoding="utf-8"))
            for cue in sc.get("cues", []):
                td = next(t for t in timing["shots"] if t["shotId"] == cue["shotId"])["dialogue"]
                ok = (cue["speakerId"] == td["speaker"]
                      and cue.get("speakerDisplay") == td.get("speakerDisplay")
                      and cue["windowSeconds"] == td["windowSeconds"])
                check("aggCue.%s" % cue["shotId"], ok,
                      "speakerId=%s" % cue["speakerId"])

    # 3. per-scene re-derivation
    scene_rows = {r["sceneId"]: r for r in cont["scenes"]}
    shot_rows = {r["shotId"]: r for r in cont["shots"]}
    tot_dur = tot_shots = tot_cues = 0
    for scene_id in SCENES:
        timing = json.loads((ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % scene_id)).read_text(encoding="utf-8"))
        export = json.loads((ROOT / ("ClientGodot/assets/cinematics/%s/scene_export_manifest_v1.json" % scene_id)).read_text(encoding="utf-8"))
        rts = next(s for s in rt["scenes"] if s["sceneId"] == scene_id)
        srtp = ROOT / ("ClientGodot/assets/cinematics/timing/%s_vi.srt" % scene_id)
        cues = srt_cues(srtp)
        mix = json.loads(mix_path(scene_id).read_text(encoding="utf-8"))
        ms = next(s for s in mix["scenes"] if s["sceneId"] == scene_id)
        row = scene_rows[scene_id]
        ts = timing["shots"]
        tiling = (abs(ts[0]["startSeconds"]) <= TOL
                  and all(abs(a["endSeconds"] - b["startSeconds"]) <= TOL for a, b in zip(ts, ts[1:]))
                  and abs(ts[-1]["endSeconds"] - timing["durationSeconds"]) <= TOL
                  and len(ts) == len(by_scene[scene_id]))
        check("scene.%s.tiling" % scene_id, row["tilingOk"] == tiling)
        check("scene.%s.timingSha" % scene_id,
              row["timingShaMatchesRuntimeManifest"] == (sha(ROOT / ("ClientGodot/assets/cinematics/timing/%s_timing_v1.json" % scene_id)) == rts["timingSha256"]))
        check("scene.%s.srtSha" % scene_id,
              row["srtShaMatchesRuntimeManifest"] == (sha(srtp) == rts["srtSha256"]))
        check("scene.%s.cueCount" % scene_id,
              row["srtCueCountMatchesExport"] == (len(cues) == export["dialogueCues"]),
              "%d vs %d" % (len(cues), export["dialogueCues"]))
        ordered = all(cues[i][1] <= cues[i + 1][0] + TOL for i in range(len(cues) - 1))
        check("scene.%s.cuesOrdered" % scene_id, row["srtCuesOrderedNonOverlapping"] == ordered)
        check("scene.%s.durationsAgree" % scene_id,
              row["durationsAgreeAcrossSources"] == (
                  abs(export["durationSeconds"] - timing["durationSeconds"]) <= TOL
                  and abs(ms["seconds"] - timing["durationSeconds"]) <= TOL
                  and rts["durationSeconds"] == timing["durationSeconds"]))
        ledger_timing = all(abs(by_shot[t["shotId"]]["startSeconds"] - t["startSeconds"]) <= TOL
                            and abs(by_shot[t["shotId"]]["endSeconds"] - t["endSeconds"]) <= TOL
                            for t in ts)
        check("scene.%s.ledgerTiming" % scene_id,
              row["ledgerTimingMatchesTimingManifest"] == ledger_timing)
        tot_dur += timing["durationSeconds"]
        tot_shots += len(ts)
        tot_cues += export["dialogueCues"]

        # dialogue shots: SRT cue window + text
        for s in by_scene[scene_id]:
            if not s["dialogue"]:
                continue
            w = s["dialogue"]["windowSeconds"]
            match = [c for c in cues if abs(c[0] - w[0]) <= TOL and abs(c[1] - w[1]) <= TOL]
            ok = len(match) == 1 and match[0][0] >= s["startSeconds"] - TOL \
                and match[0][1] <= s["endSeconds"] + TOL \
                and unicodedata.normalize("NFC", match[0][2]) == unicodedata.normalize("NFC", s["dialogue"]["text"])
            check("dialogue.%s.srtCue" % s["shotId"], ok,
                  "matches=%d" % len(match))

        # per-shot audio roles
        vo_entries = ms.get("voices") or ([ms["vo"]] if ms.get("vo") else [])
        vo_wins = [v["windowSeconds"] for v in vo_entries if v.get("windowSeconds")]
        for s in by_scene[scene_id]:
            a, b = s["startSeconds"], s["endSeconds"]
            roles = set()
            for st in ms.get("stems", []):
                seg = st.get("segmentSceneSeconds")
                if seg and seg[1] - a > TOL and b - seg[0] > TOL:
                    roles.add(st["role"])
                at = st.get("atSeconds")
                if at is not None:
                    starts = [x["startSeconds"] for x in by_scene[scene_id]]
                    if abs(at - a) <= TOL or (a - TOL <= at <= b + TOL
                                              and not any(abs(at - ss) <= TOL for ss in starts)):
                        roles.add(st["role"])
            for vw in vo_wins:
                if vw[1] - a > TOL and b - vw[0] > TOL:
                    roles.add("vo")
            row = shot_rows[s["shotId"]]
            check("audio.%s.roles" % s["shotId"], row["audioRoles"] == sorted(roles),
                  "%s vs %s" % (row["audioRoles"], sorted(roles)))
            check("audio.%s.bounds" % s["shotId"],
                  abs(row["startSeconds"] - a) <= TOL and abs(row["endSeconds"] - b) <= TOL)

    check("totals.durationSum", abs(tot_dur - 378.0) <= TOL, str(tot_dur))
    check("totals.shotSum", tot_shots == 63, str(tot_shots))
    check("totals.cueSum", tot_cues == 21, str(tot_cues))

    # 4. character continuity rows
    char_rows = {(r["character"], r["sceneId"]): r for r in cont["characterContinuity"]}
    for scene_id in SCENES:
        ss = by_scene[scene_id]
        chars = set()
        for s in ss:
            chars.update(s["namedCharactersVisible"])
            chars.update(s["namedCharactersRequired"])
        for ch in sorted(chars):
            vis = [s["shotId"] for s in ss if ch in s["namedCharactersVisible"]]
            req = [s["shotId"] for s in ss if ch in s["namedCharactersRequired"]]
            row = char_rows.get((ch, scene_id))
            ok = row is not None and row["visibleShotIds"] == vis and row["requiredShotIds"] == req
            check("character.%s.%s" % (scene_id, ch), ok, "vis=%d req=%d" % (len(vis), len(req)))

    # 5. guardrail rows
    guard_rows = {(r["guardrailKey"], r["originShot"]): r for r in cont["guardrailContinuity"]}
    for s in shots:
        for g in s["guardrails"]:
            key = g.split(":", 1)[0].strip()
            subject = GUARDRAIL_SUBJECT.get(key)
            ss = by_scene[s["sceneId"]]
            if subject:
                app = [x["shotId"] for x in ss
                       if subject in x["namedCharactersVisible"] or subject in x["namedCharactersRequired"]]
            else:
                app = [x["shotId"] for x in ss]
            asserted = [x["shotId"] for x in ss
                        if any(gr.split(":", 1)[0].strip() == key for gr in x["guardrails"])]
            row = guard_rows.get((key, s["shotId"]))
            ok = row is not None and row["subjectAppearances"] == app \
                and row["assertedOnShotIds"] == asserted \
                and row["unassertedShotIds"] == [i for i in app if i not in asserted]
            check("guardrail.%s.%s" % (key, s["shotId"]), ok,
                  "appear=%d asserted=%d" % (len(app), len(asserted)))

    # 6. findings re-derived as (severity, category, tuple(shots)) multiset
    expected = []
    # K3 speaker flags/notes
    for s in shots:
        if not s["dialogue"]:
            continue
        sp = s["dialogue"]["speaker"]
        if sp is None:
            expected.append(("FLAG", "K3_SPEAKER_NO_ID", (s["shotId"],)))
            continue
        if sp == "PLAYER":
            continue
        if sp not in s["namedCharactersVisible"]:
            if s["dialogue"].get("onscreen") is False:
                expected.append(("NOTE", "K3_SPEAKER_OFFSCREEN_DECIDED", (s["shotId"],)))
            elif s["speakerNotInFrame"] or s["speakerIdentifiabilityDefect"]:
                expected.append(("NOTE", "K3_SPEAKER_OFFSCREEN_STAGING", (s["shotId"],)))
            else:
                expected.append(("FLAG", "K3_SPEAKER_NOT_VISIBLE", (s["shotId"],)))
        # required-not-visible
    for scene_id in SCENES:
        for s in by_scene[scene_id]:
            for ch in s["namedCharactersRequired"]:
                if ch not in s["namedCharactersVisible"]:
                    expected.append(("NOTE", "K3_REQUIRED_NOT_VISIBLE", (s["shotId"],)))
    # K4 guardrail notes
    for (key, origin), row in guard_rows.items():
        if row["unassertedShotIds"]:
            expected.append(("NOTE", "K4_GUARDRAIL_NOT_ASSERTED_ELSEWHERE",
                             tuple([origin] + row["unassertedShotIds"])))
    # K5 stinger boundary + K6 take extent (recomputed from mix manifests)
    for scene_id in SCENES:
        mix = json.loads(mix_path(scene_id).read_text(encoding="utf-8"))
        ms = next(s for s in mix["scenes"] if s["sceneId"] == scene_id)
        ss = by_scene[scene_id]
        bounds = [x["startSeconds"] for x in ss] + [ss[-1]["endSeconds"]]
        for st in ms.get("stems", []):
            at = st.get("atSeconds")
            if at is not None and any(abs(at - bd) <= TOL for bd in bounds):
                owner = next((x["shotId"] for x in ss if abs(at - x["startSeconds"]) <= TOL),
                             next(x["shotId"] for x in ss if x["startSeconds"] - TOL <= at <= x["endSeconds"] + TOL))
                expected.append(("NOTE", "K5_STINGER_AT_SHOT_BOUNDARY", (owner,)))
        vo_entries = ms.get("voices") or ([ms["vo"]] if ms.get("vo") else [])
        for ve in vo_entries:
            sid = ve.get("shotId")
            if not sid:
                dlg = [x for x in ss if x["dialogue"]]
                sid = dlg[0]["shotId"] if len(dlg) == 1 else None
            if not sid or sid not in by_shot:
                continue
            take_end = ve.get("takeEndSeconds", ve["windowSeconds"][1])
            locked_end = by_shot[sid]["dialogue"]["windowSeconds"][1]
            if abs(take_end - locked_end) > TOL:
                expected.append(("NOTE", "K6_VO_TAKE_EXTENT", (sid,)))
    actual = [(f["severity"], f["category"], tuple(f["shots"])) for f in cont["findings"]]
    check("findings.multiset", sorted(actual) == sorted(expected),
          "actual=%d expected=%d" % (len(actual), len(expected)))
    if sorted(actual) != sorted(expected):
        from collections import Counter
        ca, ce = Counter(actual), Counter(expected)
        for item in sorted(set(ca) ^ set(ce)):
            print("  DIFF", item, "actual=%d expected=%d" % (ca.get(item, 0), ce.get(item, 0)))
    check("findings.no_dry_shots",
          cont["totals"]["dryShots"] == 0 and not any(f["category"] == "K5_DRY_SHOT" for f in cont["findings"]))
    check("findings.no_blinks",
          cont["totals"]["characterBlinks"] == 0 and not any(f["category"] == "K3_CHARACTER_BLINK" for f in cont["findings"]))

    n_pass = sum(1 for r in results if r["pass"])
    val = {
        "validatorId": "NGM_CONTINUITY_LEDGER_VALIDATION_V2",
        "checkpoint": "MEDIA-02 WO37 M-C CP5 — continuity ledger v2 (CP4 FLAG closure)",
        "branch": "muse/media-production-20261104",
        "baseSha": "9ac73dc",
        "headSha": "9ab006f",
        "ledgerFile": "Implementation/Content/Narrative/Deliveries/CONTINUITY_LEDGER_v2.json",
        "ledgerSha256": sha(CONT),
        "checksTotal": len(results),
        "checksPassed": n_pass,
        "checksFailed": len(results) - n_pass,
        "verdict": "PASS" if n_pass == len(results) else "FAIL",
        "results": results,
    }
    OUT.write_text(json.dumps(val, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("checks: %d/%d PASS — verdict %s" % (n_pass, len(results), val["verdict"]))
    print("validation JSON:", OUT)
    sys.exit(0 if n_pass == len(results) else 1)


if __name__ == "__main__":
    main()
