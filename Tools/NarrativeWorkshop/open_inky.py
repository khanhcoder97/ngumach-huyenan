"""Open the authored Ink project in a portable Inky editor when explicitly invoked."""
import argparse,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--editor',type=Path);a=p.parse_args()
choices=[a.editor,ROOT.parent/'NGUMACHHUYENAN-tools/narrative/inky/0.15.2/Inky.exe',Path.home()/'.cache/ngumach-narrative/inky/0.15.2/Inky.exe']
editor=next((p for p in choices if p and p.is_file()),None)
if editor is None:raise SystemExit('Run setup_tools.py --editor or provide --editor /path/to/Inky.exe')
subprocess.Popen([str(editor),str(ROOT/'docs/narrative/workshop/ink/main.ink')])
