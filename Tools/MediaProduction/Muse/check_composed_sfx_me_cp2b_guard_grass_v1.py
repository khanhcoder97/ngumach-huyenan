#!/usr/bin/env python3
"""Independent validator: MEDIA-02 WO39 M39-A CP1, guard + grass SFX.

Re-reads EVERYTHING from the real bytes on disk; imports nothing from
the builder. Checks:
  1. manifest parses; counts 2 cues / 6 variants; decision/approval refs.
  2. each master is a real WAV (RIFF, not an LFS pointer), ffprobe
     pcm_s24le 48 kHz stereo, duration/sha256/size match the manifest.
  3. loudness re-measured with ffmpeg loudnorm: guard LUFS -27.5 +/- 1,
     TP <= -9 dBTP; grass LUFS unmeasurable (short clip, CP08 note),
     TP <= -7 dBTP; grass RMS -25.0 +/- 0.75 dBFS.
  4. spectrum re-measured (numpy FFT): guard centroid 1000-1600 Hz,
     tonal prominence < 200, 3-8 kHz band < 0.10; grass centroid
     1800-3000 Hz, 2.5-5.5 kHz band >= 0.35.
  5. baselines re-measured from the real ported runtime files AND
     cross-checked by sha256 against SFX_UI_pack_v1.json: guard must
     sit >= 250 Hz from metal_parry's centroid, prominence < 1% of
     parry's, >= 2 LU quieter, >= 1000 Hz from basic_blade; grass
     must sit >= 400 Hz from every footstep sibling's centroid with
     a 2.5-5.5 kHz band at least 0.10 above each sibling's.
  6. inter-variant waveform distinctness (diff RMS ratio >= 0.05).
  7. audition playlist lists all 6 masters + 4 baselines; every
     listed file exists.
  8. runtime untouched: `git status --porcelain ClientGodot/` empty;
     no checkpoint file lives outside the policy media/tool roots.
Writes MEDIA02_WO39_M39A_CP1_GUARD_GRASS_VALIDATION_20261112.json.
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
            / "SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json")
PLAYLIST = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt")
SFX_PACK = (ROOT / "Implementation/Content/Audio/Deliveries"
            / "SFX_UI_pack_v1.json")
OUT = (ROOT / "Implementation/Reports/MuseMedia"
       / "MEDIA02_WO39_M39A_CP1_GUARD_GRASS_VALIDATION_20261112.json")

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
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path),
         "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"decode failed for {path}: "
                           f"{r.stderr.decode()[-500:]}")
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, 2).astype(
        np.float64)


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
    check("counts 2 cues / 6 variants",
          pack.get("counts") == {"cues": 2, "variants": 6},
          pack.get("counts"))
    cues = {c["cueKey"]: c for c in pack["cues"]}
    check("cue keys",
          set(cues) == {"SFX/COMBAT/guard_expire",
                        "SFX/WORLD/step_grass"}, list(cues))
    for key, cue in cues.items():
        check(f"{key} trigger UNSUPPORTED, no binding",
              cue.get("triggerStatus") == "UNSUPPORTED"
              and cue.get("binding") is None, cue.get("triggerStatus"))
        check(f"{key} provenance composed",
              cue.get("provenance") == "ORIGINAL_COMPOSED_BY_MUSE")

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
                for k in ("centroidHz", "band2500_5500", "band3000_8000")}
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
    stone = baseline_stats("SFX/WORLD/step_stone", "world", "step_stone")
    wood = baseline_stats("SFX/WORLD/step_wood", "world", "step_wood")
    mud = baseline_stats("SFX/WORLD/step_mud", "world", "step_mud")
    print(f"baselines: parry={parry} blade={blade} stone={stone} "
          f"wood={wood} mud={mud}", flush=True)

    # ---- each variant: bytes + loudness + spectrum + distinctness
    measured = {}
    for key, cue in cues.items():
        is_guard = "guard_expire" in key
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
            rms = float(20 * np.log10(
                np.sqrt((mono ** 2).mean()) + 1e-12))
            decoded[v["variantId"]] = tr
            measured[(key, v["variantId"])] = {
                "lufs": lufs, "tp": tp, "rms": round(rms, 2), **spec}
            if is_guard:
                check(f"{key} {v['variantId']} duration 0.50s",
                      abs(m["durationSeconds"] - 0.50) < 0.01,
                      m["durationSeconds"])
                check(f"{key} {v['variantId']} LUFS -27.5 +/- 1.0",
                      lufs is not None
                      and abs(lufs - (-27.5)) <= 1.0, lufs)
                check(f"{key} {v['variantId']} manifest LUFS matches",
                      m["integratedLufs"] is not None
                      and abs(m["integratedLufs"] - lufs) < 0.05,
                      m["integratedLufs"])
                check(f"{key} {v['variantId']} TP <= -9 dBTP",
                      tp <= -9.0, tp)
                check(f"{key} {v['variantId']} centroid 1000-1600 Hz",
                      1000.0 <= spec["centroidHz"] <= 1600.0,
                      spec["centroidHz"])
                check(f"{key} {v['variantId']} prominence < 200 "
                      "(broadband, not a metallic ring)",
                      spec["prominence400_2000"] < 200.0,
                      spec["prominence400_2000"])
                check(f"{key} {v['variantId']} 3-8k band < 0.10",
                      spec["band3000_8000"] < 0.10,
                      spec["band3000_8000"])
                check(f"{key} {v['variantId']} manifest spectral matches",
                      abs(v["spectral"]["spectralCentroidHz"]
                          - spec["centroidHz"]) < 0.2, v["spectral"])
            else:
                check(f"{key} {v['variantId']} duration 0.21s",
                      abs(m["durationSeconds"] - 0.21) < 0.01,
                      m["durationSeconds"])
                check(f"{key} {v['variantId']} LUFS unmeasurable "
                      "(short clip, CP08 note)",
                      lufs is None and m["integratedLufs"] is None
                      and "loudnormNote" in m, lufs)
                check(f"{key} {v['variantId']} TP <= -7 dBTP",
                      tp <= -7.0, tp)
                check(f"{key} {v['variantId']} RMS -25.0 +/- 0.75 dBFS",
                      abs(rms - (-25.0)) <= 0.75, round(rms, 2))
                check(f"{key} {v['variantId']} manifest RMS matches",
                      abs(v["rmsDbfs"] - rms) < 0.05, v["rmsDbfs"])
                check(f"{key} {v['variantId']} centroid 1800-3000 Hz",
                      1800.0 <= spec["centroidHz"] <= 3000.0,
                      spec["centroidHz"])
                check(f"{key} {v['variantId']} 2.5-5.5k band >= 0.35",
                      spec["band2500_5500"] >= 0.35,
                      spec["band2500_5500"])
        # inter-variant distinctness
        ids = [v["variantId"] for v in variants]
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                ratio = diff_rms(decoded[ids[i]], decoded[ids[j]])
                check(f"{key} diff-RMS {ids[i]} vs {ids[j]} >= 0.05",
                      ratio >= 0.05, ratio)

    # ---- distinctness vs baselines (measured above, from real bytes)
    for vid in ("v01", "v02", "v03"):
        g = measured[("SFX/COMBAT/guard_expire", vid)]
        check(f"guard {vid} centroid >=250 Hz from metal_parry "
              f"({parry['centroidHz']} Hz)",
              abs(g["centroidHz"] - parry["centroidHz"]) >= 250.0,
              g["centroidHz"])
        check(f"guard {vid} prominence < 1% of parry's "
              f"({parry['prominenceMax']})",
              g["prominence400_2000"] < parry["prominenceMax"] / 100.0,
              g["prominence400_2000"])
        check(f"guard {vid} >=2 LU quieter than parry "
              f"({parry['lufsMean']} LUFS)",
              g["lufs"] <= parry["lufsMean"] - 2.0, g["lufs"])
        check(f"guard {vid} centroid >=1000 Hz from basic_blade "
              f"({blade['centroidHz']} Hz)",
              abs(g["centroidHz"] - blade["centroidHz"]) >= 1000.0,
              g["centroidHz"])
        s = measured[("SFX/WORLD/step_grass", vid)]
        for name, sib in (("stone", stone), ("wood", wood),
                          ("mud", mud)):
            check(f"grass {vid} centroid >=400 Hz from step_{name} "
                  f"({sib['centroidHz']} Hz)",
                  abs(s["centroidHz"] - sib["centroidHz"]) >= 400.0,
                  s["centroidHz"])
            check(f"grass {vid} 2.5-5.5k band >= {name} + 0.10 "
                  f"({sib['band2500_5500']})",
                  s["band2500_5500"] >= sib["band2500_5500"] + 0.10,
                  s["band2500_5500"])

    # ---- playlist
    text = PLAYLIST.read_text(encoding="utf-8")
    check("playlist is M3U text", text.startswith("#EXTM3U"))
    check("playlist says NOT_AUDITIONED",
          "NOT_AUDITIONED" in text)
    listed = [ln.strip() for ln in text.splitlines()
              if ln.strip() and not ln.startswith("#")]
    check("playlist lists 10 files (6 drafts + 4 baselines)",
          len(listed) == 10, len(listed))
    for rel in listed:
        check(f"playlist file exists: {rel}",
              (ROOT / rel).exists() if not rel.startswith("..")
              else (PLAYLIST.parent / rel).exists(), rel)
    for key, cue in cues.items():
        for v in cue["variants"]:
            check(f"playlist lists {v['master']['path']}",
                  v["master"]["path"] in text
                  or ("../../../" + v["master"]["path"]) in text)

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
    new_paths = [
        "Tools/MediaProduction/Muse/"
        "build_composed_sfx_me_cp2b_guard_grass.py",
        "Tools/MediaProduction/Muse/"
        "check_composed_sfx_me_cp2b_guard_grass_v1.py",
        "Art_Source/Audio/Muse/COMPOSED/sfx/guard_expire_v01.wav",
        "Art_Source/Audio/Muse/COMPOSED/sfx/guard_expire_v02.wav",
        "Art_Source/Audio/Muse/COMPOSED/sfx/guard_expire_v03.wav",
        "Art_Source/Audio/Muse/COMPOSED/sfx/step_grass_v01.wav",
        "Art_Source/Audio/Muse/COMPOSED/sfx/step_grass_v02.wav",
        "Art_Source/Audio/Muse/COMPOSED/sfx/step_grass_v03.wav",
        "Implementation/Content/Audio/Deliveries/"
        "SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json",
        "Implementation/Content/Audio/Deliveries/"
        "SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt",
    ]
    bad = check_agent_scope.violations(
        new_paths, "muse/media-production-20261104", policy)
    check("checkpoint paths in scope (0 violations)", bad == [], bad)

    result = {
        "validator": "check_composed_sfx_me_cp2b_guard_grass_v1.py",
        "checkpoint": "MEDIA-02 WO39 M39-A CP1 - guard + grass SFX draft",
        "decisionId": "DEC-MEDIA-SFX-DRAFT-20261112",
        "branch": "muse/media-production-20261104",
        "checksTotal": len(CHECKS),
        "checksPassed": sum(1 for c in CHECKS if c["pass"]),
        "failures": FAILURES,
        "pass": not FAILURES,
        "baselinesReMeasured": {
            "metal_parry": parry, "basic_blade": blade,
            "step_stone": stone, "step_wood": wood, "step_mud": mud,
        },
        "measured": {f"{k[0]} {k[1]}": v
                     for k, v in measured.items()},
        "measurementNotes": [
            "Baseline RMS is measured from a true mono decode (-ac 1): "
            "ffmpeg's mono->stereo upmix scales each channel by 0.707, "
            "so a -ac 2 decode under-reads a mono file by 3.01 dB. "
            "Grass RMS is the mono-fold (mean of channels) of a true "
            "stereo master -- the comparable figure for a cue played "
            "centred under an equal-power pan law.",
            "Guard-vs-parry LUFS comparison is conservative: a stereo "
            "render measures ~+3 LU over the same mono content "
            "(BS.1770 channel sum), so the real gap between the "
            "stereo guard drafts and the mono metal_parry is wider "
            "than the headline LUFS numbers show.",
            "Grass tonal prominence (400-2000 Hz) is recorded, not "
            "asserted: the cue's energy sits above 1800 Hz, so the "
            "median in 400-2000 Hz is near the noise floor and the "
            "ratio is not a tonality claim.",
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
