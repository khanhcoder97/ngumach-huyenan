"""I-only attachment metadata. Read RGBA without repainting/resampling source art."""
import argparse,json,math
from PIL import Image
from inspect_actor_library import ART,inspect,dark_boot_foot_pivot


def head_registered_height(idle_height,idle_span,action_span):
    # A longer reaching boot is not a larger skeleton. Use the neutral head
    # silhouette to keep the same head/body display scale across the clips.
    assert all(type(v) in (int,float) and math.isfinite(v) and v>0 for v in (idle_height,idle_span,action_span))
    return idle_height*action_span/idle_span


def measure(record):
    raw={k:v for k,v in record.items() if k not in ('bodyReferenceHeight','pivotMode','sourceFootPivots')}
    raw['gutterPolicy']='SOLID_CORE_GUTTER';page=inspect(raw)
    frames=page['directions'][0]['frames'];assert len(frames)==16
    f=frames[0];x,y,w,h=f['rect'];b=f['bounds']
    with Image.open(ART/record['source']) as image:
        region=image.crop((x,y,x+w,y+h));data=region.get_flattened_data() if hasattr(region,'get_flattened_data') else region.getdata()
        foot=dark_boot_foot_pivot(data,w,h)
        # All fifteen source0 poses have the dao safely low. This upper band
        # measures only the head/hair; an overhead action must not use this recipe.
        band=[b[0],b[1],b[2],round(b[1]+(b[3]-b[1])*.42)]
        mask=region.getchannel('A').crop(tuple(band)).point(lambda a:255 if a>=200 else 0)
        head=mask.getbbox();assert head
    return dict(page=page,neutralFootHeight=foot[1]-b[1],headSpan=head[2]-head[0],headSearchRect=band)


def run(apply=False,candidates=False):
    path=ART/'Candidates_20261113i/candidate_manifest.json' if candidates else ART/'generation_records.json'
    container=json.loads(path.read_text(encoding='utf8'));records=container['records'] if candidates else container
    selected=[r for r in records if r.get('batch')=='20261113i'];assert len(selected)==15
    measured={r['id']:measure(r) for r in selected};entries=[]
    for r in selected:
        item=measured[r['id']];idle=measured['class_anh_dao_idle_'+r['direction'].lower()]
        height=head_registered_height(idle['neutralFootHeight'],idle['headSpan'],item['headSpan'])
        entry=dict(id=r['id'],source=r['source'],sourceSha256=item['page']['sha256'],bodyReferenceHeight=height,
                   pivotMode='DARK_BOOT_CORE_FOOT',gutterPolicy='SOLID_CORE_GUTTER',neutralSourceFrame=0,
                   headSpan=item['headSpan'],headSearchRect=item['headSearchRect'],idleHeadSpan=idle['headSpan'],
                   idleFootHeight=idle['neutralFootHeight'],unregisteredFootHeight=item['neutralFootHeight'],
                   method='NEUTRAL_HEAD_SCALE_WITH_DENSE_DARK_BOOT_ATTACHMENT',rasterModified=False,
                   scope='VISUAL_ATTACHMENT_ONLY_NATIVE_REVIEW_REQUIRED_NOT_ROOT_MOTION_OR_PHYSICS')
        entries.append(entry)
        if apply:
            for key in ('bodyReferenceHeight','pivotMode','gutterPolicy'):r[key]=entry[key]
            r['registrationCalibration']='Art_Source/Actor_Library_20261107/body_registration_20261113i.json'
            inspect(r)
    if apply:
        path.write_text(json.dumps(container,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        (ART/'body_registration_20261113i.json').write_text(json.dumps(dict(scope='GEOMETRY_ONLY_NOT_VISUAL_APPROVAL',sourcePages=15,entries=entries),ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(dict(applied=apply,pages=len(entries),heights={e['id']:round(e['bodyReferenceHeight'],2) for e in entries})))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');parser.add_argument('--candidates',action='store_true');args=parser.parse_args()
    run(args.apply,args.candidates)
