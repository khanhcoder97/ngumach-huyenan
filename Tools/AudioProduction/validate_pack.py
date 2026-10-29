"""Decode and inspect real audio, source hashes and explicit reuse. Not an ear/engine test."""
import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
import numpy as np
import soundfile as sf
from catalog import ROOT, BASE, build_bindings
from dsp import SR, metrics
from codec import decode


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def source_sha(path):
    # Sources were authored as UTF-8/LF. Git autocrlf may materialize CRLF on
    # Windows; canonicalize text only. Runtime audio/master hashes stay binary.
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def inside(root,raw,prefix):
    if not isinstance(raw,str) or '\\' in raw or ':' in raw or PurePosixPath(raw).is_absolute() or '..' in PurePosixPath(raw).parts:
        raise ValueError('unsafe relative path: '+str(raw))
    if not raw.startswith(prefix+'/'): raise ValueError('path outside '+prefix+': '+raw)
    p=(root/raw).resolve();p.relative_to(root.resolve())
    if not p.is_file():raise ValueError('missing file: '+raw)
    with p.open('rb') as f:head=f.read(100)
    if head.startswith(b'version https://git-lfs.github.com/spec/v1'):raise ValueError('Git LFS pointer, run git lfs pull: '+raw)
    return p


def check_clip(root,clip,loop,*,require_meta=True):
    errors=[];pcm_digest=None;measured=None
    try:
        p=inside(root,clip['path'],'Client/Assets/Audio/PackV1')
        if sha(p)!=clip['sha256']: errors.append('runtime hash mismatch')
        info=sf.info(p);x,rate=decode(p)
        if rate!=SR or info.frames!=clip['frames'] or info.channels!=clip['channels']: errors.append('rate/frame/channel mismatch')
        if len(x)<SR*.04 or len(x)>SR*90:errors.append('unexpected duration')
        if loop and (info.channels!=2 or info.format!='OGG' or info.subtype!='VORBIS'):errors.append('loop must be stereo OGG/Vorbis')
        if not loop and (info.channels!=1 or info.format!='WAV' or info.subtype!='PCM_16'):errors.append('one-shot must be mono WAV16')
        if not np.isfinite(x).all():errors.append('non-finite samples')
        measured=metrics(x)
        if measured['peak']>.95:errors.append('clipping/headroom failure')
        if measured['rmsDb']< -70:errors.append('silent/near-silent clip')
        if measured['dc']>.0015:errors.append('DC offset')
        if not loop and measured['firstLastPeak']>.002:errors.append('hard one-shot boundary')
        if loop and measured['seamRelativeToInterior995']>2:errors.append('loop boundary exceeds normal interior transitions')
        pcm_digest=hashlib.sha256(np.rint(x*32767).astype('<i2').tobytes()).hexdigest()
        if require_meta:
            mp=Path(str(p)+'.meta')
            text=mp.read_text(encoding='utf-8-sig')
            if not re.search(r'^guid: [0-9a-f]{32}$',text,re.MULTILINE) or 'AudioImporter:' not in text:errors.append('invalid AudioImporter meta')
            if f'loadType: {2 if loop else 0}' not in text:errors.append('static import loadType does not match streaming/one-shot policy')
        if clip.get('masterPath'):
            source=inside(root,clip['masterPath'],'Art_Source/Audio/Masters')
            if sha(source)!=clip['masterSha256']: errors.append('master hash mismatch')
            mi=sf.info(source)
            if mi.format!='FLAC' or mi.subtype!='PCM_24' or mi.frames!=info.frames or mi.channels!=info.channels or mi.samplerate!=SR:
                errors.append('lossless24 master geometry mismatch')
    except (ValueError,KeyError,OSError,sf.SoundFileError) as exc:
        errors.append(str(exc))
    return errors,measured,pcm_digest


def validate(root,manifest):
    issues=[];results=[];keys=set();paths=set();guids=set()
    baseline=json.loads((root/BASE.relative_to(ROOT)).read_text(encoding='utf-8-sig'))
    baseline_keys={c['cueKey'] for c in baseline['cues']}
    for c in manifest['cues']:
        key=c['cueKey']
        if key in keys:issues.append(key+': duplicate cueKey')
        keys.add(key)
        if c['assetState']!='RENDERED_CANDIDATE' or c['engineImport']!='UNVERIFIED' or c['artReview']!='LISTENING_REVIEW_PENDING':
            issues.append(key+': do not claim listening/engine approval from render')
        if c.get('sourceLicense')!='original_procedural_synthesis_no_external_samples':issues.append(key+': unknown provenance')
        if len(c['clips'])!=(1 if c['loop'] else 3):issues.append(key+': variation count')
        cue_pcm=[]
        for clip in c['clips']:
            p=clip['path']
            if p in paths:issues.append(p+': duplicate path')
            paths.add(p)
            err,m,pcm=check_clip(root,clip,c['loop'])
            issues.extend(p+': '+e for e in err)
            if pcm:cue_pcm.append(pcm)
            if m:results.append(dict(path=p,**m))
            meta_path=root/(p+'.meta')
            if meta_path.exists():
                match=re.search(r'^guid: (\w+)',meta_path.read_text(),re.MULTILINE)
                if match:
                    if match[1] in guids:issues.append(p+': duplicate GUID')
                    guids.add(match[1])
        if len(cue_pcm)!=len(set(cue_pcm)):issues.append(key+': identical decoded variations')
    if not baseline_keys<=keys:issues.append('missing core63 cues: '+str(sorted(baseline_keys-keys)))
    expected=build_bindings(manifest['cues'])
    if manifest['bindings']!=expected:issues.append('canonical bindings changed or incomplete')
    for group in ('skills','monsters','bosses','maps','npcs','companions','cinema'):
        if not manifest['bindings'].get(group):issues.append('empty bindings '+group)
    for source in manifest['sources']:
        try:
            prefix='Tools/AudioProduction' if source['path'].startswith('Tools/AudioProduction/') else 'Art_Source/Audio'
            p=inside(root,source['path'],prefix)
            if source_sha(p)!=source['sha256']:issues.append(source['path']+': source hash mismatch')
        except ValueError as exc:issues.append(str(exc))
    def refs(value):
        if isinstance(value,dict):
            for v in value.values():yield from refs(v)
        elif isinstance(value,list):
            for v in value:yield from refs(v)
        elif isinstance(value,str) and value.startswith(('SFX/','MUSIC/','AMBIENCE/')):yield value
    missing_refs=set(refs(manifest['bindings']))-keys
    if missing_refs:issues.append('dangling cue bindings: '+str(sorted(missing_refs)))
    actual={p.relative_to(root).as_posix() for p in (root/'Client/Assets/Audio/PackV1').rglob('*') if p.suffix in ('.wav','.ogg')}
    if actual!=paths:issues.append('orphan/missing runtime audio files: '+str(sorted(actual^paths)))
    summary=dict(status='FAIL' if issues else 'PASS_TECHNICAL_AUDIO_NOT_LISTENING_OR_ENGINE_APPROVAL',
        cues=len(keys),runtimeClips=len(paths),coreCueCoverage=len(baseline_keys&keys),
        musicLoops=sum(c['bus']=='Music' for c in manifest['cues']),ambienceLoops=sum(c['bus']=='Ambience' for c in manifest['cues']),
        bindings={k:len(v) for k,v in manifest['bindings'].items()},maxDecodedPeak=max((r['peak'] for r in results),default=0),
        maxDcOffset=max((r['dc'] for r in results),default=0),maxLoopBoundaryRatio=max((r['seamRelativeToInterior995'] for r in results if r['path'].endswith('.ogg')),default=0),
        manifestSha256=sha(root/'Client/Assets/AudioManifests/game_audio_v1.json'),issues=issues,
        exclusions=['Subjective listening review','Actual Unity import/playback/mixer/device QA','Spoken NPC dialogue and picture-locked cinema edit'])
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--report',default='');args=p.parse_args()
    path=ROOT/'Client/Assets/AudioManifests/game_audio_v1.json'
    manifest=json.loads(path.read_text(encoding='utf-8-sig'))
    report=validate(ROOT,manifest)
    if args.report:
        out=ROOT/args.report;out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 1 if report['issues'] else 0


if __name__=='__main__':raise SystemExit(main())
