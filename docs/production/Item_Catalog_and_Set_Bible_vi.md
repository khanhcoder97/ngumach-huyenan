# BIBLE TRANG BỊ VÀ DANH MỤC ITEM
## Ngũ Mạch: Huyền Ấn — catalog khóa v1.0

### 1. Phạm vi catalog

File Item_Master_Catalog_vi.csv là danh mục master để import vào spreadsheet/database. Bản này có 556 template: 420 template trang bị nền (5 môn phái × 7 dải cấp × 12 slot) cùng 136 template tiêu hao, ngọc, nguyên liệu, quest, vé hoạt động, công cụ nghề, thú/cưỡi, recipe và mỹ phẩm. Item_Rarity_Variant_Catalog_vi.csv bung 5 phẩm chất thành 2.100 biến thể gear có ID và chỉ số nền đã scale riêng, cộng 136 item fixed; tổng 2.236 dòng. Affix roll, socket roll, upgrade và durability vẫn là thuộc tính instance theo schema. Bảy vật liệu node và bốn công cụ nghề được tra vị trí trong `World_Spawn_Gathering_Manifest_vi.csv`.

Các item names, chỉ số, hiệu ứng và nguồn rơi ở đây là đề xuất mới cho game Ngũ Mạch: Huyền Ấn. KPAH JAR không cung cấp catalog server hoàn chỉnh để xác minh từng tên, stat hay drop table.

### 2. Tier và tăng chỉ số nền

Bảy tier dùng đúng band GDD. Item yêu cầu cấp đầu band. Một món ở band mới là nâng cấp chính; item ở band cũ vẫn có thể hữu dụng qua affix/set build.

| Tier | Cấp yêu cầu | Vùng/tên bộ | Weapon power nền | Giáp mỗi mảnh nón/áo/quần/găng/giày |
|---|---:|---|---:|---:|
| T1 | 1 | Mưa Khởi / Bến Mưa | 12 | 2 / 4 / 2 / 1 / 1 |
| T2 | 16 | Thanh Lạc / Thành Thanh Lạc | 78 | 6 / 12 / 6 / 4 / 4 |
| T3 | 31 | Rễ Nhớ / Lâm Triều | 175 | 12 / 24 / 12 / 8 / 8 |
| T4 | 46 | Tro Lò / Sa Hỏa | 345 | 20 / 40 / 20 / 13 / 13 |
| T5 | 61 | Sơn Thệ / Trấn Sơn | 560 | 29 / 58 / 29 / 19 / 19 |
| T6 | 76 | Uyên Lam / Bạch Uyên | 805 | 38 / 76 / 38 / 25 / 25 |
| T7 | 91 | Nghịch Mạch / Vực Nghịch Mạch | 1.050 | 48 / 96 / 48 / 32 / 32 |

Vũ khí phép và vật lý cùng power budget trong band; nội dung visual/animation khác theo lớp. Chênh vũ khí lớp tối đa 5%. Trang bị phụ không có weapon power; chỉ số ghi trong CSV là stat nền trước rarity và affix.

### 3. Phẩm chất, dòng phụ, socket và scaling

| Phẩm chất | Hệ số chỉ số nền | Số affix random | Số socket | Giám định dòng ẩn |
|---|---:|---:|---:|---|
| Thường | ×1,00 | 0 | 0 | không có |
| Tinh | ×1,06 | 1 | 0 | không có |
| Linh | ×1,12 | 2 | 0–1 | không có |
| Huyền | ×1,20 | 3 | 1–2 | có 1 dòng |
| Cổ Vật | ×1,30 | 4 | 0–3 | có 1 dòng đặc biệt |

Rarity không đổi level yêu cầu hoặc class restriction. Rarity modifier áp dụng lên base stat theo rounding gần nhất, sau đó cộng affix; không nhân tiếp set bonus, hidden effect hoặc upgrade. Set bonus không cộng chồng với một set khác cùng class; tối đa một set effect 2-piece và một effect 4-piece cùng set đang active.

### 4. Pool dòng ngẫu nhiên và giá trị

Affix random chỉ lấy từ pool hợp lệ theo slot. Mỗi dòng có roll từ min tới max; server seed quyết định giá trị. Không thể roll hai dòng cùng stat trên cùng món. Chỉ số phần trăm áp dụng vào base trước cap; UI hiển thị cap còn lại.

| Affix ID | Stat | T1 | T2 | T3 | T4 | T5 | T6 | T7 | Slot |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| AFF-STR | Sức mạnh | 1–2 | 3–5 | 5–8 | 8–12 | 11–16 | 14–20 | 17–24 | armor/accessory |
| AFF-INT | Linh lực | 1–2 | 3–5 | 5–8 | 8–12 | 11–16 | 14–20 | 17–24 | armor/accessory |
| AFF-AGI | Nhanh nhẹn | 1–2 | 3–5 | 5–8 | 8–12 | 11–16 | 14–20 | 17–24 | armor/accessory |
| AFF-VIT | Thể chất | 1–2 | 3–5 | 5–8 | 8–12 | 11–16 | 14–20 | 17–24 | armor/accessory |
| AFF-LUK | Vận khí | 1–2 | 3–5 | 5–8 | 8–12 | 11–16 | 14–20 | 17–24 | armor/accessory |
| AFF-HP | HP tối đa | 10–20 | 35–60 | 70–110 | 130–190 | 200–280 | 300–410 | 430–570 | chest/neck |
| AFF-MP | MP tối đa | 5–10 | 18–30 | 35–55 | 60–90 | 95–135 | 140–190 | 200–270 | neck/ring |
| AFF-ARMOR | Giáp | 1–2 | 3–5 | 6–10 | 10–16 | 16–23 | 23–32 | 32–44 | armor |
| AFF-RES | Kháng nguyên tố | 1–2% | 2–3% | 3–4% | 4–5% | 5–6% | 6–7% | 7–8% | armor/accessory |
| AFF-ACC | Chính xác | 1–2% | 1–2% | 2–3% | 2–3% | 3–4% | 3–4% | 4–5% | weapon/glove |
| AFF-DODGE | Né | 0,5–1% | 1% | 1–1,5% | 1,5% | 1,5–2% | 2% | 2–2,5% | boots |
| AFF-CRIT | Chí mạng | 0,5% | 0,5–1% | 1% | 1–1,5% | 1,5% | 1,5–2% | 2% | ring/weapon |
| AFF-CRITRES | Kháng chí mạng | 1–2% | 2–3% | 3–4% | 4–5% | 5–6% | 6–7% | 7–8% | armor/accessory |
| AFF-ATKSPEED | Tốc đánh | 0,5% | 0,5–1% | 1% | 1–1,5% | 1,5% | 1,5–2% | 2% | gloves/ring |
| AFF-CDR | Hồi chiêu | 0,5% | 0,5% | 0,5–1% | 1% | 1–1,5% | 1,5% | 1,5–2% | accessory |
| AFF-HEAL | Hiệu quả hồi | 1% | 1–2% | 2% | 2–3% | 3% | 3–4% | 4% | Huyền Bút gear |
| AFF-ELITE | Damage tinh anh/boss | 1% | 1–2% | 2% | 2–3% | 3% | 3–4% | 4% | weapon/pendant |
| AFF-PVPDMG | Damage PvP | 0,5% | 0,5% | 0,5–1% | 1% | 1–1,5% | 1,5% | 1,5–2% | PvP pool only |

Affix PvP không roll trên đồ quest campaign; cap damage PvP tổng 15%, cap CDR 15%, crit PvP 25%, né PvP 15%, tốc chạy từ trang bị 15%. Tỉ lệ proc/khống chế không thể roll ngẫu nhiên trên gear.

### 5. Dòng ẩn — mã hóa rõ, không có stat bí mật không thể tra cứu

Huyền/Cổ Vật có đúng một dòng ẩn. Khi rơi, dòng ở trạng thái “chưa giám định”; item detail ghi loại hiệu ứng nhưng giấu trị số cụ thể. Giám định tại NPC miễn phí lần đầu/ngày, sau đó phí Đồng cố định theo tier; không random hóa dòng, không phá item. Danh mục dòng ẩn:

| Slot | Hidden effect | T1→T7 trị số | Giới hạn |
|---|---|---|---|
| Vũ khí | Tăng tạo tài nguyên lớp từ đòn trúng | +1/2/3/4/5/6/7% | không tăng damage trực tiếp |
| Nón | Kháng khống chế | +1/2/3/4/5/6/7% | tổng cap 35% |
| Áo | Khi HP dưới 35%, nhận khiên | 2/4/6/8/10/12/14% HP, ICD 60s | không cộng dồn |
| Quần | Giảm damage hazard môi trường | 2/3/4/5/6/7/8% | PvP không áp dụng |
| Găng | Tăng damage đòn thường lên elite | 1/2/3/4/5/6/7% | boss/raid coefficient riêng |
| Giày | Sau né thành công tăng tốc chạy 1s | 2/3/4/5/6/7/8% | ICD 8s, cap movement |
| Dây chuyền | Hồi MP trong combat mỗi 5s | 1/2/3/4/5/6/7 MP | không kích hoạt khi full MP |
| Nhẫn trái | Chí mạng | +0,5/0,7/0,9/1,1/1,3/1,5/1,7% | chịu cap class mode |
| Nhẫn phải | Kháng chí mạng | +1/2/3/4/5/6/7% | chịu cap PvP |
| Ngọc bội | Tăng damage lên mục tiêu đang có debuff | +1/2/3/4/5/6/7% | chỉ một debuff check, không nhân theo số debuff |
| Phi phong | Giảm damage đạn xa | 1/2/3/4/5/6/7% | không áp boss AoE |
| Ấn hộ mệnh | Tăng tốc tích tài nguyên lớp | 1/2/3/4/5/6/7% | không rút ngắn skill CD trực tiếp |

### 6. Set bonus cho mọi tier/class

Mỗi class có một bộ 5 mảnh theo từng tier: nón, áo, quần, găng, giày. Weapon và phụ kiện thuộc tier nhưng không cộng vào số mảnh. Số liệu bonus theo tier:

| Tier | T1 | T2 | T3 | T4 | T5 | T6 | T7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Hệ số 2 mảnh, n% | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| Hệ số 4 mảnh, m% | 4 | 5 | 7 | 9 | 11 | 13 | 15 |
| Khiên hồi phục 4 mảnh | 2 | 3 | 4 | 5 | 6 | 7 | 8% HP |

| Class | Hiệu ứng 2 mảnh | Hiệu ứng 4 mảnh |
|---|---|---|
| Minh Kiếm | Phản Quang thành công tăng giảm sát thương thêm n% trong 3s | Sau đỡ chuẩn, Tầm Long gây thêm m% damage trong 4s; ICD 8s |
| Ảnh Đao | Chảy máu do Huyết Nguyệt tăng n% damage | Tử Diệm tăng m% damage khi tiêu ít nhất 3 Nhiệt |
| Huyền Bút | Khiên và hồi máu của lớp tăng n% | Đồng minh nhận Mưa Tinh có khiên bằng bảng “Khiên hồi phục 4 mảnh” trong 3s; ICD 20s |
| Thạch Chùy | Thiết Bích tăng thêm n% damage reduction, tổng cap 40% | Khiêu Chiến tạo khiên theo bảng “Khiên hồi phục 4 mảnh” cho bản thân; ICD 20s |
| Linh Cung | Damage nhóm lên mục tiêu Khóa Mạch tăng n% | Đòn đầu tiên trúng mục tiêu mới được đánh dấu tăng damage nhóm m% trong 4s; ICD 12s |

Các con số ghi trong CSV cho từng bộ SET-T1..T7-CLASS, không tự scale ngoài bảng. Số set hiện trên UI trước khi mặc và khi người chơi đổi món.

### 7. Cường hóa và nâng cấp

- Cấp nâng +0..+15; +1–+5 chắc chắn, +6–+10 thất bại không mất cấp/đồ; +11–+15 cần vật liệu bảo hộ, fail không phá đồ.
- Mỗi cấp cộng weapon power/armor theo phần trăm cơ sở: +1..+5 mỗi cấp +2%, +6..+10 mỗi cấp +1,5%, +11..+15 mỗi cấp +1%; tổng +27,5% tại +15. Không tăng hidden/set bonus.
- Chi phí Đồng T1→T7 tại cấp +1: 100/500/1.500/4.000/8.000/15.000/25.000; mỗi cấp tiếp theo ×1,35, round lên 10.
- Vật liệu nâng cấp theo tier: T1 MAT-ORE-01, T2 MAT-ORE-02, T3 MAT-ORE-03, T4 MAT-ORE-04, T5 MAT-ORE-05, T6 MAT-SCALE-01, T7 MAT-CORE-01. Mỗi lượt +1..+5 cần 1 vật liệu; +6..+10 cần 2; +11..+15 cần 3 và 1 MAT-GUARD-01 (Phù Bảo Hộ). Tỷ lệ công khai lần lượt +6:80%, +7:70%, +8:60%, +9:50%, +10:40%, +11:35%, +12:30%, +13:25%, +14:20%, +15:15%; thất bại không phá/giảm cấp.

Tinh luyện một affix dùng MAT-SEAL-01 + 1 vật liệu cường hóa đúng tier và phí Đồng theo tier; chi tiết mode/UI, repair, salvage, gem fusion và phí xem `Forge_Crafting_Overlay_Spec_vi.md`. Làm tròn stat nâng cấp một lần từ base theo `round_half_up`, không cộng dồn sai số từng cấp.

### 8. Vật phẩm non-gear

CSV bao gồm các vật phẩm phục vụ đúng vòng chơi:
- Potion HP/MP ba band, giải Chậm/Độc; cooldown theo nhóm 8s.
- Thức ăn PvE công/giáp/thu thập 20 phút; không cộng dồn cùng nhóm buff.
- Dụng cụ sửa, phù về hub, vé Mạch Triều, pet feed, vật phẩm hồi sinh ngoài boss.
- Năm loại ngọc nguyên tố, mỗi loại 5 cấp; mỗi level có một stat cố định.
- 17 vật liệu chính gồm quặng, gỗ, dược, linh phách, lõi mạch, Cổ Linh Phách, nước sạch, tro lò, vảy uyên, mảnh ấn, da, vải, hạt giống, cá, thạch mạch, giấy phù và Phù Bảo Hộ. Phù Khóa nằm trong nhóm tiêu hao tiện ích.
- Quest item theo campaign có questLocked, không bán/không giao dịch.
- 5 companion, 5 thú cưỡi và nhóm cosmetic launch. Cosmetic không có stat.

### 9. Trường dữ liệu CSV và quy trình import

Mỗi row chứa itemId ổn định, tên, category, slot, class restriction, level, rarity pool, base stats, affix/socket range, set ID/bonus, hidden effect ID/trigger, durability/binding/tradeability, map source và description. ID không chứa tên hiển thị/localization. CSV dùng dấu phẩy chuẩn, UTF-8, tất cả text quote RFC4180. Import phải báo duplicate ID, missing localization key, invalid slot/class, stat ngoài band, set bonus trên item không thuộc set và vật phẩm quest có thể bán.
