"""Boundary tests for the media-only gate, including git rename/delete paths."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from check_agent_scope import violations

ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT/"Implementation/Coordination/agent_scope_v2.json").read_text(encoding="utf-8"))

class ScopeTests(unittest.TestCase):
    def test_media_bundle_allowed(self):
        self.assertEqual([], violations(["Art_Source/Cinematics/cin006/storyboard.png",
            "ClientGodot/assets/audio/rain.ogg",
            "Implementation/Content/Narrative/Deliveries/opening.srt",
            "Tools/MediaProduction/Muse/check_media.py"],"muse/media-production-20261104",POLICY))
    def test_graphics_and_runtime_blocked(self):
        for path in ["ClientGodot/scripts/Main.cs","ClientGodot/assets/hud/attack.png",
            "Art_Source/Visual_Reboot_20261104/hero.png",
            "ClientGodot/assets/audio/inject.cs","Tools/MediaProduction/Muse/build.yml"]:
            self.assertTrue(violations([path],"muse/media-test",POLICY),path)
    def test_traversal_and_frozen(self):
        self.assertTrue(violations(["Art_Source/Cinematics/../../secret.txt"],"muse/media-test",POLICY))
        self.assertTrue(violations(["Art_Source/Cinematics/a.md"],"muse/engine-dec-024",POLICY))
        self.assertEqual([],violations(["ClientGodot/scripts/Main.cs"],"codex/art-takeover-20261104",POLICY))
    def test_no_rename_hiding(self):
        with tempfile.TemporaryDirectory() as temp:
            def git(*args):
                return subprocess.check_output(["git","-C",temp,*args],text=True).strip()
            git("init","-q")
            git("config","user.name","Scope Test")
            git("config","user.email","scope@example.invalid")
            old=Path(temp)/"ClientGodot/assets/hud/attack.png"
            old.parent.mkdir(parents=True); old.write_text("dummy")
            git("add","."); git("commit","-qm","base"); base=git("rev-parse","HEAD")
            new=Path(temp)/"Art_Source/Cinematics/poster.png"
            new.parent.mkdir(parents=True); old.rename(new)
            git("add","-A"); git("commit","-qm","rename")
            paths=git("diff","--no-renames","--name-only",base,"HEAD").splitlines()
            self.assertIn("ClientGodot/assets/hud/attack.png",paths)
            self.assertTrue(violations(paths,"muse/media-test",POLICY))

if __name__ == "__main__":
    unittest.main()
