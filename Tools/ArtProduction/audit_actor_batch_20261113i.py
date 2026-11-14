"""Delivery audit: prior art/approvals stay intact; held gait never gains approval."""
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113i'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json')
    pins={p['id']:p for p in review['sourceApprovals']}
    for old in baseline['approvedSourcePins']:assert pins[old['id']]==old,'prior source pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for old in baseline['preservedPages']:assert payload(by_id[old['id']])==old['payloadSha256'],'prior page payload changed: '+old['id']
    assert all(i not in by_id for i in baseline['archivedIds'])
    selected=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261113i'];assert len(selected)==15
    assert sum(by_id[r['id']]['sourceFrames'] for r in selected)==240
    selected_approved=[r for r in selected if by_id[r['id']]['productionApproved']]
    assert len(selected_approved)==14,'fourteen sources should pass; E gait remains a hold'
    held=by_id['class_anh_dao_walk_e'];assert held['visualState']=='HOLD' and not held['productionApproved'] and held['id'] not in pins
    assert all(len(by_id[r['id']]['directions'])==1 and len(by_id[r['id']]['directions'][0]['frames'])==16 for r in selected)
    for r in selected:
        p=by_id[r['id']];assert sha(ART/r['source'])==p['sha256'];assert (ART/r['prompt']).is_file()
        for source in r['generationInputs']:
            assert sha(ROOT/source['path'])==source['sourceSha256'],'reference missing or changed'
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(ROOT/'ClientGodot/assets/actor_library_v1'/p['file'])==p['sha256'],'runtime PNG differs'
    coverage=read(ART/'coverage.json');assert coverage['requiredPages']==1028 and coverage['boundRequiredPages']==71 and coverage['pendingPages']==957
    jobs={j['id']:j for j in read(ART/'generation_jobs.json')}
    for actor in ('minh_kiem','anh_dao','huyen_but','thach_chuy','linh_cung'):
        for clip in ('run','interact','basic_attack_02','basic_attack_03'):assert 'class_'+actor+'_'+clip in jobs
    source_review=read(EV/'source_native_review.json');assert len(source_review['entries'])==15
    for entry in source_review['entries']:
        page=by_id[entry['id']];assert page['sha256']==entry['sourceSha256'] and page['bindingSha256']==entry['bindingSha256']
        assert entry['productionApproved']==page['productionApproved']
        for f in entry['nativeEvidence']:assert (ROOT/f).is_file(),'missing review evidence'
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==19 and media['supersededVideos']==0
    old_png=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for old in old_png:assert sha(ROOT/old['file'])==old['expectedSha256'],'approved original PNG changed'
    return dict(batch='20261113i',selectedSheets=15,sourceCells=240,newSourceApprovals=14,newSourceHolds=1,
                previousSourcePinsUnchanged=len(baseline['approvedSourcePins']),previousPagesUnchanged=len(baseline['preservedPages']),
                ownerSelectedOriginalsUnchanged=len(old_png),runtimeSourcesByteIdentical=len(runtime),
                requiredJobs=1028,boundJobs=71,pendingJobs=957,nativeReviewVideos=19,fullGameComplete=False,
                note='Source/clip acceptance only. E and mirrored W walk remain unavailable to the approved renderer; no gameplay FPS/combat acceptance.')


if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
