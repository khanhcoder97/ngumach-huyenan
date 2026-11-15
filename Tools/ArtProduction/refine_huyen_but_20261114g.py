"""Correct a semantic row boundary found in the pilot; original PNG bytes immutable."""
import hashlib,json
from PIL import Image
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256
from calibrate_huyen_but_20261114f import component_registration

def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def refine():
    records=read(ART/'generation_records.json');structure=read(ART/'structure_report.json');review=read(ART/'visual_review.json')
    assert len(review['sourceApprovals'])==329
    record=next(r for r in records if r['id']=='sk_hb_06_expire_component');assert record['batch']=='20261114g'
    page=next(p for p in structure['pages'] if p['id']==record['id']);assert not page['productionApproved']
    assert record['gridEdges']['rows']==[0,397,633,991,1246],'One-time pilot refinement guard'
    original_sha=page['sha256'];old_binding=page['bindingSha256']
    # 939..956 is the TOP node of row3, not an extra ending bead of row2.
    # 876 lies in the empty solid-core gap813..939 between the complete triangles.
    record['gridEdges']['rows']=[0,397,633,876,1246]
    record.pop('sourcePivots',None);record['pivotMode']='CELL_CENTER'
    raw=inspect(record)
    with Image.open(ART/record['source']) as image:
        mode,pivots,method=component_registration('sk_hb_04_expire_component',raw['directions'][0]['frames'],image)
    record.update(pivotMode=mode,sourcePivots=pivots,semanticGridReview='MANUAL_COMPLETE_THREE_NODE_TRIANGLES_ROW_BOUNDARY876')
    updated=inspect(record);updated.update(bindingSha256=binding_sha256(updated),productionApproved=False,visualState=page['visualState'],visualNotes=page['visualNotes'])
    assert updated['sha256']==original_sha==hashlib.sha256((RUN/updated['file']).read_bytes()).hexdigest()
    structure['pages']=[updated if p['id']==updated['id'] else p for p in structure['pages']]
    registration=read(ART/'component_registration_20261114g.json');entry=next(e for e in registration['entries'] if e['id']==record['id'])
    entry.update(sourcePivots=pivots,gridEdges=record['gridEdges'],method=method,semanticGridReview=record['semanticGridReview'])
    save(ART/'generation_records.json',records);save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']));save(ART/'component_registration_20261114g.json',registration)
    save(ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g/native_registration_refinement.json',dict(id=record['id'],oldBinding=old_binding,newBinding=updated['bindingSha256'],sha256=original_sha,pixelEditing=False,sourcePinsUnchanged=329,reason='Pilot frame8..11 included the next row top node; explicit empty gutter876 retains each complete three-node triangle.'))
    print('G semantic boundary refined; PNG bytes unchanged; native recapture required')

if __name__=='__main__':refine()
