# MEDIA-02 — Checkpoint 05: timing CIN_006 (P1) theo DEC-MEDIA-P0 Q3/Q4

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base đồng bộ: integration HEAD `cf17178` (không đổi so với checkpoint 01–04; `git fetch` lượt này không có commit mới).
- Khối hoàn thiện trong lượt này: **(d) timing CIN_006 (P1)** — khối tiếp theo sau (a) đo stem, (b) animatic P0, (c) VO P0 đã xong ở checkpoint 02/03/04.

## 1. Nguồn đọc (không bịa)

- `Implementation/Content/Narrative/Cinema_Production_Pack_v1.json`, scene CIN_006 / quest C1-06, “Con dấu qua phố”: 18 giây, 3 shot × 6 giây, playback `OPTIONAL_SKIP_SAFE_LAYER`, fallback “Approved still keyframe plus localized recap; never blocks quest”, dialogueLines canonical duy nhất của Hạ Mặc.
- `docs/narrative/workshop/MUSE_THANG_LONG_CIN006_DIRECTION_vi.md`: alternate take “Tới đây ta theo được. Chỗ trống này giữ nguyên.” — ghi rõ không thay canonical, không ghép hai take.
- `Client/Assets/AudioManifests/game_audio_v1.json`, bindings.cinema CIN_006: stinger `SFX/CINEMA/reveal`, `REQUIRES_PICTURE_LOCK_NOT_SYNCED`.
- DEC-MEDIA-P0-20261105: Q3 alternate take có takeId/version riêng; Q4 Hạ Mặc/Sầm chỉ cinematic-only staging.

## 2. Deliverable

`Implementation/Content/Narrative/Deliveries/CIN_006/`:

| File | Nội dung |
|---|---|
| `CIN_006_timing_v1.json` | 18s / 3 shot: S01 0–6 MEDIUM_STATIC, S02 6–12 DETAIL_LOCKED, S03 12–18 MEDIUM_STATIC; staging Q4; alternate take tách riêng |
| `CIN_006_vi.srt` | UTF-8, NFC, 1 cue, chỉ thoại canonical |
| `CIN_006_timing_manifest_v1.json` | sha256 nguồn + SRT, tốc độ đọc, trạng thái cửa sổ |

Công cụ tái lập: `Tools/MediaProduction/Muse/build_cin006_timing.py` (đọc pack + direction + manifest audio, tự kiểm 18s/3 shot/6s mỗi shot rồi mới ghi).

## 3. Quyết định áp dụng — và cái gì vẫn là PROPOSED

- **Canonical giữ nguyên:** thoại SRT là câu Hạ Mặc trong pack: “Ba thứ cùng đi qua một tuyến. Chưa có thứ nào bảo người bán biết mình đang chở gì.” (82 ký tự).
- **Cửa sổ thoại là PROPOSED, không phải canonical:** pack không gán shot/timecode cho câu này. Đặt dự thảo ở S03 (shot có Hạ Mặc, onscreen) 12.5–17.5s — 0.5s headroom mỗi đầu, 16.4 ký tự/giây (trong khoảng gợi ý 12–17). Chờ đạo diễn/Codex xác nhận trước khi coi là SRT final, theo đúng quy ước checkpoint 01 cho CIN_002/CIN_004.
- **Alternate take không thay canonical (Q3):** ghi riêng trong timing JSON với `takeId: CIN_006_ALT_T01`, `version: v1-alt`, `status: ALTERNATE_TAKE_DOES_NOT_REPLACE_CANONICAL`, `windowSeconds: null` (chưa gán cửa sổ — chỉ gán khi animatic lock chọn take này), và **không có trong SRT**.
- **Staging cinematic-only (Q4):** timing JSON ghi `staging: CINEMATIC_ONLY_NO_PERSISTENT_ID_DUPLICATION_NO_SPAWN_MOVE` — không nhân đôi persistent ID NPC_HA_MAC/NPC_SAM_CHU_QUY, không dời default spawn.
- **Stem:** chỉ liệt kê stinger đã bind trong manifest audio (`SFX/CINEMA/reveal`), `stemStatus: CANDIDATE_POOL_NOT_LOCKED`. Pool stem P0 đã đo không có loop ambience chợ Thăng Long nên không gán ambience nào cho cảnh này — không bịa stem chợ.

## 4. Giới hạn còn mở

- Chưa có keyframe/character lock đã duyệt cho Hạ Mặc/Sầm: chỉ chặn final picture của các shot có nhân vật, không chặn timing/SRT/audio (theo quy tắc DEC).
- Cửa sổ thoại S03 vẫn PROPOSED (xem mục 3).
- Issue #116 lượt này không đọc trực tiếp được qua GitHub connector: tool `get_issue` không được MCP server quảng cáo, `issue_read` nằm ngoài tập read-only đã duyệt nên connector yêu cầu thẻ duyệt write-capable — không treo chờ thẻ trong lượt chạy định kỳ; trạng thái cuối đã biết vẫn là OPEN 6 comment (từ các lượt trước). Việc cần thẻ duyệt (ACK checkpoint 05 + media PR) ghi trong báo cáo để luồng chính xử lý.
- Chưa làm video/VO cho CIN_006 — đây là checkpoint timing/SRT, chưa phải bản xem.

## 5. Khối tiếp theo

- (e) các pack tiếp của M3/M4/M5: video campaign toàn cục, nhạc, SFX/ambience theo cue ID — bắt đầu từ việc đối chiếu cue manifest với các cảnh P1 còn lại trước khi sinh pack mới; hoặc storyboard/animatic CIN_006 khi có character lock.
