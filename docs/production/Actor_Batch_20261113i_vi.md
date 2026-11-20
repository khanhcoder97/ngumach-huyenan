# 20261113i — Nền chuyển động có đao và phạm vi action/class

Đợt này bàn giao **15 sheet chọn / 240 pose nguồn** cho Ảnh Đao: đứng nghỉ, đi bộ và nhát chém thường đầu tiên, mỗi động tác có N/NE/E/SE/S. **14 trang được duyệt source/native; trang walk E còn HOLD**, kéo theo hướng W dùng lật. Đây là bàn giao nguồn và phòng authoring, chưa thay toàn bộ renderer gameplay hoặc nghiệm thu toàn class.

## Phạm vi chính xác

| Action | Góc vẽ gốc | Nguồn/clip | Nhịp preview | Kết quả |
|---|---|---|---|---|
| idle | N/NE/E/SE/S | 16 pose/góc | 1,00 s, 62,5 ms/pose | 5 nguồn duyệt |
| walk | N/NE/E/SE/S | 16 pose/góc | 0,80 s, 50 ms/pose | N/NE/SE/S duyệt; E HOLD |
| basic_attack | N/NE/E/SE/S | 16 pose/góc | 0,60 s, 37,5 ms/pose | 5 nguồn duyệt; chỉ combo nhát 1 |

Các khoảng thời gian trên là profile trình bày/authoring hiện có, không xác lập hit window, vận tốc mạng, hồi chiêu hoặc quyền gây sát thương. Ba góc SW/W/NW là lật từ SE/E/NE khi class cho phép; không tính là góc vẽ riêng.

19 PNG gốc đã sinh gồm 15 trang chọn và bốn biến thể bị thay/loại. PNG gốc giữ nguyên byte ở `Sheets`; nội dung prompt thực lưu ở `Prompts` (chỉ chuẩn hóa khoảng trắng cuối dòng khi lưu); `generation_history.json` ghi lý do loại. Không đệm hình trùng thành 16 pose. Kiểm unique hash chỉ là kiểm cấu trúc, không thay review động tác.

## Sửa dáng đi và HOLD

SE v1 lặp chân dẫn ở 0/8, thay bằng v2. NE v1 và bản sửa v2 vẫn giữ cùng chân kéo sau; chọn bản v3 có chân sau bên phải ở 0 và bên trái ở 8, cùng các pha đi qua. Hai lần thử E chưa thể hiện rõ đảo chân gần/xa; giữ E v1 trong review để sửa, không duyệt E hoặc W vào renderer mặc định.

Các hướng N/NE/SE/S đã xem cả sheet nguồn và chuỗi mẫu native để kiểm chân trụ, đường nối 15→0 và tiếp xúc tay–đao. Nguồn basic là một nhát chém thấp rồi hồi thế, không lặp cú chém ở nửa sau. Idle là một chu kỳ thở, giữ đao thấp; góc sau không quay mặt về camera để chớp mắt.

## Tỉ lệ và điểm neo

`calibrate_anh_dao_locomotion.py` chỉ đọc RGBA và ghi metadata. Dùng bề ngang phần đầu ở pose trung tính 0, so với idle cùng hướng, để đặt một chiều cao tham chiếu cố định cho toàn clip. Nhờ đó chân bước vươn dài không kéo cả đầu/thân thu nhỏ theo bounding box. Pose 0 của cả ba action giữ đao thấp, tránh lấy lưỡi đao giơ cao vào vùng đo đầu.

Điểm chân dùng vùng giày màu tối dày, tránh mũi thép/viền mảnh; recipe đã có trong inspector. `body_registration_20261113i.json` ghi hash nguồn, vùng đo và chiều cao trước/sau. Không sửa, nắn, resample PNG hoặc tạo thêm pose bằng tọa độ. Metadata này phục vụ gắn ảnh, không phải collision/root motion của game.

## Phòng kiểm chuyển động

Thêm `ActorLocomotionReview.tscn` và launcher:

```powershell
ClientGodot/Run_Actor_Library.ps1 -LocomotionReview
ClientGodot/Run_Actor_Library.ps1 -LocomotionReview -Test -SkipBuild
```

Chuỗi tám hướng: đứng 1,0 → đi 0,8 → đứng 1,0 → chém nhát 1 0,6 → đứng 1,0, tổng 4,4 s. Có dừng/phát, phát lại, chỉnh tốc độ và bật/tắt mốc chân. E/W ghi WALK HOLD. Review được xem nguồn giữ lại để sửa; renderer mặc định vẫn chặn HOLD.

Studio tiếp tục hỗ trợ xem/chỉnh tay, Fit clip và timeline. Giữ kiểu chibi nguyên khối đã chốt; không bật lại paper-doll.

## Khép thiếu sót trong hàng đợi class

Canon combat yêu cầu combo ba nhát, chạy và tương tác. Baseline 12 action/class trước đây thiếu `run`, `interact`, `basic_attack_02`, `basic_attack_03`. Bổ sung **20 job cho năm class**; mỗi class hiện có **16 action bắt buộc**, catalogue đổi **1008→1028 job**. Xem [quy định action](Actor_Action_Scope_20261113_vi.md).

Ba nhát mỗi class có mô tả riêng theo canon; nhát đầu Thạch Chùy sửa thành bổ ngang, nhát ba mới giáng thẳng. `comboStage` là metadata trình bày; không sửa wire enum hoặc quyền combat. Không dùng một clip để đánh dấu xong ba nhát. Huyền Bút/Linh Cung tách body khỏi projectile.

## Bảo toàn và kiểm chứng

- 46 PNG cũ được chủ dự án chọn giữ nguyên SHA.
- 215 pin source/binding trước đợt I giữ nguyên; thêm 14 pin mới, tổng 229.
- 254 page cũ ngoài ba atlas nền chưa duyệt được thay giữ nguyên toàn bộ payload.
- Ba atlas idle/walk/basic cũ chưa duyệt chuyển lịch sử, PNG/prompt vẫn giữ.
- 269 page qua cấu trúc, gồm ba clip Motion16 kế thừa; 266 PNG runtime khớp nguồn.
- 75 bài Python đạt. Godot .NET build không lỗi/cảnh báo.
- Native library: 17.480; Studio: 82.098 phép kiểm / 335 entry; locomotion: 4.297; phản ứng Ảnh Đao: 3.034.
- 19 video native: 18 clip × 180 frame và một chuỗi × 300 frame, cùng ảnh mẫu thời gian. Giải mã sạch, không có video bị thay còn lẫn trong selection.
- Toàn bộ 15 inventory cập nhật theo catalogue hiện hành; historical report giữ số liệu lịch sử.
- `delivery_audit.json`, `source_native_review.json`, `native_media_audit.json`, `reference_delivery_audit.json` và log nằm trong `Implementation/Reports/Evidence/Actor_Batch_20261113i`.

Video Movie Maker xuất offline 60 bước/giây. Những số này kiểm timeline và pose; **không chứng nhận gameplay đạt 60 FPS**. Chất lượng pose vẫn được ghi duyệt riêng theo SHA nguồn và binding.

## Những phần tiếp tục phải làm

Catalogue có **71/1028 job đủ nguồn cấu trúc**, **43 job đủ hướng đã duyệt source**, **957 job chưa đủ nguồn**; 18 page HOLD được nhận vào catalogue, thêm một bản VFX Kiếm Trận cũ bị loại cấu trúc vẫn giữ trong hồ sơ HOLD.

Ảnh Đao có 12/16 action đủ nguồn cấu trúc, **11/16 action đủ hướng đã duyệt source**. Còn sửa walk E/W và sản xuất run/interact/hai nhát combo tiếp theo, rồi kiểm nối đủ combo/skill/VFX trong gameplay. Đợt J đã bắt đầu bản nháp nhưng chưa được cộng vào approval hoặc coverage đợt này.

Toàn thư viện còn các class, quái, boss, NPC, component/assembly VFX, biến thể ngoại trang và tài nguyên map/UI chưa hoàn thành. Không coi các trạng thái source/native đạt là nghiệm thu actor, AI, collision, combat, map hoặc game hoàn chỉnh.
