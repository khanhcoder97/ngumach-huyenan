# Cơ chế cộng tác GitHub

## Cập nhật quyền và nhịp làm việc 2026-10-29

Các gói liên tục và quyền sửa mở rộng tại `Implementation/Work_Orders/04_CONTINUOUS_DELIVERY_20261029.md` được ưu tiên hơn bảng phạm vi ban đầu bên dưới. OpenCode nhận toàn bộ dây chuyền asset không Unity OPC-06→10; Qoder nhận vòng chơi authoritative QOD-11→15. Mỗi mốc vẫn qua PR/review; mở PR xong tiếp tục phần độc lập hoặc stacked branch thay vì chờ giao một tác vụ nhỏ mới. Issue gói việc và work orders 05/06 chứa acceptance criteria. Không tự merge hoặc bỏ gate chưa đủ dữ liệu.

## Mục tiêu

Muse làm asset trên máy ảo riêng. Asset chỉ đi vào nhánh `main` qua GitHub Pull Request (PR), có manifest, preview và asset-handoff CI validation. Unity import/runtime integration được ghi rõ là chưa xác minh cho tới khi có máy Unity phù hợp.

## Truy cập repo

Repo `khanhcoder97/ngumach-huyenan` hiện public. Các agent clone từ `main`; quyền ghi hiện dùng chung tài khoản chủ repo theo quyết định ở GitHub issue #4. Không đưa token vào issue, PR, source hoặc file cấu hình.

```powershell
git clone https://github.com/khanhcoder97/ngumach-huyenan.git
cd ngumach-huyenan
git lfs install
git config user.name "Muse"  # đổi thành OpenCode / Qoder theo agent
git config user.email "khanhcoder97@users.noreply.github.com"
git switch -c muse/p1-first-asset-pack  # OpenCode: opencode/opc-05-asset-validator
                                          # Qoder: qoder/qod-06-combat-endpoint
```

`git user.name` giúp nhận diện agent trong commit; branch prefix và tiêu đề PR là định danh bổ sung. Chỉ owner merge vào `main`. Nếu branch ruleset chưa bật, owner kiểm tra PR và yêu cầu CI xanh trước khi merge.

## Nhánh và phạm vi

| Agent | Prefix nhánh | Thư mục được phép sửa |
|---|---|---|
| Muse | `muse/` | `Client/Assets/Art/`, `Client/Assets/UI/Art/`, `Client/Assets/Tilemaps/`, `Client/Assets/VFX/`, `Client/Assets/Animation/`, `Client/Assets/ArtManifests/`, `Implementation/Asset_Handoff/` |
| OpenCode | `opencode/` | `.github/workflows/asset-handoff-validation.yml`, `Implementation/Asset_Handoff/validate_asset_delivery.py`, `Implementation/Asset_Handoff/tests/` |
| Qoder | `qoder/` | `Server/`, `Implementation/Contracts/`, `Implementation/Tools/`, `Implementation/Reports/`, `Implementation/Content/Runtime/` |

Không gộp hai agent vào một branch. `main` chỉ chứa nội dung đã review.

## Quy trình Muse → GitHub → Unity

1. Muse tạo branch, ví dụ `muse/p1-thang-long-city-kit`, từ `main` mới nhất.
2. Muse chạy `git lfs install`, thêm source file và bản PNG export. Không commit file export thử, PSD/Aseprite thiếu layer hay file Unity `Library/`.
3. Muse cập nhật `Client/Assets/ArtManifests/muse_delivery_manifest.json` theo schema tại `Implementation/Asset_Handoff/asset_delivery_manifest.schema.json`.
4. Muse tạo PR dùng template `ASSET_HANDOFF.md`, kèm preview PNG/GIF trong PR body và ghi rõ `assetPackVersion`.
5. Asset handoff CI kiểm tra manifest, PNG dimensions, PPU metadata, hướng sprite và đường dẫn file. Hiện chưa có máy đủ khả năng chạy Unity import; ghi rõ engine import là `unverified` cho tới khi có Unity-capable build machine.
6. Sau khi PR merge, lưu asset trong `main` để làm nguồn chuẩn. Prefab/scene runtime integration được thực hiện khi client Unity workstream tiếp tục; không tuyên bố asset đã import trong engine nếu chưa có kết quả thực tế.
7. Nếu Muse cần thay thế asset đã dùng, tạo version mới trong manifest. Không đổi đường dẫn hoặc `assetId` của asset đã được tích hợp mà không có migration note.

## Contract bàn giao asset

Một bundle asset có thể được dùng bởi OpenCode khi và chỉ khi:

- Có `assetPackVersion` tăng dần.
- Mỗi asset có `assetId`, path, loại asset, trạng thái và bản quyền nguồn `original`.
- Có dimensions, PPU, pivot hoặc tile size; animation có FPS và event frames.
- PR chứa preview.
- Không có file mượn, file từ game tham chiếu, hay asset không xác định nguồn.

## Giao tiếp giữa agent

- Công việc được giao và cập nhật trong GitHub Issues gắn nhãn `agent:muse`, `agent:opencode`, `agent:qoder`; mỗi agent comment xác nhận nhận việc, branch, tiến độ và blocker.
- Yêu cầu thay đổi asset hoặc contract: tạo GitHub Issue với label `integration` rồi liên kết vào PR.
- Thay đổi chặn tiến độ: ghi trong `Implementation/Work_Orders/Integration_Notes.md` và mở Issue cùng ngày.
- OpenCode duy trì kiểm tra manifest qua CI; Muse không merge thay đổi C#; Qoder không merge thay đổi client/art.
- OpenCode hiện xây validator asset bằng Python/GitHub Actions, không cần Unity; Unity client runtime/import verification vẫn là backlog.
- Issues điều phối: Muse #1, OpenCode #2, Qoder P1 #3, Qoder combat endpoint #13. Agent phải liên kết PR về issue tương ứng; khi scope tiếp diễn, tạo issue mới hoặc ghi rõ milestone kế tiếp trên issue.

## Khôi phục khi asset PR bị lỗi

Revert PR trên GitHub bằng PR mới; không force push `main`. Muse tạo PR hotfix với asset pack version mới và manifest ghi asset bị thay thế.
