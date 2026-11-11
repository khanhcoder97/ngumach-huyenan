"""Read-only raster inspection and metadata export. Never edits/resamples a bitmap."""
import argparse,hashlib,json,statistics
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[2];ART=ROOT/'Art_Source/Actor_Library_20261107';RUN=ROOT/'ClientGodot/assets/actor_library_v1'
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

def inspect(record, art_root=None):
    path=(art_root or ART)/record['source']
    with Image.open(path) as im:
        assert im.mode=='RGBA','PNG must retain RGBA'
        w,h=im.size;a=im.getchannel('A');assert a.getextrema()[0]==0,'opaque fake background'
        # Projection locates the actual transparent gutters instead of assuming a cropped output retained equal cells.
        mask=a.point(lambda x:255 if x>=200 else 0);pix=mask.load();xs=[0]*w;ys=[0]*h
        for y in range(h):
            for x in range(w):
                if pix[x,y]:xs[x]+=1;ys[y]+=1
        if record.get('layout')=='VISUALLY_VERIFIED_UNIFORM_GRID':
            # Particle islands do not define extra columns/rows. Only opt in after
            # viewing the whole sheet; per-cell emptiness, edge and hash checks remain.
            assert (record['columns'],record['rows'])==(4,4) and record['id'].startswith('sk_'),'explicit grid currently restricted to reviewed 16-frame effects'
            xx=[round(i*w/4) for i in range(5)];yy=[round(i*h/4) for i in range(5)]
            cols=list(zip(xx,xx[1:]));rows=list(zip(yy,yy[1:]))
        else:
            cols=locate(xs,record['columns'],max(2,int(w/100)))
            rows=locate(ys,record['rows'],max(2,int(h/120)))
            assert len(cols)==record['columns'],f"columns expected {record['columns']}, got {len(cols)}"
            assert len(rows)==record['rows'],f"rows expected {record['rows']}, got {len(rows)}"
            edges=lambda groups,maximum:[0]+[round((a[1]+b[0])/2) for a,b in zip(groups,groups[1:])]+[maximum]
            xx=edges(cols,w);yy=edges(rows,h)
        frames=[];hashes=[]
        for row in range(len(rows)):
            for col in range(len(cols)):
                x,y,x1,y1=xx[col],yy[row],xx[col+1],yy[row+1]
                alpha=mask.crop((x,y,x1,y1));bb=alpha.getbbox();assert bb,'empty frame'
                margin=min(bb[0],bb[1],x1-x-bb[2],y1-y-bb[3]);assert margin>=2,f'clipped/overlapping frame row{row} col{col}'
                # Foot-ground anchor is metadata only. Source pixels remain byte-identical.
                foot=alpha.crop((int((x1-x)*.25),int((y1-y)*.6),int((x1-x)*.75),y1-y)).getbbox()
                pivot=[(bb[0]+bb[2])/2,bb[3]] if not foot else [int((x1-x)*.25)+(foot[0]+foot[2])/2,int((y1-y)*.6)+foot[3]]
                if record.get('pivotMode')=='CELL_CENTER':
                    assert record['id'].startswith('sk_'),'cell-center mode is VFX-only'
                    pivot=[(x1-x)/2,(y1-y)/2]
                frames.append(dict(rect=[x,y,x1-x,y1-y],bounds=list(bb),pivot=pivot))
                hashes.append(hashlib.sha256(im.crop((x,y,x1,y1)).tobytes()).hexdigest())
        assert len(set(hashes))==len(hashes),'duplicate full-frame pixels; frame count cannot be padded'
        directions=[]
        if len(cols)==8 and (len(rows) in (2,4,6,8,10) or record.get('unboundRows')==1):
            authored=record.get('authoredDirections') or ['N','NE','E','SE','S']
            assert len(authored)*2+record.get('unboundRows',0)==len(rows) and len(set(authored))==len(authored),'partial atlas must declare its actual direction blocks and unused rows'
            assert all(d in ['N','NE','E','SE','S','SW','W','NW'] for d in authored)
            for source,name in enumerate(authored):
                block=frames[source*16:source*16+16];assert len(block)==16
                # Page resolution varies. Calibrate from the neutral first poses, never
                # scale a lying death pose back up to standing height.
                height=statistics.median(f['bounds'][3]-f['bounds'][1] for f in block[:3])
                directions.append(dict(direction=name,flip=False,referenceHeight=height,frames=block))
            if record.get('mirrorAllowed',True):
                for target,source in [('SW','SE'),('W','E'),('NW','NE')]:
                    if target not in authored and source in authored:
                        original=next(d for d in directions if d['direction']==source)
                        directions.append(dict(direction=target,flip=True,referenceHeight=original['referenceHeight'],frames=original['frames']))
            directions.sort(key=lambda d:['N','NE','E','SE','S','SW','W','NW'].index(d['direction']))
        elif (len(cols),len(rows))==(4,4):
            vfx=record['id'].startswith('sk_');height=max(f['bounds'][3]-f['bounds'][1] for f in frames) if vfx else statistics.median(f['bounds'][3]-f['bounds'][1] for f in frames[:3])
            directions=[dict(direction=record.get('direction') or ('OMNI' if vfx else 'S'),flip=False,referenceHeight=height,frames=frames)]
        else:raise AssertionError('unreviewed atlas layout')
        page=dict(id=record['id'],file='sheets/'+path.name,source=record['source'],sha256=hashlib.sha256(path.read_bytes()).hexdigest(),imageSize=[w,h],directions=directions,
            sourceFrames=len(frames),framesPerDirection=16,referenceHeight=statistics.median(f['bounds'][3]-f['bounds'][1] for f in frames),status='STRUCTURE_PASS_NOT_VISUAL_APPROVAL')
        if record.get('unboundRows'):page['unboundSourceFrames']=record['unboundRows']*record['columns']
        return page

def covers(job,accepted,approved_only=False):
    pages=[p for p in accepted if p['id']==job['id'] or any(p['id']==job['id']+'_'+d for d in ['n','ne','e','se','s','sw','w','nw'])]
    if approved_only:pages=[p for p in pages if p['productionApproved']]
    have={d['direction'] for p in pages for d in p['directions'] if not d['flip']}
    need={'OMNI' if d=='OMNI_OR_ROTATED' else d for d in job['directions']}
    return need<=have

def main(export,require_complete,check=False):
    records=json.loads((ART/'generation_records.json').read_text(encoding='utf8'));accepted=[];rejected=[]
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
    for page in accepted:
        source_changed=page['id'] in component_hashes and page['sha256']!=component_hashes[page['id']]
        page['productionApproved']=bool(page.get('legacy') or (page['id'] in approved and not source_changed))
        page['visualState']='EXISTING_NATIVE_APPROVED' if page.get('legacy') else 'HOLD' if source_changed else 'APPROVED' if page['id'] in approved else 'HOLD' if page['id'] in holds else 'AWAITING_VISUAL_REVIEW'
        page['visualNotes']=holds.get(page['id'],'')
        if source_changed:page['visualNotes']='Approved component source hash changed; native visual review required again.'
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
