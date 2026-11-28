"""Export shared skill previews. Actor selection is independent of both timelines and atlases."""
import argparse
import shutil

from inspect_actor_library import RUN
from prepare_thach_chuy_candidates_20261116c import ART, EV, read, save, sha


def compact_document(components):
    document = read(ART / 'skill_assembly_profiles_v1.json')
    document.update(SchemaVersion=2, SourcePolicy='Three reusable body facings, eight world aim directions, independent OMNI effects.')
    document['Sources'].append('docs/production/Actor_Batch_20261119b_ThachChuy_Facings_vi.md')
    roles = {
        'SK_MK_01': 'BRACE', 'SK_MK_04': 'BRACE', 'SK_MK_05': 'STEP',
        'SK_AD_02': 'BRACE', 'SK_AD_05': 'STEP',
    }
    for profile in document['Profiles']:
        del profile['ActorId'], profile['BodyClip']
        profile['Motion'] = roles.get(profile['Id'], 'STRIKE')
        for variant in profile['Variants']:
            del variant['OverrideClip'], variant['OverrideStart']

    def track(skill, part, start, duration, size, *, name=None, anchor='CASTER', forward=0,
              side=0, elevation=0, rotation='SCREEN', angle=0, z=0, loop=False, optional=False):
        component = f'sk_tc_{skill:02d}_{part}_component'
        source_seconds = sum(components[component]['sourceFrameDurationsMs']) / 1000
        return dict(Id=name or part, ComponentId=component, Start=start, Duration=duration,
                    SourceSeconds=source_seconds, Anchor=anchor, Forward=forward, Side=side,
                    Elevation=elevation, Size=size, Rotation=rotation, Angle=angle, Z=z,
                    Loop=loop, LowFxOptional=optional)

    def variant(identifier, name, duration, tracks, *, dash=0, contact=None):
        result = dict(Id=identifier, Name=name, Duration=duration, Tracks=tracks)
        if dash:
            result.update(DashStart=.12, DashDuration=.26, DashDistance=dash)
        if contact is not None:
            result['MotionContact'] = contact
        return result

    def skill(number, name, motion, variants, target=110):
        document['Profiles'].append(dict(Id=f'SK_TC_{number:02d}', Name=name,
                                         Motion=motion, TargetDistance=target, Variants=variants))

    # The shared strike clip is 600 ms. Resolve the impacts after its windup.
    wedge = track(1, 'charge_wedge', 0, .25, 35, forward=30, rotation='FACING')
    crack = track(1, 'impact_crack', .25, .35, 46, anchor='TARGET')
    dust = track(1, 'dust_end', .50, .40, 36, anchor='TARGET', optional=True)
    skill(1, 'Trấn Sơn', 'STRIKE', [
        variant('hit', 'Nện trúng bia', 1.0, [wedge, crack, dust], contact=.25),
        variant('miss', 'Nện ngoài tầm', .8, [wedge], contact=.25),
    ], target=78)

    skill(2, 'Chấn Địa', 'STRIKE', [
        variant('pulse', 'Vòng bụi, sóng đá, lắng', 1.32, [
            track(2, 'pre_ring', 0, .35, 90),
            track(2, 'shockwave', .35, .48, 175),
            track(2, 'dust_end', .80, .40, 65, optional=True),
        ], contact=.35),
    ])

    def plates(part, start, duration, loop=False, optional=False):
        return [
            track(3, part, start, duration, 36, name=f'{part}_{label}',
                  side=side, elevation=height, z=depth, loop=loop, optional=optional)
            for label, side, height, depth in (('left', -31, -68, 2), ('right', 31, -68, 2), ('back', 0, -96, 0))
        ]

    armor = plates('plate_gain', .25, .48) + plates('plate_sustain', .73, 3.52, loop=True)
    skill(3, 'Thiết Bích', 'BRACE', [
        variant('expire', 'Giáp giữ đủ nhịp rồi tan', 4.7, armor + plates('plate_end', 4.25, .4)),
        variant('crack', 'Giáp rạn khi chịu đòn', 4.7, armor + plates('plate_crack_overlay', 1.12, .4, optional=True) + plates('plate_end', 4.25, .4)),
    ])

    pulse = track(4, 'caster_pulse', .22, .4, 155)
    skill(4, 'Khiêu Chiến', 'BRACE', [
        variant('accepted', 'Quái thường nhận dấu khiêu chiến', 2.5, [
            pulse, track(4, 'target_chevron', .34, .7, 24, anchor='TARGET_HP',
                         elevation=-117, rotation='FACING', angle=180, z=3),
            track(4, 'target_status', 1.04, 1.28, 22, anchor='TARGET_HP', elevation=-113, z=3),
        ]),
        variant('no_target', 'Hô tại chỗ', .74, [pulse]),
    ])

    trail = track(5, 'dash_trail', .12, .42, 95, forward=-24, rotation='FACING')
    stop = track(5, 'stop_dust', .38, .32, 42, anchor='END')
    skill(5, 'Phá Nham', 'STEP', [
        variant('hit', 'Lao trúng mục tiêu', .92, [
            trail, track(5, 'hit_impact', .38, .4, 62, anchor='END', forward=20), stop,
        ], dash=80),
        variant('blocked', 'Vật cản chặn đà', .82, [trail, stop], dash=34),
    ])

    zone = [
        track(6, 'zone_charge', 0, .64, 268),
        track(6, 'open_zone_sustain', .92, 3.20, 270, loop=True),
        track(6, 'zone_end', 4.12, .64, 270),
    ]
    # Screen-aligned stones keep the entrance at the front of the camera.
    for label, forward, side, elevation in (('back', 0, 0, -73), ('left', 0, -88, -47), ('right', 0, 88, -47)):
        rock = track(6, 'plate_gain', .56, .48, 38, name='plate_' + label,
                     forward=forward, elevation=elevation, optional=True)
        zone.append(dict(rock, ScreenX=side))
    skill(6, 'Sơn Thần Giáng Thế', 'BRACE', [
        variant('release', 'Vòng đá mở về phía người chơi', 5.12, zone),
    ])
    return document


def build(check):
    records = read(ART / 'Candidates_20261116c/candidate_manifest.json')['records']
    components = {}
    textures = RUN / 'assembly_components'
    if not check:
        textures.mkdir(exist_ok=True)
    for record in records:
        identifier = record['id']
        if not identifier.startswith('sk_tc_'):
            continue
        registration = read(EV / 'Candidate_Studio' / identifier / 'source_registration.json')
        page = registration['page']
        source = ART / record['source']
        assert page['sha256'] == record['sourceSha256'] == sha(source)
        assert registration['record']['id'] == identifier and not registration['productionApproved']
        assert page['sourceFrames'] == 16 and len(page['directions']) == 1
        target = textures / source.name
        if not check and (not target.exists() or sha(target) != page['sha256']):
            shutil.copyfile(source, target)
        assert sha(target) == page['sha256']
        components[identifier] = dict(page, file='assembly_components/' + target.name,
                                      sourceFrameDurationsMs=record['sourceFrameDurationsMs'],
                                      productionApproved=False, visualState='STUDIO_COMPONENT',
                                      visualNotes='Source candidate for skill assembly.')
    assert len(components) == 20
    document = compact_document(components)
    used_components = {track['ComponentId'] for profile in document['Profiles'] for variant in profile['Variants']
                       for track in variant['Tracks'] if track['ComponentId'].startswith('sk_tc_')}
    assert used_components == components.keys()
    outputs = {
        RUN / 'skill_assembly_components.json': dict(pages=list(components.values())),
        RUN / 'skill_assemblies_compact.json': document,
    }
    for path, data in outputs.items():
        if check:
            assert read(path) == data, f'Stale export: {path}'
        else:
            save(path, data)
    print(f'{len(document["Profiles"])} independent skill profiles, {len(components)} shared Thạch Chùy effect atlases')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    build(parser.parse_args().check)
