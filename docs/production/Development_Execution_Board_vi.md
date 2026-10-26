# Bảng điều phối triển khai — Ngũ Mạch: Huyền Ấn

**Trạng thái:** Tiền sản xuất; đã có scaffold/bootstrap và công cụ kiểm định nội dung, chưa có gameplay runtime hoặc asset pixel-art production.  
**Nguồn chuẩn:** `Production_Index_vi.md`, GDD, Decision Register, AI Agent Implementation Plan, Technical Contracts, QA/Release Gates và các đặc tả domain. Khi khác nhau, ghi vấn đề để khóa qua Decision Register; không tự sửa thiết kế trong code.

## 1. Phân vai

| Luồng | Người/agent phụ trách | Phạm vi | Bàn giao bắt buộc |
|---|---|---|---|
| Điều phối / sản xuất | Codex | Giữ nguồn chuẩn và phạm vi phase; lập dependency; theo dõi blockers; rà tích hợp; phụ trách art direction, asset, VFX, animation và nghiệm thu hình ảnh | Cập nhật board, quyết định cần khóa, asset manifest và trạng thái nghiệm thu |
| Code | Codex (tiếp quản phần OpenCode còn dở theo yêu cầu chủ dự án) | Unity client, server C#, schema/API, content importer, gameplay và công cụ theo phase; không tự sửa ý nghĩa record/ID | File thay đổi, module/API/schema, cách chạy local, trạng thái build, dữ liệu đã kiểm tra, TODO/blocker |
| Mỹ thuật / đồ họa | Codex + công cụ tạo asset khi khả dụng | Pixel concept, actor/environment sprite sheets, pixel UI, tilemaps, icon, animation frame table, VFX/weather, budget LowFX/mobile | Tệp nguồn + export, pixel size/atlas/frame table, ID tham chiếu, license/provenance, trạng thái placeholder hay final |
| Chủ dự án | Người dùng | Khóa quyết định sản phẩm có ảnh hưởng lớn; cung cấp quyền/cấu hình công cụ khi cần | Phê duyệt các mục đang ghi `BLOCKED_DESIGN_APPROVAL` hoặc quyết định sản phẩm |

## 2. Thứ tự triển khai

### P0 — Nền dự án (đang thực hiện; chưa qua exit gate)

**Đã bàn giao từ OpenCode:** Unity 6.3 LTS / C# / URP scaffold; title bootstrap; health endpoint correlation ID; 7 definition schemas/examples; manifest/reference validator; 8 P1 transport contracts/examples; README. Codex giữ module boundaries và tiếp tục P0/P1 theo gate, không đổi canonical IDs.

**Codex:** bảo toàn bộ tài liệu nguồn; quản lý asset IDs và P1 queue; khóa visual direction/production settings; chuẩn bị brief cho Bến Mưa. Unity Editor và .NET hiện chưa được phát hiện trong PATH nên nghiệm thu mở project/build cần thực hiện khi runtime có sẵn.

**Exit gate:** máy mới mở project theo README; title hiển thị online/offline từ health endpoint; 7 schema example hợp lệ; importer xác nhận đủ 349 record, ID/reference resolve và map bounds; không chứa endpoint/KPAH cũ.

**Trạng thái hiện tại:** scaffold nền đã có: `Implementation/Tools/validate_content.py`, `Server/Health` (ASP.NET Core `/health` với correlation ID), Unity client skeleton, 7 schema/example definition, 8 P1 transport contracts và README. Các report đã lưu cho thấy manifest 349 hàng, ID/reference, map bounds, schema/example và P1 contracts từng đạt `PASSED`. Codex đã thêm cấu hình Pixel Perfect Camera URP, import preset cho pixel sprites, config URL health, menu tạo URP 2D/startup scene và scene hiệu chuẩn tilemap/placeholder sprite. Các thay đổi mới chưa được Unity import/compile; scene/asset sẽ sinh khi chạy menu trong Unity. Dùng Pixel Perfect Camera tích hợp URP 17.3, không cài package Built-in RP riêng. `TOOL-ROD-01` đã có trong Item_Master. Đã đồng bộ turn-in P00-01 sang `NPC_TA_VAN_KHANH` theo Quest Production Spec, GDD và spawn registry; báo cáo validator có sẵn là trước thay đổi này, cần chạy lại khi tiếp tục kiểm định. Môi trường hiện không có Unity Editor hoặc .NET CLI nên không xác nhận Unity import/build server. Codex tiếp quản toàn bộ phần code còn dở theo yêu cầu chủ dự án.

### P1 — Vertical slice Bến Mưa

**Codex:** tiếp tục triển khai di chuyển/combat authoritative, một nhân vật Minh Kiếm với 3 kỹ năng; một mob, một elite, boss Mãng Cốt; quest chain và trạng thái lưu; túi/trang bị/vật phẩm tối thiểu, teleport; UI responsive; data-driven hooks. Chốt API/event trước khi nối asset; animation không quyết định gameplay.

**Codex (art):** theo `Art_Production_Queue_P1_vi.md`: pixel hero Minh Kiếm; NPC Bến Mưa; mob/elite/Mãng Cốt; environment tile kit/props; mưa; telegraph/VFX của 3 skill + boss; pixel HUD skin và item icons. Asset production phải khớp ID, sprite-set/frame table, atlas, FX budget, LowFX/mobile và các điều kiện đọc telegraph trong Art Bible.

**Trạng thái P1.1:** 8 JSON contract transport-independent tại `Implementation/Contracts/P1/` (envelope, move intent, combat input, world snapshot, combat event, quest state, inventory snapshot, teleport request) kèm example và validator. Report `Implementation/Reports/P1_contract_validation.json` đã đạt `PASSED`; ID skill/map/quest/item/currency/entity/class đều resolve. Chưa implement server/client runtime; chờ hoàn thành P0 và môi trường .NET/Unity để compile.

**Exit gate:** hoàn thành chuỗi từ tạo nhân vật đến cổng Thanh Lạc trên PC/mobile; quest state không mất; reward không nhân đôi; telegraph rõ khi LowFX; UI không che tương tác ở 16:9 và 20:9; toàn bộ ID resolve.

**Blocker thiết kế:** hồ sơ Mãng Cốt đang mô tả hai đòn; điều kiện P1 yêu cầu ba. Đòn quét đuôi tầm thấp chỉ là đề xuất trong art queue, chưa được khóa; chưa làm animation/VFX cuối cho đòn thứ ba trước khi quyết định.

### P2–P6 — Mở rộng

Codex chỉ chuyển phase sau khi gate phase trước được nghiệm thu. Mở rộng lần lượt 5 môn phái/tiến trình; dungeon/raid/economy; guild/party/chat; PvP/season/live ops; bảo mật, moderation, load/release gates. Pixel art mở rộng theo content đã khóa, giữ tỷ lệ tái sử dụng tile/actor sprite set và ngân sách thiết bị.

## 3. Quy ước giao việc và tích hợp

- Mỗi ticket code gắn phase, file nguồn, ID chịu trách nhiệm, tiêu chí nghiệm thu và giới hạn “không tự suy diễn”. OpenCode đọc đặc tả domain tương ứng trước khi sửa module.
- ID trong CSV/manifest là canonical. Display name và thoại đi qua localization keys; code không tạo ID dựa trên tên hiển thị.
- Server quyết định sát thương, loot, tiền, quest completion và item state. Animation/VFX chỉ trình bày event; không quyết định hit hoặc reward.
- Mọi asset production có `asset_id`, entity/map/skill tham chiếu, kích thước/clip, export format, budget, license/provenance, trạng thái và điều kiện duyệt. Placeholder phải được đánh dấu, không được giao nhầm thành final.
- Thay đổi API/schema hoặc cân bằng liên module cần cập nhật contract/version và semantic diff trước khi tích hợp.
- Bàn giao ghi rõ đã compile/import hay chưa; không dùng “đã làm xong” nếu chỉ mới có mockup/placeholder.

## 4. Trạng thái đồ họa hiện tại

- Đã có Art Bible và queue 21 hạng mục cho P1 Bến Mưa; queue là kế hoạch sản xuất, không phải asset đã tạo.
- Ngày 2026-10-26 chủ dự án đổi toàn bộ hướng đồ họa sang pixel art. Chuẩn hiện hành: `Pixel_Art_Production_Standard_vi.md`; GDD, Art Bible, queue, combat, HUD, UI/UX và modal specs đã được chuyển sang logical 640×360, 20 PPU, integer scale và frame-based sprite art.
- Hai concept SVG Minh Kiếm v1/v2 đã chuyển khỏi `Client/Assets` vào `docs/production/Art_Concepts_History/`; chúng là lịch sử vector, không phải pixel art/runtime. Sprite concept pixel mới cần được tạo theo ảnh tham chiếu trước khi `ART-P1-002` qua `CONCEPT_APPROVED`.
- Chưa có sprite sheet, tilemap, VFX hoặc animation pixel-art production. Image generation tích hợp không có trong phiên này; CLI fallback cần được chủ dự án chọn rõ và máy có `OPENAI_API_KEY`. Pixel Perfect Camera URP và sprite import defaults đã được thêm ở scaffold, nhưng còn chờ Unity import/compile và project render configuration để xác nhận end-to-end.
- Ưu tiên asset: pixel concept sheet → actor spritesheets → Bến Mưa tilemap/weather → mob/boss sheets → skill VFX → pixel UI/icons; mọi gói theo ID, palette, pixel size, provenance và nghiệm thu riêng.

## 5. Việc tiếp theo

1. Mở Unity và chạy `Tools/Ngũ Mạch/Initialize Pixel Art Project`, rồi `Create Pixel Art Smoke Scene`; xác nhận camera/import pipeline và cấu hình render URP thực tế.
2. Chạy content/contract validators sau khi thay đổi P00-01; cập nhật report theo dữ liệu hiện hành.
3. Bắt đầu P1 server-authoritative world/combat/persistence từ contract hiện có, sau khi P0 compile được.
4. Thiết kế và đặc tả đòn thứ ba của Mãng Cốt trước animation/VFX final; chọn phương án ít ảnh hưởng combat đã khóa, ghi decision nếu đổi phạm vi.
5. Tạo và duyệt pixel concept pack đầu tiên khi công cụ ảnh khả dụng; sau đó xuất sprite sheets/tilemap theo chuẩn mới và cập nhật queue.
