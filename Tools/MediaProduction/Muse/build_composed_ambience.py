#!/usr/bin/env python3
"""MEDIA-02 checkpoint 30: ORIGINAL composed ambience (all 13 cues).

Checkpoint 26 composed the 9 music cues + 4 cinema stingers; ambience
stayed the ported PackV1 renders (checkpoint 07 measured them, 541
ported files keep their own provenance). This checkpoint composes the
remaining set -- all 13 AMBIENCE/* cues -- from scratch, delivered in
parallel, with the ported pack untouched. Adoption is Codex's
presentation-adapter decision, exactly as for the composed music.

Every cue is 16.0 s (the ported ambience length), stereo 48 kHz,
procedural synthesis only: filtered noise beds, slow gust/swell
envelopes, and sparse deterministic events (droplets, crackle, clinks,
cricket chirps). No external samples, no ported bytes, no voices at
all. The crowd beds (thang_long_crowd, city_night) are band-limited
noise with slowly wandering formant-like bands -- they cannot produce
intelligible words, by construction.

Loudness targets are the ported cues' measured integrated LUFS from
checkpoint 07, so a composed bed sits at the same mix level the P0
draft mixes were designed around. Loudness is measured from the real
rendered bytes with ffmpeg loudnorm (the checkpoint 07 method); each
cue is gain-staged to its target in at most 3 passes and the recorded
values are the final measured ones. Loops use the checkpoint 26
construction: the last 1.5 s of bed is wrapped over the head with an
equal-power crossfade, and the final 0.25 s is blended to the first
sample. Sparse events are scheduled only inside [0.5, 14.0] s so the
wrapped tail stays bed-only. The seam indicator is recorded, not
claimed as a PASS. No ear audition has been done.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/ambience/<name>.wav  (master, 48k/24b)
  ClientGodot/assets/audio/composed/ambience/<name>.ogg (runtime)
  Implementation/Content/Audio/Deliveries/AMBIENCE_COMPOSED_pack_v1.json
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

ROOT = Path(__file__).resolve().parents[3]
SR = 48000
DUR = 16.0
MASTER_DIR = ROOT / "Art_Source/Audio/Muse/COMPOSED"
RUNTIME_DIR = ROOT / "ClientGodot/assets/audio/composed"
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "AMBIENCE_COMPOSED_pack_v1.json")
TMP = Path("/tmp/composed_ambience")
TMP.mkdir(parents=True, exist_ok=True)

N = int(DUR * SR)
T = np.arange(N) / SR


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n"
                           f"{r.stderr[-1500:]}")
    return r


# ---------------------------------------------------------------- filters
def _sos(kind, freq, order=4):
    if kind == "low":
        return butter(order, freq, btype="lowpass", fs=SR, output="sos")
    if kind == "high":
        return butter(order, freq, btype="highpass", fs=SR, output="sos")
    return butter(order, freq, btype="bandpass", fs=SR, output="sos")


def filt(x, kind, freq, order=4):
    return sosfilt(_sos(kind, freq, order), x)


def lowpass(x, cutoff):
    return filt(x, "low", cutoff)


def highpass(x, cutoff):
    return filt(x, "high", cutoff)


def bandpass(x, lo, hi):
    return filt(x, "band", (lo, hi))


def noise(rng, n=N):
    return rng.standard_normal(n)


def bed(rng, kind, freq, gain=1.0, seeds=(0, 1)):
    """Stereo filtered-noise bed, decorrelated per channel."""
    out = np.zeros((N, 2))
    for ch, sd in enumerate(seeds):
        r = np.random.default_rng(rng.integers(0, 2 ** 31) + sd * 7919)
        x = noise(r)
        if kind == "low":
            x = lowpass(x, freq)
        elif kind == "high":
            x = highpass(x, freq)
        else:
            x = bandpass(x, freq[0], freq[1])
        x = x / (np.max(np.abs(x)) + 1e-9)
        out[:, ch] = x * gain
    return out


def swell(depth, freqs=(0.05, 0.11), phases=(0.0, 1.7)):
    """Slow gain envelope in [1-depth, 1+depth], mean ~1."""
    env = np.ones(N)
    for f, p in zip(freqs, phases):
        env = env + depth * 0.5 * np.sin(2 * np.pi * f * T + p)
    return env[:, None]


def apply_env(track, env):
    return track * env


def normalize(track, peak=0.9):
    m = np.max(np.abs(track)) + 1e-9
    return track / m * peak


# ---------------------------------------------------------------- events
def add_event(track, sig, at_s, pan=0.0, gain=1.0):
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


def droplet(rng, f0=None):
    """One falling-pitch water blip (sine, ~0.16 s)."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f0 = f0 or (600.0 + rng.random() * 600.0)
    f = f0 * np.exp(-t * 14.0) + 180.0
    phase = 2 * np.pi * np.cumsum(f) / SR
    env = np.sin(np.pi * np.minimum(1.0, t / 0.16)) ** 2
    return np.sin(phase) * env * 0.8


def tick(rng, dur=0.03, lo=2500.0, hi=5000.0):
    """Short filtered-noise tick (rain droplet impact)."""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    x = bandpass(x, lo, hi)
    env = np.exp(-np.arange(n) / (0.008 * SR))
    x = x * env
    return x / (np.max(np.abs(x)) + 1e-9)


def crackle_tick(rng, dur=0.025):
    n = int(dur * SR)
    x = highpass(rng.standard_normal(n), 3000.0)
    env = np.exp(-np.arange(n) / (0.006 * SR))
    x = x * env
    return x / (np.max(np.abs(x)) + 1e-9)


def clink(rng, freq=None):
    """Short inharmonic metallic clink (~0.35 s)."""
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f0 = freq or (1800.0 + rng.random() * 800.0)
    sig = np.zeros(n)
    for ratio, g, tau in ((1.0, 1.0, 0.22), (2.71, 0.45, 0.12),
                          (4.95, 0.2, 0.06)):
        sig += g * np.sin(2 * np.pi * f0 * ratio * t) * np.exp(-t / tau)
    return sig / (np.max(np.abs(sig)) + 1e-9)


def chirp_group(rng):
    """One cricket triplet: three 4.2 kHz pulses, ~0.3 s total."""
    out = np.zeros(int(0.3 * SR))
    for i in range(3):
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        pulse = np.sin(2 * np.pi * 4200.0 * t) * np.sin(np.pi * t / 0.05)
        s = int(i * 0.09 * SR)
        out[s:s + n] += pulse
    return out / (np.max(np.abs(out)) + 1e-9)


def thump(rng):
    """Soft wooden knock (~0.12 s)."""
    n = int(0.12 * SR)
    t = np.arange(n) / SR
    f = 90.0 + 60.0 * np.exp(-t * 30.0)
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * np.exp(-t * 28.0)
    return sig / (np.max(np.abs(sig)) + 1e-9)


# ---------------------------------------------------------------- pieces
def piece_rain_light(tr, rng):
    tr += apply_env(bed(rng, "low", 1800.0, 0.55), swell(0.15))
    for _ in range(36):
        add_event(tr, tick(rng), 0.5 + rng.random() * 13.5,
                  float(rng.uniform(-0.7, 0.7)),
                  float(rng.uniform(0.04, 0.10)))


def piece_rain_heavy(tr, rng):
    tr += apply_env(bed(rng, "low", 3000.0, 0.6), swell(0.12))
    tr += bed(rng, "low", 120.0, 0.18)  # low rumble
    for _ in range(110):
        add_event(tr, tick(rng, 0.025, 2000.0, 4500.0),
                  0.5 + rng.random() * 13.5,
                  float(rng.uniform(-0.8, 0.8)),
                  float(rng.uniform(0.05, 0.12)))


def piece_river_shore(tr, rng):
    tr += apply_env(bed(rng, "low", 500.0, 0.5), swell(0.18))
    lap = bed(rng, "band", (700.0, 1200.0), 0.35)
    tr += apply_env(lap, swell(0.4, (0.08, 0.13), (0.4, 2.2)))
    for t0 in (2.0, 5.1, 8.4, 11.2, 14.0):
        n = int(1.2 * SR)
        tt = np.arange(n) / SR
        env = np.sin(np.pi * np.minimum(1.0, tt / 1.2)) ** 2
        seg = bandpass(rng.standard_normal(n), 500.0, 1000.0)
        seg = seg / (np.max(np.abs(seg)) + 1e-9) * env * 0.22
        add_event(tr, seg, t0, 0.0, 1.0)


def piece_underwater(tr, rng):
    tr += apply_env(bed(rng, "low", 280.0, 0.6), swell(0.2, (0.04, 0.09)))
    pulse = (np.sin(2 * np.pi * 55.0 * T)
             * (0.6 + 0.4 * np.sin(2 * np.pi * 0.1 * T)))
    tr[:, 0] += pulse * 0.05
    tr[:, 1] += pulse * 0.05


def piece_waterfall(tr, rng):
    tr += apply_env(bed(rng, "low", 900.0, 0.65), swell(0.1))
    tr += bed(rng, "high", 80.0, 0.15)  # low-end weight
    tr += bed(rng, "high", 4000.0, 0.06)  # mist hiss


def piece_wind_canopy(tr, rng):
    gust = swell(0.45, (0.06, 0.11), (0.2, 1.9))
    tr += apply_env(bed(rng, "band", (400.0, 1000.0), 0.55), gust)
    rustle = highpass(rng.standard_normal(N), 5000.0)
    rustle = rustle / (np.max(np.abs(rustle)) + 1e-9)
    gate = np.clip(gust[:, 0] - 0.9, 0.0, None) * 2.0
    tr[:, 0] += rustle * gate * 0.10
    tr[:, 1] += rustle * gate * 0.10


def piece_desert_wind(tr, rng):
    gust = swell(0.4, (0.09, 0.17), (0.9, 0.3))
    tr += apply_env(bed(rng, "band", (900.0, 1600.0), 0.55), gust)
    for _ in range(14):
        add_event(tr, tick(rng, 0.05, 3000.0, 6000.0),
                  0.5 + rng.random() * 13.5,
                  float(rng.uniform(-0.6, 0.6)), 0.05)


def piece_mountain_wind(tr, rng):
    tr += apply_env(bed(rng, "band", (250.0, 450.0), 0.5),
                    swell(0.35, (0.05, 0.08), (0.0, 1.2)))
    # Slowly wandering whistle partials (deterministic drift).
    wander = 220.0 + 15.0 * np.sin(2 * np.pi * 0.05 * T + 0.6)
    ph = 2 * np.pi * np.cumsum(wander) / SR
    tr[:, 0] += np.sin(ph) * 0.06
    tr[:, 1] += np.sin(ph + 0.4) * 0.06
    tr += bed(rng, "high", 6000.0, 0.03)  # cold shimmer


def piece_cave_drips(tr, rng):
    tr += bed(rng, "low", 200.0, 0.16)  # near-quiet bed
    times = [1.2, 2.9, 4.4, 6.1, 7.8, 9.3, 10.9, 12.4, 13.8]
    for t0 in times:
        add_event(tr, droplet(rng), t0,
                  float(rng.uniform(-0.6, 0.6)),
                  float(rng.uniform(0.25, 0.45)))
    n = int(2.0 * SR)
    tt = np.arange(n) / SR
    stone = np.sin(2 * np.pi * 90.0 * tt) * np.exp(-tt / 0.7) * 0.12
    add_event(tr, stone, 8.0, 0.0, 1.0)


def piece_forge(tr, rng):
    tr += bed(rng, "low", 150.0, 0.35)  # fire rumble
    for _ in range(180):
        add_event(tr, crackle_tick(rng), 0.5 + rng.random() * 13.5,
                  float(rng.uniform(-0.7, 0.7)),
                  float(rng.uniform(0.03, 0.09)))
    for t0 in (1.6, 4.2, 7.0, 10.5, 13.2):
        add_event(tr, clink(rng), t0, float(rng.uniform(-0.5, 0.5)),
                  float(rng.uniform(0.10, 0.18)))


def piece_thang_long_crowd(tr, rng):
    # Murmur = filtered noise only. Two formant-like bands wander
    # slowly and independently; no voice, no words, by construction.
    low_band = apply_env(bed(rng, "band", (300.0, 900.0), 0.5),
                         swell(0.3, (0.05, 0.08), (0.1, 2.0)))
    high_band = apply_env(bed(rng, "band", (900.0, 2500.0), 0.32),
                          swell(0.35, (0.07, 0.12), (1.5, 0.4)))
    tr += low_band + high_band
    for t0 in (3.1, 7.6, 11.8):
        add_event(tr, thump(rng), t0, float(rng.uniform(-0.4, 0.4)),
                  0.12)


def piece_city_night(tr, rng):
    tr += apply_env(bed(rng, "band", (300.0, 700.0), 0.22),
                    swell(0.25, (0.04, 0.07)))
    hum = (np.sin(2 * np.pi * 50.0 * T)
           + 0.4 * np.sin(2 * np.pi * 100.0 * T))
    tr[:, 0] += hum * 0.03
    tr[:, 1] += hum * 0.03
    for t0 in (2.2, 6.8, 11.4):
        add_event(tr, chirp_group(rng), t0,
                  float(rng.uniform(-0.5, 0.5)), 0.10)


def piece_rift(tr, rng):
    # Low D drone (the leitmotif root) with a slow beating detune and
    # inharmonic shimmer partials a tritone away: the rift is wrong.
    drone = (np.sin(2 * np.pi * 73.42 * T)
             + 0.7 * np.sin(2 * np.pi * 110.0 * T)
             + 0.5 * np.sin(2 * np.pi * 74.0 * T))
    tr[:, 0] += drone * 0.16
    tr[:, 1] += drone * 0.16
    shim = (np.sin(2 * np.pi * 311.13 * T)
            + 0.6 * np.sin(2 * np.pi * 466.16 * T))
    tr += apply_env(np.stack([shim, shim], axis=1) * 0.035,
                    swell(0.4, (0.06, 0.1)))
    tr += bed(rng, "low", 300.0, 0.12)


# cueKey, nameVi, stem, target LUFS (ported, checkpoint 07), builder, note
CUES = [
    ("AMBIENCE/rain_light", "Mưa nhẹ", "rain_light", -27.48,
     piece_rain_light,
     "Light rain: low-passed noise bed + 36 sparse droplet ticks."),
    ("AMBIENCE/rain_heavy", "Mưa nặng hạt", "rain_heavy", -27.47,
     piece_rain_heavy,
     "Heavy rain: denser bed + low rumble + 110 droplet ticks."),
    ("AMBIENCE/river_shore", "Nước ven bờ", "river_shore", -29.53,
     piece_river_shore,
     "River shore: low bed + lapping band noise + 5 soft lap swells."),
    ("AMBIENCE/underwater", "Dòng nước sâu", "underwater", -33.02,
     piece_underwater,
     "Underwater: heavy low-pass bed + faint 55 Hz pulse; quietest."),
    ("AMBIENCE/waterfall", "Thác nước", "waterfall", -29.31,
     piece_waterfall,
     "Waterfall: broad low-pass body + low-end weight + mist hiss."),
    ("AMBIENCE/wind_canopy", "Gió qua tán cây", "wind_canopy", -29.55,
     piece_wind_canopy,
     "Wind through canopy: gusted band noise + leaf rustle at peaks."),
    ("AMBIENCE/desert_wind", "Gió Sa Hỏa", "desert_wind", -29.57,
     piece_desert_wind,
     "Desert wind: drier, thinner band + faster gusts + sand hiss."),
    ("AMBIENCE/mountain_wind", "Gió tháp", "mountain_wind", -29.56,
     piece_mountain_wind,
     "Mountain wind: narrow low whistle + wandering sine partials."),
    ("AMBIENCE/cave_drips", "Hang nhỏ giọt", "cave_drips", -29.54,
     piece_cave_drips,
     "Cave drips: near-quiet bed + 9 droplets + one low stone tone."),
    ("AMBIENCE/forge", "Lò rèn", "forge", -29.50, piece_forge,
     "Forge: fire rumble + 180 crackle ticks + 5 metallic clinks."),
    ("AMBIENCE/thang_long_crowd", "Phố Thăng Long", "thang_long_crowd",
     -30.34, piece_thang_long_crowd,
     "Street crowd: filtered-noise murmur only (no voices, no words) "
     "+ soft wooden knocks."),
    ("AMBIENCE/city_night", "Phố đêm", "city_night", -30.34,
     piece_city_night,
     "Night city: quiet murmur + distant 50 Hz hum + cricket triplets."),
    ("AMBIENCE/rift", "Mạch nghịch", "rift", -30.48, piece_rift,
     "Rift: low D drone with beating detune + tritone shimmer."),
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


def tail_wrap(track: np.ndarray, wrap_s: float = 1.5) -> np.ndarray:
    """Loop construction (checkpoint 26): the final wrap_s of bed is
    mixed over the head (fading out) and faded to zero at the file
    end, so in a loop the bed continues across the seam instead of
    being cut. Total length is unchanged."""
    n = int(wrap_s * SR)
    if len(track) <= 2 * n:
        return track
    fade_out = np.linspace(1.0, 0.0, n)[:, None]
    out = track.copy()
    out[:n] = track[:n] + track[-n:] * fade_out
    out[-n:] = track[-n:] * fade_out
    return out


def end_landing(track: np.ndarray, land_s: float = 0.25):
    """Blend the final land_s toward the first sample's value so the
    loop point is sample-continuous. Returns (track, raw_jump) where
    raw_jump is the mono |last - first| step BEFORE the landing."""
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


def render_cue(spec, idx) -> dict:
    cue_key, name_vi, stem, target_lufs, builder, note = spec
    rng = np.random.default_rng(3000 + idx)
    tr = np.zeros((N, 2), dtype=np.float64)
    builder(tr, rng)
    tr = normalize(tr, 0.9)
    tr = tail_wrap(tr, 1.5)
    tr, raw_jump = end_landing(tr, 0.25)
    tr, _, _ = gain_stage(tr, target_lufs, -7.0, stem)
    master = MASTER_DIR / "ambience" / f"{stem}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    write_master_wav(tr, master)
    runtime = RUNTIME_DIR / "ambience" / f"{stem}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    encode_ogg(master, runtime)
    m_entry = file_entry(master, f"Art_Source/Audio/Muse/COMPOSED/"
                         f"ambience/{stem}.wav", "pcm_s24le")
    r_entry = file_entry(runtime, f"ClientGodot/assets/audio/composed/"
                         f"ambience/{stem}.ogg", "vorbis")
    assert abs(m_entry["durationSeconds"] - DUR) < 0.05, stem
    assert abs(m_entry["integratedLufs"] - target_lufs) <= 1.5, (
        stem, m_entry)
    assert m_entry["truePeakDbtp"] <= -6.0, (stem, m_entry)
    return {
        "cueKey": cue_key, "nameVi": name_vi, "kind": "AMBIENCE",
        "loop": True,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "composition": {
            "durationSeconds": DUR,
            "targetLufsPorted": target_lufs,
            "structure": note,
            "rendering": "procedural synthesis (filtered-noise beds, "
                         "slow gust/swell envelopes, sparse deterministic "
                         "events), authored in "
                         "build_composed_ambience.py; no external "
                         "samples, no voices",
        },
        "master": m_entry, "runtime": r_entry,
        "seam": {**seam_stats(tr), "wrapJumpRaw": raw_jump,
                 "landingNote": "wrapJump is measured after a 0.25 s "
                                "end-landing blend to the first sample "
                                "(loop crossfade construction); "
                                "wrapJumpRaw is the step before it"},
    }


def save_pack(by_key: dict):
    """Write the delivery manifest from whatever cues exist so far.
    Called after every single render: a killed run still leaves a
    valid partial manifest on disk."""
    order = [c[0] for c in CUES]
    cues = [by_key[k] for k in order if k in by_key]
    pack = {
        "packId": "NGM_AMBIENCE_COMPOSED_V1",
        "checkpoint": "MEDIA-02 checkpoint 30 - original composed "
                      "ambience (all 13 AMBIENCE/* cues)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "f0859d0",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: ambience beds and "
                      "events authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_ambience.py and rendered by "
                      "procedural synthesis. No external samples, no "
                      "ported bytes, no voices. These 13 cues are NEW "
                      "audio and are counted separately from the 541 "
                      "ported PackV1 files of checkpoints 07/08, which "
                      "keep their own provenance and are untouched.",
        "counts": {"ambience": len(cues), "total": len(cues)},
        "cues": cues,
        "notes": [
            "Adoption is a presentation-adapter decision (Codex): the "
            "composed cues are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ambience/ and do NOT "
            "replace the ported PackV1 files or their cue bindings.",
            "Ambience cues loop by construction (1.5 s tail wrap); the "
            "seam block records the checkpoint-07 indicator, not a "
            "seamlessness PASS. No ear audition has been done; "
            "loudness/true-peak are measured from real bytes.",
            "Loudness targets are the ported cues' measured integrated "
            "LUFS from checkpoint 07, so a composed bed sits at the "
            "same mix level the P0 draft mixes were designed around.",
            "Crowd beds are filtered noise only: no voice, no words, "
            "no intelligible speech is possible by construction.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['total']} composed cues", flush=True)


def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))
    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}
    for idx, spec in enumerate(CUES):
        if only is not None and spec[2] not in only:
            continue
        entry = render_cue(spec, idx)
        by_key[entry["cueKey"]] = entry
        save_pack(by_key)
        print(f"OK {entry['cueKey']}: "
              f"{entry['master']['durationSeconds']} s master "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP, "
              f"runtime {entry['runtime']['integratedLufs']} LUFS / "
              f"{entry['runtime']['truePeakDbtp']} dBTP, "
              f"wrap jump {entry['seam']['wrapJump']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
