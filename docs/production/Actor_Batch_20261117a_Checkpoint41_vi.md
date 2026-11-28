# Mốc 41/50 nguồn Thạch Chùy — Phá Nham

Ngày 17/11/2026. Bổ sung năm hướng nhân vật và ba VFX Phá Nham sau mốc 33 nguồn. Tổng 41 sheet, 656 pose/pha nguồn, 47 phiên bản kể cả sáu bản cũ. Còn chín nguồn Sơn Thần Giáng Thế trong gói 50; phạm vi thư viện đầy đủ của game vẫn tiếp tục.

## Nhân vật và điều cần chỉnh

Phá Nham là một lần hạ trọng tâm, ghì chùy, lao rồi hãm và hồi thế. Mỗi hướng có 16 hình nguyên khối, giữ một chùy và tay nối với thân. Không dùng chu kỳ chạy tám frame nhân đôi. PNG không quyết định di chuyển, va chạm hoặc xuyên địa hình.

Qua native, hướng Bắc có độ nghiêng thân về chéo phải lớn; cần xác minh hoặc vẽ lại trục lao chính Bắc. Root hiện dò theo chân vươn, chưa chứng minh pha lao/nhấc chân đã khớp gốc thế giới. Hai hướng chéo dùng đề xuất dark-sole riêng gắn đúng SHA, bù 10 px ở SE và 9 px ở NE vì bộ dò màu bỏ viền giày tối. Giới hạn dò chung không bị nới. Các đề xuất vẫn chờ xem ở camera cố định cùng dịch chuyển thật, va chạm và idle.

Montage nhỏ cắt đầu chùy ở vài tư thế nghiêng mạnh của N/SE. PNG gốc và viewport native đầy đủ vẫn chứa cả nhân vật/vũ khí; montage rộng `_source_samples.png` đã được xem và ghi thêm mã băm. Không dùng crop nhỏ để kết luận PNG bị mất nét vẽ.

## Ba component VFX

| Component | Nơi gắn đề xuất | Quy tắc |
| --- | --- | --- |
| `sk_tc_05_dash_trail_component` | Điểm phát bụi sau chân, bụi kéo về local −X | Bụi đất thấp, ngắn; vị trí phát và dịch chuyển do gameplay cung cấp |
| `sk_tc_05_hit_impact_component` | Điểm va trúng đã được xác nhận | Một vòng mỏng tâm rỗng và vài mảnh nhỏ; không tự suy diễn hit từ hình ảnh |
| `sk_tc_05_stop_dust_component` | Chân tại điểm dừng thật, kể cả bị chặn | Bụi lắng nhỏ, không gây damage và không giả hiệu ứng trúng mục tiêu |

Đã thay gốc tâm ô bằng đề xuất front/baseline cho trail, baseline cho bụi dừng và footprint cho va trúng. Bản native trước khi sửa được lưu riêng tại máy để đối chiếu. Những mảnh vỡ cuối bất đối xứng và biên bụi thay đổi vẫn cần chỉnh tay trong bản ghép kỹ năng; pivot riêng chưa phải bằng chứng điểm va chạm vật lý đúng.

## Kiểm chứng và bàn giao

41 project và 41 video nguồn được đối chiếu receipt, SHA PNG/project/movie, trace đủ 16 pha và giải mã 7.380 frame. Ghi chú thủ công gắn đúng mã băm; các hold hướng/root và biểu cảm Khiêu Chiến vẫn còn nguyên. Không có phê duyệt nguồn C hoặc thay catalogue/runtime gameplay ở mốc này.

Build và Studio đã kiểm chứng ở mốc 33 với 0 lỗi/cảnh báo, 106.016 assertions trên 516 mục và 119 test công cụ. Thay đổi sau đó chỉ bổ sung source, metadata và công cụ đăng ký/review; không thay mã client. Các native mới dùng cùng binary đã kiểm chứng. Video clock 60 FPS không đo FPS thật của game.

Mở `Implementation/Reports/Evidence/Actor_Batch_20261116c/Candidate_Studio/<ID>/project.json` để chỉnh tay. Ảnh/prompt nằm trong `Art_Source/Actor_Library_20261107/Candidates_20261116c/`; 50 job portable phân biệt nguồn hiện có/chưa tạo. Bản ghép Thiết Bích hướng Nam và các giới hạn của nó vẫn được mô tả ở Checkpoint33.

Tiếp tục chín nguồn còn thiếu, sửa các nguồn bị hold, chuẩn hóa idle và chuyển động tác, ghép đủ tám hướng và camera rộng với cue gameplay. Các lớp khác, quái, boss, NPC, map, UI và phần còn lại của thư viện game chưa hoàn tất.
