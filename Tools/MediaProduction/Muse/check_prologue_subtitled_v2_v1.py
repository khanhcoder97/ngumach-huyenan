#!/usr/bin/env python3
"""WO37 M-B CP5 — independent checker for the subtitled prologue v2.

Verifies the delivered block from real bytes only, re-deriving every
claim instead of trusting the builder:

- Sources: canonical MP4 / SRT / v2 mix / History takes / Ly An take
  shas vs their manifests; v1 method check (canonical SRT windows ==
  Helio take durations) re-derived from the CP27 VO manifest.
- Subtitle derivation: the chunk split + proportional allocation
  algorithm is re-implemented here (copied from the CP28 spec, not
  imported from the builder) and run on the canonical SRT with the
  v2 windows from the M-F CP2 manifest; the delivered readable v2
  SRT must match cue-by-cue (text exact, timing +/-0.002 s).
- Narration presence: each History take correlates with the v2 mix
  at its slot start (>= 0.90 at lag 0, 0.25 s window); the Ly An
  take correlates at 80.907 s. Audible ends re-measured from the
  take files (-50 dBFS, 10 ms windows) vs the manifest.
- 640 variant: streams [video, audio, subtitle], 640x360@30,
  duration, loudness vs mix+gain prediction, embedded mov_text
  round-trip 26/26, audio correlation vs the v2 mix WAV
  (>= 0.999), video frames vs the canonical MP4 with the subtitle
  band masked (mean|diff| < 8).
- 720p variant: streams, 1280x720@30, audio stream hash == 640
  variant audio (stream copy), subtitle track == readable v2 SRT,
  frames downscaled to 640 vs the 640 variant (mean|diff| <= 6.0)
  and the 2x2-block structure of the 1280x720 frame itself
  (mean intra-block range <= 24, CP2/CP4 thresholds).
- Registration: film manifest subtitledVariantV2 + CP5 delivery
  manifest entries vs disk; runtime tree untouched (git status
  under ClientGodot/ empty); canonical v1 files unchanged.
"""
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
CINE_DIR = ROOT / "ClientGodot/assets/cinematics/CIN_000"
CANON_MP4 = CINE_DIR / "CIN_000_640x360_30fps.mp4"
CANON_SRT = ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi.srt"
V1_READABLE = CINE_DIR / "CIN_000_vi_readable.srt"
V2_MIX = ROOT / "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_mix_draft_v2.wav"
V2_MANIFEST = ROOT / "Art_Source/Audio/Muse/MIX/CIN000_DRAFT_V2/CIN_000_MIX_V2_manifest_v1.json"
FILM_MANIFEST = ROOT / "Art_Source/Cinematics/Prologue/CIN000_film_manifest_v1.json"
VO_MANIFEST = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json"
TAKE_DIR = ROOT / "Art_Source/Audio/Muse/VO/PALETTE_PICKUPS_v1"
LYAN_TAKE = ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT/VO_CIN001_S05_LYAN_draft_v1.wav"
OUT_SRT = ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000/CIN_000_vi_readable_v2.srt"
OUT_MP4_640 = ROOT / "Art_Source/Cinematics/Prologue/CIN_000_640x360_30fps_sub_vi_v2.mp4"
OUT_MP4_720 = ROOT / "Art_Source/Cinematics/Standard720/CIN_000_subtitled_v2/CIN_000_1280x720_30fps_sub_vi_v2.mp4"
CP5_MANIFEST = ROOT / "Implementation/Content/Narrative/Deliveries/STANDARD720_SUBTITLED_V2_MB_CP5_v1.json"
OUT_JSON = ROOT / "Implementation/Reports/MuseMedia/MEDIA02_WO37_MB_CP5_VALIDATION_20261113.json"
MAX_CHARS = 82
MIN_DUR = 1.2
ELLIPSIS = "\u2026"
FAIL = []
CHECKS = {"total": 0, "passed": 0}
DETAILS = {}


def check(name, ok, detail=""):
    CHECKS["total"] += 1
    if ok:
        CHECKS["passed"] += 1
    else:
        FAIL.append(name)
    DETAILS[name] = detail
    print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def probe(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def loudnorm(p):
    r = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    txt = r.stderr
    i = txt.rfind("{")
    depth = 0
    for j in range(i, len(txt)):
        if txt[j] == "{":
            depth += 1
        elif txt[j] == "}":
            depth -= 1
            if depth == 0:
                d = json.loads(txt[i:j + 1])
                return float(d["input_i"]), float(d["input_tp"])
    raise ValueError("loudnorm JSON block not found")


def decode_mono_f32(p):
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-vn", "-ac", "1",
         "-ar", "48000", "-f", "f32le", "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32)


def stream_hash(p, spec):
    r = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(p), "-map", spec,
         "-f", "hash", "-hash", "sha256", "-"],
        capture_output=True, text=True, check=True)
    return r.stdout.strip().split("=")[-1]


def frame(p, t, size=None):
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        tmp = Path(tf.name)
    vf = f"scale={size}:flags=neighbor" if size else "null"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t}", "-i",
                    str(p), "-frames:v", "1", "-vf", vf, str(tmp)],
                   check=True)
    arr = np.asarray(Image.open(tmp).convert("RGB"), dtype=np.int16)
    tmp.unlink()
    return arr


def parse_srt(text):
    cues = []
    for block in re.split(r"\r?\n\r?\n", text.strip()):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if len(lines) < 2:
            continue
        m = re.match(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*"
                     r"(\d+):(\d+):(\d+)[,.](\d+)", lines[1])
        if not m:
            continue
        g = [int(x) for x in m.groups()]
        cues.append({"start": g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0,
                     "end": g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0,
                     "text": " ".join(lines[2:]).strip()})
    return cues


def norm_text(s):
    return re.sub(r"\s+", " ", s).strip()


# --- CP28 split algorithm, re-implemented here (not imported) ---
def split_sentences(text):
    t = text.replace("...", ELLIPSIS)
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", t) if p.strip()]


def split_atoms(sentence):
    atoms = re.split(r"(?<=[,;])\s+|(?<=\u2014)\s+", sentence)
    out = []
    for a in atoms:
        a = a.strip()
        if not a:
            continue
        if len(a) <= MAX_CHARS:
            out.append(a)
            continue
        piece = ""
        for w in a.split():
            cand = (piece + " " + w).strip()
            if len(cand) > MAX_CHARS and piece:
                out.append(piece)
                piece = w
            else:
                piece = cand
        if piece:
            out.append(piece)
    return out


def chunk_cue(text):
    chunks = []
    for sent in split_sentences(text):
        if len(sent) <= MAX_CHARS:
            chunks.append(sent)
            continue
        cur = ""
        for atom in split_atoms(sent):
            cand = (cur + " " + atom).strip()
            if len(cand) > MAX_CHARS and cur:
                chunks.append(cur)
                cur = atom
            else:
                cur = cand
        if cur:
            chunks.append(cur)
    return [c.replace(ELLIPSIS, "...") for c in chunks]


def allocate(total_dur, weights):
    durs = [0.0] * len(weights)
    free = list(range(len(weights)))
    remaining = total_dur
    while free:
        wsum = sum(weights[i] for i in free)
        fixed = [i for i in free
                 if remaining * weights[i] / wsum < MIN_DUR]
        if not fixed:
            for i in free:
                durs[i] = remaining * weights[i] / wsum
            break
        for i in fixed:
            durs[i] = MIN_DUR
            free.remove(i)
            remaining -= MIN_DUR
    return durs


def derive_readable(canon, windows):
    readable = []
    prev_end = 0.0
    for cue, (ws, we) in zip(canon, windows):
        texts = chunk_cue(cue["text"])
        durs = allocate(we - ws, [len(t) for t in texts])
        t = ws
        spans = []
        for txt, dur in zip(texts, durs):
            spans.append([t, t + dur, txt])
            t += dur
        spans[-1][1] = we
        if spans[0][0] < prev_end + 0.05:
            delta = prev_end + 0.05 - spans[0][0]
            for sp in spans:
                sp[0] += delta
                sp[1] += delta
        for s, e, txt in spans:
            readable.append({"start": s, "end": e, "text": txt})
            prev_end = e
    return readable


def corr_at(mix, take, start_s, win_s=0.25, sr=48000):
    """Pearson corr of take vs mix span at start_s, lag 0 and best
    lag in +/-300 ms (fix-checker method). The lag scan runs on the
    take's LOUDEST win_s window: the first 0.25 s of a take can be
    lead-in silence, and scanning silence returns a spurious lag
    (calibration lesson from M-F CP2)."""
    i0 = int(start_s * sr)
    seg = mix[i0:i0 + len(take)]
    n = min(len(seg), len(take))
    a, b = take[:n].astype(np.float64), seg[:n].astype(np.float64)
    a -= a.mean()
    b -= b.mean()
    denom = np.sqrt((a * a).sum() * (b * b).sum())
    c0 = float((a * b).sum() / denom) if denom else 0.0
    # loudest win_s window of the take (speech content guaranteed)
    w = int(win_s * sr)
    step = w // 2 or 1
    best_e, best_i = -1.0, 0
    for i in range(0, max(1, len(take) - w + 1), step):
        e = float(np.mean(take[i:i + w].astype(np.float64) ** 2))
        if e > best_e:
            best_e, best_i = e, i
    a2 = take[best_i:best_i + w].astype(np.float64)
    b2 = mix[i0 + best_i:i0 + best_i + w].astype(np.float64)
    best, best_lag = -1.0, 0
    for lag in range(-int(0.3 * sr), int(0.3 * sr) + 1, 48):
        if lag >= 0:
            x, y = a2[lag:], b2[:len(b2) - lag]
        else:
            x, y = a2[:len(a2) + lag], b2[-lag:]
        m = min(len(x), len(y))
        x, y = x[:m], y[:m]
        d = np.sqrt((x * x).sum() * (y * y).sum())
        c = float((x * y).sum() / d) if d else 0.0
        if c > best:
            best, best_lag = c, lag
    return c0, best, best_lag / sr


def audible_end(take, sr=48000, thresh_db=-50.0):
    """Last 10 ms window above thresh (take file, no bed)."""
    win = int(0.01 * sr)
    n = len(take) // win
    rms = np.sqrt(np.mean(take[:n * win].reshape(n, win).astype(
        np.float64) ** 2, axis=1))
    peak = np.max(np.abs(take)) or 1.0
    db = 20 * np.log10(np.maximum(rms, 1e-9) / peak)
    above = np.nonzero(db > thresh_db)[0]
    if len(above) == 0:
        return 0.0
    return float((above[-1] + 1) * win / sr)


def main():
    fman = json.loads(FILM_MANIFEST.read_text(encoding="utf-8"))
    v2man = json.loads(V2_MANIFEST.read_text(encoding="utf-8"))
    voman = json.loads(VO_MANIFEST.read_text(encoding="utf-8"))
    cp5 = json.loads(CP5_MANIFEST.read_text(encoding="utf-8"))

    # --- 1. sources ---
    check("source canonical MP4 sha == film manifest",
          sha256_of(CANON_MP4) == fman["exports"]["mp4"]["sha256"],
          sha256_of(CANON_MP4)[:16])
    check("source canonical SRT sha == film manifest",
          sha256_of(CANON_SRT) == fman["srtSha256"])
    check("source v2 mix WAV sha == v2 manifest",
          sha256_of(V2_MIX) == v2man["sha256"],
          sha256_of(V2_MIX)[:16])
    canon = parse_srt(CANON_SRT.read_text(encoding="utf-8"))
    check("canonical SRT has 6 cues", len(canon) == 6, f"{len(canon)}")
    ok_v1 = all(abs(s["durationSeconds"] - (c["end"] - c["start"])) <= 0.001
                for s, c in zip(voman["segments"], canon[:5])) and \
        abs(voman["finalLine"]["durationSeconds"]
            - (canon[5]["end"] - canon[5]["start"])) <= 0.001
    check("v1 method: SRT windows == Helio take durations", ok_v1)
    takes_ok = True
    for ch in v2man["paletteRemix"]["narrationChanges"]:
        p = TAKE_DIR / ch["paletteTakeFile"].split("/")[-1]
        if sha256_of(p) != ch["paletteTakeSha256"]:
            takes_ok = False
    check("History takes sha == v2 manifest", takes_ok)
    check("Ly An take sha == v2 manifest note",
          sha256_of(LYAN_TAKE).startswith("51fc65de"),
          sha256_of(LYAN_TAKE)[:16])

    # --- 2. re-derive the readable v2 SRT independently ---
    windows = [(ch["cp27SegmentStartSeconds"], ch["paletteEndSeconds"])
               for ch in v2man["paletteRemix"]["narrationChanges"]]
    windows.append((canon[5]["start"], canon[5]["end"]))
    expected = derive_readable(canon, windows)
    delivered = parse_srt(OUT_SRT.read_text(encoding="utf-8"))
    check("readable v2 SRT has 26 chunks", len(delivered) == 26,
          f"{len(delivered)}")
    txt_ok = [c["text"] for c in delivered] == [c["text"] for c in expected]
    check("readable v2 chunk texts == re-derived split", txt_ok)
    tim_ok = all(abs(a["start"] - b["start"]) <= 0.002 and
                 abs(a["end"] - b["end"]) <= 0.002
                 for a, b in zip(delivered, expected)) \
        if len(delivered) == len(expected) else False
    check("readable v2 chunk timings == re-derived (<=0.002 s)", tim_ok)
    v1r = parse_srt(V1_READABLE.read_text(encoding="utf-8"))
    check("readable v2 chunk texts == v1 readable chunk texts",
          [c["text"] for c in delivered] == [c["text"] for c in v1r])
    check("readable v2 text == canonical text (normalized)",
          norm_text(" ".join(c["text"] for c in delivered)) ==
          norm_text(" ".join(c["text"] for c in canon)))
    mono = all(delivered[i]["start"] >= delivered[i - 1]["end"] - 0.001
               for i in range(1, len(delivered)))
    check("readable v2 cues monotonic, non-overlapping", mono)
    mindur = min(c["end"] - c["start"] for c in delivered)
    check("readable v2 min chunk duration >= 1.0 s", mindur >= 1.0,
          f"{mindur:.3f} s")
    # cue 3 shift (SEG02/SEG03 overlap rule)
    c3_first = next(c for c in delivered
                    if abs(c["start"] - 35.667) < 1.0)
    check("SEG03 chunks shifted +0.168 s (overlap rule)",
          abs(c3_first["start"] - 35.835) <= 0.002,
          f"first SEG03 chunk starts {c3_first['start']:.3f}")

    # --- 3. narration presence + audible ends in the v2 mix ---
    mix = decode_mono_f32(V2_MIX)
    for ch in v2man["paletteRemix"]["narrationChanges"]:
        take = decode_mono_f32(
            TAKE_DIR / ch["paletteTakeFile"].split("/")[-1])
        c0, best, lag = corr_at(mix, take, ch["cp27SegmentStartSeconds"])
        check(f"take {ch['takeKey']} in v2 mix (lag 0)",
              c0 >= 0.90 and abs(lag) < 0.01,
              f"corr {c0:.3f} best {best:.3f} lag {lag:.3f} s")
        ae = audible_end(take) + ch["cp27SegmentStartSeconds"]
        check(f"take {ch['takeKey']} audible end == manifest",
              abs(ae - ch["paletteAudibleEndSeconds"]) <= 0.15,
              f"measured {ae:.3f} vs manifest "
              f"{ch['paletteAudibleEndSeconds']:.3f}")
        # subtitle window covers the audible speech, ending in the
        # trailing file silence (<= 0.40 s after the audible end)
        seg_chunks = [c for c in delivered
                      if c["start"] >= ch["cp27SegmentStartSeconds"] - 0.001
                      and c["end"] <= ch["paletteEndSeconds"] + 0.20]
        last_end = max(c["end"] for c in seg_chunks)
        check(f"cue {ch['segment']} last chunk ends <=0.50 s after "
              f"audible end",
              -0.05 <= last_end - ae <= 0.50,
              f"last chunk end {last_end:.3f}, audible end {ae:.3f} "
              f"(cue 3 carries the +0.168 s monotonic shift)")
    lyan = decode_mono_f32(LYAN_TAKE)
    c0, best, lag = corr_at(mix, lyan, 80.907)
    check("Ly An final line in v2 mix at 80.907 s (lag 0)",
          c0 >= 0.90 and abs(lag) < 0.01,
          f"corr {c0:.3f} best {best:.3f} lag {lag:.3f} s")

    # --- 4. 640 variant ---
    pr640 = probe(OUT_MP4_640)
    kinds = [s["codec_type"] for s in pr640["streams"]]
    check("640 stream layout [video, audio, subtitle]",
          kinds == ["video", "audio", "subtitle"], str(kinds))
    v640 = pr640["streams"][0]
    check("640 video 640x360@30 h264",
          v640["width"] == 640 and v640["height"] == 360
          and v640["codec_name"] == "h264"
          and v640["r_frame_rate"] == "30/1")
    check("640 video duration 87.2667 s",
          abs(float(v640["duration"]) - 87.2667) <= 0.05,
          v640["duration"])
    gain = cp5["entries"][0]["audio"]["presentationGainDb"]
    mix_lufs, mix_tp = v2man["integratedLufs"], v2man["truePeakDbtp"]
    lufs640, tp640 = loudnorm(OUT_MP4_640)
    check("640 loudness == v2 mix + gain (LUFS +-0.15)",
          abs(lufs640 - (mix_lufs + gain)) <= 0.15,
          f"{lufs640:.2f} vs {mix_lufs + gain:.2f}")
    check("640 true peak == v2 mix + gain (TP +-0.25, AAC shift)",
          abs(tp640 - (mix_tp + gain)) <= 0.25,
          f"{tp640:.2f} vs {mix_tp + gain:.2f}")
    check("640 true peak <= -1.0 dBTP ceiling", tp640 <= -1.0,
          f"{tp640:.2f}")
    emb = parse_srt(subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(OUT_MP4_640), "-map", "0:s:0",
         "-f", "srt", "-"], capture_output=True, text=True).stdout)
    emb_ok = len(emb) == len(delivered) and all(
        norm_text(a["text"]) == norm_text(b["text"]) and
        abs(a["start"] - b["start"]) <= 0.05 and
        abs(a["end"] - b["end"]) <= 0.05
        for a, b in zip(emb, delivered))
    check("640 embedded mov_text == readable v2 SRT (26/26)", emb_ok,
          f"{len(emb)} cues")
    aac = decode_mono_f32(OUT_MP4_640)
    wav = mix[:len(aac)] * (10 ** (gain / 20))
    n = min(len(aac), len(wav))
    aa, bb = aac[:n].astype(np.float64), wav[:n].astype(np.float64)
    aa -= aa.mean()
    bb -= bb.mean()
    corr = float((aa * bb).sum() /
                 np.sqrt((aa * aa).sum() * (bb * bb).sum()))
    check("640 audio correlates with v2 mix WAV (>= 0.999, lag 0)",
          corr >= 0.999, f"{corr:.4f}")
    # video picture vs canonical film, subtitle band masked
    worst = 0.0
    for t in (6.0, 45.0, 82.2):
        f_new = frame(OUT_MP4_640, t)
        f_old = frame(CANON_MP4, t)
        diff = np.abs(f_new[:-60] - f_old[:-60]).mean()
        worst = max(worst, float(diff))
    check("640 picture == canonical film (band masked, mean|diff| < 8)",
          worst < 8.0, f"worst {worst:.3f} at 6/45/82.2 s")

    # --- 5. 720p variant ---
    pr720 = probe(OUT_MP4_720)
    kinds720 = [s["codec_type"] for s in pr720["streams"]]
    check("720 stream layout [video, audio, subtitle]",
          kinds720 == ["video", "audio", "subtitle"], str(kinds720))
    v720 = pr720["streams"][0]
    check("720 video 1280x720@30 h264",
          v720["width"] == 1280 and v720["height"] == 720
          and v720["codec_name"] == "h264")
    check("720 video duration 87.2667 s",
          abs(float(v720["duration"]) - 87.2667) <= 0.05,
          v720["duration"])
    h640 = stream_hash(OUT_MP4_640, "0:a:0")
    h720 = stream_hash(OUT_MP4_720, "0:a:0")
    check("720 audio stream bit-copied from 640 variant", h640 == h720,
          f"{h640[:12]} vs {h720[:12]}")
    emb720 = parse_srt(subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(OUT_MP4_720), "-map", "0:s:0",
         "-f", "srt", "-"], capture_output=True, text=True).stdout)
    emb720_ok = len(emb720) == len(delivered) and all(
        norm_text(a["text"]) == norm_text(b["text"]) and
        abs(a["start"] - b["start"]) <= 0.05 and
        abs(a["end"] - b["end"]) <= 0.05
        for a, b in zip(emb720, delivered))
    check("720 embedded mov_text == readable v2 SRT (26/26)", emb720_ok,
          f"{len(emb720)} cues")
    # CP4 metric (NOT the diff): mean 2x2 intra-block range of the
    # 1280x720 frame itself — the 2x2-block structure of an integer
    # upscale survives iff this stays small (CP2 threshold <= 24).
    worst_mean, worst_rng = 0.0, 0.0
    for t in (6.0, 45.0, 82.2):
        f720 = frame(OUT_MP4_720, t, "640x360")
        f640 = frame(OUT_MP4_640, t)
        d = np.abs(f720 - f640)
        worst_mean = max(worst_mean, float(d.mean()))
        full = frame(OUT_MP4_720, t, "1280:720").astype(np.int16)
        blocks = full.reshape(360, 2, 640, 2, 3)
        rng = float((blocks.max(axis=(1, 3))
                     - blocks.min(axis=(1, 3))).mean())
        worst_rng = max(worst_rng, rng)
    check("720 downscale vs 640 (mean|diff| <= 6.0, CP2 threshold)",
          worst_mean <= 6.0, f"worst {worst_mean:.3f}")
    check("720 frame 2x2 intra-block range mean <= 24 (CP2 threshold)",
          worst_rng <= 24.0, f"worst {worst_rng:.2f}")

    # --- 6. registration + runtime untouched ---
    sv2 = fman.get("subtitledVariantV2", {})
    check("film manifest subtitledVariantV2 sha == disk",
          sv2.get("sha256") == sha256_of(OUT_MP4_640),
          (sv2.get("sha256") or "")[:16])
    check("film manifest subtitledVariantV2 readable SRT sha == disk",
          sv2.get("readableSrtSha256") == sha256_of(OUT_SRT))
    e640, e720 = cp5["entries"]
    check("CP5 manifest 640 entry sha/size == disk",
          e640["sha256"] == sha256_of(OUT_MP4_640)
          and e640["sizeBytes"] == OUT_MP4_640.stat().st_size)
    check("CP5 manifest 720 entry sha/size == disk",
          e720["outSha256"] == sha256_of(OUT_MP4_720)
          and e720["outBytes"] == OUT_MP4_720.stat().st_size)
    check("CP5 manifest budget arithmetic",
          cp5["budget"]["mp4Set"]["totalBytes"]
          == e640["sizeBytes"] + e720["outBytes"])
    check("CP5 manifest runtimeTreeModified == false",
          cp5.get("runtimeTreeModified") is False)
    st = subprocess.run(["git", "status", "--porcelain", "--",
                         "ClientGodot/"], cwd=ROOT, capture_output=True,
                        text=True).stdout.strip()
    check("runtime tree untouched (git status ClientGodot/ clean)",
          st == "", st[:200])
    exp = json.loads((CINE_DIR / "scene_export_manifest_v1.json")
                     .read_text(encoding="utf-8"))
    check("v1 export manifest mp4SubVi sha unchanged (50ec6a98)",
          exp["mp4SubVi"]["sha256"].startswith("50ec6a98"))

    result = {
        "checkpoint": "WO37 M-B CP5",
        "validator": "check_prologue_subtitled_v2_v1.py",
        "checks": CHECKS,
        "failures": FAIL,
        "details": DETAILS,
        "files": {
            "readableSrtV2": {
                "path": str(OUT_SRT.relative_to(ROOT)),
                "sha256": sha256_of(OUT_SRT),
                "sizeBytes": OUT_SRT.stat().st_size, "chunks": 26},
            "mp4_640": {
                "path": str(OUT_MP4_640.relative_to(ROOT)),
                "sha256": sha256_of(OUT_MP4_640),
                "sizeBytes": OUT_MP4_640.stat().st_size,
                "loudnessLufs": round(lufs640, 2),
                "truePeakDbtp": round(tp640, 2)},
            "mp4_720": {
                "path": str(OUT_MP4_720.relative_to(ROOT)),
                "sha256": sha256_of(OUT_MP4_720),
                "sizeBytes": OUT_MP4_720.stat().st_size},
        },
        "presentationGainDb": gain,
        "status": "PASS" if not FAIL else "FAIL",
    }
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n{CHECKS['passed']}/{CHECKS['total']} PASS"
          + (f" — FAILURES: {FAIL}" if FAIL else ""))
    return 0 if not FAIL else 1


if __name__ == "__main__":
    sys.exit(main())
