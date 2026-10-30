# Bến Mưa — generated candidates, runtime OFF

- `candidates.json`:21records/56unresolved trong snapshot đầu tiên; gồm P00-01..05 và objective maps, actor/3mobs/boss/item references. Field provenance/digests/activation gates nằm trong JSON.
- `muse_map_candidate.json`: **synthetic importer fixture**, giữ original349record count và24placements Bến Mưa, so1actor Muse thật. Không là full Bến Mưa map hoặc nav data được phê duyệt.

Không sửa generated JSON bằng tay. Build/check từ ContentPipeline và MuseMapAdapter; xem README của từng tool để biết schema, limits và source lock. Hai file đều `runtimeActivationAllowed=false` và cần review/migration consumer riêng.

Một lệnh nghiệm thu toàn tooling, gồm browser thật:

```sh
python Tools/AssetPack/run_all_checks.py --include-candidates --include-browser
```

Không có Chrome/Edge thì bỏ `--include-browser` để kiểm headless Python, nhưng lượt đó phải ghi browser UNVERIFIED. Unity/type/import/device/P1-online vẫn là gates khác.
