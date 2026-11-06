"""Build the MEDIA-02 checkpoint 33 A/B review shortlist (Goi 31 item 3).

Re-measures from real bytes (ffprobe + ffmpeg loudnorm + loop-seam decode):
  - P0 draft mixes v1/v2/v3 (12 files: 3 scenes x 3 versions + 3 x 72 s review)
  - Composed music (9) + cinema stingers (4) runtime OGGs
  - Composed ambience (13) + ported music/ambience (22) runtime OGGs, incl. seam
  - Draft VO takes (21 canonical + 1 CIN006 alternate, kept separate)

Outputs (all inside policy-allowed roots):
  Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json
  Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.md
  Implementation/Reports/MuseMedia/ab_shortlist_*_playlist.txt
  (6 playlists; files hold valid M3U content but use the .txt extension
  because .m3u is not in the scope policy's mediaExtensions -- rename a
  copy to .m3u to open it directly in a player)

Audition status is NOT_AUDITIONED throughout: this environment cannot listen.
Loudness/codec numbers are measurements, never a listening PASS.
The alternate take CIN_006_ALT_T01 keeps its own takeId/version and is never
placed in the canonical VO playlist (DEC-MEDIA-P0 Q3).

Label fix (checkpoint 36, 2026-11-07): the owner decided the canonical
spelling of NPC_TA_VAN_KHANH is "Tạ Vân Khanh" (D-12). The wrong spelling
"Tạ Văn Khánh" came from this tool's SPEAKER_DISPLAY fallback -- the P0 VO
manifest stores the speaker id only, no manifest ever carried the wrong
spelling. SPEAKER_DISPLAY / PROPER_NAMES corrected and the CP33 outputs
regenerated; measurements are unchanged.
"""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
RUNTIME = ROOT / "ClientGodot/assets/audio"
CHECKPOINT = "MEDIA-02 checkpoint 33"
BASE_SHA = "6f2b4659b1935dc739df688942b5142a13dde770"  # integration HEAD at build time
BRANCH = "muse/media-production-20261104"

MIX_VERSIONS = [
    ("v1", "ported stems", "Art_Source/Audio/Muse/MIX/P0_DRAFT/P0_MIX_manifest_v1.json",
     "mix/p0", ["CIN_001_mix_draft_v1.wav", "CIN_002_mix_draft_v1.wav",
                "CIN_004_mix_draft_v1.wav", "P0_mix_review_72s_draft_v1.wav"]),
    ("v2", "composed music + stingers, ported ambience",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/P0_MIX_V2_manifest_v1.json",
     "mix/p0_v2", ["CIN_001_mix_draft_v2.wav", "CIN_002_mix_draft_v2.wav",
                   "CIN_004_mix_draft_v2.wav", "P0_mix_review_72s_draft_v2.wav"]),
    ("v3", "fully composed stems",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json",
     "mix/p0_v3", ["CIN_001_mix_draft_v3.wav", "CIN_002_mix_draft_v3.wav",
                   "CIN_004_mix_draft_v3.wav", "P0_mix_review_72s_draft_v3.wav"]),
]
SCENES = ["CIN_001", "CIN_002", "CIN_004"]

VO_MANIFESTS = [
    ("Art_Source/Audio/Muse/VO/P0_DRAFT/P0_VO_manifest_v1.json", "vo/p0"),
    ("Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT/CAMPAIGN_VO_manifest_v1.json", "vo/campaign"),
    ("Art_Source/Audio/Muse/VO/CIN006_DRAFT/CIN006_VO_manifest_v1.json", "vo/cin006"),
]

# Proper names a listener must check by ear (spelling as written in each text).
PROPER_NAMES = [
    "Ly An", "Tạ Vân Khanh", "Hạ Mặc", "Sầm", "Chu Quý",
    "Mãng Cốt", "Bến Mưa", "Thăng Long", "Lạc Châu", "Sa Hỏa", "Sa Hoa",
    "Trần Sơn", "Lâm Triều", "Bách Uyên", "Ngũ Mạch", "Tống Bành",
    "Cô Vô Tướng", "Cơ Vô Tướng",
    "Minh Kiếm", "Ảnh Đao", "Huyền Bút", "Thạch Chùy", "Linh Cung",
]

# P0 VO manifest stores the speaker id only; map it to the display name.
SPEAKER_DISPLAY = {"NPC_LYAN": "Ly An", "NPC_TA_VAN_KHANH": "Tạ Vân Khanh",
                   "NPC_HA_MAC": "Hạ Mặc", "NPC_SAM_CHU_QUY": "Sầm Chủ Quỹ"}

ERRORS = []


def err(msg):
    ERRORS.append(msg)
    print("ERROR: " + msg, file=sys.stderr)


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def is_lfs_pointer(path):
    return Path(path).read_bytes()[:40].startswith(b"version https://git-lfs")


def probe(path):
    """ffprobe + single-pass ffmpeg loudnorm, measured from real bytes."""
    p = Path(path)
    if is_lfs_pointer(p):
        raise SystemExit(f"LFS pointer, not real bytes: {path}")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,sample_rate,channels",
         "-of", "json", str(p)],
        capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    stream = j["streams"][0]
    res = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    loud = json.loads("{" + res.stderr.split("{", 1)[1].rsplit("}", 1)[0] + "}")
    return {
        "codec": stream["codec_name"],
        "sample_rate_hz": int(stream["sample_rate"]),
        "channels": int(stream["channels"]),
        "duration_s": round(float(j["format"]["duration"]), 4),
        "size_bytes": int(j["format"]["size"]),
        "integrated_lufs": round(float(loud["input_i"]), 2),
        "true_peak_dbtp": round(float(loud["input_tp"]), 2),
        "lra_lu": round(float(loud["input_lra"]), 2),
        "sha256": sha256_of(p),
    }


def seam(path):
    """CP07 seam method: mono 48 kHz f32 decode; head/tail = first/last 100 ms;
    wrap jump = |last sample - first sample|. Indicator only, never a PASS."""
    p = Path(path)
    if is_lfs_pointer(p):
        raise SystemExit(f"LFS pointer, not real bytes: {path}")
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-ac", "1", "-ar", "48000",
         "-f", "f32le", "-"],
        capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    n = len(x)
    if n < 9600:
        raise SystemExit(f"too short for seam method: {path}")
    head, tail = x[:4800], x[-4800:]
    return {
        "head_rms": round(float(np.sqrt(np.mean(head ** 2))), 6),
        "tail_rms": round(float(np.sqrt(np.mean(tail ** 2))), 6),
        "wrap_jump": round(float(abs(x[-1] - x[0])), 6),
    }


def measure_many(paths):
    with ThreadPoolExecutor(max_workers=4) as ex:
        return dict(zip(paths, ex.map(probe, paths)))


def measure_seams(paths):
    with ThreadPoolExecutor(max_workers=4) as ex:
        return dict(zip(paths, ex.map(seam, paths)))


def rel_m3u(repo_rel):
    """Path inside an M3U stored in Implementation/Reports/MuseMedia/."""
    return "../../../" + repo_rel


def main():
    runtime_manifest = json.loads(
        (RUNTIME / "RUNTIME_AUDIO_manifest_v1.json").read_text(encoding="utf-8"))
    manifest_sha = {"ClientGodot/" + f["runtimePath"]: f["sha256"]
                    for f in runtime_manifest["files"]}

    def check_runtime(rel, label):
        if rel not in manifest_sha:
            err(f"{label}: {rel} not in RUNTIME_AUDIO manifest")
            return
        got = sha256_of(ROOT / rel)
        if got != manifest_sha[rel]:
            err(f"{label}: sha mismatch {rel}")

    # ---------------------------------------------------------------- mixes
    mixes = {}
    mix_files = []
    for version, stem_note, manifest_rel, runtime_dir, files in MIX_VERSIONS:
        man = json.loads((ROOT / manifest_rel).read_text(encoding="utf-8"))
        scenes = {s["sceneId"]: s for s in man["scenes"]}
        mixes[version] = {
            "version": version,
            "stemProvenance": stem_note,
            "mixVersion": man.get("mixVersion", "v1_ported_stems"),
            "status": man["status"],
            "scenes": {},
            "review": {},
        }
        for fname in files:
            mix_files.append(RUNTIME / runtime_dir / fname)
        # scene mixes
        for scene_id in SCENES:
            s = scenes[scene_id]
            m = s["mix"]
            rel = f"ClientGodot/assets/audio/{runtime_dir}/{m['file']}"
            check_runtime(rel, f"mix {version} {scene_id}")
            mixes[version]["scenes"][scene_id] = {
                "file": m["file"],
                "runtimePath": rel,
                "recorded": {"duration_s": m["durationSeconds"],
                             "integrated_lufs": float(m["integratedLUFS"]),
                             "true_peak_dbtp": float(m["truePeakDBTP"])},
                "stems": [{"cue": st["cue"], "role": st["role"],
                           "provenance": st.get(
                               "provenance",
                               "PORTED_CODEX_PACKV1 (checkpoints 07/08)"),
                           "source": st["source"]}
                          for st in s["stems"]],
                "ducking": s.get("ducking", {}).get("evidence", []),
                "loopQA": s.get("loopQA", []),
            }
        r = man["reviewMix"]
        rel = f"ClientGodot/assets/audio/{runtime_dir}/{r['file']}"
        check_runtime(rel, f"mix {version} review")
        mixes[version]["review"] = {
            "file": r["file"], "runtimePath": rel,
            "recorded": {"duration_s": r["durationSeconds"],
                         "integrated_lufs": float(r["integratedLUFS"]),
                         "true_peak_dbtp": float(r["truePeakDBTP"])},
            "note": r.get("note", ""),
        }

    mix_measured = measure_many([str(p) for p in mix_files])
    for version, _, _, runtime_dir, files in MIX_VERSIONS:
        for fname in files:
            rel = f"ClientGodot/assets/audio/{runtime_dir}/{fname}"
            meas = mix_measured[str(RUNTIME / runtime_dir / fname)]
            target = (mixes[version]["review"] if "review" in fname
                      else mixes[version]["scenes"]["_".join(fname.split("_")[:2])])
            rec = target["recorded"]
            for key, tol in (("integrated_lufs", 0.05), ("true_peak_dbtp", 0.05),
                             ("duration_s", 0.02)):
                if abs(meas[key] - rec[key]) > tol:
                    err(f"mix {version} {fname}: measured {key} {meas[key]} != "
                        f"recorded {rec[key]}")
            target["measured"] = meas
            target["sha256"] = meas["sha256"]
            if meas["true_peak_dbtp"] > -1.0:
                err(f"mix {version} {fname}: true peak {meas['true_peak_dbtp']} "
                    "above -1.0 dBTP ceiling")

    # A/B deltas per scene (v2/v3 vs v1), from re-measured values.
    ab_table = []
    for scene_id in SCENES + ["REVIEW_72S"]:
        row = {"scene": scene_id}
        for version in ("v1", "v2", "v3"):
            src = (mixes[version]["review"] if scene_id == "REVIEW_72S"
                   else mixes[version]["scenes"][scene_id])
            row[version] = {"file": src["file"],
                            "integrated_lufs": src["measured"]["integrated_lufs"],
                            "true_peak_dbtp": src["measured"]["true_peak_dbtp"],
                            "duration_s": src["measured"]["duration_s"]}
        row["delta_v2_minus_v1_lufs"] = round(
            row["v2"]["integrated_lufs"] - row["v1"]["integrated_lufs"], 2)
        row["delta_v3_minus_v1_lufs"] = round(
            row["v3"]["integrated_lufs"] - row["v1"]["integrated_lufs"], 2)
        row["delta_v3_minus_v2_lufs"] = round(
            row["v3"]["integrated_lufs"] - row["v2"]["integrated_lufs"], 2)
        ab_table.append(row)

    # ------------------------------------------------- music / stingers (composed)
    music_pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                             "/MUSIC_COMPOSED_pack_v1.json").read_text(encoding="utf-8"))
    music_rows, stinger_rows = [], []
    music_paths = []
    for cue in music_pack["cues"]:
        rel = cue["runtime"]["path"]
        check_runtime(rel, "composed " + cue["cueKey"])
        music_paths.append(ROOT / rel)
    music_measured = measure_many([str(p) for p in music_paths])
    for cue in music_pack["cues"]:
        rel = cue["runtime"]["path"]
        meas = music_measured[str(ROOT / rel)]
        rec = cue["runtime"]
        for key, rec_key in (("integrated_lufs", "integratedLufs"),
                             ("true_peak_dbtp", "truePeakDbtp")):
            if abs(meas[key] - rec[rec_key]) > 0.5:
                err(f"composed {cue['cueKey']}: measured {key} {meas[key]} "
                    f"differs from pack {rec[rec_key]} by >0.5")
        row = {"cueKey": cue["cueKey"], "nameVi": cue["nameVi"],
               "kind": cue["kind"], "runtimePath": rel,
               "duration_s": meas["duration_s"],
               "measured_lufs": meas["integrated_lufs"],
               "measured_dbtp": meas["true_peak_dbtp"],
               "pack_lufs": rec["integratedLufs"],
               "pack_dbtp": rec["truePeakDbtp"],
               "sha256": meas["sha256"],
               "provenance": cue["provenance"], "loop": cue["loop"]}
        if cue.get("seam"):
            row["wrap_jump_recorded"] = cue["seam"]["wrapJump"]
            row["wrap_jump_raw_recorded"] = cue["seam"]["wrapJumpRaw"]
            # CP26 seam was measured on the master WAV (post-landing); the
            # shortlist re-measures the runtime OGG, so a small delta is the
            # Vorbis re-encode of the landing, not a new defect.
            row["seamBasis"] = "master WAV (CP26, post-landing)"
        (music_rows if cue["kind"] == "MUSIC" else stinger_rows).append(row)

    # ------------------------------------------- ambience (composed + ported)
    amb_pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                           "/AMBIENCE_COMPOSED_pack_v1.json").read_text(encoding="utf-8"))
    ported_pack = json.loads((ROOT / "Implementation/Content/Audio/Deliveries"
                              "/MUSIC_AMBIENCE_pack_v1.json").read_text(encoding="utf-8"))
    amb_rows = []
    amb_paths = []
    for cue in amb_pack["cues"]:
        rel = cue["runtime"]["path"]
        check_runtime(rel, "composed ambience " + cue["cueKey"])
        amb_paths.append(ROOT / rel)
    amb_measured = measure_many([str(p) for p in amb_paths])
    amb_seams = measure_seams([str(p) for p in amb_paths])
    for cue in amb_pack["cues"]:
        rel = cue["runtime"]["path"]
        meas, sm = amb_measured[str(ROOT / rel)], amb_seams[str(ROOT / rel)]
        amb_rows.append({
            "cueKey": cue["cueKey"], "nameVi": cue["nameVi"],
            "version": "composed", "runtimePath": rel,
            "duration_s": meas["duration_s"],
            "measured_lufs": meas["integrated_lufs"],
            "measured_dbtp": meas["true_peak_dbtp"],
            "target_lufs_ported": cue["composition"]["targetLufsPorted"],
            "pack_lufs": cue["runtime"]["integratedLufs"],
            "seam_measured": sm,
            "seam_recorded": {"head_rms": cue["seam"]["headRms"],
                              "tail_rms": cue["seam"]["tailRms"],
                              "wrap_jump": cue["seam"]["wrapJump"]},
            "wrap_jump_raw_recorded": cue["seam"]["wrapJumpRaw"],
            "seamBasis": "runtime OGG (CP30)",
            "sha256": meas["sha256"], "provenance": cue["provenance"]})

    ported_rows = []
    ported_paths = []
    for cue in ported_pack["cues"]:
        name = cue["cueKey"].split("/", 1)[1]
        kind_dir = "music" if cue["cueKey"].startswith("MUSIC/") else "ambience"
        rel = f"ClientGodot/assets/audio/{kind_dir}/{name}.ogg"
        check_runtime(rel, "ported " + cue["cueKey"])
        ported_paths.append(ROOT / rel)
    ported_measured = measure_many([str(p) for p in ported_paths])
    ported_seams = measure_seams([str(p) for p in ported_paths])
    for cue in ported_pack["cues"]:
        name = cue["cueKey"].split("/", 1)[1]
        kind_dir = "music" if cue["cueKey"].startswith("MUSIC/") else "ambience"
        rel = f"ClientGodot/assets/audio/{kind_dir}/{name}.ogg"
        meas, sm = ported_measured[str(ROOT / rel)], ported_seams[str(ROOT / rel)]
        rec_seam = cue["runtime"].get("seam", {})
        ported_rows.append({
            "cueKey": cue["cueKey"], "nameVi": cue["nameVi"],
            "version": "ported", "runtimePath": rel,
            "duration_s": meas["duration_s"],
            "measured_lufs": meas["integrated_lufs"],
            "measured_dbtp": meas["true_peak_dbtp"],
            "pack_lufs": cue["runtime"]["integrated_lufs"],
            "pack_dbtp": cue["runtime"]["true_peak_dbtp"],
            "seam_measured": sm,
            "seam_recorded": rec_seam,
            "seamBasis": "runtime OGG (CP07)",
            "sha256": meas["sha256"],
            "provenance": "PORTED_PACKV1",
            "loop": cue["loop"]})

    # Seam table: every loop cue, sorted by measured wrap jump desc.
    seam_table = []
    for row in amb_rows + ported_rows + music_rows:
        if row.get("loop") is False:
            continue
        seam_table.append({
            "cueKey": row["cueKey"], "version": row.get("version", "composed"),
            "wrap_jump_measured": row["seam_measured"]["wrap_jump"]
            if "seam_measured" in row else None,
            "head_rms": row["seam_measured"]["head_rms"]
            if "seam_measured" in row else None,
            "tail_rms": row["seam_measured"]["tail_rms"]
            if "seam_measured" in row else None,
            "wrap_jump_recorded": row.get("seam_recorded", {}).get("wrap_jump")
            if "seam_recorded" in row else row.get("wrap_jump_recorded"),
            "wrap_jump_raw_recorded": row.get("wrap_jump_raw_recorded"),
            "seamBasis": row.get("seamBasis", "runtime OGG"),
            "flag_ear_check": None,
        })
    # music rows have no seam_measured yet: measure seams for composed music too
    music_seam_paths = [ROOT / r["runtimePath"] for r in music_rows]
    music_seams = measure_seams([str(p) for p in music_seam_paths])
    for row in music_rows:
        sm = music_seams[str(ROOT / row["runtimePath"])]
        row["seam_measured"] = sm
    for entry in seam_table:
        if entry["cueKey"].startswith("MUSIC/") and entry["version"] == "composed":
            row = next(r for r in music_rows if r["cueKey"] == entry["cueKey"])
            entry["wrap_jump_measured"] = row["seam_measured"]["wrap_jump"]
            entry["head_rms"] = row["seam_measured"]["head_rms"]
            entry["tail_rms"] = row["seam_measured"]["tail_rms"]
    seam_table.sort(key=lambda e: (e["wrap_jump_measured"] is None,
                                   -(e["wrap_jump_measured"] or 0)))
    for entry in seam_table:
        w = entry["wrap_jump_measured"]
        entry["flag_ear_check"] = bool(w is not None and w > 0.015)
        # Only compare against a recorded value measured on the same bytes:
        # composed-music pack seams were measured on the master WAV, while
        # this shortlist measures the runtime OGG (Vorbis re-encode shifts
        # the landing by up to ~0.02 at music levels). That delta is recorded,
        # not an error.
        if entry["wrap_jump_recorded"] is not None and w is not None \
                and entry["seamBasis"].startswith("runtime"):
            if abs(w - entry["wrap_jump_recorded"]) > 0.005:
                err(f"seam {entry['cueKey']} {entry['version']}: measured "
                    f"{w} != recorded {entry['wrap_jump_recorded']}")

    # ------------------------------------------------------------------ VO
    vo_rows, alt_rows = [], []
    vo_paths = []
    for manifest_rel, runtime_dir in VO_MANIFESTS:
        man = json.loads((ROOT / manifest_rel).read_text(encoding="utf-8"))
        for take in man["takes"]:
            rel = f"ClientGodot/assets/audio/{runtime_dir}/{take['wav']}"
            check_runtime(rel, "VO " + take["key"])
            vo_paths.append(ROOT / rel)
    vo_measured = measure_many([str(p) for p in vo_paths])
    scene_order = {}
    for manifest_rel, runtime_dir in VO_MANIFESTS:
        man = json.loads((ROOT / manifest_rel).read_text(encoding="utf-8"))
        for take in man["takes"]:
            rel = f"ClientGodot/assets/audio/{runtime_dir}/{take['wav']}"
            meas = vo_measured[str(ROOT / rel)]
            window = take["windowSceneSeconds"]
            if window is None:
                window_s, fit, over = None, take.get("fit", "NO_WINDOW_ASSIGNED"), None
            else:
                window_s = round(window[1] - window[0], 3)
                dur0 = round(take.get("durationSeconds", meas["duration_s"]), 3)
                fit = "FITS" if dur0 <= window_s + 1e-9 else "OVERRUN"
                over = round(dur0 - window_s, 3) if fit == "OVERRUN" else 0.0
            dur = round(take.get("durationSeconds", meas["duration_s"]), 3)
            if abs(dur - meas["duration_s"]) > 0.05:
                err(f"VO {take['key']}: manifest duration {dur} != "
                    f"measured {meas['duration_s']}")
            names = [n for n in PROPER_NAMES if n in take["text"]]
            display = take.get("speakerDisplay") or SPEAKER_DISPLAY.get(
                take["speaker"], take["speaker"])
            listen_for = ("Phát âm tên riêng trong câu: " + ", ".join(names)
                          if names else
                          f"Giọng đóng vai {display} — kiểm tra độ hợp vai")
            row = {"key": take["key"], "shotId": take["shotId"],
                   "speaker": take["speaker"],
                   "speakerDisplay": display,
                   "voice": take.get("voiceLabel", take.get("voice", "")),
                   "text": take["text"],
                   "windowSceneSeconds": window, "window_s": window_s,
                   "takeDuration_s": dur, "fit": fit, "overrun_s": over,
                   "runtimePath": rel, "wav": take["wav"],
                   "measured_lufs": meas["integrated_lufs"],
                   "measured_dbtp": meas["true_peak_dbtp"],
                   "status": take.get("status", ""),
                   "properNamesInText": names,
                   "listenFor": listen_for,
                   "sha256": meas["sha256"]}
            if take["key"] == "CIN006_ALT_T01":
                row["takeId"] = "CIN_006_ALT_T01"
                row["takeVersion"] = "v1-alt"
                row["canonical"] = False
                alt_rows.append(row)
            else:
                row["canonical"] = True
                vo_rows.append(row)
                scene_order[take["key"]] = take["shotId"]
    vo_rows.sort(key=lambda r: r["shotId"])
    if len(vo_rows) != 21:
        err(f"canonical VO takes: {len(vo_rows)} != 21")
    if len(alt_rows) != 1:
        err(f"alternate VO takes: {len(alt_rows)} != 1")

    # P0 S05 loudness vs the other two P0 takes (CP04 note: ~5.5 LUFS louder).
    p0_loud = {r["key"]: r["measured_lufs"] for r in vo_rows
               if r["key"] in ("CIN001_S05", "CIN002_S02", "CIN004_S02")}
    s05_delta = None
    if len(p0_loud) == 3:
        others = [v for k, v in p0_loud.items() if k != "CIN001_S05"]
        s05_delta = round(p0_loud["CIN001_S05"] - sum(others) / len(others), 2)

    rain_heavy = next(e for e in seam_table
                      if e["cueKey"] == "AMBIENCE/rain_heavy"
                      and e["version"] == "ported")
    top_seam = seam_table[0]
    overruns = [r for r in vo_rows if r["fit"] == "OVERRUN"]

    # ------------------------------------------------------------- playlists
    def m3u_entry(title, repo_rel, duration_s):
        return f"#EXTINF:{int(round(duration_s))},{title}\n{rel_m3u(repo_rel)}\n"

    playlists = {}

    mix_entries = []
    for scene_id in SCENES:
        for version in ("v1", "v2", "v3"):
            src = mixes[version]["scenes"][scene_id]
            mix_entries.append((f"P0 MIX A/B — {scene_id} {version} "
                                f"({mixes[version]['stemProvenance']})",
                                src["runtimePath"],
                                src["measured"]["duration_s"]))
    for version in ("v1", "v2", "v3"):
        src = mixes[version]["review"]
        mix_entries.append((f"P0 MIX A/B — REVIEW 72s {version} "
                            f"({mixes[version]['stemProvenance']})",
                            src["runtimePath"],
                            src["measured"]["duration_s"]))
    playlists["ab_shortlist_p0_mixes_playlist.txt"] = mix_entries

    music_entries = [(f"COMPOSED MUSIC — {r['cueKey']} ({r['nameVi']})",
                      r["runtimePath"], r["duration_s"]) for r in music_rows]
    music_entries += [(f"COMPOSED STINGER — {r['cueKey']}",
                       r["runtimePath"], r["duration_s"]) for r in stinger_rows]
    playlists["ab_shortlist_music_playlist.txt"] = music_entries

    amb_entries = []
    for cue_key in [r["cueKey"] for r in amb_rows]:
        c = next(r for r in amb_rows if r["cueKey"] == cue_key)
        p = next(r for r in ported_rows if r["cueKey"] == cue_key)
        amb_entries.append((f"AMBIENCE A/B — {cue_key} COMPOSED (CP30)",
                            c["runtimePath"], c["duration_s"]))
        amb_entries.append((f"AMBIENCE A/B — {cue_key} PORTED (CP07)",
                            p["runtimePath"], p["duration_s"]))
    playlists["ab_shortlist_ambience_playlist.txt"] = amb_entries

    vo_entries = [(f"VO — {r['shotId']} {r['speakerDisplay']} "
                   f"[{r['fit']}{(' +' + str(r['overrun_s']) + 's') if r['fit'] == 'OVERRUN' else ''}] "
                   f"— {r['text']}",
                   r["runtimePath"], r["takeDuration_s"]) for r in vo_rows]
    playlists["ab_shortlist_vo_playlist.txt"] = vo_entries

    alt_entries = [(f"VO ALTERNATE (NOT canonical) — {r['shotId']} "
                    f"{r['speakerDisplay']} takeId={r['takeId']} "
                    f"version={r['takeVersion']} — {r['text']}",
                    r["runtimePath"], r["takeDuration_s"]) for r in alt_rows]
    playlists["ab_shortlist_vo_alt_playlist.txt"] = alt_entries

    playlists["ab_shortlist_all_playlist.txt"] = (mix_entries + music_entries
                                         + amb_entries + vo_entries)

    playlist_meta = {}
    for fname, entries in playlists.items():
        header = ("#EXTM3U\n"
                  f"# MEDIA-02 checkpoint 33 — Goi 31 item 3 A/B review shortlist\n"
                  "# AUDITION STATUS: NOT_AUDITIONED (this environment cannot listen)\n"
                  "# This file holds valid M3U content under a .txt name because\n"
                  "# .m3u is not in the scope policy mediaExtensions; rename a\n"
                  "# copy to .m3u to open it directly in a player. Open this file\n"
                  "# from the repo so the relative paths resolve.\n"
                  "# Measurements are loudness/codec numbers, NOT a listening PASS.\n")
        body = "".join(m3u_entry(t, p, d) for t, p, d in entries)
        (REPORTS / fname).write_text(header + body, encoding="utf-8")
        playlist_meta[fname] = {
            "entries": len(entries),
            "totalDuration_s": round(sum(d for _, _, d in entries), 3),
            "path": f"Implementation/Reports/MuseMedia/{fname}",
        }

    def _seam_of(cue_key, version):
        e = next(x for x in seam_table
                 if x["cueKey"] == cue_key and x["version"] == version)
        return e["wrap_jump_measured"]

    # ------------------------------------------------------------ defect table
    defects = [
        {"id": "D-01", "area": "VO overrun (3 windows)",
         "evidence": "; ".join(
             f"{r['shotId']} +{r['overrun_s']} s (take {r['takeDuration_s']} s "
             f"vs window {r['window_s']} s)" for r in overruns),
         "listenAt": "ab_shortlist_vo_playlist.txt — " + ", ".join(
             r["shotId"] for r in overruns),
         "question": "Câu thoại có bị cắt/nghe vội ở cuối cửa sổ không? "
                     "Cửa sổ giữ nguyên chờ Codex quyết — không cắt thoại, "
                     "không nới cửa sổ, không tăng tốc.",
         "status": "OPEN_FOR_DIRECTOR"},
        {"id": "D-02", "area": "VO male voices not distinct",
         "evidence": "Mọi nhân vật nam dùng chung một production voice "
                     "Helio trong bản nháp (ghi trong VO manifest CP17/CP19).",
         "listenAt": "ab_shortlist_vo_playlist.txt — CIN_008_S03, CIN_010_S03, "
                     "CIN_011_S03, CIN_012_S03, CIN_014_S03, CIN_016_S03",
         "question": "Có phân biệt được Tạ Vân Khanh / Sầm / Hạ Mặc / "
                     "Tống Bành qua giọng không, hay nghe như một người?",
         "status": "OPEN_FOR_DIRECTOR"},
        {"id": "D-03", "area": "P0 VO loudness imbalance",
         "evidence": ("CIN001_S05 take đo lại "
                      f"{p0_loud.get('CIN001_S05')} LUFS, cao hơn trung bình "
                      f"2 take P0 còn lại {s05_delta} LUFS (ghi chú CP04: "
                      "~5,5 LUFS). VO giữ unity trong mix nên chênh này đi "
                      "thẳng vào mix."),
         "listenAt": "ab_shortlist_vo_playlist.txt — CIN_001_S05 vs CIN_002_S02 / "
                     "CIN_004_S02; ab_shortlist_p0_mixes_playlist.txt — CIN_001",
         "question": "Câu S05 có to hẳn lên so với 2 câu P0 còn lại không? "
                     "Cần gain-stage lại take hay giữ nguyên làm neo?",
         "status": "OPEN_FOR_DIRECTOR"},
        {"id": "D-04", "area": "Loop seam — rain_heavy (ported)",
         "evidence": (f"wrap jump đo lại {rain_heavy['wrap_jump_measured']} "
                      f"(CP07 ghi {rain_heavy['wrap_jump_recorded']}), cao "
                      "nhất trong 22 cue ported; RMS đầu/cuối gần bằng nhau "
                      f"({rain_heavy['head_rms']} / {rain_heavy['tail_rms']})."),
         "listenAt": "ab_shortlist_ambience_playlist.txt — AMBIENCE/rain_heavy PORTED",
         "question": "Có nghe tiếng click/nấc ở điểm nối vòng lặp 16 s không?",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-05", "area": "Loop seam — composed music wrapJumpRaw",
         "evidence": ("tran_son wrapJumpRaw 0.404, bach_uyen 0.295 (trước "
                      "landing 0,25 s, CP26); wrap jump sau landing trên "
                      "master ≈ 0, nhưng trên runtime OGG đo lại tran_son "
                      f"{_seam_of('MUSIC/tran_son', 'composed')} / bach_uyen "
                      f"{_seam_of('MUSIC/bach_uyen', 'composed')} (lệch do "
                      "Vorbis mã hóa lại). Nghe tai vẫn còn nợ."),
         "listenAt": "ab_shortlist_music_playlist.txt — MUSIC/tran_son, MUSIC/bach_uyen",
         "question": "Vòng lặp nhạc có liền mạch không, hay nghe rõ điểm nối?",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-06", "area": "Ducking — CIN_002 v3 deeper than v2",
         "evidence": ("Duck ambience CIN_002: v3 −7,32 dB vs v2 −6,48 dB "
                      "(cùng tham số sidechain; chênh do RMS bed composed "
                      "trên cửa sổ 2 s, CP31)."),
         "listenAt": "ab_shortlist_p0_mixes_playlist.txt — CIN_002 v2 rồi v3 "
                     "(cửa sổ VO 7,0–11,0 s)",
         "question": "Ở v3, ambience có bị dìm quá sâu dưới VO trong cửa sổ "
                     "7–11 s không?",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-07", "area": "Crowd beds are filtered noise, not speech",
         "evidence": ("thang_long_crowd / city_night composed là nhiễu qua "
                      "dải formant trôi chậm — theo cấu trúc không thể tạo "
                      "lời nói có nghĩa (CP30). Độ 'giống đám đông' là nhận "
                      "định nghe tai."),
         "listenAt": "ab_shortlist_ambience_playlist.txt — AMBIENCE/thang_long_crowd "
                     "COMPOSED, AMBIENCE/city_night COMPOSED",
         "question": "Bed có đọc như đám đông thật không, hay nghe như nhiễu "
                     "trắng lọc?",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-08", "area": "Stinger placements PROPOSED",
         "evidence": ("reveal @30,0 s CIN_001; tension trong CIN_004 — vị trí "
                      "PROPOSED chờ picture lock (CP20/CP29/CP31)."),
         "listenAt": "ab_shortlist_p0_mixes_playlist.txt — CIN_001 v1/v2/v3 (30 s), "
                     "CIN_004 v1/v2/v3",
         "question": "Stinger có rơi đúng nhịp hình không, hay lệch/thừa?",
         "status": "OPEN_FOR_DIRECTOR"},
        {"id": "D-09", "area": "P0 mixes are DRAFT, never auditioned",
         "evidence": ("v1/v2/v3 đều DRAFT_MIX_NOT_FINAL; cân bằng VO/nhạc/"
                      "ambience chưa nghiệm thu bằng tai. Chênh LUFS giữa "
                      "các version ≤ 1,4 LUFS/scene theo bảng A/B."),
         "listenAt": "ab_shortlist_p0_mixes_playlist.txt — toàn bộ 12 file",
         "question": "Version nào nghe cân bằng nhất (VO rõ, nhạc không lấn, "
                     "ambience không rỗng)? Ghi lựa chọn v1/v2/v3 theo scene.",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-10", "area": "VO proper-name pronunciation",
         "evidence": ("Tên riêng nói ra trong câu thoại: "
                      + (", ".join(sorted({n for r in vo_rows
                                           for n in r['properNamesInText']}))
                         or "không có")
                      + " — chỉ 'Sa Hỏa' (CIN_018_S03). Tên người nói mà mỗi "
                        "giọng phải đóng vai: "
                      + ", ".join(sorted({r['speakerDisplay']
                                          for r in vo_rows}))
                      + ". TTS hư cấu, chưa nghe tai."),
         "listenAt": "ab_shortlist_vo_playlist.txt — toàn bộ 21 take",
         "question": "Tên riêng có phát âm đúng và thống nhất qua các take "
                     "không? Giọng có hợp với nhân vật mình đóng vai không? "
                     "Ghi lại tên nào nghe sai.",
         "status": "OPEN_FOR_LISTENER"},
        {"id": "D-11", "area": "Placeholder voices (cinematic-only)",
         "evidence": ("CIN_020 dùng VOICE_LETTER_RECIPIENT cho Người nhận thư "
                      "vô danh (vai giọng cinematic, không phải NPC gameplay); "
                      "CIN_018_S03 PLAYER là timing-only placeholder, "
                      "VOICE_GUIDE không gán giọng nói cho player."),
         "listenAt": "ab_shortlist_vo_playlist.txt — CIN_020_S03, CIN_018_S03",
         "question": "Giọng placeholder có chấp nhận được cho bản nháp không, "
                     "hay cần casting riêng?",
         "status": "OPEN_FOR_DIRECTOR"},
        {"id": "D-12", "area": "Tên nhân vật viết không thống nhất — ĐÃ CHỐT",
         "evidence": ("Chủ dự án chốt 2026-11-07: cách viết canonical là "
                      "'Tạ Vân Khanh' — khớp docs/production (176 lần; "
                      "'Văn Khánh' 0 lần), campaign VO manifest (CIN_008_S03), "
                      "Cinema Production Pack và questkit PR #118. Cách viết "
                      "sai 'Tạ Văn Khánh' không nằm trong manifest nào: P0 VO "
                      "manifest chỉ lưu speaker ID NPC_TA_VAN_KHANH, nhãn "
                      "hiển thị của take CIN_002_S02 do ánh xạ SPEAKER_DISPLAY "
                      "dự phòng trong chính tool shortlist này sinh ra. Đã "
                      "sửa ánh xạ và sinh lại nhãn tại checkpoint 36. Không "
                      "thu lại VO: cả hai câu thoại đều không đọc tên nhân "
                      "vật."),
         "listenAt": "ab_shortlist_vo_playlist.txt — CIN_002_S02 vs CIN_008_S03",
         "question": "Đã chốt — không còn câu hỏi mở về cách viết. Khi nghe "
                     "hai take, kiểm tra giọng có đọc như cùng một nhân vật "
                     "không (xem thêm D-02).",
         "status": "RESOLVED_OWNER_DECISION_20261107"},
    ]

    # ------------------------------------------------------------------ JSON
    shortlist = {
        "checkpoint": CHECKPOINT + " — A/B review shortlist (Goi 31 item 3)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": BRANCH,
        "baseSha": BASE_SHA,
        "auditionStatus": "NOT_AUDITIONED",
        "auditionNote": "This environment cannot listen. All loudness/codec/seam "
                        "numbers are measurements from real bytes, never a "
                        "listening PASS. A human listener must work through the "
                        "playlists and answer the defect table.",
        "provenanceRule": "Alternate takes keep their own takeId/version and "
                          "never replace canonical dialogue (DEC-MEDIA-P0 Q3). "
                          "v1/v2/v3 mixes are delivered in parallel; adoption "
                          "is Codex's adapter decision at PR #119 review.",
        "mixesAB": ab_table,
        "mixStemProvenance": {
            "v1": "ported PackV1 music + ambience + stingers",
            "v2": "composed music + stingers (CP26), ported ambience",
            "v3": "fully composed stems: music + stingers (CP26), "
                  "ambience (CP30)",
        },
        "mixDucking": {
            version: {scene: mixes[version]["scenes"][scene]["ducking"]
                      for scene in SCENES}
            for version in ("v1", "v2", "v3")},
        "mixLoopQA": {
            version: {scene: mixes[version]["scenes"][scene]["loopQA"]
                      for scene in SCENES}
            for version in ("v1", "v2", "v3")},
        "music": music_rows,
        "stingers": stinger_rows,
        "ambienceComposed": amb_rows,
        "ambiencePorted": [r for r in ported_rows
                           if r["cueKey"].startswith("AMBIENCE/")],
        "musicPorted": [r for r in ported_rows
                        if r["cueKey"].startswith("MUSIC/")],
        "seamTable": seam_table,
        "seamMethod": "mono 48kHz f32 decode; head/tail = first/last 100 ms; "
                      "wrap jump = |last sample - first sample|; indicator "
                      "only, not a seamlessness PASS (CP07 method)",
        "seamFlagThreshold": 0.015,
        "voCanonical": vo_rows,
        "voAlternate": alt_rows,
        "voCounts": {"canonical": len(vo_rows),
                     "alternateSeparate": len(alt_rows),
                     "overruns": [r["shotId"] for r in overruns]},
        "p0VoLoudnessDelta": {"CIN001_S05_minus_other_p0_mean_lufs": s05_delta,
                              "takes": p0_loud},
        "defects": defects,
        "playlists": playlist_meta,
        "counts": {
            "mixFiles": 12, "musicCues": len(music_rows),
            "stingers": len(stinger_rows),
            "ambienceComposed": len(amb_rows),
            "ambiencePorted": len([r for r in ported_rows
                                   if r["cueKey"].startswith("AMBIENCE/")]),
            "portedMusic": len([r for r in ported_rows
                                if r["cueKey"].startswith("MUSIC/")]),
            "voCanonical": len(vo_rows), "voAlternate": len(alt_rows),
        },
    }
    json_path = REPORTS / "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json"
    json_path.write_text(json.dumps(shortlist, indent=2, ensure_ascii=False)
                         + "\n", encoding="utf-8")

    md = build_markdown(shortlist)
    (REPORTS / "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.md").write_text(
        md, encoding="utf-8")

    if ERRORS:
        print(f"FAILED with {len(ERRORS)} errors", file=sys.stderr)
        return 1
    print("OK: shortlist JSON + 6 playlists + report written; "
          f"mixes 12, music {len(music_rows)}, stingers {len(stinger_rows)}, "
          f"ambience {len(amb_rows)} composed + "
          f"{len(ported_rows)} ported, VO {len(vo_rows)} + {len(alt_rows)} alt")
    return 0


def build_markdown(s):
    L = []
    L.append("# MEDIA-02 CHECKPOINT 33 — A/B review shortlist: P0 mix v1/v2/v3, "
             "nhạc/ambience, VO, loop seam (Gói 31 item 3) (2026-11-06)")
    L.append("")
    L.append("## Trạng thái nghe: NOT_AUDITIONED")
    L.append("")
    L.append("Môi trường này **không nghe được**. Mọi số loudness / true peak / "
             "seam trong báo cáo này đều đo từ byte thật (ffprobe / ffmpeg "
             "loudnorm / decode seam), **không phải PASS nghe tai**. Shortlist "
             "này giao cho người nghe: 6 playlist M3U + bảng A/B + bảng VO + "
             "bảng seam + bảng khuyết điểm có câu hỏi nghe cụ thể cho từng mục.")
    L.append("")
    L.append("Quy tắc provenance giữ nguyên: alternate take CIN_006_ALT_T01 có "
             "takeId/version riêng, nằm trong playlist riêng, **không thay** "
             "dialogue canonical và không có trong playlist VO chính. Ba bản "
             "mix v1/v2/v3 giao song song; chọn bản nào là quyết định adapter "
             "của Codex tại review PR #119.")
    L.append("")
    L.append("## Playlist (file .txt chứa nội dung M3U hợp lệ — đổi tên bản sao "
             "thành .m3u để mở trực tiếp trong trình phát; mở file từ trong repo "
             "để đường dẫn tương đối đúng; nghe theo thứ tự trong file)")
    L.append("")
    L.append("Đuôi .m3u không nằm trong `mediaExtensions` của policy scope "
             "hiện hành (`agent_scope_v2.json`, do Codex sở hữu) nên playlist "
             "giao dưới dạng .txt; nội dung là M3U chuẩn (#EXTM3U/#EXTINF), "
             "không đổi gì khác.")
    L.append("")
    L.append("")
    L.append("| Playlist | Mục | Tổng thời lượng |")
    L.append("|---|---|---|")
    for fname, meta in s["playlists"].items():
        L.append(f"| `{fname}` | {meta['entries']} | {meta['totalDuration_s']} s |")
    L.append("")
    L.append("## 1. A/B mix P0 v1 / v2 / v3 (đo lại từ byte thật)")
    L.append("")
    L.append("- **v1:** stem ported PackV1 (nhạc + ambience + stinger).")
    L.append("- **v2:** nhạc + stinger sáng tác (CP26), ambience vẫn ported.")
    L.append("- **v3:** stem hoàn toàn sáng tác — nhạc + stinger (CP26) + "
             "ambience (CP30).")
    L.append("- Cùng bảng stem CP02, cùng VO nháp CP04, cùng công thức gain "
             "và ducking; v1/v2 không bị thay thế.")
    L.append("")
    L.append("| Scene | v1 LUFS / dBTP | v2 LUFS / dBTP | v3 LUFS / dBTP | "
             "Δ v2−v1 | Δ v3−v1 | Δ v3−v2 |")
    L.append("|---|---|---|---|---|---|---|")
    for row in s["mixesAB"]:
        L.append(f"| {row['scene']} | {row['v1']['integrated_lufs']} / "
                 f"{row['v1']['true_peak_dbtp']} | {row['v2']['integrated_lufs']} / "
                 f"{row['v2']['true_peak_dbtp']} | {row['v3']['integrated_lufs']} / "
                 f"{row['v3']['true_peak_dbtp']} | {row['delta_v2_minus_v1_lufs']:+} | "
                 f"{row['delta_v3_minus_v1_lufs']:+} | {row['delta_v3_minus_v2_lufs']:+} |")
    L.append("")
    L.append("Ducking đo được (depth trong cửa sổ VO / ngoài cửa sổ):")
    L.append("")
    for version in ("v1", "v2", "v3"):
        for scene in SCENES:
            for ev in s["mixDucking"][version][scene]:
                L.append(f"- {version} {scene} bus {ev['bus']}: "
                         f"{ev['depthInWindowDb']} dB / "
                         f"{ev['depthOutsideWindowDb']} dB, cửa sổ "
                         f"{ev['windowSeconds'][0]}–{ev['windowSeconds'][1]} s.")
    L.append("")
    L.append("Loop QA trong mix (river_shore, acrossfade 1 s): tỉ lệ nhảy mẫu "
             "tại mối nối 0,58–0,60× p99.9 của chính bed ở cả ba version — "
             "không dấu hiệu click theo số đo; nghe tai vẫn còn nợ.")
    L.append("")
    L.append("## 2. Nhạc sáng tác (9 cue) + stinger (4)")
    L.append("")
    L.append("| Cue | Thời lượng | Đo lại LUFS / dBTP | Pack LUFS / dBTP | "
             "wrapJumpRaw (trước landing) |")
    L.append("|---|---|---|---|---|")
    for r in s["music"]:
        L.append(f"| {r['cueKey']} | {r['duration_s']} s | {r['measured_lufs']} / "
                 f"{r['measured_dbtp']} | {r['pack_lufs']} / {r['pack_dbtp']} | "
                 f"{r.get('wrap_jump_raw_recorded', '—')} |")
    for r in s["stingers"]:
        L.append(f"| {r['cueKey']} (stinger, one-shot) | {r['duration_s']} s | "
                 f"{r['measured_lufs']} / {r['measured_dbtp']} | "
                 f"{r['pack_lufs']} / {r['pack_dbtp']} | — |")
    L.append("")
    L.append("Leitmotif 'câu nhạc bỏ lửng' (CP26): đuôi trả lời chỉ xuất hiện ở "
             "`resolve` và `rift_finale`. Chất lượng giai điệu và độ liền vòng "
             "lặp là nhận định nghe tai — chưa có.")
    L.append("")
    L.append("## 3. Ambience: sáng tác (13) vs ported (13)")
    L.append("")
    L.append("| Cue | Composed LUFS / dBTP (đo lại) | Ported LUFS / dBTP (đo lại) | "
             "Seam composed | Seam ported |")
    L.append("|---|---|---|---|---|")
    for c in s["ambienceComposed"]:
        p = next(r for r in s["ambiencePorted"] if r["cueKey"] == c["cueKey"])
        L.append(f"| {c['cueKey']} | {c['measured_lufs']} / {c['measured_dbtp']} | "
                 f"{p['measured_lufs']} / {p['measured_dbtp']} | "
                 f"{c['seam_measured']['wrap_jump']} | "
                 f"{p['seam_measured']['wrap_jump']} |")
    L.append("")
    L.append("Đích loudness của bed sáng tác là LUFS ported tương ứng ở CP07 "
             "(khớp trong 0,01 LUFS ở master; runtime OGG lệch tối đa 0,36 LUFS "
             "do mã hóa Vorbis). Bed sáng tác: nhiễu lọc + gust/swell + sự kiện "
             "rời rạc xác định; không sample, không giọng nói.")
    L.append("")
    L.append("## 4. Loop seam — toàn bộ cue loop (xếp theo wrap jump đo lại)")
    L.append("")
    L.append("Phương pháp CP07: decode mono 48 kHz f32; head/tail = 100 ms đầu/"
             "cuối; wrap jump = |mẫu cuối − mẫu đầu|. Chỉ số đo, không phải "
             "kết luận seamless. Ngưỡng gắn cờ nghe tai: > 0,015.")
    L.append("")
    L.append("Lưu ý cơ sở đo: seam của nhạc sáng tác trong pack CP26 đo trên "
             "master WAV (sau landing), còn shortlist này đo lại trên runtime "
             "OGG — Vorbis mã hóa lại làm lệch điểm nối tới ~0,02 ở mức nhạc "
             "nên số runtime cao hơn số pack; đó không phải lỗi mới, mà là "
             "đúng số tai người nghe sẽ nghe từ file runtime. Seam của ambience "
             "sáng tác (CP30) và toàn bộ pack ported (CP07) đều đo trên runtime "
             "OGG nên so khớp trực tiếp.")
    L.append("")
    L.append("| Cue | Bản | Wrap jump đo lại | Ghi trong pack | Cờ nghe |")
    L.append("|---|---|---|---|---|")
    for e in s["seamTable"]:
        L.append(f"| {e['cueKey']} | {e['version']} | {e['wrap_jump_measured']} | "
                 f"{e['wrap_jump_recorded']} | "
                 f"{'CỜ — nghe điểm nối' if e['flag_ear_check'] else '—'} |")
    L.append("")
    L.append("## 5. VO dự thảo — 21 cửa sổ canonical (phát âm / tên riêng)")
    L.append("")
    L.append("Giọng hư cấu, không clone giọng người thật, không sample không "
             "license. Nam dùng chung một production voice Helio trong bản nháp "
             "(xem D-02). 3 overrun giữ nguyên cửa sổ chờ Codex quyết.")
    L.append("")
    L.append("| Shot | Người nói / giọng | Cửa sổ (s) | Take (s) | Khớp | "
             "LUFS đo lại | Tên riêng trong câu |")
    L.append("|---|---|---|---|---|---|---|")
    for r in s["voCanonical"]:
        names = ", ".join(r["properNamesInText"]) if r["properNamesInText"] else "—"
        L.append(f"| {r['shotId']} | {r['speakerDisplay']} / {r['voice']} | "
                 f"{r['windowSceneSeconds'][0]}–{r['windowSceneSeconds'][1]} "
                 f"({r['window_s']} s) | {r['takeDuration_s']} | {r['fit']}"
                 f"{(' +' + str(r['overrun_s']) + ' s') if r['fit'] == 'OVERRUN' else ''} | "
                 f"{r['measured_lufs']} | {names} |")
    L.append("")
    L.append("Alternate take riêng (không trong playlist VO chính): "
             "CIN_006_ALT_T01 v1-alt — Hạ Mặc: “Tới đây ta theo được. Chỗ trống "
             "này giữ nguyên.” — playlist `ab_shortlist_vo_alt_playlist.txt`.")
    L.append("")
    L.append("## 6. Bảng khuyết điểm cần người nghe trả lời")
    L.append("")
    L.append("| ID | Mục | Bằng chứng đo được | Nghe ở đâu | Câu hỏi |")
    L.append("|---|---|---|---|---|")
    for d in s["defects"]:
        L.append(f"| {d['id']} | {d['area']} | {d['evidence']} | {d['listenAt']} | "
                 f"{d['question']} |")
    L.append("")
    L.append("## Giới hạn còn lại")
    L.append("")
    L.append("- **NOT_AUDITIONED:** chưa có lần nghe thẩm định nào cho mix/nhạc/"
             "ambience/VO/seam trong checkpoint này; mọi kết luận nghe phải chờ "
             "người nghe làm việc với playlist trên.")
    L.append("- Mix vẫn DRAFT_MIX_NOT_FINAL; bảng stem PROPOSED_CANDIDATE chưa "
             "khóa; vị trí stinger PROPOSED chờ picture lock; VO vẫn bản nháp TTS.")
    L.append("- Final picture vẫn chờ keyframe/character lock; checkpoint này "
             "không chặn ở mức đó.")
    L.append("- Gói 31 item 4 (minimal runtime pack) là khối tiếp theo; item 5 "
             "(.gitattributes) vẫn chờ merge commit của chủ dự án từ integration.")
    L.append("")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
