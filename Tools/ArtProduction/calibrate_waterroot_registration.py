"""Read source geometry to register Waterroot's stump; never draw/edit a bitmap."""
import argparse,json,statistics
from pathlib import Path
from PIL import Image
from inspect_actor_library import inspect,moss_body_pivot

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'Art_Source/Actor_Library_20261107'


def calibrate(record):
    raw=dict(record)
    for key in ('pivotMode','bodyReferenceHeight','rootFootOffset','registrationCalibration'):raw.pop(key,None)
    page=inspect(raw)
    assert len(page['directions'])==1 and page['sourceFrames']==16,'directional sources only'
    # Recovery starts with a long whip. Its last neutral poses, not that whip,
    # define stump height. Other clips start neutral/charged with the root tucked.
    neutral=[13,14,15] if '_recovery_01_' in record['id'] else [0,1,2]
    frames=page['directions'][0]['frames']
    height=statistics.median(frames[i]['bounds'][3]-frames[i]['bounds'][1] for i in neutral)
    offsets=[]
    with Image.open(ART/record['source']) as source:
        for i in neutral:
            frame=frames[i];x,y,w,h=frame['rect'];region=source.crop((x,y,x+w,y+h))
            pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
            core=moss_body_pivot(pixels,w,height,[0,0])
            offsets.append([(frame['pivot'][axis]-core[axis])/height for axis in (0,1)])
    offset=[statistics.median(p[axis] for p in offsets) for axis in (0,1)]
    return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],
                neutralSourceFrames=neutral,bodyReferenceHeight=height,rootFootOffset=offset,
                pivotMode='MOSS_CORE_ROOT',method='Green-core centroid with a fixed neutral-foot offset; neutral body height held through the clip. Geometry calibration, not anatomical/native approval.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    path=ART/'generation_records.json';records=json.loads(path.read_text(encoding='utf8'))
    selected=[r for r in records if r['id'].startswith('mob_waterroot_') and any('_'+a+'_' in r['id'] for a in ('idle','telegraph_01','attack_01','recovery_01'))]
    assert len(selected)==20 and len({r['id'] for r in selected})==20,'batch e requires five idle and fifteen combat directional sources'
    result=[calibrate(r) for r in selected]
    idle={r['id'].rsplit('_',1)[-1]:r for r in result if '_idle_' in r['id']}
    assert set(idle)=={'n','ne','e','se','s'},'missing neutral angle for shared foot registration'
    for r in result:
        basis=idle[r['id'].rsplit('_',1)[-1]]
        r['rootFootOffset']=list(basis['rootFootOffset'])
        r['rootOffsetBasis']=basis['id']
        r['method']='Green-core centroid with the shared per-angle idle foot offset. Each clip uses its own neutral body height, held through the clip. Geometry calibration, not anatomical/native approval.'
    if args.apply:
        for r,c in zip(selected,result):
            for key in ('pivotMode','bodyReferenceHeight','rootFootOffset','rootOffsetBasis'):r[key]=c[key]
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261112e.json'
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261112e.json').write_text(json.dumps(dict(scope='GEOMETRY_CALIBRATION_REQUIRES_NATIVE_REVIEW',sourcePages=len(result),entries=result,fullGameComplete=False),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(pages=len(result),applied=args.apply,heights={r['id']:r['bodyReferenceHeight'] for r in result}),ensure_ascii=False))
