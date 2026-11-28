"""Preview 29 new IDs and two explicitly held repairs; no automatic approvals."""
import hashlib,json,shutil,subprocess
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,covers
BATCH='20261114f'
REPAIRS={'class_huyen_but_skill_01_ne','class_huyen_but_skill_02_ne'}

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def promote():
    records=read(ART/'generation_records.json');assert not any(r.get('batch')==BATCH for r in records),'Already promoted'
    m=read(ART/('Candidates_'+BATCH+'/candidate_manifest.json'));selected=m['records'];assert len(selected)==31 and m['remainingSourcePages']==0
    ids={r['id'] for r in selected};old_ids={r['id'] for r in records};assert len(ids)==31 and ids&old_ids==REPAIRS
    review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json');old={p['id']:p for p in structure['pages']}
    assert len(review['sourceApprovals'])==301 and len(old)==345
    assert not ids&{p['id'] for p in review['sourceApprovals']},'Cannot replace an approved source through this migration'
    assert all(old[i]['visualState']=='HOLD' and not old[i]['productionApproved'] for i in REPAIRS)
    assert sum(bool(r.get('componentOnly')) for r in selected)==9
    for r in selected:
        assert r['batch']==BATCH and r['source'].startswith('Candidates_'+BATCH+'/') and r['prompt'].startswith('Candidates_'+BATCH+'/')
        assert inspect(r)['sourceFrames']==16 and (ART/r['prompt']).is_file()
        if not r.get('componentOnly'):assert r['pivotMode']=='SOURCE_FOOT_PIVOTS'
    for p in old.values():
        if not p.get('legacy'):assert sha(ART/p['source'])==p['sha256']==sha(RUN/p['file'])
    variants=selected+m.get('history',[])
    for r in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):
            assert not (ART/folder/(ART/r[key]).name).exists(),'Destination exists'
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH);ev.mkdir(parents=True,exist_ok=True)
    save(ev/'baseline_preservation.json',dict(previousHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),approvedSourcePins=review['sourceApprovals'],previousPages=len(old),replacedHeldIds=sorted(REPAIRS),replacedHeldPages=[old[i] for i in sorted(REPAIRS)],preservedPages=[dict(id=p['id'],payloadSha256=payload(p)) for p in old.values() if p['id'] not in REPAIRS]))
    for r in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):
            src=ART/r[key];out=ART/folder/src.name
            if key=='source':shutil.copyfile(src,out);assert sha(src)==sha(out)
            else:out.write_text('\n'.join(line.rstrip() for line in src.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
    relocations=[];updates={};replacements={};holds={h['id']:h['reason'] for h in review['holds']}
    for r in variants:
        inputs=[]
        for original in [r['reference']]+r.get('additionalReferences',[]):
            delivered=original.replace('/Candidates_'+BATCH+'/','/Sheets/')
            role='AI_ORIENTATION_GUIDE_NOT_OWNER_APPROVED' if '/Guides_' in delivered else 'OWNER_SELECTED_IDENTITY_REFERENCE' if delivered.endswith('class_huyen_but_idle_v2.png') else 'PREVIOUS_VFX_STYLE_REFERENCE'
            entry=dict(role=role,path=delivered,sourceSha256=sha(ROOT/delivered))
            if delivered!=original:
                assert sha(ROOT/original)==entry['sourceSha256'];entry['generationInputPath']=original;relocations.append(dict(original=original,delivered=delivered,sha256=entry['sourceSha256'],byteIdentical=True))
            inputs.append(entry)
        r.update(generationInputs=inputs,reference=inputs[0]['path'],additionalReferences=[e['path'] for e in inputs[1:]],source='Sheets/'+(ART/r['source']).name,prompt='Prompts/'+(ART/r['prompt']).name)
    for r in selected:
        ident=r['id'];r.update(status='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW',reviewScope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE')
        if ident in REPAIRS:r['replacesSource']=old[ident]['source']
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='HOLD' if ident in REPAIRS else 'AWAITING_VISUAL_REVIEW',visualNotes=holds.get(ident,''))
        shutil.copyfile(ART/r['source'],RUN/p['file']);assert sha(RUN/p['file'])==p['sha256'];updates[ident]=p;replacements[ident]=r
    history=read(ART/'generation_history.json')
    history.extend({**r,'supersededByBatch':BATCH,'archiveStatus':'HELD_SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in records if r['id'] in REPAIRS)
    history.extend({**r,'supersededByBatch':BATCH,'archiveStatus':'SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in m.get('history',[]))
    save(ART/'generation_history.json',history);save(ART/'generation_records.json',[replacements.get(r['id'],r) for r in records]+[r for r in selected if r['id'] not in REPAIRS])
    structure['pages']=[updates.get(p['id'],p) for p in structure['pages'] if not p.get('legacy')]+[updates[i] for i in updates if i not in REPAIRS]+[p for p in structure['pages'] if p.get('legacy')]
    assert len(structure['pages'])==374;save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    for kind in ('body','component'):
        p=ART/(kind+'_registration_'+BATCH+'.json');registration=read(p)
        for e in registration['entries']:e['source']=e['source'].replace('Candidates_'+BATCH+'/','Sheets/')
        save(p,registration)
    jobs=read(ART/'generation_jobs.json');coverage=read(ART/'coverage.json');pending=[j['id'] for j in jobs if not covers(j,structure['pages'])]
    coverage.update(structurePassed=len(structure['pages']),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage);save(ev/'reference_delivery_audit.json',dict(relocatedReferences=relocations,guideReferencesAreNotOwnerApprovals=True,allByteIdentical=True))
    receipt=dict(batch=BATCH,selected=31,sourceCells=496,generatedVariants=m['generatedVariants'],sourceReviewPending=True,newSourceApprovals=0,replacedHeldIds=sorted(REPAIRS),newIds=29,fullGameComplete=False)
    save(ART/('candidate_'+BATCH+'_receipt.json'),receipt);print(json.dumps(receipt))

if __name__=='__main__':promote()
