"""Record the newly viewed v2 call expressions; freeze their exact artifact bindings."""
import json
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha


def record_views():
    records={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    native=read(EV/'native_media_audit.current.json');movies={r['file'][4:-4]:r for r in native['files']}
    bindings=[]
    for facing in ('e','se'):
        identifier='class_thach_chuy_skill_04_'+facing;record=records[identifier];movie=movies[identifier]
        assert record['source'].endswith('_v2_20261116c.png')
        project=EV/'Candidate_Studio'/identifier/'project.json';montage=EV/('raw_'+identifier+'_poses.png')
        assert movie['sourceSha256']==record['sourceSha256'] and movie['portableProjectSha256']==sha(project)
        assert movie['sha256']==sha(EV/movie['file'])
        bindings.append(dict(id=identifier,sourceSha256=record['sourceSha256'],portableProjectSha256=sha(project),movieSha256=movie['sha256'],montageSha256=sha(montage)))
    packet=dict(scope='LOCKED_EXPLICIT_MANUAL_V2_EXPRESSION_VIEW_NOT_APPROVAL',entries=bindings)
    binding_path=EV/'manual_view_bindings.taunt_expression_v2_20261117a.json'
    if binding_path.exists():assert read(binding_path)==packet,'New artifacts require a newly viewed/versioned review packet'
    else:save(binding_path,packet)
    observations=read(EV/'manual_review_observations.json')
    for binding in bindings:
        identifier=binding['id'];facing=identifier.rsplit('_',1)[1]
        timing='E phases7–10show an open mouth, then close.' if facing=='e' else 'SE phases7–9show an open mouth; phase10already closes as the head settles.'
        note='All16original and current native v2 poses explicitly viewed. Targeted expression revision now shows a readable call while preserving single tap,connected one-hammer grip and recovery. '+timing+' This clears the closed-mouth observation for this version only. Exact facing,root/owner-idle continuity and wide gameplay/event acceptance remain pending.'
        if facing=='se':note+=' Source gutters are registered separately; SHA-bound10px neutral dark-sole proposal remains geometry-only.'
        item=dict(**binding,originalAtlasViewed=True,nativePoseFramesInspected=16,status='CALL_VISIBILITY_REPAIRED_OTHER_SOURCE_ACCEPTANCE_PENDING',visualNotes=note,productionApproved=False)
        observations['entries']=[e for e in observations['entries'] if e['id']!=identifier]+[item]
    save(EV/'manual_review_observations.json',observations)
    print(json.dumps(dict(revisedSources=2,nativePosesViewed=32,closedMouthObservationResolved=True,sourceApprovalsApplied=0)))


if __name__=='__main__':record_views()
