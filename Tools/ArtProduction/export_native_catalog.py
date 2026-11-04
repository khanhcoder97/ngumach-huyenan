"""Export labels and copy reviewed dialogue bytes; never change authoritative content."""
import argparse,csv,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"ClientGodot/assets/combat_v1"
names={};sources=[]
parser=argparse.ArgumentParser();parser.add_argument("--check",action="store_true")
check=parser.parse_args().check
def emit(name,data):
    target=OUT/name
    if check:
        assert target.read_bytes().replace(b"\r\n",b"\n")==data.replace(b"\r\n",b"\n"),f"stale native catalog: {name}"
    else:target.write_bytes(data)
for rel in ["docs/production/Item_Master_Catalog_vi.csv","docs/production/Item_Rarity_Variant_Catalog_vi.csv"]:
    path=ROOT/rel
    sources.append(dict(path=rel,sha256=hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()))
    for row in csv.DictReader(path.open(encoding="utf-8-sig")):
        key=row.get("item_id")
        name=row.get("display_name") or row.get("display_name_vi")
        if key and name:names[key]=name
dialogue=ROOT/"Client/Assets/Resources/Narrative/dialogue_vi.json"
emit("dialogue_vi.json",dialogue.read_bytes())
sources.append(dict(path=dialogue.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(dialogue.read_bytes().replace(b"\r\n",b"\n")).hexdigest()))
emit("item_names.json",(json.dumps(names,ensure_ascii=False,indent=2)+"\n").encode("utf8"))
world=ROOT/"docs/production/World_Spawn_Gathering_Manifest_vi.csv"
entity_names={}
for row in csv.DictReader(world.open(encoding="utf-8-sig")):
    if row["map_id"]!="MAP_BEN_MUA":continue
    entity_names["ENT_"+row["record_id"].replace("-","_")]=row["display_name_vi"]
sources.append(dict(path=world.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(world.read_bytes().replace(b"\r\n",b"\n")).hexdigest()))
emit("entity_names.json",(json.dumps(entity_names,ensure_ascii=False,indent=2)+"\n").encode("utf8"))
emit("catalog_provenance.json",(json.dumps(dict(hashNormalization="UTF8 original bytes with CRLF normalized to LF",sources=sources,items=len(names),entities=len(entity_names)),indent=2)+"\n").encode("utf8"))
print(f"NATIVE_CATALOG: {len(names)} item labels; reviewed dialogue copied byte-for-byte")
