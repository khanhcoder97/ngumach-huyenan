# ĐẶC TẢ DUNGEON, RAID, BOSS, KINH TẾ VÀ HOẠT ĐỘNG
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.1

> DEC-016 (2026-10-28): áp dụng `Top_Down_Gameplay_World_Spec_vi.md`. Các bảng kích thước/placement cũ là blockout chưa nghiệm thu top-down. Y luôn là Bắc–Nam trên mặt đất. “Platform” là bệ/cầu/vùng an toàn có đường đi hoặc floor link, không yêu cầu nhảy; chiều cao silhouette/capsule cũ không dùng làm collider. ID được giữ; không tự chuyển tọa độ cũ thành độ cao.


### 1. Quy tắc hoạt động dùng chung

- Encounter chạy trên instance riêng cho nhóm; người chơi đơn có thể vào các dungeon campaign 5 người với bot hỗ trợ không cấp loot/achievement, nếu sản phẩm quyết định bật. Mặc định không có bot trong raid.
- Tối đa 5 người/dungeon, 10 người/raid; raid chia 2 party 5. Người chơi phải cùng khu vực server và cùng mức campaign. Ghép trận ưu tiên thời gian chờ, level band, latency; không bắt buộc thành phần healer/tank.
- Người rời vùng encounter hơn 60 giây bị đưa về checkpoint; reconnect trong 120 giây giữ slot nếu party chưa vượt cap. Boss reset nếu toàn đội chết hoặc rời khu trong 90 giây, trừ checkpoint cụ thể.
- Mỗi encounter có: mapInstanceId, encounterId, seed, phase, actor states, checkpoint, reward ledger, anti-repeat window. Boss HP/phase authoritative server. Mọi phase transition và reward idempotent.
- Người chơi nhận contribution từ damage, healing, shield, interrupt, objective, revive và tránh cơ chế. Đạt 5% contribution hoặc tham gia objective bắt buộc mới đủ điều kiện loot; AFK không nhận.
- Telegraph boss tối thiểu 0,9s cho đòn nguy hiểm, trừ đòn cận chiến thường; báo bằng shape + animation + audio. Cửa né phải hợp lệ ở ping 150ms.
- Raid có tiến độ hàng tuần; dungeon campaign replay vô hạn nhưng reward lớn giới hạn 2 lần/ngày/nhân vật; token phụ giảm dần, không khóa chơi.
- Mọi reward hiện trước khi vào: cấp đề nghị, số người, reset, loại token/loot, cơ chế trọng tâm. Không có RNG bắt buộc để hoàn tất cốt truyện.
- ID map activity dùng trong dữ liệu: DG-01…04 = `MAP_DG_01`…`MAP_DG_04`; RD-01/02 = `MAP_RD_01`/`MAP_RD_02`; công thành = `MAP_TRAN_SON_SIEGE`; Tháp Lạc Ấn tầng n = `MAP_LAC_AN_TOWER_Fnn`. Vị trí nhóm, actor, level band, điều kiện, reset và loot tham chiếu `World_Spawn_Gathering_Manifest_vi.csv`; tọa độ dungeon/raid/tháp là local instance WU.

### 2. Bốn dungeon 5 người

#### DG-01 — Hầm Van Rừng
- Level đề nghị 24–30; mở qua C2-03; thời lượng mục tiêu 18–24 phút.
- Bối cảnh: hành lang gốc cây và trạm nước dưới Lâm Triều. Map riêng 3 screen zones, mỗi zone 360×72 WU. Respawn checkpoint sau mỗi van.
- Mục tiêu: bật ba van theo thứ tự ký hiệu → ngăn hai wave Rễ Mộng → đánh Cổ Thụ Con.
- Encounter 1, Van Gãy: 3 người giữ cần, 2 người ngăn wave; mỗi van có 20s hold. Nếu wave chạm van, timer reset 5s chứ không reset toàn dungeon.
- Encounter 2, Sương Tên: chọn đúng 4 tên khắc trên cây theo quest clue; sai spawn 2 quái, không softlock.
- Boss Cổ Thụ Con: pha 1 quật rễ hình nón 0.9s; pha 2 thả nấm độc 3 vùng, đứng sau gốc cây che; pha 3 gọi rễ tuần hoàn quanh arena. Phá rễ sáng trong 6s giảm shield 20%. Boss có shield 3 stack, không miễn damage dài.
- Loot: gỗ linh, dược thảo, Ngọc Mộc cấp 1–2, set Lâm Triều Tinh; mỗi người nhận 1 cache cá nhân khi hoàn thành và 1 `CURRENCY_TOKEN_DG01` mỗi clear đủ điều kiện (tối đa 10/tuần/nhân vật), đổi đồ tại thương nhân Bí Cảnh.

#### DG-02 — Lò Tro Nghịch
- Level 40–47; mở sau C3-02; 20–26 phút.
- Bối cảnh: đường thông gió, kho than, ba van lửa; hazard khí độc/cát nóng.
- Mục tiêu: cân áp ba đường ống → giải cứu 4 thợ → hạ Người Canh Lò → tắt 3 lõi trong một khoảng.
- Encounter 1, Hành Lang Khí: ba vent có trạng thái mở/đóng; lặp pattern mỗi 12s, có đèn/puff báo trước 2s. Đi qua vùng khí khi đóng gây độc nhẹ, không one-shot.
- Encounter 2, Người Canh Lò: giáp 2 stack; mỗi người tương tác búa/van khác nhau, damage lên boss vẫn có tác dụng; thợ được giải cứu sửa một ụ chắn.
- Boss Lò Tro: pha 1 hai đòn quét ngang và cột lửa giữa; pha 2 nạp lò 10s, phải đóng ít nhất 2/3 van để tránh nổ lớn; pha 3 arena chia 3 làn lửa có khe an toàn di chuyển. Đóng van sai vẫn cho retry ở phase 2.
- Loot: quặng, MAT-SOUL, lõi Hỏa nhỏ, blueprint thuốc/giáp; cache cá nhân và 1 `CURRENCY_TOKEN_DG02` mỗi clear đủ điều kiện (tối đa 10/tuần/nhân vật), đổi bộ Lò Rèn.

#### DG-03 — Kho Ải Cờ
- Level 55–62; mở sau C4-02; 18–25 phút.
- Bối cảnh: tuyến vận tải bên dưới Trấn Sơn, không trùng mode siege.
- Mục tiêu: mở 2 cửa kho theo lệnh thật → hộ tống vật tư → đánh Phá Thành Cơ.
- Encounter 1, Lệnh Giả: đọc 3 dấu sáp, tương tác đúng cặp; sai làm spawn thêm wave, không khóa cửa.
- Encounter 2, Hộ Tống: xe có 100% durability, 2 checkpoint; repair action 2s; nhóm có thể dùng ụ nỏ để ngăn xe địch.
- Boss Phá Thành Cơ: pha 1 phá khiên sau lưng; pha 2 bắn nỏ vào ba lane, cắt dây neo để đổi vị trí; pha 3 lao qua arena, né sang platform thấp. Mỗi lần thất bại vẫn giữ 1/3 tiến độ dây neo đã cắt.
- Loot: quặng, phụ kiện Huyền cấp thấp, huy hiệu chiến trường, cờ/skin; 1 `CURRENCY_TOKEN_DG03` mỗi clear đủ điều kiện (tối đa 10/tuần/nhân vật); không thưởng siege rating.

#### DG-04 — Phế Tích Bạch Uyên
- Level 68–76; mở sau C5-02; 22–30 phút.
- Bối cảnh: 4 buồng áp suất; nước sâu, platform, dòng triều theo chu kỳ.
- Mục tiêu: bật 3 trạm → tìm 4 trang nhật ký → phá Mẫu Xà Non.
- Encounter 1, Buồng Áp: ba trạm có biểu tượng hình học. Đúng thứ tự: vòng, vạch, chấm; sai reset trạm hiện tại và sinh 2 Cá Gương.
- Encounter 2, Triều Ngược: tide timer 18s; lên platform an toàn; có 3 lựa chọn đường platform, không bắt buộc nhảy chính xác pixel.
- Boss Mẫu Xà Non: pha 1 đớp theo target, có vệt báo; pha 2 nhấn chìm hai phần arena, platform sáng xanh là an toàn; pha 3 gọi clone nước, đánh dấu thân thật bằng sóng âm. Boss không yêu cầu phân biệt màu một mình.
- Loot: MAT-CORE-01 có weekly cap, ngọc Thủy, trang bị Huyền, cosmetic thợ lặn; 1 `CURRENCY_TOKEN_DG04` mỗi clear đủ điều kiện (tối đa 10/tuần/nhân vật); nhật ký là collectible lore, không tiêu thụ.

Registry boss theo manifest: DG-01 `BOSS_YOUNG_TREE` (Cổ Thụ Con), DG-02 `BOSS_ASH_FURNACE` (Lò Tro), DG-03 `BOSS_SIEGE_ENGINE` (Phá Thành Cơ), DG-04 `BOSS_YOUNG_SERPENT` (Mẫu Xà Non). Đây là boss riêng của bốn dungeon, không dùng chung ID với boss thế giới cùng họ hình ảnh.

### 3. Hai raid 10 người

#### RD-01 — Tim Áp Suất Bạch Uyên
- Level 75 đề nghị; 10 người; 30–38 phút; mở sau C5-05, có 2 encounter + boss.
- Tổ chức: 2 nhóm 5; raid leader/assist marker, party frames giữ riêng.
- Encounter A, Bốn Trạm: chia thành 4 cặp chạy tới trạm; mỗi trạm cần một người giữ, mỗi lần giữ 15s; wave quái ưu tiên người gần. Nếu thiếu người, trạm vẫn hoạt động chậm hơn.
- Encounter B, Đường Nứt: 3 người giải áp, 3 người xử lý add, 4 người đánh lõi; vai trò hoán đổi sau 45s.
- Boss Tim Áp Suất: pha 1 bắn tia áp lực theo ba lane, người bị đánh dấu đưa tia vào cột; pha 2 chia raid làm 2 phòng, mỗi phòng một van, đồng bộ mở trong cửa 6s; pha 3 nước dâng, boss chuyển vị trí, 4 safe platform. Một wipe không xóa checkpoint Encounter A.
- Bảo đảm loot: MAT-CORE-01 tuần đầu tiên; 1 `CURRENCY_TOKEN_RD01` mỗi clear đủ điều kiện (tối đa 2/tuần/nhân vật); 6 token đổi một món Huyền phù hợp slot; cosmetic hiếm có pity tiến độ 12 clear, không bán vé.

Boss có canonical ID `BOSS_PRESSURE_HEART`; encounter group/add và điểm đặt dùng `MAP_RD_01` trong manifest.

#### RD-02 — Hợp Mạch: Huyền Ấn mới
- Level 100; 10 người; 35–45 phút; là final raid của C6-05.
- Arena 4 zone liên thông: Ngũ Tháp, Cầu Mạch, Sảnh Hợp Nhất, Lõi Ấn; 5 sockets theo thuộc tính nhưng mọi class đều có thể tương tác.
- Encounter A, Năm Trụ: nhóm chia 2/2/2/2/2; mỗi trụ có một người xử lý tương tác và một người phòng wave; giữ 5 trụ tổng 60s. Người vắng trụ làm giảm tiến độ, không reset hết.
- Encounter B, Kẻ Đục Mạch: 3 add đồng thời, mỗi add có shield yếu trước một loại hành động (interrupt, break, cleanse), không bắt buộc class cụ thể. Đạt ít nhất 2/3 add trước 90s để mở boss.
- Boss Cơ Vô Tướng: pha 1, 100–70%, pattern ba đòn line/sweep/orb; dấu mục tiêu hiển thị cả icon lẫn đường nối; pha 2, 70–35%, tạo hai bản sao ký ức, raid phá 2 thiết bị ở platform đối diện; pha 3 dưới 35%, Hợp Mạch tích 60s, mỗi trụ cần người tương tác, boss đồng thời telegraph vòng lớn và đường thẳng. Thành công cần hoàn tất objective, không chỉ DPS race.
- Wipe checkpoint: pha 1/2 reset encounter; ở pha 3 giữ lại 2 trụ đã ổn định trong lần trước; có giới hạn 3 lần checkpoint/tuần, sau đó có thể tiếp tục nhưng không có clear loot.
- Loot: cosmetic class weapon, 1 `CURRENCY_TOKEN_RD02` mỗi clear đủ điều kiện (tối đa 2/tuần/nhân vật), vật liệu nâng cấp Cổ Vật theo cap; không có lựa chọn cốt truyện khác khóa người chơi khỏi kết thúc.

### 4. Sáu boss thế giới và raid boss cuối

Sáu boss thế giới dùng event instance nhẹ hoặc shard objective; không cho một party khóa spawn. Mỗi boss tồn tại tối đa 12 phút, sau đó rút lui và lịch spawn sau 4 giờ. Reward theo contribution cá nhân, không last hit. Raid boss Cơ Vô Tướng nằm trong raid 10 người ở mục trước và không tính là world boss.

| Boss | Khu vực | Cơ chế trọng tâm | Nhóm gợi ý |
|---|---|---|---:|
| Mãng Cốt | Đầm Chuông | quét ngang, bọt nước/né vòng ngoài | 1–3 |
| Tượng Hành Hỏa | Thanh Lạc | phá cọc điều khiển, đọc ký hiệu | 3–5 |
| Cổ Thụ Trăm Mắt | Lâm Triều | rễ theo đuổi, chặt rễ sáng | 3–5 |
| Lò Trời | Sa Hỏa | cân ba van, tránh làn lửa | 3–5 |
| Tống Bành | Trấn Sơn | khiên, ụ nỏ, đổi lane | 3–5 |
| Mẫu Xà Thủy | Bạch Uyên | triều lên/xuống, platform | 3–5 |

Mỗi boss có phiên bản quest instanced để narrative không phụ thuộc lịch world event; world boss có level band/coefficient riêng. Tham gia sau khi boss còn 10% HP vẫn có thể nhận reward nếu đóng góp objective hợp lệ, nhưng không cấp full cache cho hit đầu cuối.

#### Lệnh Truy Mạch — Thí Luyện Hồi Ức (bản thiết kế bổ sung)

Encounter chiến dịch, boss thế giới, dungeon và raid gốc không yêu cầu vé để thử; giới hạn thưởng hiện tại vẫn áp dụng: boss vùng 1 cache/ngày/vùng, dungeon 3 reward clear/ngày, raid 2 reward clear/tuần. Vé chỉ mở bản đánh lại tính điểm để luyện cơ chế, không mở khóa cốt truyện và không vượt ledger thưởng.

- **Vật phẩm:** `TICKET-BOSS-01` Lệnh Truy Mạch, khóa tài khoản, không giao dịch, stack tối đa 3; nhận tối đa 3 vé/tài khoản/tuần từ nhiệm vụ Bảng Truy Nã đầu tiên trong ngày tại NPC_HA_MAC ở MAP_THANH_LAC hoặc MAP_THANG_LONG. Hai điểm dùng chung một account ledger. Không bán bằng tiền thật/Đồng.
- **Vào:** nhân vật cấp 81+, đã mở MAP_VUC_NGHICH_MACH và đã gặp boss được chọn; NPC_RAID_KEEPER hiển thị boss đủ điều kiện, level khuyến nghị, nhóm 1–5, thời gian, vé sẽ tiêu và quota thưởng còn lại. Mỗi thành viên xác nhận tiêu 1 vé cá nhân; thiếu vé thì không khởi tạo instance.
- **Phiên:** chọn một trong 12 hồ sơ boss đã khám phá, hệ thống tạo arena ký ức riêng; scale HP/damage theo nhóm 1–5, giữ nguyên telegraph/cơ chế đọc được. Một vé cấp một session 20 phút; wipe reset encounter trong session, rời instance hoặc hết giờ thì đóng. Không tiêu vé nếu server không tạo được arena hoặc boss chưa spawn; sau spawn vé được commit.
- **Thưởng:** clear có thể dùng quota cache thường còn lại của cùng boss/activity; nếu quota đã dùng thì chỉ ghi score/thành tích tuần, không rơi gear/vật liệu/cache phụ. Bảng thành tích dùng thời gian + objective, không last-hit. Không có thưởng sức mạnh độc quyền.
- **Bảo vệ:** vé Mạch Triều `TICKET-TIDE-01` chỉ dùng cho event Mạch Triều; không dùng thay Lệnh Truy Mạch. Ledger cap theo account và reset thứ Hai 05:00 giờ server; counter/điều kiện phải hiện trong cửa sổ party trước nút vào.

### 5. Tháp thử thách 30 tầng

Tên hoạt động **Tháp Lạc Ấn**. Mở cấp 30, solo hoặc party tối đa 5. Một tầng 2–4 phút, checkpoint mỗi 5 tầng. Người chơi có thể leo nhiều tầng trong một lượt nhưng tổng thời gian mục tiêu 30–45 phút. Reset weekly score vào cùng giờ reset server.

| Tầng | Dải cấp | Kiểu thử thách |
|---|---:|---|
| 1–5 | 30–39 | đánh nhóm, né telegraph, phá vật thể |
| 6–10 | 40–49 | wave, giữ van, elite |
| 11–15 | 50–59 | platform, escort ngắn, boss biến thể |
| 16–20 | 60–69 | hai objective song song, quái có shield |
| 21–25 | 70–79 | triều/hazard, add, kiểm soát vùng |
| 26–29 | 80–89 | boss remix, tăng áp lực theo thời gian |
| 30 | 90+ | boss thử thách theo tuần, không phải final campaign |

Mỗi tầng có bronze/silver/gold theo hoàn thành, số down và objective; thời gian chỉ là một phần điểm. Phần thưởng lần đầu mỗi tuần gồm Đồng, token, nguyên liệu; cosmetic leaderboard theo mùa. Tầng không yêu cầu gear score cứng; nếu sức mạnh thấp hơn band, cảnh báo đề nghị nhưng vẫn cho vào.

**Boss tuần tầng 30** được resolve từ Weekly_Boss_Rotation_Data_vi.csv theo chu kỳ sáu tuần; tuần bắt đầu thứ Hai 05:00 Asia/Ho_Chi_Minh. Season config ký season_offset; scheduler ghi week_start_utc, source_boss_id, weekly_modifier_id, reward_table_id và ruleset_hash. Instance spawn prefab/pixel sprite set của source boss canonical tại altar `(180,0)`; không tồn tại actor/art ID BOSS_WEEKLY_ROTATION. Reward cap một clear/character/tuần; clear thêm chỉ ghi score.

## 6. PvP ngoài công thành

**Đấu tay đôi:** thách đấu 1v1 tại vùng an toàn; hai người xác nhận; chọn best-of-3, level scaling theo người thấp hơn hoặc normalized profile; consumable combat bị khóa; không rơi đồ/độ bền.

**Đấu trường 3v3:** round 3 phút, first-to-2; matchmaking theo MMR ẩn, class composition không bắt buộc. Mỗi người có 1 revive token/round; vùng arena co ở phút cuối bằng đường viền rõ. Kết quả chỉ thưởng rating/token cosmetic, không có stat gear.

**Chiến Trường Trấn Sơn 10v10:** mở cấp 36 sau C3-01; queue solo hoặc party 2–5; match 12 phút, 1.000 điểm thắng, giữ ba điểm và ghi Huy Hiệu về căn cứ. Dùng MAP_TRAN_SON_SIEGE/zone_id=BG10, có spawn/objective anchors trong world manifest nhưng không spawn actor công thành; normalized level 40, consumable/buff PvE/pet damage tắt, gear không tạo chênh lệch. Casual queue luôn mở; reward cache tối đa 3/ngày; currency CURRENCY_TSS_MERIT chỉ đổi cosmetic. Reconnect 120 giây giữ slot; anti-AFK và void rule theo Battleground_10v10_Production_Spec_vi.md.

#### Giải Đấu Trường Long Môn hàng tuần

Giải 3v3 vòng bảng → knock-out được đăng ký và theo dõi tại `NPC_ARENA_STEWARD` trong `MAP_THANG_LONG`; khán giả đứng ở sảnh, trận chạy ở PvP instance. Đây là giải chính thức theo tuần, tách khỏi queue 3v3 thường và công thành. Lịch, NPC, props, map phases và story hook nằm trong `Thang_Long_Thanh_Capital_Map_Spec_vi.md`.

- Đăng ký Thứ Hai 05:00–Thứ Tư 04:00 Asia/Ho_Chi_Minh; roster 3 chính + 1 dự bị, một account/đội/tuần, tối đa 64 đội/region; roster khóa trước seed. Captain chỉ được đổi người chính với dự bị đã khóa đến 60 phút trước trận đầu; sau trận đầu roster bất biến.
- Thứ Năm–Sáu round-robin tối đa 16 bảng × 4 đội, 3 trận/đội; thắng 3 điểm, hòa 1, thua 0. Xếp toàn bộ roster theo điểm/tiebreaker; tối đa 16 đội (chọn lũy thừa 2 phù hợp khi ít hơn) vào knock-out. Thứ Bảy 18:00–21:00 đánh vòng 16/tứ kết; Chủ Nhật bán kết 18:00, tranh hạng ba 19:00, chung kết 20:00.
- Match best-of-3 round, mỗi round 3 phút; chung kết/tranh hạng ba best-of-5. Check-in 5 phút; reconnect một lần trong 90 giây; forfeit và tie-break ghi vào match ledger.
- Level 20+, hoàn tất C1-06, region PvP hợp lệ. Normalized profile; khóa consumable, pet damage, buff PvE và gear differential. Không có chỉ số hoặc loot sức mạnh trong giải.
- Mỗi trận hoàn thành cấp 5 `CURRENCY_LONG_MON_MEDAL` (Ấn Long Môn), thưởng tham gia tối đa 30/account/tuần; placement bonus chỉ nhận hạng cao nhất, tối đa thêm 30, tổng trần 60/account/tuần theo bảng map spec. Danh hiệu top 3 trao theo leaderboard mùa sau tuần thứ tám. Currency account-bound, chỉ đổi cosmetic/emote tại NPC_ARENA_REWARD_CLERK.
- Mùa 8 tuần: season champions nhận `COS-TITLE-04` Quán Quân Long Môn, á quân `COS-TITLE-05`, hạng ba `COS-TITLE-06`; danh hiệu theo account và roster khóa, title chỉ trang trí. Tuần còn lại ghi thành tích/cúp Hall of Fame và điểm mùa.
- Với 8 đội trở lên chạy vòng bảng → knock-out; 4–7 đội chạy ladder vòng tròn rút gọn rồi final tối đa 4 đội; dưới 4 đội không trao podium tuần và người chơi dùng queue ranked 3v3 thường để ghi rating mùa. Bracket, leaderboard và reward do server authoritative; thể thức tuần hiện rõ trước khi khóa đăng ký.

**World PvP:** mặc định tắt. Nếu phát triển sau alpha, chỉ bật ở map có banner vùng chiến đấu và opt-in; không đánh người dưới level band, không mất item, không camp checkpoint, không hạ thương nhân/NPC quest.

**Giới hạn combat PvP:** skill coefficient riêng, heal/shield cap, stun DR tăng theo số lần trong 8s; slow/root không cộng dồn; potion cooldown 12s; knockback không đẩy khỏi map; gear difference normalized trong arena. Siege có rule riêng tại Guild Social Spec.

### 7. Kinh tế, currencies và giao dịch

**Tiền tệ**
- Đồng: tiền chơi chính; nguồn quái/quest/bán đồ; dùng shop NPC, sửa, craft, phí chợ.
- Danh Vọng vùng: `CURRENCY_REP_THANH_LAC`, `CURRENCY_REP_LAM_TRIEU`, `CURRENCY_REP_SA_HOA`, `CURRENCY_REP_TRAN_SON`, `CURRENCY_REP_BACH_UYEN`; mỗi quest bảng vùng đủ điều kiện +5, boss vùng +10, trần 200/ngày/tài khoản/mỗi vùng; đổi recipe, nguyên liệu cơ bản và cosmetic vùng.
- Ấn Long Môn: `CURRENCY_LONG_MON_MEDAL`, account-bound; +5 mỗi trận hoàn tất, tối đa 30/tuần tham gia và tối đa 30/tuần placement; tổng 60/tuần, chỉ đổi ngoại trang/động tác.
- Token dungeon: `CURRENCY_TOKEN_DG01`…`DG04`, tương ứng DG-01…04; 1 mỗi clear đủ điều kiện, trần 10/tuần/nhân vật; chỉ đổi tại thương nhân dungeon tương ứng.
- Token raid: `CURRENCY_TOKEN_RD01` (Tim Áp Suất) và `CURRENCY_TOKEN_RD02` (Cơ Vô Tướng); 1 mỗi clear đủ điều kiện, trần 2/tuần/nhân vật; đổi trang bị phù hợp slot/cosmetic ở hub.
- Công Huân Trấn Sơn `CURRENCY_TSS_MERIT`: BG10; 10 tham gia +10 thắng +5 objective theo điều kiện, trần 60/ngày/tài khoản; chỉ cosmetic.
- Ấn Tháp `CURRENCY_TOWER_MERIT`: 10 clear + thưởng hạng bronze/silver/gold lần lượt 10/20/30; trần 60/tuần/tài khoản; chỉ cosmetic/title/banner.
- Cống Hiến Bang `CURRENCY_GUILD_CONTRIBUTION`: 50 mỗi quest bang; đổi 1000 Đồng lấy 1 điểm; trần 5000/ngày/nhân vật; dùng cửa hàng/xây dựng bang, không mua chỉ số chiến đấu.
- Vé Mạch Triều `TICKET-TIDE-01` là **item vé**, không phải currency ví; chỉ dùng cho event chơi miễn phí, không bán bằng tiền thật.

Registry chuẩn, ownership, cap/reset và faucet/sink nằm trong `Currency_Production_Data_vi.csv`; mỗi dòng cấp/tiêu thụ có source ID và ledger cap trong `Loot_Recipe_Reward_Production_Data_vi.csv`.

**Nguồn và sink mục tiêu**
- Sources: quest, loot, craft surplus sell, hoạt động tuần, chợ giữa người chơi.
- Sinks: repair, upgrade, craft fee, teleport tiện ích, listing fee, guild cosmetic.
- Cần dashboard server theo daily faucet/sink, median balance, top 1% inflation, trade concentration; điều chỉnh bằng config chứ không wipe.
- Chợ có phí niêm yết 2% và phí giao dịch 5%; cap 10 listing/nhân vật, 30 listings/tài khoản. Giá hiển thị Đồng, người bán nhận tiền qua settlement ledger; buyer confirmation atomic.
- Giao dịch trực tiếp có xác nhận hai bên theo bước offer → review → confirm → commit; đổi item/currency một bên làm hủy confirm cũ. Đồ khóa hoặc quest-bound không thể đưa vào.
- Mailbox 30 ngày chỉ nhận tiền chợ/hoàn giao dịch/quest overflow; không dùng làm kho vòng qua cap.

**Loot fairness:** quái thường drop theo vùng/band; elite có bảng deterministic token; boss cache cá nhân. Drop ngẫu nhiên có pity meter hoặc token đổi chắc chắn. Không có gear stat trong paid gacha; xác suất công bố nếu bất kỳ random cosmetic reward nào được bật.

### 8. Nghề, nông trại và mini game

**Ba nghề thu thập:** khai khoáng, hái dược, đốn gỗ. 35 node có vị trí, ID đầu ra, tier, level nghề, tool, yield và hồi riêng theo shard trong `World_Spawn_Gathering_Manifest_vi.csv` (5 node trên mỗi map Bến Mưa, Lâm Triều, Sa Hỏa, Trấn Sơn, Bạch Uyên, Vực Nghịch Mạch và Đại Ngũ Mạch). Mỗi node có 3 quality tier; harvest 1,2s, bị đánh thì ngắt; respawn từ 60–180s theo vùng. Người chơi nhìn thấy node riêng theo shard, tranh chấp bằng spawn khác chứ không last hit. Tool là utility slot riêng (`TOOL-PICK-01`, `TOOL-SICKLE-01`, `TOOL-HATCHET-01`, `TOOL-ROD-01`); tool condition không giảm khi PvP. Quy tắc farm/câu cá, năm luống, sáu bãi cá, quota và minigame nằm trong `Life_Sim_Production_Spec_vi.md` và data CSV.

**Nông trại:** mở cấp 20, 6 luống. Mỗi cây cần hạt + nước, thời gian 20m–8h, offline tối đa 24h; quá hạn không chết trong 24h grace, chỉ dừng tăng trưởng. Thức ăn/craft ingredient là đầu ra; không có cây bán tiền thật để tăng damage. Thu hoạch tương tác 1s/luống, harvest batch nếu đứng cạnh.

**Mini game**
- Chuông Bến Mưa: nhấn nhịp 60s, 3 độ khó; reward Đồng nhỏ + cosmetic progress.
- Chèo Bè Nước Cạn: điều hướng 90s, tránh đá/rễ; không dùng combat stats.
- Đường Gánh Hàng: memory/route 2 phút; thưởng nghề và contribution guild.
Mỗi mini game 3 lượt/ngày cho reward chính, lượt thêm chỉ điểm cá nhân/đồ trang trí. UI có tutorial, skip âm thanh, không tạo nút QTE gây lỗi accessibility.

### 9. Lịch hoạt động mẫu

| Chu kỳ | Nội dung | Reset |
|---|---|---|
| Hàng ngày | 3 nhiệm vụ vùng, 3 lượt mini game, 2 cache dungeon; 3 reward cache BG10 | 05:00 Asia/Ho_Chi_Minh |
| Hàng tuần | 2 raid reward, 3 quest bang, 1 siege roster, Tháp Lạc Ấn score, giải Long Môn (vòng bảng + playoff) | Thứ Hai 05:00 Asia/Ho_Chi_Minh; khung Long Môn theo lịch riêng |
| 4 giờ | world boss rotation theo vùng | server scheduler |
| Mùa 8 tuần | arena rating, siege banner/leaderboard | ngày công bố season |

Người chơi nhận thông báo trong game trước 10 phút và 2 phút. Không push notification ngoài game nếu chưa opt-in. Reset giờ hiển thị rõ timezone server và đếm ngược UI.

### 10. Chống exploit và phục hồi

- Cooldown, reward cap, eligibility và encounter phase được kiểm tra tại server.
- Không nhận loot khi ở ngoài instance hoặc vượt range contribution; contribution có threshold công khai.
- Party split/merge không reset boss hoặc tạo thêm cache.
- Khi instance server crash, restore checkpoint gần nhất; nếu không thể, cấp token bù theo ledger mà không cấp loot trùng.
- Không dùng client RNG cho loot hoặc arena result; seed server được audit.
- Market, guild, loot và reward đều có transaction ledger + requestId; có công cụ rollback theo transaction.
- Boss mechanic fail không softlock; mọi puzzle có fallback sau 3 lần thất bại hoặc 5 phút.




