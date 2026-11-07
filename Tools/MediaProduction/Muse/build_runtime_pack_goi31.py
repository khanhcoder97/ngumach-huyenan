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
                        checkpoint_label=("CP41" if scene_id == "CIN_009"
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
        "checkpoint": "MEDIA-02 checkpoint 41 - Goi 31 item 4 extended: minimal runtime pack (prologue + CIN_001/002/004/006 + CIN_003 + CIN_005 + CIN_007 + CIN_008 + CIN_009 draft mixes v1 embedded in the runtime OGV + review MP4; CP34/CP37/CP38/CP39/CP40 scenes verified unchanged)",
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
            "its v1, CIN_008 embeds its v1 and CIN_009 embeds its "
            "v1; v1/v2 P0 mixes "
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
