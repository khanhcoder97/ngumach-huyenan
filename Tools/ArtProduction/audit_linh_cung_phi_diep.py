"""Audit Phi Diệp source integrity, retreat tracks and recorded Godot playback."""
import argparse
from itertools import accumulate
from math import dist, isclose

from audit_linh_cung_day_gai import check_source, distinct, montage
from audit_linh_cung_khoa_mach_preview import LAYER_TICK, decoded_frames, verify_log
from audit_linh_cung_lien_chau import sample_track
from prepare_linh_cung_phi_diep import (ARROW, ASSEMBLIES, BATCH, FACINGS, HEEL, LANDING_MS, OUTPUT,
                                      RELEASE_MS, RELEASE_POSE, SHORT_STOP_MS, START_MS, TARGET)
from prepare_thach_chuy_candidates_20261116c import ART, read, save, sha


def check_project(facing, pins):
    bundle = ASSEMBLIES / facing
    path = bundle / 'project.json'
    project = read(path)
    info = read(bundle / 'assembly_descriptor.json')
    assert info['projectSha256'] == sha(path)
    body = 'class_linh_cung_skill_05_' + facing.lower()
    identities = {body: body, TARGET: TARGET, ARROW: ARROW, 'heel_1': HEEL, 'heel_2': HEEL}
    assert {layer['Id'] for layer in project['Layers']} == set(identities)
    for layer in project['Layers']:
        assert sha(bundle / layer['Texture']) == pins[identities[layer['Id']]]
    assert len(project['Clips']) == len(info['modes']) == 2
    for clip, mode, stop in zip(project['Clips'], info['modes'], (LANDING_MS, SHORT_STOP_MS), strict=True):
        assert clip['Direction'] == facing and not clip['Loop'] and clip['Name'] == mode['name']
        starts = [0, *accumulate(clip['DurationsMs'])]
        markers = {mark['Name']: mark for mark in clip['Markers']}
        expected = dict(retreat_start=START_MS, arrow_release=RELEASE_MS, retreat_stop=stop)
        assert {name: starts[mark['Frame']] for name, mark in markers.items()} == expected
        poses = {track['LayerId']: list(sample_track(track, len(clip['DurationsMs']))) for track in clip['Tracks']}
        release = markers['arrow_release']['Frame']
        assert poses[body][release]['SourceFrame'] == RELEASE_POSE
        assert [poses[ARROW][release]['X'], poses[ARROW][release]['Y']] == mode['releaseOrigin']
        roots = [(pose['X'], pose['Y']) for pose in poses[body]]
        travel = [dist(root, mode['start']) for root in roots]
        assert all(a <= b + 1e-8 for a, b in zip(travel, travel[1:]))
        assert all(list(point) == mode['finish'] for point in roots[markers['retreat_stop']['Frame']:])
        assert isclose(travel[-1], mode['retreatDistance'], abs_tol=.0051)
        for identifier, initial in ((ARROW, RELEASE_MS), ('heel_1', START_MS), ('heel_2', RELEASE_MS)):
            visible = [i for i, pose in enumerate(poses[identifier]) if pose['Alpha']]
            assert visible == list(range(starts.index(initial), visible[-1] + 1))
            assert starts[visible[-1] + 1] - initial == 400
            assert distinct(poses[identifier][i]['SourceFrame'] for i in visible) == list(range(16))
            if identifier != ARROW:
                assert len({(poses[identifier][i]['X'], poses[identifier][i]['Y']) for i in visible}) == 1
    return dict(facing=facing, projectSha256=info['projectSha256'], modes=info['modes'])


def check_recording(facing, mode, ffmpeg):
    bundle = ASSEMBLIES / facing
    stem = 'preview' if mode == 0 else 'short'
    movie, log = bundle / f'{stem}.mp4', bundle / f'{stem}.godot.log'
    count = decoded_frames(movie, ffmpeg)
    assert count == 96
    events = {}
    for tick, name, phase in LAYER_TICK.findall(verify_log(log)):
        events.setdefault(name, []).append((int(tick), int(phase)))
    body = 'class_linh_cung_skill_05_' + facing.lower()
    assert set(events) == {body, TARGET, ARROW, 'heel_1', 'heel_2'}
    for identifier in (body, ARROW, 'heel_1', 'heel_2'):
        assert distinct(phase for _, phase in events[identifier]) == list(range(16)), identifier
    first_heel, arrow = events['heel_1'][0][0], events[ARROW][0][0]
    assert arrow - first_heel in (7, 8)
    assert arrow == events['heel_2'][0][0] == next(tick for tick, phase in events[body] if phase == RELEASE_POSE)
    indices = [
        max(1, events[body][0][0]),
        first_heel,
        next(tick for tick, phase in events[body] if phase == 7),
        arrow,
        next(tick for tick, phase in events[ARROW] if phase == 3),
        next(tick for tick, phase in events[ARROW] if phase == 8),
        events[ARROW][-1][0],
        events[ARROW][-1][0] + 4,
    ]
    assert indices == sorted(set(indices)) and indices[-1] < count
    image = bundle / ('sequence.png' if mode == 0 else 'short_sequence.png')
    montage(movie, image, indices, 'crop=566:260:402:116,tile=4x2', ffmpeg)
    return dict(facing=facing, mode=mode, framesDecoded=count, releaseFrame=arrow, moveStartFrame=first_heel,
                sourcePhasesRendered=64, movieSha256=sha(movie), logSha256=sha(log), montageSha256=sha(image),
                sampleFrames=indices)


def audit(ffmpeg):
    plan = read(OUTPUT / 'candidate_review_plan.json')
    pins = {entry['id']: entry['sourceSha256'] for entry in plan['entries']}
    approved = next(item for item in read(ART / 'visual_review.json')['sourceApprovals'] if item['id'] == TARGET)
    pins[TARGET] = approved['sourceSha256']
    sources = [check_source(entry, ffmpeg, OUTPUT) for entry in plan['entries']]
    assert len(sources) == 10
    projects = [check_project(facing, pins) for facing in FACINGS]
    cases = [(facing, 0) for facing in FACINGS] + [('E', 1), ('NW', 1)]
    recordings = [check_recording(facing, mode, ffmpeg) for facing, mode in cases]
    save(OUTPUT / 'native_audit.json',
         dict(batch=BATCH, catalogueUnchanged=True, productionApproved=False, sourceViews=sources,
              nativeSourcePoses=sum(item['sourcePosesObserved'] for item in sources),
              sourceFramesDecoded=sum(item['decodedFrames'] for item in sources), projects=projects,
              assemblyFramesDecoded=sum(item['framesDecoded'] for item in recordings), nativeAssemblies=recordings))
    print('Verified ten Phi Diệp atlases, sixteen timelines and ten native recordings.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
