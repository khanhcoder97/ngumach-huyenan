import argparse,json,os,re,socket,subprocess,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--godot',required=True);p.add_argument('--project',required=True)
p.add_argument('--dotnet-root',required=True);p.add_argument('--server-dotnet',required=True)
p.add_argument('--server-dll',required=True);p.add_argument('--server-cwd',required=True);p.add_argument('--output',required=True)
p.add_argument('--only',choices=['both','online'],default='both')
a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env['DOTNET_ROOT']=a.dotnet_root;env['DOTNET_ROLL_FORWARD']='LatestMajor'
env['PATH']=a.dotnet_root+os.pathsep+env.get('PATH','')
# The unmodified Muse tests hard-code :5000. Refuse to touch any existing listener.
s=socket.socket();s.bind(('127.0.0.1',5000));s.close()
env['ASPNETCORE_URLS']='http://127.0.0.1:5000'
results=[]
with (out/'server.log').open('w',encoding='utf-8') as f:
 server=subprocess.Popen([a.server_dotnet,a.server_dll,'--urls',env['ASPNETCORE_URLS']],cwd=a.server_cwd,env=env,stdout=f,stderr=subprocess.STDOUT)
 try:
  ready=False
  for _ in range(90):
   if server.poll() is not None:break
   try:
    with urllib.request.urlopen(env['ASPNETCORE_URLS']+'/health',timeout=1) as r:ready=r.status==200
   except OSError:pass
   if ready:break
   time.sleep(0.5)
  if not ready:raise RuntimeError('Owned review server failed health check')
  suites=[('NETTEST','NetTest.tscn','--nettest'),('ONLINETEST','OnlineTest.tscn','--onlinetest')]
  if a.only=='online':suites=suites[1:]
  for name,scene,flag in suites:
   cmd=[a.godot,'--headless','--path',a.project,scene,'--',flag]
   log=out/(name.lower()+'.log');start=time.monotonic();timed=False
   with log.open('w',encoding='utf-8') as capture:
    child=subprocess.Popen(cmd,env=env,stdout=capture,stderr=subprocess.STDOUT)
    try:rc=child.wait(timeout=120)
    except subprocess.TimeoutExpired:timed=True;child.kill();rc=child.wait(timeout=10)
   txt=log.read_text(encoding='utf-8',errors='replace')
   markers=re.findall(r'^'+name+r' RESULT: (PASS|FAIL).*$',txt,re.M)
   row={'suite':name,'exit':rc,'timeout':timed,'pass':rc==0 and not timed and markers==['PASS'],
        'seconds':round(time.monotonic()-start,2),'markers':markers,'log':str(log),'server_pid':server.pid}
   results.append(row);print(json.dumps(row),flush=True)
   (out/'online-results.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
 finally:
  if server.poll() is None:
   server.terminate()
   try:server.wait(timeout=10)
   except subprocess.TimeoutExpired:server.kill();server.wait(timeout=10)
raise SystemExit(0 if results and all(r['pass'] for r in results) else 1)
