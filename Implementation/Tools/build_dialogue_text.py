"""Export Vietnamese gameplay prose into a read-only Unity resource; never export Ink checkpoints/events."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'docs/production/Quest_Dialogue_Production_Data_vi.csv'
EXPANSIONS = ROOT / 'docs/narrative/gameplay/dialogue_expansions_vi.json'
MANIFEST = ROOT / 'docs/production/World_Spawn_Gathering_Manifest_vi.csv'
REWRITES = [ROOT/'docs/narrative/gameplay/campaign_rewrite_vi.json', ROOT/'docs/narrative/gameplay/side_stories_rewrite_vi.json']
OUTPUT = ROOT / 'Client/Assets/Resources/Narrative/dialogue_vi.json'
STATES = {'QUEST_AVAILABLE': 'AVAILABLE', 'QUEST_ACTIVE': 'ACTIVE', 'QUEST_READY_TO_TURN_IN': 'READY_TO_TURN_IN'}
MAPS = {'P00': 'MAP_BEN_MUA', 'C1': 'MAP_THANH_LAC', 'C2': 'MAP_LAM_TRIEU', 'C3': 'MAP_SA_HOA',
        'C4': 'MAP_TRAN_SON', 'C5': 'MAP_BACH_UYEN', 'C6': 'MAP_VUC_NGHICH_MACH',
        'SQ-BM': 'MAP_BEN_MUA', 'SQ-TL': 'MAP_THANH_LAC', 'SQ-LT': 'MAP_LAM_TRIEU',
        'SQ-SH': 'MAP_SA_HOA', 'SQ-TS': 'MAP_TRAN_SON', 'SQ-BU': 'MAP_BACH_UYEN',
        'SQ-VN': 'MAP_VUC_NGHICH_MACH', 'SQ-DM': 'MAP_DAI_NGU_MACH'}

def maps_for(quest):
    if quest == 'C1-06': return ['MAP_THANG_LONG']
    if quest == 'C6-05': return ['MAP_DAI_NGU_MACH']
    prefix = '-'.join(quest.split('-')[:-1])
    if prefix not in MAPS: raise ValueError('Unmapped quest region: ' + quest)
    return [MAPS[prefix]]

def build():
    extra = json.loads(EXPANSIONS.read_text(encoding='utf-8-sig'))
    if extra['schemaVersion'] != 1 or extra['locale'] != 'vi': raise ValueError('Invalid expansion source')
    rewrites={}
    for source in REWRITES:
        packet=json.loads(source.read_text(encoding='utf-8-sig'))
        if packet['schemaVersion'] != 3 or packet['locale'] != 'vi': raise ValueError('Invalid rewrite source')
        for quest,parts in packet['quests'].items():
            if quest in rewrites or len(parts)!=3 or any(not isinstance(t,str) or not t.strip() for t in parts):
                raise ValueError('Invalid/duplicate quest rewrite: '+quest)
            rewrites[quest]=parts
    records = {};quests=set()
    with SOURCE.open(encoding='utf-8-sig', newline='') as f:
        for row in csv.DictReader(f):
            key = row['node_id']
            if key in records: continue  # CHOICE rows share one node; no client-owned flags are exported.
            quests.add(row['quest_id'])
            rewritten=rewrites[row['quest_id']][{'OFFER':0,'CLUE':1,'TURN_IN':2}.get(row['node_type'],2)]
            if row['node_type']=='CHOICE':
                rewritten='Nhật ký có phần được công bố và tên người cần bảo vệ. Công bố phải giữ danh tính theo lời người kể; giao hội đồng phải có biên nhận và một bản sao ở nơi khác. Lựa chọn cần được ghi nhận cùng tiến độ, không đổi chiến lợi phẩm.'
            state = STATES[row['condition_key']]
            records[key] = dict(nodeId=key, questId=row['quest_id'], title=row['quest_title_vi'],
                speakerId=row['speaker_id'], questState=state,
                command={'OFFER':'ACCEPT','TURN_IN':'TURN_IN'}.get(row['node_type'], 'NONE'),
                allowedMapIds=maps_for(row['quest_id']), pages=rewritten.split('\n\n'), committedPages=[], replies=[],
                requiredCheckpoint='C3_05_POST_BOSS_CHOICE' if row['node_type']=='CHOICE' else None)
    if quests != set(rewrites) or len(quests)!=76: raise ValueError('Rewrite must cover exactly all 76 canonical quests')
    for key, content in extra['entries'].items():
        if key not in records: raise ValueError('Unknown expansion node: ' + key)
        if set(content) - {'pages', 'committedPages', 'replies'}: raise ValueError('Prose cannot declare gameplay authority')
        records[key].update(content)
    with MANIFEST.open(encoding='utf-8-sig', newline='') as f:
        npcs = [dict(entityId='ENT_'+r['record_id'].replace('-','_').upper(), npcId=r['entity_id'],
                    mapId=r['map_id'], displayName=r['display_name_vi']) for r in csv.DictReader(f) if r['record_type']=='NPC']
    # Same identity algorithm as build_world_entities.py; coordinates stay in authoritative world snapshots.
    hashes = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_text(encoding='utf-8-sig').replace('\r\n','\n').encode()).hexdigest()
              for p in [SOURCE, EXPANSIONS, MANIFEST, *REWRITES]}
    bundle = dict(schemaVersion=1,locale='vi',sourceDigest=hashlib.sha256(json.dumps(hashes,sort_keys=True).encode()).hexdigest(),
                  presentationOnly=True, textVersion=3, sourceHashes=hashes, entries=list(records.values()),npcs=npcs)
    text = json.dumps(bundle,ensure_ascii=False,indent=2)+'\n'
    if unicodedata.normalize('NFC',text)!=text or '\ufffd' in text: raise ValueError('Non-NFC/invalid Unicode')
    return text, len(records), len(npcs)

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--check',action='store_true'); args=p.parse_args()
    text,entries,npcs=build()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding='utf-8').replace('\r\n','\n')!=text:
            raise SystemExit('Stale narrative resource: run Implementation/Tools/build_dialogue_text.py')
    else:
        OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(text,encoding='utf-8',newline='\n')
    # A reviewer can read the exact shipped pages with gate and source IDs beside them.
    bundle=json.loads(text)
    lines=['# Ngũ Mạch: Huyền Ấn — bản viết lại gameplay v3','',
        '36 nhiệm vụ chính,40 nhiệm vụ phụ;229 node nội dung. Prose đã viết lại; runtime chỉ mở phần có quest/actor/checkpoint được hỗ trợ. Không đổi reward hoặc objective bằng văn bản.',
        '', 'Nguồn: campaign_rewrite_vi.json, side_stories_rewrite_vi.json và dialogue_expansions_vi.json; resource sinh bằng build_dialogue_text.py. CSV cũ giữ nguyên logic và bản biên tập lịch sử.','']
    for e in bundle['entries']:
        lines.extend(['## '+e['questId']+' · '+e['title']+' / '+e['questState'],'',
            '`'+e['nodeId']+'` · `'+e['speakerId']+'`','',*sum(([page,''] for page in e['pages']),[])])
        for reply in e['replies']:lines.extend(['Lựa chọn đọc: '+reply['label'],'',reply['text'],''])
        if e['committedPages']:lines.extend(['Sau receipt đã xác nhận:','',*sum(([page,''] for page in e['committedPages']),[])])
    manuscript=ROOT/'docs/narrative/gameplay/CAMPAIGN_REWRITE_V3_vi.md';content='\n'.join(lines).rstrip()+'\n'
    if args.check:
        if not manuscript.exists() or manuscript.read_text(encoding='utf-8').replace('\r\n','\n')!=content:
            raise SystemExit('Stale v3 manuscript')
    else:manuscript.write_text(content,encoding='utf-8',newline='\n')
    print(f'PASS narrative resource: {entries} entries, {npcs} canonical NPC bindings; presentation only')

if __name__=='__main__': main()
