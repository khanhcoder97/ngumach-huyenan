"""Package reviewed Linh Cung skill sources for local Bến Mưa practice."""
import argparse
from itertools import accumulate
import json
import shutil

from prepare_linh_cung_bach_tien import (ARROW as RAIN_ARROW, CONTACT_POSE, FLECKS as RAIN_FLECKS,
                                        OUTPUT as RAIN_OUTPUT, RELEASE_POSE as RAIN_RELEASE_POSE, RING as RAIN_RING)

from build_linh_cung_khoa_mach_preview import ARROW, MARK, TAIL, TARGET, FACING_LAYOUTS
from prepare_linh_cung_khoa_mach_review import OUTPUT
from prepare_linh_cung_day_gai import BODY as TRAP_BODY, EFFECTS as TRAP_EFFECTS, OUTPUT as TRAP_OUTPUT
from prepare_linh_cung_lien_chau import (ARROW as VOLLEY_ARROW, NOCK as VOLLEY_NOCK,
                                       OUTPUT as VOLLEY_OUTPUT, RELEASE_MS, RELEASE_POSES, SOURCE_MS)
from prepare_linh_cung_phi_diep import (ARROW as RETREAT_ARROW, HEEL, LANDING_MS, OUTPUT as RETREAT_OUTPUT,
                                      RELEASE_MS as RETREAT_RELEASE_MS, RELEASE_POSE as RETREAT_RELEASE_POSE, START_MS)
from prepare_linh_cung_tan_hoa import (FALL, FAN, FALL_DELAY_MS, FULL_POSE, OUTPUT as FAN_OUTPUT,
                                     RELEASE_POSE as FAN_RELEASE_POSE)
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
    volley_review = read(VOLLEY_OUTPUT / 'manual_review.json')
    volley_audit_path = VOLLEY_OUTPUT / 'native_audit.json'
    assert volley_review['nativeAuditSha256'] == sha(volley_audit_path)
    volley_audit = read(volley_audit_path)
    assert set(volley_review['nativeAssemblyFacingsReviewed']) == set(FACINGS)
    fan_review = read(FAN_OUTPUT / 'manual_review.json')
    fan_audit_path = FAN_OUTPUT / 'native_audit.json'
    assert fan_review['nativeAuditSha256'] == sha(fan_audit_path)
    fan_audit = read(fan_audit_path)
    assert set(fan_review['nativeAssemblyFacingsReviewed']) == set(FACINGS)
    retreat_review = read(RETREAT_OUTPUT / 'manual_review.json')
    retreat_audit_path = RETREAT_OUTPUT / 'native_audit.json'
    assert retreat_review['nativeAuditSha256'] == sha(retreat_audit_path)
    retreat_audit = read(retreat_audit_path)
    assert set(retreat_review['nativeFullFacingsReviewed']) == set(FACINGS)
    rain_review = read(RAIN_OUTPUT / 'manual_review.json')
    rain_audit_path = RAIN_OUTPUT / 'native_audit.json'
    assert rain_review['nativeAuditSha256'] == sha(rain_audit_path)
    rain_audit = read(rain_audit_path)
    assert set(rain_review['nativeAssemblyFacingsReviewed']) == set(FACINGS)
    reports = (audit, trap_audit, volley_audit, fan_audit, retreat_audit, rain_audit)
    reviewed = {item['id']: item['sourceSha256'] for report in reports
                for item in report['sourceViews']}
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
    volley = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_03_' + facing.lower()
        record, direction = candidate(identifier, VOLLEY_OUTPUT)
        registration = read(VOLLEY_OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
        assert direction['direction'] == facing and record['sourceFrameDurationsMs'] == list(SOURCE_MS)
        grips = registration['releaseSourcePoints']
        assert len(grips) == len(RELEASE_POSES)
        releases = []
        for index, time, grip in zip(RELEASE_POSES, RELEASE_MS, grips):
            pivot = direction['frames'][index]['pivot']
            muzzle = [(point - root) / direction['referenceHeight'] for point, root in zip(grip, pivot)]
            releases.append(dict(time=time / 1000, offset=muzzle))
        volley.append(dict(format_clip(direction, package(identifier, record), sum(SOURCE_MS) / 1000),
                           frameEnds=[end / 1000 for end in accumulate(SOURCE_MS)], releases=releases))
    manifest['clips']['volley'] = volley
    for label, identifier in (('volley_arrow', VOLLEY_ARROW), ('volley_nock', VOLLEY_NOCK)):
        record, direction = candidate(identifier, VOLLEY_OUTPUT)
        effect = format_clip(direction, package(identifier, record), sum(record['sourceFrameDurationsMs']) / 1000)
        effect['iconRect'] = icon_rect(direction['frames'][0])
        effect['sourceHeight'] = effect['iconRect'][2]
        manifest['effects'][label] = effect

    retreat_cast = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_05_' + facing.lower()
        record, direction = candidate(identifier, RETREAT_OUTPUT)
        data = read(RETREAT_OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
        timing = record['sourceFrameDurationsMs']
        assert direction['direction'] == facing and data['releasePose'] == RETREAT_RELEASE_POSE
        assert sum(timing[:RETREAT_RELEASE_POSE]) == RETREAT_RELEASE_MS == START_MS + 120
        pivot = direction['frames'][RETREAT_RELEASE_POSE]['pivot']
        offset = [(point - root) / direction['referenceHeight'] for point, root in zip(data['releaseSourcePoint'], pivot)]
        retreat_cast.append(dict(format_clip(direction, package(identifier, record), sum(timing) / 1000),
                                 frameEnds=[end / 1000 for end in accumulate(timing)],
                                 release=RETREAT_RELEASE_MS / 1000, releaseOffset=offset))
    manifest['clips']['retreat'] = retreat_cast
    for label, identifier in (('retreat_arrow', RETREAT_ARROW), ('retreat_heel', HEEL)):
        record, direction = candidate(identifier, RETREAT_OUTPUT)
        timing = record['sourceFrameDurationsMs']
        effect = format_clip(direction, package(identifier, record), sum(timing) / 1000)
        effect['iconRect'] = icon_rect(direction['frames'][0])
        effect['sourceHeight'] = effect['iconRect'][2]
        if identifier == HEEL:
            effect.update(retreatStartsAt=START_MS / 1000, retreatEndsAt=LANDING_MS / 1000)
        manifest['effects'][label] = effect

    fan_cast = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_04_' + facing.lower()
        record, direction = candidate(identifier, FAN_OUTPUT)
        data = read(FAN_OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
        timing = record['sourceFrameDurationsMs']
        assert direction['direction'] == facing and data['releasePose'] == FAN_RELEASE_POSE
        pivot = direction['frames'][FAN_RELEASE_POSE]['pivot']
        offset = [(point - root) / direction['referenceHeight'] for point, root in zip(data['releaseSourcePoint'], pivot)]
        fan_cast.append(dict(format_clip(direction, package(identifier, record), sum(timing) / 1000),
                             frameEnds=[end / 1000 for end in accumulate(timing)],
                             release=sum(timing[:FAN_RELEASE_POSE]) / 1000, releaseOffset=offset))
    manifest['clips']['fan'] = fan_cast
    for label, identifier in (('fan_open', FAN), ('fan_fall', FALL)):
        record, direction = candidate(identifier, FAN_OUTPUT)
        timing = record['sourceFrameDurationsMs']
        effect = format_clip(direction, package(identifier, record), sum(timing) / 1000)
        if identifier == FAN:
            data = read(FAN_OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
            effect.update(sourceHeight=data['sourceReach'], ratioY=data['fanRatioY'],
                          angleCorrectionDegrees=data['sourceAngleCorrection'], sectorDegrees=data['measuredSectorDegrees'],
                          iconRect=icon_rect(direction['frames'][FULL_POSE]), fullAt=sum(timing[:FULL_POSE]) / 1000,
                          fallAt=FALL_DELAY_MS / 1000)
        manifest['effects'][label] = effect
    rain_cast = []
    for facing in FACINGS:
        identifier = 'class_linh_cung_skill_06_' + facing.lower()
        record, direction = candidate(identifier, RAIN_OUTPUT)
        timing = record['sourceFrameDurationsMs']
        assert direction['direction'] == facing
        rain_cast.append(dict(format_clip(direction, package(identifier, record), sum(timing) / 1000),
                              frameEnds=[end / 1000 for end in accumulate(timing)],
                              release=sum(timing[:RAIN_RELEASE_POSE]) / 1000))
    manifest['clips']['rain'] = rain_cast
    for label, identifier in (('rain_ring', RAIN_RING), ('rain_arrow', RAIN_ARROW), ('rain_impact', RAIN_FLECKS)):
        record, direction = candidate(identifier, RAIN_OUTPUT)
        timing = record['sourceFrameDurationsMs']
        effect = format_clip(direction, package(identifier, record), sum(timing) / 1000)
        if identifier == RAIN_RING:
            geometry = read(RAIN_OUTPUT / 'Candidate_Studio' / identifier / 'source_registration.json')
            effect.update(sourceHeight=geometry['sourceWidth'], ratioY=geometry['ratioY'],
                          iconRect=icon_rect(direction['frames'][0]))
        if identifier == RAIN_ARROW:
            effect['contactAt'] = sum(timing[:CONTACT_POSE]) / 1000
        manifest['effects'][label] = effect

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
    print('Linh Cung practice: six skills with eight authored facings each.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    export(parser.parse_args().check)
