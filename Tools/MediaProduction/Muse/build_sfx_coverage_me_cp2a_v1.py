#!/usr/bin/env python3
"""MEDIA-02 WO37 M-E checkpoint 2a: SFX coverage audit + proposal.

Audits the delivered SFX/UI + music/ambience packs against two
requirement baselines, all from real bytes on disk:

  * the Codex-owned design catalogue
    Implementation/Content/DesignBaselines/audio_cues_v1.json
    (63 soundKeys: 54 SFX + 5 AMBIENCE + 4 MUSIC), and
  * the WO37 M-E requirement phrases (Work Order 37, module M-E):
    footstep materials, 5 weapon / 30 skill cast-impact-miss,
    guard-counter, boss warning, loot/equip/consume/inventory-full,
    quest / NPC / craft / forge / market / water / weather / cinema.

For every one of the 63 catalogue keys the builder verifies a real
representative file on disk (never a pack number alone):
  * SFX keys: variants[0] runtime WAV from SFX_UI_pack_v1.json
    (sha256 + size + ffprobe codec/duration vs the pack entry).
  * MUSIC/AMBIENCE keys: the ported runtime OGG from
    MUSIC_AMBIENCE_pack_v1.json AND the composed runtime OGG from
    MUSIC_COMPOSED_pack_v1.json / AMBIENCE_COMPOSED_pack_v1.json
    (sha256 + ffprobe codec/duration vs each pack entry).

An LFS pointer file fails the sha check instead of producing a
number. This checkpoint renders NO new audio and changes NO runtime
file: its deliverable is the coverage manifest + the proposal table
(proposed cueKey IDs only, flagged PROPOSED_NOT_RUNTIME, no runtime
key is introduced, no cue is composed). Composing the proposed cues
is M-E CP2 proper and still awaits the Codex decision.

Writes Implementation/Content/Audio/Deliveries/SFX_COVERAGE_ME_CP2A_v1.json
and exits non-zero on any mismatch.

Usage: python3 Tools/MediaProduction/Muse/build_sfx_coverage_me_cp2a_v1.py
"""
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CATALOGUE = ROOT / "Implementation/Content/DesignBaselines/audio_cues_v1.json"
SFX_PACK = ROOT / "Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json"
MA_PACK = ROOT / "Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json"
MUSIC_COMP = ROOT / "Implementation/Content/Audio/Deliveries/MUSIC_COMPOSED_pack_v1.json"
AMB_COMP = ROOT / "Implementation/Content/Audio/Deliveries/AMBIENCE_COMPOSED_pack_v1.json"
GAME_MANIFEST = ROOT / "Client/Assets/AudioManifests/game_audio_v1.json"
OUT = ROOT / "Implementation/Content/Audio/Deliveries/SFX_COVERAGE_ME_CP2A_v1.json"

ERRORS = []
CHECKS = Counter()


def fail(msg):
    ERRORS.append(msg)
    print("MISMATCH: " + msg, file=sys.stderr)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def is_lfs_pointer(p: Path) -> bool:
    try:
        head = p.read_bytes()[:200]
    except OSError:
        return False
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


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


def verify_file(rel_path, expect_sha, expect_size, expect_dur,
                expect_codec, label):
    """Verify one representative file from real bytes. Returns a dict."""
    p = ROOT / rel_path
    CHECKS["files_checked"] += 1
    if not p.exists():
        fail(f"{label}: missing file {rel_path}")
        return {"cueKey": label, "path": rel_path, "status": "MISSING_FILE"}
    if is_lfs_pointer(p):
        fail(f"{label}: LFS pointer, not real bytes: {rel_path}")
        return {"cueKey": label, "path": rel_path, "status": "LFS_POINTER"}
    got_sha = sha256_file(p)
    got_size = p.stat().st_size
    if got_sha != expect_sha:
        fail(f"{label}: sha mismatch {rel_path} "
             f"disk {got_sha[:12]} != pack {expect_sha[:12]}")
    if expect_size is not None and got_size != expect_size:
        fail(f"{label}: size mismatch {rel_path} "
             f"disk {got_size} != pack {expect_size}")
    pr = probe(p)
    if pr is None:
        fail(f"{label}: ffprobe failed {rel_path}")
        return {"cueKey": label, "path": rel_path, "status": "PROBE_FAILED",
                "sha256": got_sha, "sizeBytes": got_size}
    streams = pr.get("streams", [])
    codec = streams[0].get("codec_name") if streams else None
    if codec != expect_codec:
        fail(f"{label}: codec {codec} != {expect_codec} ({rel_path})")
    dur = float(pr.get("format", {}).get("duration", -1))
    if expect_dur is not None and abs(dur - expect_dur) > 0.05:
        fail(f"{label}: duration {dur} != {expect_dur} ({rel_path})")
    CHECKS["files_verified"] += 1
    return {"cueKey": label, "path": rel_path, "status": "VERIFIED",
            "sha256": got_sha, "sizeBytes": got_size,
            "codec": codec, "duration_s": round(dur, 4)}


def main():
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

    # Cross-check: delivered packs must equal the game manifest cue set.
    union_keys = set(sfx_by_key) | set(ma_by_key)
    if union_keys != game_keys:
        fail(f"pack union {len(union_keys)} != game manifest {len(game_keys)}: "
             f"only-in-packs={sorted(union_keys - game_keys)[:5]} "
             f"only-in-manifest={sorted(game_keys - union_keys)[:5]}")
    CHECKS["union_vs_game_manifest"] = 1 if union_keys == game_keys else 0

    coverage = []
    for cat in catalogue["cues"]:
        key = cat["cueKey"]
        entry = {"cueKey": key,
                 "catalogueTrigger": cat.get("triggerSemantic"),
                 "catalogueSkillId": cat.get("skillId"),
                 "catalogueClassId": cat.get("classId")}
        if key.startswith("SFX/"):
            cue = sfx_by_key.get(key)
            if cue is None:
                fail(f"catalogue SFX key missing from SFX_UI pack: {key}")
                entry["status"] = "MISSING_FROM_PACK"
                coverage.append(entry)
                continue
            v0 = cue["variants"][0]
            rt = v0["runtime"]
            entry["pack"] = "SFX_UI_pack_v1"
            entry["variants"] = len(cue["variants"])
            entry["verifiedFile"] = verify_file(
                rt["path"], rt["sha256"], rt["size_bytes"],
                rt["duration_s"], "pcm_s16le", key)
            entry["status"] = ("COVERED_VERIFIED"
                               if entry["verifiedFile"]["status"] == "VERIFIED"
                               else "COVERAGE_UNVERIFIED")
        else:
            cue = ma_by_key.get(key)
            if cue is None:
                fail(f"catalogue music/ambience key missing from ported pack: {key}")
                entry["status"] = "MISSING_FROM_PACK"
                coverage.append(entry)
                continue
            rt = cue["runtime"]
            entry["pack"] = "MUSIC_AMBIENCE_pack_v1"
            entry["verifiedFile"] = verify_file(
                rt["path"], rt["sha256"], rt["size_bytes"],
                rt["duration_s"], "vorbis", key)
            comp = comp_by_key.get(key)
            if comp is None:
                fail(f"catalogue key missing from composed packs: {key}")
                entry["composed"] = None
            else:
                crt = comp["runtime"]
                entry["composed"] = verify_file(
                    crt["path"], crt["sha256"], crt["sizeBytes"],
                    crt["durationSeconds"], "vorbis", key + " [composed]")
            entry["status"] = ("COVERED_VERIFIED"
                               if entry["verifiedFile"]["status"] == "VERIFIED"
                               else "COVERAGE_UNVERIFIED")
        coverage.append(entry)

    covered = sum(1 for e in coverage if e["status"] == "COVERED_VERIFIED")
    CHECKS["catalogue_keys"] = len(coverage)
    CHECKS["catalogue_covered_verified"] = covered

    # Delivered expansion beyond the catalogue, grouped by category.
    cat_keys = {c["cueKey"] for c in catalogue["cues"]}
    extra = [k for k in sfx_by_key if k not in cat_keys]
    extra_by_cat = Counter(k.split("/")[1] for k in extra)
    CHECKS["delivered_beyond_catalogue"] = len(extra)

    # Binding counts from the game manifest (source of truth for IDs).
    bindings = {k: len(v) for k, v in game["bindings"].items()}

    # BOSS composition: intro / warning / success.
    boss_keys = [k for k in sfx_by_key if k.startswith("SFX/BOSS/")]
    boss_comp = {"intro": sum(1 for k in boss_keys if "intro" in k),
                 "warning": sum(1 for k in boss_keys if "warning" in k),
                 "success": sum(1 for k in boss_keys if "success" in k)}
    mon_keys = [k for k in sfx_by_key if k.startswith("SFX/MONSTER/")]
    mon_families = sorted({k.split("/")[2].rsplit("_", 1)[0]
                           for k in mon_keys})
    mon_phases = Counter(k.rsplit("_", 1)[-1] for k in mon_keys)

    requirements = [
        {
            "reqId": "R-FOOTSTEP",
            "wo37Phrase": "vật liệu bước chân",
            "verdict": "COVERED",
            "evidence": ["SFX/WORLD/step_stone", "SFX/WORLD/step_wood",
                         "SFX/WORLD/step_mud", "SFX/WORLD/water_splash",
                         "SFX/WORLD/mount_step"],
            "note": "Catalogue defines exactly 3 footstep materials "
                    "(stone/wood/mud) + shallow-water contact; all 5 "
                    "delivered and byte-verified. Grass has no cue in "
                    "catalogue or delivered set — see question Q-GRASS.",
        },
        {
            "reqId": "R-WEAPON",
            "wo37Phrase": "5 weapon",
            "verdict": "QUESTION",
            "evidence": ["SFX/COMBAT/basic_blade"],
            "note": "Catalogue defines ONE shared weapon cue "
                    "(basic_blade, BASIC_SWING_CONFIRMED); all 5 class "
                    "weapons (sword/đao/brush/mace/bow) share it. "
                    "Whether WO37 '5 weapon' means per-weapon swings "
                    "needs a Codex sound-direction decision — see "
                    "proposal P-WEAPON (candidate IDs only, no audio).",
        },
        {
            "reqId": "R-SKILL-PHASE",
            "wo37Phrase": "30 skill cast-impact-miss",
            "verdict": "COVERED_PER_CATALOGUE",
            "evidence": ["30 SFX/SKILL/* cues, 1 per skillId SK-MK/AD/HB/TC/LC-01..06",
                         "SFX/COMBAT/miss", "SFX/COMBAT/projectile_hit",
                         "SFX/COMBAT/heavy_hit"],
            "note": "Catalogue design is 1 cue per skill at its confirm "
                    "semantic + shared combat impact/miss cues "
                    "(direction doc §2: skill soundKey is the semantic "
                    "reference; impact only from confirmed events). "
                    "Per-skill cast+impact+miss triples would be +60 "
                    "cues and contradict the catalogue — see question "
                    "Q-PHASES. No IDs proposed for that reading.",
        },
        {
            "reqId": "R-GUARD",
            "wo37Phrase": "guard-counter",
            "verdict": "PARTIAL",
            "evidence": ["SFX/SKILL/metal_parry"],
            "note": "Counter COVERED (metal_parry, SK-MK-01, "
                    "COUNTER_CONFIRMED). Guard-expire is a GAP: "
                    "direction doc §2 says guard gets a small "
                    "transition sound 'nếu sau này bổ sung cue' and "
                    "'Cửa guard hết mà không bị đánh không có tiếng đỡ "
                    "chuẩn'. See proposal P-GUARD.",
        },
        {
            "reqId": "R-BOSS-WARN",
            "wo37Phrase": "boss warning",
            "verdict": "COVERED",
            "evidence": ["14 SFX/BOSS/*_warning cues",
                         "12 bosses with intro/warning/success bindings"],
            "note": "12 intro + 14 warning + 12 success = 38 BOSS cues. "
                    "The 3 Mãng Cốt warnings (sweep/emerge/bubble) match "
                    "direction doc §4 telegraphs with distinct semantics.",
        },
        {
            "reqId": "R-LOOT",
            "wo37Phrase": "loot/equip/consume/inventory-full",
            "verdict": "COVERED",
            "evidence": ["SFX/UI/item_pickup_common",
                         "SFX/UI/item_pickup_rare",
                         "SFX/UI/item_pickup_legendary",
                         "SFX/UI/item_equip", "SFX/COSMETIC/equip",
                         "SFX/UI/potion_use", "SFX/UI/inventory_full"],
            "note": "All four moments have cues; pickup tiers are "
                    "separate cues, not one cue with pitch shifts.",
        },
        {
            "reqId": "R-QUEST",
            "wo37Phrase": "quest",
            "verdict": "COVERED",
            "evidence": ["SFX/QUEST/discovery", "SFX/QUEST/completed",
                         "SFX/QUEST/accepted", "SFX/QUEST/journal_update"],
            "note": "Plus SFX/TRADE/request for the quest-adjacent "
                    "request moment.",
        },
        {
            "reqId": "R-NPC",
            "wo37Phrase": "NPC",
            "verdict": "COVERED_BY_SHARED_CUE",
            "evidence": ["83 NPC IDs bind openCue=SFX/UI/panel_open, "
                         "closeCue=SFX/UI/panel_close",
                         "spokenVoice=null for all 83"],
            "note": "NPC service open/close is a shared UI cue by "
                    "design (delivery doc §1: '83 ID có cue mở/đóng "
                    "dịch vụ'). Spoken NPC dialogue is a scope "
                    "exclusion in game_audio_v1.json and is NOT "
                    "proposed here.",
        },
        {
            "reqId": "R-CRAFT-FORGE",
            "wo37Phrase": "craft/forge",
            "verdict": "COVERED",
            "evidence": ["SFX/CRAFT/material_combine",
                         "SFX/CRAFT/recipe_unlock",
                         "7 SFX/FORGE/* cues"],
            "note": "Forge: hammer_work, heat_ember, upgrade_success, "
                    "upgrade_fail, socket_success, repair, salvage.",
        },
        {
            "reqId": "R-MARKET",
            "wo37Phrase": "market",
            "verdict": "COVERED",
            "evidence": ["SFX/TRADE/request", "SFX/TRADE/offer_locked",
                         "SFX/TRADE/complete", "SFX/TRADE/buy",
                         "SFX/TRADE/sell"],
            "note": "Market moments use the TRADE cue family.",
        },
        {
            "reqId": "R-WATER-WEATHER",
            "wo37Phrase": "water/weather",
            "verdict": "COVERED",
            "evidence": ["SFX/WORLD/water_splash", "SFX/SKILL/water_step",
                         "SFX/SKILL/water_glass", "SFX/SKILL/water_rain_soft",
                         "13 AMBIENCE/* cues incl. rain_light/rain_heavy"],
            "note": "Weather is carried by the ambience beds "
                    "(LOCAL_WEATHER_RAIN_ACTIVE etc.), not by one-shots.",
        },
        {
            "reqId": "R-CINEMA",
            "wo37Phrase": "cinema",
            "verdict": "COVERED",
            "evidence": ["SFX/CINEMA/reveal", "SFX/CINEMA/tension",
                         "SFX/CINEMA/resolve", "SFX/CINEMA/transition",
                         "20 scene stinger bindings"],
            "note": "Cinema stingers are presentation-only until "
                    "picture lock (binding state in game manifest).",
        },
    ]

    proposals = [
        {
            "proposalId": "P-GUARD",
            "kind": "GAP",
            "proposedCueKey": "SFX/COMBAT/guard_expire",
            "proposedTriggerSemantic": "GUARD_WINDOW_EXPIRED_UNHIT",
            "status": "PROPOSED_NOT_RUNTIME",
            "source": "docs/production/Audio_Production_Direction_v1_vi.md §2",
            "rationale": "Direction doc names this cue as a future "
                         "addition: guard window expiring without a hit "
                         "has no standard block sound today; metal_parry "
                         "plays only on counter confirmed and must NOT "
                         "cover this moment.",
            "decisionNeededFrom": "Codex (sound direction)",
        },
        {
            "proposalId": "P-WEAPON",
            "kind": "QUESTION",
            "proposedCueKeys": ["SFX/COMBAT/dao_swing",
                                "SFX/COMBAT/brush_stroke",
                                "SFX/COMBAT/mace_swing",
                                "SFX/COMBAT/bow_string"],
            "status": "PROPOSED_NOT_RUNTIME",
            "source": "WO37 M-E '5 weapon' vs catalogue (1 shared cue)",
            "rationale": "Candidate IDs IF Codex wants per-weapon basic "
                         "swings; basic_blade stays the shared default. "
                         "Direction doc §1 gives per-class material "
                         "identity (dry metal / wind+ember / brush on "
                         "paper / stone+wood / string+leaf) that such "
                         "cues would follow. No audio composed here.",
            "decisionNeededFrom": "Codex (sound direction)",
        },
        {
            "proposalId": "P-GRASS",
            "kind": "QUESTION",
            "proposedCueKey": "SFX/WORLD/step_grass",
            "status": "PROPOSED_NOT_RUNTIME",
            "source": "WO37 M-E 'vật liệu bước chân' vs production map "
                      "(Bến Mưa grass terrain)",
            "rationale": "Catalogue defines stone/wood/mud only; the "
                         "production map has grass fields, so walking on "
                         "grass has no footstep cue today. Whether grass "
                         "needs one is a design decision, not an audit "
                         "verdict.",
            "decisionNeededFrom": "Codex (sound direction)",
        },
    ]
    questions = [
        {
            "questionId": "Q-PHASES",
            "question": "Does WO37 '30 skill cast-impact-miss' mean "
                        "1 cue per skill (current catalogue design: 30 "
                        "cues at confirm semantics + shared COMBAT "
                        "miss/impact cues) or 3 phases per skill "
                        "(cast + impact + miss = +60 cues)?",
            "askedTo": "Codex",
            "note": "No IDs proposed for the triples reading: inventing "
                    "60 IDs before the reading is decided would be "
                    "scope fabrication.",
        },
        {
            "questionId": "Q-GRASS",
            "question": "Does grass terrain need its own footstep cue "
                        "(proposed SFX/WORLD/step_grass), or do grass "
                        "steps stay silent / reuse mud?",
            "askedTo": "Codex",
            "proposalRef": "P-GRASS",
        },
    ]

    manifest = {
        "coverageId": "NGM_SFX_COVERAGE_ME_CP2A_V1",
        "checkpoint": "MEDIA-02 WO37 M-E checkpoint 2a",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrder": "37_MUSE_FULL_CAMPAIGN_MEDIA_20261108.md module M-E",
        "branch": "muse/media-production-20261104",
        "sources": {
            "catalogue": "Implementation/Content/DesignBaselines/audio_cues_v1.json",
            "catalogueBundle": catalogue.get("bundleId"),
            "catalogueOwner": catalogue.get("owner"),
            "sfxPack": "Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json",
            "sfxPackId": sfx_pack.get("packId"),
            "musicAmbiencePack": "Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json",
            "musicAmbiencePackId": ma_pack.get("packId"),
            "musicComposedPack": "Implementation/Content/Audio/Deliveries/MUSIC_COMPOSED_pack_v1.json",
            "ambienceComposedPack": "Implementation/Content/Audio/Deliveries/AMBIENCE_COMPOSED_pack_v1.json",
            "gameManifest": "Client/Assets/AudioManifests/game_audio_v1.json",
            "gamePackId": game.get("packId"),
            "workOrder37": "Implementation/Work_Orders/37_MUSE_FULL_CAMPAIGN_MEDIA_20261108.md",
            "audioDirection": "docs/production/Audio_Production_Direction_v1_vi.md",
            "audioDelivery": "docs/production/Audio_Pack_V1_Delivery_vi.md",
        },
        "counts": {
            "catalogueKeys": len(coverage),
            "catalogueCoveredVerified": covered,
            "catalogueSfxKeys": sum(1 for e in coverage
                                    if e["cueKey"].startswith("SFX/")),
            "catalogueMusicAmbienceKeys": sum(1 for e in coverage
                                              if not e["cueKey"].startswith("SFX/")),
            "deliveredSfxUiCues": len(sfx_by_key),
            "deliveredMusicAmbienceCues": len(ma_by_key),
            "deliveredBeyondCatalogue": len(extra),
            "deliveredBeyondCatalogueByCategory": dict(sorted(extra_by_cat.items())),
            "gameManifestCues": len(game_keys),
            "bindings": bindings,
            "bossComposition": dict(boss_comp),
            "monsterFamilies": mon_families,
            "monsterPhases": dict(sorted(mon_phases.items())),
            "filesVerified": CHECKS["files_verified"],
        },
        "coverage": coverage,
        "requirements": requirements,
        "proposals": proposals,
        "questions": questions,
        "verdicts": {
            "covered": sum(1 for r in requirements if r["verdict"] == "COVERED"),
            "coveredPerCatalogue": sum(1 for r in requirements if r["verdict"] == "COVERED_PER_CATALOGUE"),
            "coveredBySharedCue": sum(1 for r in requirements if r["verdict"] == "COVERED_BY_SHARED_CUE"),
            "partial": sum(1 for r in requirements if r["verdict"] == "PARTIAL"),
            "question": sum(1 for r in requirements if r["verdict"] == "QUESTION"),
            "gap": sum(1 for r in requirements
                       if r["verdict"] == "GAP"),
        },
        "verification": dict(CHECKS),
        "notes": [
            "No new audio was rendered in this checkpoint; runtime audio "
            "stays 783 files (composed 162, ported 541 unchanged, "
            "plus mixes/VO as before). No runtime file was modified.",
            "Proposals are cueKey IDs + trigger semantics only, flagged "
            "PROPOSED_NOT_RUNTIME. They introduce no runtime key, no "
            "file, no binding. Composing them is M-E CP2 proper and "
            "still awaits the Codex decision.",
            "The byte check here is scoped to the 63 catalogue keys' "
            "representative files (the evidence for the new coverage "
            "claim). It does not re-measure loudness or re-audit the "
            "CP08 SFX_UI pack, per Gói 38 (no repeat checkpoints over "
            "unchanged bytes without a binary/policy/tool delta).",
            "All verdicts are coverage verdicts, not listening verdicts: "
            "NOT_AUDITIONED still holds for every cue.",
        ],
    }
    OUT.write_text(json.dumps(manifest, indent=1, ensure_ascii=False)
                   + "\n", encoding="utf-8")
    print(f"catalogue: {len(coverage)} keys, {covered} COVERED_VERIFIED")
    print(f"delivered beyond catalogue: {len(extra)} keys")
    print(f"files verified from real bytes: {CHECKS['files_verified']}")
    print(f"requirements: {len(requirements)} "
          f"({manifest['verdicts']})")
    print(f"proposals: {len(proposals)} (1 GAP + 2 QUESTION), "
          f"questions: {len(questions)}")
    if ERRORS:
        print(f"FAILED with {len(ERRORS)} mismatches", file=sys.stderr)
        return 1
    print("wrote " + str(OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
