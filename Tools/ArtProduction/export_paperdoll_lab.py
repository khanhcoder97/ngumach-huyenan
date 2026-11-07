"""Export a read-only fit-lab catalogue; copy original PNG bytes, never resample/edit."""
import argparse, hashlib, json, math, shutil
from pathlib import Path
from inspect_actor_library import inspect

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / 'Art_Source/Modular_Characters_20261107'
RUN = ROOT / 'ClientGodot/assets/paperdoll_lab'
PREFIX = 'res://assets/paperdoll_lab/'
PARTS = [
    ('HAIR_CHESTNUT', 'Tóc ngắn hạt dẻ', 'hair_front', 'head', 'HAIR'),
    ('HAIR_TOPKNOT', 'Tóc búi huyền', 'hair_front', 'head', 'HAIR'),
    ('EYES_JADE', 'Mắt ngọc', 'eyes', 'face', 'EYES'),
    ('EYES_AMBER', 'Mắt hổ phách', 'eyes', 'face', 'EYES'),
    ('CHEST_IVORY', 'Áo giao lĩnh ngà', 'chest_front', 'chest', 'OUTFIT'),
    ('CHEST_INDIGO', 'Áo giao lĩnh chàm', 'chest_front', 'chest', 'OUTFIT'),
    ('LEGS_IVORY', 'Quần ngà', 'legs', 'hip', 'OUTFIT'),
    ('LEGS_INDIGO', 'Quần chàm', 'legs', 'hip', 'OUTFIT'),
    ('BOOTS_BROWN', 'Hài nâu', 'boots', 'ground', 'OUTFIT'),
    ('BOOTS_SILVER', 'Hài viền bạc', 'boots', 'ground', 'OUTFIT'),
    ('JIAN_STEEL', 'Kiếm thép', 'weapon_near', 'hand_near', 'WEAPON'),
    ('JIAN_JADE', 'Kiếm ngọc', 'weapon_near', 'hand_near', 'WEAPON'),
    ('HAT_CIRCLET', 'Trán quan ngọc', 'hat_front', 'head', 'HAT'),
    ('HAT_TRAVELLER', 'Nón hành lữ', 'hat_front', 'head', 'HAT'),
    ('CAPE_JADE', 'Choàng ngọc', 'cape_back', 'chest', 'CAPE'),
    ('CAPE_INDIGO', 'Choàng chàm', 'cape_back', 'chest', 'CAPE'),
]
ORDER = ['cape_back', 'body', 'legs', 'boots', 'chest_front', 'eyes', 'hair_front', 'hat_front', 'weapon_near']
def sha(data):
    return hashlib.sha256(data).hexdigest()
def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
def save(path, data, check):
    rendered = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
    if check:
        assert path.read_text(encoding='utf8') == rendered, 'stale lab metadata: ' + str(path)
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding='utf8')
def source_rect(frame):
    x, y, _, _ = frame['rect']; l, t, r, b = frame['bounds']
    return [x+l, y+t, r-l, b-t]
def copy_source(relative, name, check):
    source = ART / relative; target = RUN / name
    if check:
        assert target.read_bytes() == source.read_bytes(), 'lab PNG differs from original: ' + name
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return dict(file=PREFIX+name, sha256=sha(source.read_bytes()))

def main(check=False):
    bodies = []
    report = json.loads((ART/'structure_report.json').read_text(encoding='utf8'))
    sources = []
    for sex in ['male', 'female']:
        page = next(p for p in report['pages'] if p['id'] == 'body_human_'+sex+'_idle_s_v1')
        # Reinspect bytes, not merely trust a potentially stale previous report.
        actual = inspect(dict(id=page['id'], source=page['source'], columns=4, rows=4, direction='S'), ART)
        assert actual['sha256'] == page['sha256']
        texture = copy_source(page['source'], sex+'_idle_s.png', check); sources.append(texture)
        frames = []
        for f in actual['directions'][0]['frames']:
            region = source_rect(f); l,t,_,_ = f['bounds']; px,py = f['pivot']
            # Seed only: all poses share one fixed source calibration, never fit each part to alpha height.
            offset = [48-round((px-l)/6), 72-math.ceil((py-t)/6)]
            top = offset[1]; head = [48, top+1]
            anchors = dict(ground=[48,72], head=head, face=[48,top+10],
                           chest=[48,top+16], hip=[48,top+26], hand_near=[57,top+23])
            guide = dict(region=region, offset=offset, anchors=anchors, paintOrder=ORDER)
            frames.append(dict(**guide, fingerprint=sha(canonical(dict(sourceSha256=texture['sha256'], **guide)))))
        bodies.append(dict(id='MK_'+('M' if sex=='male' else 'F'), name='Minh Kiếm · '+('Nam' if sex=='male' else 'Nữ'),
                           rigId='RIG_HUMAN_'+('M' if sex=='male' else 'F')+'_V1', texture=texture['file'],
                           sourcePixelsPerUnit=6, frames=frames))
    record = dict(id='mk_s_parts_v1', source='Wardrobe_Study/mk_s_parts_v1.png', columns=4, rows=4, direction='S')
    wardrobe = inspect(record, ART)
    texture = copy_source(record['source'], 'mk_s_parts_v1.png', check); sources.append(texture)
    parts = []
    for spec, frame in zip(PARTS, wardrobe['directions'][0]['frames'], strict=True):
        id_, name, slot, anchor, category = spec
        region = source_rect(frame); width, height = region[2]/12, region[3]/12
        offset = [-round(width/2), 0]
        if slot == 'hair_front': offset[1] = -5 if id_ == 'HAIR_TOPKNOT' else -1
        elif slot == 'hat_front': offset[1] = -3
        elif slot == 'boots': offset[1] = -math.ceil(height)
        elif slot == 'legs': offset[1] = -3
        elif slot == 'weapon_near': offset = [-3,-7]
        elif slot == 'cape_back': offset[1] = -2
        parts.append(dict(id=id_, name=name, slot=slot, anchor=anchor, category=category, region=region,
                          offset=offset, texture=texture['file'], sourcePixelsPerUnit=12,
                          hides=['hair_front'] if id_=='HAT_TRAVELLER' else [],
                          uniqueSourceImages=1, approved=False,
                          note='Static isolated SOUTH part; sixteen placement bindings are not sixteen authored garment poses.'))
    catalogue = dict(schemaVersion=1, scope='FIT_LAB_ONLY', productionApproved=False, canvas=[96,96], origin=[48,72],
                     direction='S', clip='idle', seconds=1.2, frameCount=16, sources=sources, bodies=bodies, parts=parts,
                     limitations=['Initial body guides are unapproved seeds; inspect every pose.',
                                  'Sources are not native pixel masters; explicit atlas-wide review calibration only.',
                                  'No walk, attack, skill, eight-direction art, under-hat variant or split arm skin passes.',
                                  'Tunic/cape reuse is a static fitting study, not accepted deformable animation.',
                                  'No create-character, equipment mutation, ownership or online persistence.'])
    catalogue['catalogueFingerprint'] = sha(canonical(catalogue))
    save(RUN/'catalog.json', catalogue, check)
    save(ART/'Wardrobe_Study/inspection.json', dict(sourceSha256=texture['sha256'], imageSize=wardrobe['imageSize'],
         parts=16, uniqueSourceImages=16, productionApproved=False, sourcePixelsPerUnit=12,
         note='Original generated bytes retained. Cells are isolated parts, not animation frames.'), check)
    print(json.dumps(dict(scope=catalogue['scope'], bodies=2, candidateBodyCells=32, staticParts=16,
                          approvedNativeClips=0, productionApproved=False)))
if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true')
    main(parser.parse_args().check)
