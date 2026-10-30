#!/usr/bin/env python3
"""Compile the real factory against a source-extracted root method signature.

This is a narrow local-API binding probe using synthetic Unity type stubs.
It is NOT Unity compilation, import, scene setup or runtime acceptance.
The reviewed checkout is never patched. Exit1 means a factory binding finding.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--dotnet',default='dotnet')
    p.add_argument('--output',required=True,type=Path)
    a=p.parse_args();root=a.root.resolve()
    base=root/'Client/Assets/Scripts/Online/Unity/PlayerUI'
    inputs=[base/n for n in ['PlayerUIFactory.cs','PlayerUIRoot.cs','PlayerPrefsSettingsStore.cs']]
    factory,root_file,store_file=inputs
    method=re.search(r'public void SetPanelReferences\s*\((.*?)\)\s*\{',root_file.read_text(encoding='utf-8-sig'),re.S)
    namespace=re.search(r'namespace\s+([\w.]+)',store_file.read_text(encoding='utf-8-sig'))
    if not method or not namespace: p.error('unsupported source shape; do not guess a signature')
    signature=method.group(1)
    params=[x.strip() for x in signature.split(',') if x.strip()]
    if any(not re.fullmatch(r'\w+\s+\w+',x) for x in params):p.error('unsupported parameter declaration')
    panels=['InventoryPanel','CharacterPanel','QuestJournalPanel','NpcDialoguePanel','SettingsPanel','MapPanel','PlayerUIButtonBar','CinemaOverlay']
    stubs="""namespace UnityEngine {
      public class Component {}
      public class MonoBehaviour:Component {}
      public class Transform {public void SetParent(Transform p,bool b){}}
      public class GameObject {public Transform transform=new Transform();public GameObject(string n){}
        public T GetComponent<T>() where T:Component => default(T);
        public T GetComponentInChildren<T>() where T:Component => default(T);
        public T AddComponent<T>() where T:Component,new()=>new T();}
    }
    namespace UnityEngine.UIElements {public class UIDocument:UnityEngine.MonoBehaviour {}}
    namespace NguMach.Client.P1 {
    """+''.join('public class '+n+':UnityEngine.MonoBehaviour {}' for n in panels)+"""
    public class PlayerUIRoot:UnityEngine.MonoBehaviour {public void SetPanelReferences("""+signature+"""){} }
    }
    namespace """+namespace.group(1)+""" {public class PlayerPrefsSettingsStore:UnityEngine.MonoBehaviour {}}
    """
    head=subprocess.run(['git','-C',str(root),'rev-parse','HEAD'],capture_output=True,text=True,check=True).stdout.strip()
    evidence={'reviewedHead':head,'scope':'NARROW_SOURCE_API_BINDING_WITH_SYNTHETIC_UNITY_STUBS_NOT_NATIVE',
      'rootParameterCount':len(params),'storeNamespace':namespace.group(1),
      'sourceSha256':{x.relative_to(root).as_posix():hashlib.sha256(x.read_bytes()).hexdigest() for x in inputs}}
    with tempfile.TemporaryDirectory(prefix='ngumach-factory-binding-') as tmp:
      folder=Path(tmp);(folder/'Stubs.cs').write_text(stubs,encoding='utf8')
      project=ET.Element('Project',Sdk='Microsoft.NET.Sdk');props=ET.SubElement(project,'PropertyGroup')
      for k,v in [('TargetFramework','net10.0'),('EnableDefaultCompileItems','false')]:ET.SubElement(props,k).text=v
      group=ET.SubElement(project,'ItemGroup')
      for path in [factory,folder/'Stubs.cs']:ET.SubElement(group,'Compile',Include=str(path))
      ET.ElementTree(project).write(folder/'Binding.csproj',encoding='unicode')
      r=subprocess.run([a.dotnet,'build',str(folder/'Binding.csproj'),'--nologo','--verbosity','minimal'],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=120)
      evidence['exitCode']=r.returncode
      evidence['diagnostics']=list(dict.fromkeys(line.strip() for line in (r.stdout+r.stderr).splitlines() if ': error CS' in line))
      evidence['status']='PASS_BINDING_ONLY' if not r.returncode else ('FAIL_BINDING' if evidence['diagnostics'] else 'BLOCKED')
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(evidence,ensure_ascii=False,indent=2))
    return 2 if evidence['status']=='BLOCKED' else int(bool(r.returncode))

if __name__=='__main__':raise SystemExit(main())
