# 20261114b — Nguồn nền Minh Kiếm có kiếm và kiểm duyệt theo binding hiện hành

Thêm **15 sheet / 240 tư thế nguồn** cho đứng, đi và nhát chém thường đầu của Minh Kiếm. **8 sheet duyệt source/native; 7 sheet HOLD cần sửa**. Giữ kiểu chibi nguyên khối đã chốt, không quay lại paperdoll. Đây là đợt nguồn và phòng kiểm; chưa nghiệm thu class hay gameplay.

| Action | Nhịp xem nguồn | Góc đạt | Góc HOLD |
|---|---|---|---|
| `idle` | 16 × 62,5 ms = 1,00 s, lặp | N, NE, E, SE, S | — |
| `walk` | 16 × 50 ms = 0,80 s, lặp | N, S | NE, E, SE |
| `basic_attack` | 16 × 37,5 ms = 0,60 s, một lần | S | N, NE, E, SE |

SW/W/NW là tham chiếu lật SE/E/NE có ghi nhãn, không cộng thành góc vẽ riêng; trạng thái duyệt đi theo nguồn. Mỗi góc nguồn là 16 tư thế có ảnh thực, không đệm bản trùng hoặc biến dạng raster để tạo thêm khung. Nhịp trình bày không quy định vận tốc di chuyển, hit window hay kết quả server. Mục tiêu renderer 60 FPS vẫn tách với số tư thế vẽ.

## Tạo hình và chuyển động

Giữ tóc đen búi cao khóa vàng, áo trong trắng ngà cổ chéo, áo ngoài xanh trầm viền vàng, giáp vai nhỏ, quần tối và giày nâu. Một thanh kiếm thẳng chuôi vàng nằm trong tay phải giải phẫu; tay trái trống. Nguồn đứng mới thở nhẹ, chớp mắt, cử động ngón tay trống và vạt áo, chân trụ không bước. Kiếm ở bên hông thấp, mũi chéo ra ngoài chân, không đặt thẳng xuyên người.

Dáng đi Bắc/Nam cho thấy hai nửa đổi chân rõ trong sheet gốc và mẫu thời gian native. Ba góc NE/E/SE còn khó đọc chân gần–xa tại hai contact đối nhau; giữ HOLD để vẽ lại, không dùng số hash khác nhau làm bằng chứng dáng đi đúng.

Nhát đầu yêu cầu một lần quét ngang tầm eo, phân biệt với nhát hai chém chéo và nhát ba đâm kiếm. Hướng S đã đọc được cung quét từ bên thân qua trước tới bên đối diện, có thu ngắn phối cảnh và thu kiếm về thấp. Các góc E/SE/NE còn giống động tác đưa mũi kiếm về trước, đường quét ngang/chều dài lưỡi cần làm rõ. Hướng N v2 sửa được phần lấy đà nhưng đoạn qua thân vẫn có dấu hiệu chuyển tay cầm; chưa duyệt cả nguồn. Không gán lại tên thành đâm kiếm để né yêu cầu nhát đầu.

Sinh **17 PNG**, chọn 15, giữ hai bản không dùng trong lịch sử: đi NE v1 nền đục và chém N v1 lỗi tay. Đi NE được sửa nền bằng imagegen thành v2 có alpha, song lỗi đọc chân vẫn HOLD. Chém N v2 vẫn HOLD. Không tẩy nền, ghép atlas hoặc sửa ảnh bằng script. Mọi prompt và hash tham chiếu được giữ trong hồ sơ nguồn.

## Gắn ảnh và giữ nguồn cũ

`calibrate_minh_kiem_extended.py --batch 20261114b --apply` dùng cùng cách đo đầu và hai vùng giày đã kiểm ở đợt a; chỉ ghi metadata. Đi dùng root ảo suy từ đầu và contact 0/8 để chân đang nâng không kéo cả ảnh. Đứng/chém dùng hai vùng giày nâu, loại áo xanh, thép và vàng sáng. Đây là mốc gắn hình cho authoring, không phải collision hoặc root motion. Giữ cúi/nghiêng đã vẽ; tỉ lệ cố định trong mỗi clip.

309 payload page trước và 269 pin source trước giữ nguyên. 46 PNG cũ chủ dự án chọn giữ nguyên SHA. Ba clip Motion16 không cầm kiếm tiếp tục tồn tại nguyên byte; các page mới theo từng hướng được ưu tiên trong phòng kiểm. Không xóa nguồn cũ để thay bằng bản mới.

## Sửa thống kê theo nguồn thực sự được client chọn

`ActorLibraryData.Resolve` ưu tiên page riêng từng hướng và chặn page chưa duyệt trong chế độ production. Phép tính độ phủ trước đây lọc bỏ page chưa duyệt trước khi chọn hướng, có thể quay lại tính page Motion16 cũ là đã duyệt dù client không dùng được nó.

Đã sửa `covers` chọn page có hiệu lực trước rồi mới xét duyệt, khớp thứ tự client. Sáu bài kiểm mới giữ nguyên toàn bộ bài cũ, kiểm page thay thế chưa duyệt che nguồn cũ, độc lập thứ tự, góc còn thiếu, mirror và component OMNI. Vì đi/chém đầu mới chưa đủ hướng đạt, số action đủ hướng đã duyệt giảm **51 → 49**, Minh Kiếm **15 → 13/16**. Đây là đếm đúng binding hiện hành, không thu hồi 269 pin nguồn trước. Không được báo class hoàn chỉnh từ ba page legacy đã bị che.

## Xem và chỉnh tay

```powershell
ClientGodot/Run_Actor_Library.ps1 -MobilityReview -Actor CLASS_MINH_KIEM
ClientGodot/Run_Actor_Library.ps1 -LocomotionReview -Actor CLASS_MINH_KIEM
ClientGodot/Run_Art_Studio.ps1 -Entry class_minh_kiem_walk_e -Play -Loop
ClientGodot/Run_Art_Studio.ps1 -Entry class_minh_kiem_basic_attack_n -Play
```

Phòng nối tự đọc nguồn đang dùng để cảnh báo còn clip nền không cầm kiếm hoặc đang xem nguồn có kiếm mới; không đóng dấu đạt từ việc chạy hết timeline. Studio giữ các công cụ chỉnh tọa độ, pivot, lớp, thời gian, tốc độ và xem từng frame. HOLD vẫn xem được để sửa, không được cấp quyền production.

## Bằng chứng và giới hạn

- Đã xem toàn bộ 15 sheet gốc và 15 mẫu thời gian crop viewport native; xem ba grid tám hướng và chuỗi nối 8,84 giây.
- 19 video native: 18 video × 180 frame và một chuỗi × 600 frame. Công cụ decode kiểm frame thực, lỗi giải mã và SHA; không trộn video lịch sử vào selection.
- Ledger `source_native_review.json` ghi rõ tám nguồn đạt, bảy nguồn HOLD, SHA nguồn/binding và từng file chứng cứ. Công cụ áp dụng kiểm đủ ledger trước khi ghi pin.
- 92 bài Python đạt; build .NET không lỗi/cảnh báo. Native Library 18.360 phép kiểm; Studio 91.800 phép kiểm / 398 entry. Profile base và mobility của Minh Kiếm/Ảnh Đao tiếp tục kiểm source timing và chặn nguồn chưa duyệt.
- Full inspector/export, 18 inventory và audit bảo toàn phải đạt trước khi đóng gói. `audit_actor_batch_20261114b.py` kiểm nguồn, runtime, nguồn tham chiếu, pin cũ, page cũ, ảnh cũ và media đã duyệt.

Video offline 60 bước/giây không đo FPS gameplay thực tế. Chưa nghiệm thu sát thương, di chuyển/collision, AI/network hoặc cả class. Bảy HOLD mới cùng chạy NE từ đợt a phải sửa tiếp; còn ghép VFX nhiều pha cho sáu skill và nối vào gameplay.

Toàn thư viện hiện **324 page cấu trúc**, **321 PNG runtime khớp nguồn**, **277 pin source**, **79/1028 job đủ nguồn cấu trúc**, **49 job đủ hướng đã duyệt source**, **949 job chưa đủ nguồn**. Còn 25 page HOLD nhận vào catalogue và một Kiếm Trận cũ bị loại cấu trúc. Các class, quái, boss, NPC, biến thể, môi trường và UI vẫn còn trong phạm vi hoàn thiện toàn thư viện.
