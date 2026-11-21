# MEDIA-02 — PR #119 Body Restructure R37: delivery index + body v2 coverage to `9ec1fd9`

Date: 2026-11-15 (JST). Branch: `muse/media-production-20261104`.
Coverage head: `9ec1fd9` (PR119 BODY RESTRUCTURE R36 report). Content commit: `9d45aae`.
PR #119 stays HOLD; Muse does not self-merge.
Status: **DRAFT_NOT_FINAL / NOT_AUDITIONED** — bookkeeping only; no media
byte, mix, runtime file, or casting decision is changed here.

## What R37 does

R36 left a disclosed gap: the delivery index covered 261 commits to
`03b0a8a`; R36's own 2 commits were to fold in at R37. Since then the
R36 body v2 was NOT posted — the live PR description is still the R8 body
(head `f2ba478` · 207 · 2419, title 763 ký tự kết thúc "+ R8", body_len
11.793, verified by connector list endpoint 2026-11-15 ~15:40 JST this
round: PR head `9ec1fd9`, updated 2026-11-15T05:44:28Z). The R36 payload
(`pr119_update_body_v2_r36.json`, 26.199 ký tự) is now SUPERSEDED by the
R37 body v2 before any tap, following the same pattern as R3/R4/R5/R7/R9–R36.
No new Codex/owner direction has landed on issue #116. Note: this is a
detached scheduled run (15:40 JST, in-hours), so the R37 payload is prepared
here for the main agent to present — the approval card lives ~30 minutes,
tap while at the machine.

Đính chính — tiêu đề body v2 bị thiếu R33: bản R36 (commit `386216b`)
đã làm rơi "PR119 BODY RESTRUCTURE R33" khỏi tiêu đề khi sửa tay
(tiêu đề cũ kết thúc "...R32 + R33 + R34" thành "...R32 + R34 + R35").
R37 khôi phục R33 vào tiêu đề và thêm R36; checker R37 khẳng định tiêu
đề chứa cả R33 lẫn R36. Nội dung khối R33 không hề mất (đoạn văn trong
body v2 + dòng trong bảng index vẫn đủ) — chỉ tiêu đề thiếu một mục.
Vì mô tả live vẫn là bản R8 (xác minh ~15:40 JST), payload R36 mang
tiêu đề lỗi này chưa từng đăng lên GitHub — khuyết điểm không lọt ra ngoài.

Fresh derivation at `9ec1fd9` (~15:40 JST): `git rev-list --count
cf17178..9ec1fd9` = 263 commits, `git diff --name-only` = 2503 files,
`--shortstat` = 232719 insertions, 0 deletions — exactly matching the
R36 report's remote-tip figures. The structural cross-check stands:
`git merge-tree --write-tree` `9ec1fd9` vs integration `f3db6b3`
exit 0, 0 conflicts, tree `d81bf954b69728746c757e807d4e27ddb1a03ec1`.

R37 closes the gap:

- **Delivery index** (`MEDIA02_PR119_DELIVERY_INDEX_20261113.md`):
  milestone lines refreshed to head `9ec1fd9` (263 commits / 2503 files /
  232719 additions; API figures cited are the last verified read at
  `f891e40`, ~13:41 JST — no fresh PR read this round, see Verification);
  one row appended — PR119 BODY RESTRUCTURE R36 (`386216b`/`9ec1fd9`),
  including the note that its body payload was superseded by the R37 body
  v2 before posting; issue line still 34 comments. The index now covers
  every block through `9ec1fd9`; R37's own 2 commits fold in at the next
  index update (R38), disclosed in the index itself.
- **Body v2 file** (`MEDIA02_PR119_BODY_V2_20261113.md`): head line synced
  to `9ec1fd9` · 263 · 2503 (with the last verified mergeable true/clean
  read at `f891e40` plus the true/unstable read at `03b0a8a`), plus the
  R36 paragraph in "Khối mới nhất", the R37 note, and the R33 title fix.
  The live PR description is refreshed from this file in the posting round
  that follows R37 (owner tap) — the R8 body v2 already live is the base;
  only the R36 paragraph + new head line + title fix are new.
- **Checker** `check_pr119_restructure_r37_v1.py`: re-derives every
  figure from git (counts, additions, merge-tree) and asserts the
  index/body coverage claims, including the title fix (R33 + R36 both in
  the title line). **PASS 17/17**
  (`MEDIA02_PR119_BODY_RESTRUCTURE_R37_VALIDATION_20261115.json`),
  first run — no fix round needed this time.

## Verification

- Merge-tree `9ec1fd9` vs integration `f3db6b3`: exit 0, 0 conflicts,
  tree `d81bf954b69728746c757e807d4e27ddb1a03ec1`. Merge-tree at the R37
  content head `9d45aae` vs `f3db6b3`: exit 0, tree
  `7a3f64267f1ef57cf6563cd7aaa81e8535500eec`.
- PR API single-PR read: NOT re-read this round — the public REST API
  returned HTTP 403 rate limit (unauthenticated IP quota) for
  `/pulls/119` at ~15:40 JST; no retry loop was run. The connector list
  endpoint answered instead: PR #119 head `9ec1fd9`, title 763 ký tự kết
  thúc "+ R8", body_len 11.793, updated 2026-11-15T05:44:28Z — the live
  body is still R8; mergeable is null via the list endpoint. Last verified
  reads stand: mergeable true / clean at head `f891e40` (~13:41 JST),
  and mergeable true / mergeable_state unstable at head `03b0a8a`
  (~13:44 JST, CI running on the new head — not a review failure).
- Issue #116: 34 comments, `updated_at` 2026-11-13T19:24:49Z (unchanged
  since the ACK `6862732081` posting), latest ACK `6862732081` (CP5 + M-G
  CP10 + R2, posted 2026-11-14 ~04:24 JST); no new Codex/owner direction
  since Gói 39 (`6815238814`). Read via the connector `list_issues`
  endpoint (~15:40 JST); `get_issue`/`get_pull_request` are not advertised
  by the live MCP server, and the public REST API is rate-limited.
- Scope audit: R37 block 3 paths / 0 violations; cumulative at the R37
  content commit 2504 paths / 1 violation — the known `.gitattributes`
  merge-base artifact only (byte-identical with integration `f3db6b3`,
  sha256 `23352e4c…` on both sides, re-verified at `9d45aae`).
  Merge-tree at the R37 content head `9d45aae` vs `f3db6b3`: exit 0,
  tree `7a3f6426…`.

## Next

Posting round (owner tap, in-hours): PR #119 description refresh to the
R37 body v2 (R36 paragraph + new head line + R33 title fix are the only
new parts vs the live R8 body). Payload `pr119_update_body_v2_r37.json`
prepared at `~/workspace/godot-prototype/pr_comments/` after the R37 push
(title 764 ký tự, kết thúc "+ R37"; body = body v2 R37 trong repo, head
line làm tươi tới head sau khi R37 push). Do NOT tap the R36 widget
(`pr119_update_body_v2_r36.json`) — it is superseded by R37 (and it
carried the broken title missing R33). No separate ACK comment for R37:
its content is pure bookkeeping. Standing blocks unchanged: 32 shots await
character lock; ear audition is the owner's ears; full OGV 720p deferred
per Gói 39; SFX binding awaits Codex.
