"""Validate new VFX originals and reproducible authoring evidence, not gameplay."""
import hashlib,json
from inspect_actor_library import ART,RUN,ROOT,binding_sha256

EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114d'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def audit():
    baseline=read(EV/'baseline_preservation.json')
    review=read(ART/'visual_review.json');pins={p['id']:p for p in review['sourceApprovals']}
    for p in baseline['approvedSourcePins']:assert pins[p['id']]==p,'prior pin changed'
    pages=read(ART/'structure_report.json')['pages'];by_id={p['id']:p for p in pages}
    for p in baseline['preservedPages']:assert payload(by_id[p['id']])==p['payloadSha256'],'prior page changed: '+p['id']
    records=[r for r in read(ART/'generation_records.json') if r.get('batch')=='20261114d']
    ledger=read(EV/'source_native_review.json');assert ledger['manualReviewComplete']
    entries={e['id']:e for e in ledger['entries']};assert len(records)==len(entries)==5
    for r in records:
        p=by_id[r['id']];e=entries[r['id']]
        assert sha(ART/r['source'])==p['sha256']==e['sourceSha256']
        assert binding_sha256(p)==p['bindingSha256']==e['bindingSha256']
        assert p['sourceFrames']==16 and len(p['directions'])==1 and len(p['directions'][0]['frames'])==16
        assert r['componentOnly'] and (ART/r['prompt']).is_file()
        assert p['productionApproved']==e['productionApproved']==(r['id'] in pins)
        for ref in r['generationInputs']:assert sha(ROOT/ref['path'])==ref['sourceSha256']
        for f,expected in e['nativeEvidenceSha256'].items():assert sha(ROOT/f)==expected,'native evidence changed'
    runtime=[p for p in pages if not p.get('legacy')]
    for p in runtime:assert sha(RUN/p['file'])==p['sha256']
    originals=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json')['files']
    for old in originals:assert sha(ROOT/old['file'])==old['expectedSha256']
    assert sha(ART/'skill_assembly_profiles_v1.json')==sha(RUN/'skill_assemblies.json')
    doc=read(RUN/'skill_assemblies.json');assert not doc['ProductionApproved'] and doc['Scope']=='PRESENTATION_ASSEMBLY_REVIEW_ONLY'
    snapshot=read(EV/'assembly_source_snapshot.json');assert snapshot['profileSha256']==sha(RUN/'skill_assemblies.json')
    for source in snapshot['sources']:
        page=by_id[source['id']]
        assert source['sha256']==page['sha256']==sha(ART/source['source'])==sha(RUN/source['file'])
        assert source['bindingSha256']==page['bindingSha256']==binding_sha256(page)
    scenarios=[(p,v) for p in doc['Profiles'] for v in p['Variants']];assert len(doc['Profiles'])==12 and len(scenarios)==20
    visual=read(EV/'assembly_visual_review.json');assert visual['manualReviewComplete'] and not visual['gameplayAccepted']
    assert {(e['profile'],e['variant']) for e in visual['entries']}=={(p['Id'],v['Id']) for p,v in scenarios}
    for e in visual['entries']:
        assert e['notes'] and e['reviewedFacings']==8
        for f,expected in e['evidenceSha256'].items():assert sha(ROOT/f)==expected
    media=read(EV/'native_media_audit.json');assert media['selectedVideos']==27 and media['supersededVideos']==5
    for m in media['files']:
        assert m['decodedWithoutDiagnostics'] and sha(EV/m['file'])==m['sha256']
        assert m['decodedFrames']==(600 if m['file'].startswith('assembly_') else 180)
    c=read(ART/'coverage.json')
    assert (c['requiredPages'],c['boundRequiredPages'],c['pendingPages'],c['productionApprovedPages'],c['visualHoldPages'])==(1028,79,949,50,20)
    return dict(batch='20261114d',newComponents=5,newSourcePoses=80,newSourceApprovals=sum(e['productionApproved'] for e in entries.values()),
        priorPinsUnchanged=len(baseline['approvedSourcePins']),priorPagePayloadsUnchanged=len(baseline['preservedPages']),
        sourcePins=len(pins),structurePages=len(pages),runtimeSourcesByteIdentical=len(runtime),ownerSelectedOriginalsUnchanged=len(originals),
        authoringSkillProfiles=12,authoringScenarios=20,assemblyBoundSources=len(snapshot['sources']),selectedNativeVideos=27,lowFxComparisons=2,
        requiredJobs=1028,boundJobs=79,pendingJobs=949,sourceReviewedJobs=50,fullGameComplete=False,
        scope='SOURCE_VISUAL_CLIPS_AND_EDITABLE_PRESENTATION_EXAMPLES_NOT_GAMEPLAY_OR_CLASS_ACCEPTANCE')

if __name__=='__main__':
    result=audit();(EV/'delivery_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result))
