# MEDIA-02 Checkpoint — WO37 M-B CP4: standard 720p re-rendered with the M-F CP2 draft v2 mixes

Date: 2026-11-13 (JST). Branch: `muse/media-production-20261104`.
Baseline: `7f461da`. Content commit: `21bc9ef386bec6cbd823a9dff564df03ee3534d4`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — review masters for Codex;
no runtime file, mix, or casting decision is changed here.

## What was delivered

The M-B CP2 standard 720p set (2026-11-10) stream-copied its audio
bit-exact from the 640×360 runtime masters, which still embed the v1
mixes. M-F CP2 (2026-11-12) then delivered draft v2 mixes for 14 of
the 21 playback entries (new voice palette; prologue plumbing fixed,
narration History). This checkpoint re-renders exactly those 14
entries so the standard review set carries the CURRENT draft mixes:

| Scene | Mix | LUFS | TP | 720p bytes (CP2 → CP4) |
|---|---|---|---|---|
| CIN_000 | DRAFT_V2 (History) | -21.75 | -1.98 | 33,875,842 → 33,892,413 |
| CIN_002 | P0_DRAFT_V4 | -26.28 | -2.93 | 733,937 → 733,257 |
| CIN_006 | DRAFT_V2 | -23.69 | -6.71 | 7,498,383 → 7,498,252 |
| CIN_008 | DRAFT_V2 | -26.07 | -4.88 | 5,406,160 → 5,407,246 |
| CIN_010 | DRAFT_V2 | -26.20 | -8.70 | 7,706,106 → 7,706,783 |
| CIN_011 | DRAFT_V2 | -24.32 | -6.54 | 7,396,926 → 7,395,664 |
| CIN_012 | DRAFT_V2 | -26.00 | -5.83 | 5,258,730 → 5,251,606 |
| CIN_013 | DRAFT_V2 | -24.51 | -3.68 | 5,975,116 → 5,975,344 |
| CIN_014 | DRAFT_V2 | -26.16 | -5.65 | 6,507,298 → 6,507,762 |
| CIN_015 | DRAFT_V2 | -25.33 | -5.81 | 5,499,750 → 5,499,788 |
| CIN_016 | DRAFT_V2 | -25.40 | -6.54 | 4,758,573 → 4,757,887 |
| CIN_017 | DRAFT_V2 | -25.95 | -5.92 | 6,020,830 → 6,021,331 |
| CIN_018 | DRAFT_V2 | -22.97 | -4.71 | 5,876,734 → 5,876,287 |
| CIN_020 | DRAFT_V2 | -25.97 | -9.61 | 7,404,050 → 7,403,304 |

The other 7 entries (CIN_001/003/004/005/007/009/019) have no v2 mix —
their v1 audio is unchanged — so their CP2 files are carried over
byte-identical (verified via their committed LFS oids, not re-rendered,
not re-downloaded).

**Method — disclosed, same as CP2 for picture:** integer 2×
nearest-neighbour upscale of the delivered 640×360 runtime master
(picture of record; P0 scenes keep the runtime A picture, candidate B
keeps its own M38-A/B package). Video: H.264 crf26 preset medium,
yuv420p, +faststart. Audio: from the v2 mix WAV master, encoded AAC
192k 48 kHz stereo to match the nominal bitrate of the v1 embedded AAC
track (runtime masters probe ~192 kbps). It is a re-encode, NOT a
stream copy, so the checker verifies it by measurement (loudnorm +
lag-tolerant waveform correlation vs the v2 WAV) instead of byte
equality. This set is NOT a native 720p capture and is labelled as
such in the manifest, same as CP2.

## Budget (measured from real bytes)

- MP4 standard set: **21 files, 148,002,469 B** vs 147,993,980 B at CP2
  → **+8,489 B** (the v2 audio re-encode is ~the same size as the v1
  stream copy; the 14 re-rendered files total 109,926,924 B vs
  109,918,435 B at CP2). Ratio vs the 640 masters stays 3.388×.
- No OGV re-render: the 3 CP2 OGV samples are all v1-only scenes
  (CIN_001/003/019); the full OGV standard set stays deferred per
  Gói 39 (Codex budget decision).

## Validation

Checker `check_standard720_mb_cp4_v1.py`: **PASS 271/271, 0 failures**
(`MEDIA02_WO37_MB_CP4_VALIDATION_20261110.json`). Per re-rendered
entry: video source sha == manifest, CP2 manifest and git LFS oid; v2
mix WAV sha == manifest and M-F CP2 validation (PASS 369/369); output
sha/bytes == manifest; probe 1280×720 @30fps with AAC audio; duration
delta ≤ 0.06 s (all exact: 18.000 / 87.367); frames at 3 timestamps
downscale back to the master with worst mean|diff| **4.215** and worst
2×2 intra-block range **6.07** across all 14 (CP2 measured 4.215 /
6.08 — the video encode is essentially identical); audio decoded from
the output AAC correlates with the v2 mix WAV at **≥ 0.9998** (lag 0
on all 14 — no AAC priming shift survived the mux), loudnorm
integrated LUFS within **0.04** and true peak within **0.10 dBTP** of
the v2 mix values; budget arithmetic re-derived; git status clean
under `ClientGodot/` (runtime untouched).

One in-build fix, recorded per standing rule: the checker's first run
crashed parsing loudnorm output — ffmpeg 8.1.2 prints a muxing
summary line AFTER the JSON block, so `json.loads` from the last `{`
fails with "Extra data". The parser now brace-matches the JSON object
instead. No repo bytes were affected (the fix is in the checker only,
before any commit).

## Scope audit

- Block (7f461da → content 21bc9ef): **17 paths / 0 violations**
  (14 re-rendered MP4s + manifest + builder + checker).
- Cumulative vs merge-base `cf17178` at the content commit:
  **2365 paths / 1 violation** — the single `.gitattributes`
  violation is the known merge-base artifact (byte-identical with
  integration `f3db6b3`, verified by sha256 this run), not a new
  breach. Note the count: 2362 at head 7f461da + 3 truly new paths
  (manifest + 2 tools) = 2365 — the 14 re-rendered MP4s are
  modifications of paths already in the cumulative diff, so they add
  0. The report commit adds exactly 2 files (this report +
  validation JSON), so the head count is 2367 paths / 181 commits.

## Limits / notes

- DRAFT standard versions of DRAFT mixes; final picture remains
  character-lock-blocked for the locked shots — this set will be
  re-rendered from final masters, it does not pre-empt them.
- CIN_000's subtitled variant (M-B CP3) is NOT re-rendered here: its
  burned-in subtitles are timed to the v1 narration; re-muxing v2
  audio under them would misalign subtitles vs narration. Subtitle
  re-timing to the v2 narration is a separate follow-up.
- Nothing was listened to or watched by ear/eye beyond the numeric
  frame and audio checks; all 14 mixes remain DRAFT_NOT_FINAL and
  NOT_AUDITIONED. The ear verdict belongs to the listener, runtime
  adoption to Codex.
- Issue #116 re-checked this run (public API): still 31 comments,
  latest Muse ACK 6831053345 (M-F CP2 + M-G CP8 + M-D CP10, posted
  2026-11-13 ~02:32 JST). No new Codex/owner direction since Gói 39
  (6815238814).

## Files

- Tools: `Tools/MediaProduction/Muse/build_standard720_mb_cp4.py`,
  `Tools/MediaProduction/Muse/check_standard720_mb_cp4_v1.py`.
- Media: `Art_Source/Cinematics/Standard720/` — 14 MP4 re-rendered
  (109,926,924 B); 7 CP2 files carried over byte-identical.
- Manifest + this report + validation JSON.

## Next

Post the CP4 delta with the next PR #119 / issue #116 handoff (owner
tap; the main thread owns posting — this run does not post). Otherwise
the standing blocks remain: 32 shots motion wait on character lock;
prologue v1 re-render (plumbing-fixed, narration Helio) waits on the
owner/Codex decision; SFX has no new composition approval (18/18
drafts done); full OGV 720p set deferred per Gói 39. PR #119 stays
HOLD; Muse does not self-merge.
