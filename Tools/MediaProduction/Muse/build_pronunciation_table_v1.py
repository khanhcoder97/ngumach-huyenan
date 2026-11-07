#!/usr/bin/env python3
"""MEDIA-02 checkpoint 44: pronunciation / proper-name table + gap,
head-tail, ducking and seam cues + fallback playback (Codex WO32 item 3).

Builds Implementation/Content/Audio/Deliveries/PRONUNCIATION_TABLE_v1.json
(manifestId NGM_PRONUNCIATION_TABLE_V1) from real bytes and real sources:

- NAMES (16): every proper name a VO listener / reviewer must pronounce --
  the 4 names actually SPOKEN in current audio (Lac Chau, Huyen An, Ben Mua
  in the prologue narration; Sa Hoa in CIN_018_S03), the 10 speaker/role
  names the draft voices have to embody (D-10), the boss name Mang Cot
  (BOSS_MANG_COT, CIN_004 character list) and the title Ngu Mach.
  Each entry carries syllable + tone guidance, approximate Northern
  Vietnamese IPA, the takes that embody it, where (if anywhere) it is
  spoken, and its decision status. The builder VERIFIES every grounding:
  speaker IDs and displays against the VO manifests, spoken names against
  the prologue SRT / take texts, "Ta Van Khanh" against a docs/production
  count (owner decision 2026-11-07, D-12), "Mang Cot" against
  docs/production + the CIN_004 timing character list. Any mismatch exits
  1 and writes nothing.
- PLAYBACK CUES (17 mix rows): the 11 embedded mixes + the 6 P0 v1/v2
  alternates. Per row: head/tail silence measured by silencedetect
  (-60 dBFS) on the real mix WAV, VO take lead/tail silence measured on
  the real take WAV, window slack from the VO manifests, ducking depth
  from the mix manifest evidence (sha256-verified), and loop joins from
  the manifest loopQA (bed loop 16.0 s, 1.0 s crossfade; prologue bed
  ben_mua hard-loops at 56.667 s, ported beds at their OGG periods).
- SEAM TABLE (19 rows): wrap jump re-measured from the real runtime OGG
  bed bytes (the files the adapter loops) with the CP07/CP33 method
  (mono 48 kHz f32; head/tail first/last 100 ms; |last-first|), asserted
  equal to the CP33 shortlist recorded values within 0.002. Flag
  ear-check above 0.015. Indicator only, never a seamlessness PASS.
  (Measuring the composed master WAV instead would give ~0: the master
  carries a 0.25 s end-landing, so it hides the real runtime seam.)
- FALLBACK TABLE (21 scenes): per-scene playback fallback chain from
  PLAYBACK_METADATA_v1.json + the mix manifests, every referenced file
  verified to exist (mix WAV sha256 vs manifest for embedded scenes):
  embedded soundtrack -> standalone mix WAV -> stem re-assembly + VO
  take -> VO take + SRT -> silent video + SRT overlay. Silent scenes
  (CIN_011-020) have no mix fallback: the adapter must not improvise
  one. Global rules: never play embedded + external audio together;
  burned-subtitle variant is review-only; rewatch/skip/seen/fallback
  never grant quest.

NOT_AUDITIONED: this environment cannot listen. All numbers are
measurements from real bytes; the table hands the listener playlists,
timecodes and questions, it is not a listening PASS. Loudness is NOT
re-measured here as a creative checkpoint (WO32 item 3 rule): the only
loudness figures carried over are the mix-manifest values, cited with
their checkpoint, for ducking context.
"""
import hashlib
import json
import math
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
OUT = (ROOT / "Implementation/Content/Audio/Deliveries"
       / "PRONUNCIATION_TABLE_v1.json")
CP33 = (ROOT / "Implementation/Reports/MuseMedia"
        / "MEDIA02_CHECKPOINT_33_AB_SHORTLIST_20261106.json")
PLAYBACK = ROOT / "ClientGodot/assets/cinematics/PLAYBACK_METADATA_v1.json"
SRT_PROLOGUE = (ROOT / "Implementation/Content/Narrative/Deliveries/CIN_000"
                / "CIN_000_vi.srt")
CIN004_TIMING = (ROOT / "Implementation/Content/Narrative/Deliveries/CIN_004"
                 / "CIN_004_timing_v1.json")
VO_DIRS = {
    "p0": ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT",
    "campaign": ROOT / "Art_Source/Audio/Muse/VO/CAMPAIGN_DRAFT",
    "cin006": ROOT / "Art_Source/Audio/Muse/VO/CIN006_DRAFT",
    "prologue": ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT",
}
VO_MANIFESTS = {
    "p0": VO_DIRS["p0"] / "P0_VO_manifest_v1.json",
    "campaign": VO_DIRS["campaign"] / "CAMPAIGN_VO_manifest_v1.json",
    "cin006": VO_DIRS["cin006"] / "CIN006_VO_manifest_v1.json",
    "prologue": ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json",
}
MIX_MANIFESTS = {
    "p0v1": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT/P0_MIX_manifest_v1.json",
    "p0v2": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/P0_MIX_V2_manifest_v1.json",
    "p0v3": ROOT / "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/P0_MIX_V3_manifest_v1.json",
    "cin003": ROOT / "Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1/CIN003_MIX_V1_manifest_v1.json",
    "cin005": ROOT / "Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1/CIN005_MIX_V1_manifest_v1.json",
    "cin006": ROOT / "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1/CIN006_MIX_V1_manifest_v1.json",
    "cin007": ROOT / "Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1/CIN007_MIX_V1_manifest_v1.json",
    "cin008": ROOT / "Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1/CIN008_MIX_V1_manifest_v1.json",
    "cin009": ROOT / "Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1/CIN009_MIX_V1_manifest_v1.json",
    "cin010": ROOT / "Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1/CIN010_MIX_V1_manifest_v1.json",
    "prologue": ROOT / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_manifest_v1.json",
}
COMPOSED = ROOT / "Art_Source/Audio/Muse/COMPOSED"
SEAM_TOL = 0.002
SEAM_FLAG = 0.015
SILENCE_NOISE_DB = -60.0

ERRORS = []


def err(msg):
    ERRORS.append(msg)
    print("MISMATCH:", msg, file=sys.stderr)


def fail_if_errors():
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} mismatch(es); no file written.",
              file=sys.stderr)
        sys.exit(1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print("FAILED:", " ".join(str(c) for c in cmd), file=sys.stderr)
        print(r.stdout[-2000:], r.stderr[-2000:], file=sys.stderr)
        sys.exit(1)
    return r


def probe_duration(path: Path) -> float:
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "csv=p=0", str(path)])
    return float(r.stdout.strip())


def silence_intervals(path: Path):
    """[(start, end)] silence intervals from silencedetect at -60 dBFS."""
    r = run(["ffmpeg", "-i", str(path), "-af",
             f"silencedetect=noise={SILENCE_NOISE_DB}dB:d=0.05",
             "-f", "null", "-"])
    starts, ends, intervals = [], [], []
    for line in r.stderr.splitlines():
        m = re.search(r"silence_start: ([0-9.]+)", line)
        if m:
            starts.append(float(m.group(1)))
        m = re.search(r"silence_end: ([0-9.]+)", line)
        if m:
            ends.append(float(m.group(1)))
    for s, e in zip(starts, ends):
        intervals.append((s, e))
    if len(starts) > len(ends):  # silence runs to end of file
        intervals.append((starts[-1], probe_duration(path)))
    return intervals


def head_tail_silence(path: Path, duration: float):
    iv = silence_intervals(path)
    head = 0.0
    tail = 0.0
    for s, e in iv:
        if s <= 0.01:
            head = round(e, 3)
    for s, e in iv:
        if e >= duration - 0.01:
            tail = round(duration - s, 3)
    return head, tail


def measure_wrap_jump(path: Path):
    """CP07/CP33 seam method: mono 48 kHz f32; head/tail 100 ms RMS;
    wrap jump = |last sample - first sample|."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path),
                        "-ac", "1", "-ar", "48000", "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0:
        print("DECODE FAILED:", path, file=sys.stderr)
        sys.exit(1)
    x = np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)
    if x.size < 9600:
        print("TOO SHORT FOR SEAM:", path, file=sys.stderr)
        sys.exit(1)
    head = x[:4800]
    tail = x[-4800:]
    head_rms = float(np.sqrt(np.mean(head * head)))
    tail_rms = float(np.sqrt(np.mean(tail * tail)))
    wrap = float(abs(x[-1] - x[0]))
    return round(wrap, 6), round(head_rms, 6), round(tail_rms, 6)


def parse_srt(path: Path):
    text = path.read_text(encoding="utf-8")
    cues = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().splitlines()
        if len(lines) < 3:
            continue
        m = re.match(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> "
                     r"(\d\d):(\d\d):(\d\d),(\d\d\d)", lines[1])
        if not m:
            continue
        a = (int(m.group(1)) * 3600 + int(m.group(2)) * 60
             + int(m.group(3)) + int(m.group(4)) / 1000.0)
        b = (int(m.group(5)) * 3600 + int(m.group(6)) * 60
             + int(m.group(7)) + int(m.group(8)) / 1000.0)
        cues.append({"index": int(lines[0]), "startSeconds": round(a, 3),
                     "endSeconds": round(b, 3),
                     "text": " ".join(lines[2:]).strip()})
    return cues


def docs_counts(names):
    counts = {n: 0 for n in names}
    for p in (ROOT / "docs/production").rglob("*.md"):
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for n in names:
            counts[n] += t.count(n)
    return counts


def find_take_wav(filename: str) -> Path:
    for d in VO_DIRS.values():
        p = d / filename
        if p.exists():
            return p
    err(f"VO take file not found in any VO dir: {filename}")
    return VO_DIRS["campaign"] / filename

# ---------------------------------------------------------------- names
# Curated pronunciation entries. Tones use the Northern Vietnamese names
# (ngang level, huyen low-falling, sac rising, hoi dipping-rising,
# nga creaky-rising, nang heavy falling). IPA is an approximation for a
# Northern listener, not a phonetic claim about the draft TTS.
NAME_ENTRIES = [
    {"name": "Lạc Châu", "kind": "PLACE", "speakerId": None,
     "voice": None, "status": "PROPOSED",
     "source": "Prologue SRT cue 1 + cue 4 (spoken narration); docs/production",
     "syllables": [{"syllable": "Lạc", "tone": "nặng"},
                   {"syllable": "Châu", "tone": "ngang"}],
     "ipaApprox": "/laːk˨˩ʔ tɕəw˧/",
     "listenFor": "“Lạc” nặng phải dứt khoát, không đọc thành “Lạc” sắc; “Châu” ngang giữ nguyên, không lên giọng ở cuối câu."},
    {"name": "Huyền Ấn", "kind": "CONCEPT", "speakerId": None,
     "voice": None, "status": "PROPOSED",
     "source": "Prologue SRT cue 1 (spoken narration); docs/production",
     "syllables": [{"syllable": "Huyền", "tone": "huyền"},
                   {"syllable": "Ấn", "tone": "nặng"}],
     "ipaApprox": "/hwiən˨˩ ʔən˨˩ʔ/",
     "listenFor": "“Huyền” huyền trầm xuống; “Ấn” nặng ngắt gọn — cả hai đều trầm, không đọc “Ấn” thành sắc."},
    {"name": "Bến Mưa", "kind": "PLACE", "speakerId": None,
     "voice": None, "status": "PROPOSED",
     "source": "Prologue SRT cue 5 (spoken narration); docs/production",
     "syllables": [{"syllable": "Bến", "tone": "nặng"},
                   {"syllable": "Mưa", "tone": "ngang"}],
     "ipaApprox": "/ɓen˨˩ʔ mɯə˧/",
     "listenFor": "“Bến” nặng ngắt; “Mưa” ngang kéo nhẹ — tên bến là mốc địa danh của cả campaign, phải đọc thống nhất với mọi lần nhắc sau."},
    {"name": "Sa Hỏa", "kind": "PLACE", "speakerId": None,
     "voice": None, "status": "PROPOSED",
     "source": "CIN_018_S03 dialogue text (spoken); scene setting Sa Hỏa",
     "syllables": [{"syllable": "Sa", "tone": "ngang"},
                   {"syllable": "Hỏa", "tone": "hỏi"}],
     "ipaApprox": "/sa˧ hwa˧˩˧/",
     "listenFor": "“Hỏa” hỏi phải có chỗ luyến xuống rồi lên — đây là tên riêng duy nhất được nói ra trong 21 cửa sổ thoại campaign; nghe tại CIN_018_S03 (D-10)."},
    {"name": "Ly An", "kind": "CHARACTER", "speakerId": "NPC_LYAN",
     "voice": "Aria (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifests (7 takes, speaker NPC_LYAN)",
     "syllables": [{"syllable": "Ly", "tone": "ngang"},
                   {"syllable": "An", "tone": "ngang"}],
     "ipaApprox": "/li˧ ʔan˧/",
     "listenFor": "Tên nhân vật KHÔNG được nói ra trong bất kỳ câu thoại nào — kiểm tra giọng Aria có đọc như cùng một nhân vật qua 7 take (D-02/D-10), không kiểm tra phát âm tên."},
    {"name": "Tạ Vân Khanh", "kind": "CHARACTER", "speakerId": "NPC_TA_VAN_KHANH",
     "voice": "Helio (fictional system voice)", "status": "DECIDED",
     "source": "Owner decision 2026-11-07 (D-12 RESOLVED): canonical spelling; docs/production count verified by this builder",
     "syllables": [{"syllable": "Tạ", "tone": "nặng"},
                   {"syllable": "Vân", "tone": "huyền"},
                   {"syllable": "Khanh", "tone": "ngang"}],
     "ipaApprox": "/taː˨˩ʔ vən˨˩ xajŋ˧/",
     "listenFor": "Cách viết ĐÃ CHỐT — “Tạ Vân Khanh”, không phải “Tạ Văn Khánh”. Tên KHÔNG được nói ra trong cả hai câu thoại — kiểm tra giọng Helio có đọc như cùng một nhân vật ở CIN_002_S02 và CIN_008_S03 (D-12/D-02)."},
    {"name": "Hạ Mặc", "kind": "CHARACTER", "speakerId": "NPC_HA_MAC",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifests (4 takes, speaker NPC_HA_MAC); DEC-MEDIA-P0 Q4 cinematic-only staging",
     "syllables": [{"syllable": "Hạ", "tone": "nặng"},
                   {"syllable": "Mặc", "tone": "nặng"}],
     "ipaApprox": "/haː˨˩ʔ măk˨˩ʔ/",
     "listenFor": "Tên KHÔNG được nói ra trong câu thoại — kiểm tra giọng có hợp vai qua 4 take (CIN_006_S03, CIN_011_S03, CIN_012_S03, CIN_016_S03); cả hai âm tiết đều nặng, không đọc “Mặc” thành “Mạc” sắc."},
    {"name": "Sầm Chủ Quỹ", "kind": "CHARACTER", "speakerId": "NPC_SAM_CHU_QUY",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker NPC_SAM_CHU_QUY); DEC-MEDIA-P0 Q4 cinematic-only staging",
     "syllables": [{"syllable": "Sầm", "tone": "huyền"},
                   {"syllable": "Chủ", "tone": "hỏi"},
                   {"syllable": "Quỹ", "tone": "ngã"}],
     "ipaApprox": "/səm˨˩ cu˧˩˧ kwi˧˥ˀ/",
     "listenFor": "Tên KHÔNG được nói ra trong câu thoại — kiểm tra giọng hợp vai tại CIN_010_S03; “Quỹ” ngã phải có độ nghẹn đặc trưng, không đọc thành “Quỷ” hỏi."},
    {"name": "Tống Bành", "kind": "CHARACTER", "speakerId": "NPC_TONG_BANH",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker NPC_TONG_BANH)",
     "syllables": [{"syllable": "Tống", "tone": "nặng"},
                   {"syllable": "Bành", "tone": "huyền"}],
     "ipaApprox": "/toŋ˨˩ʔ ɓaɲ˨˩/",
     "listenFor": "Tên KHÔNG được nói ra trong câu thoại — kiểm tra giọng hợp vai tại CIN_014_S03; “Tống” nặng ngắt, “Bành” huyền trầm."},
    {"name": "Cơ Vô Tướng", "kind": "CHARACTER", "speakerId": "NPC_CO_VO_TUONG",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker NPC_CO_VO_TUONG)",
     "syllables": [{"syllable": "Cơ", "tone": "ngang"},
                   {"syllable": "Vô", "tone": "huyền"},
                   {"syllable": "Tướng", "tone": "ngã"}],
     "ipaApprox": "/kɤ˧ vo˨˩ tɯəŋ˧˥ˀ/",
     "listenFor": "Tên KHÔNG được nói ra trong câu thoại — kiểm tra giọng hợp vai tại CIN_018_S02; “Tướng” ngã, không đọc thành “Tưởng” hỏi."},
    {"name": "Trưởng đoàn", "kind": "ROLE", "speakerId": "NPC_REFUGEE_LEADER",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker NPC_REFUGEE_LEADER, display “Trưởng đoàn”)",
     "syllables": [{"syllable": "Trưởng", "tone": "hỏi"},
                   {"syllable": "đoàn", "tone": "huyền"}],
     "ipaApprox": "/tʂɯəŋ˧˩˧ ɗwaːn˨˩/",
     "listenFor": "Chức danh, không phải tên riêng — kiểm tra giọng hợp vai tại CIN_013_S03; “Trưởng” hỏi có chỗ luyến."},
    {"name": "Đội trưởng thợ lặn", "kind": "ROLE", "speakerId": "NPC_DIVER_LEAD",
     "voice": "Helio (fictional system voice)", "status": "PROPOSED",
     "source": "VO manifests (2 takes, speaker NPC_DIVER_LEAD, display “Đội trưởng thợ lặn”)",
     "syllables": [{"syllable": "Đội", "tone": "nặng"},
                   {"syllable": "trưởng", "tone": "hỏi"},
                   {"syllable": "thợ", "tone": "hỏi"},
                   {"syllable": "lặn", "tone": "nặng"}],
     "ipaApprox": "/ɗoːj˨˩ʔ tʂɯəŋ˧˩˧ tʰɤ˧˩˧ lăn˨˩ʔ/",
     "listenFor": "Chức danh — kiểm tra giọng có đọc như cùng một nhân vật ở CIN_015_S03 và CIN_017_S03 (D-02)."},
    {"name": "Người chơi", "kind": "ROLE", "speakerId": "PLAYER",
     "voice": "Helio (fictional system voice, timing-only placeholder)",
     "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker PLAYER); VOICE_GUIDE assigns the player no spoken voice",
     "syllables": [{"syllable": "Người", "tone": "huyền"},
                   {"syllable": "chơi", "tone": "ngang"}],
     "ipaApprox": "/ŋɯəj˨˩ tɕɤj˧/",
     "listenFor": "Vai placeholder chỉ để canh timing (CIN_018_S03) — VOICE_GUIDE không gán giọng nói cho người chơi; không dùng take này làm chuẩn phát âm hay chuẩn giọng."},
    {"name": "Người nhận thư", "kind": "ROLE", "speakerId": None,
     "voice": "Aria (fictional system voice, placeholder role voice)",
     "status": "PROPOSED",
     "source": "VO manifest (1 take, speaker null, display “Người nhận thư”)",
     "syllables": [{"syllable": "Người", "tone": "huyền"},
                   {"syllable": "nhận", "tone": "nặng"},
                   {"syllable": "thư", "tone": "ngang"}],
     "ipaApprox": "/ŋɯəj˨˩ ɲən˨˩ʔ tʰɯ˧/",
     "listenFor": "Vai placeholder (CIN_020_S03) — kiểm tra giọng hợp vai trò, không phải tên riêng của một nhân vật cố định."},
    {"name": "Mãng Cốt", "kind": "BOSS", "speakerId": "BOSS_MANG_COT",
     "voice": None, "status": "PROPOSED",
     "source": "CIN_004 timing charactersOnScreen [BOSS_MANG_COT]; docs/production; MUSIC/boss_mang_cot cue",
     "syllables": [{"syllable": "Mãng", "tone": "ngã"},
                   {"syllable": "Cốt", "tone": "nặng"}],
     "ipaApprox": "/maːŋ˧˥ˀ kot˨˩ʔ/",
     "listenFor": "Boss không có câu thoại — tên chỉ xuất hiện trong danh sách nhân vật và cue nhạc; “Mãng” ngã, “Cốt” nặng, không đọc “Mãng” thành “Mang” ngang."},
    {"name": "Ngũ Mạch", "kind": "CONCEPT", "speakerId": None,
     "voice": None, "status": "PROPOSED",
     "source": "Game title; docs/production",
     "syllables": [{"syllable": "Ngũ", "tone": "ngã"},
                   {"syllable": "Mạch", "tone": "nặng"}],
     "ipaApprox": "/ŋu˧˥ˀ maːk˨˩ʔ/",
     "listenFor": "Tên game — không được nói ra trong audio hiện tại; ghi để thống nhất nếu narration sau này nhắc tới."},
]


def load_vo_takes():
    """All draft VO takes: key -> {shotId, speaker, speakerDisplay, voice,
    text, windowSceneSeconds, durationSeconds, wav, wavSha256, sourceDir}."""
    takes = {}
    for label, mp in VO_MANIFESTS.items():
        if label == "prologue":
            continue
        d = json.loads(mp.read_text(encoding="utf-8"))
        for t in d["takes"]:
            takes[t["key"]] = {
                "shotId": t["shotId"], "speaker": t.get("speaker"),
                "speakerDisplay": t.get("speakerDisplay"),
                "voice": t.get("voiceLabel") or t.get("voice"),
                "text": t["text"],
                "windowSceneSeconds": t["windowSceneSeconds"],
                "durationSeconds": t["durationSeconds"],
                "wav": t["wav"], "wavSha256": t.get("wavSha256"),
                "sourceDir": label,
            }
    return takes


def build_names(takes, srt_cues, srt_text):
    docs = docs_counts(["Tạ Vân Khanh", "Tạ Văn Khánh", "Mãng Cốt",
                        "Ngũ Mạch", "Lạc Châu", "Bến Mưa", "Sa Hỏa",
                        "Huyền Ấn"])
    all_texts = [t["text"] for t in takes.values()] + [c["text"] for c in srt_cues]
    out = []
    for e in NAME_ENTRIES:
        name = e["name"]
        if not unicodedata.is_normalized("NFC", name):
            err(f"name not NFC: {name}")
        # spoken occurrences in real audio texts
        spoken = []
        for c in srt_cues:
            if name in c["text"]:
                spoken.append({"source": "prologue SRT",
                               "cue": c["index"],
                               "spanSeconds": [c["startSeconds"], c["endSeconds"]]})
        for key, t in takes.items():
            if name in t["text"]:
                spoken.append({"source": "dialogue take", "key": key,
                               "shotId": t["shotId"],
                               "windowSeconds": t["windowSceneSeconds"]})
        # speaker takes
        entry_takes = []
        if e["speakerId"]:
            for key, t in takes.items():
                if t["speaker"] == e["speakerId"]:
                    entry_takes.append({
                        "key": key, "shotId": t["shotId"],
                        "wav": t["wav"],
                        "windowSeconds": t["windowSceneSeconds"],
                        "durationSeconds": t["durationSeconds"],
                        "voice": t["voice"]})
            if not entry_takes and e["speakerId"] != "BOSS_MANG_COT":
                err(f"no VO takes found for speaker {e['speakerId']} ({name})")
            if entry_takes and e["voice"]:
                for t in entry_takes:
                    # entry voice may add a parenthetical note after the
                    # manifest voiceLabel; the base voice name must match.
                    base_manifest = (t["voice"] or "").split(" (")[0]
                    base_table = e["voice"].split(" (")[0]
                    if base_manifest != base_table:
                        err(f"voice mismatch for {name}: manifest {t['voice']!r} vs table {e['voice']!r}")
        if e["speakerId"] is None and name == "Người nhận thư":
            for key, t in takes.items():
                if t.get("speakerDisplay") == "Người nhận thư":
                    entry_takes.append({
                        "key": key, "shotId": t["shotId"],
                        "wav": t["wav"],
                        "windowSeconds": t["windowSceneSeconds"],
                        "durationSeconds": t["durationSeconds"],
                        "voice": t["voice"]})
            if not entry_takes:
                err("no VO take found for display 'Người nhận thư'")
        # targeted grounding checks
        if name == "Tạ Vân Khanh":
            # Method: docs/production/**/*.md substring count (this builder).
            # CP36 counted a wider tree (176x); the decision stands either
            # way: canonical present, wrong spelling absent.
            if docs["Tạ Vân Khanh"] < 10:
                err(f"Tạ Vân Khanh docs count too low: {docs['Tạ Vân Khanh']}")
            if docs["Tạ Văn Khánh"] != 0:
                err(f"wrong spelling 'Tạ Văn Khánh' found in docs: {docs['Tạ Văn Khánh']}")
        if name == "Mãng Cốt":
            if docs["Mãng Cốt"] < 1:
                err("Mãng Cốt not found in docs/production")
            timing = json.loads(CIN004_TIMING.read_text(encoding="utf-8"))
            if "BOSS_MANG_COT" not in timing.get("charactersOnScreen", []):
                err("BOSS_MANG_COT missing from CIN_004 timing charactersOnScreen")
        if name in ("Lạc Châu", "Huyền Ấn", "Bến Mưa"):
            if not spoken:
                err(f"{name} claimed spoken in prologue but not found in SRT text")
        if name == "Sa Hỏa":
            if not any(s["source"] == "dialogue take" for s in spoken):
                err("Sa Hỏa claimed spoken in dialogue but not found in any take text")
        if name in ("Ly An", "Hạ Mặc", "Sầm Chủ Quỹ", "Tống Bành",
                    "Cơ Vô Tướng", "Tạ Vân Khanh", "Mãng Cốt", "Ngũ Mạch",
                    "Trưởng đoàn", "Đội trưởng thợ lặn", "Người chơi",
                    "Người nhận thư"):
            if spoken:
                err(f"{name} unexpectedly spoken in audio: {spoken}")
        out.append({
            "name": name, "kind": e["kind"], "speakerId": e["speakerId"],
            "voice": e["voice"], "status": e["status"], "source": e["source"],
            "syllables": e["syllables"], "ipaApprox": e["ipaApprox"],
            "spokenInAudio": bool(spoken), "spokenOccurrences": spoken,
            "takes": entry_takes, "takeCount": len(entry_takes),
            "listenFor": e["listenFor"],
            "docsProductionOccurrences": docs.get(name),
        })
    return out, docs

# ------------------------------------------------------- playback cues
# (sceneId, mixVersion, manifestKey, sourceMixRel, runtimeMixRel)
MIX_ROWS = [
    ("CIN_000", "prologue_mix_v1", "prologue",
     "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT/PROLOGUE_mix_v1.wav",
     "ClientGodot/assets/audio/mix/prologue/PROLOGUE_mix_v1.wav"),
    ("CIN_001", "v1", "p0v1",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT/CIN_001_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/p0/CIN_001_mix_draft_v1.wav"),
    ("CIN_002", "v1", "p0v1",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT/CIN_002_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/p0/CIN_002_mix_draft_v1.wav"),
    ("CIN_004", "v1", "p0v1",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT/CIN_004_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/p0/CIN_004_mix_draft_v1.wav"),
    ("CIN_001", "v2", "p0v2",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/CIN_001_mix_draft_v2.wav",
     "ClientGodot/assets/audio/mix/p0_v2/CIN_001_mix_draft_v2.wav"),
    ("CIN_002", "v2", "p0v2",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/CIN_002_mix_draft_v2.wav",
     "ClientGodot/assets/audio/mix/p0_v2/CIN_002_mix_draft_v2.wav"),
    ("CIN_004", "v2", "p0v2",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V2/CIN_004_mix_draft_v2.wav",
     "ClientGodot/assets/audio/mix/p0_v2/CIN_004_mix_draft_v2.wav"),
    ("CIN_001", "v3", "p0v3",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/CIN_001_mix_draft_v3.wav",
     "ClientGodot/assets/audio/mix/p0_v3/CIN_001_mix_draft_v3.wav"),
    ("CIN_002", "v3", "p0v3",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/CIN_002_mix_draft_v3.wav",
     "ClientGodot/assets/audio/mix/p0_v3/CIN_002_mix_draft_v3.wav"),
    ("CIN_004", "v3", "p0v3",
     "Art_Source/Audio/Muse/MIX/P0_DRAFT_V3/CIN_004_mix_draft_v3.wav",
     "ClientGodot/assets/audio/mix/p0_v3/CIN_004_mix_draft_v3.wav"),
    ("CIN_003", "v1_cin003_proposed", "cin003",
     "Art_Source/Audio/Muse/MIX/CIN003_DRAFT_V1/CIN_003_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin003_v1/CIN_003_mix_draft_v1.wav"),
    ("CIN_005", "v1_cin005_proposed", "cin005",
     "Art_Source/Audio/Muse/MIX/CIN005_DRAFT_V1/CIN_005_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin005_v1/CIN_005_mix_draft_v1.wav"),
    ("CIN_006", "v1_cin006_proposed", "cin006",
     "Art_Source/Audio/Muse/MIX/CIN006_DRAFT_V1/CIN_006_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin006_v1/CIN_006_mix_draft_v1.wav"),
    ("CIN_007", "v1_cin007_proposed", "cin007",
     "Art_Source/Audio/Muse/MIX/CIN007_DRAFT_V1/CIN_007_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin007_v1/CIN_007_mix_draft_v1.wav"),
    ("CIN_008", "v1_cin008_proposed", "cin008",
     "Art_Source/Audio/Muse/MIX/CIN008_DRAFT_V1/CIN_008_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin008_v1/CIN_008_mix_draft_v1.wav"),
    ("CIN_009", "v1_cin009_proposed", "cin009",
     "Art_Source/Audio/Muse/MIX/CIN009_DRAFT_V1/CIN_009_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin009_v1/CIN_009_mix_draft_v1.wav"),
    ("CIN_010", "v1_cin010_proposed", "cin010",
     "Art_Source/Audio/Muse/MIX/CIN010_DRAFT_V1/CIN_010_mix_draft_v1.wav",
     "ClientGodot/assets/audio/mix/cin010_v1/CIN_010_mix_draft_v1.wav"),
]
EMBEDDED_RUNTIME_MIX = {  # sceneId -> runtime standalone mix (embedded set)
    "CIN_000": "ClientGodot/assets/audio/mix/prologue/PROLOGUE_mix_v1.wav",
    "CIN_001": "ClientGodot/assets/audio/mix/p0_v3/CIN_001_mix_draft_v3.wav",
    "CIN_002": "ClientGodot/assets/audio/mix/p0_v3/CIN_002_mix_draft_v3.wav",
    "CIN_004": "ClientGodot/assets/audio/mix/p0_v3/CIN_004_mix_draft_v3.wav",
    "CIN_003": "ClientGodot/assets/audio/mix/cin003_v1/CIN_003_mix_draft_v1.wav",
    "CIN_005": "ClientGodot/assets/audio/mix/cin005_v1/CIN_005_mix_draft_v1.wav",
    "CIN_006": "ClientGodot/assets/audio/mix/cin006_v1/CIN_006_mix_draft_v1.wav",
    "CIN_007": "ClientGodot/assets/audio/mix/cin007_v1/CIN_007_mix_draft_v1.wav",
    "CIN_008": "ClientGodot/assets/audio/mix/cin008_v1/CIN_008_mix_draft_v1.wav",
    "CIN_009": "ClientGodot/assets/audio/mix/cin009_v1/CIN_009_mix_draft_v1.wav",
    "CIN_010": "ClientGodot/assets/audio/mix/cin010_v1/CIN_010_mix_draft_v1.wav",
}


def load_mix_manifests():
    out = {}
    for key, p in MIX_MANIFESTS.items():
        out[key] = json.loads(p.read_text(encoding="utf-8"))
    return out


def scene_entry(manifest, scene_id):
    if "scenes" in manifest:
        for s in manifest["scenes"]:
            if s["sceneId"] == scene_id:
                return s
        err(f"scene {scene_id} missing from mix manifest")
        return {}
    if scene_id == "CIN_000":
        return manifest  # prologue manifest is flat
    err(f"no scenes list in mix manifest for {scene_id}")
    return {}


def build_playback_cues(takes, srt_cues, mix_manifests):
    cues = []
    seam_inputs = {}  # (cueKey, version) -> measure path
    for scene_id, mix_version, mkey, src_rel, rt_rel in MIX_ROWS:
        src = ROOT / src_rel
        rt = ROOT / rt_rel
        if not src.exists():
            err(f"mix source missing: {src_rel}")
            continue
        if not rt.exists():
            err(f"mix runtime copy missing: {rt_rel}")
            continue
        man = mix_manifests[mkey]
        entry = scene_entry(man, scene_id)
        mix_info = entry.get("mix", {})
        if mix_info.get("file") and mix_info["file"] != src.name:
            err(f"mix filename mismatch {scene_id} {mix_version}: "
                f"manifest {mix_info['file']} vs file {src.name}")
        if mix_info.get("sha256"):
            actual = sha256(src)
            if actual != mix_info["sha256"]:
                err(f"mix sha256 mismatch {scene_id} {mix_version}")
            rt_actual = sha256(rt)
            if rt_actual != mix_info["sha256"]:
                err(f"runtime mix sha256 mismatch {scene_id} {mix_version}")
        duration = probe_duration(src)
        if mix_info.get("durationSeconds"):
            if abs(duration - mix_info["durationSeconds"]) > 0.01:
                err(f"mix duration mismatch {scene_id} {mix_version}: "
                    f"{duration} vs manifest {mix_info['durationSeconds']}")
        head_s, tail_s = head_tail_silence(src, duration)
        # VO span + take lead/tail
        vo_span = None
        take_lead = take_tail = None
        slack = None
        if scene_id == "CIN_000":
            vo_span = [{"cue": c["index"],
                        "spanSeconds": [c["startSeconds"], c["endSeconds"]],
                        "text": c["text"]} for c in srt_cues]
            # Final line reuses the CP04 take; its own lead/tail measured below.
            final_take = find_take_wav("VO_CIN001_S05_LYAN_draft_v1.wav")
            d = probe_duration(final_take)
            take_lead, take_tail = head_tail_silence(final_take, d)
            slack = None
            # Narration takes: lead/tail per segment (the take's true speech
            # onset is the SRT cue start + lead).
            narr_takes = []
            pro_vo = json.loads(VO_MANIFESTS["prologue"].read_text(encoding="utf-8"))
            for seg in pro_vo.get("segments", []):
                w = seg.get("file")
                if not w:
                    continue
                p = VO_DIRS["prologue"] / w
                if not p.exists():
                    err(f"prologue narration take missing: {w}")
                    continue
                if seg.get("sha256") and sha256(p) != seg["sha256"]:
                    err(f"prologue narration take sha mismatch: {w}")
                dd = probe_duration(p)
                if seg.get("durationSeconds") and abs(dd - seg["durationSeconds"]) > 0.01:
                    err(f"prologue narration take duration mismatch {w}")
                lead, tl = head_tail_silence(p, dd)
                narr_takes.append({"takeId": seg.get("takeId"), "file": w,
                                   "durationSeconds": round(dd, 3),
                                   "leadSilenceSeconds": lead,
                                   "tailSilenceSeconds": tl,
                                   "speaker": seg.get("speaker"),
                                   "voice": seg.get("voice")})
            vo_span = {"srtCues": vo_span, "narrationTakes": narr_takes,
                       "finalLineTake": "VO_CIN001_S05_LYAN_draft_v1.wav",
                       "finalLineTakeNote": "voTakeLeadSilenceSeconds / voTakeTailSilenceSeconds below belong to this reused CP04 take; narration takes carry their own lead/tail above."}
        else:
            vo = entry.get("vo", {})
            take_name = vo.get("take")
            take = None
            for t in takes.values():
                if t["wav"] == take_name:
                    take = t
                    break
            if take is None:
                err(f"VO take {take_name} not in VO manifests ({scene_id})")
            else:
                vo_span = {"windowSeconds": take["windowSceneSeconds"],
                           "takeSpanSeconds": vo.get("windowSeconds"),
                           "takeDurationSeconds": take["durationSeconds"]}
                w0, w1 = take["windowSceneSeconds"]
                slack = round(w1 - (w0 + take["durationSeconds"]), 3)
                take_path = find_take_wav(take_name)
                if take.get("wavSha256"):
                    if sha256(take_path) != take["wavSha256"]:
                        err(f"VO take sha256 mismatch: {take_name}")
                d = probe_duration(take_path)
                if abs(d - take["durationSeconds"]) > 0.01:
                    err(f"VO take duration mismatch {take_name}: "
                        f"{d} vs manifest {take['durationSeconds']}")
                take_lead, take_tail = head_tail_silence(take_path, d)
        # ducking evidence (manifest-recorded; not re-measured here)
        ducking = None
        duck_note = None
        dk = entry.get("ducking")
        if isinstance(dk, dict) and dk.get("evidence"):
            ducking = dk["evidence"]
        elif isinstance(dk, str):
            duck_note = dk
        # loop joins (manifest-recorded loopQA)
        loop_joins = entry.get("loopQA", [])
        if scene_id == "CIN_000":
            ben = probe_duration(ROOT / "ClientGodot/assets/audio/composed/music/ben_mua.ogg")
            joins = [{"cue": "MUSIC/ben_mua", "joinType": "hard loop, no crossfade",
                      "joinAtSeconds": [round(ben, 3)],
                      "note": "ben_mua OGG looped once (-stream_loop 1); one hard join inside the 87.367 s film"}]
            for cue_name in ("rain_light", "river_shore"):
                ogg = ROOT / f"ClientGodot/assets/audio/ambience/{cue_name}.ogg"
                if not ogg.exists():
                    err(f"prologue ported bed missing: {ogg}")
                    continue
                per = probe_duration(ogg)
                at = []
                t = per
                while t < duration - 0.01:
                    at.append(round(t, 3))
                    t += per
                joins.append({"cue": f"AMBIENCE/{cue_name}",
                              "joinType": "hard loop, no crossfade",
                              "joinAtSeconds": at,
                              "note": f"ported OGG looped infinitely (-stream_loop -1); period {round(per, 3)} s"})
            loop_joins = joins
        # seam inputs from stems
        stems = entry.get("stems", [])
        if scene_id == "CIN_000":
            stems = [
                {"cue": "MUSIC/ben_mua", "role": "music bed",
                 "source": "ClientGodot/assets/audio/composed/music/ben_mua.ogg",
                 "provenance": "ORIGINAL_COMPOSED_BY_MUSE_CP26"},
                {"cue": "AMBIENCE/rain_light", "role": "ambience",
                 "source": "ClientGodot/assets/audio/ambience/rain_light.ogg",
                 "provenance": "PORTED_CODEX_PACKV1"},
                {"cue": "AMBIENCE/river_shore", "role": "ambience",
                 "source": "ClientGodot/assets/audio/ambience/river_shore.ogg",
                 "provenance": "PORTED_CODEX_PACKV1"},
            ]
        for st in stems:
            cue = st.get("cue", "")
            # Stingers are one-shots, not loop beds: no seam row.
            if not cue or "/" not in cue or cue.startswith("SFX/"):
                continue
            if st.get("role") == "stinger":
                continue
            kind, name = cue.split("/", 1)
            version = ("composed" if "composed" in st.get("source", "")
                       or "COMPOSED" in st.get("provenance", "")
                       else "ported")
            # Measure the RUNTIME OGG bed bytes -- the file the adapter
            # actually loops. (CP33's wrap_jump_measured is a runtime-OGG
            # measurement; the master WAV carries a 0.25 s end-landing, so
            # measuring the master would give ~0 and hide the real seam.)
            measure = ROOT / st["source"]
            key = (cue, version)
            if key in seam_inputs and seam_inputs[key] != measure:
                err(f"seam measure path conflict for {key}")
            seam_inputs[key] = measure
        cues.append({
            "sceneId": scene_id, "mixVersion": mix_version,
            "sourceMix": src_rel, "runtimeMix": rt_rel,
            "durationSeconds": round(duration, 3),
            "mixIntegratedLUFS_manifest": mix_info.get("integratedLUFS"),
            "mixTruePeakDBTP_manifest": mix_info.get("truePeakDBTP"),
            "headSilenceSeconds": head_s,
            "tailSilenceSeconds": tail_s,
            "voSpan": vo_span,
            "voTakeLeadSilenceSeconds": take_lead,
            "voTakeTailSilenceSeconds": take_tail,
            "voWindowSlackSeconds": slack,
            "duckingEvidence_manifest": ducking,
            "duckingNote_manifest": duck_note,
            "loopJoins": loop_joins,
        })
    return cues, seam_inputs


def build_seam_table(seam_inputs):
    cp33 = json.loads(CP33.read_text(encoding="utf-8"))
    recorded = {}
    for row in cp33["seamTable"]:
        recorded[(row["cueKey"], row["version"])] = row
    table = []
    for (cue_key, version), path in sorted(seam_inputs.items()):
        if not path.exists():
            err(f"seam bed file missing: {path}")
            continue
        wrap, head_rms, tail_rms = measure_wrap_jump(path)
        ref = recorded.get((cue_key, version))
        if ref is None:
            err(f"no CP33 seam row for {(cue_key, version)}")
            continue
        if abs(wrap - ref["wrap_jump_measured"]) > SEAM_TOL:
            err(f"seam wrap jump drift {(cue_key, version)}: measured "
                f"{wrap} vs CP33 {ref['wrap_jump_measured']}")
        table.append({
            "cueKey": cue_key, "version": version,
            "measuredFrom": str(path.relative_to(ROOT)),
            "wrapJumpMeasured": wrap,
            "cp33WrapJumpMeasured": ref["wrap_jump_measured"],
            "cp33PostLandingRecorded": ref.get("wrap_jump_recorded"),
            "headRms100ms": head_rms, "tailRms100ms": tail_rms,
            "seamBasis": ref.get("seamBasis"),
            "flagEarCheck": bool(wrap > SEAM_FLAG),
        })
    return table

# -------------------------------------------------------- fallback table
FALLBACK_RULES = [
    {"id": "FB-0",
     "rule": "Never play the embedded soundtrack and any external mix/VO at the same time. EmbeddedMix, standalone mix WAVs and VO takes are the SAME mix delivered three ways, not layers (PLAYBACK_METADATA_v1.json audioOwnershipPolicy)."},
    {"id": "FB-1",
     "rule": "If the embedded audio stream is missing or corrupt in the OGV/MP4, fall back to the standalone mix WAV (same mixVersion, same sha256 as the mix manifest). Video stays the same file."},
    {"id": "FB-2",
     "rule": "If the standalone mix WAV is missing, re-assemble from stems + VO take per the mix manifest (same cues, gains and ducking recipe; adapter rebuilds, Muse does not re-render here)."},
    {"id": "FB-3",
     "rule": "If stems are missing, play the VO take + SRT overlay only (bed dropped). Never substitute another scene's bed."},
    {"id": "FB-4",
     "rule": "If all audio is missing, play silent video + SRT overlay. Subtitles carry the scene."},
    {"id": "FB-5",
     "rule": "If the SRT is missing, show no captions. Never burn captions from VO text and never use the review-only burned-subtitle variant as runtime."},
    {"id": "FB-6",
     "rule": "Scenes with no mix yet (CIN_011-020) play silent video + SRT only. The adapter must not improvise a mix from stems or play a VO take over silent video."},
    {"id": "FB-7",
     "rule": "Rewatch, skip, seen-state and any fallback step never grant quest progress (WO32 item 4; enforcement is the Codex runtime's job)."},
]

MIX_MANIFEST_BY_SCENE = {
    "CIN_000": "prologue",
    "CIN_001": "p0v3", "CIN_002": "p0v3", "CIN_004": "p0v3",
    "CIN_003": "cin003", "CIN_005": "cin005", "CIN_006": "cin006",
    "CIN_007": "cin007", "CIN_008": "cin008", "CIN_009": "cin009",
    "CIN_010": "cin010",
}


def build_fallback_table(takes, mix_manifests):
    pb = json.loads(PLAYBACK.read_text(encoding="utf-8"))
    rows = []
    checked_files = 0
    for sc in pb["scenes"]:
        sid = sc["sceneId"]
        ogv = sc["video"]["ogv"]["path"]
        mp4 = sc["video"]["mp4"]["path"]
        srt = sc.get("subtitle", {}).get("srtPath")
        for p in (ogv, mp4, srt):
            if p and not (ROOT / p).exists():
                err(f"fallback file missing for {sid}: {p}")
            if p:
                checked_files += 1
        row = {"sceneId": sid, "kind": sc["kind"],
               "hasEmbeddedSoundtrack": sc["hasEmbeddedSoundtrack"],
               "audioOwnership": sc["audioOwnership"],
               "primary": None, "fallbackMixWav": None,
               "fallbackStemsAndVo": None, "fallbackVoAndSrt": None,
               "fallbackSrtOnly": {"srt": srt},
               "ogv": ogv, "mp4": mp4}
        if sc["hasEmbeddedSoundtrack"]:
            mkey = MIX_MANIFEST_BY_SCENE[sid]
            entry = scene_entry(mix_manifests[mkey], sid)
            mix_info = entry.get("mix", {})
            rt_mix = EMBEDDED_RUNTIME_MIX[sid]
            if not (ROOT / rt_mix).exists():
                err(f"embedded fallback mix missing: {rt_mix}")
            elif mix_info.get("sha256") and sha256(ROOT / rt_mix) != mix_info["sha256"]:
                err(f"embedded fallback mix sha mismatch: {rt_mix}")
            else:
                checked_files += 1
            stems = entry.get("stems", [])
            stem_list = []
            if sid == "CIN_000":
                # The flat prologue manifest lists stems as descriptive
                # text, not paths; use the real runtime OGG paths.
                pro_vo = json.loads(VO_MANIFESTS["prologue"].read_text(encoding="utf-8"))
                narr = []
                for t in pro_vo.get("segments", []):
                    w = t.get("file")
                    if w:
                        p = VO_DIRS["prologue"] / w
                        if not p.exists():
                            err(f"prologue narration take missing: {w}")
                        else:
                            checked_files += 1
                        narr.append(w)
                vo_files = narr + ["VO_CIN001_S05_LYAN_draft_v1.wav"]
                if not find_take_wav("VO_CIN001_S05_LYAN_draft_v1.wav").exists():
                    err("prologue final-line take missing")
                else:
                    checked_files += 1
                stem_list = [
                    {"cue": "MUSIC/ben_mua", "role": "music bed",
                     "source": "ClientGodot/assets/audio/composed/music/ben_mua.ogg"},
                    {"cue": "AMBIENCE/rain_light", "role": "ambience",
                     "source": "ClientGodot/assets/audio/ambience/rain_light.ogg"},
                    {"cue": "AMBIENCE/river_shore", "role": "ambience",
                     "source": "ClientGodot/assets/audio/ambience/river_shore.ogg"},
                    {"cue": "SFX/CINEMA/resolve", "role": "title stinger",
                     "source": "ClientGodot/assets/audio/composed/cinema/resolve.ogg"},
                ]
                for st in stem_list:
                    if not (ROOT / st["source"]).exists():
                        err(f"prologue fallback stem missing: {st['source']}")
                    else:
                        checked_files += 1
            else:
                for st in stems:
                    src = st.get("source", "")
                    if src and not (ROOT / src).exists():
                        err(f"fallback stem missing for {sid}: {src}")
                    elif src:
                        checked_files += 1
                    stem_list.append({"cue": st.get("cue"), "role": st.get("role"),
                                      "source": src,
                                      "segmentSceneSeconds": st.get("segmentSceneSeconds"),
                                      "atSeconds": st.get("atSeconds")})
                vo = entry.get("vo", {})
                vo_files = [vo.get("take")] if vo.get("take") else []
                for w in vo_files:
                    if not find_take_wav(w).exists():
                        err(f"fallback VO take missing for {sid}: {w}")
                    else:
                        checked_files += 1
            row["primary"] = {"mode": "EMBEDDED_SOUNDTRACK",
                              "mixVersion": (sc.get("embeddedMix") or {}).get("mixVersion")}
            row["fallbackMixWav"] = {"path": rt_mix,
                                     "sha256": mix_info.get("sha256"),
                                     "mixVersion": (sc.get("embeddedMix") or {}).get("mixVersion")}
            row["fallbackStemsAndVo"] = {"stems": stem_list, "voTakes": vo_files}
            row["fallbackVoAndSrt"] = {"voTakes": vo_files, "srt": srt}
        else:
            scene_takes = [t for t in takes.values()
                           if t.get("shotId") and t["shotId"].startswith(sid)]
            row["primary"] = {"mode": "SILENT_VIDEO_PLUS_SRT_OVERLAY",
                              "note": "No scene mix delivered yet; adapter must not improvise one (FB-6)."}
            row["fallbackMixWav"] = None
            row["fallbackStemsAndVo"] = None
            row["fallbackVoAndSrt"] = None
            row["silentNote"] = {
                "voDraftsExist": [t["wav"] for t in scene_takes],
                "reason": "VO drafts exist for later mixing only; they are NOT a playback fallback over silent video."}
        rows.append(row)
    return rows, checked_files


def main():
    takes = load_vo_takes()
    srt_cues = parse_srt(SRT_PROLOGUE)
    srt_text = " ".join(c["text"] for c in srt_cues)
    if len(srt_cues) != 6:
        err(f"prologue SRT cue count changed: {len(srt_cues)} (expected 6)")
    mix_manifests = load_mix_manifests()
    names, docs = build_names(takes, srt_cues, srt_text)
    cues, seam_inputs = build_playback_cues(takes, srt_cues, mix_manifests)
    seam_table = build_seam_table(seam_inputs)
    fallback_rows, fallback_files = build_fallback_table(takes, mix_manifests)
    fail_if_errors()
    out = {
        "manifestId": "NGM_PRONUNCIATION_TABLE_V1",
        "checkpoint": "MEDIA-02 checkpoint 44 - pronunciation/proper-name table + gap/head-tail/ducking/seam cues + fallback playback (Codex WO32 item 3)",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "workOrderRef": "Work Order 32 (PR #128) item 3; issue #116 comment 6713518554",
        "branch": "muse/media-production-20261104",
        "baseSha": "6f2b4659b1935dc739df688942b5142a13dde770",
        "status": "DRAFT_NOT_FINAL",
        "auditionStatus": "NOT_AUDITIONED",
        "auditionNote": ("This environment cannot listen. Pronunciation guidance "
                         "is syllable + tone + approximate IPA for a Northern "
                         "listener to check against the draft takes; it is not a "
                         "listening PASS. All gap/head-tail/seam numbers are "
                         "measurements from real bytes. Loudness is not "
                         "re-measured here; mix loudness figures are cited from "
                         "their mix manifests only."),
        "counts": {
            "names": len(names),
            "namesSpokenInAudio": sum(1 for n in names if n["spokenInAudio"]),
            "namesDecided": sum(1 for n in names if n["status"] == "DECIDED"),
            "playbackCueRows": len(cues),
            "seamRows": len(seam_table),
            "seamRowsFlaggedEarCheck": sum(1 for r in seam_table if r["flagEarCheck"]),
            "fallbackScenes": len(fallback_rows),
            "fallbackFilesVerified": fallback_files,
        },
        "docsProductionOccurrences": docs,
        "names": names,
        "playbackCues": cues,
        "playbackCueNotes": {
            "silenceThreshold": "-60 dBFS (silencedetect, min 0.05 s)",
            "headSilence": "Silence from 0.0 s to first sound above threshold; use for fade-in / trim decisions.",
            "tailSilence": "Silence from last sound above threshold to file end; use for fade-out / trim decisions.",
            "voTakeLeadTail": "Leading/trailing silence INSIDE the VO take file; the take's true speech onset is window start + lead.",
            "voWindowSlack": "Window end minus take end; negative = overrun kept per owner verdict (3 campaign overruns untouched for Codex).",
            "ducking": "Music-bus depth from the mix manifest evidence (measured at mix build from the ducked vs unducked bus); NOT re-measured from the bounced mix, where VO energy and bed cannot be separated.",
            "loopJoins": "Ambience bed loop 16.0 s with 1.0 s crossfade: join centres at 15.5 s (18 s scenes) and 15.5/31.5 s (36 s scenes). Prologue beds hard-loop (no crossfade) at their periods.",
            "seamFlag": "wrap jump > 0.015 flags an ear check; it is an indicator, not a seamlessness PASS (CP07/CP33 method).",
        },
        "seamTable": seam_table,
        "fallbackRules": FALLBACK_RULES,
        "fallbackTable": fallback_rows,
        "verification": {
            "namesVerifiedAgainstVoManifests": True,
            "spokenNamesVerifiedAgainstSrtAndTakeTexts": True,
            "mixSha256VerifiedAgainstManifests": True,
            "seamWrapJumpReMeasuredAndMatchedCp33Within": SEAM_TOL,
            "fallbackFilesExistenceChecked": fallback_files,
        },
    }
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if not unicodedata.is_normalized("NFC", text):
        err("output JSON is not NFC")
        fail_if_errors()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text + "\n", encoding="utf-8")
    print(f"WROTE {OUT.relative_to(ROOT)}")
    print(f"names={len(names)} spoken={out['counts']['namesSpokenInAudio']} "
          f"cues={len(cues)} seam={len(seam_table)} "
          f"flagged={out['counts']['seamRowsFlaggedEarCheck']} "
          f"fallback={len(fallback_rows)} files={fallback_files}")
    print("PASS: 0 mismatches")


if __name__ == "__main__":
    main()
