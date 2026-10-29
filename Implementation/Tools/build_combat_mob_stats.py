#!/usr/bin/env python3
"""Build the runtime combat mob stat bundle from the versioned design sources.

Source of truth (QOD-16 proposal, work order 07 QOD-B):
  * Art_Entity_Weather_UI_Visual_Bible_vi.md section 12 — mob base formulas,
    archetype multipliers, attack moves, elite/boss multipliers.
  * Production_Rules_Complete_v1_vi.md section 4 — Mãng Cốt three attacks.
  * P1_Design_Resolution_20261029_vi.md — reference values used as build-time
    assertions (owner-locked level-5 reference table).

Output: Implementation/Content/Runtime/combat_mob_stats_v1.json

Per-spawn mob level has no source in World_Spawn_Gathering_Manifest_vi.csv
(only character_level_min/max bands), so the bundle carries the owner-locked
REFERENCE_L5 values and the base formulas; a per-spawn level source is an open
decision (QOD-16 Q1). The bundle is DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION:
the server loads it only behind the P1:CombatDamage gate, which is OFF by
default. Deterministic output: sorted keys, fixed float formatting, one
trailing newline.
"""

import argparse
import json
import math
import sys
from pathlib import Path

OUTPUT = Path("Implementation/Content/Runtime/combat_mob_stats_v1.json")

METERS_PER_WU = 0.5
REFERENCE_LEVEL = 5

# Art Bible §12 "Monster stat and AI profile baseline".
BASE_FORMULAS = {
    "hp": {"base": 120, "perLevel": 24},
    "attack": {"base": 10, "perLevel": 2},
    "defense": {"base": 2, "perLevel": 0.8},
}

# Art Bible §12 archetype table (HPx/ATKx/DEFx, speed m/s, aggro m, attacks).
# Attack names are kept from the canonical table; multipliers and telegraphs
# are transcribed exactly.
ARCHETYPES = [
    {
        "mobId": "MOB_CARPLING",
        "multipliers": {"hp": 0.8, "attack": 0.75, "defense": 0.7},
        "moveSpeedMetersPerSecond": 3.0,
        "aggroRadiusMeters": 7,
        "attacks": [
            {"attackId": "BITE", "nameVi": "đớp", "attackMultiplier": 0.8,
             "rangeMeters": 2.0, "telegraphSeconds": 0.45},
            {"attackId": "LEAP", "nameVi": "nhảy", "attackMultiplier": 1.1,
             "rangeMeters": None, "telegraphSeconds": 0.45},
        ],
    },
    {
        "mobId": "MOB_WATERROOT",
        "multipliers": {"hp": 1.1, "attack": 1.0, "defense": 1.1},
        "moveSpeedMetersPerSecond": 0.5,
        "aggroRadiusMeters": 5,
        "attacks": [
            {"attackId": "VINE", "nameVi": "roi rễ", "attackMultiplier": 1.0,
             "rangeMeters": 2.6, "telegraphSeconds": 0.45},
            {"attackId": "SPROUT", "nameVi": "chồi đất", "attackMultiplier": 1.5,
             "rangeMeters": 4.0, "lineMeters": 4.0, "telegraphSeconds": 0.7},
        ],
    },
    {
        "mobId": "MOB_SHORE_STALKER",
        "multipliers": {"hp": 0.9, "attack": 1.15, "defense": 0.8},
        "moveSpeedMetersPerSecond": 3.4,
        "aggroRadiusMeters": 8,
        "attacks": [
            {"attackId": "POUNCE", "nameVi": "vồ", "attackMultiplier": 1.0,
             "rangeMeters": None, "telegraphSeconds": 0.45},
            {"attackId": "DASH_BITE", "nameVi": "lao", "attackMultiplier": 1.4,
             "rangeMeters": None, "telegraphSeconds": 0.6},
        ],
    },
]

ELITE = {"hpMultiplier": 6.0, "attackMultiplier": 1.6, "defenseMultiplier": 1.8}

# Art Bible §12 boss table + Production_Rules §4 Mãng Cốt moves.
# phaseGuard/interruptible are not specified anywhere yet, so the boss record
# stays BOSSDATA_BLOCKED per Production_Rules §4 (missing fields fail export,
# no other boss profile may substitute).
BOSSES = [
    {
        "bossId": "BOSS_MANG_COT",
        "hpMultiplier": 35.0,
        "attackMultiplier": 2.0,
        "partyHpMultiplierPerAdditionalPlayer": 0.65,
        "referenceLevel": 10,
        "attacks": [
            {"attackId": "A_BODY_SWEEP", "shape": "CONE", "angleDegrees": 120,
             "rangeWu": 8.0, "telegraphSeconds": 0.9, "attackMultiplier": 1.2,
             "recoverySeconds": 0.8, "cooldownSeconds": 4.0},
            {"attackId": "B_DIVE_SURFACE", "shape": "CIRCLE", "radiusWu": 4.0,
             "atLockedTarget": True, "telegraphSeconds": 1.2,
             "attackMultiplier": 1.5, "recoverySeconds": 1.0,
             "cooldownSeconds": 9.0},
            {"attackId": "C_BUBBLE_RING", "shape": "ANNULUS",
             "innerRadiusWu": 3.0, "outerRadiusWu": 7.0,
             "telegraphSeconds": 1.0, "attackMultiplier": 1.3,
             "recoverySeconds": 1.0, "cooldownSeconds": 12.0},
        ],
        "activation": "BOSSDATA_BLOCKED",
        "blockedReason": ("phaseGuard/interruptible not specified; "
                          "Production_Rules §4 requires full numeric data "
                          "before boss export"),
    },
]

# Owner-locked reference values from P1_Design_Resolution_20261029_vi.md §2.
# The builder asserts its computed level-5 values match these exactly.
DESIGN_RESOLUTION_L5 = {
    "MOB_CARPLING": {"hp": 192, "attack": 15.0, "defense": 4.2},
    "MOB_WATERROOT": {"hp": 264, "attack": 20.0, "defense": 6.6},
    "MOB_SHORE_STALKER": {"hp": 216, "attack": 23.0, "defense": 4.8},
}
DESIGN_RESOLUTION_ELITE_L5 = {"hp": 1152, "attack": 24.0, "defense": 7.56}
DESIGN_RESOLUTION_BOSS_L10 = {"hp": 12600.0, "attack": 60.0, "defense": 10.0}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def level_stats(multipliers, level):
    def base(key):
        return BASE_FORMULAS[key]["base"] + BASE_FORMULAS[key]["perLevel"] * level

    return {
        "hp": base("hp") * multipliers["hp"],
        "attack": base("attack") * multipliers["attack"],
        "defense": base("defense") * multipliers["defense"],
    }


def close(a, b, epsilon=1e-9):
    return abs(a - b) <= epsilon


def clean(value):
    """Pin float representation to 9 decimals so the export is readable and
    byte-deterministic. Values like 4.199999999999999 come from exact math on
    decimal multipliers; 9 decimals keeps every design value (0.8, 7.56, ...)
    exact while removing binary float noise."""
    if isinstance(value, float):
        return float(f"{value:.9f}")
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    return value


def build():
    archetypes = []
    for source in ARCHETYPES:
        l5 = level_stats(source["multipliers"], REFERENCE_LEVEL)
        expected = DESIGN_RESOLUTION_L5[source["mobId"]]
        for key in ("hp", "attack", "defense"):
            if not close(l5[key], expected[key]):
                fail(f"{source['mobId']} L5 {key} computed {l5[key]} "
                     f"!= design resolution {expected[key]}")
        archetypes.append({
            "mobId": source["mobId"],
            "multipliers": source["multipliers"],
            "moveSpeedMetersPerSecond": source["moveSpeedMetersPerSecond"],
            "aggroRadiusMeters": source["aggroRadiusMeters"],
            "attacks": source["attacks"],
            "referenceLevel5": {
                "hp": int(round(l5["hp"])),
                "attack": l5["attack"],
                "defense": l5["defense"],
            },
            "sourceRef": ("docs/production/Art_Entity_Weather_UI_Visual_"
                          "Bible_vi.md#12"),
        })

    elite_l5 = level_stats(
        ARCHETYPES[0]["multipliers"], REFERENCE_LEVEL)
    elite_l5 = {key: elite_l5[key] * ELITE[key + "Multiplier"]
                for key in ("hp", "attack", "defense")}
    for key in ("hp", "attack", "defense"):
        if not close(elite_l5[key], DESIGN_RESOLUTION_ELITE_L5[key]):
            fail(f"elite L5 {key} computed {elite_l5[key]} "
                 f"!= design resolution {DESIGN_RESOLUTION_ELITE_L5[key]}")

    bosses = []
    for source in BOSSES:
        level = source["referenceLevel"]
        hp = (BASE_FORMULAS["hp"]["base"]
              + BASE_FORMULAS["hp"]["perLevel"] * level) * source["hpMultiplier"]
        attack = (BASE_FORMULAS["attack"]["base"]
                  + BASE_FORMULAS["attack"]["perLevel"] * level) * source["attackMultiplier"]
        defense = (BASE_FORMULAS["defense"]["base"]
                   + BASE_FORMULAS["defense"]["perLevel"] * level)
        expected = DESIGN_RESOLUTION_BOSS_L10
        if not (close(hp, expected["hp"]) and close(attack, expected["attack"])
                and close(defense, expected["defense"])):
            fail(f"{source['bossId']} L{level} computed "
                 f"({hp}, {attack}, {defense}) != design resolution "
                 f"{expected}")
        bosses.append({
            "bossId": source["bossId"],
            "hpMultiplier": source["hpMultiplier"],
            "attackMultiplier": source["attackMultiplier"],
            "partyHpMultiplierPerAdditionalPlayer":
                source["partyHpMultiplierPerAdditionalPlayer"],
            "referenceLevel": level,
            "referenceStats": {"hp": int(round(hp)), "attack": attack,
                               "defense": defense},
            "attacks": source["attacks"],
            "activation": source["activation"],
            "blockedReason": source["blockedReason"],
            "sourceRef": ("docs/production/Art_Entity_Weather_UI_Visual_"
                          "Bible_vi.md#12; docs/production/"
                          "Production_Rules_Complete_v1_vi.md#4"),
        })

    bundle = {
        "schemaVersion": 1,
        "bundleId": "COMBAT_MOB_STATS_V1",
        "activation": "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION",
        "referenceLevel": REFERENCE_LEVEL,
        "levelPolicy": "REFERENCE_L5",
        "levelPolicyNote": (
            "Per-spawn mob level has no source in "
            "World_Spawn_Gathering_Manifest_vi.csv (only "
            "character_level_min/max bands); owner decision pending "
            "(QOD-16 proposal Q1)."),
        "units": {"distance": "WU", "metersPerWu": METERS_PER_WU,
                  "time": "seconds"},
        "baseFormulas": BASE_FORMULAS,
        "elite": ELITE,
        "eliteReferenceLevel5": {
            "hp": int(round(elite_l5["hp"])),
            "attack": elite_l5["attack"],
            "defense": elite_l5["defense"],
        },
        "archetypes": archetypes,
        "bosses": bosses,
        "sourceRef": ("docs/production/Art_Entity_Weather_UI_Visual_"
                      "Bible_vi.md#12; docs/production/"
                      "Production_Rules_Complete_v1_vi.md#4; docs/production/"
                      "P1_Design_Resolution_20261029_vi.md"),
    }
    return bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    bundle = build()
    payload = json.dumps(clean(bundle), ensure_ascii=False, indent=2,
                         sort_keys=True) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(payload, encoding="utf-8")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
