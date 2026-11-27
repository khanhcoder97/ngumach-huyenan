# Muse PR119 delta review

Pinned head: `67f0d92503c0661a9ded21e5b871b54aa683f981`, verified through GitHub. Delta from `3f34f0de1de33f1d6ff97f19251165949a40a716`:22files. No source edits, GitHub posts or merges.

| Finding | Delta result |
|---|---|
| Four zero dialogue counts | **Fixed**. New parsed timing/SRT/source cross-check runs independently with20scenes/21cues/0errors. Runtime CIN001/002/004/006 now1. |
| Four admitted picture defects | **Materially improved at storyboard level**, all four changed panels viewed: bell reflection only, LyAn identity, one broken horn, overhead arena. Not approval of animated final takes. |
| Fifth defect: Tạ hand/crop | **Unchanged**. CIN002S02 panel is byte-identical to old version: bandaged hand touching water, head/face cut. |
| Forty Windows text SHA mismatches | Still40raw failures at Musehead,40passafterLFnormalization. Musehead does not contain ownerintegrationa84ce590. OwnerLFattributes already address merged checkout; do not require Muse to edit forbidden-root attributes or regenerate otherwise-correct canonical hashes. |
| Raw binaries underLFS | Not normalized. New v2sheet increases23patternedrawfiles; new ownerOGVpattern includes one more→24currentrawmedia blobs. Normalize current owned files by attributes, rather than stopping on obsolete literal22count. |
| Overstated completion | CP14 honestly discloses541inheritedaudio+4newVO, timing-onlycampaign, stillreel. PRtitle/body stillstaleCP01–07; oldCP11claim remains historical. No newaudioor17remainingVO/videoassets in this delta. |

Independent v2 checks: MP4/OGV/posterSHA match; MP4decode2160frames/72s exit0; OGVdecode263storedholdframes/72s exit0. Logs `mp4-v2-decode.log`/`ogv-v2-decode.log`. Audio paths unchanged, so did not redo545file checks.

Recommendation: HOLD whole PR for runtime/final-picture acceptance. Parsed cue fix can be accepted separately. Do not autoplay concatenated72s reel as opening. Continue fifthshot repair, independent16:9keyframes/per-sceneexports,17VOdrafts and campaignanimatedtakes under ownerdrafttimingdecision. Current Musehead predates/doesnotcontain a84ce590 and must read latest issue116decision rather than keeping previous questions as a package-wide blocker.
