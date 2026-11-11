"""Verify old sheet availability and original Git LFS hashes; never edits any bitmap."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'Art_Source/Actor_Library_20261107'


def audit():
    paths = subprocess.check_output(['git', 'ls-files', 'Art_Source/Actor_Library_20261107/Sheets'], cwd=ROOT, text=True).splitlines()
    stream = io.BytesIO(subprocess.check_output(['git', 'cat-file', '--batch'], cwd=ROOT,
                                              input=''.join('HEAD:' + p + '\n' for p in paths).encode()))
    entries = []
    for path in paths:
        header = stream.readline().decode().split()
        assert len(header) == 3 and header[1] == 'blob', 'missing HEAD source ' + path
        blob = stream.read(int(header[2])); assert stream.read(1) == b'\n'
        match = re.search(rb'oid sha256:([a-f0-9]{64})', blob)
        expected = match[1].decode() if match else hashlib.sha256(blob).hexdigest()
        local = ROOT / path
        row = dict(file=path, exists=local.is_file(), expectedSha256=expected)
        if local.is_file():
            data = local.read_bytes()
            row.update(sha256=hashlib.sha256(data).hexdigest(), lfsPointerOnly=data.startswith(b'version https://git-lfs.github.com/spec/'))
            try:
                with Image.open(io.BytesIO(data)) as image:
                    row.update(size=list(image.size), mode=image.mode)
                    image.verify()
                row['validImage'] = True
            except Exception:
                row['validImage'] = False
            row['matchesOriginal'] = row['sha256'] == expected
        entries.append(row)
    records = json.loads((ART / 'generation_records.json').read_text(encoding='utf8'))
    record_missing = [r['source'] for r in records if not (ART / r['source']).is_file()]
    pages = json.loads((ROOT / 'ClientGodot/assets/actor_library_v1/pages.json').read_text(encoding='utf8'))['pages']
    exports = []
    for page in pages:
        if not page.get('file'):
            continue
        source = ART / page['source']
        target = ROOT / 'ClientGodot/assets/actor_library_v1' / page['file']
        exports.append(dict(id=page['id'], matchesSource=source.is_file() and target.is_file() and source.read_bytes() == target.read_bytes()))
    summary = dict(trackedOldSheets=len(entries), present=sum(r['exists'] for r in entries),
                   originalHashMatches=sum(r.get('matchesOriginal', False) for r in entries),
                   validPng=sum(r.get('validImage', False) for r in entries),
                   lfsPointerOnly=sum(r.get('lfsPointerOnly', False) for r in entries),
                   missingRecordSources=record_missing, runtimeExports=len(exports),
                   runtimeOriginalCopies=sum(r['matchesSource'] for r in exports),
                   grouped={kind: sum(Path(r['file']).name.startswith(prefix) for r in entries) for kind, prefix in
                            [('class', 'class_'), ('mob', 'mob_'), ('npc', 'npc_'), ('vfx', 'sk_')]})
    result = dict(scope='RESTORATION_OF_PREEXISTING_FILES_NOT_FULL_GAME_OR_VISUAL_APPROVAL', summary=summary, files=entries, runtime=exports,
                  note='Minh Kiem inherited motion16 sources remain in Art_Source/Motion_16F_20261106; not missing from this sheet folder. Existing visual HOLDs and incomplete production coverage remain.')
    assert entries and summary['present'] == summary['validPng'] == summary['originalHashMatches'] == len(entries), summary
    assert summary['lfsPointerOnly'] == 0 and not record_missing and summary['runtimeOriginalCopies'] == len(exports), summary
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--output', type=Path); args = parser.parse_args()
    result = audit()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result['summary'], ensure_ascii=False))
