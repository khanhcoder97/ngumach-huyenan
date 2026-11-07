import json, hashlib, unicodedata, os
ROOT = os.path.expanduser('~/workspace/projects/ngumach-media02')
def sha(p):
    return hashlib.sha256(open(p,'rb').read()).hexdigest()
pack = json.load(open(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'))
dec  = json.load(open(f'{ROOT}/Implementation/Content/DesignBaselines/media_p0_decisions_20261105.json'))
scenes = {s['sceneId']: s for s in pack['scenes']}

# Dialogue windows: DECIDED from DEC-MEDIA-P0-20261105 where given; otherwise PROPOSED animatic placement (not canonical)
windows = {
 'CIN_001': dict(shotId='CIN_001_S05', start=24.8, end=28.5, status='DECIDED_DEC_MEDIA_P0', speaker='NPC_LYAN', onscreen=True),
 'CIN_002': dict(shotId='CIN_002_S02', start=7.0, end=11.0, status='PROPOSED_ANIMATIC_PLACEMENT', speaker='NPC_TA_VAN_KHANH', onscreen=True),
 'CIN_004': dict(shotId='CIN_004_S02', start=7.5, end=9.5, status='PROPOSED_ANIMATIC_PLACEMENT; OFFSCREEN_DECIDED_DEC_MEDIA_P0', speaker='NPC_LYAN', onscreen=False),
}
stem_pool = {
 'CIN_001': ['AMBIENCE/rain_light','AMBIENCE/river_shore','MUSIC/quiet_discovery','SFX/CINEMA/reveal'],
 'CIN_002': ['AMBIENCE/underwater','AMBIENCE/river_shore','SFX/CINEMA/tension'],
 'CIN_004': ['AMBIENCE/river_shore','MUSIC/boss_mang_cot','SFX/CINEMA/reveal'],
}
def srt_time(t):
    h=int(t//3600); m=int((t%3600)//60); s=int(t%60); ms=int(round((t-int(t))*1000))
    if ms==1000: s+=1; ms=0
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

manifest = {
 'schemaVersion': 1,
 'checkpoint': 'MEDIA-02 checkpoint 01 - P0 animatic timing + SRT draft',
 'decisionId': 'DEC-MEDIA-P0-20261105',
 'branch': 'muse/media-production-20261104',
 'baseSha': 'cf171786baebb10c3f17d3060d47429faf3e4026',
 'sourceHashes': {
   'Cinema_Production_Pack_v1.json': sha(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'),
   'media_p0_decisions_20261105.json': sha(f'{ROOT}/Implementation/Content/DesignBaselines/media_p0_decisions_20261105.json'),
   'game_audio_v1.json': sha(f'{ROOT}/Client/Assets/AudioManifests/game_audio_v1.json'),
 },
 'inventoryRebaselined': {'scenes': len(pack['scenes']), 'shots': sum(len(s['shots']) for s in pack['scenes']), 'seconds': sum(s['durationSeconds'] for s in pack['scenes'])},
 'scenes': [],
}
for cid in ['CIN_001','CIN_002','CIN_004']:
    s = scenes[cid]; w = windows[cid]
    line = s['dialogueLines'][0]
    dialogue_text = line.split(': ',1)[1] if ': ' in line else line
    dialogue_text = unicodedata.normalize('NFC', dialogue_text)
    offset = 0.0; shots_out = []
    for sh in s['shots']:
        entry = {'shotId': sh['shotId'], 'startSeconds': offset, 'endSeconds': offset + sh['durationSeconds'], 'camera': sh['camera'], 'referenceRequirement': sh['referenceRequirement']}
        if sh['shotId'] == w['shotId']:
            entry['dialogue'] = {'speaker': w['speaker'], 'onscreen': w['onscreen'], 'windowSeconds': [w['start'], w['end']], 'status': w['status'], 'text': dialogue_text}
        shots_out.append(entry); offset += sh['durationSeconds']
    timing = {'sceneId': cid, 'questId': s['questId'], 'title': s['title'], 'durationSeconds': s['durationSeconds'],
              'playback': s['playback'], 'runtimeActivation': s['runtimeActivation'], 'charactersOnScreen': s['characters'],
              'audioDirection': s['audioDirection'], 'candidateStems': stem_pool[cid], 'stemStatus': 'CANDIDATE_POOL_NOT_LOCKED',
              'shots': shots_out}
    outdir = f'{ROOT}/Implementation/Content/Narrative/Deliveries/{cid}'
    os.makedirs(outdir, exist_ok=True)
    tpath = f'{outdir}/{cid}_timing_v1.json'
    json.dump(timing, open(tpath,'w'), ensure_ascii=False, indent=2)
    srt = f"1\n{srt_time(w['start'])} --> {srt_time(w['end'])}\n{dialogue_text}\n"
    srt = unicodedata.normalize('NFC', srt)
    spath = f'{outdir}/{cid}_vi.srt'
    open(spath,'w',encoding='utf-8').write(srt)
    manifest['scenes'].append({'sceneId': cid, 'timingFile': f'Implementation/Content/Narrative/Deliveries/{cid}/{cid}_timing_v1.json',
        'srtFile': f'Implementation/Content/Narrative/Deliveries/{cid}/{cid}_vi.srt', 'srtSha256': sha(spath),
        'srtStatus': 'DRAFT', 'dialogueWindowStatus': w['status'],
        'charsPerSecond': round(len(dialogue_text)/ (w['end']-w['start']), 2)})
    print(cid, 'chars', len(dialogue_text), 'cps', manifest['scenes'][-1]['charsPerSecond'])

mpath = f'{ROOT}/Implementation/Content/Narrative/Deliveries/P0_timing_manifest_v1.json'
json.dump(manifest, open(mpath,'w'), ensure_ascii=False, indent=2)
print('manifest written', mpath)
