"""Record the completed source/native visual review. One-time guarded I migration."""
import hashlib,json
from pathlib import Path
from inspect_actor_library import binding_sha256,covers
ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';RUN=ROOT/'ClientGodot/assets/actor_library_v1';EV=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261113i'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
review=read(ART/'visual_review.json');assert len(review['sourceApprovals'])==215,'One-time reviewed selection already recorded or baseline changed'
records=read(ART/'generation_records.json');structure=read(ART/'structure_report.json');pages={p['id']:p for p in structure['pages']}
selected=[r for r in records if r.get('batch')=='20261113i'];assert len(selected)==15
prefix='Implementation/Reports/Evidence/Actor_Batch_20261113i/';entries=[]
for r in selected:
 p=pages[r['id']];assert hashlib.sha256((ART/r['source']).read_bytes()).hexdigest()==p['sha256'] and binding_sha256(p)==p['bindingSha256']
 clip='basic_attack' if '_basic_attack_' in r['id'] else 'walk' if '_walk_' in r['id'] else 'idle'
 direction=r['direction'].lower();approved=r['id']!='class_anh_dao_walk_e'
 evidence=[prefix+clip+'_raw_'+direction+'.mp4',prefix+clip+'_raw_'+direction+'_samples.png',prefix+clip+'_eight_angles.mp4',prefix+clip+'_eight_angles_samples.png',prefix+'locomotion_chain.mp4',prefix+'locomotion_chain_samples.png']
 assert all((ROOT/f).is_file() for f in evidence)
 note=('One quiet breath and held low dao; clean loop.' if clip=='idle' else 'One low forehand with low recovery, secure right-hand grip; combo stage1 only.' if clip=='basic_attack' else 'Opposite contact/leg overlap at0/8 and passing phases; selected repaired source where needed. E/W excluded.' if approved else 'HOLD: E near/far contact/overlap at0/8 not convincingly opposite; mirroredW inherits hold.')
 entry=dict(id=r['id'],sourceSha256=p['sha256'],bindingSha256=p['bindingSha256'],reviewedSourceFrames=16,productionApproved=approved,sourceSheet='Art_Source/Actor_Library_20261107/'+r['source'],nativeEvidence=evidence,nativeReviewed=True,visualNotes=note)
 entries.append(entry)
 if approved:
  review['productionApproved'].append(r['id'])
  pin={k:v for k,v in entry.items() if k not in ('productionApproved','nativeReviewed','visualNotes')}
  pin.update(scope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE',evidence=evidence[2],method='Viewed complete original16pose sheet and native Godot point-filtered temporal captures. Checked identity/camera/held dao, single breath/one strike or alternate gait contact, neutral-head scale, boot registration, source timing and phase transitions. Original RGBA unchanged.',reviewScale='88px library;100px locomotion chain;Studio whole-clip fit',batch='20261113i',reviewDate='2026-11-13')
  review['sourceApprovals'].append(pin);p.update(productionApproved=True,visualState='APPROVED',visualNotes='')
  r['status']='SOURCE_NATIVE_VISUAL_REVIEWED'
 else:
  assert not p['productionApproved'] and p['visualState']=='HOLD';r['status']='SOURCE_NATIVE_REVIEW_HOLD';r['gaitReviewNote']=note
save(ART/'generation_records.json',records);save(ART/'visual_review.json',review)
save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
coverage=read(ART/'coverage.json');jobs=read(ART/'generation_jobs.json')
coverage['productionApprovedPages']=sum(covers(j,structure['pages'],True) for j in jobs);save(ART/'coverage.json',coverage)
receipt=read(ART/'candidate_20261113i_receipt.json');receipt.update(sourceReviewPending=False,newSourceApprovals=14,newSourceHolds=1,nativeReview='Implementation/Reports/Evidence/Actor_Batch_20261113i/source_native_review.json');save(ART/'candidate_20261113i_receipt.json',receipt)
save(EV/'source_native_review.json',dict(batch='20261113i',scope='SOURCE_CLIP_VISUAL_REVIEW_NOT_GAMEPLAY_ACCEPTANCE',approved=14,held=1,entries=entries,notes='Temporal sample captures supplement full original sheet review; source-pose visitation checked separately at60steps. No real-time FPS acceptance. E/W walk hold remains.'))
print('REVIEW_RECORDED priorPins=215 newPins=14 totalPins=229 approvedJobs='+str(coverage['productionApprovedPages']))
