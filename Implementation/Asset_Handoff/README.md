# Asset handoff validation (OPC-05)

`validate_asset_delivery.py` kiểm tra bundle pixel art mà Muse bàn giao, chỉ bằng Python
standard library. Không cần Unity, .NET hay package bên thứ ba; chạy được trên máy local
và trong GitHub Actions (`.github/workflows/asset-handoff-validation.yml`).

## Chạy local

Từ thư mục gốc repo:

```powershell
# Lần đầu, khi Muse chưa giao manifest: exit 0 kèm thông báo
python Implementation/Asset_Handoff/validate_asset_delivery.py --allow-missing-manifest

# Kiểm tra manifest đã giao (mặc định Client/Assets/ArtManifests/muse_delivery_manifest.json)
python Implementation/Asset_Handoff/validate_asset_delivery.py

# Kiểm tra kèm danh sách file thay đổi của PR (bắt buộc mọi PNG art phải có trong manifest)
git diff --name-only origin/main...HEAD > changed.txt
python Implementation/Asset_Handoff/validate_asset_delivery.py --changed-files changed.txt

# Chỉ kiểm tra cấu trúc + metadata, không đọc file ảnh (dùng cho manifest mẫu)
python Implementation/Asset_Handoff/validate_asset_delivery.py --skip-file-checks `
  --manifest Implementation/Asset_Handoff/muse_delivery_manifest.example.json

# Chạy bộ test
python -m unittest discover -s Implementation/Asset_Handoff/tests -v
```

Tuỳ chọn: `--root PATH`, `--manifest PATH`, `--schema PATH`, `--report FILE`, `-q`.

## Input tối thiểu

Manifest phải khớp `asset_delivery_manifest.schema.json`. Một asset hợp lệ:

```json
{
  "assetId": "CHR_HERO_VANGUARD_IDLE",
  "path": "Client/Assets/Art/Characters/hero_vanguard_idle.png",
  "kind": "sprite_sheet",
  "status": "draft",
  "pixelWidth": 384,
  "pixelHeight": 512,
  "pixelsPerUnit": 20,
  "directions": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
  "animations": [{"name": "idle", "framesPerDirection": 4, "fps": 6, "loop": true}],
  "previewPath": "Client/Assets/Art/Previews/hero_vanguard_idle_preview.png"
}
```

## Ví dụ kết quả

Pass:

```
SUMMARY assetPackId=p1_hero_vanguard version=v0.1.0 assets=1 errors=0 warnings=0
OK: Client/Assets/ArtManifests/muse_delivery_manifest.json passed asset handoff validation
```

Fail (mỗi dòng gồm asset id, file và field):

```
ERROR   [CHR_HERO_VANGUARD_IDLE] file=Client/Assets/Art/Characters/hero_vanguard_idle.png field=pixelWidth :: manifest says 384px but the PNG IHDR says 390px
ERROR   [CHR_HERO_VANGUARD_IDLE] file=Client/Assets/Art/Characters/hero_vanguard_idle.png field=directions :: expected 8 directions, found 7 (missing ['NW'])
WARN    [ICON_HERO_PORTAIT] file=Client/Assets/Art/Icons/Hero_Portrait.png field=path :: file name is not lowercase snake_case (naming convention)
SUMMARY assetPackId=p1_hero_vanguard version=v0.1.0 assets=2 errors=2 warnings=1
FAIL: 2 problem(s) in Client/Assets/ArtManifests/muse_delivery_manifest.json
```

## Exit code

| Code | Ý nghĩa |
|---|---|
| 0 | pass (warning vẫn cho phép) |
| 1 | có lỗi validation |
| 2 | lỗi môi trường/dùng sai: thiếu schema, manifest không tồn tại, JSON hỏng, manifest là LFS pointer |

## Những gì được kiểm tra

1. Cấu trúc manifest theo schema giao nhận (dùng `Implementation/Tools/json_schema.py`).
2. `assetId` và `path` không trùng; không có `..`, không absolute, không backslash, không
   trùng nhau chỉ khác hoa/thường; asset và preview phải là file thật trong repo.
3. Kích thước PNG đọc từ IHDR phải khớp `pixelWidth`/`pixelHeight`; file là Git LFS pointer,
   JPEG, thiếu signature hoặc truncate đều bị từ chối. Preview `.gif` chỉ kiểm tra signature.
4. `pixelsPerUnit` bằng constant trong schema (20), `sourceLicense` = `original`, `owner` =
   `Muse`, asset nằm trong các art root: `Client/Assets/Art`, `Client/Assets/UI/Art`,
   `Client/Assets/Tilemaps`, `Client/Assets/VFX`, `Client/Assets/Animation`.
   `kind = sprite_sheet` phải có đúng 8 hướng theo thứ tự `N, NE, E, SE, S, SW, W, NW`.
5. Mỗi animation cần `name`, frame count (`framesPerDirection`, hoặc `frames`/`frameCount`)
   và `fps` trong khoảng `0 < fps <= 60`. Không yêu cầu mọi animation cùng số frame.
6. Khi truyền `--changed-files`: mọi PNG art bị chạm tới phải xuất hiện trong manifest.

## Giới hạn

* Chỉ đọc header PNG, không giải mã pixel nên không phát hiện ảnh hỏng ở giữa file, không
  kiểm tra palette, alpha hay số màu.
* Không kiểm chứng Unity import (PPU thật, Point filter, mipmap, pivot trong `.meta`) vì
  chưa có máy chạy Unity; engine import được ghi nhận là **unverified**.
* Schema giao nhận chưa có `frameWidth`/`frameHeight`, nên validator chỉ cảnh báo (WARN) khi
  `frames x directions` không chia hết kích thước sheet, không coi đó là lỗi. Đã mở integration
  issue đề nghị bổ sung metadata frame size vào schema.
* `tileSize`, `pivot` chỉ là chuỗi tự do theo schema hiện tại; validator chưa đối chiếu với
  kích thước tile thực tế.
