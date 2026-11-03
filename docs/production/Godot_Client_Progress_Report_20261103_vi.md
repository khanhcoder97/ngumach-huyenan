# Muse — Báo cáo thay đổi engine sang Godot .NET và tiến độ sản xuất

Ngày báo cáo 2026-11-03, Asia/Tokyo. Người gửi: Muse (phụ trách pixel art và client runtime). Người nhận: Codex (phụ trách tài liệu production, tích hợp client và review). Chủ dự án (Spu) là người ra quyết định được trích dẫn trong báo cáo này.

**Tóm tắt cho người bận:** Chủ dự án đã chốt **bỏ Unity** từ 2026-10-31 — client chính thức duy nhất là **Godot .NET 4.7.2 (C#)** và đã chạy thật, kiểm chứng end-to-end trên máy của Muse. Tài liệu production hiện vẫn khóa Unity trong văn bản; dự thảo sửa đổi **DEC-024** đã soạn xong ở phía Muse và chờ chủ dự án duyệt văn bản trước khi mở PR sửa tài liệu. Về sản xuất: chương trình làm lại chuẩn 64×64/8 hướng đã qua ART_REVIEW gần hết (4/5 class đã đóng, quái + boss vừa xử lý xong các lỗi lớn nhất ngày 2026-11-03), toàn bộ vẫn là DRAFT ở workspace của Muse, chưa vào repo.

## 1. Thay đổi engine — cần Codex ghi nhận

### 1.1 Quyết định

- **Quyết định của chủ dự án, 2026-10-31 16:09 JST: KHÔNG dùng Unity nữa.** Godot .NET là client chính thức duy nhất của Ngũ Mạch — Huyền Ấn. Quyết định này thay thế cả phương án chạy song song đã cân nhắc cùng ngày.
- **Phiên bản khóa: Godot 4.7.2 stable mono** (.NET 8, C#). Bản 4.8 đang beta và đòi .NET 10 nên bị loại khỏi xét duyệt.
- Lý do gốc: máy của chủ dự án không chạy được Unity; Godot không cần tài khoản/giấy phép, tải và chạy được qua hạ tầng hiện có, và đã được Muse kiểm chứng trực tiếp trên dự án thật (mục 1.2).

### 1.2 Bằng chứng kiểm chứng (thực hiện 2026-10-31 trên client thật)

- Import ấm + `dotnet build` **0 lỗi** trên Godot 4.7.2 mono (các gói Godot.NET.Sdk/GodotSharp 4.7.2 được đưa vào local feed vì môi trường build ngoại tuyến một phần).
- **Toàn bộ battery kiểm thử 10/10 PASS**, gồm 2 suite online đấu với server P1 thật của Qoder.
- **Export Linux thành công** bằng export templates mono 4.7.2; bản build chạy lại self-test và full-map test đều PASS. Cross-export Windows thành công (chưa run-test trên máy Windows thật). Android: xem mục 2.4.
- Lưu ý vận hành đã ghi nhận: các suite đọc lại texture **đứng treo nếu cache import lạnh** — luôn chạy một lượt `--import` làm ấm trước khi test trên bản sao mới; bản ấm chạy qua trong khoảng 1,5 giây.

### 1.3 Hệ quả phân vai và các PR cũ

- Muse phụ trách luôn **client runtime Godot** trên VM của mình, bên cạnh pixel art. Dòng phân vai "Unity proof khi có máy phù hợp" trong bàn giao Bến Mưa ngày 2026-10-30 không còn áp dụng.
- **PR #22 và PR #51** (bản draft client Unity) giữ nguyên trạng làm **tham chiếu lịch sử**, không phát triển tiếp. Đóng hay giữ mở là quyết định riêng của chủ dự án (điểm mở §6.2 của dự thảo DEC-024, mục 1.4).
- Mục tiêu BM-D (tích hợp map vào client) đã đạt bằng Godot — client Godot đã chạy toàn bộ map Bến Mưa production — nên việc hủy tuyến tích hợp Unity không làm mất phần việc nào.

### 1.4 Trạng thái tài liệu production và dự thảo DEC-024

- Văn bản production hiện hành vẫn khóa Unity: **64 dòng chứa từ "Unity" trên 26 file** trong `docs/` (69 lượt xuất hiện), gồm 13 file chuẩn (normative) cần sửa câu chữ.
- Muse đã soạn **dự thảo DEC-024** đầy đủ theo lệnh chủ dự án 2026-10-31: văn bản quyết định đề xuất (Godot 4.7.2 .NET là client chính thức; ánh xạ 20 px = 1 WU, Point filter, không mipmap, TileMapLayer, AnimatedSprite2D/AnimationPlayer, lật Y theo công thức py = (36 − y) · 20; Unity và PR #22/#51 là tham chiếu lịch sử; BM-D chuyển đích sang Godot), bảng sửa từng dòng cho 13 file chuẩn, danh sách file chỉ chú thích và file giữ nguyên như lịch sử. Kiểm tra tính áp dụng của dự thảo trên `main` hiện tại: đối chiếu 29/29 điểm vẫn khớp.
- `Production_Technical_Contracts_vi.md` **không chứa khóa engine** — phần server/contracts không bị ảnh hưởng bởi DEC-024.
- Báo cáo này **không tự áp dụng** dự thảo. Quy trình đã thống nhất: chủ dự án duyệt văn bản → Muse áp sửa đổi text-only trên branch `muse/engine-dec-024` → mở PR để **Codex review** (đặc biệt dòng phân vai trong `Development_Execution_Board_vi.md` cần Codex xác nhận phần của mình) → chỉ merge khi chủ dự án duyệt.

## 2. Trạng thái client Godot (đã chạy thật)

Client nằm tại workspace của Muse (chưa vào repo — việc đưa client vào repo cần quyết định riêng của chủ dự án).

### 2.1 Map và di chuyển

- Chạy **toàn bộ map Bến Mưa production**: lưới 450×60 = **27.000 ô** (nước 4.960, blocked 5.069), cả 5 seam khớp tuyệt đối, cổng Đông (neo 348) thông, đấu trường thông. Lớp detail round-13 được tách theo lưới blocked thành lớp dưới (z=5) và lớp trên (z=15) quanh player (z=10); hình học/collision/tiledata không đổi.

### 2.2 Online server-authoritative (đấu với server P1 của Qoder)

- Luồng session → snapshot → move intent 5 Hz → render bám snapshot (snap khi lệch > 2 WU) chạy thật; HUD hiển thị session, tọa độ, revision, tick, RTT.
- Client tự clamp intent tại thời điểm thực thi: bước tối đa 1,5 WU, hộp chân 24×12 px, thử toàn phần → chỉ X → chỉ Y (trượt tường), không gửi intent khi bị chặn hẳn. Suite online mở rộng **13/13 PASS** (dừng ở mép nước phía Nam, clamp kích hoạt đúng, trượt SE, 0 vi phạm/0 reject).
- **Lưu ý phạm vi cho Codex:** server P1 của Qoder hiện **hard-code `CLASS_MINH_KIEM`** và trả lỗi 400 cho bốn class còn lại. Đây là phạm vi P1 phía server, **không phải lỗi client**; client không cần thay đổi gì khi phía server mở thêm class. Collision tile phía server vẫn thuộc Qoder; lớp blocked phía client đã sẵn sàng.

### 2.3 HUD board-06 và chọn class

- HUD board-06 đã chạy trong scene online: HP/MP fill động, cooldown sweep động theo thời gian thực, joystick hoạt động, minimap thật, panel quest + pips, portrait theo class, nút BAG, nhịp tấn công, badge, API thanh EXP. Kiểm toán hình học so với layout board-06: 31/31 đạt; HudTest 15/15 PASS.
- **Phát hiện HUD — một đã sửa, một còn treo:**
  1. Thanh EXP: **ĐÃ SỬA xong ngày 2026-11-03 theo cách B** (khoét 32.158 px vàng đặc ở ruột `exp_bar.png` thành máng tối, đảo thứ tự vẽ trong `BuildExp` để fill nằm trên khung) — đã kiểm chứng bằng ảnh chụp trong game ở tỉ lệ 35% và battery kiểm thử đầy đủ 10/10 PASS. Phiên bản báo cáo ban đầu ghi mục này là "chưa sửa" — đính chính tại đây.
  2. `Main.tscn` **chưa gắn HUD board-06** — scene chính hiện chỉ có một nhãn trạng thái kết nối; HUD đầy đủ mới có trong scene test online. Việc này vẫn chờ phán quyết riêng của chủ dự án.
- Chọn class chạy thật ngay trong menu: 5 thẻ class, chọn bằng click hoặc phím 1–5, portrait đầu nhân vật theo class. Thư viện clip của cả 5 class đã port sang client (bảng clip 48×64 của tuyến cũ).
- Khuyết duy nhất còn lại của HUD: **font pixel tiếng Việt** — client đang dùng font mặc định của engine, Muse không tự chế font.

### 2.4 Android — toolchain xong, chặn ở hạ tầng máy chủ

- Đã lắp và kiểm chứng từng bước: JDK 17, Android SDK (platform 35, build-tools 35), templates Android của Godot 4.7.2, preset arm64, và bản publish .NET self-contained cho android-arm64 **PASS** (197 file).
- **Điểm chặn:** tiến trình Gradle chết lặng trong mọi lần build — nguyên nhân đo được là giới hạn commit bộ nhớ toàn máy chủ (~4,0 GB) trong khi các tiến trình nền đã chiếm ~3,4–3,8 GB. Không sửa được từ bên trong máy ảo này; APK cần một máy có ≥ 4 GB commit trống (máy của chủ dự án hoặc CI) dùng lại đúng bộ toolchain đã kiểm chứng.
- **Đường thoát đã viết sẵn:** pipeline GitHub Actions (build trên ubuntu-24.04, đúng các phiên bản trên, tự kiểm chứng APK trong job và tải lên artifact) đã sẵn sàng ở workspace của Muse, **chưa từng chạy** — cần quyết định đưa client vào repo dưới `.github/workflows/` và bấm Run thủ công.

### 2.5 Việc chưa làm phía client

- Lớp nhân vật **64×64 mới chưa migrate vào engine**: `DirectionalAnimator2D` hiện khóa ô 48×64, số frame cố định theo action, nạp file `attack1.png` trong khi bộ mới dùng `attack.png` và có thêm dash. Migration chỉ thực hiện **sau khi ART_REVIEW chốt**, kèm quyết định khóa số frame thật theo từng hàng làm chuẩn engine (số frame thật thường thấp hơn mục tiêu danh nghĩa; các ô thừa để trong suốt, engine phải lặp theo số frame thật của từng hàng).
- Run-test bản export Windows trên máy thật (mục tùy chọn, chưa thực hiện).

## 3. Tiến độ sản xuất art — chuẩn mới 64×64, 8 hướng

Chuẩn thực thi đang khóa: ô 64×64 cho nhân vật (quái giữ ô riêng theo loài, boss đầu 128×128), 8 hàng theo thứ tự N, NE, E, SE, S, SW, W, NW; **hướng chéo sinh riêng, không lật gương** cho nhân vật; FPS là ước số sạch của 60. Board PR #38 chỉ là tham chiếu thiết kế + màu, không bao giờ cắt/xén thành asset; canon và quyết định đã khóa thắng lỗi trên board.

### 3.1 Năm class — tổng 2.655 ô, ART_REVIEW đã đóng 4/5

| Class | Ô | Trạng thái ART_REVIEW |
|---|---|---|
| Minh Kiếm | 558 | **ĐÃ ĐÓNG** 2026-11-01, bổ sung code-fix 2026-11-03 (mục dưới) |
| Ảnh Đao | 549 | **ĐÃ ĐÓNG** 2026-11-01 (chỉ sinh lại attack W theo phán quyết) |
| Huyền Bút | 524 | **ĐÃ ĐÓNG** 2026-11-03 |
| Thạch Chùy | 528 | **ĐÃ ĐÓNG** 2026-11-03 |
| Linh Cung | 496 | Đã hết lỗi đã ghi; chủ dự án **chưa chốt đóng** (xét sau khối quái/boss) |

- Bài học đã kiểm chứng bằng số liệu và đang áp dụng: với các lỗi màu cục bộ trên nhân vật đã khóa, **code-fix hẹp trên sheet hiện có thắng sinh lại** — 4 vòng sinh lại Minh Kiếm chỉ cứu được 1 hàng. Các code-fix đã áp dụng đều có dùng thử trên bản sao, kiểm chứng mặt nạ-diff theo pixel, sao lưu bản gốc và kiểm toán lại: dải đen sau đầu ở hàng dash E của Minh Kiếm (vi phạm thật điều "bỏ khăn trán" của DEC-015; 190 px), mực xanh → mực đen và áo đảo màu ở attack của Huyền Bút (417 + 573 px, kèm cắt 2 ô mảnh ở dash), màu plume đỏ/vàng/cam → xanh đậm khóa và râu nâu → sẫm ở Thạch Chùy (tổng ~7.264 px), cùng các đợt cắt ô mảnh và cứu phân đoạn attack của Linh Cung (hàng attack E/SW bị xé vụn do dây cung nối ngang — đã neo phân đoạn bằng `seg_overrides`, strip gốc vốn nguyên vẹn).
- Các hàng bị công cụ sinh ảnh từ chối nội dung (một số strip dash của Minh Kiếm, attack của Huyền Bút) đã **dừng cứng** theo quy tắc: không thử lại dưới bất kỳ dạng nào nếu chủ dự án không ra phán quyết mới.

### 3.2 Quái Bến Mưa và boss Mãng Cốt — cập nhật 2026-11-03

- Quái: 46 sheet, **3.952 ô** (Cá Linh, Rễ Nước, Shore Stalker + biến thể elite bằng remap palette). Boss Mãng Cốt: 8 sheet, **520 ô**. Kiểm toán pixel toàn bộ: kích thước đúng 46/46 + 8/8, magenta khóa 0, không trùng chéo hàng, hàng gương khớp tuyệt đối.
- Theo phán quyết ART_REVIEW ngày 2026-11-03:
  - **Vá lỗi offset trong script suy diễn clip break của boss**: hai hàm cắt lát dán phần thân dưới sai vị trí cắt khiến từ frame 3 cổ bị kéo lên ~42 px (hiện tượng "nhảy pivot, mất cổ" đã báo cáo trước đây). Sau vá: khoảng hở đáy = **0 trên cả 96 ô**; hit/dive/emerge tái sinh byte-identical. Kết luận: đây là **bug code, không phải khiếm khuyết thiết kế** — phán quyết 3 lựa chọn từng treo cho mục này được khép lại.
  - **Sinh lại Stalker walk NE**: hàng cũ quay mặt trước thay vì lưng — hàng mới là lưng thật ở mọi frame (đánh đổi đã ghi manifest: dáng hơi dựng, bờm vàng đậm).
  - **Sinh lại Rễ Nước telegraph E**: hàng cũ nhảy hình thể ở frame 6/7 — hàng mới thống nhất một silhouette cả 12 frame (còn vết seam sáng giữa hai nửa strip, cùng họ lỗi đã ghi ở các hàng khác của chính quái này).
- Các hàng bị từ chối sinh vĩnh viễn giữ nguyên dạng pool/suy diễn theo lệnh đứng: Cá Linh walk E, Cá Linh telegraph E, Stalker telegraph S, Stalker hide SE, Stalker lunge S/SE/E.
- **ART-P1-013** (đòn tấn công thứ ba của boss) vẫn **BLOCKED chờ duyệt thiết kế** — không sản xuất.

### 3.3 Map Bến Mưa, NPC, VFX, thuyền

- **Map Bến Mưa**: gói detail style-2 cho toàn map (7200×960) đã hoàn thành ở workspace với mật độ chi tiết kiểu tham chiếu đã duyệt; tiledata không đổi (27.000 ô / nước 4.960 / blocked 5.069), cổng Đông thông 4,2 WU, mọi neo khóa giữ nguyên. Gói này là **DRAFT chờ ART_REVIEW và giữ local** theo quyết định của chủ dự án — chưa push. Runtime Godot hiện vẫn chạy lớp detail round-13 (v1); chuyển sang style-2 chỉ làm sau khi style-2 qua duyệt.
- **Câu hỏi mở cho vòng duyệt map**: 306 ô nước hở + 37 ô bờ đang **đi được** trong collision của client (chỉ lớp blocked mới chặn), mọi ô đều tới được từ spawn theo mô hình hộp chân thật; dải hở bắt đầu đúng biên strip X = 64 WU trong khi strip phía Tây chặn hoàn toàn — nghiêng về giả thuyết "quên đặt blocked". Cần phán quyết: chặn cả 306 ô như sửa bug, hay giữ làm lối lội nước/thuyền được tài liệu hóa. **Chưa ô nào bị sửa.**
- **NPC Bến Mưa** (Ly An, Tạ Văn Khánh, Hạ Mặc, Fisher, Medic, BoatKeeper): bộ walk + idle hoàn chỉnh dạng draft, chờ ART_REVIEW (đến lượt sau quái/boss). Ghi nhận kiểm toán: các hàng Tây là gương tuyệt đối ở mức mặt nạ alpha; walk N của Hạ Mặc và walk S của Tạ Văn Khánh gần như tĩnh.
- **VFX kỹ năng: 30/30 sheet** (240 frame) hoàn chỉnh dạng draft, kiểm toán độc lập PASS, chờ ART_REVIEW ở cuối hàng đợi; bốn sheet có bước nhảy tâm lớn đã đo và ghi sẵn cho vòng duyệt (nặng nhất SK-TC-05: 153,5 px tại frame 6→7).
- **Thuyền top-down**: 3 biến thể (chèo 120×40, hàng 120×35, mui 120×29) + thuyền buồm 220×75, draft chờ duyệt; kích thước buồm 220 hay 240 và chuẩn bề rộng thân thuyền chưa chốt. Bộ NPC placeholder từ gói asset ngoài chỉ dùng trong prototype Godot, có README cấm đưa lên production.

## 4. Việc cần phía Codex và chủ dự án

1. **Codex ghi nhận thay đổi engine** (mục 1) và chuẩn bị phía tài liệu theo dự thảo DEC-024; khi chủ dự án duyệt văn bản, Muse mở PR text-only để Codex review.
2. **Ba điểm mở còn lại của DEC-024 §6** (chủ dự án chốt): (a) PR #22/#51 đóng kèm ghi chú hay giữ mở; (b) thư mục `Client/` Unity trong repo giữ làm lịch sử hay lên kế hoạch dọn sau khi project Godot vào repo; (c) đường dẫn delivery cinema chốt ngay hay để khi CINEMA-01 khởi động.
3. **Font pixel tiếng Việt** cho HUD (mục 2.3) — cần nguồn font hoặc quyết định phạm vi phía nội dung.
4. **Phán quyết 306 ô nước** (mục 3.3) và các điểm mở MIG-01..08 của gói map, tại vòng duyệt map của ART_REVIEW.
5. Thứ tự ART_REVIEW còn lại (chủ dự án điều phối): Linh Cung chốt đóng → NPC → map style-2 + thuyền → VFX 30 → tổng kết khóa số frame thật theo hàng làm chuẩn engine cho migration 64px.

## 5. Ranh giới không thay đổi

- Server, contracts, schemas thuộc **Qoder** — Muse không sửa. Tài liệu production chỉ sửa khi chủ dự án ra lệnh trực tiếp (quy trình DEC-024 ở mục 1.4 là ví dụ đang chạy).
- Mọi asset nêu trong báo cáo này là **DRAFT tại workspace của Muse**, chưa phải hàng repo; chỉ những gì chủ dự án duyệt trong chat mới được đẩy lên repo. Báo cáo này là file duy nhất trong lần gửi này.
