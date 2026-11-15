"""Publish registered body candidates for review, preserving approved sources/jobs."""
import argparse,hashlib,json,shutil,subprocess
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,covers
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):
    pending=p.with_suffix(p.suffix+'.pending');pending.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n');pending.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(v):return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def promote(batch,expected,prior_pins,prior_pages,replacements):
    assert batch.isalnum() and expected>0
    records=read(ART/'generation_records.json');assert not any(r.get('batch')==batch for r in records),'Already promoted'
    review=read(ART/'visual_review.json');structure=read(ART/'structure_report.json');old={p['id']:p for p in structure['pages']}
    assert len(review['sourceApprovals'])==prior_pins and len(old)==prior_pages,'Baseline changed'
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);manifest=read(ART/('Candidates_'+batch)/'candidate_manifest.json');plan=read(ev/'candidate_review_plan.json')
    assert manifest['selected']==plan['selected']==expected and manifest['remainingSourcePages']==0 and manifest['generatedVariants']==expected,'Versioned repairs require explicit history handling'
    media=read(ev/'native_media_audit.json');assert not media['pilot'] and media['selectedVideos']==expected
    captured={m['sourceSha256'] for m in media['files']};assert len(captured)==expected
    selected=[]
    for original in manifest['records']:
        r=read(ev/'Candidate_Studio'/original['id']/'source_registration.json')['record']
        assert not r.get('componentOnly') and r.get('direction') in ('N','NE','E','SE','S')
        assert r['sourceSha256']==original['sourceSha256']==sha(ART/r['source']) and r['sourceSha256'] in captured
        assert inspect(r)['sourceFrames']==16 and (ART/r['prompt']).is_file();selected.append(r)
    ids={r['id'] for r in selected};assert len(ids)==expected and ids&set(old)==set(replacements)
    assert not ids&{p['id'] for p in review['sourceApprovals']},'Approved source replacement forbidden'
    assert all(not old[i]['productionApproved'] for i in replacements)
    jobs=read(ART/'generation_jobs.json');approved_before={j['id'] for j in jobs if covers(j,structure['pages'],True)}
    staged_pages=[]
    for r in selected:
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='AWAITING_VISUAL_REVIEW',visualNotes='');staged_pages.append(p)
    proposed=[next((q for q in staged_pages if q['id']==p['id']),p) for p in structure['pages']]+[p for p in staged_pages if p['id'] not in old]
    assert approved_before<={j['id'] for j in jobs if covers(j,proposed,True)},'Unreviewed replacements would shadow approved jobs'
    owner_report=read(ROOT/'Implementation/Reports/Evidence/Sprite_Studio_20261112/sprite_restore_audit.json');owners={o['file'] for o in owner_report['files']}
    for o in owner_report['files']:assert sha(ROOT/o['file'])==o['expectedSha256']
    for r in selected:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):assert not (ART/folder/(ART/r[key]).name).exists(),'Destination exists'
        for ref in [r['reference']]+r.get('additionalReferences',[]):assert (ROOT/ref).resolve().is_relative_to(ROOT.resolve()) and (ROOT/ref).is_file()
    save(ev/'baseline_preservation.json',dict(previousHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),approvedSourcePins=review['sourceApprovals'],previousPages=prior_pages,replacedUnapprovedIds=sorted(replacements),replacedUnapprovedPages=[old[i] for i in sorted(replacements)],preservedPages=[dict(id=p['id'],payloadSha256=payload(p)) for p in structure['pages'] if p['id'] not in replacements],approvedJobsBefore=sorted(approved_before)))
    source_map=[];updates={};new_records={};pinned_hashes={p['sourceSha256'] for p in review['sourceApprovals']}
    for r in selected:
        captured_source=r['source'];source=ART/captured_source;dest=ART/'Sheets'/source.name;shutil.copyfile(source,dest);assert sha(dest)==r['sourceSha256']
        prompt=ART/r['prompt'];out=ART/'Prompts'/prompt.name;out.write_text(prompt.read_text(encoding='utf8').rstrip()+'\n',encoding='utf8',newline='\n')
        inputs=[]
        for ref in [r['reference']]+r.get('additionalReferences',[]):
            digest=sha(ROOT/ref);role='AI_ORIENTATION_GUIDE_NOT_OWNER_APPROVED' if '/Guides_' in ref else 'OWNER_SELECTED_IDENTITY_REFERENCE' if ref in owners else 'PREVIOUS_REVIEWED_SOURCE_REFERENCE' if digest in pinned_hashes else 'UNAPPROVED_SOURCE_REFERENCE'
            inputs.append(dict(path=ref,sourceSha256=digest,role=role))
        r.update(source='Sheets/'+dest.name,prompt='Prompts/'+out.name,generationInputs=inputs,status='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW',reviewScope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE')
        if r['id'] in replacements:r['replacesSource']=old[r['id']]['source']
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState='AWAITING_VISUAL_REVIEW',visualNotes='');shutil.copyfile(dest,RUN/p['file']);assert sha(RUN/p['file'])==p['sha256']
        updates[r['id']]=p;new_records[r['id']]=r;source_map.append(dict(id=r['id'],capturedSource=captured_source,deliveredSource=r['source'],sourceSha256=r['sourceSha256'],byteIdentical=True))
    history=read(ART/'generation_history.json');history.extend({**r,'supersededByBatch':batch,'archiveStatus':'UNAPPROVED_SOURCE_REPAIR_HISTORY_NOT_RENDERED'} for r in records if r['id'] in replacements)
    save(ART/'generation_history.json',history);save(ART/'generation_records.json',[new_records.get(r['id'],r) for r in records]+[r for r in selected if r['id'] not in old])
    structure['pages']=[updates.get(p['id'],p) for p in structure['pages']]+[updates[i] for i in updates if i not in old]
    # The inspector emits all authored pages first, then the three legacy clips.
    # Keep that deterministic order when adding candidates to an existing library.
    structure['pages']=[p for p in structure['pages'] if not p.get('legacy')]+[p for p in structure['pages'] if p.get('legacy')]
    assert len(structure['pages'])==prior_pages+expected-len(replacements)
    save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    registration=read(ART/('body_registration_'+batch+'.json'));save(ev/'registration_before_delivery.json',registration)
    for entry in registration['entries']:
        entry['record']=new_records[entry['record']['id']];entry['page']=updates[entry['record']['id']]
    save(ART/('body_registration_'+batch+'.json'),registration)
    coverage=read(ART/'coverage.json');pending=[j['id'] for j in jobs if not covers(j,structure['pages'])]
    coverage.update(structurePassed=len(structure['pages']),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
    save(ART/'coverage.json',coverage);save(ev/'source_delivery_map.json',dict(entries=source_map,allByteIdentical=True))
    receipt=dict(batch=batch,selected=expected,sourceCells=expected*16,generatedVariants=expected,sourceReviewPending=True,newSourceApprovals=0,newIds=expected-len(replacements),replacedUnapprovedIds=sorted(replacements),fullGameComplete=False)
    save(ART/('candidate_'+batch+'_receipt.json'),receipt);print(json.dumps(receipt))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--expected',type=int,required=True);p.add_argument('--prior-pins',type=int,required=True);p.add_argument('--prior-pages',type=int,required=True);p.add_argument('--replace',action='append',default=[]);a=p.parse_args();promote(a.batch,a.expected,a.prior_pins,a.prior_pages,a.replace)
