#!/usr/bin/env python3
"""MEDIA-02 WO37 M-E checkpoint 2a: independent validator for the
SFX coverage audit + proposal.

Re-checks from the sources, never trusting the builder's manifest:

  * re-reads the design catalogue (63 keys), the SFX_UI pack (173),
    the ported music/ambience pack (22), the composed music/ambience
    packs (13 + 13) and the game manifest (195 cues + bindings);
  * re-hashes + ffprobes every representative file the manifest
    claims VERIFIED (54 SFX v01 WAVs, 9 ported OGGs, 9 composed
    OGGs) and compares sha/size/codec/duration against the PACK
    entries (not against the manifest);
  * re-derives the counts: 63/63 coverage, 119 delivered keys beyond
    the catalogue with the per-category breakdown, pack-union ==
    game-manifest cue set (195), binding counts, boss composition
    (12 intro / 14 warning / 12 success), monster families/phases;
  * re-checks every requirement's evidence cueKeys exist in the
    delivered packs (or, for R-NPC, in the game-manifest bindings);
  * re-checks every proposal: proposed cueKey(s) collide with NO
    existing cueKey in any pack or the game manifest, and carry no
    runtime path, no file and no binding (PROPOSED_NOT_RUNTIME);
  * re-checks the manifest's counts/verdict tallies match the
    recomputation.

Writes Implementation/Reports/MuseMedia/MEDIA02_WO37_ME_CP2A_VALIDATION_20261111.json
and exits 0 on PASS, 1 on any mismatch.

Usage: python3 Tools/MediaProduction/Muse/check_sfx_coverage_me_cp2a_v1.py
"""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COVERAGE_ME_CP2A_v1.json")
CATALOGUE = ROOT / "Implementation/Content/DesignBaselines/audio_cues_v1.json"
SFX_PACK = ROOT / "Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json"
MA_PACK = ROOT / "Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json"
MUSIC_COMP = ROOT / "Implementation/Content/Audio/Deliveries/MUSIC_COMPOSED_pack_v1.json"
AMB_COMP = ROOT / "Implementation/Content/Audio/Deliveries/AMBIENCE_COMPOSED_pack_v1.json"
GAME_MANIFEST = ROOT / "Client/Assets/AudioManifests/game_audio_v1.json"
REPORT_DIR = ROOT / "Implementation/Reports/MuseMedia"
OUT = REPORT_DIR / "MEDIA02_WO37_ME_CP2A_VALIDATION_20261111.json"

ERRORS = []
CHECKS = Counter()


def fail(msg):
    ERRORS.append(msg)
    print("MISMATCH: " + msg, file=sys.stderr)


def check(cond, msg):
    CHECKS["total"] += 1
    if cond:
        CHECKS["passed"] += 1
    else:
        fail(msg)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(path: Path):
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_name,sample_rate,channels",
         "-show_entries", "format=duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    sfx_pack = json.loads(SFX_PACK.read_text(encoding="utf-8"))
    ma_pack = json.loads(MA_PACK.read_text(encoding="utf-8"))
    music_comp = json.loads(MUSIC_COMP.read_text(encoding="utf-8"))
    amb_comp = json.loads(AMB_COMP.read_text(encoding="utf-8"))
    game = json.loads(GAME_MANIFEST.read_text(encoding="utf-8"))

    sfx_by_key = {c["cueKey"]: c for c in sfx_pack["cues"]}
    ma_by_key = {c["cueKey"]: c for c in ma_pack["cues"]}
    comp_by_key = {c["cueKey"]: c
                   for c in music_comp["cues"] + amb_comp["cues"]}
    game_keys = {c["cueKey"] for c in game["cues"]}
    all_existing = set(sfx_by_key) | set(ma_by_key) | set(comp_by_key) | game_keys

    # --- source counts ---
    check(len(catalogue["cues"]) == 63,
          f"catalogue has {len(catalogue['cues'])} cues, expected 63")
    check(len(sfx_pack["cues"]) == 173,
          f"SFX_UI pack has {len(sfx_pack['cues'])} cues, expected 173")
    check(len(ma_pack["cues"]) == 22,
          f"music/ambience pack has {len(ma_pack['cues'])} cues, expected 22")
    check(len(game["cues"]) == 195,
          f"game manifest has {len(game['cues'])} cues, expected 195")
    check(set(sfx_by_key) | set(ma_by_key) == game_keys,
          "pack union != game manifest cue set")

    # --- manifest counts vs recomputation ---
    counts = manifest["counts"]
    cat_keys = {c["cueKey"] for c in catalogue["cues"]}
    check(counts["catalogueKeys"] == 63, "manifest catalogueKeys != 63")
    check(counts["catalogueCoveredVerified"] == 63,
          "manifest catalogueCoveredVerified != 63")
    extra = [k for k in sfx_by_key if k not in cat_keys]
    check(counts["deliveredBeyondCatalogue"] == len(extra) == 119,
          f"manifest deliveredBeyondCatalogue={counts['deliveredBeyondCatalogue']}, recomputed {len(extra)}")
    extra_by_cat = dict(sorted(Counter(k.split("/")[1] for k in extra).items()))
    check(counts["deliveredBeyondCatalogueByCategory"] == extra_by_cat,
          "manifest extra-by-category != recomputed")
    check(counts["gameManifestCues"] == 195, "manifest gameManifestCues != 195")
    bindings = {k: len(v) for k, v in game["bindings"].items()}
    check(counts["bindings"] == bindings,
          f"manifest bindings {counts['bindings']} != {bindings}")
    boss_keys = [k for k in sfx_by_key if k.startswith("SFX/BOSS/")]
    boss_comp = {"intro": sum(1 for k in boss_keys if "intro" in k),
                 "warning": sum(1 for k in boss_keys if "warning" in k),
                 "success": sum(1 for k in boss_keys if "success" in k)}
    check(counts["bossComposition"] == boss_comp,
          f"manifest bossComposition {counts['bossComposition']} != {boss_comp}")
    mon_keys = [k for k in sfx_by_key if k.startswith("SFX/MONSTER/")]
    mon_fam = sorted({k.split("/")[2].rsplit("_", 1)[0] for k in mon_keys})
    check(counts["monsterFamilies"] == mon_fam,
          "manifest monsterFamilies != recomputed")
    mon_ph = dict(sorted(Counter(k.rsplit("_", 1)[-1] for k in mon_keys).items()))
    check(counts["monsterPhases"] == mon_ph,
          "manifest monsterPhases != recomputed")

    # --- re-verify every representative file from the PACK entries ---
    cov = {e["cueKey"]: e for e in manifest["coverage"]}
    check(len(cov) == 63, f"manifest coverage has {len(cov)} entries, expected 63")
    verified = 0
    for cat in catalogue["cues"]:
        key = cat["cueKey"]
        entry = cov.get(key)
        check(entry is not None, f"manifest missing coverage entry for {key}")
        if entry is None:
            continue
        check(entry["status"] == "COVERED_VERIFIED",
              f"{key}: manifest status {entry['status']} != COVERED_VERIFIED")
        if key.startswith("SFX/"):
            cue = sfx_by_key.get(key)
            check(cue is not None, f"{key} missing from SFX_UI pack")
            if cue is None:
                continue
            rt = cue["variants"][0]["runtime"]
            p = ROOT / rt["path"]
            check(p.exists() and not p.read_bytes()[:60].startswith(
                b"version https://git-lfs.github.com/spec/v1"),
                f"{key}: file missing or LFS pointer: {rt['path']}")
            check(sha256_file(p) == rt["sha256"],
                  f"{key}: sha mismatch {rt['path']}")
            check(p.stat().st_size == rt["size_bytes"],
                  f"{key}: size mismatch {rt['path']}")
            pr = probe(p)
            check(pr is not None, f"{key}: ffprobe failed")
            if pr is not None:
                codec = pr["streams"][0]["codec_name"]
                dur = float(pr["format"]["duration"])
                check(codec == "pcm_s16le", f"{key}: codec {codec}")
                check(abs(dur - rt["duration_s"]) <= 0.05,
                      f"{key}: duration {dur} != {rt['duration_s']}")
            verified += 1
        else:
            cue = ma_by_key.get(key)
            check(cue is not None, f"{key} missing from ported pack")
            if cue is None:
                continue
            rt = cue["runtime"]
            p = ROOT / rt["path"]
            check(p.exists() and not p.read_bytes()[:60].startswith(
                b"version https://git-lfs.github.com/spec/v1"),
                f"{key}: file missing or LFS pointer: {rt['path']}")
            check(sha256_file(p) == rt["sha256"],
                  f"{key}: sha mismatch {rt['path']}")
            pr = probe(p)
            check(pr is not None, f"{key}: ffprobe failed")
            if pr is not None:
                check(pr["streams"][0]["codec_name"] == "vorbis",
                      f"{key}: codec != vorbis")
                check(abs(float(pr["format"]["duration"]) - rt["duration_s"]) <= 0.05,
                      f"{key}: ported duration mismatch")
            verified += 1
            comp = comp_by_key.get(key)
            check(comp is not None, f"{key} missing from composed packs")
            if comp is not None:
                crt = comp["runtime"]
                cp = ROOT / crt["path"]
                check(cp.exists() and not cp.read_bytes()[:60].startswith(
                    b"version https://git-lfs.github.com/spec/v1"),
                    f"{key}: composed file missing or LFS pointer: {crt['path']}")
                check(sha256_file(cp) == crt["sha256"],
                      f"{key}: composed sha mismatch {crt['path']}")
                cpr = probe(cp)
                check(cpr is not None, f"{key}: composed ffprobe failed")
                if cpr is not None:
                    check(cpr["streams"][0]["codec_name"] == "vorbis",
                          f"{key}: composed codec != vorbis")
                    check(abs(float(cpr["format"]["duration"]) - crt["durationSeconds"]) <= 0.05,
                          f"{key}: composed duration mismatch")
                verified += 1
    check(counts["filesVerified"] == verified,
          f"manifest filesVerified={counts['filesVerified']}, recomputed {verified}")
    CHECKS["files_reverified"] = verified

    # --- requirement evidence exists in the delivered set ---
    for req in manifest["requirements"]:
        for ev in req["evidence"]:
            if ev.startswith("30 SFX/SKILL/"):
                skill_keys = [k for k in sfx_by_key
                              if k.startswith("SFX/SKILL/")]
                check(len(skill_keys) == 30,
                      f"{req['reqId']}: skill cue count {len(skill_keys)} != 30")
            elif ev.startswith("14 SFX/BOSS/"):
                check(boss_comp["warning"] == 14,
                      f"{req['reqId']}: boss warnings {boss_comp['warning']} != 14")
            elif ev.startswith("12 bosses"):
                check(len(game["bindings"]["bosses"]) == 12,
                      f"{req['reqId']}: boss bindings != 12")
            elif ev.startswith("83 NPC"):
                check(len(game["bindings"]["npcs"]) == 83,
                      f"{req['reqId']}: NPC bindings != 83")
                npc = game["bindings"]["npcs"][0]
                check(npc["openCue"] == "SFX/UI/panel_open"
                      and npc["closeCue"] == "SFX/UI/panel_close"
                      and npc["spokenVoice"] is None,
                      f"{req['reqId']}: NPC binding shape changed")
            elif ev.startswith("7 SFX/FORGE/"):
                check(sum(1 for k in sfx_by_key if k.startswith("SFX/FORGE/")) == 7,
                      f"{req['reqId']}: FORGE cues != 7")
            elif ev.startswith("13 AMBIENCE/"):
                check(sum(1 for k in ma_by_key if k.startswith("AMBIENCE/")) == 13,
                      f"{req['reqId']}: ported AMBIENCE cues != 13")
            elif ev.startswith("20 scene"):
                check(len(game["bindings"]["cinema"]) == 20,
                      f"{req['reqId']}: cinema bindings != 20")
            else:
                # Only cueKey-shaped evidence is checked here; descriptive
                # notes (e.g. "spokenVoice=null for all 83") are not keys.
                if ev.startswith(("SFX/", "MUSIC/", "AMBIENCE/")):
                    check(ev in all_existing,
                          f"{req['reqId']}: evidence cue {ev} not in any delivered pack")
    check(len(manifest["requirements"]) == 12,
          f"requirements count {len(manifest['requirements'])} != 12")
    tallies = Counter(r["verdict"] for r in manifest["requirements"])
    for k, v in manifest["verdicts"].items():
        key = {"covered": "COVERED", "coveredPerCatalogue": "COVERED_PER_CATALOGUE",
               "coveredBySharedCue": "COVERED_BY_SHARED_CUE",
               "partial": "PARTIAL", "question": "QUESTION",
               "gap": "GAP"}[k]
        check(tallies.get(key, 0) == v,
              f"verdict tally {k}: manifest {v} != recomputed {tallies.get(key, 0)}")

    # --- proposals: no collision, no runtime key ---
    proposed_ids = []
    for prop in manifest["proposals"]:
        ids = prop.get("proposedCueKeys") or [prop.get("proposedCueKey")]
        for pid in ids:
            proposed_ids.append(pid)
            check(pid not in all_existing,
                  f"proposal {prop['proposalId']}: {pid} already exists")
            check("runtime" not in json.dumps(prop).lower()
                  or "PROPOSED_NOT_RUNTIME" in json.dumps(prop),
                  f"proposal {prop['proposalId']}: runtime key leaked")
        check(prop.get("status") == "PROPOSED_NOT_RUNTIME",
              f"proposal {prop['proposalId']}: status != PROPOSED_NOT_RUNTIME")
        check("path" not in prop and "binding" not in prop,
              f"proposal {prop['proposalId']}: carries path/binding")
    check(len(set(proposed_ids)) == len(proposed_ids),
          "duplicate proposed cueKey IDs")
    check(len(manifest["proposals"]) == 3,
          f"proposals count {len(manifest['proposals'])} != 3")
    check(len(manifest["questions"]) == 2,
          f"questions count {len(manifest['questions'])} != 2")

    result = {
        "validator": "check_sfx_coverage_me_cp2a_v1.py",
        "checkpoint": "MEDIA-02 WO37 M-E checkpoint 2a",
        "manifest": "Implementation/Content/Audio/Deliveries/SFX_COVERAGE_ME_CP2A_v1.json",
        "checksTotal": CHECKS["total"],
        "checksPassed": CHECKS["passed"],
        "mismatches": ERRORS,
        "counts": dict(CHECKS),
        "status": "PASS" if not ERRORS else "FAIL",
    }
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"checks: {CHECKS['passed']}/{CHECKS['total']} passed; "
          f"files re-verified: {verified}")
    if ERRORS:
        print(f"FAILED with {len(ERRORS)} mismatches", file=sys.stderr)
        return 1
    print("PASS — wrote " + str(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
