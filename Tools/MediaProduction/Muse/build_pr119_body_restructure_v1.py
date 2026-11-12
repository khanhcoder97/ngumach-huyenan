#!/usr/bin/env python3
"""Build + validate the PR #119 description restructure (MEDIA-02).

- Generates Implementation/Reports/MuseMedia/MEDIA02_PR119_DELIVERY_INDEX_20261113.md
  from `git log cf17178..HEAD` (187 commits): every commit is paired
  content+report (via the SHA the report subject references) or listed as a
  singleton / merge / fix / erratum. Nothing is dropped.
- Validates Implementation/Reports/MuseMedia/MEDIA02_PR119_BODY_V2_20261113.md:
  byte/char size, live head/commit/file counts, every git SHA resolves,
  every block named in the body exists in the index.
- Writes MEDIA02_PR119_BODY_RESTRUCTURE_VALIDATION_20261113.json.

Run from anywhere inside the media clone:
  python3 Tools/MediaProduction/Muse/build_pr119_body_restructure_v1.py [--base <sha>]

The --base SHA is the integration head verified by `git ls-remote` in this run
(f3db6b3). Never trust a local tracking ref for it (single-branch clone lesson).
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MERGE_BASE = "cf17178"
HEAD_SHORT = "443d3e4"
BASE_SHA = "f3db6b3"  # integration head, ls-remote-verified 2026-11-13 ~04:44 JST
BODY_MAX_BYTES = 60000

REPO = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"],
    cwd=Path(__file__).resolve().parent, text=True).strip())
REPORTS = REPO / "Implementation/Reports/MuseMedia"
INDEX_MD = REPORTS / "MEDIA02_PR119_DELIVERY_INDEX_20261113.md"
BODY_MD = REPORTS / "MEDIA02_PR119_BODY_V2_20261113.md"
VALIDATION_JSON = REPORTS / "MEDIA02_PR119_BODY_RESTRUCTURE_VALIDATION_20261113.json"

# Backticked tokens in the body that are NOT git objects (verified separately).
KNOWN_FILE_SHA_PREFIX = {
    # prologue fixed mix sha256, cross-checked against the PROLOGUE V1 FIX
    # validation JSON (mix_sha256 field) in validate_body().
    "4f8224e1": "prologue fixed mix sha256 prefix",
}
KNOWN_GITHUB_IDS = {
    # Verified by public-API read of issue #116 comments in this run.
    "6833806995": "issue #116 ACK comment (SCENE-CLIPS FIX + M-G CP9)",
    "6815238814": "issue #116 Gói 39 direction comment (Codex)",
}

HEADLINE = """## Tổng quan bàn giao (số thật tại head `443d3e4`)

| Hạng mục | Số liệu |
|---|---|
| Campaign | 20 scene / 63 shot / 378 s; timing JSON + SRT UTF-8/NFC; dialogueCues = 21 |
| Video | animatic P0 v3 72 s + clip riêng 20/20 scene; motion 38/38 action shot; 26/26 hold slice; B take 20/20 scene |
| VO | 21/21 cửa sổ có VO dự thảo; palette 11 vai / 11 giọng; 20 pickup; mix v2 14 mix (Art_Source) |
| Nhạc sáng tác gốc | 13 cue + 4 stinger; 13 ambience + 26 variant; score 15/15 slot, 16 cue có intensity layer |
| SFX | coverage 63/63 key; 18/18 draft variant đã duyệt (source-only, binding UNSUPPORTED) |
| Runtime audio | 783 file (composed 162, ported 541) |
| Standard 720p | 21 MP4, tổng 148.002.469 B (integer 2× NN, không phải 720p native); 14 entry mang soundtrack v2 |
| Prologue CIN_000 | film 87,367 s + bản phụ đề + bản 720p phụ đề |
| Ear-audition pack | v1 196 item + v2 delta 58 item = 254 item; NOT_AUDITIONED |
| QA | `validate_media_deliveries` PASS 0 mismatch; `verify_runtime_delivery` PASS; fresh-checkout baseline `14b588c` |

Mốc quyết định DEC-MEDIA-P0-20261105: Q1 CIN_001_S05 bản B “Đầu kia! Giữ giúp tôi đầu kia!”, VO 24.8–28.5 s; Q2 Ly An voice off-screen trong CIN_004, characters chỉ `BOSS_MANG_COT`; Q3 alternate CIN006 có takeId/version riêng, không thay canon; Q4 Hạ Mặc/Sầm cinematic-only staging, không nhân đôi persistent ID. Tên canonical “Tạ Vân Khanh”.
"""


def git(*args):
    return subprocess.check_output(["git", *args], cwd=REPO, text=True).strip()


def git_ok(*args):
    return subprocess.run(["git", *args], cwd=REPO,
                          stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0


def parse_log():
    out = git("log", "--format=%H|%s", f"{MERGE_BASE}..HEAD")
    commits = []  # chronological
    for line in reversed(out.splitlines()):
        sha, subject = line.split("|", 1)
        commits.append({"sha": sha, "short": sha[:7], "subject": subject})
    return commits


def is_report(subject):
    return (" report: " in subject or " report - " in subject) and "erratum" not in subject


def referenced_content_sha(subject, by_prefix):
    m = re.search(r"content (?:commit )?([0-9a-f]{7,40})", subject)
    if not m:
        m = re.search(r"record pushed SHA ([0-9a-f]{7,40})", subject)
    if not m:
        m = re.search(r"content commit ([0-9a-f]{7,40})", subject)
    if not m:
        return None
    return by_prefix.get(m.group(1)[:7])


def strip_prefix(subject):
    s = subject
    for p in ("MEDIA-02 ", "media: MEDIA-02 ", "media: ", "fix(media): "):
        if s.startswith(p):
            s = s[len(p):]
            break
    return s


def block_label(subject):
    s = strip_prefix(subject)
    head = re.split(r" - |: ", s, maxsplit=1)[0].strip()
    head = re.sub(r"\s+content$", "", head)
    m = re.match(r"checkpoint (\d+)$", head)
    if m:
        return f"CP{m.group(1)}"
    if head == "SCENE-CLIPS manifest fix":
        return "SCENE-CLIPS MANIFEST FIX"
    return head


def result_text(subject, label):
    s = strip_prefix(subject)
    # drop "<label> report: " / "<label>: " lead-in
    s = re.sub(r"^.*?report:\s*", "", s) if "report:" in s else s
    s = re.sub(r"^.*?report - \s*", "", s) if "report - " in s else s
    s = re.sub(r"^checkpoint \d+:\s*", "", s)
    s = re.sub(r"^WO\d+ [A-Z0-9\- ]+:\s*", "", s)
    s = re.sub(r"^PROLOGUE V1 FIX:\s*", "", s)
    s = re.sub(r"^SCENE-CLIPS manifest fix:\s*", "", s)
    # drop embedded "content <sha>" references left in the summary
    s = re.sub(r"content commit [0-9a-f]{7,40},?;?\s*", "", s)
    s = re.sub(r"content [0-9a-f]{7,40} \+ [0-9a-f]{7,40},?;?\s*", "", s)
    s = re.sub(r"content [0-9a-f]{7,40},?;?\s*", "", s)
    s = re.sub(r"\+\s*[0-9a-f]{7,40},?;?\s*", "", s)
    s = re.sub(r"\(\s*\)", "", s)
    s = re.sub(r"\(\s*,", "(", s)
    s = re.sub(r"\s{2,}", " ", s)
    s = s.strip()
    return (s[:220] + "…") if len(s) > 220 else s


def validator_text(subject):
    m = re.search(r"PASS (\d+/\d+|0 mismatches)", subject)
    return f"PASS {m.group(1)}" if m else "—"


def _pair_result(report_commit, content_commit, label):
    result = result_text(report_commit["subject"], label)
    if result.startswith(("record pushed SHA", "correct pushed SHA")):
        # Old-style report subjects are stubs; the content subject
        # carries the actual summary.
        result = result_text(content_commit["subject"], label)
    return result


def build_blocks(commits):
    by_prefix = {c["short"]: c for c in commits}
    used = set()
    rows = []  # (label, content_short, report_short, result, validator, kind)
    for idx, c in enumerate(commits):
        if c["sha"] in used or not is_report(c["subject"]):
            continue
        content = referenced_content_sha(c["subject"], by_prefix)
        if content is None:
            # No explicit SHA reference (CP26, CP34, CP35, M-D CP2): the
            # content commit is the immediately preceding commit.
            prev = commits[idx - 1] if idx > 0 else None
            if prev and prev["sha"] not in used and not is_report(prev["subject"]) \
                    and not prev["subject"].startswith("Merge "):
                content = prev
        if content is None:
            continue
        used.add(c["sha"])
        used.add(content["sha"])
        label = block_label(content["subject"])
        content_cell = content["short"]
        # A report may cover a second content commit ("content X + Y", M-G CP7).
        m2 = re.search(r"\+\s*([0-9a-f]{7})\b", c["subject"])
        if m2 and m2.group(1) in by_prefix and by_prefix[m2.group(1)]["sha"] not in used:
            used.add(by_prefix[m2.group(1)]["sha"])
            content_cell = f"`{content['short']}` + `{m2.group(1)}`"
        rows.append((label, content_cell, c["short"], _pair_result(c, content, label),
                     validator_text(c["subject"] + " " + content["subject"]),
                     "pair", commits.index(content)))
    for c in commits:
        if c["sha"] in used:
            continue
        used.add(c["sha"])
        s = c["subject"]
        ci = commits.index(c)
        if s.startswith("Merge "):
            rows.append(("— (merge)", c["short"], "—",
                         result_text(s, ""), "—", "merge", ci))
        elif s.startswith("fix(media)"):
            rows.append(("— (fix)", c["short"], "—",
                         result_text(s, ""), "—", "fix", ci))
        elif "erratum" in s:
            rows.append(("CP26 (erratum)", c["short"], "—",
                         result_text(s, ""), "—", "erratum", ci))
        else:
            label = block_label(s)
            rows.append((label, c["short"], "—",
                         result_text(s, label),
                         validator_text(s), "single", ci))
    rows.sort(key=lambda r: r[6])
    return rows, used


def build_index(rows, counts, merge_tree):
    lines = []
    lines.append("# MEDIA-02 — PR #119 Delivery Index (head `443d3e4`)")
    lines.append("")
    lines.append("Chi tiết đầy đủ từng khối bàn giao của PR #119, chuyển ra khỏi mô tả PR")
    lines.append("khi mô tả cũ (114.929 ký tự tại head `be9ccb8`) chạm trần truyền của connector")
    lines.append("(131.072 byte cho một tham số). Mô tả PR hiện tại là bản tóm tắt gọn")
    lines.append("(`MEDIA02_PR119_BODY_V2_20261113.md`); mọi SHA trong mô tả đều có ở bảng dưới.")
    lines.append("")
    lines.append("## Mốc xác minh")
    lines.append("")
    lines.append(f"- Head nhánh `muse/media-production-20261104`: `{counts['head_full']}`")
    lines.append(f"- Commit trên nhánh (diff từ merge-base `{MERGE_BASE}`): "
                 f"**{counts['commits']} commit / {counts['files']} file** "
                 "(khớp API PR: commits 187, changed_files 2381, additions 221756, deletions 0)")
    lines.append(f"- Integration: `{BASE_SHA}` (ls-remote 2026-11-13 ~04:44 JST, không đổi)")
    lines.append(f"- Mergeable: true / clean (API đọc 2026-11-13 ~04:44 JST tại head `{HEAD_SHORT}`; "
                 f"`git merge-tree --write-tree` vs `{BASE_SHA}` exit 0, 0 conflict, "
                 f"tree `{merge_tree}`)")
    lines.append("- Issue #116: 33 comment, mới nhất ACK `6833806995` "
                 "(SCENE-CLIPS FIX + WO37 M-G CP9, đăng 2026-11-13 ~04:32 JST); "
                 "trước đó Gói 39 của Codex `6815238814`, không chỉ đạo mới.")
    lines.append("- Scope audit toàn nhánh: 1 violation duy nhất là `.gitattributes` — "
                 "artifact của cách tính diff từ merge-base `cf17178` (chưa có các dòng LF); "
                 "file này byte-identical với integration, không phải lệch nội dung thật.")
    lines.append("")
    lines.append(HEADLINE)
    lines.append("")
    lines.append("## Bảng khối bàn giao (theo thứ tự thời gian)")
    lines.append("")
    lines.append("Cột Nội dung = commit chứa asset/tool; cột Báo cáo/Head = commit báo cáo "
                 "(cũng là head nhánh tại thời điểm khối đó xong).")
    lines.append("")
    lines.append("| Khối | Nội dung | Báo cáo/Head | Kết quả (tóm tắt) | Kiểm chứng |")
    lines.append("|---|---|---|---|---|")
    for label, content, report, result, val, kind, _sort in rows:
        result = result.replace("|", "/")
        content_cell = content if content.startswith("`") else f"`{content}`"
        lines.append(f"| {label} | {content_cell} | `{report}` | {result} | {val} |")
    lines.append("")
    lines.append("## Ghi chú")
    lines.append("")
    lines.append("- Cách đếm commit/file: `git rev-list --count cf17178..HEAD` và "
                 "`git diff --name-only cf17178 HEAD | wc -l` (cách đếm của mọi payload trước). "
                 "Một commit báo cáo làm head tăng thêm 4 file so với con số 'cumulative' trong "
                 "chính báo cáo đó (báo cáo md + 3 JSON) — luôn dùng head count cho payload.")
    lines.append("- Trường `base.sha` mà API pull trả về (`f383233…`) là giá trị cũ (merge PR #118), "
                 "không phải integration hiện tại; integration hiện tại xác minh bằng ls-remote.")
    lines.append("- Trạng thái: mọi VO/mix DRAFT_NOT_FINAL, NOT_AUDITIONED; final picture 32 shot "
                 "chờ character lock; 3 VO overrun để Codex quyết ở review; full OGV 720p deferred (Gói 39).")
    lines.append("")
    return "\n".join(lines) + "\n"


def validate_body(rows, counts, merge_tree):
    checks = []
    body_bytes = BODY_MD.read_bytes()
    body_text = body_bytes.decode("utf-8")
    checks.append({"name": "body_bytes_under_ceiling",
                   "pass": len(body_bytes) <= BODY_MAX_BYTES,
                   "detail": f"{len(body_bytes)} bytes (ceiling {BODY_MAX_BYTES}; "
                             f"connector argv ceiling 131072)"})
    checks.append({"name": "body_head_matches",
                   "pass": HEAD_SHORT in body_text,
                   "detail": f"head {HEAD_SHORT} present"})
    checks.append({"name": "body_counts_match_git",
                   "pass": f"{counts['commits']} commit" in body_text
                   and f"{counts['files']} file" in body_text,
                   "detail": f"{counts['commits']} commits / {counts['files']} files"})
    checks.append({"name": "body_merge_tree_matches",
                   "pass": merge_tree in body_text,
                   "detail": f"merge-tree {merge_tree}"})
    labels = {r[0] for r in rows}
    missing = [b for b in ("SCENE-CLIPS MANIFEST FIX", "WO37 M-G CP9",
                          "PROLOGUE V1 FIX", "WO37 M-B CP4", "WO37 M-D CP10",
                          "WO37 M-F CP2", "WO37 M-G CP8") if b not in labels]
    checks.append({"name": "body_blocks_in_index",
                   "pass": not missing,
                   "detail": "all 7 newest blocks in index" if not missing
                   else f"missing: {missing}"})
    # SHA classification for every backticked token in the body.
    import hashlib
    unresolved, classified = [], {"git_commit": 0, "git_tree": 0,
                                  "known_file_sha": 0, "known_github_id": 0}
    for tok in sorted(set(re.findall(r"`([0-9A-Za-z_./\-…]+)`", body_text))):
        tok = tok.rstrip("…")
        if not re.fullmatch(r"[0-9a-f]{7,40}", tok) and tok not in KNOWN_GITHUB_IDS:
            continue  # not an identifier (paths, counts, cue names...)
        if tok in KNOWN_GITHUB_IDS:
            classified["known_github_id"] += 1
            continue
        if tok in KNOWN_FILE_SHA_PREFIX:
            classified["known_file_sha"] += 1
            continue
        if git_ok("cat-file", "-e", f"{tok}^{{commit}}"):
            classified["git_commit"] += 1
        elif git_ok("cat-file", "-e", f"{tok}^{{tree}}"):
            classified["git_tree"] += 1
        else:
            unresolved.append(tok)
    checks.append({"name": "body_identifiers_resolve",
                   "pass": not unresolved,
                   "detail": f"classified={classified}; unresolved={unresolved}"})
    # Cross-check the prologue fixed-mix sha prefix against the fix manifest
    # (repo-side source of truth; the working clone holds an LFS pointer for
    # the WAV itself, so hash the manifest record, not the pointer bytes).
    # The full sha was already verified over real bytes by M-G CP9's
    # fresh-checkout run (validator 126/126).
    mf = REPO / "Art_Source/Audio/Muse/MIX/PROLOGUE_DRAFT_V1_FIXED" \
        / "PROLOGUE_MIX_V1_FIXED_manifest_v1.json"
    mix_sha, mix_size = "", 0
    if mf.exists():
        mdata = json.loads(mf.read_text())
        mix_sha = mdata.get("sha256", "")
        mix_size = mdata.get("sizeBytes", 0)
    checks.append({"name": "prologue_mix_sha_prefix",
                   "pass": mix_sha.startswith("4f8224e1") and mix_size == 16774542,
                   "detail": f"manifest sha256 {mix_sha[:12]}…, size {mix_size} B"})
    return checks, len(body_bytes), len(body_text), \
        hashlib.sha256(body_bytes).hexdigest()


def main():
    base = sys.argv[sys.argv.index("--base") + 1] if "--base" in sys.argv else BASE_SHA
    commits = parse_log()
    rows, used = build_blocks(commits)
    assert len(used) == len(commits) == 187, \
        f"index must cover all 187 commits, got {len(used)}/{len(commits)}"
    counts = {
        "head_full": git("rev-parse", "HEAD"),
        "commits": int(git("rev-list", "--count", f"{MERGE_BASE}..HEAD")),
        "files": len(git("diff", "--name-only", MERGE_BASE, "HEAD").splitlines()),
    }
    assert counts["head_full"].startswith(HEAD_SHORT), counts
    mt = subprocess.run(["git", "merge-tree", "--write-tree", "HEAD", base],
                        cwd=REPO, capture_output=True, text=True)
    merge_tree = mt.stdout.splitlines()[0].strip() if mt.stdout else ""
    merge_ok = mt.returncode == 0 and len(mt.stdout.splitlines()) == 1
    assert merge_ok, f"merge-tree not clean: rc={mt.returncode} out={mt.stdout[:500]}"
    index_text = build_index(rows, counts, merge_tree)
    INDEX_MD.write_text(index_text)
    checks, body_bytes, body_chars, body_sha = validate_body(rows, counts, merge_tree)
    checks.append({"name": "index_covers_all_commits",
                   "pass": len(used) == 187,
                   "detail": f"{len(used)} commits in {len(rows)} table rows"})
    checks.append({"name": "merge_tree_clean",
                   "pass": merge_ok,
                   "detail": f"tree {merge_tree} vs base {base}"})
    verdict = "PASS" if all(c["pass"] for c in checks) else "FAIL"
    validation = {
        "tool": "build_pr119_body_restructure_v1.py",
        "generated_at_jst": datetime.now(timezone.utc).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S %Z"),
        "head": HEAD_SHORT,
        "head_full": counts["head_full"],
        "base_integration": base,
        "merge_base": MERGE_BASE,
        "commits": counts["commits"],
        "files_changed": counts["files"],
        "merge_tree": merge_tree,
        "body": {"path": str(BODY_MD.relative_to(REPO)),
                 "bytes": body_bytes, "chars": body_chars,
                 "sha256": body_sha},
        "index": {"path": str(INDEX_MD.relative_to(REPO)),
                  "rows": len(rows), "commits_covered": len(used)},
        "checks": checks,
        "verdict": verdict,
    }
    VALIDATION_JSON.write_text(json.dumps(validation, indent=2,
                                         ensure_ascii=False) + "\n")
    print(f"index rows: {len(rows)}, commits covered: {len(used)}")
    print(f"body: {body_bytes} bytes / {body_chars} chars, sha256 {body_sha[:12]}…")
    print(f"merge-tree: {merge_tree} (exit 0, clean)")
    for c in checks:
        print(f"[{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['detail']}")
    print(f"verdict: {verdict}")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
