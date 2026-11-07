"""MEDIA-02 checkpoint 05: CIN_006 (P1) timing + SRT draft.

Sources (read, not invented):
- Implementation/Content/Narrative/Cinema_Production_Pack_v1.json, scene CIN_006
  (C1-06, 18s, 3 shots x 6s, canonical dialogueLine, playback, fallback).
- docs/narrative/workshop/MUSE_THANG_LONG_CIN006_DIRECTION_vi.md
  (alternate take text; does NOT replace canonical dialogue).
- DEC-MEDIA-P0-20261105 Q3/Q4 (via media_p0_decisions_20261105.json):
  Q3 alternate take keeps its own takeId/version; Q4 Ha Mac / Sam are
  cinematic-only staging, no persistent-ID duplication, no spawn move.
- Client/Assets/AudioManifests/game_audio_v1.json bindings.cinema for CIN_006
  (stinger SFX/CINEMA/reveal, REQUIRES_PICTURE_LOCK_NOT_SYNCED).

Status honesty: the pack assigns NO shot/timecode to the dialogue line, so
the S03 window below is PROPOSED_ANIMATIC_PLACEMENT (same convention as
CIN_002/CIN_004 in checkpoint 01), not canonical. The alternate take gets
no window until an animatic lock chooses it. SRT carries canonical only.
No market ambience stem is claimed: the measured P0 stem pool contains no
Thang Long market loop, so candidateStems lists only the manifest-bound
stinger and stemStatus stays CANDIDATE_POOL_NOT_LOCKED.
"""
import json, hashlib, unicodedata, os

ROOT = os.path.expanduser('~/workspace/projects/ngumach-media02')

def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()

def srt_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    if ms == 1000:
        s += 1; ms = 0
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

pack = json.load(open(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'))
scene = next(s for s in pack['scenes'] if s['sceneId'] == 'CIN_006')
assert scene['durationSeconds'] == 18 and len(scene['shots']) == 3
assert all(sh['durationSeconds'] == 6 for sh in scene['shots'])

canon_line = scene['dialogueLines'][0]
assert canon_line.startswith('Hạ Mặc: ')
canon_text = unicodedata.normalize('NFC', canon_line.split(': ', 1)[1])
alt_text = unicodedata.normalize('NFC', 'Tới đây ta theo được. Chỗ trống này giữ nguyên.')

# Proposed window inside S03 (12.0-18.0): 0.5s headroom each side.
W_START, W_END = 12.5, 17.5
cps = round(len(canon_text) / (W_END - W_START), 2)
assert 12 <= cps <= 17, cps

offset = 0.0
shots_out = []
for sh in scene['shots']:
    entry = {'shotId': sh['shotId'], 'startSeconds': offset,
             'endSeconds': offset + sh['durationSeconds'], 'camera': sh['camera'],
             'referenceRequirement': sh['referenceRequirement']}
    if sh['shotId'] == 'CIN_006_S03':
        entry['dialogue'] = {'speaker': 'NPC_HA_MAC', 'onscreen': True,
                             'windowSeconds': [W_START, W_END],
                             'status': 'PROPOSED_ANIMATIC_PLACEMENT',
                             'text': canon_text}
    shots_out.append(entry)
    offset += sh['durationSeconds']

timing = {
    'sceneId': 'CIN_006', 'questId': scene['questId'], 'title': scene['title'],
    'durationSeconds': 18, 'playback': scene['playback'],
    'runtimeActivation': scene['runtimeActivation'],
    'charactersOnScreen': scene['characters'],
    'staging': 'CINEMATIC_ONLY_NO_PERSISTENT_ID_DUPLICATION_NO_SPAWN_MOVE',
    'stagingNote': ('DEC-MEDIA-P0 Q4: NPC_HA_MAC / NPC_SAM_CHU_QUY are staged for '
                    'cinema only; this timing duplicates no persistent NPC ID and '
                    'moves no default spawn.'),
    'audioDirection': scene['audioDirection'],
    'candidateStems': ['SFX/CINEMA/reveal'],
    'stemStatus': 'CANDIDATE_POOL_NOT_LOCKED',
    'stemNote': ('Only the manifest-bound stinger is listed. No Thang Long market '
                 'ambience stem exists in the measured P0 stem pool; none is '
                 'assigned to this scene.'),
    'fallback': scene['fallback'],
    'alternateTake': {
        'takeId': 'CIN_006_ALT_T01', 'version': 'v1-alt',
        'status': 'ALTERNATE_TAKE_DOES_NOT_REPLACE_CANONICAL',
        'text': alt_text, 'windowSeconds': None,
        'note': ('DEC-MEDIA-P0 Q3: kept under its own takeId/version. It is NOT '
                 'in the SRT. If an animatic lock ever chooses it, assign it a '
                 'labelled window then; never merge both takes into one line.'),
        'source': 'docs/narrative/workshop/MUSE_THANG_LONG_CIN006_DIRECTION_vi.md',
    },
    'shots': shots_out,
}

outdir = f'{ROOT}/Implementation/Content/Narrative/Deliveries/CIN_006'
os.makedirs(outdir, exist_ok=True)
tpath = f'{outdir}/CIN_006_timing_v1.json'
json.dump(timing, open(tpath, 'w'), ensure_ascii=False, indent=2)
srt = unicodedata.normalize(
    'NFC', f"1\n{srt_time(W_START)} --> {srt_time(W_END)}\n{canon_text}\n")
spath = f'{outdir}/CIN_006_vi.srt'
open(spath, 'w', encoding='utf-8').write(srt)

manifest = {
    'schemaVersion': 1,
    'checkpoint': 'MEDIA-02 checkpoint 05 - CIN_006 (P1) timing + SRT draft',
    'decisionId': 'DEC-MEDIA-P0-20261105',
    'branch': 'muse/media-production-20261104',
    'sourceHashes': {
        'Cinema_Production_Pack_v1.json': sha(f'{ROOT}/Implementation/Content/Narrative/Cinema_Production_Pack_v1.json'),
        'MUSE_THANG_LONG_CIN006_DIRECTION_vi.md': sha(f'{ROOT}/docs/narrative/workshop/MUSE_THANG_LONG_CIN006_DIRECTION_vi.md'),
        'game_audio_v1.json': sha(f'{ROOT}/Client/Assets/AudioManifests/game_audio_v1.json'),
    },
    'scene': {'sceneId': 'CIN_006', 'durationSeconds': 18, 'shots': 3,
              'timingFile': 'Implementation/Content/Narrative/Deliveries/CIN_006/CIN_006_timing_v1.json',
              'srtFile': 'Implementation/Content/Narrative/Deliveries/CIN_006/CIN_006_vi.srt',
              'srtSha256': sha(spath),
              'srtStatus': 'DRAFT',
              'dialogueWindowStatus': 'PROPOSED_ANIMATIC_PLACEMENT',
              'canonicalChars': len(canon_text),
              'charsPerSecond': cps,
              'alternateTakeId': 'CIN_006_ALT_T01',
              'alternateTakeInSrt': False},
}
mpath = f'{outdir}/CIN_006_timing_manifest_v1.json'
json.dump(manifest, open(mpath, 'w'), ensure_ascii=False, indent=2)
print('canon chars', len(canon_text), 'cps', cps)
print('timing', tpath)
print('srt', spath)
print('manifest', mpath)
