#!/usr/bin/env python3
"""MEDIA-02 WO39 M39-A checkpoint 1: COMPOSED SFX draft, guard + grass.

First asset block of DEC-MEDIA-SFX-DRAFT-20261112 (Codex, Gói 39,
issue #116 comment 6815238814, 2026-11-12; machine-readable approval
Implementation/Content/DesignBaselines/media_sfx_draft_execution_20261112.json
@ e4b3e4b on PR #131). The approval authorises 18 draft variants
(guard-expire + 4 weapon identities + grass, 3 variants each); this
checkpoint delivers the FIRST block only: guard + grass = 6 variants.
The 4 weapon identities are the next block (M39-A CP2).

Cues (candidate keys from the approval; NOT runtime keys):
  SFX/COMBAT/guard_expire -- small stance-release cue on an UNHIT
    guard-window expiry (proposed trigger GUARD_WINDOW_EXPIRED_UNHIT).
    Must be audibly distinct from the confirmed counter cue
    SFX/SKILL/metal_parry (CP08: centroid ~748-777 Hz, extreme tonal
    prominence ~1.16M, LUFS -24.35..-24.05, TP max -6.93 dBTP) and
    from basic_blade (bright whoosh, centroid ~2650-2740 Hz):
    breathy band-noise release + soft low settle thump + faint cloth
    rustle; NO sustained metallic partials, NO sharp attack, NO HF
    ring. It must NEVER be played when a counter is confirmed --
    that is metal_parry's job.
  SFX/WORLD/step_grass -- grass footstep, distinct from the three
    ported footsteps (CP08, measured from real bytes here):
    step_stone centroid ~1138-1323 Hz / 2.5-5.5 kHz band 0.17-0.21,
    step_wood and step_mud centroid ~495-511 Hz / band 0.07, all
    RMS -25.0 dBFS, duration 0.203-0.217 s, LUFS not measurable
    (<400 ms EBU gate). Grass is a dry rustle (1.6-4.5 kHz) + soft
    ground thud + sparse blade snaps; target centroid 1800-3000 Hz,
    2.5-5.5 kHz band >= 0.35, RMS -25.0 dBFS like its siblings.

Rendering: procedural synthesis only (filtered-noise bands, pitch-
gliding sine thumps, sparse ticks), deterministic per-seed. No
external samples, no ported bytes, no voices. Masters are stereo
48 kHz / 24-bit WAV, the composed-audio convention (CP26/CP30).

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
            / "SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json")
PLAYLIST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt")
TMP = Path("/tmp/composed_sfx_guard_grass")
TMP.mkdir(parents=True, exist_ok=True)

SEED_GUARD = 41000
SEED_GRASS = 42000
GUARD_DUR = 0.50
GRASS_DUR = 0.21
GUARD_TARGET_LUFS = -27.5
GUARD_TP_CEILING = -10.0
GRASS_TARGET_RMS_DBFS = -25.0
GRASS_TP_CEILING_DBTP = -8.0


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
    """Attack, flat sustain, then exponential decay. A footstep crush
    carries energy through the contact (low crest), unlike a ping
    whose fast exponential decay leaves the clip peaky: with tau-only
    decay the grass rustle measured crest ~18.7 dB and RMS staging
    could not reach the -25 dBFS family level under the TP ceiling."""
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


def _thump(n, f0, f1, dur_s, gain):
    """Centred pitch-gliding sine thump (soft ground/stance settle)."""
    m = int(dur_s * SR)
    t = np.arange(m) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 25.0)
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * np.exp(-t / 0.05)
    sig = sig / (np.max(np.abs(sig)) + 1e-9) * gain
    out = np.zeros((n, 2))
    out[:m, 0] = sig
    out[:m, 1] = sig
    return out


def _ticks(rng, n, count, t_lo, t_hi, gain):
    """Sparse dry snaps: 8 ms high-passed noise ticks at random times."""
    out = np.zeros((n, 2))
    for _ in range(count):
        at = float(rng.uniform(t_lo, t_hi))
        m = int(0.008 * SR)
        x = rng.standard_normal(m)
        x = _hp(x, 4000.0)
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


def piece_guard_expire(rng, band, tau, thump_gain, rustle_gain):
    n = int(GUARD_DUR * SR)
    tr = np.zeros((n, 2))
    # Breath/air release: broadband band-noise, soft attack, fast decay.
    tr += _noise_band(rng, n, band[0], band[1], 0.012, tau, 0.55)
    # Soft low settle thump (stance weight, not an impact).
    tr += _thump(n, 110.0, 70.0, 0.16, thump_gain)
    # Faint cloth rustle at the onset only.
    rustle_n = int(0.05 * SR)
    rustle = _noise_band(rng, rustle_n, 2800.0, 6000.0, 0.004, 0.02,
                         rustle_gain)
    tr[:rustle_n] += rustle
    return tr


def piece_step_grass(rng, band, tick_count, thud_gain):
    n = int(GRASS_DUR * SR)
    tr = np.zeros((n, 2))
    # Dry rustle: the grass identity (1.6-4.5 kHz band noise) with a
    # short sustain so the crush carries body energy (low crest) --
    # a tau-only decay left the clip too peaky to stage to the
    # footstep family's RMS -25 dBFS under the TP ceiling.
    tr += _noise_band(rng, n, band[0], band[1], 0.003, 0.04, 0.55,
                      plateau_s=0.12)
    # Soft ground thud under the rustle (quiet underlay only: a loud
    # low thump drags the centroid down to the wood/mud slot).
    tr += _thump(n, 95.0, 60.0, 0.10, thud_gain)
    # Sparse dry blade snaps inside the first 80 ms.
    tr += _ticks(rng, n, tick_count, 0.005, 0.08, 0.12)
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


def stage_rms(track, target_rms_db, tp_ceiling_dbtp, tag):
    """Iterative RMS staging on the float track (short-clip SFX:
    integrated LUFS is not measurable, CP08 method is RMS -25 dBFS).
    The peak limit is the TRUE PEAK from ffmpeg loudnorm, measured on
    the staged bytes each pass -- sample peak alone understates the
    true peak of steep band-passed noise by >1 dB."""
    tmpf = TMP / f"{tag}_measure.wav"
    for attempt in range(3):
        base.write_f32_wav(track, tmpf)
        mono = decode_mono(tmpf)
        rms_db = float(20 * np.log10(np.sqrt((mono ** 2).mean()) + 1e-12))
        _, tp = loudnorm_safe(tmpf)
        gain = min(target_rms_db - rms_db, tp_ceiling_dbtp - tp)
        if abs(gain) < 0.2 or attempt == 2:
            return track, rms_db, tp
        track = track * (10.0 ** (gain / 20.0))
    return track, rms_db, tp


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
GUARD_SPECS = [
    # variant, band Hz, breath tau s, thump gain, rustle gain
    ("v01", (700.0, 1600.0), 0.12, 0.18, 0.08),
    ("v02", (700.0, 1500.0), 0.14, 0.14, 0.06),
    ("v03", (800.0, 1800.0), 0.10, 0.22, 0.10),
]
GRASS_SPECS = [
    # variant, rustle band Hz, snap ticks, thud gain
    ("v01", (1700.0, 3800.0), 3, 0.08),
    ("v02", (1500.0, 3500.0), 2, 0.10),
    ("v03", (1800.0, 3900.0), 4, 0.06),
]


def render_guard(variant, band, tau, thump_gain, rustle_gain):
    seed = SEED_GUARD + (int(variant[1:]) - 1) * 100
    rng = np.random.default_rng(seed)
    tr = piece_guard_expire(rng, band, tau, thump_gain, rustle_gain)
    tr = base.normalize(tr, 0.9)
    tr, _, _ = base.gain_stage(tr, GUARD_TARGET_LUFS, GUARD_TP_CEILING,
                                f"guard_expire_{variant}")
    master = MASTER_DIR / f"guard_expire_{variant}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    base.write_master_wav(tr, master)
    assert master.read_bytes()[:4] == b"RIFF", "master is not real WAV"
    entry = file_entry_sfx(
        master, f"Art_Source/Audio/Muse/COMPOSED/sfx/"
                f"guard_expire_{variant}.wav")
    mono = decode_mono(master)
    spec = spectral_stats(mono)
    n30 = int(0.30 * SR)
    tail_frac = round(float((mono[n30:] ** 2).sum()
                            / ((mono ** 2).sum() + 1e-12)), 4)
    assert abs(entry["durationSeconds"] - GUARD_DUR) < 0.01, entry
    assert entry["integratedLufs"] is not None, entry
    assert abs(entry["integratedLufs"] - GUARD_TARGET_LUFS) <= 1.0, entry
    assert entry["truePeakDbtp"] <= -9.0, entry
    assert 1000.0 <= spec["spectralCentroidHz"] <= 1600.0, spec
    assert spec["tonalProminence400_2000Hz"] < 200.0, spec
    assert spec["bandEnergy3000_8000Hz"] < 0.10, spec
    return {
        "variantId": variant,
        "seed": seed,
        "recipe": (
            f"breath band-noise {band[0]:.0f}-{band[1]:.0f} Hz "
            f"(tau {tau:.2f} s) + pitch-glide settle thump "
            f"(110->70 Hz, gain {thump_gain}) + faint cloth rustle "
            f"(2.8-6 kHz, gain {rustle_gain}); no metallic partials, "
            f"no sharp attack"),
        "master": entry,
        "spectral": {**spec, "tailEnergyFractionAfter030s": tail_frac},
        "levelNote": ("staged to integrated LUFS "
                      f"{GUARD_TARGET_LUFS} (quieter than metal_parry "
                      "-24.2 LUFS: a small release, not a confirmed "
                      "counter); TP ceiling -10 dBTP"),
    }


def render_grass(variant, band, tick_count, thud_gain):
    seed = SEED_GRASS + (int(variant[1:]) - 1) * 100
    rng = np.random.default_rng(seed)
    tr = piece_step_grass(rng, band, tick_count, thud_gain)
    tr = base.normalize(tr, 0.9)
    tr, rms_db, _ = stage_rms(tr, GRASS_TARGET_RMS_DBFS,
                              GRASS_TP_CEILING_DBTP,
                              f"step_grass_{variant}")
    master = MASTER_DIR / f"step_grass_{variant}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    base.write_master_wav(tr, master)
    assert master.read_bytes()[:4] == b"RIFF", "master is not real WAV"
    entry = file_entry_sfx(
        master, f"Art_Source/Audio/Muse/COMPOSED/sfx/"
                f"step_grass_{variant}.wav")
    mono = decode_mono(master)
    spec = spectral_stats(mono)
    assert abs(entry["durationSeconds"] - GRASS_DUR) < 0.01, entry
    assert entry["integratedLufs"] is None, entry
    assert entry["truePeakDbtp"] <= -7.0, entry
    assert abs(rms_db - GRASS_TARGET_RMS_DBFS) <= 0.75, (variant, rms_db)
    assert 1800.0 <= spec["spectralCentroidHz"] <= 3000.0, spec
    assert spec["bandEnergy2500_5500Hz"] >= 0.35, spec
    return {
        "variantId": variant,
        "seed": seed,
        "recipe": (
            f"dry rustle band-noise {band[0]:.0f}-{band[1]:.0f} Hz + "
            f"pitch-glide ground thud (95->60 Hz, gain {thud_gain}) + "
            f"{tick_count} dry blade snaps in the first 80 ms"),
        "master": entry,
        "spectral": spec,
        "rmsDbfs": round(rms_db, 2),
        "levelNote": ("staged to RMS -25.0 dBFS like the ported "
                      "footstep family (step_stone/wood/mud); "
                      "integrated LUFS not measurable under 400 ms"),
    }


def save_pack(cues):
    pack = {
        "packId": "NGM_SFX_COMPOSED_DRAFT_GUARD_GRASS_V1",
        "checkpoint": "MEDIA-02 WO39 M39-A CP1 - composed SFX draft: "
                      "guard + grass (first block of "
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
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: guard-expire and "
                      "grass-footstep cues authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_sfx_me_cp2b_guard_grass.py and "
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
            "guard_expire must NEVER be played when a counter is "
            "confirmed -- that is SFX/SKILL/metal_parry's job "
            "(trigger COUNTER_CONFIRMED). It plays only on an unhit "
            "guard-window expiry, if the client/server ever exposes "
            "that trigger; until then binding is UNSUPPORTED.",
            "basic_blade stays the shared swing default and "
            "metal_parry stays the confirmed-counter cue; the 4 "
            "weapon identities (dao_swing, brush_stroke, mace_swing, "
            "bow_string) are the next block (M39-A CP2), not this "
            "checkpoint.",
            "step_grass plays only on grass surfaces; stone, wood "
            "and wet mud keep their ported cues. If the map has no "
            "authoritative grass-surface flag, binding is "
            "UNSUPPORTED, not guessed.",
            "No phase-specific skill keys were created: the catalogue "
            "stays 1 cue/skill with shared miss/impact (Gói 39 "
            "rules, Q-PHASES unanswered).",
            "All loudness/true-peak/spectral numbers are measured "
            "from the real rendered bytes; no ear audition has been "
            "done. Spectral distinctness vs the ported baselines is "
            "re-measured independently by "
            "check_composed_sfx_me_cp2b_guard_grass_v1.py.",
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
        "# MEDIA-02 WO39 M39-A CP1 — composed SFX draft: guard + grass",
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
        "(guard_expire must NOT sound like this)",
        "../../../../ClientGodot/assets/audio/sfx/skill/metal_parry_v01.wav",
        "#EXTINF:0.2026,SFX/WORLD/step_stone v01 — footstep on stone",
        "../../../../ClientGodot/assets/audio/sfx/world/step_stone_v01.wav",
        "#EXTINF:0.2026,SFX/WORLD/step_wood v01 — footstep on wood",
        "../../../../ClientGodot/assets/audio/sfx/world/step_wood_v01.wav",
        "#EXTINF:0.2026,SFX/WORLD/step_mud v01 — footstep on wet mud",
        "../../../../ClientGodot/assets/audio/sfx/world/step_mud_v01.wav",
        "",
    ]
    PLAYLIST.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {PLAYLIST.relative_to(ROOT)}", flush=True)


def main() -> int:
    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}

    guard_variants = []
    for spec in GUARD_SPECS:
        entry = render_guard(*spec)
        guard_variants.append(entry)
        print(f"OK guard_expire {spec[0]}: "
              f"{entry['master']['durationSeconds']} s / "
              f"{entry['master']['integratedLufs']} LUFS / "
              f"{entry['master']['truePeakDbtp']} dBTP / centroid "
              f"{entry['spectral']['spectralCentroidHz']} Hz / "
              f"prominence "
              f"{entry['spectral']['tonalProminence400_2000Hz']}",
              flush=True)
    # Inter-variant distinctness (same method as ambience variants).
    for i in range(len(guard_variants)):
        for j in range(i + 1, len(guard_variants)):
            a = decode_f32(ROOT / guard_variants[i]["master"]["path"])
            b = decode_f32(ROOT / guard_variants[j]["master"]["path"])
            ratio = diff_rms_ratio(a, b)
            assert ratio >= 0.05, (i, j, ratio)
            guard_variants[i].setdefault("distinctness", {})[
                f"vs_{guard_variants[j]['variantId']}"] = ratio

    grass_variants = []
    for spec in GRASS_SPECS:
        entry = render_grass(*spec)
        grass_variants.append(entry)
        print(f"OK step_grass {spec[0]}: "
              f"{entry['master']['durationSeconds']} s / RMS "
              f"{entry['rmsDbfs']} dBFS / "
              f"{entry['master']['truePeakDbtp']} dBTP / centroid "
              f"{entry['spectral']['spectralCentroidHz']} Hz / "
              f"2.5-5.5k band "
              f"{entry['spectral']['bandEnergy2500_5500Hz']}",
              flush=True)
    for i in range(len(grass_variants)):
        for j in range(i + 1, len(grass_variants)):
            a = decode_f32(ROOT / grass_variants[i]["master"]["path"])
            b = decode_f32(ROOT / grass_variants[j]["master"]["path"])
            ratio = diff_rms_ratio(a, b)
            assert ratio >= 0.05, (i, j, ratio)
            grass_variants[i].setdefault("distinctness", {})[
                f"vs_{grass_variants[j]['variantId']}"] = ratio

    by_key["SFX/COMBAT/guard_expire"] = {
        "cueKey": "SFX/COMBAT/guard_expire",
        "candidateKey": "SFX/COMBAT/guard_expire",
        "proposal": "P-GUARD",
        "nameVi": "Hết thế thủ (không bị đánh)",
        "category": "COMBAT",
        "kind": "SFX",
        "loop": False,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "triggerSemanticProposed": "GUARD_WINDOW_EXPIRED_UNHIT",
        "triggerStatus": "UNSUPPORTED",
        "binding": None,
        "eventIntent": {
            "playWhen": "Guard window expires with no hit landing, "
                        "if the client/server exposes that event.",
            "neverPlayWhen": "A counter/parry is confirmed (that is "
                             "metal_parry, trigger COUNTER_CONFIRMED). "
                             "Never imply a successful block.",
            "mixRole": "Small stance-release cue, quieter than the "
                       "confirmed counter.",
        },
        "composition": {
            "durationSeconds": GUARD_DUR,
            "targetLufs": GUARD_TARGET_LUFS,
            "structure": "Breathy band-noise release + soft low "
                         "settle thump + faint cloth rustle; no "
                         "metallic partials, no sharp attack.",
            "rendering": "procedural synthesis, authored in "
                         "build_composed_sfx_me_cp2b_guard_grass.py; "
                         "no external samples, no voices",
        },
        "variants": guard_variants,
    }
    by_key["SFX/WORLD/step_grass"] = {
        "cueKey": "SFX/WORLD/step_grass",
        "candidateKey": "SFX/WORLD/step_grass",
        "proposal": "P-GRASS",
        "nameVi": "Bước trên cỏ",
        "category": "WORLD",
        "kind": "SFX",
        "loop": False,
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
        "triggerSemanticProposed": "FOOT_CONTACT_GRASS",
        "triggerStatus": "UNSUPPORTED",
        "binding": None,
        "eventIntent": {
            "playWhen": "Foot contact on a grass surface, if the map "
                        "exposes an authoritative grass-surface flag.",
            "neverPlayWhen": "On stone, wood or wet mud (those keep "
                             "their ported cues).",
            "mixRole": "Footstep family member, level-matched to "
                       "step_stone/wood/mud (RMS -25 dBFS).",
        },
        "composition": {
            "durationSeconds": GRASS_DUR,
            "targetRmsDbfs": GRASS_TARGET_RMS_DBFS,
            "structure": "Dry rustle (1.6-4.5 kHz band noise, short "
                         "ground thud + sparse dry blade snaps.",
            "rendering": "procedural synthesis, authored in "
                         "build_composed_sfx_me_cp2b_guard_grass.py; "
                         "no external samples, no voices",
        },
        "variants": grass_variants,
    }
    cues = [by_key["SFX/COMBAT/guard_expire"],
            by_key["SFX/WORLD/step_grass"]]
    save_pack(cues)
    save_playlist(cues)
    return 0


if __name__ == "__main__":
    sys.exit(main())
