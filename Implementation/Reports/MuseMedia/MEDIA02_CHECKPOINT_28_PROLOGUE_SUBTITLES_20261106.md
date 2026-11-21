# MEDIA-02 Checkpoint 28 — Prologue CIN_000 subtitled viewing variant

Date: 2026-11-06 · Branch: `muse/media-production-20261104` · Base integration: `f0859d0`
Content commit: `a662218`

## Owner request

After watching the checkpoint 27 prologue, the owner reported that
the film had no accompanying subtitles for viewers to read and
follow the story/background, and that voiceover still needed to be
added to the video.

Verification against the delivered bytes, before changing anything:

- The checkpoint 27 MP4 **does** carry its narration mix embedded
  (AAC stereo, measured −20.81 LUFS / −9.08 dBTP) — but at that
  level the voice sits low for casual laptop/phone playback, and a
  muted or audio-less preview shows nothing at all.
- The film had **no subtitle stream and no burned-in subtitles**.
  The only subtitles were the sidecar SRT, whose 6 cues run up to
  ~20 s each with paragraph-length text — not readable on screen
  as-is.

## What this checkpoint delivers

A **viewing variant** of the same film, registered in the scene
export manifest as `mp4SubVi` and carried into the runtime
cinematics manifest's `prologue` key. The canonical CP27 files
(MP4 `88049317`, OGV `f7323bcf`, canonical SRT, mix) are
**unchanged**.

**`CIN_000_640x360_30fps_sub_vi.mp4`** — sha `2aae25e4`,
11,918,592 bytes, video stream 87.2667 s, streams in order
video (H.264) + audio (AAC) + subtitle (mov_text):

- **Burned-in Vietnamese subtitles** (libass, DejaVu Sans bold,
  white on a semi-transparent black box, bottom center), so the
  text is visible in every player, including chat previews that
  ignore subtitle tracks.
- **An embedded mov_text subtitle track** (language vie, default
  disposition) carrying the same cues for players that prefer
  soft subtitles.
- **Narration at +5.0 dB flat presentation gain** over the CP27
  embedded mix (no dynamics change). Measured on the variant file
  from real bytes: **−15.83 LUFS / −4.09 dBTP** (canonical files
  keep the CP27 mix at −20.81 LUFS).

**`CIN_000_vi_readable.srt`** — sha `762b8669`, the subtitle source
for both the burn-in and the embedded track: the canonical 6 cues
split into **26 readable chunks** by tool
`Tools/MediaProduction/Muse/build_prologue_subtitled.py` —
sentence splits first, then clause splits at ≤82 characters;
timing proportional to character count inside each canonical cue
window, with a 1.2 s minimum display per chunk redistributed
inside the cue (the dramatic short sentence "Thí nghiệm vỡ."
gets its full 1.2 s); the one canonical overlap (cue 3 end
55.419 s vs cue 4 start 55.133 s) is resolved by shifting cue 4's
chunks +0.336 s so the sequence is monotonic. The concatenated
chunk text is verified **identical** to the canonical SRT text
(whitespace-normalized): a presentation split, not an edit. Ly
An's closing line displays as two beats — "Đầu kia!" / "Giữ giúp
tôi đầu kia!".

## QA (from real bytes)

- ffprobe: stream layout exactly [video, audio, subtitle];
  duration matches the canonical film's video stream.
- The embedded mov_text track was extracted back to SRT and
  compared cue-by-cue with the readable SRT: 26/26 cues, text and
  timing (±0.05 s) identical.
- Frame grabs inspected by eye: 6.0 s (opening cue, two lines,
  correct Vietnamese diacritics), 45.0 s ("Thí nghiệm vỡ."),
  82.2 s ("Giữ giúp tôi đầu kia!" over the arrival shot), 85.8 s
  (title card — correctly carries no subtitle).
- `build_runtime_delivery.py` re-run: ALL VERIFIED (section 6c
  verifies the variant's sha/size/duration/stream layout and the
  readable SRT); runtime audio manifest regenerates byte-identical
  (589 files — no audio registration changes).
- Source re-validation: **PASS, 0 mismatches** (audio files
  checked 1125; prologue files checked 45).
  `MEDIA02_CHECKPOINT_28_SOURCE_REVALIDATION_20261106.json`
- Runtime re-verify: **PASS, 0 mismatches** (589 audio files;
  prologue files checked 7 — the CP27 five plus the variant MP4
  and the readable SRT).
  `MEDIA02_CHECKPOINT_28_RUNTIME_REVERIFY_20261106.json`
- Scope audit: **1110 changed paths, 0 violations** vs integration
  `f0859d0` (1109 at the content commit + this report).

## Limits

- This is a **viewing variant**, not a new cut: picture, timing,
  narration takes and mix balance are the CP27 ones. The +5 dB is
  a flat presentation gain on the variant only.
- The narration remains **DRAFT TTS** (narrator casting is a
  director decision) and the mix remains **DRAFT_MIX_NOT_FINAL**;
  **no ear audition** has been done — the loudness figures above
  are measurements, not a listening verdict.
- Burned-in subtitle font is DejaVu Sans — the project has no
  locked Vietnamese display font (same placeholder status as the
  CP27 title card).
- No OGV subtitled variant: in-engine subtitle display belongs to
  the presentation adapter (Codex); the readable SRT ships beside
  the film files for that use.
- CP27's recorded picture revision items (S01↔S03 mechanism
  drift, S11 arrival direction, S10 seal grooves, …) are
  unchanged by this checkpoint.
