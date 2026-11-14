#!/usr/bin/env python3
"""MEDIA-02 WO37 M-F checkpoint 1: distinct fictional voice palette + pickups.

Resolves the draft-casting collisions recorded in the campaign VO drafts
(CP04/CP17) and in checkpoint 54: every male speaker shared one voice
(avocado_v2:MAI_03 Helio), Ly An shared her voice with the undecided
letter recipient (avocado_v2:MAI_01 Aria), and the prologue narrator also
used Helio. This checkpoint assigns ONE distinct fictional system voice
per role (11 roles / 11 voices; no real-voice cloning) and records a
palette pickup (alternate take) for every affected take: 15 dialogue
takes + 5 prologue narration segments = 20 pickups. Ly An keeps Aria;
her 7 takes are NOT re-recorded.

Raw MP3s are synthesized first with /opt/hatch/bin/tts (speed 100,
language vi), one call per take, e.g.:

  tts speak --voice avocado_v2:conor --language vi \\
      --output CIN002_S02_palette_tts_raw.mp3 --text-stdin

(Text is read character-exact from the four existing VO manifests by the
synthesis driver; this builder re-verifies every text against the timing
JSON dialogue + scene SRT, and fails on any mismatch. D1 forbids voice
speed-up to fit a window: a pickup that overruns its window is recorded
as data and does NOT fail the build; the three kept canonical overruns
(CIN_005_S03 / CIN_018_S03 / CIN_006_S03) are unchanged by this
checkpoint, and pickup fit is recorded separately from canonical fit.)

This tool converts each raw MP3 to WAV 48 kHz mono, measures duration
(ffprobe) and loudness/true peak (ffmpeg loudnorm) from real bytes,
checks window fit, checks every pickup differs in bytes from its
canonical take, and writes:

  Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/  (20 WAV + 20 raw MP3)
  Implementation/Content/Audio/Deliveries/VOICE_PALETTE_v1.json
  Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json
  Implementation/Content/Audio/Deliveries/PRONUNCIATION_REVIEW_PACK_v1.json
  Implementation/Reports/MuseMedia/vo_palette_review_playlist.txt (M3U)

The pickup takes are ALTERNATES with a recorded purpose. They do NOT
replace the canonical takes embedded in the 21 scene mixes, and they do
NOT change any mix, timing, SRT or the pronunciation table (which stays
tied to the embedded mixes; the review pack cross-references it).
Adoption into mixes is a Codex/director decision (M-B follow-up).
Status throughout: DRAFT_PALETTE / DRAFT_NOT_FINAL / NOT_AUDITIONED.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"
DELIVERIES = ROOT / "Implementation/Content/Audio/Deliveries"
NARRATIVE = ROOT / "Implementation/Content/Narrative/Deliveries"
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
VOICE_CATALOG = Path("/opt/muse/assets/voice-selector/voice_source.json")

CHECKPOINT = "MEDIA-02 WO37 M-F CP1"
BRANCH = "muse/media-production-20261104"

# role -> (voice id, display vi, previous voice, change, rationale)
PALETTE = {
    "NPC_LYAN": ("avocado_v2:MAI_01", "Ly An", "avocado_v2:MAI_01", "KEPT",
                 "Established in CP04/CP17; 7 takes already use Aria. No pickup."),
    "NPC_TA_VAN_KHANH": ("avocado_v2:conor", "Tạ Vân Khanh", "avocado_v2:MAI_03",
                         "NEW_DISTINCT",
                         "Named escort; was sharing Helio with all male speakers."),
    "NPC_HA_MAC": ("avocado_v2:vincent", "Hạ Mặc", "avocado_v2:MAI_03",
                   "NEW_DISTINCT",
                   "Cinematic-only staging (DEC Q4); was sharing Helio."),
    "NPC_SAM_CHU_QUY": ("avocado_v2:hubert", "Sầm Chủ Quỹ", "avocado_v2:MAI_03",
                        "NEW_DISTINCT",
                        "Cinematic-only staging (DEC Q4); was sharing Helio."),
    "NPC_REFUGEE_LEADER": ("avocado_v2:magnus", "Trưởng đoàn", "avocado_v2:MAI_03",
                           "NEW_DISTINCT", "One-line role; was sharing Helio."),
    "NPC_TONG_BANH": ("avocado_v2:ronan", "Tống Bành", "avocado_v2:MAI_03",
                      "NEW_DISTINCT", "One-line role; was sharing Helio."),
    "NPC_DIVER_LEAD": ("avocado_v2:briggs", "Đội trưởng thợ lặn", "avocado_v2:MAI_03",
                       "NEW_DISTINCT", "Two takes; was sharing Helio."),
    "NPC_CO_VO_TUONG": ("avocado_v2:atlas", "Cơ Vô Tướng", "avocado_v2:MAI_03",
                        "NEW_DISTINCT", "One-line role; was sharing Helio."),
    "PLAYER": ("avocado_v2:miles", "Người chơi", "avocado_v2:MAI_03",
               "NEW_DISTINCT",
               "Timing-only placeholder (VOICE_PLACEHOLDER_ONLY); distinct voice "
               "so the placeholder no longer sounds like a named character. "
               "Still NOT a casting or gender decision."),
    "LETTER_RECIPIENT": ("avocado_v2:ElvenWizard", "Người nhận thư",
                         "avocado_v2:MAI_01", "NEW_NEUTRAL_PLACEHOLDER",
                         "Recipient identity/gender UNDECIDED (owner direction, "
                         "CP54). Was sharing Aria with Ly An (draft-casting "
                         "collision). Neutral-gender catalog voice used as a "
                         "placeholder; NOT a casting or gender decision."),
    "NARRATOR": ("avocado_v2:History", "Người kể chuyện", "avocado_v2:MAI_03",
                 "NEW_DISTINCT",
                 "Prologue narrator; was sharing Helio with all male characters."),
}

# (takeKey, manifest relpath, match field, match value, role, canonical dir,
#  canonical wav, palette wav, palette raw mp3, kind)
TAKES = [
    ("CIN002_S02", "Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json",
     "key", "CIN002_S02", "NPC_TA_VAN_KHANH",
     "Art_Source/Audio/Muse/VO/P0_DRAFT", "VO_CIN002_S02_TAVANKHANH_draft_v1.wav",
     "VO_CIN002_S02_TAVANKHANH_palette_v1.wav", "CIN002_S02_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN006_S03", "Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json",
     "key", "CIN006_S03", "NPC_HA_MAC",
     "Art_Source/Audio/Muse/VO/CIN006_DRAFT", "VO_CIN_006_S03_HAMAC_draft_v1.wav",
     "VO_CIN_006_S03_HAMAC_palette_v1.wav", "CIN006_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN006_ALT_T01", "Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json",
     "key", "CIN006_ALT_T01", "NPC_HA_MAC",
     "Art_Source/Audio/Muse/VO/CIN006_DRAFT", "VO_CIN_006_ALT_T01_HAMAC_draft_v1-alt.wav",
     "VO_CIN_006_ALT_T01_HAMAC_palette_v1-alt.wav", "CIN006_ALT_T01_palette_tts_raw.mp3",
     "alternate"),
    ("CIN008_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_008_S03_TAVANKHANH_draft_v1.wav", "NPC_TA_VAN_KHANH",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_008_S03_TAVANKHANH_draft_v1.wav",
     "VO_CIN_008_S03_TAVANKHANH_palette_v1.wav", "CIN008_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN010_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_010_S03_SAMCHUQUY_draft_v1.wav", "NPC_SAM_CHU_QUY",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_010_S03_SAMCHUQUY_draft_v1.wav",
     "VO_CIN_010_S03_SAMCHUQUY_palette_v1.wav", "CIN010_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN011_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_011_S03_HAMAC_draft_v1.wav", "NPC_HA_MAC",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_011_S03_HAMAC_draft_v1.wav",
     "VO_CIN_011_S03_HAMAC_palette_v1.wav", "CIN011_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN012_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_012_S03_HAMAC_draft_v1.wav", "NPC_HA_MAC",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_012_S03_HAMAC_draft_v1.wav",
     "VO_CIN_012_S03_HAMAC_palette_v1.wav", "CIN012_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN013_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_013_S03_REFUGEELEADER_draft_v1.wav", "NPC_REFUGEE_LEADER",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_013_S03_REFUGEELEADER_draft_v1.wav",
     "VO_CIN_013_S03_REFUGEELEADER_palette_v1.wav", "CIN013_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN014_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_014_S03_TONGBANH_draft_v1.wav", "NPC_TONG_BANH",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_014_S03_TONGBANH_draft_v1.wav",
     "VO_CIN_014_S03_TONGBANH_palette_v1.wav", "CIN014_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN015_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_015_S03_DIVERLEAD_draft_v1.wav", "NPC_DIVER_LEAD",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_015_S03_DIVERLEAD_draft_v1.wav",
     "VO_CIN_015_S03_DIVERLEAD_palette_v1.wav", "CIN015_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN016_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_016_S03_HAMAC_draft_v1.wav", "NPC_HA_MAC",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_016_S03_HAMAC_draft_v1.wav",
     "VO_CIN_016_S03_HAMAC_palette_v1.wav", "CIN016_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN017_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_017_S03_DIVERLEAD_draft_v1.wav", "NPC_DIVER_LEAD",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_017_S03_DIVERLEAD_draft_v1.wav",
     "VO_CIN_017_S03_DIVERLEAD_palette_v1.wav", "CIN017_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN018_S02", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_018_S02_COVOTUONG_draft_v1.wav", "NPC_CO_VO_TUONG",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_018_S02_COVOTUONG_draft_v1.wav",
     "VO_CIN_018_S02_COVOTUONG_palette_v1.wav", "CIN018_S02_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN018_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_018_S03_PLAYER_draft_v1.wav", "PLAYER",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_018_S03_PLAYER_draft_v1.wav",
     "VO_CIN_018_S03_PLAYER_palette_v1.wav", "CIN018_S03_palette_tts_raw.mp3",
     "dialogue"),
    ("CIN020_S03", "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json",
     "wav", "VO_CIN_020_S03_LETTERRECIPIENT_draft_v1.wav", "LETTER_RECIPIENT",
     "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT", "VO_CIN_020_S03_LETTERRECIPIENT_draft_v1.wav",
     "VO_CIN_020_S03_LETTERRECIPIENT_palette_v1.wav", "CIN020_S03_palette_tts_raw.mp3",
     "dialogue"),
]
for _n in range(1, 6):
    TAKES.append((
        f"CIN000_SEG0{_n}",
        "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json",
        "takeId", f"VO_CIN000_SEG0{_n}", "NARRATOR",
        "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT",
        f"VO_CIN000_SEG0{_n}_NARRATOR.wav",
        f"VO_CIN000_SEG0{_n}_NARRATOR_palette_v1.wav",
        f"CIN000_SEG0{_n}_palette_tts_raw.mp3", "narration"))


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        fail(f"command failed: {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    return r


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error",
             "-show_entries", "stream=codec_name,sample_rate,channels",
             "-show_entries", "format=duration,size",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def loudnorm(path: Path) -> dict:
    r = run(["ffmpeg", "-i", str(path), "-vn", "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    tail = r.stderr.strip().splitlines()
    start = next(i for i, line in enumerate(tail) if line.strip() == "{")
    end = next(i for i, line in enumerate(tail) if line.strip() == "}")
    return json.loads("\n".join(tail[start:end + 1]))


def timing_dialogue(scene_id: str, shot_id: str):
    timing = json.loads(
        (NARRATIVE / scene_id / f"{scene_id}_timing_v1.json").read_text(encoding="utf-8"))
    srt = (NARRATIVE / scene_id / f"{scene_id}_vi.srt").read_text(encoding="utf-8")
    srt_nfc = unicodedata.normalize("NFC", srt)
    for shot in timing["shots"]:
        if shot["shotId"] == shot_id:
            dlg = shot.get("dialogue")
            if not dlg:
                return None
            return {"text": dlg["text"], "windowSeconds": dlg["windowSeconds"],
                    "status": dlg.get("status"), "inSrt": (
                        unicodedata.normalize("NFC", dlg["text"]) in srt_nfc)}
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    global ROOT, OUT_DIR, DELIVERIES, NARRATIVE, REPORTS
    ROOT = Path(args.root).resolve()
    OUT_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"
    DELIVERIES = ROOT / "Implementation/Content/Audio/Deliveries"
    NARRATIVE = ROOT / "Implementation/Content/Narrative/Deliveries"
    REPORTS = ROOT / "Implementation/Reports/MuseMedia"

    catalog = {v["id"]: v for v in json.loads(VOICE_CATALOG.read_text(encoding="utf-8"))}
    voices = [p[0] for p in PALETTE.values()]
    if len(set(voices)) != len(voices):
        fail("palette voices are not unique per role")
    for vid in voices:
        if vid not in catalog:
            fail(f"palette voice not in catalog: {vid}")

    synth_log = json.loads(
        (OUT_DIR / "PALETTE_PICKUPS_synthesis_log_v1.json").read_text(encoding="utf-8"))
    synth_by_mp3 = {t["mp3"]: t for t in synth_log["takes"]}
    if len(synth_log["takes"]) != 20:
        fail(f"synthesis log has {len(synth_log['takes'])} takes, expected 20")

    results = []
    overruns = []
    for (key, manifest_rel, field, value, role, canon_dir_rel, canon_wav,
         palette_wav, palette_mp3, kind) in TAKES:
        voice, display, prev_voice, change, _rationale = PALETTE[role]
        manifest = json.loads((ROOT / manifest_rel).read_text(encoding="utf-8"))
        entries = manifest.get("takes") or manifest.get("segments")
        hit = [e for e in entries if e.get(field) == value]
        if len(hit) != 1:
            fail(f"{key}: manifest match {field}={value} -> {len(hit)}")
        canon_take = hit[0]
        text = canon_take["text"]

        # Text cross-check against timing JSON + SRT for windowed dialogue.
        window = None
        window_status = None
        if kind == "dialogue":
            scene_id = f"CIN_{key[3:6]}" if key.startswith("CIN0") else None
            shot_id = f"CIN_{key[3:6]}_S{key[8:10]}" if key.startswith("CIN0") else None
            dlg = timing_dialogue(scene_id, shot_id)
            if dlg is None:
                fail(f"{key}: no dialogue entry in {scene_id} timing")
            if unicodedata.normalize("NFC", dlg["text"]) != unicodedata.normalize("NFC", text):
                fail(f"{key}: manifest text != timing dialogue text")
            if not dlg["inSrt"]:
                fail(f"{key}: dialogue text not in scene SRT")
            window = dlg["windowSeconds"]
            window_status = dlg["status"]
        elif kind == "alternate":
            # Q3: alternate take has its own takeId/version, no dialogue window.
            if canon_take.get("takeId") != "CIN_006_ALT_T01":
                fail(f"{key}: alternate takeId mismatch")
            window = None
            window_status = "NO_WINDOW_BY_DESIGN_Q3"
        else:  # narration: manifest script is the owner-approved source.
            window = None
            window_status = "NO_WINDOW_NARRATION_SEGMENT"

        # Canonical take: measure fresh from real bytes.
        canon_path = ROOT / canon_dir_rel / canon_wav
        if not canon_path.exists():
            fail(f"{key}: canonical wav missing: {canon_path}")
        canon_probe = probe(canon_path)
        canon_ln = loudnorm(canon_path)
        canon_duration = float(canon_probe["format"]["duration"])
        canon_sha = sha256(canon_path)

        # Palette take: raw MP3 must match the synthesis log + returned voice.
        raw = OUT_DIR / palette_mp3
        if not raw.exists():
            fail(f"{key}: raw palette mp3 missing: {raw}")
        slog = synth_by_mp3.get(palette_mp3)
        if slog is None:
            fail(f"{key}: no synthesis log entry for {palette_mp3}")
        if slog["voice"] != voice or slog["ttsReturnedVoice"] != voice:
            fail(f"{key}: synthesis log voice {slog['voice']} != palette {voice}")
        if sha256(raw) != slog["sha256"]:
            fail(f"{key}: raw mp3 sha mismatch vs synthesis log")
        if sha256(raw) == canon_sha:
            fail(f"{key}: palette raw mp3 identical to canonical wav (impossible)")

        # Convert to WAV 48 kHz mono (same recipe as CP04/CP17).
        wav_path = OUT_DIR / palette_wav
        run(["ffmpeg", "-y", "-v", "error", "-i", str(raw),
             "-ar", "48000", "-ac", "1", str(wav_path)])
        wav_probe = probe(wav_path)
        stream = wav_probe["streams"][0]
        if (stream["codec_name"] != "pcm_s16le" or int(stream["sample_rate"]) != 48000
                or int(stream["channels"]) != 1):
            fail(f"{key}: wav format wrong: {stream}")
        wav_ln = loudnorm(wav_path)
        duration = float(wav_probe["format"]["duration"])
        wav_sha = sha256(wav_path)
        if wav_sha == canon_sha:
            fail(f"{key}: palette wav byte-identical to canonical take")

        fit = None
        slack_s = None
        if window is not None:
            win_len = float(window[1]) - float(window[0])
            slack_s = round(win_len - duration, 3)
            fit = "FITS" if duration <= win_len + 1e-9 else "OVERRUN"
            if fit == "OVERRUN":
                overruns.append((key, slack_s))
        results.append({
            "takeKey": key,
            "takeId": palette_wav.replace(".wav", ""),
            "kind": kind,
            "role": role,
            "speakerDisplay": display,
            "voice": voice,
            "voiceLabel": f"{catalog[voice]['name']} (fictional system voice)",
            "voiceGender": catalog[voice].get("gender"),
            "previousVoice": prev_voice,
            "paletteChange": change,
            "text": text,
            "windowSceneSeconds": window,
            "windowStatus": window_status,
            "fit": fit,
            "slackSeconds": slack_s,
            "canonicalTake": {
                "file": canon_wav,
                "dir": canon_dir_rel,
                "sha256": canon_sha,
                "durationSeconds": round(canon_duration, 4),
                "integratedLufs": float(canon_ln["input_i"]),
                "truePeakDbtp": float(canon_ln["input_tp"]),
            },
            "paletteTake": {
                "wav": palette_wav,
                "wavSha256": wav_sha,
                "wavBytes": wav_path.stat().st_size,
                "rawMp3": palette_mp3,
                "rawMp3Sha256": slog["sha256"],
                "rawMp3Bytes": slog["bytes"],
                "ttsReturnedVoice": slog["ttsReturnedVoice"],
                "durationSeconds": round(duration, 4),
                "integratedLufs": float(wav_ln["input_i"]),
                "truePeakDbtp": float(wav_ln["input_tp"]),
                "lra": float(wav_ln["input_lra"]),
            },
            "purpose": ("Palette alternate: distinct fictional voice for this role. "
                        "Does NOT replace the canonical take embedded in the scene "
                        "mix; adoption is a Codex/director decision (M-B follow-up)."),
        })
        print(f"OK {key} {role} {voice} {duration:.3f}s "
              f"{float(wav_ln['input_i']):.2f} LUFS fit={fit} slack={slack_s}")

    if len(results) != 20:
        fail(f"take count {len(results)} != 20")

    # ---- VOICE_PALETTE_v1.json ----
    palette_doc = {
        "manifestId": "NGM_VOICE_PALETTE_V1",
        "checkpoint": CHECKPOINT,
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrderRef": "WO37 M-F",
        "branch": BRANCH,
        "status": "DRAFT_PALETTE",
        "auditionStatus": "NOT_AUDITIONED",
        "scope": ("One distinct fictional system voice per speaking role. "
                  "No real-voice cloning. DRAFT TTS is not final casting or "
                  "acting. Ly An keeps her established voice; every other "
                  "role gets a distinct voice; the undecided letter "
                  "recipient gets the catalog's only neutral-gender voice as "
                  "a placeholder, NOT a casting or gender decision."),
        "collisionsResolved": [
            "All male speakers shared avocado_v2:MAI_03 (Helio) in CP04/CP17.",
            "Letter recipient shared avocado_v2:MAI_01 (Aria) with Ly An (CP54).",
            "Prologue narrator shared avocado_v2:MAI_03 (Helio) with all male characters.",
        ],
        "roles": [],
    }
    for role, (voice, display, prev_voice, change, rationale) in PALETTE.items():
        palette_doc["roles"].append({
            "role": role,
            "speakerDisplay": display,
            "voice": voice,
            "voiceLabel": f"{catalog[voice]['name']} (fictional system voice)",
            "voiceGender": catalog[voice].get("gender"),
            "previousVoice": prev_voice,
            "paletteChange": change,
            "rationale": rationale,
            "status": "DRAFT_PALETTE",
        })
    palette_doc["counts"] = {
        "roles": len(PALETTE),
        "distinctVoices": len(set(voices)),
        "keptVoices": 1,
        "newVoices": 10,
        "pickupTakes": 20,
    }
    (DELIVERIES / "VOICE_PALETTE_v1.json").write_text(
        json.dumps(palette_doc, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- VO_PALETTE_PICKUPS_pack_v1.json ----
    pack_doc = {
        "manifestId": "NGM_VO_PALETTE_PICKUPS_V1",
        "checkpoint": CHECKPOINT,
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrderRef": "WO37 M-F",
        "branch": BRANCH,
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "sourceDir": "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1",
        "counts": {
            "takes": len(results),
            "dialogue": sum(1 for r in results if r["kind"] == "dialogue"),
            "alternate": sum(1 for r in results if r["kind"] == "alternate"),
            "narration": sum(1 for r in results if r["kind"] == "narration"),
            "fits": sum(1 for r in results if r["fit"] == "FITS"),
            "overruns": len(overruns),
        },
        "overruns": [{"takeKey": k, "slackSeconds": s} for k, s in overruns],
        "keptCanonicalOverrunsUnchanged": [
            "CIN_005_S03 +0.160 s", "CIN_018_S03 +0.280 s", "CIN_006_S03 +0.520 s",
        ],
        "notes": [
            "Pickup fit is recorded separately from canonical fit; a pickup "
            "overrun does not change the kept canonical overrun decision.",
            "Ly An's 7 takes were not re-recorded (voice kept).",
            "CIN_018_S03 pickup stays VOICE_PLACEHOLDER_ONLY.",
            "All measurements are from real bytes (ffprobe/ffmpeg loudnorm).",
        ],
        "takes": results,
    }
    (DELIVERIES / "VO_PALETTE_PICKUPS_pack_v1.json").write_text(
        json.dumps(pack_doc, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- PRONUNCIATION_REVIEW_PACK_v1.json ----
    pron_table = json.loads(
        (DELIVERIES / "PRONUNCIATION_TABLE_v1.json").read_text(encoding="utf-8"))
    table_by_name = {n["name"]: n for n in pron_table["names"]}
    review = build_pronunciation_review(results, table_by_name)
    (DELIVERIES / "PRONUNCIATION_REVIEW_PACK_v1.json").write_text(
        json.dumps(review, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---- Review playlist (M3U content in .txt, per CP9 convention) ----
    playlist_lines = ["#EXTM3U", "#PLAYLIST:VO palette + pronunciation review (M-F CP1)"]
    for item in review["playlist"]:
        playlist_lines.append(f"#EXTINF:{item['durationSeconds']:.3f},{item['label']}")
        playlist_lines.append(item["path"])
    (REPORTS / "vo_palette_review_playlist.txt").write_text(
        "\n".join(playlist_lines) + "\n", encoding="utf-8")

    print(f"BUILD DONE: {len(results)} takes, {len(overruns)} pickup overruns, "
          f"playlist {len(review['playlist'])} entries")


def est_timecode(text: str, name: str, duration: float):
    """Estimated in-take span of a name by character ratio. Labelled
    ESTIMATED in the review pack: navigation aid for the listener, not a
    measured alignment."""
    idx = text.find(name)
    if idx < 0:
        return None
    start = round(idx / len(text) * duration, 3)
    end = round((idx + len(name)) / len(text) * duration, 3)
    return [start, end]


def build_pronunciation_review(results, table_by_name):
    by_key = {r["takeKey"]: r for r in results}
    questions = {
        "Lạc Châu": [
            "Nghe 'Lạc' có đủ thanh nặng và âm cuối -c bật rõ không, hay bị nuốt thành 'Lạ'?",
            "So sánh take cũ (Helio) và take palette (History): giọng mới có giữ rõ hai âm tiết Lạc–Châu ở cả hai lần xuất hiện (SEG01 và SEG04) không?",
        ],
        "Huyền Ấn": [
            "Nghe 'Huyền' có đủ thanh huyền, 'Ấn' có đủ thanh nặng và âm cuối -n không?",
            "Cụm 'Huyền Ấn' trong câu dài SEG01 có bị nuốt âm nào khi giọng History đọc liền mạch không?",
        ],
        "Bến Mưa": [
            "Nghe 'Bến' có đủ thanh nặng, 'Mưa' có đủ thanh ngang và nguyên âm ươ không?",
            "Câu kết SEG05 đọc chậm — tên Bến Mưa có nổi rõ như một địa danh, hay chìm vào nhịp câu?",
        ],
        "Sa Hỏa": [
            "Nghe 'Sa' có đọc thành 'Xa' không; 'Hỏa' có đủ thanh hỏi và âm cuối -a không?",
            "So sánh take cũ (Helio, VOICE_PLACEHOLDER_ONLY) và take palette (miles): giọng mới có giữ rõ hai âm tiết không, và có còn nghe như một nhân vật đã đặt tên không (không được — vẫn là placeholder)?",
        ],
    }
    # Spoken-name occurrences: (name, takeKey, source note)
    occurrences = [
        ("Lạc Châu", "CIN000_SEG01", "Prologue SRT cue 1 (SEG01)"),
        ("Huyền Ấn", "CIN000_SEG01", "Prologue SRT cue 1 (SEG01)"),
        ("Lạc Châu", "CIN000_SEG04", "Prologue SRT cue 4 (SEG04)"),
        ("Bến Mưa", "CIN000_SEG05", "Prologue SRT cue 5 (SEG05)"),
        ("Sa Hỏa", "CIN018_S03", "Dialogue take CIN_018_S03"),
    ]
    spoken_rows = []
    playlist = []
    for name, take_key, source_note in occurrences:
        r = by_key[take_key]
        table_name = table_by_name[name]
        canon = r["canonicalTake"]
        pal = r["paletteTake"]
        tc_canon = est_timecode(r["text"], name, canon["durationSeconds"])
        tc_pal = est_timecode(r["text"], name, pal["durationSeconds"])
        spoken_rows.append({
            "name": name,
            "ipaApprox": table_name.get("ipaApprox"),
            "syllables": table_name.get("syllables"),
            "status": table_name.get("status"),
            "source": source_note,
            "takeKey": take_key,
            "line": r["text"],
            "aTake": {
                "label": "canonical take (embedded in mix/prologue film)",
                "file": canon["file"],
                "voice": r["previousVoice"],
                "durationSeconds": canon["durationSeconds"],
                "integratedLufs": canon["integratedLufs"],
                "estimatedNameTimecodeSeconds": tc_canon,
            },
            "bTake": {
                "label": "palette pickup (M-F CP1 alternate)",
                "file": pal["wav"],
                "voice": r["voice"],
                "durationSeconds": pal["durationSeconds"],
                "integratedLufs": pal["integratedLufs"],
                "estimatedNameTimecodeSeconds": tc_pal,
            },
            "listeningQuestions": questions[name],
        })
        playlist.append({
            "label": f"A {name} — canonical {take_key}",
            "path": f"Art_Source/Audio/Muse/VO/{canon['dir'].split('/')[-1]}/{canon['file']}",
            "durationSeconds": canon["durationSeconds"],
        })
        playlist.append({
            "label": f"B {name} — palette {take_key}",
            "path": f"Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/{pal['wav']}",
            "durationSeconds": pal["durationSeconds"],
        })
    unspoken = []
    for name, rec in table_by_name.items():
        if rec.get("spokenInAudio"):
            continue
        unspoken.append({
            "name": name,
            "status": rec.get("status"),
            "note": ("DECIDED spelling; never spoken in delivered audio — no "
                     "pickup recorded." if name == "Tạ Vân Khanh" else
                     "Not spoken in delivered audio — no pickup recorded "
                     "(WO37 M-F: no useless reads to inflate count)."),
        })
    return {
        "manifestId": "NGM_PRONUNCIATION_REVIEW_PACK_V1",
        "checkpoint": CHECKPOINT,
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrderRef": "WO37 M-F",
        "branch": BRANCH,
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "crossReference": ("PRONUNCIATION_TABLE_v1.json (CP44): 16 names, 4 spoken, "
                           "only Tạ Vân Khanh DECIDED. This pack does NOT modify "
                           "that table (it stays tied to the embedded mixes); it "
                           "adds A-B listening rows for the palette pickups."),
        "timecodeMethod": ("Estimated in-take timecodes by character ratio "
                           "(name offset / line length x take duration). "
                           "ESTIMATED — navigation aid for the listener, NOT a "
                           "measured forced alignment."),
        "spokenNames": spoken_rows,
        "unspokenNames": unspoken,
        "counts": {
            "spokenNames": len(spoken_rows),
            "distinctSpokenNames": len({r["name"] for r in spoken_rows}),
            "unspokenNames": len(unspoken),
            "abPairs": len(spoken_rows),
        },
        "playlist": playlist,
    }


if __name__ == "__main__":
    main()
