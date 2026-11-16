"""Persist observations of the explicitly viewed current source/native artifacts."""
from prepare_thach_chuy_candidates_20261116c import ART, EV, ROOT, read, save, sha


def record_views():
    records={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    native=read(EV/'native_media_audit.current.json')
    movies={r['file'][4:-4]:r for r in native['files']}
    notes={
        'class_thach_chuy_skill_04_s':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16original/native poses explicitly viewed. One gentle downward hammer tap then readable open-mouth call, returning to same frontal hammer side. Whole body remains coherent. Fixed-camera owner-idle seam and confirmed taunt cue integration still pending.'),
        'class_thach_chuy_skill_04_e':('HOLD_CALL_EXPRESSION_AND_FIXED_FACING_REVIEW','All16original/native poses explicitly viewed. Single tap and head/chest lift readable; mouth remains closed, so the call is weaker than intended. Near/far shoulder/eye presentation also needs exact-E review. Keep as unapproved candidate; improve call expression before source acceptance.'),
        'class_thach_chuy_skill_04_se':('HOLD_CALL_EXPRESSION_REPAIR','All16original/native poses explicitly viewed. Distinct single tap/raise/recovery and coherent one hammer. Mouth is closed during call; needs expression revision. Root/neutral continuity still requires fixed-camera idle comparison.'),
        'class_thach_chuy_skill_04_n':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16original/native poses explicitly viewed. Back remains readable, one low tap then chest/head rise; forward grip largely hidden naturally. Need exact-N yaw check, native idle/weapon seam and world-root stability review.'),
        'class_thach_chuy_skill_04_ne':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16original/native poses explicitly viewed. Rear-quarter tap/call/recovery readable. Warm boot mask missed dark soles; SHA-bound source-specific boot proposal registers the near foot. It avoids the initial failure, but near/far foot balance and root sway remain unaccepted. No blanket alpha-bottom rule applied to other sources.'),
        'sk_tc_04_caster_pulse_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases explicitly viewed after envelope-centre registration. V2 is a thin low expanding broken ellipse, with open interior and no stone platform. Centres now remain at the anchor across source rows. Actual caster-foot/world scale and low-contrast ground readability still need gameplay review. V1 raised annulus is rejected.'),
        'sk_tc_04_target_chevron_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases explicitly viewed. V2 one clean right-pointing chevron, no orbiting rocks or multi-arrow clutter. Quiet split-stroke ending remains nonempty. Actor-relative direction routing and24px gameplay readability pending. V1 noisy debris symbol is rejected.'),
        'sk_tc_04_target_status_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases and actual14→15→0→1wrap explicitly viewed. One compact hammer/attention glyph, stable silhouette and quiet brightness loop, no extinction/restart. Nameplate/world-UI sizing and authoritative status expiration still pending.'),
    }
    path=EV/'manual_review_observations.json';observations=read(path)
    for identifier,(status,note) in notes.items():
        record=records[identifier];movie=movies[identifier]
        project=EV/'Candidate_Studio'/identifier/'project.json'
        assert record['sourceSha256']==movie['sourceSha256']
        assert sha(project)==movie['portableProjectSha256']
        assert sha(EV/movie['file'])==movie['sha256']
        item=dict(id=identifier,sourceSha256=record['sourceSha256'],portableProjectSha256=sha(project),movieSha256=movie['sha256'],montageSha256=sha(EV/('raw_'+identifier+'_poses.png')),originalAtlasViewed=True,nativePoseFramesInspected=16,visualNotes=note,status=status,productionApproved=False)
        observations['entries']=[e for e in observations['entries'] if e['id']!=identifier]+[item]
    save(path,observations)
    for seam in native['loopSeams']:
        assert sha(EV/seam['file'])==seam['sha256']
        seam['manualViewed']=True
    save(EV/'native_media_audit.current.json',native)
    bundle=ROOT/'Implementation/Reports/Evidence/Actor_Assembly_20261117a/ThietBich_S_trial1'
    audit=read(bundle/'native_audit.json')
    assert audit['projectSha256']==sha(bundle/'project.json') and audit['movieSha256']==sha(bundle/'native.mp4')
    assert audit['montageSha256']==sha(bundle/'phase_chain_review.png')
    save(bundle/'manual_visual_review.json',dict(scope='TWELVE_PHASE_SAMPLES_OF_SOUTH_SOCKET_ASSEMBLY_ONLY',projectSha256=audit['projectSha256'],movieSha256=audit['movieSha256'],montageSha256=audit['montageSha256'],sampleOrder=audit['sampleOrder'],manuallyViewed=True,productionApproved=False,observations=['Shoulder/knee plates stay on the front right-side body surfaces during the viewed phases.','Back plate remains occluded by the frontal body; active layer coverage is not evidence of its visible silhouette.','Crack overlay stays within the plate envelope; source fixed parent origin avoids centre drift of early fracture strokes.','End starts on the sustain footprint, then reveals the underlying metal armour as it breaks down. This is only a south-view trial.'],remaining=['All8facings and per-action hand/face occlusion.','All64FXsource phases against each parent socket, not just12selected samples.','Owner idle transition, actual wide gameplay camera and confirmed server buff lifecycle.','Body is held at final activation pose for inspection; replace with gameplay idle before integration.']))
    print('RECORDED8CURRENT_SOURCE_NATIVE_VIEWS_AND2LOOP_SEAMS;ASSEMBLY12SAMPLES;NO_APPROVALS')


if __name__=='__main__':
    record_views()
