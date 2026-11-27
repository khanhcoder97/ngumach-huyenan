#!/usr/bin/env python3
"""Measure the MEDIA-02 M5 SFX + UI pack from real bytes.

Reads Client/Assets/AudioManifests/game_audio_v1.json, takes the 146 SFX
and 27 UI cues (bus SFX / UI; cueKeys live under SFX/<category>/...),
and measures EVERY variant (v01/v02/v03) of every cue, BOTH the runtime
WAV (clipPath, Client/Assets/Audio/PackV1/sfx/...) and the FLAC master
(masterPath, Art_Source/Audio/Masters/sfx/...) with ffprobe
(codec/duration/sample rate/channels/size) and ffmpeg loudnorm
(integrated LUFS / true peak / LRA, measurement only, no normalization).

All 173 cues are loop=False one-shots, so there is no loop-seam
indicator here (unlike the music/ambience pack); the per-variant
manifest cross-check (sha256 + bytes + duration) is recorded instead.

Files must be real bytes (git lfs pull), not LFS pointers; a pointer
fails loudly instead of yielding a fake measurement. A sha mismatch
against the manifest is recorded on the variant and counted in the
summary, never silently overwritten.
Usage: python3 Tools/MediaProduction/Muse/measure_sfx_ui.py
       [repo-root] [out-json]
Defaults: repo-root = cwd, out-json =
  Implementation/Content/Audio/Deliveries/SFX_UI_pack_v1.json
"""
import hashlib
import json
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
    lufs = float(loud["input_i"])
    entry = {
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": round(float(j["format"]["duration"]), 4),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": lufs,
        "true_peak_dbtp": float(loud["input_tp"]),
        "lra_lu": float(loud["input_lra"]),
        "sha256": hashlib.sha256(data).hexdigest(),
    }
    if lufs == float("-inf"):
        # EBU R128 gated loudness needs a 400 ms block: clips shorter
        # than 400 ms cannot yield an integrated LUFS value (verified:
        # every -inf variant here is 0.1737-0.3726 s, every finite one
        # is >= 0.4632 s). True peak stays valid (it matches the sample
        # peak); fall back to a plain decoded RMS level, labelled as
        # dBFS RMS and NEVER as LUFS, so the JSON stays strict-JSON
        # (no -Infinity token) and the clip is not misread as silent.
        import math
        import struct
        raw = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le",
             "-ac", "1", "-ar", "48000", "-"],
            capture_output=True, check=True).stdout
        n = len(raw) // 4
        samples = struct.unpack(f"<{n}f", raw)
        rms = (sum(x * x for x in samples) / n) ** 0.5
        entry["integrated_lufs"] = None
        entry["lra_lu"] = None
        entry["loudnorm_note"] = (
            "integrated LUFS not measurable: clip shorter than the "
            "400 ms EBU R128 gating window; true peak is still valid")
        entry["short_clip_level_dbfs_rms"] = round(
            20 * math.log10(rms), 2) if rms > 0 else None
        entry["short_clip_peak_dbfs"] = round(
            20 * math.log10(max(abs(x) for x in samples)), 2)
    return entry


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else (
        root / "Implementation/Content/Audio/Deliveries"
        / "SFX_UI_pack_v1.json")
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    cues = [c for c in manifest["cues"] if c["bus"] in ("SFX", "UI")]
    assert len(cues) == 173, f"expected 173 SFX+UI cues, got {len(cues)}"
    assert sum(1 for c in cues if c["bus"] == "SFX") == 146
    assert sum(1 for c in cues if c["bus"] == "UI") == 27
    assert all(c["loop"] is False for c in cues), "expected all one-shots"
    entries = []
    sha_mismatch = []
    dur_mismatch = []
    for c in cues:
        assert len(c["clips"]) == 3, f"{c['cueKey']}: expected 3 variants"
        variants = []
        for cl in c["clips"]:
            runtime = probe(root / cl["path"])
            master = probe(root / cl["masterPath"])
            r_sha_ok = runtime["sha256"] == cl["sha256"]
            m_sha_ok = master["sha256"] == cl["masterSha256"]
            r_dur_ok = abs(runtime["duration_s"]
                           - round(cl["durationSeconds"], 4)) <= 0.001
            if not (r_sha_ok and m_sha_ok):
                sha_mismatch.append(
                    f"{c['cueKey']}/{cl['variantId']} runtime_sha={r_sha_ok} "
                    f"master_sha={m_sha_ok}")
            if not r_dur_ok:
                dur_mismatch.append(
                    f"{c['cueKey']}/{cl['variantId']} manifest="
                    f"{cl['durationSeconds']} measured="
                    f"{runtime['duration_s']}")
            variants.append({
                "variantId": cl["variantId"],
                "manifest": {
                    "bytes": cl["bytes"],
                    "duration_s": cl["durationSeconds"],
                    "sample_rate_hz": cl["sampleRate"],
                    "channels": cl["channels"],
                    "frames": cl["frames"],
                    "format": cl["format"],
                },
                "runtime": {"path": cl["path"], **runtime,
                            "sha_matches_manifest": r_sha_ok,
                            "duration_matches_manifest": r_dur_ok,
                            "bytes_match_manifest":
                                runtime["size_bytes"] == cl["bytes"]},
                "master": {"path": cl["masterPath"], **master,
                           "sha_matches_manifest": m_sha_ok},
                "master_minus_runtime_s": round(
                    master["duration_s"] - runtime["duration_s"], 4),
            })
        r_lufs = [v["runtime"]["integrated_lufs"] for v in variants
                  if v["runtime"]["integrated_lufs"] is not None]
        r_tp = [v["runtime"]["true_peak_dbtp"] for v in variants]
        r_dur = [v["runtime"]["duration_s"] for v in variants]
        n_short = sum(1 for v in variants
                      if v["runtime"]["integrated_lufs"] is None)
        entries.append({
            "cueKey": c["cueKey"],
            "category": c["cueKey"].split("/")[1],
            "nameVi": c["nameVi"],
            "bus": c["bus"],
            "loop": c["loop"],
            "gain": c["gain"],
            "priority": c["priority"],
            "voiceGroup": c["voiceGroup"],
            "maxInstances": c.get("maxInstances"),
            "minGapMs": c.get("minGapMs"),
            "spatialPolicy": c.get("spatialPolicy"),
            "triggerSemantic": c.get("triggerSemantic"),
            "skillId": c.get("skillId"),
            "classId": c.get("classId"),
            "assetState": c["assetState"],
            "wireStatus": c["wireStatus"],
            "sourceLicense": c["sourceLicense"],
            "sourceRef": c["sourceRef"],
            "summary": {
                "variants": 3,
                "variants_with_integrated_lufs": len(r_lufs),
                "variants_short_clip_lufs_not_measurable": n_short,
                "duration_s_min": min(r_dur),
                "duration_s_max": max(r_dur),
                "runtime_lufs_min": min(r_lufs) if r_lufs else None,
                "runtime_lufs_max": max(r_lufs) if r_lufs else None,
                "runtime_true_peak_max_dbtp": max(r_tp),
            },
            "variants": variants,
        })
    pack = {
        "packId": "NGM_SFX_UI_PACK_V1",
        "checkpoint": "MEDIA-02 checkpoint 08",
        "sourceManifest": MANIFEST,
        "sourceManifestPackId": manifest["packId"],
        "sourceManifestState": manifest["state"],
        "counts": {
            "sfx": 146, "ui": 27, "total_cues": 173,
            "variants_per_cue": 3, "variant_files_measured": 173 * 3 * 2,
        },
        "crosscheck": {
            "sha_mismatches": sha_mismatch,
            "duration_mismatches_over_1ms": dur_mismatch,
        },
        "notes": [
            "Every measurement is from real bytes (git lfs pull); "
            "LFS pointers fail the tool instead of producing numbers.",
            "Per-cue/per-variant loudness/true-peak only, NOT a mix "
            "PASS: no combined mix, no VO, no ducking was measured.",
            "All 173 cues are loop=False one-shots, so no loop-seam "
            "indicator applies (unlike the music/ambience pack).",
            "186 of 519 runtime variants are shorter than 400 ms, so "
            "EBU R128 gated integrated LUFS is not measurable for "
            "them (ffmpeg loudnorm returns -inf); those variants "
            "carry integrated_lufs=null plus a decoded RMS level in "
            "dBFS (short_clip_level_dbfs_rms), which is NOT a LUFS "
            "value, and their true peak remains valid. The other "
            "333 variants have finite integrated LUFS.",
            "All cues remain RENDERED_CANDIDATE + "
            "REQUIRES_PRESENTATION_ADAPTER in the manifest: measured, "
            "not yet runtime-connected, not final.",
        ],
        "cues": entries,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(pack, indent=1, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"wrote {out} ({len(entries)} cues, "
          f"{len(entries) * 3 * 2} variant files)")
    print(f"sha mismatches: {len(sha_mismatch)}; "
          f"duration mismatches: {len(dur_mismatch)}")
    for m in sha_mismatch[:20]:
        print("  SHA MISMATCH:", m)
    for m in dur_mismatch[:20]:
        print("  DUR MISMATCH:", m)


if __name__ == "__main__":
    main()
