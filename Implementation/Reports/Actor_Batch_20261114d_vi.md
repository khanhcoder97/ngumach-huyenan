# 20261114d — Hiệu ứng trạng thái và bàn chỉnh ghép kỹ năng

Tiếp tục kiểu **sprite chibi nguyên khối đã chốt**, giữ Studio chỉnh tay. Đợt này bổ sung năm thành phần VFX, mỗi nguồn có **16 tư thế vẽ**, và một bàn chỉnh Godot ghép thân–VFX để xem đồng thời tám hướng. Không tái mở hướng paperdoll.

## Nguồn bổ sung

| ID | Chức năng | Đồng hồ nguồn | Kiểu phát |
|---|---|---|---|
| `sk_mk_01_guard_ready_component` | Hai nét bạc báo thế thủ Phản Quang; chưa phải đỡ thành công | 16 × 25 ms = 0,40 s | Lặp trong cửa sổ thế thủ |
| `sk_mk_02_aim_component` | Hình thoi rỗng báo hướng Tầm Long, đầu trước cố định | 16 × 20 ms = 0,32 s | Một lượt, có thể retime trong preview |
| `sk_mk_04_sustain_component` | Viền thép xanh rỗng và ánh lướt khi duy trì Thiết Y | 16 × 50 ms = 0,80 s | Lặp độc lập với thời gian khiên |
| `sk_ad_01_bleed_status_component` | Ba vạch đỏ sẫm cạnh thanh HP mục tiêu | 16 × 50 ms = 0,80 s | Lặp; số vạch không phải số stack damage |
| `sk_ad_04_expire_component` | Ba nét chậm tan thành tàn nhỏ, không nổ | 16 × 25 ms = 0,40 s | Một lượt rồi xóa phần còn lại |

PNG gốc và bản runtime khớp byte; prompt, ảnh tham chiếu cùng SHA được lưu. Hiệu chỉnh chỉ thay metadata chọn ô/pivot, không vẽ lại raster bằng script. Hai sheet có các mảng alpha rời dùng lưới đều đã xem trực tiếp, vẫn kiểm đủ 16 ô không rỗng/không cắt biên. Aim dùng pivot từng ô tại mũi trước; các nguồn còn lại căn giữa bounds đối xứng. Ledger nguồn và ledger ghép kỹ năng là hai phạm vi riêng.

## Bàn chỉnh kỹ năng

Nhấp đôi `ClientGodot/Xem_Ghep_Ky_Nang.cmd` để mở, hoặc dùng các lệnh dưới. Launcher dùng Godot/.NET portable cùng vị trí với các tool cũ; máy khác có thể truyền `-GodotPath` và `-DotnetPath` cho script PowerShell.

```powershell
ClientGodot/Run_Skill_Assembly.ps1
ClientGodot/Run_Skill_Assembly.ps1 -Profile SK_MK_04 -Variant shield_break
ClientGodot/Run_Skill_Assembly.ps1 -Profile SK_AD_06 -LowFx -Resource 3
ClientGodot/Run_Skill_Assembly.ps1 -SelfTest
```

Chọn kỹ năng/tình huống; dừng, phát lại, tua và đổi tốc độ. Tám ô xem có cùng tỉ lệ thân trong suốt mỗi tình huống. N/NE/E/SE/S dùng nguồn vẽ; SW/W/NW ghi rõ thân lật theo policy, VFX xoay riêng theo hướng. Không tự coi ba hướng lật là ba nguồn mới.

Bảng bên phải cho chỉnh từng lớp: thời điểm bắt đầu, thời gian hiện, tiến/lùi theo hướng, lệch bên, X/Y màn hình, kích thước, góc xoay, Z, bán kính dàn cánh, điểm gắn caster/target/target-HP/end và chế độ lặp. Có zoom, bật/tắt mốc, LowFX và 0–5 tầng cánh than mẫu. Xuất bản chỉnh JSON vào thư mục `user://skill_assembly`, rồi có thể mở lại. Bản chỉnh luôn chưa duyệt, không ghi đè PNG gốc hoặc catalogue đã chốt.

`DepthByFacing` trong JSON đặt VFX phía trước thân xuống lớp sau khi nhìn N/NE/NW, để thân che phần hiệu ứng ở xa. Có thể tắt trong JSON hoặc chỉnh Z thủ công. Đây là quy tắc trình bày ban đầu; chưa phải giải pháp mask từng bộ phận cho mọi vũ khí.

## Hai mươi tình huống

| Kỹ năng | Tình huống và điều kiện trình bày |
|---|---|
| Phản Quang | Hết thế thủ: chỉ báo thế thủ, không phản kích. Giả lập đỡ được: thế thủ → chớp đỡ → clip chém thường và cung phản kích riêng |
| Tầm Long | Đường lướt mẫu đủ hoặc ngắn: báo hướng → vệt lướt → bụi tại điểm dừng; không tạo damage hoặc quyết định va chạm |
| Kiếm Trận | Ba cung riêng tại 0 / 0,12 / 0,26 s; LowFX vẫn giữ cả ba nhịp |
| Thiết Y | Hết hạn: gain → sustain → expire. Bị phá: gain → sustain → break; không phát cả break lẫn expire |
| Bạch Hồng | Lướt đủ hoặc ngắn; vệt chỉ 0,16 s, không thêm impact |
| Vạn Tượng Quy Nhất | Tụ lực → phát kiếm lớn → tan, ba giai đoạn nhìn rõ |
| Huyết Nguyệt | Trúng mẫu có dấu chảy máu cạnh HP mục tiêu; hụt mẫu chỉ có cung chém |
| Tàn Hỏa | Hết hạn hoặc bị gỡ dùng expire; chỉ tình huống kích dấu mới dùng pop |
| Xích Ảnh | Hai cung thuận/ngược tách thời điểm, có dịch thân minh họa |
| Tước Mạch | Dấu chậm duy trì 2,5 s rồi tan; tình huống boss mẫu không gắn dấu chậm |
| Ảnh Bộ | Khói lướt không sinh impact, không làm nhân vật biến mất |
| Tử Diệm | Tụ lực → quét thấp; 0–5 cánh than mẫu. LowFX bỏ cánh phụ nhưng giữ lượt quét chính |

Các sự kiện trên là **ví dụ authoring để so art**. JSON ghi `PRESENTATION_ASSEMBLY_REVIEW_ONLY`, `ProductionApproved=false`; không nối vào server, không cấp resource, không xác nhận hit, miễn nhiễm, damage, cooldown hoặc thời gian bất tử. Cự ly là pixel preview ở thân chuẩn 140 px, không phải mét/WU/collider. Tích hợp gameplay phải nhận sự kiện thực đã xác nhận, không biến các timer ví dụ thành logic chiến đấu.

## Quy tắc đồng hồ và chuyển trạng thái

Thân và từng lớp VFX có đồng hồ riêng. Thân chạy đủ clip nguồn rồi trở về idle; chỉ tình huống phản kích mới chuyển sang clip chém thường ở mốc đã ghi. Loop lấy modulo thời lượng nguồn, không kéo 0,8 s thành cả năm giây chỉ vì debuff kéo dài năm giây. One-shot có thể retime toàn bộ nguồn vào cửa sổ xem; preview chậm/Studio vẫn cho kiểm từng tư thế nguồn.

Kết thúc cửa sổ phải ẩn lớp, không giữ fragment cuối. Vệt Bạch Hồng chỉ hiện 0,16 s dù nguồn có 16 tư thế; tại render 60 Hz, cửa sổ ngắn này sẽ bỏ qua một số tư thế nguồn. Không kéo dài cửa sổ chỉ để ép hiển thị đủ 16 lần cập nhật hoặc nhân bản khung cho đủ số. Video review offline ghi 60 bước/giây **không chứng minh gameplay đạt 60 FPS**.

## Kiểm hình và lỗi đã sửa

Đã sửa bảng chọn track dài làm tràn bảng chỉnh; chờ container hoàn tất bố cục trước khi fit tám ô, giữ cùng chiều cao thân giữa các góc. Dấu thế thủ chuyển lên vùng tay kiếm. Qua lượt xem đầu phát hiện cung chém bị gắn gần chân; đã nâng điểm gắn và ghi lại các tình huống chịu ảnh hưởng. Năm cánh than từng chồng thành một cụm khó đọc: giảm kích thước mỗi cánh từ 46 xuống 26 px authoring, tăng bán kính từ 18 lên 34 px và thêm điều chỉnh bán kính. Đây là bố trí các instance của cùng nguồn, không tính thêm tư thế vẽ. Giữ năm video cũ trong `Superseded_*` để truy vết; không dùng chúng làm bằng chứng lựa chọn cuối.

Nguồn, crop native, mẫu thời gian và các ảnh theo từng pha nằm trong `Implementation/Reports/Evidence/Actor_Batch_20261114d`. Có 27 video lựa chọn: năm nguồn Studio, hai mươi tình huống và hai bản so LowFX. Năm clip nguồn có thể được duyệt độc lập; các timeline ghép vẫn là bản chỉnh thử, cần kiểm tiếp với camera, mục tiêu thật và hệ chiến đấu.

Ledger ghi rõ các điểm chưa nghiệm thu: dấu báo hướng/tụ lực và viền khiên mảnh còn khó thấy ở mức fit tám ô; đầu kiếm và hiệu ứng cần cân theo từng hướng ở camera gameplay thật. Target hiện là mốc vòng/HP, chưa phải enemy đang chạy. Không dùng việc video decode sạch để kết luận những điểm này đã đạt.

Các kiểm tự động gồm nguồn/pivot/nhịp, cửa sổ nửa mở, xóa VFX khi hết, hướng che khuất, cùng tỉ lệ thân, điều kiện không phản kích khi timeout/không nổ khi expire, LowFX không mất nhịp chính, khoảng cách năm cánh than và xuất/đọc JSON. `build_skill_assembly_profiles.py --check` khóa hai bản dữ liệu source/runtime cùng nội dung. Snapshot 102 nguồn ghi 120 binding thân theo hướng và 27 component dùng trong các tình huống. Kiểm cấu trúc và hash không thay việc xem hình.

Kết quả đóng gói: build .NET không lỗi/cảnh báo; 92 bài Python đạt; inspector/export và 20 inventory hiện hành đạt. Native Library 18.440 assertion; Studio 91.945 assertion/403 entry; bàn ghép 13.311 assertion đạt. 27 video lựa chọn decode sạch. Sau ghi ledger có 287 pin source, bảo toàn 282 pin cũ, 324 payload page trước, 46 PNG chủ dự án đã chốt; 326 PNG runtime hiện hành khớp nguồn. Các con số này là kiểm thư viện và công cụ, không phải chứng nhận gameplay.

## Phạm vi còn lại

Đợt này bổ sung component, không lấp các job toàn actor bằng cách gắn nhãn hoàn chỉnh cho một hiệu ứng. Coverage vẫn **79/1028 job đủ cấu trúc, 50 job đủ hướng đã duyệt source, 949 job thiếu nguồn**. Minh Kiếm còn chạy NE, đi NE/SE HOLD; tiếp tục sửa theo contact pose đã kiểm. Những class còn lại, quái, boss, NPC, biến thể, môi trường và UI chưa hoàn tất. Cần đưa assembly đạt chất lượng vào gameplay qua sự kiện thật và đo hiệu năng trực tiếp.
