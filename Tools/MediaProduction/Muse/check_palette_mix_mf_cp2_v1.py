"""MEDIA-02 WO37 M-F CP2 checker: verify the 14 palette re-mixes
from the real bytes.

Checks, per mix (12 scene v2 + CIN_002 v4 in P0_DRAFT_V4 +
prologue CIN_000 v2):
  * WAV exists; sha256 matches its manifest (size recorded; the
    prologue manifest also carries sizeBytes -- checked equal);
  * ffprobe: pcm_s16le / 48 kHz / stereo; duration 18.000 s
    (scenes, tol 0.01) or 87.367 s (prologue, tol 0.05);
  * loudness re-measured with ffmpeg loudnorm matches the
    manifest LUFS / true peak within 0.2;
  * manifest status == DRAFT_NOT_FINAL, auditionStatus ==
    NOT_AUDITIONED, decisionRef present (owner delegation
    2026-11-12 18:30 JST);
  * per changed VO take: pickup WAV exists, sha256 matches the
    manifest record, duration re-measured from its bytes; fit
    recomputed from the DELIVERY timing file's dialogue window
    (take starts at the window start, take end <= window end,
    slack matches the record within 0.01) -- the prologue uses
    its CP27 segment starts + the audible-end slot rule;
  * waveform integrity: the gain-scaled pickup correlates with
    the mix span at the take position: corr at lag 0 >= 0.75,
    corr at lag 0 is the sharp peak of a +/-100 ms lag scan
    (lag-0 corr exceeds the best off-lag |corr| by >= 0.35 --
    a voiced take legitimately keeps ~0.25 correlation at a
    10 ms shift, so the margin is absolute, not a ratio), and
    the take explains
    >= 50% of the span energy. (A quiet take over an unducked
    bed legitimately dilutes corr -- CIN_010 measures 0.813 with
    a zero off-lag floor -- while frame-drop defects of the kind
    found in the CP27 prologue render collapse corr to ~0 at
    EVERY lag; the lag scan is the discriminator.)
Global:
  * git status --porcelain -- ClientGodot/ is EMPTY (runtime
    tree untouched; the runtime still embeds the v1 mixes and
    the runtime audio count stays 783);
  * the CIN_018 player and CIN_020 recipient records keep their
    PLACEHOLDER flags in the manifests.

Exit code 0 iff every check passes. --out writes the JSON
verdict (default: print only).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
SR = 48000

SCENES = ["CIN_006", "CIN_008", "CIN_010", "CIN_011", "CIN_012",
          "CIN_013", "CIN_014", "CIN_015", "CIN_016", "CIN_017",
          "CIN_018", "CIN_020"]

FAILURES: list[str] = []
CHECKS = 0


def check(cond: bool, label: str) -> None:
    global CHECKS
    CHECKS += 1
    if not cond:
        FAILURES.append(label)
        print(f"FAIL: {label}")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(path)], capture_output=True, text=True)
    return json.loads(r.stdout)


def loudnorm(path: Path) -> tuple[float, float]:
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vn", "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    err = r.stderr
    d = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return float(d["input_i"]), float(d["input_tp"])


def load_wav(path: Path) -> np.ndarray:
    with wave.open(str(path), "rb") as w:
        ch, n = w.getnchannels(), w.getnframes()
        x = np.frombuffer(w.readframes(n),
                          dtype=np.int16).astype(np.float64) / 32768.0
    return x.reshape(-1, ch).mean(axis=1) if ch > 1 else x


def audible_end(path: Path, thr_db: float = -50.0) -> float:
    x = load_wav(path)
    idx = np.nonzero(np.abs(x) > 10 ** (thr_db / 20))[0]
    return (idx[-1] + 1) / SR if len(idx) else 0.0


def timing_window(scene: str, shot_id: str) -> list[float]:
    t = json.loads((ROOT / "Implementation/Content/Narrative/"
                    f"Deliveries/{scene}/{scene}_timing_v1.json")
                   .read_text(encoding="utf-8"))
    for sh in t["shots"]:
        if sh["shotId"] == shot_id and sh.get("dialogue"):
            return sh["dialogue"]["windowSeconds"]
    raise KeyError(f"{scene}/{shot_id} has no dialogue window")


def verify_take(mix_audio: np.ndarray, scene: str, rec: dict,
                gain_db: float, tag: str) -> None:
    pk = ROOT / rec["paletteTakeFile"]
    check(pk.exists(), f"{tag}: pickup missing {pk}")
    if not pk.exists():
        return {"takeKey": rec["takeKey"]}
    check(sha256(pk) == rec["paletteTakeSha256"],
          f"{tag}: pickup sha mismatch")
    p = probe(pk)
    dur = float(p["format"]["duration"])
    check(abs(dur - rec["paletteTakeDurationSeconds"]) <= 0.01,
          f"{tag}: pickup duration {dur} != record "
          f"{rec['paletteTakeDurationSeconds']}")
    if scene == "CIN_000":
        start = rec["cp27SegmentStartSeconds"]
        slot_end = rec["slotEndSeconds"]
        end = start + dur
        a_end = start + audible_end(pk)
        check(a_end <= slot_end + 0.01,
              f"{tag}: audible end {a_end} past slot {slot_end}")
        check(abs(rec["paletteEndSeconds"] - end) <= 0.01,
              f"{tag}: paletteEndSeconds mismatch")
    else:
        win = timing_window(scene, rec["shotId"])
        check([round(x, 3) for x in win] ==
              [round(x, 3) for x in rec["windowSeconds"]],
              f"{tag}: record window {rec['windowSeconds']} != "
              f"timing window {win}")
        start = win[0]
        end = start + dur
        check(abs(rec["takeStartSeconds"] - start) <= 0.001,
              f"{tag}: take start != window start")
        check(abs(rec["takeEndSeconds"] - end) <= 0.01,
              f"{tag}: take end mismatch")
        check(end <= win[1] + 0.001 and rec["fit"] == "FITS",
              f"{tag}: take does not fit window")
        check(abs(rec["slackSeconds"] - (win[1] - end)) <= 0.01,
              f"{tag}: slack mismatch")
    # waveform integrity vs the mix span
    take = load_wav(pk)
    seg = mix_audio[int(start * SR):int(start * SR) + len(take)]
    check(len(seg) == len(take), f"{tag}: mix span truncated")
    out = {"takeKey": rec["takeKey"]}
    if len(seg) == len(take):
        g = 10 ** (gain_db / 20)
        t = take - take.mean()

        def corr_at(lag_ms: float) -> float:
            a = int((start + lag_ms / 1000) * SR)
            sg = mix_audio[a:a + len(take)]
            if len(sg) < len(take):
                return 0.0
            sg = sg - sg.mean()
            d = np.linalg.norm(t) * np.linalg.norm(sg)
            return float(np.dot(t, sg) / d) if d else 0.0

        corr = corr_at(0)
        off = max(abs(corr_at(l)) for l in
                  range(-100, 101, 10) if l != 0)
        resid = seg - g * take
        frac = 1 - float(np.sum(resid ** 2) / np.sum(seg ** 2))
        check(corr >= 0.75, f"{tag}: corr {corr:.3f} < 0.75")
        check(corr - off >= 0.35,
              f"{tag}: corr {corr:.3f} not a sharp lag-0 peak "
              f"(best off-lag |corr| {off:.3f})")
        check(frac >= 0.5, f"{tag}: take energy fraction "
                           f"{frac:.3f} < 0.5")
        out.update({"corrLag0": round(corr, 3),
                    "bestOffLagAbsCorr": round(off, 3),
                    "takeEnergyFraction": round(frac, 3)})
    return out


def verify_scene_mix(scene: str, wav_rel: str, man_rel: str) -> dict:
    man = json.loads((ROOT / man_rel).read_text(encoding="utf-8"))
    mix = man["scenes"][0]["mix"]
    wav = ROOT / wav_rel
    tag = scene
    check(wav.exists(), f"{tag}: mix WAV missing")
    check(mix["file"] == wav.name, f"{tag}: manifest file name")
    check(sha256(wav) == mix["sha256"], f"{tag}: mix sha mismatch")
    p = probe(wav)
    st = p["streams"][0]
    check(st["codec_name"] == "pcm_s16le" and
          int(st["sample_rate"]) == SR and st["channels"] == 2,
          f"{tag}: format {st['codec_name']}/{st['sample_rate']}/"
          f"{st['channels']}")
    dur = float(p["format"]["duration"])
    check(abs(dur - 18.0) <= 0.01, f"{tag}: duration {dur} != 18")
    check(abs(mix["durationSeconds"] - dur) <= 0.01,
          f"{tag}: manifest duration mismatch")
    lufs, tp = loudnorm(wav)
    check(abs(lufs - float(mix["integratedLUFS"])) <= 0.2,
          f"{tag}: LUFS {lufs} != manifest {mix['integratedLUFS']}")
    check(abs(tp - float(mix["truePeakDBTP"])) <= 0.2,
          f"{tag}: TP {tp} != manifest {mix['truePeakDBTP']}")
    check(man.get("status") == "DRAFT_NOT_FINAL",
          f"{tag}: status != DRAFT_NOT_FINAL")
    check(man.get("auditionStatus") == "NOT_AUDITIONED",
          f"{tag}: auditionStatus != NOT_AUDITIONED")
    dr = man.get("decisionRef") or {}
    check("2026-11-12" in json.dumps(dr), f"{tag}: decisionRef")
    audio = load_wav(wav)
    takes = [verify_take(audio, scene, rec, 0.0,
                         f"{tag}/{rec['takeKey']}")
             for rec in man["paletteRemix"]["changes"]]
    return {"scene": scene, "file": wav_rel, "sha256": mix["sha256"],
            "sizeBytes": wav.stat().st_size,
            "durationSeconds": round(dur, 3),
            "integratedLUFS": lufs, "truePeakDBTP": tp,
            "takes": takes}


def verify_prologue() -> dict:
    man_rel = ("Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/"
               "CIN_000_MIX_V2_manifest_v1.json")
    wav_rel = ("Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/"
               "CIN_000_mix_draft_v2.wav")
    man = json.loads((ROOT / man_rel).read_text(encoding="utf-8"))
    wav = ROOT / wav_rel
    tag = "CIN_000"
    check(wav.exists(), f"{tag}: mix WAV missing")
    check(sha256(wav) == man["sha256"], f"{tag}: mix sha mismatch")
    check(wav.stat().st_size == man["sizeBytes"],
          f"{tag}: mix size != manifest sizeBytes")
    p = probe(wav)
    st = p["streams"][0]
    check(st["codec_name"] == "pcm_s16le" and
          int(st["sample_rate"]) == SR and st["channels"] == 2,
          f"{tag}: format")
    dur = float(p["format"]["duration"])
    check(abs(dur - 87.367) <= 0.05, f"{tag}: duration {dur}")
    lufs, tp = loudnorm(wav)
    check(abs(lufs - float(man["integratedLufs"])) <= 0.2,
          f"{tag}: LUFS {lufs} != {man['integratedLufs']}")
    check(abs(tp - float(man["truePeakDbtp"])) <= 0.2,
          f"{tag}: TP {tp} != {man['truePeakDbtp']}")
    check(man.get("status") == "DRAFT_NOT_FINAL", f"{tag}: status")
    check(man.get("auditionStatus") == "NOT_AUDITIONED",
          f"{tag}: auditionStatus")
    check("2026-11-12" in json.dumps(man.get("decisionRef") or {}),
          f"{tag}: decisionRef")
    audio = load_wav(wav)
    takes = [verify_take(audio, "CIN_000", rec,
                         rec["appliedGainDb"],
                         f"{tag}/{rec['takeKey']}")
             for rec in man["paletteRemix"]["narrationChanges"]]
    return {"scene": "CIN_000", "file": wav_rel,
            "sha256": man["sha256"], "sizeBytes": man["sizeBytes"],
            "durationSeconds": round(dur, 3),
            "integratedLUFS": lufs, "truePeakDBTP": tp,
            "takes": takes}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    results = []
    for scene in SCENES:
        u = scene.replace("_", "")
        results.append(verify_scene_mix(
            scene,
            f"Art_Source/Audio/Muse/MIX/{u}_DRAFT_V2/"
            f"{scene}_mix_draft_v2.wav",
            f"Art_Source/Audio/Muse/MIX/{u}_DRAFT_V2/"
            f"{u}_MIX_V2_manifest_v1.json"))
    results.append(verify_scene_mix(
        "CIN_002",
        "Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/"
        "CIN_002_mix_draft_v4.wav",
        "Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/"
        "P0_MIX_V4_manifest_v1.json"))
    results.append(verify_prologue())

    # placeholder flags kept
    for scene, u in (("CIN_018", "CIN018"), ("CIN_020", "CIN020")):
        txt = (ROOT / f"Art_Source/Audio/Muse/MIX/{u}_DRAFT_V2/"
               f"{u}_MIX_V2_manifest_v1.json").read_text(
                   encoding="utf-8")
        check("PLACEHOLDER" in txt,
              f"{scene}: PLACEHOLDER flag missing from manifest")

    r = subprocess.run(["git", "status", "--porcelain", "--",
                        "ClientGodot/"], cwd=ROOT,
                       capture_output=True, text=True)
    check(r.stdout.strip() == "",
          f"runtime tree dirty: {r.stdout[:200]}")

    verdict = {
        "checker": "check_palette_mix_mf_cp2_v1",
        "checkpoint": "MEDIA-02 WO37 M-F CP2",
        "checksTotal": CHECKS,
        "checksPassed": CHECKS - len(FAILURES),
        "failures": FAILURES,
        "status": "PASS" if not FAILURES else "FAIL",
        "runtimeClientGodotDirty": bool(r.stdout.strip()),
        "mixes": results,
    }
    print(json.dumps({"status": verdict["status"],
                      "checks": f"{verdict['checksPassed']}/"
                                f"{CHECKS}"}, ensure_ascii=False))
    if args.out:
        Path(args.out).write_text(
            json.dumps(verdict, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
