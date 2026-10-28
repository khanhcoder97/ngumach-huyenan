"""Check authored narrative handoff references/coverage; does not certify video quality."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    errors = []
    base = ROOT / 'Implementation/Content/Narrative'
    beats = json.loads((base / 'Narrative_Quest_Beats_v2.json').read_text(encoding='utf-8'))['quests']
    scenes = json.loads((base / 'Cinema_Production_Pack_v1.json').read_text(encoding='utf-8'))['scenes']
    with (ROOT / 'docs/production/Quest_Dialogue_Production_Data_vi.csv').open(encoding='utf-8-sig', newline='') as f:
        quests = {row['quest_id'] for row in csv.DictReader(f)}
    with (ROOT / 'docs/production/World_Spawn_Gathering_Manifest_vi.csv').open(encoding='utf-8-sig', newline='') as f:
        entities = {part for row in csv.DictReader(f) for part in row['entity_id'].split('|')}
    ids = [q['questId'] for q in beats]
    if set(ids) != quests or len(ids) != len(set(ids)):
        errors.append('Quest beat coverage must equal the canonical dialogue quest set without duplicates')
    for quest in beats:
        for key in ('clue', 'dramaticQuestion', 'playerAgency', 'payoff', 'scope', 'newAnchorPolicy'):
            if not quest.get(key):
                errors.append(f"{quest['questId']}: missing {key}")
    seen_scenes, seen_shots = set(), set()
    for scene in scenes:
        sid = scene['sceneId']
        if sid in seen_scenes:
            errors.append(f'{sid}: duplicate scene')
        seen_scenes.add(sid)
        if scene['questId'] not in quests:
            errors.append(f'{sid}: unknown quest')
        for actor in scene['characters']:
            if actor not in entities:
                errors.append(f'{sid}: unknown actor {actor}')
        if scene['durationSeconds'] != sum(s['durationSeconds'] for s in scene['shots']):
            errors.append(f'{sid}: duration differs from shot sum')
        for key in ('triggerDescription', 'revealTier', 'purpose', 'fallback', 'serverAuthority'):
            if not scene.get(key):
                errors.append(f'{sid}: missing {key}')
        for shot in scene['shots']:
            if shot['shotId'] in seen_shots:
                errors.append(f"{shot['shotId']}: duplicate shot")
            seen_shots.add(shot['shotId'])
            if shot['durationSeconds'] != 6 or len(shot['prompt']) < 400:
                errors.append(f"{shot['shotId']}: incomplete prompt or invalid duration")
    if errors:
        print('\n'.join('ERROR: ' + e for e in errors))
        return 1
    print(f'PASS: {len(beats)}/{len(quests)} quest beats, {len(scenes)} scenes, '
          f'{len(seen_shots)} shots, {sum(s["durationSeconds"] for s in scenes)} seconds; '
          'quest/actor references and handoff fields valid. Video generation and runtime guards unverified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
