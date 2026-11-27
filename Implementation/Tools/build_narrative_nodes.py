#!/usr/bin/env python3
"""Build the runtime narrative node catalog from the quest dialogue data.

Source of truth: docs/production/Quest_Dialogue_Production_Data_vi.csv
Output: Implementation/Content/Runtime/narrative_nodes_v1.json

The dialogue file is *presentation*: text, conditions and flags. It must never
become an objective graph on its own, so this bundle carries only what the
server needs to decide "which node may this character see, and what does
entering it do" — node ids, order, type, speaker, condition, text key, next
node, on-enter event and flag. Text stays behind the text key.

Usage:
  python Implementation/Tools/build_narrative_nodes.py [--check]

--check rebuilds the bundle and diffs it against the committed file, which is
what CI runs so a CSV edit cannot land without its runtime record.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

SOURCE = Path("docs/production/Quest_Dialogue_Production_Data_vi.csv")
OUTPUT = Path("Implementation/Content/Runtime/narrative_nodes_v1.json")

NODE_TYPES = {"OFFER", "CLUE", "CHOICE", "TURN_IN"}
CONDITION_KEYS = {"QUEST_AVAILABLE", "QUEST_ACTIVE", "QUEST_READY_TO_TURN_IN"}
ENTER_EVENTS = {"ACCEPT_QUEST", "CHOICE_REQUIRED", "COMMIT_REWARD", "OBJECTIVE_PROGRESS"}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def build(rows):
    nodes = {}
    order = []
    for row in rows:
        node_id = (row.get("node_id") or "").strip()
        quest_id = (row.get("quest_id") or "").strip()
        if not node_id or not quest_id:
            fail(f"row without quest_id/node_id: {row}")

        node_type = (row.get("node_type") or "").strip()
        if node_type not in NODE_TYPES:
            fail(f"{node_id}: unknown node_type {node_type!r}")
        condition = (row.get("condition_key") or "").strip()
        if condition and condition not in CONDITION_KEYS:
            fail(f"{node_id}: unknown condition_key {condition!r}")
        event = (row.get("on_enter_event") or "").strip()
        if event and event not in ENTER_EVENTS:
            fail(f"{node_id}: unknown on_enter_event {event!r}")

        row_flag = (row.get("set_flag") or "").strip() or None
        choice_id = (row.get("choice_id") or "").strip()
        node = {
            "questId": quest_id,
            "graphId": (row.get("graph_id") or "").strip(),
            "nodeId": node_id,
            "order": int((row.get("node_order") or "0").strip() or 0),
            "type": node_type,
            "speakerNpcId": (row.get("speaker_id") or "").strip(),
            "conditionKey": condition or None,
            "textKey": (row.get("text_key") or "").strip() or None,
            "nextNodeId": (row.get("next_node_id") or "").strip() or None,
            "onEnterEvent": event or None,
            # A CHOICE node gets one row per option, and the option carries the
            # flag its pick sets; the node itself must not also carry one.
            "setFlag": None if choice_id else row_flag,
            "choiceGroupId": (row.get("choice_group_id") or "").strip() or None,
            "choices": [{"choiceId": choice_id, "flag": row_flag}] if choice_id else [],
        }

        if node_id not in nodes:
            nodes[node_id] = node
            order.append(node_id)
            continue

        existing = nodes[node_id]
        for key in ("questId", "graphId", "order", "type", "speakerNpcId",
                    "conditionKey", "textKey", "nextNodeId", "onEnterEvent",
                    "choiceGroupId"):
            if existing[key] != node[key]:
                fail(f"{node_id}: duplicate rows disagree on {key}")
        if not choice_id:
            fail(f"{node_id}: duplicate row without a choice_id")
        if any(choice["choiceId"] == choice_id for choice in existing["choices"]):
            fail(f"{node_id}: duplicate choice_id {choice_id}")
        existing["choices"].append({"choiceId": choice_id, "flag": row_flag})

    catalog = [nodes[node_id] for node_id in order]
    catalog.sort(key=lambda node: (node["questId"], node["order"], node["nodeId"]))
    known = set(nodes)
    next_ids = {node["nextNodeId"] for node in catalog if node["nextNodeId"]}
    for node in catalog:
        if node["nextNodeId"] and node["nextNodeId"] not in known:
            fail(f"{node['nodeId']}: next_node_id {node['nextNodeId']} does not exist")
        if node["type"] == "CHOICE" and not node["choices"]:
            fail(f"{node['nodeId']}: CHOICE node without options")

    flags = set()
    for node in catalog:
        if node["setFlag"]:
            flags.add(node["setFlag"])
        for choice in node["choices"]:
            if not choice["flag"]:
                fail(f"{node['nodeId']}: choice {choice['choiceId']} sets no flag")
            flags.add(choice["flag"])

    return {
        "schemaVersion": 1,
        "sourceRef": SOURCE.as_posix(),
        "conditionKeys": sorted(CONDITION_KEYS),
        "onEnterEvents": sorted(ENTER_EVENTS),
        "flags": sorted(flags),
        "terminalNodeIds": sorted(known - next_ids),
        "nodes": catalog,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not SOURCE.exists():
        fail(f"{SOURCE} not found; run from the repository root")
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    bundle = build(rows)
    serialized = json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=False) + "\n"

    if args.check:
        if not OUTPUT.exists():
            fail(f"{OUTPUT} is missing")
        if OUTPUT.read_text(encoding="utf-8") != serialized:
            fail(f"{OUTPUT} is stale; run python Implementation/Tools/build_narrative_nodes.py")
        print(f"OK: {OUTPUT} matches {SOURCE}")
        return

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(serialized, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT} ({len(bundle['nodes'])} nodes)")


if __name__ == "__main__":
    main()
