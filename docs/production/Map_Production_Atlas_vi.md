# ATLAS SẢN XUẤT MAP VÀ BLOCKOUT
## Ngũ Mạch: Huyền Ấn — bản sản xuất v1.0

### 1. Hệ tọa độ và quy ước đặt cảnh

Đây là tài liệu chuẩn cho level design, world building và AI dựng blockout. Tên/ID map, NPC, spawn và cổng dịch chuyển là khóa tham chiếu, có thể đổi hiển thị nhưng không đổi ID sau khi nội dung đã phát hành.

- Map 2D ngang. Kích thước blockout chuẩn mỗi vùng: X=0..360 WU, Y=0..72 WU; ngoại lệ thủ phủ `MAP_THANG_LONG` rộng 900×96 WU. 1 WU=0,5m; map chuẩn rộng 180m, Thăng Long Thành rộng 450m.
- Sàn chính Y=0 là mặt đất nhân vật đứng; các giá trị Y dương là độ cao mặt platform, không phải tọa độ tâm sprite. Chiều sâu giả lập bằng layer Z riêng, không dùng trục Y.
- Máy quay ngang 32 WU, cao 18 WU ở 16:9; trên 20:9 giữ chiều cao 18 WU và mở ngang tối đa 40 WU. Actor sprite có bounds silhouette 5 WU (100 source px/300 output px ở 1080p, 20 PPU), capsule collision cao 3,6 WU. Tầm nhảy tối đa 7 WU ngang / 5 WU cao; platform gameplay phải nằm trong giới hạn này.
- Tọa độ trong bảng là điểm neo tâm, trừ khi ghi rõ “đầu/cuối”. Quái spawn theo điểm trung tâm và bán kính tuần tra. NPC đứng yên theo tọa độ; NPC đi tuần được ghi hướng/tuyến.
- Kích thước prop là WU, theo rộng × cao. Prop decor nằm ở layer xa/giữa/gần; prop collision có tên riêng. Không đặt bụi/cỏ cao che nhân vật. Nền nước có thể trang trí nhưng mép bờ, độ sâu, vùng bơi phải có collision/nav rõ.
- Mỗi khu gồm cổng vào, một đường chính dễ nhận, tối đa hai nhánh phụ, điểm nghỉ/teleport, vùng encounter và một landmark nhìn thấy từ camera. Collision của decor không tự động bật.
- Spawn quái tính theo nhóm độc lập; nhóm thường không spawn trong 18 WU quanh NPC/teleport. Khi có encounter quest, bật wave quest và tắt spawn thường chồng lấn.
- Ký hiệu spawn: N=quái thường, E=tinh anh, B=boss; số là tổng số thực thể lúc nhóm đầy đủ; R là respawn giây; P là bán kính tuần tra. Mọi spawn gắn level band map.
- Vật thể có tương tác được đặt trên foreground, có outline nhẹ khi mục tiêu gần hơn 2,5m. Cảnh nền xa không nhận interaction.
- Map dùng 8 layer: sky/backdrop, distant silhouette, far props, mid terrain, collision terrain, gameplay actors, near props, weather/lighting. Tương tác ánh sáng không được làm mất telegraph đỏ/cam của boss.

### 2. Chuẩn prefab và vật liệu

| Prefab / ID | Kích thước chuẩn (WU) | Tương tác/collision |
|---|---:|---|
| TREE_SMALL | 5×9 | decor; collision thân bán kính 0,45 |
| TREE_LARGE | 9×18 | decor + thân collision 0,8; tán ở layer xa |
| BUSH_LOW | 3×1.5 | không collision |
| ROCK_SMALL | 3×2 | collision 0,5 |
| ROCK_LARGE | 8×6 | collision; climbable chỉ khi gắn tag |
| HOUSE_SMALL | 18×12 | nền/foreground tùy đường; cửa là socket |
| HOUSE_LARGE | 30×18 | không collision nội thất nếu không có entry |
| PIER | theo đoạn 12×1.2 | collision đi bộ, có socket neo thuyền |
| WATER_SURFACE | patch 12×6 | trigger nước; không chặn trừ vùng sâu |
| LANTERN_POST | 1.5×6 | decor; light cookie 4m |
| TELEPORT_GATE | 6×8 | trigger bán kính 2, tương tác 0,5s |
| QUEST_MARKER | 1×2.5 | client overlay, không là world collision |
| PLATFORM_WOOD | theo đoạn 8–16×1 | collision một chiều |
| PLATFORM_STONE | theo đoạn 8–18×1.5 | collision đặc |
| BRIDGE | đoạn 18×1.2 | collision; có railing ở layer gần |
| SPAWN_RING_BOSS | đường kính 22 | khóa camera encounter, không chặn thoát trừ khi ghi |

Thảm thực vật, đá, kiến trúc cần ít nhất ba biến thể mesh/paintover mỗi họ, đổi scale ±10% và xoay 0/±3 độ để tránh lặp. Không nhân bản asset trong JAR cũ.

### 3. Bản đồ 01 — Bến Mưa

**ID MAP_BEN_MUA.** Level 1–10, khu tân thủ và hub nhỏ. Bảng màu xanh mưa, gỗ bạc nước, ánh đèn vàng ấm. Đường chính hướng Đông. Landmark: Đầm Chuông ở x≈170 và cây cầu chuông treo x≈205. Spawn player x=18, cổng Thanh Lạc x=348.

**Địa hình và đạo cụ đặt cố định**

| Vị trí / X | Đặt cảnh |
|---|---|
| x=0–28 | bờ đất cao 1.5; 3 bụi cỏ thấp (x=5,13,23); 2 đá nhỏ (8,21); cổng bến xa nền |
| x=28–68 | bến gỗ chính; 3 kiện nhiệm vụ tại x=36,44,52; nhà kho 18×12 neo x=60; 2 cột đèn x=31,64 |
| x=68–110 | đường bờ cong; 3 cây nhỏ x=74,94,106; 4 đá nhỏ x=79,88,97,108; 1 cầu gỗ qua rãnh x=92–108 |
| x=110–154 | đầm nông patch nước 36×9 (tâm 132, Y=-3); 6 nén lá nổi; 2 gốc cây; 3 bụi lau; platform gỗ x=122–138, Y=4 |
| x=154–202 | bờ Đầm Chuông; vòng boss tâm x=178, đường kính 22; 4 cọc chuông ở x=169/175/181/187; cột chuông cao 10 tại x=178 |
| x=202–255 | đường cầu; cầu gỗ x=202–228, Y=5; 2 bè neo; 3 đèn lồng x=210/222/246; 2 nhà nhỏ ở x=239 và 252 |
| x=255–315 | ruộng ven bờ; 5 bụi cỏ x=263/275/286/299/310; 3 cây nhỏ x=270/292/307; 5 đá nhỏ x=258/278/289/301/314 |
| x=315–360 | đường cổng phía Đông; cổng teleport x=348; 2 trụ biển x=333/357; 1 xe hàng x=326; 2 đèn x=340/354 |

**NPC**

| ID | Tọa độ | Hành vi |
|---|---:|---|
| NPC_LYAN | (42,0) | đứng cạnh kiện hàng, hướng Đông; điểm start P00-01/P00-03/P00-04 |
| NPC_TA_VAN_KHANH | (64,0) | đứng trước kho, hướng Tây; nhận/trả nhiệm vụ chính |
| NPC_CLASS_TRIAL | (188,0) | xuất hiện sau boss, menu chọn lớp |
| NPC_FISHER_01 | (112,0) | câu cá, thoại phụ |
| NPC_MEDIC_BEN | (30,0) | shop potion; mở sau P00-02 |
| NPC_BOAT_KEEPER | (343,0) | cổng/đi thuyền sau P00-05 |

**Tương tác/trigger nhiệm vụ:** OBJ_BM_PACKAGE_01/02/03 tại (36,0)/(44,0)/(52,0); OBJ_BM_WATER_RIPPLE_01/02/03 tại (122,-1)/(132,-1)/(142,-1); NPC_BM_RESCUE_01=(135,0), NPC_BM_RESCUE_02=(148,0), 2 dân mắc kẹt sau rễ có trigger giải cứu; NPC_LYAN_ESCORT checkpoints tại x=80 và x=120; mỗi checkpoint có vùng kích hoạt rộng 5 WU và điểm dừng an toàn. Rễ nước tương tác đặt tại (126,0)/(138,0)/(151,0).

**Quái/spawn**

| Spawn ID | Vị trí trung tâm | Thành phần | R / P | Ghi chú |
|---|---:|---|---|---|
| SPAWN_BM_01 | (84,0) | 3 MOB_CARPLING — Cá Linh (N) | 18s / 8 | vòng gần cầu, level 1 |
| SPAWN_BM_02 | (116,0) | 4 MOB_CARPLING — Cá Linh (N) | 20s / 9 | bờ đầm; không spawn khi escort đi qua |
| SPAWN_BM_03 | (143,0) | 3 MOB_WATERROOT — Rễ Nước (N) | 24s / 5 | tương tác/đánh xen kẽ |
| SPAWN_BM_04 | (160,0) | 2 MOB_CARPLING + 1 MOB_WATERROOT | 24s / 7 | tắt khi boss trigger |
| SPAWN_BM_05 | (178,0) | 1 Mãng Cốt / BOSS_MANG_COT (B) | quest instance / — | solo scaled 1–3; ring 22 |
| SPAWN_BM_06 | (270,0) | 3 MOB_SHORE_STALKER — Kẻ Rình Bờ (N) | 24s / 8 | mở sau P00-05 |
| SPAWN_BM_07 | (303,0) | 1 MOB_SHORE_STALKER tinh anh (E) + 2 MOB_SHORE_STALKER (N) | 90s / 6 | nhánh phụ |

Trigger wave P00-04: WAVE_BM_ESCORT_A spawn 3 Cá Linh tại (76,0)/(80,0)/(84,0), kích hoạt khi Ly An chạm x=80; WAVE_BM_ESCORT_B spawn 3 Rễ Nước tại (116,0)/(120,0)/(124,0), kích hoạt x=120. Hai wave dùng quest instance layer, thay SPAWN_BM_01/02, respawn sau 30s nếu party wipe. Boss P00-05 giữ anchor x=178; objective nhặt mảnh ấn OBJ_BM_SEAL=(178,0), chỉ xuất hiện sau boss death.

**Cổng / điểm hồi sinh:** TP_BM_HUB=(24,0), hồi sinh SP_BM=(24,0), TP_BM_THANH_LAC=(348,0), TP_BM_THANG_LONG=(348,0) mở sau C1-06; các điểm cùng tọa độ dùng một route selector. TP_BM_DAM_CHUONG=(150,0) mở sau P00-02. Bến Chuông có ranh giới nước an toàn: nhân vật không thể đi quá x=150..195 trừ lối cầu; vùng bơi trang trí không gây drown.

### 4. Bản đồ 02 — Thành Thanh Lạc

**ID MAP_THANH_LAC.** Level 10–20; hub dịch vụ. Nền đá xanh, mái sơn đỏ trầm, cờ năm sắc tối giản. Đường chính y=0 qua quảng trường; không có spawn quái thường trong nội thành.

| X / khu | Địa hình và đạo cụ |
|---|---|
| 0–45 | cổng phía Tây; cổng đá rộng 16, 2 tượng hộ vệ cao 8 tại x=8/38, 4 cờ phướn |
| 45–115 | phố chợ; 6 sạp (x=53,64,76,87,99,110), 3 mái che, 8 đèn/lồng |
| 115–200 | quảng trường; đài phun khô đường kính 8 tại x=155; cột cờ trung tâm x=166; 5 bia thử theo cung x=128/145/162/179/196 |
| 200–282 | phố môn phái; 5 cổng học viện tại x=214/230/246/262/278, mỗi cổng 8×7; sân thử bên trong y=3 |
| 282–360 | cổng phía Đông và bến xe; 2 nhà hội lớn, 1 bảng nhiệm vụ, 2 teleport |
| Platform | mái đi được tại y=8 ở đoạn x=68–88 và x=290–310; cầu gỗ x=303–321, y=10 |

NPC: NPC_LYAN=(30,0), NPC_HA_MAC=(155,0), NPC_GUARD_CAPTAIN=(18,0), NPC_CLASS_TRIAL=(186,0), NPC_MASTER_MINH_KIEM=(218,0), NPC_MASTER_ANH_DAO=(234,0), NPC_MASTER_HUYEN_BUT=(250,0), NPC_MASTER_THACH_CHUY=(266,0), NPC_MASTER_LINH_CUNG=(282,0), NPC_BLACKSMITH=(102,0), NPC_TRADER=(72,0), NPC_VAN_NHU=(124,0), NPC_GUILD_CLERK=(309,0), NPC_TELEPORTER=(339,0). Vân Như dùng sạp nhuộm cạnh mép quảng trường, lối tương tác không chắn đài phun hoặc bia thử. Mỗi nhân vật chỉ thấy trainer của lớp mình; 5 vị trí/đại diện cùng tồn tại trong quảng trường.

Spawn: SPAWN_TL_TRIAL_01=(143,0), 3 hình nhân (training dummy, không loot); spawn trong phòng thử, R=quest; SPAWN_TL_TRIAL_02=(178,0), 1 BOSS_FLAME_SENTINEL — Tượng Hành Hỏa theo C1-05; SPAWN_TL_ROOFTOP=(300,8), 3 MOB_FALSE_SIGIL — Kẻ Giả Phù chỉ khi quest active. Quái không spawn ngoài instance thử. TP_TL_WEST=(8,0), TP_TL_EAST=(350,0), TP_TL_BEN_MUA=(20,0), TP_TL_THANG_LONG=(350,0) sau C1-05, TP_TL_LAM_TRIEU=(350,0) sau C1-06; dùng chung selector tại cửa Đông, SP_TL=(160,0).

Quest placements: OBJ_TL_SIGIL_01..04 tại (128,0)/(146,0)/(174,0)/(193,0); NPC_TL_WITNESS_01=(112,0), NPC_TL_WITNESS_02=(203,0); Kẻ Giả Phù mục tiêu SPAWN_TL_IMPOSTOR=(300,8), 1 MOB_FALSE_SIGIL tinh anh + 2 MOB_FALSE_SIGIL guard. Phe C1-04 dùng SPAWN_TL_STATUES=(142,0), 6 MOB_SMALL_STATUE — Tượng Nhỏ theo cặp tại x=136/142/148 và x=182/188/194; OBJ_TL_CONTROL_STAKE_A=(154,0), B=(176,0); NPC_TL_GUARD_RESCUE=(190,0), actor không bị target. C1-05 boss ring tâm (178,0), 1 BOSS_FLAME_SENTINEL — Tượng Hành Hỏa; 5 trưởng phái đứng tại các anchor học viện x=218/234/250/266/282, mỗi người tương tác được ngoài encounter.

### 5. Bản đồ 03 — Thăng Long Thành

**ID `MAP_THANG_LONG`.** Thủ phủ trung tâm, map an toàn lớn nhất game; kích thước 900×96 WU, ba streaming cell liền mạch (0–299/300–599/600–899). Mở sau C1-05; lần đầu có nhiệm vụ C1-06 và sau đó trở thành cửa ngõ tới mọi map đã mở. Không có mob/spawn combat. Full blockout, NPC, props, giải đấu, dịch chuyển và quest: `Thang_Long_Thanh_Capital_Map_Spec_vi.md`.

| Khu | Dải X | Anchor cố định |
|---|---:|---|
| Cửa Tây và cầu thành | 0–99 | cổng song long (22,0), entry/route (24,0) |
| Bến Sông Ngự | 100–199 | bến hàng (147,0); 2 cầu đá |
| Đại Chợ Ngũ Mạch | 200–299 | trader (237,0), 16 quầy phố chợ |
| Phường Giao Dịch | 300–399 | sàn/kho tài khoản (316/322,0), đổi token (366,0) |
| Phố Bách Công | 400–499 | lò rèn (409,0), phòng thay đồ (455,0) |
| Quảng trường Ngũ Mạch | 500–599 | quảng trường/điểm hồi sinh (520,0), bảng hoạt động (548,0), arena (577,0) |
| Phường Bang Hội | 600–699 | hội quán (636,0), thú (673,0) |
| Phường Công Văn | 700–799 | Hạ Mặc (723,0), Lưu trữ (758,0), nhiệm vụ/truy nã |
| Cửa Đông và Trạm Dịch Chuyển | 800–899 | cổng điều phối (876,0) |

NPC trọng yếu: `NPC_TRADER`, `NPC_TL_APOTHECARY`, `NPC_TL_AUCTION_CLERK`, `NPC_TL_BANKER`, `NPC_RELIC_MERCHANT`, `NPC_BLACKSMITH`, `NPC_VAN_NHU`, `NPC_ACTIVITY_STEWARD`, `NPC_RAID_KEEPER`, `NPC_ARENA_STEWARD`, `NPC_ARENA_REWARD_CLERK`, `NPC_GUILD_CLERK`, `NPC_TL_BEAST_TENDER`, `NPC_HA_MAC`, `NPC_COURT_ARCHIVIST`, `NPC_TL_GATEKEEPER_W/E`. Dùng `locationId` riêng nếu trùng canonical NPC ở map khác.

**Cổng/respawn:** `TP_THANG_LONG_WEST=(24,0)` về Thanh Lạc/Bến Mưa; `TP_THANG_LONG_EAST=(876,0)` mở route selector theo unlock flags; `TP_THANG_LONG_CENTER=(520,0)` là waypoint và bản đồ nhanh; `TP_THANG_LONG_ARENA=(577,0)` chỉ chuyển vào lobby/instance Giải Long Môn. `SP_THANG_LONG=(520,0)`. Các cổng không bỏ qua điều kiện quest.

### 6. Bản đồ 04 — Rừng Lâm Triều

**ID MAP_LAM_TRIEU.** Level 21–35; rừng rễ nhớ tên. Bảng màu lục ẩm, lam sâu, đốm sáng nấm. Đường chính vòng quanh suối; nhánh dưới tán có platform rễ.

| X / khu | Địa hình/props |
|---|---|
| 0–55 | cổng rừng, 7 cây lớn (x=8/18/30/42/51 và layer xa 12/47), 4 đá nhỏ, 2 bụi rễ |
| 55–125 | lán thợ gỗ (nhà 24×14 tại x=82), 6 gốc cây, 8 cây nhỏ, 3 xe gỗ; platform cành y=6 từ x=68–82 và x=101–116 |
| 125–195 | suối patch 40×8 tâm (158,-3), 2 cầu đá x=135–149 và 171–185; 5 nấm phát sáng xa; 6 rễ tương tác |
| 195–265 | Cổ Thụ Trăm Mắt ở x=231, cao 28; boss ring Ø26; 8 rễ phụ làm telegraph, không collision combat |
| 265–360 | thác nhỏ và trạm nước; 3 platform đá y=5/9; 1 cửa van ở x=333; 1 teleport |

NPC: NPC_FOREMAN_MOC=(72,0), NPC_WATER_KEEPER=(324,0), NPC_HA_MAC=(18,0) chỉ ở trại quest, NPC_WOODCUTTER_01=(88,0), NPC_MUSHROOMER=(187,0).  
Spawn: SPAWN_LT_01=(42,0), 4 MOB_DREAM_ROOT — Rễ Mộng (N), R=24/P=8; LT_02=(103,0), 3 MOB_DREAM_ROOT + 2 MOB_MOSS_BEAST — Thú Rêu (N), 25/9; LT_03=(147,0), 3 MOB_DREAM_ROOT, 25/7; LT_04=(209,0), 1 MOB_DREAM_ROOT tinh anh + 2 MOB_DREAM_ROOT (N), 100/7; LT_05=(231,0), 1 BOSS_ANCIENT_TREE — Cổ Thụ Trăm Mắt (B), quest instance; LT_06=(286,5), 3 MOB_MOSS_BEAST trên platform, 30/8; LT_07=(337,0), 2 MOB_DREAM_ROOT khi van quest active.
TP_LT_CAMP=(16,0) là route gate về Thăng Long Thành (mở C1-06), TP_LT_STREAM=(181,0) sau C2-03, TP_LT_THANH_LAC=(350,0), TP_LT_SA_HOA=(350,0) sau C2-05; các destination trùng x dùng chung một selector, không tạo trigger chồng; SP_LT=(16,0).

Quest placements: C2-01 dấu chân OBJ_LT_TRACK_01..03 tại x=38/49/61; rìu OBJ_LT_AXE_01/02 tại x=76/93; 4 Rễ Mộng quest spawn thêm ở x=88/99/110/120. C2-02 tên khắc OBJ_LT_NAME_01..04 tại (84,5)/(112,0)/(155,0)/(197,0), có dấu gợi ý nhìn thấy trong camera. C2-03 van OBJ_LT_VALVE_A/B/C tại (305,0)/(323,0)/(340,0); NPC_LT_MECHANIC=(292,0) đi escort; trigger wave 2×3 Rễ Mộng ở x=310 và x=332, checkpoint sau mỗi van. C2-04 elite SPAWN_LT_MEMORY_ELITE=(210,0), 1 Rễ Mộng Tinh Anh; 3 ký ức OBJ_LT_MEMORY_01..03 tại (218,0)/(231,4)/(244,0). C2-05 boss vẫn dùng x=231; 3 rễ phát sáng OBJ_LT_ROOT_A/B/C tại x=220/231/242, mở hitbox tương tác theo thứ tự A→B→C sau khi boss telegraph.

### 7. Bản đồ 05 — Sa Hỏa

**ID MAP_SA_HOA.** Level 36–50; sa mạc lò và đoàn xe. Bảng màu đất đỏ, cát vàng, tro đen; xa cảnh nhiều khói, khu chơi giữ tương phản tốt.

| X / khu | Địa hình/props |
|---|---|
| 0–64 | trại đoàn xe; 4 lều (14×10), 3 thùng nước lớn, 2 xe, 6 cọc đèn |
| 64–138 | cồn cát; 5 đồi cát foreground xa, đường lõm gameplay, 7 đá/đá quặng, 3 cây khô |
| 138–210 | Hẻm Tro; vách đá hai bên nhưng lối giữa rộng ít nhất 16; 4 miệng thông gió, 5 cột đá; hazard khí độc ở x=168–188 theo chu kỳ |
| 210–295 | lò; nhà lò 34×22 neo x=246, 3 ống khói; 3 van tương tác x=226/246/266; cầu sắt y=8 |
| 295–360 | bãi slag và cửa Trấn Sơn; 6 đống xỉ, 3 xe hàng, 1 teleport |

NPC: NPC_SAM_CHU_QUY=(26,0), NPC_MEDIC_SA_HOA=(82,0), NPC_FORGE_MASTER=(232,0), NPC_HA_MAC=(312,0), NPC_CARAVAN_GUARD=(43,0), NPC_WATER_SELLER=(110,0).  
Spawn: SH_01=(75,0), 4 MOB_SAND_BEETLE — Bọ Cát (N), R=24/P=10; SH_02=(123,0), 3 MOB_SAND_BEETLE + 2 MOB_ASH_RAIDER — Cướp Tro (N), 26/10; SH_03=(174,0), 4 MOB_FURNACE_WARDEN — Người Canh Lò (N), 28/7; SH_04=(205,0), 1 MOB_FURNACE_WARDEN tinh anh + 2 MOB_ASH_RAIDER, 100/7; SH_05=(246,0), 1 BOSS_FURNACE — Lò Trời (B) theo encounter 3 pha; SH_06=(305,0), 3 MOB_ASH_RAIDER, 30/8.
TP_SH_CARAVAN=(18,0), TP_SH_THANG_LONG=(18,0) sau C1-06, TP_SH_FORGE=(288,0) sau C3-04, TP_SH_LAM_TRIEU=(350,0), TP_SH_TRAN_SON=(350,0) sau C3-05; cùng anchor dùng selector; SP_SH=(18,0).

Quest placements: C3-01 OBJ_SH_WATER_01..03 tại x=34/43/52; NPC convoy checkpoint x=92/128, route split trigger tại x=88; hai wave phục kích spawn 3 Cướp Tro tại x=102 và 3 Bọ Cát tại x=132. C3-02 OBJ_SH_MASK_01..05 tại x=72/81/90/99/108; NPC_SH_WORKER_01..04 tại x=127/136/145/154; gas trigger ở x=165–188, an toàn ở vent OBJ_SH_VENT_01/02/03 tại x=160/177/194. C3-03 Người Canh Lò mục tiêu SPAWN_SH_WATCHER=(205,0), 1 elite; bản khắc OBJ_SH_TABLET_01..03 tại x=218/246/274. C3-04 dùng van x=226/246/266, mỗi van spawn 3 add tại x=222/246/270; van cần giữ 20s và mỗi van là checkpoint. C3-05 Lò Trời tâm x=246, arena Ø28, ba wave hazard lửa đồng bộ vent.

### 8. Bản đồ 06 — Trấn Sơn

**ID MAP_TRAN_SON.** Level 51–65; thành có ba cổng tranh chấp và sân công thành. Đá xám xanh, cờ màu tương phản. Encounter đánh theo instance, hub không có quái.

| X / khu | Địa hình/props |
|---|---|
| 0–55 | trại tị nạn ngoài thành; 6 lều nhỏ, 1 bếp, 2 xe, 3 đống vật tư |
| 55–115 | tường Tây và cổng; tường cao 16; platform tường y=12; 2 ụ nỏ, 4 khiên gỗ |
| 115–200 | sân trong; 8 thùng, 4 xe, 3 nhà kho; cờ trục giữa x=160; lối chiến đấu rộng 18 |
| 200–280 | tường Đông, cổng tiếp tế; 2 cầu vượt platform y=9; 3 ụ nỏ |
| 280–360 | thành trên và tháp cờ; tháp cao 24 x=326; cầu thang platform y=4/8/12; boss area Ø28 |

NPC: NPC_REFUGEE_LEADER=(26,0), NPC_CAPTAIN_TRAN_SON=(57,0), NPC_GUILD_SCOUT=(114,0), NPC_TONG_BANH=(315,0) sau boss, NPC_SIEGE_CLERK=(84,0), NPC_REPAIRER=(63,0).  
Spawn: TS_01=(94,0), 3 MOB_AMBUSH_TROOPER — phục kích binh (N), 24/8; TS_02=(147,0), 4 MOB_STONE_AUTOMATON — Tượng Cơ (N), 25/8; TS_03=(215,0), 3 MOB_FALSE_SOLDIER — binh sĩ giả lệnh + 1 MOB_FALSE_SOLDIER tinh anh theo quest; TS_04=(267,0), 2 ụ nỏ hazard có thể phá và 3 MOB_AMBUSH_TROOPER; TS_05=(326,0), 1 BOSS_TONG_BANH — Tống Bành (B) encounter; TS_06=(36,0), 3 nhóm hộ tống theo 3 wave quest.
TP_TS_CAMP=(18,0), TP_TS_THANG_LONG=(18,0) sau C1-06, TP_TS_GATE_EAST=(350,0), TP_TS_SA_HOA=(0,0) và TP_TS_BACH_UYEN=(350,0) sau C4-05; cùng anchor dùng selector; SP_TS=(18,0). Trong siege thật dùng biến thể MAP_TRAN_SON_SIEGE 20v20, spawn nhóm theo phe, tách khỏi nhiệm vụ cốt truyện.

Quest placements: C4-01 NPC refugee squads NPC_TS_REFUGEE_A/B/C tại x=66/142/232; gate OBJ_TS_SAFE_GATE=(82,0); wave phục kích tại x=94/147. C4-02 ba lệnh OBJ_TS_ORDER_01..03 tại x=108/124/140; NPC_TS_ENVOY_01/02 tại x=118/146; dấu sáp OBJ_TS_SEAL=(160,0). C4-03 các objective cổng x=94/180/266, timer giữ tổng 240s; hai ụ nỏ sửa OBJ_TS_BOW_A/B tại x=132/228. C4-04 kho tiếp tế OBJ_TS_SUPPLY=(180,0), cổng phá OBJ_TS_GATE=(266,0), cờ OBJ_TS_FLAG=(326,12); các vị trí chỉ kích hoạt trong campaign instance. C4-05 arena Tống Bành tâm (326,0), thư sau trận OBJ_TS_LETTER=(315,0).

### 9. Bản đồ 07 — Bạch Uyên

**ID MAP_BACH_UYEN.** Level 66–80; thành phố chìm. Giao diện có lớp nước trên cao và ánh sáng xanh lam; nước sâu là hazard được telegraph bằng bong bóng/cột sáng.

| X / khu | Địa hình/props |
|---|---|
| 0–60 | Đài Lặn trên bờ; 2 nhà 18×12; 3 bình khí, 1 cần cẩu, 4 cọc neo |
| 60–125 | lối chìm nông; sàn đá tại y=0 và y=7; 3 vùng nước sâu, 4 cột san hô |
| 125–210 | phế tích; 5 tường đổ, 3 cổng vòm; 3 trạm áp suất x=145/168/191; platform đá y=5/10 |
| 210–290 | phố dưới nước; 6 mặt tiền nhà, 2 xe đẩy hóa thạch, 4 cột đèn cổ; điểm nhật ký tại x=246 |
| 290–360 | hang triều/boss; sàn arena Ø30; 4 cột áp suất quanh boss; teleport phía Đông |

NPC: NPC_DIVER_LEAD=(26,0), NPC_HA_MAC=(245,0), NPC_PRESSURE_KEEPER=(178,0), NPC_RELIC_MERCHANT=(42,0).  
Spawn: BY_01=(83,0), 3 MOB_MIRRORFISH — Cá Gương (N), 25/8; BY_02=(117,7), 3 MOB_MIRRORFISH trên platform, 26/7; BY_03=(156,0), 4 MOB_PRESSURE_GUARD — Kẻ Gác Buồng (N), 27/8; BY_04=(222,0), 2 MOB_PRESSURE_GUARD + 1 MOB_PRESSURE_GUARD tinh anh, 95/8; BY_05=(322,0), 1 BOSS_TIDE_SERPENT — Mẫu Xà Thủy (B) trong arena; BY_06=(280,0), 3 MOB_DROWNED_EXILE — Kẻ Lưu Vong chỉ khi quest phụ.
TP_BY_DIVE=(18,0), TP_BY_THANG_LONG=(18,0) sau C1-06, TP_BY_RUINS=(185,0), TP_BY_TRAN_SON=(0,0), TP_BY_VUC_NGHICH=(350,0) sau C5-05; cùng anchor dùng selector; SP_BY=(18,0). Nước sâu không gây damage tức thì; người chơi nhận cảnh báo 3s trước dòng triều và có đường thoát.

Quest placements: NPC_BY_DIVER_01/02/03 tại x=34/46/58; bình khí OBJ_BY_TANK=(67,0), cửa phế tích OBJ_BY_GATE=(123,0). Ba trạm OBJ_BY_PRESSURE_A/B/C tại x=145/168/191; hai tide trigger tại x=176 và x=198, báo 2s trước khi nước dâng. Bốn trang nhật ký OBJ_BY_PAGE_01..04 tại x=226/238/250/262; ngăn bí mật OBJ_BY_SECRET=(246,0) chỉ hiện khi soi vết khắc. Năm đại diện môn phái projection NPC_BY_WITNESS_MINH_KIEM/ANH_DAO/HUYEN_BUT/THACH_CHUY/LINH_CUNG tại x=214/226/238/250/262; đây là bản chiếu cho nhiệm vụ đối thoại, không có va chạm. Boss Mẫu Xà Thủy giữ tâm x=322, ring Ø30.

### 10. Bản đồ 08 — Vực Nghịch Mạch

**ID MAP_VUC_NGHICH_MACH.** Level 81–100; khu chuẩn bị và các tháp riêng. Không gian trừu tượng màu mực tím, nhưng mặt đi được có texture đá rõ.

| X / khu | Địa hình/props |
|---|---|
| 0–60 | trại chiến dịch; 5 cờ môn phái, 2 bàn y tế, bảng thế giới |
| 60–145 | cầu mạch gãy; platform đá các đoạn x=64–80 y=3, 91–108 y=6, 119–137 y=3; khe vực có vệt sáng |
| 145–220 | tháp trung tâm; 5 cột tương tác quanh tâm (182,0), tọa độ vòng x=167/175/182/189/197; arena wave Ø24 |
| 220–292 | hành lang nghịch mạch; 3 cửa, 6 tường nứt, 2 bẫy laser mạch có telegraph 1s |
| 292–360 | cửa lõi/raid lobby; portal lớn 18×22 x=335; bảng sẵn sàng |

NPC: NPC_LYAN=(24,0), NPC_TA_VAN_KHANH=(46,0), NPC_MASTER_[CLASS] tại trại theo lớp, NPC_CO_VO_TUONG=(312,0) chỉ trong encounter/cutscene, NPC_RAID_KEEPER=(329,0).  
Spawn: VM_01=(83,3), 3 MOB_MACHINIST (N), 30/7; VM_02=(137,0), 4 MOB_RIFT_HUNTER (N), 30/8; VM_03=(182,0), 3 wave quest, mỗi wave 5/6/8 thực thể và 60s event lock; VM_04=(258,0), 1 tinh anh + 3 N, 100/8; VM_05=(312,0), BOSS_COSM (boss campaign, phase 1) trong instance quest; VM_06=(211,0), 3 MOB_RIFT_HUNTER theo quest phụ. Final raid C6-05 dùng instance riêng 10 người, không dùng spawn campaign này.
TP_VM_CAMP=(20,0), TP_VM_THANG_LONG=(20,0) sau C1-06, TP_VM_TOWERS=(154,0) sau C6-01, TP_VM_RAID=(335,0) sau C6-04, TP_VM_BACH_UYEN=(0,0); cùng anchor dùng selector; SP_VM=(20,0).

Quest placements: C6-01 sockets năm trụ tại x=167/175/182/189/197; mỗi socket yêu cầu tương tác 2s và có progress toàn server. C6-02 ba wave spawn tâm x=162/182/202, lần lượt 5/6/8 địch; 3 column OBJ_VM_COLUMN_A/B/C tại x=168/182/196, giữ tối thiểu 2/3 trong 60s. C6-03 lớp cá nhân có 3 mục tiêu chung: OBJ_VM_CLASS_TRIAL_A=(244,0), B=(260,0), C=(276,0); spawn cùng một tinh anh theo lớp, không nhân bản toàn map. C6-04 NPC_CO_VO_TUONG=(312,0), boss encounter riêng phase 1 trong ring Ø24; thoại sau trận giữ ở checkpoint x=312. C6-05 raid lobby x=335, final arena trong instance, không dùng SPAWN_VM_05 ngoài raid.

### 11. Bản đồ 09 — Đại Ngũ Mạch / Mạch Triều

**ID MAP_DAI_NGU_MACH.** Endgame mở sau C6-05; khu tuần hoàn, hoạt động Mạch Triều, năm cánh vùng và trung tâm sự kiện. Mỗi cánh có ít nhất một đường an toàn và một nhánh thử thách.

| X / khu | Nội dung cố định |
|---|---|
| 0–55 | bến trung tâm, NPC_LYAN, bảng hoạt động, 2 cổng về hub |
| 55–110 | vườn Kim: 5 cột kim loại, 6 bụi thấp, 2 mini-boss spawn |
| 110–165 | rừng Mộc: 8 cây nhỏ, 3 cây lớn, 1 suối, 2 mini-boss spawn |
| 165–220 | hồ Thủy: 3 platform, 4 vùng nước, 1 vòng câu cá sự kiện |
| 220–275 | lò Hỏa: 3 vent, 4 đá slag, 1 arena wave |
| 275–330 | thành Thổ: 2 cổng, 4 khiên đá, 1 điểm phòng thủ |
| 330–360 | trụ trung tâm/portal thế giới, 5 sockets theo ngũ hành |

Spawn event pool theo cánh: mỗi cánh có 3 nhóm N (mỗi nhóm 4 quái), 1 E (2 quái hộ vệ + elite), 1 mini-boss B; respawn N=30s, E=180s, B theo event 20 phút. Số quái đang hoạt động toàn map không vượt 36/người chơi shard. Hoạt động world event dùng contribution scoreboard, không last-hit. TP_DNM_HUB=(18,0), TP_DNM_THANG_LONG=(18,0) sau C1-06, TP_DNM_KIM=(74,0), TP_DNM_MOC=(129,0), TP_DNM_THUY=(185,0), TP_DNM_HOA=(240,0), TP_DNM_THO=(295,0), TP_DNM_VUC=(350,0); cùng hub anchor dùng selector; SP_DNM=(18,0).

### 12. Bảng liên kết cổng dịch chuyển

| Từ | Tọa độ | Đến | Điều kiện |
|---|---:|---|---|
| Bến Mưa | x=348 | Thanh Lạc, x=8 | P00-05 |
| Bến Mưa | x=348 | Thăng Long Thành, x=24 | C1-06 |
| Thanh Lạc | x=350 | Thăng Long Thành, x=24 | C1-05 |
| Thăng Long Thành | x=24 / 876 | Thanh Lạc / Bến Mưa | C1-06, theo route selector |
| Thăng Long Thành | x=876 | Lâm Triều, x=16 | C1-06 |
| Thăng Long Thành | x=876 | Sa Hỏa, x=18 | C2-05 |
| Thăng Long Thành | x=876 | Trấn Sơn, x=18 | C3-05 |
| Thăng Long Thành | x=876 | Bạch Uyên, x=18 | C4-05 |
| Thăng Long Thành | x=876 | Vực Nghịch Mạch, x=20 | C5-05 |
| Thăng Long Thành | x=876 | Đại Ngũ Mạch / Mạch Triều | C6-05 |
| Lâm Triều | x=16 | Thăng Long Thành, x=876 | C1-06 |
| Sa Hỏa | x=18 | Thăng Long Thành, x=876 | C1-06 |
| Trấn Sơn | x=18 | Thăng Long Thành, x=876 | C1-06 |
| Bạch Uyên | x=18 | Thăng Long Thành, x=876 | C1-06 |
| Vực Nghịch Mạch | x=20 | Thăng Long Thành, x=876 | C1-06 |
| Đại Ngũ Mạch / Mạch Triều | x=18 | Thăng Long Thành, x=876 | C1-06 |
| Lâm Triều | x=350 | Sa Hỏa, x=0 | C2-05 |
| Sa Hỏa | x=350 | Trấn Sơn, x=0 | C3-05 |
| Trấn Sơn | x=350 | Bạch Uyên, x=0 | C4-05 |
| Bạch Uyên | x=350 | Vực Nghịch Mạch, x=0 | C5-05 |
| Vực Nghịch Mạch | x=335 | Instance raid | C6-04 và party 10 |
| Vực Nghịch Mạch | x=0 | Bạch Uyên, x=350 | luôn sau khi mở |
| Mạch Triều | x=350 | Vực Nghịch Mạch, x=350 | C6-05 |

### 13. Quy tắc cổng, spawn và kiểm tra blockout

- Cổng là socket ở mép map; interaction range 2,5m; teleport có fade 0,2s, không có xác nhận nếu đi ngược chiều tuyến truyện đã mở.
- Cổng chưa mở có biển/đá chặn và biểu tượng điều kiện; không để người chơi đi ra rìa trống.
- NPC cốt truyện không bị đẩy khỏi điểm anchor. Hub thường tối đa 4 crowd actor đồng thời; riêng Thăng Long Thành dùng ngân sách 8 actor hoạt cảnh trong camera theo `Thang_Long_Thanh_Capital_Map_Spec_vi.md`; actor xa chuyển sang animation rẻ.
- Mỗi map có điểm hồi sinh an toàn, cách spawn quái ít nhất 18 WU; khi chết trong boss encounter hồi tại checkpoint instance, không về hub.
- Bảng spawn/NPC/node có tọa độ từng hàng nằm trong `World_Spawn_Gathering_Manifest_vi.csv`; đọc thêm `World_Spawn_Gathering_Manifest_Spec_vi.md` để phân biệt anchor từ Atlas với vị trí activity/node đề xuất. Atlas vẫn là nguồn hình học, props, đường đi và cổng.
- Level designer cần kiểm tra mọi mục tiêu quest nằm trong vùng camera hoặc được dẫn marker; không đặt collectible sau collision không thể tới.
- Tối đa 3 tầng platform gameplay nhìn thấy cùng lúc trong camera; không để cây/nóc nhà che vị trí nhảy.
- Quái không spawn bên trong cổng, cầu thang, vùng tương tác, boss arena đang đóng hoặc trong khoảng escort.
- Đường đi cốt truyện có bề rộng tối thiểu 8 WU; đường combat boss tối thiểu 16 WU nếu boss có vùng quét ngang.
- Kiểm tra mỗi platform bằng đường nhảy hợp lệ, kiểm tra mọi prop collision ở tốc độ chạy, né, đẩy lùi; NPC không được đứng trên collision chỉ decor.
- Bản vẽ hoàn thiện cần xuất scene graybox có nhãn tọa độ 20 WU, screenshot từng map ở tỷ lệ 16:9, bảng spawn và trigger được validate trong editor.

### 14. Fishing anchors và farm pocket

Fishing là interactable, không phải quái hay node tài nguyên bị cạn. Đặt sáu bãi nước: Bến Mưa (132,-1) tại mép Đầm Chuông; Lâm Triều (158,-3) giữa suối; Bạch Uyên (168,0) tại hồ áp suất; Đại Ngũ Mạch (185,0) tại hồ Thủy và (240,0) ở hồ làm mát cạnh cánh Hỏa; Vực Nghịch Mạch (182,0) tại hồ phản chiếu cạnh vùng trại an toàn. Bãi Hỏa chỉ tương tác khi vent đóng và không có combat. Mỗi anchor có vùng thao tác bán kính 3 WU, không chặn đường cốt truyện; marker chỉ hiện khi người chơi cầm cần câu hoặc bật activity overlay.

Nông trại là private pocket, không đặt vật thể trong overworld: MAP_THANG_LONG/FARM_PRIVATE_POCKET, bounds local 0..84 × 0..16 WU; năm luống ở (10,0), (26,0), (42,0), (58,0), (74,0). Farm state per-account; pocket được khởi tạo khi vào, không giữ actor online khi người chơi rời.
