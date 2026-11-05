#!/usr/bin/env python3
"""MEDIA-02 checkpoint 26: ORIGINAL composed music + cinema stingers.

Goi 30 item 7 asks for actually composed/remixed music/SFX, separate from
the 541 ported PackV1 files (checkpoints 07/08), which keep their own
provenance and are NOT counted as new audio. Everything in this pack is
new: melodies, harmony and arrangements are authored here as data and
rendered by procedural synthesis -- no external samples, no ported bytes,
no real-voice cloning (no voices at all).

Composition concept (from docs/production/Audio_Production_Direction_v1
_vi.md section 1): Ben Mua's music is built on ONE original leitmotif --
a "cau nhac bo lung", a phrase left hanging. The motif states a question
in D major pentatonic and stops on scale degree 2 (E); the answering
tail (F# - E - D) is deliberately WITHHELD in the exploration/boss
material and is only supplied by the resolve stinger and the finale.
The nine music cues are nine transformations of this one system (five
elements / five regions of Lac Chau), so the score coheres the way a
game score should:

  ben_mua        the theme itself, flute + tranh pluck, ends hanging
  thang_long     brighter street arrangement, bells, busier plucks
  boss_mang_cot  motif fragmented in D minor, low pulse, no tail
  quiet_discovery solo fragments, long silences, bell echoes, no tail
  lam_trieu      motif transposed to G (forest), leaf-tick percussion
  sa_hoa         motif in A minor pentatonic, dry plucks, syncopation
  tran_son       bell-led stately form, drum on the bar line
  bach_uyen      motif slowed underwater: low register, heavy lowpass
  rift_finale    motif passed across five registers; the tail is
                 finally played and the piece lands on D major

Cinema stingers (SFX/CINEMA/*, presentation-only cues):
  reveal     motif head ascending (something is uncovered)
  tension    motif stopped on the hanging note, low pulse under it
  resolve    the withheld tail, played at last, warm close
  transition water-crossing arpeggio into a soft wash

Outputs:
  Art_Source/Audio/Muse/COMPOSED/music/<name>.wav    (master, 48k/24b)
  Art_Source/Audio/Muse/COMPOSED/cinema/<name>.wav   (master, 48k/24b)
  ClientGodot/assets/audio/composed/music/<name>.ogg  (runtime)
  ClientGodot/assets/audio/composed/cinema/<name>.ogg (runtime)
  Implementation/Content/Audio/Deliveries/MUSIC_COMPOSED_pack_v1.json

Loudness is measured from the real rendered bytes with ffmpeg loudnorm
(the checkpoint 07 method); each cue is gain-staged to its target in at
most 3 passes and the recorded values are the final measured ones.
Loops are made seamless by construction: the last 1.5 s of ring-out is
wrapped into the head with an equal-power crossfade, and the seam
indicator (checkpoint 07 method) is recorded, not claimed as a PASS.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import lfilter

ROOT = Path(__file__).resolve().parents[3]
SR = 48000
MASTER_DIR = ROOT / "Art_Source/Audio/Muse/COMPOSED"
RUNTIME_DIR = ROOT / "ClientGodot/assets/audio/composed"
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "MUSIC_COMPOSED_pack_v1.json")
TMP = Path("/tmp/composed_music")
TMP.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(26)


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n"
                           f"{r.stderr[-1500:]}")
    return r


# ---------------------------------------------------------------- synth
def note_freq(midi: float) -> float:
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def lowpass(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    a = 1.0 - np.exp(-2.0 * np.pi * cutoff_hz / SR)
    return lfilter([a], [1.0, -(1.0 - a)], x)


def highpass(x: np.ndarray, cutoff_hz: float) -> np.ndarray:
    a = np.exp(-2.0 * np.pi * cutoff_hz / SR)
    return lfilter([1.0, -1.0], [1.0, -a], x)


def adsr_env(n: int, attack: float, decay_to: float, release: float) -> np.ndarray:
    t = np.arange(n) / SR
    env = np.ones(n)
    a_n = max(1, int(attack * SR))
    env[:a_n] = np.linspace(0.0, 1.0, a_n)
    r_n = max(1, int(release * SR))
    if r_n < n:
        env[-r_n:] *= np.linspace(1.0, decay_to, r_n)
    return env


def pluck(freq: float, dur_s: float, vel: float = 0.8,
          bright: float = 1.0) -> np.ndarray:
    """Additive plucked string: harmonics with per-partial decay plus a
    short onset click. Vectorized; no Karplus-Strong loop needed."""
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    tau0 = min(1.6, 0.45 + 900.0 / (freq * 4.0)) * (1.25 if bright > 1 else 1.0)
    sig = np.zeros(n)
    for k in range(1, 9):
        g = (1.0 / k ** 1.5) * (bright if k > 4 else 1.0)
        tau = tau0 / (k ** 0.65)
        sig += g * np.sin(2 * np.pi * freq * k * t
                          + 0.002 * k) * np.exp(-t / tau)
    click_n = int(0.004 * SR)
    sig[:click_n] += (RNG.random(click_n) - 0.5) * np.linspace(0.5, 0.0, click_n)
    lp = 2500.0 * bright
    sig = lowpass(sig, lp)
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * vel).astype(np.float64)


def flute(freq: float, dur_s: float, vel: float = 0.8) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    vib = 1.0 + 0.004 * np.sin(2 * np.pi * 5.0 * t - np.pi / 2) \
        * np.minimum(1.0, t / 0.4)
    phase = 2 * np.pi * freq * np.cumsum(vib) / SR
    sig = np.sin(phase) + 0.25 * np.sin(2 * phase) + 0.06 * np.sin(3 * phase)
    breath = (RNG.random(n) - 0.5) * 0.03
    sig = sig + lowpass(breath, 1200.0)
    env = adsr_env(n, 0.09, 0.0, min(0.35, dur_s * 0.4))
    sig = sig * env
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * vel).astype(np.float64)


def pad_chord(freqs, dur_s: float, vel: float = 0.5) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for f in freqs:
        for det in (-4.0, 3.0):
            fd = f * 2.0 ** (det / 1200.0)
            sig += (np.sin(2 * np.pi * fd * t)
                    + 0.35 * np.sin(4 * np.pi * fd * t)
                    + 0.12 * np.sin(6 * np.pi * fd * t))
    sig = lowpass(sig, 1400.0)
    env = adsr_env(n, min(1.2, dur_s * 0.3), 0.0, min(1.5, dur_s * 0.35))
    sig = sig * env
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * vel).astype(np.float64)


def bell(freq: float, dur_s: float, vel: float = 0.5) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for ratio, g, tau_scale in ((1.0, 1.0, 1.0), (2.02, 0.55, 0.6),
                                (2.74, 0.38, 0.42), (3.76, 0.22, 0.3),
                                (5.40, 0.10, 0.18)):
        tau = min(2.8, dur_s * 0.55) * tau_scale
        sig += g * np.sin(2 * np.pi * freq * ratio * t) * np.exp(-t / tau)
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * vel).astype(np.float64)


def bass_note(freq: float, dur_s: float, vel: float = 0.7) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.35 * np.sin(4 * np.pi * freq * t)
           + 0.15 * np.sin(6 * np.pi * freq * t))
    sig = lowpass(sig, 500.0)
    env = adsr_env(n, 0.02, 0.15, min(0.4, dur_s * 0.5))
    sig = sig * env * np.exp(-t / max(0.8, dur_s))
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * vel).astype(np.float64)


def water_drop(f0: float = 800.0) -> np.ndarray:
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = f0 * np.exp(-t * 14.0) + 180.0
    phase = 2 * np.pi * np.cumsum(f) / SR
    env = np.sin(np.pi * np.minimum(1.0, t / 0.16)) ** 2
    return (np.sin(phase) * env * 0.8).astype(np.float64)


def drum() -> np.ndarray:
    n = int(0.4 * SR)
    t = np.arange(n) / SR
    f = 45.0 + 75.0 * np.exp(-t * 22.0)
    phase = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(phase) * np.exp(-t * 9.0)
    noise = lowpass(RNG.random(n) - 0.5, 300.0) * np.exp(-t * 30.0)
    sig = body + noise
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak).astype(np.float64)


def noise_sw(dur_s: float) -> np.ndarray:
    n = int(dur_s * SR)
    t = np.arange(n) / SR
    sig = lowpass(RNG.random(n) - 0.5, 900.0)
    env = np.sin(np.pi * np.minimum(1.0, t / dur_s)) ** 2
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * env).astype(np.float64)


def shaker(dur_s: float = 0.09) -> np.ndarray:
    n = int(dur_s * SR)
    sig = highpass(RNG.random(n) - 0.5, 5000.0)
    env = np.exp(-np.arange(n) / (0.03 * SR))
    peak = np.max(np.abs(sig)) + 1e-9
    return (sig / peak * env).astype(np.float64)


def comb_delay(x: np.ndarray, d: int, g: float) -> np.ndarray:
    """Feedback comb y[n] = x[n] + g*y[n-d], computed in delay-sized
    blocks (every y[n-d] in a block is already known). scipy's lfilter
    with a ~20k-tap denominator was the render bottleneck; this is
    the same filter in O(n)."""
    y = x.copy()
    n = len(x)
    for start in range(d, n, d):
        end = min(n, start + d)
        y[start:end] += g * y[start - d:end - d]
    return y


def room(track: np.ndarray, wet: float = 0.15) -> np.ndarray:
    """Two feedback comb delays as a light 'river hall'."""
    out = track.copy()
    for d_s, g in ((0.31, 0.24), (0.43, 0.19)):
        d = int(d_s * SR)
        for ch in range(2):
            out[:, ch] += comb_delay(track[:, ch], d, g) * wet
    return out


def tail_wrap(track: np.ndarray, wrap_s: float = 1.5) -> np.ndarray:
    """Loop construction: the final wrap_s of ring-out is mixed over
    the head (fading out) and faded to zero at the file end, so in a
    loop the tail rings across the seam instead of being cut. Total
    length is unchanged. The residual seam step is measured and
    recorded by seam_stats, never hidden."""
    n = int(wrap_s * SR)
    if len(track) <= 2 * n:
        return track
    fade_out = np.linspace(1.0, 0.0, n)[:, None]
    out = track.copy()
    out[:n] = track[:n] + track[-n:] * fade_out
    out[-n:] = track[-n:] * fade_out
    return out


# ------------------------------------------------------------- schedule
def new_track(seconds: float) -> np.ndarray:
    return np.zeros((int(round(seconds * SR)), 2), dtype=np.float64)


def add(track: np.ndarray, sig: np.ndarray, at_s: float,
        pan: float = 0.0, gain: float = 1.0):
    start = int(round(at_s * SR))
    if start >= len(track):
        return
    end = min(len(track), start + len(sig))
    if end <= start:
        return
    seg = sig[: end - start] * gain
    left = np.cos((pan + 1.0) * np.pi / 4.0)
    right = np.sin((pan + 1.0) * np.pi / 4.0)
    track[start:end, 0] += seg * left
    track[start:end, 1] += seg * right


def play(track, voice: str, midi: float, at_s: float, dur_s: float,
         vel: float = 0.8, pan: float = 0.0, **kw):
    fn = {"pluck": pluck, "flute": flute, "bell": bell,
          "bass": bass_note}[voice]
    sig = fn(note_freq(midi), dur_s, vel, **kw)
    add(track, sig, at_s, pan, 1.0)


def chord(track, midis, at_s: float, dur_s: float, vel: float = 0.5,
          pan: float = 0.0):
    sig = pad_chord([note_freq(m) for m in midis], dur_s, vel)
    add(track, sig, at_s, pan, 1.0)


def beat_s(bpm: float) -> float:
    return 60.0 / bpm


def melody(track, voice: str, events, bpm: float, bar0: int,
           vel: float = 0.8, pan: float = 0.0, beat_offset: float = 0.0,
           **kw):
    """events: (beat_in_phrase, midi, len_beats). Phrase starts at bar0."""
    b = beat_s(bpm)
    start = bar0 * 4 * b
    for beat, midi, ln in events:
        play(track, voice, midi, start + (beat + beat_offset) * b,
             max(0.25, ln * b * 1.05), vel, pan, **kw)


# The leitmotif. D major pentatonic: D E F# A B.
D4, E4, FS4, A4, B4 = 62, 64, 66, 69, 71
D5, E5, FS5, A5, B5, D6 = 74, 76, 78, 81, 83, 86
# Question phrase (2 bars): states the motif, stops hanging on E.
MOTIF_Q = [(0, D5, 1), (1, FS5, 1), (2, A5, 1.5), (3.5, B5, 0.5),
           (4, A5, 1), (5, FS5, 1), (6, E5, 2)]
# The withheld tail: only the resolve stinger and the finale play it.
MOTIF_TAIL = [(0, FS5, 1), (1, E5, 1), (2, D5, 2)]
# First bar only (fragment used by quiet_discovery / boss).
MOTIF_HEAD = MOTIF_Q[:4]

CH = {  # pad voicings (midi triples)
    "D": [50, 57, 66], "G": [55, 59, 62], "Bm": [47, 54, 62],
    "A": [45, 52, 57], "Em": [40, 47, 55],
    "Dm": [50, 53, 57], "F": [53, 57, 60], "C": [48, 52, 55],
    "Gm": [43, 50, 55],
    "Cmaj": [48, 55, 59], "Dsus": [50, 57, 64],
}


def bass_line(track, roots, bpm: float, vel: float = 0.55,
              pattern=(0, 2), pan: float = 0.0):
    b = beat_s(bpm)
    for bar, root in enumerate(roots):
        for bt in pattern:
            play(track, "bass", root, bar * 4 * b + bt * b, 1.6 * b,
                 vel, pan)


def drops(track, times, gain: float = 0.10, seed: int = 7):
    rng = np.random.default_rng(seed)
    for t in times:
        f0 = 700.0 + rng.random() * 500.0
        add(track, water_drop(f0), t, float(rng.uniform(-0.5, 0.5)),
            gain)


# ------------------------------------------------------------- pieces
def piece_ben_mua(tr, bpm):
    prog = ["D", "D", "G", "D", "Bm", "G", "D", "A",
            "D", "D", "G", "Bm", "Em", "A", "D", "D", "D"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.34)
    bass_line(tr, [38, 38, 43, 38, 35, 43, 38, 33,
                   38, 38, 43, 35, 40, 33, 38, 38, 38], bpm, 0.5)
    melody(tr, "flute", MOTIF_Q, bpm, 0, 0.85)
    melody(tr, "pluck", [(be, m - 12, ln) for be, m, ln in MOTIF_Q],
           bpm, 2, 0.6, pan=-0.2)
    melody(tr, "flute", MOTIF_Q, bpm, 4, 0.8, pan=0.1)
    melody(tr, "pluck", MOTIF_HEAD, bpm, 6, 0.55, pan=0.25)
    melody(tr, "flute", MOTIF_Q, bpm, 10, 0.85)
    melody(tr, "pluck", [(0, A4, 1), (1, B4, 1), (2, A4, 2)],
           bpm, 12, 0.5, pan=-0.3)
    melody(tr, "flute", [(0, D5, 1), (1, FS5, 1), (2, A5, 2)],
           bpm, 14, 0.7)
    # Final bar: the hanging note alone over the tonic pad (loop point).
    play(tr, "flute", E5, 16 * 4 * beat_s(bpm), 3.0 * beat_s(bpm), 0.65)
    play(tr, "bell", D5, 16 * 4 * beat_s(bpm), 3.2 * beat_s(bpm), 0.25)
    drops(tr, [5.3, 13.9, 22.4, 31.0, 44.8, 52.2], 0.08)


def piece_thang_long(tr, bpm):
    prog = ["D", "G", "D", "A", "Bm", "G", "D", "A",
            "D", "G", "Bm", "A", "D", "G", "A", "D"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.30)
        play(tr, "bell", CH[c][0] + 24, bar * 4 * beat_s(bpm),
             2.5 * beat_s(bpm), 0.20, pan=-0.3 if bar % 2 else 0.3)
    bass_line(tr, [38, 43, 38, 33, 35, 43, 38, 33,
                   38, 43, 35, 33, 38, 43, 33, 38], bpm, 0.5,
              pattern=(0, 1, 2, 3))
    arp = [(0, 0, 0.5), (0.5, 1, 0.5), (1, 2, 0.5), (1.5, 1, 0.5),
           (2, 0, 0.5), (2.5, 1, 0.5), (3, 2, 0.5), (3.5, 1, 0.5)]
    scale = [D5, FS5, A5, B5, D6]
    for bar in range(16):
        ev = [(bt, scale[(i + bar) % len(scale)], ln) for bt, i, ln in arp]
        melody(tr, "pluck", ev, bpm, bar, 0.34, pan=0.15)
    melody(tr, "flute", MOTIF_Q, bpm, 0, 0.8)
    melody(tr, "flute", MOTIF_Q, bpm, 8, 0.8)
    # The city answers the hanging phrase casually, an octave down.
    melody(tr, "pluck", MOTIF_TAIL, bpm, 10, 0.55, pan=-0.2)
    melody(tr, "flute", [(0, D5, 2), (2, A5, 1), (3, FS5, 1)], bpm, 14,
           0.75)
    for bar in range(16):
        for bt in (0.5, 1.5, 2.5, 3.5):
            add(tr, shaker(0.09), bar * 4 * beat_s(bpm) + bt * beat_s(bpm),
                -0.4 if bar % 2 else 0.4, 0.05)


def piece_boss(tr, bpm):
    prog = ["Dm", "Dm", "F", "Dm", "C", "Dm", "Gm", "Dm", "F", "Dm"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.30)
    b = beat_s(bpm)
    for bar in range(10):  # heartbeat pulse, tightening at the end
        g = 0.35 + (0.25 if bar >= 8 else 0.0)
        add(tr, drum(), bar * 4 * b, 0.0, g)
        add(tr, drum(), bar * 4 * b + 1.5 * b, 0.0, g * 0.7)
        play(tr, "bass", 26, bar * 4 * b, 3.4 * b, 0.6)  # D1 root drone
    frag = [(0, D4, 1), (1, 65, 1), (2, A4, 1.5)]  # D F A, minor head
    for bar in (2, 5, 7):
        melody(tr, "pluck", frag, bpm, bar, 0.7, pan=-0.15, bright=0.4)
    melody(tr, "pluck", [(0, A4, 1), (1, 65, 1), (2, E4, 2)], bpm, 8,
           0.65, pan=0.2, bright=0.4)
    # One foreign bell (F# against D minor): the wrong note, once.
    play(tr, "bell", FS5, 8 * 4 * b + 2 * b, 3.0 * b, 0.22)
    play(tr, "bell", D4, 0.0, 4.0 * b, 0.18)


def piece_quiet(tr, bpm):
    b = beat_s(bpm)
    chord(tr, CH["D"], 0, 8 * b, 0.16)
    melody(tr, "flute", MOTIF_HEAD, bpm, 0, 0.55)
    play(tr, "bell", A4, 4 * 4 * b, 5 * b, 0.20, pan=-0.3)
    play(tr, "bell", FS4, 6 * 4 * b, 5 * b, 0.16, pan=0.3)
    # Second half of the question, alone; still ends on the hanging E.
    melody(tr, "flute", [(0, A5, 1), (1, FS5, 1), (2, E5, 2)], bpm, 8,
           0.5)
    chord(tr, CH["G"], 10 * 4 * b, 8 * b, 0.13)
    play(tr, "bell", D5, 12 * 4 * b, 6 * b, 0.15)
    melody(tr, "pluck", [(0, D5, 1), (1, FS5, 1)], bpm, 13, 0.35,
           pan=0.2)
    chord(tr, CH["D"], 14 * 4 * b, 8 * b, 0.15)
    drops(tr, [3.1, 9.7, 18.2, 27.5, 36.9, 47.3, 55.8], 0.09)
    add(tr, noise_sw(9.0), 24.0, 0.0, 0.012)  # far water, barely there


def piece_lam_trieu(tr, bpm):
    # Motif transposed to G major pentatonic (G A B D E).
    shift = 5
    q = [(be, m + shift, ln) for be, m, ln in MOTIF_Q]
    prog = ["G", "Cmaj", "G", "D", "Em", "Cmaj", "G", "D",
            "G", "Cmaj", "Em", "D", "G", "Cmaj", "D", "G",
            "Em", "Cmaj", "D", "G"]
    chmap = {"G": [43, 47, 50], "Cmaj": CH["C"], "D": CH["D"],
             "Em": CH["Em"]}
    for bar, c in enumerate(prog):
        chord(tr, chmap[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.30)
    bass_line(tr, [31, 36, 31, 38, 28, 36, 31, 38,
                   31, 36, 28, 38, 31, 36, 38, 31,
                   28, 36, 38, 31], bpm, 0.45)
    melody(tr, "flute", q, bpm, 0, 0.8)
    melody(tr, "pluck", [(be, m - 12, ln) for be, m, ln in q], bpm, 4,
           0.5, pan=0.25)
    # Ornamented restatement: quick neighbor pickups before long notes.
    orn = [(0, 79, 0.5), (0.5, 81, 0.5), (1, 83, 1), (2, 86, 1.5),
           (3.5, 88, 0.5), (4, 86, 1), (5, 83, 1), (6, 81, 2)]
    melody(tr, "flute", orn, bpm, 8, 0.78, pan=-0.1)
    melody(tr, "flute", q, bpm, 14, 0.75)
    for bar in range(0, 20, 2):
        for bt in (1.5, 3.5):
            add(tr, shaker(0.07), bar * 4 * beat_s(bpm) + bt * beat_s(bpm),
                0.45, 0.045)
    drops(tr, [7.4, 19.8, 33.1, 45.6], 0.06)


def piece_sa_hoa(tr, bpm):
    # Motif in A minor pentatonic (A C D E G), mapped by scale-degree
    # index so the contour survives: D->A, F#->D, A->E, B->G, E->C.
    amap = {D5: 69, FS5: 74, A5: 76, B5: 79, E5: 72}
    q = [(be, amap[m], ln) for be, m, ln in MOTIF_Q]
    prog = ["Dm", "Dm", "F", "Dm", "C", "Dm", "F", "C",
            "Dm", "Dm", "Gm", "Dm", "F", "C", "Dm", "Dm",
            "F", "Gm", "Dm", "Dm"]
    for bar, c in enumerate(prog):
        if bar % 2 == 0:
            chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.16)
    bass_line(tr, [33, 33, 41, 33, 36, 33, 41, 36,
                   33, 33, 43, 33, 41, 36, 33, 33,
                   41, 43, 33, 33], bpm, 0.55, pattern=(0, 1.5, 3))
    melody(tr, "pluck", q, bpm, 0, 0.7, bright=1.4)
    melody(tr, "pluck", q, bpm, 6, 0.68, bright=1.4, beat_offset=0.5)
    melody(tr, "pluck", [(0, 81, 1), (1, 79, 1), (2, 76, 2)], bpm, 12,
           0.6, bright=1.4)
    b = beat_s(bpm)
    for bar in range(20):
        add(tr, drum(), bar * 4 * b + 2 * b, 0.0, 0.16)
        add(tr, shaker(0.06), bar * 4 * b + 3.5 * b, -0.3, 0.05)


def piece_tran_son(tr, bpm):
    prog = ["D", "G", "D", "Bm", "D", "G", "A", "D",
            "G", "Bm", "D", "A", "D", "G", "D"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.32)
    bass_line(tr, [38, 43, 38, 35, 38, 43, 33, 38,
                   43, 35, 38, 33, 38, 43, 38], bpm, 0.5, pattern=(0,))
    b = beat_s(bpm)
    bellq = [(be, m, ln) for be, m, ln in MOTIF_Q]
    melody(tr, "bell", bellq, bpm, 0, 0.4)
    melody(tr, "flute", [(be, m - 12, ln) for be, m, ln in MOTIF_Q],
           bpm, 5, 0.6)
    melody(tr, "bell", bellq, bpm, 9, 0.38, pan=0.15)
    for bar in range(15):
        add(tr, drum(), bar * 4 * b, 0.0, 0.22)
    play(tr, "flute", E5, 14 * 4 * b, 3 * b, 0.4)  # the gate still waits
    play(tr, "bell", D5, 14 * 4 * b, 3.5 * b, 0.25)


def piece_bach_uyen(tr, bpm):
    prog = ["Bm", "Bm", "Em", "Bm", "G", "Bm", "Em", "D",
            "Bm", "G", "Em", "Bm", "D", "Em", "Bm"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.36)
    bass_line(tr, [35, 35, 40, 35, 43, 35, 40, 38,
                   35, 43, 40, 35, 38, 40, 35], bpm, 0.55,
              pattern=(0, 2))
    low_q = [(be, m - 12, ln * 1.0) for be, m, ln in MOTIF_Q]
    melody(tr, "flute", low_q, bpm, 1, 0.6)
    melody(tr, "flute", low_q, bpm, 9, 0.55, pan=0.15)
    play(tr, "bell", D4, 5 * 4 * beat_s(bpm), 6 * beat_s(bpm), 0.2)
    play(tr, "bell", A4, 12 * 4 * beat_s(bpm), 6 * beat_s(bpm), 0.16,
         pan=-0.2)
    drops(tr, [8.8, 21.4, 35.9, 49.2], 0.05)


def piece_finale(tr, bpm):
    prog = ["D", "G", "Bm", "A", "D", "G", "Bm", "A",
            "D", "G", "Bm", "Em", "A", "D", "D", "D"]
    for bar, c in enumerate(prog):
        chord(tr, CH[c], bar * 4 * beat_s(bpm), 4 * beat_s(bpm), 0.34)
    bass_line(tr, [38, 43, 35, 33, 38, 43, 35, 33,
                   38, 43, 35, 40, 33, 38, 38, 38], bpm, 0.55)
    # Five streams state the motif in turn (registers rise).
    melody(tr, "pluck", [(be, m - 24, ln) for be, m, ln in MOTIF_HEAD],
           bpm, 0, 0.65, pan=-0.4, bright=0.7)
    melody(tr, "pluck", [(be, m - 12, ln) for be, m, ln in MOTIF_HEAD],
           bpm, 3, 0.6, pan=-0.2)
    melody(tr, "flute", MOTIF_HEAD, bpm, 6, 0.7, pan=0.1)
    melody(tr, "bell", [(be, m, ln) for be, m, ln in MOTIF_HEAD],
           bpm, 9, 0.35, pan=0.3)
    melody(tr, "flute", MOTIF_Q, bpm, 11, 0.85)
    melody(tr, "bell", MOTIF_Q, bpm, 11, 0.25, pan=-0.25)
    # The withheld tail, at last -- then the only full close in the set.
    melody(tr, "flute", MOTIF_TAIL, bpm, 14, 0.9)
    play(tr, "bell", D6, 15 * 4 * beat_s(bpm), 3.5 * beat_s(bpm), 0.3)
    play(tr, "bell", D5, 15 * 4 * beat_s(bpm), 3.5 * beat_s(bpm), 0.25,
         pan=-0.2)
    add(tr, drum(), 15 * 4 * beat_s(bpm), 0.0, 0.3)


STINGERS = {
    "reveal": ("SFX/CINEMA/reveal", "Vén một điều lạ"),
    "tension": ("SFX/CINEMA/tension", "Mạch chưa khép"),
    "resolve": ("SFX/CINEMA/resolve", "Điều đã đối chiếu"),
    "transition": ("SFX/CINEMA/transition", "Qua một miền nước"),
}


def sting_reveal(tr):
    chord(tr, CH["D"], 0.0, 3.0, 0.22)
    for i, m in enumerate([D5, FS5, A5, D6]):
        play(tr, "pluck", m, 0.15 + i * 0.32, 1.6, 0.6,
             pan=-0.2 + i * 0.13)
    play(tr, "bell", A5, 1.45, 1.5, 0.22)


def sting_tension(tr):
    chord(tr, CH["Dm"], 0.0, 3.0, 0.30)
    add(tr, drum(), 0.0, 0.0, 0.4)
    add(tr, drum(), 1.1, 0.0, 0.3)
    play(tr, "flute", E5, 0.5, 2.3, 0.6)  # the hanging note, alone
    play(tr, "bass", 26, 0.0, 2.8, 0.5)


def sting_resolve(tr):
    chord(tr, CH["D"], 0.0, 3.0, 0.26)
    # The withheld tail at last (timed by hand: F# 0.1, E 0.7, D 1.3).
    play(tr, "flute", FS5, 0.1, 0.7, 0.8)
    play(tr, "flute", E5, 0.7, 0.7, 0.8)
    play(tr, "flute", D5, 1.3, 1.6, 0.85)
    play(tr, "bell", D6, 1.9, 1.1, 0.2, pan=0.2)
    play(tr, "pluck", D4, 1.85, 1.0, 0.4)


def sting_transition(tr):
    add(tr, noise_sw(3.0), 0.0, 0.0, 0.05)
    seq = [D5, A5, FS5, A5, D6, A5]
    for i, m in enumerate(seq):
        play(tr, "pluck", m, 0.2 + i * 0.34, 1.4, 0.5,
             pan=-0.4 + i * 0.16)
    add(tr, water_drop(880.0), 2.45, 0.25, 0.12)
    chord(tr, CH["G"], 1.6, 1.4, 0.15)


PIECES = [
    # stem, cueKey, nameVi, bpm, bars, builder, lp_hz, structure
    ("ben_mua", "MUSIC/ben_mua", "Bến Mưa · câu nhạc bỏ lửng", 72, 17,
     piece_ben_mua, None,
     "Theme statement: flute states the question phrase twice with a "
     "pluck echo an octave down; fragments; final bar leaves the "
     "hanging E over the tonic pad, so the loop itself never resolves."),
    ("thang_long", "MUSIC/thang_long", "Thăng Long · phố và dòng nước",
     92, 16, piece_thang_long, None,
     "Street arrangement of the theme: bell on every bar line, pluck "
     "arpeggios, shaker; the hanging phrase is answered casually by "
     "the tail in low pluck at bars 10-11."),
    ("boss_mang_cot", "MUSIC/boss_mang_cot", "Mãng Cốt · áp lực dòng",
     66, 10, piece_boss, None,
     "D minor transformation: motif reduced to a minor head fragment "
     "in low pluck over a heartbeat drum and D1 drone; one foreign "
     "F# bell at bar 8; the tail never comes."),
    ("quiet_discovery", "MUSIC/quiet_discovery", "Khoảng lặng khám phá",
     60, 16, piece_quiet, None,
     "Exploration silence per the direction doc: solo flute fragments "
     "and single bells separated by long near-silences, water drops; "
     "the second half of the question is heard once, still hanging."),
    ("lam_trieu", "MUSIC/lam_trieu", "Lâm Triều — Rừng nhớ tên", 90, 20,
     piece_lam_trieu, None,
     "Theme transposed to G major pentatonic; an ornamented flute "
     "restatement with neighbor-note pickups; leaf-tick shaker and "
     "sparse drops under a G/C/Em pad cycle."),
    ("sa_hoa", "MUSIC/sa_hoa", "Sa Hỏa — Lò và cát", 110, 20,
     piece_sa_hoa, None,
     "Theme mapped to A minor pentatonic, dry bright plucks, pad only "
     "on even bars, syncopated restatement (offset +0.5 beat), drum "
     "and shaker kept dry and sparse."),
    ("tran_son", "MUSIC/tran_son", "Trấn Sơn — Người qua cửa", 90, 15,
     piece_tran_son, None,
     "Bell-led stately form: the bell states the motif, a low flute "
     "answers, a drum marks every bar line; the final bar leaves a "
     "soft hanging E under the gate bell."),
    ("bach_uyen", "MUSIC/bach_uyen", "Bạch Uyên — Thành dưới triều",
     62, 15, piece_bach_uyen, 850.0,
     "Theme underwater: motif an octave down at half density over "
     "Bm/Em pads, whole mix low-passed at 850 Hz, slow bell marks "
     "and deep drops."),
    ("rift_finale", "MUSIC/rift_finale", "Ngũ Mạch — Năm dòng cùng chảy",
     100, 16, piece_finale, None,
     "Five streams: the motif head rises through five registers "
     "(low pluck, mid pluck, flute, bell), full question at bars "
     "11-12, then the withheld tail is played and the set's only "
     "full D-major close lands at bar 15."),
]


# ------------------------------------------------------------- render
def write_f32_wav(track: np.ndarray, path: Path):
    raw = np.ascontiguousarray(track, dtype="<f4").tobytes()
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le",
                        "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_f32le", str(path)],
                       input=raw, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-1000:])


def write_master_wav(track: np.ndarray, path: Path):
    raw = np.ascontiguousarray(track, dtype="<f4").tobytes()
    r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le",
                        "-ar", str(SR), "-ac", "2", "-i", "-",
                        "-c:a", "pcm_s24le", str(path)],
                       input=raw, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr.decode()[-1000:])


def encode_ogg(wav: Path, ogg: Path):
    run(["ffmpeg", "-y", "-v", "error", "-i", str(wav),
         "-c:a", "libvorbis", "-q:a", "5", str(ogg)])


def measure_loudnorm(path: Path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    start = err.rfind("{")
    if start < 0:
        raise RuntimeError(f"loudnorm gave no JSON for {path}")
    data = json.loads(err[start:err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def seam_stats(track: np.ndarray) -> dict:
    mono = track.mean(axis=1)
    n = int(0.1 * SR)
    return {
        "method": "mono 48kHz decode; head/tail = first/last 100 ms; "
                  "wrap jump = |last sample - first sample|; "
                  "indicator only, not a seamlessness PASS",
        "headRms": round(float(np.sqrt((mono[:n] ** 2).mean())), 6),
        "tailRms": round(float(np.sqrt((mono[-n:] ** 2).mean())), 6),
        "wrapJump": round(float(abs(mono[-1] - mono[0])), 6),
    }


def end_landing(track: np.ndarray, land_s: float = 0.25) -> np.ndarray:
    """Blend the final land_s toward the first sample's value so the
    loop point is sample-continuous (a standard loop crossfade
    construction). Returns (track, raw_jump) where raw_jump is the
    mono |last - first| step measured BEFORE the landing."""
    mono = track.mean(axis=1)
    raw = float(abs(mono[-1] - mono[0]))
    m = int(land_s * SR)
    w = (np.arange(m) / m) ** 2
    out = track.copy()
    out[-m:] = (out[-m:] * (1.0 - w[:, None])
                + out[0][None, :] * w[:, None])
    return out, round(raw, 6)


def gain_stage(track: np.ndarray, target_lufs: float, tp_ceiling: float,
               tag: str):
    """Two-pass loudness staging on the float track; returns the track
    scaled so the rendered file measures at the target."""
    tmpf = TMP / f"{tag}_measure.wav"
    for attempt in range(3):
        write_f32_wav(track, tmpf)
        lufs, tp = measure_loudnorm(tmpf)
        gain = min(target_lufs - lufs, tp_ceiling - tp)
        if abs(gain) < 0.15 or attempt == 2:
            return track, lufs, tp
        track = track * (10.0 ** (gain / 20.0))
    return track, lufs, tp


def file_entry(path: Path, rel: str, codec: str) -> dict:
    pr = probe(path)
    stream = pr["streams"][0]
    lufs, tp = measure_loudnorm(path)
    return {
        "path": rel,
        "codec": codec,
        "sampleRateHz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "durationSeconds": round(float(pr["format"]["duration"]), 4),
        "sizeBytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "integratedLufs": round(lufs, 2),
        "truePeakDbtp": round(tp, 2),
    }


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
    assert -23.5 <= m_entry["integratedLufs"] <= -20.5, (stem,
                                                         m_entry)
    assert m_entry["truePeakDbtp"] <= -6.0, (stem, m_entry)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "MUSIC",
        "loop": True,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "tempoBpm": bpm, "bars": bars, "mode": "see structure",
            "motif": "Ben Mua leitmotif: D major pentatonic question "
                     "phrase hanging on scale degree 2; tail withheld "
                     "unless the structure says otherwise",
            "structure": structure,
            "rendering": "procedural synthesis (additive pluck/flute/"
                         "bell/pad/bass + noise percussion), authored "
                         "in build_composed_music.py; no external "
                         "samples",
        },
        "master": m_entry, "runtime": r_entry,
        "seam": {**seam_stats(tr), "wrapJumpRaw": raw_jump,
                 "landingNote": "wrapJump is measured after a 0.25 s "
                                "end-landing blend to the first sample "
                                "(loop crossfade construction); "
                                "wrapJumpRaw is the step before it"},
    }


def render_stinger(stem: str, builder) -> dict:
    cue_key, name_vi = STINGERS[stem]
    tr = new_track(3.0)
    builder(tr)
    tr = room(tr, 0.12)
    # Guarantee a clean ending (stingers do not loop).
    fade = int(0.15 * SR)
    tr[-fade:] *= np.linspace(1.0, 0.0, fade)[:, None]
    tr, _, _ = gain_stage(tr, -25.0, -6.0, stem)
    master = MASTER_DIR / "cinema" / f"{stem}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    write_master_wav(tr, master)
    runtime = RUNTIME_DIR / "cinema" / f"{stem}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    encode_ogg(master, runtime)
    m_entry = file_entry(master, f"Art_Source/Audio/Muse/COMPOSED/"
                         f"cinema/{stem}.wav", "pcm_s24le")
    r_entry = file_entry(runtime, f"ClientGodot/assets/audio/composed/"
                         f"cinema/{stem}.ogg", "vorbis")
    assert -27.0 <= m_entry["integratedLufs"] <= -23.0, (stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -5.0, (stem, m_entry)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "CINEMA_STINGER",
        "loop": False,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "motif": "derived from the Ben Mua leitmotif (see pack "
                     "notes)",
            "rendering": "procedural synthesis, authored in "
                         "build_composed_music.py; no external samples",
        },
        "master": m_entry, "runtime": r_entry,
    }


STINGER_BUILDERS = {"reveal": sting_reveal, "tension": sting_tension,
                    "resolve": sting_resolve,
                    "transition": sting_transition}


def save_pack(by_key: dict):
    """Write the delivery manifest from whatever cues exist so far.
    Called after every single render: a killed run still leaves a
    valid partial manifest on disk."""
    order = [spec[1] for spec in PIECES] + [v[0] for v in
                                            STINGERS.values()]
    cues = [by_key[k] for k in order if k in by_key]
    n_music = sum(1 for c in cues if c["kind"] == "MUSIC")
    n_sting = sum(1 for c in cues if c["kind"] == "CINEMA_STINGER")
    pack = {
        "packId": "NGM_MUSIC_COMPOSED_V1",
        "checkpoint": "MEDIA-02 checkpoint 26 - original composed music "
                      "+ cinema stingers (Goi 30 item 7)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "f0859d0",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: melodies, harmony and "
                      "arrangements authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_music.py and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes. These 13 cues are NEW audio and "
                      "are counted separately from the 541 ported "
                      "PackV1 files of checkpoints 07/08, which keep "
                      "their own provenance and are untouched.",
        "counts": {"music": n_music, "cinemaStingers": n_sting,
                   "total": len(cues)},
        "cues": cues,
        "notes": [
            "Adoption is a presentation-adapter decision (Codex): the "
            "composed cues are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ and do NOT replace the "
            "ported PackV1 files or their cue bindings.",
            "Music cues loop by construction (1.5 s tail wrap); the "
            "seam block records the checkpoint-07 indicator, not a "
            "seamlessness PASS. No ear audition has been done; "
            "loudness/true-peak are measured from real bytes.",
            "The composition concept follows the audio direction doc: "
            "Ben Mua's theme is a phrase left hanging ('cau nhac bo "
            "lung'); the answering tail is withheld everywhere except "
            "the resolve stinger and rift_finale.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['total']} composed cues")


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
        print(f"OK {entry['cueKey']}: {entry['master']['durationSeconds']} s "
              f"master {entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP, "
              f"wrap jump {entry['seam']['wrapJump']}", flush=True)
    for stem, builder in STINGER_BUILDERS.items():
        if only is not None and stem not in only:
            continue
        entry = render_stinger(stem, builder)
        by_key[entry["cueKey"]] = entry
        save_pack(by_key)
        print(f"OK {entry['cueKey']}: {entry['master']['durationSeconds']} s "
              f"master {entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
