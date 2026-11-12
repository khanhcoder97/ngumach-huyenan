"""MEDIA-02 WO37 M-G CP8 validator: fresh-checkout verification of the
M-F CP2 binary delta (scoped -- NOT a repeat checkpoint over the same
783 runtime bytes; Gogi 38 rule 1).

Scope: the 14 new draft v2 mix WAVs from M-F CP2 (content 2d7f02a,
report/head 81f33e6), verified in a FRESH clone made with
GIT_LFS_SKIP_SMUDGE=1 and then a pure-network `git lfs pull -I` of
exactly those 14 paths. This catches the D1 defect class found by
M-G CP7 (working-clone files that were LFS pointers, not real bytes)
for the new delta -- the CP2 checker itself ran in the working clone.

Checks, per mix (13 scene mixes + prologue CIN_000 v2):
  * WAV exists in the fresh clone; first 4 bytes are RIFF (not an
    LFS pointer);
  * sha256 == the M-F CP2 validation JSON (measured in the working
    clone at build time); size == expected;
  * ffprobe: pcm_s16le / 48 kHz / stereo; duration 18.000 s
    (scenes, tol 0.01) or 87.367 s (prologue, tol 0.05);
  * loudness re-measured with ffmpeg loudnorm (single pass,
    print_format=json) matches the CP2 LUFS / true peak within 0.2.
Global:
  * fresh clone HEAD == 81f33e6e061e79ca10778b8961680e7c4b043245;
  * runtime audio file count identical in fresh vs working clone
    (784 files = 783 audio + 1 json -- runtime untouched);
  * delta 129b363..81f33e6 is 45 files with 0 under ClientGodot/;
  * `git lfs ls-files` tracked count + distinct OIDs identical in
    fresh vs working clone.

Exit code 0 iff every check passes. --out writes the JSON verdict
(default: print only). Write --out to scratch, NOT into
Implementation/Reports/MuseMedia/ (a counted root -- see the M-G CP7
re-run caveat); copy the PASS JSON in afterwards.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

EXPECTED_HEAD = "81f33e6e061e79ca10778b8961680e7c4b043245"
BASELINE = "129b363"
LUFS_TOL = 0.2
TP_TOL = 0.2


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def probe(path: Path) -> dict:
    r = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def loudnorm(path: Path) -> tuple[float, float]:
    # Same extraction as the M-F CP2 checker: default verbosity (the
    # JSON summary is printed at info level -- `-v error` suppresses
    # it), parse from the LAST "{" to the last "}".
    r = subprocess.run(
        ["ffmpeg", "-i", str(path), "-vn", "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    err = r.stderr
    data = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def run(cmd, cwd=None):
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return r


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", required=True, help="fresh clone path")
    ap.add_argument("--work", required=True, help="working clone path")
    ap.add_argument("--expected", required=True,
                    help="M-F CP2 validation JSON")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    fresh = Path(args.fresh)
    work = Path(args.work)
    expected = json.loads(Path(args.expected).read_text())

    checks_total = 0
    checks_passed = 0
    failures: list[str] = []
    mixes_out = []

    def check(ok: bool, label: str):
        nonlocal checks_total, checks_passed
        checks_total += 1
        if ok:
            checks_passed += 1
        else:
            failures.append(label)

    # --- global: fresh HEAD
    head = run(["git", "rev-parse", "HEAD"], cwd=fresh).stdout.strip()
    check(head == EXPECTED_HEAD, f"fresh HEAD {head} != {EXPECTED_HEAD}")

    # --- global: runtime audio file counts, fresh vs working
    def audio_count(root: Path) -> int:
        return sum(1 for _ in (root / "ClientGodot" / "assets" / "audio").rglob("*")
                   if _.is_file())

    fresh_audio = audio_count(fresh)
    work_audio = audio_count(work)
    check(fresh_audio == work_audio == 784,
          f"runtime audio file count fresh={fresh_audio} work={work_audio} != 784")

    # --- global: delta file list 129b363..81f33e6
    delta = run(["git", "diff", "--name-only", f"{BASELINE}..{EXPECTED_HEAD[:7]}"],
                cwd=fresh).stdout.split()
    check(len(delta) == 45, f"delta file count {len(delta)} != 45")
    check(not any(p.startswith("ClientGodot/") for p in delta),
          "delta touches ClientGodot/")

    # --- global: LFS tracked counts, fresh vs working
    def lfs_counts(root: Path):
        r = run(["git", "lfs", "ls-files"], cwd=root)
        lines = [ln for ln in r.stdout.splitlines() if ln.strip()]
        oids = {ln.split()[0] for ln in lines}
        return len(lines), len(oids)

    f_lfs, f_oid = lfs_counts(fresh)
    w_lfs, w_oid = lfs_counts(work)
    check((f_lfs, f_oid) == (w_lfs, w_oid) == (2831, 2135),
          f"LFS tracked fresh={f_lfs}/{f_oid} work={w_lfs}/{w_oid} != 2831/2135")

    # --- per mix
    for m in expected["mixes"]:
        rel = m["file"]
        wav = fresh / rel
        rec = {"file": rel, "scene": m["scene"]}
        ok_all = True

        def mcheck(ok: bool, label: str):
            nonlocal ok_all
            if not ok:
                ok_all = False
                failures.append(f"{m['scene']}: {label}")

        checks_total += 1
        if not wav.exists():
            checks_passed += 0
            failures.append(f"{m['scene']}: missing in fresh clone")
            rec["status"] = "MISSING"
            mixes_out.append(rec)
            continue
        checks_passed += 1

        # header RIFF, not LFS pointer
        with open(wav, "rb") as f:
            magic = f.read(4)
        mcheck(magic == b"RIFF", f"header {magic!r} != RIFF (pointer?)")
        checks_total += 1
        if magic == b"RIFF":
            checks_passed += 1

        # sha + size
        got_sha = sha256(wav)
        mcheck(got_sha == m["sha256"],
               f"sha256 {got_sha[:12]} != expected {m['sha256'][:12]}")
        checks_total += 1
        if got_sha == m["sha256"]:
            checks_passed += 1
        got_size = wav.stat().st_size
        mcheck(got_size == m["sizeBytes"],
               f"size {got_size} != {m['sizeBytes']}")
        checks_total += 1
        if got_size == m["sizeBytes"]:
            checks_passed += 1

        # ffprobe
        info = probe(wav)
        stream = info["streams"][0]
        dur = float(info["format"]["duration"])
        exp_dur = m["durationSeconds"]
        tol = 0.05 if m["scene"] == "CIN_000" else 0.01
        mcheck(stream["codec_name"] == "pcm_s16le" and
               int(stream["sample_rate"]) == 48000 and
               int(stream["channels"]) == 2,
               f"format {stream['codec_name']}/{stream['sample_rate']}/"
               f"{stream['channels']} != pcm_s16le/48000/2")
        checks_total += 1
        if (stream["codec_name"] == "pcm_s16le" and
                int(stream["sample_rate"]) == 48000 and
                int(stream["channels"]) == 2):
            checks_passed += 1
        mcheck(abs(dur - exp_dur) <= tol,
               f"duration {dur} != {exp_dur} (tol {tol})")
        checks_total += 1
        if abs(dur - exp_dur) <= tol:
            checks_passed += 1
        rec["durationSeconds"] = dur

        # loudnorm
        lufs, tp = loudnorm(wav)
        rec["integratedLUFS"] = round(lufs, 2)
        rec["truePeakDBTP"] = round(tp, 2)
        mcheck(abs(lufs - m["integratedLUFS"]) <= LUFS_TOL,
               f"LUFS {lufs:.2f} != {m['integratedLUFS']} (tol {LUFS_TOL})")
        checks_total += 1
        if abs(lufs - m["integratedLUFS"]) <= LUFS_TOL:
            checks_passed += 1
        mcheck(abs(tp - m["truePeakDBTP"]) <= TP_TOL,
               f"TP {tp:.2f} != {m['truePeakDBTP']} (tol {TP_TOL})")
        checks_total += 1
        if abs(tp - m["truePeakDBTP"]) <= TP_TOL:
            checks_passed += 1

        rec["sha256"] = got_sha
        rec["sizeBytes"] = got_size
        rec["status"] = "PASS" if ok_all else "FAIL"
        mixes_out.append(rec)

    verdict = {
        "checker": "check_fresh_delta_mg_cp8_v1",
        "checkpoint": "MEDIA-02 WO37 M-G CP8",
        "freshHead": head,
        "baseline": BASELINE,
        "checksTotal": checks_total,
        "checksPassed": checks_passed,
        "failures": failures,
        "status": "PASS" if not failures else "FAIL",
        "runtimeAudioFilesFresh": fresh_audio,
        "runtimeAudioFilesWork": work_audio,
        "deltaFiles": len(delta),
        "lfsTrackedFresh": f_lfs,
        "lfsOidsFresh": f_oid,
        "mixes": mixes_out,
    }
    text = json.dumps(verdict, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n")
    print(text)
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
