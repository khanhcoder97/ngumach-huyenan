"""Register TC body/FX drawings for isolated review; never edits PNGs or approves art."""
import argparse,hashlib,json,os,shutil
from collections import Counter
from PIL import Image
from inspect_actor_library import ART,ROOT,inspect,binary_projection
from calibrate_anh_dao_mobility import head_landmark
from calibrate_huyen_but_20261114f import gutter_edges
BATCH='20261116c';EV=ROOT/('Implementation/Reports/Evidence/Actor_Batch_'+BATCH)
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,v):
    pending=p.with_suffix(p.suffix+'.pending')
    with pending.open('w',encoding='utf8',newline='\n') as stream:
        stream.write(json.dumps(v,ensure_ascii=False,indent=2)+'\n');stream.flush();os.fsync(stream.fileno())
    assert read(pending)==v
    pending.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def neutral_foot_center(region,ground,body_height):
    width,height=region.size;band=max(3,int(round(body_height*.05)))
    xs=[i%width for i,(r,g,b,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and ground-band<=i//width<ground]
    assert len(xs)>=12,'Neutral foot envelope requires manual registration'
    return (min(xs)+max(xs))/2
def sash_landmark(region,head_top,neutral_height):
    width,height=region.size
    points=[(i%width,i//width) for i,(r,g,b,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and r>=70 and r>=1.8*g and r-g>=35 and g-b>=5 and b<90 and head_top+.35*neutral_height<=i//width<=head_top+.9*neutral_height]
    return ((min(x for x,y in points)+max(x for x,y in points))/2,len(points)) if points else (None,0)
def boot_contact(region,head_top,neutral_height):
    width,height=region.size;start=head_top+neutral_height*.5
    # Dark warm boots/trousers, excluding steel hammer and bright bronze fittings.
    points={(i%width,i//width) for i,(r,g,b,a) in enumerate(getattr(region,'get_flattened_data',region.getdata)()) if a>=200 and 30<=r<=130 and r-g>=12 and g-b>=5 and r-b>=40 and r-g>=g-b and i//width>=start}
    assert points,'No dark warm boots; manual registration required'
    rows=Counter(y for x,y in points);minimum=max(8,int(max(rows.values())*.1));ground=max(y for y,n in rows.items() if n>=minimum)+1
    remaining={p for p in points if p[1]>=ground-neutral_height*.18};groups=[]
    while remaining:
        seed=remaining.pop();group=[seed];todo=[seed]
        while todo:
            x,y=todo.pop()
            for dx,dy in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
                p=(x+dx,y+dy)
                if p in remaining:remaining.remove(p);todo.append(p);group.append(p)
        if len(group)>=12 and max(y for x,y in group)>=ground-12:groups.append(group)
    groups=sorted(groups,key=len,reverse=True)[:2];assert groups,'No grounded boot component; manual review required'
    xs=[x for group in groups for x,y in group]
    return (min(xs)+max(xs))/2,ground
def prepare(only=None):
    manifest=read(ART/('Candidates_'+BATCH)/'candidate_manifest.json');assert manifest['expectedSourcePages']==50 and manifest['selected']>0
    assert not any(r.get('batch')==BATCH for r in read(ART/'generation_records.json'))
    before={n:sha(ART/n) for n in ('generation_records.json','visual_review.json','structure_report.json')};entries=[];registrations=[];pending=[]
    override_path=ART/('registration_overrides_'+BATCH+'.json')
    overrides={e['id']:e for e in read(override_path)['entries']} if override_path.exists() else {}
    identifiers={r['id'] for r in manifest['records']}
    assert not only or set(only)<=identifiers,'Unknown candidate ID'
    for original in manifest['records']:
        if only and original['id'] not in only:continue
        r=dict(original);source=ART/r['source'];assert sha(source)==r['sourceSha256']
        if r['id'] in overrides:
            override=overrides[r['id']];assert override['sourceSha256']==r['sourceSha256'],'Registration override is for another PNG version'
            r.update(override['fields'])
        print('REGISTER_SOURCE_BEGIN '+r['id'],flush=True)
        try:page=inspect(r)
        except AssertionError as error:
            assert 'clipped/overlapping' in str(error),str(error)
            with Image.open(source) as image:
                xs,ys=binary_projection(image.getchannel('A').point(lambda a:255 if a>=16 else 0))
            r['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));page=inspect(r)
        frames=page['directions'][0]['frames'];diagnostics=[]
        if r.get('direction') and not r.get('sourceFootPivots'):
            pivots=[];neutral=None;sole_offset=None;sash_reference=None;sash_offset=None;neutral_x_correction=None
            with Image.open(source) as image:
                for f in frames:
                    x,y,w,h=f['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,f['bounds'])
                    if neutral is None:
                        # Neutral poses carry the hammer below the head and
                        # above the boots. Include the whole hair silhouette:
                        # dark-hair landmarks alone made rear views too large.
                        neutral=f['bounds'][3]-f['bounds'][1]
                        root_x,ground=boot_contact(region,head['top'],neutral);sole_offset=f['bounds'][3]-ground;assert 0<=sole_offset<=8,'Neutral soles require manual registration'
                        neutral_x_correction=neutral_foot_center(region,f['bounds'][3],neutral)-root_x
                    root_x,ground=boot_contact(region,head['top'],neutral);root_x+=neutral_x_correction;sash_x,sash_pixels=sash_landmark(region,head['top'],neutral);x_method='BOOT_COMPONENTS_WITH_NEUTRAL_ALPHA_FOOT_CENTER_CORRECTION'
                    if sash_reference is None:
                        assert sash_pixels>=8,'Neutral pelvis reference requires manual registration';sash_reference=sash_pixels;sash_offset=root_x-sash_x
                    if sash_pixels<sash_reference*.3:
                        assert sash_pixels>=8,'Occluded pelvis requires a manual source pivot'
                        # The hammer hides a boot during the low slam. Do not
                        # jump the character root onto the remaining boot.
                        root_x=sash_x+sash_offset;x_method='RED_SASH_REFERENCE_UNDER_HAND_HAMMER_OCCLUSION'
                    pivots.append([root_x,ground+sole_offset]);diagnostics.append(dict(head=head,root=pivots[-1],rootXMethod=x_method,sashCenterX=sash_x,sashPixelCount=sash_pixels))
            r.update(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=neutral,neutralFootCenterXCorrection=neutral_x_correction,registrationMethod='TC_NEUTRAL_FULL_ALPHA_HEIGHT_AND_FOOT_CENTER_BOOT_Y_OCCLUDED_SASH_X_PENDING_NATIVE_REVIEW');page=inspect(r)
        else:neutral=page['directions'][0]['referenceHeight']
        assert page['sourceFrames']==16;frames=page['directions'][0]['frames'];bundle=EV/'Candidate_Studio'/r['id'];textures=bundle/'textures';dest=textures/(page['sha256']+'.png')
        if dest.exists():assert sha(dest)==page['sha256']
        loop=bool(r.get('previewLoop',False));keys=[dict(Frame=i,Pose=dict(X=0,Y=0,PivotX=f['pivot'][0],PivotY=f['pivot'][1],ScaleX=140/neutral,ScaleY=140/neutral,Angle=0,Alpha=1,SourceFrame=i)) for i,f in enumerate(frames)]
        layer=dict(Id='sprite',Name=r['id'],Kind='sprite',Texture='textures/'+dest.name,Regions=[f['rect'] for f in frames],Rest=keys[0]['Pose'],Z=0,Visible=True)
        clip=dict(Name=r['id'],Direction=r.get('direction','OMNI'),Loop=loop,SourceNote='CANDIDATE_NOT_APPROVED; source/body root review only',DurationsMs=r['sourceFrameDurationsMs'],Tracks=[dict(LayerId='sprite',Interpolate=False,Keys=keys)],Markers=[])
        project=bundle/'project.json';document=dict(SchemaVersion=1,Scope='PRESENTATION_AUTHORING_ONLY',Name=r['id'],ProductionApproved=False,Layers=[layer],Sockets=[],Clips=[clip])
        registration=dict(record=r,page=page,bodyRootDiagnostics=diagnostics,originalPngUnchanged=True,productionApproved=False);registrations.append(registration)
        pending.append((source,dest,project,document,registration))
        entries.append(dict(id=r['id'],project=project.relative_to(ROOT).as_posix(),source=source.relative_to(ROOT).as_posix(),sourceSha256=page['sha256'],timing=r['sourceFrameDurationsMs'],loop=loop))
        print('REGISTER_SOURCE_COMPLETE '+r['id'],flush=True)
    assert before=={n:sha(ART/n) for n in before}
    prepared=len(entries)
    registration_path=ART/('body_registration_'+BATCH+'.json')
    if only and registration_path.exists():
        current={r['id']:r for r in manifest['records']};changed={r['record']['id'] for r in registrations}
        for old in read(registration_path)['entries']:
            r=old['record'];active=current.get(r['id'])
            if r['id'] in changed or not active or active['sourceSha256']!=r['sourceSha256']:continue
            override=overrides.get(r['id'])
            if override and (override['sourceSha256']!=r['sourceSha256'] or any(r.get(k)!=v for k,v in override['fields'].items())):continue
            effective=dict(active)
            if override:effective.update(override['fields'])
            if any(r.get(k)!=v for k,v in effective.items()):continue
            project=EV/'Candidate_Studio'/r['id']/'project.json';document=read(project)
            assert sha(ART/r['source'])==r['sourceSha256']==sha(project.parent/document['Layers'][0]['Texture'])
            assert document['Clips'][0]['DurationsMs']==r['sourceFrameDurationsMs']
            registrations.append(old);entries.append(dict(id=r['id'],project=project.relative_to(ROOT).as_posix(),source=(ART/r['source']).relative_to(ROOT).as_posix(),sourceSha256=r['sourceSha256'],timing=r['sourceFrameDurationsMs'],loop=bool(r.get('previewLoop',False))))
        order={r['id']:i for i,r in enumerate(manifest['records'])};entries.sort(key=lambda e:order[e['id']]);registrations.sort(key=lambda e:order[e['record']['id']])
    # Validate every source before replacing any existing review project.
    # An invalid late VFX sheet must not leave earlier captures bound to
    # half-updated roots while their old plan is still on disk.
    for source,dest,project,document,registration in pending:
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists():shutil.copyfile(source,dest)
        save(project,document);save(project.parent/'source_registration.json',registration)
    save(EV/'candidate_review_plan.json',dict(batch=BATCH,selected=len(entries),expected=50,pilot=len(entries)<50,catalogueUnchanged=True,missingCandidateIds=[r['id'] for r in manifest['records'] if r['id'] not in {e['id'] for e in entries}],entries=entries))
    save(ART/('body_registration_'+BATCH+'.json'),dict(scope='GEOMETRY_ONLY_REQUIRES_NATIVE_REVIEW',pilot=len(entries)<50,entries=registrations,issues=[]))
    print(json.dumps(dict(selected=len(entries),expected=50,preparedThisCall=prepared,registered=len(entries),catalogueUnchanged=True,productionApproved=False)))
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--only',nargs='+');args=parser.parse_args();prepare(args.only)
