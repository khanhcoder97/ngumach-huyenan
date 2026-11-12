import argparse,json,os,re,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--godot',required=True)
p.add_argument('--project',required=True)
p.add_argument('--dotnet-root',required=True)
p.add_argument('--output',required=True)
p.add_argument('--stage',choices=['import','offline'],required=True)
a=p.parse_args(); out=Path(a.output); out.mkdir(parents=True,exist_ok=True)
env=os.environ.copy(); env['DOTNET_ROOT']=a.dotnet_root
env['PATH']=a.dotnet_root+os.pathsep+env.get('PATH','')
env['DOTNET_ROLL_FORWARD']='LatestMajor'
suites=[('SELFTEST',None,'--selftest'),('TILEMTEST','TilemapTest.tscn','--tilemtest'),
 ('FULLTEST','FullMapTest.tscn','--fulltest'),('HUDTEST','HudTest.tscn','--hudtest'),
 ('ANIMTEST','AnimTest.tscn','--animtest'),('DETAILTEST','DetailTest.tscn','--detailtest'),
 ('CLASSTEST','ClassTest.tscn','--classtest'),('SELECTTEST','OnlineTest.tscn','--selecttest')]
if a.stage=='import': suites=[('IMPORT',None,None)]
results=[]
for name,scene,flag in suites:
 cmd=[a.godot,'--headless','--path',a.project]
 if name=='IMPORT': cmd+=['--editor','--import']
 else:
  if scene:cmd+=[scene]
  cmd+=['--',flag]
 start=time.monotonic(); log=out/(name.lower()+'.log')
 timed=False; rc=None
 with log.open('w',encoding='utf-8') as f:
  child=subprocess.Popen(cmd,env=env,stdout=f,stderr=subprocess.STDOUT)
  try:rc=child.wait(timeout=240 if name=='IMPORT' else 100)
  except subprocess.TimeoutExpired:
   timed=True;child.kill();rc=child.wait(timeout=10)
 txt=log.read_text(encoding='utf-8',errors='replace')
 markers=re.findall(r'^'+re.escape(name)+r' RESULT: (PASS|FAIL).*$',txt,re.M)
 success=rc==0 and not timed and (name=='IMPORT' or markers==['PASS'])
 row={'suite':name,'command':cmd,'exit':rc,'timeout':timed,'seconds':round(time.monotonic()-start,2),
      'markers':markers,'pass':success,'runtime_errors':len(re.findall(r'^(?:ERROR|SCRIPT ERROR):',txt,re.M)),'log':str(log)}
 results.append(row);print(json.dumps(row),flush=True)
 (out/(a.stage+'-results.json')).write_text(json.dumps(results,indent=2),encoding='utf-8')
 if name=='IMPORT' and not success:break
raise SystemExit(0 if all(x['pass'] for x in results) else 1)
