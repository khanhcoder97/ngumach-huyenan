"""Loopback-only reading room. Serves only six explicit files, no game/API access."""
import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
ROUTES={'/':('index.html','text/html; charset=utf-8'),'/styles.css':('styles.css','text/css; charset=utf-8'),'/app.js':('app.js','application/javascript; charset=utf-8'),'/story.json':('ben_mua.preview.json','application/json; charset=utf-8'),'/manifest.json':('scene_manifest.json','application/json; charset=utf-8'),'/ink.js':('node_modules/inkjs/dist/ink.js','application/javascript; charset=utf-8')}
ROUTES['/gameplay-catalog.json']=('../../Client/Assets/Resources/Narrative/dialogue_vi.json','application/json; charset=utf-8')
class Handler(BaseHTTPRequestHandler):
 def do_GET(self):self.serve(False)
 def do_HEAD(self):self.serve(True)
 def serve(self,head):
  spec=ROUTES.get(urlsplit(self.path).path)
  if spec is None:self.send_error(404);return
  file=ROOT/spec[0]
  if not file.is_file():self.send_error(503,'Run npm ci and npm run build first');return
  data=file.read_bytes();self.send_response(200)
  self.send_header('Content-Type',spec[1]);self.send_header('Content-Length',str(len(data)))
  self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; object-src 'none'; frame-ancestors 'none'")
  self.end_headers()
  if not head:self.wfile.write(data)
 def log_message(self,*args):pass
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--port',type=int,default=8126);a=p.parse_args()
 if not 0<=a.port<=65535:p.error('Invalid port')
 server=ThreadingHTTPServer(('127.0.0.1',a.port),Handler)
 print(f'READING_ROOM=http://127.0.0.1:{server.server_port}',flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
