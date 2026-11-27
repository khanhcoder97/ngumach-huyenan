# Muse PR119 review — pinned 3f34f0d

Reviewed head: `3f34f0de1de33f1d6ff97f19251165949a40a716`, 691 changed paths, against integration `f38323386b079f861c6472d2bd139e1ed9762c3c`. Isolated detached worktree: `D:/Project/NGUMACHHUYENAN-media-review-20261105`. No source edits, merge or GitHub posts were made.

## Decision

HOLD whole PR as currently presented. It is a useful draft/timing/porting checkpoint, not a finished M1–M8 media package. Two runtime metadata/provenance defects need correction before consumption. Final picture is not approved; the review reel should not automatically play during the opening.

## Findings

1. **P2 — four dialogue cue counts are wrong.** `Tools/MediaProduction/Muse/build_runtime_delivery.py:308` obtains `len(s.get("cues", []))` from three differently shaped manifests. Runtime `RUNTIME_CINEMATICS_manifest_v1.json` consequently says zero dialogue cues for CIN_001, CIN_002, CIN_004 and CIN_006, although each corresponding SRT has one. This can make a consumer skip dialogue/subtitle resources. Derive the count from parsed timing dialogue/SRT and add cross-manifest equality validation.

2. **P2 — Windows checkout invalidates all forty timing/SRT hashes.** On this fresh Windows checkout, all 20 runtime JSON timing hashes and all 20 SRT hashes fail the recorded SHA256. Every one matches after CRLF→LF normalization. Raw-byte verifier (`verify_runtime_delivery.py:101`) therefore rejects a correct normal Windows checkout. The repository lacks LF attributes for these new source/runtime delivery files. Codex can add appropriate `text eol=lf` rules, then regenerate/check cross-platform hashes. Do not silently weaken hashes or treat malformed/tampered files as equivalent.

3. **P2 — actual CIN_002_S02 picture contradicts its action.** `Art_Source/Cinematics/P0_Animatic/P0_animatic_spec_v1.json:186` requires Tạ's GOOD hand to stop before touching the water. The actual MP4 at 45s shows his BANDAGED hand touching it. The center crop also clips his head/face. See `cin002_s02_actual_mp4.png` in this review folder. This is additional to four admitted defects at spec lines70/148/248/308: solid bell instead of reflection-only, wrong character in CIN001S06, unreadable broken horn, angled CIN004S03. Generate independent correctly framed 16:9 shot keyframes; a single irregular storyboard sheet and automatic center crops are not suitable final frames.

4. **P3 — 22 binaries are raw Git blobs despite LFS attributes.** Source PNG/MP3/WAV and runtime MP4/poster cause checkout warnings that they should be pointers. Current `git status` is nevertheless clean; this is repository hygiene/compliance, not proof of corrupt runtime bytes. Normalize just the approved media paths through LFS in a reviewed commit. `.ogv` is not currently a LFS pattern and needs an owner decision if it should be added.

5. **Completion claim exceeds delivery.** `MEDIA02_CHECKPOINT_11_M8_HANDOVER_QA_20261105.md:100` says Muse finished M1–M8. Independently checked provenance proves 541/545 runtime audio files are unchanged ports of the pre-existing Codex PackV1. Only four audio files are new VO products (three TTS takes plus their timeline). The 20-scene campaign has timing/SRT, not 20 completed videos. The only video is a 72s twelve-still review reel covering CIN001/002/004, not animated final takes. CP07/08 elsewhere correctly disclose this; title/body/completion summary need the same precision.

## Independent checks

- `review_result.json`: 545 audio source/runtime SHA or LFS object identifiers checked, zero provenance mismatches; 541 inherited PackV1 and four VO.
- Three actual WAVs: 48kHz/mono/16bit, 2.568/3.792/1.752s, correct SHA and fit the stated windows. No auditory audition or pronunciation assessment was performed.
- Fifteen actual image/video SHA checks pass: 12 panels + MP4 + OGV + poster.
- FFmpeg installed only into `D:/Project/NGUMACHHUYENAN-tools/review-media`, package `imageio-ffmpeg==0.6.0` from pip, bundled FFmpeg7.1. No global install/PATH/auth changes.
- `mp4-decode.log`: H264 High/yuv420p, 640×360,30fps,72.00s,2160 frames fully decoded, exit0.
- `ogv-decode.log`: Theora/yuv444p,640×360,72.00s,211 stored still-hold frames decoded, exit0. Both contain no audio. YUV444 alone is not an unsupported-Godot defect: official Theora implementation supports444/422/420 (`https://raw.githubusercontent.com/godotengine/godot/master/modules/theora/video_stream_theora.cpp`, video_write).
- Storyboard sheet and actual extracted MP4 frame were visually inspected. No claim of native Godot video playback, audio audition, final mix, loop quality or campaign playback acceptance.

## Director decisions and next large package

- D1 can be approved for **rough VO production only** using the current 21 canonical text/window records. CIN001S05 remains24.8–28.5s; CIN0027–11s; CIN0047.5–9.5s off-screen; CIN00612.5–17.5s. Remaining campaign cues mostly12.5–17.5s, CIN01112.2–17.8s, CIN0186.5–11.5s plus12.5–17.5s. This releases 17 remaining VO drafts without locking final picture/mix. Do not change canonical text to force a window or silently speed speech.
- Fix all five identified picture defects and verify the five-groove seal readability. Character references exist; missing final character locks should only block the affected final shot, not independent environmental shots/audio work.
- Export per-scene review/runtime clips with explicit sceneID/URI/start/end/duration metadata. The current single72s reel concatenates001/002/004 and would reveal later story/boss if used as the opening asset. Keep it in a media preview/gallery until fixed/approved; no video callback grants gameplay rewards.
- Complete actual campaign animated takes,17 remaining VO drafts, new/refined music/SFX arrangements and full mixed P0 preview with separate stems/gain/ducking/loop QA. Carry original Codex sound pack provenance honestly. Existing measurements alone are not new audio production.
- Correct metadata/LFS and extend validators to catch cue-count disagreement and Windows LF behavior, then push a source/media checkpoint and continue large independent work. Re-running the same M8 hashes after every merge should not replace remaining creative production.

Evidence in this folder is review-only and outside the project. Root owns any source changes, GitHub review and acceptance decisions.
