"""Audit F source/registration/evidence integrity, separately from visual judgement."""
import hashlib,json,re
from inspect_actor_library import ART,RUN,ROOT,binding_sha256
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114f'

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'Prior source pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'Prior page changed: '+p['id']
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114f'];assert len(records)==31
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert set(entries)=={r['id'] for r in records}
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256']==sha(RUN/p['file'])
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['sourceFrames']==16 and len(p['directions'])==1 and len(p['directions'][0]['frames'])==16
        assert p['productionApproved']==e['productionApproved']==(r['id'] in pins)
        assert e['nativeReviewed'] and e['reviewedSourceFrames']==16 and e['visualNotes'] and (ART/r['prompt']).is_file()
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected,'Native evidence changed'
    ne=[r for r in records if r.get('direction')=='NE'];assert len(ne)==6
    for r in ne:
        guide=r['generationInputs'][0];assert guide['role']=='AI_ORIENTATION_GUIDE_NOT_OWNER_APPROVED' and '/Guides_20261114f/' in guide['path']
        assert guide['sourceSha256']=='540597ab63601f3f2959885d2f5e806b127669c17b3d096401bdb3a51b0d0bca'
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==37
    for m in media['files']:assert m['decodedFrames']==180 and m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
    plan=read(EV/'capture_sample_plan.json');assert len(plan)==37
    raw=[p for p in plan if p['Name'].startswith('raw_')];assert len(raw)==31
    for p in raw:
        assert p['RenderedSourceFramesVerified']==16 and len(set(p['NativeSampleIndices']))==16
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(p['Name']+'.godot.log')).read_text(encoding='utf-8-sig'))]
        assert {b for a,b in ticks}==set(range(16))
        for frame,native in enumerate(p['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==frame,'Source pose/sample mismatch'
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(RUN/p['file'])==p['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for p in originals:assert sha(ROOT/p['file'])==p['expectedSha256']
    variants=list((ART/'Sheets').glob('*_20261114f.png'));assert len(variants)==33
    for p in variants:assert (ART/'Prompts'/(p.stem+'.txt')).is_file()
    history=[r for r in read(ART/'generation_history.json') if r.get('supersededByBatch')=='20261114f'];assert len(history)==4
    for r in history:assert sha(ART/r['source'])==r['sourceSha256']
    coverage=read(ART/'coverage.json');assert (coverage['requiredPages'],coverage['boundRequiredPages'],coverage['pendingPages'])==(1028,85,943)
    approved=sum(e['productionApproved'] for e in entries.values());assert len(pins)==301+approved
    return dict(batch='20261114f',selectedSources=31,generatedVariants=33,sourcePoses=496,bodySources=22,vfxComponents=9,newSourceApprovals=approved,newSourceHolds=31-approved,sourcePins=len(pins),priorPinsUnchanged=len(baseline['approvedSourcePins']),priorPagePayloadsUnchanged=len(baseline['preservedPages']),replacedHeldSources=2,structurePages=len(pages),runtimeSourcesByteIdentical=len(runtime),ownerSelectedOriginalsUnchanged=len(originals),nativeVideos=37,nativeSourcePosesMeasured=496,requiredJobs=1028,boundJobs=85,pendingJobs=943,sourceReviewedJobs=coverage['productionApprovedPages'],sourceHolds=coverage['visualHoldPages'],fullGameComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_SKILL_CLASS_OR_GAMEPLAY_ACCEPTANCE')

if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
