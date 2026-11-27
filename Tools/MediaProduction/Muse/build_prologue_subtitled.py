#!/usr/bin/env python3
"""Checkpoint 28: subtitled viewing variant of the prologue film
CIN_000 "Truoc khi toi Ben Mua" (owner request 2026-11-06: the
delivered film had its narration embedded but no on-screen subtitles,
and the voice sat low for casual playback).

What this tool does, from real bytes only:

1. Reads the canonical runtime MP4 (checkpoint 27, embedded draft
   mix) and the canonical SRT (6 long cues, UTF-8/NFC). The canonical
   MP4 / OGV / SRT are NOT modified.
2. Derives a READABLE subtitle file `CIN_000_vi_readable.srt`: each
   canonical cue is split into sentences, then into clause chunks of
   at most 82 characters, timed proportionally to character count
   inside the canonical cue window. Chunk text concatenated (white-
   space normalized) is IDENTICAL to the canonical cue text -- this
   is a presentation split, not an edit. Chunk sequences are kept
   monotonic and non-overlapping across cue boundaries.
3. Renders `CIN_000_640x360_30fps_sub_vi.mp4`:
   - video: readable subtitles BURNED IN via libass (DejaVu Sans,
     white bold on a semi-transparent black box, bottom center), so
     the text shows in every player, including chat previews;
   - audio: the checkpoint 27 mix copied through a +5.0 dB
     presentation gain (no dynamics change; canonical mix file and
     canonical MP4 audio untouched) so the narration is clearly
     audible on laptop/phone speakers;
   - an embedded mov_text subtitle track (vie, default) carrying
     the same readable cues for players that prefer soft subs.
4. Measures the result from real bytes (sha256, size, ffprobe
   streams/durations, loudnorm of the audio, extraction of the
   embedded subtitle stream compared against the readable SRT) and
   registers the variant in the scene export manifest (+ a pointer
   in the film manifest). build_runtime_delivery.py then carries it
   into the runtime cinematics manifest's 'prologue' key.
"""
import hashlib
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CINE_DIR = ROOT / "ClientGodot/assets/cinematics/CIN_000"
CANON_MP4 = CINE_DIR / "CIN_000_640x360_30fps.mp4"
CANON_SRT = CINE_DIR / "CIN_000_vi.srt"
SRC_SRT = (ROOT / "Implementation/Content/Narrative/Deliveries"
           / "CIN_000/CIN_000_vi.srt")
READABLE_SRT = CINE_DIR / "CIN_000_vi_readable.srt"
OUT_MP4 = CINE_DIR / "CIN_000_640x360_30fps_sub_vi.mp4"
EXPORT_MANIFEST = CINE_DIR / "scene_export_manifest_v1.json"
FILM_MANIFEST = (ROOT / "Art_Source/Cinematics/Prologue"
                 / "CIN000_film_manifest_v1.json")
MAX_CHARS = 82
GAIN_DB = 5.0
ELLIPSIS = "\u2026"


def sha256_of(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


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
        start = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000.0
        end = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000.0
        cues.append({"start": start, "end": end,
                     "text": " ".join(lines[2:]).strip()})
    return cues


def fmt_ts(sec):
    ms = int(round(sec * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_sentences(text):
    t = text.replace("...", ELLIPSIS)
    parts = re.split(r"(?<=[.!?])\s+", t)
    return [p.strip() for p in parts if p.strip()]


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
    """Split one canonical cue text into readable chunks (<=MAX_CHARS),
    never merging across sentence boundaries."""
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


MIN_DUR = 1.2


def allocate(total_dur, weights):
    """Proportional durations with a MIN_DUR floor, redistributed
    inside the cue (water-filling): very short sentences (e.g.
    'Thi nghiem vo.') still get a readable minimum display time,
    taken from the cue's longest chunks; the cue window is fixed."""
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


def build_readable_cues(canon):
    readable = []
    prev_end = 0.0
    for cue in canon:
        texts = chunk_cue(cue["text"])
        durs = allocate(cue["end"] - cue["start"],
                        [len(t) for t in texts])
        t = cue["start"]
        spans = []
        for txt, dur in zip(texts, durs):
            spans.append([t, t + dur, txt])
            t += dur
        spans[-1][1] = cue["end"]
        # keep the whole film monotonic: the canonical SRT has one
        # small overlap (cue 3 end 55.419 vs cue 4 start 55.133);
        # shift this cue's chunks forward if needed (gaps between
        # narration segments leave room; verified by the assert).
        if spans[0][0] < prev_end + 0.05:
            delta = prev_end + 0.05 - spans[0][0]
            for sp in spans:
                sp[0] += delta
                sp[1] += delta
        for s, e, txt in spans:
            assert e - s >= 1.0, f"chunk too short: {txt[:30]}"
            readable.append({"start": s, "end": e, "text": txt})
            prev_end = e
    return readable


def norm_text(s):
    return re.sub(r"\s+", " ", s).strip()


def probe(p):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", str(p)], capture_output=True, text=True)
    return json.loads(out.stdout)


def loudnorm(p):
    out = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(p), "-map", "0:a:0",
         "-af", "loudnorm=print_format=json", "-f", "null", "-"],
        capture_output=True, text=True)
    m = re.search(r"\{\s*\"input_i\".*?\}", out.stderr, re.S)
    d = json.loads(m.group(0))
    return float(d["input_i"]), float(d["input_tp"])


def main():
    exp = json.loads(EXPORT_MANIFEST.read_text(encoding="utf-8"))
    if sha256_of(CANON_MP4) != exp["mp4"]["sha256"]:
        sys.exit("canonical MP4 sha drift vs export manifest")
    if sha256_of(CANON_SRT) != exp["srtSha256"]:
        sys.exit("canonical runtime SRT sha drift vs export manifest")
    if sha256_of(SRC_SRT) != sha256_of(CANON_SRT):
        sys.exit("runtime SRT != Deliveries source SRT")
    canon = parse_srt(CANON_SRT.read_text(encoding="utf-8"))
    if len(canon) != 6:
        sys.exit(f"canonical SRT cues {len(canon)} != 6")

    readable = build_readable_cues(canon)
    joined_new = norm_text(" ".join(c["text"] for c in readable))
    joined_old = norm_text(" ".join(c["text"] for c in canon))
    if joined_new != joined_old:
        sys.exit("readable split changed the text (must be identical)")
    srt_text = ""
    for i, c in enumerate(readable, 1):
        srt_text += (f"{i}\n{fmt_ts(c['start'])} --> "
                     f"{fmt_ts(c['end'])}\n{c['text']}\n\n")
    srt_text = unicodedata.normalize("NFC", srt_text)
    READABLE_SRT.write_text(srt_text, encoding="utf-8")
    print(f"readable SRT: {len(readable)} chunks from 6 canonical cues")

    style = ("FontName=DejaVu Sans,FontSize=16,Bold=1,"
             "PrimaryColour=&HFFFFFF,OutlineColour=&H000000,"
             "BorderStyle=3,BackColour=&HA0000000,Outline=1,Shadow=0,"
             "Alignment=2,MarginV=14,MarginL=20,MarginR=20")
    fc = (f"[0:v]subtitles='{READABLE_SRT}':force_style='{style}'[v];"
          f"[0:a]volume={GAIN_DB}dB[a]")
    cmd = ["ffmpeg", "-y", "-i", str(CANON_MP4), "-i",
           str(READABLE_SRT), "-filter_complex", fc,
           "-map", "[v]", "-map", "[a]", "-map", "1:0",
           "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-r", "30",
           "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-c:s", "mov_text", "-metadata:s:s:0", "language=vie",
           "-metadata:s:s:0", "title=Tieng Viet (phu de)",
           "-disposition:s:0", "default",
           "-metadata:s:a:0", "language=vie",
           "-movflags", "+faststart", str(OUT_MP4)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit("ffmpeg render failed:\n" + r.stderr[-3000:])

    pr = probe(OUT_MP4)
    kinds = [(s["codec_type"], s["codec_name"]) for s in pr["streams"]]
    if [k[0] for k in kinds] != ["video", "audio", "subtitle"]:
        sys.exit(f"unexpected stream layout: {kinds}")
    dur = float(pr["streams"][0]["duration"])
    lufs, tp = loudnorm(OUT_MP4)
    print(f"variant: streams={kinds} dur={dur:.4f} "
          f"loudness={lufs} LUFS tp={tp} dBTP")
    if not (-17.0 <= lufs <= -14.5 and tp <= -3.0):
        sys.exit("variant loudness outside the expected +5 dB window")

    # embedded subtitle stream must carry the readable cues verbatim
    out = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(OUT_MP4), "-map", "0:s:0",
         "-f", "srt", "-"], capture_output=True, text=True)
    emb = parse_srt(out.stdout)
    if len(emb) != len(readable):
        sys.exit(f"embedded cues {len(emb)} != readable {len(readable)}")
    for a, b in zip(emb, readable):
        if norm_text(a["text"]) != norm_text(b["text"]):
            sys.exit("embedded subtitle text drift vs readable SRT")
        if abs(a["start"] - b["start"]) > 0.05 or \
                abs(a["end"] - b["end"]) > 0.05:
            sys.exit("embedded subtitle timing drift vs readable SRT")
    print("embedded mov_text track verified against readable SRT")

    entry = {
        "path": "ClientGodot/assets/cinematics/CIN_000/"
                "CIN_000_640x360_30fps_sub_vi.mp4",
        "sha256": sha256_of(OUT_MP4),
        "sizeBytes": OUT_MP4.stat().st_size,
        "durationSeconds": round(dur, 4),
        "streams": ["video:h264", "audio:aac", "subtitle:mov_text"],
        "subtitles": {
            "burnedIn": True,
            "embeddedTrack": "mov_text, language vie, default",
            "renderer": "libass subtitles filter, DejaVu Sans bold "
                        "16, white on semi-transparent black box",
            "sourceFile": "CIN_000_vi_readable.srt",
            "chunks": len(readable),
        },
        "audio": {
            "source": "checkpoint 27 embedded mix of the canonical "
                      "MP4 (mix file itself unchanged)",
            "presentationGainDb": GAIN_DB,
            "loudnessLufs": lufs,
            "truePeakDbtp": tp,
        },
        "note": "Owner-requested viewing variant (2026-11-06): "
                "on-screen Vietnamese subtitles + clearly audible "
                "narration. Canonical MP4 / OGV / SRT unchanged.",
    }
    exp["mp4SubVi"] = entry
    exp["readableSrt"] = {
        "path": "ClientGodot/assets/cinematics/CIN_000/"
                "CIN_000_vi_readable.srt",
        "sha256": sha256_of(READABLE_SRT),
        "sizeBytes": READABLE_SRT.stat().st_size,
        "cues": len(readable),
        "derivedFrom": "CIN_000_vi.srt (canonical 6 cues, unchanged)",
        "method": "sentence then clause split at <=82 chars; timing "
                  "proportional to character count inside each "
                  "canonical cue window, with a 1.2 s minimum "
                  "display per chunk redistributed inside the cue; "
                  "concatenated text identical "
                  "to canonical (whitespace-normalized); sequence "
                  "kept monotonic across the one canonical overlap "
                  "(cue 3/4) by a +0.336 s shift of cue 4 chunks",
    }
    exp.setdefault("notes", []).append(
        "Checkpoint 28 adds mp4SubVi: a subtitled viewing variant "
        "(burned-in + embedded readable subtitles, narration at "
        "+5 dB presentation gain). Canonical files unchanged.")
    EXPORT_MANIFEST.write_text(
        json.dumps(exp, ensure_ascii=False, indent=1),
        encoding="utf-8")

    fman = json.loads(FILM_MANIFEST.read_text(encoding="utf-8"))
    fman["subtitledVariant"] = {
        "file": entry["path"].split("/")[-1],
        "sha256": entry["sha256"],
        "checkpoint": "MEDIA-02 checkpoint 28",
        "readableSrtSha256": exp["readableSrt"]["sha256"],
    }
    FILM_MANIFEST.write_text(
        json.dumps(fman, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(json.dumps({"mp4SubVi": entry["sha256"],
                      "sizeBytes": entry["sizeBytes"],
                      "durationSeconds": entry["durationSeconds"],
                      "readableSrtSha256":
                          exp["readableSrt"]["sha256"],
                      "chunks": len(readable)},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
