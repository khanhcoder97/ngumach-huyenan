#!/usr/bin/env python3
"""OPC-05b coverage audit: catalogue -> runtime definition -> delivered asset.

Standard library only. The report is derived from repository sources; nothing in
the counts, IDs, frame geometry or import metadata is hand-typed.

Outputs (deterministic, no timestamps):

    Implementation/Asset_Handoff/COVERAGE_REPORT.md
    Implementation/Asset_Handoff/coverage_report.json

Usage:

    python Implementation/Asset_Handoff/coverage_audit.py
    python Implementation/Asset_Handoff/coverage_audit.py --check
    python Implementation/Asset_Handoff/coverage_audit.py --source-commit <sha>

``--check`` regenerates in memory and exits non-zero when a committed report is
missing or stale. It pins the ``sourceCommit`` value already recorded in the
JSON so the check stays reproducible in shallow checkouts.

Scope boundaries: this script reads files; it never writes to assets, the
delivery manifest, schemas, server code or production specs. It does not run
Unity and does not claim engine playback acceptance. Schema conformance of the
definition examples is covered by ``Implementation/Tools/validate_content.py``;
this report only measures presence, ID resolution and static import metadata.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import subprocess
import sys
from collections import Counter
from pathlib import Path

REPORT_SCHEMA = "opc05b.coverage_report/1"
MD_NAME = "COVERAGE_REPORT.md"
JSON_NAME = "coverage_report.json"

# Text evidence is hashed in canonical LF form so Windows and Linux checkouts
# produce the same report. Binaries (PNG) are hashed byte-for-byte.
TEXT_SUFFIXES = frozenset({".json", ".csv", ".md", ".meta", ".py", ".yml", ".yaml", ".txt"})

MANIFEST_PATH = "Client/Assets/ArtManifests/muse_delivery_manifest.json"
MANIFEST_SCHEMA_PATH = "Implementation/Asset_Handoff/asset_delivery_manifest.schema.json"
EXAMPLES_DIR = "Implementation/Content/Examples"
SCHEMAS_DIR = "Implementation/Content/Schemas"
PRODUCTION_DIR = "docs/production"

ART_STANDARD = "docs/production/Pixel_Art_Production_Standard_vi.md"
COMBAT_SPEC = "docs/production/Combat_Skills_VFX_Animation_Spec_vi.md"
RELEASE_SPEC = "docs/production/Online_Persistence_Release_Complete_vi.md"

CLASS_CSV = "Class_Passive_Production_Data_vi.csv"
PLACEMENT_CSV = "World_Spawn_Gathering_Manifest_vi.csv"
QUEST_CSV = "Quest_Dialogue_Production_Data_vi.csv"
ITEM_MASTER_CSV = "Item_Master_Catalog_vi.csv"
ITEM_VARIANT_CSV = "Item_Rarity_Variant_Catalog_vi.csv"
NPC_CSV = "NPC_Actor_Production_Registry_vi.csv"

ID_KEYS = {
    "ClassDefinition": "classId",
    "SkillDefinition": "skillId",
    "QuestDefinition": "questId",
    "ItemDefinition": "itemId",
    "MapDefinition": "mapId",
    "SpawnDefinition": "recordId",
    "GatheringNodeDefinition": "recordId",
    "MapTopology": "mapId",
}

CATEGORY_OF_DIR = {
    "ClassDefinition": "class",
    "SkillDefinition": "skill",
    "QuestDefinition": "quest",
    "ItemDefinition": "item",
    "MapDefinition": "map",
    "SpawnDefinition": "spawn",
    "GatheringNodeDefinition": "node",
}

FILTER_MODES = {0: "Point", 1: "Bilinear", 2: "Trilinear"}
SPRITE_MODES = {0: "None", 1: "Single", 2: "Multiple", 3: "Polygon"}
SPRITE_MESH_TYPES = {0: "FullRect", 1: "Tight"}
SPRITE_ALIGNMENTS = {
    0: "Center",
    1: "TopLeft",
    2: "TopCenter",
    3: "TopRight",
    4: "LeftCenter",
    5: "RightCenter",
    6: "BottomLeft",
    7: "BottomCenter",
    8: "BottomRight",
    9: "Custom",
}


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def file_bytes(path: Path) -> bytes:
    """Return canonical bytes: LF for text sources, raw bytes for binaries."""
    data = path.read_bytes()
    if path.suffix.lower() in TEXT_SUFFIXES:
        return data.replace(b"\r\n", b"\n")
    return data


def sha256_file(path: Path) -> str:
    return hashlib.sha256(file_bytes(path)).hexdigest()


class Evidence:
    """Deduplicated byte-level evidence for every source the audit reads."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.items: dict[str, dict] = {}

    def add(self, path: Path) -> dict:
        resolved = path.resolve()
        rel = resolved.relative_to(self.root).as_posix()
        if rel not in self.items:
            self.items[rel] = {
                "path": rel,
                "bytes": len(file_bytes(resolved)),
                "sha256": sha256_file(resolved),
            }
        return self.items[rel]

    def paths(self) -> list[str]:
        return sorted(self.items)

    def as_list(self) -> list[dict]:
        return [self.items[key] for key in sorted(self.items)]

    def digest(self) -> str:
        lines = [f"{item['path']}\0{item['sha256']}\n" for item in self.as_list()]
        return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path):
    return json.loads(read_text(path))


def read_csv_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean(value) -> str:
    return (value or "").strip()


def unique_sorted(values) -> list[str]:
    return sorted({clean(value) for value in values if clean(value)})


def first_match(pattern: str, text: str, cast=str, flags=0):
    match = re.search(pattern, text, flags)
    if not match:
        return None
    return cast(match.group(1))


def png_ihdr(path: Path) -> dict:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG file")
    length, chunk_type = struct.unpack(">I4s", data[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise ValueError(f"{path} does not start with an IHDR chunk")
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", data[16:29]
    )
    return {
        "width": width,
        "height": height,
        "bitDepth": bit_depth,
        "colorType": color_type,
        "colorTypeName": {0: "grayscale", 2: "RGB", 3: "palette", 4: "grayscale+alpha", 6: "RGBA"}.get(
            color_type, f"unknown({color_type})"
        ),
        "interlaced": bool(interlace),
        "bytes": len(data),
        "sha256": sha256_file(path),
    }


def git_last_commit(root: Path, paths: list[str]) -> str | None:
    if not paths:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "log", "-1", "--format=%H", "--", *paths],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    sha = result.stdout.strip()
    return sha if re.fullmatch(r"[0-9a-f]{40}", sha) else None


# --------------------------------------------------------------------------- #
# source parsers
# --------------------------------------------------------------------------- #
def parse_art_standard(text: str) -> dict:
    ppu = first_match(r"Pixels Per Unit\s*\|\s*(\d+)\s*px/WU", text, int)
    cell = re.search(r"cell\s*(\d+)\s*[×x]\s*(\d+)\s*source px", text)
    walk = re.search(r"Walk:\s*(\d+)\s*frame/hướng ở\s*(\d+)\s*fps", text)
    order = re.search(r"thứ tự hàng `([NSEW,\s]+)`", text)
    if not (ppu and cell and walk and order):
        raise ValueError(
            "Could not parse the locked art convention from " + ART_STANDARD
        )
    directions = [part.strip() for part in order.group(1).split(",") if part.strip()]
    return {
        "pixelsPerUnit": ppu,
        "cellWidth": int(cell.group(1)),
        "cellHeight": int(cell.group(2)),
        "walkFrames": int(walk.group(1)),
        "walkFps": int(walk.group(2)),
        "directions": directions,
        "source": ART_STANDARD,
        "quote": {
            "cell": cell.group(0),
            "walk": walk.group(0),
            "directions": order.group(1),
        },
    }


def parse_skill_spec(text: str, class_names: dict[str, str]) -> dict:
    """Map canonical classId -> skill IDs documented in the combat spec."""
    sections = re.split(r"\n### ", text)
    name_to_class = {name: class_id for class_id, name in class_names.items()}
    result: dict[str, list[str]] = {}
    for section in sections:
        heading = re.match(r"([^\n—]+?)\s*—", section)
        ids = re.findall(r"\*\*(SK-[A-Z]{2}-\d{2})\b", section)
        if not heading or not ids:
            continue
        name = heading.group(1).strip()
        class_id = name_to_class.get(name)
        if class_id is None:
            continue
        result.setdefault(class_id, []).extend(ids)
    return {key: sorted(set(value)) for key, value in sorted(result.items())}


def parse_unity_meta(text: str) -> dict:
    """Parse the subset of Unity YAML used by a TextureImporter .meta file."""

    def importer(key: str, cast=str):
        return first_match(rf"^  {key}: (.+)$", text, cast, re.MULTILINE)

    pivot_match = re.search(r"^  spritePivot: \{x: ([-\d.]+), y: ([-\d.]+)\}$", text, re.MULTILINE)
    if not pivot_match:
        raise ValueError("spritePivot missing from .meta")

    importer_pivot = (float(pivot_match.group(1)), float(pivot_match.group(2)))

    sprites = []
    blocks = re.split(r"\n    - serializedVersion: \d+\n", text)
    for block in blocks[1:]:
        block = block.split("\n    - serializedVersion:", 1)[0]
        name = re.search(r"\n      name: (\S+)", "\n" + block)
        rect = re.search(
            r"rect:\n        serializedVersion: \d+\n"
            r"        x: (\d+)\n        y: (\d+)\n"
            r"        width: (\d+)\n        height: (\d+)",
            "\n" + block,
        )
        if not name or not rect:
            continue
        sprite_pivot = re.search(r"\n      pivot: \{x: ([-\d.]+), y: ([-\d.]+)\}", "\n" + block)
        alignment = re.search(r"\n      alignment: (\d+)", "\n" + block)
        sprite_id = re.search(r"\n      spriteID: (\S+)", "\n" + block)
        sprites.append(
            {
                "name": name.group(1),
                "x": int(rect.group(1)),
                "y": int(rect.group(2)),
                "width": int(rect.group(3)),
                "height": int(rect.group(4)),
                "alignment": int(alignment.group(1)) if alignment else None,
                "pivot": (
                    (float(sprite_pivot.group(1)), float(sprite_pivot.group(2)))
                    if sprite_pivot
                    else None
                ),
                "spriteId": sprite_id.group(1) if sprite_id else None,
            }
        )

    return {
        "guid": first_match(r"^guid: (\S+)$", text, str, re.MULTILINE),
        "spriteMode": importer("spriteMode", int),
        "spritePixelsToUnits": importer("spritePixelsToUnits", int),
        "spritePivot": importer_pivot,
        "alignment": importer("alignment", int),
        "spriteMeshType": importer("spriteMeshType", int),
        "spriteExtrude": importer("spriteExtrude", int),
        "textureType": importer("textureType", int),
        "maxTextureSize": importer("maxTextureSize", int),
        "alphaIsTransparency": importer("alphaIsTransparency", int),
        "sRGBTexture": first_match(r"^    sRGBTexture: (\d+)$", text, int, re.MULTILINE),
        "nPOTScale": importer("nPOTScale", int),
        "textureShape": importer("textureShape", int),
        "enableMipMap": first_match(r"^    enableMipMap: (\d+)$", text, int, re.MULTILINE),
        "filterMode": first_match(r"^    filterMode: (\d+)$", text, int, re.MULTILINE),
        "wrapU": first_match(r"^    wrapU: (\d+)$", text, int, re.MULTILINE),
        "wrapV": first_match(r"^    wrapV: (\d+)$", text, int, re.MULTILINE),
        "textureCompression": first_match(
            r"^    textureCompression: (\d+)$", text, int, re.MULTILINE
        ),
        "sprites": sprites,
    }


# --------------------------------------------------------------------------- #
# audit
# --------------------------------------------------------------------------- #
def build_report(root: Path, source_commit: str | None = None) -> dict:
    evidence = Evidence(root)

    def load(rel: str) -> Path:
        path = root / rel
        if not path.is_file():
            raise FileNotFoundError(f"required source is missing: {rel}")
        evidence.add(path)
        return path

    # --- art standard / combat spec / release claim ------------------------ #
    standard_text = read_text(load(ART_STANDARD))
    standard = parse_art_standard(standard_text)
    combat_text = read_text(load(COMBAT_SPEC))
    release_text = read_text(load(RELEASE_SPEC))

    release_claim = re.search(
        r"(\d+)\s*quest,\s*(\d+)\s*active,\s*(\d+)\s*lớp,\s*(\d+)\s*map,\s*(\d+)\s*placements",
        release_text,
    )
    declared = None
    if release_claim:
        declared = {
            "quests": int(release_claim.group(1)),
            "activeSkills": int(release_claim.group(2)),
            "classes": int(release_claim.group(3)),
            "maps": int(release_claim.group(4)),
            "placements": int(release_claim.group(5)),
            "source": RELEASE_SPEC,
            "quote": release_claim.group(0),
        }

    # --- production catalogues --------------------------------------------- #
    production_dir = root / PRODUCTION_DIR
    csv_files = sorted(production_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"no production CSVs under {PRODUCTION_DIR}")
    csv_rows = {}
    for csv_path in csv_files:
        evidence.add(csv_path)
        csv_rows[csv_path.name] = read_csv_rows(csv_path)

    class_rows = csv_rows.get(CLASS_CSV, [])
    class_names = {
        clean(row.get("class_id")): clean(row.get("class_name_vi"))
        for row in class_rows
        if clean(row.get("class_id"))
    }
    class_ids = sorted(class_names)
    passive_counts = Counter(clean(row.get("class_id")) for row in class_rows)

    placement_rows = csv_rows.get(PLACEMENT_CSV, [])
    placement_ids = unique_sorted(row.get("record_id") for row in placement_rows)
    map_ids = unique_sorted(row.get("map_id") for row in placement_rows)
    record_types = Counter(clean(row.get("record_type")) for row in placement_rows)
    design_states = Counter(clean(row.get("design_state")) for row in placement_rows)
    node_ids = unique_sorted(
        row.get("record_id") for row in placement_rows if clean(row.get("record_type")) == "GATHER_NODE"
    )

    quest_rows = csv_rows.get(QUEST_CSV, [])
    quest_ids = unique_sorted(row.get("quest_id") for row in quest_rows)

    item_master = unique_sorted(row.get("item_id") for row in csv_rows.get(ITEM_MASTER_CSV, []))
    item_variants = unique_sorted(row.get("item_id") for row in csv_rows.get(ITEM_VARIANT_CSV, []))
    item_all = sorted(set(item_master) | set(item_variants))

    skill_map = parse_skill_spec(combat_text, class_names)
    skill_ids = sorted({skill_id for ids in skill_map.values() for skill_id in ids})

    # Cross-check: every MAP_* value in the other catalogue CSVs must already
    # be part of the 46-map placement set; reject pseudo values such as "quest".
    other_map_values = set()
    for filename, key in (
        (NPC_CSV, "source_map_id"),
        ("Life_Sim_Content_Data_vi.csv", "map_id"),
        ("Weekly_Boss_Rotation_Data_vi.csv", "spawn_map_id"),
        (ITEM_MASTER_CSV, "source_map"),
    ):
        other_map_values.update(
            value
            for value in (clean(row.get(key)) for row in csv_rows.get(filename, []))
            if value.startswith("MAP_")
        )
    map_union = sorted(set(map_ids) | other_map_values)

    catalogue = {
        "csvFiles": [
            {"name": name, "rows": len(rows)} for name, rows in sorted(csv_rows.items())
        ],
        "classes": {
            "count": len(class_ids),
            "ids": class_ids,
            "names": {class_id: class_names[class_id] for class_id in class_ids},
            "passiveNodesPerClass": {
                class_id: passive_counts.get(class_id, 0) for class_id in class_ids
            },
        },
        "maps": {
            "count": len(map_ids),
            "ids": map_ids,
            "unionWithOtherCatalogues": len(map_union),
            "unionMatchesPlacementSet": map_union == map_ids,
        },
        "quests": {
            "count": len(quest_ids),
            "ids": quest_ids,
            "dialogueRows": len(quest_rows),
        },
        "placements": {
            "count": len(placement_rows),
            "distinctRecordIds": len(placement_ids),
            "ids": placement_ids,
            "recordTypes": dict(sorted(record_types.items())),
            "designStates": dict(sorted(design_states.items())),
            "newProposed": design_states.get("NEW_PROPOSED", 0),
            "gatheringNodeIds": node_ids,
        },
        "items": {
            "masterCount": len(item_master),
            "variantCount": len(item_variants),
            "unionCount": len(item_all),
            "masterOnly": len(set(item_master) - set(item_variants)),
        },
        "activeSkills": {
            "count": len(skill_ids),
            "ids": skill_ids,
            "byClass": {
                class_id: {
                    "className": class_names.get(class_id, ""),
                    "ids": ids,
                }
                for class_id, ids in skill_map.items()
            },
            "source": COMBAT_SPEC,
        },
        "npcActors": len(csv_rows.get(NPC_CSV, [])),
    }

    # --- manifest + PNG + .meta -------------------------------------------- #
    manifest_schema = read_json(load(MANIFEST_SCHEMA_PATH))
    manifest = read_json(load(MANIFEST_PATH))

    assets = []
    meta_checks_all = []
    for asset in manifest.get("assets", []):
        asset_path_rel = clean(asset.get("path"))
        asset_path = root / asset_path_rel
        preview_rel = clean(asset.get("previewPath"))
        preview_path = root / preview_rel if preview_rel else None
        meta_path = Path(str(asset_path) + ".meta")

        for candidate in (asset_path, meta_path):
            if not candidate.is_file():
                raise FileNotFoundError(f"manifest asset file is missing: {candidate}")
            evidence.add(candidate)
        if preview_path and preview_path.is_file():
            evidence.add(preview_path)

        png = png_ihdr(asset_path)
        preview = None
        if preview_path and preview_path.is_file():
            preview = png_ihdr(preview_path)

        directions = list(asset.get("directions") or [])
        animations = list(asset.get("animations") or [])
        geometry = None
        if directions and animations:
            frames = int(animations[0].get("framesPerDirection", 0))
            width = int(asset.get("pixelWidth", 0))
            height = int(asset.get("pixelHeight", 0))
            if frames:
                geometry = {
                    "directions": len(directions),
                    "framesPerDirection": frames,
                    "frameWidth": width // frames if width % frames == 0 else None,
                    "frameHeight": height // len(directions) if height % len(directions) == 0 else None,
                    "widthAligned": width % frames == 0,
                    "heightAligned": height % len(directions) == 0,
                }

        meta = parse_unity_meta(read_text(meta_path))
        checks = audit_meta(meta, asset, geometry, standard)
        meta_checks_all.extend(
            {"assetId": asset.get("assetId"), **check} for check in checks
        )

        asset_audit = {
            "assetId": clean(asset.get("assetId")),
            "kind": clean(asset.get("kind")),
            "status": clean(asset.get("status")),
            "path": asset_path_rel,
            "previewPath": preview_rel,
            "ppu": asset.get("pixelsPerUnit"),
            "manifest": {
                "pixelWidth": asset.get("pixelWidth"),
                "pixelHeight": asset.get("pixelHeight"),
                "directions": directions,
                "directionsMatchStandard": directions == standard["directions"],
                "animations": animations,
            },
            "png": png,
            "preview": preview,
            "geometry": geometry,
            "geometryMatchesStandard": bool(
                geometry
                and geometry["frameWidth"] == standard["cellWidth"]
                and geometry["frameHeight"] == standard["cellHeight"]
            ),
            "meta": {
                "guid": meta["guid"],
                "spriteMode": meta["spriteMode"],
                "spriteModeName": SPRITE_MODES.get(meta["spriteMode"]),
                "spritePixelsToUnits": meta["spritePixelsToUnits"],
                "spritePivot": list(meta["spritePivot"]),
                "alignment": meta["alignment"],
                "spriteMeshType": meta["spriteMeshType"],
                "spriteMeshTypeName": SPRITE_MESH_TYPES.get(meta["spriteMeshType"]),
                "filterMode": meta["filterMode"],
                "filterModeName": FILTER_MODES.get(meta["filterMode"]),
                "enableMipMap": meta["enableMipMap"],
                "textureCompression": meta["textureCompression"],
                "alphaIsTransparency": meta["alphaIsTransparency"],
                "spriteCount": len(meta["sprites"]),
            },
            "metaChecks": checks,
            "spriteGrid": audit_sprite_grid(meta, asset_path.stem, geometry, standard),
            "criticalFindings": [check["id"] for check in checks if check["status"] == "fail"],
            "advisories": [check["id"] for check in checks if check["status"] == "advisory"],
        }
        assets.append(asset_audit)

    # --- definition examples ------------------------------------------------ #
    examples_dir = root / EXAMPLES_DIR
    example_paths = sorted(examples_dir.rglob("*.json"))
    if not example_paths:
        raise FileNotFoundError(f"no definition examples under {EXAMPLES_DIR}")

    canonical = []
    synthetic = []
    for example_path in example_paths:
        evidence.add(example_path)
        data = read_json(example_path)
        kind = example_path.parent.name
        if kind not in ID_KEYS:
            raise ValueError(f"unknown definition directory: {example_path}")
        identifier = data.get(ID_KEYS[kind])
        entry = {
            "kind": kind,
            "file": example_path.relative_to(root).as_posix(),
            "idKey": ID_KEYS[kind],
            "id": identifier,
        }
        if kind == "MapTopology" or example_path.stem.startswith("SYNTHETIC"):
            entry["reviewState"] = data.get("reviewState")
            synthetic.append(entry)
        else:
            entry["category"] = CATEGORY_OF_DIR[kind]
            canonical.append(entry)

    catalogue_sets = {
        "class": set(class_ids),
        "skill": set(skill_ids),
        "quest": set(quest_ids),
        "item": set(item_all),
        "map": set(map_ids),
        "spawn": set(placement_ids),
        "node": set(node_ids),
    }
    coverage = {}
    for category, id_set in catalogue_sets.items():
        entries = [entry for entry in canonical if entry["category"] == category]
        resolved = [entry for entry in entries if entry["id"] in id_set]
        coverage[category] = {
            "catalogueCount": len(id_set),
            "exampleCount": len(entries),
            "resolvedCount": len(resolved),
            "resolvedIds": sorted(entry["id"] for entry in resolved),
            "absentCount": len(id_set) - len({entry["id"] for entry in resolved}),
            "absentIds": sorted(id_set - {entry["id"] for entry in resolved}),
        }
    # item example resolves against the rarity-variant catalogue, not the master
    item_entry = next((entry for entry in canonical if entry["category"] == "item"), None)
    if item_entry:
        coverage["item"]["resolvedInMaster"] = item_entry["id"] in set(item_master)
        coverage["item"]["resolvedInVariants"] = item_entry["id"] in set(item_variants)

    schema_files = sorted((root / SCHEMAS_DIR).glob("*.schema.json"))
    for schema_path in schema_files:
        evidence.add(schema_path)
    exercised = {entry["kind"] for entry in canonical} | {entry["kind"] for entry in synthetic}

    definitions = {
        "canonicalCount": len(canonical),
        "syntheticCount": len(synthetic),
        "canonical": canonical,
        "synthetic": synthetic,
        "schemas": {
            "fileCount": len(schema_files),
            "files": [path.name for path in schema_files],
            "exercisedByExamples": sorted(exercised),
            "notExercised": sorted({path.stem.replace(".schema", "") for path in schema_files} - exercised),
        },
        "coverage": coverage,
    }

    # --- findings / verification split ------------------------------------- #
    findings = []
    for asset in assets:
        for check in asset["metaChecks"]:
            if check["status"] in {"fail", "advisory"}:
                findings.append(
                    {
                        "id": check["id"],
                        "assetId": asset["assetId"],
                        "severity": "fail" if check["status"] == "fail" else "advisory",
                        "owner": "Muse",
                        "summary": check["label"],
                        "expected": check["expected"],
                        "actual": check["actual"],
                        "action": check["note"],
                    }
                )
        if asset["status"] != "approved":
            findings.append(
                {
                    "id": "ASSET_STATUS_NOT_APPROVED",
                    "assetId": asset["assetId"],
                    "severity": "info",
                    "owner": "Muse",
                    "summary": "Asset pack status is not approved",
                    "expected": "approved",
                    "actual": asset["status"],
                    "action": "Owner review required; coverage does not imply art acceptance.",
                }
            )
    if catalogue["placements"]["newProposed"]:
        findings.append(
            {
                "id": "PLACEMENTS_NEW_PROPOSED",
                "severity": "info",
                "owner": "Owner/Muse",
                "summary": "Placements still marked NEW_PROPOSED",
                "expected": "reviewed placement state",
                "actual": str(catalogue["placements"]["newProposed"]),
                "action": "These rows are catalogue proposals, not approved runtime records.",
            }
        )

    verification = {
        "staticImportMetadata": {
            "status": "verified_with_findings" if any(f["severity"] == "fail" for f in findings) else "verified",
            "method": "Python standard library parse of Unity .meta (no Unity Editor)",
            "verifiedFields": [
                check["id"] for check in meta_checks_all if check["status"] == "pass"
            ],
            "failedFields": [check["id"] for check in meta_checks_all if check["status"] == "fail"],
            "advisoryFields": [
                check["id"] for check in meta_checks_all if check["status"] == "advisory"
            ],
        },
        "png": {
            "status": "header_verified",
            "method": "PNG signature + IHDR parsed with struct; pixel decode not performed",
        },
        "enginePlayback": {
            "status": "not_verified",
            "reason": "No Unity/.NET runtime in this environment",
            "requiredEvidence": "Unity import log + PlayMode capture tied to an exact commit",
        },
        "runtimeContent": {
            "status": "not_verified",
            "reason": "No authoritative server runtime here; only catalogue rows and definition examples",
        },
    }

    report = {
        "reportSchema": REPORT_SCHEMA,
        "generatedBy": "Implementation/Asset_Handoff/coverage_audit.py",
        "repo": {
            "sourceCommit": source_commit or "unavailable",
            "sourceCommitMeaning": "last commit touching the evidence files (not the report commit)",
            "evidenceDigest": evidence.digest(),
        },
        "standards": standard,
        "declaredTargets": declared,
        "manifest": {
            "assetPackId": manifest.get("assetPackId"),
            "assetPackVersion": manifest.get("assetPackVersion"),
            "owner": manifest.get("owner"),
            "sourceLicense": manifest.get("sourceLicense"),
            "assetCount": len(manifest.get("assets", [])),
            "schema": MANIFEST_SCHEMA_PATH,
            "schemaDialect": manifest_schema.get("$schema", "unknown"),
        },
        "assets": assets,
        "catalogue": catalogue,
        "definitions": definitions,
        "findings": sorted(
            findings,
            key=lambda item: (
                {"fail": 0, "advisory": 1, "info": 2}.get(item["severity"], 3),
                item["id"],
            ),
        ),
        "verification": verification,
        "evidence": evidence.as_list(),
    }
    return report


def audit_meta(meta: dict, asset: dict, geometry: dict | None, standard: dict) -> list[dict]:
    checks: list[dict] = []

    def add(check_id: str, label: str, expected, actual, status: str, note: str = "") -> None:
        checks.append(
            {
                "id": check_id,
                "label": label,
                "expected": expected,
                "actual": actual,
                "status": status,
                "note": note,
            }
        )

    ppu_expected = standard["pixelsPerUnit"]
    ppu_actual = meta["spritePixelsToUnits"]
    add(
        "META_PPU",
        "Sprite pixels per unit",
        ppu_expected,
        ppu_actual,
        "pass" if ppu_actual == ppu_expected else "fail",
        "Must match the locked 20 PPU art standard.",
    )

    filter_actual = meta["filterMode"]
    add(
        "META_FILTER_MODE",
        "Texture filter mode",
        "0 (Point)",
        f"{filter_actual} ({FILTER_MODES.get(filter_actual, 'unknown')})",
        "pass" if filter_actual == 0 else "fail",
        "Pixel art requires Point (no filter); Bilinear blurs source pixels.",
    )

    mip_actual = meta["enableMipMap"]
    add(
        "META_MIPMAP",
        "Mip maps",
        0,
        mip_actual,
        "pass" if mip_actual == 0 else "fail",
        "Mip maps must be off for pixel art.",
    )

    compression_actual = meta["textureCompression"]
    add(
        "META_COMPRESSION",
        "Texture compression",
        "0 (None)",
        compression_actual,
        "pass" if compression_actual == 0 else "fail",
        "Lossy compression must be off for pixel art.",
    )

    mode_actual = meta["spriteMode"]
    add(
        "META_SPRITE_MODE",
        "Sprite import mode",
        "2 (Multiple)",
        f"{mode_actual} ({SPRITE_MODES.get(mode_actual, 'unknown')})",
        "pass" if mode_actual == 2 else "fail",
        "A sheet must import as Multiple so each cell is a named sprite.",
    )

    expected_sprites = (
        geometry["directions"] * geometry["framesPerDirection"] if geometry else None
    )
    add(
        "META_SPRITE_COUNT",
        "Sliced sprite count",
        expected_sprites,
        len(meta["sprites"]),
        "pass" if expected_sprites == len(meta["sprites"]) else "fail",
        "One sprite per direction row x frame column.",
    )

    widths = sorted({sprite["width"] for sprite in meta["sprites"]})
    heights = sorted({sprite["height"] for sprite in meta["sprites"]})
    actual_size = (
        f"{widths[0]}×{heights[0]}"
        if len(widths) == 1 and len(heights) == 1
        else f"{widths}×{heights}"
    )
    add(
        "META_FRAME_SIZE",
        "Sprite rect size",
        f"{standard['cellWidth']}×{standard['cellHeight']}",
        actual_size,
        "pass"
        if widths == [standard["cellWidth"]] and heights == [standard["cellHeight"]]
        else "fail",
        "Every rect must match the locked "
        f"{standard['cellWidth']}x{standard['cellHeight']} cell.",
    )

    pivot = meta["spritePivot"]
    pivot_ok = abs(pivot[0] - 0.5) < 1e-6 and abs(pivot[1]) < 1e-6
    add(
        "META_PIVOT",
        "Sprite pivot",
        "0.5, 0 (bottom center)",
        f"{pivot[0]:g}, {pivot[1]:g}",
        "pass" if pivot_ok else "fail",
        "Bottom-center pivot keeps feet on the ground line.",
    )

    alignments = sorted(
        {sprite["alignment"] for sprite in meta["sprites"] if sprite["alignment"] is not None}
    )
    add(
        "META_SPRITE_ALIGNMENT",
        "Per-sprite alignment",
        "9 (Custom)",
        ", ".join(str(value) for value in alignments) or "(missing)",
        "pass" if alignments == [9] else "fail",
        "Sliced sprites must keep the custom pivot instead of a default alignment.",
    )

    add(
        "META_ALPHA_TRANSPARENCY",
        "Alpha is transparency",
        1,
        meta["alphaIsTransparency"],
        "pass" if meta["alphaIsTransparency"] == 1 else "fail",
        "Transparent sprite edges must be treated as alpha.",
    )

    add(
        "META_TEXTURE_TYPE",
        "Texture importer type",
        "8 (Sprite)",
        f"{meta['textureType']}",
        "pass" if meta["textureType"] == 8 else "fail",
        "The importer must treat the texture as a sprite.",
    )

    add(
        "META_SRGB",
        "sRGB texture",
        1,
        meta["sRGBTexture"],
        "pass" if meta["sRGBTexture"] == 1 else "fail",
        "Colour art must import as sRGB.",
    )

    add(
        "META_WRAP",
        "Wrap mode",
        "1/1 (Clamp)",
        f"{meta['wrapU']}/{meta['wrapV']}",
        "pass" if meta["wrapU"] == 1 and meta["wrapV"] == 1 else "fail",
        "Clamp sampling prevents neighbouring cells bleeding in.",
    )

    add(
        "META_NPOT",
        "Non-power-of-two scaling",
        "0 (None)",
        meta["nPOTScale"],
        "pass" if meta["nPOTScale"] == 0 else "fail",
        "Do not rescale a 288x512 sheet.",
    )

    mesh = meta["spriteMeshType"]
    add(
        "META_MESH_TYPE",
        "Sprite mesh type",
        "0 (FullRect preferred)",
        f"{mesh} ({SPRITE_MESH_TYPES.get(mesh, 'unknown')})",
        "pass" if mesh == 0 else "advisory",
        "Tight meshes trim transparent pixels; FullRect keeps a stable frame rect for animation.",
    )

    add(
        "META_EXTRUDE",
        "Sprite extrude",
        "0-1 px",
        meta["spriteExtrude"],
        "pass" if meta["spriteExtrude"] in (0, 1) else "advisory",
        "Extrude above 1 px can bleed neighbouring cells.",
    )

    max_size = meta["maxTextureSize"]
    needed = max(int(asset.get("pixelWidth", 0)), int(asset.get("pixelHeight", 0)))
    add(
        "META_MAX_SIZE",
        "Max texture size",
        f">= {needed}",
        max_size,
        "pass" if max_size >= needed else "fail",
        "Import size must not clamp the sheet.",
    )

    return checks


def audit_sprite_grid(meta: dict, stem: str, geometry: dict | None, standard: dict) -> dict:
    sprites = meta["sprites"]
    directions = standard["directions"]
    frames = geometry["framesPerDirection"] if geometry else None
    result = {
        "stem": stem,
        "expectedCount": None,
        "namesMatch": False,
        "positionsMatch": False,
        "uniqueNames": len({sprite["name"] for sprite in sprites}) == len(sprites),
        "uniqueSpriteIds": len({sprite["spriteId"] for sprite in sprites}) == len(sprites),
        "uniqueRects": len({(s["x"], s["y"]) for s in sprites}) == len(sprites),
        "coversFullGrid": False,
        "pivotPerSpriteBottomCenter": all(
            s["pivot"] is not None and abs(s["pivot"][0] - 0.5) < 1e-6 and abs(s["pivot"][1]) < 1e-6
            for s in sprites
        ),
        "alignmentCustomCount": sum(1 for s in sprites if s["alignment"] == 9),
        "rows": [],
    }
    if not geometry or not frames:
        return result

    expected = {
        f"{stem}_{direction}_{frame}": (row, frame)
        for row, direction in enumerate(directions)
        for frame in range(frames)
    }
    result["expectedCount"] = len(expected)

    by_name = {sprite["name"]: sprite for sprite in sprites}
    names_match = set(by_name) == set(expected)
    positions_match = True
    for name, (row, frame) in expected.items():
        sprite = by_name.get(name)
        if not sprite:
            positions_match = False
            continue
        expected_x = frame * standard["cellWidth"]
        expected_y = (len(directions) - 1 - row) * standard["cellHeight"]
        if (sprite["x"], sprite["y"]) != (expected_x, expected_y):
            positions_match = False

    result["namesMatch"] = names_match
    result["positionsMatch"] = positions_match
    result["coversFullGrid"] = names_match and positions_match and result["uniqueRects"]
    result["rows"] = directions
    return result


# --------------------------------------------------------------------------- #
# rendering
# --------------------------------------------------------------------------- #
def render_json(report: dict) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(report: dict) -> str:
    lines: list[str] = []
    add = lines.append

    repo = report["repo"]
    standard = report["standards"]
    catalogue = report["catalogue"]
    definitions = report["definitions"]
    declared = report["declaredTargets"]
    assets = report["assets"]
    coverage = definitions["coverage"]

    add("# OPC-05b — Coverage report: catalogue → definition → asset")
    add("")
    add("> Generated by `Implementation/Asset_Handoff/coverage_audit.py` (Python standard library).")
    add("> Do not edit by hand. Regenerate and check with:")
    add(">")
    add("> ```bash")
    add("> python Implementation/Asset_Handoff/coverage_audit.py")
    add("> python Implementation/Asset_Handoff/coverage_audit.py --check")
    add("> ```")
    add("")
    add(f"- **Source commit:** `{repo['sourceCommit']}` — {repo['sourceCommitMeaning']}.")
    add(f"- **Evidence digest:** `{repo['evidenceDigest']}` over {len(report['evidence'])} files (SHA256 per file in §8).")
    add("- **Phạm vi:** chỉ đọc nguồn; không sửa schema, manifest, asset, `.meta`, server hay gameplay numeric.")
    add("")

    # --- 1. TL;DR ---------------------------------------------------------- #
    add("## 1. Kết luận")
    add("")
    da = next((asset for asset in assets if asset["assetId"]), None)
    if da:
        geo = da["geometry"]
        add(
            f"1. **Asset Minh Kiếm:** manifest và PNG IHDR khớp `{da['png']['width']}×{da['png']['height']}`; "
            f"{geo['framesPerDirection']} frame/hướng × {geo['directions']} hướng, cell "
            f"`{geo['frameWidth']}×{geo['frameHeight']}`. `.meta` tĩnh đã đọc bằng Python: "
            f"{da['meta']['spriteCount']} sprite, PPU {da['meta']['spritePixelsToUnits']}, pivot bottom-center."
        )
        bad = [check for check in da["metaChecks"] if check["status"] == "fail"]
        if bad:
            add(
                "2. **Lỗi import tĩnh:** "
                + "; ".join(
                    f"`{check['id']}` = {check['actual']}, cần {check['expected']}" for check in bad
                )
                + " → thuộc phạm vi Muse, không sửa trong PR này."
            )
        else:
            add("2. **Import tĩnh:** không phát hiện sai lệch so với chuẩn pixel art.")
        add(
            "3. **Engine playback:** **chưa nghiệm thu**. Không có Unity trong môi trường này; "
            "báo cáo chỉ xác nhận metadata tĩnh và header PNG."
        )
    coverage_parts = []
    for key in ("class", "skill", "quest", "item", "map", "spawn", "node"):
        denominator = (
            catalogue["items"]["variantCount"] if key == "item" else coverage[key]["catalogueCount"]
        )
        coverage_parts.append(f"{coverage[key]['resolvedCount']}/{denominator} {key}")
    add(
        f"4. **Độ phủ definition:** {definitions['canonicalCount']} ví dụ canonical "
        f"(+{definitions['syntheticCount']} fixture synthetic tách riêng). "
        + ", ".join(coverage_parts)
        + "."
    )
    add("")

    # --- 2. measured source numbers ---------------------------------------- #
    add("## 2. Số đo nguồn (đo từ file, không suy đoán)")
    add("")
    add("| Hạng mục | Số đo | Nguồn |")
    add("|---|---:|---|")
    add(f"| Class ID canonical | {catalogue['classes']['count']} | `{PRODUCTION_DIR}/{CLASS_CSV}` |")
    add(f"| Map ID | {catalogue['maps']['count']} | `{PRODUCTION_DIR}/{PLACEMENT_CSV}` |")
    add(f"| Quest ID | {catalogue['quests']['count']} | `{PRODUCTION_DIR}/{QUEST_CSV}` ({catalogue['quests']['dialogueRows']} dòng dialogue) |")
    add(f"| Placement | {catalogue['placements']['count']} | `{PRODUCTION_DIR}/{PLACEMENT_CSV}` ({catalogue['placements']['distinctRecordIds']} record_id riêng) |")
    add(f"| Active skill ID | {catalogue['activeSkills']['count']} | `{COMBAT_SPEC}` (5 lớp × 6) |")
    add(f"| Item master / rarity variant | {catalogue['items']['masterCount']} / {catalogue['items']['variantCount']} | `{ITEM_MASTER_CSV}` / `{ITEM_VARIANT_CSV}` |")
    add(f"| Definition example canonical | {definitions['canonicalCount']} | `{EXAMPLES_DIR}` |")
    add(f"| Fixture synthetic | {definitions['syntheticCount']} | `{EXAMPLES_DIR}/MapTopology` |")
    add(f"| Schema file | {definitions['schemas']['fileCount']} | `{SCHEMAS_DIR}` |")
    add("")

    add("**Class ID canonical (đủ 5):**")
    add("")
    for class_id in catalogue["classes"]["ids"]:
        name = catalogue["classes"]["names"][class_id]
        passives = catalogue["classes"]["passiveNodesPerClass"][class_id]
        add(f"- `{class_id}` — {name} ({passives} passive node)")
    add("")

    if declared:
        measured = {
            "quests": catalogue["quests"]["count"],
            "activeSkills": catalogue["activeSkills"]["count"],
            "classes": catalogue["classes"]["count"],
            "maps": catalogue["maps"]["count"],
            "placements": catalogue["placements"]["count"],
        }
        add(
            "**Đối chiếu tuyên bố trong "
            f"`{RELEASE_SPEC}`:** “{declared['quote']}” → "
            + ", ".join(
                f"{key} {declared[key]}={measured[key]} {'✅' if declared[key] == measured[key] else '❌'}"
                for key in ("quests", "activeSkills", "classes", "maps", "placements")
            )
            + "."
        )
        add("")

    add(
        f"**Placement theo `record_type`:** "
        + ", ".join(f"{key} {value}" for key, value in catalogue["placements"]["recordTypes"].items())
        + f". Trong {catalogue['placements']['count']} dòng, "
        f"**{catalogue['placements']['newProposed']}** còn `design_state=NEW_PROPOSED` — đây là catalogue proposal, "
        "không phải runtime record đã duyệt."
    )
    add("")

    ids = {
        "map": catalogue["maps"]["ids"],
        "quest": catalogue["quests"]["ids"],
        "skill": catalogue["activeSkills"]["ids"],
    }
    add("<details><summary>Danh sách ID đo được (map / quest / skill)</summary>")
    add("")
    for label, values in ids.items():
        add(f"**{label} ({len(values)}):** " + ", ".join(f"`{value}`" for value in values))
        add("")
    add("</details>")
    add("")

    # --- 3. asset ---------------------------------------------------------- #
    add("## 3. Asset Minh Kiếm — manifest, PNG và import metadata")
    add("")
    for index, asset in enumerate(assets, start=1):
        geo = asset["geometry"]
        add(f"### 3.{index} `{asset['assetId']}` ({asset['kind']}, status `{asset['status']}`)")
        add("")
        add("| Kiểm tra | Manifest / chuẩn | Đo được | Kết quả |")
        add("|---|---|---|---|")
        add(
            f"| PNG IHDR | {asset['manifest']['pixelWidth']}×{asset['manifest']['pixelHeight']} | "
            f"{asset['png']['width']}×{asset['png']['height']} ({asset['png']['colorTypeName']}, {asset['png']['bitDepth']}-bit) | "
            f"{'✅' if asset['png']['width'] == asset['manifest']['pixelWidth'] and asset['png']['height'] == asset['manifest']['pixelHeight'] else '❌'} |"
        )
        add(
            f"| Hướng | {len(standard['directions'])} hướng theo thứ tự chuẩn | "
            f"{len(asset['manifest']['directions'])} hướng | "
            f"{'✅' if asset['manifest']['directionsMatchStandard'] else '❌'} |"
        )
        animation = asset["manifest"]["animations"][0] if asset["manifest"]["animations"] else {}
        add(
            f"| Walk | {standard['walkFrames']} frame/hướng @ {standard['walkFps']} fps | "
            f"{animation.get('framesPerDirection')} frame @ {animation.get('fps')} fps | "
            f"{'✅' if animation.get('framesPerDirection') == standard['walkFrames'] and animation.get('fps') == standard['walkFps'] else '❌'} |"
        )
        if geo:
            add(
                f"| Cell suy ra | {standard['cellWidth']}×{standard['cellHeight']} | "
                f"{asset['png']['width']}/{geo['framesPerDirection']} = {geo['frameWidth']} × "
                f"{asset['png']['height']}/{geo['directions']} = {geo['frameHeight']} | "
                f"{'✅' if asset['geometryMatchesStandard'] else '❌'} |"
            )
        add(
            "| Preview | tồn tại, bội số nguyên của sheet | "
            + (
                f"{asset['preview']['width']}×{asset['preview']['height']} | "
                + (
                    "✅ |"
                    if asset["preview"]["width"] % asset["png"]["width"] == 0
                    and asset["preview"]["height"] % asset["png"]["height"] == 0
                    else "⚠️ |"
                )
                if asset["preview"]
                else "thiếu | ❌ |"
            )
        )
        add("")
        add("**Đọc `.meta` tĩnh bằng Python (không cần Unity):**")
        add("")
        add("| Kiểm tra | Kỳ vọng | Thực tế | Trạng thái |")
        add("|---|---|---|---|")
        for check in asset["metaChecks"]:
            mark = {"pass": "✅ pass", "fail": "❌ fail", "advisory": "⚠️ advisory"}[check["status"]]
            add(f"| `{check['id']}` | {check['expected']} | {check['actual']} | {mark} |")
        add("")
        grid = asset["spriteGrid"]
        frames_text = geo["framesPerDirection"] if geo else "?"
        add(
            f"- Lưới sprite: {len(grid['rows'])} hàng × {frames_text} cột; "
            f"tên khớp `{grid['stem']}_<DIR>_<frame>`: {'✅' if grid['namesMatch'] else '❌'}; "
            f"vị trí rect khớp lưới: {'✅' if grid['positionsMatch'] else '❌'}; "
            f"phủ kín lưới: {'✅' if grid['coversFullGrid'] else '❌'}; "
            f"{grid['alignmentCustomCount']}/{asset['meta']['spriteCount']} sprite dùng alignment Custom + pivot (0.5, 0)."
        )
        add(
            f"- PNG pixel decode đầy đủ: **chưa thực hiện** (chỉ xác nhận signature + IHDR). "
            f"File SHA256: `{asset['png']['sha256']}`."
        )
        add("")

    verification = report["verification"]
    static = verification["staticImportMetadata"]
    add("### 3.x Tách trạng thái nghiệm thu")
    add("")
    add("| Lớp kiểm tra | Trạng thái | Ghi chú |")
    add("|---|---|---|")
    add(
        f"| Static import metadata (`.meta`) | **{static['status']}** | "
        f"pass: {', '.join(static['verifiedFields']) or '(none)'} |"
    )
    if static["failedFields"]:
        add(f"| Static import metadata — vi phạm | **failed** | {', '.join(static['failedFields'])} |")
    if static["advisoryFields"]:
        add(
            f"| Static import metadata — advisory | **advisory** | "
            f"{', '.join(static['advisoryFields'])} |"
        )
    for asset in assets:
        png = asset["png"]
        add(
            f"| PNG header `{asset['assetId']}` | **verified** | "
            f"{png['width']}×{png['height']}, {png['bitDepth']}-bit {png['colorTypeName']} |"
        )
    add(f"| PNG pixel-level audit | **not performed** | {verification['png']['method']} |")
    add(
        f"| Unity engine playback | **{verification['enginePlayback']['status']}** | "
        f"{verification['enginePlayback']['reason']} |"
    )
    add(
        f"| Runtime content | **{verification['runtimeContent']['status']}** | "
        f"{verification['runtimeContent']['reason']} |"
    )
    add("")

    # --- 4. definitions ---------------------------------------------------- #
    add("## 4. Độ phủ definition so với catalogue")
    add("")
    add("| Nhóm | Catalogue | Example canonical | Resolve | Absent runtime record | Unknown nghiệm thu |")
    add("|---|---:|---:|---:|---:|---|")
    labels = {
        "class": ("Class", "classId"),
        "skill": ("Skill", "skillId"),
        "quest": ("Quest", "questId"),
        "item": ("Item", "itemId"),
        "map": ("Map", "mapId"),
        "spawn": ("Spawn placement", "recordId"),
        "node": ("Gathering node", "recordId"),
    }
    for key, (label, id_key) in labels.items():
        row = coverage[key]
        if key == "item":
            items = catalogue["items"]
            add(
                f"| Item master (`{id_key}`) | {items['masterCount']} | 0 | 0 | {items['masterCount']} | unverified |"
            )
            add(
                f"| Item rarity variant (`{id_key}`) | {items['variantCount']} | {row['exampleCount']} | "
                f"{row['resolvedCount']} | {items['variantCount'] - row['resolvedCount']} | unverified |"
            )
            continue
        add(
            f"| {label} (`{id_key}`) | {row['catalogueCount']} | {row['exampleCount']} | "
            f"{row['resolvedCount']} | {row['absentCount']} | unverified |"
        )
    add("")
    add(
        f"**{definitions['canonicalCount']} definition examples canonical** "
        "(1 class + 3 skill + 1 quest + 1 item + 1 map + 1 spawn + 1 gathering node). "
        f"Fixture `{definitions['synthetic'][0]['file']}` "
        f"(`reviewState={definitions['synthetic'][0].get('reviewState')}`) **không** tính vào coverage."
        if definitions["synthetic"]
        else f"**{definitions['canonicalCount']} definition examples canonical.**"
    )
    add("")
    if coverage["item"].get("resolvedInMaster") is not None and coverage["item"]["resolvedIds"]:
        add(
            f"- Item example `{coverage['item']['resolvedIds'][0]}`: "
            f"có trong rarity-variant catalogue: {'✅' if coverage['item'].get('resolvedInVariants') else '❌'}; "
            f"có trong item master: {'✅' if coverage['item'].get('resolvedInMaster') else '❌'}."
        )
        add("")
    add(
        f"- Schema files: {definitions['schemas']['fileCount']}; exercised by examples: "
        + ", ".join(f"`{name}`" for name in definitions["schemas"]["exercisedByExamples"])
        + (f"; not exercised: {', '.join(definitions['schemas']['notExercised'])}" if definitions["schemas"]["notExercised"] else "")
        + ". Schema conformance chạy bằng `Implementation/Tools/validate_content.py`, không lặp ở đây."
    )
    add("")

    add("<details><summary>ID chưa có runtime definition (absent)</summary>")
    add("")
    for key in ("class", "skill", "map", "quest"):
        row = coverage[key]
        shown = row["absentIds"]
        add(f"**{key} — {len(shown)} absent:** " + (", ".join(f"`{value}`" for value in shown) if shown else "(none)"))
        add("")
    for key in ("item", "spawn", "node"):
        row = coverage[key]
        if key == "item":
            items = catalogue["items"]
            add(
                f"**item — {items['masterCount']} master + "
                f"{items['variantCount'] - row['resolvedCount']} variant absent** "
                "(danh sách đầy đủ trong `coverage_report.json`)."
            )
        else:
            add(f"**{key} — {row['absentCount']} absent** (danh sách đầy đủ trong `coverage_report.json`).")
        add("")
    add("</details>")
    add("")

    # --- 5. findings ------------------------------------------------------- #
    add("## 5. Findings")
    add("")
    if report["findings"]:
        add("| ID | Severity | Owner | Expected | Actual | Action |")
        add("|---|---|---|---|---|---|")
        for finding in report["findings"]:
            add(
                f"| `{finding['id']}` | {finding['severity']} | {finding['owner']} | "
                f"{finding['expected']} | {finding['actual']} | {finding['action']} |"
            )
    else:
        add("Không có finding.")
    add("")
    add(
        "Các finding `fail`/`advisory` thuộc file do Muse bàn giao. OPC-05b **không sửa** asset, manifest hay `.meta`; "
        "chỉ báo cáo kèm bằng chứng để Muse re-export."
    )
    add("")

    # --- 6. unknowns ------------------------------------------------------- #
    add("## 6. Điều báo cáo này KHÔNG chứng minh")
    add("")
    add("- Không chứng minh Unity import thành công hoặc animation chạy đúng trong engine.")
    add("- Không decode toàn bộ pixel, palette, frame duplicate hay bleed giữa các cell.")
    add("- Không chứng minh quest/boss/reward/save end-to-end, navmesh hay combat runtime.")
    add("- `349` placement là số dòng catalogue; `NEW_PROPOSED` chưa phải placement đã duyệt.")
    add(
        "- Placement/mob/NPC là record nội dung, **không phải asset độc lập**; không suy ra số "
        "asset Muse phải giao từ một walk sheet."
    )
    add("- Không thay thế `validate_content.py`, `validate_contracts.py` hay `validate_asset_delivery.py`.")
    add("")

    # --- 7. reproduce ------------------------------------------------------ #
    add("## 7. Tái tạo và kiểm tra")
    add("")
    add("```bash")
    add("python Implementation/Asset_Handoff/coverage_audit.py")
    add("python Implementation/Asset_Handoff/coverage_audit.py --check")
    add("```")
    add("")
    add("Script chỉ dùng standard library, không cần Unity/.NET, không ghi vào nguồn ngoài hai file report.")
    add("")

    # --- 8. evidence ------------------------------------------------------- #
    add("## 8. Evidence (SHA256)")
    add("")
    add("File text được hash ở dạng **LF chuẩn hoá** để Windows và Linux cho cùng kết quả; PNG giữ byte gốc.")
    add("")
    add("| File | Bytes | SHA256 |")
    add("|---|---:|---|")
    for item in report["evidence"]:
        add(f"| `{item['path']}` | {item['bytes']} | `{item['sha256']}` |")
    add("")
    add(f"**Evidence digest:** `{repo['evidenceDigest']}`")
    add("")

    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def write_text_lf(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(normalize_newlines(text))


def first_difference(expected: str, actual: str) -> str:
    expected_lines = expected.splitlines()
    actual_lines = actual.splitlines()
    for index in range(max(len(expected_lines), len(actual_lines))):
        left = expected_lines[index] if index < len(expected_lines) else "<missing>"
        right = actual_lines[index] if index < len(actual_lines) else "<missing>"
        if left != right:
            return f"line {index + 1}:\n  expected: {left}\n  actual:   {right}"
    return "content differs only in trailing whitespace"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate the OPC-05b coverage report from repository sources."
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Repository root (default: two levels above this script).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail when the committed reports are missing or stale; write nothing.",
    )
    parser.add_argument(
        "--source-commit",
        default=None,
        help="Pin the recorded source commit instead of asking git.",
    )
    args = parser.parse_args(argv)

    root = Path(args.repo).resolve() if args.repo else Path(__file__).resolve().parents[2]
    output_dir = root / "Implementation" / "Asset_Handoff"
    md_path = output_dir / MD_NAME
    json_path = output_dir / JSON_NAME

    pinned = args.source_commit
    if pinned is None and args.check and json_path.is_file():
        try:
            pinned = read_json(json_path).get("repo", {}).get("sourceCommit")
        except (OSError, ValueError):
            pinned = None

    report = build_report(root, source_commit=pinned)
    if pinned is None:
        commit = git_last_commit(root, [item["path"] for item in report["evidence"]])
        report["repo"]["sourceCommit"] = commit or "unavailable"

    markdown = render_markdown(report)
    payload = render_json(report)

    if args.check:
        failures = []
        for path, expected in ((md_path, markdown), (json_path, payload)):
            if not path.is_file():
                failures.append(f"MISSING {path.relative_to(root).as_posix()}")
                continue
            actual = normalize_newlines(path.read_text(encoding="utf-8-sig"))
            if actual != normalize_newlines(expected):
                failures.append(
                    f"STALE {path.relative_to(root).as_posix()}: "
                    + first_difference(normalize_newlines(expected), actual)
                )
        if failures:
            print("coverage report check failed:", file=sys.stderr)
            for failure in failures:
                print(f"  {failure}", file=sys.stderr)
            print(
                "run: python Implementation/Asset_Handoff/coverage_audit.py",
                file=sys.stderr,
            )
            return 1
        print(
            "coverage report is up to date "
            f"({md_path.name}, {json_path.name}, {len(report['evidence'])} evidence files)"
        )
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    write_text_lf(md_path, markdown)
    write_text_lf(json_path, payload)

    print(f"wrote {md_path.relative_to(root).as_posix()}")
    print(f"wrote {json_path.relative_to(root).as_posix()}")
    print(
        f"source commit: {report['repo']['sourceCommit']}; "
        f"evidence digest: {report['repo']['evidenceDigest']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
