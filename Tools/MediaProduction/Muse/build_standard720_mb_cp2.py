#!/usr/bin/env python3
"""WO37 M-B CP2 — standard 720p versions of the 21 playback cinematics.

Method (disclosed, not hidden): every committed picture source for these
cinematics is 640x360 native (P0 + campaign keyframes are 640x360 PNG).
The standard version is therefore an exact INTEGER 2x upscale
(ffmpeg scale flags=neighbor) of the delivered 640x360 runtime master,
which matches the project's own integer-scale display doctrine
(docs/production: integer scale, no blur/bleed). It is NOT a native
720p capture and is never labelled as one.

Video: H.264 crf26 from the runtime MP4 (picture of record, embedded
soundtrack carried over by stream copy — the audio bytes are identical,
no re-encode). CRF choice measured 2026-11-10 on the two most complex
Ken Burns scenes (CIN_005 / CIN_003): crf16 -> 10.8-11.2x the 640 master
bytes, crf20 -> 7.3-8.1x, crf23 -> 5.3-5.8x, crf26 -> 3.8-4.1x with
downscale-back mean|diff| <= 4.20 and 2x2 intra-block range <= 6.08
(the integer structure survives essentially intact at every tested CRF;
the size is the honest cost of full-frame Ken Burns motion at 4x the
pixels — the 640 masters run at only ~535 kbps video). Output lives under Art_Source/Cinematics/Standard720/
(review/standard masters); the ClientGodot runtime tree is NOT touched
— adoption into runtime stays Codex's decision, same pattern as M38-B.

Three OGV samples (panel-hold CIN_001, Ken Burns CIN_003, wide CIN_019)
are rendered to measure the Theora cost of a full standard OGV set;
their audio is re-encoded AAC->Vorbis 160k from the embedded track
(a full adopted set should be rendered from the mix WAV masters,
per the M38-B recipe — noted in the manifest).
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = ROOT / "Art_Source/Cinematics/Standard720"
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP2_v1.json"
SCENES = ["CIN_000"] + [f"CIN_{i:03d}" for i in range(1, 21)]
OGV_SAMPLES = ["CIN_001", "CIN_003", "CIN_019"]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    return {"width": v["width"], "height": v["height"], "fps": v["r_frame_rate"],
            "videoCodec": v["codec_name"], "hasAudio": bool(a),
            "audioCodec": a[0]["codec_name"] if a else None,
            "duration": float(d["format"]["duration"])}


def lfs_oid(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("oid sha256:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    entries = []
    for scene in SCENES:
        src_rel = f"ClientGodot/assets/cinematics/{scene}/{scene}_640x360_30fps.mp4"
        src = ROOT / src_rel
        assert src.exists(), src
        src_sha = sha256(src)
        oid = lfs_oid(src_rel)
        assert oid == src_sha, f"{scene}: worktree bytes != git LFS oid ({src_sha} vs {oid})"
        sp = probe(src)
        out_dir = OUT_ROOT / scene
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{scene}_1280x720_30fps.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-i", str(src),
             "-vf", "scale=1280:720:flags=neighbor",
             "-c:v", "libx264", "-crf", "26", "-preset", "medium",
             "-pix_fmt", "yuv420p", "-c:a", "copy",
             "-movflags", "+faststart", str(out)], check=True)
        op = probe(out)
        e = {"sceneId": scene, "sourcePath": src_rel, "sourceSha256": src_sha,
             "sourceBytes": src.stat().st_size, "sourceDuration": sp["duration"],
             "outPath": f"Art_Source/Cinematics/Standard720/{scene}/{scene}_1280x720_30fps.mp4",
             "outSha256": sha256(out), "outBytes": out.stat().st_size,
             "outDuration": op["duration"], "outProbe": op}
        if scene in OGV_SAMPLES:
            ogv = out_dir / f"{scene}_1280x720_30fps.ogv"
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-i", str(src),
                 "-vf", "scale=1280:720:flags=neighbor",
                 "-c:v", "libtheora", "-q:v", "6",
                 "-c:a", "libvorbis", "-b:a", "160k", str(ogv)], check=True)
            gp = probe(ogv)
            e["ogvSample"] = {
                "outPath": f"Art_Source/Cinematics/Standard720/{scene}/{scene}_1280x720_30fps.ogv",
                "outSha256": sha256(ogv), "outBytes": ogv.stat().st_size,
                "outDuration": gp["duration"],
                "bytesPerSecond": ogv.stat().st_size / gp["duration"],
                "audioNote": "Vorbis re-encoded from the embedded AAC track; "
                             "an adopted full set should be rendered from the mix WAV masters"}
        entries.append(e)
        print(f"{scene}: src {e['sourceBytes']} B -> mp4 {e['outBytes']} B "
              f"({e['outBytes']/e['sourceBytes']:.2f}x)", flush=True)

    tot_src = sum(e["sourceBytes"] for e in entries)
    tot_out = sum(e["outBytes"] for e in entries)
    tot_dur = sum(e["sourceDuration"] for e in entries)
    samples = [e["ogvSample"] for e in entries if "ogvSample" in e]
    ogv_bps = [s["bytesPerSecond"] for s in samples]
    budget = {
        "mp4Set": {"files": len(entries), "sourceBytes": tot_src, "outBytes": tot_out,
                   "ratio": round(tot_out / tot_src, 3), "totalDuration": round(tot_dur, 3)},
        "ogvSamples": {"files": len(samples),
                       "bytesPerSecondMin": round(min(ogv_bps), 1),
                       "bytesPerSecondMax": round(max(ogv_bps), 1),
                       "bytesPerSecondMean": round(sum(ogv_bps) / len(ogv_bps), 1),
                       "fullSetProjectionBytes": round(
                           (sum(ogv_bps) / len(ogv_bps)) * tot_dur),
                       "projectionNote": "mean bytes/second of the 3 samples x total "
                                         "duration of the 21 entries; estimate, not a render"},
    }
    manifest = {
        "id": "STANDARD720_MB_CP2_v1",
        "checkpoint": "WO37 M-B CP2",
        "status": "DRAFT_STANDARD_VERSIONS_NOT_IN_RUNTIME",
        "method": "integer 2x nearest-neighbour upscale of the delivered 640x360 "
                  "runtime masters; all committed picture sources are 640x360 native, "
                  "so this is NOT a native 720p capture; H.264 crf26 (measured choice: "
                  "crf16 cost 9.7x total bytes for no structural gain — see report); "
                  "audio stream-copied bit-exact "
                  "from the runtime MP4 (EMBEDDED_SOUNDTRACK_ONLY preserved)",
        "baseline": "aa1cd978b98f86b574cd22704599336eb8e5eeca",
        "entries": entries,
        "budget": budget,
        "runtimeTreeModified": False,
        "notes": [
            "CIN_000 subtitled variant (CIN_000_640x360_30fps_sub_vi.mp4) is not part "
            "of the playback set and has no standard version in this checkpoint.",
            "P0 scenes carry the runtime A picture (panel-hold), same as the runtime "
            "package of record; candidate B keeps its own M38-A/B package.",
            "Adoption into ClientGodot runtime (and any full 720p OGV set) is Codex's "
            "decision; projected OGV cost is in budget.ogvSamples.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(budget, ensure_ascii=False, indent=1))
    print("manifest:", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
