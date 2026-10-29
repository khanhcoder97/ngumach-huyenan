# Codex review gói asset — 2026-10-30

Đã đọc code và tái hiện bằng Python/HTTP trên immutable heads: PR61 `cf59102fc0600d05266bdf4b44e15a9825c5d711`, PR62 `2613f1be188b305f41ab58e4eb4240ca646db0e5`. Kết quả **1 ca đạt, 9 ca không đạt** acceptance, không merge hai PR trong đợt này. Không sửa checkout/module đang thuộc OpenCode.

Lệnh từ root của worktree này:

```powershell
python Tools/ProducerReview/review_asset_handoff.py --report Implementation/Reports/Producer_Asset_Review_20261030.json
```

Exit1 là kết quả mong đợi của **bản bàn giao đang lỗi**, không phải báo suite đã xanh. Script đọc Git objects đúng SHA, dùng ảnh PNG1×1 và file marker tự tạo trong thư mục tạm; không đọc/phục vụ dữ liệu cá nhân. Không bật server public. Không phải browser/Unity evidence. Nếu clone chưa có commit dùng fetch branch PR trước; script không tự fetch/reset checkout.

## PR61 — cần sửa trước merge

1. **P1: PNG structure chưa kiểm những gì báo cáo hứa.** `validate_png_structure` return sau IHDR, không gọi chunk scan/decompress. PNG CRC IDAT bị sửa, ảnh chỉ có33byte signature+IHDR (không IDAT/IEND) và ảnh cắt giữa IDAT đều accepted. Hàm scan chưa dùng còn XOR CRC và tăng offset thiếu4byte CRC; không chỉ gọi lại là xong. Cần validate chunk bounds/order/CRC/IEND/IDAT và decode-size budget, fixture lỗi đi qua CLI thật.
2. **P1: --root không được truyền tới asset resolver.** Manifest ở root mới đọc được, nhưng asset path vẫn ghép REPO_ROOT module. Ca manifest/PNG/meta hợp lệ ở root tạm kết thúc traceback thay vì pass. Missing/unreadable asset phải thành finding có assetId/path/field, không crash; path confinement theo root.
3. **P1: metadata thiếu hoặc Unity rect đa dòng bị coi như pass.** TextureImporter trống không có lỗi/warning; spriteMode2 chứa rect đa dòng parse0sprite không có finding. Cần required fields, pivot/rect/bounds/duplicate GUID, compression/PPU chính xác theo schema, loại unsupported phải báo rõ. Không cắt `20.5` thành20 bằng regex integer. PNG alpha hiện chỉ báo channel, chưa chứng minh có pixel trong suốt; phân biệt metadata và decoded-alpha evidence.

Giữ PNG indexed colorType3 và tRNS đúng thuật ngữ: type2 là RGB, type4 là grayscale+alpha. Nếu chưa hỗ trợ decode thì báo unsupported, không gọi palette là type2. Nếu .meta thiếu không được báo “all imports validated” hoặc warning-only ngầm tương đương engine-import pass. Các test hiện tại chưa phủ những lỗi này; cần kiểm command-level có fixture âm tính thật.

## PR62 — cần sửa trước merge

1. **P1: giao diện không tải được path mà chính nó gửi.** JS dùng encodeURIComponent cho cả `nested/pixel.png`→`nested%2Fpixel.png`; handler không decode nên literalURL200 nhưng browserURL404. Decode có kiểm soát trước resolve/confinement, kiểm malformed/encoded traversal. Dùng một quy ước URL xuyên UI và server.
2. **P1: manifest thật không resolve được asset.** API lookup `entry.id`, manifest canonical dùng `assetId`, request CHR_MINH_KIEM_WALK trả404. Layout code tự giả `isDirectional/frameSize/framesPerDirection` và8cột×6hàng, trong khi sheet thật288×512 là6cột frame×8hàng hướng. Dùng schema version/geometry đã duyệt; v1 thiếu geometry explicit thì báo unsupported hoặc fallback có nhãn với nguồn kiểm, không bịa grid rồi PASS.
3. **P1: --root không cô lập file được phục vụ.** Khi file không ở root, handler fallback tới CWD; marker tự tạo ngoài configured root vẫn HTTP200. Bỏ fallback, chỉ allowlist ảnh/manifest đã biết trong root sau resolve; kiểm symlink/reparse/drive/UNC và decoded path, không wildcard CORS với arbitrary file endpoint. Đây là lỗi được tái hiện bằng marker, không phải claim đã có khai thác hay lộ dữ liệu thật.
4. **P1: vòng JS chưa hoàn thiện.** `showDirectionsPanel` khai báo hai lần, bản sau bỏ lệnh gắn listener hướng. `selectAnimation` có nhánh directional trống trong interval nên bấm Play cho actor8hướng không chạy frame. Với strip, frame hiện tại còn được vẽ ở vị trí đích dịch theo index thay vì viewport preview cố định. Cần chạy browser thật load→layout→8hướng→frame step/play/pause→zoom/grid, console không lỗi. Đây là source findings, chưa phải kết quả chạy browser; không lấy4test Python layout tự tạo làm bằng chứng UI hoạt động.

## Điều kiện nhận lại

OpenCode tiếp tục gói lớn #40: sửa cả CLI/HTTP/browser contracts, thêm regression tương ứng, giao SHA mới và commands/logs; không sửa Muse manifest/art để hợp thức hóa tool. Bộ reproduction này giữ head lịch sử; khi review mới phải chỉ rõ head và ca đã hết lỗi. Python probes không thay pixel visual review, Unity import, animation coherence hoặc topology review.
