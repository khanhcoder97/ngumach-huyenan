"""Local browser playtest, Python standard library only; no production accounts or rewards."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import webbrowser

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIO = ROOT / "Client/Assets/Audio/PackV1"


class Handler(SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_error(405)

    def do_GET(self):
        requested = unquote(urlsplit(self.path).path)
        if requested == "/api/info":
            body = json.dumps(dict(game="Ngũ Mạch: Huyền Ấn", mode="LOCAL_SINGLE_PLAYER_PLAYTEST", version=1), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        base = AUDIO if requested.startswith("/audio/") else HERE
        relative = requested.removeprefix("/audio/") if base == AUDIO else requested.lstrip("/") or "index.html"
        target = (base / relative).resolve()
        if not target.is_relative_to(base.resolve()) or not target.is_file():
            self.send_error(404)
            return
        allowed = {".ogg", ".wav"} if base == AUDIO else {".html", ".css", ".mjs", ".json", ".png"}
        if target.suffix not in allowed or target.name.startswith("."):
            self.send_error(404)
            return
        self.send_response(200)
        mime = "text/javascript" if target.suffix == ".mjs" else self.guess_type(str(target))
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(target.stat().st_size))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        try:
            with target.open("rb") as stream:
                self.copyfile(stream, self.wfile)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, fmt, *args):
        if "404" in str(args):
            super().log_message(fmt, *args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8090)
    parser.add_argument("--open", action="store_true")
    args = parser.parse_args()
    if not (HERE / "content.json").is_file():
        raise SystemExit("Missing packaged content. Run prepare_content.py first.")
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        raise SystemExit(f"Port {args.port} is in use; try --port 8091.")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"Ngũ Mạch — Bến Mưa local playtest: {url}", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
