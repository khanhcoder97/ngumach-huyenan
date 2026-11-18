"""Package reviewed Khóa Mạch sources for the local Bến Mưa practice encounter."""
import argparse
import json
import shutil

from build_linh_cung_khoa_mach_preview import ARROW, MARK, TAIL, TARGET, FACING_LAYOUTS
from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, sha

CLIENT = ROOT / 'ClientGodot/assets'
RUNTIME = CLIENT / 'linh_cung_practice'
FACINGS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')


def export(check):
    review = read(OUTPUT / 'manual_facing_review.json')
    assert review['nativeAuditSha256'] == sha(OUTPUT / 'native_audit.current.json')
    audit = read(OUTPUT / 'native_audit.current.json')
    reviewed = {item['id']: item['sourceSha256'] for item in audit['sourceViews']}
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

    def candidate(identifier):
        data = read(OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
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
                         release=release_frame * .06, muzzle=muzzle))
    manifest['clips']['cast'] = cast
    for label, identifier, duration in (('arrow', ARROW, .32), ('tail', TAIL, .4)):
        record, direction = candidate(identifier)
        manifest['effects'][label] = format_clip(direction, package(identifier, record), duration)
        if label == 'arrow':
            first = direction['frames'][0]
            x, y, _, _ = first['rect']
            left, top, right, bottom = first['bounds']
            manifest['effects'][label]['iconRect'] = [x + left, y + top, right - left, bottom - top]
    records = {record['id']: record for record in read(ART / 'generation_records.json')}
    approvals = {record['id']: record['sourceSha256'] for record in read(ART / 'visual_review.json')['sourceApprovals']}
    for label, identifier, duration in (('mark', MARK, .96), ('dummy', TARGET, 1.6)):
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
    print('Linh Cung practice: eight body directions, two new VFX and two reused effects.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    export(parser.parse_args().check)
