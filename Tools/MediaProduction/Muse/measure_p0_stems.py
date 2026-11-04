#!/usr/bin/env python3
"""Re-measure the MEDIA-02 P0 stem pool (11 files) from real bytes.

Reads files under Client/Assets/Audio/PackV1/ in the repo checkout,
runs ffprobe (codec/duration/size) and ffmpeg loudnorm (measured
integrated loudness / true peak / LRA, no normalization), and prints
one JSON object with the same shape as
Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_02_P0_STEMS_20261105.json
(stems list only). Files must be real bytes (git lfs pull), not LFS
pointers; a pointer file fails the ffprobe step instead of yielding a
fake measurement.
Usage: python3 Tools/MediaProduction/Muse/measure_p0_stems.py [repo-root]
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

FILES = [
    "Client/Assets/Audio/PackV1/sfx/cinema/reveal_v01.wav",
    "Client/Assets/Audio/PackV1/sfx/cinema/tension_v01.wav",
    "Client/Assets/Audio/PackV1/sfx/cinema/resolve_v01.wav",
    "Client/Assets/Audio/PackV1/sfx/cinema/transition_v01.wav",
    "Client/Assets/Audio/PackV1/music/ben_mua.ogg",
    "Client/Assets/Audio/PackV1/music/boss_mang_cot.ogg",
    "Client/Assets/Audio/PackV1/music/quiet_discovery.ogg",
    "Client/Assets/Audio/PackV1/ambience/rain_light.ogg",
    "Client/Assets/Audio/PackV1/ambience/river_shore.ogg",
    "Client/Assets/Audio/PackV1/ambience/underwater.ogg",
    "Client/Assets/Audio/PackV1/ambience/rain_heavy.ogg",
]


def probe(root: Path, rel: str) -> dict:
    p = root / rel
    data = p.read_bytes()
    if data.startswith(b"version https://git-lfs"):
        raise SystemExit(f"LFS pointer, not real bytes: {rel}")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries", "stream=codec_name,sample_rate,channels",
         "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    stream = j["streams"][0]
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    loud = json.loads("{" + err.split("{", 1)[1].rsplit("}", 1)[0] + "}")
    return {
        "path": rel,
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": float(j["format"]["duration"]),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": float(loud["input_i"]),
        "true_peak_dbtp": float(loud["input_tp"]),
        "lra_lu": float(loud["input_lra"]),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    print(json.dumps({"stems": [probe(root, f) for f in FILES]}, indent=1))


if __name__ == "__main__":
    main()
