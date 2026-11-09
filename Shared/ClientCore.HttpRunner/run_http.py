#!/usr/bin/env python3
"""Paired private-alpha HTTP runner for OPC-15.

The client checkout and the server checkout are independent inputs. The runner
never builds Health from the client root unless that root is explicitly given as
the server root, and it never copies a server tree over the client branch.

Two gate modes are supported so CI can measure both sides of the same pairing:
  gates-off      - every private-alpha route must be unmapped/feature_unavailable
  private-alpha  - AlphaProfile plus QuestTalk/Portal/DeathReturn are enabled and
                   the checkpoint routes are exercised for real.

Mandatory contract: exit 0 only with a positive assertion count, a healthy
server that reports the expected identity, a server checkout whose HEAD
matches the requested pin, and (when --contract-pin is given) contract bytes
at the server root that hash exactly like the pinned manifest. Anything
missing is UNVERIFIED (exit 2) or FAIL (1), never a PASS. A child process
that survives cleanup is an orphan and fails the run.

The pass/fail decisions (decide_runner_exit, verify_contract_pin,
survivors) are pure functions so run_negative_controls.py can drive them
with real inputs and assert the runner refuses to pass.

Artifacts: TestResults/clientcore-http/<mode>/ plus a top-level summary.
"""

import argparse
import hashlib
import json
import os
import re
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DOTNET = os.environ.get("DOTNET", "dotnet")
DOTNET_CLIENT = os.environ.get("DOTNET_CLIENT", DOTNET)
DOTNET_SERVER = os.environ.get("DOTNET_SERVER", DOTNET)
# The full private-alpha journey (P00-01..P00-05 + finale + portal) walks about
# 1900 WU and casts through a 1200 HP boss over real HTTP at 0.3 s/step, so the
# default budget is 20 minutes; the CI workflow matches it.
RUNNER_TIMEOUT_SECONDS = int(os.environ.get("RUNNER_TIMEOUT_SECONDS", "1200"))
SERVER_IDENTITY = "ngu-mach-huyen-an-server"
ASSERTION_MARKER = re.compile(r"^PASS ClientCore HTTP assertions: (\d+)\s*$", re.MULTILINE)

BASE_FLAGS = {
    "P1__QuestAccept__Enabled": "true",
    "P1__Interact__Enabled": "true",
    "P1__QuestTurnIn__Enabled": "true",
    "P1__CombatV2__Enabled": "true",
    "P1__CombatDamage__Enabled": "true",
    "P1__MobBehavior__Enabled": "false",
}

ALPHA_FLAGS = {
    "P1__AlphaProfile__Enabled": "true",
    "P1__QuestTalk__Enabled": "true",
    "P1__Portal__Enabled": "true",
    "P1__DeathReturn__Enabled": "true",
    "P1__Equipment__Enabled": "true",
    # Checkpoint 2 (full tutorial): the P00 chain needs the alpha loot band to
    # exist (coin drop proves the kill credit + inventory revision) and a pool
    # that survives the wave-trial/escort/boss damage the AlphaProfile-driven
    # world tick applies regardless of MobBehavior. 4000/500 matches the
    # reference alpha-p00 boot in the server's run_e2e_p1.sh.
    #
    # MobBehavior must be ON here even though BASE_FLAGS keeps it OFF: the
    # projected `state` of MOB/BOSS rows comes from MobLifecycleService, whose
    # Tick only runs while the gate is enabled. With it off a killed mob keeps
    # projecting IDLE forever and no journey step can ever witness a death
    # (probe: "witnessed 0 of 4 CARPLING"). The reference alpha-p00 boot also
    # runs with MobBehavior enabled.
    "P1__MobBehavior__Enabled": "true",
    "P1__AlphaLoot__GrantEnabled": "true",
    "P1World__StartingHp": "4000",
    "P1World__StartingMaxHp": "4000",
    "P1World__StartingMp": "500",
    "P1World__StartingMaxMp": "500",
}

MODES = {
    "gates-off": {},
    "private-alpha": ALPHA_FLAGS,
}


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def run(cmd, cwd=None, **kwargs):
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=cwd, **kwargs)


def decode_capture(value):
    if value is None:
        return ""
    return value if isinstance(value, str) else value.decode("utf-8", "replace")


def kill_tree(process, label):
    """Terminate exactly the process tree rooted at this PID."""
    if process is None or process.poll() is not None:
        return
    print("==> cleanup {} pid={}".format(label, process.pid), flush=True)
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        else:
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=10)
    except (subprocess.TimeoutExpired, OSError, ProcessLookupError):
        try:
            if os.name == "nt":
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
            else:
                os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            process.wait(timeout=10)
        except (subprocess.TimeoutExpired, OSError, ProcessLookupError):
            pass


def git_head(root):
    try:
        result = subprocess.run(
            ["git", "-C", root, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def git_dirty_tracked(root):
    try:
        result = subprocess.run(
            ["git", "-C", root, "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            return [line for line in result.stdout.splitlines() if line.strip()]
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_contract_file(path):
    """Digest of the LF-normalized bytes.

    The same contract file checks out CRLF on Windows (core.autocrlf) and LF
    on CI, so contract pins must be EOL-independent to mean anything.
    """
    with open(path, "rb") as stream:
        data = stream.read()
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def content_fingerprint(content_root):
    """Hash the runtime bundles the checkpoint actually reads."""
    candidates = [
        "Implementation/Content/Runtime/narrative_nodes_v1.json",
        "Implementation/Content/Runtime/npc_anchors.json",
        "Implementation/Content/Runtime/world_entities_bm.json",
        "Implementation/Content/Runtime/world_records.json",
        "Implementation/Content/Runtime/loot_recipe_v1.json",
        "Implementation/Content/DesignBaselines/ben_mua_alpha_20261103.json",
    ]
    fingerprint = {}
    for relative in candidates:
        path = os.path.join(content_root, relative)
        if os.path.isfile(path):
            fingerprint[relative] = sha256_file(path)
    return fingerprint


def wait_healthy(base_url, process, timeout_seconds=None):
    if timeout_seconds is None:
        timeout_seconds = int(os.environ.get("P1_HEALTH_TIMEOUT_SECONDS", "90"))
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=2) as reply:
                if reply.status == 200:
                    body = reply.read().decode("utf-8", "replace")
                    if SERVER_IDENTITY in body:
                        return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(1)
    return False


def assertion_count(stdout):
    match = ASSERTION_MARKER.search(stdout or "")
    if not match:
        return None
    try:
        return int(match.group(1))
    except ValueError:
        return None


def decide_runner_exit(returncode, count):
    """Pure pass/fail decision for a finished runner process.

    Returns (exit_code, message). exit 2 = UNVERIFIED, 1 = FAIL, 0 = PASS.
    """
    if returncode == 2:
        return 2, "runner UNVERIFIED (no server / skip)"
    if returncode != 0:
        return 1, "runner exited {}".format(returncode)
    if count is None:
        return 1, ("runner did not report '" + ASSERTION_MARKER.pattern +
                   "' - zero-assertion runs cannot pass")
    if count <= 0:
        return 1, "runner reported zero assertions"
    return 0, ""


def verify_contract_pin(server_root, manifest_path):
    """Verify contract bytes at server_root against the pinned manifest.

    Pure decision helper: every file listed in the manifest must exist under
    server_root/Implementation/Contracts/P1 with exactly the pinned SHA-256,
    and the tree must contain no unpinned schema/example file. Returns
    (ok, message).
    """
    try:
        with open(manifest_path, "r", encoding="utf-8") as stream:
            manifest = json.load(stream)
    except (OSError, ValueError) as exc:
        return False, "contract manifest unreadable: {}".format(exc)
    files = manifest.get("files")
    if not files:
        return False, "contract manifest lists no files"
    root = os.path.join(server_root, "Implementation", "Contracts", "P1")
    problems = []
    pinned = set()
    for entry in files:
        kind, name, want = entry.get("kind"), entry.get("name"), entry.get("sha256")
        if kind not in ("schema", "example") or not name or not want:
            problems.append("malformed manifest entry: {!r}".format(entry))
            continue
        relative = (os.path.join("Examples", name) if kind == "example" else name)
        pinned.add(os.path.normpath(relative))
        path = os.path.join(root, relative)
        if not os.path.isfile(path):
            problems.append("missing {} {}".format(kind, name))
            continue
        got = sha256_contract_file(path)
        if got != want:
            problems.append("content mismatch {} {}: pinned {} got {}".format(
                kind, name, want[:12], got[:12]))
    # No unpinned contract file may hide next to the pinned set.
    if os.path.isdir(root):
        on_disk = set()
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isfile(path) and name.endswith(".schema.json"):
                on_disk.add(os.path.normpath(name))
        examples = os.path.join(root, "Examples")
        if os.path.isdir(examples):
            for name in os.listdir(examples):
                if name.endswith(".example.json"):
                    on_disk.add(os.path.normpath(os.path.join("Examples", name)))
        for relative in sorted(on_disk - pinned):
            problems.append("unpinned contract file: " + relative)
    else:
        problems.append("contract tree missing: " + root)
    if problems:
        return False, "; ".join(problems[:10]) + (
            " (+{} more)".format(len(problems) - 10) if len(problems) > 10 else "")
    return True, "{} pinned contract files verified".format(len(files))


def survivors(processes):
    """Pure check: which of these child processes are still alive?"""
    return [label for label, process in processes
            if process is not None and process.poll() is None]


def find_health_dll(server_root):
    health_bin = os.path.join(server_root, "Server", "Health", "bin", "Release")
    if not os.path.isdir(health_bin):
        return None
    # The pinned server targets net10.0; prefer that output over any stale
    # framework directory left by an older local build.
    preferred = os.path.join(health_bin, "net10.0", "Health.dll")
    if os.path.isfile(preferred):
        return preferred
    candidates = []
    for framework in os.listdir(health_bin):
        candidate = os.path.join(health_bin, framework, "Health.dll")
        if os.path.isfile(candidate):
            candidates.append((os.path.getmtime(candidate), candidate))
    candidates.sort(reverse=True)
    return candidates[0][1] if candidates else None


def write_summary(artifacts, lines):
    with open(os.path.join(artifacts, "summary.txt"), "w", encoding="utf-8") as stream:
        stream.write("\n".join(lines) + "\n")


def run_mode(args, mode):
    artifacts = os.path.join(args.artifacts_root, mode)
    os.makedirs(artifacts, exist_ok=True)
    server_log_path = os.path.join(artifacts, "server.log")
    runner_log_path = os.path.join(artifacts, "runner.log")
    assertions_path = os.path.join(artifacts, "assertions.txt")
    pins_path = os.path.join(artifacts, "pins.txt")
    with open(assertions_path, "w", encoding="utf-8") as stream:
        stream.write("0\n")

    server_head = git_head(args.server_root)
    client_head = git_head(args.client_root)
    if not server_head:
        print("ERROR: server root is not a readable git checkout: " + args.server_root,
              file=sys.stderr)
        return 1
    if not client_head:
        print("ERROR: client root is not a readable git checkout: " + args.client_root,
              file=sys.stderr)
        return 1
    if args.server_head and server_head != args.server_head:
        print("ERROR: server HEAD {} != pinned {}".format(server_head, args.server_head),
              file=sys.stderr)
        return 1
    if args.client_head and client_head != args.client_head:
        print("ERROR: client HEAD {} != pinned {}".format(client_head, args.client_head),
              file=sys.stderr)
        return 1
    contract_ok = None
    if args.contract_pin:
        contract_ok, contract_message = verify_contract_pin(args.server_root, args.contract_pin)
        print("==> contract pin: " + contract_message, flush=True)
        if not contract_ok:
            print("ERROR: contract pin verification failed: " + contract_message,
                  file=sys.stderr)
            return 1
    dirty = git_dirty_tracked(args.server_root)
    if dirty:
        print("ERROR: server checkout has tracked modifications: " + "; ".join(dirty),
              file=sys.stderr)
        return 1
    if not os.path.isdir(args.content_root):
        print("ERROR: content root does not exist: " + args.content_root, file=sys.stderr)
        return 1

    health_csproj = os.path.join(args.server_root, "Server", "Health", "Health.csproj")
    runner_csproj = os.path.join(
        args.client_root, "Shared", "ClientCore.HttpRunner", "ClientCore.HttpRunner.csproj")
    if not os.path.isfile(health_csproj):
        print("ERROR: server checkout has no Server/Health/Health.csproj: " + args.server_root,
              file=sys.stderr)
        return 1
    if not os.path.isfile(runner_csproj):
        print("ERROR: client checkout has no HTTP runner project: " + args.client_root,
              file=sys.stderr)
        return 1

    build = run([DOTNET_SERVER, "build", health_csproj, "-c", "Release", "--nologo"],
                cwd=args.server_root)
    if build.returncode != 0:
        print("ERROR: server build failed", file=sys.stderr)
        return 1
    rbuild = run([DOTNET_CLIENT, "build", runner_csproj, "-c", "Release", "--nologo"],
                 cwd=args.client_root)
    if rbuild.returncode != 0:
        print("ERROR: runner build failed", file=sys.stderr)
        return 1

    health_dll = find_health_dll(args.server_root)
    if not health_dll:
        print("ERROR: Health.dll not found after build under " + args.server_root,
              file=sys.stderr)
        return 1
    health_hash = sha256_file(health_dll)
    content_hashes = content_fingerprint(args.content_root)

    print("==> client dotnet: " + DOTNET_CLIENT, flush=True)
    print("==> server dotnet: " + DOTNET_SERVER, flush=True)
    print("==> mode: " + mode, flush=True)
    print("==> client root: " + args.client_root, flush=True)
    print("==> server root: " + args.server_root, flush=True)
    print("==> content root: " + args.content_root, flush=True)
    print("==> client head: " + str(client_head), flush=True)
    print("==> server head: " + str(server_head), flush=True)
    print("==> health sha256: " + health_hash, flush=True)
    for relative, digest in content_hashes.items():
        print("==> content " + relative + ": " + digest, flush=True)

    with open(pins_path, "w", encoding="utf-8") as stream:
        stream.write("mode={}\n".format(mode))
        stream.write("client_root={}\n".format(args.client_root))
        stream.write("client_head={}\n".format(client_head))
        stream.write("server_root={}\n".format(args.server_root))
        stream.write("server_head={}\n".format(server_head))
        stream.write("content_root={}\n".format(args.content_root))
        stream.write("health_dll={}\n".format(health_dll))
        stream.write("health_sha256={}\n".format(health_hash))
        if args.contract_pin:
            stream.write("contract_pin_manifest={}\n".format(args.contract_pin))
            stream.write("contract_pin_ok={}\n".format(contract_ok))
        for relative, digest in content_hashes.items():
            stream.write("content:{}={}\n".format(relative, digest))

    port = int(os.environ.get("E2E_PORT") or free_port())
    base_url = "http://127.0.0.1:{}".format(port)
    env = os.environ.copy()
    env.update(BASE_FLAGS)
    env.update(MODES[mode])
    env["ASPNETCORE_URLS"] = base_url
    env["ASPNETCORE_CONTENTROOT"] = args.content_root
    env["DOTNET_ROLL_FORWARD"] = "LatestMajor"
    env["P1_ALPHA_MODE"] = mode

    print("==> starting private server at " + base_url, flush=True)
    server_log = open(server_log_path, "w", encoding="utf-8", errors="replace")
    process = subprocess.Popen(
        [DOTNET_SERVER, health_dll, "--urls", base_url],
        cwd=args.content_root, env=env, stdout=server_log, stderr=subprocess.STDOUT,
        start_new_session=(os.name != "nt"))
    runner_process = None
    result = 1
    try:
        if not wait_healthy(base_url, process):
            print("ERROR: server pid={} did not become healthy with identity '{}'; see {}".format(
                process.pid, SERVER_IDENTITY, server_log_path), file=sys.stderr)
            result = 1
        elif process.poll() is not None:
            print("ERROR: server pid={} exited after health check".format(process.pid),
                  file=sys.stderr)
            result = 1
        else:
            print("==> server healthy pid={}".format(process.pid), flush=True)

            env["P1_BASE_URL"] = base_url
            print("==> running portable HTTP runner (mandatory)", flush=True)
            runner_process = subprocess.Popen(
                [DOTNET_CLIENT, "run", "--project", runner_csproj, "-c", "Release", "--no-build"],
                cwd=args.client_root, env=env,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                start_new_session=(os.name != "nt"))
            try:
                stdout, _ = runner_process.communicate(timeout=RUNNER_TIMEOUT_SECONDS)
            except subprocess.TimeoutExpired:
                kill_tree(runner_process, "runner-timeout")
                stdout, _ = runner_process.communicate()
                with open(runner_log_path, "w", encoding="utf-8") as log:
                    log.write(decode_capture(stdout))
                    log.write("\nERROR: runner exceeded {} seconds\n".format(RUNNER_TIMEOUT_SECONDS))
                print("ERROR: runner exceeded " + str(RUNNER_TIMEOUT_SECONDS) + " seconds",
                      file=sys.stderr)
                result = 1
            else:
                text = decode_capture(stdout)
                with open(runner_log_path, "w", encoding="utf-8") as log:
                    log.write(text)
                sys.stdout.write(text)

                count = assertion_count(text)
                with open(assertions_path, "w", encoding="utf-8") as stream:
                    stream.write(str(count if count is not None else 0) + "\n")
                print("==> runner exit {}".format(runner_process.returncode), flush=True)
                print("==> assertions: {}".format(count if count is not None else "missing"),
                      flush=True)
                print("artifacts: " + artifacts, flush=True)

                result, message = decide_runner_exit(runner_process.returncode, count)
                if result != 0:
                    print("ERROR: " + message, file=sys.stderr)
    finally:
        if runner_process is not None:
            kill_tree(runner_process, "runner")
        server_log.flush()
        server_log.close()
        kill_tree(process, "server")
        if process.poll() is not None:
            print("==> server pid={} reaped exit={}".format(process.pid, process.returncode),
                  flush=True)
        # A child that survives cleanup is an orphan: the run cannot pass.
        orphans = survivors([("runner", runner_process), ("server", process)])
        if orphans:
            print("ERROR: orphan process(es) survived cleanup: " + ", ".join(orphans),
                  file=sys.stderr)
            result = 1
    return result


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", default=os.environ.get("P1_CLIENT_ROOT", CLIENT_ROOT))
    parser.add_argument("--server-root", default=os.environ.get("P1_SERVER_ROOT", CLIENT_ROOT))
    parser.add_argument("--server-head", default=os.environ.get("P1_SERVER_HEAD"))
    parser.add_argument("--client-head", default=os.environ.get("P1_CLIENT_HEAD"))
    parser.add_argument("--content-root", default=os.environ.get("P1_CONTENT_ROOT"))
    parser.add_argument("--contract-pin",
                        default=os.environ.get("P1_CONTRACT_PIN"),
                        help="path to qoder-contract-pins.json; when given, every "
                             "contract byte at the server root must match its pinned SHA-256")
    parser.add_argument("--mode", choices=sorted(MODES), default=os.environ.get("P1_ALPHA_MODE", "gates-off"))
    parser.add_argument("--artifacts-root",
                        default=os.environ.get("P1_ARTIFACTS_ROOT",
                                              os.path.join(CLIENT_ROOT, "TestResults", "clientcore-http")))
    args = parser.parse_args(argv)
    args.client_root = os.path.abspath(args.client_root)
    args.server_root = os.path.abspath(args.server_root)
    args.content_root = os.path.abspath(args.content_root or args.server_root)
    args.artifacts_root = os.path.abspath(args.artifacts_root)
    if args.contract_pin:
        args.contract_pin = os.path.abspath(args.contract_pin)
    return args


def main(argv=None):
    args = parse_args(argv)
    os.makedirs(args.artifacts_root, exist_ok=True)
    modes = [args.mode]
    results = []
    for mode in modes:
        print("=" * 72, flush=True)
        print("MODE " + mode, flush=True)
        print("=" * 72, flush=True)
        code = run_mode(args, mode)
        results.append((mode, code))
        if code != 0:
            break
    summary = ["mode={} exit={}".format(mode, code) for mode, code in results]
    write_summary(args.artifacts_root, summary)
    for line in summary:
        print("==> " + line, flush=True)
    return 0 if all(code == 0 for _, code in results) and len(results) == len(modes) else (
        results[-1][1] if results else 1)


if __name__ == "__main__":
    sys.exit(main())
