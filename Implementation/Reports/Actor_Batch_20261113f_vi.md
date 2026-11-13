# Bàn giao asset 20261113f

20 sheet chọn/320 khung nguồn: Huyết Nguyệt, Tàn Hỏa, Xích Ảnh ×5 góc ×16 và năm VFX component. Giữ chibi nguyên khối, đao/phục trang trong source, hiệu ứng tách lớp. Ba biến thể sửa nguồn lưu lịch sử: SE bị nối gutter, chiều vệt chém đầu và đuôi than mờ.23 PNG mới lưu, chỉ20 lựa chọn được cộng inventory.

Thêm DARK_BOOT_CORE_FOOT theo palette Ảnh Đao và chiều cao trung tính cố định. Grid directional có khai báo/đường cắt rõ để giữ mũi đao; còn kiểm ô rỗng, mép/đè ô và source trùng. Đuôi VFX expire dùng alpha64 bounds chỉ ở frame12–15, giữ nguyên RGBA; không áp actor hoặc cho phép ô thiếu. Đồng bộ timing raw/grouped Studio:0,64/0,72/0,66s, hai nhịp Xích Ảnh0,10s tách nhau. Chưa bind damage/root-motion/Nhiệt/mark lifetime hoặc full-skill assembly.

62 Python tests; build0 warning/error và import; native Library16.248 assertions, Studio77.212/286 entries.46 baseline PNG nguyên SHA;221 runtime nguồn khớp byte;204 source/binding và159 source pins trước giữ nguyên.20 source pins mới sau visual review;9 MP4/ảnh/dải mẫu/decode/hash. Offline60 bước/s không chứng nhận gameplay60FPS.

Coverage224page structure,67/1008job đủ nguồn,35job đủ nguồn kiểm source;941 còn thiếu,19 HOLD và full VFX Kiếm Trận sai hàng giữ nguyên. Chưa hoàn tất thư viện/class/gameplay.

[Chi tiết và lệnh mở](../../docs/production/Actor_Batch_20261113f_vi.md). Nguồn và prompt thực dùng imagegen tích hợp nằm trong `Art_Source/Actor_Library_20261107/Sheets/` và `Prompts/`; inventory `batch_20261113f.json`; evidence `Implementation/Reports/Evidence/Actor_Batch_20261113f/`.
