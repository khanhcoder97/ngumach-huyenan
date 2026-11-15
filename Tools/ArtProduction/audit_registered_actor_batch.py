"""Verify delivered source ledgers and preserved baselines, without accepting gameplay."""
import argparse,hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def audit(batch,expected,prior_pins):
    assert batch.isalnum() and expected>0 and prior_pins>=0
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);baseline=read(ev/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    assert len(baseline['approvedSourcePins'])==prior_pins
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages};ledger=read(ev/'source_native_review.json');assert ledger['manualReviewComplete'] and ledger['batch']==batch
    entries={e['id']:e for e in ledger['entries']};records=[r for r in read(ART/'generation_records.json') if r.get('batch')==batch]
    assert len(entries)==len(records)==expected and set(entries)=={r['id'] for r in records}
    preserved=baseline['preservedPages'];assert len(preserved)==baseline['previousPages']-len(baseline['replacedUnapprovedIds'])
    for p in preserved:assert payload(by_id[p['id']])==p['payloadSha256']
    assert set(by_id)=={p['id'] for p in preserved}|set(entries)
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==sha(RUN/p['file'])==p['sha256']==e['sourceSha256'] and p['sourceFrames']==e['reviewedSourceFrames']==16
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert e['nativeReviewed'] and e['productionApproved']==p['productionApproved']==(r['id'] in pins)
        assert p['visualState']==('APPROVED' if e['productionApproved'] else 'HOLD')
        assert set(e['nativeEvidence'])==set(e['nativeEvidenceSha256'])
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,digest in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==digest
    approved=sum(e['productionApproved'] for e in entries.values());assert len(pins)==prior_pins+approved
    media=read(ev/'native_media_audit.json');catalogue=read(ev/'catalogue_media_audit.json');assert not media['pilot'] and media['selectedVideos']==expected and media['sourceFramesMeasured']==expected*16
    assert len(media['files'])==expected and {m['sourceSha256'] for m in media['files']}=={e['sourceSha256'] for e in entries.values()}
    for m in media['files']+catalogue['files']:assert m['decodedFrames']==180 and m['decodedWithoutDiagnostics'] and sha(ev/m['file'])==m['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files'];assert len(originals)==46
    for p in originals:assert sha(ROOT/p['file'])==p['expectedSha256']
    active=[p for p in pages if not p.get('legacy')]
    for p in active:assert sha(RUN/p['file'])==p['sha256']
    jobs=read(ART/'generation_jobs.json');source_jobs={j['id'] for j in jobs if covers(j,pages,True)};bound=sum(covers(j,pages) for j in jobs)
    assert set(baseline['approvedJobsBefore'])<=source_jobs
    coverage=read(ART/'coverage.json');assert (coverage['boundRequiredPages'],coverage['productionApprovedPages'],coverage['pendingPages'],coverage['visualHoldPages'])==(bound,len(source_jobs),len(jobs)-bound,sum(p['visualState']=='HOLD' for p in pages))
    receipt=read(ART/('candidate_'+batch+'_receipt.json'));assert receipt['selected']==expected and not receipt['sourceReviewPending'] and receipt['newSourceApprovals']==approved
    assert len(pages)==baseline['previousPages']+receipt['newIds']
    return dict(batch=batch,selectedSources=expected,sourcePoses=expected*16,newSourceApprovals=approved,newSourceHolds=expected-approved,sourcePins=len(pins),priorPinsUnchanged=prior_pins,priorPagePayloadsUnchanged=len(preserved),ownerSelectedOriginalsUnchanged=46,activeRuntimePngsByteIdentical=len(active),structurePages=len(pages),nativeVideos=media['selectedVideos']+catalogue['selectedVideos'],sourceReviewedJobs=len(source_jobs),pendingJobs=coverage['pendingPages'],sourceHolds=coverage['visualHoldPages'],fullLibraryComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_CLASS_OR_GAMEPLAY_ACCEPTANCE')
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--expected',type=int,required=True);p.add_argument('--prior-pins',type=int,required=True);a=p.parse_args();result=audit(a.batch,a.expected,a.prior_pins);(ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+a.batch)/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
