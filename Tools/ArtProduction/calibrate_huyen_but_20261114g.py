"""Register whole source drawings; PNG bytes stay untouched and review stays pending."""
import json,statistics
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect,binary_projection
from calibrate_anh_dao_mobility import head_landmark
from calibrate_huyen_but_20261114f import gutter_edges,belt_root_x,cool_boot_x,component_registration

BATCH='20261114g'
def read(path):return json.loads(path.read_text(encoding='utf8'))
def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def boot_root(region,head,neutral,moving):
    """A compressed low dodge must not inherit standing height or a narrow head column."""
    width,height=region.size
    solid=region.getchannel('A').point(lambda a:255 if a>=200 else 0).getbbox()
    assert solid,'Empty source'
    current=solid[3]-head['top'];low=current<neutral*.85
    cutoff=head['top']+min(current,neutral)*(.67 if low else .76)
    radius=head['span']*(1.25 if low and moving else .75 if moving else .50)
    points=[(i%width,i//width) for i,(red,g,blue,alpha) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if alpha>=200 and i//width>=cutoff and abs(i%width-head['centerX'])<=radius and max(red,g,blue)<105 and max(red,g,blue)-min(red,g,blue)<40 and blue>=red-4 and blue>=g-4]
    assert len(points)>12,'No usable cool boot landmarks'
    ground=max(y for x,y in points)+1
    support=[x for x,y in points if y>=ground-13]
    return (min(support)+max(support))/2,ground,low

def calibrate():
    path=ART/('Candidates_'+BATCH+'/candidate_manifest.json');manifest=read(path)
    assert len(manifest['records'])==36 and manifest['remainingSourcePages']==0
    assert not any(r.get('batch')==BATCH for r in read(ART/'generation_records.json')),'Delivered bindings require a new review migration'
    results=[]
    for record in manifest['records']:
        if record.get('componentOnly'):
            record.update(layout='VISUALLY_VERIFIED_UNIFORM_GRID',layoutReviewNote='Original 4x4 atlas manually viewed; explicit empty solid-core gutters retain crop/empty/duplicate gates.')
        # The 0.24s departure idea cannot expose 16 source phases at a60Hz review clock.
        # Preview is0.32s; this does not extend the server movement/cast window.
        if record['id']=='sk_hb_05_departure_component':
            record.update(previewDurationSeconds=.32,sourceFrameDurationsMs=[20]*16,previewTimingNote='SOURCE_PREVIEW_0.32S_NOT_SERVER_MOVEMENT_DURATION')
        clean={k:v for k,v in record.items() if k not in ('sourceFootPivots','sourcePivots','bodyReferenceHeight','pivotMode')}
        if record.get('componentOnly'):clean['pivotMode']='CELL_CENTER'
        with Image.open(ART/record['source']) as image:
            try:page=inspect(clean)
            except AssertionError as error:
                assert 'clipped/overlapping' in str(error),'Source needs redraw: '+record['id']+' / '+str(error)
                xs,ys=binary_projection(image.getchannel('A').point(lambda a:255 if a>=200 else 0))
                record['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));clean['gridEdges']=record['gridEdges'];page=inspect(clean)
            frames=page['directions'][0]['frames'];pivots=[];heads=[]
            if record.get('direction'):
                neutral=None;offset=None;moving=any(s in record['id'] for s in ('_run_','_dodge_'))
                for index,frame in enumerate(frames):
                    x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,frame['bounds']);heads.append(head)
                    preliminary=frame['bounds'][3]-head['top'] if neutral is None else neutral
                    try:boot_x,ground,low=boot_root(region,head,preliminary,moving)
                    except AssertionError as error:raise AssertionError('Need manual boot landmark: '+record['id']+' frame'+str(index)) from error
                    if neutral is None:neutral=ground-head['top'];offset=boot_x-head['centerX']
                    pivots.append([head['centerX']+offset if moving else boot_x,ground])
                record.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral)
                method='NEUTRAL_HEAD_PROJECTED_X_COOL_BOOT_BASELINE_Y' if moving else 'CENTRAL_COOL_BOOT_BASELINE_XY'
            else:
                identifier=record['id']
                if identifier in ('sk_hb_05_expire_component','sk_hb_06_expire_component'):
                    mode,pivots,method=component_registration('sk_hb_04_expire_component',frames,image)
                elif identifier=='sk_hb_06_ally_heal_component':
                    mode,pivots,method=component_registration('sk_hb_04_heal_tick_component',frames,image)
                elif identifier in ('sk_hb_06_tell_component','sk_hb_06_wave_component'):
                    mode,pivots,method='SYMMETRIC_BOUNDS_CENTER',[],'SYMMETRIC_ELLIPSE_FOOTPRINT_NATIVE_REVIEW_REQUIRED'
                else:mode,pivots,method=component_registration(identifier,frames,image)
                record['pivotMode']=mode
                if pivots:record['sourcePivots']=pivots
            record['registrationCalibration']='Art_Source/Actor_Library_20261107/'+('component' if record.get('componentOnly') else 'body')+'_registration_'+BATCH+'.json'
        verified=inspect(record)
        results.append(dict(id=record['id'],source=record['source'],sourceSha256=verified['sha256'],method=method,pivotMode=record['pivotMode'],sourcePivots=pivots,bodyReferenceHeight=record.get('bodyReferenceHeight'),headLandmarks=heads,gridEdges=record.get('gridEdges'),rasterModified=False,productionApproved=False,note='Source registration only. Inspect native anchors, alternating contacts, handedness, alpha and return seams before approval; world movement unaccepted.'))
    save(path,manifest)
    for component in (False,True):
        save(ART/(('component' if component else 'body')+'_registration_'+BATCH+'.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',entries=[r for r in results if r['id'].startswith('sk_')==component]))
    evidence=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH);evidence.mkdir(exist_ok=True,parents=True)
    report=dict(selected=len(results),sourcePoses=len(results)*16,bodySources=27,components=9,explicitGutterSources=[r['id'] for r in results if r['gridEdges']],productionApproved=False,rasterModified=False)
    save(evidence/'candidate_registration_summary.json',report);print(json.dumps(report))

if __name__=='__main__':calibrate()
