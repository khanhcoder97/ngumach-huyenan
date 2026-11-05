# MEDIA-02 — Checkpoint 26: Original composed music + cinema stingers (Gói 30, item 7)

Date: 2026-11-06 (JST) · Branch: `muse/media-production-20261104` · Base integration: `f0859d0`
Tool: `Tools/MediaProduction/Muse/build_composed_music.py`
Delivery pack: `Implementation/Content/Audio/Deliveries/MUSIC_COMPOSED_pack_v1.json`

## What this checkpoint is

Gói 30 item 7 requires actually composed/remixed music/SFX, counted separately from the
ported PackV1 audio. Checkpoints 07/08 measured and delivered Codex's PackV1 renders
(541 ported files); checkpoint 20 mixed the P0 scenes from those ported stems. This
checkpoint adds the first audio that is **new composition by Muse**: 13 cues — all 9
`MUSIC/*` cues and all 4 `SFX/CINEMA/*` stingers — composed from scratch, delivered in
parallel, with the ported pack untouched.

## Composition

One original leitmotif system, following the audio direction doc
(`docs/production/Audio_Production_Direction_v1_vi.md` §1: Bến Mưa's music is a
"câu nhạc bỏ lửng" — a phrase left hanging):

- The motif is a question phrase in D major pentatonic (D–E–F#–A–B) that stops on
  scale degree 2 (E). The answering tail (F#–E–D) is **withheld** in the exploration
  and boss material.
- The tail is played only by the `resolve` stinger and by `rift_finale` — the set's
  only full close.
- The 9 music cues are 9 transformations of the system: the theme itself (ben_mua,
  ending on the hanging note so the loop never resolves), a brighter street
  arrangement (thang_long), a D-minor fragmentation over a heartbeat pulse
  (boss_mang_cot, with one foreign F# bell), near-silence exploration
  (quiet_discovery), a G-major transposition with ornamented flute (lam_trieu),
  an A-minor dry-pluck syncopated form (sa_hoa), a bell-led gate form (tran_son),
  an underwater low-passed form (bach_uyen, 850 Hz), and the five-register finale
  (rift_finale).
- The 4 stingers are motif gestures: reveal = motif head ascending; tension = the
  hanging E held over a minor pad and low pulse; resolve = the withheld tail;
  transition = a water-crossing arpeggio.
- Rendering is procedural synthesis authored in the tool (additive pluck / flute /
  bell / pad / bass voices, noise percussion, two feedback-comb "river hall"
  delays). No external samples, no ported bytes, no voices.

## Measured results (real bytes, ffmpeg loudnorm — the checkpoint 07 method)

Masters are WAV 48 kHz / 24-bit stereo in `Art_Source/Audio/Muse/COMPOSED/`;
runtime OGG (Vorbis q5) in `ClientGodot/assets/audio/composed/`.

| Cue | Dur (s) | Master LUFS / TP | Runtime LUFS / TP | wrapJumpRaw |
|---|---|---|---|---|
| MUSIC/ben_mua | 56.67 | −21.98 / −10.43 | −21.93 / −10.33 | 0.138 |
| MUSIC/thang_long | 41.74 | −22.00 / −10.68 | −21.96 / −10.55 | 0.146 |
| MUSIC/boss_mang_cot | 36.36 | −22.00 / −7.46 | −21.98 / −7.35 | 0.039 |
| MUSIC/quiet_discovery | 64.00 | −21.87 / −13.15 | −21.72 / −13.09 | 0.064 |
| MUSIC/lam_trieu | 53.33 | −21.99 / −10.99 | −21.93 / −10.98 | 0.043 |
| MUSIC/sa_hoa | 43.64 | −22.00 / −8.63 | −21.96 / −8.58 | 0.006 |
| MUSIC/tran_son | 40.00 | −22.00 / −8.36 | −21.95 / −8.32 | 0.404 |
| MUSIC/bach_uyen | 58.06 | −22.00 / −10.74 | −21.96 / −10.77 | 0.295 |
| MUSIC/rift_finale | 38.40 | −22.00 / −10.16 | −21.95 / −9.91 | 0.091 |
| SFX/CINEMA/reveal | 3.00 | −24.99 / −15.62 | −24.96 / −15.50 | — |
| SFX/CINEMA/tension | 3.00 | −25.00 / −16.78 | −24.93 / −17.04 | — |
| SFX/CINEMA/resolve | 3.00 | −24.99 / −18.47 | −24.93 / −18.30 | — |
| SFX/CINEMA/transition | 3.00 | −25.00 / −16.11 | −24.97 / −16.16 | — |

Loop construction, stated plainly: each music cue's final 1.5 s of ring-out is mixed
over its head, and the final 0.25 s is blended to the first sample (a standard loop
crossfade construction), so the recorded `wrapJump` is ≈ 0. `wrapJumpRaw` in the
delivery manifest is the sample step **before** that landing — it is large where a
piece ends with drum/bell content near the seam (tran_son 0.404, bach_uyen 0.295).
Both numbers are recorded per cue; a loop-seam **ear check remains outstanding**,
exactly as it does for the ported pack (checkpoint 07 recorded indicators, not a
seamlessness PASS).

## Delivery and validation

- Runtime audio manifest: 570 → **583 files** (counts now include `composed: 13`).
  Composed entries carry `provenance: ORIGINAL_COMPOSED_BY_MUSE` and
  `assetState: COMPOSED_CANDIDATE`; ported entries are byte-identical to before.
- The composed cues do **not** replace the ported PackV1 files or their cue
  bindings. Adoption (or a re-mix of the P0 scenes from composed stems) is Codex's
  presentation-adapter decision at review.
- Source re-validation: **PASS, 0 mismatches**
  (`MEDIA02_CHECKPOINT_26_SOURCE_REVALIDATION_20261106.json`: audio files checked
  1119, composed cues 13; the validator gained a composed-pack checker that also
  asserts the provenance field on every cue).
- Runtime re-verification: **PASS, 0 mismatches**
  (`MEDIA02_CHECKPOINT_26_RUNTIME_REVERIFY_20261106.json`).
- Masters total 127.9 MB (WAV, carried by Git LFS); runtime OGGs 3.38 MB.

## Process notes (for the next run)

- Two render attempts were lost to environment restarts before any file landed;
  the composer now saves the delivery manifest after **every single cue**, and
  the final pack was re-rendered end-to-end by one tool version and verified
  file-by-file against the manifest before this report was written.
- A first renderer used scipy `lfilter` with a ~20k-tap comb denominator and
  took minutes per cue; the shipped tool computes the same feedback combs in
  delay-sized blocks (O(n)).

## Limits

- No ear audition: melodic quality, loop seams, and mix balance are unverified by
  listening. Loudness/true-peak are measured; musical judgement is the director's.
- The P0 draft mixes (checkpoint 20) still use the ported stems; re-mixing them
  from the composed stems is a follow-up, not part of this checkpoint.
- Ambience and gameplay SFX/UI remain the ported PackV1 renders with their own
  provenance; this checkpoint composes the music set and the cinema stingers,
  which are the cues inside Muse's cinema scope.

> **Erratum (same day):** the report commit message states a scope-audit count of 1062 paths; the verified three-dot diff count vs integration `f0859d0` is **1058 paths, 0 violations**. The commit message is not amended (no force-push); this note is the correction of record.
