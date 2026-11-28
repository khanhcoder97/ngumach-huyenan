# Bàn giao asset Bến Mưa — đợt 20261112b

## Kết quả

- Thêm 13 sheet được chọn / 208 ô nguồn / 13 chuỗi 16 khung. Rễ Nước và Kẻ Rình Bờ có thêm N/NE/E/SE; cùng S đợt trước có 5 góc nguồn và 3 góc lật để xem. Cá Linh có telegraph_01, attack_01, recovery_01, hurt, death hướng S.
- Các ảnh dùng `image_gen` tích hợp; PNG gốc, prompt và tham chiếu được lưu. Bốn bản thử bị loại ghi trong history/Rejections; bản attack/recovery cuối là v2 sau khi kiểm native thấy v1 kéo méo thân.
- 46/46 PNG cũ giữ nguyên SHA256; 59/59 runtime source page khớp byte nguồn hiện được chọn. Không đổi renderer gameplay sang toàn bộ nguồn chưa duyệt.
- Studio có 102 entry/group; source Cá Linh riêng và grouped có cùng timing. Báo 0,45 s/hồi 0,50 s lấy từ visual bible; đánh 0,30 s là giả định review, không thay hit window/server. One-shot giữ khung cuối; các nguồn chỉ S không tự sinh các góc thiếu.
- Sửa scale của Kẻ Rình Bờ: dùng trục dài ba pose đầu để chuẩn hóa overhead quadruped, tránh lớn đột ngột khi quay ngang. Không warp, resample hoặc vẽ lại PNG bằng code.
- Sửa header thư viện quá dài đẩy timeline ra ngoài viewport. Chi tiết HOLD giữ trong Studio.
- Thêm `CarplingCombatReview.tscn`: xem năm action và điểm nối ba pha, ảnh tĩnh có chọn khung, video native offline 120 khung ở time step 60 FPS.

## Kiểm tra trên bản hiện hành

| Kiểm tra | Kết quả |
|---|---|
| .NET 8 build | 0 warning / 0 error |
| Godot import | Thành công |
| Native Studio | 44.154 assertions / 102 entry-group đạt |
| Native library | 11.472 assertions đạt; kiểm 16 pose ở clock 60 bước/s, one-shot và cổng duyệt |
| Python scale + directional coverage | 11 test đạt |
| Catalog/metadata/export check | Khớp dữ liệu sinh lại |
| Batch inventory, cả hai đợt | Qua `--check`; coverage fields có nhãn snapshot catalogue hiện tại |
| Bảo toàn gốc | 46/46 hash, 0 LFS pointer giả ảnh |
| Runtime copy | 59/59 khớp byte nguồn |
| Native capture | Cá Linh combat, Rễ Nước 8 hướng, Kẻ Rình Bờ 8 hướng |

Log và ảnh/video: `Implementation/Reports/Evidence/Actor_Batch_20261112b/`. Video `carpling_combat_review.mp4` được Godot Movie Maker xuất rồi ffmpeg chuyển H.264, không phải benchmark FPS gameplay thực. Không dùng ảnh concept làm bằng chứng engine. PNG nguồn không bị encoder chỉnh sửa.

## Giới hạn nghiệm thu

62 page qua structure; **40/1008 job đủ góc nguồn**, 968 job còn thiếu. 28 page HOLD; 13 source mới vẫn chưa được mở cổng production. Rễ Nước NE còn gần N; quái cần kiểm chuyển góc/giải phẫu phía sau. Chuỗi Cá Linh còn thiếu bốn góc nguồn, đồng nhất dáng idle–combat và timing tích hợp encounter. Có đủ source cells không chứng minh mọi pose đẹp hoặc giải phẫu tốt.

Hai atlas idle cũ sai grid đã rút khỏi active record, giữ nguyên PNG/historical record; còn một full VFX atlas `sk_mk_03_vfx` lỗi hàng. Component cung Kiếm Trận đã duyệt đợt trước vẫn độc lập và không thay đổi. Không nghiệm thu PCK/shipping hoặc tuyên bố game hoàn tất trong đợt này.

Hướng dẫn và ranh giới timing: `docs/production/Actor_Batch_20261112b_vi.md`. Manifest chính xác: `Art_Source/Actor_Library_20261107/batch_20261112b.json`.
