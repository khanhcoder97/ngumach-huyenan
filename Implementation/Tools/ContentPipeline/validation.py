#!/usr/bin/env python3
"""Validation and field-level diff for Bến Mưa candidate bundles (OPC-11).

Validation is fail-closed: schema errors, missing provenance, dangling
references, duplicate IDs, unresolved values that do not explain missing
required fields, stale source hashes and digest mismatches all produce errors.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path

try:  # Direct execution from the tool directory.
    from compiler import BUNDLE_ID, TARGET_MAP_ID, canonical_bytes, digest_for
    from compiler_core import (
        Context,
        PipelineEnvironmentError,
        SOURCE_SPECS,
        iter_leaves,
        leaf_units,
        source_bytes,
    )
except ImportError:  # Import as part of the ContentPipeline package.
    from .compiler import BUNDLE_ID, TARGET_MAP_ID, canonical_bytes, digest_for
    from .compiler_core import (
        Context,
        PipelineEnvironmentError,
        SOURCE_SPECS,
        iter_leaves,
        leaf_units,
        source_bytes,
    )

_TOOLS_DIR = Path(__file__).resolve().parents[1]
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

from json_schema import validate as validate_schema  # noqa: E402

EXPECTED_QUESTS = [f"P00-0{index}" for index in range(1, 6)]
EXPECTED_MOBS = ["MOB_CARPLING", "MOB_WATERROOT", "MOB_SHORE_STALKER"]
EXPECTED_BOSS = "BOSS_MANG_COT"
EXPECTED_ACTOR = "ACTOR_BASE_L1_NO_GEAR"
METERS_TO_WU = 2.0
QUEST_OBJECTIVE_TYPES = {
    "TALK",
    "INTERACT",
    "KILL",
    "COLLECT",
    "ESCORT",
    "DEFEND",
    "BOSS_PHASE",
    "INSTANCE_CLEAR",
    "BOSS",
}
EVENT_TYPES = {"COLLECT", "KILL", "INTERACT", "ESCORT", "BOSS", "TALK"}
_ID_REFERENCE_TYPES = {
    "KILL": ("mob", "boss"),
    "BOSS": ("boss",),
    "TALK": ("npc", "design"),
    "INTERACT": ("npc", "design"),
    "ESCORT": ("npc", "design"),
    "COLLECT": ("design",),
}


def _unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"non-finite JSON constant {value}")


def load_json_file(path: Path, label: str) -> dict:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as exc:
        raise PipelineEnvironmentError(f"{label}: cannot read ({exc})") from exc
    try:
        value = json.loads(text, object_pairs_hook=_unique_members, parse_constant=_reject_constant)
    except ValueError as exc:
        raise PipelineEnvironmentError(f"{label}: invalid JSON ({exc})") from exc
    if not isinstance(value, dict):
        raise PipelineEnvironmentError(f"{label}: expected a JSON object")
    return value


def _pointer_parts(pointer: str) -> list[str]:
    if pointer == "/":
        return []
    if not pointer.startswith("/"):
        raise ValueError(f"invalid JSON pointer {pointer!r}")
    return [part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/")]


def pointer_get(document, pointer: str):
    current = document
    for part in _pointer_parts(pointer):
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


def pointer_exists(document, pointer: str) -> bool:
    found, _ = pointer_get(document, pointer)
    return found


def _escape_token(value) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _join_pointer(base: str, token) -> str:
    if base in ("", "/"):
        return "/" + _escape_token(token)
    return base + "/" + _escape_token(token)


def _label_to_pointer(label: str) -> str:
    tokens: list = []
    for match in re.finditer(r"([^.\[\]]+)|\[(\d+)\]", label):
        if match.group(1) is not None:
            tokens.append(match.group(1))
        else:
            tokens.append(int(match.group(2)))
    if tokens and tokens[0] == "definition":
        tokens = tokens[1:]
    pointer = "/"
    for token in tokens:
        pointer = _join_pointer(pointer, token)
    return pointer


def _missing_property_pointer(error: str, label: str) -> str | None:
    match = re.search(r"missing required property '([^']+)'", error)
    if not match:
        return None
    return _join_pointer(_label_to_pointer(label), match.group(1))


def _is_suppressed(path: str, unresolved: list[dict]) -> bool:
    for entry in unresolved:
        if entry.get("blocking") and entry.get("valueState") == "MISSING":
            unresolved_path = entry.get("path", "")
            if path == unresolved_path or path.startswith(unresolved_path.rstrip("/") + "/"):
                return True
    return False


def _validate_schema_document(document, schema_path: Path, label: str, errors: list[str]) -> None:
    try:
        schema = load_json_file(schema_path, f"schema {schema_path.name}")
    except PipelineEnvironmentError as exc:
        errors.append(str(exc))
        return
    raw_errors: list[str] = []
    validate_schema(document, schema, label, raw_errors)
    errors.extend(raw_errors)


def _source_entry_errors(
    entry: dict,
    source_map: dict[str, dict],
    label: str,
    errors: list[str],
) -> dict | None:
    source_id = entry.get("sourceId")
    if source_id not in source_map:
        errors.append(f"{label}: unknown sourceId {source_id!r}")
        return None
    source = source_map[source_id]
    source_ref = entry.get("sourceRef", "")
    if not source_ref:
        errors.append(f"{label}: empty sourceRef")
    elif not (source_ref == source["path"] or source_ref.startswith(source["path"] + "#")):
        errors.append(f"{label}: sourceRef does not reference {source['path']!r}")
    if entry.get("sourceVersion") != source["version"]:
        errors.append(
            f"{label}: sourceVersion {entry.get('sourceVersion')!r} does not match "
            f"{source['version']!r}"
        )
    return source


def _validate_sources(bundle: dict, ctx: Context, root: Path, errors: list[str]) -> dict[str, dict]:
    source_map: dict[str, dict] = {}
    sources = bundle.get("sources")
    if not isinstance(sources, list):
        errors.append("bundle: sources must be an array")
        return source_map
    ids = []
    for index, entry in enumerate(sources):
        label = f"bundle.sources[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        source_id = entry.get("sourceId")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{label}: missing sourceId")
            continue
        if source_id in source_map:
            errors.append(f"{label}: duplicate sourceId {source_id!r}")
            continue
        source_map[source_id] = entry
        ids.append(source_id)
        path_text = entry.get("path")
        if not isinstance(path_text, str) or not path_text:
            errors.append(f"{label}: missing path")
            continue
        relative = Path(path_text)
        if relative.is_absolute() or ".." in relative.parts:
            errors.append(f"{label}: source path escapes the repository")
            continue
        file_path = (root / relative).resolve()
        if not file_path.is_relative_to(root.resolve()):
            errors.append(f"{label}: source path escapes the repository")
            continue
        try:
            file_path.relative_to(root.resolve())
        except ValueError:
            errors.append(f"{label}: source path escapes the repository")
            continue
        expected = ctx.sources.get(source_id)
        if expected is None:
            errors.append(f"{label}: sourceId {source_id!r} is not produced by the compiler")
        elif entry != expected:
            errors.append(f"{label}: source metadata is stale; rebuild the bundle")
        try:
            digest = "sha256:" + hashlib.sha256(source_bytes(file_path.read_bytes())).hexdigest()
        except (OSError, UnicodeDecodeError) as exc:
            errors.append(f"{label}: cannot read source ({exc})")
            continue
        if entry.get("sha256") != digest:
            errors.append(f"{label}: source sha256 mismatch; rebuild the bundle")
    if ids != sorted(ids):
        errors.append("bundle: sources are not sorted by sourceId")
    missing = sorted(set(ctx.sources) - set(source_map))
    if missing:
        errors.append(f"bundle: missing compiler sources {missing}")
    return source_map


def _validate_bundle_digest(bundle: dict, errors: list[str]) -> None:
    payload = {key: value for key, value in bundle.items() if key != "bundleDigest"}
    expected = digest_for(payload)
    if bundle.get("bundleDigest") != expected:
        errors.append("bundle: bundleDigest does not match canonical content")


def _validate_candidate_digest(candidate: dict, errors: list[str]) -> None:
    payload = {key: value for key, value in candidate.items() if key != "candidateDigest"}
    expected = digest_for(payload)
    if candidate.get("candidateDigest") != expected:
        errors.append(f"{candidate.get('candidateId', '?')}: candidateDigest mismatch")


def _validate_provenance(
    candidate: dict,
    definition: dict,
    source_map: dict[str, dict],
    errors: list[str],
) -> None:
    candidate_id = candidate.get("candidateId", "?")
    provenance = candidate.get("fieldProvenance")
    if not isinstance(provenance, list):
        errors.append(f"{candidate_id}: fieldProvenance must be an array")
        return
    paths: list[str] = []
    leaf_values = dict(iter_leaves(definition))
    for index, entry in enumerate(provenance):
        label = f"{candidate_id}.fieldProvenance[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path.startswith("/"):
            errors.append(f"{label}: invalid path")
            continue
        paths.append(path)
        if not entry.get("units"):
            errors.append(f"{label}: empty units")
        elif path in leaf_values and entry["units"] != leaf_units(path, leaf_values[path]):
            errors.append(f"{label}: units do not match the field dimension")
        if not entry.get("transform"):
            errors.append(f"{label}: empty transform")
        _source_entry_errors(entry, source_map, label, errors)
    if len(paths) != len(set(paths)):
        errors.append(f"{candidate_id}: duplicate provenance paths")
    if paths != sorted(paths):
        errors.append(f"{candidate_id}: provenance paths are not sorted")

    leaves = set(dict(iter_leaves(definition)))
    missing = sorted(leaves - set(paths))
    extra = sorted(set(paths) - leaves)
    if missing:
        errors.append(f"{candidate_id}: missing provenance for {missing}")
    if extra:
        errors.append(f"{candidate_id}: provenance for absent fields {extra}")


def _validate_unresolved(
    candidate: dict,
    definition: dict,
    provenance_paths: set[str],
    source_map: dict[str, dict],
    errors: list[str],
) -> None:
    candidate_id = candidate.get("candidateId", "?")
    unresolved = candidate.get("unresolved")
    if not isinstance(unresolved, list):
        errors.append(f"{candidate_id}: unresolved must be an array")
        return
    paths: list[str] = []
    for index, entry in enumerate(unresolved):
        label = f"{candidate_id}.unresolved[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected object")
            continue
        path = entry.get("path")
        if not isinstance(path, str) or not path.startswith("/"):
            errors.append(f"{label}: invalid path")
            continue
        paths.append(path)
        if not isinstance(entry.get("blocking"), bool):
            errors.append(f"{label}: blocking must be a boolean")
        state = entry.get("valueState")
        if state not in {"MISSING", "PRESENT_UNRESOLVED"}:
            errors.append(f"{label}: invalid valueState {state!r}")
        if not entry.get("reason"):
            errors.append(f"{label}: empty reason")
        _source_entry_errors(entry, source_map, label, errors)
        exists = pointer_exists(definition, path)
        if state == "MISSING" and exists:
            errors.append(f"{label}: MISSING path exists in definition")
        if state == "PRESENT_UNRESOLVED":
            if not exists:
                errors.append(f"{label}: PRESENT_UNRESOLVED path is absent")
            elif path not in provenance_paths:
                errors.append(f"{label}: PRESENT_UNRESOLVED path lacks provenance")
    if len(paths) != len(set(paths)):
        errors.append(f"{candidate_id}: duplicate unresolved paths")
    if paths != sorted(paths):
        errors.append(f"{candidate_id}: unresolved paths are not sorted")

    blocking = any(entry.get("blocking") for entry in unresolved if isinstance(entry, dict))
    expected_status = "BLOCKED_UNRESOLVED" if blocking else "READY_FOR_REVIEW"
    if candidate.get("status") != expected_status:
        errors.append(
            f"{candidate_id}: status {candidate.get('status')!r} should be {expected_status!r}"
        )


def _validate_target_schema(
    candidate: dict,
    root: Path,
    schema_cache: dict,
    errors: list[str],
) -> None:
    candidate_id = candidate.get("candidateId", "?")
    target = candidate.get("targetSchema")
    if not isinstance(target, str) or not target:
        errors.append(f"{candidate_id}: missing targetSchema")
        return
    relative = Path(target)
    if relative.is_absolute() or ".." in relative.parts:
        errors.append(f"{candidate_id}: targetSchema escapes the repository")
        return
    schema_path = (root / relative).resolve()
    try:
        schema_path.relative_to(root.resolve())
    except ValueError:
        errors.append(f"{candidate_id}: targetSchema escapes the repository")
        return
    if schema_path not in schema_cache:
        try:
            schema_cache[schema_path] = load_json_file(schema_path, f"schema {relative}")
        except PipelineEnvironmentError as exc:
            errors.append(str(exc))
            return
    raw_errors: list[str] = []
    validate_schema(candidate.get("definition"), schema_cache[schema_path], "definition", raw_errors)
    unresolved = candidate.get("unresolved", [])
    for error in raw_errors:
        label = error.split(":", 1)[0]
        if "missing required property" in error:
            pointer = _missing_property_pointer(error, label)
            if pointer is not None and _is_suppressed(pointer, unresolved):
                continue
        errors.append(f"{candidate_id}: {error}")


def _validate_candidate(candidate: dict, root: Path, schema_cache: dict, source_map, errors: list[str]) -> None:
    schemas = {
        "QUEST": "Implementation/Content/Schemas/QuestDefinition.schema.json",
        "OBJECTIVE_MAP": "objective_map.schema.json",
        "ACTOR_PROFILE": "actor_profile.schema.json",
        "MOB_PROFILE": "mob_profile.schema.json",
        "BOSS_REFERENCE": "boss_reference.schema.json",
        "ITEM_REFERENCE": "item_reference.schema.json",
    }
    expected = schemas.get(candidate.get("kind"))
    if expected and not expected.startswith("Implementation/"):
        expected = "Implementation/Tools/ContentPipeline/schemas/" + expected
    if candidate.get("targetSchema") != expected:
        errors.append(f"{candidate.get('candidateId')}: targetSchema does not match candidate kind")
    candidate_id = candidate.get("candidateId")
    if not isinstance(candidate_id, str) or not candidate_id:
        errors.append("bundle.candidates: candidate without candidateId")
        return
    definition = candidate.get("definition")
    if not isinstance(definition, dict):
        errors.append(f"{candidate_id}: definition must be an object")
        return
    _validate_candidate_digest(candidate, errors)
    _validate_provenance(candidate, definition, source_map, errors)
    _validate_unresolved(candidate, definition, {
        entry["path"] for entry in candidate.get("fieldProvenance", []) if isinstance(entry, dict)
    }, source_map, errors)
    _validate_target_schema(candidate, root, schema_cache, errors)


def _check_reference(reference: str, kinds, ctx: Context) -> bool:
    if "mob" in kinds and reference in ctx.mob_ids:
        return True
    if "boss" in kinds and reference in ctx.boss_ids:
        return True
    if "npc" in kinds and reference in ctx.npc_by_id:
        return True
    if "design" in kinds and reference in ctx.design_ids:
        return True
    return False


def _as_list(value) -> list:
    return value if isinstance(value, list) else []


def _validate_quests(candidates: list[dict], ctx: Context, errors: list[str]) -> dict[str, dict]:
    quests: dict[str, dict] = {}
    for candidate in candidates:
        if candidate.get("kind") != "QUEST":
            continue
        definition = candidate.get("definition", {})
        quest_id = definition.get("questId")
        if not isinstance(quest_id, str) or not quest_id:
            errors.append(f"{candidate.get('candidateId', '?')}: missing questId")
            continue
        if quest_id in quests:
            errors.append(f"QUEST: duplicate questId {quest_id!r}")
        quests[quest_id] = definition
        if candidate.get("targetId") != quest_id:
            errors.append(f"QUEST {quest_id}: targetId does not match questId")
        for npc_key in ("startNpcId", "turnInNpcId"):
            npc_id = definition.get(npc_key)
            if npc_id not in ctx.npc_by_id:
                errors.append(f"QUEST {quest_id}: unknown {npc_key} {npc_id!r}")
        band = definition.get("levelBand", {})
        if isinstance(band, dict):
            minimum = band.get("min")
            maximum = band.get("max")
            if not isinstance(minimum, int) or not isinstance(maximum, int) or minimum > maximum:
                errors.append(f"QUEST {quest_id}: invalid levelBand")
            else:
                map_band = ctx.jsons["MAP_EXAMPLE_BEN_MUA"].get("levelBand", {})
                if minimum < map_band.get("min", 1) or maximum > map_band.get("max", 100):
                    errors.append(f"QUEST {quest_id}: levelBand outside Bến Mưa band")
        objective_ids: list[str] = []
        for index, objective in enumerate(_as_list(definition.get("objectives"))):
            label = f"QUEST {quest_id}.objectives[{index}]"
            objective_id = objective.get("objectiveId")
            objective_type = objective.get("type")
            if not isinstance(objective_id, str) or not objective_id:
                errors.append(f"{label}: missing objectiveId")
            elif objective_id in objective_ids:
                errors.append(f"{label}: duplicate objectiveId {objective_id!r}")
            else:
                objective_ids.append(objective_id)
            if objective_type not in QUEST_OBJECTIVE_TYPES:
                errors.append(f"{label}: invalid objective type {objective_type!r}")
            count = objective.get("count")
            if not isinstance(count, int) or count < 1:
                errors.append(f"{label}: count must be a positive integer")
            targets = _as_list(objective.get("targetIds"))
            if not targets:
                errors.append(f"{label}: empty targetIds")
            target_kinds = _ID_REFERENCE_TYPES.get(objective_type)
            if target_kinds:
                for target in targets:
                    if not _check_reference(target, target_kinds, ctx):
                        errors.append(f"{label}: dangling targetId {target!r}")
            map_id = objective.get("mapId")
            if map_id not in ctx.map_ids:
                errors.append(f"{label}: unknown mapId {map_id!r}")
        rewards = definition.get("rewards")
        if isinstance(rewards, dict):
            for currency in _as_list(rewards.get("currency")):
                currency_id = currency.get("currencyId")
                amount = currency.get("amount")
                if currency_id not in ctx.currency_ids:
                    errors.append(f"QUEST {quest_id}: unknown currencyId {currency_id!r}")
                if not isinstance(amount, int) or amount < 1:
                    errors.append(f"QUEST {quest_id}: invalid currency amount")
            for item_id in _as_list(rewards.get("itemIds")):
                if item_id not in ctx.item_by_id:
                    errors.append(f"QUEST {quest_id}: dangling reward itemId {item_id!r}")
            xp_rule = rewards.get("xpRule")
            if xp_rule is not None and not isinstance(xp_rule, str):
                errors.append(f"QUEST {quest_id}: invalid xpRule")
        for key in ("prerequisiteQuestIds", "unlocks"):
            for referenced in _as_list(definition.get(key)):
                if referenced not in ctx.quest_ids:
                    errors.append(f"QUEST {quest_id}: dangling {key} {referenced!r}")
        if not definition.get("sourceRef"):
            errors.append(f"QUEST {quest_id}: missing sourceRef")

    for quest_id in EXPECTED_QUESTS:
        if quest_id not in quests:
            errors.append(f"QUEST: expected candidate {quest_id} is missing")

    graph = {
        quest_id: [
            prerequisite
            for prerequisite in _as_list(definition.get("prerequisiteQuestIds"))
            if prerequisite in quests
        ]
        for quest_id, definition in quests.items()
    }
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(quest_id: str) -> None:
        if quest_id in visiting:
            errors.append(f"QUEST: prerequisite cycle involving {quest_id}")
            return
        if quest_id in visited:
            return
        visiting.add(quest_id)
        for prerequisite in graph.get(quest_id, []):
            visit(prerequisite)
        visiting.remove(quest_id)
        visited.add(quest_id)

    for quest_id in sorted(graph):
        visit(quest_id)

    for quest_id, definition in quests.items():
        for prerequisite in _as_list(definition.get("prerequisiteQuestIds")):
            if prerequisite not in quests:
                continue
            prerequisite_definition = quests[prerequisite]
            unlocks = _as_list(prerequisite_definition.get("unlocks"))
            if quest_id not in unlocks:
                blocking_unlocks = any(
                    entry.get("path") == "/unlocks" and entry.get("blocking")
                    for entry in _unresolved_for_quest(candidates, prerequisite)
                )
                if not blocking_unlocks:
                    errors.append(
                        f"QUEST {prerequisite}: does not unlock prerequisite target {quest_id}"
                    )
    return quests


def _unresolved_for_quest(candidates: list[dict], quest_id: str) -> list[dict]:
    for candidate in candidates:
        if candidate.get("kind") == "QUEST" and candidate.get("targetId") == quest_id:
            return _as_list(candidate.get("unresolved"))
    return []


def _validate_positions(positions, bounds: dict, label: str, errors: list[str]) -> None:
    for index, position in enumerate(_as_list(positions)):
        if not isinstance(position, dict):
            errors.append(f"{label}[{index}]: expected object")
            continue
        x = position.get("xWu")
        y = position.get("yWu")
        if not isinstance(x, (int, float)) or not math.isfinite(x):
            errors.append(f"{label}[{index}]: invalid xWu")
        elif x < bounds["xMin"] or x > bounds["xMax"]:
            errors.append(f"{label}[{index}]: xWu outside map bounds")
        if not isinstance(y, (int, float)) or not math.isfinite(y):
            errors.append(f"{label}[{index}]: invalid yWu")
        elif y < bounds["yMin"] or y > bounds["yMax"]:
            errors.append(f"{label}[{index}]: yWu outside map bounds")


def _validate_objective_maps(candidates: list[dict], quests: dict[str, dict], ctx: Context, errors: list[str]) -> None:
    seen: set[str] = set()
    for candidate in candidates:
        if candidate.get("kind") != "OBJECTIVE_MAP":
            continue
        definition = candidate.get("definition", {})
        quest_id = definition.get("questId")
        if quest_id in seen:
            errors.append(f"OBJECTIVE_MAP: duplicate mapping for quest {quest_id!r}")
        seen.add(quest_id)
        if quest_id != candidate.get("targetId"):
            errors.append(f"OBJECTIVE_MAP {quest_id}: targetId does not match questId")
        quest = quests.get(quest_id)
        if quest is None:
            errors.append(f"OBJECTIVE_MAP {quest_id}: quest candidate is missing")
            continue
        map_id = definition.get("mapId")
        if map_id not in ctx.map_ids:
            errors.append(f"OBJECTIVE_MAP {quest_id}: unknown mapId {map_id!r}")
        if not definition.get("floorId"):
            errors.append(f"OBJECTIVE_MAP {quest_id}: missing floorId")
        bounds = ctx.bounds_for(map_id) if map_id in ctx.map_ids else ctx.bounds["defaultBounds"]
        objectives = {
            objective.get("objectiveId"): objective
            for objective in _as_list(quest.get("objectives"))
            if isinstance(objective, dict)
        }
        counts: dict[str, int] = {objective_id: 0 for objective_id in objectives}
        for index, mapping in enumerate(_as_list(definition.get("mappings"))):
            label = f"OBJECTIVE_MAP {quest_id}.mappings[{index}]"
            objective_id = mapping.get("objectiveId")
            objective = objectives.get(objective_id)
            if objective is None:
                errors.append(f"{label}: unknown objectiveId {objective_id!r}")
                continue
            event_type = mapping.get("eventType")
            if event_type not in EVENT_TYPES:
                errors.append(f"{label}: invalid eventType {event_type!r}")
            count = mapping.get("count")
            if not isinstance(count, int) or count < 1:
                errors.append(f"{label}: count must be a positive integer")
            else:
                counts[objective_id] += count
            source_ids = _as_list(mapping.get("sourceIds"))
            if source_ids:
                kinds = _ID_REFERENCE_TYPES.get(event_type, ("design", "npc"))
                for source_id in source_ids:
                    if not _check_reference(source_id, kinds, ctx):
                        errors.append(f"{label}: dangling sourceId {source_id!r}")
                objective_targets = set(_as_list(objective.get("targetIds")))
                for source_id in source_ids:
                    if source_id not in objective_targets:
                        errors.append(f"{label}: sourceId {source_id!r} not in objective targetIds")
            _validate_positions(mapping.get("positions"), bounds, f"{label}.positions", errors)
            for record_id in _as_list(mapping.get("spawnRecordIds")):
                record = ctx.spawn_by_id.get(record_id)
                if record is None:
                    errors.append(f"{label}: unknown spawnRecordId {record_id!r}")
                    continue
                if record.get("map_id") != map_id:
                    errors.append(f"{label}: spawn {record_id} is not on {map_id}")
                if source_ids:
                    entities = set((record.get("entity_id") or "").split("|"))
                    if not entities.intersection(source_ids):
                        errors.append(f"{label}: spawn {record_id} does not contain a sourceId")
                respawn = mapping.get("respawnSeconds")
                if record.get("respawn_seconds") not in (None, "") and respawn != int(record["respawn_seconds"]):
                    errors.append(f"{label}: respawnSeconds does not match spawn {record_id}")
            for checkpoint in _as_list(mapping.get("checkpoints")):
                trigger = checkpoint.get("triggerXWu")
                radius = checkpoint.get("rangeWu")
                if not isinstance(trigger, (int, float)) or trigger < bounds["xMin"] or trigger > bounds["xMax"]:
                    errors.append(f"{label}: checkpoint trigger outside map bounds")
                if not isinstance(radius, (int, float)) or radius <= 0:
                    errors.append(f"{label}: checkpoint rangeWu must be positive")
            for key in ("rangeWu", "arenaRingDiameterWu"):
                value = mapping.get(key)
                if value is not None and (not isinstance(value, (int, float)) or value < 0):
                    errors.append(f"{label}: {key} must be non-negative")
        for objective_id, objective in objectives.items():
            if counts.get(objective_id, 0) == 0:
                index = list(objectives).index(objective_id)
                blocking = any(
                    entry.get("blocking") and entry.get("path", "").startswith(f"/objectives/{index}")
                    for entry in _as_list(candidate.get("unresolved"))
                )
                if not blocking:
                    errors.append(f"OBJECTIVE_MAP {quest_id}: objective {objective_id} has no mapping")
            elif counts[objective_id] != objective.get("count"):
                errors.append(
                    f"OBJECTIVE_MAP {quest_id}: objective {objective_id} count "
                    f"{counts[objective_id]} does not match quest count {objective.get('count')}"
                )
    for quest_id in EXPECTED_QUESTS:
        if quest_id not in seen:
            errors.append(f"OBJECTIVE_MAP: expected mapping for {quest_id} is missing")


def _validate_actor(candidates: list[dict], ctx: Context, errors: list[str]) -> None:
    actors = [candidate for candidate in candidates if candidate.get("kind") == "ACTOR_PROFILE"]
    if len(actors) != 1:
        errors.append(f"ACTOR_PROFILE: expected exactly one actor profile, found {len(actors)}")
        return
    candidate = actors[0]
    definition = candidate.get("definition", {})
    if candidate.get("targetId") != EXPECTED_ACTOR:
        errors.append(f"ACTOR_PROFILE: expected targetId {EXPECTED_ACTOR!r}")
    attributes = definition.get("attributes", {})
    if not isinstance(attributes, dict):
        errors.append("ACTOR_PROFILE: attributes must be an object")
        return
    stats = {}
    for name in ("STR", "INT", "AGI", "VIT", "LUK"):
        value = attributes.get(name)
        if not isinstance(value, int) or value < 0:
            errors.append(f"ACTOR_PROFILE: invalid attribute {name}")
        stats[name] = value if isinstance(value, int) else 0
    level = definition.get("level")
    if level != 1:
        errors.append("ACTOR_PROFILE: this export supports level 1 only")
    expected = {
        "maxHp": 100 + 28 * level + 14 * stats["VIT"] if isinstance(level, int) else None,
        "maxMp": 50 + 12 * level + 8 * stats["INT"] if isinstance(level, int) else None,
        "physicalAttack": 3 * stats["STR"] + stats["AGI"],
        "magicAttack": 3 * stats["INT"] + stats["LUK"],
        "armor": 2 * stats["VIT"],
    }
    derived = definition.get("derived", {})
    for key, value in expected.items():
        if value is not None and derived.get(key) != value:
            errors.append(f"ACTOR_PROFILE: {key} should be {value}, got {derived.get(key)!r}")
    if definition.get("equipment") != []:
        errors.append("ACTOR_PROFILE: equipment must be empty until item stat vectors exist")
    if definition.get("mapId") not in ctx.map_ids:
        errors.append("ACTOR_PROFILE: unknown mapId")
    for reference in _as_list(definition.get("classSkillReferences")):
        class_id = reference.get("classId")
        if class_id not in ctx.class_ids:
            errors.append(f"ACTOR_PROFILE: unknown classId {class_id!r}")
        for skill_id in _as_list(reference.get("startingSkillIds")):
            if skill_id not in ctx.skill_ids:
                errors.append(f"ACTOR_PROFILE: unknown skillId {skill_id!r}")
            else:
                skill = next(
                    (
                        document
                        for source_id, document in ctx.jsons.items()
                        if source_id.startswith("SKILL_EXAMPLE_")
                        and document.get("skillId") == skill_id
                    ),
                    None,
                )
                if skill is None or skill.get("classId") != class_id:
                    errors.append(f"ACTOR_PROFILE: {skill_id} does not belong to {class_id}")


def _validate_mobs(candidates: list[dict], ctx: Context, errors: list[str]) -> None:
    mobs = {
        candidate.get("targetId"): candidate
        for candidate in candidates
        if candidate.get("kind") == "MOB_PROFILE"
    }
    for mob_id in EXPECTED_MOBS:
        if mob_id not in mobs:
            errors.append(f"MOB_PROFILE: expected candidate {mob_id} is missing")
    for mob_id, candidate in mobs.items():
        definition = candidate.get("definition", {})
        records = []
        for record_id in _as_list(definition.get("spawnRecordIds")):
            record = ctx.spawn_by_id.get(record_id)
            if record is None:
                errors.append(f"MOB {mob_id}: unknown spawnRecordId {record_id!r}")
            else:
                records.append(record)
                if record.get("map_id") != TARGET_MAP_ID:
                    errors.append(f"MOB {mob_id}: spawn {record_id} is not on {TARGET_MAP_ID}")
                if mob_id not in (record.get("entity_id") or "").split("|"):
                    errors.append(f"MOB {mob_id}: spawn {record_id} does not contain {mob_id}")
        if not records:
            continue
        levels_min = min(int(record["character_level_min"]) for record in records)
        levels_max = max(int(record["character_level_max"]) for record in records)
        if definition.get("levelBand") != {"min": levels_min, "max": levels_max}:
            errors.append(f"MOB {mob_id}: levelBand does not match spawn records")
        reference_level = definition.get("referenceLevel")
        if not isinstance(reference_level, int) or not levels_min <= reference_level <= levels_max:
            errors.append(f"MOB {mob_id}: referenceLevel outside spawn levelBand")
            reference_level = levels_min
        base_hp = 120 + 24 * reference_level
        base_attack = 10 + 2 * reference_level
        base_defense = 2 + 0.8 * reference_level
        base = definition.get("baseStats", {})
        if base.get("hp") != base_hp:
            errors.append(f"MOB {mob_id}: base HP should be {base_hp}")
        if base.get("attack") != base_attack:
            errors.append(f"MOB {mob_id}: base Attack should be {base_attack}")
        if not _close(base.get("defense"), base_defense):
            errors.append(f"MOB {mob_id}: base Defense should be {base_defense}")
        multipliers = definition.get("multipliers", {})
        for key in ("hp", "attack", "defense"):
            value = multipliers.get(key)
            if not isinstance(value, (int, float)) or value <= 0:
                errors.append(f"MOB {mob_id}: invalid {key} multiplier")
        stats = definition.get("stats", {})
        for key, base_value in (("hp", base_hp), ("attack", base_attack), ("defense", base_defense)):
            multiplier = multipliers.get(key)
            if isinstance(multiplier, (int, float)) and not _close(
                stats.get(key), round(base_value * multiplier, 6)
            ):
                errors.append(f"MOB {mob_id}: stats.{key} does not apply multiplier once")
        for key in ("speedMetersPerSecond", "speedWuPerSecond", "aggroRadiusMeters", "aggroRadiusWu"):
            value = definition.get(key)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"MOB {mob_id}: invalid {key}")
        attack_ids = []
        for index, attack in enumerate(_as_list(definition.get("attacks"))):
            attack_id = attack.get("attackId")
            if attack_id in attack_ids:
                errors.append(f"MOB {mob_id}: duplicate attackId {attack_id!r}")
            attack_ids.append(attack_id)
            multiplier = attack.get("damageMultiplier")
            if not isinstance(multiplier, (int, float)) or multiplier <= 0:
                errors.append(f"MOB {mob_id}.attacks[{index}]: invalid damageMultiplier")
            for key in ("rangeMeters", "rangeWu", "telegraphSeconds"):
                value = attack.get(key)
                if value is not None and (not isinstance(value, (int, float)) or value < 0):
                    errors.append(f"MOB {mob_id}.attacks[{index}]: invalid {key}")
            minimum = 0.45 if attack.get("kind") == "BASIC" else 0.7
            telegraph = attack.get("telegraphSeconds")
            if telegraph is None:
                if not _has_unresolved(candidate, f"/attacks/{index}/telegraphSeconds"):
                    errors.append(f"MOB {mob_id}.attacks[{index}]: missing telegraph without unresolved entry")
            elif telegraph < minimum and not _has_unresolved(
                candidate, f"/attacks/{index}/telegraphSeconds"
            ):
                errors.append(
                    f"MOB {mob_id}.attacks[{index}]: telegraph {telegraph} below minimum {minimum}"
                )
        for loot_id in _as_list(definition.get("lootTableIds")):
            if loot_id not in ctx.loot_ids:
                errors.append(f"MOB {mob_id}: unknown lootTableId {loot_id!r}")


def _close(left, right) -> bool:
    return isinstance(left, (int, float)) and not isinstance(left, bool) and abs(left - right) < 1e-9


def _has_unresolved(candidate: dict, path: str) -> bool:
    return any(entry.get("path") == path for entry in _as_list(candidate.get("unresolved")))


def _validate_boss(candidates: list[dict], ctx: Context, errors: list[str]) -> None:
    bosses = [candidate for candidate in candidates if candidate.get("kind") == "BOSS_REFERENCE"]
    if len(bosses) != 1:
        errors.append(f"BOSS_REFERENCE: expected one boss reference, found {len(bosses)}")
        return
    candidate = bosses[0]
    definition = candidate.get("definition", {})
    if candidate.get("targetId") != EXPECTED_BOSS or definition.get("bossId") != EXPECTED_BOSS:
        errors.append(f"BOSS_REFERENCE: expected {EXPECTED_BOSS}")
    records = []
    for record_id in _as_list(definition.get("spawnRecordIds")):
        record = ctx.spawn_by_id.get(record_id)
        if record is None:
            errors.append(f"BOSS {EXPECTED_BOSS}: unknown spawnRecordId {record_id!r}")
        else:
            records.append(record)
            if record.get("map_id") != TARGET_MAP_ID:
                errors.append(f"BOSS {EXPECTED_BOSS}: spawn {record_id} is not on {TARGET_MAP_ID}")
            if EXPECTED_BOSS not in (record.get("entity_id") or "").split("|"):
                errors.append(f"BOSS {EXPECTED_BOSS}: spawn {record_id} does not contain the boss")
    if not records:
        return
    levels_min = min(int(record["character_level_min"]) for record in records)
    levels_max = max(int(record["character_level_max"]) for record in records)
    if definition.get("levelBand") != {"min": levels_min, "max": levels_max}:
        errors.append("BOSS: levelBand does not match spawn records")
    reference_level = definition.get("referenceLevel")
    if not isinstance(reference_level, int) or not levels_min <= reference_level <= levels_max:
        errors.append("BOSS: referenceLevel outside spawn levelBand")
        return
    base_hp = 120 + 24 * reference_level
    hp_factor = definition.get("hpFactor")
    if definition.get("baseHp") != base_hp:
        errors.append(f"BOSS: baseHp should be {base_hp}")
    if not isinstance(hp_factor, (int, float)) or hp_factor <= 0:
        errors.append("BOSS: invalid hpFactor")
        return
    if not _close(definition.get("hpSolo"), base_hp * hp_factor):
        errors.append("BOSS: hpSolo does not match baseHp * hpFactor")
    if not _close(definition.get("hpParty2"), base_hp * hp_factor * 1.65):
        errors.append("BOSS: hpParty2 does not match baseHp * hpFactor * 1.65")
    if not definition.get("partyScalingFormula"):
        errors.append("BOSS: missing partyScalingFormula")
    party_range = definition.get("partySizeRange", {})
    if (
        not isinstance(party_range.get("min"), int)
        or not isinstance(party_range.get("max"), int)
        or not 1 <= party_range["min"] <= party_range["max"] <= 5
    ):
        errors.append("BOSS: invalid partySizeRange")
    quest_record = ctx.spawn_by_id.get("MAN-BM-SPAWN_BM_05_QUEST")
    if quest_record:
        match = re.search(r"scale\s*(\d+)\s*[–-]\s*(\d+)", quest_record.get("condition", ""))
        if match and party_range != {"min": int(match.group(1)), "max": int(match.group(2))}:
            errors.append("BOSS: partySizeRange does not match manifest condition")
        ring = re.search(r"Ø\s*(\d+)", quest_record.get("condition", ""))
        arena = definition.get("arena", {})
        if ring and arena.get("ringDiameterWu") != int(ring.group(1)):
            errors.append("BOSS: arena ringDiameterWu does not match manifest condition")
    arena = definition.get("arena", {})
    _validate_positions([arena.get("anchor", {})], ctx.bounds_for(TARGET_MAP_ID), "BOSS.arena.anchor", errors)
    attacks = _as_list(definition.get("attacks"))
    if not attacks:
        errors.append("BOSS: no attacks")
    attack_ids = []
    for index, attack in enumerate(attacks):
        attack_id = attack.get("attackId")
        if attack_id in attack_ids:
            errors.append(f"BOSS: duplicate attackId {attack_id!r}")
        attack_ids.append(attack_id)
        shape = attack.get("shape")
        if shape == "CONE" and not isinstance(attack.get("coneAngleDegrees"), (int, float)):
            errors.append(f"BOSS.attacks[{index}]: CONE requires coneAngleDegrees")
        if shape == "CONE" and not isinstance(attack.get("rangeWu"), (int, float)):
            errors.append(f"BOSS.attacks[{index}]: CONE requires rangeWu")
        if shape == "CIRCLE" and not isinstance(attack.get("radiusWu"), (int, float)):
            errors.append(f"BOSS.attacks[{index}]: CIRCLE requires radiusWu")
        if shape == "ANNULUS":
            inner = attack.get("innerRadiusWu")
            outer = attack.get("outerRadiusWu")
            if not isinstance(inner, (int, float)) or not isinstance(outer, (int, float)) or inner > outer:
                errors.append(f"BOSS.attacks[{index}]: invalid ANNULUS radii")
        telegraph = attack.get("telegraphSeconds")
        if not isinstance(telegraph, (int, float)) or telegraph < 0.9:
            errors.append(f"BOSS.attacks[{index}]: AoE telegraph below 0.9s")
        for key in ("damageMultiplier", "recoverySeconds", "cooldownSeconds"):
            value = attack.get(key)
            if not isinstance(value, (int, float)) or value < 0:
                errors.append(f"BOSS.attacks[{index}]: invalid {key}")
    phases = _as_list(definition.get("phases"))
    previous_threshold = 1.0
    previous_phase = 0
    for index, phase in enumerate(phases):
        number = phase.get("phase")
        threshold = phase.get("hpThresholdFraction")
        if not isinstance(number, int) or number <= previous_phase:
            errors.append(f"BOSS.phases[{index}]: phase numbers must increase")
        previous_phase = number if isinstance(number, int) else previous_phase
        if not isinstance(threshold, (int, float)) or not 0 < threshold < previous_threshold:
            errors.append(f"BOSS.phases[{index}]: hpThresholdFraction must decrease in (0,1)")
        else:
            previous_threshold = threshold
    if definition.get("telegraphOverlap") is not False:
        errors.append("BOSS: telegraphOverlap must be false")
    if not definition.get("attackPriority"):
        errors.append("BOSS: missing attackPriority")
    for loot_id in _as_list(definition.get("lootTableIds")):
        if loot_id not in ctx.loot_ids:
            errors.append(f"BOSS: unknown lootTableId {loot_id!r}")


def _validate_items(candidates: list[dict], quests: dict[str, dict], ctx: Context, errors: list[str]) -> None:
    references: dict[str, dict] = {}
    per_quest: dict[str, int] = {quest_id: 0 for quest_id in EXPECTED_QUESTS}
    for candidate in candidates:
        if candidate.get("kind") != "ITEM_REFERENCE":
            continue
        definition = candidate.get("definition", {})
        reference_id = definition.get("referenceId")
        if reference_id in references:
            errors.append(f"ITEM_REFERENCE: duplicate referenceId {reference_id!r}")
        references[reference_id] = definition
        quest_id = definition.get("questId")
        if quest_id not in quests:
            errors.append(f"ITEM_REFERENCE {reference_id}: unknown questId {quest_id!r}")
        else:
            per_quest[quest_id] += 1
        resolution = definition.get("resolution")
        if resolution == "RESOLVED":
            item_id = definition.get("resolvedItemId")
            item = ctx.item_by_id.get(item_id)
            if item is None:
                errors.append(f"ITEM_REFERENCE {reference_id}: unknown itemId {item_id!r}")
                continue
            category = ITEM_CATEGORY_MAP.get(item.get("category", ""))
            rarity = ITEM_RARITY_MAP.get(item.get("rarity_pool", ""))
            if definition.get("category") != category:
                errors.append(f"ITEM_REFERENCE {reference_id}: category does not match catalog")
            if definition.get("catalogSlotVi") != item.get("slot"):
                errors.append(f"ITEM_REFERENCE {reference_id}: catalogSlotVi does not match catalog")
            if definition.get("requiredLevel") != int(item.get("required_level", 0)):
                errors.append(f"ITEM_REFERENCE {reference_id}: requiredLevel does not match catalog")
            if definition.get("rarity") != rarity:
                errors.append(f"ITEM_REFERENCE {reference_id}: rarity does not match catalog")
        elif resolution == "UNRESOLVED":
            if definition.get("resolvedItemId") is not None:
                errors.append(f"ITEM_REFERENCE {reference_id}: unresolved reference has resolvedItemId")
            if not _has_unresolved(candidate, "/resolvedItemId"):
                errors.append(f"ITEM_REFERENCE {reference_id}: unresolved reference lacks blocking entry")
        elif resolution == "CLASS_CONDITIONAL":
            choices = _as_list(definition.get("classCandidates"))
            seen_classes = set()
            if definition.get("resolvedItemId") is not None:
                errors.append(f"ITEM_REFERENCE {reference_id}: conditional reference must not preselect a player class")
            for choice in choices:
                item = ctx.item_rarity_by_id.get(choice.get("itemId"), {})
                class_id = choice.get("classId")
                if class_id in seen_classes or item.get("class_id") != class_id or item.get("rarity_pool") != "Thường" or item.get("required_level") != "1" or item.get("category") != "Trang bị / vũ khí":
                    errors.append(f"ITEM_REFERENCE {reference_id}: invalid conditional class/item mapping")
                seen_classes.add(class_id)
            expected_classes = {r['class_id'] for r in ctx.item_master_by_id.values() if r['category']=='Trang bị / vũ khí'}
            if seen_classes != expected_classes:
                errors.append(f"ITEM_REFERENCE {reference_id}: conditional class coverage is incomplete")
        else:
            errors.append(f"ITEM_REFERENCE {reference_id}: invalid resolution {resolution!r}")
        for item_id in _as_list(definition.get("candidateItemIds")):
            if item_id not in ctx.item_by_id:
                errors.append(f"ITEM_REFERENCE {reference_id}: unknown candidateItemId {item_id!r}")
    for quest_id, count in per_quest.items():
        if count == 0:
            errors.append(f"ITEM_REFERENCE: quest {quest_id} has no item reference")


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


def _validate_bundle_summary(bundle: dict, candidates: list[dict], errors: list[str]) -> None:
    summary = bundle.get("summary", {})
    expected_counts = {
        "candidateCount": len(candidates),
        "readyCount": sum(1 for candidate in candidates if candidate.get("status") == "READY_FOR_REVIEW"),
        "blockedCount": sum(
            1 for candidate in candidates if candidate.get("status") == "BLOCKED_UNRESOLVED"
        ),
        "unresolvedCount": sum(len(_as_list(candidate.get("unresolved"))) for candidate in candidates),
    }
    if summary != expected_counts:
        errors.append(f"bundle: summary {summary!r} does not match {expected_counts!r}")
    blocked = any(
        candidate.get("status") == "BLOCKED_UNRESOLVED"
        or any(entry.get("blocking") for entry in _as_list(candidate.get("unresolved")))
        for candidate in candidates
    )
    activation = bundle.get("activation", {})
    if activation.get("eligible") is not (not blocked):
        errors.append("bundle: activation.eligible is inconsistent with unresolved state")
    if activation.get("blockedByUnresolved") is not blocked:
        errors.append("bundle: activation.blockedByUnresolved is inconsistent")
    if activation.get("requiresReview") is not True:
        errors.append("bundle: activation.requiresReview must be true")
    if activation.get("runtimeActivationAllowed") is not False:
        errors.append("bundle: runtimeActivationAllowed must stay false for candidates")
    if not activation.get("reason"):
        errors.append("bundle: activation.reason is empty")
    expected_status = "BLOCKED_UNRESOLVED" if blocked else "READY_FOR_REVIEW"
    if bundle.get("status") != expected_status:
        errors.append(f"bundle: status should be {expected_status!r}")
    if bundle.get("bundleId") != BUNDLE_ID:
        errors.append(f"bundle: bundleId should be {BUNDLE_ID!r}")
    if bundle.get("targetMapId") != TARGET_MAP_ID:
        errors.append(f"bundle: targetMapId should be {TARGET_MAP_ID!r}")


def validate_bundle(bundle: dict, ctx: Context, root=None, verify_sources: bool = True) -> list[str]:
    errors: list[str] = []
    root = Path(root or ctx.root).resolve()
    if not isinstance(bundle, dict):
        return ["bundle: expected object"]
    schema_cache: dict[Path, dict] = {}
    schema_path = root / "Implementation/Tools/ContentPipeline/schemas/candidate_bundle.schema.json"
    _validate_schema_document(bundle, schema_path, "bundle", errors)
    if errors:
        return errors
    _validate_bundle_digest(bundle, errors)

    source_map = _validate_sources(bundle, ctx, root, errors) if verify_sources else {
        entry.get("sourceId"): entry for entry in _as_list(bundle.get("sources")) if isinstance(entry, dict)
    }
    candidates = _as_list(bundle.get("candidates"))
    seen_ids: set[str] = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            errors.append("bundle.candidates: expected objects")
            continue
        candidate_id = candidate.get("candidateId")
        if candidate_id in seen_ids:
            errors.append(f"bundle.candidates: duplicate candidateId {candidate_id!r}")
        seen_ids.add(candidate_id)
        _validate_candidate(candidate, root, schema_cache, source_map, errors)

    _validate_bundle_summary(bundle, candidates, errors)
    quests = _validate_quests(candidates, ctx, errors)
    _validate_objective_maps(candidates, quests, ctx, errors)
    _validate_actor(candidates, ctx, errors)
    _validate_mobs(candidates, ctx, errors)
    _validate_boss(candidates, ctx, errors)
    _validate_items(candidates, quests, ctx, errors)
    return errors


# ---------------------------------------------------------------------------
# Field-level diff


def _flatten(value, base: str = ""):
    if isinstance(value, dict):
        if not value:
            yield (base or "/", value)
            return
        for key in sorted(value):
            yield from _flatten(value[key], _join_pointer(base, key))
    elif isinstance(value, list):
        if not value:
            yield (base or "/", value)
            return
        for index, child in enumerate(value):
            yield from _flatten(child, _join_pointer(base, index))
    else:
        yield (base or "/", value)


def field_diff(old, new) -> list[dict]:
    old_flat = dict(_flatten(old))
    new_flat = dict(_flatten(new))
    changes = []
    for path in sorted(set(old_flat) | set(new_flat)):
        if path not in old_flat:
            changes.append({"path": path, "change": "added", "old": None, "new": new_flat[path]})
        elif path not in new_flat:
            changes.append({"path": path, "change": "removed", "old": old_flat[path], "new": None})
        elif old_flat[path] != new_flat[path]:
            changes.append(
                {
                    "path": path,
                    "change": "changed",
                    "old": old_flat[path],
                    "new": new_flat[path],
                }
            )
    return changes


def format_diff(changes: list[dict], as_json: bool = False) -> str:
    if as_json:
        return json.dumps(changes, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    lines = []
    for change in changes:
        if change["change"] == "added":
            lines.append(f"+ {change['path']} = {json.dumps(change['new'], ensure_ascii=False, sort_keys=True)}")
        elif change["change"] == "removed":
            lines.append(f"- {change['path']} = {json.dumps(change['old'], ensure_ascii=False, sort_keys=True)}")
        else:
            lines.append(
                f"~ {change['path']}: "
                f"{json.dumps(change['old'], ensure_ascii=False, sort_keys=True)} -> "
                f"{json.dumps(change['new'], ensure_ascii=False, sort_keys=True)}"
            )
    return "\n".join(lines) + ("\n" if lines else "")


__all__ = [
    "EXPECTED_ACTOR",
    "EXPECTED_BOSS",
    "EXPECTED_MOBS",
    "EXPECTED_QUESTS",
    "field_diff",
    "format_diff",
    "load_json_file",
    "pointer_exists",
    "pointer_get",
    "validate_bundle",
]
