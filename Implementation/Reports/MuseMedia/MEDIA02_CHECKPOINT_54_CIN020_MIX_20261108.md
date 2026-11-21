# MEDIA-02 Checkpoint 54 — CIN_020 Draft Mix v1 (Work Order 37, M-B big checkpoint 1 COMPLETE)

Date: 2026-11-08 (JST). Branch: `muse/media-production-20261104`.
Produced by the MAIN THREAD on the owner's direct order ("hãy làm
đi", 2026-11-08 18:42 JST), following checkpoint 53 in the same
session. Integration baseline: `6f79853`. PR #119 stays HOLD;
Muse does not self-merge. Production OFF.

## What was delivered

The seventeenth per-scene draft mix: **CIN_020 "Thư có hồi âm"**
(quest SQ-DM-05, the closing campaign scene), built with the P0
v3 recipe (fully composed stems, VO at unity, sidechain ducking
threshold 0.03 / ratio 4 / attack 15 ms / release 350 ms, peak
guard −1.0 dBTP, 1 s acrossfade ambience loop join), embedded
into the runtime OGV + review MP4 (video streams copied
bit-for-bit).

**With this mix, every one of the 21 cinematics entries carries
an embedded soundtrack (21 embedded / 0 silent) — Work Order 37
M-B big checkpoint 1 is complete.** (P0 alternate v1/v2 mixes are
kept as standalone alternates, not deleted; the alpha candidate
remains P0 v3 fully-composed + CIN_006 v1 per WO37.)

New tool: `Tools/MediaProduction/Muse/build_cin020_mix_v1.py`
(cloned from the CP51 builder; all mixing code identical, only
scene constants, docstring and manifest prose are new).

## Mix measurements (from the real rendered bytes)

- Mix WAV `Art_Source/Audio/Muse/MIX/CIN020_DRAFT_V1/CIN_020_mix_draft_v1.wav`
  sha256 `90b51db920c68ca516c92510c9e706c87d9079136d41dbbc48f9b9262e60ba8f`,
  3,456,100 bytes, 18.000 s, pcm_s16le 48 kHz stereo:
  **−23.41 LUFS / −5.22 dBTP, LRA 10.10**, peak trim 0.0 dB.
- Stems (PROPOSED_CANDIDATE, new assignment; the CP02 table
  assigns nothing to CIN_020): composed **MUSIC/ben_mua**
  (−21.93 LUFS re-measured = pack) ducked by VO; composed
  **AMBIENCE/river_shore** (−29.69) unducked; composed
  **SFX/CINEMA/reveal** (−24.96) at 6.0 s (S02 start,
  PROPOSED_PENDING_PICTURE_LOCK). ben_mua is the rain-quay
  leitmotif of the opening where the sealed letter changed
  hands, back for the closing scene where the letter is
  answered at the same river — third scene-mix use (CIN_003,
  CIN_014); river_shore is a fourth use (CIN_003, CIN_008,
  CIN_019). rift_finale was passed over: its full close was
  spent at CIN_019's resolution; this scene is the quiet
  morning after, not a second climax.
- VO (CP17 draft, Người nhận thư): take 3.000 s placed at
  12.5 s, runs 12.5–15.500 s, **FITS window [12.5, 17.5] by
  2.000 s**; no overrun, no tail trim; window/take/timing
  unchanged. Take loudness −19.59 LUFS (re-verified from real
  bytes this run), kept at unity per the recipe.
- Ducking (CP39 full-window method): **−5.25 dB** in-window,
  0.0 dB outside — a real cut (ben_mua segment RMS −20.5 dBFS
  in the window, measured from the stem bytes this run).
- Ambience loop join (river_shore @15.5 s): maxJump 0.00154,
  ratio 0.58 vs the bed's own p999 (same bed and join point as
  CIN_019 — same values, as expected).
- Embedded re-measurement after mux: OGV **−23.37 LUFS /
  −5.22 dBTP** (Vorbis 160k), MP4 **−23.42 / −5.20** (AAC
  192k); video streams bit-identical (pack builder verified).

## Casting + staging notes (NOT mix defects)

- **Casting:** the recipient's voice is a placeholder role
  voice (CP17 `VOICE_LETTER_RECIPIENT`; recipient
  identity/gender undecided) and the draft take uses the same
  fictional system voice as Ly An's drafts (avocado_v2:MAI_01)
  — a draft-casting collision for the WO37 M-F VO palette work
  to resolve with a distinct voice. Not a mix decision.
- **Staging:** the timing records the S03 dialogue
  `onscreen: null`. The S03 keyframe shows the villager seated
  at frame left **seen from behind** (top-down match frame) —
  the speaker is present in the frame but his face is not
  visible; the line reads as an on-set voice from behind. The
  CP24 keyframe manifest also records that this unnamed
  villager's appearance **drifts between all three shots**
  (S01 headband + brown vest; S02 conical hat + blue tunic;
  S03 green top + dark headwrap) — the scene's pack character
  list is empty, so no named character lock exists for him.
  Final-picture/casting matters for Codex/director; the mix
  did not move the VO.

## Tables and runtime state re-run

- `PLAYBACK_METADATA_v1.json`: **21 embedded / 0 silent**;
  CIN_020 ownership EMBEDDED_SOUNDTRACK_ONLY, runtime = clean
  video + overlay SRT (builder verdict PASS).
- `PRONUNCIATION_TABLE_v1.json`: **27 cue rows, 23 seam rows
  (no new row — ben_mua + river_shore were already measured at
  CIN_003; flagged stays 1 — MUSIC/sa_hoa 0.016015), 21
  fallback rows, 176 files verified**. The no-mix fallback
  rule now reads as the terminal fallback only (missing/corrupt
  embedded file). Names unchanged (16 names, 4 spoken, only
  Tạ Vân Khanh DECIDED); CIN_020's line speaks no proper name.
- Runtime audio **626 → 627** (mix 29 → 30); runtime pack
  **20 → 21 scenes** (all entries).
- Validators: source re-validation PASS, 0 mismatches
  (`MEDIA02_CHECKPOINT_54_SOURCE_REVALIDATION_20261108.json`);
  runtime re-verify PASS, 0 mismatches
  (`MEDIA02_CHECKPOINT_54_RUNTIME_REVERIFY_20261108.json`).
  The CP53 ordering lesson was applied (pack mux before
  `build_runtime_delivery.py`), and both validations passed on
  the first run.
- Scope audit: content-only 18 paths / 0 violations; cumulative
  vs integration `6f79853` carries the 1 known `.gitattributes`
  violation — a merge-base artifact (the checker diffs from
  cf17178; the file is byte-identical to integration), not a
  new breach. Historical reports' records are not edited.

## Limits

DRAFT_MIX_NOT_FINAL; NOT_AUDITIONED (no ear audition of this
mix or its VO take); stem assignment and stinger placement
PROPOSED pending Codex review / picture lock; final picture
character-lock-blocked (storyboard keyframes, Ken Burns motion
— not final pose animation). Loudness figures are measurements,
not a listening PASS. The three kept overruns (CIN_005_S03
+0.160 s, CIN_018_S03 +0.280 s, CIN_006_S03 +0.520 s) are
unchanged, per the owner's verdict.

## Next

WO37 big checkpoint 2: P0 motion/final-picture revisions for
ref-sufficient shots (per the M-C 63-shot ledger delivered by
the hourly run at `da1b7d5`/`6d882b9`: 38 action-animation
candidates — 12 P0 + 26 ref-sufficient; 25 Ken Burns hold) +
soundtrack A/B. Then M-D whole-game score/transitions, M-E
SFX/ambience variants, M-F VO palette/pickups (including a
distinct voice for the letter recipient).
