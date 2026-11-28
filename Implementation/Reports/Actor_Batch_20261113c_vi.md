# Bàn giao asset 20261113c

Bổ sung **20 sheet chọn /320 khung nguồn**: Tầm Long, Kiếm Trận, Thiết Y ×N/NE/E/SE/S ×16, và năm VFX. Giữ chibi nguyên khối, PNG nguyên byte, prompt thực; giữ bản Bắc đâm sai trục và bản vỡ khiên mọc lại trong lịch sử.

Nguồn có timing từng khung: Tầm Long0,15/0,20/0,24s; Kiếm Trận0,10/0,12/0,14s +0,24s hồi trình bày; Thiết Y0,80s xem, tách khiên4s. Library/Studio giữ seek/resume và cùng lịch khung. Pin binding bao gồm timing. BOOT_CORE_FOOT loại mũi kiếm/chuôi khỏi điểm neo giày, chiều cao trung tính cố định, không sửa bitmap/collider.

VFX gồm vệt lướt và bụi dừng, ánh kim nhận khiên, vỡ khiên, tan tự nhiên. Kiếm Trận dùng lại cung16 khung cũ. Mới kiểm nguồn độc lập, chưa ghép mọi body/VFX hoặc bind sự kiện combat. Readout video cập nhật theo pose render cùng tick; ảnh đại diện lấy giữa chu kỳ.

Kiểm:44 Python tests; build0 warning/error; Godot import; library14.424 assertions; Studio70.890/238 entries. Baseline46 PNG nguyên SHA256;178 runtime copies khớp nguồn.10 MP4 native chọn,3 lịch sử, ảnh/dải mẫu/pin/decode audit; offline60 bước/s chưa là benchmark gameplay.

181 page structure,62/1008 job đủ nguồn,26 job đủ nguồn kiểm source;946 còn thiếu,21 HOLD cũ và full VFX atlas sai hàng. Minh Kiếm10/12 clip đủ dữ liệu xem, chưa nghiệm thu toàn class.

[Chi tiết và lệnh mở](../../docs/production/Actor_Batch_20261113c_vi.md). Inventory Art_Source/Actor_Library_20261107/batch_20261113c.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113c/.
