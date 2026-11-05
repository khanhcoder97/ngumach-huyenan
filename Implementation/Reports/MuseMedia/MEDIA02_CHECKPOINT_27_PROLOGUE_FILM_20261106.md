# MEDIA-02 Checkpoint 27 — Prologue film CIN_000 "Trước khi tới Bến Mưa"

Date: 2026-11-06 · Branch: `muse/media-production-20261104` · Base integration: `f0859d0`

## Owner order

The owner asked for a cinematic film presenting the origin, setting,
history, and the situation that leads to the player character
appearing at the game's first map after character creation. Muse
researched the canon sources first (Content Bible §1,
Narrative_Depth_and_Discovery §§2–3, STORY_DECISIONS_V3, the Bến Mưa
screenplay, MUSE_CINEMA_DIRECTION), drafted a 5-part Vietnamese
narration script, and the owner approved it in main chat on
2026-11-06 ("Duyệt kịch bản — sản xuất luôn"). This checkpoint is
the full production of that film.

## The film

**CIN_000 — "Trước khi tới Bến Mưa"**, 87.367 s, 12 shots, a
standalone pre-game prologue (NOT one of the 20 campaign scenes; it
is registered under a separate `prologue` key in the runtime
cinematics manifest and is not counted in campaign totals
20/63/378/21).

Structure (narration-driven; shot windows derive from the MEASURED
VO durations, not from a fixed grid):

1. **Origin** (SEG01, 16.512 s) — S01 the land and the five currents
   converging on the ring mechanism; S02 the five towers in harmony.
2. **~300 years ago** (SEG02, 15.528 s) — S03 the earthquake breaks
   the mechanism; S04 the towers divided, hoarding water and name
   lists.
3. **~30 years ago** (SEG03, 19.752 s) — S05 drought and flood; S06
   the sinking city quarter; S07 a hand signing the sealing order
   (face out of frame); S08 the archive of erased names.
4. **Present day** (SEG04, 14.928 s) — S09 the bell that exists only
   as a reflection (nothing above the water); S10 the five-groove
   wax-sealed letter on a cargo boat.
5. **Arrival** (SEG05, 8.040 s) — S11 Bến Mưa in the rain, a cloaked
   traveler from behind stepping onto the dock; then Ly An's line,
   off-screen — **the checkpoint 04 CIN_001_S05 take reused
   byte-for-byte** (2.568 s, sha `51fc65de`), so the film ends on the
   exact voice and line the game opens with — then the title card
   (S12, code-rendered) with the composed `resolve` stinger.

Exports (all probed from real bytes): MP4 `88049317` (H.264 + AAC,
12,249,759 bytes), OGV `f7323bcf` (Theora + Vorbis, 25,267,547
bytes) — **unlike the campaign clips, the prologue carries its mixed
soundtrack embedded**. Poster = the S12 title-card PNG (a documented
choice for this standalone film). Recorded nuance: the video stream
measures 87.2667 s vs the 87.3667 s format/audio duration — the
xfade chain's non-frame-aligned offsets cost 3 frames (2618 of
2621), inside the final fade-out; export manifests record the
first-stream duration, the quantity the runtime verifier measures.

## Canon guardrails (held)

- No avatar origin, name, face, or secret bloodline; the traveler
  is an unnamed, class-neutral, back-view silhouette (no weapon).
- The reveal table is honored: the narration never names Cơ Vô
  Tướng, the hợp mạch mechanism, or Tạ Vân Khánh's responsibility —
  it hints ("a sealing order was signed", "records were erased").
- No boss kill and no seal-fragment reaction before gameplay
  (Content Bible §1).
- Painterly cinematic panels (a pre-game film does not use the
  20 PPU sprite standard); no baked subtitles (SRT ships separately).

## Audio

- Narration: 5 draft TTS takes (fictional voice `avocado_v2:MAI_03`;
  the narrator is a NEW role — casting is a director decision),
  measured −21.72…−22.49 LUFS, in `Art_Source/Audio/Muse/VO/
  PROLOGUE_DRAFT/` + runtime `assets/audio/vo/prologue/`.
- Mix (`PROLOGUE_mix_v1.wav`, **−20.81 LUFS / −9.08 dBTP**, no peak
  trim): narration unity + reused Ly An take (−5 dB) over a
  sidechain-ducked bed (CP20 settled values) of the **checkpoint 26
  composed** Bến Mưa theme (−9.07 dB) + ported rain_light /
  river_shore ambience (−8.52 / −8.47 dB, provenance kept separate)
  + the composed `resolve` stinger on the title card.

## Verification (all from real bytes)

- Film builder gates: staging SHAs 11/11; identity per shot
  (crop-compensated: full-res 8.27–15.27, 160×90 structure
  3.68–6.47); motion per shot 12.0–24.3. The S01 investigation is
  documented in `build_prologue_film.py`: a brute-force fit over
  zoom/offsets found the designed zooms (1.015 / 1.035 / 1.055 at
  t = 1.2 / 3.017 / 5.0 s) at zero offset — the residual is a
  measured resampling floor of the double-resample render path,
  not wrong content.
- Runtime delivery rebuilt: audio **589 files** (vo 30, mix 5,
  composed 13; the 541 ported PackV1 files untouched), campaign
  totals unchanged; `ALL VERIFIED`.
- Source re-validation: **PASS**, 0 mismatches (audio files checked
  1125; prologue files checked 42; timing scenes 20, dialogues 21).
- Runtime re-verify: **PASS**, 0 mismatches (589 audio files;
  prologue files 5).
- The campaign timing checker now explicitly skips CIN_000 (the
  prologue follows its own narration-driven contract, verified by
  the new `check_prologue()`).

## Limits / revision-pass items

- Everything is DRAFT: narration is draft TTS (no ear audition,
  pronunciation not yet reviewed by a native listener), the mix is
  DRAFT_MIX_NOT_FINAL (formula staging), panels are not final
  picture.
- Headline picture defects (full per-shot records in
  `CIN000_keyframes_manifest_v1.json`): S01↔S03 mechanism design
  drift (flat ring vs vertical arch with gears); S11's arrival
  direction is ambiguous (can read as boarding the boat); S04's
  ledger bears pseudo-script glyphs (illegible, closest to text of
  any panel); S07's script flavour leans Western cursive with a
  heraldic seal crest; S10's seal grooves are not crisply five;
  S09's reflection reads almost solid/submerged; S02's five regions
  blend into one valley; S06 has faintly modern distant buildings.
- Title typography uses DejaVu Sans Bold as a placeholder — the
  project has no locked Vietnamese display font yet.
- Wiring the prologue into the post-character-creation flow is
  Codex's presentation-adapter work.
