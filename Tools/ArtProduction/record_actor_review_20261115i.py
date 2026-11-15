"""Serialize I manual observations after original/native/directional inspection."""
import hashlib,json,re,subprocess
from inspect_actor_library import ART,ROOT,binding_sha256
BATCH='20261115i';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
FFMPEG='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json')
    assert len(review['sourceApprovals'])==365 and review['sourceApprovals']==baseline['approvedSourcePins'],'Already applied or baseline changed'
    working=read(EV/'manual_review_working.json');assert not working['manualReviewComplete'] and working['individualNativeSourcesInspected']==25 and working['actualLoopWrapsInspected']==10
    direction=read(EV/'eight_facing_manual_review.json');assert direction['manualReviewComplete'] is True and direction['batch']==BATCH
    observed={e['id']:e for e in working['entries']};comparisons={e['clip']:e for e in direction['entries']}
    assert set(comparisons)=={'idle','walk','basic_attack','hurt','death'}
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')==BATCH];assert len(records)==25
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==25 and media['sourceFramesMeasured']==400
    pages={p['id']:p for p in read(ART/'structure_report.json')['pages']};decoded=[]
    for clip,c in comparisons.items():
        assert c['allEightFacingsInspected'] and c['temporalSamplesInspected'] and c['visualNotes']
        for f,digest in c['evidenceSha256'].items():assert sha(ROOT/f)==digest
        movie=EV/(clip+'_eight_angles.mp4')
        result=subprocess.run([FFMPEG,'-v','error','-i',str(movie),'-map','0:v:0','-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
        assert not result.stderr.strip() and int(re.findall(r'^frame=(\d+)$',result.stdout,re.M)[-1])==180
        assert not re.search(r'^ERROR:',(EV/(clip+'_eight_angles.godot.log')).read_text(encoding='utf-8-sig'),re.M)
        decoded.append(dict(file=movie.name,sha256=sha(movie),decodedFrames=180,decodedWithoutDiagnostics=True))
    entries=[]
    for r in records:
        ident=r['id'];p=pages[ident];o=observed[ident];clip=r['clip'] if 'clip' in r else ident.removeprefix('class_huyen_but_').rsplit('_',1)[0]
        assert o['nativePoseFramesInspected']==16 and o['originalAtlasViewed'] and o['sourceSha256']==sha(ART/r['source'])==p['sha256']
        assert binding_sha256(p)==p['bindingSha256']
        for f,digest in o['nativeEvidenceSha256'].items():assert sha(ROOT/f)==digest
        files=list(o['nativeEvidenceSha256'])+list(comparisons[clip]['evidenceSha256'])
        held=o['status'].startswith('HOLD');assert held==(clip=='walk'),'Unexpected manual disposition; review before editing gate'
        notes=o['visualNotes']+' '+comparisons[clip]['visualNotes']+' Source clip review only; cross-action transitions, world travel/collision, final skill events and live60FPS remain unaccepted.'
        entries.append(dict(id=ident,sourceSheet=(ART/r['source']).relative_to(ROOT).as_posix(),sourceSha256=p['sha256'],bindingSha256=p['bindingSha256'],productionApproved=not held,nativeReviewed=True,reviewedSourceFrames=16,visualNotes=notes,nativeEvidence=files,nativeEvidenceSha256={f:sha(ROOT/f) for f in files}))
    save(EV/'manual_pose_observations.json',working)
    ledger=dict(batch=BATCH,manualReviewComplete=True,reviewDate='2026-11-16',reviewScale='ORIGINAL_16_NATIVE_PHASES_8_FACINGS_AND_REAL_LOOP_WRAPS',scope='SOURCE_VISUAL_CLIP_REVIEW_NOT_CLASS_OR_GAMEPLAY_ACCEPTANCE',entries=entries)
    save(EV/'source_native_review.json',ledger);save(EV/'manual_review_working.json',ledger)
    save(EV/'catalogue_media_audit.json',dict(selectedVideos=5,files=decoded,scope='EIGHT_FACING_SOURCE_COMPARISON_NOT_GAMEPLAY_FPS'))
    print(json.dumps(dict(selected=25,sourceApprovalsPrepared=20,sourceHoldsPrepared=5,nativeVideos=30,priorPins=365,applied=False)))
if __name__=='__main__':record()
