"""Render actual game audio, original scores, loop masters and an audition gallery."""
import argparse
import hashlib
import json
import platform
import subprocess
import uuid
from pathlib import Path
import numpy as np
import soundfile as sf

from catalog import ROOT, MUSIC, build_catalog, build_bindings
from dsp import SR, master, metrics, render_sfx, render_music, render_score, render_ambience, seed_for
from codec import write_encoded,decode

PACK = ROOT/'Client/Assets/Audio/PackV1'
MANIFEST = ROOT/'Client/Assets/AudioManifests/game_audio_v1.json'
SOURCE = ROOT/'Art_Source/Audio'


def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(path): return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def rel(path): return path.relative_to(ROOT).as_posix()


def meta(path, *, audio=False, loop=False, mono=False):
    target=Path(str(path)+'.meta')
    if target.exists(): return
    guid=uuid.uuid5(uuid.NAMESPACE_URL,'ngumach/original-audio/'+rel(path)).hex
    header=f'fileFormatVersion: 2\nguid: {guid}\n'
    if path.is_dir():
        body='folderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    elif audio:
        body=f'''AudioImporter:
  externalObjects: {{}}
  serializedVersion: 7
  defaultSettings:
    serializedVersion: 2
    loadType: {2 if loop else 0}
    sampleRateSetting: 0
    sampleRateOverride: 48000
    compressionFormat: {1 if loop else 0}
    quality: 0.7
    conversionMode: 0
    preloadAudioData: {0 if loop else 1}
  platformSettingOverrides: {{}}
  forceToMono: {1 if mono else 0}
  normalize: 0
  loadInBackground: 1
  ambisonic: 0
  3D: 1
  userData: NGM_AUDIO_V1_CANDIDATE_ENGINE_UNVERIFIED
  assetBundleName:
  assetBundleVariant:
'''
    else:
        body='TextScriptImporter:\n  externalObjects: {}\n  userData:\n  assetBundleName:\n  assetBundleVariant:\n'
    target.write_text(header+body,encoding='utf-8')


def write_clip(cue,index,data):
    loop=cue['loop']; mono=data.shape[1]==1
    suffix='' if loop else f'_v{index+1:02}'
    leaf=Path(cue['cueKey'].lower()+suffix)
    runtime=PACK/leaf.with_suffix('.ogg' if loop else '.wav')
    original=SOURCE/'Masters'/leaf.with_suffix('.flac')
    runtime.parent.mkdir(parents=True,exist_ok=True); original.parent.mkdir(parents=True,exist_ok=True)
    # Lossless editable 24-bit master, short 16-bit runtime WAV and streaming Vorbis loops.
    write_encoded(original,data,SR,format='FLAC',subtype='PCM_24')
    write_encoded(runtime,data,SR,format='OGG' if loop else 'WAV',subtype='VORBIS' if loop else 'PCM_16')
    decoded,rate=decode(runtime)
    if rate!=SR or len(decoded)!=len(data): raise ValueError('Encoded duration mismatch: '+str(runtime))
    meta(runtime,audio=True,loop=loop,mono=mono)
    return dict(variantId=f'v{index+1:02}',path=rel(runtime),sha256=digest(runtime),bytes=runtime.stat().st_size,
        masterPath=rel(original),masterSha256=digest(original),sampleRate=SR,channels=data.shape[1],
        frames=len(data),durationSeconds=round(len(data)/SR,6),format='OGG_VORBIS' if loop else 'WAV_PCM_16',
        loopStartFrame=0 if loop else None,loopEndFrame=len(data) if loop else None,
        seed=seed_for(cue['cueKey'].lower()+f'/{index}'),measurements=metrics(decoded))


def preview(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=master(data,loop=False,bus='Music')
    try:
        write_encoded(path,data,SR,format='MP3',bitrate_mode='VARIABLE',compression_level=.45)
        if sf.info(path).frames<100: raise ValueError('Empty MP3')
    except (RuntimeError,ValueError,sf.SoundFileError):
        path=path.with_suffix('.wav');write_encoded(path,data,SR,format='WAV',subtype='PCM_16')
    return rel(path)


def montage(items,path):
    clips=[]; timeline=[]; cursor=0
    for label,clip in items:
        x,_=decode(ROOT/clip['path'])
        if x.shape[1]==1: x=np.repeat(x,2,axis=1)
        x=x[:round(min(3,len(x)/SR)*SR)]
        gap=np.zeros((round(.38*SR),2),np.float32)
        timeline.append(dict(name=label,startSeconds=round(cursor/SR,3),sourcePath=clip['path']))
        clips.extend((x,gap));cursor+=len(x)+len(gap)
    out=preview(path,np.concatenate(clips))
    return dict(path=out,timeline=timeline)


def build_player(manifest):
    template=(ROOT/'Tools/AudioProduction/player_template.html').read_text(encoding='utf-8')
    data=json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    (ROOT/'Tools/AudioProduction/player.html').write_text(template.replace('__EMBEDDED_AUDIO_CATALOG__',data),encoding='utf-8')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--recompose',action='store_true',help='Explicitly replace score JSON from authored motifs; default preserves edited scores')
    ap.add_argument('--only',default='',help='Render a cueKey prefix for an audition; does not publish a full manifest')
    args=ap.parse_args()
    cues,baseline=build_catalog()
    recipes=SOURCE/'game_audio_recipes_v1.json'
    if recipes.exists():
        cues=json.loads(recipes.read_text(encoding='utf-8-sig'))['cues']
    else:
        dump(recipes,dict(version=1,description='Editable original DSP recipes; no sampled audio input',cues=cues))
    selected=[c for c in cues if not args.only or c['cueKey'].startswith(args.only)]
    for number,c in enumerate(selected,1):
        records=[]
        for variant in range(c['renderVariants']):
            if c['synthFamily']=='music':
                key=c['cueKey'].split('/')[-1]; score_path=SOURCE/'Scores'/(key+'.json')
                if score_path.exists() and not args.recompose:
                    score=json.loads(score_path.read_text(encoding='utf-8-sig')); signal=render_score(key,score)
                else:
                    signal,score=render_music(key,MUSIC[key]);dump(score_path,score)
            elif c['synthFamily']=='ambience': signal=render_ambience(c['cueKey'].split('/')[-1])
            else: signal=render_sfx(c,variant)
            data=master(signal,loop=c['loop'],bus=c['bus'])
            records.append(write_clip(c,variant,data))
        c['clips']=records;c['clipPath']=records[0]['path'];c['assetState']='RENDERED_CANDIDATE'
        c['artReview']='LISTENING_REVIEW_PENDING';c['engineImport']='UNVERIFIED';c['runtimeIntegration']='NOT_CONNECTED'
        print(f"[{number}/{len(selected)}] {c['cueKey']} -> {len(records)} clip(s)",flush=True)
    if args.only:
        print('Audition subset rendered; full catalog was not published.');return
    bindings=build_bindings(cues)
    lookup={c['cueKey']:c for c in cues}
    showcases=[]
    skills=[]
    for cls in ('MK','AD','HB','TC','LC'):
        for slot in (1,6):
            c=next(c for c in cues if c.get('skillId')==f'SK-{cls}-{slot:02}')
            skills.append((c['nameVi'],c['clips'][0]))
    showcases.append(montage(skills,SOURCE/'Previews/01_five_class_skills.mp3'))
    keys=['SFX/BOSS/mang_cot_sweep_warning','SFX/BOSS/mang_cot_emerge_warning','SFX/BOSS/mang_cot_bubble_warning',
        'SFX/MONSTER/aquatic_attack','SFX/MONSTER/construct_attack','SFX/MONSTER/roots_hurt','SFX/FORGE/upgrade_success',
        'SFX/UI/mail_received','SFX/TRADE/complete','SFX/LIFE/fishing_success']
    showcases.append(montage([(lookup[k]['nameVi'],lookup[k]['clips'][0]) for k in keys],SOURCE/'Previews/02_boss_world_services.mp3'))
    for key in ('thang_long','ben_mua'):
        clip=lookup['MUSIC/'+key]['clips'][0];data,_=decode(ROOT/clip['path'])
        showcases.append(dict(path=preview(SOURCE/'Previews'/('music_'+key+'.mp3'),data),timeline=[dict(name=MUSIC[key]['title'],startSeconds=0)]))
    source_paths=[recipes,*sorted((SOURCE/'Scores').glob('*.json')),
        *(ROOT/'Tools/AudioProduction'/f for f in ('catalog.py','dsp.py','codec.py','render_pack.py','requirements.txt'))]
    manifest=dict(schemaVersion=1,packId='NGM_ORIGINAL_AUDIO_V1',state='ASSETS_CREATED_NOT_RUNTIME_CONNECTED',
        owner='Codex',originality='Original DSP and original scores; no external audio samples, no voice cloning',
        sourceGitBase=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        sourceAuthority='Source file hashes below include newly authored files, not an assertion that the base commit contains the renderer',
        sourceHashMode='SHA256_UTF8_LF_CANONICAL_TEXT_BINARY_AUDIO_UNCHANGED',
        environment=dict(python=platform.python_version(),numpy=np.__version__,soundfile=sf.__version__,libsndfile=sf.__libsndfile_version__),
        voiceCaps=baseline['voiceCaps'],dedupeKey=baseline['dedupeKey'],warningDucking=baseline['warningDucking'],
        cues=cues,bindings=bindings,showcases=showcases,
        sources=[dict(path=rel(p),sha256=source_digest(p)) for p in source_paths],
        scopeExclusions=['Spoken NPC dialogue/voice acting','Picture-locked cinema sound edit','Unity/device mixing verification'])
    dump(MANIFEST,manifest);meta(MANIFEST)
    for p in sorted((ROOT/'Client/Assets/Audio').rglob('*')):
        if p.is_dir():meta(p)
    meta(ROOT/'Client/Assets/Audio');meta(ROOT/'Client/Assets/AudioManifests')
    build_player(manifest)
    clips=[v for c in cues for v in c['clips']]
    print(json.dumps(dict(cues=len(cues),runtimeClips=len(clips),music=sum(c['bus']=='Music' for c in cues),
        ambience=sum(c['bus']=='Ambience' for c in cues),runtimeMB=round(sum(v['bytes'] for v in clips)/1048576,2),
        bindings={k:len(v) for k,v in bindings.items()}),ensure_ascii=False),flush=True)


if __name__=='__main__': main()
