# CHIẾN TRƯỜNG TRẤN SƠN 10v10 — ĐẶC TẢ PRODUCTION

## 1. Phạm vi và luật trận

Mode 10v10 là hoạt động PvP ghép trận độc lập, dùng art/geometry `MAP_TRAN_SON_SIEGE` nhưng tạo instance với `zone_id=BG10`. Không dùng bang hội, roster, MMR, lịch, siege objective hay ledger thưởng của công thành 20v20. Bản đồ combat bounds 0–360 WU, sàn Y=0; camera giữ toàn bộ lane trung tâm và không cho thấy vị trí spawn đối phương.

| Tham số | Giá trị baseline |
|---|---|
| Cấp vào | 36+, mở sau C3-01; queue solo hoặc nhóm 2–5 |
| Đội | Lam 10 / Đỏ 10; server cân class, không bắt buộc role |
| Match | 12 phút; không overtime quá 90 giây |
| Thắng | 1.000 điểm trước, hoặc điểm cao nhất khi hết giờ |
| Mục tiêu | giữ 2/3 cờ để sinh điểm; cướp Huy Hiệu Trấn Sơn về điểm nhà để cộng điểm lớn |
| Đồ dùng | consumable chiến đấu, buff PvE và sát thương pet bị khóa; ngoại trang vẫn hiện |
| Gear/skill | stat chuẩn hóa theo profile cấp 40; khi vào mode mọi account được PvP template mở cùng bộ skill và chọn tối đa 2 passive class, không phụ thuộc level PvE; gear ép HP/attack/defense vào band |
| Hệ số PvP | dùng coefficient PvP của skill; stun DR, heal/shield caps theo Activities spec |
| Xếp hạng | casual queue trước launch; ranked MMR chỉ bật theo season config, không phụ thuộc siege rating |

## 2. Bố trí zone và tọa độ

Toàn bộ tọa độ dùng WU; thiết kế map full-width 360×72 WU, lane chính Y=0. Các điểm sau phải dùng `BG10` layer để không đè lên actor công thành. Hai căn cứ có vùng bất khả xâm phạm bán kính 12 WU; đòn đánh và target lock bị chặn bên trong.

| ID | Loại | X,Y | Quy tắc |
|---|---|---:|---|
| BG10_SPAWN_BLUE | team spawn | 28,0 | 10 anchor player slot, spawn spread ±5 WU; immunity 3s hoặc tới khi gây damage |
| BG10_SPAWN_RED | team spawn | 332,0 | 10 anchor player slot, spawn spread ±5 WU; immunity 3s hoặc tới khi gây damage |
| BG10_POINT_W | capture | 92,0 | capture radius 8 WU; progress 8s khi không tranh chấp |
| BG10_POINT_M | capture | 180,0 | capture radius 9 WU; tiến độ trung lập 10s, tranh chấp thì dừng |
| BG10_POINT_E | capture | 268,0 | capture radius 8 WU; progress 8s khi không tranh chấp |
| BG10_RELIC_NEUTRAL | flag altar | 180,7 | hiện sau 90s, rồi mỗi 150s sau khi được ghi điểm/trả về |
| BG10_RELIC_HOME_BLUE | home socket | 40,0 | điểm nộp cờ Lam |
| BG10_RELIC_HOME_RED | home socket | 320,0 | điểm nộp cờ Đỏ |
| BG10_JUMP_W / BG10_JUMP_E | flank route | 132,0 / 228,0 | đường vòng 1 chiều 6s; khóa khi người mang cờ |

Props công thành như siege engine, NPC guard, phá cổng, cờ guild và công cụ repair không spawn trong `BG10`. Chỉ tái dùng collision đã kiểm duyệt; loại bỏ tương tác gây damage hoặc block path không thuộc mode.

## 3. Flow, tính điểm và mục tiêu cờ

1. **Queue:** validate level, account penalty, party max 5, latency region; queue cross-party ưu tiên tạo hai đội cân class và MMR (nếu ranked). Không tạo bot lấp chỗ.
2. **Ready room:** 20 giây, hiển thị map, mode, normalized rules, latency và đội hình. Người từ chối/timeout rời trận và nhận penalty theo mục 6.
3. **Warm-up:** 15 giây trong căn cứ; cấm damage/di chuyển ra cổng. Đồng hồ trận bắt đầu khi cổng mở đồng thời.
4. **Capture:** một điểm do một đội chiếm sẽ sinh 1 điểm/giây. Hai hoặc ba điểm do cùng đội giữ sinh lần lượt 3 hoặc 5 điểm/giây. Điểm đang bị tranh chấp không sinh điểm. Control đổi owner sau 8s liên tục có mặt duy nhất một team; capture progress decay 2× khi không ai giữ.
5. **Huy Hiệu:** relic spawn theo chu kỳ. Chạm 1.2s để nhặt; người mang di chuyển 80%, không dùng mobility ultimate, hiện marker cho cả hai đội và không thể stealth. Hạ người mang làm relic rơi tại chỗ; tương tác nhặt lại 1s. Không được nhặt trong spawn shield.
6. **Ghi điểm relic:** mang relic tới home socket, giữ tương tác 2s, cộng 100 điểm và 10s capture score boost ×2; sau đó relic hồi tại altar sau 20s. Nếu không nhặt trong 30s, tự về altar. Kết thúc trận không thưởng relic đang trên đường.
7. **Tiebreak:** điểm match → số điểm capture tích lũy → số lần ghi relic → tổng objective contribution → hòa được ghi draw. Overtime chỉ chạy nếu hai đội bằng điểm ở phút 12 và một đội đang capture progress; dừng ngay khi điểm thay đổi, tối đa 90s.

## 4. Combat, spawn, reconnect và hành vi bất thường

- Server authoritative 20 tick/s; capture/relic/score/chống AFK xác nhận từ server. Client chỉ gửi intent di chuyển, skill ID, target ID và input sequence.
- Hạ gục: respawn 8s, thêm tối đa 4s theo chuỗi chết liên tục; không mất đồ/độ bền/EXP. Assist dựa damage/heal/objective trong 10s.
- Disconnect: giữ slot 120s và cho người chơi nối lại đúng trận; avatar đứng yên 2s rồi chuyển sang guard AI chỉ né hazard, không tấn công/capture. Không có backfill sau khi match bắt đầu.
- Nếu đội thiếu người do timeout, trận vẫn tiếp tục; dưới 7 người còn kết nối trong 60s thì có thể concede bằng đầu phiếu 6 người. Server không tự trao thắng dựa trên disconnect đơn lẻ.
- Anti-AFK: mỗi 60s cần một trong các tín hiệu server xác thực: di chuyển >2 WU, damage/heal hợp lệ, tương tác mục tiêu, block/dodge trúng timing. UI cảnh báo ở giây 90 không hoạt động; loại khỏi reward ở 120s; queue penalty 5 phút lần đầu, 15 phút lần hai trong 24h, 60 phút lần ba. CS có thể đảo penalty nếu có sự cố server.
- Leaver, evade, queue-dodge và disconnect có reason code; không phạt khi match server-side bị void.
- Void match nếu server crash trước phút 3 hoặc bất kỳ đội nào có dưới 5 người do lỗi hệ thống; reward/quest ledger không commit và MMR không đổi.

## 5. Reward và lịch

- Casual queue luôn khả dụng, giới hạn 3 reward cache/ngày; trận sau vẫn cho XP tài khoản/achievement không lặp và không tạo currency lạm phát.
- Thưởng thắng: `CURRENCY_TSS_MERIT` ×20; tham gia hoàn tất: ×10; objective score ≥100: +5; thua không bị trừ Đồng/đồ. Cap merit 60/ngày/account. Queue abandon/AFK không nhận.
- Merit chỉ đổi cosmetic, emote, title, banner, dye; không mua power gear, craft material hoặc progression acceleration.
- Daily reward ledger reset 05:00 Asia/Ho_Chi_Minh; season/ranked reset theo config versioned. Ranked season chưa bật thì casual mode không ghi MMR.
- Result payload lưu `match_id`, `season_id|null`, `team_result`, per-player score, objective score, reconnect/AFK flags, rewards, server build và ruleset hash.

## 6. Telemetry và nghiệm thu

Emit `bg10.queue_join`, `bg10.match_start`, `bg10.capture_change`, `bg10.relic_pickup`, `bg10.relic_score`, `bg10.disconnect`, `bg10.afk_warning`, `bg10.match_end`, `bg10.reward_commit`. Không đưa nội dung chat hay PII vào gameplay analytics.

Nghiệm thu: đủ 20 anchor spawn không chồng collision; điểm capture không đổi khi client sửa packet; không thể gây damage xuyên spawn shield; cờ không thể nhân đôi qua reconnect; kết quả duy nhất cho mỗi match; điều kiện void không cấp MMR/reward; toàn bộ telegraph/marker đọc được ở VFX Low; camera giữ objective trong vùng hiển thị ở 16:9 và 20:9.

