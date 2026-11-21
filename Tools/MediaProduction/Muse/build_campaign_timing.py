"""MEDIA-02 checkpoint 06: M3 campaign timing pack for the 16 cinema scenes
not yet delivered (all scenes except P0 CIN_001/002/004 and P1 CIN_006).

Sources (read, not invented):
- Implementation/Content/Narrative/Cinema_Production_Pack_v1.json (20 scenes,
  63 shots, 378 seconds; each non-P0 scene is 18s / 3 shots x 6s, canonical
  dialogueLines as "Speaker: text", playback OPTIONAL_SKIP_SAFE_LAYER,
  fallback "Approved still keyframe plus localized recap; never blocks quest").
- Client/Assets/AudioManifests/game_audio_v1.json bindings.cinema (every scene
  binds stinger SFX/CINEMA/reveal, REQUIRES_PICTURE_LOCK_NOT_SYNCED, with a
  revealTier per scene).

Status honesty (same convention as checkpoints 01 and 05):
- The pack assigns NO shot/timecode to any dialogue line in these 16 scenes,
  so EVERY window below is PROPOSED_ANIMATIC_PLACEMENT, not canonical.
  Only CIN_001_S05 (24.8-28.5s, DEC-MEDIA-P0 Q1) is decided, and it is not
  part of this pack.
- Placement rule, applied uniformly and stated so a director can overturn it
  in one place: a single line goes in the last shot (S03, 12.0-18.0s) inset
  0.5s each side -> 12.5-17.5s (5.0s). Two exceptions, both forced by the
  numbers, not by taste:
  * CIN_011 (87 chars): 5.0s would read at 17.4 chars/s, above the 12-17
    guide used in checkpoint 05, so its window widens to 12.2-17.8s (5.6s,
    15.5 chars/s, 0.2s headroom each side) and is flagged widenedForRate.
  * CIN_018 (two lines, 42 + 78 = 120 chars): one 5.0s window would read at
    24.0 chars/s, so the lines split across S02 (6.5-11.5s, line 1) and S03
    (12.5-17.5s, line 2). No line is merged, dropped, or reworded.
- Speaker IDs: display names in dialogueLines map to pack character IDs
  (Ly An -> NPC_LYAN, Ta Van Khanh -> NPC_TA_VAN_KHANH, Sam Chu Quy ->
  NPC_SAM_CHU_QUY, Ha Mac -> NPC_HA_MAC, Truong doan -> NPC_REFUGEE_LEADER,
  Tong Banh -> NPC_TONG_BANH, Doi truong tho lan -> NPC_DIVER_LEAD,
  Co Vo Tuong -> NPC_CO_VO_TUONG, Nguoi choi -> PLAYER). onscreen is true
  only when that ID is in the scene's pack character list; otherwise it is
  null (unknown), never false: the pack listing no characters (CIN_005,
  CIN_009, CIN_020), listing a different character (CIN_017 lists only
  BOSS_TIDE_SERPENT), or the player line in CIN_018 does not prove the
  speaker is off-screen, so this pack does not guess.
- DEC-MEDIA-P0 Q4 staging (cinematic-only, no persistent-ID duplication, no
  spawn move) is carried on every scene listing NPC_HA_MAC or
  NPC_SAM_CHU_QUY (CIN_010, CIN_011, CIN_012, CIN_016). Q2 (Ly An voice
  off-screen) was decided for CIN_004 only and is NOT generalised here.
- Stems: only the manifest-bound stinger is listed per scene, status
  CANDIDATE_POOL_NOT_LOCKED. No ambience/music stem is assigned: the
  measured P0 stem pool contains no per-scene ambience for these scenes,
  and none is invented.
- SRT: UTF-8, NFC, canonical dialogue only, one cue per line, in the same
  format as the P0/CIN_006 SRT drafts. SRT status is DRAFT until the
  proposed windows are director/Codex-confirmed.
"""
import json, hashlib, unicodedata, os

ROOT = os.path.expanduser('~/workspace/projects/ngumach-media02')
DONE = {'CIN_001', 'CIN_002', 'CIN_004', 'CIN_006'}

SPEAKER_IDS = {
    'Ly An': 'NPC_LYAN',
    'Tạ Vân Khanh': 'NPC_TA_VAN_KHANH',
    'Sầm Chủ Quỹ': 'NPC_SAM_CHU_QUY',
    'Hạ Mặc': 'NPC_HA_MAC',
    'Trưởng đoàn': 'NPC_REFUGEE_LEADER',
    'Tống Bành': 'NPC_TONG_BANH',
    'Đội trưởng thợ lặn': 'NPC_DIVER_LEAD',
    'Cơ Vô Tướng': 'NPC_CO_VO_TUONG',
    'Người chơi': 'PLAYER',
    'Người nhận thư': None,
}

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def srt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

pack = json.load(open(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'))
audio = json.load(open(f'{ROOT}/Client/Assets/AudioManifests/game_audio_v1.json'))
assert len(pack['scenes']) == 20
assert sum(s['durationSeconds'] for s in pack['scenes']) == 378
assert sum(len(s['shots']) for s in pack['scenes']) == 63
cin_bind = {b['sceneId']: b for b in audio['bindings']['cinema']}
assert len(cin_bind) == 20

scenes_out = []
for scene in pack['scenes']:
    sid = scene['sceneId']
    if sid in DONE:
        continue
    assert scene['durationSeconds'] == 18 and len(scene['shots']) == 3
    assert all(sh['durationSeconds'] == 6 for sh in scene['shots'])
    assert scene['playback'] == 'OPTIONAL_SKIP_SAFE_LAYER'
    bind = cin_bind[sid]
    assert bind['stinger'] == 'SFX/CINEMA/reveal'
    assert bind['timelineState'] == 'REQUIRES_PICTURE_LOCK_NOT_SYNCED'

    lines = []
    for raw in scene['dialogueLines']:
        speaker, text = raw.split(': ', 1)
        lines.append({'speakerDisplay': speaker,
                      'speakerId': SPEAKER_IDS[speaker],
                      'text': unicodedata.normalize('NFC', text)})
    assert lines, sid

    # Windows per the stated rule.
    if len(lines) == 1:
        if sid == 'CIN_011':
            windows = [(12.2, 17.8, True)]
        else:
            windows = [(12.5, 17.5, False)]
        cue_shots = ['CIN_%s_S03' % sid[4:]]
    elif sid == 'CIN_018' and len(lines) == 2:
        windows = [(6.5, 11.5, False), (12.5, 17.5, False)]
        cue_shots = ['CIN_018_S02', 'CIN_018_S03']
    else:
        raise AssertionError('unexpected dialogue shape: %s %d lines' % (sid, len(lines)))

    cues = []
    for (line, (w0, w1, widened), shot_id) in zip(lines, windows, cue_shots):
        dur = round(w1 - w0, 1)
        cps = round(len(line['text']) / dur, 2)
        assert cps <= 17, (sid, cps)
        # Short lines read slower than the 12-17 guide; that is fine and is
        # reported, not hidden: the window is kept uniform so VO can breathe.
        # Only a rate ABOVE 17 would force a widening (see CIN_011).
        cues.append({'shotId': shot_id, 'speakerDisplay': line['speakerDisplay'],
                     'speakerId': line['speakerId'], 'text': line['text'],
                     'windowSeconds': [w0, w1], 'charsPerSecond': cps,
                     'widenedForRate': widened,
                     'status': 'PROPOSED_ANIMATIC_PLACEMENT'})

    shots_out = []
    offset = 0.0
    for sh in scene['shots']:
        entry = {'shotId': sh['shotId'], 'startSeconds': offset,
                 'endSeconds': offset + sh['durationSeconds'],
                 'camera': sh['camera'],
                 'referenceRequirement': sh['referenceRequirement']}
        for cue in cues:
            if cue['shotId'] == sh['shotId']:
                entry['dialogue'] = {
                    'speaker': cue['speakerId'],
                    'speakerDisplay': cue['speakerDisplay'],
                    'onscreen': (True if cue['speakerId'] in scene['characters']
                                 else None),
                    'windowSeconds': cue['windowSeconds'],
                    'status': 'PROPOSED_ANIMATIC_PLACEMENT',
                    'text': cue['text']}
        shots_out.append(entry)
        offset += sh['durationSeconds']

    cinematic_only = bool(set(scene['characters']) &
                          {'NPC_HA_MAC', 'NPC_SAM_CHU_QUY'})
    timing = {
        'sceneId': sid, 'questId': scene['questId'], 'title': scene['title'],
        'durationSeconds': 18, 'playback': scene['playback'],
        'runtimeActivation': scene['runtimeActivation'],
        'revealTier': bind['revealTier'],
        'charactersOnScreen': scene['characters'],
        'staging': ('CINEMATIC_ONLY_NO_PERSISTENT_ID_DUPLICATION_NO_SPAWN_MOVE'
                    if cinematic_only else 'PACK_CHARACTERS_AS_LISTED_NO_SPAWN_CLAIM'),
        'stagingNote': ('DEC-MEDIA-P0 Q4: cinematic-only staging; duplicates no '
                        'persistent NPC ID and moves no default spawn.'
                        if cinematic_only else
                        'No staging claim beyond the pack character list; '
                        'no persistent ID is duplicated and no spawn is moved.'),
        'audioDirection': scene['audioDirection'],
        'candidateStems': ['SFX/CINEMA/reveal'],
        'stemStatus': 'CANDIDATE_POOL_NOT_LOCKED',
        'stemNote': ('Only the manifest-bound stinger is listed. No per-scene '
                     'ambience/music stem is assigned for this scene; none is '
                     'invented from the P0 stem pool.'),
        'fallback': scene['fallback'],
        'dialogueWindowStatus': 'PROPOSED_ANIMATIC_PLACEMENT',
        'dialogueWindowNote': ('Pack assigns no shot/timecode to these lines. '
                               'Windows follow the uniform campaign rule in '
                               'build_campaign_timing.py; director/Codex '
                               'confirmation required before SRT final.'),
        'shots': shots_out,
    }

    outdir = f'{ROOT}/Implementation/Content/Narrative/Deliveries/{sid}'
    os.makedirs(outdir, exist_ok=True)
    tpath = f'{outdir}/{sid}_timing_v1.json'
    json.dump(timing, open(tpath, 'w'), ensure_ascii=False, indent=2)
    blocks = []
    for i, cue in enumerate(cues, 1):
        w0, w1 = cue['windowSeconds']
        blocks.append(f"{i}\n{srt_time(w0)} --> {srt_time(w1)}\n{cue['text']}")
    spath = f'{outdir}/{sid}_vi.srt'
    open(spath, 'w', encoding='utf-8').write(
        unicodedata.normalize('NFC', '\n\n'.join(blocks) + '\n'))

    scenes_out.append({
        'sceneId': sid, 'questId': scene['questId'], 'title': scene['title'],
        'revealTier': bind['revealTier'], 'durationSeconds': 18, 'shots': 3,
        'timingFile': f'Implementation/Content/Narrative/Deliveries/{sid}/{sid}_timing_v1.json',
        'srtFile': f'Implementation/Content/Narrative/Deliveries/{sid}/{sid}_vi.srt',
        'srtSha256': sha(spath), 'srtStatus': 'DRAFT',
        'dialogueWindowStatus': 'PROPOSED_ANIMATIC_PLACEMENT',
        'cues': [{'speakerDisplay': c['speakerDisplay'], 'speakerId': c['speakerId'],
                  'shotId': c['shotId'], 'windowSeconds': c['windowSeconds'],
                  'chars': len(c['text']), 'charsPerSecond': c['charsPerSecond'],
                  'widenedForRate': c['widenedForRate']} for c in cues],
        'staging': timing['staging'],
    })

assert len(scenes_out) == 16
assert sum(s['durationSeconds'] for s in scenes_out) == 288
assert sum(s['shots'] for s in scenes_out) == 48
assert sum(len(s['cues']) for s in scenes_out) == 17  # CIN_018 has 2

manifest = {
    'schemaVersion': 1,
    'checkpoint': 'MEDIA-02 checkpoint 06 - M3 campaign timing pack (16 scenes)',
    'decisionId': 'DEC-MEDIA-P0-20261105',
    'branch': 'muse/media-production-20261104',
    'campaignTotals': {'scenesDeliveredHere': 16, 'shots': 48,
                       'durationSeconds': 288, 'dialogueCues': 17,
                       'fullCampaign': {'scenes': 20, 'shots': 63,
                                        'durationSeconds': 378},
                       'previouslyDelivered': ['CIN_001', 'CIN_002', 'CIN_004',
                                               'CIN_006'],
                       'previouslyDeliveredSeconds': 90},
    'placementRule': ('Single line -> S03 12.5-17.5s. CIN_011 widened to '
                      '12.2-17.8s for rate. CIN_018 split S02 6.5-11.5s + S03 '
                      '12.5-17.5s. All windows PROPOSED_ANIMATIC_PLACEMENT.'),
    'sourceHashes': {
        'Cinema_Production_Pack_v1.json': sha(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'),
        'game_audio_v1.json': sha(f'{ROOT}/Client/Assets/AudioManifests/game_audio_v1.json'),
    },
    'scenes': scenes_out,
}
mpath = (f'{ROOT}/Implementation/Content/Narrative/Deliveries/'
         'CAMPAIGN_timing_manifest_v1.json')
json.dump(manifest, open(mpath, 'w'), ensure_ascii=False, indent=2)
print('scenes', len(scenes_out), 'shots 48', 'seconds 288', 'cues 17')
for s in scenes_out:
    for c in s['cues']:
        print(s['sceneId'], c['shotId'], c['windowSeconds'], c['chars'],
              c['charsPerSecond'], 'widened' if c['widenedForRate'] else '')
