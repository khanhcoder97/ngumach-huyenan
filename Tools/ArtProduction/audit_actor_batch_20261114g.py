"""Integrity evidence for G; manual visual decisions remain in the source ledger."""
import hashlib,json,re
from inspect_actor_library import ART,RUN,ROOT,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g'
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def payload(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json');review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    assert len(baseline['approvedSourcePins'])==329 and len(baseline['preservedPages'])==371
    for old in baseline['approvedSourcePins']:assert pins[old['id']]==old,'Prior pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for old in baseline['preservedPages']:assert payload(by_id[old['id']])==old['payloadSha256'],'Prior page changed'
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114g'];assert len(records)==36
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete'];entries={e['id']:e for e in ledger['entries']};assert set(entries)=={r['id'] for r in records}
    for record in records:
        page=by_id[record['id']];entry=entries[record['id']]
        assert sha(ART/record['source'])==page['sha256']==entry['sourceSha256']==sha(RUN/page['file'])
        assert binding_sha256(page)==page['bindingSha256']==entry['bindingSha256']
        assert page['sourceFrames']==16 and len(page['directions'])==1 and len(page['directions'][0]['frames'])==16
        assert page['productionApproved']==entry['productionApproved']==(record['id'] in pins)
        assert entry['nativeReviewed'] and entry['reviewedSourceFrames']==16 and entry['visualNotes']
        assert (ART/record['prompt']).is_file() and (ROOT/entry['sourceSheet']).is_file()
        for ref in record['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for proof,expected in entry['nativeEvidenceSha256'].items():assert sha(ROOT/proof)==expected,'Evidence changed after manual review'
    ne=[r for r in records if r.get('direction')=='NE'];assert len(ne)==5
    for record in ne:
        guide=record['generationInputs'][0]
        assert guide['role']=='AI_ORIENTATION_GUIDE_NOT_OWNER_APPROVED' and '/Guides_20261114f/' in guide['path']
        assert guide['sourceSha256']=='540597ab63601f3f2959885d2f5e806b127669c17b3d096401bdb3a51b0d0bca'
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==43 and media['supersededVideos']==5 and len(media['unchangedActiveSnapshots'])==1
    for video in media['files']:assert video['decodedFrames']==180 and video['decodedWithoutDiagnostics'] and sha(EV/video['file'])==video['sha256']
    plan=read(EV/'capture_sample_plan.json');assert len(plan)==43
    raw=[p for p in plan if p['Name'].startswith('raw_')];assert len(raw)==36
    for source in raw:
        assert source['RenderedSourceFramesVerified']==16 and len(set(source['NativeSampleIndices']))==16
        ticks=[(int(a),int(b)) for a,b in re.findall(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)',(EV/(source['Name']+'.godot.log')).read_text(encoding='utf-8-sig'))]
        for phase,native in enumerate(source['NativeSampleIndices']):assert max((a,b) for a,b in ticks if a<=native)[1]==phase
    seams=read(EV/'loop_seam_sample_plan.json');assert len(seams)==4 and all(s['actualWrap'] and s['sourceFrames']==[14,15,0,1] for s in seams)
    active=[p for p in pages if not p.get('legacy')];assert len(active)==404 and len(pages)==407
    for page in active:assert sha(RUN/page['file'])==page['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for original in originals:assert sha(ROOT/original['file'])==original['expectedSha256']
    variants=list((ART/'Sheets').glob('*_20261114g.png'));assert len(variants)==41
    for variant in variants:assert (ART/'Prompts'/(variant.stem+'.txt')).is_file()
    history=[r for r in read(ART/'generation_history.json') if r.get('supersededByBatch')=='20261114g'];assert len(history)==8
    for record in history:assert sha(ART/record['source'])==record['sourceSha256']
    coverage=read(ART/'coverage.json');assert (coverage['requiredPages'],coverage['boundRequiredPages'],coverage['pendingPages'],coverage['productionApprovedPages'])==(1028,90,938,59)
    approved=sum(e['productionApproved'] for e in entries.values());assert approved==33 and len(pins)==329+approved
    jobs=read(ART/'generation_jobs.json');hb=[j for j in jobs if j['ownerId']=='CLASS_HUYEN_BUT' and j['kind']=='CLASS'];assert len(hb)==16
    source_actions=sum(covers(j,pages,True) for j in hb);assert source_actions==9
    return dict(batch='20261114g',selectedSources=36,persistedGeneratedVariants=41,sourcePoses=576,bodySources=27,vfxComponents=9,newSourceApprovals=approved,newSourceHolds=3,sourcePins=len(pins),priorPinsUnchanged=329,priorPagePayloadsUnchanged=371,replacedHeldSources=3,structurePages=407,runtimeSourcesByteIdentical=404,ownerSelectedOriginalsUnchanged=len(originals),nativeVideos=43,supersededNativeVideos=5,unchangedArchivedSnapshots=1,nativeSourcePosesMeasured=576,requiredJobs=1028,boundJobs=90,pendingJobs=938,sourceReviewedJobs=59,sourceHolds=coverage['visualHoldPages'],huyenButSourceActions=source_actions,huyenButRequiredActions=16,fullGameComplete=False,scope='SOURCE_CLIP_REVIEW_NOT_CLASS_SKILL_OR_GAMEPLAY_ACCEPTANCE')

if __name__=='__main__':
    report=audit();(EV/'delivery_audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(report))
