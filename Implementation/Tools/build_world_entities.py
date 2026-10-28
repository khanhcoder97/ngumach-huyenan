#!/usr/bin/env python3
"""Build the Bến Mưa runtime world-entity registry from the canonical manifest.

Source of truth: docs/production/World_Spawn_Gathering_Manifest_vi.csv.
Output: Implementation/Content/Runtime/world_entities_bm.json

One entity per manifest placement record (spawn group / node / NPC), with the
canonical template IDs kept separate. No HP/stat values are invented.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

MANIFEST = Path("docs/production/World_Spawn_Gathering_Manifest_vi.csv")
MAP_BOUNDS = Path("Implementation/Content/map_bounds.json")
OUTPUT = Path("Implementation/Content/Runtime/world_entities_bm.json")
MAP_ID = "MAP_BEN_MUA"
FLOOR_ID = "OVERWORLD"

KIND_BY_RECORD_TYPE = {
    "NPC": "NPC",
    "MOB_GROUP": "MOB",
    "BOSS": "BOSS",
    "GATHER_NODE": "GATHER_NODE",
    "INTERACTABLE": "INTERACTABLE",
}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def entity_id_for(record_id):
    return "ENT_" + record_id.replace("-", "_").upper()


def bounds_for(map_id, config):
    return (config.get("overrides") or {}).get(map_id) or config.get("defaultBounds")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--map-bounds", type=Path, default=MAP_BOUNDS)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not args.manifest.is_file():
        fail(f"{args.manifest} not found")
    if not args.map_bounds.is_file():
        fail(f"{args.map_bounds} not found")

    map_config = json.loads(args.map_bounds.read_text(encoding="utf-8"))
    bounds = bounds_for(MAP_ID, map_config)
    if not bounds:
        fail(f"{MAP_ID} has no bounds")

    rows = [
        row
        for row in csv.DictReader(args.manifest.open(encoding="utf-8-sig", newline=""))
        if (row.get("map_id") or "").strip() == MAP_ID
    ]
    if not rows:
        fail(f"no manifest rows for {MAP_ID}")

    entities = []
    templates = {}
    for row in sorted(rows, key=lambda item: (item.get("record_id") or "")):
        record_id = (row.get("record_id") or "").strip()
        record_type = (row.get("record_type") or "").strip()
        kind = KIND_BY_RECORD_TYPE.get(record_type)
        if kind is None:
            fail(f"{record_id}: unsupported record_type '{record_type}'")

        template_ids = [
            part.strip()
            for part in (row.get("entity_id") or "").split("|")
            if part.strip()
        ]
        if not template_ids:
            fail(f"{record_id}: entity_id is empty")

        try:
            x_wu = float((row.get("x_wu") or "").strip())
            y_wu = float((row.get("y_wu") or "").strip())
        except ValueError:
            fail(f"{record_id}: x_wu/y_wu are not numeric")
        if not (math.isfinite(x_wu) and math.isfinite(y_wu)):
            fail(f"{record_id}: x_wu/y_wu are not finite")
        if not (
            bounds["xMin"] <= x_wu <= bounds["xMax"]
            and bounds["yMin"] <= y_wu <= bounds["yMax"]
        ):
            fail(f"{record_id}: ({x_wu}, {y_wu}) outside {MAP_ID} bounds")

        try:
            quantity = int((row.get("quantity") or "1").strip() or "1")
            respawn_seconds = int((row.get("respawn_seconds") or "0").strip() or "0")
        except ValueError:
            fail(f"{record_id}: quantity/respawn_seconds are not integers")
        if quantity < 1 or respawn_seconds < 0:
            fail(f"{record_id}: quantity/respawn_seconds out of range")

        for template_id in template_ids:
            templates.setdefault(template_id, kind)

        entities.append(
            {
                "entityId": entity_id_for(record_id),
                "recordId": record_id,
                "kind": kind,
                "templateIds": template_ids,
                "mapId": MAP_ID,
                "floorId": FLOOR_ID,
                "xWu": x_wu,
                "yWu": y_wu,
                "quantity": quantity,
                "respawnSeconds": respawn_seconds,
                "condition": (row.get("condition") or "").strip(),
            }
        )

    payload = {
        "schemaVersion": 1,
        "mapId": MAP_ID,
        "sourceRef": "docs/production/World_Spawn_Gathering_Manifest_vi.csv",
        "hpRule": "No HP/stat values: canonical numeric stats are not locked yet",
        "templates": [
            {"templateId": template_id, "kind": templates[template_id]}
            for template_id in sorted(templates)
        ],
        "entities": entities,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"OK: wrote {len(entities)} entities and {len(templates)} templates to {args.output}")


if __name__ == "__main__":
    main()
