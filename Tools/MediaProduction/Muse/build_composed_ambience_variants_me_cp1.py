#!/usr/bin/env python3
"""MEDIA-02 WO37 M-E checkpoint 1: REAL VARIANTS for composed ambience.

Checkpoint 30 composed all 13 AMBIENCE/* cues but each cue shipped
exactly ONE 16.0 s master (v01). A looping ambience bed with a single
render repeats identically forever in game, so M-E adds two REAL
variants per cue (v02, v03) -- new deterministic renders of the same
recipe, not copies, not gain/pitch re-prints of v01:

  * same piece_* builder and structure as checkpoint 30 (imported
    from build_composed_ambience.py, untouched), new seeds
    32000 + idx*100 + variant (v01 used 3000 + idx);
  * same duration 16.0 s, same loudness target (the ported cue's
    checkpoint-07 measured LUFS), same loop construction (1.5 s tail
    wrap + 0.25 s end landing), same TP ceiling -7 dB (asserted
    master TP <= -6 dBTP);
  * rift only: the CP30 recipe is almost fully deterministic (fixed
    D drone + fixed shimmer partials), so its variants would differ
    only in the low bed. The variant recipe detunes the drone/shimmer
    partials by +0.4 Hz (v02) / -0.4 Hz (v03) -- same character,
    genuinely different beating. All other cues carry enough
    stochastic content (noise beds, random event times/pitches) that
    a new seed is a real variant.

Distinctness is MEASURED, not asserted: every variant master is
SHA-distinct from v01 and from its sibling, and the waveform
difference RMS vs v01 (decoded from real bytes) is recorded per
variant. No ear audition has been done.

Outputs:
  Art_Source/Audio/Muse/COMPOSED/ambience/<stem>_v02.wav (master, 48k/24b)
  Art_Source/Audio/Muse/COMPOSED/ambience/<stem>_v03.wav
  ClientGodot/assets/audio/composed/ambience/<stem>_v02.ogg (runtime)
  ClientGodot/assets/audio/composed/ambience/<stem>_v03.ogg
  Implementation/Content/Audio/Deliveries/
      AMBIENCE_COMPOSED_VARIANTS_pack_v1.json
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_composed_ambience as base  # noqa: E402

ROOT = base.ROOT
SR = base.SR
DUR = base.DUR
N = base.N
T = base.T
MASTER_DIR = base.MASTER_DIR
RUNTIME_DIR = base.RUNTIME_DIR
DELIVERY = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "AMBIENCE_COMPOSED_VARIANTS_pack_v1.json")
V01_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "AMBIENCE_COMPOSED_pack_v1.json")
TMP = Path("/tmp/composed_ambience_variants")
TMP.mkdir(parents=True, exist_ok=True)

SEED_BASE = 32000
VARIANTS = (2, 3)
LUFS_TOL = 0.5
TP_MAX = -6.0
DIFF_RMS_MIN = 0.05


def decode_f32(path: Path) -> np.ndarray:
    """Decode any audio file to float32 stereo (SR) via ffmpeg."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: "
                           f"{r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def diff_rms_ratio(a: np.ndarray, b: np.ndarray) -> float:
    """rms(a - b) / rms(b); 0.0 = identical, ~1.0 = fully different."""
    n = min(len(a), len(b))
    denom = float(np.sqrt((b[:n] ** 2).mean())) + 1e-12
    return round(float(np.sqrt(((a[:n] - b[:n]) ** 2).mean())) / denom, 4)


def piece_rift_variant(detune_hz: float):
    """CP30 piece_rift with the deterministic partials detuned.

    Same character (low D drone + beating detune + tritone shimmer),
    different beating: the drone partials shift by detune_hz and the
    shimmer partials by 2*detune_hz. The noise bed still uses the rng.
    """
    def _piece(tr, rng):
        d = detune_hz
        drone = (np.sin(2 * np.pi * (73.42 + d) * T)
                 + 0.7 * np.sin(2 * np.pi * (110.0 + d) * T)
                 + 0.5 * np.sin(2 * np.pi * (74.0 + d) * T))
        tr[:, 0] += drone * 0.16
        tr[:, 1] += drone * 0.16
        shim = (np.sin(2 * np.pi * (311.13 + 2 * d) * T)
                + 0.6 * np.sin(2 * np.pi * (466.16 + 2 * d) * T))
        tr += base.apply_env(np.stack([shim, shim], axis=1) * 0.035,
                             base.swell(0.4, (0.06, 0.1)))
        tr += base.bed(rng, "low", 300.0, 0.12)
    return _piece


def render_variant(spec, idx, variant_no, v01_master_path):
    cue_key, name_vi, stem, target_lufs, builder, note = spec
    if stem == "rift":
        builder = piece_rift_variant(+0.4 if variant_no == 2 else -0.4)
    rng = np.random.default_rng(SEED_BASE + idx * 100 + variant_no)
    tr = np.zeros((N, 2), dtype=np.float64)
    builder(tr, rng)
    tr = base.normalize(tr, 0.9)
    tr = base.tail_wrap(tr, 1.5)
    tr, raw_jump = base.end_landing(tr, 0.25)
    tr, _, _ = base.gain_stage(tr, target_lufs, -7.0,
                               f"{stem}_v0{variant_no}")
    master = MASTER_DIR / "ambience" / f"{stem}_v0{variant_no}.wav"
    master.parent.mkdir(parents=True, exist_ok=True)
    base.write_master_wav(tr, master)
    runtime = RUNTIME_DIR / "ambience" / f"{stem}_v0{variant_no}.ogg"
    runtime.parent.mkdir(parents=True, exist_ok=True)
    base.encode_ogg(master, runtime)
    m_entry = base.file_entry(
        master, f"Art_Source/Audio/Muse/COMPOSED/ambience/"
                f"{stem}_v0{variant_no}.wav", "pcm_s24le")
    r_entry = base.file_entry(
        runtime, f"ClientGodot/assets/audio/composed/ambience/"
                 f"{stem}_v0{variant_no}.ogg", "vorbis")
    assert abs(m_entry["durationSeconds"] - DUR) < 0.05, stem
    assert abs(m_entry["integratedLufs"] - target_lufs) <= LUFS_TOL, (
        stem, m_entry)
    assert m_entry["truePeakDbtp"] <= TP_MAX, (stem, m_entry)
    v01 = decode_f32(v01_master_path)
    mine = decode_f32(master)
    ratio = diff_rms_ratio(mine, v01)
    assert ratio >= DIFF_RMS_MIN, (stem, variant_no, ratio)
    return {
        "variantId": f"v0{variant_no}",
        "seed": SEED_BASE + idx * 100 + variant_no,
        "recipe": ("same piece_* builder as v01 (build_composed_ambience.py)"
                   + ("; rift drone/shimmer detuned "
                      f"{'+0.4' if variant_no == 2 else '-0.4'} Hz"
                      if stem == "rift" else "")),
        "master": m_entry,
        "runtime": r_entry,
        "seam": {**base.seam_stats(tr), "wrapJumpRaw": raw_jump,
                 "landingNote": "wrapJump is measured after a 0.25 s "
                                "end-landing blend to the first sample "
                                "(loop crossfade construction); "
                                "wrapJumpRaw is the step before it"},
        "distinctnessVsV01": {
            "method": "waveform difference RMS vs the v01 master, both "
                      "decoded from real bytes (ffmpeg f32le 48k stereo); "
                      "0.0 = identical, ~1.0 = fully different",
            "diffRmsRatio": ratio,
            "shaDistinctFromV01": m_entry["sha256"] != base.sha256_file(
                v01_master_path),
        },
    }


def save_pack(by_key: dict):
    """Write the delivery manifest from whatever cues exist so far."""
    order = [c[0] for c in base.CUES]
    cues = [by_key[k] for k in order if k in by_key]
    new_variants = sum(len([v for v in c["variants"]
                            if v["variantId"] in ("v02", "v03")])
                       for c in cues)
    pack = {
        "packId": "NGM_AMBIENCE_COMPOSED_VARIANTS_V1",
        "checkpoint": "MEDIA-02 WO37 M-E checkpoint 1 - real variants "
                      "for composed ambience (2 new variants per cue)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "provenance": "ORIGINAL_COMPOSED_BY_MUSE: variant renders of "
                      "the checkpoint-30 recipes, authored as data in "
                      "Tools/MediaProduction/Muse/"
                      "build_composed_ambience_variants_me_cp1.py and "
                      "rendered by procedural synthesis. No external "
                      "samples, no ported bytes, no voices. The v01 "
                      "masters are NOT re-rendered: their entries are "
                      "cross-referenced from "
                      "AMBIENCE_COMPOSED_pack_v1.json (checkpoint 30) "
                      "and re-hashed from the real bytes on disk at "
                      "build time.",
        "counts": {"ambienceCues": len(cues),
                   "variantsPerCue": 3,
                   "newVariants": new_variants,
                   "totalVariants": len(cues) * 3},
        "cues": cues,
        "notes": [
            "Adoption is a presentation-adapter decision (Codex): the "
            "variants are delivered in parallel under "
            "ClientGodot/assets/audio/composed/ambience/ and do NOT "
            "replace the ported PackV1 files, the v01 masters, or "
            "their cue bindings. A runtime adapter may rotate v01/v02/"
            "v03 per cue (NO_IMMEDIATE_REPEAT) or keep v01 only.",
            "Variant loudness targets are the same ported cues' "
            "checkpoint-07 measured LUFS as v01, so any variant sits "
            "at the same mix level the P0 draft mixes were designed "
            "around. Loudness/true-peak are measured from real bytes; "
            "no ear audition has been done.",
            "Ambience cues loop by construction (1.5 s tail wrap); the "
            "seam block records the checkpoint-07 indicator, not a "
            "seamlessness PASS. Crowd beds are filtered noise only: "
            "no voice, no words, no intelligible speech is possible "
            "by construction.",
            "SFX side of M-E: the 173 ported SFX/UI cues already carry "
            "3 measured variants each (checkpoint 08, SFX_UI_pack_v1) "
            "so no new SFX variants were composed in this checkpoint; "
            "composed SFX replacements remain a separate Codex "
            "decision, not silently assumed here.",
        ],
    }
    DELIVERY.write_text(json.dumps(pack, ensure_ascii=False, indent=1)
                        + "\n", encoding="utf-8")
    print(f"wrote {DELIVERY.relative_to(ROOT)}: "
          f"{pack['counts']['ambienceCues']} cues / "
          f"{pack['counts']['newVariants']} new variants", flush=True)


def main() -> int:
    only = None
    for arg in sys.argv[1:]:
        if arg.startswith("--only="):
            only = set(arg.split("=", 1)[1].split(","))
    v01_pack = json.loads(V01_PACK.read_text(encoding="utf-8"))
    v01_by_key = {c["cueKey"]: c for c in v01_pack["cues"]}
    by_key = {}
    if DELIVERY.exists():
        existing = json.loads(DELIVERY.read_text(encoding="utf-8"))
        by_key = {c["cueKey"]: c for c in existing["cues"]}
    for idx, spec in enumerate(base.CUES):
        cue_key, name_vi, stem, target_lufs, builder, note = spec
        if only is not None and stem not in only:
            continue
        v01 = v01_by_key[cue_key]
        # Cross-reference v01 from real bytes on disk (no re-render).
        v01_master_path = ROOT / v01["master"]["path"]
        v01_runtime_path = ROOT / v01["runtime"]["path"]
        assert base.sha256_file(v01_master_path) == v01["master"]["sha256"], \
            f"v01 master sha mismatch {cue_key}"
        assert base.sha256_file(v01_runtime_path) == v01["runtime"]["sha256"], \
            f"v01 runtime sha mismatch {cue_key}"
        variants = [{
            "variantId": "v01",
            "seed": 3000 + idx,
            "recipe": "checkpoint-30 master (build_composed_ambience.py)",
            "master": v01["master"],
            "runtime": v01["runtime"],
            "seam": v01["seam"],
            "distinctnessVsV01": None,
        }]
        for vn in VARIANTS:
            entry = render_variant(spec, idx, vn, v01_master_path)
            variants.append(entry)
            print(f"OK {cue_key} v0{vn}: "
                  f"{entry['master']['durationSeconds']} s master "
                  f"{entry['master']['integratedLufs']} LUFS / "
                  f"{entry['master']['truePeakDbtp']} dBTP, runtime "
                  f"{entry['runtime']['integratedLufs']} LUFS / "
                  f"{entry['runtime']['truePeakDbtp']} dBTP, "
                  f"diff-vs-v01 {entry['distinctnessVsV01']['diffRmsRatio']}",
                  flush=True)
        by_key[cue_key] = {
            "cueKey": cue_key, "nameVi": name_vi, "kind": "AMBIENCE",
            "loop": True,
            "provenance": "ORIGINAL_COMPOSED_BY_MUSE",
            "targetLufsPorted": target_lufs,
            "composition": {
                "durationSeconds": DUR,
                "structure": note,
                "rendering": "procedural synthesis (filtered-noise beds, "
                             "slow gust/swell envelopes, sparse "
                             "deterministic events), variant renders "
                             "authored in "
                             "build_composed_ambience_variants_me_cp1.py; "
                             "no external samples, no voices",
            },
            "variants": variants,
        }
        save_pack(by_key)
    return 0


if __name__ == "__main__":
    sys.exit(main())
