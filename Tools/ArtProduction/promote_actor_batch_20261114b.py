"""Preview armed base clips; never grant approval or edit approved source bytes."""
import hashlib,json,shutil
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114b'

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

if __name__=='__main__':
    records=read(ART/'generation_records.json');assert not any(r.get('batch')=='20261114b' for r in records),'Already promoted'
    m=read(ART/'Candidates_20261114b/candidate_manifest.json');assert len(m['records'])==15 and m['remainingSourcePages']==0
    assert not ({r['id'] for r in m['records']}&{r['id'] for r in records}),'replacement IDs need a separate reviewed migration'
    for r in m['records']:
        assert r['pivotMode']=='SOURCE_FOOT_PIVOTS' and 'sourceFootPivots' in r
        assert inspect(r)['sourceFrames']==16
    review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json')
    assert len(review['sourceApprovals'])==269 and len(structure['pages'])==309
    for p in structure['pages']:
        if not p.get('legacy'):assert sha(ART/p['source'])==p['sha256']==sha(RUN/p['file'])
    EV.mkdir(parents=True,exist_ok=True)
    save(EV/'baseline_preservation.json',dict(previousHead='40af7133c4169daab5e0c0ab4065a11fffd4e15d',approvedSourcePins=review['sourceApprovals'],
        previousPages=len(structure['pages']),preservedPages=[dict(id=p['id'],payloadSha256=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()) for p in structure['pages']]))
    for ext,target in (('png','Sheets'),('txt','Prompts')):
        for p in (ART/'Candidates_20261114b').glob('*.'+ext):
            out=ART/target/p.name;assert not out.exists()
            if ext=='png':shutil.copyfile(p,out);assert sha(p)==sha(out)
            else:out.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    relocations=[]
    def normalize(r):
        r['generationInputs']=[]
        for i,original in enumerate([r['reference']]+r.get('additionalReferences',[])):
            delivered=original.replace('/Candidates_20261114b/','/Sheets/');assert (ROOT/delivered).is_file()
            e=dict(role=r.get('inputRole','IDENTITY_REFERENCE') if i==0 else 'SUPPORTING_REFERENCE',path=delivered,sourceSha256=sha(ROOT/delivered))
            if delivered!=original:
                assert sha(ROOT/original)==e['sourceSha256'];e['generationInputPath']=original
                relocations.append(dict(original=original,delivered=delivered,sha256=e['sourceSha256'],byteIdentical=True))
            r['generationInputs'].append(e)
        r['reference']=r['generationInputs'][0]['path'];r['additionalReferences']=[e['path'] for e in r['generationInputs'][1:]]
        r['source']=r['source'].replace('Candidates_20261114b/','Sheets/');r['prompt']=r['prompt'].replace('Candidates_20261114b/','Prompts/')
    selected=[];by_id={r['id']:r for r in m['records']}
    for clip in ('idle','walk','basic_attack'):
        for d in ('n','ne','e','se','s'):
            r=by_id['class_minh_kiem_'+clip+'_'+d];normalize(r);r['status']='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW'
            r['reviewScope']='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE';selected.append(r)
    history=read(ART/'generation_history.json')
    for r in m['history']:
        normalize(r);history.append({**r,'supersededByBatch':'20261114b','archiveStatus':'SOURCE_REPAIR_HISTORY_NOT_RENDERED'})
    pages=[]
    for r in selected:
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='AWAITING_VISUAL_REVIEW',visualNotes='')
        shutil.copyfile(ART/r['source'],RUN/p['file']);assert sha(RUN/p['file'])==p['sha256'];pages.append(p)
    structure['pages']=[p for p in structure['pages'] if not p.get('legacy')]+pages+[p for p in structure['pages'] if p.get('legacy')]
    save(ART/'generation_records.json',records+selected);save(ART/'generation_history.json',history);save(ART/'structure_report.json',structure)
    save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    registration=read(ART/'body_registration_20261114b.json')
    for e in registration['entries']:e['source']=e['source'].replace('Candidates_20261114b/','Sheets/')
    save(ART/'body_registration_20261114b.json',registration)
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json');pending=[j['id'] for j in jobs if not covers(j,structure['pages'])]
    coverage.update(structurePassed=len(structure['pages']),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,
        productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage);save(EV/'reference_delivery_audit.json',dict(generationInputsRetained=True,relocatedReferences=relocations,allByteIdentical=True))
    save(ART/'candidate_20261114b_receipt.json',dict(batch='20261114b',selected=15,sourceCells=240,generatedVariants=m['generatedVariants'],
        sourceReviewPending=True,newSourceApprovals=0,fullGameComplete=False,note='Preview only; reviewed source/native ledger required. Legacy PNGs preserved; approval counts follow directional override precedence.'))
    print(json.dumps(dict(previewPages=15,sourceCells=240,priorPinsUnchanged=269,sourceReviewedJobs=coverage['productionApprovedPages'],fullGameComplete=False)))
