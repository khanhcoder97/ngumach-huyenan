"""Read-only original-pixel registration; no raster output or visual approval."""
import json,statistics
from PIL import Image
from inspect_actor_library import ART,inspect
from calibrate_anh_dao_mobility import head_landmark

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def calibrate():
    path=ART/'Candidates_20261114e/candidate_manifest.json';m=json.loads(path.read_text(encoding='utf8'))
    assert len(m['records'])==16 and m['remainingSourcePages']==0
    entries=[]
    for r in m['records']:
        # Source review must visit all16 poses at60Hz. Gameplay windows stay
        # separate: stroke.24s, travelling wave.25s, cast tell.18s.
        if r.get('componentOnly') and r['previewDurationSeconds']<16/60:
            r['presentationWindowExampleSeconds']=r['previewDurationSeconds']
            r['previewDurationSeconds']=.32;r['sourceFrameDurationsMs']=[20]*16
        if r.get('componentOnly'):
            r.update(layout='VISUALLY_VERIFIED_UNIFORM_GRID',layoutReviewNote='Whole original manually viewed as4x4 complete effect groups. Separated droplets/dots/petals are not additional columns; empty/crop/duplicate gates retained.')
            # Measured transparent gutters of these four ORIGINAL PNGs.
            # Equal quarters cut adjacent wide strokes/petals. Keep all pixels
            # in source; only the sixteen source regions change.
            edges={
                'sk_hb_01_stroke_component':([0,337,630,925,1268],[0,314,603,902,1241]),
                'sk_hb_01_wave_component':([0,329,620,916,1268],[0,318,605,903,1241]),
                'sk_hb_02_frost_gain_component':([0,341,628,918,1263],[0,325,599,868,1246]),
                'sk_hb_02_frost_expire_component':([0,339,628,919,1263],[0,369,634,902,1246])}
            if r['id'] in edges:
                xx,yy=edges[r['id']];r['gridEdges']=dict(columns=xx,rows=yy)
        clean={k:v for k,v in r.items() if k not in ('sourceFootPivots','sourcePivots','bodyReferenceHeight','pivotMode')}
        if r.get('componentOnly'):clean['pivotMode']='CELL_CENTER'
        p=inspect(clean);frames=p['directions'][0]['frames'];pivots=[];heads=[]
        if r.get('direction'):
            with Image.open(ART/r['source']) as im:
                for f in frames:
                    x,y,w,h=f['rect'];region=im.crop((x,y,x+w,y+h));b=f['bounds'];head=head_landmark(region,b);heads.append(head)
                    pixels=region.get_flattened_data();floor=b[1]+(b[3]-b[1])*.76
                    dark=[(i%w,i//w) for i,(red,g,blue,a) in enumerate(pixels) if a>=200 and i//w>=floor and abs(i%w-head['centerX'])<=head['span']*.42 and max(red,g,blue)<105 and max(red,g,blue)-min(red,g,blue)<50]
                    assert len(dark)>16,'central boot baseline needs manual review: '+r['id']
                    bottom=max(y for x,y in dark);base=[x for x,y in dark if y>=bottom-13]
                    pivots.append([(min(base)+max(base))/2,bottom+1])
            height=pivots[0][1]-heads[0]['top'];assert 50<height<frames[0]['rect'][3]
            r.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=height)
            method='CENTRAL_DARK_BOOT_BASELINE_NEUTRAL_FIRST_POSE_HEIGHT'
        elif r['id']=='sk_hb_01_stroke_component':
            pivots=[[f['bounds'][0],(f['bounds'][1]+f['bounds'][3])/2] for f in frames]
            r.update(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots);method='LEFT_STROKE_ORIGIN'
        elif r['id'] in ('sk_hb_01_wave_component','sk_hb_02_needle_component'):
            pivots=[[f['bounds'][2]-1,(f['bounds'][1]+f['bounds'][3])/2] for f in frames]
            r.update(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots);method='RIGHT_LEADING_TIP'
        elif r['id']=='sk_hb_02_cast_dots_component':
            tops=[]
            with Image.open(ART/r['source']) as im:
                for f in frames:
                    x,y,w,h=f['rect'];region=im.crop((x,y,x+w,y+h));b=f['bounds'];data=region.get_flattened_data()
                    top=[(i%w,i//w) for i,(_,_,_,a) in enumerate(data) if a>=200 and i//w<b[1]+8];assert top
                    tops.append([statistics.median(x for x,y in top),statistics.median(y for x,y in top)])
            b=frames[7]['bounds'];delta=[(b[0]+b[2])/2-tops[7][0],(b[1]+b[3])/2-tops[7][1]]
            pivots=[[x+delta[0],y+delta[1]] for x,y in tops]
            r.update(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots);method='FIRST_TOP_DOT_PLUS_PEAK_TRIANGLE_ORIGIN_OFFSET'
        else:r['pivotMode']='SYMMETRIC_BOUNDS_CENTER';method='SIX_PETAL_SYMMETRIC_FOOTPRINT_CENTER'
        r['registrationCalibration']='Art_Source/Actor_Library_20261107/component_registration_20261114e.json' if r.get('componentOnly') else 'Art_Source/Actor_Library_20261107/body_registration_20261114e.json'
        result=inspect(r)
        entries.append(dict(id=r['id'],source=r['source'],sourceSha256=result['sha256'],method=method,pivotMode=r['pivotMode'],
            sourcePivots=pivots,bodyReferenceHeight=r.get('bodyReferenceHeight'),headLandmarks=heads,rasterModified=False,
            note='Attachment candidate only; source/native visual review still required. No physics, gameplay or approval inferred.'))
    save(path,m)
    for component in (False,True):
        selected=[e for e in entries if e['id'].startswith('sk_')==component]
        save(ART/(('component' if component else 'body')+'_registration_20261114e.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',entries=selected))
    print(json.dumps(dict(pages=len(entries),body=10,components=6,rasterModified=False,productionApproved=False)))

if __name__=='__main__':calibrate()
