"""Promote original I candidates for native review; never approves a source."""
import hashlib,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113i'
EV.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=read(ART/'Candidates_20261113i/candidate_manifest.json');assert len(m['records'])==15 and len(m['history'])==4
records=read(ART/'generation_records.json');review=read(ART/'visual_review.json');history=read(ART/'generation_history.json')
assert not any(r.get('batch')=='20261113i' for r in records),'Already promoted; do not rerun.'
old_ids={'class_anh_dao_idle','class_anh_dao_walk','class_anh_dao_basic_attack'}
assert not old_ids.intersection(review['productionApproved'])
baseline=read(ART/'structure_report.json')['pages'];keep=[p for p in baseline if p['id'] not in old_ids]
save(EV/'baseline_preservation.json',dict(previousHead='b2fe592a26a915c95b0cf0e15647779570e467f9',approvedSourcePins=review['sourceApprovals'],preservedPages=[dict(id=p['id'],payloadSha256=hashlib.sha256(json.dumps(p,sort_keys=True,separators=(',',':')).encode()).hexdigest()) for p in keep],archivedIds=sorted(old_ids)))
for ext,target in (('png','Sheets'),('txt','Prompts')):
 for p in (ART/'Candidates_20261113i').glob('*.'+ext):
  out=ART/target/p.name;assert not out.exists()
  if ext=='png':shutil.copyfile(p,out);assert sha(p)==sha(out)
  else:out.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf8').splitlines())+'\n',encoding='utf8')
def relocation(p):
 return p.replace('/Candidates_20261113i/','/Sheets/')
audits=[]
for r in m['records']:
 sources=[r['reference']]+r.get('additionalReferences',[])
 r['generationInputs']=[]
 for i,p in enumerate(sources):
  delivered=relocation(p);assert (ROOT/delivered).is_file()
  item=dict(role=r.get('inputRole','REFERENCE') if i==0 else 'SUPPORTING_REFERENCE',path=delivered,sourceSha256=sha(ROOT/delivered))
  if delivered!=p:
   assert sha(ROOT/p)==item['sourceSha256'];item['generationInputPath']=p
   audits.append(dict(original=p,delivered=delivered,sha256=item['sourceSha256'],byteIdentical=True))
  r['generationInputs'].append(item)
 r['reference']=r['generationInputs'][0]['path'];r['additionalReferences']=[x['path'] for x in r['generationInputs'][1:]]
 r['referenceRelocations']=[dict(generationInputPath=x['generationInputPath'],deliveredPath=x['path'],sourceSha256=x['sourceSha256']) for x in r['generationInputs'] if 'generationInputPath' in x]
 r['source']=r['source'].replace('Candidates_20261113i/','Sheets/')
 r['prompt']=r['prompt'].replace('Candidates_20261113i/','Prompts/')
 if 'replacesSource' in r:r['replacesSource']=r['replacesSource'].replace('Candidates_20261113i/','Sheets/')
 r['status']='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW';r['reviewScope']='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE'
 if '_basic_attack_' in r['id']:r['comboStage']=1;r['combatAuthority']='PRESENTATION_ONLY_SERVER_OWNS_HIT_INDEX_AND_OUTCOMES'
for r in records:
 if r['id'] in old_ids:history.append({**r,'reason':'Replace unapproved whole base atlas with armed five-angle I sources; old PNG/prompt bytes retained.','supersededByBatch':'20261113i','archiveStatus':'UNAPPROVED_SOURCE_PRESERVED_NOT_RENDERED'})
selected_by_id={r['id']:r for r in m['records']};ordered=[]
for r in records:
 if r['id'] in old_ids:ordered.extend(selected_by_id[r['id']+'_'+d] for d in ('n','ne','e','se','s'))
 else:ordered.append(r)
records=ordered
for r in m['history']:
 history.append({**r,'source':r['source'].replace('Candidates_20261113i/','Sheets/'),'prompt':r['prompt'].replace('Candidates_20261113i/','Prompts/'),'supersededByBatch':'20261113i','archiveStatus':'GAIT_REPAIR_HISTORY_NOT_RENDERED'})
review['holds'].append(dict(id='class_anh_dao_walk_e',reason='Near/far leg support and boot overlap do not clearly reverse between source0 and8; repeated half-cycle suspected. Native review only; E and mirroredW blocked from approved renderer.'))
registration=read(ART/'body_registration_20261113i.json')
for e in registration['entries']:e['source']=e['source'].replace('Candidates_20261113i/','Sheets/')
save(ART/'body_registration_20261113i.json',registration)
save(ART/'generation_records.json',records);save(ART/'generation_history.json',history);save(ART/'visual_review.json',review)
save(EV/'reference_delivery_audit.json',dict(generationInputsRetained=True,relocatedReferences=audits,allByteIdentical=True))
save(ART/'candidate_20261113i_receipt.json',dict(batch='20261113i',selected=15,sourceCells=240,generatedVariants=19,unselectedVariants=4,fullGameComplete=False,sourceReviewPending=True,holds=['class_anh_dao_walk_e'],note='Native review and source pinning required; complete16frame geometry is not motion approval.'))
print('PROMOTED_FOR_REVIEW selected=15 sourceCells=240 historicalVariants=4 priorPins=215 unchanged')
