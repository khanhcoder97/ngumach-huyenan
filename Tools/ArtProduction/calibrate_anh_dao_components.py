"""Read-only VFX attachment registration. Coordinates only; never paints/crops an output."""
import argparse,json,statistics
from PIL import Image
from inspect_actor_library import ART,inspect


def calibrate(record):
    raw={k:v for k,v in record.items() if k not in ('sourcePivots','pivotMode')}
    raw['pivotMode']='CELL_CENTER'
    page=inspect(raw);frames=page['directions'][0]['frames'];assert len(frames)==16
    if record['id'] in ('sk_ad_04_slow_mark_component','sk_ad_06_charge_component'):
        return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],pivotMode='SYMMETRIC_BOUNDS_CENTER',method='DRAWN_SYMMETRIC_MARK_OR_CONVERGENCE_CENTER')
    leading=record['id'] in ('sk_ad_04_down_cut_component','sk_ad_05_smoke_component')
    pivots=[]
    with Image.open(ART/record['source']) as image:
        if leading:
            axis=1 if record['id']=='sk_ad_04_down_cut_component' else 0
            for f in frames:
                x,y,w,h=f['rect'];region=image.crop((x,y,x+w,y+h));data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
                hot=[(i%w,i//w) for i,(r,g,b,a) in enumerate(data) if a>=64 and r>=170 and g>=65 and b<=130 and r>=g*1.15]
                if hot:
                    edge=max(p[axis] for p in hot);tip=[p for p in hot if p[axis]>=edge-2]
                    pivots.append([sum(p[0] for p in tip)/len(tip),sum(p[1] for p in tip)/len(tip)])
                else:
                    b=f['bounds'];pivots.append([(b[0]+b[2])/2,b[3]-1] if axis else [b[2]-1,(b[1]+b[3])/2])
            method='LOWER_HOT_IMPACT_TIP' if axis else 'RIGHT_HOT_TRAIL_HEAD_DARK_BOUND_FALLBACK'
        else:
            # Peak source5..9 defines the invisible origin for partial arcs and
            # fragments. Do not attach each shrinking fragment by its own box.
            absolute=lambda i,axis:frames[i]['rect'][axis]+(frames[i]['bounds'][axis]+frames[i]['bounds'][axis+2])/2
            peak=[5,6,7,8,9]
            columns=[statistics.median(absolute(i,0) for i in peak if i%4==col) for col in range(4)]
            row1=statistics.median(absolute(i,1) for i in (5,6,7));row2=statistics.median(absolute(i,1) for i in (8,9));pitch=row2-row1
            assert pitch>0
            for i,f in enumerate(frames):pivots.append([columns[i%4]-f['rect'][0],row1+(i//4-1)*pitch-f['rect'][1]])
            method='PEAK_GRID_ORIGIN_EXTRAPOLATED_ACROSS_OPENING_AND_FADE'
    return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],pivotMode='SOURCE_PIVOTS',sourcePivots=pivots,method=method,
                note='Attachment recipe only; inspect native origin continuity before source pin. No raster edits or gameplay/collision authority.')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    path=ART/'generation_records.json';records=json.loads(path.read_text(encoding='utf8'))
    selected=[r for r in records if r.get('batch')=='20261113g' and r['id'].startswith('sk_')];assert len(selected)==6
    entries=[calibrate(r) for r in selected]
    if args.apply:
        for r,entry in zip(selected,entries):
            r['pivotMode']=entry['pivotMode'];r.pop('sourcePivots',None)
            if 'sourcePivots' in entry:r['sourcePivots']=entry['sourcePivots']
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/component_registration_20261113g.json'
            inspect(r)
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'component_registration_20261113g.json').write_text(json.dumps(dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_ATTACHMENT_REVIEW',sourcePages=6,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,pages=len(entries),methods={e['id']:e['method'] for e in entries})))
