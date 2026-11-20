> 12/11/2026 — ĐÃ THAY THẾ: chủ dự án hủy hướng nhân vật paper-doll mới, quay lại sprite sheet chibi cũ. Mặc định mở ArtStudio.tscn; xem [hướng dẫn hiện hành](Sprite_Studio_20261112_vi.md). Nội dung dưới đây là lịch sử.

# Khóa hướng mỹ thuật nhân vật pixel — 10/11/2026, lần sửa phong cách

Yêu cầu của chủ dự án: không dùng cách vẽ hình khối/procedural vừa thử; giữ phong cách pixel chi tiết của bộ trước, điều chỉnh cơ thể dài hơn và vẽ quần áo theo base mới.

## Quy tắc hiện hành

1. Dùng nét minh họa pixel liền mạch, đường viền bo tự nhiên, cụm pixel nhỏ, nhiều mức sáng/tối có chủ đích. Không thay sprite bằng các hình chữ nhật/đoạn rời hay dùng bản kỹ thuật 54 px làm chuẩn mỹ thuật.
2. Giữ vẻ stylized/chibi fantasy của reference. Tăng chiều dài cổ, thân, cẳng tay, đùi/cẳng chân theo hình tổng thể; tỉ lệ mới là ứng viên, chưa chốt bằng một con số lý thuyết.
3. Vẽ base trước. Vẽ cả áo và quần thành một bộ trực tiếp trên cùng dáng/base, khớp cổ/vai/khuỷu/cổ tay/hông/gối. Không sinh quần áo độc lập rồi cố kéo scale từng món.
4. Bản chỉnh diện mạo giữ trang phục/tỉ lệ; thêm tóc/mắt và kiếm có cán nằm trong tay. Trang bị và chỉ số gameplay không đổi.
5. Nguồn authoring phải đủ mật độ chi tiết để giữ nét cũ; không ép về độ thô của mẫu procedural bằng cách vẽ lại từng mảng. Grid/atlas/runtime v3 chỉ được khóa sau khi master được nghiệm thu.
6. Chuẩn animation 16–20 pose thật/action/hướng và render 60 FPS vẫn giữ. Một hình master không được tính thành bộ animation bằng lặp hoặc đổi metadata.
7. Không dùng kết quả 0-pixel của mẫu procedural để công nhận master ảnh mới. Phải kiểm source layer/pose thực của master mới.

## Đã tạo

Art_Source/Restored_Pixel_Style_20261110: base nam/nữ; outfit ngà/ngọc edit trên base; diện mạo hoàn chỉnh edit tiếp. PNG/prompt/reference chain và SHA được lưu, không sửa/resample bitmap bằng script.

Đây là master một pose hướng S. Viền alpha, nối layer, mặt/tóc/đồ độc lập, đủ góc/động tác, fit và animation chưa nghiệm thu. Bản ảnh hoàn chỉnh là composite để xét nét/tỉ lệ, không phải một gói paper-doll đã tách.

## Phòng xem

Run_PaperDoll_Lab.ps1 mặc định mở PaperDollArtReview.tscn với ba bản vẽ. Công cụ không vẽ procedural nhân vật. Chồng base chỉ giúp đối chiếu bằng mắt.

- -ArtView 0/1/2 chọn Base/Trang phục/Diện mạo.
- -ArtSelfTest kiểm nạp ảnh, hash và nút chuyển.
- -Capture đường_dẫn.png chụp viewport.
- -FitTools chỉ là công cụ kỹ thuật cũ, tách khỏi màn xem chính.
- -SelfTest giữ kiểm hợp đồng/cơ chế cũ, không chứng nhận thẩm mỹ.

Chưa thay hero gameplay, chưa sửa source equip/HP/stat, chưa hứa đã có 8 hướng hoặc 16–20 khung cho hình mới. Các file registered master V2 cũ giữ lịch sử kỹ thuật, bị bác bỏ làm mẫu vẽ.
