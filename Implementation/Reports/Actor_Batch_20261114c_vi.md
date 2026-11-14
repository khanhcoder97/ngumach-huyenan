# 20261114c — Sửa cung chém thường và dáng đi ngang Minh Kiếm

Vẽ lại **8 sheet / 128 tư thế nguồn** đang HOLD, giữ nguyên kiểu chibi nguyên khối đã chốt. Qua xem toàn sheet và mẫu native, **5 nguồn đạt**, **3 nguồn tiếp tục HOLD**. Nhát chém thường đầu hiện đủ năm góc nguồn đạt; chưa nghiệm thu toàn Minh Kiếm hoặc gameplay.

| Nguồn sửa | Kết quả | Bằng chứng hình ảnh |
|---|---|---|
| `basic_attack_n` | Duyệt | Tay phải giữ kiếm; đoạn quét ở phía trước thân được che khuất theo chiều sâu, tay trái vẫn trống |
| `basic_attack_ne/e/se` | Duyệt | Lưỡi kiếm lấy đà quay về sau, đổi góc qua cung tầm eo rồi thu về; phân biệt được với đâm thẳng |
| `walk_e` | Duyệt | Chân gần dẫn ở nửa đầu, lùi về sau khi chân xa dẫn ở nửa đối diện; đọc được chỗ nối hông–cẳng chân |
| `walk_ne`, `walk_se` | HOLD | Chưa đọc chắc đổi chân gần–xa tại hai contact đối nhau |
| `run_ne` | HOLD | Vẫn có cảm giác lặp chân dẫn; đủ 16 ảnh khác pixel chưa chứng minh chu kỳ chạy đúng |

Hướng S của nhát đầu giữ nguồn đã duyệt từ đợt b. SW/W/NW tham chiếu lật SE/E/NE theo policy, không tính là góc vẽ riêng. Các hướng lật kế thừa cả trạng thái HOLD của nguồn. Bộ nhịp không đổi: chém 16 × 37,5 ms = 0,60 s; đi 16 × 50 ms = 0,80 s; chạy 16 × 40 ms = 0,64 s. Renderer mục tiêu 60 FPS; timing trình bày không xác lập hit window hoặc vận tốc gameplay.

## Cách sửa khác với bản trước

Vẽ mới từ nguồn đứng có kiếm đã duyệt để tránh kế thừa đường kiếm sai. Góc N buộc bàn tay trái luôn mở/trống; khi kiếm qua phía trước thân, cho phép thân che tay phải và lưỡi kiếm. Không chuyển kiếm sang tay trái chỉ để vũ khí luôn hiện lên ảnh. Ở E/SE/NE, tư thế lấy đà chỉ rõ lưỡi dài hướng về sau; nhịp giữa đổi góc qua một cung rồi hồi thấp, không trượt chuôi về trước trong khi mũi kiếm giữ nguyên hướng.

Dáng đi E mới thể hiện chân gần ở phía trước/thấp tại contact đầu, rồi ở phía sau/thấp khi chân xa bước trước/cao hơn theo phối cảnh. Hai góc đi chéo và chạy NE vẫn giữ HOLD sau khi xem native. Lần sửa kế tiếp cần **kiểm riêng hai tư thế tiếp đất đối nhau**, nhìn rõ hông, gối và cổ chân của mỗi chân trước khi tạo lại cả chu kỳ. Không tiếp tục duyệt bằng số ô, hash hoặc lặp thêm cùng một prompt toàn sheet.

## Bố cục, pivot và nguyên bản

Tám PNG sinh bằng imagegen tích hợp, không sửa raster bằng script. Một kết quả đi SE được công cụ trả trực tiếp dạng data URL; lưu bằng giải mã base64 nguyên byte, ghi `nativePngRecovery` và SHA `a390f99f292772a7b80caf5c99cce90cf5a9143befba9f7af52149794ef5bd8d`. Không có thao tác tẩy nền hay vẽ lại bằng code.

Sheet chém E gốc 1254 × 1254 có lưỡi kiếm dài chiếm khoảng trống không đều. Cắt theo phép chiếu hoặc lưới đều làm thiếu mũi kiếm. Đã xem nguyên sheet và đo alpha từng ô, dùng `VISUALLY_VERIFIED_DIRECTIONAL_GRID` với cột `[0,314,655,925,1254]`, hàng `[0,314,627,940,1254]`. Cả 16 ô tiếp tục qua kiểm rỗng, cắt biên và trùng ảnh. Ảnh không bị resize/ghép/cắt lại; metadata chỉ chọn đầy đủ vùng nguồn. Đã soi lại toàn đường kiếm trong crop viewport native.

`calibrate_minh_kiem_extended.py --batch 20261114c --apply` giữ cách đo đầu/giày và root ảo từ contact như đợt trước. Ghi `body_registration_20261114c.json`, không cấp approval từ phép đo. Trước khi ghi pin đã khóa SHA nguồn, binding và từng file chứng cứ native trong ledger.

Giữ nguyên **277 pin source trước**, **316 payload page khác**, **8 PNG nguồn/runtime HOLD cũ** và **46 PNG gốc đã chốt**. Chỉ thay binding của tám ID chưa được duyệt. Record cũ chuyển lịch sử, prompt và PNG cũ còn nguyên. Không ghi đè nguồn đã duyệt hoặc xóa bản cũ để giấu lỗi.

## Kiểm trong Studio

```powershell
ClientGodot/Run_Actor_Library.ps1 -Actor CLASS_MINH_KIEM -Clip basic_attack
ClientGodot/Run_Actor_Library.ps1 -MobilityReview -Actor CLASS_MINH_KIEM
ClientGodot/Run_Art_Studio.ps1 -Entry class_minh_kiem_basic_attack_e -Play
ClientGodot/Run_Art_Studio.ps1 -Entry class_minh_kiem_walk_ne -Play -Loop
```

Giữ Studio chỉnh tay, không tái kích hoạt paperdoll. Ảnh chụp/video review ghi trước khi áp dụng ledger nên còn nhãn HOLD; nguồn, pivot và thời gian không đổi sau ghi hình. Chế độ production chỉ dùng pin hiện hành, review vẫn cho xem nguồn bị giữ lại để sửa. Chuỗi nối không chứng nhận chuyển thế/gameplay hoàn chỉnh.

## Kiểm chứng và phạm vi tiếp tục

- 12 video native chọn: 11 × 180 frame và một chuỗi 600 frame; tất cả decode sạch, kèm still/mẫu thời gian/crop native. Đã xem cả tám nguồn, tám crop thời gian, ba grid tám hướng và chuỗi nối.
- 92 bài Python; full inspector/export và 19 inventory phải đạt khi đóng gói. Native Library/Studio và profile base/mobility chạy lại trên nguồn hiện hành sau áp dụng ledger. Code C# không đổi so với build đợt b đã đạt, các nguồn mới được import trước kiểm native.
- `audit_actor_batch_20261114c.py` kiểm các pin cũ, page ngoài phạm vi sửa, tám nguồn HOLD cũ, tham chiếu, prompt, runtime và hash chứng cứ. Cập nhật inventory phản ánh **lựa chọn hiện hành**: đợt a/b có nguồn chuyển lịch sử; báo cáo đợt cũ giữ số giao tại thời điểm đó.

Hiện có **282 pin source**, **50/1028 job đủ hướng đã duyệt source**, **79 job đủ nguồn cấu trúc**, **949 job chưa đủ nguồn**; 324 page cấu trúc, 321 PNG runtime khớp nguồn, 20 HOLD nhận vào catalogue và một Kiếm Trận cũ bị loại cấu trúc. Minh Kiếm **14/16 action đủ hướng đã duyệt**, còn đi/chạy thiếu các góc nêu trên.

Vẫn cần sửa vận động, kiểm chuyển thế và ghép body với VFX nhiều pha cho sáu skill; tiếp tục các class, quái, boss, NPC, biến thể và môi trường/UI. Video offline 60 bước/giây không chứng nhận gameplay 60 FPS. Mục tiêu hoàn thiện toàn thư viện chưa hoàn tất.
