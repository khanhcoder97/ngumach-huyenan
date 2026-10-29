"""Validate design cue references/budgets; never claim that audio clips exist."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    catalog = json.loads((ROOT / 'Implementation/Content/DesignBaselines/audio_cues_v1.json').read_text(encoding='utf-8-sig'))
    skills = json.loads((ROOT / 'Implementation/Content/DesignBaselines/skill_vfx_art_v1.json').read_text(encoding='utf-8-sig'))['skills']
    expected = {s['skillId']: s['soundKey'] for s in skills}
    cues = catalog['cues']
    ids = [c['cueKey'] for c in cues]
    assert len(ids) == len(set(ids)), 'Duplicate cueKey'
    mapped = {c['skillId']: c['cueKey'] for c in cues if c.get('skillId')}
    assert mapped == expected and len(mapped) == 30, 'Canonical skill soundKey mismatch'
    assert catalog['activation'] == 'DESIGN_ONLY_AUDIO_NOT_IN_RUNTIME'
    assert catalog['voiceCaps'] == dict(footstep=8, hit=16, skill=12, UI=4, ambience=4, music=2)
    for c in cues:
        assert c['bus'] in ('Music', 'Ambience', 'SFX', 'UI'), c['cueKey']
        assert c['voiceGroup'] in catalog['voiceCaps'], c['cueKey']
        assert 0 < c['maxInstances'] <= catalog['voiceCaps'][c['voiceGroup']], c['cueKey']
        assert 0 <= c['priority'] <= 100 and 0 <= c['gain'] <= 1, c['cueKey']
        assert c['assetState'] == 'MISSING' and c['clipPath'] is None and c['sourceLicense'] is None, 'Do not certify unproduced clips'
        assert c['sourceRef'] and c['triggerSemantic'] and c['wireStatus'] == 'REQUIRES_PRESENTATION_ADAPTER', c['cueKey']
        assert c['maxDistanceWu'] >= c['minDistanceWu'] >= 0
        if c['loop']:
            assert c['stopPolicy'] == 'STATE_END_CANCEL_DESPAWN_OR_MAP_EXIT', c['cueKey']
    parry = next(c for c in cues if c.get('skillId') == 'SK-MK-01')
    assert parry['triggerSemantic'] == 'COUNTER_CONFIRMED'
    print(f'PASS: {len(cues)} unique planned cues, 30 canonical skill refs; all clips explicitly MISSING. No audio/engine/license approval.')


if __name__ == '__main__':
    main()
