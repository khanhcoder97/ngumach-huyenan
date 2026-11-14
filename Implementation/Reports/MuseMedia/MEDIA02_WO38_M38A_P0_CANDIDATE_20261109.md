# MEDIA-02 — WO38 M38-A: P0 candidate for real review

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Baseline: `14b588c663a6d53295b34f1d632e84c48c7f5ca9` (the pin Codex audited
on Windows). Direction: Gói 38 / Work Order 38 (issue #116 comment
6733227370; PR #130, integration `9ac73dc`). PR #119 stays HOLD; Muse
does not self-merge. Production OFF.

Status: **DRAFT_CANDIDATE_FOR_CODEX_REVIEW** — not final animation,
**NOT_AUDITIONED**, and the runtime package is **not** modified.

## What was delivered

One P0 candidate assembled from the existing WO37 M-C CP2 motion A/B
deliverables, packaged so Codex can watch, listen and judge it without
digging through the checkpoint history:

- **Combined review reel (new):**
  `Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_review_72s_640x360_30fps.mp4`
  — 72.021 s, 640×360, 30 fps, H.264 + AAC 48 kHz stereo, stream-copy
  concatenation of the three candidate scene takes.
  sha256 `a9ae424cd95de09899dfd8bcff40a1ca572f571f7043d3259e10f14c0110780c`, 2,989,770 B.
- **Combined contact sheet (new):**
  `Art_Source/Cinematics/P0_Motion/candidate_m38a/P0_candidate_contact_all12.png`
  — all 12 shots × 5 poses, labelled, 1920×720.
  sha256 `916dbeb4d8d660435f3ec91a4a24889acb1d878debbde7d837efed5358d68739`, 866,130 B.
- **Subset manifest + source closure:**
  `Implementation/Content/Narrative/Deliveries/P0_CANDIDATE_M38A_SUBSET_v1.json`
  — 32 candidate files with sha256/bytes/role; source closure of
  12 keyframes, 3 timing files, 6 SRT files, 8 VO source files,
  3 mix manifests (v1/v2/v3) and 3 builder tools; 9 runtime-proof
  hashes (see "Runtime untouched").
- Per-scene candidate takes and A/B comparison videos are the CP2
  files, referenced in place (not copied):
  `Art_Source/Cinematics/P0_Motion/takes/CIN_001_pose_640x360_30fps.mp4`
  (36 s, sha `e244b152…`), `…/CIN_002_pose_…` (18 s, sha `822a32d7…`),
  `…/CIN_004_pose_…` (18 s, sha `15e1b8d1…`), and
  `Art_Source/Cinematics/P0_Motion/ab/CIN_00X_ab_kenburns_vs_pose_640x720_30fps.mp4`.

## Candidate definition and selection rationale

- **Video = B takes.** A is the currently shipped runtime take:
  storyboard panels with panel-hold/Ken Burns and no action beat.
  B adds one 5-pose action beat per shot at 10 pose/s (each pose held
  3 frames at 30 fps), rendered procedurally from the storyboard
  keyframes. B is the only version that answers WO37 M-C's rule that
  Ken Burns is not final pose animation, and the three dialogue beats
  start exactly at the locked dialogue-window heads (24.8 s / 7.0 s /
  7.5 s — see table). A stays in place as the runtime take and as the
  fallback until Codex adopts or rejects B; nothing was swapped.
- **Audio = P0 draft mix v3, embedded.** v3 is the fully composed
  chain (composed music + composed ambience + draft VO,
  sidechain-ducked), so the candidate's audio provenance is
  single-source and license-clean — no ported PackV1 stems anywhere
  in it. Loudness re-measured from the WAV masters for this package:
  CIN_001 −21.06 LUFS / −1.66 dBTP; CIN_002 −22.67 / −4.25;
  CIN_004 −26.78 / −8.27. v1 (ported stems) and v2 (composed music +
  ported ambience) remain delivered alternates under
  `ClientGodot/assets/audio/mix/p0/` and `…/p0_v2/`; choosing among
  them stays Codex's adapter decision.
- **What this candidate is not:** not final acting (procedural
  multi-pose from storyboard keyframes, unreviewed), not auditioned,
  not a runtime change.

## Timing / camera / pose notes (12 shots)

Beat = 5 poses at 10 pose/s (0.5 s). Diff values are mean absolute
channel differences from the CP2 manifest, re-verified at this
checkpoint. Dialogue beats start at the window head in all 3 cases.

| Shot | Camera | Beat (scene s) | Mean inter-pose diff | Last pose vs keyframe | Notes |
|---|---|---|---|---|---|
| CIN_001_S01 | WIDE_STATIC | 2.0–2.5 | 0.734 | 0.438 | rain/ambience beat |
| CIN_001_S02 | DETAIL_LOCKED | 2.0–2.5 | 1.502 | 0.388 | |
| CIN_001_S03 | DETAIL_LOCKED | 2.0–2.5 | 0.498 | 0.473 | gentlest beat |
| CIN_001_S04 | DETAIL_LOCKED | 2.0–2.5 | 0.503 | 0.486 | |
| CIN_001_S05 | MEDIUM_STATIC | 24.8–25.3 | 2.493 | 5.534 | Ly An dialogue, window 24.8–28.5 **DECIDED version B** "Đầu kia! Giữ giúp tôi đầu kia!"; character lock required |
| CIN_001_S06 | TOPDOWN_MATCH | 32.0–32.5 | 1.813 | 0.000 | sway returns exactly to rest (first/last pose = keyframe); Ly An visible, lock required |
| CIN_002_S01 | GROUND_DETAIL | 2.0–2.5 | 1.054 | 0.691 | |
| CIN_002_S02 | MEDIUM_STATIC | 7.0–7.5 | 1.611 | 3.388 | Tạ Vân Khanh dialogue, window 7.0–11.0 "Trên bờ chỉ nghe nửa tiếng. Phần còn lại ở dưới ấy."; hand lowers only 4 px — guardrail: the uninjured hand never touches the water; lock required |
| CIN_002_S03 | TOPDOWN_MATCH | 14.0–14.5 | 1.487 | 0.129 | |
| CIN_004_S01 | WIDE_STATIC | 2.0–2.5 | 2.896 | 6.391 | BOSS_MANG_COT; guardrail kept: exactly one broken horn + one whole horn; lock required |
| CIN_004_S02 | DETAIL_LOCKED | 7.5–8.0 | 10.890 | 25.588 | strongest beat (under the 30 review threshold); Ly An speaks **off-screen** (DEC Q2) — only the boss is in frame; lock required |
| CIN_004_S03 | TOPDOWN_MATCH | 14.0–14.5 | 7.718 | 9.701 | boss; lock required |

## Audio routing

- **EMBEDDED_SOUNDTRACK_ONLY**, consistent with
  `PLAYBACK_METADATA_v1.json`: play only the soundtrack embedded in
  the candidate clip (AAC, from the v3 WAV masters listed in the
  subset manifest). Never play a standalone mix WAV or VO take at
  the same time — they are the same mix delivered separately.
- Subtitles are the external SRT files (`CIN_00X_vi.srt`, UTF-8),
  not baked into the candidate video; no double captions.
- Alternates **not** in this candidate: P0 mixes v1 and v2; the M-F
  CP1 palette pickup VO takes (alternate casting — the candidate
  keeps the original draft VO; the Tạ Vân Khanh line still uses the
  shared male draft voice, the known CP04 casting limit).
- Fallback if B is rejected: the current runtime A takes + posters,
  untouched (below).

## Runtime untouched

The candidate lives entirely in `Art_Source/` + Deliveries + Reports
+ Tools. The subset manifest records sha256 for the 9 current runtime
files of the three scenes (MP4/OGV/poster); the checker re-hashed
them and `git status` over `ClientGodot/assets/cinematics` and
`ClientGodot/assets/audio` shows no tracked modification.

## Validation

- Builder re-hashed **every** CP2/ledger-referenced file (3 scene
  takes, 3 mix WAVs, 12 shot takes, 3 A/B videos, 12 contact sheets,
  60 pose frames, 12 keyframes) against the CP2 manifest and the
  motion ledger — all match.
- Independent checker `check_p0_candidate_m38a_v1.py`: **11/11 PASS,
  0 failures** (hashes of all 80 subset entries; ffprobe facts for
  the reel, the 3 scene takes and the 3 A/B videos; contact-sheet
  geometry; SRT windows vs notes incl. beat-at-window-head; runtime
  trees unmodified). Record:
  `MEDIA02_WO38_M38A_VALIDATION_20261109.json`.
- Scope audit: content commit **5 paths / 0 violations** (7 paths
  total including this report); cumulative from merge-base `cf17178`
  **2130 paths / 1 violation** at this head — the known
  `.gitattributes` merge-base artifact (byte-identical with
  integration). Content commit
  `9a7722709f4e1942ad5e14e2b500dbdabb7ec432`.
- Provenance note: this package was built in a separate worktree on
  baseline `14b588c` (the 14:40 scheduled run held the shared clone
  with its M-G CP6 commits) and rebased onto the M-G CP6 head
  `cdbab7c` before push; the checker was re-run after the rebase —
  still 11/11 PASS.

## Limits

- DRAFT pose animation: procedural, from storyboard-level keyframes;
  6 of 12 shots still require the character lock for final picture.
- NOT_AUDITIONED: nobody has listened to this candidate; the Ly An
  CIN_001_S05 take is the known hot take (−16.01 LUFS measured at
  CP33) sitting at unity inside the v3 mix.
- 640×360 only, as per the locked P0 review standard; no 720p
  variant in this package.
- The generated-strip route stays rejected (8 strips, CP2 record);
  0 generated pixels in the takes.

## Next

M38-B: selective P0 runtime ingest guide (subset manifest for the
runtime subset + embedded-vs-external single-audio-path guidance,
cues/subtitles/seams/fallback, license/provenance) — separate block.
