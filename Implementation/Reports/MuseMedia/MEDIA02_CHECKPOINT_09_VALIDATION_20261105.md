# MEDIA-02 — Checkpoint 09: kiểm chứng V4 toàn bộ deliverable media (M7)

- Ngày: 2026-11-05 (JST). Agent: Muse (chỉ media, theo policy `agent_scope_v2.json` / work 28 + work 29).
- Nhánh: `muse/media-production-20261104`. Base đồng bộ: integration HEAD `cf17178` (không đổi so với checkpoint 01–08; `git fetch` lượt này không có commit mới trên integration hay trên nhánh media).
- Khối hoàn thiện trong lượt này: **M7/V4 — kiểm chứng chéo toàn bộ deliverable MEDIA-02 (checkpoint 01–08) đối chiếu byte thật trên đĩa**, thay vì đo lại loudness. Issue #116 đọc qua trang công khai: body không đổi, không có chỉ đạo mới làm thay đổi DEC-MEDIA-P0; ACK checkpoint 09 trên issue #116 vẫn cần thẻ duyệt của luồng chính (lượt chạy định kỳ không treo chờ, không tự đăng comment).

## 1. Phạm vi kiểm chứng (không đo lại loudness)

Công cụ mới chỉ đọc cây repo và đối chiếu với các pack/báo cáo đã giao; loudness/true peak vẫn là số đo của checkpoint 02/04/07/08 từ byte thật, không bị ghi đè hay ghi PASS giả ở đây:

| Nhóm | Đối chiếu |
|---|---|
| Audio pack nhạc + ambience (checkpoint 07) | 22 cue × runtime OGG + master FLAC = 44 file: tồn tại, không phải con trỏ LFS, byte, sha256, codec, 48 kHz, kênh, thời lượng (±0,02 s) |
| Audio pack SFX + UI (checkpoint 08) | 173 cue × 3 variant × runtime WAV + master FLAC = 1038 file: cùng 6 tiêu chí trên |
| Pool stem P0 (checkpoint 02) | 11 file stem: cùng 6 tiêu chí trên (4 stinger cinema, 3 nhạc, 4 ambience) |
| Timing + SRT toàn campaign (checkpoint 01/05/06) | 20 cảnh: shot nối tiếp từ 0, mỗi shot đúng 6 s, tổng shot = durationSeconds; cửa sổ thoại nằm trong shot; SRT giải mã UTF-8 strict, chuẩn NFC, số cue = số thoại trong timing, từng cue khớp cửa sổ và khớp từng ký tự với thoại timing |
| Animatic P0 (checkpoint 03) | MP4 H.264 + OGV Theora trong `ClientGodot/assets/cinematics/`: 640×360, thời lượng 72 s; poster 640×360; 12 panel: sha256 khớp `P0_animatic_outputs_v1.json`, kích thước 640×360 |
| VO dự thảo P0 (checkpoint 04) | 3 take WAV: sha256 khớp manifest, thời lượng khớp manifest (±0,02 s), thời lượng take ≤ cửa sổ; timeline VO 72,0 s |

## 2. Deliverable

| Đường dẫn | Nội dung |
|---|---|
| `Tools/MediaProduction/Muse/validate_media_deliveries.py` | Công cụ kiểm chứng V4: từ chối con trỏ LFS thay vì đo giả; exit 0 khi không có mismatch, exit 1 khi có mismatch; `--out` ghi JSON |
| `Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_09_VALIDATION_20261105.json` | Kết quả kiểm chứng dạng máy đọc (counts, mismatches, notes, verdict, limits) |
| Báo cáo này | `Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_09_VALIDATION_20261105.md` |

## 3. Kết quả: PASS — 0 mismatch

- **Audio: 1093/1093 file khớp tuyệt đối** (44 nhạc/ambience + 1038 SFX/UI + 11 stem P0; stem P0 trùng lặp với các file đã nằm trong hai pack nên tổng số lần kiểm là 1093, không phải 1093 file riêng biệt). Không file nào mất, không file nào còn là con trỏ LFS, không lệch byte/sha256/codec/tần số lấy mẫu/kênh/thời lượng.
- **Timing + SRT: 20/20 cảnh khớp.** 63 shot đều 6 s, tổng 378 s. 21 thoại trong timing = 21 cue SRT (P0 3 + CIN_006 1 + campaign 17), từng cue khớp cửa sổ và khớp từng ký tự với thoại timing; tất cả SRT đều UTF-8 strict và NFC.
- **Animatic: 12/12 panel khớp sha**, MP4 H.264 640×360 thời lượng 72 s, OGV Theora 640×360 thời lượng 72 s, poster 640×360.
- **VO: 3/3 take khớp sha và thời lượng**, đều vừa cửa sổ; timeline VO 72,0 s.
- Ghi chú duy nhất không phải lỗi: ffprobe báo `avg_frame_rate 0/0` cho file OGV (đặc tính metadata Theora), trong khi thời lượng 72 s và codec/dims đều khớp — không kết luận lỗi khung hình từ đó; checkpoint 03 đã ghi OGV chỉ có 211 stored frame do Theora gộp frame giữ nguyên.

## 4. Kiểm chứng đã chạy

- Lệnh: `python3 Tools/MediaProduction/Muse/validate_media_deliveries.py --out Implementation/Reports/MuseMedia/MEDIA02_CHECKPOINT_09_VALIDATION_20261105.json` → exit 0, `verdict: PASS`, `mismatches: 0`, thời gian chạy ~78 s (chủ yếu là sha256 + ffprobe cho 1093 file).
- Scope: `Tools/Coordination/check_agent_scope.py --base cf17178 --head HEAD --branch muse/media-production-20261104` → xem mục 6 (chạy trước khi push; commit checkpoint 09 chỉ push khi đạt 0 violations).

## 5. Giới hạn còn mở (không giấu)

- Đây là kiểm chứng toàn vẹn + nhất quán, KHÔNG phải mix PASS, KHÔNG nghe tai: vòng lặp ambience (đặc biệt rain_heavy, checkpoint 07), độ cân bằng VO (S05 to hơn ~5,5 LUFS, checkpoint 04) và 4 khuyết điểm panel storyboard (checkpoint 03) vẫn nguyên trạng chờ xử lý riêng.
- Tất cả cue vẫn `RENDERED_CANDIDATE` + `REQUIRES_PRESENTATION_ADAPTER` — đã đo và đã kiểm chứng toàn vẹn, chưa nối runtime, chưa phải final.
- Cửa sổ thoại campaign vẫn PROPOSED, chỉ CIN_001_S05 là DECIDED; kiểm chứng này chỉ khẳng định SRT khớp timing đã giao, không khẳng định đạo diễn đã duyệt cửa sổ.
- VO vẫn là bản dự thảo TTS (giọng hư cấu hệ thống, không clone giọng thật), chưa nghe thử bằng tai, chưa copy sang runtime.

## 6. Trạng thái push (điền sau khi chạy scope audit)

- Scope audit: _chưa chạy lúc viết bản nháp — xem commit message sau push_.
- Commit checkpoint 09: _điền SHA sau khi push + xác minh ls-remote_.
- PR #119: vẫn mở, chưa merge; commit này nối tiếp lên cùng nhánh media, KHÔNG mở PR mới, KHÔNG tự merge.
- Khối tiếp theo: M6 runtime delivery (copy có kiểm chứng các deliverable P0/campaign đã kiểm chứng này sang `ClientGodot/assets/cinematics/` + `ClientGodot/assets/audio/` kèm manifest runtime), hoặc VO dự thảo campaign khi cửa sổ được xác nhận.
