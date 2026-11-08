#!/usr/bin/env python3
"""MEDIA-02 checkpoint 34 (Goi 31 item 4): minimal runtime pack.

Checkpoint 37 extends it with CIN_003 (draft mix v1, same recipe);
the CP34 scenes are verified unchanged on re-run (idempotent
verify_muxed path), never re-muxed.

Checkpoint 38 extends it with CIN_005 (draft mix v1, same recipe);
the CP34/CP37 scenes are verified unchanged on re-run, never
re-muxed.

Checkpoint 39 extends it with CIN_007 (draft mix v1, same recipe);
the CP34/CP37/CP38 scenes are verified unchanged on re-run, never
re-muxed.

Checkpoint 40 extends it with CIN_008 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39 scenes are verified unchanged on re-run,
never re-muxed.

Checkpoint 41 extends it with CIN_009 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40 scenes are verified unchanged on re-run,
never re-muxed.

Checkpoint 42 extends it with CIN_010 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41 scenes are verified unchanged on
re-run, never re-muxed.

Checkpoint 45 extends it with CIN_011 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42 scenes are verified
unchanged on re-run, never re-muxed.

Checkpoint 46 extends it with CIN_012 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45 scenes are verified
unchanged on re-run, never re-muxed.

Checkpoint 47 extends it with CIN_013 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46 scenes are verified
unchanged on re-run, never re-muxed.

Checkpoint 48 extends it with CIN_014 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47 scenes are
verified unchanged on re-run, never re-muxed.

Checkpoint 49 extends it with CIN_015 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48 scenes are
verified unchanged on re-run, never re-muxed.

Checkpoint 50 extends it with CIN_016 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49
scenes are verified unchanged on re-run, never re-muxed.

Checkpoint 51 extends it with CIN_017 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50
scenes are verified unchanged on re-run, never re-muxed.

Checkpoint 52 extends it with CIN_018 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50/CP51
scenes are verified unchanged on re-run, never re-muxed. CIN_018
is the only campaign scene with TWO dialogue windows (S02 Co Vo
Tuong at 6.5 s, S03 player at 12.5 s); both draft VO takes are
mixed in, the S03 overrun (+0.280 s) kept per the owner verdict.

Checkpoint 53 extends it with CIN_019 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50/CP51/CP52
scenes are verified unchanged on re-run, never re-muxed.

Checkpoint 54 extends it with CIN_020 (draft mix v1, same recipe);
the CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50/CP51/CP52/CP53
scenes are verified unchanged on re-run, never re-muxed. With
CIN_020 the pack covers all 21 entries and every scene embeds a
draft mix v1 (Work Order 37 M-B big checkpoint 1 complete).

Turns the per-scene clips for the prologue + CIN_001/002/004/006 into
a playable runtime pack:

  * CIN_001 / CIN_002 / CIN_004: embed the P0 draft mix v3 (fully
    composed stems, checkpoint 31) into the runtime OGV (Theora +
    Vorbis 160 kbps, mirroring the prologue film's OGV audio) and
    the review/master MP4 (H.264 + AAC 192 kbps). Video streams are
    copied bit-for-bit (-c:v copy); only an audio stream is added.
    The v1/v2 mixes stay as separate files in mix/p0/ and mix/p0_v2/;
    v3 is the embedded default and adoption remains Codex's adapter
    decision at PR review.
  * CIN_006: embed the new draft mix v1 (checkpoint 34, same recipe,
    PROPOSED stem assignment) the same way.
  * CIN_000 (prologue): verify only -- its MP4/OGV already carry the
    embedded mix (checkpoint 27); canonical files are NOT re-muxed.

Per scene the script also verifies poster (640x360 PNG), SRT
(UTF-8/NFC, cue count == timing dialogue count) and timing JSON,
then updates the scene's scene_export_manifest_v1.json (new
sha256/size for mp4/ogv + hasAudioTrack + audio block) and writes
the pack index ClientGodot/assets/cinematics/RUNTIME_PACK_GOI31_v1.json.

Run order: build_cin006_mix_v1.py -> this script -> re-run
build_runtime_delivery.py (rebuilds both runtime manifests from the
updated export manifests and verifies the embedded audio streams).

All measurements are from real bytes (ffprobe / loudnorm). Exit code
0 = every check passed; 1 = any failure (details printed, no files
replaced for the failed scene).
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(".")
CINE = ROOT / "ClientGodot/assets/cinematics"
MIX_V3 = ROOT / "ClientGodot/assets/audio/mix/p0_v3"
MIX_CIN006 = ROOT / "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1"
MIX_CIN003 = ROOT / "Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1"
MIX_CIN005 = ROOT / "Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1"
MIX_CIN007 = ROOT / "Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1"
MIX_CIN008 = ROOT / "Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1"
MIX_CIN009 = ROOT / "Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1"
MIX_CIN010 = ROOT / "Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1"
MIX_CIN011 = ROOT / "Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V1"
MIX_CIN012 = ROOT / "Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V1"
MIX_CIN013 = ROOT / "Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V1"
MIX_CIN014 = ROOT / "Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V1"
MIX_CIN015 = ROOT / "Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V1"
MIX_CIN016 = ROOT / "Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V1"
MIX_CIN017 = ROOT / "Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V1"
MIX_CIN018 = ROOT / "Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1"
MIX_CIN019 = ROOT / "Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1"
MIX_CIN020 = ROOT / "Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V1"
FAILURES = []


def fail(msg):
    FAILURES.append(msg)
    print("FAIL: " + msg, file=sys.stderr)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)
    return r


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def count_frames(path: Path) -> int:
    r = run(["ffprobe", "-v", "error", "-count_frames",
             "-select_streams", "v:0",
             "-show_entries", "stream=nb_read_frames",
             "-of", "csv=p=0", str(path)])
    return int(r.stdout.strip())


def loudnorm(path: Path) -> dict:
    r = run(["ffmpeg", "-i", str(path), "-vn", "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    tail = r.stderr.strip().splitlines()
    start = next(i for i, line in enumerate(tail) if line.strip() == "{")
    end = next(i for i, line in enumerate(tail) if line.strip() == "}")
    return json.loads("\n".join(tail[start:end + 1]))


def video_params(p: dict) -> dict:
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    return {
        "codec": v["codec_name"],
        "width": int(v["width"]),
        "height": int(v["height"]),
        "r_frame_rate": v["r_frame_rate"],
        "duration": float(v.get("duration")
                          or p["format"]["duration"]),
    }


def mux(scene_id: str, mix_wav: Path, mix_version: str,
        mix_manifest_sha: str, work: Path,
        checkpoint_label: str = "CP34") -> dict:
    """Mux mix audio into the scene's OGV + MP4; return audio records."""
    d = CINE / scene_id
    records = {}
    for key, audio_codec, bitrate in (
            ("ogv", "libvorbis", "160k"), ("mp4", "aac", "192k")):
        src = d / f"{scene_id}_640x360_30fps.{key}"
        before = probe(src)
        bv = video_params(before)
        frames_before = count_frames(src)
        if bv["codec"] != ("theora" if key == "ogv" else "h264"):
            fail(f"{scene_id}/{key}: unexpected video codec {bv['codec']}")
            return None
        if (bv["width"], bv["height"]) != (640, 360):
            fail(f"{scene_id}/{key}: unexpected size "
                 f"{bv['width']}x{bv['height']}")
            return None
        if bv["r_frame_rate"] != "30/1":
            fail(f"{scene_id}/{key}: unexpected frame rate "
                 f"{bv['r_frame_rate']}")
            return None
        if any(s["codec_type"] == "audio" for s in before["streams"]):
            fail(f"{scene_id}/{key}: already has an audio stream")
            return None
        # Temp file lives next to the target (same filesystem) so the
        # replace is atomic; the loudnorm WAV can stay in the tmp dir.
        tmp = d / f".{scene_id}_640x360_30fps.{key}.packtmp"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
             "-i", str(mix_wav),
             "-map", "0:v", "-map", "1:a",
             "-c:v", "copy", "-c:a", audio_codec, "-b:a", bitrate,
             "-t", f"{bv['duration']:.3f}",
             "-metadata", f"comment=Ngũ Mạch MEDIA-02 {checkpoint_label}: "
                          f"embedded draft mix {mix_version}",
             "-f", key,
             str(tmp)])
        after = probe(tmp)
        av = video_params(after)
        frames_after = count_frames(tmp)
        if av != bv:
            fail(f"{scene_id}/{key}: video params changed on mux: "
                 f"{bv} -> {av}")
            tmp.unlink(missing_ok=True)
            return None
        if frames_after != frames_before:
            fail(f"{scene_id}/{key}: stored frames changed on mux: "
                 f"{frames_before} -> {frames_after}")
            tmp.unlink(missing_ok=True)
            return None
        a = next((s for s in after["streams"]
                  if s["codec_type"] == "audio"), None)
        if a is None:
            fail(f"{scene_id}/{key}: no audio stream after mux")
            tmp.unlink(missing_ok=True)
            return None
        if int(a["sample_rate"]) != 48000 or int(a["channels"]) != 2:
            fail(f"{scene_id}/{key}: audio stream "
                 f"{a['sample_rate']} Hz/{a['channels']} ch")
            tmp.unlink(missing_ok=True)
            return None
        if abs(float(a.get("duration") or after["format"]["duration"])
               - bv["duration"]) > 0.05:
            fail(f"{scene_id}/{key}: audio duration != video duration")
            tmp.unlink(missing_ok=True)
            return None
        # Measure the muxed (encoded) audio, not the source WAV.
        wav_tmp = work / f"{scene_id}_{key}_audio.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(tmp),
             "-map", "0:a", "-ac", "2", "-ar", "48000", str(wav_tmp)])
        ln = loudnorm(wav_tmp)
        records[key] = {
            "codec": ("vorbis" if key == "ogv" else "aac"),
            "sampleRateHz": 48000,
            "channels": 2,
            "bitRateKbps": int(bitrate[:-1]),
            "sourceMix": str(mix_wav.relative_to(ROOT)),
            "sourceMixSha256": mix_manifest_sha,
            "mixVersion": mix_version,
            "integratedLUFS": ln["input_i"],
            "truePeakDBTP": ln["input_tp"],
            "durationSeconds": round(
                float(after["format"]["duration"]), 4),
            "videoStoredFrames": frames_after,
        }
        # Replace in place only after all checks passed for this file.
        tmp.replace(src)
        print(f"{scene_id}/{key}: muxed {mix_version} -> "
              f"{a['codec_name']} {bitrate}, LUFS {ln['input_i']} "
              f"TP {ln['input_tp']}, video {frames_after} frames "
              f"unchanged")
    return records


def check_srt(scene_id: str) -> dict:
    d = CINE / scene_id
    srt = d / f"{scene_id}_vi.srt"
    text = srt.read_bytes().decode("utf-8")  # raises on bad UTF-8
    if not unicodedata.is_normalized("NFC", text):
        fail(f"{scene_id}: SRT is not NFC")
        return None
    cues = [b for b in text.strip().split("\n\n") if b.strip()]
    timing = json.loads((d / f"{scene_id}_timing_v1.json")
                        .read_text(encoding="utf-8"))
    n_dialogue = 0
    for sh in timing.get("shots", []):
        dlg = sh.get("dialogue")
        if isinstance(dlg, dict):
            n_dialogue += 1
        elif isinstance(dlg, list):
            # Prologue CIN_000: narration segments listed per shot.
            n_dialogue += len(dlg)
    if len(cues) != n_dialogue:
        fail(f"{scene_id}: SRT cues {len(cues)} != timing dialogues "
             f"{n_dialogue}")
        return None
    return {"cues": len(cues), "sha256": sha256(srt),
            "sizeBytes": srt.stat().st_size, "encoding": "UTF-8/NFC"}


def check_poster(scene_id: str) -> dict:
    d = CINE / scene_id
    poster = d / f"{scene_id}_poster.png"
    p = probe(poster)
    v = p["streams"][0]
    if (v["codec_name"], int(v["width"]), int(v["height"])) != (
            "png", 640, 360):
        fail(f"{scene_id}: poster is not 640x360 PNG")
        return None
    return {"sha256": sha256(poster), "sizeBytes": poster.stat().st_size,
            "width": 640, "height": 360}


def update_export_manifest(scene_id: str, audio_records: dict,
                           checkpoint_note: str = None) -> None:
    d = CINE / scene_id
    mp = d / "scene_export_manifest_v1.json"
    exp = json.loads(mp.read_text(encoding="utf-8"))
    exp["hasAudioTrack"] = True
    for key in ("mp4", "ogv"):
        f = d / f"{scene_id}_640x360_30fps.{key}"
        exp["files"][key]["sha256"] = sha256(f)
        exp["files"][key]["sizeBytes"] = f.stat().st_size
        exp["files"][key]["audio"] = audio_records[key]
    exp["checkpoint"] = checkpoint_note or (
        "MEDIA-02 checkpoint 34 - Goi 31 item 4: "
        "embedded draft mix audio in the runtime OGV "
        "+ review MP4 (video streams bit-identical); "
        "poster/SRT/timing unchanged")
    mp.write_text(json.dumps(exp, ensure_ascii=False, indent=2) + "\n",
                  encoding="utf-8")


def verify_muxed(scene_id: str, work: Path) -> dict:
    """Re-verify a scene whose OGV/MP4 were already muxed by an
    earlier (interrupted) run of this script: audio streams present,
    video params match the export manifest, muxed-audio LUFS/TP
    re-measured and matched to the recorded values. Returns the
    audio records from the export manifest (no re-mux, no rewrite)."""
    d = CINE / scene_id
    exp = json.loads((d / "scene_export_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    records = {}
    for key in ("ogv", "mp4"):
        f = d / f"{scene_id}_640x360_30fps.{key}"
        rec = exp["files"][key]["audio"]
        if sha256(f) != exp["files"][key]["sha256"]:
            fail(f"{scene_id}/{key}: sha != export manifest "
                 f"(already-muxed file changed?)")
            return None
        p = probe(f)
        v = video_params(p)
        if (v["codec"], v["width"], v["height"],
                v["r_frame_rate"]) != (
                ("theora" if key == "ogv" else "h264"), 640, 360, "30/1"):
            fail(f"{scene_id}/{key}: unexpected video params {v}")
            return None
        if count_frames(f) != rec["videoStoredFrames"]:
            fail(f"{scene_id}/{key}: stored frames changed")
            return None
        a = next((s for s in p["streams"]
                  if s["codec_type"] == "audio"), None)
        if a is None or a["codec_name"] != rec["codec"]:
            fail(f"{scene_id}/{key}: audio stream missing/wrong codec")
            return None
        wav_tmp = work / f"{scene_id}_{key}_audio.wav"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(f),
             "-map", "0:a", "-ac", "2", "-ar", "48000", str(wav_tmp)])
        ln = loudnorm(wav_tmp)
        if (abs(float(ln["input_i"]) - float(rec["integratedLUFS"]))
                > 0.05
                or abs(float(ln["input_tp"])
                       - float(rec["truePeakDBTP"])) > 0.05):
            fail(f"{scene_id}/{key}: re-measured muxed audio "
                 f"{ln['input_i']}/{ln['input_tp']} != manifest "
                 f"{rec['integratedLUFS']}/{rec['truePeakDBTP']}")
            return None
        records[key] = rec
        print(f"{scene_id}/{key}: already muxed, verified "
              f"(LUFS {ln['input_i']} TP {ln['input_tp']})")
    return records


def verify_prologue_unchanged(work: Path) -> dict:
    """CIN_000 keeps its checkpoint-27 embedded mix; verify only."""
    d = CINE / "CIN_000"
    exp = json.loads((d / "scene_export_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    for key in ("mp4", "ogv"):
        f = d / f"CIN_000_640x360_30fps.{key}"
        if sha256(f) != exp[key]["sha256"]:
            fail(f"CIN_000/{key}: sha changed -- canonical film must "
                 f"not be re-muxed")
            return None
        p = probe(f)
        kinds = [s["codec_type"] for s in p["streams"]]
        if "audio" not in kinds:
            fail(f"CIN_000/{key}: embedded audio missing")
            return None
    return {"mp4Sha256": exp["mp4"]["sha256"],
            "ogvSha256": exp["ogv"]["sha256"],
            "note": "verified unchanged from checkpoint 27/28"}


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="runtime_pack_goi31_"))
    scenes = {
        "CIN_001": (MIX_V3 / "CIN_001_mix_draft_v3.wav", "v3_fully_composed"),
        "CIN_002": (MIX_V3 / "CIN_002_mix_draft_v3.wav", "v3_fully_composed"),
        "CIN_004": (MIX_V3 / "CIN_004_mix_draft_v3.wav", "v3_fully_composed"),
        "CIN_006": (MIX_CIN006 / "CIN_006_mix_draft_v1.wav",
                    "v1_cin006_proposed"),
        "CIN_003": (MIX_CIN003 / "CIN_003_mix_draft_v1.wav",
                    "v1_cin003_proposed"),
        "CIN_005": (MIX_CIN005 / "CIN_005_mix_draft_v1.wav",
                    "v1_cin005_proposed"),
        "CIN_007": (MIX_CIN007 / "CIN_007_mix_draft_v1.wav",
                    "v1_cin007_proposed"),
        "CIN_008": (MIX_CIN008 / "CIN_008_mix_draft_v1.wav",
                    "v1_cin008_proposed"),
        "CIN_009": (MIX_CIN009 / "CIN_009_mix_draft_v1.wav",
                    "v1_cin009_proposed"),
        "CIN_010": (MIX_CIN010 / "CIN_010_mix_draft_v1.wav",
                    "v1_cin010_proposed"),
        "CIN_011": (MIX_CIN011 / "CIN_011_mix_draft_v1.wav",
                    "v1_cin011_proposed"),
        "CIN_012": (MIX_CIN012 / "CIN_012_mix_draft_v1.wav",
                    "v1_cin012_proposed"),
        "CIN_013": (MIX_CIN013 / "CIN_013_mix_draft_v1.wav",
                    "v1_cin013_proposed"),
        "CIN_014": (MIX_CIN014 / "CIN_014_mix_draft_v1.wav",
                    "v1_cin014_proposed"),
        "CIN_015": (MIX_CIN015 / "CIN_015_mix_draft_v1.wav",
                    "v1_cin015_proposed"),
        "CIN_016": (MIX_CIN016 / "CIN_016_mix_draft_v1.wav",
                    "v1_cin016_proposed"),
        "CIN_017": (MIX_CIN017 / "CIN_017_mix_draft_v1.wav",
                    "v1_cin017_proposed"),
        "CIN_018": (MIX_CIN018 / "CIN_018_mix_draft_v1.wav",
                    "v1_cin018_proposed"),
        "CIN_019": (MIX_CIN019 / "CIN_019_mix_draft_v1.wav",
                    "v1_cin019_proposed"),
        "CIN_020": (MIX_CIN020 / "CIN_020_mix_draft_v1.wav",
                    "v1_cin020_proposed"),
    }
    mix_manifest_shas = {}
    v3_manifest = json.loads(
        (ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3"
         / "P0_MIX_V3_manifest_v1.json").read_text(encoding="utf-8"))
    for scene in v3_manifest["scenes"]:
        mix_manifest_shas[scene["sceneId"]] = scene["mix"]["sha256"]
    cin006_manifest = json.loads(
        (MIX_CIN006 / "CIN006_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_006"] = \
        cin006_manifest["scenes"][0]["mix"]["sha256"]
    cin003_manifest = json.loads(
        (MIX_CIN003 / "CIN003_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_003"] = \
        cin003_manifest["scenes"][0]["mix"]["sha256"]
    cin005_manifest = json.loads(
        (MIX_CIN005 / "CIN005_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_005"] = \
        cin005_manifest["scenes"][0]["mix"]["sha256"]
    cin007_manifest = json.loads(
        (MIX_CIN007 / "CIN007_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_007"] = \
        cin007_manifest["scenes"][0]["mix"]["sha256"]
    cin008_manifest = json.loads(
        (MIX_CIN008 / "CIN008_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_008"] = \
        cin008_manifest["scenes"][0]["mix"]["sha256"]
    cin009_manifest = json.loads(
        (MIX_CIN009 / "CIN009_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_009"] = \
        cin009_manifest["scenes"][0]["mix"]["sha256"]
    cin010_manifest = json.loads(
        (MIX_CIN010 / "CIN010_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_010"] = \
        cin010_manifest["scenes"][0]["mix"]["sha256"]
    cin011_manifest = json.loads(
        (MIX_CIN011 / "CIN011_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_011"] = \
        cin011_manifest["scenes"][0]["mix"]["sha256"]
    cin012_manifest = json.loads(
        (MIX_CIN012 / "CIN012_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_012"] = \
        cin012_manifest["scenes"][0]["mix"]["sha256"]
    cin013_manifest = json.loads(
        (MIX_CIN013 / "CIN013_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_013"] = \
        cin013_manifest["scenes"][0]["mix"]["sha256"]
    cin014_manifest = json.loads(
        (MIX_CIN014 / "CIN014_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_014"] = \
        cin014_manifest["scenes"][0]["mix"]["sha256"]
    cin015_manifest = json.loads(
        (MIX_CIN015 / "CIN015_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_015"] = \
        cin015_manifest["scenes"][0]["mix"]["sha256"]
    cin016_manifest = json.loads(
        (MIX_CIN016 / "CIN016_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_016"] = \
        cin016_manifest["scenes"][0]["mix"]["sha256"]
    cin017_manifest = json.loads(
        (MIX_CIN017 / "CIN017_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_017"] = \
        cin017_manifest["scenes"][0]["mix"]["sha256"]
    cin018_manifest = json.loads(
        (MIX_CIN018 / "CIN018_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_018"] = \
        cin018_manifest["scenes"][0]["mix"]["sha256"]
    cin019_manifest = json.loads(
        (MIX_CIN019 / "CIN019_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_019"] = \
        cin019_manifest["scenes"][0]["mix"]["sha256"]
    cin020_manifest = json.loads(
        (MIX_CIN020 / "CIN020_MIX_V1_manifest_v1.json")
        .read_text(encoding="utf-8"))
    mix_manifest_shas["CIN_020"] = \
        cin020_manifest["scenes"][0]["mix"]["sha256"]

    pack_scenes = []
    for scene_id, (mix_wav, mix_version) in scenes.items():
        if not mix_wav.exists():
            fail(f"{scene_id}: mix wav missing {mix_wav}")
            continue
        if sha256(mix_wav) != mix_manifest_shas[scene_id]:
            fail(f"{scene_id}: mix wav sha != its manifest")
            continue
        srt = check_srt(scene_id)
        poster = check_poster(scene_id)
        if srt is None or poster is None:
            continue
        exp_path = CINE / scene_id / "scene_export_manifest_v1.json"
        exp = json.loads(exp_path.read_text(encoding="utf-8"))
        if exp.get("hasAudioTrack") is True:
            # Idempotent re-run: an interrupted earlier run already
            # muxed this scene; verify the muxed files, do not re-mux.
            audio = verify_muxed(scene_id, work)
        else:
            audio = mux(scene_id, mix_wav, mix_version,
                        mix_manifest_shas[scene_id], work,
                        checkpoint_label=("CP54" if scene_id == "CIN_020"
                                          else "CP53" if scene_id == "CIN_019"
                                          else "CP52" if scene_id == "CIN_018"
                                          else "CP51" if scene_id == "CIN_017"
                                          else "CP50" if scene_id == "CIN_016"
                                          else "CP49" if scene_id == "CIN_015"
                                          else "CP48" if scene_id == "CIN_014"
                                          else "CP47" if scene_id == "CIN_013"
                                          else "CP46" if scene_id == "CIN_012"
                                          else "CP45" if scene_id == "CIN_011"
                                          else "CP42" if scene_id == "CIN_010"
                                          else "CP41" if scene_id == "CIN_009"
                                          else "CP40" if scene_id == "CIN_008"
                                          else "CP39" if scene_id == "CIN_007"
                                          else "CP38" if scene_id == "CIN_005"
                                          else "CP37" if scene_id == "CIN_003"
                                          else "CP34"))
        if audio is None:
            continue
        note = None
        if scene_id == "CIN_003":
            note = ("MEDIA-02 checkpoint 37 - CIN_003 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_005":
            note = ("MEDIA-02 checkpoint 38 - CIN_005 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_007":
            note = ("MEDIA-02 checkpoint 39 - CIN_007 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_008":
            note = ("MEDIA-02 checkpoint 40 - CIN_008 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_009":
            note = ("MEDIA-02 checkpoint 41 - CIN_009 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_010":
            note = ("MEDIA-02 checkpoint 42 - CIN_010 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_011":
            note = ("MEDIA-02 checkpoint 45 - CIN_011 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_012":
            note = ("MEDIA-02 checkpoint 46 - CIN_012 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_013":
            note = ("MEDIA-02 checkpoint 47 - CIN_013 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_014":
            note = ("MEDIA-02 checkpoint 48 - CIN_014 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_015":
            note = ("MEDIA-02 checkpoint 49 - CIN_015 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_016":
            note = ("MEDIA-02 checkpoint 50 - CIN_016 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_017":
            note = ("MEDIA-02 checkpoint 51 - CIN_017 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_018":
            note = ("MEDIA-02 checkpoint 52 - CIN_018 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_019":
            note = ("MEDIA-02 checkpoint 53 - CIN_019 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        if scene_id == "CIN_020":
            note = ("MEDIA-02 checkpoint 54 - CIN_020 draft mix v1: "
                    "embedded draft mix audio in the runtime OGV "
                    "+ review MP4 (video streams bit-identical); "
                    "poster/SRT/timing unchanged")
        update_export_manifest(scene_id, audio, checkpoint_note=note)
        pack_scenes.append({
            "sceneId": scene_id,
            "durationSeconds": audio["ogv"]["durationSeconds"],
            "embeddedMixVersion": mix_version,
            "files": {
                "ogv": {**audio["ogv"],
                        "path": f"assets/cinematics/{scene_id}/"
                                f"{scene_id}_640x360_30fps.ogv",
                        "sha256": sha256(
                            CINE / scene_id /
                            f"{scene_id}_640x360_30fps.ogv"),
                        "sizeBytes": (CINE / scene_id /
                                      f"{scene_id}_640x360_30fps.ogv")
                        .stat().st_size},
                "mp4": {**audio["mp4"],
                        "path": f"assets/cinematics/{scene_id}/"
                                f"{scene_id}_640x360_30fps.mp4",
                        "sha256": sha256(
                            CINE / scene_id /
                            f"{scene_id}_640x360_30fps.mp4"),
                        "sizeBytes": (CINE / scene_id /
                                      f"{scene_id}_640x360_30fps.mp4")
                        .stat().st_size},
                "poster": {**poster,
                           "path": f"assets/cinematics/{scene_id}/"
                                   f"{scene_id}_poster.png"},
                "srt": {**srt,
                        "path": f"assets/cinematics/{scene_id}/"
                                f"{scene_id}_vi.srt"},
                "timing": {
                    "path": f"assets/cinematics/{scene_id}/"
                            f"{scene_id}_timing_v1.json",
                    "sha256": sha256(
                        CINE / scene_id / f"{scene_id}_timing_v1.json"),
                    "sizeBytes": (CINE / scene_id /
                                  f"{scene_id}_timing_v1.json")
                    .stat().st_size},
            },
        })

    prologue = verify_prologue_unchanged(work)
    if prologue is not None:
        srt = check_srt("CIN_000")
        poster = check_poster("CIN_000")
        if srt is not None and poster is not None:
            pack_scenes.insert(0, {
                "sceneId": "CIN_000",
                "durationSeconds": 87.367,
                "embeddedMixVersion": "prologue_mix_v1 (checkpoint 27)",
                "files": {
                    "ogv": {"path": "assets/cinematics/CIN_000/"
                                    "CIN_000_640x360_30fps.ogv",
                            "sha256": prologue["ogvSha256"],
                            "codec": "theora",
                            "audioCodec": "vorbis",
                            "note": prologue["note"]},
                    "mp4": {"path": "assets/cinematics/CIN_000/"
                                    "CIN_000_640x360_30fps.mp4",
                            "sha256": prologue["mp4Sha256"],
                            "codec": "h264",
                            "audioCodec": "aac",
                            "note": prologue["note"]},
                    "poster": {**poster,
                               "path": "assets/cinematics/CIN_000/"
                                       "CIN_000_poster.png"},
                    "srt": {**srt,
                            "path": "assets/cinematics/CIN_000/"
                                    "CIN_000_vi.srt"},
                    "timing": {
                        "path": "assets/cinematics/CIN_000/"
                                "CIN_000_timing_v1.json",
                        "sha256": sha256(
                            CINE / "CIN_000" / "CIN_000_timing_v1.json"),
                        "sizeBytes": (CINE / "CIN_000" /
                                      "CIN_000_timing_v1.json")
                        .stat().st_size},
                    "reviewOnlyBakedSubtitles": {
                        "mp4SubVi": "assets/cinematics/CIN_000/"
                                    "CIN_000_640x360_30fps_sub_vi.mp4",
                        "readableSrt": "assets/cinematics/CIN_000/"
                                       "CIN_000_vi_readable.srt",
                        "status": "REVIEW_ONLY_NOT_RUNTIME",
                    },
                },
            })

    pack = {
        "manifestId": "NGM_RUNTIME_PACK_GOI31_V1",
        "checkpoint": "MEDIA-02 checkpoint 54 - Goi 31 item 4 extended: minimal runtime pack (prologue + CIN_001/002/004/006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 + CIN_010 + CIN_011 + CIN_012 + CIN_013 + CIN_014 + CIN_015 + CIN_016 + CIN_017 + CIN_018 + CIN_019 + CIN_020 draft mixes v1 embedded in the runtime OGV + review MP4; CP34/CP37/CP38/CP39/CP40/CP41/CP42/CP45/CP46/CP47/CP48/CP49/CP50/CP51/CP52/CP53 scenes verified unchanged; all 21 entries now embed a soundtrack, WO37 M-B big checkpoint 1 complete)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL",
        "spec": {
            "video": "640x360, 30 fps; runtime OGV Theora+Vorbis, "
                     "review/master MP4 H.264+AAC",
            "audio": "OGV Vorbis 160 kbps / MP4 AAC 192 kbps, 48 kHz "
                     "stereo, embedded draft mix",
            "poster": "640x360 PNG (first keyframe / title card)",
            "subtitles": "runtime = CLEAN video + subtitle overlay "
                         "from the sidecar .srt (UTF-8/NFC, DRAFT); "
                         "the baked-subtitle variant is REVIEW-ONLY",
            "timing": "per-scene timing JSON, scene-local time",
        },
        "contract": [
            "Runtime playback uses the clean OGV + the sidecar SRT "
            "overlay; no baked subtitles in any runtime file.",
            "CIN_000_640x360_30fps_sub_vi.mp4 (burned-in + embedded "
            "subtitles) is a review-only viewing variant, NOT part "
            "of the runtime pack.",
            "Embedded mixes are DRAFT_MIX_NOT_FINAL; P0 scenes embed "
            "v3 (fully composed), CIN_006 embeds its v1, CIN_003 "
            "embeds its v1, CIN_005 embeds its v1, CIN_007 embeds "
            "its v1, CIN_008 embeds its v1, CIN_009 embeds its v1, "
            "CIN_010 embeds its v1, CIN_011 embeds its v1, "
            "CIN_012 embeds its v1, CIN_013 embeds its v1, "
            "CIN_014 embeds its v1, CIN_015 embeds its v1, "
            "CIN_016 embeds its v1, CIN_017 embeds its v1, "
            "CIN_018 embeds its v1, CIN_019 embeds its v1 and "
            "CIN_020 embeds its v1 -- all 21 entries now embed "
            "a soundtrack; "
            "v1/v2 P0 mixes "
            "stay as separate files and "
            "Codex's adapter chooses the mix version at PR review -- "
            "swapping the embedded mix is a re-mux only, no picture "
            "change.",
            "CIN_006 stem assignment (thang_long music + "
            "thang_long_crowd ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the alternate take CIN_006_ALT_T01 "
            "is NOT in the pack (DEC-MEDIA-P0 Q3).",
            "CIN_008 stem assignment (tran_son music + "
            "river_shore ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 16.052 s, no overrun, no "
            "tail trim). tran_son is the composed set's bell-led gate "
            "form, matching the scene's central gate image (S02); "
            "river_shore is the water-edge bed for the bamboo forest "
            "pool (S03).",
            "CIN_009 stem assignment (lam_trieu music + "
            "waterfall ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 16.580 s, no overrun, no "
            "tail trim). lam_trieu is the composed set's G-major "
            "transposition with ornamented flute (Lam Trieu, forest "
            "tide) -- the flute carries the forest's answering voice "
            "of the scene title 'Tieng rung duoc dap'; waterfall is "
            "the water bed for the stream running through all three "
            "shots (S01 roots stream, S02 forest path, S03 top-down "
            "waterfall and shrine). The mix is hotter than CIN_008 "
            "(-17.84 LUFS) because the CP17 VO take itself is hot "
            "(-17.23 LUFS); VO is kept at unity per the recipe, not "
            "normalized.",
            "CIN_010 stem assignment (sa_hoa music + "
            "desert_wind ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 15.308 s, no overrun, no "
            "tail trim). sa_hoa is the composed set's desert form "
            "('Sa Hoa -- Lo va cat', kiln and sand: A minor "
            "pentatonic, dry bright plucks, 110 BPM), matching the "
            "scene's ash-gold caravan rest and last-water-flask "
            "image (S01 caravan + barrel, S02 flask poured into the "
            "barrel, S03 flask set on the map cloth); desert_wind "
            "is the desert wind bed for the dunes running through "
            "all three shots. The mix measures -24.60 LUFS because "
            "the CP17 VO take itself is quiet (-22.01 LUFS); VO is "
            "kept at unity per the recipe, not normalized.",
            "CIN_011 stem assignment (quiet_discovery music + "
            "wind_canopy ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.2-17.8 s window (ends 17.792 s, no overrun, no "
            "tail trim) by 0.008 s. quiet_discovery is the composed "
            "set's exploration silence ('Khoang lang kham pha': "
            "solo flute fragments, single bells, long "
            "near-silences, water drops, 60 BPM), matching the "
            "scene's quiet carving workshop and moral reflection "
            "(S01 workbench with carved tablets, S02 two men in an "
            "open bamboo shelter, S03 Ha Mac leaning over a carved "
            "landscape panel); wind_canopy is the wind-through-"
            "canopy bed for the open shelter and the greenery "
            "behind S02. The mix measures -20.34 LUFS because the "
            "CP17 VO take itself is quiet (-21.50 LUFS); VO is "
            "kept at unity per the recipe, not normalized.",
            "CIN_012 stem assignment (tran_son music + "
            "forge ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 16.820 s, no overrun, no "
            "tail trim) with 0.680 s to spare. tran_son is the "
            "composed set's bell-led stately form ('Tran Son — "
            "Nguoi qua cua': the bell states the motif, a low "
            "flute answers, a drum marks every bar line, 90 BPM), "
            "matching the scene's lantern-lit hall and moral "
            "decision (S01 stone furnace, S02 archive desk, S03 "
            "Ha Mac behind the long wooden table); forge is the "
            "fire bed (fire rumble + crackle + metallic clinks) "
            "for the stone furnace and smithing tools of S01. "
            "sa_hoa was passed over: it was just used for CIN_010 "
            "and its 110 BPM drive suits that desert scene better "
            "than this quiet moral line. The mix measures -25.60 "
            "LUFS because the CP17 VO take itself is quiet "
            "(-25.38 LUFS); VO is kept at unity per the recipe, "
            "not normalized.",
            "CIN_013 stem assignment (lam_trieu music + "
            "mountain_wind ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 14.972 s, no overrun, no "
            "tail trim) with 2.528 s to spare. lam_trieu is the "
            "composed set's G-major transposition with ornamented "
            "flute, matching the scene's village road, rice "
            "paddies and waiting line (S01 stone gatehouse, S02 "
            "the refugee leader with his map, S03 Ly An at the "
            "open gate); mountain_wind is the wind bed for the "
            "mountain gate and open pass. tran_son was passed "
            "over: the bell-led gate form, but just used for "
            "CIN_012, the immediately preceding scene. The mix "
            "measures -25.87 LUFS; VO is kept at unity per the "
            "recipe, not normalized. Staging question, not a mix "
            "defect: the timing manifest marks the S03 dialogue "
            "onscreen: true for the refugee leader, but the S03 "
            "keyframe and the runtime clip at 15 s show only Ly "
            "An at the open gate; the leader is on screen in S02. "
            "The line plays over Ly An waiting at the gate; "
            "voice-over vs staging mismatch is a director/Codex "
            "call.",
            "CIN_014 stem assignment (ben_mua music + "
            "wind_canopy ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 15.572 s, no overrun, no "
            "tail trim) with 1.928 s to spare. ben_mua is the "
            "campaign's own leitmotif statement ('Ben Mua', the "
            "rain quay): D major pentatonic question phrase hanging "
            "on scale degree 2, tail withheld -- the unresolved "
            "hanging phrase for a commander who stamps an order he "
            "knows is false (S01 kneeling among discarded armour, "
            "S02 the seal set down in detail, S03 Tong Banh at the "
            "open village gate); wind_canopy is the wind-through-"
            "canopy bed for the bamboo framing all three shots. "
            "lam_trieu was passed over: the pastoral flute was just "
            "used for CIN_013, the immediately preceding scene; "
            "tran_son was passed over: the bell-led gate form, "
            "already used for CIN_008 and CIN_012. The mix "
            "measures -24.42 LUFS; the CP17 VO take itself is "
            "-22.05 LUFS; ducking is -8.84 dB over the full VO "
            "window; VO is kept at unity per the recipe, not "
            "normalized. Staging: the timing manifest marks the "
            "S03 dialogue onscreen: true for Tong Banh and the "
            "keyframe places a blue-robed figure at the gate, but "
            "the recorded keyframe defects note he is not visually "
            "identifiable in S03 (his armour differs across "
            "S01/S02 and neither S03 figure matches it) -- a "
            "final-picture/character-lock matter, not a mix "
            "defect; the mix does not move the VO.",
            "CIN_015 stem assignment (bach_uyen music + "
            "underwater ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 15.380 s, no overrun, no "
            "tail trim) with 2.120 s to spare. bach_uyen is the "
            "composed set's underwater low-passed form (850 Hz) -- "
            "the setting-exact cue for a drowned city (S01 wide "
            "view of the submerged ruined town, S02 the dining bowl "
            "tied to the stone table with the guide rope and a bare "
            "diver hand, S03 top-down underwater corridor with a "
            "small diver figure in a conical hat); underwater is the "
            "composed underwater bed for the submerged city framing "
            "all three shots; both are first scene-mix uses (P0 v3 "
            "review reel only before). ben_mua was passed over: just "
            "used for CIN_014, the immediately preceding scene. The "
            "mix measures -25.30 LUFS; the CP17 VO take itself is "
            "-23.27 LUFS; ducking is -6.87 dB over the full VO "
            "window; VO is kept at unity per the recipe, not "
            "normalized. Staging: the timing manifest marks the "
            "S03 dialogue onscreen: true for the Diver Lead and the "
            "keyframe places a small diver figure at the bottom "
            "centre of the corridor, but the figure is tiny and seen "
            "from above/behind, so the speaker is not identifiable "
            "by face or gear from the picture alone (S02 shows only "
            "a bare diver hand, S01 no figure at all) -- a "
            "final-picture/character-lock matter, not a mix "
            "defect; the mix does not move the VO.",
            "CIN_016 stem assignment (quiet_discovery music + "
            "wind_canopy ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 14.972 s, no overrun, no "
            "tail trim) with 2.528 s to spare. quiet_discovery is the "
            "composed set's exploration silence ('Khoang lang kham "
            "pha': solo flute fragments, single bells, long "
            "near-silences, water drops, 60 BPM) -- the setting-exact "
            "cue for a quiet indoor conversation about writing "
            "someone else's story down (S01 detail of the old "
            "manuscript under the hanging lamp, S02 the blue-robed man "
            "at the desk with a hooded figure seen from behind, S03 "
            "Ha Mac writing in his book as he asks the elder across "
            "the desk); wind_canopy is the wind-through-canopy bed "
            "for the greenery outside the S03 window and the bamboo "
            "walls. Both are third scene-mix uses (CIN_007, CIN_011, "
            "CIN_014 for wind_canopy). The mix measures -25.07 LUFS; "
            "the CP17 VO take itself is -21.92 LUFS; VO is kept at "
            "unity per the recipe, not normalized. Ducking is 0.0 dB "
            "over the full VO window -- NOT a missing compressor: "
            "quiet_discovery is digitally silent from 12 s to 15 s "
            "(RMS -120 dB floor), so the 12.5-14.972 s window falls "
            "entirely inside the cue's near-silence gap between "
            "fragments; the earlier quiet_discovery mixes show a real "
            "cut (CIN_007 -9.43 dB, CIN_011 -10.79 dB) because their "
            "longer windows extended past 15 s. Staging: unlike "
            "CIN_015, the speaker IS identifiable here (S03 shows Ha "
            "Mac clearly, face in profile, brush in hand); whether "
            "the hooded figure seen from behind in S02 is Ha Mac "
            "arriving is a continuity question for final picture "
            "(woven basket-hat vs rectangular backpack) -- a "
            "final-picture/character-lock matter, not a mix defect; "
            "the mix does not move the VO.",
            "CIN_017 stem assignment (bach_uyen music + "
            "underwater ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 15.668 s, no overrun, no "
            "tail trim) with 1.832 s to spare. bach_uyen is the "
            "composed set's underwater low-passed form (850 Hz) -- "
            "the setting-exact cue for a tide-serpent scene built "
            "around water and a crystal core (S01 wide view of the "
            "flooded ruined temple courtyard at night, the teal "
            "tide serpent coiled around the crystal core in the "
            "water; S02 detail of the serpent coiled around the "
            "glowing crystal on the stone pillar, bubbles rising; "
            "S03 misty river gorge with fishing gear on the bank "
            "and the serpent-shaped dark current winding down the "
            "river); underwater is the composed underwater bed for "
            "the water framing all three shots. Both are second "
            "scene-mix uses -- the same pairing as CIN_015 (the "
            "drowned city), stated plainly because the two scenes "
            "share one water chapter and the cue set has a single "
            "water form; boss_mang_cot was passed over because it "
            "is boss material for the WRONG boss (Mang Cot, not "
            "the Tide Serpent), and this beat is a quiet line, not "
            "a boss fight. The mix measures -24.63 LUFS; the CP17 "
            "VO take itself is -22.33 LUFS; ducking is -4.85 dB "
            "over the full VO window; VO is kept at unity per the "
            "recipe, not normalized. Staging: like CIN_015, the "
            "speaker is NOT identifiable here -- the timing "
            "manifest marks the S03 dialogue onscreen: null for "
            "the Diver Lead, and the S03 keyframe shows only the "
            "river gorge with no diver figure anywhere in the "
            "frame (S01 the serpent with no human figure, S02 "
            "only the serpent and the crystal) -- the line is "
            "delivered off-screen, like Ly An's voice in CIN_004 "
            "(DEC-MEDIA-P0 Q2); a final-picture/character-lock "
            "matter, not a mix defect; the mix does not move "
            "the VO.",
            "CIN_018 stem assignment (sa_hoa music + "
            "desert_wind ambience + reveal at 0.0 s) is "
            "PROPOSED_CANDIDATE; this is the ONLY campaign scene "
            "with TWO dialogue windows -- the S02 take (Co Vo "
            "Tuong) fits inside its 6.5-11.5 s window (2.880 s, "
            "ends 9.380 s, no overrun, no tail trim) and the S03 "
            "take (player) overruns its 12.5-17.5 s window by "
            "0.280 s (5.280 s, ends 17.780 s) with the overrun "
            "KEPT per the owner verdict, no tail trim. sa_hoa is "
            "the composed set's desert form ('Sa Hoa -- Lo va "
            "cat': kiln and sand, A minor pentatonic, dry bright "
            "plucks, 110 BPM) -- the setting-exact cue for a "
            "drought scene built around the lack of water (S01 "
            "cracked drought field, a man pouring the last water "
            "from a gourd, a sealed petition and a measuring post; "
            "S02 Co Vo Tuong at his desk; S03 the masked hooded "
            "figure beside the copper water-machine at night); "
            "desert_wind is the desert wind bed for the dry field "
            "and the night bamboo of all three shots. Both are "
            "second scene-mix uses -- the same pairing as CIN_010 "
            "(the ash-gold caravan rest), stated plainly because "
            "the two scenes share the Sa Hoa / desert setting and "
            "the cue set has a single desert form. The reveal "
            "stinger is placed at 0.0 s (S01 start), NOT the "
            "recipe's 6.0 s: the cue is 3.000 s long, so at 6.0 s "
            "it would sit under 2.5 s of the S02 line -- the "
            "scene's key refusal line, spoken on screen. The mix "
            "measures -21.51 LUFS; the CP17 VO takes themselves "
            "are -23.77 LUFS (S02) and -22.54 LUFS (S03); ducking "
            "is -6.05 dB (S02 window) and -7.44 dB (S03 window) "
            "over the full VO windows; VO is kept at unity per the "
            "recipe, not normalized. The S03 take is "
            "VOICE_PLACEHOLDER_ONLY (VOICE_GUIDE assigns the "
            "player no spoken voice or gender). Staging: the S02 "
            "speaker IS identifiable (onscreen: true, face "
            "visible at his desk); the S03 line is delivered "
            "off-screen (onscreen: null, like Ly An's voice in "
            "CIN_004) -- the masked figure in the S03 keyframe is "
            "NOT identified as the speaker, and the keyframe "
            "defects record its full-face porcelain mask (not the "
            "specified cracked half mask) and torso-spanning "
            "copper machinery; S02 is a medium shot instead of "
            "the detail close view and his hair differs from "
            "S01's; S01's petition renders as a modern "
            "wax-sealed envelope. Final-picture/character-lock "
            "matters, not mix defects; the mix does not move "
            "the VO.",
            "CIN_020 stem assignment (ben_mua music + "
            "river_shore ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; ben_mua is the rain-quay "
            "leitmotif of the opening where the sealed letter "
            "changed hands, back for the closing scene where "
            "the letter is answered at the same river (third "
            "scene-mix use, CIN_003/CIN_014); river_shore is "
            "a fourth use (CIN_003/CIN_008/CIN_019). The CP17 "
            "draft VO take fits inside its 12.5-17.5 s window "
            "(3.000 s, ends 15.500 s) by 2.000 s: no overrun, "
            "no tail trim. The mix measures -23.41 LUFS; the "
            "CP17 take itself measures -19.59 LUFS; VO is "
            "kept at unity per the recipe, not normalized. "
            "Casting: the recipient's voice is a placeholder "
            "role voice (identity/gender undecided) sharing "
            "Ly An's draft voice -- an M-F palette item, not "
            "a mix decision. Staging: the timing records S03 "
            "onscreen: null; the S03 frame shows the villager "
            "from behind (top-down), face not visible, and "
            "the CP24 manifest records his appearance "
            "drifting between all three shots (no named lock "
            "exists for him). Final-picture/casting matters, "
            "not mix defects; the mix does not move the VO. "
            "With this mix the pack covers all 21 entries "
            "and WO37 M-B big checkpoint 1 is complete.",
            "CIN_019 stem assignment (rift_finale music + "
            "river_shore ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; rift_finale is the composed "
            "set's only full close (the leitmotif's answering "
            "tail) and this is its first scene-mix use; "
            "river_shore is a third scene-mix use (CIN_003/"
            "CIN_008). The CP17 draft VO take fits inside its "
            "12.5-17.5 s window (2.880 s, ends 15.380 s) by "
            "2.120 s: no overrun, no tail trim. The mix "
            "measures -27.09 LUFS -- the quietest scene mix so "
            "far -- because the CP17 take itself is one of the "
            "quietest (-25.52 LUFS); VO is kept at unity per "
            "the recipe, not normalized. Staging: the timing "
            "records S03 onscreen: true for Ly An, but the S03 "
            "frame is a wide dawn view of the whole village "
            "under reconstruction and no individual figure is "
            "identifiable as Ly An at this scale; faces and "
            "costumes are storyboard placeholders (no approved "
            "cinematic character lock). Final-picture matter, "
            "not a mix defect; the mix does not move the VO.",
            "CIN_003 stem assignment (ben_mua music + river_shore "
            "ambience + reveal at 6.0 s) is PROPOSED_CANDIDATE; the "
            "CP17 draft VO take fits inside its 12.5-17.5 s window "
            "(ends 16.532 s, no overrun, no tail trim).",
            "CIN_005 stem assignment (thang_long music + "
            "thang_long_crowd ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take overruns "
            "its 12.5-17.5 s window by 0.160 s and the overrun is "
            "KEPT per the owner verdict (Goi 30 D1); no tail trim.",
            "CIN_007 stem assignment (quiet_discovery music + "
            "wind_canopy ambience + reveal at 6.0 s) is "
            "PROPOSED_CANDIDATE; the CP17 draft VO take fits inside "
            "its 12.5-17.5 s window (ends 16.412 s, no overrun, no "
            "tail trim). Ducking evidence is measured over the full "
            "VO window because quiet_discovery is sparse by design "
            "(the first 2 s of the window are near-silence).",
            "Final picture per shot stays blocked on the character "
            "lock; these clips are animatic-level Ken Burns on "
            "storyboard keyframes, NOT final pose animation.",
            "No ear audition has been done (NOT_AUDITIONED); loudness "
            "figures here are measured from the encoded bytes.",
        ],
        "scenes": pack_scenes,
        "failures": FAILURES,
    }
    if FAILURES:
        print(f"PACK BUILD FAILED: {len(FAILURES)} failures")
        sys.exit(1)
    (CINE / "RUNTIME_PACK_GOI31_v1.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: RUNTIME_PACK_GOI31_v1.json written "
          f"({len(pack_scenes)} scenes)")


if __name__ == "__main__":
    main()
