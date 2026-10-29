"""Package existing Muse candidate sprites and edited opening dialogue for local playtesting."""
import csv
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
MUSE = "497702ec0e7d3f9167466007b90877e901a4c95c"


def build():
    assets = HERE / "assets"
    assets.mkdir(exist_ok=True)
    sprites = {}
    for name in ("idle", "walk", "attack1", "attack2", "attack3", "skill1", "skill2", "skill3", "dodge", "hurt", "death"):
        source = f"Client/Assets/Art/Characters/MinhKiem/minh_kiem_{name}.png"
        data = subprocess.check_output(["git", "show", f"{MUSE}:{source}"], cwd=ROOT)
        if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
            data = subprocess.check_output(["git", "lfs", "smudge", "--", source], input=data, cwd=ROOT)
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError(f"Fetch actual PNG/LFS object before packaging: {source}")
        width, height = struct.unpack_from(">II", data, 16)
        if width % 48 or height != 512:
            raise ValueError(f"Unexpected sprite geometry: {source} {width}x{height}")
        target = assets / f"{name}.png"
        target.write_bytes(data)
        sprites[name] = dict(url=f"assets/{name}.png", columns=width // 48, rows=8,
                             cellWidth=48, cellHeight=64, fps=8 if name == "walk" else 12,
                             source=source, sourceCommit=MUSE, sha256=hashlib.sha256(data).hexdigest(),
                             approval="MUSE_CANDIDATE_LOCAL_PLAYTEST_ONLY")
    with (ROOT / "docs/production/Quest_Dialogue_Production_Data_vi.csv").open(encoding="utf-8-sig", newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["quest_id"].startswith("P00-")]
    dialogue = [{k: r[k] for k in ("quest_id", "quest_title_vi", "node_type", "speaker_id", "text_key", "text_vi")} for r in rows]
    content = dict(version="ben-mua-local-v1", mode="LOCAL_SINGLE_PLAYER_PLAYTEST",
                   artStatus="Hero: Muse candidate; terrain/mobs: original procedural blockout",
                   directions=["N", "NE", "E", "SE", "S", "SW", "W", "NW"], sprites=sprites,
                   dialogue=dialogue,
                   sources=["docs/production/Quest_and_Narrative_Production_Spec_vi.md",
                            "docs/production/Map_Production_Atlas_vi.md",
                            "docs/production/P1_Guard_Precision_20261030_vi.md"],
                   tuningNote="Local ordinary mobs use a chosen level1 onboarding profile; boss HP640/ATK20/DEF6, potion/weapon and compact playable topology are fixtures, not production balance or reviewed topology.")
    (HERE / "content.json").write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(sprites)} candidate sheets and {len(dialogue)} canonical opening dialogue lines")


if __name__ == "__main__":
    build()
