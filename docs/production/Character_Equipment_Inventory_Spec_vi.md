# ĐẶC TẢ NHÂN VẬT, TRANG BỊ VÀ TÚI ĐỒ
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Vòng đời nhân vật

Tài khoản giữ tối đa 4 nhân vật theo cấu hình máy chủ. Nhân vật thuộc một môn phái cố định khi tạo; lớp quyết định vũ khí chuyên dụng, bộ kỹ năng và cây 8 node nội tại (hai nhánh × bốn node, cấp mở 20/40/60/80); người chơi có tối đa 2 slot passive đang trang bị. Data effect, cap, prerequisite và giá reset ở `Class_Passive_Production_Data_vi.csv`. Lớp không khóa ngoại hình hay giới tính. Tạo nhân vật gồm chọn tên, lớp, diện mạo, tóm tắt vai trò và xác nhận. Tên dài 3–16 ký tự, chuẩn hóa Unicode, cấm ký tự điều khiển/ký tự vô hình và kiểm tra trùng ở server.

Diện mạo gốc lưu trên nhân vật (`bodyFrame`, `facePreset`, `skinTone`, `hairStyle`, `hairColor`, `faceMark`, `accessoryPreset`); ngoại trang mở khóa dùng `cosmeticUnlockLedger` cấp tài khoản và loadout trang bị ngoại hình riêng theo nhân vật. Vanity không cộng stat, không đổi collision/hitbox/tầm đánh/animation combat. Preview/thay diện mạo, nhuộm, buff, auto-use và NPC service được đặc tả tại `Appearance_Buff_NPC_Service_Overlay_Spec_vi.md`.

**Năm môn phái mới**

| ID | Tên | Ngũ hành | Vai trò thiết kế | Vũ khí | Độ khó |
|---|---|---|---|---|---|
| CLASS_MINH_KIEM | Minh Kiếm | Kim | cận chiến linh hoạt, phản công | kiếm | trung bình |
| CLASS_ANH_DAO | Ảnh Đao | Hỏa | áp sát, dồn sát thương theo Nhiệt | đao | cao |
| CLASS_HUYEN_BUT | Huyền Bút | Thủy | tấn công tầm trung, khiên và hồi nhóm | bút pháp | trung bình |
| CLASS_THACH_CHUY | Thạch Chùy | Thổ | tuyến trước, giảm sát thương, giữ quái thường | chùy | thấp |
| CLASS_LINH_CUNG | Linh Cung | Mộc | tầm xa, đánh dấu, kiểm soát vùng | cung | trung bình |

**Tiến trình cấp:** tối đa cấp 100. Cấp nhân vật tăng HP/MP/chỉ số nền theo data table. Không mở quá 6 ô kỹ năng chủ động; cấp 1/4/8/12/16/30. Kỹ năng bổ sung mở qua nhiệm vụ/lớp; cấp kỹ năng có tối đa 8% damage hoặc giảm 4% cost theo thiết kế. Cấp nghề, thú và danh vọng tách khỏi cấp nhân vật.

### 2. Chỉ số và công thức thiết kế

Mỗi nhân vật có 5 chỉ số phân phối: Sức mạnh, Linh lực, Nhanh nhẹn, Thể chất, Vận khí. Mỗi lớp có hệ số quy đổi riêng nhưng panel hiển thị rõ đóng góp. Sức mạnh tăng công vật lý; Linh lực tăng công phép/MP; Nhanh nhẹn tăng chính xác/né/tốc đánh; Thể chất tăng HP/giáp; Vận khí tăng chí mạng/kháng chí mạng. Thuộc tính dẫn xuất gồm Công vật lý, Công phép, HP, MP, Giáp, Kháng nguyên tố, Chính xác, Né, Chí mạng, Kháng chí mạng, Tốc đánh, Tốc chạy, Hồi phục.

GDD định nghĩa chuẩn công thức cho vertical slice; mọi hằng số chỉnh server-side:

- HP tối đa = HP nền + 28 × cấp + 14 × Thể chất + HP trang bị.
- MP tối đa = MP nền + 12 × cấp + 8 × Linh lực + MP trang bị.
- Công vật lý cơ sở = vũ khí vật lý + 3 × Sức mạnh + Nhanh nhẹn + bonus trang bị.
- Công phép cơ sở = vũ khí phép + 3 × Linh lực + Vận khí + bonus trang bị.
- Sát thương kỹ năng = (Công cơ sở + sát thương cộng cố định) × hệ số kỹ năng × bonus damage × 100/(100 + giáp mục tiêu chuẩn hóa theo cấp). Crit cơ sở ×1,5.
- Giáp giảm damage theo hàm 100/(100+giáp); kháng nguyên tố tính riêng, cap PvE 50%.
- Tỉ lệ trúng = clamp(90% + chính xác − né, 5%, 98%); né không thể thành bất tử. Cap né PvE 25%, PvP 15%, crit PvP 25%.
- Tốc chạy từ trang bị cap +15%; tốc đánh cap +20%; bonus sát thương PvP có stat bucket riêng, không áp nguyên hệ số PvE.

Giá trị trên là baseline để làm vertical slice, mọi hệ số phải lấy từ bảng server versioned. Không dùng “chiến lực” thay cho khả năng sinh tồn, vai trò hoặc item level. Trong UI, tooltip chỉ ra nguồn từng cộng/trừ.

### 3. Trang bị nhân vật

**12 slot người chơi**

| Slot | ID | Nhóm chỉ số thường gặp | Ngoại hình |
|---|---|---|---|
| Nón | EQUIP_HAT | giáp, HP, kháng | tùy chọn ẩn nón |
| Áo | EQUIP_CHEST | giáp, HP, thuộc tính | thân trên |
| Quần | EQUIP_LEGS | giáp, thể chất | thân dưới |
| Vũ khí | EQUIP_WEAPON | công, chỉ số lớp, hiệu ứng đòn | thay weapon sprite/anchor set |
| Găng | EQUIP_GLOVES | tốc đánh, chính xác | tay |
| Giày | EQUIP_BOOTS | tốc chạy, né | chân |
| Dây chuyền | EQUIP_NECK | HP/MP, kháng | icon UI |
| Nhẫn trái | EQUIP_RING_L | crit, chính xác | icon UI |
| Nhẫn phải | EQUIP_RING_R | HP/MP/kháng | icon UI |
| Ngọc bội | EQUIP_PENDANT | hiệu ứng tiện ích, kháng | icon UI |
| Phi phong | EQUIP_CLOAK | phòng thủ/thuộc tính | lớp vải sau lưng |
| Ấn hộ mệnh | EQUIP_SEAL | bonus build, socket đặc biệt | hiệu ứng nhỏ ở nhân vật |

Không cho trang bị sai lớp nếu item có restriction class. Trang bị cấp cao hơn level nhân vật bị khóa nút, tooltip ghi level yêu cầu. Đổi đồ không tự bind nếu định nghĩa không-bind; item bị bind khi equip nếu item schema đặt bindOnEquip. Lớp không thể mang hai item có uniqueGroup trùng nhau. 4 slot trang bị thú là mũ, giáp, vòng cổ, yên/đai; không tính vào 12 slot nhân vật.

**Bộ chỉ số gợi ý theo slot:** armor slot có phòng thủ chính + một chỉ số phụ; phụ kiện có hai chỉ số phụ; vũ khí có công nền + 1–2 dòng. Cùng level/rarity, sức mạnh vũ khí giữa lớp lệch tối đa 5%. Bộ có bonus 2/4 món nếu có; chỉ 1 bộ hoạt động, không cho xếp bonus cùng tên từ nhiều nguồn.

### 4. Phẩm chất, cấp đồ, socket và độ bền

| Chất lượng | Viền/icon | Dòng phụ | Socket | Nguồn phổ biến |
|---|---|---:|---:|---|
| Thường | viền xám + hình tròn | 0 | 0 | quái, shop đầu game |
| Tinh | xanh lục + tam giác | 1 | 0 | quest/craft |
| Linh | lam + hình thoi | tối đa 2 | 0–1 | elite/dungeon |
| Huyền | tím + hai vạch | tối đa 3 | 1–2 | boss/raid |
| Cổ Vật | vàng + ấn riêng | tối đa 4 | 0–3 | hoạt động cuối game có giới hạn |

Phẩm chất là độ rộng/độ hiếm của lựa chọn build, không tạo khoảng cách sức mạnh vô hạn. Item level là 1–100; trang bị được giữ dùng được khoảng 5–10 cấp trong campaign. Mỗi món có durability 0–100. Ở 0 độ bền, tổng chỉ số của trang bị giảm 10%, không phá hủy vật phẩm. Độ bền không giảm khi chết. Sửa tại NPC hoặc bằng Bộ Vá Giáp ngoài combat.

Socket nhận ngọc cấp 1–5. Lắp ngọc miễn phí ở hub, tháo bằng phí nhỏ hoặc nguyên liệu; ngọc bị khóa vào item chỉ nếu người chơi xác nhận. Ghép 3 ngọc cùng cấp thành cấp kế tiếp, chắc chắn; rút ngọc luôn trả lại viên. Nâng cấp item tối đa +15: +1–+5 chắc chắn; +6–+10 thất bại không mất cấp hoặc trang bị; +11–+15 cần vật liệu bảo hộ, thất bại không phá trang bị. Mọi xác suất/chi phí hiển thị; không có cơ chế ép mua.

### 5. Định nghĩa item và quy tắc giao dịch

Mỗi item instance gồm:
- itemId (khóa dữ liệu ổn định), instanceId, quantity, level, rarity, ownerAccountId, createdAt;
- binding: NONE, ON_EQUIP, CHARACTER, ACCOUNT, QUEST; boundTo;
- durability, upgradeLevel, sockets[], randomAffixes[], uniqueGroup, sourceId, expiryAt nếu vật phẩm sự kiện;
- flags: protected, equipped, questLocked, tradeable, salvageable, sellable;
- version schema để chuyển đổi khi cập nhật nội dung.

Tên hiển thị, icon, mô tả và localization nằm ở bảng tĩnh theo itemId. Client không được tự tạo item/stat/giá. Mọi giao dịch, nâng cấp, phân giải và chuyển kho được xử lý idempotent trên server; hai yêu cầu đồng thời không thể tiêu cùng item hai lần.

**Binding:** item nhiệm vụ Character/Quest; vật phẩm boss hiếm thường Character; nguyên liệu craft phổ thông tradeable; cosmetic có thể Account-bound. Chợ người chơi chỉ nhận item tradeable, durability trên 0, không có protected flag; phí niêm yết và phí giao dịch hiện trước xác nhận.

### 6. Thiết kế túi đồ và thao tác

Túi nhân vật có 100 ô thường, chia 4 trang 25 ô; stack vật phẩm phổ thông tối đa 99, trang bị không stack. Túi nhiệm vụ là kho riêng 30 ô không chiếm túi thường. Kho cá nhân 120 ô ở hub, mở rộng theo tiến trình/Đồng tối đa 200 ô; có kho bang riêng theo Guild Social Spec. Mở rộng kho là tiện ích theo tiến trình; không tăng sức mạnh trực tiếp.

**Grid và tương tác**
- 5 cột ×5 hàng mỗi trang (25 ô, 4 trang =100 ô), khớp UI_UX và DEC-023; icon 56–72dp tùy màn, nền phẩm chất theo shape/color/icon. Responsive không tăng số slot server.
- Chọn một lần để đọc chi tiết, nhấn lần hai hoặc nút menu để mở hành động; kéo-thả trên PC đổi vị trí/swap.
- Nút so sánh chỉ hiện khi item phù hợp với slot đang trang bị. Tooltip so sánh dùng giá trị đã cộng set/socket/buff; đổi stat theo dấu và số, không chỉ màu.
- Khóa/mở khóa bảo vệ trong túi là thao tác miễn phí, không tiêu vật phẩm. Đây là trạng thái riêng với `protectedFromSalvage`: dùng MAT-LOCK-01 sẽ tiêu một Phù Khóa để đặt chặn phân giải; bỏ chặn cần xác nhận riêng. Mọi phân giải/bán/bỏ vật phẩm hiếm yêu cầu xác nhận; Cổ/Di vật yêu cầu gõ tên món hoặc giữ nút 1s.
- Filter category, class, slot, rarity, bound, lock, min level. Search theo tên và ID hiển thị, không tìm chuỗi kỹ thuật server.
- Sort: loại, level, phẩm chất, mới nhận, số lượng, chỉ số công. Sort không chuyển vật phẩm giữa server slots, chỉ là view.

**Túi đầy:** cảnh báo từ 80/100 ô, nhắc mạnh từ 90/100. Loot thường không nhặt khi đầy; quest key item đi vào kho nhiệm vụ nếu template khai đúng loại và còn chỗ. Turn-in mặc định trả inventory_full, giữ READY_TO_TURN_IN, không tiêu quest item hoặc cấp một phần thưởng; không tự chuyển thưởng vào thư. Overflow mailbox chỉ dùng khi reward policy versioned khai rõ và có atomicity/dedupe theo Completion Addendum §2/DEC-023. Không xóa tự động đồ Huyền/Cổ Vật. Nút dọn túi mở danh sách đề xuất nhưng không thực hiện giao dịch trước khi người chơi chọn.

### 7. Chi tiết panel vật phẩm

Panel phải hiển thị theo thứ tự:
1. Tên, rarity, level yêu cầu, lớp/slot.
2. Stat chính và phụ, cùng dòng giới hạn/cap nếu chạm cap.
3. Ngọc, upgrade, durability và bộ đồ.
4. Binding, khả năng giao dịch, khóa bảo vệ.
5. Lore ngắn tối đa 140 ký tự, nguồn rơi/chế tạo.
6. Hành động hợp lệ: trang bị, dùng, so sánh, khóa, đưa vào kho, chế tạo, phân giải, bán.

Giá bán mặc định thấp và hiện rõ trước xác nhận. Item có ngưỡng giá trị cao hoặc lượng lớn yêu cầu xác nhận thêm. Nút “mặc ngay” không tự tháo item cũ khỏi inventory nếu túi đầy; đổi hai item trong một giao dịch atomic.

### 8. Loot, chế tạo và nâng cấp

Quái có loot table theo level band và loại; người chơi có contribution cá nhân với boss để chống last-hit. Loot quest instanced; loot thường được reserve 5s cho người đánh, sau đó shared nếu trong party. Boss raid chia reward bằng roll chọn vật phẩm hoặc currency token; không dùng random drop duy nhất khiến raid thất bại không có tiến độ.

**Nghề:** khai khoáng, đốn gỗ, hái thuốc, chế tác. Vị trí 35 node cùng ID vật liệu/level nghề/yield nằm trong `World_Spawn_Gathering_Manifest_vi.csv`. Tool nghề dùng slot utility riêng: `TOOL-PICK-01` Cuốc Mạch Khởi Nghề, `TOOL-HATCHET-01` Rìu Đốn Nghề, `TOOL-SICKLE-01` Liềm Hái Dược. Mỗi node có thời gian tương tác 1,2s; bị đánh ngắt. Công thức mở bằng level nghề, quest hoặc khám phá; nguyên liệu và đầu ra hiển thị trước craft. Chế tác hỗ trợ batch tối đa 10, không tiêu tự động nếu nguyên liệu nằm trong bank trừ khi người chơi bật tùy chọn.

**Công thức mẫu** (khớp Content Bible):
- 3 dược thảo + 1 nước sạch → 2 Dược Bến Mưa.
- 3 ngọc cấp 1 + 5 quặng → 1 ngọc cấp 2, chắc chắn.
- 8 quặng + 4 gỗ + 1 linh phách → áo cấp 10 chọn lớp, Thường/Tinh.
- 2 quặng + 1 gỗ → 1 Bộ Vá Giáp.
- 5 MAT-SOUL-02 + 1 MAT-CORE-01 → 1 MAT-RELIC-01 Cổ Linh Phách; giới hạn 3 lần/tuần.
- 6 MAT-ORE-05 + 3 MAT-CLOTH-01 + 2 MAT-RELIC-01 + 1 MAT-CORE-01 → Ấn Hộ Mệnh T5 phẩm chất Tinh theo lớp; cấp 61, nghề Chế tác bậc 5.
- Phù Bảo Hộ MAT-GUARD-01: chất xúc tác dùng cho mỗi lần thử +11..+15; thất bại không phá/giảm cấp.

### 9. Bộ mẫu dữ liệu hiển thị

| Item ID | Tên hiển thị | Mẫu chỉ số |
|---|---|---|
| EQ-MK-WEAPON-T1-R-COMMON | Thường Kiếm Mưa Khởi Minh Kiếm | Minh Kiếm, cấp 1, Công 12, +2 Sức mạnh |
| EQ-AD-WEAPON-T1-R-COMMON | Thường Đao Mưa Khởi Ảnh Đao | Ảnh Đao, cấp 1, Công 12, +2 Nhanh nhẹn |
| EQ-HB-WEAPON-T1-R-COMMON | Thường Bút Mưa Khởi Huyền Bút | Huyền Bút, cấp 1, Công phép 12, +2 Linh lực |
| EQ-TC-WEAPON-T1-R-COMMON | Thường Chùy Mưa Khởi Thạch Chùy | Thạch Chùy, cấp 1, Công 12, +2 Thể chất |
| EQ-LC-WEAPON-T1-R-COMMON | Thường Cung Mưa Khởi Linh Cung | Linh Cung, cấp 1, Công 12, +2 Nhanh nhẹn |
| POT-HP-01 | Dược Bến Mưa | hồi 25% HP, potion shared cooldown 8s |
| GEM-KIM-01 | Ngọc Kim | +1% chính xác, 1 socket |
| MAT-CORE-01 | Lõi Mạch | vật liệu nâng cấp, khóa giao dịch |
| MAT-RELIC-01 | Cổ Linh Phách | nguyên liệu tuần cho Ấn Hộ Mệnh T5, khóa nhân vật |
| MAT-GUARD-01 | Phù Bảo Hộ | chất xúc tác +11..+15, khóa nhân vật |
| MAT-LOCK-01 | Phù Khóa | bảo vệ khỏi phân giải, tiêu hao |

### 10. Bảo vệ người chơi và trường hợp lỗi

- Transaction equip/sell/craft/upgrade có requestId duy nhất; server lưu kết quả trước khi client hiển thị thành công.
- Nếu mất kết nối khi craft: lần đăng nhập lại đọc transaction gần nhất, không trừ nguyên liệu lần hai.
- Hai người mua cùng listing: chỉ một người thắng atomic purchase; người kia nhận thông báo hết hàng.
- Nếu item bị xóa do rollback, gửi thư hệ thống có log transaction; không dùng mailbox như cách mặc định để tạo item.
- Hệ thống cảnh báo vật phẩm đang khóa hoặc đang mặc; batch sell bỏ qua các item đó và báo số lượng bỏ qua.
- Vật phẩm nhiệm vụ có trạng thái hoàn tất riêng, không phụ thuộc item instance trong túi thường.

### 11. Checklist bàn giao

- Data table có schema/version, ID ổn định, localization key, icon address và validation cho mọi item.
- Mỗi item có luật binding, stack, sell, salvage, trade, durability và source rõ.
- UI túi test ở 16:9 và 20:9, gamepad focus, cỡ chữ 200%, túi đầy và mất mạng giữa thao tác.
- So sánh stat phản ánh đúng công thức server, không tính nhầm bonus PvP/raid cap.
- Test nội dung bằng item giả lập mọi rarity; không tái sử dụng asset hình ảnh/tên/dữ liệu độc quyền trích từ KPAH.
