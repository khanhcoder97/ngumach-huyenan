#!/usr/bin/env python3
"""Start the private Health server and run the OPC-14 O2 HTTP acceptance.

No optional skip: this script either starts a real server, runs the real
P1Client/P1ClientAdapter/presenters against it, and returns the harness exit
code, or it returns non-zero. Artifacts (server + acceptance logs) are written
to TestResults/player-ui-http for CI upload.

Env:
  DOTNET   path to the dotnet executable (default: dotnet on PATH)
  E2E_PORT optional fixed port; otherwise a free ephemeral port is chosen

Usage: python Client/Tests/PlayerUIAcceptance/run_acceptance.py
"""

import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DOTNET = os.environ.get("DOTNET", "dotnet")
ARTIFACTS = os.path.join(ROOT, "TestResults", "player-ui-http")
SERVER_LOG = os.path.join(ARTIFACTS, "server.log")
ACCEPTANCE_LOG = os.path.join(ARTIFACTS, "acceptance.log")
HEALTH_CSPROJ = os.path.join(ROOT, "Server", "Health", "Health.csproj")
HEALTH_DLL = os.path.join(ROOT, "Server", "Health", "bin", "Release", "net10.0", "Health.dll")
ACCEPTANCE_CSPROJ = os.path.join(ROOT, "Client", "Tests", "PlayerUIAcceptance", "PlayerUIAcceptance.csproj")

P1_FLAGS = {
    "P1__QuestAccept__Enabled": "true",
    "P1__Interact__Enabled": "true",
    "P1__QuestTurnIn__Enabled": "true",
    "P1__CombatV2__Enabled": "true",
    "P1__CombatDamage__Enabled": "true",
    "P1__MobBehavior__Enabled": "false",
}


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run(cmd, **kwargs):
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, **kwargs)


def wait_healthy(base_url, process, timeout_seconds=90):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=1) as reply:
                if reply.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1)
    return False


def main():
    os.makedirs(ARTIFACTS, exist_ok=True)

    build = run([DOTNET, "build", HEALTH_CSPROJ, "-c", "Release", "--nologo"],
                cwd=ROOT)
    if build.returncode != 0:
        print("ERROR: server build failed", file=sys.stderr)
        return 1
    if not os.path.isfile(HEALTH_DLL):
        print("ERROR: Health.dll not found at " + HEALTH_DLL, file=sys.stderr)
        return 1

    port = int(os.environ.get("E2E_PORT") or free_port())
    base_url = "http://127.0.0.1:{}".format(port)
    env = os.environ.copy()
    env.update(P1_FLAGS)
    env["ASPNETCORE_URLS"] = base_url
    # Local SDKs only carry the newest runtime; net8 test/acceptance apps roll forward.
    env["DOTNET_ROLL_FORWARD"] = "LatestMajor"

    print("==> starting private server at " + base_url, flush=True)
    server_log = open(SERVER_LOG, "w", encoding="utf-8", errors="replace")
    process = subprocess.Popen(
        [DOTNET, HEALTH_DLL, "--urls", base_url],
        cwd=ROOT, env=env, stdout=server_log, stderr=subprocess.STDOUT)
    try:
        if not wait_healthy(base_url, process):
            print("ERROR: server did not become healthy; see " + SERVER_LOG, file=sys.stderr)
            return 1

        env["P1_BASE_URL"] = base_url
        print("==> running HTTP acceptance (mandatory)", flush=True)
        result = subprocess.run(
            [DOTNET, "run", "--project", ACCEPTANCE_CSPROJ, "-c", "Release"],
            cwd=ROOT, env=env, capture_output=True, text=True)
        with open(ACCEPTANCE_LOG, "w", encoding="utf-8") as log:
            log.write(result.stdout or "")
            log.write(result.stderr or "")
        sys.stdout.write(result.stdout or "")
        sys.stderr.write(result.stderr or "")
        print("==> acceptance exit {}".format(result.returncode), flush=True)
        print("artifacts: " + ARTIFACTS, flush=True)

        if result.returncode == 2:
            print("ERROR: acceptance UNVERIFIED (server reachable but harness skipped)", file=sys.stderr)
            return 2
        return 0 if result.returncode == 0 else 1
    finally:
        server_log.flush()
        server_log.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


if __name__ == "__main__":
    sys.exit(main())
