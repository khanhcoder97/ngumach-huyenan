"""Register the photographed ground footprint of the four sanctuary sources."""
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha

SOURCE_PINS = {
    'open_zone_sustain': '6125b704a2886ac0714d81ec9a26e55aa70cd07a8443a786e5df4de3f3b31269',
    'zone_charge': '15c54b62a221620aadbe27c6c57c92d50615169ba980fd7178cc30827dc6296e',
    'zone_end': '4b01869dd87cfa65c3c77cb19c7add4895cbfbc01cac5c084ee3beec84a07757',
    'plate_gain': 'da9346bfec5561728c5d241ac19c46d089f1b0636f4da7265a8cd5dda55f9ec5',
}


def register():
    entries = []
    for part, source_sha in SOURCE_PINS.items():
        identifier = f'sk_tc_06_{part}_component'
        registration = read(EV / 'Candidate_Studio' / identifier / 'source_registration.json')
        record = registration['record']
        assert record['sourceSha256'] == sha(ART / record['source']) == source_sha
        frames = registration['page']['directions'][0]['frames']
        pivots = []
        for index, frame in enumerate(frames):
            left, top, right, bottom = frame['bounds']
            if part == 'open_zone_sustain':
                # The visible U omits its south arc. Its geometric origin is
                # slightly below the bounding-box centre of the visible art.
                pivot = [(left + right) / 2, top + 80]
            elif part == 'zone_charge':
                # Keep the centre of the projected horseshoe through the
                # first and last sparse footing phases.
                pivot = [[162,159,157,155][index % 4], [200,177,154,134][index // 4]]
            elif part == 'zone_end':
                # When stones disappear the remaining chips are asymmetric.
                # Retain the intact perimeter's origin within each row.
                pivot = [[162,160,158,155][index % 4], [212,189,169,149][index // 4]]
            else:
                pivot = [(left + right) / 2, bottom - 1]
            assert 0 < pivot[0] < frame['rect'][2]
            assert 0 < pivot[1] < frame['rect'][3]
            pivots.append(pivot)
        assert len(pivots) == 16
        fields = dict(pivotMode='SOURCE_PIVOTS', sourcePivots=pivots,
                      registrationMethod='SANCTUARY_GROUND_FOOTPRINT_VISUALLY_PROPOSED')
        entries.append(dict(id=identifier, sourceSha256=source_sha, fields=fields,
                            reviewNote='Use the projected open ring centre or the single plate baseline. The remaining dust and sparse marks retain the parent footprint. Confirm the phase seams in Studio.'))

    path = ART / 'registration_overrides_20261116c.json'
    overrides = read(path)
    updated = {entry['id'] for entry in entries}
    overrides['entries'] = [item for item in overrides['entries'] if item['id'] not in updated] + entries
    save(path, overrides)
    print(f'Registered {len(entries)} sanctuary ground-footprint proposals.')


if __name__ == '__main__':
    register()
