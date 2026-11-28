"""Verify Khoa Mach source movies and extract native shot sequences."""
import argparse
import re
import subprocess

from build_linh_cung_khoa_mach_preview import ARROW, BODY, BUNDLE, FACING_LAYOUTS, MARK, TAIL, TARGET
from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, read, save, sha

SOURCE_TICK = re.compile(r'ART_STUDIO_SOURCE_TICK nativeFrame=(\d+) sourceFrame=(\d+)')
LAYER_TICK = re.compile(r'ART_STUDIO_LAYER_TICK nativeFrame=(\d+) layer=(\S+) sourceFrame=(\d+)')


def decoded_frames(movie, ffmpeg):
    result = subprocess.run([ffmpeg, '-v', 'error', '-progress', 'pipe:1', '-nostats',
                             '-i', str(movie), '-map', '0:v:0', '-f', 'null', '-'],
                            capture_output=True, text=True, check=True)
    assert not result.stderr.strip()
    return int(re.findall(r'^frame=(\d+)', result.stdout, re.M)[-1])


def verify_log(path):
    log = path.read_text(encoding='utf-8-sig')
    assert '\0' not in log and not re.search(r'(^ERROR:|SCRIPT ERROR)', log, re.M)
    return log


def audit_sources(ffmpeg, pilot_only=False):
    plan = read(OUTPUT / 'candidate_review_plan.json')
    source_views = []
    for entry in plan['entries']:
        if pilot_only and entry['id'] not in (BODY, ARROW, TAIL):
            continue
        stem = 'raw_' + entry['id']
        movie = OUTPUT / (stem + '.mp4')
        receipt = read(OUTPUT / (stem + '.capture_receipt.json'))
        assert receipt['sourceSha256'] == entry['sourceSha256'] == sha(ROOT / entry['source'])
        assert receipt['projectSha256'] == sha(ROOT / entry['project'])
        assert receipt['movieSha256'] == sha(movie)
        clock = SOURCE_TICK.findall(verify_log(OUTPUT / (stem + '.godot.log')))
        assert list(dict.fromkeys(int(pose) for _, pose in clock)) == list(range(16))
        assert decoded_frames(movie, ffmpeg) == 180
        source_views.append(dict(id=entry['id'], projectSha256=receipt['projectSha256'],
                                 sourceSha256=receipt['sourceSha256'], movieSha256=receipt['movieSha256'],
                                 montageSha256=sha(OUTPUT / (stem + '_poses.png')), decodedFrames=180,
                                 sourcePosesObserved=16))
        if entry['id'] == ARROW:
            phases = [int(pose) for _, pose in clock]
            wrap_index = next(i for i in range(2, len(phases)-1) if phases[i-2:i+2] == [14,15,0,1])
            native_frames = [int(clock[i][0]) + 1 for i in range(wrap_index-2, wrap_index+2)]
            seam = OUTPUT / (stem + '_loop_wrap.png')
            selected = '+'.join(f'eq(n,{frame})' for frame in native_frames)
            subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-vf',
                            f"select='{selected}',crop=256:256:550:120,tile=4x1",
                            '-frames:v', '1', str(seam)], check=True)
            source_views[-1]['loopWrap'] = dict(nativeFrames=native_frames, montage=seam.name,
                                               sha256=sha(seam))
    return source_views


def audit_preview(ffmpeg, facing, source_views):
    bundle = BUNDLE.with_name('KhoaMach_' + facing)
    body = 'class_linh_cung_skill_01_' + facing.lower()
    descriptor = read(bundle / 'assembly_descriptor.json')
    project = read(bundle / 'project.json')
    assert descriptor['projectSha256'] == sha(bundle / 'project.json')
    for item in descriptor['sources'].values():
        assert sha(ART / item['source']) == item['sha256'] == sha(bundle / item['texture'])
    clip = project['Clips'][0]
    assert clip['Direction'] == facing
    release, contact = clip['Markers']
    for marker, kind, ms, point in (
        (release, 'bow_release', 'releaseMs', 'releasePosition'),
        (contact, 'confirmed_contact_preview', 'contactMs', 'contactPosition'),
    ):
        assert marker['Name'] == kind
        assert sum(clip['DurationsMs'][:marker['Frame']]) == descriptor[ms]
        assert [marker['X'], marker['Y']] == descriptor[point]
    tracks = {track['LayerId']: track for track in clip['Tracks']}
    arrow_poses = [key['Pose'] for key in tracks[ARROW]['Keys'] if key['Pose']['Alpha'] > 0]
    assert [pose['SourceFrame'] for pose in arrow_poses] == sorted(pose['SourceFrame'] for pose in arrow_poses)
    assert all(pose['Angle'] == (FACING_LAYOUTS[facing][2] if facing != 'E' else 0) for pose in arrow_poses)
    assert not tracks[ARROW]['Keys'][contact['Frame']]['Pose']['Alpha']
    for identifier in (TAIL, MARK):
        pose = tracks[identifier]['Keys'][contact['Frame']]['Pose']
        assert pose['Alpha'] == 1 and pose['SourceFrame'] == 0
    events = {}
    for frame, layer, pose in LAYER_TICK.findall(verify_log(bundle / 'preview.godot.log')):
        events.setdefault(layer, []).append((int(frame), int(pose)))
    assert set(events) == {body, ARROW, TAIL, TARGET, MARK}
    for layer in events:
        assert list(dict.fromkeys(pose for _, pose in events[layer])) == list(range(16)), layer
    assert events[ARROW][-1][0] < events[TAIL][0][0] == events[MARK][0][0]
    movie = bundle / 'preview.mp4'
    assert decoded_frames(movie, ffmpeg) == 120
    draw_pose = descriptor['releaseMs'] // 60 - 1
    samples = [(body, 0), (body, draw_pose), (ARROW, 0), (ARROW, 8), (ARROW, 15),
               (MARK, 0), (TAIL, 9), (MARK, 15)]
    # Sample the frame recorded by the layer clock. A 20 ms final flight
    # pose can last one 60 Hz image; adding one would sample contact.
    frames = [next(max(1, frame) for frame, pose in events[layer] if pose == selected)
              for layer, selected in samples]
    assert frames == sorted(set(frames))
    montage = bundle / 'shot_sequence.png'
    select = '+'.join(f'eq(n,{frame})' for frame in frames)
    crop = 'crop=416:260:476:116' if facing == 'E' else 'crop=448:260:460:116'
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-vf',
                    f"select='{select}',{crop},tile=4x2",
                    '-frames:v', '1', str(montage)], check=True)
    result = dict(projectSha256=descriptor['projectSha256'], sourceViews=source_views,
                  movieSha256=sha(movie), logSha256=sha(bundle / 'preview.godot.log'),
                  montageSha256=sha(montage), framesDecoded=120, reviewFrames=frames,
                  sourcePhasesPerLayer={layer:16 for layer in events}, productionApproved=False)
    save(bundle / 'native_audit.json', result)
    return result


def audit(ffmpeg, facing):
    source_views = audit_sources(ffmpeg, pilot_only=facing == 'E')
    if facing != 'all':
        audit_preview(ffmpeg, facing, [view for view in source_views
                                       if view['id'] in (ARROW, TAIL, 'class_linh_cung_skill_01_' + facing.lower())])
        print(f'Checked {facing} shot and its native source captures.')
        return
    # One east body, every other authored facing, and two new effect sources.
    assert len(source_views) == len(FACING_LAYOUTS) + 3
    # The already reviewed E pilot keeps its original proof and pin.
    east = read(BUNDLE / 'native_audit.json')
    assert east['movieSha256'] == sha(BUNDLE / 'preview.mp4')
    assert east['projectSha256'] == sha(BUNDLE / 'project.json')
    assert east['logSha256'] == sha(BUNDLE / 'preview.godot.log')
    assert decoded_frames(BUNDLE / 'preview.mp4', ffmpeg) == east['framesDecoded'] == 120
    previews = {'E': east}
    for direction in FACING_LAYOUTS:
        related = (ARROW, TAIL, 'class_linh_cung_skill_01_' + direction.lower())
        previews[direction] = audit_preview(ffmpeg, direction, [v for v in source_views if v['id'] in related])
    save(OUTPUT / 'native_audit.current.json',
         dict(sourceViews=source_views, previewFacings=list(previews),
              previewAudits={direction: sha(BUNDLE.with_name('KhoaMach_' + direction) / 'native_audit.json')
                             for direction in previews},
              sourceFramesDecoded=sum(v['decodedFrames'] for v in source_views),
              previewFramesDecoded=sum(v['framesDecoded'] for v in previews.values()),
              productionApproved=False))
    print(f'Checked {len(source_views)} source movies and {len(previews)} assembled shots.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    parser.add_argument('--facing', choices=('all', 'E', *FACING_LAYOUTS), default='E')
    args = parser.parse_args()
    audit(args.ffmpeg, args.facing)
