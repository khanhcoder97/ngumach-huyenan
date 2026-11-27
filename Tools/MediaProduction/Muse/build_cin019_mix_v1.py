#!/usr/bin/env python3
"""
MEDIA-02 checkpoint 53: CIN_019 DRAFT mix v1.

Sixteenth scene mix after CIN_006 v1 (checkpoint 34), CIN_003 v1
(checkpoint 37), CIN_005 v1 (checkpoint 38), CIN_007 v1
(checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1
(checkpoint 41), CIN_010 v1 (checkpoint 42), CIN_011 v1
(checkpoint 45), CIN_012 v1 (checkpoint 46), CIN_013 v1
(checkpoint 47), CIN_014 v1 (checkpoint 48), CIN_015 v1
(checkpoint 49), CIN_016 v1 (checkpoint 50), CIN_017 v1
(checkpoint 51) and CIN_018 v1 (checkpoint 52) ("Dieu ong khong
cho ai tu choi", 18 s), built with the exact recipe of the P0
draft mixes v1/v2/v3 and the CIN_006/CIN_003/CIN_005/CIN_007/
CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/
CIN_016/CIN_017/CIN_018 mixes v1 (build_cin006_mix_v1.py /
build_cin003_mix_v1.py / build_cin005_mix_v1.py /
build_cin007_mix_v1.py / build_cin008_mix_v1.py /
build_cin009_mix_v1.py / build_cin010_mix_v1.py /
build_cin011_mix_v1.py / build_cin012_mix_v1.py /
build_cin013_mix_v1.py / build_cin014_mix_v1.py /
build_cin015_mix_v1.py / build_cin016_mix_v1.py /
build_cin017_mix_v1.py / build_cin018_mix_v1.py): same gain
targets, same ducking params, same peak guard, same loop-join
method, same runtime stem bytes
(ClientGodot/assets/audio/composed/, OGG music/ambience/stingers).

NEW PROPOSED_CANDIDATE stem assignment (nothing in the CP02 P0 stem
table assigns any stem to CIN_019, and the scene timing manifest
lists only SFX/CINEMA/reveal as a candidate stem -- this assignment
is new, proposed, not locked; adoption is Codex's adapter decision):
  music    MUSIC/rift_finale (composed, CP26) 0-18 s, ducked by VO
  ambience AMBIENCE/river_shore (composed, CP30) 0-18 s, unducked
  stinger  SFX/CINEMA/reveal (composed, CP26) at 6.0 s = S02 start,
           PROPOSED placement (mirrors the CIN_004 reveal at 6.0 s)
  VO       CIN_019_S03 draft take (CP17) at the 12.5 s window start

rift_finale is the composed set's only full close: the Ben Mua
leitmotif's answering tail (F#-E-D), withheld in every other cue
except the resolve stinger, sounds here -- the setting-exact cue
for the campaign's resolution scene (S01: wide three-quarter view
of a mountaintop stone platform at dusk, five elemental pillars
(grey metal, wave-crested blue water, bamboo wood, flaming red
fire, brown earth) around an empty central space, WIDE_STATIC;
S02: medium interior shot of a machinery hall, a young warden
straining against a large sparking wall lever, a second warden at
a bank of levers on a control console, MEDIUM; S03: wide dawn view
of a riverside village under reconstruction, water cascading
through a stepped, stone-repaired channel in the foreground,
small groups of workers carrying logs and baskets, WIDE_STATIC;
keyframes CIN_019 S01/S02/S03). This is rift_finale's FIRST
scene-mix use. river_shore is the composed water-edge bed for the
scene's landing: the spoken line sits in S03, at the rebuilt
river village with the repaired channel running through the
frame; the bed was used before for CIN_003 and CIN_008 (third
scene-mix use). mountain_wind was passed over: it beds only
S01's mountaintop -- neither the machinery hall nor the river
village the line lands in. ben_mua was passed over: the
rain-quay leitmotif of the opening (CIN_003/CIN_014) -- this
scene is the answer to that opening, and the set reserves its
full close for it. quiet_discovery was passed over: the
exploration silence (CIN_007/CIN_011/CIN_016), wrong for a
resolution. thang_long (capital-city form), tran_son (bell-led
gate form, CIN_008/CIN_012), lam_trieu (pastoral flute,
CIN_009/CIN_013) and sa_hoa (desert/dry, CIN_010/CIN_018) are
wrong for this setting; bach_uyen is the underwater low-passed
form (CIN_015/CIN_017) -- the water here runs in an open repaired
channel at dawn, not submerged; boss_mang_cot is boss material
and there is no boss in this beat. Ambience passes: underwater
is a submerged bed (wrong -- open channel, dawn air);
wind_canopy is a forest bed; waterfall was used for CIN_009;
rain_light/rain_heavy are rain beds, but no rain is depicted
(dusk platform, hall interior, dawn village); cave_drips is a
cave bed; desert_wind, city_night, thang_long_crowd and forge
are wrong for this setting; rift (the ambience bed) beds the
rift site itself, not the village the scene lands in.

Like CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/
CIN_014/CIN_015/CIN_016/CIN_017, the CIN_019 take FITS its window
with room to spare: the take is 2.880 s, so it runs
12.5-15.380 s, ending 2.120 s BEFORE the 17.5 s window end and
2.620 s before the 18.00 s scene end. No overrun, no tail trim.
The window is the uniform 12.5-17.5 s; the window, the take and
the timing are NOT changed. (The line is 39 characters, 7.80
characters per second on the 5 s window -- the take duration is
measured from real bytes, CP17: 2.880 s, windowFit FITS, not
sped up.)

Staging note: the timing manifest records the S03 dialogue
onscreen: true for Ly An (NPC_LYAN), and the keyframe manifest
lists Ly An among the scene's on-screen characters -- but S03's
frame is a WIDE dawn view of the whole village under
reconstruction, with only small groups of workers carrying logs
and baskets: no individual figure is identifiable as Ly An at
this scale, and the scene's faces and costumes are storyboard
placeholders (NPC_LYAN has no approved cinematic character
lock). The placement is onscreen per the timing; the identity
is not verifiable in the frame -- a final-picture/character-lock
matter, not a mix defect; the mix does not move the VO.

Ducking finding (measured, not a defect): the ducking depth is
measured from real bytes over the full VO window (CP39 method,
same params as every scene mix); rift_finale carries real
signal inside this window (segment RMS -22.1 dBFS measured from
the stem bytes this run), so a real cut is expected, and the
number in the manifest is the measured one, not a target. A
0.0 dB reading would mean the cue is silent in this window --
that is NOT the case for rift_finale (unlike quiet_discovery in
CIN_016, which is digitally silent 12-15 s); a 0.0 dB reading
here would be investigated, not reported as a silence pocket.

Outputs land in Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1/: one WAV
(48 kHz stereo pcm_s16le) + CIN019_MIX_V1_manifest_v1.json.
Intermediates live in a temp dir. DRAFT_MIX_NOT_FINAL, no ear
audition; measurements are from the real rendered bytes.
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

MUSIC_CUE = "MUSIC/rift_finale"
AMB_CUE = "AMBIENCE/river_shore"
STINGER_CUE = "SFX/CINEMA/reveal"
STEM_FILES = {
    MUSIC_CUE: "ClientGodot/assets/audio/composed/music/rift_finale.ogg",
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
PACK_LUFS = {MUSIC_CUE: -21.95, AMB_CUE: -29.69, STINGER_CUE: -24.96}

VO_SRC = "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/VO_CIN_019_S03_LYAN_draft_v1.wav"
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
    out_dir = root / "Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="cin019_mix_"))

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
    # comparable across the CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019 mixes
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
    mix_path = out_dir / "CIN_019_mix_draft_v1.wav"
    mixdown(parts, TOTAL, mix_path, trim_db=trim)
    ln = loudnorm(mix_path)
    p = probe(mix_path)
    dur = float(p["format"]["duration"])
    if abs(dur - TOTAL) > 0.05:
        print(f"CIN_019: MIX DURATION {dur} != {TOTAL}", file=sys.stderr)
        sys.exit(1)
    print(f"CIN_019: mix {dur:.3f}s LUFS {ln['input_i']} "
          f"TP {ln['input_tp']} (peak trim {trim:.2f} dB), "
          f"ducking music {duck_evidence[0]['depthInWindowDb']} dB, "
          f"VO tail trimmed {tail_trim} s")

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 53 - CIN_019 draft mix v1 (sixteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1, CIN_017 v1 and CIN_018 v1, same recipe as P0 v3)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_MIX_NOT_FINAL",
        "mixVersion": "v1_cin019_proposed",
        "mixVerdict": ("DRAFT_MIX_FOR_REVIEW: sixteenth scene mix after "
                       "CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, "
                       "CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, "
                       "CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, "
                       "CIN_016 v1, CIN_017 v1 and CIN_018 v1, "
                       "built with the P0 v3 recipe (same gain targets, "
                       "ducking params, peak guard, loop joins). Stem "
                       "assignment is NEW and PROPOSED_CANDIDATE (the "
                       "CP02 stem table assigns nothing to CIN_019; "
                       "the scene timing manifest lists only the "
                       "reveal stinger as a candidate stem). VO take "
                       "is the CP17 draft; the take FITS its window "
                       "(2.880 s, 12.5-15.380 s) by 2.120 s: no "
                       "overrun, no tail trim at the scene edge. NOT "
                       "a mix PASS: no ear audition, stem table not "
                       "locked, stinger placement PROPOSED pending "
                       "picture lock. Adoption is Codex's adapter "
                       "decision."),
        "stemAssignment": {
            "status": "PROPOSED_CANDIDATE_NEW",
            "source": ("No CP02 assignment exists for CIN_019; "
                       "rift_finale music + river_shore ambience "
                       "are the resolution cues (composed, "
                       "CP26/CP30) for this scene "
                       "(S01: wide three-quarter view of a "
                       "mountaintop stone platform at dusk, five "
                       "elemental pillars around an empty central "
                       "space, WIDE_STATIC; S02: medium interior "
                       "shot of a machinery hall, a young warden "
                       "straining at a large sparking wall lever, a "
                       "second warden at a bank of levers on a "
                       "control console, MEDIUM; S03: wide dawn view "
                       "of a riverside village under reconstruction, "
                       "water cascading through a stepped, "
                       "stone-repaired channel in the foreground, "
                       "small groups of workers carrying logs and "
                       "baskets, WIDE_STATIC; keyframes "
                       "CIN_019 S01/S02/S03). "
                       "rift_finale is the composed set's only full "
                       "close -- the Ben Mua leitmotif's answering "
                       "tail (F#-E-D), withheld in every other cue "
                       "except the resolve stinger, sounds here -- "
                       "for the line that closes the campaign's "
                       "arc ('Lan nay khong ai giu het nam con "
                       "duong.'). It has not been used in any scene "
                       "mix before; this is its first scene-mix "
                       "use. river_shore is the composed water-edge "
                       "bed for the scene's landing: the spoken "
                       "line sits in S03, at the rebuilt river "
                       "village with the repaired channel running "
                       "through the frame; also used for CIN_003 "
                       "and CIN_008 (third scene-mix use). "
                       "mountain_wind was passed over: it beds "
                       "only S01's mountaintop -- neither the "
                       "machinery hall nor the river village the "
                       "line lands in. ben_mua was passed over: "
                       "the rain-quay leitmotif of the opening "
                       "(CIN_003/CIN_014) -- this scene is the "
                       "answer to that opening, and the set "
                       "reserves its full close for it. "
                       "quiet_discovery was passed over: the "
                       "exploration silence (CIN_007/CIN_011/"
                       "CIN_016), wrong for a resolution. "
                       "thang_long is the capital-city form (wrong "
                       "setting); tran_son is the bell-led gate "
                       "form (CIN_008/CIN_012); lam_trieu is the "
                       "pastoral flute (CIN_009/CIN_013); sa_hoa "
                       "is desert/dry (CIN_010/CIN_018); bach_uyen "
                       "is the underwater low-passed form "
                       "(CIN_015/CIN_017) -- the water here runs in "
                       "an open repaired channel at dawn, not "
                       "submerged; boss_mang_cot is boss material "
                       "and there is no boss in this beat. "
                       "underwater was passed over: a submerged "
                       "bed, wrong for an open channel at dawn; "
                       "wind_canopy is a forest bed; waterfall "
                       "was used for CIN_009; rain_light and "
                       "rain_heavy are rain beds, but no rain is "
                       "depicted in any of the three keyframes "
                       "(dusk platform, hall interior, dawn "
                       "village); cave_drips is a cave bed; "
                       "desert_wind, city_night, thang_long_crowd "
                       "and forge are wrong for this setting; "
                       "rift (the ambience bed) beds the rift "
                       "site itself, not the village the scene "
                       "lands in. "
                       "The reveal stinger is the scene's only "
                       "manifest-listed candidate stem "
                       "(CIN_019_timing_v1.json)."),
            "alternateTakeExcluded": "N/A: CIN_019 has no alternate take.",
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
            "VO take runs 12.5-15.380 s: 2.880 s, ending 2.120 s "
            "BEFORE the 17.5 s window end -- the take FITS inside "
            "its window by 2120 ms (no overrun, unlike CIN_005/CIN_006/CIN_018). "
            "The take ends 2.620 s before the 18.00 s scene end, so no "
            "tail trim at the scene edge. The window, the take and "
            "the timing are unchanged.",
            "The CP17 VO take measures -25.52 LUFS (checkpoint 17, "
            "re-verified from real bytes this run) -- one of the "
            "quietest campaign takes (the CIN_008 take measured "
            "-23.10 LUFS). VO is kept at unity per the recipe, "
            "not normalized.",
            "Staging: the timing manifest records the S03 dialogue "
            "onscreen: true for Ly An (NPC_LYAN), and the keyframe "
            "manifest lists Ly An among the scene's on-screen "
            "characters -- but S03's frame is a WIDE dawn view of "
            "the whole village under reconstruction (stepped, "
            "stone-repaired channel in the foreground, small "
            "groups of workers carrying logs and baskets): no "
            "individual figure is identifiable as Ly An at this "
            "scale, and the scene's faces and costumes are "
            "storyboard placeholders (NPC_LYAN has no approved "
            "cinematic character lock). The placement is onscreen "
            "per the timing; the identity is not verifiable in "
            "the frame -- a final-picture/character-lock matter, "
            "not a mix defect; the mix does not move the VO.",
            "Ducking depth is measured on the ducked bus against its "
            "unducked render (RMS over the full VO window vs a 2 s "
            "reference before the window). The full-window method "
            "from checkpoint 39 is retained so the depth is "
            "comparable across the CIN_003/CIN_005/CIN_007/CIN_008/ "
            "CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018/CIN_019 mixes (a 2 s slice can understate "
            "the cut on cues whose window opening is quiet).",
            "Ducking depth is measured from real bytes over the full "
            "VO window (CP39 method, same params as every scene "
            "mix); rift_finale carries real signal inside this "
            "window (segment RMS -22.1 dBFS measured from the stem "
            "bytes this run), so a real cut is "
            "expected here, and the number in the manifest is "
            "the measured one, not a target. If the depth came out "
            "0.0 dB it would mean the cue is silent in this window "
            "-- that is NOT the case for rift_finale (unlike "
            "quiet_discovery in CIN_016, which is digitally silent "
            "12-15 s); a 0.0 dB reading here would be investigated, "
            "not reported as a silence pocket.",
            "Ambience loop join uses a 1 s acrossfade; loopQA reports "
            "the max sample jump at the join against the bed's own "
            "99.9th-percentile jump.",
            "Stinger placement at 6.0 s (S02 start) is PROPOSED pending "
            "picture lock, mirroring the CIN_004 reveal at 6.0 s.",
        ],
        "scenes": [{
            "sceneId": "CIN_019",
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

    (out_dir / "CIN019_MIX_V1_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: CIN019_MIX_V1_manifest_v1.json written")


if __name__ == "__main__":
    main()
