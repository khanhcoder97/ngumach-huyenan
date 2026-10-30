# Muse — Con dấu qua phố, đạo diễn CIN_006

Bản ứng viên để làm storyboard/keyframe trước. Source canonical `Cinema_Production_Pack_v1.json`, CIN_006/C1-06:18giây, giữ3shot có sẵn, mỗi shot6giây. Prompt máy đọc tại `muse_cinema_candidate.json`. Đây là cảnh sau ledger/forge/archive và đối chiếu, trước báo cáo; không phát sớm để kể đáp án, không gán end video thành quest completed.

## Trải nghiệm cần giữ

Khán giả vừa đi qua thành lớn, hỏi ba nơi và thấy cách một giả thuyết hình thành. Cảnh ngắn gom lại đường giấy đã đi; chỗ trống cuối đường vẫn trống. Chợ có giao dịch khác tiếp diễn, không đồng loạt quay lại nhìn avatar. Không zoom toàn thành vào một sân nhỏ. Lộ trình ba điểm trong gameplay giữ khoảng cách/quy mô; montage chỉ nhớ lại các nơi đã tới, không teleport NPC.

640×360 logical pixel,16:9; cluster rõ, nearest-neighbor khi upscale. Hold pose8–12fps trong delivery30fps theo pack; không AI nội suy mặt/biến ngón tay hoặc pan camera kiểu3D. UI/subtitle/font rendering làm riêng. Không ép avatar thành mẫu nam/nữ/môn phái cố định. Cần reference/model sheet được duyệt của Sầm, Hạ Mặc và palette Thăng Long; thiếu thì bàn giao storyboard có nhãn, không đoán final costume.

| Shot | Hành động và nhịp | Âm thanh / phần tránh diễn sai |
|---|---|---|
| CIN_006_S01,0–6s | Quầy Sầm dưới mái hổ phách. Ba giấy gấp cạnh cân; ngón tay giữ mép lật. Xe/người qua sau lưng. Chờ cân đứng một nhịp. | Cân, bánh xe, tiếng chợ tách lớp; không sting bắt tội, không biểu cảm bị bắt quả tang. Dấu trên giấy là hình thiết kế, không chữ do model bịa. |
| CIN_006_S02,6–12s | Cận dấu đồng và giấy: một gờ kéo khác hai vết ép. Tay dừng trước sợi nhựa, không phủi đi. Hai mẫu đặt cạnh, không chồng khít giả. | Lò ở xa, giấy ở gần. Có descriptive text/icon tương đương ở UI, không giấu clue trong một pixel xanh hoặc một âm độc quyền. Nhựa không phát sáng thành thực thể mới. |
| CIN_006_S03,12–18s | Hạ Mặc đặt ba bản chép theo chặng, chừa khoảng chưa biết; phủ tờ sạch lên vùng tên theo shot nguồn, đưa bản sao. Chiếc ghế còn bên cạnh. | Kết bằng tiếng chợ, không nhạc chiến thắng/hiện phản diện. Trả quyền cho người chơi báo cáo. Không gọi lệnh bắt ai. |

Thoại nguồn có “Ba thứ cùng đi qua một tuyến. Chưa có thứ nào bảo người bán biết mình đang chở gì.” Bản đọc mới dùng “Tới đây ta theo được. Chỗ trống này giữ nguyên.” như **alternate take**, không thay canonical dialogueLines hoặc ghép cả hai thành lời giảng. Khi khóa animatic chọn một take có nhãn version; VO/SRT tách track để sửa mà không render lại tranh. Chưa có VO/video được tạo trong packet này.

## Packet bàn giao cần có

Ba keyframe, contact sheet có shotID/timecode, animatic18s, renderpixel30fps, still fallback, SRT riêng, ambience/music/voice stems nếu làm audio, source/version/model references và report lỗi. Check continuity dấu/sợi/giấy, vật cầm tay, cổ tay và hướng ánh sáng giữa các shot. Không thêm watermark hoặc subtitle baked-in. Fallback có recap cùng lượng thông tin; skip/replay không đổi gameplay.

Hạ Mặc/Sầm hiện chưa có binding Thăng Long thống nhất giữa quest/cinema và spawn registry. Muse được dựng scene candidate độc lập; không sửa placement/gameplay hoặc nhân đôi persistent NPC ID để chữa. Gửi producer yêu cầu phase/anchor cụ thể, tiếp keyframe và các shot không phụ thuộc.
