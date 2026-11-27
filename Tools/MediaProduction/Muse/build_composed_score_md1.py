#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 1: whole-game score, batch 1.

Work Order 37 module M-D asks for the score across every biome /
chapter / activity / boss / ending "theo Audio Direction", keeping the
one leitmotif system but with arrangement / instrumentation / density /
rhythm / space that is functional per scene -- "khong chi doi pitch /
tempo mot loop de du so cue". This checkpoint closes the coverage gaps:

  M-D slots (15): hub, explore, Ben Mua, Thanh Lac, Thang Long, rain,
  swamp, forest, mountain, desert, dungeon, boss, arena, tragedy,
  resolution.

  Checkpoint 26 already composed 9 music cues covering 8 slots
  (ben_mua, thang_long, boss_mang_cot, quiet_discovery, lam_trieu,
  sa_hoa, tran_son, rift_finale) plus bach_uyen (underwater city,
  outside the M-D slot list). 7 slots had NO music cue at all --
  hub, Thanh Lac, rain, swamp, dungeon, arena, tragedy -- and the
  score had no transitions between states.

  This checkpoint composes those 7 missing cues + 3 transition
  bridges (calm->danger, danger->calm, area->area), all ORIGINAL
  procedural synthesis from the same leitmotif system (D major
  pentatonic question phrase hanging on scale degree 2; the full
  flute tail stays reserved for the resolve stinger and rift_finale
  -- a low pluck tail, as thang_long already does, is the quiet
  answer a home/street cue may give). No external samples, no ported
  bytes, no voices. The 541 ported PackV1 files are untouched and are
  NOT counted as new audio.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/music/<stem>.wav     (master, 48k/24b)
  Art_Source/Audio/Muse/COMPOSED/transitions/<stem>.wav (master, 48k/24b)
  ClientGodot/assets/audio/composed/music/<stem>.ogg   (runtime)
  ClientGodot/assets/audio/composed/transitions/<stem>.ogg (runtime)
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD1_pack_v1.json
  Implementation/Content/Audio/Deliveries/MUSIC_SCORE_MD_COVERAGE_v1.json

Loudness is measured from the real rendered bytes with ffmpeg
loudnorm (the checkpoint 07 / 26 method); music targets -22 LUFS,
transitions -25 LUFS. Loops use the same disclosed construction as
checkpoint 26 (1.5 s tail wrap + 0.25 s end-landing blend); seam
numbers are recorded indicators, never claimed as a PASS.
"""
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

TOOLS_DIR = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[3]
SR = 48000
MASTER_DIR = ROOT / "Art_Source/Audio/Muse/COMPOSED"
RUNTIME_DIR = ROOT / "ClientGodot/assets/audio/composed"
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD1_pack_v1.json")
COVERAGE = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_SCORE_MD_COVERAGE_v1.json")
TMP = Path("/tmp/composed_score_md1")
TMP.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location(
    "build_composed_music", TOOLS_DIR / "build_composed_music.py")
cm = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cm)

# Re-export the synth primitives (the engine lives in checkpoint 26).
new_track = cm.new_track
play = cm.play
melody = cm.melody
chord = cm.chord
bass_line = cm.bass_line
drops = cm.drops
add = cm.add
drum = cm.drum
shaker = cm.shaker
noise_sw = cm.noise_sw
beat_s = cm.beat_s
lowpass = cm.lowpass
room = cm.room
tail_wrap = cm.tail_wrap
end_landing = cm.end_landing
gain_stage = cm.gain_stage
write_master_wav = cm.write_master_wav
encode_ogg = cm.encode_ogg
file_entry = cm.file_entry
seam_stats = cm.seam_stats

D4, E4, FS4, A4, B4 = 62, 64, 66, 69, 71
D5, E5, FS5, A5, B5, D6 = 74, 76, 78, 81, 83, 86
MOTIF_Q = cm.MOTIF_Q
MOTIF_TAIL = cm.MOTIF_TAIL
MOTIF_HEAD = cm.MOTIF_HEAD
CH = cm.CH

RENDERING = ("procedural synthesis (additive pluck/flute/bell/pad/bass "
             "+ noise percussion), authored in "
             "build_composed_score_md1.py on the checkpoint-26 engine "
             "(build_composed_music.py); no external samples")
MOTIF_NOTE = ("Ben Mua leitmotif: D major pentatonic question phrase "
              "hanging on scale degree 2; tail withheld unless the "
              "structure says otherwise")


# ------------------------------------------------------------- pieces
def piece_hub(tr, bpm):
    """Lac Chau hub: warm, safe, unhurried. Flute states the question
    twice; a low pluck answers with the tail at bars 10-11 (the quiet
    answer a home may give -- the thang_long precedent); the final bar
    rests on a soft D bell over the tonic pad."""
    prog = ["D", "G", "D", "Bm", "Em", "G", "D", "A",
            "D", "G", "D", "Bm", "Em", "A", "D", "D"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.32)
        play(tr, "bell", CH[c][0] + 24, bar * 4 * b, 2.8 * b, 0.14,
             pan=-0.25 if bar % 2 else 0.25)
    bass_line(tr, [38, 43, 38, 35, 40, 43, 38, 33,
                   38, 43, 38, 35, 40, 33, 38, 38], bpm, 0.45,
              pattern=(0, 2))
    melody(tr, "flute", MOTIF_Q, bpm, 0, 0.8)
    melody(tr, "pluck", [(be, m - 12, ln) for be, m, ln in MOTIF_Q],
           bpm, 4, 0.5, pan=0.2)
    melody(tr, "flute", MOTIF_Q, bpm, 8, 0.78, pan=-0.1)
    melody(tr, "pluck", MOTIF_TAIL, bpm, 10, 0.5, pan=-0.2)
    melody(tr, "flute", [(0, D5, 2), (2, A5, 1), (3, FS5, 1)], bpm, 14,
           0.7)
    play(tr, "bell", D5, 15 * 4 * b, 3.5 * b, 0.22)
    drops(tr, [6.1, 19.4, 33.7], 0.05)


def piece_thanh_lac(tr, bpm):
    """Thanh Lac morning market: the busiest street form. Pluck
    arpeggios every bar, a second pluck voice answering off-beat,
    bells on the bar line, shaker on offbeats; flute motif at bars 0
    and 8, low pluck tail at bar 12."""
    prog = ["D", "G", "D", "A", "Bm", "G", "D", "A",
            "D", "G", "Bm", "A", "D", "G", "A", "D"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.28)
        play(tr, "bell", CH[c][0] + 24, bar * 4 * b, 2.2 * b, 0.18,
             pan=-0.3 if bar % 2 else 0.3)
    bass_line(tr, [38, 43, 38, 33, 35, 43, 38, 33,
                   38, 43, 35, 33, 38, 43, 33, 38], bpm, 0.5,
              pattern=(0, 1, 2, 3))
    arp = [(0, 0, 0.5), (0.5, 1, 0.5), (1, 2, 0.5), (1.5, 1, 0.5),
           (2, 0, 0.5), (2.5, 1, 0.5), (3, 2, 0.5), (3.5, 1, 0.5)]
    scale = [D5, FS5, A5, B5, D6]
    for bar in range(16):
        ev = [(bt, scale[(i + bar) % len(scale)], ln) for bt, i, ln in arp]
        melody(tr, "pluck", ev, bpm, bar, 0.32, pan=0.15)
        # Second pluck voice, off-beat, an octave down.
        ev2 = [(bt + 0.25, scale[(i + bar + 2) % len(scale)] - 12, ln)
               for bt, i, ln in arp[::2]]
        melody(tr, "pluck", ev2, bpm, bar, 0.22, pan=-0.25)
    melody(tr, "flute", MOTIF_Q, bpm, 0, 0.75)
    melody(tr, "flute", MOTIF_Q, bpm, 8, 0.75)
    melody(tr, "pluck", MOTIF_TAIL, bpm, 12, 0.5, pan=-0.2)
    for bar in range(16):
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.08), bar * 4 * b + bt * b,
                -0.4 if bar % 2 else 0.4, 0.05)


def piece_rain(tr, bpm):
    """Rain: a veil over the theme. Sparse flute fragments (head at
    bar 0, second half at bar 8), long pads, frequent drops; the whole
    mix is low-passed so the rain ambience can sit on top without a
    fight. Ends on the hanging E."""
    prog = ["D", "D", "Bm", "D", "G", "D", "Bm", "G",
            "D", "D", "Bm", "Em", "G", "A", "D", "D"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.34)
    bass_line(tr, [38, 38, 35, 38, 43, 38, 35, 43,
                   38, 38, 35, 40, 43, 33, 38, 38], bpm, 0.4,
              pattern=(0,))
    melody(tr, "flute", MOTIF_HEAD, bpm, 0, 0.6)
    play(tr, "bell", A4, 4 * 4 * b, 5 * b, 0.15, pan=-0.3)
    melody(tr, "flute", [(0, A5, 1), (1, FS5, 1), (2, E5, 2)], bpm, 8,
           0.55)
    play(tr, "bell", D5, 12 * 4 * b, 6 * b, 0.13)
    melody(tr, "pluck", [(0, D5, 1), (1, FS5, 1)], bpm, 13, 0.3,
           pan=0.2)
    play(tr, "flute", E5, 15 * 4 * b, 3 * b, 0.5)  # still hanging
    drops(tr, [2.2, 5.8, 9.1, 12.6, 16.9, 21.3, 25.7, 29.4, 34.8,
               39.2, 43.6, 48.1, 52.5, 56.0], 0.09)
    add(tr, noise_sw(12.0), 20.0, 0.0, 0.012)
    add(tr, noise_sw(12.0), 40.0, 0.0, 0.012)


def piece_swamp(tr, bpm):
    """Swamp (dam): standing water. The motif an octave down, half
    density, over Bm/Em pads and a low drone; slow deep drops, one low
    bell per phrase. No drums -- nothing hurries here."""
    prog = ["Bm", "Bm", "Em", "Bm", "G", "Em", "Bm", "Em",
            "Bm", "G", "Em", "Bm", "Em", "Bm", "Bm", "Bm"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.36)
    bass_line(tr, [35, 35, 40, 35, 43, 40, 35, 40,
                   35, 43, 40, 35, 40, 35, 35, 35], bpm, 0.55,
              pattern=(0, 2))
    low_q = [(be, m - 12, ln) for be, m, ln in MOTIF_Q]
    melody(tr, "flute", low_q, bpm, 1, 0.55)
    melody(tr, "flute", low_q, bpm, 9, 0.5, pan=0.15)
    play(tr, "bass", 23, 0.0, 8 * b, 0.5)  # B0 standing drone
    play(tr, "bell", D4, 5 * 4 * b, 6 * b, 0.18)
    play(tr, "bell", A4, 12 * 4 * b, 6 * b, 0.14, pan=-0.2)
    melody(tr, "pluck", [(0, D4, 1), (2, A4, 2)], bpm, 6, 0.4,
           pan=0.25, bright=0.5)
    play(tr, "flute", E4, 15 * 4 * b, 3 * b, 0.45)  # hanging, low
    drops(tr, [7.9, 15.2, 24.6, 31.8, 40.5, 49.3, 58.7], 0.07)


def piece_dungeon(tr, bpm):
    """Dungeon (ham): cold stone. D-minor fragments in low pluck,
    soft drum on the bar line, D1 drone, cold bell marks; the motif
    never completes -- the hanging E is the only high note, once."""
    prog = ["Dm", "Dm", "F", "Dm", "C", "Dm", "Gm", "Dm",
            "F", "Dm", "Gm", "Dm"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.30)
    for bar in range(12):
        add(tr, drum(), bar * 4 * b, 0.0, 0.15)
        play(tr, "bass", 26, bar * 4 * b, 3.4 * b, 0.5)
    frag = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]
    for bar in (1, 5, 9):
        melody(tr, "pluck", frag, bpm, bar, 0.6, pan=-0.15, bright=0.4)
    melody(tr, "pluck", [(0, A4, 1), (1, 65, 1), (2, E4, 2)], bpm, 7,
           0.55, pan=0.2, bright=0.4)
    play(tr, "bell", D4, 4 * 4 * b, 5 * b, 0.16)
    play(tr, "bell", 65, 8 * 4 * b, 5 * b, 0.15,  # F4, cold mark
         pan=-0.2)
    play(tr, "flute", E5, 11 * 4 * b, 3 * b, 0.4)  # hanging, once
    drops(tr, [11.3, 29.8], 0.05)


def piece_arena(tr, bpm):
    """Arena (dau truong): drum-led drive. Drum every beat plus an
    offbeat hit, pluck ostinato in eighth notes, motif stated in
    bright pluck at bars 0 and 8, bell hits on the bar line. The one
    cue that lands: drum + bell D close the loop."""
    prog = ["D", "D", "A", "D", "Bm", "D", "A", "D",
            "D", "D", "A", "Bm", "G", "A", "D", "D"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.26)
        play(tr, "bell", CH[c][0] + 24, bar * 4 * b, 1.6 * b, 0.2,
             pan=0.3 if bar % 2 else -0.3)
    bass_line(tr, [38, 38, 33, 38, 35, 38, 33, 38,
                   38, 38, 33, 35, 43, 33, 38, 38], bpm, 0.6,
              pattern=(0, 1, 2, 3))
    for bar in range(16):
        add(tr, drum(), bar * 4 * b, 0.0, 0.30)
        add(tr, drum(), bar * 4 * b + 2 * b, 0.0, 0.20)
        add(tr, shaker(0.06), bar * 4 * b + 1 * b, 0.3, 0.05)
        add(tr, shaker(0.06), bar * 4 * b + 3 * b, -0.3, 0.05)
    ost = [(0, D5, 0.5), (0.5, A5, 0.5), (1, FS5, 0.5), (1.5, A5, 0.5),
           (2, D5, 0.5), (2.5, B5, 0.5), (3, A5, 0.5), (3.5, FS5, 0.5)]
    for bar in range(16):
        melody(tr, "pluck", ost, bpm, bar, 0.30, pan=-0.1, bright=1.2)
    melody(tr, "pluck", MOTIF_Q, bpm, 0, 0.55, bright=1.2)
    melody(tr, "pluck", MOTIF_Q, bpm, 8, 0.55, bright=1.2, pan=0.1)
    melody(tr, "flute", MOTIF_HEAD, bpm, 12, 0.6, pan=-0.15)
    add(tr, drum(), 15 * 4 * b, 0.0, 0.35)
    play(tr, "bell", D6, 15 * 4 * b, 3.0 * b, 0.25)


def piece_tragedy(tr, bpm):
    """Tragedy (bi kich): a broken string. Slow D minor, solo flute
    fragments with long silences between them, single bells, one low
    pluck figure; no drums, no tail -- the last note is the hanging E
    alone over a Dm pad."""
    prog = ["Dm", "Dm", "Gm", "Dm", "F", "Dm", "Gm", "Dm",
            "C", "Dm", "Gm", "Dm"]
    b = beat_s(bpm)
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * b, 4 * b, 0.34)
    bass_line(tr, [38, 38, 43, 38, 41, 38, 43, 38,
                   36, 38, 43, 38], bpm, 0.4, pattern=(0,))
    melody(tr, "flute", [(0, D5, 1), (1, 65, 1), (2, A4, 2)], bpm, 0,
           0.6)
    play(tr, "bell", A4, 3 * 4 * b, 6 * b, 0.16, pan=-0.3)
    melody(tr, "flute", [(0, A4, 1), (1, 65, 1), (2, E4, 2)], bpm, 5,
           0.55, pan=0.15)
    play(tr, "bell", D5, 7 * 4 * b, 6 * b, 0.14)
    melody(tr, "pluck", [(0, D4, 1), (2, A4, 2)], bpm, 9, 0.4,
           pan=0.25, bright=0.5)
    play(tr, "flute", E5, 11 * 4 * b, 3.5 * b, 0.5)  # hanging, alone
    play(tr, "bell", D4, 11 * 4 * b, 3.5 * b, 0.10)


# --------------------------------------------------- transitions (6 s)
def trans_calm_danger(tr):
    """Yen sang hiem: flute head, fragments quicken, low pulse enters
    at 4 s; ends on the hanging E over a minor pad."""
    chord(tr, CH["D"], 0.0, 3.0, 0.22)
    play(tr, "flute", D5, 0.1, 0.7, 0.7)
    play(tr, "flute", FS5, 0.8, 0.7, 0.7)
    play(tr, "flute", A5, 1.5, 0.9, 0.7)
    chord(tr, CH["Dm"], 3.0, 3.0, 0.28)
    for i, m in enumerate([D5, 65, A4, E4]):
        play(tr, "pluck", m, 2.6 + i * 0.35, 0.6, 0.55,
             pan=-0.2 + i * 0.13, bright=0.5)
    add(tr, drum(), 4.0, 0.0, 0.35)
    add(tr, drum(), 5.0, 0.0, 0.30)
    play(tr, "bass", 26, 4.0, 2.0, 0.5)
    play(tr, "flute", E5, 4.6, 1.3, 0.55)


def trans_danger_calm(tr):
    """Hiem ve yen: heartbeat pulse fades, the minor pad lifts to D
    major, the flute head returns softly; ends on a D pad + bell."""
    chord(tr, CH["Dm"], 0.0, 3.0, 0.28)
    add(tr, drum(), 0.0, 0.0, 0.35)
    add(tr, drum(), 1.1, 0.0, 0.28)
    add(tr, drum(), 2.0, 0.0, 0.20)
    play(tr, "bass", 26, 0.0, 2.6, 0.5)
    chord(tr, CH["D"], 2.6, 3.4, 0.26)
    play(tr, "flute", D5, 3.0, 0.8, 0.65)
    play(tr, "flute", FS5, 3.8, 0.8, 0.65)
    play(tr, "flute", A5, 4.6, 1.2, 0.6)
    play(tr, "bell", D5, 5.0, 1.0, 0.18, pan=0.2)
    play(tr, "pluck", D4, 4.9, 1.0, 0.35)


def trans_area(tr):
    """Qua mien khac: a water-crossing arpeggio (fuller than the 3 s
    cinema transition stinger), wash underneath, G pad at 3 s, D bell
    at 4.5 s; ends soft on the new shore."""
    add(tr, noise_sw(6.0), 0.0, 0.0, 0.04)
    seq = [D5, FS5, A5, B5, D6, B5, A5, FS5]
    for i, m in enumerate(seq):
        play(tr, "pluck", m, 0.2 + i * 0.42, 1.3, 0.5,
             pan=-0.4 + i * 0.11)
    chord(tr, CH["G"], 3.0, 3.0, 0.18)
    play(tr, "bell", D6, 4.5, 1.4, 0.2, pan=0.2)
    play(tr, "flute", D5, 4.6, 1.3, 0.55)
    add(tr, cm.water_drop(880.0), 5.2, 0.25, 0.10)


PIECES = [
    # stem, cueKey, nameVi, bpm, bars, builder, lp_hz, structure
    ("hub_lac_chau", "MUSIC/hub_lac_chau", "Lạc Châu · Nơi trở về",
     80, 16, piece_hub, None,
     "Hub form: warm D/G/Bm pads, bell on every bar line, flute "
     "states the question twice; a low pluck answers with the tail "
     "at bars 10-11 (the quiet answer a home may give); final bar "
     "rests on a soft D bell over the tonic pad."),
    ("thanh_lac", "MUSIC/thanh_lac", "Thanh Lạc · Chợ sáng",
     96, 16, piece_thanh_lac, None,
     "Town form: busiest street arrangement -- pluck arpeggios every "
     "bar plus a second off-beat pluck voice an octave down, bells, "
     "shaker; flute motif at bars 0 and 8, low pluck tail at bar 12."),
    ("rain_veil", "MUSIC/rain_veil", "Mưa · Màn nước mỏng",
     66, 16, piece_rain, 1200.0,
     "Rain form: sparse flute fragments (head at bar 0, second half "
     "at bar 8) over long pads, frequent drops, whole mix low-passed "
     "at 1200 Hz so rain ambience can sit on top; ends hanging on E."),
    ("swamp", "MUSIC/swamp", "Đầm · Nước đứng",
     58, 16, piece_swamp, None,
     "Swamp form: motif an octave down at half density over Bm/Em "
     "pads, low B0 drone, slow deep drops, one low bell per phrase; "
     "no drums; ends on a low hanging E."),
    ("dungeon", "MUSIC/dungeon", "Hầm · Đá lạnh",
     70, 12, piece_dungeon, None,
     "Dungeon form: D-minor fragments in low pluck, soft drum on the "
     "bar line, D1 drone, cold bell marks; the motif never completes "
     "-- the hanging E is the only high note, once, in the last bar."),
    ("arena", "MUSIC/arena", "Đấu trường · Hồi trống",
     120, 16, piece_arena, None,
     "Arena form: drum-led drive -- drum every beat plus offbeat hit, "
     "pluck ostinato in eighth notes, motif in bright pluck at bars 0 "
     "and 8, bell hits on the bar line; the one cue that lands, drum "
     "+ bell D closing the loop."),
    ("tragedy", "MUSIC/tragedy", "Bi kịch · Dây đứt",
     56, 12, piece_tragedy, None,
     "Tragedy form: slow D minor, solo flute fragments with long "
     "silences between them, single bells, one low pluck figure; no "
     "drums, no tail -- the last note is the hanging E alone over a "
     "Dm pad."),
]

TRANSITIONS = [
    # stem, cueKey, nameVi, builder, structure
    ("transition_calm_danger", "MUSIC/transition_calm_danger",
     "Chuyển · Yên sang hiểm", trans_calm_danger,
     "Calm to danger (6 s): flute head, pluck fragments quicken, low "
     "drum pulse enters at 4 s; ends on the hanging E over a minor "
     "pad. Use at encounter start; do not replay the intro of the "
     "danger cue (per Audio Direction, no intro replay on a "
     "non-reset encounter)."),
    ("transition_danger_calm", "MUSIC/transition_danger_calm",
     "Chuyển · Hiểm về yên", trans_danger_calm,
     "Danger to calm (6 s): heartbeat pulse fades by 2.5 s, minor pad "
     "lifts to D major, flute head returns softly; ends on a D pad + "
     "bell. Use at encounter end / safe-area return."),
    ("transition_area", "MUSIC/transition_area",
     "Chuyển · Qua miền khác", trans_area,
     "Area to area (6 s): water-crossing pluck arpeggio rising D5-D6 "
     "over a wash, G pad at 3 s, D bell at 4.5 s; ends soft on the "
     "new shore. Use at map/biome change; fuller than the 3 s cinema "
     "transition stinger, which stays presentation-only."),
]


# ------------------------------------------------------------- render
def render_music(spec) -> dict:
    (stem, cue_key, name_vi, bpm, bars, builder, lp_hz, structure) = spec
    seconds = bars * 240.0 / bpm
    tr = new_track(seconds)
    builder(tr, bpm)
    if lp_hz:
        for ch in range(2):
            tr[:, ch] = lowpass(tr[:, ch], lp_hz)
    tr = room(tr, 0.16)
    tr = tail_wrap(tr, 1.5)
    tr, raw_jump = end_landing(tr, 0.25)
    tr, _, _ = gain_stage(tr, -22.0, -7.0, stem)
    master = MASTER_DIR / "music" / f"{stem}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    write_master_wav(tr, master)
    runtime = RUNTIME_DIR / "music" / f"{stem}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    encode_ogg(master, runtime)
    m_entry = file_entry(master, f"Art_Source/Audio/Muse/COMPOSED/"
                         f"music/{stem}.wav", "pcm_s24le")
    r_entry = file_entry(runtime, f"ClientGodot/assets/audio/composed/"
                         f"music/{stem}.ogg", "vorbis")
    assert abs(m_entry["durationSeconds"] - seconds) < 0.05, stem
    assert -23.5 <= m_entry["integratedLufs"] <= -20.5, (stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -6.0, (stem, m_entry)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "MUSIC",
        "loop": True,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "tempoBpm": bpm, "bars": bars, "mode": "see structure",
            "motif": MOTIF_NOTE,
            "structure": structure,
            "rendering": RENDERING,
        },
        "master": m_entry, "runtime": r_entry,
        "seam": {**seam_stats(tr), "wrapJumpRaw": raw_jump,
                 "landingNote": "wrapJump is measured after a 0.25 s "
                                "end-landing blend to the first sample "
                                "(loop crossfade construction); "
                                "wrapJumpRaw is the step before it"},
    }


def render_transition(spec) -> dict:
    (stem, cue_key, name_vi, builder, structure) = spec
    tr = new_track(6.0)
    builder(tr)
    tr = room(tr, 0.12)
    fade = int(0.15 * SR)
    tr[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    tr, _, _ = gain_stage(tr, -25.0, -6.0, stem)
    master = MASTER_DIR / "transitions" / f"{stem}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    write_master_wav(tr, master)
    runtime = RUNTIME_DIR / "transitions" / f"{stem}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    encode_ogg(master, runtime)
    m_entry = file_entry(master, f"Art_Source/Audio/Muse/COMPOSED/"
                         f"transitions/{stem}.wav", "pcm_s24le")
    r_entry = file_entry(runtime, f"ClientGodot/assets/audio/composed/"
                         f"transitions/{stem}.ogg", "vorbis")
    assert -27.0 <= m_entry["integratedLufs"] <= -23.0, (stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -5.0, (stem, m_entry)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "TRANSITION",
        "loop": False,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "tempoBpm": None, "bars": None, "mode": "see structure",
            "motif": MOTIF_NOTE,
            "structure": structure,
            "rendering": RENDERING,
        },
        "master": m_entry, "runtime": r_entry,
    }


def save_pack(by_key: dict):
    """Write the delivery manifest from whatever cues exist so far.
    Called after every single render: a killed run still leaves a
    valid partial manifest on disk (checkpoint 26 lesson)."""
    order = [spec[1] for spec in PIECES] + [t[1] for t in TRANSITIONS]
    cues = [by_key[k] for k in order if k in by_key]
    n_music = sum(1 for c in cues if c["kind"] == "MUSIC")
    n_trans = sum(1 for c in cues if c["kind"] == "TRANSITION")
    pack = {
        "packId": "NGM_MUSIC_SCORE_MD1_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 1 - whole-game "
                      "score batch 1: 7 missing core cues + 3 "
                      "transition bridges (Work Order 37 module M-D)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: melodies, harmony and "
                      "arrangements authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_score_md1.py (synthesis engine "
                      "reused from checkpoint 26 "
                      "build_composed_music.py) and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These 10 cues are NEW audio and "
                      "are counted separately from the 541 ported "
                      "PackV1 files of checkpoints 07/08 and from the "
                      "checkpoint-26 composed pack, which keep their "
                      "own provenance and are untouched.",
        "counts": {"music": n_music, "transitions": n_trans,
                   "total": len(cues)},
        "cues": cues,
        "notes": [
            "Adoption is a presentation-adapter decision (Codex): the "
            "MD1 cues are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ and do NOT replace the "
            "ported PackV1 files, their cue bindings, or the "
            "checkpoint-26 composed cues.",
            "Music cues loop by construction (1.5 s tail wrap); the "
            "seam block records the checkpoint-07 indicator, not a "
            "seamlessness PASS. No ear audition has been done; "
            "loudness/true-peak are measured from real bytes.",
            "Transitions are 6.0 s one-shots (-25 LUFS target). They "
            "bridge score states (calm/danger/area); they do NOT "
            "replay a destination cue's intro, per the Audio "
            "Direction rule for non-reset encounters.",
            "The composition concept follows the audio direction doc: "
            "Ben Mua's theme is a phrase left hanging ('cau nhac bo "
            "lung'); the full flute tail is reserved for the resolve "
            "stinger and rift_finale. A low pluck tail is the quiet "
            "answer a home/street cue may give (thang_long precedent, "
            "checkpoint 26).",
            "Remaining M-D work for a later checkpoint: per-cue "
            "intro/outro segments, stems, and phase-layer candidates "
            "for the new cues; the coverage matrix "
            "(MUSIC_SCORE_MD_COVERAGE_v1.json) lists them as open.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['total']} MD1 cues", flush=True)


def build_coverage() -> dict:
    """M-D slot coverage: all 15 WO37 slots mapped to composed cues
    (checkpoint 26 + this MD1 batch), ported PackV1 cues and adjacent
    ambience. Written after every render completes."""
    ported = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_AMBIENCE_pack_v1.json").read_text(encoding="utf-8"))
    ported_music = {c["cueKey"] for c in ported["cues"]
                    if c["cueKey"].startswith("MUSIC/")}
    ported_amb = {c["cueKey"] for c in ported["cues"]
                  if c["cueKey"].startswith("AMBIENCE/")}
    cp26 = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "MUSIC_COMPOSED_pack_v1.json").read_text(encoding="utf-8"))
    cp26_music = {c["cueKey"] for c in cp26["cues"]
                  if c["kind"] == "MUSIC"}
    pack = json.loads(DELIVERY.read_text(encoding="utf-8"))
    md1_music = {c["cueKey"] for c in pack["cues"]
                 if c["kind"] == "MUSIC"}
    md1_trans = {c["cueKey"] for c in pack["cues"]
                 if c["kind"] == "TRANSITION"}

    def row(slot, slot_vi, composed, pack_name, notes, adjacent=None):
        p = composed if composed in ported_music else None
        return {
            "slot": slot, "slotVi": slot_vi,
            "composedCueKey": composed,
            "composedPack": pack_name,
            "portedCueKey": p,
            "adjacentAmbience": adjacent or [],
            "status": ("COVERED_COMPOSED" if composed
                       else "GAP_NO_MUSIC_CUE"),
            "notes": notes,
        }

    slots = [
        row("hub", "Trung tâm / hub an toàn", "MUSIC/hub_lac_chau",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before (ported pack has "
            "no hub music; city_night ambience is adjacent only)."),
        row("explore", "Khám phá", "MUSIC/quiet_discovery",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26; ported cue with the same key exists."),
        row("ben_mua", "Bến Mưa", "MUSIC/ben_mua",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26; the theme itself; ported cue exists."),
        row("thanh_lac", "Thanh Lạc (thị trấn)", "MUSIC/thanh_lac",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before (no ported "
            "Thanh Lac music; thang_long_crowd ambience belongs to "
            "Thang Long, not Thanh Lac)."),
        row("thang_long", "Thăng Long", "MUSIC/thang_long",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26; ported cue exists.",
            ["AMBIENCE/thang_long_crowd"]),
        row("rain", "Mưa (nhạc nền mưa)", "MUSIC/rain_veil",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: before, only ambience existed "
            "(rain_light, rain_heavy); no music cue.",
            ["AMBIENCE/rain_light", "AMBIENCE/rain_heavy"]),
        row("swamp", "Đầm (swamp)", "MUSIC/swamp",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before; river_shore "
            "ambience is water-edge, not swamp.",
            ["AMBIENCE/river_shore"]),
        row("forest", "Rừng", "MUSIC/lam_trieu",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26 (Lam Trieu, G major transposition); ported "
            "cue exists.", ["AMBIENCE/wind_canopy"]),
        row("mountain", "Núi / cửa ải", "MUSIC/tran_son",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26 (Tran Son gate form); ported cue exists.",
            ["AMBIENCE/mountain_wind"]),
        row("desert", "Sa mạc", "MUSIC/sa_hoa",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26 (Sa Hoa, A minor pentatonic); ported cue "
            "exists.", ["AMBIENCE/desert_wind"]),
        row("dungeon", "Hầm / dungeon", "MUSIC/dungeon",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before; cave_drips "
            "ambience is adjacent only.",
            ["AMBIENCE/cave_drips"]),
        row("boss", "Boss", "MUSIC/boss_mang_cot",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26; ported cue exists."),
        row("arena", "Đấu trường / arena", "MUSIC/arena",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before."),
        row("tragedy", "Bi kịch / tragedy", "MUSIC/tragedy",
            "MUSIC_SCORE_MD1_pack_v1",
            "MD1 batch 1: no music cue existed before."),
        row("resolution", "Kết / resolution", "MUSIC/rift_finale",
            "MUSIC_COMPOSED_pack_v1",
            "Checkpoint 26; the set's only full close; ported cue "
            "exists."),
    ]
    covered = sum(1 for s in slots if s["status"] == "COVERED_COMPOSED")
    coverage = {
        "coverageId": "NGM_MUSIC_SCORE_MD_COVERAGE_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 1",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "workOrder": "37_MUSE_FULL_CAMPAIGN_MEDIA_20261108.md module M-D",
        "slotsTotal": len(slots),
        "slotsCoveredComposed": covered,
        "slotsGap": len(slots) - covered,
        "extraComposedOutsideSlots": [
            {"cueKey": "MUSIC/bach_uyen",
             "pack": "MUSIC_COMPOSED_pack_v1",
             "note": "Bach Uyen (underwater city) is a composed cue "
                     "outside the 15 WO37 M-D slots; kept, not counted "
                     "as slot coverage."},
        ],
        "transitions": sorted(md1_trans),
        "transitionNotes": [
            "3 bridges delivered (calm->danger, danger->calm, "
            "area->area); each 6.0 s, -25 LUFS target, one-shot.",
            "The 3 s cinema transition stinger (checkpoint 26) stays "
            "presentation-only and is NOT a score transition.",
        ],
        "openForMdCp2": [
            "Per-cue intro/outro segments for the 7 MD1 cues (and the "
            "9 checkpoint-26 cues, if the director wants them).",
            "Stems (lead / pad-bass / percussion groups) per cue.",
            "Phase-layer candidates (e.g. arena low/high intensity "
            "layers, boss phase layers).",
            "Ear audition of all 10 MD1 cues + loop seams "
            "(NOT_AUDITIONED).",
        ],
        "slots": slots,
    }
    COVERAGE.write_text(json.dumps(coverage, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {COVERAGE.relative_to(ROOT)}: "
          f"{covered}/{len(slots)} slots covered, "
          f"{len(slots) - covered} gaps", flush=True)
    return coverage


def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))
    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}
    for spec in PIECES:
        if only is not None and spec[0] not in only:
            continue
        entry = render_music(spec)
        by_key[entry["cueKey"]] = entry
        save_pack(by_key)
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP, wrap jump "
              f"{entry['seam']['wrapJump']}", flush=True)
    for spec in TRANSITIONS:
        if only is not None and spec[0] not in only:
            continue
        entry = render_transition(spec)
        by_key[entry["cueKey"]] = entry
        save_pack(by_key)
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP", flush=True)
    build_coverage()
    return 0


if __name__ == "__main__":
    sys.exit(main())
