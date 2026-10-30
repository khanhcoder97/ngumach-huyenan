"""Exercise the actual browser reading room, then close only processes started here."""
import argparse,json,re,shutil,subprocess,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--screenshot',type=Path,required=True);p.add_argument('--report',type=Path);p.add_argument('--entry',choices=['ben-mua','thang-long'],default='ben-mua');a=p.parse_args()
 candidates=[Path('C:/Program Files/Google/Chrome/Application/chrome.exe'),Path('C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe')]
 browser=next((str(p) for p in candidates if p.is_file()),None) or shutil.which('google-chrome') or shutil.which('chromium')
 if not browser:raise SystemExit('Browser unavailable; no browser PASS may be claimed')
 a.screenshot.parent.mkdir(parents=True,exist_ok=True)
 server=subprocess.Popen([shutil.which('python') or 'python',str(ROOT/'server.py'),'--port','0'],stdout=subprocess.PIPE,text=True,encoding='utf8')
 try:
  line=server.stdout.readline().strip();url=line.split('=',1)[1]
  for route in ['/../.git/config','/%2e%2e/.git/config','/unknown']:
   try:urllib.request.urlopen(url+route,timeout=5);raise AssertionError('Unexpected route served')
   except urllib.error.HTTPError as e:assert e.code==404
  with tempfile.TemporaryDirectory(prefix='ngumach-reader-chrome-') as profile:
   command=[browser,'--headless=new','--no-sandbox','--disable-gpu','--disable-dev-shm-usage','--no-first-run','--no-default-browser-check',f'--user-data-dir={profile}','--window-size=1400,1050','--virtual-time-budget=7000','--dump-dom',f'--screenshot={a.screenshot.resolve()}',url+'/?smoke='+('thang-long' if a.entry=='thang-long' else '1')]
   r=subprocess.run(command,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=45)
   assert r.returncode==0,r.stderr[-1000:]
   assert 'data-reader-ready="true"' in r.stdout,'Reader did not load'
   assert 'data-browser-smoke="pass"' in r.stdout,'Actual branch button did not advance'
   assert a.screenshot.is_file() and a.screenshot.stat().st_size>10000,'Screenshot missing'
  result={'status':'PASS_BROWSER','sourceDigest':json.loads((ROOT/'scene_manifest.json').read_text(encoding='utf8'))['sourceDigest'],'load':'PASS','buttonAdvancesActualInkRuntime':'PASS','unknownAndTraversalRoutes404':'PASS','screenshot':str(a.screenshot.resolve()),'nativeGame':'UNVERIFIED'}
  if a.report:a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
  print(json.dumps(result,ensure_ascii=False,indent=2))
 finally:server.terminate();server.wait(timeout=10)
if __name__=='__main__':main()
