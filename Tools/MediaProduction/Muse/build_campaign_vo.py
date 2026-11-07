#!/usr/bin/env python3
"""MEDIA-02 checkpoint 17: build the campaign VO drafts (17 lines) from TTS MP3s.

Cues are parsed from the campaign timing JSONs (source of truth), cross-checked
character-exact against each scene SRT, and placed at their absolute campaign
offsets (scene order CIN_001..CIN_020; CIN_001 is 36 s, every other scene 18 s,
full campaign 378 s). Voice map (fictional system voices only, no real-voice
cloning, no unlicensed samples):

  NPC_LYAN            -> avocado_v2:MAI_01 (Aria, as in checkpoint 04)
  NPC_TA_VAN_KHANH    -> avocado_v2:MAI_03 (Helio, as in checkpoint 04)
  every other male speaker (HA_MAC, SAM_CHU_QUY, REFUGEE_LEADER, TONGBANH,
  DIVER_LEAD, CO_VO_TUONG) -> avocado_v2:MAI_03 (Helio). Limitation: the
  male characters are NOT voice-distinct in this draft; distinct casting is
  a director decision, not something this draft invents.
  PLAYER (CIN_018_S03) -> avocado_v2:MAI_03, flagged VOICE_PLACEHOLDER_ONLY:
  VOICE_GUIDE assigns the player no spoken voice or gender; this take exists
  only so the director can hear the timing. It must be replaced or dropped
  by the director; it implies no casting or gender decision.
  CIN_020 (speaker null, "Nguoi nhan thu") -> avocado_v2:MAI_01 under the
  role VOICE_LETTER_RECIPIENT (see MEMORY / checkpoint 16 next block). The
  recipient identity/gender is undecided; this is a placeholder role voice.

Regenerate the raw MP3s first (speed stays 100: D1 forbids voice speed-up
to fit a window) with /opt/hatch/bin/tts, one call per take, e.g.:

  tts speak --voice avocado_v2:MAI_01 --language vi \\
      --output CIN003_S03.mp3 --text-stdin   # "Co the ho da dung o hai cho..."
  tts speak --voice avocado_v2:MAI_03 --language vi \\
      --output CIN018_S03.mp3 --text-stdin   # "O Sa Hoa ong da cho nuoc..."

(Vietnamese text is passed verbatim via stdin; the comments above are ASCII
placeholders only, never synthesis input.)

This tool then converts each MP3 to WAV 48 kHz mono, measures duration with
ffprobe and loudness/true peak with ffmpeg loudnorm, and records whether each
take fits its dialogue window. An OVERRUN is recorded as data (exact slack in
the manifest and a printed summary) and does NOT fail the build: D1 forbids
speeding the voice up to fit, so a take that is too long at natural speed is
a director finding (widen the window or trim the line), not a build error to
hide. The tool DOES fail on missing/unreadable input, on a text/SRT mismatch,
or on a timeline duration mismatch. It assembles a 378 s VO-only timeline WAV
placing each take at its absolute window start; overrun takes are placed
unchanged (they bleed audibly past their window, which is exactly what the
director needs to hear). The timeline is a DRAFT assembly, not a mix: no
music/ambience stems are mixed in, and no loudness normalization is applied.
Outputs land in Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

CAMPAIGN_SCENES = [f"CIN_{n:03d}" for n in range(3, 21) if n != 4 and n != 6]
# CIN_003, CIN_005, CIN_007..CIN_020 (16 scenes, 17 cues; CIN_018 has 2).
VOICE_MAP = {
    "NPC_LYAN": ("avocado_v2:MAI_01", "Aria (fictional system voice)"),
    "NPC_TA_VAN_KHANH": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_HA_MAC": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_SAM_CHU_QUY": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_REFUGEE_LEADER": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_TONG_BANH": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_DIVER_LEAD": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "NPC_CO_VO_TUONG": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    "PLAYER": ("avocado_v2:MAI_03", "Helio (fictional system voice)"),
    None: ("avocado_v2:MAI_01", "Aria (fictional system voice)"),
}
SPEAKER_SHORT = {
    "NPC_LYAN": "LYAN",
    "NPC_TA_VAN_KHANH": "TAVANKHANH",
    "NPC_HA_MAC": "HAMAC",
    "NPC_SAM_CHU_QUY": "SAMCHUQUY",
    "NPC_REFUGEE_LEADER": "REFUGEELEADER",
    "NPC_TONG_BANH": "TONGBANH",
    "NPC_DIVER_LEAD": "DIVERLEAD",
    "NPC_CO_VO_TUONG": "COVOTUONG",
    "PLAYER": "PLAYER",
    None: "LETTERRECIPIENT",
}
ROLE_NOTE = {
    "PLAYER": ("VOICE_PLACEHOLDER_ONLY: VOICE_GUIDE assigns the player no "
               "spoken voice or gender; timing-only placeholder, director "
               "must replace or drop it."),
    None: ("VOICE_LETTER_RECIPIENT: placeholder role voice; recipient "
           "identity/gender undecided."),
}
CAMPAIGN_SECONDS = 378.0


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stdout, r.stderr, file=sys.stderr)
        sys.exit(1)
    return r


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


def load_cues(root: Path):
    """Parse the 17 campaign cues from timing JSONs + scene offsets."""
    deliveries = root / "Implementation" / "Content" / "Narrative" / "Deliveries"
    # Scene offsets from every scene's duration, in campaign order.
    offsets = {}
    cursor = 0.0
    for n in range(1, 21):
        sid = f"CIN_{n:03d}"
        timing = json.loads(
            (deliveries / sid / f"{sid}_timing_v1.json").read_text(encoding="utf-8"))
        offsets[sid] = cursor
        cursor += float(timing["durationSeconds"])
    if abs(cursor - CAMPAIGN_SECONDS) > 1e-9:
        print(f"SCENE DURATIONS SUM {cursor} != {CAMPAIGN_SECONDS}", file=sys.stderr)
        sys.exit(1)
    takes = []
    for sid in CAMPAIGN_SCENES:
        timing = json.loads(
            (deliveries / sid / f"{sid}_timing_v1.json").read_text(encoding="utf-8"))
        srt = (deliveries / sid / f"{sid}_vi.srt").read_text(encoding="utf-8")
        srt_nfc = unicodedata.normalize("NFC", srt)
        for shot in timing["shots"]:
            dlg = shot.get("dialogue")
            if not dlg:
                continue
            text = unicodedata.normalize("NFC", dlg["text"])
            if text not in srt_nfc:
                print(f"SRT MISMATCH: {shot['shotId']} text not in SRT",
                      file=sys.stderr)
                sys.exit(1)
            speaker = dlg.get("speaker")
            voice, voice_label = VOICE_MAP[speaker]
            key = shot["shotId"].replace("CIN_", "CIN")  # CIN003_S03
            takes.append({
                "key": key,
                "shotId": shot["shotId"],
                "sceneId": sid,
                "speaker": speaker,
                "speakerDisplay": dlg.get("speakerDisplay"),
                "onscreen": dlg.get("onscreen"),
                "voice": voice,
                "voiceLabel": voice_label,
                "roleNote": ROLE_NOTE.get(speaker),
                "mp3": f"{key}.mp3",
                "wav": (f"VO_{shot['shotId']}_{SPEAKER_SHORT[speaker]}"
                        f"_draft_v1.wav"),
                "text": dlg["text"],
                "windowSceneSeconds": dlg["windowSeconds"],
                "sceneOffsetSeconds": offsets[sid],
                "status": dlg.get("status"),
            })
    if len(takes) != 17:
        print(f"CUE COUNT {len(takes)} != 17", file=sys.stderr)
        sys.exit(1)
    return takes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--mp3-dir", required=True)
    ap.add_argument("--out-dir",
                    default="Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT")
    args = ap.parse_args()
    root = Path(args.root)
    mp3_dir = Path(args.mp3_dir)
    out = root / args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    takes = load_cues(root)
    results = []
    overruns = []
    for take in takes:
        src = mp3_dir / take["mp3"]
        if not src.exists():
            print(f"MISSING MP3: {src}", file=sys.stderr)
            sys.exit(1)
        raw = out / take["mp3"].replace(".mp3", "_tts_raw.mp3")
        raw.write_bytes(src.read_bytes())
        wav = out / take["wav"]
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
             "-ar", "48000", "-ac", "1", str(wav)])
        p = probe(wav)
        duration = float(p["format"]["duration"])
        window = take["windowSceneSeconds"][1] - take["windowSceneSeconds"][0]
        slack = window - duration
        ln = loudnorm(wav)
        fit = "FITS" if slack >= 0 else "OVERRUN"
        print(f"{take['shotId']}: {duration:.4f}s in {window:.1f}s window "
              f"(slack {slack:+.4f}s) {fit} "
              f"LUFS {ln['input_i']} TP {ln['input_tp']}")
        if slack < 0:
            overruns.append(take["shotId"])
        results.append({
            **take,
            "wav": take["wav"],
            "wavSha256": sha256(wav),
            "rawMp3": raw.name,
            "rawMp3Sha256": sha256(raw),
            "durationSeconds": round(duration, 4),
            "windowSeconds": window,
            "slackSeconds": round(slack, 4),
            "fit": fit,
            "timelineStartSeconds": round(
                take["sceneOffsetSeconds"] + take["windowSceneSeconds"][0], 1),
            "loudness": {
                "integratedLUFS": ln["input_i"],
                "truePeakDBTP": ln["input_tp"],
                "loudnessRangeLU": ln["input_lra"],
                "thresholdLUFS": ln["input_thresh"],
            },
            "format": {
                "codec": p["streams"][0]["codec_name"],
                "sampleRateHz": int(p["streams"][0]["sample_rate"]),
                "channels": int(p["streams"][0]["channels"]),
                "bytes": int(p["format"]["size"]),
            },
        })

    # 378 s VO-only timeline: each take delayed to its absolute window start.
    timeline = out / "CAMPAIGN_VO_timeline_draft_v1.wav"
    inputs, filters = [], []
    for i, take in enumerate(results):
        inputs += ["-i", str(out / take["wav"])]
        ms = int(round(take["timelineStartSeconds"] * 1000))
        filters.append(f"[{i}:a]adelay={ms}:all=1[a{i}]")
    filters.append("".join(f"[a{i}]" for i in range(len(results))) +
                   f"amix=inputs={len(results)}:normalize=0,"
                   f"apad=whole_dur={int(CAMPAIGN_SECONDS)},"
                   f"atrim=0:{int(CAMPAIGN_SECONDS)}[aout]")
    run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex",
         ";".join(filters), "-map", "[aout]", "-ar", "48000", "-ac", "1",
         str(timeline)])
    tp = probe(timeline)
    tl_duration = float(tp["format"]["duration"])
    print(f"timeline: {tl_duration:.4f}s")
    if abs(tl_duration - CAMPAIGN_SECONDS) > 0.05:
        print("TIMELINE DURATION MISMATCH", file=sys.stderr)
        sys.exit(1)

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 17 - campaign VO drafts (17 lines)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "d1Approval": ("D1 APPROVED draft VO production only for the 21 "
                       "dialogue windows; no canon changes, no voice "
                       "speed-up to fit."),
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL_VO",
        "campaignSeconds": CAMPAIGN_SECONDS,
        "fits": sum(1 for r in results if r["fit"] == "FITS"),
        "overruns": overruns,
        "notes": [
            "Fictional system voices only; no real-voice cloning, "
            "no unlicensed samples.",
            "All 17 windows are PROPOSED_ANIMATIC_PLACEMENT (checkpoint 06); "
            "none is DECIDED except by D1 for draft VO production.",
            "All takes synthesized at speed 100 (D1: no voice speed-up to "
            "fit). An OVERRUN take is delivered unchanged and flagged; the "
            "director decides whether to widen its window or trim its line.",
            "Male characters share one production voice (Helio) in this "
            "draft; they are NOT voice-distinct. Distinct casting is a "
            "director decision.",
            "PLAYER take is a timing-only placeholder (VOICE_GUIDE assigns "
            "the player no spoken voice); CIN_020 uses placeholder role "
            "voice VOICE_LETTER_RECIPIENT.",
            "Per-take loudness only, NOT a mix PASS; stems stay separate.",
            "Timeline is VO-only draft assembly; no music/ambience mixed in.",
        ],
        "takes": results,
        "timeline": {
            "file": timeline.name,
            "sha256": sha256(timeline),
            "durationSeconds": round(tl_duration, 4),
            "format": {"codec": tp["streams"][0]["codec_name"],
                       "sampleRateHz": int(tp["streams"][0]["sample_rate"]),
                       "channels": int(tp["streams"][0]["channels"])},
        },
    }
    (out / "CAMPAIGN_VO_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"OK: manifest written ({manifest['fits']}/17 FITS, "
          f"overruns: {overruns or 'none'})")


if __name__ == "__main__":
    main()
