# MEDIA-02 Checkpoint — WO37 M-B CP2: standard 720p versions of the 21 playback cinematics (integer 2× upscale, measured budget)

Date: 2026-11-10 (JST). Branch: `muse/media-production-20261104`.
Baseline: `aa1cd97`. PR #119 stays HOLD; Muse does not self-merge.
Production OFF. Owner order: main-chat "tiếp tục" 2026-11-10 14:51 JST;
built in the main thread (worktree on baseline `aa1cd97`).

## What was delivered

The MEDIA-01 V2 delivery spec lists two picture sizes per cinematic —
low 640×360 and **standard 720p** — but until now only 640×360 existed.
This checkpoint delivers the standard set for all **21 playback entries**
(CIN_000 prologue + CIN_001–CIN_020 campaign), as review/standard masters
under `Art_Source/Cinematics/Standard720/<SCENE>/`. The ClientGodot
runtime tree is **not modified**; adoption stays Codex's decision
(same pattern as M38-A/B).

**Method — disclosed, not hidden:** every committed picture source for
these cinematics is 640×360 native (P0 and campaign keyframes alike are
640×360 PNG; the CP21-era 2048×1152 staging was never committed). The
standard version is therefore an exact **integer 2× nearest-neighbour
upscale** of the delivered 640×360 runtime master, matching the
project's own integer-scale display doctrine (no blur/bleed). It is
**not** a native 720p capture and is labelled as such in the manifest.
When final picture lands (character-locked shots), the builder simply
re-runs against the new runtime master.

**Encode:** H.264, `scale=1280:720:flags=neighbor`, preset medium,
**crf26**; audio **stream-copied bit-exact** from the runtime MP4
(EMBEDDED_SOUNDTRACK_ONLY preserved — the checker proves the AAC
payloads are byte-identical, so the soundtrack situation is unchanged).

**CRF choice, measured** (two most complex Ken Burns scenes,
CIN_005 / CIN_003; downscale-back mean|diff| and 2×2 intra-block range
stay ≤ 4.20 / ≤ 6.08 at *every* tested CRF, so extra bits buy no
structure — only size):

| CRF | size vs 640 master |
|-----|--------------------|
| 16 | 10.8–11.2× (full set measured: 423,195,998 B, 9.69×) |
| 20 | 7.3–8.1× |
| 23 | 5.3–5.8× |
| **26 (chosen)** | **3.8–4.1×** |

The size is the honest cost of full-frame Ken Burns motion at 4× the
pixels; the 640 masters run at only ~535 kbps video.

## Budget (measured from real bytes)

- MP4 standard set: **21 files, 147,993,980 B** vs 43,686,587 B for the
  640 set → **3.39×**. By picture type: P0 panel-hold scenes 1.21–1.26×;
  Ken Burns campaign scenes 3.39–4.05×; prologue CIN_000 2.77×
  (33,875,842 B for 87.367 s).
- OGV samples (Theora q6 + Vorbis 160k, mirroring the runtime recipe):
  CIN_001 7,110,206 B (197,447 B/s, panel-hold), CIN_003 12,386,615 B,
  CIN_019 12,684,356 B (704,478 B/s, wide) → mean 529,956 B/s →
  **full-set projection ≈ 246,623,785 B**. The full OGV standard set was
  **not** rendered: at ~5.6× the MP4 set's growth it is a budget
  decision for Codex, and the samples' audio is re-encoded from the
  embedded AAC — an adopted set should be rendered from the mix WAV
  masters per the M38-B recipe.

## Validation

Checker `check_standard720_mb_cp2_v1.py`: **PASS 237/237, 0 failures**
(`MEDIA02_WO37_MB_CP2_VALIDATION_20261110.json`). Per entry: source
sha256 equals the git LFS oid of the delivered master; output sha/bytes
match the manifest; probe 1280×720 @ 30 fps with audio; duration delta
≤ 0.06 s; audio elementary streams byte-identical source vs output;
frames at 3 timestamps downscale back to the master with worst
mean|diff| **4.215** and worst 2×2 intra-block range **6.08** across
all 21 entries; budget totals re-derived; git status clean under
`ClientGodot/` (runtime untouched).

Manifest: `Implementation/Content/Narrative/Deliveries/STANDARD720_MB_CP2_v1.json`
(per-file source/output sha256 + bytes + durations + budget + method).

## Limits / notes

- DRAFT standard versions of DRAFT masters; final picture remains
  character-lock-blocked for the locked shots — this set will be
  re-rendered from final masters, it does not pre-empt them.
- CIN_000's subtitled variant is not part of the playback set and has
  no standard version here.
- P0 scenes carry the runtime A picture, same as the runtime package
  of record; candidate B keeps its own M38-A/B package.
- Nothing was listened to or watched by ear/eye beyond the numeric
  frame checks; audio is a bit-exact copy, so no new audition state.

## Scope audit

- Content commit `563eb0d63085bab2653e108c7b47957970b3b261`:
  **27 paths / 0 violations** (base `aa1cd97`).
- Cumulative from merge-base `cf17178` at the content commit:
  2189 paths / 1 known `.gitattributes` merge-base artifact
  (byte-identical with integration `9ac73dc`, not a real divergence).
  The report commit adds exactly 2 files (this report + validation
  JSON), so the head count is 2191 paths / 159 commits.

## Files

- Tools: `Tools/MediaProduction/Muse/build_standard720_mb_cp2.py`,
  `Tools/MediaProduction/Muse/check_standard720_mb_cp2_v1.py`.
- Media: `Art_Source/Cinematics/Standard720/` — 21 MP4 (147,993,980 B)
  + 3 OGV samples (32,181,177 B).
- Manifest + this report + validation JSON.
