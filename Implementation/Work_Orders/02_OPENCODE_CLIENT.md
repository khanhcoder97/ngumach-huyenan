# OpenCode — GitHub Asset Pipeline Validator

## Gói tiếp theo đang được giao — 2026-10-29

OPC-05 đã bàn giao; PR #31 là coverage follow-up đang review. Tiếp tục cả gói OPC-06→10 trong `05_OPENCODE_ASSET_PIPELINE_EPIC.md` theo cơ chế `04_CONTINUOUS_DELIVERY_20261029.md`. Phạm vi được mở rộng sang schema migration có review, PNG/meta hardening, browser preview và release tooling; các hạn chế phạm vi OPC-05 bên dưới không chặn gói mới. Không cần Unity; không dừng sau mỗi PR nếu còn phần độc lập được giao.

## Lý do đổi phạm vi

Máy phát triển hiện không đủ tài nguyên để cài Unity Editor. Tạm hoãn Unity client runtime cho tới khi có máy build phù hợp. Hạng mục hiện tại chạy bằng Python tiêu chuẩn và GitHub Actions, không cần Unity, .NET hay engine cài trên máy.

## Phạm vi sở hữu

- `.github/workflows/asset-handoff-validation.yml`
- `Implementation/Asset_Handoff/validate_asset_delivery.py`
- `Implementation/Asset_Handoff/tests/`

Không sửa asset, manifest do Muse giao, schema giao nhận, server, contract, Unity runtime hay production specs. Nếu schema hiện tại chưa đủ để kiểm tra yêu cầu, mở integration issue và mô tả thay đổi cần thiết trước.

## OPC-05: Kiểm tra asset handoff tự động

Tạo validator Python chỉ dùng standard library để kiểm tra `Client/Assets/ArtManifests/muse_delivery_manifest.json` khi PR có thay đổi art:

1. Đọc và kiểm tra manifest theo `Implementation/Asset_Handoff/asset_delivery_manifest.schema.json` và mẫu `muse_delivery_manifest.example.json`.
2. Kiểm tra `assetId` và `path` không trùng; đường dẫn ở trong repo và trỏ tới asset cùng preview có thật.
3. Kiểm tra PNG dimensions khớp manifest bằng đọc IHDR; từ chối file LFS pointer thay vì nội dung ảnh trong job CI.
4. Kiểm tra `pixelsPerUnit` bằng 20, các path nằm trong thư mục asset hợp lệ, `sourceLicense` là `original`, và sprite sheet có đủ 8 hướng đúng thứ tự.
5. Kiểm tra thông tin animation tối thiểu gồm tên, frame count và FPS hợp lệ; không tự yêu cầu mọi animation phải có cùng số frame.
6. Báo lỗi gồm asset ID, file và field cụ thể; trả exit code khác 0 khi sai.
7. Thêm unit tests Python `unittest`: manifest hợp lệ, ID trùng, path traversal, file thiếu, PNG dimensions lệch, thiếu hướng và manifest sai schema.
8. Tạo GitHub Actions workflow chỉ chạy khi PR thay đổi art/manifest/handoff; bật Git LFS checkout; không cài Unity.

## Giao thức với Muse

- Dùng manifest/schema đã merge; không tự sửa manifest của Muse.
- Nếu cần metadata như `frameWidth` chưa có trong schema, mở integration issue yêu cầu Muse/owner bổ sung rồi cập nhật validator sau khi có quyết định.
- Báo cho Muse trong issue #1 về field validator yêu cầu và lỗi asset dễ gặp.

## Bàn giao

- Branch: `opencode/opc-05-asset-validator`.
- PR tiêu đề `[OpenCode] Add asset handoff validation`; body liên kết `Refs #2`.
- Ghi lệnh chạy local, ví dụ input tối thiểu, sample pass/fail và giới hạn kiểm tra PNG trong README nhỏ.
- CI mới phải chạy xanh trên GitHub. Không cần mở Unity Editor để nghiệm thu.

## Tiêu chí hoàn tất

- Bộ test Python chạy bằng `python -m unittest discover` và pass.
- Workflow chạy thành công trong GitHub Actions cho manifest hợp lệ, và fail có giải thích khi PR có manifest/file sai.
- Không cần Unity hoặc dependency Python ngoài standard library.
- Work order Unity client được giữ lại làm backlog tương lai sau OPC-05, không nằm trong nghiệm thu hiện tại.
