# OPC-06 — Manifest v2: frame geometry và hướng (draft)

Trạng thái: **draft để review**, chưa áp dụng cho manifest Muse. Theo dõi tại issue
#33 (schema proposal) và issue #40 (gói OPC-06 → OPC-10).

Tài liệu này thay thế phần số liệu và công thức trong proposal cũ ở #33. Các con số
đúng của walk sheet hiện có:

| Thuộc tính | Giá trị |
|---|---|
| Kích thước sheet | 288 × 512 px |
| Frame mỗi hướng | 6 |
| Số hướng | 8 |
| Frame size | 48 × 64 px |
| FPS | 8 |
| Layout | `direction_rows` (8 hàng hướng, 6 cột frame) |

Công thức cũ `288 / (8 × 4) = 12` và `512 / 4 = 128` là sai vì nó vừa nhân số
hướng vào trục ngang vừa đoán số hàng. Công thức đúng cho `direction_rows`:

```
frameWidth      = pixelWidth  / framesPerDirection   = 288 / 6 = 48
frameHeight     = pixelHeight / directionCount       = 512 / 8 = 64
sheetWidth      = frameWidth  × framesPerDirection   = 48 × 6 = 288
sheetHeight     = frameHeight × directionCount       = 64 × 8 = 512
```

Không nhân `directionCount` vào cả width lẫn height. Mỗi hàng là một hướng, mỗi cột
là một frame trong hướng đó.

## 1. Versioning

| `manifestVersion` | Ý nghĩa | Schema |
|---|---|---|
| vắng mặt | legacy v1 (manifest Muse hiện tại) | `asset_delivery_manifest.schema.json` |
| `1` | legacy v1 tường minh | `asset_delivery_manifest.schema.json` |
| `2` | OPC-06 v2 draft | `asset_delivery_manifest.v2.schema.json` |
| khác | lỗi unsupported, không fallback | — |

- Manifest legacy tiếp tục đọc và pass như trước; không rewrite manifest Muse trong PR
  tooling này.
- v2 **bắt buộc** `manifestVersion: 2`; không có chế độ "tự nhận là v2".
- v2 sheet phải khai báo `isDirectional` tường minh. Không ngầm mặc định sheet mới là
  không hướng, cũng không ngầm mặc định là 8 hướng.
- Field v2 không được xuất hiện trong manifest v1: schema v1 đóng
  (`additionalProperties: false`), nên `frameSize`/`layout`/`isDirectional` trong v1 bị
  từ chối thay vì bị bỏ qua.

`manifestVersion: true` (JSON boolean) bị coi là unsupported, không được so sánh bằng
`1`.

## 2. Layout được hỗ trợ

### 2.1 `direction_rows`

Dùng cho actor 8 hướng. Điều kiện:

- `pixelHeight = frameSize.height × directionCount`.
- `pixelWidth = frameSize.width × framesPerDirection` cho clip bắt đầu ở cột 0; với
  nhiều clip, `pixelWidth` phải chia hết cho `frameSize.width` và mỗi clip khai báo
  `framesPerDirection` + `columnStart` (mặc định 0).
- `directions` phải là đúng 8 mã `N, NE, E, SE, S, SW, W, NW` theo thứ tự đã khóa,
  không trùng, không thiếu.
- `framesPerDirection` là số frame của clip trong mỗi hàng hướng.
- Clip range là `[columnStart, columnStart + framesPerDirection)`, phải nằm trong số cột
  thực có và không chồng lên clip khác.
- `frameStart` không hợp lệ trong layout này.

### 2.2 `strip`

Dùng cho VFX một hướng hoặc sheet một hàng. Điều kiện:

- `pixelHeight = frameSize.height` (đúng một hàng).
- `pixelWidth` chia hết cho `frameSize.width`; tổng frame = `pixelWidth / frameSize.width`.
- Animation dùng `frames` hoặc `frameCount`, kèm `frameStart` tùy chọn (mặc định 0).
- Clip range `[frameStart, frameStart + frames)` không được vượt tổng frame và không
  chồng nhau.
- `framesPerDirection` và `columnStart` không hợp lệ trong layout này.
- `isDirectional: true` không được dùng với `strip`; VFX có hướng là unsupported trong
  draft này.

### 2.3 Layout khác

`packed_rects`, grid tự do, sheet nhiều animation không khai báo range, hoặc bất kỳ
layout nào khác đều trả **unsupported**. Validator không suy rect từ số frame, không
cắt hình theo công thức một clip để kiểm toàn sheet. Muốn hỗ trợ phải mở proposal riêng
với frame rect/clip range mô tả tường minh.

## 3. Field v2 theo kind

| Kind | `frameSize`/`layout` | `isDirectional` | `directions` | Animation |
|---|---|---|---|---|
| `sprite_sheet` | bắt buộc | bắt buộc | bắt buộc khi `true`; cấm khi `false` | ≥1, range theo layout |
| `vfx_sheet` | bắt buộc | bắt buộc `false` | cấm | ≥1, `strip` |
| `icon`, `ui_texture`, `sprite`, `tileset`, `tilemap`, `animation` | cấm | chỉ `false`/vắng mặt | cấm | giữ legacy nếu có |

`frameSize` là object `{width, height}`, cả hai là số nguyên ≥ 1. `pixelsPerUnit` vẫn
là hằng 20 như v1. Các field `pivot`, `tileSize` vẫn là chuỗi theo schema hiện tại.

## 4. Migration draft

Công cụ: `Implementation/Asset_Handoff/migrate_manifest_v2.py`. Chỉ đọc nguồn; không bao
giờ ghi đè manifest nguồn.

```powershell
# Dry-run: in unified diff giữa v1 và proposal v2
python Implementation/Asset_Handoff/migrate_manifest_v2.py

# Xem JSON proposal, không ghi file
python Implementation/Asset_Handoff/migrate_manifest_v2.py --show-json

# Chỉ kiểm tra migration có khả thi (CI)
python Implementation/Asset_Handoff/migrate_manifest_v2.py --quiet

# Ghi proposal ra file mới sau review; từ chối nếu file đã tồn tại
python Implementation/Asset_Handoff/migrate_manifest_v2.py --output out/muse_delivery_manifest.v2.json
```

Quy tắc tự động:

- `sprite_sheet`: chỉ migrate khi có đúng 8 hướng chuẩn theo thứ tự và **đúng một**
  animation với frame count rõ ràng. Frame size suy theo công thức ở §1. Nhiều clip,
  hướng thiếu/sai thứ tự, hoặc field lạ trong animation đều bị chặn để người review tự
  khai báo range.
- `vfx_sheet`: không đoán từ frame count. Phải có sẵn `frameSize`, `layout`,
  `isDirectional`; draft chỉ nhận `isDirectional: false` + `layout: strip`.
- Kind khác: chỉ thêm `manifestVersion: 2`; nếu còn `frameSize`/`layout`/`directions`
  hoặc `isDirectional: true` thì chặn.
- Output phải nằm trong `--root`, khác đường dẫn nguồn, và cần `--force` mới ghi đè file
  output cũ.

Kết quả dry-run trên manifest Muse hiện tại (chưa ghi file):

```
manifestVersion: 2
isDirectional: true
layout: direction_rows
frameSize: {width: 48, height: 64}
animations[0].framesPerDirection: 6
```

Manifest Muse **không được chuyển** trong PR này. Muse/Codex review proposal trước, sau
đó mới dùng `--output` để tạo bản v2 và mở PR riêng.

## 5. Fixtures

Nằm trong `Implementation/Asset_Handoff/fixtures/manifest_v2/`; đây là fixture cấu trúc,
không phải catalogue runtime và không được copy vào `Client/Assets/ArtManifests/`.

| File | Mục đích |
|---|---|
| `valid_actor_8dir.json` | actor 288×512, 6 frame × 8 hướng, frame 48×64, 8 FPS |
| `valid_effect_single_direction.json` | VFX strip 96×64, frame 24×64, 4 frame, một hướng (synthetic, PNG chưa giao) |
| `valid_icon_static.json` | icon 32×32, không có frame geometry |
| `valid_multi_animation_ranges.json` | hai clip với `columnStart` tường minh, không overlap |
| `invalid_missing_frame_size.json` | thiếu `frameSize` |
| `invalid_grid_mismatch.json` | frame width 40 không chia hết 288 |
| `invalid_duplicate_direction.json` | hướng trùng |
| `invalid_direction_order.json` | hướng sai thứ tự |
| `invalid_animation_overlap.json` | hai clip chồng range |
| `invalid_unsupported_version.json` | `manifestVersion: 3` |

Fixture VFX/icon dùng `--skip-file-checks` vì chưa có PNG thật; không đưa vào catalogue
runtime và không tuyên bố engine playback đã kiểm chứng.

## 6. Lệnh kiểm tra

Từ thư mục gốc repo:

```powershell
python -m py_compile Implementation/Asset_Handoff/manifest_geometry.py `
  Implementation/Asset_Handoff/validate_asset_delivery.py `
  Implementation/Asset_Handoff/migrate_manifest_v2.py

python -m unittest discover -s Implementation/Asset_Handoff/tests -v

# Legacy vẫn pass
python Implementation/Asset_Handoff/validate_asset_delivery.py

# Fixture v2 hợp lệ
python Implementation/Asset_Handoff/validate_asset_delivery.py `
  --manifest Implementation/Asset_Handoff/fixtures/manifest_v2/valid_actor_8dir.json `
  --skip-file-checks

# Migration dry-run
python Implementation/Asset_Handoff/migrate_manifest_v2.py --quiet
```

CI `.github/workflows/asset-handoff-validation.yml` chạy unit tests, validate toàn bộ
fixture v2 hợp lệ và migration dry-run trên manifest legacy.

## 7. Giới hạn / unverified

- Chỉ `direction_rows` và `strip` được kiểm tra đầy đủ. Layout khác trả unsupported,
  không đoán rect.
- FPS chỉ là metadata; tốc độ playback thực trong Unity vẫn **unverified**.
- Chưa kiểm tra nội dung pixel, alpha, chunk/CRC PNG — thuộc OPC-07.
- Chưa đọc `.meta` Unity, PPU/filter/pivot thực tế — thuộc OPC-07.
- Migration proposal chưa được áp dụng; manifest Muse vẫn là v1 cho đến khi review xong.
- `vfx_sheet` có hướng và sheet nhiều animation không khai báo range là unsupported
  trong draft này, không phải "tự động suy ra".

## 8. Câu hỏi review

1. Đồng ý version marker: vắng mặt/`1` = legacy, `2` = v2, còn lại lỗi?
2. Đồng ý v2 bắt buộc `isDirectional` tường minh cho `sprite_sheet`/`vfx_sheet`?
3. Đồng ý `vfx_sheet` chỉ một hướng + `strip` trong draft này, hướng khác trả
   unsupported?
4. Đồng ý nhiều animation phải có `columnStart`/`frameStart` tường minh, không overlap,
   và không dùng một công thức clip để kiểm toàn sheet?
5. Đồng ý static kinds không mang `frameSize`/`layout`/`directions` trong v2?
6. Đồng ý migration chỉ ghi ra file mới (`--output`), không bao giờ sửa manifest nguồn,
   và chỉ tự migrate sprite_sheet 8 hướng + đúng một animation?
