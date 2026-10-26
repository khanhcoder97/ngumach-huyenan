#!/usr/bin/env python3
"""Validate production CSV and definition content with the standard library only.

Checks performed:
  * Manifest file: row count == 349, required columns present, record IDs
    unique, coordinates numeric, map IDs known, coordinates inside canonical
    map bounds (standard maps X 0..360 and Y 0..72 inclusive; MAP_THANG_LONG
    X 0..900 and Y 0..96 inclusive; the sole documented exception is the
    fishing anchor record_id=MAN-LT-FISHING-RE, map_id=MAP_LAM_TRIEU,
    entity_id=FISHING_SPOT_CA_RE at (158, -3)).
  * Manifest semantics: required fields non-empty, allowed record/design states,
    positive quantities, valid level bands/respawn values, composition totals,
    NPC/item/tool/drop references resolvable (NPC entity IDs must be listed as
    npc_id in NPC_Actor_Production_Registry_vi.csv).
  * Definition schemas: seven JSON schemas under Implementation/Content/Schemas
    with at least one example under Implementation/Content/Examples.
  * Definition references: class/skill/item/map/spawn/gathering/quest examples
    resolve against the source CSVs and the manifest.

Usage:
  python validate_content.py [--docs PATH] [--content PATH]

Exit codes:
  0  all checks passed
  1  validation failures found
  2  environment/usage error (missing directory or required file, bad input)
"""

import argparse
import csv
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from json_schema import validate as validate_json_schema

MANIFEST_ROW_COUNT = 349
MANIFEST_REQUIRED_COLUMNS = [
    "record_id",
    "map_id",
    "record_type",
    "entity_id",
    "x_wu",
    "y_wu",
]
MANIFEST_REQUIRED_NONEMPTY = [
    "record_id",
    "map_id",
    "record_type",
    "design_state",
    "entity_id",
    "display_name_vi",
    "condition",
    "respawn_policy",
    "art_ref",
    "source_ref",
]
COORD_COLUMNS = ["x_wu", "y_wu"]

# Canonical content rules: manifest positions are validated against these
# inclusive bounds (in WU), not against the more permissive water margin that
# map_bounds.json allows for definition-level checks.
CANONICAL_DEFAULT_BOUNDS = {"xMin": 0, "xMax": 360, "yMin": 0, "yMax": 72}
CANONICAL_MAP_BOUNDS = {
    "MAP_THANG_LONG": {"xMin": 0, "xMax": 900, "yMin": 0, "yMax": 96},
}
# Documented exception to the canonical bounds. Only this exact record
# (record_id, map_id, entity_id, x_wu, y_wu) is allowed outside the bounds.
MANIFEST_BOUNDS_EXCEPTIONS = {
    ("MAN-LT-FISHING-RE", "MAP_LAM_TRIEU", "FISHING_SPOT_CA_RE", 158.0, -3.0),
}

NPC_REGISTRY_FILE = "NPC_Actor_Production_Registry_vi.csv"
NPC_REGISTRY_ID_COLUMN = "npc_id"
ID_UNIQUENESS_FILES = [
    "Item_Master_Catalog_vi.csv",
    "Item_Rarity_Variant_Catalog_vi.csv",
    NPC_REGISTRY_FILE,
    "Currency_Production_Data_vi.csv",
    "Class_Passive_Production_Data_vi.csv",
]
ENCODING = "utf-8-sig"

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONTENT_DIR = PROJECT_ROOT / "Implementation" / "Content"
SCHEMA_DIR_NAME = "Schemas"
EXAMPLES_DIR_NAME = "Examples"
MAP_BOUNDS_FILE_NAME = "map_bounds.json"
SCHEMA_SUFFIX = ".schema.json"

ALLOWED_RECORD_TYPES = {"MOB_GROUP", "BOSS", "NPC", "GATHER_NODE", "INTERACTABLE"}
ALLOWED_DESIGN_STATES = {
    "ATLAS_ANCHOR",
    "ATLAS_QUEST_WAVE",
    "ACTIVITY_PLACEMENT",
    "ATLAS_SPAWN",
    "ATLAS_EVENT_POOL",
    "ATLAS_BOSS",
    "ACTIVITY_BOSS",
    "ATLAS_QUEST_ACTOR",
    "NEW_PROPOSED",
    "REPLACED",
    "CUT",
}
ALLOWED_PROFESSIONS = {"MINING", "HERBALISM", "LOGGING"}
ALLOWED_QUALITY_TIERS = {"I", "II", "III"}
LOOT_TABLE_RE = re.compile(r"^(LT_[A-Z0-9_]+|NONE)$")
COMPOSITION_PART_RE = re.compile(r"^([A-Z][A-Z0-9_]*)\s*(?:[×xX]\s*(\d+))?$")

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_ENVIRONMENT = 2


def read_rows(path, errors):
    """Read a CSV with utf-8-sig and csv.DictReader. Returns (fieldnames, rows)."""
    try:
        with path.open("r", encoding=ENCODING, newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                errors.append(f"{path.name}: file has no header row")
                return None, None
            fieldnames = [name.strip() for name in reader.fieldnames]
            rows = []
            for line_no, row in enumerate(reader, start=2):
                cleaned = {
                    (key.strip() if key else key): (value if value is not None else "")
                    for key, value in row.items()
                }
                rows.append((line_no, cleaned))
            return fieldnames, rows
    except FileNotFoundError:
        errors.append(f"{path}: file not found")
    except PermissionError:
        errors.append(f"{path}: permission denied")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: not valid {ENCODING} text ({exc})")
    except csv.Error as exc:
        errors.append(f"{path}: malformed CSV ({exc})")
    return None, None


def read_json(path, errors):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        errors.append(f"{path}: file not found")
    except PermissionError:
        errors.append(f"{path}: permission denied")
    except UnicodeDecodeError as exc:
        errors.append(f"{path}: not valid UTF-8 text ({exc})")
    except json.JSONDecodeError as exc:
        errors.append(f"{path}: malformed JSON ({exc})")
    return None


def find_manifest(docs_dir, errors):
    """Locate the single manifest CSV in the docs directory."""
    # Match case-insensitively because production files use "Manifest" while
    # POSIX globbing is case-sensitive.
    candidates = sorted(
        p for p in docs_dir.glob("*.csv") if p.is_file() and "manifest" in p.name.lower()
    )
    if not candidates:
        errors.append(
            f"{docs_dir}: no manifest CSV found (expected a CSV file whose "
            f"name contains 'manifest')"
        )
        return None
    if len(candidates) > 1:
        names = ", ".join(p.name for p in candidates)
        errors.append(
            f"{docs_dir}: ambiguous manifest, multiple candidates found: {names}"
        )
        return None
    return candidates[0]


def check_required_columns(path, fieldnames, errors):
    lowered = {name.lower(): name for name in fieldnames}
    missing = [col for col in MANIFEST_REQUIRED_COLUMNS if col.lower() not in lowered]
    if missing:
        errors.append(
            f"{path.name}: missing required column(s): {', '.join(missing)}; "
            f"found: {', '.join(fieldnames)}"
        )
        return False
    return True


def check_row_count(path, rows, errors):
    count = len(rows)
    if count != MANIFEST_ROW_COUNT:
        errors.append(
            f"{path.name}: row count is {count}, expected {MANIFEST_ROW_COUNT}"
        )
        return False
    return True


def check_record_ids(path, rows, errors):
    seen = {}
    ok = True
    for line_no, row in rows:
        value = (row.get("record_id") or "").strip()
        if not value:
            errors.append(f"{path.name}: line {line_no}: record_id is empty")
            ok = False
            continue
        if value in seen:
            errors.append(
                f"{path.name}: line {line_no}: duplicate record_id '{value}' "
                f"(first seen on line {seen[value]})"
            )
            ok = False
        else:
            seen[value] = line_no
    return ok


def check_numeric_coordinates(path, rows, errors):
    ok = True
    for line_no, row in rows:
        for column in COORD_COLUMNS:
            raw = (row.get(column) or "").strip()
            if not raw:
                errors.append(
                    f"{path.name}: line {line_no}: {column} is empty"
                )
                ok = False
                continue
            try:
                number = float(raw)
            except ValueError:
                errors.append(
                    f"{path.name}: line {line_no}: {column} is not numeric "
                    f"(value: '{raw}')"
                )
                ok = False
                continue
            if not math.isfinite(number):
                errors.append(
                    f"{path.name}: line {line_no}: {column} is not a finite "
                    f"number (value: '{raw}')"
                )
                ok = False
    return ok


def detect_id_column(fieldnames):
    """Pick the most likely ID column from a header: exact 'id', then '*_id',
    then any column with 'id' as a token."""
    by_lower = {name.lower(): name for name in fieldnames}
    if "id" in by_lower:
        return by_lower["id"]
    id_suffixed = [name for name in fieldnames if name.lower().endswith("_id")]
    if id_suffixed:
        return id_suffixed[0]
    token_match = [
        name for name in fieldnames if re.search(r"(^|_)id($|_)", name.lower())
    ]
    if token_match:
        return token_match[0]
    contains = [name for name in fieldnames if "id" in name.lower()]
    if contains:
        return contains[0]
    return None


def check_id_uniqueness(path, fieldnames, rows, errors):
    column = detect_id_column(fieldnames)
    if column is None:
        errors.append(
            f"{path.name}: no ID column detected in header "
            f"({', '.join(fieldnames)})"
        )
        return False
    seen = {}
    ok = True
    for line_no, row in rows:
        value = (row.get(column) or "").strip()
        if not value:
            errors.append(
                f"{path.name}: line {line_no}: ID column '{column}' is empty"
            )
            ok = False
            continue
        if value in seen:
            errors.append(
                f"{path.name}: line {line_no}: duplicate {column} '{value}' "
                f"(first seen on line {seen[value]})"
            )
            ok = False
        else:
            seen[value] = line_no
    return ok


def load_id_set(docs_dir, file_name, column, errors):
    path = docs_dir / file_name
    names, rows = read_rows(path, errors)
    if names is None:
        return set()
    if column not in names:
        errors.append(f"{file_name}: missing ID column '{column}'")
        return set()
    return {
        (row.get(column) or "").strip()
        for _, row in rows
        if (row.get(column) or "").strip()
    }


def load_map_bounds(content_dir, errors):
    path = content_dir / MAP_BOUNDS_FILE_NAME
    data = read_json(path, errors)
    if data is None:
        return None
    if not isinstance(data, dict):
        errors.append(f"{path.name}: top-level JSON value must be an object")
        return None
    default_bounds = data.get("defaultBounds")
    overrides = data.get("overrides", {})
    known_ids = data.get("knownMapIds")
    if not isinstance(default_bounds, dict):
        errors.append(f"{path.name}: defaultBounds must be an object")
        return None
    for key in ("xMin", "xMax", "yMin", "yMax"):
        if not isinstance(default_bounds.get(key), (int, float)):
            errors.append(f"{path.name}: defaultBounds.{key} must be numeric")
            return None
    if not isinstance(overrides, dict):
        errors.append(f"{path.name}: overrides must be an object")
        return None
    if not isinstance(known_ids, list) or not known_ids:
        errors.append(f"{path.name}: knownMapIds must be a non-empty array")
        return None
    if len(known_ids) != len(set(known_ids)):
        errors.append(f"{path.name}: knownMapIds contains duplicates")
    for map_id, bounds in overrides.items():
        if not isinstance(bounds, dict):
            errors.append(f"{path.name}: override for {map_id} must be an object")
            return None
        for key in ("xMin", "xMax", "yMin", "yMax"):
            if not isinstance(bounds.get(key), (int, float)):
                errors.append(
                    f"{path.name}: overrides.{map_id}.{key} must be numeric"
                )
                return None
    return {
        "default": default_bounds,
        "overrides": overrides,
        "known": set(known_ids),
    }


def bounds_for(map_id, map_config):
    return map_config["overrides"].get(map_id, map_config["default"])


def parse_int(value):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def parse_float(value):
    try:
        number = float(str(value).strip())
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def parse_composition(value):
    parts = [part.strip() for part in value.split("+") if part.strip()]
    if not parts:
        return None
    parsed = []
    for part in parts:
        match = COMPOSITION_PART_RE.match(part)
        if not match:
            return None
        parsed.append((match.group(1), int(match.group(2) or 1)))
    return parsed


def check_manifest_semantics(
    path, rows, map_config, item_ids, errors
):
    ok = True
    for line_no, row in rows:
        for column in MANIFEST_REQUIRED_NONEMPTY:
            if not (row.get(column) or "").strip():
                errors.append(
                    f"{path.name}: line {line_no}: {column} is empty"
                )
                ok = False

        record_type = (row.get("record_type") or "").strip()
        design_state = (row.get("design_state") or "").strip()
        map_id = (row.get("map_id") or "").strip()
        entity_ids = [
            value.strip()
            for value in (row.get("entity_id") or "").split("|")
            if value.strip()
        ]

        if record_type not in ALLOWED_RECORD_TYPES:
            errors.append(
                f"{path.name}: line {line_no}: unknown record_type '{record_type}'"
            )
            ok = False
        if design_state not in ALLOWED_DESIGN_STATES:
            errors.append(
                f"{path.name}: line {line_no}: unknown design_state '{design_state}'"
            )
            ok = False
        if map_id not in map_config["known"]:
            errors.append(
                f"{path.name}: line {line_no}: unknown map_id '{map_id}'"
            )
            ok = False

        quantity = parse_int(row.get("quantity"))
        level_min = parse_int(row.get("character_level_min"))
        level_max = parse_int(row.get("character_level_max"))
        respawn = parse_int(row.get("respawn_seconds"))
        if quantity is None or quantity < 1:
            errors.append(
                f"{path.name}: line {line_no}: quantity must be a positive integer"
            )
            ok = False
        if level_min is None or level_max is None:
            errors.append(
                f"{path.name}: line {line_no}: character level band must be integer"
            )
            ok = False
        elif not (1 <= level_min <= level_max <= 100):
            errors.append(
                f"{path.name}: line {line_no}: invalid level band "
                f"{level_min}..{level_max}"
            )
            ok = False
        if respawn is None or respawn < 0:
            errors.append(
                f"{path.name}: line {line_no}: respawn_seconds must be >= 0"
            )
            ok = False

        if record_type == "GATHER_NODE":
            profession = (row.get("gather_profession") or "").strip()
            quality_tier = (row.get("quality_tier") or "").strip()
            gather_item = (row.get("gather_item_id") or "").strip()
            tool_id = (row.get("tool_id") or "").strip()
            yield_min = parse_int(row.get("yield_min"))
            yield_max = parse_int(row.get("yield_max"))
            profession_level = parse_int(row.get("profession_level_required"))
            if profession not in ALLOWED_PROFESSIONS:
                errors.append(
                    f"{path.name}: line {line_no}: unknown gather_profession "
                    f"'{profession}'"
                )
                ok = False
            if quality_tier not in ALLOWED_QUALITY_TIERS:
                errors.append(
                    f"{path.name}: line {line_no}: unknown quality_tier "
                    f"'{quality_tier}'"
                )
                ok = False
            if gather_item not in item_ids:
                errors.append(
                    f"{path.name}: line {line_no}: gather_item_id "
                    f"'{gather_item}' does not resolve"
                )
                ok = False
            if tool_id not in item_ids:
                errors.append(
                    f"{path.name}: line {line_no}: tool_id '{tool_id}' "
                    f"does not resolve"
                )
                ok = False
            if (
                yield_min is None
                or yield_max is None
                or yield_min < 1
                or yield_max < yield_min
            ):
                errors.append(
                    f"{path.name}: line {line_no}: invalid yield range "
                    f"{yield_min}..{yield_max}"
                )
                ok = False
            if profession_level is None or profession_level < 1:
                errors.append(
                    f"{path.name}: line {line_no}: invalid "
                    f"profession_level_required"
                )
                ok = False
        elif record_type in {"MOB_GROUP", "BOSS"}:
            loot_table = (row.get("loot_table_id") or "").strip()
            if not LOOT_TABLE_RE.match(loot_table):
                errors.append(
                    f"{path.name}: line {line_no}: invalid loot_table_id "
                    f"'{loot_table}'"
                )
                ok = False
            composition = (row.get("composition") or "").strip()
            parsed = parse_composition(composition)
            if parsed is None:
                errors.append(
                    f"{path.name}: line {line_no}: cannot parse composition "
                    f"'{composition}'"
                )
                ok = False
            else:
                composition_total = sum(count for _, count in parsed)
                if composition_total != quantity:
                    errors.append(
                        f"{path.name}: line {line_no}: composition total "
                        f"{composition_total} != quantity {quantity}"
                    )
                    ok = False
                composition_ids = {entity_id for entity_id, _ in parsed}
                missing = composition_ids - set(entity_ids)
                if missing:
                    errors.append(
                        f"{path.name}: line {line_no}: composition IDs not in "
                        f"entity_id: {', '.join(sorted(missing))}"
                    )
                    ok = False

        for column in ("gather_item_id", "tool_id"):
            value = (row.get(column) or "").strip()
            if value and value not in item_ids:
                errors.append(
                    f"{path.name}: line {line_no}: {column} '{value}' "
                    f"does not resolve"
                )
                ok = False
        for drop_id in (row.get("drop_item_ids") or "").split("|"):
            drop_id = drop_id.strip()
            if drop_id and drop_id not in item_ids:
                errors.append(
                    f"{path.name}: line {line_no}: drop_item_ids "
                    f"'{drop_id}' does not resolve"
                )
                ok = False
    return ok


def check_manifest_npc_references(path, rows, npc_ids, errors):
    """Every manifest record with record_type NPC must reference entity IDs
    that are registered as npc_id in NPC_Actor_Production_Registry_vi.csv
    (set loaded UTF-8-safe via read_rows/load_id_set). Missing IDs are
    reported per line and summarised once at the end."""
    if not npc_ids:
        # Registry missing/unreadable: load_id_set already recorded the error.
        return True
    ok = True
    missing = []
    for line_no, row in rows:
        if (row.get("record_type") or "").strip() != "NPC":
            continue
        entity_ids = [
            value.strip()
            for value in (row.get("entity_id") or "").split("|")
            if value.strip()
        ]
        record_id = (row.get("record_id") or "").strip()
        for entity_id in entity_ids:
            if entity_id not in npc_ids:
                errors.append(
                    f"{path.name}: line {line_no}: record_id '{record_id}': "
                    f"NPC entity_id '{entity_id}' not found in "
                    f"{NPC_REGISTRY_FILE} ({NPC_REGISTRY_ID_COLUMN})"
                )
                missing.append(entity_id)
                ok = False
    if missing:
        unique = sorted(set(missing))
        errors.append(
            f"{path.name}: unresolved NPC entity_id(s) "
            f"({NPC_REGISTRY_FILE}): {', '.join(unique)}"
        )
    return ok


def canonical_bounds_for(map_id):
    return CANONICAL_MAP_BOUNDS.get(map_id, CANONICAL_DEFAULT_BOUNDS)


def is_documented_bounds_exception(row, x_wu, y_wu):
    """True only for the exact fishing anchor record MAN-LT-FISHING-RE."""
    key = (
        (row.get("record_id") or "").strip(),
        (row.get("map_id") or "").strip(),
        (row.get("entity_id") or "").strip(),
        x_wu,
        y_wu,
    )
    return key in MANIFEST_BOUNDS_EXCEPTIONS


def check_manifest_bounds(path, rows, map_config, errors):
    """Validate manifest positions against the canonical map bounds:
    standard maps X 0..360 and Y 0..72 inclusive; MAP_THANG_LONG
    X 0..900 and Y 0..96 inclusive. The only exception is the documented
    fishing anchor (MANIFEST_BOUNDS_EXCEPTIONS); every other out-of-range
    row is an error reported with its line number and map id."""
    ok = True
    for line_no, row in rows:
        map_id = (row.get("map_id") or "").strip()
        if map_id not in map_config["known"]:
            continue
        x_wu = parse_float(row.get("x_wu"))
        y_wu = parse_float(row.get("y_wu"))
        if x_wu is None or y_wu is None:
            continue
        bounds = canonical_bounds_for(map_id)
        if (
            bounds["xMin"] <= x_wu <= bounds["xMax"]
            and bounds["yMin"] <= y_wu <= bounds["yMax"]
        ):
            continue
        if is_documented_bounds_exception(row, x_wu, y_wu):
            continue
        errors.append(
            f"{path.name}: line {line_no}: map_id '{map_id}': position "
            f"({x_wu}, {y_wu}) outside canonical bounds "
            f"[X {bounds['xMin']}..{bounds['xMax']}, "
            f"Y {bounds['yMin']}..{bounds['yMax']}]"
        )
        ok = False
    return ok


def load_definition_data(content_dir, errors):
    schema_dir = content_dir / SCHEMA_DIR_NAME
    examples_dir = content_dir / EXAMPLES_DIR_NAME
    if not schema_dir.is_dir():
        errors.append(f"{schema_dir}: schema directory not found")
        return {}, {}
    if not examples_dir.is_dir():
        errors.append(f"{examples_dir}: examples directory not found")
        return {}, {}

    schemas = {}
    for path in sorted(schema_dir.glob(f"*{SCHEMA_SUFFIX}")):
        name = path.name[: -len(SCHEMA_SUFFIX)]
        schema = read_json(path, errors)
        if schema is not None:
            schemas[name] = (path, schema)
    if not schemas:
        errors.append(f"{schema_dir}: no *{SCHEMA_SUFFIX} files found")

    examples = {}
    for name in schemas:
        directory = examples_dir / name
        files = sorted(directory.glob("*.json")) if directory.is_dir() else []
        if not files:
            errors.append(f"{directory}: no example JSON files found")
            continue
        examples[name] = []
        for path in files:
            example = read_json(path, errors)
            if example is not None:
                examples[name].append((path, example))
    return schemas, examples


def check_definition_schemas(schemas, examples, errors):
    for name, (schema_path, schema) in schemas.items():
        for example_path, example in examples.get(name, []):
            label = f"{name}/{example_path.name}"
            validate_json_schema(example, schema, label, errors)


def check_definition_references(
    examples, manifest_rows, map_config, item_ids, npc_ids, currency_ids,
    class_ids, quest_ids, graph_ids, errors
):
    manifest = {row["record_id"].strip(): row for _, row in manifest_rows}
    skill_ids = {
        example.get("skillId")
        for _, example in examples.get("SkillDefinition", [])
        if isinstance(example.get("skillId"), str)
    }
    class_example_ids = {
        example.get("classId")
        for _, example in examples.get("ClassDefinition", [])
        if isinstance(example.get("classId"), str)
    }

    for path, example in examples.get("ClassDefinition", []):
        label = f"ClassDefinition/{path.name}"
        class_id = example.get("classId")
        if class_id not in class_ids:
            errors.append(f"{label}: classId '{class_id}' does not resolve")
        for skill_id in example.get("startingSkillIds", []):
            if skill_id not in skill_ids:
                errors.append(
                    f"{label}: starting skill '{skill_id}' has no example"
                )
        if class_id not in class_example_ids:
            errors.append(f"{label}: classId '{class_id}' missing")

    for path, example in examples.get("SkillDefinition", []):
        label = f"SkillDefinition/{path.name}"
        class_id = example.get("classId")
        if class_id not in class_ids:
            errors.append(f"{label}: classId '{class_id}' does not resolve")

    for path, example in examples.get("ItemDefinition", []):
        label = f"ItemDefinition/{path.name}"
        item_id = example.get("itemId")
        if item_id not in item_ids:
            errors.append(f"{label}: itemId '{item_id}' does not resolve")
        source_map = example.get("sourceMapId")
        if source_map not in map_config["known"]:
            errors.append(
                f"{label}: sourceMapId '{source_map}' does not resolve"
            )

    for path, example in examples.get("MapDefinition", []):
        label = f"MapDefinition/{path.name}"
        map_id = example.get("mapId")
        if map_id not in map_config["known"]:
            errors.append(f"{label}: mapId '{map_id}' does not resolve")
            continue
        bounds = bounds_for(map_id, map_config)
        width = example.get("widthWu")
        height = example.get("heightWu")
        if not isinstance(width, (int, float)) or not isinstance(height, (int, float)):
            continue
        if width != bounds["xMax"] - bounds["xMin"]:
            errors.append(
                f"{label}: widthWu {width} does not match bounds width "
                f"{bounds['xMax'] - bounds['xMin']}"
            )
        floor = example.get("floorYWu", 0)
        if height != bounds["yMax"] - floor:
            errors.append(
                f"{label}: heightWu {height} does not match bounds height "
                f"{bounds['yMax'] - floor}"
            )
        spawn = example.get("spawnPoint", {})
        x_wu = spawn.get("xWu")
        y_wu = spawn.get("yWu")
        if (
            isinstance(x_wu, (int, float))
            and isinstance(y_wu, (int, float))
            and not (
                bounds["xMin"] <= x_wu <= bounds["xMax"]
                and bounds["yMin"] <= y_wu <= bounds["yMax"]
            )
        ):
            errors.append(f"{label}: spawnPoint is outside map bounds")

    for path, example in examples.get("SpawnDefinition", []):
        label = f"SpawnDefinition/{path.name}"
        record_id = example.get("recordId")
        row = manifest.get(record_id)
        if row is None:
            errors.append(f"{label}: recordId '{record_id}' not in manifest")
            continue
        if example.get("mapId") != row.get("map_id"):
            errors.append(f"{label}: mapId does not match manifest")
        if example.get("recordType") != row.get("record_type"):
            errors.append(f"{label}: recordType does not match manifest")
        if example.get("designState") != row.get("design_state"):
            errors.append(f"{label}: designState does not match manifest")
        expected_entities = [
            value.strip()
            for value in (row.get("entity_id") or "").split("|")
            if value.strip()
        ]
        if example.get("entityIds") != expected_entities:
            errors.append(f"{label}: entityIds do not match manifest")
        if example.get("quantity") != parse_int(row.get("quantity")):
            errors.append(f"{label}: quantity does not match manifest")
        if example.get("composition") != row.get("composition"):
            errors.append(f"{label}: composition does not match manifest")
        if example.get("lootTableId") != row.get("loot_table_id"):
            errors.append(f"{label}: lootTableId does not match manifest")
        position = example.get("position", {})
        if (
            position.get("xWu") != parse_float(row.get("x_wu"))
            or position.get("yWu") != parse_float(row.get("y_wu"))
        ):
            errors.append(f"{label}: position does not match manifest")
        level = example.get("levelBand", {})
        if (
            level.get("min") != parse_int(row.get("character_level_min"))
            or level.get("max") != parse_int(row.get("character_level_max"))
        ):
            errors.append(f"{label}: levelBand does not match manifest")
        if example.get("respawnSeconds") != parse_int(row.get("respawn_seconds")):
            errors.append(f"{label}: respawnSeconds does not match manifest")

    for path, example in examples.get("GatheringNodeDefinition", []):
        label = f"GatheringNodeDefinition/{path.name}"
        record_id = example.get("recordId")
        row = manifest.get(record_id)
        if row is None:
            errors.append(f"{label}: recordId '{record_id}' not in manifest")
            continue
        if row.get("record_type") != "GATHER_NODE":
            errors.append(f"{label}: manifest record is not GATHER_NODE")
        checks = {
            "mapId": "map_id",
            "nodeId": "entity_id",
            "designState": "design_state",
            "profession": "gather_profession",
            "gatherItemId": "gather_item_id",
            "toolId": "tool_id",
            "qualityTier": "quality_tier",
        }
        for example_key, manifest_key in checks.items():
            if example.get(example_key) != row.get(manifest_key):
                errors.append(
                    f"{label}: {example_key} does not match manifest"
                )
        numeric_checks = {
            "professionLevelRequired": "profession_level_required",
            "yieldMin": "yield_min",
            "yieldMax": "yield_max",
            "respawnSeconds": "respawn_seconds",
        }
        for example_key, manifest_key in numeric_checks.items():
            if example.get(example_key) != parse_int(row.get(manifest_key)):
                errors.append(
                    f"{label}: {example_key} does not match manifest"
                )
        position = example.get("position", {})
        if (
            position.get("xWu") != parse_float(row.get("x_wu"))
            or position.get("yWu") != parse_float(row.get("y_wu"))
        ):
            errors.append(f"{label}: position does not match manifest")
        if example.get("gatherItemId") not in item_ids:
            errors.append(f"{label}: gatherItemId does not resolve")
        if example.get("toolId") not in item_ids:
            errors.append(f"{label}: toolId does not resolve")

    for path, example in examples.get("QuestDefinition", []):
        label = f"QuestDefinition/{path.name}"
        quest_id = example.get("questId")
        if quest_id not in quest_ids:
            errors.append(f"{label}: questId '{quest_id}' does not resolve")
        graph_id = example.get("graphId")
        if graph_id not in graph_ids:
            errors.append(f"{label}: graphId '{graph_id}' does not resolve")
        for npc_key in ("startNpcId", "turnInNpcId"):
            npc_id = example.get(npc_key)
            if npc_id not in npc_ids:
                errors.append(
                    f"{label}: {npc_key} '{npc_id}' does not resolve"
                )
        for prerequisite in example.get("prerequisiteQuestIds", []):
            if prerequisite not in quest_ids:
                errors.append(
                    f"{label}: prerequisite '{prerequisite}' does not resolve"
                )
        for objective in example.get("objectives", []):
            map_id = objective.get("mapId")
            if map_id not in map_config["known"]:
                errors.append(
                    f"{label}: objective mapId '{map_id}' does not resolve"
                )
        rewards = example.get("rewards", {})
        for item_id in rewards.get("itemIds", []):
            if item_id not in item_ids:
                errors.append(
                    f"{label}: reward item '{item_id}' does not resolve"
                )
        for currency in rewards.get("currency", []):
            currency_id = currency.get("currencyId")
            if currency_id not in currency_ids:
                errors.append(
                    f"{label}: currency '{currency_id}' does not resolve"
                )


def relative_display(path):
    try:
        return path.resolve().relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def write_report(path, docs_dir, content_dir, manifest, rows, schemas, examples, errors):
    report = {
        "schemaVersion": 1,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "docsDirectory": relative_display(docs_dir),
        "contentDirectory": relative_display(content_dir),
        "manifest": {
            "file": manifest.name,
            "rowCount": len(rows),
            "expectedRowCount": MANIFEST_ROW_COUNT,
        },
        "definitions": {
            "schemaCount": len(schemas),
            "exampleCount": sum(len(items) for items in examples.values()),
        },
        "status": "FAILED" if errors else "PASSED",
        "errorCount": len(errors),
        "errors": errors,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"ERROR: cannot write report {path}: {exc}", file=sys.stderr)
        return False
    print(f"Report: {path}")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Validate production CSV and definition content "
        "(standard library only)."
    )
    parser.add_argument(
        "--docs",
        default=None,
        help="Directory containing the source CSVs "
        "(default: docs/production relative to the project root)",
    )
    parser.add_argument(
        "--content",
        default=None,
        help="Directory containing schemas/examples/map bounds "
        "(default: Implementation/Content relative to the project root)",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Write a JSON validation report to this path",
    )
    args = parser.parse_args(argv)

    docs_dir = (
        Path(args.docs)
        if args.docs
        else PROJECT_ROOT / "docs" / "production"
    )
    if not docs_dir.is_absolute():
        docs_dir = (Path.cwd() / docs_dir).resolve()
    if not docs_dir.is_dir():
        print(f"ERROR: docs directory not found: {docs_dir}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    content_dir = (
        Path(args.content) if args.content else DEFAULT_CONTENT_DIR
    )
    if not content_dir.is_absolute():
        content_dir = (Path.cwd() / content_dir).resolve()
    if not content_dir.is_dir():
        print(
            f"ERROR: content directory not found: {content_dir}",
            file=sys.stderr,
        )
        return EXIT_ENVIRONMENT

    errors = []
    print(f"Docs directory: {docs_dir}")
    print(f"Content directory: {content_dir}")

    manifest = find_manifest(docs_dir, errors)
    if manifest is None:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    fieldnames, rows = read_rows(manifest, errors)
    if fieldnames is None:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    print(f"Manifest: {manifest.name}")
    check_required_columns(manifest, fieldnames, errors)
    check_row_count(manifest, rows, errors)
    check_record_ids(manifest, rows, errors)
    check_numeric_coordinates(manifest, rows, errors)

    for file_name in ID_UNIQUENESS_FILES:
        path = docs_dir / file_name
        names, file_rows = read_rows(path, errors)
        if names is None:
            continue
        id_column = detect_id_column(names)
        print(f"{file_name}: ID column = {id_column or 'NOT DETECTED'}")
        check_id_uniqueness(path, names, file_rows, errors)

    item_ids = load_id_set(
        docs_dir, "Item_Master_Catalog_vi.csv", "item_id", errors
    )
    item_ids |= load_id_set(
        docs_dir, "Item_Rarity_Variant_Catalog_vi.csv", "item_id", errors
    )
    npc_ids = load_id_set(
        docs_dir, NPC_REGISTRY_FILE, NPC_REGISTRY_ID_COLUMN, errors
    )
    currency_ids = load_id_set(
        docs_dir, "Currency_Production_Data_vi.csv", "currency_id", errors
    )
    class_ids = load_id_set(
        docs_dir, "Class_Passive_Production_Data_vi.csv", "class_id", errors
    )

    graph_ids = set()
    quest_ids = set()
    quest_path = docs_dir / "Quest_Dialogue_Production_Data_vi.csv"
    quest_names, quest_rows = read_rows(quest_path, errors)
    if quest_names is not None:
        for _, row in quest_rows:
            if (row.get("graph_id") or "").strip():
                graph_ids.add(row["graph_id"].strip())
            if (row.get("quest_id") or "").strip():
                quest_ids.add(row["quest_id"].strip())

    map_config = load_map_bounds(content_dir, errors)
    if map_config is None:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return EXIT_ENVIRONMENT

    manifest_map_ids = {
        (row.get("map_id") or "").strip() for _, row in rows
    } - {""}
    missing_maps = manifest_map_ids - map_config["known"]
    extra_maps = map_config["known"] - manifest_map_ids
    if missing_maps:
        errors.append(
            f"manifest: map IDs missing from map bounds: "
            f"{', '.join(sorted(missing_maps))}"
        )
    if extra_maps:
        errors.append(
            f"map_bounds.json: map IDs not present in manifest: "
            f"{', '.join(sorted(extra_maps))}"
        )

    check_manifest_semantics(manifest, rows, map_config, item_ids, errors)
    check_manifest_npc_references(manifest, rows, npc_ids, errors)
    check_manifest_bounds(manifest, rows, map_config, errors)

    schemas, examples = load_definition_data(content_dir, errors)
    check_definition_schemas(schemas, examples, errors)
    if examples:
        check_definition_references(
            examples,
            rows,
            map_config,
            item_ids,
            npc_ids,
            currency_ids,
            class_ids,
            quest_ids,
            graph_ids,
            errors,
        )

    print(f"Definition schemas: {len(schemas)}")
    for name in sorted(schemas):
        print(f"  {name}: {len(examples.get(name, []))} example(s)")

    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = (Path.cwd() / report_path).resolve()
        if not write_report(
            report_path,
            docs_dir,
            content_dir,
            manifest,
            rows,
            schemas,
            examples,
            errors,
        ):
            return EXIT_ENVIRONMENT

    if errors:
        print(f"\nFAILED: {len(errors)} problem(s) found:", file=sys.stderr)
        for message in errors:
            print(f"  - {message}", file=sys.stderr)
        return EXIT_VALIDATION

    print("\nOK: all content validation checks passed.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
