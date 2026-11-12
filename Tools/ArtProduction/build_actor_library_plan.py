"""Build the complete actor/VFX production queue from canonical text. No bitmap editing."""
import argparse,csv,hashlib,json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Actor_Library_20261107'
CLASSES={
 'CLASS_MINH_KIEM':('Minh Kiếm','MK','young martial swordsman, dark high topknot with gold clasp, ivory crossed tunic, short dark teal coat and gunmetal shoulder guards edged in muted gold, dark trousers and boots, slim straight jian sword'),
 'CLASS_ANH_DAO':('Ảnh Đao','AD','agile martial artist, swept dark hair with copper streak, charcoal and crimson short crossed coat, ochre belt, dark fitted trousers and boots, curved short dao in dark hip scabbard'),
 'CLASS_HUYEN_BUT':('Huyền Bút','HB','young ink sorceress, neat black braid and jade clasp, ivory and ink-blue scholarly crossed robe, restrained cyan stole, practical navy boots, closed ink pot and large bamboo calligraphy brush'),
 'CLASS_THACH_CHUY':('Thạch Chùy','TC','sturdy stocky guardian, medium tan skin, dark short hair and bronze headband, ochre and stone-grey quilted armour, squared shoulder plates, brown boots, rust sash and broad square stone hammer'),
 'CLASS_LINH_CUNG':('Linh Cung','LC','lean woodland archer, dark high ponytail, moss-green crossed tunic, short jade-and-oat layered shoulder cape, ochre wrist wraps, forest trousers, soft boots, compact bent wooden leaf-tip bow and short quiver')}

LAYOUT=(' ORIGINAL frame-based pixel-art asset for a Vietnamese fantasy MMORPG. Crisp hard pixel clusters, dark contour, limited stepped palette; no soft paint, blur, smooth AA or gradient. High overhead top-down camera, not isometric. Genuine transparent RGBA. Exactly EIGHT columns and TEN rows, all80 whole-body sprites fully inside the canvas, wide outer transparent margin and15% gutters. Each direction spans two rows of8frames: rows1-2 NORTH/back,3-4 NORTHEAST/back-right,5-6 EAST/right profile,7-8 SOUTHEAST/front-right,9-10 SOUTH/front. Sixteen genuinely distinct consecutive animation poses per direction, read left to right then next row. Never omit the eighth column or tenth row. Same identity, outfit, proportions and camera in all80cells. Stable ground anchor, no travel across cells. No text, labels, grid lines, borders, scenery, ground or cast shadows. All props and limbs fit inside their own cell. Shrink drawings uniformly to fit; never crop.')
ACTION={
 'idle':'calm16-pose breathing/blink/cloth or fin settle loop, seamless16to0, no walking',
 'walk':'16-pose walk cycle: left contact0, acceptance1-3, passing4, right swing5-7, right contact8, acceptance9-11, passing12, left swing13-15; natural opposite arms and seamless loop',
 'run':'16-pose controlled run cycle with alternating contact/flight, clothing lag, readable feet and continuous stride; anchor stays in place',
 'turn':'16-pose alert weight shift and turn-in-place preparation; each block keeps its declared viewing direction, no spin into another block',
 'basic_attack':'16-pose physical weapon strike: ready0-2, windup3-6, release7-10, follow-through11-13, recover14-15; clear hips, shoulders and weapon grip, no magical VFX',
 'hurt':'ONE16-pose non-gory hit reaction per direction: first row frames0-7 ONLY braces then builds recoil to the maximum at7; second row frames8-15 ONLY gradually recovers from that same recoil to neutral. Never start a second flinch in the second row. No repeated8-frame loop, travel or scenery',
 'death':'ONE16-pose non-gory defeat per direction: FIRST row frames0-7 starts upright then staggers and bends both knees; SECOND row frames8-15 continues that SAME fall, puts hand down8-9, collapses10-11, settles12-15. Last frame lies down and NEVER returns upright. Never restart the fall in the second row. No disappearing sprite',
 'dodge':'16-pose ground evasive step: coil0-3, low lateral motion4-9, regain footing10-13, finish14-15; no teleport, effects or ground translation',
 'interact':'16-pose character-specific spoken/work gesture using the authored profession and prop: anticipate0-3, perform4-10, settle11-15; preserve identity and held objects',
 'trial':'16-pose restrained demonstration by this sect master using their own weapon; readable anticipation, execution and recovery; no scenery or magical effects',
 'rescue_wait':'16-pose restrained waiting/struggling loop with low root bindings, no injury/gore; hands and face readable',
 'rescue_free':'16-pose release and regain balance: roots loosen, step onto secure feet, thank the player with an open hand, settle; do not move ground anchor'}

def read(name):return (ROOT/'docs/production'/name).read_text(encoding='utf-8-sig')
def dump(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def creature_action(actor,clip,default):
    """The human fall/walk template must not invent hands or knees on creatures."""
    if actor['kind'] not in ('MOB','BOSS'):return default
    base=actor.get('variantOf',actor['id'])
    if base=='MOB_WATERROOT' and clip in ('walk','run'):
        return 'ONE16-pose '+('quick low root-scuttle' if clip=='run' else 'slow root-creeping')+' cycle: alternating SHORT basal-root bundles contact, grip/load/pull, pass, extend and replant; opposite contact at8 and smooth15to0. Preserve rooted stump anatomy, moss, crown curls and front-seed occlusion for the declared view. Some roots stay grounded; no human limbs, hopping, long attack whip or leaf-only idle. Visual source only; does not authorize AI movement or assign world speed'
    if base=='MOB_WATERROOT' and clip=='turn':
        return 'ONE16-pose alert root replant/weight-shift: neutral0-3, one basal bundle grips while the opposite loosens4-7, slight braid/crown torsion and opposite replant8-11, settle original declared facing12-15. Keep camera/facing fixed, no spin into another direction, walking stride or humanoid limbs. Preparation only; heading changes remain renderer/gameplay state'
    if base=='MOB_WATERROOT' and clip=='death':
        return 'ONE16-pose root-stump defeat: neutral0-2; seed dims and crown roots sag3-5; braided stump buckles6-8; SAME collapse continues into a low wood-and-moss heap9-11; inert heap settles12-15. No human limbs, no second fall, no return upright, no disappearing sprite'
    if base=='MOB_WATERROOT' and clip=='hurt':
        return 'ONE16-pose planted root-stump recoil: brace0-3, root forks and leaf mass flex once4-7, recover from that SAME bend8-11, neutral12-15. Keep basal roots grounded; do not lock the moving crown, add human limbs, release a root whip or repeat the flinch'
    if clip=='death':
        return 'ONE16-pose species-appropriate defeat using the authored anatomy: rest0-2, body loses support3-7, SAME non-gory collapse or inert settling8-11, final defeated pose12-15. Preserve the creature silhouette; do not invent limbs absent from the reference, restart the fall, return upright or disappear'
    if clip in ('walk','run'):
        return 'Sixteen distinct consecutive poses of species-appropriate '+clip+' locomotion using only the authored anatomy (walk, creep, slither, swim or hover as described). Preserve body mass, actual appendages and declared view; complete a seamless cycle at a stable ground/body anchor. Do not invent human arms or feet on a creature without them'
    return default

def build():
    bible=read('Art_Entity_Weather_UI_Visual_Bible_vi.md');skill_text=read('Combat_Skills_VFX_Animation_Spec_vi.md')
    npcs=list(csv.DictReader(read('NPC_Actor_Production_Registry_vi.csv').splitlines()))
    actors=[];skills=[];jobs=[]
    def add(actor):
        if actor['kind']=='CLASS':
            actor['newProductionStrategy']='BAKED_SPRITE_SHEETS_V1'
            actor['bakedAssetUsage']='PRIMARY_ART_DIRECTION_REVIEW_PER_SHEET'
        actor['mirrorAllowed']=actor['id'] not in {'NPC_TA_VAN_KHANH','NPC_CO_VO_TUONG','NPC_TONG_BANH','BOSS_MANG_COT','BOSS_COSM','BOSS_TONG_BANH'}
        actors.append(actor)
        for clip in actor['requiredClips']:
            description=ACTION.get(clip,'16-pose '+clip+' with anticipation0-5, execution6-10 and recovery11-15')
            if clip.startswith('skill_'):
                sk=next(s for s in skills if s['classId']==actor['id'] and s['slot']==int(clip[-2:]))
                description='Sixteen-pose body/weapon casting choreography for '+sk['name']+'. Canonical description: '+sk['description']+' Render ONLY the actor and carried prop, no detached magic, attack shape, particles or target.'
            elif clip=='basic_attack':
                description={'CLASS_LINH_CUNG':'16-pose bow draw and release: nock0-3, draw4-7, aim8, release9-10, follow-through11-13, recover14-15. Never swing the bow like a sword.', 'CLASS_HUYEN_BUT':'16-pose physical calligraphy brush sweep: prepare0-3, lift4-7, draw one invisible ink stroke8-10, follow-through11-13, recover14-15. No detached VFX.', 'CLASS_THACH_CHUY':'16-pose weighty square stone-hammer downswing: ready0-2, both hands raise shaft3-7, drive downward8-10, follow-through11-13, recover14-15.'}.get(actor['id'],description)
            elif re.match(r'(telegraph|attack|recovery)_\d+',clip):
                phase=clip.split('_')[0];description='Sixteen-pose '+phase+' sequence for attack variant '+clip[-2:]+'. Follow the authored tell/action in the creature description. Telegraph anticipates without hitting, attack releases, recovery settles. No separate magical VFX, environment or targets.'
            description=creature_action(actor,clip,description)
            key=actor['id'].lower()+'_'+clip
            jobs.append(dict(id=key,ownerId=actor['id'],kind=actor['kind'],clip=clip,columns=8,rows=10,framesPerDirection=16,directions=['N','NE','E','SE','S'],status='REQUESTED',referenceJob=None if clip=='idle' else actor['id'].lower()+'_idle',prompt='Subject '+actor['id']+' — '+actor['name']+'. Identity: '+actor['appearance']+'. Animation: '+description+'.'+LAYOUT))
            if not actor['mirrorAllowed']:
                for direction in ['SW','W','NW']:
                    jobs.append(dict(id=key+'_'+direction.lower(),ownerId=actor['id'],kind=actor['kind'],clip=clip,direction=direction,columns=4,rows=4,framesPerDirection=16,directions=[direction],status='REQUESTED',referenceJob=actor['id'].lower()+'_idle',prompt='Original anatomically consistent '+direction+' view of '+actor['name']+'. Identity: '+actor['appearance']+'. '+description+'. EXACT4columns4rows16consecutive full-body frames, one direction ONLY: '+direction+'. Preserve the correct anatomical side of bandages, broken horn, mask, armour and held props: redraw this angle, do NOT horizontally mirror another view. All sixteen frames whole, padded and separate; stable ground anchor. Top-down crisp pixel art, limited stepped palette, genuine transparent alpha. No text/grid/border/background/ground/shadow.'))
    for match in re.finditer(r'\*\*(SK-([A-Z]{2})-(\d{2})) — (.*?)\*\*\s*\n(.*?)(?=\n\*\*SK-|\n#{2,3} |\Z)',skill_text,re.S):
        sid,code,slot,name,body=match.groups();cid=next(k for k,v in CLASSES.items() if v[1]==code)
        skills.append(dict(id=sid,classId=cid,slot=int(slot),name=name,description=body.strip()))
    for cid,(name,code,appearance) in CLASSES.items():
        add(dict(id=cid,name=name,kind='CLASS',appearance=appearance,uniqueFace=True,renderHeightPx=36,requiredClips=['idle','walk','basic_attack',*[f'skill_{i:02}' for i in range(1,7)],'hurt','death','dodge']))
    # Only table definition rows create actors. Regex references elsewhere are not new species.
    creatures=[]
    for line in bible.splitlines():
        if not line.startswith('| '):continue
        cells=[x.strip() for x in line.strip('|').split('|')]
        match=re.match(r'((?:MOB|BOSS)_[A-Z0-9_]+) — (.+)',cells[0])
        if match and match[1] not in {x['id'] for x in creatures}:
            mid,name=match.groups();boss=mid.startswith('BOSS_')
            attacks=3 if boss else 2
            clips=['idle','walk','hurt','death']+[f'{phase}_{i:02}' for i in range(1,attacks+1) for phase in ['telegraph','attack','recovery']]
            if not boss:clips+=['run','turn']
            creatures.append(dict(id=mid,name=name,kind='BOSS' if boss else 'MOB',appearance='; '.join(cells[1:]),uniqueFace=True,renderHeightPx=150 if boss else 40,requiredClips=clips))
    for actor in creatures:add(actor)
    for n in npcs:
        # Registry/bible are canon. Archetype use is declared, never a completed bespoke face.
        line=next((x for x in bible.splitlines() if x.startswith('| ') and n['npc_id'] in x.split('|')[1]),'')
        appearance=('; '.join(x.strip() for x in line.strip('|').split('|')[1:]) if line else 'Regional Vietnamese fantasy '+n['role_profile']+', wardrobe '+n['costume_set_id']+', palette '+n['palette_id']+', identifying detail '+n['visual_delta'])
        if n['unique_face']=='true':appearance+='; this is a distinct named person with a bespoke face, not the player or a generic crowd clone'
        clips=['idle','walk','interact']
        if n['role_profile']=='SECT_MASTER':clips+=['trial']
        if n['npc_id'] in ('NPC_BM_RESCUE_01','NPC_BM_RESCUE_02'):clips+=['rescue_wait','rescue_free']
        add(dict(id=n['npc_id'],name=n['display_name_vi'],kind='NPC',appearance=appearance,uniqueFace=n['unique_face']=='true',archetype=n['base_prefab_id'],paletteId=n['palette_id'],renderHeightPx=38,requiredClips=clips))
    for s in skills:
        jobs.append(dict(id=s['id'].lower().replace('-','_')+'_vfx',ownerId=s['id'],kind='VFX',clip='full_timeline',columns=4,rows=4,framesPerDirection=16,directions=['OMNI_OR_ROTATED'],status='REQUESTED',referenceJob=None,prompt='Original production pixel-art spell-effect sprite atlas for '+s['id']+' — '+s['name']+'. Canonical visual brief: '+s['description']+'. Render only the visual energy, never a person/weapon/user interface. Sixteen genuinely distinct consecutive frames in EXACT4columns4rows, read left-to-right top-to-bottom: anticipation0-3, release4-6, main effect7-11, dissipation12-15. First/last frames still contain a small visible effect, not empty. Genuine transparent RGBA, hard pixel clusters, limited stepped palette, no blur, no smooth glow/bloom, no text/grid/borders/ground, wide gutters; effect wholly inside each cell. Top-down ground perspective and clear negative space. Visual art only; no numeric damage, no target or environment.'))
    assert len(skills)==30 and len(npcs)==83
    assert all('\n## ' not in skill['description'] for skill in skills),'skill parse must stop at the next section'
    ids=[a['id'] for a in actors];assert len(set(ids))==len(ids)
    # Identify all canonical manifest references, including explicit elite variants.
    rows=list(csv.DictReader(read('World_Spawn_Gathering_Manifest_vi.csv').splitlines()))
    refs=sorted({i for r in rows for field in ['entity_id','composition'] for i in re.findall(r'\b(?:MOB|BOSS)_[A-Z0-9_]+',r[field])})
    aliases=[];unresolved=[];selectors=[]
    for ref in refs:
        if ref in ids:continue
        if ref=='BOSS_WEEKLY_ROTATION':
            rotation=list(csv.DictReader(read('Weekly_Boss_Rotation_Data_vi.csv').splitlines()))
            choices=sorted({r['source_boss_id'] for r in rotation});assert all(x in ids for x in choices)
            selectors.append(dict(id=ref,source='docs/production/Weekly_Boss_Rotation_Data_vi.csv',actorIds=choices));continue
        if ref.endswith('_ELITE') and ref[:-6] in ids:
            original=next(a for a in actors if a['id']==ref[:-6]);variant={**original,'id':ref,'name':original['name']+' tinh anh','variantOf':original['id'],'appearance':original['appearance']+'; elite variant retains the same species but has visibly reinforced armour/ridges/spines as appropriate and a distinct readable elite silhouette, not just a colour swap'}
            add(variant);aliases.append(dict(id=ref,baseActor=ref[:-6],variant='ELITE',status='DISTINCT_VARIANT_CLIPS_REQUIRED'))
        else:unresolved.append(ref)
    return dict(schemaVersion=1,scope='BASE_ACTOR_ANIMATIONS_AND_SKILL_TIMELINE_CANDIDATES',
        excludes=['equipment/outfit/body variants','static portraits and skill icons','mounts/pets','map tiles and UI','additional split VFX components required by each mechanic'],
        policy='Actor_Animation_16_20F_60FPS_20261107_vi.md',renderTargetFps=60,framesPerDirection=16,directionOrder=['N','NE','E','SE','S','SW','W','NW'],mirrorMap={'SW':'SE','W':'E','NW':'NE'},actors=actors,skills=skills,aliases=aliases,selectors=selectors,unresolvedManifestIds=unresolved),jobs

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    catalogue,jobs=build()
    for path,value in [(ART/'production_catalog.json',catalogue),(ART/'generation_jobs.json',jobs),(ROOT/'ClientGodot/assets/actor_library_v1/catalog.json',catalogue)]:
        if args.check:assert json.loads(path.read_text(encoding='utf8'))==value,'stale catalogue/queue: '+str(path)
        else:dump(path,value)
    print(json.dumps(dict(actors=len(catalogue['actors']),classes=sum(a['kind']=='CLASS' for a in catalogue['actors']),mobs=sum(a['kind']=='MOB' for a in catalogue['actors']),bosses=sum(a['kind']=='BOSS' for a in catalogue['actors']),npcs=sum(a['kind']=='NPC' for a in catalogue['actors']),skills=len(catalogue['skills']),pagesRequired=len(jobs),unresolved=catalogue['unresolvedManifestIds']),ensure_ascii=False))
