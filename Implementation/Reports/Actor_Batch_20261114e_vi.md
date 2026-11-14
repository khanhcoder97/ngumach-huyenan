# 20261114e — Mực Triều, Hàn Châm và khôi phục tác vụ

Tiếp tục sprite chibi nguyên khối đã chốt, giữ Studio chỉnh tay. Đợt này tạo **10 sheet thân và 6 component VFX**, mỗi nguồn có 16 tư thế: 256 tư thế được chọn. Có 17 lần sinh/272 tư thế kể cả một bản cánh băng bị thay. Không sửa pixel, ghép atlas hay kéo biến dạng một hình để tăng số khung.

## Thân nhân vật

Nhận diện tham chiếu là Huyền Bút đã chọn: tóc đen tết dài, hoa ngọc sau đầu, áo trắng/xanh băng, vai xanh, thắt lưng nâu, giày tối; một bút lông gỗ tối có đai vàng trong tay phải giải phẫu, tay trái trống. Không bake đạn hoặc băng vào thân.

| Action | Nội dung | Đồng hồ nguồn | Kết quả nguồn |
|---|---|---|---|
| `skill_01` — Mực Triều | Chuẩn bị → quét bút ngang → thu tay | 10 × 40 ms + 6 × 53⅓ ms = 0,72 s | N/E/SE/S duyệt; NE HOLD |
| `skill_02` — Hàn Châm | Nâng cổ tay → ba nhịp chấm → phát bút gọn → hồi phục | 6 × 30 ms + 4 × 35 ms + 6 × 53⅓ ms = 0,64 s | N/E/SE/S duyệt; NE HOLD |

N/NE/E/SE/S là năm nguồn riêng; SW/W/NW chỉ là tham chiếu lật có ghi nhãn theo policy hiện hành. Sau so sánh native tám góc, hai nguồn NE có đầu/vai/thân quá gần hình nhìn thẳng từ sau. Khác nét đưa tay chưa đủ làm hướng Đông Bắc rõ ràng. Giữ HOLD cả hai và các hướng NW phụ thuộc, cần vẽ lại góc thân/đầu sau ba phần tư; không tự xoay raster hoặc duyệt bằng hash.

Tám nguồn thân còn lại đã kiểm riêng 16 pha, tay cầm bút, đường quét/chấm, giày neo đất, tóc/viền áo và khoảng trống quanh nguồn. Duyệt từng clip không chứng nhận tỉ lệ đầu/thân khi nối các action, chuyển idle/đi/chạy hoặc độ rõ tại camera gameplay rộng. Những phần này còn phải kiểm trong cảnh thật.

## Thành phần hiệu ứng

| ID | Hình và điểm neo | Thời lượng xem nguồn | Giới hạn |
|---|---|---|---|
| `sk_hb_01_stroke_component` | Nét mực tím chàm, rìa xanh, phát từ đầu trái rồi rã mảnh | 0,32 s | Điểm gắn đầu bút cần chỉnh trong assembly |
| `sk_hb_01_wave_component` | Sóng mực phẳng, lưỡi cong xanh ở đầu phải, đuôi mực rời | 0,32 s | Cửa sổ bay ví dụ 0,25 s tách riêng; không quyết định va chạm |
| `sk_hb_02_cast_dots_component` | Lần lượt hiện ba chấm xanh thành tam giác nhỏ rồi tan | 0,32 s | Tell thiết kế vẫn 0,18 s |
| `sk_hb_02_needle_component` | Kim băng mảnh hướng phải, tan thành mảnh lạnh | 0,40 s | Thời lượng review không định nghĩa vận tốc đạn |
| `sk_hb_02_frost_gain_component` | Sáu cánh băng rời, tâm rỗng; chọn v2 | 0,32 s | Chỉ gain, chưa có loop duy trì dấu chậm/đóng băng |
| `sk_hb_02_frost_expire_component` | Sáu cánh nứt, rã thành mảnh và mất dần | 0,32 s | Cần kiểm nối gain/sustain/expire và gắn chân mục tiêu |

Cả sáu component đạt kiểm nguồn/native riêng. Tái sử dụng `sk_hb_01_ink_hit_component` đã duyệt từ đợt trước, không tính là nguồn mới. Các sheet timeline cũ không tự trở thành VFX hoàn chỉnh sau khi thêm component.

V1 của frost gain trông như mảng liền nên được giữ trong lịch sử, không copy vào runtime. V2 có sáu cánh tách biệt và tâm rỗng trong Godot. RGB xanh ở alpha rất thấp trong PNG nguồn không tạo mảng nền đục ở render native; giữ nguyên byte PNG, không dùng script xóa màu/alpha.

Thời lượng xem nguồn 0,32 s cho phép kiểm đủ 16 tư thế ở 60 bước/giây. Khi ghép vào tell 0,18 s hoặc bay 0,25 s, cần retime theo cửa sổ thật và có thể bỏ qua tư thế tại một số lần render; không kéo dài tell/bay để ép hiển thị đủ 16 lần. Kết quả trúng/kháng, xuyên quái, chậm hoặc đóng băng phải đến từ combat đã xác nhận. Đợt này không triển khai những cơ chế đó.

## Đăng ký và bằng chứng native

Neo chân từng frame đọc từ vùng giày tối, tránh lấy đầu bút làm gốc; chiều cao tham chiếu lấy tư thế đứng trung tính. Một số nguồn có khoảng cách ô không đều: metadata ghi biên ô đã xem trực tiếp, vẫn kiểm crop, ô rỗng và hash từng nguồn. PNG gốc/runtime luôn khớp byte. Không dùng thay đổi metadata để chấp nhận một hướng vẽ sai.

Studio thêm cờ `--studio-trace-source` chỉ hoạt động lúc xuất movie offline. Log ghi số khung native và tư thế nguồn thực đang hiển thị. Script capture lấy mẫu nằm bên trong khoảng hiển thị đo được của từng tư thế; audit kiểm lại đủ 0–15, không chỉ suy đoán thời điểm từ thời lượng clip. Có 16 video nguồn và hai video so tám hướng, mỗi video 180 khung, decode sạch. Hai video lấy mẫu thử đầu tiên giữ riêng trong `Superseded_Source_Sampling`, không dùng làm bằng chứng lựa chọn cuối. Video 60 bước/giây không đo FPS gameplay.

`source_native_review.json` ghi cụ thể 14 nguồn duyệt và hai NE HOLD, kèm SHA ảnh/binding/bằng chứng. Trạng thái trong ảnh capture là lúc ứng viên chưa duyệt; ledger sau kiểm quyết định trạng thái hiện hành. Chế độ xem review vẫn được mở nguồn HOLD; renderer mặc định phải chặn nguồn chưa duyệt và bản lật phụ thuộc.

## Lỗi và phục hồi

Phát hiện `record_generated_candidate.py` từng chứa 3.982 byte rỗng, khiến Python báo lỗi byte null. Đã giữ bản hỏng ngoài repo, khôi phục riêng script thuộc tác vụ, compile lại và kiểm replay. Chưa biết nguyên nhân file bị hỏng; không có bằng chứng xác định đây là nguyên nhân phiên trò chuyện bị ngắt.

Đã đối chiếu lại đủ 16 cặp PNG nguồn/runtime, tất cả khớp SHA. Cơ chế lưu ghi prompt và PNG gốc ngay từng job, ghi manifest qua file tạm và đọc kiểm trước khi thay; chạy lại cùng job không thêm bản trùng hoặc xóa calibration, cùng version có byte khác bị từ chối, version mới giữ nguồn cũ trong lịch sử. Các kiểm này hỗ trợ phục hồi dữ liệu, không chứng minh đã loại trừ mọi nguyên nhân ngắt phiên hoặc lỗi ổ đĩa.

## Phạm vi bàn giao

301 pin source hiện hành, gồm 14 pin mới; bảo toàn 287 pin và 329 payload page trước đợt. Có 345 page cấu trúc, 342 PNG runtime; 46 PNG cũ đã chốt không đổi. Coverage **81/1028 job đủ cấu trúc, 50 job đủ hướng đã duyệt, 947 job thiếu nguồn**. Hai job Huyền Bút mới đủ binding nhưng chưa đủ hướng duyệt vì NE HOLD; toàn catalogue còn 22 nguồn HOLD.

Build .NET không lỗi/cảnh báo, 98 kiểm Python đã đạt. Native Library 18.696 assertion; Studio 94.477 assertion/421 mục; bàn ghép 13.311 assertion đạt. Inspector/export và 21 inventory hiện hành đạt. Kiểm staging xác nhận 111 đường dẫn media/93 đối tượng LFS khớp byte; không sửa media để vượt cổng kiểm. Đây là bàn giao nguồn và công cụ, chưa nghiệm thu toàn skill, class hoặc game.

Cần tiếp tục sửa NE, bổ sung bốn skill Huyền Bút còn lại, các action nền/combo/phản ứng, dấu trạng thái duy trì, ghép VFX theo đầu bút từng hướng và sự kiện gameplay. Minh Kiếm còn ba hướng vận động HOLD; thư viện quái, boss, NPC, biến thể, môi trường và UI vẫn chưa hoàn thành.
