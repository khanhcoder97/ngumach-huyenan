#!/usr/bin/env python3
"""Measure the MEDIA-02 M4/M5 music + ambience pack from real bytes.

Reads Client/Assets/AudioManifests/game_audio_v1.json, takes the 9 Music
and 13 Ambience cues, and measures BOTH the runtime OGG (clipPath) and
the FLAC master (Art_Source/Audio/Masters/<bus>/<stem>.flac) with
ffprobe (codec/duration/sample rate/channels/size) and ffmpeg loudnorm
(integrated LUFS / true peak / LRA, measurement only, no normalization).

Loop-seam indicator (measurement only, NOT a seamlessness PASS): the
file is decoded once to mono f32, then RMS of the first and last 100 ms
and the wrap jump |last sample - first sample| are reported. A loop
still needs an ear check before it is called seamless.

Files must be real bytes (git lfs pull), not LFS pointers; a pointer
fails loudly instead of yielding a fake measurement.
Usage: python3 Tools/MediaProduction/Muse/measure_music_ambience.py
       [repo-root] [out-json]
Defaults: repo-root = cwd, out-json =
  Implementation/Content/Audio/Deliveries/MUSIC_AMBIENCE_pack_v1.json
"""
import hashlib
import json
import struct
import subprocess
import sys
from pathlib import Path

MANIFEST = "Client/Assets/AudioManifests/game_audio_v1.json"


def is_pointer(p: Path) -> bool:
    return p.read_bytes()[:40].startswith(b"version https://git-lfs")


def probe(p: Path) -> dict:
    if is_pointer(p):
        raise SystemExit(f"LFS pointer, not real bytes: {p}")
    data = p.read_bytes()
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,sample_rate,channels",
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
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": round(float(j["format"]["duration"]), 4),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": float(loud["input_i"]),
        "true_peak_dbtp": float(loud["input_tp"]),
        "lra_lu": float(loud["input_lra"]),
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def seam(p: Path) -> dict:
    """Head/tail RMS + wrap jump on a mono 48 kHz f32 decode."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le",
         "-ac", "1", "-ar", "48000", "-"],
        capture_output=True, check=True).stdout
    n = len(raw) // 4
    samples = struct.unpack(f"<{n}f", raw)
    win = 4800  # 100 ms at 48 kHz
    head = samples[:win]
    tail = samples[-win:]

    def rms(xs):
        return (sum(x * x for x in xs) / len(xs)) ** 0.5

    return {
        "method": "mono 48kHz f32 decode; head/tail = first/last 100 ms; "
                  "wrap jump = |last sample - first sample|; indicator only, "
                  "not a seamlessness PASS",
        "head_rms": round(rms(head), 6),
        "tail_rms": round(rms(tail), 6),
        "wrap_jump": round(abs(samples[-1] - samples[0]), 6),
    }


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        root / "Implementation/Content/Audio/Deliveries"
        / "MUSIC_AMBIENCE_pack_v1.json")
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    cues = [c for c in manifest["cues"] if c["bus"] in ("Music", "Ambience")]
    assert len(cues) == 22, f"expected 22 music+ambience cues, got {len(cues)}"
    assert sum(1 for c in cues if c["bus"] == "Music") == 9
    assert sum(1 for c in cues if c["bus"] == "Ambience") == 13
    # Map bindings: which mapIds use each music/ambience cue.
    map_use: dict[str, list[str]] = {}
    for m in manifest["bindings"].get("maps", []):
        for key in ("music", "ambience"):
            map_use.setdefault(m[key], []).append(m["mapId"])
    entries = []
    for c in cues:
        runtime_rel = c["clipPath"]
        stem = Path(runtime_rel).stem
        bus_dir = "music" if c["bus"] == "Music" else "ambience"
        master_rel = f"Art_Source/Audio/Masters/{bus_dir}/{stem}.flac"
        runtime = probe(root / runtime_rel)
        master = probe(root / master_rel)
        runtime["seam"] = seam(root / runtime_rel)
        entries.append({
            "cueKey": c["cueKey"],
            "nameVi": c["nameVi"],
            "bus": c["bus"],
            "loop": c["loop"],
            "gain": c["gain"],
            "priority": c["priority"],
            "voiceGroup": c["voiceGroup"],
            "assetState": c["assetState"],
            "wireStatus": c["wireStatus"],
            "sourceLicense": c["sourceLicense"],
            "sourceRef": c["sourceRef"],
            "runtime": {"path": runtime_rel, **runtime},
            "master": {"path": master_rel, **master},
            "master_minus_runtime_s": round(
                master["duration_s"] - runtime["duration_s"], 4),
            "boundToMaps": sorted(map_use.get(c["cueKey"], [])),
            "bindingState": "DESIGN_BINDING_CANDIDATE_REQUIRES_MODE_ZONE_REVIEW "
                           "(from game_audio_v1 bindings.maps; server "
                           "mode/zone context wins, not automatic "
                           "map-name activation)",
        })
    pack = {
        "packId": "NGM_MUSIC_AMBIENCE_PACK_V1",
        "checkpoint": "MEDIA-02 checkpoint 07",
        "sourceManifest": MANIFEST,
        "sourceManifestPackId": manifest["packId"],
        "sourceManifestState": manifest["state"],
        "counts": {"music": 9, "ambience": 13, "total": 22},
        "notes": [
            "Every measurement is from real bytes (git lfs pull); "
            "LFS pointers fail the tool instead of producing numbers.",
            "Per-cue loudness/true-peak only, NOT a mix PASS: no VO, "
            "no combined mix was measured here.",
            "All 22 cues are loop=True in the manifest; the seam "
            "indicator is a measurement, not a seamlessness PASS.",
            "Map bindings are DESIGN_BINDING_CANDIDATEs from the "
            "manifest; they do not auto-activate on map name.",
            "No SFX/UI cues are in this pack; those remain M5 follow-up.",
        ],
        "cues": entries,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {out} ({len(entries)} cues)")
    for e in entries:
        r, m = e["runtime"], e["master"]
        print(f"{e['cueKey']}: runtime {r['duration_s']}s "
              f"{r['integrated_lufs']} LUFS / {r['true_peak_dbtp']} dBTP | "
              f"master {m['duration_s']}s {m['integrated_lufs']} LUFS / "
              f"{m['true_peak_dbtp']} dBTP | seam wrap {r['seam']['wrap_jump']}")


if __name__ == "__main__":
    main()
