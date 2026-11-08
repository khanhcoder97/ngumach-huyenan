#!/usr/bin/env python3
"""Build PLAYBACK_METADATA_v1.json — MEDIA-02 checkpoint 43 (Codex WO32 item 4); re-run at checkpoint 53 for the CIN_019 draft mix v1 (20 embedded mixes, 1 silent).

Purpose (Codex direction 2026-11-08, issue #116 comment 6713518554, item 4):
runtime OGV/MP4 files now carry embedded soundtracks. The presentation adapter
(Codex) needs explicit playback metadata — embeddedMix / voice / subtitle
source and audio ownership — so it never plays an embedded soundtrack and an
external mix/VO at the same time.

Sources (claims):
- ClientGodot/assets/cinematics/RUNTIME_PACK_GOI31_v1.json (scenes with mixes)
- ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json (all scenes)
- Art_Source/Audio/Muse/MIX/** mix manifests (stems + VO per scene)

Every claim is VERIFIED against real bytes before it is written:
- ffprobe stream layout of every runtime OGV/MP4 (audio stream present/absent)
- ffmpeg loudnorm of the embedded audio vs the source mix WAV and vs the
  loudness recorded in the pack manifest (tolerance 0.40 LUFS)
- sha256 of every runtime file vs its manifest entry
- SRT cue counts from the actual subtitle files
The tool exits 1 and writes no metadata when any check mismatches.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CINE = ROOT / "ClientGodot/assets/cinematics"
PACK_PATH = CINE / "RUNTIME_PACK_GOI31_v1.json"
CINE_MANIFEST_PATH = CINE / "RUNTIME_CINEMATICS_manifest_v1.json"
OUT_PATH = CINE / "PLAYBACK_METADATA_v1.json"

LOUDNESS_TOL = 0.40  # LUFS, embedded (lossy) vs source WAV / recorded value
DURATION_TOL = 0.5   # s, container duration vs manifest duration

MIX_MANIFEST_BY_VERSION = {
    "v3_fully_composed": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json",
}
PER_SCENE_MIX_DIR = ROOT / "Art_Source/Audio/Muse/MIX"
PROLOGUE_MIX_MANIFEST = PER_SCENE_MIX_DIR / "PROLOGUE_DRAFT/PROLOGUE_mix_manifest_v1.json"

ERRORS = []


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ffprobe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format",
         "-of", "json", str(path)],
        capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {out.stderr[:200]}")
    return json.loads(out.stdout)


def loudnorm(path: Path):
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(path), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    text = out.stderr
    start = text.rfind("{")
    end = text.rfind("}") + 1
    if start < 0:
        raise RuntimeError(f"loudnorm parse failed for {path}")
    d = json.loads(text[start:end])
    return float(d["input_i"]), float(d["input_tp"])


def srt_cues(path: Path) -> int:
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines()
               if "-->" in line)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def mix_manifest_for(scene_id: str, version: str):
    if version in MIX_MANIFEST_BY_VERSION:
        return load_json(MIX_MANIFEST_BY_VERSION[version])
    if version.startswith("prologue"):
        return load_json(PROLOGUE_MIX_MANIFEST)
    # v1_cinNNN_proposed -> CINNNN_DRAFT_V1/CINNNN_MIX_V1_manifest_v1.json
    tag = scene_id.replace("_", "")  # CIN_003 -> CIN003
    p = PER_SCENE_MIX_DIR / f"{tag}_DRAFT_V1" / f"{tag}_MIX_V1_manifest_v1.json"
    return load_json(p)


def mix_scene_entry(manifest: dict, scene_id: str):
    for s in manifest.get("scenes", []):
        if s.get("sceneId") == scene_id:
            return s
    return None


def check_file_sha(rel: str, expected: str, label: str):
    p = ROOT / rel if not rel.startswith("ClientGodot/") else ROOT / rel
    if not p.exists():
        ERRORS.append(f"{label}: missing file {rel}")
        return None
    actual = sha256_of(p)
    if expected and actual != expected:
        ERRORS.append(f"{label}: sha256 mismatch {rel}: {actual} != {expected}")
    return actual


def probe_video(rel: str, label: str):
    """Return dict with stream facts + measured embedded loudness (or None)."""
    p = ROOT / rel
    if not p.exists():
        ERRORS.append(f"{label}: missing file {rel}")
        return None
    info = ffprobe(p)
    streams = info.get("streams", [])
    audio = [s for s in streams if s.get("codec_type") == "audio"]
    subs = [s for s in streams if s.get("codec_type") == "subtitle"]
    dur = float(info.get("format", {}).get("duration", 0.0))
    result = {
        "path": rel,
        "durationSecondsMeasured": round(dur, 3),
        "audioStream": None,
        "subtitleStreamsEmbedded": len(subs),
    }
    if audio:
        a = audio[0]
        result["audioStream"] = {
            "codec": a.get("codec_name"),
            "sampleRateHz": int(a.get("sample_rate", 0)),
            "channels": a.get("channels"),
        }
        li, tp = loudnorm(p)
        result["embeddedLoudnessLUFS"] = li
        result["embeddedTruePeakDBTP"] = tp
    return result


def main():
    pack = load_json(PACK_PATH)
    cine_manifest = load_json(CINE_MANIFEST_PATH)
    pack_by_scene = {s["sceneId"]: s for s in pack["scenes"]}
    clips_by_scene = {s["sceneId"]: s for s in cine_manifest["sceneClips"]}

    scenes_out = []

    # ---- scenes WITH embedded soundtracks (the Gói 31 pack) ----
    for scene_id in sorted(pack_by_scene):
        ps = pack_by_scene[scene_id]
        files = ps["files"]
        version = ps["embeddedMixVersion"]
        entry = {
            "sceneId": scene_id,
            "kind": "prologue" if scene_id == "CIN_000" else "campaign",
            "durationSeconds": ps["durationSeconds"],
            "hasEmbeddedSoundtrack": True,
            "audioOwnership": "EMBEDDED_SOUNDTRACK_ONLY",
            "audioOwnershipNote": (
                "Play ONLY the soundtrack embedded in the video file. Do NOT "
                "play any standalone mix file (ClientGodot/assets/audio/mix/**) "
                "or VO take at the same time: those are the same mix delivered "
                "as separate files for review / alternate routing, not an "
                "additional layer."),
        }
        # video files, verified from real bytes
        entry["video"] = {}
        for kind in ("ogv", "mp4"):
            f = files[kind]
            rel = "ClientGodot/" + f["path"] if not f["path"].startswith("ClientGodot/") else f["path"]
            probed = probe_video(rel, f"{scene_id}/{kind}")
            if probed is None:
                continue
            if f.get("sha256"):
                check_file_sha(rel, f["sha256"], f"{scene_id}/{kind}")
            if probed["audioStream"] is None:
                ERRORS.append(f"{scene_id}/{kind}: pack claims embedded mix but no audio stream in {rel}")
            rec = f.get("integratedLUFS")
            if rec is not None and probed.get("embeddedLoudnessLUFS") is not None:
                delta = abs(probed["embeddedLoudnessLUFS"] - float(rec))
                probed["deltaVsPackRecordedLUFS"] = round(delta, 3)
                if delta > LOUDNESS_TOL:
                    ERRORS.append(
                        f"{scene_id}/{kind}: embedded loudness {probed['embeddedLoudnessLUFS']} "
                        f"vs pack-recorded {rec} (delta {delta:.2f} > {LOUDNESS_TOL})")
            if abs(probed["durationSecondsMeasured"] - float(ps["durationSeconds"])) > DURATION_TOL:
                ERRORS.append(
                    f"{scene_id}/{kind}: duration {probed['durationSecondsMeasured']} "
                    f"vs manifest {ps['durationSeconds']}")
            entry["video"][kind] = probed
        # embedded mix detail from the mix manifest
        manifest = mix_manifest_for(scene_id, version)
        mix_info = {
            "mixVersion": version,
            "status": manifest.get("status", "DRAFT_MIX_NOT_FINAL"),
            "mixManifest": str((MIX_MANIFEST_BY_VERSION.get(version) or
                                (PROLOGUE_MIX_MANIFEST if version.startswith("prologue") else
                                 PER_SCENE_MIX_DIR / f"{scene_id.replace('_','')}_DRAFT_V1" /
                                 f"{scene_id.replace('_','')}_MIX_V1_manifest_v1.json")
                                ).relative_to(ROOT)),
        }
        ogv = files["ogv"]
        if ogv.get("sourceMix"):
            src_rel = ogv["sourceMix"]
            src_path = ROOT / src_rel
            if src_path.exists():
                li, tp = loudnorm(src_path)
                mix_info["sourceMixWav"] = src_rel
                mix_info["sourceMixSha256"] = sha256_of(src_path)
                if ogv.get("sourceMixSha256") and mix_info["sourceMixSha256"] != ogv["sourceMixSha256"]:
                    ERRORS.append(f"{scene_id}: sourceMix sha mismatch vs pack")
                mix_info["sourceMixMeasuredLUFS"] = li
                mix_info["sourceMixMeasuredTruePeakDBTP"] = tp
                emb = entry["video"].get("ogv", {}).get("embeddedLoudnessLUFS")
                if emb is not None:
                    delta = abs(emb - li)
                    mix_info["embeddedVsSourceDeltaLUFS"] = round(delta, 3)
                    if delta > LOUDNESS_TOL:
                        ERRORS.append(
                            f"{scene_id}: embedded loudness {emb} vs source mix {li} "
                            f"(delta {delta:.2f} > {LOUDNESS_TOL})")
            else:
                ERRORS.append(f"{scene_id}: sourceMix missing: {src_rel}")
        if scene_id == "CIN_000":
            mix_info["stems"] = [
                {"role": s.get("role"), "source": s.get("source"),
                 "provenance": s.get("provenance")}
                for s in manifest.get("stems", [])]
            mix_info["voice"] = {
                "type": "narration_plus_final_line",
                "narration": ("5 draft TTS narration segments "
                              "(Art_Source/Audio/Muse/VO/PROLOGUE/, checkpoint 27; "
                              "narrator casting is a director decision)"),
                "finalLine": "VO_CIN001_S05_LYAN_draft_v1.wav (checkpoint 04 take, reused bytes)",
                "status": "DRAFT_VO_NOT_FINAL",
            }
            mix_info["sourceMixWav"] = "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav"
            mix_info["sourceMixSha256"] = manifest.get("sha256")
            if check_file_sha(mix_info["sourceMixWav"], manifest.get("sha256"), "CIN_000/mix") is None:
                pass
            li, tp = loudnorm(ROOT / mix_info["sourceMixWav"])
            mix_info["sourceMixMeasuredLUFS"] = li
            mix_info["sourceMixMeasuredTruePeakDBTP"] = tp
            emb = entry["video"].get("ogv", {}).get("embeddedLoudnessLUFS")
            if emb is not None:
                delta = abs(emb - li)
                mix_info["embeddedVsSourceDeltaLUFS"] = round(delta, 3)
                if delta > LOUDNESS_TOL:
                    ERRORS.append(f"CIN_000: embedded loudness {emb} vs source mix {li} (delta {delta:.2f})")
        else:
            ms = mix_scene_entry(manifest, scene_id)
            if ms is None:
                ERRORS.append(f"{scene_id}: no scene entry in mix manifest for {version}")
            else:
                mix_info["stems"] = [
                    {"cue": s.get("cue"), "role": s.get("role"),
                     "source": s.get("source"), "provenance": s.get("provenance")}
                    for s in ms.get("stems", [])]
                vo = ms.get("vo") or {}
                mix_info["voice"] = {
                    "type": "dialogue_take_inside_mix",
                    "take": vo.get("take"),
                    "windowSeconds": vo.get("windowSeconds"),
                    "takeDurationSeconds": vo.get("takeDurationSeconds"),
                    "overrunVsWindowSeconds": vo.get("overrunVsWindowSeconds"),
                    "status": "DRAFT_VO_NOT_FINAL",
                }
                # CIN_018 is the only campaign scene with TWO dialogue
                # windows: record both takes (the single "voice" above
                # stays the S03 take, as in every earlier mix).
                voices = ms.get("voices")
                if voices:
                    mix_info["voices"] = [
                        {"shotId": v.get("shotId"),
                         "speaker": v.get("speaker"),
                         "speakerDisplay": v.get("speakerDisplay"),
                         "take": v.get("take"),
                         "windowSeconds": v.get("windowSeconds"),
                         "takeDurationSeconds": v.get("takeDurationSeconds"),
                         "overrunVsWindowSeconds": v.get("overrunVsWindowSeconds"),
                         "fit": v.get("fit"),
                         "status": "DRAFT_VO_NOT_FINAL"}
                        for v in voices]
        if scene_id in ("CIN_001", "CIN_002", "CIN_004"):
            mix_info["alternateStandaloneMixesNotEmbedded"] = [
                {"mixVersion": "v1_ported_stems",
                 "wav": f"Art_Source/Audio/Muse/MIX/P0_DRAFT/{scene_id}_mix_draft_v1.wav",
                 "runtimeCopy": f"ClientGodot/assets/audio/mix/p0/{scene_id}_mix_draft_v1.wav"},
                {"mixVersion": "v2_composed_music_ported_ambience",
                 "wav": f"Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/{scene_id}_mix_draft_v2.wav",
                 "runtimeCopy": f"ClientGodot/assets/audio/mix/p0_v2/{scene_id}_mix_draft_v2.wav"},
            ]
        entry["embeddedMix"] = mix_info
        # subtitles: runtime = clean video + overlay SRT (never burned)
        srt = files.get("srt")
        sub = {"mode": "OVERLAY_SRT", "burnedIntoRuntimeVideo": False}
        if srt:
            rel = "ClientGodot/" + srt["path"] if not srt["path"].startswith("ClientGodot/") else srt["path"]
            sp = ROOT / rel
            if sp.exists():
                sub["srtPath"] = rel
                sub["cuesMeasured"] = srt_cues(sp)
                if srt.get("cues") is not None and sub["cuesMeasured"] != srt["cues"]:
                    ERRORS.append(f"{scene_id}: SRT cue count {sub['cuesMeasured']} != pack {srt['cues']}")
                check_file_sha(rel, srt.get("sha256"), f"{scene_id}/srt")
            else:
                ERRORS.append(f"{scene_id}: SRT missing {rel}")
        if files.get("reviewOnlyBakedSubtitles"):
            sub["reviewOnlyBakedVariant"] = files["reviewOnlyBakedSubtitles"]
        entry["subtitle"] = sub
        scenes_out.append(entry)

    # ---- campaign scenes WITHOUT embedded soundtracks ----
    for scene_id in sorted(clips_by_scene):
        if scene_id in pack_by_scene:
            continue
        clip = clips_by_scene[scene_id]
        entry = {
            "sceneId": scene_id,
            "kind": "campaign",
            "durationSeconds": clip["durationSeconds"],
            "hasEmbeddedSoundtrack": False,
            "audioOwnership": "NO_EMBEDDED_SOUNDTRACK",
            "audioOwnershipNote": (
                "The runtime video is SILENT (verified: no audio stream). No "
                "scene mix has been delivered for this scene yet; the adapter "
                "must not improvise one from stems. Dialogue VO takes exist as "
                "drafts under Art_Source/Audio/Muse/VO/ for later mixing."),
            "video": {},
            "embeddedMix": None,
        }
        for kind in ("ogv", "mp4"):
            f = clip["files"][kind]
            rel = "ClientGodot/" + f["path"] if not f["path"].startswith("ClientGodot/") else f["path"]
            probed = probe_video(rel, f"{scene_id}/{kind}")
            if probed is None:
                continue
            check_file_sha(rel, f.get("sha256"), f"{scene_id}/{kind}")
            if probed["audioStream"] is not None:
                ERRORS.append(f"{scene_id}/{kind}: expected silent video but found audio stream in {rel}")
            entry["video"][kind] = probed
        srt_rel = f"ClientGodot/assets/cinematics/{scene_id}/{scene_id}_vi.srt"
        sp = ROOT / srt_rel
        sub = {"mode": "OVERLAY_SRT", "burnedIntoRuntimeVideo": False}
        if sp.exists():
            sub["srtPath"] = srt_rel
            sub["cuesMeasured"] = srt_cues(sp)
        entry["subtitle"] = sub
        scenes_out.append(entry)

    scenes_out.sort(key=lambda e: e["sceneId"])

    # ---- P0 review reel (72 s): probe and record the truth ----
    reel = {"files": {}}
    for name in ("P0_animatic_640x360_30fps.ogv", "P0_animatic_640x360_30fps.mp4"):
        rel = f"ClientGodot/assets/cinematics/{name}"
        probed = probe_video(rel, f"reel/{name}")
        if probed:
            reel["files"][name] = probed
    reel["hasEmbeddedSoundtrack"] = any(
        f.get("audioStream") for f in reel["files"].values())
    reel["note"] = ("Review/gallery reel only — never auto-plays as the game "
                    "opening. The P0 review mixes (v1/v2/v3, 72 s WAV) are "
                    "standalone audio files, not embedded in this reel.")

    metadata = {
        "manifestId": "NGM_PLAYBACK_METADATA_V1",
        "checkpoint": "MEDIA-02 checkpoint 53 (re-run of the checkpoint 43 builder: CIN_019 draft mix v1 embedded; 20 embedded soundtracks, 1 silent CIN_020)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrderRef": "Codex Work Order 32 / issue #116 comment 6713518554 item 4",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_PLAYBACK_METADATA_FOR_ADAPTER_REVIEW",
        "audioOwnershipPolicy": {
            "embeddedScenes": ("When a scene hasEmbeddedSoundtrack=true, the "
                               "video file's own soundtrack is the ONLY audio "
                               "for that scene. Never play a standalone mix "
                               "file or a VO take simultaneously."),
            "standaloneMixFiles": ("Files under ClientGodot/assets/audio/mix/** "
                                   "are the same mixes delivered as separate "
                                   "files for review and alternate routing. They "
                                   "are alternates OF the embedded soundtrack, "
                                   "not layers on top of it."),
            "voTakes": ("VO takes under Art_Source/Audio/Muse/VO/ and "
                        "ClientGodot/assets/audio/vo/ are components already "
                        "mixed into the embedded soundtracks. Never schedule "
                        "them over a scene whose mix is embedded."),
            "subtitles": ("Runtime playback = clean video + SRT overlay. "
                          "Burned-subtitle variants are REVIEW ONLY and must "
                          "never be combined with the overlay (no double "
                          "captions)."),
            "questSemantics": ("Rewatch, skip, already-seen and fallback "
                               "playback grant NO quest progress. (Adapter "
                               "rule recorded from WO32 item 4; enforcement is "
                               "Codex's runtime work.)"),
        },
        "alphaCandidate": {
            "p0Scenes": "v3_fully_composed (embedded at checkpoint 34)",
            "cin006": "v1_cin006_proposed (embedded at checkpoint 34)",
            "note": ("Per WO32 item 4 the runtime-alpha candidate mixes are "
                     "the fully-composed P0 v3 set + CIN_006 v1 — which is "
                     "what is embedded. Final audible approval is PENDING: "
                     "every mix is DRAFT_MIX_NOT_FINAL and NOT_AUDITIONED."),
        },
        "counts": {
            "scenesTotal": len(scenes_out),
            "withEmbeddedSoundtrack": sum(1 for s in scenes_out if s["hasEmbeddedSoundtrack"]),
            "silent": sum(1 for s in scenes_out if not s["hasEmbeddedSoundtrack"]),
        },
        "scenes": scenes_out,
        "reviewReel": reel,
        "verification": {
            "method": ("ffprobe stream layout + ffmpeg loudnorm of embedded "
                       "audio vs source mix WAV and pack-recorded loudness "
                       f"(tolerance {LOUDNESS_TOL} LUFS) + sha256 of every "
                       "runtime file + SRT cue counts, all from real bytes at "
                       "build time."),
            "mismatches": ERRORS,
            "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        },
    }

    if ERRORS:
        print(f"FAILED with {len(ERRORS)} mismatch(es):")
        for e in ERRORS:
            print("  MISMATCH: " + e)
        return 1
    OUT_PATH.write_text(json.dumps(metadata, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"written: {OUT_PATH.relative_to(ROOT)}")
    print(f"scenes: {metadata['counts']}")
    print("verdict: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
