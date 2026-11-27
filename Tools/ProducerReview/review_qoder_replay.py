#!/usr/bin/env python3
"""Probe completed-cast replay on a private loopback DEV server; never patch source."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--dotnet', default='dotnet')
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    dll = root / 'Server/Health/bin/Release/net10.0/Health.dll'
    if not dll.is_file():
        parser.error('Build Server/Health in Release before running this probe')
    head = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], check=True,
                          capture_output=True, text=True).stdout.strip()
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    base = 'http://127.0.0.1:' + str(port)

    def call(method, path, body=None, session=None):
        data = None if body is None else json.dumps(body).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        if session:
            headers['X-Session-ID'] = session
        req = urllib.request.Request(base + path, data=data, method=method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=4) as response:
                return response.status, json.loads(response.read() or '{}')
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read() or '{}')

    evidence = {'reviewedHead': head,
                'serverBinarySha256': hashlib.sha256(dll.read_bytes()).hexdigest(),
                'scope': 'Private synthetic DEV HTTP; completed BASIC_ATTACK replay, not HP damage or Unity',
                'mobBehaviorEnabled': False}
    environment = os.environ.copy()
    for feature in ['QuestAccept', 'Interact', 'QuestTurnIn', 'CombatV2', 'CombatDamage']:
        environment['P1__' + feature + '__Enabled'] = 'true'
    environment['P1__MobBehavior__Enabled'] = 'false'
    environment['ASPNETCORE_URLS'] = base
    with tempfile.TemporaryDirectory(prefix='ngumach-qoder-replay-') as temp:
        with (Path(temp) / 'server.log').open('w', encoding='utf-8') as log:
            process = subprocess.Popen([args.dotnet, str(dll)], cwd=root / 'Server/Health',
                                       env=environment, stdout=log, stderr=subprocess.STDOUT)
            try:
                ready = False
                for _ in range(100):
                    if process.poll() is not None:
                        break
                    try:
                        call('GET', '/health')
                        ready = True
                        break
                    except (OSError, ValueError):
                        time.sleep(0.1)
                if not ready:
                    raise RuntimeError('Private server failed to start; no other process was modified')
                character = 'CHR_CDX_QODER_REPLAY'
                status, created = call('POST', '/p1/sessions', {'characterId': character})
                if status != 201:
                    raise RuntimeError('Session returned HTTP ' + str(status))
                session = created['sessionId']
                body = {'schemaVersion': 2, 'requestId': uuid.uuid4().hex,
                        'idempotencyKey': uuid.uuid4().hex,
                        'sentAtUtc': datetime.now(timezone.utc).isoformat(), 'characterId': character,
                        'payload': {'actionKind': 'BASIC_ATTACK', 'inputSequence': 1, 'aimX': 1, 'aimY': 0}}
                status, first = call('POST', '/p1/v2/combat', body, session)
                if status != 200:
                    raise RuntimeError('Cast returned HTTP ' + str(status))
                cast = first['result']['castId']
                before = None
                for _ in range(100):
                    _, page = call('GET', '/p1/v2/events/' + session + '?cursor=0')
                    result = page.get('result', {})
                    if any(e['type'] == 'END' and e['castId'] == cast for e in result.get('events', [])):
                        before = result
                        break
                    time.sleep(0.05)
                if before is None:
                    raise RuntimeError('No END observed before replay; probe inconclusive')
                cursor = before['nextCursor']
                status, replay = call('POST', '/p1/v2/combat', body, session)
                after = []
                for _ in range(24):
                    time.sleep(0.05)
                    _, page = call('GET', '/p1/v2/events/' + session + '?cursor=' + str(cursor))
                    after = page.get('result', {}).get('events', [])
                    if after:
                        break
                evidence.update(replayHttpStatus=status,
                                sameCastId=replay.get('result', {}).get('castId') == cast,
                                eventsBefore=[{'type': e['type'], 'cursor': e['cursor']} for e in before['events']],
                                eventsAfterReplay=[{'type': e['type'], 'cursor': e['cursor']} for e in after])
                evidence['status'] = ('PASS' if status == 200 and evidence['sameCastId'] and not after else 'FAIL')
            except Exception as error:
                evidence.update(status='BLOCKED', reason=str(error))
            finally:
                process.terminate()
                try:
                    process.wait(timeout=8)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=4)
                evidence['ownServerStopped'] = process.poll() is not None
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(evidence, indent=2))
    return 2 if evidence['status'] == 'BLOCKED' else (1 if evidence['status'] == 'FAIL' else 0)


if __name__ == '__main__':
    raise SystemExit(main())
