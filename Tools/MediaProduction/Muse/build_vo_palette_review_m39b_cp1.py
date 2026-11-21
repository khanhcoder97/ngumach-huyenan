#!/usr/bin/env python3
"""MEDIA-02 WO39 M39-B checkpoint 1: level-matched A/B review comparison
of the M-F CP1 voice palette.

Goi 39 (Codex, issue #116 comment 6815238814; disposition doc
`Implementation/Work_Orders/39_HANDOFF_DISPOSITION_AND_NEXT_DELIVERIES_20261112.md`,
merged to integration as PR #131 @ f3db6b3) M39-B allows exactly this:
"duoc lam level-matched review comparison tren palette hien co, khong
thay runtime/commit final voice" -- no casting choice exists yet, so the
originals stay; this checkpoint makes the choice listenable.

For each of the 20 M-F CP1 palette takes, render BOTH sides gain-matched
to one pair level so the director judges voice, not volume:

  A = canonical take (Helio/Aria, as embedded in the scene mixes)
  B = palette pickup (distinct fictional system voice, M-F CP1)

Pair target is -23.00 LUFS integrated, except where the -1.00 dBTP
true-peak ceiling forces a lower pair level: the pair level is
min(-23.00, loudest level both sides can reach without breaching the
ceiling). Renders are GAIN-ONLY (ffmpeg `volume`, no EQ/compression/
limiting, no re-synthesis): same codec pcm_s16le, 48 kHz, mono, same
sample count as the source. No mix, timing, SRT, pronunciation table
or runtime file is touched; runtime audio stays 783.

Sources (re-hashed + re-measured from real bytes, never trusted from
the manifest alone):
  Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json
  (M-F CP1; canonical takes in Art_Source/Audio/Muse/VO/{P0_DRAFT,
  CIN006_DRAFT, CAMPAIGN_DRAFT, PROLOGUE_DRAFT}, palette takes in
  Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1/)

Outputs:
  Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1/  (40 WAV)
  Implementation/Content/Audio/Deliveries/VO_PALETTE_REVIEW_M39B_v1.json
  Implementation/Reports/MuseMedia/vo_palette_review_m39b_playlist.txt (M3U)

Status throughout: DRAFT / NOT_AUDITIONED / REVIEW_ONLY. Adoption of
any palette voice into a mix is a Codex/director decision (M-F CP2
follow-up). The player take stays VOICE_PLACEHOLDER_ONLY and the
letter-recipient take stays a neutral placeholder, not a casting
decision.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PACK = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json"
OUT_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1"
DELIVERIES = ROOT / "Implementation/Content/Audio/Deliveries"
REPORTS = ROOT / "Implementation/Reports/MuseMedia"

CHECKPOINT = "MEDIA-02 WO39 M39-B CP1"
BRANCH = "muse/media-production-20261104"
TARGET_LUFS = -23.00
TP_CEILING_DBTP = -1.00
# tolerances (same ffmpeg loudnorm method as M-F CP1, same bytes)
PRE_TOL_LUFS = 0.15
PRE_TOL_TP = 0.15
POST_TOL_LUFS = 0.30
POST_MAX_TP = -1.00
DUR_TOL_S = 0.002


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        fail(f"command failed ({r.returncode}): {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def probe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error",
             "-show_entries", "stream=codec_name,sample_rate,channels",
             "-show_entries", "format=duration,size",
             "-of", "json", str(path)])
    return json.loads(r.stdout)


def loudnorm(path: Path) -> dict:
    r = run(["ffmpeg", "-i", str(path), "-vn", "-af",
             "loudnorm=print_format=json", "-f", "null", "-"])
    tail = r.stderr.strip().splitlines()
    start = next(i for i, line in enumerate(tail) if line.strip() == "{")
    end = next(i for i, line in enumerate(tail) if line.strip() == "}")
    return json.loads("\n".join(tail[start:end + 1]))


def measure(path: Path) -> dict:
    p = probe(path)
    stream = p["streams"][0]
    ln = loudnorm(path)
    return {
        "durationSeconds": round(float(p["format"]["duration"]), 3),
        "integratedLufs": round(float(ln["input_i"]), 2),
        "truePeakDbtp": round(float(ln["input_tp"]), 2),
        "codec": stream["codec_name"],
        "sampleRate": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "bytes": int(p["format"]["size"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    global ROOT, PACK, OUT_DIR, DELIVERIES, REPORTS
    ROOT = Path(args.root).resolve()
    PACK = ROOT / "Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json"
    OUT_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1"
    DELIVERIES = ROOT / "Implementation/Content/Audio/Deliveries"
    REPORTS = ROOT / "Implementation/Reports/MuseMedia"

    pack = json.loads(PACK.read_text(encoding="utf-8"))
    takes = pack["takes"]
    if len(takes) != 20:
        fail(f"expected 20 palette takes, pack has {len(takes)}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pairs = []
    for t in takes:
        c = t["canonicalTake"]
        p = t["paletteTake"]
        canon_path = ROOT / c["dir"] / c["file"]
        pal_path = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1" / p["wav"]
        for label, path, exp_sha in (("canonical", canon_path, c["sha256"]),
                                     ("palette", pal_path, p["wavSha256"])):
            if not path.exists():
                fail(f"{t['takeKey']} {label} missing: {path}")
            got = sha256(path)
            if got != exp_sha:
                fail(f"{t['takeKey']} {label} sha mismatch: {got[:12]} != {exp_sha[:12]}")
        # re-measure pre levels from real bytes; cross-check vs M-F CP1 manifest
        cm = measure(canon_path)
        pm = measure(pal_path)
        for label, m, exp_lufs, exp_tp in (
                ("canonical", cm, c["integratedLufs"], c["truePeakDbtp"]),
                ("palette", pm, p["integratedLufs"], p["truePeakDbtp"])):
            if abs(m["integratedLufs"] - exp_lufs) > PRE_TOL_LUFS:
                fail(f"{t['takeKey']} {label} LUFS drift: measured {m['integratedLufs']} "
                     f"vs manifest {exp_lufs}")
            if abs(m["truePeakDbtp"] - exp_tp) > PRE_TOL_TP:
                fail(f"{t['takeKey']} {label} TP drift: measured {m['truePeakDbtp']} "
                     f"vs manifest {exp_tp}")
            if (m["codec"], m["sampleRate"], m["channels"]) != ("pcm_s16le", 48000, 1):
                fail(f"{t['takeKey']} {label} unexpected format: {m}")
        # pair target: -23 unless the TP ceiling forces lower
        achievable = []
        for m in (cm, pm):
            max_gain = TP_CEILING_DBTP - m["truePeakDbtp"]
            achievable.append(m["integratedLufs"] + max_gain)
        pair_target = round(min(TARGET_LUFS, min(achievable)), 2)
        ceiling_limited = pair_target < TARGET_LUFS - 0.005
        sides = []
        for side, path, m, voice_label in (
                ("A", canon_path, cm, "canonical"),
                ("B", pal_path, pm, "palette")):
            gain_db = round(pair_target - m["integratedLufs"], 2)
            out_name = f"{t['takeKey']}_{side}_{voice_label}_lm_v1.wav"
            out_path = OUT_DIR / out_name
            run(["ffmpeg", "-y", "-v", "error", "-i", str(path),
                 "-af", f"volume={gain_db:.2f}dB",
                 "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "1", str(out_path)])
            post = measure(out_path)
            if abs(post["durationSeconds"] - m["durationSeconds"]) > DUR_TOL_S:
                fail(f"{t['takeKey']} {side} duration changed: "
                     f"{m['durationSeconds']} -> {post['durationSeconds']}")
            if abs(post["integratedLufs"] - pair_target) > POST_TOL_LUFS:
                fail(f"{t['takeKey']} {side} post LUFS {post['integratedLufs']} "
                     f"misses pair target {pair_target}")
            if post["truePeakDbtp"] > POST_MAX_TP + 0.01:
                fail(f"{t['takeKey']} {side} post TP {post['truePeakDbtp']} "
                     f"breaches ceiling {POST_MAX_TP}")
            if (post["codec"], post["sampleRate"], post["channels"]) != ("pcm_s16le", 48000, 1):
                fail(f"{t['takeKey']} {side} render format changed: {post}")
            sides.append({
                "side": side,
                "kind": voice_label,
                "sourceFile": path.relative_to(ROOT).as_posix(),
                "sourceSha256": sha256(path),
                "preIntegratedLufs": m["integratedLufs"],
                "preTruePeakDbtp": m["truePeakDbtp"],
                "appliedGainDb": gain_db,
                "renderFile": f"Art_Source/Audio/Muse/VO/PALETTE_REVIEW_M39B_v1/{out_name}",
                "renderSha256": sha256(out_path),
                "renderBytes": out_path.stat().st_size,
                "postIntegratedLufs": post["integratedLufs"],
                "postTruePeakDbtp": post["truePeakDbtp"],
                "durationSeconds": post["durationSeconds"],
            })
        pairs.append({
            "takeKey": t["takeKey"],
            "takeId": t["takeId"],
            "kind": t["kind"],
            "role": t["role"],
            "speakerDisplay": t["speakerDisplay"],
            "voice": t["voice"],
            "voiceLabel": t["voiceLabel"],
            "previousVoice": t["previousVoice"],
            "paletteChange": t["paletteChange"],
            "text": t["text"],
            "windowSceneSeconds": t.get("windowSceneSeconds"),
            "windowStatus": t.get("windowStatus"),
            "fit": t.get("fit"),
            "slackSeconds": t.get("slackSeconds"),
            "pairTargetLufs": pair_target,
            "ceilingLimited": ceiling_limited,
            "pairLevelSpreadLu": round(abs(sides[0]["postIntegratedLufs"] - sides[1]["postIntegratedLufs"]), 2),
            "sides": sides,
        })

    manifest = {
        "manifestId": "NGM_VO_PALETTE_REVIEW_M39B_V1",
        "checkpoint": CHECKPOINT,
        "decisionId": "DEC-MEDIA-P0-20261105",
        "goi39Ref": "Codex Gói 39, issue #116 comment 6815238814; disposition Implementation/Work_Orders/39_HANDOFF_DISPOSITION_AND_NEXT_DELIVERIES_20261112.md (PR #131 merged f3db6b3)",
        "workOrderRef": "WO39 M39-B",
        "branch": BRANCH,
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "reviewOnly": True,
        "method": "Gain-only level match (ffmpeg volume, no EQ/compression/limiting/re-synthesis). Pair target -23.00 LUFS integrated unless the -1.00 dBTP true-peak ceiling forces a lower pair level. All measurements from real bytes (ffprobe + ffmpeg loudnorm, same method as M-F CP1).",
        "targetLufs": TARGET_LUFS,
        "truePeakCeilingDbtp": TP_CEILING_DBTP,
        "sourceManifest": "Implementation/Content/Audio/Deliveries/VO_PALETTE_PICKUPS_pack_v1.json (M-F CP1)",
        "counts": {
            "pairs": len(pairs),
            "renders": 2 * len(pairs),
            "dialoguePairs": sum(1 for x in pairs if x["kind"] == "dialogue"),
            "alternatePairs": sum(1 for x in pairs if x["kind"] == "alternate"),
            "narrationPairs": sum(1 for x in pairs if x["kind"] == "narration"),
            "ceilingLimitedPairs": sum(1 for x in pairs if x["ceilingLimited"]),
        },
        "notes": [
            "A = canonical take (voice embedded in the scene mixes). B = palette pickup (M-F CP1 distinct fictional voice). Within each pair A and B sit at the same pair level, so the director judges voice, not volume.",
            "Ly An has no pair: her voice (Aria) was KEPT in M-F CP1, no pickup exists.",
            "CIN018_S03 player take stays VOICE_PLACEHOLDER_ONLY; CIN020_S03 recipient take stays a neutral placeholder (ElvenWizard). Neither is a casting decision.",
            "The three kept canonical overruns (CIN_005_S03 / CIN_018_S03 / CIN_006_S03) are unchanged; this pack does not re-mix anything.",
            "No runtime file, mix, timing, SRT or pronunciation table was touched.",
        ],
        "pairs": pairs,
    }
    manifest_path = DELIVERIES / "VO_PALETTE_REVIEW_M39B_v1.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
                             encoding="utf-8")

    lines = ["#EXTM3U", "#PLAYLIST:VO palette level-matched A/B review (WO39 M39-B CP1)"]
    for pr in pairs:
        lines.append(f"# PAIR {pr['takeKey']} ({pr['kind']}) — {pr['speakerDisplay']} — "
                     f"target {pr['pairTargetLufs']:.2f} LUFS"
                     + (" [CEILING-LIMITED]" if pr["ceilingLimited"] else ""))
        for s in pr["sides"]:
            label = "canonical" if s["side"] == "A" else f"palette {pr['voice']}"
            lines.append(f"#EXTINF:{s['durationSeconds']:.3f},{s['side']} {label} — {pr['takeKey']} "
                         f"({s['postIntegratedLufs']:.2f} LUFS)")
            lines.append(s["renderFile"])
    playlist_path = REPORTS / "vo_palette_review_m39b_playlist.txt"
    playlist_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    total_bytes = sum(s["renderBytes"] for pr in pairs for s in pr["sides"])
    print(f"pairs={len(pairs)} renders={2 * len(pairs)} "
          f"ceiling_limited={manifest['counts']['ceilingLimitedPairs']} "
          f"total_render_bytes={total_bytes}")
    for pr in pairs:
        a, b = pr["sides"]
        print(f"  {pr['takeKey']}: target {pr['pairTargetLufs']:.2f} "
              f"A {a['preIntegratedLufs']:.2f}->{a['postIntegratedLufs']:.2f} "
              f"(gain {a['appliedGainDb']:+.2f}, TP {a['postTruePeakDbtp']:.2f}) "
              f"B {b['preIntegratedLufs']:.2f}->{b['postIntegratedLufs']:.2f} "
              f"(gain {b['appliedGainDb']:+.2f}, TP {b['postTruePeakDbtp']:.2f})"
              + (" CEILING-LIMITED" if pr["ceilingLimited"] else ""))
    print(f"manifest: {manifest_path.relative_to(ROOT)}")
    print(f"playlist: {playlist_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
