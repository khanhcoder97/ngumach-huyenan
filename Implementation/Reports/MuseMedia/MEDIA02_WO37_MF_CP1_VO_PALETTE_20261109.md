# MEDIA-02 Checkpoint — WO37 M-F CP1: voice palette + pickups + pronunciation review pack

Date: 2026-11-09 (JST). Branch: `muse/media-production-20261104`.
Integration baseline: `6f79853`. PR #119 stays HOLD; Muse does not
self-merge. Production OFF.

## What was delivered

WO37 M-F checkpoint 1 resolves the draft-casting collisions recorded in
CP04/CP17 and CP54: every male speaker shared one voice (Helio), Ly An
shared her voice with the undecided letter recipient (Aria), and the
prologue narrator also used Helio. This checkpoint assigns **one distinct
fictional system voice per speaking role (11 roles / 11 voices; no
real-voice cloning)** and records a **palette pickup (alternate take) for
every affected take: 15 dialogue takes + 5 prologue narration segments =
20 pickups**. Ly An keeps Aria; her 7 takes were NOT re-recorded.

New tools: `Tools/MediaProduction/Muse/build_vo_palette_mf_cp1.py`
(converts the raw TTS MP3s to WAV 48 kHz mono, measures from real bytes,
cross-checks every text against the timing JSON dialogue + scene SRT,
checks window fit) and
`Tools/MediaProduction/Muse/check_vo_palette_mf_cp1_v1.py` (independent
re-verification: re-hash + re-measure + palette distinctness + text
equality + runtime entries).

## Voice palette (VOICE_PALETTE_v1.json, DRAFT_PALETTE)

| Role | Voice | Previous | Change |
|---|---|---|---|
| Ly An (NPC_LYAN) | avocado_v2:MAI_01 Aria (F) | MAI_01 | KEPT — no pickup |
| Tạ Vân Khanh | avocado_v2:conor Polished Coin (M) | MAI_03 Helio | NEW_DISTINCT |
| Hạ Mặc | avocado_v2:vincent Gruff Brick (M) | MAI_03 Helio | NEW_DISTINCT |
| Sầm Chủ Quỹ | avocado_v2:hubert Loud Gravel (M) | MAI_03 Helio | NEW_DISTINCT |
| Trưởng đoàn | avocado_v2:magnus Boomy Mountain (M) | MAI_03 Helio | NEW_DISTINCT |
| Tống Bành | avocado_v2:ronan Fluid Hammock (M) | MAI_03 Helio | NEW_DISTINCT |
| Đội trưởng thợ lặn | avocado_v2:briggs Husky Campfire (M) | MAI_03 Helio | NEW_DISTINCT |
| Cơ Vô Tướng | avocado_v2:atlas Burnished Trophy (M) | MAI_03 Helio | NEW_DISTINCT |
| Người chơi | avocado_v2:miles Satiny Moon (M) | MAI_03 Helio | NEW_DISTINCT, still VOICE_PLACEHOLDER_ONLY |
| Người nhận thư | avocado_v2:ElvenWizard Ethereal Star (N) | MAI_01 Aria | NEW_NEUTRAL_PLACEHOLDER |
| Người kể chuyện | avocado_v2:History Learned Globe (M) | MAI_03 Helio | NEW_DISTINCT |

The recipient's identity/gender is UNDECIDED (owner direction, CP54);
ElvenWizard is the catalog's only neutral-gender voice and is used as a
placeholder — NOT a casting or gender decision. The player pickup is
still a timing-only placeholder: a distinct voice so the placeholder no
longer sounds like a named character, not a casting decision.

## Pickup measurements (from the real rendered bytes)

All 20 raw MP3s were synthesized at speed 100, language vi, with the
CLI-returned `voice` field verified against the requested voice for
every take; all 20 renders have distinct SHA-256 values (no cache
collision: the conor probe of Tạ's line differs from the canonical
Helio render). Texts are character-exact vs the canonical manifests
(and vs timing JSON + SRT for the 14 windowed dialogue takes).

| Take | Role / voice | Canonical | Pickup | Fit |
|---|---|---|---|---|
| CIN002_S02 | Tạ / conor | 3.792 s, −21.61 LUFS | 3.312 s, −23.59 LUFS | FITS, slack 0.688 s |
| CIN006_S03 | Hạ Mặc / vincent | 5.520 s, −21.96 LUFS | 4.848 s, −23.23 LUFS | FITS, slack 0.152 s |
| CIN006_ALT_T01 | Hạ Mặc / vincent | 3.000 s, −22.37 LUFS | 3.312 s, −24.83 LUFS | no window (Q3) |
| CIN008_S03 | Tạ / conor | 3.552 s, −23.10 LUFS | 3.168 s, −24.75 LUFS | FITS, slack 1.832 s |
| CIN010_S03 | Sầm / hubert | 2.808 s, −22.01 LUFS | 3.360 s, −27.96 LUFS | FITS, slack 1.640 s |
| CIN011_S03 | Hạ Mặc / vincent | 5.592 s, −21.50 LUFS | 4.392 s, −24.02 LUFS | FITS, slack 1.208 s |
| CIN012_S03 | Hạ Mặc / vincent | 4.320 s, −25.38 LUFS | 3.792 s, −25.56 LUFS | FITS, slack 1.208 s |
| CIN013_S03 | Trưởng đoàn / magnus | 2.472 s, −22.51 LUFS | 2.592 s, −20.17 LUFS | FITS, slack 2.408 s |
| CIN014_S03 | Tống Bành / ronan | 3.072 s, −22.05 LUFS | 2.712 s, −25.35 LUFS | FITS, slack 2.288 s |
| CIN015_S03 | Thợ lặn / briggs | 2.880 s, −23.27 LUFS | 3.048 s, −23.36 LUFS | FITS, slack 1.952 s |
| CIN016_S03 | Hạ Mặc / vincent | 2.472 s, −21.92 LUFS | 2.472 s, −22.26 LUFS | FITS, slack 2.528 s |
| CIN017_S03 | Thợ lặn / briggs | 3.168 s, −22.33 LUFS | 2.880 s, −24.85 LUFS | FITS, slack 2.120 s |
| CIN018_S02 | Cơ Vô Tướng / atlas | 2.880 s, −23.77 LUFS | 2.568 s, −24.27 LUFS | FITS, slack 2.432 s |
| CIN018_S03 | Người chơi / miles | 5.280 s, −22.54 LUFS | 4.512 s, −23.43 LUFS | FITS, slack 0.488 s |
| CIN020_S03 | Người nhận thư / ElvenWizard | 3.000 s, −19.59 LUFS | 3.072 s, −24.83 LUFS | FITS, slack 1.928 s |
| CIN000_SEG01 | Narrator / History | 16.512 s, −21.72 LUFS | 13.008 s, −30.13 LUFS | narration segment |
| CIN000_SEG02 | Narrator / History | 15.528 s, −22.31 LUFS | 16.752 s, −28.79 LUFS | narration segment |
| CIN000_SEG03 | Narrator / History | 19.752 s, −22.49 LUFS | 16.248 s, −29.21 LUFS | narration segment |
| CIN000_SEG04 | Narrator / History | 14.928 s, −21.80 LUFS | 12.768 s, −27.77 LUFS | narration segment |
| CIN000_SEG05 | Narrator / History | 8.040 s, −22.33 LUFS | 6.672 s, −28.67 LUFS | narration segment |

**All 14 windowed pickups FIT; 0 pickup overruns.** The two lines
whose canonical takes overrun fit in their new voices (CIN_006_S03
vincent 4.848 s vs the 5.0 s window, slack 0.152 s; CIN_018_S03 miles
4.512 s vs the 5.0 s window, slack 0.488 s) — recorded as data only.
The three kept canonical overruns (CIN_005_S03 +0.160 s, CIN_018_S03
+0.280 s, CIN_006_S03 +0.520 s) are UNCHANGED: the mixes still embed
the canonical takes, and the overrun decision stands until the
director adopts the palette and re-mixes (M-B follow-up).

## Pronunciation review pack (PRONUNCIATION_REVIEW_PACK_v1.json)

Cross-references PRONUNCIATION_TABLE_v1.json (CP44, unchanged — it
stays tied to the embedded mixes) and adds A-B listening rows for the
4 spoken names, with estimated in-take timecodes (character-ratio
estimate, a navigation aid, NOT a forced alignment) and specific
listening questions per name:

- **Lạc Châu** — SEG01 + SEG04, A = Helio, B = History.
- **Huyền Ấn** — SEG01, A = Helio, B = History.
- **Bến Mưa** — SEG05, A = Helio, B = History.
- **Sa Hỏa** — CIN_018_S03, A = Helio (placeholder), B = miles (placeholder).

The 12 unspoken names — including **Tạ Vân Khanh (DECIDED spelling,
never spoken in delivered audio)** — get no pickup, per WO37 M-F (no
useless reads to inflate count). Playlist
`vo_palette_review_playlist.txt` (M3U content): 10 entries, A then B
per name occurrence.

## Tables and runtime state

- `VOICE_PALETTE_v1.json`: 11 roles / 11 distinct voices (1 kept, 10 new).
- `VO_PALETTE_PICKUPS_pack_v1.json`: 20 takes (14 dialogue + 1 alternate + 5 narration), 14 fits, 0 overruns.
- Runtime delivery (§3s in `build_runtime_delivery.py`): 20 pickup WAVs
  copied to `ClientGodot/assets/audio/vo/palette_pickups/` as
  `PALETTE_ALTERNATE` entries. Runtime audio **737 → 757** (vo 30 → 50;
  music/ambience 22, SFX/UI 519, mix 30, composed 136 unchanged).
  Campaign totals unchanged: 20 scenes / 63 shots / 378 s / 21 cues.
  Playback metadata unchanged (21 embedded / 0 silent); pronunciation
  table unchanged (27 cue rows / 23 seam rows / 21 fallback rows).
- Validators: MF CP1 validator **PASS, 0 mismatches**
  (`MEDIA02_WO37_MF_CP1_VALIDATION_20261109.json` — 40 source files
  re-hashed, 20 runtime entries verified); source re-validation
  **PASS, 0 mismatches**
  (`MEDIA02_WO37_MF_CP1_SOURCE_REVALIDATION_20261109.json` — 1411 audio
  files checked; one stale hardcoded total in `check_prologue` (737)
  was corrected to 757 as part of this checkpoint, then re-run PASS);
  runtime re-verify **PASS, 0 mismatches**
  (`MEDIA02_WO37_MF_CP1_RUNTIME_REVERIFY_20261109.json`).
- Scope audit: content-only **71 paths / 0 violations**; cumulative vs
  integration `6f79853` is **2032 paths / 1 violation** — the single
  violation is `.gitattributes`, a merge-base artifact (the checker
  diffs from cf17178; the file is byte-identical to integration), not
  a new breach. Historical reports' records are not edited.

## Limits

DRAFT_PALETTE / DRAFT_NOT_FINAL; NOT_AUDITIONED (no ear audition of
any palette take or A-B pair — the review pack is the listening
brief). Pickups are alternates, not replacements: no mix, timing,
SRT, playback metadata or pronunciation table changed in this
checkpoint. Level notes for the listener: the narrator pickups run
6–8 LUFS quieter than the canonical Helio narration (History −27.77
to −30.13 LUFS vs −21.72 to −22.49 LUFS) and mostly shorter — adopting
them means re-balancing the prologue mix, not re-recording; the Sầm
pickup is the quietest dialogue take (−27.96 LUFS) and the refugee
leader the loudest (−20.17 LUFS). In-take name timecodes in the review
pack are character-ratio estimates, not measured alignments. The
recipient's neutral voice and the player's distinct voice are
placeholders, not casting decisions.

## Next

M-E (SFX/ambience real variants) or M-F CP2 (palette adoption re-mixes
once the director/Codex picks voices from the A-B review). PR #119
description + ACK MF CP1 need the main thread (owner approval card for
GitHub writes).
