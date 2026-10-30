# Phân công ba agent — Ngũ Mạch: Huyền Ấn

## Owner hiện hành sau bàn giao OpenCode — 2026-10-31

Theo yêu cầu chủ dự án, **Codex nhận toàn bộ OPC-05b/06…12**: coverage, manifest/migration, PNG/meta, preview, pack/CI, compiler dữ liệu ứng viên và adapter map Muse. OpenCode giữ các checkout/WIP cũ để đối chiếu, không sửa/push tiếp các nhánh đã bàn giao. Chi tiết tại `15_CODEX_OPENCODE_TAKEOVER_20261031.md`; các phân công OpenCode bên dưới là lịch sử và không còn là lệnh giao mới.

Qoder local tiếp gameplay/Health tại #41/#87; QODER Remote giữ Persistence tại #79; Antigravity giữ PlayerUI tại #85/#89; Muse giữ art/map/sprite/VFX/cinema và native engine evidence tại #1/#29/#39. Codex tiếp tục quản lý/review/client core/audio và phần tooling mới nhận. Không dùng checkout của nhau, không tự thay canonical IDs/349XY hoặc bật runtime từ candidate.

## Chương trình hiện hành từ 2026-10-29

Đọc `04_CONTINUOUS_DELIVERY_20261029.md` trước các backlog P1 bên dưới. OpenCode nhận gói OPC-06→10 tại `05_OPENCODE_ASSET_PIPELINE_EPIC.md`; Qoder nhận QOD-11→15 tại `06_QODER_GAMEPLAY_LOOP_EPIC.md`. Được làm tiếp mốc độc lập sau mỗi PR, giữ review gate và worktree riêng. Muse tiếp tục hàng đợi art/map/UI/VFX/cinema theo #1/#29/#39. Quyền sửa mở rộng và các profile camera mới ghi tại work order 04; bảng cũ bên dưới chỉ là baseline ban đầu.

Tài liệu này là đầu mối điều phối. Mỗi agent chỉ sửa các khu vực mình sở hữu. Mọi định nghĩa gameplay dùng ID chuẩn trong `docs/production/` và `Implementation/Content/`.

| Agent | Trách nhiệm chính | Tài liệu giao việc |
|---|---|---|
| Muse | Toàn bộ hình ảnh pixel art, animation, tilemap, VFX và UI art | `01_MUSE_PIXEL_ART.md` |
| OpenCode | GitHub asset handoff validator và CI; Unity client chuyển thành backlog khi có máy build phù hợp | `02_OPENCODE_CLIENT.md` |
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
- OpenCode asset handoff validator: https://github.com/khanhcoder97/ngumach-huyenan/issues/2
- Qoder authoritative server P1 slice: https://github.com/khanhcoder97/ngumach-huyenan/issues/3
- Qoder combat endpoint follow-up: https://github.com/khanhcoder97/ngumach-huyenan/issues/13

Repo được mở public ngày 2026-10-27. Theo mô hình đã chốt tại issue #4, các agent dùng chung tài khoản chủ repo; phân biệt bằng `git user.name`, branch prefix và tiêu đề PR. Agent xác nhận nhận việc, branch, tiến độ và blocker bằng comment trên issue.

## Trạng thái điều phối 2026-10-27

- Qoder đã hoàn tất P1 server, combat/quest/inventory/teleport service skeletons và runtime self-check; PR #5–#12 đã merge, CI trên `main` xanh. Việc tiếp theo là issue #13.
- OpenCode cần triển khai asset handoff validator không cần Unity theo issue #2; client runtime được hoãn.
- Muse cần bắt đầu asset pack đầu tiên theo issue #1.


## Antigravity AG-02 acceptance — 2026-10-31

Review exact head a0bb0ab (PR89):71author checks PASS nhưng84producer acceptance checks có11FAIL; factory binding3compiler diagnostics (synthetic API probe, không nativeUnity). Đọc `16_ANTIGRAVITY_AG02_ACCEPTANCE_COMPLETION_20261031.md` và `Antigravity_AG02_Review_20261031.md`. Antigravity tiếp toànR0→R6 trên nhánh/PR89 và issue85 hiện hành; không mởepic mới hoặc tựmerge/đóng. Codex giữreview/tooling; Qoder/Muse ownership khôngđổi.
