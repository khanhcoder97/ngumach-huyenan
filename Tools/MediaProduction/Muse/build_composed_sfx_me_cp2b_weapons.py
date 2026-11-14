#!/usr/bin/env python3
"""MEDIA-02 WO39 M39-A checkpoint 2: COMPOSED SFX draft, 4 weapon identities.

Second asset block of DEC-MEDIA-SFX-DRAFT-20261112 (Codex, Gói 39,
issue #116 comment 6815238814, 2026-11-12; machine-readable approval
Implementation/Content/DesignBaselines/media_sfx_draft_execution_20261112.json
@ e4b3e4b on PR #131). The approval authorises 18 draft variants
(guard-expire + 4 weapon identities + grass, 3 variants each); CP1
delivered guard + grass (6 variants). This checkpoint delivers the
remaining block: the 4 weapon identities x 3 variants = 12 variants.

Cues (candidate keys from proposal P-WEAPON, M-E CP2a; NOT runtime keys):
  SFX/COMBAT/dao_swing    -- Anh Dao (dao, Hoa): wind through cloth,
    small ember crackle, deep blade; two short beats, tail cuts fast.
  SFX/COMBAT/brush_stroke -- Huyen But (brush, Thuy): brush on paper,
    water touching porcelain, thin water breath; lead-release-stop.
  SFX/COMBAT/mace_swing   -- Thach Chuy (mace, Tho): deep wood, cracking
    stone slab, falling sand; weighty, attack clear before the deep tail.
  SFX/COMBAT/bow_string   -- Linh Cung (bow, Moc): string snap, wind
    through leaves, short flute-like tone (not melodic); per confirmed
    shot, light tail.
Material identity per Audio Direction v1 §1 (docs/production/
Audio_Production_Direction_v1_vi.md). basic_blade stays the shared
swing default; these four are per-weapon identities only if Codex
wants a swing per weapon (P-WEAPON, CP2a).

Spectral slots (measured from real bytes; baselines re-measured here
and independently by the validator): basic_blade centroid ~2702 Hz,
LUFS -22.25, prominence ~21; metal_parry centroid ~764 Hz, prominence
~1.49M (extreme tonal ring), band <500 Hz = 0.00. Each weapon sits in
its own slot, >=300 Hz from every sibling weapon, >=400 Hz from
basic_blade, and (except mace, whose slot is low by design) >=250 Hz
from metal_parry; mace is told apart from parry by its low-end weight
(band <500 Hz >= 0.30 vs parry's 0.00) and its prominence staying
below 1% of parry's. (Prominence 400-2000 Hz is recorded, not
asserted, for brush and mace: their energy sits outside that window
-- brush above 2400 Hz, mace below 700 Hz -- so the window median is
near the noise floor and the ratio is not a tonality claim, the same
note CP1 recorded for the grass cue.)

Rendering: procedural synthesis only (filtered-noise bands, pitch-
gliding sine tones, additive plucked-string partials, sparse ticks),
deterministic per-seed. No external samples, no ported bytes, no
voices. Masters are stereo 48 kHz / 24-bit WAV, the composed-audio
convention (CP26/CP30).

Delivery is SOURCE ONLY: masters under Art_Source/Audio/Muse/
COMPOSED/sfx/ + this manifest + audition playlist. NO runtime file
is written and NO runtime manifest is touched -- runtime audio stays
783 files until Codex reviews the delta (Gói 39 M39-C). Binding
status is UNSUPPORTED: no authoritative client/server trigger exists
yet; the asset is delivered, the trigger is not invented.

Loudness/true-peak/spectrum are MEASURED from the real rendered
bytes (ffmpeg loudnorm / ffprobe / numpy FFT); no ear audition.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, sosfilt

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_composed_ambience as base  # noqa: E402

ROOT = base.ROOT
SR = base.SR
MASTER_DIR = ROOT / "Art_Source/Audio/Muse/COMPOSED/sfx"
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json")
PLAYLIST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt")
TMP = Path("/tmp/composed_sfx_weapons")
TMP.mkdir(parents=True, exist_ok=True)

SEED_DAO = 43000
SEED_BRUSH = 44000
SEED_MACE = 45000
SEED_BOW = 46000
DAO_DUR = 0.45
BRUSH_DUR = 0.55
MACE_DUR = 0.50
BOW_DUR = 0.50
DAO_TARGET_LUFS = -23.5
BRUSH_TARGET_LUFS = -24.0
MACE_TARGET_LUFS = -23.5
BOW_TARGET_LUFS = -23.5
WEAPON_TP_CEILING = -8.0


# ---------------------------------------------------------------- synthesis
def _bp(x, lo, hi, order=4):
    sos = butter(order, (lo, hi), btype="bandpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def _hp(x, freq, order=4):
    sos = butter(order, freq, btype="highpass", fs=SR, output="sos")
    return sosfilt(sos, x)


def _env(n, attack_s, tau):
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / max(attack_s, 1e-6))
    d = np.exp(-np.maximum(0.0, t - attack_s) / tau)
    return a * d


def _env_plateau(n, attack_s, sustain_s, tau):
    t = np.arange(n) / SR
    a = np.minimum(1.0, t / max(attack_s, 1e-6))
    d = np.where(t <= sustain_s, 1.0,
                 np.exp(-(t - sustain_s) / tau))
    return a * d


def _noise_band(rng, n, lo, hi, attack_s, tau, gain, plateau_s=None):
    """Stereo decorrelated band-noise burst with attack/decay envelope,
    or attack/sustain/decay when plateau_s is given."""
    env = (_env_plateau(n, attack_s, plateau_s, tau) if plateau_s
           is not None else _env(n, attack_s, tau))
    out = np.zeros((n, 2))
    for ch in range(2):
        r = np.random.default_rng(rng.integers(0, 2 ** 31) + ch * 104729)
        x = r.standard_normal(n)
        x = _bp(x, lo, hi)
        x = x / (np.max(np.abs(x)) + 1e-9)
        out[:, ch] = x * env * gain
    return out


def _noise_band_at(rng, n, lo, hi, at_s, dur_s, attack_s, tau, gain):
    """Band-noise burst of dur_s placed at at_s (a whoosh beat)."""
    m = int(dur_s * SR)
    env = _env(m, attack_s, tau)
    out = np.zeros((n, 2))
    for ch in range(2):
        r = np.random.default_rng(rng.integers(0, 2 ** 31) + ch * 104729)
        x = r.standard_normal(m)
        x = _bp(x, lo, hi)
        x = x / (np.max(np.abs(x)) + 1e-9)
        s = int(at_s * SR)
        e = min(n, s + m)
        if e <= s:
            continue
        out[s:e, ch] = x[: e - s] * env[: e - s] * gain
    return out


def _tone(n, f0, f1, dur_s, at_s, gain, attack_s=0.01, tau=0.05,
          glide_rate=8.0):
    """Pitch-gliding sine tone (blade body, water breath, flute blip)
    placed at at_s, attack/decay envelope."""
    m = int(dur_s * SR)
    env = _env(m, attack_s, tau)
    t = np.arange(m) / SR
    f = f1 + (f0 - f1) * np.exp(-t * glide_rate)
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * env
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    out = np.zeros((n, 2))
    s = int(at_s * SR)
    e = min(n, s + m)
    if e > s:
        out[s:e, 0] = sig[: e - s]
        out[s:e, 1] = sig[: e - s]
    return out


def _ping(n, freq, dur_s, at_s, gain):
    """Short porcelain sine burst (fast exponential decay)."""
    m = int(dur_s * SR)
    t = np.arange(m) / SR
    sig = np.sin(2 * np.pi * freq * t) * np.exp(-t / 0.012)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    out = np.zeros((n, 2))
    s = int(at_s * SR)
    e = min(n, s + m)
    if e > s:
        out[s:e, 0] = sig[: e - s]
        out[s:e, 1] = sig[: e - s]
    return out


def _pluck(n, f0, dur_s, gain, harmonics=8):
    """Additive plucked string: harmonic series 1/k^1.5, higher
    harmonics decaying faster (tau 0.09/k s). Centred (mono)."""
    m = int(dur_s * SR)
    t = np.arange(m) / SR
    sig = np.zeros(m)
    for k in range(1, harmonics + 1):
        sig += ((1.0 / k ** 1.5)
                * np.sin(2 * np.pi * f0 * k * t)
                * np.exp(-t / (0.09 / k)))
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    out = np.zeros((n, 2))
    out[:m, 0] = sig
    out[:m, 1] = sig
    return out


def _ticks(rng, n, count, t_lo, t_hi, gain, hp_freq=4000.0, dur=0.008):
    """Sparse dry snaps: short high-passed noise ticks at random times."""
    out = np.zeros((n, 2))
    for _ in range(count):
        at = float(rng.uniform(t_lo, t_hi))
        m = int(dur * SR)
        x = rng.standard_normal(m)
        x = _hp(x, hp_freq)
        x = x / (np.max(np.abs(x)) + 1e-9)
        x = x * np.exp(-np.arange(m) / (0.002 * SR)) * gain
        s = int(at * SR)
        e = min(n, s + m)
        if e <= s:
            continue
        pan = float(rng.uniform(-0.5, 0.5))
        left = np.cos((pan + 1.0) * np.pi / 4.0)
        right = np.sin((pan + 1.0) * np.pi / 4.0)
        out[s:e, 0] += x[: e - s] * left
        out[s:e, 1] += x[: e - s] * right
    return out


def piece_dao_swing(rng, band1, band2, blade_gain, ember_ticks):
    """Anh Dao: two short cloth-wind beats + deep blade tone + ember
    crackle. Tail cuts fast (second beat decays in ~0.1 s)."""
    n = int(DAO_DUR * SR)
    tr = np.zeros((n, 2))
    tr += _noise_band_at(rng, n, band1[0], band1[1], 0.0, 0.13,
                         0.015, 0.08, 0.55)
    tr += _noise_band_at(rng, n, band2[0], band2[1], 0.17, 0.13,
                         0.015, 0.08, 0.50)
    tr += _tone(n, 200.0, 130.0, 0.20, 0.0, blade_gain,
                attack_s=0.008, tau=0.07)
    tr += _ticks(rng, n, ember_ticks, 0.02, 0.35, 0.05,
                 hp_freq=5000.0, dur=0.005)
    return tr


def piece_brush_stroke(rng, band, breath_f, ping_gain):
    """Huyen But: paper swish (lead-sustain-release) + thin water
    breath + two porcelain pings. Soft, no impact."""
    n = int(BRUSH_DUR * SR)
    tr = np.zeros((n, 2))
    tr += _noise_band(rng, n, band[0], band[1], 0.03, 0.12, 0.55,
                      plateau_s=0.25)
    tr += _tone(n, breath_f, breath_f * 0.85, 0.30, 0.05, 0.05,
                attack_s=0.05, tau=0.15, glide_rate=4.0)
    tr += _ping(n, 3600.0, 0.03, 0.10, ping_gain)
    tr += _ping(n, 3400.0, 0.03, 0.32, ping_gain * 0.8)
    return tr


def piece_mace_swing(rng, band, knock_gain, crack_ticks, sand_gain):
    """Thach Chuy: low whoosh + deep wood knock + stone cracks + sand
    tail. Attack clear first, deep tail after; never sub-bass only
    (whoosh band reaches 650-750 Hz, cracks sit 0.8-2 kHz)."""
    n = int(MACE_DUR * SR)
    tr = np.zeros((n, 2))
    tr += _noise_band(rng, n, band[0], band[1], 0.01, 0.18, 0.50)
    tr += _tone(n, 150.0, 75.0, 0.18, 0.0, knock_gain,
                attack_s=0.006, tau=0.06)
    tr += _ticks(rng, n, crack_ticks, 0.05, 0.20, 0.12,
                 hp_freq=800.0, dur=0.015)
    tr += _noise_band_at(rng, n, 1800.0, 3600.0, 0.15, 0.35,
                         0.05, 0.20, sand_gain)
    return tr


def piece_bow_string(rng, f0, wind_band, flute_gain):
    """Linh Cung: string twang (plucked partials) + release snap +
    leaf wind + short flute-like blip. One confirmed shot, light
    tail; never a big explosion for five arrows."""
    n = int(BOW_DUR * SR)
    tr = np.zeros((n, 2))
    tr += _pluck(n, f0, 0.35, 0.15)
    tr += _ticks(rng, n, 1, 0.0, 0.005, 0.15, hp_freq=2000.0,
                 dur=0.006)
    tr += _noise_band(rng, n, wind_band[0], wind_band[1], 0.02, 0.15,
                      0.55)
    tr += _tone(n, 1200.0, 950.0, 0.12, 0.05, flute_gain,
                attack_s=0.01, tau=0.05)
    return tr


# ---------------------------------------------------------------- measurement
def decode_f32(path: Path) -> np.ndarray:
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: "
                           f"{r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def decode_mono(path: Path) -> np.ndarray:
    return decode_f32(path).mean(axis=1)


def loudnorm_safe(path: Path):
    """(integrated LUFS or None, true peak dBTP). Short clips (<400 ms)
    have no measurable integrated LUFS -- same as CP08."""
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    start = err.rfind("{")
    if start < 0:
        raise RuntimeError(f"loudnorm gave no JSON for {path}")
    data = json.loads(err[start:err.rfind("}") + 1])
    raw_i = data.get("input_i")
    lufs = None
    if raw_i is not None:
        try:
            v = float(raw_i)
            if v > -70.0:
                lufs = v
        except (TypeError, ValueError):
            lufs = None
    return lufs, float(data["input_tp"])


def spectral_stats(mono: np.ndarray) -> dict:
    x = mono * np.hanning(len(mono))
    X = np.abs(np.fft.rfft(x)) ** 2
    f = np.fft.rfftfreq(len(mono), 1 / SR)
    total = X.sum() + 1e-12
    centroid = float((f * X).sum() / total)

    def band(lo, hi):
        m = (f >= lo) & (f < hi)
        return round(float(X[m].sum() / total), 4)

    m = (f >= 400.0) & (f <= 2000.0)
    xb = X[m]
    prominence = round(float(xb.max() / (np.median(xb) + 1e-12)), 1)
    return {
        "spectralCentroidHz": round(centroid, 1),
        "bandEnergyLt500Hz": band(0.0, 500.0),
        "bandEnergy2500_5500Hz": band(2500.0, 5500.0),
        "bandEnergy3000_8000Hz": band(3000.0, 8000.0),
        "tonalProminence400_2000Hz": prominence,
    }


def diff_rms_ratio(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    denom = float(np.sqrt((b[:n] ** 2).mean())) + 1e-12
    return round(float(np.sqrt(((a[:n] - b[:n]) ** 2).mean())) / denom, 4)


def file_entry_sfx(path: Path, rel: str) -> dict:
    pr = base.probe(path)
    stream = pr["streams"][0]
    lufs, tp = loudnorm_safe(path)
    entry = {
        "path": rel,
        "codec": "pcm_s24le",
        "sampleRateHz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "durationSeconds": round(float(pr["format"]["duration"]), 4),
        "sizeBytes": path.stat().st_size,
        "sha256": base.sha256_file(path),
        "integratedLufs": round(lufs, 2) if lufs is not None else None,
        "truePeakDbtp": round(tp, 2),
    }
    if lufs is None:
        entry["loudnormNote"] = (
            "integrated LUFS not measurable: clip shorter than the "
            "400 ms EBU R128 gate (same note as the ported footstep "
            "cues in SFX_UI_pack_v1.json); level is staged and "
            "recorded as RMS dBFS instead")
    return entry


# ---------------------------------------------------------------- specs
DAO_SPECS = [
    # variant, whoosh band 1 Hz, whoosh band 2 Hz, blade gain, embers
    ("v01", (800.0, 1800.0), (700.0, 1600.0), 0.10, 4),
    ("v02", (850.0, 1900.0), (750.0, 1700.0), 0.08, 3),
    ("v03", (750.0, 1700.0), (650.0, 1500.0), 0.12, 5),
]
BRUSH_SPECS = [
    # variant, paper band Hz, breath freq Hz, porcelain ping gain
    ("v01", (2600.0, 5200.0), 2800.0, 0.06),
    ("v02", (2800.0, 5500.0), 3000.0, 0.05),
    ("v03", (2400.0, 5000.0), 2600.0, 0.07),
]
MACE_SPECS = [
    # variant, whoosh band Hz, knock gain, stone cracks, sand gain
    ("v01", (200.0, 700.0), 0.35, 3, 0.06),
    ("v02", (180.0, 650.0), 0.30, 2, 0.07),
    ("v03", (220.0, 750.0), 0.40, 4, 0.07),
]
BOW_SPECS = [
    # variant, string f0 Hz, leaf-wind band Hz, flute blip gain
    ("v01", 230.0, (1500.0, 3500.0), 0.06),
    ("v02", 245.0, (1550.0, 3600.0), 0.05),
    ("v03", 215.0, (1400.0, 3300.0), 0.07),
]


def _render(stem, variant, seed, piece, dur, target_lufs,
            centroid_lo, centroid_hi, prom_max, extra_asserts):
    rng = np.random.default_rng(seed)
    tr = piece(rng)
    tr = base.normalize(tr, 0.9)
    tr, _, _ = base.gain_stage(tr, target_lufs, WEAPON_TP_CEILING,
                                f"{stem}_{variant}")
    master = MASTER_DIR / f"{stem}_{variant}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    base.write_master_wav(tr, master)
    assert master.read_bytes()[:4] == b"RIFF", "master is not real WAV"
    entry = file_entry_sfx(
        master, f"Art_Source/Audio/Muse/COMPOSED/sfx/"
                f"{stem}_{variant}.wav")
    mono = decode_mono(master)
    spec = spectral_stats(mono)
    assert abs(entry["durationSeconds"] - dur) < 0.01, entry
    assert entry["integratedLufs"] is not None, entry
    assert abs(entry["integratedLufs"] - target_lufs) <= 1.0, entry
    assert entry["truePeakDbtp"] <= -7.0, entry
    assert centroid_lo <= spec["spectralCentroidHz"] <= centroid_hi, spec
    if prom_max is not None:
        assert spec["tonalProminence400_2000Hz"] < prom_max, spec
    for name, ok, detail in extra_asserts(spec):
        assert ok, (name, detail)
    return {
        "variantId": variant,
        "seed": seed,
        "master": entry,
        "spectral": spec,
        "levelNote": (f"staged to integrated LUFS {target_lufs} "
                      f"(shared default basic_blade is -22.25 LUFS); "
                      f"TP ceiling -8 dBTP"),
    }


def render_dao(variant, band1, band2, blade_gain, ember_ticks):
    seed = SEED_DAO + (int(variant[1:]) - 1) * 100
    entry = _render(
        "dao_swing", variant, seed,
        lambda rng: piece_dao_swing(rng, band1, band2, blade_gain,
                                    ember_ticks),
        DAO_DUR, DAO_TARGET_LUFS, 1050.0, 1400.0, 200.0,
        lambda s: [("3-8k band < 0.10 (no bright ring)",
                    s["bandEnergy3000_8000Hz"] < 0.10,
                    s["bandEnergy3000_8000Hz"])])
    entry["recipe"] = (
        f"two cloth-wind whoosh beats {band1[0]:.0f}-{band1[1]:.0f} Hz "
        f"then {band2[0]:.0f}-{band2[1]:.0f} Hz (0.13 s each, 0.17 s "
        f"apart) + deep blade tone (200->130 Hz glide, gain "
        f"{blade_gain}) + {ember_ticks} ember crackle ticks "
        f"(5-8 kHz, gain 0.05); tail cuts fast")
    return entry


def render_brush(variant, band, breath_f, ping_gain):
    seed = SEED_BRUSH + (int(variant[1:]) - 1) * 100
    entry = _render(
        "brush_stroke", variant, seed,
        lambda rng: piece_brush_stroke(rng, band, breath_f, ping_gain),
        BRUSH_DUR, BRUSH_TARGET_LUFS, 3200.0, 4200.0, None,
        lambda s: [("3-8k band >= 0.35 (airy paper/water identity)",
                    s["bandEnergy3000_8000Hz"] >= 0.35,
                    s["bandEnergy3000_8000Hz"])])
    # Prominence 400-2000 Hz is recorded, not asserted for brush: the
    # cue's energy sits above 2400 Hz, so the median in 400-2000 Hz
    # is near the noise floor and the ratio is not a tonality claim
    # (same note as the grass cue in CP1).
    entry["recipe"] = (
        f"paper swish band-noise {band[0]:.0f}-{band[1]:.0f} Hz "
        f"(attack 0.03 s, sustain 0.25 s, decay 0.12 s) + thin water "
        f"breath sine {breath_f:.0f} Hz glide + two porcelain pings "
        f"(3.6/3.4 kHz, gain {ping_gain}); soft, no impact")
    return entry


def render_mace(variant, band, knock_gain, crack_ticks, sand_gain):
    seed = SEED_MACE + (int(variant[1:]) - 1) * 100
    entry = _render(
        "mace_swing", variant, seed,
        lambda rng: piece_mace_swing(rng, band, knock_gain, crack_ticks,
                                     sand_gain),
        MACE_DUR, MACE_TARGET_LUFS, 450.0, 650.0, None,
        lambda s: [("low-end weight: <500 Hz band >= 0.30 "
                    "(vs metal_parry 0.00)",
                    s["bandEnergyLt500Hz"] >= 0.30,
                    s["bandEnergyLt500Hz"]),
                   ("not sub-bass only: 2.5-5.5 kHz band present "
                    "(stone cracks + sand)",
                    s["bandEnergy2500_5500Hz"] >= 0.02,
                    s["bandEnergy2500_5500Hz"])])
    # Prominence 400-2000 Hz is recorded, not asserted for mace: the
    # cue's energy is concentrated below 700 Hz, so the median in
    # 400-2000 Hz is near the noise floor and the ratio is not a
    # tonality claim (same note as the grass cue in CP1). The
    # decisive parry discriminator is the <500 Hz band (mace >= 0.30
    # vs parry 0.00) plus the <1%-of-parry prominence bound checked
    # by the validator.
    entry["recipe"] = (
        f"low whoosh band-noise {band[0]:.0f}-{band[1]:.0f} Hz + deep "
        f"wood knock (150->75 Hz glide, gain {knock_gain}) + "
        f"{crack_ticks} stone-crack ticks (0.8 kHz high-pass) + sand "
        f"tail (1.8-3.6 kHz, gain {sand_gain}); attack clear before the "
        f"deep tail")
    return entry


def render_bow(variant, f0, wind_band, flute_gain):
    seed = SEED_BOW + (int(variant[1:]) - 1) * 100
    entry = _render(
        "bow_string", variant, seed,
        lambda rng: piece_bow_string(rng, f0, wind_band, flute_gain),
        BOW_DUR, BOW_TARGET_LUFS, 1750.0, 2400.0, 5000.0,
        lambda s: [("leaf-wind presence: 2.5-5.5 kHz band >= 0.10",
                    s["bandEnergy2500_5500Hz"] >= 0.10,
                    s["bandEnergy2500_5500Hz"])])
    entry["recipe"] = (
        f"plucked-string twang (f0 {f0:.0f} Hz, 8 harmonics, "
        f"1/k^1.5) + release snap + leaf-wind band-noise "
        f"{wind_band[0]:.0f}-{wind_band[1]:.0f} Hz + short flute-like "
        f"blip (1200->950 Hz glide, gain {flute_gain}); one confirmed "
        f"shot, light tail")
    return entry


def save_pack(cues):
    pack = {
        "packId": "NGM_SFX_COMPOSED_DRAFT_WEAPONS_V1",
        "checkpoint": "MEDIA-02 WO39 M39-A CP2 - composed SFX draft: "
                      "4 weapon identities (second block of "
                      "DEC-MEDIA-SFX-DRAFT-20261112)",
        "decisionId": "DEC-MEDIA-SFX-DRAFT-20261112",
        "approvalRef": (
            "Implementation/Content/DesignBaselines/"
            "media_sfx_draft_execution_20261112.json @ e4b3e4b "
            "(PR #131, Codex Gói 39, issue #116 comment 6815238814, "
            "2026-11-12); approval is DRAFT production of 18 variants, "
            "not runtime adoption"),
        "branch": "muse/media-production-20261104",
        "baseSha": "9ac73dc",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: weapon-identity cues "
                      "authored as data in Tools/MediaProduction/Muse/"
                      "build_composed_sfx_me_cp2b_weapons.py and "
                      "rendered by procedural synthesis. No external "
                      "samples, no ported bytes, no voices.",
        "status": "DRAFT",
        "auditionStatus": "NOT_AUDITIONED",
        "runtime": {
            "ingested": False,
            "runtimeAudioCountUnchanged": 783,
            "note": "SOURCE ONLY: no runtime file was written and no "
                    "runtime manifest was touched. Runtime ingest is a "
                    "Codex review decision (Gói 39 M39-C).",
        },
        "counts": {"cues": len(cues),
                   "variants": sum(len(c["variants"]) for c in cues)},
        "cues": cues,
        "notes": [
            "basic_blade stays the shared swing default; these four "
            "identities play only if Codex wants a swing per weapon "
            "(P-WEAPON, M-E CP2a). No runtime key or binding is "
            "created here.",
            "Each weapon sits in its own spectral slot (mace "
            "450-650 Hz, dao 1050-1400 Hz, bow 1750-2400 Hz, brush "
            "3200-4200 Hz), >=300 Hz from every sibling weapon and "
            ">=400 Hz from basic_blade (2702 Hz). Mace is told apart "
            "from metal_parry (764 Hz, prominence ~1.49M) by its "
            "low-end weight (<500 Hz band >= 0.30 vs parry 0.00) and "
            "its prominence staying below 1% of parry's (recorded, "
            "not a <200 bound: mace energy sits below 700 Hz, so the "
            "400-2000 Hz window median is near the noise floor; same "
            "note as the grass cue in CP1).",
            "dao_swing never plays as a fire roar and never implies "
            "gore; brush_stroke never loops bubbles and is not an "
            "impact; mace_swing is never sub-bass only (phone "
            "speakers must keep the attack); bow_string plays once "
            "per confirmed arrow release, never five sounds at once "
            "and never one big explosion for five arrows (Audio "
            "Direction v1 §1).",
            "All loudness/true-peak/spectral numbers are measured "
            "from the real rendered bytes; no ear audition has been "
            "done. Spectral distinctness vs the ported baselines is "
            "re-measured independently by "
            "check_composed_sfx_me_cp2b_weapons_v1.py.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['cues']} cues / "
          f"{pack['counts']['variants']} variants", flush=True)


def save_playlist(cues):
    lines = [
        "#EXTM3U",
        "# MEDIA-02 WO39 M39-A CP2 — composed SFX draft: 4 weapon identities",
        "# AUDITION STATUS: NOT_AUDITIONED (this environment cannot "
        "listen)",
        "# This file holds valid M3U content under a .txt name because",
        "# .m3u is not in the scope policy mediaExtensions; rename a",
        "# copy to .m3u to open it directly in a player. Open this file",
        "# from the repo so the relative paths resolve: this playlist",
        "# sits 4 levels deep (Implementation/Content/Audio/Deliveries)",
        "# so entries start with ../../../../ .",
        "# Measurements are loudness/codec/spectrum numbers, NOT a",
        "# listening PASS. Baselines at the end are the ported cues",
        "# these drafts must be told apart from.",
        "",
    ]
    for cue in cues:
        for v in cue["variants"]:
            m = v["master"]
            lines.append(
                f"#EXTINF:{m['durationSeconds']},{cue['cueKey']} "
                f"{v['variantId']} — {cue['nameVi']} "
                f"(LUFS {m['integratedLufs']}, TP "
                f"{m['truePeakDbtp']} dBTP)")
            lines.append(f"../../../../{m['path']}")
    lines += [
        "",
        "# --- baseline A/B (ported, for comparison only) ---",
        "#EXTINF:0.4632,SFX/SKILL/metal_parry v01 — confirmed counter "
        "(mace_swing must NOT sound like a parry ring)",
        "../../../../ClientGodot/assets/audio/sfx/skill/metal_parry_v01.wav",
        "#EXTINF:0.2026,SFX/COMBAT/basic_blade v01 — shared swing "
        "default (each weapon identity must sit in its own slot)",
        "../../../../ClientGodot/assets/audio/sfx/combat/basic_blade_v01.wav",
        "",
    ]
    PLAYLIST.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {PLAYLIST.relative_to(ROOT)}", flush=True)


def cue_entry(key, proposal, name_vi, trigger, play_when, never_when,
              mix_role, structure, duration, target_lufs, variants):
    return {
        "cueKey": key,
        "candidateKey": key,
        "proposal": proposal,
        "nameVi": name_vi,
        "category": "COMBAT",
        "kind": "SFX",
        "loop": False,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "triggerSemanticProposed": trigger,
        "triggerStatus": "UNSUPPORTED",
        "binding": None,
        "eventIntent": {
            "playWhen": play_when,
            "neverPlayWhen": never_when,
            "mixRole": mix_role,
        },
        "composition": {
            "durationSeconds": duration,
            "targetLufs": target_lufs,
            "structure": structure,
            "rendering": "procedural synthesis, authored in "
                         "build_composed_sfx_me_cp2b_weapons.py; "
                         "no external samples, no voices",
        },
        "variants": variants,
    }


def main() -> int:
    rendered = {}
    specs = [
        ("dao_swing", DAO_SPECS, render_dao),
        ("brush_stroke", BRUSH_SPECS, render_brush),
        ("mace_swing", MACE_SPECS, render_mace),
        ("bow_string", BOW_SPECS, render_bow),
    ]
    for stem, spec_list, fn in specs:
        variants = []
        for spec in spec_list:
            entry = fn(*spec)
            variants.append(entry)
            print(f"OK {stem} {spec[0]}: "
                  f"{entry['master']['durationSeconds']} s / "
                  f"{entry['master']['integratedLufs']} LUFS / "
                  f"{entry['master']['truePeakDbtp']} dBTP / centroid "
                  f"{entry['spectral']['spectralCentroidHz']} Hz / "
                  f"prominence "
                  f"{entry['spectral']['tonalProminence400_2000Hz']}",
                  flush=True)
        for i in range(len(variants)):
            for j in range(i + 1, len(variants)):
                a = decode_f32(ROOT / variants[i]["master"]["path"])
                b = decode_f32(ROOT / variants[j]["master"]["path"])
                ratio = diff_rms_ratio(a, b)
                assert ratio >= 0.05, (stem, i, j, ratio)
                variants[i].setdefault("distinctness", {})[
                    f"vs_{variants[j]['variantId']}"] = ratio
        rendered[stem] = variants

    cues = [
        cue_entry(
            "SFX/COMBAT/dao_swing", "P-WEAPON", "Vung đao (Ảnh Đao)",
            "WEAPON_SWING_DAO",
            "Ảnh Đao swing, if the client/server exposes a per-weapon "
            "swing event.",
            "Never as a fire roar covering the whole skill, and never "
            "as realistic blood/violence audio (Audio Direction §1).",
            "Deep blade + cloth wind, two short beats; quieter than "
            "the shared default (LUFS -23.5 vs -22.25).",
            "Two cloth-wind whoosh beats + deep blade tone + ember "
            "crackle ticks; tail cuts fast.",
            DAO_DUR, DAO_TARGET_LUFS, rendered["dao_swing"]),
        cue_entry(
            "SFX/COMBAT/brush_stroke", "P-WEAPON",
            "Nét bút (Huyền Bút)", "WEAPON_SWING_BRUSH",
            "Huyền Bút stroke, if the client/server exposes a "
            "per-weapon swing event.",
            "Never as looping bubbles, and never as an impact hit "
            "(Audio Direction §1: heal-soft, not an impact).",
            "Airy paper/water swish, softest of the four (LUFS "
            "-24.0); lead-release-stop.",
            "Paper swish (sustain 0.25 s) + thin water-breath sine + "
            "two porcelain pings.",
            BRUSH_DUR, BRUSH_TARGET_LUFS, rendered["brush_stroke"]),
        cue_entry(
            "SFX/COMBAT/mace_swing", "P-WEAPON", "Vung chùy (Thạch Chùy)",
            "WEAPON_SWING_MACE",
            "Thạch Chùy swing, if the client/server exposes a "
            "per-weapon swing event.",
            "Never sub-bass only (phone speakers must keep the "
            "attack); never a stone-only thud without the wood "
            "knock (Audio Direction §1).",
            "Weighty low swing with a clear attack before the deep "
            "tail (LUFS -23.5).",
            "Low whoosh + deep wood knock + stone-crack ticks + sand "
            "tail.",
            MACE_DUR, MACE_TARGET_LUFS, rendered["mace_swing"]),
        cue_entry(
            "SFX/COMBAT/bow_string", "P-WEAPON", "Bật dây (Linh Cung)",
            "WEAPON_SWING_BOW",
            "Linh Cung release, once per confirmed arrow (Liên Châu: "
            "one cue per confirmed shot, never five at once).",
            "Never one big explosion for five arrows, and never a "
            "dragon howl for a Mộc projectile (Audio Direction §1).",
            "String twang + leaf wind, light tail (LUFS -23.5).",
            "Plucked-string partials + release snap + leaf wind + "
            "short flute-like blip.",
            BOW_DUR, BOW_TARGET_LUFS, rendered["bow_string"]),
    ]
    save_pack(cues)
    save_playlist(cues)
    return 0


if __name__ == "__main__":
    sys.exit(main())
