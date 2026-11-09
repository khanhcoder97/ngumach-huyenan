import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('D:/Project/NGUMACHHUYENAN-review-media-20261109').resolve()
OUT = Path(__file__).resolve().parent / 'evidence/media-audit.json'
FFMPEG = 'D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe'

def file_path(value):
    rel = value if value.startswith('ClientGodot/') else 'ClientGodot/' + value
    path = (ROOT / rel).resolve()
    assert path.is_relative_to(ROOT), 'Media path escaped checkout'
    return path

def entries(value):
    if isinstance(value, dict):
        path = value.get('runtimePath', value.get('path'))
        if isinstance(path, str) and path.startswith(('assets/', 'ClientGodot/assets/')) and 'sha256' in value:
            yield path, value
        for child in value.values():
            yield from entries(child)
    elif isinstance(value, list):
        for child in value:
            yield from entries(child)

report = {'head': '14b588c663a6d53295b34f1d632e84c48c7f5ca9', 'manifests': {}, 'streamChecks': [], 'limits': ['No ear audition', 'No native playback', 'No loudness remeasurement', 'Only first 50ms decoded per OGV stream check']}
for name in ['audio/RUNTIME_AUDIO_manifest_v1.json', 'cinematics/RUNTIME_CINEMATICS_manifest_v1.json']:
    rows = list(entries(json.loads((ROOT / 'ClientGodot/assets' / name).read_text(encoding='utf-8'))))
    bad = []
    for path, item in rows:
        binary = file_path(path).read_bytes()
        if binary.startswith(b'version https://git-lfs') or hashlib.sha256(binary).hexdigest() != item['sha256'] or ('sizeBytes' in item and len(binary) != item['sizeBytes']):
            bad.append(path)
    report['manifests'][name] = {'references': len(rows), 'mismatches': bad}

metadata = json.loads((ROOT / 'ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json').read_text(encoding='utf-8'))
report['playbackCounts'] = metadata['counts']
for scene in metadata['scenes']:
    ogv = scene['video']['ogv']
    result = subprocess.run([FFMPEG, '-hide_banner', '-threads', '1', '-i', str(file_path(ogv['path'])), '-t', '0.05', '-f', 'null', '-'], capture_output=True, text=True, timeout=30)
    actual = 'Audio:' in result.stderr
    expected = scene['hasEmbeddedSoundtrack']
    report['streamChecks'].append({'sceneId': scene['sceneId'], 'hasAudio': actual, 'expected': expected, 'decodeExit': result.returncode, 'matches': actual == expected and result.returncode == 0})

names = json.loads((ROOT / 'Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json').read_text(encoding='utf-8'))
report['pronunciationCounts'] = names['counts']
report['auditionStatus'] = names['auditionStatus']
report['verdict'] = 'PASS' if not any(v['mismatches'] for v in report['manifests'].values()) and all(v['matches'] for v in report['streamChecks']) else 'FAIL'
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(0 if report['verdict'] == 'PASS' else 1)
