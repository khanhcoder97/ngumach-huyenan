#!/usr/bin/env python3
"""MEDIA-02 checkpoint 52: CIN_018 DRAFT mix v1.

Fifteenth scene mix after CIN_006 v1 (checkpoint 34), CIN_003 v1
(checkpoint 37), CIN_005 v1 (checkpoint 38), CIN_007 v1
(checkpoint 39), CIN_008 v1 (checkpoint 40), CIN_009 v1
(checkpoint 41), CIN_010 v1 (checkpoint 42), CIN_011 v1
(checkpoint 45), CIN_012 v1 (checkpoint 46), CIN_013 v1
(checkpoint 47), CIN_014 v1 (checkpoint 48), CIN_015 v1
(checkpoint 49), CIN_016 v1 (checkpoint 50) and CIN_017 v1
(checkpoint 51) ("Dieu ong khong cho ai tu choi", 18 s), built
with the exact recipe of the P0 draft mixes v1/v2/v3 and the
CIN_006/CIN_003/CIN_005/CIN_007/CIN_008/CIN_009/CIN_010/CIN_011/
CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017 mixes v1
(build_cin006_mix_v1.py / build_cin003_mix_v1.py /
build_cin005_mix_v1.py / build_cin007_mix_v1.py /
build_cin008_mix_v1.py / build_cin009_mix_v1.py /
build_cin010_mix_v1.py / build_cin011_mix_v1.py /
build_cin012_mix_v1.py / build_cin013_mix_v1.py /
build_cin014_mix_v1.py / build_cin015_mix_v1.py /
build_cin016_mix_v1.py / build_cin017_mix_v1.py): same gain
targets, same ducking params, same peak guard, same loop-join
method, same runtime stem bytes
(ClientGodot/assets/audio/composed/, OGG music/ambience/stingers).

CIN_018 is the ONLY campaign scene with TWO dialogue windows
(recorded in its scene export manifest), so this is the first
scene mix with two VO takes. Both takes are placed at their
window starts and duck the music bus through ONE combined VO
bus (the sidechain key carries both takes), so the music dips
under each line and recovers in the 3.12 s gap between them
(9.38-12.5 s; compressor release 350 ms). Ducking evidence is
measured separately over EACH window (CP39 full-window method
per window), so the two depths are comparable with the
single-window mixes.

NEW PROPOSED_CANDIDATE stem assignment (nothing in the CP02 P0 stem
table assigns any stem to CIN_018, and the scene timing manifest
lists only SFX/CINEMA/reveal as a candidate stem -- this assignment
is new, proposed, not locked; adoption is Codex's adapter decision):
  music    MUSIC/sa_hoa (composed, CP26) 0-18 s, ducked by VO
  ambience AMBIENCE/desert_wind (composed, CP30) 0-18 s, unducked
  stinger  SFX/CINEMA/reveal (composed, CP26) at 0.0 s = S01 start,
           PROPOSED placement (see the stinger note below: the
           recipe's usual 6.0 s would sit under the S02 dialogue)
  VO       CIN_018_S02 draft take (CP17) at the 6.5 s window start
           + CIN_018_S03 draft take (CP17) at the 12.5 s window start

sa_hoa is the composed set's desert form ("Sa Hoa -- Lo va cat":
kiln and sand, A minor pentatonic, dry bright plucks, 110 BPM) --
the setting-exact cue for a drought scene built around the lack
of water (S01: cracked drought field, a man pouring the last
water from a gourd into a cup, a sealed petition letter and a
measuring post, MEMORY_MEDIUM; S02: Co Vo Tuong at his desk
with scrolls and seal, MEMORY_DETAIL; S03: the masked hooded
figure beside the copper water-machine at night, MEDIUM_STATIC;
keyframes CIN_018 S01/S02/S03). desert_wind is the desert wind
bed for the dry field and the night bamboo of all three shots.
Both are second scene-mix uses -- the same pairing as CIN_010
(the ash-gold caravan rest), stated plainly because the two
scenes share the Sa Hoa / desert setting and the cue set has a
single desert form. ben_mua was passed over: the rain-quay
leitmotif, wrong setting for a drought scene about water that
is NOT there. thang_long was passed over: the capital-city
form. tran_son was passed over: the bell-led gate form, used
for CIN_008 and CIN_012. lam_trieu was passed over: the
pastoral flute, used for CIN_013. quiet_discovery was passed
over: the exploration silence, used for CIN_007/CIN_011/CIN_016
-- wrong for a confrontation scene. bach_uyen was passed over:
the underwater low-passed form, used for CIN_015/CIN_017 --
the opposite of this scene (water present there, water
withheld here). boss_mang_cot is boss material for the WRONG
boss (Mang Cot, not Co Vo Tuong) -- and this beat is a quiet
confrontation, not a boss fight. rift_finale is the set's only
full close (finale material, wrong for a mid-campaign chapter
beat). river_shore was passed over: a water-edge bed, used for
CIN_003/CIN_008 -- the S01 field is cracked dry earth, not a
shore. rain_light/rain_heavy are rain beds, but no rain is
depicted in any of the three keyframes (drought field, desk
interior, night yard -- no rain streaks). mountain_wind was
used for CIN_013; forge was used for CIN_012; waterfall was
used for CIN_009; wind_canopy is a forest bed; underwater is
a water bed (wrong here); cave_drips is a cave bed;
city_night, thang_long_crowd and rift are wrong for this
setting.

The two VO takes (CP17, measured from real bytes):
  S02 Co Vo Tuong "Ta khong con chap nhan phan ta khong biet."
      2.880 s, window 6.5-11.5 s, FITS by +2.120 s (runs
      6.5-9.380 s, ends 2.120 s BEFORE the window end and 8.620 s
      before the 18.00 s scene end). No overrun, no tail trim.
      (33 characters, 6.60 characters per second on the 5 s
      window -- the take duration is measured from real bytes,
      CP17: 2.880 s, windowFit FITS, not sped up.)
  S03 PLAYER "O Sa Hoa ong da cho nuoc. O noi khac, nguoi ta
      khong duoc hoi vi sao nuoc mat." 5.280 s, window
      12.5-17.5 s, OVERRUNS by +0.280 s (runs 12.5-17.780 s,
      ends 0.280 s AFTER the window end but 0.220 s BEFORE the
      18.00 s scene end). The overrun is KEPT, not trimmed and
      not sped up, per the owner verdict on the three campaign
      overruns (CIN_005_S03 +0.160 s, CIN_018_S03 +0.280 s,
      CIN_006_S03 +0.520 s -- windows stay as-is, the decision
      is Codex's at PR review). No tail trim at the scene edge.
      (70 characters, 14.00 characters per second on the 5 s
      window -- CP17: 5.280 s, windowFit OVERRUN.)
The S03 take is a VOICE_PLACEHOLDER_ONLY take (CP17): VOICE_GUIDE
assigns the player no spoken voice or gender; the take exists
to time the line, and the director must replace it with a cast
voice or drop the spoken line. It is mixed in as delivered so
the timing can be heard, not as a casting decision.

Stinger placement (deviation from the recipe, stated plainly):
the recipe places reveal at 6.0 s (S02 start), as in all
fourteen earlier scene mixes. Here the reveal cue is 3.000 s
long, so at 6.0 s it would run 6.0-9.0 s and sit under 2.5 s
of the 2.880 s S02 line (6.5-9.380 s) -- the scene's key
refusal line, spoken on screen by Co Vo Tuong. The stinger
is therefore placed at 0.0 s (S01 start -- the memory's opening
reveal: the drought field, the sealed petition, the measuring
post), running 0.0-3.0 s, clear of both VO windows. Placement
is PROPOSED pending picture lock; the director may move it to
6.0 s (sting under the line) or to 12.0 s (S03 start).

Staging notes (NOT mix defects, final-picture/character-lock
matters; the mix does not move the VO):
- S02: the speaker IS identifiable -- the timing manifest
  marks the S02 dialogue onscreen: true for Co Vo Tuong
  (NPC_CO_VO_TUONG), and the S02 keyframe shows him at his
  desk, face visible. Two recorded keyframe defects touch this
  shot: it is a medium shot instead of the detail close view
  the timing calls MEMORY_DETAIL, and his hair differs from
  S01's although both shots are the same memory period.
- S03: the PLAYER speaks and the timing manifest marks the
  S03 dialogue onscreen: null, so the line is delivered
  off-screen, like Ly An's voice in CIN_004 (DEC-MEDIA-P0 Q2).
  The S03 keyframe shows the masked hooded figure beside the
  copper water-machine -- that figure is NOT identified as the
  speaker, and the keyframe defects record that its porcelain
  mask covers the full face instead of the specified cracked
  half mask, and its copper machinery spans the whole torso,
  reading more automaton than a man wearing a chest core and
  back brace.
- S01: the petition renders as a modern wax-sealed envelope
  rather than a folded petition sheet (recorded keyframe
  defect); the two men in the drought field are the scene's
  memory of who gave water at Sa Hoa.

Ducking finding (measured, not a defect): the ducking depth is
measured from real bytes over each full VO window (CP39 method,
same params as every scene mix); sa_hoa was NOT silent inside
CIN_010's window (measured cut -7.94 dB there), so a real cut
is expected in both windows here too, and the numbers in the
manifest are the measured ones, not targets. If either depth
came out 0.0 dB it would mean the cue is silent in that window
-- that is NOT the case for sa_hoa (unlike quiet_discovery in
CIN_016, which is digitally silent 12-15 s); a 0.0 dB reading
here would be investigated, not reported as a silence pocket.

Outputs land in Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1/: one WAV
(48 kHz stereo pcm_s16le) + CIN018_MIX_V1_manifest_v1.json.
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

MUSIC_CUE = "MUSIC/sa_hoa"
AMB_CUE = "AMBIENCE/desert_wind"
STINGER_CUE = "SFX/CINEMA/reveal"
STEM_FILES = {
    MUSIC_CUE: "ClientGodot/assets/audio/composed/music/sa_hoa.ogg",
    AMB_CUE: "ClientGodot/assets/audio/composed/ambience/desert_wind.ogg",
    STINGER_CUE: "ClientGodot/assets/audio/composed/cinema/reveal.ogg",
}
PROVENANCE = {
    MUSIC_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
    AMB_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 30)",
    STINGER_CUE: "ORIGINAL_COMPOSED_BY_MUSE (checkpoint 26)",
}
# Pack-table LUFS (CP26 music/stingers, CP30 ambience); re-measured
# this run before mixing and asserted to match within 0.05 LUFS.
# sa_hoa / desert_wind values are the CIN_010 mix's pack values
# (same composed cues, same pack tables).
PACK_LUFS = {MUSIC_CUE: -21.96, AMB_CUE: -29.93, STINGER_CUE: -24.96}

# Two dialogue windows -- the only campaign scene with two cues.
# Each entry: shot, speaker, source take, window start, window end.
VO_TAKES = [
    {"shotId": "CIN_018_S02", "speaker": "NPC_CO_VO_TUONG",
     "speakerDisplay": "Cơ Vô Tướng",
     "src": "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/VO_CIN_018_S02_COVOTUONG_draft_v1.wav",
     "at": 6.5, "winEnd": 11.5},
    {"shotId": "CIN_018_S03", "speaker": "PLAYER",
     "speakerDisplay": "Người chơi",
     "src": "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/VO_CIN_018_S03_PLAYER_draft_v1.wav",
     "at": 12.5, "winEnd": 17.5},
]
# Primary VO for the manifest's single-take "vo" field: the S03 take
# (the scene's uniform-window dialogue, as in every earlier mix).
PRIMARY_VO_INDEX = 1
STINGER_AT = 0.0


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


def combine(parts: list, total: float, work: Path, name: str) -> Path:
    """Sum N placed buses (no gain change) into one bus."""
    out = work / f"{name}.wav"
    inputs = []
    for p in parts:
        inputs += ["-i", str(p)]
    filt = ("".join(f"[{i}:a]" for i in range(len(parts)))
            + f"amix=inputs={len(parts)}:normalize=0:dropout_transition=0,"
            f"atrim=0:{fmt_t(total)}[a]")
    run(["ffmpeg", "-y", "-v", "error", *inputs,
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
    out_dir = root / "Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V1"
    out_dir.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix="cin018_mix_"))

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

    # Both VO takes: probe duration, re-measure loudness, place at
    # their window starts, then combine into ONE sidechain key bus.
    vo_records = []
    placed = []
    for i, vt in enumerate(VO_TAKES):
        vo_path = root / vt["src"]
        vo_take = probe(vo_path)
        vo_dur = float(vo_take["format"]["duration"])
        vo_ln = loudnorm(vo_path)
        vo_end = vt["at"] + vo_dur
        tail_trim = round(max(0.0, vo_end - TOTAL), 3)
        win = (vt["at"], round(min(vo_end, TOTAL), 3))
        overrun = round(vo_end - vt["winEnd"], 3)
        placed.append(place(vo_path, vt["at"], TOTAL, work,
                            f"vo_{i}", mono_to_stereo=True))
        vo_records.append({
            "shotId": vt["shotId"],
            "speaker": vt["speaker"],
            "speakerDisplay": vt["speakerDisplay"],
            "take": vo_path.name,
            "windowSeconds": list(win),
            "windowEndSeconds": vt["winEnd"],
            "takeDurationSeconds": vo_dur,
            "takeEndSeconds": round(vo_end, 3),
            "tailTrimmedAtSceneEdgeSeconds": tail_trim,
            "overrunVsWindowSeconds": overrun,
            "fit": ("FITS" if overrun <= 0 else
                    "OVERRUN_KEPT_PER_OWNER_VERDICT"),
            "measuredLUFS": float(vo_ln["input_i"]),
            "measuredTruePeakDBTP": float(vo_ln["input_tp"]),
            "gainDb": 0.0,
        })
        print(f"VO {vt['shotId']}: take {vo_dur:.3f}s at {vt['at']}s, "
              f"ends {vo_end:.3f}s, overrun {overrun:+.3f}s, "
              f"LUFS {vo_ln['input_i']} TP {vo_ln['input_tp']}")
    vo_bus = combine(placed, TOTAL, work, "vo_bus")
    # Primary VO (S03) for the manifest's single-take "vo" field,
    # keeping the shape every earlier scene mix uses.
    vo = dict(vo_records[PRIMARY_VO_INDEX])
    wins = [(r["windowSeconds"][0], r["windowSeconds"][1])
            for r in vo_records]

    stem_records = []
    loop_records = []

    # Music bus (ducked by the combined VO bus)
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
                           work, "amb_desert_wind")
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

    # Stinger (PROPOSED placement at S01 start -- see docstring:
    # the recipe's 6.0 s would sit under the S02 dialogue).
    st = place(root / STEM_FILES[STINGER_CUE], STINGER_AT, TOTAL, work,
               "stinger")
    stinger_record = {
        "cue": STINGER_CUE, "source": STEM_FILES[STINGER_CUE],
        "provenance": PROVENANCE[STINGER_CUE],
        "atSeconds": STINGER_AT, "gainDb": 0.0,
        "packMeasuredLUFS": PACK_LUFS[STINGER_CUE],
        "remeasuredLUFS": measured[STINGER_CUE],
        "placementStatus": "PROPOSED_PENDING_PICTURE_LOCK",
        "placementNote": ("Deviation from the recipe's 6.0 s (S02 "
                          "start): the reveal cue is 3.000 s long, "
                          "so at 6.0 s it would run 6.0-9.0 s and "
                          "sit under 2.5 s of the 2.880 s S02 line "
                          "(6.5-9.380 s). Placed at 0.0 s (S01 "
                          "start, the memory's opening reveal), "
                          "running 0.0-3.0 s, clear of both VO "
                          "windows. Director may move it to 6.0 s."),
    }
    stem_records.append({**stinger_record, "role": "stinger"})

    # Ducking evidence (music bus, each FULL VO window vs a 2 s
    # reference before it). The CP39 full-window method is retained
    # per window so each depth is comparable with the single-window
    # mixes (a 2 s slice can understate the cut on cues whose
    # window opening is quiet). References: S02 [4.0, 6.0],
    # S03 [10.0, 12.0] -- both clear of any VO (S02 take ends
    # 9.380 s; the compressor release is 350 ms).
    duck_evidence = []
    for (w0, w1), rec in zip(wins, vo_records):
        ref_start = max(0.0, w0 - 2.5)
        win_dur = w1 - w0
        in_raw = segment_rms_db(music_raw, w0, win_dur)
        in_duck = segment_rms_db(music_ducked, w0, win_dur)
        out_raw = segment_rms_db(music_raw, ref_start, 2.0)
        out_duck = segment_rms_db(music_ducked, ref_start, 2.0)
        duck_evidence.append({
            "bus": "music",
            "shotId": rec["shotId"],
            "windowSeconds": [w0, w1],
            "referenceSeconds": [ref_start, ref_start + 2.0],
            "depthInWindowDb": round(in_duck - in_raw, 2),
            "depthOutsideWindowDb": round(out_duck - out_raw, 2),
        })

    parts = [vo_bus, music_ducked, amb_bus, st]
    tmp_mix = work / "mix_untrimmed.wav"
    mixdown(parts, TOTAL, tmp_mix)
    ln = loudnorm(tmp_mix)
    tp = float(ln["input_tp"])
    trim = round(tp - PEAK_CEILING_DBTP, 2) if tp > PEAK_CEILING_DBTP else 0.0
    mix_path = out_dir / "CIN_018_mix_draft_v1.wav"
    mixdown(parts, TOTAL, mix_path, trim_db=trim)
    ln = loudnorm(mix_path)
    p = probe(mix_path)
    dur = float(p["format"]["duration"])
    if abs(dur - TOTAL) > 0.05:
        print(f"CIN_018: MIX DURATION {dur} != {TOTAL}", file=sys.stderr)
        sys.exit(1)
    print(f"CIN_018: mix {dur:.3f}s LUFS {ln['input_i']} "
          f"TP {ln['input_tp']} (peak trim {trim:.2f} dB), "
          f"ducking music {[e['depthInWindowDb'] for e in duck_evidence]} dB, "
          f"VO tail trimmed {[r['tailTrimmedAtSceneEdgeSeconds'] for r in vo_records]} s")

    manifest = {
        "checkpoint": "MEDIA-02 checkpoint 52 - CIN_018 draft mix v1 (fifteenth scene mix after CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, CIN_016 v1 and CIN_017 v1, same recipe as P0 v3)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "status": "DRAFT_MIX_NOT_FINAL",
        "mixVersion": "v1_cin018_proposed",
        "mixVerdict": ("DRAFT_MIX_FOR_REVIEW: fifteenth scene mix after "
                       "CIN_006 v1, CIN_003 v1, CIN_005 v1, CIN_007 v1, "
                       "CIN_008 v1, CIN_009 v1, CIN_010 v1, CIN_011 v1, "
                       "CIN_012 v1, CIN_013 v1, CIN_014 v1, CIN_015 v1, "
                       "CIN_016 v1 and CIN_017 v1, built with the P0 v3 "
                       "recipe (same gain targets, ducking params, peak "
                       "guard, loop joins). Stem assignment is NEW and "
                       "PROPOSED_CANDIDATE (the CP02 stem table assigns "
                       "nothing to CIN_018; the scene timing manifest "
                       "lists only the reveal stinger as a candidate "
                       "stem). This is the ONLY campaign scene with TWO "
                       "dialogue windows: the S02 take FITS its window "
                       "(2.880 s, 6.5-9.380 s) by 2.120 s and the S03 "
                       "take OVERRUNS its window by 0.280 s (5.280 s, "
                       "12.5-17.780 s) -- the overrun is KEPT per the "
                       "owner verdict on the three campaign overruns, "
                       "not trimmed, not sped up. NOT a mix PASS: no "
                       "ear audition, stem table not locked, stinger "
                       "placement PROPOSED pending picture lock "
                       "(placed at 0.0 s, not the recipe's 6.0 s, so "
                       "it does not sit under the S02 dialogue). "
                       "Adoption is Codex's adapter decision."),
        "stemAssignment": {
            "status": "PROPOSED_CANDIDATE_NEW",
            "source": ("No CP02 assignment exists for CIN_018; "
                       "sa_hoa music + desert_wind ambience are the "
                       "desert cues (composed, CP26/CP30) for this "
                       "scene (S01: cracked drought field, a man "
                       "pouring the last water from a gourd into a "
                       "cup, a sealed petition letter and a measuring "
                       "post, MEMORY_MEDIUM; S02: Co Vo Tuong at his "
                       "desk with scrolls and seal, MEMORY_DETAIL; "
                       "S03: the masked hooded figure beside the "
                       "copper water-machine at night, MEDIUM_STATIC; "
                       "keyframes CIN_018 S01/S02/S03). "
                       "sa_hoa is the composed set's desert form "
                       "('Sa Hoa -- Lo va cat': kiln and sand, A "
                       "minor pentatonic, dry bright plucks, 110 "
                       "BPM) -- the setting-exact cue for a drought "
                       "scene built around the lack of water, for "
                       "the confrontation about who gave water at "
                       "Sa Hoa and who was never asked why water "
                       "vanished elsewhere. It was used before in "
                       "scene mix CIN_010 (the ash-gold caravan "
                       "rest); this is its second scene-mix use, "
                       "same pairing as CIN_010, stated plainly "
                       "because the two scenes share the Sa Hoa / "
                       "desert setting and the cue set has a single "
                       "desert form. desert_wind is the desert wind "
                       "bed for the dry field and the night bamboo "
                       "of all three shots; also second scene-mix "
                       "use (CIN_010). "
                       "ben_mua was passed over: the rain-quay "
                       "leitmotif, wrong setting for a drought "
                       "scene about water that is NOT there. "
                       "thang_long is the capital-city form (wrong "
                       "setting); tran_son ('Tran Son — Nguoi qua "
                       "cua', the bell-led gate form) was passed "
                       "over: already used for CIN_008 and CIN_012. "
                       "lam_trieu was passed over: the pastoral "
                       "flute, used for CIN_013. quiet_discovery "
                       "was passed over: the exploration silence, "
                       "used for CIN_007/CIN_011/CIN_016 -- wrong "
                       "for a confrontation scene. bach_uyen was "
                       "passed over: the underwater low-passed "
                       "form, used for CIN_015/CIN_017 -- the "
                       "opposite of this scene (water present "
                       "there, water withheld here). rift_finale "
                       "is the set's only full close (finale "
                       "material, wrong for a mid-campaign chapter "
                       "beat); boss_mang_cot is boss material for "
                       "the WRONG boss (Mang Cot, not Co Vo "
                       "Tuong) -- and this beat is a quiet "
                       "confrontation, not a boss fight. "
                       "river_shore was passed over: a water-edge "
                       "bed, used for CIN_003 and CIN_008 -- the "
                       "S01 field is cracked dry earth, not a "
                       "shore. rain_light and rain_heavy are rain "
                       "beds, but no rain is depicted in any of "
                       "the three keyframes (drought field, desk "
                       "interior, night yard -- no rain streaks); "
                       "mountain_wind was used for CIN_013, forge "
                       "for CIN_012, waterfall for CIN_009; "
                       "wind_canopy is a forest bed, underwater a "
                       "water bed (wrong here), cave_drips a cave "
                       "bed; city_night, thang_long_crowd and rift "
                       "are wrong for this setting. "
                       "The reveal stinger is the scene's only "
                       "manifest-listed candidate stem "
                       "(CIN_018_timing_v1.json)."),
            "alternateTakeExcluded": "N/A: CIN_018 has no alternate take.",
        },
        "gainStaging": {
            "vo": "unity (anchor; takes as delivered)",
            "musicTargetLUFS": MUSIC_TARGET_LUFS,
            "ambiencePrimaryTargetLUFS": AMB_PRIMARY_LUFS,
            "stingers": "unity",
            "peakCeilingDBTP": PEAK_CEILING_DBTP,
        },
        "notes": [
            "VO windows 6.5-11.5 s (S02) and 12.5-17.5 s (S03) are "
            "PROPOSED_ANIMATIC_PLACEMENT (only CIN_001_S05 is "
            "DECIDED); all 21 windows are approved for DRAFT VO per "
            "Goi 30 D1. Neither window was widened.",
            "VO take S02 runs 6.5-9.380 s: 2.880 s, ending 2.120 s "
            "BEFORE the 11.5 s window end -- the take FITS inside "
            "its window by 2120 ms (no overrun). The take ends "
            "8.620 s before the 18.00 s scene end, so no tail trim "
            "at the scene edge. The window, the take and the timing "
            "are unchanged.",
            "VO take S03 runs 12.5-17.780 s: 5.280 s, ending 0.280 s "
            "AFTER the 17.5 s window end but 0.220 s BEFORE the "
            "18.00 s scene end -- the overrun is KEPT, not trimmed "
            "and not sped up, per the owner verdict on the three "
            "campaign overruns (CIN_005_S03 +0.160 s, CIN_018_S03 "
            "+0.280 s, CIN_006_S03 +0.520 s -- windows stay as-is, "
            "the decision is Codex's at PR review). No tail trim "
            "at the scene edge. The window, the take and the timing "
            "are unchanged.",
            "The S03 take is VOICE_PLACEHOLDER_ONLY (CP17): "
            "VOICE_GUIDE assigns the player no spoken voice or "
            "gender; the take exists to time the line, and the "
            "director must replace it with a cast voice or drop "
            "the spoken line. It is mixed in as delivered so the "
            "timing can be heard, not as a casting decision.",
            "The CP17 VO takes measure -23.77 LUFS (S02) and "
            "-22.54 LUFS (S03) per checkpoint 17 (re-measured from "
            "real bytes this run, recorded per take in the voices "
            "list). VO is kept at unity per the recipe, not "
            "normalized.",
            "Staging: the S02 speaker IS identifiable -- the timing "
            "manifest marks the S02 dialogue onscreen: true for Co "
            "Vo Tuong (NPC_CO_VO_TUONG), and the S02 keyframe shows "
            "him at his desk, face visible. Two recorded keyframe "
            "defects touch this shot: it is a medium shot instead "
            "of the detail close view the timing calls "
            "MEMORY_DETAIL, and his hair differs from S01's "
            "although both shots are the same memory period. The "
            "S03 speaker is NOT identifiable in the picture -- the "
            "timing manifest marks the S03 dialogue onscreen: null "
            "for the PLAYER, so the line is delivered off-screen, "
            "like Ly An's voice in CIN_004 (DEC-MEDIA-P0 Q2); the "
            "S03 keyframe shows the masked hooded figure beside "
            "the copper water-machine, but that figure is NOT "
            "identified as the speaker, and the keyframe defects "
            "record that its porcelain mask covers the full face "
            "instead of the specified cracked half mask, and its "
            "copper machinery spans the whole torso, reading more "
            "automaton than a man wearing a chest core and back "
            "brace. S01's petition renders as a modern wax-sealed "
            "envelope rather than a folded petition sheet. All of "
            "these are final-picture/character-lock matters, not "
            "mix defects; the mix does not move the VO.",
            "Ducking depth is measured on the ducked bus against its "
            "unducked render (RMS over each full VO window vs a 2 s "
            "reference before the window). The full-window method "
            "from checkpoint 39 is retained per window so each depth "
            "is comparable across the CIN_003/CIN_005/CIN_007/CIN_008/ "
            "CIN_009/CIN_010/CIN_011/CIN_012/CIN_013/CIN_014/CIN_015/CIN_016/CIN_017/CIN_018 mixes (a 2 s slice can understate "
            "the cut on cues whose window opening is quiet). The "
            "two windows are ducked through ONE combined VO bus, "
            "so the music recovers in the 3.12 s gap between the "
            "takes (9.38-12.5 s; compressor release 350 ms).",
            "Ducking depth is measured from real bytes over each "
            "full VO window (CP39 method, same params as every "
            "scene mix); sa_hoa was NOT silent inside CIN_010's "
            "window (measured cut -7.94 dB there), so a real cut "
            "is expected in both windows here too, and the numbers "
            "in the manifest are the measured ones, not targets. "
            "If either depth came out 0.0 dB it would mean the cue "
            "is silent in that window -- that is NOT the case for "
            "sa_hoa (unlike quiet_discovery in CIN_016, which is "
            "digitally silent 12-15 s); a 0.0 dB reading here would "
            "be investigated, not reported as a silence pocket.",
            "Ambience loop join uses a 1 s acrossfade; loopQA reports "
            "the max sample jump at the join against the bed's own "
            "99.9th-percentile jump.",
            "Stinger placement at 0.0 s (S01 start) is PROPOSED pending "
            "picture lock. It is a deviation from the recipe's 6.0 s "
            "(S02 start): the reveal cue is 3.000 s long, so at 6.0 s "
            "it would run 6.0-9.0 s and sit under 2.5 s of the "
            "2.880 s S02 line (6.5-9.380 s) -- the scene's key "
            "refusal line, spoken on screen. At 0.0 s it runs "
            "0.0-3.0 s, clear of both VO windows. The director may "
            "move it to 6.0 s (sting under the line) or 12.0 s "
            "(S03 start).",
        ],
        "scenes": [{
            "sceneId": "CIN_018",
            "seconds": TOTAL,
            "vo": vo,
            "voices": vo_records,
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
    (out_dir / "CIN018_MIX_V1_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print("OK: CIN018_MIX_V1_manifest_v1.json written")


if __name__ == "__main__":
    main()
