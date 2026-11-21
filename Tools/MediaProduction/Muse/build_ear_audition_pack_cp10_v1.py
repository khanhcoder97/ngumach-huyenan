#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D CP10 - Ear-audition pack v2 (DELTA).

Builds EAR_AUDITION_PACK_v2_DELTA.json + 2 new playlists, covering ONLY
the audio delivered since the v1 ear pack (M-D CP9, 2026-11-09, 196 items):

  mixesV2         14  M-F CP2 palette re-mixes (13 scene v2 + CIN_002 P0 v4)
  ambienceVariants 26 M-E CP1 real variants (13 cues x v02/v03)
  sfxDrafts        18 WO39 M39-A CP1+CP2 draft variants (guard/grass + 4 weapons)

DELTA discipline (Codex Gói 38): the 196 v1 items are NOT re-hashed and
NOT re-delivered. This pack references EAR_AUDITION_PACK_v1.json by id
only (supersedes / variantOf pointers are checked for existence, never
re-measured). The 18 SFX drafts already have audition playlists delivered
in M39-A (SFX_COMPOSED_DRAFT_*_audition_playlist.txt); they are referenced
here, not duplicated. The 40 M39-B A/B renders likewise keep their own
playlist (vo_palette_review_m39b_playlist.txt) and are referenced only.

Every number in the pack is measured fresh from real bytes on disk
(ffprobe + ffmpeg loudnorm, same invocation as measure_music_ambience.py)
and cross-checked against the delivery checkpoint that produced the file:
  mixes    vs MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json
  ambience vs AMBIENCE_COMPOSED_VARIANTS_pack_v1.json (master entries)
  sfx      vs WO39 M39-A CP1/CP2 validation JSONs (lufs/tp) + pack JSONs (sha)

Any cross-check mismatch aborts the build with a non-zero exit.
LFS pointers fail loudly instead of yielding a fake measurement.

Usage: python3 Tools/MediaProduction/Muse/build_ear_audition_pack_cp10_v1.py
Outputs (repo-relative):
  Implementation/Reports/MuseMedia/EAR_AUDITION_PACK_v2_DELTA.json
  Implementation/Reports/MuseMedia/ear_audition_08_v2mixes_playlist.txt
  Implementation/Reports/MuseMedia/ear_audition_09_ambience_variants_playlist.txt
"""
import hashlib
import json
import math
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
DELIVERIES = ROOT / "Implementation/Content/Audio/Deliveries"
TOL = 0.05  # LUFS / dBTP cross-check tolerance

# ---------------------------------------------------------------- item table
# (itemId, cueKey, file, priority, supersedes(v1 id or None), variantOf(v1 id or None), question)
MIXES = [
    ("MIX2-001", "CIN_000_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav",
     "P0", "MIX-030", None,
     "Nghe prologue v2 (narration History): narration co nghe ro toan bo 87s khong; ban v1 mat narration do loi plumbing - day la diem kiem chinh; nhac/ambience co lan narration khong."),
    ("MIX2-002", "CIN_002_mix_draft_v4",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V4/CIN_002_mix_draft_v4.wav",
     "P0", "MIX-027", None,
     "Nghe P0 v4 (giong palette): 3 cau thoai co vua cua so khoa khong; doi giong moi co lac voi nhac/ambience P0 khong."),
    ("MIX2-003", "CIN_006_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V2/CIN_006_mix_draft_v2.wav",
     "P0", "MIX-003", None,
     "Nghe CIN_006 v2: overrun v1 +0.520s da het chua (take palette co vua cua so khong); canon van dung, alternate take rieng."),
    ("MIX2-004", "CIN_008_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V2/CIN_008_mix_draft_v2.wav",
     "P1", "MIX-005", None,
     "Nghe CIN_008 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-005", "CIN_010_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V2/CIN_010_mix_draft_v2.wav",
     "P1", "MIX-007", None,
     "Nghe CIN_010 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-006", "CIN_011_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN011_DRAFT_V2/CIN_011_mix_draft_v2.wav",
     "P1", "MIX-008", None,
     "Nghe CIN_011 v2: cua so VO v1 chi thua 8ms - nghe cau thoai co bi cat duoi khong; giong palette co hop khong."),
    ("MIX2-007", "CIN_012_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN012_DRAFT_V2/CIN_012_mix_draft_v2.wav",
     "P1", "MIX-009", None,
     "Nghe CIN_012 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-008", "CIN_013_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN013_DRAFT_V2/CIN_013_mix_draft_v2.wav",
     "P1", "MIX-010", None,
     "Nghe CIN_013 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-009", "CIN_014_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN014_DRAFT_V2/CIN_014_mix_draft_v2.wav",
     "P1", "MIX-011", None,
     "Nghe CIN_014 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-010", "CIN_015_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN015_DRAFT_V2/CIN_015_mix_draft_v2.wav",
     "P1", "MIX-012", None,
     "Nghe CIN_015 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-011", "CIN_016_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN016_DRAFT_V2/CIN_016_mix_draft_v2.wav",
     "P1", "MIX-013", None,
     "Nghe CIN_016 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-012", "CIN_017_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN017_DRAFT_V2/CIN_017_mix_draft_v2.wav",
     "P1", "MIX-014", None,
     "Nghe CIN_017 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
    ("MIX2-013", "CIN_018_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN018_DRAFT_V2/CIN_018_mix_draft_v2.wav",
     "P0", "MIX-015", None,
     "Nghe CIN_018 v2: overrun v1 S03 +0.280s da het chua (take palette co vua cua so khong); take nguoi choi van la VOICE_PLACEHOLDER_ONLY."),
    ("MIX2-014", "CIN_020_mix_draft_v2",
     "Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V2/CIN_020_mix_draft_v2.wav",
     "P1", "MIX-017", None,
     "Nghe CIN_020 v2 (giong palette): thoai co vua cua so khong; duoi cau co bi cat khong."),
]

# Ambience cue order follows the v1 pack (AMB-001..013); v02 then v03 each.
AMB_CUES = [
    ("rain_light", "AMB-001"), ("rain_heavy", "AMB-002"),
    ("river_shore", "AMB-003"), ("underwater", "AMB-004"),
    ("waterfall", "AMB-005"), ("wind_canopy", "AMB-006"),
    ("desert_wind", "AMB-007"), ("mountain_wind", "AMB-008"),
    ("cave_drips", "AMB-009"), ("forge", "AMB-010"),
    ("thang_long_crowd", "AMB-011"), ("city_night", "AMB-012"),
    ("rift", "AMB-013"),
]

SFX = [
    ("SFX-001", "SFX/COMBAT/guard_expire", "guard_expire_v01",
     "Nghe guard_expire v01: co phai tieng het bao ve, khong giong metal_parry hay counter da xac nhan khong."),
    ("SFX-002", "SFX/COMBAT/guard_expire", "guard_expire_v02",
     "Nghe guard_expire v02: co phan biet duoc voi v01 khong; co giong metal_parry khong."),
    ("SFX-003", "SFX/COMBAT/guard_expire", "guard_expire_v03",
     "Nghe guard_expire v03: co phan biet duoc voi v01/v02 khong; co giong metal_parry khong."),
    ("SFX-004", "SFX/WORLD/step_grass", "step_grass_v01",
     "Nghe step_grass v01: co doc la co (khac da/go/bun) khong."),
    ("SFX-005", "SFX/WORLD/step_grass", "step_grass_v02",
     "Nghe step_grass v02: co phan biet duoc voi v01 khong; co doc la co khong."),
    ("SFX-006", "SFX/WORLD/step_grass", "step_grass_v03",
     "Nghe step_grass v03: co phan biet duoc voi v01/v02 khong; co doc la co khong."),
    ("SFX-007", "SFX/COMBAT/dao_swing", "dao_swing_v01",
     "Nghe dao_swing v01: co sac, nhe, doc la dao (khac basic_blade/metal_parry) khong."),
    ("SFX-008", "SFX/COMBAT/dao_swing", "dao_swing_v02",
     "Nghe dao_swing v02: co phan biet duoc voi v01 khong; co doc la dao khong."),
    ("SFX-009", "SFX/COMBAT/dao_swing", "dao_swing_v03",
     "Nghe dao_swing v03: co phan biet duoc voi v01/v02 khong; co doc la dao khong."),
    ("SFX-010", "SFX/COMBAT/brush_stroke", "brush_stroke_v01",
     "Nghe brush_stroke v01: co mem, luot but (cao, thoang) khong."),
    ("SFX-011", "SFX/COMBAT/brush_stroke", "brush_stroke_v02",
     "Nghe brush_stroke v02: co phan biet duoc voi v01 khong; co doc la but khong."),
    ("SFX-012", "SFX/COMBAT/brush_stroke", "brush_stroke_v03",
     "Nghe brush_stroke v03: co phan biet duoc voi v01/v02 khong; co doc la but khong."),
    ("SFX-013", "SFX/COMBAT/mace_swing", "mace_swing_v01",
     "Nghe mace_swing v01: co nang, tram (band thap) khong."),
    ("SFX-014", "SFX/COMBAT/mace_swing", "mace_swing_v02",
     "Nghe mace_swing v02: co phan biet duoc voi v01 khong; co doc la chuy khong."),
    ("SFX-015", "SFX/COMBAT/mace_swing", "mace_swing_v03",
     "Nghe mace_swing v03: co phan biet duoc voi v01/v02 khong; co doc la chuy khong."),
    ("SFX-016", "SFX/COMBAT/bow_string", "bow_string_v01",
     "Nghe bow_string v01: co cang day cung khong."),
    ("SFX-017", "SFX/COMBAT/bow_string", "bow_string_v02",
     "Nghe bow_string v02: co phan biet duoc voi v01 khong; co doc la day cung khong."),
    ("SFX-018", "SFX/COMBAT/bow_string", "bow_string_v03",
     "Nghe bow_string v03: co phan biet duoc voi v01/v02 khong; co doc la day cung khong."),
]
SFX_FILE = {
    "guard_expire": "Art_Source/Audio/Muse/COMPOSED/sfx/guard_expire_{v}.wav",
    "step_grass": "Art_Source/Audio/Muse/COMPOSED/sfx/step_grass_{v}.wav",
    "dao_swing": "Art_Source/Audio/Muse/COMPOSED/sfx/dao_swing_{v}.wav",
    "brush_stroke": "Art_Source/Audio/Muse/COMPOSED/sfx/brush_stroke_{v}.wav",
    "mace_swing": "Art_Source/Audio/Muse/COMPOSED/sfx/mace_swing_{v}.wav",
    "bow_string": "Art_Source/Audio/Muse/COMPOSED/sfx/bow_string_{v}.wav",
}


def is_pointer(p: Path) -> bool:
    return p.read_bytes()[:40].startswith(b"version https://git-lfs")


def pooled_rms_dbfs(p: Path) -> float:
    """True RMS over all decoded f32 samples (both channels pooled)."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p),
         "-f", "f32le", "-ac", "2", "-ar", "48000", "-"],
        capture_output=True, check=True).stdout
    n = len(raw) // 4
    xs = struct.unpack(f"<{n}f", raw)
    rms = math.sqrt(sum(x * x for x in xs) / n)
    return round(20 * math.log10(rms), 2)


def probe(p: Path) -> dict:
    if is_pointer(p):
        raise SystemExit(f"LFS pointer, not real bytes: {p}")
    data = p.read_bytes()
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,sample_rate,channels",
         "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    stream = j["streams"][0]
    err = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    loud = json.loads("{" + err.split("{", 1)[1].rsplit("}", 1)[0] + "}")
    # Files shorter than loudnorm's 400 ms gating window have NO defined
    # integrated loudness (ffmpeg reports -inf). Record null + pooled RMS
    # instead of writing -Infinity (invalid strict JSON) or a fake number.
    lufs = None if loud["input_i"] == "-inf" else float(loud["input_i"])
    return {
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": round(float(j["format"]["duration"]), 4),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": lufs,
        "true_peak_dbtp": float(loud["input_tp"]),
        "lra_lu": float(loud["input_lra"]),
        "rms_dbfs": pooled_rms_dbfs(p) if lufs is None else None,
        "sha256": hashlib.sha256(data).hexdigest(),
    }


def fail(msg: str):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    v1 = json.loads((REPORTS / "EAR_AUDITION_PACK_v1.json").read_text())
    v1_ids = {it["id"] for sec in v1["sections"].values() for it in sec}
    if len(v1_ids) != 196:
        fail(f"v1 pack item count {len(v1_ids)} != 196; refusing to build delta")

    # ---- cross-check sources (read-only; never copied as measurement) ----
    mf = json.loads((REPORTS / "MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json").read_text())
    mix_ref = {m["file"]: m for m in mf["mixes"]}
    amb_pack = json.loads((DELIVERIES / "AMBIENCE_COMPOSED_VARIANTS_pack_v1.json").read_text())
    amb_ref = {}
    amb_names = {}
    for cue in amb_pack["cues"]:
        amb_names[cue["cueKey"].split("/")[-1]] = cue.get("nameVi", "")
        for var in cue["variants"]:
            if var["variantId"] in ("v02", "v03"):
                amb_ref[var["master"]["path"]] = var["master"]
    sfx_ref = {}  # (cueKey, variant) -> (lufs, tp) from M39-A validation JSONs
    sfx_sha = {}
    for fn in ("MEDIA02_WO39_M39A_CP1_GUARD_GRASS_VALIDATION_20261112.json",
               "MEDIA02_WO39_M39A_CP2_WEAPONS_VALIDATION_20261112.json"):
        d = json.loads((REPORTS / fn).read_text())
        for k, m in d["measured"].items():
            cue, _, var = k.rpartition(" ")
            sfx_ref[(cue, var)] = (m["lufs"], m["tp"])
    for fn in ("SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json",
               "SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json"):
        d = json.loads((DELIVERIES / fn).read_text())
        for cue in d["cues"]:
            for var in cue.get("variants", []):
                master = var.get("master", {})
                if master.get("sha256"):
                    sfx_sha[master["path"]] = master["sha256"]

    mismatches = []

    def measure(rel: str) -> dict:
        p = ROOT / rel
        if not p.is_file():
            fail(f"missing file: {rel}")
        m = probe(p)
        if m["codec"] not in ("pcm_s24le", "pcm_s16le") or m["sample_rate_hz"] != 48000:
            fail(f"unexpected codec/sr for {rel}: {m['codec']} {m['sample_rate_hz']}")
        return m

    def xcheck(label: str, m: dict, ref_sha=None, ref_size=None,
               ref_dur=None, ref_lufs=None, ref_tp=None):
        if ref_sha and m["sha256"] != ref_sha:
            mismatches.append(f"{label}: sha mismatch")
        if ref_size is not None and m["size_bytes"] != ref_size:
            mismatches.append(f"{label}: size {m['size_bytes']} != {ref_size}")
        if ref_dur is not None and abs(m["duration_s"] - ref_dur) > 0.005:
            mismatches.append(f"{label}: duration {m['duration_s']} != {ref_dur}")
        if ref_lufs is not None and abs(m["integrated_lufs"] - ref_lufs) > TOL:
            mismatches.append(f"{label}: LUFS {m['integrated_lufs']} != {ref_lufs}")
        if ref_tp is not None and abs(m["true_peak_dbtp"] - ref_tp) > TOL:
            mismatches.append(f"{label}: TP {m['true_peak_dbtp']} != {ref_tp}")

    sections = {"mixesV2": [], "ambienceVariants": [], "sfxDrafts": []}

    for item_id, cue_key, rel, prio, supersedes, _var, question in MIXES:
        m = measure(rel)
        ref = mix_ref.get(rel)
        if ref is None:
            fail(f"no M-F CP2 reference for {rel}")
        xcheck(item_id, m, ref["sha256"], ref["sizeBytes"],
               ref["durationSeconds"], ref["integratedLUFS"], ref["truePeakDBTP"])
        if supersedes not in v1_ids:
            fail(f"{item_id}: supersedes {supersedes} not in v1 pack")
        sections["mixesV2"].append({
            "id": item_id, "cueKey": cue_key, "kind": "MIX", "codec": m["codec"],
            "file": rel, "sha256": m["sha256"], "sizeBytes": m["size_bytes"],
            "durationSeconds": m["duration_s"], "lufs": m["integrated_lufs"],
            "rmsDbfs": m["rms_dbfs"],
            "truePeakDbtp": m["true_peak_dbtp"], "lraLu": m["lra_lu"],
            "question": question, "priority": prio, "source": "M-F CP2",
            "supersedes": supersedes,
            "note": "Palette re-mix v2 (M-F CP2); Art_Source only, runtime still embeds v1.",
        })

    n = 0
    for cue, v1_id in AMB_CUES:
        for var in ("v02", "v03"):
            n += 1
            rel = f"Art_Source/Audio/Muse/COMPOSED/ambience/{cue}_{var}.wav"
            m = measure(rel)
            ref = amb_ref.get(rel)
            if ref is None:
                fail(f"no M-E CP1 reference for {rel}")
            xcheck(f"AMB2-{n:03d}", m, ref["sha256"], ref["sizeBytes"],
                   ref["durationSeconds"], ref["integratedLufs"], ref["truePeakDbtp"])
            sections["ambienceVariants"].append({
                "id": f"AMB2-{n:03d}", "cueKey": f"AMBIENCE/{cue}", "codec": m["codec"],
                "nameVi": amb_names.get(cue, ""), "kind": "AMBIENCE",
                "file": rel, "sha256": m["sha256"], "sizeBytes": m["size_bytes"],
                "durationSeconds": m["duration_s"], "lufs": m["integrated_lufs"],
            "rmsDbfs": m["rms_dbfs"],
                "truePeakDbtp": m["true_peak_dbtp"], "lraLu": m["lra_lu"],
                "question": (f"Nghe {cue} {var} so voi v01 master: co khac ro tai khong; "
                             f"diem loop 16s co lien khong; variant nao hop hon cho khung canh dung cue nay."),
                "priority": "P2", "source": "M-E CP1",
                "variantOf": v1_id,
                "note": "Real variant render (M-E CP1); v01 master stays in v1 pack as " + v1_id + ".",
            })

    for item_id, cue_key, fname, question in SFX:
        cue_short = cue_key.split("/")[-1]
        var = fname.rsplit("_", 1)[-1]
        rel = SFX_FILE[cue_short].format(v=var)
        m = measure(rel)
        ref = sfx_ref.get((cue_key, var))
        if ref is None:
            fail(f"no M39-A reference for {cue_key} {var}")
        xcheck(item_id, m, sfx_sha.get(rel), None, None, ref[0], ref[1])
        sections["sfxDrafts"].append({
            "id": item_id, "cueKey": cue_key, "kind": "SFX", "codec": m["codec"],
            "file": rel, "sha256": m["sha256"], "sizeBytes": m["size_bytes"],
            "durationSeconds": m["duration_s"], "lufs": m["integrated_lufs"],
            "rmsDbfs": m["rms_dbfs"],
            "truePeakDbtp": m["true_peak_dbtp"], "lraLu": m["lra_lu"],
            "question": question, "priority": "P1",
            "source": "WO39 M39-A CP1" if cue_short in ("guard_expire", "step_grass")
                      else "WO39 M39-A CP2",
            "note": ("Draft variant (DEC-MEDIA-SFX-DRAFT-20261112); source-only, no runtime binding." +
                      (f" Integrated LUFS undefined: {m['duration_s']} s file is shorter than the 400 ms loudnorm gating window; level is pooled stereo RMS {m['rms_dbfs']} dBFS." if m["integrated_lufs"] is None else "")),
        })

    if mismatches:
        for x in mismatches:
            print(f"MISMATCH: {x}", file=sys.stderr)
        sys.exit(1)

    total_dur = round(sum(it["durationSeconds"]
                          for sec in sections.values() for it in sec), 3)
    pack = {
        "packId": "NGM_EAR_AUDITION_PACK_V2_DELTA",
        "checkpoint": "MEDIA-02 WO37 M-D CP10 - ear-audition pack v2 (delta)",
        "decisionId": "DEC-MEDIA-P0-20261105; DEC-MEDIA-SFX-DRAFT-20261112 (SFX section)",
        "branch": "muse/media-production-20261104",
        "baseSha": "8e311aa",
        "status": "DRAFT_NOT_FINAL",
        "statusNote": "NOT_AUDITIONED. Delta pack only: 58 new items delivered since the v1 ear pack (M-D CP9). The 196 v1 items are NOT re-hashed or re-delivered here; listen to v1 + this delta together (196 + 58 = 254 items).",
        "howToListen": ("Core pass v2 first (4 P0 items below, ~3 min): the v2 mixes that "
                        "replace v1 core-pass items. Then playlist 08 (v2 mixes), playlist 10 "
                        "(SFX drafts), playlist 09 (ambience variants). Voice-palette A/B pairs "
                        "are NOT duplicated here; listen via vo_palette_review_m39b_playlist.txt "
                        "(M39-B CP1). Record verdicts by item id: PASS / FAIL / note. A FAIL item "
                        "becomes its own fix block; do not edit this pack silently."),
        "counts": {"mixesV2": 14, "ambienceVariants": 26, "sfxDrafts": 18},
        "totalItems": 58,
        "v1TotalItems": 196,
        "combinedTotalItems": 254,
        "totalDurationSeconds": total_dur,
        "v1Pack": "Implementation/Reports/MuseMedia/EAR_AUDITION_PACK_v1.json",
        "priorityQueue": [
            {"id": "MIX2-001", "section": "mixesV2", "ref": "CIN_000_mix_draft_v2",
             "flags": ["Prologue v2, narration History - diem kiem chinh: narration co nghe ro toan bo 87s khong (v1 mat narration do loi plumbing)"]},
            {"id": "MIX2-002", "section": "mixesV2", "ref": "CIN_002_mix_draft_v4",
             "flags": ["P0 v4, giong palette - 3 cau thoai co vua cua so khoa khong"]},
            {"id": "MIX2-003", "section": "mixesV2", "ref": "CIN_006_mix_draft_v2",
             "flags": ["Overrun v1 +0.520s - ban v2 co vua cua so khong"]},
            {"id": "MIX2-013", "section": "mixesV2", "ref": "CIN_018_mix_draft_v2",
             "flags": ["Overrun v1 S03 +0.280s - ban v2 co vua cua so khong; take nguoi choi van placeholder"]},
        ],
        "corePassUpdate": [
            {"v1Id": "MIX-030", "v1Ref": "PROLOGUE_mix_v1", "v2Id": "MIX2-001",
             "v2Ref": "CIN_000_mix_draft_v2", "change": "Narration Helio -> History; plumbing fixed; v1 mix defect (narration absent) is the reason to re-listen."},
            {"v1Id": "MIX-003", "v1Ref": "CIN_006_mix_draft_v1", "v2Id": "MIX2-003",
             "v2Ref": "CIN_006_mix_draft_v2", "change": "Palette voice; v1 overrun +0.520s kept for Codex in v1, v2 take fits window."},
            {"v1Id": "MIX-015", "v1Ref": "CIN_018_mix_draft_v1", "v2Id": "MIX2-013",
             "v2Ref": "CIN_018_mix_draft_v2", "change": "Palette voice; v1 overrun S03 +0.280s kept for Codex in v1, v2 take fits window."},
            {"v1Id": "MIX-002", "v1Ref": "CIN_005_mix_draft_v1", "v2Id": None,
             "v2Ref": None, "change": "No v2 exists (Ly An dialogue, no palette change); v1 stays the listening copy, overrun +0.160s kept for Codex."},
            {"v1Id": "MIX-008", "v1Ref": "CIN_011_mix_draft_v1", "v2Id": "MIX2-006",
             "v2Ref": "CIN_011_mix_draft_v2", "change": "Palette voice; v1 window slack was 8ms - listen for clipped tail in v2."},
        ],
        "relatedPlaylists": [
            {"file": "Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_GUARD_GRASS_audition_playlist.txt",
             "covers": "SFX-001..SFX-006 (guard_expire + step_grass), delivered in M39-A CP1; referenced, not duplicated."},
            {"file": "Implementation/Content/Audio/Deliveries/SFX_COMPOSED_DRAFT_WEAPONS_audition_playlist.txt",
             "covers": "SFX-007..SFX-018 (4 weapon identities), delivered in M39-A CP2; referenced, not duplicated."},
            {"file": "Implementation/Reports/MuseMedia/vo_palette_review_m39b_playlist.txt",
             "covers": "40 A/B voice-palette renders (M39-B CP1); referenced, not duplicated."},
        ],
        "sections": sections,
        "sources": [
            "MEDIA02_WO37_MF_CP2_VALIDATION_20261112.json",
            "AMBIENCE_COMPOSED_VARIANTS_pack_v1.json",
            "MEDIA02_WO39_M39A_CP1_GUARD_GRASS_VALIDATION_20261112.json",
            "MEDIA02_WO39_M39A_CP2_WEAPONS_VALIDATION_20261112.json",
            "SFX_COMPOSED_DRAFT_GUARD_GRASS_pack_v1.json",
            "SFX_COMPOSED_DRAFT_WEAPONS_pack_v1.json",
            "EAR_AUDITION_PACK_v1.json (id references only; v1 bytes not re-hashed)",
        ],
    }

    (REPORTS / "EAR_AUDITION_PACK_v2_DELTA.json").write_text(
        json.dumps(pack, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def playlist(fname: str, title: str, items):
        lines = ["#EXTM3U",
                 f"# MEDIA-02 WO37 M-D checkpoint 10 — ear-audition pack v2 (delta): {title}",
                 "# AUDITION STATUS: NOT_AUDITIONED (prepared for a human listener)",
                 "# M3U content under a .txt name (.m3u is not a policy extension);",
                 "# rename a copy to .m3u to open it directly in a player.",
                 "# Paths are relative to Implementation/Reports/MuseMedia/."]
        for it in items:
            lines.append(f"#EXTINF:-1,{it['id']} {it['cueKey']}")
            lines.append(f"../../../{it['file']}")
        (REPORTS / fname).write_text("\n".join(lines) + "\n", encoding="utf-8")

    playlist("ear_audition_08_v2mixes_playlist.txt",
             "palette re-mix v2 (M-F CP2: 13 scene v2 + CIN_002 P0 v4)",
             sections["mixesV2"])
    playlist("ear_audition_09_ambience_variants_playlist.txt",
             "composed ambience real variants (M-E CP1: 13 cues x v02/v03)",
             sections["ambienceVariants"])

    print(f"OK: 58 items, total {total_dur}s, 0 cross-check mismatches")
    print(f"  mixesV2={len(sections['mixesV2'])} "
          f"ambienceVariants={len(sections['ambienceVariants'])} "
          f"sfxDrafts={len(sections['sfxDrafts'])}")


if __name__ == "__main__":
    main()
