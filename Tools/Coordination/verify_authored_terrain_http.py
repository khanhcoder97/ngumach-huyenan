"""Private real HTTP checks for game movement/collision/guard. Starts/stops only its own server."""
import argparse, datetime, json, math, os, socket, subprocess, time, urllib.request, urllib.error, uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def run(dotnet,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with socket.socket() as probe:probe.bind(('127.0.0.1',0));port=probe.getsockname()[1]
    base='http://127.0.0.1:'+str(port);env=os.environ.copy()
    env.update({'DOTNET_ROOT':str(Path(dotnet).parent),'Content__BenMuaTerrainPath':str(ROOT/'Implementation/Content/Maps/BenMua/terrain.json'),
        'P1World__MoveSpeedWuPerSecond':'3.2','P1World__MaxStepSeconds':'0.10','P1__CombatV2__Enabled':'true','P1__CombatDamage__Enabled':'true',
        'P1__MobBehavior__Enabled':'false','P1__DeathReturn__Enabled':'false','Logging__LogLevel__Microsoft.AspNetCore':'Warning'})
    log=(output/'terrain_http.server.log').open('w',encoding='utf-8');checks=[]
    server=subprocess.Popen([dotnet,str(ROOT/'Server/Health/bin/Release/net10.0/Health.dll'),'--urls',base],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    def check(ok,name):
        if not ok:raise AssertionError(name)
        checks.append(name)
    def call(path,body=None,session=None):
        headers={'Content-Type':'application/json'}
        if session:headers['X-Session-ID']=session['id']
        req=urllib.request.Request(base+path,data=None if body is None else json.dumps(body).encode(),headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=8) as response:return response.status,json.load(response)
        except urllib.error.HTTPError as e:return e.code,json.load(e)
    def create():
        code,r=call('/p1/sessions',{'classId':'CLASS_MINH_KIEM'});check(code==201,'real session created')
        return {'id':r['sessionId'],'char':r['result']['self']['characterId'],'self':r['result']['self'],'seq':0}
    def command(s,payload,schema=1):
        s['seq']+=1;payload['inputSequence']=s['seq'];now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        return {'schemaVersion':schema,'requestId':uuid.uuid4().hex,'idempotencyKey':uuid.uuid4().hex,'sentAtUtc':now,'characterId':s['char'],'payload':payload}
    def move(s,dx,dy):
        time.sleep(.06);code,r=call('/p1/move',command(s,{'moveX':dx,'moveY':dy}),s)
        if code==200:s['self']=r['result']['self']
        else:check(code==422 and r['error']['code']=='movement_blocked','server rejects movement through terrain: '+str((code,r)))
        return code,r
    def axis(s,key,target):
        deadline=time.monotonic()+18
        while abs(s['self'][key]-target)>.15:
            if time.monotonic()>deadline:raise TimeoutError('axis '+key+' '+str(target))
            direction=1 if target>s['self'][key] else -1
            code,r=move(s,direction if key=='x' else 0,direction if key=='y' else 0)
            if code!=200:raise AssertionError(('unexpected blocked path',key,target,s['self'],r))
    def blocked(s,dx,dy):
        for _ in range(150):
            before=dict(s['self']);code,r=move(s,dx,dy)
            if code!=200:
                code,world=call('/p1/world/'+s['id']);check(code==200 and world['result']['self']['x']==before['x'] and world['result']['self']['y']==before['y'],'rejected move does not change position');return
        raise AssertionError('terrain never blocked motion')
    try:
        for _ in range(120):
            if server.poll() is not None:raise RuntimeError('owned server exited')
            try:
                code,health=call('/health')
                if code==200:break
            except (OSError,ValueError):pass
            time.sleep(.1)
        else:raise TimeoutError('owned server health')
        a=create();axis(a,'x',27);blocked(a,0,1);check(0<a['self']['y']<2,'house foundation blocks northward walk')
        b=create();axis(b,'x',39);blocked(b,0,-1);check(-8<b['self']['y']<-4,'river bank blocks water walking')
        c=create();axis(c,'x',37);axis(c,'y',-10.5);check(c['self']['y']<-10,'real server allows connected dock deck')
        blocked(c,1,0);check(c['self']['x']<37.3,'dock side prevents walking on water')
        blocked(c,0,-1);check(-12<c['self']['y']<-11,'dock end respects full actor footprint')
        g=create();now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        payload={'actionKind':'SKILL','skillId':'SK-MK-01','targetId':None,'aimX':1,'aimY':0,'clientTimeUtc':now}
        code,r=call('/p1/v2/combat',command(g,dict(payload),2),g)
        check(code==200 and r['result']['mp']==38 and r['result']['mpCost']==12,'self guard with null target is accepted once')
        check(any(e['type']=='CAST_START' for e in r['result']['events']),'accepted skill supplies presentation start event')
        check(not any(e['type']=='COUNTER_CONFIRMED' for e in r['result']['events']),'guard acceptance does not invent a counter hit')
        code,r=call('/p1/v2/combat',command(g,dict(payload),2),g);check(code==409 and r['error']['code']=='cooldown_active','duplicate fresh cast gets explicit cooldown rejection')
        code,r=call('/p1/world/'+g['id']);check(r['result']['self']['mp']==38,'rejected cooldown cast consumes no extra MP')
        result={'status':'PASS','checks':len(checks),'assertions':checks,'baseUrl':base,'serverPid':server.pid,'scope':'real private HTTP movement/terrain/guard; no production sessions or fake grants'}
        (output/'terrain_http.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print('AUTHORED_TERRAIN_HTTP PASS assertions='+str(len(checks)))
    finally:
        server.terminate()
        try:server.wait(timeout=8)
        except subprocess.TimeoutExpired:server.kill();server.wait()
        log.close()
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dotnet',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.dotnet,a.output)
