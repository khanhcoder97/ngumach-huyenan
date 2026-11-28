"""Serialize completed original/native H observations, then use the common approval gate."""
import hashlib,json,re,subprocess
from pathlib import Path
from inspect_actor_library import ART,ROOT,binding_sha256
BATCH='20261115h';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
FFMPEG='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record():
    review=read(ART/'visual_review.json');assert len(review['sourceApprovals'])==362,'Already applied or baseline changed'
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')==BATCH];assert len(records)==3
    pages={p['id']:p for p in read(ART/'structure_report.json')['pages']};media=read(EV/'native_media_audit.json');assert media['selectedVideos']==3
    for clip in ('run','interact'):
        movie=EV/(clip+'_eight_angles.mp4')
        decoded=subprocess.run([FFMPEG,'-v','error','-i',str(movie),'-map','0:v:0','-f','null','-','-progress','pipe:1','-nostats'],capture_output=True,text=True,check=True)
        assert not decoded.stderr.strip() and int(re.findall(r'^frame=(\d+)$',decoded.stdout,re.M)[-1])==180
        media['files'].append(dict(file=movie.name,sha256=sha(movie),decodedFrames=180,decodedWithoutDiagnostics=True,scope='EIGHT_FACING_NATIVE_COMPARISON'))
    media.update(selectedVideos=5,failedImportTrials=2,scope='SOURCE_NATIVE_REVIEW_NOT_CLASS_ACCEPTANCE');save(EV/'native_media_audit.json',media)
    notes={
      'class_huyen_but_run_n':'PASS source N: inspected original,16native phases,actual14/15/0/1 wrap and eight-facing comparison after resource import. Opposite0/8 lower boots now separate; stable head-projected root,one right brush,empty left,no rear-view face. Full world movement/collision and action transitions unaccepted.',
      'class_huyen_but_run_e':'PASS v4 source E: inspected original/all16native phases plus regenerated actual14/15/0/1 wrap,eight-facing E/W comparison and temporal samples. Brush arm back at0,forward at8,returns by14/15; v4restores missing cream bristles/ferrule at12. One right brush/two arms retained,near/far boot silhouettes readable. Earlier v1/v2/v3errors archived. Source review does not certify world travel or stable live60FPS.',
      'class_huyen_but_interact_ne':'PASS source NE: inspected original/all16native phases plus NE/NW eight-facing and temporal comparison after import. Obsolete hanging far-hand removed during open-palm phases; right brush hand remains,far arm occludes naturally,no third hand. Clear rear-three-quarter back plane and stable root. Cross-action/style continuity and full dialogue gameplay unaccepted.'}
    entries=[]
    for r in records:
        ident=r['id'];p=pages[ident];assert sha(ART/r['source'])==p['sha256'] and binding_sha256(p)==p['bindingSha256']
        prefix='raw_'+ident;clip='interact' if '_interact_' in ident else 'run'
        files=[EV/(prefix+s) for s in ('.mp4','.png','_poses.png','_samples.png','_source_samples.png')]
        files += [EV/(clip+'_eight_angles'+s) for s in ('.mp4','.png','_samples.png')]
        if (EV/(prefix+'_loop_seam.png')).exists():files.append(EV/(prefix+'_loop_seam.png'))
        for name in (prefix,clip+'_eight_angles'):
            assert not re.search(r'^ERROR:',(EV/(name+'.godot.log')).read_text(encoding='utf-8-sig'),re.M),'Reject resource/render failures even if exit code was0'
        evidence=[p.relative_to(ROOT).as_posix() for p in files]
        entries.append(dict(id=ident,sourceSheet=(ART/r['source']).relative_to(ROOT).as_posix(),sourceSha256=p['sha256'],bindingSha256=p['bindingSha256'],productionApproved=True,nativeReviewed=True,reviewedSourceFrames=16,visualNotes=notes[ident],nativeEvidence=evidence,nativeEvidenceSha256={f:sha(ROOT/f) for f in evidence}))
    old=read(EV/'manual_review_working.json');save(EV/'manual_review_before_e4.json',old)
    ledger=dict(batch=BATCH,manualReviewComplete=True,reviewDate='2026-11-15',reviewScale='ORIGINAL_16_NATIVE_PHASES_8_FACINGS_AND_REAL_LOOP_WRAPS',scope='SOURCE_VISUAL_CLIP_REVIEW_NOT_CLASS_OR_GAMEPLAY_ACCEPTANCE',entries=entries)
    save(EV/'source_native_review.json',ledger);save(EV/'manual_review_working.json',ledger)
    print(json.dumps(dict(selected=3,sourceApprovalsPrepared=3,nativeVideos=5,priorPins=362,applied=False)))
if __name__=='__main__':record()
