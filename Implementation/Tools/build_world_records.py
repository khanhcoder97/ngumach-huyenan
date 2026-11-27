#!/usr/bin/env python3
"""Build the canonical world-record catalog used to validate quest objective targets.

Source of truth: docs/production/World_Spawn_Gathering_Manifest_vi.csv (all rows),
plus Atlas-sourced supplements for quest objects that are not manifest rows.
Output: Implementation/Content/Runtime/world_records.json

The server uses this catalog to fail startup when a quest objective references a
recordId that does not exist (dangling IDs). Gather metadata (profession, item,
yield, level, tool) is copied verbatim for GATHER_NODE rows only.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

MANIFEST = Path("docs/production/World_Spawn_Gathering_Manifest_vi.csv")
OUTPUT = Path("Implementation/Content/Runtime/world_records.json")

# Quest objects defined by the map atlas, not present as manifest rows.
# respawnSeconds 20 is a labelled DEV FIXTURE: the quest spec only says the
# packages respawn ("kiện respawn") without a canonical number.
ATLAS_SUPPLEMENTS = [
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_01",
        "mapId": "MAP_BEN_MUA",
        "recordType": "INTERACTABLE",
        "designState": "ATLAS_ANCHOR",
        "entityId": "OBJ_BM_PACKAGE_01",
        "xWu": 36.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "respawnPolicy": "DEV FIXTURE: atlas says 'kiện respawn' without a number; 20s fixture",
        "condition": "P00-01; quest package",
        "sourceRef": "docs/production/Map_Production_Atlas_vi.md",
    },
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_02",
        "mapId": "MAP_BEN_MUA",
        "recordType": "INTERACTABLE",
        "designState": "ATLAS_ANCHOR",
        "entityId": "OBJ_BM_PACKAGE_02",
        "xWu": 44.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "respawnPolicy": "DEV FIXTURE: atlas says 'kiện respawn' without a number; 20s fixture",
        "condition": "P00-01; quest package",
        "sourceRef": "docs/production/Map_Production_Atlas_vi.md",
    },
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_03",
        "mapId": "MAP_BEN_MUA",
        "recordType": "INTERACTABLE",
        "designState": "ATLAS_ANCHOR",
        "entityId": "OBJ_BM_PACKAGE_03",
        "xWu": 52.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "respawnPolicy": "DEV FIXTURE: atlas says 'kiện respawn' without a number; 20s fixture",
        "condition": "P00-01; quest package",
        "sourceRef": "docs/production/Map_Production_Atlas_vi.md",
    },
]

RECORD_TYPES = {"NPC", "MOB_GROUP", "BOSS", "GATHER_NODE", "INTERACTABLE"}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not args.manifest.is_file():
        fail(f"{args.manifest} not found")

    records = []
    seen = set()
    for row in csv.DictReader(args.manifest.open(encoding="utf-8-sig", newline="")):
        record_id = (row.get("record_id") or "").strip()
        record_type = (row.get("record_type") or "").strip()
        if record_type not in RECORD_TYPES:
            fail(f"{record_id}: unsupported record_type '{record_type}'")
        if record_id in seen:
            fail(f"{record_id}: duplicate recordId")
        seen.add(record_id)

        try:
            x_wu = float((row.get("x_wu") or "").strip())
            y_wu = float((row.get("y_wu") or "").strip())
            respawn_seconds = int((row.get("respawn_seconds") or "0").strip() or "0")
        except ValueError:
            fail(f"{record_id}: x_wu/y_wu/respawn_seconds are not numeric")
        if not (math.isfinite(x_wu) and math.isfinite(y_wu)):
            fail(f"{record_id}: x_wu/y_wu are not finite")
        if respawn_seconds < 0:
            fail(f"{record_id}: respawn_seconds out of range")

        entry = {
            "recordId": record_id,
            "mapId": (row.get("map_id") or "").strip(),
            "recordType": record_type,
            "designState": (row.get("design_state") or "").strip(),
            "entityId": (row.get("entity_id") or "").strip(),
            "xWu": x_wu,
            "yWu": y_wu,
            "respawnSeconds": respawn_seconds,
            "respawnPolicy": (row.get("respawn_policy") or "").strip(),
            "condition": (row.get("condition") or "").strip(),
            "sourceRef": (row.get("source_ref") or "").strip(),
        }

        if record_type == "GATHER_NODE":
            try:
                yield_min = int((row.get("yield_min") or "1").strip() or "1")
                yield_max = int((row.get("yield_max") or "1").strip() or "1")
                level = int((row.get("profession_level_required") or "1").strip() or "1")
            except ValueError:
                fail(f"{record_id}: yield/level columns are not integers")
            if yield_min < 0 or yield_max < yield_min or level < 1:
                fail(f"{record_id}: yield/level out of range")
            entry["gather"] = {
                "profession": (row.get("gather_profession") or "").strip(),
                "itemId": (row.get("gather_item_id") or "").strip(),
                "yieldMin": yield_min,
                "yieldMax": yield_max,
                "professionLevelRequired": level,
                "toolId": (row.get("tool_id") or "").strip(),
            }

        records.append(entry)

    for supplement in ATLAS_SUPPLEMENTS:
        if supplement["recordId"] in seen:
            fail(f"{supplement['recordId']}: supplement collides with manifest row")
        seen.add(supplement["recordId"])
        records.append(supplement)

    payload = {
        "schemaVersion": 1,
        "sourceRef": [
            "docs/production/World_Spawn_Gathering_Manifest_vi.csv",
            "docs/production/Map_Production_Atlas_vi.md (supplements)",
        ],
        "records": sorted(records, key=lambda item: item["recordId"]),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"OK: wrote {len(records)} world records to {args.output}")


if __name__ == "__main__":
    main()
