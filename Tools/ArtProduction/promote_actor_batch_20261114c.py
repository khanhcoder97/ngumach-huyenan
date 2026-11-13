"""Replace eight held bindings for preview; preserve all approved originals/pins."""
import hashlib,json,shutil
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,covers
EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114c'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

if __name__=='__main__':
    records=read(ART/'generation_records.json');assert not any(r.get('batch')=='20261114c' for r in records),'Already promoted'
    m=read(ART/'Candidates_20261114c/candidate_manifest.json');assert len(m['records'])==8 and m['remainingSourcePages']==0
    ids={r['id'] for r in m['records']};review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json');old={p['id']:p for p in structure['pages']}
    assert len(review['sourceApprovals'])==277 and len(old)==324
    assert all(i in old and old[i]['visualState']=='HOLD' and not old[i]['productionApproved'] for i in ids)
    assert not ids&{p['id'] for p in review['sourceApprovals']},'approved sources need a separate review migration'
    for r in m['records']:assert r['pivotMode']=='SOURCE_FOOT_PIVOTS' and inspect(r)['sourceFrames']==16
    for p in old.values():
        if not p.get('legacy'):assert sha(ART/p['source'])==p['sha256']==sha(RUN/p['file'])
    EV.mkdir(parents=True,exist_ok=True)
    save(EV/'baseline_preservation.json',dict(previousHead='6a1f3dad438f32f36d128418cc18a0e1f0c2f8cf',approvedSourcePins=review['sourceApprovals'],
        previousPages=324,replacedHeldIds=sorted(ids),replacedHeldPages=[old[i] for i in sorted(ids)],
        preservedPages=[dict(id=p['id'],payloadSha256=payload(p)) for p in old.values() if p['id'] not in ids]))
    for ext,target in (('png','Sheets'),('txt','Prompts')):
        for p in (ART/'Candidates_20261114c').glob('*.'+ext):
            out=ART/target/p.name;assert not out.exists()
            if ext=='png':shutil.copyfile(p,out);assert sha(p)==sha(out)
            else:out.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    replacements={};updates={};relocations=[];holds={h['id']:h['reason'] for h in review['holds']}
    for r in m['records']:
        r['generationInputs']=[]
        for i,original in enumerate([r['reference']]+r.get('additionalReferences',[])):
            delivered=original.replace('/Candidates_20261114c/','/Sheets/');e=dict(role=r.get('inputRole','IDENTITY_REFERENCE') if i==0 else 'SUPPORTING_REFERENCE',path=delivered,sourceSha256=sha(ROOT/delivered))
            if delivered!=original:
                assert sha(ROOT/original)==e['sourceSha256'];e['generationInputPath']=original;relocations.append(dict(original=original,delivered=delivered,sha256=e['sourceSha256'],byteIdentical=True))
            r['generationInputs'].append(e)
        r['reference']=r['generationInputs'][0]['path'];r['additionalReferences']=[e['path'] for e in r['generationInputs'][1:]]
        r['source']=r['source'].replace('Candidates_20261114c/','Sheets/');r['prompt']=r['prompt'].replace('Candidates_20261114c/','Prompts/')
        r['status']='SOURCE_REPAIR_PREVIEW_PENDING_NATIVE_REVIEW';r['reviewScope']='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE';replacements[r['id']]=r
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='HOLD',visualNotes=holds[r['id']])
        shutil.copyfile(ART/r['source'],RUN/p['file']);assert sha(RUN/p['file'])==p['sha256'];updates[r['id']]=p
    history=read(ART/'generation_history.json')
    history.extend({**r,'supersededByBatch':'20261114c','archiveStatus':'HELD_SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in records if r['id'] in ids)
    save(ART/'generation_history.json',history);save(ART/'generation_records.json',[replacements.get(r['id'],r) for r in records])
    structure['pages']=[updates.get(p['id'],p) for p in structure['pages']];save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    registration=read(ART/'body_registration_20261114c.json')
    for e in registration['entries']:e['source']=e['source'].replace('Candidates_20261114c/','Sheets/')
    save(ART/'body_registration_20261114c.json',registration)
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json');coverage.update(productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage);save(EV/'reference_delivery_audit.json',dict(relocatedReferences=relocations,allByteIdentical=True))
    save(ART/'candidate_20261114c_receipt.json',dict(batch='20261114c',selected=8,sourceCells=128,generatedVariants=m['generatedVariants'],sourceReviewPending=True,newSourceApprovals=0,fullGameComplete=False,note='Eight held bindings replaced for preview. Prior holds stay active until source/native review. All277previouspins unchanged.'))
    print(json.dumps(dict(repairPreviews=8,sourceCells=128,unchangedSourcePins=277,pages=324,newApprovals=0)))
