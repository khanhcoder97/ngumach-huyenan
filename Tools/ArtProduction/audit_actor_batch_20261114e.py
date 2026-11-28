"""Check E originals, prior bindings and measured native source-frame evidence."""
import hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114e'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'prior source pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'prior page changed: '+p['id']
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114e'];assert len(records)==16
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert len(entries)==16
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256'] and sha(RUN/p['file'])==p['sha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['sourceFrames']==16 and len(p['directions'])==1 and len(p['directions'][0]['frames'])==16
        assert p['productionApproved']==e['productionApproved']==(r['id'] in pins)
        assert (ART/r['prompt']).is_file()
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected,'native evidence changed'
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==18 and media['supersededVideos']==2
    for m in media['files']:assert m['decodedFrames']==180 and m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
    plan=read(EV/'capture_sample_plan.json');assert len(plan)==18
    raw=[p for p in plan if p['Name'].startswith('raw_')];assert len(raw)==16
    for p in raw:
        assert p['RenderedSourceFramesVerified']==16 and len(set(p['NativeSampleIndices']))==16
        log=(EV/(p['Name']+'.godot.log')).read_text(encoding='utf-8-sig')
        import re
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',log)]
        assert {b for a,b in ticks}==set(range(16)),'native source phase missing'
        for frame,native in enumerate(p['NativeSampleIndices']):
            shown=max((a,b) for a,b in ticks if a<=native)[1];assert shown==frame,'temporal crop does not show the requested source pose'
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(RUN/p['file'])==p['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for p in originals:assert sha(ROOT/p['file'])==p['expectedSha256']
    variants=list((ART/'Sheets').glob('*_20261114e.png'));assert len(variants)==17
    for p in variants:assert (ART/'Prompts'/(p.stem+'.txt')).is_file()
    old=[r for r in read(ART/'generation_history.json') if r.get('supersededByBatch')=='20261114e'];assert len(old)==1 and sha(ART/old[0]['source'])==old[0]['sourceSha256']
    c=read(ART/'coverage.json');assert (c['requiredPages'],c['boundRequiredPages'],c['pendingPages'])==(1028,81,947)
    approved=sum(e['productionApproved'] for e in entries.values());assert len(pins)==len(baseline['approvedSourcePins'])+approved
    return dict(batch='20261114e',selectedSources=16,generatedVariants=17,sourcePoses=256,bodySources=10,vfxComponents=6,
        newSourceApprovals=approved,newSourceHolds=16-approved,sourcePins=len(pins),priorPinsUnchanged=len(baseline['approvedSourcePins']),
        priorPagePayloadsUnchanged=len(baseline['preservedPages']),structurePages=len(pages),runtimeSourcesByteIdentical=len(runtime),
        ownerSelectedOriginalsUnchanged=len(originals),nativeVideos=18,nativeSourcePosesMeasured=256,requiredJobs=1028,boundJobs=81,pendingJobs=947,
        sourceReviewedJobs=c['productionApprovedPages'],fullGameComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_FULL_SKILL_CLASS_OR_GAMEPLAY_ACCEPTANCE')

if __name__=='__main__':
    value=audit();(EV/'delivery_audit.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(value))
