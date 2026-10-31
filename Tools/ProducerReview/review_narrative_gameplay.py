"""Run concrete client narrative against a private server; never patch either checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import urllib.request

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--client-root',type=Path,required=True);p.add_argument('--server-root',type=Path,required=True)
    p.add_argument('--dotnet',default='dotnet');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();client=a.client_root.resolve();server=a.server_root.resolve();a.output.parent.mkdir(parents=True,exist_ok=True)
    binary=server/'Server/Health/bin/Release/net10.0/Health.dll'
    runner=client/'Client/Tests/NarrativeChecks/bin/Release/net10.0/NarrativeChecks.dll'
    if not binary.is_file() or not runner.is_file():p.error('Build both projects in Release first')
    with socket.socket() as sock:sock.bind(('127.0.0.1',0));port=sock.getsockname()[1]
    base=f'http://127.0.0.1:{port}';env=os.environ.copy();env['ASPNETCORE_URLS']=base
    for name in ['QuestAccept','Interact','QuestTurnIn','CombatV2','CombatDamage']:env[f'P1__{name}__Enabled']='true'
    env['P1__MobBehavior__Enabled']='false'
    evidence={'scope':'CONCRETE_P1CLIENT_PRIVATE_DEV_HTTP_NOT_UNITY','profile':'quest/CombatV2/CombatDamage ON (required HP projection); mob AI OFF; production topology not approved',
        'serverHead':subprocess.check_output(['git','rev-parse','HEAD'],cwd=server,text=True).strip(),
        'serverBinarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'resourceSha256':hashlib.sha256((client/'Client/Assets/Resources/Narrative/dialogue_vi.json').read_bytes()).hexdigest()}
    with a.output.with_suffix('.server.log').open('w',encoding='utf-8') as log:
        process=subprocess.Popen([a.dotnet,str(binary)],cwd=server/'Server/Health',env=env,stdout=log,stderr=subprocess.STDOUT)
        try:
            for _ in range(100):
                try:urllib.request.urlopen(base+'/health',timeout=1).close();break
                except OSError:time.sleep(.1)
            else:raise RuntimeError('private server unavailable')
            run=subprocess.run([a.dotnet,str(runner),str(client/'Client/Assets/Resources/Narrative/dialogue_vi.json'),'--http',base],
                cwd=client,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=150)
            a.output.with_suffix('.client.log').write_text(run.stdout+run.stderr,encoding='utf-8')
            evidence.update(status='PASS' if run.returncode==0 else 'FAIL',exitCode=run.returncode,
                assertions=sum(line.startswith('PASS ') and not line.startswith('PASS narrative HTTP') for line in run.stdout.splitlines()),
                diagnostics=run.stderr[-2000:])
        finally:process.terminate();process.wait(timeout=10);evidence['ownServerStopped']=True
    a.output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,ensure_ascii=False,indent=2));return evidence['exitCode']
if __name__=='__main__':raise SystemExit(main())
