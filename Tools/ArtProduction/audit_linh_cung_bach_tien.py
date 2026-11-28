"""Audit Bách Tiễn ground timing, independent falling layers and native playback."""
import argparse
from itertools import accumulate
from math import dist, isclose

from audit_linh_cung_day_gai import check_source, distinct, montage
from audit_linh_cung_khoa_mach_preview import LAYER_TICK, decoded_frames, verify_log
from audit_linh_cung_lien_chau import sample_track
from prepare_linh_cung_bach_tien import (ARROW, ASSEMBLIES, BATCH, CONTACT_POSE, FACINGS, FLECKS, OUTPUT,
                                       RADIUS, RELEASE_POSE, RING, TARGET, WARNING_MS, WAVE_SPACING_MS)
from prepare_thach_chuy_candidates_20261116c import ART, read, save, sha


def check_view(facing, pins, ffmpeg):
    bundle = ASSEMBLIES / facing
    project_path = bundle / 'project.json'
    project = read(project_path)
    info = read(bundle / 'assembly_descriptor.json')
    assert info['projectSha256'] == sha(project_path)
    body = 'class_linh_cung_skill_06_' + facing.lower()
    identities = info['layerSources']
    assert len(identities) == len(project['Layers']) == 35
    assert {drawing['Id'] for drawing in project['Layers']} == set(identities)
    for drawing in project['Layers']:
        assert sha(bundle / drawing['Texture']) == pins[identities[drawing['Id']]]
    clip, = project['Clips']
    assert clip['Direction'] == facing and not clip['Loop']
    assert {track['LayerId'] for track in clip['Tracks']} == set(identities)
    times = [0, *accumulate(clip['DurationsMs'])]
    poses = {track['LayerId']: list(sample_track(track, len(clip['DurationsMs']))) for track in clip['Tracks']}
    marks = {marker['Name']: marker for marker in clip['Markers']}
    assert info['warningMs'] == WARNING_MS and info['radius'] == RADIUS
    starts, contacts = info['waveStarts'], info['waveContacts']
    assert starts == [WARNING_MS + WAVE_SPACING_MS * i for i in range(4)]
    assert [contact - start for start, contact in zip(starts, contacts)] == [140] * 4
    assert poses[body][marks['release_up']['Frame']]['SourceFrame'] == RELEASE_POSE
    zone = [marks['warning']['X'], marks['warning']['Y']]
    for wave, (start, contact) in enumerate(zip(starts, contacts), 1):
        for event, time in (('drop', start), ('contact', contact)):
            marker = marks[f'wave_{wave}_{event}']
            assert times[marker['Frame']] == time and marker['Radius'] == RADIUS
            assert [marker['X'], marker['Y']] == zone
        for index in range(1, 7):
            arrow = poses[f'arrow_{wave}_{index}']
            at = arrow[times.index(contact)]
            assert at['SourceFrame'] == CONTACT_POSE and dist((at['X'], at['Y']), zone) < RADIUS
            assert arrow[times.index(start)]['Y'] < at['Y']
            assert all(isclose(state['Y'], at['Y']) for state in arrow[times.index(contact):])
    for identifier, source in identities.items():
        if source in (body, TARGET):
            continue
        visible = [i for i, state in enumerate(poses[identifier]) if state['Alpha'] == 1]
        assert visible == list(range(visible[0], visible[-1] + 1))
        assert distinct(poses[identifier][i]['SourceFrame'] for i in visible) == list(range(16))
        onset, length = times[visible[0]], times[visible[-1] + 1] - times[visible[0]]
        if source == RING:
            assert onset == 0 and length == WARNING_MS
            assert all([state['X'], state['Y']] == zone for state in poses[identifier])
        else:
            wave = int(identifier.split('_')[1]) - 1
            assert onset == (starts if source == ARROW else contacts)[wave] and length == 320

    video, log = bundle / 'preview.mp4', bundle / 'preview.godot.log'
    count = decoded_frames(video, ffmpeg)
    assert count == 156
    events = {}
    for tick, identifier, phase in LAYER_TICK.findall(verify_log(log)):
        events.setdefault(identifier, []).append((int(tick), int(phase)))
    assert set(events) == set(identities)
    for identifier in events:
        if identifier != TARGET:
            assert distinct(phase for _, phase in events[identifier]) == list(range(16)), (facing, identifier)
    drop_ticks = [events[f'arrow_{wave}_1'][0][0] for wave in range(1, 5)]
    contact_ticks = [events[f'flecks_{wave}_1'][0][0] for wave in range(1, 5)]
    assert drop_ticks[0] - events[RING][0][0] in (71, 72, 73)
    assert all(b - a in (11, 12, 13) for a, b in zip(drop_ticks, drop_ticks[1:]))
    assert all(contact - drop in (8, 9) for drop, contact in zip(drop_ticks, contact_ticks))
    indices = [max(1, events[RING][0][0]), next(tick for tick, phase in events[body] if phase == RELEASE_POSE),
               events[RING][-1][0], *contact_ticks, events['flecks_4_1'][-1][0] + 3]
    assert indices == sorted(set(indices)) and indices[-1] < count
    image = bundle / 'sequence.png'
    montage(video, image, indices, 'crop=566:260:402:116,tile=4x2', ffmpeg)
    return dict(facing=facing, projectSha256=info['projectSha256'], framesDecoded=count,
                waveStartsNative=drop_ticks, waveContactsNative=contact_ticks, sourceLayersRendered=34,
                movieSha256=sha(video), logSha256=sha(log), montageSha256=sha(image), sampleFrames=indices)


def audit(ffmpeg):
    plan = read(OUTPUT / 'candidate_review_plan.json')
    pins = {entry['id']: entry['sourceSha256'] for entry in plan['entries']}
    target = next(item for item in read(ART / 'visual_review.json')['sourceApprovals'] if item['id'] == TARGET)
    pins[TARGET] = target['sourceSha256']
    sources = [check_source(entry, ffmpeg, OUTPUT) for entry in plan['entries']]
    assert len(sources) == 11
    assemblies = [check_view(facing, pins, ffmpeg) for facing in FACINGS]
    save(OUTPUT / 'native_audit.json',
         dict(batch=BATCH, catalogueUnchanged=True, productionApproved=False, sourceViews=sources,
              nativeSourcePoses=sum(item['sourcePosesObserved'] for item in sources),
              sourceFramesDecoded=sum(item['decodedFrames'] for item in sources),
              assemblyFramesDecoded=sum(item['framesDecoded'] for item in assemblies), nativeAssemblies=assemblies))
    print('Verified eleven Bách Tiễn sources and eight four-wave native captures.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
