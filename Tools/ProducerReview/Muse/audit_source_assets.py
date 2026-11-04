import argparse, hashlib, json, re, struct, subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('checkout')
p.add_argument('output')
a = p.parse_args()
root = Path(a.checkout).resolve()
proj = root / 'ClientGodot'
report = {'head': subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(),
          'pngs': [], 'unhydrated': [], 'scene_missing_references': [], 'sprite_table_mismatch': []}
tracked=set(subprocess.check_output(['git','-C',str(root),'ls-files','ClientGodot'],text=True).splitlines())
actions = {'idle':4,'walk':6,'run':6,'hurt':2,'death':4,'dodge':4,'attack1':5,
           'attack2':5,'attack3':5,'skill1':6,'skill2':6,'skill3':6,'jump':4,'fall':4,'land':4,'interact':4}
for path in sorted(proj.rglob('*.png')):
    b = path.read_bytes()
    rel = path.relative_to(root).as_posix()
    if rel not in tracked:continue
    if b.startswith(b'version https://git-lfs.github.com/spec/v1'):
        report['unhydrated'].append(rel)
        continue
    if not b.startswith(b'\x89PNG\r\n\x1a\n'):
        report.setdefault('invalid_png',[]).append(rel)
        continue
    w,h = struct.unpack('>II', b[16:24])
    row = {'path':rel,'width':w,'height':h,'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
    report['pngs'].append(row)
    if '/assets/chars/' in '/' + rel and path.stem in actions:
        row['runtime_cell'] = [48,64]
        row['expected_size_by_runtime'] = [48*actions[path.stem],64*8]
        if [w,h] != row['expected_size_by_runtime']:
            report['sprite_table_mismatch'].append(row)
for path in sorted(proj.rglob('*.tscn')):
    txt = path.read_text(encoding='utf-8-sig')
    for ref in set(re.findall(r'"res://([^"\r\n]+)"',txt)):
        if not (proj/ref).is_file():
            report['scene_missing_references'].append({'scene':path.relative_to(root).as_posix(),'ref':ref})
tile = json.loads((proj/'assets/tilemap/full_map/tilemap.json').read_text())
report['tilemap'] = {'cols':tile['cols'],'rows':tile['rows'],'blocked':len(tile['blocked']),
                     'blocked_unique':len(set(map(tuple,tile['blocked']))),'originWU':tile['originWU'],'cellWU':tile['cellWU']}
e = json.loads((proj/'docs/evidence_water_block_20261104/water_block_evidence_pack_20261104.json').read_text())
wc=e['water_cells']['cells']
report['water_evidence']={'count':len(wc),'unique':len({(x['global_col'],x['global_row']) for x in wc}),
    'invalid_layers':sum(x['ground'] is not None or x['path'] is not None or x['blocked_before'] != 0 or x['blocked_after'] != 1 for x in wc)}
out=Path(a.output)
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k != 'pngs'},ensure_ascii=False))
print('hydrated_png_count='+str(len(report['pngs'])))
print('png_bytes='+str(sum(x['bytes'] for x in report['pngs'])))
