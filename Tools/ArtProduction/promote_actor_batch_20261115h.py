"""Replace three unapproved G sources for native comparison; never approves art."""
import hashlib,json,shutil,subprocess
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256
BATCH='20261115h';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
IDS={'class_huyen_but_run_n','class_huyen_but_run_e','class_huyen_but_interact_ne'}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def promote():
    records=read(ART/'generation_records.json');assert not any(r.get('batch')==BATCH for r in records),'Already promoted'
    review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json');old={p['id']:p for p in structure['pages']}
    assert len(review['sourceApprovals'])==362 and len(old)==407
    assert all(old[i]['visualState']=='HOLD' and not old[i]['productionApproved'] for i in IDS)
    assert not IDS&{p['id'] for p in review['sourceApprovals']}
    manifest=read(ART/('Candidates_'+BATCH)/'candidate_manifest.json');assert manifest['selected']==3 and manifest['generatedVariants']==6
    selected=[]
    native={v['sourceSha256'] for v in read(EV/'native_media_audit.json')['files']}
    for original in manifest['records']:
        reg=read(EV/'Candidate_Studio'/original['id']/'source_registration.json');r=reg['record']
        assert r['sourceSha256']==original['sourceSha256']==sha(ART/r['source']) and r['sourceSha256'] in native
        assert inspect(r)['sourceFrames']==16;selected.append(r)
    assert {r['id'] for r in selected}==IDS
    save(EV/'baseline_preservation.json',dict(previousHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),approvedSourcePins=review['sourceApprovals'],previousPages=407,replacedHeldIds=sorted(IDS),replacedHeldPages=[old[i] for i in sorted(IDS)],preservedPages=[dict(id=p['id'],payloadSha256=payload(p)) for p in old.values() if p['id'] not in IDS]))
    variants=selected+manifest['history']
    assert len(variants)==6
    for r in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):
            src=ART/r[key];dest=ART/folder/src.name;assert not dest.exists(),'Destination exists'
            if key=='source':shutil.copyfile(src,dest);assert sha(src)==sha(dest)
            else:dest.write_text('\n'.join(s.rstrip() for s in src.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    for r in variants:
        inputs=[]
        for ref in [r['reference']]+r.get('additionalReferences',[]):
            delivered=ref.replace('/Candidates_'+BATCH+'/','/Sheets/')
            role='OWNER_SELECTED_IDENTITY_REFERENCE' if delivered.endswith('class_huyen_but_idle_v2.png') else 'PREVIOUS_REJECTED_CANDIDATE_EDIT_TARGET' if BATCH in delivered else 'PREVIOUS_HELD_SOURCE_EDIT_TARGET'
            entry=dict(path=delivered,sourceSha256=sha(ROOT/delivered),role=role)
            assert sha(ROOT/ref)==entry['sourceSha256']
            if delivered!=ref:entry['generationInputPath']=ref
            inputs.append(entry)
        r.update(generationInputs=inputs,reference=inputs[0]['path'],additionalReferences=[e['path'] for e in inputs[1:]],source='Sheets/'+(ART/r['source']).name,prompt='Prompts/'+(ART/r['prompt']).name)
    replacements={};pages={};holds={h['id']:h['reason'] for h in review['holds']}
    for r in selected:
        r.update(replacesSource=old[r['id']]['source'],status='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW',reviewScope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE')
        page=inspect(r);page.update(bindingSha256=binding_sha256(page),productionApproved=False,visualState='HOLD',visualNotes=holds[r['id']])
        shutil.copyfile(ART/r['source'],RUN/page['file']);assert sha(RUN/page['file'])==page['sha256'];pages[r['id']]=page;replacements[r['id']]=r
    history=read(ART/'generation_history.json')
    history.extend({**r,'supersededByBatch':BATCH,'archiveStatus':'HELD_SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in records if r['id'] in IDS)
    history.extend({**r,'supersededByBatch':BATCH,'archiveStatus':'REJECTED_CANDIDATE_HISTORY_NOT_RENDERED'} for r in manifest['history'])
    save(ART/'generation_history.json',history);save(ART/'generation_records.json',[replacements.get(r['id'],r) for r in records])
    structure['pages']=[pages.get(p['id'],p) for p in structure['pages']];assert len(structure['pages'])==407
    save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    save(ART/('body_registration_'+BATCH+'.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',entries=[dict(id=r['id'],source=r['source'],sourceSha256=r['sourceSha256'],pivotMode=r['pivotMode'],sourceFootPivots=r['sourceFootPivots'],bodyReferenceHeight=r['bodyReferenceHeight']) for r in selected]))
    receipt=dict(batch=BATCH,selected=3,sourceCells=48,generatedVariants=6,sourceReviewPending=True,newSourceApprovals=0,newIds=0,replacedHeldIds=sorted(IDS),fullGameComplete=False)
    save(ART/('candidate_'+BATCH+'_receipt.json'),receipt);print(json.dumps(receipt))
if __name__=='__main__':promote()
