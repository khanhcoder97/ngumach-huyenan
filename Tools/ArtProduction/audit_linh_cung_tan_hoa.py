"""Check Tán Hoa's intact source sheets, eight timelines and native renders."""
import argparse
from itertools import accumulate

from audit_linh_cung_day_gai import check_source, distinct, montage
from audit_linh_cung_khoa_mach_preview import LAYER_TICK, decoded_frames, verify_log
from audit_linh_cung_lien_chau import sample_track
from prepare_linh_cung_tan_hoa import (ASSEMBLIES, BATCH, FACINGS, FALL, FAN, FULL_POSE, OUTPUT,
                                     RELEASE_POSE, SECTOR_DEGREES, TARGET)
from prepare_thach_chuy_candidates_20261116c import ART, read, save, sha


def check_assembly(facing, pins, ffmpeg):
    bundle = ASSEMBLIES / facing
    project_path = bundle / 'project.json'
    project = read(project_path)
    info = read(bundle / 'assembly_descriptor.json')
    assert info['projectSha256'] == sha(project_path)
    body = 'class_linh_cung_skill_04_' + facing.lower()
    identifiers = {body, TARGET, FALL, FAN}
    assert {layer['Id'] for layer in project['Layers']} == identifiers
    for layer in project['Layers']:
        assert sha(bundle / layer['Texture']) == pins[layer['Id']]
    clip, = project['Clips']
    assert clip['Direction'] == facing and not clip['Loop']
    marks = clip['Markers']
    starts = [0, *accumulate(clip['DurationsMs'])]
    assert [mark['Name'] for mark in marks] == ['fan_release', 'fan_full', 'leaves_fall']
    assert [starts[mark['Frame']] for mark in marks] == [info['releaseMs'], info['fullMs'], info['fallMs']]
    poses = {track['LayerId']: list(sample_track(track, len(clip['DurationsMs']))) for track in clip['Tracks']}
    at, full, leaves = [mark['Frame'] for mark in marks]
    assert poses[body][at]['SourceFrame'] == RELEASE_POSE
    assert poses[FAN][full]['SourceFrame'] == FULL_POSE
    for identifier, start in ((FAN, at), (FALL, leaves)):
        visible = [i for i, pose in enumerate(poses[identifier]) if pose['Alpha']]
        assert visible == list(range(start, visible[-1] + 1))
        assert distinct(poses[identifier][i]['SourceFrame'] for i in visible) == list(range(16))
    assert poses[FAN][leaves]['Alpha'] and abs(info['sectorDegrees'] - SECTOR_DEGREES) <= .05

    log, movie = bundle / 'preview.godot.log', bundle / 'preview.mp4'
    count = decoded_frames(movie, ffmpeg)
    assert count == 96
    events = {}
    for tick, identifier, phase in LAYER_TICK.findall(verify_log(log)):
        events.setdefault(identifier, []).append((int(tick), int(phase)))
    assert set(events) == identifiers
    for identifier in (body, FAN, FALL):
        assert distinct(phase for _, phase in events[identifier]) == list(range(16)), (facing, identifier)
    first_fan = events[FAN][0][0]
    first_fall = events[FALL][0][0]
    assert first_fan == next(tick for tick, phase in events[body] if phase == RELEASE_POSE)
    assert first_fan < first_fall < events[FAN][-1][0] < events[FALL][-1][0]
    indices = [
        max(1, events[body][0][0]),
        next(tick for tick, phase in events[body] if phase == 4),
        first_fan,
        next(tick for tick, phase in events[FAN] if phase == FULL_POSE),
        first_fall,
        next(tick for tick, phase in events[FALL] if phase == 8),
        events[FALL][-1][0],
        events[FALL][-1][0] + 3,
    ]
    assert indices == sorted(set(indices)) and indices[-1] < count
    image = bundle / 'sequence.png'
    montage(movie, image, indices, 'crop=566:274:402:116,tile=4x2', ffmpeg)
    return dict(facing=facing, projectSha256=info['projectSha256'], movieSha256=sha(movie), logSha256=sha(log),
                montageSha256=sha(image), framesDecoded=count, renderSourcePhases=48, sampleFrames=indices)


def audit(ffmpeg):
    plan = read(OUTPUT / 'candidate_review_plan.json')
    pins = {entry['id']: entry['sourceSha256'] for entry in plan['entries']}
    approved = next(item for item in read(ART / 'visual_review.json')['sourceApprovals'] if item['id'] == TARGET)
    pins[TARGET] = approved['sourceSha256']
    sources = [check_source(entry, ffmpeg, OUTPUT) for entry in plan['entries']]
    assert len(sources) == 10
    assemblies = [check_assembly(facing, pins, ffmpeg) for facing in FACINGS]
    save(OUTPUT / 'native_audit.json',
         dict(batch=BATCH, catalogueUnchanged=True, productionApproved=False,
              nativeSourcePoses=sum(source['sourcePosesObserved'] for source in sources),
              sourceFramesDecoded=sum(source['decodedFrames'] for source in sources),
              assemblyFramesDecoded=sum(item['framesDecoded'] for item in assemblies),
              sourceViews=sources, nativeAssemblies=assemblies))
    print('Verified all ten Tán Hoa sheets and eight 60 FPS native timelines.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
