# ĐẶC TẢ PHÒNG THAY ĐỒ, BUFF VÀ MẠNG DỊCH VỤ NPC
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Phạm vi và nguyên tắc theo game

Một modal có ba khu vực nghiệp vụ: **Ngoại trang**, **Vật phẩm buff**, **NPC & Dịch vụ**. Modal mở từ Character, HUD quick slot, cửa hàng NPC, class master, guild clerk, Bảng Truy Nã và NPC_RAID_KEEPER. Dịch vụ khớp theo `npcId + mapId + serviceId + playerState`; client không tự dựng cửa hàng hoặc quyết định quyền mua/vào boss.

Ngũ Mạch là game hành động 2D nhìn từ trên pixel art theo `Pixel_Art_Production_Standard_vi.md`. Preview là **sân khấu sprite pixel-art** (không viewport 3D); chuyển frame/góc front/back/side có asset, không xoay hoặc scale phân số làm mờ pixel. Ngoại trang là mỹ phẩm thuần; buff dùng item/cooldown trong catalog; lệnh boss là vé tài khoản cho Thí Luyện Hồi Ức và không thay quota loot game gốc.

Nguồn chuẩn: `Item_Master_Catalog_vi.csv`, `Item_Rarity_Variant_Catalog_vi.csv`, `Item_Catalog_and_Set_Bible_vi.md`, `Activities_Economy_PvP_Production_Spec_vi.md`, `Map_Production_Atlas_vi.md`, `Guild_Social_Spec_vi.md`, `Character_Equipment_Inventory_Spec_vi.md` và `Art_Entity_Weather_UI_Visual_Bible_vi.md`. Tên, ID, stat, giá, source và unlock state chỉ do content registry/server trả.

### 2. Modal tổng thể và preview sân khấu

Desktop: dialog tối đa 1360×840 CSS px, rộng 92vw/cao 88vh; trái 35% (preview), phải 65% (tab nghiệp vụ). Nền gameplay phủ tối bằng overlay phẳng, không blur; panel Ink-900, frame pixel-art viền đồng, accent Kim-Gold, họa tiết Ngũ Mạch vẽ theo pixel cluster. UI raster theo pixel grid, point sampling và integer scale; LowFX giảm decoration/particle nhưng giữ panel/icon.

| Kích thước | Bố cục |
|---|---|
| Desktop ≥1440px | trái 476px, phải 884px; CTA/tab cố định, hai pane nội dung cuộn độc lập |
| Desktop 1024–1439px | 35/65 theo tỷ lệ nhưng preview tối thiểu 340px; khi tổng <920px chuyển tab dọc |
| Mobile ngang 720–1023px | full-screen; header + preview 30% chiều cao; tab console chiếm phần còn lại, CTA sticky đáy |
| Mobile dọc <720px | preview thành banner 26–30vh, tối thiểu 180px; console dưới có tab cuộn ngang; nút hành động luôn trong safe area |

#### 2.1 Trái — Sân khấu nhân vật/NPC

- Render sprite sheet nhân vật/NPC hiện hành hoặc được chọn trên nền studio theo map: tile giấy mưa Bến Mưa, đá xanh Thanh Lạc, mực/đồng ở dịch vụ khác. Nền không kéo scene gameplay vào modal.
- Layer order: body/face → hair → outfit/armor appearance → headwear → weapon skin → trail → aura → title/emote preview. Gear stats và layer hiển thị tách nhau; skin không ghi vào item instance stat.
- Chuyển trái/phải/front/back qua pose sprite có asset; nút zoom đổi integer scale 1×/2×/3×, không dùng scale phân số; nút `Đứng / Chiến đấu / Chào / Ngồi` phát animation frame preview. Không phát VFX combat lặp vô hạn.
- `Nhân vật / NPC` selector: mặc định nhân vật. Khi ở tab NPC, portrait/idle của NPC hiện cùng service role/location; người chơi không thay outfit NPC bằng vanity của mình.
- Preview unowned chỉ ghi vào `previewLoadout` phía client; nút `Hoàn tác thử` khôi phục trước preview. Không thay appearance gameplay tới khi server xác nhận `Equip`/`Save Appearance`.
- Dải buff hiện dưới sprite preview: icon, group label, thời lượng còn lại, pixel progress ring; bấm icon mở inspector item. Không hiển thị buff đồng minh như buff cá nhân.

### 3. Tab A — Ngoại trang và diện mạo

#### 3.1 Phân loại và slot hiển thị

Sub-tab: `Y phục`, `Tóc & diện mạo`, `Mũ`, `Ngoại trang vũ khí`, `Áo choàng`, `Hiệu ứng & hào quang`, `Danh hiệu/động tác`, `Thú`. Filter: `Tất cả / Đang dùng / Sở hữu / Chưa sở hữu / Mới`, nguồn, lớp, map/chương. Card có icon pixel 32–64px source, tên, slot, class restriction, discovery, `Đang dùng / Đã có / Chưa mở`; click chỉ thử trên sân khấu.

Catalog hiện có 18 item mỹ phẩm; các category rỗng không giả thêm item. Dữ liệu gồm 3 weapon trail, 3 outfit, 6 title (trong đó COS-TITLE-04/05/06 là danh hiệu mùa Giải Long Môn), 2 emote, 1 guild banner, 1 pet cosmetic, 1 cloak skin và 1 aura. Hair/headwear preset là kênh diện mạo gốc; cosmetic hair/headwear riêng chỉ xuất hiện khi có item ID trong catalog.

| Slot/nhóm | Record hiện có | Luật preview/equip |
|---|---|---|
| Y phục full outfit | COS-OUT-01/02/03 | overlay phần giáp nhìn thấy; gear base, stat, set, rarity không đổi |
| Tóc & diện mạo | preset appearance của nhân vật | không đổi khi đổi lớp; không có item cosmetic hair trong catalog hiện tại |
| Mũ | chưa có cosmetic item | không hiện tile “khóa” giả; gear nón vẫn ở panel trang bị thường |
| Ngoại trang vũ khí | COS-WP-01/02/03 | giới hạn đúng loại vũ khí/môn phái nếu asset yêu cầu; không đổi range, hitbox, tốc đánh hoặc VFX gameplay |
| Áo choàng | COS-CLOAK-01 | overlay Phi Phong, không mở slot chiến đấu mới |
| Hào quang | COS-AURA-01 | có tùy chọn tắt cho bản thân/nhóm; LowFX giảm hạt nhưng giữ nhận diện |
| Danh hiệu/động tác | COS-TITLE-01/02/03/04/05/06, COS-EMOTE-01/02 | title hiển thị trên nhân vật theo privacy setting; 04–06 trao theo top 3 mùa Long Môn; emote không có damage/hitbox |
| Thú | COS-PET-01 | chỉ hiện khi PET-02 đang summon; không tăng pet stat |
| Cờ bang | COS-BANNER-01 | gắn ở banner bang theo quyền guild, không phải trang phục cá nhân |

Cosmetic không có chỉ số chiến đấu. Trường `Stat Bonuses` luôn nói rõ `Không cộng chỉ số` và link sang stat gear thật nếu người chơi đang so sánh. Không dùng phẩm chất trang bị Thường/Tinh/Linh/Huyền/Cổ Vật để gắn “độ mạnh” cho skin. Nếu cần phân loại sưu tập, dùng tag nguồn `Nhiệm vụ / Vùng / Bang / Bí cảnh / Mùa`, không làm viền phẩm chất giả.

#### 3.2 Diện mạo gốc nhân vật

Nhân vật giữ lựa chọn `bodyFrame`, `facePreset`, `skinTone`, `hairStyle`, `hairColor`, `faceMark`, `accessoryPreset`; ID preset nằm trong Appearance Manifest, không biến thành item nếu không sở hữu/tiêu thụ. Baseline art pack:

| Kênh | Gói tạo hình tiền sản xuất | Luật |
|---|---:|---|
| Silhouette/body frame | 3 biến thể | cùng collision capsule, reach, tốc độ, anchor vũ khí và animation combat |
| Mặt | 6 preset | cùng voice/subtitle; không gắn lớp hay giới tính |
| Tông da | 8 swatch có kiểm tra tương phản | không thay ánh sáng VFX/telegraph |
| Tóc | 10 kiểu tương thích sprite-set | mọi lớp dùng chung; mũ có cờ `hairVisibility` |
| Màu tóc | 8 palette gốc + 5 sắc mạch | không cần item; sắc mở khóa theo quest/danh vọng nếu được quy định |
| Dấu mặt/phụ kiện | 6 dấu, tối đa 1 dấu + 1 phụ kiện | không chồng qua mắt/đọc combat portrait |

Tạo nhân vật chọn miễn phí. Sau khi vào game, NPC_VAN_NHU cho xem trước miễn phí; lần chỉnh/lưu diện mạo gốc đầu tiên tại salon miễn phí, từ lần thứ hai giá baseline là 2.000 Đồng/lần lưu và phải lấy quote từ server. Đổi preset cosmetic đã sở hữu miễn phí. Lớp/giới tính không đổi qua salon; đổi lớp theo progression service riêng.

#### 3.3 Nhuộm

Vân Như dùng `DyePalette` có version, không item ngẫu nhiên. Chọn tối đa 3 kênh của cosmetic hỗ trợ: vải chính, viền/phụ kiện, pixel aura cosmetic (sprite/palette, không shader glow). Mỗi tile cho xem trước mọi kênh trước khi trả phí.

- Bảng màu thường: 5 màu trung tính (mực, giấy, đất, gỗ, đồng) miễn phí.
- Bảng Mạch: Kim/Vàng, Mộc/Lục, Thủy/Lam, Hỏa/Cam, Thổ/Nâu; mở bằng cờ quest/danh vọng tương ứng, không bán sức mạnh.
- Chi phí lưu màu: 500 Đồng/cosmetic slot; quote hiển thị trước confirm, không thu phí khi chọn preview hoặc đóng.
- Chỉ item có `dyeableChannels[]` mới nhận màu; COS-AURA, trail, title, banner và pet bell không nhuộm. Không đổi màu gear stat/rarity hoặc telegraph.

#### 3.4 Bản đồ sở hữu cosmetic hiện tại

Đây là nguồn mở khóa tiền sản xuất đã đồng bộ vào trường `source_map/source_rule` của Item Master và Rarity Variant catalog. Các nguồn là đề xuất nội dung của Ngũ Mạch; quest/activity ID và NPC phải tồn tại trong content registry trước khi bật phần thưởng.

| ID | Cosmetic | Nguồn mở khóa đề xuất |
|---|---|---|
| COS-WP-01 | Vệt Kiếm Mưa | clear Mãng Cốt lần đầu trong P00-05 |
| COS-WP-02 | Tro Tàn Lặng | clear Lò Trời lần đầu trong C3-05 |
| COS-WP-03 | Mực Lam | clear DG-04 lần đầu |
| COS-OUT-01 | Áo Choàng Người Gác Bờ | hoàn tất P00-05 |
| COS-OUT-02 | Áo Lâm Triều | hoàn tất C2-05 |
| COS-OUT-03 | Khăn Sa Hỏa | hoàn tất C3-05 |
| COS-TITLE-01 | Người Giữ Chuông | hoàn tất P00-05 |
| COS-TITLE-02 | Người Qua Năm Tháp | clear tầng 30 Tháp Lạc Ấn |
| COS-TITLE-03 | Người Dẫn Mạch | clear RD-02 lần đầu |
| COS-EMOTE-01 | Chào Bến Mưa | hoàn tất P00-01 |
| COS-EMOTE-02 | Nghi Thức Huyền Ấn | hoàn tất C6-05 |
| COS-BANNER-01 | Cờ Năm Mạch | mở quyền banner khi guild đạt cấp 5; claim qua NPC_GUILD_CLERK |
| COS-PET-01 | Chuông Rùa Rêu | claim sau khi mở khóa PET-02; chỉ trang trí Rùa Rêu |
| COS-CLOAK-01 | Phi Phong Mưa Mỏng | hoàn tất P00-04 |
| COS-AURA-01 | Quầng Ngũ Sắc | hoàn tất 5 regional trust flags; không bán bằng tiền thật |
| COS-TITLE-04 | Quán Quân Long Môn | roster vô địch season 8 tuần; mở khóa account-wide |
| COS-TITLE-05 | Á Quân Long Môn | roster á quân season 8 tuần; mở khóa account-wide |
| COS-TITLE-06 | Tam Quân Long Môn | roster hạng ba season 8 tuần; mở khóa account-wide |

Phần `Mua` chỉ xuất hiện với offer có `offerId`, loại tiền, giá, giới hạn sở hữu và lịch hết hạn do server trả. Không có lootbox, random stat, gacha skin hoặc preview trả phí. Shop tiền thật nếu game bổ sung trong tương lai nằm ngoài NPC này và chỉ bán vanity.

### 4. Tab B — Vật phẩm buff, consumable và lệnh bài

Panel chia `Hồi phục`, `Buff thời hạn`, `Tiện ích`, `Vé hoạt động`. Mỗi card hiển thị ID QA, số lượng túi, hiệu lực, duration, cooldown group, stacking, combat restrictions, binding, nguồn và nút `Dùng`/`Ghim nhanh`. Cân số có live inventory delta; khi item sắp hết, số lượng tabular chuyển amber kèm số cụ thể.

| Item trong catalog | Hiệu lực | UI/luật dùng |
|---|---|---|
| POT-HP-01/02/03 | hồi 25/35/45% HP tối đa | dùng khi sống; cooldown potion chung 8s |
| POT-MP-01/02/03 | hồi 20/30/40% MP tối đa | cùng cooldown 8s với HP potion; không dùng khi MP đầy |
| POT-CLEAN-01 | xóa một Chậm hoặc Độc | không xóa stun/raid mechanic; confirm nếu có nhiều trạng thái hợp lệ để chọn |
| POT-REVIVE-01 | hồi sinh đồng minh, 15% HP | PvE thường ngoài boss/raid; khóa trong PvP; target/range phải hợp lệ |
| FOOD-ATK-01 | +2% sát thương PvE, 20 phút | buffGroup `FOOD_OFFENSE`; không áp PvP |
| FOOD-DEF-01 | +2% giáp PvE, 20 phút | buffGroup `FOOD_DEFENSE`; không áp PvP |
| FOOD-GATHER-01 | +10% tốc thu thập, 20 phút | buffGroup `FOOD_PROFESSION`; chỉ giảm thời gian node nghề |
| SCROLL-WAY-01 | về hub đã mở, niệm 10s | bị ngắt khi nhận sát thương; utility, không phải buff |
| KIT-REPAIR-01 | sửa 25 durability | ngoài combat; không vào auto-use |
| PET-FEED-01 | +100 XP cho pet | chỉ ở Pet panel/ngoài combat; không tăng nhân vật |
| TICKET-TIDE-01 | 1 lượt Mạch Triều | chỉ event Mạch Triều; không thay lệnh boss |
| TICKET-BOSS-01 | 1 lượt Thí Luyện Hồi Ức | cấp 81+, account-bound; 1 ticket/người vào, tối đa 3 nhận/tuần; không bypass loot cap |

Danh mục `Đan dược` là alias/filter của potion/consumable hiện có. Không có talisman tăng chỉ số, `EXP Boost 2h`, `+100 HP cosmetic` hoặc buff item mới trong master catalog; các placeholder generic không được render thành tile cho tới khi có record, effect, duration, cap, source và server config. Badge rank/huy hiệu danh vọng là currency/status, hiển thị ở header/tài khoản chứ không tự coi là vật phẩm buff.

#### 4.1 Buff state và stacking

| Quy tắc | Kết quả |
|---|---|
| Cùng `buffGroupId`, item mới bằng hoặc yếu hơn item đang chạy | modal báo `Buff hiện tại còn …`; chọn `Thay thế` hoặc `Giữ buff`; nếu giữ thì không tiêu item |
| Cùng group nhưng item mới có hiệu lực cao hơn | vẫn xác nhận thay thế; khi xác nhận xóa timer/nguồn cũ rồi bắt đầu timer mới, không cộng phần thời lượng còn dư |
| Cùng item dùng lại trước hết hạn | nếu item có `refreshPolicy=refresh`, reset về duration tối đa; không cộng dồn thời lượng/stats |
| Khác group | được chạy song song nếu `stackPolicy` server cho phép; ví dụ offense + defense + profession |
| Buff PvE khi vào PvP | icon còn đếm giờ nhưng effect suspend; tooltip ghi `Không áp dụng PvP`; không tiêu lại khi rời PvP |
| Ngắt mạng/server reject | item không bị trừ ở client; chờ inventory transaction result theo `requestId` |

HP/MP potion dùng `POTION_RECOVERY` shared cooldown 8s theo catalog. Cleanse/Revive dùng cooldown và state server riêng; UI nhận `cooldownMs` từ server, không hardcode value chưa có. Food duration do server giữ `expiresAt`. Death/relog chỉ giữ nếu buff record có `persistOnDeath/reconnect`; baseline food còn timer qua relog, không kéo dài thời lượng.

#### 4.2 Quick-use và tự dùng

Quick strip có 4 ô, đồng bộ HUD và panel này; kéo card vào ô hoặc chọn `Ghim nhanh`. Auto-use là opt-in theo group/item, trạng thái mặc định Off, có threshold và context:

- HP/MP potion (tùy chọn riêng): auto ở ≤35% HP hoặc ≤20% MP, ưu tiên potion phù hợp band/cấp có sẵn; dùng theo cooldown server. Toast có `Tắt tự dùng` cho lần kế tiếp; không trì hoãn potion hoặc hứa Undo sau commit. Request chưa rõ kết quả phải query receipt, không hoàn HP/item bằng client (DEC-023).
- Buff food: auto refresh khi còn ≤60s, ngoài combat mặc định. Có toggle `Cho phép trong dungeon`, mặc định Off; luôn Off trong PvP và raid boss. Không tự thay buff cùng group đang mạnh hơn.
- Không auto dùng POT-REVIVE, POT-CLEAN, SCROLL-WAY, KIT-REPAIR, PET-FEED, dye, ticket, vật phẩm quest hoặc item có confirm/destructive effect.
- Nếu stack =0, item bị thay trong quick slot, nhân vật downed, khóa PvP, thiếu cooldown hoặc server offline: tự tắt lần auto đó, hiện lý do và không spin loop.
- Setting toggle ghi trên server theo characterId; người chơi thấy tóm tắt `Tự dùng HP ≤35% · MP ≤20% · thức ăn ≤60s` trước khi bật.

### 5. Lệnh boss giới hạn và cửa vào

HUD/buff panel có widget `Lệnh Truy Mạch x/y` và quota loot riêng. `TICKET-BOSS-01` mở **Thí Luyện Hồi Ức** ở NPC_RAID_KEEPER tại MAP_VUC_NGHICH_MACH; nội dung, cấp, phí, quota, disconnect/refund được khóa tại mục 4 của `Activities_Economy_PvP_Production_Spec_vi.md`.

Trong party, mỗi người dùng một lệnh cá nhân. Nút vào chỉ bật khi toàn đội đủ cấp, đã khám phá boss, đã mở region/activity, có ticket và đồng ý. Màn xác nhận ghi: boss/arena, quy mô party, cấp đề nghị, duration 20 phút, `Tiêu 1 Lệnh Truy Mạch`, quota cache boss/activity còn lại, score nếu quota loot đã dùng. Server commit item sau khi instance tạo và boss spawn; lỗi tạo trước spawn trả item, disconnect sau spawn tiếp tục session/không tự cấp entry mới. Raid/dungeon/boss thường không đòi ticket; vé không là cửa bắt buộc cho progression.

### 6. Tab C — NPC, merchant và service routing

Header NPC hiện tên/portrait/title, NPC ID trong QA mode, vai trò hiện tại, map + tọa độ, trạng thái giờ mở, service tab và chấm kết nối. Thoại là một dòng ngắn theo nhân vật; phục vụ không mở bản sao NPC nếu cùng actor nhận nhiều service.

| NPC / map anchor | Dịch vụ | Danh mục/điều kiện |
|---|---|---|
| **NPC_VAN_NHU — Vân Như**, MAP_THANG_LONG (455,0), salon chính; MAP_THANH_LAC (124,0), quầy cơ bản | diện mạo gốc, vanity wardrobe, nhuộm, thử/hoàn tác | dùng chung cosmetic ledger; salon thành có toàn bộ palette/service; hai anchor là cùng canonical actor, không nhân đôi tiến độ |
| **NPC_TL_AUCTION_CLERK**, MAP_THANG_LONG (316,0) | mua/bán qua sàn người chơi | giá/fee/listing cap dùng `Activities_Economy_PvP_Production_Spec_vi.md`; không cho đặt lệnh qua tin nhắn riêng |
| **NPC_TL_BANKER**, MAP_THANG_LONG (322,0) | kho account và mailbox | binding/TTL/ô kho do inventory service quyết định; không chuyển quest-bound/soulbound |
| **NPC_BLACKSMITH**, MAP_THANG_LONG (409,0); quầy dịch vụ cơ bản MAP_THANH_LAC (102,0) | sửa/rèn/nâng cấp/phân giải | thao tác sâu mở `Forge_Crafting_Overlay_Spec_vi.md`; giao dịch có quote/version |
| **NPC_ARENA_STEWARD / NPC_ARENA_REWARD_CLERK**, MAP_THANG_LONG (587/599,0) | roster, vòng đấu, leaderboard, lịch sử và đổi Ấn Long Môn | giải 3v3 theo tuần; chỉ đổi vanity, không đổi stat |
| **NPC_ACTIVITY_STEWARD**, MAP_THANG_LONG (548,0) | lịch hoạt động/dungeon/raid và đăng ký | hiện điều kiện mở, giờ server, nhóm và quota |
| NPC_TRADER, MAP_THANG_LONG (237,0) / MAP_THANH_LAC (72,0) | hàng hóa cơ bản theo `offerId` | thành có đủ band/đồ dùng; Thanh Lạc phục vụ người mới; không bán item stat cuối game hoặc lệnh boss |
| NPC_TL_APOTHECARY, MAP_THANG_LONG (181,0) | potion/cleanse/thức ăn catalog | stock/limit theo offer; buff PvE không áp PvP |
| NPC_MEDIC_BEN, MAP_BEN_MUA (30,0) | HP/MP potions cơ bản, cleanse sau P00-02 | POT-HP-01/MP-01; giá/stock server; chưa hoàn thành tutorial thì có sample quest grant riêng |
| NPC_MEDIC_SA_HOA, MAP_SA_HOA (82,0) | dược cấp vùng và FOOD-ATK/DEF/GATHER | yêu cầu band/map đã mở; không bán combat advantage PvP |
| NPC_WATER_SELLER, MAP_SA_HOA (110,0) | nước và hàng vật tư sa mạc | Nước Sạch/crafting supply; không bị gán nhầm thành buff XP |
| NPC_MASTER_[CLASS], MAP_THANH_LAC (mỗi học viện) | ngoại trang vũ khí class, dấu mạch/tên lớp | class hiện tại, quest/danh vọng; unlock bằng quest/currency earned, không đổi stat |
| NPC_GUILD_CLERK, MAP_THANG_LONG (636,0) chính / MAP_THANH_LAC (309,0) cơ bản | COS-BANNER-01, phù hiệu/title bang, guild service | guild level/role permission; vật phẩm bang theo `Guild_Social_Spec_vi.md`, log giao dịch |
| NPC_RELIC_MERCHANT, MAP_THANG_LONG (366,0) / MAP_BACH_UYEN (42,0) | đổi token lấy cosmetic/boss relic vanity | mở theo quest/discovery; stock curated; không bán random gear |
| NPC_HA_MAC, MAP_THANG_LONG (723,0), MAP_THANH_LAC (155,0) và các điểm quest | Bảng Truy Nã, claim TICKET-BOSS-01 từ daily record | giới hạn chung account 3 vé/tuần; cùng NPC ID không nhân bản tiến độ khi đổi map |
| NPC_RAID_KEEPER, MAP_THANG_LONG (566,0) / MAP_VUC_NGHICH_MACH (329,0) | roster, boss memory, lệnh vào, raid | vé cá nhân, boss discovery, C6 unlock, quota loot, party ready; không lấy vé Mạch Triều |

`NPC_RELIC_MERCHANT` có hai node cố định tại Thăng Long Thành và Bạch Uyên, cùng canonical actor nhưng inventory/offer có thể lọc theo map và quest; đây không phải NPC lang thang. Nếu muốn tạo wandering merchant, content cần khai báo `npcSpawnId`, map, time window, visibility/unlock và sprite-set trong Atlas trước khi hiển thị icon. NPC seller không tự mua currency premium; NPC services dùng Đồng, điểm danh vọng, guild contribution hoặc token event được nêu rõ.

#### 6.1 Routing và quyền truy cập

Service request chứa `{npcId, mapId, serviceId, actorInstanceId, characterId, contentVersion}`; server xác thực actor ở đúng map, khoảng cách tương tác ≤2,5m, NPC active/time window, quest/level/class/guild permission và offer revision. Gửi toạ độ không đủ để gọi cửa hàng ngoài vùng. NPC multi-location (ví dụ Hạ Mặc) dùng actor cùng canonical NPC ID nhưng service location/locationId riêng; quest state và inventory không reset khi đổi điểm.

`serviceInventory` được merge từ base catalog + `npcOfferSetId` + region + rotation time + player eligibility. Stock unavailable hiện khóa kèm lý do; inventory thiếu item không khiến nút mua disable vô cớ nếu offer có thể tìm ở NPC khác—panel `Nơi khác có dịch vụ` dẫn tới map đã mở. Giá, currency, daily cap, binding sau mua, expiry và confirmation copy đều do quote server trả.

### 7. Giao dịch, sở hữu và trạng thái account

- Cosmetics account-bound dùng `cosmeticUnlockLedger`; equip state theo character và slot. Vanity unowned preview không ghi vào ledger.
- Buff/ticket nằm trong inventory ledger; chỉ server commit consume. Quick slot/autouse chỉ gửi intent; item delta và buff state đẩy sau ACK.
- Buy/save appearance/dye dùng `requestId` idempotent, quote revision và price snapshot. `QuoteExpired` refresh quote; `InsufficientCurrency`, `AlreadyOwned`, `WrongClass`, `ServiceClosed`, `TicketLimit`, `BuffConflict` trả giải thích tiếng Việt.
- Dye save hoặc appearance save không thể commit cùng lúc với cosmetic purchase nếu một thao tác thất bại; mỗi thao tác là transaction độc lập.
- Không xoá ngoại trang đã mở nếu quest/season/merchant hết hạn. Offer hết hạn ngừng mua mới, đồ sở hữu vẫn trang bị được.
- Khi user mở từ NPC, đóng modal trả về dialogue/service ban đầu; mở từ Character thì đóng về HUD, không tự teleport.

### 8. Data contract tối thiểu

```json
{
  "appearance": {
    "bodyFrame": "BODY_B",
    "facePreset": "FACE_03",
    "skinTone": "SKIN_05",
    "hairStyle": "HAIR_07",
    "hairColor": "PAL_MOC_02",
    "equippedCosmetics": {"outfit":"COS-OUT-02","weapon":"COS-WP-03","aura":null},
    "dyeChannels": {"main":"DYE_INK","trim":"DYE_KIM"},
    "revision": 17
  },
  "buffs": [
    {"buffGroupId":"FOOD_OFFENSE","sourceItemId":"FOOD-ATK-01","expiresAt":"server-time","state":"active"}
  ],
  "npcContext": {"npcId":"NPC_VAN_NHU","mapId":"MAP_THANH_LAC","serviceId":"appearance"}
}
```

Mọi trường preset/art, palette, appearance slot, skin compatibility, dyeable channels, buff group, duration, cooldown, stack policy, auto-use eligibility, ticket cap, NPC service, offer, source và price version đều nằm trong data manifest/server config. Client chỉ dựng preview và trạng thái từ payload, không tự tính bonus hoặc cấp quyền.

### 9. Phím, accessibility và performance

- PC click/double click không mua/dùng; Enter xác nhận chỉ khi quote preview đang mở; Esc đóng popup xác nhận trước modal. Controller focus: category → card → preview controls → action.
- Mobile hit target 48×48dp, gesture rotate không chặn cuộn grid; có nút xoay trái/phải thay cho drag; slider zoom có reset.
- Body text 15–17px PC/14–16sp mobile; màu trạng thái luôn có label/icon; timer đọc được bằng screen reader `Còn 12 phút 08 giây`.
- Reduced motion tắt xoay tự động, shimmer/aura particles và camera ease; LowFX không tắt icon active buff hoặc trạng thái cooldown.
- Cache tối đa một character sprite set + một NPC portrait cùng lúc; swap cosmetic sprite variant/layer không reload toàn scene; không render 3D viewport trên client nhìn từ trên.

### 10. Handoff checklist

- Mockup 1920×1080, 1366×768, 1280×720 landscape, 390×844 portrait; có preview character/NPC, owned/unowned, auto-use, buff conflict, no ticket, ticket ready, shop closed, insufficient Đồng.
- Chứng minh preview thử skin không đổi gameplay loadout trước ACK; skin không sửa stat/set/durability/animation hitbox.
- HP/MP 8s shared cooldown; food 20 phút; các group conflict, auto-off defaults, no-auto exclusions, reconnect timer và PvP suspend đều dùng server state.
- Ticket có cap 3/account/week, one per participant, consume-at-boss-spawn/refund-before-spawn; regular boss/dungeon/raid không bị lệnh khóa entry và quota loot không bị reset.
- Vân Như có anchor mới tại MAP_THANH_LAC; art/profile, atlas, navigation icon, ID và interaction range nhất quán. Hạ Mặc/merchant/medic/guild/raid routes resolve từ content registry.
- Bản đồ ngoài trang phục có `Không cộng chỉ số`; không tồn tại `EXP Boost 2h`, rarity skin giả hoặc hair/headwear inventory tile chưa có ID.

### 11. Tài liệu liên quan

- Item/vanity/buff/ticket: `Item_Master_Catalog_vi.csv`, `Item_Rarity_Variant_Catalog_vi.csv`, `Item_Catalog_and_Set_Bible_vi.md`.
- Map/NPC coordinates and NPC art: `Map_Production_Atlas_vi.md`, `Art_Entity_Weather_UI_Visual_Bible_vi.md`.
- Boss tickets/quota/activities: `Activities_Economy_PvP_Production_Spec_vi.md`.
- Character and gear state: `Character_Equipment_Inventory_Spec_vi.md`.
- Guild cosmetic permissions: `Guild_Social_Spec_vi.md`.
- HUD and modal patterns: `Gameplay_HUD_Overlay_Spec_vi.md`, `Settings_Overlay_Spec_vi.md`, `Forge_Crafting_Overlay_Spec_vi.md`.
