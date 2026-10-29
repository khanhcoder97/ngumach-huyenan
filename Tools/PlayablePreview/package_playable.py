"""Export a standalone local playtest ZIP with only required original audio and candidate art."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def package(output):
    files = [ROOT / "CHOI_THU.cmd"]
    files.extend(HERE / name for name in ("index.html", "style.css", "game.mjs", "engine.mjs", "renderer.mjs", "server.py", "content.json", "README_vi.md"))
    files.extend(sorted((HERE / "assets").glob("*.png")))
    script = (HERE / "game.mjs").read_text(encoding="utf-8")
    clips = set(re.findall(r"sound\.play\('(sfx/[^']+\.(?:wav|ogg))'", script))
    clips.update("sfx/boss/mang_cot_" + attack + "_warning_v01.wav" for attack in ("sweep", "emerge", "bubble"))
    clips.update(("music/ben_mua.ogg", "music/boss_mang_cot.ogg", "ambience/rain_light.ogg"))
    files.extend(ROOT / "Client/Assets/Audio/PackV1" / clip for clip in sorted(clips))
    manifest = []
    for path in files:
        data = path.read_bytes()
        if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
            raise ValueError("Fetch LFS objects before packaging: " + str(path))
        manifest.append(dict(path=path.relative_to(ROOT).as_posix(), bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, path.relative_to(ROOT).as_posix())
        archive.writestr("PLAYTEST_MANIFEST.json", json.dumps(dict(mode="LOCAL_SINGLE_PLAYER_PLAYTEST", files=manifest), ensure_ascii=False, indent=2))
    print(json.dumps(dict(zip=str(output), files=len(files), audioClips=len(clips), bytes=output.stat().st_size), ensure_ascii=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    package(parser.parse_args().output.resolve())
