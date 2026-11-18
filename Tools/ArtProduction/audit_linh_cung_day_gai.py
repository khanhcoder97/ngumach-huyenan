"""Check the Dây Gai source exports and native screenshots against Studio traces."""
import argparse
from itertools import groupby
import subprocess

from audit_linh_cung_khoa_mach_preview import LAYER_TICK, SOURCE_TICK, decoded_frames, verify_log
from prepare_linh_cung_day_gai import ASSEMBLIES, BODY, EFFECTS, FACINGS, OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, read, save, sha

CAPTURES = (('E', 'trigger', 216), ('S', 'expire', 288), ('NW', 'trigger', 216))


def distinct(values):
    return [value for value, _ in groupby(values)]


def check_source(entry, ffmpeg):
    prefix = OUTPUT / ('raw_' + entry['id'])
    movie = prefix.with_suffix('.mp4')
    receipt = read(prefix.with_suffix('.capture_receipt.json'))
    assert receipt['sourceSha256'] == entry['sourceSha256'] == sha(ROOT / entry['source'])
    assert receipt['projectSha256'] == sha(ROOT / entry['project'])
    assert receipt['movieSha256'] == sha(movie)
    trace = SOURCE_TICK.findall(verify_log(prefix.with_suffix('.godot.log')))
    phases = [int(pose) for _, pose in trace]
    assert list(dict.fromkeys(phases)) == list(range(16))
    frames = decoded_frames(movie, ffmpeg)
    assert frames == 180
    audit = dict(id=entry['id'], sourceSha256=receipt['sourceSha256'],
                 projectSha256=receipt['projectSha256'], movieSha256=receipt['movieSha256'],
                 montageSha256=sha(prefix.with_name(prefix.name + '_poses.png')),
                 sourcePosesObserved=16, decodedFrames=frames)
    if entry['loop']:
        at = next(i for i in range(len(phases) - 3) if phases[i:i+4] == [14, 15, 0, 1])
        indices = [max(1, int(tick)) for tick, _ in trace[at:at+4]]
        path = prefix.with_name(prefix.name + '_loop_wrap.png')
        montage(movie, path, indices, 'crop=256:256:550:120,tile=4x1', ffmpeg)
        audit['loopWrap'] = dict(nativeFrames=indices, montage=path.name, sha256=sha(path))
    return audit


def check_project(facing, records):
    bundle = ASSEMBLIES / facing
    project = read(bundle / 'project.json')
    body_id = 'class_linh_cung_skill_02_' + facing.lower()
    assert [drawing['Id'] for drawing in project['Layers']] == [body_id, *EFFECTS]
    for drawing in project['Layers']:
        record = records[drawing['Id']]
        assert sha(bundle / drawing['Texture']) == record['sourceSha256'] == sha(ART / record['source'])
    assert len(project['Clips']) == 2
    for editing, clip in zip(('trigger', 'expire'), project['Clips']):
        assert clip['Direction'] == facing and clip['Name'].endswith(editing) and not clip['Loop']
        marks = clip['Markers']
        assert [mark['Name'] for mark in marks] == ['seed_release', 'trap_growth', 'trap_armed', 'trap_' + editing]
        assert [mark['Frame'] for mark in marks] == sorted({m['Frame'] for m in marks})
        ground = [list(mark[key] for key in ('X', 'Y')) for mark in marks]
        assert all(point == list(BODY[facing][-1]) for point in ground)
        times = [sum(clip['DurationsMs'][:mark['Frame']]) for mark in marks]
        assert times == [BODY[facing][-2] * 70 + t for t in (0, 480, 1120, 1120 + (980 if editing == 'trigger' else 2240))]
        tracks = {track['LayerId']: track for track in clip['Tracks']}
        expected = (16, 16, 14 if editing == 'trigger' else 32, 16)
        for identifier, phases in zip(EFFECTS, expected):
            sequence = distinct(key['Pose']['SourceFrame'] for key in tracks[identifier]['Keys'] if key['Pose']['Alpha'] > 0)
            assert sequence == [index % 16 for index in range(phases)], (facing, editing, identifier)
        for i in range(len(clip['DurationsMs'])):
            visible = [name for name in EFFECTS if tracks[name]['Keys'][i]['Pose']['Alpha'] > 0]
            assert len(visible) == int(i >= marks[0]['Frame'])
            for name in visible:
                pose = tracks[name]['Keys'][i]['Pose']
                if name != EFFECTS[0]:
                    assert [pose['X'], pose['Y']] == ground[0]
    return dict(facing=facing, projectSha256=sha(bundle / 'project.json'), editableClips=2)


def montage(movie, path, indices, layout, ffmpeg):
    selections = '+'.join(f'eq(n,{index})' for index in indices)
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-vf',
                    f"select='{selections}',{layout}", '-frames:v', '1', str(path)], check=True)


def check_capture(facing, ending, frame_count, ffmpeg):
    bundle = ASSEMBLIES / facing
    prefix = bundle / ending
    movie, log = prefix.with_suffix('.mp4'), prefix.with_suffix('.godot.log')
    body = 'class_linh_cung_skill_02_' + facing.lower()
    assert decoded_frames(movie, ffmpeg) == frame_count
    events = {}
    for frame, id_, pose in LAYER_TICK.findall(verify_log(log)):
        events.setdefault(id_, []).append((int(frame), int(pose)))
    assert set(events) == {body, *EFFECTS}
    for identifier in (body, *EFFECTS):
        count = (14 if ending == 'trigger' else 32) if identifier == EFFECTS[2] else 16
        assert distinct(pose for _, pose in events[identifier]) == [i % 16 for i in range(count)], (identifier, ending)
    for first, second in zip(EFFECTS, EFFECTS[1:]):
        assert events[first][-1][0] < events[second][0][0]
    points = [(body, 0), (EFFECTS[0], 0), (EFFECTS[0], 8), (EFFECTS[1], 6),
              (EFFECTS[2], 0), (EFFECTS[2], 10), (EFFECTS[3], 7), (EFFECTS[3], 15)]
    indices = [next(max(1, frame) for frame, index in events[identifier] if index == pose)
               for identifier, pose in points]
    assert indices == sorted(set(indices))
    sheet = prefix.with_name(prefix.name + '_sequence.png')
    montage(movie, sheet, indices, 'crop=400:260:480:116,tile=4x2', ffmpeg)
    return dict(facing=facing, ending=ending, framesDecoded=frame_count,
                movieSha256=sha(movie), logSha256=sha(log), montageSha256=sha(sheet),
                phaseSamples=indices)


def audit(ffmpeg):
    manifest = read(ART / 'Candidates_20261118b/candidate_manifest.json')
    records = {record['id']: record for record in manifest['records']}
    plan = read(OUTPUT / 'candidate_review_plan.json')
    project_bindings = [check_project(facing, records) for facing in FACINGS]
    sources = [check_source(entry, ffmpeg) for entry in plan['entries']]
    assert len(sources) == len(records) == 12
    views = [check_capture(facing, ending, frames, ffmpeg) for facing, ending, frames in CAPTURES]
    save(OUTPUT / 'native_audit.json',
         dict(batch='20261118b', productionApproved=False, catalogueUnchanged=True,
              sourcePoses=sum(source['sourcePosesObserved'] for source in sources),
              sourceFramesDecoded=sum(source['decodedFrames'] for source in sources),
              assemblyFramesDecoded=sum(view['framesDecoded'] for view in views),
              sourceViews=sources, projects=project_bindings, nativeExamples=views))
    print(f'Checked {len(sources)} native sources, {len(project_bindings) * 2} timelines and {len(views)} assembled movies.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
