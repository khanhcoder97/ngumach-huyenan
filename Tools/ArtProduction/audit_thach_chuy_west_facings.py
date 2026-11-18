"""Verify Thạch Chùy source coverage and the new western Studio captures."""
import argparse

from audit_linh_cung_day_gai import check_source
from build_thach_chuy_sanctuary_preview import ALL_FACINGS, FACINGS, WEST_BATCH, WEST_BUNDLE
from prepare_thach_chuy_candidates_20261116c import ART, EV, ROOT, read, save, sha


def audit(ffmpeg):
    output = WEST_BUNDLE.parent
    plan = read(output / 'candidate_review_plan.json')
    entries = {entry['id']: entry for entry in plan['entries']}
    sources = {facing: EV for facing in FACINGS}
    sources.update({facing: output for facing in ALL_FACINGS[len(FACINGS):]})
    captures = []
    coverage = []
    source_hashes = set()
    checked_ids = set()
    for skill in range(1, 7):
        for facing, evidence in sources.items():
            identifier = f'class_thach_chuy_skill_{skill:02d}_{facing.lower()}'
            bundle = evidence / 'Candidate_Studio' / identifier
            registration = read(bundle / 'source_registration.json')
            record = registration['record']
            page = registration['page']
            digest = record['sourceSha256']
            assert record['id'] == identifier and record['direction'] == facing
            assert digest not in source_hashes, identifier
            source_hashes.add(digest)
            assert digest == page['sha256'] == sha(ART / record['source'])
            assert page['sourceFrames'] == 16 and registration['originalPngUnchanged']
            project = read(bundle / 'project.json')
            assert len(project['Layers']) == len(project['Clips']) == 1
            clip = project['Clips'][0]
            assert clip['Direction'] == facing and clip['DurationsMs'] == record['sourceFrameDurationsMs']
            assert len(clip['DurationsMs']) == 16
            assert sha(bundle / project['Layers'][0]['Texture']) == digest
            keys = clip['Tracks'][0]['Keys']
            assert [key['Pose']['SourceFrame'] for key in keys] == list(range(16))
            frames = page['directions'][0]['frames']
            assert project['Layers'][0]['Regions'] == [frame['rect'] for frame in frames]
            for key, frame in zip(keys, frames):
                assert [key['Pose']['PivotX'], key['Pose']['PivotY']] == frame['pivot']
            coverage.append(dict(skill=skill, direction=facing, sourceSha256=digest,
                                 source=record['source'], project=(bundle / 'project.json').relative_to(ROOT).as_posix()))
            if evidence == output:
                captures.append(check_source(entries[identifier], ffmpeg, output))
                checked_ids.add(identifier)
    assert plan['batch'] == WEST_BATCH and plan['selected'] == plan['expected'] == len(entries) == 18
    assert set(entries) == checked_ids and not plan['pilot']
    assert len(coverage) == 48
    save(output / 'native_source_audit.json',
         dict(scope='THACH_CHUY_BODY_SOURCE_AND_WEST_NATIVE_STUDIO', previewFrameClock=60,
              skills=6, uniqueBodySheets=len(coverage), sourcePoses=16 * len(coverage),
              newSourcePoses=16 * len(captures), nativeCaptures=captures, coverage=coverage,
              productionApproved=False))
    print(f'Checked {len(coverage)} body sheets, {len(captures)} new native captures and '
          f'{sum(entry["decodedFrames"] for entry in captures)} new decoded frames.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ffmpeg', default='D:/Project/NGUMACHHUYENAN-tools/review-media/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe')
    audit(parser.parse_args().ffmpeg)
