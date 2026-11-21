#!/usr/bin/env python3
"""MEDIA-02 checkpoint 27: prologue film CIN_000 "Truoc khi toi Ben Mua".

Owner request + script approval (main chat 2026-11-06): a cinematic
lore prologue shown after character creation and before gameplay --
the origin of the Five Veins, the quake ~300 years ago, the disaster
and sealing ~30 years ago, the present wrong currents, and the
arrival at Ben Mua, ending on Ly An's canonical first line so the
film hands off into CIN_001 / the first map.

Canon guardrails (Content Bible section 1; Narrative Depth section
2-3; STORY_DECISIONS_V3):
  - no avatar origin/name/face, no secret bloodline, no chosen one;
    the traveler is a back-view cloaked silhouette (class-neutral);
  - the reveal table forbids naming Co Vo Tuong, the hop mach
    mechanism, or Ta Van Khanh's responsibility at this story point:
    the narration hints, never names;
  - no boss kill and no seal-fragment reaction before gameplay;
  - the final line reuses the checkpoint 04 CIN_001_S05 take (vB).

Pipeline (mirrors the campaign builders, extended for a film WITH a
mixed soundtrack -- campaign clips intentionally carry no audio):
  1. verify staging WebP SHAs (registry below, from the three group
     handover notes) and downscale to 640x360 keyframe PNGs;
  2. render the title card with PIL (DejaVu Sans Bold);
  3. derive the shot timeline from the MEASURED narration durations
     (PROLOGUE_VO_manifest_v1.json): shots tile each segment's span
     by sentence-share; SRT cues are the 5 narration segments + the
     Ly An line, placed on the post-crossfade timeline;
  4. render per-shot zoompan clips and chain them with 0.7 s xfades
     (fadeblack into the title card), fade in/out;
  5. mix: narration bus (unity) + reused Ly An take (-5 dB to sit
     with the narration) over a ducked bed of the checkpoint 26
     COMPOSED ben_mua theme (looped) + ported rain_light/river_shore
     ambience (provenance kept separate) + the composed resolve
     stinger on the title card; sidechain ducking uses the settled
     checkpoint 20 values; peak guard trims only above -1.0 dBTP;
  6. mux MP4 (H.264 + AAC) and OGV (Theora + Vorbis) WITH the mix;
     poster = the title card PNG (documented choice for this film);
  7. write keyframe / film / scene-export manifests and copy timing
     + SRT into the runtime folder.

Outputs:
  Art_Source/Cinematics/Prologue/keyframes_16x9/*.png
  Art_Source/Cinematics/Prologue/CIN000_keyframes_manifest_v1.json
  Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json
  Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav (+manifest)
  Implementation/Content/Narrative/Deliveries/CIN_000/ (timing + SRT)
  ClientGodot/assets/cinematics/CIN_000/ (MP4/OGV/poster/timing/SRT/
     scene_export_manifest_v1.json)
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
STAGING = (Path.home() / "workspace/goals/ng-m-ch-continuous-"
           "development/hidden_files/prologue_keyframes_staging")
KF_DIR = ROOT / "Art_Source/Cinematics/Prologue/keyframes_16x9"
PRO_DIR = ROOT / "Art_Source/Cinematics/Prologue"
DELIV = ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000"
RT_DIR = ROOT / "ClientGodot/assets/cinematics/CIN_000"
MIX_DIR = ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT"
VO_MANIFEST = (ROOT / "Art_Source/Audio/Muse/VO"
               / "PROLOGUE_VO_manifest_v1.json")
LYAN_WAV = (ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
            / "VO_CIN001_S05_LYAN_draft_v1.wav")
MUSIC_OGG = (ROOT / "ClientGodot/assets/audio/composed/music"
             / "ben_mua.ogg")
STING_OGG = (ROOT / "ClientGodot/assets/audio/composed/cinema"
             / "resolve.ogg")
RAIN_OGG = ROOT / "ClientGodot/assets/audio/ambience/rain_light.ogg"
RIVER_OGG = (ROOT / "ClientGodot/assets/audio/ambience"
             / "river_shore.ogg")
TMP = Path("/tmp/prologue_film")
TMP.mkdir(parents=True, exist_ok=True)
FPS = 30
XFADE = 0.7

# shotId, staging file, staging sha256, snapshot id, camera, motion,
# (segment index, [sentence indices]) -- sentences split the segment
# text for span shares; defects from the group handover notes.
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


def srt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


PROMPTS = {
    "CIN_000_S01": "Painterly cinematic concept art, watercolor-and-ink, muted teal and ochre palette, soft volumetric light, no text, no watermark: an ancient stylized landmass seen from high above like a living map, five great rivers of faintly luminous water flowing beneath and across the land, converging and exchanging currents around a central stone-and-bronze ring mechanism, fertile valleys, dawn mist, serene and mythic mood, 16:9 composition.",
    "CIN_000_S02": "Painterly cinematic concept art, watercolor-and-ink, muted teal and ochre palette, soft volumetric light, no text, no watermark: five distinct watchtowers standing in five different landscapes of one realm — river delta, pine forest, dry furnace hills, mountain pass, sunken coast — connected by streams of gently glowing water flowing between them, golden morning, harmony and balance, wide panoramic composition, 16:9.",
    "CIN_000_S03": "Painterly cinematic concept art, watercolor-and-ink, muted slate and ochre palette, dramatic light, no text, no watermark: the moment of a great earthquake in an old river land, ground cracking in dark fissures, a monumental stone-and-bronze ring mechanism tilting and fracturing, watchtowers trembling in the distance, dust and startled birds, no people in close view, no gore, wide 16:9 composition.",
    "CIN_000_S04": "Painterly cinematic concept art, watercolor-and-ink, muted grey-teal palette, cold fog, no readable text, no watermark: five watchtowers now separated by fog, dams and closed gates, each hoarding its own pool of still water, a stone ledger tablet with rows of illegible carved strokes standing by a tower gate, lonely possessive mood, wide 16:9 composition.",
    "CIN_000_S05": "Painterly cinematic concept art, watercolor-and-ink, muted ochre and slate palette, harsh divided light, no text, no watermark: a split landscape of disaster — on one side cracked dry earth and an empty riverbed under a white sun, on the other side flood water rising over rice fields and rooftops under black rain clouds, a village caught between drought and flood, wide 16:9 composition.",
    "CIN_000_S06": "Painterly cinematic concept art, watercolor-and-ink, deep teal and dusk-gold palette, melancholic light, no text, no watermark: a city quarter slowly sinking into still water at dusk, tiled rooftops and a bell frame emerging from the surface, small wooden boats moving between roofs carrying silhouetted people to safety, no faces in close view, quiet tragedy, wide 16:9 composition.",
    "CIN_000_S07": "Painterly cinematic concept art, watercolor-and-ink, warm candlelight against dark teal shadow, no readable text, no watermark: extreme close view of a hand in a dark sleeve signing a paper order with a brush pen by candlelight, a wax seal stamp pressed beside illegible calligraphy strokes, the signer's face completely out of frame, heavy fateful mood, 16:9 composition.",
    "CIN_000_S08": "Painterly cinematic concept art, watercolor-and-ink, dusty amber and grey palette, dim archive light, no readable text, no watermark: a dim archive room of wooden shelves and bound ledgers, some ledger pages with rows of names faded, scratched out and washed away into illegible pale strokes, dust motes in a shaft of light, an empty space on a shelf where a volume is missing, mood of deliberate forgetting, 16:9 composition.",
    "CIN_000_S09": "Painterly cinematic concept art, watercolor-and-ink, dark teal water palette, soft rain light, no text, no watermark: a rain-pocked dark water surface at a wooden dock, in the reflection beneath the water appears the clear contour of a large hanging bell — but above the surface there is only empty air and rain, no bell and no tower, one ripple breaking the reflected contour, mysterious and quiet, 16:9 composition.",
    "CIN_000_S10": "Painterly cinematic concept art, watercolor-and-ink, warm wood and rain-grey palette, gentle light, no readable text, no watermark: close view inside a small wooden cargo boat in the rain — woven parcels and a letter wrapped in oilcloth sealed with dark wax bearing five fine groove lines, rope and a bamboo basket beside it, river water and reeds beyond the gunwale, the letter is the clear subject, 16:9 composition.",
    "CIN_000_S11": "Painterly cinematic concept art, watercolor-and-ink, rain-teal and lantern-amber palette, soft volumetric rain light, no text, no watermark: wide view of a rainy ferry landing in a Vietnamese river village — wet wooden dock, warehouse with tiled roof, mooring posts, a small boat just arrived, and a lone traveler seen strictly from behind in a plain hooded travelling cloak with no visible weapon, stepping onto the wet planks carrying a simple bag, rain falling steadily, lantern light reflecting on wet wood, cinematic arrival mood, 16:9 composition.",
}
HANDOVERS = {0: "prologue_keyframes_handover_a_20261106.md",
             1: "prologue_keyframes_handover_a_20261106.md",
             2: "prologue_keyframes_handover_a_20261106.md",
             3: "prologue_keyframes_handover_a_20261106.md",
             4: "prologue_keyframes_handover_b_20261106.md",
             5: "prologue_keyframes_handover_b_20261106.md",
             6: "prologue_keyframes_handover_b_20261106.md",
             7: "prologue_keyframes_handover_b_20261106.md",
             8: "prologue_keyframes_handover_c_20261106.md",
             9: "prologue_keyframes_handover_c_20261106.md",
             10: "prologue_keyframes_handover_c_20261106.md"}


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


def make_keyframes() -> dict:
    KF_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for i, (shot_id, fname, sha, snap, camera, motion, segmap,
            defects) in enumerate(SHOTS):
        src = STAGING / fname
        assert src.exists(), f"staging missing {fname}"
        got = sha256_file(src)
        assert got == sha, f"{shot_id}: staging sha {got} != {sha}"
        img = Image.open(src).convert("RGB")
        assert img.size == (2048, 1152), (shot_id, img.size)
        out = KF_DIR / f"keyframe_{shot_id}.png"
        img.resize((640, 360), Image.LANCZOS).save(out)
        frames.append({
            "shotId": shot_id, "camera": camera, "motion": motion,
            "keyframePng": f"Art_Source/Cinematics/Prologue/"
                           f"keyframes_16x9/keyframe_{shot_id}.png",
            "keyframeSha256": sha256_file(out),
            "staging": {"file": fname, "sha256": sha,
                        "snapshotId": snap,
                        "handoverNote": HANDOVERS[i],
                        "transform": "center-crop to 16:9 + resize "
                                     "2048x1152 by the staging agent "
                                     "(some natives were 3:2 / 2:1); "
                                     "builder downscales to 640x360"},
            "prompt": PROMPTS[shot_id],
            "knownDefects": defects,
        })
    # Title card (code-rendered, not generated).
    title = Image.new("RGB", (640, 360), (7, 11, 13))
    glow = np.zeros((360, 640, 3), dtype=np.float32)
    yy, xx = np.mgrid[0:360, 0:640]
    d = np.sqrt(((xx - 320) / 300.0) ** 2 + ((yy - 180) / 170.0) ** 2)
    glow[..., 0] = np.clip(1.2 - d, 0, 1) * 14
    glow[..., 1] = np.clip(1.2 - d, 0, 1) * 22
    glow[..., 2] = np.clip(1.2 - d, 0, 1) * 24
    base = np.asarray(title).astype(np.float32) + glow
    title = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(title)
    bold = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    reg = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    f1 = ImageFont.truetype(bold, 62)
    f2 = ImageFont.truetype(bold, 40)
    gold = (216, 178, 92)
    pale = (196, 205, 200)

    def centered(text, font, y, fill, tracking=0):
        if tracking == 0:
            w = dr.textlength(text, font=font)
            dr.text(((640 - w) / 2, y), text, font=font, fill=fill)
            return
        widths = [dr.textlength(ch, font=font) for ch in text]
        total_w = sum(widths) + tracking * (len(text) - 1)
        x = (640 - total_w) / 2
        for ch, wch in zip(text, widths):
            dr.text((x, y), ch, font=font, fill=fill)
            x += wch + tracking

    centered("NGŨ MẠCH", f1, 118, gold)
    dr.line([(220, 205), (420, 205)], fill=(140, 118, 66), width=2)
    centered("HUYỀN ẤN", f2, 224, pale, tracking=10)
    out = KF_DIR / "keyframe_CIN_000_S12.png"
    title.save(out)
    frames.append({
        "shotId": "CIN_000_S12", "camera": "TITLE_CARD",
        "motion": "static",
        "keyframePng": "Art_Source/Cinematics/Prologue/keyframes_16x9/"
                       "keyframe_CIN_000_S12.png",
        "keyframeSha256": sha256_file(out),
        "staging": {"file": None, "sha256": None, "snapshotId": None,
                    "handoverNote": None,
                    "transform": "rendered in code with PIL "
                                 "(DejaVu Sans Bold); no generation"},
        "prompt": None,
        "knownDefects": ["Title typography uses DejaVu Sans Bold, a "
                         "placeholder until a game display font is "
                         "locked (the project has no locked "
                         "Vietnamese pixel/display font yet)."],
    })
    manifest = {
        "manifestId": "NGM_CIN000_KEYFRAMES_V1",
        "sceneId": "CIN_000",
        "title": "Trước khi tới Bến Mưa",
        "checkpoint": "MEDIA-02 checkpoint 27",
        "level": "CINEMATIC_PANELS_NOT_FINAL_PICTURE",
        "frames": frames,
        "notes": [
            "Panels are painterly cinematic art (not pixel-art "
            "sprites); the prologue is a pre-game film, so it does "
            "not use the 20 PPU sprite standard.",
            "Cross-shot mechanism drift (S01 flat ring vs S03 "
            "vertical arch) and S11's ambiguous arrival direction "
            "are the headline revision-pass items.",
        ],
    }
    (PRO_DIR / "CIN000_keyframes_manifest_v1.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    return manifest


def write_timing_srt(finals, cues, total):
    import unicodedata
    shots_json = []
    cue_by_shot = {}
    for c in cues:
        cue_by_shot.setdefault(c["takeId"], c)
    seg_first_shot = {}
    for si, s, raw, fs, fe in finals:
        if s:
            seg_first_shot.setdefault(s[6][0], s[0])
    for si, s, raw, fs, fe in finals:
        if s is None:
            shots_json.append({
                "shotId": "CIN_000_S12", "startSeconds": round(fs, 3),
                "endSeconds": round(fe, 3), "camera": "TITLE_CARD",
                "dialogue": []})
            continue
        dlg = []
        for c in cues:
            seg_idx = s[6][0]
            if c["speaker"] == "NARRATOR" and \
                    seg_first_shot.get(seg_idx) == s[0] and \
                    abs(c["start"] - (fs + (1.4 if seg_idx == 0
                                            else 0.9))) < 0.01:
                dlg.append({"speaker": "NARRATOR",
                            "startSeconds": round(c["start"], 3),
                            "endSeconds": round(c["end"], 3),
                            "text": c["text"], "takeId": c["takeId"]})
            if c["speaker"] == "NPC_LYAN" and s[0] == "CIN_000_S11":
                dlg.append({"speaker": "NPC_LYAN",
                            "startSeconds": round(c["start"], 3),
                            "endSeconds": round(c["end"], 3),
                            "text": c["text"], "takeId": c["takeId"]})
        shots_json.append({
            "shotId": s[0], "startSeconds": round(fs, 3),
            "endSeconds": round(fe, 3), "camera": s[4],
            "dialogue": dlg})
    timing = {
        "sceneId": "CIN_000",
        "questId": "INTRO_PROLOGUE",
        "title": "Trước khi tới Bến Mưa",
        "durationSeconds": round(total, 3),
        "playback": "PRE_GAME_INTRO_AFTER_CHARACTER_CREATION",
        "runtimeActivation": "DESIGN_HANDOFF_NOT_YET_INTEGRATED",
        "revealTier": "PROLOGUE_NO_SPOILER",
        "charactersOnScreen": [],
        "staging": "NO_NAMED_CHARACTER_ON_SCREEN; the traveler in "
                   "S11 is an unnamed back-view silhouette (no class "
                   "design, no face, no weapon); no persistent ID, "
                   "no spawn claim",
        "stagingNote": "The prologue is a standalone pre-game film, "
                       "separate from the 20-scene campaign pack; it "
                       "is NOT counted in the campaign totals.",
        "audioDirection": "Vietnamese narration (draft TTS) over the "
                          "checkpoint 26 composed Ben Mua theme + "
                          "ported rain/river ambience, sidechain-"
                          "ducked; the mixed track is embedded in the "
                          "film files. Final line reuses the CP04 "
                          "CIN_001_S05 take.",
        "dialogueWindowStatus": "OWNER_APPROVED_SCRIPT_20261106",
        "dialogueWindowNote": "Narration script approved by the "
                              "owner in main chat 2026-11-06; shot "
                              "windows derive from the measured VO "
                              "durations, not from a pack timecode.",
        "shots": shots_json,
    }
    DELIV.mkdir(parents=True, exist_ok=True)
    timing_path = DELIV / "CIN_000_timing_v1.json"
    timing_path.write_text(json.dumps(timing, ensure_ascii=False,
                                      indent=1) + "\n",
                           encoding="utf-8")
    lines = []
    for i, c in enumerate(cues, 1):
        text = unicodedata.normalize("NFC", c["text"])
        lines.append(f"{i}\n{srt_ts(c['start'])} --> "
                     f"{srt_ts(c['end'])}\n{text}\n")
    srt_path = DELIV / "CIN_000_vi.srt"
    srt_path.write_text("\n".join(lines), encoding="utf-8")
    return timing_path, srt_path


def render_shot_clip(shot_id: str, kf_png: Path, raw_dur: float,
                     motion: str) -> Path:
    frames = int(round(raw_dur * FPS))
    up = TMP / f"{shot_id}_up.png"
    Image.open(kf_png).convert("RGB").resize(
        (1280, 720), Image.LANCZOS).save(up)
    out = TMP / f"{shot_id}.mp4"
    if motion == "static":
        run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i",
             str(up), "-vf", f"fps={FPS},scale=640:360",
             "-frames:v", str(frames), "-c:v", "libx264",
             "-pix_fmt", "yuv420p", str(out)])
        return out
    if motion == "in":
        z = f"1+0.07*on/{max(1, frames - 1)}"
    else:
        z = f"1.07-0.07*on/{max(1, frames - 1)}"
    vf = (f"zoompan=z='{z}':x='iw/2-(iw/zoom/2)':"
          f"y='ih/2-(ih/zoom/2)':d={frames}:s=640x360:fps={FPS}")
    run(["ffmpeg", "-y", "-v", "error", "-i", str(up), "-vf", vf,
         "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out)])
    return out


def render_video(finals) -> Path:
    clips = []
    for si, s, raw, fs, fe in finals:
        if s is None:
            clips.append(render_shot_clip(
                "CIN_000_S12", KF_DIR / "keyframe_CIN_000_S12.png",
                raw, "static"))
        else:
            clips.append(render_shot_clip(
                s[0], KF_DIR / f"keyframe_{s[0]}.png", raw, s[5]))
    cmd = ["ffmpeg", "-y", "-v", "error"]
    for c in clips:
        cmd += ["-i", str(c)]
    filt = []
    prev = "[0:v]"
    for k in range(1, len(clips)):
        off = finals[k][3]
        trans = "fadeblack" if k == len(clips) - 1 else "fade"
        label = f"[x{k}]"
        filt.append(f"{prev}[{k}:v]xfade=transition={trans}:"
                    f"duration={XFADE}:offset={off:.3f}{label}")
        prev = label
    total = finals[-1][4]
    filt.append(f"{prev}fade=t=in:st=0:d=1.0,fade=t=out:"
                f"st={total - 1.2:.3f}:d=1.2,format=yuv420p[vout]")
    out = TMP / "prologue_video.mp4"
    run(cmd + ["-filter_complex", ";".join(filt), "-map", "[vout]",
               "-c:v", "libx264", "-crf", "19", "-r", str(FPS),
               str(out)])
    return out


def render_mix(cues, total, title_start, lyan_start, trim_db=0.0):
    vo = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    seg_files = [ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
                 / s["file"] for s in vo["segments"]]
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
    parts.append("[bed][vo]sidechaincompress=threshold=0.03:"
                 "ratio=4:attack=15:release=350[duck]")
    st_ms = int(round((title_start + 0.15) * 1000))
    parts.append(f"[9:a]adelay={st_ms}|{st_ms},volume=-2dB[st]")
    parts.append(f"[duck][vo][st]amix=inputs=3:normalize=0,"
                 f"volume={trim_db:.2f}dB,afade=t=in:st=0:d=0.8,"
                 f"afade=t=out:st={total - 1.2:.3f}:d=1.2,"
                 f"atrim=0:{total:.3f}[mix]")
    MIX_DIR.mkdir(parents=True, exist_ok=True)
    out = MIX_DIR / "PROLOGUE_mix_v1.wav"
    run(cmd + ["-filter_complex", ";".join(parts), "-map", "[mix]",
               "-c:a", "pcm_s16le", "-ar", "48000", str(out)])
    return out


def frame_diff(mp4: Path, t: float, png: Path,
               zoom: float = 1.0):
    """Identity metrics between the film frame at t and the
    keyframe, compensating the Ken Burns center-crop at the given
    zoom. Returns (full-res diff, structure diff at 160x90). The
    film path resamples twice (640->1280 upscale, zoompan, back to
    640), so the numbers carry a resampling floor. Checkpoint 27
    diagnostic (brute-force fit over zoom/offsets on S01, the most
    detailed panel): best fits land at zooms 1.015 / 1.035 / 1.055
    for t = 1.2 / 3.017 / 5.0 s -- exactly the designed values --
    with zero offset, and residual structure diffs of 4.2-6.5.
    Identity is therefore the correct panel under the intended
    transform; the gates below sit above that measured floor."""
    fr = TMP / f"chk_{int(t * 10)}.png"
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i",
         str(mp4), "-frames:v", "1", str(fr)])
    a_img = Image.open(fr).convert("RGB")
    img = Image.open(png).convert("RGB").resize((640, 360))
    if zoom > 1.001:
        w, h = img.size
        cw, ch = w / zoom, h / zoom
        img = img.crop(((w - cw) / 2, (h - ch) / 2,
                        (w + cw) / 2, (h + ch) / 2)).resize((640, 360))
    a = np.asarray(a_img, dtype=np.float32)
    b = np.asarray(img, dtype=np.float32)
    full = float(np.abs(a - b).mean())
    a_lo = np.asarray(a_img.resize((160, 90)), dtype=np.float32)
    b_lo = np.asarray(img.resize((160, 90)), dtype=np.float32)
    struct = float(np.abs(a_lo - b_lo).mean())
    return full, struct


def main() -> int:
    vo = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    kf_manifest = make_keyframes()
    finals, cues, total, title_start, lyan_start = build_timeline(vo)
    timing_path, srt_path = write_timing_srt(finals, cues, total)
    print(f"timeline: {len(finals)} shots, total {total:.3f} s, "
          f"title at {title_start:.2f} s, Ly An at {lyan_start:.2f} s")
    video = render_video(finals)
    mix = render_mix(cues, total, title_start, lyan_start)
    lufs, tp = loudnorm(mix)
    trim = 0.0
    for _ in range(2):
        if tp <= -1.0:
            break
        trim += (-1.0 - tp - 0.1)
        mix = render_mix(cues, total, title_start, lyan_start, trim)
        lufs, tp = loudnorm(mix)
    print(f"mix: {lufs:.2f} LUFS / {tp:.2f} dBTP (trim {trim:.2f} dB)")
    RT_DIR.mkdir(parents=True, exist_ok=True)
    mp4 = RT_DIR / "CIN_000_640x360_30fps.mp4"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i",
         str(mix), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
         "-shortest", str(mp4)])
    ogv = RT_DIR / "CIN_000_640x360_30fps.ogv"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4),
         "-c:v", "libtheora", "-q:v", "7", "-c:a", "libvorbis",
         "-q:a", "5", str(ogv)])
    poster = RT_DIR / "CIN_000_poster.png"
    shutil.copyfile(KF_DIR / "keyframe_CIN_000_S12.png", poster)
    for f in (timing_path, srt_path):
        shutil.copyfile(f, RT_DIR / f.name)
    # --- verification gates ---
    for path, tol in ((mp4, 0.05), (ogv, 0.15)):
        pr = probe(path)
        dur = float(pr["format"]["duration"])
        assert abs(dur - total) <= tol, (path, dur, total)
        kinds = [s["codec_type"] for s in pr["streams"]]
        assert "audio" in kinds and "video" in kinds, (path, kinds)
        vs = next(s for s in pr["streams"]
                  if s["codec_type"] == "video")
        assert (vs["width"], vs["height"]) == (640, 360), path
    identity = {}
    motion = {}
    for si, s, raw, fs, fe in finals:
        if s is None:
            continue
        mid = (fs + fe) / 2.0
        kf = KF_DIR / f"keyframe_{s[0]}.png"
        prog = 0.5
        zoom = 1.0 + 0.07 * prog if s[5] == "in" else \
            1.07 - 0.07 * prog
        d_full, d_struct = frame_diff(mp4, mid, kf, zoom)
        identity[s[0]] = {"fullRes": round(d_full, 3),
                          "structure160x90": round(d_struct, 3)}
        assert d_full < 20.0 and d_struct < 8.0, \
            (s[0], d_full, d_struct)
        f1 = TMP / f"mv_{s[0]}_a.png"
        f2 = TMP / f"mv_{s[0]}_b.png"
        for t, f in ((mid - 0.8, f1), (mid + 0.8, f2)):
            run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}",
                 "-i", str(mp4), "-frames:v", "1", str(f)])
        dm = float(np.abs(
            np.asarray(Image.open(f1).convert("RGB"), dtype=np.float32)
            - np.asarray(Image.open(f2).convert("RGB"),
                         dtype=np.float32)).mean())
        motion[s[0]] = round(dm, 3)
        assert dm > 0.4, (s[0], dm)
    print(f"identity: {identity}")
    print(f"motion: {motion}")
    # --- manifests ---
    def fentry(p: Path, rel: str) -> dict:
        # durationSeconds records the FIRST STREAM's duration (the
        # video stream), the quantity verify_runtime_delivery
        # measures. The xfade chain's non-frame-aligned offsets
        # cost 3 frames (2618 of 2621 designed), so the video
        # stream (87.2667 s) is 0.1 s shorter than the format /
        # audio duration (87.3667 s); the difference sits inside
        # the final fade-out and is recorded, not hidden.
        pr = probe(p)
        dur = pr["streams"][0].get("duration") or \
            pr["format"]["duration"]
        return {"path": rel, "sha256": sha256_file(p),
                "sizeBytes": p.stat().st_size,
                "durationSeconds": round(float(dur), 4)}

    mix_manifest = {
        "manifestId": "NGM_PROLOGUE_MIX_V1",
        "checkpoint": "MEDIA-02 checkpoint 27",
        "file": "PROLOGUE_mix_v1.wav",
        "sha256": sha256_file(mix),
        "sizeBytes": mix.stat().st_size,
        "durationSeconds": round(total, 4),
        "integratedLufs": round(lufs, 2), "truePeakDbtp": round(tp, 2),
        "assetState": "DRAFT_MIX_NOT_FINAL",
        "stems": [
            {"role": "narration", "source": "PROLOGUE_VO_manifest_v1"
             ".json (checkpoint 27 draft TTS)",
             "provenance": "NEW_DRAFT_VO"},
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
        "notes": ["DRAFT_MIX_NOT_FINAL: formula gain staging, no ear "
                  "audition; narration pronunciation not yet "
                  "reviewed by a native listener."],
    }
    (MIX_DIR / "PROLOGUE_mix_manifest_v1.json").write_text(
        json.dumps(mix_manifest, ensure_ascii=False, indent=1) + "\n",
        encoding="utf-8")
    export_manifest = {
        "sceneId": "CIN_000",
        "title": "Trước khi tới Bến Mưa",
        "checkpoint": "MEDIA-02 checkpoint 27",
        "videoStatus": "VIDEO_PROLOGUE_FILM_WITH_MIXED_AUDIO",
        "hasAudioTrack": True,
        "durationSeconds": round(total, 4),
        "mp4": fentry(mp4, "ClientGodot/assets/cinematics/CIN_000/"
                           "CIN_000_640x360_30fps.mp4"),
        "ogv": fentry(ogv, "ClientGodot/assets/cinematics/CIN_000/"
                           "CIN_000_640x360_30fps.ogv"),
        "poster": {"path": "ClientGodot/assets/cinematics/CIN_000/"
                           "CIN_000_poster.png",
                   "sha256": sha256_file(poster),
                   "sizeBytes": poster.stat().st_size,
                   "rule": "poster is the title-card keyframe "
                           "(CIN_000_S12), a documented choice for "
                           "this standalone film"},
        "timingFile": "CIN_000_timing_v1.json",
        "timingSha256": sha256_file(timing_path),
        "srtFile": "CIN_000_vi.srt",
        "srtSha256": sha256_file(srt_path),
        "identityDiffs": identity, "motionDiffs": motion,
        "notes": ["Standalone pre-game prologue; NOT part of the "
                  "20-scene campaign pack or its totals.",
                  "Picture is cinematic panels with Ken Burns "
                  "motion; character/spoiler guardrails per the "
                  "timing JSON staging note."],
    }
    (RT_DIR / "scene_export_manifest_v1.json").write_text(
        json.dumps(export_manifest, ensure_ascii=False, indent=1)
        + "\n", encoding="utf-8")
    film_manifest = {
        "manifestId": "NGM_CIN000_FILM_V1",
        "sceneId": "CIN_000",
        "title": "Trước khi tới Bến Mưa",
        "checkpoint": "MEDIA-02 checkpoint 27",
        "scriptApproval": "Owner approved the narration script in "
                          "main chat 2026-11-06",
        "durationSeconds": round(total, 4),
        "keyframesManifest": "CIN000_keyframes_manifest_v1.json",
        "keyframesManifestSha256": sha256_file(
            PRO_DIR / "CIN000_keyframes_manifest_v1.json"),
        "timingFile": "Implementation/Content/Narrative/Deliveries/"
                      "CIN_000/CIN_000_timing_v1.json",
        "timingSha256": sha256_file(timing_path),
        "srtSha256": sha256_file(srt_path),
        "voManifest": "Art_Source/Audio/Muse/VO/"
                      "PROLOGUE_VO_manifest_v1.json",
        "mixManifest": "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/"
                       "PROLOGUE_mix_manifest_v1.json",
        "mixSha256": sha256_file(mix),
        "exports": export_manifest,
    }
    (PRO_DIR / "CIN000_film_manifest_v1.json").write_text(
        json.dumps(film_manifest, ensure_ascii=False, indent=1)
        + "\n", encoding="utf-8")
    print(f"\nprologue film built: {total:.2f} s, MP4 "
          f"{export_manifest['mp4']['sha256'][:8]}, OGV "
          f"{export_manifest['ogv']['sha256'][:8]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
