# Phạm vi động tác bắt buộc của năm lớp nhân vật

## Sửa thiếu sót trong hàng đợi sản xuất

Đặc tả combat hiện hành đã yêu cầu chạy, tương tác và ba nhát đánh thường riêng tại `Combat_Skills_VFX_Animation_Spec_vi.md`, mục “Thiết kế combo đánh thường” và “Hướng dẫn asset”. Hàng đợi trước đây mới có 12 action/class, gộp đánh thường vào một clip và bỏ chạy/tương tác. Không dùng mức 12/12 cũ để nghiệm thu đầy đủ một lớp nhân vật.

Từ đợt 20261113i, mỗi class có **16 action bắt buộc**. Thêm bốn action/class × năm class = **20 job**; catalogue toàn thư viện đổi từ **1008 sang 1028 job**. Đây là tăng phạm vi cần sản xuất, không phải đã tạo thêm 20 bộ ảnh. Các báo cáo lịch sử giữ số liệu ở thời điểm bàn giao.

| ID clip | Nội dung cần vẽ | Nối động tác |
|---|---|---|
| `idle` | Một chu kỳ thở/chớp mắt, giữ vũ khí | Về tư thế sẵn sàng |
| `walk` | Một chu kỳ đủ chân trái/phải; contact 0/8, passing 4/12 | Kiểm cả đường nối 15→0 |
| `run` | Chu kỳ chạy riêng, có thay đổi nhịp và tư thế | Không tăng tốc walk để tính là đã vẽ run |
| `basic_attack` | Chỉ nhát thứ nhất | Nối neutral hoặc nhát hai theo server |
| `basic_attack_02` | Chỉ nhát thứ hai | Nối neutral hoặc nhát ba theo server |
| `basic_attack_03` | Chỉ nhát thứ ba | Recovery về neutral |
| `skill_01` … `skill_06` | Sáu body action theo kỹ năng tương ứng | VFX tách và gắn riêng |
| `hurt` | Một lần phản ứng trúng đòn | Không tự gây stun/knockback |
| `death` | Một lần ngã và giữ tư thế cuối | Không lặp thành tự hồi sinh |
| `dodge` | Một động tác né đủ chuẩn bị/thực hiện/hồi phục | Không tự cấp i-frame |
| `interact` | Tương tác vật thể/người, tay/vũ khí không xuyên nhau | Điểm chạm cần kiểm theo đối tượng |

Mỗi action/hướng cần **16–20 pose vẽ thật**; các trang đang sản xuất dùng 16. Nhịp render mục tiêu 60 FPS khác số pose nguồn. Không đệm bản trùng, biến dạng một hình hay lặp hai chu kỳ 8 pose để tính là 16 pose đạt chất lượng.

## Ba nhát combo theo nguồn combat

| Class | Nhát 1 | Nhát 2 | Nhát 3 |
|---|---|---|---|
| Minh Kiếm | Kiếm ngang | Kiếm chéo | Đâm kiếm |
| Ảnh Đao | Chém thấp | Xoay cổ tay | Chém ngược |
| Huyền Bút | Nét bút đầu | Nét bút thứ hai | Nét bút kết thúc |
| Thạch Chùy | Bổ ngang chậm | Nện thấp | Giáng thẳng |
| Linh Cung | Lần kéo/thả tên đầu | Lần kéo/thả tên hai | Lần kéo/thả tên ba |

Clip body Huyền Bút/Linh Cung không bake đạn/tên bay vào nhân vật. Projectile, trail và impact thuộc component riêng. Thạch Chùy nhát đầu phải là bổ ngang theo canon; không nhầm với giáng thẳng của nhát ba.

`comboStage` là metadata trình bày trong hàng đợi và hồ sơ nguồn. Bổ sung clip không mở rộng wire enum trang bị, không cấp tài nguyên, không xác nhận hit và không sửa quy tắc combat. Server quyết định nhát nào được thi triển và kết quả. Các thời lượng preview mặc định 0,6 s cho từng nhát chỉ phục vụ authoring; mốc pose trong prompt không phải hit window.

## Bàn giao và nghiệm thu

Năm góc vẽ gốc N/NE/E/SE/S; ba góc SW/W/NW chỉ dùng lật khi actor cho phép và phải ghi nhãn. Nhân vật bất đối xứng cần góc bổ sung riêng. Giữ nguyên style chibi nguyên khối được chủ dự án chốt; thay đổi metadata tỉ lệ/neo không được sửa pixel PNG đã duyệt.

Điều kiện duyệt một trang: nguồn đầy đủ trong cell; đúng người/đồ/tay cầm/hướng; 16 pose có chuyển động đúng; native Godot kiểm tỉ lệ/neo/timing/đường nối; pin SHA của PNG và binding. Hash khác nhau chỉ chứng minh byte khác, không chứng minh hai nửa dáng đi dùng chân đối nhau.

Phòng `ActorLocomotionReview.tscn` dùng để xem đứng→đi→đứng→chém nhát 1→đứng ở tám hướng, dừng/phát/chỉnh tốc độ và bật mốc chân. Chế độ review được xem HOLD để sửa; renderer mặc định vẫn chặn HOLD và cả hướng lật phụ thuộc nó. Xuất video 60 bước/giây không chứng nhận game chạy ổn định 60 FPS.

Đợt I chưa sản xuất run/interact/basic_attack_02/basic_attack_03 cho Ảnh Đao. Cả bốn vẫn bắt buộc trong `generation_jobs.json`; không gạch xong vì idle/walk/basic đã có bản nguồn mới. Các class khác cũng giữ đủ 16 action bắt buộc. Toàn thư viện và gameplay vẫn đang phát triển.
