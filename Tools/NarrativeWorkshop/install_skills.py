"""Install only the pinned writing skills using Codex's bundled installer. Preserve existing skills."""
import hashlib,json,os,shutil,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
BASE=Path(os.environ.get('CODEX_HOME',Path.home()/'.codex'))
lock=json.loads(Path(__file__).with_name('sources.lock.json').read_text(encoding='utf8'))
installer=BASE/'skills/.system/skill-installer/scripts/install-skill-from-github.py'
if not installer.is_file():raise SystemExit('Codex bundled skill-installer missing; use pinned links in sources.lock.json manually')
for spec in lock['skills']:
 folder=BASE/'skills'/spec['name'];stamp=folder/'SOURCE.json'
 if folder.exists():
  if not stamp.is_file():raise SystemExit('Existing skill has no matching ownership stamp; preserved: '+str(folder))
  old=json.loads(stamp.read_text(encoding='utf8'))
  if any(old.get(k)!=spec[k] for k in ['repository','commit','path']):raise SystemExit('Existing skill version differs; preserved: '+str(folder))
  print('ALREADY INSTALLED',spec['name']);continue
 subprocess.run([sys.executable,str(installer),'--repo',spec['repository'],'--ref',spec['commit'],'--path',spec['path']],check=True)
 file=folder/'SKILL.md';text=file.read_text(encoding='utf8');raw=text.encode('utf8')
 if hashlib.sha256(raw).hexdigest()!=spec['upstreamSkillSha256']:raise SystemExit('Unexpected skill source bytes: '+spec['name'])
 refs=folder/'references';refs.mkdir(exist_ok=True);(refs/'upstream-SKILL.md').write_bytes(raw)
 file.write_text(text.replace('model-invocable: true\n',''),encoding='utf8',newline='\n');stamp.write_text(json.dumps(spec,indent=2)+'\n',encoding='utf8')
project=ROOT/'.agents/skills/ngumach-narrative/SKILL.md';folder=BASE/'skills/ngumach-narrative';folder.mkdir(exist_ok=True)
target=folder/'SKILL.md'
normalize=lambda text:text.replace('\r\n','\n').replace('\r','\n')
if target.exists() and normalize(target.read_text(encoding='utf8'))!=normalize(project.read_text(encoding='utf8')):raise SystemExit('Existing project skill differs; preserved: '+str(target))
target.write_text(normalize(project.read_text(encoding='utf8')),encoding='utf8',newline='\n')
print('Project skill ready. Skills are available on the next turn; no project bootstrap or global hooks installed.')
