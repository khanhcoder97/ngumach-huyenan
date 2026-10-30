"""Install pinned portable Ink tools outside the repository; no admin or Unity needed."""
import argparse,hashlib,json,platform,urllib.request,zipfile
from pathlib import Path
COMPILERS={'Windows':('inklecate_windows.zip','96bc130f57d134faf3d52019f36ce0879ea015fa7e84d280ccc1a9c8d376843f'),'Linux':('inklecate_linux.zip','1997ff5bca618c90003ecd5fecb286e7468abb955005a2a185042949642f8fb5'),'Darwin':('inklecate_mac.zip','200aae0b4471b38142465559a0640baf143e87fc9a236c68d08e1adde48053cf')}
def install(base,repo,version,asset,expected):
 folder=base/repo/version;folder.mkdir(parents=True,exist_ok=True);archive=folder/asset
 if not archive.is_file():
  request=urllib.request.Request(f'https://github.com/inkle/{repo}/releases/download/{version}/{asset}',headers={'User-Agent':'Ngumach-Narrative-Workshop'})
  with urllib.request.urlopen(request,timeout=60) as response:archive.write_bytes(response.read())
 actual=hashlib.sha256(archive.read_bytes()).hexdigest()
 if actual!=expected:raise ValueError('Release SHA256 mismatch: '+asset)
 with zipfile.ZipFile(archive) as package:
  if any(not (folder/m.filename).resolve().is_relative_to(folder.resolve()) for m in package.infolist()):raise ValueError('Archive path escape')
  if not (folder/'verified-release.json').exists():package.extractall(folder)
 if platform.system()!='Windows':
  for executable in folder.rglob('inklecate'):
   if executable.is_file():executable.chmod(executable.stat().st_mode|0o111)
 (folder/'verified-release.json').write_text(json.dumps({'repo':'inkle/'+repo,'tag':version,'asset':asset,'sha256':actual},indent=2)+'\n',encoding='utf8')
 print('VERIFIED',folder)
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dir',type=Path,default=Path.home()/'.cache/ngumach-narrative');p.add_argument('--editor',action='store_true');a=p.parse_args()
 system=platform.system()
 if system not in COMPILERS:p.error('Unsupported OS; use npm build instead')
 asset,sha=COMPILERS[system];install(a.dir,'ink','v1.2.1',asset,sha)
 if a.editor:
  if system!='Windows':p.error('Pinned editor package is Windows x64; compiler is available above')
  install(a.dir,'inky','0.15.2','Inky_windows_64.zip','c6cf8cf567d63ff322e8a41dfda453200b02d94403ef403cbd43778147f8411c')
