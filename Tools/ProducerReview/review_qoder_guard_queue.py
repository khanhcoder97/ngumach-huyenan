#!/usr/bin/env python3
"""Compile a guard-queue probe against a built server without patching it."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--root', required=True, type=Path)
p.add_argument('--dotnet', default='dotnet')
p.add_argument('--output', required=True, type=Path)
a = p.parse_args()
root = a.root.resolve()
dll = root / 'Server/Health/bin/Release/net10.0/Health.dll'
if not dll.is_file():
    p.error('Build the server in Release first')
probe = Path(__file__).with_name('QoderGuardQueueProbe.cs')
with tempfile.TemporaryDirectory(prefix='ngumach-guard-queue-') as temp:
    project = ET.Element('Project', Sdk='Microsoft.NET.Sdk')
    props = ET.SubElement(project, 'PropertyGroup')
    for k, v in [('TargetFramework', 'net10.0'), ('OutputType', 'Exe'), ('EnableDefaultCompileItems', 'false')]:
        ET.SubElement(props, k).text = v
    items = ET.SubElement(project, 'ItemGroup')
    ET.SubElement(items, 'Compile', Include=str(probe))
    ref = ET.SubElement(items, 'Reference', Include='Health')
    ET.SubElement(ref, 'HintPath').text = str(dll)
    ET.SubElement(items, 'FrameworkReference', Include='Microsoft.AspNetCore.App')
    path = Path(temp) / 'QueueProbe.csproj'
    ET.ElementTree(project).write(path, encoding='unicode')
    run = subprocess.run([a.dotnet, 'run', '--project', str(path), '-c', 'Release', '--verbosity', 'quiet'],
                         capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    marker = next((s[len('QUEUE_EVIDENCE '):] for s in run.stdout.splitlines()
                   if s.startswith('QUEUE_EVIDENCE ')), None)
    result = json.loads(marker) if marker else {'status': 'BLOCKED', 'diagnostics': (run.stdout + run.stderr)[-2000:]}
    result['reviewedHead'] = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                                          check=True, capture_output=True, text=True).stdout.strip()
    result['serverBinarySha256'] = hashlib.sha256(dll.read_bytes()).hexdigest()
    result['exitCode'] = run.returncode
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, indent=2))
raise SystemExit(2 if result['status'] == 'BLOCKED' else (1 if result['status'] == 'FAIL' else 0))
