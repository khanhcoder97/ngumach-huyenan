"""Check native Studio playback for the five-facing sanctuary preview."""
import argparse
import re
import subprocess
from itertools import groupby

from build_thach_chuy_sanctuary_preview import BUNDLE, FACINGS
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha

LAYER_TICK = re.compile(r'ART_STUDIO_LAYER_TICK nativeFrame=(\d+) layer=(\S+) sourceFrame=(\d+)')


def read_capture(facing, project_sha, ffmpeg):
    prefix = BUNDLE / ('preview_' + facing)
    movie = prefix.with_suffix('.mp4')
    log_path = prefix.with_suffix('.godot.log')
    receipt = read(prefix.with_suffix('.receipt.json'))
    assert receipt['direction'] == facing and receipt['projectSha256'] == project_sha
    assert receipt['movieSha256'] == sha(movie) and receipt['logSha256'] == sha(log_path)
    log = log_path.read_text(encoding='utf-8-sig')
    assert '\0' not in log and not re.search(r'(^ERROR:|SCRIPT ERROR)', log, re.M)
    ticks = {}
    for frame, layer, source in LAYER_TICK.findall(log):
        ticks.setdefault(layer, []).append((int(frame), int(source)))
    expected = {'body_' + facing, 'charge', 'plate_back', 'plate_left', 'plate_right', 'sustain', 'end'}
    assert set(ticks) == expected, (facing, set(ticks))
    phase_counts = {}
    for layer, events in ticks.items():
        phases = list(dict.fromkeys(pose for _, pose in events))
        assert phases == list(range(16)), (facing, layer, phases)
        phase_counts[layer] = len(phases)
    sustain = [pose for pose, _ in groupby(pose for _, pose in ticks['sustain'])]
    assert sustain == list(range(16)) * 2, (facing, sustain)
    result = subprocess.run(
        [ffmpeg, '-v', 'error', '-progress', 'pipe:1', '-nostats', '-i', str(movie),
         '-map', '0:v:0', '-f', 'null', '-'],
        capture_output=True, text=True, check=True)
    assert not result.stderr.strip()
    decoded = int(re.findall(r'^frame=(\d+)', result.stdout, re.M)[-1])
    assert decoded == 324

    phase_samples = [('charge', 0), ('charge', 12), ('plate_back', 0), ('sustain', 0),
                     ('plate_back', 15), ('sustain', 15), ('end', 0), ('end', 8), ('end', 15)]
    frames = [next(frame + 1 for frame, pose in ticks[layer] if pose == source)
              for layer, source in phase_samples]
    assert frames == sorted(set(frames))
    select = '+'.join('eq(n,%d)' % frame for frame in frames)
    montage = prefix.with_suffix('.phases.png')
    subprocess.run([ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-vf',
                    f"select='{select}',crop=416:260:476:116,tile=3x3",
                    '-frames:v', '1', str(montage)], check=True)
    return dict(direction=facing, movie=movie.name, movieSha256=receipt['movieSha256'],
                logSha256=receipt['logSha256'], decodedFrames=decoded,
                sourcePhasesByLayer=phase_counts, sustainCyclesObserved=2,
                montage=montage.name, montageSha256=sha(montage), nativeFrames=frames)


def audit(directions, ffmpeg):
    project = BUNDLE / 'project.json'
    descriptor = read(BUNDLE / 'assembly_descriptor.json')
    assert descriptor['projectSha256'] == sha(project)
    manifest = read(ART / 'Candidates_20261116c/candidate_manifest.json')
    records = {entry['id']: entry for entry in manifest['records']}
    for identifier, item in descriptor['sourceInputs'].items():
        record = records[identifier]
        registration = EV / 'Candidate_Studio' / identifier / 'source_registration.json'
        assert sha(registration) == item['registrationSha256']
        assert sha(ART / record['source']) == item['pngSha256'] == record['sourceSha256']
        assert sha(BUNDLE / 'textures' / (item['pngSha256'] + '.png')) == item['pngSha256']
    captures = [read_capture(facing, descriptor['projectSha256'], ffmpeg) for facing in directions]
    if tuple(directions) == FACINGS:
        save(BUNDLE / 'native_audit.json',
             dict(scope='SANCTUARY_FIVE_FACING_STUDIO_PLAYBACK', projectSha256=sha(project),
                  sourceInputs=descriptor['sourceInputs'], previewFrameClock=60,
                  captures=captures, productionApproved=False))
    print(f'Checked {len(captures)} native previews and extracted their phase views.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--direction', choices=FACINGS, action='append')
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    args = parser.parse_args()
    audit(tuple(args.direction) if args.direction else FACINGS, args.ffmpeg)
