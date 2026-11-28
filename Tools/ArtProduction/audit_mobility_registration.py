"""Read-only landmark diagnostics; this does not approve animation or measure FPS."""
import argparse, hashlib, json, math
from PIL import Image
from inspect_actor_library import ART
from calibrate_anh_dao_mobility import head_landmark


def hair_landmark(region,bounds):
    """Exclude a raised silver dao from the head diagnostic in combat poses."""
    w,h=region.size;top=bounds[1];bottom=top+(bounds[3]-top)*.42
    data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
    points={(i%w,i//w) for i,(r,g,b,a) in enumerate(data)
            if top<=i//w<bottom and a>=200 and 20<=r<=160 and 15<=g<=130 and 15<=b<=140
            and r>=g*1.05 and r>=b*.95 and b>=g*.85}
    assert len(points)>100,'hair core absent; manual diagnostic required'
    groups=[]
    while points:
        stack=[points.pop()];group=[]
        while stack:
            x,y=stack.pop();group.append((x,y))
            for dx in (-1,0,1):
                for dy in (-1,0,1):
                    neighbor=(x+dx,y+dy)
                    if neighbor in points:points.remove(neighbor);stack.append(neighbor)
        groups.append(group)
    points=max(groups,key=len);assert len(points)>100
    # Hair occupies most of the band. Small hilt/edge outliers cannot pull a
    # percentile envelope to a raised weapon in an otherwise empty quadrant.
    xx=sorted(x for x,y in points);yy=sorted(y for x,y in points)
    return dict(centerX=(xx[int(len(xx)*.02)]+xx[int(len(xx)*.98)])/2,top=yy[int(len(yy)*.02)])


def snapshot(baseline=None):
    if baseline:
        records=[e['sourceRecord'] for e in baseline['entries']];pages={e['id']:e['page'] for e in baseline['entries']}
    else:
        records=[r for r in json.loads((ART/'generation_records.json').read_text(encoding='utf8')) if r.get('batch')=='20261113j']
        pages={p['id']:p for p in json.loads((ART/'structure_report.json').read_text(encoding='utf8'))['pages']}
    entries=[]
    for record in records:
        page=pages[record['id']];heads=[]
        with Image.open(ART/record['source']) as image:
            assert hashlib.sha256((ART/record['source']).read_bytes()).hexdigest()==page['sha256']
            for frame in page['directions'][0]['frames']:
                x,y,w,h=frame['rect'];head=hair_landmark(image.crop((x,y,x+w,y+h)),frame['bounds'])
                scale=100/page['directions'][0].get('referenceHeight',page['referenceHeight'])
                heads.append([(head['centerX']-frame['pivot'][0])*scale,(head['top']-frame['pivot'][1])*scale])
        edges=list(zip(heads,heads[1:]))
        if '_run_' in record['id'] or '_walk_' in record['id']:edges.append((heads[-1],heads[0]))
        entries.append(dict(id=record['id'],sourceSha256=page['sha256'],bindingSha256=page['bindingSha256'],
                            sourceRecord=record,page=page,headPositionsAt100px=heads,
                            maxAdjacentHeadDeltaX=max(abs(a[0]-b[0]) for a,b in edges),
                            maxAdjacentHeadDeltaY=max(abs(a[1]-b[1]) for a,b in edges)))
    return dict(scope='LANDMARK_DIAGNOSTICS_ONLY_NOT_POSE_ACCEPTANCE_OR_FPS',headDiagnostic='LARGEST_CONNECTED_BROWN_HAIR_PERCENTILE_CORE_EXCLUDES_RAISED_DAO',entries=entries)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--baseline');args=parser.parse_args()
    from pathlib import Path
    result=snapshot(json.loads(Path(args.baseline).read_text(encoding='utf8')) if args.baseline else None)
    Path(args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps([{k:e[k] for k in ('id','maxAdjacentHeadDeltaX','maxAdjacentHeadDeltaY')} for e in result['entries']]))
