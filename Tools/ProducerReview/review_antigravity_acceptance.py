#!/usr/bin/env python3
"""Run unchanged author tests and AG-02 acceptance probes outside the checkout.

This diagnostic does not patch the reviewed csproj/source and does not verify
Unity types, scene bootstrap, input dispatch or real HTTP. Exit 1 means findings.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    negative = Path(__file__).with_name('AntigravityAcceptanceChecks.cs')
    inputs = []
    for folder in ['Client/Assets/Scripts/Online/Core',
                   'Client/Assets/Scripts/Online/Presentation',
                   'Client/Tests/PlayerUIChecks']:
        files = sorted((root / folder).glob('*.cs'))
        if not files:
            parser.error('Missing C# inputs: ' + folder)
        inputs.extend(files)
    head = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'],
                          check=True, capture_output=True, text=True).stdout.strip()
    evidence = {'reviewedHead': head,
                'scope': 'Author tests plus AG-02 acceptance probes; no source patch or native Unity/HTTP',
                'sourceSha256': {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in inputs},
                'negativeChecksSha256': hashlib.sha256(negative.read_bytes()).hexdigest()}
    with tempfile.TemporaryDirectory(prefix='ngumach-ag-review-') as scratch:
        folder = Path(scratch)
        project = ET.Element('Project', Sdk='Microsoft.NET.Sdk')
        props = ET.SubElement(project, 'PropertyGroup')
        for key, value in [('TargetFramework', 'net10.0'), ('LangVersion', '9.0'),
                           ('Nullable', 'disable'), ('ImplicitUsings', 'disable'),
                           ('EnableDefaultCompileItems', 'false')]:
            ET.SubElement(props, key).text = value
        packages = ET.SubElement(project, 'ItemGroup')
        for name, version in [('Microsoft.NET.Test.Sdk', '17.11.1'), ('xunit', '2.9.2'),
                              ('xunit.runner.visualstudio', '2.8.2'), ('Newtonsoft.Json', '13.0.3')]:
            ET.SubElement(packages, 'PackageReference', Include=name, Version=version)
        sources = ET.SubElement(project, 'ItemGroup')
        for path in inputs + [negative]:
            ET.SubElement(sources, 'Compile', Include=str(path))
        ET.ElementTree(project).write(folder / 'ProducerChecks.csproj', encoding='unicode')
        command = [args.dotnet, 'test', str(folder / 'ProducerChecks.csproj'), '-c', 'Release',
                   '--nologo', '--logger', 'trx;LogFileName=producer.trx',
                   '--results-directory', str(folder / 'results'), '--verbosity', 'minimal']
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    encoding='utf-8', errors='replace', timeout=240)
        except (OSError, subprocess.TimeoutExpired) as error:
            evidence.update(status='BLOCKED', reason=type(error).__name__)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            print('BLOCKED:', type(error).__name__)
            return 2
        evidence['exitCode'] = result.returncode
        trx = folder / 'results/producer.trx'
        if trx.is_file():
            ns = {'t': 'http://microsoft.com/schemas/VisualStudio/TeamTest/2010'}
            tree = ET.parse(trx)
            evidence['counters'] = tree.find('.//t:Counters', ns).attrib
            evidence['failedTests'] = [
                {'name': test.attrib['testName'],
                 'message': test.findtext('t:Output/t:ErrorInfo/t:Message', default='', namespaces=ns)}
                for test in tree.findall('.//t:UnitTestResult', ns)
                if test.attrib['outcome'] != 'Passed']
            evidence['status'] = 'PASS_DIAGNOSTIC_ONLY' if result.returncode == 0 else 'FAIL'
        else:
            evidence.update(status='BLOCKED', reason='No TRX; build/restore failed',
                            diagnostics=[line for line in (result.stdout + result.stderr).splitlines()
                                         if 'error ' in line][:12])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: evidence[k] for k in ['reviewedHead', 'status', 'exitCode', 'counters', 'failedTests']
                      if k in evidence}, ensure_ascii=False, indent=2))
    return 2 if evidence['status'] == 'BLOCKED' else (1 if result.returncode else 0)


if __name__ == '__main__':
    raise SystemExit(main())
