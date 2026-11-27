#!/usr/bin/env python3
"""Core source loading and provenance helpers for the Bến Mưa compiler.

The compiler reads only canonical documentation, CSV tables, schemas and
examples. It never writes canonical content and never activates runtime data.
Every supplied field carries source/version/units/transform provenance. Any
field that cannot be sourced is omitted and recorded as a blocking unresolved
entry instead of being defaulted to zero.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "Implementation/Tools/ContentPipeline/schemas"
QUEST_SCHEMA_PATH = "Implementation/Content/Schemas/QuestDefinition.schema.json"
ACTOR_SCHEMA_PATH = f"{SCHEMA_REL}/actor_profile.schema.json"
MOB_SCHEMA_PATH = f"{SCHEMA_REL}/mob_profile.schema.json"
BOSS_SCHEMA_PATH = f"{SCHEMA_REL}/boss_reference.schema.json"
ITEM_SCHEMA_PATH = f"{SCHEMA_REL}/item_reference.schema.json"
OBJECTIVE_MAP_SCHEMA_PATH = f"{SCHEMA_REL}/objective_map.schema.json"
BUNDLE_SCHEMA_PATH = f"{SCHEMA_REL}/candidate_bundle.schema.json"
OUTPUT_REL = "Implementation/Content/BuildCandidates/BEN_MUA/candidates.json"

REFERENCE_LEVEL = 5
BOSS_REFERENCE_LEVEL = 10
METERS_PER_WU = 0.5


class PipelineError(Exception):
    """Input content is structurally invalid or cannot be compiled."""


class PipelineEnvironmentError(Exception):
    """A required file, directory or CLI argument is missing or unreadable."""


def source_bytes(raw: bytes) -> bytes:
    """Canonical text digest: UTF-8 without BOM, LF on every checkout OS."""
    return raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").encode("utf-8")


@dataclass(frozen=True)
class SourceSpec:
    path: str
    version: str


SOURCE_SPECS = {
    "P1_RESOLUTION": SourceSpec("docs/production/P1_Design_Resolution_20261029_vi.md", "2026-10-29"),
    "PRODUCTION_RULES": SourceSpec("docs/production/Production_Rules_Complete_v1_vi.md", "v1-2026-10-28"),
    "ART_BIBLE": SourceSpec("docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md", "v2.0"),
    "QUEST_SPEC": SourceSpec("docs/production/Quest_and_Narrative_Production_Spec_vi.md", "v1"),
    "QUEST_DIALOGUE": SourceSpec("docs/production/Quest_Dialogue_Production_Data_vi.csv", "v1-VI_EDITED_P1"),
    "MAP_ATLAS": SourceSpec("docs/production/Map_Production_Atlas_vi.md", "v1.0"),
    "SPAWN_MANIFEST": SourceSpec("docs/production/World_Spawn_Gathering_Manifest_vi.csv", "v1"),
    "NPC_REGISTRY": SourceSpec("docs/production/NPC_Actor_Production_Registry_vi.csv", "v1"),
    "ITEM_MASTER": SourceSpec("docs/production/Item_Master_Catalog_vi.csv", "v1"),
    "ITEM_RARITY": SourceSpec("docs/production/Item_Rarity_Variant_Catalog_vi.csv", "v1"),
    "PRODUCTION_AUDIT": SourceSpec("docs/production/Production_Content_Audit_20261030_vi.md", "2026-10-30"),
    "RUNTIME_PRECISION": SourceSpec("docs/production/Runtime_State_and_Catalog_Precision_vi.md", "DEC-023"),
    "DECISIONS": SourceSpec("docs/production/Production_Decision_Register_vi.md", "DEC-001..023"),
    "QUEST_SCHEMA": SourceSpec("Implementation/Content/Schemas/QuestDefinition.schema.json", "v1"),
    "ITEM_SCHEMA": SourceSpec("Implementation/Content/Schemas/ItemDefinition.schema.json", "v1"),
    "QUEST_EXAMPLE_P00_01": SourceSpec("Implementation/Content/Examples/QuestDefinition/P00-01.json", "v1"),
    "SPAWN_EXAMPLE_BM_04": SourceSpec("Implementation/Content/Examples/SpawnDefinition/MAN-BM-SPAWN_BM_04.json", "v1"),
    "COMPLETION_V1": SourceSpec("Implementation/Content/DesignBaselines/completion_v1.json", "v1"),
    "LEVEL_PROGRESSION": SourceSpec("Implementation/Content/DesignBaselines/level_progression_v1.json", "v1"),
    "MAP_BOUNDS": SourceSpec("Implementation/Content/map_bounds.json", "v1"),
    "MAP_EXAMPLE_BEN_MUA": SourceSpec("Implementation/Content/Examples/MapDefinition/MAP_BEN_MUA.json", "v1"),
    "CLASS_EXAMPLE_MINH_KIEM": SourceSpec("Implementation/Content/Examples/ClassDefinition/CLASS_MINH_KIEM.json", "v1"),
    "SKILL_EXAMPLE_SK_01": SourceSpec("Implementation/Content/Examples/SkillDefinition/SK-MK-01.json", "v1"),
    "SKILL_EXAMPLE_SK_02": SourceSpec("Implementation/Content/Examples/SkillDefinition/SK-MK-02.json", "v1"),
    "SKILL_EXAMPLE_SK_03": SourceSpec("Implementation/Content/Examples/SkillDefinition/SK-MK-03.json", "v1"),
}

KIND_ORDER = {
    "QUEST": 0,
    "OBJECTIVE_MAP": 1,
    "ACTOR_PROFILE": 2,
    "MOB_PROFILE": 3,
    "BOSS_REFERENCE": 4,
    "ITEM_REFERENCE": 5,
}

DESIGN_ID_RE = re.compile(
    r"\b(?:OBJ|NPC|MOB|BOSS|WAVE|SPAWN|MAP|ITEM|SK|EQ|POT|MAT|LT|ENT|MAN|CLASS|ACTOR|GRAPH|DLG)\s*[-_][A-Z0-9]+[A-Z0-9_-]*\b"
)


@dataclass
class Context:
    root: Path
    sources: dict[str, dict] = field(default_factory=dict)
    texts: dict[str, str] = field(default_factory=dict)
    rows: dict[str, list[dict]] = field(default_factory=dict)
    jsons: dict[str, dict] = field(default_factory=dict)
    quest_ids: set[str] = field(default_factory=set)
    npc_by_id: dict[str, dict] = field(default_factory=dict)
    map_ids: set[str] = field(default_factory=set)
    bounds: dict[str, dict] = field(default_factory=dict)
    item_master_by_id: dict[str, dict] = field(default_factory=dict)
    item_rarity_by_id: dict[str, dict] = field(default_factory=dict)
    item_by_id: dict[str, dict] = field(default_factory=dict)
    skill_ids: set[str] = field(default_factory=set)
    class_ids: set[str] = field(default_factory=set)
    class_skills: dict[str, list[str]] = field(default_factory=dict)
    spawn_by_id: dict[str, dict] = field(default_factory=dict)
    mob_ids: set[str] = field(default_factory=set)
    boss_ids: set[str] = field(default_factory=set)
    loot_ids: set[str] = field(default_factory=set)
    design_ids: set[str] = field(default_factory=set)
    currency_ids: set[str] = field(default_factory=set)
    dialogue_by_quest: dict[str, list[dict]] = field(default_factory=dict)

    def source_entry(self, source_id: str) -> dict:
        if source_id not in self.sources:
            raise PipelineError(f"unknown sourceId {source_id!r}")
        return self.sources[source_id]

    def source_ref(self, source_id: str, fragment: str = "") -> str:
        entry = self.source_entry(source_id)
        base = entry["path"]
        if not fragment:
            return base
        return base + (fragment if fragment.startswith("#") else "#" + fragment)

    def source_version(self, source_id: str) -> str:
        return self.source_entry(source_id)["version"]

    def bounds_for(self, map_id: str) -> dict:
        if map_id in self.bounds.get("overrides", {}):
            return self.bounds["overrides"][map_id]
        return self.bounds["defaultBounds"]


def _unique_rows(rows: list[dict], key: str, label: str) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for row in rows:
        value = row.get(key, "")
        if not value:
            raise PipelineError(f"{label}: empty {key}")
        if value in out:
            raise PipelineError(f"{label}: duplicate {key} {value!r}")
        out[value] = row
    return out


def _load_json(text: str, label: str) -> dict:
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise PipelineEnvironmentError(f"{label}: invalid JSON ({exc})") from exc
    if not isinstance(value, dict):
        raise PipelineEnvironmentError(f"{label}: expected a JSON object")
    return value


def load_context(root: Path | str = DEFAULT_ROOT) -> Context:
    root = Path(root).resolve()
    ctx = Context(root=root)

    for source_id, spec in SOURCE_SPECS.items():
        path = root / spec.path
        if not path.resolve().is_relative_to(root):
            raise PipelineEnvironmentError(f"source escapes root: {spec.path}")
        if not path.is_file():
            raise PipelineEnvironmentError(f"required source not found: {spec.path}")
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise PipelineEnvironmentError(f"cannot read {spec.path}: {exc}") from exc
        try:
            normalized = source_bytes(raw)
        except UnicodeDecodeError as exc:
            raise PipelineEnvironmentError(f"{spec.path}: not UTF-8 ({exc})") from exc
        digest = "sha256:" + hashlib.sha256(normalized).hexdigest()
        ctx.sources[source_id] = {
            "sourceId": source_id,
            "path": spec.path,
            "version": spec.version,
            "sha256": digest,
            "normalization": "UTF8_NO_BOM_LF",
        }
        try:
            text = normalized.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise PipelineEnvironmentError(f"{spec.path}: not UTF-8 ({exc})") from exc
        ctx.texts[source_id] = text

    csv_sources = [
        "QUEST_DIALOGUE",
        "SPAWN_MANIFEST",
        "NPC_REGISTRY",
        "ITEM_MASTER",
        "ITEM_RARITY",
    ]
    for source_id in csv_sources:
        reader = csv.DictReader(io.StringIO(ctx.texts[source_id], newline=""))
        if not reader.fieldnames:
            raise PipelineEnvironmentError(f"{SOURCE_SPECS[source_id].path}: missing CSV header")
        ctx.rows[source_id] = list(reader)

    json_sources = [sid for sid, spec in SOURCE_SPECS.items() if spec.path.endswith(".json")]
    for source_id in json_sources:
        ctx.jsons[source_id] = _load_json(ctx.texts[source_id], SOURCE_SPECS[source_id].path)

    dialogue = ctx.rows["QUEST_DIALOGUE"]
    seen_dialogue_rows = set()
    for row in dialogue:
        key = (row.get("node_id", ""), row.get("choice_id", ""))
        if key in seen_dialogue_rows:
            raise PipelineError(
                "Quest_Dialogue_Production_Data_vi.csv: duplicate dialogue row "
                f"node_id={key[0]!r} choice_id={key[1]!r}"
            )
        seen_dialogue_rows.add(key)
    ctx.quest_ids = {row["quest_id"] for row in dialogue if row.get("quest_id")}
    for row in dialogue:
        ctx.dialogue_by_quest.setdefault(row["quest_id"], []).append(row)

    manifest = ctx.rows["SPAWN_MANIFEST"]
    ctx.spawn_by_id = _unique_rows(manifest, "record_id", "World_Spawn_Gathering_Manifest_vi.csv")
    ctx.loot_ids = {row["loot_table_id"] for row in manifest if row.get("loot_table_id")}

    ctx.npc_by_id = _unique_rows(ctx.rows["NPC_REGISTRY"], "npc_id", "NPC_Actor_Production_Registry_vi.csv")

    ctx.item_master_by_id = _unique_rows(ctx.rows["ITEM_MASTER"], "item_id", "Item_Master_Catalog_vi.csv")
    ctx.item_rarity_by_id = _unique_rows(ctx.rows["ITEM_RARITY"], "item_id", "Item_Rarity_Variant_Catalog_vi.csv")
    for item_id, row in ctx.item_master_by_id.items():
        if not item_id.startswith("EQ-") and ctx.item_rarity_by_id.get(item_id) != row:
            raise PipelineError(f"fixed item catalog drift: {item_id} (DEC-023)")
    ctx.item_by_id = dict(ctx.item_master_by_id)
    ctx.item_by_id.update(ctx.item_rarity_by_id)

    for source_id in ["SKILL_EXAMPLE_SK_01", "SKILL_EXAMPLE_SK_02", "SKILL_EXAMPLE_SK_03"]:
        skill_id = ctx.jsons[source_id].get("skillId")
        if not skill_id:
            raise PipelineError(f"{SOURCE_SPECS[source_id].path}: missing skillId")
        ctx.skill_ids.add(skill_id)

    class_doc = ctx.jsons["CLASS_EXAMPLE_MINH_KIEM"]
    class_id = class_doc.get("classId")
    if not class_id:
        raise PipelineError("CLASS_MINH_KIEM.json: missing classId")
    ctx.class_ids.add(class_id)
    ctx.class_skills[class_id] = list(class_doc.get("startingSkillIds", []))

    map_bounds = ctx.jsons["MAP_BOUNDS"]
    ctx.map_ids = set(map_bounds.get("knownMapIds", []))
    if "MAP_BEN_MUA" not in ctx.map_ids:
        raise PipelineError("map_bounds.json: MAP_BEN_MUA missing from knownMapIds")
    ctx.bounds = map_bounds

    for row in manifest:
        for entity_id in (row.get("entity_id") or "").split("|"):
            if entity_id.startswith("MOB_"):
                ctx.mob_ids.add(entity_id)
            elif entity_id.startswith("BOSS_"):
                ctx.boss_ids.add(entity_id)

    for text in ctx.texts.values():
        for match in DESIGN_ID_RE.finditer(text):
            identifier = match.group()
            ctx.design_ids.add(identifier)
            # The atlas explicitly writes e.g. OBJ_BM_WATER_RIPPLE_01/02/03.
            # Expand only adjacent numeric suffix shorthand, never invent IDs
            # from a count, prose name, range or unrelated slash expression.
            suffix = re.search(r"([_-])(\d+)$", identifier)
            if suffix:
                continuation = re.match(r"(?:/\d{%d})+" % len(suffix[2]), text[match.end():])
                if continuation:
                    prefix = identifier[:suffix.start(2)]
                    ctx.design_ids.update(prefix + value for value in continuation[0].split('/')[1:])
    ctx.mob_ids.update(x for x in ctx.design_ids if x.startswith("MOB_"))
    ctx.boss_ids.update(x for x in ctx.design_ids if x.startswith("BOSS_"))
    ctx.currency_ids.add("COIN")

    # Human-transcribed graph/geometry constants must be reviewed again when
    # their inputs change. Re-hashing new prose without re-transcribing values
    # would misleadingly certify stale numbers as current source data.
    lock_path = Path(__file__).with_name("transcription_lock.json")
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PipelineEnvironmentError(f"transcription lock unavailable: {exc}") from exc
    actual = {source_id: entry["sha256"] for source_id, entry in ctx.sources.items()}
    if lock.get("sources") != actual:
        changed = sorted(source_id for source_id in set(actual) | set(lock.get("sources", {}))
                         if lock.get("sources", {}).get(source_id) != actual.get(source_id))
        raise PipelineError("source transcription review required: " + ", ".join(changed))

    return ctx


def iter_leaves(value, base: str = ""):
    if isinstance(value, dict):
        if not value:
            yield (base or "/", value)
            return
        for key, child in value.items():
            yield from iter_leaves(child, f"{base}/{key}")
    elif isinstance(value, list):
        if not value:
            yield (base or "/", value)
            return
        for index, child in enumerate(value):
            yield from iter_leaves(child, f"{base}/{index}")
    else:
        yield (base or "/", value)


_ID_ARRAYS = {
    "targetIds",
    "sourceIds",
    "itemIds",
    "spawnRecordIds",
    "lootTableIds",
    "startingSkillIds",
    "candidateItemIds",
    "prerequisiteQuestIds",
    "unlocks",
}


def leaf_units(path: str, value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, list):
        return "list"
    if isinstance(value, dict):
        return "object"
    name = path.rsplit("/", 1)[-1]
    parent = path.rsplit("/", 2)[-2] if path.count("/") >= 2 else ""
    if parent in _ID_ARRAYS:
        return "id"
    if name in {"schemaVersion"}:
        return "schema_version"
    if name in {"level", "referenceLevel", "requiredLevel"}:
        return "level"
    if name in {"min", "max"}:
        return "level" if parent == "levelBand" else "count"
    if name in {"phase"}:
        return "ordinal"
    if name in {"count", "quantity", "partySize", "safePadCount"}:
        return "count"
    if name == "amount":
        return "currency_units"
    if name.endswith("MetersPerSecond"):
        return "m/s"
    if name.endswith("WuPerSecond"):
        return "WU/s"
    if name.endswith("Meters"):
        return "m"
    if name.endswith("Wu"):
        return "WU"
    if name.endswith("Seconds"):
        return "seconds"
    if name.endswith("Degrees"):
        return "degrees"
    if name in {
        "damageMultiplier",
        "hpFactor",
        "attackMultiplier",
        "recoveryMultiplier",
        "hpThresholdFraction",
        "multiplier",
    }:
        return "fraction"
    if name in {
        "hp",
        "maxHp",
        "maxMp",
        "baseHp",
        "hpSolo",
        "hpParty2",
        "attack",
        "physicalAttack",
        "magicAttack",
        "defense",
        "armor",
    }:
        return "points"
    if name.endswith("Ids") or name.endswith("Id"):
        return "id"
    if name == "unlocks":
        return "id"
    if name.endswith("Key"):
        return "localization_key"
    if name == "sourceRef":
        return "source_reference"
    if name == "xpRule":
        return "rule_token"
    if name.endswith("Formula") or name == "formula":
        return "formula"
    if name == "attackPriority":
        return "priority_order"
    if name in {"sourceToken", "catalogSlotVi"}:
        return "text"
    if name in {
        "questType",
        "type",
        "kind",
        "status",
        "resolution",
        "eventType",
        "shape",
        "category",
        "rarity",
        "sharePolicy",
        "availability",
    }:
        return "enum"
    if isinstance(value, str):
        return "text"
    if isinstance(value, (int, float)):
        return "number"
    return "value"


def _lookup_pointer(value, pointer: str):
    if pointer in ("", "/"):
        return True, value
    current = value
    for part in pointer.strip("/").split("/"):
        if isinstance(current, dict):
            if part not in current:
                return False, None
            current = current[part]
        elif isinstance(current, list):
            try:
                index = int(part)
            except ValueError:
                return False, None
            if index < 0 or index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def _add_tree(prov, definition, prefix, source_id, fragment="", units=None, transform="verbatim"):
    found, value = _lookup_pointer(definition, prefix or "/")
    if not found:
        raise PipelineError(f"provenance prefix not found: {prefix}")
    base = "" if prefix in ("", "/") else prefix
    for path, child in iter_leaves(value, base):
        prov[path] = {
            "sourceId": source_id,
            "fragment": fragment,
            "units": units or leaf_units(path, child),
            "transform": transform,
        }


def build_provenance(ctx: Context, candidate_id: str, definition: dict, fill) -> list[dict]:
    prov: dict[str, dict] = {}
    fill(prov)
    leaves = dict(iter_leaves(definition))
    missing = sorted(set(leaves) - set(prov))
    extra = sorted(set(prov) - set(leaves))
    if missing:
        raise PipelineError(f"{candidate_id}: missing field provenance for {missing}")
    if extra:
        raise PipelineError(f"{candidate_id}: provenance for absent fields {extra}")
    out = []
    for path in sorted(prov):
        item = prov[path]
        out.append(
            {
                "path": path,
                "sourceId": item["sourceId"],
                "sourceRef": ctx.source_ref(item["sourceId"], item["fragment"]),
                "sourceVersion": ctx.source_version(item["sourceId"]),
                "units": item["units"],
                "transform": item["transform"],
            }
        )
    return out


def _unresolved(ctx: Context, path: str, reason: str, value_state: str, source_id: str, fragment="") -> dict:
    return {
        "path": path,
        "reason": reason,
        "blocking": True,
        "valueState": value_state,
        "sourceId": source_id,
        "sourceRef": ctx.source_ref(source_id, fragment),
        "sourceVersion": ctx.source_version(source_id),
    }


def _candidate(candidate_id, kind, target_id, target_schema, definition, prov, unresolved):
    ordered_unresolved = sorted(unresolved, key=lambda item: item["path"])
    blocking = any(item["blocking"] for item in ordered_unresolved)
    return {
        "candidateId": candidate_id,
        "kind": kind,
        "targetId": target_id,
        "targetSchema": target_schema,
        "status": "BLOCKED_UNRESOLVED" if blocking else "READY_FOR_REVIEW",
        "definition": definition,
        "fieldProvenance": prov,
        "unresolved": ordered_unresolved,
    }


def _quest_row(ctx: Context, quest_id: str, node_type: str) -> dict:
    for row in ctx.dialogue_by_quest.get(quest_id, []):
        if row.get("node_type") == node_type:
            return row
    raise PipelineError(f"quest {quest_id}: missing {node_type} dialogue node")


def _map_level_band(ctx: Context) -> dict:
    level_band = ctx.jsons["MAP_EXAMPLE_BEN_MUA"].get("levelBand")
    if not level_band:
        raise PipelineError("MAP_BEN_MUA.json: missing levelBand")
    return {"min": int(level_band["min"]), "max": int(level_band["max"])}


def _quest_source_ref(quest_id: str) -> str:
    return f"Quest_and_Narrative_Production_Spec_vi.md#{quest_id}"


QUEST_SPECS = {
    "P00-02": {
        "prereq": ["P00-01"],
        "objectives": [
            {
                "objectiveId": "OBJ_P00_02_RIPPLES",
                "type": "INTERACT",
                "targetIds": [
                    "OBJ_BM_WATER_RIPPLE_01",
                    "OBJ_BM_WATER_RIPPLE_02",
                    "OBJ_BM_WATER_RIPPLE_03",
                ],
                "count": 3,
                "targetSource": "MAP_ATLAS",
            },
            {
                "objectiveId": "OBJ_P00_02_CARPLING",
                "type": "KILL",
                "targetIds": ["MOB_CARPLING"],
                "count": 4,
                "targetSource": "QUEST_SPEC",
            },
            {
                "objectiveId": "OBJ_P00_02_REPORT",
                "type": "TALK",
                "targetIds": ["NPC_TA_VAN_KHANH"],
                "count": 1,
                "targetSource": "NPC_REGISTRY",
            },
        ],
        "rewards": None,
        "unlocks": None,
        "unresolved": [
            ("/rewards", "Quest text says XP and a potion but gives no exact XP token/amount and no exact potion item ID.", "MISSING", "QUEST_SPEC", "P00-02"),
            ("/unlocks", "Quest text says minimap/targeting unlock but gives no canonical unlock IDs.", "MISSING", "QUEST_SPEC", "P00-02"),
        ],
    },
    "P00-03": {
        "prereq": ["P00-02"],
        "objectives": [
            {
                "objectiveId": "OBJ_P00_03_WATERROOTS",
                "type": "KILL",
                "targetIds": ["MOB_WATERROOT"],
                "count": 3,
                "targetSource": "QUEST_SPEC",
                "presentUnresolved": [
                    (
                        "/type",
                        "Quest says destroy three Rễ Nước; the Map Atlas places interactive roots, so KILL versus INTERACT remains unresolved.",
                        "QUEST_SPEC",
                        "P00-03",
                    )
                ],
            },
            {
                "objectiveId": "OBJ_P00_03_RESCUE",
                "type": "INTERACT",
                "targetIds": ["NPC_BM_RESCUE_01", "NPC_BM_RESCUE_02"],
                "count": 2,
                "targetSource": "NPC_REGISTRY",
            },
        ],
        "rewards": None,
        "unlocks": ["P00-04"],
        "unresolved": [
            ("/objectives/2", "The dodge-one-wave step has no canonical QuestDefinition objective type or target ID.", "MISSING", "QUEST_SPEC", "P00-03"),
            ("/rewards", "T1 footwear exists in the catalog; the quest still needs class/rarity policy, potion choice and an exact XP rule or amount.", "MISSING", "QUEST_SPEC", "P00-03"),
        ],
    },
    "P00-04": {
        "prereq": ["P00-03"],
        "objectives": [
            {
                "objectiveId": "OBJ_P00_04_ESCORT",
                "type": "ESCORT",
                "targetIds": ["NPC_LYAN"],
                "count": 1,
                "targetSource": "MAP_ATLAS",
            },
            {
                "objectiveId": "OBJ_P00_04_WAVES",
                "type": "KILL",
                "targetIds": ["MOB_CARPLING", "MOB_WATERROOT"],
                "count": 6,
                "targetSource": "QUEST_SPEC",
            },
        ],
        "rewards": {"currency": [{"currencyId": "COIN", "amount": 30}]},
        "unlocks": ["P00-05"],
        "unresolved": [
            ("/rewards/xpRule", "Quest text says XP but gives no exact XP token/amount for P00-04.", "MISSING", "QUEST_SPEC", "P00-04"),
            ("/rewards/itemIds", "Quest text says a potion but gives no exact potion item ID.", "MISSING", "QUEST_SPEC", "P00-04"),
        ],
    },
    "P00-05": {
        "prereq": ["P00-04"],
        "objectives": [
            {
                "objectiveId": "OBJ_P00_05_BOSS",
                "type": "BOSS",
                "targetIds": ["BOSS_MANG_COT"],
                "count": 1,
                "targetSource": "ART_BIBLE",
            },
            {
                "objectiveId": "OBJ_P00_05_SEAL",
                "type": "INTERACT",
                "targetIds": ["OBJ_BM_SEAL"],
                "count": 1,
                "targetSource": "MAP_ATLAS",
            },
            {
                "objectiveId": "OBJ_P00_05_CLASS_CONFIRM",
                "type": "TALK",
                "targetIds": ["NPC_CLASS_TRIAL"],
                "count": 1,
                "targetSource": "NPC_REGISTRY",
            },
        ],
        "rewards": None,
        "unlocks": None,
        "unresolved": [
            ("/objectives/3", "Entering the boss ring has no canonical QuestDefinition objective type or target ID.", "MISSING", "QUEST_SPEC", "P00-05"),
            ("/rewards", "Reward token EQ-[CLASS]-WEAPON-T1-R-COMMON needs a class substitution; no XP amount/token is specified.", "MISSING", "QUEST_SPEC", "P00-05"),
            ("/unlocks", "Quest text says Thanh Lạc / Chapter I but gives no canonical unlock IDs.", "MISSING", "QUEST_SPEC", "P00-05"),
        ],
    },
}


def build_quest_candidates(ctx: Context) -> list[dict]:
    canonical = ctx.jsons["QUEST_EXAMPLE_P00_01"]

    def p00_01_fill(prov):
        _add_tree(prov, canonical, "/", "QUEST_EXAMPLE_P00_01", transform="copy_canonical_example")

    p00_01 = _candidate(
        "QUEST-P00-01",
        "QUEST",
        "P00-01",
        QUEST_SCHEMA_PATH,
        canonical,
        build_provenance(ctx, "QUEST-P00-01", canonical, p00_01_fill),
        [],
    )

    candidates = [p00_01]
    for quest_id, spec in QUEST_SPECS.items():
        offer = _quest_row(ctx, quest_id, "OFFER")
        turn_in = _quest_row(ctx, quest_id, "TURN_IN")
        graph_id = offer.get("graph_id")
        if not graph_id or graph_id != turn_in.get("graph_id"):
            raise PipelineError(f"{quest_id}: graphId missing or inconsistent in dialogue CSV")
        definition = {
            "schemaVersion": 1,
            "questId": quest_id,
            "titleKey": f"QUEST.{quest_id}.TITLE",
            "graphId": graph_id,
            "questType": "MAIN",
            "levelBand": _map_level_band(ctx),
            "startNpcId": offer["speaker_id"],
            "turnInNpcId": turn_in["speaker_id"],
            "prerequisiteQuestIds": list(spec["prereq"]),
            "objectives": [
                {
                    "objectiveId": obj["objectiveId"],
                    "type": obj["type"],
                    "targetIds": list(obj["targetIds"]),
                    "count": obj["count"],
                    "mapId": "MAP_BEN_MUA",
                }
                for obj in spec["objectives"]
            ],
        }
        if spec["rewards"] is not None:
            definition["rewards"] = spec["rewards"]
        if spec["unlocks"] is not None:
            definition["unlocks"] = list(spec["unlocks"])
        definition["sourceRef"] = _quest_source_ref(quest_id)

        def fill(prov, quest_id=quest_id, spec=spec, definition=definition):
            _add_tree(prov, definition, "/schemaVersion", "QUEST_SCHEMA", "/properties/schemaVersion", transform="verbatim")
            _add_tree(prov, definition, "/questId", "QUEST_SPEC", quest_id, transform="verbatim")
            _add_tree(prov, definition, "/titleKey", "QUEST_DIALOGUE", quest_id, transform="derived_stable_key")
            _add_tree(prov, definition, "/graphId", "QUEST_DIALOGUE", quest_id, transform="verbatim")
            _add_tree(prov, definition, "/questType", "QUEST_SPEC", "2", transform="mapped_to_schema_enum")
            _add_tree(prov, definition, "/levelBand", "MAP_EXAMPLE_BEN_MUA", "/levelBand", transform="verbatim")
            _add_tree(prov, definition, "/startNpcId", "QUEST_DIALOGUE", f"{quest_id}/OFFER", transform="verbatim")
            _add_tree(prov, definition, "/turnInNpcId", "QUEST_DIALOGUE", f"{quest_id}/TURN_IN", transform="verbatim")
            _add_tree(prov, definition, "/prerequisiteQuestIds", "QUEST_SPEC", "2", transform="transcribed")
            for index, obj in enumerate(spec["objectives"]):
                prefix = f"/objectives/{index}"
                _add_tree(prov, definition, prefix, "QUEST_SPEC", quest_id, transform="verbatim")
                _add_tree(prov, definition, f"{prefix}/objectiveId", "QUEST_SPEC", quest_id, transform="proposed_stable_id")
                _add_tree(prov, definition, f"{prefix}/type", "QUEST_SPEC", quest_id, transform="mapped_to_schema_enum")
                if obj["targetSource"] == "QUEST_SPEC":
                    target_fragment = quest_id
                elif obj["targetSource"] == "MAP_ATLAS":
                    target_fragment = "Map-01-Ben-Mua"
                elif obj["targetSource"] == "ART_BIBLE":
                    target_fragment = "12"
                else:
                    target_fragment = ""
                _add_tree(
                    prov,
                    definition,
                    f"{prefix}/targetIds",
                    obj["targetSource"],
                    target_fragment,
                    transform="transcribed",
                )
                _add_tree(prov, definition, f"{prefix}/mapId", "MAP_ATLAS", "Map-01-Ben-Mua", transform="verbatim")
            if spec["rewards"] is not None:
                _add_tree(prov, definition, "/rewards", "QUEST_SPEC", quest_id, transform="verbatim")
                if "currency" in spec["rewards"]:
                    _add_tree(prov, definition, "/rewards/currency", "QUEST_SPEC", quest_id, transform="verbatim")
            if spec["unlocks"] is not None:
                _add_tree(prov, definition, "/unlocks", "QUEST_SPEC", quest_id, transform="transcribed")
            _add_tree(prov, definition, "/sourceRef", "QUEST_SPEC", quest_id, transform="verbatim")

        unresolved = [
            _unresolved(ctx, path, reason, state, source_id, fragment)
            for path, reason, state, source_id, fragment in spec["unresolved"]
        ]
        # QOD-18 made activation mandatory. A full design candidate is not the
        # partial server runtime projection: never infer ACTIVE from its graph.
        unresolved.append(_unresolved(
            ctx, "/activation",
            "The runtime schema now requires ACTIVE/BLOCKED. This full design graph still needs a reviewed runtime migration and activation/gap policy; do not infer ACTIVE from a structurally valid candidate.",
            "MISSING", "QUEST_SCHEMA", "/properties/activation"))
        for index, obj in enumerate(spec["objectives"]):
            for suffix, reason, source_id, fragment in obj.get("presentUnresolved", []):
                unresolved.append(
                    _unresolved(ctx, f"/objectives/{index}{suffix}", reason, "PRESENT_UNRESOLVED", source_id, fragment)
                )
        candidates.append(
            _candidate(
                f"QUEST-{quest_id}",
                "QUEST",
                quest_id,
                QUEST_SCHEMA_PATH,
                definition,
                build_provenance(ctx, f"QUEST-{quest_id}", definition, fill),
                unresolved,
            )
        )
    return candidates
