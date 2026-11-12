"""Register authored boots/neutral body height; never edit or resample PNGs."""
import argparse,json
from PIL import Image
from inspect_actor_library import ART,inspect,boot_foot_pivot


def calibrate(record):
    raw={k:v for k,v in record.items() if k not in ('pivotMode','bodyReferenceHeight','registrationCalibration')}
    raw['gutterPolicy']='SOLID_CORE_GUTTER'
    page=inspect(raw);frames=page['directions'][0]['frames']
    assert len(page['directions'])==1 and len(frames)==16,'directional sixteen-frame source required'
    frame=frames[0];x,y,w,h=frame['rect']
    with Image.open(ART/record['source']) as image:
        region=image.crop((x,y,x+w,y+h))
        pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
        pivot=boot_foot_pivot(pixels,w,h)
    height=pivot[1]-frame['bounds'][1]
    assert 16<=height<=h,'invalid neutral head-to-boots height'
    return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],
                pivotMode='BOOT_CORE_FOOT',gutterPolicy='SOLID_CORE_GUTTER',bodyReferenceHeight=height,
                neutralSourceFrames=[0],method='NEUTRAL_FRAME_ZERO_HEAD_TO_BROWN_BOOTS_WITH_FIXED_TWO_PIXEL_SOLE_OFFSET',
                note='Lower brown boot/pants components only. Silver sword/gold guard excluded; no raster warp. Native ground/contact review still required.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    path=ART/'generation_records.json';records=json.loads(path.read_text(encoding='utf8'))
    selected=[r for r in records if r.get('batch')=='20261113c' and r['id'].startswith('class_minh_kiem_')]
    assert len(selected)==15 and len({r['id'] for r in selected})==15,'requires three skills x five authored angles'
    entries=[calibrate(r) for r in selected]
    if args.apply:
        for record,entry in zip(selected,entries):
            for key in ('pivotMode','gutterPolicy','bodyReferenceHeight'):record[key]=entry[key]
            record['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261113c.json'
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261113c.json').write_text(json.dumps(dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',sourcePages=15,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,pages=len(entries),bodyHeights={r['id']:r['bodyReferenceHeight'] for r in entries})))
