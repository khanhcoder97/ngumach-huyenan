"""Verify H preservation/provenance and completed source review, not full game acceptance."""
import hashlib,json,re
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261115h'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    assert len(baseline['approvedSourcePins'])==362 and len(baseline['preservedPages'])==404
    for old in baseline['approvedSourcePins']:assert pins[old['id']]==old
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for old in baseline['preservedPages']:assert payload(by_id[old['id']])==old['payloadSha256']
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']}
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261115h'];assert len(records)==len(entries)==3
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert p['productionApproved'] and e['productionApproved'] and r['id'] in pins
        assert sha(ART/r['source'])==sha(RUN/p['file'])==p['sha256']==e['sourceSha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256'] and p['sourceFrames']==16
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected
    variants=list((ART/'Sheets').glob('*_20261115h.png'));assert len(variants)==6
    for path in variants:assert (ART/'Prompts'/(path.stem+'.txt')).is_file()
    history=[r for r in read(ART/'generation_history.json') if r.get('supersededByBatch')=='20261115h'];assert len(history)==6
    for r in history:assert sha(ART/r['source'])==r['sourceSha256']
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==5 and media['supersededVideos']==3 and media['failedImportTrials']==2
    for m in media['files']:assert m['decodedFrames']==180 and m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
    for m in media['supersededFiles']:assert sha(EV/m['file'])==m['sha256']
    raw=read(EV/'capture_sample_plan.json');assert len(raw)==3
    for entry in raw:
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(entry['Name']+'.godot.log')).read_text(encoding='utf-8-sig'))]
        for phase,native in enumerate(entry['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==phase
    seams=read(EV/'loop_seam_sample_plan.json');assert len(seams)==2 and all(s['actualWrap'] and s['sourceFrames']==[14,15,0,1] for s in seams)
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files'];assert len(originals)==46
    for original in originals:assert sha(ROOT/original['file'])==original['expectedSha256']
    active=[p for p in pages if not p.get('legacy')];assert len(pages)==407 and len(active)==404 and len(pins)==365
    for p in active:assert sha(RUN/p['file'])==p['sha256']
    coverage=read(ART/'coverage.json');assert (coverage['boundRequiredPages'],coverage['productionApprovedPages'],coverage['pendingPages'],coverage['visualHoldPages'])==(90,61,938,20)
    hb=[j for j in read(ART/'generation_jobs.json') if j['ownerId']=='CLASS_HUYEN_BUT' and j['kind']=='CLASS'];assert sum(covers(j,pages,True) for j in hb)==11
    return dict(batch='20261115h',selectedSources=3,persistedVariants=6,sourcePoses=48,newSourceApprovals=3,sourcePins=365,priorPinsUnchanged=362,priorPagePayloadsUnchanged=404,ownerSelectedOriginalsUnchanged=46,activeRuntimePngsByteIdentical=404,selectedNativeVideos=5,supersededNativeTrials=3,failedImportTrialsRetained=2,huyenButSourceActions='11/16',sourceReviewedJobs=61,pendingJobs=938,sourceHolds=20,fullLibraryComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_CLASS_OR_GAMEPLAY_ACCEPTANCE')
if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
