# Bàn giao asset 20261112e

Thêm **16 sheet được chọn / 256 ô nguồn**: báo đòn, roi rễ và hồi thế của Rễ Nước ở N/NE/E/SE/S, mỗi góc 16 khung; thêm vòng gợn OMNI 16 khung. SW/W/NW dùng mirror theo policy cũ. Ảnh do `image_gen` tích hợp tạo, giữ PNG nguyên byte và prompt/tham chiếu. Không tạo frame bằng code hoặc lặp pose.

Năm idle cũ được kiểm lại sau khi đổi điểm neo. Lõi rêu xác định thân; chiều cao lấy từ pose trung tính và giữ suốt clip. Dùng chung offset chân idle theo từng hướng để giảm lệch giữa pha. Chênh điểm đăng ký metadata trước sửa tới 18,53px theo X ở NE, nay cùng chuẩn; đây không phải bằng chứng bàn chân/giải phẫu khớp tuyệt đối. Một đường cắt ô N được chuyển vào dải nền trống thật để giữ nguyên ngọn roi mảnh.

VFX vòng rỗng đã xem native, 16 mẫu tâm alpha 0. Chỉ ghép trong cảnh review: xuất hiện trong 0,70s báo đòn, tắt khi đánh/hồi/idle. Vòng báo lấy đà, không phải hitbox hoặc bán kính sát thương. 0,35s đánh / 0,55s hồi là timing review. Không đổi damage/server/AI.

| Kiểm tra | Kết quả |
|---|---|
| .NET 8 / Godot import | Thành công, build 0 warning / 0 error |
| Python regressions | 26 test: coverage, scale, source pin, core registration và không cắt ngọn roi |
| Native library | 12.495 assertions: source/texture/gate, tám hướng, đi qua 16 pose ở clock 60 bước/s |
| Native Studio | 55.963 assertions / 153 entries; raw/group timing và one-shot |
| Cue boundary review | 6 assertions đạt, có kiểm chu kỳ quay lại |
| VFX component cũ | 14 assertions đạt |
| Bảo toàn PNG | 46/46 baseline không đổi, 105/105 runtime source khớp byte |
| Media | 10 MP4 native, bốn ảnh tám hướng và dải mẫu thời gian; không đo FPS gameplay |

21 source quyết định được pin cả PNG và binding: 15 combat mới, 5 idle kiểm lại và một component. Năm pin đăng ký idle trước được giữ trong lịch sử. Các quyết định có phạm vi source/clip, không nghiệm thu toàn actor/encounter hoặc bản đóng gói.

Catalogue: **108 structure page; 50/1008 job đủ góc nguồn; 14 job đủ góc được kiểm source**. Còn 958 job thiếu, 21 active HOLD, một full VFX atlas cũ sai hàng; các bộ map/UI/icon/audio còn ngoài tổng này. Rễ Nước hiện có 4/12 action đủ nguồn, không được trình bày thành actor hoàn chỉnh.

Tool thư viện thêm `-CombatReview -Actor MOB_WATERROOT -Direction NE`; Studio giữ toàn bộ chỉnh tay. Các ô hurt/death thiếu vẫn hiện rõ, không thay bằng idle. Chi tiết: `docs/production/Actor_Batch_20261112e_vi.md`. Inventory: `Art_Source/Actor_Library_20261107/batch_20261112e.json`. Bằng chứng: `Implementation/Reports/Evidence/Actor_Batch_20261112e/`.
