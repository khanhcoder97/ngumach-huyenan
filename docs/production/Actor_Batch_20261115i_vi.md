# Đợt I — năm động tác nền Huyền Bút

Ngày bàn giao: 16/11/2026. ID sản xuất giữ `20261115i` theo lúc bắt đầu sinh nguồn.

Đã bổ sung **25 sheet nguyên khối / 400 tư thế nguồn** cho đứng, đi, nét bút đầu, trúng đòn và ngã, mỗi động tác có năm góc vẽ N/NE/E/SE/S. Duyệt riêng **20 nguồn** của đứng/đánh thường/trúng đòn/ngã. Cả **năm nguồn đi bộ giữ HOLD** và bị chặn ở renderer production; browser review vẫn cho xem để sửa. SW/W/NW là các tham chiếu lật được ghi nhãn, không tính thêm tư thế vẽ.

| Nhóm nguồn | Sheet | Tư thế nguồn | Quyết định kiểm hình |
|---|---:|---:|---|
| `idle` | 5 | 80 | Duyệt source/clip |
| `walk` | 5 | 80 | HOLD, phải sửa hai lượt chân |
| `basic_attack` | 5 | 80 | Duyệt source/clip |
| `hurt` | 5 | 80 | Duyệt source/clip |
| `death` | 5 | 80 | Duyệt source/clip |

## Hình ảnh và chuyển động

Giữ mẫu Huyền Bút nữ chibi đã chốt: tóc đen tết, hoa ngọc nhạt, áo trắng/xanh băng, khăn vai xanh, đai nâu, giày tối và một bút gỗ cán vàng đầu lông kem ở tay phải. Hai mươi nguồn được duyệt đã xem atlas gốc, đủ 16 pha trong Godot và đối chiếu tám hướng. Đứng có thở/chớp mắt; đánh thường là một lần chuẩn bị–phẩy bút–thu tay; trúng đòn có một lần giật người–hồi phục; ngã có một lần khuỵu–quỳ–sụp–nằm yên, không dựng lại giữa clip.

Kiểm kỹ hơn các dáng đi cho thấy đổi pha tay chưa chứng minh chân trái/phải đổi lượt ở contact 0/8. N/S che hoặc giữ cùng dáng chân dẫn; NE/SE chưa rõ sở hữu chân gần/xa; E còn giống chạy/nhảy và bật thân khi nối 15→0. Không dùng hash khác nhau, đủ 16 ô hay cánh tay đổi bên để duyệt chu kỳ đi. Các hướng lật kế thừa HOLD của nguồn gốc. Đợt sửa tiếp phải làm rõ chân dẫn trái/phải, chân trụ, passing 4/12 và nối vòng thật.

## Neo, thời lượng và bảo toàn nguồn

PNG được tạo bằng `image_gen` tích hợp; tệp trong `Sheets` và bản runtime nguyên byte. Prompt chính xác trong `Prompts`. Giữ 46 PNG chủ dự án đã chọn, toàn bộ 365 pin trước và 406 payload page không thuộc thay nguồn. Đợt này thêm 24 ID, thay một ID `death_se` chưa được duyệt; nguồn cũ và generation record cũ lưu lịch sử.

Ba atlas walk N/death NE/death SE cần lấy ranh ô theo dải alpha trống thật. Metadata neo chân giữ theo nguồn; corpse dùng footprint thân lạnh và chiều cao trung tính ban đầu, tránh phóng to tư thế nằm. Bộ lọc footprint đã kiểm trường hợp bút vàng và viền bút tối thấp hơn thân: chúng không được kéo lệch neo ngang/dọc. Đây là đăng ký để xem nguồn, chưa phải nghiệm thu vị trí corpse/collider trong gameplay.

Chu kỳ xem: idle 1,60 giây, walk 0,96 giây; đánh thường 0,64 giây, trúng đòn 0,48 giây, ngã 1,20 giây. Mỗi clip có 16 thời lượng nguồn; không sửa số combat, hit window hoặc quyền di chuyển của server. Xuất video ở 60 bước/giây không chứng nhận FPS gameplay thực.

## Bằng chứng

`Implementation/Reports/Evidence/Actor_Batch_20261115i` chứa 25 project Studio di động với texture gốc, 25 video nguồn riêng và năm video bảng tám hướng. Mỗi video giải mã sạch 180 frame. Trace xác nhận 400 pha nguồn; mười dải nối vòng 14/15/0/1 lấy từ vòng lặp thực. Receipt pin SHA texture/project/video tránh tái dùng nhầm clip khi Resume. Project JSON chuẩn hóa LF để kiểm ổn định khi Git đổi newline; hash PNG/video giữ nguyên byte.

Lần kiểm metadata đầu phát hiện tool thêm page mới phía sau ba clip legacy, khác thứ tự xuất chuẩn của inspector. Đã sửa tool và chỉ sắp lại danh sách metadata; không sửa PNG, nội dung page hoặc binding. Nhật ký trước sửa vẫn giữ để truy vết. Script capture kiểm cả `ERROR:` trong log, kể cả trường hợp Godot trả exit code 0.

Quyết định kiểm hình từng nguồn nằm ở `source_native_review.json`; so sánh hướng ở `eight_facing_manual_review.json`; bảo toàn nguồn ở `delivery_audit.json`. Các video được ghi trước áp ledger nên con số HOLD trong header là trạng thái khi ghi, không phải số liệu cuối.

Kiểm cuối: build 0 lỗi/0 cảnh báo; 111 bài kiểm Python đạt. Metadata inspector `--export --check` đạt sau sửa thứ tự. Godot Library 20.072 kiểm tra; Studio 106.013 kiểm tra/516 entry; Skill Assembly 13.311 kiểm tra/12 profile/20 tình huống/tám hướng. Cả 25 inventory hiện hành đã dựng lại và đối chiếu. Kiểm assembly hiện có thuộc các profile đã tồn tại, không thay nghiệm thu assembly Huyền Bút. Một nguồn VFX Kiếm Trận cũ vẫn bị loại vì sai hàng; không xóa khỏi báo cáo để làm đẹp coverage.

## Phần còn lại

Hiện có **385 pin source**, 431 page cấu trúc gồm ba clip legacy, 428 PNG runtime đang chọn. Catalogue lõi có **90/1028 job đủ nguồn cấu trúc, 65 job đủ góc được duyệt, 938 job thiếu nguồn và 25 page HOLD**. Huyền Bút đạt **15/16 action đủ góc duyệt source**, còn đi bộ. Nguồn đủ không thay thế nghiệm thu toàn class.

Cần sửa năm hướng walk, kiểm nối động tác/độ lớn thân giữa các action, ghép VFX Huyền Bút theo sự kiện thật, kiểm camera rộng và khả năng đọc kỹ năng, neo tay/đầu bút, đường đi/collision và đo FPS thực. Phần lớn Thạch Chùy/Linh Cung, quái, boss, NPC, biến thể trang bị, map/UI và các thành phần VFX vẫn chưa hoàn thành. Hàng đợi 1028 job không bao gồm toàn bộ phạm vi hình ảnh của game.
