# MEDIA-02 Checkpoint 53 — CIN_019 Draft Mix v1 (Work Order 37, M-B big checkpoint 1)

Date: 2026-11-08 (JST). Branch: `muse/media-production-20261104`.
Produced by the MAIN THREAD on the owner's direct order ("hãy làm đi",
2026-11-08 18:42 JST), in parallel with the hourly run's WO37 M-C
motion-ledger block (separate files, separate checkpoint).
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

The sixteenth per-scene draft mix: **CIN_019 "Năm mạch, không một
chủ nhân"** (quest C6-05, the campaign's resolution scene), built
with the P0 v3 recipe (fully composed stems, VO at unity, sidechain
ducking threshold 0.03 / ratio 4 / attack 15 ms / release 350 ms,
peak guard −1.0 dBTP, 1 s acrossfade ambience loop join), embedded
into the runtime OGV + review MP4 (video streams copied
bit-for-bit). **20 of 21 entries now carry an embedded soundtrack;
1 silent scene remains (CIN_020).**

New tool: `Tools/MediaProduction/Muse/build_cin019_mix_v1.py`
(cloned from the CP51 builder; all mixing code identical, only
scene constants, docstring and manifest prose are new).

## Mix measurements (from the real rendered bytes)

- Mix WAV `Art_Source/Audio/Muse/MIX/CIN019_DRAFT_V1/CIN_019_mix_draft_v1.wav`
  sha256 `28d6c4754fd2634e7964518b1c6def55d4bea53058389c72e2d497549b943c69`,
  3,456,100 bytes, 18.000 s, pcm_s16le 48 kHz stereo:
  **−27.09 LUFS / −8.62 dBTP, LRA 8.10**, peak trim 0.0 dB. The quietest scene mix so far — the CP17 VO
  take itself is one of the quietest (−25.52 LUFS, re-verified
  from real bytes this run); VO is kept at unity per the recipe,
  not normalized.
- Stems (PROPOSED_CANDIDATE, new assignment; the CP02 table
  assigns nothing to CIN_019): composed **MUSIC/rift_finale**
  (−21.95 LUFS re-measured = pack) ducked by VO; composed
  **AMBIENCE/river_shore** (−29.69) unducked; composed
  **SFX/CINEMA/reveal** (−24.96) at 6.0 s (S02 start,
  PROPOSED_PENDING_PICTURE_LOCK). rift_finale is the composed
  set's only full close — the leitmotif's answering tail
  (F#–E–D), withheld in every other cue except the resolve
  stinger — and this is its **first scene-mix use**; river_shore
  is a third scene-mix use (CIN_003, CIN_008) for the rebuilt
  river village the spoken line lands in. mountain_wind was
  passed over: it beds only S01's mountaintop.
- VO (CP17 draft, Ly An): take 2.880 s placed at 12.5 s, runs
  12.5–15.380 s, **FITS window [12.5, 17.5] by 2.120 s**; no
  overrun, no tail trim; window/take/timing unchanged.
- Ducking (CP39 full-window method): **−4.29 dB** in-window,
  0.0 dB outside — a real cut (rift_finale carries real signal
  in the window; segment RMS −22.1 dBFS measured from the stem
  bytes this run), not a silence pocket.
- Ambience loop join (river_shore @15.5 s): maxJump 0.00154,
  ratio 0.58 vs the bed's own p999.
- Embedded re-measurement after mux: OGV **−27.08 LUFS /
  −8.59 dBTP** (Vorbis 160k), MP4 **−27.10 / −8.53** (AAC 192k);
  video streams bit-identical (pack builder verified; stored
  frame counts 498/540 unchanged — a copy check, not motion
  evidence).

## Staging note (NOT a mix defect)

The timing records the S03 dialogue `onscreen: true` for Ly An
(NPC_LYAN), and the keyframe manifest lists her among the scene's
on-screen characters — but the S03 keyframe is a **wide dawn view
of the whole village under reconstruction** (stepped,
stone-repaired channel in the foreground, small groups of workers
carrying logs and baskets): no individual figure is identifiable
as Ly An at this scale, and the scene's faces/costumes are
storyboard placeholders (NPC_LYAN has no approved cinematic
character lock). The placement stays onscreen per the timing; the
identity is not verifiable in the frame. A
final-picture/character-lock matter for Codex/director; the mix
did not move the VO.

## Tables and runtime state re-run

- `PLAYBACK_METADATA_v1.json`: **20 embedded / 1 silent
  (CIN_020)**; CIN_019 ownership EMBEDDED_SOUNDTRACK_ONLY,
  runtime = clean video + overlay SRT (builder verdict PASS).
- `PRONUNCIATION_TABLE_v1.json`: **26 cue rows, 23 seam rows
  (1 new: MUSIC/rift_finale 0.00036, first measured now that the
  cue is used in a scene mix; flagged stays 1 — MUSIC/sa_hoa
  0.016015), 21 fallback rows, 171 files verified**. Names
  unchanged (16 names, 4 spoken, only Tạ Vân Khanh DECIDED);
  CIN_019's line speaks no proper name.
- Runtime audio **625 → 626** (mix 28 → 29); runtime pack
  **19 → 20 scenes**.
- Validators: source re-validation PASS, 0 mismatches
  (`MEDIA02_CHECKPOINT_53_SOURCE_REVALIDATION_20261108.json`);
  runtime re-verify PASS, 0 mismatches
  (`MEDIA02_CHECKPOINT_53_RUNTIME_REVERIFY_20261108.json`).
  One ordering lesson recorded: `build_runtime_delivery.py` must
  run (or re-run) AFTER the pack mux, because it rebuilds
  `RUNTIME_CINEMATICS_manifest_v1.json` from the scene export
  manifests — a first validation pass caught the stale pre-mux
  CIN_019 entry plus the prologue total assert (625 → 626); both
  fixed and re-validated PASS.
- Scope audit: content-only 18 paths / 0 violations; cumulative
  vs integration `6f79853` shows the 1 known `.gitattributes`
  violation — a merge-base artifact (the checker diffs from
  cf17178; the file is byte-identical to integration), not a new
  breach. Historical reports' records are not edited.

## Limits

DRAFT_MIX_NOT_FINAL; NOT_AUDITIONED (no ear audition of this mix,
its VO take, or the new rift_finale seam); stem assignment and
stinger placement PROPOSED pending Codex review / picture lock;
final picture character-lock-blocked (storyboard keyframes, Ken
Burns motion — not final pose animation). Loudness figures are
measurements, not a listening PASS.

## Next

CIN_020 draft mix v1 — the last silent scene; after it, all 21
entries carry embedded soundtracks and WO37 M-B big checkpoint 1
closes. Then M-C (63-shot ledger follow-ups / P0 motion), M-D/M-E/
M-F per Work Order 37.
