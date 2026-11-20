"""Read-only raster inspection and metadata export. Never edits/resamples a bitmap."""
import argparse,hashlib,json,statistics,math
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';RUN=ROOT/'ClientGodot/assets/actor_library_v1'

def binary_projection(mask):
    # The caller supplies the alpha>=200 L mask (only 0/255). Pillow counts
    # exact solid pixels in native code; avoid millions of Python pixel reads.
    # Counts and resulting source rectangles remain byte-for-byte identical.
    w,h=mask.size
    return ([mask.crop((x,0,x+1,h)).histogram()[255] for x in range(w)],
            [mask.crop((0,y,w,y+1)).histogram()[255] for y in range(h)])
def bands(values,gap):
    result=[];start=None;last=-999
    for i,v in enumerate(values):
        if not v:continue
        if start is None:start=i
        elif i-last>gap+1:result.append((start,last+1));start=i
        last=i
    if start is not None:result.append((start,last+1))
    return result

def locate(values,expected,maximum_gap):
    # A long hammer can leave only a four-pixel inter-row gutter. Large gap
    # bridging would falsely merge two complete rows. Prefer the largest safe
    # bridge that retains the declared count and rejects tiny isolated bands.
    threshold=max(3,max(values)*.025);occupied=[v>threshold for v in values]
    for gap in range(maximum_gap,1,-1):
        found=bands(occupied,gap)
        if len(found)==expected and min(b-a for a,b in found)>=len(values)/expected*.2:return found
    return bands(occupied,maximum_gap)

def clear_gutter_edges(groups,maximum,values):
    # Opt-in for long whips/weapon tips: thresholded projection can miss a thin
    # tip. Values count alpha>=200 pixels. Cut in a >=4px solid-core-free run;
    # keep the existing margin check to retain the tip and its edge pixels.
    result=[0]
    for left,right in zip(groups,groups[1:]):
        start,end=left[1],right[0]
        empty=bands([v==0 for v in values[start:end]],0)
        assert empty,'no clear gutter between source cells'
        a,b=max(empty,key=lambda run:run[1]-run[0])
        assert b-a>=4,'gutter too narrow for an intact source frame'
        result.append(start+(a+b)//2)
    return result+[maximum]

def reference_height(frames,scale_mode='HEIGHT'):
    assert scale_mode in ('HEIGHT','LONGEST_AXIS'),'unreviewed source scale mode'
    return statistics.median(max(f['bounds'][2]-f['bounds'][0],f['bounds'][3]-f['bounds'][1])
                             if scale_mode=='LONGEST_AXIS' else f['bounds'][3]-f['bounds'][1]
                             for f in frames[:3])

def registered_height(record,frames,cell_height,vfx=False):
    # Charged clips can start crouched. An explicitly reviewed neutral height
    # prevents their first low pose being enlarged back to standing size.
    # This changes metadata only, and remains part of the source approval hash.
    if 'bodyReferenceHeight' in record:
        height=record['bodyReferenceHeight']
        assert not vfx,'body reference height is actor-only'
        assert record.get('scaleMode','HEIGHT')=='HEIGHT','body reference height requires HEIGHT mode'
        assert type(height) in (int,float) and math.isfinite(height) and 16<=height<=cell_height,'invalid neutral body reference height'
        return height
    assert record.get('pivotMode') not in ('MOSS_CORE_ROOT','BOOT_CORE_FOOT','DARK_BOOT_CORE_FOOT'),'body-core registration requires neutral body reference height'
    if vfx:
        # Long narrow components use their maximum visible span for the
        # editor's nominal display size. Existing HEIGHT sources keep pins.
        return max(max(f['bounds'][2]-f['bounds'][0],f['bounds'][3]-f['bounds'][1])
                   if record.get('scaleMode')=='LONGEST_AXIS' else f['bounds'][3]-f['bounds'][1] for f in frames)
    return reference_height(frames,record.get('scaleMode','HEIGHT'))

def silver_core_pivot(pixels,width):
    # Explicit fish-only registration: the silver torso defines its root, not
    # the green flexible tail. Read coordinates only; never alter source pixels.
    points=[(i%width,i//width) for i,(r,g,b,a) in enumerate(pixels)
            if a>=200 and r>=110 and r>=g*.82 and b>=g*.95]
    assert len(points)>=8,'silver torso core absent; manual registration required'
    return [sum(x for x,y in points)/len(points),sum(y for x,y in points)/len(points)]

def binding_sha256(page):
    payload={k:page.get(k) for k in ('directions','referenceHeight','scaleMode','pivotMode')}
    # A timing/loop edit changes what was reviewed. Preserve old pins on pages
    # with no explicit preview profile; new profiles must be reviewed again.
    for key in ('previewDurationSeconds','previewLoop','sourceFrameDurationsMs'):
        if key in page:payload[key]=page[key]
    return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def preview_profile(record):
    keys=('previewDurationSeconds','previewLoop')
    if not any(k in record for k in keys):return {}
    assert record['id'].startswith('sk_') and record.get('componentOnly'),'preview profile is component-only'
    assert all(k in record for k in keys),'incomplete preview profile'
    seconds=record['previewDurationSeconds']
    assert type(seconds) in (int,float) and math.isfinite(seconds) and 16/60<=seconds<=60,'invalid preview duration; 60-step review must visit all16 frames'
    assert type(record['previewLoop']) is bool,'invalid preview loop flag'
    return {k:record[k] for k in keys}

def source_timing(record):
    if 'sourceFrameDurationsMs' not in record:return {}
    durations=record['sourceFrameDurationsMs']
    assert type(durations) is list and len(durations)==16,'source timing must bind exactly sixteen frames'
    assert all(type(n) in (int,float) and math.isfinite(n) and 1000/60<=n<=10000 for n in durations),'invalid source-frame duration; 60-step review must visit each pose'
    seconds=sum(durations)/1000
    assert seconds<=60,'source timeline exceeds sixty seconds'
    if 'previewDurationSeconds' in record:
        assert abs(record['previewDurationSeconds']-seconds)<1e-6,'source and preview durations disagree'
    return {'sourceFrameDurationsMs':durations}

def moss_body_pivot(pixels,width,body_height,foot_offset):
    # Waterroot-only registration. A brown whip must not define the stump's
    # foot or scale. Read the green core; never alter source pixels.
    assert math.isfinite(body_height) and body_height>=16,'invalid root body height'
    assert len(foot_offset)==2 and all(math.isfinite(v) and abs(v)<=1 for v in foot_offset),'invalid root foot offset'
    points=[(i%width,i//width) for i,(r,g,b,a) in enumerate(pixels)
            if a>=200 and g>=60 and g>r*1.05 and g>=b*.9]
    assert len(points)>=8,'moss core absent; manual registration required'
    return [sum(p[axis] for p in points)/len(points)+foot_offset[axis]*body_height for axis in (0,1)]

def boot_foot_pivot(pixels,width,height):
    # Explicit Minh Kiem palette registration. Silver blade and gold hilt do
    # not define the floor when the sword points below the character's boots.
    points={(i%width,i//width) for i,(r,g,b,a) in enumerate(pixels)
            if i//width>=height*.55 and a>=200 and 35<=r<=140 and 25<=g<=100 and 20<=b<=90 and r>=g*1.08 and g>=b*1.05}
    groups=[]
    while points:
        stack=[points.pop()];group=[]
        while stack:
            x,y=stack.pop();group.append((x,y))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    p=(x+dx,y+dy)
                    if p in points:points.remove(p);stack.append(p)
        if len(group)>=8:groups.append(group)
    assert groups,'brown boot core absent; manual registration required'
    selected=[p for group in sorted(groups,key=lambda g:(-len(g),min(g)))[:2] for p in group]
    bottom=max(y for x,y in selected)
    low=[p for p in selected if p[1]>=bottom-max(3,height*.10)]
    return [sum(x for x,y in low)/len(low),min(height-1,bottom+2)]

def dark_boot_foot_pivot(pixels,width,height):
    # Anh Dao boots are dark plum/brown, unlike Minh Kiem's warmer boots.
    # Dense fill components reject thin dark blade contours; bright steel and
    # gold are outside the palette. This selects coordinates, never edits PNG.
    candidates={(i%width,i//width) for i,(r,g,b,a) in enumerate(pixels)
                if i//width>=height*.55 and a>=200 and 18<=r<=130 and 12<=g<=110 and 10<=b<=115
                and r>=g*1.02 and r>=b*.9 and g>=b*.7}
    points={p for p in candidates if sum((p[0]+dx,p[1]+dy) in candidates for dx in (-1,0,1) for dy in (-1,0,1))>=5}
    groups=[]
    while points:
        stack=[points.pop()];group=[]
        while stack:
            x,y=stack.pop();group.append((x,y))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    p=(x+dx,y+dy)
                    if p in points:points.remove(p);stack.append(p)
        if len(group)>=16:groups.append(group)
    assert groups,'dark boot fill absent; manual registration required'
    selected=[p for group in sorted(groups,key=lambda g:(-len(g),min(g)))[:2] for p in group]
    bottom=max(y for x,y in selected)
    low=[p for p in selected if p[1]>=bottom-max(3,height*.06)]
    return [sum(x for x,y in low)/len(low),min(height-1,bottom+2)]


def source_approval_matches(page,approval):
    return approval.get('sourceSha256')==page['sha256'] and approval.get('bindingSha256')==binding_sha256(page)

def inspect(record, art_root=None):
    assert record.get('gutterPolicy') in (None,'SOLID_CORE_GUTTER'),'unreviewed gutter policy'
    preview=preview_profile(record)
    timing=source_timing(record)
    source_pivots=record.get('sourcePivots')
    if source_pivots is not None or record.get('pivotMode')=='SOURCE_PIVOTS':
        assert record['id'].startswith('sk_') and record.get('componentOnly') and record.get('pivotMode')=='SOURCE_PIVOTS','source pivots require an explicitly registered VFX component'
        assert type(source_pivots) is list and len(source_pivots)==16,'source pivots must bind sixteen real frames'
        assert all(type(pair) is list and len(pair)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in pair) for pair in source_pivots),'invalid source pivot coordinates'
    foot_pivots=record.get('sourceFootPivots')
    if foot_pivots is not None or record.get('pivotMode')=='SOURCE_FOOT_PIVOTS':
        assert record['id'].startswith(('class_','mob_','boss_','npc_')) and not record.get('componentOnly') and record.get('pivotMode')=='SOURCE_FOOT_PIVOTS','source foot pivots require an explicitly registered actor'
        assert 'bodyReferenceHeight' in record and record.get('scaleMode','HEIGHT')=='HEIGHT','authored foot origins require a fixed neutral body height'
        assert type(foot_pivots) is list and len(foot_pivots)==16,'source foot pivots must bind sixteen real frames'
        assert all(type(pair) is list and len(pair)==2 and all(type(v) in (int,float) and math.isfinite(v) for v in pair) for pair in foot_pivots),'invalid source foot coordinates'
    translucent_tail=record.get('translucentTailFromFrame')
    if translucent_tail is not None:
        assert record['id'].startswith('sk_') and record.get('componentOnly') and record.get('layout')=='VISUALLY_VERIFIED_UNIFORM_GRID','translucent tail requires a reviewed VFX component grid'
        assert type(translucent_tail) is int and 12<=translucent_tail<=15,'translucent tail is limited to the last four source frames'
    path=(art_root or ART)/record['source']
    with Image.open(path) as im:
        assert im.mode=='RGBA','PNG must retain RGBA'
        w,h=im.size;a=im.getchannel('A');assert a.getextrema()[0]==0,'opaque fake background'
        # Projection locates the actual transparent gutters instead of assuming a cropped output retained equal cells.
        mask=a.point(lambda x:255 if x>=200 else 0);xs,ys=binary_projection(mask)
        if record.get('layout') in ('VISUALLY_VERIFIED_UNIFORM_GRID','VISUALLY_VERIFIED_DIRECTIONAL_GRID'):
            # Particle islands do not define extra columns/rows. Only opt in after
            # viewing the whole sheet; per-cell emptiness, edge and hash checks remain.
            assert (record['columns'],record['rows'])==(4,4),'explicit grid requires sixteen source cells'
            if record['layout']=='VISUALLY_VERIFIED_DIRECTIONAL_GRID':
                # A thin held blade can split the projection into extra islands.
                # Opt in only after inspecting an actual equal-cell actor page;
                # retain empty-cell, full source-edge and duplicate-frame gates.
                assert record['id'].startswith('class_') and record.get('direction') in ('N','NE','E','SE','S','SW','W','NW'),'directional grid requires a declared class facing'
            else:
                assert record['id'].startswith('sk_'),'uniform effect grid is VFX-only'
            xx=[round(i*w/4) for i in range(5)];yy=[round(i*h/4) for i in range(5)]
            if 'gridEdges' in record:
                assert record['layout']=='VISUALLY_VERIFIED_DIRECTIONAL_GRID' or (record.get('componentOnly') and record.get('layoutReviewNote')),'effect edges require a recorded manual layout review'
                # Explicit atlas regions preserve wide weapon follow-throughs
                # that cross an ideal equal-cell boundary into a clear gutter.
                grid=record['gridEdges'];xx=grid['columns'];yy=grid['rows']
                for edges,maximum in ((xx,w),(yy,h)):
                    assert len(edges)==5 and all(type(v) is int for v in edges),'invalid explicit directional edges'
                    assert edges[0]==0 and edges[-1]==maximum and all(a<b for a,b in zip(edges,edges[1:])),'non-monotonic/out-of-image directional edges'
            cols=list(zip(xx,xx[1:]));rows=list(zip(yy,yy[1:]))
        else:
            cols=locate(xs,record['columns'],max(2,int(w/100)))
            rows=locate(ys,record['rows'],max(2,int(h/120)))
            assert len(cols)==record['columns'],f"columns expected {record['columns']}, got {len(cols)}"
            assert len(rows)==record['rows'],f"rows expected {record['rows']}, got {len(rows)}"
            edges=lambda groups,maximum:[0]+[round((a[1]+b[0])/2) for a,b in zip(groups,groups[1:])]+[maximum]
            xx=edges(cols,w);yy=edges(rows,h)
            if record.get('gutterPolicy')=='SOLID_CORE_GUTTER':
                xx=clear_gutter_edges(cols,w,xs);yy=clear_gutter_edges(rows,h,ys)
        frames=[];hashes=[]
        for row in range(len(rows)):
            for col in range(len(cols)):
                x,y,x1,y1=xx[col],yy[row],xx[col+1],yy[row+1]
                tail_frame=translucent_tail is not None and row*len(cols)+col>=translucent_tail
                alpha=a.crop((x,y,x1,y1)).point(lambda value:255 if value>=64 else 0) if tail_frame else mask.crop((x,y,x1,y1))
                # A deliberately fading RGBA tail need not contain alpha200.
                # Require a visible cluster, retain crop gates and full pixel
                # uniqueness; missing/fully transparent cells still fail.
                if tail_frame:assert alpha.histogram()[255]>=4,'translucent tail lacks a visible source cluster'
                bb=alpha.getbbox();assert bb,'empty frame'
                margin=min(bb[0],bb[1],x1-x-bb[2],y1-y-bb[3]);assert margin>=2,f'clipped/overlapping frame row{row} col{col}'
                # Foot-ground anchor is metadata only. Source pixels remain byte-identical.
                foot=alpha.crop((int((x1-x)*.25),int((y1-y)*.6),int((x1-x)*.75),y1-y)).getbbox()
                pivot=[(bb[0]+bb[2])/2,bb[3]] if not foot else [int((x1-x)*.25)+(foot[0]+foot[2])/2,int((y1-y)*.6)+foot[3]]
                if record.get('pivotMode')=='CELL_CENTER':
                    assert record['id'].startswith('sk_'),'cell-center mode is VFX-only'
                    offset=record.get('cellCenterOffset',[0,0])
                    assert len(offset)==2 and all(math.isfinite(v) for v in offset),'invalid VFX center offset'
                    pivot=[(x1-x)/2+offset[0],(y1-y)/2+offset[1]]
                    assert 0<=pivot[0]<x1-x and 0<=pivot[1]<y1-y,'VFX pivot outside cell'
                elif record.get('pivotMode')=='SYMMETRIC_BOUNDS_CENTER':
                    # Opt-in for a reviewed symmetric converging glint. Its
                    # actual drawn center can drift within AI-generated cells.
                    # Never apply to travelling projectiles or asymmetric dust.
                    assert record['id'].startswith('sk_'),'symmetric center is VFX-only'
                    pivot=[(bb[0]+bb[2])/2,(bb[1]+bb[3])/2]
                elif record.get('pivotMode')=='SILVER_CORE_CENTER':
                    assert record['id'].startswith('mob_carpling_'),'silver-core registration is fish-only'
                    region=im.crop((x,y,x1,y1))
                    pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    pivot=silver_core_pivot(pixels,x1-x)
                elif record.get('pivotMode')=='MOSS_CORE_ROOT':
                    assert record['id'].startswith('mob_waterroot_'),'moss registration is Waterroot-only'
                    region=im.crop((x,y,x1,y1));body_height=record['bodyReferenceHeight']
                    assert body_height<=h/record['rows'],'root body height exceeds cell'
                    pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    pivot=moss_body_pivot(pixels,x1-x,body_height,record['rootFootOffset'])
                    assert 0<=pivot[0]<region.width and 0<=pivot[1]<region.height,'root anchor outside source cell'
                elif record.get('pivotMode')=='BOOT_CORE_FOOT':
                    assert record['id'].startswith('class_minh_kiem_'),'boot palette registration is Minh Kiem-only'
                    region=im.crop((x,y,x1,y1))
                    pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    pivot=boot_foot_pivot(pixels,x1-x,y1-y)
                elif record.get('pivotMode')=='DARK_BOOT_CORE_FOOT':
                    assert record['id'].startswith('class_anh_dao_'),'dark boot registration is Anh Dao-only'
                    region=im.crop((x,y,x1,y1))
                    pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    pivot=dark_boot_foot_pivot(pixels,x1-x,y1-y)
                elif record.get('pivotMode')=='SOURCE_PIVOTS':
                    pivot=source_pivots[row*len(cols)+col]
                    assert 0<=pivot[0]<x1-x and 0<=pivot[1]<y1-y,'registered source pivot outside its original cell'
                elif record.get('pivotMode')=='SOURCE_FOOT_PIVOTS':
                    pivot=foot_pivots[row*len(cols)+col]
                    assert 0<=pivot[0]<x1-x and 0<=pivot[1]<y1-y,'registered foot origin outside its original cell'
                frames.append(dict(rect=[x,y,x1-x,y1-y],bounds=list(bb),pivot=pivot))
                if tail_frame:frames[-1]['boundsAlphaThreshold']=64
                hashes.append(hashlib.sha256(im.crop((x,y,x1,y1)).tobytes()).hexdigest())
        assert len(set(hashes))==len(hashes),'duplicate full-frame pixels; frame count cannot be padded'
        directions=[]
        assert record.get('scaleMode','HEIGHT') in ('HEIGHT','LONGEST_AXIS'),'unreviewed source scale mode'
        if len(cols)==8 and (len(rows) in (2,4,6,8,10) or record.get('unboundRows')==1):
            authored=record.get('authoredDirections') or ['N','NE','E','SE','S']
            assert len(authored)*2+record.get('unboundRows',0)==len(rows) and len(set(authored))==len(authored),'partial atlas must declare its actual direction blocks and unused rows'
            assert all(d in ['N','NE','E','SE','S','SW','W','NW'] for d in authored)
            for source,name in enumerate(authored):
                block=frames[source*16:source*16+16];assert len(block)==16
                # Page resolution varies. Calibrate from the neutral first poses, never
                # scale a lying death pose back up to standing height.
                height=registered_height(record,block,h/record['rows'])
                directions.append(dict(direction=name,flip=False,referenceHeight=height,frames=block))
            if record.get('mirrorAllowed',True):
                for target,source in [('SW','SE'),('W','E'),('NW','NE')]:
                    if target not in authored and source in authored:
                        original=next(d for d in directions if d['direction']==source)
                        directions.append(dict(direction=target,flip=True,referenceHeight=original['referenceHeight'],frames=original['frames']))
            directions.sort(key=lambda d:['N','NE','E','SE','S','SW','W','NW'].index(d['direction']))
        elif (len(cols),len(rows))==(4,4):
            vfx=record['id'].startswith('sk_');height=registered_height(record,frames,h/record['rows'],vfx)
            directions=[dict(direction=record.get('direction') or ('OMNI' if vfx else 'S'),flip=False,referenceHeight=height,frames=frames)]
        else:raise AssertionError('unreviewed atlas layout')
        page=dict(id=record['id'],file='sheets/'+path.name,source=record['source'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),imageSize=[w,h],directions=directions,
            sourceFrames=len(frames),framesPerDirection=16,referenceHeight=statistics.median(f['bounds'][3]-f['bounds'][1] for f in frames),status='STRUCTURE_PASS_NOT_VISUAL_APPROVAL')
        if record.get('pivotMode'):page['pivotMode']=record['pivotMode']
        if record.get('scaleMode'):page['scaleMode']=record['scaleMode']
        if record.get('unboundRows'):page['unboundSourceFrames']=record['unboundRows']*record['columns']
        page.update(preview)
        page.update(timing)
        return page

def covers(job,accepted,approved_only=False):
    pages=[p for p in accepted if p['id']==job['id'] or any(p['id']==job['id']+'_'+d for d in ['n','ne','e','se','s','sw','w','nw'])]
    # Match ActorLibraryData.Resolve: a directional replacement shadows the
    # inherited common page even while the replacement is held/unreviewed.
    # Filtering before selecting would incorrectly count an approved legacy
    # source that the runtime cannot resolve in approval-only mode.
    effective={}
    for page in pages:
        priority=0 if page['id']==job['id'] else 1
        for direction in page['directions']:
            if direction['flip']:continue
            name=direction['direction']
            if name not in effective or priority>effective[name][0]:
                effective[name]=(priority,page['productionApproved'])
    have={name for name,(_,approved) in effective.items() if not approved_only or approved}
    need={'OMNI' if d=='OMNI_OR_ROTATED' else d for d in job['directions']}
    return need<=have

def main(export,require_complete,check=False):
    records=json.loads((ART/'generation_records.json').read_text(encoding='utf8'));accepted=[];rejected=[]
    assert len({r['id'] for r in records})==len(records),'duplicate active source IDs; move superseded versions to history'
    for r in records:
        try:accepted.append(inspect(r))
        except (AssertionError,OSError) as e:rejected.append(dict(id=r['id'],reason=str(e)))
    # Reuse the already delivered sixteen-frame Minh Kiếm clips, with explicit provenance.
    old_path=ROOT/'ClientGodot/assets/motion16/manifest.json'
    old=json.loads(old_path.read_text(encoding='utf8'))
    for action,legacy in [('idle','idle'),('walk','walk'),('basic_attack','attack')]:
        directions=[]
        for d,clip in enumerate(old['clips'][legacy]):
            frames=[dict(rect=f['rect'],pivot=f['pivot'],bounds=f['bounds'],file='res://assets/motion16/'+f['file']) for f in clip['frames']]
            assert len(frames)==16
            directions.append(dict(direction=old['directionOrder'][d],flip=d>=5,referenceHeight=clip['sourceHeight'],frames=frames))
        accepted.append(dict(id='class_minh_kiem_'+action,file='',source='ClientGodot/assets/motion16/manifest.json#'+legacy,
            sha256=hashlib.sha256(json.dumps(old['clips'][legacy],sort_keys=True).encode()).hexdigest(),directions=directions,sourceFrames=80,framesPerDirection=16,
            referenceHeight=statistics.median(d['referenceHeight'] for d in directions),status='EXISTING_NATIVE_MOTION16',legacy=True))
    review=json.loads((ART/'visual_review.json').read_text(encoding='utf8'))
    holds={h['id']:h['reason'] for h in review['holds']};approved=set(review['productionApproved'])
    component_hashes={r['id']:r.get('sourceSha256') for r in review.get('componentApprovals',[])}
    source_approvals={r['id']:r for r in review.get('sourceApprovals',[])}
    for page in accepted:
        page['bindingSha256']=binding_sha256(page)
        source_changed=(page['id'] in component_hashes and page['sha256']!=component_hashes[page['id']]) or (page['id'] in source_approvals and not source_approval_matches(page,source_approvals[page['id']]))
        page['productionApproved']=bool(page.get('legacy') or (page['id'] in approved and not source_changed))
        page['visualState']='EXISTING_NATIVE_APPROVED' if page.get('legacy') else 'HOLD' if source_changed else 'APPROVED' if page['id'] in approved else 'HOLD' if page['id'] in holds else 'AWAITING_VISUAL_REVIEW'
        page['visualNotes']=holds.get(page['id'],'')
        if source_changed:page['visualNotes']='Approved source or registration changed; native visual review required again.'
        # 12/11 owner returned to baked sheets. Keep actual visual holds/review states;
        # changing art direction does NOT approve a candidate or manufacture missing clips.
    def save(path,value):
        rendered=json.dumps(value,ensure_ascii=False,indent=2)+'\n'
        if check:assert path.read_text(encoding='utf8')==rendered,'stale metadata: '+str(path)
        else:path.write_text(rendered,encoding='utf8')
    result=dict(schemaVersion=1,renderTargetFps=60,framesPerDirection=16,pages=accepted,rejected=rejected)
    save(ART/'structure_report.json',result)
    if export:
        import shutil
        (RUN/'sheets').mkdir(parents=True,exist_ok=True)
        for page in accepted:
            if not page.get('legacy'):
                if check:assert (RUN/page['file']).read_bytes()==(ART/page['source']).read_bytes(),'runtime source mismatch: '+page['id']
                else:shutil.copyfile(ART/page['source'],RUN/page['file'])
        save(RUN/'pages.json',dict(schemaVersion=1,pages=accepted))
    catalog=json.loads((ART/'production_catalog.json').read_text(encoding='utf8'))
    jobs=json.loads((ART/'generation_jobs.json').read_text(encoding='utf8'))
    def covered(job,approved_only=False):
        # Directional repairs reference original PNGs; no atlas concatenation or pose padding.
        return covers(job,accepted,approved_only)
    pending=[j['id'] for j in jobs if not covered(j)]
    coverage=dict(actors=len(catalog['actors']),requiredPages=len(jobs),structurePassed=len(accepted),boundRequiredPages=sum(covered(j) for j in jobs),legacyClips=3,rejected=rejected,pendingPages=len(pending),pendingIds=pending,
        productionApprovedPages=sum(covered(j,True) for j in jobs),visualHoldPages=sum(p['visualState']=='HOLD' for p in accepted),modularMigrationReferencePages=sum(p['visualState']=='REFERENCE_ONLY_MODULAR_MIGRATION' for p in accepted),structureComplete=not pending and not rejected,
        complete=all(covered(j,True) for j in jobs) and not rejected,warning='Structure pass is not visual/animation/native approval. Partial directional pages do not complete a job until every required authored direction exists. Mirrored directions are frame references, not separately authored poses.')
    save(ART/'coverage.json',coverage)
    print(json.dumps({k:v for k,v in coverage.items() if k!='pendingIds'},ensure_ascii=False))
    if require_complete:assert coverage['complete'],'actor/VFX library remains incomplete'
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--export',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--require-complete',action='store_true');a=p.parse_args();main(a.export,a.require_complete,a.check)
