"""Verify Liên Châu authored releases and native source/project captures."""
import argparse
from itertools import accumulate

from audit_linh_cung_day_gai import check_source, distinct, montage
from audit_linh_cung_khoa_mach_preview import LAYER_TICK, decoded_frames, verify_log
from prepare_linh_cung_lien_chau import (ARROW, ASSEMBLIES, BATCH, FACINGS, NOCK, OUTPUT,
                                       RELEASE_MS, RELEASE_POSES, SOURCE_MS, SPREAD, TARGET)
from prepare_thach_chuy_candidates_20261116c import ART, read, save, sha

ARROWS = [f'arrow_{index}' for index in range(1, 6)]
NOCKS = [f'nock_{index}' for index in range(1, 6)]


def sample_track(track, count):
    assert track['Keys'][0]['Frame'] == 0 and not track['Interpolate']
    at = {key['Frame']: key['Pose'] for key in track['Keys']}
    assert len(at) == len(track['Keys']) and max(at) < count
    sample = at[0]
    for index in range(count):
        sample = at.get(index, sample)
        yield sample


def check_project(facing, source_pins):
    bundle = ASSEMBLIES / facing
    project_path = bundle / 'project.json'
    project = read(project_path)
    metadata = read(bundle / 'assembly_descriptor.json')
    assert metadata['projectSha256'] == sha(project_path)
    body = 'class_linh_cung_skill_03_' + facing.lower()
    identities = {body: body, TARGET: TARGET} | dict.fromkeys(ARROWS, ARROW) | dict.fromkeys(NOCKS, NOCK)
    assert {drawing['Id'] for drawing in project['Layers']} == set(identities)
    for drawing in project['Layers']:
        assert sha(bundle / drawing['Texture']) == source_pins[identities[drawing['Id']]]
    clip, = project['Clips']
    assert clip['Direction'] == facing and not clip['Loop']
    cumulative = [0, *accumulate(clip['DurationsMs'])]
    tracks = {track['LayerId']: list(sample_track(track, len(clip['DurationsMs']))) for track in clip['Tracks']}
    assert distinct(cell['SourceFrame'] for cell in tracks[body]) == list(range(16))
    marks = clip['Markers']
    assert [mark['Name'] for mark in marks] == [f'arrow_release_{index}' for index in range(1, 6)]
    assert [cumulative[mark['Frame']] for mark in marks] == metadata['releaseMs'] == list(RELEASE_MS)
    assert [[mark['X'], mark['Y']] for mark in marks] == metadata['releasePositions']
    ready = cumulative.index(70)
    assert all(tracks[nock][ready - 1]['Alpha'] == 0 and tracks[nock][ready]['Alpha'] == 1 for nock in NOCKS)
    for marker, phase, arrow, nock, spread in zip(marks, RELEASE_POSES, ARROWS, NOCKS, SPREAD):
        at = marker['Frame']
        assert tracks[body][at]['SourceFrame'] == phase
        assert tracks[nock][at - 1]['Alpha'] == 1 and tracks[nock][at]['Alpha'] == 0
        active = [index for index, cell in enumerate(tracks[arrow]) if cell['Alpha'] == 1]
        assert active == list(range(at, active[-1] + 1))
        assert cumulative[active[-1] + 1] - cumulative[at] == metadata['reviewFlightMs'] == 320
        assert distinct(tracks[arrow][index]['SourceFrame'] for index in active) == list(range(16))
        assert all(tracks[arrow][index]['Angle'] == (-90 + FACINGS.index(facing) * 45 + spread) for index in active)
    assert list(RELEASE_MS) == [sum(SOURCE_MS[:i]) for i in RELEASE_POSES]
    return dict(facing=facing, projectSha256=metadata['projectSha256'], releases=5)


def check_native(facing, ffmpeg):
    directory = ASSEMBLIES / facing
    video, log = directory / 'preview.mp4', directory / 'preview.godot.log'
    frames = decoded_frames(video, ffmpeg)
    assert frames == 96
    events = {}
    for frame, identifier, pose in LAYER_TICK.findall(verify_log(log)):
        events.setdefault(identifier, []).append((int(frame), int(pose)))
    body = 'class_linh_cung_skill_03_' + facing.lower()
    assert set(events) == {body, TARGET, *ARROWS, *NOCKS}
    assert distinct(index for _, index in events[body]) == list(range(16))
    assert len({events[nock][0][0] for nock in NOCKS}) == 1
    for arrow, nock in zip(ARROWS, NOCKS):
        assert distinct(index for _, index in events[arrow]) == list(range(16)), (facing, arrow)
        assert events[nock][-1][0] < events[arrow][0][0]
    releases = [events[arrow][0][0] for arrow in ARROWS]
    assert all(right - left in (6, 7) for left, right in zip(releases, releases[1:]))
    assert max(sum(first <= frame <= last for first, last in
                   ((events[arrow][0][0], events[arrow][-1][0]) for arrow in ARROWS))
               for frame in range(frames)) == 3
    indices = [max(1, events[body][0][0]), next(frame for frame, index in events[NOCKS[-1]] if index == 2),
               *releases, events[ARROWS[-1]][-1][0]]
    assert indices == sorted(set(indices))
    output = directory / 'sequence.png'
    montage(video, output, indices, 'crop=566:274:402:116,tile=4x2', ffmpeg)
    return dict(facing=facing, releaseNativeFrames=releases, framesDecoded=frames,
                movieSha256=sha(video), nativeLogSha256=sha(log),
                montageSha256=sha(output), sampleFrames=indices)


def audit(ffmpeg):
    records = read(ART / ('Candidates_' + BATCH) / 'candidate_manifest.json')['records']
    pins = {record['id']: record['sourceSha256'] for record in records}
    target = next(record for record in read(ART / 'visual_review.json')['sourceApprovals'] if record['id'] == TARGET)
    pins[TARGET] = target['sourceSha256']
    projects = [check_project(facing, pins) for facing in FACINGS]
    plan = read(OUTPUT / 'candidate_review_plan.json')
    sources = [check_source(entry, ffmpeg, OUTPUT) for entry in plan['entries']]
    assert len(sources) == len(records) == 10
    examples = [check_native(facing, ffmpeg) for facing in FACINGS]
    save(OUTPUT / 'native_audit.json',
         dict(batch=BATCH, catalogueUnchanged=True, productionApproved=False,
              nativeSourcePoses=sum(source['sourcePosesObserved'] for source in sources),
              sourceFramesDecoded=sum(source['decodedFrames'] for source in sources),
              assemblyFramesDecoded=sum(example['framesDecoded'] for example in examples),
              sourceViews=sources, projects=projects, nativeExamples=examples))
    print('Verified ten native sources and eight timelines with five authored releases each.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
