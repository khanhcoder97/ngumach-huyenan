#!/usr/bin/env python3
"""MEDIA-02 WO37 M-F checkpoint 1 validator: re-verify the voice palette
and its 20 pickup takes from real bytes, independently of the builder.

Re-checks, without trusting the builder's in-memory values:
  - every palette WAV + raw MP3 exists and re-hashes to the pack values;
  - duration (ffprobe) and loudness/true peak (ffmpeg loudnorm) re-measured
    from real bytes match the pack within tolerance;
  - palette: 11 roles / 11 distinct voices; each take's voice matches its
    role; the CLI-returned voice matches the requested voice;
  - every pickup text is character-exact vs its canonical manifest take;
  - every pickup WAV differs in bytes from its canonical take (and the
    canonical files still hash to the values recorded at build time);
  - runtime manifest carries exactly 20 PALETTE_ALTERNATE entries whose
    sha/size/duration match the runtime copies;
  - pronunciation review pack: 5 spoken rows (4 distinct names), 12
    unspoken names, 10-entry A-B playlist, all files exist;
  - Ly An has no pickup (voice kept); the three kept canonical overruns
    are still recorded as unchanged.

Usage: python3 check_vo_palette_mf_cp1_v1.py [--out <json>]
Exit code 0 = 0 mismatches; 1 = at least one mismatch.
Only reads the repo tree; writes only the JSON report passed via --out.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ERRORS = []
NOTES = []
COUNTS = {}

DUR_TOL_S = 0.01
LUFS_TOL = 0.05
TP_TOL = 0.1


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


def probe(path):
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
    try:
        dur = float(s.get("duration") or data["format"]["duration"])
    except Exception:
        err(f"ffprobe found no duration in {path}")
        return None
    return {"codec": s.get("codec_name"),
            "sample_rate": int(s["sample_rate"]) if s.get("sample_rate") else None,
            "channels": s.get("channels"), "duration": dur}


def loudnorm(path):
    try:
        r = subprocess.run(
            ["ffmpeg", "-i", str(path), "-vn", "-af",
             "loudnorm=print_format=json", "-f", "null", "-"],
            capture_output=True, text=True, timeout=300)
    except Exception as exc:
        err(f"loudnorm failed for {path}: {exc}")
        return None
    tail = r.stderr.strip().splitlines()
    try:
        start = next(i for i, line in enumerate(tail) if line.strip() == "{")
        end = next(i for i, line in enumerate(tail) if line.strip() == "}")
    except StopIteration:
        err(f"loudnorm produced no JSON for {path}")
        return None
    return json.loads("\n".join(tail[start:end + 1]))


def check_measurements(path, label, expect_dur, expect_lufs, expect_tp):
    pr = probe(path)
    if pr is None:
        return
    if pr["codec"] != "pcm_s16le" or pr["sample_rate"] != 48000 \
            or pr["channels"] != 1:
        err(f"{label}: format {pr['codec']}/{pr['sample_rate']}/"
            f"{pr['channels']} != pcm_s16le/48000/mono")
    if abs(pr["duration"] - expect_dur) > DUR_TOL_S:
        err(f"{label}: duration {pr['duration']} != {expect_dur}")
    ln = loudnorm(path)
    if ln is None:
        return
    if abs(float(ln["input_i"]) - expect_lufs) > LUFS_TOL:
        err(f"{label}: LUFS {ln['input_i']} != {expect_lufs}")
    if abs(float(ln["input_tp"]) - expect_tp) > TP_TOL:
        err(f"{label}: true peak {ln['input_tp']} != {expect_tp}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    deliveries = ROOT / "Implementation/Content/Audio/Deliveries"
    pickup_dir = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"

    palette = json.loads((deliveries / "VOICE_PALETTE_v1.json").read_text(
        encoding="utf-8"))
    pack = json.loads((deliveries / "VO_PALETTE_PICKUPS_pack_v1.json")
                      .read_text(encoding="utf-8"))
    review = json.loads((deliveries / "PRONUNCIATION_REVIEW_PACK_v1.json")
                        .read_text(encoding="utf-8"))

    # ---- palette shape ----
    roles = palette["roles"]
    if len(roles) != 11:
        err(f"palette roles {len(roles)} != 11")
    voices = [r["voice"] for r in roles]
    if len(set(voices)) != 11:
        err("palette voices are not unique per role")
    if palette["counts"] != {"roles": 11, "distinctVoices": 11,
                             "keptVoices": 1, "newVoices": 10,
                             "pickupTakes": 20}:
        err(f"palette counts drift: {palette['counts']}")
    role_voice = {r["role"]: r["voice"] for r in roles}
    ly_an = [r for r in roles if r["role"] == "NPC_LYAN"]
    if len(ly_an) != 1 or ly_an[0]["paletteChange"] != "KEPT":
        err("Ly An palette entry missing or not KEPT")
    COUNTS["palette_roles"] = len(roles)

    # ---- pack shape ----
    if pack["counts"] != {"takes": 20, "dialogue": 14, "alternate": 1,
                         "narration": 5, "fits": 14, "overruns": 0}:
        err(f"pickup pack counts drift: {pack['counts']}")
    if pack.get("keptCanonicalOverrunsUnchanged") != [
            "CIN_005_S03 +0.160 s", "CIN_018_S03 +0.280 s",
            "CIN_006_S03 +0.520 s"]:
        err("kept canonical overruns record drift")
    takes = pack["takes"]
    if len(takes) != 20:
        err(f"pickup takes {len(takes)} != 20")
    if any(t["role"] == "NPC_LYAN" for t in takes):
        err("Ly An take found in pickups (voice was to be kept, not re-recorded)")

    files_checked = 0
    for t in takes:
        key = t["takeKey"]
        if role_voice.get(t["role"]) != t["voice"]:
            err(f"{key}: take voice {t['voice']} != palette role voice "
                f"{role_voice.get(t['role'])}")
        pal = t["paletteTake"]
        if pal["ttsReturnedVoice"] != t["voice"]:
            err(f"{key}: ttsReturnedVoice {pal['ttsReturnedVoice']} != {t['voice']}")
        # Text character-exact vs the canonical manifest take.
        canon = t["canonicalTake"]
        manifest = json.loads((ROOT / _manifest_for(key)).read_text(
            encoding="utf-8"))
        entries = manifest.get("takes") or manifest.get("segments")
        if t["kind"] == "narration":
            hit = [e for e in entries if e.get("takeId") == "VO_" + key]
        else:
            hit = [e for e in entries if e.get("wav") == canon["file"]]
        if len(hit) != 1:
            err(f"{key}: canonical manifest match -> {len(hit)}")
            continue
        if unicodedata.normalize("NFC", hit[0]["text"]) != \
                unicodedata.normalize("NFC", t["text"]):
            err(f"{key}: pickup text != canonical manifest text")
        # Canonical file still hashes to the build-time value.
        canon_path = ROOT / canon["dir"] / canon["file"]
        if not canon_path.exists():
            err(f"{key}: canonical file missing {canon_path}")
            continue
        if sha256_of(canon_path) != canon["sha256"]:
            err(f"{key}: canonical file hash drift")
        # Pickup WAV + raw MP3 re-hash + re-measure.
        wav_path = pickup_dir / pal["wav"]
        if not wav_path.exists():
            err(f"{key}: palette wav missing {wav_path}")
            continue
        if sha256_of(wav_path) != pal["wavSha256"]:
            err(f"{key}: palette wav hash mismatch")
        if pal["wavSha256"] == canon["sha256"]:
            err(f"{key}: palette wav identical to canonical take")
        raw_path = pickup_dir / pal["rawMp3"]
        if not raw_path.exists():
            err(f"{key}: raw mp3 missing {raw_path}")
            continue
        if sha256_of(raw_path) != pal["rawMp3Sha256"]:
            err(f"{key}: raw mp3 hash mismatch")
        if raw_path.stat().st_size != pal["rawMp3Bytes"]:
            err(f"{key}: raw mp3 size mismatch")
        check_measurements(wav_path, f"{key} palette wav",
                           pal["durationSeconds"], pal["integratedLufs"],
                           pal["truePeakDbtp"])
        files_checked += 2
        # Window fit recomputed from the pack's own numbers.
        if t["windowSceneSeconds"] is not None:
            win_len = float(t["windowSceneSeconds"][1]) - float(
                t["windowSceneSeconds"][0])
            expect_fit = "FITS" if pal["durationSeconds"] <= win_len + 1e-9 \
                else "OVERRUN"
            if t["fit"] != expect_fit:
                err(f"{key}: fit {t['fit']} != recomputed {expect_fit}")
            if abs(round(win_len - pal["durationSeconds"], 3)
                   - t["slackSeconds"]) > 1e-9:
                err(f"{key}: slack {t['slackSeconds']} != recomputed")
    COUNTS["pickup_files_checked"] = files_checked

    # ---- review pack shape ----
    if review["counts"] != {"spokenNames": 5, "distinctSpokenNames": 4,
                            "unspokenNames": 12, "abPairs": 5}:
        err(f"review pack counts drift: {review['counts']}")
    if len(review["spokenNames"]) != 5 or len(review["unspokenNames"]) != 12:
        err("review pack row counts drift")
    playlist_path = ROOT / "Implementation/Reports/MuseMedia" / \
        "vo_palette_review_playlist.txt"
    if not playlist_path.exists():
        err("review playlist file missing")
    else:
        lines = playlist_path.read_text(encoding="utf-8").splitlines()
        listed = [ln for ln in lines if ln and not ln.startswith("#")]
        if len(listed) != 10:
            err(f"review playlist entries {len(listed)} != 10")
        for p in listed:
            if not (ROOT / p).exists():
                err(f"review playlist path missing: {p}")
    for row in review["spokenNames"]:
        for side in ("aTake", "bTake"):
            if not row[side].get("estimatedNameTimecodeSeconds"):
                err(f"{row['name']} {side}: missing estimated timecode")
        if not row.get("listeningQuestions"):
            err(f"{row['name']}: missing listening questions")
    note(f"review pack: {len(review['spokenNames'])} spoken rows, "
         f"{len(review['unspokenNames'])} unspoken names, "
         f"10-entry A-B playlist")

    # ---- runtime manifest: exactly 20 PALETTE_ALTERNATE entries ----
    runtime = json.loads(
        (ROOT / "ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json")
        .read_text(encoding="utf-8"))
    pal_entries = [e for e in runtime["files"]
                   if e.get("takePurpose") == "PALETTE_ALTERNATE"]
    if len(pal_entries) != 20:
        err(f"runtime palette entries {len(pal_entries)} != 20")
    if runtime["totalFiles"] != 757:
        err(f"runtime totalFiles {runtime['totalFiles']} != 757")
    if runtime["counts"].get("vo") != 50:
        err(f"runtime vo count {runtime['counts'].get('vo')} != 50")
    pack_by_wav = {t["paletteTake"]["wav"]: t for t in takes}
    for e in pal_entries:
        wav = e["runtimePath"].split("vo/palette_pickups/", 1)[1]
        t = pack_by_wav.get(wav)
        if t is None:
            err(f"runtime palette entry with no pack take: {wav}")
            continue
        pal = t["paletteTake"]
        rt_path = ROOT / "ClientGodot" / e["runtimePath"]
        if not rt_path.exists():
            err(f"runtime palette file missing: {e['runtimePath']}")
            continue
        if sha256_of(rt_path) != pal["wavSha256"]:
            err(f"runtime palette sha mismatch: {wav}")
        if sha256_of(rt_path) != e["sha256"]:
            err(f"runtime manifest sha mismatch: {wav}")
        if rt_path.stat().st_size != e["sizeBytes"]:
            err(f"runtime palette size mismatch: {wav}")
        if abs(e["durationSeconds"] - pal["durationSeconds"]) > DUR_TOL_S:
            err(f"runtime palette duration mismatch: {wav}")
    COUNTS["runtime_palette_entries"] = len(pal_entries)

    note(f"palette validated: 11 roles / 11 distinct voices, "
         f"20 pickups re-measured from real bytes, "
         f"{files_checked} source files re-hashed, "
         f"runtime 757 files with 20 palette alternates")
    result = {
        "checkpoint": "MEDIA-02 WO37 M-F CP1",
        "validator": "check_vo_palette_mf_cp1_v1.py",
        "verdict": "PASS" if not ERRORS else "FAIL",
        "mismatches": len(ERRORS),
        "errors": ERRORS,
        "notes": NOTES,
        "counts": COUNTS,
    }
    print(f"counts: {json.dumps(COUNTS, indent=1)}")
    print(f"mismatches: {len(ERRORS)}")
    for e in ERRORS[:50]:
        print("  MISMATCH: " + e)
    print("verdict: " + result["verdict"])
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"report written: {args.out}")
    return 0 if not ERRORS else 1


def _manifest_for(key):
    if key.startswith("CIN000"):
        return "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json"
    if key.startswith("CIN006"):
        return "Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json"
    if key.startswith("CIN002"):
        return "Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json"
    return "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json"


if __name__ == "__main__":
    sys.exit(main())
