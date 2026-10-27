# Phân công ba agent — Ngũ Mạch: Huyền Ấn

Tài liệu này là đầu mối điều phối. Mỗi agent chỉ sửa các khu vực mình sở hữu. Mọi định nghĩa gameplay dùng ID chuẩn trong `docs/production/` và `Implementation/Content/`.

| Agent | Trách nhiệm chính | Tài liệu giao việc |
|---|---|---|
| Muse | Toàn bộ hình ảnh pixel art, animation, tilemap, VFX và UI art | `01_MUSE_PIXEL_ART.md` |
| OpenCode | Unity client: gameplay runtime, điều khiển, networking client, UI logic | `02_OPENCODE_CLIENT.md` |
| Qoder | ASP.NET Core authoritative server, gameplay systems, dữ liệu và kiểm thử | `03_QODER_SERVER_CONTENT.md` |

## Quy ước chung

- Phong cách: pixel art nguyên gốc, 640×360 logical render, 20 PPU, Point filter, không mipmap. Chi tiết ở `docs/production/Pixel_Art_Production_Standard_vi.md`.
- Không sao chép asset, tên riêng, bản đồ, hội thoại hay dữ liệu từ game tham chiếu.
- Không thay đổi schema, ID canonical hay tài liệu đặc tả khi chưa ghi một đề xuất thay đổi trong `Implementation/Work_Orders/Proposals/`.
- Asset mới dùng tên lowercase snake_case, không dấu; một file `.meta` đi kèm mọi asset Unity.
- Các agent không sửa file do agent khác sở hữu. Khi cần tích hợp, tạo file mới ở khu vực của mình hoặc ghi yêu cầu trong `Implementation/Work_Orders/Integration_Notes.md`.

## Điểm tích hợp

1. **Muse → OpenCode:** PNG, sprite sheet, tile palette, Animation Clip/Controller metadata và asset manifest.
2. **Qoder → OpenCode:** endpoint contract, error code, ví dụ request/response và bản build API cục bộ.
3. **OpenCode → Muse:** danh sách prefab/canvas cần asset, kích thước sprite chính xác và trạng thái thiếu asset.
4. **OpenCode → Qoder:** yêu cầu contract thay đổi dưới dạng JSON mẫu, không tự sửa server schema.

## Definition of done chung

- Không lỗi compile ở phần thay đổi.
- Không làm lệch chuẩn pixel rendering.
- Mọi endpoint hoặc asset có manifest/README ngắn mô tả cách dùng.
- Đã chạy validator liên quan nếu môi trường cài công cụ: `python Implementation/Tools/validate_content.py`, `python Implementation/Tools/validate_contracts.py`, Unity import/build hoặc `dotnet build`.

## GitHub issue queue

Mọi công việc của agent được nhận và cập nhật qua GitHub Issues; không coi file work order trong máy local là thông báo giao việc. Agent comment vào issue để nhận việc, ghi branch, cập nhật tiến độ và báo blocker. Mỗi PR phải liên kết issue tương ứng; merge vào `main` chỉ sau review và kiểm tra thuộc phạm vi.

- Muse pixel-art delivery: https://github.com/khanhcoder97/ngumach-huyenan/issues/1
- OpenCode Unity client P1 slice: https://github.com/khanhcoder97/ngumach-huyenan/issues/2
- Qoder authoritative server P1 slice: https://github.com/khanhcoder97/ngumach-huyenan/issues/3
- Qoder combat endpoint follow-up: https://github.com/khanhcoder97/ngumach-huyenan/issues/13

Repo được mở public ngày 2026-10-27. Theo mô hình đã chốt tại issue #4, các agent dùng chung tài khoản chủ repo; phân biệt bằng `git user.name`, branch prefix và tiêu đề PR. Agent xác nhận nhận việc, branch, tiến độ và blocker bằng comment trên issue.

## Trạng thái điều phối 2026-10-27

- Qoder đã hoàn tất P1 server, combat/quest/inventory/teleport service skeletons và runtime self-check; PR #5–#12 đã merge, CI trên `main` xanh. Việc tiếp theo là issue #13.
- OpenCode cần bắt đầu tích hợp session/movement/world snapshot theo issue #2.
- Muse cần bắt đầu asset pack đầu tiên theo issue #1.
