"""Verify original portrait provenance and byte-identical runtime copy; never edit pixels."""
import hashlib, json
from pathlib import Path
from PIL import Image
ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'Art_Source/MoonGlass_UI_20261105'
RUNTIME = ROOT / 'ClientGodot/assets/ui_moonglass'

def inspect():
    record = json.loads((SOURCE / 'source_inventory.json').read_text(encoding='utf-8'))
    source = SOURCE / record['source']
    runtime = RUNTIME / record['runtime']
    data = source.read_bytes()
    assert data == runtime.read_bytes(), 'Runtime portrait differs from authored source'
    assert hashlib.sha256(data).hexdigest() == record['sha256'], 'Portrait hash changed'
    assert (SOURCE / record['prompt']).is_file(), 'Missing source prompt'
    with Image.open(source) as im:
        assert list(im.size) == record['size'] and im.mode == 'RGBA'
        assert im.getchannel('A').getextrema() == (0, 255), 'Missing genuine transparency'
    print('MOONGLASS_ART PASS: one original RGBA portrait, prompt and byte-identical runtime copy')
    print('This checks provenance and structure, not visual quality or complete game functionality.')

if __name__ == '__main__':
    inspect()
