#!/usr/bin/env python3
"""Negative controls for the paired HTTP runner (OPC-17 O-A).

Every control here drives the REAL run_http.py (or its pure decision helpers)
with inputs that must NOT produce a pass, and asserts the runner refuses:

  wrong-server-head      - pinned server HEAD differs          -> exit 1
  wrong-client-head      - pinned client HEAD differs          -> exit 1
  contract-pin-mismatch  - contract bytes differ from manifest -> exit 1
  contract-pin-unreadable- manifest missing/unparseable        -> exit 1
  content-root-missing   - content root does not exist         -> exit 1
  server-not-healthy     - a listener that never reports the
                           server identity on /health          -> exit 1
  decision-helpers       - decide_runner_exit / verify_contract_pin /
                           survivors called directly with hostile inputs

No control fakes a success: each one is a real process run (or a real call on
the real helper) whose expected outcome is a refusal. Exit 0 only when every
control refused as required; any control that slipped through exits 1.

Artifacts: <artifacts-root>/negative-controls/<control>/ plus summary.txt.
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
RUN_HTTP = os.path.join(HERE, "run_http.py")
CLIENT_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_MANIFEST = os.path.join(
    CLIENT_ROOT, "Shared", "ClientCore.Tests", "Fixtures", "qoder-contract-pins.json")

sys.path.insert(0, HERE)
import run_http  # noqa: E402  (same directory, real helpers under test)

RESULTS = []


def record(name, ok, detail):
    RESULTS.append((name, ok, detail))
    print("{} {}: {}".format("PASS" if ok else "FAIL", name, detail), flush=True)


def run_runner(artifacts, extra_args, env=None):
    """Run run_http.py as a real subprocess; return its exit code."""
    control_dir = os.path.join(artifacts, "logs")
    os.makedirs(control_dir, exist_ok=True)
    cmd = [sys.executable, RUN_HTTP] + extra_args
    print("+ " + " ".join(cmd), flush=True)
    completed = subprocess.run(
        cmd, cwd=CLIENT_ROOT, env=env, capture_output=True, text=True, timeout=900)
    name = os.path.basename(artifacts)
    with open(os.path.join(control_dir, name + ".stdout.txt"), "w", encoding="utf-8") as stream:
        stream.write(completed.stdout)
    with open(os.path.join(control_dir, name + ".stderr.txt"), "w", encoding="utf-8") as stream:
        stream.write(completed.stderr)
    return completed.returncode


def control_wrong_server_head(args, root):
    code = run_runner(os.path.join(root, "wrong-server-head"), [
        "--client-root", args.client_root,
        "--server-root", args.server_root,
        "--server-head", "0" * 40,
        "--artifacts-root", os.path.join(root, "wrong-server-head", "out"),
    ])
    record("wrong-server-head", code == 1,
           "exit {} (expected 1)".format(code))


def control_wrong_client_head(args, root):
    code = run_runner(os.path.join(root, "wrong-client-head"), [
        "--client-root", args.client_root,
        "--server-root", args.server_root,
        "--client-head", "0" * 40,
        "--artifacts-root", os.path.join(root, "wrong-client-head", "out"),
    ])
    record("wrong-client-head", code == 1,
           "exit {} (expected 1)".format(code))


def control_contract_pin_mismatch(args, root):
    # Real manifest, one digest flipped: the bytes at the server root no longer
    # match the pin, so verification must refuse before anything is built.
    with open(args.contract_pin, "r", encoding="utf-8") as stream:
        manifest = json.load(stream)
    entry = manifest["files"][0]
    entry["sha256"] = "0" * 64
    broken = os.path.join(root, "contract-pin-mismatch", "qoder-contract-pins.broken.json")
    os.makedirs(os.path.dirname(broken), exist_ok=True)
    with open(broken, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream)
    code = run_runner(os.path.join(root, "contract-pin-mismatch"), [
        "--client-root", args.client_root,
        "--server-root", args.server_root,
        "--contract-pin", broken,
        "--artifacts-root", os.path.join(root, "contract-pin-mismatch", "out"),
    ])
    record("contract-pin-mismatch", code == 1,
           "exit {} (expected 1)".format(code))


def control_contract_pin_unreadable(args, root):
    missing = os.path.join(root, "contract-pin-unreadable", "no-such-manifest.json")
    code = run_runner(os.path.join(root, "contract-pin-unreadable"), [
        "--client-root", args.client_root,
        "--server-root", args.server_root,
        "--contract-pin", missing,
        "--artifacts-root", os.path.join(root, "contract-pin-unreadable", "out"),
    ])
    record("contract-pin-unreadable", code == 1,
           "exit {} (expected 1)".format(code))


def control_content_root_missing(args, root):
    ghost = os.path.join(root, "content-root-missing", "no-such-content")
    code = run_runner(os.path.join(root, "content-root-missing"), [
        "--client-root", args.client_root,
        "--server-root", args.server_root,
        "--content-root", ghost,
        "--artifacts-root", os.path.join(root, "content-root-missing", "out"),
    ])
    record("content-root-missing", code == 1,
           "exit {} (expected 1)".format(code))


class _IdentityStub:
    """Loopback HTTP listener that answers /health 200 without the identity."""

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("127.0.0.1", 0))
        self.port = self.sock.getsockname()[1]
        self.sock.listen(8)
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self):
        while not self.stop.is_set():
            try:
                conn, _ = self.sock.accept()
            except OSError:
                return
            try:
                conn.recv(4096)
                conn.sendall(
                    b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                    b"Content-Length: 16\r\nConnection: close\r\n\r\n{\"status\":\"ok\"}")
            except OSError:
                pass
            finally:
                try:
                    conn.close()
                except OSError:
                    pass

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.stop.set()
        try:
            self.sock.close()
        except OSError:
            pass
        self.thread.join(timeout=5)


def control_server_not_healthy(args, root):
    # The server never reports SERVER_IDENTITY, so the health gate must fail.
    # P1_HEALTH_TIMEOUT_SECONDS keeps the wait bounded; E2E_PORT points the
    # runner at the stub instead of a free port.
    with _IdentityStub() as stub:
        env = os.environ.copy()
        env["E2E_PORT"] = str(stub.port)
        env["P1_HEALTH_TIMEOUT_SECONDS"] = "5"
        code = run_runner(os.path.join(root, "server-not-healthy"), [
            "--client-root", args.client_root,
            "--server-root", args.server_root,
            "--content-root", args.content_root,
            "--artifacts-root", os.path.join(root, "server-not-healthy", "out"),
        ], env=env)
    record("server-not-healthy", code == 1,
           "exit {} (expected 1)".format(code))


def control_decision_helpers(args, root):
    # decide_runner_exit: zero/absent assertions and non-zero runner exits
    # must never become 0.
    cases = [
        ((0, 0), 1), ((0, None), 1), ((0, -5), 1),
        ((1, 42), 1), ((2, 42), 2), ((3, 42), 1),
        ((0, 42), 0),
    ]
    bad = []
    for (returncode, count), expected in cases:
        got, _ = run_http.decide_runner_exit(returncode, count)
        if got != expected:
            bad.append("decide_runner_exit({}, {}) -> {} want {}".format(
                returncode, count, got, expected))
    # verify_contract_pin on a hostile tree: mutate one byte of one vendored
    # contract copy served as a fake server root and expect a refusal.
    fake_root = os.path.join(root, "decision-helpers", "fake-server")
    real_root = args.server_root
    manifest = os.path.join(root, "decision-helpers", "manifest.json")
    os.makedirs(os.path.dirname(manifest), exist_ok=True)
    shutil.copyfile(args.contract_pin, manifest)
    source = os.path.join(real_root, "Implementation", "Contracts", "P1")
    target = os.path.join(fake_root, "Implementation", "Contracts", "P1")
    if os.path.isdir(source):
        shutil.copytree(source, target)
        victim = os.path.join(target, "TalkResponse.schema.json")
        if os.path.isfile(victim):
            with open(victim, "ab") as stream:
                stream.write(b" ")
        ok, message = run_http.verify_contract_pin(fake_root, manifest)
        if ok:
            bad.append("verify_contract_pin accepted mutated bytes: " + message)
        ok, message = run_http.verify_contract_pin(real_root, manifest)
        if not ok:
            bad.append("verify_contract_pin rejected the real pinned tree: " + message)
    else:
        bad.append("server contract tree missing at " + source)
    # survivors: a live child must be reported, a reaped one must not.
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
    try:
        if "live" not in run_http.survivors([("live", child)]):
            bad.append("survivors missed a live child")
    finally:
        child.kill()
        child.wait(timeout=10)
    if run_http.survivors([("dead", child)]):
        bad.append("survivors reported a reaped child")
    if not bad:
        ok, message = True, "all hostile helper inputs refused"
    else:
        ok, message = False, "; ".join(bad)
    record("decision-helpers", ok, message)


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client-root", default=os.environ.get("P1_CLIENT_ROOT", CLIENT_ROOT))
    parser.add_argument("--server-root", default=os.environ.get("P1_SERVER_ROOT"))
    parser.add_argument("--content-root", default=os.environ.get("P1_CONTENT_ROOT"))
    parser.add_argument("--contract-pin",
                        default=os.environ.get("P1_CONTRACT_PIN", DEFAULT_MANIFEST))
    parser.add_argument("--artifacts-root",
                        default=os.environ.get("P1_NEGATIVE_ARTIFACTS_ROOT",
                                               os.path.join(CLIENT_ROOT, "TestResults",
                                                            "clientcore-http",
                                                            "negative-controls")))
    args = parser.parse_args(argv)
    args.client_root = os.path.abspath(args.client_root)
    if not args.server_root:
        parser.error("--server-root is required (the real pinned server checkout)")
    args.server_root = os.path.abspath(args.server_root)
    args.content_root = os.path.abspath(args.content_root or args.server_root)
    args.contract_pin = os.path.abspath(args.contract_pin)
    args.artifacts_root = os.path.abspath(args.artifacts_root)
    return args


def main(argv=None):
    args = parse_args(argv)
    if not os.path.isfile(args.contract_pin):
        print("ERROR: contract manifest not found: " + args.contract_pin, file=sys.stderr)
        return 1
    if not os.path.isfile(RUN_HTTP):
        print("ERROR: run_http.py not found: " + RUN_HTTP, file=sys.stderr)
        return 1
    root = os.path.join(args.artifacts_root, "work")
    os.makedirs(root, exist_ok=True)
    controls = [
        control_wrong_server_head,
        control_wrong_client_head,
        control_contract_pin_mismatch,
        control_contract_pin_unreadable,
        control_content_root_missing,
        control_decision_helpers,
        control_server_not_healthy,
    ]
    for control in controls:
        control(args, root)
    failed = [name for name, ok, _ in RESULTS if not ok]
    summary = ["{}={}".format(name, "ok" if ok else "REFUSED-TO-REFUSE")
               for name, ok, _ in RESULTS]
    summary.append("failed={}".format(",".join(failed) if failed else "none"))
    os.makedirs(args.artifacts_root, exist_ok=True)
    with open(os.path.join(args.artifacts_root, "summary.txt"), "w", encoding="utf-8") as stream:
        stream.write("\n".join(summary) + "\n")
    shutil.rmtree(root, ignore_errors=True)
    print("==> negative controls: {}/{} refused as required".format(
        len(RESULTS) - len(failed), len(RESULTS)), flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
