# OpenCode — Gói công cụ asset hoàn chỉnh OPC-06 → OPC-10

Nhận cả gói và thực hiện liên tục theo `04_CONTINUOUS_DELIVERY_20261029.md`. Không cần cài Unity. Đích là một dây chuyền mà Muse giao bundle, người quản lý kiểm lỗi/xem trước, và người tích hợp nhận được gói có nguồn gốc rõ ràng. Không phải một bản báo cáo rồi dừng.

## Mốc 0 — Kết thúc đúng PR #31

Giữ branch/worktree PR #31, cập nhật main và kiểm tra lại report generated sau thay đổi nguồn. Không tự sửa asset `filterMode` của Muse. Phân biệt lỗi metadata thực với bước playback chưa kiểm chứng. Lệnh `coverage_audit.py --check` phải tái tạo được ở CI Linux và local Windows; không dùng timestamp/SHA tự thay đổi gây fail mỗi lần commit.

## OPC-06 — Manifest có frame geometry và hướng rõ ràng

- Sửa proposal #33: walk thật 288×512, 6 cột frame, 8 hàng hướng, frame 48×64, 8 FPS. Với layout direction-rows, width = frameWidth × framesPerDirection, height = frameHeight × directionCount; không nhân directions vào cả width lẫn height.
- Được giao triển khai draft migration cho `frameSize` và `isDirectional`, kèm phân biệt legacy/v2 rõ ràng. Giữ legacy manifest đang có đọc được; không ngầm mặc định mọi sheet mới là không hướng. Quyết định schema/version/layout phải thể hiện bằng proposal và PR trước khi chuyển bundle của Muse.
- Quy định layout hỗ trợ cụ thể, nhiều animation không dùng công thức một clip để kiểm toàn sheet; layout khác cần frame rect/clip ranges được mô tả hoặc trả unsupported rõ ràng. Không suy ra các rect tùy ý từ số frame.
- Có ví dụ hợp lệ cho actor 8 hướng, effect một hướng, icon tĩnh; ví dụ fail thiếu kích thước, lệch grid, hướng trùng/thứ tự sai và version không hỗ trợ. Dùng kind có sẵn, không thêm enum vô cớ.
- Không rewrite manifest Muse trong PR tooling. Cung cấp lệnh dry-run migration và diff để Muse dùng sau review.

## OPC-07 — Kiểm tra PNG và Unity import metadata

- Kiểm PNG ngoài IHDR: cấu trúc chunk/CRC, kết thúc file, dữ liệu ảnh hỏng, LFS pointer, kích thước và giới hạn giải nén an toàn. Ghi chính xác subset PNG được hỗ trợ; không PASS format chưa thực sự giải mã/kiểm tra.
- Kiểm alpha cho asset được khai báo cần trong suốt; báo opaque-background nghi vấn ở mức đúng. Không đoán alpha/palette chỉ từ screenshot, không đặt mọi UI opaque thành lỗi.
- Đọc `.meta` tĩnh cho PPU, Point, mipmaps, compression, pivot, sprite rect và bounds. GUID/path trùng và asset thiếu meta phải có finding rõ. Parser chỉ hỗ trợ cấu trúc đã kiểm chứng; cấu trúc lạ ghi unsupported/unverified thay vì PASS.
- Report JSON/MD có severity, field, assetId, evidence path và phép đo. Tách structural validation, static import metadata, art review và engine runtime.
- Tests âm tính thực sự: PNG truncated/CRC lỗi, pointer, rect vượt ảnh, duplicate GUID, Bilinear, pivot lệch. Không tạo test chỉ đối chiếu lại hằng số trong implementation.

## OPC-08 — Asset Preview chạy bằng trình duyệt trên máy yếu

Tạo `Tools/AssetPreview/`: trang HTML/CSS/JS tĩnh và server Python stdlib chỉ bind localhost. Chỉ là công cụ xem asset; không thay Unity client hoặc giả gameplay server.

- Load manifest/report qua cùng origin; không yêu cầu npm build hay dịch vụ ngoài. Chống path traversal ở local server, không expose thư mục máy tùy ý.
- Lọc theo lớp/loại/trạng thái/từ khóa; chọn asset để thấy kích thước, PPU, source/hash và lỗi.
- Canvas nearest-neighbor zoom 1×/2×/4×, lưới frame, nền sáng/tối/checker; play/pause, chọn clip/hướng, tốc độ từ metadata. Layout không hỗ trợ phải báo rõ, không cắt hình đoán.
- VFX timeline xem prep/release/hold/end theo metadata; thiếu runtime asset chỉ hiện missing/concept, không crop concept board thành effect. Hiển thị native preview và chế độ nhiều instance để review độ che khuất; không chứng nhận FPS engine.
- Có smoke hướng dẫn cụ thể và ảnh chụp công cụ chạy với asset thật. Chọn một actor và một effect fixture có nhãn synthetic khi Muse chưa giao effect; không đưa fixture vào catalog runtime.

## OPC-09 — Release bundle và coverage dùng để tích hợp

- Lệnh audit một bundle bất kỳ, xuất danh mục file/kích thước/hash/license/version/dependencies và validation summary. Chỉ đọc nguồn; đóng gói ra thư mục output mới, không ghi đè art.
- Lệnh pack/dry-run với allowlist đường dẫn, fail missing/deprecated reference hoặc chưa đủ metadata; đối với draft chỉ được tạo bundle draft với cảnh báo rõ.
- Coverage liên kết canonical class/skill/map và các design baselines với runtime definitions và asset khi có mapping explicit. Record nội dung, placement và asset độc lập phải đếm riêng. Không suy ra asset tồn tại chỉ vì ID giống tên.
- Đầu ra phân biệt present/absent/unknown/unverified, giữ evidence SHA; deterministic theo cùng input. Archive lặp lại phải cùng nội dung manifest/digest; không chứa token, Library, cache hoặc output cũ.

## OPC-10 — CI và bàn giao cả dây chuyền

- Workflow LFS checkout, validate legacy/v2 fixtures, unit tests và report check trên phạm vi path phù hợp. Chạy được khi không có Unity và không có PNG LFS hydrated thì fail giải thích, không pass giả.
- Một lệnh kiểm tra local tổng hợp và README từ clone → LFS → validate → preview → pack. Có bộ input fail có thể tái tạo.
- Cập nhật report coverage cuối gói từ main đã tích hợp; liệt kê finding Muse phải sửa và integration Qoder cần, không tự thay code của họ.
- Hoàn tất bằng demo liên tục một bundle: phát hiện lỗi → sửa fixture → pass → preview → tạo bundle/hash. Ghi exact SHA và lệnh đã chạy. Art quality/Unity playback vẫn unverified nếu chưa có bằng chứng.

## Nhịp giao việc và giới hạn

Mỗi mốc một PR hoặc vài PR có dependency rõ; không gộp toàn gói thành PR khổng lồ. Sau khi mở PR tiếp tục mốc độc lập kế tiếp, tự sửa CI/review trong phạm vi. Nếu v2 đang chờ review vẫn làm PNG validator, preview khung và pack legacy. Không tự merge. Không đổi balance, server/P1 contract, runtime C# hoặc vẽ thay Muse. Ghi checkpoint nếu phiên dừng; không tuyên bố đã hoàn thành phần chưa chạy.
