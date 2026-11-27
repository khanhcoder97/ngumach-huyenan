#!/usr/bin/env python3
"""MEDIA-02 checkpoint 19: build the CIN_006 VO drafts (canonical + alt take).

Closes the last of the 21 D1-approved dialogue windows: checkpoints 04 and 17
delivered 20 of the 21 draft VO takes (3 P0 + 17 campaign); CIN_006_S03 was
the only one left. Two takes are built here, kept strictly separate per
DEC-MEDIA-P0-20261105 Q3:

  - Canonical cue CIN_006_S03 (NPC_HA_MAC, on-screen, window 12.5-17.5 s,
    status PROPOSED_ANIMATIC_PLACEMENT in the timing JSON; D1 approved the
    window for DRAFT VO production only). Its text is parsed from the
    timing JSON and cross-checked character-exact against the scene SRT.
  - Alternate take CIN_006_ALT_T01 (version v1-alt): its own takeId/version,
    NO window assigned, NOT in the SRT (asserted), never merged with the
    canonical line and never placed on the timeline. The source direction
    (MUSE_THANG_LONG_CIN006_DIRECTION_vi.md) assigns the S03 beat to
    Ha Mac and does not cast the alternate reading separately, so the
    draft reads it with the same fictional voice; that is recorded as a
    draft assumption, not a casting decision.

Voice (fictional system voice only, no real-voice cloning, no unlicensed
samples), consistent with the checkpoint 17 campaign casting:

  NPC_HA_MAC -> avocado_v2:MAI_03 (Helio). Limitation, same as checkpoint
  17: the male characters are NOT voice-distinct in these drafts; distinct
  casting is a director decision.

Regenerate the raw MP3s first (speed stays 100: D1 forbids voice speed-up
to fit a window) with /opt/hatch/bin/tts, one call per take, feeding the
exact timing-JSON text via stdin:

  tts speak --voice avocado_v2:MAI_03 --language vi \
      --output CIN006_S03.mp3 --text-stdin
  tts speak --voice avocado_v2:MAI_03 --language vi \
      --output CIN006_ALT_T01.mp3 --text-stdin

This tool converts each MP3 to WAV 48 kHz mono, measures duration with
ffprobe and loudness/true peak with ffmpeg loudnorm, and records whether
the canonical take fits its window. An OVERRUN is recorded as data (exact
slack in the manifest) and does NOT fail the build: it is a director
finding (widen the window or trim the line), not a build error to hide.
The tool DOES fail on missing/unreadable input, on a canonical text/SRT
mismatch, on the alt text leaking into the SRT, or on a timeline
duration mismatch. The VO-only timeline places ONLY the canonical take
at its window start (12.5 s); if the take overruns past the 18 s scene
end it is delivered UNTRUNCATED and the timeline extends by exactly the
overrun tail (recorded in the manifest) -- cutting a sentence in half
would corrupt the draft, and speeding it up is forbidden by D1. The
timeline is a DRAFT assembly, not a mix: no music/ambience stems, no
loudness normalization.
Outputs land in Art_Source/Audio/Muse/VO/CIN006_DRAFT/.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

SCENE_ID = "CIN_006"
SCENE_SECONDS = 18.0
VOICE = ("avocado_v2:MAI_03", "Helio (fictional system voice)")


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
    """Parse the canonical cue + alternate take from the CIN_006 timing."""
    deliveries = root / "Implementation" / "Content" / "Narrative" / "Deliveries"
    timing = json.loads(
        (deliveries / SCENE_ID / f"{SCENE_ID}_timing_v1.json")
        .read_text(encoding="utf-8"))
    srt = unicodedata.normalize(
        "NFC", (deliveries / SCENE_ID / f"{SCENE_ID}_vi.srt")
        .read_text(encoding="utf-8"))
    if abs(float(timing["durationSeconds"]) - SCENE_SECONDS) > 1e-9:
        print("SCENE DURATION != 18.0", file=sys.stderr)
        sys.exit(1)
    dialogues = [s for s in timing["shots"] if s.get("dialogue")]
    if len(dialogues) != 1:
        print(f"CANONICAL CUE COUNT {len(dialogues)} != 1", file=sys.stderr)
        sys.exit(1)
    shot = dialogues[0]
    dlg = shot["dialogue"]
    text = unicodedata.normalize("NFC", dlg["text"])
    if text not in srt:
        print("SRT MISMATCH: canonical text not in SRT", file=sys.stderr)
        sys.exit(1)
    if dlg["speaker"] != "NPC_HA_MAC":
        print(f"UNEXPECTED SPEAKER {dlg['speaker']}", file=sys.stderr)
        sys.exit(1)
    canonical = {
        "key": "CIN006_S03",
        "shotId": shot["shotId"],
        "sceneId": SCENE_ID,
        "speaker": dlg["speaker"],
        "onscreen": dlg.get("onscreen"),
        "voice": VOICE[0],
        "voiceLabel": VOICE[1],
        "mp3": "CIN006_S03.mp3",
        "wav": "VO_CIN_006_S03_HAMAC_draft_v1.wav",
        "text": dlg["text"],
        "windowSceneSeconds": dlg["windowSeconds"],
        "status": dlg.get("status"),
        "takeKind": "CANONICAL",
    }
    alt_src = timing["alternateTake"]
    alt_text = unicodedata.normalize("NFC", alt_src["text"])
    if alt_text in srt:
        print("ALT TAKE TEXT LEAKED INTO SRT (Q3 violation)",
              file=sys.stderr)
        sys.exit(1)
    alternate = {
        "key": "CIN006_ALT_T01",
        "takeId": alt_src["takeId"],
        "version": alt_src["version"],
        "shotId": None,
        "sceneId": SCENE_ID,
        "speaker": "NPC_HA_MAC",
        "speakerNote": ("The source direction assigns the S03 beat to "
                        "Ha Mac and does not cast the alternate reading "
                        "separately; read with the same draft voice as "
                        "a draft assumption, not a casting decision."),
        "onscreen": True,
        "voice": VOICE[0],
        "voiceLabel": VOICE[1],
        "mp3": "CIN006_ALT_T01.mp3",
        "wav": "VO_CIN_006_ALT_T01_HAMAC_draft_v1-alt.wav",
        "text": alt_src["text"],
        "windowSceneSeconds": None,
        "status": alt_src["status"],
        "takeKind": "ALTERNATE_TAKE_DOES_NOT_REPLACE_CANONICAL",
    }
    return canonical, alternate


def build_take(take: dict, mp3_dir: Path, out: Path) -> dict:
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
    ln = loudnorm(wav)
    if take["windowSceneSeconds"] is not None:
        window = take["windowSceneSeconds"][1] - take["windowSceneSeconds"][0]
        slack = window - duration
        fit = "FITS" if slack >= 0 else "OVERRUN"
        timeline_start = take["windowSceneSeconds"][0]
    else:
        window = None
        slack = None
        fit = "NO_WINDOW_ASSIGNED"
        timeline_start = None
    print(f"{take['key']}: {duration:.4f}s, fit {fit}"
          + (f" (window {window:.1f}s, slack {slack:+.4f}s)"
             if window is not None else " (no window)")
          + f" LUFS {ln['input_i']} TP {ln['input_tp']}")
    return {
        **take,
        "wav": take["wav"],
        "wavSha256": sha256(wav),
        "rawMp3": raw.name,
        "rawMp3Sha256": sha256(raw),
        "durationSeconds": round(duration, 4),
        "windowSeconds": window,
        "slackSeconds": (round(slack, 4) if slack is not None else None),
        "fit": fit,
        "timelineStartSeconds": timeline_start,
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
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--mp3-dir", required=True)
    ap.add_argument("--out-dir",
                    default="Art_Source/Audio/Muse/VO/CIN006_DRAFT")
    args = ap.parse_args()
    root = Path(args.root)
    mp3_dir = Path(args.mp3_dir)
    out = root / args.out_dir
    out.mkdir(parents=True, exist_ok=True)

    canonical_src, alternate_src = load_cues(root)
    canonical = build_take(canonical_src, mp3_dir, out)
    alternate = build_take(alternate_src, mp3_dir, out)

    # VO-only timeline: ONLY the canonical take at its window start.
    # The alternate take is never placed on any timeline (Q3). An
    # overrunning canonical take stays untruncated: the timeline
    # extends past the scene end by exactly the overrun tail.
    timeline = out / "CIN006_VO_timeline_draft_v1.wav"
    ms = int(round(canonical["timelineStartSeconds"] * 1000))
    tl_target = max(SCENE_SECONDS,
                    canonical["timelineStartSeconds"]
                    + canonical["durationSeconds"])
    tl_target = round(tl_target, 3)
    overrun_tail = round(tl_target - SCENE_SECONDS, 4)
    run(["ffmpeg", "-y", "-v", "error",
         "-i", str(out / canonical["wav"]),
         "-filter_complex",
         f"[0:a]adelay={ms}:all=1,apad=whole_dur={tl_target},"
         f"atrim=0:{tl_target}[aout]",
         "-map", "[aout]", "-ar", "48000", "-ac", "1", str(timeline)])
    tp = probe(timeline)
    tl_duration = float(tp["format"]["duration"])
    print(f"timeline: {tl_duration:.4f}s (scene {SCENE_SECONDS:.1f}s, "
          f"overrun tail {overrun_tail:.4f}s)")
    if abs(tl_duration - tl_target) > 0.05:
        print("TIMELINE DURATION MISMATCH", file=sys.stderr)
        sys.exit(1)

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 19 - CIN_006 VO drafts "
                      "(canonical cue + alternate take)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "d1Approval": ("D1 APPROVED draft VO production only for the 21 "
                       "dialogue windows; no canon changes, no voice "
                       "speed-up to fit."),
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL_VO",
        "sceneId": SCENE_ID,
        "sceneSeconds": SCENE_SECONDS,
        "dialogueWindowsCovered": "21/21 (this checkpoint closes the "
                                  "last one, CIN_006_S03)",
        "notes": [
            "Fictional system voices only; no real-voice cloning, "
            "no unlicensed samples.",
            "Canonical window 12.5-17.5 s is PROPOSED_ANIMATIC_PLACEMENT "
            "in the timing JSON, approved by D1 for draft VO production "
            "only; it is not a picture/mix lock.",
            "Alternate take CIN_006_ALT_T01 (v1-alt) has its own "
            "takeId/version per DEC-MEDIA-P0 Q3; it does NOT replace "
            "the canonical dialogue, is NOT in the SRT and is NOT "
            "placed on the scene timeline.",
            "All takes synthesized at speed 100 (D1: no voice "
            "speed-up to fit). An OVERRUN canonical take is delivered "
            "unchanged and flagged; the director decides whether to "
            "widen its window or trim its line.",
            "Male characters share one production voice (Helio) in "
            "this draft; they are NOT voice-distinct. Distinct casting "
            "is a director decision.",
            "Per-take loudness only, NOT a mix PASS; stems stay "
            "separate.",
            "Timeline is VO-only draft assembly (canonical take only); "
            "no music/ambience mixed in.",
            "If the canonical take overruns past the 18 s scene end, "
            "the timeline extends by exactly the overrun tail so the "
            "take is delivered untruncated; see timeline.sceneSeconds "
            "vs timeline.durationSeconds and the take's slackSeconds. "
            "The director decides: widen the window/scene, trim the "
            "line, or accept the bleed.",
        ],
        "takes": [canonical, alternate],
        "timeline": {
            "file": timeline.name,
            "sha256": sha256(timeline),
            "durationSeconds": round(tl_duration, 4),
            "sceneSeconds": SCENE_SECONDS,
            "overrunTailSeconds": overrun_tail,
            "containsTakes": ["CIN006_S03"],
            "format": {"codec": tp["streams"][0]["codec_name"],
                       "sampleRateHz": int(tp["streams"][0]["sample_rate"]),
                       "channels": int(tp["streams"][0]["channels"])},
        },
    }
    (out / "CIN006_VO_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"OK: manifest written (canonical fit {canonical['fit']}, "
          f"alt take separate)")


if __name__ == "__main__":
    main()
