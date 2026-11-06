#!/usr/bin/env python3
"""Start a private Health server and run the OPC-15 portable HTTP runner.

Mandatory: exits 0 only when the runner reports a positive assertion count.
Missing/unreachable server => exit 2 (UNVERIFIED). A runner exit code alone is
not enough: zero assertions or a missing marker is a failure, never a pass.
Artifacts in TestResults/clientcore-http.
"""

import os
import re
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DOTNET = os.environ.get("DOTNET", "dotnet")
# O7: the portable client builds with SDK 8, the Health server with SDK 10.
# A single DOTNET remains a valid fallback for machines that only have one SDK.
DOTNET_CLIENT = os.environ.get("DOTNET_CLIENT", DOTNET)
DOTNET_SERVER = os.environ.get("DOTNET_SERVER", DOTNET)
RUNNER_TIMEOUT_SECONDS = int(os.environ.get("RUNNER_TIMEOUT_SECONDS", "600"))
ARTIFACTS = os.path.join(ROOT, "TestResults", "clientcore-http")
SERVER_LOG = os.path.join(ARTIFACTS, "server.log")
RUNNER_LOG = os.path.join(ARTIFACTS, "runner.log")
ASSERTIONS_FILE = os.path.join(ARTIFACTS, "assertions.txt")
HEALTH_CSPROJ = os.path.join(ROOT, "Server", "Health", "Health.csproj")
HEALTH_DLL = os.path.join(ROOT, "Server", "Health", "bin", "Release", "net10.0", "Health.dll")
RUNNER_CSPROJ = os.path.join(ROOT, "Shared", "ClientCore.HttpRunner", "ClientCore.HttpRunner.csproj")

ASSERTION_MARKER = re.compile(r"^PASS ClientCore HTTP assertions: (\d+)\s*$", re.MULTILINE)
SERVER_IDENTITY = "ngu-mach-huyen-an-server"

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


def decode_capture(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else value.decode("utf-8", "replace")


def wait_healthy(base_url, process, timeout_seconds=90):
    identity_seen = False
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=1) as reply:
                if reply.status == 200:
                    body = reply.read().decode("utf-8", "replace")
                    if SERVER_IDENTITY in body:
                        identity_seen = True
                        return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1)
    if identity_seen:
        print("ERROR: health endpoint responded without the expected server identity", file=sys.stderr)
    return False


def assertion_count(stdout):
    match = ASSERTION_MARKER.search(stdout or "")
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def main():
    os.makedirs(ARTIFACTS, exist_ok=True)
    with open(ASSERTIONS_FILE, "w", encoding="utf-8") as f:
        f.write("0\n")

    build = run([DOTNET_SERVER, "build", HEALTH_CSPROJ, "-c", "Release", "--nologo"], cwd=ROOT)
    if build.returncode != 0:
        print("ERROR: server build failed", file=sys.stderr)
        return 1
    rbuild = run([DOTNET_CLIENT, "build", RUNNER_CSPROJ, "-c", "Release", "--nologo"], cwd=ROOT)
    if rbuild.returncode != 0:
        print("ERROR: runner build failed", file=sys.stderr)
        return 1

    print("==> client dotnet: " + DOTNET_CLIENT, flush=True)
    print("==> server dotnet: " + DOTNET_SERVER, flush=True)

    port = int(os.environ.get("E2E_PORT") or free_port())
    base_url = "http://127.0.0.1:{}".format(port)
    env = os.environ.copy()
    env.update(P1_FLAGS)
    env["ASPNETCORE_URLS"] = base_url
    env["DOTNET_ROLL_FORWARD"] = "LatestMajor"

    print("==> starting private server at " + base_url, flush=True)
    server_log = open(SERVER_LOG, "w", encoding="utf-8", errors="replace")
    process = subprocess.Popen(
        [DOTNET_SERVER, HEALTH_DLL, "--urls", base_url],
        cwd=ROOT, env=env, stdout=server_log, stderr=subprocess.STDOUT)
    try:
        if not wait_healthy(base_url, process):
            print("ERROR: server did not become healthy with identity '" + SERVER_IDENTITY +
                  "'; see " + SERVER_LOG, file=sys.stderr)
            return 1

        env["P1_BASE_URL"] = base_url
        print("==> running portable HTTP runner (mandatory)", flush=True)
        try:
            result = subprocess.run(
                [DOTNET_CLIENT, "run", "--project", RUNNER_CSPROJ, "-c", "Release"],
                cwd=ROOT, env=env, capture_output=True, text=True,
                timeout=RUNNER_TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired as timeout:
            with open(RUNNER_LOG, "w", encoding="utf-8") as log:
                log.write(decode_capture(timeout.output))
                log.write(decode_capture(timeout.stderr))
                log.write("\nERROR: runner exceeded {} seconds\n".format(RUNNER_TIMEOUT_SECONDS))
            print("ERROR: runner exceeded " + str(RUNNER_TIMEOUT_SECONDS) + " seconds", file=sys.stderr)
            return 1
        with open(RUNNER_LOG, "w", encoding="utf-8") as log:
            log.write(result.stdout or "")
            log.write(result.stderr or "")
        sys.stdout.write(result.stdout or "")
        sys.stderr.write(result.stderr or "")

        count = assertion_count(result.stdout)
        with open(ASSERTIONS_FILE, "w", encoding="utf-8") as f:
            f.write(str(count if count is not None else 0) + "\n")
        print("==> runner exit {}".format(result.returncode), flush=True)
        print("==> assertions: {}".format(count if count is not None else "missing"), flush=True)
        print("artifacts: " + ARTIFACTS, flush=True)

        if result.returncode == 2:
            print("ERROR: runner UNVERIFIED (no server / skip)", file=sys.stderr)
            return 2
        if result.returncode != 0:
            return 1
        if count is None:
            print("ERROR: runner did not report '" + ASSERTION_MARKER.pattern +
                  "' - zero-assertion runs cannot pass", file=sys.stderr)
            return 1
        if count <= 0:
            print("ERROR: runner reported zero assertions", file=sys.stderr)
            return 1
        return 0
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
