"""Read-only source geometry; apply fixed per-clip neutral-height metadata only."""
import argparse,json,statistics
from inspect_actor_library import ART,inspect


def height(frame):return frame['bounds'][3]-frame['bounds'][1]


def calibrate(records):
    selected=[r for r in records if r.get('batch')=='20261113b' and r['id'].startswith('mob_waterroot_')]
    assert len(selected)==15 and len({r['id'] for r in selected})==15,'requires 3 phases x 5 authored angles'
    raw={}
    for record in selected:
        source={k:v for k,v in record.items() if k not in ('bodyReferenceHeight','registrationCalibration')}
        raw[record['id']]=inspect(source)
    entries=[];joins=[]
    for facing in ('n','ne','e','se','s'):
        ids=['mob_waterroot_'+a+'_02_'+facing for a in ('telegraph','attack','recovery')]
        frames=[raw[i]['directions'][0]['frames'] for i in ids]
        tell=statistics.median(height(f) for f in frames[0][:3])
        recovery=statistics.median(height(f) for f in frames[2][-3:])
        # Solve ONE constant attack scale to minimize both charged boundary
        # height differences. No per-frame scaling, resampling or pose warping.
        a0,a1=height(frames[1][0]),height(frames[1][-1])
        t1,r0=height(frames[0][-1])/tell,height(frames[2][0])/recovery
        attack=(a0*a0+a1*a1)/(a0*t1+a1*r0)
        refs=[tell,attack,recovery]
        for index,id in enumerate(ids):
            assert 16<=refs[index]<=raw[id]['imageSize'][1]/4,'invalid neutral calibration'
            entries.append(dict(id=id,sourceSha256=raw[id]['sha256'],bodyReferenceHeight=refs[index],pivotMode='FOOT',
                                neutralSourceFrames=[0,1,2] if index==0 else [13,14,15] if index==2 else [],
                                method='NEUTRAL_FIRST_THREE' if index==0 else 'NEUTRAL_LAST_THREE' if index==2 else 'ONE_FIXED_SCALE_LEAST_SQUARES_BOTH_CHARGED_BOUNDARIES',
                                boundaryReferenceIds=ids if index==1 else []))
        for index in (0,1):
            before=height(frames[index][-1])/refs[index]*88
            after=height(frames[index+1][0])/refs[index+1]*88
            joins.append(dict(direction=facing.upper(),before=ids[index],after=ids[index+1],
                              renderedEndHeightPx=before,renderedStartHeightPx=after,heightJumpPx=abs(after-before)))
    return dict(scope='FIXED_SOURCE_HEIGHT_GEOMETRY_NOT_VISUAL_OR_ENCOUNTER_APPROVAL',reviewHeightPx=88,
                sourcePages=15,entries=entries,phaseJoins=joins,maximumHeightJumpPx=max(j['heightJumpPx'] for j in joins),
                note='Foot pivots track source ground; compression remains authored. Boundary height is a scalar diagnostic, not silhouette/pose continuity proof. Native review required.')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
    path=ART/'generation_records.json';records=json.loads(path.read_text(encoding='utf8'))
    result=calibrate(records)
    if a.apply:
        by_id={r['id']:r for r in records}
        for entry in result['entries']:
            record=by_id[entry['id']];record['bodyReferenceHeight']=entry['bodyReferenceHeight']
            record['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261113b.json'
        path.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261113b.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=a.apply,sourcePages=15,maximumHeightJumpPx=result['maximumHeightJumpPx'])))
