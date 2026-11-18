"""Package reviewed Linh Cung skill sources for local Bến Mưa practice."""
import argparse
import json
import shutil

from build_linh_cung_khoa_mach_preview import ARROW, MARK, TAIL, TARGET, FACING_LAYOUTS
from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_linh_cung_day_gai import BODY as TRAP_BODY, EFFECTS as TRAP_EFFECTS, OUTPUT as TRAP_OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, sha

CLIENT = ROOT / 'ClientGodot/assets'
RUNTIME = CLIENT / 'linh_cung_practice'
FACINGS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')


def export(check):
    review = read(OUTPUT / 'manual_facing_review.json')
    assert review['nativeAuditSha256'] == sha(OUTPUT / 'native_audit.current.json')
    audit = read(OUTPUT / 'native_audit.current.json')
    trap_review = read(TRAP_OUTPUT / 'manual_review.json')
    trap_audit_path = TRAP_OUTPUT / 'native_audit.json'
    assert trap_review['nativeAuditSha256'] == sha(trap_audit_path)
    trap_audit = read(trap_audit_path)
    reviewed = {item['id']: item['sourceSha256'] for item in audit['sourceViews'] + trap_audit['sourceViews']}
    manifest = dict(clips={}, effects={}, sources={})

    def package(identifier, record):
        source = ART / record['source']
        digest = sha(source)
        name = identifier + '.png'
        target = RUNTIME / name
        if not check and (not target.is_file() or sha(target) != digest):
            shutil.copyfile(source, target)
        assert sha(target) == digest, identifier
        manifest['sources'][name] = dict(source=record['source'], sha256=digest)
        return name

    def format_clip(direction, file, seconds):
        return dict(duration=seconds, sourceHeight=direction['referenceHeight'],
                    frames=[dict(file=frame.get('file', file), rect=frame['rect'], pivot=frame['pivot'],
                                 flip=direction['flip']) for frame in direction['frames']])

    def icon_rect(frame):
        x, y, _, _ = frame['rect']
        left, top, right, bottom = frame['bounds']
        return [x + left, y + top, right - left, bottom - top]

    atlas = read(CLIENT / 'actor_library_v1/pages.json')
    pages = {page['id']: page for page in atlas['pages']}
    if not check:
        RUNTIME.mkdir(exist_ok=True)
    for action, catalogue_clip, duration in (
        ('idle', 'idle', 1.0), ('walk', 'walk', .8), ('attack', 'basic_attack', .6),
    ):
        page = pages['class_linh_cung_' + catalogue_clip]
        file = 'res://assets/actor_library_v1/' + page['file']
        assert sha(CLIENT / 'actor_library_v1' / page['file']) == page['sha256']
        directions = {direction['direction']: dict(direction, referenceHeight=direction.get('referenceHeight', page['referenceHeight']))
                      for direction in page['directions']}
        manifest['clips'][action] = [
            format_clip(directions[facing], file, duration) for facing in FACINGS
        ]

    def candidate(identifier, source_batch=OUTPUT):
        data = read(source_batch / 'Candidate_Studio' / identifier / 'source_registration.json')
        record, page = data['record'], data['page']
        assert reviewed[identifier] == page['sha256'] == sha(ART / record['source'])
        direction, = page['directions']
        assert not direction['flip'] and len(direction['frames']) == 16
        return record, direction

    cast = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_01_' + facing.lower()
        record, direction = candidate(identifier)
        assert direction['direction'] == facing and record['sourceFrameDurationsMs'] == [60] * 16
        release_frame = FACING_LAYOUTS[facing][4] if facing != 'E' else 8
        draw = direction['frames'][release_frame - 1]
        tip = FACING_LAYOUTS[facing][1] if facing != 'E' else (draw['bounds'][2] - 1, 176.5)
        muzzle = [(tip[axis] - draw['pivot'][axis]) / direction['referenceHeight'] for axis in (0, 1)]
        cast.append(dict(format_clip(direction, package(identifier, record), .96),
                         release=release_frame * .06, releaseOffset=muzzle))
    manifest['clips']['cast'] = cast
    for label, identifier, duration in (('arrow', ARROW, .32), ('tail', TAIL, .4)):
        record, direction = candidate(identifier)
        manifest['effects'][label] = format_clip(direction, package(identifier, record), duration)
        if label == 'arrow':
            manifest['effects'][label]['iconRect'] = icon_rect(direction['frames'][0])

    trap_cast = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_02_' + facing.lower()
        record, direction = candidate(identifier, TRAP_OUTPUT)
        assert direction['direction'] == facing and record['sourceFrameDurationsMs'] == [70] * 16
        _, _, _, hand, release_index, _ = TRAP_BODY[facing]
        pivot = direction['frames'][release_index]['pivot']
        offset = [(point - root) / direction['referenceHeight'] for point, root in zip(hand, pivot)]
        trap_cast.append(dict(format_clip(direction, package(identifier, record), 1.12),
                              release=release_index * .07, releaseOffset=offset))
    manifest['clips']['trap'] = trap_cast
    for role, identifier, width_frame in zip(('seed', 'grow', 'armed', 'retract'), TRAP_EFFECTS, (15, 15, 0, 0)):
        record, direction = candidate(identifier, TRAP_OUTPUT)
        timing = record['sourceFrameDurationsMs']
        assert len(set(timing)) == 1
        effect = format_clip(direction, package(identifier, record), sum(timing) / 1000)
        left, _, right, _ = direction['frames'][width_frame]['bounds']
        effect['sourceHeight'] = right - left  # Reference width for ground effects.
        if role == 'seed':
            first = direction['frames'][0]
            left, top, right, _ = first['bounds']
            x, y = first['pivot']
            effect['releaseOffset'] = [(left + right) / 2 - x, top + 22 - y]
        if role == 'armed':
            effect['iconRect'] = icon_rect(direction['frames'][0])
        manifest['effects']['trap_' + role] = effect
    records = {record['id']: record for record in read(ART / 'generation_records.json')}
    approvals = {record['id']: record['sourceSha256'] for record in read(ART / 'visual_review.json')['sourceApprovals']}
    for label, identifier, duration in (('mark', MARK, .96), ('dummy', TARGET, 1.6),
                                        ('patrol', 'mob_waterroot_walk_e', .8)):
        record = records[identifier]
        file = 'res://assets/actor_library_v1/' + pages[identifier]['file']
        assert sha(ART / record['source']) == approvals[identifier] == sha(CLIENT / 'actor_library_v1' / pages[identifier]['file'])
        direction, = inspect(record)['directions']
        if label == 'mark':
            for frame in direction['frames']:
                left, top, right, bottom = frame['bounds']
                frame['pivot'] = [(left + right) / 2, (top + bottom) / 2]
        manifest['effects'][label] = format_clip(direction, file, duration)

    document = json.dumps(manifest, ensure_ascii=False, indent=2) + '\n'
    output = RUNTIME / 'manifest.json'
    if check:
        assert output.read_text(encoding='utf-8') == document, 'Practice pack is out of date'
    else:
        output.write_text(document, encoding='utf-8', newline='\n')
    print('Linh Cung practice: two skills, eight authored facings each, six skill effects and two reused effects.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    export(parser.parse_args().check)
