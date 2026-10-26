# ĐẶC TẢ NÔNG TRẠI, CÂU CÁ VÀ THU THẬP

## 1. Phạm vi, truy cập và dữ liệu chuẩn

Nông trại và câu cá là vòng lặp bổ trợ, không chặn main quest/endgame và không tạo vật phẩm sức mạnh độc quyền. Runtime rows nằm trong Life_Sim_Content_Data_vi.csv; ba nghề thu thập quặng/dược/gỗ tiếp tục lấy vị trí từ world manifest. Câu cá dùng activity riêng, không tính là nghề thứ tư.

Nông trại mở sau SQ-BM-05, truy cập từ hoạt động Nghề ở Thăng Long. Mỗi tài khoản có một farm pocket riêng gắn MAP_THANG_LONG, zone_id=FARM_PRIVATE_POCKET, local bounds X=0..84/Y=0..16 WU, năm luống tại (10,0), (26,0), (42,0), (58,0), (74,0). Năm luống là năm điểm trồng đồng thời; quyền sở hữu/seed/crop/ready timestamp nằm server-side. Không có va chạm hoặc PvP.

| Thông số farm | Baseline |
|---|---|
| Lượt trồng đồng thời | 5 luống/account |
| Thu hoạch | tổng tối đa 12 item output/ngày/account; reset 05:00 Asia/Ho_Chi_Minh |
| Thời gian phát triển | 1–6 giờ theo loài, real time server UTC; tăng trưởng khi offline |
| Cửa sổ thu hoạch | từ matured tới 24h; quá hạn cây héo, mất output nhưng trả lại luống |
| Tưới/chăm | một tương tác 2s; không bắt buộc đăng nhập hàng ngày; chỉ cosmetic growth FX, không tăng yield |
| Seed | MAT-SEED-01; giá mua đề xuất 10 Đồng/seed, giới hạn shop 20/day/account |
| Tool | TOOL-SICKLE-01; utility item, không giảm condition trong PvP |
| Chất lượng | Common 80%, Rare 18%, Epic 2%; mỗi roll server-seeded; Rare +1 output, Epic +2 output |

## 2. Câu cá — vị trí, vòng thao tác và tính thưởng

Các vị trí là anchors trong manifest với record IDs MAN-BM-FISHING-LINH, MAN-DNM-FISHING-MACH/TRO, MAN-LT-FISHING-RE, MAN-BY-FISHING-BANG, MAN-VM-FISHING-VUC. Tọa độ WU bám atlas: Bến Mưa (132,-1), Đại Ngũ Mạch hồ trung tâm (185,0), Đại Ngũ Mạch hồ làm mát lò (240,0), Lâm Triều suối (158,-3), Bạch Uyên hồ áp suất (168,0), Vực Nghịch Mạch hồ phản chiếu (182,0).

| Bãi | ID loài | Level | Điều kiện |
|---|---|---:|---|
| Bến Mưa | LIFE_FISH_CA_LINH — Cá Linh | 1 | mưa; mọi ngày |
| Đại Ngũ Mạch — hồ | LIFE_FISH_CA_MACH — Cá Mạch | 5 | rạng sáng/ban đêm |
| Đại Ngũ Mạch — hồ làm mát | LIFE_FISH_CA_TRO — Cá Tro | 12 | vent lò mở, ngoài combat |
| Lâm Triều | LIFE_FISH_CA_RE — Cá Rễ | 8 | ban đêm |
| Bạch Uyên | LIFE_FISH_CA_BANG — Cá Băng | 20 | triều lạnh |
| Vực Nghịch Mạch | LIFE_FISH_CA_VUC — Cá Vực | 30 | event tuần đang active, vùng an toàn cạnh trại |

Flow: kiểm tra level/bãi/tool/bait/quota → bắt đầu cast 4s → server tạo tension sequence → client gửi 3 input có sequence number trong tổng 8s → server tính quality/yield → commit bait/output/quota atomically. RTT tolerance ±180ms, nhưng client không gửi roll/quality. Bait chỉ tiêu sau khi cast hợp lệ; đứt dây sau ba input sai/miss. Một bãi chỉ có một fishing interaction mỗi character; bị hit, combat, map transition hoặc mất kết nối trên 10s thì cancel cast không cấp output. Quota 20 cá/ngày/account; bắt tiếp có thể chơi minigame nhưng không tạo item sau cap.

Quality weights: Common 85%, Rare 14%, Epic 1%. Rare +1, Epic +2 output so với output_min; output không vượt output_max. Fish item output dùng ID từ item master; market/bind theo item template, không tạo loại item mới theo chất lượng.

## 3. Anti-exploit, persistence và UI states

- Store plot_id, seed_instance_id, crop_id, planted_at_utc, mature_at_utc, wither_at_utc, state, row_revision; chỉ server time quyết định trưởng thành.
- Harvest commit idempotent trên plot_id + cycle_id; double click/retry không cấp gấp đôi. Daily cap dùng ledger account-wide, không reset bằng đổi nhân vật/region.
- Fish cast dùng cast_id, server seed, input sequence/nonce; replay packet bị từ chối, đổi map/hop shard hủy cast, reward ledger unique theo cast_id.
- Tool/bait/output nằm trong transaction; inventory đầy thì kết quả vào inbox tối đa 24h và giữ quota đã dùng, tránh retry farm vô hạn.
- Cross-account trade không tạo giá trị vượt seed/merchant sink; source, sink, quality và số lượng ghi vào economy telemetry.

UI bắt buộc: empty plot, growing timer, ready, withered, inventory-full, cap reached, locked level, unavailable weather/window, missing tool/bait, offline/reconnect. Countdown hiển thị server estimate; tooltip nói rõ quota còn lại và sản lượng cơ bản trước khi bắt đầu.

## 4. Thú đồng hành và thú cưỡi

Roster và item refs nằm trong Pet_Mount_Production_Data_vi.csv; companion template IDs PET-01..05, mount MOUNT-01..05. Mỗi character có thể sở hữu 5 companion nhưng chỉ triệu hồi một; skill active tự kích hoạt theo AI/PvE, người chơi có thể tắt auto skill. Pet XP nhận từ hoạt động hoàn tất, không từ AFK; cấp tối đa 30; cấp 10/20/30 mở skill tier trong data. Bond feed dùng PET-FEED-01, cooldown 12h, chỉ tăng bond/cosmetic progress.

Bốn slot thú là PET_HEAD, PET_ARMOR, PET_COLLAR, PET_SADDLE; baseline chỉ là ngoại hình, chưa có item stat. Pet skill không tấn công/hồi/taunt trong PvP, raid boss, world boss hay objective siege; quái boss không bị pet taunt. Một pet tự động không thể tăng số loot, contribution score hoặc quest count. Pet teleport về chủ sau 5s vượt leash 8 WU; ẩn trong cutscene.

Mount không có level/skill/battle stat; +10% tốc độ chỉ trong overworld ngoài combat. Không kích hoạt trong city interior, instance, PvP, conversation hoặc khi người chơi đang mang relic/objective; server hủy movement bonus ngay khi combat state bật. Cosmetic mount khác nhau về model/animation/FX, không khác tốc độ.

