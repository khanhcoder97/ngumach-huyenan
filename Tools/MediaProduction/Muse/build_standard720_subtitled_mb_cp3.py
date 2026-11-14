#!/usr/bin/env python3
"""WO37 M-B CP3 — standard 720p version of the CIN_000 subtitled viewing variant.

Closes the gap named in the M-B CP2 report ("CIN_000's subtitled variant
is not part of the playback set and has no standard version here").

Method (same measured recipe as CP2, disclosed not hidden): the subtitled
variant CIN_000_640x360_30fps_sub_vi.mp4 (CP28: burned-in Vietnamese
subtitles + embedded mov_text track, narration +5.0 dB, -15.83 LUFS) is
640x360 native, so the standard version is an exact INTEGER 2x upscale
(ffmpeg scale flags=neighbor) — NOT a native 720p capture, labelled as
such in the manifest. H.264 crf26 (CP2 measured choice), preset medium;
audio stream-copied bit-exact; the embedded mov_text subtitle track is
also stream-copied (-map 0 -c:s copy) so the review variant keeps its
soft-subtitle companion. No OGV sample: CP28 records "no OGV subtitled
variant" (in-engine subtitle display belongs to the film files), so
there is no 640 OGV subtitled source to upscale.

Output lives under Art_Source/Cinematics/Standard720/CIN_000_subtitled/
(a separate folder from the 21 playback entries, so the CP2 set stays
exactly 21); the ClientGodot runtime tree is NOT touched — adoption
stays Codex's decision, same pattern as M38-B / M-B CP2.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = ROOT / "Art_Source/Cinematics/Standard720/CIN_000_subtitled"
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_MB_CP3_v1.json"
SRC_REL = "ClientGodot/assets/cinematics/CIN_000/CIN_000_640x360_30fps_sub_vi.mp4"
OUT_NAME = "CIN_000_1280x720_30fps_sub_vi.mp4"
# CP28 recorded prefix for the subtitled variant (full sha re-derived below).
CP28_SHA_PREFIX = "2aae25e4"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate:stream_tags=language",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    s = [x for x in d["streams"] if x["codec_type"] == "subtitle"]
    return {"width": v["width"], "height": v["height"], "fps": v["r_frame_rate"],
            "videoCodec": v["codec_name"], "hasAudio": bool(a),
            "audioCodec": a[0]["codec_name"] if a else None,
            "subtitle": [{"codec": x["codec_name"],
                          "language": x.get("tags", {}).get("language")}
                         for x in s],
            "duration": float(d["format"]["duration"])}


def lfs_oid(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("oid sha256:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    src = ROOT / SRC_REL
    assert src.exists(), src
    src_sha = sha256(src)
    oid = lfs_oid(SRC_REL)
    assert oid == src_sha, f"worktree bytes != git LFS oid ({src_sha} vs {oid})"
    assert src_sha.startswith(CP28_SHA_PREFIX), f"sha != CP28 record ({src_sha})"
    sp = probe(src)
    assert sp["width"] == 640 and sp["height"] == 360 and sp["fps"] == "30/1", sp
    assert sp["hasAudio"] and sp["audioCodec"] == "aac", sp
    assert len(sp["subtitle"]) == 1 and sp["subtitle"][0]["codec"] == "mov_text", sp
    print(f"source: {src_sha} {src.stat().st_size} B {sp['duration']:.3f} s {sp}")

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    out = OUT_ROOT / OUT_NAME
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src),
         "-map", "0",
         "-vf", "scale=1280:720:flags=neighbor",
         "-c:v", "libx264", "-crf", "26", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "copy",
         "-movflags", "+faststart", str(out)], check=True)
    op = probe(out)
    entry = {"sceneId": "CIN_000_subtitled", "sourcePath": SRC_REL,
             "sourceSha256": src_sha, "sourceBytes": src.stat().st_size,
             "sourceDuration": sp["duration"], "sourceProbe": sp,
             "outPath": f"Art_Source/Cinematics/Standard720/CIN_000_subtitled/{OUT_NAME}",
             "outSha256": sha256(out), "outBytes": out.stat().st_size,
             "outDuration": op["duration"], "outProbe": op}
    manifest = {
        "id": "STANDARD720_SUBTITLED_MB_CP3_v1",
        "checkpoint": "WO37 M-B CP3",
        "status": "DRAFT_STANDARD_VERSION_NOT_IN_RUNTIME",
        "method": "integer 2x nearest-neighbour upscale of the delivered 640x360 "
                  "subtitled viewing variant (CP28); NOT a native 720p capture; "
                  "H.264 crf26 (CP2 measured choice); audio stream-copied bit-exact; "
                  "embedded mov_text subtitle track stream-copied; no OGV sample "
                  "(CP28: no OGV subtitled variant exists)",
        "baseline": "c0caf221458da934800e4478711dfe3bf3a208d4",
        "entries": [entry],
        "budget": {"mp4Set": {"files": 1, "sourceBytes": entry["sourceBytes"],
                              "outBytes": entry["outBytes"],
                              "ratio": round(entry["outBytes"] / entry["sourceBytes"], 3),
                              "totalDuration": round(entry["sourceDuration"], 3)}},
        "runtimeTreeModified": False,
        "notes": [
            "Closes the gap named in the M-B CP2 report (subtitled variant had no "
            "standard version). Lives in its own CIN_000_subtitled folder so the "
            "CP2 playback set stays exactly 21 entries.",
            "Source is the CP28 viewing variant: burned-in Vietnamese subtitles "
            "(26 readable chunks) + embedded mov_text track + narration +5.0 dB "
            "(-15.83 LUFS). Canonical CP27 files unchanged.",
            "Adoption into ClientGodot runtime is Codex's decision.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"out: {entry['outSha256']} {entry['outBytes']} B "
          f"({entry['outBytes']/entry['sourceBytes']:.2f}x) {op['duration']:.3f} s")
    print("manifest:", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
