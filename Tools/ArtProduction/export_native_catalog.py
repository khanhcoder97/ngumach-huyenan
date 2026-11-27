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
dialogue_data=json.loads(dialogue.read_text(encoding="utf-8-sig"))
npc_names={n["npcId"]:n["displayName"] for n in dialogue_data["npcs"]}
labels={"OBJ_P00_01_PACKAGES":"Kiện hàng","OBJ_P00_02_CARPLING":"Cá Linh",
    "OBJ_P00_02_RIPPLES":"Gợn nước đã điều tra","OBJ_P00_03_WATERROOT":"Rễ Nước",
    "OBJ_P00_03_VILLAGERS":"Người dân đã cứu","OBJ_P00_03_WAVE_TRIAL":"Vượt đợt sóng",
    "OBJ_P00_04_WAVE_A":"Đợt Cá Linh","OBJ_P00_04_WAVE_B":"Đợt Rễ Nước",
    "OBJ_P00_05_BOSS":"Mãng Cốt","OBJ_P00_05_FRAGMENT":"Mảnh ấn","OBJ_P00_05_CLASS_CONFIRM":"Xác nhận nhập môn"}
quests=[]
for n in range(1,6):
    quest_id=f"P00-0{n}"
    path=ROOT/f"Implementation/Content/Examples/QuestDefinition/{quest_id}.json"
    # Alpha definitions are separate owner-reviewed source, never rewrite canonical activation.
    alpha=ROOT/f"Implementation/Content/Examples/QuestDefinitionAlpha/{quest_id}.json"
    if alpha.is_file():path=alpha
    data=json.loads(path.read_text(encoding="utf-8-sig"))
    entries=[e for e in dialogue_data["entries"] if e["questId"]==quest_id]
    offer=next(e for e in entries if e["command"]=="ACCEPT")
    clue=next(e for e in entries if e["questState"]=="ACTIVE")
    turn=next(e for e in entries if e["command"]=="TURN_IN")
    quests.append(dict(questId=quest_id,title=offer["title"],startNpc=npc_names[offer["speakerId"]],
        turnInNpc=npc_names[turn["speakerId"]],offer=offer["pages"][0],clue=clue["pages"][0],
        completed="\n\n".join(turn.get("committedPages",[])),
        objectives=[dict(objectiveId=o["objectiveId"],label=labels.get(o["objectiveId"],"Mục tiêu"),count=o["count"]) for o in data["objectives"]]))
    sources.append(dict(path=path.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(path.read_bytes().replace(b"\r\n",b"\n")).hexdigest()))
emit("quest_catalog.json",(json.dumps(dict(quests=quests),ensure_ascii=False,indent=2)+"\n").encode("utf8"))
emit("catalog_provenance.json",(json.dumps(dict(hashNormalization="UTF8 original bytes with CRLF normalized to LF",sources=sources,items=len(names),entities=len(entity_names)),indent=2)+"\n").encode("utf8"))
print(f"NATIVE_CATALOG: {len(names)} item labels; reviewed dialogue copied byte-for-byte")
