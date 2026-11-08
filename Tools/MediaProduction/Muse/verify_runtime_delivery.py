#!/usr/bin/env python3
"""MEDIA-02 checkpoint 11 (M8 handover/QA): re-verify the checkpoint-10
runtime delivery still matches its manifests, file by file, from real bytes.

Checks every entry of the two runtime manifests:
  ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json (545 audio files)
  ClientGodot/assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json
    (3 animatic files + 20 scenes x timing JSON + SRT)

Per file: existence, LFS-pointer detection, size, sha256; audio files also
get ffprobe codec / sample rate / channels / duration (+-0.02 s) when the
manifest carries those fields. This tool does NOT re-measure loudness
(checkpoints 02/04/07/08 already measured it from real bytes) and does NOT
re-validate the source packs (validate_media_deliveries.py does that).

Usage: python3 verify_runtime_delivery.py [--out <json>]
Exit code 0 = no mismatches; 1 = at least one mismatch (details in JSON).
Only reads the repo tree; writes only the JSON report passed via --out.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CLIENT = ROOT / "ClientGodot"
ERRORS = []
NOTES = []
COUNTS = {}


def err(msg):
    ERRORS.append(msg)


def note(msg):
    NOTES.append(msg)


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_lfs_pointer(path):
    try:
        with open(path, "rb") as f:
            return f.read(40).startswith(b"version https://git-lfs")
    except OSError:
        return False


def probe(path):
    """ffprobe first stream + format duration; returns dict or None."""
    try:
        out = subprocess.check_output(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", str(path)],
            text=True, timeout=120)
    except Exception as exc:
        err(f"ffprobe failed for {path}: {exc}")
        return None
    data = json.loads(out)
    streams = data.get("streams") or []
    if not streams:
        err(f"ffprobe found no stream in {path}")
        return None
    s = streams[0]
    dur = None
    try:
        dur = float(s.get("duration") or data["format"]["duration"])
    except Exception:
        pass
    return {
        "codec": s.get("codec_name"),
        "sample_rate": int(s["sample_rate"]) if s.get("sample_rate") else None,
        "channels": s.get("channels"),
        "duration": dur,
    }


def check_file(rel_client_path, want_sha, want_size, label, audio_fields=None):
    """rel_client_path is relative to ClientGodot/ (e.g. assets/audio/...)."""
    path = CLIENT / rel_client_path
    if not path.exists():
        err(f"{label}: MISSING {rel_client_path}")
        return
    if is_lfs_pointer(path):
        err(f"{label}: LFS POINTER, not real bytes: {rel_client_path}")
        return
    size = path.stat().st_size
    if want_size is not None and size != want_size:
        err(f"{label}: size {size} != manifest {want_size}: {rel_client_path}")
    digest = sha256_of(path)
    if want_sha is not None and digest != want_sha:
        err(f"{label}: sha256 mismatch: {rel_client_path}")
    if audio_fields:
        p = probe(path)
        if p is None:
            return
        if audio_fields.get("codec") and p["codec"] != audio_fields["codec"]:
            err(f"{label}: codec {p['codec']} != manifest {audio_fields['codec']}: {rel_client_path}")
        if audio_fields.get("sampleRateHz") and p["sample_rate"] != audio_fields["sampleRateHz"]:
            err(f"{label}: sample_rate {p['sample_rate']} != manifest {audio_fields['sampleRateHz']}: {rel_client_path}")
        if audio_fields.get("channels") and p["channels"] != audio_fields["channels"]:
            err(f"{label}: channels {p['channels']} != manifest {audio_fields['channels']}: {rel_client_path}")
        if audio_fields.get("durationSeconds") is not None and p["duration"] is not None:
            if abs(p["duration"] - audio_fields["durationSeconds"]) > 0.02:
                err(f"{label}: duration {p['duration']:.4f} != manifest {audio_fields['durationSeconds']}: {rel_client_path}")


def check_audio_manifest():
    manifest = json.loads((CLIENT / "assets/audio/RUNTIME_AUDIO_manifest_v1.json").read_text(encoding="utf-8"))
    files = manifest["files"]
    total = 0
    for entry in files:
        check_file(entry["runtimePath"], entry["sha256"], entry["sizeBytes"],
                   f"AUDIO {entry.get('cueKey', entry['runtimePath'])}", audio_fields=entry)
        total += 1
    COUNTS["runtime_audio_files_checked"] = total
    COUNTS["runtime_audio_manifest_total"] = manifest["totalFiles"]
    if total != manifest["totalFiles"]:
        err(f"AUDIO manifest totalFiles {manifest['totalFiles']} != entries checked {total}")
    note(f"Audio manifest counts: {manifest['counts']}")


def check_cinematics_manifest():
    manifest = json.loads((CLIENT / "assets/cinematics/RUNTIME_CINEMATICS_manifest_v1.json").read_text(encoding="utf-8"))
    anim = 0
    for entry in manifest["animatic"]:
        check_file(entry["runtimePath"], entry["sha256"], entry["sizeBytes"],
                   f"ANIMATIC {entry['runtimePath']}")
        anim += 1
    scenes = 0
    timing = 0
    srt = 0
    for scene in manifest["scenes"]:
        scenes += 1
        check_file(scene["timingFile"], scene["timingSha256"], None,
                   f"TIMING {scene['sceneId']}")
        timing += 1
        check_file(scene["srtFile"], scene["srtSha256"], None,
                   f"SRT {scene['sceneId']}")
        srt += 1
    clips = 0
    clip_files = 0
    for clip in manifest.get("sceneClips", []):
        clips += 1
        for key, f in clip.get("files", {}).items():
            audio_fields = None
            if key in ("mp4", "ogv"):
                audio_fields = {"durationSeconds": f["durationSeconds"]}
            check_file(f["path"], f["sha256"], f["sizeBytes"],
                       f"SCENE-CLIP {clip['sceneId']}/{key}",
                       audio_fields=audio_fields)
            clip_files += 1
    pro = manifest.get("prologue")
    pro_files = 0
    if pro is None:
        err("CINEMATICS manifest has no 'prologue' entry (cp27)")
    else:
        for key in ("mp4", "ogv", "poster"):
            f = pro[key]
            rel = f["path"]
            if rel.startswith("ClientGodot/"):
                rel = rel[len("ClientGodot/"):]
            audio_fields = None
            if key in ("mp4", "ogv"):
                audio_fields = {"durationSeconds":
                                f["durationSeconds"]}
            check_file(rel, f["sha256"], f["sizeBytes"],
                       f"PROLOGUE {key}", audio_fields=audio_fields)
            pro_files += 1
        check_file(pro["timingFile"], pro["timingSha256"], None,
                   "PROLOGUE timing")
        check_file(pro["srtFile"], pro["srtSha256"], None,
                   "PROLOGUE srt")
        pro_files += 2
        if "mp4SubVi" in pro:
            f = pro["mp4SubVi"]
            rel = f["path"]
            if rel.startswith("ClientGodot/"):
                rel = rel[len("ClientGodot/"):]
            check_file(rel, f["sha256"], f["sizeBytes"],
                       "PROLOGUE mp4SubVi",
                       audio_fields={"durationSeconds":
                                     f["durationSeconds"]})
            pro_files += 1
            pr = json.loads(subprocess.run(
                ["ffprobe", "-v", "error", "-show_streams", "-of",
                 "json", str(CLIENT / rel)],
                capture_output=True, text=True).stdout)
            kinds = [s["codec_type"] for s in pr["streams"]]
            if kinds != ["video", "audio", "subtitle"]:
                err(f"PROLOGUE mp4SubVi: streams {kinds} != "
                    f"[video, audio, subtitle]")
            check_file(pro["readableSrtFile"],
                       pro["readableSrtSha256"], None,
                       "PROLOGUE readable srt")
            pro_files += 1
    COUNTS["prologue_files_checked"] = pro_files
    COUNTS["animatic_files_checked"] = anim
    COUNTS["cinematics_scenes_checked"] = scenes
    COUNTS["timing_files_checked"] = timing
    COUNTS["srt_files_checked"] = srt
    COUNTS["scene_clips_checked"] = clips
    COUNTS["scene_clip_files_checked"] = clip_files
    if clips != 20:
        err(f"CINEMATICS manifest sceneClips {clips} != 20")
    totals = manifest.get("campaignTotals", {})
    if totals.get("scenes") != scenes:
        err(f"CINEMATICS manifest scenes {totals.get('scenes')} != checked {scenes}")
    note(f"Campaign totals in manifest: {totals}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    check_audio_manifest()
    check_cinematics_manifest()
    result = {
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 7 (phase layers: thang_long intensity, tran_son intensity, bach_uyen intensity, rift_finale intensity, quiet_discovery intensity under assets/audio/composed/layers/; runtime audio manifest total 731 -> 736; WO37 M-B big checkpoint 1 (21 embedded soundtracks) unchanged) - runtime re-verification",
        "base_integration": "6f79853",
        "branch": "muse/media-production-20261104",
        "verifies": "checkpoint 10 runtime delivery as revised by checkpoint 13 (animatic v2), checkpoint 14 (dialogueCues fix), checkpoint 15 (LF + LFS fix), checkpoint 16 (animatic v3: CIN_002_S02 corrected keyframe + 16:9 keyframes), checkpoint 17 (campaign VO: 17 takes + 378 s timeline), checkpoint 18 (per-scene clips: CIN_001/CIN_002/CIN_004 video + CIN_006 timing/SRT only) checkpoint 19 (CIN_006 VO: canonical + alternate takes + 18 s timeline), checkpoint 20 (P0 draft mixes: 3 scenes + 72 s review) checkpoint 21 (CIN_005 animated take: 3 keyframes + 18 s clip), checkpoint 22 (CIN_006 animated take: 3 keyframes + 18 s clip; CIN_006 leaves PENDING_PANELS_NO_STORYBOARD) checkpoint 23 (CIN_009 animated take: 3 keyframes + 18 s clip; first Chapter 2 campaign scene with video) and checkpoint 24 (CIN_020 animated take: 3 keyframes + 18 s clip; closing campaign scene with video; CIN_009 keyframe manifest title corrected) and checkpoint 25 (campaign video batch: animated takes for the remaining 13 campaign scenes, 3 keyframes + 18 s clip each; all 20 scenes now carry video) and checkpoint 26 (original composed music + cinema stingers: 13 cues registered in the runtime audio manifest under assets/audio/composed/, parallel to the untouched ported packs) and checkpoint 27 (prologue film CIN_000: 5 narration VO takes + film mix in the audio manifest, total 589; the film registered under the cinematics manifest's separate 'prologue' key, campaign totals unchanged) and checkpoint 28 (prologue subtitled viewing variant: mp4SubVi with burned-in + embedded readable Vietnamese subtitles and +5 dB narration presentation gain, plus CIN_000_vi_readable.srt, registered under the same 'prologue' key; canonical prologue files unchanged; prologue files checked now 7) and checkpoint 29 (P0 draft mixes v2 from checkpoint-26 composed stems: 3 scenes + 72 s review under mix/p0_v2/, parallel to the untouched v1 mixes; runtime audio manifest total 593) and checkpoint 30 (original composed ambience: all 13 AMBIENCE/* cues under assets/audio/composed/ambience/, parallel to the untouched ported packs; runtime audio manifest total 606) and checkpoint 31 (P0 draft mixes v3 from fully composed stems: 3 scenes + 72 s review under mix/p0_v3/, parallel to the untouched v1/v2 mixes; runtime audio manifest total 610) and checkpoint 32 (Goi 31 item 2: shot-content fixes -- CIN_012_S03 English UI bar, CIN_017_S02 missing crystal core/serpent, CIN_015_S02 dry-courtyard setting failure -- plus unprompted mascot/character cleanup, bandage left/right and environment continuity; 14 revised keyframes across 8 scenes, re-exported video, before/after contact sheets; runtime audio manifest total still 610) and checkpoint 33 (A/B review shortlist: no runtime files added or changed; 6 M3U playlists in Implementation/Reports/MuseMedia/ reference the delivered runtime audio by path + sha256; audition status NOT_AUDITIONED) and checkpoint 34 (Goi 31 item 4: minimal runtime pack -- P0 mixes v3 + CIN_006 mix v1 embedded in the runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 611) and checkpoint 35 (Goi 31 item 5 prep: fresh-checkout verification tool + negative control; no runtime files added or changed) and checkpoint 36 (D-12 name-label fix: canonical spelling 'Tạ Vân Khanh' per owner decision 2026-11-07; labels/metadata only, no runtime files added or changed) and checkpoint 37 (CIN_003 draft mix v1: ben_mua music + river_shore ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; embedded in CIN_003 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 612, mix 15) and checkpoint 38 (CIN_005 draft mix v1: thang_long music + thang_long_crowd ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; VO overrun +0.160 s KEPT per owner verdict; embedded in CIN_005 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 613, mix 16) and checkpoint 39 (CIN_007 draft mix v1: quiet_discovery music + wind_canopy ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; VO take fits inside its window, ends 16.412 s; embedded in CIN_007 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 614, mix 17) and checkpoint 40 (CIN_008 draft mix v1: tran_son music + river_shore ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; VO take fits inside its window, ends 16.052 s; embedded in CIN_008 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 615, mix 18) and checkpoint 41 (CIN_009 draft mix v1: lam_trieu music + waterfall ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; VO take fits inside its window, ends 16.580 s; embedded in CIN_009 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 616, mix 19) and checkpoint 42 (CIN_010 draft mix v1: sa_hoa music + desert_wind ambience + reveal stinger + CP17 draft VO, same P0 v3 recipe; VO take fits inside its window, ends 15.308 s; embedded in CIN_010 runtime OGV + review MP4, video streams bit-identical; runtime audio manifest total 617, mix 20) and checkpoint 43 (playback metadata for embedded mixes, Codex WO32 item 4: PLAYBACK_METADATA_v1.json added beside the cinematics manifests with per-scene embeddedMix/voice/subtitle source and audio ownership, verified from real bytes; no runtime media files added or changed; runtime audio manifest total stays 617) and checkpoint 44 (pronunciation/proper-name table + gap/head-tail/ducking/seam cues + fallback playback, Codex WO32 item 3: PRONUNCIATION_TABLE_v1.json added under Implementation/Content/Audio/Deliveries/ — 16 names, 17 playback cue rows, 19 seam rows, 21 fallback rows — verified from real bytes; no runtime media files added or changed; runtime audio manifest total stays 617) and checkpoint 45 (CIN_011 draft mix v1: quiet_discovery music + wind_canopy ambience + reveal stinger + CP17 draft VO at 12.2 s, take fits its 12.2-17.8 s window by 0.008 s; embedded in CIN_011 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 12 embedded soundtracks, 9 silent CIN_012-020, 18 playback cue rows; runtime audio manifest total 618, mix 21) and checkpoint 46 (CIN_012 draft mix v1: tran_son music + forge ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 0.680 s; embedded in CIN_012 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 13 embedded soundtracks, 8 silent CIN_013-020, 19 playback cue rows, 20 seam rows; runtime audio manifest total 619, mix 22) and checkpoint 47 (CIN_013 draft mix v1: lam_trieu music + mountain_wind ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 2.528 s; embedded in CIN_013 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 14 embedded soundtracks, 7 silent CIN_014-020, 20 playback cue rows, 21 seam rows; runtime audio manifest total 620, mix 23; integration baseline re-pinned 6f2b465 -> 6f79853) and checkpoint 48 (CIN_014 draft mix v1: ben_mua music + wind_canopy ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 1.928 s; embedded in CIN_014 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 15 embedded soundtracks, 6 silent CIN_015-020, 21 playback cue rows; runtime audio manifest total 621, mix 24) and checkpoint 49 (CIN_015 draft mix v1: bach_uyen music + underwater ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 2.120 s; embedded in CIN_015 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 16 embedded soundtracks, 5 silent CIN_016-020, 22 playback cue rows, 22 seam rows; runtime audio manifest total 622, mix 25) and checkpoint 50 (CIN_016 draft mix v1: quiet_discovery music + wind_canopy ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 2.528 s; embedded in CIN_016 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 17 embedded soundtracks, 4 silent CIN_017-020, 23 playback cue rows, 22 seam rows; runtime audio manifest total 623, mix 26) and checkpoint 51 (CIN_017 draft mix v1: bach_uyen music + underwater ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 1.832 s; embedded in CIN_017 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 18 embedded soundtracks, 3 silent CIN_018-020, 24 playback cue rows, 22 seam rows; runtime audio manifest total 624, mix 27) and checkpoint 52 (CIN_018 draft mix v1: sa_hoa music + desert_wind ambience + reveal stinger at 0.0 s + TWO CP17 draft VO takes, S02 fits its 6.5-11.5 s window by 2.120 s, S03 overrun +0.280 s KEPT per owner verdict, same P0 v3 recipe; embedded in CIN_018 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 19 embedded soundtracks, 2 silent CIN_019-020, 25 playback cue rows, 22 seam rows; runtime audio manifest total 625, mix 28) and checkpoint 53 (CIN_019 draft mix v1: rift_finale music + river_shore ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 2.120 s; embedded in CIN_019 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 20 embedded soundtracks, 1 silent CIN_020, 26 playback cue rows, 23 seam rows; runtime audio manifest total 626, mix 29) and checkpoint 54 (CIN_020 draft mix v1: ben_mua music + river_shore ambience + reveal stinger + CP17 draft VO at 12.5 s, take fits its 12.5-17.5 s window by 2.000 s; embedded in CIN_020 runtime OGV + review MP4, video streams bit-identical; playback metadata + pronunciation table re-run: 21 embedded soundtracks, 0 silent, 27 playback cue rows, 23 seam rows; runtime audio manifest total 627, mix 30; WO37 M-B big checkpoint 1 complete) and WO37 M-D checkpoint 1 (MD1 score batch: 7 missing core cues + 3 transition bridges under assets/audio/composed/music/ and assets/audio/composed/transitions/, 15/15 M-D slots covered, 0 gaps; runtime audio manifest total 627 -> 637) and WO37 M-D checkpoint 2 (MD2 intro/outro + stems + phase layers: 7 intros + 7 outros + 21 stems + 2 layers under assets/audio/composed/intros|outros|stems|layers/; stems sum to their MD1 parent master within 24-bit quantisation; runtime audio manifest total 637 -> 674) and WO37 M-D checkpoint 3 (MD3 intro/outro + stems + phase layers: 9 intros + 9 outros + 27 stems + 3 layers under assets/audio/composed/intros|outros|stems|layers/; stems sum to their checkpoint-26 parent master within 24-bit quantisation; runtime audio manifest total 674 -> 722) and WO37 M-D checkpoint 4 (MD4 phase layers: boss phase 4, swamp intensity, dungeon intensity under assets/audio/composed/layers/; runtime audio manifest total 722 -> 725) and WO37 M-D checkpoint 5 (MD5 phase layers: boss phase 5, hub intensity, rain intensity under assets/audio/composed/layers/; runtime audio manifest total 725 -> 728) and WO37 M-D checkpoint 6 (MD6 phase layers: ben_mua intensity, lam_trieu intensity, sa_hoa intensity under assets/audio/composed/layers/; runtime audio manifest total 728 -> 731) and WO37 M-D checkpoint 7 (MD7 phase layers: thang_long intensity, tran_son intensity, bach_uyen intensity, rift_finale intensity, quiet_discovery intensity under assets/audio/composed/layers/; runtime audio manifest total 731 -> 736) and WO37 M-D checkpoint 8 (MD8 phase layer: thanh_lac intensity under assets/audio/composed/layers/; runtime audio manifest total 736 -> 737; after MD8 every composed score cue carries an intensity layer) (RUNTIME_AUDIO_manifest_v1.json + RUNTIME_CINEMATICS_manifest_v1.json)",
        "counts": COUNTS,
        "mismatches": ERRORS,
        "notes": NOTES,
        "verdict": "PASS" if not ERRORS else "MISMATCHES_FOUND",
        "limits": [
            "Loudness/true-peak values are NOT re-measured here; they come from checkpoints 02/04/07/08/17/19/20/26/29/30/31/33/34/37, measured from real bytes.",
            "This check verifies runtime copies still match their manifests; it does not verify the source packs (see validate_media_deliveries.py, re-run at checkpoint 11).",
            "NOT a mix PASS and NOT an ear audition; NOT a Godot wiring check (presentation adapter is Codex's work).",
            "Checkpoint 33 adds no runtime files: the A/B shortlist (JSON + 6 M3U playlists + report) lives in Implementation/Reports/MuseMedia/ and references the already-delivered runtime audio by path + sha256; audition status NOT_AUDITIONED.",
        ],
    }
    print(f"counts: {json.dumps(COUNTS, indent=1)}")
    print(f"mismatches: {len(ERRORS)}")
    for e in ERRORS[:50]:
        print("  MISMATCH: " + e)
    print(f"notes: {len(NOTES)}")
    for n in NOTES[:20]:
        print("  NOTE: " + n)
    print("verdict: " + result["verdict"])
    if args.out:
        Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report written: {args.out}")
    return 0 if not ERRORS else 1


if __name__ == "__main__":
    sys.exit(main())
