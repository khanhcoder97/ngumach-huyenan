# MEDIA-02 — Checkpoint 06: pack timing M3 cho toàn bộ campaign (16 cảnh còn lại)

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base đồng bộ: integration HEAD `cf17178` (không đổi so với checkpoint 01–05; `git fetch` lượt này không có commit mới).
- Khối hoàn thiện trong lượt này: **(e) pack tiếp của M3 — timing + SRT cho 16 cảnh chưa có deliverable**, hoàn tất phủ timing toàn campaign: 20 cảnh / 63 shot / 378 giây (trước đó đã có P0 CIN_001/002/004 = 72s và P1 CIN_006 = 18s).

## 1. Nguồn đọc (không bịa)

- `Implementation/Content/Narrative/Cinema_Production_Pack_v1.json`: 20 cảnh, 63 shot, 378 giây; mỗi cảnh còn lại 18s / 3 shot × 6s, thoại canonical dạng "Người nói: câu thoại", playback `OPTIONAL_SKIP_SAFE_LAYER`, fallback "Approved still keyframe plus localized recap; never blocks quest".
- `Client/Assets/AudioManifests/game_audio_v1.json`, bindings.cinema: cả 20 cảnh đều bind stinger `SFX/CINEMA/reveal`, `REQUIRES_PICTURE_LOCK_NOT_SYNCED`, kèm revealTier (OPENING / CHAPTER_1–6 / ENDING / EPILOGUE).
- DEC-MEDIA-P0-20261105: Q4 staging cinematic-only áp cho các cảnh có NPC_HA_MAC / NPC_SAM_CHU_QUY; Q2 (Ly An voice off-screen) chỉ quyết cho CIN_004 nên KHÔNG khái quát hoá sang các cảnh khác.

## 2. Deliverable

`Implementation/Content/Narrative/Deliveries/`:

| Nhóm | Nội dung |
|---|---|
| `CIN_003, CIN_005, CIN_007–CIN_020` (trừ CIN_006) | Mỗi cảnh: `{SID}_timing_v1.json` (18s / 3 shot, camera + referenceRequirement từ pack, revealTier, candidateStems, fallback) + `{SID}_vi.srt` (UTF-8, NFC, thoại canonical) |
| `CAMPAIGN_timing_manifest_v1.json` | Tổng hợp 16 cảnh / 48 shot / 288 giây / 17 cue + sha256 nguồn + sha256 từng SRT + quy tắc đặt cửa sổ |
| `Tools/MediaProduction/Muse/build_campaign_timing.py` | Công cụ tái lập: đọc pack + manifest audio, assert 20/63/378 rồi mới ghi; SRT nào cũng được kiểm khớp từng ký tự với thoại canonical của pack |

Cộng với 90 giây đã có (P0 72s + CIN_006 18s), toàn campaign nay có timing + SRT draft cho đủ 378 giây.

## 3. Quy tắc đặt cửa sổ — và cái gì vẫn là PROPOSED

- **Tất cả 17 cửa sổ đều là PROPOSED_ANIMATIC_PLACEMENT, không phải canonical:** pack không gán shot/timecode cho bất kỳ câu nào trong 16 cảnh này. Chỉ có CIN_001_S05 (24.8–28.5s) là DECIDED theo DEC-MEDIA-P0 Q1, và nó không thuộc pack này.
- Quy tắc thống nhất: một câu thoại đặt ở shot cuối S03 (12.0–18.0s), lùi 0.5s mỗi đầu → 12.5–17.5s (5.0s). Hai ngoại lệ bắt buộc vì tốc độ đọc, không vì sở thích:
  - CIN_011 (87 ký tự): cửa sổ 5.0s sẽ đọc 17.4 ký tự/giây, vượt hướng dẫn 12–17 dùng ở checkpoint 05 → nới thành 12.2–17.8s (5.6s, 15.54 ký tự/giây, headroom 0.2s mỗi đầu), ghi rõ `widenedForRate`.
  - CIN_018 (2 câu, 42 + 78 = 120 ký tự): một cửa sổ 5.0s sẽ đọc 24.0 ký tự/giây → tách thành S02 6.5–11.5s (câu Cơ Vô Tướng, 8.4 ký tự/giây) + S03 12.5–17.5s (câu Người chơi, 15.6 ký tự/giây). Không gộp, không bỏ, không sửa câu nào.
- Tốc độ đọc các cue còn lại: 7.4–14.2 ký tự/giây. Các câu ngắn đọc chậm hơn hướng dẫn 12–17 là có chủ ý — giữ cửa sổ thống nhất để VO có nhịp thở, và con số được báo công khai trong manifest, không giấu.
- `onscreen` chỉ là `true` khi ID người nói nằm trong danh sách characters của pack cho cảnh đó; các trường hợp còn lại là `null` (không rõ), không bao giờ là `false`: pack không liệt kê characters (CIN_005, CIN_009, CIN_020), chỉ liệt kê nhân vật khác (CIN_017 chỉ có BOSS_TIDE_SERPENT trong khi người nói là Đội trưởng thợ lặn), hoặc câu của Người chơi ở CIN_018 — không có nguồn nào chứng minh người nói ngoài màn hình nên không đoán.
- Staging Q4: các cảnh CIN_010, CIN_011, CIN_012, CIN_016 ghi `CINEMATIC_ONLY_NO_PERSISTENT_ID_DUPLICATION_NO_SPAWN_MOVE` — không nhân đôi persistent ID, không dời default spawn.
- Stem: mỗi cảnh chỉ liệt kê stinger đã bind trong manifest (`SFX/CINEMA/reveal`), trạng thái `CANDIDATE_POOL_NOT_LOCKED`. Không gán ambience/nhạc riêng cho cảnh nào — pool stem P0 đã đo không có ambience riêng cho các cảnh này, không bịa stem.

## 4. Kiểm chứng đã chạy

- Pack: 20 cảnh / 63 shot / 378 giây khớp; 16 cảnh trong pack này mỗi cảnh 18s / 3 shot × 6s; tổng 48 shot / 288 giây / 17 cue.
- SRT: 16/16 file UTF-8 + NFC; văn bản từng cue khớp từng ký tự với thoại canonical của pack (kiểm bằng code, không đọc mắt).
- Timing: 16/16 file đủ 3 shot, tổng thời lượng shot = 18s; mọi cửa sổ thoại nằm trong shot của nó.
- Scope: `Tools/Coordination/check_agent_scope.py --base cf17178 --head HEAD --branch muse/media-production-20261104` → 48 changed paths, 0 violations (chạy sau khi stage, trước khi commit).

## 5. Giới hạn còn mở

- Chưa có keyframe/character lock đã duyệt cho các cảnh này: chỉ chặn final picture của shot có nhân vật, không chặn timing/SRT/audio (theo quy tắc DEC).
- Mọi cửa sổ thoại trong pack này vẫn PROPOSED — cần đạo diễn/Codex xác nhận trước khi coi SRT là final, theo đúng quy ước checkpoint 01/05.
- Issue #116 lượt này vẫn không đọc trực tiếp được qua GitHub connector/gh CLI (gh chưa đăng nhập; theo checkpoint 05, `issue_read` nằm ngoài tập read-only đã duyệt nên connector yêu cầu thẻ duyệt write-capable) — không treo chờ thẻ trong lượt chạy định kỳ; trạng thái cuối đã biết vẫn là OPEN, 6 comment (từ các lượt trước). Việc cần thẻ duyệt (ACK checkpoint 06 + media PR) ghi trong báo cáo để luồng chính xử lý.
- Chưa làm video/VO cho 16 cảnh này — đây là checkpoint timing/SRT, chưa phải bản xem. Khối tiếp theo: (e) tiếp — pack nhạc / SFX-ambience theo cue ID (M4/M5), hoặc VO dự thảo cho các câu campaign khi có cửa sổ được xác nhận.
