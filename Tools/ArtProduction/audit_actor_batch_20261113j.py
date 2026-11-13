"""J delivery snapshot: previous art is immutable; approval must match the inspected binding."""
import hashlib,json
from pathlib import Path
from inspect_actor_library import binding_sha256,covers
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113j'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'prior approval pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'prior page payload changed: '+p['id']
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261113j'];assert len(records)==21
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert len(entries)==21
    assert sum(by_id[r['id']]['sourceFrames'] for r in records)==336
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['productionApproved']==e['productionApproved'] and (ART/r['prompt']).is_file()
        assert len(p['directions'])==1 and len(p['directions'][0]['frames'])==16
        assert len(r['sourceFrameDurationsMs'])==16 and min(r['sourceFrameDurationsMs'])>=1000/60
        for reference in r['generationInputs']:assert sha(ROOT/reference['path'])==reference['sourceSha256']
        for f in e['nativeEvidence']:assert (ROOT/f).is_file()
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(ROOT/'ClientGodot/assets/actor_library_v1'/p['file'])==p['sha256']
    old_png=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for old in old_png:assert sha(ROOT/old['file'])==old['expectedSha256']
    coverage=read(ART/'coverage.json');assert coverage['requiredPages']==1028 and coverage['boundRequiredPages']==75 and coverage['pendingPages']==953
    jobs=read(ART/'generation_jobs.json');ad=[j for j in jobs if j['id'].startswith('class_anh_dao_')];assert len(ad)==16
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==27 and media['supersededVideos']==25
    for m in media['files']:
        assert m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
        assert m['decodedFrames']==(600 if 'mobility_chain' in m['file'] else 180)
    source_approved=sum(by_id[r['id']]['productionApproved'] for r in records)
    assert len(pins)==len(baseline['approvedSourcePins'])+source_approved
    return dict(batch='20261113j',selectedSheets=21,sourceCells=336,newSourceApprovals=source_approved,newSourceHolds=21-source_approved,
        previousSourcePinsUnchanged=len(baseline['approvedSourcePins']),previousPagesUnchanged=len(baseline['preservedPages']),
        ownerSelectedOriginalsUnchanged=len(old_png),runtimeSourcesByteIdentical=len(runtime),structurePages=len(pages),
        requiredJobs=1028,boundJobs=75,pendingJobs=953,sourceReviewedJobs=coverage['productionApprovedPages'],
        anhDaoRequiredActions=16,anhDaoSourceReviewedActions=sum(covers(j,pages,True) for j in ad),
        nativeReviewVideos=27,historicalRejectedRegistrationVideos=25,fullGameComplete=False,
        note='Source/native visual acceptance only. Offline60-step movies do not certify gameplay FPS, combat, root motion, damage or complete class integration.')

if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
