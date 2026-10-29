"""Authored audio recipes. No downloaded samples, lyrics, voices or existing tunes."""
import copy
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / 'Implementation/Content/DesignBaselines/audio_cues_v1.json'

MUSIC = {
    'ben_mua': dict(title='Bến Mưa — Thư chưa gửi', bpm=68, root=50, scale=[0,3,5,7,10],
        motif=[0,3,1,4,2,3,0,1], mood='rain', density=.62),
    'thang_long': dict(title='Thăng Long — Dòng người qua phố', bpm=92, root=50, scale=[0,2,4,7,9],
        motif=[0,2,4,3,1,2,0,3], mood='city', density=.9),
    'boss_mang_cot': dict(title='Mãng Cốt — Chuông dưới đầm', bpm=104, root=38, scale=[0,2,3,5,7,8,10],
        motif=[0,4,1,0,3,2,5,1], mood='boss', density=.95),
    'quiet_discovery': dict(title='Khám phá — Điều nước giữ lại', bpm=60, root=45, scale=[0,3,5,7,10],
        motif=[0,2,1,3,0,4,2,1], mood='quiet', density=.4),
    'lam_trieu': dict(title='Lâm Triều — Rừng nhớ tên', bpm=72, root=52, scale=[0,2,3,7,9],
        motif=[0,1,3,2,4,1,0,2], mood='forest', density=.64),
    'sa_hoa': dict(title='Sa Hỏa — Lò và cát', bpm=88, root=48, scale=[0,1,4,5,7,8,10],
        motif=[0,2,3,1,4,3,5,2], mood='desert', density=.82),
    'tran_son': dict(title='Trấn Sơn — Người qua cửa', bpm=96, root=38, scale=[0,2,5,7,9],
        motif=[0,3,2,4,1,0,2,3], mood='frontier', density=.85),
    'bach_uyen': dict(title='Bạch Uyên — Thành dưới triều', bpm=66, root=45, scale=[0,2,3,5,7,10],
        motif=[0,3,1,4,2,5,3,1], mood='underwater', density=.5),
    'rift_finale': dict(title='Ngũ Mạch — Năm dòng cùng chảy', bpm=100, root=50, scale=[0,2,4,7,9],
        motif=[0,1,3,4,2,3,1,0], mood='finale', density=.96),
}
FAMILIES = {
    'CLASS_MINH_KIEM': 'metal', 'CLASS_ANH_DAO': 'fire', 'CLASS_HUYEN_BUT': 'water',
    'CLASS_THACH_CHUY': 'stone', 'CLASS_LINH_CUNG': 'wood'
}
MONSTER_FAMILIES = {
    'aquatic': ['MOB_CARPLING','MOB_MIRRORFISH'],
    'roots': ['MOB_WATERROOT','MOB_DREAM_ROOT'],
    'beast': ['MOB_SHORE_STALKER','MOB_MOSS_BEAST'],
    'insect': ['MOB_SAND_BEETLE'],
    'raider': ['MOB_ASH_RAIDER','MOB_FALSE_SIGIL','MOB_FALSE_SOLDIER','MOB_AMBUSH_TROOPER','MOB_DROWNED_EXILE'],
    'construct': ['MOB_SMALL_STATUE','MOB_STONE_AUTOMATON','MOB_FLAME_SENTINEL'],
    'engine': ['MOB_FURNACE_WARDEN','MOB_SIEGE_ENGINE','MOB_MACHINIST','MOB_PRESSURE_GUARD'],
    'rift': ['MOB_RIFT_HUNTER','MOB_BOSS_ADD'],
}


def read_csv(name):
    with (ROOT/'docs/production'/name).open(encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def extra(key, name, family, semantic, *, bus='SFX', group='skill', priority=65, loop=False):
    return dict(cueKey=key, nameVi=name, bus=bus, voiceGroup=group, priority=priority,
        maxInstances=1 if group=='music' else 2, gain=.7, minGapMs=80,
        loop=loop, minDistanceWu=0 if bus in ('UI','Music') else 4,
        maxDistanceWu=0 if bus in ('UI','Music') else 28,
        triggerSemantic=semantic, wireStatus='REQUIRES_PRESENTATION_ADAPTER',
        authority='LOCAL_PRESENTATION' if bus in ('UI','Music','Ambience') else 'SERVER_CONFIRMED_EVENT_OR_STATE',
        stopPolicy='STATE_END_CANCEL_DESPAWN_OR_MAP_EXIT' if loop else 'ONE_SHOT',
        sourceRef='docs/production/Audio_Production_Direction_v1_vi.md', synthFamily=family)


def build_catalog():
    base = json.loads(BASE.read_text(encoding='utf-8-sig'))
    cues = copy.deepcopy(base['cues'])
    skills = {s['skillId']: s for s in json.loads((ROOT/'Implementation/Content/DesignBaselines/skill_vfx_art_v1.json').read_text(encoding='utf-8-sig'))['skills']}
    for c in cues:
        key = c['cueKey'].lower()
        if c.get('skillId'):
            s = skills[c['skillId']]
            c['synthFamily'] = FAMILIES[s['classId']]
            c['skillSlot'] = int(s['skillId'][-2:])
            c['variationSelector'] = 'CONFIRMED_HIT_INDEX_LIGHT_MEDIUM_HEAVY' if s['skillId']=='SK-MK-03' else 'NO_IMMEDIATE_REPEAT'
        elif key.startswith('music/'):
            c['synthFamily'] = 'music'
        elif key.startswith('ambience/'):
            c['synthFamily'] = 'ambience'
        elif '/boss/' in key:
            c['synthFamily'] = 'warning_water'
        elif '/ui/' in key or '/quest/' in key:
            c['synthFamily'] = 'ui'
        elif any(w in key for w in ('stone','mine','heavy')):
            c['synthFamily'] = 'stone'
        elif any(w in key for w in ('water','splash','herb')):
            c['synthFamily'] = 'water'
        elif any(w in key for w in ('wood','step_mud')):
            c['synthFamily'] = 'wood'
        elif '/step_' in key:
            c['synthFamily'] = 'stone'
        else:
            c['synthFamily'] = 'combat'

    placements = read_csv('World_Spawn_Gathering_Manifest_vi.csv')
    bosses = sorted({r['entity_id'] for r in placements if r['record_type']=='BOSS'})
    for boss in bosses:
        family = 'warning_water' if any(x in boss for x in ('SERPENT','MANG','PRESSURE')) else 'warning_wood' if 'TREE' in boss else 'warning_metal' if any(x in boss for x in ('FURNACE','SENTINEL','ENGINE','BANH')) else 'warning_rift'
        for action, vi, event in [('intro','xuất hiện','ENCOUNTER_START'),('warning','cảnh báo','ENCOUNTER_ATTACK_TELEGRAPH'),('success','kết thúc','ENCOUNTER_SUCCESS')]:
            # Mãng Cốt already has three separate mechanic warnings in the core63.
            if boss=='BOSS_MANG_COT' and action=='warning': continue
            c=extra(f'SFX/BOSS/{boss.lower()}_{action}', f'{boss} · {vi}', family, event,
                priority=100 if action=='warning' else 75)
            if action=='warning':
                c['maxDistanceWu']=48
                c['audience']='AFFECTED_ENCOUNTER_PARTICIPANTS_ONLY'
                c['visualEquivalentRequired']=True
            cues.append(c)

    for family in MONSTER_FAMILIES:
        for action, vi, event in [('attack','ra đòn','MONSTER_ATTACK_CONFIRMED'),('hurt','bị trúng','MONSTER_HP_DAMAGE_CONFIRMED'),('death','gục ngã','ENTITY_LIFE_DEATH_ONCE')]:
            cues.append(extra(f'SFX/MONSTER/{family}_{action}', f'{family} · {vi}', 'creature_'+family, event,
                group='hit' if action!='attack' else 'skill', priority=55))

    functions = [
        ('UI/item_pickup_common','Nhặt vật phẩm','ui','ITEM_GRANT_COMMITTED'),
        ('UI/item_pickup_rare','Nhặt đồ hiếm','reward','ITEM_RARE_GRANT_COMMITTED'),
        ('UI/item_pickup_legendary','Nhặt đồ truyền thuyết','reward','ITEM_LEGENDARY_GRANT_COMMITTED'),
        ('UI/item_equip','Mặc trang bị','metal','EQUIP_COMMITTED'),
        ('UI/potion_use','Dùng dược','water','CONSUMABLE_USE_COMMITTED'),
        ('UI/buff_apply','Nhận hỗ trợ','reward','BUFF_FIRST_APPLY'),
        ('UI/debuff_apply','Trúng bất lợi','rift','DEBUFF_FIRST_APPLY'),
        ('UI/inventory_full','Túi đầy','error','INVENTORY_FULL_REJECTED'),
        ('UI/mail_received','Thư mới','paper','MAIL_RECEIVED'),
        ('UI/notification','Thông báo','ui','LOCAL_NOTIFICATION_SHOWN'),
        ('FORGE/hammer_work','Búa rèn','metal','LOCAL_FORGE_AMBIENT_CONTACT'),
        ('FORGE/heat_ember','Than lò','fire','LOCAL_FORGE_HEAT'),
        ('FORGE/upgrade_success','Cường hóa thành công','reward','UPGRADE_SUCCESS_COMMITTED'),
        ('FORGE/upgrade_fail','Cường hóa thất bại','error','UPGRADE_FAILURE_COMMITTED'),
        ('FORGE/socket_success','Khảm thành công','crystal','SOCKET_COMMITTED'),
        ('FORGE/repair','Sửa chữa','metal','REPAIR_COMMITTED'),
        ('FORGE/salvage','Phân giải','stone','SALVAGE_COMMITTED'),
        ('TRADE/request','Mời giao dịch','ui','TRADE_INVITE_RECEIVED'),
        ('TRADE/offer_locked','Khóa đề nghị','metal','TRADE_OFFER_LOCKED'),
        ('TRADE/complete','Giao dịch hoàn tất','reward','TRADE_COMMITTED'),
        ('TRADE/buy','Mua hàng','coins','PURCHASE_COMMITTED'),
        ('TRADE/sell','Bán hàng','coins','SALE_COMMITTED'),
        ('GUILD/invite','Lời mời bang','paper','GUILD_INVITE_RECEIVED'),
        ('GUILD/level_up','Bang thăng cấp','reward','GUILD_LEVEL_COMMITTED'),
        ('GUILD/siege_start','Hiệu công thành','horn','SIEGE_STARTED'),
        ('GUILD/siege_victory','Thắng công thành','reward','SIEGE_RESULT_COMMITTED'),
        ('WORLD/mount_summon','Gọi tọa kỵ','crystal','MOUNT_SUMMON_ACCEPTED'),
        ('WORLD/mount_step','Bước tọa kỵ','wood','MOUNT_FOOT_CONTACT'),
        ('LIFE/seed_plant','Gieo hạt','wood','PLANT_COMMITTED'),
        ('LIFE/watering','Tưới cây','water','WATERING_COMMITTED'),
        ('LIFE/crop_harvest','Thu hoạch','paper','HARVEST_COMMITTED'),
        ('LIFE/fishing_cast','Thả câu','water','FISHING_CAST_ACCEPTED'),
        ('LIFE/fishing_bite','Cá cắn câu','ui','FISHING_BITE_PRESENTATION'),
        ('LIFE/fishing_reel','Thu dây câu','wood','FISHING_REEL_PRESENTATION'),
        ('LIFE/fishing_success','Câu cá thành công','reward','FISHING_GRANT_COMMITTED'),
        ('LIFE/fishing_escape','Cá thoát','water','FISHING_FAILED'),
        ('PET/summon','Gọi linh thú','crystal','PET_SUMMON_ACCEPTED'),
        ('PET/assist','Linh thú hỗ trợ','wood','PET_ASSIST_CONFIRMED'),
        ('PET/interact','Chăm linh thú','ui','PET_INTERACTION_ACCEPTED'),
        ('PVP/match_ready','Sẵn sàng trận','ui','MATCH_READY_CHECK'),
        ('PVP/countdown','Đếm ngược','warning_metal','MATCH_COUNTDOWN_TICK'),
        ('PVP/start','Bắt đầu trận','horn','MATCH_STARTED'),
        ('PVP/victory','Thắng trận','reward','MATCH_RESULT_VICTORY'),
        ('PVP/defeat','Kết thúc bại trận','error','MATCH_RESULT_DEFEAT'),
        ('PVP/objective_capture','Chiếm mục tiêu','crystal','OBJECTIVE_CAPTURE_COMMITTED'),
        ('PVP/flag_pickup','Nhận cờ','paper','FLAG_OWNER_CHANGED'),
        ('PVP/flag_drop','Rơi cờ','wood','FLAG_DROPPED'),
        ('ACCOUNT/login_success','Vào phiên','ui','SESSION_ESTABLISHED'),
        ('ACCOUNT/disconnect','Mất kết nối','error','LOCAL_CONNECTION_LOST'),
        ('ACCOUNT/reconnect','Kết nối lại','reward','SESSION_RESYNC_CONFIRMED'),
        ('COSMETIC/equip','Đổi ngoại trang','paper','COSMETIC_EQUIP_COMMITTED'),
        ('COSMETIC/dye','Nhuộm màu','water','COSMETIC_DYE_COMMITTED'),
        ('CRAFT/material_combine','Ghép nguyên liệu','crystal','MATERIAL_CRAFT_COMMITTED'),
        ('CRAFT/recipe_unlock','Học công thức','paper','RECIPE_UNLOCK_COMMITTED'),
        ('QUEST/accepted','Nhận nhiệm vụ','paper','QUEST_ACCEPT_COMMITTED'),
        ('QUEST/journal_update','Cập nhật nhật ký','paper','QUEST_OBJECTIVE_COMMITTED'),
    ]
    for key, name, family, event in functions:
        c = extra('SFX/'+key, name, family, event, bus='UI' if key.split('/')[0] in ('UI','TRADE','ACCOUNT','COSMETIC','QUEST') else 'SFX', group='footstep' if key=='WORLD/mount_step' else 'UI' if key.split('/')[0] in ('UI','TRADE','ACCOUNT','COSMETIC','QUEST') else 'skill')
        cues.append(c)
    for key,name in [('rain_heavy','Mưa nặng hạt'),('desert_wind','Gió Sa Hỏa'),('underwater','Dòng nước sâu'),('cave_drips','Hang nhỏ giọt'),('waterfall','Thác nước'),('city_night','Phố đêm'),('mountain_wind','Gió tháp'),('rift','Mạch nghịch')]:
        cues.append(extra('AMBIENCE/'+key,name,'ambience','LOCAL_ZONE_WEATHER_STATE',bus='Ambience',group='ambience',priority=10,loop=True))
    for key in ('lam_trieu','sa_hoa','tran_son','bach_uyen','rift_finale'):
        cues.append(extra('MUSIC/'+key,MUSIC[key]['title'],'music','LOCAL_MUSIC_DIRECTOR_WITH_SERVER_MODE_POLICY',bus='Music',group='music',priority=30,loop=True))
    for key,name in [('reveal','Vén một điều lạ'),('tension','Mạch chưa khép'),('resolve','Điều đã đối chiếu'),('transition','Qua một miền nước')]:
        cues.append(extra('SFX/CINEMA/'+key,name,'cinema','CINEMA_PRESENTATION_ONLY_NOT_QUEST_REWARD',priority=60))

    keys = [c['cueKey'] for c in cues]
    if len(keys)!=len(set(keys)): raise ValueError('duplicate cue key')
    for c in cues:
        c['assetState']='RENDER_RECIPE'
        c['clipPath']=None
        c['sourceLicense']='original_procedural_synthesis_no_external_samples'
        c['renderVariants']=1 if c['loop'] else 3
    return cues, base


def build_bindings(cues):
    placements=read_csv('World_Spawn_Gathering_Manifest_vi.csv')
    mobs=sorted(set(re.findall(r'MOB_[A-Z0-9_]+',' '.join(r['composition']+' '+r['entity_id'] for r in placements))))
    # Include a designed archetype even before a map placement has been exported.
    mobs=sorted(set(mobs)|set(re.findall(r'^\|\s*(MOB_[A-Z0-9_]+)\b',(ROOT/'docs/production/Art_Entity_Weather_UI_Visual_Bible_vi.md').read_text(encoding='utf-8-sig'),re.MULTILINE)))
    monster=[]
    for entity in mobs:
        base=entity.removesuffix('_ELITE')
        family=next((k for k,v in MONSTER_FAMILIES.items() if base in v),None)
        if family is None: raise ValueError('Unmapped monster: '+entity)
        monster.append(dict(entityId=entity, family=family, reuse='EXPLICIT_SHARED_ARCHETYPE',
            cues={a:f'SFX/MONSTER/{family}_{a}' for a in ('attack','hurt','death')}))
    bosses=[]
    for entity in sorted({r['entity_id'] for r in placements if r['record_type']=='BOSS'}):
        p='SFX/BOSS/'+entity.lower()
        warnings=['SFX/BOSS/mang_cot_sweep_warning','SFX/BOSS/mang_cot_emerge_warning','SFX/BOSS/mang_cot_bubble_warning'] if entity=='BOSS_MANG_COT' else [p+'_warning']
        bosses.append(dict(entityId=entity,intro=p+'_intro',warnings=warnings,success=p+'_success',
            state='REQUIRES_SERVER_ENCOUNTER_AND_TELEGRAPH_ADAPTER_NOT_NEW_ATTACKS'))
    known=json.loads((ROOT/'Implementation/Content/map_bounds.json').read_text(encoding='utf-8-sig'))['knownMapIds']
    direct={
        'MAP_BEN_MUA':('ben_mua','river_shore'),'MAP_THANG_LONG':('thang_long','thang_long_crowd'),
        'MAP_THANH_LAC':('thang_long','city_night'),'MAP_LAM_TRIEU':('lam_trieu','wind_canopy'),
        'MAP_SA_HOA':('sa_hoa','desert_wind'),'MAP_TRAN_SON':('tran_son','mountain_wind'),
        'MAP_TRAN_SON_SIEGE':('tran_son','mountain_wind'),'MAP_BACH_UYEN':('bach_uyen','underwater'),
        'MAP_VUC_NGHICH_MACH':('rift_finale','rift'),'MAP_DAI_NGU_MACH':('rift_finale','rift')}
    maps=[]
    for mid in known:
        profile=direct.get(mid)
        if profile is None:
            profile=('quiet_discovery','cave_drips') if mid.startswith('MAP_LAC_AN_TOWER_') else ('boss_mang_cot','cave_drips')
        maps.append(dict(mapId=mid,music='MUSIC/'+profile[0],ambience='AMBIENCE/'+profile[1],
            state='DESIGN_BINDING_CANDIDATE_REQUIRES_MODE_ZONE_REVIEW',
            overrides='Weather/encounter/safe-area/competitive server context wins; not automatic map-name activation'))
    npcs=[dict(npcId=r['npc_id'],openCue='SFX/UI/panel_open',closeCue='SFX/UI/panel_close',
        spokenVoice=None,voiceState='NOT_PRODUCED_FINAL_DIALOGUE_AND_VOICE_SOURCE_REQUIRED') for r in read_csv('NPC_Actor_Production_Registry_vi.csv')]
    companions=[dict(entityId=r['entity_id'],summonCue='SFX/PET/summon' if r['entity_type'] in ('PET','COMPANION') else 'SFX/WORLD/mount_summon',
        reuse='SHARED_NONVERBAL_CUE_NOT_RECORDED_SPECIES_VOCAL') for r in read_csv('Pet_Mount_Production_Data_vi.csv')]
    cinema=json.loads((ROOT/'Implementation/Content/Narrative/Cinema_Production_Pack_v1.json').read_text(encoding='utf-8-sig'))['scenes']
    return dict(skills=[dict(skillId=c['skillId'],cueKey=c['cueKey']) for c in cues if c.get('skillId')],
        monsters=monster,bosses=bosses,maps=maps,npcs=npcs,companions=companions,
        cinema=[dict(sceneId=s['sceneId'],stinger='SFX/CINEMA/reveal',timelineState='REQUIRES_PICTURE_LOCK_NOT_SYNCED',revealTier=s['revealTier']) for s in cinema])
