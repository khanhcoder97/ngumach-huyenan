"""Read original pixels to register F candidates; never writes raster or approvals."""
import json,statistics
from collections import Counter
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect,binary_projection,bands
from calibrate_anh_dao_mobility import head_landmark

def save(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def gutter_edges(values):
    """Choose a genuinely empty gutter near each manually identified quarter."""
    maximum=len(values);runs=bands([v==0 for v in values],0);edges=[0]
    for quarter in (1,2,3):
        nominal=maximum*quarter/4
        candidates=[(a,b) for a,b in runs if b-a>=8 and abs((a+b)/2-nominal)<=maximum/4*.35]
        assert candidates,'no intact common gutter; redraw or manual regions required'
        a,b=min(candidates,key=lambda run:abs((run[0]+run[1])/2-nominal))
        edges.append((a+b)//2)
    edges.append(maximum);assert all(a<b for a,b in zip(edges,edges[1:]))
    return edges

def belt_root_x(region,head,height):
    """A wide central brown belt outranks a narrow moving wooden brush."""
    w,h=region.size;points=[]
    for i,(red,g,blue,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()):
        x,y=i%w,i//w
        if a>=200 and abs(x-head['centerX'])<=head['span']*.42 and head['top']+height*.48<=y<=head['top']+height*.80 and 45<=red<165 and g>=25 and red-g>=12 and g-blue>=4:
            points.append((x,y))
    counts=Counter(y for x,y in points)
    if not counts or max(counts.values())<5:return None
    line=max(counts,key=counts.get);row={x for x,y in points if y==line}
    runs=bands([x in row for x in range(w)],0)
    left,right=max(runs,key=lambda run:run[1]-run[0])
    return (left+right-1)/2 if right-left>=5 else None

def cool_boot_x(region,head,ground_y):
    w,h=region.size
    points=[i%w for i,(red,g,blue,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and ground_y-14<=i//w<ground_y and abs(i%w-head['centerX'])<=head['span']*.50 and max(red,g,blue)<105 and max(red,g,blue)-min(red,g,blue)<40 and blue>=red-4 and blue>=g-4]
    assert len(points)>6,'Stationary boot root needs manual review'
    return (min(points)+max(points))/2

def component_registration(identifier,frames,original):
    if identifier in ('sk_hb_02_frost_sustain_component','sk_hb_03_sustain_component'):
        return 'SYMMETRIC_BOUNDS_CENTER',[],'COMPLETE_SYMMETRIC_FOOTPRINT_CENTRE'
    if identifier in ('sk_hb_03_gain_component','sk_hb_04_tell_component'):
        # Both sources explicitly begin at the bottom of the eventual rim.
        # Its persistent bottom extremity preserves a forming arc's centre;
        # bounding-box centres alone would chase the open arc.
        bottom=[]
        for f in frames:
            x,y,w,h=f['rect'];b=f['bounds'];region=original.crop((x,y,x+w,y+h))
            row=[i%w for i,(_,_,_,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and i//w>=b[3]-3]
            assert row;bottom.append([statistics.median(row),b[3]])
        dx=statistics.median(bottom[i][0]-(frames[i]['bounds'][0]+frames[i]['bounds'][2])/2 for i in range(12,16))
        dy=statistics.median(bottom[i][1]-(frames[i]['bounds'][1]+frames[i]['bounds'][3])/2 for i in range(12,16))
        return 'SOURCE_PIVOTS',[[x-dx,y-dy] for x,y in bottom],'PERSISTENT_BOTTOM_RIM_FROM_COMPLETED_LAST_ROW'
    if identifier in ('sk_hb_03_expire_component','sk_hb_03_break_component','sk_hb_04_expire_component'):
        # Early rows retain opposite fragments of the initial full rim. Keep
        # that footprint through sparse last beads; never chase one fragment.
        cx=[frames[c]['rect'][0]+(frames[c]['bounds'][0]+frames[c]['bounds'][2])/2 for c in range(4)]
        cy=[]
        for row in range(3):
            bb=[(f['rect'][1]+f['bounds'][1],f['rect'][1]+f['bounds'][3]) for f in frames[row*4:row*4+4]]
            cy.append((min(a for a,b in bb)+max(b for a,b in bb))/2)
        pitch=statistics.median((cy[1]-cy[0],cy[2]-cy[1]));origins=cy+[cy[2]+pitch]
        return 'SOURCE_PIVOTS',[[cx[i%4]-f['rect'][0],origins[i//4]-f['rect'][1]] for i,f in enumerate(frames)],'INITIAL_RIM_COLUMNS_PER_ROW_AND_EXTRAPOLATED_FADE_ORIGIN'
    if identifier=='sk_hb_04_heal_tick_component':
        cx=[frames[c+4]['rect'][0]+(frames[c+4]['bounds'][0]+frames[c+4]['bounds'][2])/2 for c in range(4)]
        return 'SOURCE_PIVOTS',[[cx[i%4]-f['rect'][0],f['rect'][3]*.84] for i,f in enumerate(frames)],'TWO_RIBBON_COLUMN_ORIGIN_AND_FIXED_LOW_BASELINE'
    # Particle positions vary, but the emitter footprint must not inherit the
    # image generator's unequal outside padding in its four atlas columns.
    cx=[];cy=[]
    for col in range(4):
        bb=[(f['rect'][0]+f['bounds'][0],f['rect'][0]+f['bounds'][2]) for f in frames[col::4]]
        cx.append((min(a for a,b in bb)+max(b for a,b in bb))/2)
    for row in range(4):
        bb=[(f['rect'][1]+f['bounds'][1],f['rect'][1]+f['bounds'][3]) for f in frames[row*4:row*4+4]]
        cy.append((min(a for a,b in bb)+max(b for a,b in bb))/2)
    return 'SOURCE_PIVOTS',[[cx[i%4]-f['rect'][0],cy[i//4]-f['rect'][1]] for i,f in enumerate(frames)],'MEASURED_PARTICLE_FIELD_COLUMN_AND_ROW_ORIGINS'

def calibrate():
    batch='20261114f';path=ART/('Candidates_'+batch+'/candidate_manifest.json');m=json.loads(path.read_text(encoding='utf8'))
    assert len(m['records'])==31 and m['remainingSourcePages']==0
    assert not any(r.get('batch')==batch for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8'))),'Do not recalibrate delivered/approved bindings'
    results=[]
    for r in m['records']:
        if r.get('componentOnly'):r.update(layout='VISUALLY_VERIFIED_UNIFORM_GRID',layoutReviewNote='Original manually viewed as4x4 effect groups; droplets/glints are within a group. Explicit clear gutters do not relax crop/empty/duplicate gates.')
        clean={k:v for k,v in r.items() if k not in ('sourceFootPivots','sourcePivots','bodyReferenceHeight','pivotMode')}
        if r.get('componentOnly'):clean['pivotMode']='CELL_CENTER'
        with Image.open(ART/r['source']) as original:
            try:p=inspect(clean)
            except AssertionError as exc:
                assert 'clipped/overlapping' in str(exc),'Needs separate source review: '+r['id']+' / '+str(exc)
                xs,ys=binary_projection(original.getchannel('A').point(lambda a:255 if a>=200 else 0))
                r['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));clean['gridEdges']=r['gridEdges'];p=inspect(clean)
            frames=p['directions'][0]['frames'];pivots=[];heads=[];fallbacks=[]
            if r.get('direction'):
                neutral_height=None
                for n,f in enumerate(frames):
                    x,y,w,h=f['rect'];region=original.crop((x,y,x+w,y+h));bb=f['bounds'];head=head_landmark(region,bb);heads.append(head)
                    preliminary=bb[3]-head['top'] if neutral_height is None else neutral_height
                    belt=belt_root_x(region,head,preliminary)
                    centre=head['centerX'] if belt is None else belt
                    dark=[(i%w,i//w) for i,(red,g,blue,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and i//w>=head['top']+preliminary*.76 and abs(i%w-centre)<=head['span']*.50 and max(red,g,blue)<105 and max(red,g,blue)-min(red,g,blue)<40 and blue>=red-4 and blue>=g-4]
                    assert len(dark)>12,'Central boot baseline needs manual review: '+r['id']+' f'+str(n)
                    bottom=max(y for x,y in dark);base=[x for x,y in dark if y>=bottom-13]
                    if belt is None:fallbacks.append(n)
                    root_x=(belt if belt is not None else (min(base)+max(base))/2) if '_skill_05_' in r['id'] else cool_boot_x(region,head,bottom+1)
                    pivots.append([root_x,bottom+1])
                    if neutral_height is None:neutral_height=pivots[0][1]-head['top']
                r.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral_height)
                if '_skill_05_' in r['id']:
                    offset=cool_boot_x(original.crop((frames[0]['rect'][0],frames[0]['rect'][1],frames[0]['rect'][0]+frames[0]['rect'][2],frames[0]['rect'][1]+frames[0]['rect'][3])),heads[0],pivots[0][1])-heads[0]['centerX']
                    for i,head in enumerate(heads):pivots[i][0]=head['centerX']+offset
                method='NEUTRAL_HEAD_PROJECTION_X_COOL_BOOT_BASELINE_Y' if '_skill_05_' in r['id'] else 'CENTRAL_COOL_BOOT_BASELINE_XY';r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_'+batch+'.json'
            else:
                mode,pivots,method=component_registration(r['id'],frames,original);r['pivotMode']=mode
                if pivots:r['sourcePivots']=pivots
                r['registrationCalibration']='Art_Source/Actor_Library_20261107/component_registration_'+batch+'.json'
        result=inspect(r)
        results.append(dict(id=r['id'],source=r['source'],sourceSha256=result['sha256'],method=method,pivotMode=r['pivotMode'],sourcePivots=pivots,bodyReferenceHeight=r.get('bodyReferenceHeight'),headLandmarks=heads,beltFallbackFrames=fallbacks,gridEdges=r.get('gridEdges'),rasterModified=False,note='Registration candidate only; inspect native stability, handedness and loop/return seams before source approval. World movement and combat authority unchanged.'))
    save(path,m)
    for component in (False,True):
        selected=[e for e in results if e['id'].startswith('sk_')==component]
        save(ART/(('component' if component else 'body')+'_registration_'+batch+'.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',entries=selected))
    ev=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+batch);ev.mkdir(parents=True,exist_ok=True)
    report=dict(selected=len(results),sourcePoses=len(results)*16,bodySources=22,components=9,explicitGutterSources=[e['id'] for e in results if e['gridEdges']],beltFallbacks={e['id']:e['beltFallbackFrames'] for e in results if e['beltFallbackFrames']},productionApproved=False,rasterModified=False)
    save(ev/'candidate_registration_summary.json',report);print(json.dumps(report))

if __name__=='__main__':calibrate()
