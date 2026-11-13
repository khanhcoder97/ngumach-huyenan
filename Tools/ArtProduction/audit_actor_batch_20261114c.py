"""Verify held-source repairs without rewriting prior accepted bindings."""
import hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114c'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');pins={p['id']:p for p in read(ART/'visual_review.json')['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'prior source pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'prior page changed: '+p['id']
    history=read(ART/'generation_history.json')
    for p in baseline['replacedHeldPages']:
        assert not p['productionApproved'] and p['visualState']=='HOLD'
        assert sha(ART/p['source'])==p['sha256']==sha(RUN/p['file']),'old held PNG changed/deleted'
        assert any(r['id']==p['id'] and r['source']==p['source'] and r.get('supersededByBatch')=='20261114c' for r in history),'held history missing'
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114c'];assert len(records)==8
    assert {r['id'] for r in records}==set(baseline['replacedHeldIds'])
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert len(entries)==8
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256'] and binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['productionApproved']==e['productionApproved'] and (ART/r['prompt']).is_file() and p['sourceFrames']==16
        assert len(p['directions'])==1 and len(p['directions'][0]['frames'])==16 and (r['id'] in pins)==p['productionApproved']
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected,'native evidence changed'
    assert sum(e['productionApproved'] for e in entries.values())==5 and len(pins)==282
    assert {e['id'] for e in entries.values() if not e['productionApproved']}=={'class_minh_kiem_run_ne','class_minh_kiem_walk_ne','class_minh_kiem_walk_se'}
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(RUN/p['file'])==p['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for old in originals:assert sha(ROOT/old['file'])==old['expectedSha256']
    variants=list((ART/'Sheets').glob('*_20261114c.png'));assert len(variants)==8
    for p in variants:assert (ART/'Prompts'/(p.stem+'.txt')).is_file()
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==12 and media['supersededVideos']==0
    for m in media['files']:assert m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256'] and m['decodedFrames']==(600 if m['file']=='mobility_chain.mp4' else 180)
    c=read(ART/'coverage.json');assert (c['requiredPages'],c['boundRequiredPages'],c['pendingPages'],c['productionApprovedPages'],c['visualHoldPages'])==(1028,79,949,50,20)
    mk=[j for j in read(ART/'generation_jobs.json') if j['id'].startswith('class_minh_kiem_')];assert sum(covers(j,pages,True) for j in mk)==14
    return dict(batch='20261114c',selectedRepairs=8,sourceCells=128,newSourceApprovals=5,remainingSourceHolds=3,
        priorPinsUnchanged=277,otherPagePayloadsUnchanged=len(baseline['preservedPages']),oldHeldSourcesPreserved=8,ownerSelectedOriginalsUnchanged=46,
        sourcePins=282,runtimeSourcesByteIdentical=len(runtime),structurePages=len(pages),requiredJobs=1028,boundJobs=79,pendingJobs=949,
        sourceReviewedJobs=50,minhKiemSourceReviewedActions=14,nativeReviewVideos=12,fullGameComplete=False,
        note='First cut now complete across five authored directions. RunNE/walkNE/walkSE still held; do not certify class or gameplay from source counts.')

if __name__=='__main__':
    r=audit();(EV/'delivery_audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r))
