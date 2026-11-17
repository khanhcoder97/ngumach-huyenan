"""Verify the east Khoa Mach source movies and extract the native shot sequence."""
import argparse
import re
import subprocess

from build_linh_cung_khoa_mach_preview import ARROW, BODY, BUNDLE, MARK, TAIL, TARGET
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


def audit(ffmpeg):
    plan = read(OUTPUT / 'candidate_review_plan.json')
    source_views = []
    for entry in plan['entries']:
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

    descriptor = read(BUNDLE / 'assembly_descriptor.json')
    assert descriptor['projectSha256'] == sha(BUNDLE / 'project.json')
    for item in descriptor['sources'].values():
        assert sha(ART / item['source']) == item['sha256'] == sha(BUNDLE / item['texture'])
    events = {}
    for frame, layer, pose in LAYER_TICK.findall(verify_log(BUNDLE / 'preview.godot.log')):
        events.setdefault(layer, []).append((int(frame), int(pose)))
    assert set(events) == {BODY, ARROW, TAIL, TARGET, MARK}
    for layer in events:
        assert list(dict.fromkeys(pose for _, pose in events[layer])) == list(range(16)), layer
    assert events[ARROW][-1][0] < events[TAIL][0][0] == events[MARK][0][0]
    movie = BUNDLE / 'preview.mp4'
    assert decoded_frames(movie, ffmpeg) == 120
    samples = [(BODY, 0), (BODY, 7), (ARROW, 0), (ARROW, 8), (ARROW, 15),
               (MARK, 0), (TAIL, 9), (MARK, 15)]
    # Sample the frame recorded by the layer clock. A 20 ms final flight
    # pose can last one 60 Hz image; adding one would sample contact.
    frames = [next(max(1, frame) for frame, pose in events[layer] if pose == selected)
              for layer, selected in samples]
    assert frames == sorted(set(frames))
    montage = BUNDLE / 'shot_sequence.png'
    select = '+'.join(f'eq(n,{frame})' for frame in frames)
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-vf',
                    f"select='{select}',crop=416:260:476:116,tile=4x2",
                    '-frames:v', '1', str(montage)], check=True)
    save(BUNDLE / 'native_audit.json',
         dict(projectSha256=descriptor['projectSha256'], sourceViews=source_views,
              movieSha256=sha(movie), logSha256=sha(BUNDLE / 'preview.godot.log'),
              montageSha256=sha(montage), framesDecoded=120, reviewFrames=frames,
              sourcePhasesPerLayer={layer:16 for layer in events}, productionApproved=False))
    print(f'Checked {len(source_views)} source movies, one east shot and {len(frames)} native samples.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
