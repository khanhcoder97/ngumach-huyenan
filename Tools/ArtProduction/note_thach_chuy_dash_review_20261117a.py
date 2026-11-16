"""Bind explicitly viewed Phá Nham source/native observations, without promotion."""
import json
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha


def record_views():
    records={r['id']:r for r in read(ART/'Candidates_20261116c/candidate_manifest.json')['records']}
    native=read(EV/'native_media_audit.current.json');movies={r['file'][4:-4]:r for r in native['files']}
    notes={
        'class_thach_chuy_skill_05_s':('HOLD_DASH_WORLD_ROOT_AND_FLIGHT_REVIEW','All16original/native poses viewed. One crouch, forward braced drive with reaching boot, deceleration and neutral recovery; one hammer remains screen-left. Boot-based root follows the reaching foot during the dash. Need fixed-camera world/root and idle seam review; source art does not move the server character.'),
        'class_thach_chuy_skill_05_e':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16original/native poses viewed. Clear rightward shoulder-braced drive/recovery with connected hands and one hammer. Forward lean remains readable without repeated run cycle. Exact-E yaw, planted/airborne root registration and actual terrain-aware movement still pending.'),
        'class_thach_chuy_skill_05_se':('HOLD_DASH_WORLD_ROOT_AND_FLIGHT_REVIEW','All16original/native poses viewed, including wider native montage because compact crop cuts the hammer in extreme lean. Source itself and full Studio viewport retain whole weapon. SHA-bound10px neutral dark-sole proposal bypasses no global guard. Airborne pose/root and return-to-idle remain unaccepted.'),
        'class_thach_chuy_skill_05_n':('HOLD_NORTH_DASH_AXIS_VERIFICATION','All16original/native poses viewed, including wider native montage. Back-facing neutral retained, but drive leans strongly diagonally toward upper-right. Verify or redraw exact-N dash axis before acceptance. Root follows alternating visible boots; actual northward movement/grounding and idle seam are unaccepted.'),
        'class_thach_chuy_skill_05_ne':('HOLD_DASH_WORLD_ROOT_AND_FLIGHT_REVIEW','All16original/native poses viewed. Connected rear-quarter hammer brace, one drive and recovery. SHA-bound9px dark-sole proposal corrects neutral mask omission. Foot/flight root balance needs fixed-camera world review; no collision or displacement authority is implied.'),
        'sk_tc_05_dash_trail_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases viewed after front-right/baseline proposal. Short low tan dust extends left from its proposed emitter, with only small grains, then settles. Emission point can still shift with an irregular front silhouette; verify against moving caster foot and terrain before acceptance.'),
        'sk_tc_05_hit_impact_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases viewed after radial envelope proposal. One thin open ring with a few fragments; no raised solid annulus. Asymmetric late grains are not proof of a stable physical hit hub. Hand-tune ground centre in assembly and emit only for confirmed contact.'),
        'sk_tc_05_stop_dust_component':('SOURCE_REVIEW_IN_PROGRESS_NOT_APPROVED','All16current native phases viewed after low baseline proposal. Small tan settling clumps and grains, no shockwave or hit star. Keep at an externally confirmed stop foot location; blocked-path dust must not create target damage.'),
    }
    path=EV/'manual_review_observations.json';observations=read(path)
    for identifier,(status,note) in notes.items():
        record=records[identifier];movie=movies[identifier];project=EV/'Candidate_Studio'/identifier/'project.json'
        assert movie['sourceSha256']==record['sourceSha256'] and movie['portableProjectSha256']==sha(project)
        assert movie['sha256']==sha(EV/movie['file'])
        item=dict(id=identifier,sourceSha256=record['sourceSha256'],portableProjectSha256=sha(project),movieSha256=movie['sha256'],montageSha256=sha(EV/('raw_'+identifier+'_poses.png')),originalAtlasViewed=True,nativePoseFramesInspected=16,status=status,visualNotes=note,productionApproved=False)
        if identifier in ('class_thach_chuy_skill_05_n','class_thach_chuy_skill_05_se'):
            wider=EV/('raw_'+identifier+'_source_samples.png')
            item['additionalNativeViews']=[dict(file=wider.name,sha256=sha(wider),reason='Compact crop clips extreme lean; wider native stage shows all16whole poses.')]
        observations['entries']=[e for e in observations['entries'] if e['id']!=identifier]+[item]
    save(path,observations)
    print(json.dumps(dict(addedCurrentNativeViews=8,reviewedPoses=128,sourceApprovalsApplied=0)))


if __name__=='__main__':record_views()
