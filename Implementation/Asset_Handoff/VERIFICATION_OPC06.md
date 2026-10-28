# OPC-06 Verification (draft)

Ngày: 2026-10-29  
Người xác minh: OpenCode

## Phạm vi

Draft manifest v2 cho OPC-06, tách khỏi PR coverage #31:

- `asset_delivery_manifest.v2.schema.json` — schema v2 draft
- `manifest_geometry.py` — rule layout/hướng/clip range
- `migrate_manifest_v2.py` — dry-run migration, diff, output ra file mới
- `validate_asset_delivery.py` — tự chọn schema v1/v2 theo `manifestVersion`
- `fixtures/manifest_v2/` — fixture hợp lệ và fail
- `tests/test_manifest_v2.py` — test v2 + migration
- `OPC-06_manifest_v2_proposal.md` — proposal sửa số liệu #33
- README + workflow cập nhật cho v2

Manifest Muse `Client/Assets/ArtManifests/muse_delivery_manifest.json` **không bị sửa**.

## Kết quả local

```text
$ python -m unittest discover -s Implementation/Asset_Handoff/tests
Ran 97 tests
OK

$ python Implementation/Asset_Handoff/validate_asset_delivery.py
SUMMARY assetPackId=p1_minh_kiem_walk version=v0.1.0 assets=1 errors=0 warnings=0
OK: Client/Assets/ArtManifests/muse_delivery_manifest.json passed asset handoff validation

$ python Implementation/Asset_Handoff/migrate_manifest_v2.py --quiet
(exit 0, source manifest unchanged)

$ python Implementation/Asset_Handoff/migrate_manifest_v2.py --show-json
manifestVersion: 2
frameSize: {width: 48, height: 64}
framesPerDirection: 6
```

Bốn fixture v2 hợp lệ pass qua CLI với `--skip-file-checks`; fixture
`invalid_grid_mismatch.json` fail đúng field `frameSize` với lỗi
`pixelWidth 288 is not divisible by frameSize.width 40`.

## Chưa xác minh

- CI Linux của PR này: cập nhật sau khi workflow chạy.
- Unity playback/FPS thực: unverified (không có Unity).
- PNG chunk/CRC, alpha, `.meta` import: thuộc OPC-07.
- Manifest Muse chưa chuyển sang v2; chờ review proposal #33.
