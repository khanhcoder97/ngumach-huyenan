#!/usr/bin/env python3
"""WO37 M-B CP4 — standard 720p versions re-rendered with the M-F CP2 draft v2 mixes.

What changes vs M-B CP2 (2026-11-10): the CP2 standard set stream-copied
its audio bit-exact from the 640x360 runtime masters, which still embed the
v1 mixes. M-F CP2 (2026-11-12) delivered draft v2 mixes for 14 of the 21
playback entries (new voice palette; prologue plumbing fixed, narration
History). This checkpoint re-renders exactly those 14 entries so the
standard review set carries the CURRENT draft mixes. The other 7 entries
(CIN_001/003/004/005/007/009/019) have no v2 mix — their v1 audio is
unchanged — so their CP2 files are carried over untouched (verified via
their committed LFS oids, not re-rendered, not re-downloaded).

Method (disclosed, same as CP2 for picture): integer 2x nearest-neighbour
upscale of the delivered 640x360 runtime master (picture of record;
P0 scenes keep the runtime A picture, candidate B keeps its own M38-A/B
package). Video: H.264 crf26 preset medium, yuv420p, +faststart — the
measured CP2 choice. Audio: from the v2 mix WAV master, encoded AAC 192k
48 kHz stereo to match the nominal bitrate of the v1 embedded AAC track
(runtime masters probe ~192 kbps); it is a re-encode, NOT a stream copy,
so the checker verifies it by measurement (loudnorm + lag-tolerant waveform
correlation vs the v2 WAV) instead of byte equality.

NOT in this checkpoint: the CIN_000 subtitled variant (M-B CP3) — its
burned-in subtitles are timed to the v1 narration; re-muxing v2 audio
under them would misalign subtitles vs narration. Re-timing subtitles to
the v2 narration is a separate follow-up. No OGV re-render: the 3 CP2 OGV
samples are all v1-only scenes (CIN_001/003/019); the full OGV standard
set stays deferred per Gói 39 (Codex budget decision).

Output lives under Art_Source/Cinematics/Standard720/ (review/standard
masters, in place — same filenames as CP2, supersedes recorded per entry
in the manifest). The ClientGodot runtime tree is NOT touched; adoption
stays Codex's decision, same pattern as M38-B.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_ROOT = ROOT / "Art_Source/Cinematics/Standard720"
MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP4_v1.json"
CP2_MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP2_v1.json"
MF_CP2_VALIDATION = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json"

# Scenes with a v2 mix, in playback order, with their mix version label.
SCENES_V2 = ["CIN_000", "CIN_002", "CIN_006", "CIN_008", "CIN_010", "CIN_011",
             "CIN_012", "CIN_013", "CIN_014", "CIN_015", "CIN_016", "CIN_017",
             "CIN_018", "CIN_020"]
ALL_SCENES = ["CIN_000"] + [f"CIN_{i:03d}" for i in range(1, 21)]
AAC_BITRATE = "192k"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(p: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,bit_rate",
         "-show_entries", "format=duration", "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video"), None)
    a = [s for s in d["streams"] if s["codec_type"] == "audio"]
    return {"width": v["width"] if v else None, "height": v["height"] if v else None,
            "fps": v["r_frame_rate"] if v else None,
            "videoCodec": v["codec_name"] if v else None, "hasAudio": bool(a),
            "audioCodec": a[0]["codec_name"] if a else None,
            "audioBitRate": int(a[0]["bit_rate"]) if a and a[0].get("bit_rate") else None,
            "duration": float(d["format"]["duration"])}


def lfs_oid(rel: str) -> str | None:
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                       capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if line.startswith("oid sha256:"):
            return line.split(":", 1)[1].strip()
    return None


def main() -> int:
    cp2 = json.loads(CP2_MANIFEST.read_text(encoding="utf-8"))
    cp2_by_scene = {e["sceneId"]: e for e in cp2["entries"]}
    mf2 = json.loads(MF_CP2_VALIDATION.read_text(encoding="utf-8"))
    assert mf2["status"] == "PASS" and mf2["checksPassed"] == mf2["checksTotal"] == 369, \
        "M-F CP2 validation must be PASS 369/369"
    mix_by_scene = {m["scene"]: m for m in mf2["mixes"]}
    assert set(mix_by_scene) == set(SCENES_V2), \
        f"v2 mix scenes {sorted(mix_by_scene)} != {sorted(SCENES_V2)}"

    entries = []
    for scene in ALL_SCENES:
        cp2e = cp2_by_scene[scene]
        if scene not in SCENES_V2:
            carried = dict(cp2e)
            carried["carriedOverFrom"] = "STANDARD720_MB_CP2_v1"
            carried["audioVersion"] = "DRAFT_V1 (unchanged — no v2 mix for this scene)"
            entries.append(carried)
            print(f"{scene}: carried over from CP2 (v1 audio unchanged)", flush=True)
            continue

        mix = mix_by_scene[scene]
        src_rel = f"ClientGodot/assets/cinematics/{scene}/{scene}_640x360_30fps.mp4"
        src = ROOT / src_rel
        assert src.exists(), src
        src_sha = sha256(src)
        assert src_sha == cp2e["sourceSha256"], f"{scene}: runtime master sha != CP2 manifest"
        assert src_sha == lfs_oid(src_rel), f"{scene}: runtime master bytes != git LFS oid"
        sp = probe(src)

        wav_rel = mix["file"]
        wav = ROOT / wav_rel
        assert wav.exists(), wav
        wav_sha = sha256(wav)
        assert wav_sha == mix["sha256"], f"{scene}: v2 mix sha != M-F CP2 validation"
        assert wav.stat().st_size == mix["sizeBytes"], f"{scene}: v2 mix size != validation"
        wp = probe(wav)
        assert abs(wp["duration"] - sp["duration"]) <= 0.05, \
            f"{scene}: v2 mix duration {wp['duration']} vs picture {sp['duration']}"
        assert abs(wp["duration"] - mix["durationSeconds"]) <= 0.01, \
            f"{scene}: v2 mix duration != validation"

        out_dir = OUT_ROOT / scene
        out_dir.mkdir(parents=True, exist_ok=True)
        out = out_dir / f"{scene}_1280x720_30fps.mp4"
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y",
             "-i", str(src), "-i", str(wav),
             "-map", "0:v:0", "-map", "1:a:0",
             "-vf", "scale=1280:720:flags=neighbor",
             "-c:v", "libx264", "-crf", "26", "-preset", "medium",
             "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", AAC_BITRATE, "-ar", "48000", "-ac", "2",
             "-movflags", "+faststart",
             "-t", f"{sp['duration']:.3f}", str(out)], check=True)
        op = probe(out)
        e = {"sceneId": scene,
             "videoSourcePath": src_rel, "videoSourceSha256": src_sha,
             "videoSourceBytes": src.stat().st_size,
             "sourceDuration": sp["duration"],
             "audioSourcePath": wav_rel, "audioSourceSha256": wav_sha,
             "audioSourceBytes": wav.stat().st_size,
             "audioSourceDuration": wp["duration"],
             "audioSourceIntegratedLUFS": mix["integratedLUFS"],
             "audioSourceTruePeakDBTP": mix["truePeakDBTP"],
             "audioVersion": ("P0_DRAFT_V4" if scene == "CIN_002" else "DRAFT_V2"),
             "audioEncode": f"AAC {AAC_BITRATE} 48kHz stereo (re-encode from v2 mix WAV)",
             "supersedesCp2OutSha256": cp2e["outSha256"],
             "outPath": f"Art_Source/Cinematics/Standard720/{scene}/{scene}_1280x720_30fps.mp4",
             "outSha256": sha256(out), "outBytes": out.stat().st_size,
             "outDuration": op["duration"], "outProbe": op}
        entries.append(e)
        print(f"{scene}: src {e['videoSourceBytes']} B + v2 mix -> mp4 {e['outBytes']} B "
              f"({e['outBytes']/e['videoSourceBytes']:.2f}x) "
              f"LUFS {mix['integratedLUFS']} TP {mix['truePeakDBTP']}", flush=True)

    new_entries = [e for e in entries if "supersedesCp2OutSha256" in e]
    tot_src = sum(e["videoSourceBytes"] if "videoSourceBytes" in e else e["sourceBytes"]
                  for e in entries)
    tot_out = sum(e["outBytes"] for e in entries)
    tot_dur = sum(e["sourceDuration"] for e in entries)
    cp2_total = cp2["budget"]["mp4Set"]["outBytes"]
    budget = {
        "mp4Set": {"files": len(entries), "sourceBytes": tot_src, "outBytes": tot_out,
                   "ratio": round(tot_out / tot_src, 3),
                   "totalDuration": round(tot_dur, 3)},
        "v2Rerendered": {"files": len(new_entries),
                         "outBytes": sum(e["outBytes"] for e in new_entries),
                         "cp2OutBytes": sum(cp2_by_scene[e["sceneId"]]["outBytes"]
                                            for e in new_entries)},
        "deltaVsCp2SetBytes": tot_out - cp2_total,
        "carriedOver": {"files": len(entries) - len(new_entries),
                        "note": "CP2 files untouched; verified via committed LFS oids, "
                                "not re-rendered"},
    }
    manifest = {
        "id": "STANDARD720_MB_CP4_v1",
        "checkpoint": "WO37 M-B CP4",
        "status": "DRAFT_STANDARD_VERSIONS_NOT_IN_RUNTIME",
        "method": "integer 2x nearest-neighbour upscale of the delivered 640x360 "
                  "runtime masters (picture of record, same as CP2); video H.264 crf26 "
                  "preset medium; audio for the 14 re-rendered entries is the M-F CP2 "
                  "draft v2 mix WAV re-encoded AAC 192k 48kHz stereo (NOT a stream copy "
                  "— the runtime masters still embed v1 mixes); the 7 entries without "
                  "a v2 mix keep their CP2 files byte-identical. NOT a native 720p capture.",
        "baseline": "7f461da",
        "supersedes": "STANDARD720_MB_CP2_v1 (14 entries re-rendered with v2 audio; "
                      "7 entries carried over byte-identical)",
        "entries": entries,
        "budget": budget,
        "runtimeTreeModified": False,
        "notes": [
            "CIN_000 subtitled variant (M-B CP3) is NOT re-rendered here: its burned-in "
            "subtitles are timed to the v1 narration; re-muxing v2 audio under them "
            "would misalign subtitles vs narration. Subtitle re-timing to the v2 "
            "narration is a separate follow-up.",
            "P0 scenes carry the runtime A picture (panel-hold), same as the runtime "
            "package of record; candidate B keeps its own M38-A/B package.",
            "No OGV re-render: the 3 CP2 OGV samples are all v1-only scenes "
            "(CIN_001/003/019); the full OGV standard set stays deferred per Gói 39 "
            "(Codex budget decision).",
            "Adoption into ClientGodot runtime is Codex's decision.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(budget, ensure_ascii=False, indent=1))
    print("manifest:", MANIFEST.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
