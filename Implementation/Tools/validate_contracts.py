#!/usr/bin/env python3
"""Validate P1 JSON message contracts and their examples."""

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from json_schema import validate as validate_json_schema
from validate_content import (
    bounds_for,
    load_map_bounds,
    read_json,
    read_rows,
    relative_display,
)

CONTRACTS_DIR_NAME = Path("Implementation") / "Contracts" / "P1"
EXAMPLES_DIR_NAME = "Examples"
SCHEMA_SUFFIX = ".schema.json"
EXAMPLE_SUFFIX = ".example.json"
REPORT_SCHEMA_VERSION = 1

EXIT_OK = 0
EXIT_VALIDATION = 1
EXIT_ENVIRONMENT = 2

# Art Bible §6 bestiary state machine for hostile actors; everything else in
# the snapshot is a world object with an availability lifecycle instead.
MOB_LIFECYCLE_STATES = {
    "IDLE",
    "AGGRO",
    "CHASE",
    "TELEGRAPH",
    "ATTACK",
    "RECOVER",
    "RETURN",
    "DEAD",
}
OBJECT_STATES = {"ACTIVE", "AVAILABLE", "DEPLETED"}

ID_FIELDS = {
    "skillId": "skill",
    "mapId": "map",
    "questId": "quest",
    "templateId": "item",
    "currencyId": "currency",
    "entityId": "entity",
    "npcId": "entity",
    "classId": "class",
}


def load_schemas(contracts_dir, errors):
    schema_dir = contracts_dir
    if not schema_dir.is_dir():
        errors.append(f"{schema_dir}: contracts directory not found")
        return {}
    schemas = {}
    for path in sorted(schema_dir.glob(f"*{SCHEMA_SUFFIX}")):
        name = path.name[: -len(SCHEMA_SUFFIX)]
        schema = read_json(path, errors)
        if schema is None:
            continue
        if not isinstance(schema, dict):
            errors.append(f"{path.name}: schema must be a JSON object")
            continue
        schemas[name] = schema
    if not schemas:
        errors.append(f"{schema_dir}: no *{SCHEMA_SUFFIX} files found")
    return schemas


def load_examples(contracts_dir, schemas, errors):
    examples_dir = contracts_dir / EXAMPLES_DIR_NAME
    if not examples_dir.is_dir():
        errors.append(f"{examples_dir}: examples directory not found")
        return {}
    examples = {}
    for name in schemas:
        path = examples_dir / f"{name}{EXAMPLE_SUFFIX}"
        if not path.is_file():
            errors.append(f"{path}: missing example for schema '{name}'")
            continue
        example = read_json(path, errors)
        if example is not None:
            examples[name] = example
    for path in sorted(examples_dir.glob(f"*{EXAMPLE_SUFFIX}")):
        name = path.name[: -len(EXAMPLE_SUFFIX)]
        if name not in schemas:
            errors.append(f"{path.name}: example has no matching schema")
    return examples


def load_csv_ids(path, column, errors):
    if not path.is_file():
        errors.append(f"{path}: file not found")
        return set()
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                errors.append(f"{path.name}: file has no header row")
                return set()
            if column not in reader.fieldnames:
                errors.append(f"{path.name}: missing column '{column}'")
                return set()
            values = set()
            for row in reader:
                value = (row.get(column) or "").strip()
                if value:
                    values.add(value)
            return values
    except (OSError, UnicodeDecodeError, csv.Error) as exc:
        errors.append(f"{path}: cannot read CSV ({exc})")
        return set()


def load_definition_ids(content_dir, folder, id_field, errors):
    values = set()
    examples_dir = content_dir / "Examples" / folder
    if not examples_dir.is_dir():
        errors.append(f"{examples_dir}: examples directory not found")
        return values
    for path in sorted(examples_dir.glob("*.json")):
        data = read_json(path, errors)
        if not isinstance(data, dict):
            continue
        value = data.get(id_field)
        if isinstance(value, str) and value:
            values.add(value)
    return values


def load_runtime_entity_ids(content_dir, errors):
    path = content_dir / "Runtime" / "world_entities_bm.json"
    values = set()
    if not path.is_file():
        return values
    data = read_json(path, errors)
    if not isinstance(data, dict):
        return values
    for entity in data.get("entities", []):
        if isinstance(entity, dict):
            value = entity.get("entityId")
            if isinstance(value, str) and value:
                values.add(value)
    return values


def load_reference_sets(docs_dir, content_dir, errors):
    manifest_path = docs_dir / "World_Spawn_Gathering_Manifest_vi.csv"
    entity_ids = set()
    fieldnames, rows = read_rows(manifest_path, errors)
    if fieldnames is not None and rows is not None:
        if "entity_id" not in fieldnames:
            errors.append(f"{manifest_path.name}: missing column 'entity_id'")
        else:
            for _, row in rows:
                for part in (row.get("entity_id") or "").split("|"):
                    value = part.strip()
                    if value:
                        entity_ids.add(value)

    map_config = load_map_bounds(content_dir, errors)
    map_ids = map_config["known"] if map_config else set()

    return {
        "class": load_definition_ids(content_dir, "ClassDefinition", "classId", errors),
        "skill": load_definition_ids(content_dir, "SkillDefinition", "skillId", errors),
        "map": map_ids,
        "quest": load_csv_ids(
            docs_dir / "Quest_Dialogue_Production_Data_vi.csv", "quest_id", errors
        ),
        "item": load_csv_ids(
            docs_dir / "Item_Master_Catalog_vi.csv", "item_id", errors
        )
        | load_csv_ids(
            docs_dir / "Item_Rarity_Variant_Catalog_vi.csv", "item_id", errors
        ),
        "currency": load_csv_ids(
            docs_dir / "Currency_Production_Data_vi.csv", "currency_id", errors
        ),
        "entity": entity_ids,
        "entityInstance": load_runtime_entity_ids(content_dir, errors),
    }


def walk_references(value, references, label, errors):
    if isinstance(value, dict):
        for key, child in value.items():
            if key in ID_FIELDS and isinstance(child, str):
                kind = ID_FIELDS[key]
                if kind == "entity" and child.startswith("ENT_"):
                    # Runtime instance IDs (ENT_...) resolve against the
                    # world-entity bundle, not the manifest template column.
                    if references["entityInstance"] and child not in references["entityInstance"]:
                        errors.append(
                            f"{label}.{key}: '{child}' does not resolve to a runtime entity instance"
                        )
                elif child not in references[kind]:
                    errors.append(
                        f"{label}.{key}: '{child}' does not resolve to a {kind} ID"
                    )
            walk_references(child, references, f"{label}.{key}", errors)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            walk_references(child, references, f"{label}[{index}]", errors)


def check_map_bounds(example, map_config, label, errors):
    if not isinstance(example, dict):
        return
    map_id = example.get("mapId")
    if not isinstance(map_id, str):
        return
    if map_config is None or map_id not in map_config["known"]:
        return
    bounds = bounds_for(map_id, map_config)
    points = []
    if "xWu" in example or "yWu" in example:
        points.append(("xWu/yWu", example.get("xWu"), example.get("yWu")))
    self_data = example.get("self")
    if isinstance(self_data, dict):
        points.append(("self", self_data.get("x"), self_data.get("y")))
    entities = example.get("entities")
    if isinstance(entities, list):
        for index, entity in enumerate(entities):
            if isinstance(entity, dict):
                points.append((f"entities[{index}]", entity.get("x"), entity.get("y")))
    for point_label, x, y in points:
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            continue
        if not (
            bounds["xMin"] <= x <= bounds["xMax"]
            and bounds["yMin"] <= y <= bounds["yMax"]
        ):
            errors.append(
                f"{label}.{point_label}: ({x}, {y}) outside {map_id} bounds "
                f"x={bounds['xMin']}..{bounds['xMax']} y={bounds['yMin']}..{bounds['yMax']}"
            )


def check_world_snapshot(example, label, errors):
    if not isinstance(example, dict):
        return
    self_data = example.get("self")
    if isinstance(self_data, dict):
        if self_data.get("hp", 0) > self_data.get("maxHp", 0):
            errors.append(f"{label}.self: hp exceeds maxHp")
        if self_data.get("mp", 0) > self_data.get("maxMp", 0):
            errors.append(f"{label}.self: mp exceeds maxMp")
    entities = example.get("entities")
    if not isinstance(entities, list):
        return
    seen = set()
    for index, entity in enumerate(entities):
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("entityId")
        if isinstance(entity_id, str):
            if entity_id in seen:
                errors.append(f"{label}.entities[{index}]: duplicate entityId '{entity_id}'")
            seen.add(entity_id)
        if entity.get("hp", 0) > entity.get("maxHp", 0):
            errors.append(f"{label}.entities[{index}]: hp exceeds maxHp")


def check_combat_event(example, label, errors):
    if not isinstance(example, dict):
        return
    if example.get("eventType") != "combat.hit":
        return
    payload = example.get("payload")
    if not isinstance(payload, dict):
        errors.append(f"{label}.payload: combat.hit requires a payload object")
        return
    if not isinstance(payload.get("skillId"), str):
        errors.append(f"{label}.payload.skillId: combat.hit requires a skillId")
    if not isinstance(payload.get("damage"), int) or isinstance(payload.get("damage"), bool):
        errors.append(f"{label}.payload.damage: combat.hit requires an integer damage")
    if not isinstance(payload.get("hit"), bool):
        errors.append(f"{label}.payload.hit: combat.hit requires a boolean hit")


def check_quest_state(example, label, errors):
    if not isinstance(example, dict):
        return
    counters = example.get("objectiveCounters")
    if not isinstance(counters, dict):
        return
    for key, value in counters.items():
        if not key.startswith("OBJ_"):
            errors.append(f"{label}.objectiveCounters: '{key}' must start with OBJ_")
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{label}.objectiveCounters.{key}: must be a non-negative integer")


def check_inventory(example, label, errors):
    if not isinstance(example, dict):
        return
    items = example.get("items")
    if not isinstance(items, list):
        return
    seen = set()
    for index, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        instance_id = item.get("instanceId")
        if isinstance(instance_id, str):
            if instance_id in seen:
                errors.append(f"{label}.items[{index}]: duplicate instanceId '{instance_id}'")
            seen.add(instance_id)
        if item.get("location") == "EQUIPPED" and not isinstance(item.get("slot"), str):
            errors.append(f"{label}.items[{index}]: equipped item requires a slot")


def check_world_snapshot_v2(example, label, errors):
    if not isinstance(example, dict):
        return
    audience = example.get("audience")
    if not isinstance(audience, dict) or (
        audience.get("aoiEnterWu") != 40 or audience.get("aoiLeaveWu") != 48
    ):
        errors.append(f"{label}.audience: AOI must be enter 40 WU / leave 48 WU")
    top_instance = example.get("mapInstanceId")
    top_floor = example.get("floorId")
    top_phase = example.get("phase")
    seen = set()
    entities = example.get("entities")
    if not isinstance(entities, list):
        return
    for index, entity in enumerate(entities):
        if not isinstance(entity, dict):
            continue
        entity_id = entity.get("entityId")
        if isinstance(entity_id, str):
            if entity_id in seen:
                errors.append(f"{label}.entities[{index}]: duplicate entityId '{entity_id}'")
            seen.add(entity_id)
        for key, expected in (
            ("mapInstanceId", top_instance),
            ("floorId", top_floor),
            ("phase", top_phase),
        ):
            if entity.get(key) != expected:
                errors.append(
                    f"{label}.entities[{index}].{key}: must equal the snapshot {key}"
                )
        if entity.get("hp", 0) > entity.get("maxHp", 0):
            errors.append(f"{label}.entities[{index}]: hp exceeds maxHp")
        kind = entity.get("kind")
        health_state = entity.get("healthState")
        targetable = entity.get("targetable")
        state = entity.get("state")
        if kind in ("MOB", "BOSS"):
            if state not in MOB_LIFECYCLE_STATES:
                errors.append(
                    f"{label}.entities[{index}].state: '{state}' is not a mob "
                    f"lifecycle state"
                )
            if health_state == "ALIVE" and targetable is not True:
                errors.append(
                    f"{label}.entities[{index}]: an alive mob must be targetable"
                )
            if health_state == "DEAD" and targetable is not False:
                errors.append(
                    f"{label}.entities[{index}]: a dead mob must not be targetable"
                )
        elif state not in OBJECT_STATES:
            errors.append(
                f"{label}.entities[{index}].state: '{state}' belongs to the mob "
                f"lifecycle, not to a {kind}"
            )
        if kind == "NPC" and (health_state != "INVULNERABLE" or targetable is not False):
            errors.append(
                f"{label}.entities[{index}]: NPC must be INVULNERABLE and not targetable"
            )
        if kind == "BOSS" and health_state == "BLOCKED" and targetable is not False:
            errors.append(
                f"{label}.entities[{index}]: blocked boss must not be targetable"
            )
        if kind in ("GATHER_NODE", "INTERACTABLE") and "availability" not in entity:
            errors.append(
                f"{label}.entities[{index}]: claimable entity requires availability"
            )


def check_combat_input_v2(example, label, errors):
    if not isinstance(example, dict):
        return
    action_kind = example.get("actionKind")
    skill_id = example.get("skillId")
    if action_kind == "SKILL" and not isinstance(skill_id, str):
        errors.append(f"{label}.skillId: SKILL requires a skillId")
    if action_kind == "BASIC_ATTACK" and skill_id is not None:
        errors.append(f"{label}.skillId: BASIC_ATTACK must not carry a skillId")


def check_combat_event_v2(example, label, errors):
    if not isinstance(example, dict):
        return
    event_type = example.get("type")
    result = example.get("result")
    if event_type in ("IMPACT", "MISS"):
        if not isinstance(example.get("targetId"), str) or not isinstance(
            example.get("targetLifeId"), int
        ):
            errors.append(f"{label}: {event_type} requires targetId and targetLifeId")
        if not isinstance(example.get("hitIndex"), int):
            errors.append(f"{label}: {event_type} requires hitIndex")
        if not isinstance(result, dict):
            errors.append(f"{label}: {event_type} requires a result object")
        elif event_type == "IMPACT" and result.get("hit") is not True:
            errors.append(f"{label}.result.hit: IMPACT requires hit true")
        elif event_type == "MISS" and result.get("hit") is not False:
            errors.append(f"{label}.result.hit: MISS requires hit false")
    if event_type == "DEATH":
        if not isinstance(example.get("targetId"), str) or not isinstance(
            example.get("targetLifeId"), int
        ):
            errors.append(f"{label}: DEATH requires targetId and targetLifeId")
    if event_type == "CAST_START" and result is not None:
        errors.append(f"{label}.result: CAST_START must not carry a damage result")
    if event_type == "COUNTER_CONFIRMED" and result is not None:
        errors.append(
            f"{label}.result: COUNTER_CONFIRMED is a guard confirmation/reserve, "
            "not counter damage"
        )


def check_combat_result_v2(example, label, errors):
    if not isinstance(example, dict):
        return
    action_kind = example.get("actionKind")
    skill_id = example.get("skillId")
    if action_kind == "SKILL" and not isinstance(skill_id, str):
        errors.append(f"{label}.skillId: SKILL requires a skillId")
    if action_kind == "BASIC_ATTACK" and skill_id is not None:
        errors.append(f"{label}.skillId: BASIC_ATTACK must not carry a skillId")
    cast_id = example.get("castId")
    events = example.get("events")
    if not isinstance(events, list) or not events:
        errors.append(f"{label}.events: accepted casts return at least CAST_START")
        return
    cursors = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            continue
        cursors.append(event.get("cursor"))
        if event.get("castId") != cast_id:
            errors.append(f"{label}.events[{index}].castId must equal the cast id")
    if any(not isinstance(cursor, int) for cursor in cursors):
        errors.append(f"{label}.events: every event requires an integer cursor")
    elif cursors != sorted(set(cursors)):
        errors.append(f"{label}.events: cursors must be strictly increasing")
    if events and isinstance(events[0], dict) and events[0].get("type") != "CAST_START":
        errors.append(f"{label}.events[0].type: accepted cast starts with CAST_START")


def check_combat_event_page_v2(example, label, errors):
    if not isinstance(example, dict):
        return
    events = example.get("events")
    if not isinstance(events, list):
        return
    cursors = [event.get("cursor") for event in events if isinstance(event, dict)]
    if any(not isinstance(cursor, int) for cursor in cursors):
        errors.append(f"{label}.events: every event requires an integer cursor")
    elif cursors != sorted(set(cursors)):
        errors.append(f"{label}.events: cursors must be strictly increasing")
    next_cursor = example.get("nextCursor")
    if isinstance(next_cursor, int) and cursors and max(cursors) > next_cursor:
        errors.append(f"{label}.nextCursor: must be >= every event cursor")
    if example.get("resyncRequired") is True and "resyncReason" not in example:
        errors.append(f"{label}.resyncReason: required when resyncRequired is true")
    if example.get("resyncRequired") is False and "resyncReason" in example:
        errors.append(f"{label}.resyncReason: only allowed when resyncRequired is true")


def check_example_semantics(name, example, map_config, errors):
    label = f"{name}{EXAMPLE_SUFFIX}"
    check_map_bounds(example, map_config, label, errors)
    if name == "WorldSnapshot":
        check_world_snapshot(example, label, errors)
    elif name == "WorldSnapshotV2":
        check_world_snapshot_v2(example, label, errors)
    elif name == "CombatInputV2":
        check_combat_input_v2(example, label, errors)
    elif name == "CombatEventV2":
        check_combat_event_v2(example, label, errors)
    elif name == "CombatEventPageV2":
        check_combat_event_page_v2(example, label, errors)
    elif name == "CombatResultV2":
        check_combat_result_v2(example, label, errors)
    elif name == "CombatEvent":
        check_combat_event(example, label, errors)
    elif name == "QuestState":
        check_quest_state(example, label, errors)
    elif name == "InventorySnapshot":
        check_inventory(example, label, errors)


def write_report(
    path,
    contracts_dir,
    schema_count,
    example_count,
    errors,
):
    report = {
        "schemaVersion": REPORT_SCHEMA_VERSION,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "contractsDirectory": relative_display(contracts_dir),
        "schemaCount": schema_count,
        "exampleCount": example_count,
        "status": "PASSED" if not errors else "FAILED",
        "errorCount": len(errors),
        "errors": errors,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Report: {path}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--contracts",
        default=str(CONTRACTS_DIR_NAME),
        help="P1 contracts directory (default: %(default)s)",
    )
    parser.add_argument(
        "--docs",
        default="docs/production",
        help="Production docs directory (default: %(default)s)",
    )
    parser.add_argument(
        "--content",
        default="Implementation/Content",
        help="Content directory (default: %(default)s)",
    )
    parser.add_argument(
        "--report",
        help="Optional path to write a JSON validation report",
    )
    args = parser.parse_args(argv)

    contracts_dir = Path(args.contracts)
    docs_dir = Path(args.docs)
    content_dir = Path(args.content)
    errors = []

    if not contracts_dir.is_dir():
        errors.append(f"{contracts_dir}: contracts directory not found")
    if not docs_dir.is_dir():
        errors.append(f"{docs_dir}: docs directory not found")
    if not content_dir.is_dir():
        errors.append(f"{content_dir}: content directory not found")

    schemas = load_schemas(contracts_dir, errors)
    examples = load_examples(contracts_dir, schemas, errors)
    references = load_reference_sets(docs_dir, content_dir, errors)
    map_config = load_map_bounds(content_dir, errors)

    print(f"Contracts directory: {contracts_dir}")
    print(f"Schemas: {len(schemas)}")
    print(f"Examples: {len(examples)}")
    print(f"Reference sets: {', '.join(f'{key}={len(value)}' for key, value in references.items())}")

    for name, schema in schemas.items():
        example = examples.get(name)
        if example is None:
            continue
        label = f"{name}{EXAMPLE_SUFFIX}"
        validate_json_schema(example, schema, label, errors)
        walk_references(example, references, label, errors)
        check_example_semantics(name, example, map_config, errors)

    if args.report:
        write_report(
            Path(args.report),
            contracts_dir,
            len(schemas),
            len(examples),
            errors,
        )

    if errors:
        print(f"\nFAILED: {len(errors)} error(s)")
        for error in errors:
            print(f"  - {error}")
        return EXIT_VALIDATION

    print("\nOK: all contract validation checks passed.")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
