"""Read-only dark-boot registration recipe; optional metadata write, no bitmap edits."""
import argparse,json
from PIL import Image
from inspect_actor_library import ART,inspect,dark_boot_foot_pivot


def calibrate(record):
    raw={k:v for k,v in record.items() if k not in ('bodyReferenceHeight','pivotMode')}
    raw['gutterPolicy']='SOLID_CORE_GUTTER'
    page=inspect(raw);frames=page['directions'][0]['frames']
    assert len(page['directions'])==1 and len(frames)==16
    neutral=record.get('neutralSourceFrame',0)
    assert type(neutral) is int and 0<=neutral<16
    frame=frames[neutral];x,y,w,h=frame['rect']
    with Image.open(ART/record['source']) as image:
        region=image.crop((x,y,x+w,y+h))
        pixels=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
        pivot=dark_boot_foot_pivot(pixels,w,h)
    height=pivot[1]-frame['bounds'][1]
    assert 16<=height<=h
    return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],pivotMode='DARK_BOOT_CORE_FOOT',
                gutterPolicy='SOLID_CORE_GUTTER',bodyReferenceHeight=height,neutralSourceFrames=[neutral],
                method='DENSE_DARK_PLUM_BOOT_FILL_EXCLUDING_STEEL_GOLD_AND_THIN_CONTOURS',
                note='Fixed whole-clip neutral height; no per-frame raster scale/warp. Native sole/weapon/contact review required.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--batch',choices=('20261113f','20261113g'),default='20261113f');args=parser.parse_args()
    path=ART/'generation_records.json';records=json.loads(path.read_text(encoding='utf8'))
    selected=[r for r in records if r.get('batch')==args.batch and r['id'].startswith('class_anh_dao_')]
    expected=15 if args.batch=='20261113f' else 20
    assert len(selected)==expected and len({r['id'] for r in selected})==expected,'requires every selected action x five source angles'
    entries=[calibrate(r) for r in selected]
    if args.apply:
        for record,entry in zip(selected,entries):
            for key in ('pivotMode','gutterPolicy','bodyReferenceHeight'):record[key]=entry[key]
            record['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_'+args.batch+'.json'
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/('body_registration_'+args.batch+'.json')).write_text(json.dumps(dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',sourcePages=expected,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,pages=len(entries),heights={r['id']:r['bodyReferenceHeight'] for r in entries})))
