# MA TRẬN CHỨC NĂNG MMORPG
## Ngũ Mạch: Huyền Ấn — Functional Specification v1.0

### 1. Phạm vi và nguyên tắc

Định nghĩa chức năng bắt buộc của MMORPG 2D nhìn từ trên PC/mobile: tạo nhân vật, vào thế giới nhiều người, chiến đấu, làm nhiệm vụ, phát triển nhân vật, giao dịch, chơi cùng nhóm/bang và tham gia hoạt động. Kinh tế, combat, quest và quyền truy cập do server quyết định.

Mức ưu tiên: **P0** bắt buộc cho vertical slice/alpha; **P1** cần cho launch; **P2** có thể thêm sau nhưng chuẩn bị data/API; **Cấu hình** chỉnh qua server config/live ops.

### 2. Ma trận chức năng

| Domain | Chức năng | Ưu tiên | Authority |
|---|---|---|---|
| Tài khoản | đăng nhập, chọn server, session, đăng xuất, reconnect | P0 | account service |
| Nhân vật | tạo/chọn/xóa có thời gian chờ, tên, lớp, diện mạo, 4 slot | P0 | character service |
| Thế giới | map, shard/kênh, chuyển vùng, teleport, hồi sinh | P0 | world/zone |
| Điều khiển | đi 8 hướng, né, tương tác, camera, tay cầm | P0 | server xác thực movement |
| Combat | đánh thường, 6 skill, né, tài nguyên lớp, target, aggro, status, death | P0 | combat authority |
| PvE | quái thường/elite/boss, loot, party contribution, respawn | P0 | world/combat/loot |
| Quest | main/side/daily/weekly/class/guild, dialogue, objective, reward | P0 | quest authority |
| Build | level, EXP, 5 chỉ số, skill tree, 2 preset, danh hiệu | P0/P1 | progression |
| Gear | 12 slot, 4 pet slot, rarity, affix, dòng ẩn, set, socket, upgrade, repair | P0/P1 | item ledger |
| Túi/kho | 100 bag, 120 personal storage, guild vault, quest inventory | P0 | item ledger |
| Craft | nghề, recipe, preview, batch, validate material | P1 | craft transaction |
| Thương mại | NPC shop, direct trade, market, escrow, fee, mail | P1 | economy ledger |
| Social | party 5, raid 10, friends, block, invite, LFG, presence | P0/P1 | social service |
| Guild | create, rank, permission, quest, contribution, vault, siege | P1 | guild authority |
| Pet/mount | summon pet/passive/feed/gear, mount ngoài combat | P1 | companion |
| Life | mining, wood, herb, farm 5 plots, fishing, minigame | P1 | activity service |
| PvP | duel, arena 3v3, siege 20v20; gear normalization | P1 | match service |
| Endgame | 4 dungeon, 2 raid, 6 world bosses, final raid boss, 30-floor tower, event pool | P1 | encounter |
| UX | HUD, key rebinding, LowFX, subtitles, colorblind patterns | P0 | client settings |
| Safety | report, mute, block, rate limits, audit/mod tools | P0/P1 | moderation |
| Operations | config, scheduled events, dashboards, rollback, notice | P1 | ops/admin |
| Monetization | mỹ phẩm/tiện ích; không bán combat RNG theo policy hiện tại | P2 | commerce optional |

### 3. Account và nhân vật

**Session:** heartbeat mỗi 15s; sau 45s không nhận heartbeat zone đánh dấu reconnecting trong 120s rồi logout. Reconnect phục hồi safe zone/checkpoint, quest, inventory snapshot và giao dịch/reward đang chờ. Đăng nhập mới trả accountId, sessionId, region, build và danh sách nhân vật.

**Tạo nhân vật:** server normalize Unicode, lọc tên trùng/từ cấm/ký tự vô hình; chọn 1 trong 5 lớp; chỉnh body frame, mặt, da, tóc, phụ kiện; chọn gợi ý phân bổ 5 stat hoặc tự chia. Lớp cố định sau xác nhận; không khóa lớp theo giới tính, ngoại hình không tạo chỉ số. Character tạo cùng bundle đồ đầu game trong một transaction. Tối đa 4 nhân vật/account. Xóa cần xác nhận 2 bước và chờ 7 ngày; hỗ trợ có thể phục hồi trước purge.

**Chọn nhân vật:** preview pixel sprite, class, level, khu vực cuối, thời gian chơi/đăng nhập; tải patch trước khi vào. Nhân vật lưu loadout, ngoại hình, danh vọng, quest, guild/friend pointers.

### 4. Thế giới, di chuyển và vùng

**Movement:** client gửi input intent tối đa 20Hz; server kiểm tốc độ XY, collision trên mặt đất, knockback và vùng đi được. Client dự đoán chuyển động của mình rồi hòa giải; người khác được nội suy. Không chấp nhận client ghi trực tiếp tọa độ. Anti-cheat đánh dấu velocity/teleport bất thường để xem xét, không tự xóa nhân vật.

**Zone/map:** dữ liệu gồm MapID, bounds, layers, walkable polygons/collision, floor links, portals, NPC anchors, spawn groups, weather profile, encounter sockets. Nhiều shard/kênh mỗi vùng; đổi kênh chỉ ở hub; leader có thể mời party theo nếu encounter cho phép. Teleport cần điểm đích đã mở, không combat/raid; lưu nhân vật trước khi đổi map.

**Death:** HP=0 vào downed 15s trong PvE nhóm; đồng minh hồi sinh; solo về checkpoint. Sau hồi sinh có 2s movement safety nhưng không miễn nhiễm tấn công. Death không rơi item, không giảm durability. Rules boss/checkpoint theo Activities Spec.

**Map UX:** minimap/world map, known/unknown, NPC/quest marker chỉ hiện khi khám phá hoặc quest liên quan; không lộ người chơi địch ở PvP.

### 5. Cấp độ và build

- Level 1–100, EXP từ quest/PvE/events/exploration; repeated farm giảm dần reward nhỏ nhưng không giảm first clear/quest.
- Năm stat: Sức mạnh, Linh lực, Nhanh nhẹn, Thể chất, Vận khí; phân bổ có preview/confirm, server kiểm point budget.
- Sáu ô active skill mở ở 1/4/8/12/16/30; ultimate mở cấp 30; 8 passive nodes/class (hai nhánh × bốn node; cấp mở 20/40/60/80), tối đa hai passive được trang bị. Hai preset; đổi ở hub/rest point, không đổi giữa boss/PvP. Chi tiết import: `Class_Passive_Production_Data_vi.csv`.
- Class trial trong opening. Lớp cố định sau tạo; cảnh class trial xác nhận lớp, không đổi lớp/preset thành lớp khác.
- Năm regional trust flags, honor môn phái và guild contribution mở thoại/cosmetic/recipe, không khóa ending.
- Achievement theo first clear, collect, social, craft, boss strategy, season; thưởng cosmetic/title/emote/tiện ích nhẹ.
- Leaderboard tách theo activity/season; privacy có thể ẩn tên công khai.

### 6. Combat command và event

Lệnh **basicAttack**, **useSkill**, **dodge**, **interact** kiểm tra class/loadout/rank, MP/tài nguyên, cooldown, target/range/line-of-sight, combat state và permission. Server trả accepted/rejected reason + timestamp. Command có requestId để không tiêu tài nguyên hai lần khi client retry.

Combat resolution:
1. Validate lệnh và reserve cost/CD.
2. Xử lý cửa sổ hitbox/animation marker.
3. Validate target sống, team, LOS, invulnerability.
4. Apply damage/heal/shield/debuff/aggro.
5. Emit combat log/event tới party.
6. Commit objective/loot riêng, idempotent.

Status registry: slow, poison, bleed, shield, mark, stun, root, burn, pressure, class resource stacks, Mạch Stun boss. Mỗi trạng thái phải có stacking rule, duration cap, PvP coefficient, boss resist và cleanse rule.

### 7. Quest và narrative

Hỗ trợ main, side, daily/weekly, class, guild, collection, event. Quest schema có ID ổn định, prereq, level range, start/turn-in anchor, objective graph, dialogue key, fail/retry, reward, unlock, reset. Quest progress event-sourced/server-side; rewards có transaction ID.

State flow: LOCKED → AVAILABLE → ACTIVE → READY_TO_TURN_IN → COMPLETE. Repeatables reset về AVAILABLE theo lịch. Fail chỉ xảy ra rõ ràng ở escort/timer/instance objective, có checkpoint; dialogue choice đổi trust/thoại/cosmetic, không loại người chơi khỏi main path.

### 8. Túi, trang bị, craft và kinh tế

Item template tách item instance. Equip/use/sell/trade/mail/craft/salvage/upgrade/socket khóa item và commit atomic. Instance có binding, stack, rarity, stat roll, durability, flags, source, schema version. Client cache không phải authority.

**Craft:** preview đầu ra/chi phí; kiểm recipe/skill/level; reserve nguyên liệu; commit; lưu kết quả. Batch dừng khi cap/thiếu nguyên liệu/người chơi hủy. Reconnect trả kết quả transaction.

**Direct trade:** hai người tạo offer; đổi offer làm mất confirm cũ; mỗi bên xem item/tiền/phí; cả hai xác nhận rồi server commit atomic. Mất kết nối/rời vùng/bị tấn công hủy giao dịch.

**Market:** listing escrow lấy item khỏi túi; mua xác nhận; phí và tiền net hiện trước; settlement ledger trả qua mailbox; simultaneous purchase chỉ một người thành công. Listing cap, anomaly price band và cancel policy cấu hình server.

**Currency ledger:** Đồng, regional marks, dungeon/raid tokens, guild construction points, Mạch Triều tickets có nguồn/sink/cap riêng. Repair/upgrade/socket/market fee dùng transaction; client không tự roll tỷ lệ.

### 9. Nhóm, bạn bè, chat và bang

- Party 5: leader/invite/transfer/kick/promote; loot personal hoặc round-robin chọn trước dungeon. EXP tính damage/heal/shield/interrupt/objective.
- Raid 10 chia 2 nhóm 5, marker assistant, ready check, callout phase; class role không bắt buộc.
- Friends: request/accept/remove, presence/location sharing toggle; block chặn invite/whisper.
- Chat: Zone, Party, Guild, Whisper, System; rate limit; item link preview; report/mute; không có kênh giao dịch tiền thật mặc định.
- LFG lọc activity/level/ping/region/ngôn ngữ; class optional, không loại người chơi khỏi queue.
- Guild lifecycle, roles/permission, vault, quests, siege theo Guild Social Spec; mọi quyền kiểm ở server.

### 10. Thú, mount, nghề và farm

Một pet active; một passive pet skill; pet đi theo bằng path riêng, collision off trong combat; auto-loot chỉ nguyên liệu thường, không loot gear/quest/locked. Năm companion được thiết kế, 4 pet gear slots, level cap bằng config. Mount +10% speed ngoài combat, tắt trong instance/PvP; các mount cùng tốc độ.

Khai khoáng/hái dược/đốn gỗ: node sở hữu theo shard, tương tác 1,2s, bị damage thì ngắt; chỉ cấp nghề khi harvest hợp lệ. Farm 5 luống, trồng/tưới/thời gian/thu hoạch; offline growth cap 24h + grace. Fishing/minigame có daily cap reward chính; lượt thêm chỉ điểm/cosmetic.

### 11. Endgame, live events và PvP

Dungeon 5, raid 10, world boss, tower, arena 3v3, Trấn Sơn 10v10, siege 20v20, Mạch Triều theo Activities Spec và battleground spec. Scheduler có eventId, start/end/recurrence/timezone/shard/eligibility/reward caps. World event progress theo contribution, không last-hit. Session reconnect grace 120 giây; giải Long Môn cho một lần reconnect 90 giây; từng mode áp dụng luật riêng đã nêu. Reconnect khôi phục phase/contribution. Arena MMR theo season; thất bại không làm rơi đồ. Siege roster khóa 30m trước, disconnect reserve 90s, anti-AFK và tie/void logic ở server.

Duel 1v1 cần hai bên xác nhận; arena 3v3; siege 20v20. PvP profile có coefficient/caps/cooldown riêng. World PvP mặc định off; nếu thêm phải opt-in, vùng báo rõ, không camp checkpoint.

**Các chức năng online bổ sung:**
- Lịch hoạt động/điểm danh ngày-tháng hiển thị reset server, các mốc 7/14/28 ngày thưởng Đồng, nguyên liệu phổ thông hoặc cosmetic; bỏ lỡ không xóa streak đã nhận và không có gear độc quyền.
- Bảng xếp hạng gồm cấp, tower floor, arena rating, season siege và achievement; không phát vị trí realtime. Người chơi chọn ẩn tên khỏi bảng không cạnh tranh.
- Hòm thư dùng cho settlement chợ, hoàn giao dịch, quest overflow và system notice; attachment có expiration 30 ngày, hiện countdown, không là kho né giới hạn.
- Auto PvE là tùy chọn trợ năng trong vùng thường cấp thấp: tự đánh mục tiêu thường trong 5m bằng đòn cơ bản, không auto di chuyển qua portal, không dùng skill/potion, tự dừng khi boss/elite/quest object xuất hiện, inventory đầy, HP thấp hơn 25% hoặc PvP bật. Auto không tăng reward và không chạy dungeon/raid/siege.
- Hồ sơ nhân vật có title, achievement, lớp, cosmetic đang mặc, quyền riêng tư và nút report/block; không công khai thông tin account, email, thời điểm online chính xác nếu người chơi ẩn.

### 12. UX, thiết bị và network states

Settings modal dùng `Settings_Overlay_Spec_vi.md` làm nguồn UI. Preference service lưu schema versioned theo account/device; keybind, layout và FPS cap ưu tiên per-device; âm thanh, theme, HUD/text scale, accessibility và graphics sync theo account khi có mạng. Graphics preview có timeout/rollback, lưu lỗi giữ pending và retry; UI không ghi gameplay state. Account linking/logout/delete đi qua Account Service, không gửi credential trong log/client analytics. Thoát kẹt là request server-validated và bị từ chối trong boss/raid/siege, combat hoặc quest interaction bị khóa. Mở modal không pause world; LowFX/thời tiết tắt không được xóa telegraph/objective.

Network states: Connecting, Online, HighLatency, Reconnecting, Offline, Maintenance. High latency hiện ping và không báo reward thành công trước server commit. Offline chặn trade/market/party; maintenance có notice địa phương và thời gian.

### 13. Moderation, support và live operations

Player tools: mute, block, report, privacy, presence. Report categories harassment/scam/bot/exploit/name/other; evidence gồm message/event ID, không thu file cục bộ. Rate limit report, không auto-ban theo số report.

Moderator tools: tìm account/character, xem item/trade/guild ledger, mute/timeout/suspend, rollback transaction, restore deleted character trong retention, xem combat/siege event. Mọi admin action có reason/audit; thao tác nhạy cảm cần staff permission.

Live ops: config staged 5→25→100%, rollback, scheduler/reset, event, news banner, maintenance, dashboard economy/loot/latency/crash/reports. Không chứa secret trong client hoặc repository.

### 14. Điều kiện nghiệm thu chức năng launch

1. Người chơi mới tạo nhân vật, hoàn tất P00-01..05, trang bị EQ-[CLASS]-WEAPON-T1-R-COMMON, sang Thanh Lạc, hoàn tất C1-01..06 để mở Thăng Long Thành rồi reconnect không mất quest/reward/route unlock.
2. Hai người lập nhóm, thấy movement/HP, hoàn objective và chỉ nhận loot một lần.
3. Equip/craft/market/trade giữ atomic khi double click, timeout, logout và mua listing đồng thời.
4. Mọi skill enforce PvE/PvP/boss ở server; telegraph vẫn đọc được LowFX.
5. Bang tạo được, mời thành viên, làm quest tuần, xem kho/log và đăng ký siege theo permission.
6. Reconnect world event giữ đúng phase/contribution; caps và currency sinks chỉnh bằng server config.
7. Moderator truy vết report bằng immutable log và thực hiện rollback có audit.
