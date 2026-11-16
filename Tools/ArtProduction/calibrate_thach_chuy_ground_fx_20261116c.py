"""Read-only source landmarks for isolated TC VFX review; no pixels or approvals changed."""
import hashlib,json
from PIL import Image
from inspect_actor_library import ART
from prepare_thach_chuy_candidates_20261116c import save
BATCH='20261116c'

def bright_crack_hub(region):
    width,height=region.size
    pixels=list(getattr(region,'get_flattened_data',region.getdata)())
    # Native review showed a dense ochre side branch outranking the bright
    # actual intersection in phases4..8. Register the cream core instead.
    # The last fading drawings have no cream left: retain their small warm
    # remnant, with an explicit native-review gate rather than a fake pose.
    for red,green,blue in ((220,190,130),(220,170,110),(180,135,65)):
        core=[(i%width,i//width) for i,(r,g,b,a) in enumerate(pixels) if a>=200 and r>=red and g>=green and b>=blue and r>=g>=b]
        if core:return [sum(x for x,y in core)/len(core),sum(y for x,y in core)/len(core)],len(core)
    raise AssertionError('No visible pale crack hub; manual source coordinates required')

def calibrate():
    read=lambda p:json.loads(p.read_text(encoding='utf8'))
    registrations=read(ART/('body_registration_'+BATCH+'.json'))['entries']
    selected={e['id']:e for e in read(ART/('Candidates_'+BATCH)/'candidate_manifest.json')['records']}
    path=ART/('registration_overrides_'+BATCH+'.json');out=read(path) if path.exists() else dict(scope='SHA_BOUND_REGISTRATION_ONLY_NOT_SOURCE_APPROVAL',entries=[])
    diagnostics=[]
    for registration in registrations:
        r=registration['record'];identifier=r['id']
        if not identifier.startswith(('sk_tc_01_','sk_tc_02_')):continue
        assert selected[identifier]['sourceSha256']==r['sourceSha256']
        source=ART/r['source'];assert hashlib.sha256(source.read_bytes()).hexdigest()==r['sourceSha256']
        pivots=[];landmarks=[]
        with Image.open(source) as image:
            for frame in registration['page']['directions'][0]['frames']:
                left,top,right,bottom=frame['bounds'];x,y,w,h=frame['rect']
                if identifier=='sk_tc_01_impact_crack_component':
                    pivot,count=bright_crack_hub(image.crop((x,y,x+w,y+h)));landmarks.append(dict(paleCorePixels=count))
                    method='CREAM_CRACK_INTERSECTION_WITH_FADING_REMNANT'
                elif identifier=='sk_tc_01_charge_wedge_component':
                    pivot=[left+(right-left)*.08,(top+bottom)/2];method='SHORT_WEDGE_REAR_GROUND_ORIGIN';landmarks.append({})
                elif identifier.endswith('dust_end_component'):
                    pivot=[(left+right)/2,bottom];method='LOW_DUST_VISIBLE_FOOTPRINT_BASELINE';landmarks.append({})
                else:
                    pivot=[(left+right)/2,(top+bottom)/2];method='RADIAL_FOOTPRINT_CENTRE_PENDING_NATIVE_REVIEW';landmarks.append({})
                assert 0<=pivot[0]<w and 0<=pivot[1]<h
                pivots.append(pivot)
        assert len(pivots)==16
        fields=dict(pivotMode='SOURCE_PIVOTS',sourcePivots=pivots,registrationMethod=method+'_NOT_APPROVED')
        entry=dict(id=identifier,sourceSha256=r['sourceSha256'],reviewNote='Source atlas and initial native rendering reviewed where available. Uneven atlas placement made cell-centre attachments drift. These landmark coordinates are registration candidates only: inspect all16native phases and whole-skill/ground attachment before acceptance. Fading asymmetric debris may still need hand-tuned coordinates; no automatic gameplay or source approval.',fields=fields)
        out['entries']=[e for e in out['entries'] if e['id']!=identifier]+[entry]
        diagnostics.append(dict(id=identifier,sourceSha256=r['sourceSha256'],method=method,pivots=pivots,landmarks=landmarks,originalPngUnchanged=True,productionApproved=False))
    assert len(diagnostics)==6,'Need all six TC1/2 components before calibration'
    save(path,out);save(ART/('ground_fx_registration_'+BATCH+'.json'),dict(scope='LANDMARK_PROPOSALS_NOT_VISUAL_ACCEPTANCE',entries=diagnostics))
    print(json.dumps(dict(registeredComponents=len(diagnostics),sourcePoses=len(diagnostics)*16,originalPngUnchanged=True,productionApproved=False)))
if __name__=='__main__':calibrate()
