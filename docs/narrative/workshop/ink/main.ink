// NGUMACH narrative reading-room. No runtime bindings, rewards or live story flags.
INCLUDE p00_01.ink
INCLUDE p00_02.ink
INCLUDE p00_03.ink
INCLUDE p00_04.ink
INCLUDE p00_05.ink

VAR kept_distance = false
VAR water_report = 0
VAR heard_first = false
VAR held_letter = false

-> reading_room
=== reading_room ===
# scene:READING_ROOM
# kind:AUTHORING_ONLY
NGŨ MẠCH: HUYỀN ẤN · BẾN MƯA
Bản đọc biên kịch. Các mốc chiến đấu, nhặt vật và trả nhiệm vụ dưới đây là mô phỏng do người đọc chọn. Không kết nối tài khoản, không thưởng vật phẩm và không mở khóa cốt truyện trong game.
Bạn có thể đọc liền tuyến hoặc vào một cảnh để biên tập. Mỗi nhiệm vụ đặt lại trạng thái lựa chọn riêng khi đọc lại.
+ [Bắt đầu từ Thư qua bến] -> p01_rope
+ [Chuông không người] -> p02_bank
+ [Dưới mặt đầm] -> p03_call
+ [Người giữ bờ] -> p04_depart
+ [Mảnh ấn đầu tiên] -> p05_before
+ [Đóng bản đọc] -> END
