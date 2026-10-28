"""Validate design handoff coverage and reference provenance, not game balance/art quality."""
from pathlib import Path
import hashlib
import json
import re
import struct

ROOT = Path(__file__).resolve().parents[2]


def main():
    data = json.loads((ROOT / 'Implementation/Content/DesignBaselines/skill_vfx_art_v1.json').read_text(encoding='utf-8'))
    source = (ROOT / 'docs/production/Combat_Skills_VFX_Animation_Spec_vi.md').read_text(encoding='utf-8')
    expected = set(re.findall(r'\*\*(SK-[A-Z]{2}-0[1-6]) —', source))
    skills = data['skills']
    ids = [s['skillId'] for s in skills]
    errors = []
    if len(ids) != 30 or len(set(ids)) != 30 or set(ids) != expected:
        errors.append('Expected exactly all 30 canonical active skills without duplicates')
    class_prefix = {'CLASS_MINH_KIEM': 'MK', 'CLASS_ANH_DAO': 'AD',
                    'CLASS_HUYEN_BUT': 'HB', 'CLASS_THACH_CHUY': 'TC', 'CLASS_LINH_CUNG': 'LC'}
    if {c['classId'] for c in data['classes']} != set(class_prefix):
        errors.append('Expected five canonical class palettes')
    for skill in skills:
        sid = skill['skillId']
        if skill['classId'] not in class_prefix or sid.split('-')[1] != class_prefix.get(skill['classId']):
            errors.append(f'{sid}: class mismatch')
        if skill['hudSlot'] != int(sid[-2:]) or skill['sourcePixelsPerUnit'] != 20:
            errors.append(f'{sid}: slot/PPU mismatch')
        if set(skill['visualPhases']) != {'prep', 'release', 'fade'} or not all(skill['visualPhases'].values()):
            errors.append(f'{sid}: incomplete visual phases')
        if skill['maxModuleCellPx'] not in (64, 96, 128, 256, 512):
            errors.append(f'{sid}: unsupported cell budget')
        if skill['wireStatus'] != 'REQUIRES_EVENT_ADAPTER_NOT_NEW_WIRE_ENUM':
            errors.append(f'{sid}: semantic cue must not masquerade as implemented wire event')
        for key in ('mechanicsSourceText', 'attachMode', 'shapeKey', 'soundKey', 'iconSilhouetteVi', 'lowFxPolicyVi', 'timingPolicy'):
            if not skill.get(key):
                errors.append(f'{sid}: missing {key}')
    manifest = json.loads((ROOT / 'docs/production/Art_Concept_References/skill_vfx_v1/reference_manifest.json').read_text(encoding='utf-8'))
    if len(manifest['boards']) != 5:
        errors.append('Expected five concept boards')
    for board in manifest['boards']:
        path = (ROOT / board['path']).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            errors.append(f'Invalid board path: {board["path"]}')
            continue
        raw = path.read_bytes()
        if raw[:8] != b'\x89PNG\r\n\x1a\n' or len(raw) < 24:
            errors.append(f'{path.name}: PNG missing or unresolved LFS object')
            continue
        if tuple(struct.unpack('>II', raw[16:24])) != (board['width'], board['height']):
            errors.append(f'{path.name}: dimensions mismatch')
        if hashlib.sha256(raw).hexdigest() != board['sha256']:
            errors.append(f'{path.name}: hash mismatch')
    if errors:
        print('\n'.join('ERROR: ' + e for e in errors))
        return 1
    print('PASS: 30 canonical skill art cards, five class palettes, five PNG references with matching hashes/dimensions. Runtime VFX/adapter/balance/device checks remain unverified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
