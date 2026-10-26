# Cơ chế cộng tác GitHub

## Mục tiêu

Muse làm asset trên máy ảo riêng. Asset chỉ đi vào nhánh `main` qua GitHub Pull Request (PR), có manifest, preview và kiểm tra import Unity. OpenCode và Qoder tiếp tục làm mã nguồn ở nhánh riêng, không chờ quyền truy cập trực tiếp vào máy Muse.

## Khởi tạo một lần bởi quản trị dự án

1. Tạo GitHub repository riêng tư `NGUMACHHUYENAN` và thêm ba tài khoản Muse, OpenCode, Qoder quyền Write.
2. Từ thư mục dự án hiện tại, gắn remote và đẩy baseline:

```powershell
git remote add origin <GITHUB_REPOSITORY_URL>
git add .
git commit -m "chore: establish project baseline and collaboration workflow"
git push -u origin main
```

3. Trên GitHub, bật branch protection cho `main`:
   - Bắt buộc Pull Request.
   - Cấm force push và xóa branch.
   - Bắt buộc một review trước khi merge.
   - Bắt buộc kiểm tra `content-validation` và `contract-validation` khi các workflow này được thêm vào CI.
4. Điền tên GitHub thật vào `.github/CODEOWNERS.example`, sau đó đổi tên thành `.github/CODEOWNERS`.

## Nhánh và phạm vi

| Agent | Prefix nhánh | Thư mục được phép sửa |
|---|---|---|
| Muse | `muse/` | `Client/Assets/Art/`, `Client/Assets/UI/Art/`, `Client/Assets/Tilemaps/`, `Client/Assets/VFX/`, `Client/Assets/Animation/`, `Client/Assets/ArtManifests/`, `Implementation/Asset_Handoff/` |
| OpenCode | `opencode/` | `Client/Assets/Scripts/`, `Client/Assets/Prefabs/`, `Client/Assets/Scenes/`, `Client/Assets/UI/UXML/`, `Client/Assets/UI/USS/`, `Client/Assets/Tests/` |
| Qoder | `qoder/` | `Server/`, `Implementation/Contracts/`, `Implementation/Tools/`, `Implementation/Reports/`, `Implementation/Content/Runtime/` |

Không gộp hai agent vào một branch. `main` chỉ chứa nội dung đã review.

## Quy trình Muse → GitHub → Unity

1. Muse tạo branch, ví dụ `muse/p1-thang-long-city-kit`, từ `main` mới nhất.
2. Muse chạy `git lfs install`, thêm source file và bản PNG export. Không commit file export thử, PSD/Aseprite thiếu layer hay file Unity `Library/`.
3. Muse cập nhật `Client/Assets/ArtManifests/muse_delivery_manifest.json` theo schema tại `Implementation/Asset_Handoff/asset_delivery_manifest.schema.json`.
4. Muse tạo PR dùng template `ASSET_HANDOFF.md`, kèm preview PNG/GIF trong PR body và ghi rõ `assetPackVersion`.
5. OpenCode checkout branch/PR và kiểm tra import Unity: 20 PPU, Point filter, mipmap tắt, pivot chính xác, sprite slicing và animation reference hợp lệ.
6. Sau khi PR merge, OpenCode chỉ cập nhật prefab/scene để trỏ sang `assetId` đã merge. Không copy file qua chat, zip riêng hay ổ đĩa cục bộ.
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
- OpenCode không merge asset PR trước khi kiểm tra Unity import; Muse không merge thay đổi C#; Qoder không merge thay đổi client/art.
- Ba issue điều phối ban đầu: Muse #1, OpenCode #2, Qoder #3. Agent phải liên kết PR về issue tương ứng.

## Khôi phục khi asset PR bị lỗi

Revert PR trên GitHub bằng PR mới; không force push `main`. Muse tạo PR hotfix với asset pack version mới và manifest ghi asset bị thay thế.
