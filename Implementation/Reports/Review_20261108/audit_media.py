"""Read-only independent byte audit; no ffprobe or auditory claims."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('D:/Project/NGUMACHHUYENAN-review-media-policy-20261108/ClientGodot')
OUT = Path(__file__).resolve().parent / 'evidence'
FFMPEG = Path('D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')

def entries(value):
    if isinstance(value, dict):
        path = value.get('runtimePath', value.get('path'))
        if isinstance(path, str) and path.startswith('assets/') and 'sha256' in value:
            yield path, value
        for child in value.values():
            yield from entries(child)
    elif isinstance(value, list):
        for child in value:
            yield from entries(child)

report = {'head': '9deb06c', 'manifests': {}, 'decode': [], 'limits': ['No ear audition', 'No Godot playback', 'No fresh loudness measurement', 'Source packs not fully revalidated']}
REPO = ROOT.parent
COMMON = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], cwd=REPO, text=True).strip())
if not COMMON.is_absolute():
    COMMON = (REPO / COMMON).resolve()
resolved = {}
for name in ('audio/RUNTIME_AUDIO_manifest_v1.json', 'cinematics/RUNTIME_CINEMATICS_manifest_v1.json'):
    data = json.loads((ROOT / 'assets' / name).read_text(encoding='utf-8'))
    rows = list(entries(data))
    mismatches = []
    git_verified = 0
    for path, metadata in rows:
        binary = (ROOT / path).read_bytes()
        if binary.startswith(b'version https://git-lfs'):
            mismatches.append({'path': path, 'error': 'LFS_POINTER'})
        elif hashlib.sha256(binary).hexdigest() != metadata['sha256'] or ('sizeBytes' in metadata and len(binary) != metadata['sizeBytes']):
            mismatches.append({'path': path, 'error': 'HASH_OR_SIZE'})
        blob = subprocess.check_output(['git', 'cat-file', 'blob', 'HEAD:ClientGodot/' + path], cwd=REPO)
        if blob.startswith(b'version https://git-lfs'):
            oid = blob.decode().split('oid sha256:')[1].splitlines()[0]
            object_path = COMMON / 'lfs/objects' / oid[:2] / oid[2:4] / oid
            if object_path.exists():
                blob = object_path.read_bytes()
                resolved[path] = object_path
        else:
            resolved[path] = ROOT / path
        if hashlib.sha256(blob).hexdigest() == metadata['sha256'] and ('sizeBytes' not in metadata or len(blob) == metadata['sizeBytes']):
            git_verified += 1
    report['manifests'][name] = {'references': len(rows), 'uniquePaths': len(set(p for p, _ in rows)), 'workingTreeMismatches': mismatches, 'gitBlobOrLfsObjectsVerified': git_verified}
    if 'sceneClips' in data:
        report['campaign'] = {'totals': data['campaignTotals'], 'videoScenes': len(data['sceneClips']), 'prologueSeparate': 'prologue' in data}

cinema = json.loads((ROOT / 'assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json').read_text())
samples = [ROOT / e['path'] for scene in cinema['sceneClips'] if scene['sceneId'] in ('CIN_001', 'CIN_006') for kind, e in scene['files'].items() if kind == 'ogv']
samples += list((ROOT / 'assets/audio/mix/p0_v3').glob('*'))[:1]
for path in samples:
    actual = resolved.get(path.relative_to(ROOT).as_posix(), path)
    result = subprocess.run([str(FFMPEG), '-hide_banner', '-v', 'error', '-i', str(actual), '-f', 'null', '-'], capture_output=True, text=True, timeout=60)
    report['decode'].append({'path': str(path.relative_to(ROOT)), 'exit': result.returncode, 'stderr': result.stderr[-2000:]})
OUT.mkdir(exist_ok=True)
(OUT / 'media-independent.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
