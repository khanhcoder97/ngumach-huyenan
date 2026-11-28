"""J-only visual attachment. RGBA stays untouched; contacts are authoring assumptions."""
import argparse,hashlib,json,math,statistics
from PIL import Image
from inspect_actor_library import ART,inspect,dark_boot_foot_pivot
from calibrate_anh_dao_locomotion import head_registered_height


def head_landmark(region,bounds):
    band=[bounds[0],bounds[1],bounds[2],round(bounds[1]+(bounds[3]-bounds[1])*.42)]
    box=region.getchannel('A').crop(tuple(band)).point(lambda a:255 if a>=200 else 0).getbbox();assert box
    return dict(span=box[2]-box[0],centerX=band[0]+(box[0]+box[2])/2,top=band[1]+box[1],searchRect=band)


def waist_landmark(region,bounds):
    head=head_landmark(region,bounds);span=head['span'];cx=head['centerX'];w,h=region.size
    box=[max(0,int(cx-span*.38)),max(0,int(bounds[1]+span*.9)),min(w,int(cx+span*.38)),min(h,int(bounds[1]+span*1.45))]
    data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
    points=[(i%w,i//w) for i,(r,g,b,a) in enumerate(data)
            if box[0]<=i%w<box[2] and box[1]<=i//w<box[3] and a>=200 and r>=120 and g>=75 and b<=110 and g>=r*.53 and b<g*.82]
    assert len(points)>=10,'waist palette absent; manual landmark needed'
    counts={y:sum(py==y for _,py in points) for y in range(box[1],box[3])}
    peak=max(counts,key=lambda y:sum(counts.get(y+d,0) for d in range(-2,3)))
    belt=[p for p in points if abs(p[1]-peak)<=2];assert len(belt)>=10
    return dict(position=[statistics.median(p[0] for p in belt),statistics.median(p[1] for p in belt)],searchRect=box,goldPixels=len(belt))


def both_boot_landmark(region,bounds):
    """Horizontal midpoint uses both boot fills, not whichever sole is lowest."""
    w,h=region.size;data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
    cutoff=bounds[1]+(bounds[3]-bounds[1])*.8
    candidates={(i%w,i//w) for i,(r,g,b,a) in enumerate(data)
                if i//w>=cutoff and a>=200 and 18<=r<=130 and 12<=g<=110 and 10<=b<=115
                and r>=g*1.25 and r>=b*1.12 and g>=b*.75 and b>=g*.8}
    points={p for p in candidates if sum((p[0]+dx,p[1]+dy) in candidates for dx in (-1,0,1) for dy in (-1,0,1))>=5}
    groups=[]
    while points:
        stack=[points.pop()];group=[]
        while stack:
            x,y=stack.pop();group.append((x,y))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    neighbor=(x+dx,y+dy)
                    if neighbor in points:points.remove(neighbor);stack.append(neighbor)
        if len(group)>=16:groups.append(group)
    assert groups,'bilateral boot fill absent; manual root review needed'
    largest=max(map(len,groups));selected=sorted((g for g in groups if len(g)>=max(16,largest*.18)),key=lambda g:(-len(g),min(g)))[:2]
    solid=[p for group in selected for p in group]
    return dict(centerX=(min(p[0] for p in solid)+max(p[0] for p in solid))/2,cutoffY=cutoff,componentSizes=[len(g) for g in selected])


def run_ground_trace(anchors,contact0_y,contact8_y,horizontal_offset):
    assert len(anchors)==16 and all(len(p)==2 and all(math.isfinite(v) for v in p) for p in anchors)
    assert all(math.isfinite(v) for v in (contact0_y,contact8_y,horizontal_offset))
    first=contact0_y-anchors[0][1];opposite=contact8_y-anchors[8][1];result=[]
    for i,anchor in enumerate(anchors):
        # A visual ground trace between visible contacts, not a physics path.
        # Crucially, a folded airborne boot never becomes the actor root.
        blend=i/8 if i<=8 else (16-i)/8
        distance=first*(1-blend)+opposite*blend
        result.append([anchor[0]+horizontal_offset,anchor[1]+distance])
    return result


def raw_page(record):
    clean={k:v for k,v in record.items() if k not in ('bodyReferenceHeight','pivotMode','sourceFootPivots')}
    return inspect({**clean,'gutterPolicy':'SOLID_CORE_GUTTER'})


def calibrate(records):
    old={r['id']:r for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8'))}
    pages={p['id']:p for p in json.loads((ART/'structure_report.json').read_text(encoding='utf8'))['pages']}
    idle_cal={e['id']:e for e in json.loads((ART/'body_registration_20261113i.json').read_text(encoding='utf8'))['entries'] if '_idle_' in e['id']}
    references={}
    for direction in ('n','ne','e','se','s'):
        key='class_anh_dao_idle_'+direction;r=old[key];p=pages[key];f=p['directions'][0]['frames'][0];x,y,w,h=f['rect']
        assert hashlib.sha256((ART/r['source']).read_bytes()).hexdigest()==p['sha256']
        with Image.open(ART/r['source']) as im:
            region=im.crop((x,y,x+w,y+h));waist=waist_landmark(region,f['bounds']);head=head_landmark(region,f['bounds']);boots=both_boot_landmark(region,f['bounds'])
        references[direction]=dict(id=key,headSpan=idle_cal[key]['headSpan'],height=r['bodyReferenceHeight'],
                                   horizontalOffset=f['pivot'][0]-waist['position'][0],headHorizontalOffset=f['pivot'][0]-head['centerX'],
                                   bootHorizontalOffset=f['pivot'][0]-boots['centerX'],waist=waist,head=head,boots=boots,sourceSha256=p['sha256'])
    entries=[]
    for record in records:
        page=raw_page(record);frames=page['directions'][0]['frames'];assert len(frames)==16
        ref=references[record['direction'].lower()];is_movement='_run_' in record['id'] or record['id']=='class_anh_dao_walk_e'
        with Image.open(ART/record['source']) as im:
            neutral=frames[0];x,y,w,h=neutral['rect'];head=head_landmark(im.crop((x,y,x+w,y+h)),neutral['bounds'])
            height=head_registered_height(ref['height'],ref['headSpan'],head['span'])
            entry=dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],bodyReferenceHeight=height,
                       gutterPolicy='SOLID_CORE_GUTTER',pivotMode='SOURCE_FOOT_PIVOTS',
                       headSpan=head['span'],headSearchRect=head['searchRect'],idleReference=ref,
                       method='HEAD_PACKING_STABILISATION_WITH_CONTACT_TRACED_VIRTUAL_GROUND' if is_movement else 'BOTH_BOOT_MIDPOINT_WITH_VISIBLE_GROUNDED_SOLE',
                       scope='VISUAL_ATTACHMENT_REQUIRES_NATIVE_REVIEW_NOT_PHYSICS_OR_ROOT_MOTION',rasterModified=False)
            if is_movement:
                waists=[];heads=[];feet=[]
                for f in frames:
                    x,y,w,h=f['rect'];region=im.crop((x,y,x+w,y+h));waists.append(waist_landmark(region,f['bounds']))
                    heads.append(head_landmark(region,f['bounds']))
                    data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    feet.append(dark_boot_foot_pivot(data,w,h))
                pivots=run_ground_trace([[v['centerX'],v['top']] for v in heads],feet[0][1],feet[8][1],ref['headHorizontalOffset']*head['span']/ref['headSpan'])
                entry.update(sourceFootPivots=pivots,headLandmarks=heads,waistLandmarks=waists,visibleFootLandmarks=feet,contactSourceFrames=[0,8],
                             bootToVirtualGroundPx=[feet[i][1]-pivots[i][1] for i in range(16)],
                             assumption='Visible contacts0/8; linear head-to-root offset between contacts, closed at16. Stable head landmarks remove atlas packing drift; gold waist measurements are diagnostics only. Airborne feet never define the root. This debug root is not a physical plane for every projected foot; native gait/transition review remains required.')
            else:
                feet=[];boots=[]
                for f in frames:
                    x,y,w,h=f['rect'];region=im.crop((x,y,x+w,y+h));boots.append(both_boot_landmark(region,f['bounds']))
                    data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                    feet.append(dark_boot_foot_pivot(data,w,h))
                offset=ref['bootHorizontalOffset']*head['span']/ref['headSpan']
                entry.update(sourceFootPivots=[[boot['centerX']+offset,foot[1]] for boot,foot in zip(boots,feet)],
                             bootLandmarks=boots,visibleFootLandmarks=feet,
                             assumption='Grounded actions use both boot silhouettes for horizontal centering and visible lowest soles for vertical contact. Preserve authored head nod/weapon motion; neither foot alone may yank the horizontal root. Native review required.')
        entries.append(entry)
    return entries


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--candidates',action='store_true');args=parser.parse_args()
    path=ART/'Candidates_20261113j/candidate_manifest.json' if args.candidates else ART/'generation_records.json'
    container=json.loads(path.read_text(encoding='utf8'));records=container['records'] if args.candidates else container
    selected=[r for r in records if r.get('batch')=='20261113j'];assert len(selected)==21
    entries=calibrate(selected)
    if args.apply:
        for r,e in zip(selected,entries):
            for key in ('bodyReferenceHeight','pivotMode','gutterPolicy'):r[key]=e[key]
            if 'sourceFootPivots' in e:r['sourceFootPivots']=e['sourceFootPivots']
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261113j.json';inspect(r)
        path.write_text(json.dumps(container,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261113j.json').write_text(json.dumps(dict(scope='GEOMETRY_ONLY_NOT_VISUAL_APPROVAL',sourcePages=21,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,pages=len(entries),runs={e['id']:[round(x,1) for x in e['bootToVirtualGroundPx']] for e in entries if 'bootToVirtualGroundPx' in e})))
