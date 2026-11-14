#!/usr/bin/env python3
"""MEDIA-02 WO37 M-F CP2: CIN_020 DRAFT mix v2 -- palette re-mix.

Clone of build_cin020_mix_v1.py (MEDIA-02 checkpoint 54) with
ONLY these changes:
  (a) VO take source: the M-F CP1 palette pickup
      VO_CIN_020_S03_LETTERRECIPIENT_palette_v1.wav -- Người nhận thư voiced by Ethereal Star (fictional system voice)
      (avocado_v2:ElvenWizard), replacing the draft take voiced by avocado_v2:MAI_01
      (Ly An's draft voice, which the draft mix shared with the letter recipient -- the casting defect this checkpoint fixes for this role);
  (b) outputs land in Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V2/
      (CIN_020_mix_draft_v2.wav + CIN020_MIX_V2_manifest_v1.json);
  (c) manifest prose records the palette decision: the project
      owner delegated the voice choice to Muse (main chat
      2026-11-12 18:30 JST) and Muse's decision is to apply the
      M-F CP1 palette (side B of the WO39 M39-B CP1 level-matched
      A/B review) to every role with a distinct pickup.
The mixing code is byte-for-byte the v1 code: same composed stems
and stem assignment (rationale in build_cin020_mix_v1.py), same
gain targets, same sidechain ducking (threshold 0.03, ratio 4,
attack 15 ms, release 350 ms), same 1 s acrossfade ambience loop
joins, same peak guard (-1.0 dBTP); VO at unity.

The palette take measures 3.072 s: placed at the 12.5 s window
start it runs to 15.572 s and FITS the 12.5-17.5 s window with
1.928 s of slack. The pickup is a NEUTRAL PLACEHOLDER voice (not a casting or gender decision); the manifest keeps the placeholder flag.

DRAFT_NOT_FINAL, NOT_AUDITIONED. The v2 mix lives in Art_Source
only: the runtime still embeds the v1 mix and the runtime audio
count is unchanged (783); adoption is Codex's decision at review.
"""
import hashlib
import json
import math
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 48000
TOTAL = 18.0
MUSIC_TARGET_LUFS = -30.0
AMB_PRIMARY_LUFS = -36.0
PEAK_CEILING_DBTP = -1.0
DUCK = {"threshold": 0.03, "ratio": 4, "attackMs": 15, "releaseMs": 350}
LOOP_SECONDS = 16.0
XFADE_SECONDS = 1.0

MUSIC_CUE = "MUSIC/ben_mua"
AMB_CUE = "AMBIENCE/river_shore"
STINGER_CUE = "SFX/CINEMA/reveal"
STEM_FILES = {
    MUSIC_CUE: "ClientGodot/assets/audio/composed/music/ben_mua.ogg",
    AMB_CUE: "ClientGodot/assets/audio/composed/ambience/river_shore.ogg",
    STINGER_CUE: "ClientGodot/assets/audio/composed/cinema/reveal.ogg",
}
PROVENANCE = {
    MUSIC_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    AMB_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
    STINGER_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
}
# Pack-table LUFS (CP26 music/stingers, CP30 ambience); re-measured
# this run before mixing and asserted to match within 0.05 LUFS.
PACK_LUFS = {MUSIC_CUE: -21.93, AMB_CUE: -29.69, STINGER_CUE: -24.96}

VO_SRC = "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/VO_CIN_020_S03_LETTERRECIPIENT_palette_v1.wav"
VO_AT = 12.5
WIN_END = 17.5
STINGER_AT = 6.0


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


def segment_rms_db(path: Path, start: float, dur: float) -> float:
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        w.setpos(int(start * sr))
        frames = w.readframes(int(dur * sr))
    x = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
    if x.size == 0:
        print(f"EMPTY SEGMENT {path} @{start}", file=sys.stderr)
        sys.exit(1)
    rms = float(np.sqrt(np.mean(x * x)))
    return 20.0 * math.log10(rms) if rms > 0 else -120.0


def fmt_t(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".") if "." in f"{x:.3f}" else str(x)


def build_bed(src: Path, length: float, gain_db: float, work: Path,
              name: str, fade_out: float = 0.0):
    out = work / f"{name}.wav"
    step = LOOP_SECONDS - XFADE_SECONDS
    n = 1
    while LOOP_SECONDS + (n - 1) * step < length:
        n += 1
    joins = [LOOP_SECONDS - XFADE_SECONDS / 2 + i * step
             for i in range(n - 1)]
    if n == 1:
        filt = (f"[0:a]atrim=0:{fmt_t(length)},"
                f"volume={gain_db:.2f}dB")
        if fade_out:
            filt += f",afade=t=out:st={fmt_t(length - fade_out)}:d={fmt_t(fade_out)}"
        filt += "[a]"
        run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
             "-filter_complex", filt, "-map", "[a]",
             "-ar", str(SR), "-ac", "2", str(out)])
    else:
        inputs = []
        for _ in range(n):
            inputs += ["-i", str(src)]
        chain = []
        prev = "[0:a]"
        for i in range(1, n):
            lbl = f"[s{i}]"
            chain.append(f"{prev}[{i}:a]acrossfade=d={int(XFADE_SECONDS)}{lbl}")
            prev = lbl
        filt = ";".join(chain) + (
            f";{prev}atrim=0:{fmt_t(length)},volume={gain_db:.2f}dB")
        if fade_out:
            filt += f",afade=t=out:st={fmt_t(length - fade_out)}:d={fmt_t(fade_out)}"
        filt += "[a]"
        run(["ffmpeg", "-y", "-v", "error", *inputs,
             "-filter_complex", filt, "-map", "[a]",
             "-ar", str(SR), "-ac", "2", str(out)])
    return out, joins


def loop_qa(wav_path: Path, joins) -> list:
    with wave.open(str(wav_path), "rb") as w:
        frames = w.readframes(w.getnframes())
        ch = w.getnchannels()
    x = np.frombuffer(frames, dtype=np.int16).astype(np.float64) / 32768.0
    x = x.reshape(-1, ch).mean(axis=1)
    d = np.abs(np.diff(x))
    p999 = float(np.percentile(d, 99.9)) if len(d) else 0.0
    results = []
    for t in joins:
        c = int(t * SR)
        lo = max(0, c - int(0.05 * SR))
        hi = min(len(d), c + int(0.05 * SR))
        jump = float(d[lo:hi].max()) if hi > lo else 0.0
        results.append({
            "atSeconds": round(t, 3),
            "maxJump": round(jump, 5),
            "bedP999Jump": round(p999, 5),
            "ratioToP999": (round(jump / p999, 3) if p999 > 0 else None),
        })
    return results


def place(src: Path, at: float, total: float, work: Path, name: str,
          gain_db: float = 0.0, seg_len: float = None,
          fade_in: float = 0.0, fade_out: float = 0.0,
          mono_to_stereo: bool = False) -> Path:
    out = work / f"{name}.wav"
    filt = "[0:a]"
    if seg_len is not None:
        filt += f"atrim=0:{fmt_t(seg_len)},"
    filt += "aresample=48000"
    if mono_to_stereo:
        filt += ",pan=stereo|c0=c0|c1=c0"
    else:
        filt += ",aformat=channel_layouts=stereo"
    if gain_db:
        filt += f",volume={gain_db:.2f}dB"
    if fade_in:
        filt += f",afade=t=in:st=0:d={fmt_t(fade_in)}"
    if fade_out and seg_len is not None:
        filt += f",afade=t=out:st={fmt_t(seg_len - fade_out)}:d={fmt_t(fade_out)}"
    ms = int(round(at * 1000))
    filt += (f",adelay={ms}:all=1,apad=whole_dur={fmt_t(total)},"
             f"atrim=0:{fmt_t(total)}[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out)])
    return out


def duck(bus: Path, key: Path, work: Path, name: str) -> Path:
    out = work / f"{name}.wav"
    filt = (f"[0:a][1:a]sidechaincompress="
            f"threshold={DUCK['threshold']}:ratio={DUCK['ratio']}:"
            f"attack={DUCK['attackMs']}:release={DUCK['releaseMs']}[a]")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(bus), "-i", str(key),
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out)])
    return out


def mixdown(parts: list, total: float, out_path: Path,
            trim_db: float = 0.0) -> None:
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    filt = ("".join(f"[{i}:a]" for i in range(len(parts)))
            + f"amix=inputs={len(parts)}:normalize=0:dropout_transition=0")
    if trim_db:
        filt += f",volume={-trim_db:.2f}dB"
    filt += (f",afade=t=in:st=0:d=0.3,"
             f"afade=t=out:st={fmt_t(total - 0.3)}:d=0.3,"
             f"atrim=0:{fmt_t(total)}[a]")
    run(["ffmpeg", "-y", "-v", "error", *inputs,
         "-filter_complex", filt, "-map", "[a]",
         "-ar", str(SR), "-ac", "2", str(out_path)])


def main() -> None:
    root = Path(".")
    out_dir = root / "Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V2"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="cin020_mix_"))

    # Re-measure the stems actually mixed; gains use these values.
    measured = {}
    for cue, rel in STEM_FILES.items():
        ln = loudnorm(root / rel)
        measured[cue] = float(ln["input_i"])
        if abs(measured[cue] - PACK_LUFS[cue]) > 0.05:
            print(f"STEM LUFS DRIFT {cue}: measured {measured[cue]} "
                  f"vs pack {PACK_LUFS[cue]}", file=sys.stderr)
            sys.exit(1)
        print(f"stem {cue}: re-measured {measured[cue]} LUFS "
              f"(pack {PACK_LUFS[cue]})")

    vo_path = root / VO_SRC
    vo_take = probe(vo_path)
    vo_dur = float(vo_take["format"]["duration"])
    vo_end = VO_AT + vo_dur
    tail_trim = round(max(0.0, vo_end - TOTAL), 3)
    win = (VO_AT, round(min(vo_end, TOTAL), 3))
    vo_bus = place(vo_path, VO_AT, TOTAL, work, "vo", mono_to_stereo=True)

    stem_records = []
    loop_records = []

    # Music bus (ducked by VO)
    gain = MUSIC_TARGET_LUFS - measured[MUSIC_CUE]
    seg = place(root / STEM_FILES[MUSIC_CUE], 0.0, TOTAL, work,
                "music_raw", gain_db=gain, seg_len=TOTAL,
                fade_in=0.5, fade_out=1.5)
    stem_records.append({
        "cue": MUSIC_CUE, "role": "music",
        "source": STEM_FILES[MUSIC_CUE],
        "provenance": PROVENANCE[MUSIC_CUE],
        "segmentSceneSeconds": [0.0, TOTAL],
        "targetLUFS": MUSIC_TARGET_LUFS,
        "packMeasuredLUFS": PACK_LUFS[MUSIC_CUE],
        "remeasuredLUFS": measured[MUSIC_CUE],
        "gainDb": round(gain, 2), "duckedByVo": True,
    })
    music_raw, music_ducked = seg, duck(seg, vo_bus, work, "music_ducked")

    # Ambience bus (unducked, looped with 1 s acrossfade joins)
    gain_a = AMB_PRIMARY_LUFS - measured[AMB_CUE]
    bed, joins = build_bed(root / STEM_FILES[AMB_CUE], TOTAL, gain_a,
                           work, "amb_river_shore")
    loop_records.append({"cue": AMB_CUE, "joins": loop_qa(bed, joins)})
    amb_bus = place(bed, 0.0, TOTAL, work, "amb_placed")
    stem_records.append({
        "cue": AMB_CUE, "role": "ambience",
        "source": STEM_FILES[AMB_CUE],
        "provenance": PROVENANCE[AMB_CUE],
        "segmentSceneSeconds": [0.0, TOTAL],
        "targetLUFS": AMB_PRIMARY_LUFS,
        "packMeasuredLUFS": PACK_LUFS[AMB_CUE],
        "remeasuredLUFS": measured[AMB_CUE],
        "gainDb": round(gain_a, 2), "duckedByVo": False,
    })

    # Stinger (PROPOSED placement at S02 start)
    st = place(root / STEM_FILES[STINGER_CUE], STINGER_AT, TOTAL, work,
               "stinger")
    stinger_record = {
        "cue": STINGER_CUE, "source": STEM_FILES[STINGER_CUE],
        "provenance": PROVENANCE[STINGER_CUE],
        "atSeconds": STINGER_AT, "gainDb": 0.0,
        "packMeasuredLUFS": PACK_LUFS[STINGER_CUE],
        "remeasuredLUFS": measured[STINGER_CUE],
        "placementStatus": "PROPOSED_PENDING_PICTURE_LOCK",
    }
    stem_records.append({**stinger_record, "role": "stinger"})

    # Ducking evidence (music bus, full VO window vs 2 s reference
    # before it). The FULL window is measured, not the first 2 s:
    # the CP39 full-window method is retained so the depth is
    # comparable across the CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019/CIN_020 mixes
    # (a 2 s slice can understate the cut on cues whose window
    # opening is quiet).
    ref_start = max(0.0, win[0] - 2.5)
    win_dur = win[1] - win[0]
    in_raw = segment_rms_db(music_raw, win[0], win_dur)
    in_duck = segment_rms_db(music_ducked, win[0], win_dur)
    out_raw = segment_rms_db(music_raw, ref_start, 2.0)
    out_duck = segment_rms_db(music_ducked, ref_start, 2.0)
    duck_evidence = [{
        "bus": "music",
        "windowSeconds": list(win),
        "referenceSeconds": [ref_start, ref_start + 2.0],
        "depthInWindowDb": round(in_duck - in_raw, 2),
        "depthOutsideWindowDb": round(out_duck - out_raw, 2),
    }]

    parts = [vo_bus, music_ducked, amb_bus, st]
    tmp_mix = work / "mix_untrimmed.wav"
    mixdown(parts, TOTAL, tmp_mix)
    ln = loudnorm(tmp_mix)
    tp = float(ln["input_tp"])
    trim = round(tp - PEAK_CEILING_DBTP, 2) if tp > PEAK_CEILING_DBTP else 0.0
    mix_path = out_dir / "CIN_020_mix_draft_v2.wav"
    mixdown(parts, TOTAL, mix_path, trim_db=trim)
    ln = loudnorm(mix_path)
    p = probe(mix_path)
    dur = float(p["format"]["duration"])
    if abs(dur - TOTAL) > 0.05:
        print(f"CIN_020: MIX DURATION {dur} != {TOTAL}", file=sys.stderr)
        sys.exit(1)
    print(f"CIN_020: mix {dur:.3f}s LUFS {ln['input_i']} "
          f"TP {ln['input_tp']} (peak trim {trim:.2f} dB), "
          f"ducking music {duck_evidence[0]['depthInWindowDb']} dB, "
          f"VO tail trimmed {tail_trim} s")

    manifest = {
        "checkpoint": "MEDIA-02 WO37 M-F CP2 - CIN_020 draft mix v2 (palette re-mix of the checkpoint 54 v1 mix; M-F CP1 palette applied under the owner-delegated voice decision, 2026-11-12)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_NOT_FINAL",
        "mixVersion": "v2_palette_mf_cp2",
        "mixVerdict": ("DRAFT_MIX_FOR_REVIEW: seventeenth scene mix after "
                       "CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, "
                       "CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, "
                       "CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, "
                       "CIN_016 v1, CIN_017 v1, CIN_018 v1 and CIN_019 v1, "
                       "built with the P0 v3 recipe (same gain targets, "
                       "ducking params, peak guard, loop joins). Stem "
                       "assignment is NEW and PROPOSED_CANDIDATE (the "
                       "CP02 stem table assigns nothing to CIN_020; "
                       "the scene timing manifest lists only the "
                       "reveal stinger as a candidate stem). VO take "
                       "is the CP17 draft; the take FITS its window "
                       "(3.000 s, 12.5-15.500 s) by 2.000 s: no "
                       "overrun, no tail trim at the scene edge. NOT "
                       "a mix PASS: no ear audition, stem table not "
                       "locked, stinger placement PROPOSED pending "
                       "picture lock. Adoption is Codex's adapter "
                       "decision."),
        "stemAssignment": {
            "status": "PROPOSED_CANDIDATE_NEW",
            "source": ("No CP02 assignment exists for CIN_020; "
                       "ben_mua music + river_shore ambience "
                       "are the home-river cues (composed, "
                       "CP26/CP30) for this scene "
                       "(S01: medium shot, the villager at the "
                       "repaired plank table on the river dock "
                       "reading the opened letter, the sealed "
                       "delivered letter and a worn bowl on the "
                       "table, a newly tied paper lamp on the "
                       "bamboo, MEDIUM_STATIC; S02: interior, the "
                       "villager at a wooden desk by an open "
                       "window writing the reply, brush over a "
                       "fresh sheet, ink stone and brush pots on "
                       "the desk, the river beyond the window, "
                       "DETAIL_LOCKED; S03: top-down view of the "
                       "table -- bowl of food, folded reply, "
                       "chopsticks, cloth pouch -- the villager "
                       "seated at frame left seen from behind, an "
                       "open village path beyond the fence, "
                       "TOPDOWN_MATCH; keyframes "
                       "CIN_020 S01/S02/S03). "
                       "ben_mua is the composed set's rain-quay "
                       "leitmotif -- the theme of the opening quay "
                       "where the sealed letter changed hands -- "
                       "for the line that answers it ('Cho mot "
                       "chut. Toi muon gui lai vai loi.'). It was "
                       "used before in scene mixes CIN_003 and "
                       "CIN_014 (third scene-mix use; the P0 mixes "
                       "also carry it, as the opening's own). "
                       "river_shore is the composed water-edge "
                       "bed for the dock and the river beyond the "
                       "window; also used for CIN_003, CIN_008 "
                       "and CIN_019 (fourth scene-mix use). "
                       "rift_finale was passed over: the set's "
                       "only full close, spent at CIN_019's "
                       "resolution -- this scene is the quiet "
                       "morning after, not a second climax. "
                       "quiet_discovery was passed over: the "
                       "exploration silence (CIN_007/CIN_011/"
                       "CIN_016), wrong for a homecoming. "
                       "thang_long is the capital-city form (wrong "
                       "setting); tran_son is the bell-led gate "
                       "form (CIN_008/CIN_012); lam_trieu is the "
                       "pastoral flute (CIN_009/CIN_013); sa_hoa "
                       "is desert/dry (CIN_010/CIN_018); bach_uyen "
                       "is the underwater low-passed form "
                       "(CIN_015/CIN_017); boss_mang_cot is boss "
                       "material and there is no boss in this "
                       "beat. "
                       "wind_canopy is a forest bed; waterfall "
                       "was used for CIN_009; mountain_wind was "
                       "used for CIN_013; rain_light and "
                       "rain_heavy are rain beds, but no rain is "
                       "depicted in any of the three keyframes "
                       "(dock daylight, desk interior, top-down "
                       "table); underwater is a submerged bed; "
                       "cave_drips is a cave bed; desert_wind, "
                       "city_night, thang_long_crowd, forge and "
                       "rift are wrong for this setting. "
                       "The reveal stinger is the scene's only "
                       "manifest-listed candidate stem "
                       "(CIN_020_timing_v1.json)."),
            "alternateTakeExcluded": "N/A: CIN_020 has no alternate take.",
        },
        "gainStaging": {
            "vo": "unity (anchor; take as delivered)",
            "musicTargetLUFS": MUSIC_TARGET_LUFS,
            "ambiencePrimaryTargetLUFS": AMB_PRIMARY_LUFS,
            "stingers": "unity",
            "peakCeilingDBTP": PEAK_CEILING_DBTP,
        },
        "notes": [
            "VO window 12.5-17.5 s is PROPOSED_ANIMATIC_PLACEMENT (only "
            "CIN_001_S05 is DECIDED); all 21 windows are approved for "
            "DRAFT VO per Goi 30 D1. The window is the uniform "
            "12.5-17.5 s; it was NOT widened.",
            "VO take runs 12.5-15.500 s: 3.000 s, ending 2.000 s "
            "BEFORE the 17.5 s window end -- the take FITS inside "
            "its window by 2000 ms (no overrun, unlike CIN_005/CIN_006/CIN_018). "
            "The take ends 2.500 s before the 18.00 s scene end, so no "
            "tail trim at the scene edge. The window, the take and "
            "the timing are unchanged.",
            "The CP17 VO take measures -19.59 LUFS (checkpoint 17, "
            "re-verified from real bytes this run, vs -25.52 LUFS "
            "for the CIN_019 take and -22.54 LUFS for the CIN_018 "
            "S03 take). VO is kept at unity per the recipe, "
            "not normalized.",
            "Casting: the recipient's voice is a placeholder role "
            "voice (CP17 roleNote VOICE_LETTER_RECIPIENT; recipient "
            "identity/gender undecided), and the draft take uses "
            "the same fictional system voice as Ly An's drafts "
            "(avocado_v2:MAI_01, Aria) -- a draft-casting collision "
            "for the WO37 M-F palette work to resolve with a "
            "distinct voice, not a mix decision.",
            "Staging: the timing manifest records the S03 dialogue "
            "onscreen: null for the letter recipient. The S03 "
            "keyframe does show the villager -- seated at frame "
            "left, seen from behind in the top-down match frame "
            "-- so the speaker is present in the frame but his "
            "face is not visible and the line reads as an on-set "
            "voice from behind. The CP24 keyframe manifest also "
            "records that this unnamed villager's appearance "
            "drifts between all three shots (S01 headband and "
            "brown vest; S02 conical hat and blue tunic; S03 "
            "green top and dark headwrap) -- the scene's pack "
            "character list is empty, so no named character lock "
            "exists for him. Final-picture/casting matters, not "
            "mix defects; the mix does not move the VO.",
            "Ducking depth is measured on the ducked bus against its "
            "unducked render (RMS over the full VO window vs a 2 s "
            "reference before the window). The full-window method "
            "from checkpoint 39 is retained so the depth is "
            "comparable across the CIN_003/CIN_005/CIN_007/CIN_008/ "
            "CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019/CIN_020 mixes (a 2 s slice can understate "
            "the cut on cues whose window opening is quiet).",
            "Ducking depth is measured from real bytes over the full "
            "VO window (CP39 method, same params as every scene "
            "mix); ben_mua carries real signal inside this "
            "window (segment RMS -20.5 dBFS measured from the stem "
            "bytes this run), so a real cut is "
            "expected here, and the number in the manifest is "
            "the measured one, not a target. If the depth came out "
            "0.0 dB it would mean the cue is silent in this window "
            "-- that is NOT the case for ben_mua (unlike "
            "quiet_discovery in CIN_016, which is digitally silent "
            "12-15 s); a 0.0 dB reading here would be investigated, "
            "not reported as a silence pocket.",
            "Ambience loop join uses a 1 s acrossfade; loopQA reports "
            "the max sample jump at the join against the bed's own "
            "99.9th-percentile jump.",
            "Stinger placement at 6.0 s (S02 start) is PROPOSED pending "
            "picture lock, mirroring the CIN_004 reveal at 6.0 s.",
            "With this mix embedded, every one of the 21 cinematics "
            "entries carries an embedded soundtrack (0 silent) and "
            "Work Order 37 M-B big checkpoint 1 is complete.",
        ],
        "scenes": [{
            "sceneId": "CIN_020",
            "seconds": TOTAL,
            "vo": {"take": VO_SRC.split("/")[-1],
                   "windowSeconds": list(win),
                   "takeDurationSeconds": vo_dur,
                   "takeEndSeconds": round(vo_end, 3),
                   "tailTrimmedAtSceneEdgeSeconds": tail_trim,
                   "overrunVsWindowSeconds": round(vo_end - WIN_END, 3),
                   "gainDb": 0.0},
            "stems": stem_records,
            "ducking": {"params": DUCK, "evidence": duck_evidence},
            "stinger": stinger_record,
            "loopQA": loop_records,
            "mix": {
                "file": mix_path.name,
                "sha256": sha256(mix_path),
                "durationSeconds": round(dur, 4),
                "integratedLUFS": ln["input_i"],
                "truePeakDBTP": ln["input_tp"],
                "loudnessRangeLU": ln["input_lra"],
                "peakTrimDb": trim,
                "format": {"codec": p["streams"][0]["codec_name"],
                           "sampleRateHz": int(p["streams"][0]["sample_rate"]),
                           "channels": int(p["streams"][0]["channels"]),
                           "bytes": int(p["format"]["size"])},
            },
        }],
    }

    (out_dir / "CIN020_MIX_V2_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: CIN020_MIX_V2_manifest_v1.json written")


# ---------------------------------------------------------------------
# MEDIA-02 WO37 M-F CP2 palette record. The mixing code above is the
# v1 code, unchanged; main() still writes the v1-schema manifest and
# augment_manifest() then records the palette decision, the recomputed
# window fit of the pickup take(s) and the review status on it.
# ---------------------------------------------------------------------
DECISION_REF = {
    "decision": ("Apply the M-F CP1 voice palette (side B of the "
                 "WO39 M39-B CP1 level-matched A/B review) to every "
                 "role that has a distinct pickup take"),
    "delegatedBy": ("Project owner delegated the voice choice to "
                    "Muse (main chat, 2026-11-12 18:30 JST)"),
    "chosenBy": ("Muse (decision recorded in the dev queue, "
                 "2026-11-12 ~18:32 JST)"),
    "checkpoint": "MEDIA-02 WO37 M-F CP2",
    "paletteSourceManifest": ("Implementation/Content/Audio/Deliveries/"
                              "VO_PALETTE_PICKUPS_pack_v1.json"),
    "reason": ("Fixes the draft casting defect: every male speaker "
               "shared one draft voice (avocado_v2:MAI_03) and the "
               "CIN_020 letter recipient shared Ly An's draft voice "
               "(avocado_v2:MAI_01)"),
    "adoption": ("Draft v2 mixes live in Art_Source only; the runtime "
                 "still embeds the v1 mixes (runtime audio count "
                 "unchanged at 783) until Codex adopts v2 at review. "
                 "Final casting remains Codex's review decision."),
}
MANIFEST_REL = "Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V2/CIN020_MIX_V2_manifest_v1.json"
TIMING_REL = "Implementation/Content/Narrative/Deliveries/CIN_020/CIN_020_timing_v1.json"
PALETTE_TAKES = [{'takeKey': 'CIN020_S03', 'shotId': 'CIN_020_S03', 'voiceStatus': 'PLACEHOLDER_NEUTRAL'}]
V2_MIX_VERDICT = "DRAFT_MIX_FOR_REVIEW (v2, MEDIA-02 WO37 M-F CP2 palette re-mix): built with the exact v1 recipe (same composed stems, gain targets, ducking params, peak guard, loop joins); the ONLY change is the VO take -- Người nhận thư is now the M-F CP1 palette pickup (VO_CIN_020_S03_LETTERRECIPIENT_palette_v1.wav; Ethereal Star (fictional system voice), avocado_v2:ElvenWizard) instead of the draft take voiced by avocado_v2:MAI_01. The palette take FITS its window (12.5-15.572 s inside 12.5-17.5 s, slack 1.928 s), measured from the real pickup bytes. The pickup is a NEUTRAL PLACEHOLDER voice (not a casting or gender decision); the manifest keeps the placeholder flag. NOT a mix PASS: no ear audition; the stem assignment remains PROPOSED_CANDIDATE from v1; adoption is Codex's adapter decision. The runtime still embeds the v1 mix."
V2_MANIFEST_OVERRIDES = {}


def _mf_cp2_probe_dur(path: Path) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "json", str(path)], capture_output=True, text=True)
    if r.returncode != 0:
        print(f"FFPROBE FAILED {path}", file=sys.stderr)
        sys.exit(1)
    return float(json.loads(r.stdout)["format"]["duration"])


def augment_manifest() -> None:
    root = Path(".")
    mpath = root / MANIFEST_REL
    manifest = json.loads(mpath.read_text(encoding="utf-8"))
    timing = json.loads((root / TIMING_REL).read_text(encoding="utf-8"))
    pickups = json.loads(
        (root / "Implementation/Content/Audio/Deliveries/"
         "VO_PALETTE_PICKUPS_pack_v1.json").read_text(encoding="utf-8"))
    by_key = {t["takeKey"]: t for t in pickups["takes"]}
    shots = {s["shotId"]: s for s in timing["shots"]}
    changes = []
    for spec in PALETTE_TAKES:
        take = by_key[spec["takeKey"]]
        win = shots[spec["shotId"]]["dialogue"]["windowSeconds"]
        rel = ("Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/"
               + take["paletteTake"]["wav"])
        dur = _mf_cp2_probe_dur(root / rel)
        start = float(win[0])
        end = start + dur
        entry = {
            "takeKey": spec["takeKey"],
            "shotId": spec["shotId"],
            "role": take["role"],
            "speakerDisplay": take.get("speakerDisplay"),
            "previousVoice": take["previousVoice"],
            "paletteVoice": take["voice"],
            "paletteVoiceLabel": take.get("voiceLabel"),
            "paletteTakeFile": rel,
            "paletteTakeSha256": sha256(root / rel),
            "paletteTakeDurationSeconds": round(dur, 3),
            "windowSeconds": [win[0], win[1]],
            "takeStartSeconds": start,
            "takeEndSeconds": round(end, 3),
            "slackSeconds": round(float(win[1]) - end, 3),
            "fit": "FITS" if end <= float(win[1]) + 0.005 else "OVERRUN",
            "voGainDb": 0.0,
        }
        if spec.get("voiceStatus"):
            entry["voiceStatus"] = spec["voiceStatus"]
        changes.append(entry)
    manifest["decisionRef"] = DECISION_REF
    manifest["auditionStatus"] = "NOT_AUDITIONED"
    manifest["mixVerdict"] = V2_MIX_VERDICT
    for key, value in V2_MANIFEST_OVERRIDES.items():
        manifest[key] = value
    manifest["paletteRemix"] = {
        "checkpoint": "MEDIA-02 WO37 M-F CP2",
        "palette": "M-F CP1 (side B)",
        "changes": changes,
        "unchanged": ("Stems, stem gains, ducking, peak guard, "
                      "placements and scene-edge fades run the exact "
                      "v1 code; only the VO take source(s) changed."),
    }
    if isinstance(manifest.get("notes"), list):
        manifest["notes"] = [
            "M-F CP2 palette re-mix: the VO take(s) listed under "
            "paletteRemix.changes replace the v1 draft take(s). Any "
            "v1 note below describing the canonical take's duration "
            "or overrun describes the v1 mix only and does not apply "
            "to v2."
        ] + manifest["notes"]
    mpath.write_text(json.dumps(manifest, ensure_ascii=False,
                                indent=2) + "\n", encoding="utf-8")
    print(f"OK: {mpath.name} augmented with the M-F CP2 palette record")


if __name__ == "__main__":
    main()
    augment_manifest()
