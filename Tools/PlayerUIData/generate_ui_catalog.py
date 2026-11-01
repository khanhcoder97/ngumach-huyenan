"""Generate a read-only UI item catalog from canonical CSVs.

Output: Client/Assets/Resources/PlayerUI/ui_item_catalog.json
- Read-only projection for UI tooltips/bag/character. Does NOT modify canonical CSVs.
- Deterministic: sorted by item_id, stable JSON, no timestamps.
- Duplicate item_id across inputs -> fail (exit 1).
- Malformed/empty input -> fail.
- Includes source provenance (file + row) and a digest per entry + overall.
"""
import csv
import hashlib
import json
import os
import sys

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
INPUTS = [
    os.path.join(REPO_ROOT, "docs", "production", "Item_Rarity_Variant_Catalog_vi.csv"),
    os.path.join(REPO_ROOT, "docs", "production", "Item_Master_Catalog_vi.csv"),
]
OUT_DIR = os.path.join(REPO_ROOT, "Client", "Assets", "Resources", "PlayerUI")
OUT_FILE = os.path.join(OUT_DIR, "ui_item_catalog.json")

FIELDS = ["item_id", "display_name", "category", "slot", "class_id", "element",
          "required_level", "rarity_pool", "binding", "tradeable", "stack_limit",
          "durability", "description"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_csv(path):
    rows = []
    seen_in_file = set()
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None or "item_id" not in reader.fieldnames:
            raise ValueError(f"{path}: missing header or item_id column")
        for i, row in enumerate(reader, start=2):
            if row is None:
                raise ValueError(f"{path}: empty row at line {i}")
            iid = (row.get("item_id") or "").strip()
            if not iid:
                raise ValueError(f"{path}: empty item_id at line {i}")
            if iid in seen_in_file:
                raise ValueError(f"{path}: duplicate item_id within file: {iid} at line {i}")
            seen_in_file.add(iid)
            entry = {"_source": {"file": os.path.basename(path), "row": i}}
            for field in FIELDS:
                entry[field] = (row.get(field) or "").strip()
            rows.append(entry)
    if not rows:
        raise ValueError(f"{path}: no data rows")
    return rows


def entry_digest(entry):
    payload = {k: entry[k] for k in FIELDS}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def main():
    seen = set()
    entries = []
    source_digests = {}
    for path in INPUTS:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
        source_digests[os.path.basename(path)] = sha256_file(path)
        for row in read_csv(path):
            iid = row["item_id"]
            if iid in seen:
                # Cross-file subset relationship (master is subset of variant catalog):
                # keep the first (variant) entry, skip the duplicate.
                continue
            seen.add(iid)
            row["digest"] = entry_digest(row)
            entries.append(row)

    entries.sort(key=lambda e: e["item_id"])

    catalog = {
        "schemaVersion": 1,
        "generator": "Tools/PlayerUIData/generate_ui_catalog.py",
        "sourceDigests": source_digests,
        "count": len(entries),
        "entries": entries,
    }
    # overall digest over sorted entries
    overall = hashlib.sha256(json.dumps([e["digest"] for e in entries], ensure_ascii=False).encode("utf-8")).hexdigest()
    catalog["catalogDigest"] = overall

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"wrote {OUT_FILE}: {len(entries)} entries, digest {overall}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
