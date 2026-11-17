"""Register original Khoa Mach atlases in editable, isolated Studio projects."""
import shutil
from statistics import median

from PIL import Image

from prepare_thach_chuy_candidates_20261116c import ART, ROOT, inspect, read, save, sha

BATCH = '20261118a'
OUTPUT = ROOT / 'Implementation/Reports/Evidence/Actor_Batch_20261118a'


def approximate_stance(record, frames, path):
    """Review first with a narrow sole envelope anchored to the lowest boot."""
    # The viewed E sheet keeps bow and quiver above the boot line. Other
    # facings need their own source review before using this registration.
    assert record['sourceSha256'] == '1debff8d9292b9eb0f88e7e1054bbe6e02a802f1f530cb9ea1c099859ec2b2d3'
    pivots = []
    with Image.open(path) as atlas:
        alpha = atlas.getchannel('A').point(lambda value: 255 if value >= 200 else 0)
        for frame in frames:
            x, y, width, _ = frame['rect']
            bottom = frame['bounds'][3]
            soles = alpha.crop((x, y + bottom - 12, x + width, y + bottom)).getbbox()
            assert soles
            pivots.append([(soles[0] + soles[2]) / 2, bottom])
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
    for source_record in manifest['records']:
        record = dict(source_record)
        identifier = record['id']
        source = ART / record['source']
        source_sha = sha(source)
        assert source_sha == record['sourceSha256']
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
              catalogueUnchanged=True, entries=plan))
    print(f'Registered {len(plan)} Khoa Mach Studio projects.')


if __name__ == '__main__':
    prepare()
