#!/usr/bin/env python3
"""MEDIA-02 checkpoint 27: prologue (CIN_000) narration VO drafts.

Owner-approved script (main chat, 2026-11-06): a ~100 s lore prologue
shown after character creation, covering the origin of the Five Veins,
the quake 300 years ago, the disaster and sealing 30 years ago, the
present wrong currents, and the arrival at Ben Mua -- ending on Ly An's
 canonical first line, which hands off into CIN_001 / gameplay.

Canon guardrails (Content Bible section 1, Narrative Depth reveal
table, STORY_DECISIONS_V3):
  - the player has NO secret bloodline and is not a chosen one; the
    film never gives the avatar an origin, a name or a face;
  - at this point in the story the audience must NOT yet learn Co Vo
    Tuong, the hop mach mechanism, or Ta Van Khanh's responsibility --
    the narration hints ("a sealing order was signed", "records were
    erased") without naming anyone;
  - the final line is Ly An's canonical CIN_001_S05 line, version B.
    It REUSES the checkpoint 04 take byte-for-byte (same voice, same
    line) instead of re-synthesizing a near-duplicate; the reuse is
    recorded in the manifest.

Voices are fictional TTS (no real-voice cloning, no unlicensed
samples): narrator = avocado_v2:MAI_03 (Helio) as a DRAFT casting --
the narrator is a new role and final casting is a director decision.
Outputs mirror the checkpoint 04/17 layout:
  Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT/ (WAV masters + raw MP3)
  ClientGodot/assets/audio/vo/prologue/    (runtime WAV copies)
  Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json
All durations/loudness are measured from the real rendered bytes
(ffprobe + ffmpeg loudnorm, the checkpoint 07 method).
"""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_DRAFT"
RT_DIR = ROOT / "ClientGodot/assets/audio/vo/prologue"
MANIFEST = ROOT / "Art_Source/Audio/Muse/VO/PROLOGUE_VO_manifest_v1.json"
LYAN_SRC = (ROOT / "Art_Source/Audio/Muse/VO/P0_DRAFT"
            / "VO_CIN001_S05_LYAN_draft_v1.wav")
TTS = "/opt/hatch/bin/tts"
NARRATOR_VOICE = "avocado_v2:MAI_03"

SEGMENTS = [
    ("SEG01", "Xưa, Lạc Châu sống nhờ năm dòng mạch chảy dưới lòng đất "
              "và mặt nước. Năm mạch trao nhau dòng chảy qua một cơ chế "
              "điều hòa gọi là Huyền Ấn — và năm ngọn tháp canh giữ sự "
              "trao đổi ấy, để không vùng nào thừa nước, không vùng nào "
              "cạn khô."),
    ("SEG02", "Ba trăm năm trước, một cơn địa chấn phá vỡ cơ chế điều "
              "hòa. Để ngăn thảm họa, người ta tách năm tháp ra khỏi "
              "nhau. Thảm họa qua đi — nhưng từ đó, điều tiết dần biến "
              "thành sở hữu. Mỗi tháp giữ mạch của mình, và giữ cả "
              "những danh sách ghi tên người sống dưới mạch ấy."),
    ("SEG03", "Ba mươi năm trước, hạn hán và lũ lụt nối nhau tràn qua "
              "một vùng quê. Trong cơn tuyệt vọng, người ta thử nối "
              "các mạch lại làm một. Thí nghiệm vỡ. Một phần thành phố "
              "chìm xuống nước — và nhiều người còn sống bị ghi vào sổ "
              "là đã chết. Một lệnh phong tỏa được ký. Rồi hồ sơ bị "
              "xóa dần, như thể chưa từng có ai ở đó."),
    ("SEG04", "Ngày nay, dòng chảy ở Lạc Châu không còn đi đúng đường. "
              "Có tiếng chuông ngân dưới mặt nước, ở nơi không hề treo "
              "chuông. Có những cái tên bị mất khỏi danh sách. Và vẫn "
              "còn những lá thư — niêm sáp năm vạch — đi qua các tuyến "
              "đường thủy, chờ người nhận chịu mở."),
    ("SEG05", "Bến Mưa là một bến đò nhỏ nơi các tuyến ấy giao nhau. "
              "Mưa không ngớt. Và hôm nay, một người khách lạ vừa "
              "bước lên bến..."),
]


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {cmd}\n{r.stderr[-1200:]}")
    return r


def probe_duration(path: Path) -> float:
    out = run(["ffprobe", "-v", "error", "-show_entries",
               "format=duration", "-of", "json", str(path)]).stdout
    return float(json.loads(out)["format"]["duration"])


def loudnorm(path: Path):
    r = subprocess.run(["ffmpeg", "-i", str(path), "-af",
                        "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    err = r.stderr
    start = err.rfind("{")
    data = json.loads(err[start:err.rfind("}") + 1])
    return float(data["input_i"]), float(data["input_tp"])


def synth(seg_id: str, text: str) -> dict:
    mp3 = SRC_DIR / f"VO_CIN000_{seg_id}_NARRATOR_raw.mp3"
    wav = SRC_DIR / f"VO_CIN000_{seg_id}_NARRATOR.wav"
    SRC_DIR.mkdir(parents=True, exist_ok=True)
    if not wav.exists():
        run([TTS, "speak", "--voice", NARRATOR_VOICE, "--language",
             "vi", "--output", str(mp3), "--text-stdin"],
            input=text)
        run(["ffmpeg", "-y", "-v", "error", "-i", str(mp3),
             "-ar", "48000", "-ac", "1", "-c:a", "pcm_s16le",
             str(wav)])
    dur = probe_duration(wav)
    lufs, tp = loudnorm(wav)
    RT_DIR.mkdir(parents=True, exist_ok=True)
    rt = RT_DIR / wav.name
    shutil.copyfile(wav, rt)
    assert sha256_file(rt) == sha256_file(wav)
    return {
        "takeId": f"VO_CIN000_{seg_id}",
        "speaker": "NARRATOR",
        "voice": NARRATOR_VOICE,
        "castingStatus": "DRAFT_CASTING_DIRECTOR_DECISION_PENDING",
        "text": text,
        "file": wav.name,
        "rawMp3": mp3.name,
        "runtimePath": f"assets/audio/vo/prologue/{wav.name}",
        "durationSeconds": round(dur, 4),
        "integratedLufs": round(lufs, 2),
        "truePeakDbtp": round(tp, 2),
        "sha256": sha256_file(wav),
        "assetState": "DRAFT_NOT_FINAL_VO",
    }


def main() -> int:
    takes = []
    for seg_id, text in SEGMENTS:
        entry = synth(seg_id, text)
        takes.append(entry)
        print(f"OK {entry['takeId']}: {entry['durationSeconds']} s, "
              f"{entry['integratedLufs']} LUFS / {entry['truePeakDbtp']}"
              f" dBTP", flush=True)
    assert LYAN_SRC.exists(), f"missing CP04 Ly An take {LYAN_SRC}"
    dur = probe_duration(LYAN_SRC)
    lufs, tp = loudnorm(LYAN_SRC)
    ly = {
        "takeId": "VO_CIN001_S05_LYAN (reused)",
        "speaker": "NPC_LYAN",
        "voice": "avocado_v2:MAI_01",
        "text": "Đầu kia! Giữ giúp tôi đầu kia!",
        "reuse": "Byte-identical reuse of the checkpoint 04 canonical "
                 "take (CIN_001_S05, version B, DEC-MEDIA-P0 Q1); the "
                 "prologue ends on the same voice the game opens "
                 "with. Source: Art_Source/Audio/Muse/VO/P0_DRAFT/"
                 "VO_CIN001_S05_LYAN_draft_v1.wav",
        "durationSeconds": round(dur, 4),
        "integratedLufs": round(lufs, 2),
        "truePeakDbtp": round(tp, 2),
        "sha256": sha256_file(LYAN_SRC),
        "assetState": "DRAFT_NOT_FINAL_VO",
    }
    total = sum(t["durationSeconds"] for t in takes)
    manifest = {
        "manifestId": "NGM_PROLOGUE_VO_V1",
        "checkpoint": "MEDIA-02 checkpoint 27 - prologue CIN_000 "
                      "narration VO drafts",
        "decisionId": "DEC-MEDIA-P0-20261105",
        "branch": "muse/media-production-20261104",
        "scriptApproval": "Owner approved the narration script in "
                          "main chat 2026-11-06 (option 'Duyệt kịch "
                          "bản — sản xuất luôn')",
        "canonGuardrails": [
            "No avatar origin/name/face; no secret bloodline "
            "(STORY_DECISIONS_V3).",
            "No naming of Co Vo Tuong, the hop mach mechanism, or Ta "
            "Van Khanh's responsibility (reveal table, Narrative "
            "Depth section 3).",
            "Final line is the canonical CIN_001_S05 version B line, "
            "reused from checkpoint 04.",
        ],
        "segments": takes,
        "finalLine": ly,
        "narrationTotalSeconds": round(total, 4),
        "notes": [
            "Draft VO only: fictional TTS voices, no ear audition, "
            "pronunciation not yet reviewed by a native listener.",
            "Segment durations are measured from real bytes; the "
            "film builder derives shot windows from them.",
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False,
                                   indent=1) + "\n", encoding="utf-8")
    print(f"\nnarration total: {total:.2f} s across {len(takes)} "
          f"segments; manifest written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
