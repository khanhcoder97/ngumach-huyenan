
"""Candidate builders for the Bến Mưa content pipeline (OPC-11)."""

from __future__ import annotations

import re

try:  # Direct execution from the tool directory.
    from compiler_core import (
        ACTOR_SCHEMA_PATH,
        BOSS_REFERENCE_LEVEL,
        BOSS_SCHEMA_PATH,
        Context,
        ITEM_SCHEMA_PATH,
        KIND_ORDER,
        METERS_PER_WU,
        MOB_SCHEMA_PATH,
        OBJECTIVE_MAP_SCHEMA_PATH,
        PipelineError,
        REFERENCE_LEVEL,
        _add_tree,
        _candidate,
        _unresolved,
        build_provenance,
        build_quest_candidates,
    )
except ImportError:  # Import as part of the ContentPipeline package.
    from .compiler_core import (
        ACTOR_SCHEMA_PATH,
        BOSS_REFERENCE_LEVEL,
        BOSS_SCHEMA_PATH,
        Context,
        ITEM_SCHEMA_PATH,
        KIND_ORDER,
        METERS_PER_WU,
        MOB_SCHEMA_PATH,
        OBJECTIVE_MAP_SCHEMA_PATH,
        PipelineError,
        REFERENCE_LEVEL,
        _add_tree,
        _candidate,
        _unresolved,
        build_provenance,
        build_quest_candidates,
    )

OBJECTIVE_MAP_SPECS = {
    "P00-01": {
        "mappings": [
            {
                "objectiveId": "OBJ_P00_01_PACKAGES",
                "eventType": "COLLECT",
                "sourceIds": ["OBJ_BM_PACKAGE_01", "OBJ_BM_PACKAGE_02", "OBJ_BM_PACKAGE_03"],
                "positions": [
                    {"sourceId": "OBJ_BM_PACKAGE_01", "xWu": 36, "yWu": 0},
                    {"sourceId": "OBJ_BM_PACKAGE_02", "xWu": 44, "yWu": 0},
                    {"sourceId": "OBJ_BM_PACKAGE_03", "xWu": 52, "yWu": 0},
                ],
                "count": 3,
                "rangeWu": 5,
                "rangeSource": ("PRODUCTION_RULES", "5"),
                "sharePolicy": "PER_CHARACTER_ONCE",
            }
        ],
        "unresolved": [],
    },
    "P00-02": {
        "mappings": [
            {
                "objectiveId": "OBJ_P00_02_RIPPLES",
                "eventType": "INTERACT",
                "sourceIds": [
                    "OBJ_BM_WATER_RIPPLE_01",
                    "OBJ_BM_WATER_RIPPLE_02",
                    "OBJ_BM_WATER_RIPPLE_03",
                ],
                "positions": [
                    {"sourceId": "OBJ_BM_WATER_RIPPLE_01", "xWu": 122, "yWu": -1},
                    {"sourceId": "OBJ_BM_WATER_RIPPLE_02", "xWu": 132, "yWu": -1},
                    {"sourceId": "OBJ_BM_WATER_RIPPLE_03", "xWu": 142, "yWu": -1},
                ],
                "count": 3,
            },
            {
                "objectiveId": "OBJ_P00_02_CARPLING",
                "eventType": "KILL",
                "sourceIds": ["MOB_CARPLING"],
                "positions": [{"sourceId": "MOB_CARPLING", "xWu": 116, "yWu": 0}],
                "spawnRecordIds": ["MAN-BM-SPAWN_BM_02"],
                "respawnSeconds": 20,
                "count": 4,
            },
            {
                "objectiveId": "OBJ_P00_02_REPORT",
                "eventType": "TALK",
                "sourceIds": ["NPC_TA_VAN_KHANH"],
                "positions": [{"sourceId": "NPC_TA_VAN_KHANH", "xWu": 64, "yWu": 0}],
                "count": 1,
                "rangeWu": 2,
                "rangeSource": ("NPC_REGISTRY", ""),
            },
        ],
        "unresolved": [
            ("/mappings/0/rangeWu", "Map Atlas gives ripple positions but no interaction radius.", "MISSING", "MAP_ATLAS", "Map-01-Ben-Mua"),
            ("/mappings/0/sharePolicy", "Rules require a share policy per objective but only P00-01 collect is specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/1/sharePolicy", "Rules require a share policy per objective but P00-02 kill sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/2/sharePolicy", "Rules require a share policy per objective but P00-02 talk sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
        ],
    },
    "P00-03": {
        "mappings": [
            {
                "objectiveId": "OBJ_P00_03_WATERROOTS",
                "eventType": "KILL",
                "positions": [
                    {"xWu": 126, "yWu": 0},
                    {"xWu": 138, "yWu": 0},
                    {"xWu": 151, "yWu": 0},
                ],
                "count": 3,
            },
            {
                "objectiveId": "OBJ_P00_03_RESCUE",
                "eventType": "INTERACT",
                "sourceIds": ["NPC_BM_RESCUE_01", "NPC_BM_RESCUE_02"],
                "positions": [
                    {"sourceId": "NPC_BM_RESCUE_01", "xWu": 135, "yWu": 0},
                    {"sourceId": "NPC_BM_RESCUE_02", "xWu": 148, "yWu": 0},
                ],
                "count": 2,
                "rangeWu": 2,
                "rangeSource": ("NPC_REGISTRY", ""),
                "availability": "P00-04_PER_MANIFEST",
                "availabilitySource": ("SPAWN_MANIFEST", "MAN-BM-NPC_BM_RESCUE_01"),
            },
        ],
        "unresolved": [
            ("/mappings/0/sourceIds", "Map Atlas places three interactive roots but gives no objective source IDs.", "MISSING", "MAP_ATLAS", "Map-01-Ben-Mua"),
            ("/mappings/0/eventType", "Map Atlas calls the roots interactive while the quest says destroy them; KILL versus INTERACT is unresolved.", "PRESENT_UNRESOLVED", "PRODUCTION_RULES", "5"),
            ("/mappings/0/rangeWu", "Map Atlas gives root positions but no interaction radius.", "MISSING", "MAP_ATLAS", "Map-01-Ben-Mua"),
            ("/mappings/0/sharePolicy", "Rules require a share policy per objective but P00-03 root sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/1/sharePolicy", "Rules require a share policy per objective but P00-03 rescue sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/1/availability", "The manifest labels the rescue NPCs P00-04 while the quest assigns the rescue to P00-03.", "PRESENT_UNRESOLVED", "SPAWN_MANIFEST", "MAN-BM-NPC_BM_RESCUE_01"),
            ("/mappings/2", "The dodge-one-wave step has no canonical event type or target record.", "MISSING", "QUEST_SPEC", "P00-03"),
        ],
    },
    "P00-04": {
        "mappings": [
            {
                "objectiveId": "OBJ_P00_04_ESCORT",
                "eventType": "ESCORT",
                "sourceIds": ["NPC_LYAN"],
                "positions": [{"sourceId": "NPC_LYAN", "xWu": 42, "yWu": 0}],
                "checkpoints": [
                    {"triggerXWu": 80, "rangeWu": 5},
                    {"triggerXWu": 120, "rangeWu": 5},
                ],
                "count": 1,
            },
            {
                "objectiveId": "OBJ_P00_04_WAVES",
                "eventType": "KILL",
                "sourceIds": ["MOB_CARPLING", "MOB_WATERROOT"],
                "positions": [
                    {"sourceId": "WAVE_BM_ESCORT_A", "xWu": 76, "yWu": 0},
                    {"sourceId": "WAVE_BM_ESCORT_A", "xWu": 80, "yWu": 0},
                    {"sourceId": "WAVE_BM_ESCORT_A", "xWu": 84, "yWu": 0},
                    {"sourceId": "WAVE_BM_ESCORT_B", "xWu": 116, "yWu": 0},
                    {"sourceId": "WAVE_BM_ESCORT_B", "xWu": 120, "yWu": 0},
                    {"sourceId": "WAVE_BM_ESCORT_B", "xWu": 124, "yWu": 0},
                ],
                "spawnRecordIds": [
                    "MAN-BM-WAVE_BM_ESCORT_A",
                    "MAN-BM-WAVE_BM_ESCORT_B",
                ],
                "respawnSeconds": 30,
                "count": 6,
            },
        ],
        "unresolved": [
            ("/mappings/0/sharePolicy", "Rules require a share policy per objective but P00-04 escort sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/1/sharePolicy", "Rules require a share policy per objective but P00-04 wave sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
        ],
    },
    "P00-05": {
        "mappings": [
            {
                "objectiveId": "OBJ_P00_05_BOSS",
                "eventType": "BOSS",
                "sourceIds": ["BOSS_MANG_COT"],
                "positions": [{"sourceId": "BOSS_MANG_COT", "xWu": 178, "yWu": 0}],
                "spawnRecordIds": ["MAN-BM-SPAWN_BM_05_QUEST"],
                "respawnSeconds": 0,
                "count": 1,
                "arenaRingDiameterWu": 22,
            },
            {
                "objectiveId": "OBJ_P00_05_SEAL",
                "eventType": "INTERACT",
                "sourceIds": ["OBJ_BM_SEAL"],
                "positions": [{"sourceId": "OBJ_BM_SEAL", "xWu": 178, "yWu": 0}],
                "count": 1,
                "availability": "AFTER_BOSS_DEATH",
                "availabilitySource": ("MAP_ATLAS", "Map-01-Ben-Mua"),
            },
            {
                "objectiveId": "OBJ_P00_05_CLASS_CONFIRM",
                "eventType": "TALK",
                "sourceIds": ["NPC_CLASS_TRIAL"],
                "positions": [{"sourceId": "NPC_CLASS_TRIAL", "xWu": 188, "yWu": 0}],
                "count": 1,
                "rangeWu": 2,
                "rangeSource": ("NPC_REGISTRY", ""),
                "availability": "AFTER_P00_05_COMPLETION",
                "availabilitySource": ("SPAWN_MANIFEST", "MAN-BM-NPC_CLASS_TRIAL"),
            },
        ],
        "unresolved": [
            ("/mappings/0/sharePolicy", "Rules require a share policy per objective but P00-05 boss sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/1/rangeWu", "Map Atlas places the seal at x=178 but gives no interaction radius.", "MISSING", "MAP_ATLAS", "Map-01-Ben-Mua"),
            ("/mappings/1/sharePolicy", "Rules require a share policy per objective but P00-05 seal sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/2/availability", "The manifest says NPC_CLASS_TRIAL appears only after P00-05, but P00-05 itself requires confirming the class at that NPC.", "PRESENT_UNRESOLVED", "SPAWN_MANIFEST", "MAN-BM-NPC_CLASS_TRIAL"),
            ("/mappings/2/sharePolicy", "Rules require a share policy per objective but P00-05 class-confirm sharing is not specified.", "MISSING", "PRODUCTION_RULES", "5"),
            ("/mappings/3", "Entering the boss ring has no canonical event type or source record.", "MISSING", "QUEST_SPEC", "P00-05"),
        ],
    },
}


def build_objective_map_candidates(ctx: Context) -> list[dict]:
    candidates = []
    for quest_id, spec in OBJECTIVE_MAP_SPECS.items():
        mappings = []
        sources = []
        for raw in spec["mappings"]:
            mapping = {key: value for key, value in raw.items() if not key.endswith("Source")}
            mappings.append(mapping)
            sources.append(raw)
        definition = {
            "questId": quest_id,
            "mapId": "MAP_BEN_MUA",
            "floorId": "OVERWORLD",
            "mappings": mappings,
        }

        def fill(prov, quest_id=quest_id, sources=sources):
            _add_tree(prov, definition, "/questId", "QUEST_SPEC", quest_id, transform="verbatim")
            _add_tree(prov, definition, "/mapId", "MAP_ATLAS", "Map-01-Ben-Mua", transform="verbatim")
            _add_tree(prov, definition, "/floorId", "SPAWN_MANIFEST", "", transform="verbatim")
            for index, raw in enumerate(sources):
                prefix = f"/mappings/{index}"
                _add_tree(prov, definition, prefix, "QUEST_SPEC", quest_id, transform="verbatim")
                _add_tree(prov, definition, f"{prefix}/objectiveId", "QUEST_SPEC", quest_id, transform="proposed_stable_id")
                _add_tree(prov, definition, f"{prefix}/eventType", "PRODUCTION_RULES", "5", transform="mapped_to_event_type")
                if "sourceIds" in raw:
                    _add_tree(prov, definition, f"{prefix}/sourceIds", "MAP_ATLAS", "Map-01-Ben-Mua", transform="transcribed")
                if "positions" in raw:
                    _add_tree(prov, definition, f"{prefix}/positions", "MAP_ATLAS", "Map-01-Ben-Mua", transform="transcribed")
                if "spawnRecordIds" in raw:
                    _add_tree(prov, definition, f"{prefix}/spawnRecordIds", "SPAWN_MANIFEST", "", transform="verbatim")
                if "respawnSeconds" in raw:
                    _add_tree(prov, definition, f"{prefix}/respawnSeconds", "SPAWN_MANIFEST", "", transform="verbatim")
                if "count" in raw:
                    _add_tree(prov, definition, f"{prefix}/count", "QUEST_SPEC", quest_id, transform="verbatim")
                if "rangeWu" in raw:
                    source_id, fragment = raw["rangeSource"]
                    _add_tree(prov, definition, f"{prefix}/rangeWu", source_id, fragment, transform="verbatim")
                if "checkpoints" in raw:
                    _add_tree(prov, definition, f"{prefix}/checkpoints", "MAP_ATLAS", "Map-01-Ben-Mua", transform="transcribed")
                if "sharePolicy" in raw:
                    _add_tree(prov, definition, f"{prefix}/sharePolicy", "PRODUCTION_RULES", "5", transform="verbatim")
                if "availability" in raw:
                    source_id, fragment = raw["availabilitySource"]
                    _add_tree(prov, definition, f"{prefix}/availability", source_id, fragment, transform="verbatim")
                if "arenaRingDiameterWu" in raw:
                    _add_tree(prov, definition, f"{prefix}/arenaRingDiameterWu", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_05_QUEST", transform="verbatim")

        unresolved = [
            _unresolved(ctx, path, reason, state, source_id, fragment)
            for path, reason, state, source_id, fragment in spec["unresolved"]
        ]
        candidates.append(
            _candidate(
                f"OBJMAP-{quest_id}",
                "OBJECTIVE_MAP",
                quest_id,
                OBJECTIVE_MAP_SCHEMA_PATH,
                definition,
                build_provenance(ctx, f"OBJMAP-{quest_id}", definition, fill),
                unresolved,
            )
        )
    return candidates


def build_actor_candidate(ctx: Context) -> dict:
    class_id = "CLASS_MINH_KIEM"
    definition = {
        "profileId": "ACTOR_BASE_L1_NO_GEAR",
        "level": 1,
        "mapId": "MAP_BEN_MUA",
        "attributes": {"STR": 5, "INT": 5, "AGI": 5, "VIT": 5, "LUK": 5},
        "derived": {
            "maxHp": 198,
            "maxMp": 102,
            "physicalAttack": 20,
            "magicAttack": 20,
            "armor": 10,
        },
        "formulas": {
            "maxHp": "100 + 28*level + 14*VIT + gearHP",
            "maxMp": "50 + 12*level + 8*INT + gearMP",
            "physicalAttack": "weaponPhysical + 3*STR + AGI + flatGearAttack",
            "magicAttack": "weaponMagic + 3*INT + LUK + flatGearAttack",
            "armor": "gearArmor + 2*VIT",
        },
        "equipment": [],
        "classSkillReferences": [
            {"classId": class_id, "startingSkillIds": list(ctx.class_skills[class_id])}
        ],
    }

    def fill(prov):
        _add_tree(prov, definition, "/profileId", "P1_RESOLUTION", "2", transform="verbatim")
        _add_tree(prov, definition, "/level", "P1_RESOLUTION", "2", transform="verbatim")
        _add_tree(prov, definition, "/mapId", "MAP_ATLAS", "Map-01-Ben-Mua", transform="verbatim")
        _add_tree(prov, definition, "/attributes", "PRODUCTION_RULES", "1", transform="verbatim")
        _add_tree(prov, definition, "/derived", "P1_RESOLUTION", "2", transform="derived_formula_reference")
        _add_tree(prov, definition, "/formulas", "PRODUCTION_RULES", "1", transform="verbatim")
        _add_tree(prov, definition, "/equipment", "P1_RESOLUTION", "2", transform="verbatim")
        _add_tree(prov, definition, "/classSkillReferences", "CLASS_EXAMPLE_MINH_KIEM", "", transform="verbatim")

    unresolved = [
        _unresolved(
            ctx,
            "/equippedProfile",
            "Canonical item catalogs contain gear vectors; an equipped profile still needs a reviewed loadout/instance adapter applying DEC-023 aliases without double counting.",
            "MISSING",
            "RUNTIME_PRECISION",
            "3",
        ),
        _unresolved(
            ctx,
            "/classCoverage",
            "Only CLASS_MINH_KIEM has canonical ClassDefinition and SkillDefinition examples; the other four classes are not compiled.",
            "MISSING",
            "PRODUCTION_AUDIT",
            "GAP-01",
        ),
    ]
    return _candidate(
        "ACTOR-BASE-L1-NO-GEAR",
        "ACTOR_PROFILE",
        "ACTOR_BASE_L1_NO_GEAR",
        ACTOR_SCHEMA_PATH,
        definition,
        build_provenance(ctx, "ACTOR-BASE-L1-NO-GEAR", definition, fill),
        unresolved,
    )


MOB_SPECS = {
    "MOB_CARPLING": {
        "spawnRecordIds": [
            "MAN-BM-SPAWN_BM_01",
            "MAN-BM-SPAWN_BM_02",
            "MAN-BM-SPAWN_BM_04",
            "MAN-BM-WAVE_BM_ESCORT_A",
        ],
        "multipliers": {"hp": 0.8, "attack": 0.75, "defense": 0.7},
        "speed": 3.0,
        "aggro": 7,
        "attacks": [
            {
                "attackId": "ATK_CARPLING_BITE",
                "kind": "BASIC",
                "damageMultiplier": 0.8,
                "rangeMeters": 2.0,
            },
            {
                "attackId": "ATK_CARPLING_LEAP",
                "kind": "SPECIAL",
                "damageMultiplier": 1.1,
                "telegraphSeconds": 0.45,
            },
        ],
        "unresolved": [
            ("/spawnLevel", "The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only.", "MISSING", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_01"),
            ("/quantizationPolicy", "P1 leaves runtime HP/attack/defense integer quantization undecided.", "MISSING", "P1_RESOLUTION", "2"),
            ("/attacks/0/telegraphSeconds", "Art Bible gives no exact basic-bite telegraph; only the general melee minimum.", "MISSING", "ART_BIBLE", "12"),
            ("/attacks/1/rangeMeters", "Art Bible gives the leap multiplier and telegraph but no range.", "MISSING", "ART_BIBLE", "12"),
            ("/attacks/1/telegraphSeconds", "Art Bible gives 0.45s for the leap while the general heavy-attack minimum is 0.7s; the conflict is unresolved.", "PRESENT_UNRESOLVED", "ART_BIBLE", "12"),
        ],
    },
    "MOB_WATERROOT": {
        "spawnRecordIds": ["MAN-BM-SPAWN_BM_03", "MAN-BM-SPAWN_BM_04", "MAN-BM-WAVE_BM_ESCORT_B"],
        "multipliers": {"hp": 1.1, "attack": 1.0, "defense": 1.1},
        "speed": 0.5,
        "aggro": 5,
        "attacks": [
            {
                "attackId": "ATK_WATERROOT_ROOT_WHIP",
                "kind": "BASIC",
                "damageMultiplier": 1.0,
                "rangeMeters": 2.6,
            },
            {
                "attackId": "ATK_WATERROOT_BURROW",
                "kind": "SPECIAL",
                "damageMultiplier": 1.5,
                "rangeMeters": 4.0,
                "telegraphSeconds": 0.7,
            },
        ],
        "unresolved": [
            ("/spawnLevel", "The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only.", "MISSING", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_03"),
            ("/quantizationPolicy", "P1 leaves runtime HP/attack/defense integer quantization undecided.", "MISSING", "P1_RESOLUTION", "2"),
            ("/attacks/0/telegraphSeconds", "Art Bible gives no exact basic root-whip telegraph; only the general melee minimum.", "MISSING", "ART_BIBLE", "12"),
        ],
    },
    "MOB_SHORE_STALKER": {
        "spawnRecordIds": ["MAN-BM-SPAWN_BM_06", "MAN-BM-SPAWN_BM_07"],
        "multipliers": {"hp": 0.9, "attack": 1.15, "defense": 0.8},
        "speed": 3.4,
        "aggro": 8,
        "attacks": [
            {
                "attackId": "ATK_SHORE_STALKER_POUNCE",
                "kind": "BASIC",
                "damageMultiplier": 1.0,
            },
            {
                "attackId": "ATK_SHORE_STALKER_CHARGE",
                "kind": "SPECIAL",
                "damageMultiplier": 1.4,
                "telegraphSeconds": 0.6,
            },
        ],
        "unresolved": [
            ("/spawnLevel", "The manifest gives a level band 1-10, not a chosen spawn level; P1 level 5 is a reference profile only.", "MISSING", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_06"),
            ("/quantizationPolicy", "P1 leaves runtime HP/attack/defense integer quantization undecided.", "MISSING", "P1_RESOLUTION", "2"),
            ("/eliteVariant", "Spawn group SPAWN_BM_07 also contains MOB_SHORE_STALKER_ELITE; its elite override stats are not part of this base profile.", "MISSING", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_07"),
            ("/attacks/0/rangeMeters", "Art Bible gives the pounce multiplier but no range.", "MISSING", "ART_BIBLE", "12"),
            ("/attacks/0/telegraphSeconds", "Art Bible gives no exact pounce telegraph; only the general melee minimum.", "MISSING", "ART_BIBLE", "12"),
            ("/attacks/1/rangeMeters", "Art Bible gives the charge multiplier and telegraph but no range.", "MISSING", "ART_BIBLE", "12"),
            ("/attacks/1/telegraphSeconds", "Art Bible gives 0.6s for the charge while the general heavy-attack minimum is 0.7s; the conflict is unresolved.", "PRESENT_UNRESOLVED", "ART_BIBLE", "12"),
        ],
    },
}


def _number(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def build_mob_candidates(ctx: Context) -> list[dict]:
    base_hp = 120 + 24 * REFERENCE_LEVEL
    base_attack = 10 + 2 * REFERENCE_LEVEL
    base_defense = 2 + 0.8 * REFERENCE_LEVEL
    candidates = []
    for mob_id, spec in MOB_SPECS.items():
        records = [ctx.spawn_by_id[record_id] for record_id in spec["spawnRecordIds"]]
        levels_min = min(int(record["character_level_min"]) for record in records)
        levels_max = max(int(record["character_level_max"]) for record in records)
        loot_table_ids = sorted({record["loot_table_id"] for record in records if record.get("loot_table_id")})
        attacks = []
        for attack in spec["attacks"]:
            value = dict(attack)
            if "rangeMeters" in value:
                value["rangeWu"] = _number(value["rangeMeters"] * (1.0 / METERS_PER_WU))
            attacks.append(value)
        definition = {
            "mobId": mob_id,
            "referenceLevel": REFERENCE_LEVEL,
            "levelBand": {"min": levels_min, "max": levels_max},
            "spawnRecordIds": list(spec["spawnRecordIds"]),
            "baseStats": {
                "hp": base_hp,
                "attack": base_attack,
                "defense": _number(base_defense),
            },
            "multipliers": dict(spec["multipliers"]),
            "stats": {
                "hp": _number(round(base_hp * spec["multipliers"]["hp"], 6)),
                "attack": _number(round(base_attack * spec["multipliers"]["attack"], 6)),
                "defense": _number(round(base_defense * spec["multipliers"]["defense"], 6)),
            },
            "speedMetersPerSecond": spec["speed"],
            "speedWuPerSecond": _number(spec["speed"] * (1.0 / METERS_PER_WU)),
            "aggroRadiusMeters": spec["aggro"],
            "aggroRadiusWu": _number(spec["aggro"] * (1.0 / METERS_PER_WU)),
            "attacks": attacks,
            "lootTableIds": loot_table_ids,
        }

        def fill(prov, mob_id=mob_id, spec=spec):
            _add_tree(prov, definition, "/mobId", "ART_BIBLE", "12", transform="verbatim")
            _add_tree(prov, definition, "/referenceLevel", "P1_RESOLUTION", "2", transform="verbatim")
            _add_tree(prov, definition, "/levelBand", "SPAWN_MANIFEST", "", transform="verbatim")
            _add_tree(prov, definition, "/spawnRecordIds", "SPAWN_MANIFEST", "", transform="verbatim")
            _add_tree(prov, definition, "/baseStats", "ART_BIBLE", "12", transform="base_formula_at_reference_level")
            _add_tree(prov, definition, "/multipliers", "ART_BIBLE", "12", transform="verbatim")
            _add_tree(prov, definition, "/stats", "ART_BIBLE", "12", transform="archetype_multiplier_applied_once")
            _add_tree(prov, definition, "/speedMetersPerSecond", "ART_BIBLE", "12", transform="verbatim")
            _add_tree(prov, definition, "/speedWuPerSecond", "ART_BIBLE", "12", transform="meters_to_wu")
            _add_tree(prov, definition, "/aggroRadiusMeters", "ART_BIBLE", "12", transform="verbatim")
            _add_tree(prov, definition, "/aggroRadiusWu", "ART_BIBLE", "12", transform="meters_to_wu")
            _add_tree(prov, definition, "/attacks", "ART_BIBLE", "12", transform="verbatim")
            for index, attack in enumerate(definition["attacks"]):
                if "rangeWu" in attack:
                    _add_tree(prov, definition, f"/attacks/{index}/rangeWu", "ART_BIBLE", "12", transform="meters_to_wu")
            _add_tree(prov, definition, "/lootTableIds", "SPAWN_MANIFEST", "", transform="aggregated_manifest_lookup")

        unresolved = [
            _unresolved(ctx, path, reason, state, source_id, fragment)
            for path, reason, state, source_id, fragment in spec["unresolved"]
        ]
        candidates.append(
            _candidate(
                f"MOB-{mob_id}",
                "MOB_PROFILE",
                mob_id,
                MOB_SCHEMA_PATH,
                definition,
                build_provenance(ctx, f"MOB-{mob_id}", definition, fill),
                unresolved,
            )
        )
    return candidates


def build_boss_candidate(ctx: Context) -> dict:
    reference_level = BOSS_REFERENCE_LEVEL
    base_hp = 120 + 24 * reference_level
    hp_factor = 35
    hp_solo = base_hp * hp_factor
    hp_party2 = base_hp * hp_factor * (1 + 0.65)
    spawn_record_ids = ["MAN-BM-SPAWN_BM_05_QUEST", "MAN-BM-EVENT_BOSS_BM_MANG_COT"]
    records = [ctx.spawn_by_id[record_id] for record_id in spawn_record_ids]
    levels_min = min(int(record["character_level_min"]) for record in records)
    levels_max = max(int(record["character_level_max"]) for record in records)
    loot_table_ids = sorted({record["loot_table_id"] for record in records if record.get("loot_table_id")})
    quest_record = ctx.spawn_by_id["MAN-BM-SPAWN_BM_05_QUEST"]
    ring_match = re.search(r"Ø\s*(\d+)", quest_record["condition"])
    if not ring_match:
        raise PipelineError("MAN-BM-SPAWN_BM_05_QUEST: missing boss ring diameter in condition")
    ring_diameter = int(ring_match.group(1))
    definition = {
        "bossId": "BOSS_MANG_COT",
        "referenceLevel": reference_level,
        "levelBand": {"min": levels_min, "max": levels_max},
        "spawnRecordIds": spawn_record_ids,
        "baseHp": base_hp,
        "hpFactor": hp_factor,
        "hpSolo": _number(hp_solo),
        "hpParty2": _number(hp_party2),
        "partyScalingFormula": "baseHp * 35 * (1 + 0.65 * (partySize - 1))",
        "partySizeRange": {"min": 1, "max": 3},
        "attackMultiplier": 2.0,
        "attacks": [
            {
                "attackId": "ATK_MANG_COT_SWEEP",
                "shape": "CONE",
                "coneAngleDegrees": 120,
                "rangeWu": 8,
                "telegraphSeconds": 0.9,
                "damageMultiplier": 1.2,
                "recoverySeconds": 0.8,
                "cooldownSeconds": 4,
            },
            {
                "attackId": "ATK_MANG_COT_DIVE",
                "shape": "CIRCLE",
                "radiusWu": 4,
                "telegraphSeconds": 1.2,
                "damageMultiplier": 1.5,
                "recoverySeconds": 1,
                "cooldownSeconds": 9,
            },
            {
                "attackId": "ATK_MANG_COT_BUBBLE_RING",
                "shape": "ANNULUS",
                "innerRadiusWu": 3,
                "outerRadiusWu": 7,
                "telegraphSeconds": 1,
                "damageMultiplier": 1.3,
                "recoverySeconds": 1,
                "cooldownSeconds": 12,
            },
        ],
        "attackPriority": "C>B>A",
        "telegraphOverlap": False,
        "phases": [
            {"phase": 2, "hpThresholdFraction": 0.6, "recoveryMultiplier": 0.8},
            {"phase": 3, "hpThresholdFraction": 0.3, "safePadCount": 2},
        ],
        "arena": {
            "ringDiameterWu": ring_diameter,
            "anchor": {
                "xWu": _number(float(quest_record["x_wu"])),
                "yWu": _number(float(quest_record["y_wu"])),
            },
        },
        "lootTableIds": loot_table_ids,
    }

    def fill(prov):
        _add_tree(prov, definition, "/bossId", "ART_BIBLE", "12", transform="verbatim")
        _add_tree(prov, definition, "/referenceLevel", "P1_RESOLUTION", "2", transform="verbatim")
        _add_tree(prov, definition, "/levelBand", "SPAWN_MANIFEST", "", transform="verbatim")
        _add_tree(prov, definition, "/spawnRecordIds", "SPAWN_MANIFEST", "", transform="verbatim")
        _add_tree(prov, definition, "/baseHp", "ART_BIBLE", "12", transform="base_formula_at_reference_level")
        _add_tree(prov, definition, "/hpFactor", "P1_RESOLUTION", "2", transform="boss_table_override_applied_once")
        _add_tree(prov, definition, "/hpSolo", "P1_RESOLUTION", "2", transform="derived_formula")
        _add_tree(prov, definition, "/hpParty2", "P1_RESOLUTION", "2", transform="derived_formula")
        _add_tree(prov, definition, "/partyScalingFormula", "P1_RESOLUTION", "2", transform="verbatim")
        _add_tree(prov, definition, "/partySizeRange", "SPAWN_MANIFEST", "MAN-BM-SPAWN_BM_05_QUEST", transform="verbatim")
        _add_tree(prov, definition, "/attackMultiplier", "ART_BIBLE", "12", transform="verbatim")
        _add_tree(prov, definition, "/attacks", "PRODUCTION_RULES", "4", transform="verbatim")
        _add_tree(prov, definition, "/attackPriority", "PRODUCTION_RULES", "4", transform="verbatim")
        _add_tree(prov, definition, "/telegraphOverlap", "PRODUCTION_RULES", "4", transform="verbatim")
        _add_tree(prov, definition, "/phases", "PRODUCTION_RULES", "4", transform="verbatim")
        _add_tree(prov, definition, "/arena", "MAP_ATLAS", "Map-01-Ben-Mua", transform="verbatim")
        _add_tree(prov, definition, "/lootTableIds", "SPAWN_MANIFEST", "", transform="aggregated_manifest_lookup")

    unresolved = [
        _unresolved(ctx, "/encounterLevel", "P1 level 10 is an illustrative calculation, not a chosen encounter level.", "MISSING", "P1_RESOLUTION", "2"),
        _unresolved(ctx, "/baseAttack", "Art Bible gives the boss attack multiplier but no resolved base attack.", "MISSING", "ART_BIBLE", "12"),
        _unresolved(ctx, "/defense", "Art Bible gives no boss defense profile.", "MISSING", "ART_BIBLE", "12"),
        _unresolved(ctx, "/partyScalingRounding", "P1 does not choose rounding for party-scaled HP.", "MISSING", "P1_RESOLUTION", "2"),
        _unresolved(ctx, "/attackDescriptors", "Phase guard, interruptible, damage type and exact hit window are not specified per boss attack.", "MISSING", "PRODUCTION_RULES", "4"),
        _unresolved(ctx, "/phases/1/safePadPositions", "Rules require two safe pads outside the bubble ring but give no positions or geometry.", "MISSING", "PRODUCTION_RULES", "4"),
    ]
    return _candidate(
        "BOSS-BOSS_MANG_COT",
        "BOSS_REFERENCE",
        "BOSS_MANG_COT",
        BOSS_SCHEMA_PATH,
        definition,
        build_provenance(ctx, "BOSS-BOSS_MANG_COT", definition, fill),
        unresolved,
    )


ITEM_REF_SPECS = [
    {
        "referenceId": "ITEM_REF_P00_01_CHEST",
        "candidateId": "ITEM-REF-P00-01-CHEST",
        "questId": "P00-01",
        "sourceToken": "áo Thường",
        "resolution": "RESOLVED",
        "resolvedItemId": "EQ-MK-CHEST-T1-R-COMMON",
    },
    {
        "referenceId": "ITEM_REF_P00_02_POTION",
        "candidateId": "ITEM-REF-P00-02-POTION",
        "questId": "P00-02",
        "sourceToken": "thuốc",
        "resolution": "UNRESOLVED",
        "candidateItemIds": ["POT-HP-01", "POT-MP-01"],
        "reason": "The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one.",
    },
    {
        "referenceId": "ITEM_REF_P00_03_SHOES",
        "candidateId": "ITEM-REF-P00-03-SHOES",
        "questId": "P00-03",
        "sourceToken": "giày",
        "resolution": "UNRESOLVED",
        "reason": "T1 footwear exists for all five classes; the generic shoes reward still needs an explicit class/rarity resolution policy.",
    },
    {
        "referenceId": "ITEM_REF_P00_03_POTION",
        "candidateId": "ITEM-REF-P00-03-POTION",
        "questId": "P00-03",
        "sourceToken": "thuốc",
        "resolution": "UNRESOLVED",
        "candidateItemIds": ["POT-HP-01", "POT-MP-01"],
        "reason": "The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one.",
    },
    {
        "referenceId": "ITEM_REF_P00_04_POTION",
        "candidateId": "ITEM-REF-P00-04-POTION",
        "questId": "P00-04",
        "sourceToken": "thuốc",
        "resolution": "UNRESOLVED",
        "candidateItemIds": ["POT-HP-01", "POT-MP-01"],
        "reason": "The generic token 'thuốc' matches both POT-HP-01 and POT-MP-01; the quest does not choose one.",
    },
    {
        "referenceId": "ITEM_REF_P00_05_CLASS_WEAPON",
        "candidateId": "ITEM-REF-P00-05-CLASS-WEAPON",
        "questId": "P00-05",
        "sourceToken": "EQ-[CLASS]-WEAPON-T1-R-COMMON",
        "resolution": "UNRESOLVED",
        "reason": "The reward is a class token, not one item ID; substituting Minh Kiếm would invent the player's class.",
    },
]

ITEM_CATEGORY_MAP = {
    "Trang bị / giáp": "EQUIPMENT_ARMOR",
    "Trang bị / vũ khí": "EQUIPMENT_WEAPON",
    "Trang bị / phụ kiện": "EQUIPMENT_ACCESSORY",
    "Tiêu hao": "CONSUMABLE",
    "Nguyên liệu": "MATERIAL",
}

ITEM_RARITY_MAP = {
    "Thường": "COMMON",
    "Tinh": "REFINED",
    "Linh": "SPIRIT",
    "Huyền": "ARCANE",
    "Cổ Vật": "RELIC",
    "Fixed": "FIXED",
}


def build_item_candidates(ctx: Context) -> list[dict]:
    candidates = []
    for original in ITEM_REF_SPECS:
        spec = dict(original)
        if spec["referenceId"] == "ITEM_REF_P00_03_SHOES":
            spec["candidateItemIds"] = sorted(i for i,row in ctx.item_master_by_id.items()
                                             if row["slot"] == "Giày" and row["required_level"] == "1")
        if spec["referenceId"] == "ITEM_REF_P00_05_CLASS_WEAPON":
            spec["resolution"] = "CLASS_CONDITIONAL"
            spec["classCandidates"] = sorted(
                [{"classId":row["class_id"],"itemId":i} for i,row in ctx.item_rarity_by_id.items()
                 if row["category"] == "Trang bị / vũ khí" and row["required_level"] == "1" and row["rarity_pool"] == "Thường"],
                key=lambda x:x["classId"])
        definition = {
            "referenceId": spec["referenceId"],
            "questId": spec["questId"],
            "sourceToken": spec["sourceToken"],
            "resolution": spec["resolution"],
        }
        if spec["resolution"] == "RESOLVED":
            item = ctx.item_by_id[spec["resolvedItemId"]]
            category = ITEM_CATEGORY_MAP.get(item.get("category", ""))
            rarity = ITEM_RARITY_MAP.get(item.get("rarity_pool", ""))
            if not category or not rarity:
                raise PipelineError(f"{spec['resolvedItemId']}: cannot map catalog category/rarity")
            definition.update(
                {
                    "resolvedItemId": spec["resolvedItemId"],
                    "category": category,
                    "catalogSlotVi": item["slot"],
                    "requiredLevel": int(item["required_level"]),
                    "rarity": rarity,
                }
            )
        if "candidateItemIds" in spec:
            definition["candidateItemIds"] = list(spec["candidateItemIds"])
        if "classCandidates" in spec:
            definition["classCandidates"] = spec["classCandidates"]

        def fill(prov, spec=spec, definition=definition):
            _add_tree(prov, definition, "/referenceId", "QUEST_SPEC", spec["questId"], transform="proposed_stable_id")
            _add_tree(prov, definition, "/questId", "QUEST_SPEC", spec["questId"], transform="verbatim")
            _add_tree(prov, definition, "/sourceToken", "QUEST_SPEC", spec["questId"], transform="transcribed")
            _add_tree(prov, definition, "/resolution", "ITEM_RARITY" if spec["resolution"] == "RESOLVED" else "QUEST_SPEC", spec["questId"] if spec["resolution"] != "RESOLVED" else "", transform="resolution_state")
            if spec["resolution"] == "RESOLVED":
                _add_tree(prov, definition, "/resolvedItemId", "ITEM_RARITY", spec["resolvedItemId"], transform="catalog_lookup")
                _add_tree(prov, definition, "/category", "ITEM_RARITY", spec["resolvedItemId"], transform="mapped_to_schema_enum")
                _add_tree(prov, definition, "/catalogSlotVi", "ITEM_RARITY", spec["resolvedItemId"], transform="verbatim")
                _add_tree(prov, definition, "/requiredLevel", "ITEM_RARITY", spec["resolvedItemId"], transform="verbatim")
                _add_tree(prov, definition, "/rarity", "ITEM_RARITY", spec["resolvedItemId"], transform="mapped_to_schema_enum")
            if "candidateItemIds" in spec:
                _add_tree(prov, definition, "/candidateItemIds", "ITEM_MASTER", "/".join(spec["candidateItemIds"]), transform="catalog_lookup")
            if "classCandidates" in spec:
                _add_tree(prov, definition, "/classCandidates", "ITEM_RARITY", "T1-COMMON-WEAPONS", transform="catalog_class_lookup")

        unresolved = []
        if spec["resolution"] == "UNRESOLVED":
            unresolved.append(
                _unresolved(ctx, "/resolvedItemId", spec["reason"], "MISSING", "QUEST_SPEC", spec["questId"])
            )
        candidates.append(
            _candidate(
                spec["candidateId"],
                "ITEM_REFERENCE",
                spec["referenceId"],
                ITEM_SCHEMA_PATH,
                definition,
                build_provenance(ctx, spec["candidateId"], definition, fill),
                unresolved,
            )
        )
    return candidates


def build_candidates(ctx: Context) -> list[dict]:
    candidates = []
    candidates.extend(build_quest_candidates(ctx))
    candidates.extend(build_objective_map_candidates(ctx))
    candidates.append(build_actor_candidate(ctx))
    candidates.extend(build_mob_candidates(ctx))
    candidates.append(build_boss_candidate(ctx))
    candidates.extend(build_item_candidates(ctx))
    candidates.sort(key=lambda item: (KIND_ORDER[item["kind"]], item["candidateId"]))
    return candidates
