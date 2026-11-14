#!/usr/bin/env python3
"""WO38 M38-B builder: selective P0 runtime ingest subset.

Renders candidate-B OGV runtime-format files (video = M-C CP2 pose-animation
takes, audio = P0 draft mix v3 encoded from the WAV masters, mirroring the
existing runtime OGV encoding: Theora + Vorbis 160 kbps 48 kHz stereo) into
Art_Source/Cinematics/P0_Motion/candidate_m38a/ and writes the ingest subset
manifest Implementation/Content/Narrative/Deliveries/P0_INGEST_M38B_SUBSET_v1.json.

The runtime tree is NOT modified: candidate files live in Art_Source only.
All numbers are measured from real bytes (ffprobe / ffmpeg loudnorm).
"""
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CAND_DIR = ROOT / "Art_Source/Cinematics/P0_Motion/candidate_m38a"
TAKES_DIR = ROOT / "Art_Source/Cinematics/P0_Motion/takes"
MIX_DIR = ROOT / "ClientGodot/assets/audio/mix/p0_v3"
RT_DIR = ROOT / "ClientGodot/assets/cinematics"
M38A_SUBSET = ROOT / "Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json"
V3_MANIFEST = ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json"
SEAM_TABLE = ROOT / "Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json"
OUT = ROOT / "Implementation/Content/Narrative/Deliveries/P0_INGEST_M38B_SUBSET_v1.json"

SCENES = ["CIN_001", "CIN_002", "CIN_004"]
SPEAKERS = {"CIN_001": "NPC_LY_AN (Ly An)", "CIN_002": "NPC_TA_VAN_KHANH (Tạ Vân Khanh)",
            "CIN_004": "NPC_LY_AN (Ly An, voice off-screen per DEC-MEDIA-P0 Q2)"}
WINDOW_STATUS = {"CIN_001": "DECIDED_DEC_MEDIA_P0 (version B, 24.8-28.5 s)",
                 "CIN_002": "PROPOSED_CANDIDATE (timing v1)",
                 "CIN_004": "PROPOSED_CANDIDATE (timing v1)"}


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
    streams = []
    for s in d.get("streams", []):
        e = {"codecType": s["codec_type"], "codec": s["codec_name"]}
        if s["codec_type"] == "video":
            e.update({"width": s["width"], "height": s["height"], "fps": s["r_frame_rate"]})
        else:
            e.update({"sampleRateHz": int(s["sample_rate"]), "channels": s["channels"],
                      "bitRateBps": int(s["bit_rate"]) if s.get("bit_rate", "N/A") != "N/A" else None})
        streams.append(e)
    return {"durationSeconds": round(float(d["format"]["duration"]), 3), "streams": streams}


def loudnorm(p: Path) -> dict:
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-vn", "-af",
         "loudnorm=I=-23:TP=-2:LRA=11:print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r'"input_i"\s*:\s*"([-\d.]+)".*?"input_tp"\s*:\s*"([-\d.]+)"', r.stderr, re.S)
    if not m:
        raise RuntimeError(f"loudnorm parse failed for {p}")
    return {"integratedLUFS": float(m.group(1)), "truePeakDBTP": float(m.group(2))}


def entry(p: Path, role: str, with_probe=False, with_loudness=False) -> dict:
    e = {"path": str(p.relative_to(ROOT)), "sha256": sha256(p), "sizeBytes": p.stat().st_size,
         "role": role}
    if with_probe:
        e["probe"] = probe(p)
    if with_loudness:
        e["loudness"] = loudnorm(p)
    return e


def parse_srt(p: Path) -> dict:
    raw = p.read_bytes()
    text = raw.decode("utf-8")
    m = re.search(r"(\d+):(\d+):(\d+),(\d+)\s*-->\s*(\d+):(\d+):(\d+),(\d+)\s*\n(.+)", text)
    def t(h, mi, s, ms):
        return int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000.0
    return {"windowSeconds": [t(*m.groups()[:4]), t(*m.groups()[4:8])],
            "text": m.group(9).strip(),
            "encoding": {"utf8": True, "bom": raw.startswith(b"\xef\xbb\xbf"),
                         "nfc": unicodedata.is_normalized("NFC", text),
                         "crlf": b"\r\n" in raw, "cues": text.count("-->")}}


def render_ogv(scene: str) -> Path:
    src = TAKES_DIR / f"{scene}_pose_640x360_30fps.mp4"
    wav = MIX_DIR / f"{scene}_mix_draft_v3.wav"
    out = CAND_DIR / f"{scene}_candidateB_640x360_30fps.ogv"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(src), "-i", str(wav),
         "-map", "0:v:0", "-map", "1:a:0", "-c:v", "libtheora", "-q:v", "6",
         "-c:a", "libvorbis", "-b:a", "160k", "-ar", "48000", "-ac", "2", str(out)],
        check=True)
    return out


def main() -> int:
    v3 = json.loads(V3_MANIFEST.read_text(encoding="utf-8"))
    v3_scenes = {s["sceneId"]: s for s in v3["scenes"]}
    seams = {}
    st = json.loads(SEAM_TABLE.read_text(encoding="utf-8"))
    for row in st.get("seamTable", []):
        if row.get("version") == "composed":
            seams[row["cueKey"]] = row["wrapJumpMeasured"]
    m38a = json.loads(M38A_SUBSET.read_text(encoding="utf-8"))
    runtime_proof = {e["path"]: e["sha256"] for e in m38a["runtimeUnchangedProof"]}

    files, scenes = [], []
    for scene in SCENES:
        ogv = render_ogv(scene)
        b_mp4 = entry(TAKES_DIR / f"{scene}_pose_640x360_30fps.mp4",
                      "candidate B video+audio (review MP4, H.264/AAC)", with_probe=True)
        b_ogv = entry(ogv, "candidate B runtime-format file (Theora/Vorbis) — NEW in M38-B",
                      with_probe=True, with_loudness=True)
        wav = entry(MIX_DIR / f"{scene}_mix_draft_v3.wav",
                    "embedded soundtrack source master (mix v3, fully composed)",
                    with_loudness=True)
        rt = RT_DIR / scene
        rt_mp4 = entry(rt / f"{scene}_640x360_30fps.mp4",
                       "current runtime A file (panel-hold video + embedded mix v3)", with_probe=True)
        rt_ogv = entry(rt / f"{scene}_640x360_30fps.ogv",
                       "current runtime A file (panel-hold video + embedded mix v3)", with_probe=True)
        poster = entry(rt / f"{scene}_poster.png", "runtime poster (S01 keyframe) — unchanged by ingest")
        srt_path = rt / f"{scene}_vi.srt"
        srt = entry(srt_path, "runtime subtitle (external SRT) — unchanged by ingest")
        srt_info = parse_srt(srt_path)
        timing = entry(rt / f"{scene}_timing_v1.json", "runtime timing — unchanged by ingest")
        export_manifest = entry(rt / "scene_export_manifest_v1.json",
                                "runtime scene export manifest (CP34: A video + embedded mix v3)")
        # runtime-unchanged cross-proof vs the M38-A subset record
        for e in (rt_mp4, rt_ogv, poster):
            assert runtime_proof.get(e["path"]) == e["sha256"], f"runtime drift: {e['path']}"
        cues = []
        for stem in v3_scenes[scene]["stems"]:
            c = {"cue": stem["cue"], "role": stem["role"], "provenance": stem["provenance"]}
            if "segmentSceneSeconds" in stem:  # beds: music / ambience
                c.update({"segmentSceneSeconds": stem["segmentSceneSeconds"],
                          "targetLUFS": stem["targetLUFS"], "duckedByVo": stem["duckedByVo"]})
            else:  # stingers: single placement at unity gain
                c.update({"atSeconds": stem["atSeconds"],
                          "placementStatus": stem["placementStatus"]})
            if stem["cue"] in seams:
                c["loopSeamWrapJump"] = seams[stem["cue"]]
            cues.append(c)
        vo = v3_scenes[scene]["vo"]
        files += [b_mp4, b_ogv, wav, rt_mp4, rt_ogv, poster, srt, timing, export_manifest]
        scenes.append({
            "sceneId": scene,
            "durationSeconds": b_ogv["probe"]["durationSeconds"],
            "dialogue": {"speaker": SPEAKERS[scene], "windowSeconds": srt_info["windowSeconds"],
                         "windowStatus": WINDOW_STATUS[scene], "srtText": srt_info["text"],
                         "voTakeInMix": vo["take"],
                         "voTakeEndSeconds": vo["windowSeconds"][1],
                         "srt": srt_info},
            "candidateVideo": {"mp4": b_mp4, "ogv": b_ogv},
            "runtimeCurrent": {"mp4": rt_mp4, "ogv": rt_ogv, "poster": poster, "srt": srt,
                               "timing": timing, "sceneExportManifest": export_manifest},
            "embeddedSoundtrack": {"mixVersion": "v3_fully_composed", "sourceMixWav": wav,
                                   "cues": cues},
            "ingestAction": ("REPLACE the video file with candidate B (MP4 for review contexts, "
                             "OGV for the Godot runtime). KEEP poster, SRT and timing byte-identical. "
                             "Audio needs no action: A and B embed the same mix v3."),
        })

    reel = entry(CAND_DIR / "P0_candidate_review_72s_640x360_30fps.mp4",
                 "combined 72 s review reel (M38-A)", with_probe=True)
    sheet = entry(CAND_DIR / "P0_candidate_contact_all12.png",
                  "combined contact sheet, all 12 shots (M38-A)")
    files += [reel, sheet]

    manifest = {
        "manifestId": "NGM_P0_INGEST_M38B_SUBSET_V1",
        "workOrder": "WO38 M38-B (Goi 38, issue #116 comment 6733227370, PR #130) — selective P0 runtime ingest guide subset",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "parentHead": "67a9c744240349f1057774dc130cc91ac98bb74b",
        "qaBaselineSha": "14b588c663a6d53295b34f1d632e84c48c7f5ca9",
        "integrationSha": "9ac73dc",
        "status": "DRAFT_FOR_CODEX_REVIEW — NOT_AUDITIONED, no mix PASS, no self-PASS; M38-B does NOT modify the runtime tree",
        "scope": "P0 only: CIN_001 (36 s), CIN_002 (18 s), CIN_004 (18 s) — 72 s total",
        "audioPathRule": {
            "rule": "EXACTLY ONE audio path per playback. Recommended: EMBEDDED_SOUNDTRACK_ONLY (matches ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json audioOwnershipPolicy).",
            "embedded": "Play the video file's own audio stream (mix v3, fully composed). A and B embed the SAME mix v3, so adopting B changes picture only.",
            "externalAlternative": "Only if the adapter deliberately chooses external audio: mute/ignore the embedded stream and play the standalone mix WAV/OGG as the single source. Never play embedded + standalone mix or VO takes simultaneously (double audio).",
            "neverDo": "Do not layer palette pickups, VO takes or stems over the embedded soundtrack; they are alternates/components for review, not playback layers.",
        },
        "subtitleRule": "External SRT (UTF-8, NFC, LF, no BOM), one cue per P0 scene, shown by the player; subtitles are NOT baked into candidate video — do not enable a second caption source.",
        "seamNote": "Composed ambience/music runtime OGGs loop inside the mixes with a 1 s acrossfade join (CP31 recipe). loopSeamWrapJump per cue is the CP44 raw wrap discontinuity of the composed runtime file; all P0 cues are <= 0.002311 and none is ear-check flagged (the flagged cue MUSIC/sa_hoa is not in P0).",
        "fallback": {
            "videoFallback": "Current runtime A files (panel-hold video + embedded mix v3) stay in place until Codex adopts B; they are the fallback take. Poster is the static fallback frame.",
            "formatFallback": "If the OGV fails to decode in a review context, use the candidate B MP4 (same picture, same mix as AAC). Runtime playback stays OGV per project standard.",
            "audioFallback": "If embedded audio is rejected at review, the standalone mix v3 WAV (ClientGodot/assets/audio/mix/p0_v3/) is the single external source — see audioPathRule.externalAlternative. Mix v1/v2 remain review alternates, never simultaneous.",
        },
        "provenanceLicense": {
            "musicAmbienceStingers": "ORIGINAL_COMPOSED_BY_MUSE — procedural synthesis, no samples (CP26/CP30); 0 ported PackV1 files inside mix v3 or the candidate.",
            "voice": "Fictional TTS draft voices (Ly An = avocado_v2 Aria; the CIN_002 male line still uses the shared male draft voice of CP04; M-F CP1 palette pickups are alternates NOT embedded in this candidate). No real-voice cloning.",
            "picture": "Procedural pose animation rendered from storyboard keyframes (M-C CP2); keyframes derive from the Cinema Production Pack shot prompts. Draft picture — final picture still character-lock-blocked for 6 of 12 P0 shots.",
        },
        "auditionStatus": "NOT_AUDITIONED — use the CP9 ear-audition pack (Implementation/Reports/MuseMedia/, EAR_AUDITION_PACK_v1.json) for the real listening pass; unlistened items carry no PASS from Muse.",
        "deviceStatus": "No physical playback device is available to Muse in this environment and Muse performs no Godot playback (runtime side is Codex's). Prior evidence: Codex's Windows audit at 14b588c decoded the first 50 ms of all 21 embedded soundtracks PASS and verified the runtime subset byte/size/hash.",
        "scenes": scenes,
        "reviewAssets": {"combinedReel": reel, "contactSheetAll12": sheet},
        "files": files,
        "fileCount": len(files),
    }
    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(files)} file entries")
    for s in scenes:
        o = s["candidateVideo"]["ogv"]
        print(s["sceneId"], "OGV", o["sizeBytes"], "B", o["probe"]["durationSeconds"], "s",
              "LUFS", o["loudness"]["integratedLUFS"], "vs WAV",
              s["embeddedSoundtrack"]["sourceMixWav"]["loudness"]["integratedLUFS"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
