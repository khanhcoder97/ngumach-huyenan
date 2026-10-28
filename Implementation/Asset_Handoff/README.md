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

## Coverage audit (OPC-05b)

`coverage_audit.py` sinh báo cáo coverage từ nguồn thật (catalogue CSV, definition
examples, delivery manifest, PNG header và `.meta`), chỉ dùng standard library:

```powershell
python Implementation/Asset_Handoff/coverage_audit.py
python Implementation/Asset_Handoff/coverage_audit.py --check
```

Kết quả ghi vào `COVERAGE_REPORT.md` và `coverage_report.json` (cùng thư mục). Script:

* đếm ID thật từ `docs/production/*.csv` và parse 30 active skill ID từ combat spec;
* phân loại 9 definition example canonical và tách fixture `MapTopology` synthetic;
* suy ra frame size từ manifest (`pixelWidth / frames`, `pixelHeight / directions`) và đối
  chiếu với cell 48×64 đã khóa;
* đọc `.meta` tĩnh để kiểm PPU, filter, mipmap, compression, pivot, tên/rect lưới sprite —
  **không cần Unity**;
* ghi SHA256 từng file evidence và `sourceCommit` của lần thay đổi nguồn gần nhất. File text
  được hash ở dạng LF chuẩn hoá để Windows/Linux cho cùng report; PNG giữ byte gốc.

`--check` trả exit code 1 khi report đã commit không còn khớp nguồn. Engine playback vẫn là
**unverified**; audit chỉ xác nhận metadata tĩnh và header PNG.

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
* Không kiểm chứng Unity engine playback (import runtime, animation chạy, pixel snap). File
  `.meta` được `coverage_audit.py` kiểm **tĩnh** bằng Python (PPU, Point filter, mipmap,
  pivot, rect lưới) nhưng engine import/playback vẫn ghi nhận là **unverified**.
* Schema giao nhận chưa có `frameWidth`/`frameHeight`, nên validator chỉ cảnh báo (WARN) khi
  `frames x directions` không chia hết kích thước sheet, không coi đó là lỗi. Đã mở integration
  issue đề nghị bổ sung metadata frame size vào schema.
* `tileSize`, `pivot` chỉ là chuỗi tự do theo schema hiện tại; validator chưa đối chiếu với
  kích thước tile thực tế.
