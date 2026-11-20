# Đợt tiếp theo: quái Bến Mưa và chuỗi combat Cá Linh

Ngày 12/11/2026, tiếp tục hướng sprite chibi nguyên khối chủ dự án đã chốt. Không dùng lại nhân vật paper-doll. Chuẩn giữ nguyên: 16–20 ảnh nguồn cho từng hành động/hướng; renderer mục tiêu 60 FPS.

## Nguồn mới đã đưa vào Studio

**13 sheet được chọn, 208 ô nguồn = 13 chuỗi × 16 khung**. PNG được tạo bằng `image_gen` tích hợp, lưu nguyên byte vào `Art_Source/Actor_Library_20261107/Sheets/`; prompt thực ở `Prompts/`. Danh mục chính xác, hash và file runtime: `batch_20261112b.json`. Mỗi record ghi ảnh tham chiếu, vai trò tham chiếu và batch.

| Entity / action | Bổ sung | Hiện có để xem | Giới hạn |
|---|---|---|---|
| Rễ Nước / idle | N, NE, E, SE × 16 | Cùng S cũ thành 5 góc nguồn; SW/W/NW lật theo policy | NE còn quá gần N; chưa duyệt production |
| Kẻ Rình Bờ / idle | N, NE, E, SE × 16 | Cùng S cũ thành 5 góc nguồn / 8 hướng xem | Cần kiểm tiếp chuyển góc và giải phẫu phía sau |
| Cá Linh / telegraph_01 | S × 16 | Co người, căng vây, mở miệng tăng dần | Còn thiếu N/NE/E/SE |
| Cá Linh / attack_01 | S × 16, v2 | Khép hàm một lần, vây/đuôi theo đà | Cần chỉnh điểm nối với idle và timing combat thực |
| Cá Linh / recovery_01 | S × 16, v2 | Hàm đóng, vây và đuôi về thế nghỉ | Chỉ S; chưa đủ action toàn hướng |
| Cá Linh / hurt | S × 16 | Một lần co giật, nhắm mắt rồi hồi | Chỉ S |
| Cá Linh / death | S × 16 | Ngã một lần, cuối chuỗi nằm yên | Chỉ S; chưa thay actor gameplay |

Đếm ô và hash khác nhau **không chứng minh mọi pose có chuyển động giải phẫu tốt**. Những hướng lật chỉ tham chiếu ảnh nguồn, không được cộng thành ảnh vẽ mới. Không đổi tên idle thành attack hoặc chép 8 pose cho đủ 16.

## Sửa lỗi phát hiện trong Godot

1. Pha đớp đầu tiên kéo Cá Linh thành thân dài và quá mảnh. Attack và recovery v1 bị loại khỏi binding; v2 giữ đầu, bụng và vây đầy hơn. Bản loại nguyên gốc và prompt vẫn ở `Rejections/` và `generation_history.json`.
2. Góc ngang Kẻ Rình Bờ bị phóng lớn khi chuẩn hóa theo chiều cao màn hình. Năm sheet hướng idle dùng `scaleMode=LONGEST_AXIS`: lấy trung vị trục dài của ba pose đầu, giữ scale cho cả chuỗi. Không resample/warp PNG; hướng lật dùng cùng scale nguồn. Chính sách cũ cho nhân vật khác giữ nguyên.
3. Bảng thư viện từng đẩy thanh timeline khỏi viewport vì ghi toàn bộ năm ghi chú dài. Header nay ghi số nguồn/HOLD ngắn gọn; ghi chú chi tiết vẫn xem tại từng nguồn trong Studio.
4. Hai atlas idle cũ sai số hàng/cột được rút khỏi active records và ghi lịch sử thay bằng sheet hướng riêng. **Không xóa hoặc sửa PNG trong 46 sheet cũ chủ dự án đã chọn.**

Hai bản thử khác bị loại vì quay hướng trong chuỗi hoặc đảo đầu/đuôi. Tổng cộng bốn bản thử của đợt này được lưu riêng; không tính vào 13 sheet được chọn.

## Nhịp animation và phạm vi authority

`ActorLibraryData.Duration(actorId, clip)` có override trình bày riêng cho Cá Linh:

| Pha | Thời lượng review | Nguồn quyết định |
|---|---:|---|
| telegraph_01 | 0,45 s | `Art_Entity_Weather_UI_Visual_Bible_vi.md`, dòng Cá Linh |
| attack_01 | 0,30 s | **Giả định trình bày để thử pose**, chưa là hợp đồng combat |
| recovery_01 | 0,50 s | Visual bible, cùng dòng |
| hurt | 0,30 s | Default preview cũ |
| death | 1,20 s | Default preview cũ |

Studio mở source riêng và nhóm hướng dùng cùng timing. Hurt/death/telegraph/attack/recovery mặc định phát một lần; death giữ khung cuối. 16 pose nguồn không phải giới hạn FPS renderer: mỗi pose được giữ tới mốc thời gian tiếp theo, không tạo pose mới bằng tween.

Đây là thay đổi presentation/review. Không gửi damage, loot, AI state hoặc cập nhật hit window/server. Timing 0,30 s không được lấy làm cơ sở sửa authoritative combat. Các actor khác không nhận override Cá Linh.

## Xem và chỉnh tay

Chạy từ worktree chứa tài liệu này:

```powershell
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:telegraph_01 -Direction S -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:attack_01 -Direction S -Frame 7
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:recovery_01 -Direction S -Play
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_CARPLING:death -Direction S -Frame 15
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_WATERROOT:idle -Direction E -Play -Loop
.\ClientGodot\Run_Art_Studio.ps1 -SkipBuild -Entry actor:MOB_SHORE_STALKER:idle -Direction NE -Play -Loop
```

Studio vẫn chỉnh pivot, tọa độ, lớp, góc, tốc độ, từng key, VFX và marker; undo/redo, lưu và xuất bundle mang PNG nguyên gốc. Cửa sổ Studio cũ cần mở lại để nạp danh sách mới; không ghi đè project người dùng đang chỉnh.

Scene `ClientGodot/CarplingCombatReview.tscn` bổ sung màn xem native sáu ô: năm action và một chuỗi nối báo–đánh–hồi–nghỉ. Chuỗi nghỉ 0,75 s chỉ giúp soi điểm nối, không mô phỏng lịch AI. `--combat-capture <đường dẫn tuyệt đối>` xuất ảnh tĩnh và thoát; ESC đóng cửa sổ.

## Nghiệm thu đợt và việc còn lại

Build .NET, import Godot, source/runtime hash audit, kiểm clock ở 60 bước/giây, one-shot giữ pose cuối và tính nhất quán timing raw/grouped đều phải qua. Ba test scale mới ngăn quái phóng lớn khi quay ngang; tám test coverage tiếp tục ngăn mirror/component bị tính thành action hoàn chỉnh.

Coverage hiện tại: **62 page qua cấu trúc, 40/1008 job đủ góc nguồn, 968 job còn thiếu nguồn; chỉ 3 job toàn bộ đã có nghiệm thu production kế thừa**. 28 page có HOLD; 13 source mới chưa được mở cổng gameplay. Còn atlas full VFX `sk_mk_03_vfx` sai số hàng, độc lập với cung Kiếm Trận component đang dùng. Báo cáo inventory của cả hai batch có nhãn rõ rằng trường coverage phản ánh catalogue hiện tại, không phải snapshot lịch sử ngày tạo batch.

Bằng chứng và log ở `Implementation/Reports/Evidence/Actor_Batch_20261112b/`. Video native xuất `--fixed-fps 60` là review offline, **không phải phép đo FPS gameplay thực**. Ảnh tĩnh không chứng minh mượt chuyển động.

Việc tiếp theo: sửa rõ góc NE Rễ Nước; kiểm liên tục đầu/đuôi Kẻ Rình Bờ ở N/NE; đồng bộ dáng idle–combat Cá Linh rồi vẽ bốn góc còn thiếu cho từng action; bổ sung walk/interact Người Giữ Thuyền; tiếp tục body choreography/VFX các lớp. Chỉ mở cổng gameplay theo từng action/hướng đã kiểm trực tiếp, không duyệt cả thư viện vì đã đủ file.
