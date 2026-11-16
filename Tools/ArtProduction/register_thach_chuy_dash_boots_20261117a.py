"""Pin two reviewed dark-sole proposals; do not relax the shared root guard."""
import json
from PIL import Image
from inspect_actor_library import ART, inspect, binary_projection
from calibrate_huyen_but_20261114f import gutter_edges
from calibrate_anh_dao_mobility import head_landmark
from prepare_thach_chuy_candidates_20261116c import boot_contact, neutral_foot_center, sash_landmark, read, save, sha

SOURCES={
    'class_thach_chuy_skill_05_se':('ce74fdcfdf82ef929874164fcab9ac1b213f6fd3cfe50b35478318b9921a19cd',10),
    'class_thach_chuy_skill_05_ne':('2821363b1a34c4f0014527692137c1642519cbcebd21a0492667c5c0993c4d74',9),
}


def register(sources=None, mechanic='DASH'):
    assert mechanic in ('DASH','TAUNT')
    sources=SOURCES if sources is None else sources
    records={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    path=ART/'registration_overrides_20261116c.json';overrides=read(path)
    proposals=[]
    for identifier,(expected,expected_offset) in sources.items():
        r=records[identifier]
        assert r['sourceSha256']==sha(ART/r['source'])==expected,'Proposal belongs to another source version'
        try:page=inspect(r)
        except AssertionError as error:
            assert 'clipped/overlapping' in str(error),str(error)
            with Image.open(ART/r['source']) as image:
                xs,ys=binary_projection(image.getchannel('A').point(lambda a:255 if a>=16 else 0))
            r['gridEdges']=dict(columns=gutter_edges(xs),rows=gutter_edges(ys));page=inspect(r)
        frames=page['directions'][0]['frames'];height=frames[0]['bounds'][3]-frames[0]['bounds'][1]
        pivots=[];diagnostics=[];sash_reference=None
        with Image.open(ART/r['source']) as image:
            for index,frame in enumerate(frames):
                x,y,w,h=frame['rect'];region=image.crop((x,y,x+w,y+h));head=head_landmark(region,frame['bounds'])
                root_x,ground=boot_contact(region,head['top'],height)
                if index==0:
                    assert frame['bounds'][3]-ground==expected_offset
                    correction=neutral_foot_center(region,frame['bounds'][3],height)-root_x
                root_x+=correction
                sash_x,pixels=sash_landmark(region,head['top'],height)
                assert pixels>=8,'Manual pelvis landmark required for this pose'
                if sash_reference is None:
                    sash_reference=pixels;sash_offset=root_x-sash_x
                method='BOOT_COMPONENTS_NEUTRAL_FOOT_ENVELOPE_AND_REVIEWED_DARK_SOLE_OFFSET'
                if pixels<sash_reference*.3:
                    root_x=sash_x+sash_offset;method='RED_SASH_X_UNDER_OCCLUSION_WITH_REVIEWED_DARK_SOLE_OFFSET'
                pivot=[root_x,ground+expected_offset]
                assert 0<=pivot[0]<w and 0<pivot[1]<=h
                pivots.append(pivot);diagnostics.append(dict(head=head,root=pivot,method=method,sashPixels=pixels))
        method='SHA_BOUND_DASH_DARK_SOLE_PROPOSAL_REQUIRES_NATIVE_AND_AIRBORNE_ROOT_REVIEW' if mechanic=='DASH' else 'SHA_BOUND_TAUNT_DARK_SOLE_PROPOSAL_REQUIRES_NATIVE_ROOT_REVIEW'
        remaining='Dash flight/root travel and ground contact remain unaccepted.' if mechanic=='DASH' else 'Tap contact and owner-idle root continuity remain unaccepted.'
        fields=dict(pivotMode='SOURCE_FOOT_PIVOTS',sourceFootPivots=pivots,bodyReferenceHeight=height,sourceBootDiagnostics=diagnostics,registrationMethod=method)
        if r.get('gridEdges'):fields['gridEdges']=r['gridEdges']
        proposals.append(dict(id=identifier,sourceSha256=expected,reviewNote='Original whole4x4 manually viewed. Neutral pose shows boots below hammer; saturated warm mask omits the dark sole outline by exactly%dsourcepx. Source-specific offset is pinned to this PNG; shared8px guard remains unchanged. Per-pose boot/sash tracking is only an editable review proposal. '%expected_offset+remaining,fields=fields))
    for proposal in proposals:
        overrides['entries']=[e for e in overrides['entries'] if e['id']!=proposal['id']]+[proposal]
    save(path,overrides)
    print(json.dumps(dict(registeredProposals=len(proposals),rasterModified=False,productionApproved=False)))


if __name__=='__main__':register()
