# QOD-10 — Topology validation report

**Ngày:** 2026-10-28. **Issue:** #32. **Máy chạy:** Windows 10, `Python 3.14.6`, chạy từ repo root `D:\Project\NGUMACHHUYENAN`.
Không có .NET SDK/Unity trên máy; các lệnh dưới đây chỉ chạy Python validator, không phải bằng chứng runtime server.

## 1. Positive checks

```text
$ python Implementation/Tools/validate_topology.py
Bundles: 1 (reviewed=0, synthetic=1)
OK: all 1 topology bundle(s) passed validation.
```

```text
$ python Implementation/Tools/validate_content.py
Definition schemas: 8
  MapTopology: 1 example(s)
OK: all content validation checks passed.
```

```text
$ python Implementation/Tools/validate_contracts.py
Schemas: 10
Examples: 10
OK: all contract validation checks passed.
```

## 2. Negative checks (mỗi case chạy trong thư mục tạm riêng, đã xoá sau khi chạy)

| Case | Thay đổi | Exit | Thông báo thật |
|---|---|---|---|
| bowtie | walkable polygon tự cắt | 1 | `MapTopology/bowtie.json.walkablePolygons[0]: polygon self-intersects` |
| short_polygon | polygon chỉ 2 điểm | 1 | `MapTopology/short_polygon.json.walkablePolygons[0]: needs at least 3 points` |
| dup_floor | lặp `OVERWORLD` trong `floorIds` | 1 | `MapTopology/dup_floor.json: floorIds contains duplicates` |
| bad_record | `recordId=MAN-BM-NOPE` | 1 | `MapTopology/bad_record.json.placements[0]: recordId 'MAN-BM-NOPE' is not in the manifest` |
| bad_bounds | `bounds.xMax=1000` | 1 | `MapTopology/bad_bounds.json: bounds.xMax=1000 does not match registry 360` |
| outside_point | điểm walkable `x=-5` | 1 | `MapTopology/outside_point.json.walkablePolygons[0].points[0] (-5,-10) is outside map bounds` |
| bad_bundle | `bundleVersion=1` | 1 | `MapTopology/bad_bundle.json: bundleVersion 1 is not 2` |

## 3. Ghi chú

- `content-validation` CI chạy thêm `validate_topology.py` sau `validate_content.py`, nên bundle hỏng sẽ fail PR.
- Fixture `SYNTHETIC_TEST_ROOM_MAP_BEN_MUA.json` có `reviewState: SYNTHETIC_TEST_ONLY`, **không** phải layout Bến Mưa canonical; chưa có bundle `REVIEWED` nào.
- Bước 2 (geometry service + LOS enforcement cho quest accept) chưa làm trong PR này; quest accept vẫn feature-flag off và log `DEV STUB`.
- Cần Muse bàn giao layout Bến Mưa đã review trước khi bật enforcement trên môi trường thật.
