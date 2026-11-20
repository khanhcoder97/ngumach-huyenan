Thư viện sprite chibi nguyên khối còn thiếu nhiều action và VFX. PR bổ sung combat Cá Linh đủ hướng, idle/interact Người Giữ Thuyền, chín action của Rễ Nước và động tác Phản Quang của Minh Kiếm. Mỗi hướng nguồn có 16 khung; hướng lật được khai báo riêng. Walk NPC E/NE còn HOLD.

Đợt mới nhất 20261113a có 20 sheet chọn / 320 ô nguồn: 15 sheet walk/run/turn Rễ Nước và 5 sheet skill_01 Minh Kiếm. Quái bò bằng bó rễ ngắn; turn là chuyển trọng tâm, không xoay sang block khác hoặc cấp quyền dịch chuyển AI. Phản Quang giữ nét nhân vật Motion16 đã chốt, kiếm chéo trước ngực, che khuất đúng ở góc sau. Toàn clip preview 0,80s không thay cửa đỡ combat 0,40s; cung sáng thành công là component riêng.

Studio thêm chèn component 16 khung vào layer/track và launcher -Component, giữ texture/regions/pivot/order. Host dưới 16 ô bị từ chối. Bản chèn trải đều theo timeline host để chỉnh tay, chưa tự bảo toàn nhịp riêng hoặc gắn sự kiện gameplay. Selector dài không ép panel tràn ngang; layer mới được cuộn tới; ghi chú đầy đủ ở tooltip/tab Xuất. PNG nguồn, undo/redo, socket/timing và JSON/bundle giữ nguyên.

Validation: .NET 8 build 0 warning/error; Godot import; 34 Python tests; native library 13.215 assertions; Studio 63.370 assertions / 194 entries. Baseline 46 PNG nguyên SHA256; 140 nguồn runtime chọn khớp byte. Đợt mới có 6 video native cùng ảnh/dải mẫu, source/binding pins và decode/hash audit. Video 60 bước/s offline không chứng nhận gameplay 60 FPS.

Catalogue: 143 page structure, 56/1008 job đủ nguồn, 20 job đủ nguồn kiểm source; còn 952 job thiếu, 21 HOLD và atlas full VFX cũ sai hàng. Component không tính thành full skill. Chưa nghiệm thu toàn actor/skill, gameplay renderer/AI/hit/collision/LowFX/PCK. Map/UI/icon/audio và các nguồn thiếu khác tiếp tục.

Chi tiết: docs/production/Actor_Batch_20261113a_vi.md; inventory Art_Source/Actor_Library_20261107/batch_20261113a.json; evidence Implementation/Reports/Evidence/Actor_Batch_20261113a/. Các đợt trước và lịch sử kiểm riêng được giữ.
