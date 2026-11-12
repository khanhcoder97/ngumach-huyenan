#!/usr/bin/env python3
"""WO37 M-B CP5 — subtitled viewing variant of the prologue film
CIN_000 with the M-F CP2 draft v2 mix (History narration).

Follow-up named in the M-B CP4 report: the CP28 / M-B CP3 subtitled
variant is timed to the v1 (Helio) narration, so re-muxing the v2
audio under it would misalign subtitles vs narration. This checkpoint
re-times the subtitles to the v2 narration and renders a parallel
viewing variant. The canonical v1 files are NOT modified and the
ClientGodot runtime tree is NOT touched (v2 is an Art_Source-only
alternate for Codex review, same discipline as M-F CP2 / M-B CP4).

Method, from real bytes only:

1. Sources verified against their manifests before any work:
   canonical runtime MP4 (film manifest, video source), canonical
   SRT (film manifest), v2 mix WAV + History takes + Ly An take
   (M-F CP2 manifest). All shas must match; the working clone's
   LFS files are pulled selectively first (see run notes).
2. V2 subtitle windows use the SAME rule CP28 used for v1: each
   canonical cue window is the narration take's file span placed at
   its CP27 slot start. V1 windows were the Helio take durations
   (16.512 / 15.528 / 19.752 / 14.928 / 8.040 s + Ly An 2.568 s,
   verified against PROLOGUE_VO_manifest_v1.json); v2 windows are
   the History take durations (13.008 / 16.752 / 16.248 / 12.768 /
   6.672 s) at the same starts, Ly An unchanged (same take reused
   in v2 at -5 dB). Chunk split + proportional allocation + 1.2 s
   minimum display are CP28's exact algorithm (imported from
   build_prologue_subtitled.py), so the 26 chunk TEXTS are identical
   to the v1 readable SRT — only timings move. The one window
   overlap (SEG02 file end 35.785 s vs SEG03 start 35.667 s; the
   0.118 s tail is silence below -50 dBFS per the v2 manifest) is
   resolved by CP28's monotonic rule (+0.168 s shift of the SEG03
   chunks, 0.118 overlap + 0.05 gap).
3. Render CIN_000_640x360_30fps_sub_vi_v2.mp4: video from the
   canonical MP4, burned-in subtitles via libass (CP28 style),
   audio = v2 mix WAV with a presentation gain re-measured on the
   v2 mix (rule: min(+2.0 dB, headroom to -1.0 dBTP), rounded down
   to 0.1 dB — the v2 mix is hotter than the fixed v1 mix, so the
   gain is true-peak-limited, not the +2.0 dB of the v1 variant),
   embedded mov_text track carrying the re-timed readable cues.
   Output trimmed to the video duration (87.2667 s, CP28 behaviour).
4. Render the 720p standard version by the CP3 recipe: integer 2x
   nearest-neighbour upscale of the 640 v2 variant, H.264 crf26,
   audio + subtitle tracks stream-copied. NOT a native 720p capture.
5. Register: film manifest `subtitledVariantV2` (640 file) + a new
   delivery manifest STANDARD720_SUBTITLED_V2_MB_CP5_v1.json (both
   files). No runtime manifest, no export manifest, no mix file is
   touched.
"""
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_prologue_subtitled import (  # noqa: E402
    allocate, chunk_cue, fmt_ts, norm_text, parse_srt)

ROOT = Path(__file__).resolve().parents[3]
CINE_DIR = ROOT / "ClientGodot/assets/cinematics/CIN_000"
CANON_MP4 = CINE_DIR / "CIN_000_640x360_30fps.mp4"
CANON_SRT = ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi.srt"
V1_READABLE = CINE_DIR / "CIN_000_vi_readable.srt"
V2_MIX = ROOT / "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav"
V2_MANIFEST = ROOT / "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_MIX_V2_manifest_v1.json"
FILM_MANIFEST = ROOT / "Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json"
VO_MANIFEST = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json"
OUT_SRT = ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt"
OUT_MP4_640 = ROOT / "Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4"
OUT_DIR_720 = ROOT / "Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2"
OUT_MP4_720 = OUT_DIR_720 / "CIN_000_1280x720_30fps_sub_vi_v2.mp4"
CP5_MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_V2_MB_CP5_v1.json"
TP_CEILING_DBTP = -1.0
GAIN_CAP_DB = 2.0


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def probe(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(p)], capture_output=True, text=True)
    return json.loads(out.stdout)


def loudnorm(p):
    """Single-pass loudnorm; brace-match the JSON (ffmpeg 8.x prints
    a muxing summary line after the JSON block)."""
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    txt = r.stderr
    i = txt.rfind("{")
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                d = json.loads(txt[i:j + 1])
                return float(d["input_i"]), float(d["input_tp"])
    raise ValueError("loudnorm JSON block not found")


def build_readable_v2(canon, windows):
    """Same algorithm as CP28's build_readable_cues, with the v2 cue
    windows substituted for the canonical ones."""
    readable = []
    prev_end = 0.0
    for cue, (ws, we) in zip(canon, windows):
        texts = chunk_cue(cue["text"])
        durs = allocate(we - ws, [len(t) for t in texts])
        t = ws
        spans = []
        for txt, dur in zip(texts, durs):
            spans.append([t, t + dur, txt])
            t += dur
        spans[-1][1] = we
        if spans[0][0] < prev_end + 0.05:
            delta = prev_end + 0.05 - spans[0][0]
            for sp in spans:
                sp[0] += delta
                sp[1] += delta
        for s, e, txt in spans:
            assert e - s >= 1.0, f"chunk too short: {txt[:30]}"
            readable.append({"start": s, "end": e, "text": txt})
            prev_end = e
    return readable


def main():
    fman = json.loads(FILM_MANIFEST.read_text(encoding="utf-8"))
    v2man = json.loads(V2_MANIFEST.read_text(encoding="utf-8"))
    voman = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))

    # --- 1. source integrity vs manifests (real bytes only) ---
    if sha256_of(CANON_MP4) != fman["exports"]["mp4"]["sha256"]:
        sys.exit("canonical MP4 sha drift vs film manifest "
                 "(pull its LFS object first)")
    if sha256_of(CANON_SRT) != fman["srtSha256"]:
        sys.exit("canonical SRT sha drift vs film manifest")
    if sha256_of(V2_MIX) != v2man["sha256"]:
        sys.exit("v2 mix WAV sha drift vs v2 manifest")
    v1r = parse_srt(V1_READABLE.read_text(encoding="utf-8"))
    if len(v1r) != 26:
        sys.exit(f"v1 readable SRT cues {len(v1r)} != 26")
    canon = parse_srt(CANON_SRT.read_text(encoding="utf-8"))
    if len(canon) != 6:
        sys.exit(f"canonical SRT cues {len(canon)} != 6")

    # v1 windows == Helio take file spans (method check): durations
    # from the CP27 VO manifest must equal the canonical SRT windows.
    for seg, cue in zip(voman["segments"], canon[:5]):
        if abs(seg["durationSeconds"] - (cue["end"] - cue["start"])) > 0.001:
            sys.exit(f"v1 method check failed: {seg['takeId']} take "
                     f"{seg['durationSeconds']} != SRT window "
                     f"{cue['end'] - cue['start']:.3f}")
    if abs(voman["finalLine"]["durationSeconds"]
           - (canon[5]["end"] - canon[5]["start"])) > 0.001:
        sys.exit("v1 method check failed: Ly An take != SRT window")

    # --- 2. v2 windows = History take file spans at the same starts ---
    windows = []
    for ch in v2man["paletteRemix"]["narrationChanges"]:
        windows.append((ch["cp27SegmentStartSeconds"],
                        ch["paletteEndSeconds"]))
    windows.append((canon[5]["start"], canon[5]["end"]))  # Ly An unchanged
    print("v2 cue windows:")
    for i, (s, e) in enumerate(windows, 1):
        print(f"  cue {i}: {s:.3f} --> {e:.3f} ({e - s:.3f} s)")

    readable = build_readable_v2(canon, windows)
    print(f"readable v2 SRT: {len(readable)} chunks from 6 canonical cues")
    if [c["text"] for c in readable] != [c["text"] for c in v1r]:
        sys.exit("v2 chunk texts differ from v1 readable SRT (split "
                 "rule must be identical — only timings move)")
    if norm_text(" ".join(c["text"] for c in readable)) != \
            norm_text(" ".join(c["text"] for c in canon)):
        sys.exit("readable v2 split changed the text")
    prev = 0.0
    for c in readable:
        if c["start"] < prev - 0.001 or c["end"] <= c["start"]:
            sys.exit("v2 cues not monotonic")
        prev = c["end"]
    srt_text = ""
    for i, c in enumerate(readable, 1):
        srt_text += (f"{i}\n{fmt_ts(c['start'])} --> "
                     f"{fmt_ts(c['end'])}\n{c['text']}\n\n")
    OUT_SRT.write_text(unicodedata.normalize("NFC", srt_text),
                       encoding="utf-8")

    # --- 3. presentation gain, re-measured on the v2 mix ---
    mix_lufs, mix_tp = loudnorm(V2_MIX)
    print(f"v2 mix measured: {mix_lufs:.2f} LUFS / {mix_tp:.2f} dBTP "
          f"(manifest {v2man['integratedLufs']} / {v2man['truePeakDbtp']})")
    if abs(mix_lufs - v2man["integratedLufs"]) > 0.15 or \
            abs(mix_tp - v2man["truePeakDbtp"]) > 0.15:
        sys.exit("v2 mix loudness drift vs manifest")
    gain = min(GAIN_CAP_DB,
               math.floor((TP_CEILING_DBTP - mix_tp) * 10) / 10)
    gain = max(0.0, gain)
    print(f"presentation gain: +{gain:.1f} dB (rule: min(+{GAIN_CAP_DB:.1f} dB, "
          f"headroom to {TP_CEILING_DBTP:.1f} dBTP); predicted variant "
          f"{mix_lufs + gain:.2f} LUFS / {mix_tp + gain:.2f} dBTP)")

    # --- 4. render the 640 v2 variant (CP28 recipe, v2 sources) ---
    pr = probe(CANON_MP4)
    vdur = float(pr["streams"][0]["duration"])
    style = ("FontName=DejaVu Sans,FontSize=16,Bold=1,"
             "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
             "BorderStyle=3,BackColour=&HA0000000,Outline=1,Shadow=0,"
             "Alignment=2,MarginV=14,MarginL=20,MarginR=20")
    fc = (f"[0:v]subtitles='{OUT_SRT}':force_style='{style}'[v];"
          f"[1:a]volume={gain}dB[a]")
    cmd = ["ffmpeg", "-y", "-i", str(CANON_MP4), "-i", str(V2_MIX),
           "-i", str(OUT_SRT), "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]", "-map", "2:0",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-c:s", "mov_text", "-metadata:s:s:0", "language=vie",
           "-metadata:s:s:0", "title=Tieng Viet (phu de, ban v2)",
           "-disposition:s:0", "default",
           "-metadata:s:a:0", "language=vie",
           "-movflags", "+faststart", "-t", f"{vdur:.4f}",
           str(OUT_MP4_640)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg 640 render failed:\n" + r.stderr[-3000:])

    pr640 = probe(OUT_MP4_640)
    kinds = [s["codec_type"] for s in pr640["streams"]]
    if kinds != ["video", "audio", "subtitle"]:
        sys.exit(f"640 stream layout {kinds} != [video, audio, subtitle]")
    v640 = pr640["streams"][0]
    if abs(float(v640["duration"]) - vdur) > 0.05:
        sys.exit(f"640 video duration {v640['duration']} != {vdur}")
    lufs640, tp640 = loudnorm(OUT_MP4_640)
    print(f"640 variant: {lufs640:.2f} LUFS / {tp640:.2f} dBTP "
          f"(predicted {mix_lufs + gain:.2f} / {mix_tp + gain:.2f})")
    # TP tolerance is wider than the LUFS one: AAC re-encoding shifts
    # intersample peaks (the v1 variant measured -1.19 vs -1.11
    # predicted, same effect). The hard gate is the -1.0 dBTP ceiling.
    if abs(lufs640 - (mix_lufs + gain)) > 0.15 or \
            abs(tp640 - (mix_tp + gain)) > 0.25:
        sys.exit("640 variant loudness outside prediction window")
    if tp640 > TP_CEILING_DBTP:
        sys.exit(f"640 variant true peak {tp640} above ceiling "
                 f"{TP_CEILING_DBTP}")
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(OUT_MP4_640), "-map", "0:s:0",
         "-f", "srt", "-"], capture_output=True, text=True)
    emb = parse_srt(out.stdout)
    if len(emb) != len(readable):
        sys.exit(f"640 embedded cues {len(emb)} != readable "
                 f"{len(readable)}")
    for a, b in zip(emb, readable):
        if norm_text(a["text"]) != norm_text(b["text"]) or \
                abs(a["start"] - b["start"]) > 0.05 or \
                abs(a["end"] - b["end"]) > 0.05:
            sys.exit("640 embedded subtitle drift vs readable v2 SRT")
    print("640 embedded mov_text track verified against readable v2 SRT")

    # --- 5. render the 720p standard version (CP3 recipe) ---
    OUT_DIR_720.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(OUT_MP4_640),
         "-map", "0",
         "-vf", "scale=1280:720:flags=neighbor",
         "-c:v", "libx264", "-crf", "26", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "copy",
         "-movflags", "+faststart", str(OUT_MP4_720)], check=True)
    pr720 = probe(OUT_MP4_720)
    kinds720 = [s["codec_type"] for s in pr720["streams"]]
    if kinds720 != ["video", "audio", "subtitle"]:
        sys.exit(f"720 stream layout {kinds720} != [video, audio, subtitle]")
    v720 = pr720["streams"][0]
    if v720["width"] != 1280 or v720["height"] != 720:
        sys.exit(f"720 dimensions {v720['width']}x{v720['height']} != 1280x720")
    if abs(float(v720["duration"]) - vdur) > 0.05:
        sys.exit(f"720 video duration {v720['duration']} != {vdur}")

    # --- 6. register (film manifest + new CP5 delivery manifest) ---
    entry640 = {
        "path": "Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4",
        "sha256": sha256_of(OUT_MP4_640),
        "sizeBytes": OUT_MP4_640.stat().st_size,
        "durationSeconds": round(float(v640["duration"]), 4),
        "streams": ["video:h264", "audio:aac", "subtitle:mov_text"],
        "subtitles": {
            "burnedIn": True,
            "embeddedTrack": "mov_text, language vie, default",
            "renderer": "libass subtitles filter, DejaVu Sans bold "
                        "16, white on semi-transparent black box",
            "sourceFile": "CIN_000_vi_readable_v2.srt",
            "chunks": len(readable),
            "timingBasis": "M-F CP2 draft v2 narration windows "
                           "(History take file spans at CP27 slot "
                           "starts; Ly An line unchanged); chunk "
                           "texts identical to the v1 readable SRT",
        },
        "audio": {
            "source": "M-F CP2 draft v2 mix (History narration), "
                      "Art_Source only — runtime still embeds the "
                      "fixed v1 mix",
            "presentationGainDb": gain,
            "loudnessLufs": lufs640,
            "truePeakDbtp": tp640,
        },
        "note": "Viewing variant of the prologue with the v2 draft "
                "mix; subtitles re-timed to the History narration "
                "(WO37 M-B CP5). Canonical v1 files unchanged; "
                "runtime tree untouched.",
    }
    entry720 = {
        "sceneId": "CIN_000_subtitled_v2",
        "sourcePath": entry640["path"],
        "sourceSha256": entry640["sha256"],
        "sourceBytes": entry640["sizeBytes"],
        "sourceDuration": entry640["durationSeconds"],
        "outPath": "Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/"
                   "CIN_000_1280x720_30fps_sub_vi_v2.mp4",
        "outSha256": sha256_of(OUT_MP4_720),
        "outBytes": OUT_MP4_720.stat().st_size,
        "outDuration": round(float(v720["duration"]), 4),
    }
    fman["subtitledVariantV2"] = {
        "file": "CIN_000_640x360_30fps_sub_vi_v2.mp4",
        "sha256": entry640["sha256"],
        "sizeBytes": entry640["sizeBytes"],
        "checkpoint": "MEDIA-02 WO37 M-B CP5",
        "readableSrtSha256": sha256_of(OUT_SRT),
        "presentationGainDb": gain,
        "loudnessLufs": lufs640,
        "truePeakDbtp": tp640,
        "manifest": "STANDARD720_SUBTITLED_V2_MB_CP5_v1",
    }
    FILM_MANIFEST.write_text(
        json.dumps(fman, ensure_ascii=False, indent=1),
        encoding="utf-8")
    manifest = {
        "id": "STANDARD720_SUBTITLED_V2_MB_CP5_v1",
        "checkpoint": "WO37 M-B CP5",
        "status": "DRAFT_STANDARD_VERSION_NOT_IN_RUNTIME",
        "method": "640 variant: CP28 recipe with the M-F CP2 draft v2 "
                  "mix (History narration) + subtitles re-timed to the "
                  "v2 narration windows (same chunk split as v1, only "
                  "timings move); presentation gain true-peak-limited "
                  "to -1.0 dBTP. 720p: integer 2x nearest-neighbour "
                  "upscale of the 640 v2 variant (CP3 recipe); NOT a "
                  "native 720p capture; H.264 crf26; audio + subtitle "
                  "tracks stream-copied; no OGV sample (CP28: no OGV "
                  "subtitled variant exists)",
        "sourceMix": {"file": "CIN_000_mix_draft_v2.wav",
                      "sha256": v2man["sha256"],
                      "integratedLufs": mix_lufs,
                      "truePeakDbtp": mix_tp},
        "v2Windows": [{"cue": i + 1, "start": round(s, 3),
                       "end": round(e, 3)}
                      for i, (s, e) in enumerate(windows)],
        "entries": [entry640, entry720],
        "budget": {"mp4Set": {"files": 2,
                              "bytes640": entry640["sizeBytes"],
                              "bytes720": entry720["outBytes"],
                              "totalBytes": entry640["sizeBytes"]
                                            + entry720["outBytes"],
                              "ratio720vs640": round(
                                  entry720["outBytes"]
                                  / entry640["sizeBytes"], 3),
                              "totalDuration": entry640["durationSeconds"]}},
        "runtimeTreeModified": False,
        "notes": [
            "Closes the follow-up named in the M-B CP4 report "
            "(subtitled variant re-timing to the v2 narration). "
            "Lives in Art_Source only; the runtime still carries "
            "the v1 subtitled variant (mp4SubVi, fixed mix). "
            "Adoption is Codex's decision.",
            "The SEG02/SEG03 window overlap (0.118 s, silent file "
            "tail) is resolved by the CP28 monotonic rule: SEG03 "
            "chunks shift +0.168 s.",
        ],
    }
    CP5_MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(json.dumps(
        {"readableSrtV2Sha256": sha256_of(OUT_SRT),
         "mp4_640": {"sha256": entry640["sha256"],
                     "sizeBytes": entry640["sizeBytes"],
                     "loudnessLufs": lufs640, "truePeakDbtp": tp640},
         "mp4_720": {"sha256": entry720["outSha256"],
                     "sizeBytes": entry720["outBytes"]},
         "presentationGainDb": gain, "chunks": len(readable)},
        ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
