"""Run the integrated Bến Mưa development profile; optionally configure this checkout's Unity client."""
import argparse
import json
import os
from pathlib import Path
import socket
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--dotnet',default='dotnet')
    p.add_argument('--port',type=int,default=5000);p.add_argument('--configure-client',action='store_true');a=p.parse_args()
    if not 1024<=a.port<=65535:p.error('Port must be 1024..65535')
    with socket.socket() as sock:
        try:sock.bind(('127.0.0.1',a.port))
        except OSError:raise SystemExit(f'Port {a.port} is occupied. Choose --port; no existing process was stopped.')
    subprocess.run([a.dotnet,'build',str(ROOT/'Server/Health/Health.csproj'),'-c','Release','--nologo'],cwd=ROOT,check=True)
    url=f'http://127.0.0.1:{a.port}'
    if a.configure_client:
        local=ROOT/'Client/Assets/Resources/client-config.local.json'
        if local.exists():
            raise SystemExit('Local client profile already exists; preserve it and configure it manually, or run without --configure-client.')
        local.write_text(json.dumps(dict(healthUrl=url+'/health',healthTimeoutSeconds=3,healthPollIntervalSeconds=10,
            apiBaseUrl=url,apiTimeoutSeconds=5,onlineV2Enabled=True),indent=2)+'\n',encoding='utf-8')
        print('Wrote ignored local client profile; Unity uses it when present.',flush=True)
    env=os.environ.copy();env['ASPNETCORE_URLS']=url
    for flag in ['QuestAccept','Interact','QuestTurnIn','CombatV2','CombatDamage']:env[f'P1__{flag}__Enabled']='true'
    env['P1__MobBehavior__Enabled']='false'
    print('DEV NARRATIVE: P00-01 executable; later quests remain source-blocked. No approved production navigation.',flush=True)
    print('Quest/CombatV2/CombatDamage routes ON for valid entity HP; mob AI OFF. '+url,flush=True)
    server=subprocess.Popen([a.dotnet,str(ROOT/'Server/Health/bin/Release/net10.0/Health.dll')],
        cwd=ROOT/'Server/Health',env=env,creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
    try:return server.wait()
    except KeyboardInterrupt:server.terminate();return server.wait(timeout=10)
if __name__=='__main__':raise SystemExit(main())
