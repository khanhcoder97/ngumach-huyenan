#!/usr/bin/env python3
"""Independent validator: MEDIA-02 WO39 M39-A CP2, 4 weapon identities.

Re-reads EVERYTHING from the real bytes on disk; imports nothing from
the builder. Checks:
  1. manifest parses; counts 4 cues / 12 variants; decision/approval refs.
  2. each master is a real WAV (RIFF, not an LFS pointer), ffprobe
     pcm_s24le 48 kHz stereo, duration/sha256/size match the manifest.
  3. loudness re-measured with ffmpeg loudnorm: each cue at its target
     LUFS +/- 1.0 (dao/mace/bow -23.5, brush -24.0), TP <= -7 dBTP.
  4. spectrum re-measured (numpy FFT): dao centroid 1050-1400 Hz,
     brush 3200-4200 Hz, mace 450-650 Hz, bow 1750-2400 Hz; dao
     prominence < 200, bow prominence < 5000; brush/mace prominence
     recorded, not asserted (their energy sits outside the 400-2000 Hz
     window, so the window median is near the noise floor -- same note
     as the grass cue in CP1); per-cue band checks (dao 3-8k < 0.10,
     brush 3-8k >= 0.35, mace <500 Hz >= 0.30 and 2.5-5.5k >= 0.02,
     bow 2.5-5.5k >= 0.10).
  5. baselines re-measured from the real ported runtime files AND
     cross-checked by sha256 against SFX_UI_pack_v1.json: pairwise
     weapon centroids >= 300 Hz apart; every weapon >= 400 Hz from
     basic_blade's centroid; dao/bow/brush >= 250 Hz from metal_parry's
     centroid; mace told apart from parry by its <500 Hz band (>=
     parry's + 0.20) and centroid <= 700 Hz; every weapon's prominence
     < 1% of parry's.
  6. inter-variant waveform distinctness (diff RMS ratio >= 0.05).
  7. audition playlist lists all 12 masters + 2 baselines; every
     listed file exists.
  8. runtime untouched: `git status --porcelain ClientGodot/` empty;
     no checkpoint file lives outside the policy media/tool roots.
Writes MEDIA02_WO39_M39A_CP2_WEAPONS_VALIDATION_20261112.json.
Exit 0 only when every check passes.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SR = 48000
MANIFEST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json")
PLAYLIST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt")
SFX_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_UI_pack_v1.json")
OUT = (ROOT / "Implementation/Reports/MuseMedia"
       / "MEDIA02_WO39_M39A_CP2_WEAPONS_VALIDATION_20261112.json")

CHECKS = []
FAILURES = []


def check(name, ok, detail=""):
    CHECKS.append({"name": name, "pass": bool(ok), "detail": str(detail)})
    if not ok:
        FAILURES.append(name)
        print(f"FAIL {name}: {detail}", flush=True)
    return ok


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}\n"
                           f"{r.stderr[-1000:]}")
    return r


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def loudnorm_safe(path: Path):
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


def decode(path: Path) -> np.ndarray:
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: "
                           f"{r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


def decode_ac1(path: Path) -> np.ndarray:
    """True mono decode (no upmix scaling). ffmpeg's mono->stereo
    upmix scales each channel by 0.707 (-3.01 dB), so a mono file
    decoded with -ac 2 measures 3 dB low; RMS comparisons against the
    mono ported siblings must use -ac 1."""
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: "
                           f"{r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").astype(np.float64)


def spectral(mono: np.ndarray) -> dict:
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
        "centroidHz": round(centroid, 1),
        "bandLt500": band(0.0, 500.0),
        "band2500_5500": band(2500.0, 5500.0),
        "band3000_8000": band(3000.0, 8000.0),
        "prominence400_2000": prominence,
    }


def diff_rms(a: np.ndarray, b: np.ndarray) -> float:
    n = min(len(a), len(b))
    denom = float(np.sqrt((b[:n] ** 2).mean())) + 1e-12
    return round(float(np.sqrt(((a[:n] - b[:n]) ** 2).mean())) / denom, 4)


# cueKey -> (duration s, target LUFS, centroid lo/hi, prominence bound
# or None when the cue's energy sits outside the 400-2000 Hz window)
CUE_RULES = {
    "SFX/COMBAT/dao_swing": (0.45, -23.5, 1050.0, 1400.0, 200.0),
    "SFX/COMBAT/brush_stroke": (0.55, -24.0, 3200.0, 4200.0, None),
    "SFX/COMBAT/mace_swing": (0.50, -23.5, 450.0, 650.0, None),
    "SFX/COMBAT/bow_string": (0.50, -23.5, 1750.0, 2400.0, 5000.0),
}


def main() -> int:
    pack = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check("manifest parses", True)
    check("decision id", pack.get("decisionId")
          == "DEC-MEDIA-SFX-DRAFT-20261112", pack.get("decisionId"))
    check("approval ref names PR131/e4b3e4b",
          "e4b3e4b" in pack.get("approvalRef", "")
          and "media_sfx_draft_execution_20261112.json"
          in pack.get("approvalRef", ""), pack.get("approvalRef"))
    check("status DRAFT / NOT_AUDITIONED",
          pack.get("status") == "DRAFT"
          and pack.get("auditionStatus") == "NOT_AUDITIONED")
    check("runtime not ingested, count 783",
          pack.get("runtime", {}).get("ingested") is False
          and pack.get("runtime", {}).get("runtimeAudioCountUnchanged")
          == 783, pack.get("runtime"))
    check("counts 4 cues / 12 variants",
          pack.get("counts") == {"cues": 4, "variants": 12},
          pack.get("counts"))
    cues = {c["cueKey"]: c for c in pack["cues"]}
    check("cue keys",
          set(cues) == set(CUE_RULES), list(cues))
    for key, cue in cues.items():
        check(f"{key} trigger UNSUPPORTED, no binding",
              cue.get("triggerStatus") == "UNSUPPORTED"
              and cue.get("binding") is None, cue.get("triggerStatus"))
        check(f"{key} provenance composed",
              cue.get("provenance") == "ORIGINAL_COMPOSED_BY_MUSE")
        check(f"{key} proposal P-WEAPON",
              cue.get("proposal") == "P-WEAPON", cue.get("proposal"))

    # ---- baselines: re-measure + sha-cross-check against CP08 pack
    sfx_pack = json.loads(SFX_PACK.read_text(encoding="utf-8"))
    pack_by_key = {c["cueKey"]: c for c in sfx_pack["cues"]}
    baseline = {}

    def baseline_stats(cue_key, subdir, stem):
        entries = []
        for v in ("v01", "v02", "v03"):
            rel = (f"ClientGodot/assets/audio/sfx/{subdir}/"
                   f"{stem}_{v}.wav")
            p = ROOT / rel
            check(f"baseline file exists {stem}_{v}", p.exists())
            sha = sha256_file(p)
            pack_entry = pack_by_key[cue_key]["variants"][
                int(v[1:]) - 1]
            check(f"baseline sha matches CP08 pack {stem}_{v}",
                  sha == pack_entry["runtime"]["sha256"],
                  sha[:12])
            mono = decode(p).mean(axis=1)
            st = spectral(mono)
            lufs, tp = loudnorm_safe(p)
            # RMS from the true mono decode (-ac 1): the stereo decode
            # path would under-read a mono file by 3.01 dB (upmix).
            mono1 = decode_ac1(p)
            rms = float(20 * np.log10(
                np.sqrt((mono1 ** 2).mean()) + 1e-12))
            entries.append({**st, "lufs": lufs, "tp": tp, "rms": rms})
        mean = {k: round(float(np.mean([e[k] for e in entries])), 2)
                for k in ("centroidHz", "bandLt500", "band2500_5500",
                          "band3000_8000")}
        mean["lufsMean"] = round(float(np.mean(
            [e["lufs"] for e in entries if e["lufs"] is not None])), 2) \
            if any(e["lufs"] is not None for e in entries) else None
        mean["prominenceMax"] = max(e["prominence400_2000"]
                                    for e in entries)
        mean["rmsMean"] = round(float(np.mean([e["rms"]
                                               for e in entries])), 2)
        check(f"baseline {stem} RMS -25.0 dBFS (CP08 family staging)",
              abs(mean["rmsMean"] - (-25.0)) <= 0.5, mean["rmsMean"])
        baseline[cue_key] = mean
        return mean

    parry = baseline_stats("SFX/SKILL/metal_parry", "skill",
                           "metal_parry")
    blade = baseline_stats("SFX/COMBAT/basic_blade", "combat",
                           "basic_blade")
    print(f"baselines: parry={parry} blade={blade}", flush=True)

    # ---- each variant: bytes + loudness + spectrum + distinctness
    measured = {}
    for key, cue in cues.items():
        dur, target_lufs, clo, chi, prom_max = CUE_RULES[key]
        variants = cue["variants"]
        check(f"{key} has 3 variants", len(variants) == 3, len(variants))
        decoded = {}
        for v in variants:
            m = v["master"]
            p = ROOT / m["path"]
            check(f"{key} {v['variantId']} master exists", p.exists())
            raw = p.read_bytes()
            check(f"{key} {v['variantId']} real WAV bytes",
                  raw[:4] == b"RIFF" and len(raw) > 1000, len(raw))
            pr = probe(p)
            st = pr["streams"][0]
            check(f"{key} {v['variantId']} codec pcm_s24le 48k stereo",
                  st["codec_name"] == "pcm_s24le"
                  and int(st["sample_rate"]) == 48000
                  and int(st["channels"]) == 2, st)
            check(f"{key} {v['variantId']} duration matches manifest",
                  abs(float(pr["format"]["duration"])
                      - m["durationSeconds"]) < 0.002, pr["format"])
            check(f"{key} {v['variantId']} sha matches manifest",
                  sha256_file(p) == m["sha256"])
            check(f"{key} {v['variantId']} size matches manifest",
                  p.stat().st_size == m["sizeBytes"])
            lufs, tp = loudnorm_safe(p)
            tr = decode(p)
            mono = tr.mean(axis=1)
            spec = spectral(mono)
            decoded[v["variantId"]] = tr
            measured[(key, v["variantId"])] = {
                "lufs": lufs, "tp": tp, **spec}
            check(f"{key} {v['variantId']} duration {dur}s",
                  abs(m["durationSeconds"] - dur) < 0.01,
                  m["durationSeconds"])
            check(f"{key} {v['variantId']} LUFS {target_lufs} +/- 1.0",
                  lufs is not None
                  and abs(lufs - target_lufs) <= 1.0, lufs)
            check(f"{key} {v['variantId']} manifest LUFS matches",
                  m["integratedLufs"] is not None
                  and abs(m["integratedLufs"] - lufs) < 0.05,
                  m["integratedLufs"])
            check(f"{key} {v['variantId']} TP <= -7 dBTP",
                  tp <= -7.0, tp)
            check(f"{key} {v['variantId']} centroid {clo}-{chi} Hz",
                  clo <= spec["centroidHz"] <= chi,
                  spec["centroidHz"])
            if prom_max is not None:
                check(f"{key} {v['variantId']} prominence < {prom_max}",
                      spec["prominence400_2000"] < prom_max,
                      spec["prominence400_2000"])
            else:
                check(f"{key} {v['variantId']} prominence recorded "
                      "(not asserted: energy outside 400-2000 Hz)",
                      True, spec["prominence400_2000"])
            check(f"{key} {v['variantId']} manifest spectral matches",
                  abs(v["spectral"]["spectralCentroidHz"]
                      - spec["centroidHz"]) < 0.2, v["spectral"])
            if "dao_swing" in key:
                check(f"{key} {v['variantId']} 3-8k band < 0.10 "
                      "(no bright ring)",
                      spec["band3000_8000"] < 0.10,
                      spec["band3000_8000"])
            elif "brush_stroke" in key:
                check(f"{key} {v['variantId']} 3-8k band >= 0.35 "
                      "(airy paper/water identity)",
                      spec["band3000_8000"] >= 0.35,
                      spec["band3000_8000"])
            elif "mace_swing" in key:
                check(f"{key} {v['variantId']} <500 Hz band >= 0.30 "
                      "(low-end weight)",
                      spec["bandLt500"] >= 0.30, spec["bandLt500"])
                check(f"{key} {v['variantId']} 2.5-5.5k band >= 0.02 "
                      "(not sub-bass only)",
                      spec["band2500_5500"] >= 0.02,
                      spec["band2500_5500"])
            elif "bow_string" in key:
                check(f"{key} {v['variantId']} 2.5-5.5k band >= 0.10 "
                      "(leaf-wind presence)",
                      spec["band2500_5500"] >= 0.10,
                      spec["band2500_5500"])
        # inter-variant distinctness
        ids = [v["variantId"] for v in variants]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                ratio = diff_rms(decoded[ids[i]], decoded[ids[j]])
                check(f"{key} diff-RMS {ids[i]} vs {ids[j]} >= 0.05",
                      ratio >= 0.05, ratio)

    # ---- distinctness vs baselines + between weapons (real bytes)
    centroids = {k: [measured[(k, v)]["centroidHz"]
                     for v in ("v01", "v02", "v03")]
                 for k in CUE_RULES}
    keys = list(CUE_RULES)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            lo = min(abs(a - b) for a in centroids[keys[i]]
                     for b in centroids[keys[j]])
            check(f"centroid gap {keys[i].split('/')[-1]} vs "
                  f"{keys[j].split('/')[-1]} >= 300 Hz",
                  lo >= 300.0, lo)
    for key in keys:
        for vid in ("v01", "v02", "v03"):
            g = measured[(key, vid)]
            check(f"{key.split('/')[-1]} {vid} centroid >=400 Hz from "
                  f"basic_blade ({blade['centroidHz']} Hz)",
                  abs(g["centroidHz"] - blade["centroidHz"]) >= 400.0,
                  g["centroidHz"])
            check(f"{key.split('/')[-1]} {vid} prominence < 1% of "
                  f"parry's ({parry['prominenceMax']})",
                  g["prominence400_2000"]
                  < parry["prominenceMax"] / 100.0,
                  g["prominence400_2000"])
            if "mace_swing" in key:
                check(f"mace {vid} <500 Hz band >= parry + 0.20 "
                      f"(parry {parry['bandLt500']})",
                      g["bandLt500"] >= parry["bandLt500"] + 0.20,
                      g["bandLt500"])
                check(f"mace {vid} centroid <= 700 Hz (low slot, "
                      "not a parry ring)",
                      g["centroidHz"] <= 700.0, g["centroidHz"])
            else:
                check(f"{key.split('/')[-1]} {vid} centroid >=250 Hz "
                      f"from metal_parry ({parry['centroidHz']} Hz)",
                      abs(g["centroidHz"] - parry["centroidHz"])
                      >= 250.0, g["centroidHz"])

    # ---- playlist
    text = PLAYLIST.read_text(encoding="utf-8")
    check("playlist is M3U text", text.startswith("#EXTM3U"))
    check("playlist says NOT_AUDITIONED",
          "NOT_AUDITIONED" in text)
    listed = [ln.strip() for ln in text.splitlines()
              if ln.strip() and not ln.startswith("#")]
    check("playlist lists 14 files (12 drafts + 2 baselines)",
          len(listed) == 14, len(listed))
    for rel in listed:
        check(f"playlist file exists: {rel}",
              (PLAYLIST.parent / rel).exists(), rel)
    for key, cue in cues.items():
        for v in cue["variants"]:
            check(f"playlist lists {v['master']['path']}",
                  ("../../../../" + v["master"]["path"]) in text)

    # ---- runtime untouched + scope
    r = subprocess.run(["git", "status", "--porcelain", "ClientGodot/"],
                       capture_output=True, text=True, cwd=ROOT)
    check("runtime tree untouched (git status ClientGodot/ empty)",
          r.stdout.strip() == "", r.stdout.strip()[:300])
    sys.path.insert(0, str(ROOT / "Tools/Coordination"))
    import check_agent_scope  # noqa: E402
    policy = json.loads((ROOT / "Implementation/Coordination"
                         / "agent_scope_v2.json").read_text(
                             encoding="utf-8"))
    stems = ("dao_swing", "brush_stroke", "mace_swing", "bow_string")
    new_paths = [
        "Tools/MediaProduction/Muse/"
        "build_composed_sfx_me_cp2b_weapons.py",
        "Tools/MediaProduction/Muse/"
        "check_composed_sfx_me_cp2b_weapons_v1.py",
    ]
    for stem in stems:
        for v in ("v01", "v02", "v03"):
            new_paths.append(
                f"Art_Source/Audio/Muse/COMPOSED/sfx/{stem}_{v}.wav")
    new_paths += [
        "Implementation/Content/Audio/Deliveries/"
        "SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json",
        "Implementation/Content/Audio/Deliveries/"
        "SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt",
    ]
    bad = check_agent_scope.violations(
        new_paths, "muse/media-production-20261104", policy)
    check("checkpoint paths in scope (0 violations)", bad == [], bad)

    result = {
        "validator": "check_composed_sfx_me_cp2b_weapons_v1.py",
        "checkpoint": "MEDIA-02 WO39 M39-A CP2 - 4 weapon identities "
                      "SFX draft",
        "decisionId": "DEC-MEDIA-SFX-DRAFT-20261112",
        "branch": "muse/media-production-20261104",
        "checksTotal": len(CHECKS),
        "checksPassed": sum(1 for c in CHECKS if c["pass"]),
        "failures": FAILURES,
        "pass": not FAILURES,
        "baselinesReMeasured": {
            "metal_parry": parry, "basic_blade": blade,
        },
        "measured": {f"{k[0]} {k[1]}": v
                     for k, v in measured.items()},
        "measurementNotes": [
            "Baseline RMS is measured from a true mono decode (-ac 1): "
            "ffmpeg's mono->stereo upmix scales each channel by 0.707, "
            "so a -ac 2 decode under-reads a mono file by 3.01 dB.",
            "Weapon-vs-parry LUFS comparison is conservative: a stereo "
            "render measures ~+3 LU over the same mono content "
            "(BS.1770 channel sum), so the real gap between the "
            "stereo weapon drafts and the mono metal_parry is wider "
            "than the headline LUFS numbers show.",
            "Brush/mace tonal prominence (400-2000 Hz) is recorded, "
            "not asserted: brush energy sits above 2400 Hz and mace "
            "energy below 700 Hz, so the median in 400-2000 Hz is "
            "near the noise floor and the ratio is not a tonality "
            "claim (same note as the grass cue in CP1). The decisive "
            "parry discriminator for mace is its <500 Hz band "
            "(>= parry + 0.20) and centroid <= 700 Hz; for brush it "
            "is the 3200-4200 Hz centroid slot.",
        ],
        "checks": CHECKS,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1)
                   + "\n", encoding="utf-8")
    print(f"validator: {result['checksPassed']}/{result['checksTotal']} "
          f"PASS; failures={FAILURES}", flush=True)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
