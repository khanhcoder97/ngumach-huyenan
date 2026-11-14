"""Refine only unapproved F registration after native pilot observations."""
import json
from PIL import Image
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256
from calibrate_huyen_but_20261114f import cool_boot_x,component_registration

def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

if __name__=='__main__':
    records=read(ART/'generation_records.json');structure=read(ART/'structure_report.json');pages={p['id']:p for p in structure['pages']}
    review=read(ART/'visual_review.json');assert len(review['sourceApprovals'])==301
    body=read(ART/'body_registration_20261114f.json');components=read(ART/'component_registration_20261114f.json');regs={e['id']:e for doc in (body,components) for e in doc['entries']};changed=[]
    for r in [r for r in records if r.get('batch')=='20261114f']:
        old=pages[r['id']];assert not old['productionApproved'] and not any(p['id']==r['id'] for p in review['sourceApprovals'])
        frames=old['directions'][0]['frames'];e=regs[r['id']]
        with Image.open(ART/r['source']) as image:
            if r.get('direction'):
                moving='_skill_05_' in r['id'];offset=None
                for n,f in enumerate(frames):
                    x,y,w,h=f['rect'];region=image.crop((x,y,x+w,y+h));head=e['headLandmarks'][n]
                    boot=cool_boot_x(region,head,r['sourceFootPivots'][n][1])
                    if offset is None:offset=boot-head['centerX']
                    r['sourceFootPivots'][n][0]=head['centerX']+offset if moving else boot
                e.update(method='NEUTRAL_HEAD_PROJECTION_X_COOL_BOOT_BASELINE_Y' if moving else 'CENTRAL_COOL_BOOT_BASELINE_XY',sourcePivots=r['sourceFootPivots'])
            else:
                mode,pivots,method=component_registration(r['id'],frames,image);r['pivotMode']=mode;r.pop('sourcePivots',None)
                if pivots:r['sourcePivots']=pivots
                e.update(method=method,pivotMode=mode,sourcePivots=pivots)
        p=inspect(r);p.update(bindingSha256=binding_sha256(p),productionApproved=False,visualState=old['visualState'],visualNotes=old['visualNotes'])
        if p['bindingSha256']!=old['bindingSha256']:changed.append(dict(id=r['id'],oldBinding=old['bindingSha256'],newBinding=p['bindingSha256'],method=e['method']))
        pages[r['id']]=p
    save(ART/'generation_records.json',records);save(ART/'body_registration_20261114f.json',body);save(ART/'component_registration_20261114f.json',components)
    structure['pages']=[pages[p['id']] for p in structure['pages']];save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']))
    ev=ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114f';report=ev/'native_registration_refinement.json';previous=read(report) if report.exists() else None
    runs=(previous.get('runs',[dict(changed=previous['changed'])]) if previous else [])+[dict(changed=changed)]
    save(report,dict(scope='UNAPPROVED_REGISTRATION_REFINEMENT_NOT_RASTER_EDIT_OR_APPROVAL',changed=changed,runs=runs,priorSourcePinsUnchanged=301))
    print(json.dumps(dict(changed=len(changed),sourceApprovals=0,sourcePins=301)))
