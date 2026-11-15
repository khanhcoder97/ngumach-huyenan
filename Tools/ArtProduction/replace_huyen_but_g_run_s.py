"""Replace one unapproved G source after contact/costume trials; no raster editing."""
import copy,hashlib,json,shutil
from PIL import Image
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256,binary_projection
from calibrate_huyen_but_20261114g import boot_root
from calibrate_huyen_but_20261114f import gutter_edges
from calibrate_anh_dao_mobility import head_landmark

ID='class_huyen_but_run_s';BATCH='20261114g'
def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def replace():
    records=read(ART/'generation_records.json');structure=read(ART/'structure_report.json');review=read(ART/'visual_review.json')
    previous=next(r for r in records if r['id']==ID);old=next(p for p in structure['pages'] if p['id']==ID)
    assert len(review['sourceApprovals'])==329 and not old['productionApproved']
    assert previous['source'].endswith('_v1_20261114g.png'),'One-time unapproved repair guard'
    manifest=read(ART/'Candidates_20261114g/candidate_manifest.json');candidate=copy.deepcopy(next(r for r in manifest['records'] if r['id']==ID))
    assert candidate['source'].endswith('_v3_20261114g.png')
    variants=[copy.deepcopy(r) for r in manifest['history'] if r['id']==ID]+[candidate]
    assert len(variants)==3
    for record in variants:
        for key,folder in (('source','Sheets'),('prompt','Prompts')):
            original=ART/record[key];target=ART/folder/original.name
            if target.exists():assert sha(original)==sha(target)
            else:shutil.copyfile(original,target)
            record[key]=folder+'/'+target.name
        inputs=[]
        for path in [record['reference']]+record.get('additionalReferences',[]):
            delivered=path.replace('/Candidates_20261114g/','/Sheets/')
            assert sha(ROOT/path)==sha(ROOT/delivered)
            role='OWNER_SELECTED_IDENTITY_REFERENCE' if delivered.endswith('class_huyen_but_idle_v2.png') else 'EDIT_TARGET_PREVIOUS_REJECTED_GAIT' if 'huyen_but_run_s_v2_' in delivered else 'OTHER_CLASS_GAIT_CHOREOGRAPHY_NOT_IDENTITY'
            inputs.append(dict(path=delivered,sourceSha256=sha(ROOT/delivered),role=role,generationInputPath=path))
        record.update(reference=inputs[0]['path'],additionalReferences=[x['path'] for x in inputs[1:]],generationInputs=inputs)
    candidate=variants[-1]
    with Image.open(ART/candidate['source']) as image:
        try:raw=inspect(candidate)
        except AssertionError as error:
            assert 'clipped/overlapping' in str(error)
            xs,ys=binary_projection(image.getchannel('A').point(lambda a:255 if a>=200 else 0));candidate['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));raw=inspect(candidate)
        pivots=[];heads=[];neutral=None;offset=None
        for frame in raw['directions'][0]['frames']:
            x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,frame['bounds']);heads.append(head)
            boot_x,ground,low=boot_root(region,head,frame['bounds'][3]-head['top'] if neutral is None else neutral,True)
            if neutral is None:neutral=ground-head['top'];offset=boot_x-head['centerX']
            pivots.append([head['centerX']+offset,ground])
    candidate.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral,registrationCalibration='Art_Source/Actor_Library_20261107/body_registration_20261114g.json',status='SOURCE_GEOMETRY_READY_PENDING_NATIVE_REVIEW',replacesSource=previous['source'],reviewScope='SOURCE_VISUAL_CLIP_REVIEW_NOT_ACTOR_OR_GAMEPLAY_ACCEPTANCE')
    page=inspect(candidate);page.update(bindingSha256=binding_sha256(page),productionApproved=False,visualState='AWAITING_VISUAL_REVIEW',visualNotes='New v3 contact/costume repair requires current native review; v1 contact HOLD notes are historical only.')
    shutil.copyfile(ART/candidate['source'],RUN/page['file']);assert sha(RUN/page['file'])==page['sha256']
    history=read(ART/'generation_history.json')
    for record in variants[:-1]:
        assert not any(r['source']==record['source'] for r in history)
        history.append({**record,'supersededByBatch':BATCH,'archiveStatus':'RUN_CONTACT_OR_COSTUME_TRIAL_NOT_RENDERED'})
    records=[candidate if r['id']==ID else r for r in records];structure['pages']=[page if p['id']==ID else p for p in structure['pages']]
    registration=read(ART/'body_registration_20261114g.json');entry=next(e for e in registration['entries'] if e['id']==ID)
    entry.update(source=candidate['source'],sourceSha256=page['sha256'],method='NEUTRAL_HEAD_PROJECTED_X_COOL_BOOT_BASELINE_Y',sourcePivots=pivots,bodyReferenceHeight=neutral,headLandmarks=heads,gridEdges=candidate.get('gridEdges'))
    save(ART/'generation_records.json',records);save(ART/'generation_history.json',history);save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']));save(ART/'body_registration_20261114g.json',registration)
    receipt=read(ART/'candidate_20261114g_receipt.json');receipt.update(generatedVariants=manifest['generatedVariants'],sourceReviewPending=True);save(ART/'candidate_20261114g_receipt.json',receipt)
    save(ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g/run_s_replacement.json',dict(id=ID,oldSource=previous['source'],oldSha256=old['sha256'],newSource=candidate['source'],newSha256=page['sha256'],oldBinding=old['bindingSha256'],newBinding=page['bindingSha256'],sourcePinsUnchanged=329,productionApprovals=0,generatedVariants=manifest['generatedVariants']))
    print(json.dumps(dict(replacedUnapprovedSource=ID,generatedVariants=manifest['generatedVariants'],sourceApprovals=0,nativeRecaptureRequired=True)))

if __name__=='__main__':replace()
