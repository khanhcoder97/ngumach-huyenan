# Muse map sidecar adapter — Codex triển khai OPC-12

Bridge Python stdlib để Muse bàn giao layout/tile/prop/actor metadata và Codex/Qoder đối chiếu tọa độ. Không sửa CSV canonical, Unity assets/meta, nav review status hoặc runtime. Chạy từ repo root:

```sh
python Implementation/Tools/MuseMapAdapter/cli.py build --layout Implementation/Tools/MuseMapAdapter/fixtures/synthetic_layout.json
python Implementation/Tools/MuseMapAdapter/cli.py check --layout Implementation/Tools/MuseMapAdapter/fixtures/synthetic_layout.json
python -m unittest discover -s Implementation/Tools/MuseMapAdapter/tests -v
```

Hỗ trợ `--root`, `--asset-manifest`, `--output`; output mặc định ở BuildCandidates/BEN_MUA. Check là rebuild/byte comparison để phát hiện tamper/drift, không auto-write. Input/paths/images/refs sai exit1 và không ghi output; không được output đè source layout hoặc canonical repo files.

## Hợp đồng Muse cần cung cấp

Xem `schemas/layout_input.schema.json` và fixture JSON. Các object được kiểm schema và semantic/resource bounds:

- `mapId`, `layoutVersion`, `synthetic`, originWu và rowAxis `+Y` hoặc `-Y` rõ; tile16px,20PPU cố định →0.8WU/cell. Origin là góc grid; props bottom-center anchor đặt tại tâm cell `(column+0.5,row+0.5)` theo dấu rowAxis.
- Tilesets có ID/image repo-relative/sourceRef; PNG được decode/CRC/size validation thực, không nhận LFS pointer/truncated/header-only. Atlas phải chia hết16px; tileID1-based,0là ô trống.
- Layers có role GROUND/DECORATION/COLLISION_CANDIDATE, tilesetId,width,height và flat tileIDs row-major. Chung kích thước, tối đa1triệu cells/layer, mỗi chiều≤4096; không biến collision layer thành nav đã review. Map lớn chia chunk/layout riêng có origin/version, không tăng budget tùy tiện để nạp cả kinh thành vào một array.
- Props có stableID/tileset/tileId/cell; output có world anchor và atlas rect top-left.
- `placementOverrides` tham chiếu originalRecordId đúng map, target XY và reason; output luôn giữ originalRecord nguyên row/originalXY/candidateXY, migrationState TOPDOWN_REVIEW_REQUIRED.
- `actorAssets` là IDs từ manifest Muse; adapter dùng geometry resolver cùng preview, kiểm ảnh/PPU/pivot/8directions, xuất rect top-left lẫn Unity bottom-left. Draft art giữ finding, engineImport vẫn UNVERIFIED.

`map_candidate.schema.json` là envelope review-only; adapter thêm kiểm path confinement/duplicate/ref/bounds/PNG/digest và rebuild. Output `runtimeActivationAllowed=false`, `navigationReview=TOPDOWN_REVIEW_REQUIRED` không thể đổi qua input.

## Fixture và giới hạn nghiệm thu

Fixture gồm atlas16×32px do code tạo riêng (hai màu, original test data),2layers4×3 và1prop. **Diện tích3.2×2.4WU chỉ là fixture kiểm importer, không phải thiết kế map Bến Mưa**. Nó đối chiếu1asset Muse thật CHR_MINH_KIEM_WALK288×512/48×64/6columns×8rows; không chứng minh full animation/gear/map art đã giao.

Output giữ đủ349record count và24Bến Mưa records trong source snapshot.24records nằm ngoài fixture nhỏ được ghi OUTSIDE_CANDIDATE_LAYOUT; actor draft có ART_NOT_APPROVED.25findings này là kết quả đúng của fixture, không tự dời NPC/quái cho vừa ảnh nhỏ hoặc hô REVIEWED. Khi Muse giao layout thật phải thay input/ref, review original→candidate migration và chạy nav/gameplay acceptance riêng.

Nguồn CSV/manifest/bounds có SHA text chuẩn UTF8-noBOM/LF; ảnh hash binary. Renderer/engine import vẫn cần consumer adapter, không copy JSON vào runtime rồi coi đã nghiệm thu. Không có template asset/fallback ngoài root hoặc silently skip missing source.
