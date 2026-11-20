"""I delivery provenance/preservation gates; full game acceptance stays separate."""
import hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261115i'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    assert len(baseline['approvedSourcePins'])==365 and len(baseline['preservedPages'])==406
    for old in baseline['approvedSourcePins']:assert pins[old['id']]==old
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for old in baseline['preservedPages']:assert payload(by_id[old['id']])==old['payloadSha256']
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']}
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261115i'];assert len(records)==len(entries)==25
    for r in records:
        p=by_id[r['id']];e=entries[r['id']];held='_walk_' in r['id']
        assert p['productionApproved']==e['productionApproved']==(not held)
        assert (r['id'] in pins)==(not held) and (p['visualState']=='HOLD')==held
        assert sha(ART/r['source'])==sha(RUN/p['file'])==p['sha256']==e['sourceSha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256'] and p['sourceFrames']==16
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,digest in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==digest
    delivery=read(EV/'source_delivery_map.json');assert len(delivery['entries'])==25 and delivery['allByteIdentical']
    for e in delivery['entries']:assert sha(ART/e['deliveredSource'])==e['sourceSha256'] and e['byteIdentical']
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==25 and media['sourceFramesMeasured']==400 and media['actualLoopWraps']==10
    catalogue=read(EV/'catalogue_media_audit.json');assert catalogue['selectedVideos']==5
    for m in media['files']+catalogue['files']:assert m['decodedFrames']==180 and m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
    seams=read(EV/'loop_seam_sample_plan.json');assert len(seams)==10 and all(s['actualWrap'] and s['sourceFrames']==[14,15,0,1] for s in seams)
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files'];assert len(originals)==46
    for o in originals:assert sha(ROOT/o['file'])==o['expectedSha256']
    active=[p for p in pages if not p.get('legacy')];assert len(pages)==431 and len(active)==428 and len(pins)==385
    for p in active:assert sha(RUN/p['file'])==p['sha256']
    coverage=read(ART/'coverage.json');assert (coverage['boundRequiredPages'],coverage['productionApprovedPages'],coverage['pendingPages'],coverage['visualHoldPages'])==(90,65,938,25)
    jobs=read(ART/'generation_jobs.json');hb=[j for j in jobs if j['ownerId']=='CLASS_HUYEN_BUT' and j['kind']=='CLASS'];assert sum(covers(j,pages,True) for j in hb)==15
    assert set(baseline['approvedJobsBefore'])<={j['id'] for j in jobs if covers(j,pages,True)}
    return dict(batch='20261115i',selectedSources=25,sourcePoses=400,newSourceApprovals=20,newSourceHolds=5,sourcePins=385,priorPinsUnchanged=365,priorPagePayloadsUnchanged=406,ownerSelectedOriginalsUnchanged=46,activeRuntimePngsByteIdentical=428,nativeVideos=30,huyenButSourceActions='15/16; walking held',sourceReviewedJobs=65,pendingJobs=938,sourceHolds=25,fullLibraryComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_CLASS_OR_GAMEPLAY_ACCEPTANCE')
if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
