#!/usr/bin/env python3
"""MEDIA-02 WO37 M-D checkpoint 9 — ear-audition preparation pack.

Assembles ONE listening pack for everything that is still NOT_AUDITIONED:
the composed score (masters / transitions / stingers / intros / outros /
stems / layers), the composed ambience, the per-scene draft mixes and the
VO takes. All loudness/peak/seam numbers are taken from the already
validated pack manifests (MD1..MD8, checkpoint 26, checkpoint 30) or, for
mixes and VO (which have no machine-readable loudness manifest), measured
here from the real bytes with ffmpeg loudnorm. Every item carries a
sha256 of the file the listener will open.

Outputs (Implementation/Reports/MuseMedia/):
  EAR_AUDITION_PACK_v1.json
  ear_audition_01_score_playlist.txt
  ear_audition_02_intro_outro_playlist.txt
  ear_audition_03_layers_playlist.txt
  ear_audition_04_stems_playlist.txt
  ear_audition_05_ambience_playlist.txt
  ear_audition_06_mixes_playlist.txt
  ear_audition_07_vo_playlist.txt
Playlists hold M3U content under .txt names (.m3u is not a policy
extension); entry paths are relative to the playlist folder.
Status stays NOT_AUDITIONED: this pack prepares the listening, it does
not perform it.
"""
import hashlib
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DELIV = ROOT / "Implementation/Content/Audio/Deliveries"
REPORTS = ROOT / "Implementation/Reports/MuseMedia"
RUNTIME_MANIFEST = ROOT / "ClientGodot/assets/audio/RUNTIME_AUDIO_manifest_v1.json"
PLAYLIST_PREFIX = "../../../"  # Reports/MuseMedia -> repo root

Q_MASTER = ("Nghe toan cue: cau nhac bo lung co dung o bac 2 khong; "
            "tail day du chi duoc phep o resolve/rift_finale; diem loop co lien tai khong.")
Q_STINGER = "Stinger co dung vai tro (reveal/resolve/warning) va khong qua dai so voi cua so hinh khong."
Q_TRANSITION = "Cau chuyen 6 s co noi hai trang thai muot khong, khong de lo seam o giua."
Q_INTRO = "Intro ket bang chuong handoff dung downbeat dau cua loop chua; nghe lien voi master ngay sau no."
Q_OUTRO = "Outro co dong tren pad tonic + chuong khong; tail co dung quy tac cua cue (chi rift_finale duoc full flute tail) khong."
Q_STEM = ("Stem co sach khong (khong lot nhom khac); ba stem cong lai bang master "
          "(da kiem so: khop luong tu 24-bit, max diff 3.58e-07) — nghe xac nhan khong artifact.")
Q_LAYER = ("Nghe cap base -> layer: fade layer vao, tong cong gop co choi/duc khong; "
           "adapter co can ride gain khong (so combined ghi kem).")
Q_AMBIENCE = "Diem loop (16 s) co nghe thay nhip/dut khong; chi so seam wrapJumpRaw ghi kem chi la chi bao."
Q_MIX = ("VO co ro tren nen khong; ducking co tu nhien khong; cua so thoai co khop hinh khong; "
         "nhac/ambience co lan VO khong.")
Q_VO = ("Phat am ten rieng (Lac Chau, Huyen An, Ben Mua, Sa Hoa, Ta Van Khanh) co dung khong; "
        "cam xuc va nhip cau co khop ngu canh khong.")


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def loudnorm(path):
    """Integrated LUFS + true peak (dBTP) from real bytes via ffmpeg loudnorm."""
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True, timeout=300)
    txt = out.stderr
    i = txt.rfind("{")
    j = txt.rfind("}")
    if i < 0 or j <= i:
        raise RuntimeError(f"loudnorm parse failed for {path}")
    d = json.loads(txt[i:j + 1])
    return float(d["input_i"]), float(d["input_tp"])


def item_from_cue(cue, group, q, source, use_runtime=False):
    f = cue["runtime"] if use_runtime else cue["master"]
    it = {
        "cueKey": cue["cueKey"],
        "nameVi": cue.get("nameVi"),
        "kind": cue.get("kind"),
        "file": f["path"],
        "sha256": f["sha256"],
        "durationSeconds": f.get("durationSeconds"),
        "lufs": f.get("integratedLufs"),
        "truePeakDbtp": f.get("truePeakDbtp"),
        "question": q,
        "priority": "P2",
        "source": source,
    }
    if cue.get("parentCueKey"):
        it["parentCueKey"] = cue["parentCueKey"]
    if cue.get("seam"):
        it["seamWrapJump"] = cue["seam"].get("wrapJump")
        it["seamWrapJumpRaw"] = cue["seam"].get("wrapJumpRaw")
    if cue.get("combinedWithBase"):
        cb = cue["combinedWithBase"]
        it["combinedLufs"] = cb.get("integratedLufs")
        it["combinedTruePeakDbtp"] = cb.get("truePeakDbtp")
        it["combinedBaseCueKey"] = cb.get("baseCueKey")
    return it


def main():
    packs = {}
    packs["cp26"] = load(DELIV / "MUSIC_COMPOSED_pack_v1.json")
    for n in range(1, 9):
        packs[f"md{n}"] = load(DELIV / f"MUSIC_SCORE_MD{n}_pack_v1.json")
    amb = load(DELIV / "AMBIENCE_COMPOSED_pack_v1.json")
    pron = load(DELIV / "PRONUNCIATION_TABLE_v1.json")
    shortlist = load(REPORTS / "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json")
    runtime = load(RUNTIME_MANIFEST)

    sections = {}

    # --- score masters / stingers / transitions ---
    score = []
    for c in packs["cp26"]["cues"]:
        if c["kind"] == "MUSIC":
            score.append(item_from_cue(c, "score", Q_MASTER, "MUSIC_COMPOSED_pack_v1.json"))
    for c in packs["md1"]["cues"]:
        if c["kind"] == "MUSIC":
            score.append(item_from_cue(c, "score", Q_MASTER, "MUSIC_SCORE_MD1_pack_v1.json"))
    sections["scoreMasters"] = score
    sections["stingers"] = [item_from_cue(c, "stingers", Q_STINGER, "MUSIC_COMPOSED_pack_v1.json")
                            for c in packs["cp26"]["cues"] if c["kind"] != "MUSIC"]
    sections["transitions"] = [item_from_cue(c, "transitions", Q_TRANSITION, "MUSIC_SCORE_MD1_pack_v1.json")
                               for c in packs["md1"]["cues"] if c["kind"] == "TRANSITION"]

    # --- intros / outros / stems (MD2 + MD3) ---
    io, stems = [], []
    for n in (2, 3):
        src = f"MUSIC_SCORE_MD{n}_pack_v1.json"
        for c in packs[f"md{n}"]["cues"]:
            if c["kind"] in ("INTRO", "OUTRO"):
                io.append(item_from_cue(c, "introOutro", Q_INTRO if c["kind"] == "INTRO" else Q_OUTRO, src))
            elif c["kind"] == "STEM":
                io_q = Q_STEM
                stems.append(item_from_cue(c, "stems", io_q, src))
    # intro/outro listening order: per parent cue, intro -> outro
    io.sort(key=lambda x: (x.get("parentCueKey") or "", 0 if x["kind"] == "INTRO" else 1))
    stems.sort(key=lambda x: (x.get("parentCueKey") or "", x["cueKey"]))
    sections["introOutro"] = io
    sections["stems"] = stems

    # --- layers (MD2..MD8) with parent master first in the playlist ---
    layers = []
    master_by_key = {it["cueKey"]: it for it in score}
    for n in range(2, 9):
        src = f"MUSIC_SCORE_MD{n}_pack_v1.json"
        for c in packs[f"md{n}"]["cues"]:
            if c["kind"] == "LAYER":
                layers.append(item_from_cue(c, "layers", Q_LAYER, src))
    sections["layers"] = layers

    # --- ambience (composed, CP30) ---
    sections["ambience"] = [item_from_cue(c, "ambience", Q_AMBIENCE, "AMBIENCE_COMPOSED_pack_v1.json")
                            for c in amb["cues"]]

    # --- mixes: measure loudnorm from the real WAV bytes ---
    mix_root = ROOT / "ClientGodot/assets/audio/mix"
    mix_files = sorted(mix_root.rglob("*.wav"))
    with ThreadPoolExecutor(max_workers=4) as ex:
        measured = list(ex.map(lambda p: (p, *loudnorm(p)), mix_files))
    mixes = []
    for p, lufs, tp in measured:
        rel = str(p.relative_to(ROOT))
        mixes.append({
            "cueKey": None, "nameVi": p.stem, "kind": "MIX", "file": rel,
            "sha256": sha256_of(p), "durationSeconds": None,
            "lufs": round(lufs, 2), "truePeakDbtp": round(tp, 2),
            "question": Q_MIX, "priority": "P2",
            "source": "measured in CP9 from the mix WAV bytes (ffmpeg loudnorm)",
        })
    sections["mixes"] = mixes

    # --- VO takes: runtime manifest vo entries (loudness already recorded there) ---
    vos = []
    for f in runtime["files"]:
        if f.get("category") != "vo":
            continue
        rel = "ClientGodot/" + f["runtimePath"]
        vos.append({
            "cueKey": f.get("cueKey"), "nameVi": Path(rel).stem, "kind": "VO", "file": rel,
            "sha256": f["sha256"], "durationSeconds": f.get("durationSeconds"),
            "lufs": f.get("integratedLufs"), "truePeakDbtp": f.get("truePeakDbtp"),
            "question": Q_VO, "priority": "P2",
            "source": "RUNTIME_AUDIO_manifest_v1.json (loudness recorded at delivery)",
        })
    vos.sort(key=lambda x: x["file"])
    sections["vo"] = vos

    # --- flags / priority queue (curated, each cites its source) ---
    def flag(section_items, match, priority, note, source):
        for it in section_items:
            if match(it):
                it["priority"] = priority
                it.setdefault("flags", []).append(note)
                it["flagSource"] = source
                return it
        return None

    p0 = []
    # hottest combined layers
    hot = sorted([it for it in layers if it.get("combinedLufs") is not None],
                 key=lambda x: -x["combinedLufs"])[:3]
    for it in hot:
        it["priority"] = "P0"
        it.setdefault("flags", []).append(
            f"combined base+layer {it['combinedLufs']} LUFS / {it['combinedTruePeakDbtp']} dBTP — top-3 nong nhat, nghe fade-in va ride gain")
        p0.append(it["cueKey"])
    # arena low near the -3.0 dBTP ceiling
    it = flag(layers, lambda x: x["cueKey"] == "MUSIC/arena_layer_low", "P0",
              "combined true peak -3.80 dBTP, sat gioi han -3.0 — nghe co vo/choi khi cong gop khong",
              "MEDIA02_WO37_MD_CP3 report")
    if it: p0.append(it["cueKey"])
    # sa_hoa master seam ear-check flag from the pronunciation table
    it = flag(score, lambda x: x["cueKey"] == "MUSIC/sa_hoa", "P0",
              "seam ear-check flag trong PRONUNCIATION_TABLE_v1 (indicator 0.016015) — nghe dung diem loop",
              "PRONUNCIATION_TABLE_v1.json seamTable")
    if it: p0.append(it["cueKey"])
    # worst composed-ambience seam by wrapJumpRaw
    amb_sorted = sorted(sections["ambience"], key=lambda x: -(x.get("seamWrapJumpRaw") or 0))
    if amb_sorted:
        it = amb_sorted[0]
        it["priority"] = "P0"
        it.setdefault("flags", []).append(
            f"seam wrapJumpRaw cao nhat trong ambience sang tac ({it.get('seamWrapJumpRaw')}) — nghe diem loop 16 s")
        p0.append(it["cueKey"])
    # Ly An S05 hot VO take (CP33): loudest VO item in p0 group
    p0vo = [v for v in vos if "/vo/p0/" in v["file"] and v["lufs"] is not None]
    if p0vo:
        it = max(p0vo, key=lambda x: x["lufs"])
        it["priority"] = "P0"
        it.setdefault("flags", []).append(
            "take VO nong nhat nhom P0 (CP33 do -16.01 LUFS, hon cac take khac ~5.5 LUFS) — nghe co choi tren nen khong")
        p0.append(it["file"])
    # mixes: CIN_011 (8 ms VO margin), the three kept overruns, P0 A/B choice
    for name, note, src in [
        ("CIN_011", "cua so VO chi thua 8 ms (CP45) — nghe cau thoai co bi cat duoi khong", "MEDIA02 checkpoint 45 report"),
        ("CIN_005", "overrun VO +0.160 s GIU NGUYEN cho Codex quyet — nghe muc do lan sang shot sau", "DEC owner 2026-11-06 / CP38"),
        ("CIN_006", "overrun VO +0.520 s GIU NGUYEN cho Codex quyet — ban canonical; alternate take rieng, khong thay canon", "DEC-MEDIA-P0 Q3 / CP20+CP34"),
        ("CIN_018", "overrun VO S03 +0.280 s GIU NGUYEN; take nguoi choi la VOICE_PLACEHOLDER_ONLY", "CP52"),
    ]:
        for it in mixes:
            if name in it["file"] and "_v1" in it["file"] or (name in ("CIN_005", "CIN_006") and name in it["file"]):
                it["priority"] = "P0"
                it.setdefault("flags", []).append(note)
                it["flagSource"] = src
                p0.append(it["file"])
                break

    # --- ids, totals ---
    prefixes = {"scoreMasters": "SCR", "stingers": "STG", "transitions": "TRN",
                "introOutro": "IO", "stems": "STM", "layers": "LAY",
                "ambience": "AMB", "mixes": "MIX", "vo": "VO"}
    counts, total_dur = {}, 0.0
    for sec, items in sections.items():
        for i, it in enumerate(items, 1):
            it["id"] = f"{prefixes[sec]}-{i:03d}"
            if it.get("durationSeconds"):
                total_dur += it["durationSeconds"]
        counts[sec] = len(items)
    priority_queue = []
    for sec, items in sections.items():
        for it in items:
            if it["priority"] == "P0":
                priority_queue.append({"id": it["id"], "section": sec,
                                       "ref": it.get("cueKey") or it["file"],
                                       "flags": it.get("flags", [])})

    pack = {
        "packId": "NGM_EAR_AUDITION_PACK_V1",
        "checkpoint": "MEDIA-02 WO37 M-D checkpoint 9 - ear-audition preparation",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f79853",
        "status": "NOT_AUDITIONED",
        "statusNote": ("This pack PREPARES the ear audition for every composed/mixed/voiced "
                       "asset delivered so far. Nothing in it has been heard by a human ear; "
                       "each item becomes PASS/FAIL only when a listener records a verdict."),
        "howToListen": [
            "Core pass = the priorityQueue below (P0 items). Full pass = every playlist in order.",
            "Playlists are .txt files with M3U content in this same folder; rename a copy to .m3u to open in a player.",
            "Layers must be judged as base+layer summed (the adapter use case); playlists order each layer right after its parent master.",
            "Record verdicts per item id: PASS / FAIL / note. FAIL items come back as fix blocks, not silent edits.",
        ],
        "counts": counts,
        "totalItems": sum(counts.values()),
        "knownDurationSecondsExcludingMixes": round(total_dur, 1),
        "priorityQueue": priority_queue,
        "sections": sections,
        "sources": [
            "MUSIC_COMPOSED_pack_v1.json", "MUSIC_SCORE_MD1_pack_v1.json",
            "MUSIC_SCORE_MD2_pack_v1.json", "MUSIC_SCORE_MD3_pack_v1.json",
            "MUSIC_SCORE_MD4_pack_v1.json", "MUSIC_SCORE_MD5_pack_v1.json",
            "MUSIC_SCORE_MD6_pack_v1.json", "MUSIC_SCORE_MD7_pack_v1.json",
            "MUSIC_SCORE_MD8_pack_v1.json", "AMBIENCE_COMPOSED_pack_v1.json",
            "PRONUNCIATION_TABLE_v1.json",
            "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json",
            "RUNTIME_AUDIO_manifest_v1.json",
        ],
    }
    (REPORTS / "EAR_AUDITION_PACK_v1.json").write_text(
        json.dumps(pack, ensure_ascii=False, indent=1), encoding="utf-8")

    # --- playlists ---
    def playlist(fname, title, entries):
        lines = ["#EXTM3U",
                 f"# MEDIA-02 WO37 M-D checkpoint 9 — ear-audition pack: {title}",
                 "# AUDITION STATUS: NOT_AUDITIONED (prepared for a human listener)",
                 "# M3U content under a .txt name (.m3u is not a policy extension);",
                 "# rename a copy to .m3u to open it directly in a player.",
                 "# Paths are relative to Implementation/Reports/MuseMedia/."]
        for label, rel in entries:
            lines.append(f"#EXTINF:-1,{label}")
            lines.append(PLAYLIST_PREFIX + rel)
        (REPORTS / fname).write_text("\n".join(lines) + "\n", encoding="utf-8")

    playlist("ear_audition_01_score_playlist.txt", "score masters + stingers + transitions",
             [(f"{it['id']} {it['cueKey']}", it["file"]) for it in score]
             + [(f"{it['id']} {it['cueKey']}", it["file"]) for it in sections["stingers"]]
             + [(f"{it['id']} {it['cueKey']}", it["file"]) for it in sections["transitions"]])
    playlist("ear_audition_02_intro_outro_playlist.txt", "intros + outros (per parent cue)",
             [(f"{it['id']} {it['cueKey']}", it["file"]) for it in io])
    lay_entries = []
    for it in layers:
        parent = master_by_key.get(it.get("parentCueKey") or it.get("combinedBaseCueKey"))
        if parent:
            lay_entries.append((f"BASE {parent['cueKey']}", parent["file"]))
        lay_entries.append((f"{it['id']} {it['cueKey']}", it["file"]))
    playlist("ear_audition_03_layers_playlist.txt", "layers (parent master immediately before each layer)",
             lay_entries)
    playlist("ear_audition_04_stems_playlist.txt", "stems (lead / pad-bass / percussion per cue)",
             [(f"{it['id']} {it['cueKey']}", it["file"]) for it in stems])
    playlist("ear_audition_05_ambience_playlist.txt", "composed ambience (16 s loops)",
             [(f"{it['id']} {it['cueKey']}", it["file"]) for it in sections["ambience"]])
    playlist("ear_audition_06_mixes_playlist.txt", "draft mixes (P0 v1/v2/v3 + per-scene v1 + prologue)",
             [(f"{it['id']} {it['nameVi']}", it["file"]) for it in mixes])
    playlist("ear_audition_07_vo_playlist.txt", "VO takes (P0 + campaign + CIN_006 alt + prologue)",
             [(f"{it['id']} {it['nameVi']}", it["file"]) for it in vos])

    print(json.dumps({"counts": counts, "totalItems": pack["totalItems"],
                      "priorityQueue": len(priority_queue),
                      "knownDurationSecondsExcludingMixes": pack["knownDurationSecondsExcludingMixes"]},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
