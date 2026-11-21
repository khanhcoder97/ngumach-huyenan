#!/usr/bin/env python3
"""Prologue CIN_000 mix v1 PLUMBING FIX (owner order 2026-11-13).

Defect (found at MEDIA-02 WO37 M-F CP2, 2026-11-12, verified by
cross-correlation on the shipped bytes): build_prologue_film.py
(CP27) fed the single ffmpeg label [vo] to BOTH the
sidechaincompress key input and the final amix. ffmpeg steals
frames between the two consumers of one label, so the narration
in the shipped v1 mix is dropped / shifted (SEG01 take vs mix
max|corr| 0.020, SEG03 0.017, final Ly An line -0.063 -- the whole
VO chain is effectively absent) and two renders of the same graph
measure differently (-20.30 vs -20.51 LUFS). Integrated loudness
still read a healthy -20.81 LUFS, so loudness QA could not catch
it; nobody had listened (NOT_AUDITIONED).

Fix (this tool): re-render the CP27 mix with the graph plumbing
corrected EXACTLY the way the M-F CP2 prologue v2 render proved
(apad the VO bus to the full timeline, then asplit so each
consumer gets its own copy). NOTHING else changes: the same five
CP27 draft narration takes (Helio, avocado_v2:MAI_03) at unity
gain, the same timeline derived from the CP27 narration manifest,
the same composed ben_mua bed + ported rain_light / river_shore
ambience at the CP27 gains (-9.07 / -8.52 / -8.47 dB), the same
sidechain ducking (threshold 0.03, ratio 4, attack 15 ms, release
350 ms), Ly An's final line reusing the checkpoint-04 take at
-5 dB, the composed resolve stinger on the title card at -2 dB,
the same fades and the same peak guard (trim only above
-1.0 dBTP).

The render is run TWICE and the two outputs must be byte
identical: determinism is part of the fix (the broken graph was
non-reproducible).

Output: Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED/
PROLOGUE_mix_v1_fixed.wav + its manifest. The delivery tool
(build_prologue_v1_fix_delivery.py) then installs this render at
the canonical v1 paths and re-muxes the runtime film. The broken
bytes stay in git history (sha f026ed3e... at head 7f461da).

Owner approval: main chat 2026-11-13 02:58 JST ("va luon di"),
answering the decision widget presented 2026-11-12 ~19:52 JST.
Status stays DRAFT_NOT_FINAL / NOT_AUDITIONED -- this is a defect
correction of the same draft mix, not a final mix.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_prologue_mix_v2 import (  # noqa: E402
    LYAN_WAV, MUSIC_OGG, RAIN_OGG, RIVER_OGG, ROOT, STING_OGG,
    VO_MANIFEST, build_timeline, loudnorm, probe_duration, run,
    sha256_file)

TAKE_DIR = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
OUT_DIR = ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED"
OUT_WAV = OUT_DIR / "PROLOGUE_mix_v1_fixed.wav"
BROKEN_SHA256 = ("f026ed3e10499b42ea4fcc39ada9a1b42e0b5b749d16"
                 "ab77208afd54016ffb54")
TMP2 = Path("/tmp/prologue_v1_fixed_render2.wav")


def render_fixed(cues, total, title_start, lyan_start, seg_files,
                 out_path, trim_db=0.0):
    """The CP27 render_mix graph with ONLY the plumbing fixed
    (apad + asplit on the VO bus). Narration legs carry no volume
    filter, exactly as CP27 (unity gain)."""
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-stream_loop", "1", "-i", str(MUSIC_OGG),
           "-stream_loop", "-1", "-i", str(RAIN_OGG),
           "-stream_loop", "-1", "-i", str(RIVER_OGG)]
    for f in seg_files:
        cmd += ["-ac", "2", "-i", str(f)]
    cmd += ["-ac", "2", "-i", str(LYAN_WAV),
            "-i", str(STING_OGG)]
    parts = [
        f"[0:a]atrim=0:{total:.3f},volume=-9.07dB[mus]",
        f"[1:a]atrim=0:{total:.3f},volume=-8.52dB[rain]",
        f"[2:a]atrim=0:{total:.3f},volume=-8.47dB[riv]",
        "[mus][rain][riv]amix=inputs=3:normalize=0[bed]",
    ]
    vo_labels = []
    for i, c in enumerate(cues[:5]):
        ms = int(round(c["start"] * 1000))
        parts.append(f"[{3 + i}:a]aresample=48000,adelay={ms}|{ms}"
                     f"[v{i}]")
        vo_labels.append(f"[v{i}]")
    lyan_ms = int(round(lyan_start * 1000))
    parts.append(f"[8:a]aresample=48000,adelay={lyan_ms}|{lyan_ms},"
                 f"volume=-5dB[ly]")
    vo_labels.append("[ly]")
    parts.append("".join(vo_labels) +
                 f"amix=inputs={len(vo_labels)}:normalize=0[vo]")
    # PLUMBING FIX (the only change vs CP27): CP27 fed [vo] to
    # both sidechaincompress and the final amix; give each
    # consumer its own copy. apad first so the sidechain key
    # stream spans the whole timeline (without it the ducked bed
    # ends when the key EOFs and the mix comes out short).
    parts.append(f"[vo]apad=whole_dur={total:.3f}[vopad]")
    parts.append("[vopad]asplit=2[vokey][vomix]")
    parts.append("[bed][vokey]sidechaincompress=threshold=0.03:"
                 "ratio=4:attack=15:release=350[duck]")
    st_ms = int(round((title_start + 0.15) * 1000))
    parts.append(f"[9:a]adelay={st_ms}|{st_ms},volume=-2dB[st]")
    parts.append(f"[duck][vomix][st]amix=inputs=3:normalize=0,"
                 f"volume={trim_db:.2f}dB,afade=t=in:st=0:d=0.8,"
                 f"afade=t=out:st={total - 1.2:.3f}:d=1.2,"
                 f"atrim=0:{total:.3f}[mix]")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run(cmd + ["-filter_complex", ";".join(parts), "-map", "[mix]",
               "-c:a", "pcm_s16le", "-ar", "48000", str(out_path)])
    return out_path


def main() -> int:
    vo = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    finals, cues, total, title_start, lyan_start = build_timeline(vo)
    seg_files = [TAKE_DIR / s["file"] for s in vo["segments"]]
    for f in seg_files:
        assert f.exists(), f
    assert LYAN_WAV.exists(), LYAN_WAV

    mix = render_fixed(cues, total, title_start, lyan_start,
                       seg_files, OUT_WAV)
    lufs, tp = loudnorm(mix)
    trim = 0.0
    for _ in range(2):
        if tp <= -1.0:
            break
        trim += (-1.0 - tp - 0.1)
        mix = render_fixed(cues, total, title_start, lyan_start,
                           seg_files, OUT_WAV, trim)
        lufs, tp = loudnorm(mix)
    dur = probe_duration(mix)
    assert abs(dur - total) <= 0.05, (dur, total)
    sha1 = sha256_file(mix)
    print(f"fixed mix: {dur:.3f} s, {lufs:.2f} LUFS / {tp:.2f} dBTP "
          f"(trim {trim:.2f} dB) sha {sha1[:16]}...")

    # Reproducibility: the broken graph rendered differently every
    # run; the fixed graph must be byte deterministic.
    mix2 = render_fixed(cues, total, title_start, lyan_start,
                        seg_files, TMP2, trim)
    sha2 = sha256_file(mix2)
    assert sha2 == sha1, f"non-deterministic render: {sha1} vs {sha2}"
    print("reproducibility: second render byte-identical")

    seg_records = []
    for i, s in enumerate(vo["segments"]):
        f = seg_files[i]
        seg_records.append({
            "segment": i + 1,
            "takeId": s["takeId"],
            "file": f"Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT/"
                    f"{s['file']}",
            "sha256": sha256_file(f),
            "durationSeconds": s["durationSeconds"],
            "startSeconds": round(cues[i]["start"], 3),
            "gainDb": 0.0,
            "voice": "avocado_v2:MAI_03 (Helio) -- CP27 draft "
                     "narration, unchanged",
        })
    manifest = {
        "manifestId": "NGM_PROLOGUE_MIX_V1_FIXED",
        "checkpoint": "MEDIA-02 prologue v1 plumbing fix "
                      "(owner order 2026-11-13)",
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "file": "PROLOGUE_mix_v1_fixed.wav",
        "sha256": sha1,
        "sizeBytes": mix.stat().st_size,
        "durationSeconds": round(dur, 4),
        "integratedLufs": round(lufs, 2),
        "truePeakDbtp": round(tp, 2),
        "peakTrimDb": round(trim, 2),
        "assetState": "DRAFT_MIX_NOT_FINAL",
        "defect": {
            "foundAt": "MEDIA-02 WO37 M-F CP2 (2026-11-12), "
                       "report section 5; independently verified "
                       "by cross-correlation in the main thread",
            "rootCause": "build_prologue_film.py (CP27) fed the "
                         "single ffmpeg label [vo] to both the "
                         "sidechaincompress key input and the "
                         "final amix; ffmpeg frame-stealing "
                         "between the two consumers drops / "
                         "shifts narration frames in the mix",
            "brokenMixSha256": BROKEN_SHA256,
            "brokenMixMeasurements": {
                "seg01TakeVsMixMaxAbsCorr": 0.020,
                "seg03TakeVsMixMaxAbsCorr": 0.017,
                "finalLineTakeVsMixMaxAbsCorr": -0.063,
                "integratedLufs": -20.81,
                "note": "loudness read healthy; the VO chain "
                        "was effectively absent",
            },
            "brokenRendersNonReproducible": "-20.30 vs -20.51 "
                                             "LUFS on two renders "
                                             "of the CP27 graph",
        },
        "fix": {
            "change": "Graph plumbing only: the VO bus is apad'ed "
                      "to the full timeline and asplit so each "
                      "consumer (sidechain key / final amix) gets "
                      "its own copy -- the same fix the M-F CP2 "
                      "prologue v2 render proved (take-vs-mix "
                      "correlations 0.983-0.989 there)",
            "recipeDeltaVsCp27": "NONE: same takes, same unity "
                                 "narration gain, same timeline, "
                                 "same bed gains, ducking, "
                                 "stinger, fades and peak guard",
            "reproducible": True,
            "renderSha256Run1": sha1,
            "renderSha256Run2": sha2,
        },
        "ownerApproval": "Main chat 2026-11-13 02:58 JST: owner "
                         "answered the pending decision widget "
                         "with 'va luon di' (fix it now)",
        "segments": seg_records,
        "finalLine": {
            "file": "Art_Source/Audio/Muse/VO/P0_DRAFT/"
                    "VO_CIN001_S05_LYAN_draft_v1.wav",
            "sha256": sha256_file(LYAN_WAV),
            "startSeconds": round(lyan_start, 3),
            "gainDb": -5.0,
            "note": "Checkpoint-04 take reused byte-for-byte, "
                    "as in CP27",
        },
        "stems": [
            {"role": "narration", "source": "PROLOGUE_VO_manifest"
             "_v1.json (checkpoint 27 draft TTS)",
             "provenance": "NEW_DRAFT_VO"},
            {"role": "final line", "source": "VO_CIN001_S05_LYAN_"
             "draft_v1.wav (checkpoint 04 take, reused bytes)",
             "provenance": "REUSED_CP04"},
            {"role": "music bed", "source": "MUSIC/ben_mua "
             "composed runtime OGG (checkpoint 26)",
             "gainDb": -9.07,
             "provenance": "ORIGINAL_COMPOSED_BY_MUSE_CP26"},
            {"role": "ambience", "source": "AMBIENCE/rain_light + "
             "AMBIENCE/river_shore runtime OGGs (checkpoint 07 "
             "pack)", "gainDb": [-8.52, -8.47],
             "provenance": "PORTED_CODEX_PACKV1"},
            {"role": "title stinger", "source": "SFX/CINEMA/resolve "
             "composed runtime OGG (checkpoint 26)",
             "provenance": "ORIGINAL_COMPOSED_BY_MUSE_CP26"},
        ],
        "ducking": "sidechaincompress on the music+ambience bed, "
                   "keyed by the VO bus: threshold 0.03, ratio 4, "
                   "attack 15 ms, release 350 ms (checkpoint 20 "
                   "settled values); peak guard trims the whole "
                   "mix only above -1.0 dBTP",
        "delivery": "build_prologue_v1_fix_delivery.py installs "
                    "this render at the canonical v1 paths "
                    "(Art_Source PROLOGUE_DRAFT + runtime mix "
                    "copy) and re-muxes the runtime CIN_000 film "
                    "and its subtitled / 720p variants. The "
                    "broken bytes remain in git history at "
                    "7f461da (sha f026ed3e...).",
        "notes": [
            "DRAFT_NOT_FINAL, NOT_AUDITIONED: same draft mix, "
            "defect corrected; no content, casting or level "
            "decision is changed by this fix.",
            "The M-F CP2 palette v2 mix (CIN000_DRAFT_V2) is a "
            "separate alternate and is NOT touched.",
        ],
    }
    (OUT_DIR / "PROLOGUE_MIX_V1_FIXED_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print("OK: PROLOGUE_MIX_V1_FIXED_manifest_v1.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
