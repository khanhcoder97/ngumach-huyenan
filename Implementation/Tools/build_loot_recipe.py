#!/usr/bin/env python3
"""Build the runtime loot recipe bundle from the canonical loot CSV.

Source of truth: docs/production/Loot_Recipe_Reward_Production_Data_vi.csv
(LOOT_ENTRY rows). Output: Implementation/Content/Runtime/loot_recipe_v1.json

The bundle is DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION and grantEnabled=false:
the mob coin band has no executable source yet (DEC/work-order Q4), so actual
mob-loot grants stay OFF. Rolls are one-per-group, then SELECT_ONE by weight.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

CSV_PATH = Path("docs/production/Loot_Recipe_Reward_Production_Data_vi.csv")
OUTPUT = Path("Implementation/Content/Runtime/loot_recipe_v1.json")

BUNDLE_ID = "LOOT_RECIPE_V1"
ACTIVATION = "DESIGN_ONLY_REQUIRES_RUNTIME_MIGRATION"
SEED_VERSION = "loot-rng-v1"

# P1 placements resolved against the Bến Mưa world-entity templates. The boss
# uses the QUEST placement pool (P00-05) per the production notes; the boss
# itself stays BOSSDATA_BLOCKED until the QOD-19 encounter data exists.
MOB_SOURCE_MAP = [
    {
        "mobTemplateId": "MOB_CARPLING",
        "sourceId": "LT_MOB_CARPLING",
        "provenance": "MANIFEST_SPAWN_BM_01_02_04_ESCORT_A",
    },
    {
        "mobTemplateId": "MOB_WATERROOT",
        "sourceId": "LT_MOB_WATERROOT",
        "provenance": "MANIFEST_SPAWN_BM_03_04_ESCORT_B",
    },
    {
        "mobTemplateId": "MOB_SHORE_STALKER",
        "sourceId": "LT_MOB_SHORE_STALKER",
        "provenance": "MANIFEST_SPAWN_BM_06",
    },
    {
        "mobTemplateId": "MOB_SHORE_STALKER_ELITE",
        "sourceId": "LT_MOB_SHORE_STALKER_ELITE",
        "provenance": "MANIFEST_SPAWN_BM_07_ELITE",
    },
    {
        "mobTemplateId": "BOSS_MANG_COT",
        "sourceId": "LT_BOSS_MANG_COT_QUEST",
        "provenance": "QUEST_PLACEMENT_P00_05",
        "bossBlocked": True,
    },
]


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=CSV_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()

    if not args.csv.is_file():
        fail(f"{args.csv} not found")

    with args.csv.open(encoding="utf-8-sig", newline="") as handle:
        all_rows = list(csv.DictReader(handle))
    rows = [row for row in all_rows if row["row_type"] == "LOOT_ENTRY"]
    if not rows:
        fail("no LOOT_ENTRY rows")

    # RECIPE rows are craft definitions, not loot groups. No craft service exists
    # and the forge spec's baseline table disagrees with these rows, so they stay
    # unexported — but the unsupported ledger must name every dropped row instead
    # of silently discarding them.
    recipe_rows = sorted(
        (row for row in all_rows if row["row_type"] == "RECIPE"),
        key=lambda item: item["entry_id"],
    )
    recipe_ids = [row["entry_id"].strip() for row in recipe_rows]
    if len(set(recipe_ids)) != len(recipe_ids):
        fail("duplicate RECIPE entry_id")

    # REWARD/CURRENCY_REWARD rows carry the per-source ledger caps (cap_scope) for
    # activity payouts. No reward-ledger service reads them and cap enforcement
    # awaits an owner decision, so they stay unexported but must be named.
    reward_rows = sorted(
        (row for row in all_rows if row["row_type"] == "REWARD"),
        key=lambda item: item["entry_id"],
    )
    currency_reward_rows = sorted(
        (row for row in all_rows if row["row_type"] == "CURRENCY_REWARD"),
        key=lambda item: item["entry_id"],
    )
    for label, group in (("REWARD", reward_rows), ("CURRENCY_REWARD", currency_reward_rows)):
        ids = [row["entry_id"].strip() for row in group]
        if len(set(ids)) != len(ids):
            fail(f"duplicate {label} entry_id")
        for row in group:
            if not (row["item_or_currency_id"] or "").strip():
                fail(f"{row['entry_id']}: {label} row has no item_or_currency_id")
            if not (row["cap_scope"] or "").strip():
                fail(f"{row['entry_id']}: {label} row has no cap_scope")

    # Gear only appears in RECIPE rows (craft outputs). If a mob loot table ever
    # names an EQ- item, the rarity/roll vector that decides which variant drops
    # does not exist in any source, so refuse instead of shipping a guess.
    gear_loot = [
        row for row in rows
        if (row.get("item_or_currency_id") or "").strip().startswith("EQ-")
    ]
    if gear_loot:
        fail(
            "LOOT_ENTRY references gear without a gear roll vector in source: "
            + ", ".join(row["entry_id"] for row in gear_loot)
        )

    sources = {}
    for row in sorted(rows, key=lambda item: item["entry_id"]):
        source_id = row["source_id"].strip()
        group_id = row["group_id"].strip()
        mode = row["group_mode"].strip()
        if mode not in ("SELECT_ONE", "ALL"):
            fail(f"{row['entry_id']}: unsupported group_mode '{mode}'")
        try:
            chance = int(row["group_chance_bps"])
            weight = int(row["selection_weight"])
            quantity_min = int(row["quantity_min"])
            quantity_max = int(row["quantity_max"])
        except ValueError:
            fail(f"{row['entry_id']}: non-integer numeric fields")
        if not (0 <= chance <= 10000):
            fail(f"{row['entry_id']}: group_chance_bps out of range")
        if weight < 1 or quantity_min < 1 or quantity_max < quantity_min:
            fail(f"{row['entry_id']}: invalid weight/quantity")

        entry = {
            "entryId": row["entry_id"].strip(),
            "itemId": row["item_or_currency_id"].strip(),
            "quantityMin": quantity_min,
            "quantityMax": quantity_max,
            "weight": weight,
        }
        source = sources.setdefault(source_id, {"sourceId": source_id, "groups": {}})
        group = source["groups"].get(group_id)
        if group is None:
            group = {"groupId": group_id, "mode": mode, "chanceBps": chance, "entries": []}
            source["groups"][group_id] = group
        elif group["mode"] != mode or group["chanceBps"] != chance:
            fail(f"{source_id}/{group_id}: inconsistent mode/chance rows")
        group["entries"].append(entry)

    payload_sources = []
    for source_id in sorted(sources):
        groups = sources[source_id]["groups"]
        payload_sources.append(
            {
                "sourceId": source_id,
                "groups": [
                    {
                        "groupId": groups[group_id]["groupId"],
                        "mode": groups[group_id]["mode"],
                        "chanceBps": groups[group_id]["chanceBps"],
                        "entries": groups[group_id]["entries"],
                    }
                    for group_id in sorted(groups)
                ],
            }
        )

    known_sources = {source["sourceId"] for source in payload_sources}
    mapping = []
    for item in MOB_SOURCE_MAP:
        if item["sourceId"] not in known_sources:
            fail(f"{item['mobTemplateId']}: source '{item['sourceId']}' missing from CSV")
        source = next(s for s in payload_sources if s["sourceId"] == item["sourceId"])
        if any(group["mode"] != "SELECT_ONE" for group in source["groups"]):
            fail(f"{item['sourceId']}: P1 mob sources must be SELECT_ONE groups")
        mapping.append(item)

    payload = {
        "schemaVersion": 1,
        "bundleId": BUNDLE_ID,
        "activation": ACTIVATION,
        "grantEnabled": False,
        "grantBlockedReason": "COIN_BAND_MISSING",
        "sourceRef": str(args.csv).replace("\\", "/"),
        "rng": {
            "seedVersion": SEED_VERSION,
            "groupRoll": "ONE_ROLL_PER_GROUP",
            "selection": "WEIGHTED_SELECT_ONE",
        },
        "mobTemplateToSource": mapping,
        "sources": payload_sources,
        "unsupported": {
            "mobCoinBand": "MISSING_SOURCE",
            "bossLoot": "BOSSDATA_BLOCKED_UNTIL_QOD_19",
            "craftRecipes": {
                "status": "PRESENT_IN_SOURCE_NOT_EXPORTED",
                "reason": "NO_CRAFT_SERVICE; FORGE_SPEC_BASELINE_CONFLICT_UNRESOLVED",
                "count": len(recipe_ids),
                "entryIds": recipe_ids,
            },
            "activityRewards": {
                "status": "PRESENT_IN_SOURCE_NOT_EXPORTED",
                "reason": "NO_REWARD_LEDGER_SERVICE; CAPS_UNENFORCED_PENDING_OWNER",
                "count": len(reward_rows),
                "entryIds": [row["entry_id"].strip() for row in reward_rows],
            },
            "currencyRewards": {
                "status": "PRESENT_IN_SOURCE_NOT_EXPORTED",
                "reason": "NO_REWARD_LEDGER_SERVICE; CAPS_UNENFORCED_PENDING_OWNER",
                "count": len(currency_reward_rows),
                "entryIds": [row["entry_id"].strip() for row in currency_reward_rows],
            },
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    entries = sum(len(group["entries"]) for source in payload_sources for group in source["groups"])
    print(
        f"OK: wrote {len(payload_sources)} loot sources / {entries} entries to {args.output}"
        f"; {len(recipe_ids)} RECIPE rows named in unsupported (not exported)"
        f"; {len(reward_rows)} REWARD + {len(currency_reward_rows)} CURRENCY_REWARD rows"
        " named in unsupported (not exported)"
    )


if __name__ == "__main__":
    main()
