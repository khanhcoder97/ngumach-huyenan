"""Delivery snapshot: armed base source review with explicit quality holds."""
import hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114b'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');pins={p['id']:p for p in read(ART/'visual_review.json')['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'prior source pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'prior page changed: '+p['id']
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114b'];assert len(records)==15
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert len(entries)==15
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['productionApproved']==e['productionApproved'] and (ART/r['prompt']).is_file()
        assert p['sourceFrames']==16 and len(p['directions'])==1 and len(p['directions'][0]['frames'])==16
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected,'native evidence changed'
        assert (r['id'] in pins)==p['productionApproved']
    assert sum(e['productionApproved'] for e in entries.values())==8 and len(pins)==277
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(RUN/p['file'])==p['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for old in originals:assert sha(ROOT/old['file'])==old['expectedSha256']
    variants=list((ART/'Sheets').glob('*_20261114b.png'));assert len(variants)==17
    for p in variants:assert (ART/'Prompts'/(p.stem+'.txt')).is_file()
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==19 and media['supersededVideos']==0
    for m in media['files']:assert m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256'] and m['decodedFrames']==(600 if m['file']=='mobility_chain.mp4' else 180)
    coverage=read(ART/'coverage.json');assert (coverage['requiredPages'],coverage['boundRequiredPages'],coverage['pendingPages'],coverage['productionApprovedPages'])==(1028,79,949,49)
    mk=[j for j in read(ART/'generation_jobs.json') if j['id'].startswith('class_minh_kiem_')];assert len(mk)==16
    assert sum(covers(j,pages,True) for j in mk)==13
    return dict(batch='20261114b',selectedSheets=15,sourceCells=240,generatedVariants=17,newSourceApprovals=8,newSourceHolds=7,
        previousSourcePinsUnchanged=len(baseline['approvedSourcePins']),previousPagesUnchanged=len(baseline['preservedPages']),sourcePins=len(pins),
        ownerSelectedOriginalsUnchanged=len(originals),runtimeSourcesByteIdentical=len(runtime),structurePages=len(pages),
        requiredJobs=1028,boundJobs=79,pendingJobs=949,sourceReviewedJobs=49,minhKiemSourceReviewedActions=13,nativeReviewVideos=19,
        fullGameComplete=False,note='Held directional overrides shadow legacy bindings; do not count inherited approval as current runtime acceptance. Walk NE/E/SE, first cut N/NE/E/SE and previous run NE still need repair.')

if __name__=='__main__':
    r=audit();(EV/'delivery_audit.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(r))
