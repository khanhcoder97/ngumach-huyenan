"""MEDIA-02 WO37 M-F CP2: prologue CIN_000 DRAFT mix v2 -- palette re-mix.

Clone of the MIX portion of build_prologue_film.py (MEDIA-02
checkpoint 27) with ONLY these changes:
  (a) the five narration segments are the M-F CP1 palette pickups
      (narrator re-cast from the draft Helio, avocado_v2:MAI_03,
      to History, avocado_v2:History) instead of the CP27 draft
      narration takes;
  (b) each pickup carries a per-segment gain compensation
      gain = (integrated LUFS of that narration segment as it sits
      in the CP27 mix) - (integrated LUFS of the pickup), both
      measured from real bytes at build time, so the narration
      sits at the same relative level as in CP27 (the History
      pickups measure ~6-8 LUFS quieter than the Helio takes);
  (c) outputs land in Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/
      (CIN_000_mix_draft_v2.wav + CIN_000_MIX_V2_manifest_v1.json).
Everything else is the CP27 mix: the same timeline derived from
the CP27 narration manifest (same segment starts, same total
87.367 s), the composed ben_mua music bed + ported rain_light /
river_shore ambience at the CP27 gains, the bed sidechain-ducked
by the VO bus (threshold 0.03, ratio 4, attack 15 ms, release
350 ms), Ly An's final line reusing the checkpoint-04 take at
-5 dB (Ly An keeps her Aria voice; she has no pickup), the
composed resolve stinger on the title card at -2 dB, and the
same peak guard (trim only above -1.0 dBTP). NO video is built
and the subtitled variant is not touched.

The palette decision: the project owner delegated the voice
choice to Muse (main chat 2026-11-12 18:30 JST) and Muse's
decision is to apply the M-F CP1 palette (side B of the WO39
M39-B CP1 level-matched A/B review) to every role with a
distinct pickup.

DRAFT_NOT_FINAL, NOT_AUDITIONED. The v2 mix lives in Art_Source
only: the runtime still embeds the CP27 v1 mix and the runtime
audio count is unchanged (783); adoption is Codex's decision at
review.
"""
import hashlib
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
VO_MANIFEST = (ROOT / "Art_Source/Audio/Muse/VO"
               / "PROLOGUE_VO_manifest_v1.json")
PICKUP_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"
PICKUP_FILES = [
    "VO_CIN000_SEG01_NARRATOR_palette_v1.wav",
    "VO_CIN000_SEG02_NARRATOR_palette_v1.wav",
    "VO_CIN000_SEG03_NARRATOR_palette_v1.wav",
    "VO_CIN000_SEG04_NARRATOR_palette_v1.wav",
    "VO_CIN000_SEG05_NARRATOR_palette_v1.wav",
]
CP27_MIX = (ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
            / "PROLOGUE_mix_v1.wav")
MIX_DIR = ROOT / "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2"
LYAN_WAV = (ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
            / "VO_CIN001_S05_LYAN_draft_v1.wav")
MUSIC_OGG = (ROOT / "ClientGodot/assets/audio/composed/music"
             / "ben_mua.ogg")
STING_OGG = (ROOT / "ClientGodot/assets/audio/composed/cinema"
             / "resolve.ogg")
RAIN_OGG = ROOT / "ClientGodot/assets/audio/ambience/rain_light.ogg"
RIVER_OGG = (ROOT / "ClientGodot/assets/audio/ambience"
             / "river_shore.ogg")
TMP = Path("/tmp/prologue_mix_v2")
TMP.mkdir(parents=True, exist_ok=True)
FPS = 30
XFADE = 0.7

DECISION_REF = {
    "decision": ("Apply the M-F CP1 voice palette (side B of the "
                 "WO39 M39-B CP1 level-matched A/B review) to every "
                 "role that has a distinct pickup take"),
    "delegatedBy": ("Project owner delegated the voice choice to "
                    "Muse (main chat, 2026-11-12 18:30 JST)"),
    "chosenBy": ("Muse (decision recorded in the dev queue, "
                 "2026-11-12 ~18:32 JST)"),
    "checkpoint": "MEDIA-02 WO37 M-F CP2",
    "paletteSourceManifest": ("Implementation/Content/Audio/Deliveries/"
                              "VO_PALETTE_PICKUPS_pack_v1.json"),
    "adoption": ("Draft v2 mixes live in Art_Source only; the runtime "
                 "still embeds the v1 mixes (runtime audio count "
                 "unchanged at 783) until Codex adopts v2 at review."),
}

SHOTS = [
    ("CIN_000_S01", "prologue_s01.webp",
     "efdff4496062be4d5ca97618600390a0ad7eaa2c1adcf8b0da4a4eb071f98dd6",
     "97b3ba22-6d56-40be-adb6-310d417226e9:ixmbb6",
     "WIDE_AERIAL", "in", (0, [0]),
     ["The five rivers are not cleanly countable (many tributaries "
      "feed the ring): reads as many currents, one ring.",
      "Palette warmer/more ochre than the muted-teal brief.",
      "The ring reads partly as a circular dam/weir."]),
    ("CIN_000_S02", "prologue_s02.webp",
     "31b2189acbf3c441302dfd885bda2ddab544215e03b1039ab2d21f93f80c592f",
     "1098f158-e00d-4616-91a9-c5d63b9cb8ed:n6ztxw",
     "WIDE_PANORAMA", "out", (0, [1]),
     ["The five landscapes blend into one continuous valley; regions "
      "are suggested, not five separated zones.",
      "Tower designs are similar to one another, not strongly "
      "region-differentiated.",
      "16:9 center-crop trims the far-left marsh and far-right "
      "coast slightly."]),
    ("CIN_000_S03", "prologue_s03.webp",
     "c3b13eb688f0a775e0bc780e699e1eee74600bc9164a33d15b7038403f00394b",
     "7c413a31-2129-4cbd-a23c-67f7c3c89b1a:klgp0g",
     "WIDE", "in", (1, [0, 1]),
     ["DESIGN DRIFT vs S01: the mechanism is a tall vertical arch "
      "with bronze gears, not S01's flat circular ring; a "
      "final-picture pass should unify the mechanism design.",
      "Decorative geometric glyph carvings on the arch blocks "
      "(abstract, illegible; not readable text)."]),
    ("CIN_000_S04", "prologue_s04.webp",
     "f9b9a34a1e818a3b16fe7710f6497eb689647ecb7ce52a8a2d8245c12ca3d860",
     "37d6ac99-8535-4dad-9568-897d63998e69:nvkf4g",
     "WIDE", "in", (1, [2, 3]),
     ["The ledger tablet's carvings are pseudo-script glyphs "
      "resembling letterform rows at a glance -- illegible, no "
      "readable words, but the closest any panel comes to text.",
      "All five towers share one identical grey design (region "
      "identity from S02 lost).",
      "The tablet stands by the central pool, not at a tower gate."]),
    ("CIN_000_S05", "prologue_s05.webp",
     "8beac29424aad6ddf40093b9ba0767e6c5c7c59f1f5bce220e755a227452748b",
     "f37fdff5-fbb8-445f-b806-739f7d8687e1:wlo8we",
     "WIDE", "out", (2, [0, 1]),
     ["The empty riverbed reads as a dry cracked valley floor "
      "rather than a carved riverbed channel.",
      "The sun is a stylised starburst, slightly graphic-novel "
      "against the watercolor elsewhere."]),
    ("CIN_000_S06", "prologue_s06.webp",
     "e41da4eda624b1a05d3eda3bc7aa17a964df9414e1f402d140bbf35a18722639",
     "2ac16685-f9ba-4e8e-b149-cca287dce122:d3sqiu",
     "WIDE", "in", (2, [2, 3]),
     ["Two or three blocky multi-storey buildings in the far hazy "
      "skyline read more modern than the setting (distant, "
      "fog-softened).",
      "The quarter reads as already flooded rather than actively "
      "sinking; the bell sits in a full tower, not a bare frame."]),
    ("CIN_000_S07", "prologue_s07.webp",
     "e3284870a275eb80712b0591e8dc7542c91fde293be07b7634d470d8fb195b71",
     "c29fe943-551c-4736-a944-8c00820fba17:x1t463",
     "DETAIL", "in", (2, [4]),
     ["Script flavour drift: decorative pseudo-calligraphy leans "
      "Western cursive, and the wax seal carries a European "
      "heraldic shield-and-wreath crest instead of an East Asian "
      "seal impression (illegible; no letters; signer's face fully "
      "out of frame as required).",
      "The pen shaft reads slightly glossy/metallic, like a "
      "fountain pen, though the tip at the page is brush-like."]),
    ("CIN_000_S08", "prologue_s08.webp",
     "085e9ad36d2e4f2ac6c8669cf9e4dccc781a37b9ddf36accc34f4c8988f0c23a",
     "62d51751-8a79-4e01-81b9-7f1989298b1c:xkar1t",
     "WIDE", "out", (2, [5]),
     ["The missing-volume beat is weak/ambiguous (a dark recessed "
      "bay may or may not read as the gap).",
      "Erased names register only as faint ruled lines (safely "
      "text-free, but the beat leans on narration).",
      "Palette leans greyer than the dusty-amber brief."]),
    ("CIN_000_S09", "prologue_s09.webp",
     "371ad8c832cd387b8fee3374559aa453ee364495b1ef852ceae374c1ca91dd03",
     "6554cd9a-9848-4a64-993d-cd31a721c2d2:0iozcw",
     "DETAIL", "in", (3, [0, 1]),
     ["Hard constraint PASS: no bell and no tower above the water.",
      "The reflected bell is rendered very solidly (modeled volume, "
      "visible clapper); can read as a submerged physical bell "
      "rather than a pure reflection.",
      "An unexplained dark blob at lower-center-left (broken "
      "reflection fragment or submerged stone), not in the prompt."]),
    ("CIN_000_S10", "prologue_s10.webp",
     "16b63306c5c5a681d77471eb06c8c6e3f491cc3a58283dbaff75f90f8ebb6d2f",
     "244e362b-a43d-4992-a5a5-11dcbacedd24:n1kgzg",
     "DETAIL", "in", (3, [2, 3]),
     ["The wax seal's groove count is ambiguous (roughly 4-5 "
      "stacked lines, not crisply five) -- an exact five-groove "
      "canon read cannot be certified from this render.",
      "The letter reads as a bulky cloth-wrapped parcel rather "
      "than a slim letter packet."]),
    ("CIN_000_S11", "prologue_s11.webp",
     "c098f5d1d11eaca4447148b1e282d35e65e6256557f9ad985e1634fae42acef8",
     "f5e5585a-e777-4f0d-9c9b-c76adddaef69:drrgyj",
     "WIDE", "out", (4, [0, 1, 2]),
     ["Hard constraints PASS: traveler strictly from behind, hood "
      "up, no face, no weapon.",
      "MAIN DEFECT: arrival direction is ambiguous -- the pose can "
      "read as BOARDING the boat rather than stepping off onto the "
      "dock. First candidate for the revision pass.",
      "Two or three tiny background figures in distant moored "
      "boats (not requested, do not compete)."]),
]

SEGMENTS_SENTENCES = [
    ["Xưa, Lạc Châu sống nhờ năm dòng mạch chảy dưới lòng đất và "
     "mặt nước.",
     "Năm mạch trao nhau dòng chảy qua một cơ chế điều hòa gọi là "
     "Huyền Ấn — và năm ngọn tháp canh giữ sự trao đổi ấy, để không "
     "vùng nào thừa nước, không vùng nào cạn khô."],
    ["Ba trăm năm trước, một cơn địa chấn phá vỡ cơ chế điều hòa.",
     "Để ngăn thảm họa, người ta tách năm tháp ra khỏi nhau.",
     "Thảm họa qua đi — nhưng từ đó, điều tiết dần biến thành sở hữu.",
     "Mỗi tháp giữ mạch của mình, và giữ cả những danh sách ghi tên "
     "người sống dưới mạch ấy."],
    ["Ba mươi năm trước, hạn hán và lũ lụt nối nhau tràn qua một "
     "vùng quê.",
     "Trong cơn tuyệt vọng, người ta thử nối các mạch lại làm một.",
     "Thí nghiệm vỡ.",
     "Một phần thành phố chìm xuống nước — và nhiều người còn sống "
     "bị ghi vào sổ là đã chết.",
     "Một lệnh phong tỏa được ký.",
     "Rồi hồ sơ bị xóa dần, như thể chưa từng có ai ở đó."],
    ["Ngày nay, dòng chảy ở Lạc Châu không còn đi đúng đường.",
     "Có tiếng chuông ngân dưới mặt nước, ở nơi không hề treo chuông.",
     "Có những cái tên bị mất khỏi danh sách.",
     "Và vẫn còn những lá thư — niêm sáp năm vạch — đi qua các tuyến "
     "đường thủy, chờ người nhận chịu mở."],
    ["Bến Mưa là một bến đò nhỏ nơi các tuyến ấy giao nhau.",
     "Mưa không ngớt.",
     "Và hôm nay, một người khách lạ vừa bước lên bến..."],
]

def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(map(str, cmd))}"
                           f"\n{r.stderr[-1500:]}")
    return r


def probe(path: Path) -> dict:
    out = run(["ffprobe", "-v", "error", "-show_format",
               "-show_streams", "-of", "json", str(path)]).stdout
    return json.loads(out)


def loudnorm(path: Path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null",
                        "-"], capture_output=True, text=True)
    err = r.stderr
    data = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])

def build_timeline(vo: dict):
    """Derive shot spans from measured narration durations.

    Returns (shots, cues): shots carry raw durations and FINAL
    timeline windows (after 0.7 s xfade overlaps); cues are the SRT
    dialogue windows on the final timeline."""
    segs = vo["segments"]
    assert len(segs) == 5
    for i, sents in enumerate(SEGMENTS_SENTENCES):
        joined = " ".join(sents)
        assert joined == segs[i]["text"], f"segment {i} text drift"
    lyan_dur = vo["finalLine"]["durationSeconds"]
    layout = []  # (shot meta, seg idx, raw duration)
    seg_vo_start = {}
    cursor = 0.0
    for seg_idx, seg in enumerate(segs):
        lead = 1.4 if seg_idx == 0 else 0.9
        tail = 1.0
        breath = 0.0 if seg_idx == 4 else 0.6
        vo_dur = seg["durationSeconds"]
        seg_shots = [(i, s) for i, s in enumerate(SHOTS)
                     if s[6][0] == seg_idx]
        # sentence-share of the VO region per shot, with a 3.2 s
        # floor redistributed proportionally (water-filling).
        shares = []
        for _, s in seg_shots:
            chars = sum(len(SEGMENTS_SENTENCES[seg_idx][j])
                        for j in s[6][1])
            shares.append(chars)
        total_chars = sum(shares)
        region = [vo_dur * c / total_chars for c in shares]
        floor = 3.2
        for _ in range(10):
            under = [k for k, r in enumerate(region) if r < floor]
            if not under:
                break
            deficit = sum(floor - region[k] for k in under)
            over = [k for k, r in enumerate(region) if r >= floor]
            room = sum(region[k] - floor for k in over)
            for k in under:
                region[k] = floor
            for k in over:
                region[k] -= deficit * (region[k] - floor) / room
        span = lead + vo_dur + tail + breath
        if seg_idx == 4:
            span += 0.7 + lyan_dur + 1.0  # pause + Ly An + hold
        pos = cursor
        seg_vo_start[seg_idx] = pos + lead
        for k, (shot_i, s) in enumerate(seg_shots):
            start_rel = 0.0 if k == 0 else lead + sum(region[:k])
            end_rel = span if k == len(seg_shots) - 1 else \
                lead + sum(region[:k + 1])
            layout.append((shot_i, s, end_rel - start_rel))
        cursor += span
    title_dur = 3.6
    layout.append((None, None, title_dur))
    # Quantize every clip to whole frames so the computed timeline
    # and the rendered frame counts agree exactly.
    layout = [(si, s, round(raw * FPS) / FPS) for si, s, raw in layout]
    # Final timeline: each xfade overlaps XFADE seconds.
    finals = []
    t = 0.0
    for shot_i, s, raw in layout:
        finals.append((shot_i, s, raw, t, t + raw))
        t += raw - XFADE
    total = t + XFADE
    # VO cue windows on the final timeline: a segment's first shot
    # final-start + lead; Ly An sits inside S11 after SEG05 + tail +
    # pause (its raw offset), shifted by S11's xfade count (10).
    cues = []
    for seg_idx, seg in enumerate(segs):
        first_i = next(i for i, (si, s, raw, fs, fe)
                       in enumerate(finals) if s and s[6][0] == seg_idx)
        lead = 1.4 if seg_idx == 0 else 0.9
        start = finals[first_i][3] + lead
        cues.append({"speaker": "NARRATOR", "text": seg["text"],
                     "start": start,
                     "end": start + seg["durationSeconds"],
                     "takeId": seg["takeId"]})
    s11 = finals[10]
    lyan_start = s11[3] + 0.9 + segs[4]["durationSeconds"] + 1.0 + 0.7
    cues.append({"speaker": "NPC_LYAN",
                 "text": vo["finalLine"]["text"],
                 "start": lyan_start,
                 "end": lyan_start + lyan_dur,
                 "takeId": "VO_CIN001_S05_LYAN (reused CP04)"})
    title_start = finals[11][3]
    return finals, cues, total, title_start, lyan_start

def segment_loudnorm(path: Path, start: float, dur: float):
    """Integrated LUFS / true peak of one span of a mix, measured
    with ffmpeg loudnorm on the extracted span."""
    r = subprocess.run(
        ["ffmpeg", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}",
         "-i", str(path), "-vn", "-af",
         "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"segment loudnorm failed: {path} "
                           f"@{start}\n{r.stderr[-1500:]}")
    err = r.stderr
    data = json.loads(err[err.rfind("{"):err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def render_mix_v2(cues, total, title_start, lyan_start, gains,
                  trim_db=0.0):
    """The CP27 render_mix filtergraph, with the narration inputs
    swapped for the palette pickups and a per-segment compensation
    gain on each narration leg. Bed gains, Ly An gain, stinger,
    ducking, fades and trim are the CP27 values."""
    cmd = ["ffmpeg", "-y", "-v", "error",
           "-stream_loop", "1", "-i", str(MUSIC_OGG),
           "-stream_loop", "-1", "-i", str(RAIN_OGG),
           "-stream_loop", "-1", "-i", str(RIVER_OGG)]
    for name in PICKUP_FILES:
        cmd += ["-ac", "2", "-i", str(PICKUP_DIR / name)]
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
        parts.append(f"[{3 + i}:a]aresample=48000,"
                     f"volume={gains[i]:.2f}dB,adelay={ms}|{ms}"
                     f"[v{i}]")
        vo_labels.append(f"[v{i}]")
    lyan_ms = int(round(lyan_start * 1000))
    parts.append(f"[8:a]aresample=48000,adelay={lyan_ms}|{lyan_ms},"
                 f"volume=-5dB[ly]")
    vo_labels.append("[ly]")
    parts.append("".join(vo_labels) +
                 f"amix=inputs={len(vo_labels)}:normalize=0[vo]")
    # M-F CP2 PLUMBING FIX (recipe unchanged): CP27's graph fed
    # the single [vo] label to BOTH sidechaincompress and the
    # final amix; ffmpeg frame-stealing between the two consumers
    # drops / shifts narration frames in the final mix (measured
    # on the CP27 v1 mix: SEG01 take correlates ~0.01 with its
    # mix span, the take peak is absent, and two identical renders
    # of the shared-label graph measure differently). asplit gives
    # each consumer its own copy; every recipe parameter (gains,
    # ducking, fades, peak guard) is identical to CP27. The bus is
    # apad'ed to the full timeline first (silence after the last
    # line): without it the sidechain filter ends the ducked bed
    # when the key stream EOFs at ~82.8 s and the mix comes out
    # 0.45 s short (measured).
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
    MIX_DIR.mkdir(parents=True, exist_ok=True)
    out = MIX_DIR / "CIN_000_mix_draft_v2.wav"
    run(cmd + ["-filter_complex", ";".join(parts), "-map", "[mix]",
               "-c:a", "pcm_s16le", "-ar", "48000", str(out)])
    return out


def audible_end(path: Path, thr_db: float = -50.0) -> float:
    """End of audible content in a WAV: the last sample above
    thr_db (TTS renders carry trailing padding silence; a segment
    slot is only truly overrun if AUDIBLE content crosses it)."""
    with wave.open(str(path), "rb") as w:
        sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
        x = np.frombuffer(w.readframes(n),
                          dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    idx = np.nonzero(np.abs(x) > 10 ** (thr_db / 20))[0]
    return (idx[-1] + 1) / sr if len(idx) else 0.0


def probe_duration(path: Path) -> float:
    pr = probe(path)
    return float(pr["format"]["duration"])


def main() -> int:
    vo = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    finals, cues, total, title_start, lyan_start = build_timeline(vo)
    pickups = json.loads(
        (ROOT / "Implementation/Content/Audio/Deliveries"
         / "VO_PALETTE_PICKUPS_pack_v1.json").read_text(encoding="utf-8"))
    by_key = {t["takeKey"]: t for t in pickups["takes"]}

    # Per-segment gain compensation: level of the segment as it
    # sits in the CP27 mix minus the pickup's own level.
    seg_records = []
    gains = []
    for i, c in enumerate(cues[:5]):
        take = by_key[f"CIN000_SEG0{i + 1}"]
        pk = PICKUP_DIR / PICKUP_FILES[i]
        in_mix_lufs, _ = segment_loudnorm(
            CP27_MIX, c["start"], c["end"] - c["start"])
        pk_lufs, pk_tp = loudnorm(pk)
        gain = round(in_mix_lufs - pk_lufs, 2)
        gains.append(gain)
        pk_dur = probe_duration(pk)
        seg_records.append({
            "segment": i + 1,
            "takeKey": f"CIN000_SEG0{i + 1}",
            "previousVoice": take["previousVoice"],
            "paletteVoice": take["voice"],
            "paletteVoiceLabel": take.get("voiceLabel"),
            "paletteTakeFile": ("Art_Source/Audio/Muse/VO/"
                                "PALETTE_PICKUPS_v1/" + PICKUP_FILES[i]),
            "paletteTakeSha256": sha256_file(pk),
            "paletteTakeDurationSeconds": round(pk_dur, 3),
            "paletteTakeIntegratedLufs": round(pk_lufs, 2),
            "cp27SegmentStartSeconds": round(c["start"], 3),
            "cp27SegmentDurationSeconds": round(c["end"] - c["start"], 3),
            "cp27MixSegmentIntegratedLufs": round(in_mix_lufs, 2),
            "appliedGainDb": gain,
            "paletteEndSeconds": round(c["start"] + pk_dur, 3),
            "paletteAudibleEndSeconds": round(
                c["start"] + audible_end(pk), 3),
        })
        print(f"SEG0{i + 1}: CP27 mix segment {in_mix_lufs:.2f} LUFS, "
              f"pickup {pk_lufs:.2f} LUFS -> gain {gain:+.2f} dB")
    # Overlap safety: each pickup's AUDIBLE content must end
    # before the next narration start (or, for SEG05, before the
    # Ly An line). Trailing padding silence below -50 dBFS may
    # cross the boundary; it is measured and recorded, not hidden.
    for i, rec in enumerate(seg_records):
        limit = (seg_records[i + 1]["cp27SegmentStartSeconds"]
                 if i < 4 else lyan_start)
        rec["slotEndSeconds"] = round(limit, 3)
        rec["fileTailOverlapSeconds"] = round(
            max(0.0, rec["paletteEndSeconds"] - limit), 3)
        assert rec["paletteAudibleEndSeconds"] <= limit + 0.01, (
            f"SEG0{i + 1} pickup AUDIBLE content overruns its "
            f"slot: ends {rec['paletteAudibleEndSeconds']} > {limit}")

    mix = render_mix_v2(cues, total, title_start, lyan_start, gains)
    lufs, tp = loudnorm(mix)
    trim = 0.0
    for _ in range(2):
        if tp <= -1.0:
            break
        trim += (-1.0 - tp - 0.1)
        mix = render_mix_v2(cues, total, title_start, lyan_start,
                            gains, trim)
        lufs, tp = loudnorm(mix)
    dur = probe_duration(mix)
    assert abs(dur - total) <= 0.05, (dur, total)
    print(f"mix v2: {dur:.3f} s, {lufs:.2f} LUFS / {tp:.2f} dBTP "
          f"(trim {trim:.2f} dB)")

    manifest = {
        "manifestId": "NGM_CIN000_MIX_V2",
        "checkpoint": "MEDIA-02 WO37 M-F CP2",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "decisionRef": DECISION_REF,
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "file": "CIN_000_mix_draft_v2.wav",
        "sha256": sha256_file(mix),
        "sizeBytes": mix.stat().st_size,
        "durationSeconds": round(dur, 4),
        "integratedLufs": round(lufs, 2),
        "truePeakDbtp": round(tp, 2),
        "peakTrimDb": round(trim, 2),
        "assetState": "DRAFT_MIX_NOT_FINAL",
        "sourceMixV1": {
            "file": "PROLOGUE_mix_v1.wav",
            "dir": "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT",
            "sha256": sha256_file(CP27_MIX),
            "note": ("CP27 mix, byte-unchanged; v2 re-derives the "
                     "timeline from the same CP27 narration "
                     "manifest and measures its segment levels "
                     "from these bytes."),
        },
        "paletteRemix": {
            "checkpoint": "MEDIA-02 WO37 M-F CP2",
            "palette": "M-F CP1 (side B)",
            "narrationChanges": seg_records,
            "finalLine": ("UNCHANGED: Ly An's final line reuses "
                          "the checkpoint-04 take "
                          "(VO_CIN001_S05_LYAN_draft_v1.wav, sha "
                          "51fc65de...) at -5 dB, as in CP27; Ly An "
                          "keeps her Aria voice and has no pickup."),
            "gainMethod": ("Per-segment compensation: (integrated "
                           "LUFS of the segment span measured in "
                           "the CP27 mix) - (integrated LUFS of "
                           "the pickup file); no EQ, compression, "
                           "limiting or re-synthesis."),
        },
        "stems": [
            {"role": "narration", "source": "M-F CP1 palette "
             "pickups (History), gain-compensated per segment",
             "provenance": "NEW_DRAFT_VO_PALETTE"},
            {"role": "final line", "source": "VO_CIN001_S05_LYAN_"
             "draft_v1.wav (checkpoint 04 take, reused bytes)",
             "provenance": "REUSED_CP04"},
            {"role": "music bed", "source": "MUSIC/ben_mua composed "
             "runtime OGG (checkpoint 26)", "gainDb": -9.07,
             "provenance": "ORIGINAL_COMPOSED_BY_MUSE_CP26"},
            {"role": "ambience", "source": "AMBIENCE/rain_light + "
             "AMBIENCE/river_shore runtime OGGs (checkpoint 07 pack)",
             "gainDb": [-8.52, -8.47],
             "provenance": "PORTED_CODEX_PACKV1"},
            {"role": "title stinger", "source": "SFX/CINEMA/resolve "
             "composed runtime OGG (checkpoint 26)",
             "provenance": "ORIGINAL_COMPOSED_BY_MUSE_CP26"},
        ],
        "ducking": "sidechaincompress on the music+ambience bed, "
                   "keyed by the VO bus: threshold 0.03, ratio 4, "
                   "attack 15 ms, release 350 ms (checkpoint 20 "
                   "settled values); peak guard trims the whole mix "
                   "only above -1.0 dBTP",
        "notes": [
            "DRAFT_NOT_FINAL, NOT_AUDITIONED: formula gain staging, "
            "no ear audition; the History narration is a deliberately "
            "different voice from the CP27 Helio draft -- that "
            "difference IS the palette decision, not a defect.",
            "Timeline identical to CP27 (segment starts and total "
            "duration derived from the CP27 narration manifest); "
            "pickup durations differ from the Helio takes, so the "
            "silences between segments differ slightly; every "
            "pickup's audible content ends inside its CP27 slot "
            "(asserted at build). SEG02's pickup FILE is 0.118 s "
            "longer than its slot: only trailing padding silence "
            "below -50 dBFS crosses into SEG03's leading silence; "
            "the audible narration ends 0.193 s early (measured, "
            "recorded per segment in the manifest).",
            "No video is built by this tool and the CP28 subtitled "
            "variant is untouched; the runtime still embeds the "
            "CP27 mix.",
        ],
    }
    (MIX_DIR / "CIN_000_MIX_V2_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    print("OK: CIN_000_MIX_V2_manifest_v1.json written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
