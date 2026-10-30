# Asset handoff validation (OPC-05, OPC-06 draft)

`validate_asset_delivery.py` kiểm tra bundle pixel art mà Muse bàn giao, chỉ bằng Python
standard library. Không cần Unity, .NET hay package bên thứ ba; chạy được trên máy local
và trong GitHub Actions (`.github/workflows/asset-handoff-validation.yml`).

Từ OPC-06, validator đọc được hai phiên bản manifest:

| `manifestVersion` | Phiên bản | Schema |
|---|---|---|
| vắng mặt hoặc `1` | legacy v1 (manifest Muse hiện tại) | `asset_delivery_manifest.schema.json` |
| `2` | v2 draft, có frame geometry | `asset_delivery_manifest.v2.schema.json` |
| khác | unsupported, exit 1 | — |

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
Nếu không truyền `--schema`, validator tự chọn schema v1/v2 theo `manifestVersion`.

### Manifest v2 draft (OPC-06)

```powershell
# Fixture actor 8 hướng (288×512, 6 frame/hướng, frame 48×64)
python Implementation/Asset_Handoff/validate_asset_delivery.py `
  --manifest Implementation/Asset_Handoff/fixtures/manifest_v2/valid_actor_8dir.json `
  --skip-file-checks

# Migration dry-run: in diff, không sửa manifest nguồn
python Implementation/Asset_Handoff/migrate_manifest_v2.py

# Chỉ kiểm tra migration có khả thi (CI)
python Implementation/Asset_Handoff/migrate_manifest_v2.py --quiet

# Ghi proposal ra file mới sau review (không bao giờ ghi đè nguồn)
python Implementation/Asset_Handoff/migrate_manifest_v2.py --output out/muse_delivery_manifest.v2.json
```

Quy tắc layout v2:

- `direction_rows`: `pixelHeight = frameSize.height × directionCount`;
  `pixelWidth = frameSize.width × framesPerDirection` (clip đầu); nhiều clip phải khai
  báo `columnStart` và không overlap. Đúng 8 hướng theo thứ tự
  `N, NE, E, SE, S, SW, W, NW`.
- `strip`: một hàng, `pixelHeight = frameSize.height`, animation dùng
  `frames`/`frameCount` + `frameStart` tùy chọn, không overlap.
- Layout khác trả unsupported; validator không suy frame rect từ số frame.

Chi tiết và câu hỏi review: `OPC-06_manifest_v2_proposal.md`. Manifest Muse vẫn là v1;
PR tooling này không rewrite manifest của Muse.

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
6. Với manifest v2: kiểm tra `frameSize`, `layout`, `isDirectional`, grid/hướng và clip
   range như mô tả ở trên; sai grid hoặc clip vượt biên là lỗi, không chỉ warning. Với
   manifest legacy v1: `frames x directions` không chia hết sheet vẫn chỉ là WARN để giữ
   tương thích.
7. Khi truyền `--changed-files`: mọi PNG art bị chạm tới phải xuất hiện trong manifest.

## Giới hạn

* `validate_asset_delivery.py` chỉ đọc header PNG, không giải mã pixel nên không phát hiện ảnh
  hỏng ở giữa file, không kiểm tra palette, alpha hay số màu. Dùng `validate_import.py` (OPC-07)
  cho lớp kiểm tra đầy đủ hơn.
* Không kiểm chứng Unity import (PPU thật, Point filter, mipmap, pivot trong `.meta`) vì
  chưa có máy chạy Unity; engine import được ghi nhận là **unverified**.
* Schema giao nhận v1 chưa có `frameWidth`/`frameHeight`, nên với manifest legacy
  validator chỉ cảnh báo (WARN) khi `frames x directions` không chia hết kích thước sheet.
  Manifest v2 (OPC-06 draft) đã có `frameSize`/`layout`/`isDirectional` và kiểm tra grid,
  hướng, clip range ở mức lỗi. Proposal và câu hỏi review nằm trong
  `OPC-06_manifest_v2_proposal.md`.
* Chỉ layout `direction_rows` và `strip` được hỗ trợ trong v2 draft; layout khác trả
  unsupported, không đoán frame rect.
* `tileSize`, `pivot` chỉ là chuỗi tự do theo schema hiện tại; validator chưa đối chiếu với
  kích thước tile thực tế.

## OPC-07 — kiểm tra cấu trúc PNG, alpha thực và `.meta`

`validate_import.py` bổ sung lớp kiểm tra trước khi Unity import. Công cụ chỉ dùng thư viện
chuẩn, không sửa manifest/art và không tuyên bố Unity import đã PASS.

```bash
# Chạy trên manifest thật, giới hạn mọi đường dẫn trong repo root
python Implementation/Asset_Handoff/validate_import.py `
  --manifest Client/Assets/ArtManifests/muse_delivery_manifest.json

# Chạy trên một root khác (fixture/temp checkout) và ghi report trong root đó
python Implementation/Asset_Handoff/validate_import.py `
  --root D:/fixtures/opc07 --manifest manifest.json --report reports/import.txt
```

Kiểm tra gồm:

* Đọc toàn bộ chunk PNG, xác minh CRC trên `type + payload`, thứ tự IHDR/PLTE/tRNS/IDAT/IEND,
  không chấp nhận file truncate, IDAT không liên tục, IEND thiếu, byte thừa sau IEND hoặc chunk
  critical lạ.
* Inflate IDAT có giới hạn 256 MB, xác minh zlib stream kết thúc đúng, kích thước scanline khớp
  IHDR và mọi filter byte thuộc `0..4`.
* Giải mã pixel thật để đếm pixel trong suốt (kể cả `tRNS` cho RGB/grayscale/indexed). Một ảnh
  RGBA nhưng mọi pixel opaque sẽ được báo là **không có bằng chứng alpha**, không chỉ dựa vào
  colour type.
* Đọc `.meta` Unity dạng text: `guid`, `TextureImporter`, `spritePixelsToUnits` (giữ nguyên số
  thập phân), `filterMode`, `enableMipMap`, `textureCompression`, pivot và danh sách sprite.
  Rect inline `{x, y, width, height}` và rect nhiều dòng đều được parse; rect được kiểm tra biên
  theo kích thước PNG thật.
* Báo lỗi trùng `guid` giữa các asset, trùng tên sprite, trùng `spriteID`, pivot ngoài `[0..1]`,
  `spriteMode: 2` nhưng không có sprite, và field bắt buộc bị thiếu.
* `--root` được truyền xuyên suốt; path tuyệt đối, `..`, symlink/reparse thoát root đều bị từ
  chối với finding có cấu trúc thay vì traceback.

Giới hạn: công cụ chỉ kiểm tra **static import metadata**, không chạy Unity. Kết quả PASS ở đây
không phải bằng chứng Unity compile/playback. Asset Muse hiện tại vẫn báo `filterMode=1`
(Bilinear) như một finding thật; không sửa art/manifest để làm validator xanh.

