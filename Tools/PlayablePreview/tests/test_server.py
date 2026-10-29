import importlib.util
import json
from pathlib import Path
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import urlopen

HERE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("playable_server", HERE / "server.py")
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


class ServerChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join(timeout=5)
        cls.server.server_close()

    def read(self, path):
        with urlopen(f"http://127.0.0.1:{self.server.server_port}" + path, timeout=5) as response:
            return response.headers, response.read()

    def test_page_and_javascript(self):
        headers, body = self.read("/")
        self.assertIn(b'lang="vi"', body)
        headers, body = self.read("/engine.mjs")
        self.assertEqual("text/javascript", headers["Content-Type"])
        self.assertIn(b"export class Game", body)

    def test_packaged_assets_have_real_pngs_and_expected_geometry(self):
        _, data = self.read("/content.json")
        content = json.loads(data)
        self.assertEqual("LOCAL_SINGLE_PLAYER_PLAYTEST", content["mode"])
        self.assertEqual(11, len(content["sprites"]))
        for sprite in content["sprites"].values():
            _, image = self.read("/" + sprite["url"])
            self.assertTrue(image.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(8, sprite["rows"])
        self.assertEqual(15, len(content["dialogue"]))

    def test_info_is_local_not_online_mmo(self):
        _, data = self.read("/api/info")
        self.assertEqual("LOCAL_SINGLE_PLAYER_PLAYTEST", json.loads(data)["mode"])

    def test_traversal_and_source_files_are_not_served(self):
        for path in ("/../README.md", "/%2e%2e/%2e%2e/README.md", "/server.py", "/.git/config", "/audio/../catalog.json", "/assets/idle.png.meta"):
            with self.assertRaises(HTTPError) as caught:
                self.read(path)
            self.assertEqual(404, caught.exception.code)
            caught.exception.close()


if __name__ == "__main__":
    unittest.main()
