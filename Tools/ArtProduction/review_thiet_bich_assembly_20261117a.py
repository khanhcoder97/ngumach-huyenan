"""Audit native layer clocks and extract review evidence, never asset pixels."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

from inspect_actor_library import ART, ROOT
from prepare_thach_chuy_candidates_20261116c import save


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def review(bundle, ffmpeg):
    project_path = bundle / 'project.json'
    project = json.loads(project_path.read_text(encoding='utf8'))
    descriptor = json.loads((bundle / 'assembly_descriptor.json').read_text(encoding='utf8'))
    assert sha(project_path) == descriptor['projectSha256'], 'Project changed after assembly registration'
    assert project['ProductionApproved'] is False
    original_pins = {}
    for item in descriptor['sourceInputs'].values():
        registration = ROOT / 'Implementation/Reports/Evidence/Actor_Batch_20261116c/Candidate_Studio' / item['id'] / 'source_registration.json'
        assert sha(registration) == item['registrationSha256'], 'Source registration changed'
        source = ART / json.loads(registration.read_text(encoding='utf8'))['record']['source']
        assert sha(source) == item['pngSha256']
        assert sha(bundle / 'textures' / (item['pngSha256'] + '.png')) == item['pngSha256']
        original_pins[item['id']] = item['pngSha256']
    log_path = bundle / 'native.godot.log'
    log = log_path.read_text(encoding='utf-8-sig')
    assert '\0' not in log and not re.search(r'^ERROR:', log, re.M), 'Native error or interrupted log'
    ticks = [(int(a), b, int(c)) for a, b, c in re.findall(r'ART_STUDIO_LAYER_TICK nativeFrame=(\d+) layer=(\S+) sourceFrame=(\d+)', log)]
    coverage = {}
    for layer in project['Layers']:
        phases = sorted({phase for _, name, phase in ticks if name == layer['Id']})
        assert phases == list(range(16)), (layer['Id'], phases)
        coverage[layer['Id']] = phases
    movie = bundle / 'native.mp4'
    decoded = subprocess.run([ffmpeg, '-v', 'error', '-i', str(movie), '-map', '0:v:0', '-f', 'null', '-'], capture_output=True, text=True)
    assert decoded.returncode == 0 and not decoded.stderr.strip(), decoded.stderr
    samples = []
    for phase in ('gain', 'sustain', 'crack_overlay', 'end'):
        for source in (0, 8, 15):
            first = next(frame for frame, name, pose in ticks if name == 'guard_shoulder_' + phase and pose == source)
            samples.append(dict(layer='guard_shoulder_' + phase, sourceFrame=source, nativeFrame=first + 1))
    montage = bundle / 'phase_chain_review.png'
    # A crop of a decoded native movie is review evidence, never an authored sprite.
    # Crack and sustain overlap in time. Preserve row order and shared frames;
    # an OR-selection would silently de-duplicate and chronologically reorder them.
    split = '[0:v]split=12' + ''.join('[v%d]' % i for i in range(12))
    extracts = ['[v%d]select=eq(n\\,%d),crop=210:180:580:108,scale=420:360:flags=neighbor,setpts=PTS-STARTPTS[o%d]' % (i, item['nativeFrame'], i) for i, item in enumerate(samples)]
    layout = '|'.join('%d_%d' % ((i % 3) * 420, (i // 3) * 360) for i in range(12))
    stack = ''.join('[o%d]' % i for i in range(12)) + 'xstack=inputs=12:layout=' + layout + '[out]'
    command = [ffmpeg, '-v', 'error', '-y', '-i', str(movie), '-filter_complex', ';'.join([split, *extracts, stack]), '-map', '[out]', '-frames:v', '1', str(montage)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = dict(scope='NATIVE_THREE_SOCKET_PHASE_CLOCK_AND_IMMUTABLE_SOURCE_AUDIT', projectSha256=sha(project_path), movieSha256=sha(movie), nativeLogSha256=sha(log_path), sourcePins=original_pins, layerSourceCoverage=coverage, sampleOrder=samples, montageSha256=sha(montage), originalPngsUnchanged=True, decodePassed=True, manualVisualReviewComplete=False, productionApproved=False, limitations=['Active layer clock coverage does not prove visible pixels for the occluded back plate.', 'Fixed-clock movie capture does not measure gameplay FPS.', 'Final activation pose is held for authoring inspection; gameplay idle/event/8-facing acceptance is pending.'])
    save(bundle / 'native_audit.json', report)
    print(json.dumps(dict(bundle=str(bundle), auditedLayers=len(coverage), originalSources=len(original_pins), sourcePhasesPerLayer=16, sampledPhases=len(samples), productionApproved=False)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--bundle', type=Path, default=ROOT / 'Implementation/Reports/Evidence/Actor_Assembly_20261117a/ThietBich_S_trial1')
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    args = parser.parse_args()
    review(args.bundle, args.ffmpeg)
