#!/usr/bin/env python3
"""Prologue v1 plumbing fix -- DELIVERY (owner order 2026-11-13).

Installs the plumbing-fixed CP27 mix render
(build_prologue_mix_v1_fixed.py, PROLOGUE_DRAFT_V1_FIXED) at the
canonical v1 paths and re-derives every file that embedded the
broken mix:

  1. Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav
     and its runtime copy ClientGodot/assets/audio/mix/prologue/
     PROLOGUE_mix_v1.wav are replaced by the fixed render (same
     deliverable, defect corrected; broken bytes stay in git
     history, sha f026ed3e...). PROLOGUE_mix_manifest_v1.json is
     updated with the new measurements + a plumbingFix record.
  2. Runtime film CIN_000_640x360_30fps.mp4 is re-muxed: video
     stream copied bit-exact from the current MP4, audio = fixed
     mix encoded AAC 192k (the CP27 mux recipe). The OGV is
     re-encoded from the new MP4 with the CP27 settings
     (libtheora q:v 7, libvorbis q:a 5).
  3. The CP28 subtitled viewing variant is re-rendered with the
     CP28 recipe (burned-in readable subtitles, audio = canonical
     MP4 audio + a presentation gain, embedded mov_text) -- with
     ONE measured adjustment: CP28's +5.0 dB gain was calibrated
     against the broken mix (true peak -9.08 dBTP, narration
     absent). The fixed mix's narration peaks at -3.11 dBTP, so
     +5.0 dB would push the variant past full scale (measured
     +5 dB render: -17.4 LUFS / -0.42 dBTP). The gain is
     therefore +2.0 dB (variant -20.4 LUFS / -1.1 dBTP): still a
     pure gain with no dynamics change, exactly CP28's method.
     The readable SRT itself is unchanged (canonical SRT
     unchanged), so the variant's subtitle content is identical;
     only its audio changes.
  4. The M-B CP3 standard-720p subtitled version is re-rendered
     with the CP3 recipe (integer 2x neighbour upscale, audio +
     subtitle stream-copied) and registered in a NEW manifest
     (STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json); the CP3
     manifest stays as the historical record.
  5. Registrations updated to the new bytes: film manifest,
     scene export manifest, RUNTIME_AUDIO_manifest (mix entry),
     RUNTIME_CINEMATICS_manifest (prologue entries),
     PLAYBACK_METADATA (CIN_000 measured loudness / durations /
     source mix sha).

Preconditions assert the CURRENT bytes are exactly the known
broken ones; the tool refuses to run over any other state.
Replaced files are backed up under /tmp (session safety only;
git history is the durable record). DRAFT_NOT_FINAL /
NOT_AUDITIONED throughout -- a defect correction, not a final.
"""
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FIX_DIR = ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED"
FIX_WAV = FIX_DIR / "PROLOGUE_mix_v1_fixed.wav"
FIX_MANIFEST = FIX_DIR / "PROLOGUE_MIX_V1_FIXED_manifest_v1.json"
AS_MIX = (ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
          / "PROLOGUE_mix_v1.wav")
AS_MIX_MANIFEST = AS_MIX.parent / "PROLOGUE_mix_manifest_v1.json"
RT_MIX = (ROOT / "ClientGodot/assets/audio/mix/prologue"
          / "PROLOGUE_mix_v1.wav")
CINE = ROOT / "ClientGodot/assets/cinematics/CIN_000"
MP4 = CINE / "CIN_000_640x360_30fps.mp4"
OGV = CINE / "CIN_000_640x360_30fps.ogv"
SUB_MP4 = CINE / "CIN_000_640x360_30fps_sub_vi.mp4"
READABLE_SRT = CINE / "CIN_000_vi_readable.srt"
EXPORT_MANIFEST = CINE / "scene_export_manifest_v1.json"
FILM_MANIFEST = (ROOT / "Art_Source/Cinematics/Prologue"
                 / "CIN000_film_manifest_v1.json")
RT_AUDIO_MANIFEST = (ROOT / "ClientGodot/assets/audio"
                     / "RUNTIME_AUDIO_manifest_v1.json")
RT_CINE_MANIFEST = (ROOT / "ClientGodot/assets/cinematics"
                    / "RUNTIME_CINEMATICS_manifest_v1.json")
PLAYBACK = (ROOT / "ClientGodot/assets/cinematics"
            / "PLAYBACK_METADATA_v1.json")
S720_DIR = ROOT / "Art_Source/Cinematics/Standard720/CIN_000_subtitled"
S720_MP4 = S720_DIR / "CIN_000_1280x720_30fps_sub_vi.mp4"
CP3_MANIFEST = (ROOT / "Implementation/Content/Narrative/Deliveries"
                / "STANDARD720_SUBTITLED_MB_CP3_v1.json")
FIX720_MANIFEST = (ROOT / "Implementation/Content/Narrative"
                   / "Deliveries"
                   / "STANDARD720_SUBTITLED_PROLOGUE_FIX_v1.json")
BACKUP = Path("/tmp/prologue_v1_fix_backup")
TMP = Path("/tmp/prologue_v1_fix")
TMP.mkdir(parents=True, exist_ok=True)

BROKEN_MIX_SHA = ("f026ed3e10499b42ea4fcc39ada9a1b42e0b5b749d16"
                  "ab77208afd54016ffb54")
OLD_MP4_SHA = ("8804931743e31d21c46c269f86b3deb65800668e3ec9c3e"
               "7c38d6a73057c2806")
OLD_OGV_SHA = ("f7323bcf0ec35a81357e2cfc80ba029f55df09b4"
               "a16492cf9001273f19c2cb4d")
OLD_SUB_SHA = ("2aae25e418c5c264efc494ac117a1416c555e8bb09efe0f"
               "55a4fb63f9d0ba25b")
FIX_NOTE = ("Prologue v1 plumbing fix (2026-11-13, owner order): "
            "the CP27 mix graph fed one ffmpeg label to two "
            "consumers and lost the narration; the mix was "
            "re-rendered with the plumbing corrected (apad + "
            "asplit), same takes / recipe / timeline, and the "
            "runtime film + variants were re-derived from it. "
            "Broken mix sha f026ed3e... stays in git history.")


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {cmd}\n"
                           f"{r.stderr[-1500:]}")
    return r


def probe(p):
    out = run(["ffprobe", "-v", "error", "-show_format",
               "-show_streams", "-of", "json", str(p)]).stdout
    return json.loads(out)


def loudnorm_audio(p):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"\{\s*\"input_i\".*?\}", out.stderr, re.S)
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_tp"])


def load_json(p):
    return json.loads(p.read_text(encoding="utf-8"))


def save_json(p, data):
    """Write JSON preserving the file's existing indent style."""
    old = p.read_text(encoding="utf-8") if p.exists() else ""
    indent = 1
    for line in old.splitlines()[1:6]:
        m = re.match(r"^( +)\S", line)
        if m:
            indent = len(m.group(1))
            break
    text = json.dumps(data, ensure_ascii=False, indent=indent)
    if old.endswith("\n") or not old:
        text += "\n"
    p.write_text(text, encoding="utf-8")


def parse_srt(text):
    cues = []
    for block in re.split(r"\r?\n\r?\n", text.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*"
                     r"(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        cues.append({
            "start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
            "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0,
            "text": " ".join(lines[2:]).strip()})
    return cues


def norm_text(s):
    return re.sub(r"\s+", " ", s).strip()


def stream_dur(pr):
    return round(float(pr["streams"][0].get("duration")
                       or pr["format"]["duration"]), 4)


def main() -> int:
    # ---------- preconditions: current bytes are the broken ones
    fixman = load_json(FIX_MANIFEST)
    assert sha256_of(FIX_WAV) == fixman["sha256"], "fixed mix drift"
    assert sha256_of(AS_MIX) == BROKEN_MIX_SHA, "Art_Source mix "\
        "is not the known broken bytes"
    assert sha256_of(RT_MIX) == BROKEN_MIX_SHA, "runtime mix is "\
        "not the known broken bytes"
    assert sha256_of(MP4) == OLD_MP4_SHA, "runtime MP4 drift"
    assert sha256_of(OGV) == OLD_OGV_SHA, "runtime OGV drift"
    assert sha256_of(SUB_MP4) == OLD_SUB_SHA, "subtitled MP4 drift"
    cp3 = load_json(CP3_MANIFEST)
    old720 = cp3["entries"][0]
    assert sha256_of(S720_MP4) == old720["outSha256"], "720p sub "\
        "drift vs CP3 manifest"
    exp = load_json(EXPORT_MANIFEST)
    assert sha256_of(READABLE_SRT) == exp["readableSrt"]["sha256"]
    print("preconditions OK: all current bytes are the known "
          "broken / derived ones")

    BACKUP.mkdir(parents=True, exist_ok=True)
    for f in (AS_MIX, RT_MIX, MP4, OGV, SUB_MP4, S720_MP4):
        shutil.copyfile(f, BACKUP / f.name)
    print(f"backups in {BACKUP}")

    fixed_sha = fixman["sha256"]
    fixed_lufs = fixman["integratedLufs"]
    fixed_tp = fixman["truePeakDbtp"]

    # ---------- 1. install the fixed mix at the canonical paths
    shutil.copyfile(FIX_WAV, AS_MIX)
    shutil.copyfile(FIX_WAV, RT_MIX)
    assert sha256_of(AS_MIX) == fixed_sha == sha256_of(RT_MIX)
    mman = load_json(AS_MIX_MANIFEST)
    mman["sha256"] = fixed_sha
    mman["sizeBytes"] = AS_MIX.stat().st_size
    mman["integratedLufs"] = fixed_lufs
    mman["truePeakDbtp"] = fixed_tp
    mman["plumbingFix"] = {
        "checkpoint": "MEDIA-02 prologue v1 plumbing fix "
                      "(2026-11-13)",
        "defect": "CP27 graph fed the single [vo] label to both "
                  "the sidechaincompress key and the final amix; "
                  "narration frames were stolen between "
                  "consumers (take-vs-mix correlations "
                  "0.008-0.020; renders non-reproducible)",
        "supersededSha256": BROKEN_MIX_SHA,
        "supersededMeasurements": {"integratedLufs": -20.81,
                                   "truePeakDbtp": -9.08},
        "fixedRender": "Art_Source/Audio/Muse/MIX/"
                       "PROLOGUE_DRAFT_V1_FIXED/"
                       "PROLOGUE_mix_v1_fixed.wav",
        "fixedRenderManifest": "Art_Source/Audio/Muse/MIX/"
                               "PROLOGUE_DRAFT_V1_FIXED/"
                               "PROLOGUE_MIX_V1_FIXED_manifest"
                               "_v1.json",
        "recipeDeltaVsCp27": "NONE (plumbing only: apad + "
                             "asplit on the VO bus)",
        "ownerApproval": "main chat 2026-11-13 02:58 JST",
    }
    mman.setdefault("notes", []).append(FIX_NOTE)
    save_json(AS_MIX_MANIFEST, mman)
    print("mix installed + mix manifest updated")

    # ---------- 2. re-mux the runtime film
    new_mp4 = TMP / "CIN_000_640x360_30fps.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(MP4),
         "-i", str(FIX_WAV), "-map", "0:v:0", "-map", "1:a:0",
         "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(new_mp4)])
    shutil.copyfile(new_mp4, MP4)
    new_ogv = TMP / "CIN_000_640x360_30fps.ogv"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(MP4),
         "-c:v", "libtheora", "-q:v", "7", "-c:a", "libvorbis",
         "-q:a", "5", str(new_ogv)])
    shutil.copyfile(new_ogv, OGV)
    mp4_pr, ogv_pr = probe(MP4), probe(OGV)
    mp4_lufs, mp4_tp = loudnorm_audio(MP4)
    ogv_lufs, ogv_tp = loudnorm_audio(OGV)
    print(f"film re-muxed: MP4 {sha256_of(MP4)[:16]}... "
          f"{mp4_lufs:.2f} LUFS; OGV {sha256_of(OGV)[:16]}... "
          f"{ogv_lufs:.2f} LUFS")

    # ---------- 3. subtitled variant (CP28 recipe)
    style = ("FontName=DejaVu Sans,FontSize=16,Bold=1,"
             "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
             "BorderStyle=3,BackColour=&HA0000000,Outline=1,"
             "Shadow=0,Alignment=2,MarginV=14,MarginL=20,"
             "MarginR=20")
    fc = (f"[0:v]subtitles='{READABLE_SRT}':force_style='{style}'"
          f"[v];[0:a]volume=2.0dB[a]")
    new_sub = TMP / "CIN_000_640x360_30fps_sub_vi.mp4"
    run(["ffmpeg", "-y", "-i", str(MP4), "-i", str(READABLE_SRT),
         "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
         "-map", "1:0", "-c:v", "libx264", "-preset", "medium",
         "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
         "-c:s", "mov_text", "-metadata:s:s:0", "language=vie",
         "-metadata:s:s:0", "title=Tieng Viet (phu de)",
         "-disposition:s:0", "default",
         "-metadata:s:a:0", "language=vie",
         "-movflags", "+faststart", str(new_sub)])
    sub_pr = probe(new_sub)
    kinds = [s["codec_type"] for s in sub_pr["streams"]]
    assert kinds == ["video", "audio", "subtitle"], kinds
    sub_lufs, sub_tp = loudnorm_audio(new_sub)
    assert fixed_lufs + 1.3 <= sub_lufs <= fixed_lufs + 2.7 \
        and sub_tp <= -0.9, (sub_lufs, sub_tp)
    emb = parse_srt(run(["ffmpeg", "-v", "error", "-i",
                         str(new_sub), "-map", "0:s:0", "-f",
                         "srt", "-"]).stdout)
    readable = parse_srt(READABLE_SRT.read_text(encoding="utf-8"))
    assert len(emb) == len(readable), (len(emb), len(readable))
    for a, b in zip(emb, readable):
        assert norm_text(a["text"]) == norm_text(b["text"])
        assert abs(a["start"] - b["start"]) <= 0.05
        assert abs(a["end"] - b["end"]) <= 0.05
    shutil.copyfile(new_sub, SUB_MP4)
    print(f"subtitled variant re-rendered: "
          f"{sha256_of(SUB_MP4)[:16]}... {sub_lufs:.2f} LUFS / "
          f"{sub_tp:.2f} dBTP, embedded track verified")

    # ---------- 4. 720p subtitled (CP3 recipe) + new manifest
    new720 = TMP / "CIN_000_1280x720_30fps_sub_vi.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(SUB_MP4),
         "-map", "0", "-vf", "scale=1280:720:flags=neighbor",
         "-c:v", "libx264", "-crf", "26", "-preset", "medium",
         "-pix_fmt", "yuv420p", "-c:a", "copy", "-c:s", "copy",
         "-movflags", "+faststart", str(new720)])
    shutil.copyfile(new720, S720_MP4)
    s720_pr = probe(S720_MP4)
    v720 = next(s for s in s720_pr["streams"]
                if s["codec_type"] == "video")
    assert (v720["width"], v720["height"]) == (1280, 720)
    entry720 = {
        "sceneId": "CIN_000_subtitled",
        "sourcePath": "ClientGodot/assets/cinematics/CIN_000/"
                      "CIN_000_640x360_30fps_sub_vi.mp4",
        "sourceSha256": sha256_of(SUB_MP4),
        "sourceBytes": SUB_MP4.stat().st_size,
        "sourceDuration": stream_dur(sub_pr),
        "outPath": "Art_Source/Cinematics/Standard720/"
                   "CIN_000_subtitled/"
                   "CIN_000_1280x720_30fps_sub_vi.mp4",
        "outSha256": sha256_of(S720_MP4),
        "outBytes": S720_MP4.stat().st_size,
        "outDuration": stream_dur(s720_pr),
        "supersedesCp3OutSha256": old720["outSha256"],
    }
    man720 = {
        "id": "STANDARD720_SUBTITLED_PROLOGUE_FIX_v1",
        "checkpoint": "MEDIA-02 prologue v1 plumbing fix "
                      "(2026-11-13)",
        "status": "DRAFT_STANDARD_VERSION_NOT_IN_RUNTIME",
        "method": "integer 2x nearest-neighbour upscale of the "
                  "re-rendered 640x360 subtitled viewing variant; "
                  "NOT a native 720p capture; H.264 crf26; audio "
                  "stream-copied bit-exact; embedded mov_text "
                  "subtitle track stream-copied (CP3 recipe, "
                  "unchanged)",
        "reason": "The CP28 subtitled variant derived from the "
                  "broken CP27 mix; after the plumbing fix it was "
                  "re-rendered from the fixed mix, so its 720p "
                  "standard version is re-derived here. The CP3 "
                  "manifest (STANDARD720_SUBTITLED_MB_CP3_v1) "
                  "stays as the historical record of the "
                  "pre-fix bytes.",
        "entries": [entry720],
        "runtimeTreeModified": False,
        "notes": [FIX_NOTE],
    }
    save_json(FIX720_MANIFEST, man720)
    print(f"720p subtitled re-rendered: "
          f"{entry720['outSha256'][:16]}... "
          f"{entry720['outBytes']} B")

    # ---------- 5. registrations
    mp4_entry = {"path": "ClientGodot/assets/cinematics/CIN_000/"
                         "CIN_000_640x360_30fps.mp4",
                 "sha256": sha256_of(MP4),
                 "sizeBytes": MP4.stat().st_size,
                 "durationSeconds": stream_dur(mp4_pr)}
    ogv_entry = {"path": "ClientGodot/assets/cinematics/CIN_000/"
                         "CIN_000_640x360_30fps.ogv",
                 "sha256": sha256_of(OGV),
                 "sizeBytes": OGV.stat().st_size,
                 "durationSeconds": stream_dur(ogv_pr)}
    sub_entry = dict(exp["mp4SubVi"])
    sub_entry.update({
        "sha256": sha256_of(SUB_MP4),
        "sizeBytes": SUB_MP4.stat().st_size,
        "durationSeconds": stream_dur(sub_pr),
        "audio": {
            "source": "plumbing-fixed checkpoint 27 mix "
                      "embedded in the canonical MP4 (mix file "
                      "at PROLOGUE_DRAFT, fixed render "
                      "PROLOGUE_DRAFT_V1_FIXED)",
            "presentationGainDb": 2.0,
            "loudnessLufs": round(sub_lufs, 2),
            "truePeakDbtp": round(sub_tp, 2),
        },
        "note": "Owner-requested viewing variant (2026-11-06): "
                "on-screen Vietnamese subtitles + clearly "
                "audible narration. Re-rendered 2026-11-13 from "
                "the plumbing-fixed mix; subtitle content "
                "unchanged. Canonical MP4 / OGV carry the same "
                "fixed mix without the presentation gain.",
    })
    exp["mp4"] = mp4_entry
    exp["ogv"] = ogv_entry
    exp["mp4SubVi"] = sub_entry
    exp.setdefault("notes", []).append(FIX_NOTE)
    save_json(EXPORT_MANIFEST, exp)

    fman = load_json(FILM_MANIFEST)
    fman["mixSha256"] = fixed_sha
    fman["exports"]["mp4"] = mp4_entry
    fman["exports"]["ogv"] = ogv_entry
    fman["subtitledVariant"] = {
        "file": "CIN_000_640x360_30fps_sub_vi.mp4",
        "sha256": sub_entry["sha256"],
        "checkpoint": "MEDIA-02 checkpoint 28; re-rendered at "
                      "the prologue v1 plumbing fix (2026-11-13)",
        "readableSrtSha256": exp["readableSrt"]["sha256"],
    }
    fman["prologueV1PlumbingFix"] = {
        "date": "2026-11-13",
        "supersededMixSha256": BROKEN_MIX_SHA,
        "fixedMixSha256": fixed_sha,
        "note": FIX_NOTE,
    }
    save_json(FILM_MANIFEST, fman)

    ra = load_json(RT_AUDIO_MANIFEST)
    hits = [e for e in ra["files"]
            if e.get("runtimePath") == "assets/audio/mix/"
            "prologue/PROLOGUE_mix_v1.wav"]
    assert len(hits) == 1, len(hits)
    hits[0]["sha256"] = fixed_sha
    hits[0]["sizeBytes"] = RT_MIX.stat().st_size
    ra.setdefault("notes", []).append(FIX_NOTE)
    save_json(RT_AUDIO_MANIFEST, ra)

    rc = load_json(RT_CINE_MANIFEST)
    rc["prologue"]["mp4"] = mp4_entry
    rc["prologue"]["ogv"] = ogv_entry
    rc["prologue"]["mp4SubVi"] = sub_entry
    rc.setdefault("notes", []).append(FIX_NOTE)
    save_json(RT_CINE_MANIFEST, rc)

    pm = load_json(PLAYBACK)
    e0 = next(s for s in pm["scenes"] if s["sceneId"] == "CIN_000")
    e0["video"]["mp4"]["durationSecondsMeasured"] = round(
        float(mp4_pr["format"]["duration"]), 3)
    e0["video"]["mp4"]["embeddedLoudnessLUFS"] = round(mp4_lufs, 2)
    e0["video"]["mp4"]["embeddedTruePeakDBTP"] = round(mp4_tp, 2)
    e0["video"]["ogv"]["durationSecondsMeasured"] = round(
        float(ogv_pr["format"]["duration"]), 3)
    e0["video"]["ogv"]["embeddedLoudnessLUFS"] = round(ogv_lufs, 2)
    e0["video"]["ogv"]["embeddedTruePeakDBTP"] = round(ogv_tp, 2)
    em = e0["embeddedMix"]
    # NOTE: em["mixVersion"] is an ID string shared with the
    # playback pack + the pronunciation table fallback chain
    # (validate_media_deliveries compares them for equality);
    # it stays "prologue_mix_v1 (checkpoint 27)" -- the fix is
    # recorded via the sha / loudness fields below and the
    # plumbingFix records in the mix / film manifests.
    em["sourceMixSha256"] = fixed_sha
    em["sourceMixMeasuredLUFS"] = fixed_lufs
    em["sourceMixMeasuredTruePeakDBTP"] = fixed_tp
    em["embeddedVsSourceDeltaLUFS"] = round(
        abs(mp4_lufs - fixed_lufs), 2)
    save_json(PLAYBACK, pm)
    print("registrations updated: film / export / runtime audio "
          "/ runtime cinematics / playback metadata")
    print(json.dumps({
        "fixedMixSha256": fixed_sha,
        "mp4": mp4_entry, "ogv": ogv_entry,
        "mp4Loudness": [round(mp4_lufs, 2), round(mp4_tp, 2)],
        "ogvLoudness": [round(ogv_lufs, 2), round(ogv_tp, 2)],
        "subSha256": sub_entry["sha256"],
        "subLoudness": [round(sub_lufs, 2), round(sub_tp, 2)],
        "s720": entry720}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
