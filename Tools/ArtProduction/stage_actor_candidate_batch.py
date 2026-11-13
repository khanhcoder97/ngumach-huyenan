"""Stage new IDs for source/native preview without granting production approval."""
import argparse,hashlib,json,shutil,subprocess
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,covers
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def stage(batch,expected):
    assert batch.isalnum() and expected>0
    records=read(ART/'generation_records.json');assert not any(r.get('batch')==batch for r in records),'Already staged'
    m=read(ART/('Candidates_'+batch+'/candidate_manifest.json'));selected=m['records'];assert len(selected)==expected and m['remainingSourcePages']==0
    assert not ({r['id'] for r in selected}&{r['id'] for r in records}),'Held/approved replacements require a separate migration'
    for r in selected:
        assert r['batch']==batch and r['source'].startswith('Candidates_'+batch+'/') and r['prompt'].startswith('Candidates_'+batch+'/')
        assert inspect(r)['sourceFrames']==16 and (ART/r['prompt']).is_file()
    review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json')
    for p in structure['pages']:
        if not p.get('legacy'):assert sha(ART/p['source'])==p['sha256']==sha(RUN/p['file'])
    # Validate every destination before making any file copy.
    variants=selected+m.get('history',[])
    for r in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):assert not (ART/folder/(ART/r[key]).name).exists(),'Destination exists'
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);ev.mkdir(parents=True,exist_ok=True)
    save(ev/'baseline_preservation.json',dict(previousHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        approvedSourcePins=review['sourceApprovals'],previousPages=len(structure['pages']),
        preservedPages=[dict(id=p['id'],payloadSha256=payload(p)) for p in structure['pages']]))
    relocations=[]
    for r in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):
            src=ART/r[key];out=ART/folder/src.name
            if key=='source':shutil.copyfile(src,out);assert sha(src)==sha(out)
            else:out.write_text('\n'.join(line.rstrip() for line in src.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    for r in variants:
        r['generationInputs']=[]
        for i,original in enumerate([r['reference']]+r.get('additionalReferences',[])):
            delivered=original.replace('/Candidates_'+batch+'/','/Sheets/');e=dict(role=r.get('inputRole','IDENTITY_REFERENCE') if i==0 else 'SUPPORTING_REFERENCE',path=delivered,sourceSha256=sha(ROOT/delivered))
            if delivered!=original:
                assert sha(ROOT/original)==e['sourceSha256'];e['generationInputPath']=original;relocations.append(dict(original=original,delivered=delivered,sha256=e['sourceSha256'],byteIdentical=True))
            r['generationInputs'].append(e)
        r['reference']=r['generationInputs'][0]['path'];r['additionalReferences']=[e['path'] for e in r['generationInputs'][1:]]
        r['source']='Sheets/'+(ART/r['source']).name;r['prompt']='Prompts/'+(ART/r['prompt']).name
    pages=[]
    for r in selected:
        r['status']='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW';r['reviewScope']='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE'
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='AWAITING_VISUAL_REVIEW',visualNotes='')
        shutil.copyfile(ART/r['source'],RUN/p['file']);assert sha(RUN/p['file'])==p['sha256'];pages.append(p)
    history=read(ART/'generation_history.json');history.extend({**r,'supersededByBatch':batch,'archiveStatus':'SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in m.get('history',[]))
    save(ART/'generation_history.json',history);save(ART/'generation_records.json',records+selected)
    structure['pages']=[p for p in structure['pages'] if not p.get('legacy')]+pages+[p for p in structure['pages'] if p.get('legacy')]
    save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    cal=ART/('component_registration_'+batch+'.json')
    if cal.is_file():
        registration=read(cal)
        for e in registration['entries']:e['source']=e['source'].replace('Candidates_'+batch+'/','Sheets/')
        save(cal,registration)
    coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json');pending=[j['id'] for j in jobs if not covers(j,structure['pages'])]
    coverage.update(structurePassed=len(structure['pages']),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,
        productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage);save(ev/'reference_delivery_audit.json',dict(relocatedReferences=relocations,allByteIdentical=True))
    receipt=dict(batch=batch,selected=len(selected),sourceCells=16*len(selected),generatedVariants=m['generatedVariants'],sourceReviewPending=True,newSourceApprovals=0,fullGameComplete=False)
    save(ART/('candidate_'+batch+'_receipt.json'),receipt);return receipt

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--expected-pages',type=int,required=True);a=p.parse_args();print(json.dumps(stage(a.batch,a.expected_pages)))
