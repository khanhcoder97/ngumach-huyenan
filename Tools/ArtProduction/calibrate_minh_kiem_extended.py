"""Register twenty new Minh Kiem candidates without changing PNGs or granting approval."""
import argparse,hashlib,json,math
from PIL import Image
from inspect_actor_library import ART,inspect,boot_foot_pivot
from calibrate_anh_dao_mobility import head_landmark,run_ground_trace,raw_page
from calibrate_anh_dao_locomotion import head_registered_height


def brown_boot_landmark(region,bounds):
    """Both warm boot silhouettes, excluding teal cloth and bright steel/gold."""
    w,h=region.size;cutoff=bounds[1]+(bounds[3]-bounds[1])*.75
    data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
    candidates={(i%w,i//w) for i,(r,g,b,a) in enumerate(data)
                if i//w>=cutoff and a>=200 and 35<=r<=140 and 25<=g<=100 and 20<=b<=90
                and r>=g*1.18 and g>=b*1.1}
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
    assert groups,'brown boot fill missing; manual source review required'
    largest=max(map(len,groups));selected=sorted((g for g in groups if len(g)>=max(16,largest*.18)),key=lambda g:(-len(g),min(g)))[:2]
    solid=[p for group in selected for p in group]
    return dict(centerX=(min(x for x,y in solid)+max(x for x,y in solid))/2,
                bottom=min(h-1,max(y for x,y in solid)+2),componentSizes=[len(g) for g in selected],cutoffY=cutoff)


def calibrate(records):
    active={r['id']:r for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8'))}
    pages={p['id']:p for p in json.loads((ART/'structure_report.json').read_text(encoding='utf8'))['pages']}
    references={}
    for d in ('n','ne','e','se','s'):
        key='class_minh_kiem_skill_01_'+d;r=active[key];p=pages[key];direction=p['directions'][0];f=direction['frames'][0];x,y,w,h=f['rect']
        assert p['productionApproved'] and hashlib.sha256((ART/r['source']).read_bytes()).hexdigest()==p['sha256']
        with Image.open(ART/r['source']) as im:
            region=im.crop((x,y,x+w,y+h));head=head_landmark(region,f['bounds']);boots=brown_boot_landmark(region,f['bounds'])
        references[d]=dict(id=key,sourceSha256=p['sha256'],referenceHeight=direction['referenceHeight'],head=head,boots=boots,
                           headHorizontalOffset=f['pivot'][0]-head['centerX'],bootHorizontalOffset=f['pivot'][0]-boots['centerX'])
    entries=[]
    for r in records:
        page=raw_page(r);frames=page['directions'][0]['frames'];assert len(frames)==16
        ref=references[r['direction'].lower()];heads=[];boots=[];visible=[]
        with Image.open(ART/r['source']) as im:
            for f in frames:
                x,y,w,h=f['rect'];region=im.crop((x,y,x+w,y+h));heads.append(head_landmark(region,f['bounds']))
                boots.append(brown_boot_landmark(region,f['bounds']))
                data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata();visible.append(boot_foot_pivot(data,w,h))
        ratio=heads[0]['span']/ref['head']['span'];height=head_registered_height(ref['referenceHeight'],ref['head']['span'],heads[0]['span'])
        movement='_run_' in r['id']
        pivots=run_ground_trace([[h['centerX'],h['top']] for h in heads],visible[0][1],visible[8][1],ref['headHorizontalOffset']*ratio) if movement else [[b['centerX']+ref['bootHorizontalOffset']*ratio,b['bottom']] for b in boots]
        assert all(all(math.isfinite(v) for v in p) for p in pivots)
        entries.append(dict(id=r['id'],source=r['source'],sourceSha256=page['sha256'],bodyReferenceHeight=height,
            pivotMode='SOURCE_FOOT_PIVOTS',gutterPolicy='SOLID_CORE_GUTTER',sourceFootPivots=pivots,
            method='HEAD_PACKING_WITH_CONTACT_TRACED_VIRTUAL_GROUND' if movement else 'BOTH_WARM_BOOT_SILHOUETTES',
            reference=ref,headLandmarks=heads,bootLandmarks=boots,visibleBootLandmarks=visible,
            contactSourceFrames=[0,8] if movement else [],rasterModified=False,
            scope='CANDIDATE_VISUAL_ATTACHMENT_REQUIRES_NATIVE_REVIEW_NOT_PHYSICS_OR_APPROVAL'))
    return entries


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    path=ART/'Candidates_20261114a/candidate_manifest.json';m=json.loads(path.read_text(encoding='utf8'));assert len(m['records'])==20
    entries=calibrate(m['records'])
    if args.apply:
        for r,e in zip(m['records'],entries):
            assert r['id']==e['id']
            for key in ('bodyReferenceHeight','pivotMode','gutterPolicy','sourceFootPivots'):r[key]=e[key]
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261114a.json';inspect(r)
        path.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261114a.json').write_text(json.dumps(dict(scope='WIP_GEOMETRY_ONLY_NOT_VISUAL_APPROVAL',entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,candidatePages=len(entries),sourcePixelsChanged=False,productionApprovals=0)))
