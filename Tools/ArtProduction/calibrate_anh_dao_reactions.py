"""Read original RGBA only. H reaction-specific registration, never a physics solver."""
import argparse,json,statistics
from PIL import Image
from inspect_actor_library import ART,inspect


def dark_points(region,box):
    w,h=region.size;data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
    points={(i%w,i//w) for i,(r,g,b,a) in enumerate(data)
            if box[0]<=i%w<box[2] and box[1]<=i//w<box[3] and a>=200 and max(r,g,b)<=150}
    # Thin steel contours must not define a foot. This reads dense original fill.
    return [p for p in points if sum((p[0]+dx,p[1]+dy) in points for dx in (-1,0,1) for dy in (-1,0,1))>=6]


def calibrate(record):
    raw={k:v for k,v in record.items() if k not in ('bodyReferenceHeight','pivotMode','sourceFootPivots')}
    raw['gutterPolicy']='SOLID_CORE_GUTTER';page=inspect(raw);frames=page['directions'][0]['frames']
    assert len(frames)==16 and len(page['directions'])==1
    front_fall=record['id']=='class_anh_dao_death_s';death='_death_' in record['id'];pivots=[];landmarks=[]
    with Image.open(ART/record['source']) as image:
        for i,f in enumerate(frames):
            x,y,w,h=f['rect'];b=f['bounds'];bw=b[2]-b[0];bh=b[3]-b[1]
            box=[b[0],b[1]+bh*.60,b[2],b[3]];method='DENSE_LOWER_SOLES'
            if death and i>=8 and not front_fall:
                # N/NE/E/SE lie with the boots at the left of the visible head.
                # This source-specific window excludes the head and right hand.
                box=[b[0],b[1]+bh*.45,b[0]+bw*.43,b[3]];method='VISIBLE_REAR_BOOT_REGION'
            if front_fall and i>=12:
                # Front-facing prone feet are ABOVE the hair, not below it.
                box=[b[0],b[1],b[2],b[1]+24];method='VISIBLE_PAIRED_BOOTS_ABOVE_HEAD'
            points=dark_points(image.crop((x,y,x+w,y+h)),box);assert len(points)>=8,f'foot region absent: {record["id"]}/{i}'
            if front_fall and i>=12:
                pivot=[(min(p[0] for p in points)+max(p[0] for p in points))/2,
                       (min(p[1] for p in points)+max(p[1] for p in points))/2+2]
            else:
                bottom=max(p[1] for p in points);sole=[p for p in points if p[1]>=bottom-max(4,bh*.035)]
                pivot=[statistics.mean(p[0] for p in sole),bottom+1]
            pivots.append(pivot);landmarks.append(dict(frame=i,searchRect=box,method=method))
    if death:
        # Hidden feet between kneeling and prone need a continuous authoring
        # origin. Trace in pose-bound coordinates, not global atlas coordinates.
        # This is an attachment assumption requiring native review, not measured
        # movement, a rigid transform of source poses, or gameplay root motion.
        normalized=lambda i:[(pivots[i][a]-frames[i]['bounds'][a])/(frames[i]['bounds'][a+2]-frames[i]['bounds'][a]) for a in (0,1)]
        target=12 if front_fall else 8
        start,end=normalized(5),normalized(target)
        for i in range(6,target):
            t=(i-5)/(target-5);b=frames[i]['bounds'];pivots[i]=[b[a]+(start[a]*(1-t)+end[a]*t)*(b[a+2]-b[a]) for a in (0,1)]
            landmarks[i]=dict(frame=i,method='OCCLUDED_FOOT_ORIGIN_TRACE_BETWEEN_VISIBLE_LANDMARKS',assumption=True)
    height=pivots[0][1]-frames[0]['bounds'][1]
    return dict(id=record['id'],source=record['source'],sourceSha256=page['sha256'],pivotMode='SOURCE_FOOT_PIVOTS',gutterPolicy='SOLID_CORE_GUTTER',
                sourceFootPivots=pivots,bodyReferenceHeight=height,landmarks=landmarks,
                scope='ATTACHMENT_RECIPE_REQUIRES_NATIVE_REVIEW_NOT_PHYSICS_OR_GAMEPLAY',rasterModified=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--candidates',action='store_true');args=parser.parse_args()
    path=ART/'Candidates_20261113h/candidate_manifest.json' if args.candidates else ART/'generation_records.json'
    container=json.loads(path.read_text(encoding='utf8'));records=container['records'] if args.candidates else container
    selected=[r for r in records if r.get('batch')=='20261113h'];assert len(selected)==10
    entries=[calibrate(r) for r in selected]
    if args.apply:
        for r,entry in zip(selected,entries):
            for key in ('pivotMode','gutterPolicy','sourceFootPivots','bodyReferenceHeight'):r[key]=entry[key]
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261113h.json'
            inspect(r)
        path.write_text(json.dumps(container,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261113h.json').write_text(json.dumps(dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_ATTACHMENT_REVIEW',sourcePages=10,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=args.apply,pages=len(entries),heights={e['id']:e['bodyReferenceHeight'] for e in entries})))
