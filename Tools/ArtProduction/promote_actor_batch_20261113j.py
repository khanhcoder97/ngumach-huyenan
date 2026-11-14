"""One-time J source promotion and incremental preview export, without approval."""
import hashlib,json,shutil
from pathlib import Path
from inspect_actor_library import inspect,binding_sha256,covers
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';RUN=ROOT/'ClientGodot/assets/actor_library_v1';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113j'
EV.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=read(ART/'generation_records.json');assert not any(r.get('batch')=='20261113j' for r in records),'Already promoted'
review=read(ART/'visual_review.json');assert len(review['sourceApprovals'])==229
m=read(ART/'Candidates_20261113j/candidate_manifest.json');assert len(m['records'])==21 and m['remainingSourcePages']==0
structure=read(ART/'structure_report.json');old_pages={p['id']:p for p in structure['pages']};replacement='class_anh_dao_walk_e'
for p in structure['pages']:
 if not p.get('legacy'):assert sha(ART/p['source'])==p['sha256'] and sha(RUN/p['file'])==p['sha256'],'prior source changed'
baseline=dict(previousHead='83272654b2a2e9ef46ac3fb200a34f37b5eddd91',approvedSourcePins=review['sourceApprovals'],replacedUnapprovedIds=[replacement],
              preservedPages=[dict(id=p['id'],payloadSha256=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()) for p in structure['pages'] if p['id']!=replacement],
              previousPages=len(structure['pages']))
save(EV/'baseline_preservation.json',baseline)
for ext,target in (('png','Sheets'),('txt','Prompts')):
 for p in (ART/'Candidates_20261113j').glob('*.'+ext):
  out=ART/target/p.name;assert not out.exists()
  if ext=='png':shutil.copyfile(p,out);assert sha(p)==sha(out)
  else:out.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
audits=[]
def normalize(r):
 inputs=[r['reference']]+r.get('additionalReferences',[]);r['generationInputs']=[]
 for i,p in enumerate(inputs):
  delivered=p.replace('/Candidates_20261113j/','/Sheets/');assert (ROOT/delivered).is_file()
  entry=dict(role=r.get('inputRole','IDENTITY_REFERENCE') if i==0 else 'SUPPORTING_REFERENCE',path=delivered,sourceSha256=sha(ROOT/delivered))
  if delivered!=p:
   assert sha(ROOT/p)==entry['sourceSha256'];entry['generationInputPath']=p;audits.append(dict(original=p,delivered=delivered,sha256=entry['sourceSha256'],byteIdentical=True))
  r['generationInputs'].append(entry)
 r['reference']=r['generationInputs'][0]['path'];r['additionalReferences']=[x['path'] for x in r['generationInputs'][1:]]
 r['referenceRelocations']=[dict(generationInputPath=x['generationInputPath'],deliveredPath=x['path'],sourceSha256=x['sourceSha256']) for x in r['generationInputs'] if 'generationInputPath' in x]
 r['source']=r['source'].replace('Candidates_20261113j/','Sheets/');r['prompt']=r['prompt'].replace('Candidates_20261113j/','Prompts/')
 if 'replacesSource' in r:r['replacesSource']=r['replacesSource'].replace('Candidates_20261113j/','Sheets/')
for r in m['records']:
 normalize(r);r['status']='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW';r['reviewScope']='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE'
selected={r['id']:r for r in m['records']};ordered=[]
history=read(ART/'generation_history.json')
for r in records:
 if r['id']==replacement:
  history.append({**r,'supersededByBatch':'20261113j','archiveStatus':'HELD_SOURCE_PRESERVED_NOT_RENDERED','reason':'New E gait source ready for native review; do not transfer old source approval or clear HOLD before review.'})
  ordered.append(selected[replacement])
 else:ordered.append(r)
for clip in ('run','basic_attack_02','basic_attack_03','interact'):
 ordered.extend(selected['class_anh_dao_'+clip+'_'+d] for d in ('n','ne','e','se','s'))
assert len({r['id'] for r in ordered})==len(ordered)
for r in m['history']:
 if 'reference' not in r:r['reference']='Art_Source/Actor_Library_20261107/Sheets/class_anh_dao_idle_se_v1_20261113i.png'
 normalize(r);history.append({**r,'supersededByBatch':'20261113j','archiveStatus':'SOURCE_REPAIR_HISTORY_NOT_RENDERED'})
for hold in review['holds']:
 if hold['id']==replacement:hold['reason']='New J E gait replaces held I source. Near/far boot position0/8 and passing4/12 require native review; E and mirroredW remain HOLD.'
save(ART/'generation_records.json',ordered);save(ART/'generation_history.json',history);save(ART/'visual_review.json',review)
registration=read(ART/'body_registration_20261113j.json')
for e in registration['entries']:e['source']=e['source'].replace('Candidates_20261113j/','Sheets/')
save(ART/'body_registration_20261113j.json',registration)
for r in m['records']:
 p=inspect(r);p['bindingSha256']=binding_sha256(p);p['productionApproved']=False
 p['visualState']='HOLD' if p['id']==replacement else 'AWAITING_VISUAL_REVIEW'
 p['visualNotes']=next((h['reason'] for h in review['holds'] if h['id']==p['id']),'')
 old_pages[p['id']]=p;shutil.copyfile(ART/r['source'],RUN/p['file']);assert sha(RUN/p['file'])==p['sha256']
structure['pages']=[old_pages[r['id']] for r in ordered if r['id'] in old_pages]+[p for p in structure['pages'] if p.get('legacy')]
assert len(structure['pages'])==289
save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json');pending=[j['id'] for j in jobs if not covers(j,structure['pages'])]
coverage.update(structurePassed=len(structure['pages']),boundRequiredPages=len(jobs)-len(pending),pendingPages=len(pending),pendingIds=pending,
                productionApprovedPages=sum(covers(j,structure['pages'],True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in structure['pages']))
save(ART/'coverage.json',coverage)
save(EV/'reference_delivery_audit.json',dict(generationInputsRetained=True,relocatedReferences=audits,allByteIdentical=True))
save(ART/'candidate_20261113j_receipt.json',dict(batch='20261113j',selected=21,sourceCells=336,generatedVariants=m['generatedVariants'],unselectedVariants=len(m['history']),newSourceApprovals=0,sourceReviewPending=True,fullGameComplete=False,heldIds=[replacement],note='Incremental preview export retains all268 unaffected prior page payloads. Final full inspector recomputation required after native review.'))
print('J_PROMOTED_PREVIEW pages=21 poses=336 previousPins=229 unchanged; libraryPages=289 jobsBound='+str(coverage['boundRequiredPages'])+' pending='+str(coverage['pendingPages']))
