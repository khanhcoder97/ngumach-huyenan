"""Register original Khoa Mach atlases in editable, isolated Studio projects."""
import shutil
from statistics import median

from PIL import Image

from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118a'
OUTPUT = ROOT / 'Implementation/Reports/Evidence/Actor_Batch_20261118a'
REVIEWED_STANCE_SOURCES = {
    '1debff8d9292b9eb0f88e7e1054bbe6e02a802f1f530cb9ea1c099859ec2b2d3': None,  # E v1
    '9f4709597dc78c9f219789661da2cee7aec453e0141c0d093703d7036f031f70': None,  # S v2
    '8ed97d099f2e38d5ae92eefd6b82d224cda73244eafa0bf66c43fb49a28d3929': None,  # N v2
    'aff3783df8358db77376587d2bd40b3b52d1db9ab3997631a1d84dc0d6f8f717': None,  # NE v2
    '1cc140e0bc6e47971639980e3b87272fcb979b0e6b62ab1576648448546a3d33': None,  # W v1
    '8d04b0f69645a493a182672e17439b790699629c4fd70fccf3d4f57f88cf593a': None,  # SW v2
    'f0787066a4312317ef226410a045a034a554829af9089b9f33476f653aa85b06': None,  # NW v2
    # SE v2: the low arrowhead reaches the boot line outside this X window.
    'fa95e7758df232b5ba3f7a70ef030faf9fa99d8b4951458d8e14649001b786d4': (80, 200),
}


def approximate_stance(record, frames, path):
    """Review first with a narrow sole envelope anchored to the lowest boot."""
    boot_window = REVIEWED_STANCE_SOURCES[record['sourceSha256']]
    pivots = []
    with Image.open(path) as atlas:
        alpha = atlas.getchannel('A').point(lambda value: 255 if value >= 200 else 0)
        for frame in frames:
            x, y, width, _ = frame['rect']
            left, right = boot_window or (0, width)
            bottom = frame['bounds'][3]
            floor = alpha.crop((x + left, y + bottom - 18, x + right, y + bottom)).getbbox()
            assert floor
            bottom += floor[3] - 18
            soles = alpha.crop((x + left, y + bottom - 12, x + right, y + bottom)).getbbox()
            assert soles
            pivots.append([left + (soles[0] + soles[2]) / 2, bottom])
    return pivots


def projectile_tip_pivots(frames, path):
    """Track the pale arrowhead's axis separately from the leaf outline."""
    pivots = []
    with Image.open(path) as atlas:
        for frame in frames:
            x, y, width, height = frame['rect']
            right = frame['bounds'][2]
            tip = atlas.crop((x + right - 24, y, x + right, y + height))
            bright = [i // 24 for i, (r, g, b, a) in enumerate(tip.get_flattened_data())
                      if a >= 160 and min(r, g, b) >= 140 and g >= r]
            assert bright, 'Arrowhead highlight is missing'
            pivots.append([min(width - 1, right - 1), median(bright)])
    return pivots


def prepare():
    manifest = read(ART / f'Candidates_{BATCH}/candidate_manifest.json')
    plan = []
    held = []
    for source_record in manifest['records']:
        record = dict(source_record)
        identifier = record['id']
        source = ART / record['source']
        source_sha = sha(source)
        assert source_sha == record['sourceSha256']
        if record.get('direction') and source_sha not in REVIEWED_STANCE_SOURCES:
            held.append(dict(id=identifier, sourceSha256=source_sha,
                             reason='SOURCE_FACING_OR_STANCE_REVIEW_REQUIRED'))
            continue
        if identifier == 'sk_lc_01_leaf_dissipate_component':
            assert source_sha == 'ba3f1c6d9ffdb81c4e8c0490dcaccb26d7e0136aff7d886eeb3b80774e51b97b'
            # The final fading fleck has sixteen alpha>=64 pixels and
            # no alpha>=200 pixels. Keep the established visible-tail rule.
            record['translucentTailFromFrame'] = 15
        raw_frames = inspect(record)['directions'][0]['frames']
        assert len(raw_frames) == 16
        if record.get('direction'):
            height = raw_frames[0]['bounds'][3] - raw_frames[0]['bounds'][1]
            record.update(pivotMode='SOURCE_FOOT_PIVOTS', bodyReferenceHeight=height,
                          sourceFootPivots=approximate_stance(record, raw_frames, source))
        else:
            height = max(max(f['bounds'][2] - f['bounds'][0], f['bounds'][3] - f['bounds'][1])
                         for f in raw_frames)
            if identifier == 'sk_lc_01_projectile_component':
                assert source_sha == 'd072a37c3503ae6a0af7e24f9642a2c6e8e8a717fd8d91ada12ac69e784bc852'
                record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=projectile_tip_pivots(raw_frames, source))
            elif identifier == 'sk_lc_01_leaf_dissipate_component':
                record.update(pivotMode='SOURCE_PIVOTS', sourcePivots=[
                    [226,160], [225,160], [227,159], [228,159],
                    [226,158], [226,158], [227,158], [227,158],
                    [226,160], [225,160], [225,160], [225,160],
                    [223,160], [222,160], [222,160], [222,160],
                ])
        page = inspect(record)
        assert page['sha256'] == source_sha
        frames = page['directions'][0]['frames']
        bundle = OUTPUT / 'Candidate_Studio' / identifier
        textures = bundle / 'textures'
        textures.mkdir(parents=True, exist_ok=True)
        texture = textures / (source_sha + '.png')
        if not texture.exists():
            shutil.copyfile(source, texture)
        assert sha(texture) == source_sha
        scale = 140 / height
        poses = [dict(X=0, Y=0, PivotX=frame['pivot'][0], PivotY=frame['pivot'][1],
                      ScaleX=scale, ScaleY=scale, Alpha=1, Angle=0, SourceFrame=i)
                 for i, frame in enumerate(frames)]
        layer = dict(Id='source', Kind='sprite', Name=identifier, Visible=True, Z=0,
                     Texture='textures/' + texture.name, Regions=[frame['rect'] for frame in frames],
                     Rest=poses[0])
        track = dict(LayerId=layer['Id'], Interpolate=False,
                     Keys=[dict(Frame=index, Pose=pose) for index, pose in enumerate(poses)])
        loop = record.get('previewLoop', False)
        clip = dict(Name=identifier, Direction=record.get('direction', 'OMNI'), Loop=loop,
                    DurationsMs=record['sourceFrameDurationsMs'], Tracks=[track], Markers=[],
                    SourceNote='Original 16-pose Khoa Mach source preview. The bow, quiver and apparel are baked into the body.')
        project = dict(SchemaVersion=1, Scope='PRESENTATION_AUTHORING_ONLY',
                       Name=identifier, ProductionApproved=False, Layers=[layer], Sockets=[], Clips=[clip])
        project_path = bundle / 'project.json'
        if project_path.exists():
            assert read(project_path) == project, 'Preserve the edited project and register the next revision separately'
        else:
            save(project_path, project)
        save(bundle / 'source_registration.json', dict(record=record, page=page, productionApproved=False))
        plan.append(dict(id=identifier, project=project_path.relative_to(ROOT).as_posix(),
                         source=source.relative_to(ROOT).as_posix(), sourceSha256=source_sha,
                         timing=record['sourceFrameDurationsMs'], loop=loop))
    save(OUTPUT / 'candidate_review_plan.json',
         dict(batch=BATCH, selected=len(plan), expected=manifest['expectedSourcePages'],
              catalogueUnchanged=True, entries=plan, held=held))
    print(f'Registered {len(plan)} Khoa Mach Studio projects.')


if __name__ == '__main__':
    prepare()
