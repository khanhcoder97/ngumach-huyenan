> Hết hiệu lực làm hướng mỹ thuật: chủ dự án bác bỏ mẫu procedural. Chỉ lưu tài liệu kỹ thuật. Hướng hiện hành: Restored_Pixel_Style_20261110_vi.md.

# Master nhân vật dùng chung cơ thể/trang phục — 10/11/2026

Trạng thái: **master kỹ thuật có layer và kiểm chứng đăng ký pixel**, chưa phải art cuối hoặc bộ nhân vật gameplay đầy đủ. Các PNG base/đồ sinh riêng trước đây bị chủ dự án bác bỏ vì tỉ lệ và khớp nối sai; không tiếp tục coi chúng là nguồn master.

## Quyết định

Dùng một nguồn hình học và pose cho body và trang phục. Vẽ/retouch nhân vật mặc hoàn chỉnh trên canvas này, giữ các phần trên layer riêng. Mỗi trang phục lấy cổ, vai, khuỷu, cổ tay, eo, háng và chân từ cùng pose. Xuất layer theo tọa độ gốc, không tự fit theo alpha bounds và không kéo giãn từng món cho vừa một base khác.

Bản hiện tại dùng nguồn authoring native gồm master.json và RegisteredPaperDollMaster.cs để dựng pixel trên cùng lưới; đây là nguồn kỹ thuật có thể chỉnh, không phải ảnh AI vẽ riêng rồi dán. File .aseprite được xuất để trau chuốt trên các layer thật. Nét vẽ còn ở mức prototype; kiểm khớp không đồng nghĩa đẹp hoặc hoàn tất.

Source rig mới là RIG_HUMAN_M_V2/F_V2; class profile V1 giữ lịch sử, không trộn quần áo V1 vào V2.

## Tỉ lệ và pose

- Canvas 96×96; điểm chân (48,72).
- Chiều cao đứng 54 pixel; đầu 12 pixel, khoảng 4,5 đầu.
- Đầu ở y=18; cổ nối tới vai y≈33–34; eo y=48; hông y=51; gối y=60; cổ chân y=69.
- Tay nối cùng vai/khuỷu/cổ tay trong cả body và sleeve. Chân/pants dùng chung trục hông–gối–cổ chân.
- 16 pose khớp được định nghĩa rõ, đầu/vài/eo và tay thay đổi; bàn chân không trôi. Kiểm không có body/outfit lặp pixel để đệm số.
- Hiện chỉ S/idle, chu kỳ 1,6 giây; renderer giới hạn 60 FPS. Chưa có đủ 8 hướng, walk, combat hay sáu skill.

Nguồn authoring:
- ClientGodot/assets/paperdoll_master/master.json: hợp đồng tỉ lệ và bảng pose.
- ClientGodot/scripts/RegisteredPaperDollMaster.cs: hình học, pixel palette, layer và xuất source.
- Art_Source/Registered_Master_20261110: hai file .aseprite có 20 layer, 16 frame mỗi file.

Một số tỉ lệ là hợp đồng cố định với source vẽ; sửa anatomy cần sửa nguồn vẽ và JSON cùng nhau rồi nghiệm thu lại, không chỉ đổi một con số UI.

## Bộ ngoại hình và trang bị

Một lựa chọn OUTFIT gồm cả áo và quần. Nam/nữ có biến thể phù hợp rig; một pose dùng đúng biến thể. Giày, vũ khí, tóc, mắt, mũ và cape vẫn độc lập.

Chỉ đổi presentation. EQUIP_CHEST/EQUIP_LEGS cùng item, stat, nâng cấp và protocol hiện có vẫn giữ. Resolver tương lai chọn outfit family từ áo/ngoại trang để phủ phần hiển thị áo và quần; không gửi thao tác tháo quần hoặc thay chỉ số. Phòng thử hiện chưa nối equip online.

## Nón và kiếm

Nón giữ hairStyle. Với nón rộng, chỉ phần crown/topknot nằm dưới vùng che bị mask; mái và tóc hai bên còn nguyên. Tháo/ẩn nón trả lại toàn bộ vùng tóc và transform ban đầu. Source có hai layer UNDER_HAT riêng để retouch.

Kiếm ngắn hơn body, có nguồn chéo trái/phải. Pivot ở cán, gắn hand_near; skin hand_near được vẽ sau kiếm để phủ cán. Chỉnh góc thêm quanh pivot, không lấy góc trên-trái ảnh làm điểm cầm.

## Phòng thử nâng cấp

Mở ClientGodot/Run_PaperDoll_Lab.ps1. Mặc định dùng registered master. PNG cũ chỉ là nguồn tham khảo bị bác bỏ, không bật mặc định.

- Chọn nam/nữ, tóc/mắt, outfit liền, giày, kiếm, nón/cape.
- Inspector có ba tab: Vị trí; Góc & lớp; Bản nháp.
- X/Y có ba hệ: offset theo anchor, canvas master, viewport. Attachment đổi neo nhưng giữ vị trí hiện tại.
- Pivot nhập theo pixel nguồn; đổi pivot giữ vị trí ảnh trên lưới, nút “Đưa pivot về điểm neo” dùng để gắn cán kiếm vào tay. Quay -180..180°, scale thử .25..2, lật ngang/dọc, ẩn/hiện.
- Nút trước/sau đổi painter order theo pose; có thể chọn skin bàn tay để kiểm lớp nắm cán.
- Kéo thả; Ctrl+bấm chọn lớp theo bounds; Alt+bấm đặt pivot. Gizmo hiển thị biên, pivot và trục X phải/Y xuống.
- Chỉnh pose hiện tại hoặc áp cho cả 16 placement. Chép pose trước. Undo/Redo dành cho thao tác fit.
- Draft master lưu riêng fit_registered_master_v1.json, gắn SHA nguồn; không ghi đè draft PNG cũ.
- Đổi đồ giữ clock. Lỗi transform/texture/schema giữ bản trước.

Thao tác thử:
```powershell
.\ClientGodot\Run_PaperDoll_Lab.ps1 -Hat
.\ClientGodot\Run_PaperDoll_Lab.ps1 -Female -Indigo -Hat
.\ClientGodot\Run_PaperDoll_Lab.ps1 -SelfTest
```

## Nguồn .aseprite

Hai file có 20 layer/frame, gồm body, hai outfit, boots, bốn kiếm, tay trước, mắt, tóc, under-hat và mũ/cape. Variants không dùng được tắt mặc định. Tag IDLE_S_16_MASTER; 100 ms/frame.

Nút “Xuất master gốc .aseprite” xuất source gốc, không bake fit draft; dùng -ExportMaster để chọn thư mục qua launcher.

File được viết theo [đặc tả chính thức Aseprite](https://github.com/aseprite/aseprite/blob/main/docs/ase-file-specs.md), dùng RGBA 32-bit và cel ZLIB. Bộ kiểm tra độc lập đọc lại chunk/layer/cel và so hash bản flatten. Chưa xác nhận mở trên GUI Aseprite trong phiên này.

Bản source xuất là điểm bắt đầu retouch có layer. Nạp ngược bản đã retouch vào catalog runtime/production vẫn cần importer và review; hiện phòng thử dựng từ nguồn native, không tự đọc mọi chỉnh sửa .aseprite.

## Nghiệm thu kỹ thuật và việc còn lại

So sánh 64 composite (2 body × 2 outfit × 16 pose) với bản tổng hợp trực tiếp từ master, yêu cầu 0 pixel lệch. Kiểm riêng các màu coverage nền không thò ra ngoài outfit. Hai source .aseprite phải có 16 body pose và 16 outfit pose khác nhau, flatten khớp reference.

Đây là phép đo đăng ký layer và hình học; chưa nghiệm thu chất lượng mỹ thuật. Còn cần retouch nét/shading/silhouette, đủ hành động/hướng, importer source, approved registry/hash, appearance/equip persistence, UI tạo nhân vật và kiểm đông người. Không bật hero modular gameplay bằng bộ này. Master 54 px cần nghiệm thu cỡ hiển thị world/camera riêng trước khi tích hợp; không đổi collider hoặc camera toàn game theo phòng thử.
