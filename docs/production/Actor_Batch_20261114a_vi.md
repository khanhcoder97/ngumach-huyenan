# 20261114a — Chạy, kiếm chéo, đâm kiếm và tương tác Minh Kiếm

Đợt này bàn giao **20 sheet / 320 pose nguồn**. **19 trang được duyệt source/native**, chạy NE còn HOLD và kéo theo NW dùng lật. Đây là nguồn hoạt ảnh và công cụ xem; chưa nghiệm thu toàn class hoặc thay toàn bộ renderer gameplay. Giữ kiểu chibi nguyên khối đã chốt, Studio tiếp tục hỗ trợ chỉnh tay.

| Action | Góc nguồn | Nhịp xem nguồn | Kết quả |
|---|---|---|---|
| run | N, NE, E, SE, S; 16 pose/góc | 0,64 s; 40 ms/pose | N/E/SE/S duyệt; NE HOLD |
| basic_attack_02 | N, NE, E, SE, S; 16 pose/góc | 0,60 s; 37,5 ms/pose | 5 nguồn duyệt; một nhát kiếm chéo |
| basic_attack_03 | N, NE, E, SE, S; 16 pose/góc | 0,60 s; 37,5 ms/pose | 5 nguồn duyệt; một lần đâm–rút |
| interact | N, NE, E, SE, S; 16 pose/góc | 1,60 s; 100 ms/pose | 5 nguồn duyệt; một cử chỉ tay trống |

SW/W/NW là tham chiếu lật SE/E/NE theo chính sách class; không cộng thành góc vẽ riêng. Nhịp trên phục vụ trình bày, không xác lập hit window, vận tốc, hồi chiêu, tương tác thành công hoặc cấp vật phẩm. Mục tiêu renderer 60 FPS khác số pose vẽ nguồn.

## Nội dung, các bản sửa và HOLD

Chạy có hai nửa đổi chân và pha co/vươn. N v1 chưa đổi rõ chân dẫn, thay bằng v2 có chân trái đưa xuống ở contact 8 thay cho chân phải ở contact 0. Các góc N/E/SE/S đã kiểm sheet đầy đủ và mẫu thời gian native; tay phải giữ một thanh kiếm thẳng thấp suốt chu kỳ.

NE v1 vẫn chưa đọc chắc quan hệ chân gần/xa tại 0/8 trong ảnh mẫu native. Thử sửa v2 còn cho hình đế giày phía sau tương tự, nên **cả hai chưa được duyệt**. Giữ v1 làm bản HOLD để sửa; v2 chỉ ở lịch sử, không vào runtime. NW dùng lật NE cũng bị chặn trong chế độ chỉ đọc nguồn đã duyệt. Đếm đủ 16 ô hoặc có hash khác nhau không chứng minh dáng chạy đúng.

Nhát hai là một lần lấy kiếm lên, chém chéo và thu về thấp; nhát ba đẩy kiếm theo một trục rồi rút theo trục đó. Kiếm luôn có chuôi trong tay phải, tay trái trống; góc sau cho phép che khuất đúng chiều sâu khi vũ khí ở phía trước thân. Góc chính diện của đâm kiếm có thu ngắn theo phối cảnh. Tương tác gồm cúi/nghiêng, đưa lòng tay trái và thu về, tay phải giữ kiếm thấp; không vẽ sẵn đồ nhặt vào tay.

Tổng **23 PNG đã sinh**, 20 trang chọn, ba trang không dùng: chạy N v1, kiếm chéo S v1 và chạy NE v2. Kiếm chéo S v1 còn nền trắng mờ/bóng, đã sửa bằng imagegen thành RGBA v2. Một lần công cụ trả ảnh nhưng file mặc định rỗng; khôi phục nguyên byte PNG từ data URL của chính kết quả đó, lưu SHA và `nativePngRecovery` trong hồ sơ nguồn. Không sửa raster bằng script, ghép atlas hoặc đệm bản trùng.

## Tỉ lệ và mốc gắn

`calibrate_minh_kiem_extended.py` chỉ đọc RGBA, dùng phần đầu ở pose trung tính so với nguồn Phản Quang cùng hướng đã duyệt để đặt chiều cao cố định cho toàn clip. Chạy dùng mốc đầu và đường root ảo giữa hai contact, tránh chân đang co trên không kéo cả sprite. Hai nhát đánh/tương tác dùng vùng giày nâu ấm của cả hai chân, loại áo xanh và thép/vàng sáng; chuyển động cúi/nghiêng đã vẽ vẫn giữ.

`body_registration_20261114a.json` ghi hash, landmark và pivot từng frame. Đây là căn ảnh cho authoring, không phải collision/root motion hoặc mặt phẳng vật lý. PNG nguồn và runtime khớp byte. Kiểm vùng giày mới có bài thử riêng cho hai chân, một chân nâng, thép/vàng/áo xanh và trường hợp thiếu vùng giày.

Hai sheet tương tác N/E có bàn tay đưa rộng làm phép chiếu toàn ảnh nhận nhầm thêm cột. Đã xem đủ bố cục 4×4 và khai báo vùng cắt đều; vẫn kiểm ô trống, biên cắt, số frame và pixel trùng. Đây là sửa metadata. Cả 16 pose đã được soi lại trong viewport native để kiểm bàn tay và kiếm không bị cắt.

## Phòng kiểm nối dùng chung

```powershell
ClientGodot/Run_Actor_Library.ps1 -MobilityReview -Actor CLASS_MINH_KIEM
ClientGodot/Run_Actor_Library.ps1 -MobilityReview
ClientGodot/Run_Actor_Library.ps1 -LocomotionReview -Actor CLASS_MINH_KIEM
ClientGodot/Run_Art_Studio.ps1 -Entry class_minh_kiem_basic_attack_03_e -Play
```

Phòng mobility hỗ trợ Minh Kiếm và Ảnh Đao. Chuỗi tám hướng 8,84 giây: đứng → đi → chạy → đứng → ba nhát combo → đứng → tương tác → đứng. Có dừng/phát, phát lại, chỉnh tốc độ, bật mốc chân; nhãn HOLD/chờ duyệt lấy từ dữ liệu thật. Tra nguồn hỗ trợ cả page riêng từng hướng và ba page Motion16 kế thừa. Profile locomotion 4,4 giây vẫn giữ.

Phòng Minh Kiếm ghi rõ ba clip nền cũ không cầm kiếm. Chuỗi đã cho thấy chỗ bật/tắt kiếm khi nối chúng với clip mới; **đây còn là việc phải sửa**, không dùng việc đi hết timeline để nghiệm thu chuyển thế. Nguồn cũ tiếp tục giữ nguyên; cần thêm đứng/đi/nhát thường đầu có kiếm rồi kiểm lại.

## Kiểm chứng bàn giao

- 250 pin cũ và 289 payload page cũ giữ nguyên; thêm 19 pin, tổng 269. Giữ một HOLD mới cho NE/NW.
- 46 PNG cũ chủ dự án chọn giữ nguyên SHA; 309 page qua cấu trúc, 306 PNG runtime khớp nguồn.
- 25 video native chọn: 24 video × 180 frame, một chuỗi × 600 frame; có mẫu thời gian và crop canvas ở tỷ lệ pixel native. Không có video bị thay lẫn trong selection.
- Ledger `source_native_review.json` ghi SHA của PNG, binding và từng file chứng cứ native. Công cụ áp dụng kiểm đủ ledger/hash trước khi ghi pin; không suy ra duyệt từ cấu trúc.
- 86 bài Python đạt; build Godot .NET không lỗi/cảnh báo. Native library 18.120 phép kiểm; Studio 91.530 / 383 entry; mobility Minh Kiếm và Ảnh Đao mỗi profile 9.029 phép kiểm.
- Full inspector/export và 17 inventory được kiểm trước khi đóng gói. Hồ sơ nguồn, bảo toàn, decode và self-test nằm tại `Implementation/Reports/Evidence/Actor_Batch_20261114a`.

Video xuất offline 60 bước/giây kiểm nguồn/timeline, **không chứng nhận gameplay chạy thực tế 60 FPS**. Đây không phải đợt sản xuất thêm VFX component hoặc nghiệm thu sát thương/AI/network.

## Phạm vi còn lại

Minh Kiếm hiện 16/16 action có nguồn cấu trúc, **15/16 action đủ hướng đã duyệt source**; run còn thiếu NE đạt chất lượng. Ba clip nền không cầm kiếm còn cần nguồn thay và kiểm chuyển thế. Sáu skill cần tiếp tục ghép VFX nhiều pha và nối vào gameplay.

Toàn thư viện hiện **79/1028 job đủ nguồn cấu trúc**, **51 job đủ hướng đã duyệt source**, **949 job chưa đủ nguồn**. Còn 18 page HOLD nhận vào catalogue cùng một bản Kiếm Trận cũ bị loại cấu trúc. Các class, quái, boss, NPC, biến thể ngoại trang và tài nguyên môi trường/UI vẫn tiếp tục; mục tiêu hoàn thiện toàn thư viện còn giữ nguyên.
