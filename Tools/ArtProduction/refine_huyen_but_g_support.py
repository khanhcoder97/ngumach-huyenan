"""Metadata-only support VFX corrections from complete native pose inspection."""
import json
from PIL import Image
from inspect_actor_library import ART,RUN,ROOT,inspect,binding_sha256

def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def three_node_origin(region,bounds):
    """Centroid of the three persistent12/4/8-o'clock nodes, not a forming arc bbox."""
    width,height=region.size;left,top,right,bottom=bounds;cx=(left+right)/2;bw=right-left;bh=bottom-top
    pixels=[(i%width,i//width,g-max(red,blue)) for i,(red,g,blue,alpha) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if alpha>=200 and g>=130 and g-blue>=30 and g-red>=15]
    windows=[[(x,y,v) for x,y,v in pixels if abs(x-cx)<=bw*.15 and y<=top+bh*.28],[(x,y,v) for x,y,v in pixels if x<=left+bw*.25 and y>=top+bh*.50],[(x,y,v) for x,y,v in pixels if x>=right-bw*.25 and y>=top+bh*.50]]
    nodes=[]
    for window in windows:
        assert len(window)>=4,'Persistent node needs manual landmark'
        peak=max(v for x,y,v in window);selected=[(x,y,v*v) for x,y,v in window if v>=peak*.75]
        mass=sum(v for x,y,v in selected);nodes.append([sum(x*v for x,y,v in selected)/mass,sum(y*v for x,y,v in selected)/mass])
    return [sum(x for x,y in nodes)/3,sum(y for x,y in nodes)/3],nodes

def refine():
    records=read(ART/'generation_records.json');structure=read(ART/'structure_report.json');review=read(ART/'visual_review.json');registration=read(ART/'component_registration_20261114g.json')
    assert len(review['sourceApprovals'])==329
    updated={};changes=[]
    for identifier in ('sk_hb_06_tell_component','sk_hb_06_ally_heal_component'):
        record=next(r for r in records if r['id']==identifier);old=next(p for p in structure['pages'] if p['id']==identifier)
        assert record['batch']=='20261114g' and not old['productionApproved']
        assert not record.get('supportPilotRefined'),'One-time pilot refinement guard'
        record.pop('sourcePivots',None);record['pivotMode']='CELL_CENTER'
        if identifier=='sk_hb_06_tell_component':
            assert record['gridEdges']['rows']==[0,244,636,888,1246]
            record['gridEdges']['rows']=[0,383,636,888,1246]
        initial=inspect(record);frames=initial['directions'][0]['frames'];nodes=[]
        with Image.open(ART/record['source']) as image:
            if identifier=='sk_hb_06_tell_component':
                pivots=[]
                for frame in frames:
                    x,y,w,h=frame['rect'];pivot,node=three_node_origin(image.crop((x,y,x+w,y+h)),frame['bounds']);pivots.append(pivot);nodes.append(node)
                method='CENTROID_OF_THREE_PERSISTENT_JADE_NODES'
            else:
                # First two rows still contain the developing ribbon foot ends.
                # Fixed floor origins preserve the later upward particle travel.
                baseline=[max(f['rect'][1]+f['bounds'][3] for f in frames[row*4:row*4+4]) for row in range(2)]
                pitch=baseline[1]-baseline[0];assert pitch>0
                baseline += [baseline[0]+2*pitch,baseline[0]+3*pitch]
                column=[frames[col+4]['rect'][0]+(frames[col+4]['bounds'][0]+frames[col+4]['bounds'][2])/2 for col in range(4)]
                pivots=[[column[i%4]-f['rect'][0],baseline[i//4]-f['rect'][1]] for i,f in enumerate(frames)]
                method='MEASURED_EARLY_RIBBON_FLOOR_ROWS_THEN_FIXED_EMITTER_PITCH'
        record.update(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots,supportPilotRefined=True)
        page=inspect(record);page.update(bindingSha256=binding_sha256(page),productionApproved=False,visualState=old['visualState'],visualNotes=old['visualNotes'])
        assert page['sha256']==old['sha256']
        updated[identifier]=page
        entry=next(e for e in registration['entries'] if e['id']==identifier);entry.update(sourcePivots=pivots,pivotMode=record['pivotMode'],method=method,gridEdges=record.get('gridEdges'),nodeLandmarks=nodes)
        changes.append(dict(id=identifier,sourceSha256=page['sha256'],oldBinding=old['bindingSha256'],newBinding=page['bindingSha256'],method=method,pixelEditing=False))
    structure['pages']=[updated.get(p['id'],p) for p in structure['pages']]
    save(ART/'generation_records.json',records);save(ART/'structure_report.json',structure);save(RUN/'pages.json',dict(schemaVersion=1,pages=structure['pages']));save(ART/'component_registration_20261114g.json',registration)
    save(ROOT/'Implementation/Reports/Evidence/Actor_Batch_20261114g/support_native_refinement.json',dict(changes=changes,sourcePinsUnchanged=329,productionApprovals=0))
    print(json.dumps(dict(changed=len(changes),rasterModified=False,nativeRecaptureRequired=True)))

if __name__=='__main__':refine()
