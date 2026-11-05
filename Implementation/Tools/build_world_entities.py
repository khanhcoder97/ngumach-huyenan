#!/usr/bin/env python3
"""Build the Bến Mưa runtime world-entity registry from the canonical manifest.

Source of truth: docs/production/World_Spawn_Gathering_Manifest_vi.csv plus
Atlas-sourced supplements (quest objects not present as manifest rows).
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

# Production_Rules_Complete_v1_vi.md §5: each P00-01 package counts at most
# once per character and never removes the world item for other characters.
# Generic shared INTERACTABLEs keep the shared rule; gather nodes are
# per-character by the manifest shard rule.
CLAIM_POLICY_SHARED = "SHARED"
CLAIM_POLICY_PER_CHARACTER = "PER_CHARACTER"
CLAIM_POLICY_BY_KIND = {
    "GATHER_NODE": CLAIM_POLICY_PER_CHARACTER,
    "INTERACTABLE": CLAIM_POLICY_SHARED,
}
PACKAGE_CLAIM_SOURCE = (
    "Production_Rules_Complete_v1_vi.md §5: mỗi ID tính tối đa 1/character, "
    "không trừ item world cho người khác"
)

# Quest objects defined by the map atlas, not present as manifest rows.
# respawnSeconds 20 is a labelled DEV FIXTURE: the quest spec only says the
# packages respawn ("kiện respawn") without a canonical number.
ATLAS_SUPPLEMENTS = [
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_01",
        "kind": "INTERACTABLE",
        "templateIds": ["OBJ_BM_PACKAGE_01"],
        "xWu": 36.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "claimPolicy": CLAIM_POLICY_PER_CHARACTER,
        "condition": (
            "P00-01; per-character claim (Production_Rules §5); "
            "DEV FIXTURE respawn 20s (atlas: 'kiện respawn' without a number)"
        ),
    },
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_02",
        "kind": "INTERACTABLE",
        "templateIds": ["OBJ_BM_PACKAGE_02"],
        "xWu": 44.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "claimPolicy": CLAIM_POLICY_PER_CHARACTER,
        "condition": (
            "P00-01; per-character claim (Production_Rules §5); "
            "DEV FIXTURE respawn 20s (atlas: 'kiện respawn' without a number)"
        ),
    },
    {
        "recordId": "MAN-BM-OBJ_BM_PACKAGE_03",
        "kind": "INTERACTABLE",
        "templateIds": ["OBJ_BM_PACKAGE_03"],
        "xWu": 52.0,
        "yWu": 0.0,
        "respawnSeconds": 20,
        "claimPolicy": CLAIM_POLICY_PER_CHARACTER,
        "condition": (
            "P00-01; per-character claim (Production_Rules §5); "
            "DEV FIXTURE respawn 20s (atlas: 'kiện respawn' without a number)"
        ),
    },
]


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

        condition = (row.get("condition") or "").strip()
        if kind == "MOB" and quantity > 1:
            # QOD-17: open the manifest group composition instead of one
            # representative entity. Member 1 keeps the historic entity id;
            # later members get a stable _M suffix. Per-member templates are a
            # labelled DEV fixture (round robin) because the manifest only
            # declares the group's template set, not a per-member split.
            base_entity_id = entity_id_for(record_id)
            for index in range(quantity):
                template_id = template_ids[index % len(template_ids)]
                member_entity_id = (
                    base_entity_id if index == 0 else f"{base_entity_id}_M{index + 1}"
                )
                entities.append(
                    {
                        "entityId": member_entity_id,
                        "recordId": record_id,
                        "kind": kind,
                        "templateIds": [template_id],
                        "mapId": MAP_ID,
                        "floorId": FLOOR_ID,
                        "xWu": x_wu,
                        "yWu": y_wu,
                        "quantity": 1,
                        "respawnSeconds": 0,
                        "groupId": record_id,
                        "memberIndex": index + 1,
                        "groupQuantity": quantity,
                        "groupRespawnSeconds": respawn_seconds,
                        "composition": "ROUND_ROBIN_DEV_FIXTURE",
                        "condition": condition,
                    }
                )
            continue

        entity = {
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
            "condition": condition,
        }
        claim_policy = CLAIM_POLICY_BY_KIND.get(kind)
        if claim_policy is not None:
            entity["claimPolicy"] = claim_policy
        entities.append(entity)

    for supplement in ATLAS_SUPPLEMENTS:
        record_id = supplement["recordId"]
        entities.append(
            {
                "entityId": entity_id_for(record_id),
                "recordId": record_id,
                "kind": supplement["kind"],
                "templateIds": supplement["templateIds"],
                "mapId": MAP_ID,
                "floorId": FLOOR_ID,
                "xWu": supplement["xWu"],
                "yWu": supplement["yWu"],
                "quantity": 1,
                "respawnSeconds": supplement["respawnSeconds"],
                "claimPolicy": supplement["claimPolicy"],
                "claimPolicySource": PACKAGE_CLAIM_SOURCE,
                "condition": supplement["condition"],
            }
        )
        for template_id in supplement["templateIds"]:
            templates.setdefault(template_id, supplement["kind"])

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
