"""Optional local audition only. Serves the player/audio, not the rest of the workspace."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT=Path(__file__).resolve().parents[2]


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def do_GET(self):
        path=unquote(urlsplit(self.path).path)
        if path=='/':self.send_response(302);self.send_header('Location','/Tools/AudioProduction/player.html');self.end_headers();return
        try:
            file=(ROOT/path.lstrip('/')).resolve();file.relative_to(ROOT)
            allowed=(path=='/Tools/AudioProduction/player.html' or path.startswith('/Client/Assets/Audio/PackV1/') or path.startswith('/Art_Source/Audio/Previews/'))
            if not allowed or not file.is_file() or '..' in Path(path).parts:raise ValueError()
        except ValueError:self.send_error(404);return
        return super().do_GET()
    def do_HEAD(self):
        # HEAD uses the same whitelist; no directory listing or arbitrary workspace reads.
        path=unquote(urlsplit(self.path).path)
        try:
            file=(ROOT/path.lstrip('/')).resolve();file.relative_to(ROOT)
            if not file.is_file() or not (path=='/Tools/AudioProduction/player.html' or path.startswith('/Client/Assets/Audio/PackV1/') or path.startswith('/Art_Source/Audio/Previews/')):raise ValueError()
        except ValueError:self.send_error(404);return
        return super().do_HEAD()
    def list_directory(self,path):self.send_error(404);return None


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8078);a=p.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
    print(f'Audio audition: http://127.0.0.1:{a.port}/',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
